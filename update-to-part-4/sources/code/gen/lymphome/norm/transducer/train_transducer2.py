"""Tête B, forme intégrable : le champ conditionne le DÉCODEUR, plus l'entrée caractère.

L'étape 1 concaténait le libellé dans l'entrée : `"date de diagnostic | 2017-04-15"`. Cela
marche (0.869) mais rend l'encodage dépendant du champ — dans la loss à variable latente il
faudrait ré-encoder les M spans du document une fois PAR CHAMP, soit ~26 fois le même travail.

Ici le span est encodé seul, le libellé est encodé à part, et il n'entre que par l'état initial
du décodeur. Conséquence : par document on encode les M spans UNE FOIS et on décode chaque champ
dessus. C'est ce qui rend la vraisemblance marginale calculable.

L'invariant tient toujours : le champ n'entre que par son libellé, en texte, donc zéro paramètre
par champ et par classe.

Ce script ne teste qu'une chose : **le déplacement du conditionnement ne coûte rien en qualité.**
Même paires, même split, mêmes epochs que l'étape 1. Barre à battre : 0.869.

  python train_transducer2.py --epochs 12
"""
import argparse
import json
import random
import time
from collections import defaultdict

import torch
import torch.nn as nn
import torch.nn.functional as F

from train_transducer import PAD, BOS, EOS, MAXOUT, build_vocab, pad

MAXSPAN, MAXLAB = 200, 60


USE_ANCHOR = False      # mis à True par --anchor


def enc_span(r, stoi):
    """Texte du span, précédé de l'en-tête de son document source si demandé.

    L'annotateur enregistrait l'en-tête dans `source_document`, jamais dans `span` :
    0 span gold DATE sur 6 275 ne tombe sur un en-tête, alors que 55,7 % des cibles DATE
    VALENT une date d'en-tête. L'information n'était pas absente, elle était dans une
    colonne qu'on ne lisait pas. Concaténer la rend disponible sans qu'aucun pointeur
    n'ait à viser l'en-tête.
    """
    s = (r.get("sd", "") + " | " + r["span"]) if USE_ANCHOR and r.get("sd") else r["span"]
    return [stoi.get(c, 3) for c in s[:MAXSPAN]] or [3]


def enc_lab(r, stoi):
    return [stoi.get(c, 3) for c in r["label"][:MAXLAB]] or [3]


def enc_out(r, stoi):
    return [BOS] + [stoi.get(c, 3) for c in r["value"][:MAXOUT]] + [EOS]


class Transducer2(nn.Module):
    def __init__(self, V, d=128, h=256, hf=128):
        super().__init__()
        self.emb = nn.Embedding(V, d, padding_idx=PAD)
        self.enc = nn.GRU(d, h, batch_first=True, bidirectional=True)      # span, sans le champ
        self.fld = nn.GRU(d, hf, batch_first=True, bidirectional=True)     # libellé du champ
        self.h0 = nn.Linear(2 * h + 2 * hf, h)
        self.dec = nn.GRU(d + 2 * h, h, batch_first=True)
        self.att = nn.Linear(2 * h + h, h)
        self.att_v = nn.Linear(h, 1)
        self.out = nn.Linear(h + 2 * h, V)

    @staticmethod
    def _pool(e, mask):
        return e.masked_fill(mask.unsqueeze(-1), 0).sum(1) / (~mask).sum(1, keepdim=True).clamp(min=1)

    def encode_span(self, x):
        """[B,T] -> e [B,T,2h], mask [B,T], pooled [B,2h]. Indépendant du champ : partageable."""
        e, _ = self.enc(self.emb(x))
        mask = (x == PAD)
        return e, mask, self._pool(e, mask)

    def encode_field(self, xf):
        e, _ = self.fld(self.emb(xf))
        return self._pool(e, (xf == PAD))

    def init_state(self, pooled, fvec, extra=None):
        """`extra` [B,h] : apport optionnel de `span_rep` (contextuel, côté GLiNER).

        Il est ajouté AVANT la tanh et sa projection est initialisée à zéro côté appelant,
        de sorte qu'un checkpoint entraîné sans lui redonne exactement le même état initial.
        C'est ce qui fait remonter le gradient de la tête B dans l'encodeur : sans cet apport,
        B ne lit que des caractères et ne peut jamais corriger une frontière de span.
        """
        z = self.h0(torch.cat([pooled, fvec], -1))
        return torch.tanh(z if extra is None else z + extra).unsqueeze(0)

    def step(self, y_emb, h, e, mask):
        q = h[-1].unsqueeze(1).expand(-1, e.shape[1], -1)
        a = self.att_v(torch.tanh(self.att(torch.cat([e, q], -1)))).squeeze(-1)
        a = torch.softmax(a.masked_fill(mask, -1e9), -1)
        ctx = (a.unsqueeze(-1) * e).sum(1)
        o, h = self.dec(torch.cat([y_emb, ctx], -1).unsqueeze(1), h)
        return self.out(torch.cat([o.squeeze(1), ctx], -1)), h

    def _roll(self, e, mask, h, ye, steps):
        logits = []
        for t in range(steps):
            lg, h = self.step(ye[:, t], h, e, mask)
            logits.append(lg)
        return torch.stack(logits, 1)

    def forward(self, x, xf, y):
        e, mask, pooled = self.encode_span(x)
        h = self.init_state(pooled, self.encode_field(xf))
        return self._roll(e, mask, h, self.emb(y), y.shape[1] - 1)

    def logprob(self, e, mask, h, y):
        """log P(y | span, champ), sommé sur les caractères. [B]"""
        lg = self._roll(e, mask, h, self.emb(y), y.shape[1] - 1)
        lp = torch.log_softmax(lg, -1).gather(-1, y[:, 1:].unsqueeze(-1)).squeeze(-1)
        return (lp * (y[:, 1:] != PAD)).sum(-1)

    @torch.no_grad()
    def greedy(self, x, xf, itos):
        e, mask, pooled = self.encode_span(x)
        h = self.init_state(pooled, self.encode_field(xf))
        tok = torch.full((x.shape[0],), BOS, device=x.device)
        done = torch.zeros(x.shape[0], dtype=torch.bool, device=x.device)
        outs = [[] for _ in range(x.shape[0])]
        for _ in range(MAXOUT + 1):
            lg, h = self.step(self.emb(tok), h, e, mask)
            tok = lg.argmax(-1)
            for i, t in enumerate(tok.tolist()):
                if not done[i]:
                    if t == EOS:
                        done[i] = True
                    elif t > 3:
                        outs[i].append(itos[t])
            if bool(done.all()):
                break
        return ["".join(o) for o in outs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default="gen/lymphome/norm/transducer/pairs.json")
    ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--bs", type=int, default=256)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--anchor", action="store_true",
                    help="entrée = en-tête du document source ⊕ span, au lieu du span seul")
    ap.add_argument("--out", default="gen/lymphome/norm/transducer/transducer2.pt")
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0); random.seed(0)
    global USE_ANCHOR; USE_ANCHOR = a.anchor
    print(f"entrée = {'EN-TÊTE ⊕ span' if USE_ANCHOR else 'span seul'}", flush=True)
    # Sans ce garde-fou, une ancre vide (regex cassée, champ absent) fait rendre au bras
    # « avec ancre » exactement le chiffre du bras de référence, sans qu'aucune erreur ne
    # soit levée : l'expérience paraît tourner et ne teste rien. C'est arrivé.


    rows = json.load(open(a.pairs, encoding="utf-8"))
    tr = [r for r in rows if r["split"] == "train"]
    te = [r for r in rows if r["split"] == "test"]
    if USE_ANCHOR:
        frac = sum(1 for r in tr if r.get("sd")) / max(len(tr), 1)
        print(f"paires portant une ancre : {frac:.1%}", flush=True)
        assert frac > 0.5, (f"--anchor demandé mais seulement {frac:.1%} des paires ont "
                            "une ancre : l'expérience ne testerait rien.")
    stoi, itos = build_vocab(tr)
    print(f"train={len(tr):,} test={len(te):,} vocab={len(itos)} device={dev}", flush=True)

    model = Transducer2(len(itos)).to(dev)
    print(f"paramètres : {sum(p.numel() for p in model.parameters())/1e6:.2f}M", flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, a.lr, total_steps=a.epochs * (len(tr) // a.bs + 1))

    def batch_of(b):
        return (pad([enc_span(r, stoi) for r in b], MAXSPAN).to(dev),
                pad([enc_lab(r, stoi) for r in b], MAXLAB).to(dev),
                pad([enc_out(r, stoi) for r in b], MAXOUT + 2).to(dev))

    def evaluate():
        model.eval()
        per = defaultdict(lambda: [0, 0])
        with torch.no_grad():
            for i in range(0, len(te), 512):
                b = te[i:i + 512]
                x, xf, _ = batch_of(b)
                for r, p in zip(b, model.greedy(x, xf, itos)):
                    per[r["fam"]][0] += int(p == r["value"]); per[r["fam"]][1] += 1
        model.train()
        tot = [sum(v) for v in zip(*per.values())]
        return per, tot[0] / max(tot[1], 1)

    t0 = time.time()
    for ep in range(a.epochs):
        random.shuffle(tr); run = n = 0
        for i in range(0, len(tr), a.bs):
            x, xf, y = batch_of(tr[i:i + a.bs])
            logits = model(x, xf, y)
            loss = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), y[:, 1:].reshape(-1),
                                   ignore_index=PAD)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step()
            run += float(loss); n += 1
        per, acc = evaluate()
        det = "  ".join(f"{f}={c/max(t,1):.3f}" for f, (c, t) in sorted(per.items()))
        print(f"ep{ep} loss={run/n:.4f}  EXACT-MATCH test={acc:.4f}   {det}  ({(time.time()-t0)/60:.1f}min)",
              flush=True)
        torch.save({"model": model.state_dict(), "stoi": stoi, "itos": itos, "acc": acc}, a.out)

    print("\n=== conditionnement au décodeur (intégrable) vs à l'entrée (étape 1)")
    print(f"    étape 1 (libellé dans l'entrée) : 0.869   CAT 0.914  DATE 0.733  NUM 0.832  ORD 0.969")
    print(f"    intégrable (libellé au décodeur): {acc:.3f}   {det}")


if __name__ == "__main__":
    main()
