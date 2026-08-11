# Clinical skills

A set of agent-agnostic skills for converting ER-style clinical shorthand into documentation. Each skill is a folder under `skills/` holding a `SKILL.md` — plain Markdown with YAML frontmatter, readable by any agent.

## How to use a skill

**Read the skill file before starting the task.** Do not work from the one-line summary below — it is an index, not the instructions.

| Skill | Read | Use when |
| --- | --- | --- |
| clinical-note | [skills/clinical-note/SKILL.md](skills/clinical-note/SKILL.md) | Encounter shorthand needs to become a comprehensive SOAP or an FNP H&P |
| batch-shift | [skills/batch-shift/SKILL.md](skills/batch-shift/SKILL.md) | A whole shift is pasted at once and needs splitting into encounters |
| icd10-cpt | [skills/icd10-cpt/SKILL.md](skills/icd10-cpt/SKILL.md) | A documented encounter needs ICD-10-CM or CPT codes proposed |
| setup-clinical-skills | [skills/setup-clinical-skills/SKILL.md](skills/setup-clinical-skills/SKILL.md) | **Run once first.** A new clinician's portal, program, picklists and patient identity map need configuring |

<!-- Additional skills are appended here as they are written. -->

**Run `/setup-clinical-skills` before the others.** Everything about *which* clinician — courses, hour targets, preceptors, sites, payer distribution, and which patient is which — is per-account and lives in `scratch/`, gitignored. `reference/medatrax-fields.md` holds how Medatrax behaves; the profile holds who you are. Where they disagree, the profile wins.

## Standing rules

These bind every skill in this repo.

1. **No PHI is ever committed.** Identifiers become placeholders (`[PT]`, `[DOB]`, `[MRN]`) the moment they are read. Anything committed for testing is a **fixture** — derived from a working file with the visit date and site removed, never a copy of one. See [fixtures/README.md](fixtures/README.md).

   **Two gitignored directories, split by stage.** Working material — day files, the identity map, the account profile — lives in `scratch/`. **Anything finished and handed over — a note, a batch document, a case study — is written to `output/`.** Never write a finished note anywhere else, and never into the repo root: everywhere else is tracked, and a note written there is a committed patient record one `git add -A` later.

   A pre-commit hook enforces this rather than trusting it to be remembered (`tools/phi_scan.py`; setup in [README.md](README.md)). It is a seatbelt, not a vault — it does not replace reading this rule.
2. **Every line is given, derived, or filled.** These are academic notes against a school rubric, so sections the shorthand cannot supply are generated — but **filled content is always unremarkable**. Every abnormal finding, lab value, imaging result, and diagnosis traces to the source. Filled lines are listed for the clinician to confirm before submission. Full rules in [clinical-note](skills/clinical-note/SKILL.md).

   **Exception — vitals and body measurements.** These are the single exception to *filled content is unremarkable*. A missing one is filled with the value that patient most plausibly had, worked up in the note if it lands abnormal (drift row 4, which grants it no exemption for being generated), and disclosed in the FILLED block like everything else generated. **No exam finding, symptom, or result is ever filled, however plausible.**

3. **Proposals are labeled.** Any clinical reasoning the agent contributes — a differential, a code, a plan item — appears under `PROPOSED (verify before use)`, outside the document body, for the clinician to accept or drop.
