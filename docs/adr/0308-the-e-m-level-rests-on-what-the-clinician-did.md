# The E/M level rests on what the clinician did

**Measured at:** 50281e6561feec34a1f25af454589a3884c4911f

[#1473](https://github.com/mshamblin5150-code/clinical-skills/issues/1473) was filed from the
after-action review of a NUR5144 `batch-shift` run for the shift of 2026-09-30. Two of eleven note
passes set an office E/M level one step higher than the encounter supports, and the clinician
lowered both when the orchestrator put them to him before approval. One pass counted a chronic
condition as a problem addressed although the only management for it was a Plan line the pass
itself proposed; 99204 became 99203. The other reached 99205 by scoring a problem as a threat to
life that the clinician read as an undiagnosed new problem with uncertain prognosis, and by
counting his own ECG read as an independent interpretation; it became 99204 and 93000 was not
billed. Grilled 2026-10-08 against `main` at the commit above, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The ticket's "one test counts once" sentence contradicts the committed sheet.** The
`definition-independent-interpretation` entry of `reference/cpt-em-mdm-2026.md` ends: *"A test that
is ordered and independently interpreted may count both as a test ordered and interpreted."* The
same entry excludes the interpretation only when the clinician reporting the E/M service is
reporting or has reported the test, and `definition-data-analyzed` ends: *"Any service for which
the professional component is separately reported by the physician or other qualified health care
professional reporting the E/M services is not counted as a data element ordered, reviewed,
analyzed, or independently interpreted for the purposes of determining the level of MDM."* The
tracker sweep of 2026-10-03 on #1473 found the contradiction first.

**The ticket's draft paragraph restates CPT definitions.**
[ADR 0292](0292-directed-otc-agents-are-drug-management-and-modifier-25-joins-the-committed-cpt-sheet.md)
ruling 8 has `icd10-cpt` name sheet entries and never restate them, so the draft is not adopted;
the rulings below replace it.

**CPT already places a problem addressed with the reporting clinician.** The sheet's
`definition-problem-addressed` entry reads: *"A problem is addressed or managed when it is evaluated
or treated at the encounter by the physician or other qualified health care professional reporting
the service."* A note pass is not that clinician.

**Proposed tests already count, with a mark.** ADR 0292 ruling 7 counts a test the skill proposed
and the note writes as a Plan order toward data, and marks the E/M line when the level rests on it.
Its ruling 1 left open how a drug the skill itself proposes counts toward risk.

**`clinical-note` writes proposed management for history conditions on purpose.** Its *What may be
inferred* list names *"A medication proposed in the Plan for a condition in the history"* as *"the
clinical reasoning being graded; make it."*

**The threat-to-life definition turns on the evaluation and treatment.** The sheet's
`definition-threat-life-function` entry admits a symptom whose condition is significantly probable
*"when the evaluation and treatment are consistent with this degree of potential severity."*

**The ECG splits.** `python tools/procedure_codes_lookup.py 93000 93005 93010 --on 2026-09-30`
returns all three active: 93000 with interpretation and report, 93005 tracing only without
interpretation and report, and 93010 interpretation and report only. All three are flagged
`CPT DESCRIPTORS UNVERIFIED`, so a worksheet takes their wording from the rendered page.

**Modifier 25 has left the book-only list.** ADR 0292 ruling 3 brought the Appendix A entry into the
committed sheet. Under [ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md)
ruling 3 the rendered book is still required for a service date outside every committed edition and
for total time, critical care and prolonged services. Neither record states whether a private
reading from an earlier shift may stand in for a live one.

## Ruling 1 — a problem is addressed only by the clinician's own decision

A condition counts toward the problems element only where the clinician's shorthand, or his
recorded answer, shows he evaluated or treated it at this visit. A Plan line the pass proposed for
a condition the shorthand records nothing about does not make it a problem addressed, and the level
is selected without it. A proposed line on a problem the clinician did address leaves that problem
counted. `icd10-cpt` names `definition-problem-addressed` and does not restate it.

Counting the condition and marking the E/M line, as proposed tests are marked, was declined because
the pass would supply the management and then take credit for it; on this run the clinician lowered
exactly that level by hand. Applying [ADR 0297](0297-a-history-condition-is-coded-only-where-it-affected-this-visit-and-a-filled-medication-never-vouches-for-it.md)
ruling 2's concrete-change test was declined because a pass can always write concrete management,
and on this run that test would have counted the condition.

## Ruling 2 — the clinician is asked only where his answer would change the code

When ruling 1 leaves a condition out and that lowers the level, the pass selects the lower level
and puts one question to the clinician before approval, in the run's existing pre-approval
questions: whether he addressed that condition this visit, naming both levels. A yes is recorded as
his answer and counts under ruling 1. No question is asked when the condition would not change the
level. Where pre-approval questions are delegated, no answer exists and the lower level stands.

Selecting the lower level silently was declined because a condition he managed and did not write
down would then stay undercoded unless he noticed its absence. Showing the left-out condition on the
worksheet without a question was declined because an unanswered line is easy to approve past.

## Ruling 3 — a proposed drug counts toward risk on a problem the clinician addressed

A drug the pass proposes counts as prescription drug management where it treats a problem the
clinician addressed. When the level rests on it, meaning re-deriving two of three elements without
the skill-proposed drugs gives a lower level, the E/M line carries the filled mark ADR 0292 ruling 7
uses for data, naming the risk element and those drugs. A proposed drug for a condition ruling 1
left out counts for nothing. This settles the question ADR 0292 ruling 1 left open.

Never counting a proposed drug was declined because an encounter whose shorthand records a
diagnosis and a discharge without naming the drug was still treated, and risk would read low on
nearly every such chart. Asking about every proposed drug was declined because the question list
would carry one on most encounters and stop being read.

## Ruling 4 — the proposed Plan line stays when the clinician answers no

A no to ruling 2's question removes nothing from the note. The proposed Plan line stays as the
reasoning `clinical-note` is told to write, and the coding worksheet and the note's E/M paragraph
list only the problems that counted. The answer stays with the run's recorded pre-approval answers.

Removing the line was declined because it deletes graded reasoning and contradicts `clinical-note`'s
rule that the note adds orders and never subtracts them. Naming the uncounted condition in the E/M
paragraph was declined because it puts a coding explanation in the note body, which the tier-word
rule keeps clean except for the one data mark.

## Ruling 5 — a threat to life rests on the clinician's evaluation and treatment

A problem counts as an acute or chronic illness or injury posing a threat to life or bodily
function only where the clinician's own evaluation and treatment, meaning what his shorthand
orders, gives or decides about disposition, are consistent with that severity. The pass's own
reasoning and its proposed workup cannot supply that consistency. Otherwise the problem is graded at
the level his documented evaluation supports. Where the threat-to-life reading would raise the
level, ruling 2's question is put to him in the same way. `icd10-cpt` names
`definition-threat-life-function` and does not restate it.

Leaving the reading wholly to judgment was declined because the pass would then judge whether its
own account is consistent, which is the error this run made. Asking whenever the level depends on a
threat to life was declined because many emergency encounters already answer it in the
clinician's own orders.

## Ruling 6 — the clinician's own ECG read counts toward the level, and only its tracing is billed

Where the clinician's shorthand records his own read of an ECG, the worksheet counts it toward data
as a test ordered and as an independent interpretation, and bills neither 93000 nor 93010. In an
office or clinic encounter it adds 93005 for the tracing, unless the note says the tracing came
from elsewhere; in an emergency department encounter it bills no ECG code. `icd10-cpt` names
`definition-independent-interpretation` and `definition-data-analyzed` and does not restate them.

Billing 93000 or 93010 and counting the ECG toward nothing was declined because the data element
loses up to two points and the clinician made the opposite call on this run. Billing the
interpretation and counting it too is not available: both sheet entries above forbid it.

## Ruling 7 — a book-only CPT page is read live each time, and a recurring one joins the sheet

When an E/M line needs one of the CPT pages ADR 0251 ruling 3 still sends to the rendered book, the
pass reads it live through `vitalsource-chrome` and never reuses a reading from an earlier shift. A
page needed a second time is added to the committed sheet through ADR 0251 ruling 5's two-reader
procedure, as ADR 0292 ruling 3 did for modifier 25.

Reusing a private reading when the edition matches was declined because a single-reader
transcription with no verbatim comparison is the source the committed sheet was built to retire.

## Consequences recorded as derived rather than ruled

- `skills/icd10-cpt/SKILL.md` step 5 states rulings 1 through 7, naming the sheet entries rather than
  restating them, beside its existing *Orders and provenance* paragraph and the sentence it carries
  from ADR 0292 ruling 1 that the risk of a drug the skill proposes is not settled, which ruling 3
  replaces.
- `skills/batch-shift/SKILL.md` step 7 and `skills/clinical-note/SKILL.md`'s standalone
  pre-approval block carry ruling 2's question shape as a pointer to `icd10-cpt` step 5, not as a
  second copy of the rule.
- The filled data mark generalizes to name the element it rests on, so a risk mark reads
  `[SOURCE: filled - risk: <drugs>]` beside the existing data form.
- `CONTEXT.md` gains **Problem addressed**.
- #1473's *Done when* is a synthetic encounter whose only management for a history condition is a
  proposed Plan line, worked at the lower level with ruling 2's question, plus a synthetic office
  encounter with the clinician's ECG read coded under ruling 6.

## What this does not reach

Whether the clinician's documented evaluation is consistent with a threat to life remains a reading
of the note; ruling 5 fixes whose evaluation is read, not the verdict. Whether a proposed drug
treats an addressed problem is a reading. No grader derives an E/M level: `anchor_scan.py` excludes
E/M lines and `coding_freshness.py` verifies code identity, edition and date status, so every
ruling here is a required reading with no new gate claim. Preserved run records are not edited.
