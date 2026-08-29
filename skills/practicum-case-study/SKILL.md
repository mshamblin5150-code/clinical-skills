---
name: practicum-case-study
description: Turn a practicum case study's faculty material into a finished, APA-formatted graded submission — full workup, MDM, plan, prescriptions, patient education and references — delivered as a .docx. Use when the clinician hands over a course case study, a module video's intake data, or a "case study" Word document.
---

The input is **the live assignment URL and faculty material for a graded case study** — an intake
block transcribed from a module video, usually with the clinician's own rough differential and plan
underneath it. The output is the finished academic document that gets submitted, plus the `.docx`
it is submitted as and the run directory that proves what produced it.

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

**Derive the assignment key live before writing.** Open the assignment URL and read the course and
module from the LMS breadcrumbs. The fixed artifact word for this skill is `case-study`, so the run
directory is `scratch/runs/<course>-<module>-case-study/`. Never type a course or module from
memory. Transcribe the live assignment and course syllabus requirements into that directory's
`bar.md`; the assignment overrides the syllabus where both state the same element, and the syllabus
fills the assignment's silence. Show the transcription and precedence to the clinician, and do not
write its `SIGNED:` ISO date or draft until the clinician explicitly approves it.

**Every run uses one provenance layout.** Set `<run-directory>` to that derived directory,
`<claims-ledger>` to `<run-directory>/claims.md`, and `<checks-ledger>` to
`<run-directory>/checks.md`. Evidence handed to the ledger is
`<run-directory>/evidence.txt`; the clinician's standing-rule-3 review copy is
`<run-directory>/proposed-<date>.md`. When [discussion-post](../discussion-post/SKILL.md) routes a
worked clinical case here, this skill owns the patient-bearing board snapshot too: preserve
`board-<date>.md`, `posts/`, and the signed `bar.md` in this same case-study run directory. The
routing skill reads only enough of the prompt to choose this branch.

**Only the submission goes under `output/`.** Write the Markdown and `.docx` side by side in
`output/case-studies/` as `<course>-<module>-case-study-<date>.md` and `.docx`. The run directory is
undated because it names the assignment; the output is dated because it names one sitting. A
filename carries no patient name. `output_root()` resolves this directory to the main checkout, and
the renderer refuses a destination inside a disposable worktree while still allowing an explicit
temporary export outside every checkout.

The drafting context on that routed branch **does not see the classmate posts**. Give it the faculty
prompt and material, the signed bar, and the voice model, but not `posts/`. After the draft exists,
send the draft and the snapshotted posts to a fresh differentiation reader. The reader reports what
the existing posts converge on and where the clinician's completed draft already differs; the
orchestrator alone writes that return to `<run-directory>/differentiation.md` and shows it to the
clinician before approval. The report does not silently rewrite the draft.

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

**And there are no bullets anywhere else either. Ruled 2026-08-19** — *"remember I abhor bullet
points"* — after a run set the HPI's OLDCARTS breakdown as a bulleted list. The 2026-08-18 ruling
above named four sections because those four are where a bullet costs the *correspondence*; the
wider rule is a house preference and it covers the whole document.

**The drafted numeral controls whether a numbered list restarts.** A top-level item written `1.`
starts a new list; any other top-level numeral continues the open list across headings, labels and
prose. A nested `1.` remains a sub-list of the open list. A run does not have to do anything beyond
writing the intended numerals — `docx_write.py` allocates the required `w:num` — but a reader
comparing the Markdown to the `.docx` should know that Word receives those authored boundaries.

**The intake block is *not* a table. Ruled 2026-08-19, reversing what this file used to say.**
Demographics, the Review of Systems and the Physical Examination are written as defined fields with
their values appended, as running text. A table is still right for a given result set — laboratory
values, diagnostic studies — and the prescriptions in `Rx:` stay tables because a prescription is a
form. See [reference/style.md](reference/style.md) §1a, which carries the shapes, the Review of
Systems closer, and the three pieces of scaffolding language that must not reach the document.

The Assessment still runs as prose.

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

### A wrapper instruction that does not fit this patient is reasoned about, not answered literally

**Amended 2026-08-19, and it is the clinician amending his own ruling above:** *"I know I told you
to follow the scaffold exactly, but there needs to be some reasoning in here — it should not have
contained a separate growth and development line."*

The course wrapper carries an instruction to evaluate **growth and development**, copied from a
pediatric case. Against a 26-year-old it is not a section with a thin answer; it is a section that
does not exist. The run wrote it out as its own heading and then explained in the body why it did
not apply, which puts a paragraph in a graded document whose entire content is *this prompt is the
wrong prompt*.

**The rule is narrow and it is not a license to drop scored sections.** *Every section of the
skeleton is still written every time* — that ruling stands untouched, and the fifteen points it
protects are the reason. What this reaches is a **wrapper instruction inherited from a different
case**, where the honest response is to fold the applicable substance into the section that already
owns it — here the fetal assessment, in the Plan, carried by the fundal height, the fetal heart
tones and the dating ultrasound — and write no heading of its own. **If nothing is applicable and
nothing can be folded anywhere, say so in one clause inside the nearest owning section**, never as a
section.

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
python tools/docx_read.py "<the references document>" --normalize > <run-directory>/evidence.txt
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
  document resting on a 2011 trial is a current source — a rule that refused a 2013 KDIGO threshold
  on its date would refuse *the* threshold, not an outdated one.
- **Catalog membership is not standing**, and this rule shipped citing it as though it were.
  `reference/guidelines-catalog.md`'s own legend names rows it declines to call in-force
  guidelines — go and read them there rather than from here, because which rows those are is a
  curation and this file cannot follow one. The catalog settles what a document *is* and never
  whether it stands, so `guideline in force` is a reading of the document in front of the run and
  never a fact read off a row. `clinical-note` already refuses to read a document's *content* off
  a row; standing is the same refusal one axis over. Nothing grades that reading, which is what
  makes it worth saying.
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

Standing rule 3 still binds: a `PROPOSED (verify before use)` block lists every clinical claim this
skill contributed that the clinician's draft did not already contain — each differential added,
each code, each drug, each dose. Write it to `<run-directory>/proposed-<date>.md`, show it to the
clinician before submission, and never put it after References in the submission Markdown.

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

**Every command below that reads a ledger, check record or draft produced during a parallel run is
a checker handoff, not an author self-check.** The writing context finishes the artifact and returns
it to the orchestrator. The orchestrator gathers it into a completed-state path no writer can
modify, then gives that path and the stated command to a fresh non-authoring context. The checker
reports the result and does not edit. On a failure, the orchestrator records that first result before
returning the named finding to the writer; after the repair, it gathers a new completed state and
another fresh non-authoring context runs the command again. This is
[standing rule 6](../../AGENTS.md) applied to this skill. Where the harness has no subagent tool, the
serial fallbacks stated below remain the available floor; no parallel artifact is shared in that
case.

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

**Every drug you are going to prescribe is one of those claims, and since
[#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289) that is a rule rather than
a reading.** The run that produced the Module 1 submission recorded in its own ledger that the
treatment topic was missing from the companion evidence, and then wrote a specific dose into a
prescription table citing it. **A prescription is a dose**, and it was the one claim in that
document nothing sourced: this command graded the six records that existed, `tools/reference_scan.py`
checked that the entry was well formed and that the citation resolved to it, `tools/checks_ledger.py`
graded the readers, and **all three exited 0**.

**So a record is required for every drug the run chose a number for.** Ruled by the clinician
2026-08-19. A home medication continued unchanged at the patient's own dose is not one of them --
the run did not choose that number, the patient arrived on it -- and such a row **declares itself**:
`Continued home medication: prenatal vitamin one tablet PO daily`. **The exemption is declared and
never inferred**, so a drug row that says nothing is graded, and that is the direction it has to
fail in. A `Delayed order:` is graded too: a dose that has not started yet is still a dose the run
chose. The declaration lives in [style.md](reference/style.md) §8 with the table it is written in.

**The claim heading is what names the drug**, not the restatement buried under it — a record whose
`## CLAIM:` line says *ceftriaxone* is a claim about ceftriaxone, and one that reaches the drug only
in its `RESTATEMENT` is a record about something else that happened to mention it. Where the order
states a dose, **the heading states a number too**: that is what puts the record in front of
`NUMERIC_CLAIM_UNQUANTIFIED` above, so the restatement has to answer with a number and the chain
runs from the table's dose to a source.

**Write the claim list down before spawning anything.** `<claims-ledger>`, its `DATE`
header and one `## CLAIM:` heading per claim, and nothing under them yet. That ordering is what
makes a lost answer visible: a heading whose record never arrived has no `STATUS`, and the grader
refuses a record with no `STATUS`.

**One agent per remaining claim, all of them at once.** Each gets the same brief, and the brief is
**six returns** and the recency rule above — a reputable source in one of four classes, a full
APA 7 reference, the claim restated in the source's own terms, **the locator it actually opened with
the date it opened it, the year the page itself carries with where the page says so, and the
source's stated expiry or `none stated`**. Tell it
the source classes by name, because a returned source outside them is a finding rather than an
answer.

**The last two are not extra bookkeeping**, and a run that treats them as optional writes a ledger
the grader refuses: they are what turns *"I found a source"* into something the clinician can audit
in one click. See the paragraphs under the record shape below, and note that a **seventh** return
comes from a different agent afterwards.

**They return their record; they do not write it.** One writer to the ledger, and it is the context
that spawned them, filling each heading in as its answer comes back. **N agents appending to one
Markdown file lose records to each other**, and a ledger holding three of eight claims because two
appends collided would grade clean and let the run draft —
[#206](https://github.com/mshamblin5150-code/clinical-skills/issues/206)'s shared-artifact channel
with the sign flipped. Where the harness returns nothing usable, write one file per claim and
concatenate; what is not allowed is two writers on one file.

**One record per claim**, filled in under its heading:

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
RESOLVED: https://doi.org/10.1097/AOG.0b013e3181c2bde8 - read 2026-08-19
PAGE-YEAR: 2009 - stated on the article's masthead and in the journal citation.
REFUTATION: stands - the volume, issue and pages match the publisher's landing page, and the
    third-trimester row is on page 1327.
SECOND-ROUTE: publisher landing page -> journal PDF and table on page 1327
STATED-EXPIRY: none stated
```

`STATUS` is `sourced` or `unsourced`, and an `unsourced` record says on the same line what was
searched. `SOURCE` is one of `society guideline`, `peer-reviewed`, `government` or
`tertiary reference`. `RECENCY` is one of `current`, `within five`, `nothing newer` or
`guideline in force`, and the last two carry the reason after a hyphen — *the run must have looked,
and must say so.* `DATE` is the day the paper is written, and the recency rule is measured against
it rather than against the clock. `RESOLVED` is the URL or DOI the agent actually opened and the
day it opened it — the word `read` or `retrieved`, then an ISO date. `PAGE-YEAR` is the year the
page itself states and where on the page it says so. `STATED-EXPIRY` is `none stated`, an ISO date
and where the document states it, or an ISO date followed by `superseded cited deliberately` and a
reason. Transcribe only what the document states; do not infer an expiry from a publication cadence.
`42 C.F.R. § 414.56 (2025)` is the known case where `none stated` is correct: the codification year is
provenance, and the annual reissue schedule is not a stated expiry. `REFUTATION` is `stands`,
`refuted` or `paywalled` with the reason after a hyphen. A field's value may wrap onto the next line.

The grader also refuses a `SECOND-ROUTE` with no ASCII `->` separator.
It refuses a `SECOND-ROUTE` with an empty half.
It refuses a `SECOND-ROUTE` whose normalized halves are equal.
It refuses a `STATED-EXPIRY` outside the three forms.
It refuses a stated expiry at or before `DATE` without the deliberate-supersession reason.

**Two of those returns are what stops a citation nobody can check, and the third is a second agent.**
A reference in correct APA form is not evidence that the document exists — an invented one looks
like scholarship, which is exactly why *a wrong citation is worse than no citation: it survives
review.*

**`RESOLVED` and `PAGE-YEAR` come back from the agent that did the research.** It was on the page,
so it writes down what it opened, when, and the year the page itself carries along with where the
page says so. **No tool here touches the network** — the fetching already happened during the
research, and what these two fields do is turn it into something the clinician can audit in one
click instead of a claim nobody can check. `PAGE-YEAR` has to agree with the year in `REFERENCE`;
where a source genuinely carries no date, `REFERENCE` reads `n.d.` and `PAGE-YEAR` says the page
states none, and the two agree that way.

**Then a refutation pass, by a second agent — not the one that wrote the record.** One per sourced
claim, all at once, into the same ledger by the same one writer. The brief is adversarial: *here is
a reference and a restatement,* ***try to prove it wrong****.* Not *check whether this is right*,
because an agent asked that says yes. It looks for the document at the locator, checks the year, the
volume, the numbering and the pages, and reads whether the source says what the restatement says it
says. It also returns `SECOND-ROUTE: <research route> -> <refutation route>`. The ASCII `->`
separator and both substantive halves are required, and the two normalized halves must differ.
Before writing `paywalled`, try the clinician's authenticated Chrome route through
`mcp__claude-in-chrome__*`; the in-app Browser pane is not that signed-in route. Refuter
independence remains orchestrator-owned; see `research_ledger.DECLARED_LIMITS` for the mechanical
boundary. A source is `paywalled` only when its body remains inaccessible through that
**Authenticated route**; an anonymous or in-app login wall does not establish the disposition.
Where the profile says the **Authenticated route** is available, the researcher must try it before
giving up on the intended source, settling for a reachable substitute, or writing
`STATUS: unsourced` because the body was inaccessible.

It comes back `stands`, `refuted` or `paywalled`, with the reason after a hyphen. **A `refuted`
record is a failure and not an outcome** — unlike `unsourced`, which is honest and goes to
`PROPOSED`. It means a false citation is sitting in the ledger, so the claim goes back through this
step and comes out either with a sound record or as `unsourced`. It is never drafted from.

**`paywalled` is the third word, and it exists because a wall is not the same thing as an absence.**
A locator that 404s, or that names a document a search cannot find, is `refuted` — the citation may
be invented, which is the whole failure this pass is for. A live page whose title and authors match
the entry, with the body behind a subscription, is `paywalled` and **passes**: the URL resolving to
the right document is itself evidence the document exists, and that is most of what a fabricated
citation cannot do. **Say what did match** — the title, the authors, the date the page shows.

**It is the weakest disposition that passes, and the run says so on its own face.** The report
counts `paywalled` records on their own line, because a set of citations all behind a wall has been
checked far less than a clean exit suggests. It passes because a resolving locator whose title and
authors match the entry is evidence that the document exists, while the separate count preserves
that the source body did not verify the claim. No tool here opens a socket; access belongs to the
research and refutation passes, including the required Authenticated route attempt above.

**The independence is an instruction and not a check.** Nothing in a record shows which agent wrote
it, so the grader cannot tell a real second reading from the first agent answering itself — that is
*what a written instruction cannot do is fail* arriving at its own successor. The one shape the
grader does reach is a refutation that is the restatement pasted back.

**The ledger is gitignored**, because `scratch/` is, and that is where a case study's working
material belongs — not in a tracked notes directory. Where the harness ships a general research
skill, borrow the fan-out from it and change that one thing: they write findings into the repo,
and a case study's working material is a patient record.

**What makes a record bad, in full, so this can be walked without running anything.** A record
can be several of them at once:

| The record | Why |
| --- | --- |
| a field missing or empty | a record missing its restatement is a citation nobody checked |
| a `STATUS` that is neither word | it decides which of the rules below apply, so a third word is a record graded on nothing |
| an `unsourced` with nothing said about what was searched | anybody can write `unsourced`; nobody writes *searched PubMed, IDSA and UpToDate* without having looked |
| an `unsourced` record carrying a `REFERENCE`, `RESOLVED`, `PAGE-YEAR` or `REFUTATION` | the two contradict, and nothing can tell which was meant |
| a `SOURCE` outside the four | a returned source outside the classes is a finding, not an answer |
| a `RECENCY` outside the four | it gates the window below, so a fifth word is a record the window never read |
| a `RESTATEMENT` that is the claim pasted back | the whole point is the source's own terms |
| a claim carrying a number whose restatement carries none | *"the source discusses leukocytosis in pregnancy"* against a claim about 15,000 cells |
| a reference stating no year | `n.d.` is legitimate APA and cannot be measured for recency — unless an excuse with a reason stands in for the year |
| a reference more than five years before `DATE` with no excuse | the amended rule above |
| an excuse with no reason after it | *the run must have looked, and must say so* |
| a `RESOLVED` that is not a URL or a DOI | the field exists to put a specific in front of a reader, and *on the society website* is not one |
| a `RESOLVED` that does not say when it was read | a topic page changes under its citation, so when matters as much as where |
| a locator read after the paper was written | a record describing a reading that had not happened yet |
| a `PAGE-YEAR` stating no year, against an entry that states one | the entry claims a year the page did not give |
| a `PAGE-YEAR` that is a year and nothing else | a year alone is an assertion; where it was found is a place a reader can go and look |
| a `PAGE-YEAR` that is not the year in `REFERENCE` | the row a fabricated citation has to get past |
| a `REFUTATION` outside the three | it gates the row below, so a fourth word is a record the refutation never read |
| a `REFUTATION` with no reason after it | *the run must have looked, and must say so*, arriving at the second pass |
| a `REFUTATION` reading `refuted` | a false citation is sitting in the ledger: rewrite the record or write `unsourced` |
| a `REFUTATION` that is the restatement pasted back | the first agent re-asserting rather than a second one checking |

**Two things are deliberately not on that list.** *Within two years is the target* is a target, so a
`current` disposition on a three-year-old source is not a defect. And an `unsourced` record is
**not** a defect at all — it is the honest outcome the `PROPOSED` block exists for.

**Once the prescriptions exist, hand the ledger and draft to a fresh checker as well** -- #289's
rows read the draft as well as the ledger the way #298's row below reads the evidence dump:

```bash
python tools/research_ledger.py <claims-ledger> --draft <the draft>
```

| The prescription | Why |
| --- | --- |
| a drug in an Rx table that no claim record names | the dose is the highest-stakes claim in the document and the one every other gate exits 0 on |
| an order stating a dose whose claim record states no number | a record naming the drug is not yet a record that sourced the dose, and this is the form of that a string test reaches |
| a prescription table with no readable drug row | a table this cannot read is a finding and never a table quietly dropped from the set |

**Without `--draft` those rows do not run, and the report prints `not graded` against them
rather than `0`.** A zero beside a row that never ran is the silent pass this whole arrangement
exists to refuse, so the run that graded no prescriptions says so on the same page as its clean
exit. A draft carrying no readable prescription table is exit 2 for the same reason.

The choice not to build a dose-correctness table is grounded in indication, weight, renal function,
pregnancy, route, and #215's warning against rejecting a correct result for the wrong reason. The
mechanical boundary of these rows is named only in `research_ledger.DECLARED_LIMITS`.

**Nothing downstream reads the number either, and that stopped being true on
[#299](https://github.com/mshamblin5150-code/clinical-skills/issues/299).** Step 9's `the Rx blocks`
row asks a reader whether every drug has a table, whether every `Sig` ends in an indication and
whether the prose block is there; it does not open the ledger and compare the dose, and it still
does not. `the dose against the record that sourced it` is the row that does — **a reader and not a
row here**, because a string test can only ask whether the table's number appears in the record, and
`1 g` against *1000 mg* and `q24h` against *once daily* are the same unit problem
`NUMERIC_CLAIM_UNQUANTIFIED` above refuses to touch. **Its false-alarm rate could not be grounded
either**: when it was ruled, the only run in the tree predated the rows above it and every one of its
prescriptions reached no claim record at all, so there was not one drug-row-and-record pair anywhere
to measure a string test against. [#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s
precedent is that a cut point is grounded where the corpus offers one and refused where it does not.

**And give a fresh checker the ledger and what you were actually handed** -- #298's row, ruled by
the clinician 2026-08-20, grades what the run says it read:

```bash
python tools/research_ledger.py <claims-ledger> --evidence <the evidence dump>
```

| The citation | Why |
| --- | --- |
| an UpToDate topic cited here that the evidence dump does not carry | the companion evidence is the required supplied-source set; opening a topic through another route does not put it in that set, so citing the missing topic is the Module 1 defect exactly |
| an entry whose locator names an UpToDate topic and that states no database element | the row above reads a topic only from the database element, so without this one an entry missing it escapes the check and the coverage count together |

**The grounding is companion-evidence membership, not whether some route can open the page.** The
Authenticated route may reach an UpToDate topic outside the dump; that does not add the topic to the
faculty material the case study must use. The clinician hands supplied topics over wholesale, so the
dump is the whole supplied set. **A journal article, a society guideline or a government page the
dump lacks is left alone**, because that is this step's ordinary case: a claim record only exists
because the evidence did *not* cover the claim, and a row firing on those would refuse the correct
outcome.

**A topic the dump merely *refers* to and does not carry is not a defect and is not graded.** The
dump cross-references far more topics than it carries -- by better than an order of magnitude in the
one this was measured on -- and the great majority will never be cited. Firing on those would fire on almost every case
study, which is the rate at which a warning stops being read.

**There is no escape hatch, and that is the ruling rather than an oversight.** If an UpToDate topic
is worth citing it goes in the dump, and the remedy for a finding is one paste. **The second row is
what keeps that true**: the first reads a topic only from the `UpToDate.` element APA gives it, so an
entry that drops that element was invisible to the check *and* to the count of what the check read --
four characters, and a citation walks around a row with no hatch. So an entry this cannot read is a
finding, never a citation dropped from the set in silence. **Without
`--evidence` the row does not run and the report prints `not graded` against it rather than `0`**,
on the same reasoning as the prescription rows above. **An evidence file carrying no topic body at
all is exit 2**, because a dump this cannot read would otherwise fire the row on every UpToDate
citation in the ledger -- a mass false finding rather than a scan.

[#298](https://github.com/mshamblin5150-code/clinical-skills/issues/298) records the declined wider
join and its rationale; the implemented boundary is named only in
`research_ledger.DECLARED_LIMITS`.

**Then hand the ledger to a fresh checker, and do not draft until that checker reports it clean:**

```bash
python tools/research_ledger.py <claims-ledger>
```

The grader's coverage boundaries are inventoried in
`research_ledger.DECLARED_LIMITS`; this skill points there without copying its rows.

Exit 0 is clean, 1 names how many records failed, and **2 means it did not scan** — no file, no
records, or no `DATE` header. Re-run with `--show` to see which records, and **that output is PHI**:
read it, do not paste it. The command's full coverage inventory is
`research_ledger.DECLARED_LIMITS`; the refutation pass remains the clinical-source reading.

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

**Then hand the ledger and draft to a fresh checker**, which grades the half of step 3 that could
not run before the tables existed:

```bash
python tools/research_ledger.py <claims-ledger> --draft <the draft>
```

Every rule it applies is written out in step 3 above, so a harness with no Python walks the drug rows
by eye instead. **A drug with no claim record goes back through step 3**, not into the document with
a citation borrowed from the nearest source that mentions the disease --
[#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289) is that behavior and it is
what this exists to replace.

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
| The reference list headed anything but `References`, or `Reference` for a one-entry list | rename it — and since [#217](https://github.com/mshamblin5150-code/clinical-skills/issues/217) the heading is what *applies* the hanging indent, so a wrong label changes the layout as well as the word |
| An entry written as a bullet or a numbered item | make it a paragraph — the renderer gives a list its list style and the hanging indent is lost |
| An entry carrying no year element — most often one hard-wrapped onto a second line | join it — the renderer sets every non-blank line as its own paragraph, so the second half hangs on nothing, and a line with no year is what that looks like |
| Two entries out of alphabetical order | sort the list — sorted is sorted, [apa7.md](reference/apa7.md) §1 |
| `Links to an external site.` welded to a URL | strip it — it is a Canvas paste artifact |
| Retrieval year behind the exam year | the retrieval date must be on or after the exam date |
| An UpToDate entry with no retrieval date | add one — the content is designed to change and the version cited is unarchived, [apa7.md](reference/apa7.md) §4 |
| A retrieval date on a guideline, article or textbook | remove it — [apa7.md](reference/apa7.md) §4. **The command reaches this only where the entry carries a DOI**; on a guideline PDF or a textbook nothing in the URL says so, and it stays a reading — ruled permanent on [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241), and it is the reading step 9's `the reference list, the part no command reaches` row is graded on |
| In-text year not matching the reference list year | reconcile |
| Two entries with the same authors and year and no `a`/`b` | disambiguate, in both places — and the letters are assigned by **title order**, [apa7.md](reference/apa7.md) §3. **The same *authors*, not the same first author**: `Hsu, K.` and `Hsu, K., & Khosropour, C.` in one year take no letters, and adding them is the defect |
| An UpToDate entry with the database name unitalicized | italicize it in the entry, not in the text |
| An UpToDate year that is the year it was read | use the topic's **last update** year |
| An entry in the list that is cited nowhere in the body | delete it |
| A citation in the body with no entry in the list | add it |
| A missing space in a date | `February 19, 2026` |
| A misspelled month | check every one |

**A citation year is looked up, never recalled.** UpToDate revises topics continuously and the same
topic appears in one clinician's corpus under three different years. The companion document states
each topic's own revision date — use it.

**Then hand the list to a fresh checker, because the pass that wrote an entry cannot see what is
wrong with it:**

```bash
python tools/reference_scan.py output/case-studies/<course>-<module>-case-study-<date>.md --as-of <the exam date>
```

`--as-of` is **the exam date** — the day the paper is written. The retrieval-date row is measured
against it and never against the clock, so a draft graded twice a year apart grades the same both
times, and a run that omits it gets exit 2 rather than a clean report on a row that never ran. Exit
0 is clean, 1 names how many defects, and **2 means it did not scan** — no file, no reference list
it could find, or a heading with nothing under it. Re-run with `--show` to see which entries — and
**that output is safe to paste**, ruled 2026-08-19 and the one command here of which that is true.
It cannot carry a sentence of the draft: every finding it prints is a reference entry, a heading, a
date, or a cited author's surname and year. A test pins that rather than the docstring asserting it.

It reaches every row in the table above except one: whether an UpToDate year is the topic's revision
year rather than the year it was read needs the companion evidence document, which the command never
sees. And it says nothing at all about whether a source exists or says what the sentence citing it
says. **A clean scan is not a checked reference list.**

**A list it grades clean looks like this** — one entry per line, sorted, every entry cited above and
every citation listed:

```
Nitrofurantoin is first line in the second trimester (American College of Obstetricians
and Gynecologists, 2023), and a urine culture is drawn before the first dose (Gupta &
Hooton, 2025).

## References

American College of Obstetricians and Gynecologists. (2023). Urinary tract infections in pregnancy (Practice Bulletin No. 91). https://doi.org/10.0000/illustrative-doi
Gupta, K., & Hooton, T. M. (2025). Acute simple cystitis in adult females. *UpToDate*. Retrieved August 19, 2026, from https://www.uptodate.com/contents/acute-simple-cystitis
```

The entry lines are long and are not wrapped, which is the point rather than an oversight — the
guideline entry takes no retrieval date and the UpToDate entry takes one, and the database name is
italicized in the entry and plain in the sentence above it.

**Every rule the command applies is written in the table above, so a harness with no Python walks
the list by eye instead.** The command saves the reading; it is not where the rule lives. That is
step 3's arrangement with `tools/research_ledger.py`, and [AGENTS.md](../../AGENTS.md) keeps the two
classes of tool citation apart deliberately.

### 8. Emit the document

Write only the submission Markdown to `output/case-studies/`, then render it:

```bash
python tools/docx_write.py output/case-studies/<course>-<module>-case-study-<date>.md output/case-studies/<course>-<module>-case-study-<date>.docx
```

**It refuses rather than overwriting a document it did not write** —
[#279](https://github.com/mshamblin5150-code/clinical-skills/issues/279). `output/` is gitignored,
so a destructive render has no recovery, and the `.docx` is the one file this repo produces that
the clinician opens in Word. Two things stop it: Word's `~$` owner file beside the document, which
means it is open right now, and an archive whose parts are not the ones this renderer writes, which
means something else saved it. Either is **exit 2 with nothing written**, and the message names the
flag that proceeds anyway:

```bash
python tools/docx_write.py output/case-studies/<course>-<module>-case-study-<date>.md output/case-studies/<course>-<module>-case-study-<date>.docx --force
```

**Ask him before passing it, and that is this step's rule rather than part of his ruling.** What
he ruled on #279 is the mechanism — refuse, with a flag — not that an agent must confirm each
override. The reason to ask anyway is narrower and is about who is running the command: a refusal
on the second signal means hand-edits exist in that `.docx`, re-rendering destroys them, and
`output/` is gitignored so there is nothing to restore from. An irreversible write over the
clinician's own work is not a call a run makes for him. The flag is right where the Markdown is
the newer draft, and he is the one who knows that. **The check is the command's and not this step's** — #279's
decision 2 is that a written instruction to look first is exactly what the ticket exists to
reject — so there is nothing here to run before the render.

**A `warning:` line from that command means a table row put a cell separator into its own
text.** That is the shape
[#280](https://github.com/mshamblin5150-code/clinical-skills/issues/280) was filed over: a row faking a width the grid does not have renders into column 1, and a pipe
written as `\|` or `&#124;` outside a table reaches the page as visible text. **Fix the row, not the
warning** — [reference/style.md](reference/style.md) §8 is the worked example of a table that
declares its columns. **Unless the pipe is genuinely content in that cell**, in which case the
row is right and the warning is the price of a check that reads the output rather than the
intent. The document is still written either way, because a blocked submission is a
worse outcome than a separator on the page. The warning names the forms found and a count and
**never a cell of the draft**, so it is safe to paste into a ticket.

APA 7 page setup is applied by the renderer: Times New Roman 12 pt, double spaced, one inch
margins, a page number top right, headings at body size in APA's own level styling, a 0.5 inch
first-line indent on **body paragraphs only**, tables drawn with APA's horizontal rules rather
than a grid, and a reference list that starts on a new page under a bold centered label with a
hanging indent. **What *only* excludes is deliberately not enumerated here** —
[reference/apa7.md](reference/apa7.md) §6 has it, and a partial list at a third site is what #220
was filed over.
[reference/apa7.md](reference/apa7.md) §6 is the list of what it does **and does not** do — read
it rather than assuming the render finished the job. Two things it will not do for you: the label
must be `References` or, for a single entry, exactly `Reference` — the singular is matched only as
a complete heading, so `Reference Ranges` is safe and `Reference List` is not a reference list.
The `PROPOSED (verify before use)` block is written separately to the run directory as
`proposed-<date>.md`; it never enters the Markdown submission or the rendered `.docx`.

### 9. Check

**This is the second fan-out, and it runs after the draft exists.** Step 3's ran before a word was
written and found sources; this one reads the document that was written and reports what is wrong
with it. [#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218).

**The reason it is not just a careful reread is that a run cannot audit its own work.** The same
recall that produced a reference entry, a differential order or an MDM discriminator produces the
check of it, so the check has to come from somewhere that recall does not reach —
[AGENTS.md](../../AGENTS.md)'s *a report by the pass that produced it is a baseline, not a
verification*, and [ADR 0001](../../docs/adr/0001-fixture-asserts-on-named-findings.md) one level
up. Two places qualify: a string test, where the rule is mechanical, and a **fresh reader** given
the draft and the rule and nothing else, where it is not.

**Write the check headings down before spawning anything.** `<checks-ledger>`, one
`## CHECK:` heading per row of the table below, and nothing under them yet. That ordering is step
3's and it is here for step 3's reason: a heading whose verdict never arrived is visible, and a
check that was never run is not.

| Check | What it reads | How | A `clean` says what it walked |
| --- | --- | --- | --- |
| the house style | the whole draft, section by section | `tools/case_study_scan.py` below — mechanical, so it is a command and not an agent | no |
| the reference list | the list, and every citation in the body | `tools/reference_scan.py`, step 7 — mechanical, so it is a command and not an agent | no |
| the reference list, the part no command reaches | the entries against the companion evidence | a reader: is each UpToDate year the topic's **last update** year, does any entry carry a **retrieval date that does not belong** — a guideline, a statement or a textbook takes none and the command catches that only on a DOI — the rule is [apa7.md](reference/apa7.md) §4 and how far the command reaches is §7 — and does each source exist and say what the sentence citing it says | no |
| differential ordering | the numbered differential and the intake block | a reader: is `1.` defensible as what would kill first, and does a patient of childbearing age with abdominal or pelvic pain have the pregnancy-related emergencies ranked first — *Ordering is the graded axis* above | yes |
| MDM completeness | every MDM entry | a reader: does each entry name a discriminator from **this** case rather than summarizing the disease, and does each carry a citation | yes |
| the Rx blocks | the Plan and every prescription table | a reader: every drug in the Plan has a table — **including any drug row that welds a second drug into it**, which is a drug in the Plan without its own table and is a shape no command here reaches — every `Sig` ends in an indication, and every table has the prose block under it carrying class, contraindications, monitoring, adverse effects and guideline support | no |
| the dose against the record that sourced it | every prescription table, and `<claims-ledger>` | a reader: for every drug row stating a dose, does the claim record naming that drug state **that** dose — the same quantity, in whatever unit and form the source wrote it — rather than a different one. Never whether the dose is *right*: a wrong-but-sourced dose passes this row and is [#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289)'s closing prohibition | yes |
| the clinical decisions no command reaches | the faculty material and the whole Markdown draft | a reader: for every continuing drug, **whether a stop criterion's endpoint is the right endpoint**; for every PRN drug, **whether a drug ordered PRN needs an endpoint of its own**; and against the patient in the faculty material, whether the draft carries **a wrapper section that does not apply to this patient**. Never whether a dose is correct: that remains [#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289)'s closing prohibition | yes |
| the numbering in context | `<numbering-readback>` produced by `python tools/docx_read.py "<the case study document>" --numbering`, and the Markdown draft | a reader: read the reconstructed numerals in context, never the raw `.docx`; does each section start where it should, does each MDM entry discuss **by name** the diagnosis at the same position in the differential, and does every restart or deliberate continuation suit the section | yes |
| the rendered document | the Markdown draft and the rendered `.docx`, page by page | a vision-capable reader: open or render every page, compare it page by page with the Markdown, and report clipped, overlapping or missing content; broken tables or list numbering; bad page breaks; misplaced headings, page numbers or signatures; and reference-list layout that the Markdown cannot show | yes |
| the faculty's own to-do list | the faculty material, the draft's headings, and `bar.md` on a routed board run | a reader: does every faculty item have a section that answers it, and on a routed run does every signed bar element — including word floor, reference minimum, ISBN, and every prose element — hold in the finished draft | no |

**The orchestrating context produces `<numbering-readback>` before the fan-out** and is its sole
writer. Run `python tools/docx_read.py "<the case study document>" --numbering` and redirect its
output to a new run-unique path under `scratch/`; give the numbering reader that text and the
Markdown draft, never the raw `.docx`. Remove the readback with the run's other private paths after
the checks complete.

**The last column is [#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255), and it
is some rows rather than every row.** On a row marked *yes* a `clean` verdict has to say what the
reader walked, and `tools/checks_ledger.py` fails a bare one. Those are the rows where a wrong
`clean` is most expensive; everywhere else a bare `clean` still passes, which is the gap below. **Brief
every reader on a marked row accordingly** — they report what they examined whichever verdict they
return, and the clause is one sentence written by an agent that has just walked the thing. **How
many rows are marked is the table's own column to say and is counted in no sentence about it**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms: it read *two* in
prose across this repo until #299 made it three, and the sweep that repaired those copies missed
several, which both axes of `/code-review` then found.

#### The house style is a command now, and it is the row this step gained on #277

**Ruled 2026-08-19.** The clinician read the first rendered submission and returned a list of
findings. Some were renderer defects and are fixed; **the rest were house style, and every one of
those is in the body of the draft** — which `tools/reference_scan.py` does not read and no reader
was briefed on. **The arithmetic is on the ticket and in `CLAUDE.md`, once**, because a figure
restated where nothing re-derives it is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143). His framing is the ticket: *"is there some machine checkable way to get this right every
time... this prevents me from using this skill for future work."*
[#277](https://github.com/mshamblin5150-code/clinical-skills/issues/277). The rules landed in
[reference/style.md](reference/style.md) §1a and §8 as prose, which is exactly the arrangement
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) ruled insufficient: **a
prose edit to a rule fails nothing.**

**A fresh checker runs it on the Markdown before step 8 renders it, and another fresh checker runs
it after every repair:**

```bash
python tools/case_study_scan.py output/case-studies/<course>-<module>-case-study-<date>.md
```

Exit 0 is clean, 1 names how many rows failed, and **2 means it did not scan** — no file, no section
it recognizes in the document, a skeleton that disagrees with the one this file publishes above, or
a `SKILL.md` it could not read at all. **The last is a claim about the *check* rather than about the
rows**, which all still ran; what the status refuses is a clean set of them standing for a scan
against a skeleton nobody confirmed.
Re-run with `--show` to see which, and **that output is PHI**: read it, do not paste it.
Deliberately **not** `tools/reference_scan.py`'s exception — that command's output is bounded by
what its code can draw from, and this one's is not, because a bullet's finding is the bullet's own
text.

**Every row is a rule written in [reference/style.md](reference/style.md) §1a or §8**, and how many
there are is `case_study_scan.KINDS`'s to say rather than this paragraph's. **This list is the one
copy** — a test keyed on that tuple asserts each row has a sentence here, and `CLAUDE.md` points at
it rather than repeating it. The rows are: no bullet anywhere in
the document, no table under Demographics, the Review of Systems or the Physical Examination, the
Review of Systems closing with the all-other-systems disclaimer **and the Physical Examination not
carrying one**, no scaffolding language from §1a's closed set, the Most Likely Clinical Diagnosis
not set wholly bold, the signature and its date on one line, the prescription table at six rows and
three columns wide, **a drug that continues carrying a stop criterion**, and **no `PROPOSED
(verify before use)` heading in the submission**; that review block belongs in the run directory.

**It reads the Markdown through the renderer's own parser rather than a copy of it.** A line it
calls a bullet is a `ListParagraph` in the `.docx`, because `docx_write.blocks` is what both of them
read — `tools/reference_scan.py` importing `REFERENCE_HEADING` is the precedent, at the width of one
heading rather than the whole parse. **A fenced code block is not an escape**: the renderer opens
nothing on a fence, so a bulleted line inside one is a bullet in the finished document.

**The em dash is counted and never graded, and that is a ruling rather than an omission.** His
words: *"generally I prefer not to use em dashes, just saying, though I do use them sometimes."* A
row keyed on a stated preference with a stated exception would refuse a document he would have
written himself, which is
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s own defect a third time —
that ticket exists because a recency filter cut a correct claim for a property the rule did not care
about, and its closing comment records the same mistake being made again inside the fix. The count
prints; nothing fails on it.

**Authored numbering surprises are counted and never graded.** The report counts a numbered
section that does not open at `1.` and a transition that does not advance by one. A section may
deliberately continue the prior list, so neither shape can fail the command or change its exit
status. They stay visible for the reader who compares the drafted and rendered numerals.
[#402](https://github.com/mshamblin5150-code/clinical-skills/issues/402).

**A clean scan is not a checked draft.** Here is what no row of that command reaches: **the voice,
and it never will be**, **a wrapper section that does not apply to this patient**, **whether a stop
criterion's endpoint is the right endpoint**, **whether a drug ordered PRN needs an endpoint
of its own**, **a second drug welded into one drug row, discharged by the first drug's endpoint**, **whether a dose is correct**, **whether a dose was sourced at all**,
**a scaffolding phrase nobody has written yet**, and **anything the Markdown cannot show, which the
rendered document can**.

**The two findings in his list that mattered most clinically are in that list rather than in the
rows** — the ceftriaxone order's missing endpoint being the *right* endpoint, and the growth and
development section that should not have existed at all. The command reaches that a continuing drug
states an endpoint and not whether the endpoint is defensible; the second is a reading, and it is
the amended ruling above, *A wrapper instruction that does not fit this patient is reasoned about*.
Both stay a reader's, and the last of them is why `the house style` row's `clean` is not one a
command can substitute for the walk.

**`NOT_REACHED` declares the command's limits; ownership is assigned item by item. Ruled on
[#306](https://github.com/mshamblin5150-code/clinical-skills/issues/306).** The clinical-decisions
row owns endpoint defensibility, the PRN endpoint question and wrapper applicability. The rendered-
document row owns what only the `.docx` pages can show. The welded-drug reading belongs to `the Rx
blocks`; dose sourcing belongs to `the dose against the record that sourced it`; voice belongs to
the voice-model walk below; and dose correctness remains deliberately prohibited. A limit stays in
`case_study_scan.NOT_REACHED` even after a reader owns it, because the tuple says what **that
command** cannot decide, not what the workflow ignores.

**The two new checks are separate and both substantiate a `clean`.** Clinical judgment and visual
layout read different evidence and need different capabilities, so one reader never discharges
both. The clinical reader states which continuing and PRN orders and which wrapper instructions it
walked. The vision-capable reader states that every rendered page was compared with the Markdown
and names the layout surfaces it inspected. If the harness cannot render or view the `.docx`, that
reader returns no verdict; the prewritten heading remains incomplete and the document is not
submitted. A text-only reread of the Markdown cannot substitute for the visual check.

**One reader per row, all of them at once, and none of them is the context that wrote the draft.**
Each gets the draft, the rule its row names, and the instruction to report findings rather than fix
them. **Where the harness has no subagent tool, the same briefs are worked one at a time in the main
context, into the same file** — step 3's ruling, taken whole rather than answered a second way. The
mechanism is the file and the brief; the parallelism is a speed property, and nothing downstream can
tell the difference.

**They return their record; they do not write it.** One writer to the checks file, and it is the
context that spawned them, filling each heading in as its verdict comes back — step 3's rule and
[#206](https://github.com/mshamblin5150-code/clinical-skills/issues/206)'s, arriving at the second
fan-out. **N readers appending to one Markdown file lose records to each other**, and since
[#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240) the grader below catches
one that landed on top of another — two records under one check, where the file can hold one
answer. What it cannot catch is a write that landed on nothing, so the ordering rule above is still
what makes a lost verdict visible. Where the harness returns nothing usable, write one file per
check and concatenate; what is not allowed is two writers on one file.

**One record per check**, filled in under its heading:

```
## CHECK: differential ordering
VERDICT: defect
FINDINGS: The differential's 1. is appendicitis, and the intake gives a patient of
    childbearing age with pelvic pain and no documented hCG. The pregnancy-related
    emergency is at 4 and has to be at 1 until the hCG is back.
```

`VERDICT` is `clean` or `defect`, and a `defect` says what and where. **On the rows the table
above marks, a `clean` says what it walked** — the same field and the same substance test, and it
is the only thing in the file that stands against a reader who skimmed. A heading with no `VERDICT`
under it is a check that did not run, and the draft is not submitted on it.

```
## CHECK: MDM completeness
VERDICT: clean
FINDINGS: Walked all five MDM entries. Each names a discriminator from this case — the
    36-hour onset, the absent rebound, the prior appendectomy — and each carries a
    citation.
```

**A marked row whose reading spans two documents says which pair it put side by side**, because
*walked the Rx blocks* is a clause a reader who opened one of them can write:

```
## CHECK: the dose against the record that sourced it
VERDICT: defect
FINDINGS: Four drug rows state a dose. Three match the record naming that drug. The
    ceftriaxone row orders 250 mg IM once and its record's restatement sources 1 g IV
    daily — a different dose, not a different unit for the same one.
```

**What makes a record bad, in full, so this can be walked without running anything.** A check can
be several of them at once:

| The record | Why |
| --- | --- |
| a heading the table names that is not in the file | a reader that was never spawned, or one whose record was lost |
| two records under one check | two verdicts and nothing says which was meant — the shape a second writer leaves |
| a heading with no `VERDICT` under it | a reader that never returned, and the field every rule below it needs |
| a `VERDICT` that is neither word | it decides which of the rules below apply, so a third word is a record graded on nothing |
| a `defect` with no `FINDINGS` under it, or an empty one | anybody can write `defect`; nobody writes the entry's position and the rule it fails without having read it. The field and not just the words — a reason typed after the keyword says the same thing where nobody looking for it will look |
| a `clean` with no `FINDINGS` under it, on a row the table above marks *yes* | the same test on the other verdict. Anybody can write `clean`; nobody writes *"walked all five MDM entries, each names a discriminator from this case"* without having walked them. [#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255), and it is some rows rather than every row — the rest are counted and not graded, and the report names which |

**That last row was off the list entirely until
[#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255), and it is on for some of
the rows rather than for all of them.** A `clean` with nothing under it is what a check that ran and found
nothing writes, and it is also what a check that reported nothing writes — nothing in the file tells
them apart, which is the gap
[#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240) named and left open. **There
is no better string test to reach it with**; what reaches it is requiring the `clean` to say what it
walked, and that is a change to what this step asks a reader to write rather than a grader of what it
already asked. **#255 ruled it on differential ordering and MDM completeness and against the rest**, and #299 has
since marked a third — so everywhere still unmarked the shape is exactly what #240 declared, and the reading below is still the only
thing that reaches it. `the reference list` is the clearest of the ones left out: it is graded by a
command, so its `clean` is an exit status and there was never a reader to have walked anything.

**Which two #255 marked, and the arithmetic behind them is not the arithmetic #255 offered.** That ticket put
these two at *70 of the rubric's 100 points*, and [reference/rubric.md](reference/rubric.md) does
not: *Differential Diagnoses and Clinical Reasoning* scores **15** and *Medical Decision Making*
**10**, so the two criteria these rows name carry **25** between them. **Which criteria compose the
70 is not stated here and cannot be**: [reference/rubric.md](reference/rubric.md) asserts that
figure without enumerating it, and 31 different seven-criterion subsets of its table sum to 70 — so
any count named beside it would be a number satisfiable 31 ways, which is not a claim. What the
table does settle is that *Comprehensive Treatment Plan* at **20** is the single heaviest criterion
on the sheet, and `the Rx blocks` is the row that reads it — one of the ones left out. **The ruling
stands on the 25.**

**#299 then marked a row that reads that same 20-point criterion, and it did not disturb the 25.**
`the dose against the record that sourced it` is marked because a wrong `clean` there is a **dose**,
which is an argument about what the row costs when it is wrong and not about what the criterion
scores — and it was an argument #255 could not weigh, because that reading did not exist when it was
ruled. `the Rx blocks` itself stays unmarked: its three checks are shapes in one document, and
marking the correspondence reading without marking them is the whole reason it is a row of its own
rather than a clause in that one.

**A draft of this paragraph said *the whole clinical-judgment cluster of seven criteria* and that
was the same defect one sentence later** — a figure nothing re-derives, introduced by the sentence
correcting a figure nothing re-derives. [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)
arriving inside its own repair, which this repo has now recorded happening four times.

**What the new row buys is a shape, not a reading**, and that was priced rather than glossed. A lazy
reader can satisfy it with one stock sentence — `specificity_scan.py`'s limit, inherited here — so it
converts the records on the marked rows from unfalsifiable to *checkable by eye*, which is what the walk below
is for and previously had nothing to work with.

**Then hand the checks file to a fresh checker, and do not submit until that checker reports it
clean:**

```bash
python tools/checks_ledger.py <checks-ledger>
```

Exit 0 is clean, 1 names how many checks failed, and **2 means it did not scan** — no file, or no
`## CHECK:` record in it. Re-run with `--show` to see which, and **that output is PHI**: read it, do
not paste it. **A clean scan is not a checked draft** — every verdict in that file is a reading, and
this command only grades that the reading was recorded. A well-formed `clean` from a reader that
skimmed is what a well-formed `clean` from a reader that read looks like.

**Every rule the command applies is written above, so a harness with no Python walks the file by
eye instead.** The command saves the reading; it is not where the rule lives — step 3's arrangement
with `tools/research_ledger.py`, and [AGENTS.md](../../AGENTS.md) keeps the two classes of tool
citation apart deliberately.

**A finding is fixed, not handed over.** Ruled on
[#211](https://github.com/mshamblin5150-code/clinical-skills/issues/211) and inherited here: the
clinician does not get a list of citation defects to repair by hand. What goes to `PROPOSED` is only
what a fix would require **him** to decide — a claim the evidence does not settle, a register the
voice model does not cover. Everything else is repaired in the document before it is rendered again.

**These readers see a patient record, and what they may report back is the strict form.** A finished
draft is written about a patient, so a reader reports **where and what is wrong** — the section, the
entry's position, the rule it fails — and **not the sentence itself**. That costs nothing here,
because the context reading the report is the one holding the draft and can open the line for
itself. [CLAUDE.md](../../CLAUDE.md)'s subagent rule, taken whole rather than carved out. **Ruled
2026-08-19, and ruled unchanged**: a reader is a language model summarizing clinical prose in its
own words, and no guarantee about what it will write is available.

**`tools/reference_scan.py` came apart from that on the same day**, which is
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s first decision settled.
Its `--show` output is **safe to paste**, because what the code can draw on is checkable and a
reader's wording is not: every finding it prints is a reference entry, a heading, a date, or a cited
author's surname and year. It still prints counts only by default. **The two halves of one question
were answered differently, and the split is about where the label attaches rather than a carve-out
from standing rule 1.**

Then walk this list, by eye — none of it is mechanical:

- Does every item on the faculty's own to-do list have a section that answers it, **and is every
  skeleton section present regardless of what the faculty asked for**? On a routed board run, did
  the same reader compare every signed bar element with the finished draft and report any miss?
- Is the differential **numbered**, and is `1.` defensible as the thing that would kill first?
- Does every MDM entry name a discriminator from *this* case, and carry a citation?
- Does every drug in the Plan have a prescription table — **including any drug row that welds a
  second drug into it**, which is a drug in the Plan without its own table — and every table a
  `Sig` ending in an indication **and a prose block under it carrying class, contraindications,
  monitoring, adverse effects and guideline support**?
- **Has the step 7 reference walk actually run**, against
  [reference/apa7.md](reference/apa7.md) rather than from memory, and does
  `python tools/reference_scan.py <the draft> --as-of <the exam date>` exit 0? A known reference
  defect does not leave this step in the `PROPOSED` block — it gets fixed.
- **Does `python tools/checks_ledger.py <checks-ledger>` exit 0**, and has every
  `defect` been repaired in the document rather than reported? The command settles the record
  shape, and **the defect table above is the list** — this line used to name three of its rows and
  went stale the moment #255 added one, which is the shape that table exists to keep out of prose.
  Whether the verdict is *right* is the one thing it cannot see, and that is what the readings
  above are.
- Did the clinical-decisions reader compare the faculty material with the whole draft and account
  for every continuing or PRN endpoint and every wrapper-only section?
- Did a vision-capable reader compare every page of the rendered `.docx` with the Markdown draft,
  with a substantiated verdict recorded under `the rendered document`?
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
- Is `<run-directory>/proposed-<date>.md` complete, and is no `PROPOSED (verify before use)`
  heading present in either submitted file?

**A rendered `.docx` is not a checked document.** `tools/docx_write.py` guarantees the file opens,
the page numbers land and the reference list hangs on its own page. It cannot read a differential,
and it cannot see clipping, overlap, a bad break or a layout that is correct in XML and wrong on the
page. The `the rendered document` reader is what turns the rendered file into a visually checked
one; its substantiated verdict is required before submission.
