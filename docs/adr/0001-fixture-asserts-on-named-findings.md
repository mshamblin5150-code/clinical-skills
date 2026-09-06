# Fixtures assert on named findings, not prose diffs or self-reported verdicts
<!-- no-numbered-rulings -->

`clinical-note` had no way to tell whether an edit improved it, so every change was settled by opinion. The regression set that fixes this compares runs by checking **named clinical findings** against the output text — "snuff box tenderness appears in the Assessment or the Plan" — rather than diffing the note against a reference or reading the drift-matrix verdicts the skill emits about itself.

## Considered options

**Diff the whole note against a reference.** Rejected: most of a note is prose that is legitimately free to vary run to run. A bar that trips on style is ignored within three runs, and an ignored bar is worse than none.

**Use the ten drift-matrix verdicts from step 7.** This was the obvious choice and the one the originating issue proposed. Rejected because the verdicts are the skill grading itself: a run that misses snuff box tenderness is precisely the run that also emits `row 2: PASS`. The signal is blind to the defect class the set exists to catch — every one of the five known defects would pass.

**Assert on named findings, checked externally.** Chosen. Immune to prose variation, and cannot be gamed by a skill that grades itself generously, because the check reads the note rather than the verdict.

## Consequences

Assertions have to be written by hand, in the clinician's words, and they only cover findings someone thought to name — the set has no opinion about defects nobody has seen yet. That is accepted: it catches known regressions reliably, which is the job.

The pass bar is split accordingly. Drift assertions are binary and must all pass, because that defect class is safety-relevant and stable. Softer claims — differential depth, screening content — are counted and reported but do not fail a run, so the set stays readable as the wording moves.
