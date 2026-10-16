# A subagent launch hook refuses a patient-work brief that names temp or no existing staging folder

**Measured at:** 9f6ee5f560707da7f4a0eeb8c44416344be1f161

[#1593](https://github.com/mshamblin5150-code/clinical-skills/issues/1593) was filed from the
after-action review of a `batch-shift` run on a NUR5144 clinic shift, 2026-10-06. A note writer
redirected `differential_scan.py --show` output into the system temp directory, and blind agreement
readers left generator scripts carrying verbatim note spans there. The ticket proposed naming
`<run>/private/` in the batch-shift brief templates as the only place for such files, and asked each
writer to search its own note for every source identifier before reporting one "not carried". Two
later comments recorded the same failure on two further shifts: a coordinator
reused an earlier run's brief that named the system temp directory as the staging route, at least
one pass on each shift followed it, and passes whose brief named no destination for scanner output
fell back to the session scratchpad. The clinician ruled every point below on 2026-10-16, against
`main` at the commit above, where the freshness gate read `FRESH`. **Nothing is built here; this is
the record the build reads.**

## Measured before ruling

**The proposed route conflicts with standing rule 6.** [AGENTS.md](../../AGENTS.md) standing rule 6
([ADR 0291](0291-a-writing-pass-stages-patient-text-in-a-scratch-root-and-a-hook-refuses-heredoc-writes-there.md)
ruling 1) gives every writing pass its own `scratch/sessions/<key>/<pass-label>/` staging folder,
says patient text never passes through the system temp directory or the session scratchpad, and says
the orchestrating context states that route in every brief **and no skill file copies it**. A
`<run>/private/` route written into `skills/batch-shift/SKILL.md` would be a second route in a file
the rule forbids from carrying one. The recorded runs broke a written rule; they did not fall into a
gap in it.

**Nothing reads a brief before it is sent.** The `PreToolUse` registrations in
`.claude/settings.json` match Bash, Monitor, PowerShell and the two browser tool families; none
matches the subagent launch tool. `tools/briefing_surface.py` grades briefing prose in
`skills/*/SKILL.md`, not a brief as sent. A brief is the launch call's prompt, not a file, so the
launch call is the only point at which one can be read before the pass acts on it.

**Every recurrence was a patient-work brief that named its run directory.** The reused briefs named
the shift run under `scratch/runs/` and named temp as the staging route. The passes that fell back
to the scratchpad were briefed against the same run.

**The session scratchpad sits under the system temp directory**, as ADR 0291 measured:
`AppData\Local\Temp\claude\`.

**Claude's user-level session store already holds patient text from every run.** Under
`~/.claude/projects/<project>/` Claude Code keeps each session's transcript and, for a tool output
too large to show inline, a separate file under `tool-results/`. A transcript carries the
clinician's pasted shorthand, every note a pass opened with the Read tool, and every brief sent to a
subagent. This session's own large command output was saved there while this record was being
drafted. Reading a brief with the Read tool rather than printing it moves the text from a
`tool-results/` file into the transcript; it does not keep it out of the store.

**The identifier the writer missed was caught by the step 7 sweep.** The 2026-10-06 writer's "not
carried" claim was false: a guessed form of a school name stood on a working line. The
coordinator's read of the notes for real names before the Review sheet, in
`skills/batch-shift/SKILL.md` step 7, found and removed it. The leaked form was a guessed spelling,
not the source string.

## Ruling 1 — a launch hook refuses a brief naming the system temp directory or the scratchpad

A `PreToolUse` hook on the subagent launch tool reads the brief before the subagent starts and
refuses one that names the system temp directory or the session scratchpad as a location. Standing
rule 6 stays the single home of the route; no skill file gains a copy. The hook binds every skill's
fan-outs, not only `batch-shift`'s, because the rule it enforces binds them all.

Writing the route into `skills/batch-shift/SKILL.md` was declined: it is the second copy rule 6
forbids, and it does not reach the failure, which was a reused brief rather than a misread skill. A
further prose line asking the orchestrator to confirm a brief's paths was declined because rule 6
and a memory note had already failed three times in two days. Closing the item as covered by rule 6
was declined on the same record.

## Ruling 2 — a brief that names a run directory must also name a staging folder

A brief that names a run directory, `scratch/runs/...` or `output/...`, is refused unless it also
names a `scratch/sessions/...` staging folder. A brief naming no run directory owes no route.

Requiring a route of every brief was declined: every read-only search and tracker sweep would pay
for it, and a "writes nothing" line stamped on every launch stops meaning anything. Refusing only
named bad locations was declined because it leaves the recorded scratchpad fallback open.

## Ruling 3 — the named staging folder must already exist under a registered checkout

The staging folder a patient-work brief names must already exist inside the `scratch/sessions/`
folder of a checkout `git worktree list` registers. A relative path resolves against the launch
payload's working directory. It need not be empty.

This catches the reused brief: rule 6's cleanup removes a staging folder after the checks, so a
folder named in an earlier run's brief no longer exists. It also catches a mistyped path. A
coordinator that names a folder before creating it is refused, which is the order rule 6 already
sets. An empty-folder requirement was declined because relaunching a failed pass into its own folder
is an ordinary event, and a refusal mid-shift on a leftover file would cost more than the one extra
case it catches.

## Ruling 4 — scanner `--show` output and note-text scripts are staging-folder files

Private scanner `--show` output and any script that carries note text are written into the pass's
staging folder and removed by rule 6's cleanup. Standing rule 6's staging paragraph gains one clause
naming both, so a pass that treats scanner output as something other than a file write is told
otherwise in the rule's own text.

The ticket's `<run>/private/` route was declined. That folder holds records a run keeps, and these
files are working material nothing reads after the pass returns; keeping them only multiplies
patient text, and the route would be a second one.

## Ruling 5 — no console-printing rule; the session store is a declared patient-text location

No rule forbids printing a brief or `--show` output to the console. Instead
`docs/agents/scratch.md` states that `~/.claude/projects/`, transcripts and saved tool outputs
alike, holds patient text from every run, outside the scratch census and outside the repository's
cleanup.

A printing ban was declined because the text reaches the same store through the Read tool and
through the briefs themselves, and it contradicts `--show`'s purpose as output read on screen and not
pasted. Deleting the saved tool-output files at cleanup was declined: they are the harness's own
files, outside this repository's authority, and the transcripts would remain.

## Ruling 6 — the writer's identifier self-scan is dropped

The ticket's item 1 is not adopted. The coordinator's step 7 name sweep is the check that owns
identifiers, and it caught the recorded case. A writer self-scan would amend standing rule 6's
"authors do not check their own generated artifacts" with a second exception beside
[ADR 0296](0296-a-coding-writer-grades-its-own-descriptor-agreement-before-hand-off-and-the-coordinator-gates-the-blind-brief-on-it.md)'s
Writer self-grade, and it fails in exactly the recorded case: a writer searching for the source
spelling does not find its own guessed one. Telling writers to make no identifier claim was declined
as solving a problem that cost nothing.

## What this does not reach

The hook reads Claude Code launches only. A Codex pass, and a subagent started from inside a
Workflow script if that route does not pass through the hooked tool, are outside it. Path recognition
is a floor: a temp path or run path spelled in a form the hook does not recognize passes, and a
patient-work brief that never names its run directory owes no route. The existence check does not
prove a folder is new, so a staging folder that cleanup missed still passes. Nothing here keeps
patient text out of Claude's session store; ruling 5 declares it instead.
