# Seam proposals

Proposals only. No `.tex` file was edited, no build was run. Each section covers one
seam between parts, in reading order. Line numbers are approximate.

---

## Seam 1 — Introduction → `part:biomedtext`

**Verdict: fine.**

**Evidence.** `sources/contributions.tex` (line 35) closes the outline:

> The parts follow these questions. After this introduction, the first part asks what
> biomedical text is and how far its public forms are from the clinical notes we care about.

`sources/biomedical_text/biomedical_text.tex` (lines 6-13) opens:

> Medicine does not produce a single kind of text. The same illness is written about in very
> different ways, depending on its writer and its purpose.

**Diagnosis.** The outline sets the question ("how far are the public forms from the clinical
note?") and the part opens on a concrete observation rather than on meta-commentary. The hand-off
lands. No change proposed.

**The question the reader carries.** If the public text is not the clinical note, how far apart
are they?

**Risk.** None.

---

## Seam 2 — `part:biomedtext` → Related Works

**Verdict: broken (mild).**

**Evidence.** `sources/biomedical_text/web.tex` (lines 167-172) closes the part:

> Biomedical text is not a single language. The same medical knowledge changes with who writes
> it, who reads it, and what the text is meant to do. Clinical notes, research articles, and
> patient-facing texts therefore offer different views of medicine, and only the latter two are
> widely available. The challenge for the rest of this thesis is to use this public text without
> losing sight of the clinical language we ultimately need.

`sources/related_works.tex` (lines 6-13) opens:

> Building a language model for French clinical text draws on three areas of earlier work. The
> first is the language model itself, how it represents text and learns from it. The second is
> the data it is trained on, both raw text and structured medical knowledge. The third is the
> clinical extraction task the model is finally asked to perform.

**Diagnosis.** The part ends well, on a live question. The next part then opens on an inventory of
its own three chapters and never picks that question up, so the reader arrives at Related Works
without being told why a survey comes now. Cold open plus table-of-contents framing.

**Proposed replacement** for the opening paragraph of `sources/related_works.tex`:

```latex
The previous part left a gap between the text we can train on and the text we care about. Crossing
it means knowing what earlier work already provides. Three areas matter here. The first is the
language model, how it represents text and learns from it. The second is the data it is trained
on, both raw text and structured medical knowledge. The third is the clinical extraction task the
model is finally asked to perform. The three chapters that follow review each in turn, and
together they set up the problem this thesis works on: adapting strong general methods to a
language and a domain where the right training data is hard to find.
```

**The question the reader carries.** What do existing methods already offer for crossing from
public text to the clinic, and where do they stop?

**Risk.** Low. It rewrites one sentence and keeps the rest of the paragraph verbatim. Check that
no other agent is editing `related_works.tex` this session.

---

## Seam 3 — Related Works → `part:corpus`

**Verdict: fine.**

**Evidence.** `sources/related_works/clinical_ie.tex` (lines 628-631) closes:

> The gaps above set the agenda for the contributions of this thesis. The next part begins with the
> first of them, the construction of a biomedical corpus for French from public sources.

`sources/part_1/analysis_lm.tex` (lines 6-13) opens:

> Clinical text is private, so a public model has to be trained on text gathered from elsewhere.
> This part builds that corpus.

**Diagnosis.** The RW chapter names the gap without previewing the solution, which respects the
no-spoiling rule, and the part picks up exactly that gap. No change proposed.

**The question the reader carries.** Can a public French biomedical corpus be assembled at all?

**Risk.** None.

---

## Seam 4 — `part:corpus` → `part:pretraining`

**Verdict: fine.**

**Evidence.** `sources/part_1/chapter3/article.tex` (line 230) closes the part:

> The corpus is now ready. The next two chapters use it to train French biomedical encoders.
> \Cref{chap:encoders} starts with the simplest recipe [...]

`sources/part_2/extensions_lm.tex` (lines 5-11) opens:

> A corpus is only useful once a model has learned from it. This part puts the biomedical corpus to
> work and asks what makes pretraining on it effective.

**Diagnosis.** Sound. The chapter transition hands off a named cliffhanger (the CLM detour leaving
a permanent imprint) and the part opener repeats it at a coarser grain without contradiction. The
overlap is small enough to leave alone.

**The question the reader carries.** What makes pretraining on this corpus effective?

**Risk.** None.

---

## Seam 5 — `part:pretraining` → `part:adaptation`

**Verdict: broken. This is the worst seam.**

**Evidence.** `sources/part_2/chapter5/article.tex` (line 493) ends chapter 5, which is not the
last chapter of the part:

> Parts~1 and 2 of this thesis have focused on data and pretraining: how to collect biomedical
> text, how to filter it, and how to train encoder models on it. But a pretrained model is only
> useful if it can be deployed on real tasks. In the next part, we turn to adaptation: how to
> extract clinical information when labeled data is scarce, labels number in the thousands, and
> the only available text is public.

`sources/part_2/chapter6/article.tex` (line 490) then ends the part with the real bridge:

> The textbooks in this chapter are synthetic, generated from an ontology rather than drawn from
> hospital records. That same move, building training text where none can be shared, is what the
> next part turns to. [...] (\Cref{part:adaptation})

**Diagnosis.** Duplicate hand-off. Part 3 is announced twice, two chapters apart, and the first
announcement is both premature and wrong: "In the next part" is false when a chapter of this part
still follows. It is also a summary of Parts 1 and 2 where a transition to chapter 6 belongs, so
chapter 6 opens with no thread to pick up. The paragraph additionally carries "only useful if"
framing that says nothing chapter 6 needs.

**Proposed replacement** for that final paragraph of `sources/part_2/chapter5/article.tex`. Keep
the two conclusion paragraphs above it as they are; replace only the post-`\vspace{2em}` text:

```latex
The detour improves the encoder by changing how it is trained, using the same text throughout.
Some of what a clinical coder needs is never written in that text. Codes stand in a hierarchy,
exclude one another, and carry lists of synonyms, and no article states this structure outright.
The next chapter asks whether an encoder can learn it anyway, from an ontology written out as
prose.
```

**The question the reader carries.** Can knowledge that the text never states be put into the
encoder?

**Risk.** Chapter 5 is under active edit this session (`eric-ch5`), so this must be reconciled
before applying. The proposal deletes the only place where Parts 1 and 2 are recapped together;
Rian may want that recap, in which case the conclusion chapter already carries it
(`sources/conclusion.tex`, "A Single Route Through Public Text") and no replacement is needed
here.

---

## Seam 6 — `part:adaptation` → Conclusion

**Verdict: fine.**

**Evidence.** `sources/part_3/chapter7/article.tex` (line 338) closes the part:

> Matching a fine-tuned generative model at 27 times fewer parameters, with no clinical data, is
> the result of this part. Whether it carries to human-written records is the next thing to
> establish, and confirming it on French hospital records is the necessary step before any
> clinical use.

`sources/conclusion.tex` (lines 10-13) opens:

> The parts of this thesis were built one at a time. Read together, at the close, they trace a
> single route from public text to a filled clinical form and share a single concern, the energy
> that route costs.

**Diagnosis.** The part ends on an open question and states its limit honestly. A conclusion is
allowed to open by changing altitude rather than by picking up the last question, and this one
does that cleanly. No change proposed.

**The question the reader carries.** Does the result survive contact with real hospital records?

**Risk.** None. The Part 3 internal seam was fixed recently and nothing in these proposals touches
it.

---

## Summary

| Seam | Verdict | Size of change | Priority |
|------|---------|----------------|----------|
| 1. Intro → `part:biomedtext` | fine | none | — |
| 2. `part:biomedtext` → Related Works | broken (mild) | one sentence | medium |
| 3. Related Works → `part:corpus` | fine | none | — |
| 4. `part:corpus` → `part:pretraining` | fine | none | — |
| 5. `part:pretraining` → `part:adaptation` | broken | one paragraph replaced | high |
| 6. `part:adaptation` → Conclusion | fine | none | — |
