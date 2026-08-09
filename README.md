# clinical-skills

Agent-agnostic skills that turn ER-style clinical shorthand into documentation — starting with SOAP notes for Medatrax.

## Layout

```
skills/<name>/SKILL.md    the skill, canonical location
skills/<name>/*.md        reference the skill loads on demand
reference/                shared reference (Medatrax field map, etc.)
scratch/                  live working notes — gitignored, never committed
AGENTS.md                 skill index + standing rules
```

## Wiring it to an agent

**Claude Code** — junction each skill into `.claude/skills/` so they load natively:

```bash
for s in clinical-note batch-shift icd10-cpt; do cmd //c mklink //J ".claude\\skills\\$s" "skills\\$s"; done
```

Per-skill rather than one junction on the whole folder, so `.claude/skills/` can also hold the maintainer's own tooling without mixing it into the deliverable. The whole directory is gitignored, so each machine makes its own. Claude Code also reads `CLAUDE.md` → `AGENTS.md` automatically.

**Codex / Cursor / Copilot** — these read `AGENTS.md` from the repo root with no setup. The index there tells the agent which `SKILL.md` to open.

**Anything else** — paste the relevant `SKILL.md` into context.

## PHI

Nothing in this repo is a patient record, and nothing should become one. `.gitignore` blocks `scratch/`, `cases/`, and common export formats. Work live notes inside `scratch/`; commit only skills and de-identified examples.
