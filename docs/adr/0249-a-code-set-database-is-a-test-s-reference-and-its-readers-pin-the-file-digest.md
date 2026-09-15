# A code-set database is a test's reference and its readers pin the file digest

[#1319](https://github.com/mshamblin5150-code/clinical-skills/issues/1319) was filed from #1310's
grilling on the claim that #1139's build broke a rule `tools/icd10_lookup.py`'s module docstring
states: nothing in `tools/` tests against the committed ICD-10-CM database. Grilled 2026-09-15; the
clinician ruled every point below on that date. #1310's build landed as #1323 during the grilling,
every figure was re-measured against it, and the pin ruling was ruled again on the new measurement.
Nothing is built here; this is the record the build reads.

**Measured at:** 3f8a85605af26e56e55d9083be76823619df8604

## Measured before ruling

**The rule was false the day it was written.** `tools/test_specificity_scan.py` has read the
committed ICD-10-CM database since `b29c0658` on 2026-08-15, and its `TheAuditFiguresAreReDerivable`
docstring gives the reason: the prohibition is against a parser tested on the file its own builder
wrote, and a database standing as the reference is not that. The `icd10_lookup.py` sentence landed a
day later in `a8c3b300`. `CLAUDE.md`'s ICD-10-CM code set section states the narrower rule, which is
true: `test_icd10.py`'s parsers run against committed excerpts.

**Two test modules read a Code-set database.** An AST walk of every import in `tools/` finds four
non-test modules reaching `icd10_lookup` or `procedure_codes_lookup` — the two lookups,
`anchor_scan` and `specificity_scan` — and five test modules importing one of them. All five were run
in one process with a lookup's `open_database` refusing a call that names no path. Refusing the
ICD-10-CM open fails 58 tests, 41 in `test_anchor_scan` and 17 in `test_specificity_scan`. Refusing
the procedure-code open fails 24, all in `test_anchor_scan`. `test_aar_scan`, `test_icd10` and
`test_procedure_codes` fail nothing. Three test files name a reaching script beside `subprocess`, and
each names it in prose only. The walk is a floor: a dynamic import, or a command assembled at run
time, is invisible to it.

**A rebuild from one release moved the data.** #1323 rebuilt `reference/icd10cm-2026.sqlite` from the
same FY2026 April 1 release. Its `meta.release` string changed from one ending
`code-descriptions-tabular-order.zip` to one ending `code-descriptions-in-tabular-order.zip`, and its
index rows rose from 81,515 to 138,980. A release string and an input digest both miss a builder
change on unchanged inputs.

**A file digest is stable.** No `.gitattributes` rule touches either database, each file's bytes on
disk equal its committed blob, and a read-only open leaves the ICD-10-CM file's SHA-256 unchanged.

## Ruling 1 — the rule forbids shared-reader blindness, not a read

A test may take a Code-set database as the reference for any claim except that its builder read the
official release correctly. That claim compares the builder's output with itself, so it belongs to
`test_icd10.py` and `test_procedure_codes.py` over committed release excerpts.
`test_specificity_scan.release_family` builds a clean record from the database before planting a
defect, and it qualifies, because its claim is the scanner's comparison; the anchor route tests
qualify for the same reason. Each such test is blind to a builder defect, and that is stated rather
than hidden. `icd10_lookup.py`'s sentence is corrected where it stands. Forbidding every read was
declined: it rewrites every test measured above, and ADR 0248 ruling 10's controls would need
excerpts cut to the committed notes they grade, which ADR 0243 already declined as input written
knowing the rules. Allowing a read only where the expected values were typed from outside the
database was declined, because nothing can check where a typed value came from and `release_family`
already fails that condition.

## Ruling 2 — a reading module pins the committed file's SHA-256

Every test module that reads a Code-set database first asserts that file's SHA-256 against a named
constant. A mismatch fails before any other test, naming the database and saying the reference was
rebuilt, so the hand-typed expectations are re-derived before the constant moves. A rebuild that
changes no data still trips it, and that price is accepted: once the constant is updated, a red test
is logic rather than moved data. Pinning the ICD-10-CM `meta.release` string, and the procedure-code
database's `source` digests and effective dates, was ruled first and replaced after #1323's rebuild
showed both miss a builder change on the same inputs. Adding input digests to `icd10_build.py` was
declined for the same blindness, and for a rebuild this ticket has no other reason to make.

## Ruling 3 — a committed check measures which modules read

A committed test runs every test module that reaches a lookup through its imports in a subprocess
with Code-set database opens refused, and asserts both directions: the modules that fail are exactly
the modules that carry a pin. The refusal acts on the open, a call naming no path and a call naming
the committed path alike, and never on the file, which would fail every pin whether or not its
module still reads. The import-walk floor is a declared limit printed beside the result. Declaring
the membership in prose alone was declined because it goes stale without failing; requiring a pin
of every module that reaches a lookup was declined because three of today's five read nothing.

## Ruling 4 — the term is Code-set database

`CONTEXT.md` names the committed ICD-10-CM and procedure-code databases **Code-set database** and
avoids *shipped database*, which collides with **Shipped artifact**. The rulings, the corrected
sentence, the pin and the check use it. The tree's other incidental uses of *shipped database* stay,
because rewriting them changes no meaning.

## Consequences recorded as derived rather than ruled

- **No implementation-map edge ties this to #1310**, whose build landed before this record; ruling
  3's check measures its tests.
- **The pin constants live in a `*_test_support.py` module**, beside the existing ones in `tools/`.
- **`test_anchor_scan.py` and `test_specificity_scan.py` point at this record** rather than restating
  it, and the check's module owns what a clean run does not establish in its `DECLARED_LIMITS`.

## What this does not reach

- **Whether a hand-typed expectation was read from the release or copied from a lookup's output.**
  Ruling 1 does not need it.
- **A reading module the import walk cannot see**, which ruling 3 declares.
