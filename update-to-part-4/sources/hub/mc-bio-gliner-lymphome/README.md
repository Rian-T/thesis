---
license: mit
language: fr
library_name: gliner2
tags:
- token-classification
- structured-extraction
- biomedical
- french
- clinical
- gliner
pipeline_tag: token-classification
---

# MC-bio-gliner — lymphoma eCRF (simple supervision)

French biomedical structured extractor (GLiNER2 architecture, ~150M parameters)
built on the **MedEmbed-v9** sentence-embedding backbone. Fine-tuned on a
**synthetic** lymphoma electronic case report form (eCRF) task with 89 fields.

This checkpoint is the one used to produce the reported scores in the thesis
chapter *Evaluating Open-Vocabulary Extraction* (capstone eCRF).

## Results (410-document synthetic test split, value-F1 with field competition)

- **value-F1: 0.640**\n- **span-F1: 0.503**

## Important note on data

The lymphoma eCRF is **entirely synthetic** (`rntc/lymphome-synth-v4`), not real
hospital data. It imitates a longitudinal clinical study form. See the thesis for
the evaluation protocol (validation-selected threshold, test never used for
selection).

## Usage

```python
from gliner2 import GLiNER2
model = GLiNER2.from_pretrained("rntc/mc-bio-gliner-lymphome")
```

## Variants

- `rntc/mc-bio-gliner-lymphome` — simple supervision (value-F1 0.640 / span-F1 0.503)
- `rntc/mc-bio-gliner-lymphome-joint` — joint supervision (value-F1 0.657)
