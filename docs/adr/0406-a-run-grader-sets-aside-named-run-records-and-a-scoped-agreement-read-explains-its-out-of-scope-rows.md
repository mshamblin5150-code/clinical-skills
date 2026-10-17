# A run grader sets aside named run records and a scoped agreement read explains its out-of-scope rows

**Measured at:** 4dbf0795b56f31864d63103bb4a9584bcf6ee9ae

[#1805](https://github.com/mshamblin5150-code/clinical-skills/issues/1805) was filed from the
after-action review of a `batch-shift` run (NUR5144 clinic shift) on 2026-10-14. It reported two
grader population traps. Comments added two more shifts that hit the first trap, the same trap in
`differential_scan.py`, and a coordination note for
[ADR 0404](0404-an-ambiguous-answer-is-read-back-and-earlier-care-status-is-asked-at-the-first-stop.md)
ruling 7. Grilled 2026-10-17 against `main` at the commit above, where the freshness gate read
`FRESH`. The clinician ruled every point below in that session, one question at a time. **Nothing
is built here; this is the record the build reads.**

## Measured before ruling

**The shared reader counts every top-level Markdown file except README.**
`run_grader.read_run_artifacts` is the note or worksheet population for `anchor_scan.py`,
`block_scan.py`, `differential_scan.py`, `refusal_scan.py`, `specificity_scan.py` and the fallback
of `filled_vitals_census.py`. A copy of `fixtures/filled-anchor/notes` read 12 notes and exited 0
under `block_scan.py`. With a one-line `shift-summary.md` and `delegated-answers.md` added, it read
14 notes, reported unread remainder 2, and exited 2.

**The run itself writes three records beside its notes.** `skills/batch-shift/SKILL.md` writes
`shift-summary.md` at the top level, where `shift_summary.py` and `filled_vitals_census.py` read
it. `skills/clinical-note/SKILL.md` writes `delegated-answers.md` for a delegated run, where
`delegated_answers.py` reads it. Both note skills write `reread.md` after posting. The ticket named
the first two; `reread.md` is the third.

**Two private copies of an exclusion set already exist, and they disagree with the record list.**
`medatrax_posting.note_paths` and the summary-path fallback in `filled_vitals_census.grade` each
exclude `readme.md`, `reread.md` and `shift-summary.md`. Neither excludes `delegated-answers.md`.

**The agreement read uses a third reader.** `anchor_scan._markdown_files` pairs notes and
worksheets by stem and excludes only README, so the run records arrive as unpaired notes there.

**Preserved run records do not use the `note-N.md` name.** The committed fixtures name notes
`case-01.md`, `day-b-case-02.md` and similar, and a preserved run record is never edited or
renamed to pass a grader.

**The written single-note route already pairs `--stem` with that note's own record.** Since
2026-10-08, `batch-shift` step 5, `clinical-note` and `icd10-cpt` pair `--stem <stem>` with
`agreement-self/<stem>.json`. The trap came from improvised repair briefs that paired one stem with
the shift-wide second-reader record. `anchor_scan` adds every record row whose stem is outside the
requested set to the unread remainder, so that pairing exits 2 on every input.

## Ruling 1 — a run grader sets aside named run records

The shared run reader excludes one declared list of run records: `README`, `shift-summary`,
`delegated-answers` and `reread`. Every other top-level Markdown file is still read as a note,
whatever its name. Each report names the files it set aside; the names come from the grader's own
list and draw nothing from the run, so the report stays pasteable. `anchor_scan._markdown_files`
and the two private sets above use the same list. `filled_vitals_census.py` keeps its existing
preference for the `note-N.md` posting population; this record leaves that choice unchanged.

Reading only `note-N.md` was declined because every preserved run record and earlier run would read
zero notes, and a renamed preserved record is forbidden. Reading only `note-N.md` when one is
present was declined because a misnamed note in a new run would drop out silently while the run
still reads as clean. Moving run records into a subdirectory was declined because it changes four
documents' paths and leaves the trap in every run already on disk. A declared list fails toward
counting an unlisted record as a note, which shows as a wrong count or an exit 2 and never drops a
note.

## Ruling 2 — an inventory test keeps the list in step with the skills

A test collects every backticked bare `name.md` in `skills/batch-shift/SKILL.md`,
`skills/clinical-note/` and `skills/icd10-cpt/SKILL.md`. Each must match the `note-N.md` shape, be
on ruling 1's list, or be on a declared list of names that are not run files, today `coverage.md`
and `project-context.md`. A new name fails the suite until it is classified. A one-way test that only
checks listed names still appear, and a declared limit alone, were declined because neither catches
a new run record, which is the failure the ticket's own enumeration showed.

## Ruling 3 — a scoped agreement read explains its out-of-scope rows

When `--stem` is given and the agreement record holds rows for stems outside the request,
`anchor_scan.py --agreement-read` reports those rows on their own labeled line. It keeps them in the
unread remainder, so the exit status stays 2, and the report says a scoped read takes that stem's
own self-record. `skills/batch-shift/SKILL.md` step 5 gains one sentence: a repair pass re-runs the
step 5 self-grade command against its own self-record, never the shift-wide record. A scoped mode
that leaves those rows out of the remainder was declined because a repaired note would be graded
against a reader record written for its earlier text, so a clean exit could be coincidence. A skill
sentence alone was declined because the next improvised brief would meet the same unexplained exit 2.

## Ruling 4 — a full-shift grade establishes what it did before

None of the rulings changes what a full-shift grade establishes.

## Coordination

ADR 0404 ruling 7 leaves its rapid-screen check's host to the build. Hosted on a run grader, it
inherits ruling 1 through the shared reader. Hosted on a command taking explicit note paths, like
`tools/exam_scheme.py`, the trap does not reach it. The order of the two builds does not matter.

## Build checklist

- `tools/run_grader.py`: the declared run-record list, applied in `read_run_artifacts`, with the
  set-aside names available to every member's report (ruling 1).
- `tools/anchor_scan.py` `_markdown_files`, `tools/medatrax_posting.py` `note_paths` and the
  summary-path fallback in `tools/filled_vitals_census.py` read that list instead of their own sets.
- A test over a run carrying notes, `shift-summary.md`, `delegated-answers.md` and `reread.md`,
  through each member's public command: the note count is unchanged and the set-aside names print.
- The inventory test (ruling 2), and a `DECLARED_LIMITS` row naming its backtick boundary.
- `tools/anchor_scan.py --agreement-read`: the out-of-scope row line and its message, with a test
  over a scoped read against a two-stem record (ruling 3).
- `skills/batch-shift/SKILL.md` step 5: the repair-pass sentence (ruling 3).

## What this record does not reach

- **A run record named without backticks in a skill.** Ruling 2's test reads backticked names only.
- **A run record the skills never name.** A file an agent writes on its own initiative is read as a
  note until someone lists it; the miscount shows, but nothing classifies it.
- **A misnamed note under the `note-N.md` posting population.** `filled_vitals_census.py` and the
  posting fingerprint keep their name-derived populations, which this record does not change.
