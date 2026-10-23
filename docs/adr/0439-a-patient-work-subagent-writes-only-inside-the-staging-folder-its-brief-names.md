# A patient-work subagent writes only inside the staging folder its brief names

**Measured at:** 8f23f034dc54f0c6a6b2f69c360a1ce924168d4e

[#2039](https://github.com/mshamblin5150-code/clinical-skills/issues/2039) was filed from the
after-action review of a `course-assignment` run (NUR 5042 M6), 2026-10-23. Several research and
reader subagents in that run wrote transient files outside their assigned staging folders, or
wrote them by shell redirection, although each brief said to write only in the staging folder and
only with the Write tool. The subagents reported the writes themselves and deleted the files before
returning. Nothing enforced the brief's write rule: the launch hook of
[ADR 0375](0375-a-subagent-launch-hook-refuses-a-patient-work-brief-that-names-temp-or-no-existing-staging-folder.md)
reads the brief before the subagent starts and never sees where the subagent later writes. The
clinician ruled every point below on 2026-10-23, against `main` at the commit above, where the
freshness gate read `FRESH`. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**A subagent's tool calls name the subagent, and its brief is on disk when it first writes.** A
throwaway Claude Code 2.1.306 session, started outside every checkout with an explicit `--settings`
file registering one probe hook on every `PreToolUse`, launched one general-purpose subagent whose
brief carried a marker string and told it to Write a file, Edit it, and redirect `echo` into a
second file. The probe logged field names and true/false facts only, never content:

- The launch call (`Agent`) carried no `agent_id` and no `agent_type`.
- The subagent's `Write`, `Edit` and `Bash` calls each carried `agent_id` and
  `agent_type: general-purpose`.
- Their `transcript_path` named the parent session's transcript. The subagent's own transcript
  was `<parent transcript stem>/subagents/agent-<agent_id>.jsonl`, it already existed at the first
  write, and its first row was a `user` row whose content was a string containing the brief's
  marker, on all three calls.

**No identifier exists at launch to key a record on.** The launch call carries no `agent_id`, so a
record written by the launch hook could not be joined to the subagent's later calls without a
further guess.

**The launch hook scopes patient work by what the brief names.** `tools/subagent_staging_hook.py`
owes a staging route only of a brief that names `scratch/runs/` or `output/`, and extracts the
`scratch/sessions/` folder that brief names.

**Shell reading is a floor that cannot place every target.** `heredoc_write_hook.DECLARED_LIMITS`
records that variables, substitutions and wildcards do not establish where a write lands; that
guard allows such writes because it covers every session.

**Standing rule 6 already sends every finished artifact back through the orchestrator**
([AGENTS.md](../../AGENTS.md)), so a patient-work pass has no legitimate destination but its
staging folder. Scanner `--show` output is a staging-folder file under ADR 0375 ruling 4, and a
pass writes it there by shell redirection.

## Ruling 1 — the fence is the staging folder, wherever the target is

A subagent whose brief names a staging folder may create or edit files only inside that folder.
The guard covers the file-writing tools (Write, Edit, NotebookEdit) and the shell redirections and
heredocs the heredoc guard's reader recognizes, wherever the target lies: `scratch/`, `output/`,
the system temp directory, the session scratchpad, the tracked tree, or any other place. A
subagent whose brief names no staging folder, and the main session, are untouched. Reads are
untouched.

Fencing only `scratch/` and `output/`, the ticket's wording, was declined: it leaves the temp-folder
write from the filing run uncovered, and a stray file in the tracked tree is caught only if
`phi_scan` recognizes its contents at commit. A warning without refusal was declined as the honor
system the ticket was filed over.

## Ruling 2 — the brief is re-read from the subagent's transcript at each write

At each write the guard takes `agent_id` from the payload, opens that subagent's own transcript
beside the parent transcript, reads its first row as the brief, and extracts the staging folder
with the launch hook's existing parser. A relative path resolves as the launch hook resolves it.
Nothing is recorded at launch.

A launch-time record was declined on the measurement above: the launch call carries no identifier
the subagent's later calls share.

## Ruling 3 — an unreadable brief refuses only writes aimed at patient-record locations or temp

When a payload carries `agent_id` but the guard cannot read that subagent's brief (the transcript
is missing, damaged, laid out differently, or its first row is not text), the guard refuses a write
whose target lies inside a checkout's `scratch/` or `output/`, the system temp directory or the
session scratchpad, and allows every other write with a warning naming the failure. This is
[ADR 0392](0392-a-guard-that-cannot-read-its-payload-refuses-only-on-its-own-trigger-in-the-raw-text.md)'s
posture and the clinician's 2026-10-19 ruling for the launch hook, applied one hook later.

Refusing every write was declined: one transcript-reading failure would stall every subagent in
every session, including code and review passes with no patient text. Allowing every write was
declined as the silent escape, in the case where the guard knows least.

## Ruling 4 — a shell write whose target cannot be resolved is refused in a patient-work subagent

When a subagent bound by ruling 1 runs a shell write whose target the guard cannot establish (a
variable, a substitution, a wildcard), the guard refuses it. The refusal names the remedy: spell
the staging folder out literally, which the subagent can always do because its brief names it.

This departs from the heredoc guard's allow posture on purpose. That guard covers every session and
has no single permitted destination; this one covers a context with exactly one. A wrong refusal
costs one retyped command, and a missed write leaves an unrecoverable patient file.
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
refuses a publication it cannot reproduce on the same reasoning. Allowing with a warning was
declined because a subagent that has ignored its brief can ignore a warning.

## Ruling 5 — no tally; the refusal asks the subagent to report it

The guard keeps no record of its refusals, and the orchestrator's run record gains no field for
stray writes. The refusal message tells the subagent to report the refusal in its result, which the
after-action review already reads as a subagent result.

A counts-only tally kept by the guard was declined: it builds a record, a writer and a failure mode
to measure an event that is already prevented. A self-reported stray-write field was declined
because enforcement removes the stray file it would count. If unreported refusals prove to recur,
the review shows them as failing briefs, and a tally can be added then.

## What this does not reach

A Codex subagent, and a subagent started from a Workflow script, were not measured; whether a
Workflow subagent's calls carry `agent_id` and keep a transcript at the measured path is unknown,
and ruling 3 governs if the brief cannot be found. A program the subagent runs that writes files
itself (a script given an output path, `cp`, `mv`) is invisible to a guard that reads command text.
Path recognition in briefs and shell commands remains a floor. A future change to the harness's
transcript layout falls under ruling 3 until the guard is re-measured. A subagent that omits the
refusal from its result leaves no trace across runs; ruling 5 accepts that.

## Done when

A planted subagent write outside its named staging folder is refused and a write inside it is
allowed, through the Write tool and through a literal shell redirection. A subagent with an
unreadable brief is refused on a `scratch/` target and allowed with a warning on another target. A
patient-work subagent's redirection into a variable-built path is refused with the literal-path
remedy. A subagent whose brief names no staging folder, and a main-session write, pass untouched.
The module carries a `DECLARED_LIMITS` object holding *What this does not reach* and the 2.1.306
measurement, and `CLAUDE.md`'s maintainer tooling names the hook and points to that object.
