# filled-anchor — run 2

Twelve `icd10-cpt` worksheets, one per case, produced 2026-08-16 over the twelve committed inputs in [notes/](../notes/). Scored in [assertions.md](../assertions.md); this file is the record of how the run was made and what is safe to conclude from it.

**This is the first `icd10-cpt` run this repo has kept**, and that is the whole reason the directory exists.

## Why it is committed, when no run before it was

Run 1 lived in `scratch/filled-anchor-run-1/` with the four graders that scored it. Both are gone — not in the main checkout and not in any worktree as of 2026-08-15 — because `scratch/` is gitignored by design and a worktree is removed when it merges. [fixtures/README](../../README.md) and [assertions.md](../assertions.md) both write that up at length; the short version is that **gitignored and reproducible are not compatible for longer than the directory lasts**, and every figure run 1 earned became a citation rather than a number.

[#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124) asked for the re-run and said the graders should not go back in the same place. They did not — `tools/anchor_scan.py` and `tools/specificity_scan.py` are committed, tested, and print counts only. **This directory is the other half of that**: a grader nobody can run against output nobody can see is the same problem one step along.

**It costs nothing new in exposure.** These worksheets derive from [notes/](../notes/), which are already committed and already de-identified — visit date and site removed, names `[PT]` under [standing rule 1](../../../AGENTS.md). `icd10-cpt` reads a note and returns a worksheet; unlike `clinical-note` it consults no account profile, so the widening [fixtures/README](../../README.md) records for generated inputs — *a fixture derived from a skill's output inherits that skill's whole context* — has no second context to reach here. Checked rather than assumed: no `[SITE-A]`/`[SITE-B]` marker and no date literal appears in any of the twelve.

## What it is not

**It is not a reference and it is not correct output.** It is what the skill did on one day at one commit. Where a worksheet is wrong, that is a fact about the run, and the rows in [assertions.md](../assertions.md) are what decide which parts were graded at all.

**Most of it is ungraded.** ANCHOR, C5 and R2 were scored. C1 through C4 were not re-run for their own sake — [#124](https://github.com/mshamblin5150-code/clinical-skills/issues/124) says why — so 214 for-entry codes carry descriptors that **no row in this repo has checked against the release**. Every generating pass reports having looked each one up; that is a self-report, and [ADR 0001](../../../docs/adr/0001-fixture-asserts-on-named-findings.md) is the standing objection to treating one as evidence.

## The commit this belongs to

`184462d`, with `skills/icd10-cpt/SKILL.md` last moved by `f8ac2f8` ([#68](https://github.com/mshamblin5150-code/clinical-skills/issues/68), 2026-08-15). **Neither moved while the run was in flight**, which is worth recording only because [fixtures/README](../../README.md) has now counted six consecutive runs where something did.

## How it was made

Twelve independent generating passes, one per case, each given `skills/icd10-cpt/SKILL.md` and **one** input file. Then five grading passes that authored none of it — three over the ANCHOR rows, one over R2, and the orchestrating pass, which ran the two scanners and wrote no worksheet.

**`fixtures/` was closed to every generating pass for any purpose**, including the links `AGENTS.md` and `CLAUDE.md` carry into it. [fixtures/README](../../README.md) asks for the inputs to be pasted inline rather than pointed at, because *a path into the inputs directory is what makes the neighboring file look like an input* — and this set's `notes/README.md` is exactly such a neighbor, now carrying two `grep` commands over the case files and a paragraph naming which cases word a `GAPS` entry which way.

**The inputs were copied to a neutral path instead of pasted inline**, at `scratch/filled-anchor-run-2/inputs/`, and each pass was given only its own copy. That is a deviation from the letter of the rule and it serves the same end: there is no inputs directory to be curious about, because the directory the passes could see holds twelve numbered files and nothing else. It is recorded here rather than smoothed over, since the rule was written from a run where three of ten passes read a README they had been pointed near.

**Every pass was asked afterwards what it opened.** All twelve reported `SKILL.md`, their own input, and their own output; all twelve reported opening nothing under `fixtures/`. Three deviations were self-disclosed and none touches the withholding rule:

- Several passes ran `tools/specificity_scan.py` against the shared output directory rather than their own file, so the tool read other cases' worksheets and returned **aggregate counts**. No worksheet content is printed without `--show`, which none used. Four passes noticed this themselves and re-ran against an isolated copy.
- One pass grepped `tools/specificity_scan.py` — six lines of a committed tool, not a fixture.
- One pass ran `tools/spelling_scan.py` over its own worksheet.

**None of the three touches the withholding rule and the first one narrows a claim elsewhere.** A few passes saw aggregate totals covering worksheets they never opened, so *twelve passes that could not see each other* is too strong; the accurate form is *could not see each other's **text***, which is what [assertions.md](../assertions.md) says beside the R2 verdict that rests on it.

**That audit is a self-report and cannot be made anything better**, which [fixtures/README](../../README.md) says in as many words. Nothing in the output distinguishes a contaminated run from a clean one; the audit is an admission against interest, and the defense is the withholding rather than the asking.

## Figures, and the commands that recompute them

| | | Recomputed by |
| --- | --- | --- |
| worksheets | 12 | `anchor_scan` |
| code entries | 297 | grep 1 |
| — proposed for entry | 210 | `anchor_scan` |
| — differential, `NOT FOR ENTRY` | 87 | grep 2 |
| codes carrying `SOURCE: filled` | 29 | `anchor_scan` |
| codes listed under `CODED, ANCHOR WAS FILLED` | 29 | `anchor_scan` |
| `SPECIFICITY` flags | 200 | `specificity_scan` |

```bash
python tools/anchor_scan.py fixtures/filled-anchor/run-2
python tools/specificity_scan.py fixtures/filled-anchor/run-2
```

```bash
grep -hcE '^[ \t]*(ICD-?10(-CM)?|CPT|HCPCS)[ \t]+[0-9A-Z]' fixtures/filled-anchor/run-2/case-*.md
grep -hcE 'NOT FOR ENTRY[ \t]*$' fixtures/filled-anchor/run-2/case-*.md
```

**The two halves reconcile exactly and that is the check**, not decoration: 297 entry lines less the 87 ending in `NOT FOR ENTRY` is 210, which is what `anchor_scan` counts independently by parsing rather than by subtracting. **The count is also what tells the two code shapes apart** — five parts or six for entry, three for a differential — so a run whose totals stopped reconciling would have broken C4 as well.

**The four `anchor_scan` figures are pinned by `tools/test_anchor_scan.py`**, so editing a worksheet fails a test rather than quietly voiding this table. That is `test_spelling_scan.py`'s arrangement over [notes/](../notes/), arriving at the run beside it.

**Two of these figures read 214 and 83 when this file was first written, and how they were wrong is worth more than the correction.** Four differential entries carry a descriptor too long for one line — `K27.9 Peptic ulcer, site unspecified, unspecified as acute or chronic, without hemorrhage or perforation` is 96 characters — so `NOT FOR ENTRY` lands on the **continuation line**. `anchor_scan` tested the code's own physical line, read all four as proposed for entry, and published a figure four short. **The full suite was green over the wrong number**, because the test pinned the parser's answer and the parser was what was wrong.

**That is [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70)'s open question answered from the wrong direction.** It asks whether mandating a per-entry marker collapses the ambiguity into a formatting rule. `icd10-cpt` does mandate one, for the reason #70 gives — *a block heading does not survive being copied one line at a time* — and 297 entries across twelve independent passes show it works: `specificity_scan` reports **zero** flags on a `NOT FOR ENTRY` line, so nothing crossed the boundary. **What the mandate did not do is remove the ambiguity. It moved it from *what is an entry* down to *what is a line*,** where it is smaller, rarer, and still there. Found by a reader sweeping the tracker, not by any of the 820 tests.

Both print counts only and both are safe to paste. **Their `--show` output is PHI on the same terms as every other scanner here** — read it, do not paste it — and that holds even though these twelve are committed, because the habit is what protects the run directories that are not.

**Both exit 0 on this directory.** `anchor_scan` reporting 29 against 29 is the mechanical half of A1, A2 and A5; `specificity_scan` reporting zero faults over 200 flags is **C5**, whole. Neither is a walked row: what `anchor_scan` cannot see is whether the *right* codes were marked, which needs the note beside the worksheet, and that reading is in [assertions.md](../assertions.md).

**Case 4 is worth opening first if you are here to check the tooling.** Its step-4 filled block is empty — correctly, since both its inputs are given — and it says so in a sentence that names `E66.3` and `Z68.25` **inside the block**. That is the prose hazard [assertions.md](../assertions.md) predicted under *Still unresolved*, arriving unprompted on the first run after it was written down. A substring grader reports two codes routed there; `anchor_scan` reads the block's own `<code> - <value>` line format and reports none, which is the reason it was built that way.

## Its spellings are American, and that is a result rather than a default

Zero of [standing rule 4](../../../AGENTS.md)'s forms appear in 4,766 lines — measured against the eight the table held on 2026-08-16, **and re-derived against all ten on 2026-08-18**, still zero. That is not the exemption [notes/](../notes/) carries — those twelve keep their British spellings because they are the only committed evidence the skill ever emitted any, and correcting them would falsify the record. **Nothing here needs exempting**, so `tools/spelling_scan.py --all` reads this directory like any other tracked Markdown and a form appearing here later is a real defect.
