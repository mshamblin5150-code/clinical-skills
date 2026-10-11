# A ledger copies its researcher word for word and a stated requirement is a qualifier

**Measured at:** a9b4492fa8693bb36bf5515993f5b3ce27cbb0f3

[#1507](https://github.com/mshamblin5150-code/clinical-skills/issues/1507) was filed from the
after-action review of a `discussion-reply` run (NUR 5144 Module 3) on 2026-10-02. It names three
gaps in `skills/_shared/reference/sourcing.md` that one run exposed: the orchestrator added a
denominator to a researcher's returned restatement when writing the ledger; four heading readers
split three to one over a draft sentence attributing "all three are required" to a guideline whose
claim heading listed the three criteria without the requirement; and a heading reader returned
`VERDICT: clean` beside `CONTEXT-VERDICT: narrows`. Grilled 2026-10-11 against `main`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The researcher's return is never retained.** The orchestrator writes the claim record from the
research agent's reply, and nothing in the run directory keeps that reply. So the ledger copy is the
only copy, and no tool can compare it with what the researcher returned.

**The refuter tests the ledger copy.** The added denominator was caught because the refutation leg
reads the record as written, not the researcher's reply. A word added before refutation is therefore
tested against the source; a word added after it is not tested by anything.

**Only the heading is fingerprinted.** `TESTED-HEADING` is the digest of the `## CLAIM:` heading
text. The sheet already requires a fresh refutation and second route after `PASSAGE` is corrected;
it says nothing about `RESTATEMENT` edited after refutation.

**The qualifier list landed the same day and does not name a requirement.** ADR 0326 ruling 1 made
every sourced record quote its limiting qualifiers: population, setting, comparator, condition,
eligibility, device, adjustment and tense. `research_ledger.py`'s `qualifier-heading-missing` row
already fails a heading that lacks a listed qualifier. A requirement, a quantifier and an
exclusivity are not on that list, and the run in this ticket predates the list's cutoff.

**The context-verdict pairing is already graded.** `tools/heading_read.py` refuses `VERDICT: clean`
beside any context verdict other than `agrees`, or `none` on a legacy `none` run, and a test pins
it. What is missing is the sentence telling the reader, beside the instruction to choose one line of
each.

**ADR 0330's `REMARK:` line is already in the heading-read template on `main`.** The ticket's
comment asked whichever build landed second to apply both; that coordination no longer applies.

## Ruling 1 — the ledger copies a researcher's returned fields word for word

The orchestrator writes a researcher's returned `RESTATEMENT` and `PASSAGE` into the ledger
verbatim. Wording the orchestrator adds is a change to the record's evidence and returns through
refutation before the record can certify a value. The existing rule that correcting `PASSAGE` after
refutation requires a fresh `REFUTATION` and `SECOND-ROUTE` extends to `RESTATEMENT`.
`research_ledger.DECLARED_LIMITS` gains a row stating that the grader cannot compare a ledger copy
with the researcher's return, because the return is not retained.

Fingerprinting `RESTATEMENT` and `PASSAGE` beside the heading was declined: it adds a required field
and a cutoff to every later ledger to catch an edit after refutation, which is not the shape this run
had, and refutation already caught the shape it had. Retaining every raw return and comparing it
byte for byte was declined because the orchestrator writes both files, so agreement would show only
that one writer copied itself consistently.

## Ruling 2 — a stated requirement, quantifier or exclusivity is a qualifier

ADR 0326 ruling 1's qualifier vocabulary widens to include a requirement, a quantifier and an
exclusivity the passage states, such as "all three are required", "most" or "only". The researcher
quotes each word for word in `QUALIFIERS`, the refuter checks the list is complete, and the existing
`qualifier-heading-missing` and `qualifier-restatement-missing` rows enforce their retention with no
grader change. The ledger cutoff, the `none` form and every other part of ADR 0326 ruling 1 stand.

The heading-read paragraph also gains a backstop: a requirement, quantifier or exclusivity the draft
attributes to the source is an added condition, and so `drifted`, unless the heading itself states
it, even when the record's restatement does. This settles the readers' disagreement for anything the
researcher's list misses.

Ruling at the heading reader alone was declined because it catches the defect at the last read before
the go-ahead, where the repair is a rewritten heading and a fresh refutation; the upstream list
catches it where it is cheapest and an existing row grades it. Widening the list without the reader
sentence was declined because a requirement the researcher missed would reach the readers with the
same ambiguity this run's readers split over.

## Ruling 3 — the heading reader is told the two verdicts must agree

Beside the instruction to choose exactly one `CONTEXT-VERDICT` line and one `VERDICT` line, the
sheet states that `VERDICT: clean` is legal only beside `CONTEXT-VERDICT: agrees`, or beside `none`
on a legacy `none` run. The brief then matches what `heading_read.py` already enforces.

A further rule treating such a return as defective and re-briefing the reader was declined because
the go-ahead already runs the grader, which refuses the record. Leaving the sheet unchanged was
declined because the reader's choice is made one paragraph away from the rule its record is graded
on, which is the gap that produced this return.

## Build checklist

- `skills/_shared/reference/sourcing.md`: ruling 1's verbatim-transcription paragraph after the
  paragraph requiring a fresh refutation when `PASSAGE` is corrected, and that sentence widened to
  `RESTATEMENT`; ruling 2's three added qualifier kinds in the `QUALIFIERS` definition, and its
  backstop sentence in the heading-read paragraph after the `drifted` definition; ruling 3's sentence
  after "Choose exactly one `CONTEXT-VERDICT` line and one `VERDICT` line from these forms."
- The record shapes and return lists in the coursework skills that brief a researcher or refuter on
  `QUALIFIERS`, wherever they enumerate the qualifier kinds rather than pointing at the sheet.
- `tools/research_ledger.py`: the `DECLARED_LIMITS` row for an uncompared transcription.
- Tests: the sheet carries each new sentence; a committed or synthetic record listing a requirement
  as a qualifier and a heading that omits it produces `qualifier-heading-missing` through the public
  command; the declared-limit row exists and is reported.

## What this record does not reach

- **Whether the orchestrator copied faithfully.** The rule is written and declared; nothing compares
  the copy with a return no file keeps.
- **Whether a qualifier list is complete.** ADR 0326's declared limit stands: code checks that each
  named qualifier appears, not that none was missed.
- **Whether a reader judged a requirement correctly.** The backstop sentence settles which way the
  reader rules; the judgment stays a reading.
