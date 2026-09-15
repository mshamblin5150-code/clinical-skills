# An unreproduced publication is refused unread and every gh command reaches the hook

[#1107](https://github.com/mshamblin5150-code/clinical-skills/issues/1107) found that a publication
the publish hook's command reader does not recognize is allowed with no grader run at all, and that
the raw fallback refusing some of them also refuses scripts that publish nothing.
[#1147](https://github.com/mshamblin5150-code/clinical-skills/issues/1147) found the same consequence
for a publication issued as a Python argv list. Grilled 2026-09-14 against `90b16be0`; the clinician
ruled every point below on the same day, including folding #1147 into #1107. Nothing is built here;
this is the record the build reads.

## Measured before ruling

### The harness guard drops nested commands before the hook runs

The `Bash` hook entry carries `"if": "Bash(gh *)"`, which Claude Code evaluates before the hook is
called. Each probe below was a live `gh issue comment` whose `--body-file` named an absolute path that
does not exist, so `gh` fails before any request. Every shape was first driven through
`tracker_publish_hook.extract()` offline and refuses there, so a probe that ran unrefused could only
mean the hook was never called; had the hook run, each would have been refused.

| shape | hook called |
| --- | --- |
| the publication alone (control) | yes |
| `{ cd … && gh …; }` | yes |
| `f(){ cd … && gh …; }; f` | yes |
| `if …; then cd … && gh …; fi` | yes |
| `for …; do cd … && gh …; done` | yes |
| `( cd … && gh … )` | yes |
| `sh -c 'cd … && gh …'` | **no** |
| `bash <<'SH'` whose body is `cd … && gh …` | **no** |
| read-only `python - <<'PY'` holding the string `cd … && gh …` | **no** |

Two consequences. The command-position hole #1124's census counted in compound blocks is the
tokenizer's and not the guard's, which settles the measurement [ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)
left open. And no repair inside the hook can reach a heredoc or a `-c` string while the guard stands.
**The last row contradicts the live refusals of read-only Python heredocs recorded on #897 on
2026-09-10**, so the harness's matching has evidently moved since; either way it is a boundary no
check in this repository can pin.

The official hooks documentation says a `Bash(...)` rule is checked against subcommands, `$()` and
backticks, and says nothing about heredocs or `-c` strings.

### What running the hook on every command costs

Medians of seven runs on the maintainer's machine, measured 2026-09-14: bare interpreter startup
68 ms; a stub that decodes the payload and exits on a command without `gh` 175 ms; the full hook on a
command without `gh` 561 ms. The `PostToolUse` implementation-map hook already runs on every `Bash`
call with no `if`.

### The population

Counts only, over every `Bash` and `Monitor` command string in the session transcripts under
`~/.claude/projects/`: 2,351 files, 0 unreadable, 77,465 commands, 2026-06-22 to 2026-09-14. The
figures were produced by a subagent and **re-run** by the recording session with the same instrument,
which is not an independent re-derivation. A dated floor over a population that grows while it is read.

- 180 commands carry `gh` only inside a heredoc body or a `-c` string, measured in an earlier pass.
- A classifier with no anchor adds matches in 99 commands beyond the unmodeled path's anchor, 86 of
  them with `gh` directly after a quote, measured in an earlier pass; the argv-list form matches 25
  commands the text form does not.
- Against the classifier as first sketched, 616 commands would newly refuse: 228 carrying two or more
  publications, 219 with no publication in command position, 168 where the precise reader reaches a
  qualifying call and grades nothing, and 1 other. **It is a ceiling over a classifier the build does
  not use**: 133 of the 168 are `gh api` calls the precise reader's own method judgment treats as reads,
  and ruling 5 lets that judgment win.

## Ruled 2026-09-14

### 1. An unreproduced publication is refused unread

On the modeled path a loose classifier runs beside the precise reader. When it sees a publication the
precise reader did not grade — a second publication in a chain, one in a compound block, a heredoc
body, a `-c` string, or a program — the command is refused with `NOT SCANNED`. That includes a script
that only mentions a publication: a missed publication cannot be withdrawn, and a false refusal costs
a retype, which is ADR 0188 ruling 6's asymmetry on the path it did not govern.
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
ruling 2's bound stands: a command carrying no publish route with a publication flag is untouched.

**Grading more shapes was declined for now**: it is reproduction work, where a miss publishes a wrong
value as though it had been read, and a shape can be graded later without reopening this ruling.
**Declaring the gap was declined**: it rebuilds #1107's own *what must not come out of this*.

This amends ADR 0188 ruling 2, which kept the loose anchor off the modeled path and left loosening it
to #1107.

### 2. Every Bash command naming `gh` reaches the hook

The `Bash` entry drops its `if`. The registered command becomes a stub that decodes the payload and
exits unless the decoded command text contains `gh`; otherwise it runs the full hook. This supersedes
ADR 0188 ruling 8's clause keeping `Bash(gh *)`.

The match is on the decoded text and on the substring: a word-boundary match on the raw payload
misses a heredoc line opening with `gh`, because the newline before it is escaped. A pre-filter
built this way can only let through text containing no `gh`, and no publication can be written
without one.

**Running the full hook on every call was declined** on cost. **Adding guard entries for named
interpreters was declined**: the matching is undocumented, and an interpreter nobody listed would pass
silently, which is the failure ADR 0188 ruling 8 warned of.

### 3. A literal argv list is a publication, and #1147 folds into #1107

The loose classifier recognizes a quoted `'gh'` followed by quoted route words and requires a quoted
publication flag. `subprocess.run(['gh', 'issue', 'comment', '5', '--body-file', 'a.md'])` refuses,
and its remedy is to issue it as a Bash command; `['gh', 'issue', 'view', '5', '--json', 'body']` is a
read and is untouched. A list assembled at run time is invisible to it and is a declared floor beside
the rule, which is #1147's own requirement. **Grading a literal list was declined** on ADR 0096
ruling 3's reconstruct-rather-than-expand ground.

### 4. The implementation-map hook says what it did not derive

When the shared loose classifier finds a ready flip, a pull-request merge or a push toward the default
branch that the precise reader derived no work from, the `PostToolUse` hook emits its existing
*"not derived … inspect the completed command by hand"* context. It still never refuses. ADR 0188
ruling 5 treated the two hooks as one defect wearing two registrations.

### 5. The loose classifier is anchor-free, and the precise reader's judgment wins where it reaches

One classifier serves both paths: any `gh` word followed by a publish route and a publication flag,
wherever it sits. Where the precise reader reaches a call, its own route and method judgment decides,
so `gh api graphql -f query=…` stays a read. **Adding quote characters to the existing anchor was
declined**: it refuses the same mentions and still misses `xargs gh`, `env X=1 gh` and `time gh`.
**Keeping today's anchor was declined**: `-c` strings would stay unreached and ruling 2 would buy
nothing.

### 6. `CONTEXT.md` gains **Unreproduced publication**

It sits beside **Modeled shell** and **Unreadable body**. **Widening Modeled shell was declined**:
that term is a property of a grammar and this is a position inside one command.

### 7. One ready ticket, and no follow-up for grading chains

#1107 is retitled to carry the term and all four shapes and respecified as one `ready-for-agent`
ticket that includes #1147, which closes on this record. The stub and the refusal are one defect's
two halves, so they are not split. No enhancement is filed for grading chained or compound
publications: the remedy is one retype and no measured need asks for more.

## Taken as conventions, not ruled

- The stub fails closed: a payload it cannot decode runs the full hook.
- One remedy sentence names both causes: publish one top-level `gh` per Bash call, and run a script
  that merely mentions a publication from a file.
- The raw `invalid-command` fallback for a nested `cd … && gh` is subsumed by ruling 1, and its
  *repair the command quoting* remedy is retired with it.
- `--command-file` inherits every ruling through the function it shares with the hook route, per
  [ADR 0216](0216-a-pre-grade-grades-the-exact-publication-command-and-the-aar-quotation-gate-runs-on-it.md)
  ruling 6.
- ADR 0188 is not edited, on ADR 0225's ground that whether a superseded record carries a marker is
  [#1201](https://github.com/mshamblin5150-code/clinical-skills/issues/1201)'s open decision.
- The classifier's exact expressions and the stub's module name are the build's.

## Consequences

- `tracker_publish_hook` gains the refusal and the argv-list form; the unmodeled path adopts the same
  classifier.
- `implementation_map_post_hook` gains the not-derived context for the shapes in ruling 4.
- `.claude/settings.json`'s `Bash` entry loses its `if` and registers the stub.
- `tracker_publish_hook.NOT_REACHED` and `implementation_map_post_hook.DECLARED_LIMITS` gain rows for
  the floors below, which settles #1107's finding 3 by adding a limit rather than repairing a false one.
- `test_an_unmodeled_shell_refuses_a_loose_publish_route` asserts today that the modeled path returns
  an empty response for a compound command carrying a publication; under ruling 1 it refuses, and the
  test changes deliberately.
- The build re-measures the refusal population with the classifier it ships and reports it, because
  the figure above is a ceiling over a different classifier.

## What this does not reach

**A command assembled at run time.** `G=gh; $G issue comment …`, a command built by string formatting
inside a program, an argv list built in pieces, and an alias or function standing in for `gh` all
carry no text a static classifier can see.

**A command-running tool the roster does not name**, which ADR 0188 ruling 4 reports at session end.

**The implementation-map direct writer**, which issues no command string and is
[#1148](https://github.com/mshamblin5150-code/clinical-skills/issues/1148)'s.

**The rate of refused mentions.** It is reported and never gated, per ADR 0188 ruling 6; the census
could identify only 17 of the 219 commands without a publication in command position as echoed or
grepped mentions, and did not classify the rest.
