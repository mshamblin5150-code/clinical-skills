# An item line quotes the one place in the item its sentence rests on and the reader writes it

**Measured at:** f56bf83a5c09f6d1b74ac5c734f090fbdd040e0c

[#1795](https://github.com/mshamblin5150-code/clinical-skills/issues/1795) was filed from the
after-action review of a `peer-critique` run (NUR 5144 Module 3) on 2026-10-12. It reported that the
final-draft heading read found **Item description** defects one class per round. It offered three
options: an author-written list of item lines before the first read, a heading read run per heading
as each is drafted, or no change. Grilled 2026-10-17 against `main` at `4014ae1d`, where the
freshness gate read `FRESH`; the merge to the commit above changed none of the measured files. The
clinician ruled every point below in that session, one question at a time. **Nothing is built
here; this is the record the build reads.**

## Measured before ruling

The run keeps all nine of its heading-read records, eight beside the superseded draft each graded
and the ninth beside the final draft. Every record's `DRAFT` digest matches the bytes of the draft
beside it, and every record says `ROUTE: separate context`. The figures below are counts over those
records and drafts. No sentence from them is reproduced here.

**The ticket's own count is wrong.** It says seven rounds and one defect class per round. Six of
the nine reads returned a defect. The first returned six item-description findings, across both
`contradicts` and `narrows`, and the fourth returned two. Every factual sentence paired cleanly in
every round (11 per read), so every finding was about an item description.

**Most later findings were sentences an earlier reader had already passed.** After the first read,
six findings remain. Four were on sentences already present, unchanged, in a draft an earlier read
had graded, and two of those earlier reads were fully clean. One finding was on a sentence written
in a redraft. One was mixed: the sentence was new, but its substance was already present and had
been passed by two earlier reads.

**Two readers gave opposite verdicts on identical input.** The third and fourth reads graded drafts
whose Diagnostic Interpretation section is byte-identical across drafts one to four, under the same
context digest. The third returned `CONTEXT-VERDICT: agrees` and `VERDICT: clean`; the fourth
returned `contradicts` naming sentences in that section. This is
[#1494](https://github.com/mshamblin5150-code/clinical-skills/issues/1494)'s shape, which
[ADR 0326](0326-a-claim-names-its-qualifiers-and-an-item-description-is-tied-to-the-item-it-describes.md)
answered for claim pairs, recurring on item lines.

**Readers already list every item description.** In all nine records the `ITEM` line count equals
the record's item count, from 62 to 68 per read. The ticket's first option promised that the reader
would grade the author's lines "rather than rediscovering them", but the readers were not failing to
find the sentences. They listed each one and judged some wrongly.

**No drafting-time comparison left a trace.** No artifact written before the first read lists the
draft's item descriptions with locations. [#1485](https://github.com/mshamblin5150-code/clinical-skills/issues/1485)'s
2026-10-10 ruling put the drafting-time comparison in `sourcing.md` as a written rule that nothing
grades, and that comment refused a graded early check by a fresh reader.

**The items are files.** The run's `project-context.md` opens twelve items: seven Markdown, two
Word and two plain-text files, plus one `none`. It opens no service item. Each opened file is
recorded with its path and SHA-256.

**Service text is not kept.**
[ADR 0272](0272-project-context-is-retrieved-into-a-confirmed-record-before-drafting.md) records a
service's opened items "by identifier only — never their text, which would copy personal records
into the run directory for no reader that needs them."

## Ruling 1 — the fix is on the reader, not the drafter

The defect is a reader passing an item description it listed, so the change binds the heading
reader's `ITEM` line rather than adding a drafting step. The ticket's first option was declined
because it adds an author-written artifact and grader that checks the author against himself.
That is the self-walk [ADR 0341](0341-the-heading-read-has-no-self-walk-and-one-course-assignment-brief-covers-both-artifacts.md)
refused, and one recorded defect was written by the author in a redraft built from the clinician's
own correction. It also leaves the readers' misses, most of the record, untouched. The second
option was declined because it multiplies reads per round to target redraft-introduced defects,
one finding of six. Leaving the mechanism unchanged was declined because each missed sentence costs
a full heading read, voice read and approval preparation. A separate item-description reader per
item was declined for now: it adds fresh contexts every round in five skills while adding no
requirement to show the support. It remains available if this ruling does not suffice.

## Ruling 2 — each item line quotes where in the item its sentence rests

Every `ITEM` line carries an exact quote from the named item that the sentence rests on, for
example `ITEM: <location> -> <opened item identifier> | rests on "<quote>"`. A sentence asserting
that the item lacks something, or that only something holds, writes `absent - whole item searched`
in the quote's place. Three of the recorded defects were an asserted absence or an exclusivity: a
reader that must point at the support cannot point at nothing.

`heading_read.py` opens the item at the path `project-context.md` records, after its SHA-256 still
matches the recorded value, and confirms the quote appears in the item's text, ignoring case and
runs of whitespace. A Word item is read through the repository's Word reader. An item whose text
cannot be read is unread remainder under
[ADR 0230](0230-a-measured-partial-read-prints-an-admissible-unread-remainder-that-exits-not-scanned-and-is-declared-only-where-no-candidate-count-is-admissible.md), never a
pass.

A location name such as a heading or paragraph number was declined because code can check nothing
about it beyond its presence, and a careless reader can write one label for every line. Writing
both a location and a quote was declined because the location half adds nothing a grader checks.
The quote proves the reader found real text in the item. It does not prove that text supports the
sentence; that limit is declared.

## Ruling 3 — the quote appears exactly once in its item

A quote that occurs more than once in the item's normalized text is a finding. A quote that
occurs once points at one place, which is what naming where a sentence rests means, and it
refuses a one-word fragment that occurs everywhere. A short unique anchor, such as a drug order in
a table cell, still passes. A minimum word count was declined because a true anchor can be shorter,
and a long but common phrase from the wrong section would still pass. No rule was declined because
any word would then satisfy Ruling 2. The cost is that word-for-word repeated passages cannot be
quoted; such a line is refused visibly rather than passed.

## Ruling 4 — a quote from a service item is counted, not graded

An `ITEM` line naming a service item cannot be checked, because ADR 0272 keeps no service text.
Such lines are counted on their own report line, a declared limit, and do not change the exit
status. Keeping the supplied service text privately so the quote could be checked was declined: it
reverses ADR 0272's ruling that personal records are not copied into run directories, and no
recorded defect has involved a service item. Leaving them as unread remainder was declined because
any run describing a service item could then never grade clean.

## Ruling 5 — the drafting-time rule stays as written

The `sourcing.md` instruction to compare each item description with its item claim by claim while
drafting, and #1485's statement that nothing grades the drafting-time check, stay unchanged. The
rule costs nothing and points the drafter the right way; the graded protection is Ruling 2's.
Removing the drafting duty for item descriptions was declined because it would split #1485's one
rule. Grading it by having the author write quotes too was declined as the ticket's first option
returned.

## Ruling 6 — the new rows start at each item's approval time

The new rows enter `reference/completion-check-starts.tsv` compared with each item's approval, the
table's standing rule for a new check. An item approved earlier reports them as `not graded`. A
fresh heading read precedes every approval, so a run in progress at the build carries the quotes at
no extra cost.

## Build checklist

- `skills/_shared/reference/sourcing.md`: the heading-read paragraph and the record template's
  `ITEM` form carry the quote, the `absent - whole item searched` form, and the once-only rule.
- `tools/heading_read.py`: parse the quote suffix beside the existing `figures` suffix; resolve the
  named item through `project-context.md`'s recorded path and SHA-256; rows for a missing quote, a
  quote absent from the item, a quote occurring more than once, and an unreadable item as unread
  remainder; a counted line for service-item quotes; `DECLARED_LIMITS` rows for
  quote-not-support, an unverifiable `absent` claim, and service items.
- `reference/completion-check-starts.tsv`: the new rows for each grader that calls `heading_read`,
  compared with approval.
- The heading-read briefs in `discussion-post`, `discussion-reply`, `peer-critique`,
  `course-assignment` and `practicum-case-study` name the quote where they describe the return.
- Tests drive, through the public commands, a clean quoted line, a quote absent from the item, a
  twice-occurring quote, an `absent` line, a moved item, an unreadable item and a service item,
  with a committed real item file as the positive control.

## What this record does not reach

- **Whether a quote supports its sentence.** The grader proves the quote is real and unique, not
  that the reader judged the comparison correctly. Round three's dropped qualifier could still pass
  with a true quote.
- **Whether an `absent` claim is true.** Nothing can show a whole-item search took place.
- **Markup inside an item.** A quote copied from rendered text may not match an item whose source
  carries emphasis markers; the build decides how the item's text is normalized.
- **Description of a service item.** Ruling 4 keeps it ungraded until a recorded defect gives
  reason to revisit ADR 0272.
