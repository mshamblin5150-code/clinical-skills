# A map overwrite is attributed rather than prevented

Out of [#966](https://github.com/mshamblin5150-code/clinical-skills/issues/966), grilled on
2026-09-12. Nothing is built here; this is the record the build reads.

**Measured at:** 7c555b7e8e579991c74f1a06a9329d72a472a2a5

#966 reported that two sequential placements each succeeded and each dropped the other's packet, and
named three causes: a time-of-check-to-time-of-use window between the state-hash comparison and the
write, a lock that cannot reach a writer on another machine, and neither limitation being declared.
The window and the cross-machine limit both re-derive. The third is false as filed and was already
corrected once. A fourth defect the ticket did not name was found by driving the code, and it is the
one a build can fix outright.

[#920](https://github.com/mshamblin5150-code/clinical-skills/issues/920) asks what a session owes the
map and is untouched by this record.

## What was measured before ruling, on 2026-09-12

**The lock already excludes every in-tree writer on this machine, which narrows the window to a
writer the lock cannot see.** `map_artifact` keys the lock on a digest of the repository and the
issue number under the machine temp directory:

```python
def map_artifact(tracker, issue_number: int) -> Path:
    """Stable lock identity for one repository's coordination issue."""
    repo = getattr(tracker, "repo", "in-memory")
    identity = hashlib.sha256(f"{repo}#{issue_number}".encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / "clinical-skills-map-artifacts" / identity
```

So it is machine-wide and checkout-independent, resolved on this machine to a path under
`clinical-skills-map-artifacts`. Two `apply-delta` runs on one box cannot both be inside the window;
the second is refused at acquisition, which #966's own 2026-09-11 comment observed live. The window
is therefore reachable only by a writer on another machine, a writer with a different
`CLINICAL_SKILLS_LOCK_ROOT`, a writer that takes no lock, or a person editing the body in the browser.

**The guard also catches the ordinary interleaving twice.** Where A publishes first, B's comparison in
`publish_body` reads A's body and B refuses; where B publishes after A's read-back, A's own
`extract_state` round-trip check fails and A returns 1. A silent double-success needs B's single
round trip to span both of A's, which is narrower than the ticket's framing.

**`userContentEdits` records API-driven body edits, contradicting decision 3's premise, and the
footer already says so.** What the footer does not say is the shape of what it returns. The `diff`
field is **the full body at that revision** rather than a unified diff — 199,860 characters against a
current body of the same length — so every retained revision of the map is recoverable. Its
`editor.login` is `mshamblin5150-code` for every edit, so it names an account and never a writer.

**And that history is capped and sliding, measured against this thread's own earlier reading.** The
connection reports `totalCount` 100 with a further page in both directions. #966's 2026-09-10 comment
tabulated 33 edits on 2026-09-08; the same query on 2026-09-12 returns **5** for that day, and
2026-09-06's 7 and 2026-09-07's 8 are gone entirely. At 36 edits on 2026-09-11 and 25 by 16:15Z on
2026-09-12, 100 revisions is about **three days**. *Had the window not slid, the 2026-09-08 row would
still read 33.* So the free trail has already lost most of the evidence for the incident that filed
this ticket.

**The Snapshot is outside both guards, checked rather than assumed.** `state_hash` re-canonicalizes
only the extracted state block — *"Hash only canonical machine state, never the volatile derived
views"* — and `derived_sections` drops the Snapshot outright, *"whose date legitimately differs
between renders."* `producer_stamp_problem` requires exactly one producer stamp and exactly one
default-branch commit line and forbids no additional line. So a per-writer value in the Snapshot can
refuse no concurrent writer and cannot read as audit drift.

**A trail inside the state block is destroyed by the overwrite it exists to record.** `render` builds
the body from `state`, and a clobbering writer's `state` came from `extract_state` of the pre-clobber
body. A's trail entry therefore vanishes with A's packet, and the surviving ring shows no gap because
the evidence and the loss are the same bytes.

**Three body writers carry three different obligation sets.** Driven with a fake tracker rather than
reasoned from the source:

| writer | lock identity | state hash | post-publish re-validation |
| --- | --- | --- | --- |
| `cmd_apply_delta` | the map's | compared | exits 1 and names the finding |
| `cmd_publish` | the map's | compared | **none: exit 0 over a live disagreement** |
| `cmd_init --adopt` | `#0` | `None` | none |

**The ticket's headline claim does not re-derive.** *"No exit status carried it. Both runs returned
0."* A fake tracker carrying two ready tickets, with one placed by `apply-delta --ticket`, returns
**1** and prints `FINDING unmapped-ready: #826 carries ['ready'] but is in no packet and not
excluded`. `validate_against_live` emitted `unmapped-ready` at the ticket's own base commit
`c78c025e`, the post-publish re-validation block was present there too, and `placement_coverage` and
`validate_against_live` derive their populations from the same `all_tickets` and `excluded_tickets`
expressions, so the printed coverage line and the finding cannot disagree. What the 2026-09-08 runs
returned is not established and is not adjudicated here; the mechanism the claim says is absent is
present and fires.

**`cmd_publish` is the defect that does re-derive.** Driven over a live `unmapped-ready` disagreement
it returns **0** and never mentions the finding, while `cmd_apply_delta` over the same disagreement
returns 1. *Had the two commands shared a posture, both would have returned the same status.*

**`CLAUDE.md`'s mutual-exclusion sentence is false three ways, and it is hard-wrapped across two
lines** — which is why a single-line search for it returns nothing, `test_run_record_claim.py`'s own
recorded finding arriving on this sentence:

> Every tracker mutation holds the repository's nonblocking artifact lock and
> compares the state-block hash immediately before publication. The hash excludes
> derived views, so concurrent publishes do not conflict

*Every tracker mutation* is wider than the map, since the tracker workflow's `gh issue comment` and
`--remove-label` hold no lock. *Holds the repository's lock and compares the state-block hash* is
false of `cmd_init --adopt`, and *the repository's* implies one lock where there is one per machine.
*Concurrent publishes do not conflict* is true of the hash and misleading about the outcome: they do
not conflict, they clobber.

**The limits row that exists covers more than the thread credits it with.** `cross-machine-prevention`
reads *"The operating-system lock coordinates only this machine; the state hash can refuse but cannot
prevent a remote race"* and predates the ticket. #966's 2026-09-09 comment proposed amending it
because *"no row says a refused writer's placement is silently dropped at exit 0"* — which rests on
the claim refuted above.

**The glossary already holds most of this model.** `CONTEXT.md`'s **Lock root** entry rules the
cross-machine hazard as declared and never warned about: *"two processes pointed at different roots do
not see each other, which is exactly the overlap the lock exists to prevent. Undetectable at run time
by construction, since the evidence would be a contention that never happened."* Its **Map
disagreement** entry already names the detection — *"a ready ticket in no packet, and a packeted
ticket that has stopped being ready."* Nothing named attribution, and nothing named the rescued
outcome.

## Ruling 1. The model is accept-and-detect, and a GitHub-side advisory lock is refused

The map is **eventually consistent with attribution**, not mutually excluded. Exclusion stays
machine-local and declared; a lost overwrite is detected and attributed after the fact.

**A GitHub-side advisory lock was available and is refused as net-negative rather than as
unreachable.** GitHub's issue-update endpoint accepts no `If-Match` precondition, so an atomic
compare-and-swap is unavailable — but comments are append-only and ordered, so a claim-comment lock is
implementable. It is refused because its liveness failure has no recovery path: a holder that dies
wedges the artifact until something expires the claim, and the expiry heuristic is itself a race. It
also buys nothing against the writer most likely to surprise, since no advisory lock reaches a browser
edit.

**A stronger local lock is refused on the ticket's own ground**, restated so it is not re-proposed: a
local lock made more thorough still cannot see a writer on another machine, and it would make the
prose above more misleading rather than less.

**This ratifies an existing entry rather than inventing a posture.** `CONTEXT.md`'s **Lock root**
already rules the hazard declared-and-never-warned.

## Ruling 2. Convergence is a bounded state-hash retry inside the lock that re-derives the delta

Three attempts, no delay, inside the held lock. Each attempt re-reads, re-extracts the state and
**re-derives the delta** — it does not re-send the rendered body, which would clobber.

**The code already supports replay and the ticket cited it at a stale coordinate.**
`_direct_placement_delta` takes `state` as its first argument, so an attempt against a freshly re-read
state recomputes: where the packet was clobbered it is re-placed, and where the other writer placed
the same ticket meanwhile it returns an empty delta and the run correctly reports zero written.

**A hash mismatch under the held lock can only be a writer this machine cannot see**, which is why the
retry belongs inside the lock: it keeps excluding this machine while converging against the remote
writer in two round trips.

**One replay hazard is named rather than left to be found.** `_apply_delta_under_lock` assigns
`args.commit = reviewed_through` in place, so a second attempt reuses the first attempt's
`default_branch_head()` rather than re-reading it. For an ADR review that pins `reviewed_through` to
the first attempt. That is defensible, since the delta was authored against that commit, and it must
be deliberate rather than incidental.

**Retry does not close the window and is not presented as closing it.** A retry loop's final write is
still unguarded. What it changes is that a detected mismatch converges instead of stranding.

## Ruling 3. The lock refusal stays a refusal

A busy lock is not retried. The observed hold on 2026-09-11 ran from `00:44:07Z` to some time before
`00:50Z`, so a retry that mattered would have to block for minutes, and a short one would block and
then refuse anyway.

**The refusal is the only guard in this mechanism that has been observed working.** Trading a legible
refusal for an unbounded wait is the wrong direction. What changes on that side is the record, in
ruling 6, and not the status.

## Ruling 4. Attribution is stamped in the derived Snapshot, where no guard can see it

The Snapshot gains the writer's identity and the state hash that revision believed it was superseding.
`expected_state_hash` is already in hand at render time, since `publish_body` renders before it
compares.

**That makes GitHub's own history a self-verifying chain.** A clobber is a revision whose declared
superseded hash is not the hash of the revision actually before it, with both writers named. No
inference, and no missing actor.

**The Snapshot is the one place in the body where a per-writer value is free**, on the measurement
above: `state_hash` cannot see it, `derived_sections` drops it before `audit` compares, and
`producer_stamp_problem` forbids no additional line. A stamp in the hashed state block would refuse
every concurrent writer instead.

**It lands first and separately from ruling 5.** The stamp is the whole of the attribution gap and is
nearly free, so it does not wait on a storage decision.

## Ruling 5. The durable trail is harvested rather than written, and records only chain breaks

A harvest on write reads `userContentEdits`, verifies the chain across every retained revision, and
appends a row to a committed ledger **only where the chain breaks**. It adds one read per publish and
no additional write to the map.

**A bounded ring in the state block is refused on a structural ground, not a cost.** It is destroyed
by the overwrite it exists to record, per the measurement above. It survives every loss the guard
already detects and is destroyed by exactly the one it was built for.

**One comment per mutation is refused on a measurement.** At the 25 writes on 2026-09-12 and 36 on
2026-09-11, it is 25 to 36 comments a day onto an issue already past 47, which buries the artifact.

**A machine-local file is refused**, on #966's own ground for that candidate: invisible to exactly the
writer whose collision it needs to record.

**The ledger is committed, on an established precedent.** `reference/guidelines-catalog-audit.md` is a
committed ledger of durable identity facts about a perishable out-of-repo corpus, written by a command
and committed separately by a person, graded at the commit under
[ADR 0031](0031-corpus-drift-is-reported-at-the-commit-and-the-cheap-limb-reads-the-audit-ledger.md).
A break ledger takes that shape and should stay near-empty.

**It carries a high-water mark and states its unread remainder.** A harvest that fell behind the
sliding window must not report a verified chain over revisions it never read. Its honest claim is that
the chain is unbroken across the revisions it saw, with the remainder named — the same shape every
other grader here states, and `CLAUDE.md`'s own rule that a matcher never turns a partial read into a
clean whole.

**The horizon is re-derived and never a constant in prose.** It moved from three days' worth of
history to 5 surviving edits on the incident day in two days flat.

## Ruling 6. A rescued outcome goes to the accounted scratch namespace and is never replayed

`preserve_refused_outcomes` writes under `scratch/runs/`, mirroring the publish hook's own marker
there, and `check` gains a line reporting pending records.

**#966's reason for moving it does not survive the glossary and the real defects are different ones.**
The ticket calls the temp directory *"the same mistake as `artifact_lock.lock_root()`."* It is not: a
lock root must be **shared** to do its job, and a peer computing a different path is the whole hazard,
while a rescue record only has to be found again by its own author — and a refused writer is by
definition the machine that authored the outcome. Machine-local is correct. The defects are that the
temp directory is **ephemeral**, cleaned on a schedule nobody controls, and **unenumerated**, since
the path is printed once to a console that scrolls away.

**`scratch/runs/` rather than a new top-level entry**, so the scratch census has nothing new to grade.

**Automatic replay is refused explicitly so it is not re-proposed.** Replay is mechanically safe,
since `_direct_placement_delta` is per-ticket and idempotent. It is refused because a rescued outcome
is a sentence a person wrote about a specific state, and placing it unattended is `CLAUDE.md`'s *a
guessed answer here is worse than a blank one* arriving on an authored judgment instead of a figure.

## Ruling 7. Map overwriter is one role with one obligation set, enforced by a walk

Every function that overwrites an existing map body takes the map's own lock identity, compares the
state hash, and re-validates after publication. A walk binds the set, so a fourth writer cannot arrive
weaker.

**The role name is load-bearing.** `cmd_init` without `--adopt` creates an issue, where there is no
prior state to hash, so the obligation attaches to **overwriting** an existing body and not to writing
one. Creating is outside the role by definition rather than by exemption.

**Two writers change.** `cmd_publish` gains the post-publish re-validation it lacks, and
`cmd_init --adopt` gains the map's lock identity and the hash it passes as `None`.

**The `--adopt` hole is latent rather than live, and it is repaired anyway.** `_init_under_lock` runs
`find_map_issues` first and raises where any issue body carries the state marker, so adopting the live
map refuses before reaching the write. It is repaired because the model now rests on the state hash
being the cross-machine defense, which makes a writer that skips it a hole in that exact defense.

**The glossary argued against uniformity and the tension is resolved rather than ignored.**
`CONTEXT.md`'s **Reconciliation** entry says a publish *"re-renders the derived views from unchanged
state and reconciles nothing, which is why the obligation to have reconciled is anchored on a field
the delta sets rather than on the rendered snapshot a publish rewrites."* Read straight, `cmd_publish`'s
silence is correct. It is resolved for grading because **Map disagreement** is defined as a property
of the map against the tracker rather than of a command's intent: a command that rewrites the map and
stays silent about a disagreement it can see publishes a page it knows to be wrong.

**A per-member posture was available and is refused on this repository's own record.** Three commands
with three declared postures is what the tree has today, and it is the shape that goes stale at the
merge — the console-codec ordinal going stale on a branch that touched nothing, and the sixteenth tool
caught one commit late. The obligation set is exactly three named things, which is what a conformance
walk can hold, on `grader_conformance.for_module`'s precedent.

## Ruling 8. The sentence narrows to the role, and one limit row is added

`CLAUDE.md`'s mutual-exclusion sentence becomes a claim about a **map overwrite** rather than about
every tracker mutation: every map overwrite takes the map's own lock identity, compares the state
hash, and re-validates; concurrent overwrites from different machines do not conflict and **can
clobber**, which is detected after the fact rather than prevented; a refusal preserves its authored
outcome in an accounted scratch record the run names and `check` lists.

**The subject narrowing is the load-bearing edit.** The sentence over-promises mostly by being about a
wider population than the mechanism serves, which is the same defect class as a matcher reporting
clean about a tree it cannot see.

**Enumerating the exceptions under the wide subject was available and is refused.** It puts a list of
non-map tracker mutations in a paragraph about the map, and a list in prose here is the thing that goes
stale — this one citation has moved four times in four days, through four distinct anchors published on
the thread.

**`cross-machine-prevention` stands as written.** It already covers the window and the cross-machine
limit, and the proposed amendment rested on a refuted claim.

**One new row rather than two.** The sliding window and the ledger's high-water mark are one claim from
a reader's side — how far back attribution reaches — and splitting them invites the halves to drift,
which is [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s recorded shape. The
row states that the trail reaches only the revisions the harvest read, bounded by a sliding
hundred-revision window, and that the ledger states its high-water mark and unread remainder rather
than claiming an unbroken chain.

## Ruling 9. `CONTEXT.md` gains `Map overwriter` and `Revision chain`

**Map overwriter**: a writer that replaces an existing map body, as distinct from one that creates the
issue — the distinction the obligation set attaches to. **Revision chain**: the ordered sequence of a
tracker record's retained body revisions, each declaring the state it superseded, which is what makes
a clobber attributable without an actor.

**Terms are coined rather than avoided**, on
[ADR 0149](0149-a-pointer-is-not-a-source-and-a-failed-read-is-not-a-negative.md) ruling 6's recorded
ground: an author with no name for a distinction reports the nearest one. **Map disagreement** is not
widened to cover attribution, because its sense is a state of the map against the tracker and says
nothing about who caused it.

## What this record does not settle

**Whether the 2026-09-08 loss was the check-to-write window or an unguarded writer.** #966's
2026-09-11 comment established that the retired out-of-tree emitter took no lock and compared no hash,
which fits both placements reporting success. GitHub records no actor for API body edits, so this
cannot be attributed, and it is the defect ruling 4 exists to prevent recurring rather than one it can
resolve.

**What the 2026-09-08 runs actually returned.** The measurement establishes that the mechanism fires
at that base, not what happened.

**Whether `tracker.issues()` should report a denominator.** `find_map_issues` reads a `--paginate`
harvest with no denominator and no unread remainder, so a harvest that drops the map makes `locate_map`
print *"no implementation map … Run `init` to create one"* — an instruction pointing at the weakest
writer. That is
[#993](https://github.com/mshamblin5150-code/clinical-skills/issues/993)'s class, inherited rather than
entangled, and it is filed separately rather than widening this.

**Where the break ledger lives, by name.** Ruling 5 fixes its shape and its precedent, not its path.

**The retry's exact bound.** Three attempts is stated; whether that is the right number is a
measurement nobody has taken, and no run has yet recorded a state-hash refusal in the wild.

**Whether the browser edit should be reachable at all.** Nothing here constrains a person editing the
map body in the GitHub UI, and every mechanism above treats that writer as outside exclusion by
construction.
