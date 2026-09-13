# A resolving locator is not verification and an authored book's chapter is cited as the book

**Measured at:** b7b04b362b6a5ab44b07edd51ae0488a98beeb5b

[#1024](https://github.com/mshamblin5150-code/clinical-skills/issues/1024) was filed by the
after-action review of one `practicum-case-study` run (NUR 5144 Module 2). Three reference entries on
the graded document were structurally complete, and `tools/reference_scan.py` exited clean over all
three: a journal article published online ahead of its issue carried no advance-online label, a whole-book
entry pointed at a repository address typed as one chapter, and a run treated an HTTP 200 as locator
verification until a guessed wrong address also returned 200. The ticket carried a proposed diff to
`skills/_shared/reference/apa7.md` and three open decisions. Grilled 2026-09-13; the clinician ruled
every point below on the same day. Freshness gate `FRESH` at `b7b04b36`. Nothing is built here; this
is the record the build reads.

## Measured before ruling

### The manual confirms the advance-online form and refutes the ticket's chapter fix

Read in the clinician's signed-in Bookshelf on 2026-09-13 by one reader, so every item below is a
claim until the build's registry re-read (ruling 6) records it. Chapter 10 Example 7 is author, year,
article title, italic journal title with no volume, issue or pages, then `Advance online publication.`
in roman type with its period, then the DOI. §9.14 dates it by the advance-online year and prefers a
final publication date once one exists. §8.5 standardizes a publisher's "online first" or "epub ahead
of print" label to advance online publication and says to refresh the publication details before
submission. §10.3 says a chapter of an **authored** book is referenced as the whole book, with the
chapter named only in text (§8.13); the chapter-level form is for edited books and reference-work
entries. §10.3 does not mention group authors, and its rule does not depend on the kind of author.
§9.34 says a URL leads directly to the cited work, and §9.37 says to test reference URLs before
submission. Nothing read distinguishes a chapter-level from a book-level DOI.

The ticket's second hunk offered restructuring the entry "as a chapter in this form" beside §14, the
edited-book chapter form. For the WHO pocket book, a group-authored book, that is the wrong form.

### The diff's registry cost is set by where its text lands

In `skills/_shared/reference/apa7-coverage.md`, manual item 10.1 binds §9, item 10.2 binds §13 and
§14, and item 9.16 binds §7. Fifty-seven items bind §39, where the ticket placed its verification
sentence. `python tools/apa7_coverage.py` reports a stale item and still exits 0, so nothing forces a
re-read after an edit.

### The scanner cannot tell a journal article from other DOI-bearing forms

`reference_scan.Entry` carries no volume, issue, page, journal-title or type field. The `doi-work`
bucket spans source classes by design, so no committed classifier settles that an entry is a journal
article. The sheet's own correct forms with a DOI and no volume, issue or pages include the Cochrane
review (§11), the article-number form without pages (§10), and the book, chapter and report forms.

### Nothing says what verifying a locator means

`skills/_shared/reference/sourcing.md` has no locator rule. The glossary's **Authenticated route**
records that an anonymous fetch can return 200 from a login form, which is a definition and not an
instruction a run follows. The `practicum-case-study` step 9 reader column for
`the reference list, the part no command reaches` does not mention opening locators, and it says
"the command catches that only on a DOI", which is false: `reference_scan.retrieval_date_disposition`
does not consult the DOI.

## Ruling 1. The verification rule lives once, in `sourcing.md`

`sourcing.md` gains a section stating that verifying a locator means opening it and confirming it is
the work's own address, and that a success status is not verification because a near-miss address
and a login form both return one. It is research practice rather than reference form, every fan-out
already reads that sheet, and §39 is not edited, so its 57 bound items stay current.

## Ruling 2. The rule is applied at research time and after drafting, with no scanner row

A claim record's `RESOLVED` field names the address the agent confirmed as the work's own, never a
bare status. The `practicum-case-study` step 9 reader for `the reference list, the part no command
reaches` opens each locator and confirms it identifies the work the entry describes, including whole
book versus chapter and advance article versus final issue. Only the second reaches an
entry-versus-locator mismatch, because that mismatch exists only once the entry is written. The same
edit removes the reader column's false "only on a DOI" clause. Neither application is graded by a
command.

## Ruling 3. An unlabeled advance-online entry stays a reading and is declared

`reference_scan.NOT_REACHED` and `apa7.md` §7 gain a row: an advance online publication with no label
is not reached, because the command cannot tell a journal article from a Cochrane review, book,
chapter or report carrying a DOI. The row takes the per-limit behavior handler every `NOT_REACHED`
row requires.

## Ruling 4. §9 carries the advance-online form

§9 gains a paragraph citing Example 7 and §§8.5 and 9.14: the periodical element is the italic journal
title alone, followed by `Advance online publication.` in roman type, then the DOI; the date is the
advance-online year; `online first` and `epub ahead of print` labels are written as advance online
publication; before submission the run checks whether volume, issue and pages have since been
assigned and uses the final form and year if so; and `in press` (§3) is a different state, accepted and
not yet published anywhere, carrying no DOI.

## Ruling 5. §13 carries the whole-book rule and §14 is unchanged

§13 gains a paragraph citing §§8.13, 9.34 and 10.3: a chapter of an authored book is cited as the whole
book, with the chapter in the in-text citation only; §14's chapter form is only for a chapter in an
edited book; the entry's DOI or URL is the book's own, so where a repository types the intended address
as part of the book, the run uses the book's own record; and a locator that resolves proves an address
exists, not that it identifies the work the entry describes.

## Ruling 6. The build re-reads what it stales, so the ticket is `ready-for-human`

The build edits §7, §9 and §13, which stales manual items 9.16, 10.1 and 10.2. The ticket is done when
those three are re-read in the clinician's signed-in session and `python tools/apa7_coverage.py`
reports `gone-stale 0`. An agent can make every edit; the re-read needs the session.

## Rejected options

**The ticket's §14 chapter restructuring.** The manual reserves the chapter form for edited books, so
following it would write a wrong entry for an authored book.

**The verification sentence in `apa7.md` §39.** It stales 57 manual items for a rule about research
practice, not reference form.

**The rule in both `sourcing.md` and `apa7.md`.** Two copies of one rule can drift with nothing
failing.

**A scanner row for a DOI with no volume, issue, pages or label.** It fires on the sheet's own correct
Cochrane, article-number, book, chapter and report forms unless a journal-article classifier exists,
and none does.

**A row keyed on a journal-title vocabulary.** The repository holds no such vocabulary, and building
one for one observed entry is a guessed classifier.

**A pointer to §13 from §14.** A second statement of one rule, and §14 needs none to stay correct.

**Shipping the edits with the three items stale, with or without a follow-up ticket.** It puts new
sheet text beside a registry that no longer vouches for its section, which is the shape the ticket's
2026-09-10 sweep flagged.

## What none of this reaches

Whether a run actually opens a locator; both applications are readings. Whether a chapter-level DOI
or a book-level DOI is correct when a publisher assigns both, which the manual pages read do not
settle. Whether an advance-online entry was refreshed before submission. Whether the single reader's
manual paraphrase above is accurate, until ruling 6's re-read records it.
