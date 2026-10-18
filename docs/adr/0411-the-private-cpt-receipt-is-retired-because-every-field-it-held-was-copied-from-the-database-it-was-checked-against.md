# The private CPT receipt is retired because every field it held was copied from the database it was checked against

**Measured at:** 91f234ebd4b9e41839f5938784f10819449159b9

[#1811](https://github.com/mshamblin5150-code/clinical-skills/issues/1811) was filed from the
after-action review of a `batch-shift` run (NUR5144 ED shift) on 2026-10-14.
`tools/coding_freshness.py` refused the batch with `CPT source fingerprint changed`: the shared
private CPT receipt in the owning checkout's `scratch/sessions/cpt-2026/` predated a procedure-code
database rebuild, and `tools/cpt_mdm_sheet.py --write-receipt` would write only into the invoking
checkout. The clinic shift hit the same refusal the next day, filed as #1816 and closed as a
duplicate. The ticket asked where the receipt lives and who refreshes it. Grilled 2026-10-18 against
`main` at the commit above, where the freshness gate read `FRESH`. The clinician ruled every point
below in that session, one question at a time. **Nothing is built here; this is the record the build
reads.**

## Measured before ruling

**The receipt's check could not fail on the claim it stood for.** `cpt_mdm_sheet.receipt_fields`
reads the CPT `source` row of the procedure-code database and writes its id, edition, source
SHA-256, and the December 31 of its effective year. `coding_freshness.validate_procedures` then
compares those fields with the same row of the same database. ADR 0251 ruling 6 has the first reader
confirm that the rendered book's edition and ISBN match the database before writing the receipt,
but nothing the reader saw enters the file. Had the book and the database disagreed, the gate would
have printed `PASS`. The only condition it distinguished was a database rebuilt after the receipt
was written, which is the refusal #1811 and #1816 recorded.

**The MDM sheet's header is copied from the database too.** `cpt_mdm_sheet.compare` writes the
sheet's `Book`, `Edition`, and `ISBN (VitalSource ebook)` lines from the `source` row, and the print
ISBN line is a literal in the code. Grading those lines against the database is therefore circular
as well. What the sheet takes from the book is the edition year in each entry's locator, which both
readers type independently; `compare` refuses a year that differs from the database's effective
year, and every entry must carry one year.

**Five receipt files exist.** One shared copy at `scratch/sessions/cpt-2026/cpt-2026-receipt.json`
in the owning checkout, one inside a shift run's own record, and three inside worktree directories
already moved under a Ticket directory. Their contents were not opened; they carry database
identity fields only.

## Ruling 1 — the private CPT receipt is retired

`tools/coding_freshness.py` no longer takes `--cpt-receipt`. Its CPT limb keeps the two checks it
already makes against the procedure-code database: the database's CPT edition must cover the
encounter's service date, and the service date must not fall after that edition's December 31. It
still requires a passing committed MDM sheet whose edition covers the service date. The private pass
receipt continues to record the CPT source id, edition, source SHA-256, database SHA-256, boundary,
and sheet digest, all read from the committed files at gate time. `tools/cpt_mdm_sheet.py
--write-receipt` is removed because nothing consumes it. A receipt file that cannot be checked
against anything the database does not already hold adds a way to go stale and no evidence.

## Ruling 2 — the ISBN confirmation is declared, not checked

The first reader still confirms the rendered book's edition and ISBN before transcribing. That ISBN
match leaves no recorded evidence, and no check is built for it. `coding_freshness.DECLARED_LIMITS`
and `cpt_mdm_sheet.DECLARED_LIMITS` state that the sheet's book, edition, and ISBN lines are copied
from the database, that only the edition year is read from the book, and that the reader's ISBN
confirmation is unrecorded. The edition year is what decides whether a code was valid on the service
date, and two readers check it; the ISBN distinguishes product variants of one year that code
identically. A transcript field for the ebook ISBN was priced and declined: the rendered copyright
page shows the print ISBN while the database holds the ebook identifier.

## Ruling 3 — existing receipt files stay, except the shared copy, which the clinician removes

No command reads a receipt after the build. The copy inside the shift run's record is evidence of
what that run passed against and stays. The three copies under the Ticket directory are already set
aside and stay. The clinician deletes `scratch/sessions/cpt-2026/cpt-2026-receipt.json` in the
owning checkout by hand after the build merges, because it is the one file shaped like a live input.
The build schedules no `scratch/` removal.

## Build checklist

- `tools/coding_freshness.py`: drop `--cpt-receipt` and the receipt comparisons; keep the edition
  coverage and year-end checks against the database; replace the receipt row of `DECLARED_LIMITS`
  with ruling 2's row.
- `tools/cpt_mdm_sheet.py`: remove `--write-receipt` and `receipt_fields`; replace the receipt row
  of `DECLARED_LIMITS` with ruling 2's row.
- `tools/test_coding_freshness.py`, `tools/test_cpt_mdm_sheet.py`, and `tools/test_write_guards.py`:
  remove the receipt cases; drive the gate through its public command with no receipt argument, and
  keep the controls that refuse a service date outside the database edition and after its year-end.
- `skills/icd10-cpt/SKILL.md`: remove the receipt-writing step; drop `--cpt-receipt` from the
  freshness command.
- `skills/clinical-note/SKILL.md` and `skills/batch-shift/SKILL.md`: drop `--cpt-receipt` from the
  freshness command and "with the current private CPT receipt" from its lead-in. This settles #1816's
  question about where batch-shift step 7's receipt comes from.
- `AGENTS.md`: the two Required-command entries stop naming the receipt.
- `CLAUDE.md` maintainer tooling: the *Coding freshness* and *CPT E/M MDM sheet* sections stop
  naming the receipt.

## What this record does not reach

- **Whether the readers read the book at all.** The edition year and exact two-reader agreement are
  recorded; whether either reader looked at the rendered page remains outside every check, as the
  existing limits already state.
- **Mid-year CPT changes within one edition.** The gate judges edition coverage by year; this record
  neither adds nor removes any check on releases inside a year.
- **The ISBN.** Declared under ruling 2 and unchecked.

## Supersedes

- [ADR 0250](0250-a-review-sheet-carries-final-coding-only-after-the-batch-is-fresh.md) ruling 5, the sentence on the durable private CPT receipt. CPT currency is the database edition's coverage of the service date and its year-end, plus the passing sheet.
- [ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md) ruling 6, the receipt the first reader writes. The reader's edition confirmation before transcribing survives; it writes no file.
- [ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md) ruling 7, its references to a CPT receipt. The service-date rule survives and applies to the database edition and the sheet.
- [ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md) ruling 9, the clause "and a new receipt is written". A new edition still needs a rebuilt database and a new two-reader sheet.
