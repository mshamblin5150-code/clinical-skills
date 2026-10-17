# A fixture writer starts without CLAUDE.md, and every run proves it

**Measured at:** 969cb94ed8428dc737f3fb34e550d7600fd6c3ee

[#1800](https://github.com/mshamblin5150-code/clinical-skills/issues/1800) was filed from
[ADR 0364](0364-the-blind-instruction-check-reads-every-skill-and-reference-sheet-and-a-bare-fixtures-directory-names-no-fixture.md)
Ruling 2. `fixtures/README.md` says every file a fixture-generating pass must read is part of its
prompt, and generating passes run as ordinary Claude Code subagents, which load `CLAUDE.md`. The
check that enforces the blindness rule has never read `CLAUDE.md`, and the file names concrete
fixtures. The ticket asked which side moves, whether past runs take a further qualification, and
whether the rule names its mechanism. Grilled 2026-10-17 against `main` at `d366ac2f`, where the
freshness gate read `FRESH`; the merge to the commit above changed none of the measured files, and
the figures below were re-derived there. The clinician ruled every point below in that session, one
question at a time. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**`CLAUDE.md` still returns 38 findings.** The count was taken by importing
`tools/test_blind_fixture_instructions.py` at the commit above and calling its own `findings()` on
the file; the checked population returned none. As the ticket says, the 38 were counted, not read,
and are not 38 leaks.

**The opt-out exists, and the installed release supports it.** Claude Code's subagent
documentation (https://code.claude.com/docs/en/sub-agents.md) lists `omitClaudeMd` as a frontmatter
field for a custom subagent definition. Set to `true`, it starts the subagent without the user,
project and local `CLAUDE.md` files; managed policy files still load. It requires v2.1.271 or later,
and the installed release was 2.1.284. The repository had no `.claude/agents/` definitions, and
`.gitignore` ignores everything under `.claude/` except `settings.json`, so a definition there is
untracked until the build adds an exception (`git check-ignore` named that rule). This is
documentation, not a measurement of the behavior, which is why Ruling 3 exists.

**The gap is Claude-only.** A Codex pass loads `AGENTS.md` and never `CLAUDE.md`. `CLAUDE.md` links
to `AGENTS.md` rather than importing it, so a writer that starts without `CLAUDE.md` has to be
handed `AGENTS.md` explicitly.

**The memory index carries no fixture identity.** The auto-memory `MEMORY.md` and every subject
list returned zero findings. No user-level `CLAUDE.md` exists on the maintainer's machine.

## Ruling 1 — the writer changes, not `CLAUDE.md`

Fixture-generating passes run as a tracked custom subagent definition, `fixture-writer`, that sets
`omitClaudeMd: true`. The orchestrator hands it what it needs: the skill files and `AGENTS.md`.

Making `CLAUDE.md` blind was declined. The file exists to describe each checker, and each checker
was built from a named set, so the rewording is large and never ends: every new checker section
brings fresh names. That is the mention-versus-use problem
[#246](https://github.com/mshamblin5150-code/clinical-skills/issues/246) ruled the two root
documents apart over. Doing both was declined because isolation already removes the whole file.
Leaving both unchanged and editing the rule to admit the exposure was declined because it would
make the blindness promise false on its face for every future run.

## Ruling 2 — a spawn naming the fixture-run folder must use the writer

Fixture-run output lives under one fixed parent folder, `scratch/fixture-runs/<run>/<pass>/`. A
`PreToolUse` hook on the subagent-spawning tool refuses any spawn whose instructions name a path
under `scratch/fixture-runs/` unless the spawn uses `fixture-writer`.

Prevention was chosen over detection because cleanup never makes a run blind after the fact
(`fixtures/README.md`, *Keep required instructions blind*): a run caught afterward is already
contaminated and must be redone. Documentation alone was declined because it leaves the silent
reopening the ticket warned about. A completed-run transcript check, alone or alongside the hook,
was declined: it only detects, depends on local transcripts surviving, and adds a large build for
the one gap the hook leaves. **That gap is declared rather than closed: a run whose output is
written outside `scratch/fixture-runs/` passes the hook unseen.**

## Ruling 3 — every run proves the opt-out before any note is written

`CLAUDE.md` carries one permanent line holding a random code word that appears nowhere else. At the
start of every fixture run, before any generating pass, the orchestrator spawns two subagents, each
told not to open any file and asked to repeat the code word. One is an ordinary subagent and must
repeat it, which proves the test can detect anything at all. The other is a `fixture-writer` and
must not. If either result is wrong, the run stops before any note is written. The result is saved
in the run folder.

The first real run is the first proof; no separate one-time test is taken. A one-time test with a
kept record was declined because a later Claude Code release could change the behavior while the
record still read as proof. Doing both was declined because the first per-run test produces the
same result immediately.

## Ruling 4 — past runs take one blanket sentence

`fixtures/README.md` states that every run made before `fixture-writer` existed had `CLAUDE.md` in
its writers' instructions, and that blind evidence starts with the first run made under this rule.
No score moves and no run is reread, consistent with the README's existing rule that cleanup
preserves kept output, recorded scores and their qualifications as historical evidence.

A count per run, taken by running the check against `CLAUDE.md` at each run's recorded commit, was
declined: some runs record no commit, and a bare count invites the reading the ticket forbids,
that a finding is a leak. A reader's verdict per run was declined as a large judgment spent
qualifying scores that new blind runs will supersede. A particular old run can be read when a
decision depends on it.

## Ruling 5 — `CLAUDE.md` stays outside the check, for a stated reason

Once writers start without it, `CLAUDE.md` is not a **Required instruction**. It stays outside
`REQUIRED_INSTRUCTIONS`, and the module's boundary sentence that ADR 0364 Ruling 3 ordered, which
gives the reason as pending this ticket, gives the reason as *writers start without it*.
`AGENTS.md` is still handed to writers and stays checked.

Joining with a cap on new findings was declined because every new checker section that names the
set it grades would turn the suite red, the same rewording fight Ruling 1 declined, spread over
time. Joining fully needs Ruling 1's declined rewording.

## Ruling 6 — where the rule is written, and the folder

`fixtures/README.md` names `fixture-writer` and `scratch/fixture-runs/` in *Isolate output, then
check the completed run*, where spawning is described. *Keep required instructions blind* points
to it in one line. `fixture-runs` is registered as an accounted scratch name so the scratch census
accepts it. The README's allowance for a writer's output root outside every checkout is deleted,
because the hook watches one folder.

Stating the names only in the blindness section was declined because an orchestrator following the
spawn steps could miss them. Keeping the folder under `scratch/` keeps fixture output inside the
existing PHI firewall, which matters because fixture inputs come from real day files.

`CONTEXT.md` gains **Fixture writer**. Its heading fires the glossary collision inventory against
**Fixture**, and the clinician classified the fire as a collision: the bare term is a committed
regression set, and a fixture writer is a kind of subagent, not a kind of set.

## What this does not establish

A green blind-instruction check still means only that no checked file names a concrete fixture
identity by pattern. The per-run test establishes only that the `fixture-writer` definition, on that
day's release, did not carry `CLAUDE.md` into its starting context; it says nothing about files a
writer opens during its pass, which the existing rule to paste inputs rather than point at them
still governs. The hook establishes nothing about a run whose output lands outside
`scratch/fixture-runs/`.

Standing rule 6 removes a run's private staging paths after the checks complete. Where the per-run
test's saved result is kept once staging is removed is the build's to place under that rule.
