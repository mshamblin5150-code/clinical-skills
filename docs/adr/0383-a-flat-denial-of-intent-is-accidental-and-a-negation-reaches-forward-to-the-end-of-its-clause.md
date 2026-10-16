# A flat denial of intent is accidental and a negation reaches forward to the end of its clause

**Measured at:** a1c440906ee7d1594dd7bcb6e66a21d7d6e54f1b

[#1636](https://github.com/mshamblin5150-code/clinical-skills/issues/1636) was filed from triage of
[#1471](https://github.com/mshamblin5150-code/clinical-skills/issues/1471), which repaired a
negation written inside the word (`unintentional`, `non-intentional`) and left a negation written
in prose out of scope on purpose. The clinician ruled every point below on 2026-10-16. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

`anchor_scan._drug_column_agrees` reads each intent signal by keyword presence alone. Driven at the
commit above, each set of agreeing words on the left is accepted only by the column on the right:

| agreeing words | column accepted |
| --- | --- |
| `ibuprofen ingestion, not intentional` | Poisoning Intentional self-harm |
| `ibuprofen ingestion, denies self-harm` | Poisoning Intentional self-harm |
| `acetaminophen overdose, denies suicidal intent` | Poisoning Intentional self-harm |
| `ibuprofen ingestion, no suicidal ideation` | Poisoning Intentional self-harm |
| `ibuprofen ingestion, no assault` | Poisoning Assault |
| `ibuprofen ingestion, no vomiting, intentional overdose` | Poisoning Intentional self-harm |
| `intentional ibuprofen overdose; patient denies` | Poisoning Intentional self-harm |
| `acetaminophen ingestion, possibly intentional self-harm; patient denies` | Poisoning Undetermined |

The first five are the defect: a sentence ruling intent out is read as asserting it. The last three
are already correct under the rulings below and must stay so.

[ADR 0248](0248-the-index-tables-ship-and-an-index-path-carries-only-a-code-s-stem.md) ruling 6
makes accidental the guideline's default where the note states no intent, and reserves undetermined
for a note saying intent cannot be determined. Its ruling 7 makes a hedged self-harm or assault
intent agree only with undetermined.

## Ruling 1 — a flat denial of intent agrees only with accidental

When the agreeing words establish a poisoning and every self-harm, intentional or assault signal in
them is negated, the check accepts only the Poisoning Accidental (unintentional) column. A denial
says at least as much as silence, and silence already takes accidental under ADR 0248 ruling 6. It
also keeps `not intentional` on the same column as `unintentional`, which #1471 placed there.

Undetermined was declined because ADR 0248 ruling 6 reserves it for a note saying intent cannot be
determined, and a denial does not say that. Refusing to grade and sending the case to a reader was
declined because the guideline settles it mechanically, and every such note would leave the run
incompletely scanned.

## Ruling 2 — the negation cues are a closed list

A negation cue is one of `not`, `no`, `denies`, `denied`, `without`, `negative for` and `never`,
matched as whole words in any case. Any other word negates nothing.

## Ruling 3 — a cue reaches forward to the end of its clause

A cue negates the intent signals that follow it up to the next comma, semicolon or period, and
nothing before it. So `no vomiting, intentional overdose` keeps its intent, and
`intentional ibuprofen overdose; patient denies` keeps its unhedged intent and stays self-harm: the
clinician's unhedged word is the clinical determination, and a patient's contrary statement does
not override it. A clinician who means to record doubt writes the hedge, and ADR 0248 ruling 7
already sends a hedged intent to undetermined.

Sending an unhedged intent followed by a trailing denial to a reader was declined because it adds
machinery and makes every documented denial an incompletely scanned run. Letting a cue anywhere in
the words cancel every intent signal was declined because it reads a real intentional overdose as
accidental whenever the note negates something else nearby.

## Ruling 4 — a hedge still wins over a denial

Negation is applied first: a negated intent signal is removed before the hedge, self-harm,
intentional and assault tests run. A hedge then attaches only to an intent signal left standing. So
`possibly intentional self-harm; patient denies` stays undetermined, because its denial follows the
intent words and negates nothing, and the existing ADR 0248 ruling 7 test keeps passing unchanged.

## What this does not reach

Clause boundaries are punctuation only. A note joining two clauses with `and` or `but` and no comma,
such as `denies nausea but intentional overdose`, reads the intent as negated; the cue list is
closed, so this is a declared limit of the clause rule and not a matcher to widen. A negation
written as a separate sentence before the intent words does not reach them. A double negation is
read as a single one. No committed real note carries a `T36`–`T65` poisoning code, which
`anchor_scan.DECLARED_LIMITS` already names; the cases here are synthetic controls and do not erase
that gap.

## Build checklist

- `tools/anchor_scan.py`: in `_drug_column_agrees`, remove each intent signal that a ruling 2 cue
  precedes within its clause before computing the hedge, self-harm, intentional and assault flags;
  add the clause-boundary limit to `anchor_scan.DECLARED_LIMITS`; extend
  `AGREEMENT_READER_INSTRUCTIONS` so a flat denial of intent agrees with accidental.
- `tools/test_anchor_scan.py`: the five defect cases above agree only with accidental; the three already-correct cases keep their columns; `without
  suicidal intent`, `negative for self-harm` and `never intentional` agree only with accidental; each
  case is driven in lower, upper and title case across all six `DRUG_COLUMNS`.
- `skills/icd10-cpt/SKILL.md` already carries the coding rule from this record; the build removes
  only its sentence saying `anchor_scan.py` does not yet read a denial.
