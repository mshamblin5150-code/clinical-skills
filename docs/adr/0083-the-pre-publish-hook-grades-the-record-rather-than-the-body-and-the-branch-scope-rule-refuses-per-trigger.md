# The pre-publish hook grades the record rather than the body and the branch-scope rule refuses per trigger

[#670](https://github.com/mshamblin5150-code/clinical-skills/issues/670) is
[ADR 0077](0077-a-digest-is-a-redaction-only-where-its-keyspace-is-large-and-a-date-literal-s-is-not.md)
ruling 5's build: a `PreToolUse` hook on Bash that scans tracker text before it is published, on the
one machine where `phi_scan`'s corpus layer is live. Its first comment folds in a second rule —
`tracker_branch_scope` on the same body — and its third relabels the ticket `grilling`, because that
second rule's posture was justified by a ruling that does not reach it.

Grilled 2026-08-30. **Five rulings, made by the clinician on that date.** Nothing is built here;
this is the record the build reads.

## What the grilling found that the ticket did not

**Every claim below was measured rather than reasoned, and three of them contradict the ticket.**
The instruments were throwaway scripts under `scratch/`, so **nothing committed re-derives these
figures** and each is a dated floor. The build may want the two censuses as `tools/` modules; that
is its call and not this record's.

**1. The hook's option space is four values, not two.** In Claude Code 2.1.241 a `PreToolUse` hook
returns `hookSpecificOutput.permissionDecision` of `allow`, `deny`, `ask` or `defer`, plus an
optional `additionalContext` described as *text injected into model context*. Plain stdout on exit 0
reaches the transcript and not the model, so the ticket's *reports a finding to the agent* has
exactly one spelling. ADR 0077 ruling 5's *advisory* is satisfiable as written and nothing here
reopens it.

**2. A hook matcher cannot express the verb list the ticket writes.** The matcher is a **tool name**
pattern — `"Bash"`, `"Edit|Write"`, or empty. A separate per-hook `if` field takes permission-rule
syntax and is described as a cost guard: *"Only runs if the tool call matches the pattern. Avoids
spawning hooks for non-matching commands."* The recognized set therefore lives in `if` or in code,
never in `matcher`.

**3. `grade_text` is not a body-only equivalent of `grade`, and the gap is two thirds of the rule.**
It hard-codes `labels: []`, `number: 0` and `event_name="issue_comment"`, so the `in flight` trigger
is structurally dead. Graded across the whole tracker at a freshly fetched `origin/main` — 705 issues
and pull requests, 2,854 comments, 3,559 records, counts only:

| trigger | firings |
| --- | ---: |
| the issue is labeled `in flight` | 239 |
| repo-relative Markdown link | 87 |
| text self-declares completion | 22 |
| unresolved path with a same-directory near miss | 5 |
| **total** | **353 of 3,559 — 9.9%** |

**A body-only check is clean on 239 of those 353 — 68% — and fires where the authoritative grade is
clean exactly zero times.** `grade_text` is purely permissive: it misses, it never false-alarms.

**4. The module has four triggers and this thread named one.** The repo-relative Markdown link rule
is the second largest at 87 records, it fires **before any git call**, and it is the other half of
the defect #670's first comment describes — the form #672's pull request body carried. Every account
of that module in the ticket omits it.

**5. The ticket's premise about where a body sits is right about half the population.** Across 1,340
transcript files in every `clinical-skills` checkout, 9,032 `gh issue|pr|api` invocations: 6,775
reads, 383 matched verbs carrying no body flag, and **1,874 publishes**. Of those, 605 are an inline
heredoc and 304 an inline quoted string — **909, 49%, free from the command string**. The rest are
file-backed, and splitting the 1,028 `--body-file <path>` publishes further:

| | |
| --- | ---: |
| variable assigned in the same command string, resolvable by a parser | 359 |
| literal path, not written in this command | 345 |
| literal path **written by an earlier stage of the same command** | 195 |
| variable assigned outside this command | 129 |

The 195 is a **floor** — the predicate looks for the path after a redirect in the same string and
misses a program invoked with an output flag. Those files do not exist when a `PreToolUse` hook
fires, and at read time an unwritten body and a mistyped path are the same `ENOENT`. So the honest
residue is **at least 335 of 1,874, roughly one publish in five, where the hook recognizes a publish
and cannot read what is being published.** *The common case needs no file read at all* is 49%, not
the common case.

**6. The ticket's first comment has its staleness direction inverted.** `_default_branch_paths`
shells `git ls-tree -r --name-only origin/main`. A stale ref holds **fewer** paths, so a citation
that has landed upstream is absent from the tracked set and reads as unresolved — a **false alarm**,
the restrictive direction. The permissive error is the one the comment lists second.

**7. The last Done-when row is not decided by where the file lands.** Project hooks are gated on
workspace trust — `shouldSkipHookDueToTrust`, whose only trace is a debug log reading *"Skipping …
hook execution - workspace trust not accepted"*, reaching neither the agent nor the transcript.
Trust is **per directory**, and a worktree is a new directory. Measured in one machine's
`~/.claude.json`: 138 project entries, 72 trusted and 66 not, with **all 60 `clinical-skills`
directories trusted, including all 58 worktree entries**. The gate has never bitten this repository
and every untrusted entry belongs to another project. That makes the row true today for a reason
nobody chose, and it is `skills_mirror`'s failure with the report removed — silently absent, no
`--repair`, nothing that says so.

## Ruled 2026-08-30

**1. The pre-publish check grades the record, not the body, and a context-blind grade is declared
rather than silent.**

Finding 3 is the whole argument: a body-only check reports clean on 68% of what the published
workflow fails, so shipping one would rebuild the ticket's own subject inside its fix. The hook reads
the issue number from the command, fetches `number,labels`, and grades the real record.

The repository's *no tool here opens a socket* rule is about `tools/` modules that must stay offline
and testable. It does not reach a hook that fires on a `gh` command, and the ticket had already
conceded the boundary: its own comment requires the hook to refresh or declare the staleness of
`origin/main`, and a `git fetch` is a socket.

**When the fetch fails or the command names no number, the hook grades body-only and says so in the
same breath** — naming the triggers it could not evaluate. That is `phi_scan --layers`' arrangement
applied to a second scanner: the report states which layers ran, and a dark layer is named rather
than netted into the result. A context-blind clean must never be readable as a full verdict.

**2. The recognized publish set lives in a tested module, and an unrecognized `gh` call is a third
outcome rather than an absence.**

`if: "Bash(gh *)"` is the cost guard only; the classification is a module-level tuple in `tools/`
with a test that fails when it moves. Under a verb list in `settings.json`, **a publish route outside
the list never reaches code that could report it** — `gh issue close --comment` publishes, the hook
never spawns, and nothing appears anywhere. That is this repository's extractor-coverage rule failing
in its named direction: *a matcher never gets to turn a partial read into a clean whole*, and the
remainder must be reportable on every run. A list in `settings.json` has no run to report on and no
test that can fail.

Three outcomes, not two: **scanned**; **recognized no publish form**, silent, which is `gh issue view`
and the overwhelming majority; and **recognized a publish form and could not read its body**, which is
loud. The set carries `gh issue close --comment` and the `gh api` write forms on day one — both are
documented publish routes in `docs/agents/issue-tracker.md` and both are outside the ticket's verbs,
and #130 records four comment bodies destroyed through the second.

**A route is recognized per invocation and never per subcommand.** The same verb both publishes and
does not: `gh issue edit` carries a body in one call and only a label in the next, and 383 measured
invocations of matched verbs carry no body flag at all. What makes a route recognized is a
body-bearing flag. **A title is a publish surface too** — `tracker_scan.records_from_github` makes a
title and a body two records deliberately, *so a finding says which of the two a reader has to go and
edit* — and 32 measured publishes carry a title and no body flag.

**3. An unreadable body is resolved where the resolution is mechanical, and the residue is reported by
class with the remedy named.**

At the measured rate a uniform loud notice fires on nearly one publish in five, which is the rate this
repository already ruled on for `review_hint` and `read_text_if_text`: *a warning printed on every
clean commit is one that stops being read*. Silence is refused without argument. So the population is
shrunk first, and the three groups are not one thing:

- **A variable assigned in the same command string** is resolved by a parser reading plain
  assignments. A `$(...)` substitution is a separate call the hook may decline, and declining is
  stated rather than folded into a miss.
- **A body written by an earlier stage of the same command** is not *I could not find it*; the hook
  can see the write. It is a statable rule with a statable remedy — the publish and the body-write
  are one command, so nothing can scan in between.
- **A variable assigned outside the command, and a body arriving on a pipe**, are beyond reach and
  small.

Each residue class emits one `additionalContext` line **naming the command the agent can run itself
before retrying**. That is the only limb that closes the residue: it converts an unreadable body from
a hole in coverage into a scan the agent performs, which is ADR 0077 ruling 5's *a value goes up with
a decision recorded* reaching the case where the hook cannot make the decision.

**4. The branch-scope rule refuses per trigger, and the two remote-dependent triggers degrade with the
fetch.**

ADR 0077 ruling 5 does not transfer and the ticket's third comment is right about why: no PHI, no
one-for-one false block, and a remedy that is a line of text rather than a ruling about a patient, so
no adjudication lane has to exist for the block to be clearable. **The argument for refusing is in the
module's own declared limits**: `tracker_branch_scope.NOT_REACHED` row 1 is *publication precedes the
check … it is a backstop and cannot intercept the original write* and row 2 is *an advisory finding
may go unread*. A refusing pre-publish hook retires both; an advisory one retires only the first —
and row 2 is what the ticket's first comment is a report of, eight red runs unread, found by a person
saying the pull request had an error.

The four triggers split along whether they need the remote, and that falls out of `grade`'s control
flow rather than being arranged:

| trigger | needs `origin/main` | posture |
| --- | --- | --- |
| repo-relative Markdown link | no | **refuse** |
| `in flight` label | no | **refuse** |
| self-declares completion | no | **refuse** |
| unresolved path | yes | refuse while the fetch succeeded |
| same-directory near miss | yes | **advise, always** |

The three local triggers are **348 of the 353 measured firings** and each has a remedy that is right
every time. The near miss is the one whose own message tells the author to fix the slug, which is a
judgment and is wrong when the slug is right and the file simply has not merged. **When the fetch
fails the two remote-dependent triggers drop to advisory and say so**, because finding 6's error runs
in the restrictive direction and a refuser on a stale tree refuses correct text; the other three need
no remote and keep their posture.

**Two costs are named here rather than left to be found.** A refuser cannot refuse what it cannot
read, so ruling 3's residue gets a notice where a readable body gets a block — the rule is strictly
weaker on exactly the publishes it can see least. And this makes the branch-scope half **stricter than
the PHI half of the same hook**, which reads as backwards to anyone who has not read ADR 0077 ruling
5's measurement. It is right: the PHI half has no remedy the agent can apply alone.

**5. The configuration is committed under a default-deny `.claude/`, and the hook's own
non-registration is reached by a dated marker.**

`.claude/settings.json` is committed. Hooks from user, project and local settings all run — only a
managed-settings flag suppresses the non-managed ones — so the project block adds to the user block
rather than replacing it. `.gitignore` gains `.claude/*` with `!.claude/settings.json`: today
`.claude/settings.local.json` and `.claude/live-retrieval-log.jsonl` are untracked **and unignored**,
one `git add -A` from a public repository, and default-deny with one exception is the posture
`scratch/` and `output/` already have. `TheNetDoesNotSwallowWhatIsCommitted` walks `git ls-files` and
fails if a tracked file is ignored, so the negation is held by a test that already exists.

**A hook that never ran cannot report that it never ran**, which is ADR 0077 ruling 5's *make the
hook's own failure loud* meeting the one failure it structurally cannot make loud from inside. So the
hook writes a dated marker and `phi_scan` states that marker's **age** on the commit path — ruling
6's arrangement whole, in `shortfall_notice`'s home and not `layer_report`'s, for the recorded reason
that the hook runs the scanner bare. Every session that publishes also commits, so the notice reaches
the one person who can accept a trust dialog. **It names no threshold**, on ruling 6's argument
verbatim: what makes the marker stale is how much was published since, not how many days passed.

## Consequences

**One build, on one ticket, and none of it is built here.** #670 is respecified against these five
rulings; its body's premise sentence is corrected on finding 5, its first comment's staleness
direction on finding 6, and its Done-when rows rewritten.

**Three findings are their own tickets rather than folded in**, because none is about a pre-publish
hook: the two unignored files under `.claude/`; `tracker_branch_scope`'s fourth trigger being absent
from every account of that module in #670; and one machine's `autoMode` environment block asserting
private visibility for this repository, which `gh repo view` contradicts.

**Ruling 1 is the one to read before touching any of it.** A body-only pre-publish check is the shape
the ticket's own comment specifies, it is what a rebuild reaches for first because `grade_text`
exists and takes a string, and finding 3 is the measurement that it reports clean on more than two
thirds of what it is being built to catch.

## What none of it reaches

The GitHub web UI, which no hook binds. A session started with hooks disabled or with `--settings`
overriding the project block, where the marker only ages. The retained pre-edit revision of any
edited record, permanently, per
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212).

**And the trust gate itself.** 60 of 60 is a floor from one machine's `~/.claude.json`, not a property
of the mechanism: the 61st worktree is one unaccepted dialog away from a hook that is silently absent,
and the marker's age is a notice at commit time rather than a guarantee at publish time.
