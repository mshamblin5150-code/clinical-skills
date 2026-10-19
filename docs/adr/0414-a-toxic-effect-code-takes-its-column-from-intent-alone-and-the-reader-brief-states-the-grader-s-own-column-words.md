# A toxic effect code takes its column from intent alone and the reader brief states the grader's own column words

**Measured at:** 5c27cfd9e13965fc4926ce9b53c877f530e4be1c

[#1814](https://github.com/mshamblin5150-code/clinical-skills/issues/1814) was filed from the
after-action review of a `batch-shift` run (NUR5144 clinic shift). A blind
descriptor-agreement reader cited a Table of Drugs and Chemicals route for a venom code, its own
self-check passed, and `tools/anchor_scan.py --agreement-read` refused the route. On retry the
reader fell back to `descriptor words`. Grilled 2026-10-18 against `main` at `31b048a1`, where
the freshness gate read `FRESH`. The commit above adds only a draft of this record and its glossary
entry to that base. The clinician ruled every point below in that session, one question
at a time. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

`anchor_scan._drug_column_agrees` accepts any of the four Poisoning columns only when the agreeing
words carry one of its poisoning words: overdose, poisoning, ingestion, got into, wrong
drug/substance/route, nonprescribed, or with alcohol. Driven at the commit above with the column
`Poisoning Accidental (unintentional)`:

| agreeing words | result |
| --- | --- |
| `Toxic effect of venom of hornets, accidental (unintentional), initial encounter` | refused |
| `hornet sting` | refused |
| `toxic effect of carbon monoxide from motor vehicle exhaust` | refused |
| `poisoning by bee venom` | accepted |

`Toxic effect of venom of hornets, intentional self-harm` is refused on the self-harm column as
well. If the claim were false, the first three rows would read accepted.

The committed Table of Drugs and Chemicals has two kinds of substance. A medicine routes to
T36-T50, whose descriptors open `Poisoning by`. Every other substance routes to T51-T65, whose
descriptors open `Toxic effect of` and never contain the word poisoning. Counted in
`reference/icd10cm-2026.sqlite`: 1,544 index paths end at each of the four Poisoning columns with a
T51-T65 code, and none ends at Adverse effect or Underdosing. So every toxic-effect route the Table
offers was refused unless the note was reworded to say poisoning.

`AGREEMENT_READER_INSTRUCTIONS` says only to distinguish poisoning, proper-use adverse effect and
underdosing. It states none of the words the grader tests, so a reader's correct self-check against
its brief cannot predict a refusal.

The index's `Sting (venomous) (with allergic or anaphylactic shock)` entry reads *see Table of Drugs
and Chemicals, by animal or substance, poisoning*, so a route from `hornet sting` reaches
`Venom, venomous (bite) (sting) > hornet > Poisoning Accidental (unintentional)` and starts on a word
the note carries.

## Ruling 1 — a toxic effect code takes its column from intent alone

For a subject code in T51-T65, the substance the route starts on is the exposure, and the poisoning
word is not required. The column is then chosen by intent exactly as for a medicine:
[ADR 0248](0248-the-index-tables-ship-and-an-index-path-carries-only-a-code-s-stem.md) ruling 6's
accidental default where no intent is stated, its self-harm and assault words, ruling 7's hedged
intent agreeing only with undetermined, and
[ADR 0383](0383-a-flat-denial-of-intent-is-accidental-and-a-negation-reaches-forward-to-the-end-of-its-clause.md)'s
flat denial agreeing with accidental. A medicine code in T36-T50 keeps the poisoning-word test.

The ground is the classification: CMS files these substances under codes that say toxic effect, and
the Table gives them no adverse-effect or underdosing column, so there is no second meaning for the
poisoning word to separate. The route start still checks mechanically that the note names the
substance. Whether the note describes harm from it stays the reader's judgment, as every later step
of a route already is.

This extends ADR 0248 ruling 6 and overturns none of it. That ruling's definitions separate
poisoning, adverse effect and underdosing, which are the three columns a medicine has. It says
nothing about a substance whose only columns are the four intents, and every medicine route keeps
its definitions word for word.

A closed list of toxic-effect words, such as toxic reaction, sting, bite, envenomation or exposure,
was declined: a correct label outside it, such as carbon monoxide from exhaust, still fails, which
is the rewording [ADR 0412](0412-a-matcher-a-note-pass-satisfies-by-rewording-is-retired-and-a-uspstf-citation-names-its-topic-by-copying-the-sheet-title.md)
ruling 2 declined for B12. Leaving the grader unchanged and only telling readers the word list was
declined on the same ground. Declaring toxic-effect routes an unread limit was declined because every
run carrying one would be incompletely scanned permanently.

*Superseded 2026-10-19.* The words "A medicine code in T36-T50 keeps the poisoning-word test." are superseded by [ADR 0430](0430-a-medicine-code-s-drug-column-is-settled-by-the-code-set-where-it-can-and-otherwise-by-a-counted-reader-quoted-ground.md) ruling 6. A medicine code's poisoning words no longer refuse its column: the code set settles it where it can, and a counted column ground quoted by the reader decides the rest. The toxic-effect ruling, its intent tests and its declined alternatives stand.

## Ruling 2 — the reader brief states each column's exact condition from the grader's own words

`AGREEMENT_READER_INSTRUCTIONS` states the condition for each Table of Drugs and Chemicals column:
the poisoning words a medicine poisoning column needs, the proper-use and reaction words an adverse
effect needs, the underdosing words, the intent words, and ruling 1. The word lists in the brief are
generated from the same named constants `_drug_column_agrees` reads, so an edit to the grader moves
the brief with it.

A reader only quotes the note, so stating a list cannot place a word in it; the list lets the reader
predict the verdict its self-check is meant to model. Typing the conditions into the brief by hand was
declined as two copies of one rule with nothing binding them, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape. Stating principles
without the lists was declined because it leaves the reader unable to model the refusal for
medicine, adverse-effect and underdosing routes.

## Ruling 3 — the medicine poisoning word gap is a separate ticket

Honest medicine labels also fail the poisoning-word test: `took too many acetaminophen tablets`,
`toddler swallowed grandmother's pills` and `accidental ibuprofen exposure` are refused on the
Accidental column. Ruling 1 does not carry over, because a medicine does have an adverse-effect
column and `digoxin toxicity` after proper use is an adverse effect under guideline I.C.19.e.
Dropping the word test for medicines would pass that wrong code silently, and widening the list here
was declined as another hand-grown list.
[#1889](https://github.com/mshamblin5150-code/clinical-skills/issues/1889) carries that decision.

## Coordination

ADR 0383's build ([#1636](https://github.com/mshamblin5150-code/clinical-skills/issues/1636)),
ADR 0412 ruling 2 ([#1812](https://github.com/mshamblin5150-code/clinical-skills/issues/1812)) and
[ADR 0374](0374-a-code-waits-on-a-pending-test-only-for-what-its-result-would-establish-and-the-reader-may-say-why-it-does-not.md)
([#1591](https://github.com/mshamblin5150-code/clinical-skills/issues/1591)) and
[ADR 0389](0389-the-coding-readers-carry-reader-remarks-to-the-clinical-go-ahead.md)
([#1702](https://github.com/mshamblin5150-code/clinical-skills/issues/1702)) all edit
`_drug_column_agrees` or `AGREEMENT_READER_INSTRUCTIONS`, and none is built at the commit above.
Whichever lands later keeps the others' words and their pinned phrases in
`test_reader_rules_have_one_source_and_all_new_rules_in_first_brief`. Ruling 2's generated sentence
carries ADR 0383's flat-denial rule once that build lands, and ADR 0383's negation cues stay a
closed list of their own. That test also refuses any sentence of the brief appearing verbatim in
`skills/icd10-cpt/SKILL.md` or `skills/batch-shift/SKILL.md`, so the skill's statement of ruling 1
is worded differently from the brief's.

## Build checklist

- `tools/anchor_scan.py`:
  - Move the poisoning, adverse-effect, underdosing and intent patterns in `_drug_column_agrees`
    into named module constants that the check reads.
  - For a subject code in T51-T65, treat the poisoning precondition as met; the intent tests and
    their order are unchanged.
  - Generate the drug-table sentence of `AGREEMENT_READER_INSTRUCTIONS` from those constants, and
    state ruling 1 in it.
  - Update `DECLARED_LIMITS` if a row's wording names the poisoning word for toxic-effect codes.
- `tools/test_anchor_scan.py`, synthetic only, since no committed real note carries a T36-T65 code
  (ADR 0248 ruling 10). Each case goes through the public brief/read seam:
  - `hornet sting` on the `Sting (venomous)` to `Venom, venomous > hornet` chain agrees with the
    Accidental column.
  - A self-harm toxic-effect label agrees only with the self-harm column, and a hedged one only with
    Undetermined.
  - A medicine route with no poisoning word is still refused, so ruling 1 does not reach T36-T50.
  - The brief's text contains every word in the grader's constants, and a mutated constant changes
    the brief.
- `skills/icd10-cpt/SKILL.md`: state ruling 1 beside the existing drug rules.

## What this record does not reach

- **Whether the note describes harm from the substance.** A label naming a venom with no sign of a
  reaction still reaches the toxic-effect code mechanically; that judgment stays the reader's.
- **Medicine routes.** Ruling 3 sends them to #1889 unchanged.
- **A real toxic-effect note.** The cases are synthetic, as ADR 0248 ruling 10 declares for every
  drug rule.
