# A number in the clinician's own sentence is excused from tracing by the heading reader's list

**Measured at:** 514eb24dcbf33500cb94647040c558163c305990

[#1571](https://github.com/mshamblin5150-code/clinical-skills/issues/1571) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M11) on 2026-10-04. The DOCX grader's
`untraced-number` row requires every numeral in the body to appear in some claim heading. The
clinician's own plan figures (a ninety-day review period, a thirty-day check) are not research
claims, so the run spelled them out in words to pass the grader, against APA number style, which
wants numerals for time spans. Grilled 2026-10-12 against `main`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Five graders trace body numbers against claim headings.** `assignment_docx_scan`
(`untraced-number`), `deck_scan` (`untraced-figure`), `discussion_post_scan`,
`discussion_reply_scan`, and `peer_critique_scan`. The first two reach the shared reader
`discussion_post_scan.traceable_numeric_values`; the match is a set difference by value, so one
claim heading carrying a number clears every occurrence of that number in the artifact.

**All five already read the heading read.** Each imports `heading_read` and grades its record.
Under `skills/_shared/reference/sourcing.md`, that separate reader sorts every sentence of the
final draft into three classes: factual (paired with a claim heading), the clinician's own
reasoning and experience (counted, unpaired, and subject to the project-context verdict), and item
descriptions (tied by an `ITEM` line to an opened project-context item and compared with it). The
`SENTENCES` line carries only counts; no line records which own sentence carries which number, and
no number grader consults the classification.

**The own-work source class cannot hold a plan figure.** `clinician's own work`
([ADR 0322](0322-the-clinician-s-own-unpublished-work-is-a-source-class-a-bar-opts-into-and-is-located-by-path-and-fingerprint.md))
cites a document the clinician already wrote, located by path and fingerprint. A figure the paper
proposes for the first time has no such document.

## Ruling 1 — the separate reader lists the numbers, and the graders excuse only those

The heading reader, which already judges a sentence to be the clinician's own, also writes down
the numbers that sentence carries. A number grader excuses a number only when the heading read
lists it. Three other routes were declined. A plan-figure list written by the drafting agent
lets the writer vouch for itself, so a researched number it never sourced could be listed and
pass. A shape exemption for a number followed by a day, week, or month unit also excuses a
researched figure such as a thirty-day readmission rate, turning a partial read into a clean one.
An inline marker in the draft's source carries the same self-vouching objection and adds a marker
to strip before rendering and the word count. The accepted cost is that a plan figure reads as
untraced while drafting, until the final heading read exists; that read is already required
before every go-ahead.

## Ruling 2 — all five number graders, not the DOCX grader alone

The excuse applies in every grader that traces body numbers: `assignment_docx_scan`, `deck_scan`,
`discussion_post_scan`, `discussion_reply_scan`, and `peer_critique_scan`, with the dispatcher
`course_assignment_scan` reaching the first two. They share the defect and the reader record the
fix extends. Fixing the DOCX grader alone was declined: the reader instructions are shared, so a
listed number would mean excused in one grader and nothing in four, and a reply stating the
clinician's years of practice would keep forcing the figure into words.

## Ruling 3 — an excused number must agree with the project context, not appear in it

The number needs only what the clinician's own sentence already needs: the heading read's
project-context verdict, under which the reader checks the sentence against the opened items, and
the clinician's go-ahead. Requiring each excused number to appear in one of his files was declined.
A plan paper proposes things that do not exist yet; the thirty-day review in M11 is in no file he
opened, and a file-trail requirement would bring back the spelled-out workaround or invite an
invented trail.

## Ruling 4 — an excused number is matched by value, as a claim heading's is

A listed number clears every occurrence of that number in the artifact, the rule claim-heading
numbers already follow. Binding the excuse to the listed sentence was declined: it needs a new
locator that resolves the reader's free-text locations into Word paragraphs, slides, and post
bodies, a parser that can misread one, while the claim-heading excuse would still match by value.
The leak this leaves is a research sentence sharing a value with an own sentence; the heading
read's required pairing of every factual sentence still reports that sentence as unrecorded when
no heading states it. Whether the reader paired correctly remains the declared reading
`heading_read` already names.

## Ruling 5 — one `OWN` line per numbered own sentence, and a listed number must be in the artifact

The heading read gains a line form `OWN: <location> -> <number>[, <number> ...]`, written only for
an own sentence that carries a number. Own sentences without a number get no line, so the line
count is not bound to the own-sentence count. A grader reports a listed number that does not appear
among the artifact's traced numbers as a finding, since it is a reader slip or a list copied from
another draft. Requiring a line for every own sentence was declined as a long record whose only
gain is a mechanical miscount check; accepting a listed number unchecked was declined because a
reader writing 9 for 90 would leave 90 flagged with nothing saying why. The grader cannot confirm
that a listed sentence really is the clinician's own; that stays the reader's judgment, like the
pairing of a factual sentence.

## Ruling 6 — an item description's numbers are listed on its `ITEM` line

A sentence describing an opened project-context item, such as a period the clinician's own notes
set, may list its numbers on its existing `ITEM` line, after the reader has confirmed them against
the item, and the same must-be-in-the-artifact check applies. Sending such a figure through a full
`clinician's own work` claim record was declined: it spends a researcher and a refuter on a figure
the heading reader has already opened and compared.

## Ruling 7 — start-dated and never backfilled

A heading-read record written before the build carries no `OWN` lines and no listed `ITEM`
numbers, so it excuses nothing and its run grades exactly as it did. The new listed-number check
enters `reference/completion-check-starts.tsv` like every later check. Re-running heading reads on
unposted runs to add the lines was declined. Posted items keep the frozen grade
[ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md)
gives them; the M11 submission is recorded on #1571 and not reposted.

## Consequence for the writer

Because a correct numeral no longer fails a grader once the read lists it, the writer instructions
state that an own plan figure or item figure is written in APA numerals per
[apa7.md](../../skills/_shared/reference/apa7.md)'s number rules, never spelled out to pass the
number check.
