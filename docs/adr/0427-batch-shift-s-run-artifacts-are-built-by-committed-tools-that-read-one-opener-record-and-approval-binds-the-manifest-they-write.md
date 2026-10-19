# Batch-shift's run artifacts are built by committed tools that read one opener record and approval binds the manifest they write

**Measured at:** e20a591e4d3ff669d4da6db2c44650c90665e0c9

[#1882](https://github.com/mshamblin5150-code/clinical-skills/issues/1882) was filed from the
grilling of #1808, whose [ADR 0408](0408-the-go-ahead-uptodate-block-and-the-medatrax-posted-reading-are-written-by-committed-tools-and-checked-before-they-are-relied-on.md)
ruling 6 left three per-run scripts to it: the identity-map helper, the Review-sheet and freshness
manifest builder, and the Medatrax fill builders. Each shift's coordinator copies them from the
previous run and edits them. On a later shift the copied identity-map helper missed a name
written on the note-number line, a shape the run's own split had already reported, and was patched
in the middle of portal entry. Grilled 2026-10-19 against `main` at the commit above, where the
freshness gate read `FRESH`. The clinician ruled every point below in that session, one question at
a time. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The scripts are copied widely and import almost nothing committed.** Across the 17 `shift-<date>`
runs in the owning checkout's `scratch/runs/`, the identity-map helper appears in 9, a Review-sheet
or manifest builder in 16 (the same `build_review.py` in 14), and a fill builder in 4, with a
separate per-patient script generator in 3. Only `build_review.py` imports a committed module
(`specificity_scan`). No identity-map helper or fill builder imports one. Counted 2026-10-19; these
are per-run files under `scratch/`, so nothing committed re-derives the figures.

**The identity-map helper guesses the name two different ways, and neither is the repo's.** Four
copies read only the line after the note number; five scan the next three lines for two words.
Neither uses `name_index.looks_like_a_name`, which `phi_scan` shares, and neither can see a name on
the note-number line. The helper inserts a row under *Newly entered patients* with a hard-coded run
date. Every copy checks for a duplicate Patient Reference, and none checks for a name that already
has a row.

**The split into encounters is done by hand and nothing records what it saw.** No committed tool
splits a day file. Agent-written `encounters/encounter-N` files exist in 16 of the 17 runs, at a path
no skill or tool names. The step 4 line listing openers missing age or sex goes to chat only. Nothing
checks that the encounter files account for the whole day file.

**The freshness gate trusts a fingerprint it does not compute.** `tools/coding_freshness.py` reads
`batch-codes.json`, whose per-encounter `normalized_sha256` covers the note plus its visible
worksheet, and its declared limits say the caller supplies that digest. Today the caller is a copied
script. The skill says the Review sheet exists only after every encounter passes freshness. Nothing
enforces that order.

**Approval binds the raw note bytes, not what the skill and glossary say it binds.** Both
`skills/batch-shift/SKILL.md` step 7 and the glossary's **Review sheet** entry say approval covers
normalized clinical and coding content, status evidence, batch order and the freshness receipts, and
that a layout-only re-render does not invalidate it. The step 7 call passes
`sources=medatrax_posting.note_paths(run, batch=True)`, and `approval_record.source_sha256` hashes
those `note-N.md` files' raw bytes. The worksheets under `worksheets/` and the manifest are not
sources. A final code changed after approval therefore leaves the approval standing, while a
trailing-space edit to a note invalidates it.

**No committed tool produces any per-encounter Medatrax field.** `entry_copy.py` and
`form_sections.py` cover the four note-form boxes, which `reference/medatrax-fields.md` has a page
script fill. Every other field, from demographics, visit date and times to the picklists, vitals and
patient time, comes from an agent-written field block in each note. The procedure describes no
scripted route for them, yet the copied fill builders generate per-patient page scripts.

**`clinical-note` repeats each of these steps for one pasted encounter.** It resolves the patient
against the identity map under the same every-row rule, adds a new Patient Reference to the map,
writes its own `batch-codes.json` for the same gate, records status from the same three sources,
writes the same field block, and is approved through the same `approval_record.approve`. It has no
day file split and no Review sheet.

## Ruling 1: the split keeps one opener record, and every builder reads patient details from it

The **Opener record** keeps, per encounter, the name, age and sex as that encounter's opening lines
write them. The identity-map writer, the manifest, and the fill builder read those details from it by
note number and never parse the shorthand themselves. A name read from the shorthand must appear in
that encounter's own text. A detail the opener omits is recorded as omitted rather than inferred.
Having the identity-map writer take the name as an argument was declined because the name would be
typed again in the middle of portal entry, where the last one went wrong, and age and sex would still
be read by three routes. Having the writer find the name itself was declined because it keeps the
guess.

## Ruling 2: the command splits on `Note N`, writes the encounter files, and records what the agent supplies

A committed command reads the day file's extracted text, splits it on `Note N` through the pattern
`corpus_census` and `name_index` already share, writes each encounter's file at a path the skill
names, and records the name, age and sex the agent supplies. It accounts for every part of the day
file in exactly one encounter. Broken or absent numbering exits 2. The agent then passes its own cut
with a stated reason, and the record marks those encounters as cut by hand. Recording over a hand
split was declined because nothing would show a dropped or merged encounter. Having the command
extract name, age and sex was declined as the guess ruling 1 removed.

## Ruling 3: the identity-map writer adds one row and leaves every other line unchanged

The writer takes a note number and the Patient Reference Medatrax just created. It reads the name
from the opener record, takes the date from the run's service date, records the source as the day file
and note number, and adds one row under *Newly entered patients*. Every other line of the map is left
byte for byte. It refuses a reference that is not 15 hexadecimal characters, and one already anywhere
in the map.

## Ruling 4: a name that already has a row is refused unless each existing row is ruled a different person

When the opener's name matches one or more existing rows, the writer refuses unless the agent names
each existing row's Patient Reference as a different person with a reason. The writer then records
that ruling under *Collisions* beside the new row. Writing with a warning was declined because the
duplicate would already exist in Medatrax. Refusing outright was declined because a same-name new
patient is sometimes correct and the row would return to hand editing.

## Ruling 5: a missing name is asked at step 4, and an unnamed reference is kept under Cannot be matched

Step 4's stop reports an opener with no name beside the openers missing age or sex. The clinician's
answer is recorded in the opener record as his answer and is exempt from the in-text check, which
still covers every name read from the shorthand. When no name comes back, the identity-map writer
files the reference under *Cannot be matched* with that encounter's age and sex. Filing it there
without asking was declined because a patient he could name would become a reference nobody can find.
Refusing was declined as the per-run hand edit this ticket ends.

## Ruling 6: one module computes the fingerprints, the freshness gate runs visibly, and rendering refuses a stale pass

One committed module reads the notes and worksheets once. Its first step computes each encounter's
normalized fingerprint and writes the manifest. The freshness gate then runs as its own command with
its output shown. The module's second step renders the Review sheet and refuses unless the passing
freshness receipt on record matches the current manifest's fingerprints. One command that runs the
gate inside itself was declined because the gate's blocking messages and live CDC and CMS reads
would be buried in a renderer's output. Two independent commands were declined because the sheet
could show content the gate never fingerprinted.

## Ruling 7: each office encounter's status is recorded by a committed command

When an office encounter's new-or-established status is settled, a committed command records the
value, which of the identity map, the portal, or the clinician's answer settles it, and a pointer to
that one row, reading or answer. The command fingerprints the evidence itself. The manifest builder
reads these records and refuses an office encounter without one. An emergency department encounter
stays `not-applicable`. Deriving status from the identity map's practice-status rows was declined
because choosing between same-name rows is the judgment the skill refuses to automate. Parsing the
agent's free-form `status-note-N.txt` was declined as the hand-built file this ticket retires.

## Ruling 8: approval binds the manifest and its passing freshness receipt

For `batch-shift`, the go-ahead binds the manifest and its passing freshness receipt in place of the
raw note bytes, and refuses when either is missing or out of step with the notes and worksheets. The
entry-copy checks on each note stay. This makes the code match what step 7 and the glossary already
say approval covers, so no ruling or definition moves. Filing the gap separately was declined because
the builders would land while approval still ignored code changes. Rewriting the documents to the
raw-byte rule was declined because it would make a code change after approval go unnoticed by rule.

## Ruling 9: the manifest also carries each encounter's field-block fingerprint, and approval binds it

The manifest carries a fingerprint of each encounter's Medatrax field block, separate from the code
fingerprint the freshness gate reads. Approval binds it with the rest of the manifest, and an edit to
a field block after the go-ahead needs the clinician's word again, as a note edit does. Leaving the
block unbound was declined because ruling 8 removes the incidental protection the raw-byte hash gave
it, and a plausible post-approval change would reach the portal. Folding the block into the code
fingerprint was declined because it contradicts the normalization step 7 defines and ties the gate's
evidence to values it does not grade.

## Ruling 10: the fill builder reads the field block and checks every value against its own source

The fill builder's one input is the note's field block. It checks age and sex against the opener
record; start and end times against the shift window through
[ADR 0410](0410-visit-times-are-checked-by-one-shared-module-both-note-graders-call-on-every-run-and-an-ed-shift-takes-no-exception.md)'s
shared module and in `HHMM` form; picklist values against their exact strings, which for Preceptor
and Site are the account profile's lists and for every other picklist are `reference/medatrax-fields.md`'s; and
every free-text field through
[ADR 0421](0421-the-builders-refuse-a-control-character-in-an-outbound-artifact-rather-than-carry-or-delete-it.md)'s
shared control-character check. It refuses any disagreement, and refuses a block whose fingerprint
differs from the one approval bound under ruling 9. Computing every value from its source was declined
because it creates a second value set that can differ from the block the clinician saw and the
readback compares against. Reformatting without checks was declined as the copied script's behavior.

## Ruling 11: the fill builder writes the checked list, and the page script is generated from it

The builder writes the checked, ordered field list as the record, then generates a page script that
types the per-encounter fields from that list, never written separately. `reference/medatrax-fields.md`
documents the scripted route beside the existing note-form script. The readback of Patient Detail
against the approved field block is unchanged. A page script alone was declined because the checked
list is what ruling 9 fingerprints and the readback compares against. A list typed by hand was
declined because it keeps the typing slip the readback only catches afterward.

## Ruling 12: the Review sheet renders through `docx_write.py`, extended with a page break and a plain layout

`docx_write.py` gains an explicit page-break line and a plain, non-APA layout its caller selects. The
Review-sheet step renders through it, keeping its overwrite guard, main-checkout guard and ADR 0421
check. The new layout is measured through the maintainer Word calibration. A second Word writer was
declined because it would have to rebuild all three protections. The unchanged APA layout was declined
because it breaks step 7's page-per-encounter and bolding rules.

## Ruling 13: every piece serves `clinical-note` too wherever the step exists there

The opener record gains a one-encounter mode that records the pasted encounter without splitting. The
identity-map writer, the status command, the manifest step, the approval binding of manifest and
field-block fingerprint, and the fill builder all serve `clinical-note`. The Review-sheet render stays
`batch-shift` only. Batch-shift only was declined because the single-note route would keep the same
hand steps and approval would bind different things in the two skills. A follow-up ticket was declined
for the same gap.

## Ruling 14: three builds in dependency order, each waiting on the shared modules it needs

1. **The split and opener record, plus the identity-map writer.** If
   [ADR 0422](0422-an-unreadable-tool-written-run-record-is-never-read-as-empty-and-a-damaged-freeze-record-is-left-untouched.md)'s
   shared run-record reader is still unbuilt, this build builds it to that record's specification.
2. **After #1811's build:** the status command, the manifest-and-render module, and the approval
   binding. The manifest step's freshness command carries no `--cpt-receipt`.
3. **After ADR 0410's times module and ADR 0421's check exist:** the fill builder.

One build for everything was declined because it overlaps four other tickets' builds in `tools/` and
step 7. Local stand-ins for missing shared modules were declined because ADR 0422 forbids a second
read route.

## Build checklist

- Build 1: the split-and-opener command, with a one-encounter mode, a hand-cut route that records its
  reason, and the in-text name check that exempts a clinician's answer. Step 4 reports a missing name.
  The identity-map writer covers rulings 3 to 5 and writes the map atomically under the artifact lock.
  The ADR 0422 shared reader is built if absent.
- Build 2: the status command; the manifest-and-render module with its freshness-receipt refusal and
  field-block fingerprints; the `docx_write.py` page-break line and plain layout, with a Word
  calibration row; `approval_record.approve` for both skills binding the manifest and receipt. Today
  the `sources` argument also sets which files get the entry-copy check, where the reply window
  starts, and `source_modified_at`. The build keeps the entry-copy check on the note files, starts the
  window from the latest of the notes, worksheets, manifest and receipt, and does not run the
  entry-copy grammar on the JSON records. Anything else keyed on the same tuple, such as a
  `reader_remarks` receipt digest, is computed over the same bound set.
- Build 3: the fill builder, its checked list, and its generated page script; ADR 0421's check is
  called on every free-text field.
- `skills/batch-shift/SKILL.md` steps 4 to 7 and `skills/clinical-note/SKILL.md` name each command
  where its step runs. `reference/medatrax-fields.md` documents the scripted route.
- `CLAUDE.md` maintainer tooling names each new command and points to its limits object.
- Tests through each public command:
  - a name on the note-number line is recorded;
  - a supplied name absent from the encounter text is refused;
  - broken numbering exits 2;
  - a dropped encounter is caught by the split's coverage count;
  - a same-name row without a ruling is refused, and with one writes *Collisions*;
  - a reference already in the map is refused;
  - an office encounter with no status record is refused;
  - a render whose receipt does not match the manifest is refused;
  - a code change after approval is refused at approval while a layout-only re-render is not;
  - a field block edited after approval is refused by the fill builder;
  - an out-of-window or non-`HHMM` time is refused, as is a picklist value outside its exact strings;
  - a control character in a free-text field is refused;
  - a clean shift and a clean single note pass.

## What this record does not reach

- **Whether the agent's cut is clinically right where it cuts by hand.** The record marks the hand cut
  and its reason; it does not judge the boundary.
- **Whether a recorded name, age or sex is the right reading of the opener.** The record checks that a
  name appears in the encounter's text, not that it is the patient's name rather than another word.
- **Whether two same-name patients are really different people.** Ruling 4 makes someone state it; it
  does not verify it.
- **Whether a field value is clinically right when it agrees with its source.** The checks catch a
  disagreement, not a source that is itself wrong.
- **Whether the page script typed what the portal saved.** The existing readback of Patient Detail
  owns that.
