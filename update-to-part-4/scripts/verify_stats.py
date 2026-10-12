"""Recalcule, depuis rntc/lymphome-synth-v5-eval, quelques faits cités dans le journal Jean Zay.
Usage : uv run --with pandas --with pyarrow python -I scripts/verify_stats.py <dataset_dir> <taxonomy_dir> <out_dir>
"""
import json, re, sys, unicodedata, csv
from collections import Counter, defaultdict
import pandas as pd

ds, taxdir, out = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, taxdir)
import taxonomy as T  # noqa

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()

splits = {s: pd.read_parquet(f"{ds}/data/{s}-00000-of-00001.parquet") for s in ["train", "validation", "test"]}
res = {}
for s, d in splits.items():
    L = d.text.str.len()
    res[s] = {"n_docs": len(d), "chars_median": int(L.median()), "chars_mean": int(L.mean()),
              "pct_docs_gt_9000": round(100 * (L > 9000).mean(), 1),
              "pct_docs_gt_24000": round(100 * (L > 24000).mean(), 1),
              "pct_docs_gt_45000": round(100 * (L > 45000).mean(), 2)}

HDR = re.compile(r"^=== .*? — (\d{4}-\d{2}-\d{2}) ===$", re.M)
fam_stats = defaultdict(Counter)
rows = []
d = splits["test"]
for _, r in d.iterrows():
    ann = json.loads(r.annotation_v4_json) if r.annotation_v4_json else None
    if not ann:
        fam_stats["_missing"]["n_docs_without_annotation"] += 1; continue
    gold = r.gold if isinstance(r.gold, dict) else json.loads(r.gold) if isinstance(r.gold, str) else r.gold
    if isinstance(gold, str):
        gold = json.loads(gold.replace("'", '"')) if gold.startswith("{") else {}
    hdr_dates = set(HDR.findall(r.text))
    tnorm = norm(r.text)
    for k, spec in T.FIELD_SPEC.items():
        fam = spec["family"]
        if fam == "TXT":
            continue
        v = ann.get(k)
        items = [v] if isinstance(v, dict) else (v or [])
        vals = [it["value"] for it in items if isinstance(it, dict) and it.get("value") not in (None, "")]
        if not vals:
            continue
        val = str(vals[0]).strip()
        spans = [it.get("span", "") for it in items if isinstance(it, dict)]
        c = fam_stats[fam]
        c["n"] += 1
        c["value_in_first_span"] += norm(val) in norm(spans[0]) if spans and spans[0] else 0
        c["value_in_document"] += norm(val) in tnorm
        if fam == "DATE":
            c["date_equals_header_date"] += val[:10] in hdr_dates
summary = {"lengths": res, "test_targets_by_family": {}}
for fam, c in fam_stats.items():
    if fam == "_missing":
        summary["test_docs_without_annotation"] = c["n_docs_without_annotation"]; continue
    n = c["n"]
    summary["test_targets_by_family"][fam] = {
        "n_targets": n,
        "pct_value_literal_in_its_annotated_span": round(100 * c["value_in_first_span"] / n, 1),
        "pct_value_literal_anywhere_in_document": round(100 * c["value_in_document"] / n, 1),
        **({"pct_date_equal_to_a_section_header_date": round(100 * c["date_equals_header_date"] / n, 1)} if fam == "DATE" else {})}
tot = sum(c["n"] for f, c in fam_stats.items() if f != "_missing")
summary["test_targets_all"] = {"n_targets": tot,
    "pct_value_not_literal_in_document": round(100 * (1 - sum(c["value_in_document"] for f, c in fam_stats.items() if f != "_missing") / tot), 1)}
json.dump(summary, open(f"{out}/verified_stats.json", "w"), ensure_ascii=False, indent=2)
print(json.dumps(summary, ensure_ascii=False, indent=2))

# Exemple : premier dossier de test, cible canonique vs spans annotés
r = d.iloc[0]
ann = json.loads(r.annotation_v4_json)
labels = r.field_labels if isinstance(r.field_labels, dict) else json.loads(r.field_labels)
with open(f"{out}/example_test_doc0_targets.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["field", "family", "label", "canonical_value", "annotated_spans", "source_documents"])
    for k, spec in T.FIELD_SPEC.items():
        v = ann.get(k)
        items = [v] if isinstance(v, dict) else (v or [])
        items = [it for it in items if isinstance(it, dict) and it.get("value") not in (None, "")]
        if not items:
            continue
        w.writerow([k, spec["family"], (labels.get(k) or {}).get("label", ""), items[0]["value"],
                    " || ".join(it.get("span", "") for it in items),
                    " || ".join(sorted({it.get("source_document", "") for it in items if it.get("source_document")}))])
open(f"{out}/example_test_doc0_text.txt", "w").write(r.text)
print("doc0 id", r.id, len(r.text))
