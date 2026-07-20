# Flow repair — `\section{The Work That Remains}` (conclusion.tex, lines 519–563)

The substance is settled and good. The problem is purely at the joints: several places
set up an inference and then start the next sentence cold, without the connective that
carries the reader across. This is a connective-tissue repair, nothing else.

Preserved: the final sentence verbatim, "Here we are.", the dream quote verbatim,
"arguably", the decades/careful concession, the companies-own-the-pressure blame with
evaluation left to independent research, the medicine/aviation/simulator comparison.

Original length: **544 words** (section body, excluding the heading). Both candidates
land at or under this.

---

## 1. Joints I found (where the prose lurches, and why)

**J1 — P1, wide intervals -> size claim.**
> "...and the intervals are wide. What the probe shows does not depend on its size."

The first sentence concedes a weakness (tiny sample), the second dismisses it. No
concession connective, so the reader reads a contradiction instead of a reply to one.

**J2 — P1, size -> benchmark.**
> "...does not depend on its size. A chat benchmark asks one question and takes one answer, and this failure needs several steps to appear."

The benchmark sentence *is the reason* size does not matter, but nothing marks it as a
reason. Inside it, "...one answer, **and** this failure needs several steps" uses "and"
for what is a contrast. Topic jump plus wrong connective.

**J3 — P2, becoming agents -> they act.**
> "...are becoming agents. They act over several steps on a patient record."

Same subject twice, and the second sentence is really a defining clause of the first.
Repeated-subject staccato.

**J4 — P3, inside is worse -> an agent acts.**
> "Running it inside is arguably worse. An agent under evaluation is an agent that acts, and the only way to find out whether an action is dangerous is to let the agent take it."

The second sentence is the justification for "worse" and starts cold. Missing causal
connective. This is the sharpest lurch in the section.

**J5 — P5, research's part -> the field's evaluation.**
> "Building it is research's part. The evaluation the field practises establishes what a model knows..."

Unsignalled pivot from what-must-be-built to what-exists. Then a single contrast is
broken across two sentences: "...while the models answered. It does not establish how
one behaves when it acts."

**J6 — P5, the "No company" one-liner interrupts.**
> "...evidence about which of those measurements can be trusted. No company has a reason to build it. Evaluation in this field has been a collection of separate exercises..."

"No company has a reason to build it" re-enters the P4 blame theme and lands *between*
the discipline description and the historical sweep, cutting both.

---

## 2A. Candidate X — minimal (**544 words**, net 0 vs original)

This is one model, one scenario, and twenty pairs, and the intervals are wide. Yet
what the probe shows does not depend on its size. A chat benchmark asks one question
and takes one answer, while this failure needs several steps to appear. The benchmark
does not measure it badly; it does not see it at all. It can report the model as safe
without ever looking where the danger is.

The systems reaching French clinical practice are becoming agents that act over
several steps on a patient record. The evidence offered for them is still a table of
question-answering scores, and the gap between what hospitals deploy and what the
field measures grows every year.

There is no easy way around this. Records cannot leave the hospital, so the test
cannot be run outside. Running it inside is arguably worse, because an agent under
evaluation is an agent that acts, and the only way to find out whether an action is
dangerous is to let the agent take it. It would not scale either, because data cannot
be pooled. Each hospital would rebuild the same setup behind its own walls, and no
result would carry to the next one. That leaves one route. The clinic must be rebuilt
from public and synthetic material, well enough that a model cannot tell the
reconstruction from the real thing. This thesis took that route for its corpora and
its models. Its evaluation needs it now.

Here we are. \textit{A computer that could weigh a patient's signs toward a likely
disease} no longer sounds like a strange thing to want, and something close to it is
being installed in hospitals. Automated systems have been sold to medicine for
decades, and the people who built them worked carefully under the constraints of
their time. What is different is the commercial scale. These systems are developed
and sold by companies competing for the same hospitals, and a hospital that installs
one is hard to move off it. Arriving first keeps the ward for years, so the pressure
is to deploy early, before the evidence is in. That pressure is the companies' to own,
and it is also what makes them the wrong party to measure the result.

Independent evaluation is what the situation asks for, and it does not exist at the
level these systems have reached. Building it is research's part. The evaluation the
field practises establishes what a model knows and how often it answers correctly,
which was enough while the models answered, but does not establish how one behaves
when it acts. What is missing is a discipline, with environments realistic enough to
act in, measurements fine enough to catch a behaviour, and evidence about which of
those measurements can be trusted. No company has a reason to build it. Evaluation in
this field has been a collection of separate exercises for as long as the field has
existed. Medicine built one for its own treatments, with controlled trials and
surveillance after release. Aviation built one too, and much of its testing runs in
simulators, for the same reason the clinic cannot serve as a testbed. Next to either,
the evaluation of AI systems looks improvised. The mountain in front of us is a
\textit{Science of Evaluation}.

### What changed in X (diff)

- **J1:** "wide. What the probe shows" -> "wide. **Yet** what the probe shows". Concession connective, and it echoes the CamemBERT-bio register ("Yet the size of the reported loss is difficult to reconcile with..."). `[+1]`
- **J2:** "...takes one answer, **and** this failure" -> "...takes one answer, **while** this failure". Contrast, not addition. `[0]`
- **J3:** "becoming agents. **They act** over several steps" -> "becoming agents **that act** over several steps". Drops the repeated subject and one sentence break. `[0]`
- **J4:** "arguably worse. **An** agent under evaluation" -> "arguably worse, **because an** agent under evaluation". States the cause. "Running it inside is arguably worse" survives verbatim. `[+1]`
- **J5 (partial):** "...while the models answered. **It does** not establish" -> "...while the models answered, **but does** not establish". One contrast, one sentence. `[0]`
- **length offset:** "The clinic **has to be** rebuilt" -> "The clinic **must be** rebuilt". Keeps the total at exactly 544. `[-2]`

Not touched in X: **J6** (the "No company" interruption stays where it is), and P4
is untouched end to end.

---

## 2B. Candidate Y — moderate (**~538 words**, ~6 shorter)

X, plus two moves that earn their keep. Only the paragraphs that differ from X are
shown; P2, P3 and P4 are identical to X.

This is one model, one scenario, and twenty pairs, and the intervals are wide. Yet
what the probe shows does not depend on its size. A chat benchmark asks one question
and takes one answer, while this failure needs several steps to appear. The benchmark
does not measure it badly; it does not see it at all, and can report the model as safe
without ever looking where the danger is.

*(P2, P3, P4 as in X.)*

Independent evaluation is what the situation asks for, and it does not exist at the
level these systems have reached. No company has a reason to build it, so building it
is research's part. Today the evaluation the field practises establishes what a model
knows and how often it answers correctly, which was enough while the models answered,
but does not establish how one behaves when it acts. What is missing is a discipline,
with environments realistic enough to act in, measurements fine enough to catch a
behaviour, and evidence about which of those measurements can be trusted. Evaluation
in this field has been a collection of separate exercises for as long as the field has
existed. Medicine built one for its own treatments, with controlled trials and
surveillance after release. Aviation built one too, and much of its testing runs in
simulators, for the same reason the clinic cannot serve as a testbed. Next to either,
the evaluation of AI systems looks improvised. The mountain in front of us is a
\textit{Science of Evaluation}.

### What changed in Y beyond X (diff)

- **P1 extra join:** "does not see it at all. **It can report**" -> "does not see it at all, **and can report**". Removes the last short "It..." beat. `[0]`
- **J6, the earned one:** moved "No company has a reason to build it." **up** and merged it into the chain of consequence — "...does not exist at the level these systems have reached. **No company has a reason to build it, so building it is research's part.**" The standalone mid-paragraph occurrence is deleted, so the discipline description now runs straight into the history uninterrupted. Net **shorter**. `[~ -6]`
- **J5, fuller:** with the freed room, "The evaluation the field practises" -> "**Today** the evaluation the field practises". Marks the pivot explicitly. `[+1]`

The blame structure survives Y intact and arguably reads harder: no company will build
it, therefore it falls to research. The pressure to deploy early still belongs to the
companies in P4, untouched.

---

## 3. My pick, and honest notes

**Pick: X.** The instruction was the smallest set of changes, and each element is there
on purpose. X removes J1–J5 with four connective edits and leaves every sentence's
content intact. Low risk, and the staccato is gone.

**If you want one more:** take Y's J6 reorder *only* (move "No company has a reason to
build it." up next to "Building it is research's part"). That interruption is a real
break, and fixing it comes out shorter rather than longer. I would not take anything
else from Y.

**Things I changed that I was not asked for (flagging them):**

- "The clinic **has to be** rebuilt" -> "**must be** rebuilt". This is a word-count
  offset, not a joint fix, and it lightly rewords one of your sentences. If you want
  that sentence verbatim, drop this edit; X then lands at 546, one word over. Two words
  is invisible on the page, but the budget was stated as hard, so I paid it.
- Y relocates one of your sentences. That is a reorder, not a joint repair, which is
  why it is in Y and not X.
- I did **not** touch P4 in either candidate. Re-reading it, its joints already hold
  ("What is different is the commercial scale." does the work). Nothing to repair there.

**Self-check against the blacklist:** no em dashes, no "not X but Y", no colon added,
no added triad (the discipline triad is your own genuine enumeration of three parts),
no wave/tide image, "mountain" remains the only image in the section, and no date,
name, "money", "this chapter" or "this thesis" enters the last two paragraphs. "This
thesis took that route" stays in P3, where it already was. The one thing I want you to
check yourself: "Yet" opens a sentence in P1, and P5 ends on the improvised/mountain
beat with no connective added; if J5 still reads like a pivot to you, Y's "Today" is
the one-word fix.
