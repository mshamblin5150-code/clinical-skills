# The readiness refusal lands at the claim rather than at the push and startability and readiness stay two derived properties

[#726](https://github.com/mshamblin5150-code/clinical-skills/issues/726) was split from
[#679](https://github.com/mshamblin5150-code/clinical-skills/issues/679) as ruling 6 of
[ADR 0089](0089-the-map-gate-is-an-offline-grader-over-a-harvest-and-the-reconciliation-obligation-is-anchored-on-a-field-the-delta-sets.md),
to close the window that ruling declared and did not close: **a map disagreement entering between
pushes is detected at the next push, not at the relabel.** The proposed mechanism was a `PreToolUse`
hook on `git push`, running the map grader's harvest before every push.

Grilled 2026-08-31 at `840040e`, freshness gate `FRESH`. **Five decisions, ruled by the clinician on
that date.** The first one retires the ticket's mechanism entirely; the remaining four are about what
replaces it. Nothing is built here; this is the record the build reads.

## Measured before ruling, at `840040e`

Every figure below is dated and scoped to that base. Nothing committed re-derives the ones taken
against the tracker or against the out-of-tree helper, and each moves on the next merge.

**The harvest the hook would have run costs about five seconds.** Three consecutive runs of the
documented `tracker_scan.py` harvest command returned the same byte count in 5.28 s, 4.79 s and
4.97 s, over a payload of roughly five and a half megabytes. That is the real per-push price the
ticket asked to have measured rather than estimated.

**`tools/map_scan.py` does not exist.** #679 carries `ready-for-agent` and is unbuilt, so decision 1's
*"does it reuse #679's grader"* was a question about a module nobody has written.

**`claim` already holds the datum the recorded harm needed.** `cmd_claim` builds `Live(tracker, state)`
— a live tracker read carrying every ticket's labels — and then calls `packet_status`, which reads
closed-ness, hard blockers, external gates, assignees and in-flight labels and **never reads
`ready_labels`**. The readiness read sits two functions away, in `validate_against_live`. So #726's
own recorded instance — *"`claim --packet P670` answered CLAIMABLE"* while #670 sat mapped and
unready — was not a staleness window at all. The label was in hand and nothing looked at it.

**The map holds 70 packets: 66 of one ticket, 3 of two, 1 of five.** Seven packets have an open
ticket; every one of those is single-ticket and every one carries `ready-for-agent`. **The readiness
direction has zero live findings today**, which matches ADR 0089's reading of defect 2 at `7744c80`
and means refuse-versus-warn could not be settled on a measured false-alarm rate.

**#648, the ticket's second recorded instance, is closed and carries `bug` alone.** So *unready* is
not only `grilling`; a ticket that never gained a readiness label is the same finding. And 63 packets
are all-closed, so a row that did not exclude closed tickets would fire on the map's whole history.

**`packet_status` has five callers** — `frontiers`, `mermaid`, `render`, `cmd_claim` and the
collision-group check — and `frontiers` enumerates statuses by name twice, in
`unavailable = {"gated", "in-flight"}` and in its first-layer guard `status[pid] not in ("ready",
"deferred")`.

**`ready_labels` is read from the state block at both of its call sites**, defaulted rather than
held, and the state block lives in #596's body. So the configurable half of the rule is shared data
in one remote artifact rather than duplicated code.

**`validate_against_live` has an `unmapped-ready` finding and no `mapped-not-ready` one**, so `check`
carried the same hole `claim` did.

**`CONTEXT.md`'s glossary gates cannot reach the entry this record edits.**
`test_glossary_terms.py` checks heading uniqueness and `test_glossary_vocabulary.py` binds declared
vocabularies to code constants; neither reads the prose of the **Startable packet** entry.

**The landed `PreToolUse` infrastructure is one hook.** `.claude/settings.json` carries a `Bash`
matcher with an `if` cost guard, and `tools/tracker_publish_hook.py` holds the recognized route set
in code — [ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)'s
arrangement. It already performs a `git fetch` and a per-record `gh issue view` on every publication,
so network work inside a `PreToolUse` hook has precedent; the cost objection below is about
frequency and audience, not about the mechanism.

## The rulings

### 1. The trigger is the claim, not the push, and the hook is refused

**#726's mechanism is retired.** A `PreToolUse` hook on `git push` pays the largest available cost —
the five-second harvest, on the most frequent command in the repository — to warn the agent least
able to act, about a window whose own recorded instance it would not have caught.

Three things decide it, and the third is the one that matters:

**A push happens after the build.** The ticket's harm is stated as *"a drone consults the map before
building, so detection at the next merge can arrive after the work it would have prevented."* A push
hook narrows detection from the merge push to the branch push — frequently the same session, minutes
apart — and the agent it warns has already done the work and usually did not owe the reconciliation.

**The warned party is the wrong one.** Every session that pushes anything would receive a finding
about a coordination artifact it did not disturb and cannot repair without abandoning finished work.
That is the false-alarm-on-correct-work shape ADR 0089 ruling 5 refused a red job over, arriving on a
noisier surface.

**And the recorded instance needed no harvest.** #670's `CLAIMABLE` was a missing read, not a stale
one. The repair is that `claim` consults the readiness label it already fetched. It costs no network
call, no harvest, no hook and no settings entry, and it closes the one instance completely.

**The window is declared rather than closed, and that is unchanged from ADR 0089 ruling 4.** A
disagreement entering between pushes is still detected at the next push by #679's gate. What this
record removes is the claim that a push-time hook was the instrument for it.

**The candidate that survives as a fallback is named rather than discarded**: a `PreToolUse` hook on
the helper's `claim` command would put a harvest-backed check at the consultation point. It is
refused only because ruling 1's repair reaches the same instance for nothing, and it becomes worth
re-pricing if a disagreement is ever recorded that `claim` holds the datum for and does not read.

### 2. An unready ticket makes `claim` refuse, and the refusal names the tickets

`claim` already speaks both postures: it refuses on `blocked`, `gated`, `done`, not-in-map and
no-packet, and warns on `in-flight` and `deferred`. Readiness joins the refusals, ordered **after
`done` and before `in-flight`**.

**The precedence argument is already written in the helper.** `packet_status`'s docstring says
*"Blocking is checked before in-flight: a packet that is both assigned and hard-blocked reads blocked
— an assignee must not launder a blocker into a warning."* The identical argument holds one property
over: a ticket nobody may build must not be laundered into a warning because somebody assigned
themselves to it.

**Warning was refused because the advisory copy already exists.** #679's `map_scan.py` row is the
advisory reading of this same rule, in CI. A second advisory copy at the consultation point buys the
same guarantee twice, and a warning the model may read past is
[#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s *what a written
instruction cannot do is fail* rebuilt in a command.

**This is not #726's prohibited refusal.** That prohibition is about denying a `git push` and about a
CI job failing a merge. `claim` is a read-only question — *may I build this now* — and refusing it
blocks nothing; it sends the agent to a different packet.

**The mixed-packet objection is answered by the message rather than by weakening the row.** A packet
holding four ready tickets and one under grilling is the only shape where a refusal stops correct
work, and 66 of 70 packets cannot exhibit it. The refusal names which open tickets are unready, so a
claimant sees the obstacle and can split the packet by delta — the remedy the map already has, and
the one `claim`'s other refusals already print. Refuse-on-all and warn-on-some was priced and refused:
it makes the strongest finding the quiet one.

**Granularity was not an open question.** `cmd_claim --ticket N` resolves to `packet_of(N)` and then
decides packet-wise, so the row inherits packet granularity from a design decision already made.

### 3. Readiness is a second derived function, not a seventh status

The first spelling of ruling 2 put readiness inside `packet_status` as a seventh status. **The
glossary gate refused it.** `CONTEXT.md`'s **Startable packet** entry, landed with ADR 0089 the day
before, reads *"A claim about **sequencing** … **Orthogonal to readiness in both directions**."*
Folding readiness into `packet_status` makes the two terms non-orthogonal and falsifies a ratified
entry one day old.

So `packet_readiness` is its own derived predicate over a packet's open tickets, consulted beside
`packet_status` rather than inside it. That is ADR 0089 ruling 8 — *"Readiness and startability are
two properties and are written down as two terms"* — carried into the code rather than collapsed on
contact with it. **Two properties, two terms, two functions.**

**Ruling 2's ordering survives intact.** `cmd_claim` refuses on `blocked`, `gated` and `done` from
`packet_status`, then refuses on unready naming the tickets, then warns on `in-flight`. Only the
phrase *seventh status* retires.

**`unready` joins `unavailable` in `frontiers`, beside `gated`.** That set exists so a packet and its
successors *"sit outside every frontier until the gate clears"*, and unreadiness clears when somebody
respecs a ticket, never when a predecessor merges. Left out of it, an unready packet drops out of
frontier 1 by the first-layer guard and **reappears under `## Later frontiers`**, rendering as though
a merge will unlock it — a new false claim in the same rendered view #679 was filed over.

**The cheaper option is named rather than left implied.** Checking readiness in `cmd_claim` alone
would have left the glossary untouched and `render` still printing an unready packet under
`## Current frontier`. Reading the rendered frontier *is* consulting the map, which is #726's own
harm statement, so a repair that fixes the command and not the view fixes half the instance.

### 4. The rule stands on three surfaces and the duplication is declared

`claim` refuses, `check` gains a `mapped-not-ready` finding, and #679's `map_scan.py` row stays.

**They are three guarantees, not one rule copied twice.** The helper is discretionary; a drone that
never runs `claim` is exactly the case #679 exists for, and #670 was caught by neither. That is
[#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s argument — *what it buys is
the guarantee that the detection ran, and not detection* — and it is `phi_scan`'s own arrangement,
where a pre-commit hook and a CI `--all` run grade one rule on two surfaces and this repository has
never called that a duplication.

**The [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220) objection is real and
is answered by declaring rather than by binding.** One rule, two implementations, in two
repositories, and **no test can bind them**: this repository's suite cannot import the helper and the
helper's suite cannot import `tools/`. That is worse than two copies of prose, because neither copy
is in the other's tree. So `map_scan.DECLARED_LIMITS` names that the helper implements the same
predicate out of tree, that nothing binds the two, and that they share only the `ready_labels`
vocabulary through #596's state block. That is ADR 0089 ruling 7's own move: for a remote artifact
the content cannot be bound, so the address is named and the residue declared.

**The divergence risk is smaller than it looks and is named where it is not.** Both sides read
`ready_labels` off the state block, so the configurable half is shared data. What can genuinely
diverge is the predicate, so both are stated identically: **an open ticket in the packet carrying no
label in `ready_labels`** — closed tickets excluded, and a packet with no open tickets already
answering `done`.

**Writing the predicate once was priced and refused.** The only place both implementations can read
is #596's state block, and putting a predicate in a coordination artifact neither suite can test is
worse than two three-line copies whose shared vocabulary already lives there.

### 5. #726 lands before #679, and the `blocked` edge it carried points the wrong way

After rulings 1 through 4, #726's entire mechanism is in one out-of-tree file. Its in-tree footprint
is this record, one sentence of `CONTEXT.md`, #596's prose, **and one row in
`map_scan.DECLARED_LIMITS` — a file #679 creates and #726 never calls.**

That row is the only coupling between them, and it points the opposite way to the label #726
carried. Nothing in the `claim` repair reads `map_scan.py`; #679 shipping first only means its
limits object omits its largest declared limit until a follow-on adds it. So **#726 goes first,
alone**, and #679's build writes the duplication row against a fact already true rather than one it
has to predict.

**The honest edge is REBUILD-SAVING at most.** Building #679 first is not wrong, it is one extra edit
to `DECLARED_LIMITS`. A HARD edge would be a false claim, and the helper's refusal to infer an edge
from a shared filename is exactly what these two have.

**Folding into P679 was priced and refused.** One branch touching the helper once is genuinely
cheaper, but it makes a few-line repair that closes the recorded instance wait on the larger unbuilt
gate, and it widens a scope ADR 0089 ruled.

## Derived from precedent rather than ruled

**The `CONTEXT.md` repair lands with the build and not with this record.** The **Startable packet**
entry's closing clause — *"the map renders startability and checks readiness nowhere"* — is **true
today** and becomes false when the build lands. Editing it now would publish a claim about code that
does not exist, which is [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s
shape. No glossary gate reaches that sentence, so nothing fails either way; the ticket's `Done when`
carries it instead.

**No new glossary term.** `packet_readiness` is the aggregate of **Ready ticket** over a **Packet**,
and both terms are already defined. A third heading for a derived aggregate would add a collision
surface for nothing.

**The out-of-tree half is tested out of tree.** `test_implementation_map.py` is where the refusal is
driven red before it is believed. This repository's suite cannot reach it, which is ruling 4's
declared residue rather than a gap this record leaves.

**No figure here is restated elsewhere.** Every count and timing above is dated to `840040e` and
re-derived by the documented harvest, `git log` and the helper's own commands.

## What must not come out of this

**A hook on `git push`.** Ruling 1 refuses it on measurement, not on cost alone. Re-proposing it
needs a recorded disagreement that `claim` cannot see.

**Readiness folded into `packet_status`.** Ruling 3 keeps two properties as two functions, and
collapsing them falsifies a ratified glossary entry.

**A machine that writes packets.** ADR 0089's prohibition stands unchanged. `claim` refuses and
reports; splitting a mixed packet stays a delta a person writes.

**A count of packets, tickets, timings or API calls written into prose outside this record.**
