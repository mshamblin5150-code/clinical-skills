# clinical-skills

Agent-agnostic skills that turn ER-style clinical shorthand into documentation — starting with SOAP notes for Medatrax.

## Layout

```
skills/<name>/SKILL.md    the skill, canonical location
skills/<name>/*.md        reference the skill loads on demand
reference/                shared reference (Medatrax field map, the ICD-10-CM code set)
fixtures/                 regression sets — de-identified, committed
scratch/                  live working files — gitignored, never committed
output/                   finished notes and graded coursework — gitignored, never committed
tools/                    maintainer scripts + repository hooks
CONTEXT.md                domain glossary
docs/adr/                 architectural decisions
AGENTS.md                 skill index + standing rules
```

`scratch/` and `output/` are both gitignored and both hold PHI. The split is by *stage*, not by sensitivity: `scratch/` is working material — day files, the identity map, the account profile — and `output/` is the finished deliverable you actually hand in.

## Wiring it to an agent

**Claude Code** — junction each skill into `.claude/skills/` so they load natively:

```bash
python tools/skills_mirror.py --repair
```

That links every skill under `skills/`, and re-run it any time to check. Per-skill rather than one junction on the whole folder, so `.claude/skills/` can also hold the maintainer's own tooling without mixing it into the deliverable. The whole directory is gitignored, so each machine makes its own. Claude Code also reads `CLAUDE.md` → `AGENTS.md` automatically.

It used to be a hand-written `for s in clinical-note batch-shift icd10-cpt` loop, which was correct when there were three skills and silently stopped installing `setup-clinical-skills` when there were four. The script enumerates `skills/` instead.

**A junction that turns into a copy is the failure mode worth knowing about**, because it looks exactly like a working install and answers with whatever the skill said the day the copy was made. `git worktree` is one way to get there: it materializes `.claude/` by copying, the copy follows the junctions rather than recreating them, and the new worktree starts out holding frozen skills. **Every worktree needs its own `--repair` run**, and the pre-commit hook prints a warning when a mirror has drifted.

**Codex / Cursor / Copilot** — these read `AGENTS.md` from the repo root with no setup. The index there tells the agent which `SKILL.md` to open.

**Anything else** — paste the relevant `SKILL.md` into context.

## PHI

Nothing in this repo is a patient record, and nothing should become one. `.gitignore` blocks `scratch/`, `output/`, `cases/`, `patients/` and common export formats. Work live material inside `scratch/`, write finished notes into `output/`; commit only skills and de-identified examples.

**Enable the repository hooks — git does not clone hooks, so every clone needs this once:**

```bash
git config core.hooksPath tools/hooks
```

`/setup-clinical-skills` does this for you and creates the folders. After that, every commit in that clone is scanned by `tools/phi_scan.py`, which refuses:

- any patient name appearing in your local corpus, and any corpus date written
  in a supported US numeric, written English, or ISO form,
- anything PHI-shaped — a `dob` followed by a date, an SSN, a phone number, an MRN plus digits, an `M-D-YY`-style short date,
- any attempt to force-add a path under `scratch/` or `output/`.

A file that genuinely needs PHI-shaped literals — the tests for the date extractors do — declares `phi-scan: synthetic` near its top, **alone on its own line**. Mentioning it mid-sentence, as this paragraph does, is not declaring it. **That exempts the shape rules only.** A file may say its dates are invented; no file may say its patient names are fine.

The same hook directory also runs the advisory spelling scan over staged Markdown, Python and filenames, then runs both the spelling and GitHub closing-keyword scans over the message in `commit-msg`. Findings warn and never refuse the commit.

It is a seatbelt, not a vault: `--no-verify` bypasses it, and the corpus layer is inert on a clone with no local corpus — though since #93 that refuses the commit rather than warning past it, until the clone declares once that it has no corpus. Details and limits in [CLAUDE.md](CLAUDE.md).
