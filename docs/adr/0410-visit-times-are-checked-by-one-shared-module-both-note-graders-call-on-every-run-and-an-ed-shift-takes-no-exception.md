# Visit times are checked by one shared module both note graders call on every run and an ED shift takes no exception

**Measured at:** 91f234ebd4b9e41839f5938784f10819449159b9

[#1810](https://github.com/mshamblin5150-code/clinical-skills/issues/1810) was filed from the
after-action review of a `batch-shift` run (NUR5144 ED shift) on 2026-10-14. The coordinator's pass
brief assigned visit lengths of 30 to 90 minutes, against the 15-to-40-minute Times rule in
`skills/clinical-note/SKILL.md`. All eight notes passed every per-pass and shift-wide grader. One
pass noticed the mismatch, and the coordinator re-timed all eight before placement. Grilled
2026-10-18 against `main` at the commit above, where the freshness gate read `FRESH`. The clinician
ruled every point below in that session, one question at a time. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**No tool reads a visit time.** Across `tools/`, start and end times are named only by
`block_scan.py`'s F2 row, which refuses them as a `GAPS` entry, and by `medatrax_posting.py`'s
Time Log line. Nothing compares a note's times with the Times rule or the Shift window.

**The rule carries no setting branch.** `skills/clinical-note/SKILL.md` *Times* assigns each visit
15 to 40 minutes in 5-minute steps, spaces encounters across the shift "rather than stacking them
back to back," keeps every start and end inside the window computed from the run's
`shift-values.json`, and treats a standalone note as a one-encounter batch. Note 1 is the first
patient and each later note follows in order. The clinician ruled the rule authoritative on
2026-08-10.

**The ticket named the wrong completion grader.** `aar_scan.COMPLETION_GRADERS` pairs `batch-shift`
with `filled_vitals_census.py` and `clinical-note` with `differential_scan.py`. Both already call
`medatrax_posting`, whose `note_paths` returns the notes a run posts: `note-N.md` in order for a
batch, the approved or sole note for a standalone run. `block_scan.py` reads every Markdown file in
the run through `run_grader.read_run_artifacts`, so until
[ADR 0406](0406-a-run-grader-sets-aside-named-run-records-and-a-scoped-agreement-read-explains-its-out-of-scope-rows.md)
is built it would read `shift-summary.md`, `delegated-answers.md` and `reread.md` as notes with no
times. No completion step requires `block_scan.py` to run.

**Before approval, a standalone note is often not named at all.** `differential_scan.py` consults
`note_paths` only under `--submission`; with neither that nor `--note`, it reads every Markdown
file through `read_run_artifacts`. Even when consulted, `note_paths` returns no note for a
standalone run carrying a second Markdown file, and `skills/clinical-note/SKILL.md` writes
`delegated-answers.md` beside the note before approval. Batch runs are unaffected: `note_paths`
returns the numbered `note-N.md` files whatever else the run holds.

**Committed notes write the times in several forms.** The fixtures carry a table row
(`| Start time | 10:25, estimated |`), a colon line (`Start time:   09:20, estimated`), four digits
with no colon (`Start time   1105, estimated`), and a tier-block restatement
(`Start 15:05, End 15:40, both estimated`). The skill prescribes no single line form.

**Both graders already run before the go-ahead.** `skills/batch-shift/SKILL.md` step 6 runs
`filled_vitals_census.py` before the Review sheet and blocks the sheet on a BMI finding; its final
`--submission` pass runs after posting. `clinical-note`'s drift walk runs `differential_scan.py`
before the go-ahead, and its completion pass runs after posting.

## Ruling 1 — an ED shift takes no exception

Every shift follows the Times rule as written. The times are estimates for the Medatrax entry, not
a record of how long a patient stayed, and the rule names no setting. An ED exception allowing
longer or overlapping visits was declined because it needs new clinical limits with nothing in the
corpus to ground them, and it would stop Visit Time matching the program's expected pace. Reporting
ED runs separately with no rule behind the report was declined because it informs nothing.

## Ruling 2 — the check enforces the rule as written and nothing more

Each `Start time` / `End time` pair spans 15 to 40 minutes in a multiple of 5. In note order, each
visit starts at least one 5-minute step after the previous visit ends, so neither overlap nor
touching visits pass; that is the mechanical form of "rather than stacking them back to back."
Note 1 may start at the shift start. Every start and end falls inside the Shift window, inclusive
at both ends. A night shift crosses midnight, so times are measured from the shift start rather
than compared as clock readings.

The clinician gave an average of about 10 minutes to triage a patient as background, and ruled that
it changes nothing: neither the skill text nor the check gains a 10-minute gap or a first-visit
offset. A check stricter than the skill was declined because a run following the skill exactly
could fail with no line to point to. Whether visits are spread evenly across the whole window was
declined as a row because it needs a threshold nobody has ruled; it stays a reading.

## Ruling 3 — the check reads the Medatrax field lines in the forms runs already write

The check reads the `Start time` and `End time` field lines of the note's Medatrax entry, as
`HH:MM` or four-digit `HHMM`. A line carrying either label that the strict reader cannot read
enters the shared unread remainder (ADR 0230), so the run reports not fully checked rather than
clean. The tier-block restatement is not read. Prescribing one exact line form was declined because
the clinician declined any change to the skill text. Requiring the restatement to agree was
declined because it has no fixed shape and would add stops to catch a disagreement nobody has seen.

## Ruling 4 — one shared module, called by both completion graders on the posted notes

A new shared times module owns the rule and its reader. `filled_vitals_census.py` (batch-shift)
and `differential_scan.py` (standalone clinical-note) both call it. The module resolves its own
population on every invocation, independent of the grader's scan population: the note named by
`differential_scan.py`'s existing `--note` option, else `medatrax_posting.note_paths`. Reading only posted notes keeps the row clear of ADR 0406's
run-record trap, so this build does not wait on that one. Covering standalone notes closes the same
defect one skill over. A batch-only row in `filled_vitals_census.py` was declined because a
standalone note enters Medatrax the same way. A row in `block_scan.py` was declined because nothing
requires it to run and it reads run records as notes.

## Ruling 5 — the row runs on every invocation

The times row runs whenever either grader runs. A finding before the Review sheet blocks the sheet
until the notes are re-timed, as a BMI finding does today, and blocks the standalone go-ahead the
same way. The final `--submission` pass checks again. Running only at completion was declined
because wrong times would already be in Medatrax before anything objected.

## Ruling 6 — missing shift values leave the window test not checked

When `shift-values.json` is absent, unreadable, or carries a null `start` or `duration`, the row
still runs the duration, step and spacing tests, which need only the notes. It reports the window
test as not checked, names the remedy of recording the shift values, and counts the run as
incomplete coverage (exit 2). A confirmed finding from the other tests outranks that and exits 1.
Calling a missing file a finding was declined because the check cannot tell a run that never asked
from a file saved in the wrong place. Skipping the window test silently was declined because it
presents a partial read as clean. `reference/completion-check-starts.tsv` grades the new row only
from its start date, so no earlier shift is regraded against it.

## Build checklist

- A shared times module with a direct command: the four tests (ruling 2), the field-line reader and
  its unread remainder (ruling 3), the shift-values handling (ruling 6), counts-only default output
  with a private `--show`, and a `DECLARED_LIMITS` object carrying this record's limits below.
- `filled_vitals_census.py` and `differential_scan.py`: call the module on every invocation over the
  posted-note population (rulings 4 and 5); a finding sets exit 1 and unread or missing shift values
  set exit 2, with 1 winning. Where `differential_scan.py` has no `--note` and `note_paths`
  resolves no note, the times row reports not checked (exit 2) and never falls back to the
  run-record read; `skills/clinical-note/SKILL.md`'s drift walk passes `--note`.
- One `unread remainder N` line per run
  ([#1740](https://github.com/mshamblin5150-code/clinical-skills/issues/1740)): the times count
  folds into `filled_vitals_census.py`'s existing line, and `differential_scan.py`, which prints
  none today, gains exactly one, held by its test.
- `shift-values.json` is a hand-written run record, so its read goes through
  [ADR 0395](0395-a-hand-written-run-record-is-read-through-one-shared-reader-that-refuses-a-control-character-by-line-or-field.md)'s
  shared reader ([#1755](https://github.com/mshamblin5150-code/clinical-skills/issues/1755))
  once built. A control character there is that record's damaged-text finding; ruling 6 above
  governs only an absent file, an unparseable one, or a null field.
- `reference/completion-check-starts.tsv`: the new row's start date.
- `skills/batch-shift/SKILL.md` step 6 and `skills/clinical-note/SKILL.md`'s drift walk: state that
  a times finding blocks the Review sheet or the go-ahead. The *Times* rule text is unchanged.
- `CLAUDE.md` maintainer tooling: name the module and point to its limits object.
- Tests through each public command: a 30-to-90-minute shift like the one that filed this ticket is
  refused; a 45-minute visit, a 22-minute visit, an overlap and touching visits are each refused; a
  visit outside the window is refused; a night shift crossing midnight passes; an unreadable labeled
  line is unread, not clean; missing shift values leave the window test not checked while a spacing
  finding still exits 1; a clean shift passes.

## What this record does not reach

- **Whether a visit's length suits its complexity.** The rule assigns lengths by complexity; the
  check reads only the 15-to-40 range and the step, so the assignment stays a reading.
- **Whether visits are spread across the whole shift.** Only touching and overlap are refused.
- **Whether the times entered in the portal match the note.** No tool compares them. The posted
  reading's `VISIT` lines carry no visit times (`medatrax_posting.DECLARED_LIMITS`), and the
  per-run Medatrax fill builder that types them is
  [#1882](https://github.com/mshamblin5150-code/clinical-skills/issues/1882)'s scope.
- **A time written without its field label.** A line the reader cannot recognize as a `Start time`
  or `End time` field is neither graded nor counted as unread.
