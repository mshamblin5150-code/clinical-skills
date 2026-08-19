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
5. This is why the skill spends its length on the ordering of a differential rather than on
citation hygiene, and it is not a guess about the grader — it is the rubric's own published
weighting.

**It is a reason to spend length. It is not a reason to skip the reference walk.** This sentence
used to read *the ordering of a differential matters more than the tidiness of a citation*, which a
run could read as permission to hand back a document with known reference-list defects still in it.
**Ruled 2026-08-18, in the clinician's words:** *ordering the differential is very important, but
that shouldn't take the place of tidiness.* So step 7 runs on every document, and a defect it finds
is **fixed before the document is handed over** rather than listed in `PROPOSED` for him to fix by
hand. [reference/apa7.md](reference/apa7.md) is the written rule it runs against — without one,
*"fix the reference list"* is a wish rather than a check.

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
returned submissions. It is the authority on the voice's **mechanics**, on section shapes and on
the normalizations; [reference/voice.md](reference/voice.md) is the method for the **register**,
which §11's mechanics turned out not to reach. [reference/apa7.md](reference/apa7.md) is the
authority on the reference list.
**Every section below is written, every time** — see *Three modes, and none of them subtracts a
section* under it. The skeleton, in order:

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
9. **Rx:** — one table per drug, fixed shape, each with the pharmacologic prose block under it.
10. **Faculty Questions:** — present only where the material poses them, and it answers them
    rather than replacing anything above.
11. **Signed by:** — name, credentials, timestamp.
12. **References** — APA 7, alphabetized. [reference/apa7.md](reference/apa7.md).

**The differential, the MDM, the Plan and the Patient Education are numbered lists. Never
bullets.** His ruling, 2026-08-18, and it is not a formatting preference. A grader counting
*"three to five prioritized differentials"* counts numerals, and an MDM entry that cannot be
referred to by number cannot be pointed at in a critique. The four sections are a **correspondence**
— differential 3 has MDM entry 3, and a plan item exists because some numbered entry called for it.
Bullets destroy that, and the corpus's own worst list mixes both markers in one list.

Everything else stays as it is: the intake block is a table, the Assessment runs as prose, and the
prescriptions are tables.

### Three modes, and none of them subtracts a section

**The skeleton is written in full, every time. Ruled 2026-08-18, reversing what this file used to
say.** Where the faculty pose explicit questions, they are answered **in addition to** the
skeleton and never instead of it: restate each question and answer it underneath in prose, under a
`Faculty Questions:` heading, and let the skeleton sections carry the rest. **Discussion** — a
narrative section for reasoning that does not fit the differential-by-differential frame — is
additive on the same terms.

**The evidence for the opposite reading is real, and it was not enough.** Two submissions in the
corpus replaced the workup with answers to the questions asked and both scored full marks; one
scored 100% with no plan, no prescriptions, no differential list and a single reference. This file
concluded from that: *answer the prompt that was set, not the prompt the skeleton expects.*

**What that conclusion missed is that the rubric scores ten criteria and a set of faculty questions
need not touch all ten.** Preventive Care and Health Promotion is 5 points, Integration of
Evidence-Based Guidelines is 5, APA Format is 5 — and four questions about a differential and a
plan ask for none of the three. **Two submissions surviving the omission is evidence that it is
survivable, not that it is right**, and a run that drops a scored section is spending fifteen points
on the clinician's behalf without being asked. A mode is still not a quality tier; what changed is
that a mode no longer subtracts sections.

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

So: spawn a research subagent per unsourced claim, in parallel. **Step 3 is the mechanism** — the
brief each agent is sent, the ledger they all write into, and the command that grades it. What one
agent must return:

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

[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215) carries the reasoning, and
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) built this rule and the
fan-out that applies it together, because a rule split from its enforcement is how the two drift
apart. `tools/research_ledger.py` is where the two meet — see step 3.

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

**The mechanism is [reference/voice.md](reference/voice.md), and it is the method rather than the
model.** It says how to ask for writing samples, how to read them into a register, and what never
to imitate. **What it builds is `scratch/voice-model.md`** — gitignored, one per clinician, built
from that clinician's own samples.

**The split is #212's rule one step out**, and it is why this skill does not ship a register in
`reference/`. A rule that only resolves against one account belongs in the profile, and a register
is that shape at its purest: it is nobody else's, it is useless to a second clinician, and shipping
his would make every other user of this skill sound like him. A model also has to **quote**, and
the quotes are the user's own work — which is [reference/style.md](reference/style.md)'s own
arrangement, distilled into `reference/` from a gitignored working file that quoted ten submissions
in full.

**The samples are collected by [setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 8**,
where the rest of this clinician's per-account configuration already lives — his ruling, 2026-08-18,
settling the one question #213 left open. [reference/voice.md](reference/voice.md) §3 is the spec
for what to ask for and §4 is how the samples are read; that step points at both rather than
restating either.

**Look in the main checkout before concluding there is no model.** `scratch/` is gitignored and a `git worktree` has none, so a model that exists can read as missing — see *Where `scratch/` actually is* in [setup-clinical-skills](../setup-clinical-skills/SKILL.md). Declaring an unmodeled voice against a model that was merely out of reach is a false declaration, not a safe default.

**Where there is genuinely no model, the run says so.** A run that finds no `scratch/voice-model.md` writes
in the §11 mechanics and **says in the `PROPOSED` block that the voice is unmodeled**, rather than
claiming a register it has not been given. **The declaration is per register**, not per document —
[reference/voice.md](reference/voice.md) §7. A model built from three MDMs and nothing else has
modeled the clinical argument and has said nothing about how this clinician argues a position,
which is the register #213 was filed about.

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

**Never write a `Case ID:` line. Ruled 2026-08-18.** It appears above the references in exactly one
submission in the corpus and nowhere else, nothing in the spec asks for it, and its absence has
never been docked. **The risk runs the other way**: a run that derived a case number from the module number
would be writing a wrong identifier onto a graded paper, which is worse than the field being
missing. The skeleton above has no such item, and this sentence is here so that omission reads as a
decision rather than an oversight.

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

### 3. Research what the evidence does not cover

**This is the fan-out, and it runs before a word of the body is drafted.** List the clinical claims
the document is going to rest on — every differential's discriminator, every threshold, every dose,
every number said out loud to the patient — and strike the ones the companion evidence, the USPSTF
table, the threshold sheets or the guideline corpus already cover. **What is left is the work of
this step**, and *What none of that reaches gets researched, not deferred* above is the rule it
applies.

**One agent per remaining claim, all of them at once.** Each gets the same brief, and the brief is
the three returns and the recency rule above — a reputable source in one of four classes, a full
APA 7 reference, and the claim restated in the source's own terms. Tell it the source classes by
name, because a returned source outside them is a finding rather than an answer.

**They all write into one ledger**, `scratch/case-study-claims.md`, one record per claim:

```
DATE: 2026-08-19

## CLAIM: A white count of 15,000 is within physiologic leukocytosis in pregnancy.
STATUS: sourced
SOURCE: peer-reviewed
REFERENCE: Abbassi-Ghanavati, M., Greer, L. G., & Cunningham, F. G. (2009). Pregnancy and
    laboratory studies. Obstetrics and Gynecology, 114(6), 1326-1331.
RESTATEMENT: The table gives a third-trimester white cell range of 5.6 to 16.9 x 10^9/L in
    normal pregnancy.
RECENCY: nothing newer - searched 2026-08-19, no later reference-range table for pregnancy exists.
```

`STATUS` is `sourced` or `unsourced`, and an `unsourced` record says on the same line what was
searched. `SOURCE` is one of `society guideline`, `peer-reviewed`, `government` or
`tertiary reference`. `RECENCY` is one of `current`, `within five`, `nothing newer` or
`guideline in force`, and the last two carry the reason after a hyphen — *the run must have looked,
and must say so.* `DATE` is the day the paper is written, and the recency rule is measured against
it rather than against the clock. A field's value may wrap onto the next line.

**The ledger is gitignored**, because `scratch/` is, and that is where a case study's working
material belongs — not in a tracked notes directory. Where the harness ships a general research
skill, borrow the fan-out from it and change that one thing: they write findings into the repo,
and a case study's working material is a patient record.

**Then grade it, and do not draft until it is clean:**

```bash
python tools/research_ledger.py scratch/case-study-claims.md
```

Exit 0 is clean, 1 names how many records failed, and **2 means it did not scan** — no file, no
records, or no `DATE` header. Re-run with `--show` to see which records, and **that output is PHI**:
read it, do not paste it. What the command checks and what it cannot are in its module docstring;
the short version is that it can see a missing field, an unexcused old reference and a restatement
that is the claim pasted back, and it **cannot** see whether the source is reputable or whether it
says what the record claims it says. **A clean scan is not a checked claim.**

**Every rule the command applies is written above, so a harness with no Python walks the ledger by
eye instead.** The command saves the reading; it is not where the rule lives. That is
`icd10-cpt`'s arrangement with `tools/specificity_scan.py`, and [AGENTS.md](../../AGENTS.md) keeps
the two classes of tool citation apart deliberately.

**Where the harness has no subagent tool, the same briefs are worked one at a time in the main
context, into the same ledger.** The mechanism is the ledger and the brief; the parallelism is a
speed property, and the grader cannot tell the difference. This settles
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s open question 1, and
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218) takes the same answer
rather than inventing a second one. **Where the harness cannot research at all** — no subagent, no
search, nothing to read — the record is written `STATUS: unsourced` with that said plainly, and the
deferral behavior is what is left: the claim goes to `PROPOSED` and, if it is a number, out of the
document. Deferral is the floor when research is impossible, never the choice when it is merely
work.

**A claim found unsourced in the middle of drafting goes back through this step**, not into the body
with `verify this` against it. That was the first run's behavior and it is what this step exists to
replace.

### 4. Write the Sanity Check

Four confirmations, one per line, each ending `- confirmed`, then `Sanity Check completed -
proceed`. The four are the module or case number, which video, the hyperlink, and a one-line
description of the case.

### 5. Draft the body

In skeleton order, in his voice — [reference/style.md](reference/style.md) is the authority and the
part that matters most is that the voice is **first person and decisive**. `I would`, `I will`,
`I'm going to stop`. Never *the provider should consider*.

**Read `scratch/voice-model.md` first, if it exists**, and write each section in the register that
section takes — the MDM, the patient education and the reflective prose are three different voices
and [reference/voice.md](reference/voice.md) §2 says which is which. Where the model declares a
register unmodeled, that section is written in the §11 mechanics and the gap is declared in
`PROPOSED`. **Where no model exists at all, this run does not stop to build one** — that needs the
clinician and his samples, it is [setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 8,
and a case study is usually being written against a deadline. Declare it and name the skill.

Two things every MDM entry carries: **the discriminator** — what in this case puts the diagnosis in
or out, not a textbook summary of the disease — and **a citation**. Ruled-out entries end on the
verdict, and the strongest form in the corpus promotes the verdict to the entry's own header line
with the reasoning underneath.

### 6. Write the prescriptions

The fixed six-row table in [reference/style.md](reference/style.md), one per drug, including the
home medications that are being continued unchanged. The patient cell is a placeholder and the date
of birth is literally `x-x-xxx` — **a case study prescription carries no identifiers**. Sig spells
the numbers out and ends `for <indication>`. Held orders say so in the drug row.

**Then a short prose block under each table**, carrying the five fields the spec's Pharmacologic
Therapy component names and the table does not: **drug class, contraindications, monitoring,
adverse effects, and the guideline that supports the choice**. One paragraph, not a second table.
**Ruled 2026-08-18.** The shape and the worked example are in
[reference/style.md](reference/style.md) §8, which is the authority on section shapes and the one
place they are written.

**Why prose rather than more rows.** The spec asks eleven fields per medication and the table
carries six, so something had to give. Eleven rows stops it looking like a prescription; nowhere
leaves a scored component answered only by accident, in whatever the Patient Education happened to
say. **The table is where the order belongs and the prose is where graded reasoning belongs**, and
the guideline citation in that block is the cheapest *Integration of Evidence-Based Guidelines*
point in the document.

**Omitting them has never cost a point, which is not the same as being safe** — it is the mode
finding again, one section down. See *Three modes, and none of them subtracts a section* above.

### 7. Fix the references

**APA 7, alphabetized — [reference/apa7.md](reference/apa7.md) is the rule, and it is checked
rather than recalled.** That sheet carries the `a`/`b` disambiguation ordering, the UpToDate entry
form, when a retrieval date belongs and when it is a defect, and the mechanics of the list itself.
An APA question it does not answer is looked up at apastyle.apa.org, never guessed.

**`Roughly alphabetical` was a description of the corpus and never the standard.** Sorted is
sorted.

**This walk is not optional and its findings are not handed back.** Ruled 2026-08-18 — see
*What it is graded by* above. Walk the defect list, every time:

| Defect | Fix |
| --- | --- |
| `Links to an external site.` welded to a URL | strip it — it is a Canvas paste artifact |
| Retrieval year behind the exam year | the retrieval date must be on or after the exam date |
| A retrieval date on a guideline, article or textbook | remove it — [apa7.md](reference/apa7.md) §4 |
| In-text year not matching the reference list year | reconcile |
| Two entries with the same author and year and no `a`/`b` | disambiguate, in both places — and the letters are assigned by **title order**, [apa7.md](reference/apa7.md) §3 |
| An UpToDate entry with the database name unitalicized | italicize it in the entry, not in the text |
| An UpToDate year that is the year it was read | use the topic's **last update** year |
| An entry in the list that is cited nowhere in the body | delete it |
| A citation in the body with no entry in the list | add it |
| A missing space in a date | `February 19, 2026` |
| A misspelled month | check every one |

**A citation year is looked up, never recalled.** UpToDate revises topics continuously and the same
topic appears in one clinician's corpus under three different years. The companion document states
each topic's own revision date — use it.

### 8. Emit the document

Write the Markdown to `output/case-studies/`, then render it:

```bash
python tools/docx_write.py output/case-studies/<stem>.md output/case-studies/<stem>.docx
```

APA 7 page setup is applied by the renderer: Times New Roman 12 pt, double spaced, one inch
margins, a page number top right, headings at body size in APA's own level styling, and a
reference list that starts on a new page under a bold centered label with a hanging indent.
[reference/apa7.md](reference/apa7.md) §6 is the list of what it does **and does not** do — read
it rather than assuming the render finished the job. Two things it will not do for you: the label
must be `References` or, for a single entry, exactly `Reference` — the singular is matched only as
a complete heading, so `Reference Ranges` is safe and `Reference List` is not a reference list.
**Strip the `PROPOSED` block from the `.docx`**, or render from a copy that does not carry it: it
is for the clinician, not for the grader.

### 9. Check

Against this list, by eye — none of it is mechanical:

- Does every item on the faculty's own to-do list have a section that answers it, **and is every
  skeleton section present regardless of what the faculty asked for**?
- Is the differential **numbered**, and is `1.` defensible as the thing that would kill first?
- Does every MDM entry name a discriminator from *this* case, and carry a citation?
- Does every drug in the Plan have a prescription table, and every table a `Sig` ending in an
  indication **and a prose block under it carrying class, contraindications, monitoring, adverse
  effects and guideline support**?
- **Has the step 7 reference walk actually run**, against
  [reference/apa7.md](reference/apa7.md) rather than from memory? A known reference defect does
  not leave this step in the `PROPOSED` block — it gets fixed.
- Is the Patient Education spoken, jargon-free, and does it end on the follow-up interval?
- **Read the draft back against the discriminating pairs in `scratch/voice-model.md`**, register by
  register — for each pair, which half does the draft's sentence resemble?
  [reference/voice.md](reference/voice.md) §5. Where the model is absent or a register is
  unmodeled, that is what `PROPOSED` declares rather than something this step can settle.
- Does any number in the body rest on recall rather than on a source in hand?
- **Does every claim researched in step 3 read the way its ledger record says the source reads?**
  `tools/research_ledger.py` exiting 0 says the records are well formed and says nothing about
  whether the source supports the claim — that comparison is this step's, one record at a time, and
  it is the limb [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) calls the
  one that matters most.
- **Is every `unsourced` ledger record accounted for** — in `PROPOSED` if it is a claim, and out of
  the document entirely if it is a number the clinician would act on?
- Is the `PROPOSED` block complete, and is it out of the `.docx`?

**A rendered `.docx` is not a checked document.** `tools/docx_write.py` guarantees the file opens,
the page numbers land and the reference list hangs on its own page. It cannot read a differential.
