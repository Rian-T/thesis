# Audit du langage causal

Date : 20 juillet 2026  
Périmètre : manuscrit principal (`sources/`), avec priorité aux chapitres de contribution et à la conclusion.  
Action sur le manuscrit : aucune.

## Méthode

Chaque formulation causale ou mécaniste repérée a été classée selon quatre niveaux :

1. **identification forte** : intervention contrôlée où le facteur invoqué est effectivement isolé ;
2. **support limité au protocole** : ablation utile, mais généralisation ou mécanisme non identifié ;
3. **association descriptive** : différence de scores sans intervention isolant la cause ;
4. **hypothèse** : explication plausible qui doit rester explicitement conjecturale.

Le critère n'est donc pas « l'explication paraît-elle raisonnable ? », mais « le protocole permet-il d'écarter les explications concurrentes ? ».

## Verdict

Le manuscrit est généralement prudent, mais contient **4 surinterprétations majeures**, **11 formulations à borner**, et plusieurs bons garde-fous déjà en place. Les risques principaux sont :

- transformer une ablation en preuve d'un mécanisme interne ;
- attribuer une différence entre corpus ou modèles à une propriété non mesurée ;
- employer *confirm*, *ensure*, *necessary* ou *establish* là où les données montrent seulement une compatibilité ;
- inférer une cause à partir de vingt essais dans l'expérience agentique exploratoire.

## 1. Corrections majeures recommandées

### C1 — La fidélité des reformulations OntoBook n'est pas assurée par le prompt et deux filtres

**Emplacement :** `sources/part_2/chapter6/article.tex:187`, puis légendes vers les lignes 215 et 240.

**Texte problématique :** le prompt « ensures » que le contenu reste ancré dans l'ontologie ; la figure affirme que tous les codes et relations sont préservés.

**Pourquoi c'est trop fort :** les deux contrôles décrits vérifient seulement une longueur minimale et la présence des codes sources. Ils ne vérifient ni l'absence d'ajouts médicaux, ni la polarité, ni la direction, ni la conservation exhaustive des relations. Un décodage à température zéro ne constitue pas davantage une preuve de fidélité sémantique.

**Formulation minimale défendable :**

> The prompt is designed to keep the generated text grounded in the ontology structure. We discard outputs shorter than 50 characters or failing to mention the source codes; relation-level fidelity is not independently validated here.

Dans les légendes, remplacer *while preserving* par *with instructions to preserve*.

### C2 — La « double dissociation » des couches basses n'est pas établie

**Emplacement :** `sources/part_2/chapter5/article.tex:388–396`.

**Texte problématique :** « establish a double dissociation: low layers are necessary and mid layers are not » ; `p=0.36` est interprété comme un modèle qui « matches » la baseline.

**Pourquoi c'est trop fort :** ne pas rejeter une différence n'établit pas l'équivalence ; il faudrait un test d'équivalence avec une marge fixée. Geler des couches modifie aussi l'optimisation et la capacité d'adaptation, pas uniquement le lieu causal de l'information. Enfin l'intervention n'est réalisée que sur French Base.

**Formulation minimale défendable :**

> In French Base, the freeze interventions are consistent with low-layer adaptation contributing more than mid-layer adaptation to the CLM gain. The low-layer-freeze condition is not significantly different from the MLM baseline (`p=0.36`), but this is not an equivalence test.

Pour la phase de decay, remplacer *confirming* par *consistent with*.

### C3 — L'explication mécaniste de l'alignement OntoBook n'est pas mesurée

**Emplacement :** `sources/part_2/chapter6/article.tex:471–489` et conclusion du chapitre.

**Texte problématique :** les objectifs « receive conflicting gradient signals », l'alignement les fait se « reinforce », les marqueurs offrent des raccourcis, et « Alignment is what separates… ».

**Pourquoi c'est trop fort :** la chute de performance du régime désaligné est réelle, mais aucune similarité de gradients, trajectoire d'optimisation, représentation de raccourci ou expérience factorielle *raw walk + relation objective* n'est rapportée. Le mécanisme proposé est plausible, pas identifié.

**Formulation minimale défendable :**

> The results show that, in this setup, using the same text for MLM and relation prediction is important. One possible explanation is that unrelated training inputs create less compatible optimization signals; gradient-level analysis would be needed to test this mechanism.

Et dans la conclusion :

> Alignment is the condition that separates the successful configuration from the misaligned configuration tested here.

### C4 — L'expérience agentique ne permet pas encore d'identifier « l'autorité » comme mécanisme

**Emplacement :** `sources/conclusion.tex:486–514`.

**Texte problématique :** « the effect comes from the claim of authority » puis « The mechanism is deference under pressure to the authority artifact ».

**Pourquoi c'est trop fort :** il s'agit d'un modèle, d'un scénario et de vingt essais par condition, avec plusieurs changements d'appareil entre conditions. Le contraste avec une note authentique périmée rend l'hypothèse intéressante, mais n'isole pas à lui seul autorité, falsification, formulation ou dynamique conversationnelle.

**Formulation minimale défendable :**

> The contrast is consistent with sensitivity to the forged note's claim of authority, although this exploratory probe does not isolate that mechanism.

Et :

> Forced retrieval alone does not eliminate the observed failure in this scenario.

Cette dernière phrase décrit l'observation sans extrapoler à toutes les corrections fondées sur l'accès à l'information.

## 2. Formulations importantes à borner

### MC-Bio : contenu, qualité et volume

- `sources/part_1/chapter3/article.tex:98` — un seul contrôle aléatoire, de volume au demeurant ambigu, ne « confirme » pas que l'effet est spécifique au type de contenu. Écrire *supports a content-specific interpretation, subject to the volume-control limitation*.
- `:139`, `:164`, `:223` — les filtres de qualité rédactionnelle et de précision terminologique obtiennent des scores inférieurs dans ces configurations ; le fait qu'ils retireraient des notes informelles utiles n'est pas mesuré. Conserver *one possible explanation is…* plutôt que présenter ce mécanisme comme la leçon des ablations.

### Biomed-Enriched : propriétés des données et résultats aval

- `sources/part_1/chapter2/article.tex:181` — les distributions de scores soutiennent le seuil choisi, mais n'« expliquent » pas les gains. Remplacer par *are consistent with the gains observed for…*.
- `:223` — une fenêtre 8K permet de conserver davantage de contexte ; elle ne garantit ni que tous les articles sont complets, ni que les dépendances inter-paragraphes sont apprises. Employer *allows articles up to the context limit to be processed with their structure preserved*.
- `:237` — « ideal balance » et « without the risk of catastrophic forgetting » ne sont pas testés. Présenter le choix de stage 1 comme un compromis expérimental, sans garantie.
- `:319`, `:507`, `:511` — une hausse sur un benchmark français et les maxima propres à quelques tâches soutiennent une spécialisation observée ; ils ne démontrent pas à eux seuls une généralisation au-delà de l'anglais ni que tel type de paragraphe « bénéficie » causalement à une famille de tâches.
- `:550` — l'analyse BiaHS montre le risque pour deux autres filtres ; elle ne démontre pas que le filtre Biomed-Enriched « avoids this particular risk ». Écrire qu'il *does not use either of the two classifiers evaluated here; its own contamination propensity remains to be measured*.

### CamemBERT-bio : comparaisons inter-corpus et inter-systèmes

- `sources/part_2/chapter4/article.tex:90` — *confirms that corpus size positively influences performance* doit être borné à la comparaison biomed-fr-small/full et ne prouve pas une loi générale.
- `:92` — la moindre diversité d'AP-HP comme cause des résultats de Dura et la base de connaissances comme cause du meilleur rappel de Mulligen ne sont pas isolées dans les comparaisons citées. Employer respectivement *may reflect* et *is compatible with*.
- `:184` — un macro-F1 supérieur pondère davantage les classes minoritaires, mais ne prouve pas à lui seul une performance « more balanced across classes ». Il faut des scores par classe ou un écart de dispersion.

### Détour CLM : effets robustes, mécanismes plus fragiles

- `sources/part_2/chapter5/article.tex:236` — l'effet français plus marqué est compatible avec un écart de domaine plus grand, mais langue, famille de modèle et préentraînement initial changent ensemble. L'explication par l'exposition PubMed et les couches basses doit rester une hypothèse.
- `:419` — le mauvais résultat des transplants est observé ; la « mismatch » entre couches co-adaptées est une interprétation non directement testée.
- `:442` — dire que le bénéfice n'est pas localisable par **les transplants testés**, et non qu'il ne peut pas l'être en général.
- Point positif : `:468–475` explicite déjà correctement que l'asymétrie encodeur-décodeur est exploratoire et confondue.

### OntoBook : portée des ablations

- `sources/part_2/chapter6/article.tex:311` — le gain maximal sur Distemist est compatible avec une aide au codage fin des maladies, sans isoler cette propriété du jeu de données.
- `:342` — relation-only échoue comme objectif autonome **dans la configuration testée** ; cela ne démontre pas son impossibilité générale.
- `:433` — attribuer le score ATC au transfert de relations médicament-maladie est particulièrement fragile : ATC est décrit plus haut comme une hiérarchie sans arêtes sémantiques et les volumes de marches diffèrent fortement entre ontologies.
- `:466–489` — la corrélation inverse entre probes géométriques et scores aval sur quelques variantes ne démontre pas que la « flexibilité » est préférable ni qu'une géométrie rigide doit être désapprise. Employer *does not support a simple positive relationship between the tested probes and downstream performance*.

### Évaluation et conclusion générale

- `sources/part_3/chapter7/article.tex:319–323` — « scaling further does not help » doit devenir *did not help among the tested Qwen sizes* ; l'affirmation matérielle sur les générateurs multi-milliards requiert un budget mémoire défini et est traitée séparément dans l'audit de cohérence.
- `sources/conclusion.tex:68` — l'écart carbone est d'abord un écart d'échelle et de recette mesurés ; « because it curates… » est une décomposition causale plus précise que les données disponibles.
- `sources/introduction.tex:120` — la non-portabilité des probabilités de Leeds est une interprétation historiquement plausible, mais le multicentre ne constitue pas une expérience isolant la provenance géographique des probabilités. *This is consistent with…* serait plus exact.

## 3. Formulations déjà bien calibrées

- Le chapitre 5 qualifie explicitement l'asymétrie encodeur-décodeur d'« exploratory » et en énumère les facteurs confondants.
- Le chapitre 8 précise que les écarts entre sections ne permettent pas d'identifier une cause linguistique unique.
- Plusieurs passages utilisent déjà correctement *may*, *possibly due to*, *is consistent with* et *we hypothesize*.
- La conclusion agentique reconnaît « one model, one scenario, and twenty pairs » et des intervalles larges ; cette prudence doit simplement remonter jusqu'aux phrases mécanistes qui précèdent.
- Les affirmations descriptives du type « le score augmente de X » ou « la variante testée obtient le meilleur résultat » sont sûres dès lors qu'elles restent limitées au protocole observé.

## 4. Ordre de correction conseillé

1. Remplacer la garantie de fidélité OntoBook par une intention de prompt et déclarer l'absence de validation relationnelle.
2. Retirer « double dissociation », l'équivalence implicite fondée sur `p=0.36`, et les mécanismes de gradients non mesurés.
3. Requalifier l'autorité de la note falsifiée comme hypothèse exploratoire.
4. Remplacer systématiquement les verbes *ensure / confirm / establish / necessary* par des formulations bornées lorsque le facteur n'est pas isolé.
5. Garder les explications biologiquement ou techniquement plausibles, mais les signaler explicitement comme hypothèses à tester.

## Conclusion

Les résultats empiriques importants ne disparaissent pas lorsque le langage est resserré : le détour CLM bat ses baselines, la configuration OntoBook alignée bat les configurations comparées, certains filtres MC-Bio obtiennent de moins bons scores, et le scénario agentique produit davantage d'actes dangereux. Ce qu'il faut retirer est uniquement la couche d'identification causale ou mécaniste que les protocoles actuels ne permettent pas encore de soutenir.
