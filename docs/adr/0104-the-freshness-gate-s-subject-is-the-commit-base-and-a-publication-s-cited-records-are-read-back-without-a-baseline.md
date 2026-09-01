# The freshness gate's subject is the commit base and a publication's cited records are read back without a baseline

[#728](https://github.com/mshamblin5150-code/clinical-skills/issues/728) records a sweep that ran
`tools/tracker_freshness.py` immediately before posting, got `FRESH`, and published three claims that
were already false. Nothing was wrong with the procedure: the base had not moved, the commands were
right, and the gate answered honestly about the question it was asked. **It was asked the wrong
question.**

Grilled 2026-09-01. **Ten rulings, made by the clinician on that date.** Nothing is built here; this
is the record the build reads.

## What the grilling found that the ticket did not

**Every figure below was measured against the live tracker on 2026-09-01 and is a dated floor.** The
tracker moves on every comment, so none of them is re-derivable from anything committed, and none is
restated anywhere else in this tree.

**1. Decision 2's blocker is false for every record a verdict names.** The ticket says a re-read
*"needs the sweep to have recorded which artifacts it read, which nothing does today."* The
pre-publish hook already holds the publication's own text as `Publication.text` and already sends it
through `phi_scan` and `tracker_branch_scope`. Every record the text names is parseable out of a
string the hook is holding, and `closing_keyword_scan.py` already carries that pattern shape. Nothing
has to be recorded.

**2. Decision 4's route is one token on a call that already happens.** `Extraction.number` carries
the number being published to, and `tracker_publish_hook.fetch_issue` at `:685` runs
`gh issue view <n> --json number,labels,url`.

**3. Citation is not dependence, and the ticket's own evidence proves it.** Its 20:34 comment records
*"21 issues carry `in flight`, all 21 closed"* — a claim whose falsifier was #676, which that sentence
**never names**. No re-read of a named record reaches it.

**4. The founding instance is the most expensive record in the tracker.** Across 792 issue and
pull-request records, body length ran to a median of 3,293 characters and a p90 of 6,639.
**#596 is 100,737 — the largest by five times, and the record #728's recorded instance is about.**

**5. Citation density is small and its tail is a sweep summary.** Over 3,159 comments, distinct `#N`
per comment ran median 2, mean 2.8, p90 5, **max 42** — on #496, a comment opening *"All 37 open
tickets read, one at a time."* 166 comments cite none.

**6. The mention-versus-use population is 7% and its cost here is inverted.** Of 13,445 bare `#N`
occurrences in comments, 149 sit inside a fenced block, 646 inside inline code and 154 inside a
blockquote line; 3,427 are the tail of an `issues/` or `pull/` URL and 3 are `owner/repo#N`.

**7. One batched GraphQL request covers the worst case measured.** `issueOrPullRequest(number:)`
resolves both kinds, so the `gh issue list` trap #130 records — that command excludes pull requests —
does not apply. Five citations returned in 0.87 s; **42 citations returned in one request in 2.55 s**,
moving 156 KB over the wire.

**8. `gh api graphql` exits 1 on an unresolvable number and still writes a complete answer.** One
real number and one bogus one returned status 1 with a payload carrying one resolved record, one
`null` and one top-level error. `fetch_issue` passes `check=True`, so the code as it stands raises on
exactly that case.

**9. `tools/tracker_publish_hook.py` is the only module in `tools/` that shells `gh`.** The seam it
established is that `phi_scan.scan_text` and `tracker_branch_scope.grade` are offline graders taking
data and returning findings, and the hook owns the socket and feeds them.

**10. `tools/tracker_freshness.py` carries no limits object.** 111 lines, a docstring, no
`NOT_REACHED` and no `DECLARED_LIMITS`.

**11. The two copies of the two-checkpoint rule have already drifted, in this ticket's own thread.**
`CLAUDE.md` gained a `Tracker freshness` section naming #728 as owner of the open boundary;
`docs/agents/issue-tracker.md`'s section did not move. Three sweeps on 2026-09-01 — at 15:56, 20:26
and 21:43 — each re-derived Done-when row 1 as unmet, by running the same greps.

**12. `additionalContext` reaches the model, and one ratified figure disagrees with its own release.**
The live hooks reference states that when set on `PreToolUse` the additional context is visible to
Claude as it makes its next decision, and that plain stdout on exit 0 reaches only the debug log.
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
finding 1 records `permissionDecision` as taking four values; the documentation gives three.
`claude --version` here is **2.1.241** — the same release ADR 0083 measured, so this is not version
drift. It changes nothing ruled below and is filed separately.

## Ruled 2026-09-01

**1. The population is three classes and only two are reachable, and the third is declared by name.**

A verdict about a tracker record attaches to it three ways: **(a)** the record being posted on, **(b)**
a record the text names, and **(c)** an aggregate naming no record at all. Finding 3 is the whole
argument for splitting them — (c)'s falsifier is a record the sentence does not mention, so no re-read
of any named record reaches it, and **a mechanism's unit is the thing it re-reads.** An aggregate over
the tracker has no smaller thing to re-read than the whole tracker, which is the always-red re-harvest
[#260](https://github.com/mshamblin5150-code/clinical-skills/issues/260) already refused and which
#728's own *What must not come out of this* forbids.

So (c) is **declared permanently unreachable, by name**, rather than left as a residue. Naming it does
work a general caution cannot: it tells the next sweep that **a sentence naming no ticket number is a
sentence no mechanism will check**, which is an instruction a writer can act on.

**2. The mechanism has no baseline. It injects current state and asserts no drift.**

Decision 2's *"comparing against what was read"* hides the build, because a re-read reports current
state and not movement. A comparison needs a baseline, and every available baseline keys on
`updated_at` — which #728's own 20:26 comment already ruled *"an upper bound on body movement rather
than a measure of it."*

The disqualifier is worse than imprecision. **A sweep inflicts the drift it would then be refused
for.** Comment 1 lands on #596 and moves its `updated_at`; twenty comments later a verdict cites #596
and any `updated_at` gate fires, correctly by its own rule, about a change the sweep caused. Over a
29-comment sweep that climbs toward always-red — #260's refused cost arriving through a different
door than the one this ticket guards.

**The conceded cost is that an injection cannot fail**, which is
[#679](https://github.com/mshamblin5150-code/clinical-skills/issues/679)'s thesis and this
repository's most-cited rule, and ADR 0083 ruling 4 already refused advisory on this very hook. The
distinction is narrow and is the reason this ruling stands: **`additionalContext` is not a written
instruction and not an unread red run.** Finding 12 establishes it arrives inside the deciding context
at the deciding moment, unlike a sentence in `docs/agents/issue-tracker.md` read forty minutes ago and
unlike a CI status nobody opened. A refusal would be stronger, and every available refusal predicate
keys on a field already ruled an upper bound.

**3. The fingerprint is metadata plus a body length, never the body.**

Per cited record: `state`, `labels`, `updatedAt`, and body length — roughly 200 bytes. Finding 4 rules
out the body on the mechanism's own terms: **its cost peaks exactly where its value peaks**, so the
publication most worth guarding is the one most likely to get the guard turned off.

The second reason is the one a build would not find on its own. `tools/tracker_publish_hook.py`'s
docstring states *"It never prints the text it scans. Counts, rule names, and the field to edit are
the complete reporting surface."* A length and a timestamp are counts. A body is not, and widening
that surface in passing would change the hook's contract inside a feature that is not about it.

**What this costs is declared rather than left to be found: the injection says a record moved, never
what moved in it.** A verdict about a body's content is told to go and look; it is not told it is
wrong. That is the direct consequence of ruling 2.

**4. The citation set takes no mention-versus-use exclusion, and the reason is written beside it.**

`spelling_scan` reads a backticked form as a mention, `differential_scan` does the same, and this
repository records three separate occasions of a scanner broken by prose describing the rule it
grades. **That rule does not transfer, because the failure directions are inverted.** In every module
carrying it, a false positive refuses something correct. Ruling 2 settled that this injection makes no
claim, so an over-included `#N` costs one fingerprint line and produces no finding, no refusal and
nothing to adjudicate — while an under-included one loses a staleness flag silently, which is the
whole subject of the ticket.

So the set is **every `#N` and every `issues/N` or `pull/N` URL tail, wherever it sits**, unioned with
`Extraction.number` — which covers class (a), the record the body may never name. Finding 6's 7% is
admitted deliberately, and the blockquote share matters most: **a blockquote is where this repository
puts branch state**, which is a claim about the world that goes stale.

**The reason is recorded beside the rule because the next author will read its absence as an
oversight**: the mention rule belongs to a checker that refuses, and this one only reports.

**A number resolving to nothing is reported as not found, never dropped** — the extractor-coverage
rule, an unread reference visible as unread. **No heuristic guesses whether a `#N` is "really" a
citation**: a stray number costs one lookup and one honest line, and a suppressor would be a rule
about intent, which no matcher here is allowed to infer.

**5. One batched GraphQL request per publication.**

Finding 7 measures the worst case in the tracker's history at one request and 2.55 seconds, against
the documented harvest's eight paginated requests over 792 records. A whole-tracker metadata cache was
refused outright: **a cached harvest is by construction a stale read, which is the bug.**

**The body crosses the wire and is never injected**, which is the module's existing discipline rather
than a compromise — GraphQL exposes no length field, so the hook measures locally what it does not
print.

**Finding 8's exit status is parsed, not trusted.** A non-zero `gh` exit carrying a usable payload
must be read, or ruling 4's not-found reporting is unreachable — #150's shape with the sign flipped,
where a traceback became a verdict and here a verdict would be discarded as a traceback.

**6. The boundary is stated on the gate's own printed line, in every mode.**

[#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258) is not analogous here, it is
the same defect on a different command: an unqualified clean result printed at the moment a reader is
deciding whether to trust it. `tracker-freshness: FRESH HEAD=… origin/main=…` is read as *I am
current*, and nothing on it says what it is current about.

**It prints on `STALE` and `DID NOT CHECK` too**, on #258's own second-order reason — a reader who
learned the qualifier beside `FRESH` would read its absence elsewhere as the stronger claim.

The permanently-unreachable class from ruling 1 belongs in the prose rather than on the line, because
it is an instruction to a writer rather than a scope note on a command.

**7. The readback is an offline module and is not named for freshness.**

Finding 9's seam is taken as it stands: `tools/tracker_readback.py` takes a body string and returns a
citation set, and takes fetched records and returns fingerprint lines; the hook makes the one request
and passes the result in. The grading half stays stdlib-only, offline and testable, which is the
property the directory is organized around.

**The name is a ruling and not a label.** `tracker_freshness` names the commit-base gate, which
**asserts a relationship** — `STALE` is a finding. Ruling 2 settled that this one **asserts nothing**.
A shared root would invite the next reader to assume a shared subject, which is the misreading #728's
own title turns on. `tools/test_glossary_collisions.py` exists because a term carrying two senses is
recorded rather than left latent, and this collision is avoidable by not making it.

**The limits split follows the objects rather than the feature.** `tracker_readback.NOT_REACHED` owns
what a citation set and a fingerprint do not establish — ruling 3's *a record moved, never what moved
in it*, and ruling 1's class (c). `tracker_publish_hook.NOT_REACHED` already owns the delivery limits
and gains one row for a fetch that fails, **degrading context-blind and saying so**, which is ADR 0083
ruling 1 applied rather than re-argued.

**8. Two tickets, one ADR.**

The declaration is buildable today with nothing to guess, which is what `ready-for-agent` promises and
what [#8](https://github.com/mshamblin5150-code/clinical-skills/issues/8) is recorded here as having
broken. Finding 11 is the reason it does not wait: **row 1 is the row every sweep re-derives**, three
times on one day, each running the same greps to the same verdict.

The coupling is weaker than it looks. Everything the declaration says stays true whether or not the
readback exists, and the readback **adds a clause rather than rewriting one**.

**The ADR is single and both tickets cite it**, because the seven design rulings are one argument and
the reason the declaration says what it says is the reason the readback is shaped as it is. Two ADRs
would put the *why* in one file and the *what* in another, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s two-copies problem with the
copies made deliberately.

**9. The readback fires only where the extraction yielded text.**

A label-only `gh issue edit` is a publication under `PUBLISH_ROUTES` and asserts nothing about any
record. Class (a)'s verdict lives in the body, so **no body, no verdict, nothing to be stale.** The
guard is on a tuple the hook already builds.

**Title and body are one citation set, not two.** `tracker_scan.records_from_github` splits them
deliberately *"so a finding says which of the two a reader has to go and edit"*, and that reason does
not transfer — a readback names records rather than fields, so there is nothing to go and edit. **The
asymmetry with the sibling is stated, or the next author reads it as an oversight.**

**A text-free publication is silent and never reported as clean.** ADR 0083 ruling 2's three outcomes
already carry the vocabulary; this is a fourth member of the silent class, and it belongs there rather
than in a report, because *no stale citations* on a label edit reads as a checked publication.

**10. The boundary is one owned object and the prose points at it.**

Finding 10 records that the module has none and finding 11 records the drift that costs. ADR 0093
ruling 4 permits a section without a limits object and requires a measurement to earn one; **this
ticket is the measurement.**

`tracker_freshness.NOT_REACHED` owns three rows — the gate reads the commit base and no tracker
record; a verdict about a tracker record is current only as of when it was read; and a verdict naming
no record number is reached by no mechanism, permanently. Both Markdown files **point at the object
and copy no row**, on `reference_scan.NOT_REACHED`'s arrangement.

**The printed line renders from the object rather than holding a literal.** Otherwise the command's
output and the declaration are two hand-kept answers to one question, which is #220's recorded cost.
The bind is `spelling_scan.vocabulary_covered`'s, and `CLAUDE.md` already records why the obvious test
is insufficient there: asserting the printed line equals the object catches a copy that has drifted
and passes a copy that agrees today.

## Consequences

**#728 is respecified to ruling 6 and 10 alone** — the declaration — and moves to `ready-for-agent`.
Its body's clipped quotation of `CLAUDE.md` is repaired, having been flagged unfixed by two separate
sweeps, and its `implementation_map.py check` is corrected to `tools/map_scan.py`, which
[ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md)
also carries in the wrong spelling at one of its two mentions.

**The readback is its own ticket**, citing rulings 1 through 5, 7 and 9. Finding 12 closed its one
open premise, so it is `ready-for-agent` rather than `grilling`.

**Finding 12's disagreement is a third ticket**, because it is about ADR 0083's account of a hook
contract and not about either deliverable here.

## What none of it reaches

**Whether the model acts on the injection.** The hook returns the context; no test in this repository
can assert it was read. That is ruling 2's conceded cost and it is a declared limit rather than a gap
somebody will close.

**A verdict about a body's content.** Ruling 3 flags the record as moved and answers nothing about
what changed in it.

**Class (c), permanently** — ruling 1, by construction rather than by cost.

**Every route ADR 0083 already named**: the GitHub web UI, a session with hooks disabled or
overridden, the workspace trust gate, and GitHub's retained pre-edit revisions per
[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212).

**And roughly 2.5 seconds added to a heavily-citing publication**, paid once per comment — twenty-nine
times in a full sweep.
