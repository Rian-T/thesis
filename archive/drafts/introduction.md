# Introduction

<!-- Draft for introduction.tex -->

[quote bitter lesson]

Health has been one of the earliest and most prominent application domains for artificial intelligence depuis ses débuts.

Les usages sont variés, allant de l'aide au diagnostic à la gestion des dossiers médicaux, la section de cohorte, la redaction de comptes-rendus ou encore l'extraction d'informations cliniques.

des les années 1970, MYCIN le système expert emblématique, développé à Stanford pour diagnostiquer les infections bactériennes et recommander des antibiotiques. Il atteignait déjà des performances comparables aux spécialistes humains dans son domaine étroit.

Cependant, ces systèmes étaient limités par leur dépendance à des règles explicites et à des bases de connaissances statiques, ce qui entravait leur capacité à s'adapter à la complexité et à la variabilité des données médicales réelles.

INTERNIST-1 / CADUCEUS (années 70-80) : Système de diagnostic en médecine interne couvrant des centaines de maladies.

Cependant, ces systèmes basés sur des règles avaient du mal à gérer la complexité et la variabilité des données médicales réelles. Ils étaient rigides et nécessitaient une maintenance constante pour rester à jour avec les avancées médicales.

Cest donc très couteux davoir des experts médicaux pour annoter des données cliniques et ecrire des regles.

Avec l'avènement de l'apprentissage automatique dans les années 1990 et 2000, les approches basées sur les données ont commencé à dominer le domaine de l'IA en santé. Des algorithmes d'apprentissage supervisé et non supervisé ont été appliqués pour entraîner des modèles. 

L'interpretabilité des modeles de regles à été troqué contre la performance des reseaux de neurones profonds capable de capturer des patterns complexes dans les données.

R2 ImageChecker (1998) : Premier système de détection assistée par ordinateur approuvé par la FDA pour la mammographie. Utilisait des réseaux de neurones pour repérer des microcalcifications suspectes.
PAPNET (années 90) : Réseau de neurones pour le dépistage cytologique du cancer du col de l'utérus (frottis).

Plus récemment, le paradigme du scaling a pris le dessus avec des modèles de langage massifs pré-entraînés sur d'immenses corpus de données textuelles. Plutot que des petits jeu de données annotées, ces modèles apprennent des représentations riches du langage à partir d'une quantité colossale de données non annotées, puis sont adaptés à des tâches spécifiques en santé.

Plus besoin dexpert cher, plus besoin de regles ecrites a la main, plus besoin de jeux de données annotées en santé. Simplement lintegralité du corpus medical et la connaissance emerge dans les representations du modele.

malgres que la santé nous offre plein de base de connaissance structuré et curated comme UMLS, SNOMED-CT, RxNorm, le temps a montré que les modeles generaux de langage pre-entraînés sur des données massives non structurées surpassent les approches basées sur des regles et des bases de connaissances spécifiques au domaine.

Il semble que nos modeles narrive pas a integrer efficacement ces bases structurées, ou que ces bases de connaissances ne couvrent pas toute la complexité et la variabilité de la connaissance et du langage médical tel qu'il est utilisé dans la pratique.

Cependant une limitation de la santé que les autres domaines n'ont pas est la confidentialité et la rareté des données cliniques annotées. Les données médicales sont sensibles et difficiles à obtenir en grande quantité pour l'entraînement de modèles.

Les travaux dapdation de modele de langue au medical utilise souvent des données publiques comme PubMed ou des forum de patients, mais ces données ne reflètent pas toujours le langage clinique réel utilisé dans les dossiers médicaux électroniques. Le domaine clinique a un jargon, des abréviations et des styles d'écriture uniques qui diffèrent des textes médicaux grand public. De plus, y'a mimic aux US mais en france on a pas grand chose de public.

donc probleme: le paradigme qui a gagné cest le pretraining scaling, mais en santé on a pas de données cliniques massives publiques pour pre-entrainer des modeles de langue.

Peut-on trouver des nouvelles manieres exploiter les donnée publique pour pre-entrainer des modeles de langue adaptés au domaine clinique, sans utiliser de données cliniques sensibles ?

Sommaire:

Related works:
- Language models and Adapting then to clinical domain
- Quality annotation of corpora
- Information extraction in clinical domain

Part1: Corpus
- Gathering a biomedical corpus
- Quality signals
- Hidden content type

Part2: Domain language modeling

- Encoders (CamemBERT-bio, ModernCamemBERT-bio)
- Decoders doesnt continue-pretrain anymore
- Beyond MLM: other objectives

Part3: Clinical task adaptation

- Limitations of naive approach
- Better architectures for low-resource clinical IE
- Synthetic data for task finetuning

Conclusion