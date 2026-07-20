# Bilan général des audits de la thèse

Date du bilan : 20 juillet 2026  
Instantané PDF de référence : SHA-256 `28f64b6099cf61618a00e2478e9313e6715df19a55594d437b1a8113834f4a71`  
Contrainte respectée : aucun fichier `.tex`, `.bib` ou fichier de données de la thèse n'a été modifié pendant cette série d'audits.

## Verdict global

La thèse est déjà solide sur sa structure, sa présentation et une grande partie de ses résultats centraux. Le PDF de 270 pages est propre, les principaux calculs ont été retrouvés, les TikZ corrigés représentent désormais les méthodes avec prudence, et l'audit de similarité avec `exemples/` n'a trouvé aucun indice préoccupant de reprise textuelle.

Le risque principal avant dépôt n'est pas une erreur générale de méthode. Il est concentré dans trois zones :

1. **la provenance de certains résultats**, car un statut `final` non documenté contourne le garde-fou `registered/provisional` ;
2. **quelques contradictions fortes entre parties**, surtout sur MIMIC-III et la revue clinique annoncée dans l'abstract ;
3. **des formulations plus fortes que les preuves**, notamment pour OntoBook, le détour CLM, la nouveauté de certains benchmarks et quelques mécanismes causaux.

Autrement dit : il ne faut pas réécrire la thèse. Il faut fermer une liste courte de défauts à fort effet, puis borner quelques revendications.

## 1. Ordre de correction recommandé

### P0 — À corriger avant tout dépôt

| Priorité | Problème encore présent | Pourquoi il est dangereux | Action minimale |
|---:|---|---|---|
| P0.1 | `visual_data.json` contient 30 entrées `final`, statut absent du schéma et non bloqué par le code | des données non enregistrées peuvent apparaître sans filigrane comme des résultats finaux | définir les statuts autorisés, faire échouer tout statut inconnu, puis enregistrer ou marquer provisoires les observations concernées |
| P0.2 | la conclusion affirme qu'aucun modèle n'a vu de vrai dossier patient, alors que le modèle anglais 50B utilise 20 % de notes MIMIC-III | contradiction factuelle directe entre chapitres | restreindre la phrase aux modèles/contributions réellement concernés ou expliciter l'exception MIMIC-III |
| P0.3 | l'abstract affirme que des cliniciens ont évalué les dossiers synthétiques ; aucun protocole, résultat ou annexe ne documente cette évaluation | revendication humaine invérifiable et très visible | documenter échantillon, critères, effectif et résultats, ou retirer la phrase |
| P0.4 | Raghavan 2014 est cité pour « jusqu'à 80 % des entités absentes du structuré » | l'article rapporte des besoins en texte libre pour des critères d'éligibilité, pas ce taux d'entités | remplacer par les mesures exactes et leur population, ou supprimer le nombre |
| P0.5 | la clé `medgemma2026` cite le rapport MedGemma 2025, pas MedGemma 1.5 | le modèle évalué et la référence ne correspondent pas | citer la source officielle de MedGemma 1.5 ou décrire précisément la version réellement utilisée |
| P0.6 | plusieurs points de la partie 3 ont des registres concurrents ou une provenance de dashboard | un lecteur ne peut pas reconstruire sans ambiguïté la table/figure finale | choisir une source canonique par expérience, la versionner avec hashes et régénérer tableaux/figures depuis elle |

### P1 — Corrections scientifiques majeures

| Priorité | Problème | Action minimale sûre |
|---:|---|---|
| P1.1 | OntoBook semble sélectionner époque et `lambda` sur les scores aval finaux | identifier un split de développement distinct ou présenter l'analyse comme exploratoire |
| P1.2 | les `p < .001` OntoBook ne sont pas reproductibles avec trois graines et sans test/unité explicités | donner le test, l'unité, les observations et la correction multiple ; sinon retirer les p-values |
| P1.3 | prompt et filtres OntoBook sont décrits comme garantissant la fidélité relationnelle | remplacer `ensure` par une réduction de risque et reconnaître l'absence de validation humaine systématique |
| P1.4 | la « double dissociation » du détour CLM n'est pas démontrée par un effet significatif d'un côté et `p=.36` de l'autre | parler de profils d'intervention différents ; ne pas transformer non-significativité en équivalence |
| P1.5 | l'explication par conflit/alignement de gradients n'est pas mesurée | présenter le mécanisme comme hypothèse compatible avec les résultats |
| P1.6 | `ModernCamemBERT-bio-v2` apparaît dans la conclusion sans définition expérimentale dans les chapitres | relier explicitement ce checkpoint à une configuration documentée ou retirer cette ligne de comparaison |
| P1.7 | la conclusion affirme que seul MC-bio-gliner est hébergeable sur site | borner à l'avantage mémoire sur les systèmes de performance comparable réellement mesurés |
| P1.8 | la prose TABIB dit que seul MedGemma reste à 0 % d'avis dangereux ; la figure donne aussi Gemma4 E2B à 0 % | distinguer les deux zéros et n'interpréter que le mécanisme effectivement mesuré |
| P1.9 | le résumé Biomed-Enriched annonce 61.08 comme meilleur score, alors qu'une cellule affichée atteint 61.71 | préciser la comparaison visée ou corriger le maximum |

### P2 — Bornage et maintenance

- Restreindre la nouveauté du détour CLM à sa combinaison précise : initialisation MLM biomédicale, aller-retour CLM→MLM, validation bilingue et interventions de couches.
- Présenter OntoBook comme la combinaison française précise de parcours, reformulation et objectifs alignés, pas comme le premier préentraînement sur texte d'ontologie.
- Éviter les négations exhaustives non prouvées : « aucun benchmark », « aucun jeu ouvert », « les langues autres que l'anglais restent inexplorées ».
- Séparer, dans MC-Bio, contenu/qualité et volume : les ablations actuelles ne permettent pas toujours d'attribuer l'effet à une seule cause.
- Qualifier le comparatif extracteur–générateur de comparaison de systèmes, pas d'ablation architecturale contrôlée.
- Réduire la whitelist bibliographique aux vraies exceptions et archiver les statistiques vivantes avec leur requête.

## 2. Points désormais rassurants

### Chiffres et calculs

Les recalculs des moyennes principales de CamemBERT-bio, MC-Bio, du détour CLM, d'OntoBook, d'OntoBench-FR, du corpus synthétique et des analyses stylométriques n'ont pas révélé d'erreur systématique. Les chiffres GPT-3 de la table 7.1 correspondent au papier. Les valeurs Chinchilla affichées sont cohérentes avec l'équation citée.

### État de l'art corrigé

Plusieurs défauts des premières passes du 19 juillet ne sont plus présents dans l'état courant :

- BioOntoBERT a maintenant le bon titre et les bons auteurs, et sa clé a été retirée de la whitelist ;
- SciBERT est décrit par l'intersection de vocabulaires, pas comme un taux direct de mots sur-segmentés ;
- DeepSeek-R1-Zero est distingué de DeepSeek-R1 ;
- BioMistral est correctement borné au régime 3-shot ;
- les 1.13 heures de MosaicBERT sont rattachées au score cible GLUE 79.6 ;
- l'exemple de Shannon utilise maintenant un alphabet de 27 symboles cohérent avec le calcul ;
- EntiGraph, SapBERT, Snomed2Vec, RDF2Vec et GLiNER sont décrits avec des schémas plus fidèles et des légendes explicitement illustratives.

Les rapports du 19 juillet doivent donc être lus comme un historique de revue, pas comme une liste entièrement actuelle.

### Bibliographie

La correction BioOntoBERT est effective. En revanche, la raison structurelle de l'erreur reste valable : une clé whitelistée est `SKIPPED`, donc `make checkbib` ne certifie pas ses métadonnées. TxT360 conserve encore `{LLM360}` comme auteur collectif, et les notices synthétiques AP-HP/PubMed restent insuffisantes pour reproduire les nombres.

### Présentation

Le PDF complet passe la revue visuelle : pas de `??`, pas d'image absente, pas de contenu coupé, pas de collision visible. Les quelques dépassements LaTeX sont inférieurs à 1.85 pt et ne produisent pas de défaut apparent. Aucune refonte de maquette n'est justifiée.

### Similarité textuelle

Le contrôle programmatique contre les thèses de `exemples/`, complété par une revue manuelle des meilleurs matches, n'a trouvé que des fragments institutionnels, des titres bibliographiques et des formulations administratives courtes. Aucun passage n'a été classé comme reprise préoccupante.

## 3. Carte des audits

| Audit | Question traitée | Résultat principal |
|---|---|---|
| [Nouveauté et antériorité](2026-07-20-novelty-prior-art-audit.md) | les contributions sont-elles réellement distinctes de l'état de l'art ? | nouveautés défendables si formulées comme combinaisons précises |
| [Comparabilité expérimentale](2026-07-20-experimental-comparability-audit.md) | les comparaisons isolent-elles le facteur revendiqué ? | CLM/MLM solide ; MC-Bio et OntoBook demandent davantage de bornage |
| [Cohérence interne](2026-07-20-internal-consistency-audit.md) | les parties se contredisent-elles ? | deux contradictions critiques : MIMIC-III et revue clinique |
| [Citations et affirmations](2026-07-20-citation-claim-alignment-audit.md) | chaque source soutient-elle la phrase ? | Raghavan et MedGemma à corriger en priorité |
| [Langage causal](2026-07-20-causal-language-audit.md) | les mécanismes sont-ils réellement identifiés ? | quatre mécanismes doivent être reformulés comme hypothèses ou associations |
| [Tables, figures et données](2026-07-20-tables-figures-data-audit.md) | les valeurs sont-elles traçables et cohérentes ? | garde-fou de statut défaillant et vérités concurrentes en partie 3 |
| [PDF final](2026-07-20-final-pdf-visual-audit.md) | le document compilé est-il propre ? | oui visuellement ; les statuts provisoires ne sont pas visibles |
| [Fidélité de l'état de l'art](2026-07-19-related-work-fidelity-audit.md) | les articles sont-ils correctement retranscrits ? | première passe, largement corrigée depuis |
| [Addendum de fidélité](2026-07-19-related-work-fidelity-audit-addendum.md) | reste-t-il d'autres mauvaises caractérisations ? | seconde passe, plusieurs formulations corrigées depuis |
| [Audit quantitatif](2026-07-19-related-work-quantitative-audit.md) | les nombres de l'état de l'art sont-ils exacts ? | trois corrections initiales et plusieurs statistiques à versionner |
| [Seconde passe quantitative](2026-07-19-related-work-quantitative-audit-second-pass.md) | existe-t-il d'autres chiffres trompeurs ? | contexte 3-shot et score cible désormais explicités |
| [Whitelist bibliographique](2026-07-19-bibcheck-whitelist-audit.md) | les exemptions de `checkbib` sont-elles sûres ? | non : la whitelist court-circuite le contrôle ; BioOntoBERT a depuis été réparé |
| [Similarité avec `exemples/`](2026-07-19-example-thesis-plagiarism-audit.md) | y a-t-il des reprises textuelles suspectes ? | aucun signal préoccupant |
| [Corrections TikZ](2026-07-19-knowledge-pretraining-tikz-change-report.md) | les schémas de préentraînement sont-ils fidèles et homogènes ? | corrections appliquées et rendu actuel cohérent |

## 4. Séquence de travail la plus efficace

1. Réparer le registre de données et décider quelles figures peuvent réellement rester finales.
2. Corriger les cinq contradictions/citations P0 visibles dès l'abstract, l'introduction et la conclusion.
3. Fermer les points OntoBook : split de sélection, p-values, fidélité des reformulations.
4. Borne le détour CLM et les revendications causales sans toucher aux résultats numériques.
5. Réconcilier les registres de la partie 3 et régénérer ses sorties à partir d'une source canonique.
6. Faire une dernière passe bibliographique hors whitelist, puis une compilation et une comparaison visuelle ciblée des pages modifiées.

## Conclusion

Le manuscrit n'a pas besoin d'une nouvelle campagne de réécriture générale. Une correction concentrée des P0, suivie du bornage des P1, éliminerait l'essentiel du risque de contestation. La force de la thèse — construire des extracteurs cliniques compacts à partir de ressources publiques et synthétiques — reste intacte ; ce sont surtout les frontières exactes de la preuve et la traçabilité de quelques résultats qui doivent devenir irréprochables.
