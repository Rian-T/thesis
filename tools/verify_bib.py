# /// script
# requires-python = ">=3.10"
# dependencies = ["bibtexparser<2", "rapidfuzz>=3", "requests>=2.31"]
# ///
"""
verify_bib.py — anti-hallucination check for thesis.bib.

For every bib entry that is actually \\cite'd in the .tex sources, resolve it
against real bibliographic databases (Crossref by DOI, arXiv by id, then
OpenAlex / DBLP / Crossref by title) and report whether the entry's metadata
(title, first author, year) matches a real publication.

Verdicts:
  VERIFIED  — solid match (title + author/year concordant)
  MISMATCH  — found, but a field diverges (wrong title for that DOI, wrong
              author, wrong year) — the most likely sign of a hallucination
  NOT_FOUND — nothing close found anywhere — possibly invented
  SKIPPED   — legitimately unverifiable (whitelisted key / entry type)

Non-blocking by default (always exits 0). Pass --strict to exit 1 when any
MISMATCH / NOT_FOUND remains (useful for a pre-submission gate).

Usage:
  uv run tools/verify_bib.py                 # check cited entries, print report
  uv run tools/verify_bib.py --all           # check every entry in the .bib
  uv run tools/verify_bib.py --offline        # cache only, no network
  uv run tools/verify_bib.py --json out.json  # machine-readable report
  uv run tools/verify_bib.py --limit 20       # first N (debug)
  uv run tools/verify_bib.py --strict         # non-zero exit on problems
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import bibtexparser
import requests
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "thesis.bib"
TEX_DIR = ROOT / "sources"
CACHE = ROOT / "tools" / ".bibcheck_cache.json"
WHITELIST = ROOT / "tools" / "bibcheck_whitelist.txt"
MAILTO = "rian.touchent@inria.fr"  # politeness for Crossref/OpenAlex pools

TITLE_OK = 88      # fuzzy title score for a confident match
TITLE_DOI_BAD = 60 # below this, a DOI clearly points to a different paper
AUTHOR_OK = 88
YEAR_TOL = 1       # preprint vs published can differ by a year

HEADERS = {"User-Agent": f"thesis-bibcheck/1.0 (mailto:{MAILTO})"}


# ----------------------------------------------------------------------------- normalization
_LATEX_ACCENT = re.compile(r"\\[`'^\"~=.]\{?([a-zA-Z])\}?")
_LATEX_CMD = re.compile(r"\\[a-zA-Z]+\s*")
_BRACES = re.compile(r"[{}]")
_NONALNUM = re.compile(r"[^a-z0-9 ]+")
_WS = re.compile(r"\s+")


def fold(s: str) -> str:
    """LaTeX/accents -> lowercase ascii alnum, for robust matching."""
    if not s:
        return ""
    s = _LATEX_ACCENT.sub(r"\1", s)
    s = _LATEX_CMD.sub(" ", s)
    s = _BRACES.sub("", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = _NONALNUM.sub(" ", s)
    return _WS.sub(" ", s).strip()


def title_sim(a: str, b: str) -> float:
    return fuzz.token_set_ratio(fold(a), fold(b))


def bib_families(author_field: str) -> list[str]:
    """Extract family names from a bibtex author field."""
    out = []
    for chunk in re.split(r"\s+and\s+", author_field or ""):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "," in chunk:                      # "Last, First"
            fam = chunk.split(",")[0]
        else:                                  # "First Last"
            fam = chunk.split()[-1] if chunk.split() else chunk
        fam = fold(fam)
        if fam:
            out.append(fam)
    return out


def family_match(bib_fams: list[str], src_fams: list[str]) -> bool:
    if not bib_fams or not src_fams:
        return False
    src = [fold(x) for x in src_fams]
    for bf in bib_fams[:1]:                    # first author is enough
        for sf in src:
            if bf and sf and (bf in sf or sf in bf or fuzz.ratio(bf, sf) >= AUTHOR_OK):
                return True
    return False


def to_year(v) -> int | None:
    if v is None:
        return None
    m = re.search(r"\d{4}", str(v))
    return int(m.group()) if m else None


# ----------------------------------------------------------------------------- cited-key extraction
_CITE = re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")
_CITE_LR = re.compile(r"\\citetlanguageresource\{([^}]*)\}")


def cited_keys(tex_dir: Path) -> set[str]:
    keys: set[str] = set()
    for tex in tex_dir.rglob("*.tex"):
        txt = tex.read_text(encoding="utf-8", errors="ignore")
        for rx in (_CITE, _CITE_LR):
            for m in rx.finditer(txt):
                for k in m.group(1).split(","):
                    k = k.strip()
                    if k:
                        keys.add(k)
    return keys


# ----------------------------------------------------------------------------- network resolvers
class Net:
    def __init__(self, offline: bool, cache: dict):
        self.offline = offline
        self.cache = cache

    def _get(self, url: str, params=None, kind="json"):
        ck = url + "|" + json.dumps(params or {}, sort_keys=True)
        if ck in self.cache:
            return self.cache[ck]
        if self.offline:
            return None
        soft_fail = False  # transient failure -> don't poison the cache with None
        for attempt in range(4):
            try:
                r = requests.get(url, params=params, headers=HEADERS, timeout=8)
                if r.status_code == 404:
                    self.cache[ck] = None  # definitive: cache the miss
                    return None
                if r.status_code == 429:  # rate limited (e.g. Semantic Scholar)
                    soft_fail = True
                    if attempt == 0:
                        time.sleep(2)  # one gentle retry, then give up (no tunnel)
                        continue
                    break
                if r.status_code in (500, 502, 503):
                    soft_fail = True
                    time.sleep(1.0)
                    continue
                r.raise_for_status()
                data = r.text if kind == "xml" else r.json()
                self.cache[ck] = data
                return data
            except Exception:
                soft_fail = True
                if attempt == 0:
                    time.sleep(0.5)
        if not soft_fail:
            self.cache[ck] = None  # only cache a clean "nothing found"
        return None

    # -- by identifier --
    def crossref_doi(self, doi: str):
        d = self._get(f"https://api.crossref.org/works/{doi.strip()}",
                      {"mailto": MAILTO})
        if not d or "message" not in d:
            return None
        m = d["message"]
        return {
            "title": (m.get("title") or [""])[0],
            "families": [a.get("family", "") for a in m.get("author", [])],
            "year": to_year((m.get("issued", {}).get("date-parts") or [[None]])[0][0]),
            "src": "crossref/doi",
        }

    def arxiv(self, aid: str):
        aid = re.sub(r"v\d+$", "", aid.strip())
        x = self._get("http://export.arxiv.org/api/query",
                      {"id_list": aid, "max_results": 1}, kind="xml")
        if not x:
            return None
        try:
            ns = {"a": "http://www.w3.org/2005/Atom"}
            root = ET.fromstring(x)
            e = root.find("a:entry", ns)
            if e is None:
                return None
            title = (e.findtext("a:title", default="", namespaces=ns) or "").strip()
            if not title:
                return None
            fams = [(a.findtext("a:name", default="", namespaces=ns) or "").split()[-1]
                    for a in e.findall("a:author", ns)]
            year = to_year(e.findtext("a:published", default="", namespaces=ns))
            return {"title": title, "families": fams, "year": year, "src": "arxiv"}
        except Exception:
            return None

    # -- by title (returns list of candidates) --
    def semanticscholar_title(self, title: str):
        # Best coverage for ACL Anthology / LREC / CEUR workshops / preprints.
        d = self._get("https://api.semanticscholar.org/graph/v1/paper/search",
                      {"query": title, "limit": 5, "fields": "title,year,authors"})
        out = []
        for p in (d or {}).get("data", [])[:5]:
            fams = [(a.get("name", "") or "").split()[-1] for a in p.get("authors", [])]
            out.append({"title": p.get("title") or "", "families": fams,
                        "year": to_year(p.get("year")), "src": "semanticscholar"})
        return out

    def arxiv_title(self, title: str):
        x = self._get("http://export.arxiv.org/api/query",
                      {"search_query": f'ti:"{title}"', "max_results": 5}, kind="xml")
        if not x:
            return []
        out = []
        try:
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for e in ET.fromstring(x).findall("a:entry", ns):
                t = (e.findtext("a:title", default="", namespaces=ns) or "").strip()
                if not t:
                    continue
                fams = [(a.findtext("a:name", default="", namespaces=ns) or "").split()[-1]
                        for a in e.findall("a:author", ns)]
                out.append({"title": t, "families": fams,
                            "year": to_year(e.findtext("a:published", default="", namespaces=ns)),
                            "src": "arxiv/title"})
        except Exception:
            pass
        return out

    def openalex_title(self, title: str):
        d = self._get("https://api.openalex.org/works",
                      {"search": title, "per_page": 5, "mailto": MAILTO})
        out = []
        for w in (d or {}).get("results", [])[:5]:
            fams = [(a.get("author", {}).get("display_name", "") or "").split()[-1]
                    for a in w.get("authorships", [])]
            out.append({"title": w.get("title") or "", "families": fams,
                        "year": to_year(w.get("publication_year")), "src": "openalex"})
        return out

    def dblp_title(self, title: str):
        d = self._get("https://dblp.org/search/publ/api",
                      {"q": title, "format": "json", "h": 5})
        out = []
        hits = (((d or {}).get("result", {}).get("hits", {}) or {}).get("hit", []) or [])
        for h in hits[:5]:
            info = h.get("info", {})
            au = info.get("authors", {}).get("author", [])
            if isinstance(au, dict):
                au = [au]
            fams = [(a.get("text", "") if isinstance(a, dict) else str(a)).split()[-1]
                    for a in au]
            out.append({"title": info.get("title", ""), "families": fams,
                        "year": to_year(info.get("year")), "src": "dblp"})
        return out

    def crossref_title(self, title: str):
        d = self._get("https://api.crossref.org/works",
                      {"query.bibliographic": title, "rows": 5, "mailto": MAILTO})
        out = []
        for m in (d or {}).get("message", {}).get("items", [])[:5]:
            out.append({"title": (m.get("title") or [""])[0],
                        "families": [a.get("family", "") for a in m.get("author", [])],
                        "year": to_year((m.get("issued", {}).get("date-parts")
                                         or [[None]])[0][0]),
                        "src": "crossref/title"})
        return out


# ----------------------------------------------------------------------------- verdict
def get_arxiv_id(entry: dict) -> str | None:
    ep = entry.get("eprint")
    if ep and re.match(r"\d{4}\.\d{4,5}", ep.strip()):
        return ep.strip()
    if ep and entry.get("archiveprefix", "").lower() == "arxiv":
        return ep.strip()
    for f in ("url", "doi", "note"):
        v = entry.get(f, "")
        m = re.search(r"(\d{4}\.\d{4,5})", v)
        if m:
            return m.group(1)
        m = re.search(r"arxiv[:/]\s*([a-z\-]+/\d{7}|\d{4}\.\d{4,5})", v, re.I)
        if m:
            return m.group(1)
    return None


def classify(entry: dict, net: Net) -> dict:
    title = entry.get("title", "")
    bfam = bib_families(entry.get("author", ""))
    byear = to_year(entry.get("year"))
    notes = []

    # 1) DOI is authoritative
    doi = entry.get("doi", "").strip()
    if doi:
        rec = net.crossref_doi(doi)
        if rec and not (rec.get("title") or "").strip():
            # Crossref has the DOI but no usable title (common for ACL
            # Anthology DOIs) — don't flag, fall through to title search.
            notes.append("DOI in Crossref but no title field")
            rec = None
        if rec:
            ts = title_sim(title, rec["title"])
            if ts < TITLE_DOI_BAD:
                return verdict("MISMATCH", entry,
                               f"DOI resolves to a DIFFERENT title (sim {ts:.0f}): "
                               f"\"{rec['title'][:70]}\"", rec)
            am = family_match(bfam, rec["families"])
            ym = byear is not None and rec["year"] is not None and abs(byear - rec["year"]) <= YEAR_TOL
            if ts >= TITLE_OK and (am or ym):
                if byear and rec["year"] and abs(byear - rec["year"]) > YEAR_TOL:
                    notes.append(f"year {byear} vs {rec['year']}")
                if not am and rec["families"]:
                    notes.append(f"first author '{bfam[0] if bfam else '?'}' not in DOI record")
                return verdict("VERIFIED", entry, "; ".join(notes) or "DOI match", rec)
            return verdict("MISMATCH", entry,
                           f"DOI found but author/year off (title sim {ts:.0f}, "
                           f"author={am}, year_bib={byear}/cr={rec['year']})", rec)
        notes.append("DOI not found in Crossref")

    # 2) arXiv id
    aid = get_arxiv_id(entry)
    if aid:
        rec = net.arxiv(aid)
        if rec:
            ts = title_sim(title, rec["title"])
            if ts >= TITLE_OK:
                return verdict("VERIFIED", entry, "; ".join(notes + ["arXiv match"]), rec)
            notes.append(f"arXiv id title mismatch (sim {ts:.0f}: \"{rec['title'][:60]}\")")

    # 3) title search across sources, stopping at the first confident match
    best, best_ts = None, -1.0
    for fn in (net.semanticscholar_title, net.arxiv_title,
               net.openalex_title, net.dblp_title, net.crossref_title):
        try:
            cands = fn(title)
        except Exception:
            cands = []
        min_len = max(12, 0.5 * len(fold(title)))
        for c in cands:
            if len(fold(c["title"])) < min_len:
                continue  # reject absurdly short candidates (token_set inflation)
            ts = title_sim(title, c["title"])
            if ts > best_ts:
                best, best_ts = c, ts
        if best is not None and best_ts >= TITLE_OK and (
            family_match(bfam, best["families"])
            or (byear is not None and best["year"] is not None
                and abs(byear - best["year"]) <= YEAR_TOL)
        ):
            break  # good enough — don't hit the remaining sources
    if best is None or best_ts < 70:
        return verdict("NOT_FOUND", entry,
                       "; ".join(notes + [f"no title match (best {best_ts:.0f})"]), best)
    am = family_match(bfam, best["families"])
    ym = byear is not None and best["year"] is not None and abs(byear - best["year"]) <= YEAR_TOL
    if best_ts >= TITLE_OK and (am or ym):
        extra = []
        if not am and best["families"]:
            extra.append(f"author '{bfam[0] if bfam else '?'}' weak vs source")
        if byear and best["year"] and abs(byear - best["year"]) > YEAR_TOL:
            extra.append(f"year {byear} vs {best['year']}")
        return verdict("VERIFIED", entry, "; ".join(notes + extra) or f"title match ({best['src']})", best)
    return verdict("MISMATCH", entry,
                   f"closest is \"{best['title'][:60]}\" (sim {best_ts:.0f}, "
                   f"author={am}, year_bib={byear}/src={best['year']}, {best['src']})", best)


def verdict(status: str, entry: dict, note: str, rec) -> dict:
    return {"key": entry.get("ID"), "type": entry.get("ENTRYTYPE"),
            "title": entry.get("title", ""), "status": status, "note": note,
            "matched": rec}


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bib", default=str(BIB))
    ap.add_argument("--tex-dir", default=str(TEX_DIR))
    ap.add_argument("--all", action="store_true", help="check every entry, not only cited")
    ap.add_argument("--offline", action="store_true", help="cache only, no network")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", default="")
    ap.add_argument("--strict", action="store_true", help="exit 1 if problems remain")
    args = ap.parse_args()

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    whitelist = set()
    if WHITELIST.exists():
        for line in WHITELIST.read_text().splitlines():
            line = line.split("#")[0].strip()
            if line:
                whitelist.add(line)

    with open(args.bib, encoding="utf-8") as f:
        db = bibtexparser.load(f)
    entries = {e["ID"]: e for e in db.entries}

    if args.all:
        keys = sorted(entries)
    else:
        cited = cited_keys(Path(args.tex_dir))
        keys = sorted(k for k in cited if k in entries)
        missing = sorted(cited - set(entries))
        if missing:
            print(f"⚠  {len(missing)} cited key(s) absent from the .bib: "
                  f"{', '.join(missing[:10])}{' …' if len(missing) > 10 else ''}")

    if args.limit:
        keys = keys[:args.limit]

    net = Net(args.offline, cache)
    results = []
    print(f"Checking {len(keys)} {'all' if args.all else 'cited'} entries "
          f"({'offline' if args.offline else 'online'})…\n")
    for i, k in enumerate(keys, 1):
        e = entries[k]
        if k in whitelist or e.get("ENTRYTYPE", "").lower() in whitelist:
            results.append(verdict("SKIPPED", e, "whitelisted", None))
        else:
            results.append(classify(e, net))
        if i % 10 == 0:
            print(f"  …{i}/{len(keys)}", file=sys.stderr)
        if i % 5 == 0:  # flush cache periodically so progress survives a kill
            CACHE.write_text(json.dumps(cache))

    CACHE.write_text(json.dumps(cache))

    order = {"MISMATCH": 0, "NOT_FOUND": 1, "VERIFIED": 2, "SKIPPED": 3}
    results.sort(key=lambda r: (order[r["status"]], r["key"]))
    counts = {s: sum(1 for r in results if r["status"] == s) for s in order}

    icon = {"VERIFIED": "✓", "MISMATCH": "✗", "NOT_FOUND": "?", "SKIPPED": "–"}
    for r in results:
        if r["status"] in ("MISMATCH", "NOT_FOUND"):
            print(f"{icon[r['status']]} [{r['status']}] {r['key']}")
            print(f"    bib:  \"{r['title'][:78]}\"")
            print(f"    why:  {r['note']}")
    print("\n── summary ──")
    for s in order:
        print(f"  {icon[s]} {s:9s} {counts[s]}")
    problems = counts["MISMATCH"] + counts["NOT_FOUND"]
    print(f"\n{problems} entr{'y' if problems == 1 else 'ies'} need manual review.")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"report → {args.json}")

    sys.exit(1 if (args.strict and problems) else 0)


if __name__ == "__main__":
    main()
