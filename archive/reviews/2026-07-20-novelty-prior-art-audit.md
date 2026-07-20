# Audit de nouveauté et d'antériorité des contributions

Date de l'instantané : 20 juillet 2026.  
Périmètre : les sept contributions énumérées dans `sources/contributions.tex`, leurs chapitres de démonstration et l'état de l'art associé. Aucun fichier de la thèse n'a été modifié.

## Verdict exécutif

La thèse contient plusieurs contributions défendables, mais deux formulations résument aujourd'hui une idée plus générale que la nouveauté effectivement établie : le détour CLM puis MLM et la génération de notes cliniques à partir de cas publics. Dans les deux cas, un précédent direct existe et est même déjà cité ailleurs dans le manuscrit. La nouveauté soutenable réside dans une instanciation et une validation plus étroites.

Les cinq autres contributions sont globalement sûres si elles sont présentées comme des ressources, des modèles ou des études empiriques propres à cette thèse, et non comme l'invention générale de leur famille de méthodes.

## Méthode

1. Relever le noyau technique de chaque contribution, indépendamment des mots `novel` ou `first`.
2. Chercher un précédent portant sur la même entrée, la même transformation et le même objectif.
3. Distinguer : **précédent direct**, **voisin proche**, et **élément différenciant vérifié**.
4. Contrôler que le chapitre reconnaît les précédents trouvés et que le résumé des contributions ne réélargit pas ensuite la revendication.
5. Ne conclure à aucune priorité absolue lorsque la recherche bibliographique n'est pas systématique au sens d'une revue PRISMA.

## Registre des sept contributions

| Contribution | Antériorité pertinente | Nouveauté soutenable | Risque actuel |
|---|---|---|---|
| `biomed-fr` et CamemBERT-bio | Le préentraînement continu de BERT sur un domaine est antérieur ; des modèles biomédicaux français existaient aussi. | Ressource publique française de 413 M mots, recette, modèle publié et comparaison coût/performance propres au travail. | Faible si présenté comme ressource/modèle, pas comme invention du préentraînement continu. |
| Biomed-Enriched | La sélection de données et l'annotation de sections biomédicales sont antérieures. | Annotation PMC au paragraphe selon plusieurs axes, évaluation contrôlée de sous-corpus, identification et diffusion d'environ 2 M de passages de cas cliniques. | Faible à modéré ; éviter une priorité mondiale implicite sur « paragraph-level annotation ». |
| MC-Bio | La curation par scores de qualité et les ablations de sources sont établies. | Mélange français de 10 Md de tokens et étude empirique des signaux/contenus dans ce contexte. | Faible si revendiquée comme corpus + étude. |
| Détour CLM | Gisserot-Boukhlef et al. montrent déjà une séquence CLM puis MLM optimale à budget fixe ; AntLM combine aussi CLM et MLM. | Détour **MLM préexistant → CLM de domaine → retour MLM**, validation biomédicale français/anglais, et interventions sur les couches. | **Élevé dans le résumé des contributions.** |
| OntoBook | BioOntoBERT génère des phrases depuis neuf ontologies et préentraîne BERT ; d'autres travaux apprennent déjà à partir de relations ontologiques. | Promenades dans trois terminologies françaises, reformulation en prose, et combinaison alignée MLM + prédiction de relation sur le même texte. | Modéré ; le chapitre est désormais bien borné, le résumé reste très large. |
| MC-bio-embed / MC-bio-gliner | GLiNER, GLiNER-BioMed et OpenBioNER conditionnent déjà la reconnaissance biomédicale sur des types/descriptions ; l'annotation synthétique par LLM est également antérieure. | Encodeur français enrichi par terminologies, intégration GLiNER2, corpus public/silver propre et évaluation sur l'eCRF longitudinal. | Faible à modéré si revendiqués comme modèles conçus dans la thèse, pas comme première NER ouverte biomédicale. |
| Rapports cliniques synthétiques | Asclepius transforme déjà des cas PMC publics en notes cliniques synthétiques pour entraîner un modèle partageable. | Génération **longitudinale** chronologique centrée lymphome, contrôle en vague, alignement de 89 champs d'eCRF et évaluation de remplissage. | **Élevé dans le résumé des contributions.** |

## N-01 — Le détour CLM n'est pas nouveau dans sa formulation générale

**Emplacement.** `sources/contributions.tex`, contribution « A pretraining method that trains the model on a different task for a while and then switches back » ; voir aussi `sources/part_2/chapter5/article.tex:41` et `:59`.

**Constat.** Le résumé présente comme contribution une méthode générique consistant à passer temporairement à une autre tâche puis à revenir à l'objectif principal. Or *Should We Still Pretrain Encoders with Masked Language Modeling?* expérimente explicitement une stratégie biphasique CLM puis MLM sous budget fixe. Le chapitre le reconnaît correctement. AntLM est un voisin supplémentaire qui alterne CLM/MLM et les masques d'attention.

**Ce qui reste distinctif.** L'initialisation par un encodeur MLM existant, le détour durant l'adaptation biomédicale, le retour au même régime d'encodeur, la validation bilingue et l'analyse interventionnelle des couches basses. C'est cette combinaison qu'il faut attribuer à la thèse, pas la séquence CLM→MLM abstraite.

**Sévérité.** Majeure pour la formulation de nouveauté ; aucun problème pour la validité des résultats expérimentaux.

**Formulation sûre proposée, sans modification du TeX.** « An application of a temporary CLM-to-MLM detour to continued biomedical encoder pretraining, together with a controlled analysis of the representations it leaves behind. »

Sources primaires : [Gisserot-Boukhlef et al., 2025](https://arxiv.org/abs/2507.00994), [AntLM, 2024](https://arxiv.org/abs/2412.03275), [article de la thèse, 2026](https://arxiv.org/abs/2605.12438).

## N-02 — La génération « cas public → note clinique » a un précédent direct

**Emplacement.** `sources/contributions.tex`, dernière contribution ; méthode détaillée dans `sources/part_3/chapter9/article.tex`.

**Constat.** La formulation actuelle — réécrire du texte biomédical public dans le style hospitalier afin d'entraîner un extracteur sans dossiers réels — recouvre directement Asclepius. Ce travail part de cas publiés dans PMC, produit des notes synthétiques et entraîne un modèle clinique partageable.

**Ce qui reste distinctif.** Le travail de la thèse ne produit pas simplement une note isolée : il construit une suite datée de documents, limite chaque génération aux événements déjà survenus, ré-extrait la chronologie entre les étapes, puis aligne les chaînes produites sur 89 champs d'un eCRF de lymphome. Cette chaîne ciblée est substantiellement plus précise que le libellé actuel.

**Sévérité.** Majeure pour la formulation de nouveauté ; le chapitre décrit déjà plusieurs différences techniques qui permettent une revendication étroite.

**Formulation sûre proposée.** « A chronology-constrained pipeline that turns public lymphoma case reports into longitudinal synthetic records and aligns their spans to an 89-field eCRF. »

Sources primaires : [Kweon et al., 2024 — Asclepius](https://aclanthology.org/2024.findings-acl.305/), [Machado et al., 2026 — cas adaptés en notes](https://aclanthology.org/2026.propor-2.15/).

## N-03 — OntoBook doit rester une combinaison précise, pas « ontologie vers texte »

**Emplacement.** `sources/contributions.tex`, contribution OntoBook ; `sources/part_2/chapter6/article.tex:90–106`.

**Constat.** BioOntoBERT est le précédent direct : génération de phrases à partir de neuf ontologies biomédicales, puis MLM de BERT. Le chapitre le décrit désormais explicitement et son tableau de comparaison isole correctement les trois différenciateurs revendiqués : prose générée, objectif relationnel et alignement des deux objectifs.

**Verdict.** La contribution est défendable comme combinaison et comme étude sur des terminologies françaises. La phrase « a way to add structured medical knowledge ... by turning a medical knowledge base into training text » est vraie comme description du livrable, mais trop générale si elle est lue comme une revendication de méthode originale.

**Formulation sûre proposée.** « OntoBook, which verbalizes walks through French medical terminologies and jointly trains masked-token and relation objectives on the resulting aligned text. »

## N-04 — Les modèles ouverts biomédicaux ont plusieurs antériorités proches

**Emplacement.** `sources/contributions.tex`, contribution MC-bio-gliner / MC-bio-embed ; `sources/part_3/chapter8/article.tex:1–66`.

**Constat.** GLiNER fournit déjà l'interface span–type ouverte ; GLiNER-BioMed l'adapte au biomédical avec données synthétiques ; OpenBioNER utilise la description d'un type pour reconnaître des entités biomédicales nouvelles. Le chapitre ne masque pas GLiNER/GLiNER2 et compare GLiNER-BioMed. La nouveauté n'est donc pas « une architecture qui accepte une nouvelle description », mais le modèle français, son espace de description entraîné à partir des terminologies et son application au formulaire longitudinal.

**Verdict.** Pas de correction indispensable si « model designs » signifie bien les modèles précis construits ici. Toute phrase extérieure présentant MC-bio-gliner comme premier extracteur biomédical ouvert serait en revanche indéfendable.

Sources primaires : [GLiNER-BioMed](https://arxiv.org/abs/2504.00676), [OpenBioNER](https://aclanthology.org/2025.findings-naacl.47/).

## N-05 — Les trois contributions de corpus sont principalement des nouveautés de ressource et d'évidence

Pour `biomed-fr`, Biomed-Enriched et MC-Bio, aucun passage examiné ne nécessite une priorité méthodologique absolue. Leur valeur est cumulativement : une ressource française publique, une annotation PMC au paragraphe avec corpus clinique dérivé, puis une étude d'ablation à grande échelle des signaux de sélection. Les verbes « assemble », « label », « identify » et « study » conviennent mieux que « introduce the first method ».

Le point à préserver est la différence entre :

- nouveauté d'une **ressource ou d'un protocole expérimental** ;
- nouveauté d'une **idée générale** telle que la curation, le préentraînement continu ou l'annotation par LLM.

## N-06 — TABIB est correctement présenté comme préliminaire

TABIB apparaît dans la conclusion comme une étude commencée au-delà du cœur de thèse et non parmi les sept contributions. L'expression « preliminary study » borne convenablement son statut. Cet audit n'établit pas qu'aucun benchmark antérieur ne combine les mêmes sept protocoles ; il conclut seulement qu'aucune priorité absolue n'est actuellement formulée.

## Recommandations prioritaires

1. Rétrécir les deux puces génériques du résumé : détour CLM et génération de dossiers.
2. Rétrécir légèrement OntoBook dans le même résumé pour faire apparaître l'alignement et les terminologies françaises.
3. Conserver l'attribution explicite à Gisserot-Boukhlef et BioOntoBERT dans les chapitres : elle protège la crédibilité de la nouveauté au lieu de l'affaiblir.
4. Présenter MC-bio-gliner comme une instanciation française et longitudinale de l'extraction conditionnée par descriptions.
5. Ne pas employer `first`, `first-ever`, `unprecedented` ou `unique` pour ces familles sans nouvelle revue systématique.

## Limites

Il s'agit d'un audit ciblé d'antériorité, fondé sur les articles primaires les plus proches trouvés et sur les références déjà présentes dans la thèse. Il ne constitue ni une recherche de brevet ni une revue systématique exhaustive de toutes les bases bibliographiques. Son objectif est plus conservateur : identifier les formulations que des précédents manifestes suffisent déjà à rendre vulnérables.

## Conclusion

Le cœur scientifique reste défendable. Les deux risques majeurs viennent d'un résumé trop abstrait, non d'une absence de contribution : le détour CLM est nouveau ici par son cadre d'adaptation biomédicale et son analyse mécaniste ; la génération synthétique est nouvelle ici par sa structure longitudinale et son alignement eCRF. Dire exactement cela rend la thèse plus solide.
