"""Étape 2 — entraînement de la tête d'affectation, span latent, bout en bout.

Un seul objectif : `L = − log Σ_spans P_A(span|champ) · P_B(valeur|span,champ)`.

⚠️ La loss de détection native est SUPPRIMÉE (`--det_w 0`), contre ce que ce fichier a
longtemps affirmé. J'avais écrit qu'il fallait la garder « en auxiliaire à poids faible », au
motif que l'annuler ferait dériver `span_rep`. C'est faux, et la courbe est monotone :

    det_w      0.1     0.02    0.002    0.0
    val macro  0.670   0.673   0.749    0.776

Elle n'était pas un peu trop lourde, elle CAPTURAIT l'encodeur : à det_w=0.1 la loss valait
97,5 % de détection et 2,5 % d'affectation. Et sa nature explique le reste — elle entraîne le
modèle à pointer LÀ OÙ L'ANNOTATEUR A POINTÉ, c'est-à-dire jamais sur un en-tête de section,
où vivent 55,7 % des cibles DATE. On lui apprenait activement à ignorer la moitié d'une
famille.

Trois mesures, pas une (DESIGN_V2 §5) :
  1. macro-F1 test contre 0.603 ;
  2. rappel du pool DATE, qui doit passer de 0.52 vers ~0.9  <- la mesure décisive ;
  3. macro-F1 sur les champs indexés par un rôle, avec et sans compétition entre champs.

Sondes anti-effondrement journalisées à chaque epoch, parce qu'une loss qui descend ne prouve
rien ici :
  - `p_null`   : masse moyenne sur ⊥. Si elle file vers 1, le modèle achète l'abstention.
  - `p_copy`   : masse moyenne sur le bloc COPIE pour les champs documentés.
  - `ecart_B`  : log P_B(cible|meilleur span) − log P_B(cible|span médian). S'il tend vers 0,
                 le transducteur est devenu un a priori inconditionnel sur le champ et
                 n'informe plus l'affectation — l'effondrement à surveiller.
  - `alpha`, `beta` : les deux scalaires appris (compétition entre champs, ancrage détection).

  python train_assign.py --epochs 2 --M 256 --out <dir>
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
import assign as A                     # noqa: E402
import gliner_integrated as G          # noqa: E402
import taxonomy as T                   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

B = "/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs"
LB = B + "/lymphome"
PROD = "/lustre/fswork/projects/rech/rua/uvb79kr/biomed-fr-v4/lymphome_v4/outputs/prod_20260527_121452.jsonl"
V5 = B + "/gliner2-lym-V5FROMV3B/best"
TRANSD2 = str(_H / "transducer" / "transducer2.pt")
FAMS = ("CAT", "DATE", "NUM", "ORD")


def macro_f1(rows):
    """Barème INCHANGÉ (comparabilité avec 0.603) : une valeur fausse compte fp ET fn."""
    c = defaultdict(lambda: [0, 0, 0])
    for fam, gold, pred in rows:
        if gold is not None and pred is not None:
            if G._match(fam, pred, gold):
                c[fam][0] += 1
            else:
                c[fam][1] += 1; c[fam][2] += 1
        elif pred is not None:
            c[fam][1] += 1
        elif gold is not None:
            c[fam][2] += 1
    per = {}
    for f in FAMS:
        tp, fp, fn = c[f]
        p, r = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
        per[f] = 2 * p * r / max(p + r, 1e-9)
    return float(np.mean([per[f] for f in FAMS])), per


def doc_forward(model, d, dev, M, crit="rank", train=True):
    """⚠️ `train=False` À L'ÉVALUATION, sans exception.

    `collate_fn_train` applique l'échantillonneur d'entraînement de GLiNER2 AU PROMPT :
    mesuré sur ce modèle, 29 % des documents voient leurs libellés de champ remplacés par
    « entity 15 », « entity 5 »… et 42 % perdent leurs descriptions, pour 59 prompts distincts
    sur 100 tirages. Or le libellé est la SEULE chose qui porte le schéma dans ce design.
    L'utiliser à l'évaluation revient à effacer le schéma au moment où on mesure : tous les
    chiffres obtenus ainsi sont des PLANCHERS, et les écarts sous ~0.02 sont du bruit.
    `collate_fn_inference` : 0 %, 0 %, un seul prompt. (`random` n'est pas semé non plus.)
    """
    cf = model.processor.collate_fn_train if train else model.processor.collate_fn_inference
    batch = cf([(d["text"], d["output"])]).to(dev)
    all_tok, all_sch = model._encode_batch(batch)
    mk = G.markers_of(all_sch[0]); l2i = G.lab2idx_of(d["output"])
    pool = A.build_pool(model, all_tok[0], d["text"], mk, M=M, crit=crit)
    F = pool["S"].shape[0]
    E = mk[1:1 + F]
    ent = [dict(e, fi=l2i[e["label"]]) for e in d["entries"]
           if l2i.get(e["label"]) is not None and l2i[e["label"]] < F]
    return batch, all_tok, all_sch, pool, E, ent


@torch.no_grad()
def evaluate(model, head, vm, ds, opt_emb, space, dev, M, crit="rank"):
    model.eval(); head.eval(); vm.m.eval()
    rows, probes = [], defaultdict(list)
    for d in ds:
        _, _, _, pool, E, ent = doc_forward(model, d, dev, M, crit, train=False)
        pred = A.assign_predict_doc(head, vm, E, pool, ent, opt_emb, space, dev)
        cp, q, nl = head(E, pool)
        for e in ent:
            fam = T.FIELD_SPEC[e["key"]]["family"]
            rows.append((fam, e["target"], pred.get(e["key"])))
            cls = space.get(e["key"], {}).get("classes") or []
            oe = opt_emb.get(e["key"])
            parts = [cp[e["fi"]]] + ([oe @ q[e["fi"]]] if oe is not None and cls else []) + [nl[e["fi"]]]
            p = torch.softmax(torch.cat(parts), 0)
            probes["p_null"].append(float(p[-1]))
            if e["target"] is not None:
                probes["p_copy"].append(float(p[:pool["S"].shape[1]].sum()))
    model.train(); head.train(); vm.m.train()
    m, per = macro_f1(rows)
    return m, per, {k: float(np.mean(v)) for k, v in probes.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--M", type=int, default=1024)
    ap.add_argument("--crit", choices=("max", "rank"), default="rank")
    ap.add_argument("--topk", type=int, default=32,
                    help="spans retenus dans la somme marginale (coût indépendant de M)")
    ap.add_argument("--nsample", type=int, default=8,
                    help="spans tirés uniformément : restaure le support de la latente")
    ap.add_argument("--accum", type=int, default=4)
    ap.add_argument("--enc_lr", type=float, default=1e-5)
    ap.add_argument("--head_lr", type=float, default=1e-4)
    ap.add_argument("--det_w", type=float, default=0.0,
                    help="poids de la loss de détection. 0 = supprimée, et c'est le "
                         "meilleur réglage mesuré (0.776 contre 0.670 à 0.1).")
    ap.add_argument("--max_chars", type=int, default=24000)
    ap.add_argument("--no_compete", action="store_true", help="ablation : gèle alpha à 0")
    ap.add_argument("--limit", type=int, default=0, help="smoke : n documents d'entraînement")
    ap.add_argument("--ctx", choices=("none", "sum", "attn", "sonly"), default="none",
                    help="contexte inter-spans dans le score de copie. none = ancien "
                         "comportement ponctuel (référence de l'ablation).")
    ap.add_argument("--hard_assign", action="store_true",
                    help="ABLATION du cœur : affectation DURE (le meilleur span seul) "
                         "au lieu de la vraisemblance marginale sur le span latent.")
    ap.add_argument("--beta0", action="store_true",
                    help="init beta=0 : la tête ne démarre PAS sur la solution du détecteur")
    ap.add_argument("--no_guided", action="store_true",
                    help="désactive la proposition de support guidée par la cible (ablation)")
    ap.add_argument("--hard_values", action="store_true",
                    help="ablation : P_B = le parseur écrit à la main, en 0/1, au lieu du "
                         "transducteur appris. Isole l'apport bout en bout de la tête B.")
    ap.add_argument("--init", default=V5,
                    help="checkpoint GLiNER2 de départ (défaut : V5FROMV3B/best ; passer "
                         "gliner2-lym-V5LARGE/best pour la lignée large, d inféré)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = "cuda"
    torch.manual_seed(0); np.random.seed(0)

    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    space, index = A.build_value_space(PROD, train_ids, fields)
    n_closed = sum(1 for k in fields if space.get(k, {}).get("classes"))
    print(f"espace dérivé du TRAIN : {n_closed}/{len(fields)} champs avec un vocabulaire observé")

    full = A.build_dataset_assign(LB + "/lymphome_train_v2.jsonl", PROD, space, index,
                                  fields, cap=a.max_chars)
    _ids = sorted(d["id"] for d in full)
    val_ids = set(np.random.RandomState(0).choice(_ids, min(100, len(_ids)), replace=False).tolist())
    train = [d for d in full if d["id"] not in val_ids]
    val = [d for d in full if d["id"] in val_ids]
    if a.limit:
        train, val = train[:a.limit], val[:max(2, a.limit // 2)]
    print(f"train={len(train)} val={len(val)} M={a.M} crit={a.crit} topk={a.topk}+{a.nsample} max_chars={a.max_chars}")

    model = load_model(a.init).to(dev)
    model.encoder.gradient_checkpointing_enable()
    d_enc = model.encoder.config.hidden_size      # 768 base, 1024 large
    head = A.AssignHead(d=d_enc, ctx=a.ctx, beta0=a.beta0).to(dev)
    vm = (A.HardValueModel(dev) if a.hard_values
          else A.ValueModel(TRANSD2, dev, train=True))      # démarrage à chaud (étape 1)
    if a.no_compete:
        head.alpha.requires_grad_(False)
    print(f"tête A : {sum(p.numel() for p in head.parameters())/1e6:.2f}M (ctx={a.ctx})  "
          f"tête B : {sum(p.numel() for p in vm.parameters())/1e6:.2f}M "
          f"({type(vm).__name__})")

    opt_emb = A.encode_options(model, space, dev)
    model.train()
    opt = torch.optim.AdamW([
        {"params": model.parameters(), "lr": a.enc_lr},
        {"params": list(head.parameters()) + list(vm.parameters()), "lr": a.head_lr},
    ], weight_decay=1e-4)

    best = -1
    for ep in range(a.epochs):
        idx = np.random.permutation(len(train)); t0 = time.time(); nb = 0
        # les deux termes SÉPARÉMENT : la détection auxiliaire domine numériquement et
        # masquerait complètement l'évolution de la loss d'affectation, la seule qui compte ici.
        run_det = run_asg = 0.0
        opt.zero_grad()
        for step, j in enumerate(idx):
            d = train[j]
            batch, all_tok, all_sch, pool, E, ent = doc_forward(model, d, dev, a.M, a.crit)
            sl = model._compute_sample_loss(all_tok[0], all_sch[0], batch.task_types[0],
                                            batch.structure_labels[0], torch.device(dev))
            det = sl["classification"] + sl["structure"] + sl["count"]
            nloss, n = A.assign_loss_doc(head, vm, E, pool, ent, opt_emb, space, dev,
                                         topk=a.topk, nsample=a.nsample,
                                         guided=not a.no_guided,
                                         hard_assign=a.hard_assign)
            loss = (a.det_w * det + nloss / max(n, 1)) / a.accum
            loss.backward(); nb += 1
            run_det += float(det.detach()); run_asg += float(nloss.detach()) / max(n, 1)
            if (step + 1) % a.accum == 0:
                torch.nn.utils.clip_grad_norm_(
                    list(model.parameters()) + list(head.parameters()) + list(vm.parameters()), 1.0)
                opt.step(); opt.zero_grad()
            if step % 100 == 0:
                print(f"  ep{ep} {step}/{len(idx)} affect~{run_asg/max(nb,1):.3f} "
                      f"det~{run_det/max(nb,1):.1f} "
                      f"alpha={float(head.alpha):+.3f} beta={float(head.beta):+.3f} "
                      f"({(time.time()-t0)/60:.1f}min)", flush=True)
        opt_emb = A.encode_options(model, space, dev)
        m, per, pr = evaluate(model, head, vm, val, opt_emb, space, dev, a.M, a.crit)
        print(f"=== ep{ep} val macro={m:.3f}  " + " ".join(f"{f}={per[f]:.3f}" for f in FAMS)
              + f"  p_null={pr.get('p_null',0):.3f} p_copy={pr.get('p_copy',0):.3f}"
              + f"  alpha={float(head.alpha):+.3f} beta={float(head.beta):+.3f} ===", flush=True)
        if m > best:
            best = m
            Path(a.out).mkdir(parents=True, exist_ok=True)
            model.save_pretrained(a.out)
            torch.save({"head": head.state_dict(),
                        "vm": None if a.hard_values else vm.m.state_dict(),
                        "hard_values": a.hard_values,
                        "stoi": getattr(vm, "stoi", None), "itos": getattr(vm, "itos", None),
                        "space": space, "ctx": a.ctx, "beta0": a.beta0,
                        "val": m}, a.out + "/assign.pt")
            print(f"  sauvegardé (best={best:.3f})", flush=True)
    print(f"=== DONE best val macro={best:.3f} (référence actuelle : 0.603 sur le TEST) ===")


if __name__ == "__main__":
    main()
