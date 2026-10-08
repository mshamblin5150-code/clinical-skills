# The refusal substitute bind lives in the agreement grader and binds every code the field names

**Measured at:** f9f8bf1c87bf22c6ea1ffef3312705f8f00f6b27

[#1452](https://github.com/mshamblin5150-code/clinical-skills/issues/1452) was filed from the
after-action review of a `batch-shift` run. In six of eleven worksheets a refusal's
`proposed instead` code was present only in the differential, `refusal_scan.py` passed all six, and
the defect surfaced only in the shift's blind descriptor-agreement read. The ticket proposed moving
that bind into `refusal_scan`. Grilled 2026-10-08 against `main`, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The defect is now caught at write time.** [ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md)
was built and merged the same day: every coding writer grades its own worksheet with
`anchor_scan --agreement-read` before hand-off, and that grader already refuses a substitute absent
from the for-entry codes.

**No run invokes `refusal_scan`.** No skill, `AGENTS.md` step, or completion grader calls it; only
its own tests and the maintainer do.

**The agreement grader's substitute bind is narrower than ADR 0243 ruling 5.** Ruling 5 says the
substitute must appear as a proposed code above. The grader reads only the first code-shaped token
after `proposed instead:` and compares it with the for-entry ICD-10-CM codes alone. Driven through
`main` on synthetic worksheets proposing `M79.675` and CPT `10060` for entry, with `B07.0` only in
the differential:

| `proposed instead` field | grader result |
| --- | --- |
| `M79.675`, a proposed diagnosis | passes, correctly |
| `B07.0`, differential only | refused, correctly |
| `10060`, a proposed procedure | refused, wrongly |
| `nothing` with a reason | passes, unread |
| `M79.675 ..., with B07.0 ...` | passes |
| `B07.0 ..., with M79.675 ...` | refused |

**No committed agreement control carries an affected shape.** Every `proposed instead` field in the
agreement and worksheet-grammar controls names one proposed diagnosis code. The preserved
`fixtures/filled-anchor/run-2` worksheets carry all three affected shapes and are not graded by the
agreement read.

## Ruling 1 — `refusal_scan` is not extended; the bind lives in the agreement grader

The substitute bind is graded only by the agreement grader, which the writer self-grade and the
blind read both run. `refusal_scan`'s declared limit on the substitute is reworded to name that
grader as where membership is checked, leaving the clinical rightness of the substitute a reading.
Adding the row to `refusal_scan` was declined because it would be a second copy of one rule in a
tool no run invokes, and would force a ruling on a preserved record that cannot be edited. Closing
the ticket outright was declined because the false alarm and the unread shapes above would stand in
a check every worksheet now passes through.

## Ruling 2 — a substitute is checked against every code proposed for entry, of any system

A `proposed instead` code passes when it appears among the worksheet's for-entry codes, diagnosis
or procedure. A same-system restriction was declined because ADR 0243 ruling 5 does not state one
and no recorded case needs it. Counting procedure substitutes as unread was declined because it
trades a false alarm for a blind spot.

## Ruling 3 — every code the field names must be proposed, wrapped lines included

Every code-shaped token in the `proposed instead` field, including its indented continuation lines,
takes the bind. A code named in that field only to set it aside is refused; such an aside belongs on
the refusal's `note:` line, and the skill says so beside the template. One code per field was
declined because it refuses everything this rule refuses and correct two-code fields too. Binding
the first code only was declined because detection would then depend on word order.

## Ruling 4 — a substitute naming no code is a finding

A `proposed instead` field with no code-shaped token is refused. A concern the encounter leaves
nothing codable for takes no refusal record under ADR 0243 ruling 4, and a considered diagnosis is
still coded by what the encounter supports. Allowing it with a reason was declined because the one
recorded instance is the record ruling 4 says should not be written. Counting it as unread was
declined because it files a known defect under a reading failure.

## What this does not reach

Whether the substitute is clinically the right code remains a reading. A code-shaped token that is
not a code, such as a dosage string shaped like a five-digit procedure number, would be read as a
substitute. `refusal_scan` keeps passing every shape above, by ruling 1.
