# Audit visuel du PDF final

Date de la passe : 20 juillet 2026  
Périmètre : `thesis.pdf`, sans recompilation et sans modification du manuscrit.

## Verdict exécutif

Le PDF est matériellement propre et soutenable : aucune page tronquée, aucun chevauchement manifeste, aucune image manquante et aucun renvoi non résolu n'ont été observés. Les tableaux larges restent dans la page, les figures sont nettes et les styles sont cohérents sur les 270 pages.

La passe visuelle confirme cependant un problème de **statut scientifique**, non de composition : plusieurs figures dont les données sont provisoires ou non enregistrées apparaissent exactement comme des résultats finaux. La chaîne de génération ne produit notamment aucun avertissement visible pour les entrées marquées `final`, statut qui contourne le garde-fou documenté. Ce point est détaillé dans l'[audit de traçabilité](2026-07-20-tables-figures-data-audit.md).

## 1. Instantané inspecté

| Propriété | Valeur |
|---|---:|
| fichier | `thesis.pdf` |
| SHA-256 | `28f64b6099cf61618a00e2478e9313e6715df19a55594d437b1a8113834f4a71` |
| création PDF | 20 juillet 2026, 00:35:38 CEST |
| taille | 9 283 744 octets |
| pages | 270 |
| format | A4, PDF 1.7 |
| moteur | LuaTeX 1.21.0 |

Aucun fichier sous `sources/` ou `plots/` n'était plus récent que ce PDF au moment du contrôle. Le PDF était donc à jour par rapport aux sources et figures présentes dans le dépôt.

Le PDF a été régénéré une fois pendant l'audit. La comparaison des deux extractions textuelles n'a trouvé qu'un ajout sur la page PDF 188 — la phrase d'ouverture « Don't get too excited. Building the models was the easy part. » — dont le rendu final a été inspecté séparément : il reste dans les marges et ne collisionne pas avec l'épigraphe. Le hash ci-dessus est celui de cette seconde version, vérifiée en dernier.

## 2. Méthode

La vérification a combiné quatre niveaux :

1. lecture des métadonnées et du journal de compilation ;
2. extraction intégrale du texte, recherche de `??`, citations ou références indéfinies, marqueurs `TODO/FIXME/XXX` et messages d'erreur ;
3. rendu raster des 270 pages, assemblé en 17 planches contact inspectées une à une ;
4. rendu à 150 dpi des pages sensibles : figures de résultats des chapitres 17–20, tableaux de transfert, courbes risque–couverture, carbone, TABIB et annexes numériques.

Le contrôle de toutes les commandes `\includegraphics` n'a trouvé aucun fichier absent.

## 3. Résultats de composition

### Aucun défaut bloquant

- aucune référence ou citation affichée comme `??` ;
- aucune image absente ou remplacée par un cadre vide ;
- aucun tableau ou graphique coupé par les marges ;
- aucun chevauchement de texte, de légende ou de folio ;
- aucun fragment de note de travail (`TODO`, `FIXME`, `XXX`) dans le texte extrait ;
- bibliographie continue et homogène jusqu'à la dernière page ;
- annexes A–G lisibles, y compris les tableaux denses des pages PDF 229–230.

Les pages blanches observées entre certaines parties et certains chapitres sont cohérentes avec l'ouverture des chapitres sur une page impaire. Elles ne ressemblent pas à des pertes de contenu.

### Avertissements LaTeX non bloquants

Le journal contient des `Underfull` et quelques `Overfull` très faibles. Le plus grand dépassement mesuré est de `1.84756 pt`; aucun n'est visible comme une sortie de marge sur les rendus. Les avertissements répétés `caption/hypcap`, `tracklang` et l'option `xcolor usenames` sont des avertissements de paquet, pas des défauts visibles du document.

## 4. Pages sensibles contrôlées en pleine résolution

| Zone | Observation visuelle |
|---|---|
| chapitre 17, pages PDF 172–174 | tableau OntoBench-FR, schéma contrastif et figures 17.3–17.4 alignés et lisibles |
| chapitre 18, pages PDF 177–185 | frise eCRF, règles de matching, tableaux et figures 18.4–18.9 propres ; légendes dans la page |
| conclusion, page PDF 190 | tableau 19.1 correctement composé ; pas de collision avec la prose |
| TABIB, pages PDF 196–197 | cartes de chaleur nettes ; valeurs et légendes lisibles |
| annexe G, pages PDF 228–230 | graphiques et tableaux de sensibilité dans les marges ; corps petit mais lisible |

## 5. Défauts ou risques qui restent visibles dans le PDF

### V1 — Des données provisoires ont l'apparence de résultats finaux

La figure 17.3, la courbe d'efficacité en données de la figure 18.8 et les intervalles appariés du chapitre 18 sont composés sans filigrane ni mention de statut. Or le registre et les notes de génération indiquent que tout ou partie de ces nombres restent provisoires, transcrits depuis un dashboard ou non régénérables depuis les prédictions versionnées.

**Sévérité : critique pour la traçabilité, nulle pour la mise en page.** Le PDF ne permet pas au lecteur de distinguer ces résultats des observations enregistrées.

### V2 — La prose TABIB contredit sa propre figure

À la page PDF 196, la figure 20.2 donne `unsafe = 0 %` à Gemma4 E2B **et** MedGemma 1.5. Le paragraphe immédiatement dessous affirme pourtant : « Only MedGemma stays at zero ». La valeur de Gemma4 E2B est également codée à `0` dans `plots/part_3/evalllm_figures.py`.

**Sévérité : majeure.** Il s'agit d'une contradiction directement visible entre texte et graphique. Elle a été ajoutée à l'audit des données.

### V3 — Densité ponctuelle, mais pas de défaut typographique

Quelques pages sont très denses, notamment les tableaux de l'annexe G et certaines pages de bibliographie. À taille réelle, leur lecture reste possible et aucun élément ne sort de la zone de composition. Je ne recommande pas une reprise globale de la maquette pour ce seul motif.

## 6. Conclusion

Le PDF passe le contrôle de finition visuelle. Les corrections prioritaires ne concernent pas l'alignement ou la typographie, mais la fiabilité des résultats qui y sont présentés comme définitifs et la contradiction TABIB repérable à la lecture. Une recompilation finale devra être contrôlée par différence de pages après correction du contenu, mais aucune refonte graphique n'est nécessaire.
