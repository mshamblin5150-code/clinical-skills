---
name: aar
description: Run the mandatory after-action review at the terminal step of a scoped clinical skill, classify observed corrections adversarially, and land every correction in a durable destination. Use only when batch-shift, clinical-note, course-assignment, discussion-post, discussion-reply, icd10-cpt, peer-critique, or practicum-case-study reaches a submission.
---

# After-action review

The review asks: **Where was I corrected, and where did I get it right? Then apply the corrections.** It reads observed reversals from the sitting; it does not invent possible mistakes or grade general quality. [ADR 0109](../../docs/adr/0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md) owns the ruling.

The record is private working material. Read it; never paste it. One submission may have several
**Review rounds**. Each round keeps its own record, extract, and baseline; a resumed review adds a
round and preserves every earlier one.

## 1. Fix the population

Choose the submission key from the artifact submitted in this sitting: its dated output stem, response filename, or the run key plus the submission date where no output file exists. Locate the canonical project memory `MEMORY.md`, then run:

Before the extract, write this round's `<run-directory>/aar/<submission-key>.reversal-candidates.md`;
later rounds use `<submission-key>.round-N.reversal-candidates.md`. List one observed reversal per
nonblank line, in your own words describing conduct and quoting no run material, whoever corrected
it: the clinician, an agent or tool, or yourself. Write exactly `none` when there are none.
The required file reaches the reader as one extractor-written entry; its absence refuses both
extract and baseline. A rebuild reads that same round's file and refuses a missing or changed
input; it never borrows a later round's candidates. Earlier extracts retain their historical grade.

```bash
python tools/aar_scan.py <run-directory> --submission <submission-key> --memory-index <MEMORY.md> --extract
```

Before running the command, require the run's `reread.md` to contain exactly one
`## REREAD: <submission-key>` Posted reading. The extractor resolves the skill from the approval
record and runs its completion grader's posted-reading check before fingerprinting that exact
block. A refused check, an undetermined skill, or a missing entry point writes no extract or
baseline. The final grade compares only the newest round's fingerprint with the current block;
earlier rounds keep their own correction grades. Records for other submissions may be appended
without changing this round's fingerprint.

Pass `--transcript <path>` only when the harness exposed the exact current transcript path. The command also reads every other main Claude or Codex transcript that names this run directory and has entries past its own watermark, so an abandoned sitting's corrections enter this round. A drone's transcript is never read as a sitting; its results reach the extract through the main transcript that launched it.

The extract keeps every human turn, assistant text block, subagent result, and tool name and status since the prior watermark. It drops ordinary tool-result bodies. Do not delete, reorder, or narrow its entries. The population is not the orchestrator's to edit. Read the generated `ENTRY-KINDS` legend in the extract; `aar_scan.ENTRY_KINDS` owns that vocabulary and this skill copies none of it. The first round uses `<submission-key>.extract.md`; each later invocation writes a new numbered extract and baseline and never overwrites an earlier round.

Claude system rows are handled by subtype: `aar_scan.READ_SYSTEM_SUBTYPES` owns the read
population and `aar_scan.NAMED_UNREAD_SYSTEM_SUBTYPES` owns the unread reasons. Read rows take
their text from `content` and their label from the same envelope matching as user rows; without
an envelope they are harness notices. A system row never carries the clinician label. Withdrawn
replies that the harness did not store remain outside the reading. `aar_scan.NAMED_UNREAD_TYPES`
owns the other deliberately unread types. An unnamed system subtype, including a missing subtype,
adds to the shared unread remainder and exits 2; a finding still exits 1. `HARNESS-VERSIONS`
continues to read the version on every row, including unread rows.

## 2. Classify adversarially

This **Second reader** under [standing rule 6](../../AGENTS.md) first reads and applies
[sourcing.md](../_shared/reference/sourcing.md), receives only the private extract and the memory
index, and returns:

- every **correction**: a claim asserted, later contradicted, with the contradiction standing;
- the corrector: `clinician`, `agent-or-tool`, or `orchestrator`;
- who was in error, separately, using the same vocabulary;
- one disposition: `skill-file`, `tracker-ticket`, `memory-write`, or `check`;
- a cause pointer for every correction: `shown - <entry>` or `unverified - <entry>`;
- every **sustain**: something the sitting got right that a later sitting could otherwise undo.
- one answer per reversal candidate, numbered by its nonblank line in that round's file: the
  exact entry identifier of the correction it became, `not a correction - <substantive reason>`,
  or `not shown - <substantive reason>` when no extract entry carries the reversal.

Mark a cause `unverified` when it rests on the main agent's or a subagent's explanation of tool
output absent from the extract and no entry from anyone else backs it. Backing may be the
clinician's words, a different subagent's result, or a grader finding relayed through a notification.
The same agent repeating or quoting itself is not independent backing. The clinician's first-hand
account and an agent's account of its own reasoning do not raise this flag. Mark the cause; do not
verify it or widen the extract. A `shown` cause about conduct visible in the extract may land in
any disposition. [ADR 0396](../../docs/adr/0396-a-cause-the-review-s-reader-cannot-see-is-marked-unverified-and-lands-only-on-a-grilling-ticket.md)
owns these distinctions.

For each candidate, find the transcript entry it refers to and re-derive the verdict. Neither a
correction nor a sustain may rest on the candidates entry itself. The departure-list sustain
permission remains unchanged. The reader returns no ticket numbers; ignore any it volunteers.
An orchestrator disagreement with a rejected candidate retains both verdicts and its reason under
the same overrule rule as every other classification.

Name every correction and sustain by one entry, using the identifier exactly as it follows `## ENTRY:`, including any `#` suffix. A correction names the entry holding the contradiction; a sustain names the entry where the right thing was settled. An extract line number or a shortened prefix is never an identifier.

A departure listed under a `GO-AHEAD:` line is the clinician's ruling on it, never an unruled departure.

A preference stated for the first time is not a correction. A correction whose corrector was wrong is supported; identify who was actually in error. The classifier reads the memory index so it can distinguish missing knowledge from knowledge that already existed and went unread.

An entry labeled `prior-review` is a previous classifier's return, not fresh evidence. Re-derive every verdict it contains from the other entries in this extract; do not adopt or exclude it. Retain the task id the classifier's return will carry for `CLASSIFIER-ENTRY` in the record.

The orchestrator verifies the return. It may overrule a classification, but writes both verdicts, who overruled whom, and a substantive reason. It never removes an entry from the fixed population.

Retain the classifier's original cause as `CLASSIFIER-CAUSE` and the final cause as `CAUSE`, separate
from the disposition verdict in `CLASSIFIER`. Both pointers name real entries in this round,
never extractor-written entries such as the candidates list. The only cause overrule is `shown`
to `unverified`, with a substantive `CAUSE-OVERRULE` reason. Never turn `unverified` into `shown`,
including after an orchestrator reads the raw transcript.

## 3. Land every correction

For coursework mechanics corrections, inspect the run's `coursework-mechanics.json`.
Propose confirmed dictionary-hyphenated words for `coursework_mechanics.DICTIONARY_HYPHENATED`
and newly observed variant pairs for its `VARIANTS` table, with the dictionary entry or
Manual section and the observed correction. File the evidence under the landing rules
below; a well-shaped retained handling record alone does not establish the dictionary fact.

`Nothing durable` is not a disposition.

Before filing or citing a `tracker-ticket` or `skill-file` landing, search the tracker's open and
closed issues for the defect. Use `gh issue list --state all --search "<defect>"` or
`gh search issues "<defect>"`. A match receives the landing as an issue comment; otherwise file a
new ticket. The grader requires a successful issue-search command in this round's raw transcripts
before the command result printing the landing address. An absent, failed,
or later search refuses the landing. The adequacy of the search terms remains a reader judgment.

- `memory-write`: update the project memory for a fact about the clinician. File it under
  [memory.md](../../docs/agents/memory.md)'s rule: a `subjects` header naming the subject whose work
  it matters to, or `subjects: none` when it applies in every session.
- `tracker-ticket`: file the tool or workflow defect.
- `skill-file`: a skill instruction is a ruling. File a ticket containing the exact proposed diff and stop; do not edit the skill unattended.
- `check`: add or tighten the mechanical check and its tests.

Land a correction by completing the record for the round that observed it. A later round never
reclassifies the earlier correction and never supplies its landing evidence.

Write every AAR-sourced ticket body first under `<run-directory>/aar/publications/`, then publish it with `gh --body-file`. Require each body to open with `**Filed from:** the after-action review of a <skill> run (<course> <module>), <YYYY-MM-DD>.` The publish hook compares it with the run's own text. Describe conduct; do not reproduce the patient, classmate, preceptor, site, faculty, or board material. A refusal means rewrite the description without the copied span, never move the body file outside the AAR publication directory. A normalized stretch already published on the local `origin/main` reference is exempt, so an exact skill-file diff quoting a published line passes; run-specific stretches remain subject to refusal ([ADR 0305](../../docs/adr/0305-an-aar-quotation-stretch-already-on-main-is-not-run-material.md)).

An unverified cause lands only as `tracker-ticket` or `skill-file`, never `memory-write` or `check`.
Put this exact sentence as the first nonblank line directly under `Filed from:`:

```text
**Cause unverified:** the review's reader could not see the tool output this cause rests on; reread the run's transcript before building on it.
```

Create a new issue with `grilling` and without `ready-for-agent`. A comment on an existing issue
carries the sentence without a label requirement. Retain the body file: the grader reads the file
named by the successful command that printed the exact landing address. An inline body or an
unrecognized command shape refuses. Relative body paths need the recorded command's absolute
working directory or a literal `cd` in that command. The grader never replays a command.
Keep one publication per command result: a multi-command batch sharing output or another shell
executable beside the publication refuses. A literal `cd ... && gh ...` remains recognized.

File a `tracker-ticket` or `skill-file` ticket as soon as its body passes the publish hook; no per-ticket go-ahead is needed, because a ticket records and ADR 0109 ruling 3 applies it unattended. The skill-file diff on that ticket still waits for the clinician's ruling. Never report a review clean while one of its tickets is unfiled.

## 4. Write and grade the record

Write this round's record under `<run-directory>/aar/` at the review-record filename the extract
command printed: for example, key `response-x.md` prints `response-x.md.md` in round one and
`response-x.md.round-2.md` in round two, including a rebuilt round.

For a `clinical-note` or `batch-shift` run, also read its `UPTODATE CONFLICTS` go-ahead block.
For each threshold-sheet conflict UpToDate won, search the tracker for an open ticket naming
that sheet and row before filing. Reuse the existing ticket when present; otherwise file a
sheet-row re-read ticket through the publication route above. Its clinical content names only
the sheet file, row, UpToDate topic title and last-updated date, and what differs. Carry no
encounter detail, identifiers, or shorthand into the search or ticket. Record the reused or
new ticket address in this round's private record. A conflict is evidence requiring a sheet
re-read, not by itself an observed correction to invent for the classifier. This work is owed
even when the correction population is empty (ADR 0347 ruling 6).

Keep every earlier round. Use this shape:

```text
# AFTER-ACTION REVIEW
SUBMISSION: <exact key>
TRANSCRIPTS: <copy from the extract>
POPULATION: <copy from the extract>
UNREAD: 0
WATERMARK: <copy from the extract>
MEMORY-INDEX: <path read by the classifier>
CLASSIFIER: fresh adversarial reader - <identity>
CLASSIFIER-ENTRY: <task id the classifier's return will carry>
DISAGREEMENTS: none recorded
CORRECTIONS: none
SUSTAINS: none

## CANDIDATE: 1
ANSWER: <correction entry identifier, not a correction - substantive reason, or not shown - substantive reason>

## CORRECTION: <extract entry identifier>
CORRECTOR: clinician
IN-ERROR: orchestrator
SUMMARY: <conduct, never working material>
CLASSIFIER-CAUSE: shown - <real extract entry identifier>
CAUSE: shown - <real extract entry identifier>
CLASSIFIER: tracker-ticket - <substantive reason>
ORCHESTRATOR: agree - <substantive reason>
DISPOSITION: tracker-ticket
TARGET: <absolute path for memory-write or check; ticket subject for tracker-ticket or skill-file>
LANDING: <GitHub issue URL or issue-comment URL ending #issuecomment-N printed by the successful gh command for tracker-ticket or skill-file; one line on what changed for memory-write or check>

## SUSTAIN: <extract entry identifier>
SUMMARY: <what was settled correctly and must not be undone>
```

Remove `CORRECTIONS: none` when a correction record exists, and remove `SUSTAINS: none` when a sustain record exists. One correction record may name only one disposition. A summary describes the agent's conduct and never quotes the material it handled.

Several corrections or sustains may rest on one extract entry: repeat the heading with the same identifier, one record per disposition, and never alter an identifier to make records look distinct. For a `memory-write` or a `check`, `TARGET` is the bare absolute path the grader resolves, with nothing after it; put any description in `LANDING` or in a reason.

For `tracker-ticket` and `skill-file`, copy the exact address the successful `gh` command printed.
That output must appear in this round's transcripts at or after its `EXTRACTED-AT`; a different
address, earlier output, failed command, or pull-request address supplies no landing evidence.
Rounds before `aar_scan.LANDING_OUTPUT_CUTOFF` keep their historical evidence rule.

The grader refuses a correction resting on an entry whose text the extractor wrote rather than copied, and it counts every record's corrector against the kind of entry it names without grading that count.
It also refuses an unanswered, duplicate, unknown, or malformed candidate answer and any sustain
resting on the candidates entry. A correction answer must name a correction recorded in this same
round. With `none`, write no candidate-answer blocks. Every report counts the round's candidates,
answers, `not a correction` rejections, and `not shown` answers separately. A `not shown` answer
lands nothing; the candidate's narration cannot become the only evidence for a correction.
Before `aar_scan.REVERSAL_CANDIDATES_CUTOFF` the row is
reported `not graded`.

Every report also prints the unverified cause count once per round, including a rebuilt grade;
the extract summary adds no second count. Rounds extracted before `aar_scan.UNVERIFIED_CAUSE_CUTOFF`
retain their historical cause grade. Unknown extraction moments receive the current cause checks.

When a correction is something an existing memory already said, the memory was missed rather than
missing. Promote it one step under ADR 0391 ruling 6: a memory filed under a subject becomes
`subjects: none`, landed as a `memory-write`; a flat memory becomes a tracked rule, landed through
`skill-file` or `check`.

After this round's memory writes land, rebuild the index and its subject lists, then measure the
index at the extract's `MEMORY-INDEX:` path:

```bash
python tools/memory_index.py <MEMORY.md> --write
python tools/aar_scan.py <run-directory> --submission <submission-key> --measure-memory
```

A rebuild exit 1 names an unplaced memory under `--show`; fix its `subjects` header and rebuild
before measuring, because the measurement records the unplaced count the grade fails on.

The command writes the newest round's `.memory-index.json` beside its review record.
Use `--round <number>` only to remeasure a named earlier round. A measurement refusal stops
grading; repair the unreadable index or extract and measure again. Then run:

```bash
python tools/aar_scan.py <run-directory> --submission <submission-key>
```

Exit 0 means every round's population is drained, every correction has a closed disposition against
its own baseline, and the newest round's Posted-reading fingerprint remains current.
Exit 1 is a finding in any round. Exit 2 means the population was not scanned. The report prints
each round's correction and unlanded counts on every run. `--show` names private findings and must
not be pasted.

Extracts before `aar_scan.SYSTEM_SUBTYPE_CUTOFF` retain their historical grade and report the
system-subtype count as not measured, never as zero. Newer extracts include that count in the
shared unread remainder; exit 0 requires it to be drained.

The memory-index row reads only each round's recorded measurement, never the live index.
It prints lines and characters against the limits in `aar_scan.MEMORY_INDEX_LIMITS` on every grade.
An oversized index or a missing or invalid measurement for a round extracted since
`aar_scan.MEMORY_MEASUREMENT_CUTOFF` fails with exit 1. Compact the index, measure that round again,
then re-run the grade. The same row reports each subject list's line count without grading it and
fails a recorded unplaced memory; a measurement taken before ADR 0391's build carries no placement
counts and reports that count as `not graded`. Earlier rounds without a measurement report `not graded`. A different
Claude Code release in `HARNESS-VERSIONS:` prints a non-failing instruction to re-measure the
limits. Later memory writes do not change the recorded grade of a finished run.

Return to the invoking skill's completion grader only after exit 0. Report correction and sustain counts, or say in two lines that the fixed population held neither; do not turn a zero-correction review into praise.
