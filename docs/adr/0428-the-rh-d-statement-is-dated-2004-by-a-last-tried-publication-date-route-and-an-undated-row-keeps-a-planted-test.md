# The Rh(D) statement is dated 2004 by a last-tried publication-date route and an undated row keeps a planted test

**Measured at:** 8e8e3340fed0cf89c8df10d4a2f569187123a1ba

[#1888](https://github.com/mshamblin5150-code/clinical-skills/issues/1888) was filed from the
tracker sweep closing [#1812](https://github.com/mshamblin5150-code/clinical-skills/issues/1812)'s
grilling. `reference/guidelines-uspstf.md` gives both Rh(D) incompatibility rows (`rhrs.pdf`) the
year `not stated`, and
[ADR 0412](0412-a-matcher-a-note-pass-satisfies-by-rewording-is-retired-and-a-uspstf-citation-names-its-topic-by-copying-the-sheet-title.md)
ruling 6 grades a citation of that topic on grade alone because of it. Ruling 6 left the year itself
as "a question for `tools/uspstf_table.py`'s derivation rule", filed separately; this is that
record. Grilled 2026-10-19 against `main` at the commit above, where the freshness gate read
`FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The document is dated.** Its extracted text, read from the shared extracted corpus at
`C:/codeing/guidelines-text`, carries on its third page a line reading only
`AHRQ Pub. No. 05-0566-A` and, on the next line, only `November 2004`. Its body also names `1996`
twice, both times as the year of the earlier recommendation this statement updates.

**The derivation cannot read it.** `uspstf_table.derive_year` looks at a document's first three
pages for a year in a journal-citation line, then in a `published online`, `copyright` or `©`
line, and otherwise returns `not stated`. An AHRQ publication-number line followed by a month-year
line is neither.

**The defect is this one document.** `derive_year` was run over all 90 USPSTF text files, each split
into pages on its form feeds as the table build reads them. Exactly one returns `not stated`:
`rhrs.txt`. A pattern for an own-line AHRQ publication number followed immediately by an own-line
month and four-digit year matches in exactly one document, that same one, on its third page, and
reads 2004. The table's year column holds `not stated` on exactly the two Rh(D) rows.

**The catalog's reason was false, and a ruling rested on it.** `reference/guidelines-catalog.md`
carries the row's year as `?` and names it in its closing list with the reason "no date appears
anywhere in its three pages". The blind independent reading in
`reference/guidelines-catalog-audit.md` read the year as `2004` from the page-3 publication line,
and a dated clinician ruling in that ledger confirmed the catalog's `?` over that reading. That ruling
row carries the same rationale as 320 other ruling rows recorded that day, so it is a bulk
confirmation of catalog values rather than a reading of this document's date. The catalog audit
refuses a ruling on a cell where the catalog and the independent reading agree.

**ADR 0412 ruling 6 and ADR 0417 ruling 4 are unbuilt.** No module in `tools/` yet prints the line
that a year was not compared, and the coverage selector in
[ADR 0417](0417-the-clinical-go-ahead-shows-its-paired-grader-s-coverage-lines-before-the-ask-and-refuses-an-approval-that-did-not.md)
has not gained `not compared`. Their builds are #1812 and
[#1845](https://github.com/mshamblin5150-code/clinical-skills/issues/1845), both open and labeled
`ready-for-agent`.

## Ruling 1 — 2004 is the document's year, in both artifacts

`rhrs.pdf` is dated 2004 in `reference/guidelines-uspstf.md` and in
`reference/guidelines-catalog.md`. The catalog's year cell becomes `2004`, which agrees with the
independent reading. The ledger's year ruling for `rhrs.pdf` is retired: its row is deleted from
the audit ledger's clinician rulings, and the closing-list entry giving the false reason is removed.
The title ruling for the same document is untouched.

**Declined:** keeping `?` and `not stated` and correcting only the false reason, which leaves two
blanks for a date the page states and needs a reason the printed date does not count that nobody
has; and correcting the USPSTF table alone, which leaves two committed artifacts disagreeing about
one document with nothing to reconcile them.

## Ruling 2 — a third year route, tried last

`derive_year` gains a third route, tried only after the journal-citation and copyright routes have
found nothing in the evidence pages. It reads a line that is only an AHRQ publication number,
immediately followed by a line that is only a month name and a four-digit year, and returns that
year. Running last makes it safe by construction for every document that already derives a year: no
such document can move. The measurement above says it moves exactly the two Rh(D) rows.

The table stays derived, which is the contract the repository states for it; the year is not typed
into the table or into a per-document override.

**Declined:** a filename-to-year override inside the generator, which moves a fact out of the
document and into code and invites the next entry instead of a rule; and taking the first four-digit
year on the page, which picks 1996 here, the year of the recommendation this one replaced.

## Ruling 3 — ADR 0412 ruling 6 stays, and its tests plant an undated row

ADR 0412 ruling 6 stands as a fallback for any future row whose year is not stated. Once ruling 2 is
built the shipped table has no such row, so the line that a year was not compared has no live
member. The builds of ADR 0412 ruling 6 (#1812) and of ADR 0417 ruling 4's `not compared` selector
(#1845) test that line against a planted `not stated` row, never against the shipped Rh(D) rows.
That makes each of the three builds correct whatever order they land in.

**Declined:** retiring ruling 6 and refusing an undated row, which would block the table rebuild or
fail every citation of a document whose date genuinely cannot be read; and holding this build until
#1812 and #1845 land, which keeps a known-false blank in the table and leaves a follow-up edit to two
finished builds for someone to remember.

## Build checklist

- `tools/uspstf_table.py`: add the third route to `derive_year` after the two existing routes, keyed
  on the own-line publication number followed immediately by the own-line month and year. Update its
  docstring to name the three routes in order.
- `tools/testdata/uspstf/`: add a public-domain excerpt carrying the page-3 publication-number and
  date lines of `rhrs.pdf`. The existing `ahrq-sentence-grade` excerpt, page 1 of the same document,
  carries both `1996` mentions and is the control that the route never chooses 1996.
- `tools/test_uspstf_table.py`: the route reads 2004 from the new excerpt; page 1 alone still reads
  `not stated`; a document whose journal-citation or copyright route finds a year keeps it when a
  publication-date pair is also present; a publication-number line not followed immediately by a
  month-year line reads nothing.
- Rebuild `reference/guidelines-uspstf.md` with
  `python tools/uspstf_table.py "C:/codeing/guidelines-text"` and confirm by diff that exactly the
  two Rh(D) year cells move, both to `2004`.
- `reference/guidelines-catalog.md`: set the `rhrs.pdf` year cell to `2004` and remove its year entry
  from the closing list. `reference/guidelines-catalog-audit.md`: delete the `rhrs.pdf`
  year ruling row. `python tools/guidelines_catalog.py` exits clean.
- Do not edit ADR 0412 ruling 6 or the ADR 0417 build; ruling 3 above is carried to #1812 and #1845
  as tracker notes.

## What this record does not reach

- **Whether 2004 is still the current USPSTF statement on this topic.** Edition currency belongs to
  `reference/guidelines-currency.md`, where `rhrs.pdf` is recorded as `unjoinable`; this record
  dates the document in the corpus and says nothing about a later statement.
- **The month.** The table and catalog carry a year; the printed November is the AHRQ publication
  date and is not recorded.
- **A future document dated some other way.** The third route reads one shape. A document with no
  journal citation, no copyright line and no publication-number pair still reads `not stated`, and
  ruling 3 keeps that path graded.
- **ADR 0412's own figure that 141 of the 143 sheet rows are indexed.** That is a measurement of the
  table as it stood when that record was written, and it is left as written.
