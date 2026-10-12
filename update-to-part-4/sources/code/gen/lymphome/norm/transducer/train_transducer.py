"""Transducteur span -> valeur canonique, appris. Remplace `taxonomy.py` (300 lignes écrites à la main).

Entrée  : "<libellé du champ> | <texte du span>"   (caractères)
Sortie  : la valeur canonique, caractère par caractère.

Aucun paramètre par champ ni par classe : le champ n'entre que par son libellé, en texte.
Le même modèle marche donc sur un autre schéma, une autre langue, une classe jamais vue.

Test décisif : battre `taxonomy.normalize_target` sur exactement les mêmes paires.
Si on perd de plus de ~2 points, la promesse "aucune normalisation écrite à la main" ne tient
pas à cette échelle de données, et le design est refusé.
"""
import argparse
import json
import random
import time
from collections import defaultdict

import torch
import torch.nn as nn
import torch.nn.functional as F

PAD, BOS, EOS = 0, 1, 2
MAXIN, MAXOUT = 160, 32


def build_vocab(rows):
    chars = set()
    for r in rows:
        chars |= set(r["label"]) | set(r["span"]) | set(r["value"])
    itos = ["<pad>", "<bos>", "<eos>", "<unk>"] + sorted(chars)
    return {c: i for i, c in enumerate(itos)}, itos


def enc_in(r, stoi):
    s = f"{r['label']} | {r['span']}"[:MAXIN]
    return [stoi.get(c, 3) for c in s]


def enc_out(r, stoi):
    return [BOS] + [stoi.get(c, 3) for c in r["value"][:MAXOUT]] + [EOS]


def pad(seqs, n):
    m = max(len(s) for s in seqs)
    return torch.tensor([s + [PAD] * (m - len(s)) for s in seqs])[:, :n]


class Transducer(nn.Module):
    """Encodeur GRU bidirectionnel + décodeur GRU avec attention additive."""

    def __init__(self, V, d=128, h=256):
        super().__init__()
        self.emb = nn.Embedding(V, d, padding_idx=PAD)
        self.enc = nn.GRU(d, h, batch_first=True, bidirectional=True)
        self.dec = nn.GRU(d + 2 * h, h, batch_first=True)
        self.att = nn.Linear(2 * h + h, h)
        self.att_v = nn.Linear(h, 1)
        self.out = nn.Linear(h + 2 * h, V)
        self.h0 = nn.Linear(2 * h, h)

    def encode(self, x):
        e, _ = self.enc(self.emb(x))
        mask = (x == PAD)
        h = self.h0(e.masked_fill(mask.unsqueeze(-1), 0).sum(1) / (~mask).sum(1, keepdim=True).clamp(min=1))
        return e, mask, torch.tanh(h).unsqueeze(0)

    def step(self, y_emb, h, e, mask):
        q = h[-1].unsqueeze(1).expand(-1, e.shape[1], -1)
        a = self.att_v(torch.tanh(self.att(torch.cat([e, q], -1)))).squeeze(-1)
        a = torch.softmax(a.masked_fill(mask, -1e9), -1)
        ctx = (a.unsqueeze(-1) * e).sum(1)
        o, h = self.dec(torch.cat([y_emb, ctx], -1).unsqueeze(1), h)
        return self.out(torch.cat([o.squeeze(1), ctx], -1)), h

    def forward(self, x, y):
        e, mask, h = self.encode(x)
        ye = self.emb(y)
        logits = []
        for t in range(y.shape[1] - 1):
            lg, h = self.step(ye[:, t], h, e, mask)
            logits.append(lg)
        return torch.stack(logits, 1)

    @torch.no_grad()
    def greedy(self, x, itos):
        e, mask, h = self.encode(x)
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
    ap.add_argument("--out", default="gen/lymphome/norm/transducer/transducer.pt")
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0); random.seed(0)

    rows = json.load(open(a.pairs, encoding="utf-8"))
    tr = [r for r in rows if r["split"] == "train"]
    te = [r for r in rows if r["split"] == "test"]
    stoi, itos = build_vocab(tr)
    print(f"train={len(tr):,} test={len(te):,} vocab={len(itos)} device={dev}", flush=True)

    model = Transducer(len(itos)).to(dev)
    print(f"paramètres : {sum(p.numel() for p in model.parameters())/1e6:.2f}M", flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, a.lr, total_steps=a.epochs * (len(tr) // a.bs + 1))

    def evaluate():
        model.eval()
        per = defaultdict(lambda: [0, 0])
        for i in range(0, len(te), 512):
            b = te[i:i + 512]
            x = pad([enc_in(r, stoi) for r in b], MAXIN).to(dev)
            for r, p in zip(b, model.greedy(x, itos)):
                per[r["fam"]][0] += int(p == r["value"]); per[r["fam"]][1] += 1
        model.train()
        tot = [sum(v) for v in zip(*per.values())]
        return per, tot[0] / max(tot[1], 1)

    t0 = time.time()
    for ep in range(a.epochs):
        random.shuffle(tr); run = n = 0
        for i in range(0, len(tr), a.bs):
            b = tr[i:i + a.bs]
            x = pad([enc_in(r, stoi) for r in b], MAXIN).to(dev)
            y = pad([enc_out(r, stoi) for r in b], MAXOUT + 2).to(dev)
            logits = model(x, y)
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

    print("\n=== VERDICT : transducteur appris vs taxonomy.py écrit à la main")
    print(f"    taxonomy.py  : 0.630   (CAT 0.501  DATE 0.663  NUM 0.714  ORD 0.902)")
    print(f"    transducteur : {acc:.3f}   {det}")


if __name__ == "__main__":
    main()
