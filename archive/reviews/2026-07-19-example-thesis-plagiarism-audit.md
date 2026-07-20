# Audit de similarité avec les thèses de `exemples/`

Date : 19 juillet 2026  
Nature : contrôle ponctuel, fermé aux trois PDF fournis, par correspondances exactes et approchées suivies d'une revue manuelle.  
Modification du manuscrit : aucune.

## Verdict exécutif

**Aucun passage préoccupant n'a été détecté dans le corps scientifique de la thèse contre les trois thèses de `exemples/`.**

Au seuil principal de douze mots consécutifs, le programme ne trouve qu'une seule correspondance : treize mots du gabarit de page de garde commun à Sorbonne Université, ED130, Inria Paris et l'équipe ALMAnaCH. Le détecteur approché ne conserve aucun candidat au seuil principal.

Une passe de sensibilité abaissée à huit mots trouve trois correspondances supplémentaires : deux autres fragments administratifs de la page de garde et huit mots provenant du titre bibliographique de RedPajama. Ce dernier apparaît dans la bibliographie de Nathan Godey et dans une phrase de la thèse qui cite correctement le travail RedPajama ; il ne s'agit pas d'une reprise de prose originale de la thèse exemple.

Ce verdict signifie uniquement qu'aucune reprise verbatim ou légèrement remaniée n'a été mise en évidence **contre ces trois documents**. Il ne constitue pas une certification d'originalité contre toute la littérature et ne remplace pas un service de comparaison disposant d'un corpus externe.

## Corpus contrôlé

| Document exemple | Pages PDF | Mots extraits par Poppler | SHA-256 |
|---|---:|---:|---|
| Paul-Ambroise Duquenne, *Sentence Embeddings for Massively Multilingual Speech and Text Processing* | 187 | 62 753 | `76b0b1bba9edc3136132164ac358d32eb021cdd3eecc7970cd1299990d406d5c` |
| Nathan Godey, *Improving Representations for Language Modeling* | 201 | 67 106 | `3f4689883d2255efacef4b20bfd728ca4703860ebe5e57f44ace9f305f4deedf` |
| Tu Anh Nguyen, *Spoken Language Modeling from Raw Audio* | 186 | 66 829 | `5e085bcb5dad0681e49877002e6ada2eefa8744da3acca69f57defc06cc9f843` |
| **Total** | **574** | **196 688** | — |

La thèse contrôlée comprend **52 fichiers `sources/**/*.tex`**. Après suppression du balisage et normalisation, elle contient 76 996 tokens comparables ; les trois exemples en contiennent 199 584. Le SHA-256 du manifeste trié des 52 fichiers TeX — chaque ligne du manifeste contenant le hash et le chemin d'un fichier — est `7b93c2506c09370caeadf2ab4e57d5bab9618b35eeeefecf65a8ff21b895d7c1`.

Les calculs bruts sont enregistrés dans `tmp/plagiarism-audit/raw-results.json`, hash `13fb6e98e9a0bfe788ab3c97637e8ad4184bdfdddeed7057b0aac03db5f60fb1`.

## Méthode

### Extraction et normalisation

- Les PDF ont été extraits avec `pdftotext -layout`. Les sauts de page `\f` permettent de conserver le numéro de page.
- Les fichiers TeX ont été passés dans `detex`. Un remappage vers les lignes sources réelles corrige les décalages de numérotation que `detex -1` peut produire autour des environnements LaTeX.
- Les césures PDF de fin de ligne ont été réparées avant tokenisation.
- Le texte a été normalisé en Unicode, passé en minuscules et réduit aux mots dans leur ordre d'origine.
- Les mathématiques, le code, les coordonnées TikZ et le contenu tabulaire essentiellement non discursif ont été exclus. Les légendes et la prose environnante restent analysées.
- Les bibliographies des PDF exemples sont restées incluses volontairement ; c'est ce qui permet d'identifier explicitement le faux positif RedPajama.

### Correspondances exactes

Le détecteur indexe les séquences de douze mots des exemples, retrouve les mêmes séquences dans la thèse, puis étend chaque résultat vers la gauche et la droite afin de produire le passage commun maximal.

Résultat principal :

| Seuil | Correspondances | Dans le corps scientifique | Verdict préoccupant |
|---:|---:|---:|---:|
| ≥ 12 mots | 1 | 0 | 0 |
| ≥ 9 mots | 1 | 0 | 0 |
| ≥ 8 mots, passe de sensibilité | 4 | 1 titre bibliographique | 0 |

### Correspondances approchées

Le détecteur flou compare des fenêtres de prose à partir de leur ordre lexical et du recouvrement de leurs mots informatifs. Le réglage principal utilise des fenêtres de 48 mots, un ratio de séquence minimal de 0,62, un Jaccard de contenu minimal de 0,35 et au moins six mots de contenu partagés.

- Réglage principal : **0 candidat**.
- Fenêtres plus courtes de 28 mots, seuils 0,60 / 0,34 / cinq mots partagés : **2 candidats**, tous deux sur la page de garde Nathan Godey.
- Réglage permissif 0,45 / 0,22 / quatre mots partagés : **3 candidats**, tous sur la page de garde Nathan Godey.

Aucun candidat approché n'a été trouvé dans le corps scientifique, même sous le réglage permissif utilisé pour la contre-vérification.

## Revue manuelle des résultats

### S-01 — Gabarit institutionnel commun, 13 mots

- **Thèse** : `sources/title/title.tex:18-26`.
- **Exemple** : Nathan Godey, PDF page 2.
- **Passage normalisé commun** : « ED130 Inria de Paris équipe ALMAnaCH thèse de doctorat discipline informatique présentée par ».
- **Verdict** : similitude conventionnelle, non préoccupante.

Les deux documents utilisent le gabarit de la même école doctorale et de la même équipe de recherche. La page a été contrôlée visuellement dans le PDF, pas seulement par extraction textuelle.

### S-02 — Titre bibliographique RedPajama, 8 mots

- **Thèse** : `sources/related_works/corpus_annotation.tex:96`.
- **Exemple** : Nathan Godey, PDF page 169 dans le fichier, page imprimée 156, section Bibliography.
- **Passage commun** : « an open dataset for training large language models ».
- **Verdict** : titre de publication partagé, correctement attribué, non préoccupant.

Dans l'exemple, ces mots appartiennent au titre de la référence *RedPajama: An Open Dataset for Training Large Language Models*. Dans la thèse, ils servent à décrire RedPajama-V2 et la phrase porte `\citep{weber2024redpajama}`. Ce résultat confirme que l'abaissement à huit mots commence à capturer les titres bibliographiques communs.

### S-03 — Deux fragments administratifs de 8 mots

- `sources/title/title.tex:29-30` contre Nathan Godey, page 2 : formule d'obtention du grade ;
- `sources/title/title.tex:67` contre Nathan Godey, page 2 : nom, équipe et rôle d'Éric de la Clergerie, encadrant commun.

**Verdict** : métadonnées institutionnelles, non préoccupantes.

Les pages de garde de Tu Anh Nguyen et Paul-Ambroise Duquenne ont également été rendues et contrôlées visuellement. Elles partagent naturellement l'institution et plusieurs formules administratives, mais aucune séquence exacte d'au moins huit mots n'a été détectée avec le texte courant de la thèse.

## Contrôles du détecteur

Six tests unitaires passent :

1. réparation d'une césure PDF ;
2. détection d'une séquence exacte de douze mots ;
3. rejet d'une séquence exacte trop courte ;
4. détection d'une reformulation légère ;
5. rejet de deux passages sans rapport ;
6. remappage d'un numéro `detex` décalé vers la véritable ligne TeX.

Un test de bout en bout supplémentaire retrouve une séquence synthétique de 22 mots et ne produit aucun résultat sur un paragraphe négatif indépendant.

Les quatre avertissements Poppler concernent le nom interne d'une ligature `volume_up` dans un PDF ; le contrôle de la page concernée et des volumes extraits ne révèle pas de perte de prose utile pour cette comparaison.

## Limites

1. Le corpus de référence se limite strictement aux trois thèses de `exemples/`.
2. L'algorithme est adapté aux reprises verbatim et aux modifications lexicales légères. Une paraphrase sémantique profonde sans vocabulaire distinctif commun peut lui échapper.
3. Les équations, dessins, structures argumentatives générales et idées sans proximité textuelle ne sont pas évalués comme du plagiat par ce contrôle.
4. Les citations, noms de modèles et titres de publications créent inévitablement de courtes similitudes ; elles nécessitent le jugement manuel appliqué ici.
5. Une absence de résultat automatique n'est pas une preuve absolue d'originalité.

## Conclusion

Dans les limites explicites de cet audit fermé, **aucun indice de reprise textuelle préoccupante n'a été trouvé**. Les seules correspondances sont entièrement expliquées par le gabarit institutionnel commun, un encadrant commun et un titre bibliographique partagé. Aucune correction du manuscrit n'est recommandée sur cette base.
