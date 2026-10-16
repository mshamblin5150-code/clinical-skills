# A site-bearing symptom code is chosen from the note's location word and the grader keeps its route-start test

**Measured at:** 34ef08900e3ff22d50f4b2286fe47805d3e0e7c2

[#1590](https://github.com/mshamblin5150-code/clinical-skills/issues/1590) was filed from the
after-action review of a `batch-shift` run on a NUR5144 clinic shift, 2026-10-06. A coding writer
gave a reducible groin bulge, which the note placed in the abdominal wall, the differential code
`R19.00 Intra-abdominal and pelvic swelling, mass and lump, unspecified site`. The blind
descriptor-agreement reader found no index route from the note's words to that code, and the writer
replaced it with `R22.2 Localized swelling, mass and lump, trunk`. The ticket proposed a
`skills/icd10-cpt/SKILL.md` sentence telling the writer to read "the category's Excludes1" before
choosing a swelling or mass code. The clinician ruled every point below on 2026-10-16, against
`main` at the commit above, where the freshness gate read `FRESH`. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The tabular states the R19.0-/R22 split on one side only.** `tools/icd10_lookup.py R22.2` prints
`excludes1: intra-abdominal or pelvic mass and lump (R19.0-)` and `excludes1: intra-abdominal or
pelvic swelling (R19.0-)` on `R22.2` itself, not on the `R22` category. `R19.00` inherits only
`acute abdomen (R10.0)` from `R19` and `abdominal distension (gaseous) (R14.-)` and `ascites
(R18.-)` from `R19.0`. Nothing on the code the writer chose points to `R22`. So the proposed
sentence, which sends the writer to the Excludes1 of the code being chosen, would have shown the
writer of this case notes that never mention a wall, groin or skin mass.

**The alphabetic index offers the wrong path from an organ-system word.** `--index abdominal` traces
`Mass > abdominal -> code R19.00`, while `--index trunk` traces
`Mass > localized (skin) > trunk -> code R22.2` and `Swelling (of) > localized (skin) > trunk ->
code R22.2`. The index has no `Mass` subterm for `groin`, `inguinal` or `abdominal wall`. A writer
who starts the trace from the organ system the complaint suggests reaches `R19.00`; one who starts
from the note's location reaches `R22.2`.

**The grader treats the wrong route and the right route the same.** Driven on 2026-10-16 through
`_route_status` in `tools/anchor_scan.py`: `Mass > abdominal -> code R19.00` and
`Mass > localized (skin) > trunk -> code R22.2` both grade valid on the agreeing words "Reducible
groin mass", and both grade invalid on "Reducible groin bulge". The test compares only the route's
first main term with the note's words, as
[ADR 0312](0312-the-blind-brief-states-the-whole-route-start-test-and-a-retry-carries-only-the-grader-s-finding-lines.md)
records and states to the blind reader. The
[ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md)
Writer self-grade runs the same test, so it passes a site-mismatched code as well.

**A whole-path test would refuse the correct code.** The later entries of the `R22.2` route,
`localized (skin)` and `trunk`, do not occur in the words "Reducible groin mass". A rule requiring
every step of the path to appear in the note's words would refuse `R22.2` on the very note where it
is right.

## Ruling 1 — a site-bearing symptom code is traced from the note's own location word

`skills/icd10-cpt/SKILL.md` gains a general rule, placed after the paragraph that begins
"**`Z03.-` is not proposed here**". For any symptom code whose descriptor names a body site, the
writer traces `--index` from the location words the note uses, never from the organ system the
complaint suggests. The writer then looks up both the candidate code and the code the index gives
for the note's location, and reads the Excludes1 of each, because the tabular can state a split on
one side only. `R19.00` against `R22.2` is the worked example, with the trap path and the correct
path above, and the observation that `R19.00`'s own notes say nothing of the split.

The paragraph says that a site the note does not describe fails the blind reader's
descriptor-agreement judgment and the writer's own reading. It does not say the grader fails it.

Adopting the ticket's sentence as written was declined because it sends the writer to the notes of
the code already chosen, which in the recorded case are silent. A rule naming only the
`R19.0-`/`R22.-` pair was declined because the defect is the starting word of the trace and the
one-sided placement of an Excludes1, and neither is particular to that pair.

*Superseded 2026-10-16.* The words "For any symptom code whose descriptor names a body site, the
writer traces `--index` from the location words the note uses" are widened by
[ADR 0378](0378-a-code-is-also-traced-from-the-note-s-site-cause-or-type-word-and-the-trigger-widens-adr-0373-s-location-rule.md)
ruling 1: for any code, the writer also traces from each site, cause or type word the note names,
and #1598 builds the one paragraph. The worked example, the instruction to read both codes'
Excludes1, and the placement survive.

## Ruling 2 — the grader keeps its route-start test and the site stays a reading

`_route_status` and the Writer self-grade are unchanged. Whether a later step of an index path, such
as a site, is reached by the note's words remains the blind reader's judgment, as ADR 0312 ruling 1
already states to that reader. The new skill paragraph is the writer-side guard.

A whole-path test was declined on the measurement above: it refuses the correct `R22.2` route on
this note. A whole-path test with a body-site synonym table was declined because the code set
supplies no such table. The repository would have to author and defend one, and each gap in it
would be either a false refusal or a silent pass. That is the instrument-widening this repository
declines in favor of declaring coverage.

## What this does not reach

Ruling 1 is a reading instruction. Nothing mechanical shows that a writer traced from the note's
location word or read both codes' notes, and the Writer self-grade still passes a site-mismatched
route whose first main term the note contains. The blind reader caught this case on the recorded
shift; a reader who misjudges a site in the same way as the writer is not caught, which is the
Shared-reader blindness the Writer self-grade already carries. The second item in #1590, a
differential carried as a coded entry while its establishment waited on a pending exam and tests, is
a miss of the existing step 3 rule and is not ruled here.
