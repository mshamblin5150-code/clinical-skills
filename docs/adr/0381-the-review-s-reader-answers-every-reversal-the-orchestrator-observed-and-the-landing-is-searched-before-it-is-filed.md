# The review's reader answers every reversal the orchestrator observed, and the landing is searched before it is filed

**Measured at:** c08aeb5d03992f4736d4a1bd93f126aae3b8ceb0

[#1601](https://github.com/mshamblin5150-code/clinical-skills/issues/1601) was filed from the
after-action review of a `discussion-reply` run (NUR 5042 Module 10), 2026-10-07. Its fresh
classifier missed two reversals the orchestrator had observed, and the orchestrator added them
afterward. The ticket proposed a sentence for `skills/aar/SKILL.md` step 2 handing the classifier
the orchestrator's own list of reversals as candidates to re-derive. A comment on 2026-10-08 added a
second gap: the classifier named a ticket for a landing although it has no tracker access, and the
orchestrator's own search found the defect already filed under another number. The clinician ruled
every point below on 2026-10-16 against `main` at `cf590bcb`, where the freshness gate read `FRESH`.
The commit above is this record's first draft on that base; a reader's re-derivation of that draft
corrected its facts and returned two new questions, ruled as the last paragraph of ruling 5 and the
sustain bar in ruling 1. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The miss recurs, and it is mostly not the orchestrator's own reversal.** Every review record under
`scratch/runs/*/aar/` beneath the 213 registered checkouts was read, counting only. 32 records hold
507 correction blocks. In 5 of them, across 3 records, the classifier's recorded verdict was none or
not returned and the orchestrator added the correction; their correctors are an agent or tool 3
times, the clinician once, and the orchestrator once. Had the classifier never missed a reversal,
the count would read 0, provided an overruled rejection is never recorded as `none`; the records do
not separate the two. The matcher keys on a `CLASSIFIER:` value opening `none` or `not returned`, or
an `ORCHESTRATOR:` value opening `added`, so it is a floor: an added block worded otherwise is not
counted. The count was taken by a subagent and re-derived in a second process before it was written
here.

**An added correction is disposed of by the context that erred.** [ADR
0109](0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md)
ruling 8 lets the orchestrator overrule the classifier and record both verdicts, which is how the
five were added and why they are visible. But the classification of an added correction, its
disposition included, is then the orchestrator's alone, which is the self-grading ruling 2 of that
record exists to prevent.

**A prose input is the shape [ADR
0282](0282-other-skills-second-readers-keep-their-context-and-the-review-sees-the-case-study-s-go-ahead.md)
refused.** Its rejected options decline adding the departure file to the classifier's input list in
prose, because nothing fails when an orchestrator forgets to attach it and the extract is already
the reader's whole population. Its ruling 3 carries the departure list into the extract as an
extractor-written entry instead. The `prior-review` entry is the other precedent: a previous
classifier's return the next reader must re-derive and may not adopt.

**The classifier's return carries no ticket.** Step 2's required return lists the correction, the
corrector, who was in error, a disposition, and the sustains. The record's `TARGET` line is the
orchestrator's to write. Step 3 says to file the defect and never says to search first. The skill's
only search-before-filing instruction is step 4's, for threshold-sheet conflicts UpToDate won, which
it says are not corrections. The general rule lives in `CLAUDE.md` and
`docs/agents/issue-tracker.md`, and `CLAUDE.md` itself says a consumer of the skills needs neither.
The same count found one `CLASSIFIER:` line naming a ticket. Orchestrator reasons recording a
landing on an existing ticket are common, but two matchers over the same records gave 9 and 20
depending on the wording each accepted, so the figure settles only that a moved target is ordinary,
not how often.

## Ruling 1 — the reversal candidates reach the reader through the extract

Before each **Review round**, the orchestrator writes a per-round file of **Reversal candidates**
under `<run-directory>/aar/`, keyed to that round so an earlier round's file is never read again.
Each line names one reversal in the orchestrator's own words, describing conduct and quoting no run
material. `aar_scan.py --extract` carries the file as one entry of its own kind in
`aar_scan.ENTRY_KINDS`, extractor-written, so no correction may rest on it; the classifier must find
the transcript entry each candidate refers to. Unlike the departure entry, no sustain may rest on it
either, and the grader refuses one that does. ADR 0282 ruling 3 let a sustain name the departure
entry because it holds the clinician's go-ahead, a settled ruling; a candidates entry holds the
orchestrator's own claim, and a sustain resting on it would be the erring context attesting to
itself. A true sustain can always cite the transcript entry where the right thing was settled. The
classifier's input list stays the extract and the memory index, as ADR 0282 ruling 3 left it. ADR
0109 ruling 8's *the population is not the orchestrator's to touch* stands: the entry adds
orchestrator-authored text to the extract, as the departure entry adds the clinician's, but removes
nothing and can carry no correction.

A sentence in step 2 was declined on ADR 0282's ground. A blind first read followed by a second
fresh classifier for whatever the orchestrator adds was declined for its second run and the grader
rule proving it happened; it would have kept an honest measure of the first reader's misses, and
that measure is the cost recorded below. Declaring the miss only was declined because every added
correction would stay self-graded.

## Ruling 2 — the file is required every round, and `none` is an answer

The extract refuses to write an extract or baseline when the round's candidates file is absent, as
it refuses without the run's `reread.md`. A round with nothing to list writes `none`. Rounds
extracted before the build's cutoff keep their historical grade. An optional file was declined
because a forgotten list would read exactly like an empty one. Requiring the file only after an
earlier round's miss was declined because it misses the first round, which is this ticket's case.

## Ruling 3 — the reader answers every candidate, and the grader counts the answers

The review record carries one answer for each candidate: the extract entry identifier of the
correction it became, or `not a correction` with a substantive reason. The grader counts the
candidates in the file and refuses a record that leaves one unanswered. When the orchestrator
disagrees with a rejection, ADR 0109 ruling 8 applies unchanged: both verdicts, who overruled whom,
and a reason. A return that merely lists ordinary corrections was declined because a dropped
candidate and a rejected one would read alike; an ungraded per-candidate answer was declined because
nothing would fail when it was missing.

## Ruling 4 — a candidate is every reversal observed, whoever corrected it

The file lists reversals by the clinician, by an agent or tool, and by the orchestrator. Listing
only the orchestrator's self-corrections would have missed four of the five recorded misses; leaving
out the clinician's would have missed one.

## Ruling 5 — the classifier names no ticket, and the orchestrator searches before it lands

Step 2 states that the classifier returns no ticket numbers, and the orchestrator ignores any it
volunteers. Before filing or citing a landing for a `tracker-ticket` or `skill-file` correction, the
orchestrator searches open and closed issues for the defect; a match receives the landing as an
issue comment, whose address step 4 already accepts, and otherwise a new ticket is filed. Giving the
classifier tracker access was declined because placing a correction on the tracker is the work skill
step 3 assigns to the orchestrator, and the classifier's part is the disposition. Relying on
`CLAUDE.md` was declined because the review skill is the file every run reads.

**The search is graded.** For each `tracker-ticket` or `skill-file` correction, the grader requires
a successful `gh` command searching the tracker's issues in the round's transcripts before the
command that printed the correction's landing address; a landing with none is a finding. Rounds
extracted before the build's cutoff keep their historical grade. The evidence is the one
`_successful_gh_call` already opens: the raw transcripts named by the extract, whose tool calls
carry their full command text, which the extract itself drops. Leaving the rule unchecked was first
ruled on the false premise that no grader could see a command's text, and was reversed once the
grader's own landing check showed otherwise.

## Ruling 6 — #1759 stays separate

[#1759](https://github.com/mshamblin5150-code/clinical-skills/issues/1759) asks how far the
classifier may trust an agent's narration of a tool result it cannot see. A reversal candidate is
the orchestrator's narration of a reversal, so whatever #1759 rules about narrated causes covers
candidates too, and that ticket receives a note saying so. Rulings 1, 2, 4 and 5 do not depend on
its outcome; if #1759 adds a state for a cause the extract cannot verify, ruling 3's answer set
gains it. Widening this record to absorb it was declined because one of its remedies, carrying tool
output in the extract, raises privacy and size questions unrelated to what the reader is handed.

## Consequences

**Every reversal the orchestrator saw ends in an independent verdict**, confirmed or rejected with a
reason, before any of it is disposed of.

**`CONTEXT.md` gains *Reversal candidate*** under *Review*, distinct from **Correction**, which is
the reversal itself as it stands in the transcript.

**The build touches `tools/aar_scan.py`'s extract, entry kinds and grade, the review record's
grammar, and `skills/aar/SKILL.md` steps 1 to 4.** #1601 is respecified to these rulings. Three
mechanics are the build's to settle and are not ruled here: the key by which a record's answer names
one candidate line, the required file's treatment on `--rebuild-round` under [ADR
0271](0271-a-notification-entry-is-named-by-its-row-and-a-refused-round-is-rebuilt-against-its-own-entries.md),
and the new kind's place beside `departure-list` wherever the extractor special-cases that kind in
watermarks and rebuild counts.

## What this does not reach

**A careless `none`.** The file's presence is graded and its completeness cannot be; ADR 0109 ruling
8's ceiling, an orchestrator that under-reports, applies here as well.

**Whether the reader would have found a listed reversal without the list.** The record shows which
corrections came from candidates and which the reader found alone, but not what the reader would
have missed unaided. Ruling 1's declined second reader was the only instrument for that.

**Whether the tracker search was adequate.** Ruling 5's grade shows that a search ran before a
landing, not that its terms would have found the defect; a search for the wrong words passes.

**An error nobody contradicted.** It is no reversal, so it is outside the population, as ADR 0109
rulings 1 and 7 declare. A reversal the orchestrator did not observe is still in the extract, which
the reader reads whole; it is lost only if the reader misses it too. 