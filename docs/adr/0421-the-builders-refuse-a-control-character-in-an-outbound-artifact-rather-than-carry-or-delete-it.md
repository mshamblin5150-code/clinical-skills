# The builders refuse a control character in an outbound artifact rather than carry or delete it

**Measured at:** 7821ce1f7dbc98555b246eaa0bef65105c700f3d

[#1859](https://github.com/mshamblin5150-code/clinical-skills/issues/1859) was filed from the
grilling of #1755 under
[ADR 0395](0395-a-hand-written-run-record-is-read-through-one-shared-reader-that-refuses-a-control-character-by-line-or-field.md)
ruling 6. ADR 0395 kept the work that leaves a run out of its shared run-record reader and named a
refusal before anything leaves as the remedy. #1859 asked three questions: where that refusal
belongs, which characters it refuses, and whether work already posted is rechecked. Grilled
2026-10-19 against `main`, where the freshness gate read `FRESH`. The clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**No builder refuses a control character, and the routes split into two behaviors.** Each builder
was driven through its public function with a tab, bell, NUL, form feed, vertical tab, bare carriage
return, escape and DEL placed in an ordinary prose line. Every string was synthetic.

| Builder | Behavior |
| --- | --- |
| `entry_copy.derive` (the Medatrax **Entry copy**), and `form_sections` after it | Carries all eight into the four boxes and the private JSON |
| `post_text.render` (the **Plain-text build** for Canvas) | Carries all eight mid-line; strips some at a line edge only |
| `post_html.render` (the Canvas HTML) | Deletes all but tab and DEL |
| `docx_write` and `assignment_docx` (the Word documents) | Delete all but tab and DEL |

The deletion is `docx_write.esc`, which keeps a character only if it is at or above a space, or is a
tab. `post_html` and both Word builders escape through it, while `post_text` never calls it. Silent
deletion is a guess about what the writer meant, and it shows: `post_html.render('b\x0bc')` yields
`bc`, so a vertical tab used as a separator joins two words with no trace. In the HTML a form feed
also cuts a link short: `https://e.org/a\x0cb` becomes an anchor to `https://e.org/a` followed by a
bare `b`. Every command boundary reads its input with `Path.read_text`, which turns a bare carriage
return into a line break before any builder sees it.

**The Entry copy's own check passes these characters by design.** `entry_copy._portal_characters`
refuses only a non-ASCII character it has not measured. A C0 character and DEL are ASCII and pass;
a C1 character such as U+0085 is non-ASCII and is refused, as an unmeasured portal character rather
than as damage. A vertical tab is worse than carried: `note_grammar.parse` splits lines with
`str.splitlines`, so `Subjective words.<VT>O:<VT>more.` inside the S section reads as a second `O:`
heading. `entry_copy.check` then refuses with `duplicate or out-of-order note section`, naming no
character. `entry_copy.derive` instead catches the parse failure in its legacy partial-note path and
returns the text unchanged, because the text is all ASCII.

**The glossary already says the plain-text route refuses.** `CONTEXT.md` defines a **Plain-text
build** as refusing a shape the command cannot read rather than guessing. `post_text.render`
returning a bell and a NUL unchanged, driven on the ticket, is that definition broken in code.

**No outbound artifact carries the damage.** A count over every `.md`, `.txt`, `.html`, `.json`,
`.docx` and `.pptx` file under the registered checkouts' `scratch/runs/` and the owning checkout's
`output/`, excluding copied classmate posts, found 4,618 files. It counted C0 except a line ending,
DEL and C1, and read Word and PowerPoint XML parts with character references decoded. 29 files carry
one. None is a note, Entry copy, form-sections record, post, reply, critique, case study, Word
document or deck. They are private captures, transcriptions, saved web pages briefed to a refuter,
and after-action review material. Every Word and PowerPoint file read clean, with no tab element
either. An independent count by note kind agreed: 0 of about 800 outbound artifacts, including the 91
posted Medatrax notes and every posted coursework item. That count covered C0 only; the recount above
adds DEL and C1.

**No skill documents a tab as content.** Every mention of a tab in `skills/` means a browser tab, and
`skills/_shared/reference/apa7-coverage.md` says tables use real table structure rather than tabs.
The only tabs found are in classmates' posts copied into a run, which a reply or critique can quote.

**Two outbound artifacts have no builder here.** The agent builds a PowerPoint deck outside
`tools/`; the last repo code to read its text before upload is the deck grader, which
`assignment_submission._pre_upload_grade` runs before the go-ahead is recorded. The `icd10-cpt`
worksheet is never pasted or posted itself; its codes are typed into Medatrax and verified against
the committed code sets.

## Ruling 1 — the builders refuse, through one shared check

A control character in an **Outbound artifact** is refused by the builder that makes it:
`entry_copy`, `post_text`, `post_html`, `docx_write` and `assignment_docx`. All five call one shared
check. The refusal names the line and the character, never the surrounding text, since a note is a
patient record. `post_html` and the Word builders stop deleting these characters and refuse
instead. The go-ahead gets the check wherever it already re-runs a builder: `approval_record.approve`
runs `entry_copy.check` on every note, and the coursework approval re-reads its sources.

Refusing at the go-ahead only was declined, because the agent would learn of damage after drafting,
at the clinician's approval, while the builders kept carrying or deleting it and the **Plain-text
build** definition stayed false. Refusing in the completion graders was declined because they run
after posting and cannot stop anything, and a frozen item is never regraded. Declaring the gap was
declined on ADR 0395 ruling 1's ground: no real artifact has carried the damage, but the route that
produces it is still open. A script written with the Write tool and then run still turns `\t` in an
ordinary Python string into a tab. Keeping the deletion as cleanup was declined because deleting is
a guess, and the guess has already been shown to weld words and truncate links.

## Ruling 2 — every control character except a line ending is damage, tab included

The set is every C0 character except a line feed or a carriage return directly before a line feed,
plus DEL (U+007F) and the C1 range (U+0080 to U+009F). Tab is damage. A tab in a quoted classmate
passage is replaced by a space.

This is deliberately wider than ADR 0395 ruling 3's run-record set, which is C0 only and allows tab
in copied classmate posts. An outbound artifact goes to systems outside the repository, Medatrax,
Canvas and Word, and nobody has measured what any of them does with a raw tab, DEL or C1 character.
Nothing legitimate in the clinician's work uses one. Adding DEL and C1 costs nothing, because no
outbound artifact has ever held either. Allowing tab, as the tracker-body set does, was declined
because a mistyped `\t` is the commonest damage and the tab is also the one character the HTML and
Word builders do not delete today. The copied-post exception does not transfer: it exists because
the run-record reader reads the copy itself, while an outbound artifact is the clinician's own
words, and a quoted tab costs one space.

## Ruling 3 — the deck grader refuses the same characters before the go-ahead

The deck grader refuses a ruled character in slide text or speaker notes and names the slide. It is
the last repo code to read a deck's text before upload, and the pre-upload grade already runs it
before durable approval. Declaring the deck outside this fix was declined: a tab, DEL or C1
character can be stored legally in the slide XML and would pass unseen, and other C0 damage would
surface only as a deck the grader cannot read. That second outcome was reasoned from the XML rules
and not driven.

The `icd10-cpt` worksheet is outside this record. Its text never leaves the run, and the codes it
carries are verified against the committed code sets when they are chosen.

## Ruling 4 — work already approved is not rechecked

[ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md)
holds: a frozen item is never regraded. Some completion graders rebuild the artifact through a
builder and compare it byte for byte. For example, the peer-critique grader rebuilds the plain-text
comment and the discussion-post grader rebuilds the HTML. There the builder's refusal becomes a
completion check. The build derives that set of graders from the modules that call a builder,
rather than trusting this example. It gets one row in `reference/completion-check-starts.tsv`, compared with
`approval`, so an item approved before the check lands reports `not graded` for it. The census above
is the evidence that nothing already out carries the damage.

Regrading every posted item once was declined because it breaks the freeze to find what the census
already counted as zero. Giving the rebuild refusal no start date was declined because it is
exactly a completion check without a recorded start, which ADR 0346 ruling 4 forbids and the
start-table test refuses.

## Ruling 5 — the population is named Outbound artifact

`CONTEXT.md` gains **Outbound artifact**: the exact text or file made from a run's source for a system
outside the repository, which includes the deck that ruling 3 covers. The **Hand-written run record**
entry used "deliverable", which the glossary lists as a term to avoid under **Graded artifact** and
**Submission**; it now uses the new term. Naming the builders without a term was declined because
the shared check needs a name for what it guards, and the next ticket would reach for "deliverable"
again. Legitimizing "deliverable" was declined because it reopens a word the glossary retired for
blurring graded work with portal entries. "Outbound" already carries this sense in **Outbound
search**.

## What this record does not reach

- **Damage that produces printable characters**, such as a lost backslash. ADRs 0351 and 0395 name
  the same limit.
- **What Medatrax, Canvas or Word do with these characters.** None was measured, and ruling 2 makes
  that question moot by refusing them.
- **An outbound artifact made by a route other than these builders and the deck grader**, such as
  text the clinician types by hand into a portal.
- **The `icd10-cpt` worksheet**, under ruling 3.
- **Items approved before the check lands**, under ruling 4.

## Build checklist

- One shared predicate for ruling 2's set. If ADR 0395's shared run-record module has landed, it lives
  there beside that module's set as a separately named set, with the reason the two differ.
  Otherwise it gets its own module, which ADR 0395's build then joins. It returns each damaged line
  number and character as `line N: U+XXXX`.
- Each command reads its input with `newline=""` so a bare carriage return reaches the check instead
  of becoming a line break.
- `entry_copy`: the check runs in `derive` before `note_grammar.parse` and before the legacy
  partial-note fallback, so a vertical tab is named as damage rather than read as a section break or
  passed through. `check` and `main` inherit it, and so does `approval_record.approve`.
- `post_text.render` and `post_html.render` refuse before building.
- `docx_write`: the refusal runs before `esc`, so `esc` no longer decides anything for builder input.
  `assignment_docx` refuses on every text field it writes, including the title page and `docProps`.
- The deck grader gains a row that refuses a ruled character in slide text or speaker notes and
  names the slide.
- One row in `reference/completion-check-starts.tsv` for each completion grader that reaches a
  builder's refusal through a rebuild, compared with `approval`.
- `CONTEXT.md`'s **Plain-text build** definition becomes true of the code; no wording changes.
- Tests drive each builder's public seam and command with a planted tab, bell, NUL, form feed,
  vertical tab, bare carriage return, escape, DEL and U+0085. Each expects a refusal naming the line
  and character. A Windows-line-ending control artifact builds unchanged. Name these as controls,
  because each is a symptom the check must prevent:
  - a vertical tab followed by `O:` inside the S section, which today `derive` passes and `check`
    refuses as a duplicate section;
  - a form feed inside a URL, which today truncates the HTML anchor;
  - a vertical tab between two letters, which today the HTML and Word builders weld into one word.
