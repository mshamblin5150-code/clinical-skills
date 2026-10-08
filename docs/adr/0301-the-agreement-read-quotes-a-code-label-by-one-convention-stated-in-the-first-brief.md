# The agreement read quotes a code label by one convention stated in the first brief

**Measured at:** 5245d5a7f3630a75218a2c1eac219811a75b096c

[#1459](https://github.com/mshamblin5150-code/clinical-skills/issues/1459) was filed from the
after-action review of a `batch-shift` run. The blind descriptor-agreement read's first round
graded 85 of 210 codes "agreeing words from the wrong place" although every span was verbatim note
text, and three later shifts recorded the same loop at a larger scale. Grilled 2026-10-08 against
`main`, where the freshness gate read `FRESH` after a rebase onto `5245d5a7`; the clinician ruled
every point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The finding is ADR 0243 ruling 10's comparison.** `_grade_agreement` in `tools/anchor_scan.py`
requires the reader's `agreeing_words` to occur inside the worksheet row's `ANCHOR`, and reports
"agreeing words are from the wrong place" when they are note text outside it. ADR 0258 ruling 5
states what that comparison proves: an author's anchor is independently findable from the note and
the descriptor.

**Almost every wrong-place finding was a reader quoting a different line that also agreed.** The
ticket's four recorded shifts each cleared most of the round with a retry brief stating where
worksheets quote: 85 to 5, 203 to 21, 79 to 10, and 130 to 12. The residue was same-line misses,
where the author's anchor was narrower than the reader's span, plus one entry anchor quoting a
history line rather than the Final diagnosis line.

**Two of the ticket's options do not reach the different-line failures.** Option 1, anchoring
whole lines by default, is the minimum anchor width ADR 0258 ruling 6 declined. Option 3, accepting
reader words anywhere on the anchor's physical line, reaches only same-line misses, and a physical
line can carry more than one code: `fixtures/slot-form-run/day-a-case-06.md` writes
`Obesity, class 3 - E66.813 with Body mass index [BMI] 40.0-44.9, adult - Z68.41` on one line.

**The committed controls were written under ADR 0243 ruling 7.** Counted over the five
`fixtures/descriptor-agreement-*` sets by a throwaway script that printed counts only:

| set | entry anchors on the diagnosis line naming their code | entry anchors elsewhere | differential and refusal rows with no anchor |
| --- | ---: | ---: | ---: |
| authored-anchor control | 1 | 0 | 0, and its one refusal anchor sits outside the welded clause |
| index-table control | 2 | 1 | 0 |
| negative control | 0 | 11 | 8 |
| note-path control | 3, none quoting the whole label | 2 | 8 |
| positive control | 3 | 6 | 11 |

**The brief still omits rules the skill states for its reader.** ADR 0282 ruling 2 left this gap to
#1459. `_brief_payload` carries no rule for the `refused` role, carries the hedge rule only for
self-harm and assault intent, says nothing about filled tier-block values, and does not say that a
disclosed estimated measurement is not a pending result. #1447's build, merged in `21f4d007` just
before this record, replaced the brief's history sentence with a pointer to "the coexisting-condition
test in icd10-cpt's descriptor-agreement section" and made `open_status_evidence` verbatim note text.
The reader never receives that skill section, so the pointer is one more rule the reader cannot see.

## Ruling 1 — one quoting convention binds author and reader, and the first brief states it

An entry code's agreement is quoted from the Final diagnosis or Preexisting diagnoses line that
names it. A differential code's is quoted from its numbered Differential entry. A refused code's is
quoted from the code-and-descriptor half of its welded `NOT CODED:` clause, never its reason. A CPT
or HCPCS code's is quoted from the line documenting the act done in this encounter. The blind brief
states this convention from the first round, identically for every run, so it discloses nothing
drawn from any worksheet. This narrows ADR 0243 ruling 7 for authors.

A per-code location hint derived from each anchor was declined: it is ADR 0258 ruling 4's deferred
echo, the 2026-10-06 shift's hint carried a character offset and length that with the note spell the
anchor, and authors quoting anywhere would still need a hint per code. Dropping the requirement that
the reader's words fall inside the anchor was declined because it leaves the author's quotation
graded by nobody independent, which is #1139's defect. Accepting the extra rounds was declined on
four measured shifts.

## Ruling 2 — a convention break is an author finding before the brief goes out

For entry, differential and refused codes the grader refuses an anchor that does not sit in the
place ruling 1 names, under a finding worded as the author's, and the check runs at the gate ADR 0296
puts before the blind brief. The procedure placement is declared a reading in
`anchor_scan.DECLARED_LIMITS`, because "the line documenting today's act" has no mechanical form.

Skill prose alone was declined because a break would cost a reader round and print as the reader's
error. Requiring procedure anchors in the Plan or Procedure section was declined because a Plan line
ordering a later procedure would pass it, which is what ADR 0243 ruling 4 refuses.

## Ruling 3 — a reader records `none` when the convention's line does not agree

Where the line ruling 1 names holds no words stating or reaching the descriptor, the reader records
`agreeing_words` as `none`, even when other note text agrees. The grader then reports "no agreeing
words", which points at the label. How a note writer words a label so that it reaches its code
belongs to [#1475](https://github.com/mshamblin5150-code/clinical-skills/issues/1475).

Quoting the agreeing words from elsewhere was declined because it prints the same "wrong place"
finding a reader's own slip prints and sends the repair to the anchor. Quoting the label anyway was
declined because it prints a route finding for a wording defect and has the reader submit words it
knows do not agree.

## Ruling 4 — for entry, differential and refused codes the anchor is the whole code label

The anchor runs from the line's start, or the end of the preceding code on that line, to the
hyphen that pins its code, keeping any hedge and any joining word, and excluding a differential
rationale after the colon. A refused code's anchor is the whole code-and-descriptor half of the
welded clause. Ruling 2's check enforces it, so an anchor quoting part of a label is an author
finding. This narrows ADR 0258 ruling 6 for these three roles; the bound is a unit in the document
rather than a chosen width, and there is nothing left to widen.

Accepting the reader's words anywhere on the anchor's physical line was declined for the multi-code
line above, where one code's agreement would stand on another's label. Keeping the retry and
widen-to-sentence loop with a committed widening helper was declined for these roles because a
round per shift would remain.

## Ruling 5 — procedures keep the widening loop, with no helper yet

CPT and HCPCS codes keep ADR 0258 ruling 6's loop. The author's pass edits that one anchor by hand
as `skills/icd10-cpt/SKILL.md` already states, and the after-action review counts procedure
widenings per shift. A committed helper is built when a recorded shift shows the step recurring.

Building the helper now was declined because its frequency after ruling 4 is unmeasured. Folding
procedures into a whole-line convention was declined for ruling 2's reason.

## Ruling 6 — the brief is the only copy of the reader's rules

The reader's rules are one named module constant in `tools/anchor_scan.py`, and the brief's
instructions are that constant. It gains ruling 1's convention and ruling 3's `none` instruction,
the refused-role rule from ADR 0243 ruling 5, the general hedge rule from ADR 0243 ruling 9's first
sentence, that codes may rest on the tier block's filled values, that a disclosed estimated
measurement is not a pending result for `waits_on_result`, and the coexisting-condition test in
place of the pointer #1447's build wrote. `skills/icd10-cpt/SKILL.md` stops restating the reader's
rules and names the constant; its author-side instructions stay. A test asserts the skill names the
constant and repeats none of its sentences.

Keeping both copies under a phrase-for-phrase test was declined as the arrangement
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) ruled insufficient.
Building the brief from the skill's Markdown at run time was declined because the grader would
depend on a section's boundaries and author prose would leak into a blind reader's input.

## Ruling 7 — the committed controls become pre-convention records, and a new control is generated

The five `fixtures/descriptor-agreement-*` sets keep their files, and their tests expect the
convention findings, which makes them real-material negative cases for ruling 2's check. A fresh
blind generating pass under the amended skill writes a new note-path control, a fresh blind reader
grades it with the first-round brief, and its record states the first-round wrong-place count. That
follows ADR 0243 ruling 19's pattern.

Rewriting the existing anchors was declined because it falsifies preserved run records whose
generation records describe what was written. Exempting them by a declared list was declined because
the convention would then have no real material showing it can be followed or that it ends the
extra rounds.

## Supersedes

- [ADR 0243](0243-descriptor-agreement-is-read-blind-against-the-note-and-the-index.md) ruling 7,
  its sentence that a quotation passes wherever it sits in the note, and its decline of a location
  table. Ruling 1 narrows it for authors: an anchor sits in the place the convention names. That the
  reader names the exact agreeing words stands, and so does the decline of a minimum-span rule
  outside the unit ruling 4 defines.
- [ADR 0258](0258-descriptor-agreement-grades-an-authored-anchor-on-every-role.md) ruling 4,
  its deferral of the echo proposal. Ruling 1 declines a per-code hint drawn from an anchor and
  states a convention instead; the split finding and the rule that no figure derived from the
  support is echoed stand.
- [ADR 0258](0258-descriptor-agreement-grades-an-authored-anchor-on-every-role.md) ruling 6,
  its retry and widen-to-sentence loop for entry, differential and refused codes. Ruling 4 replaces
  it with the whole code label for those roles; procedures keep the loop under ruling 5.

## Consequences recorded as derived rather than ruled

- **`CONTEXT.md` gains Code label.**
- **#1475 gains a comment** saying ruling 1 makes the label the place where agreement must show, so a
  lay label the index does not reach fails on the first round as "no agreeing words".
- **#1447's history wording stands as its build ruled it**; ruling 6 moves that rule into the brief's
  constant rather than changing it.

## What this does not reach

- Whether the label is the right label for the encounter, which stays a reading.
- Where a procedure anchor sits, which ruling 2 declares a reading.
- Independence of the reader, which ADR 0243 and **Blind read** already declare.
