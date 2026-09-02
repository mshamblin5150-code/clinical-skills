---
name: aar
description: Run the mandatory after-action review at the terminal step of a scoped clinical skill, classify observed corrections adversarially, and land every correction in a durable destination. Use only when batch-shift, clinical-note, course-assignment, discussion-post, discussion-reply, icd10-cpt, or practicum-case-study reaches a submission.
---

# After-action review

The review asks: **Where was I corrected, and where did I get it right? Then apply the corrections.** It reads observed reversals from the sitting; it does not invent possible mistakes or grade general quality. [ADR 0109](../../docs/adr/0109-the-after-action-review-s-signal-is-an-observed-correction-and-its-findings-land-or-the-run-is-not-done.md) owns the ruling.

The record is private working material. Read it; never paste it. One record belongs to one submission, even when several sittings share a run directory. A resumed run accumulates records.

## 1. Fix the population

Choose the submission key from the artifact submitted in this sitting: its dated output stem, response filename, or the run key plus the submission date where no output file exists. Locate the canonical project memory `MEMORY.md`, then run:

```bash
python tools/aar_scan.py <run-directory> --submission <submission-key> --memory-index <MEMORY.md> --extract
```

Pass `--transcript <path>` only when the harness exposed the exact current transcript path. Otherwise the command selects the newest scoped main transcript that names this run directory. It also consumes every orphan pointer as input, but does not clear one until the finished record grades clean.

The extract keeps every human turn, assistant text block, subagent result, and tool name and status since the prior watermark. It drops ordinary tool-result bodies. Do not delete, reorder, or narrow its entries. The population is not the orchestrator's to edit.

## 2. Classify in a fresh adversarial context

Give a fresh non-authoring context only the private extract and the memory index. The classifier returns:

- every **correction**: a claim asserted, later contradicted, with the contradiction standing;
- the corrector: `clinician`, `agent-or-tool`, or `orchestrator`;
- who was in error, separately, using the same vocabulary;
- one disposition: `skill-file`, `tracker-ticket`, `memory-write`, or `check`;
- every **sustain**: something the sitting got right that a later sitting could otherwise undo.

A preference stated for the first time is not a correction. A correction whose corrector was wrong is supported; identify who was actually in error. The classifier reads the memory index so it can distinguish missing knowledge from knowledge that already existed and went unread.

The orchestrator verifies the return. It may overrule a classification, but writes both verdicts, who overruled whom, and a substantive reason. It never removes an entry from the fixed population.

## 3. Land every correction

`Nothing durable` is not a disposition.

- `memory-write`: update the project memory for a fact about the clinician.
- `tracker-ticket`: file the tool or workflow defect.
- `skill-file`: a skill instruction is a ruling. File a ticket containing the exact proposed diff and stop; do not edit the skill unattended.
- `check`: add or tighten the mechanical check and its tests.

Write every AAR-sourced ticket body first under `<run-directory>/aar/publications/`, then publish it with `gh --body-file`. The publish hook compares it with the run's own text. Describe conduct; do not reproduce the patient, classmate, preceptor, site, faculty, or board material. A refusal means rewrite the description without the copied span, never move the body file outside the AAR publication directory.

## 4. Write and grade the record

Write `<run-directory>/aar/<submission-key>.md` in this shape:

```text
# AFTER-ACTION REVIEW
SUBMISSION: <exact key>
TRANSCRIPTS: <copy from the extract>
POPULATION: <copy from the extract>
UNREAD: 0
WATERMARK: <copy from the extract>
MEMORY-INDEX: <path read by the classifier>
CLASSIFIER: fresh adversarial reader - <identity>
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

Exit 0 means the population is drained, every correction has a closed disposition, the landing evidence is present, and orphan pointers were cleared. Exit 1 is a finding. Exit 2 means the population was not scanned. `--show` names private findings and must not be pasted.

Return to the invoking skill's completion grader only after exit 0. Report correction and sustain counts, or say in two lines that the fixed population held neither; do not turn a zero-correction review into praise.
