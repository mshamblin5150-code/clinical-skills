# A gh api call is graded left alone or refused as unclassified

[#1111](https://github.com/mshamblin5150-code/clinical-skills/issues/1111) found that
`tracker_publish_hook._api_grade_route` ends in `return ("issue", "edit")`, so a non-GET `gh api`
call to an endpoint the route table does not name is graded as an issue edit. A read-only
`gh api markdown --input -` render is then refused as an unreadable pipe body, and an inline render
is allowed under a route that asserts more than the reader knows. Grilled 2026-09-14 against
`9770b1a0`; the clinician ruled every point below on the same day. Nothing is built here; this is
the record the build reads.

## Measured before ruling

### The fallback carries more than the ticket names

Driven in process through `_api_grade_route` and `extract` at `9770b1a0`. Every non-GET call below
resolves to `("issue", "edit")`: `markdown`, a GraphQL query, a GraphQL mutation carrying its comment
text inline, a GraphQL mutation carrying it in a `body` variable, a `gist` create, and
`/issues/N/labels`, `/issues/N/reactions` and `/issues/N/dependencies/blocked_by`. A GET to an
unnamed endpoint, `user`, returns `None` through
[#1084](https://github.com/mshamblin5150-code/clinical-skills/issues/1084)'s method limb.

The fallback is doing hidden work in both directions. The `body`-variable mutation is graded only
because the variable happens to be named `body`. The inline mutation's text sits inside the
`query=` value, which `extract` never reads, so it publishes as an issue edit with no body. And
`gh api markdown --input /nonexistent.json` is refused as `missing-file` on an endpoint that
publishes nothing.

### ADR 0231's GraphQL sentence names the wrong mechanism

[ADR 0231](0231-an-unreproduced-publication-is-refused-unread-and-every-gh-command-reaches-the-hook.md)
ruling 5 says `gh api graphql -f query=…` stays a read because the precise reader's own route and
method judgment decides. `_api_method` resolves that call to `POST`, because `-f` carries
parameters; the call is allowed only because the fallback grades it as an issue edit with no body.
The outcome that ruling states is right and becomes true by the stated mechanism once ruling 2
below is built. The same record's *133 of the 168 are `gh api` calls the precise reader's own method
judgment treats as reads* may rest on the same reading; nothing here re-derives that population.
ADR 0231 is not edited, on ADR 0225's ground.

### The population

Counts only, over every `Bash`, `Monitor` and `PowerShell` tool command in the session transcripts
under `~/.claude/projects/`, measured 2026-09-14 by the recording session with one instrument, so
this is not an independent re-derivation. 2,358 files, 0 unreadable, 77,035 commands, 1,613
`gh api` occurrences of which 162 did not tokenize and are unread. A dated floor over a population
that grows while it is read.

| class | method | occurrences |
| --- | --- | ---: |
| `/issues` or `/pulls` path | GET | 1,069 |
| `/issues` or `/pulls` path | non-GET | 83 |
| GraphQL, query inline (127) or from a file (1) | non-GET | 128 |
| GraphQL mutation | non-GET | 0 |
| any other endpoint | GET | 159 |
| any other endpoint | non-GET | 11 |

The 11 are 5 `markdown` renders and 6 branch-ref writes under `git/refs` or `refs`. Among the 83,
the shapes the route table's patterns do not match are dominated by
`/issues/N/dependencies/blocked_by` and its variable-number variants, 25 occurrences, and by a comment
edit whose identifier is a shell value — `$CID`, `$id`, `$cid`, `${IDS[$n]}` — 10 occurrences. Every
one resolves to issue edit today.

**The first version of the instrument could not see a mutation.** It read the endpoint as the first
positional token and stopped, so a `-f query=` flag after `graphql` was never reached and every
GraphQL call counted as a query whatever it said. After the repair 127 queries carry an inline value;
had one opened with `mutation`, the mutation row would be nonzero.

On the unmodeled path, 12 `PowerShell` commands name the `api` subcommand and
`_loose_publish_route` refuses 3, all GraphQL reads. The ticket's PowerShell comment reproduced a
`markdown` refusal through an in-process `handle` call rather than a live command.

### Text reaches an issue or pull request page outside those paths

Reported by a research subagent from docs.github.com and taken as a claim: check-run output is shown
on a pull request's Checks tab, a commit status is shown on the pull request, and GitHub's comments
guide lists a comment on a commit within a pull request as a kind of pull request comment. GitHub
Discussions are writable over GraphQL only. No ruling below depends on which of these holds; ruling 1
is chosen so that none has to be enumerated.

## Ruled 2026-09-14

### 1. A non-GET call is graded, left alone, or refused as unclassified

A `gh api` call that is not a read takes one of three outcomes. An endpoint the route table names is
graded as that route. An endpoint on a named non-publication list — `markdown` and the branch-ref
paths among the measured calls — is left alone, the same as a read. Any other non-GET call is an
**unclassified API call** and is refused unread. The `return ("issue", "edit")` fallback is removed.

**Keeping only publication endpoints graded and leaving the rest alone was declined**: it passes a
commit comment, a check run or a status carrying text to a pull request page ungraded, and a missed
publication cannot be withdrawn while a false refusal costs a retype, which is ADR 0188 ruling 6's
asymmetry. **Grading a named set of pull-request-page text endpoints was declined**: the next endpoint
nobody listed passes the same way.

### 2. A GraphQL query passes and a mutation is refused unread

`graphql` is a recognized endpoint. A document whose operation is `query`, or the anonymous `{…}`
shorthand, is a read. A `mutation` is an unclassified API call, and its remedy names `gh issue`,
`gh pr` or the REST `/issues` and `/pulls` endpoints. A query supplied where the reader cannot read it
is judged as an unreadable body is: a file the reader resolves is judged by its contents, and anything
else is refused.

**Grading a mutation whose text arrives in a `body` or `title` variable was declined**: it is the
variable-binding reproduction ADR 0231 ruling 1 declined, where a miss publishes unread text as though
it were read. **Admitting a named set of text-free mutations was declined**: a second list for a use
nobody has made.

### 3. An unnamed tracker path is listed text-free or refused

An `/issues` or `/pulls` path the route table does not name takes ruling 1's rule. Text-free
sub-resources — dependencies, sub-issues, labels, assignees, reactions, lock, requested reviewers —
are on the non-publication list. Any other unnamed tracker path is refused as unclassified, including
the text-bearing review-comment reply, review submission, review dismissal and merge commit message
until the route table names them.

**A generic tracker route that scans `body` and `title` without route-specific rules was declined**:
it is a second fallback asserting a route the reader did not establish. **Keeping the issue-edit
fallback for tracker paths was declined**: it runs issue-edit rules on records that are not issue
bodies.

### 4. A shell value in the identifier position is reconstructed or refused

A route's shape is matched with any single path segment where its record identifier sits. A value
assigned in the same command is substituted, by the reconstruction
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
ruling 3 applies to a body-file path. A value the command does not assign — a loop variable, the
result of an earlier call — makes the call unclassified, and its remedy is to type the literal
identifier.

**Accepting the shape with an unknown number was declined**: readback would report the record
unresolved and the Filed-from preservation rule would report `NOT GRADED`, so an issue edit written
through a variable could strip that line unrefused. **Requiring a literal even when the command
assigns it was declined**: it is stricter than the body-file rule for no measured reason.

### 5. The unmodeled path is unchanged

`PowerShell` keeps
[ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)
ruling 2's loose refusal: any `gh api` carrying a publication flag is refused unread and told to
retype through `Bash`, `markdown` and GraphQL queries included. #1111's PowerShell comment is that
ruling working as written, not this defect.

**Teaching the loose path the non-publication list was declined**, and so was teaching it to read a
GraphQL operation: each buys back a few retypes and adds a silent pass on the path built so that a
misread is a refusal.

### 6. `CONTEXT.md` gains **Unclassified API call**

It sits beside **Unreproduced publication** and **Unreadable body**, and covers the three refusals of
rulings 1 to 4: an endpoint neither named nor listed, a GraphQL mutation, and an identifier the command
does not let the reader reconstruct. **Publish route**'s `gh api` sentence now says the method and the
endpoint decide together. **A separate term for the non-publication list was declined**: it is a
mechanism, not a concept anyone reasons with apart from the refusal.

### 7. One ready ticket, and no dependency edge to #1107

#1111 is retitled to carry the term and respecified as one `ready-for-agent` ticket covering rulings
1 to 4. Its four refusal shapes are one rule, so they are not split. It shares `extract` with
[#1107](https://github.com/mshamblin5150-code/clinical-skills/issues/1107)'s build and no decision
with it: if #1107 lands first, `gh api markdown --input -` stays refused through the pipe limb until
this lands; if this lands first, #1107's precise-reader-wins rule respects it. Whichever merges second
rebases. **A hard edge was declined**: it would assert a dependency no decision carries.

## Taken as conventions, not ruled

- The list's home, its exact endpoint expressions, and each unclassified remedy sentence are the
  build's.
- `--command-file` inherits every ruling through the function it shares with the hook route, per
  [ADR 0216](0216-a-pre-grade-grades-the-exact-publication-command-and-the-aar-quotation-gate-runs-on-it.md)
  ruling 6.
- An explicit `-X GET` remains a read whatever flags accompany it, as #1084 left it.
- ADR 0231 is not edited, on ADR 0225's ground.

## Consequences

- `_api_grade_route` loses its fallback and gains the non-publication list, the GraphQL operation
  judgment and identifier reconstruction; `extract` stops reading bodies for a listed endpoint.
- `tracker_publish_hook.UNREADABLE_REMEDIES`, or the build's equivalent, gains remedies for the three
  unclassified shapes.
- `tracker_publish_hook.NOT_REACHED` gains rows for the list being a floor — an endpoint GitHub adds
  later is refused until named — and for a GraphQL document assembled at run time.
- Tests pinning today's issue-edit result for an unnamed endpoint change deliberately.

## What this does not reach

**A text-bearing endpoint put on the non-publication list by mistake.** The list is a claim that an
endpoint publishes nothing, and a wrong entry is a silent pass.

**What a listed endpoint sends to GitHub.** `gh api markdown` transmits its text to GitHub's servers
and publishes nothing to the tracker; the hook's subject is tracker publication.

**Every non-GET shape.** The census is a floor: 162 occurrences did not tokenize, and a shape nobody
has sent is refused rather than measured.
