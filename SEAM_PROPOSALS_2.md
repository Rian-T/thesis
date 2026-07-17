# SEAM_PROPOSALS_2 — two transitions, proposals only

No `.tex` file was edited and no build was run.

---

## Transition A — end of chapter 5 (CLM detour) into chapter 6 (OntoBook)

### Current text
`sources/part_2/chapter5/article.tex`, lines ~489-493 (the final block, after the `\section*{Conclusion}` paragraphs):

```latex
\vspace{2em}

\begin{reviewread}
Parts~1 and 2 of this thesis have focused on data and pretraining: how to collect biomedical text, how to filter it, and how to train encoder models on it. But a pretrained model is only useful if it can be deployed on real tasks. In the next part, we turn to adaptation: how to extract clinical information when labeled data is scarce, labels number in the thousands, and the only available text is public.
\end{reviewread}
```

### What is wrong
It is factually wrong: chapter 6 still follows inside Part 2, so "in the next part, we turn to adaptation" skips a chapter. It also spends the Part 3 announcement one chapter too early, which is exactly the announcement transition B needs to make.

### Proposal A1 (recommended)

```latex
\vspace{2em}

Both parts of this thesis so far have worked on text. We collected biomedical text,
filtered it, and changed the objective that reads it, and the gains came from doing
those two things well. Medical knowledge is also written down in another form. The
ontologies used in French hospitals record diseases, procedures, and drugs as concepts
with explicit relations between them, hierarchy, exclusion, and association, and none of
that has entered our pretraining (\Cref{sec:corpus-ontologies}). An encoder learns from
running text, and a graph is not running text. The next chapter asks how the knowledge in
an ontology can be given to a model that can only read.
```

### Proposal A2

```latex
\vspace{2em}

So far we have improved the encoder by improving the text it reads and the objective it
reads with. Neither touches the knowledge that French hospitals keep outside of text, in
the ontologies that list codes and state how they relate to one another
(\Cref{sec:corpus-ontologies}). That knowledge is stored as a graph, and pretraining
consumes sentences. The next chapter asks what it takes to bring one into the other.
```

**Recommendation: A1.** It names what the ontology holds (relations between diagnoses, procedures, and drugs) so the reader feels the size of what is being left out, and it echoes the related works without borrowing chapter 6's opening. A2 is shorter but abstract, and "bring one into the other" is vaguer than the plain question A1 ends on.

### Overlap check with what follows
Chapter 6 opens (`sources/part_2/chapter6/article.tex`, l. 73-79):

> "To assign a code to a discharge summary, a hospital coder relies on facts that the summary never states. Type 2 diabetes, coded E11, can cause a specific kidney disease coded N08.3. Two diagnoses may be mutually exclusive... This chapter asks whether that structure can be turned into a training signal for encoders."

Neither proposal names the coder, the discharge summary, E11/N08.3, mutual exclusion, or the walk-and-rewrite method. Both stop at the mismatch (knowledge is a graph, a model reads text) and leave the coding scene, the concrete example, and the answer entirely to chapter 6's own hook. The one deliberate echo is with the related works, `\Cref{sec:corpus-ontologies}`, which already ends on the same mismatch ("stored as graphs rather than as the running text that language models expect").

### The question the reader carries forward
How can the knowledge in an ontology be turned into something an encoder can be trained on?

---

## Transition B — end of chapter 6 into Part 3

### Current text
`sources/part_2/chapter6/article.tex`, final paragraph (~l. 488-490, after `\section*{Conclusion}` and `\vspace{2em}`):

```latex
The textbooks in this chapter are synthetic, generated from an ontology rather than drawn from hospital records. That same move, building training text where none can be shared, is what the next part turns to. It leaves pretraining behind and puts an encoder to work on the task a clinical study needs: reading the reports written about a patient during care and filling the structured form the study keeps for that patient. No real hospital record can be shared to learn from, so the constraint that shaped the corpus and the encoders of the first two parts now shapes the task as well (\Cref{part:adaptation}).
```

### What is wrong
It writes the Part 3 introduction. The task description ("reading the reports written about a patient during care and filling the structured form") and the no-shareable-records constraint are both delivered again, at greater length, one page later in `sources/part_3/clinical_tasks.tex`. A bridge should ask the question that the Part 3 intro then answers.

### Proposal B1 (recommended)

```latex
Two parts of pretraining end here. We have a corpus, an objective, and a way to add
ontology knowledge, and every gain has been measured on benchmarks, one fixed label set
at a time. That is not the shape of the problem a hospital brings. The next part takes a
pretrained encoder to a clinical task and asks what fine-tuning it there actually requires
(\Cref{part:adaptation}).
```

### Proposal B2

```latex
Pretraining ends here. The first two parts produced encoders, and their quality has only
been read off benchmark scores. The question left is what happens at the end of the chain,
when one of these encoders has to be fine-tuned for a task a clinical service needs
(\Cref{part:adaptation}).
```

**Recommendation: B1.** It gives one concrete reason the benchmarks are not the real problem (one fixed label set at a time), which is a fact already earned by Part 2 and not a Part 3 spoiler, and it lands on the fine-tuning question Rian wants. B2 is clean but says only "the question is what happens next", which is closer to announcing than to asking.

### Overlap check with what follows
The Part 3 intro opens (`sources/part_3/clinical_tasks.tex`):

> "The first two parts built a public biomedical corpus and pretrained encoders on it. This part uses one of those encoders on a clinical task. The task comes from clinical research. A study follows each of its patients over time and keeps a structured form for each one..."

Neither proposal describes the study, the form, the fields, the reports, the correction-over-time difficulty, the built-not-collected supervision, or the on-premise constraint. All of that stays where it belongs. The only shared idea is "a pretrained encoder now meets a clinical task", which is the seam itself and is stated in one clause in the bridge and then unfolded by the intro.

Minor note, not part of this proposal: the Part 3 intro's own first sentence ("The first two parts built a public biomedical corpus and pretrained encoders on it") is a light restatement of the bridge's first clause. If both are accepted as written, dropping the bridge's summary clause or the intro's first sentence would remove the last echo. That is Rian's call.

### The question the reader carries forward
What does it take to fine-tune one of these encoders for the task a clinical service actually has?
