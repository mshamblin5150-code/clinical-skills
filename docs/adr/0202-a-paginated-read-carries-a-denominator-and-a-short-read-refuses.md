# A paginated read carries a denominator and a short read refuses

Out of [#993](https://github.com/mshamblin5150-code/clinical-skills/issues/993), grilled on
2026-09-12 to an empty frontier. **Nine rulings, by the clinician, on that date.** Nothing is built
here; this is the record the build reads.

**Measured at:** 58b3bb8c13ca8e2fe850a716a6041a1460fca354

*Re-declared three times on 2026-09-12, from `6380b8a6`, `2f814d1f` and `00bad566`. **Only the
first move touched anything measured here**: it carried `tools/implementation_map.py` and its test,
the artifact most figures below rest on, so every figure was re-derived at that base rather than
carried across — the reads-per-command table, the 12 `DECLARED_LIMITS` rows, the
`clean-check-derived-views` wording, `blocked_by`'s unsized call and the `get_issue` re-validation
path all re-derive unchanged, and the one that did not was wrong when written rather than moved by
the merge, which the correction at the bottom records. The other two moves carried ADR files alone,
so every figure re-derives across them by construction.*

The ticket was filed 2026-09-09 because `gh api --paginate` returns a silently truncated population
with exit status 0, and `tools/implementation_map.py` consumes it as the complete live tracker.
Sixteen sweep comments followed. It asked four things: where the denominator comes from, whether
`publish` refuses or only `check` does, whether the other `--paginate` callers are affected, and what
the cause is.

## Measured before ruling, at `6380b8a`

Freshness gate `FRESH` at `6380b8a` before any reading, and again immediately before publication.

**The denominator exists, is independent of the read, and is exact today.** One GraphQL call returns
`issues.totalCount` 529 and `pullRequests.totalCount` 666, summing to **1195**. Three back-to-back
`gh api --paginate "repos/mshamblin5150-code/clinical-skills/issues?state=all&per_page=100"` runs
returned status 0 with **1195 records each, byte-identical payloads, empty stderr**. Of those, 666
carry a `pull_request` key and 529 do not, matching the two GraphQL figures separately rather than
only in sum. Numbering runs 1 to 1195 with no gap.

**The defect did not reproduce, and that settles nothing.** The thread holds five recorded
truncations across three sessions. Three clean runs are one sample of non-reproduction, which is what
the ticket already says intermittency means. What is new is that this is the first sample in the
whole evidence set that could be **checked**, because until now no denominator existed to check it
against.

**The equality is not a documented contract.** Researched against GitHub's REST reference, live
GraphQL schema introspection, and the transfer and deletion documentation. REST's issues endpoint is
documented as returning both issues and pull requests — *"GitHub's REST API considers every pull
request an issue, but not every issue is a pull request"* — so the identity holds because REST
returns the unfiltered union of the same records GraphQL splits into two disjoint views. Transfer and
deletion move both counts together, threatening absolute numbering rather than the cross-API
equality. **Two divergence classes could not be settled from primary sources: an issue converted to a
discussion, and an issue hidden as spam or abuse.** Neither the GraphQL rate-limit page nor either
connection's schema description carries any caveat that `totalCount` is approximate or capped.

**The module already reads the tracker more than once per command and compares nothing.** Counted by
AST walk over the module at this commit:

| command | full paginated reads today |
| --- | ---: |
| `check`, `claim`, `render`, `audit` | 2 |
| `publish` | 1 |
| `apply-delta --ticket` with `--outcome` | 3 |
| `init` | 2 |

`locate_map` reaching `find_map_issues` is one, `Live.__init__` is another, and
`_direct_placement_delta` is a third. *Had any pair of those been compared, a disagreement between
two reads in one command would already be a truncation signal; nothing in the module reads more than
one of them at a time.*

**Nothing that must be fresh goes through that path.** The post-publication re-validation in
`_publish_under_lock` and `_init_under_lock` reads `get_issue(number)`, a single-record call, not
`issues()`.

**The declared-limits object asserts the soundness the ticket denies.** `DECLARED_LIMITS` holds 12
rows, driven in process. None names a short, truncated, partial or incomplete read, and
`clean-check-derived-views` reads *"A clean check grades the state block against the live tracker."*
*Under that object declaring the ceiling, one of the 12 rows would name the harvest; driving the
object printed all 12 and none does.*

**A second unsized read on the same adapter, not named anywhere on the thread.** `GitHub.blocked_by`
calls the dependencies endpoint with neither `--paginate` nor `per_page`, so GitHub's default of 30
applies. A ticket with more than 30 blockers returns 30 rows, valid JSON, status 0. `Live.__init__`
calls it per mapped ticket and the result feeds the gate findings, so a truncation there reports a
ticket **unblocked when it is blocked** — a false clean rather than a false finding. Four tickets
carry the `blocked` label today, so it is latent rather than live; that label is not the dependency
edge, so it is a weak proxy, and an exact per-ticket maximum was deliberately not measured because
this repository has already tripped GitHub's **secondary** rate limit on that same dependencies
endpoint while `rate_limit` read 5000 of 5000.

**`Link rel="last"` at `per_page=1` is live on two more endpoints than the thread records.** The
labels endpoint returned `rel="next"` and `rel="last"` with a last page of **18**, against
`gh label list --limit 1000` returning **18**. The dependencies endpoint for one ticket returned no
`Link` header at all, which under
[ADR 0184](0184-a-harvest-verdict-drops-the-line-number-and-a-clean-harvest-needs-a-denominator.md)
ruling 6 mechanic 3 means a population of at most one. *Under the header being unavailable outside
the comments endpoints, the labels probe would have printed `rel="next"` alone, which is exactly what
the issues endpoint prints.*

**`tools/tracker_bodies.py` reads the same three harvest files `tools/tracker_scan.py` already
gates** — `tracker-issues.json`, `tracker-comments.json`, `tracker-reviews.json` — and
`tools/tracker_population.py`'s manifest names that exact triple, while `tracker_scan.load_population`
already validates a manifest against a harvest file set.

**The unattended consumer's signal is buried in chronic noise.** `gh run list --workflow checks.yml
--branch main --limit 25` returns **22 failures and 3 successes**, worse than the 19 of 25 the
2026-09-10 sweep recorded, and the step exits with `map_scan`'s status alone, so exit 1 and exit 2
render as the identical red result.

**The refusal-preservation mechanism fires on three write-time refusals and on no read-time one.**
`preserve_refused_outcomes` is documented as *"Persist authored judgment that a refused tracker write
would strand"* and is called from four sites covering three refusal kinds: a busy artifact lock in
`cmd_apply_delta`, a state-hash mismatch surviving three attempts in `_apply_delta_under_lock`, and a
body the publish hook refuses in `publish_body`. **Every one is reached after the read has already
succeeded.** `main` catches `MapError` and prints `did not run`, returning 2, so a refusal raised by
`issues()` — at `locate_map` before the lock, or inside `_apply_delta_attempt` — is caught by none of
the three and strands the authored outcome.

## Ruling 1. The completeness verdict belongs to the read, and every command inherits one refusal

The check lives in `GitHub.issues()`. A short read raises `MapError`, which `main` already converts
to `did not run` and status 2. `check`, `claim`, `render`, `audit`, `publish`, `apply-delta` and
`init` all refuse identically, because all of them derive from that one call.

The ticket's decision 2 asked whether `publish` refuses or only `check` does. Differentiating was
available and is refused on what a reported `check` would contain: the body records three consecutive
runs at one commit returning exit 2, exit 2, and exit 1 with **108 findings, none of which is a fact
about the tracker**. There is nothing in that report worth preserving behind a banner, and a banner
above it asks a reader to hold *here are 108 findings* and *the read was short* at once —
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling pointed the wrong
way, since a reader who learns to read a qualifier reads its absence as the stronger claim.

**The read-only path is not the safe one, which is the half the ticket's own framing understates.**
The 2026-09-09 comment records that a short read missing
[#596](https://github.com/mshamblin5150-code/clinical-skills/issues/596) makes `locate_map` print
*"Run `init` to create one"* — the module's diagnostic pointing at a mutating command, given exactly
when it cannot see the map. That damage is reachable from `check`, before any write is attempted, so
a rule that lets read-only commands report leaves the destructive instruction live.

The cost is named rather than discovered: a single flaky probe now takes down read-only `check` as
well. That is accepted, because what it takes down is the 108 findings.

**One consequence closes a thread item by construction.** The 2026-09-12 comment asks for
`locate_map`'s message to stop being printed about a map that exists. Under this ruling the adapter
raises before `find_map_issues` runs, so that message is unreachable on a short read and reachable
only on a complete read that found no marker, where it is correct. **No wording change is made.**

## Ruling 2. The read happens once per process and the denominator comes first

`GitHub.issues()` probes once, harvests once, and caches the rows for the process lifetime. `check`
goes from two harvests to one harvest and one probe; `apply-delta` goes from three to one and one.
Every command becomes strictly cheaper than it is today, and the run holds exactly one completeness
verdict rather than a property that could differ between two lines of one command.

Three mechanics, the first two inherited from ADR 0184 ruling 6 rather than re-decided:

1. **Denominator first, harvest second, and refusal only on `harvest < population`.** An overcount is
   ordinary growth during the read. Taken the other way round, growth reads as an overcount. This
   direction can report a false *short* if a record is deleted mid-run and never a false *complete*.
2. **The comparison is against the pre-filter row count.** `GitHub.issues()` drops `pull_request`
   rows before returning and the denominator is `issues + pullRequests`, so comparing the filtered
   length would fire the gate on every clean read.
3. **The cache is process-lifetime and needs no invalidation**, because these are one-shot commands
   and the one read that must be fresh — the post-publication re-validation — goes through
   `get_issue` rather than `issues()`.

**What this deletes is named rather than buried.** Today's duplicate reads are an accidental
discriminator: had `locate_map`'s harvest and `Live`'s harvest ever disagreed, the difference would
be proof of truncation with no denominator needed. Memoizing removes it. The trade is taken because
that instrument is one-directional and strictly dominated — two reads that **differ** prove
truncation, two reads that **agree** prove nothing, since a stable short read and two coinciding
short reads both look clean — while the denominator fires in every case.

## Ruling 3. Four consumers, and the harvest command is not consolidated

The build covers four surfaces:

| surface | what it gains |
| --- | --- |
| `implementation_map.GitHub.issues()` | rulings 1, 2, 5, 9 |
| `tools/map_scan.py` and the `checks.yml` step | a required `--population`, and ruling 6 |
| `tools/tracker_bodies.py` | a `--population` reusing `tracker_scan.load_population`, and probes in its documented harvest |
| the `gh label list` overflow branch in `docs/agents/issue-tracker.md` | one sentence naming the measured denominator route |

The body forbids a fix scoped to `implementation_map.py` alone *until decision 3 is measured*. It is
measured now, across the 2026-09-10 and 2026-09-11 comments and ADR 0184, so that gate has lifted.

**`tracker_bodies` is in because it is the PHI surface and because it is nearly free.** The body
singles it out — *"a short harvest there reports fewer findings and exits clean, which is the same
defect on the PHI surface"* — and the manifest, the parser and the loader already exist and already
name those three filenames, so leaving it out would be a decision to keep one of three consumers of
one file set ungated.

**`map_scan` takes `--population` as required rather than optional**, which is `tracker_scan`'s
existing behavior: absent, it prints `DID NOT ESTABLISH the full harvest population` and returns its
did-not-scan status. Making one consumer of one manifest treat it as optional would be two consumers
disagreeing about whether it is needed.

**Consolidating the six duplicated copies of the harvest command is out.** The 2026-09-10 comment
offered it as a [#875](https://github.com/mshamblin5150-code/clinical-skills/issues/875) datum; the
2026-09-10 sweep then measured that #875 was ruled as
[ADR 0165](0165-tests-list-git-paths-through-git-paths-and-no-shared-tree-reader-is-built.md), which
declines any shared tree reader and never mentions `--paginate`. The duplication is taken up in
neither record. The copies that are commands an agent runs gain the probes; nothing is consolidated.

**Finding the cause is out**, on the body's own ground that the remedy does not depend on it, and see
ruling 8.

## Ruling 4. `blocked_by` is sized from the header of the call it already makes

`GitHub.blocked_by` requests `per_page=100` with `--include` and reads the `Link` header. **An absent
header means the population is at most 100 and this page is the whole of it** — the denominator comes
from the same call, with no second request. A present header raises `MapError`, because a ticket with
more than 100 blockers is a thing a person should look at before a tool guesses at it.

That is ADR 0184 ruling 6 mechanic 3's semantics generalised from `per_page=1` to `per_page=N`, and
the generalisation is measured rather than assumed: the labels endpoint emitted `rel="last"` equal to
its true population and the dependencies endpoint emitted no header at a population of at most one.

**This is a widening rather than a filed follow-up, and the test is the artifact.** Ruling 5 commits
this build to a limits row stating what the gate establishes for this module. With `blocked_by` left
out, that row has to read *the issue population is gated and the per-ticket blocker population is
not* — a limits object conceding the module is half-gated, on a gap that costs no extra request to
close.

**The design is forced by the rate limit rather than chosen.** The obvious fix, a `per_page=1` probe
per ticket matching the harvest surfaces, doubles calls on the one endpoint this repository has
already been throttled on. Reading the header off the real call costs zero extra requests and is
cheaper than today's unsized read.

## Ruling 5. There is no way past the gate, and the refusal is diagnostic

No escape hatch. A short read is `MapError` and status 2 on every command, with no flag that converts
it to a banner.

**This is the one place the repository's own precedent does not transfer.** `phi_scan
--allow-no-corpus` and `--allow-untrusted-provenance` are sound because the operator knows something
the tool does not — whether this clone holds a corpus, whether this read was deliberate. Here the
operator knows **nothing** the tool does not: whether a given read was short is precisely the
judgment this ticket establishes cannot be made from the payload. A flag would hand a person a call
they are structurally unable to make, and the first wrong use writes a truncated map into #596 under
an explicit human authorisation, which is worse than today because today nobody claims to have
checked.

Two things make refusing with no door safe:

**The refusal is diagnostic rather than a bare stop.** It prints the population, the harvest count,
the shortfall, and the **highest record number seen**. Those three separate a genuine truncation from
a wrong denominator in one look. ADR 0184 records highest-number as *"exact today, a bound as a
rule"*; as a denominator that is too weak to gate on, and as a discriminator inside a refusal it is
exactly right. At this commit all three agree at 1195.

**Two limits rows.** One names the denominator's ceiling, including by name the two divergence
classes primary sources did not settle — an issue converted to a discussion, and an issue hidden as
spam or abuse — because if the gate ever refuses a healthy tracker, the first object anyone opens
should already name the suspects. And `clean-check-derived-views` is repaired in the same pass: it
currently asserts that a clean check grades the state block *against the live tracker*, which becomes
true under this gate but only in the narrow sense the gate establishes, and the row states which.

## Ruling 6. The unattended consumer's did-not-scan is distinguishable from its chronic redness

The `Implementation map disagreement` step derives its step-summary heading from `map_scan`'s exit
status: the did-not-scan status writes `### Implementation map: DID NOT SCAN` in place of the
existing heading, above the same report.

The 2026-09-10 comment drove the direction that makes this necessary: a short read that keeps #596
**deletes** readiness findings and exits clean, so this gate converts a silent zero into a
did-not-scan. But the step exits with the scanner's status alone, and against 22 failures in 25 runs
a red result means *the usual*. Without this, the one signal meaning *this run established nothing*
is added to the one place where every signal already looks alike.

**The banner precedent is satisfied rather than set aside.** The workflow carries a standing comment
that *a banner typed into YAML is a claim about `phi_scan` that `phi_scan` does not make and nothing
re-derives*. That forbids asserting in YAML. A heading **derived from the scanner's own exit status**
is relayed rather than asserted, which is the relationship the step already has to the report it
prints.

**The chronic redness is not absorbed here.** 22 of 25 is a signal-destroying condition, it is
reconciliation debt rather than anything this ticket caused, and it caps the value of everything on
this surface. It is filed as its own ticket at the sweep.

## Ruling 7. Nothing is re-derived backwards and the marker carries the denominator forward

No retrospective sweep of figures published from an ungated harvest. The body's statement stands as
the honest one — this ticket does not establish which are wrong, only that none carries evidence it
is right — recorded here and nowhere else.

**Re-running is not verification, which is why the sweep is refused rather than deferred.** A past
harvest cannot be re-derived: the tracker moved from ADR 0184's 1121 records on 2026-09-11 to 1195
today, so re-running any of those commands produces a different, correct, **current** number and
proves nothing about the old one. A sweep would replace old figures with new ones and file the result
under *verified*, which is an instrument printing the same thing whether the claim is true or false.
Annotating without re-deriving is that cost without that illusion, and asks an author to hand-maintain
a provenance note nothing fails on, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s shape.

**The forward half is already ruled elsewhere and needs nothing here.**
[ADR 0196](0196-a-published-figure-names-its-population-and-is-re-derived-at-publication.md) ruling 3
keys its re-derivation rule on *the population the author believed they measured is not the population
the instrument read*, and names **truncation** as the first of its three species. What this build
supplies is the denominator that makes that rule satisfiable for a harvest-derived figure; today an
author can comply in form and still be wrong, because there is nothing to name.

**One retrospective instrument does work and is kept.** ADR 0184 ruling 4 keeps `finding_counts` in
the harvest marker because its git history is what settled
[#1121](https://github.com/mshamblin5150-code/clinical-skills/issues/1121), and ruling 6 mechanic 4
already puts the population beside it. So from this build forward, the next person asking whether a
given harvest was complete has an answer recoverable with `git show`, where today they have none.

## Ruling 8. The cause is unowned and the next occurrence files itself

No cause ticket. The ADR states the cause as unsettled and #993 closes on the merge.

A cause ticket filed today is unbuildable in the strict sense: three runs at this commit returned
1195 records byte-identically, so there is nothing to attach an instrument to, and the body forbids
by name the one thing such a ticket tempts an agent into — *"a retry loop presented as a fix.
Retrying an instrument that cannot detect its own failure produces a different wrong answer, not a
right one."* Holding #993 open instead is worse, because the label vocabulary has no honest state for
*open pending an event that may not recur*.

**What makes that safe rather than a shrug is that the refusal preserves evidence.** On a refused
short read the run writes an accounted scratch record on `preserve_refused_outcomes`'s existing
pattern, carrying the probe's population, the harvest count, the timestamp of each, and **the sorted
list of record numbers the harvest returned**. That last field is the diagnostic one: the 2026-09-09
comment established the truncation is **positional** rather than a filter, since a 150-record short
read held 125 closed and 25 open, so *which* numbers went missing is the whole question and is what
no sample on the thread has ever carried. It is roughly 1195 integers, all of them already public.

The cause therefore moves from *unreproducible* to *captured on its next occurrence*. Filing a cause
ticket now is premature by exactly one event.

## Ruling 9. A refusal after an outcome is authored preserves it

`preserve_refused_outcomes` fires on any refusal reached after an outcome was authored, rather than
on the three write-time refusals alone, and the preservation moves outside the lock block so a
`locate_map` refusal is covered too. The run prints its did-not-scan reason and the record path
together, and `check` lists that record as it already lists lock-refused ones.

**The module already holds this as a principle, and a read-time refusal would be the first thing to
break it.** Three separate refusal kinds — a busy lock, a state-hash mismatch, a body the publish
hook declines — each preserve. They share nothing except being reached after an outcome was authored,
which is the property this ruling names. So this is not a new rule; it is the existing rule reaching
the one refusal that arrives before the write rather than at it.

**This is a cost ruling 1 introduces rather than one the ticket names.** Under uniform refusal,
`apply-delta --ticket N --outcome "<an authored paragraph>"` against a short read loses the
paragraph: `main` catches the `MapError` and the existing handler never runs. Today the same command
succeeds — wrongly, on a truncated population — but the human's words survive. Trading a wrong
placement for a lost judgment is not the trade this build is for.

**The retry argument is refused on its own asymmetry.** *A did-not-scan is retryable in seconds* both
assumes the operator still holds the paragraph, which is false for an unattended agent that composed
it in-process, and points the wrong way: a lock conflict is the refusal one can safely retry, because
the other holder will finish, while a short read is intermittent with an unknown cause, so *run it
again* is the retry-an-instrument-that-cannot-detect-its-own-failure move the body forbids.

## What this record does not settle

**The cause.** Unknown, unowned, and unreproducible at this commit. Ruling 8 captures the next
occurrence rather than diagnosing this one.

**Whether the GraphQL and REST populations can structurally diverge.** Two classes — an issue
converted to a discussion, and an issue hidden as spam or abuse — could not be settled from primary
sources. If either makes GraphQL count what REST omits, this gate produces a permanent false short
and refuses a healthy tracker. Ruling 5 names them in a limits row and makes the refusal diagnostic
enough to recognise, and does not rule out the possibility.

**Whether any figure already published from an ungated harvest is correct.** Ruling 7 declines to
find out, on the ground that finding out is not available.

**The chronic CI failure rate.** Out of scope by ruling 3 and filed separately by ruling 6. A gate on
a chronically red step is a gate nobody reads, so the value of this build's unattended half is capped
by a problem it does not touch.

**Whether `blocked_by`'s true maximum is under 30 today.** Ruling 4 makes it moot by sizing the read,
and the measurement was deliberately not taken because taking it reproduces a secondary rate-limit
outage.

**No new glossary term.** ADR 0184 ruling 8 added **Population denominator** for this exact property
and ADR 0196 ruling 9 added **Measured population**; a third term here is the collision those two
records just finished declaring.

## What the build verifies

- One probe and one harvest per process, driven by counting calls through a stubbed `_run` — and a
  second `issues()` call in one process issuing **no** further request.
- A short read raises from `GitHub.issues()` and reaches status 2 through `main` for **every**
  command, each driven, rather than for `check` alone.
- A harvest **longer** than the population does not refuse, so ordinary growth during the read is not
  a finding.
- The comparison is against the pre-filter count, driven by a harvest whose filtered length is below
  the population and whose raw length is not.
- The refusal names the population, the harvest count, the shortfall and the highest record number,
  and the highest-number field discriminates a truncation from a wrong denominator in a driven pair
  of cases.
- `blocked_by` with no `Link` header returns its rows; with a `Link` header it raises. Both driven,
  and a positive control proving the header-present path is reachable.
- `map_scan` without `--population` returns its did-not-scan status, and with a short population
  refuses; `tracker_bodies` likewise, against a manifest built by `tracker_population`.
- The `checks.yml` heading is derived from the status, driven by the workflow test reading the file
  rather than by asserting prose.
- An authored outcome survives a short-read refusal from **both** `locate_map` and inside the lock,
  driven separately, with the record's path printed and listed by `check`.
- The new limits rows exist and every row is driven to a live path, including
  `clean-check-derived-views` in its repaired wording.
- `CLAUDE.md`'s sections for the three tools point at the limits objects and copy no row of them.

---

*Correction, 2026-09-12.* The measured section first read *"The refusal-preservation mechanism fires
on one refusal only … `cmd_apply_delta` calls it under `except artifact_lock.ArtifactBusy` and
nowhere else,"* and ruling 9 rested on that. **It is false, and it was false at the base it was
measured against rather than made false by the merge.** `preserve_refused_outcomes` has four call
sites covering three refusal kinds, at `6380b8a6` and at `2f814d1f` alike. The error was generalising
from the one call site a `grep` for the `MapError` handler happened to show, without enumerating the
rest — this repository's own recorded shape, a partial read answering like a complete one, inside the
record whose subject is exactly that. **Ruling 9 is unchanged and its ground is stronger than the one
it was written on**: the module already preserves across three unrelated refusals, so the principle
is established and a read-time refusal is the first thing that would break it, rather than a new rule
argued from a single instance.
