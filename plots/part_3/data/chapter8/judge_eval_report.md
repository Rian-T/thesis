# Éval LLM-judge — v3c-pristine vs SE-v1 (OOD, reference-free)

**Fiabilité juge (honeypots, recadrée : rejet-bruit + reconnaissance-type, hors PARSE_FAIL)** : 192/197 = **0.975** ✅ valide

**PARSE_FAIL** : 566/157253 = 0.4% (bruit non-biaisé, comptés pas_une_entite)

**Distribution verdicts** : {'mauvais_type': 73845, 'pas_une_entite': 75230, 'correct': 5466, 'mauvaise_frontiere': 2712}

**Gold pooled (correct)** : common=3805, novel=1621


## MAP par modèle × régime (+ pooled recall, précision@seuil)

| Modèle | régime | MAP | pooled recall | P@0.3 | P@0.5 | P@0.7 | #queries |
|---|---|---|---|---|---|---|---|
| v3c-pristine | common | **0.565** | 0.608 | 0.573 | 0.690 | 0.794 | 1496 |
| v3c-pristine | novel | **0.456** | 0.610 | 0.157 | 0.210 | 0.301 | 682 |
| v3c-stage2-mix50 | common | **0.459** | 0.475 | 0.784 | 0.857 | 0.849 | 1496 |
| v3c-stage2-mix50 | novel | **0.456** | 0.614 | 0.234 | 0.308 | 0.346 | 682 |
| v3b-pristine | common | **0.581** | 0.630 | 0.478 | 0.610 | 0.726 | 1496 |
| v3b-pristine | novel | **0.474** | 0.630 | 0.137 | 0.167 | 0.246 | 682 |
| SE-v1 | common | **0.567** | 0.642 | 0.259 | 0.613 | 0.887 | 1496 |
| SE-v1 | novel | **0.377** | 0.637 | 0.056 | 0.149 | 0.000 | 682 |
| gliner2-large | common | **0.494** | 0.583 | 0.459 | 0.523 | 0.583 | 1496 |
| gliner2-large | novel | **0.281** | 0.473 | 0.058 | 0.057 | 0.064 | 682 |
| v3c-mcbio-e1 | common | **0.478** | 0.523 | 0.531 | 0.662 | 0.771 | 1496 |
| v3c-mcbio-e1 | novel | **0.333** | 0.561 | 0.084 | 0.167 | 0.378 | 682 |
| v3c-medembed-e1 | common | **0.517** | 0.565 | 0.623 | 0.751 | 0.844 | 1496 |
| v3c-medembed-e1 | novel | **0.382** | 0.558 | 0.090 | 0.135 | 0.484 | 682 |
| v3d-e1 | common | **0.530** | 0.590 | 0.627 | 0.748 | 0.828 | 1496 |
| v3d-e1 | novel | **0.358** | 0.463 | 0.105 | 0.209 | 0.417 | 682 |
| v3d | common | **0.535** | 0.573 | 0.658 | 0.760 | 0.846 | 1496 |
| v3d | novel | **0.302** | 0.309 | 0.182 | 0.221 | 0.465 | 682 |
| v3e-pristine | common | **0.487** | 0.531 | 0.646 | 0.750 | 0.839 | 1496 |
| v3e-pristine | novel | **0.356** | 0.534 | 0.195 | 0.305 | 0.429 | 682 |
| v3e-large | common | **0.587** | 0.637 | 0.566 | 0.661 | 0.757 | 1496 |
| v3e-large | novel | **0.350** | 0.609 | 0.168 | 0.181 | 0.241 | 682 |
| v3e-base-5ep | common | **0.486** | 0.516 | 0.673 | 0.766 | 0.842 | 1496 |
| v3e-base-5ep | novel | **0.340** | 0.366 | 0.207 | 0.299 | 0.404 | 682 |
| v3e-large-5ep | common | **0.555** | 0.585 | 0.527 | 0.608 | 0.712 | 1496 |
| v3e-large-5ep | novel | **0.313** | 0.410 | 0.219 | 0.291 | 0.341 | 682 |
| gliner-biomed | common | **0.386** | 0.389 | 0.400 | 0.465 | 0.533 | 1496 |
| gliner-biomed | novel | **0.125** | 0.189 | 0.101 | 0.110 | 0.121 | 682 |

## Δoverfit = MAP(common) − MAP(novel)

| Modèle | MAP common | MAP novel | Δoverfit |
|---|---|---|---|
| v3c-pristine | 0.565 | 0.456 | **+0.109** |
| v3c-stage2-mix50 | 0.459 | 0.456 | **+0.003** |
| v3b-pristine | 0.581 | 0.474 | **+0.107** |
| SE-v1 | 0.567 | 0.377 | **+0.190** |
| gliner2-large | 0.494 | 0.281 | **+0.213** |
| v3c-mcbio-e1 | 0.478 | 0.333 | **+0.145** |
| v3c-medembed-e1 | 0.517 | 0.382 | **+0.135** |
| v3d-e1 | 0.530 | 0.358 | **+0.172** |
| v3d | 0.535 | 0.302 | **+0.233** |
| v3e-pristine | 0.487 | 0.356 | **+0.131** |
| v3e-large | 0.587 | 0.350 | **+0.237** |
| v3e-base-5ep | 0.486 | 0.340 | **+0.146** |
| v3e-large-5ep | 0.555 | 0.313 | **+0.242** |
| gliner-biomed | 0.386 | 0.125 | **+0.260** |

## Head-to-head (A − B) + bootstrap CI 95%

| A vs B | common | novel |
|---|---|---|
| v3c-pristine − v3b-pristine | ΔMAP=-0.016 CI95[-0.038,+0.007] ≈ non signif | ΔMAP=-0.018 CI95[-0.053,+0.017] ≈ non signif |
| v3c-stage2-mix50 − v3c-pristine | ΔMAP=-0.106 CI95[-0.131,-0.080] ✅ signif | ΔMAP=-0.000 CI95[-0.035,+0.035] ≈ non signif |
| v3c-pristine − SE-v1 | ΔMAP=-0.003 CI95[-0.026,+0.021] ≈ non signif | ΔMAP=+0.079 CI95[+0.048,+0.112] ✅ signif |
| v3c-stage2-mix50 − SE-v1 | ΔMAP=-0.109 CI95[-0.133,-0.084] ✅ signif | ΔMAP=+0.078 CI95[+0.044,+0.113] ✅ signif |
| v3b-pristine − SE-v1 | ΔMAP=+0.013 CI95[-0.010,+0.036] ≈ non signif | ΔMAP=+0.097 CI95[+0.064,+0.130] ✅ signif |

## Interprétation

- Δoverfit v3c-pristine = **+0.109** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3c-stage2-mix50 = **+0.003** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3b-pristine = **+0.107** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit SE-v1 = **+0.190** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit gliner2-large = **+0.213** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3c-mcbio-e1 = **+0.145** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3c-medembed-e1 = **+0.135** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3d-e1 = **+0.172** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3d = **+0.233** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3e-pristine = **+0.131** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3e-large = **+0.237** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3e-base-5ep = **+0.146** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit v3e-large-5ep = **+0.242** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
- Δoverfit gliner-biomed = **+0.260** (Δ grand = chute sur types nouveaux = plus spécialisé-convention).
