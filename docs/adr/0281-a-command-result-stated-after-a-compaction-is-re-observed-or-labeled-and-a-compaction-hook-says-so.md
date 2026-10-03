# A command result stated after a compaction is re-observed or labeled and a compaction hook says so

**Measured at:** 632819dfb89991da40ca6363bf20760cded9e86f

[#1206](https://github.com/mshamblin5150-code/clinical-skills/issues/1206) recorded an orchestrator
telling the clinician an after-action review was clean after a context compaction, when the command
had exited 1 with fourteen findings. The compaction summary kept that corrections were unlanded and
dropped the exit status, and the report came from that summary rather than from a run.
[ADR 0206](0206-a-final-review-follows-a-posted-record-and-every-review-round-keeps-its-own-files.md)
ruling 8 filed it as its own ticket because nothing about it is specific to the review. Grilled
2026-10-03 against `main`, where the freshness gate read `FRESH`; the clinician ruled every point
below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

### A compaction summary is not a source of a command's result

#1206's third decision asked whether summaries systematically drop exit statuses or whether its
instance was one summary. It was measured on 2026-10-03 against the clinician's retained transcripts
by a subagent reporting counts only, and its two headline counts were re-derived by hand before they
were used. Nothing committed re-derives them, because the transcripts are private working material.

- **Population.** Every retained Claude Code transcript, subagent transcripts included, and every
  Codex rollout, live and archived. A compaction is a Claude Code `compact_boundary` entry with its
  `isCompactSummary` turn, or a Codex `compacted` item.
- **Matcher.** In the span before each Claude Code compaction, the last run of each `tools/X.py`
  script was paired with its result by tool id, and its exit status was read from the result's form.
  The summary was then searched for the script's name and for an exit number within 300 characters
  of it.
- **Result.** Claude Code retains 12 compactions. Of the 15 runs whose status was readable and whose
  script the summary named, **1** carried an exit number nearby, and passing and failing runs lost it
  alike. Every one of the 4,664 Codex compactions stores its summary as `encrypted_content`, so no
  reader, a hook included, can check what a Codex summary kept.

**What the instrument would have printed if summaries kept statuses:** an exit number beside most
named scripts. It printed one of fifteen. It cannot separate *drops failing statuses in particular*
from its negation, because only three failing runs fell in the population, and no ruling below rests
on that narrower claim.

The same pass counted statuses stated after a compaction before the command was rerun: none of 72 in
the retained Claude Code sessions, and 74 in Codex, 58 of them positive verdicts on runs whose status
the transcript does not show. Retention has pruned older Claude Code sessions, including, presumably,
#1206's own.

### The decisions that matter already recompute their own result

`run_status_stop_hook.RUN_KINDS` names all seven posting skills, not only `course-assignment` as
#1206's latest comment records. The hook writes `complete` into a run's durable state only after it
re-grades the run. A tracker publication is graded by the publish hook as it goes out, and a merge to
`main` by CI. Each recomputes its result rather than trusting the sentence that reported it.

**The reply the clinician reads is not yet covered as fully as the durable state**, and the
tracker sweep of this grilling found why before merge:

- `handle()` returns early when `stop_hook_active` is set, so a replacement reply written after a
  refusal is never graded ([#1519](https://github.com/mshamblin5150-code/clinical-skills/issues/1519)).
- The hook reads stdin with the locale codec, so on Windows a well-formed status line can be refused
  as malformed, which forces that ungraded replacement
  ([#1456](https://github.com/mshamblin5150-code/clinical-skills/issues/1456)).
- `discussion-reply` and `peer-critique` cannot write the approval record the hook reads, so it never
  sees their runs as open ([#1495](https://github.com/mshamblin5150-code/clinical-skills/issues/1495)).

So an ungraded `complete` can reach the clinician today, while the run stays open in durable state
and the next ordinary reply is graded again.

### Both harnesses expose a hook at the compaction boundary

Claude Code's `SessionStart` hook fires with the `compact` source after a compaction, and this
repository's `SessionStart` registration carries no matcher, so it already runs there. The installed
Codex binary names `PostCompact` and `SessionStart` hook events. Whether a Codex hook at that boundary
can put text in front of the model was not established by reading the binary, and ruling 6 assigns it
to a live test.

## Ruling 1 — the rule covers every command result stated to the clinician

The scope is every command result an agent states to the clinician, in any skill and in maintainer
work: graders, tests, scans, CI, the freshness gate, and any other command. A result that decides a
submission, a publication or a merge is not singled out, because the clinician cannot tell from a
sentence which kind it is, and #1206's instance read as a routine summary line.

## Ruling 2 — after a compaction a result is re-observed before it is stated, or labeled

A result is stated only from an observation made after the last compaction. A read-only command is
rerun. A command that changed something is re-observed by reading back what it left: the posted page,
the record file, the tracker comment. Where neither is possible, the statement says plainly that the
result predates a compaction and has not been re-checked. **The label is the last resort and never
the default.**

**A rerun whose exit status cannot be seen is not an observation.** A command piped into another or
chained behind `;` reports the last stage's status, so rerunning it that way re-observes nothing.
That defect in ordinary work is [#1457](https://github.com/mshamblin5150-code/clinical-skills/issues/1457)'s;
this record only declines to count such a rerun as a re-check.

## Ruling 3 — the rule does not depend on what a summary kept

Ruling 2 binds whether or not a given summary happens to carry the number. The measurement shows a
Claude Code summary almost never does and a Codex summary cannot be read at all, so a rule that
trusted a summary which looked complete would rest on the one source shown not to hold the fact.

## Ruling 4 — enforcement is a written rule and a reminder at the compaction boundary

The rule is written once, and a hook at the compaction boundary injects a reminder into the session:
the summary holds no command result that may be stated, and each one is re-observed or labeled under
ruling 2. In Claude Code it is a `SessionStart` registration for the `compact` source. Whether it is a
branch of an existing session-start module or a module of its own is the build's choice. It fires for
any session that compacts, subagents included, because a subagent's report can carry a remembered
result too. **The reminder's claim is literally true on every firing**, which is what the measurement
buys: no summary is a source a result may be stated from.

## Ruling 5 — no check blocks a reply

No hook refuses or retracts a reply for stating a result. Such a check has to recognize a result
statement in ordinary prose, and the measurement's own verdict-word matching could not tell a pass
from a fail reliably; its false alarms would fall on routine conversation to guard against a failure
that occurred in none of the 72 retained Claude Code cases.

**This includes the go-ahead.** The one unguarded spot is a result reported before the clinician's
go-ahead. A stale pass there cannot be recorded as a finished run, because the run-status hook writes
`complete` into durable state only after a re-grade. A recognizer for go-ahead requests across seven
differently worded skills would be the fuzziest check in the repository, guarding a spot a later gate
already stands behind.

**That later gate is partial until #1519, #1456 and #1495 land**, as measured above: until then an
ungraded `complete` can reach the clinician's reply, and two posting skills are outside it. The
clinician ruled this ruling stands with that stated rather than blocking this ticket on those three
or adding a go-ahead check. The reminder and the written rule do not depend on the gate, and each gap
is already an open defect with its own repair.

## Ruling 6 — Codex is covered, and a live test decides how

The build first tests live whether a Codex hook at the compaction boundary, `PostCompact` or
`SessionStart`, can deliver text to the model.

- **If it can,** the reminder is registered in `~/.codex/hooks.json` by the existing installer
  pattern of `tools/install_grilling_guard.py` and `tools/install_run_status_guard.py`, beside
  existing hooks, replacing only its own registration on a repeat run.
- **If it cannot,** the installer writes ruling 2's text into a marked block in the user-level
  `~/.codex/AGENTS.md` and reports that Codex received the written rule only.

Codex is where the measurement found the shape occurring, so it is not deferred to another ticket,
and the fallback means the build cannot stall on the unknown.

## Ruling 7 — the written rule is standing rule 7 in `AGENTS.md`

Ruling 2 becomes standing rule 7 in `AGENTS.md`, the one file every agent in this repository reads,
Codex included and Claude Code through `CLAUDE.md`. Standing rule 6 already governs how an agent
works rather than what a note contains, so this is not a new kind of standing rule. The Claude Code
reminder points at it, and the Codex fallback writes the same text. A shared reference sheet was
declined because maintainer work never reads one, and a reminder with no written rule leaves nothing
in force between compactions or wherever the hook does not fire.

## Rejected options

**A written rule only.** Nothing reminds at the moment the memory becomes untrustworthy, and a
written instruction cannot fail.

**Re-injecting each command's last status from the transcript at the boundary.** Most last runs
before a compaction have no readable status because of piping or chaining, and the rest are results from before the compaction,
which would look authoritative and invite the same mistake in a new form.

**A reply-blocking check, wide or narrowed to deciding results.** Ruling 5.

**Claude Code only, or Codex as its own ticket.** The harness with no inspectable summaries and the
observed cases would get the weaker fix or wait in a queue.

**Narrowing the scope to deciding results or to clinical and coursework runs.** The clinician cannot
tell which sentence carries weight, and nothing about the failure is specific to a skill: a test or a
freshness gate crosses a compaction the same way a grader does.

## Consequences

**Every result an agent states after a compaction is either freshly observed or visibly labeled.**

**`AGENTS.md` gains a seventh standing rule**, binding consumers and maintainer work alike.

**Both harnesses gain a compaction-boundary registration**, and the Codex branch records which form
it took.

## What this does not reach

**A result stated from memory without any compaction.** A long session can misremember a status it
saw an hour earlier; the reminder fires only at the boundary, and the written rule covers that span
only as an instruction.

**Whether an agent obeys the reminder.** It is an instruction delivered at the right moment, not a
check; ruling 5 declines the check deliberately.

**What a Codex summary keeps.** Its encryption is outside this repository's reach, and ruling 3 makes
the answer unnecessary.

**A piped or chained status in ordinary work.** That is #1457.

**An ungraded `complete` in a replacement reply, or a run in a skill the run-status hook cannot see.**
Those are #1519, #1456 and #1495, and ruling 5's reliance on that hook is partial until they land.
