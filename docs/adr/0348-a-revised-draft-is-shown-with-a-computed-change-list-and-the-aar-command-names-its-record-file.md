# A revised draft is shown with a computed change list and the AAR command names its record file

**Measured at:** ab5fb84924475f9ed161233f6cb36bb2e2b66cb0

[#1560](https://github.com/mshamblin5150-code/clinical-skills/issues/1560) was filed from the
after-action review of a `discussion-reply` run (NUR 5042 Module 9) on 2026-10-04. Two things went
wrong in that run. The clinician asked for one paragraph of a reply draft to be reworked; the
revision was shown with an account naming the phrase he had questioned, and it had also dropped the
paragraph's closing sentence, which he found himself. Separately, the after-action review record
was written under a name the grader did not read. Grilled 2026-10-12 against `main` at `d5284f5a`,
where the freshness gate read `FRESH`. `main` then advanced to `ab5fb849`, adding ADR 0347 and the
ADR 0345 build. Neither changes `tools/aar_scan.py` or the go-ahead of the four skills ruled here
(ADR 0347 rules go-ahead lines for `clinical-note` and `batch-shift`, which ruling 2 leaves out),
and every claim below was checked against that tree. The clinician ruled each point below in that session. **Nothing is built
here; this is the record the build reads.**

## Measured before ruling

**Two built rulings border the first limb and neither closes it.**
[ADR 0318](0318-rendered-pages-waits-for-a-load-and-an-approval-needs-the-whole-text-shown.md)
rulings 3 and 4 are on `main`: every approval ask in `discussion-post`, `discussion-reply` and
`peer-critique` shows the complete text, and `approval_record.verify_shown_text` refuses a first
approval of a fingerprint whose blocks were not in the agent's messages. So a silently dropped
sentence is now in front of the clinician inside the whole revised text, but nothing names it.
[ADR 0330](0330-a-reader-remark-is-shown-at-the-go-ahead-and-waived-only-by-name.md) ruling 2 makes
each reader remark say what was changed for it, which is the agent's own account of one fix.

**The case study has a leftovers reader, not a change account.** `skills/practicum-case-study/SKILL.md`
carries every change after the first draft to each section that restates it, then has a reader that
did not make the changes look for remnants of the old version. It finds stale text left behind; it
does not report a sentence that was removed.

**The clinical skills already have a computed comparison.** `tools/artifact_repairs.py`'s `compare`
route retains before and after copies of a placed note or worksheet and refuses a change outside the
declared scope. Its kinds are `note` and `worksheet` only.

**The record path is correct and derived by eye.** `aar_scan.review_path` keeps the submission key
verbatim, so `review_path(Path("run"), "response-x.md")` is `run\aar\response-x.md.md`, beside
`response-x.md.extract.md`; a later round is `response-x.md.round-2.md`. The extract route already
prints the extract's own filename (`private extract written`) and never the record's. A
`missing-review` finding carries the submission key, not the filename it looked for. Across the 171
registered checkouts, nine files under a run's `aar/` directory carry the doubled `.md.md` name;
under today's rule they are the correct records. Counts only; no file was opened.

## Ruling 1 — the change list is computed, not recalled

When a revised draft is shown to the clinician, a command compares the version shown with the
version he last saw, sentence by sentence, and prints every added, removed and reworded sentence.
The agent shows that printed list verbatim with the revision.

A written rule alone was declined because a skipped account is the defect the ticket records. Having
`approval_record.approve` refuse a re-ask whose change list was not shown was declined: the earlier
copy would have to survive to approval, a reformatted list would become a false refusal, and the
refusal would act only at the ask, while ADR 0318 ruling 4 already puts the whole revised text in
front of him there. A skipped command is an after-action review correction like any other.

## Ruling 2 — four skills: the three chat-approved text skills and the case study

The rule applies to `discussion-reply`, `discussion-post`, `peer-critique` and
`practicum-case-study`. All four draft Markdown, so one command reads all of them.

`course-assignment` is out: its artifact is a deck or a Word document reviewed as rendered page
images, and the command would need slide and paragraph extraction for an artifact the clinician
already reads page by page. `clinical-note` and `batch-shift` are out because the repair chain
already compares every change after placement. The three text skills alone was declined because the
case study's revisions are the longest and its leftovers reader does not catch a removal.

## Ruling 3 — one shared sheet, pointed to from each skill

The procedure lives in a new `skills/_shared/reference/revisions.md`, and each of the four skills
points to it in one line at the place it shows a draft to the clinician.

A sentence restated in each skill was declined because the procedure carries steps and a command
line, and four copies drift. A section of `sourcing.md` or `style.md` was declined because neither
is about revisions and a reader looking for this would not open them. This follows ADR 0330's shape
for its go-ahead procedure.

## Ruling 4 — the comparison is against the version the clinician last saw

The first showing of a draft has nothing to compare and needs no list. Every later showing lists
everything that changed since the version the clinician last saw, whoever caused it: a change he
asked for, a reader's repair, or the agent's own edit. One copy is kept each time a draft is shown,
not one per edit.

Only revisions he asked for was declined because a repair he did not ask for can drop a sentence
just as silently, and ADR 0330's remark account is the agent's self-report of one fix.

## Ruling 5 — the AAR command prints the record filename it will grade

The extract route prints the review-record filename it will grade, on its own line beside the
extract filename it already prints, for the first round and for a rebuilt or later round. A
`missing-review` finding names that expected filename. `skills/aar/SKILL.md` section 4 tells the
agent to write the record at the filename the command printed. The doubled name stays: a key ending
in `.md` gives a record ending in `.md.md`.

A clarifying clause alone, as the ticket filed it, was declined because it leaves the filename
derived by eye, which is how it went wrong. Removing the key's extension, as
[ADR 0345](0345-a-submission-s-voice-read-records-live-under-its-key-stem-and-one-function-names-the-directory.md)
did for voice-read folders, was declined: the nine existing records and their extract and baseline
files would grade as missing unless renamed under `scratch/`, which is the clinician's word per file,
or both spellings were accepted, which ADR 0345 refused. Printing the name exposes nothing new,
because the extract filename already printed carries the same key.

## Build checklist

- A new stdlib command (for example `tools/change_list.py <shown-before> <shown-now>`) reads both
  Markdown versions through `docx_write.blocks`, splits blocks into sentences with reference entries
  kept whole, collapses whitespace, and compares the two sentence sequences in order. It prints each
  added and removed sentence, and each reworded sentence as its before and after pair. A sentence
  moved without rewording appears as removed in one place and added in another. Identical versions
  print one line saying no sentence changed. Exit 0 when it printed a list, 2 when either file is
  unreadable. It calls `use_utf8()` and `require_python_floor()` on its command path. Its output is
  draft text and is private working material.
- The command declares its boundary in a module-level `DECLARED_LIMITS`, including that the
  reworded pairing is a positional heuristic: a reworded sentence may be listed as one removal and
  one addition, which keeps the list complete.
- `skills/_shared/reference/revisions.md`: keep a copy of each version shown to the clinician under
  a `revisions/<key stem>/` subdirectory of the run, using the stem `coursework_run`'s
  `voice_records_directory` computes, and never at the run root, where
  `discussion_reply_scan` reads every `response-*.md` as a reply. Run the command against the
  last-seen copy before showing a revision, show its output verbatim with the revision, and skip it
  on the first showing. A test proves a kept copy does not enter any of the four skills' graders.
- `skills/discussion-reply/SKILL.md` step 4, `skills/discussion-post/SKILL.md` at Gate 1,
  `skills/peer-critique/SKILL.md` at its go-ahead, and `skills/practicum-case-study/SKILL.md` at its
  revision paragraph: one line pointing to that sheet. The reply edit sits in the same step 4
  go-ahead ADR 0330 edited.
- `AGENTS.md`: names `tools/change_list.py` as a **Required command** for the four skills, because
  it produces the change list a revision is shown with; without its run the list is not computed.
  `python_floor`'s skill-command scan refuses a command a skill file hands consumers unnamed.
- `tools/aar_scan.py`: the extract route's output gains the review-record filename line; a
  `missing-review` finding names the expected filename. The finding kind stays `missing-review`;
  only its detail changes, so a dated start-row table keyed by finding kind, if one has landed,
  needs no new row.
- `skills/aar/SKILL.md` section 4: the first sentence tells the agent to write the record at the
  filename the extract command printed, with the `.md.md` example.
- Tests: the command lists a dropped closing sentence, an added sentence, a reworded pair and a
  moved sentence, ignores a whitespace-only change, reports an unchanged draft, and exits 2 on an
  unreadable file; the four skills point to the sheet; the extract output for `response-x.md` names
  `response-x.md.md` and a round-two name; a `missing-review` finding names the expected file.

## What this record does not reach

- **Whether the command was run.** Nothing refuses a revision shown without a change list.
- **Whether the clinician read the list.** The list is shown; reading it stays his.
- **Changes the comparison cannot see.** A change that leaves the sentence text identical, such as
  formatting the Markdown splitter discards, is not listed.
- **`course-assignment`, `clinical-note` and `batch-shift`.** Ruling 2 leaves them on their own
  review routes.
- **The existing records' names.** Ruling 5 renames nothing; whether a record's content is right is
  still the grader's existing rows.
