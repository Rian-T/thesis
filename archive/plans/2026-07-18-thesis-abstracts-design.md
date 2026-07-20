# Thesis abstracts revision design

## Scope

Revise the English and French abstracts in `sources/abstract.tex` without changing
their five-paragraph structure, scientific claims, reported results, or overall
level of detail.

## English abstract

- Keep the existing prose unless a change is needed for accuracy or clarity.
- Replace the claim that the models are deployed in hospitals with a statement
  that they are designed to be usable locally where hospital records remain.
- Distinguish the released French biomedical corpora from the two million
  multilingual clinical-case passages extracted from PubMed Central, which are
  predominantly in English.
- Only lighten sentences when required by those corrections.

## French abstract

- Rewrite the French as an autonomous scientific text rather than a sentence-level
  translation of the English.
- Follow the direct style of the CamemBERT-bio TALN 2023 paper: explicit subjects,
  concrete verbs, short logical transitions, and standard French NLP terminology.
- Remove translation calques such as `égale le préentraînement complet`, `se
  transfère à l'anglais`, and `conception des données`.
- Preserve factual parity with the English abstract, including all numerical
  results and limitations.

## ADUM and verification

- Each abstract must remain at or below 4,000 characters, counting spaces and line
  breaks.
- The text in `sources/abstract.tex` is the canonical version to paste into ADUM.
- Compile the thesis, inspect the rendered abstract pages, recount both blocks, and
  compare their claims paragraph by paragraph.
- Do not modify any other thesis content.
