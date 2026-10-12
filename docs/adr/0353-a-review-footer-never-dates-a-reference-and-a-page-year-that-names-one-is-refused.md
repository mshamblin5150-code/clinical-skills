# A review footer never dates a reference and a page year that names one is refused

**Measured at:** 59c440e7a6c2f5c81b33dcd14ce4f6e392693226

[#1566](https://github.com/mshamblin5150-code/clinical-skills/issues/1566) was filed from the
after-action review of a `course-assignment` run (NUR 5042 Module 11) on 2026-10-04. A research
agent took a government web page's reference year from its "last reviewed" footer, a first refuter
affirmed it, and a later read caught it. `research_ledger.py` records where the page year came from in
`PAGE-YEAR` but graded nothing about a year sourced from a review stamp. The ticket left the
recognized vocabulary open. Grilled 2026-10-12 against `main`, where the freshness gate read `FRESH`;
the clinician ruled every point below in that session. **Nothing is built here; this is the record
the build reads.**

## Measured before ruling

**APA has already answered the rule; the sheet does not say it.** The signed-in manual audit's row
for §9.15 in `skills/_shared/reference/apa7-coverage.md`, read to root on 2026-09-08, says a
last-updated date is used only when it demonstrably belongs to the cited content, and that a
last-reviewed date is not a publication or update date because review does not establish a change.
That row grounds `skills/_shared/reference/apa7.md` §39, whose text states neither sentence.
[ADR 0315](0315-a-claim-heading-starts-as-a-question-and-a-record-is-read-at-the-source-s-width.md)
ruling 4 dates an online entry by the publisher's citation form or its last content revision and does
not say whether a review footer is one.

**The page-year rows pass the defect and steer its honest neighbor toward it.** Driven through
`research_ledger.read_records` and `_citation_findings` on synthetic records:

| `PAGE-YEAR` | `REFERENCE` year | page-year finding |
| --- | --- | --- |
| `2024 - Page last reviewed: May 15, 2024 footer` | 2024 | none |
| `2024 - Page last reviewed: May 15, 2024 footer` | `n.d.` | `page-year-disagrees`: 2024 on the page, no year in REFERENCE |
| `the page states no year; footer reads last reviewed` | `n.d.` | none |
| `2020 - published date in header` | 2020 | none |

The first row is the ticket's defect and grades clean. The second is a worker who put the correct
`n.d.` in the reference, and the only finding it gets is answered most directly by copying the footer
year into the reference. A field that states a different second year already fails `page-year-form`
under ADR 0315, so `published 2020; last reviewed 2024` is caught today.

**The defect is live in the ledgers.** Population: every exact-name `runs/*/claims.md` beneath the
`scratch/` root of every checkout `scratch_census.worktree_roots` enumerates, read through
`research_ledger.read_records`; 17 ledgers and 912 `PAGE-YEAR` fields with substance, counts only.
Matcher: case-insensitive patterns over the field text, independent of the grader. Fifteen fields name
a `last reviewed` or `last-reviewed` footer, nine of them as the only dating source named, and eleven
of the fifteen carry their page year into `REFERENCE`. No field matched `medically reviewed`,
`peer-reviewed` or `literature review`. The bare word `reviewed` matched one field beyond the
fifteen; whether it is a footer was not read, because reading it would print ledger text.
Seventy-five fields name a `last updated` style stamp and 73 of them agree with their reference year.
Had the defect been absent, the eleven would have been zero; the instrument discriminates presence of
the wording, not whether each footer was the year's true source.

## Ruling 1 — any `PAGE-YEAR` that states a year and names a review footer is refused

`PAGE-YEAR` holds only the page's own year (ADR 0315 ruling 4), and a review footer is never that
year, so a field that states a year and names one is either the defect or noise. The new finding is
raised whatever `REFERENCE` says, and on that record it replaces `page-year-disagrees`, whose remedy
points the wrong way here. Its remedy: date the entry by the content's own publication or revision
date, or record that the page states no year and write `n.d.` with a retrieval date.

**At its edge the row reads a field that states a year.** A field recording that the page states no
year may say why, including that the only date is a review footer; that is the honest form the
remedy asks for, and refusing it would refuse the fix. Such a field cannot carry the footer's year,
because ADR 0315's form rule already refuses a no-year field holding one.

Refusing only when the reference carries the footer year, as filed, was declined because the `n.d.`
case would keep the misleading disagreement remedy. Refusing only where no other dating word appears
was declined because it rests on a closed list of dating words, and a footer beside a site-wide
copyright year, which APA §9.13 also rejects, would pass. The accepted cost is that a correct field
naming its real date and also mentioning a same-year footer must drop the mention.

## Ruling 2 — a review footer is the word `reviewed` unless it is welded to `peer`

The row recognizes the word `reviewed` in any form, so `last reviewed`, `last-reviewed`,
`Reviewed:` and `medically reviewed on` all match. `peer-reviewed` and `peer reviewed` do not, because
they describe a journal rather than date a page. The bare word `review` does not match, which keeps
`literature review current through` (an UpToDate masthead line) and `systematic review` out.

Matching only the observed `last reviewed` forms was declined because the next site's `Reviewed:` would
repeat the defect before anyone added it. A closed phrase list was declined for the same reason,
later. A false fire costs one reword, since the field has no other reason to say `reviewed`.

## Ruling 3 — a `last updated` stamp is not graded

APA §9.15 permits an update date when it belongs to the cited content, and whether it does is a
reading the refuter already owns under ADR 0315 ruling 4. Counting such stamps on the report was
declined because about 75 mostly correct fields would print on every run and teach the line to be
skipped. Refusing unless the field asserts the update belongs to the content was declined because it
invents a phrasing requirement APA does not make. The limit is declared in the module.

## Ruling 4 — earlier approvals are not graded by the new row

The row takes a start date in `reference/completion-check-starts.tsv`, compared with approval, under
[ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md).
An item approved before it reads `not graded` on this row and frozen grades are untouched. This is the
standing machinery applied, not a new rule.

## Ruling 5 — `sourcing.md` and `apa7.md` §39 both state it

`skills/_shared/reference/sourcing.md`'s record rules gain the case under ADR 0315 ruling 4's first
principle, beside "never by a link-only history row": never by a review footer, and a page whose only
date is one states no year. That is the sheet a worker reads while filling `PAGE-YEAR`.

`apa7.md` §39 gains the §9.15 sentence in its dates paragraph, beside "use `n.d.` when the date is
absent": a last-updated date dates the entry only when it belongs to the cited content, and a
last-reviewed date never does. Every coverage row grounding §39 goes stale on that edit and is
re-confirmed against the diff in the same change, each with a binding note on row 9.16's precedent,
so the committed registry still reads `gone-stale 0`. Placing it in §29 alone was declined because a
fact sheet or report page with a review footer is dated under §20 or §15. Leaving `apa7.md` alone was
declined because the registry would keep certifying a reading its grounded section does not state.

## Build checklist

- `tools/research_ledger.py`: a new kind beside the `PAGE_YEAR_*` constants, traced to #1566 in the
  module's kind-to-ticket table. In `_citation_findings`, when `record.page_year` is not `None` and the field matches
  ruling 2's word, append the new finding and do not append `page-year-disagrees` for that record.
  `page-year-form` and `bare-page-year` keep firing on their own terms.
- `DECLARED_LIMITS` gains ruling 3's limit and the declared ceiling that a footer named in other words
  passes.
- `reference/completion-check-starts.tsv`: a row for the new check at the build's landing time,
  compared with approval.
- `skills/_shared/reference/sourcing.md` and `apa7.md` §39 per ruling 5; re-confirm every coverage row
  grounding §39 and refresh its digest, with a binding note naming #1566's diff.
- `skills/practicum-case-study/SKILL.md` step 3's grader table gains the row, keyed by the existing
  test that requires one sentence per kind.
- Tests driving the public command with synthetic records: `last reviewed`, `last-reviewed`,
  `Reviewed:` and `medically reviewed on` each fire with an agreeing and an `n.d.` reference, and the
  latter raises no `page-year-disagrees`; `peer-reviewed`, `literature review current through`,
  `last updated` and a no-year field explaining a review footer do not fire.

## What this record does not reach

- **A footer named in other words.** `Content checked`, `verified` or a bare date beside no label pass.
- **Whether a `last updated` stamp belongs to the cited content.** Ruling 3 leaves it to the refuter.
- **Whether the field's year truly came from the footer.** The row reads the field's wording, not the
  page.
