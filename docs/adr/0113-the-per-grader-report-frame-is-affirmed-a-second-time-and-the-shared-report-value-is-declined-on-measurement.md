# The per-grader report frame is affirmed a second time and the shared report value is declined on measurement

Found while grilling [#830](https://github.com/mshamblin5150-code/clinical-skills/issues/830),
2026-09-02, at `origin/main` `7ad784e`, freshness gate `FRESH` at both checkpoints. **Ruled by the
clinician on that date.** Nothing is built here; this is the record the build reads.

**This record exists to be read before the option is re-proposed.**
[#405](https://github.com/mshamblin5150-code/clinical-skills/issues/405) decision 3 kept the report
per-grader and named its own reopen condition; #830 was that condition being tested, and it argued
for the shared frame from four observations. Three of the four do not survive re-derivation. Without
this record the next architecture review re-derives the same four bullets from the same `grep` and
reaches the same conclusion, which is what happened once already.

## Measured before ruling, at `7ad784e`

Each row is #830's own claim beside what running the code returned.

| the claim | what was measured |
| --- | --- |
| `counts=` is byte-identical in three modules, with a fourth variant | **three of fifteen members' `Scan` carries a `counts` field at all**; the fourth, `tracker_bodies`, is in `NOT_MEMBERS` and outside the seam |
| six directory readers under two names | **real**, and it shares nothing with the report question |
| `not graded` is written inline 18 times in one module, and the conformance walk greps for the same literal | **real** — 54 occurrences across 13 non-test modules, of which **only 8 are members** |
| `format_report` returns `str` in some members and `list` in others | **refuted** — 15 of 15 annotate `-> str` and return a join |

The last row was taken by parsing every member and reading its annotation and return expressions.
The two `list`-returning `format_report`s in `tools/` are `voice_corpus` and `name_index`; both are
outside `MEMBERS`, and `voice_corpus` is named in `run_grader.OUTSIDE_WALK` **for exactly that
reason**, so the divergence the ticket cited as evidence for a shared frame is a distinction the
frame already draws.

**The stability evidence pointed the other way too.** #830 read five single-member `Grader` fields as
*the shape a seam takes just before the next member needs a sixth*. There are **three** —
`allow_extra_positionals` is passed by six modules and the `exit_2_limbs` / `invalid_invocation_limb`
pair by three — and all three were born on 2026-08-21 in the migration itself.

**The counts are dated and are deliberately restated nowhere else**, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms.

## What is ruled

**Ruling 1. The report frame stays per-grader, and #405 decision 3's reasoning is affirmed rather
than re-argued.** Every divergence between the reports is a clinician ruling —
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s safe-to-paste banner,
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s header qualifiers,
[#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255)'s substantiated-clean list
— and a shared `Report` value holding them as data is a real design that nothing in this grilling
gave a reason to build.

**The affirmation is on evidence and not on precedent.** #405's condition was genuinely met: the
frame stopped flexing on 2026-08-23 and four members have joined since for one line each. The
option was tested rather than deferred, and it lost on measurement.

**Ruling 2. `not graded` becomes one shared constant, imported by the members and by the
conformance walk.** The literal is written by hand in 13 modules and
`grader_conformance`'s gate walk then asserts `"not graded" in ...` against it. That is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s two copies of one rule
with a string search standing in for the second copy: an edit to any member's spelling fails
nothing until the walk quietly stops matching.

**This is `REFERENCE_HEADING`'s precedent and not a step toward a report frame.** `reference_scan`
imports the heading rule from `docx_write` rather than restating it, and `guidelines_catalog`
imports `CLASSES` from `guidelines_extract`, both on the ground that an auditor holding its own copy
of a rule can pass an artifact the producer cannot answer. One constant makes the string one object
without moving a single clinician ruling.

**The constant reaches 8 of the 13 modules that write the literal**, because the convention outran
the seam. That is stated rather than papered over: the five outside `MEMBERS` keep their own copies,
and the walk's guarantee covers members only.

**Ruling 3. `counts` is not extracted, on this repository's own stated test.**
[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) refused to extract a field
parser two graders had written identically, on the ground that *a helper two modules happen to have
written the same way is not one that exists to be depended on, and a test pinning the agreement
would forbid the divergence the copy exists to permit.* Three of fifteen is that case.

**`not graded` passes the same test where `counts` fails it**, which is why one moves and the other
does not. The literal is one policy about one convention, the checker already depends on it, and
there is no divergence anyone wants. The `counts` expression is three modules agreeing; the other
twelve do not carry the field.

## What this does not reach, declared rather than left to be found

**Whether a shared `Report` value would be a better design.** Ruling 1 says the evidence offered for
it did not survive, never that no such evidence could exist. A future frame change that made the
clinician rulings expressible as data without a spec flag reopens this on its own merits.

**The six directory readers.** They are real duplication, they are #405's own unfinished step, and
they are ruled out of scope here because they share nothing with the report question. Their
extraction and the `refusal_scan` defect found beside them are separate tickets.

**Whether the five non-member modules writing `not graded` should converge.** Ruling 2's constant is
imported by members. Whether `filled_vitals_census`, `map_scan`, `threshold_sheet`, `name_index` and
`tracker_bodies` should read from it is a question about a convention wider than this seam and is
not answered here.

**Whether any member's `not graded` rows are the right rows.** The constant makes the spelling one
object. Which rows a member gates, and whether a gated row should have been graded, stays
[ADR 0080](0080-a-gated-row-set-is-declared-per-gate-and-guarded-by-an-opt-in-walk-in-the-shared-conformance-kit.md)'s
and each member's own.
