# A publication in an unmodeled shell is refused and the tool roster is keyed by shell

[#1124](https://github.com/mshamblin5150-code/clinical-skills/issues/1124) was filed on 2026-09-11 by
[ADR 0183](0183-the-publish-hook-reads-only-an-inline-value-it-can-reproduce.md) ruling 7, which
found the `PreToolUse` matcher registered for `Bash` while the harness carries a second
command-running tool, ruled that *"not a form the hook misreads, it is a tool it is not registered
for"*, and split it from [#1123](https://github.com/mshamblin5150-code/clinical-skills/issues/1123)
as its own subject. The ticket asked three things: whether the matcher widens or the surface is
declared out of scope, whether `tracker_publish_hook` must learn PowerShell quoting, and whether the
argv-list and `implementation_map` routes belong here.

Grilled 2026-09-12 to an empty frontier. **Ten rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads.

## Measured before ruling, at `500eaba` and re-derived at `084152c3`

Freshness gate `FRESH` at `500eaba` before any reading. It reported `STALE` mid-session; `main` had
gained `scratch_census` work and two ADR citation repoints, touching none of
`tools/tracker_publish_hook.py`, `.claude/settings.json`, `.github/workflows/tracker.yml`,
`docs/adr/0183-*.md` or `CONTEXT.md`, so every measurement below stands on both bases. The branch was
fast-forwarded and the gate re-run `FRESH` before anything was written.

### The ticket's central claim, settled live rather than inferred

The ticket reasoned from `.claude/settings.json`'s matcher. Byte-identical command, two tools, run
against a body file that does not exist so that `gh` reads it and errors before any API call:

| tool | result |
| --- | --- |
| `Bash` | hook denies — `NOT SCANNED -- unreadable body (missing-file)`; the command never runs |
| `PowerShell` | no hook; `gh` runs and errors on the file |

**The instrument discriminates.** Had the hook fired for `PowerShell`, it would have printed the same
refusal, because the two commands differ in nothing but the tool that carried them.

### The population

Counted over 2,209 transcript files under this account's `~/.claude/projects/`, 457,425 JSON lines,
0 unreadable, 2026-06-22 to 2026-09-12. Counts only. **Dated floors over a population that moves
while it is read**, and larger than the ticket's on every row because the window is wider — the
ticket measured 2026-08-09 to 2026-09-11 and reported 441 / 78 / 45.

| | blocks carrying a command | containing `gh` | publications |
| --- | ---: | ---: | ---: |
| `Bash` | 72,607 | 14,854 | 3,949 |
| `PowerShell` | 1,016 | 206 | 54 |
| `Monitor` | 38 | 10 | 0 |

**Three command-carrying tool names, not two.** `Monitor` is named by neither hook and by no ticket.

### The mechanism is not the one the ticket diagnosed

The ticket frames the remedy as a quoting problem, and decision 2 asks whether the hook must learn
PowerShell's rules. Driving `tracker_publish_hook.extract()` over the 54 measured publications says
otherwise:

| outcome | count |
| --- | ---: |
| the extractor sees no publication at all, and `handle` allows | **39** |
| refused as unreadable | 7 |
| read correctly, text recovered | 3 |
| read correctly, no body or title on either side | 5 |
| **read wrongly — a value returned that differs from what PowerShell delivers** | **0** |

**Thirty-nine fail before quoting is ever consulted.** The dominant idiom guards the body file, and
`gh` then sits inside a brace block — `shell_reader.is_command_prefix` does not read it as command
position, and `RAW_PUBLISH_ROUTE` requires `\A` or one of `;&|` before `gh`. A build that registered
the matcher *and* taught it PowerShell quoting would still allow 39 of 54 silently.

**And there are no wrong reads, for a reason that is luck rather than a property of the reader.** 42
of 49 body-file paths are double-quoted, and a double-quoted Windows path survives `shlex` intact.
The 7 bare ones mangle — `C:\dir\file.md` becomes `C:dirfile.md` — and all 7 refuse, because the
mangled spelling fails to resolve. A bare backslash path whose mangled form named a real file would
be read wrongly and silently. The shape is live and no instance is in the corpus.

### The same miss is larger on the tool the hook does cover

- **262 of 3,949 `Bash` publication blocks return `route=None`** — the hook runs, recognizes no
  publication, and allows. `gh` in a function body, after `then`, inside a brace group. Same shell,
  tokens present in the command as typed.
- **718 `Bash` publication blocks carry two or more `gh` publications** (534 with two, 103 with
  three, 81 with four or more); `_publish_tokens` returns the first and the rest publish ungraded.
  `PowerShell` has **zero** of these, so the chained-publication risk is entirely a `Bash` property.

Both belong to [#1107](https://github.com/mshamblin5150-code/clinical-skills/issues/1107), the second
already recorded on its thread with live evidence on 2026-09-11.

### What CI does and does not reproduce

A reframing was proposed during the grilling and **falsified**: that a publication the hook never
sees is graded late rather than ungraded, because `.github/workflows/tracker.yml` is event-keyed and
therefore publisher-indifferent. The workflow is live — 200 runs read, median verdict latency 21s
(14–36s), so ADR 0099's *"one minute after the fact"* is honest — and the conclusion is still wrong.

**Rows CI cannot reproduce at all:** every title row, both corpus PHI rows, the citation readback,
the AAR quotation gate, the verdict discriminator, the unreadable-publication refusal, and the
bodyless-issue-create refusal. That is not a residue.

**Rows on which CI is *stricter* than the hook:** the PHI shape layer under a synthetic pragma,
`branch:in-flight`, `branch:near-miss`, `branch:unresolved-path` under a failed fetch, `filed-from`
loss under a failed readback, and the #596 producer stamp on a command route. **Anyone reasoning
*hook ⊇ CI* drops real coverage.**

And enforcement is off, measured: `{"protected": false, "required": {"checks": [],
"enforcement_level": "off"}}`. ADR 0083 records eight red runs going unread.

## Ruling 1 — a publication written in a shell the command reader does not model is refused unread

Not graded and not allowed.
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
ruling 1 refuses a publication whose text cannot be read; a shell whose delivered bytes the reader
cannot reproduce is an instance of that and not a new rule. ADR 0183 ruling 1 already states the
condition — *"The hook may grade an inline value only where it can reproduce what the shell will
deliver"* — and says nothing that makes the property belong to a quoting construct rather than to a
grammar.

**The alternative was a second shell grammar**, and it is refused in *Alternatives refused* below.

**The remedy is always available**, which is what makes this a gate rather than a wall. A body file
is a file either shell can read. The one case that is not — a body built from a shell variable in the
same command — resolves to *write the file in that shell, publish from `Bash`*, two commands. There
is no publication in this repository's workflow that cannot be reissued.

**`tracker_publish_hook` reads `tool_name` for the first time.** It has never read it: `handle`
consumes `tool_input.command` and nothing else, and `PowerShell`'s `tool_input` is field-identical to
`Bash`'s. So the one-line matcher widening the ticket's decision 1 describes as cheap does not produce
a hook that is merely unhelpful — it produces one that reads PowerShell bytes with bash's rules and
returns a decision, with nothing in the module able to notice. That is the ticket's own *what must not
come out of this*, reachable by the change it prices at one line.

## Ruling 2 — classification and reproduction are separate capabilities and take opposite anchors

A classification miss is a **silent pass**; a classification false hit is a **refusal whose remedy is
one retype**. A reproduction miss is a wrong value published as though it were read. The two
therefore take opposite safe directions, and the module holds two anchors rather than one:

- **The modeled path classifies precisely and grades**, because a hit there means text predicates
  run. Its anchor is untouched by this record.
- **The unmodeled path classifies loosely and refuses**, because a hit there means a retype. Its
  anchor admits `{`, `(` and a preceding compound keyword, and reaches **54 of 54** measured
  publications.

**The two are not copies of one rule and a test asserts they disagree** in the documented direction.
This repository's recorded failure is a second copy of one rule drifting from the first; two rules
encoding different decisions is a different thing, and the way to keep it different is to pin the
disagreement rather than the agreement.

**Loosening the modeled path's anchor is out of scope and belongs to #1107**, whose *Order of repair*
states that repairing its finding 2 widens its finding 1 and that the two must be settled together.
The unmodeled path has no such tension because it has no grading state to corrupt.

**ADR 0096 ruling 2 is unchanged.** The refusal is bounded by `PUBLISH_ROUTES` and by nothing wider; a
read-only `gh` call in any shell is left alone. A body-bearing flag is what makes a route recognized,
with `gh issue create` the declared body-less exception, per ADR 0083 ruling 2.

## Ruling 3 — the tool roster is keyed by shell, and an unmodeled value refuses by default

`COMMAND_TOOLS` maps a tool name to the shell its command is written in. An unmodeled value is what
routes a tool to ruling 1, so a tool added to the roster with that value refuses from the day it is
added, without anyone writing a branch.

**Registration names tools one at a time.** A wildcard matcher is priced out twice: roughly one
second per invocation, measured at 633–1311ms over five runs, against 73,661 measured
command-carrying tool calls — and the hook denies a payload with no `command` field today, so a
wildcard would deny every file read until ruling 7's branch exists. The docs are explicit that a
single `if` rule matches one tool's calls, so each tool gets its own handler entry.

## Ruling 4 — roster completeness is reported and never prevented, and its detector is its own module

**There is no shape that makes the roster a refuser.** Only a wildcard matcher could refuse a tool the
roster has never heard of, and ruling 3 priced that out. So the honest statement ships with the
mechanism: a session publishing through a tool nobody has named still publishes, and learns at
session end.

**The detector is a new module on a second `SessionEnd` entry, not a limb of `aar_scan`.** Access to
the transcript is convenience, not ownership: that module's subject is an after-action review of a
scoped clinical skill's submission, and — decisively — **it ignores subagent sessions by design**.
`PreToolUse` fires inside subagents, confirmed empirically by hook denials recorded in this session's
own subagent transcripts, and this repository fans out constantly, so a detector inheriting that
blindness would report clean about the population most likely to carry the new tool.

**A declaration alone was refused.** A hand-kept roster in `NOT_REACHED` is the arrangement under
examination: `PowerShell` has been in this harness throughout, the matcher named `Bash` because that
is what its author had in front of them, and the gap surfaced only when a grilling counted
transcripts by hand. Under `CONTEXT.md`'s **Declared limit**, a limit is owed a check that fails when
it stops being true.

## Ruling 5 — the roster's scope is tools this repository's hooks read a command from

So the `PostToolUse` matcher widens with it. `implementation_map_post_hook.py` imports
`tracker_publish_hook.gh_command_tokens` and `command_tokens`, reads the same
`payload["tool_input"]["command"]`, reads no `tool_name`, carries the same `Bash` matcher, and
declares limits naming the web UI, Codex and outside-session merges and **no tool surface**. One
defect wearing two registrations.

**Its remedy is not the publish hook's.** That hook never refuses, so its unmodeled branch says what
it did not derive rather than deriving nothing in silence. Measured: 22 `PowerShell` blocks ran a
command it is meant to observe — 16 `git push` toward the default branch, 4 `gh pr merge`, 2 ready
flips.

**The argv-list and `implementation_map` routes are filed rather than widened into.** They share the
consequence and not the cause: neither supplies a `gh` token any command-string reader could find, so
nothing decided here reaches them. 13 measured ad-hoc argv-list publications bypassed both the
command matcher and `authorize_issue_body`.

## Ruling 6 — a false refusal is acceptable at any rate, and the rate is reported and never gated

ADR 0183 ruling 2 accepted refusing **942 of 960** measured titles on exactly this reasoning: *"The
quoting rule's miss is a false refusal whose remedy is one pair of quotes."* The asymmetry here is the
same one — a miss is a publication that reached the tracker unscanned and cannot be withdrawn, a
false hit is a retype — so a stricter bar for this refuser than for the one ratified the day before
would be the tree holding two standards for one mechanism.

**The discriminating bar was the alternative and it collapses.** Requiring the loose anchor to fire on
no non-publication means teaching it enough PowerShell to know a token inside `@'…'@` from one in
command position, which is the grammar ruling 1 refuses. So it reduces to this ruling or to *declare
and close*.

## Ruling 7 — `Monitor` runs bash and joins the modeled path, and registering it has a prerequisite

`Monitor`'s own contract says *"The script runs in the same shell environment as Bash"*, so the
existing reader is the right reader and no grammar is added. Its documented worked example polls
`gh api` in a loop, so publication from a `Monitor` is a live idiom.

**The prerequisite is a code change, not a tidy-up.** A `ws` `Monitor` sends a payload carrying no
`command` field, and today that denies with `HOOK FAILURE: analysis failed (ValueError)` under the
reason line *"tracker branch-scope text must be corrected before publication"* — a reason that is not
the cause. The hook returns an empty response for a payload with no command string before `Monitor`
is registered, and the misattributed reason is repaired with it.

**Registering it is honest and it is not coverage.** `Monitor` scripts are loops and functions, which
is the shape producing #1107's 262 blocks, so it joins the modeled path and inherits that path's
command-position hole.

## Ruling 8 — the `PowerShell` and `Monitor` entries carry no `if`, and `Bash(gh *)` stays

The `if` field is permission-rule syntax evaluated by Claude Code, so **a guard that drops the
population is invisible to every check this repository can write**. Measured, `Bash(gh *)` reaches a
`gh` after `cd … &&` and after `echo …;`, so it is not a strict prefix match — and its reach into a
brace group is unmeasured, which is exactly where the dominant unmodeled idiom puts `gh`. Registering
`PowerShell(gh *)` could therefore drop 39 of 54 before `handle` is called while every test passes.

The cost of dropping it is 1,016 `PowerShell` and 38 `Monitor` measured command blocks over 82 days —
about twelve seconds a day. `Bash`'s 72,607 keep their guard.

**The consequence is accepted rather than discovered**: the hook now runs on every `PowerShell` and
`Monitor` call, including a `Get-ChildItem` and a `ws` `Monitor`, which is why ruling 7's branch is a
prerequisite rather than a nicety.

## Ruling 9 — `CONTEXT.md` gains one term, `Modeled shell`

The property, not the tool. It is what decides grade-versus-refuse, and naming the tool instead would
put the emphasis where this record proves it does not belong — `Monitor` is a second unregistered
tool and takes the opposite answer from `PowerShell`.

**No third sense of *surface*.** That word already carries **Naming surface** and **Enumeration
surface**, both about documents; a tool-shaped third sense would be an unruled fire in
`test_glossary_collisions.DECLARED_CANDIDATES`. The roster needs no term because it is a declared
object and prose pointing at it is already a **naming surface**.

**The classify-loosely / reproduce-precisely asymmetry stays out.** It is ruling 2's subject and it is
a property of two code paths rather than of the domain; `CONTEXT.md` holds no implementation.

## Ruling 10 — #1124 ships before #1107, and its record may not claim the gap is closed

#1107 is `grilling` with its decisions unmade, including an *Order of repair* it says must be settled
before or with its finding 2, so blocking a settled design behind an unsettled one stalls both. The
separability is a property of ruling 1: no grading on the unmodeled path means no contact with the
precision the modeled classifier must keep.

**What the record may not say.** That registering the matcher closes anything. That CI grades it
afterward as consolation — falsified above. That anything here is prevention for a harness this
repository does not control; ADR 0099 ruling 4's declaration is unchanged.

**The honest sentence is that the refusal moves publications onto the covered path, and that path is
measured incomplete**: it allows 262 unrecognized publications, grades one of every chained pair, and
its PHI shape layer can be switched off by a line in the body. Anything warmer rebuilds the ticket's
own *what must not come out of this*.

## Alternatives refused

**A PowerShell grammar in `shell_reader`.** Backtick as escape rather than backslash, `\` as an
ordinary path character, `@'…'@` here-strings, `''` as the embedded-apostrophe escape, `$NAME = value`
assignment, no `&&` in 5.1. It buys coverage of a route nothing needs — the remedy under ruling 1 is
one retype — at the price of a second shell grammar that must stay correct forever. This
repository's recorded failure mode is a parser guessing at a form and failing in both directions, on
grammars far smaller than a shell.

**Declaring the surface uncovered and closing.** ADR 0106's *"a gate would therefore cover one of four
routes while reading as prevention"* is the precedent and it was answered rather than routed around:
the measured route is not one of four but the second of three command tools, its remedy costs one
retype, and the declaration alternative is the arrangement ruling 4 records failing.

**Wiring the existing reader to `PowerShell` unchanged.** It would falsely refuse 5 of 54 — every
measured `PowerShell` title is double-quoted and literal, which the bash reader calls
`expansion-exposed-inline` — and, far worse, allow 39 of 54 while reporting that a hook had run.

**Keying the refusal on the presence of a `gh` token rather than on a route.** Refused by ADR 0096
ruling 2, which bounds the refusal to recognized publications so that it does not become a general
veto over `gh`.

## What none of this reaches

- **A publication through a command-running tool the roster does not name.** Ruling 4 reports it at
  session end and nothing prevents it.
- **The modeled path's own command-position hole**, per ruling 2 — 262 measured blocks, #1107's.
- **A second publication in one command**, 718 measured blocks, #1107's.
- **A latent wrong read of a bare backslash path** whose mangled spelling names a real file. Filed.
- **`Bash(gh *)`'s reach into a brace group**, unmeasured; if it does not reach, some part of #1107's
  262 is the guard rather than the tokenizer. Recorded there as an open measurement.
- **The hook's PHI shape layer under a synthetic pragma.** The hook calls `phi_scan.scan_text`, which
  honors `phi-scan: synthetic`; CI calls `scan_lines(..., True)`, which does not. Re-derived against a
  control. Filed, and filed for a ruling rather than a patch.
- **A publication made with `GITHUB_TOKEN`**, which produces no workflow run at all — 0 of 8 isolated
  bot comments against a 65 of 65 control. The tracker's own merge receipts are graded by neither
  host. Filed.
- **Whether the hook's coverage and the workflow's are what any document says they are.** Nothing
  binds them; every such sentence is prose no check re-derives. Filed.
- **The publish marker's own claim.** `write_marker()` runs after `handle`'s `route is None` return,
  so a session where the hook was never registered and one where every publication was an
  unrecognized shape age it identically. Filed.
- **Every route ADR 0083 already named**: the GitHub web UI, a session with hooks disabled or
  overridden, the workspace trust gate, and GitHub's retained pre-edit revisions.
