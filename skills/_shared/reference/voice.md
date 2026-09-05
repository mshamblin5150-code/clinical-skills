# Voice — how a register gets modeled, and where the model lives

**This file is the method. It is not the model.** What it builds is
`scratch/voice-model.md`, gitignored, **one per clinician**, from writing samples that clinician
supplies. This file travels; the model does not.

[#213](https://github.com/mshamblin5150-code/clinical-skills/issues/213) asked for
`reference/voice.md` *built from writing samples he supplies*, and splitting the method from the
model is a change to that ask. The reason is the ticket's own *And it must generalize* section,
plus a rule that landed after it was written.
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212) put it in
[setup-clinical-skills](../../setup-clinical-skills/SKILL.md) step 5: **a rule that resolves
against one account belongs in the profile rather than in the reference**, because the reference is
the file a second clinician inherits. A register is that shape at its purest — it is nobody else's,
it is useless to anyone else, and shipping one person's in `reference/` makes every other user
sound like him, **which the ticket names as worse than no model at all**.

There is a second reason and it is the harder one: **a model has to quote, and the quotes are the
user's own work.** [style.md](style.md) is the precedent in this directory — it was distilled from
a working file that quoted ten submissions in full, that file is gitignored, and what survived into
`reference/` is the *shape*, with no name, no dates finer than a year and no links. Same split, one
step further out.

---

## 1. Why [style.md](style.md) §11 was not enough

§11 is real and it is not sufficient. **A run satisfied every bullet in it and still read as a
competent stranger** — that is the finding #213 was filed on, in the clinician's words: *"this is
missing my — I don't know how to say it — way of speaking."*

The gap is what the two files measure. **§11 was written by reading finished documents for what
they *do*.** First person and decisive, show the arithmetic, name the inconsistency, reason on
physiology, argue rarity down. Those are moves, and a competent stranger can execute all of them.

**A register is how it sounds**, and it lives in things a move list has no column for: sentence
rhythm, where the weight falls, which words are his rather than the field's, how a position is
taken and how its cost is accepted, what he never does.

**So this file does not produce more adjectives.** *Warrior, stoic, philosopher* is the clinician's
own name for his register and it is the starting point rather than the output — an adjective does
not constrain a draft. What constrains a draft is §5's **discriminating pair**, and the model is
built to carry pairs rather than descriptions.

---

## 2. The three registers, because the document contains all three

A case study is not written in one voice, and a model built from one register produces the other
two wrong.

| # | Register | Where it lives | What it sounds like |
| --- | --- | --- | --- |
| 1 | **Clinical argument** | MDM, and the differential's reasoning | A discriminator is stated and a diagnosis goes in or out. Compressed, technical, verdict-carrying. |
| 2 | **Spoken patient education** | `Patient Education:` | Second person, contractions, jargon translated in the same breath. §11 calls this the most distinctive voice in the document. |
| 3 | **Reflective or argumentative prose** | Assessment, Discussion, the MDM entry that argues a rarity down | Where warrior, stoic and philosopher actually live. Takes a position, accepts its cost, reaches for a principle when a protocol will not do. |

**Register 3 is the one the clinical corpus supplies least of**, and it is the one #213 was filed
about. A model that covers 1 and 2 and not 3 has modeled the parts that were already working.

**The failure mode of a single-register model is specific and visible.** Build only from MDMs and
the patient education comes out sounding like an MDM — [style.md](style.md) §7 exists to prevent
exactly that, and a voice model is a new way to reintroduce it.

---

## 3. Collecting the samples

**[setup-clinical-skills](../../setup-clinical-skills/SKILL.md) step 8 is where the asking happens.
This section is the spec for the ask, and it is not restated there** — the same split step 4 of
that skill already runs on with [batch-shift](../../batch-shift/SKILL.md)'s preceptor lookup, and
for the same reason: one rule written twice is one rule that drifts. What belongs to that step
rather than to this section is that the offer is skippable, that a refusal is recorded, and that a
re-run reads an existing model instead of re-collecting.

For an assistant export, [voice-corpus.md](voice-corpus.md) is the vendor-neutral method.

**Ask for 5 at minimum. 8 is better. Coverage beats count** — two or three per register beats eight
of one kind, and the count is the thing that looks like progress while the coverage is the thing
that decides whether the model works.

**Ask for register 3 explicitly and by description, not by name.** The clinician does not think in
these three categories, and nobody does. Ask for *anything you have written where you were arguing
a position rather than documenting a patient* — **non-clinical writing is wanted here** and should
be said out loud, because a request that sounds clinical returns clinical documents and register 3
is the register the clinical corpus is thinnest in.

**Ask for writing that already exists.** A sample written in order to demonstrate a voice is a
performance of one, and it will be more self-conscious, more careful and more even than the real
thing. The tics that identify a person are the ones they are not watching.

**A graded submission is a legitimate sample and it is a compromised one.** It is real writing in
registers 1 and 2, and it was written to a rubric by somebody being marked. Take it, and note in
the model which samples were graded work — a feature appearing only in graded documents is a
feature of being graded.

**Where they go.** `scratch/writing-samples/`, gitignored, one file per sample, each naming its
register and whether it was graded. A `.docx` is read with `tools/docx_read.py`, with `--normalize`
if it came through a rendered web page.

**Consent, and it is not a formality.** The samples are the user's own work and a clinical sample
is a patient record. Three rules, and they are the ones
[harvest_review.py](../../../tools/harvest_review.py) already runs on:

- Samples live under `scratch/` and nowhere else. Standing rule 1 in
  [AGENTS.md](../../../AGENTS.md).
- **A quote from a sample never goes anywhere the author is not the audience.** Not into a ticket,
  not into a commit message, not into a file outside `scratch/`, not into a summary for anyone but
  him. That is also why the model is gitignored — a model that could not quote would be a list of
  adjectives, and §1 is about why that fails.
  **The rule names the audience rather than the channel, and it was rewritten the first time it
  ran.** It read *never leaves `scratch/`, not into a summary handed back in conversation* — which
  forbids [setup-clinical-skills](../../setup-clinical-skills/SKILL.md)'s *Confirm, then write*
  step, where the clinician confirms the model by reading his own quoted sentences back. **Showing an author his own words is
  not disclosure**, and §9 says that confirmation is the only verification a voice model has. A rule
  that forbade the one check would have left the model unverifiable and looked like caution.
- **Ask before reading, and say what will be read.** A clinician handing over eight documents has
  agreed to a voice model, not to a general read of his writing.

### The export offer comes after the writing-sample ask

**Writing samples come first.** Ask for the existing pieces above; a chat export is then **offered as an
enhancement** rather than a replacement or a precondition. Name the option broadly — **ChatGPT,
Claude, Grok**, Gemini, Copilot, or another assistant — because the clinician may have unwatched
writing in any of them. Name the cost beside it: this repository reads ChatGPT directly; another
format needs a converter following [voice-corpus.md](voice-corpus.md). An export is more evidence,
not permission to make the skippable voice-model step mandatory.

**An export takes two yeses because its contents were not selected.** With writing samples,
selection is
the consent: the clinician knows which file was handed over. With an export, neither the clinician
nor the reader has reviewed the container. Stage consent on the seam the tool already provides:

1. The **first yes** permits copying the export under `scratch/` and running the **counts-only run**.
   Show the conversation and message populations, classes, unread remainder, dated span, and
   undated count. No corpus text is shown to a reader or printed in this stage.
2. Put those **real figures** in front of the clinician. The **second yes** permits reading corpus
   text, using `--show`, quoting into `scratch/voice-model.md`, and building observations. A no stops
   the reading; record it in the profile rather than treating the first yes as blanket consent.

If there is no converter for that vendor, the honest fallback is **ten named conversations** read
as ordinary writing samples under the consent rules above. State the bound beside the result. A
bounded sample may support a writing-sample-grade model; it must never be described as reading the
export.

**The export does not settle register coverage.** A prompt, a pasted paper, and prose written to a
reader can share one message shape, so the register remains a reading. Fold the accepted material
into the model, recalculate coverage by register and source, then make a **coverage-driven second
ask** in plain language for whatever is still thin. Ask for patient explanations if register 2 is
thin, clinical reasoning if register 1 is thin, or writing that argues a position if register 3 is
thin. Coverage closes the loop; the size of the export does not.

---

## 4. Reading a sample into a model

Per sample, per register, and **every observation carries a quote from the sample it came from**.
An observation with no quote is a guess about the writing rather than a reading of it.

1. **Sentence rhythm.** The length distribution, and where the short sentence lands. Most people
   who write with force have a long-then-short pattern, and the short sentence is where the
   position gets taken. Record the pattern, not the average.
2. **Where the weight falls.** Does the clause carrying the claim open the sentence or close it. A
   writer who front-loads the verdict and explains afterwards sounds nothing like one who builds to
   it, and both satisfy §11's *first person and decisive*.
3. **Lexicon that is his.** Words a competent stranger in the same field would not have reached
   for. **Separate these from field jargon** — everyone writes `discriminator` and `sequelae`, and
   the diagnostic words are the ones that are not owed to the specialty.
4. **The characteristic move.** How a paragraph opens, how an argument closes, how a concession is
   made. This is where warrior, stoic and philosopher become observable rather than asserted:
   writing that states a position and then names what it costs, rather than hedging the position
   until it costs nothing.
5. **How uncertainty is carried.** §11's *name the inconsistency instead of resolving it silently*
   is the mechanical trace of this. The register is what it sounds like — a bounded statement, a
   stated ignorance, a hedge, a question asked out loud.
6. **How humor is built, and where it sits.** §11 says dry, occasionally funny, never at the
   patient's expense. Record the construction: understatement, an incongruous register shift, a
   flat statement of an absurd fact. And record its position, because humor in a `Plan:` and humor
   in an `Assessment` are different decisions.
7. **What he never does.** The absences, and they are frequently more diagnostic than anything
   present. No exclamation points, no rhetorical questions, never opens on a definition, never
   closes on a summary — whichever of those the samples actually show.
8. **The invoked source and what it spends.** <!-- voice-model-scan: invoked-source --> Per invoked source, record the domain it draws on and
   the property that carries the claim. The domain is whatever the writer has lived, so it stays
   open rather than being selected from an enumeration.

### The two-sample rule

**A feature goes in the model when two samples show it. One occurrence is a sample-ism.**

That is [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s discipline
arriving here, and this repo has generalized from what it had open often enough to know the shape.
A striking feature seen once is recorded under **Seen once** — kept, because deleting it means the
next build re-derives it from nothing, and quarantined, because it is not yet a rule.

---

## 5. The discriminating pair — what makes the model checkable

**For each register the model carries at least two pairs.** A pair is:

- **Generic** — the sentence a competent stranger writes to make the same claim. Composed by the
  build.
- **His** — the sentence as the sample actually writes it. **Quoted, never invented.**

A pair is the whole reason this file exists. *Decisive*, *unsentimental* and *warrior* are
descriptions any draft can be argued to satisfy, which is exactly what happened to §11. **Two
sentences side by side make the difference visible and make a draft checkable against it** — read
the draft's sentence, ask which half of the pair it resembles, and the answer is not a matter of
taste.

**The `his` half is quoted, and that is what keeps the model honest.** A pair whose second half was
written by the build is the build grading its own imitation, which is
[ADR 0001](../../../docs/adr/0001-fixture-asserts-on-named-findings.md)'s reasoning: a report by
the pass that produced it is a baseline, not a verification.

### The paired version — where both halves are attested

**Look for two versions of one document, because a corpus that has them carries its own control
group.** A draft and a cleaned-up draft, a delivery script and a prose reflow, a `Mark 2`. The diff
between them is the strongest pair available: **same author, same claim, same audience**, one
distinctive and one not — so the generic half is evidence rather than the build's guess at what a
stranger would write.

**This was not predicted; it was found by running the method, and the first corpus it ran on held
three of them.** In one, the cleaned draft of a public-safety talk replaced a line establishing the
speaker's standing with a correct, complete and entirely anonymous sentence — **deleting the most
characteristic line in the document.** That is #213's whole finding, committed on the author's own
file, before any model existed to get it wrong.

**So a smoothing pass is the adversary this file is written against, and a paired document is a
recording of one.** Where the samples contain a pair, build the register-defining pairs from it
first.

---

## 6. The trap — samples teach how he talks, not what he got wrong

His submitted corpus carries real mechanical defects, and **[style.md](style.md) §12 is the list —
it is deliberately not restated here.** A list copied into a second file is a list that goes stale
in one of them, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143),
and §12 is where a reader of the house style will already be looking.

**A model built by naive imitation reproduces them, because they are as characteristic as anything
else in the text.** A defect and a trait are both *things this writer's documents contain*, and
nothing in a frequency count separates them.

So the build does two things:

- **Every mechanical defect observed goes into the model under `Seen in the samples, never
  reproduce`.** The observation is kept rather than dropped — dropping it means the next build
  re-derives it as a feature — and it is filed as a defect, so the record carries its own verdict.
- **Where the line between a defect and a trait is not obvious, it goes to the clinician.** A
  sentence fragment, a comma splice, an idiosyncratic capitalization: each of those is register in
  one writer and a slip in another, and the build does not get to rule on it. §12's list is the
  settled part. **Anything not on it is a question rather than a finding.**

### The mirror of the trap — a sample somebody else helped write

**A sample may be co-written, and a model built from one imitates the co-author.** §12's trap is
reproducing the author's errors; this is reproducing a stranger's competence, and it is harder to
see because the result reads *better* rather than worse.

**The tell is a document that is markedly more generic than its neighbors** — reaching for a
figure the rest of the corpus never uses, running longer sentences with fewer of the author's
constructions in them, or losing the lexicon that identifies him. It is the smoothed half of §5's
pair arriving on its own, with no raw version beside it to prove what was taken out.

**Ask rather than infer, and exclude while asking.** A suspected sample is dropped from every
feature count until the clinician says, because a co-written document averaged into a model moves
every observation in it toward the mean — which is the direction the model exists to move away
from. Record in the model that it was excluded and why, so the answer can put it back.

### Damping — the answer that came back, and the correction that mattered more

**The first time this was asked, the answer was neither yes nor no.** Two documents were held out as
possibly co-written. They were the author's own, damped on purpose, with a reason he stated: he is
intense, he is often misunderstood, and he had used an assistant to **tame himself** for readers he
expected to misread him.

**That was read as a register to model, and the author corrected it within the hour.** The reading
was *he damps for academic audiences, so a graded paper takes the damped setting.* His answer:
*"i don't want this to be tame because that is not me, those were outliers … i am who i am and i
make no apology for it."*

> **The default is full voice. Damping is not a register — it is what happened to two documents, and
> their author disowns the result.**

**What survives the correction is the distinction, which is the useful half.** Damping removes
**volume**; a smoothing pass removes **identity**; those are different failures. **What does not
survive is treating a damped sample as a target.**

**Intensity is only ever reduced against a constraint the author names**, and a real constraint is
specific and carries its own floor. The worked case is one clause — *keep the edge, not the
profanity*, against a religious university — where the author named the subtraction and stated the
limit in the same breath. **That is one thing removed with an explicit floor under it, and it is the
opposite of a general instruction to soften.** An inferred constraint is not a constraint; ask.

**The damped documents stay in the corpus on the other side of the ledger.** They are the **generic
half** of §5's pairs — the competent stranger's version, written by the author himself, which is
better evidence than a generic half the build composed. That is the one place a damped sample
belongs, and it is the opposite of the role the first reading gave it.

**The failure this subsection exists to prevent runs one way and is the worse one.** A model that
treats damping as a register produces a tame draft **and can cite the author's own corpus in its
defense** — which is harder to argue with than a flat draft that has no defense at all. #213 was
filed because a run read as a competent stranger; a rule licensing that from the author's own files
would have closed the ticket by institutionalizing it.

---

## 7. Partial coverage is declared, never generalized

**Where a register has fewer than two samples, the model says so for that register**, and a run
declares **that register** unmodeled in the `PROPOSED` block rather than the whole voice and rather
than nothing.

Register 3 is the one this will happen to, and it is the register #213 is about — so a model that
quietly averaged three MDMs into a claim about how the clinician argues would be answering the
ticket with the very thing the ticket says is missing.

**Partial coverage reading as complete is this repo's most repeated defect** — a scanner reporting
zero because it could not parse the shape, a tracker sweep of 9 tickets in 39 reading as a sweep.
A voice model is the same instrument: it produces confident prose either way.

---

## 8. What the built model looks like

`scratch/voice-model.md`. The headings are fixed, so a run can find its way and so a rebuild diffs
against the last one:

```markdown
# Voice model — <clinician>

Built <date>. Sources: <n supplied samples>, <n export conversations>.

## Constraints on the setting     <- §6 damping: institution, faculty reader, audience
## Coverage
| Register | Coverage | Source |
| --- | --- | --- |
| 1 — clinical argument | <n or unmodeled> | <supplied samples / assistant export / both> |
| 2 — spoken patient education | <n or unmodeled> | <supplied samples / assistant export / both> |
| 3 — reflective and argumentative prose | <n or unmodeled> | <supplied samples / assistant export / both> |

## Sample index
| File or conversation | Register | Graded work? | Date written | Source |   <- exclusions carry why

## Register 1 — clinical argument
### Observations            <- each with its quote, and the samples it appears in
### Discriminating pairs     <- generic and his, at least two
### Coverage                 <- n samples, or "unmodeled, fewer than two samples"

## Register 2 — spoken patient education
    ... the same three subheadings

## Register 3 — reflective and argumentative prose
    ... the same three subheadings

## Seen once                              <- quarantined, not rules
## Seen in the samples, never reproduce   <- the §6 defect list, with quotes
## Open questions for the clinician       <- the §6 defect-or-trait calls

## Two-tier findings
| Feature | Chat | Graded | Direction | Source |
| --- | --- | --- | --- | --- |
| <feature> | <measure> | <measure> | <intensifies / survives / declines / stripped> | <cuts> |

Withheld findings: <n>
```

Every observation and finding carries its source: supplied file or export conversation, date where
available, and the measurement or quotation it rests on. For a two-tier row, publish a direction
only when the declared cuts agree; otherwise withhold it and increase the count even when that
count is zero. **A finding is a floor, not a target.** It can forbid stripping a measured feature
from graded prose; it never licenses amplifying the feature to imitate a percentage.

**Where a run reads it.** [practicum-case-study](../../practicum-case-study/SKILL.md) step 5, before drafting, and step 9, where the
draft is read back against the discriminating pairs.

**Where there is no model.** A run that finds no `scratch/voice-model.md` writes in the §11
mechanics and **says in the `PROPOSED` block that the voice is unmodeled**, rather than claiming a
register it was not given. That rule predates this file and it survives it. What changes is that
the declaration is now per register, on §7's terms.

**A run does not stop to collect samples mid-draft.** Building a model is
[setup-clinical-skills](../../setup-clinical-skills/SKILL.md) step 8's job, it needs the clinician
present, and a case study is usually being written against a deadline. So the run declares the gap
and names the skill that closes it, and the document goes out sounding like a stranger **with that
fact attached** rather than sounding like a stranger silently.

---

## 9. What a voice model cannot reach

**It does not outrank a graded axis.** Voice is not a rubric line — [rubric.md](rubric.md) scores
clinical judgment at 70 of 100 and APA format at 5, and none of the ten criteria is *sounds like
the author*. Where the register and a rubric criterion pull apart, the rubric wins: a
better-sounding sentence that demotes the correctly-ranked differential has spent graded points on
a preference.

**It cannot be verified by the run that built it.** Only the clinician can say whether it sounds
like him, and *"this reads like you"* from the pass that wrote it is worth nothing. What §5's pairs
check is consistency with the samples, which is a weaker thing than identification and must not be
read as one.

**Samples are a snapshot.** A register moves, and a model built from eight documents describes the
writer those documents had. It carries its build date for that reason.

**It cannot make a clinical argument correct.** Everything in [practicum-case-study](../../practicum-case-study/SKILL.md)'s *Every
clinical claim is looked up, never recalled* binds a document written in a perfect register exactly
as hard.
