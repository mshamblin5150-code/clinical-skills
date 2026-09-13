# An UpToDate entry is checked against its masthead and a sourced record is cited or dropped

Out of [#1021](https://github.com/mshamblin5150-code/clinical-skills/issues/1021), grilled on
2026-09-13 at `main` `3e3a2cdb`; the clinician ruled every point below the same day. Nothing is
built here; this is the record the build reads.

#1021 was filed by the after-action review of one `practicum-case-study` run. Two defects reached a
graded draft while every command exited 0: a reference entry for an UpToDate topic carried an
invented author surname, and the body argued from a 2026 guideline update that it neither cited nor
listed, although the run's claim ledger held a `sourced` record for that work.

## Measured before ruling

**The stored topic already carries what the author check needs.** `tools/uptodate_store.py` ingest
writes each topic's `authors` string and `last_updated` date into its per-dump manifest, and
manifest validation refuses a topic missing either. `tools/research_ledger.py` already joins every
cited UpToDate title to that accumulated manifest (`cited_uptodate_entries`, `evidence_findings`).
So the check is one more comparison at an existing join, and no dump is parsed again.

**`reference_scan` is the wrong home.** Its limits say the companion evidence is a document it never
sees, and it assigns source authenticity to `research_ledger`.

**A last-word surname rule fails a correct entry.** A subagent read the private store's manifests and
the UpToDate-shaped entries in retained ledgers and drafts. Masthead names are written given name
first, joined by spaces, each followed by a comma and degrees; APA entries are written surname first.
At least one correct entry carries a two-word surname, which a rule taking the masthead name's last
word as the surname splits wrongly. Every other count that pass reported stays out of this record:
it was measured against `scratch/` and nothing committed re-derives it.

**The only citation-to-record matching in the tree is the discussion-post grader's.** It keys on the
author-and-year citation key read from each record's `REFERENCE`, and it counts an unspent record
without grading it. `research_ledger` uses none of that machinery today.

**The skill already defines which records a draft relies on.** `practicum-case-study` step 3 writes a
record for each claim the document will rest on. A `sourced` record is drafted from, an `unsourced`
one goes to the `PROPOSED` block, and a `refuted` one is never drafted from. No ledger field records
a claim cut from the draft after its research.

## Ruled 2026-09-13

### 1. Both checks live in `research_ledger`

The author and year check and the ledger-to-list check are rows of `tools/research_ledger.py`, where
the ledger, the draft and the UpToDate store are already read together. `tools/reference_scan.py`
gains nothing.

### 2. An UpToDate entry's authors and year are checked against its stored topic

For every cited UpToDate entry whose topic the accumulated manifest holds, the command compares the
entry with the stored row and fails the run on a mismatch:

- **Authors.** The entry and the masthead list the same number of authors in the same order, and
  each surname the entry writes equals the trailing words of the masthead name in the same position.
  The entry's surname decides the split, so a multi-word surname matches. Initials are not compared.
- **Year.** The entry's year equals the year of the stored `last_updated` date.

The check runs where the membership join already runs, under `--evidence`, and takes that row's gate:
where [ADR 0212](0212-the-evidence-row-grades-only-an-ingested-file-and-an-untitled-dump-is-filed-as-a-titled-copy.md)
ruling 1 leaves the membership row `not graded` because the named file is not in the store, this row
prints `not graded` too. A cited topic the store does not hold is already refused by the membership
row, so it is not a second finding here.

A titled copy's titles are declared rather than graded (ADR 0212 ruling 5), and this row joins on
them. A block given the wrong title is compared against the wrong masthead, so the row reports an
author or year mismatch on that topic: a finding that points at the title as well as at the entry.

### 3. What stays outside the check is declared, not silent

`research_ledger.DECLARED_LIMITS` gains rows saying that initials are not compared, that an entry
shortening a real surname to its trailing words passes, and that authors and years of non-UpToDate
sources are not checked by this command. The clinician holds an UpToDate account and the dump holds
each topic whole, so for an UpToDate source nothing is out of reach; for other sources the refutation
agent verifies authors, years and content through the Authenticated route. Whether a source says what
the sentence citing it says stays a reading.

`practicum-case-study`'s statement that whether an UpToDate year is the topic's revision year needs a
document no command sees narrows accordingly: `reference_scan` still cannot see it, and
`research_ledger` now grades it.

### 4. A sourced record's source reaches the reference list, or the record says it was dropped

Whenever `--draft` is given, with or without `--evidence`, every `sourced` claim record's source must
appear in the draft's reference list, or the run fails. The draft's reference list is therefore read
outside the `--evidence` branch; #1052 retired the cost that move once carried.

A record may carry a new field, `DROPPED: <why the draft no longer makes this claim>`. With it, the
source's absence from the list is correct. The field is what makes a record a **Dropped record**:

- `DROPPED` with no reason after it is a finding.
- `DROPPED` on a record whose `STATUS` is not `sourced` is a finding.
- A `DROPPED` record whose source still appears in the list is not a finding, because another record
  may rest on the same source.

### 5. A record's source is in the list when key and title both agree

A reference-list entry carries a record's source when the entry and the record's `REFERENCE` produce
the same citation key, normalized author phrase and year with any letter suffix ignored, and the same
normalized title. Neither alone is enough: the key alone lets one entry satisfy two works by the same
authors in the same year, which `apa7.md` §2 calls ordinary for UpToDate, and the full reference text
breaks on ordinary APA edits between research and the final list, such as italics, a retrieval date
or an added DOI.

## Rejected options

**Leave author accuracy to the refutation agent alone.** #1021's decision 1 asked whether an
UpToDate-only ceiling was a reason not to build. Refused: the fabrication the run shipped was on an
UpToDate entry, and it was caught only by a discretionary pass.

**Check authors only and file the year separately.** The year sits in the same stored row, behind the
same join, for the same entry. Splitting it would build a second pass over topics already read.

**Delete a record when the draft drops its claim.** Keeps the check without a new field, and destroys
the record of research that was done.

**Report unmatched sourced records as a count.** A count nobody must act on is a clean exit with a
number beside it, which is how the run's uncited guideline got through.

**Take the masthead name's last word as the surname.** Simpler, and fails a correct entry with a
multi-word surname.

**Compare initials too.** APA initials for compound and hyphenated given names vary, so a correct
entry can fail.

## What none of this reaches

- A fabricated author on a source other than an UpToDate topic the store holds.
- Whether a `DROPPED` reason is true, or whether the draft in fact still makes the claim.
- A relied-on work that has no claim record at all.
