"""Étape 2, mesure préalable : le pool de spans contient-il seulement la réponse ?

Le design V2 repose sur une hypothèse falsifiable : si on cesse de réduire la matrice
`S = [F champs x M spans]` à 12 cases par ligne, et qu'on élague à M spans par un critère
INDÉPENDANT DU CHAMP (`max_f S[f, span]`), alors la bonne valeur devient atteignable pour
~90 % des cibles DATE, contre ~0.52 aujourd'hui.

Si ce n'est pas vrai, aucune loss ne rattrapera : ce qui n'est pas dans le pool est perdu
avant la première dérivée. On mesure donc AVANT d'écrire la tête d'affectation.

Trois régimes, sur les mêmes documents et les mêmes cibles :
  actuel      top-12 par champ (CAND_K), largeur <= 6, valeur = taxonomy.normalize_target
  pool-M      top-M du document, critère max_f, valeur = transducteur appris (étape 1)
  document    la cible apparaît-elle quelque part dans le texte, sous forme littérale ?
              (borne haute lâche : ignore la structure en spans et la largeur maximale)

et deux définitions de « atteignable », parce qu'elles ne disent pas la même chose :
  transduc.   le transducteur produit EXACTEMENT la cible depuis ce span   <- le mécanisme réel
  littéral    la cible est une sous-chaîne du texte du span                <- borne haute

On rapporte aussi la part des spans gagnants qui NE chevauchent AUCUN span gold : c'est le
test direct de « 55,7 % des dates vivent dans des en-têtes que l'annotateur n'a jamais pointés ».

  python pool_diagnostic.py --n 60 --M 256
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.insert(0, str(_H / "transducer"))
import gliner_integrated as G          # noqa: E402
import taxonomy as T                   # noqa: E402
from train_transducer import MAXIN, Transducer, enc_in, pad   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

B = "/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs"
LB = B + "/lymphome"
PROD = "/lustre/fswork/projects/rech/rua/uvb79kr/biomed-fr-v4/lymphome_v4/outputs/prod_20260527_121452.jsonl"
V5 = B + "/gliner2-lym-V5FROMV3B/best"
TRANSD = str(_H / "transducer" / "transducer.pt")
FAMS = ("CAT", "DATE", "NUM", "ORD")


def norm_lit(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


class Transd:
    """Le transducteur de l'étape 1, en lot et mémoïsé sur (libellé, texte du span)."""

    def __init__(self, path, dev):
        ck = torch.load(path, map_location=dev)
        self.stoi, self.itos = ck["stoi"], ck["itos"]
        self.m = Transducer(len(self.itos)).to(dev).eval()
        self.m.load_state_dict(ck["model"])
        self.dev = dev
        self.cache = {}

    @torch.no_grad()
    def run(self, pairs, bs=4096):
        """Précalcule en un seul lot toutes les paires manquantes du document."""
        todo = [p for p in dict.fromkeys(pairs) if p not in self.cache]
        for i in range(0, len(todo), bs):
            b = todo[i:i + bs]
            x = pad([enc_in({"label": la, "span": sp}, self.stoi) for la, sp in b], MAXIN).to(self.dev)
            for p, o in zip(b, self.m.greedy(x, self.itos)):
                self.cache[p] = o

    def get(self, pair):
        return self.cache.get(pair)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--M", type=int, default=256)
    ap.add_argument("--crit", choices=("max", "rank"), default="max",
                    help="max = max_f S[f,span] ; rank = meilleur RANG du span parmi les champs. "
                         "Les scores bruts de deux champs ne sont pas à la même échelle, donc "
                         "`max` favorise les champs bruyants ; `rank` les met à égalité.")
    ap.add_argument("--max_chars", type=int, default=24000)
    ap.add_argument("--out", default=str(_H / "pool_diagnostic.json"))
    a = ap.parse_args()
    dev = "cuda"
    torch.manual_seed(0)

    ds = G.build_dataset(LB + "/lymphome_train_v2.jsonl", PROD, cap=a.max_chars)[:a.n]
    model = load_model(V5).to(dev).eval()
    tr = Transd(TRANSD, dev)
    POOL = f"pool-{a.M}"
    print(f"{len(ds)} documents  M={a.M}  max_chars={a.max_chars}", flush=True)

    reg = {k: defaultdict(lambda: [0, 0, 0]) for k in ("actuel", POOL, "document")}
    offgold = defaultdict(lambda: [0, 0])
    poolsz = []

    for di, d in enumerate(ds):
        with torch.no_grad():
            batch = model.processor.collate_fn_train([(d["text"], d["output"])]).to(dev)
            all_tok, all_sch = model._encode_batch(batch)
            tok = all_tok[0]
            mk = G.markers_of(all_sch[0]); l2i = G.lab2idx_of(d["output"])
            span_rep = model.compute_span_rep(tok)["span_rep"]
            dsc = G.detection_scores(model, span_rep, mk)               # [F,L,W]
        L, W = span_rep.shape[0], span_rep.shape[1]
        woff = G.word_offsets(model, d["text"])
        text = d["text"]; ntext = norm_lit(text)
        Lw = min(L, len(woff))

        # --- pool élagué, critère INDÉPENDANT DU CHAMP (un top-k par champ rétablirait le goulot)
        flat = dsc[:, :Lw].reshape(dsc.shape[0], -1)
        if a.crit == "max":
            key = flat.max(0).values
        else:
            rank = torch.empty_like(flat)
            order = flat.argsort(dim=1, descending=True)
            rank.scatter_(1, order, torch.arange(flat.shape[1], device=flat.device,
                                                 dtype=flat.dtype).expand_as(flat))
            key = -rank.min(0).values          # meilleur rang parmi les champs
        idx = torch.topk(key, min(a.M, flat.shape[1])).indices.tolist()
        pool = []
        for ix in idx:
            i, w = ix // W, ix % W
            cs, ce = woff[i][0], woff[min(i + w, len(woff) - 1)][1]
            if ce > cs:
                pool.append((i, w, cs, ce))
        pool_txt = [text[cs:ce] for _, _, cs, ce in pool]
        poolsz.append((len(pool), Lw * W))

        todo = [e for e in d["entries"]
                if e["target"] is not None and e["family"] in FAMS
                and l2i.get(e["label"]) is not None and l2i[e["label"]] < dsc.shape[0]]
        # UN SEUL lot de transduction pour tout le document
        tr.run([(e["label"], t[:300]) for e in todo for t in pool_txt])

        gold_spans = {e["key"]: e["spans"] for e in d["entries"]}
        for e in todo:
            li = l2i[e["label"]]; tgt = str(e["target"]); nt = norm_lit(tgt); fam = e["family"]

            cur = G.native_candidates(dsc[li], woff, L, W)
            ctxts = [text[cs:ce] for _, _, cs, ce, _ in cur]
            cvals = [T.normalize_target(e["key"], t) for t in ctxts]
            reg["actuel"][fam][0] += any(G._match(fam, v, tgt) for v in cvals)
            reg["actuel"][fam][1] += any(nt and nt in norm_lit(t) for t in ctxts)
            reg["actuel"][fam][2] += 1

            pvals = [tr.get((e["label"], t[:300])) for t in pool_txt]
            hit = [i for i, v in enumerate(pvals) if G._match(fam, v, tgt)]
            reg[POOL][fam][0] += bool(hit)
            reg[POOL][fam][1] += any(nt and nt in norm_lit(t) for t in pool_txt)
            reg[POOL][fam][2] += 1

            reg["document"][fam][1] += bool(nt and nt in ntext)
            reg["document"][fam][2] += 1

            if hit:
                gs = gold_spans.get(e["key"], [])
                _, _, cs, ce = pool[hit[0]]
                offgold[fam][0] += not any(min(ce, gb) - max(cs, ga) > 0 for ga, gb in gs)
                offgold[fam][1] += 1
        if (di + 1) % 10 == 0:
            print(f"  {di+1}/{len(ds)} docs", flush=True)

    print(f"\npool moyen : {sum(p for p,_ in poolsz)/len(poolsz):.0f} spans retenus "
          f"sur {sum(t for _,t in poolsz)/len(poolsz):.0f} possibles\n")
    print("RAPPEL DU POOL — la cible est-elle atteignable depuis un span du pool ?")
    print(f"{'régime':12s} {'critère':10s} " + " ".join(f"{f:>7s}" for f in FAMS) + f" {'total':>8s}")
    print("-" * 62)
    res = {}
    for name in ("actuel", POOL, "document"):
        per = reg[name]
        for ci, crit in ((0, "transduc."), (1, "littéral")):
            if name == "document" and ci == 0:
                continue          # pas de span défini : seul le littéral a un sens
            row = [per[f][ci] / per[f][2] if per[f][2] else float("nan") for f in FAMS]
            tot = sum(per[f][ci] for f in FAMS) / max(sum(per[f][2] for f in FAMS), 1)
            print(f"{name:12s} {crit:10s} " + " ".join(f"{v:7.3f}" for v in row) + f" {tot:8.3f}")
            res[f"{name}/{crit}"] = dict(zip(FAMS, row)) | {"total": tot}
        print()

    print("part des spans gagnants du pool qui NE chevauchent AUCUN span gold :")
    for f in FAMS:
        o, n = offgold[f]
        print(f"   {f:5s} {o}/{n} = {o/max(n,1):.3f}")
    res["hors_gold"] = {f: offgold[f][0] / max(offgold[f][1], 1) for f in FAMS}
    res["_meta"] = {"n_docs": len(ds), "M": a.M, "max_chars": a.max_chars}
    json.dump(res, open(a.out, "w"), indent=1)
    print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
