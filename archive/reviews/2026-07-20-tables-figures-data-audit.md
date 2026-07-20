# Audit de traçabilité des tableaux, figures et données

Date : 20 juillet 2026  
Périmètre : tableaux et figures quantitatives du manuscrit principal, scripts sous `plots/`, registres et artefacts sous `research/` et `publications/`.  
Action sur le manuscrit : aucune.

## Méthode

La vérification a suivi cinq niveaux :

1. inventaire de tous les `\includegraphics` du manuscrit et contrôle de l'existence des fichiers ;
2. rapprochement entre prose, tableaux, scripts de figure et fichiers JSON/CSV ;
3. recalcul des moyennes, deltas, rapports et classements à partir des cellules publiées ;
4. examen de la provenance déclarée, des empreintes SHA-256 et du statut des observations ;
5. distinction entre **valeur cohérente**, **valeur reproductible localement** et **valeur seulement transcrite**.

Le test graphique trouve **zéro image référencée manquante**. Les principaux calculs arithmétiques des chapitres 3 à 6 sont cohérents. En revanche, la chaîne de preuve de la partie 3 contient un défaut critique et plusieurs registres concurrents.

## Verdict synthétique

- **Critique :** le mécanisme qui doit empêcher l'emploi de données provisoires peut être contourné par le statut non documenté `final`.
- **Majeur :** le résumé des résultats décodeur de Biomed-Enriched annonce 61.08 comme meilleur score, alors que les cellules du tableau donnent 61.71 pour BE-All 12.6B.
- **Majeur :** les tableaux externes et capstone de la partie 3 ne disposent pas d'une source canonique unique à jour ; JSON, dashboard, registre et manuscrit ne représentent pas toujours le même run ou la même règle de seuil.
- **Majeur :** plusieurs figures finales sont alimentées par des constantes Python ou par des transcriptions de dashboard sans artefact brut versionné.
- **Positif :** les agrégats CamemBERT-bio, CLM, OntoBook, OntoBench, supervision 200 documents et stylométrie ont été recalculés sans erreur arithmétique substantielle.

## 1. Défaut critique du garde-fou `registered/provisional`

### Ce que la documentation promet

`plots/part_3/data/README.md` définit exactement deux statuts :

- `registered` : observation soutenue par le registre principal ou un artefact primaire versionné ;
- `provisional` : observation interdite dans une figure finale.

`plots/part_3/common.py` et les scripts de chapitres doivent alors refuser une construction finale contenant du provisoire ou produire un rendu `PRELIMINARY` en mode de revue.

### Ce que contient réellement le manifeste

Le parcours programmatique de `plots/part_3/data/visual_data.json` trouve :

| Statut | Nombre d'observations |
|---|---:|
| `registered` | 22 |
| `provisional` | 18 |
| `final` | 30 |

Le statut `final` n'existe pas dans le schéma décrit. Or le code teste principalement l'égalité à `provisional`. Une observation `final` est donc acceptée sans satisfaire la définition de `registered`.

### Exemple qui démontre le problème

Les cinq points de la courbe d'efficacité en données portent `status: "final"`, alors que leur propre champ `note` dit :

> dashboard-transcribed [...] pending explicit rescore and registration in results.json

Le README les qualifie d'ailleurs encore de `provisional`. Les observations capstone dérivées portent également `final`, tandis que le README explique que le registre primaire et les intervalles restent provisoires.

### Conséquence

Le garde-fou ne garantit actuellement pas qu'une figure dite finale n'utilise que des observations enregistrées. Ce n'est pas une faute graphique : c'est une rupture de la chaîne de preuve.

### Correction recommandée

1. imposer un enum strict `{registered, provisional}` lors du chargement ;
2. rejeter tout statut inconnu ;
3. convertir en `provisional` tout point dont la note mentionne une rescore ou une inscription encore attendue ;
4. ajouter un test parcourant récursivement chaque feuille du manifeste ;
5. ne retirer le filigrane qu'après génération depuis les artefacts bruts et inscription dans le registre canonique.

## 2. Erreur numérique dans le résumé Biomed-Enriched

**Emplacement :** `sources/part_1/chapter2/article.tex:319`.

Le texte affirme que BE-All obtient le meilleur score moyen, **61.08%**. Cette valeur correspond bien à la moyenne non pondérée des neuf cellules de la ligne BE-All 33.6B :

\[
(47.21+42.79+76.60+60.00+65.66+68.06+58.96+69.00+61.40)/9
=61.0756.
\]

Mais la ligne BE-All 12.6B donne :

\[
(47.21+42.94+76.40+64.44+64.53+68.75+57.23+71.00+62.87)/9
=61.7078.
\]

**Verdict :** si « average performance » désigne bien la moyenne des neuf tâches, le meilleur score est **61.71%**, pas 61.08%. Le résultat devient même plus favorable à la thèse : la variante à 12.6B tokens est la meilleure.

### Erreur de mise en évidence associée

Dans le tableau QA, la moyenne 55.53 de BE-All 33.6B est légèrement supérieure à 55.52 pour 12.6B, mais c'est la seconde qui est en gras. Il faut soit mettre 55.53 en gras, soit déclarer explicitement une égalité à la précision retenue.

Les notes « Bold indicates best result per column » sont aussi ambiguës : Llama-3-8B et Meditron-70B dépassent plusieurs variantes internes mais ne sont pas mis en gras. La note doit dire « best among our variants » si c'est la règle voulue.

## 3. Partie 3 : plusieurs vérités concurrentes

### Capstone eCRF

Le tableau du chapitre 7 donne notamment Qwen3.5-4B à `0.658/0.567`, Qwen3.5-9B à `0.650/0.558` et MC-bio-gliner à `0.640/0.503`. Ces valeurs sont cohérentes avec :

- `research/lymphome/canonical_scores.json` pour les modèles qu'il contient ;
- le recompute plus récent décrit dans `research/lymphome/DASHBOARD_NUIT.md` ;
- les constantes de `plots/part_3/money_params_vs_f1.py`.

Mais `research/lymphome/results.json`, déclaré ailleurs comme registre primaire, est daté d'avant ce recompute, s'annonce lui-même **PROVISOIRE**, et conserve pour Qwen3.5-4B l'ancien run tronqué `0.6147/0.5246`. Le dashboard précise que ce run ne remplissait que 71 champs sur 89 et que la valeur corrigée est 0.658.

**Verdict :** les chiffres du manuscrit sont compatibles avec le résultat corrigé, mais le « registre primaire » est obsolète. Tant qu'il n'est pas régénéré, la traçabilité automatique reste contradictoire.

### Comparaison externe PARHAF/FRACCO

Le tableau du chapitre 7 utilise notamment :

- PARHAF : `0.098/0.562` pour GLiNER-BioMed et `0.244/0.681` pour MC-bio-gliner ;
- FRACCO : `0.341/0.762` et `0.203/0.626`.

Ces nombres sont documentés dans `DASHBOARD_NUIT.md` comme des scores avec seuil choisi sur validation. Toutefois :

- `results.json` contient d'anciens scores à seuil d'inférence 0.001 ;
- `external_validation.json` contient une dérivation plus structurée, mais avec des variantes nommées différemment et des résultats différents (`gliner-biomed adapted` 0.603 sur PARHAF et 0.867 sur FRACCO, par exemple) ;
- aucune table machine-readable unique ne relie explicitement chaque ligne du manuscrit à son parquet, son seuil de validation, son split et son alias de modèle.

**Verdict :** les nombres du tableau ne sont pas réfutés, mais ils restent **dashboard-sourced** et insuffisamment désambiguïsés. C'est un risque élevé de mélanger base/large, v3b/v3f ou anciennes/nouvelles règles de seuil.

### Risque–couverture

Le manuscrit et `risk_coverage_curve.json` concordent :

- MC-bio-gliner : AURC 0.239, précision@50% 0.770 ;
- Qwen3.5-4B : AURC 0.2067, précision@50% 0.8284.

Mais `DASHBOARD_NUIT.md` annonce pour le même Qwen3.5-4B `0.175/0.862` et demande d'utiliser ces valeurs. Le JSON présent a été généré par `score_calib.py` et le script graphique lit bien ce JSON, mais il n'embarque ni hashes d'entrée ni métadonnées de génération.

**Verdict :** la figure et le texte sont mutuellement cohérents ; le conflit avec le dashboard doit néanmoins être tranché et le JSON doit enregistrer les hashes des parquets et du scorer.

## 4. Figures ou valeurs provisoires présentées dans le corps principal

### Courbe d'efficacité en données

Les cinq points 10/50/100/500/1540 sont transcrits depuis un dashboard. La documentation précise qu'ils ne sont pas reproductibles par l'invocation générique actuelle et attendent une rescore explicite. Ils ne doivent donc pas être traités comme finaux malgré leur statut JSON `final`.

### Intervalles de compétition

Les deltas et intervalles appariés de compétition sont marqués `provisional` et proviennent de `PARTIE3_INTRA.md`, pas d'une régénération depuis les prédictions. Le texte du chapitre les donne pourtant avec quatre décimales. Ils doivent être enregistrés ou clairement étiquetés exploratoires.

### Figure de descriptions benchmark-absent

Les quatre MAP de la figure 9 sont bien copiées du rapport de juge et les effectifs sont documentés (`n=1496` et `n=682`). Elles restent toutefois :

- absentes du registre principal ;
- fondées sur un juge LLM, non sur un gold médical humain ;
- marquées `provisional` dans le manifeste.

Le texte explicite correctement les deux dernières limites. Le statut final de la figure doit rester conditionné à l'enregistrement de l'artefact.

### Expérience agentique et carbone

`conclusion_agentic_gradient.py`, `conclusion_carbon_all.py` et les figures TABIB encodent les observations directement comme constantes Python. Les commentaires citent des fichiers extérieurs ou des documents (`figs_rows.csv`, `CARBON_FOOTPRINT.md`, `FINAL_RESULTS.md`) qui ne constituent pas, dans le dépôt, une table d'entrée hashée consommée par les scripts.

**Recommandation :** créer un petit JSON/CSV versionné par expérience, avec provenance, unité, date, définition de métrique, effectif et hash ; faire lire ce fichier au script.

### TABIB : la prose oublie un second modèle à 0 %

La figure 20.2 et sa source `plots/part_3/evalllm_figures.py` donnent un taux `unsafe` de `0` à **Gemma4 E2B** comme à **MedGemma 1.5**. La conclusion affirme pourtant : « Only MedGemma stays at zero ». Les cinq autres modèles sont bien compris entre 12 % et 28 %, mais l'unicité attribuée à MedGemma est fausse.

**Correction minimale recommandée :** remplacer l'unicité par une formulation qui distingue les mécanismes observés, par exemple : « MedGemma also stays at zero, but does so while deflecting on 61% of turns. » Il faut vérifier séparément ce qui explique le zéro de Gemma4 E2B avant de l'interpréter.

## 5. Vérifications numériques positives

### CamemBERT-bio

- Moyennes recalculées : CamemBERT `71.40`, biomed-fr-small `72.46`, biomed-fr `73.94`.
- Gain `73.94 - 71.40 = 2.54` : exact.
- Carbone : `26.11/0.80 = 32.64`, compatible avec « 32× » ; `8.16/0.80 = 10.2`, compatible avec « 10× ».

### MC-Bio

- Toutes les différences du tableau de types correspondent aux cellules affichées, à l'arrondi près.
- Le mélange final fait bien 7B + 2B + 0.6B + 0.4B = 10B et 70% + 20% + 6% + 4% = 100%.
- Le tableau reste toutefois hardcodé dans le TeX : aucun artefact brut local ne permet de refaire les neuf-seed ablations.

### Détour CLM

- French Base : `57.9000` contre `60.8125`, soit +2.9125 points, affiché +2.9.
- French Large : `61.7750` contre `63.3375`, soit +1.5625, affiché +1.5.
- Large gagne 7 tâches et fait une égalité sur MedDialog ; Base gagne bien les 8.
- Les JSON needle donnent exactement `62.22%` contre `51.56%`, soit +10.67 points, ainsi que les valeurs par longueur et position tracées.
- Les figures CKA lisent des JSON de runs avec méthode, seeds et chemins de modèles.
- En revanche, freeze, transplant et asymétrie sont encore recopiés comme constantes/tableaux sans artefacts aval versionnés.

### OntoBook

- Principales moyennes recalculées : aligné `52.5433`, MLM-only `48.6833`, misaligné `22.0433`, raw walks `48.0900`.
- Les deltas `−3.86`, `−30.50`, `+0.59` et `−46.95` sont corrects.
- Sources ontologiques : CIM `52.5433`, All `52.7967`, CCAM `53.1300`, ATC `52.9133`.
- Les nombres du tableau sont cohérents, mais les résultats aval et probes ne disposent pas d'un registre brut analogue à celui de la partie 3.

### MC-bio-embed et supervision ouverte

- OntoBench-FR : les moyennes exactes sont mE5 `50.8425`, BGE `48.7800`, Solon `47.8900`, MC-bio-embed `60.3550`; les arrondis du tableau sont corrects.
- L'ablation 200 documents concorde avec son JSON hashé : full `0.2051978`, sans clinique `0.1826377`, contrôle biomédical `0.1700135`; first-line `0.21092→0`, second-line `0.04969→0`.
- Le rapport du juge concorde avec les quatre MAP `0.478/0.333→0.517/0.382`.

### Corpus synthétique et stylométrie

- Split : 2,050 − 410 − 100 = 1,540 entraînements maximum, correct.
- TAPDL : 237,194 spans finaux, 89 champs et 2,050 dossiers concordent avec le manifeste.
- Stylométrie : les quatre métriques et `n=1000` sont reliés à un script et un log de calcul versionnés. La correction terminologique PARHAF « fictitious human-written », et non dossier hospitalier réel, est bien portée dans le manuscrit.

## 6. Reproductibilité par chapitre

| Zone | Recalcul arithmétique | Données primaires locales | État |
|---|---|---|---|
| Ch. 2 Biomed-Enriched | oui | courbes hardcodées, peu de sorties brutes | moyen |
| Ch. 3 MC-Bio | oui | ablations non retrouvées sous forme machine-readable | faible |
| Ch. 4 CamemBERT-bio | oui | tableaux essentiellement TeX/publication | moyen-faible |
| Ch. 5 CLM | oui | bon pour needle/CKA, incomplet pour résultats/freeze/transplants | moyen |
| Ch. 6 OntoBook | oui | résultats aval surtout transcrits | moyen-faible |
| Ch. 9 synthétique | oui | manifeste et log stylométrique solides | bon |
| Ch. 8 architecture | oui | bon pour ablation/judge, statut encore provisoire | moyen-bon |
| Ch. 7 évaluation | partiel | plusieurs registres concurrents | fragile |
| Conclusion TABIB/carbone | partiel | constantes de scripts, source externe/non consommée | fragile |

## 7. Ordre de correction recommandé

1. Corriger le schéma de statut et faire échouer tout statut inconnu.
2. Régénérer un registre unique de la partie 3 depuis les parquets actuels ; archiver ou marquer les anciens runs tronqués.
3. Corriger 61.08 → 61.71 dans le résumé Biomed-Enriched et les gras du tableau QA.
4. Construire une table machine-readable explicite pour le tableau externe PARHAF/FRACCO.
5. Régénérer et hasher risk-coverage pour trancher `0.207/0.828` contre `0.175/0.862`.
6. Recalculer les points d'efficacité en données et les intervalles appariés avant de retirer tout marquage préliminaire.
7. Sortir les constantes TABIB et carbone des scripts vers des fichiers de données versionnés.

## Conclusion

La plupart des opérations arithmétiques du manuscrit sont justes. Le risque dominant n'est pas une addition erronée mais la coexistence de plusieurs générations de résultats sans registre canonique synchronisé. La partie 3 est déjà proche d'une bonne architecture de provenance — hashes, scripts de dérivation, distinction registered/provisional — mais le statut `final` non documenté annule actuellement la garantie centrale. Une fois ce point réparé et les tableaux externes réenregistrés, la chaîne chiffres→figures deviendra nettement plus attaquable au bon sens du terme : chaque nombre pourra être relié à un artefact précis.
