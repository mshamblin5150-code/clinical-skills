# The run status check covers every posting skill through one approval record

**Measured at:** ba6bc7f002945b34941370bbd343fb61f24f159d

[#1421](https://github.com/mshamblin5150-code/clinical-skills/issues/1421) was filed from the
grilling of [#1398](https://github.com/mshamblin5150-code/clinical-skills/issues/1398), whose
[ADR 0274](0274-a-clinician-upload-completes-through-the-posted-reading-and-a-status-line-ends-every-reply-of-an-approved-run.md)
put an end-of-reply `Run status:` line on an approved `course-assignment` run and left the other
seven skills in `aar_scan.SCOPED_SKILLS` for this ticket. Grilled 2026-09-26 against `main`, where the
freshness gate read `FRESH` after #1398's build merged; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**#1398's check exists and has one row.** `tools/run_status_stop_hook.py` holds `RUN_KINDS` with a
single `course-assignment` entry, recognizes a run by its directory suffix, opens it on
`submission-gates.json`, and declares in `DECLARED_LIMITS` that when several approved runs appear in
one session only the most recently mentioned is graded.

**None of the seven skills writes a durable approval record.** Every go-ahead in `discussion-post`,
`discussion-reply`, `peer-critique`, `clinical-note` and `batch-shift` exists only in the
conversation. `practicum-case-study` writes a dated `GO-AHEAD:` line into its departures file, and no
tool reads it. `icd10-cpt` has no approval of its own: its codes ride inside the approved note and
it performs no portal entry of its own. So under ADR 0274's opener the check had nothing to open on
until after posting.

**What they do write is the far end.** Each skill's posted reading carries a
`SUBMISSION-SHA256` over a defined byte population; for a shift that is the finished `note-N.md`
files concatenated in numeric order (`medatrax_posting.note_paths`), and for a standalone note the
one note file. One grader has a hole the new rule closes: `discussion_post_scan`'s
`_posted_reading_findings` returns no finding when the post carries neither `POST-URL` nor `POSTED`
and no reading exists, so an absent reading is caught there only through the after-action review's
fingerprint.

**The ticket's premise about the note skills was false.** #1421 said `clinical-note`, `batch-shift`
and `icd10-cpt` had not produced a real submission. The clinician has posted with all of them; the
grilling repeated the claim before he corrected it.

**Directory names do not identify the skill.** `discussion-post` and `discussion-reply` share one
`-discussion` run directory, a shift's run directory is a `shift-` prefix, and `clinical-note` names
no run directory pattern for a standalone run. A suffix table cannot open these runs.

## Ruling 1 — an approval record written at the clinician's go-ahead opens the run

Each of six skills writes an **approval record** into its run directory at the go-ahead, through one
shared helper modeled on `assignment_submission`'s record: `discussion-post`, `discussion-reply`,
`peer-critique`, `practicum-case-study`, `clinical-note` and `batch-shift`. Only that record opens the
status-line obligation, and the record, not the directory name, says which skill's row applies.

Using `icd10-cpt` to look up a code writes nothing and opens nothing. When it codes an encounter, its
codes close with the note or shift that carries them, so it has no row of its own.

Opening on the pre-approval review records with an `awaiting approval` status was refused: it puts
the line on every drafting reply. Opening on the first posted reading was refused because it misses
the #1398 failure exactly, an agent saying *posted* before the reading exists. The residue is named:
an agent that never writes the record opens no check in that session, and the skip is caught only by
the terminal grade (ruling 3).

## Ruling 2 — the go-ahead that approves the content writes it, one record per posted item

For `discussion-post`, the first go-ahead (load into the Canvas box) writes the record and the second
(submit after the loaded box is read) updates it, as `confirm` updates `course-assignment`'s. Each
`discussion-reply` reply writes its own record at its own go-ahead. Writing at the final submit
go-ahead was refused because it leaves the load-to-submit gap unchecked; one record per run was
refused because it would cover two separately approved replies with one fingerprint.

## Ruling 3 — the record fingerprints what the posted reading fingerprints, and a mismatch is a finding

The approval record carries the SHA-256 of the same byte population that skill's posted reading
records as `SUBMISSION-SHA256`. For a shift that is the finished notes, not the Review sheet the
clinician reads; for a single note, that note; for the Canvas skills, the posted output. The terminal
grade refuses when the approval and posted-reading fingerprints differ, and an approval record with no
posted reading is a finding in every row. Each skill closes on the grader `aar_scan.COMPLETION_GRADERS`
already pairs with it, run with `--submission`.

Fingerprinting the Review sheet was refused because nothing downstream compares against it, so a note
edited after approval and then entered would pass. Recording both was refused as a fingerprint that
guards nothing.

## Ruling 4 — one status line per touched run, showing its furthest-behind approved item

When a run holds several approved items, its line reports the earliest pending step across them, and
`complete` requires every approved item's terminal grade to be clean. An item never approved does not
hold the run open. When one session touches several approved runs, **each gets its own line naming
its run key**, graded against its own row. This amends ADR 0274 ruling 2's *exactly one line* to
exactly one line per touched run, and retires the built check's *most recently mentioned run is
graded* limit.

A per-item line was refused because it puts classmate names into ordinary replies. A single line for
a whole session was refused because one run's review could hide another run's missing posting. One
run per session was refused as fighting how a shift and coursework are worked together. The run key
names a course and module or a shift date; the check must never put a classmate or patient name in
the line.

## Ruling 5 — `awaiting posting` replaces `awaiting upload`, and the clinician's own route is a clinician posting

The waiting status reads `awaiting posting` for every row, `course-assignment` included. The glossary
defines a **Submission** as the document a course marks and says a reply has none, so `awaiting
submission` was ruled first and reversed in the same session. `posting` is the glossary's word for
putting a contribution on any surface. ADR 0274's **Clinician upload** is renamed **Clinician
posting** in the glossary for the same reason; code identifiers may keep their names.

## Ruling 6 — a clinician posting closes these runs the way ADR 0274 ruling 1 closes a clinician upload

When the clinician posts, enters or uploads an approved item himself and says so, the agent records a
clinician posting in place of its own confirmation and still writes the posted reading from the
surface. The terminal grade accepts either route, and a clinician posting with no approval record
cannot grade clean. What the route gives up is stated: the checks before the submit click (the
second read of the loaded Canvas box, the per-save Medatrax reread and correction) do not run, and a
wrong Medatrax entry is found only after a visit is saved and must not be deleted.

## Ruling 7 — writing the approval record requires a clean pre-posting grade

ADR 0274 ruling 4 applies to every row: the helper refuses to write the approval record unless that
skill's grader, run without `--submission` against the run directory, has no finding. An
incomplete-coverage result is shown to the clinician and does not block, so a grader's unread shape
cannot stop a real shift. Making incomplete coverage block was refused for that reason.

## What this record does not settle

**Whether a status line is true beyond `complete`.** ADR 0274's residue stands for every new row.

**An agent that never writes the approval record.** Ruling 1 names it; nothing in the session catches
it.

**The standalone `clinical-note` run directory's name.** The skill states none; the build names one
under `scratch/runs/` and writes it into the skill.
