# Normal exam lines are the clinician's own and the abdominal scheme is a setup answer

**Measured at:** f9350d209fa75142b1e0ab78a75f2ae8c0abdddd

[#1463](https://github.com/mshamblin5150-code/clinical-skills/issues/1463) was filed from the
after-action review of a `batch-shift` run and recurred on the next shift,
where the four-quadrant abdominal line reached the approved Review sheet and was caught only at
portal entry. The clinician examines the abdomen in nine regions; the shared templates write
quadrants, and a note pass copied them twice, the second time against a brief that said not to.
The ticket proposed changing one word in the shared templates. Grilled 2026-10-08 against `main`,
where the freshness gate read `FRESH`; the clinician ruled every point below in that session.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The normal-exam wording is one clinician's, written where every user inherits it.**
`skills/clinical-note/SKILL.md` titles the rule *Normal filled examinations use the clinician's
fixed language* and fixes four lines word for word: cardiovascular, respiratory, GI and neurologic.
The same four lines sit in the `skills/clinical-note/SOAP.md` and `skills/clinical-note/HP.md`
templates, and `tools/test_differential_shape.py` pins them in both templates verbatim. The GI line
reads `Bowel sounds are positive in all quadrants; ...` in all four places.

**Per-clinician values already have a home.** `skills/setup-clinical-skills/SKILL.md` writes
per-clinician material to `scratch/medatrax-profile.md`, the note skills already read that profile
for per-account rules, and where the profile and the shared reference disagree the profile wins.

**The clinician's shorthand names abdominal location in both schemes.** Counted over the shorthand
corpus at `scratch/day-file-text/` on 2026-10-08, counts only, 63 day files: the corner
abbreviations `rlq`, `llq`, `ruq` and `luq` appear 35 times, about 27 of them beside a tenderness
or pain word and none beside an imaging word; the region names `epigastric`, `umbilical`,
`hypogastric`, `flank` and `lumbar` appear 75 times; `iliac` and `hypochondriac` never appear.
`skills/clinical-note/GLOSSARY.md` expands `llq` to `left lower quadrant`. The clinician stated in
this session that a quadrant word in his shorthand is often a forgotten region name or a roundabout
description, not a deliberate quadrant. These counts are against a gitignored directory and are
stated here only, on #143's terms.

**No scanner reads a finished note's physical examination.** No module in `tools/` parses that
section; the scheme check below is new work.

## Ruling 1 — normal-exam lines are per-clinician and live in the profile

The shared templates and the `clinical-note` rule stop carrying anyone's fixed normal-exam wording
and point at the profile instead. A normal filled examination writes the clinician's saved line for
that system. A system with no saved line is written for the encounter, as an unmentioned system
other than the four is today. Changing the shared wording to nine regions was declined because the
nine-region scheme is this clinician's, and the shared files are what a second clinician inherits.
Keeping this clinician's wording as the default with an override at setup was declined because
everyone else would inherit it unless they noticed.

## Ruling 2 — setup asks for the lines and offers this clinician's as suggestions

`setup-clinical-skills` asks each clinician for their normal lines for cardiovascular,
respiratory, GI and neurologic, then asks once whether any other system is always described the same
way when normal, and saves whatever is given. The lines this clinician uses are shown as
suggestions, never applied as a default. Asking only the four was declined because a clinician with
a fixed line for another system would have nowhere to record it; walking every system was declined
because it invites fixed lines nobody actually uses.

## Ruling 3 — this clinician's saved lines

His profile carries his four current lines, with the GI line rewritten so the scheme sits on
palpation rather than auscultation:
`GI: Bowel sounds are positive; no tenderness, guarding, masses, or organomegaly noted in any of the nine regions`.
`positive in all nine regions` was declined because it claims nine auscultation sites;
`positive in all regions` was declined because it names no scheme for a pass to copy.

## Ruling 4 — a missing exam block is asked once, before any note

When the profile has no normal-exam block, the note pass stops before writing any note, asks the
clinician for the lines with this clinician's shown as suggestions, writes the answer into the
profile and continues. A batch asks before its first note pass, never mid-shift. Falling back
silently to the suggestions was declined because it applies wording nobody chose; a generic line
with a flag was declined because it puts a maintained generic exam in the shared files.

## Ruling 5 — the abdominal scheme is its own setup answer

Setup asks whether the clinician describes the abdomen in four quadrants or nine regions and saves
the answer beside the exam lines. Setup re-asks when the answer and the saved GI line disagree.
Reading the scheme off the GI wording was declined because a line naming neither scheme leaves the
check and the shorthand expansion guessing.

## Ruling 6 — quadrant shorthand is reasoned into regions for a nine-region clinician

For a nine-region clinician, a quadrant abbreviation or a roundabout description of abdominal
location is a vocabulary gap. The note pass reasons from the encounter to the nine-region name or
names, and falls back to the corner region only when nothing in the encounter distinguishes:
`ruq` to right hypochondriac, `luq` to left hypochondriac, `rlq` to right iliac, `llq` to left
iliac. A four-quadrant clinician keeps the glossary's quadrant expansions. A fixed corner mapping
alone was declined because the clinician's quadrant word is not reliably the corner; asking on every
occurrence was declined because most answers would match the pass's reasoning.

## Ruling 7 — every interpreted location is shown before the go-ahead

Each location the pass interpreted under ruling 6 is listed beside its note at the Review-sheet
go-ahead, naming the shorthand, the region written and what in the encounter decided it, for
example: shorthand `rlq` read as right iliac, from the appendicitis workup. The clinician corrects
any before approving; a correction there is a pre-approval edit, so
[ADR 0300](0300-the-entry-copy-refusals-run-before-the-go-ahead-and-a-changed-note-needs-a-new-word.md)
ruling 4's new-word rule is not engaged. Standalone `clinical-note` shows the same list before its
go-ahead.

## Ruling 8 — a mechanical check refuses quadrant wording in a nine-region clinician's exam

For a clinician whose saved scheme is nine regions, a check refuses quadrant wording in a note's
physical examination section before the Review sheet is built, and before a standalone
`clinical-note` go-ahead. It reads that section only. Imaging names such as
`right upper quadrant ultrasound` and official code descriptors such as `Right lower quadrant pain`
sit outside it and are therefore never refused, with no exemption list to maintain. Extending it to
the history and Assessment prose with pattern exemptions was declined because those lists miss
forms, and a false refusal mid-shift costs a repair; both recorded escapes were the normal GI exam
line. A history-section escape, if one is ever observed, is filed then.

## Ruling 9 — no mirror check for a four-quadrant clinician

A four-quadrant clinician's exam is not checked for nine-region wording. The middle-column names
such as `epigastric` and `suprapubic` are standard quadrant-practice phrasing, and the lateral name
`lumbar` collides with spine-exam wording. The mirror failure has never been observed; it is filed
if it is.

## Ruling 10 — the template pin moves with the wording

The test that pins the four normal lines verbatim in both templates is replaced by a check that the
templates carry no fixed normal-exam wording and point at the profile.

## What this does not reach

The check of ruling 8 establishes only that the examination section names no quadrant; it does not
establish that the region named is the one examined, which ruling 7's listing puts in front of the
clinician. Whether the approval step should also run ruling 8's check as a backstop, as ADR 0300
ruling 5 does for the Entry copy, was not put to the clinician and is not ruled here. The cost of
the second recurrence, a fix that changed approved bytes, belongs to
[#1474](https://github.com/mshamblin5150-code/clinical-skills/issues/1474) and ADR 0300, not to this
record.
