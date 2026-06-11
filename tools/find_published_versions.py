#!/usr/bin/env python3
"""
find_published_versions.py — deterministic preprint→published-venue checker.

Companion to verify_bib.py. Where verify_bib proves an entry is *real*, this
script flags CITED entries that look like a preprint (arXiv / @misc / no DOI)
for which a *published* version (conference / journal) appears to exist.

100% deterministic: pure HTTP to Crossref + DBLP + string similarity. NO LLM,
so no hallucination. It never edits the .bib — it prints candidates for a human
to judge (title, venue, DOI, similarity). Results cached for cheap re-runs.

Usage:
    uv run tools/find_published_versions.py            # cited entries only
    uv run tools/find_published_versions.py --all      # every entry in thesis.bib
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(ROOT, "thesis.bib")
SRC = os.path.join(ROOT, "sources")
CACHE = os.path.join(ROOT, "tools", ".arxivcheck_cache.json")
MAILTO = "riantouchent@gmail.com"   # Crossref polite pool

# ---------- parse thesis.bib (brace-matched) ----------
def parse_bib(text):
    entries = {}
    i = 0
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[at:])
        if not m:
            i = at + 1; continue
        etype, key = m.group(1).lower(), m.group(2)
        b = text.find("{", at); depth = 0; j = b
        while j < len(text):
            if text[j] == "{": depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0: break
            j += 1
        entries[key] = (etype, text[at:j + 1])
        i = j + 1
    return entries

def field(raw, name):
    m = re.search(name + r"\s*=\s*[{\"](.+?)[}\"]\s*,?\s*\n", raw, re.S | re.I)
    if not m:
        m = re.search(name + r"\s*=\s*\{(.+?)\}", raw, re.S | re.I)
    if not m:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"[{}]", "", m.group(1))).strip()

# ---------- cited keys ----------
CITE = re.compile(r"\\(?:cite|citep|citet|citeyear|citetlanguageresource|citealp|citeauthor)\*?(?:\[[^\]]*\])*\{([^}]*)\}")
def cited_keys():
    keys = set()
    for dp, _, fns in os.walk(SRC):
        for fn in fns:
            if not fn.endswith(".tex"):
                continue
            txt = open(os.path.join(dp, fn), encoding="utf-8", errors="ignore").read()
            txt = re.sub(r"(?<!\\)%.*", "", txt)
            for m in CITE.finditer(txt):
                for k in m.group(1).split(","):
                    k = k.strip()
                    if k: keys.add(k)
    return keys

# ---------- is this entry a preprint candidate? ----------
def is_preprint(etype, raw):
    doi = field(raw, "doi").lower()
    blob = raw.lower()
    if "10.48550/arxiv" in doi:
        return True
    if re.search(r"archiveprefix\s*=\s*[{\"]?\s*arxiv", blob):
        return True
    if "arxiv.org" in blob or "arxiv preprint" in blob or re.search(r"\beprint\s*=", blob):
        return True
    journal = (field(raw, "journal") + " " + field(raw, "howpublished")).lower()
    if "arxiv" in journal or "corr" in journal:
        return True
    if etype in ("misc", "unpublished") and not doi:
        return True
    return False

def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()

def sim(a, b):
    return int(SequenceMatcher(None, norm(a), norm(b)).ratio() * 100)

# ---------- HTTP ----------
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"thesis-bibcheck (mailto:{MAILTO})"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

PREPRINT_TYPES = {"posted-content", "grant", "dataset"}
def crossref_published(title):
    """Return best non-preprint published hit for a title, or None."""
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 6, "mailto": MAILTO})
    try:
        items = get("https://api.crossref.org/works?" + q)["message"]["items"]
    except Exception:
        return None
    best = None
    for it in items:
        ttl = (it.get("title") or [""])[0]
        if not ttl:
            continue
        s = sim(title, ttl)
        if s < 88:
            continue
        typ = it.get("type", "")
        cont = (it.get("container-title") or [""])
        cont = cont[0] if cont else ""
        if typ in PREPRINT_TYPES or "arxiv" in cont.lower():
            continue
        if typ not in ("proceedings-article", "journal-article", "book-chapter"):
            continue
        cand = {"title": ttl, "venue": cont, "doi": it.get("DOI", ""), "type": typ, "sim": s, "src": "crossref"}
        if best is None or s > best["sim"]:
            best = cand
    return best

def dblp_published(title):
    q = urllib.parse.urlencode({"q": title, "format": "json", "h": 6})
    try:
        hits = get("https://dblp.org/search/publ/api?" + q)["result"]["hits"].get("hit", [])
    except Exception:
        return None
    best = None
    for h in hits:
        info = h.get("info", {})
        ttl = info.get("title", "")
        s = sim(title, ttl)
        if s < 88:
            continue
        venue = info.get("venue", "")
        typ = info.get("type", "")
        if "informal" in typ.lower() or venue.lower() in ("corr", "arxiv"):
            continue  # DBLP marks arXiv as "Informal Publications" / venue CoRR
        cand = {"title": ttl, "venue": venue, "doi": info.get("doi", ""), "type": typ, "sim": s, "src": "dblp"}
        if best is None or s > best["sim"]:
            best = cand
    return best

def main():
    do_all = "--all" in sys.argv
    text = open(BIB, encoding="utf-8").read()
    entries = parse_bib(text)
    keys = set(entries) if do_all else (cited_keys() & set(entries))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

    candidates = [k for k in sorted(keys) if is_preprint(*entries[k])]
    print(f"{len(keys)} entries checked · {len(candidates)} look like preprints\n")

    found = []
    for n, k in enumerate(candidates, 1):
        etype, raw = entries[k]
        title = field(raw, "title")
        if not title:
            continue
        if k in cache:
            hit = cache[k]
        else:
            hit = crossref_published(title) or dblp_published(title)
            cache[k] = hit
            json.dump(cache, open(CACHE, "w"), indent=0)
            time.sleep(0.4)  # be polite to APIs
        print(f"  …{n}/{len(candidates)} {k}", file=sys.stderr)
        if hit:
            found.append((k, title, hit))

    print("── preprints with an apparent PUBLISHED version ──\n")
    if not found:
        print("  none — every cited preprint looks genuinely preprint-only.")
    for k, title, h in found:
        print(f"✗ {k}")
        print(f"    bib (preprint): {title}")
        print(f"    published:      {h['title']}")
        print(f"    venue:          {h['venue']}  [{h['type']}, {h['src']}, sim {h['sim']}]")
        print(f"    doi:            {h['doi']}\n")
    print(f"── {len(found)} candidate(s) for manual review (script never edits the .bib) ──")

if __name__ == "__main__":
    main()
