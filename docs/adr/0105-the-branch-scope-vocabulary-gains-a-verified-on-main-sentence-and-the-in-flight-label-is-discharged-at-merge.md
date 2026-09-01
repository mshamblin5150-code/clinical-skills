# The branch scope vocabulary gains a verified on main sentence and the in flight label is discharged at merge

[#737](https://github.com/mshamblin5150-code/clinical-skills/issues/737) is
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
ruling 4 meeting a case its premise does not cover: the pre-publish hook refused a real comment,
correctly by its own rule, and the rule's only accepted sentence was untrue of the safest state the
text could be in. Filed 2026-08-31 by #689's grilling, respec'd 2026-09-01 by #725's, and grilled
here 2026-09-01 against `origin/main` `e215f98`.

**Eight rulings, made by the clinician on 2026-09-01.** Nothing is built here; this is the record the
build reads.

## What the grilling found that the ticket did not

**Every claim below was measured by driving the module or querying the tracker, not reasoned from
the source.** Figures taken against the live tracker are dated floors that move on the next
publication, and nothing committed re-derives them.

**1. The receipt escape is narrower than the body states, and the body's own account of it is the
looser one.** #737 says the escape *"requires a merge receipt naming that issue."* `RECEIPT` is a
`fullmatch` on the **whole body**, so `receipt_matches_issue` is reachable only when the comment
says nothing else at all. Driven:

```
receipt only    ->  0   explicit branch state present
receipt + text  ->  1   missing Branch state ... labeled 'in flight'
```

No verdict, no coordination note and no sweep finding can ever reach that escape. Ruling 7 turns
this from a defect into a documented role.

**2. The trigger count in the respec is wrong in the direction ADR 0083 already corrected once.**
The Related section reads *"The trigger set here is three, not two."* Driven at `4903f1ea`, `grade`
refuses **five** distinct ways: a repo-relative Markdown link, an unresolved path **with** a
same-directory near miss, an unresolved path **without** one, text that self-declares completion, and
the `in flight` label; a resolved path with no trigger returns 0. ADR 0083 was corrected from *four*
to *five* on [#743](https://github.com/mshamblin5150-code/clinical-skills/issues/743)'s branch on
2026-09-01 and recorded that *"ratified prose disagreeing with its own adjacent table is the shape
worth recording."* The respec walked into the same undercount from below.

**3. `grade` is state-blind, demonstrated rather than read.** The same event with `"state": "open"`
and `"state": "closed"` returns **identical status and identical report**; the string `state` appears
nowhere in the derivation. `tracker_publish_hook` maps that report to `branch:in-flight` with posture
`deny`.

**4. The label has a documented add-time and no stated end, and nothing anywhere removes it.**
Exhaustive search of `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, both workflows,
`CLAUDE.md` and `tools/` finds no removal step: the only `--remove-label` occurrences are a generic
command-reference bullet and a flag-argument-skipping table in the hook's own parser.
`.github/workflows/tracker.yml` holds `issues: write` and never calls `gh issue edit`.

**5. The population is mostly stale and it moved twice during the grilling.** At the session's start
24 issues carried `in flight` — 20 closed, 4 open. #713 lost the label mid-session **while open**,
after its work merged, leaving **23 — 20 closed, 3 open**. Of the three, #715 and #717 are covered by
open pull request #797 on branch `codex/tickets-715-717` and are genuinely in flight.

**6. The discharge event is the merge, not the close.** #713 is the counterexample and it happened
during this session: work merged, ticket still open, label stale, removed by hand. It is the third
recorded hand-removal, after #714 on #725's session and #676 during a reopen. A close-time rule would
have reached none of them.

**7. The label has a second consumer and it is out of tree.** `in_flight_labels` is a **dead key in
this repository** — `map_scan.py` reads only `ready_labels` and says so in `DECLARED_LIMITS`, and
`tools/implementation_map.py` does not exist here. The out-of-tree `packet_status` does read
in-flight labels, per ADR 0089 and ADR 0090, and `CONTEXT.md`'s **Startable packet** is defined as
carrying *"nothing in flight"*. An all-closed packet answers `done` before that limb is reached, so
the harm is confined to a **mixed** packet — one open ticket beside a closed one still carrying the
label — where `claim` warns and `frontiers` reads the packet unavailable. Unverifiable from this
tree, and named rather than asserted.

**8. The repository's own prose already rules the label the wrong instrument.**
`docs/agents/issue-tracker.md` says *"the label scopes a ticket rather than an individual claim. Keep
the label as a useful queue signal; do not use it as the claim's provenance."* `grade` uses that
label as the sole trigger demanding claim provenance. `docs/agents/triage-labels.md` calls it *"the
tracker workflow's active-work state"* — a state nothing maintains.

## Ruled 2026-09-01

**1. `in flight` is a claim about the ticket and never about one comment on it, and that kills the
ticket's own third option.**

The label means an agent is working the ticket now, so unmerged work may exist on it. Whether **this
comment** rests on that work is not something the comment's text reveals. #737's decision 1 offers
*"narrow the `in_flight` trigger to text that cites unmerged work"* and calls it *"closest to the
rule's purpose"*; it is the one route the repository has already refused in writing.
`docs/agents/issue-tracker.md` says the self-declaration trigger is *"a bounded fallback for a missed
`in flight` label, not a claim that the checker can infer assertions from arbitrary prose"*, and the
#673 near-miss is the recorded proof that prose inference fails — `DECLARES_COMPLETION` matches
`Implemented locally` and not `Implemented on`, so a comment openly declaring unmerged work went
ungraded by it.

The term is recorded in `CONTEXT.md` as **In flight**.

**2. The vocabulary gains a third accepted form, and it is the only one that is checked.**

> **Branch state:** this text rests on `main` at `<40 hex>` as of `<YYYY-MM-DD>`.

Accepted only when the named commit is an ancestor of `origin/main`, settled with
`git merge-base --is-ancestor` — the call `tools/tracker_freshness.py` already makes, in a grader
that already shells `git ls-tree -r origin/main`.

**The verification is what makes this not the escape-hatch phrase the ticket forbids, and the reason
is an asymmetry the ticket did not name.** `BRANCH_SCOPE` is a pure regex: nothing checks the branch
exists, the SHA is real, or the claim is true. The existing sentence survives that because it is
**against interest** — *"my work is not on `main`"* weakens the author's own claim and nobody writes
it falsely to gain anything. A positive sentence is **for interest**, and an author staring at a
refusal has every reason to type it. Same grammar, opposite incentive. So the positive form is the
one that must be checked, and it is also the only one that **can** be.

**The two forms have opposite monotonicity, which is #737's own finding 3 arriving as an argument
for this ruling rather than against it.** The negative sentence is true when written and decays:
#725 published three blocks reading `is not on \`main\` as of \`2026-09-01\`` and merged that branch
about two minutes later the same day, with `main` advancing five times during the session. Once a
commit is an ancestor of `main` it is an ancestor forever. The date on the positive form is
decoration; the SHA is the anchor.

**3. An unverifiable positive claim is accepted and declared, never refused.**

Ancestry against a **stale** local `origin/main` is monotone in the safe direction: a stale ref is
only ever behind, so a commit that is an ancestor of the stale ref is certainly an ancestor of the
true one. Verification therefore succeeds with no network for any commit that landed before the last
fetch, which is nearly every real case, since a sweep re-derives at a base it just fetched. The
assumption is named: no force-push to `main`, and nothing in this repository rewrites it.

The residue is a commit claimed on `main`, not an ancestor of the local ref, with a failed fetch — a
state in which a false claim and a stale ref are indistinguishable. There the sentence is **accepted
with a declaration beside it**, which is ADR 0083 ruling 1's *"a context-blind grade is declared
rather than silent"* applied to an escape instead of a trigger.

**This creates a shape ADR 0083's table has no row for: a local, always-refusing trigger whose only
truthful escape is remote-dependent.** That table splits triggers by remote-dependence and
`branch:in-flight` sits in the local, always-`deny` group; nothing in it splits escapes. The trigger
keeps its posture and only the escape degrades.

**Refusing instead was rejected because it rebuilds this ticket's defect one layer down.** An author
with a true on-main claim and a failed fetch would have no publishable sentence at all — they cannot
write the negative form either, because there is no branch to name — and ADR 0083 finding 6 already
establishes that the staleness error runs in the restrictive direction, so it would be a false
refusal of true text. **The hook's unused `ask` value was rejected separately**: the work on this
tracker is done by unattended agents, and an `ask` in an unattended run is a stall rather than a
decision.

**4. The label is discharged at the merge, and teaching one reader to discount it is refused.**

Three limbs. `merge-receipts` removes `in flight` from each ticket its receipt already names — one
line beside a `gh issue comment` it already runs, in a job that already holds `issues: write`, at
exactly the moment the claim is discharged. The closed carriers are cleared once by hand.
`docs/agents/issue-tracker.md` gains the end-of-life sentence its add-time has never had.

**Having `grade` consult issue state was refused rather than deferred, and it is the option the next
session will reach for because it is one line.** It is the wrong model twice. It teaches one reader
to discount a label instead of correcting a false one, and the label has a second consumer where the
same staleness still bites. And **#713 is the case it cannot reach at all**: open ticket, merged
work, stale label, refusing every publication — `state == "open"` is true, so a state-aware grader
grades it exactly as today. The shape that bit this session is the one the cheap fix misses.

**Ruling 4 shrinks how often ruling 2's sentence is needed and never removes the need.** #715 and
#717 are genuinely in flight, and a sweep verdict resting on `main` still has to reach them.

**5. The blockquote marker stays required and the diagnostic is repaired instead.**

Six of the seven branch-state comments on #429 use the bold-only form the rule refuses, and they are
the corpus the next author copies from. The measured harm is not the marker: #716's session recorded
that written without `>` *"the declaration is inert and the refusal is unchanged, with the diagnostic
naming the finding rather than the malformed escape — so the first repair attempt failed identically
to no attempt at all."* That is this repository's recurring shape, a check that cannot distinguish
*did not try* from *tried and got one character wrong*.

So a near-miss report names which limb failed, prints a limb name and never body text, and is
**derived from the accepted pattern rather than typed as a second one** — `reference_scan.py`
importing `docx_write.REFERENCE_HEADING` instead of restating it, for that module's reason.

**Accepting the bold-only form was rejected** because `docs/agents/issue-tracker.md` publishes the
blockquote form for both existing sentences, the `>` is what renders a scope *block* set apart from
the claim the document asks it to sit above, and widening the grammar would give the newly
**verified** sentence two spellings — the one place a second spelling costs most. The six historical
records are a copy-source rather than records anybody grades, and #737 already forbids editing them,
so their only harm is to the author who copies one — who is exactly the author ruling 5 tells what
went wrong.

**6. `refuse, always` survives, and the coverage argument is total for anyone with a checkout.**

#737's decision 3 is that finding 1 is *"the premise of that ruling failing rather than the ruling
being wrong."* The premise is restored: every case now has a remedy. Text resting on `main` writes
ruling 2's sentence; text resting on an unmerged branch writes the existing one; an unverifiable
positive claim is accepted under ruling 3; a stale label is discharged under ruling 4; a malformed
attempt is named under ruling 5.

**Every checkout has a `HEAD`.** Either it is an ancestor of `origin/main`, and the positive sentence
is true, or it carries local commits, and the negative sentence is true. There is no third state, so
exactly one form is always available and always true.

Dropping the trigger to advisory would discard what ADR 0083 bought: `NOT_REACHED` row 2 is *"an
advisory finding may go unread"*, and that ADR records eight unread red workflow runs as the reason
a refusing hook exists. Refusing only where a remedy is verifiably available is unimplementable in
the honest direction, because deciding which remedy applies is the provenance question ruling 1
establishes the checker cannot answer.

**7. The receipt `fullmatch` is the shape of a narrow correct escape rather than a defect.**

`parse_merge_receipt` has exactly one production caller — the branch-scope escape itself;
`tracker_merge_receipt` publishes with `render_receipt` and never parses. And `changed-record` fires
on `issue_comment: created` with no exclusion for the bot, so when `merge-receipts` posts to an
`in flight` ticket **the workflow grades its own publication**, and this escape is what stops it
refusing itself.

For that one role `fullmatch` is not a limitation but the guarantee that a receipt cannot be prefixed
onto arbitrary prose. Widening it to a leading block was rejected: it would put a **fourth**
record-level form on an anchor that `NOT_REACHED` already says cannot compose three, for no capability
ruling 2 does not already supply.

**One consequence for ruling 4 is stated here rather than left to be found.** `merge-receipts` will
both remove the label and post a receipt to the same ticket. Either order publishes cleanly — if the
label goes first the trigger never fires, and if the comment goes first this escape carries it — but a
build that comments first and assumes the trigger is gone is relying on the escape without knowing it.

**8. A published negative block is a dated claim about a moment, and the document says so and names
the resolving command.**

A record published from a branch whose branch then merges permanently opens with a sentence that
reads as though the work is unmerged, and `docs/agents/issue-tracker.md` forbids the obvious repair:
*"Do not rewrite or delete it on merge."* Ruling 2 does not reach it, because such a record was
published before the merge, when the positive sentence was not true either.

**The information is not lost and that bounds the size of it.** The block carries the branch and the
commit, so any reader with a checkout settles the current state with the same
`git merge-base --is-ancestor` call ruling 2 makes. The defect is in how the sentence reads, and no
timestamp fixes that — #737's finding 3 says in as many words that it *"is not an argument for
timestamps"*, and at second resolution a past-tense claim still reads as present-tense to a skimmer.
So the document gains one sentence: the block is a dated claim about a moment and never a
present-tense one, the commit is the anchor, and ancestry settles the current state.

**A follow-on statement published at merge was priced and deliberately not filed.** It reaches only
tickets a merge claim names, so it is partial by construction, and its whole benefit is already
available to any reader who runs the command this ruling names.

## Consequences

**One build, on one ticket.** #737 is respecified against these eight rulings. Its body's finding 1
is corrected on the receipt escape's true width, its Related section on the trigger count, and its
population figures re-derived.

**Two declared limits get wider and both are named rather than discovered.**
`tracker_branch_scope.NOT_REACHED` carries *"the qualifier forms cannot compose — both accepted
qualifiers are record-level and anchored at the first line, so one record cannot independently date
two different branch relationships."* A third form makes that three mutually exclusive record-level
claims sharing one anchor, so `docs/agents/issue-tracker.md` states the rule for **mixed** text:
write the weaker negative sentence, which is always available and never overclaims. And ruling 3 adds
a remote-dependent escape to a local trigger, which ADR 0083's posture table has no column for; the
build states it beside that table rather than leaving the two records to disagree.

**Nothing here is filed as a further ticket.** Ruling 7 retires the receipt finding rather than
splitting it, and ruling 8 declines the follow-on statement on the merits.

## What none of it reaches

**The GitHub web UI, which no hook binds**, per ADR 0083. A comment typed there has no checkout, so
neither sentence is derivable, and the only grade is the workflow's — which under
[ADR 0002](0002-ci-runs-the-suite-at-the-merge.md) is advisory and blocks nothing.

**Whether a positive claim is about the right commit.** Ancestry proves the named commit is on
`main`; it does not prove the text was derived at that commit, and no mechanical check reaches that.

**The out-of-tree `packet_status`**, whose reading of a stale `in flight` label is described from ADR
0089 and ADR 0090 rather than driven, because that code is in another repository and this suite
cannot import it.

**A branch abandoned without merging.** Ruling 4 discharges the label at the merge, so a branch that
never lands keeps its ticket labeled until somebody removes it by hand.
