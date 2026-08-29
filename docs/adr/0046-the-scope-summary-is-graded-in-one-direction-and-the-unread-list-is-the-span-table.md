# The scope summary is graded in one direction and the unread list is the span table

[ADR 0025](0025-a-section-read-is-the-unit-and-a-sheet-s-page-coverage-is-what-the-state-asserts.md) point 4 put the span table inside `## Scope` and kept the `Read:` and `Not read:` prose limbs beside it — *"the existing prose limbs stay as the human summary and keep their grader rule; the table carries the arithmetic."* That is two statements of one claim, and only one of them is graded.

[#511](https://github.com/mshamblin5150-code/clinical-skills/issues/511) is what the other one drifted into. `reference/thresholds/cervical-cancer.md:24` names the source's references as unread while `:30` retires them by class exemption, and `python tools/threshold_sheet.py --all` exits **0** with every gate clean. [ADR 0035](0035-a-none-topic-is-a-null-threshold-sheet-and-the-state-is-derived-from-its-span-table.md) ruling 4 then made those limbs load-bearing for a clinical verdict: the jump to `## Scope` is what delivers the completeness claim a run's verdict does not carry.

Grilled on 2026-08-26. The clinician ruled every point below on the same day. **Nothing is built here; this is the record the build reads.**

## What is ruled

1. **The ticket's rule is two rules with opposite footings, and only one ships.** *A span that has left the unread list may not be named in the scope summary as unread* is enforced. *Every unread span must be named in the scope summary* is declared unreachable and is not attempted.
2. **The enforced direction is not a new rule.** `CONTEXT.md`'s **Section read** already states it: a span leaves the unread list when it yields rows, when a blind independent read agrees it holds none, or when it is a reference list retired by class. Those three are exactly `yes`, `read YYYY-MM-DD` and `exempt:`. The check makes a defined term refuse rather than inventing one.
3. **It refuses, inside `gate_schema`.** Every other `## Scope` rule there refuses — a missing limb, an undeclared span source, an invalid `read` value — and the whole ticket exists because a prose edit fails nothing. A finding that printed without failing is one notch above the current state, which is what [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) ruled insufficient one artifact over.
4. **The span label is matched against the limb read as a delimited list, never as free text.** Substring matching over the whole limb is what produced the only false alarm in the measurement below.
5. **`cervical-cancer.md` is corrected in the same commit, and the failing case is planted by mutating the corrected sheet inside the test.** That is [fixtures/slot-form-run](../../fixtures/slot-form-run/README.md)'s arrangement — the record stays what it should be and the planted defect is legible to whoever asks how the branch is covered. The ticket's decision 3 does not arise: a gate that refuses cannot land beside a sheet that fires it.
6. **The correction moves the class retirement into the `Read:` limb**, matching `hypertension.md:40` and `prediabetes-type-2-diabetes-screening.md:22`. **That placement is a convention and may not become a check** — `hypertension` writes *"The reference list"* rather than the span label, so a rule requiring the label there fires on a sheet that did it right.
7. **`Scope summary` enters the glossary, and `unread list` is ruled to mean the span table.** One term for both copies is the confusion that produced the defect, and the `_Avoid_` line is the half that does the work.
8. **ADR 0035 ruling 3's declaration sentence is corrected in place.** It reads *"Every span in `## Scope` **was read**"* and a class exemption is not a read. It becomes *"has left the unread list"*. Grading that declaration remains [#483](https://github.com/mshamblin5150-code/clinical-skills/issues/483)'s, and nothing here reaches `## Thresholds`.
9. **What is not graded is declared in one module object**, on `reference_scan.NOT_REACHED`'s arrangement — [`reference/thresholds/README.md`](../../reference/thresholds/README.md) points at it and copies no row, and a test binds both directions. **`threshold_sheet.py` already holds loose limit constants and a prose bullet list**, and one row below is among them: the object points at `PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES` rather than restating it. Whether the rest migrate into it is that module's own population question, filed rather than settled here. `reference/thresholds/README.md:293`'s *"Every line currently present in `## Scope` is held by something"* is corrected in place — the limbs' **presence** was held and, after this, one direction of their **content**. Say which.

## The measurement came first and falsified the ticket's own rule

The ticket poses decision 1 as one symmetric rule. Run over all four committed sheets on 2026-08-26, its two halves do not resemble each other:

| direction | fires | true |
| --- | ---: | ---: |
| a span that has left the unread list is named as unread | **1** | **1** |
| every unread span is named in the summary | 7 | **0** |

**The second direction is not a matcher problem and no matcher rescues it.** `hypertension.md` compounds two spans into `the front matter and methods`; `prediabetes-type-2-diabetes-screening.md` deliberately pluralizes four spans across two sources into `both practice-consideration spans` and `both supporting-evidence spans`. Both are *more* accurate than a list of labels would be, and the rule refuses all seven. Requiring the labels verbatim would refuse a correct summary, which is [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s defect arriving on a sheet.

**The first direction's one false alarm indicted the matcher rather than the rule.** Against the whole limb as a substring, `diabetes.md`'s span `index` matched the phrase *a complete recommendation index* two sentences below the claim. Reading the limb's first sentence as a delimited list drops it and keeps the live instance — ruling 4, and the reason it is a ruling rather than an implementation note.

**These figures are this record's to state.** Nothing committed re-derives them until the build lands, and the build's test is what makes them re-derivable rather than cited.

## The enforced direction is the conservative one, and the record says so rather than letting a reader infer a safety net

A sheet naming a retired span as unread tells a reader that pages might hold a number when they were retired by class. The reader is **more** cautious than the truth. The dangerous direction is the other one — an unread span missing from the summary, so a reader takes the listed items as the whole gap and concludes the guideline is silent about a span nobody opened. That is precisely the harm [`reference/thresholds/README.md`](../../reference/thresholds/README.md) says the limb exists to prevent, and it is the half no matcher reaches.

So what ships is a **tripwire for a summary that has stopped tracking its table**, not a guard on the claim the summary makes. `cervical-cancer.md`'s staleness is evidence its author never revisited the limb when the row moved; the same lapse pointing the other way is invisible. Writing that down is the difference between a declared floor and a check that reads as coverage.

## ADR 0035 contradicts itself, and the ticket's own shape is why it was found

Ruling 3 fixes the null sheet's declaration as a literal sentence opening *"Every span in `## Scope` was read"*. Ruling 5's qualifier, in the same record, says *"no span can be `yes`, so every span rests on **a marker or a class exemption**"*. A class exemption is not a read — `CONTEXT.md` has it as the third and separate way a span leaves the unread list, and `gate_schema` permits it on a `references` span.

**Both USPSTF sheets in the directory exempt their references**, so [#519](https://github.com/mshamblin5150-code/clinical-skills/issues/519)'s LTBI sheet is likely to be the first null sheet written and likely to carry one — required by a ruled record to write a sentence false of its own table. That is #511's defect one section over, inside the record that creates the artifact.

It is corrected rather than re-ruled: the mechanism is right and the word is wrong, which is the correction ADR 0035 ruling 2 already records being made to itself once. [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md) permits it in place. **The corrected sentence is #483's to hold and is deliberately not reproduced here**, on [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms — a literal string quoted into a second record is one that goes stale the day the build changes it.

### Why grading the declaration is not folded in

It sits in `## Thresholds`, its presence is what lifts the zero-row refusal, and #483 is `ready-for-agent` with the build written against that region. Two branches editing one block is this repo's recorded failure and ADR 0035 already warns about it on a neighboring block. The wording is ruled here because it costs one edit today and a rebuild after; the gate is #483's.

## Two notions of a read will sit in one function, and the words look alike

[ADR 0026](0026-a-threshold-row-s-rec-is-a-source-locator-and-narrative-is-a-reserved-kind.md) rule 6 keys a row's span floor strictly on the `read` cell being `yes` — not `no`, not a dated null marker, not `exempt:`. This record keys on a span having **left the unread list**, which is `yes` **or** `read YYYY-MM-DD` **or** `exempt:`. `hypertension.md:52-53` carries one of each and neither is `yes`.

Both checks live in `gate_schema`. A builder who reads the newer phrase as rule 6's predicate widens the span floor and admits a row onto a page whose only covering span is a dated null marker — the self-contradiction rule 6 exists to refuse. **Neither record cross-referenced the other**, and this paragraph is the one place both are stated together. Found by the sweep this grilling ran, on [#464](https://github.com/mshamblin5150-code/clinical-skills/issues/464).

## Considered options

**Declare both directions ungraded and fix the sheet by hand.** [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s and [#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141)'s *declare the coverage rather than widen the instrument*, and the ticket's own decision 2. Rejected because nothing is being widened: the enforced direction is a glossary term acquiring enforcement at zero measured false alarms, and #220 ruled a declaration alone insufficient for exactly this shape one artifact over. The declaration ships **as well**, for the residue.

**Build decision 1 as filed.** Rejected on the measurement — six of its seven fires are correct summaries, and a run obeying it would rewrite them worse.

**Derive the summary from the span table.** It is #220's canonical repair and it collapses toward deletion: a derived limb carries exactly what the table two lines below carries, and ADR 0025 point 4 kept the limbs because a person wrote them. `hypertension`'s Read limb carrying the 103-recommendation argument and `prediabetes`'s Not-read limb naming #464 are what would be lost.

**Grade the mirror direction — an unread span named under `Read:`.** No instance exists in the directory, so it is a rule with no recorded defect behind it. Declared instead.

## Declared limits

**Nothing checks that the summary names every unread span**, and no matcher can — see the measurement. This is the direction in which a wrong summary misleads a clinician, and it stays a reading.

**The matcher under-fires on a compound span label.** A span named `X and Y` is not an item of a list split on `and`, so it is never compared. A floor on the shapes in the tree, on [`tools/test_ls_files_coverage.py`](../../tools/test_ls_files_coverage.py)'s terms.

**Only the limb's first sentence is read as the list.** A summary whose unread list runs to two sentences is compared against the first, and the remainder is invisible. This is what drops `diabetes.md`'s `index` collision, and it is the same narrowing paying for itself in both directions.

**It is vacuous on a null sheet as [ADR 0035](0035-a-none-topic-is-a-null-threshold-sheet-and-the-state-is-derived-from-its-span-table.md) words one, and that is a property of the wording rather than of the sheet.** Ruling 4 there has the limb read *nothing in the source page range*, which names no span, so nothing can fire. A null sheet is in fact **the one sheet where every span has left the unread list**, so a limb naming one — *the reference list, retired by class* is a plausible first draft — fires correctly and refuses. #511's sweep comment raised the vacuity against decision 1 and the narrowing does not rescue it, which is why ruling 8 leaves the declaration's own gate with #483. **Corrected in place on 2026-08-29:** [ADR 0066](0066-a-null-sheet-s-re-derivable-clause-is-re-derived-and-the-gate-keys-on-the-zero-row-condition.md) ruling 1 makes a zero-row sheet legal only where every span has left the unread list, so on a **legal** null sheet this check is no longer vacuous -- a limb naming any span fires it. It stays vacuous only against a limb naming a string that is no span label, which is this record's own unreachable direction below. **This row first read *the rule can never fire*, which is a notch stronger than the measurement** — this record's own subject arriving inside its declared limits, found by the sweep this grilling ran rather than by a reader.

**An item in the limb that is not a span label is reached by neither direction.** `cervical-cancer.md:24` names *evidence review* and the span table holds no such span; it is presumably inside `rationale and clinical considerations` at pp. 1-11, which is a reading. The graded direction compares span labels to list items and the unreachable one compares list items to span labels, so an item belonging to neither set is outside both. The correction in ruling 5 deliberately leaves it standing.

**The mirror direction is not graded** — an unread span named under `**Read:**`. No instance exists in the directory, so the rule would carry no recorded defect behind it, and `hypertension.md:40` writes *"The reference list"* rather than the span label, so the label match that reaches the graded direction does not reach this one.

**A span whose page range is drawn wrong is untouched.** This row is already in the module as `threshold_sheet.PAGE_COVERAGE_CANNOT_GRADE_SPAN_BOUNDARIES`, on ADR 0025 point 3 — the object points at that constant and does not restate it, which is the one row here that arrived with a home. Found by the sweep this grilling ran, which is [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) caught inside the record that cites #143 twice.

**The convention in ruling 6 is unenforced by construction**, and an unenforced convention drifts — which is the finding this record exists for, arriving on the remedy.
