# A run is touched by a write, and a retried status line is graded but never refused twice

**Measured at:** feafce4b6de07059b34b12832d117ea5eae8b838

[#1519](https://github.com/mshamblin5150-code/clinical-skills/issues/1519) was split out of
[#1456](https://github.com/mshamblin5150-code/clinical-skills/issues/1456) by triage on 2026-10-03
and carries two scope questions about `tools/run_status_stop_hook.py`, the check that holds every
reply touching an approved run to a keyed `Run status:` line under
[ADR 0277](0277-the-run-status-check-covers-every-posting-skill-through-one-approval-record.md).
Grilled 2026-10-11 against `main`, where the freshness gate read `FRESH`; the clinician ruled both
points in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Touched means mentioned.** `touched_runs` walks every string value in every transcript row and
treats any match of the run-path pattern as a touch. That reaches command text, tool output, the
assistant's prose and the clinician's messages alike. `DECLARED_LIMITS` states it as *a run is in
scope only after its path appears in the session transcript*.

**It has bound unworked runs four times on record.** Twice in early October a prior shift's run
was opened only to copy course, site and preceptor constants the profile already supplies. On
2026-10-04 a shell listing of `scratch/runs/*/voice-reads/` printed two other runs' names and both
were bound. On 2026-10-11 listing four run directories bound all four. A Claude memory note telling
the agent to copy reference material into scratch first is the only defense, and it has failed twice.

**A retried reply is never graded and never recorded.** `handle` returns `{}` when the harness sets
`stop_hook_active`, which it does on the reply written after a refusal. On 2026-10-11 the retry wrote
`complete` for all four of those runs; calling `completion_is_clean` directly afterwards returned
false for all six approved items. Because nothing was recorded, the next ordinary reply was refused
again, and the correction stuck only when a later ordinary reply happened to carry it.
[ADR 0281](0281-a-command-result-stated-after-a-compaction-is-re-observed-or-labeled-and-a-compaction-hook-says-so.md)
names this ticket as one of three that leave the reply the clinician reads less covered than durable
state. The other two, #1456 and #1495, have closed.

**The early return exists to prevent a refusal loop.** `tools/grilling_stop_hook.py` honors the same
flag for the same reason, and [ADR 0273](0273-grilling-asks-one-question-per-turn-and-a-codex-stop-check-retracts-a-bundle.md)
records it there. This record does not change that hook.

## Ruling 1 — a run is touched only when this session named it in a command and wrote into it

A run binds the sitting when both hold: its directory path appears in the input of a tool call in
this session's transcript, and some file under that directory changed after the session began. The
hook's own `run-status.json` does not count as a change. A path that appears only in tool output, in
the assistant's prose or in the clinician's message touches nothing, and reading a run touches
nothing however it is named.

Keeping the mention rule was refused because reading for reference and listing folders kept binding
unrelated runs, and the 2026-10-11 binding is what pushed a false `complete` out. Counting command
paths alone was refused because it fixes only the listing case: opening a file names its path in the
command. Every step that changes a run's state writes into its directory (the approval record, the
posted reading, the after-action review), so a write is the trace of work the line exists to report.

What it gives up is named: a reply that states the status of a run this session only read is not
checked, and a write by another session into a directory this session named counts as touching it.
Both become rows of the hook's `DECLARED_LIMITS`.

## Ruling 2 — a retried reply is graded, recorded when it passes, and never refused a second time

When `stop_hook_active` is set the hook runs the same grading as for any reply. If the status lines
pass, it records them in `run-status.json` exactly as it does for an ordinary reply. If they fail, it
does not block. It returns a visible warning to the clinician naming each failing line and why, and
it records nothing, so a false `complete` never reaches a run's durable state. The early return is
removed rather than declared as a limit.

Keeping the skip as a declared limit was refused because a false `complete` keeps reaching the
clinician unflagged and a correct retried line keeps going unrecorded. Refusing the retry up to a
fixed count was refused because each refusal costs a full rewritten reply and whatever passes at the
limit needs the same warning anyway. The loop risk stays at zero because a retry is never refused.

## Ruling 3 — a reply sitting owes the line from its first write into a folder with an open approval

Under ruling 1, a `discussion-reply` sitting touches the board's shared run directory with its first
drafting write. When that directory already holds an approval that is not recorded complete, such as
the initial post's, the status line is owed from that write onward, not from the reply's own
approval. `skills/discussion-reply/SKILL.md` step 4's *"From this record onward"* is false under
either rule; the build corrects it to say this. The 2026-10-04 comment on #1519 carries a proposed
diff.

## Build notes

- The session's start is read from the transcript. Where no start can be read, the hook falls back to
  the mention rule for that session, so an unreadable transcript asks for a line rather than releasing
  one.
- The warning in ruling 2 travels as the Stop hook's `systemMessage` with no `decision`. The build
  confirms it is shown in both Claude Code and Codex before relying on it.
- Tests: a synthetic read-only `Read` and a folder listing bind nothing; a command naming a run plus a
  changed file binds it; a change only to `run-status.json` binds nothing; a failing retry returns the
  warning, never blocks and writes no state; a passing retry is recorded.

## What this record does not settle

**Whether a status line is true beyond `complete`.** ADR 0274's residue stands.

**A reply about a run this session only read.** Ruling 1 names it; nothing in the session catches it.

## Supersedes

- [ADR 0277](0277-the-run-status-check-covers-every-posting-skill-through-one-approval-record.md) ruling 4, the words "When one session touches several approved runs". A run is touched only when the session named it in a command and changed a file under it; each touched run still gets its own keyed line.
