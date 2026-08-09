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

**Claude Code** — from the repo root, point `.claude/skills` at `skills/` so the skills load natively:

```bash
cmd //c mklink //J .claude\skills skills
```

The junction is gitignored, so each machine makes its own. Claude Code also reads `CLAUDE.md` → `AGENTS.md` automatically.

**Codex / Cursor / Copilot** — these read `AGENTS.md` from the repo root with no setup. The index there tells the agent which `SKILL.md` to open.

**Anything else** — paste the relevant `SKILL.md` into context.

## PHI

Nothing in this repo is a patient record, and nothing should become one. `.gitignore` blocks `scratch/`, `cases/`, and common export formats. Work live notes inside `scratch/`; commit only skills and de-identified examples.
