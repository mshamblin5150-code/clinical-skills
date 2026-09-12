# A harvest verdict drops the line number and a clean harvest needs a denominator

[#918](https://github.com/mshamblin5150-code/clinical-skills/issues/918) was filed on 2026-09-06
because `tools/tracker_scan.py --harvest` reports 29 records carrying a finding and exits 1, while
`reference/tracker-scan-rulings.json` holds **16** verdicts on the commit surface and **0** on the
harvest surface. Seven sweep comments followed. The ticket asked four things: whether the harvest
surface is triaged at all, what a harvest verdict is keyed on, whether the count marker should
record a composition, and whether `--harvest` should recur.

Grilled 2026-09-11 to an empty frontier. **Eight rulings, by the clinician, on that date.** Nothing
is built here; this is the record the build reads.

## Measured before ruling, at `8d7204a`

Freshness gate `FRESH` at `8d7204a` before any reading.

**The mechanism is built and unused.** `HarvestRulingKey(record, line, rule, line_sha256)` at
`tools/tracker_scan.py:221-225`, schema-validated at `:508-523`, applied in
`partition_ruled_findings` at `:546-553`. `reference/tracker-scan-rulings.json` is `version 2` with
`commit_findings` 16 and `harvest_findings` 0. *Had the harvest surface been triaged,
`harvest_findings` would be non-empty; `len(...)` printed 0 while `commit_findings` printed 16 from
the same load, so the instrument distinguishes a populated array from an empty one.*

**The repository and its tracker are PUBLIC.** `gh repo view --json visibility` returns
`{"isPrivate": false, "visibility": "PUBLIC"}`. Every record `--harvest` reads is already-published
text, which is the fact the ticket's PHI posture was decided without.

**`--show` prints the matched value and nothing around it.** `phi_scan.Finding.render` at `:494-496`
prints `path:line [rule] match`; the default redacts to the first character. The *digest* is of the
containing line, which `--show` never prints.

**Nothing anywhere prints `line_sha256`.** It is computed at `tracker_scan.py:674-677` and consumed
only internally. A ruler must recompute `sha256` of the containing line, matching
`record.text.splitlines()` boundaries and UTF-8 encoding, with no way to check the answer.

**An unmatched ruling row is not reported.** `partition_ruled_findings` returns cleared findings and
`main` appends `("ruled findings", len(ruled))` at `:873-874`. Nothing counts rows that matched
nothing. *Under the negation the report would carry a row-side count; it carries only the
finding-side one.*

**The marker is written from the unruled list.** `main` reassigns `findings, ruled =
partition_ruled_findings(...)` at `:870-872`, then calls `write_harvest_marker(repo, findings)` at
`:876`. So a completed triage of all 29 rewrites `reference/tracker-scan-harvest.json` to
`"finding_counts": {}` — byte-identical to a harvest of a tracker that never carried a finding.

**`finding_counts` has no programmatic reader.** Written at `tracker_scan.py:730`, read at
`phi_scan.py:1029` only to refuse a malformed marker; the returned notice spends `age` and `ran_on`
and prints no count. Its real consumer is git history: the 2026-09-12 sweep recovered `34` with
`git show 064257a:reference/tracker-scan-harvest.json`, and that recovery is what established three
prior sweeps had graded a true body sentence as falsified — now
[#1121](https://github.com/mshamblin5150-code/clinical-skills/issues/1121).

**A CI harvest can never write the marker and never runs the corpus layer.** The write is gated at
`:875` on `not missing`; `scratch/` must never reach a runner, so CI must pass `--allow-no-corpus`,
leaving `missing` non-empty. Already pinned by
`test_tracker_scan.test_a_corpus_incomplete_run_preserves_the_previous_marker`.

**Every harvest file has an exact population denominator, and it is derived independently of the
paginated read.** Measured live, serially:

| surface | route | observed | exact or bound |
| --- | --- | ---: | --- |
| `issues?state=all` | GraphQL `issues.totalCount` + `pullRequests.totalCount` | 500 + 621 = 1121 | exact |
| `issues?state=all` | highest issue/PR number | 1121 | exact today, a bound as a rule |
| `issues/comments` | REST `Link rel="last"` at `per_page=1` | 4376 | exact |
| `pulls/comments` | no `Link` header; population is 0 | 0 | see ruling 6 |

Three `--paginate` runs, one sample each, checked against those denominators: `issues` exit 0 with
1121 records, `issues/comments` exit 0 with 4376, `pulls/comments` exit 0 with 0. **All three
complete, and all three agree with a denominator derived independently of them.** That is one
sample and not a refutation of [#993](https://github.com/mshamblin5150-code/clinical-skills/issues/993),
but it is the first sample in that evidence set that could be *checked*, because until now no
denominator existed.

**Numbering is gap-free, and the arithmetic is the evidence rather than the sample.** 500 + 621 =
1121 exactly, which holds only if numbering runs unbroken from 1. Seven numbers probed in one call
resolved and **1122 returned `NOT_FOUND`**, so the probe discriminates and the positives are not
vacuous.

**`Link rel="last"` semantics, measured against independently established populations.** Sizes from
GraphQL `comments{totalCount}`, the header from REST — two independent instruments:

| issue | true comment count | `Link` present | `rel=` values | `rel="last"` |
| ---: | ---: | --- | --- | ---: |
| 1119 | 0 | no | — | — |
| 1084 | 1 | no | — | — |
| 918 | 7 | yes | `next`, `last` | 7 |

Neither falsifier appeared — the exactly-1 population emitted no header and the 7 population did,
with `rel="last"` equal to the true count. **Absent `Link` at `per_page=1` means population <= 1;
present means >= 2 with an exact count.** At `per_page=100` the header is still emitted —
`issues/comments` returns `rel="last"` at page 44 — but yields a bound of 4,301 to 4,400 rather
than a count, so the exact denominator requires `per_page=1` specifically.

**#993's `rel="last"` correction is narrowly true and has been read too widely.** That correction
says the header does not exist *on the issues endpoint*, which the measurement does not contradict.
`issues/comments` carries it. The inference drawn from the correction on that thread — that REST
offers no independent denominator — is false for two of the three harvest files. The issues-endpoint
half was not re-derived here and remains #993's measurement rather than this record's.

**Weak corroboration that the ticket's own figure rests on a complete read.** The three files total
**5497** records today. The body reports *"5,382 records"* on 2026-09-06 — 115 more over five days,
the right order for this repository's comment volume, where #993's measured truncations returned 67
and 151. Consistent-with, not proof-of.

**`Ruling` is already a defined term meaning something else.** `CONTEXT.md:295` defines it as *a
ratified ADR decision identified by its record and its ordinal*. `tracker_scan.py` uses the same
word for a human judgment on a published finding, in `RULING_VERDICTS`, `RulingKey`, `RulingError`,
`load_rulings` and the committed filename `reference/tracker-scan-rulings.json`. The collision is
live today and appears in neither `CONTEXT.md` nor `test_glossary_collisions.DECLARED_CANDIDATES`.

## Ruling 1. An agent may read the harvest surface, rule only what it can positively classify, and escalate the rest

`--show` on the **harvest surface only** is readable by an agent. Not the corpus, not `--history`
blobs, not any other surface. The ground is that the harvest surface is already-published public
text, so reading it publishes nothing; the ticket's *"the triage is the clinician's"* was decided
without that fact stated.

An agent may write a `noise` verdict whose `reason` names the **kind** of thing matched and never
the literal, which is the discipline `tracker_scan.py:105-112` already states. Anything it cannot
positively classify as non-identifying it does **not** rule: it reports the record locator and stops.
The rule therefore fails toward escalation rather than toward a verdict.

`RULING_VERDICTS` stays the closed `{"noise", "accepted-history"}`. An escalated occurrence carries
no row and stays exit 1; an occurrence judged to be a real identifier is remedied by editing the
record, which changes the digest and removes the finding from the surface. No third value is needed.

## Ruling 2. The verdicts proceed now and the clean exit is what waits for a denominator

A harvest verdict is keyed on a record and the digest of a line. Ruling one record is a judgment
about that record and does not become wrong if the read that surfaced it silently dropped another —
that record is simply unruled and surfaces on the next harvest. **The verdict is
population-independent.**

Reading the post-triage **exit 0** as a statement about the tracker is not. A short `--paginate` read
is a valid payload, so the report's `title records` and `body records` counts are the size of what
was handed to the command and never an independent denominator.

So `blocked` comes off #918, and the dependency it declared on #993 is split rather than dropped:
the verdicts land, the clean exit waits for ruling 6. The 16 commit verdicts were taken against
`git rev-list`, which has no pagination and needed no such gate, so nothing asymmetric is being
introduced.

## Ruling 3. The harvest key drops the line number, and the harvest row schema drops it too

`HarvestRulingKey` becomes `(record, rule, line_sha256)`. `RulingKey` stays four-field.

The digest is content-addressed on the containing line, so editing that line expires the ruling —
correct, and the failure is safe. The line **number** is not a property of the finding: adding one
sentence anywhere above a ruled occurrence expires every ruling below it in that record with the
ruled text untouched, and the finding returns with nothing saying it is a return. That assumption is
sound on the surface the ledger was built for and unsound on this one. **A commit's line numbers are
immutable and therefore part of a finding's identity; a tracker record's are not, while its line
content still is.**

This repository's own process is what makes it bite: sweeps append comments, respecs rewrite bodies,
[ADR 0169](0169-a-ticket-states-what-filed-it-on-an-append-only-line.md) ruling 9 adds Filed-from
lines, and [#802](https://github.com/mshamblin5150-code/clinical-skills/issues/802) mechanically
rewrote four comment bodies. Under the four-field key, 29 verdicts decay on ordinary activity and
rebuild [#264](https://github.com/mshamblin5150-code/clinical-skills/issues/264)'s defect inside the
mechanism built to retire it.

`_ruling_fields` stops validating `line` for the harvest surface. A retained `line` would be an
informational hint that goes stale on the first edit above it, and a stale hint in a public file is
worse than no hint where the locator and digest already identify the occurrence.

The `Counter` accounting is unchanged: two occurrences of the same line content in one record still
require two rows, and one row still clears exactly one of them.

## Ruling 4. The marker records totals split ruled and unruled, and the ledger records composition

`finding_counts` becomes per-rule `unruled` and `ruled` counts, and gains the population from
ruling 6.

This answers decision 3 in the negative, and only because ruling 2 populates the ledger. The
premise *"the marker records a count and nothing records a composition"* was true while
`harvest_findings` was empty. Populated, **the ledger is the composition record** — one row per
occurrence with a verdict and a prose reason a reader can open, which is strictly more than a
count-shaped field carries. Putting composition in the marker as well would be one figure in two
places neither of which fails when they disagree, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) and
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) together.

The split is not a preference. Today the marker prints `{}` for both *36 detected and all ruled* and
*nothing was ever detected*, which is
[ADR 0151](0151-the-citation-author-date-split-is-evidenced-by-the-reference-list.md) ruling 1
verbatim — an instrument that prints the same thing whether the claim is true or false settles
nothing. The report escapes this because `ruled findings 29` prints in its context block; the marker,
which is the durable half, does not.

**`finding_counts` is not withdrawn**, though nothing reads it programmatically and ADR 0151's
response to a non-discriminating instrument was withdrawal. Its problem is that it cannot
discriminate, not that it has no use: its git history is what settled #1121 four days ago, and
withdrawal would destroy that.

## Ruling 5. The ledger gains a write side and a reconciliation side

A draft mode emits candidate rows carrying `record`, `rule` and `line_sha256`, with `verdict` and
`reason` blank. Those three fields are exactly what the committed ledger already publishes, so a
draft carries no matched value and is pasteable on
[ADR 0077](0077-a-digest-is-a-redaction-only-where-its-keyspace-is-large-and-a-date-literal-s-is-not.md)
ruling 3's existing terms. Without it, a ruler hand-recomputes 29 digests and a wrong one fails
silently.

The report gains a permanent line counting **ruling rows that matched nothing**. This is the half
that outlives the triage: ruling 3 reduces the decay without removing it, because a ruling still
expires when the ruled line's own content is edited, which is the correct behavior. Without that
line, a ledger slowly filling with dead rows reads exactly like a ledger that is working — the same
non-discrimination ruling 4 refuses one artifact over.

## Ruling 6. The denominator enters as another input file, and the marker carries it

`tracker_scan` opens no socket. That is `research_ledger.py`'s ruling adopted whole, and its ground
here is testability and re-scannability: the harvest is a thing a reader can keep and re-scan, and a
socket costs both. So the denominator arrives the way the harvest does — a documented `gh` command
whose output is a file, passed in alongside it.

Four mechanics:

1. **Denominator first, harvest second.** Then `harvest_count >= population` is complete, and
   records added mid-read are harmless. Taken the other way round, ordinary growth during a
   multi-minute harvest reads as an overcount. This direction can report a false *short* if a record
   is deleted mid-run and never a false *complete*.
2. **Per file, not aggregate.** `issues` takes the GraphQL sum; each comments endpoint takes
   `Link rel="last"` at `per_page=1`, which must be `per_page=1` because `per_page=100` yields a
   page-count bound rather than a count.
3. **Absent `Link` is an exact denominator, not a blank.** Absent at `per_page=1` means population
   <= 1, and that probe's own array length is 0 or 1, so the pair is exact. `pulls/comments` is
   therefore gradeable at its present population of 0, and exit 0 clean stays reachable. *The array
   length inference is derived from `per_page` semantics plus the observed empty body and is the one
   limb of this table the build confirms rather than inherits.*
4. **The marker carries the population** beside `finding_counts`. Recovering `34` from `git show` is
   what settled #1121; recovering a bare count next time would settle nothing.

A count the read itself supplies is not a denominator. #993's truncation is **positional**, so a
short payload may or may not contain the highest number, and an instrument reading its own possibly
short output cannot detect its own shortness.

## Ruling 7. No recurrence mechanism is built, and the existing age notice is the trigger

[#260](https://github.com/mshamblin5150-code/clinical-skills/issues/260)'s ruling stands: the
tracker-event trigger covers the incremental path and the full harvest belongs to the corpus-bearing
clone. CI is out permanently — two of three layers dark and the marker unwritable — and the
recurrence signal already exists, since `phi_scan.tracker_harvest_notice` prints the marker's age on
every commit.

The counter-evidence is recorded rather than buried: the marker has not been rewritten since
`3cc99f2` on 2026-09-06, so five days passed with that age line printing on every commit and nobody
acted. It is still not a cadence. Setting one means naming a number of days at which a stale harvest
becomes a finding, and there is no measurement here to ground one — a value named at an edge, which
is `SPACE_ADVANCE_FRACTION`'s recorded failure and
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s objection.

What made the age line ignorable is more likely the 29 unruled findings beside it that nobody could
act on. Rulings 1 to 6 remove those, so **the notice is re-judged after the triage rather than
replaced before it.** A marker still going stale once a harvest reads `unruled 0` is a new and
better-grounded ticket.

## Ruling 8. Two glossary terms, and the `Ruling` collision is declared rather than resolved here

`CONTEXT.md` gains **Finding verdict** for the scanner's sense and **Population denominator** for
the property #993's consumers share and have no shared word for.

The collision between **Finding verdict** and the existing **Ruling** is recorded by the distinction
clause and the `_Avoid_` row in the `Finding verdict` entry, and by a new
`test_glossary_collisions.DECLARED_LIMITS` row naming the ceiling that hides it.

**It does not go into `DECLARED_CANDIDATES`, and the grilling got that wrong before measuring it.**
This record first ruled it into that object on `CLAUDE.md`'s *"an inventory, never a gate: a new fire
is unruled until a person classifies it"*. Driven, that object gates **both** directions:
`candidate_headings` over the edited `CONTEXT.md` returns 13 fires against 13 declarations with
`undeclared fires: []` and `declared not firing: []`, and
`test_every_fire_has_one_human_verdict_and_every_row_still_fires` asserts it. A declaration that
fires on nothing fails the suite.

Neither new term fires at all. `candidate_headings` fires only where a **bare** heading's word is
reused by a compound, and `CONTEXT.md` has no bare `Verdict` and no bare `Population`.
`DECLARED_LIMITS` row 1 already declares that ceiling for two compounds sharing a word. **What it
did not declare is a pair sharing no word**, which is exactly this one: `Ruling` and `Finding
verdict` have no token in common, so no predicate over headings can see the collision however close
the senses are. That row is added, with this pair as its confirmed instance.

So the classification stays a separate clinician decision and nothing mechanical is claimed to be
holding it — which is the honest form, and is weaker than what this record first said.

**The mechanism is not renamed.** Renaming to match the glossary would move a committed filename,
four type and constant names, the docstring, `CLAUDE.md` and `docs/agents/issue-tracker.md`, and the
16 existing rows would survive untouched — a wide diff for a naming fix, taken before the collision
has been classified.

*Harvest surface* and *unmatched ruling row* stay out. Both are implementation detail, and
`CONTEXT.md` is a glossary and nothing else.

## What the build verifies

- `HarvestRulingKey` is three-field and `RulingKey` is four; a ruled harvest finding survives an
  edit **above** it and expires on an edit **to** it, both driven.
- `_ruling_fields` refuses a harvest row carrying `line`.
- The marker discriminates all three of *detected and unruled*, *detected and ruled*, and *never
  detected*, driven through `main` rather than through `write_harvest_marker`.
- The report carries the unmatched-row count, driven by a row with a deliberately wrong digest.
- The draft mode's output contains no matched value, driven by a marker pushed through a finding.
- A harvest whose record count is below its supplied population cannot exit 0 clean; one at or above
  it can; an absent population file is its own not-scanned limb.
- `pulls/comments`-shaped input: absent `Link`, array length 0, graded complete.
- Ruling 6 mechanic 3's array-length inference, confirmed with one live `--jq length` call rather
  than inherited from this record.

## What this record does not settle

**Any verdict on any occurrence.** Ruling 1 says who may read and under what constraint; it rules on
none of the 29, and no figure in this record is a claim that any of them is noise. What is measured
is that the corpus layer returned zero, which is a weaker statement — and weaker still than the
ticket's heading suggests, because that instrument prints zero for a corpus date rendered outside
`phi_scan`'s declared US-numeric, written-English and ISO families, which is
[#261](https://github.com/mshamblin5150-code/clinical-skills/issues/261)'s residue.

**Whether the 2026-09-06 harvest was complete.** The 5497-against-5382 arithmetic is corroboration
and not a denominator; that read has no kept population file and never will.

**#993's own defect.** Nothing here fixes `gh api --paginate`. Ruling 6 makes one consumer able to
detect a short read; the other consumers that thread names are untouched.

**Whether `rel="last"` is absent on the issues endpoint.** Inherited from #993's measurement and not
re-derived here.

**Whether #993's correction was measured against an empty population.** `pulls/comments` emits no
`Link` header because it has 0 records, which in header terms is indistinguishable from an endpoint
declining to emit `rel="last"`. Filed separately.

**Whether the GraphQL exit status can be trusted.** A counting call exited 1 while returning
complete, correct data for every resolvable alias, the status coming from `NOT_FOUND` errors where
`issue(number:)` was handed pull-request numbers — the same container-and-surface split
`tracker_bodies.py` records for `gh issue list`, and the inverse of #993 on the same toolchain.
Filed separately; nothing in #918's scope reads GraphQL.
