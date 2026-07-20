# Audit de comparabilité expérimentale

Date de l'instantané : 20 juillet 2026.  
Périmètre : expériences propres à la thèse dans les chapitres 10 à 18, avec contrôle des annexes méthodologiques. Aucun fichier TeX n'a été modifié.

## Verdict exécutif

Le protocole le plus propre est celui du détour CLM : architecture, données, calendrier, budget total, fine-tuning et graines sont appariés. Les comparaisons de CamemBERT-bio sont également bien définies en interne, et le chapitre avertit honnêtement que les systèmes publiés utilisent des têtes et protocoles différents.

Les principales vulnérabilités sont ailleurs :

1. les ablations de curation de MC-Bio comparent des sous-corpus de tailles différentes sans contrôles de volume suffisants, avec des écarts parfois inférieurs à un point et sans incertitude publiée ;
2. OntoBook semble sélectionner l'époque et le poids de perte sur les mêmes benchmarks dont il publie ensuite les scores, et les tests de significativité ne sont pas décrits ;
3. la comparaison des ontologies OntoBook ne fixe pas clairement le nombre de tokens ou d'étapes alors que leurs corpus ont des tailles très différentes ;
4. la comparaison extracteur–générateur de la troisième partie ne documente pas le fine-tuning des générateurs dans l'annexe annoncée.

## Grille de contrôle

Chaque comparaison a été examinée selon huit axes : initialisation, corpus, quantité de données, calcul, tête de tâche, métrique, sélection de modèle/seuil, répétitions et incertitude. Une comparaison est dite **contrôlée** seulement si l'élément causal discuté est la différence principale restante.

| Expérience | Statut | Commentaire |
|---|---|---|
| CamemBERT vs CamemBERT-bio, même pipeline | Contrôlée | Même fine-tuning et 10 graines ; seule l'initialisation préentraînée change. |
| CamemBERT-bio vs modèles publiés | Descriptive | Protocoles, têtes, gel de couches et métriques historiques diffèrent ; le chapitre le signale. |
| Variantes Biomed-Enriched OLMo2 à 33.6B | Contrôlée sur le budget | Même checkpoint et mêmes hyperparamètres ; l'effet du mélange reste identifiable. |
| BE-All 12.6B vs BE-Base 33.6B | Comparaison d'efficacité | Intéressante, mais score unique sans intervalle ; « matches » doit rester descriptif. |
| MC-Bio content/quality ablations | Partiellement contrôlée | Même pipeline et graines, mais volumes retirés variables et incertitude absente. |
| CLM detour vs MLM-only | Contrôlée | Données, architecture, budget total, calendrier et fine-tuning appariés. |
| OntoBook vs MLM-only | Contrôlée en principe | Même base et budget annoncés ; sélection et test statistique insuffisamment documentés. |
| Ontologies CIM-10/CCAM/ATC | Non isolée | Quantité de marches et vraisemblablement de mises à jour différente. |
| MC-bio-gliner vs Qwen3.5 | Benchmark commun, non causal | Formats, objectifs, tailles et optimisation diffèrent ; utile comme comparaison système. |
| Transfert PARHAF/FRACCO | Comparable par jeu | Même métrique/splits annoncés, mais très petit test PARHAF et entraînements hétérogènes. |

## E-01 — Les ablations MC-Bio ne séparent pas qualité du contenu et quantité de texte

**Emplacement.** `sources/part_1/chapter3/article.tex:98–164`.

La table de types retire des catégories dont le volume n'est pas donné. Elle contient un unique « Random removal (same volume) », sans préciser à quelle catégorie ce volume correspond. Un seul contrôle ne peut être simultanément apparié à plusieurs catégories de tailles différentes. Il permet au mieux de soutenir le résultat de la catégorie à laquelle il est apparié.

La table des seuils de qualité retire elle aussi des proportions nécessairement différentes (`edu/cont ≥ 6`, `≥ 7`, `≥ 8`, `term ≥ 7`, `writ ≥ 7`) sans contrôle aléatoire apparié à chaque taille. Une baisse peut donc venir du signal choisi, de la quantité de texte restante, de la distribution des sources, ou de leur combinaison.

**Conséquence.** Les phrases « confirming that the effect is specific to the content type » et « writing quality ... degrade[s] performance » sont plus fortes que le dessin expérimental. Le résultat observé est réel pour les corpus construits ; son attribution au signal seul n'est pas isolée.

**Sévérité.** Majeure pour l'interprétation causale, modérée pour les chiffres eux-mêmes.

**Ce qu'il faudrait documenter.** Tokens uniques et tokens échantillonnés par condition, nombre d'étapes fixe, contrôle aléatoire apparié à chaque retrait, moyenne ± écart-type ou intervalle sur les neuf graines, et différence appariée par tâche/graine.

## E-02 — Des écarts MC-Bio sous le point sont interprétés sans incertitude

Les écarts de `+0.13`, `+0.39`, `+0.48`, `+0.55`, `−0.13`, `−0.17`, `−0.26` et `−0.33` point sont présentés comme effets directionnels. Le texte indique neuf graines, mais les tableaux donnent uniquement la moyenne agrégée sur trois tâches, sans dispersion ni test apparié.

Avec cette seule présentation, il est impossible de savoir si un effet est stable entre tâches et graines ou dominé par une cellule. La formulation sûre est « the evaluated corpus variant scored X higher/lower » ; `helps`, `hurts`, `confirms` et `degrades` nécessitent l'incertitude correspondante.

## E-03 — OntoBook sélectionne apparemment ses hyperparamètres sur les résultats finaux

**Emplacement.** `sources/part_2/chapter6/article.tex:311–395` et `sources/appendix.tex:509–536`.

Le chapitre dit que l'époque 2 est retenue parce que la moyenne aval y culmine, et que `λ=1` est retenu parce qu'il a la variance la plus faible sur FRACCO. Les mêmes benchmarks — dont FRACCO — servent ensuite au tableau principal. Aucun ensemble de développement séparé, protocole de nested selection ou correction pour recherche d'hyperparamètres n'est décrit.

**Conséquence.** Les scores OntoBook, surtout FRACCO, peuvent bénéficier d'une sélection sur le benchmark rapporté. Cela n'annule pas les gains, mais empêche de considérer le tableau comme une estimation strictement tenue à l'écart de la sélection.

**Sévérité.** Majeure si les courbes utilisent effectivement les jeux de test ; à lever par clarification si elles utilisent un développement non mentionné.

## E-04 — Les p-values OntoBook ne sont pas reproductibles à partir du manuscrit

Le chapitre rapporte `p<0.001` sur FRACCO et Distemist et `p=0.11` sur Cantemist avec trois graines pour les modèles de la thèse, mais ne donne ni test, ni unité d'échantillonnage, ni appariement, ni hypothèse bilatérale/unilatérale. Avec seulement trois graines, un résultat inférieur à 0.001 exige nécessairement une unité d'analyse plus fine ; si les documents ou prédictions servent d'unités, il faut le dire et préserver l'appariement.

**Recommandation de rapport.** Nommer le test, la statistique, l'unité, la procédure d'appariement et, idéalement, l'intervalle de la différence. Sans cela, conserver les différences moyennes et retirer la qualification « significant ».

## E-05 — La comparaison CIM-10 / CCAM / ATC confond source et quantité de préentraînement

Le chapitre génère environ 402k marches CIM-10, 763k CCAM et 139k ATC. Il dit que chaque modèle suit la même procédure, mais ne dit pas que chacun voit le même nombre de tokens ou de mises à jour. Quatre époques sur chaque corpus impliqueraient des budgets très différents.

Les conclusions « CCAM achieves the best average » et « ATC yields the best Distemist score » décrivent correctement les lignes. En revanche, elles ne permettent pas d'attribuer l'écart à la nature de l'ontologie seule. Une comparaison causale demanderait un échantillonnage à tokens/étapes constants, ou une courbe en fonction du budget.

## E-06 — Le contrôle CLM/MLM est solide, avec deux limites bien circonscrites

**Emplacement.** `sources/part_2/chapter5/article.tex:89–124`.

Points forts : même checkpoint initial, même architecture, même corpus, même budget total, même calendrier en deux phases, même optimiseur, mêmes hyperparamètres par tâche, neuf graines françaises et cinq anglaises. C'est une comparaison causale crédible de l'objectif de phase 1 dans ce cadre.

Deux nuances restent nécessaires :

- « same compute » signifie ici même budget/schéma d'entraînement, pas une mesure publiée des FLOPs ou de l'énergie de chaque objectif ;
- la conclusion selon laquelle l'effet est plus fort quand le *domain gap* est grand compare France et anglais avec des histoires de préentraînement différentes, donc ce modérateur n'est pas lui-même isolé.

La seconde nuance appartient surtout à l'audit causal ; elle ne remet pas en cause l'effet principal CLM vs MLM.

## E-07 — Les résultats Biomed-Enriched sont propres à l'intérieur des familles, moins entre familles

Les variantes OLMo2 utilisent 33.6B tokens et les mêmes hyperparamètres : leurs différences peuvent être attribuées aux mélanges. La comparaison 12.6B/33.6B matérialise une efficacité en tokens, mais les scores QA/MMLU paraissent être des évaluations ponctuelles sans dispersion. Des écarts de quelques dixièmes ne doivent donc pas être lus comme des classements robustes.

Les modèles Llama-3-8B et Meditron-70B sont correctement séparés comme « Reference Models ». Ils ne partagent ni taille, ni préentraînement, ni nécessairement protocole de prompt ; ils donnent un repère, pas une ablation.

Pour les encodeurs, reproduire le protocole BioClinical-ModernBERT améliore la comparabilité, mais « matching 77.05 » demeure un rapprochement de scores de pipelines entraînés sur des corpus et nombres de tokens différents, sans intervalle conjoint.

## E-08 — Le duel extracteur–générateur est un comparatif système, pas un test d'architecture

**Emplacement.** `sources/part_3/chapter7/article.tex:68–172`.

Le chapitre reconnaît que les objectifs et formats de sortie diffèrent et que la référence silver vient de la même famille que les générateurs. C'est une bonne limitation. Le résultat « 27× fewer parameters at a 0.018 gap » est valable comme comparaison de systèmes sur le même test synthétique, pas comme preuve que l'architecture encodeur est plus efficace à données et optimisation contrôlées.

Le point manquant est méthodologique : l'annexe annoncée (`app:eval-details`) donne les hyperparamètres de MC-bio-embed et de l'extracteur, mais aucun hyperparamètre de fine-tuning des quatre Qwen3.5. Il manque au minimum méthode d'adaptation, contexte, epochs/steps, batch, learning rate, précision, sélection de checkpoint et décodage. La phrase « fine-tuned on exactly the same data » ne suffit pas à rendre la comparaison reproductible.

**Sévérité.** Majeure pour la reproductibilité ; modérée pour la comparaison descriptive.

## E-09 — Les comparaisons externes de la troisième partie sont correctement bornées

Le manuscrit précise que PARHAF ne contient que 31 documents de test, que les petites différences y sont instables, et que FRACCO inverse le classement. Il sépare zéro-shot et adaptation sur 100 documents et sélectionne les seuils sur validation. Cette présentation évite une généralisation abusive.

La seule réserve est que la ligne `Qwen3.5-2B` sans sortie utilisable en zéro-shot ne doit pas être interprétée comme un score nul : le tiret et la note de table le font correctement.

## E-10 — Les comparaisons CamemBERT-bio sont honnêtement qualifiées

Le tableau interne CamemBERT/CamemBERT-bio utilise strict `seqeval`, IOB2, micro-$F_1$, sélection sur validation et dix graines. Le tableau avec les modèles externes mélange têtes CRF/linéaires, gel, métriques et protocoles ; le texte le dit explicitement puis consacre une table à l'effet de la méthodologie. Il faut conserver cet avertissement près de toute formulation « best ».

## Priorités

1. Clarifier immédiatement si l'époque et `λ` OntoBook ont été choisis sur validation ou test.
2. Documenter le test statistique OntoBook.
3. Ajouter les budgets par condition MC-Bio et des contrôles aléatoires appariés, ou affaiblir l'attribution.
4. Ajouter les hyperparamètres de fine-tuning Qwen3.5 dans l'annexe.
5. Pour les faibles écarts, publier l'incertitude et parler de scores observés plutôt que d'effets généraux.

## Conclusion

Les résultats centraux ne sont pas tous au même niveau de contrôle. Le détour CLM supporte une lecture causale forte dans son cadre. MC-Bio et plusieurs analyses OntoBook supportent aujourd'hui une lecture descriptive de variantes entraînées, mais pas toujours l'attribution précise donnée dans la prose. La troisième partie supporte une comparaison opérationnelle de systèmes sur un benchmark synthétique, à condition de compléter le protocole des générateurs et de ne pas la transformer en ablation architecturale.
