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

### Damping — the answer that came back, and it is not the one the question expected

**The first time this was asked, the answer was neither yes nor no.** Two documents were held out as
possibly co-written. They were the author's own, damped on purpose, with a reason he stated: he is
intense, he is often misunderstood, and he had used an assistant to **tame himself** for a reader he
expected to misread him.

**So a quieter document is not automatically a document that lost its voice.** It may be its author
choosing a lower setting, and **a model that reads damping as absence will restore intensity its
author deliberately removed** — putting the volume back up for exactly the audience he turned it
down for. That is a worse failure than a flat draft, because it is confident and it is his name on
it.

**Damping is not erasure, and telling them apart is what §5's pairs are for.** What an author's own
damping removes is **volume**. What a smoothing pass removes is **identity** — and the worked case
is a line that was neither loud nor coarse, merely his, and went anyway.

> **Damp the intensity to the audience. Never damp the identity.**

**This is the resolution of #213 rather than a footnote to it.** A run read as a competent stranger,
and the fix is not more intensity — a graded paper may be precisely the context its author would
damp for. **The fix is the identity**, which no audience ever required him to remove.

**So the model records the setting as well as the register.** Where an author damps, ask what for,
and write the constraint down: an institution, a faculty reader, a professional register, a reader
who has misread them before. **A constraint is per-account and it is a fact about the audience
rather than about the writing** — it belongs beside the register in `scratch/voice-model.md`, and it
binds every document written into that context.

**Its most useful samples may be the damped ones.** They are the closest thing the corpus holds to
the target document — the author writing at the setting the deliverable wants — which is the
opposite of the liability they first looked like.

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

Built <date> from <n> samples. Registers covered: 1 (n=<x>), 2 (n=<y>), 3 (n=<z>).

## Constraints on the setting     <- §6 damping: institution, faculty reader, audience
## Sample index
| File | Register | Graded work? | Date written |   <- and any excluded under §6, with why

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
```

**Where a run reads it.** [SKILL.md](../SKILL.md) step 4, before drafting, and step 8, where the
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

**It cannot make a clinical argument correct.** Everything in [SKILL.md](../SKILL.md)'s *Every
clinical claim is looked up, never recalled* binds a document written in a perfect register exactly
as hard.
