# Clinical skills

A set of agent-agnostic skills for converting ER-style clinical shorthand into documentation. Each skill is a folder under `skills/` holding a `SKILL.md` — plain Markdown with YAML frontmatter, readable by any agent.

## How to use a skill

**Read the skill file before starting the task.** Do not work from the one-line summary below — it is an index, not the instructions.

| Skill | Read | Use when |
| --- | --- | --- |
| clinical-note | [skills/clinical-note/SKILL.md](skills/clinical-note/SKILL.md) | Encounter shorthand needs to become a comprehensive SOAP or an FNP H&P |
| batch-shift | [skills/batch-shift/SKILL.md](skills/batch-shift/SKILL.md) | A whole shift is pasted at once and needs splitting into encounters |
| icd10-cpt | [skills/icd10-cpt/SKILL.md](skills/icd10-cpt/SKILL.md) | A documented encounter needs ICD-10-CM or CPT codes proposed |

<!-- Additional skills are appended here as they are written. -->

## Standing rules

These bind every skill in this repo.

1. **No PHI is ever committed.** Live notes are worked in `scratch/`, which is gitignored. Identifiers become placeholders (`[PT]`, `[DOB]`, `[MRN]`) the moment they are read. Anything committed for testing is a **fixture** — derived from a working file with the visit date and site removed, never a copy of one. See [fixtures/README.md](fixtures/README.md).
2. **Every line is given, derived, or filled.** These are academic notes against a school rubric, so sections the shorthand cannot supply are generated — but **filled content is always unremarkable**. Every abnormal finding, lab value, imaging result, medication, and diagnosis traces to the source. Filled lines are listed for the clinician to confirm before submission. Full rules in [clinical-note](skills/clinical-note/SKILL.md).
3. **Proposals are labelled.** Any clinical reasoning the agent contributes — a differential, a code, a plan item — appears under `PROPOSED (verify before use)`, outside the document body, for the clinician to accept or drop.
