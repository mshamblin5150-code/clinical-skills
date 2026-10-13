# A case study's routing walk is a written record and a red-flag exception goes to the clinician

**Measured at:** ac4bfe0f2866eb172b84c7bb591259387df193c6

*Re-declared from `50802feb` on 2026-10-12 for the Ruling 9 correction below. Between the two bases
`style.md` section 7's abbreviation bullet and one `practicum-case-study` step 9 paragraph changed
(#1791); neither is a context line of any #1576 hunk, so the measurements below were re-checked and
stand.*

[#1576](https://github.com/mshamblin5150-code/clinical-skills/issues/1576) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4). It proposed eleven plan,
prescription, education and repair rules for `skills/practicum-case-study/SKILL.md` and
`skills/_shared/reference/style.md` sections 5 through 8, each learned from a reader correction
made one round at a time. Grilled 2026-10-12 against `main`; the clinician ruled every point below
in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Ten of the eleven hunks still apply to `main`.** Each diff's context lines were compared with
both files at the commit above. Section 9's trailing context line, the old credential sentence in
`style.md` section 8, was replaced by the paragraph opening *Credentials are account values*; the
insertion point, after the route-change bullet, is unchanged. The step 9 paragraph sections 4 and 6
touch now has the [ADR 0348](0348-a-revised-draft-is-shown-with-a-computed-change-list-and-the-aar-command-names-its-record-file.md)
Revisions pointer on the line above it and does not conflict with either hunk.

**[ADR 0361](0361-a-case-study-s-differential-ranks-by-three-defined-standings-and-its-pre-review-walks-are-written-records-a-grader-shapes.md)
set the pattern this record follows, and its build has landed.** A walk that recurred round after
round became a written record in the run directory, and `checks_ledger` refuses a record that is
absent or carries an entry with no outcome. The build added `emergency-walk.json`, `bar-walk.json`
and `fact-trace.json` under the `pre-review-walks` check. A rule a dedicated reader already
checks every round stayed a drafting instruction.

**Two existing rules already reach parts of this ticket.** A stop criterion is a clinical claim
that takes a source (`style.md` section 8, ruled 2026-08-19), and `PROPOSED` already holds a claim
the evidence does not settle. The fresh `the leftovers of every change after the first draft`
reader runs after every round of changes, and its `clean` names the changes it walked.

## Ruling 1 — sections 1, 3 and 5 become one routing walk, written before the first reader round

The three sections state one property: every warning sign, MDM promotion trigger, ordered test and
deferred action sends the patient or the work to a **Receiving item** the Plan holds. Before the
first reader round the run writes one record in the run directory, outside the graded document,
listing each of them beside its Receiving item. Each warning sign also stated in the Patient
Education shows that the Plan and the Education give the same Receiving item. Where the presenting
complaint overlaps the warning list, each warning sign is stated as a change from the presenting
baseline (section 1). A deferred action's Receiving item is a visit or call this Plan schedules
whose agenda lists it, and a deferred decision is timed inside its cited source's window
(section 3). Three plain instructions were declined: section 5 recurred across roughly a dozen
reader rounds, and an unrecorded walk cannot be told apart from a skipped one. A record with no
grader check was declined for the same reason.

## Ruling 2 — the grader refuses a missing routing walk or a row with no Receiving item

`checks_ledger` refuses the routing record when it is absent, malformed, or carries a row that names
no Receiving item, joining the pre-review walk records Ruling 7 of ADR 0361 created. The check
reads shape only; whether each Receiving item is clinically right stays the decisions reader's
judgment. It takes its own row in `reference/completion-check-starts.tsv`, so a run already graded
on ADR 0361's three walks is not refused for a record that did not exist when it was drafted.

## Ruling 3 — the supply-to-endpoint rule binds fixed-course drugs only

Section 2 is adopted for a drug whose stop criterion is a fixed course: a stated duration or a
dated count. Its `Disp:` quantity times one plus the refill count covers that course and no
further, the refill count is never cut to repair an overshoot, and both are recomputed whenever
either changes. A drug whose stop criterion is a reassessment keeps the ordinary supply with the
house maintenance count of 3 refills. Applying the rule to every continuing drug was declined,
because it would force a seven-tablet supply on a chronic drug reassessed at four weeks. Dropping
*no further* was declined as allowing the overshoot the Rx reader caught. The rule stays prose for
the Rx reader. A mechanical supply check was declined on
[#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300)'s measurement, which
found parser rows over prescription tables firing on correct tapers and repeat doses.

## Ruling 4 — the whole-draft search for a changed rule is a drafting instruction

Section 4 is adopted as written. An author's per-change search record was declined: the leftovers
reader already reads every round independently and substantiates its verdict, and a record the
author writes about the author's own search is the same pass grading itself
([ADR 0001](0001-fixture-asserts-on-named-findings.md)'s reasoning).

## Ruling 5 — an exception that narrows a red-flag rule goes to `PROPOSED`

Section 6 is adopted in a stricter form. A repair that would add an exception narrowing a red-flag
rule is not placed. The draft keeps the single rule and the exception goes to `PROPOSED` for the
clinician; whatever the clinician rules is carried through the routing walk. The ticket's test, *if the
exception splits their routing or weakens one*, was declined because nearly every exception
weakens the trigger it carves out of, so the test is the same rule stated vaguely. Letting the
agent add a consistently carried exception was declined: narrowing a red flag decides when a
patient does not come back, and this run's carve-out was wrong and reverted.

## Ruling 6 — every numeric trigger names its source in the routing walk

Section 7 is adopted, and each routing-walk row carrying a numeric value names the threshold-sheet
row or the run's claim record it was quoted from. The grader refuses a numeric row that names no
source. A severe-range value goes where its source sends it, and no trigger sits inside the range
the source calls normal; both stay a reader's judgment. A grader comparison of the row's number
with the source's was declined: digit-string comparison rejects a correct unit conversion, which
`research_ledger` already declines, and the threshold sheets do not yet cover most topics.

## Ruling 7 — the rejected-alternative test is a drafting instruction

Section 8 is adopted as written, including its clause about every product sharing a contraindicated
ingredient. An author's record was declined on Ruling 4's ground: the decisions reader already
runs the same test independently.

## Ruling 8 — a stop rule moved to a measured value takes a claim record

Section 9 is adopted. The measured value is a stop criterion and so takes its own step 3 claim
record, and it reaches `PROPOSED` only when the evidence does not settle it. The rule does not
reach an as-needed order, whose symptom is its indication rather than a stop rule. Sending every
such choice to `PROPOSED` was declined: a measurement the guideline names outright needs no ruling.
Declining the section was rejected because this run's symptom-keyed stop rule passed the existing
sourcing rule.

## Ruling 9 — the `PROPOSED` file is reconciled in both directions every round

Section 10 is adopted with a different mechanism. Before each reader round, every entry in
`proposed-<date>.md` is checked against the placed draft: current entry numbers, every place it
applies, the clinician instruction quoted, and its source stated correctly. Every narrowing in the
draft has its `### DEPARTURE:` entry. An entry not tied to draft text stays until it is answered or
withdrawn. Rebuilding the file from the draft, as written, was declined because some entries live
only in the file, such as the visit-date assumption ADR 0361 Ruling 1 writes before drafting, and a
rebuild drops them unnoticed. The `the leftovers of every change after the first draft` reader takes
`proposed-<date>.md` as an input, and an entry left stale by a change is one of its leftovers; that
brief belongs to [#1577](https://github.com/mshamblin5150-code/clinical-skills/issues/1577). A
grader shape check was declined, because whether an entry is current is a reading with no closed
outcome vocabulary.

Correction, 2026-10-12: this ruling formerly closed *The rule stays prose; the leftovers and
decisions readers already read this file.* That was false. The leftovers reader reads only the
draft and the description of the round's changes, and the decisions reader's brief checks only for
a narrowing the departures section omits. The clinician then ruled that the leftovers reader takes
the file, so the ruling no longer rests on the false premise.

## Ruling 10 — a cited sentence carries its heading's qualifiers and nothing wider

Section 11 is adopted with its bound stated. The claim a cited sentence makes carries every
qualifier its claim heading carries (population, drug class, condition, time window) and nothing
wider. Facts about this patient, from the faculty material, may stand beside it. The ticket's
*adding nothing it does not state* was declined as written because it forbids applying the claim
to the case. The step 9 heading read stays the detection, so no author's record was added.

## Ruling 11 — **Receiving item** is defined in `CONTEXT.md`

The term names the Plan item a warning sign, trigger, abnormal result or deferred action is sent
to. *Destination* was declined because it is the head of **Destination guard**, *disposition*
because the glossary already carries it in two senses, and *route* because several entries list it
to avoid. Leaving the word undefined was declined, because Ruling 2's refusal rests on it.
