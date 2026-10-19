# The clinician rules each recommended item named in Objective at the go-ahead and a blanket delegation never promotes one

**Measured at:** 05dfc863374c3b165782b29f09b0d1575bdc3a4f

[#1596](https://github.com/mshamblin5150-code/clinical-skills/issues/1596) was ruled in
[ADR 0380](0380-a-pass-may-grammar-check-its-own-note-and-a-prior-run-is-a-record-not-a-template.md)
on 2026-10-16 and stayed under `grilling` because tracker sweeps after that ruling found one open
decision and three ambiguities in its build spec. The clinician ruled all four on 2026-10-19,
grilled against `main` at the commit above, where the freshness gate read `FRESH`. **Nothing is
built here; with ADR 0380 this is the record the build reads.**

## Supersedes

- [ADR 0380](0380-a-pass-may-grammar-check-its-own-note-and-a-prior-run-is-a-record-not-a-template.md)
  ruling 5, the words "Batch-shift's second reader rules on each one in the drift row 21 walk".
  The clinician rules each matched pair at the go-ahead (ruling 1 here). The never-graded count,
  its `--show` pairs, the allowed and defective readings of a pair, and the exit status stand.

## Measured before ruling

**Ruling 5's reader does not exist.** `skills/batch-shift/SKILL.md` carries no drift-matrix text:
`git grep -n -i drift -- skills/batch-shift/SKILL.md` returns nothing. Its only **Second reader** is
the step-6 descriptor-agreement read, which compares codes with note wording and receives a blind
brief, and [ADR 0413](0413-a-delegated-answer-names-its-note-sections-and-a-second-reader-checks-it-before-the-go-ahead-quotes-it.md)
declined to widen that brief for #1813. The drift-matrix walk belongs to the clinical-note pass,
which is the author.

**Batch-shift never runs the scanner that produces the count.** `grep -c differential_scan
skills/batch-shift/SKILL.md` prints 0; batch-shift's terminal grader is `filled_vitals_census.py`.
So the count ADR 0380 ruling 5 adds would reach no batch go-ahead.
[ADR 0417](0417-the-clinical-go-ahead-shows-its-paired-grader-s-coverage-lines-before-the-ask-and-refuses-an-approval-that-did-not.md)
rulings 1 and 4 already carry `differential_scan.py`'s never-graded lines to a standalone
clinical-note go-ahead.

**Interaction Level sits between two sources.**
[ADR 0427](0427-batch-shift-s-run-artifacts-are-built-by-committed-tools-that-read-one-opener-record-and-approval-binds-the-manifest-they-write.md)
ruling 10 checks Preceptor and Site against the profile's lists and every other picklist against
`reference/medatrax-fields.md`, which holds `Level 0` to `Level 5`. ADR 0380 ruling 2 makes the
profile's saved account default the value a shift uses.

**"Memory" moved twice after ADR 0380 ruling 3 named it.**
[ADR 0391](0391-the-memory-index-keeps-everywhere-rules-flat-and-files-situation-memories-under-generated-subject-lists.md)
filed the clinician's practice rules, including the two a reused brief contradicted, under the
`clinical` subject list rather than the flat index.
[ADR 0404](0404-an-ambiguous-answer-is-read-back-and-earlier-care-status-is-asked-at-the-first-stop.md)
ruling 5 sends a rule stated during a run to `scratch/shorthand.md`, with memory holding at most a
pointer.

**A blanket delegation already meets a written rule.** clinical-note's delegated-answer rule
([ADR 0309](0309-a-delegated-answer-never-decides-what-a-written-rule-already-settles-and-a-missing-bmi-code-is-refused.md))
says a delegate settles nothing a written rule governs and quotes that rule instead. Once ADR 0380
ruling 4 is written into clinical-note's proposal rules, it is such a rule.

## Ruling 1 — the clinician rules each matched pair at the go-ahead

In `skills/batch-shift/SKILL.md` step 7, the orchestrating context runs `tools/differential_scan.py`
over every note as a **Grader handoff**, a non-authoring run, before the Review sheet. The go-ahead
lists each matched pair, a `FILLED·proposed` item whose name appears in that note's Objective
section, beside its note, and the clinician confirms or corrects each one. The list is in the
go-ahead chat message, as step 7 already lists each note's interpreted abdominal locations and as
ADR 0417 ruling 3 places the coverage lines, never on the Review sheet. A standalone clinical-note
go-ahead lists the same pairs beside the coverage line ADR 0417 already shows. The count line keeps
the words `never graded`, which `reader_remarks.coverage_lines` carries once ADR 0417 ruling 4's
selector change is built; on this commit it matches `not graded` and not `never graded`. As with the
abdominal locations, the clinician's corrections are incorporated before approval, and an approval
confirms each listed pair it does not correct. The pair reading of ADR 0380
ruling 5 is unchanged: a proposed test the Plan writes as an actual order is allowed, and a
recommendation that reached Objective as given or ordered is a defect.

Widening the descriptor-agreement reader's brief was declined because it reverses ADR 0413's decline
and that reader is blind to the clinician's answers. A new non-authoring reader was declined for the
same reason at the cost of one more subagent and graded record per shift: the only evidence that
settles a pair is what the clinician said. Reporting the count with no per-pair ruling was declined
because the later clinic shift's promotion was caught only by comparing a repair with the clinician's answers.

## Ruling 2 — Interaction Level is checked against the reference scale only

ADR 0427 ruling 10's fill builder checks Interaction Level against `reference/medatrax-fields.md`'s
`Level 0` to `Level 5`, as it does every picklist other than Preceptor and Site. The profile's
saved default fills the value under ADR 0380 ruling 2 and is not enforced. A level that differs from
the default is read on the go-ahead constants line, where ADR 0380 ruling 2 placed it.

Requiring the value to equal the profile default was declined because it refuses a deliberate
per-shift level and is the profile-comparison grader ADR 0380 ruling 2 declined. Refusing off-scale
values and also reporting a difference from the default was declined because the report repeats a
line the clinician reads before approving.

## Ruling 3 — the prior-run sentence names where memory lives

ADR 0380 ruling 3's sentence in `AGENTS.md` standing rule 6 names its sources: each pass brief is
built from the current skill, the standing rules, the per-account files that skill names (for
clinical work, the shorthand file), and memory, meaning the memory index together with the subject
list for the work being briefed. The sentence is worded for every skill whose orchestrator writes
briefs and is copied into no skill file, as ruling 3 said.

Leaving the bare word was declined because a coordinator reading only the flat index sees none of
the practice rules a reused brief contradicted. Naming the clinical sources in batch-shift alone was
declined because it breaks ruling 3's single copy and leaves coursework briefs with the same gap.

## Ruling 4 — a blanket delegation never promotes a recommendation

A blanket delegation, such as "do whatever you think is correct", never counts as the clinician's
own words for turning a recommended test, drug, or referral into an order. Read through ADR 0309's
delegated-answer rule, ADR 0380 ruling 4 governs the question: the item stays a recommendation, and
the run's `delegated-answers.md` record quotes ruling 4's sentence as its `RULE:`. This answers the
question ADR 0380's *What this does not reach* left open; no new mechanism is built.

Counting a blanket delegation as the clinician's words was declined because it reopens the
later clinic shift's path and contradicts ADR 0309. Letting a delegate promote with the go-ahead naming each
promotion was declined because approval of a whole sheet is weaker than the specific answer ruling 4
requires, and ruling 1 already puts any promotion before the clinician.

## Ruling 5 — #1596 stays one ticket

Item 6 is not split out. Its reader ruling edits batch-shift step 7, which ADR 0380 ruling 1's
build also edits. With these rulings no decision in the build spec remains, so the ticket moves from
`grilling` to `ready-for-agent`.

## What this does not reach

Ruling 1's pair listing reaches names written alike, the limit ADR 0380 ruling 5 already declares.
A clinician confirming a pair at the go-ahead is a reading, not a check the scanner can verify.
At a batch go-ahead the pair listing is a skill instruction only: ADR 0417 ruling 2 verifies the
coverage lines of the paired completion grader, and `aar_scan.COMPLETION_GRADERS` pairs batch-shift
with `filled_vitals_census`, so the shown-and-verified check does not reach `differential_scan`'s
count line on a shift. Widening that pairing is not ruled here.
Ruling 3 remains a written rule with no mechanical check that a brief opened the subject list.
Ruling 4 relies on the delegate quoting ruling 4; `delegated_answers.py` grades the record's shape
and does not decide that the quoted rule governs. The coordination with ADRs 0405, 0406, 0409,
0412, 0413, 0417 and 0427 recorded on #1596 is unchanged: whichever build lands second keeps the
other's text.

## Build checklist

Read with ADR 0380's checklist, which this amends. Its batch-shift step 7 "writes nothing"
rewording is not built: ADR 0385 ruling 1 superseded it.

- `skills/batch-shift/SKILL.md` step 7: the non-authoring `differential_scan.py` run over every note
  and the per-pair go-ahead listing (ruling 1).
- `skills/clinical-note/SKILL.md` go-ahead: the same pair listing beside ADR 0417's coverage line
  (ruling 1).
- `tools/differential_scan.py`: the Objective count line carries `never graded` (ruling 1), reading
  the item's own name and never a tail's drug-page title, as #1596's 2026-10-18 sweep recorded. The
  line reaches the go-ahead only with ADR 0417 ruling 4's `reader_remarks.py` selector change; the
  later build keeps both.
- The batch run's note population (ruling 1): `--note` takes one path and `--submission` resolves
  only a standalone note, so the step-7 handoff runs once per numbered note or the build gives the
  scanner the batch population. It never reads `shift-summary.md`, `delegated-answers.md` or
  `reread.md` as notes, which is #1805's trap ruled in ADR 0406.
- `AGENTS.md`'s terminal-grader sentence still names `filled_vitals_census.py` alone for batch-shift;
  the step-7 handoff is not a terminal grader and the build says so where that sentence stands.
- ADR 0427's fill builder: Interaction Level against the reference scale (ruling 2).
- `AGENTS.md` standing rule 6: the prior-run sentence with its named sources (ruling 3).
- `skills/clinical-note/SKILL.md` delegated-answer rule: a blanket delegation never promotes a
  recommendation (ruling 4).
