# A GraphQL read is judged by its payload and every complaint must be a declared absence

[#1126](https://github.com/mshamblin5150-code/clinical-skills/issues/1126) found `gh api graphql`
returning a complete, correct answer with exit status 1, the inverse of
[#993](https://github.com/mshamblin5150-code/clinical-skills/issues/993)'s short read with exit
status 0. Trusting the status and distrusting it are both unsafe, and the repository had no rule for which to
do. Grilled 2026-09-14 against `9770b1a0`; the clinician ruled every point below on the same day.
Nothing is built here; this is the record the build reads.

## Measured before ruling

### `gh` exits 1 whenever the response carries any complaint

Three read-only queries against this repository, 2026-09-14:

| query | exit | `data` | `errors` |
| --- | ---: | --- | --- |
| `issue(number:)` for an issue, `issue(number:)` for a pull request, `pullRequest(number:)` for a pull request | 1 | every alias present; the pull-request number under `issue()` is `null` | one `NOT_FOUND` on that alias's path |
| `issueOrPullRequest(number:)` for an issue, a pull request, and a number past the counter | 1 | the issue and pull request resolved; the absent number `null` | one `NOT_FOUND` on the absent number's path |
| a field that does not exist on `Issue` | 1 | **no `data` key at all** | one error carrying `extensions.code` and no `type` |

So the status cannot distinguish one expected missing member from nothing having been read.
[ADR 0104](0104-the-freshness-gate-s-subject-is-the-commit-base-and-a-publication-s-cited-records-are-read-back-without-a-baseline.md)
finding 8 measured the first half of this and ruled no rule about it.

### `issueOrPullRequest` removes the container split, and not the status defect

#1126's third candidate, refusing the query shape that mixes issues and pull requests, was feared to
forbid the population measurement because the two share one number counter. The second row shows it
does not: `issueOrPullRequest` answers both containers without complaint. A number that exists
nowhere still exits 1 beside a complete answer for the rest, so the shape alone does not settle the
contract.

### Four consumers handled the status three ways

- `implementation_map.GitHub._run` raises on any nonzero status before reading stdout. The
  population probe in `GitHub.issues` and `GitHub.user_content_edits` both go through it, and
  [ADR 0224](0224-the-map-s-views-refresh-hourly-and-a-stale-view-is-reported-rather-than-failed.md)
  runs both hourly.
- `tracker_publish_hook.fetch_readback` passes no `check=`, never reads `errors`, and reads every
  `null` alias as *no such record*, whatever complaint produced it.
- `tracker_population.issue_population`, its documented shell commands, and the `checks.yml`
  implementation-map step never see the status: the redirect or pipe discards it, and only the
  payload's shape is graded.

Every GraphQL route outside `tools/` lands in `tracker_population`, so the committed consumers are
exactly those modules.

## Ruled 2026-09-14

### 1. The payload decides, and every complaint must be a declared absence

A GitHub GraphQL read is complete when every entry in `errors` is a **declared absence**; any other
complaint makes the read not scanned, however much `data` it returned. The exit status is consulted
only when stdout is not JSON. **Keying on the status was declined**: it discards a complete answer
carrying an expected `NOT_FOUND`. **Keying on the presence of `data` was declined**: it is what
`fetch_readback` does, and a `FORBIDDEN` or rate-limited `null` alias reports a record that exists as
one that does not, which is a false negative stated as a fact.

### 2. One pure reader owns the verdict, and callers keep their `gh` call

A stdlib module that opens no socket takes the response text and the caller's declared absences, and
returns `data` with the absences it accounted for or raises a typed error naming every complaint it
could not account for. `implementation_map.GitHub`, `tracker_publish_hook.fetch_readback` and
`tracker_population.issue_population` all pass their text through it. The process call stays with
the caller, which is ADR 0104 finding 9's seam. **Adding it to `tracker_records` was declined**:
[ADR 0157](0157-the-tracker-record-is-typed-and-the-publish-hook-keeps-only-tracker-policy.md)
ruling 2 scopes that module to the typed record, and a population probe is not one. **Stating the rule
in prose for each consumer to implement was declined**: the three postures above are that
arrangement's result.

### 3. A declared absence is an exact type and path, over a null value

A declared absence pairs one error `type` with the full `path` it sits on. The complaint's `path` must
equal the declared one, not begin with it; the value at that path in `data` must be `null`; and a
complaint lacking either `type` or `path` can never be declared, which keeps a schema error and a
rate-limit body always refusing. **Tolerating by type alone was declined**: a `NOT_FOUND` on
`["repository","record_18","labels"]` inside a present record would pass a record whose labels were
never read. Today the readback declares `NOT_FOUND` on each requested record alias, and the population
probe and revision query declare nothing.

### 4. A declared absence sits only on a lookup whose `NOT_FOUND` means nonexistence

For record numbers that is `issueOrPullRequest`. A declared absence on `issue(number:)` or
`pullRequest(number:)` would read a record in the other container as absent, which is #1126's container
split reached through this mechanism, in the direction nothing downstream can see.
**Leaving the choice to the caller was declined** for that reason.

### 5. An AST walk holds the consumers to the reader

Every non-test module in `tools/` whose subprocess command list carries the literal `"graphql"` must
import the reader and pass that call's stdout through it, and no module may declare an absence beside
an `issue(` or `pullRequest(` query literal. The walk is proven live by removing the reader from a
real consumer and watching it fail. **A prose rule alone was declined** on
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s terms. **One runner for
every `gh` call was declined**: most calls are REST, whose status is honest, and it reopens ADR 0104
finding 9's seam.

### 6. Each consumer keeps its refusal posture

The reader decides whether a read is complete; each command's boundary decides what an incomplete
read means for its run, on [#303](https://github.com/mshamblin5150-code/clinical-skills/issues/303)'s
ruling. `implementation_map.GitHub` raises `MapError`, reaching status 2 as
[ADR 0202](0202-a-paginated-read-carries-a-denominator-and-a-short-read-refuses.md) rules for a short
read. `fetch_readback` raises `ValueError`, which its caller already prints as a context-blind readback
without refusing the publication, as ADR 0104 rules for a read with no baseline. `tracker_population`
raises `PopulationError` and exits 2. `_run` stops refusing a GraphQL call on its status alone.
**A uniform exit 2 everywhere was declined**: it would add a refusal reason to the publish hook for a
read that is only context.

### 7. A short response with no complaint is outside the reader

The reader grades complaints and never completeness. Whether a connection returned every node belongs
to the caller's declared denominator, where ADR 0202 put it. **Checking `pageInfo` and `totalCount`
generically was declined**: `user_content_edits` reads a bounded window on purpose and reports its
older remainder, so a generic check would refuse a correct, deliberately partial read.

### 8. The measured responses are the reader's real members

The reader's tests use the three responses measured above as committed members alongside mutants, on
the extractor-coverage rule's terms, rather than only hand-written payloads.

## Taken as conventions, not ruled

- `CONTEXT.md` gains **Declared absence**.
- #1126 is the build ticket. The reader's module and function names are the build's.
- The reader carries a declared-limits object; the walk's literal-shape floor and ruling 7's scope are
  rows of it.

## Consequences

- The hourly map job's two queries declare nothing, so any complaint still fails them; what changes
  is that the complaint is judged from the payload, and a non-JSON response keeps today's message.
- A readback whose `null` alias came from anything but `NOT_FOUND` stops reporting that record as
  absent and prints the context-blind banner instead.
- A saved population probe that carries any complaint beside complete counts stops deriving a
  manifest and exits 2.
- `CLAUDE.md`'s sections for the three consumers name the reader where they describe the read.

## What this does not reach

**A command assembled at run time, a shell or workflow route, or a docstring command.** The walk reads
literal command lists. The routes that exist today are covered only because they all land in
`tracker_population`.

**Whether a complete-looking response is complete.** A response with no complaint and fewer members
than exist passes the reader; only a caller's denominator catches it.

**GraphQL APIs other than GitHub's.** The error vocabulary ruled here is GitHub's.
