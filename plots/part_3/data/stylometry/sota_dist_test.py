"""
Upgrade SOTA 2026 du test de distribution (vs ma stylométrie de surface).
Métriques distributionnelles dans l'espace d'embeddings MedEmbed :
  - MAUVE (Pillutla 2021, réimplémenté : k-means + frontière KL ; HAUT=similaire, ∈[0,1])
  - Fréchet Embedding Distance (FED, FID-style ; BAS=similaire)
  - MMD² (RBF unbiased ; BAS=similaire)
  - C2ST sur embeddings (acc≈0.5 = indistinguable)
Référence = PARHAF (vrai hospitalier expert). Compare nos sources cliniques + baselines.
"""
import json, re, glob, sys, random, statistics
import numpy as np
_trapz = getattr(np, "trapezoid", None) or np.trapz   # numpy <2.0 = trapz, >=2.0 = trapezoid
random.seed(0)
P = "/lustre/fsn1/projects/rech/rua/uvb79kr"
B = f"{P}/onto/medembed-outputs"
N = 1000
MEDEMBED = f"{B}/medembed-v9/stage1/final"

# ---- réutilise le chargement des sources de style_test.py ----
sys.path.insert(0, "gen/stylometry")
ns = {}
exec(open("gen/stylometry/style_test.py").read().split("# ---------- (A)")[0], ns)
SOURCES = {k: v[:N] for k, v in ns["SOURCES"].items()}
REF = "PARHAF (hosp. expert)"

# ---- embeddings MedEmbed (mean-pool) ----
print("embedding MedEmbed (GPU)...", file=sys.stderr)
import torch
from transformers import AutoTokenizer, AutoModel
tok = AutoTokenizer.from_pretrained(MEDEMBED)
model = AutoModel.from_pretrained(MEDEMBED, torch_dtype=torch.float16).cuda().eval()
@torch.no_grad()
def embed(texts, bs=64):
    out = []
    for i in range(0, len(texts), bs):
        b = [t[:2000] for t in texts[i:i+bs]]
        enc = tok(b, padding=True, truncation=True, max_length=384, return_tensors="pt").to("cuda")
        h = model(**enc).last_hidden_state
        m = enc.attention_mask.unsqueeze(-1).float()
        e = (h*m).sum(1)/m.sum(1).clamp(min=1e-9)
        out.append(torch.nn.functional.normalize(e, dim=-1).float().cpu().numpy())
    return np.vstack(out)
EMB = {k: embed([t for t in v if t]) for k, v in SOURCES.items()}
for k, e in EMB.items(): print(f"  {k}: {e.shape}", file=sys.stderr)

# ---- métriques ----
def fed(X, Y):  # Fréchet Embedding Distance
    from scipy.linalg import sqrtm
    mx, my = X.mean(0), Y.mean(0); cx, cy = np.cov(X, rowvar=False), np.cov(Y, rowvar=False)
    cc = sqrtm(cx@cy); cc = cc.real if np.iscomplexobj(cc) else cc
    return float(((mx-my)**2).sum() + np.trace(cx+cy-2*cc))

def mmd2(X, Y, gamma=None):  # MMD² RBF unbiased
    from sklearn.metrics.pairwise import rbf_kernel
    if gamma is None: gamma = 1.0/X.shape[1]
    Kxx, Kyy, Kxy = rbf_kernel(X, X, gamma), rbf_kernel(Y, Y, gamma), rbf_kernel(X, Y, gamma)
    m, n = len(X), len(Y)
    np.fill_diagonal(Kxx, 0); np.fill_diagonal(Kyy, 0)
    return float(Kxx.sum()/(m*(m-1)) + Kyy.sum()/(n*(n-1)) - 2*Kxy.mean())

def mauve(X, Y, k=100, c=5.0):  # réimpl : k-means joint → histos → frontière KL → aire
    from sklearn.cluster import KMeans
    Z = np.vstack([X, Y]); lab = KMeans(k, n_init=4, random_state=0).fit_predict(Z)
    lx, ly = lab[:len(X)], lab[len(X):]
    p = np.bincount(lx, minlength=k)+1e-9; p /= p.sum()
    q = np.bincount(ly, minlength=k)+1e-9; q /= q.sum()
    def kl(a, b): return float((a*np.log(a/b)).sum())
    xs, ys = [], []
    for lam in np.linspace(1e-3, 1-1e-3, 50):
        r = lam*p+(1-lam)*q
        xs.append(np.exp(-c*kl(q, r))); ys.append(np.exp(-c*kl(p, r)))
    o = np.argsort(xs); xs = np.array(xs)[o]; ys = np.array(ys)[o]
    return float(_trapz(ys, xs))

def c2st_emb(X, Y):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    n = min(len(X), len(Y)); A = np.vstack([X[:n], Y[:n]]); y = np.r_[np.zeros(n), np.ones(n)]
    return float(cross_val_score(LogisticRegression(max_iter=1000), A, y, cv=5).mean())

R = EMB[REF]
print("\n===== SOTA distributionnel vs PARHAF (référence hospitalière réelle) =====")
print(f"{'source':30}{'MAUVE↑':>9}{'FED↓':>9}{'MMD²↓':>9}{'C2ST↓':>8}")
rows = []
for k in SOURCES:
    if k == REF: continue
    rows.append((k, mauve(R, EMB[k]), fed(R, EMB[k]), mmd2(R, EMB[k]), c2st_emb(R, EMB[k])))
for k, mv, fe, mm, c2 in sorted(rows, key=lambda x: -x[1]):  # tri par MAUVE desc (plus similaire en haut)
    print(f"{k:30}{mv:>9.3f}{fe:>9.2f}{mm:>9.4f}{c2:>8.3f}")
print("\n→ Source la plus SIMILAIRE à PARHAF = MAUVE le + haut, FED/MMD/C2ST les + bas.")
