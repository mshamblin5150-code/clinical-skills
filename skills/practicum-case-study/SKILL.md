---
name: practicum-case-study
description: Turn a practicum case study's faculty material into a finished, APA-formatted graded submission — full workup, MDM, plan, prescriptions, patient education and references — delivered as a .docx. Use when the clinician hands over a course case study, a module video's intake data, a "case study" Word document, or asks to write up a graded case for a nursing practicum discussion board.
---

The input is **faculty material for a graded case study** — an intake block transcribed from a
module video, usually with the clinician's own rough differential and plan underneath it. The
output is the finished academic document that gets submitted, plus the `.docx` it is submitted as.

This is **not** [clinical-note](../clinical-note/SKILL.md), and the difference is not the format.
A clinical note documents a patient the clinician saw. A case study answers a faculty prompt about
a patient nobody saw, against a published rubric, in a course. **The single rule that inverts is
the most important sentence in this file:**

> **In a note, silence in the shorthand means normal. In a case study, silence in the faculty
> material means unknown, and unknown becomes an order.**

`clinical-note` fills a missing social history with an unremarkable value and discloses it. Here,
a missing social history is written out loud as missing and then *ordered* —
`Update allergies, height, weight, social hx, PMH, past surgical hx, family medical hx`. That line
appears in nearly every graded submission in the clinician's corpus and has never cost a point.
**Filling it would be inventing findings in a document whose entire subject is clinical
reasoning.** Standing rule 2's vitals exception does not reach here: the faculty material states
the vitals it wants stated, and a vital it omits is one the case is not about.

**Where the work goes.** `output/case-studies/`, never the repo root and never a tracked
directory — standing rule 1, and a pre-commit hook enforces it. Write the Markdown and the `.docx`
side by side under the same stem. Name files by course, module and date: `nur5144-m1-2026-08-18.md`.
A filename carries no patient name.

## What it is graded by

[reference/rubric.md](reference/rubric.md) holds the Canvas spec in full — the required components,
the 100-point rubric, and the 21 guideline bodies. Read it before drafting. Three things from it
decide how the document is written:

**Clinical judgment carries 70 of the 100 points.** APA format is 5 and guideline integration is
5. This is why the ordering of a differential matters more than the tidiness of a citation, and it
is not a guess about the grader — it is the rubric's own weighting.

**Three to five prioritized differentials is the stated cap, and the corpus exceeds it routinely
without ever being docked.** Nine, eleven and thirteen entries have each scored 98% or better.
Length is not graded. **`Prioritized` is graded**, and it is where the corpus has actually lost
points. See *Ordering is the graded axis* below.

**ICD-10 is optional here**, unlike in a note. The spec marks it optional and the corpus is
inconsistent. Write it anyway — it is a strength, and [icd10-cpt](../icd10-cpt/SKILL.md) with
`tools/icd10_lookup.py` is how a code gets verified rather than recalled.

**And every code carries its official descriptor, spelled out, wherever it appears.** This is
`icd10-cpt`'s descriptor discipline and it binds here for a sharper reason than it does there: a
coding worksheet is read by somebody coding, and a case study is read by a grader with no code book
open. `N72` is not information. `N72, inflammatory disease of cervix uteri` is. **A bare code number
is a claim the reader cannot check**, which is the one thing this repo does not ship.

**Three places the first run left uncoded, all of them errors.** The favored differential entries
were coded and these were not:

- **The most likely clinical diagnosis.** It is the single most important line in the document and
  it was the one line with no code on it.
- **An entry listed only to show it is excluded.** Listing the exclusion is right, and it is graded
  — see *Ordering is the graded axis*. Leaving it uncoded makes it decoration.
- **Anything in the Plan that codes**, where the plan item is itself a diagnosis or a screening.

**Ruled 2026-08-18.** If it names a diagnosis, it carries a code and a descriptor.

## Scope

**Starts at the faculty material and stops before the discussion board replies.** The peer critique
is a separate deliverable with its own headings and its own word count; it is described at the
bottom of [reference/rubric.md](reference/rubric.md) and this skill does not write it.

## The document

[reference/style.md](reference/style.md) holds the house style, derived from ten graded and
returned submissions. It is the authority on voice, on section shapes and on the normalizations.
The skeleton, in order:

1. **Sanity Check** — four confirmations then a closer. Always first, before any clinical content.
2. **Intake block** — the faculty material, transcribed and cleaned, never invented.
3. **Assessment:** — a container heading. Its body is optional and holds pre-differential
   reasoning that belongs to no single diagnosis: arithmetic the case data permit, teaching points
   on what the exam must include, and any conflict in the source data named out loud.
4. **Differential Diagnoses** — a numbered list, ranked, ICD-10 pinned with a hyphen.
5. **Most Likely Clinical Diagnosis** — with the discriminator attached, not bare.
6. **MDM** — one entry per differential, each stating what in *this case* puts it in or out.
7. **Plan:** — imperative orders.
8. **Patient Education:** — spoken, second person.
9. **Rx:** — one table per drug, fixed shape.
10. **Signed by:** — name, credentials, timestamp.
11. **References** — APA 7.

**The differential, the MDM, the Plan and the Patient Education are numbered lists. Never
bullets.** His ruling, 2026-08-18, and it is not a formatting preference. A grader counting
*"three to five prioritized differentials"* counts numerals, and an MDM entry that cannot be
referred to by number cannot be pointed at in a critique. The four sections are a **correspondence**
— differential 3 has MDM entry 3, and a plan item exists because some numbered entry called for it.
Bullets destroy that, and the corpus's own worst list mixes both markers in one list.

Everything else stays as it is: the intake block is a table, the Assessment runs as prose, and the
prescriptions are tables.

**Three modes, and the faculty material picks one.** A **full workup** is the skeleton end to end.
**Q&A** is what to write when the faculty pose explicit questions: restate each question as a
bullet and answer it underneath in prose. **Discussion** adds a narrative section for reasoning
that does not fit the differential-by-differential frame. A mode is not a quality tier — the Q&A
submissions in the corpus scored as well as the full workups, and one scored 100% with no plan, no
prescriptions, no differential list and a single reference, because it answered the four questions
it was asked and nothing else. **Answer the prompt that was set, not the prompt the skeleton
expects.**

## Ordering is the graded axis

The sharpest lesson in the corpus cost five points on a submission where nothing was missing.
Ectopic pregnancy *was* on the differential, *was* labeled `must exclude`, and *was* worked up with
a pregnancy test in the plan. It was listed eleventh of thirteen, appendicitis was named most
likely, and the grader wrote that ectopic needed to be number one.

**Membership is not enough. A differential nobody can see the ranking of is a ranking that was not
made.** So:

- The list is numbered, and `1.` is the favored entry.
- **Any patient of childbearing age with abdominal or pelvic pain gets pregnancy-related
  emergencies ranked first**, until imaging or a test excludes them — and when something in the
  faculty material already excludes one, say which line does it rather than dropping the entry.
- Rank on *what would kill or maim first*, then on likelihood. A rare diagnosis is argued down in
  the MDM with an explicit trigger that would promote it, never quietly omitted.

**Where the patient meets most of the published criteria for a diagnosis, that diagnosis leads.**
It is number one on the differential and it is the most likely clinical diagnosis. **Ruled
2026-08-18, against a run that did the opposite** — a patient meeting two of three minimum criteria
and four of five additional criteria for pelvic inflammatory disease was written up with cervicitis
ranked first, on the strength of an anatomic argument that the pregnancy made ascending infection
unlikely.

**The mechanism was interesting and it was the wrong output.** A criteria set is the thing the
grader, the guideline and the chart all agree on; an anatomic plausibility argument is a reason the
criteria might be misleading in this case. **The argument belongs in the MDM entry, underneath the
diagnosis it qualifies. It does not get to demote the diagnosis it argues about.** A reader who sees
the criteria met and the diagnosis ranked second has to reconstruct why, and a grader will read it
as the criteria having been missed.

## Every clinical claim is looked up, never recalled

This is the [icd10-cpt](../icd10-cpt/SKILL.md) anchor discipline applied to a graded paper. A dose,
a regimen, a threshold, a citation year and an edition are all things a fluent guess produces
convincingly and wrongly.

**The clinician usually supplies the evidence.** A case study arrives with a companion document —
the UpToDate topics pasted in full. That is the source, and it is read rather than remembered:

```bash
python tools/docx_read.py "<the references document>" --normalize > scratch/evidence.txt
```

**`--normalize` is not optional on an UpToDate paste.** The rendered pages are salted with
homoglyphs — a Cyrillic `с` inside `cervicitis`, a Greek `ο` inside `infection` — so a search for a
word the page visibly contains returns nothing and looks like a settled negative. `tools/docx_read.py`
folds them back.

**Every source is cited in the body, not only listed at the end.** APA 7 in-text citation, author
and year, on the sentence the source supports — and a reference-list entry that is nowhere cited in
the body comes out of the list. His ruling, 2026-08-18. A reference list is a bibliography of what
the argument rests on; a list of things that were read is a different document, and the rubric's
*Integration of Evidence-Based Guidelines* line is scored on integration rather than on reading.

Where the companion document does not cover a claim, the repo's own sheets do:
`reference/guidelines-uspstf.md` for a screening or preventive item, `reference/thresholds/` for a
numeric decision point, `reference/guidelines-catalog.md` and `tools/guidelines_search.py` for the
society corpus. **A missing row in a threshold sheet is not a negative finding**; a missing USPSTF
row is one about the USPSTF, and never a statement that the item is unindicated.

**What none of that reaches gets researched, not deferred.** A claim with no source in hand is
**not** written into the `PROPOSED` block with `verify this` against it and handed back — that was
the first run's behavior and it is the clinician's ruling of 2026-08-18 that it is wrong. *"That
needs to be fanned out to a research agent."* The reasoning is that a graded paper is where an
unsourced claim costs points, and handing the clinician a list of things to look up moves the work
rather than doing it.

So: spawn a research subagent per unsourced claim, in parallel. What it must return:

- **A reputable source.** A society guideline, a peer-reviewed paper, a government body, or a
  tertiary clinical reference. Not a content farm and not a summary of a summary.
- **A full APA 7 reference**, which goes into the reference list and gets cited in the body like any
  other.
- **The claim restated in the source's own terms**, so a claim the source does not actually support
  fails visibly rather than acquiring a citation.

**Recency: within two years is the target, within five is ordinarily expected, and an older source
stands where nothing newer exists.** His ruling, amended 2026-08-18 after the first version cut a
correct claim for being old.

**What the rule refuses is a claim that is old *and* superseded.** The first version conflated that
with old, and the two are not the same thing:

- **A society guideline is dated by the guideline, not by what it cites.** A current IDSA or KDIGO
  document resting on a 2011 trial is a current source. `reference/guidelines-catalog.md` spans 2009
  to 2026 and every document in it is in force — a rule that refused a 2013 KDIGO threshold on its
  date would refuse *the* threshold, not an outdated one.
- **Where nothing newer exists, the older source is the evidence.** The run must have looked, must
  say in the `PROPOSED` block that it looked, and the sentence carrying the citation says the
  evidence is the most recent available on that point. The citation's age stays visible.

**The worked case, because the rule was wrong against a real claim rather than in the abstract.** A
run researched whether the gravid uterus displaces the appendix in pregnancy. The best primary
evidence refuting it is a 2018 direct-observation study; the teaching it refutes is a **1932**
barium-enema study that has never been replicated, because replicating it means irradiating fetuses.
**The five-year rule refused the 2018 refutation and would have left the 1932 teaching standing by
default** — a recency filter returning the least recent answer available. The run cut the sentence,
which was correct under the rule as written and wrong.

[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215) carries the reasoning;
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) is where this rule and the
fan-out that applies it get built together, because a rule split from its enforcement is how the two
drift apart.

**A claim that survives all that and is still unsourced does not go in the body.** It goes in the
`PROPOSED` block, and if it is a number the clinician would act on, it comes out of the document
entirely. Fanning out replaces the deferral for claims that *can* be sourced; it is not a license to
assert the ones that cannot.

## Tiers

Standing rule 2 in this skill's terms. Every line is one of three things, and the third is the
inversion at the top of this file:

- **GIVEN** — in the faculty material. Transcribed, its typos fixed, its content untouched.
- **DERIVED** — computed from given data with the arithmetic shown on the page. eGFR, anion gap,
  BMI, an EDC by Naegele, absolute neutrophil count from the white count and the differential.
  **Show the formula**, always — it is a graded demonstration of reasoning, not a lookup.
- **ORDERED** — what a note would have filled. The faculty material's silence is stated as silence
  and converted into an order or a test. Nothing is filled.

**No exam finding, symptom, vital or result is ever invented here.** A note may fill a blood
pressure because a box demands one; a case study has no box, and a fabricated finding changes the
answer to the question being graded.

Standing rule 3 still binds: a `PROPOSED (verify before use)` block sits **after** the References,
outside the document body, listing every clinical claim this skill contributed that the clinician's
draft did not already contain — each differential added, each code, each drug, each dose. It is
what he reads before submitting, and it is deleted from the copy that goes to Canvas.

## Credentials — two strings in one document, and that is correct

| Where | String |
| --- | --- |
| The `Rx:` block | `FNP-C, CEN, TCRN` |
| The `Signed by:` line | `RN, CEN, TCRN` |

The prescription is written in the prescribing nurse-practitioner role the case study puts him in.
The signature is him attesting as himself, and it is the same string every real clinical note takes
in [clinical-note](../clinical-note/SKILL.md), [batch-shift](../batch-shift/SKILL.md) and Medatrax.
Two strings in one document is settled, not a defect. **The name is not in this file** — read it
from `scratch/medatrax-profile.md` or ask.

## Voice

**The document has to sound like the person submitting it, and the first run did not.** His words:
*"this is missing my — I don't know how to say it — way of speaking."*

[reference/style.md](reference/style.md) §11 captures the mechanics: first person and decisive, show
the arithmetic, name the inconsistency, reason on physiology rather than lists, argue rarity down
instead of ignoring it, dry humor never at the patient's expense. **Those are true and they are not
sufficient.** A run can satisfy every one of them and still read as a competent stranger, which is
what happened.

**The register he named is warrior, stoic, philosopher.** That is the thing to build toward: writing
that takes a position and accepts its cost, that is unsentimental about outcomes without being cold
about people, and that reaches for a principle rather than a protocol when the case is genuinely
hard. It is not decoration on top of the clinical content — it is *how the reasoning is carried*,
which is why a checklist of tics cannot reproduce it.

**This is not built yet.** It needs writing samples from the clinician, and the mechanism is
[reference/voice.md](reference/voice.md), which does not exist until there are samples to build it
from. Until it does, a run writes in the §11 mechanics and **says in the `PROPOSED` block that the
voice is unmodeled**, rather than claiming a register it has not been given.

**And this generalizes past one clinician.** Any user of this skill has a way of writing that a
grader already associates with them. The mechanism should take samples from whoever is using it and
build their `voice.md`, not his. A skill that hard-codes one person's register is a skill that makes
everyone else sound like him.

## Conventions

**Punctuation follows [clinical-note](../clinical-note/SKILL.md).** No middot as a separator, no em
dash, no arrow: comma, colon, and the therefore sign `∴`. A value pinned to its label takes a
hyphen — `Cervicitis - N72`. The colon keeps every position where it opens a clause.

**American English, always** — [standing rule 4](../../AGENTS.md). `tools/spelling_scan.py` holds
the table with a command in front of it.

**Normalize what the corpus varies.** Every one of these drifts across the ten submissions and
should be fixed to one form:

| Varies | Write |
| --- | --- |
| `Differential Dx` / `DDx:` / `DDX:` | `Differential Diagnoses` |
| `Most Likely Clinical Dx:` / `DX:` | `Most Likely Clinical Diagnosis:` |
| `MDM` / `MDM:` | `MDM:` |
| `RX:` | `Rx:` |
| numbered and bulleted markers mixed in one list | one or the other, never both |
| `– Confirmed` / `– proceed` / `– Proceed` | `- confirmed` / `- proceed` |
| ICD-10 present in some sections and absent in others | always present |

**Abbreviations are free in the Plan and the MDM** — `s/p`, `f/u`, `RTC`, `DC` — and **never
appear in Patient Education**, which is spoken to the patient.

## Steps

### 1. Read the faculty material

```bash
python tools/docx_read.py "<the case study document>"
```

Transcribe the intake block. **Fix the typos and change nothing else** — the corpus arrives with
`pelivic`, `progressivly`, `dyspaneuria`, and a value written `2029` where `2019` was meant in a
passage about the importance of accurate dating. A misspelling is corrected silently. **A value
that cannot be reconciled is named out loud in the Assessment**, never corrected silently and never
resolved by picking the likelier one in silence.

Note which mode the material sets, and note the questions it asks — the corpus's `Things to
complete for this case study` list is the assignment, and each item on it must be answerable by
pointing at a section.

### 2. Read the evidence

`--normalize`, as above. Index it by topic before drafting, so the MDM cites what is in hand rather
than what sounds right.

### 3. Write the Sanity Check

Four confirmations, one per line, each ending `- confirmed`, then `Sanity Check completed -
proceed`. The four are the module or case number, which video, the hyperlink, and a one-line
description of the case.

### 4. Draft the body

In skeleton order, in his voice — [reference/style.md](reference/style.md) is the authority and the
part that matters most is that the voice is **first person and decisive**. `I would`, `I will`,
`I'm going to stop`. Never *the provider should consider*.

Two things every MDM entry carries: **the discriminator** — what in this case puts the diagnosis in
or out, not a textbook summary of the disease — and **a citation**. Ruled-out entries end on the
verdict, and the strongest form in the corpus promotes the verdict to the entry's own header line
with the reasoning underneath.

### 5. Write the prescriptions

The fixed six-row table in [reference/style.md](reference/style.md), one per drug, including the
home medications that are being continued unchanged. The patient cell is a placeholder and the date
of birth is literally `x-x-xxx` — **a case study prescription carries no identifiers**. Sig spells
the numbers out and ends `for <indication>`. Held orders say so in the drug row.

### 6. Fix the references

APA 7, roughly alphabetical. Then walk the defect list, every time:

| Defect | Fix |
| --- | --- |
| `Links to an external site.` welded to a URL | strip it — it is a Canvas paste artifact |
| Retrieval year behind the exam year | the retrieval date must be on or after the exam date |
| In-text year not matching the reference list year | reconcile |
| Two entries with the same author and year and no `a`/`b` | disambiguate, in both places |
| A missing space in a date | `February 19, 2026` |
| A misspelled month | check every one |

**A citation year is looked up, never recalled.** UpToDate revises topics continuously and the same
topic appears in one clinician's corpus under three different years. The companion document states
each topic's own revision date — use it.

### 7. Emit the document

Write the Markdown to `output/case-studies/`, then render it:

```bash
python tools/docx_write.py output/case-studies/<stem>.md output/case-studies/<stem>.docx
```

APA 7 page setup — Times New Roman 12 pt, double spaced, one inch margins, hanging indents on the
reference list — is applied by the renderer. **Strip the `PROPOSED` block from the `.docx`**, or
render from a copy that does not carry it: it is for the clinician, not for the grader.

### 8. Check

Against this list, by eye — none of it is mechanical:

- Does every item on the faculty's own to-do list have a section that answers it?
- Is the differential **numbered**, and is `1.` defensible as the thing that would kill first?
- Does every MDM entry name a discriminator from *this* case, and carry a citation?
- Does every drug in the Plan have a prescription table, and every table a `Sig` ending in an
  indication?
- Is the Patient Education spoken, jargon-free, and does it end on the follow-up interval?
- Does any number in the body rest on recall rather than on a source in hand?
- Is the `PROPOSED` block complete, and is it out of the `.docx`?

**A rendered `.docx` is not a checked document.** `tools/docx_write.py` guarantees the file opens
and the reference list hangs. It cannot read a differential.
