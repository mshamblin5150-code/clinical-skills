# A deck reference list is read from the second reader's reference slides one paragraph per entry and the Word renderer's two rows do not apply

**Measured at:** 4dbf0795b56f31864d63103bb4a9584bcf6ee9ae

[#1771](https://github.com/mshamblin5150-code/clinical-skills/issues/1771) was filed from #1570's
grilling, which ruled decks outside
[ADR 0357](0357-reference-scan-refuses-four-mechanical-apa-form-defects-and-the-word-grader-carries-reference-italics.md)
and left this gap on its own. A `course-assignment` deck's reference slides get no APA
reference-form check: `tools/deck_scan.py` does not import `tools/reference_scan.py`, while the Word
branch runs `reference_scan.read_document` and `reference_scan.survey` from
`assignment_docx_scan.survey`. Grilled 2026-10-17 against `main` at `2bb7eb69`, where the
freshness gate read `FRESH`; the clinician ruled every point below that day. Before this record
landed, `main` changed two modules it reads: `reference_scan` gained the numbered-series ordering of
#1796 and `reference_alphabets` gained the German row of ADR 0399. Neither moves a fact below, and
every code fact here was re-read at the commit above.

## Measured before ruling

**The only retained deck with a reference list does not have the shape the tests build.** The
account's retained course-assignment decks were read by a subagent that reported counts only, under
the scratch PHI rule. One of them carries reference slides, a contiguous run at its end. None of
those slides has a PowerPoint title placeholder: each heading is a plain text box reading
`References` followed by a bar and a qualifier, each entry is its own text box holding one
paragraph, and each slide carries a page-number box. Every entry sits whole on one slide, no entry
paragraph carries a forced line break, every run is explicitly set non-italic, and no entry carries
a left margin or first-line indent. `tools/test_deck_scan.py` builds a reference slide as a
`References` title placeholder over one body placeholder, so a matcher keyed on the tests would have
found none of the real slides. These facts were measured against private retained material that
nothing committed re-derives, so they are stated here and pinned nowhere.

**No retained run has an `intent.md`.** Both decks predate the presentation-intent record, which
`_presentation_intent_findings` now requires on every deck scan. So the second reader's
`REFERENCE-SLIDES` population exists whenever a deck can pass, but could not be compared with any
heading matcher on real material.

**On that deck the order of entry boxes in the slide part matched their top-to-bottom order on
screen on every reference slide.** That is one deck; nothing keeps the two orders equal.

**The deck carries no in-text citation anywhere.** Neither a slide face nor a speaker note holds a
parenthetical author-year citation, or any parenthesis holding a year, outside the reference slides'
own notes.

**Two `reference_scan` rows exist because of the Word renderer.** `heading-not-apa` refuses a heading
other than `References` or `Reference` and names the renderer's missing hanging indent as the harm;
`entry-not-a-paragraph` refuses an entry the renderer would set as a list item or table cell. The
Word branch already hands the scanner a synthesized `# References` heading whenever its heading
paragraph reads `References`, so `heading-not-apa` does not fire there either.

**`deck_scan` already treats slide faces and speaker notes together as the deck's text** when it
traces figures to claim records, and its words-per-bullet count reads every word on a slide face,
so a parenthetical citation such as `(Smith, 2020)` counts two words against the signed limit.

**`deck_scan` resolves no paper language.** It takes no `--paper-language` or `--profile` option.
`assignment_docx_scan.load` takes the `--paper-language` value, else `bar.md`'s `PAPER-LANGUAGE`
field, and hands that to `reference_alphabets.paper_language`, which falls back to the account
profile's single `PAPER-LANGUAGE` answer. `reference_scan.survey` grades alphabetical order only for
a language in the committed table, and reads it `not graded` otherwise.

## Ruling 1 — the second reader's list decides which slides are reference slides

The deck reader checks the slides named by `REFERENCE-SLIDES` in the presentation-intent record. A
slide whose first text opens with `Reference` that the record does not list, and a listed slide whose
first text does not open that way, each enter the shared unread remainder under
[ADR 0230](0230-a-measured-partial-read-prints-an-admissible-unread-remainder-that-exits-not-scanned-and-is-declared-only-where-no-candidate-count-is-admissible.md),
so a disagreement makes the scan incomplete rather than clean.

A heading matcher alone was declined because it makes one matcher both the population and its
reader, misses a slide headed `Sources` or `Works Cited`, and would have to accept the qualified
heading. A title-placeholder matcher was declined on the measurement: it finds none of the real
deck's reference slides and would report that deck clean having read nothing.

## Ruling 2 — reference slides become an entry list strictly, in the order the audience reads

Listed slides are read in the record's order; boxes on a slide are read top to bottom by on-screen
position, left to right on a tie. Each nonempty paragraph is one entry, and a forced line break
inside a paragraph is read as a space. The heading box and a box whose only text is a number are
skipped. An entry carried onto the next slide is not rejoined: it reads as two broken entries and
fails as such.

Rejoining a paragraph that does not open like an entry was declined because "opens like an entry"
is a guess, and an entry genuinely missing its author would be merged silently into its neighbor.
Reading boxes in their stored order was declined because the stored order can diverge from what the
audience sees after an edit, and alphabetical order would then be graded on an invisible sequence.

## Ruling 3 — explicit italic runs are carried as on Word

The deck reader marks each run whose own run properties set italics as `*...*`, joining adjacent
italic runs, which is ADR 0357 ruling 1's rule for a Word reference paragraph. Italics a run
inherits from its paragraph defaults, list style, slide layout or theme are not read, and the
module's declared limits say so. That blind spot fails safe: an inherited-only italic UpToDate
reads as roman and is refused, and the fix it teaches is setting italics on the run.

Resolving inherited italics was declined as several inheritance levels for a case no real deck
shows, departing from the Word precedent. Carrying no italics was declined for the reason ADR 0357
declined it on Word: `uptodate-italics` would either refuse every correct entry or go silent on
decks.

## Ruling 4 — every `reference_scan` row applies except the two Word renderer rows

The reader hands `reference_scan` a fixed `References` heading and every entry as a plain paragraph,
so `heading-not-apa` and `entry-not-a-paragraph` never fire on a deck. Both exclusions are declared
in the deck module's limits. Every other row applies unchanged, including `canvas-artifact`, the
retrieval-date rows dated against the signed bar, and the ADR 0357 rows.

Passing the real heading through was declined: the real deck would fail all its reference slides on
a slide-title convention APA does not govern, under a finding naming a renderer indent slides cannot
have. Stripping a qualifier after a separator was declined as an invented heading grammar. A listed
slide headed something else entirely is still caught, by ruling 1's cross-check.

## Ruling 5 — in-text citations are read from slide faces and speaker notes together

The body handed to `reference_scan` is the deck's slide faces and speaker notes, the same text
`deck_scan` traces figures through, and all the citation rows apply: `uncited-entry`,
`unlisted-citation`, `intext-year-mismatch`, `missing-first-author-initials` and
`citation-author-spelling`, with `citation-reader-coverage` reported. A reference list the talk never
cites is refused. `skills/course-assignment/SKILL.md` gains the instruction naming where deck
citations go, so the first run under this check is told the rule it is graded by.

Slide faces alone were declined because each citation would spend words against the signed
words-per-bullet limit and the deck's text would have two definitions. Leaving the citation rows off
decks was declined because it lets a reference list the talk never uses, and a citation with no
entry, pass.

## Ruling 6 — a reference entry on a slide carries its own hanging indent

A new deck row refuses a reference entry paragraph whose own paragraph properties do not set a
positive left margin with a negative first-line indent. An indent inherited from the slide layout
or theme is not read, which fails safe as ruling 3 does. Bullets on entries are not graded, and the
module's declared limits say so, because an explicit-only reading would miss a bullet inherited from
a layout and pass it silently.

Leaving layout to a separate ticket was declined because the same reader is being built and the real
deck already shows the defect. Making it the visual reader's brief alone was declined as a verdict
with no mechanical failure.

## Ruling 7 — the new checks start when their build lands

Each new deck check takes a row in `reference/completion-check-starts.tsv` dated at its build's
landing and compared with the item's approval, the repository's rule for a new check, so earlier
approvals read `not graded`. ADR 0394 ruling 3 adds deck rows to the same table and edits the same
module; whichever build lands second rebases and keeps the other's rows.

## Ruling 8 — a deck takes its paper language by the Word branch's lookup

Ruling 4 applies the alphabetical-order row, and that row files entries by the alphabet of the
paper's language under
[ADR 0356](0356-the-paper-language-picks-the-filing-alphabet-and-english-files-a-special-letter-as-its-plain-letter.md).
The deck grader resolves that language exactly as `assignment_docx_scan.load` does: a
`--paper-language` value wins, then `bar.md`'s `PAPER-LANGUAGE` field, then the account profile's
single answer through `reference_alphabets.paper_language`, with `--profile` selecting another
profile. With no answer, or a language the table lacks, reference order reads `not graded` with the
language named, as it does on a paper. `skills/course-assignment/SKILL.md` already sends both
branches through the Paper language reference before first prose, so an ordinary deck run has the
saved account answer; the build extends that step's sentence naming the DOCX grader's flag to the
deck grader.

Reading the profile alone was declined because a deck in another language would draw order
findings that no per-deck override could correct. Declaring deck reference order ungraded was
declined because every deck with a reference list would then report an incomplete scan.

## What this record declines from #1771

Nothing in the ticket's four decisions is left open. Its first decision is rulings 1 and 2, its
second is ruling 3, its third is rulings 4 to 6 and 8, and its fourth is ruling 7.
