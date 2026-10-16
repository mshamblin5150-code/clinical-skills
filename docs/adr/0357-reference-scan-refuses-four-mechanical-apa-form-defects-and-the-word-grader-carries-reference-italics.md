# Reference scan refuses four mechanical APA form defects and the Word grader carries reference italics

**Measured at:** 5433dba9749b5d0109c6b490abd502fb7505a5c0

[#1570](https://github.com/mshamblin5150-code/clinical-skills/issues/1570) was filed from the
after-action review of a `course-assignment` run (NUR 5042 Module 11) on 2026-10-04. Independent page
reads of the final Word paper found reference-list defects `tools/reference_scan.py` never reported,
each fixed only after a full rebuild: article-number entries without the `Article` label, a
file-format bracket after a title, an identifier italicized inside a title, a site name repeating its
group author, and retrieval dates on the wrong kind of work. The clinician ruled every point below
on 2026-10-12, against `main` at the commit above, where the freshness gate read `FRESH`. **Nothing
is built here; this is the record the build reads.**

## Measured before ruling

**The scanner passes all four mechanical shapes, and the instrument could have seen a failure.**
Synthetic Markdown drafts, each a four-entry list with matching in-text citations, were run through
`python tools/reference_scan.py <draft> --as-of 2026-10-12`. For each shape the defective draft and
its APA-correct twin both exit 0 with no finding. A control draft whose list is out of order exits 1
with `list-not-sorted`, so a zero is a pass and not a dead harness.

**On a Word paper the scanner never sees italics.** `assignment_docx_scan._paragraphs` joins the
`w:t` text of each paragraph and drops its run properties, and `survey` hands that text to
`reference_scan.read_document`. Driven directly: an UpToDate entry written `In J. Doe (Ed.),
*UpToDate*.` raises nothing, and the same entry with the asterisks removed, which is what the Word
route delivers for a correctly italicized entry, raises `uptodate-italics`. So a correct Word paper
citing UpToDate is refused today, and an italic-identifier row could never fire on the route this
defect shipped through.

**A deck's reference slides get no form check at all.** `tools/deck_scan.py` does not import
`reference_scan`; it only joins citation keys against the claim ledger. Filed as
[#1771](https://github.com/mshamblin5150-code/clinical-skills/issues/1771) on the clinician's ruling
that it is an inherited gap rather than part of this ticket.

**What the M11 run actually shipped.** Read off the retained Word exports in that run's `render/`
passes, counts and shape classes only:

| Defect | In pass 1 | Shape |
| --- | --- | --- |
| `[PDF]` bracket | 2, then 3 in pass 5 (one added by a refuter's correction), 0 from pass 9 | the word `PDF` |
| Missing `Article` label | 7 entries; the label count goes from 2 to 9 by pass 9 | 2 numbers open with `e`; 5 are digits only, of 1, 2, 3, 4 and 17 digits |
| Identifier italic inside the title | 3 entries, roman from pass 12 | 2 end in a parenthetical holding the word `Table` and a letter-and-digit code; 1 is a bare code of an all-capital abbreviation and 8 digits |

The bracket and label counts were re-derived by this session from the pass 1, 5 and 9 exports; the
shape classes are a reader's report and were not re-read. Of the seven unlabeled numbers, all seven
entries carry a DOI: both `e` numbers and the 17-digit number appear in their own DOI as a delimited
token, and the other four do not. On the nine page-range articles in the same list, no page number
appears as a token in its own DOI.

**What APA says, read in the signed-in *Publication Manual*.** §9.27 (p. 294): an article number,
"which may be called 'eLocators'", takes `Article` and the number in place of the page range; the
manual gives no test that tells an article number from a page number. §9.1 (pp. 281–282): a work's
format, PDF named among them, has little if any effect on its reference entry, and §9.21 (p. 292) lists
only kinds of work as bracket descriptions. §9.19 (p. 291): any information given in the publication
for its identification follows the title in nonitalic parentheses, "e.g." making its examples open.
§9.24 and §9.33 (pp. 293, 297): omit the publisher or site name when it is the same as the author.
`skills/_shared/reference/apa7.md` states the site-name rule and the `Article` form, but carries no
sentence for the file-format rule or for §9.19, although its coverage row for 9.19 says §39 grounds it.

**Prototype predicates, priced against the sheet's own examples.** The 21 `Synthesized example`
paragraphs in `apa7.md`, joined across their wrapped lines, are a correct population. A group-author
site-name predicate fired on 0 of them, caught 9 of 9 group-author examples with the author planted
back before the locator, and stayed silent on a title that itself ends in the author's name. An
italic-identifier predicate keyed on an identifier word or five digits fired on 0 of them, caught both
M11 shapes in invented stand-ins, and stayed silent on `(COVID-19)`, `(HP2030)` and `(2000-2019)`
ending a title. These were throwaway measurements of feasibility, not the build.

## Ruling 1. The Word grader carries italics into the reference list it hands the scanner

`assignment_docx_scan` marks each italic run in a `Reference`-styled paragraph as `*...*` in the
Markdown it passes to `reference_scan.read_document`. Body paragraphs keep their current plain text,
so number tracing and the other body rows read exactly what they read now. This removes the false
`uptodate-italics` refusal on a correctly italicized Word paper and makes ruling 4 reachable there.

Grading italics on Markdown drafts only, and declaring them unread on a Word paper, was declined: the
defect shipped on a Word paper and the UpToDate row would have to go silent there. Leaving it was
declined because the false refusal teaches a run to un-italicize UpToDate to pass. The same blind spot
is the one [ADR 0333](0333-a-bold-references-label-is-read-off-the-word-path-and-an-oversized-memory-index-fails-the-review.md)
met for bold.

## Ruling 2. A missing `Article` label refuses where the number is certain and is named where it is not

On a journal entry whose locator after the volume and issue is a single number with no range and no
`Article` before it:

- the scanner refuses when the number opens with a letter (`e0123456`), or when its digits appear as a
  delimited token in the entry's own DOI;
- every other such entry is counted on every run and named under `--show` as a reader candidate. The
  candidates never change the exit status, and the reference-list reading rules on each one.

APA prescribes the same written form for a one-page article, `*17*(3), 245.`, so a bare number cannot
be refused without refusing correct work. The ticket's list-consistency rule was declined because APA
requires no consistency and it would fail a correct one-page article in a list that also cites an
article-number paper. Refusing every bare number was declined for the same reason. This candidate line
is the one report-only output among the new rows, carved out under ruling 5's exception. On M11 the
refusals reach three of the seven and the candidates name the other four.

## Ruling 3. A bracket holding only a file format is refused

The scanner refuses a square bracket whose whole content, ignoring case, is one of `PDF`, `PDF file`,
`PDF document`, `Word document`, `.pdf`, `.docx`, `.doc`, `.pptx`, `.xlsx` or `.csv`. A description of
the kind of work, such as `[PowerPoint slides]`, `[Policy brief]` or `[Data set]`, stays legal. A
format word outside the list passes and is declared; the list grows on evidence. `apa7.md` §39 gains
the §9.1 and §9.21 rule.

An allow-list of descriptions was declined because §10.4 tells the writer to use whatever terminology
fits, so any list would refuse correct descriptions.

## Ruling 4. An identifier italicized at the end of a title is refused when it is recognizable

The scanner refuses an italic span that ends in a parenthetical whose text contains an identifier word
(`No.`, `Nos.`, `Report`, `Publication`, `Pub.`, `Vol.`, `Vols.`, `ed.`, `Edition`, `Issue`, `Series`,
`Table`, `Project`, `Document`) or a run of five or more digits. A short bare code such as
`(CMS-1807-F)` passes and is declared, and so is a title whose own wording ends in a parenthetical
holding one of those words. `apa7.md` §39 gains the §9.19 sentence its coverage row already claims.

Refusing any digit-bearing final parenthetical was declined because public-health titles routinely end
`(COVID-19)` or in a year range.

## Ruling 5. The new rows refuse

Ruling 2's refusing half, 3, 4 and 6 add rows that set exit 1 like the scanner's existing rows.
Report-only rows were declined because the M11 run passed these defects through every check, and a
line that never fails is the line a run learns to skip. The exception is ruling 2's candidate count,
the one check that could not be cut to what APA's text makes certain.

## Ruling 6. A site name equal to a group author is refused

For an entry whose author contains no personal initials, the scanner refuses when the last element
before the URL or DOI, standing as its own element outside the italic title, equals the author. The
comparison ignores case, spacing and a trailing bracketed abbreviation on the author, so `American
Psychological Association [APA]` matches `American Psychological Association`. An abbreviation-only
site name (`WHO` for `World Health Organization`) and personal-author entries pass and are declared.

Treating an abbreviation as a match was declined because §9.24 says "the same" and a looser reading
could refuse correct work.

## Ruling 7. The retrieval-date direction stays a reading

Whether a work is designed to change remains the declared reading it already is in `NOT_REACHED` and
`apa7.md` §7. Nothing here moves it.

*Superseded 2026-10-16.* The words "Nothing here moves it." are narrowed by
[ADR 0367](0367-a-patient-faq-takes-no-retrieval-date-and-five-reference-shapes-are-refused-where-apa-makes-them-certain.md)
ruling 2: a recognizable patient FAQ is graded as a webpage and its retrieval date is refused.
Whether any other work is designed to change stays the declared reading.

## Build checklist

- `tools/assignment_docx_scan.py`: ruling 1, limited to `Reference`-styled paragraphs, with a test that
  builds a real `.docx` through `tools/docx_write.py` or `tools/assignment_docx.py` and shows an italic
  run reaching `reference_scan`, and that a correctly italicized UpToDate entry no longer refuses. Land
  this before ruling 4's row.
- `tools/reference_scan.py`: one kind per ruling 2's refusal, 3, 4 and 6, traced to #1570, plus ruling
  2's candidate count on the report and its entries under `--show`. Each declared limit above goes into
  `NOT_REACHED`.
- `tools/assignment_docx_scan.py` passes the candidate count through to its own report, so the
  go-ahead shows it.
- `skills/practicum-case-study/SKILL.md` step 7's defect table gains a sentence per new kind, which the
  existing `ROW_PHRASES` binding requires. The step-9 reference-list reader and the `course-assignment`
  page reading are briefed to rule on each candidate.
- `skills/_shared/reference/apa7.md`: §39 gains the §9.1/§9.21 and §9.19 sentences; §7 names every new
  declared limit, which its existing two-way bind with `NOT_REACHED` requires. Every coverage row
  grounding §39 is re-confirmed against the diff and its digest refreshed, so the registry still reads
  `gone-stale 0`.
- `reference/completion-check-starts.tsv`: a row for each new kind at the build's landing time,
  compared with approval, under
  [ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md).
- Tests driving the public command with synthetic drafts: a positive and a negative per kind, the
  `(COVID-19)`, `(HP2030)`, year-range, `[PowerPoint slides]`, one-page-article and title-ending-in-author
  controls staying silent, a digits-only number appearing as a candidate and not a finding, and the
  scanner's own every-kind-fires draft extended to the new kinds.

## What this record does not reach

- **Whether a bare single number is a page or an article number.** Ruling 2 hands it to a reader.
- **Short bare identifier codes, unlisted format words, and abbreviation-only site names.** Each is a
  declared miss in `NOT_REACHED`.
- **Deck reference slides.** [#1771](https://github.com/mshamblin5150-code/clinical-skills/issues/1771).
- **Whether a work is designed to change.** Ruling 7.
