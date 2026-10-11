# Every Canvas save waits at the loaded box for a recorded go-ahead and plain text is built by one command

**Measured at:** 85a56763aa5b22cd2419de5c3da24f90aa3408e9

[#1502](https://github.com/mshamblin5150-code/clinical-skills/issues/1502) was filed from the
after-action review of a `peer-critique` run (NUR 5144 Module 2) on 2026-10-01. That run saved the
critique to a classmate's Peer-review comment in the same step that loaded it, on the strength of the
content go-ahead, and the saved comment carried literal `**Heading**` markers and asterisks around
the italic reference titles. The comment cannot be edited or deleted. The clinician named both
defects: he expects to look at the loaded box before every Canvas save, and he does not write
Markdown markers. [#1603](https://github.com/mshamblin5150-code/clinical-skills/issues/1603) records
the same missing stop on a `discussion-reply` run on 2026-10-08. Grilled 2026-10-11 against `main`,
where the freshness gate read `FRESH`. `main` then advanced to `85a56763` with the #1497, #1498, and
#1496 builds and the #1501 ruling, and every quotation below was re-derived against it before
publication. The clinician ruled
every point below in that session and widened it to cover #1603. The tracker sweep closing the
session then found a fifth Canvas posting skill the session had not counted, `practicum-case-study`,
and the clinician ruled the same day that rulings 1 and 2 reach it. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**Five skills post to Canvas, and only some of them stop at the loaded box.** A `grep` of `skills/`
for `canvas-editor.md` lists five: `course-assignment`, `discussion-post`, `discussion-reply`,
`peer-critique`, and `practicum-case-study`; the grilling questions counted four and missed the last.
`skills/discussion-post/SKILL.md` step 8 shows the loaded, unsubmitted box and submits only on its
Gate 2, which it records through a second `approval_record.approve` call on the same item.
`skills/course-assignment/references/docx.md` keeps two gates for the DOCX branch, while
`skills/course-assignment/SKILL.md`'s deck branch says "wait for the explicit go-ahead once" and
writes no stop before its Submit click. `peer-critique` step 6 treats the content go-ahead as
authority to load and save, `discussion-reply` step 4 says the clinician's existing go-ahead "is the
single posting gate", and `practicum-case-study` says "The existing go-ahead authorizes the full-body
submit click."

**The shared Canvas sheet is scoped to Composers today.** `canvas-editor.md` opens by saying it
governs how authored bytes "must enter a Canvas rich content **Composer**". `peer-critique` step 6 says
its Composer load routes "do not apply" to the Peer-review comment, and the `file-upload` branches of
`course-assignment` and `practicum-case-study` do not read it.

**ADR 0204 never said to keep the markers.** Its ruling 2 says the text loaded into the Peer-review
comment is "plain text built from the critique's Markdown source", never the Composer HTML. The
instruction to "retain the bold heading markers … exactly as the source carries them" entered
`peer-critique` step 6 with the #991 build, not with the ruling.

**ADR 0190's "single gate" describes the gate count it found, not a ruling on it.** Its ruling 3
selects a Reply's load route and says that route is "declared to the clinician at the single gate
that already exists".

**Once the plain text stops being a copy, nothing binds it to what was approved.** The approval record
and the posted reading both fingerprint `critique.md`. The posted reading compares Canvas's stored
comment with `critique.txt`. `tools/peer_critique_scan.py` never names `critique.txt`, so a
`critique.txt` that differs from `critique.md` by anything other than the defined stripping would be
posted and graded clean. `discussion-post` closes the same gap for its HTML because
`tools/post_html.py` builds it from the Markdown through `docx_write.blocks` and the shared inline
splitter, and the grader rebuilds it and requires it byte for byte.

**The recorder already holds a second reply on one item, and nothing requires one.**
`approval_record.approve` appends each call's reply to the item's history and checks it against the
clinician's own messages, after the reply before it. Ruling 4 of ADR 0318 exempts an approval of an
unchanged fingerprint from its shown-text check. `approval_record.completion_gate` requires a content
approval, a posting route, and a matching posted reading; it does not count approvals. Since the #1496
build, `approve` also reruns `project_context.go_ahead` on every call for the coursework skills, and
each skill's go-ahead step says to show any changed notice and renew approval when it differs from
the one the clinician saw.

## Ruling 1 — one stop at the loaded box governs every Canvas save

Every save, submit, or reply click on Canvas is preceded by the same stop: the run loads the
contribution, reads it back, leaves it loaded and unsubmitted, and clicks only on the clinician's
word given after he has looked at it. The content go-ahead never covers the click. The rule is
written once in `skills/_shared/reference/canvas-editor.md`, whose opening scope widens from
Composers to every Canvas save so that the plain Peer-review comment and a file-upload submit are
inside it. `peer-critique`, `discussion-reply`, and `practicum-case-study` point at it from each step
that posts, including `practicum-case-study`'s full-body Composer submit and its attachment
fallback, where the stop shows the staged attachment's body, filename, and size. This ruling settles
#1603 as well as #1502. #1555, which concerns the editor mode a Reply is submitted from,
stays its own ticket.

Fixing `peer-critique` alone was declined because the same slip had already happened on a second
skill, and grilling #1603 separately would rule one habit of the clinician's twice with room for two
wordings.

## Ruling 2 — the posting go-ahead is recorded and checked

The clinician's word at the loaded box is a **Posting go-ahead**. In `peer-critique`,
`discussion-reply`, and `practicum-case-study` it is recorded before the click with a second `approval_record.approve` call on
the same item, carrying his whole reply, exactly as `discussion-post` records its Gate 2. The recorder
therefore verifies that the reply is his own message and that it follows the content go-ahead. On
unchanged text the shown-text check is exempt by ADR 0318 ruling 4; if he asks for a change after
seeing the box, the changed text is a new fingerprint and its next approval is a first approval,
shown in full.

The completion grade refuses an item posted by the run whose approval history holds no posting
go-ahead after its content go-ahead. This applies to `discussion-post`, `discussion-reply`,
`peer-critique`, and `practicum-case-study`. `discussion-post` already writes both replies, so for
it the row enforces what it does. Because `approve` today records no kind for a reply and resets the
item's posting route on every call, the build marks each history entry as a content or a posting
go-ahead rather than inferring the kind from order, and the posting go-ahead is recorded before the
posting route is. An item posted by the clinician himself owes no posting go-ahead, because the stop exists for
the run's own click. Items whose content approval was recorded before the build lands are graded as
before, so a correctly finished historical run does not turn into a finding.

Leaving the stop as a written rule was declined because a written stop is the instruction that
failed in both filed runs, each time by an agent reading the content go-ahead as covering the click.

## Ruling 3 — the stop shows the clinician's own browser and a status line

At the stop the run names the Chrome tab where the box is loaded, says the box is loaded and
unsubmitted, and reports the readback verdict: a match, or the exact difference. The clinician looks
at the box in his own signed-in browser. A screenshot is taken only when he asks for one, for example
when he is answering away from that computer. Because recording the posting go-ahead reruns the
project-context check, a changed notice it reports is shown at the stop and the approval is renewed
under ADR 0328's rule, before the click.

A screenshot in the conversation on every post was declined as a step that adds little to a
character-for-character readback. Retained captures with a separate vision reader and a graded
record, `discussion-post`'s arrangement, were declined for these two surfaces: that machinery exists
because a Composer renders formatting a text comparison cannot see. The Peer-review comment renders
none, and the Reply's editor-mode problem belongs to #1555.

## Ruling 4 — one command builds the plain text, and the grader rebuilds it

A committed builder command is the only route by which text reaches a plain Canvas box. It builds
`critique.txt` from `critique.md` through `docx_write.blocks` and the shared inline splitter, the
reader `tools/post_html.py` uses. `tools/peer_critique_scan.py` gains a row that rebuilds
`critique.txt` from `critique.md` and refuses a `critique.txt` that differs by one character. The
plain-text section of `canvas-editor.md` names the command, so a later plain-text surface inherits
it. This answers the ticket's open question: the stripping rule lives in the command, and the shared
sheet points at the command rather than restating the rule.

A stripping rule written in the shared sheet and applied by hand, and the ticket's original diff
writing it in `peer-critique` alone, were both declined because neither binds the posted text back to
the file the approval fingerprinted.

## Ruling 5 — the builder keeps what reads as text, drops formatting, and refuses the rest

The builder writes a bold heading line and a `#` heading as its bare text, removes emphasis markers
and backticks, decodes an escaped character such as `\*` to the character, and keeps every blank line
between paragraphs. It keeps list markers (`- ` and `1. `) as written, because they read normally in
plain text. Reference URLs and a real `&` stay literal, as ADR 0204 ruling 2 requires. Any shape it
does not recognize, including a `[text](url)` link, makes the command exit 2 and name the line, so the
draft is repaired before anything is loaded.

Accepting only the template's shapes and refusing lists was declined because a list is something the
clinician would type in a plain comment himself. Stripping bold and italic alone was declined because
a `##` or a bracketed link would then post exactly as typed, which is this ticket's defect in other
characters.

## Ruling 6 — this record changes no earlier ruling

ADR 0204 ruling 2 stands as written; the build defect is the step 6 wording that read it as keeping
the markers, and the build replaces that wording. ADR 0190 ruling 3 stands; its "single gate" is now
the first of two for a Reply. Neither record is marked superseded, because neither ruling is
overturned.

Supersession markers on ADR 0204 and ADR 0190 were declined because they would tell a later reader
that the ampersand ruling or the Reply route ruling had been reversed. Recording the rulings only in
rewritten tickets was declined because the reason a Reply now takes two words from the clinician is
surprising without this record.

## What the build changes

- `skills/_shared/reference/canvas-editor.md`: a section stating ruling 1's stop and ruling 3's
  status line for every Canvas save, and the plain-text section rewritten to name the builder command
  in place of "an exact plain-text build with every character literal".
- `skills/_shared/reference/canvas-editor.md`'s opening scope line, widened from Composers to every
  Canvas save.
- `skills/peer-critique/SKILL.md` step 6: build `critique.txt` with the command, load it, read it
  back, stop at the loaded box, record the posting go-ahead through `approve`, then save. The
  "retain the bold heading markers" and "exact copy with every character literal" wording is
  removed, and "Only an explicit go-ahead authorizes posting" becomes authority to load, not to save.
  `tools/test_peer_critique_skill.py`'s pins on the removed wording move with it.
- `skills/discussion-reply/SKILL.md` step 4: the "single posting gate" sentence is replaced by the
  stop and the recorded posting go-ahead before the submit click, and "Only an explicit go-ahead for
  this reply authorizes posting" is narrowed the same way. Step 5's second reply, which goes from load
  to submit and calls its content approval "a new, explicit posting go-ahead", takes the same stop
  and calls that approval a content go-ahead.
- `skills/practicum-case-study/SKILL.md`'s posting step: "The existing go-ahead authorizes the
  full-body submit click" is replaced by the stop and the recorded posting go-ahead, and the
  attachment fallback's "fresh explicit go-ahead" is recorded the same way.
- A new direct command in `tools/` that writes the plain-text build and refuses unrecognized shapes,
  calling `use_utf8` and `require_python_floor` from its command path, with tests against the
  committed shapes `peer-critique` step 4 prescribes and against each refused shape.
- `tools/peer_critique_scan.py`: the rebuild-and-compare row.
- `tools/approval_record.py`: the reply-kind mark on each history entry, and the completion row
  requiring a posting go-ahead on a run-posted item for the four skills, with the pre-build
  grandfathering in ruling 2.
- `CLAUDE.md`'s console-codec correction list, naming the new direct command.

## What this does not reach

- **Whether the clinician actually looked.** The recorder verifies that his posting go-ahead is his
  own message sent after the content go-ahead; it cannot verify that he opened the tab.
- **`course-assignment`'s Canvas gates.** They are still written by the agent and not checked by the
  recorder, and its deck branch writes no stop before Submit; both are
  [#1648](https://github.com/mshamblin5150-code/clinical-skills/issues/1648)'s question, and this
  ruling leaves them there.
- **How Canvas displays the stripped text.** The posted reading still compares the stored comment
  with `critique.txt`; the legacy page's display remains ADR 0204 ruling 3's.
- **A Markdown shape the builder recognizes wrongly.** The builder's tests are its evidence; a shape
  it misreads as one it knows is outside what its refusal can catch.
