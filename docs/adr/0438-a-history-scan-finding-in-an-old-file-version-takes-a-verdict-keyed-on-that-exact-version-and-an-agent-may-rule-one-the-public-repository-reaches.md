# A history scan finding in an old file version takes a verdict keyed on that exact version and an agent may rule one the public repository reaches

**Measured at:** 346cb62d61268a2620d517f707ea3e1be0597c1e

[#1928](https://github.com/mshamblin5150-code/clinical-skills/issues/1928) was filed from the
tracker sweep that closed #1921's grilling. [ADR 0415](0415-a-shift-day-date-is-exempt-only-in-a-declared-position-and-the-full-audit-itemizes-only-fixture-content.md)
ruling 7 takes most `corpus-date` findings out of `tracker_scan --history`'s exit status. It leaves
`corpus-name` and shape findings listed and graded, as `--all` does. The ticket found that some of
those findings have no route to a clean result: an old file version cannot be edited, and
`reference/tracker-scan-rulings.json` has no row an old version's finding can match. Grilled
2026-10-19 against `main` at the commit above, where the freshness gate read `FRESH`. The clinician
ruled each point below in that session, one question at a time. **Nothing is built here; this is
the record the build reads.**

**Standing rule 1. No name, date value, blob id, file line or line number from the scan appears in
this record, and none may be added.**

## Measured before ruling

Three session readers imported `tracker_scan.blob_records` and `phi_scan.scan_file_text` from this
checkout and ran them at the commit above with the corpus layer `ACTIVE`. They printed counts only.
Their matchers are this session's, so the figures are a baseline the build re-derives.

- **9,084 reachable text blobs** carry **373 `corpus-name` findings**, 139 of them in
  fixture content as ADR 0415 ruling 4 defines it. **Every one matches one of the 21 harvested
  strings that have never been ruled on.** None matches the one string already ruled a real name.
- The same blobs carry **60 shape findings in 26 blobs**: 56 `us-short-date`
  and 4 `dob-with-date`, the latter in a single blob. None is in fixture content.
- Those 60 findings are **23 distinct lines in 7 files**, keyed on path, rule and
  line digest. The rest are the same line in a later version of the same file. 12 of those lines
  still sit in one tracked file, and that file now declares `phi-scan: synthetic`, so its later
  versions add no shape finding. The old versions are that file from before the declaration.
- Every one of the 26 blobs is reachable from `refs/remotes/origin/*`, so every one is
  published.
- `tracker_scan`'s blob label carries a **ten-character abbreviated** object id, not the full id.

`tracker_scan` prints no pointer to `harvest_review.py` on any surface. `phi_scan.review_hint`
prints one, a count only, whenever a `corpus-name` finding refuses at commit or in `--all`.

## Ruling 1 — the ledger gains a row kind for a blob finding

`reference/tracker-scan-rulings.json` gains a third row kind, `blob_findings`, carrying the
existing `noise` and `accepted-history` verdicts. `RULING_VERDICTS` stays closed; no verdict value
is added. A `--history` finding that matches a blob row is removed from the graded set exactly as a
matched commit or harvest row is today.

`accepted-history` is the verdict for the case this ledger previously had no answer for: an
occurrence that is published, cannot be edited, and has been read. ADR 0184 ruling 1's remedy for a
real identifier, editing the record so its digest changes, does not reach a blob.

Rejected: counting name and shape findings outside fixture content instead of grading them,
extending ADR 0415 ruling 7's split. A real identifier in old prose would appear as a number rather
than a listed line, and listing it is the reason `--history` exists. Also rejected: declaring
`--history`'s exit 1 a standing limit. The scan would never pass, so a new finding would read like
the old ones.

## Ruling 2 — a blob verdict matches one exact version

A blob row's key is the **full** object id, the line number, the rule and the line digest. That is
the commit row's four-field key with the blob id in place of the commit. The line number belongs in
it for the reason ADR 0184 ruling 3 gives for keeping it on commits: a blob's line numbers are
immutable, so they are part of a finding's identity. The full id belongs in it because the label is
abbreviated, and a key built from the label could match a version nobody read.

One verdict clears one occurrence in one version. It does not carry to the same line in a later
version of the file. The 60 findings therefore need 60 rows, not 23, and no further
rows are expected: the only file still carrying these lines declares itself synthetic.

Rejected: keying on path, rule and line digest so one verdict covers every version of a file. The
path is a label, and ADR 0415 ruling 7 showed a blob can be reachable under several paths, so the
verdict could reach versions nobody read under that name. Also rejected: keying on rule and line
digest alone, which would clear the same line in any file, fixture content included.

## Ruling 3 — every tracker_scan surface points at the harvest review

Wherever `tracker_scan` lists a `corpus-name` finding, on any surface, it prints
`phi_scan.review_hint`'s line, imported rather than copied. The line states a count and never a
string, so the report stays pasteable.

All 373 name findings in history come from unruled harvested strings. Ruling a string vocabulary
through `harvest_review.py` stops it being scanned on every surface at once, while a blob verdict
clears one line. Without the pointer, a reader of a failing `--history` run reaches for the per-line
verdict first. The pointer appears on the harvest and commit surfaces as well as `--history`, because
all three match names from the same harvested list.

## Ruling 4 — an agent may rule a blob the public repository reaches

[ADR 0184](0184-a-harvest-verdict-drops-the-line-number-and-a-clean-harvest-needs-a-denominator.md)
ruling 1 lets an agent read and rule the harvest surface on the ground that it is already-published
public text, and names `--history` blobs as outside that permission. It gives the blob exclusion no
ground of its own, and the harvest ground reaches a blob reachable from the public repository.

An agent may read `--history --show` output and write a blob row, on ruling 1's terms unchanged,
**only for a blob reachable from `refs/remotes/origin/*`**. It writes `noise` only where it can
positively classify the match as non-identifying, and its `reason` names the kind of thing matched
and never the literal. Anything it cannot classify it reports by locator and leaves unruled, which
stays exit 1. A blob reachable only from a local ref has never been published, and reading and
ruling it stay the clinician's.

Rejected: keeping the clinician as the only reader. That leaves 23 distinct lines of mostly
test-string ratios with a human reading. Also rejected: letting an agent read every reachable blob.
A local-only blob is unpublished text, which is outside the ground ADR 0184 ruling 1 rests on.

## Ruling 5 — this is its own record

These rulings concern the verdict ledger, which is ADR 0184's subject rather than ADR 0415's, and
ruling 4 supersedes part of ADR 0184 ruling 1. They are recorded here, ADR 0184 carries the dated
marker, and ADR 0415 carries a dated line pointing here for `--history`'s name and shape route.

## Build checklist

- `tools/tracker_scan.py`: `load_rulings` reads `blob_findings` rows keyed on a full 40-hex object id,
  line, rule and line digest. `partition_ruled_findings` matches a `--history` finding against them
  using the full id of the blob it came from, never the label. Ruled and unmatched-row counts include
  the new kind.
- `tools/tracker_scan.py`: `--draft-verdicts` (ADR 0184 ruling 5) writes blob candidates with blank
  `verdict` and `reason`.
- `tools/tracker_scan.py`: print `phi_scan.review_hint`'s line on every surface that lists a
  `corpus-name` finding.
- `tools/tracker_scan.py`: a `--history --show` report marks whether each blob is reachable from
  `refs/remotes/origin/*`, so an agent can tell which findings it may rule.
- `tools/test_tracker_scan.py`: in a throwaway repository, a blob row clears exactly its finding; the
  same line in a later version stays listed; a row keyed on an abbreviated id is refused as an
  invalid row; an unmatched blob row is counted; the review line appears with a name finding on each
  surface and not without one; a blob reachable only from a local ref is marked unpublished.
- **Coordinate with [#1839](https://github.com/mshamblin5150-code/clinical-skills/issues/1839).** Its
  build of ADR 0415 ruling 7 changes the same `blob_records` and `Record` path. Whichever build lands
  second keeps both: every committed path per blob for ruling 7, and the full id for ruling 2 here.
  `git log --raw` abbreviates object ids unless given `--no-abbrev`, so the history read ruling 7's
  checklist names must pass it, or a blob-to-path join against full ids silently matches nothing.
- `CLAUDE.md`: the *Tracker scan* section states that the ledger takes blob rows and names this
  record instead of copying it.
- `docs/agents/issue-tracker.md`: the *Finding verdicts* section describes the blob row and states
  that an agent may add one only for a blob reachable from the public repository, naming ruling 4.

## Supersedes

- [ADR 0184](0184-a-harvest-verdict-drops-the-line-number-and-a-clean-harvest-needs-a-denominator.md)
  ruling 1, the words "Not the corpus, not `--history` blobs, not any other surface." for a blob
  reachable from the public repository. An agent may read and rule such a blob on ruling 1's own
  terms (ruling 4 here). The corpus and every other surface stay excluded, and a local-only blob
  stays the clinician's.

## What this record does not reach

- **Whether any harvested string is a real name.** That is the clinician's reading through
  `harvest_review.py`, and nothing here moves it.
- **A real identifier in a published blob.** `accepted-history` records that it was read and cannot
  be retracted. Removing it from GitHub is a history rewrite, which nothing here orders.
- **`--commits` and `--paths`.** A commit message already has its row kind, and a path was never a
  file's text. This record adds nothing to either beyond ruling 3's pointer.
- **A blob reachable from no ref**, which `--history` still does not scan.
