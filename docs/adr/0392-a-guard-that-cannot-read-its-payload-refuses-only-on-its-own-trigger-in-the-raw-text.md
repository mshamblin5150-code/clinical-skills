# A guard that cannot read its payload refuses only on its own trigger in the raw text

**Measured at:** 5d32d8490b61bba071e0dba6013349aff84d97ad

[#1728](https://github.com/mshamblin5150-code/clinical-skills/issues/1728) was filed from the
grilling of #1520, whose ADR 0340 ruling 5 sent the question to its own ticket: several hooks let
the call or the stop proceed when they cannot read the payload the harness hands them, and no record
rules that. Two later comments widened the population, one of them because
[ADR 0368](0368-a-doubled-backslash-in-a-bash-command-is-refused-because-the-bash-tool-halves-it.md)
ruling 4 deferred its new guard's posture to this ticket. Grilled 2026-10-17 against `main`, where
the freshness gate read `FRESH`; the clinician ruled every point below, one question at a time.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

**What each guard does today with an unreadable payload**, read from each `main` at the commit above:

| Guard | Event | Today |
|---|---|---|
| `heredoc_write_hook` | `PreToolUse` | catches `ValueError`, `OSError`, `TypeError`; a non-object payload gets `{}`; allows with no note |
| `scanner_pipe_hook` | `PreToolUse` | the same catch and the same silent allow |
| `tracker_publish_hook` | `PreToolUse` | catches `UnicodeError` and `JSONDecodeError` and allows with a `HOOK FAILURE` context note and no permission decision; an `OSError` escapes as a traceback, which the harness treats as a non-blocking error |
| `browser_tab_hook` | `PreToolUse` | catches `JSONDecodeError` and `OSError` and returns with no response; a non-object payload is graded as `{}` |
| `run_status_stop_hook` | `Stop` | grades an empty payload; with no transcript named it returns nothing; its `DECLARED_LIMITS` says so |
| `grilling_stop_hook` | Codex `Stop` | grades an empty payload and allows; its limits name malformed transcript rows, not the payload |
| `backslash_pair_hook` | `PreToolUse` | not built; ADR 0368 ruling 4 allows with a visible `backslash check: unread` note pending this ruling |

`tracker_publish_stub` is not a member. It forwards a payload it cannot decode to the full hook
rather than allowing it, and the full hook then allows under the row above. The `SessionStart` and
`SessionEnd` hooks (`compaction_reminder`, `skills_mirror --session-start`, `command_tool_roster
--session-end`) read payloads too, but none of them can refuse anything.

**Only a harness fault reaches these handlers.** Since ADR 0340 was built (PR #1734), every one of
these commands puts stdin on UTF-8 with replacement before `main` reads it, so an encoding error no
longer arrives. What is left is text that does not parse, a parsed value that is not an object, and
a failed read. Nothing in the tree records any of the three ever arriving.

## Ruling 1. A command guard refuses an unreadable payload only when its raw text carries the guard's trigger

When a `PreToolUse` guard cannot read its payload, it searches the raw text it received for the
narrowest literal its own refusal needs. If the trigger is there, it refuses. If it is not, or there
is no text because the read failed, it allows the call with the note under ruling 3.

**Always refusing was declined.** A harness format change would block every guarded call, including
every Bash call, which is the tool the repair would be made with, until someone disables the hook by
hand. **Allowing with a note alone was declined** for the guards whose subject is patient text or a
public record: where the risky literal is present in the raw text, a warning is weaker than the
refusal the guard exists to make. **The rule extends two existing postures** rather than inventing
one: the publish stub already declines to let an undecodable payload through unexamined, and ADR
0096 already refuses a publication whose text cannot be read.

## Ruling 2. Each guard's trigger

- `heredoc_write_hook`: `<<` together with `scratch` or `output`.
- `scanner_pipe_hook`: `|` together with the name of a scanner it guards.
- `tracker_publish_hook`: `gh`, the substring the stub already keys on.
- `backslash_pair_hook`: four consecutive backslashes, because the raw JSON text writes each
  backslash of a doubled pair twice.
- `browser_tab_hook`: no `tabId` anywhere in the raw text, unless the text names one of the family's
  tab-listing or tab-opening tools.

**The browser guard's trigger is an absence**, unlike the others, because its refusal is for a page
action that names no tab. Blocking on every unreadable payload without the exception was declined:
during a fault it would also block the two calls that produce a tab number, so the browser would be
unusable until the fault cleared. Allowing every unreadable payload was declined because a page
action landing in the clinician's own tab is what #1120 guards against. **The declared cost**: a
`browser_batch` in which one action carries `tabId` and another does not passes the raw search, and
the guard's limits say so.

## Ruling 3. The note reaches both the agent and the clinician

A command guard that allows an unreadable payload attaches the note as `additionalContext`, which the
agent reads, and as `systemMessage`, which the clinician sees. **Agent only was declined**: a
long autonomous run could pass many calls with guards reading nothing and the clinician would not
learn that the harness was sending broken payloads, which is a fault for the clinician to report
upstream. **Clinician only was declined**: the agent would treat a call as checked that was not. The
cost is two lines per affected call, for exactly as long as the fault lasts.

## Ruling 4. An end-of-turn check always lets the turn end, with a note

`run_status_stop_hook` and `grilling_stop_hook` never refuse a stop on an unreadable payload. Each
lets the turn end and states in its `systemMessage` warning, the channel both already use, that it
did not grade the turn. Ruling 1 does not apply to them. **Refusing a stop here asks for a retry that
cannot succeed**: the next stop carries the same broken payload, and nothing the agent writes in the
extra turn repairs a harness fault, so ruling 1 could hold the turn open indefinitely. Refusing once
and then allowing was declined because the extra turn costs work and buys nothing.

## Ruling 5. One shared reader

Every member reads its payload through one shared function that takes the guard's trigger and
returns either the parsed record or the unreadable outcome under rulings 1 and 4. The posture is one
policy across the population, so a copy per guard that drifts is the defect this ruling closes,
which is the test [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) states for
when a helper may be shared. A guard added later joins by calling it.

## Ruling 6. Each guard declares its posture, and the build is believed on planted payloads

Each member's `DECLARED_LIMITS` names its unreadable-payload posture, its trigger, and what the raw
search cannot see. Tests drive each member's public command with malformed JSON, a non-object
payload and a failed read, each with and without the trigger present, and assert the refusal, the
allow, and both channels of the note. The browser guard's tests also cover a tab-listing call and a
batch carrying `tabId` on only one action.

## Supersedes

- [ADR 0368](0368-a-doubled-backslash-in-a-bash-command-is-refused-because-the-bash-tool-halves-it.md)
  ruling 4, the words "the hook allows the call and attaches a visible `backslash check: unread`
  note". Under ruling 1 here the hook refuses an unreadable payload whose raw text carries four
  consecutive backslashes and allows the rest with the note. Placing #1728's population under this
  ruling, and declining a silent allow, still stand.
- [ADR 0368](0368-a-doubled-backslash-in-a-bash-command-is-refused-because-the-bash-tool-halves-it.md)
  ruling 7, the words "and malformed and non-object payloads (allowed with the note)". Malformed and
  non-object payloads are tested both ways under ruling 6 here. The other planted payloads and the
  live probe before merge still stand.

## Rejected options

- **Always refuse an unreadable payload.** Declined under ruling 1.
- **Always allow with a note.** Declined under ruling 1 for the command guards, adopted for the
  end-of-turn checks under ruling 4.
- **Keep the silent allow.** It is the defect #1728 was filed over.
- **A posture per guard written separately in each module.** Declined under ruling 5.

## What this does not reach

- **A raw-text search is not a read.** A trigger split by an escape the harness chose, or written in
  a form the literal does not match, is allowed with the note. The search is a floor, and each
  guard's limits say so.
- **The session-start and session-end hooks** are outside the population, because they cannot
  refuse anything.
- **Codex's handling of `additionalContext` and `systemMessage`** for the guards installed there is
  measured at the build, not assumed here.
