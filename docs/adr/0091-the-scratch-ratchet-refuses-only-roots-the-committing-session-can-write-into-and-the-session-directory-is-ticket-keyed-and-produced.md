# The scratch ratchet refuses only roots the committing session can write into and the session directory is ticket keyed and produced

[#700](https://github.com/mshamblin5150-code/clinical-skills/issues/700) was filed as a backlog of
unaccounted scratch entries needing the clinician's per-file word, self-retracted in its own comment
1 as a race, and relabelled `grilling` with three open questions. Grilled 2026-08-31 at `84cb99a`,
freshness gate `FRESH`. **Eight decisions, ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

**The grilling widened the ticket, and the widening came from the clinician rather than from the
tree.** #700's three questions are all about *blast radius* — who is refused when a root goes over.
Mid-session he supplied the fact none of them rests on: the collision that produced this ticket was
**two drones on one checkout**, because Codex, the factory he uses when working remotely, cannot
create a worktree. Every question filed on this ticket assumes one session per checkout. Rulings 4
through 6 are the half that reaches his case, and rulings 1 through 3 and 7 are the half the ticket
filed.

## What this supersedes

**[ADR 0059](0059-the-scratch-census-walks-every-checkout-that-owns-a-scratch-root-and-the-worktree-half-is-held-at-zero.md)
ruling 7's refusal of a producer, and nothing else in it.** Rulings 1 through 6 and 8 stand as
written. That paragraph stays untouched, being the dated record of what was decided on 2026-08-27;
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
holds that a deciding paragraph is untouchable.

**Ruling 6 below is not a rerun of the argument ruling 7 lost on, and the distinction is the whole
of it.** Ruling 7 refused a producer *as enforcement*, in these words: *"it constrains only sessions
that call it, and the sessions #466 recorded left the checkout entirely."* **That reasoning is
correct and is left standing** — enforcement remains the census. What ruling 7 did not weigh is that
the same paragraph counts **five tracked copies of one path**, records that two of them were found
by a verification grep run after the decision had been scoped over three, and calls that
*"[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving inside the ruling
whose subject is one path written five ways"* — and then ships the five. Ruling 5 below moves the key
in all five. A producer is adopted here as **the single statement of a path**, which is
`repo_root.py`'s, `console_codec.py`'s and `docx_write.REFERENCE_HEADING`'s standing discipline, and
never as a gate.

**[ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md)'s
naming section is untouched**, and ruling 8 below is that section holding rather than moving.

## Measured before ruling, at `84cb99a`

Every figure is dated and scoped to that base. The scratch figures are counted against a gitignored
root, so nothing committed re-derives one and the next session moves them all.

**The owning-checkout count sits exactly at the baseline. Zero headroom, confirmed live.** No digit
appears here for either, on ADR 0059 ruling 3, and the command re-derives both. The census exits 0,
`CLEAN`, over 52 enumerated worktrees and 18 checkouts owning a scratch root. **The mechanism is not
refusing; it is one loose file away from refusing every checkout**, which is the state #700's
comments 2, 3 and 4 each recorded independently and which this session found a fourth time without
looking for it.

**`scratch/sessions/` does not exist in the owning checkout.** Not empty — absent. That root's top
level holds **23 directories and 32 loose files**, and the namespace `docs/agents/scratch.md` calls
the answer has never been created in the root where the material lands. **The rule is written in six
tracked places and the directory is not there**, which is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written
instruction cannot do is fail* at full strength, and it is the single strongest fact this grilling
produced.

**The branch key is already a per-worker key for two of three harnesses and fails in the third.**
`claude/<slug>-<hex>` carries a random suffix per worktree, and the bridge branches carry a harness
session id; both are unique. **A Codex branch legitimately spans several tickets** —
`codex/tickets-550-645` merged twice, on #704 and #710, and `codex/tickets-670-706` carries a
`-marker-followup` sibling — so drones working two tickets on one branch are handed one directory.
**And the branch is mutable during a run**: one drone running `git checkout` moves every other
drone's key in that checkout, mid-session. A key derived from repository state is a key another
process can change.

**Five copies of the path, re-derived rather than taken from ruling 7.** `CLAUDE.md` twice,
`docs/agents/issue-tracker.md`, `tools/tracker_scan.py`, `tools/tracker_bodies.py`. Ruling 7's count
of five is still exactly right.

**#700's own body publishes the baseline digit twice**, in the headline figure and in its dated
footer. That is ADR 0059 ruling 3 broken in a public record, by the ticket whose subject is the
ratchet, and it is stripped in the respec rather than left standing as the reader's first encounter
with the number.

## What is ruled

**1. A top-level entry in a scratch root is a rule violation for as long as it exists, and its age is
not a property the census reads.** The census was correct both times #700 records it firing. The
declined alternative is an age or lock discriminator making a young entry a non-member: it needs a
cut point nothing in this repository grounds, which is
[#97](https://github.com/mshamblin5150-code/clinical-skills/issues/97)'s standing objection, and
#700's own comment 2 measured the only cheap instrument out — **a directory's mtime moves when its
contents change, so an entry created days ago and written to today is indistinguishable from one
created today.** The compliant path already exists and `CLAUDE.md` records a *tool* being moved onto
it rather than the check being loosened: the pre-publish hook writes
`scratch/runs/tracker-publish-hook.json` precisely because *"creating a new top-level scratch entry
would move the global scratch census and could refuse every checkout's commits."* Loosening the check
to bless the behavior that rule forbids would be
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215)'s recurring defect with its
sign flipped.

**2. A root may refuse a commit only if the committing session can write into it.** That is own root
plus the owning checkout's, and never a peer worktree's. ADR 0059 ruling 2 already split the
*grading* per root; the *status* stayed a single `owning_finding or other_finding`, and that
inconsistency is the whole of #700's comment 1. **The line is principled rather than arbitrary**: a
session in a worktree writes into exactly two roots — its own, and the owning checkout's, because
`repo_root.scratch_root()` resolves there by design since
[#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93). A peer's root is one it
cannot write into, did not dirty, and has no authorized move against; ADR 0059 ruling 6's drain runs
*to* the owning checkout, never out of a peer.

**Local-only was refused and it is the option that looks right.** Sessions work in worktrees and the
owning checkout is rarely committed from, so under local-only a loose file in the owning root —
#700 comment 1's exact shape, and the shape any tool writing through `scratch_root()` produces —
refuses no commit anywhere. That is the ratchet going dark on the one root where the real material
lives. **This ruling keeps comment 1's instance refusing every checkout deliberately**: there the
shared root really is shared, every session writes into it, so every refused session is a candidate
author and the writer is guaranteed to be among them. Comment 4's instance — a peer's private root,
no reach, no candidacy — is the collateral this removes.

**It is a no-op from the owning checkout**, where local and owning are one root.

**3. A peer worktree's root is reported on every run and graded never, and the hole that opens is
declared rather than closed.** Ruling 2 leaves a peer's loose entry gated only by that worktree's own
next commit; a session that ends without committing again is caught by nothing, and
`git worktree remove` then disposes of unrecoverable patient material with nobody's word on it.
**That hazard is not created here** — ADR 0059 ruling 5 records seven of eight worktrees merged,
clean and removable, and that *"an ordinary `git worktree remove` or prune takes their roots with
them and nothing warns."* **Ruling 2 makes it more reachable**, because universal refusal was doing
the noticing by accident, and that is stated in `DECLARED_LIMITS` rather than argued away.

Two closures were refused. Gating the owning checkout's committer on every root is a backstop that
fires for almost nobody, which `CLAUDE.md` already rules against in `docx_write`'s words — *"A second
mechanism that cannot fail is not a belt and braces; it is a line that costs a test."* Refusing
everyone once an entry outlives some age reintroduces ruling 1's rejected threshold through a side
door.

**4. A drone's working material lives inside the scratch root, under the sessions namespace.** Not an
OS temp root outside every checkout, and not `scratch/runs/`. **The temp root is where the material
is least protected, and "invisible to the census" is not "safe"** — outside the checkout `phi_scan`
cannot reach it and the census cannot see it, so a drone harvesting a tracker body with a patient
name into `%TEMP%` is guarded by nothing at all. ADR 0059 calls that placement *"directionally
good"* for accumulation and it is, and accumulation is not the only property. **`runs/` is refused on
the glossary**: `CONTEXT.md` defines a **run directory** as a graded artifact's provenance record
keyed by course, module and artifact, which *outlives every sitting* — putting disposable drone
scratch there makes the clinical provenance root and the transient bin one directory, and whoever
cleans one deletes the other. It was the correct move to unblock a live collision by hand and it is
the wrong permanent home.

**5. The session directory is keyed by the ticket.** `scratch/sessions/ticket-<n>/`. The branch key
is retired in all five copies: it hands one directory to two drones whenever a Codex branch spans
several tickets, and it is mutable by any other process in the checkout.

**Two sittings on one ticket share one directory, and that reads like a defect and is the ruling.**
`codex/tickets-670-706` and its `-marker-followup` are that shape; under a ticket key the follow-up
opens the directory its predecessor left and **finds the work**. That is the clinician's own
requirement — *"that way we don't blow this work out"* — delivered by the key rather than by anybody
remembering.

**Ticketless work gets a named sibling**, `scratch/sessions/sweep-<date>/`, rather than falling back
to the branch or to the top level. A fallback to the top level is the failure this whole ruling
closes.

**The residual is two drones running one ticket concurrently**, which the ticket key does not
separate. It is declared rather than closed: nothing in the merge log shows it happening — the
multi-ticket branches are one drone over several tickets and the repeats are sequential sittings —
and the closure available is a worker id that Codex may not expose and that nothing in this
checkout can verify.

**6. There is a producer, and it is justified as deduplication rather than as enforcement.** It
resolves through `repo_root.scratch_root()`, creates the ticket directory, prints it, and can return
nothing else — in particular it cannot return a path at the scratch top level. The five copies become
five calls. **Enforcement stays the census**, unchanged and now correctly aimed by ruling 2: the
writer is the refused party, and ruling 7 below puts the destination on the line that refuses them.
**The producer is not a second gate; it is the reason there is one place to move it to.** See *What
this supersedes* for why this is not the proposal ADR 0059 ruling 7 refused.

**7. The report names which roots gated the commit, splits the delta from the population, and carries
the remedy and the prohibition on a finding.** #700's body read one number as a disposition backlog
when it was a stopwatch reading, and the number is still one line over **two populations with
opposite remedies** — grandfathered residue awaiting the clinician's per-file word, and a rise
awaiting a drone relocating a file. Ruling 2 and ruling 3 add a second axis the report has never
carried: a gating root and a reporting root now mean different things, and on
[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s terms an absent qualifier
reads as the stronger claim, so both print on every run and not only when one fires.

**The report prints the delta and never the baseline digit.** `N unaccounted, M above baseline`, never
`baseline N`. ADR 0059 ruling 3 holds the baseline is the module's to state and appears nowhere else,
and a report is pasted into tickets — #700's body is the recorded case of that digit reaching a public
record and going stale in it. Printing the constant beside a refusal is also, practically, an
invitation to edit it, which #700 comment 1 names as *the worst remedy a blocked session will reach
for*.

**The prohibition prints on the finding line itself**, not in a document: `do not raise
OWNING_BASELINE`, at the moment somebody is blocked, because that is the only moment anybody is
tempted.

**8. The namespace keeps the name `scratch/sessions/`, and the child gains one.** ADR 0033's *The
vocabulary collision, ruled rather than avoided* chose that name deliberately and refused `passes` or
`sweeps` on the measurement that `CLAUDE.md` names the pass sense dozens of times. **Ruling 5 moved
the key, and a key is not a name** — the namespace still means *where an agent's working material
goes*, which is exactly true. Renaming to `scratch/tickets/` or `scratch/work/` would spend
`docs/agents/scratch.md`, five command copies, `tools/test_scratch_census.py` and **three ratified
records** — ADR 0033's naming section, ADR 0059 ruling 7, and ADR 0089 twice — whose deciding
paragraphs cannot be rewritten under ADR 0016, so they would permanently cite a path that does not
exist.

`CONTEXT.md` gains **Ticket directory** for the child, which has had no name while every ruling above
turned on it, and **Session**'s definition is corrected: it read *"the unit that opens a branch"*,
which the clinician falsified in this session and the merge log confirms.

## What this does not reach, declared rather than left to be found

**Two drones sharing one checkout are one root to the census, by construction.** Ruling 2 takes the
blast radius from every checkout to one; it cannot take it below one, because both drones write the
same scratch root and both are gated by it. Rulings 4 through 6 are what reach that case, and they
reach it by prevention rather than by scoping. **A grilling that had stopped at #700's three filed
questions would have shipped a fix that does not fix the case that produced the ticket.**

**A producer constrains only sessions that call it.** ADR 0059 ruling 7 is right about this and it is
not answered here, only reclassified: nothing makes a drone call it, and the census remains the only
thing that fires.

**An abandoned worktree's loose entry is graded by nothing**, and its removal disposes of
unrecoverable patient material with no word on it. Ruling 3.

**Two drones on one ticket at the same time share one directory.** Ruling 5.

**The grandfathered residue is untouched.** This record moves no baseline, schedules no `rm`, and
publishes no filename. Disposing of an unaccounted entry remains the clinician's word, per file,
after opening it rather than after reading its name —
[#417](https://github.com/mshamblin5150-code/clinical-skills/issues/417) ruling 10, ADR 0059 ruling 8,
and the standing rule above them, unchanged. **The cheap remedy is still unavailable for any entry
whose name is not safe to publish**, and #700 comment 4 found a second edge of that which nothing here
closes: **a citation outlives the transient it accounts for**, so the only cheap remedy for a
temporary entry is a permanent hole in the accounting. Ruling 4 makes the transient unnecessary
rather than making the remedy fit it.

**The swap hole, unchanged and one entry wide in the owning root.** ADR 0033's reasoning is untouched.
