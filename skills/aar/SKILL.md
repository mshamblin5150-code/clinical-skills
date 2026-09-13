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

```bash
python tools/aar_scan.py <run-directory> --submission <submission-key> --memory-index <MEMORY.md> --extract
```

Before running the command, require the run's `reread.md` to contain exactly one
`## REREAD: <submission-key>` Posted reading. The extractor fingerprints that exact block.
It refuses a missing or duplicate record, and the final grade fails if the block changes after the
snapshot. Records for other submissions may be appended without changing this round's fingerprint.

Pass `--transcript <path>` only when the harness exposed the exact current transcript path. Otherwise the command selects the newest scoped main transcript that names this run directory. It also consumes every orphan pointer as input, but does not clear one until the finished record grades clean.

The extract keeps every human turn, assistant text block, subagent result, and tool name and status since the prior watermark. It drops ordinary tool-result bodies. Do not delete, reorder, or narrow its entries. The population is not the orchestrator's to edit. Read the generated `ENTRY-KINDS` legend in the extract; `aar_scan.ENTRY_KINDS` owns that vocabulary and this skill copies none of it. The first round uses `<submission-key>.extract.md`; each later invocation writes a new numbered extract and baseline and never overwrites an earlier round.

## 2. Classify adversarially

This **Second reader** under [standing rule 6](../../AGENTS.md) first reads and applies
[sourcing.md](../_shared/reference/sourcing.md), receives only the private extract and the memory
index, and returns:

- every **correction**: a claim asserted, later contradicted, with the contradiction standing;
- the corrector: `clinician`, `agent-or-tool`, or `orchestrator`;
- who was in error, separately, using the same vocabulary;
- one disposition: `skill-file`, `tracker-ticket`, `memory-write`, or `check`;
- every **sustain**: something the sitting got right that a later sitting could otherwise undo.

A preference stated for the first time is not a correction. A correction whose corrector was wrong is supported; identify who was actually in error. The classifier reads the memory index so it can distinguish missing knowledge from knowledge that already existed and went unread.

An entry labeled `prior-review` is a previous classifier's return, not fresh evidence. Re-derive every verdict it contains from the other entries in this extract; do not adopt or exclude it. Retain the extract identifier of this sitting's classifier return for `CLASSIFIER-ENTRY` in the record.

The orchestrator verifies the return. It may overrule a classification, but writes both verdicts, who overruled whom, and a substantive reason. It never removes an entry from the fixed population.

## 3. Land every correction

`Nothing durable` is not a disposition.

- `memory-write`: update the project memory for a fact about the clinician.
- `tracker-ticket`: file the tool or workflow defect.
- `skill-file`: a skill instruction is a ruling. File a ticket containing the exact proposed diff and stop; do not edit the skill unattended.
- `check`: add or tighten the mechanical check and its tests.

Land a correction by completing the record for the round that observed it. A later round never
reclassifies the earlier correction and never supplies its landing evidence.

Write every AAR-sourced ticket body first under `<run-directory>/aar/publications/`, then publish it with `gh --body-file`. Require each body to open with `**Filed from:** the after-action review of a <skill> run (<course> <module>), <YYYY-MM-DD>.` The publish hook compares it with the run's own text. Describe conduct; do not reproduce the patient, classmate, preceptor, site, faculty, or board material. A refusal means rewrite the description without the copied span, never move the body file outside the AAR publication directory.

## 4. Write and grade the record

For the first round, write `<run-directory>/aar/<submission-key>.md`. For a later round, write the
numbered review-record path beside the numbered extract the command produced. Never replace an
earlier round. Use this shape:

```text
# AFTER-ACTION REVIEW
SUBMISSION: <exact key>
TRANSCRIPTS: <copy from the extract>
POPULATION: <copy from the extract>
UNREAD: 0
WATERMARK: <copy from the extract>
MEMORY-INDEX: <path read by the classifier>
CLASSIFIER: fresh adversarial reader - <identity>
CLASSIFIER-ENTRY: <extract identifier that will carry this classifier's return>
DISAGREEMENTS: none recorded
CORRECTIONS: none
SUSTAINS: none

## CORRECTION: <extract entry identifier>
CORRECTOR: clinician
IN-ERROR: orchestrator
SUMMARY: <conduct, never working material>
CLASSIFIER: tracker-ticket - <substantive reason>
ORCHESTRATOR: agree - <substantive reason>
DISPOSITION: tracker-ticket
TARGET: <file, memory path, or tracker subject>
LANDING: <changed path or GitHub issue URL>

## SUSTAIN: <extract entry identifier>
SUMMARY: <what was settled correctly and must not be undone>
```

Remove `CORRECTIONS: none` when a correction record exists, and remove `SUSTAINS: none` when a sustain record exists. One correction record may name only one disposition. A summary describes the agent's conduct and never quotes the material it handled.

Run:

```bash
python tools/aar_scan.py <run-directory> --submission <submission-key>
```

Exit 0 means every round's population is drained, every correction has a closed disposition against
its own baseline, the fingerprints of its Posted readings remain current, and orphan pointers were cleared.
Exit 1 is a finding in any round. Exit 2 means the population was not scanned. The report prints
each round's correction and unlanded counts on every run. `--show` names private findings and must
not be pasted.

Return to the invoking skill's completion grader only after exit 0. Report correction and sustain counts, or say in two lines that the fixed population held neither; do not turn a zero-correction review into praise.
