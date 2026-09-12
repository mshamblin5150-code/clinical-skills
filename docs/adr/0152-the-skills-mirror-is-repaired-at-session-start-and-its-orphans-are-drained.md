# The skills mirror is repaired at session start and its orphans are drained

Ruled by the clinician on 2026-09-08, out of
[#820](https://github.com/mshamblin5150-code/clinical-skills/issues/820)'s grilling.

[#820](https://github.com/mshamblin5150-code/clinical-skills/issues/820) records a `discussion-reply`
run served `contains at least 100 words` from the `.claude/skills/` mirror one day after
[#725](https://github.com/mshamblin5150-code/clinical-skills/issues/725) retired that figure, and
sat open through six tracker sweeps whose mirror compositions all disagreed with one another. Its
four decisions were written against one mechanism: *a copy goes stale over the life of a branch*.
This session measured a different one, and three of the four decisions do not survive the
measurement.

## Measured before ruling, 2026-09-08, at `88b5407`

**`tools/hooks/post-checkout` is correct and it works.** A plain `git worktree add --detach` in this
repository fired it and printed `relinked 10 skill(s).`, exit 0, all ten entries junctioned
including `_shared`. [ADR 0131](0131-the-shared-sheet-directory-moves-whole-and-the-mirror-gains-a-non-skill-rule.md)
ruling 5 is sound as written. **The discriminating question every sweep on #820 declared un-derived
— *never fired* against *fired and failed silently* — is neither.**

**Every worktree the desktop app makes carries 23 entries, 0 junctions, and no `_shared`.** Measured
across all four such worktrees alive at the time. `skill_names()` reads `skills/` and
`test_mirror_only_entries_are_ignored` pins that a mirror-only entry is never touched, so
**`--repair` cannot produce a 23-entry mirror**. The app's `.claude/` copy stands where the hook's
work should be.

**The copy's source is the main checkout's working tree, not the worktree's own.** `diff` of this
worktree's mirrored `discussion-post/SKILL.md` against `C:/codeing/clinical_skills/skills/` returns
nothing; against its own tracked copy it returns 256 changed lines. The main checkout was on `main`
at `b26ea2a`, **130 commits behind `origin/main`**. So a worktree is not a copy that drifts. **It is
born stale, from a tree it never checked out.**

**The stale path resolves, which is what makes it silent.** The mirrored
`practicum-case-study/SKILL.md` points at `reference/apa7.md`; the pre-move sheet is sitting there at
**40,604 bytes against the tracked `_shared` sheet's 49,101**. No broken link, no warning.
`_shared/reference/sourcing.md` is named nowhere in the copy, so a mirror-served run never opens it.

**Two facts about the harness, both sourced rather than reasoned.** Claude Code loads project skills
from `.claude/skills/` and there is no settings key for an alternate directory; symlinks and
junctions are documented and followed. And a `SessionStart` hook reaches the model only through
`hookSpecificOutput.additionalContext` — plain stdout does not, which is visible in the shipped
`explanatory-output-style` plugin's own handler and in neither documentation page a subagent read.

## Ruling 1 — the seam is a `SessionStart` hook in the tracked settings file, and the run path stays clean

**#820's decisions 1 and 2 are structurally too late and decision 3 is unavailable.** A `SKILL.md`
body enters context when the skill is invoked, before its own step 1 can execute anything, so an
in-run check reports a rule the run has already been given and an in-run repair cannot un-serve it.
Decision 3 is refused on the fact above: there is no alternate skills directory to load from, and
the junction design is correct rather than retiring.

**`.claude/settings.json` is tracked.** It is therefore the only seam in this repository that
propagates to every checkout by git — `core.hooksPath` is per-clone local configuration and reaches
nothing on its own. That file already carries a `PreToolUse` and a `SessionEnd` entry, so this adds
a third to an established mechanism rather than opening one.

**Decision 4 is closed.** `CLAUDE.md`'s standing ground for the advisory posture is that *the reader
is the party who can notice*. #820's founding instance is that premise falsified, and this session
added a second: a reader in the sweep of 2026-09-08 read the mirror by accident and published a
wrong section count into a draft finding.

**No command joins the consumer path.** [AGENTS.md](../../AGENTS.md)'s promise that maintainer
tooling is not cited there is kept, and the seven clinical skills gain no step.

## Ruling 2 — an orphan is drained, never deleted, and the repair then completes

`repair()` refuses an entry whose mirror holds a file `skills/<name>/` does not — *"Relinking would
delete them."* It skips that entry and relinks the rest. **In this worktree it relinks nine and
refuses `practicum-case-study`**, on six orphans that are exactly the sheets ADR 0131 ruling 1 moved.

**That refusal is correct as a safety property and fatal as an unattended remedy.** The hook runs
with nobody watching, and the entry it cannot repair is the skill whose output is a graded `.docx`.
Every later session hits the same refusal, so the entry stays stale permanently. **A remedy that
cannot complete is this ticket's own subject one level down.**

The orphans move to `.claude/skills-orphaned/<name>/<UTC stamp>/` and the entry is then relinked.
**This is the scratch census's discipline transferred unchanged** — a failing root is drained under a
Ticket directory, *a move, never a delete*, because disposal is the clinician's word per file. The
hook may not decide what to discard; nothing obliges it to leave the mirror broken to avoid deciding.

**Deleting was refused even though every orphan is recoverable from git history by construction and
`.claude/` is a source of record for nothing.** That is a claim about provenance the tool does not
check, and the refusal exists because somebody thought about the case where it is false.

## Ruling 3 — the pre-repair report is recorded before the repair runs

**This is #820 decision 2's hazard arriving at the new seam, and it is not hypothetical.** This
worktree's broken mirror is live evidence for an open ticket; the sweep of 2026-09-03 said so and
deliberately declined to repair. **A `SessionStart` hook would have destroyed that evidence at the
head of that sweep, before its reader saw anything.** Six of the ten comments on #820 rest on a
mirror state this fix erases.

So the repair writes the report first. **Paths, status words and counts, never file contents** —
which is what every sweep comment on that thread actually quoted, and what
`tracker_publish_hook.py`'s counts-free marker already establishes as a shape.

**The record and the drains live under `.claude/`, not `scratch/`.** `repo_root.scratch_root()`
resolves to the *owning* checkout, so a worktree writing there lands in the main checkout's
`scratch/`, races every other worktree for one path, and adds a top-level entry `scratch_census.py`
grades — a refusing gate. `.claude/` is per-checkout, gitignored, and outside that census.

**It also makes the fix falsifiable.** If the hook stops firing the records stop appearing, and that
is a measurement rather than a silence.

## Ruling 4 — one line always, and the full report only when something was broken

**Silence when clean would conflate *the hook ran and the mirror is linked* with *the hook never
ran*** — no Python on `PATH`, a timeout, a settings file the app did not load. Every scanner here
has an exit status to separate those; a hook has one channel, and nothing else on this path can
report. Given #820 is a check that was inert on the path that mattered, making success and
non-execution identical would rebuild the defect inside the fix.

`skills mirror: 10 of 10 linked` on a good session. The report, the relink count and what was
drained on a bad one. **`phi_scan` already prints its population row on every run for this reason**,
so a reader cannot read silence as coverage.

**A defect found on the way: `--repair` ignores `--quiet` entirely** — the repair branch prints the
full report unconditionally at `tools/skills_mirror.py:412-421`, and `--quiet` is honored only on the
report branch. `post-checkout` has therefore been printing twelve lines into checkout noise since
2026-09-05. This ruling supersedes that behavior for both callers.

## Ruling 5 — the repair runs in the main session only

`SessionStart` fires inside subagents and its payload carries `agent_id`. A tracker sweep spawns many
concurrently, and `repair()` is `shutil.rmtree` followed by `mklink /J`. **Two of those interleaving
on one entry can leave a half-removed directory or a failed link, which is worse than the stale copy
the hook exists to fix.**

Gated on the absence of `agent_id`. **The race is removed by removing every writer but one, not by
serializing them**, so no lock is taken. A subagent starts after its parent's `SessionStart` and
inherits a repaired mirror; the case a lock would buy is one where the subagent's repair would fail
identically. `aar_scan.py --session-end`, in this same settings file, already ignores subagent
sessions.

## Ruling 6 — the registration is pinned, and the pin is declared to prove registration and not firing

**`.claude/skills/` is gitignored, so the mirror's state is gradeable by nothing, ever.** That is
permanent and unchanged by this record. **`.claude/settings.json` is tracked**, and today nothing
grades it: an edit could drop the hook and the whole suite stays green, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) arriving on configuration
instead of prose.

A test pins the registration, **and states beside itself that it proves registration and not
execution.** That qualifier is not politeness. Registration without execution is exactly what
`post-checkout` has been doing since 2026-09-05 — correctly written, correctly gated, provably
functional, and inert on the path that makes these worktrees. A green test that read as coverage of
this mechanism would be the same failure a third time. `test_ci_workflow.py` is the precedent: it
reads a configuration file as text, pins it against `CLAUDE.md`, and says plainly that the first push
is the only end-to-end check.

**`tools/hooks/post-checkout` stays.** It is correct, it is proven, and it covers `git worktree add`
outside Claude Code — this repository has roughly fifteen `codex/ticket-*` worktrees made that way.
**What this record supersedes is ADR 0131 ruling 5's claim to close the worktree-birth half**, not
the hook it built.

## Ruling 7 — branch currency is out of scope, and the boundary is stated rather than left to be assumed

The main checkout has a **correctly junctioned mirror**, nine live junctions, nothing to repair — and
is 130 commits behind `origin/main`. A `practicum-case-study` run started there is served, faithfully
and with no warning from any mechanism in this record, a `SKILL.md` predating the `_shared` move.

**A repaired mirror is a consistent run, never a current one.** After this fix the worst case stops
being *a worktree served the main checkout's stale tree* and becomes *a checkout served its own stale
tree*, which is quieter — there is no longer a disagreement anywhere for a second source to catch,
and #820's founding instance was caught only because a grader's constant disagreed with the mirror.

**Folding a currency check into this hook was refused on cost rather than on relevance.** It opens a
socket, and this hook runs at the head of every session including offline ones; making the cheapest
mechanism in the fix the one that can hang is the wrong trade. `tracker_freshness.py` already answers
the question and is invoked deliberately. Filed separately.

## Ruling 8 — the protocol is a `--session-start` flag on `skills_mirror.py`

The hook must read its JSON payload from stdin to see whether `agent_id` is present, and must emit
`hookSpecificOutput.additionalContext` for its line to reach the model. Both are protocol rather than
mirror logic, and this repository has settled the same question twice in opposite directions.

**`aar_scan.py --session-end` is the closer precedent on every axis** — same settings file, same
lifecycle-event shape, same *run the thing and report* job. The split that justifies
`tracker_publish_hook.py` is that `PreToolUse` must **decide**: it parses an arbitrary `gh` command
line and returns an allow-or-deny verdict, a substantial job with its own limits object and its own
tests. This hook decides nothing.

**A shell script under `tools/hooks/` was refused on mechanics.** Hand-quoting JSON in `sh` on
Windows produces a hook that silently emits nothing, which is this ticket's own failure mode.

`skills_mirror.py` already calls `use_utf8()` at `:432`, so the console codec rule is met where it
stands.

## Ruling 9 — `repo_root()` is defeated by an inherited `GIT_WORK_TREE`, and the kept hook is where that lands

**Found live, during this session's own rebase, and measured rather than reasoned.** The `rebase`
printed:

```
skills mirror: C:\...\grill-with-docs-472-eec18b\tools
  no skills found under skills/ -- nothing to mirror.
```

Reproduced exactly with `GIT_DIR=<absolute> GIT_WORK_TREE=.`, which is the shape git exports to its
hooks: `repo_root()` returns `<worktree>/tools`, `skill_names()` finds no `skills/` beneath it,
and the command prints **nothing to mirror** and exits **0**. A clean-looking report over the wrong
tree — this ticket's own defect, inside the tool that reports it.

**The defense is the vulnerability, which is why this is a ruling rather than a bug note.**
`repo_root()` asks git from the *script's own directory* rather than the process cwd, and its
docstring says why: *"A worktree is a different toplevel than the checkout it was branched from, and
conflating the two is precisely the bug this file is about."* That `-C` is correct and it is exactly
what makes an inherited **relative** `GIT_WORK_TREE` resolve to `tools/`. A tool that had used the
process cwd would have been right here.

**The blast radius is this module alone**, measured: `tools/repo_root.py` takes no subprocess by
design and is immune; `adr_next.py` shells the same command but derives it from a passed cwd and
reports correctly under the same environment.

**It does not reach ruling 1's mechanism.** `SessionStart` is not a git hook and inherits no such
environment. **It reaches the hook ruling 6 keeps** — `post-checkout`, and `pre-commit`'s advisory
run — so the hook this record preserves can silently measure `tools/` and report success. Filed
separately; the fix is a resolution that cannot be redirected by inherited environment, not a change
to any ruling above.

**Correction, 2026-09-12, on [#978](https://github.com/mshamblin5150-code/clinical-skills/issues/978)'s grilling.** Three rows of the measurement above are false and the ruling they sit under stands. Measured on git 2.54.0.windows.1 with hooks whose whole body is `env | grep -E '^GIT_'`, and recorded in [ADR 0197](0197-root-resolution-in-the-skills-mirror-stops-asking-git-and-an-empty-population-is-a-did-not-scan.md): **git exports no `GIT_WORK_TREE` to any hook**, so the reproduction above is a real reproduction and is not the shape git produces; the live vector is an **absolute `GIT_DIR`**, exported only inside a linked worktree, and either variable alone suffices, so *relative* is doing no work; and **`post-checkout` is not an affected hook** — `git worktree add` runs it with no `GIT_*` set at all — while **`pre-commit` inside a worktree is**. What makes this module the one affected is not that it asks from the script's directory rather than from cwd, it is that the directory it asks from is **below the checkout root**, which is where git places the work tree when `GIT_DIR` is set alone. *A tool that had used the process cwd would have been right here* was measured true and is untouched.

**Ruling 2 is confirmed live by the same session.** A `--repair` run here relinked nine entries and
refused `practicum-case-study` on exactly the six sheets ADR 0131 ruling 1 moved. The prediction
that the unattended remedy completes on nine and stalls permanently on the graded-`.docx` skill is a
measurement, not an argument.

## What this record does not settle

**Whether the mirror can ever be graded.** It cannot, while `.claude/` is gitignored, and nothing
here proposes tracking it.

**What a session does when the hook did not fire at all.** The one line from ruling 4 makes silence
mean *never ran*, and nothing acts on that; the reader is told and the run proceeds.

**A mirror entry absent at session start.** The skill is unlisted and cannot be invoked, and a
mid-session repair may not restore it to the listing. That failure is loud rather than silent — the
skill is simply not there — so no mechanism is proposed for it.

**Non-Claude-Code paths.** A Codex worktree or a hand-run skill is covered by `post-checkout` alone,
and only where creation went through `git worktree add`.

**Cleanup of `.claude/skills-orphaned/`.** It accumulates, in practice once per reference-sheet move,
and nothing prunes it.

**Whether `SessionStart` fires before the skill listing is built.** The body is read at invocation, so
a repair at session start reaches it; the description in the listing may come from the pre-repair
mirror. No clinical rule lives in a description, and this was not measured.
