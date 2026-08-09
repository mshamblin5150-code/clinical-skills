# Clinical skills

A set of agent-agnostic skills for converting ER-style clinical shorthand into documentation. Each skill is a folder under `skills/` holding a `SKILL.md` — plain Markdown with YAML frontmatter, readable by any agent.

## How to use a skill

**Read the skill file before starting the task.** Do not work from the one-line summary below — it is an index, not the instructions.

| Skill | Read | Use when |
| --- | --- | --- |
| soap-note | [skills/soap-note/SKILL.md](skills/soap-note/SKILL.md) | Raw encounter shorthand needs to become a SOAP note |

<!-- Additional skills are appended here as they are written. -->

## Standing rules

These bind every skill in this repo.

1. **No PHI is ever committed.** Live notes are worked in `scratch/`, which is gitignored. Identifiers become placeholders (`[PT]`, `[DOB]`, `[MRN]`) the moment they are read.
2. **Traceable over complete.** Every clinical claim in generated output maps to a token in the source. A missing detail is reported as a gap; it is never inferred from clinical plausibility.
3. **Proposals are labelled.** Any clinical reasoning the agent contributes — a differential, a code, a plan item — appears under `PROPOSED (verify before use)`, outside the document body, for the clinician to accept or drop.
