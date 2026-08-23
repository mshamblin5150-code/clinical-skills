# `output/` holds only the submission, and everything a run produced about it lives in the run directory

[ADR 0014](0014-a-run-is-keyed-to-the-graded-artifact.md) settled the run key and stated a *layout*: `claims.md`, `checks.md` and `evidence.txt` under `scratch/runs/<key>/`, the submission under `output/<kind>/`. Grilling [#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417) on 2026-08-23 found that stating a layout is not the same as stating the rule that puts a file on one side of it, and that the tree had already got the rule wrong twice.

The clinician ruled it on 2026-08-23. **A file goes under `output/` if and only if it was handed in. Everything a run produced *about* the submission is provenance and lives in the run directory.**

## The disagreement was live, not predicted

Standing rule 3 requires a `PROPOSED (verify before use)` block — the list of every clinical claim the skill contributed that the clinician's draft did not contain, which he reads and accepts or drops before submitting. `skills/practicum-case-study/SKILL.md` says it sits after the References and *"is deleted from the copy that goes to Canvas."*

Three sittings of one assignment wrote it **three different ways**:

| sitting | where the block went |
| --- | --- |
| `nur5144-m1-2026-08-18` | out of `<stem>.md`, into a standalone `-PROPOSED.md` |
| `nur5144-m1-2026-08-19` | the same |
| `nur5144-cs1-2026-08-20` | *inside* `<stem>.md`, plus a hand-made `-SUBMIT.md` carrying the same document without it |

Neither arrangement is the one the skill documents, the heading level differed between them, and **`-PROPOSED` and `-SUBMIT` as filenames appear in `skills/`, `docs/`, `CLAUDE.md`, `AGENTS.md` and `CONTEXT.md` a combined zero times.** Three runs each invented a placement because nothing said which side of the line the file was on.

## The block is a run artifact, and it says so itself

`nur5144-m1-2026-08-18-PROPOSED.md` opens: *"**Not part of the submission.** Standing rule 3. Read it, accept or drop each line, then submit the `.docx`, which does not carry this file."*

That is a description of the record of what this run changed and why — the class `claims.md` and `checks.md` are already in. It is written to `scratch/runs/<key>/proposed-<date>.md`, dated because it belongs to one sitting rather than to the assignment, which is [ADR 0005](0005-a-run-is-keyed-to-the-board.md)'s rule applied a third time.

`-SUBMIT` was never a naming decision at all. It is `SKILL.md`'s own *"or render from a copy that does not carry it"* made into a file, because nothing stripped the block. Under this ruling the category stops existing.

## Considered options

**Have the renderer strip the block.** Rejected, and it is the option that looks obvious because it fixes the visible symptom. It is a **second mechanism for one outcome** — the block already leaves `output/` by being written elsewhere — and this repo's #279 finding is that *a second mechanism that cannot fail is not a belt and braces; it is a line that costs a test.*

It also fails on its own terms. `skills/practicum-case-study/SKILL.md` runs `reference_scan.py` and `case_study_scan.py` **against `output/case-studies/<stem>.md`**. A stripping renderer leaves the block in that file, so both scanners grade a body carrying a section `case_study_scan`'s skeleton check does not recognize — and #417's whole subject is a join between a draft and its provenance being unable to tell which file is which. And `docx_write.py`'s other caller, `skills/discussion-post/SKILL.md`, has no `PROPOSED` block at all, so the renderer would grow one skill's rule for every caller to carry.

**Both — write it to the run directory and strip in the renderer.** Rejected on the same #279 ground. This was the first draft of the ruling and it was withdrawn during the grilling rather than after it.

**Treat `-PROPOSED` and `-SUBMIT` as phases of one submission and teach the key parser a trailing token.** Rejected. It blesses a workaround into the join key and puts a vocabulary nothing owns into the one string every tool must agree on. `key_of(stem)` stays a one-rule parser — strip a trailing ISO date — because nothing else ever lands under `output/`.

**State the rule in `SKILL.md` and `CONTEXT.md` rather than as a record.** Rejected because it is what already existed. The layout was written down; three runs disagreed anyway; and a prose edit to a layout fails nothing, which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).

**Name the principle and let the layouts follow.** Adopted.

## The cost this accepts

**Nothing mechanically prevents a run writing the block into `<stem>.md` anyway.** The rule is a rule, and the tree is the evidence that a rule alone is not enough — so `tools/case_study_scan.py` gains a row refusing a `PROPOSED` heading in the submitted draft. That scanner already reads that exact file and already refuses unrecognized sections, so the check costs a row rather than a mechanism. **It catches a `PROPOSED` heading and never a block written under another name**, which is a floor rather than a guarantee.

**The clinician's reading copy and the submitted document are now two files.** Under the `cs1` arrangement he could open one file and see both; now `SKILL.md` has to point him at the run directory. That is the price of `output/` meaning exactly one thing, and it is paid once per run in a sentence rather than every time a tool has to guess which file it is looking at.

**A companion file this record did not anticipate still needs a judgment.** The rule reaches it — was it handed in? — but somebody has to ask the question. What this record buys is that the question exists and has an answer, where before there was a layout with no rule behind it and three runs each guessing.
