"""Publie le modèle eCRF (têtes + transducteur) sur le Hub, autonome et exécutable.

Ce que le dépôt publié contient, et pourquoi :
  model.safetensors / config.json / encoder_config   le GLiNER2 finetuné (chargé par `gliner2`)
  assign.pt          les têtes : tête A, transducteur, vocabulaire dérivé, alphabet
  field_schema.json  les 89 champs (libellé + description + section) — le schéma est du TEXTE
  modeling_assign.py tout le code d'inférence, sans dépendance au dépôt de recherche
  predict.py         un exemple exécutable
  README.md          les résultats, les limites, et ce qui n'a pas été vérifié

Vérification faite avant publication : la seule divergence de notre fork de GLiNER2 est un
patch de focal loss dans la LOSS D'ENTRAÎNEMENT, derrière `GLINER_FOCAL`, désactivé par
défaut. L'inférence est identique à l'upstream, et `modeling_assign.py` n'utilise que
`compute_span_rep`, `count_embed`, `_encode_batch`, `processor`, `encoder`.

  python build_upload.py [--dry_run]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from labels import LABELS  # noqa: E402

B = "/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs"
# (les chemins/repos vivent dans VARIANTS ci-dessous)


# Les trois variantes publiées. `scores` = macro/CAT/DATE/NUM/ORD sur les 410 documents
# de test, barème inchangé. `cap` = fenêtre de lecture avec laquelle le modèle a été
# ENTRAÎNÉ (et qui est le défaut à l'inférence).
VARIANTS = {
    "ecrf": dict(
        src=f"{B}/gliner2-lym-assign-best3ep", repo="rntc/mc-bio-gliner-lymphome-ecrf",
        params="150 M", model_name="modernbert-bio-fr-150m", cap=24000,
        scores=(0.786, 0.817, 0.684, 0.765, 0.877)),
    "ecrf-v2": dict(
        src=f"{B}/gliner2-lym-assign-base45k", repo="rntc/mc-bio-gliner-lymphome-ecrf-v2",
        params="150 M", model_name="modernbert-bio-fr-150m", cap=45000,
        scores=(0.809, 0.836, 0.742, 0.775, 0.883)),
    "ecrf-large": dict(
        src=f"{B}/gliner2-lym-assign-large", repo="rntc/mc-bio-gliner-lymphome-ecrf-large",
        params="395 M", model_name="modernbert-bio-fr-395m", cap=45000,
        scores=(0.815, 0.836, 0.738, 0.791, 0.896)),
}

README = """---
license: mit
language: fr
library_name: gliner2
tags: [gliner, gliner2, information-extraction, ecrf, biomedical, french, lymphoma, clinical]
---

# @@NAME@@

Extraction de 89 champs d'eCRF depuis un dossier patient longitudinal français
(~22 000 caractères, plusieurs comptes-rendus successifs). Encodeur de @@PARAMS@@ paramètres,
un seul passage sur le document.

La sortie est une valeur canonique. Selon le champ, elle coïncide avec le texte du span
(« veuve » → `veuve`) ou en diffère (« patiente » → `femme`, « le 8 avril 2017 » →
`2017-04-15`, « phénotype non germinal » → `NGC`).

## Utilisation

```bash
pip install gliner2 torch huggingface_hub
```

```python
from modeling_assign import ECRFExtractor          # fourni dans ce dépôt

m = ECRFExtractor.from_pretrained("@@REPO@@", device="cuda")
ecrf = m.extract(open("dossier.txt").read())
```

`extract` rend, pour chacun des 81 champs non textuels :

```python
{
  "value": "2017-04-15",               # None si le modèle s'abstient
  "span":  "le 8 avril 2017",          # span source
  "start": 1247, "end": 1262,          # offsets caractère dans le texte
  "confidence": 0.83,                  # masse agrégée de la valeur ; sert au seuillage
  "normalization_confidence": 0.97,    # confiance de la normalisation span -> valeur
  "source": "text"                     # ou "vocabulary"
}
```

`source = "text"` : la valeur provient d'un span du document, dont les offsets sont fournis.
Elle passe par une étape de normalisation, qui peut la laisser inchangée ou la réécrire ;
elle ne figure donc pas nécessairement telle quelle dans le texte.
`source = "vocabulary"` : la valeur provient de l'ensemble des valeurs observées à
l'entraînement pour ce champ, sans span source ; `span` vaut `None` et les offsets `-1`.

`value` suit la décision du modèle. Les autres clés décrivent le meilleur candidat, y compris
lorsque `value` est `None` : un seuil différent peut donc être appliqué a posteriori sans
réexécuter le modèle. `extract_values(texte)` rend `{champ: valeur}`.

```bash
python predict.py --demo
```

## Résultats

Macro-F1 par famille au niveau (document, champ), 410 documents de test, égalité de chaîne
canonique. Une valeur incorrecte compte comme faux positif et comme faux négatif.

| système | macro | CAT | DATE | NUM | ORD |
|---|---|---|---|---|---|
| même encodeur, sans les têtes | 0.487 | 0.430 | 0.307 | 0.537 | 0.673 |
| Qwen3.5-9B finetuné sur les mêmes 1 540 documents | 0.582 | 0.488 | 0.447 | 0.590 | 0.791 |
| **ce modèle** | **@@MACRO@@** | @@CAT@@ | @@DATE@@ | @@NUM@@ | @@ORD@@ |

Jeu d'évaluation : [`rntc/lymphome-synth-v5-eval`](https://huggingface.co/datasets/rntc/lymphome-synth-v5-eval).

### Les trois variantes

Même architecture et mêmes données ; seules la fenêtre de lecture à l'entraînement et la
taille de l'encodeur changent.

| variante | encodeur | fenêtre | macro |
|---|---|---|---|
| [`…-ecrf`](https://huggingface.co/rntc/mc-bio-gliner-lymphome-ecrf) | 150 M | 24 000 car. | 0.786 |
| [`…-ecrf-v2`](https://huggingface.co/rntc/mc-bio-gliner-lymphome-ecrf-v2) | 150 M | 45 000 car. | 0.809 |
| [`…-ecrf-large`](https://huggingface.co/rntc/mc-bio-gliner-lymphome-ecrf-large) | 395 M | 45 000 car. | 0.815 |

Le dossier médian fait 22 400 caractères et 39 % des dossiers dépassaient la fenêtre de
24 000 : lire le dossier entier vaut +0.023, tandis que multiplier l'encodeur par 2,6
n'ajoute que +0.006. **`-ecrf-v2` est donc le meilleur rapport qualité/coût** ; `-ecrf-large`
n'a d'intérêt que si la latence n'est pas une contrainte.

## Limites

Les annotations de référence sont produites par un modèle de langue, sur des documents
synthétiques issus du même pipeline ; leur accord avec une annotation humaine n'a pas été
mesuré. 97,4 % des cibles CAT du jeu de test figurent déjà dans le vocabulaire dérivé de
l'entraînement, ce qui limite ce que ces résultats indiquent sur des valeurs non observées.
Aucune évaluation n'a été conduite sur un autre corpus. Modèle de recherche, non validé
pour un usage clinique. Licence MIT.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry_run", action="store_true")
    ap.add_argument("--variant", choices=list(VARIANTS), default="ecrf")
    ap.add_argument("--src", default=None)
    ap.add_argument("--repo", default=None)
    a = ap.parse_args()
    V = VARIANTS[a.variant]

    src = Path(a.src or V["src"])
    repo = a.repo or V["repo"]
    stage = Path(f"{B}/hf_ecrf_stage_{a.variant}")
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # 1. le modèle GLiNER2. `from_pretrained` a besoin des QUATRE : config.json,
    #    encoder_config/config.json (d'où l'encodeur est reconstruit sans chemin local),
    #    le TOKENIZER (chargé depuis le dossier, sinon le chargement échoue), et les poids.
    for f in ("model.safetensors", "tokenizer.json", "tokenizer_config.json"):
        shutil.copy2(src / f, stage / f)
    for f in ("special_tokens_map.json",):
        if (src / f).exists():
            shutil.copy2(src / f, stage / f)
    shutil.copytree(src / "encoder_config", stage / "encoder_config")

    # `model_name` pointe vers un chemin ABSOLU de notre cluster. Il n'est pas utilisé au
    # chargement (encoder_config et tokenizer sont fournis) mais il serait affiché à
    # l'utilisateur et exposerait notre arborescence. On le neutralise.
    cfg = json.loads((src / "config.json").read_text(encoding="utf-8"))
    cfg["model_name"] = V["model_name"]
    (stage / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    # 2. les têtes — on retire `space` des clés inutiles au chargement ? non : tout est utile
    shutil.copy2(src / "assign.pt", stage / "assign.pt")

    # 3. le schéma : c'est du TEXTE, c'est ce qui rend le modèle indépendant du champ
    schema = {k: {"label": v["label"], "desc": v["desc"], "section": v["section"]}
              for k, v in LABELS.items()}
    (stage / "field_schema.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=1), encoding="utf-8")

    # 4. le code d'inférence, autonome
    for f in ("modeling_assign.py", "predict.py"):
        shutil.copy2(HERE / f, stage / f)
    # le défaut de lecture du code publié doit être celui SOUS LEQUEL le modèle a été
    # entraîné et mesuré : une variante 24k ne doit pas hériter du défaut 45k.
    code = (stage / "modeling_assign.py").read_text(encoding="utf-8")
    code = code.replace("max_chars=45000", f"max_chars={V['cap']}")
    (stage / "modeling_assign.py").write_text(code, encoding="utf-8")

    m, c, d, n, o = V["scores"]
    readme = README
    for k, v in (("@@NAME@@", repo.split("/")[-1]), ("@@REPO@@", repo),
                 ("@@PARAMS@@", V["params"]), ("@@MACRO@@", f"{m:.3f}"),
                 ("@@CAT@@", f"{c:.3f}"), ("@@DATE@@", f"{d:.3f}"),
                 ("@@NUM@@", f"{n:.3f}"), ("@@ORD@@", f"{o:.3f}")):
        readme = readme.replace(k, v)
    assert "@@" not in readme, "marqueur non substitué dans le README"
    (stage / "README.md").write_text(readme, encoding="utf-8")

    tot = sum(f.stat().st_size for f in stage.rglob("*") if f.is_file())
    print(f"prêt dans {stage}  ({tot/1e6:.0f} Mo)")
    for f in sorted(stage.rglob("*")):
        if f.is_file():
            print(f"   {f.relative_to(stage).as_posix():34s} {f.stat().st_size/1e6:8.2f} Mo")
    print(f"champs dans le schéma : {len(schema)}")

    if a.dry_run:
        print("dry run : rien n'est envoyé")
        return

    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(repo, repo_type="model", private=False, exist_ok=True)
    api.upload_folder(folder_path=str(stage), repo_id=repo, repo_type="model")
    print(f"=== PUBLIÉ : https://huggingface.co/{repo} ===")


if __name__ == "__main__":
    main()
