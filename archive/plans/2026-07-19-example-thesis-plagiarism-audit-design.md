# Design — audit ponctuel de similarité avec les thèses de `exemples/`

Date : 19 juillet 2026  
Nature : audit local ponctuel, sans modification du manuscrit.

## Objectif

Détecter dans la prose de la thèse les reprises verbatim ou légèrement remaniées provenant des trois PDF présents dans `exemples/`, puis examiner manuellement les résultats afin de séparer les passages préoccupants des ressemblances académiques banales.

Cet audit ne prétend pas certifier l'absence de plagiat contre la littérature entière. Son verdict est limité aux trois documents fournis :

- `exemples/exemple_nathan_godey.pdf` ;
- `exemples/exemple_nguyen.pdf` ;
- `exemples/exemple_duquenne.pdf`.

## Périmètre de la thèse

L'entrée comprend tous les fichiers `sources/**/*.tex`. Les éléments suivants sont exclus de la comparaison textuelle : commandes et environnements LaTeX, citations et références croisées, mathématiques, code, coordonnées TikZ, contenu tabulaire essentiellement numérique et bibliographie.

Les légendes et cellules contenant de la prose restent incluses. Pour chaque résultat, l'audit conserve le fichier et la ligne d'origine côté thèse, ainsi que le document et la page côté exemple.

## Normalisation

Les PDF sont extraits avec Poppler. Les deux corpus sont ensuite normalisés de manière identique :

1. conversion Unicode et passage en minuscules ;
2. réparation des mots coupés par une césure de fin de ligne dans les PDF ;
3. remplacement de la ponctuation et des espaces multiples par un espace unique ;
4. suppression des artefacts LaTeX et PDF sans valeur linguistique ;
5. conservation des mots dans leur ordre d'origine.

Une seconde représentation conserve les limites de phrases et de paragraphes pour afficher un contexte lisible.

## Détection

### Correspondances exactes

Le détecteur recherche les séquences communes d'au moins douze mots normalisés. Les chevauchements adjacents sont fusionnés en un seul passage maximal.

- 20 mots ou plus : priorité haute ;
- 12 à 19 mots : priorité moyenne, généralement soumise à davantage de faux positifs.

Les séquences apparaissant dans plusieurs thèses exemples sont conservées mais marquées comme probablement formulaires ou conventionnelles.

### Correspondances approchées

Le second détecteur compare des phrases et fenêtres de phrases d'au moins dix-huit mots. Une récupération de candidats par n-grammes lexicaux évite une comparaison quadratique complète ; les meilleurs candidats sont ensuite classés par similarité de séquence et recouvrement pondéré des mots.

Un candidat approché n'est rapporté que s'il satisfait les deux conditions suivantes :

- similarité lexicale élevée après normalisation ;
- segment commun suffisamment spécifique pour ne pas reposer uniquement sur des mots fonctionnels ou une définition standard.

Les seuils numériques définitifs sont calibrés sur les distributions observées, mais ne peuvent être abaissés au point d'inonder le rapport : seuls les candidats pouvant raisonnablement être relus manuellement sont conservés.

## Réduction des faux positifs

Sont classés séparément ou écartés après examen :

- page de garde, mentions HAL, composition du jury et formulations administratives ;
- titres génériques et transitions académiques courtes ;
- noms complets d'articles, jeux de données, institutions ou modèles ;
- citations bibliographiques et passages constitués principalement d'une citation directe correctement attribuée ;
- définitions techniques quasi canoniques lorsque la formulation n'est pas distinctive ;
- texte identique provenant manifestement d'un modèle institutionnel commun.

L'exclusion automatique reste prudente : les candidats longs sont visibles dans les résultats bruts même lorsqu'ils semblent formulaires.

## Validation manuelle et verdicts

Chaque résultat final reçoit l'un des verdicts suivants :

- **préoccupant** : formulation longue ou distinctive reprise sans attribution claire ;
- **à vérifier** : proximité substantielle, mais attribution, source commune ou caractère canonique incertain ;
- **similitude technique ou conventionnelle** : passage réel mais non probant pour le plagiat ;
- **faux positif** : ressemblance produite par la normalisation, les noms propres ou des fragments discontinus.

Le jugement tient compte de la longueur, de la rareté de la formulation, de la continuité du passage, du contexte et de la présence d'une attribution.

## Livrables

L'audit produit uniquement :

1. des fichiers temporaires d'extraction et de calcul sous `tmp/plagiarism-audit/` ;
2. un rapport Markdown daté sous `docs/reviews/`, contenant la méthode, les statistiques globales, tous les résultats retenus et les limites.

Aucun script permanent n'est ajouté au dépôt et aucun fichier TeX n'est modifié.

## Vérification

Avant remise du rapport :

- recompter les documents et les volumes analysés ;
- vérifier manuellement tous les résultats classés préoccupants ou à vérifier dans les deux contextes ;
- contrôler les localisateurs de fichier, ligne et page ;
- exécuter au moins un test positif synthétique et un test négatif pour s'assurer que le détecteur exact fonctionne ;
- confirmer par diff qu'aucun fichier du manuscrit n'a été modifié.
