# Propositions de révision — annexes

Document de propositions uniquement. Aucun fichier TeX n'est modifié. L'ordre suit
le manuscrit et les vérifications Jean Zay du 5 août 2026.

## 0. Ouverture

### Paragraphe d'orientation

**Avant**

> These appendices collect the material that supports the chapters but would break
> their flow: training configurations and hyperparameter tables, annotation prompts
> and schemas, long worked examples, and evaluation type banks.

**Après**

> These appendices collect supporting material that would interrupt the chapters'
> flow, including training configurations, annotation prompts, worked examples, and
> evaluation details. Each appendix accompanies the chapter that refers to it.

## A. Content-Type Annotation and Classifiers

### A.1. Ouverture

**Après**

> This appendix documents the two content-type pipelines used in
> \Cref{chap:quality,chap:mcbio}. Both annotate paragraphs with a teacher model,
> distil the annotations into a compact classifier, and apply that classifier to a
> complete corpus. The Biomed-Enriched pipeline uses Llama-3.1-70B-Instruct, three
> annotation dimensions, and XLM-RoBERTa-base. The later biomed-fr-v2 pipeline uses
> MedGemma, a twenty-dimension schema, and CamemBERTv2-base.

### A.2. Annotation

**Problème.** Le renvoi vers \Cref{app:gliner-prompts} est faux. Cette annexe
contient le prompt d'extraction open-vocabulary, pas le prompt content-type.

**Après**

> Both pipelines annotate individual paragraphs together with their section title
> and path in the source document. Biomed-Enriched predicts document type, domain,
> and an educational score. The French pipeline returns twenty attributes, including
> a nine-class content type, one of 45 medical specialties, writing style, and
> quality indicators. Biomed-Enriched annotates approximately 400,000 paragraphs,
> and the French pipeline 433,915.

Ajouter le vrai prompt content-type ou supprimer l'affirmation qu'il est reproduit.

### A.3. Classifieur

**Note de version.** Le checkpoint actuellement présent sur Jean Zay déclare vingt
tâches de classification, alors que le manuscrit décrit dix têtes entraînées par
cross-entropy et dix par MSE. Le dépôt a continué d'évoluer après l'expérience.
Pour cette annexe, la configuration décrite dans le manuscrit fait foi ; l'état
actuel du checkpoint ne doit pas servir à la corriger rétrospectivement.

**Après**

> The annotations train a compact encoder with one prediction head per attribute.
> All heads share the encoder and its pooled \texttt{[CLS]} representation.
> \Cref{tab:ct-classifier} reports the retained checkpoint. On its held-out split,
> content-type accuracy reaches 0.84. Sex and interactive elements reach 0.98 and
> 0.996, while the 45-way medical-subfield task reaches 0.77.

**Proposition.** Conserver la répartition CE/MSE et les accuracies du manuscrit.
Ajouter seulement, si souhaité, une phrase indiquant que la table décrit la version
expérimentale utilisée dans la thèse, et non la dernière version du classifieur.

### A.4. Table

À conserver comme configuration de l'expérience décrite :

- 390,505 + 43,391 = 433,896, soit 19 exemples de moins que les 433,915 annoncés ;
- backbone, vingt têtes, 768 dimensions et vocabulaire 32,768 ;
- optimisation, batch, fp16 et seed tels que consignés dans le manuscrit.

Le seul point interne à éclaircir reste l'écart de 19 exemples entre le total annoncé
et la somme train/eval. Il ne dépend pas de l'état actuel du dépôt.

### A.5. Figure d'entraînement

**Après**

> \Cref{fig:ct-training} shows the training loss and learning-rate schedule, together
> with held-out accuracy for three attributes.

### A.6. Première itération

**Conserver.**

### A.7. Propagation

**Après**

> We serve the classifier with dynamic batching and apply it to every paragraph.
> Inference uses fp16, sequences of at most 512 tokens, and one node with eight A100
> GPUs. Applied to PubMed Central, the first pipeline labels 146 million paragraphs,
> including 2.12 million classified as clinical cases.

### A.8. Renvoi vers les expériences

**Conserver.**

### A.9. Implémentation

**Après**

> The propagation pipeline uses DataTrove to read PubMed Central Open Access XML and
> preserves the article identifier, licence, language, and document path for every
> paragraph. This provenance allows the non-commercial split to be distributed
> without redistributing its text. Gopher and FineWeb filters remain disabled during
> propagation; corpus variants apply filtering only after annotation.

## B. Pretraining Configurations for the CLM Detour

### B.1. Ouverture

**Après**

> This appendix reports the training configurations and supporting experiments for
> the CLM detour studied in \Cref{chap:objectives}. It covers French and English
> ModernBERT encoders at base and large scale, together with matched MLM baselines.

Retirer « full » tant que toutes les valeurs ne sont pas liées à un run figé.

### B.2. Architecture

**Après**

> The architecture follows the corresponding upstream ModernBERT checkpoint at each
> size~\citep{modernbert}. Continued pretraining changes the objective and data, not
> the encoder body. \Cref{tab:clm-arch} lists the retained settings.

Les YAML génériques actuellement présents sur Jean Zay ne correspondent pas
nécessairement aux runs historiques. Conserver les valeurs consignées dans le
manuscrit, sauf contradiction interne entre ses propres tables et son texte.

### B.3. Objectif

**Après**

> The two training routes use the same encoder body. During the detour, a causal
> mask and next-token head replace bidirectional masking. The MLM baseline instead
> masks 30\% of tokens. Both routes then return to bidirectional MLM with a 15\%
> masking rate. \Cref{tab:clm-obj} summarizes the phases.

### B.4. Optimisation

Conserver les budgets 10B/1B et 50B/5B, le batch 384, la longueur 8,192, le warmup
100M, le cooldown, les quatre H100 et le seed partagé tels qu'ils sont consignés.
Les fichiers actuels sur Jean Zay sont surtout des configurations upstream plus
récentes et ne permettent pas de reconstruire l'état historique.

### B.5. Recette par modèle

**Après**

> \Cref{tab:clm-permodel} gives the initial checkpoint, token budget, and data
> mixture for each language. The French mixture combines biomed-fr-v2 with medical
> question answering, E3C, and EMEA. The English mixture combines PubMed, medical
> instructions, and MIMIC notes.

Le chapitre distingue aussi un petit run anglais sans MIMIC. Ne pas présenter une
mixture unique comme valable pour tous les runs.

### B.6. Implémentation

**Après**

> Training uses Composer with the ModernBERT research code, FlashAttention 2, fused
> cross-entropy, and \texttt{torch.compile}. The causal phase changes the attention
> mask and disables the masking collator. The decay phase restores the bidirectional
> MLM head. Documents are packed into 8,192-token sequences, and checkpoints are
> exported in Hugging Face \texttt{ModernBertForMaskedLM} format.

Retirer « with mean pooling » de l'export : le pooling appartient à l'évaluation.

### B.7. Différence avec le from-scratch

**Après**

> Continued pretraining uses a lower learning rate and shorter warmup than
> from-scratch ModernBERT. The best decay length is approximately one tenth of the
> main phase: 1B tokens after 10B and 2.5B after 25B. Longer decay does not improve
> the result.
>
> One English run exceeded the cluster wall-time and resumed from its latest
> checkpoint without repeating the warmup.

### B.8. Temps et CKA

**Après**

> On four H100 GPUs, the recorded base and large runs take approximately 4.5 and
> 8 hours. At base scale, a 10B-token causal phase takes 3 h 25, compared with
> 3 h 11 for its masked counterpart. Representational analyses use float64 and mean
> pooling over held-out paragraphs; lower precision caused underflow in deep layers.

Conserver les chiffres consignés. L'anecdote de l'early miscount peut néanmoins être
retirée pour alléger le texte, indépendamment de sa provenance.

### B.9. Généralité

**Après**

> With CamemBERTv2-base, the detour improves the mean over eight French biomedical
> tasks by 1.48 points. Cybersecurity and finance means are positive but not
> statistically distinguishable across tasks. We therefore treat these domain
> extensions as directional rather than domain-wide gains.

### B.10. Explorations précédentes

**Après**

> Before changing the objective, we tested several modifications within MLM.
> Quality-weighted losses, filtering by individual quality signals, enriched data,
> long-range masking, and grounded ICD walks did not improve consistently over the
> masked baseline. These negative results motivated changing the objective rather
> than further reshaping the same loss.

### B.11. Supporting results

**CKA — après**

> \Cref{tab:cka-region} compares CLM--MLM divergence with a same-objective,
> different-seed control. The largest relative difference appears in the early
> layers, at 14.99\% against 1.57\%.

**Courbe par couche — conserver.**

**Needle — après**

> A needle-in-a-haystack test measures long-context retrieval end to end. The detour
> improves every tested context length and position, with the largest gain in the
> middle of the document.

**MIMIC — après**

> An English MIMIC-only run improves de-identification by 2.77 points, but its
> 0.56-point mean gain over eleven tasks is not statistically distinguishable.

## C. OntoBook Generation and Pretraining

### C.1. Ouverture

**Après**

> This appendix documents the generation and training configuration behind
> \Cref{chap:ontobook}. The released model uses French CIM-10; the same pipeline is
> evaluated with CCAM and ATC.

### C.2. Marches

**Après**

> We use French CIM-10, CCAM, and ATC RDF graphs. Biased random walks sample
> neighbouring concepts according to relation-specific weights. Walk length varies
> from 8 to 20 steps, cycles are avoided when possible, and outputs shorter than
> 300 characters are discarded. CIM-10 uses five walk templates; CCAM and ATC use
> three.

Conserver les volumes 402,328 / 762,958 / 138,980 consignés dans le manuscrit. Le
dépôt de génération a évolué ou n'est plus présent sous la même forme sur Jean Zay.

### C.3. Reformulation

**Après**

> Qwen3-235B-A22B-Instruct rewrites each walk as continuous prose. The prompt asks
> it to preserve every code, definition, note, inclusion, and exclusion without
> adding information. Walks longer than 12,000 characters are skipped. Outputs
> shorter than 50 characters or missing their source codes are discarded.

Vérifier « guided JSON » dans la table : il faut expliquer que la prose était
encapsulée dans un champ JSON, ou corriger le mode réel.

### C.4. Préentraînement

**Après**

> The released model continues from ModernCamemBERT with alternating MLM and
> relation-classification steps. MLM masks 15\% of tokens. The relation task receives
> two generated passages and predicts one of six CIM-10 relation classes. Code
> strings are removed to prevent leakage. The retained checkpoint uses equal loss
> weights and is selected after epoch 2.

Conserver les 282,907 paires et le checkpoint de l'époque 2. Seule la formulation
entre alternance des batches et somme des pertes mérite d'être clarifiée si le texte
laisse entendre que les deux pertes sont calculées sur le même batch.

### C.5. Implémentation

**Après**

> Training reuses the FlexBERT implementation of \Cref{app:clm-pretraining}. MLM
> examples use MosaicML Streaming format and relation pairs use Parquet. Relation
> labels are parsed from the raw walks before code strings are removed. The chapter
> also evaluates code infilling and a three-objective hierarchical variant.

## D. Annotation Prompts

### D.1. Ouverture

**Après**

> This appendix reproduces the prompt and output schema used to annotate the
> open-vocabulary extraction corpus of \Cref{sec:gliner-data}. The English text
> below translates the French production prompt.

### D.2. Schéma

**Problème bloquant.** La classe Field est utilisée mais jamais définie. Ajouter sa
définition exacte ou annoncer que le listing est un extrait. Ne pas inventer la
classe depuis le commentaire.

### D.3. Prompt

**Conserver sous réserve de fidélité.** Pour un prompt reproduit, la fidélité au
fichier de production prime sur le style. Ajouter modèle, version du prompt, mode
de décodage et run.

### D.4. Variante clinique

**Après**

> The clinical variant tells the annotator to preserve exact spans despite
> abbreviations, missing accents, and dictation errors. A separate noisy-text variant
> applies similar surface degradation before annotation.

Remplacer « draft variant », ambigu, par son nom réel.

## E. A Synthetic Lymphoma Dossier

### E.1. Ouverture

**Après si l'exemple est une vraie sortie**

> This appendix follows one synthetic case from its structured timeline to a
> generated French report and its eCRF annotations. The patient identity and clinical
> record are entirely fictional.

Sinon, nommer clairement l'annexe « Schematic Synthetic Lymphoma Dossier ».

### E.2. Timeline et document

**Conserver seulement après provenance.** Relier l'exemple à l'identifiant et au
fichier généré. Sans cela, il ressemble à un exemple écrit pour le manuscrit.

### E.3. Champs extraits

**Problème majeur.** La structure multi-valuée contredit le chapitre 17, qui garde
une valeur par patient et par champ. Elle mélange aussi valeur et evidence span.

**Après**

> For each eCRF field, the annotation stores a normalized value and the evidence span
> that supports it in the generated record. The source document and offsets locate
> that evidence in the longitudinal dossier. The example below shows a subset of the
> 89 fields.

Le listing doit suivre exactement : field, normalized value, evidence span, source
document et offsets. Sinon supprimer cette annexe plutôt que conserver une fausse
structure.

## F. Evaluation Type Bank and Hyperparameters

### F.1. Titre

**Problème majeur.** Cette annexe concerne le chapitre 16, pas le protocole eCRF du
chapitre 17.

**Titre proposé**

> Open-Vocabulary Evaluation Types and Training Settings

### F.2. Banque de types

**Avant**

> The reference-free evaluation of \Cref{chap:evaluation} scores [...] ten common
> clinical types [...] and ten novel types [...] which no benchmark uses.

**Après**

> The reference-free evaluation of \Cref{chap:architectures} uses two sets of ten
> descriptions. The first contains familiar biomedical entity types. The second was
> constructed to be absent from the evaluation benchmarks and is called
> \emph{benchmark-absent}. These descriptions may still occur in other training
> sources and do not establish transfer to entirely unseen concepts.

Renommer les colonnes « Familiar » et « Benchmark-absent ».

### F.3. Hyperparamètres

**Après**

> \Cref{tab:hparams} reports the retained training settings for MC-bio-embed and
> MC-bio-gliner.

Conserver med-embed v9, les 20k steps et les paramètres consignés dans le manuscrit.
Harmoniser seulement 149M contre 150M comme différence d'arrondi, préciser le nom
de la perte GLiNER2, et réserver le pooling mean + L2 à MC-bio-embed.

## G. TABIB Protocol Details and Sensitivity

### G.1. Version figée

**Note de version.** Le dépôt TABIB actuel a évolué vers deux suites, behavioral et
agentic, avec des dimensions et des jeux de données différents. L'annexe décrit la
version expérimentale antérieure évaluée dans la thèse. Les nombres du manuscrit
font foi et ne doivent pas être remplacés par ceux du dépôt actuel.

**Phrase facultative pour éviter l'ambiguïté**

> This appendix documents the version of TABIB evaluated in this thesis. The
> benchmark has since evolved; the protocols and results below refer to this earlier
> experimental version.

Il n'est pas nécessaire de retrouver un commit correspondant pour accepter les
résultats consignés dans le manuscrit.

### G.2. Ouverture

**Après**

> This appendix reports protocol details and decoding-temperature sensitivity for
> the version of TABIB evaluated in
> \Cref{sec:conclusion-evaluation}.

### G.3. Figures

**Après**

> \Cref{fig:conclusion-tabib-surface-distraction,
> fig:conclusion-tabib-cap-cal,fig:conclusion-tabib-cross-bias} report the individual
> results summarized by \Cref{fig:conclusion-tabib-radar}.

Les captions doivent nommer la métrique et son sens favorable.

### G.4. Pression

**Après**

> The adversarial-pressure protocol begins with a neutral turn, followed by ten
> increasingly forceful prompts in each of five registers. Two language-model judges
> classify every response as \textsc{maintain}, \textsc{hedge}, \textsc{deflect}, or
> \textsc{capitulate}, and independently mark unsafe advice. Agreement ranges from
> $\kappa=0.36$ for MedGemma 1.5 to 0.76 for Ministral-3.

Mettre les valeurs intermédiaires dans une table ou une note.

### G.5. Triage

**Après**

> The comparative-triage protocol starts from 900 French biomedical articles
> selected for clinical content. A language model rewrites them as short notes with
> placeholders for identity, address, and coverage. Combining notes and profiles
> produces 14,400 instances; the reported experiment uses a fixed subset of 100
> cases.

Conserver le modèle, le prompt, le seed et la règle de sélection tels qu'ils sont
consignés pour cette version, lorsqu'ils sont disponibles dans le manuscrit.

### G.6. Température

**Après**

> Tables [...] compare deterministic decoding with the temperature recommended by
> each model card. The sign of the main aggregate effects is generally unchanged,
> although several model-level magnitudes differ.

Ne pas écrire globalement « directions remain stable » sans définition : certains
flip rates B1 changent fortement.

### G.7. Tables B1–B5

À corriger :

- définir DCI, Brand, Flip et T=mc ;
- préciser que les deltas B2 sont context minus direct ;
- ordonner B1, B2, B3, B4, B5 ;
- expliquer l'absence éventuelle de B3 ;
- donner le nombre d'exemples par cellule ;
- conserver les valeurs de la version expérimentale rapportée dans le manuscrit.

## Priorités

1. Corriger le faux renvoi content-type vers les prompts GLiNER.
2. Aligner le dossier lymphome sur field / value / evidence span.
3. Rattacher la type bank au chapitre 16 et la renommer benchmark-absent.
4. Présenter clairement TABIB et le classifieur comme les versions évaluées dans la
   thèse, distinctes de leurs versions actuelles.
5. Appliquer ensuite les changements de prose et compiler les annexes.
