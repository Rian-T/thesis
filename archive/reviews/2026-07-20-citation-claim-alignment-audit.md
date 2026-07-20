# Audit d'alignement entre citations et affirmations

Date de l'instantané : 20 juillet 2026.  
Périmètre : introduction, contributions, chapitres expérimentaux et conclusion. Les trois fichiers d'état de l'art ne sont pas réaudités ici, car ils disposent déjà des rapports de fidélité et de quantité du 19 juillet. Aucun fichier TeX ou BibTeX n'a été modifié.

## Verdict exécutif

La plupart des citations contrôlées soutiennent bien le noyau de la phrase. Deux corrections sont indispensables :

1. Raghavan et al. ne disent pas que « jusqu'à 80 % des entités » manquent des modalités structurées ; ils mesurent la part de **critères d'éligibilité** nécessitant le texte non structuré dans deux indications, 59 % et 77 % ;
2. la notice `medgemma2026` cite le rapport MedGemma original de 2025 (`2507.05201`) alors que la phrase porte sur **MedGemma 1.5**, documenté dans un rapport distinct de 2026 (`2604.05081`).

Trois phrases exigent une qualification ou une source explicite : l'opposition déterministe encodeur/décodeur, l'affirmation négative sur tous les benchmarks médicaux existants, et l'absence de tout jeu français dossier–eCRF.

## Méthode

- 117 occurrences de commandes de citation ont été recensées hors état de l'art.
- Relecture prioritaire des phrases contenant un nombre, une superlative, une négation exhaustive, une obligation réglementaire ou une attribution de résultat.
- Vérification contre une source primaire lorsque celle-ci est accessible : article original, page ACL, PubMed/PMC, rapport technique officiel ou texte EUR-Lex.
- Une citation est jugée **alignée** si elle soutient toutes les propositions factuelles qui lui sont attachées, pas seulement le thème général.

## C-01 — Raghavan 2014 est transformé de critères d'essai en « entités »

**Emplacement.** `sources/part_1/chapter1/article.tex:16`.

**Phrase actuelle.** « up to 80% of entities are missing from structured modalities ».

**Ce que mesure l'article.** Raghavan et al. étudient la résolution de critères d'éligibilité à des essais pour leucémie lymphoïde chronique et cancer de la prostate. Le texte non structuré est nécessaire pour 59 % des critères CLL et 77 % des critères prostate. L'unité n'est ni l'entité, ni la proportion générale d'information clinique absente des champs structurés.

**Sévérité.** Critique : chiffre proche, mais population, dénominateur et objet changés.

**Formulation fidèle possible.** « In two clinical-trial recruitment settings, unstructured narratives were needed to resolve 59% and 77% of eligibility criteria. »

Source primaire : [Raghavan et al., 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4333685/).

## C-02 — La citation MedGemma pointe vers le mauvais rapport

**Emplacement.** `sources/conclusion.tex:184–189` et entrée `medgemma2026` de `thesis.bib`.

La phrase nomme « MedGemma 1.5 4B ». L'entrée bibliographique contient pourtant le titre générique *MedGemma Technical Report*, l'année 2025 et l'e-print `2507.05201`, correspondant à la génération précédente. Le rapport primaire de MedGemma 1.5 est *MedGemma 1.5 Technical Report*, arXiv `2604.05081`, publié en 2026, avec une liste d'auteurs différente.

**Sévérité.** Critique pour l'attribution bibliographique ; le fait qu'un modèle MedGemma 1.5 4B existe est correct.

Source primaire : [MedGemma 1.5 Technical Report](https://arxiv.org/abs/2604.05081) et [model card officielle](https://developers.google.cn/health-ai-developer-foundations/medgemma/model-card).

## C-03 — « Un encodeur redonne toujours la même réponse, un décodeur non » n'est pas sourcé et mélange deux phénomènes

**Emplacement.** `sources/conclusion.tex:142–146`.

La première opposition porte sur deux exécutions du **même input**. Les exemples suivants portent sur des **inputs modifiés** : reformulation, allongement du contexte ou insistance au fil d'une conversation. Ce n'est pas la même notion de stabilité.

Un décodeur exécuté avec décodage déterministe à température 0 peut redonner la même sortie ; un encodeur peut connaître de petites non-déterminismes d'exécution, même si sa tête de classification est normalement déterministe en évaluation. L'architecture seule ne justifie donc pas l'opposition absolue.

**Sévérité.** Majeure. La revendication démontrée par TABIB est la sensibilité à des perturbations sémantiquement contrôlées, pas l'aléa intrinsèque de deux appels identiques.

## C-04 — « Aucun benchmark ne pose cette question » dépasse les citations fournies

**Emplacement.** `sources/conclusion.tex:147–154`.

Les références établissent bien les objets suivants : MedQA/PubMedQA et les benchmarks français sont principalement des questions de connaissance ; HealthBench contient 5,000 conversations réalistes évaluées par des rubriques médicales ; CARES contient plus de 18,000 prompts de sécurité avec quatre styles, dont indirect, obfusqué et jeu de rôle.

La phrase suivante — « None of them ask... » — est une conclusion comparative de l'auteur, pas un résultat énoncé par ces articles. Elle doit être soutenue par une matrice explicite de protocoles et être très précisément délimitée. CARES teste déjà des changements de forme et le jeu de rôle ; HealthBench teste des conversations multi-tours. TABIB peut rester différent par le maintien d'un même fait médicamenteux à travers ses perturbations, mais c'est ce critère exact qu'il faut revendiquer.

**Sévérité.** Majeure pour la priorité implicite de TABIB.

Sources primaires : [HealthBench](https://openai.com/index/healthbench/), [CARES, NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/hash/1ca47465a87b8e125d9076b2e6ac6c96-Abstract-Datasets_and_Benchmarks_Track.html).

## C-05 — L'absence de jeu ouvert dossier français–eCRF n'a pas de support traçable

**Emplacement.** `sources/part_3/chapter9/article.tex:10–16`.

« No open dataset pairs a French hospital record with a clinician-filled form » est une affirmation négative potentiellement défendable, mais aucune revue, date de recherche, base ou critère d'inclusion n'est cité. Un lecteur ne peut distinguer « nous n'en avons pas trouvé » de « il n'en existe aucun ».

**Sévérité.** Modérée. La formulation robuste est un résultat de recherche daté : « We found no open dataset... » accompagné des familles de ressources examinées.

## C-06 — HealthBench et CARES ne soutiennent pas exactement la même proposition

**Emplacement.** `sources/conclusion.tex:149–150`.

CARES teste directement acceptation, prudence et refus de prompts médicaux nuisibles ou ambigus. HealthBench évalue des conversations réalistes avec des rubriques rédigées par des médecins, dont des critères de sécurité, mais ce n'est pas principalement un benchmark de refus. La phrase coordonnée « testing safety and refusal at larger scale » attribue implicitement les deux propriétés aux deux références.

**Sévérité.** Mineure. Séparer les rôles des deux benchmarks rendrait l'attribution exacte.

## C-07 — La phrase sur le déploiement local de DeepSeek est globalement fidèle, avec une nuance méthodologique

**Emplacement.** `sources/conclusion.tex:132–136`.

L'étude recense bien 261 hôpitaux de Chine continentale ayant publiquement signalé un déploiement local entre le 1er janvier et le 8 mars 2025. Il s'agit toutefois d'un recensement transversal par web scraping de sources publiques, pas d'un questionnaire auquel 261 hôpitaux auraient répondu. Le verbe neutre « found » convient ; « surveyed 261 hospitals » serait ambigu.

Source primaire : [Yuan et al., 2025](https://www.medrxiv.org/content/10.1101/2025.05.15.25326843v1.full).

## C-08 — L'AI Act est correctement cité

**Emplacement.** `sources/conclusion.tex:155–159`.

L'article 15 exige pour les systèmes à haut risque un niveau approprié d'exactitude, de robustesse et de cybersécurité sur leur cycle de vie, ainsi qu'une résilience aussi grande que possible aux erreurs, défaillances et incohérences, notamment lors d'interactions avec des personnes ou d'autres systèmes. Le résumé de la thèse est fidèle. La qualification de triage comme haut risque est également cohérente avec les catégories du règlement ; pour les dispositifs d'aide à la décision, la portée dépend de leur qualification réglementaire.

Source primaire : [Règlement (UE) 2024/1689, article 15](https://eur-lex.europa.eu/legal-content/en/ALL/?uri=CELEX%3A32024R1689).

## C-09 — Qi et al. soutient bien l'indépendance entre exactitude factuelle et cohérence interlingue

**Emplacement.** `sources/conclusion.tex:334–338`.

Qi et al. définissent une mesure de cohérence indépendante de l'exactitude et observent qu'une plus grande taille améliore souvent l'exactitude factuelle sans améliorer la cohérence interlingue. La phrase « factual knowledge does not buy that consistency » est une paraphrase forte mais fidèle à ce résultat général.

Source primaire : [Qi et al., EMNLP 2023](https://aclanthology.org/2023.emnlp-main.658/).

## C-10 — Les principaux chiffres historiques de l'introduction sont bien soutenus

Contrôles positifs :

- de Dombal : 304 patients, 91.8 % pour le système et 79.6 % pour le clinicien le plus senior — [article original](https://pubmed.ncbi.nlm.nih.gov/4552594/).
- L'étude CamemBERT conclut bien que le modèle OSCAR 4 Go est globalement proche du modèle 138 Go, avec une exception NER d'environ 0.9 point — [CamemBERT, tableau 5 et section 6.2](https://camembert-model.fr/files/anthology/2020.acl-main.645.pdf).
- AliBERT rapporte 48 A100 pendant 20 heures — [article BioNLP 2023](https://aclanthology.org/2023.bionlp-1.19/).
- Le total BioBERT PubMed + PMC correspond à environ 4.5 + 13.5 = 18 milliards de mots.
- Le passage sur le déploiement local oppose correctement risques de dépendance/confidentialité des modèles fermés et contrôle local des modèles ouverts — [Dennstädt et al., 2025](https://pubmed.ncbi.nlm.nih.gov/40050366/).

## C-11 — Points correctement attribués dans les chapitres techniques

Ont été recontrôlés sans nouveau défaut d'attribution :

- le protocole biphasique CLM→MLM de Gisserot-Boukhlef et al. ;
- les caractéristiques principales de ModernBERT ;
- GLiNER et GLiNER2 comme origine de l'interface span–description ;
- MAUVE, distance de Fréchet, MMD et C2ST dans la comparaison distributionnelle ;
- le précédent BioOntoBERT, désormais décrit dans OntoBook ;
- les rôles respectifs de CamemBERT-bio, DrBERT et ModernCamemBERT comme baselines françaises.

## C-12 — Affirmations propres à la thèse sans source externe requise

Les tailles de corpus, budgets de calcul, métriques, scores et résultats d'ablation produits par les auteurs ne nécessitent pas une citation bibliographique externe. Ils nécessitent en revanche une provenance de données ou un protocole reproductible ; ce point est traité séparément dans l'audit tables/figures/données.

## Priorités

1. Corriger l'objet et le dénominateur du chiffre Raghavan.
2. Remplacer la notice MedGemma par le rapport 1.5 de 2026.
3. Reformuler l'opposition encodeur/décodeur en termes de robustesse aux perturbations, non de répétabilité du même input.
4. Transformer les deux négations exhaustives (« aucun benchmark », « aucun dataset ») en résultats de recherche bornés.
5. Séparer HealthBench et CARES dans la phrase qui décrit leur fonction.

## Conclusion

L'architecture citationnelle est globalement saine : les erreurs nouvelles sont concentrées et réparables. Le défaut le plus net est le chiffre de 80 %, où la citation et la phrase ne partagent plus la même unité d'analyse. Le second est bibliographique : MedGemma 1.5 possède désormais son propre rapport primaire, que la notice actuelle ne référence pas.
