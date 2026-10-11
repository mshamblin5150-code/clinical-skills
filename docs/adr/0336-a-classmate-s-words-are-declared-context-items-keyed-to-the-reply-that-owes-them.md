# A classmate's words are declared context items keyed to the reply that owes them

**Measured at:** b6dc917bafa3f4f09b2628511193a867fec8b952

[#1506](https://github.com/mshamblin5150-code/clinical-skills/issues/1506) was filed from the
after-action review of a `discussion-reply` run (NUR 5144 Module 3) on 2026-10-02. The reply took
five drafts to pass its heading read. Four of the five reader findings were one defect: the draft
described the classmate's paper or plan inaccurately, dropping her qualifiers, listing only the parts
of her plan that served the argument, and once asserting an absence her paper did not state. The
fifth finding was the reader's own error: the reply correctly quoted her board reply, but the
reader had only her attached paper. Grilled 2026-10-11 against `main` at `b6dc917b`, where the
freshness gate read `FRESH`; the clinician ruled every point below in that session. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**The shared half of the defect was already ruled and built.** [ADR
0326](0326-a-claim-names-its-qualifiers-and-an-item-description-is-tied-to-the-item-it-describes.md)
made a sentence stating what an opened item says an **Item description**, a third heading-read
sentence class tied to its item by an `ITEM:` line. Its ruling 6 adopted this ticket's own test: an
omission is `narrows` only when the omitted part bears on the sentence's point, and a dropped
qualifier or an invented absence is `contradicts`. `skills/_shared/reference/sourcing.md` carries
both the drafter's claim-by-claim comparison under **Draft order** and the reader's comparison, and
`tools/heading_read.py` checks that each `ITEM:` line names an item `project-context.md` records as
opened. Ruling 4 left this ticket the `discussion-reply` items.

**The classmate's words are not opened context items, so ADR 0326 cannot reach them.** In a
`discussion-reply` run they sit in the run's `posts/<name>.md`, in her retained attachment copies,
and in the dated board snapshot. No owed place or header line makes a run open them as items. A
sentence about her plan therefore cannot carry an `ITEM:` line; as a factual sentence it has no
claim heading and reads `unrecorded`, and counted as the clinician's own it is compared with
nothing. The ticket's proposed fix, adding the board and `posts/` files to the reader's inputs,
would hand the reader her words without recording which sentences were compared.

**`peer-critique` has the same gap.** Its run keeps the same `posts/` folder and board snapshot, its
Second reader in step 4 "receives only" the critique, `claims.md`, and the printed digests, and its
classmate's case study is no owed item. A critique is mostly sentences about one classmate's work.

**The attachment appendix does not record who posted a file.** Each entry carries the course-site
id, name, size, and fingerprints, so no code can tell which attachment is the selected classmate's.

**The context record is one per run and its header is confirmed once.** `tools/project_context.py`
reads one `project-context.md` per run directory and hashes the whole header into one context
digest. A `discussion-reply` run selects both reply targets at the step 1 ranking stop, before any
research, and drafts two replies to two classmates. A `peer-critique` run has one classmate.

**A posted submission's completion still re-checks the record's shape.** `completion_gate` runs the
shape check, including the `OWN-SUBMISSION:` rule, with file rehashing off for a posted key. A new
required header line with no boundary would therefore turn every earlier run red on regrading, and
adding the line afterward changes the context digest, which the gate reports as a finding after
posting.

**The step 4 reader sentence is #1524's item 1 as well.** That ticket records that four skill
surfaces, `discussion-reply` and `peer-critique` among them, list three reader inputs where
`sourcing.md` gives four: the draft, `claims.md`, the digests, and every item pointer recorded in
`project-context.md`. A reader briefed from the skill's own "only" list never opens the items. #1524
is held in `grilling` on an unrelated decision about a heading read with no second context.

## Ruling 1 — the selected classmate's words are opened context items

A sentence in a `discussion-reply` reply stating what the selected classmate wrote, found, or
planned is an **Item description** under ADR 0326. Her `posts/` file, every retained copy of a file
she attached, and the board snapshot holding her replies are opened items in the run's
`project-context.md`, so the drafter's comparison, the reader's `ITEM:` line, and the
`heading_read.py` check all apply unchanged.

Handing the reader the board and `posts/` files while counting sentences about her as the
clinician's own, the ticket's proposed diff, was declined: no record would show which sentences were
compared, which is the bare-`agrees` pass ADR 0326 ruling 5 declined. Letting an `ITEM:` line name a
run file `project-context.md` does not record was declined because one record line would then
accept two populations and `heading_read.py` would have to learn one skill's folder layout.

## Ruling 2 — confirmed header lines declare each source

The project-context header gains three lines, confirmed with the rest of the header:

```text
CLASSMATE-POST: <submission key> -> <absolute path to her posts/ file>
CLASSMATE-BOARD: <submission key> -> <absolute path to the board snapshot>
CLASSMATE-ATTACHMENT: <submission key> -> <absolute path to a retained attachment copy> | <submission key> -> none - <reason>
```

`CLASSMATE-ATTACHMENT:` repeats once per file she attached, or appears once with `none` and a reason.
`tools/project_context.py` refuses, for the submission being gated, a missing or duplicated post or
board line, a missing attachment line, a `none` without a reason, a `none` beside a path, and any
named path the record does not show opened as an item of a read place. The lines are part of the
confirmed header the context digest covers. A one-row-per-skill table in the gate names the skills
that owe them.

Telling the run to open her files as ordinary items with no header line was declined on ADR 0332
ruling 1's ground: a skipped step looks the same as a run with nothing to read. Having the gate work
out the owed files from the reply's filename was declined because it would hard-code
`discussion-reply`'s folder layout and first-name collision rule into the shared gate, and would add
an author field to the shared attachment appendix in all five skills for one skill's benefit.
Requiring the lines in all five coursework skills, with `none` where no classmate exists, was
declined because three skills would confirm a meaningless line on every run.

## Ruling 3 — the same lines bind `peer-critique`

The gate's table has two rows, `discussion-reply` and `peer-critique`. A `peer-critique` run declares
the critiqued classmate's post, attachments, and board snapshot under its submission key,
`critique.md`.

Filing `peer-critique` as a separate ticket was declined because two builds would edit the same gate
table and the same reader sentence, which is the overlap this ticket already carried with #1524.
Leaving it out was declined because the skill whose artifact is mostly descriptions of a classmate's
work would stay the one where those descriptions are never tied to her words. ADR 0326 ruling 4
declined widening this ticket from one skill to five over the shared rule; this ruling widens one
gate table by one row.

## Ruling 4 — the drafter's check is `sourcing.md`'s Draft order rule, by pointer

Step 3 of both skills points at `sourcing.md`'s **Draft order** section, which already requires the
drafter to compare each Item description with its opened item claim by claim while drafting. The
ticket's proposed step 3 paragraph, a pre-draft list of every sentence the reply will spend on the
classmate, is not added.

A private pre-draft list file was declined because nothing would grade it and a skipped list looks
the same as a short one. Copying the paragraph into both skills was declined because it restates a
rule `sourcing.md` already holds, and a prose edit to any copy fails nothing. Rulings 1 and 2 put the
recorded defect behind a gate and a blocking reader; what remains is rework, not a wrong post.

## Ruling 5 — this build makes #1524's item-pointer edit in its own two skills

The step 4 Second-reader sentence in `skills/discussion-reply/SKILL.md` and
`skills/peer-critique/SKILL.md` is edited to include every item pointer recorded in
`project-context.md`, matching `sourcing.md`. The board and `posts/` files are not added to that
sentence by name; they reach the reader as items. A comment on #1524 records that these two skills
are done. #1524 keeps item 1 for `discussion-post` and `course-assignment`, and its open decision.

Blocking this ticket on #1524 was declined because the edit it needs involves no decision, while
#1524 waits on an unrelated one. Taking #1524 item 1 in all four skills was declined because two of
them are untouched by this design.

## Ruling 6 — each classmate line is keyed to the submission that owes it

Every classmate line opens with the submission key it binds, for example
`CLASSMATE-POST: response-maren.md -> <path>`. A `discussion-reply` run writes both replies' lines
and confirms them before reply one's first prose, since both targets are signed at the step 1
ranking stop; the two board lines name the same snapshot. The gate, run for a submission, requires
that key's lines. An `ITEM:` line in a submission's heading read may name only files its own key's
classmate lines declare, or any other opened item the existing rule admits; naming another key's
classmate file is a finding.

Unkeyed lines shared by both replies were declined because one classmate's missing line would hide
behind the other's, and a sentence about one classmate tied to another's post would pass the gate.
Keying by the classmate's roster name was declined because the gate would need the reply-filename to
roster-name translation ruling 2 kept out of it.

## Ruling 7 — records confirmed before the build are not graded on these lines

A context record whose `CONFIRMED:` date is on or after the build day owes the classmate lines. An
earlier record prints the classmate row as `not graded` with the count of such records, never as a
clean result. This follows ADR 0326 ruling 3's cutoff for the same kind of change.

No cutoff, matching `OWN-SUBMISSION:`, was declined because every historical posted run would turn
red on regrading with no repair, since adding the lines changes the digest the go-ahead recorded. A
cutoff at posting was declined because it departs from ADR 0326's date rule and leaves a later
posted run guarded only by its go-ahead result rather than also by its completion re-check.

## Build checklist

- `tools/project_context.py`: parse the three keyed lines; refuse per ruling 2 for the gated
  submission; the one-row-per-skill table naming `discussion-reply` and `peer-critique`; include the
  lines in the context digest and the rendered header; the `CONFIRMED:` cutoff and the `not graded`
  row with its count; and a `DECLARED_LIMITS` row stating that the gate checks the declared files
  were opened, never that they are the right classmate's.
- `tools/heading_read.py`: an `ITEM:` naming a classmate file declared under another submission key
  is a finding, on ADR 0326's cutoff.
- `skills/_shared/reference/sourcing.md`: the three lines in the header template and their rules,
  stated once.
- `skills/discussion-reply/SKILL.md`: step 3 tells the run to write both replies' classmate lines
  before reply one and points at **Draft order**; step 4's Second-reader sentence includes the item
  pointers.
- `skills/peer-critique/SKILL.md`: the same two edits for its one classmate and `critique.md` key.
- A comment on #1524 recording that ruling 5 discharges item 1 in these two skills.
- Tests that drive, through the public commands, a missing post line, a missing board line, an
  attachment `none` without a reason, a declared path not opened, another key's line standing in for
  the gated key's, a record confirmed before the cutoff, and an `ITEM:` naming the other reply's
  classmate file, with a committed fixture record as the positive control.

## What this record does not reach

- **Whether the declared files are the selected classmate's.** The clinician confirms the header;
  the gate checks only that each named file was opened.
- **Whether a description is accurate.** The drafter's and reader's comparisons remain readings
  under ADR 0326, recorded and graded for completeness only.
- **A sentence about a classmate the run did not select.** Only the selected classmate's words are
  owed items; a reply that discusses a third classmate's post has no declared item for it.
- **`discussion-post` and `course-assignment`'s reader sentences.** They stay with #1524.
