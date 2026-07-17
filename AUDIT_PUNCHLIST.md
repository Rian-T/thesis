# Punch-list consolidée — reste-à-faire thèse (audit 2026-07-16)

Sources fusionnées : **TODO.md** (relecture Éric, autoritaire) · **audit Sonnet** (19 chapitres + cohérence globale) · **fable appendix** · scan mécanique.
Verdict audit : **1 major-gap (Ch6), 18 needs-pass, 0 stub, 0 autre papier-collé**. Arc narratif OK, questions de recherche posées et répondues.

---

## A. Bloquants / structurels

- [ ] **Ch6 OntoBook — thesis-ifier** (`part_2/chapter6/article.tex`, *major-gap*) : intro = abstract du papier (« We propose… We evaluate… We release ») → réécrire en hook ; conclusion « **We presented** OntoBook… » + `\section{Conclusion}` → clôture-insight + `\section*{Conclusion}` ; 3 TODO (l.9-11 : tables→thesis-style, hook, `\Cref`).
- [ ] **Conclusion (TABIB + agentic) jamais annoncée** dans l'intro/contributions (*global gap*) → ajouter un forward-ref (8e contribution « exploratoire » dans `contributions.tex`, ou une phrase de fin). Cf. Éric l.2 « rajouter tabib et idée tabib ».
- [ ] **Abstract sur-claim** (`abstract.tex` l.12) : « outperforms … a fine-tuned nine-billion-parameter LLM » — pas étayé par test de signif dans le corps, et le CLAUDE.md dit « quasi-parité, within 0.018 ». → étayer (comparaison 9B + signif) **ou** adoucir. Recoupe les notes abstract d'Éric (l.89-97).
- [ ] **Capstone — intégrité data (Éric 🚨, l.11-58)** : inversion du classement selon scorer, scripts producteurs manquants, « le LLM ne peut pas s'abstenir » = artefact (`confidence:1.0` en dur). ⚠️ *partiellement levé* (CLAUDE.md : chiffres « vérifiés depuis les parquets ») → **confirmer point par point** avant d'écrire un chiffre.

## B. Corrections de faits (Éric — appliquer PARTOUT, l.70-87)

- [ ] **89 champs** (pas « ~100 », pas 81).
- [ ] Grille : **25,7 %** spans partagés / **38,9 %** verbatim (les 14,4/36,2/15,1 sont faux).
- [ ] `max_width` défaut = **8 tokens** (pas 12) ; 58 % des empans dépassent.
- [ ] **Seuil de confiance choisi sur le test** dans les 3 scorers → corriger ou déclarer.
- [ ] PARHAF : **4 254 patients / 6 185 docs** (pas 4 254 CR) ; le papier **interdit** l'usage « stress-testing ».
- [ ] Cross-schéma : **89/89 descriptions, 0/89 libellés** → dire « descriptions ».
- [ ] Licences : PMC-Patients **CC BY-NC-SA** (share-alike se propage) vs lymphome-synth **MIT** → vérifier.
- [ ] Bruit : clean 30 000 car. / bruité 16 000 → mélange bruit+troncature, refaire à troncature constante.

## C. Citations manquantes (audit)

- [ ] « **30 M séjours/an** » PMSI : `chapter6` l.76 + `clinical_ie` l.25 et 182 → citer ATIH/PMSI.
- [ ] BioBERT **18 Md mots** (`chapter1`, §corpora) → `\citep{lee_biobert_2019}`.
- [ ] Gain PubMedBERT vs BioBERT (`chapter1` l.140) → citer Gu et al. ou donner le chiffre.
- [ ] Tailles d'espaces de codes **17 000 ICD-10 / 8 000 CCAM / 6 000 ATC** (`clinical_ie` §The Problem) → citer.
- [ ] **AliBERT** (`chapter4`, Table 4.4 carbone) jamais cité/introduit → `\citep{...}` + une glose.
- [ ] **biomed-fr 413 M mots** (`contemporary_ai` l.44) → `\Cref{chap:collecting}`.
- [ ] Split « échocardiographie »→écho/cardi/ographie (`language_modeling` §Domain Mismatch) → soit rouler le vrai tokenizer et citer, soit marquer « illustratif ».

## D. Narratif / front matter

- [ ] **Clear les `reviewrewrite`** (rendus « à polir ») : `introduction` (12), `contemporary_ai` (9), `conclusion` (6), `contributions` (4) → relecture finale puis retirer le wrapper.
- [ ] `contributions.tex` l.34-36 : nommer les parties via `\Cref{part:...}` au lieu de « the first part… ».
- [ ] `language_modeling.tex` : adoucir le forward-ref Ch5 (« lasting and useful mark » → question ouverte, cohérent avec le vrai résultat CLM).
- [ ] `corpus_annotation.tex` §Limits and Transition : ouvrir sur le problème, supprimer les 2 phrases de recap « This chapter examined… ».

## E. Sweep style (rapides)

- [ ] **Antithèse « not X but Y »** (interdite §7) : `clinical.tex` l.76 · `web.tex` l.163 · `chapter2` l.152 · `chapter3` l.204.
- [ ] **Captions >1 phrase** : `chapter6` (~8) · `language_modeling` (~9) · `conclusion` fig carbone l.74 · `introduction` (2) · `contemporary_ai` (3 phrases) · `scientific`/autres ponctuels.
- [ ] `chapter2` : 4 exemples **placeholder** (TODO l.77/96/149/198 : vrai extrait PMC, exemple clinique/scientifique, prompt d'annotation en appendix) → fournir ou couper la promesse.
- [ ] `chapter3` intro l.37 : liste « contributions (1)(2)(3) » → prose.
- [ ] `chapter8` : `fig:p3-section-supervision` encore **flottante** (dérive p.157) → non-float `\begin{center}…\captionof…` comme les 3 autres figs du chapitre (idem fix 16.3/16.5).
- [ ] `scientific.tex` l.137 : phrase Friedman **commentée** au milieu d'un paragraphe → restaurer ou supprimer le commentaire mort.
- [ ] `clinical.tex` l.159/173 : « (Figure 1) » hérité de la source, pointe dans le vide → « (Figure 1, non reproduite) » ou retirer.

## F. Appendix (fable)

- [ ] **6 annexes orphelines** → ajouter `\Cref{app:...}` au bon ancrage dans le **corps** : `chap:quality`/`chap:mcbio`→content-types ; `chap:objectives`→clm-pretraining ; `chap:ontobook`→ontobook-details ; `sec:gliner-data`→gliner-prompts ; `sec:lymphoma-dossiers`→lymphoma-dossier ; `chap:evaluation`→eval-details.
- [ ] Ch F (Evaluation Type Bank) : ajouter une phrase d'intro (rompt le parallélisme).
- [ ] Mineurs : « differs from *from*-scratch » l.246 · « *not only* in tokens » l.258 · `\ref`→`\Cref` l.842 · ordre tables **B1/B2/B4/B5** · 4 listings qui ouvrent à froid.

## G. Éric — points annotés par chapitre (ancres grep dans TODO.md l.109-203)

- [ ] **RW** : réf GLiNER (`Span-based NER takes a different view`) · *visit* vs *stay* (`a single stay is multi-label`) · réfs Simon/Riccardo (fin Clinical IE).
- [ ] **Collecting** : `can`→`could` (l.85) · besoin de **résultats d'éval + comparaison** dans le chapitre (note de fin).
- [ ] **Detecting Content Types** : citer Table 11.1 dans le texte · en-tête « *Document* » → *Paragraph* · perfs **Llama-3-8B** (annotateur).
- [ ] **Which Quality Signals** : mettre les 4 signaux en **table** · réfs DiaMed/FrACCO-30/EMEA · équivalent en mots des tokens · « Random » → préciser *removal*.
- [ ] **Encoders** : remettre la table biomed-fr/-small · IC/significativité (près de 67.63/67.96) · DrBERT « at the same period » (contemporain, pas postérieur).
- [ ] **CLM Detour** : MLM peu token-efficient (15 % masking) · renommer `T_CLM`→`Phase_{1,CLM}`, `T_MLM`→`Phase_{2,MLM15%}` · **déplacer la sous-section freeze APRÈS les résultats** · réfs (MediFlow, jeux d'instructions) · décrire l'xp freeze dans §CKA.
- [ ] **OntoBook** : déplacer la phrase « Table 15.1 summarizes… » (fin 1er §de 15.3).
- [ ] **Synthétique/Archi** : « AI !? » à reformuler (`Public case descriptions still read like published cases`) · **formulaire eCRF en appendix** + qq exemples de variables · exemple d'identité synthétique · mention outil d'annotation web médecins · **schéma GLiNER** (papier) · **Solon 44.9 incohérent** entre Table 17.2 et l'autre · nommer explicitement « out-of-domain / zero-shot ».

---

## Déjà fait ✅ (cette session / avant)

- **Illustration d'ontologie** (Éric p.66) = les 4 figures knowledge-graphs RW.
- **Carbone modernv2** (Fig 19.2), **TABIB** (Ch20), **conclusion agentique** (Ch21) — Éric l.1-3.
- Fig 21.1 refaite lisible ; Table 20.3 capitulation → heatmap ; nommage versionné TABIB ; flottants 16.3/16.5 ; polish visuel Part 3.

## Estimation grossière

- **Ch6 thesis-ification** : ~½ j (le seul vrai chantier de rédaction).
- **Corrections de faits + citations (B, C)** : ~½ j, mécanique mais critique soutenance.
- **Front matter reviewrewrite + sweep style (D, E)** : ~1 j de relecture.
- **Appendix back-refs (F)** : ~2-3 h.
- **Points Éric par chapitre (G)** : ~1 j, beaucoup de petits.
- **Capstone data (A/B)** : dépend de Jean Zay, hors-rédaction.
