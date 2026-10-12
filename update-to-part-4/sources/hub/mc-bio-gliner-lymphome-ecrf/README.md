---
license: mit
language: fr
library_name: gliner2
tags: [gliner, gliner2, information-extraction, ecrf, biomedical, french, lymphoma, clinical]
---

# mc-bio-gliner-lymphome-ecrf

Extraction de 89 champs d'eCRF depuis un dossier patient longitudinal français
(~22 000 caractères, plusieurs comptes-rendus successifs). Encodeur de 150 M paramètres,
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

m = ECRFExtractor.from_pretrained("rntc/mc-bio-gliner-lymphome-ecrf", device="cuda")
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
| ce modèle | 0.786 | 0.817 | 0.684 | 0.765 | 0.877 |

Jeu d'évaluation : [`rntc/lymphome-synth-v5-eval`](https://huggingface.co/datasets/rntc/lymphome-synth-v5-eval).

## Limites

Les annotations de référence sont produites par un modèle de langue, sur des documents
synthétiques issus du même pipeline ; leur accord avec une annotation humaine n'a pas été
mesuré. 97,4 % des cibles CAT du jeu de test figurent déjà dans le vocabulaire dérivé de
l'entraînement, ce qui limite ce que ces résultats indiquent sur des valeurs non observées.
Aucune évaluation n'a été conduite sur un autre corpus. Modèle de recherche, non validé
pour un usage clinique. Licence MIT.
