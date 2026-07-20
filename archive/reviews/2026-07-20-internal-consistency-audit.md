# Audit de cohérence interne de la thèse

Date de l'instantané : 20 juillet 2026.  
Périmètre : résumé anglais/français, introduction, liste des contributions, neuf chapitres de contribution, conclusion et annexes. Aucun fichier TeX n'a été modifié.

## Verdict exécutif

Les nombres centraux sont généralement cohérents : 413 M mots, cinq benchmarks et +2.54 $F_1$ pour CamemBERT-bio ; environ 2 M de passages cliniques ; 10 Md de tokens pour MC-Bio ; huit tâches françaises et +2.9/+1.5 points pour le détour ; 2,050 dossiers, 89 champs, 150 M contre 4 B paramètres et un écart de 0.018.

Quatre incohérences importantes subsistent :

1. la conclusion affirme qu'aucun modèle n'a vu de vrai dossier patient, alors que la branche anglaise du chapitre CLM utilise MIMIC-III ;
2. le résumé affirme une revue des dossiers par des cliniciens, mais cette étude n'apparaît ni dans le chapitre, ni dans l'annexe, ni dans les limitations ;
3. la conclusion transforme les contributions en une chaîne séquentielle et nomme `ModernCamemBERT-bio-v2`, modèle qui n'est pas défini dans les chapitres ;
4. la conclusion dit que MC-bio-gliner est le seul modèle comparé hébergeable sur site alors que plusieurs encodeurs comparés ont une taille voisine, et elle donne elle-même environ 8 Go pour Qwen3.5-4B.

## Méthode

- Registre des quantités et modèles répétés dans les cinq niveaux narratifs.
- Recalcul des moyennes simples accessibles dans les tableaux.
- Vérification des renvois entre corps et annexes.
- Recherche des assertions présentes uniquement dans le résumé ou la conclusion.
- Contrôle du journal de compilation existant pour références/citations non résolues.

## IC-01 — « Aucun vrai dossier patient » contredit l'entraînement anglais sur MIMIC-III

**Conclusion.** `sources/conclusion.tex:13–17` : « No model built here was shown a real patient record. »

**Chapitre source.** `sources/part_2/chapter5/article.tex:107` : le mélange anglais à 50B contient 20 % de résumés de sortie et notes cliniques MIMIC-III.

MIMIC-III est certes dé-identifié et accessible sous conditions, mais il contient de vraies notes de patients. L'assertion absolue de la conclusion est donc fausse pour les modèles anglais construits dans le chapitre 14. Elle reste défendable pour la chaîne française principale si cette portée est dite explicitement.

**Sévérité.** Critique pour le fil directeur « public text only », car la contradiction porte sur la contrainte centrale de la thèse.

**Résolution conceptuelle minimale.** Distinguer « French models in the main pipeline » des expériences anglaises auxiliaires, et décrire MIMIC comme des données cliniques réelles dé-identifiées et sous accès contrôlé.

## IC-02 — La revue clinique des dossiers n'est documentée nulle part

**Résumé.** `sources/abstract.tex:12` et `:29` déclarent que des cliniciens ont examiné les dossiers dans un outil web et les ont jugés globalement plausibles.

**Absence dans le corps.** `sources/part_3/chapter9/article.tex` décrit la génération, l'alignement silver et la comparaison distributionnelle, mais pas de protocole humain. `sources/appendix.tex` ne donne ni nombre de cliniciens, ni spécialité, ni échantillon, ni questionnaire, ni accord, ni résultats. Les limitations du chapitre ne mentionnent pas cette validation.

Une affirmation empirique positive du résumé doit pouvoir être retrouvée dans le corps. En l'état, le lecteur ne peut ni identifier ce qui a été revu, ni comprendre ce que « plausible overall » mesure.

**Sévérité.** Critique. Soit l'étude existe et doit être documentée, soit la phrase doit disparaître du résumé.

## IC-03 — `ModernCamemBERT-bio-v2` apparaît seulement dans la conclusion

**Emplacements.** `sources/conclusion.tex:60` et `:81`.

Le nom `ModernCamemBERT-bio-v2` n'est défini ni dans les contributions, ni dans le chapitre du détour, ni dans OntoBook, ni dans la troisième partie. Les scripts de carbone l'emploient pour une « ontology augmentation », mais ce statut n'est pas expliqué au lecteur de la thèse.

De plus, le modèle OntoBook principal est décrit comme initialisé depuis `ModernCamemBERT-base` (`sources/part_2/chapter6/article.tex:248`), tandis que MC-bio-embed part de `ModernCamemBERT-bio` et utilise des ressources dérivées des terminologies. Cela ne démontre pas que l'étape OntoBook transforme le checkpoint MC-bio en un checkpoint officiel « v2 ».

**Sévérité.** Majeure. Le nom et sa filiation doivent être définis, ou la conclusion doit employer les noms effectivement établis dans les chapitres.

## IC-04 — La « route unique » est plus linéaire que le protocole réel

`sources/conclusion.tex:18–28` raconte : corpus → encodeur → encodeur enrichi OntoBook → extracteur. Les chapitres montrent plutôt plusieurs branches :

- ModernCamemBERT-bio est entraîné sur MC-Bio avec le détour CLM ;
- OntoBook entraîne un autre encodeur depuis ModernCamemBERT-base ;
- MC-bio-embed part de ModernCamemBERT-bio et reçoit des paires issues des ressources terminologiques ;
- MC-bio-gliner part ensuite de MC-bio-embed.

Les ressources d'OntoBook irriguent bien l'extracteur, mais le checkpoint OntoBook n'est pas explicitement le checkpoint transmis. « The encoder is enriched » suggère une succession de poids qui n'est pas établie.

**Sévérité.** Majeure pour le schéma de synthèse ; aucun problème si la route est présentée comme circulation de ressources et d'idées plutôt que comme une lignée unique de checkpoints.

## IC-05 — « Only compared model a clinical service could host » contredit la table

**Emplacement.** `sources/part_3/chapter7/article.tex:321–326`.

Le tableau principal compare aussi ModernCamemBERT (150 M), ModernCamemBERT-bio (150 M) et GLiNER-BioMed (184 M). Tous ont une empreinte de poids du même ordre que MC-bio-gliner et sont donc eux aussi hébergeables sur site. La phrase « It is the only compared model a clinical service could host on site » est fausse au sens littéral.

Le paragraphe précédent estime par ailleurs Qwen3.5-4B à environ 8 Go en bfloat16. Dire ensuite qu'un générateur de cette taille « does not fit the modest hardware of a clinical service » n'est pas une conséquence logique de cette estimation : 8 Go peut tenir sur de nombreux GPU locaux, hors mémoire d'exécution/KV cache. L'avantage démontré est une empreinte de poids beaucoup plus faible, pas l'exclusivité de l'hébergement.

**Sévérité.** Majeure.

## IC-06 — La validation « benchmark-absent » est renvoyée au mauvais chapitre dans l'annexe

`sources/appendix.tex:713–716` décrit « the reference-free evaluation of \Cref{chap:evaluation} ». Or l'évaluation LLM-judge des vingt descriptions se trouve dans le chapitre des architectures (`sources/part_3/chapter8/article.tex:119–150`), pas dans le chapitre d'évaluation eCRF. Le renvoi compile, mais pointe sémantiquement vers le mauvais chapitre.

**Sévérité.** Mineure mais concrète.

## IC-07 — « Size-matched » est une approximation non explicitée

GLiNER-BioMed est appelé « size-matched » dans `sources/part_3/chapter7/article.tex:87`, alors que le tableau donne 184 M paramètres contre 150 M pour MC-bio-gliner, soit environ 23 % de plus. « Similar-sized » ou « same order of magnitude » serait exact ; `size-matched` suggère un appariement plus strict.

**Sévérité.** Mineure.

## IC-08 — Un tiers, 2.5× et 12.6/33.6 décrivent deux comparaisons distinctes

Le manuscrit emploie :

- « one third » pour BE-All à 12.6B contre 33.6B tokens ; le rapport exact est 37.5 %, donc plutôt « roughly one third » ou « 2.67× fewer » ;
- « 2.5× fewer » pour 67B contre 169B tokens, rapport exact 2.52.

La conclusion juxtapose les deux économies. Elles ne sont pas contradictoires, mais leurs référents doivent rester distincts. La valeur `one third` est un arrondi plus agressif que les autres chiffres du manuscrit.

**Sévérité.** Mineure.

## IC-09 — Les moyennes centrales ont été recalculées sans anomalie

Contrôles positifs :

- CamemBERT-bio : `73.94 − 71.40 = 2.54` points.
- Biomed-Enriched : combinaison des cinq tâches cliniques et six biomédicales de BE-Clinical = environ 77.08 ; BioClinical-ModernBERT = environ 77.05.
- Détour français : `60.8 − 57.9 = 2.9` et `63.3 − 61.8 = 1.5`.
- OntoBook : `58.33 − 55.81 = 2.52` sur FRACCO et `32.24 − 24.23 = 8.01` sur Distemist, correctement arrondis à +2.5 et +8.0.
- eCRF : `0.658 − 0.640 = 0.018` ; `4B / 150M = 26.67`, correctement arrondi à 27×.
- Corpus longitudinal : `1,540 + 100 + 410 = 2,050`.

## IC-10 — Nombres et noms sans conflit notable

Ont été vérifiés sans contradiction interne nouvelle :

- 413 M mots / 2.7 Go pour `biomed-fr` ;
- environ 2 M de paragraphes de cas cliniques ;
- 1,304,266 marches OntoBook et environ 1.3 Md de tokens générés ;
- 2 Md de tokens OntoBook dans MC-Bio, compatible avec l'upsampling du mélange final ;
- 16,375 rapports et 237,194 affectations de spans sur 89 champs ;
- 149 M dans l'annexe et 150 M dans la prose, arrondi acceptable.

## Contrôle des références compilées

Le `thesis.log` existant ne contient pas de citation ou référence indéfinie, ni de label multiplement défini. Le journal `condensed/build.log` demande une passe supplémentaire, mais concerne la version condensée et non le PDF principal inspecté ici.

## Priorités

1. Résoudre la contradiction MIMIC/public-only.
2. Documenter ou retirer la validation par cliniciens du résumé.
3. Définir précisément `ModernCamemBERT-bio-v2` et la filiation des checkpoints.
4. Remplacer l'exclusivité d'hébergement par une revendication d'empreinte mémoire mesurée.
5. Corriger le renvoi d'annexe et préciser les arrondis.

## Conclusion

La cohérence numérique locale est bonne. Les défauts les plus sérieux concernent le récit global : données réellement vues, preuve humaine annoncée et lignée des modèles. Ce sont précisément les éléments qu'un jury utilise pour reconstruire la contribution de bout en bout ; ils méritent donc d'être alignés avant les détails de style.
