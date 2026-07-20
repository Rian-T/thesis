# Conservative corrections to the knowledge-pretraining TikZ figures

Date: 2026-07-19

## Objective

Correct the four knowledge-pretraining figures in
`sources/related_works/corpus_annotation.tex` with the smallest defensible
changes. Each figure must communicate one bounded mechanism and must not imply
that architectures with materially different inputs or training procedures
share the same pipeline.

The governing principle is to prefer a narrower claim over a visually complete
but contestable generalisation.

## Scope

The change is limited to:

- the four TikZ figures `fig:corpus-static`, `fig:corpus-inject`,
  `fig:corpus-contrastive`, and `fig:corpus-g2t`;
- their captions;
- the immediately adjacent explanatory prose;
- the subsection title currently named `Graph-to-Text for Pretraining`;
- the two corresponding summary sentences near the end of the section.

The change does not revise the broader chapter structure, add new literature,
or alter unrelated terminology and bibliography entries.

## Shared medical example

Where a medical mini-graph remains, it is explicitly labelled an
`illustrative cross-ontology graph`, not an ontology fragment. It uses:

- `Diabetes mellitus` — ICD-10 group `E10--E14`;
- `Type 2 diabetes mellitus` — ICD-10 code `E11`;
- `Biguanides` — ATC code `A10BA`;
- `Metformin` — ATC code `A10BA02`.

All semantic relations are directed:

- `Type 2 diabetes mellitus -> Diabetes mellitus` (`is-a`);
- `Metformin -> Biguanides` (`is-a`);
- `Metformin -> Type 2 diabetes mellitus` (`treats`).

The cross-ontology clinical relation `treats` is dashed and identified as an
illustrative association rather than a native ICD-10 or ATC edge. Hierarchical
relations remain solid.

## Figure 1: static graph embeddings

### Visual design

- Retain the four-stage left-to-right layout.
- Rename the first stage `illustrative cross-ontology graph`.
- Correct the code range and all edge directions as specified above.
- Rename `random walk` to `sampled graph path`.
- Show a directionally valid path such as
  `Metformin -> Type 2 diabetes mellitus -> Diabetes mellitus`.
- Preserve relation labels on the path and add a small note that RDF2Vec
  sequences may retain predicates.
- Rename the `skip-gram` box to `word2vec-style objective`.
- Keep the final `one fixed vector per node` stage unchanged in meaning.

### Prose and caption

The prose distinguishes the algorithms rather than stating that every method
runs the same kind of random walk:

- Node2Vec uses biased random walks and a skip-gram objective.
- RDF2Vec derives sequences from directed RDF graph traversals and may retain
  relation predicates.

The caption describes the common sequence-to-vector pattern while preserving
this distinction.

## Figure 2: knowledge injection

### Represented method

The figure represents K-BERT only. DRAGON remains in the prose but is explicitly
described as a different architecture and is removed from the figure caption.

### Visual design

- Retain the original sentence-token row.
- Attach the knowledge branch
  `metformin -> treats -> Type 2 diabetes` to the `metformin` mention.
- Show that the original and added tokens enter a flattening step.
- Label the control mechanism `soft positions + visibility matrix`.
- Feed the resulting representation into the Transformer.
- Replace `triple injected at the entity token` with
  `knowledge branch attached to the entity mention`.

### Prose and caption

The subsection introduction says that this family couples text with explicit
entities or graph structure; it does not claim that every method places an
entity directly inside the token sequence.

The sentence introducing the figure states that it illustrates K-BERT's
input-level mechanism. The following sentence contrasts DRAGON: it accepts a
text segment and a relevant knowledge subgraph as separate modalities and
fuses them bidirectionally while training with masked language modelling and
link prediction.

The caption cites K-BERT only and states that other knowledge-enhanced models
use different integration mechanisms.

## Figure 3: medical contrastive learning

### Represented method

The figure represents SapBERT's synonym-alignment objective only. CODER remains
in the prose, where its relation-triplet objective is stated explicitly, but is
not claimed to be visualised.

### Visual design

- Replace the force-arrow layout with one borderless-looking but lightly framed
  two-dimensional embedding plane.
- Label the plane `illustrative 2D embedding projection — not to scale`; do not
  draw axes, graduations, coordinates, numerical distances, or trajectories.
- Place `T2DM`, `NIDDM`, and `diabète de type 2` close together inside a soft
  green cluster halo labelled `same UMLS concept`.
- Place `Type 1 diabetes mellitus` clearly farther away in the existing orange
  negative style, labelled `different but related concept — negative pair`.
- Keep all terms readable as small rounded chips rather than reducing them to
  anonymous points.
- Preserve the thesis palette, rounded corners, sans-serif figure font, line
  weights, and spacing used by the surrounding TikZ figures.
- Do not add a CODER relation branch; this avoids turning a small SapBERT
  diagram into a compressed and incomplete two-objective diagram.

### Prose and caption

The prose distinguishes:

- SapBERT: synonymous terms associated with the same UMLS concept;
- CODER: additional contrastive supervision from term--relation--term triples.

The caption cites SapBERT only, explicitly calls the geometry a schematic 2D
projection, and describes the right-hand concept as distinct but medically
related. It must not imply that the displayed coordinates or distances come
from a measured embedding run.

## Figure 4: EntiGraph

### Subsection title

Use the broader title:

```latex
\subsection{Synthetic Data for Pretraining}
```

The title avoids the incorrect implication that EntiGraph consumes an existing
knowledge graph, while remaining broad enough to cover both synthetic textbook
data and EntiGraph.

### Visual design

Replace the ontology-to-text pipeline with:

1. a small source-document box;
2. a salient-entity extraction stage;
3. sampled entity pairs or triples;
4. an `LLM relation analysis` box receiving both the sampled entities and the
   source document;
5. a relation-focused synthetic-text output.

Retain the experimentally reported scale annotation
`1.3M real tokens -> 455M synthetic tokens`.

### Prose and caption

The prose says that synthetic data can make pretraining or continued
pretraining more data-efficient. It then describes EntiGraph precisely:

- salient entities are extracted from source documents;
- groups of entities are sampled;
- an LLM with access to the source document analyses their relations and
  generates synthetic text;
- the synthetic corpus is used for continued pretraining.

The caption must not use `ontology fragment`, `graph input`, or wording that
suggests an external structured ontology is provided to EntiGraph.

## Closing paragraph

Replace `Graph-to-text for pretraining` with
`Entity-centric synthetic augmentation for continued pretraining` in the
closing discussion. Replace `generating text from the graph` with
`synthesising relation-focused text from source documents`.

These phrases describe EntiGraph's mechanism without making the subsection
title method-specific.

## Verification criteria

The implementation is acceptable only if:

1. the thesis builds successfully;
2. all four figures remain legible at thesis text width, with no overlaps or
   clipped labels;
3. every graph relation has an unambiguous direction;
4. the ICD-10 and ATC namespaces are visually explicit;
5. the `treats` edge is visibly distinguished from native classification
   hierarchy;
6. the K-BERT caption cites K-BERT only;
7. the SapBERT caption cites SapBERT only;
8. the EntiGraph figure begins with source documents, not an ontology;
9. references to DRAGON and CODER remain accurate in prose without claiming
   that their full mechanisms are shown;
10. no unrelated thesis text, bibliography entry, or figure is changed.

## Primary references used for the design

- Node2Vec: <https://arxiv.org/abs/1607.00653>
- RDF2Vec: <https://madoc.bib.uni-mannheim.de/41307/1/Ristoski_RDF2Vec.pdf>
- K-BERT: <https://arxiv.org/abs/1909.07606>
- DRAGON: <https://arxiv.org/abs/2210.09338>
- SapBERT: <https://aclanthology.org/2021.naacl-main.334/>
- CODER: <https://arxiv.org/abs/2011.02947>
- EntiGraph: <https://arxiv.org/abs/2409.07431>
- French ICD-10: <https://www.atih.sante.fr/sites/default/files/public/content/2665/cim10_2015_final_0.pdf>
- ATC classification: <https://www.who.int/tools/atc-ddd-toolkit/atc-classification>
