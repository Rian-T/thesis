- [ ] rajouter empreinte carbone modernv2 et section qui en parle bien
- [ ] rajouter tabib et idée tabib
- [ ] conclusion avec l'agentic
- [ ] rajouter gliner result silver labels

# Capstone lymphome / eCRF — audit du 2026-07-13

Dossier complet : `research/lymphome/` (gitignoré). Lire `00_INDEX.md` puis `01_AUDIT.md`.
**Aucun chiffre du capstone ne doit être écrit avant que les points 🚨 soient levés.**

## 🚨 Bloquants (rien ne s'écrit sans ça)

- [ ] 🚨 **Le classement s'inverse selon la règle de scoring.** Scorer principal : GLiNER 0.652 >
      Qwen 0.578. `paper/analyses.py` (autre règle de faux positifs) : **Qwen 0.666 > GLiNER 0.640**.
      → unifier en **un seul scorer**, une seule règle, sur les **410** dossiers, seuil choisi sur la
      validation (pas sur le test), décodage appliqué **aux trois familles**. Sans GPU.
- [ ] 🚨 **La table à 410 n'a aucun script producteur.** `paper/scores_410.py` lit en fait
      `v5_test_sub100.jsonl` (100 dossiers) et est identique à `build_thesis_scores.py`.
      → récupérer le vrai scorer sur Jean Zay.
- [ ] 🚨 **Table de décomposition du renversement** (brut / décodé × GLiNER, LLM, QA, une seule
      règle). Sans décodeur, **le LLM gagne** (0.578 vs ~0.44) : c'est le décodage qui renverse, pas
      l'architecture. C'est le vrai claim du chapitre, et il est plus fort. Sans GPU.
- [ ] 🚨 **« Le LLM ne peut pas s'abstenir » est un artefact** : `infer_llm.py:147` écrit
      `confidence: 1.0` en dur, aucun logprob demandé. → ré-inférer avec `logprobs=1` et recalculer
      l'AURC, ou **supprimer la section abstention**.

## Jean Zay (accès dans quelques heures)

- [ ] 🚨 **Rapatrier les parquets de prédictions.** C'est LA priorité : avec eux, tout le scoring se
      refait **en local, sans GPU** (c'est du post-traitement), et on ne croit plus aucun chiffre sur
      parole. Quelques Mo. Sous `/scratch/rtouchen/medembed-outputs/lymphome/` :
      ```
      preds_lym_*.parquet          # toutes les prédictions brutes (GLiNER, Qwen, QA)
      preds_lymRD_*.parquet        # les versions redécodées
      lymphome_train.jsonl         # nécessaire aux caps de cardinalité
      v5_test.jsonl                # vérifier qu'il fait bien 410 lignes
      v5_test_sub100.jsonl         # pour identifier quelle base a produit quel chiffre
      parhaf_exemplars.json        # les exemplars du bruit ancré (absents du repo)
      ```
- [ ] Récupérer **le code qui a produit la grille reconstruite**. Le repo n'a qu'un prototype
      (`regen_gold.py` : 20 dossiers, dossier entier tronqué à 20k, n'utilise jamais
      `focus_event_indices`). La carte HF parle d'une méthode « TAPDL » ancrée par compte-rendu qui
      n'existe **nulle part** dans le dépôt (ni dans les 37 commits de l'historique). Sans ce code, la
      section « reconstruire la grille » est inécrivable.
- [ ] Récupérer les **checkpoints GLiNER lymphome** (`gliner2-lym-V5base` / `V5large`). Ils ne sont
      **pas sur HF** (contrairement aux 4 adaptateurs LoRA Qwen et à tous les backbones) → sans eux,
      aucune ré-inférence côté encodeur n'est possible.
- [ ] Récupérer les scripts de scoring absents : les 410, le bruit, le cross-schéma,
      l'efficacité-données.
- [ ] Vérifier si les modèles d'ablation FULL / NO-CLINICAL sont vraiment perdus (sinon H3b revit).

## Sans GPU, dès que les parquets sont là

- [ ] **Trancher les chiffres qui coexistent** : meilleur honnête avant reconstruction (0.48 / 0.53 /
      0.533 ?), plafond oracle (0.90 / 0.85 ?), rappel de localisation (97 % / 29 % ?).
- [ ] **C2ST mots-fonction** : aucun script ne le calcule (les 0.858 / 0.901 publiés sortent de nulle
      part). À réécrire, et **corriger la fuite** : le TF-IDF est ajusté sur A+B avant la validation
      croisée.
- [ ] **Efficacité-données** : le jeu d'évaluation est inconnu (le point 1540 = 0.655 ne colle ni au
      100 ni au 410). À re-scorer sur la base unifiée.
- [ ] **A/B backbone** (+0.024) : re-scorer sur la base unifiée, il est aujourd'hui sur la base 100.

## Éric

- [ ] **Demander les détails de la relecture clinicienne.** Sa note (ch16_17 p.5) affirme que les
      dossiers ont été mis à disposition de médecins via un outil d'annotation web et jugés
      plausibles. **Aucune trace dans le repo.** Combien de dossiers ? Combien de médecins ? Quel
      outil ? Ne rien écrire avant sa réponse.

## Corrections de faits (à appliquer partout)

- [ ] **89 champs** (pas « about a hundred variables », pas 81). Sections : 6/7/11/13/6/15/12/2/12/5.
- [ ] Grille initiale : **25,7 %** de spans partagés et **38,9 %** de valeurs verbatim (recalculé sur
      le parquet). Les 14,4 % / 36,2 % / 15,1 % qui circulent sont **faux**.
- [ ] Défaut de `max_width` = **8 tokens** (pas 12), et 58 % des empans cibles le dépassent.
- [ ] Le cross-schéma reformule **89/89 descriptions et 0/89 libellés** → dire « descriptions », ou
      refaire le test en touchant aussi aux libellés.
- [ ] PARHAF : **4 254 patients / 6 185 documents** (pas « 4 254 comptes-rendus »), 104 internes.
      Et le papier **interdit** de s'en servir pour « stress-testing under realistic clinical
      conditions » → reformuler la phrase sur le bruit ancré.
- [ ] Bruit : clean tronqué à 30 000 caractères, bruité à 16 000 → les chutes mélangent bruit et
      troncature. À refaire à troncature constante.
- [ ] Seuil de confiance choisi **sur le test** dans les trois scorers → corriger ou déclarer.
- [ ] Chapitre du juge : réconcilier les chiffres thèse/repo (écarts 0.002–0.008) et l'intervalle de
      confiance recopié d'un autre run (+0.095 vs +0.097, même IC).
- [ ] Licence : PMC-Patients est en **CC BY-NC-SA 4.0**, `lymphome-synth-v5` est publié en **MIT**.
      Le *share-alike* se propage aux dérivés → à faire vérifier.

## Abstract (déjà poussé, commit dfc3cf2)

- [ ] Si Éric confirme que les médecins ont **annoté** (et pas seulement lu) les dossiers dans
      l'outil : passer `found them plausible overall` → `found them plausible enough to annotate`.
      Beaucoup plus fort : un dossier annotable contre 89 champs a passé un vrai test.
- [ ] La phrase « Transfer to real hospital records remains to be fully established » ne dit pas
      **pourquoi** c'est structurellement hors de portée (les dossiers qui trancheraient sont
      justement ceux qui ne sortent pas de l'hôpital). Sans ça, la limite se lit comme un travail
      inachevé au lieu d'être la prémisse de la thèse. → le dire dans la **conclusion**.

## À écrire (une fois les bloquants levés)

- [ ] Remplacer `tab:lymphoma-capstone` (0.174 / ~0.32) et les 3 paragraphes autour : périmés, ils
      disent l'inverse du vrai résultat.
- [ ] Décider : capstone en **chapitre séparé** (recommandé) ou section longue de `chap:evaluation`.
- [ ] Verser la matière négative jamais remontée : chaîne causale `max_width` (rappel atteignable
      42 % → 88 %), porte des négatifs (les négatifs **dégradent**, à rebours de la littérature),
      densité de supervision > volume, mur de la distillation, ablation données cliniques en
      différence-de-différences (effet global nul, mais lignes de traitement à 0.000 sans clinique).

# Relecture Éric (juillet 2026)

Extrait de 4 PDF annotés (`~/Downloads/thesis_chx.pdf`, `thesis_ch14.pdf`, `thesis_ch15.pdf`,
`thesis_ch16_17.pdf`). Pour chaque point, l'**ancre** est une citation exacte du corps du texte :
`grep -rF "<ancre>" sources/` pour retrouver l'endroit précis.

## Related Works (`thesis_chx.pdf`, p. 60-79)

- [ ] p.66 — « Could add an illustration of ontology »
      ancre : `A diagnosis, the procedures that treat it, and the drugs prescribed for it are recorded as concepts and links`
      → `sources/related_works/corpus_annotation.tex` (§ Pretraining Data: Corpora and Knowledge)
- [ ] p.73 — « Reference ? GLiNER »
      ancre : `Span-based NER takes a different view of the task` (§9.2.3 Beyond Token-Level Labeling)
      → `sources/related_works/clinical_ie.tex`
- [ ] p.74 — « Visit ? » (sur « a single stay » : parler de *visit* plutôt que *stay* ?)
      ancre : `Finally, a single stay is multi-label`
      → `sources/related_works/clinical_ie.tex`
- [ ] p.79 — « Adding ref to Simon's work ? and Riccardo ? »
      ancre : `models that use different tokenizers on a fair footing?` (fin du ch. Clinical IE)
      → `sources/related_works/clinical_ie.tex`

## Ch. Collecting Biomedical Text (`chap:collecting`, chx p. 85-88)

- [ ] p.85 — « could » (remplacer le *can*)
      ancre : `Hospitals produce millions of clinical documents every year. These can be used`
- [ ] p.88 — « Need some evaluation results in this chapter, with comparison with other models »
      (note générale de fin de chapitre)

## Ch. Detecting Content Types (`chap:quality`, chx p. 91-98)

- [ ] p.91 — « Reference to Table 11.1 » (la table n'est jamais citée dans le texte)
- [ ] p.94 — « Document or Paragraph type ? » — l'en-tête dit *Document* alors qu'on annote des paragraphes
      ancre : `By Document Type` (en-tête de groupe de la table)
- [ ] p.98 — « Performance of Llama-3-8B ? » (donner les perfs de l'annotateur)

## Ch. Which Quality Signals Matter? (`chap:mcbio`, chx p. 105-107)

- [ ] p.105 — « Tables ? » (mettre les 4 signaux de qualité dans une table)
      ancre : `The same LLM annotates each passage along four quality signals scored from 1 to 10`
- [ ] p.105 — « Add reference to these benchmarks »
      ancre : `(DiaMed, FrACCO-30, and EMEA, 9 seeds)`
- [ ] p.105 — « add an approximative equivalent in words ? » (sur les *tokens*)
      ancre : `Paragraphs shorter than 50 tokens are also excluded`
- [ ] p.106 — « Confusing Random (should add removal) » — la ligne *Random* de la table d'ablation
      de type de contenu prête à confusion, préciser qu'il s'agit d'un *retrait* aléatoire
      ancre : `Type removed` (en-tête de la table)

## Ch. Encoder Models for French Biomedicine (`chap:encoders`, chx p. 111-113)

- [ ] p.111 — « Peut-être bien de remettre ici la table détaillant biomed-fr et biomed-fr-small »
      ancre : `hours. We also identify the methodological differences that led to the contradic`
- [ ] p.113 — « Could add confidence interval if available, or signifiance » (table des résultats, près de `67.63 / 67.96`)
- [ ] p.113 — « At the same period ? » (sur « In a recent work », DrBERT est contemporain, pas postérieur)
      ancre : `In a recent work, Labrak et al. (2023) introduced a new French biomedical langua`

## Ch. CLM Detour (`chap:objectives`, `thesis_ch14.pdf`)

- [ ] p.2 — « Maybe develop here a little bit about MLM being not so token-efficient at training time with only 15% masking »
      ancre : `whether a temporary CLM phase leaves a useful trace after returning to MLM`
- [ ] p.4 — « Should rename T_CLM into Phase_{1,CLM}, T_MLM into Phase_{2,MLM15%} and another Phase_{1,MLM 30%} »
      ancre : `\omega_A = T_{MLM}(T_{CLM}(\omega_0, n), 0.1n)` (l'équation des deux trajectoires)
- [ ] p.4 — « Should be moved after the first results, because you are anticipating them ! »
      (déplacer la sous-section *freeze experiments*)
      ancre : `To test which layers carry the CLM benefit, we run three freeze experiments`
- [ ] p.4 — « References ? » (sur les jeux d'instructions)
      ancre : `plus MediFlow medical instructions`
- [ ] p.5 — « References, back ref to chapter ? » (protocole de fine-tuning)
      ancre : `Classification (DiaMED) and multilabel tasks (MedDialog, FrACCO, CAN-`
- [ ] p.5 — « multilabel classification task »
      ancre : `weighted BCEWithLogitsLoss; classification uses`
- [ ] p.9 — « Describe the freeze xp here » (§ CKA / analyse)
      ancre : `Why Does the CLM Detour Work?`

## Ch. OntoBook (`chap:ontobook`, `thesis_ch15.pdf`)

- [ ] p.3 — « Not the best place for this sentence, maybe better end of first paragraph of 15.3 »
      ancre : `Table 15.1 summarizes how OntoBook combines components not jointly present in prior work.`

## Ch. Données synthétiques + Architectures (`chap:synthetic` / `chap:architectures`, `thesis_ch16_17.pdf`)

- [ ] p.3 — « AI !? » (formulation à revoir)
      ancre : `Public case descriptions still read like published cases. They do not read like the terse notes a`
- [ ] p.3 — « Add form in appendix, and maybe examples of a few variables here » (le formulaire ~100 variables)
      ancre : `a form of about a hundred variables covering demographics, disease history, treatment lines`
- [ ] p.4 — « Provide an example » (l'identité/contexte institutionnel synthétique)
      ancre : `centre, an anchor year between 2015 and 2024, and a target document count between`
- [ ] p.5 — « Mention that the documents were available to doctors through a WEB-based annotation tool,
      and were globally perceived as plausible documents »
      ancre : `The data now exists. Whether a model can use it well is the question of the next chapter`
- [ ] p.7 — « Worth adding the schema from GLiNER paper »
      ancre : `This is the idea behind GLiNER (Zaratiana et al., 2024), which works by comparison.`
- [ ] p.11 — « Pour Solon, 44.9 in Table 17.2 !? » (incohérence de chiffre entre les deux tables)
      ancre : `Solon (baseline)`
- [ ] p.11 — « Out-of-Domain evaluation, zero-shot evaluation » (nommer explicitement les deux régimes)
      ancre : `A model that can extract a type it was never trained on is hard to measure.`