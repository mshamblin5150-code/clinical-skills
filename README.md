# clinical-skills

Agent-agnostic skills for a nurse practitioner student's written work — clinical documentation from ER-style shorthand, and graded coursework from faculty material and live course boards.

## The skills

### Clinical documentation

| Skill | What it does |
| --- | --- |
| `clinical-note` | Turns one encounter's shorthand into a comprehensive SOAP note or FNP H&P, with proposed reasoning kept outside the document for review. |
| `batch-shift` | Reads one scanned day file, separates its encounters, and carries each one through the clinical-note workflow. |
| `icd10-cpt` | Proposes ICD-10-CM and CPT codes for a documented encounter, checking code identity and specificity before use. |

### Coursework

| Skill | What it does |
| --- | --- |
| `practicum-case-study` | Builds a researched practicum case study from faculty material and delivers the graded document as a `.docx`. |
| `discussion-post` | Researches and drafts an evidence-backed initial post for one live course discussion board. |
| `discussion-reply` | Ranks live discussion topics and drafts evidence-backed replies, with approval required before each reply is posted. |

### Setup

| Skill | What it does |
| --- | --- |
| `setup-clinical-skills` | Configures one clinician's courses, Medatrax account, local patient identity map, shorthand, and optional writing voice model. Run it once before the other skills. |

Invoke a skill by name, such as `/clinical-note`, and give the agent the material it asks for. A synthetic example:

```text
/clinical-note
29F annual visit, no concerns, no pain, medications and allergies reviewed.
```

The deliverable is the completed note. Beside it, the run also produces a private review block that identifies filled details and labels any diagnosis, differential, code, or plan it contributed as `PROPOSED (verify before use)`. That tier block is the run's working record; it is not part of the submitted note.

## What ships with them

The reference tier begins with [`reference/guidelines-catalog.md`](reference/guidelines-catalog.md), covering material from USPSTF, IDSA, AHA/ACC, KDIGO, ACIP, ADA, CDC, GINA, and GOLD. The repository also includes the derived [`reference/guidelines-uspstf.md`](reference/guidelines-uspstf.md), topic decision sheets under [`reference/thresholds/`](reference/thresholds/), the 2026 ICD-10-CM code set in `reference/icd10cm-2026.sqlite`, and CDC BMI-for-age data in `reference/cdc-bmi-for-age-2022.csv`.

[`reference/thresholds/coverage.md`](reference/thresholds/coverage.md) is the live answer for threshold-sheet coverage. The source corpus PDFs remain outside this repository, and using the skills does not require them. These reference artifacts are committed, so a new edition reaches your clone with `git pull`.

## Which guidelines these rest on

A publication year is not an expiration date. The catalog records what each document is and what the repository read; it does not establish whether a society still considers that edition current. Upstream-edition monitoring is tracked in [issue #767](https://github.com/mshamblin5150-code/clinical-skills/issues/767). The committed snapshot is current through the editions recorded in the catalog and its audit ledger.

This is a bounded corpus, not all of medicine. A topic with no threshold sheet is outside this corpus; that absence does not mean no guideline or clinical recommendation applies.

## The voice model

The coursework skills can write in the clinician's established register instead of the voice of a competent stranger. The model does not ship with this repository: `/setup-clinical-skills` builds `scratch/voice-model.md` from writing samples the clinician chooses to provide, and that file stays local and gitignored.

The assistant reads those samples. It models how the author argues — rhythm, emphasis, characteristic moves, uncertainty, and word choice — while leaving the domain of the author's examples open. It does not reduce a person's writing to a fixed list of subjects or personality adjectives.

The method separates clinical argument, spoken patient education, and reflective or argumentative prose. It looks for features supported by more than one sample and uses side-by-side discriminating pairs to make the difference between generic prose and the author's prose visible.

An assistant export can help locate conversations that may contain useful writing, whether the export comes from ChatGPT, Claude, Grok, Gemini, Copilot, or another system. The clinician approves the read in stages. A small model's summary of a conversation is not the author's writing and is never treated as a source; the selected original text is what the model reads.

The model is optional and only affects graded writing. It does not replace a rubric, evidence retrieval, clinical reasoning, or the clinician's final judgment.

> [!TIP]
> A discriminating pair shows what the method preserves. In this attested pair, both versions are by the same author about the same subject:
>
> **Tidied:** “Application of a tourniquet is associated with significant discomfort; however, it remains an appropriate intervention in the setting of life-threatening extremity hemorrhage.”
>
> **His:** “Tourniquets hurt and severe pain is expected but saving a life is more valuable than saving a limb.”
>
> A separate, synthetic H&P demonstration shows the same idea in clinical argument:
>
> 1. **Generic:** “The presentation is most consistent with a self-limited viral process. Supportive care and return precautions were discussed.”
> 2. **Voice-informed:** “The exam gives me no focal bacterial finding to treat. This is most likely viral, so supportive care carries more value than an antibiotic that cannot help.”

> [!WARNING]
> A voice model describes a snapshot of the supplied writing. The run that built it cannot verify that it sounds like the clinician; only the clinician can do that. Rubric requirements outrank voice, and a sentence that sounds right still needs independently verified clinical claims.

## Getting started

You need Git and Python 3.10 or newer. No package installation is needed to use the committed skills and references.

1. Install Python.

   **Windows:** open Terminal or PowerShell and run:

   ```powershell
   winget install Python.Python.3.13
   ```

   Check the package name before accepting it: `Python.Python.2` appears in the same search results and is the obsolete major version. Close the terminal completely and reopen it after installation so the new PATH is loaded.

   **macOS:** install Python unconditionally. The [2026-09-01 setup ruling](https://github.com/mshamblin5150-code/clinical-skills/issues/401#issuecomment-5499117118) records Apple's command-line-tools Python as 3.9.6 from primary-source research; that is below this repository's 3.10 floor. Install [Homebrew](https://brew.sh/) if needed, run the `shellenv` commands its installer prints to add Homebrew to your shell, and then run:

   ```bash
   brew install python@3.13
   ```

   Close and reopen Terminal after installation.

2. Install Git and verify it.

   **Windows:** run `winget install --id Git.Git -e --source winget`, close and reopen the terminal, then run `git --version`.

   **macOS:** run `xcode-select --install`, complete the installer, close and reopen Terminal, then run `git --version`.

3. Clone the repository and enter it:

   ```bash
   git clone https://github.com/mshamblin5150-code/clinical-skills.git
   cd clinical-skills
   ```

4. Confirm Python is visible. On Windows use `python --version`; on macOS use `python3 --version`. If neither `python`, `python3`, nor `py` is on PATH, the pre-commit hook silently degrades the PHI refusal to a warning and allows the commit.

5. Wire the skills before invoking setup:

   ```bash
   python tools/skills_mirror.py --repair
   ```

   On macOS, use `python3` in place of `python` if that is the installed command. This ordering matters for Claude Code: `/setup-clinical-skills` is not available there until the mirror exists. Codex, Cursor, Copilot, and other agents that read `AGENTS.md` need no separate skill installation, but running the repair is safe.

6. Start your agent in the repository and invoke:

   ```text
   /setup-clinical-skills
   ```

   Setup enables the repository hooks before it collects account-specific or identifying material, creates the local working folders, and guides you through the remaining choices.

## PHI

You cannot push to this repository unless the maintainer has granted you access. A commit in your local clone stays on your machine and is harmless by itself. A public fork is different: anything pushed there is public and permanent in Git history and downstream copies.

Work in the gitignored `scratch/` and `output/` folders. `scratch/` holds live working material such as day files, the patient identity map, the account profile, and writing samples. `output/` holds finished notes and coursework. Both can contain protected health information; the split is by stage, not sensitivity.

`/setup-clinical-skills` configures the repository hooks. To enable them manually in a clone, run:

```bash
git config core.hooksPath tools/hooks
```

On each commit, `tools/phi_scan.py` refuses patient names and dates from the local corpus, PHI-shaped values, and attempts to force-add files under `scratch/` or `output/`. The hook also runs the repository's other local checks.

The hook is a seatbelt, not a vault. Git does not clone hooks, `--no-verify` bypasses them, and no scanner can recognize every identifier. Keep real patient material only in those ignored folders, inspect what is staged, and never push it to a fork.

## Maintaining

### Layout

```text
skills/<name>/SKILL.md    canonical skill instructions
skills/<name>/*.md        references a skill loads on demand
reference/                field map, guideline catalog and tables, threshold sheets,
                          ICD-10-CM data, CDC BMI data, and tracker records
fixtures/                 de-identified regression material and run records
scratch/                  live working files — gitignored, never committed
output/                   finished notes and coursework — gitignored, never committed
tools/                    maintainers' scripts, graders, and repository hooks
.github/workflows/        continuous-integration and tracker automation
.claude/settings.json     the only tracked path under .claude/
CONTEXT.md                domain glossary
docs/adr/                 architectural decisions
AGENTS.md                 skill index and standing rules
```

### Agent wiring

Claude Code loads the skills through `.claude/skills/`. Repair that mirror in every clone and every worktree:

```bash
python tools/skills_mirror.py --repair
```

The command creates one link per skill so `.claude/skills/` can also hold local maintainer tooling. Claude Code reads `CLAUDE.md`, which points to `AGENTS.md`. Codex, Cursor, and Copilot read the root `AGENTS.md` directly. For another agent, provide the relevant `SKILL.md` in context.

The dangerous mirror failure is a link that has become a copy. It looks installed but keeps answering from the day the copy was made. A Git worktree can create that state by materializing `.claude/` without recreating its links. Run `--repair` in every worktree; the pre-commit hook also warns when the mirror has drifted.

Only `.claude/settings.json` is tracked under `.claude/`. The skill mirror and other machine-local Claude files remain ignored.

### Guideline corpus rebuild

The committed artifacts are enough for consumers. A maintainer who has the separate source corpus can rebuild the reference tier with the same pipeline:

```bash
python -m pip install pymupdf
python tools/guidelines_build.py <corpus-folder>
python tools/guidelines_catalog.py
python tools/threshold_coverage.py
```

`guidelines_build.py` creates content-addressed extraction, index, and recommendation artifacts outside every checkout. `guidelines_catalog.py` audits the committed catalog against that corpus, and `threshold_coverage.py` re-derives the live registry report. Follow the fuller contracts in [`CLAUDE.md`](CLAUDE.md) and [`reference/thresholds/README.md`](reference/thresholds/README.md) before publishing rebuilt artifacts.

### Tools

`tools/` contains repository maintenance scripts, deterministic graders, hook entry points, and their tests. They use the Python standard library unless their own maintainer section says otherwise. The skill instructions state their workflows in full; a named command is a reproducible check or shortcut, not permission to skip reading the instruction it supports.

A tracked file that genuinely needs PHI-shaped test data declares `phi-scan: synthetic` near its top, alone on its own line. That declaration exempts only the shape rules; it never exempts a patient name or a date found in the local corpus.

On a clone with no local patient corpus, `phi_scan.py` refuses rather than presenting a partial scan as clean. A clone that genuinely has no corpus and never will can record that fact once with `git config clinical.phiAllowNoCorpus true`; a one-time run can use `--allow-no-corpus` instead.

The hook also runs the spelling scan over staged Markdown, Python, and filenames, and checks the proposed commit message for spelling and GitHub closing keywords. Those message and spelling findings are advisory; the PHI and other refusing checks retain their own exit status.
