# A caught plant is named and placed on the generic side of the pair it most resembles

**Measured at:** 4c1cc8958837c7c9aa4144f187e8e879c7fce86f

[#1486](https://github.com/mshamblin5150-code/clinical-skills/issues/1486) was filed from the
after-action review of a `discussion-post` run (NUR 5042 Module 9) on 2026-10-01. A Voice reader
named the planted sentence exactly in `suspected_plant_quote`, answered every discriminating pair
with a real sentence or `no counterpart`, and the terminal completion grade failed with
`finding - planted sentence was not flagged`. The ticket recorded two later recurrences, in
`discussion-reply` and `course-assignment`, on 2026-10-04; across the three runs, four reads needed
the requirement written into the reader's brief by hand before they graded clean.
[#1654](https://github.com/mshamblin5150-code/clinical-skills/issues/1654), filed from #1476's
tracker sweep on 2026-10-09, asks which pair the caught plant must sit on. Grilled 2026-10-10
against `main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The grader and the sheet disagree.** `tools/voice_read.py` sets the plant as flagged only when some
pair answer is `generic` and quotes the planted sentence, and it separately requires
`suspected_plant_quote` to equal that sentence. A reader that only names the plant fails.
`skills/_shared/reference/voice-read.md` section 3 says the reader answers every pair, that
`suspected_plant_quote` is "the exact planted sentence the reader flags", and that "a missed plant
voids the read". It never says the plant must also be a pair's `generic` answer.

**The sheet is the only brief.** All five coursework skills point at `voice-read.md` for the
Planter and the Voice reader, and none restates the reader's brief, so the requirement has one home.

**The grader's finding names one condition for two shapes.** "Planted sentence was not flagged" is
printed both when `suspected_plant_quote` misses the plant and when it names the plant but no
`generic` answer carries it. The `course-assignment` recurrence records the orchestrator first
reading the second shape as a byte mismatch.

**The grader credits the plant on any pair.** It checks the planter's `pair_id` against the model's
pair population and never compares it with the pair that carries the reader's `generic` answer.

## Ruling 1 — the sheet states the requirement and the grader keeps it

A caught plant is the plant named in `suspected_plant_quote` **and** quoted, character for
character, as the `generic` answer on the pair whose generic half it most resembles.
`voice-read.md` section 3 states this directly after the paragraph that defines `resemblance`;
`suspected_plant_quote` alone does not record the catch.

Relaxing the grader so `suspected_plant_quote` alone counts was refused. ADR 0275 ruling 2 makes the
plant the only limb that separates a comparison from a plausible verdict, and the pair placement is
what shows the reader recognized it through the voice model rather than as an odd sentence. The
relaxed form would also grade clean a record that names the plant while answering the pair it
imitates with a different sentence marked `his`.

## Ruling 2 — the grader splits the finding

`voice_read.py` reports a plant that `suspected_plant_quote` names but no `generic` answer carries
as its own finding, distinct from a plant `suspected_plant_quote` does not name. What passes is
unchanged. The distinct finding tells the orchestrator to rebrief the reader rather than to search
for a byte difference.

## Ruling 3 — the catch counts on any pair, and the limit is declared

The pair that carries the plant's `generic` answer is the reader's judgment of the closest generic
half. It need not be the planter's `pair_id`. `voice_read.DECLARED_LIMITS` gains a row stating that
the read tests detection of the plant, not which pair it imitates; no skill or sheet copies the row.

Requiring the planter's pair was refused. A rewritten sentence can honestly resemble more than one
generic half, so a correct reader would fail, and each failure voids the read and reruns both the
Planter and the Voice reader on a fresh plant. The clinician's act on the disowned draft, which
ADR 0275 rests on, was catching what was not his, not naming the pattern it imitated. Reporting a
planter-pair yes or no beside the grade was refused: a mismatch cannot distinguish a reader who
misjudged from a plant that resembles two halves, so the line would settle nothing while reading as a
defect signal.

## Ruling 4 — a flagged plant also labeled `his` stays passing

A record that places the plant on one pair as `generic` and on another as `his` is not refused. No
recorded run has produced the shape; every recurrence was a plant named and placed on no pair.
Refusing it ahead of an instance would add a rerun path to a read that had already cost four reruns,
and ruling 1's sheet sentence already tells the reader where the plant goes. A run that produces the
shape is filed from that run.

## Ruling 5 — #1654 is absorbed

#1654's question is ruled here because ruling 1's sheet sentence has to name the pair, and two
tickets writing one sentence from different bases is the arrangement the repository refuses. #1654
closes as absorbed into #1486, whose respecified body carries the build.
