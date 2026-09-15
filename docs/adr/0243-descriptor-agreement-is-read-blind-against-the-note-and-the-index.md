# Descriptor agreement is read blind against the note and the index

[#1139](https://github.com/mshamblin5150-code/clinical-skills/issues/1139) was filed from #1104's
mandatory after-action review. An independent reader found a generated coding worksheet pairing an
official code with nearby prose that did not document the diagnosis the descriptor names, and every
string grader stayed clean because every field had the right shape. That review record did not
survive its worktree. The worksheet #1104 kept did:
`fixtures/worksheet-grammar-positive-control/case-01.md`, accepted by a separate non-authoring pass,
carries every shape #1139 describes.

Grilled 2026-09-15. **Twenty rulings, by the clinician, on that date.** Nothing is built here; this is
the record the build reads.

**Measured at:** fc7c6e3b7947a23e7bd407ec5b2fb37357754681

## Measured before ruling

**The kept worksheet carries the shapes #1139 names.** `F17.210 Nicotine dependence, cigarettes,
uncomplicated` quotes use prose, *current daily smoker*. `R79.89 Other specified abnormal findings of
blood chemistry` quotes *history of elevated troponin*. `Z68.26` quotes a screening-list header that
restates the BMI. The differential's `Z13.1 Encounter for screening for diabetes mellitus` rests on a
screening recommended for a later visit. `CPT 10060` rests on a procedure written in the Plan for the
same visit.

**The official alphabetic index is on the maintainer's machine and not in the repository.** The CMS
FY2026 April release zip carries `icd10cm_index_2026.xml`: 8,122 main terms and 73,393 subterms,
9,691,020 bytes uncompressed. `reference/icd10cm-2026.sqlite` holds the tabular alone, as
`tools/icd10_build.py` states. In that index `Smoker` reads *see Dependence, drug, nicotine*,
`Elevated, elevation > troponin` reaches `R79.89`, and `Elevated, elevation > blood pressure >
reading (incidental) (isolated) (nonspecific), no diagnosis of hypertension` reaches `R03.0`. The
`History > personal (of)` subtree carries no abnormal-troponin entry.

**The skills already model a disease code on a considered entry.** `skills/clinical-note/SOAP.md`
writes `2. Acute bronchitis - J20.9: cough is productive, but the focal crackles argue for
consolidation. Less likely.` with no refusal, so a differential code documents what was considered.

**Every run grader reads each Markdown file in a run directory as a worksheet.** `run_grader`'s reader
takes every `*.md` except `README`, so a note stored beside its worksheet would be read as one. The
committed fixtures already keep them apart: `fixtures/filled-anchor/run-2/case-NN.md` beside
`fixtures/filled-anchor/notes/case-NN.md`.

**The note skills changed while this was grilled.** Drift row 34 of `skills/clinical-note/SKILL.md`
now follows every note with a separated `Proposed coding worksheet` of terse `E/M:`, `CPT:` and
`HCPCS:` lines. `icd10-cpt` runs privately and the rendered lines carry no quotation, specificity,
confidence or provenance. The H&P gained a numbered Medical Decision Making section, one item per
differential entry. `skills/icd10-cpt/SKILL.md` did not change.

## Ruling 1 — agreement is the descriptor's words or the official index path

A quotation agrees with a code when its words state what the code's official descriptor names, or
reach that code through the ICD-10-CM alphabetic index. Topical relation is not agreement.
Descriptor words alone were declined because they refuse `F17.210` on *smoker*, which the official
index assigns. Reader judgment with no named authority was declined because it is the arrangement
that accepted every shape above.

## Ruling 2 — the alphabetic index ships in the committed database

`tools/icd10_build.py` loads the index into `reference/icd10cm-2026.sqlite` and
`tools/icd10_lookup.py` gains an index mode that prints the path a term reaches. The neoplasm table,
the drug table and the external-cause index stay out. Reading the zip on the maintainer's machine was
declined because a consumer clone has no zip and would fall back to descriptor words; recalling the
index was declined as ruling 1's rejected option again.

## Ruling 3 — a differential code agrees with the diagnosis its entry considers

The note need not establish it. #149's limit still applies inside the differential: a descriptor naming
what only an absent or pending result would establish is refused. Grading differential codes against
what the note establishes was declined because it collapses a differential into repeated symptom codes
and reverses `SOAP.md`'s bronchitis entry; exempting the differential was declined because it leaves
`Z13.1` standing on a considered infection.

## Ruling 4 — an encounter or procedure descriptor agrees only with this encounter

A descriptor naming an encounter's purpose or a performed act agrees only with text documenting that
purpose or act in the encounter being coded. Plan text about today counts, as step 2 already takes
procedures from the Plan. A recommendation, order or referral for a later visit documents nothing
codable and takes no code and no refusal record. `10060` agrees and keeps its `needs:` for the missing
procedure note; `Z13.1` does not. Refusing a future encounter under `NOT CODED` was declined because
that block is for suspected diagnoses and its `proposed instead` has nothing to name. A status mark on
the code line was declined as a sixth field the worksheet grammar does not carry.

## Ruling 5 — a refusal record's two codes take the checks their claims carry

The refused code agrees with the diagnosis the record's first line considers, under ruling 3. The
`proposed instead` code takes the full entry check and must appear as a proposed code above.
Exempting refusal records was declined because a `proposed instead` naming an unanchored code would
stand; requiring agreement without presence was declined because the supported code would then be
reachable only inside a refusal.

## Ruling 6 — a history agrees with a present descriptor only while it stays open

Text calling a finding a history agrees with a descriptor naming it as present only when the note
documents that finding as still open in the encounter: unresolved and addressed. `R79.89` agrees
because today's Plan works up the troponin. A closed history agrees only with a personal-history code
the index reaches, or with nothing. Refusing every history against a present descriptor was declined
because an actively worked-up problem would leave the worksheet; ignoring the modifier was declined
because *history of myocardial infarction* would agree with an acute infarction code.

## Ruling 7 — where the quotation sits does not matter, and the reader names the words

Any verbatim quotation containing agreeing words passes wherever it sits in the note, and the reader
records exactly which words agree. `Z68.26` and `R12` pass. A location table was declined because
which section is the record is itself a reading; a minimum-span rule was declined as a shape rule
#1139 leaves unchanged.

## Ruling 8 — a bare value agrees with an abnormality only through a stated threshold

A value agrees with a descriptor calling it abnormal only through a threshold a committed source
states, such as a `reference/thresholds/` row, or the note itself states. Without one the code is
recorded unread. `R03.0` agrees through `bp-stage-1-range-sbp`. A `Z68` band needs no threshold: its
descriptor is the range. Requiring the word *elevated* was declined for failing correct codes on
wording; clinical recall was declined as ruling 1's rejected option.

## Ruling 9 — the agreement reader applies the hedge limit to entry codes

The reader treats hedge words as documenting the diagnosis and records, for every entry code, whether
the descriptor waits on a result and which. An entry code that waits on one is a finding against that
line. `M79.5 Residual foreign body in soft tissue`, *suspected, to be confirmed at drainage*, is such a
line. Keeping the limit a generation-time instruction was declined because it has never had an
independent check; a third reader was declined as a second reading of the same descriptor against the
same note.

## Ruling 10 — the reader never sees the worksheet's quotations

The agreement reader receives the note with its tier block and, for each code, the number and official
descriptor: entry, differential, refused and `proposed instead` codes. For each it records the
agreeing words verbatim, the route (descriptor words or an index path), the encounter or open-status
evidence where rulings 4 and 6 apply, the threshold where ruling 8 applies, the result the descriptor
waits on where ruling 9 applies, or `none`. A mechanical comparison then requires the named words to
occur verbatim in the note and inside the worksheet line's quotation. Adjudication beside the
quotation was declined because a reader that starts from the generating pass's framing is how the
topical shapes passed.

## Ruling 11 — the agreement reader and the specificity Second reader are separate

Each receives its own brief and writes its own record. The specificity reader keeps its codes-only
brief. One combined reader was declined because the note would shape the specificity reader's account
of a code's axes; one agent reading in order was declined because nothing in a record can show the
order was kept, while an omitted input can be checked in the brief itself.

## Ruling 12 — CPT and HCPCS codes agree by descriptor words, and the rest is unread

The procedure database carries no index. A procedure code agrees by its descriptor's words and ruling
4's encounter test; a code those cannot settle is recorded unread and enters the shared unread
remainder, exit 2. Reading the licensed book's index through an authenticated browser on every run was
declined as a browser dependency for every consumer; excluding procedure codes was declined because a
planned act written as a performed one would stand.

## Ruling 13 — `anchor_scan` writes the brief and grades the record

`tools/anchor_scan.py` gains an agreement-brief mode and an agreement-read mode. Completion requires
both commands, as `practicum-case-study` requires both `render_scan` and `checks_ledger`, and the
after-action row stays on `specificity_scan --submission`. Hosting both reads in `specificity_scan`
was declined for grading quotations under a name about specificity; a new module was declined for a
second worksheet parse with the same completion arrangement.

## Ruling 14 — notes pair with worksheets by filename in a separate directory

Both modes take a notes directory; a worksheet pairs with the note of the same filename stem. Worksheets
and notes are counted independently and an unpaired member of either enters the unread remainder.
Storing the note beside its worksheet was declined because every run grader would read it as a
worksheet; explicit pairs on the command line were declined as the pairing moved into whatever builds
the arguments.

## Ruling 15 — a note run keeps its private worksheet as a file

`clinical-note` saves the full anchored worksheet its private `icd10-cpt` pass produces in a
worksheets subdirectory of its run, apart from the notes, and never renders it; drift row 34 stands.
Its completion runs the agreement read over that subdirectory and `batch-shift` inherits it per note.
Leaving the note path to a separate ticket was declined because it is where the codes are submitted and
carries #1139's own defect. Reading the note's code lines with no worksheet was declined because it
loses the inside-the-quotation comparison and needs a second rule and a second grader.

## Ruling 16 — a note skill's call is the request for an E/M level

`icd10-cpt` step 5 keeps *only if asked* for a direct run and says a note skill's worksheet asks; the
level is rendered as a proposed code the clinician verifies. This coincides with
[ADR 0223](0223-a-shift-is-entered-into-medatrax-after-one-go-ahead-and-confirmed-by-one-posted-reading.md)
rulings 11 and 12, whose build on #1205 already carries the step-5 edit, so #1139's build does not
repeat it. Rendering elements instead of a level was declined for reversing row 34's terse line.

## Ruling 17 — E/M lines are excluded from agreement, declared and counted

An E/M descriptor names a place of service, a patient status and a decision-making level that its words
cannot settle. E/M lines leave the agreement brief, `anchor_scan.DECLARED_LIMITS` states why, and every
report prints the excluded count. Grading the level from the rendered CPT book was declined because every
note carries an E/M line and a run without the book would exit 2 permanently; grading place and status
alone was declined because the note often cannot say new or established.

## Ruling 18 — the note's codes and the rendered lines are bound to the saved worksheet

In both directions: the note's preexisting and final diagnosis codes equal the saved worksheet's
for-entry ICD-10 codes; its differential codes equal the `NOT FOR ENTRY` codes; every welded `NOT
CODED:` code equals a refusal record; and the rendered `CPT:` and `HCPCS:` lines equal the worksheet's
procedure codes. The `E/M:` line is outside the bind under ruling 17. A code present on one side alone
is a finding. One direction was declined because a checked refusal could silently leave the note; no
bind was declined because the saved worksheet could then differ from what is submitted.

## Ruling 19 — the worksheet control runs both directions on `case-01`

A fresh agreement reader receives `fixtures/filled-anchor/notes/case-01.md` and the code list of the
kept #1104 worksheet, told nothing about which rows are suspect, and must fail the rows these rulings
fail and pass the rest. A blind generating pass writes a new `case-01` worksheet under the amended skill
from a neutral input copy, and a separate fresh reader grades it; a finding there is a finding about the
skill edits under
[ADR 0186](0186-the-skill-as-written-settles-a-worksheet-line-and-run-2-is-a-divergent-run.md) ruling 13.
Both records and the new worksheet are committed, and the #1104 fixture's README describes its worksheet
as a divergent run. A synthetic trap note was declined as an input written knowing the rules; a
positive-only control was declined because a rubber-stamp reader passes it.

**The grilling pass predicted which kept rows fail**: `M79.5` as an entry code and again as a
differential code, and `Z13.1`. That is a prediction the negative reader re-derives without being told,
not a measured result.

## Ruling 20 — the note path has its own control with planted binding faults

A blind `clinical-note` pass over `fixtures/day-b/shorthand/case-01.md` under the amended skills saves
its note and private worksheet; a fresh agreement reader grades it and ruling 18's bind runs. The run is
committed beside ruling 19's pair. The bind's negative side is planted in tests by mutating one line of
that committed run each: a final code absent from the worksheet, a refusal dropped from the note, a
rendered procedure nobody proposed. Synthetic tests alone were declined because saving, pairing and
binding would first meet a real note on a live shift; a full twelve-case shift was declined because
only row 34 differs between a batch and a single note.

## Consequences recorded as derived rather than ruled

- **`CONTEXT.md` gains Descriptor agreement**, carrying rulings 1, 3, 4, 6 and 8 as domain language.
- **The worksheet grammar and its declared limits are unchanged**, as #1139 requires; *every
  differential entry carries a code* and `NOT FOR ENTRY` stand.
- **`fixtures/filled-anchor/run-2` is not re-graded here.** Its README already records it as a
  divergent run, and the agreement modes are opt-in.
- **#1205's build and this one both edit the three note-path skills' completion steps.** Neither
  blocks the other; whichever lands second rebases onto the first.
- **#1217's Second-reader population gains this reader**, whose brief is a deliberate blinding
  whitelist.

## What this does not reach

- **Whether a proposed code is the right code.** Agreement grades that the quotation documents the
  descriptor, never that no better code exists.
- **An index route for procedure codes**, which ruling 12 records as unread.
- **The E/M level**, which ruling 17 excludes.
- **Independence of the reader.** The brief omits the quotations; whether the reader recalls a prior
  worksheet is declared, as **Blind read** already declares it.
- **A threshold no committed source or note states**, which ruling 8 records as unread.
