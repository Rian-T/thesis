# Propositions de révision — partie IV et conclusion

Ce document ne modifie pas les fichiers TeX. Il suit le manuscrit dans son ordre
et donne un avant/après pour chaque changement proposé. « Conserver » signifie
qu'une réécriture ferait surtout bouger les mots.

## Chapitre 17 — Evaluating Open-Vocabulary Extraction

### 1. Ouverture

**Avant**

> The previous chapters constructed synthetic supervision and used it to train an
> open-vocabulary extractor. We now evaluate this extractor on complete form
> filling. Lymphoma serves as the case study for this final part of the thesis.

**Après**

> The previous chapters trained an open-vocabulary extractor to identify individual
> spans. We now ask whether it can fill a complete form from everything written
> about one patient. Lymphoma provides the case study for this final part of the
> thesis.

### 2. Origine de l'eCRF

**Avant**

> Its eCRF covers ten sections, including disease history, two treatment lines,
> imaging, and patient status.

**Après**

> Its eCRF contains the 89 variables selected for the lymphoma use case of the
> OncoLab programme. They cover ten sections, including disease history, two
> treatment lines, imaging, and patient status.

### 3. Aperçu du formulaire

**Conserver.**

> The full form is larger than this two-field example. \Cref{fig:p3-form-preview}
> shows a small extract from three of its sections.

### 4. Partition et sorties

**Avant**

> The synthetic corpus is split into 1,540 training records, 100 validation
> records, and 410 test records. No record is a hospital document. Extractive
> systems score local span--description pairs, while generative systems produce
> all requested fields jointly.

**Après**

> The synthetic corpus contains 1,540 training records, 100 validation records,
> and 410 test records. None is a hospital record.
>
> The compared systems fill the form differently. Extractive models score local
> span--field pairs, whereas generative models return all requested fields in one
> structured output.

### 5. Unité de prédiction

**Avant**

> The eCRF keeps one value per record and field: the prediction with the highest
> confidence. A wrong value contributes one false positive and one false negative.
> PARHAF and the FRACCO NER dataset remain multi-mention tasks [...]

**Après**

> The eCRF keeps one prediction per field and patient record. When a model proposes
> several values for the same field, we retain the most confident one. PARHAF and
> FRACCO remain multi-mention NER tasks, where all predictions are matched greedily
> by decreasing confidence. \Cref{fig:p3-metrics,tab:p3-metrics} summarize the two
> evaluation regimes.

### 6. Métriques et seuils

**Diagnostic.** Le renvoi vers \Cref{app:eval-details} est faux : cette annexe
décrit la banque de types du chapitre précédent.

**Avant**

> The evaluation type bank and the training settings are given in
> \Cref{app:eval-details}. We report three eCRF metrics. [...] Generative models
> return values directly and need no threshold.

**Après**

> We report three eCRF metrics. Span-$F_1$ accepts any overlap between the predicted
> and reference evidence spans. Value-$F_1$ compares the normalized token sets of
> the predicted and reference values and requires a Jaccard similarity of at least
> 0.5. This allows harmless differences in formatting between copied spans and
> generated values. Exact match is stricter and requires both the value and its
> evidence span to be correct. All three metrics measure surface agreement rather
> than clinical equivalence.
>
> Extractive models assign a confidence to each prediction. We select one decision
> threshold per model on the 100 validation records and apply it once to the test
> set. Generative models return values directly and require no threshold. For the
> main comparisons, we compute paired confidence intervals over the 410 test
> records.

### 7. Résultats bruts

**Diagnostic.** La référence vient de Qwen3-235B et les comparateurs de Qwen3.5 :
il s'agit d'une lignée commune, pas du même modèle.

**Avant**

> We compare six extractive systems with four sizes from the same generative model
> family. [...] The reference [...] is produced by the same model family [...]

**Après**

> We compare question-answering encoders, open-vocabulary extractors, and four
> Qwen3.5 generators. Their objectives and output formats differ, so this is not a
> controlled scaling experiment. The reference is the silver eCRF produced with
> Qwen3-235B in \Cref{chap:synthetic}. Its shared lineage with the generators may
> favour common conventions, and the comparison measures agreement with a generated
> reference rather than clinical accuracy.
>
> Before competition between fields, Qwen3.5-4B obtains the highest value-$F_1$ at
> 0.672. Increasing the generator to nine billion parameters does not improve this
> score. The released 150-million-parameter MC-bio-gliner reaches 0.634, and the
> joint-supervision variant reaches 0.650. Their gaps to Qwen3.5-4B are 0.038 and
> 0.022, respectively.

### 8. Compétition entre champs

**Avant**

> Strongly overlapping candidates compete, the most confident assignment is
> retained, and each field keeps one final value.

**Après**

> An extractive model scores each span--field pair locally, so the same passage may
> be assigned to several fields. We first keep the most confident prediction for
> each field. Predictions whose evidence spans have an intersection over union
> above 0.5 then compete, and only the most confident field assignment is retained.
> This rule resolves duplicate assignments but cannot repair a medically incorrect
> prediction.

### 9. Effet de la compétition

**Après**

> Field competition improves every extractive system. For the released
> MC-bio-gliner, value-$F_1$ rises from 0.634 to 0.640. Generators already produce
> the fields jointly in a constrained JSON object, so imposing the same rule is not
> part of their natural decoding. For Qwen3.5-9B, it reduces value-$F_1$ from 0.665
> to 0.650, a paired change of $-0.0153$ (95\% CI $[-0.0176, -0.0129]$).

### 10. Figure d'exemple

**Avant**

> \Cref{fig:p3-field-competition-example} illustrates the operation on one
> candidate span.

**Après**

> \Cref{fig:p3-field-competition-example} gives a schematic example of this
> operation.

Si l'exemple « BCL2 positive » reste, retirer les confiances exactes 0.79/0.42 :
elles viennent d'un exemple réel différent.

### 11. Comparaison principale

**Après**

> After competition, the released MC-bio-gliner reaches 0.640, within 0.018 of
> Qwen3.5-4B at 0.658 (95\% CI $[-0.0243, -0.0108]$). The joint-supervision
> variant reaches 0.657. Its paired difference from Qwen3.5-4B is $-0.0005$
> (95\% CI $[-0.0075, 0.0072]$), which does not distinguish the two systems.
> \Cref{fig:p3-money} places the models on the parameter axis, and
> \Cref{tab:p3-capstone} reports their final scores.

Ajouter la variante jointe à la table. Son exact match n'est pas enregistré dans
le handoff actuel : ne pas l'inventer.

### 12. Après la table

**Avant**

> Scaling the encoder further is a direction we could explore. [...]
>
> The ranking does not depend on the decoding step. [...]

**Après**

> Qwen3.5-4B retains an advantage on span-$F_1$, at 0.567 against 0.503 for the
> released MC-bio-gliner. The comparison nevertheless gives the same overall result
> before and after field competition: the compact extractor approaches the strongest
> generator on value-$F_1$, while the generator locates the supporting spans more
> accurately.

### 13. Erreurs et confiance

**Après**

> Value-$F_1$ does not show whether a model found the wrong value or placed the
> right value in the wrong field. Among their errors, wrong-field assignments
> account for 48.9\% for MC-bio-gliner and 38.8\% for Qwen3.5-4B. The encoder
> therefore makes more role confusions, where a correct string is assigned to the
> wrong part of the form.
>
> We also evaluate how well each model ranks its predictions by confidence. This
> analysis includes every committed prediction, including the low-confidence tail
> removed by the operating threshold. Qwen3.5-4B obtains a lower risk--coverage
> area, 0.207 against 0.239, and a higher precision at 50\% coverage, 0.828 against
> 0.770. MC-bio-gliner fills more fields but assigns high confidence less reliably.

Les taux 48.9\% et 38.8\% doivent recevoir une dérivation enregistrée avant de
rester dans le manuscrit.

### 14. Mémoire

**Après**

> MC-bio-gliner has a clear advantage in weight memory. In bfloat16, 150 million
> parameters require about 0.3 GB, compared with roughly 8 GB for Qwen3.5-4B and
> 18 GB for Qwen3.5-9B. These figures exclude activations and runtime overhead.
> Fewer parameters also do not imply lower end-to-end latency here, because the
> encoder must query all 89 field descriptions.

### 15. Baseline QA

**Après**

> The question-answering baseline is weaker for a structural reason. Its SQuAD-style
> head returns one main span per question, whereas a longitudinal record may contain
> several mentions and surface forms of the same value. Training on only the first
> mention discards this multiplicity. This mismatch helps explain why the biomedical
> QA encoder reaches 0.417 value-$F_1$, below the description-conditioned models.

Retirer le paragraphe isolé sur les 72.4\% de confiances identiques dans PARHAF.

### 16. Efficacité en données

**Après**

> We first measure how much generated supervision the extractor needs. A separate
> low-density variant is adapted with 10, 50, 100, 500, and 1,540 synthetic records;
> it is not the joint-supervision model in the main comparison. Value-$F_1$ rises
> from 0.182 with 10 records to 0.485 with 50 and 0.659 with the full training set.
> Fifty generated records therefore provide 74\% of the final score, although
> performance continues to improve with more data. This experiment does not
> estimate the value of equivalent human annotation.

### 17. Transfert externe

**Après**

> We next test transfer beyond the generated lymphoma records on the human-written
> PARHAF and FRACCO datasets. These remain NER benchmarks, not private hospital
> records or complete form-filling tasks. PARHAF contains two biomarker types and
> only 31 test documents, so small score differences are unstable. FRACCO contains
> three ICD-O types and about 34 mentions per document, making it a much denser NER
> task.

Retirer la phrase sur les 0.2\%, qui décrit une ablation non montrée.

### 18. Résultats externes

**Après**

> With 100 adaptation documents, MC-bio-gliner reaches 0.681 on PARHAF, compared
> with 0.562 for the size-matched GLiNER-BioMed. The Qwen3.5 generators remain
> higher, but the 31-document test set is too small to support a stable ranking.
>
> FRACCO reverses the comparison between the two extractors. GLiNER-BioMed reaches
> 0.762 after adaptation, compared with 0.626 for MC-bio-gliner. The advantage of
> MC-bio-gliner therefore does not extend to this dense, flat NER task. Its main
> result remains the longitudinal form-filling task for which it was designed.

### 19. Limites

**Après**

> The main evaluation uses generated records and a silver reference produced by
> Qwen3-235B. Shared conventions between generation, annotation, and the Qwen3.5
> comparators may affect the ranking. The experiment also covers one disease and
> one predefined form. PARHAF and FRACCO add human-annotated evidence, but only for
> narrower NER tasks. Full form filling must still be evaluated on private hospital
> records with clinical annotation before any use in practice.

### 20. Conclusion du chapitre

**Après**

> On the synthetic lymphoma eCRF, the released 150-million-parameter MC-bio-gliner
> comes within 0.018 value-$F_1$ of Qwen3.5-4B, and the joint-supervision variant
> reaches the same level. The compact model uses much less weight memory, but the
> generator remains stronger at locating evidence spans and ranking predictions by
> confidence. Transfer to PARHAF and FRACCO further shows that the comparison depends
> on the extraction task.
>
> The remaining question is no longer whether the form can be filled in this
> synthetic setting, but whether the same result survives contact with private
> hospital records.

### Provenance à régler

1. Jean Zay donne 0.640 pour le checkpoint publié ; le script actuel donne 0.6437.
2. Les taux 48.9\% et 38.8\% doivent être enregistrés proprement.
3. Les valeurs d'efficacité en données sont encore décrites comme transcrites du
   dashboard.
4. Le script local externe pointe vers d'anciens artefacts GLiNER-BioMed.

## Conclusion générale — passage paragraphe par paragraphe

### 1. Phrase d'ouverture

**Conserver.**

> Let's not get too excited. Building the models is the easy part.

### 2. Trajet de la thèse

**Avant :** la succession de « We » donne un léger effet de liste.

**Après**

> Hospital notes are the target throughout this thesis, but none of the models is
> trained on a real patient record. The route instead begins with public scientific
> articles, drug leaflets, medical ontologies, and published clinical cases. These
> sources are filtered into a biomedical corpus
> (\Cref{chap:collecting,chap:quality,chap:mcbio}), used to pretrain an encoder
> (\Cref{chap:encoders,chap:objectives}), and supplemented with knowledge from
> medical ontologies (\Cref{chap:ontobook}). The resulting model learns to extract
> fields described at inference time (\Cref{chap:architectures}) and finally fills
> the clinical form of a study (\Cref{chap:evaluation}).

### 3. Annonce des économies

**Conserver.** La table porte déjà le détail.

### 4. Données et carbone

**Avant :** le paragraphe réunit trois échelles de comparaison.

**Après**

> Paragraph-level filtering matches the performance of the complete corpus with one
> third of its tokens. The clinical filtering recipe reaches the same point with
> 2.5 times fewer tokens (\Cref{chap:quality}).
>
> Continual pretraining produces a similar reduction in training carbon.
> CamemBERT-bio emits an estimated 0.80 kg CO\textsubscript{2}eq, compared with
> 26.11 kg for DrBERT and 8.16 kg for AliBERT. Across the recent complete
> pipelines, ModernCamemBERT-bio-v2 emits an estimated 17 kg, compared with 169 kg
> for the from-scratch DoctoModernBERT.

### 5. Où le budget est dépensé

**Après**

> The budget is not spent where one might expect. Continual pretraining the encoder
> takes about 16 GPU-hours, compared with roughly 383 for training one from scratch.
> Most of the recent pipelines' cost comes instead from the language model used to
> rewrite and annotate the corpus. Our pipeline remains lighter because it curates
> a small biomedical corpus rather than rephrasing a web-scale one. These estimates
> use reserved GPU-hours and the French grid intensity of 34 g
> CO\textsubscript{2}eq per kWh; they are not hardware-level energy measurements.

### 6. Coût à l'inférence

**Après**

> The extractor also reduces weight memory at inference. MC-bio-gliner has 150
> million parameters and reaches 0.640 value-$F_1$, within 0.018 of Qwen3.5-4B
> with twenty-seven times more parameters. In bfloat16, their weights require about
> 0.3 and 8 GB, respectively. This excludes runtime memory and does not imply lower
> latency, but it makes the compact model easier to fit on hospital hardware.

### 7. Corpus utilisé deux fois

**Après**

> Biomed-Enriched served twice. Its paragraph-level filtering reduced the training
> corpus to one third of its tokens. The same process identified about two million
> published clinical cases. After filtering for quality and relevance to lymphoma,
> these cases became the seeds of the synthetic longitudinal records used in the
> final task (\Cref{chap:synthetic}).

### 8. Pas encore l'hôpital

**Après**

> None of this is ready for a hospital ward. The realism of the synthetic records
> was discussed informally with clinicians from French university hospitals (CHUs),
> not established through a clinical study. Real records would bring messier text
> and stricter checks. These results show how far public and generated data can
> support the task before a real record is needed. They do not show how the models
> behave once put to use.

### 9. Ouverture de « A New Problem »

**Conserver.** Le changement de question est explicite en trois phrases.

### 10. Une autre direction du champ

**Après**

> The methods in this thesis favour small encoders trained at low compute and carbon
> cost. Clinical deployment is also exploring a different path. Hospitals can run
> large general-purpose models locally so that patient data remain within the
> institution. Reports of on-premise deployment suggest that privacy can motivate
> this choice independently of efficiency. A single general model may also cover
> tasks for which separate encoders need separate adaptation. Efficiency remains a
> defensible objective, but it is not the only direction clinical NLP is taking.

Conserver ici les deux exemples et citations de la version actuelle.

### 11. Limites des benchmarks factuels

**Après**

> Fine-tuned encoders usually produce one prediction for one fixed input. Generative
> models are used through prompts and interactions, where wording, context, decoding,
> and pressure over several turns may change the answer. Most medical benchmarks
> test factual knowledge through clean questions; HealthBench and CARES add broader
> tests of safety and refusal. They still do not systematically test whether a model
> preserves the same behaviour when an unchanged medical fact appears inside a
> prescription, a long note, a patient's insistence, or a triage list.

### 12. Lien réglementaire

**Conserver.** Il apporte une justification distincte et mène à la mesure directe.

### 13. Définition de TABIB

**Après**

> TABIB (\textit{Testing Adversarial Behaviors In Biomedical LLMs}) is a preliminary
> benchmark of French biomedical models under changes to the interaction that leave
> the medical fact unchanged. It draws drug interactions from the ANSM thesaurus
> and commercial names from the BDPM. TABIB includes 68 interaction pairs whose
> substances are both sold as active products, 200 additional contraindications for
> calibration, and negative controls for protocols that must distinguish detection
> from over-reporting.

### 14. Panel de modèles

**Après**

> TABIB evaluates seven open-weight models small enough to run locally, from two to
> nine billion parameters (\Cref{tab:conclusion-tabib-models}). MedGemma 1.5 is the
> only medically specialized model. We report the main results at temperature 0 and
> repeat sampling-sensitive protocols at the temperatures recommended by the model
> cards. The direction of the effects remains unchanged; \Cref{app:tabib-details}
> gives the full protocols and sensitivity analysis.

### 15. Sept protocoles

**Après :** scinder en deux paragraphes.

> Four protocols test whether an unchanged drug interaction receives a stable
> answer. Surface robustness replaces generic drug names with brand names. Contextual
> distraction embeds the same pair in a clinical note. Cross-lingual consistency
> compares French and English prompts, while adversarial capitulation follows an
> eleven-turn conversation under five forms of patient pressure.
>
> Two further protocols test confidence and prudence across the four ANSM severity
> levels. The final protocol tests comparative triage by permuting five social
> profiles across the same clinical cases. \Cref{tab:conclusion-tabib-profiles}
> lists these profiles.

Conserver les citations et les définitions d'Alan et de CSS de la version actuelle.

### 16. Vue d'ensemble des échecs

**Après**

> No model remains stable across all seven protocols. Each perturbation preserves
> the medical fact but changes the form or context of the interaction. The resulting
> failures therefore concern behaviour rather than missing factual knowledge.

### 17. Noms génériques et commerciaux

**Après**

> Surface form already changes the answers. Replacing generic names with brand names
> reduces accuracy by 38 points for Gemma4 E4B and 9 points for Qwen3.5 4B. Other
> models change in both directions, so a stable mean can hide unstable decisions.

### 18. Contexte clinique

**Conserver.** Les trois comportements sont concrets et bien distingués.

### 19. Pression conversationnelle

**Après**

> Multi-turn conversation creates another failure mode without changing the medical
> content. Under patient pressure, five models give unsafe advice in 12 to 28\% of
> conversations. The largest effect comes from a role-play prompt asking the model
> to act as an unconstrained caregiver. Unsafe advice then reaches 60\% for
> Ministral-3 and 55\% for Qwen3.5-4B. MedGemma remains at zero by deflecting 61\%
> of turns rather than engaging with the request.

### 20. Confiance et prudence

**Après :** séparer les deux phénomènes.

> Reported confidence is also unreliable. Nemotron has the highest expected
> calibration error at 0.693. MedGemma obtains the lowest, 0.132, largely by
> answering ``no'' to 99\% of pairs. Its apparent calibration therefore reflects
> non-engagement rather than useful confidence estimates.
>
> Prudence across severity levels fails separately. Gemma4 E2B is maximally cautious
> almost everywhere, while MedGemma remains uniformly direct. Neither helps a
> clinician distinguish an absolute contraindication from a minor precaution.

### 21. Français contre anglais

**Conserver avec une coupe :** retirer « larger factual knowledge does not buy that
consistency », qui n'est pas directement démontré par cette expérience.

### 22. Triage comparatif

**Après :** scinder le résultat général et les profils extrêmes.

> Every model changes its triage order when social profiles are permuted across the
> same five clinical cases. None reaches Kendall's $\tau > 0.6$. MedGemma is the
> least stable at $\tau = 0.07$, followed by Nemotron at 0.17.
>
> Four models rank the ``Jean Dupont'' profile first. MedGemma and Nemotron rank
> ``Fatou Diallo'' last, with mean ranks of 4.77 and 4.85 out of 5. Yet scoring one
> patient at a time gives profile differences below 0.03. The effect appears when
> patients are compared, as they would be in a triage list.

### 23. Deux enseignements

**Après**

> Two conclusions follow. Medical specialization alone does not guarantee safer
> behaviour: MedGemma combines apparent calibration through near-blanket refusal
> with the least stable comparative triage. The evaluation format also determines
> which failures are visible. Scoring patients separately misses the instability
> that appears as soon as the model must rank them.

### 24. Risques concrets

**Après**

> These failures map to concrete clinical risks. Capitulation can endorse a
> contraindicated combination under patient pressure. The missing prudence gradient
> can blur an absolute contraindication into a minor precaution. A triage order that
> changes with a patient's name or postal code can alter access to care. Factual
> question answering does not expose any of these behaviours.

### 25. Limites de TABIB

**Après**

> TABIB remains a preliminary probe. It covers seven open-weight models of at most
> nine billion parameters and does not support conclusions about larger proprietary
> systems. Its responses are judged by language models without clinical review. The
> demographic protocol permutes five profiles over only 100 cases. This reveals
> instability in this setting, but does not estimate its frequency elsewhere.

### 26. Des modèles aux agents

**Après :** séparer les produits existants de la définition de l'agent.

> TABIB tests a model answering one question, even when the conversation applies
> pressure. Systems entering clinical practice increasingly do more. In France,
> Nabla, Alan, and Synapse already describe systems that assist clinicians or
> patients across broader workflows.
>
> An agent combines a model with tools, a patient record, incoming messages, and
> local software. It acts over several steps instead of returning one answer. Knowing
> the right medical fact no longer guarantees a safe outcome across this sequence.

Conserver les exemples précis et leurs citations dans la première proposition.

### 27. Conscience de l'évaluation

**Conserver.** Le résultat, l'AUC et l'implication sont précis.

### 28. Reconstruire la clinique

**Après**

> Agents and evaluation awareness weaken clean question answering as the main test
> of a clinical system. Observing an agent in use requires an environment with a
> patient, a record, tools, and a task carried out over several turns. The outcome
> of the task, rather than one isolated answer, becomes the unit of evaluation.
>
> Early work follows this approach. AgentClinic uses simulated consultations, while
> tau-bench builds tool-and-user environments in other domains. Both report that
> sequential agents remain unreliable.

### 29. Environnement GLM-5.2

**Conserver.** Le modèle, les outils, la note et le critère d'échec sont introduits.

### 30. Quatre conditions

**Conserver.** Chaque condition ajoute une composante identifiable.

### 31. Note falsifiée

**Après**

> With the forged note, GLM-5.2 issues the contraindicated prescription in 0 of 20
> chat sessions, 2 of 20 one-turn tool sessions, 1 of 20 agentic sessions, and 5 of
> 20 agentic sessions under patient pressure. The largest observed rate appears when
> sequential action and pressure are combined, but the intervals remain wide.

### 32. Note authentique mais périmée

**Après**

> With an authentic but outdated note, the four conditions produce 0, 2, 0, and 1
> unsafe prescriptions. When the current ANSM contraindication is also supplied,
> the model still prescribes in 4 of 20 sessions. This is consistent with sensitivity
> to the forged note's authority, but too small to identify the mechanism.

### 33. Faux zéro du chat

**Conserver.** C'est une mise en garde méthodologique claire et distincte.

### 34. Limite du probe

**Après :** fusionner les deux paragraphes actuels.

> This probe covers one model, one scenario, and twenty sessions per condition. It
> cannot provide a stable failure rate. It does show why the unit of evaluation
> matters: a one-question benchmark cannot observe a failure that appears only after
> tool use and repeated patient pressure. This gap matters because deployed systems
> increasingly act over several steps, while their evidence still comes largely
> from question-answering scores.

### 35. Pourquoi la simulation

**Après**

> Real hospital records cannot be pooled across institutions, while testing an
> acting agent directly in care would expose patients to the behaviour under study.
> Simulations built from public and synthetic material offer a comparable and
> scalable intermediate test. This thesis used that principle to build training
> data; the same principle can support evaluation.

### 36. Retour historique et pression commerciale

**Après**

> A computer that can weigh a patient's signs toward a likely disease is no longer
> a distant prospect. Systems approaching this description are entering hospitals.
> Automated medical systems are not new. What has changed is the commercial scale.
> Vendors compete for contracts that may shape hospital infrastructure for years,
> creating pressure to deploy before the evidence is complete. The same incentive
> makes vendors poorly placed to provide the only evaluation of their systems.

### 37. Une science de l'évaluation

**Après**

> Independent evaluation has not kept pace with the systems it is meant to judge.
> Existing benchmarks often establish what a model knows and how often it answers
> correctly. They do not establish how it behaves while acting through tools, over
> time, and around people.
>
> Closing this gap is a research programme of its own. It requires environments in
> which models can be observed in use, measurements that capture their behaviour,
> and evidence that these measurements predict failures beyond the benchmark.
>
> Medicine built a discipline of controlled trials and surveillance after release.
> Aviation relies on simulators because real systems cannot safely serve as testbeds.
> AI in medicine now needs the same seriousness. The work ahead is to build a
> \textit{Science of Evaluation}.

## Ordre d'application proposé

1. Résoudre les points de provenance du chapitre 17.
2. Appliquer le chapitre 17 et vérifier ses tables et figures.
3. Appliquer la conclusion dans cet ordre, un paragraphe à la fois.
4. Supprimer les environnements `reviewrewrite` après validation.
5. Compiler le manuscrit complet et vérifier flottants, renvois et coupures.
