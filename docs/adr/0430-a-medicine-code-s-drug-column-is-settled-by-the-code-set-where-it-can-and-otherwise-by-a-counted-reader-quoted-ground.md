# A medicine code's drug column is settled by the code set where it can and otherwise by a counted reader-quoted ground

**Measured at:** 592067b0598e89b7fae3429b31459b713ce157e8

[#1889](https://github.com/mshamblin5150-code/clinical-skills/issues/1889) was filed from the
grilling of [#1814](https://github.com/mshamblin5150-code/clinical-skills/issues/1814), whose
record, [ADR 0414](0414-a-toxic-effect-code-takes-its-column-from-intent-alone-and-the-reader-brief-states-the-grader-s-own-column-words.md)
ruling 3, sent the medicine half of the drug-column question here. Grilled 2026-10-19 against
`main` at the commit above, where the freshness gate read `FRESH`. The clinician ruled every point
below in that session, one question at a time. **Nothing is built here; this is the record the
build reads.**

## Measured before ruling

**The column test is a word list that refuses.** `anchor_scan._drug_column_agrees` chooses a
medicine code's column from the code label's own words: a poisoning column needs overdose,
poisoning, ingestion, got into, wrong drug/substance/route, nonprescribed or with alcohol; adverse
effect needs a proper-use phrase together with a reaction word; underdosing needs a took-less or
stopped-on-their-own phrase. A label carrying none of them agrees with no column. Driven at the
commit above:

| agreeing words | column | result |
| --- | --- | --- |
| `took too many acetaminophen tablets` | Poisoning Accidental | refused |
| `toddler swallowed grandmother's pills` | Poisoning Accidental | refused |
| `accidental ibuprofen exposure` | Poisoning Accidental | refused |
| `acetaminophen toxicity` | Poisoning Accidental | refused |
| `digoxin toxicity` | Poisoning Accidental | refused |
| `digoxin toxicity` | Adverse effect | refused |
| `rash from amoxicillin` | Adverse effect | refused |
| `ran out of insulin` | Underdosing | refused |
| `missed doses of levetiracetam` | Underdosing | refused |
| `acetaminophen overdose` | Poisoning Accidental | accepted |

If the claim were false, the honest rows above would read accepted.

**The index already names the column on some entries.** In `reference/icd10cm-2026.sqlite`, three
main terms point straight to a medicine's poisoning column on their own entry: `Overdose,
overdosage (drug)`, `Medicine poisoning` and `Wrong drug (by accident) (given in error)`, each
reading *see Table of Drugs and Chemicals, by drug, poisoning*. `Adverse effect` points to the
table's T36-T50 codes with 6th character 5. Other entries carry the pointer only on a subentry,
such as `Ingestion > drug or medicament > overdose or wrong substance given or taken`,
`Intoxication > drug > overdose or wrong substance given or taken`, `Reaction > drug NEC >
overdose or poisoning (by accident)` and `Drug > overdose`. The route check matches only a route's
first entry against the note; `AGREEMENT_READER_INSTRUCTIONS` tells the reader that every later step
is its own judgment.

**`Toxicity` points to poisoning while the guideline can make it an adverse effect.** The index
entry `Toxicity` reads *see Table of Drugs and Chemicals, by substance, poisoning*. Guideline
I.C.19.e makes a drug correctly prescribed and properly administered an adverse effect, and
digoxin toxicity in a patient on a steady prescribed dose is the ordinary case.

**An index route through `Overdose` is unread today.**
[ADR 0248](0248-the-index-tables-ship-and-an-index-path-carries-only-a-code-s-stem.md) ruling 8 fills a *by site*, *by
type* or *by substance* placeholder from the next step. `anchor_scan._reference_matches` recognizes
only those words and `animal`, so *by drug, poisoning* is read as the literal words `drug` and
`poisoning`, which the destination `Acetaminophen > Poisoning Accidental (unintentional)` does not
contain. Driven at the commit above with the label `Acetaminophen overdose`, the direct route
`Acetaminophen > Poisoning Accidental (unintentional)` is valid and the route
`Overdose, overdosage (drug) | Acetaminophen > Poisoning Accidental (unintentional)` is unread.

**A stated intent belongs only to poisoning.** Accidental, intentional self-harm, assault and
undetermined exist only as the four poisoning columns. Adverse effect and underdosing have no
intent axis.

**Only the code label is checked against the note.** The blind reader's `agreeing_words` must be
note text from the code's own label. Its `encounter_evidence` is not checked against the note.

## Ruling 1 — the code set settles the column where it can, and the reader's quoted ground decides the rest

For a medicine code in T36-T50, the check accepts the column when the code set settles it under
ruling 4 or ruling 6. Where it does not, the column rests on a **Column ground**: words the blind
reader quotes from the note showing how the drug was taken. A code whose column rests on a reader's
ground is counted on its own line of the agreement-read report, so a pass on the reader's judgment
is never reported as a clean mechanical pass.

The ground is the guideline itself: I.C.19.e chooses the column from how the drug was taken, and a
note states that in ordinary words a word list cannot enumerate. The judgment moves to the reader,
where ADR 0414 ruling 1 already put whether a substance caused harm, and the count keeps it visible.
This is the arrangement the clinician has ruled before for a checker that cannot see everything:
state what it covers.

**Declined:** the check alone deciding from code-set evidence, which leaves `took too many
acetaminophen tablets` and `toddler swallowed grandmother's pills` failing unless reworded, the
ground [ADR 0412](0412-a-matcher-a-note-pass-satisfies-by-rewording-is-retired-and-a-uspstf-citation-names-its-topic-by-copying-the-sheet-title.md)
ruling 2 declined; the reader alone deciding, which drops the mechanical pass the check can make
for `acetaminophen overdose`; counting every unsettled code as unread, which leaves each honest
plain-word overdose an incomplete run for good, as ADR 0414 declined for toxic-effect codes; and
widening the word list, declined in #1814's grilling.

## Ruling 2 — the reader's ground may be quoted from anywhere in the note

The column ground is quoted word for word from anywhere in the note: the history, the medication
list, the plan or the code label. The check refuses a ground that is not note text, and runs ruling
5's contrary tests on it. The check does not confirm that the quoted sentence is about this drug;
that is the reader's judgment, and the count under ruling 1 covers it.

**Declined:** requiring the ground to name the substance the route starts on, which fails *she
swallowed a handful of them* and every other honest sentence that names no drug, and is another
word match a correct note can miss; and confining the ground to the code label, which leaves
`acetaminophen toxicity` with *took 30 tablets* in the history unable to carry its ground without
rewriting the label.

## Ruling 3 — `toxicity` settles no column

A label or route resting only on `toxicity` settles neither poisoning nor adverse effect; its column
needs the reader's ground. `toxicity` says harm happened and not how the drug was taken, which is
the fact I.C.19.e turns on.

**Declined:** following the index to poisoning unless the quoted words say *as prescribed*, which
passes `digoxin toxicity` as a poisoning when the proper use is written only in the medication
list; and making `toxicity` an adverse effect unless misuse is quoted, which reverses the index's
own pointer and ADR 0248 ruling 6's accidental default.

## Ruling 4 — an index pointer settles the column only on the entry the check matched against the note

A medicine code's column is settled by the index when the route's first entry, the one whose main
term the check finds in the code label, itself carries the pointer to that column: `Overdose,
overdosage (drug)`, `Medicine poisoning` or `Wrong drug (by accident) (given in error)` for a
poisoning column, and `Adverse effect` for the adverse-effect column. Which poisoning column then
follows intent exactly as before, under ADR 0248 rulings 6 and 7 and
[ADR 0383](0383-a-flat-denial-of-intent-is-accidental-and-a-negation-reaches-forward-to-the-end-of-its-clause.md).
A pointer carried only on a later entry, such as `Ingestion > drug or medicament > overdose or
wrong substance given or taken`, settles nothing, and the code needs the reader's ground.

So the mechanical pass is exactly as wide as what the check has matched in the note. `Ingestion`
and `Intoxication` do not themselves say the drug was misused; in those routes the misuse lives on
a subentry only the reader judged.

ADR 0248 ruling 8's placeholder rule reaches *by drug*, which is the same instruction as *by
substance* worded for a medicine, so a route through `Overdose` is followed rather than left unread.

**Declined:** a poisoning pointer anywhere on the route, which passes `acetaminophen ingestion` in a
patient who took one prescribed dose on a subentry nobody checked; and index pointers settling
nothing, which sends `acetaminophen overdose` to the reader although the check matched `overdose`
in the note and the index sends it straight to poisoning on that entry.

## Ruling 5 — the contrary tests read only the words the code rests on

The proper-use and took-less tests read the code label and the reader's quoted ground, never the
rest of the note. Where either words carry them, a poisoning column is refused. The reader brief
tells the reader to check the medication list and history for proper use before quoting misuse.

**Declined:** reading the whole note, which refuses an honest acetaminophen overdose because the
medication list says lisinopril is taken as prescribed; and reading whole-note sentences that name
this drug, which misses proper use stated without the drug's name and refuses *takes digoxin as
prescribed but took ten extra tablets yesterday*, a poisoning, since taking more than prescribed is
an overdose.

## Ruling 6 — adverse effect and underdosing take the same treatment, and no wording refuses its own column

Each of the three medicine column families is settled mechanically by its own name in the code
label (*poisoning* or an affirmative intent under ruling 9, *adverse effect*, *underdosing*) or by
ruling 4's pointer.
The existing proper-use-with-reaction and took-less wordings keep settling their own columns when
present, and keep refusing a poisoning column under ruling 5. The existing poisoning wordings that
ruling 4 does not cover, such as *ingestion* and *got into*, no longer settle a column on their
own. Any code the code set does not settle rests on the reader's ground and is counted on ruling
1's line.

A wording that can only accept cannot fail a correct label; it can only send one to the reader.
What made the poisoning list harmful was its power to refuse, and this removes that power from all
three families at once.

**Declined:** changing poisoning only, which leaves `rash from amoxicillin`, `ran out of insulin`
and `missed doses of levetiracetam` failing their correct columns and the same decision to be
grilled again.

## Ruling 7 — no ground is a finding, not an unread code

When the code set does not settle the column and the reader quotes no ground, the code is refused as
having no column ground. A note that does not say whether the drug was misused, taken as prescribed
or taken less supports none of the columns; that is a documentation gap the clinical go-ahead can
act on.

**Declined:** counting it as unread, which would never clear because no later reader can find a
ground the note does not hold, and would file a real finding under the weaker heading.

## Ruling 8 — each code resting on a column ground is shown at the clinical go-ahead

The tracker sweep closing this grilling found that ruling 1's count reaches no one:
[ADR 0417](0417-the-clinical-go-ahead-shows-its-paired-grader-s-coverage-lines-before-the-ask-and-refuses-an-approval-that-did-not.md)
ruling 2 shows only the paired completion grader's lines at the clinical go-ahead and keeps the
coding graders out. The clinician ruled on that finding in the same session.

For each code whose column rests on a column ground, the check itself writes an entry into
[ADR 0389](0389-the-coding-readers-carry-reader-remarks-to-the-clinical-go-ahead.md)'s reader-remarks
block, naming the code and the quoted ground. The entry is written by the check, never left to the
reader's choice, so the clinician sees every such column before approving it. It changes no grade
and no exit status. ADR 0417 ruling 2 is untouched: the coding graders' own lines stay out of the
go-ahead, and this reaches it through the block ADR 0389 built for the coding readers.

**Declined:** adding the check's count line to the lines ADR 0417 shows, which partly overturns that
ruling, makes the approval step reread the agreement record, and shows only a number; and keeping the
count in the coding report alone, which lets the clinician approve a column the check never verified
with nothing at the go-ahead saying so.

## Ruling 9 — a flat denial of intent settles no column

Only an affirmative intent settles the poisoning family under ruling 6: accidental or unintentional,
intentional self-harm, assault, or undetermined. A flat denial such as *not intentional* or *denies
self-harm* settles nothing by itself. Once a poisoning is settled by ruling 4's pointer or a column
ground, the denial still chooses the Accidental column under ADR 0383 ruling 1, whose own condition
is that the words establish a poisoning.

A denial says what did not happen, not that the drug was misused, and notes record *denies suicidal
ideation* for patients who took the drug exactly as prescribed.

**Declined:** letting a denial settle poisoning, which passes *digoxin toxicity, denies self-harm*
as a poisoning mechanically when the proper use is written elsewhere.

## Coordination

ADR 0414 is unbuilt at the commit above. Its build checklist's case *a medicine route with no
poisoning word is still refused* holds under this record only for a code with no column ground;
a medicine code whose reader quotes a ground passes and is counted under ruling 1. ADR 0414 ruling
2's drug-table sentence, generated from the column test's named constants, states this record's
rules too: the code-set evidence of rulings 4 and 6, the column ground, ruling 3, and ruling 5's
instruction to check the medication list.

ADR 0414's coordination list still applies: ADR 0383's build
([#1636](https://github.com/mshamblin5150-code/clinical-skills/issues/1636)), ADR 0412 ruling 2
([#1812](https://github.com/mshamblin5150-code/clinical-skills/issues/1812)),
[ADR 0374](0374-a-code-waits-on-a-pending-test-only-for-what-its-result-would-establish-and-the-reader-may-say-why-it-does-not.md)
([#1591](https://github.com/mshamblin5150-code/clinical-skills/issues/1591)) and
[ADR 0389](0389-the-coding-readers-carry-reader-remarks-to-the-clinical-go-ahead.md)
([#1702](https://github.com/mshamblin5150-code/clinical-skills/issues/1702)) edit the same function
or brief. Whichever lands later keeps the others' words and their pinned phrases. Three of them, and
one more, meet this record at a specific point:

- **ADR 0383, #1636.** Its case table expects *ibuprofen ingestion* with a flat denial to agree with
  Accidental mechanically, because *ingestion* establishes the poisoning today. Under rulings 6 and 9
  those rows agree only on a column ground, counted, or by an `Overdose`-type route; its tests that
  drive `_drug_column_agrees(column, words)` without a route become seam tests with a route and a
  ground.
- **ADR 0389, #1702.** Its build counts an unexpected key in an agreement record as unread, so
  `column_ground` is an expected code-row key. Ruling 8's entries land in the remarks block that
  build creates.
- **ADR 0406, [#1805](https://github.com/mshamblin5150-code/clinical-skills/issues/1805).** Its item
  3 adds an out-of-scope line to the same `--agreement-read` report. Each is its own labeled line,
  and codes a scoped read leaves out stay in the unread remainder rather than on the ground line.
- **ADR 0393.** `anchor_scan` opts into the shared unread-remainder conformance, which allows exactly
  one `unread remainder N` line, so ruling 1's line does not take that shape, and ruling 7's refusal
  is a finding rather than part of the remainder.

## Build checklist

- `tools/anchor_scan.py`:
  - Add a `column_ground` evidence field to the agreement record, quoted verbatim, `none` when
    absent, and refuse a ground that is not note text.
  - For a subject code in T36-T50, settle the column from the code label's own column words and
    intent (ruling 6) and from a pointer on the route's first entry (ruling 4); `toxicity` settles
    nothing (ruling 3).
  - Where the code set does not settle the column, accept the column on the reader's ground and
    count the code on a new report line; refuse a code with no ground (ruling 7).
  - Write an entry naming the code and its quoted ground into ADR 0389's reader-remarks block for
    each such code (ruling 8).
  - Treat only an affirmative intent as settling the poisoning family; a flat denial chooses
    Accidental only once poisoning is settled (ruling 9).
  - Run the proper-use and took-less tests on the label and the ground only, refusing a poisoning
    column where they fire (ruling 5).
  - Read *by drug* as a placeholder under ADR 0248 ruling 8 (ruling 4).
  - State these rules in the reader brief, generated with ADR 0414 ruling 2's sentence.
  - Update `DECLARED_LIMITS`: whether a column ground describes this drug is the reader's.
- `tools/test_anchor_scan.py`, synthetic only, since no committed real note carries a T36-T65 code
  (ADR 0248 ruling 10). Each case goes through the public brief/read seam:
  - `Acetaminophen overdose` on the `Overdose` route agrees mechanically with Poisoning Accidental
    and is not counted on the ground line.
  - `took too many acetaminophen tablets` with no ground is refused; with that same text quoted as
    the ground, it agrees and is counted.
  - `digoxin toxicity` agrees with neither column mechanically; a ground saying the dose was taken
    as prescribed refuses Poisoning Accidental.
  - `acetaminophen ingestion` on the `Ingestion > drug or medicament > overdose ...` route needs a
    ground.
  - `rash from amoxicillin` and `ran out of insulin` agree on a ground and are counted.
  - A ground that is not note text is refused.
  - A medication-list *as prescribed* outside the label and ground does not refuse an overdose.
  - `ibuprofen ingestion, not intentional` with no ground is refused; on the `Overdose` route or
    with a ground it agrees with Accidental.
  - A code resting on a ground produces its remarks-block entry; a mechanically settled one does
    not.
- `skills/icd10-cpt/SKILL.md`: state the column ground beside the existing drug rules, worded
  differently from the brief. `skills/batch-shift/SKILL.md` carries no drug rules and points to
  that skill's descriptor-agreement section, so it gains nothing.

## What this record does not reach

- **Whether a quoted ground describes this drug.** The check confirms the ground is note text and
  free of contrary words; that it is about this medicine is the reader's judgment, counted.
- **Proper use stated outside the label and the ground.** A reader who quotes misuse and ignores a
  proper-use line elsewhere passes a poisoning; ruling 1's count is the only signal.
- **A real medicine poisoning note.** The cases are synthetic, as ADR 0248 ruling 10 declares for
  every drug rule.

## Supersedes

- [ADR 0414](0414-a-toxic-effect-code-takes-its-column-from-intent-alone-and-the-reader-brief-states-the-grader-s-own-column-words.md)
  ruling 1, the words "A medicine code in T36-T50 keeps the poisoning-word test." A medicine code's
  poisoning words no longer refuse its column: the code set settles it where it can and a counted
  column ground decides the rest. The toxic-effect ruling itself stands.
