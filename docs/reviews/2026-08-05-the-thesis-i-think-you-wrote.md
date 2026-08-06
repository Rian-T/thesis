# The thesis I think you wrote

*A final reader's note, not another audit.*

## The thesis in one sentence

This thesis asks how far French clinical NLP can progress without access to
private hospital records, and shows that public text, careful curation,
knowledge-aware pretraining, and synthetic supervision can carry a compact model
surprisingly far, but not far enough to replace evaluation in real clinical
conditions.

That is the manuscript's real claim. It is stronger than “we trained several
French biomedical models”, and more defensible than “synthetic data solves
clinical NLP”.

## The route

The manuscript follows one object through several transformations:

    public text
        ↓
    biomedical corpus
        ↓
    compact language model
        ↓
    description-conditioned extractor
        ↓
    synthetic longitudinal records
        ↓
    filled lymphoma eCRF
        ↓
    behavioural and agentic evaluation

Each part changes the question.

1. **Can public text provide enough biomedical material?**
2. **Which parts of that material are worth training on?**
3. **How should a compact model learn from it?**
4. **Can knowledge and descriptions make that model adaptable?**
5. **Can synthetic supervision approximate a task whose real data are private?**
6. **What does a good task score fail to tell us about a system in use?**

The final move is important. The thesis begins with a data-access problem and
ends with an evaluation problem. Synthetic data partly relaxes the first. It
does not solve the second.

## The four claims worth protecting

### 1. Better data can replace some quantity

The corpus chapters do not merely produce another collection of biomedical
text. They show that document and paragraph selection can remove large amounts
of training material without lowering downstream performance. The important
result is not that one third of the tokens remain. It is that this third retains
the useful signal under the evaluations performed.

The safe formulation is:

> Careful filtering can match the full corpus with substantially fewer training
> tokens in this setting.

The unsafe formulation is:

> Data quality is more important than data quantity.

The thesis supports the first. It contributes evidence toward the second, but
does not establish it generally.

### 2. Continuing from a public base is cheaper than starting again

Across CamemBERT-bio and the later ModernCamemBERT line, continual pretraining
repeatedly reaches competitive biomedical performance at a fraction of the
training cost of from-scratch alternatives. This is one of the cleanest threads
in the manuscript because it joins accuracy, accessibility, and carbon.

The result should remain tied to the accounting convention used: reserved
GPU-hours and a grid-intensity estimate. It is an estimated comparison of
pipelines, not direct electrical measurement.

### 3. A compact extractor can approach a much larger generator

On the synthetic lymphoma eCRF, MC-bio-gliner approaches Qwen3.5-4B on
value-F1, and the joint-supervision variant reaches an indistinguishable score.
This is the numerical climax of the thesis, but its qualifications are part of
the result:

- the task and reference are synthetic;
- the reference is silver;
- the generator remains better on evidence spans and confidence ranking;
- the compact model's clear systems advantage is weight memory, not demonstrated
  end-to-end latency;
- transfer differs between PARHAF and FRACCO.

The interesting claim is therefore not “the small model is as good as the large
model”. It is:

> For one structured clinical task, a compact extractor trained from public and
> generated supervision can match the larger generator on the value metric that
> defines form filling.

That sentence survives scrutiny.

### 4. Capability scores do not establish behaviour in use

TABIB and the exploratory agent environment change the scale of the argument.
The earlier chapters ask whether the model knows enough to perform a task. The
conclusion asks whether it keeps behaving safely when the same knowledge is
placed inside brand names, long notes, patient pressure, another language,
comparative triage, or a sequence of actions.

This is not a separate essay attached to the thesis. It is the consequence of
the preceding result. Once public data can produce a capable model, the limiting
question moves from construction to evaluation.

## What makes the manuscript original

The originality is not any single ingredient. Public corpora, continual
pretraining, ontologies, synthetic data, open-vocabulary extraction, and LLM
evaluation all exist independently.

The original shape comes from connecting them under one constraint:

> the target data cannot be shown.

That constraint explains the entire design:

- public biomedical sources replace hospital training text;
- filtering makes those sources computationally usable;
- continual pretraining avoids rebuilding general language knowledge;
- ontologies add medical structure without patient records;
- open-vocabulary extraction avoids fixing every future field during training;
- published cases seed synthetic longitudinal records;
- compact models allow local deployment;
- simulations make acting systems testable without exposing patients.

The same constraint creates both the methods and their limits. That coherence is
the thesis's strongest narrative asset.

## The evidence ladder

Not every experiment supports the same level of claim.

| Level | Evidence in the thesis | What it supports |
|---|---|---|
| 1 | Intrinsic corpus statistics and classifiers | The data pipeline behaves as intended |
| 2 | Biomedical benchmark performance | The representations transfer to established tasks |
| 3 | Synthetic lymphoma eCRF | The complete pipeline can fill one longitudinal form |
| 4 | PARHAF and FRACCO | Some components transfer to human-written annotated text |
| 5 | Informal feedback from CHU clinicians | The setup is plausible enough to investigate |
| 6 | TABIB and the GLM-5.2 probe | Standard scores miss some behavioural failures |
| Missing | Private hospital eCRFs with clinical annotation | Real-world validity of complete form filling |
| Missing | Prospective deployment study | Safety and usefulness in care |

The manuscript is strongest when it climbs this ladder explicitly and weakest
when language from a higher level is used for evidence from a lower one.

## A small terminological constitution

- **Field**: one variable in the eCRF.
- **Value**: the normalized answer assigned to a field.
- **Evidence span**: the passage supporting that value; it need not be identical
  to the normalized value.
- **Record**: the complete longitudinal set of documents for one patient.
- **Report** or **document**: one dated item inside that record.
- **Silver reference**: labels proposed automatically and checked structurally,
  not validated by human annotators.
- **Generated record**: the synthetic sequence of clinical documents.
- **Published clinical case**: the human-written public narrative used as a seed.
- **Human-written text**: PARHAF, FRACCO, and published cases.
- **Private hospital record**: the unavailable target data; never use
  “human-written” as its synonym.
- **Open vocabulary**: descriptions are not fixed as a classification layer. It
  does not guarantee transfer to every unseen concept.
- **Local deployment**: computation within the institution. It does not itself
  imply safety, speed, or low energy use.
- **Agent**: a model acting over several steps with tools and state, not merely a
  chat model receiving a long prompt.

## The claims that deserve permanent qualifiers

These qualifiers are not defensive clutter. They state exactly what was learned.

- **“in this experiment”** for corpus ablations with one run per condition;
- **“on the synthetic lymphoma eCRF”** for the 0.640/0.658 comparison;
- **“weight memory”** for the 0.3 GB versus 8 GB comparison;
- **“benchmark-absent”** rather than “unseen” for the new descriptions;
- **“human-written NER”** for PARHAF and FRACCO;
- **“informal feedback”** for the CHU discussions;
- **“preliminary”** for TABIB;
- **“observed rate”** for twenty-session agent conditions;
- **“consistent with”** when an experiment does not isolate a mechanism;
- **“before clinical use”** whenever a result could sound deployment-ready.

## What I would no longer change

At this stage, I would protect the following from further stylistic polishing:

1. The opening line of the conclusion.
2. Lymphoma as the single case study of Part IV.
3. The concrete explanation of published cases becoming longitudinal records.
4. Negative and mixed results, especially the CLM limits, FRACCO, calibration,
   and the false safety of refusal.
5. The final move toward a Science of Evaluation.
6. Short transitions that already say one thing once.

The manuscript now gains more from consistency and provenance than from prettier
sentences.

## What could still damage the thesis late

The main late-stage risks are not prose.

### A numerical value loses its provenance

A rounded score copied from an old dashboard can become impossible to reproduce.
Every headline number should point to a current artifact, command, or immutable
table.

### A qualification disappears during compression

Removing “synthetic”, “silver”, “weight”, or “observed” can silently strengthen a
claim beyond its evidence.

### English and French summaries diverge

They need not be sentence-level translations, but they must preserve the same
contributions, results, and limitations.

### A figure tells a cleaner story than the underlying example

Schematic figures are useful, but must be identified as schematic when their
values or text are illustrative.

### The conclusion becomes a second introduction

Its job is not to repeat every contribution. It should answer what held together,
where the route stopped, and why evaluation became the next problem.

## The ending I would want the reader to retain

The thesis does not argue that hospital data are unnecessary. It demonstrates
how much can be built before they become unavoidable.

Public data can support a biomedical corpus. Filtering can reduce its cost.
Continual pretraining can produce compact domain models. Ontologies and
descriptions can make extraction more adaptable. Published cases can seed a
synthetic longitudinal task. A small extractor can then approach a much larger
generator on that task.

At that point, the absence of hospital data stops being only a training
constraint. It becomes an evaluation constraint. We can build the model without
seeing the ward, but we cannot conclude that it will work safely there.

That is why the manuscript ends with evaluation rather than with a model.
