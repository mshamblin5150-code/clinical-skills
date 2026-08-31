# The map gate is an offline grader over a harvest and the reconciliation obligation is anchored on a field the delta sets

[#679](https://github.com/mshamblin5150-code/clinical-skills/issues/679) was filed after a
reconciliation of the implementation map found that its Maintenance rule 3 — *reconcile at every ADR
closeout that creates, splits, resequences or invalidates work* — is prose in an issue body, and had
gone eighteen ADRs without firing. While stale the map's rendered frontier read *"Of the packets
below, none is startable"* while twelve packets were startable: an agent asking the coordination
artifact what to build got a settled negative from a mechanism that could not have known.

The map had also declared its own staleness in prose, and nothing acted on it for four further ADRs.
That is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214) one level up —
**what a written instruction cannot do is fail** — arriving on the artifact whose whole job is to
answer *what can I build*.

Grilled 2026-08-31. **Nine decisions, ruled by the clinician on that date.** The ninth exists because
the glossary gate refused the eighth's first draft, so the tree found it rather than the session.
Nothing is built here; this is the record the build reads.

## Measured before ruling, at `7744c80`

Freshness gate `FRESH`. Every figure below is dated and scoped to that base; nothing committed
re-derives the ones taken against the tracker, and each moves on the next merge.

**The defect fired during the grilling, which is the fifth recorded instance.** The map's own
`## Snapshot` reads `default-branch commit: 5177d4a`, `generated: 2026-08-30`, and
`live ready-for-agent tickets: 4`. Between that commit and the base: **22 commits, 6 ADRs added
(0083 through 0088), 0 reconciliations**, and `implementation_map.py check` reports **five**
`unmapped-ready` findings.

**One harvest carries both halves of the ticket's *Done when*, and it is a command this repository
already documents.** The `tracker_scan.py` harvest —
`gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100"` — returned 330 issues at the
base; **#596's machine-state block is in it**, and every row carries `labels` and `assignees`. So
both readiness directions are computable with **no socket at all**.

**The same harvest carries no dependency edges.** `blocked_by` is a separate call per ticket at
roughly 0.58 s, so `hard-edge-not-native`, `native-edge-undeclared`, `packet_status` and `frontiers`
are the part an offline grader cannot reach. The map holds **71** distinct mapped tickets, of which
3 were open.

**The helper already has the seam a third adapter needs.** `GitHub` is one class whose every method
*"mirrors one on the test fake"* — `issues`, `blocked_by`, `get_issue`, `update_issue_body`,
`create_issue`. A harvest-backed reader is a slot that exists rather than a rewrite.

**Defect 2 re-derives and has no live instance today.** `validate_against_live` `continue`s on
`number in mapped` before it reads labels, so a mapped ticket that stops being ready is invisible;
`packet_status` reads closed-ness, hard blockers, gates, assignees and in-flight labels and **never
reads a ticket's readiness label at all**. #670, the recorded instance, has since resolved, and the
direction had zero live findings at the base.

**Two figures in the ticket's first comment have aged out and one has not.** Six open tickets
carrying `ready-for-agent` and `blocked` is now **one**, #646. But **#87 still carries `blocked`
with a `blocked_by` of length 0** — its gate is prose — so that comment's live datum re-derives
exactly.

**The `every ADR is cited` anchor is unusable and was measured rather than reasoned.** The machine
state cites 55 distinct ADR numbers; the highest is **0083** against **0088** on disk. But **33 ADRs
on disk are cited nowhere in the state**, most of them legitimately, so that anchor could only ever
be a forward high-water mark and would need an exclusion list of 28 historical entries to start.

**The snapshot line is rewritten by a bare `publish`.** `publish_body` calls `render(state, live,
snapshot)` and re-emits the same state block with a fresh snapshot, so the commit recorded there
advances without a reconciliation having happened — and Maintenance rule 8 makes every `/implement`
closeout publish.

**The surfaces are asymmetric in exactly the way that decides the question.** `checks.yml` checks out
with `fetch-depth: 0` and holds `contents: read` plus `pull-requests: read`. `tracker.yml`'s record
job is a **shallow** checkout of the default branch with `contents: read` only. The repository is
**public**.

**The hook surface is ruled in and unbuilt.** `tools/hooks/` holds `commit-msg` and `pre-commit`
only, `.claude/settings.json` carries no hooks, and the `PreToolUse` work of
[ADR 0077](0077-a-digest-is-a-redaction-only-where-its-keyspace-is-large-and-a-date-literal-s-is-not.md)
ruling 5 and [ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md)
sits in the map as `P670+706`, on the current frontier.

**`CONTEXT.md` carries no map vocabulary.** Its `### Tracker` section defines `Binding`, `Citation`,
`Closing hazard`, `Merge receipt`, `Empty plan`, `Authored message`, `Declared no-binding`,
`Publish route` and `Unreadable body`, and nothing about packets, readiness or reconciliation.

## The rulings

### 1. The helper splits; it is not vendored and it is not left whole outside

A new offline grader lands in `tools/`. It reads a harvested issues file and grades the
map-disagreement invariants. **Every mutation stays in the out-of-tree helper**, which keeps its `gh` calls, its
`publish`, its `apply-delta` and its `audit`.

This is the only candidate that departs from no ratified shape. Vendoring the helper whole would put
a module in `tools/` that shells out to `gh` **and** mutates a remote artifact, which is two
departures rather than one; leaving it entirely outside reduces to *no gate*, since the map is an
issue body and anything grading it reads the tracker. The split is
`tracker_merge_receipt.py`'s arrangement exactly — a documented `gh` command writes a file, the tool
reads it offline, the workflow performs any mutation — and it reuses the harvest command already in
`CLAUDE.md` rather than inventing one.

The cost is named rather than discovered: **the in-tree gate grades one family of invariants and not
the map.** Edge agreement, gate targets, packet status and every frontier claim stay unreachable from
CI and continue to need a session running the full helper.

### 2. The harvest carries issues, plus dependencies for the tickets carrying `blocked`, in two passes

Issues alone cannot reach the third direction: the grader sees the `blocked` label and cannot
tell a prose gate from a native edge. Harvesting dependencies for **every** mapped ticket would reach
the edge invariants too, and is refused — those are about **edges**, which is the semantic half this
ticket rules stays a person's judgment, and the full helper already grades them in session.

The fetch set is keyed on the **label** rather than on the map, so it costs one call per `blocked`
ticket rather than a fixed 71.

**Two fixed commands, never one command with a loop.** A first pass over the issues file grades both
readiness directions and prints an explicit *not graded* line naming the tickets whose gates were not
read and the command that reads them; a second pass takes that file and grades the third direction.
A documented procedure whose input set comes from parsing the first command's output is one a session
gets wrong, and a run that only had the issues file must **say so** rather than report a clean third
direction it never looked at.

The residue is accepted in both directions: **`blocked` is graded as a label against an edge, never
as a reading.** A ticket whose prose gate has genuinely cleared, still carrying the label, is
indistinguishable from a real finding; a ticket that should carry `blocked` and does not is invisible
at every harvest width.

### 3. Both limbs are built, and the obligation limb is anchored on a field the delta sets

The **label-keyed** limb grades consequences: a ready ticket in no packet, a packeted ticket that has
stopped being ready. The **ADR-keyed** limb grades the obligation, which is the ticket's own thesis —
*the reconciliation stays a judgment; the obligation to have made it becomes mechanical*. It is the
only thing reaching the class the label-keyed limb structurally cannot: an ADR that **resequences
already-mapped packets**, both of them mapped and both still ready, which is what ADR 0074 did in
ruling #645's row into #550's build.

The anchor is a new `reconciled_through` field on the machine-state block, set by `apply-delta`. The
in-tree grader compares it against `git log <that sha>..HEAD -- docs/adr/`.

**The two cheaper anchors are refused on measurement.** The existing snapshot commit is free and
**launderable by a bare `publish`** — in precisely the resequencing case the limb exists for, since
the label-keyed limb covers every other case and not that one. The highest-cited-ADR anchor is free
and not launderable, but 33 ADRs on disk are cited nowhere, so an ADR that honestly creates no work
would have nowhere to be recorded as such and the limb would fire on correct work with no remedy but
inventing a citation.

`reconciled_through` is **not a second copy of the state**. It records a fact about the map's own
reconciliation, which is the map's own business, and mirrors nothing the tracker holds.

This ruling reopens the out-of-tree helper: the split of ruling 1 holds, and the helper gains a field
it must write.

### 4. The surface is `checks.yml`, on `push: main` and `workflow_dispatch`

It is the only surface holding a full git history and a token at once, it is where
[ADR 0002](0002-ci-runs-the-suite-at-the-merge.md) puts merge-time guarantees, and it is where the
race is visible: a closeout that reconciles correctly at its own base can be stale before it pushes.
The permissions block gains `issues: read`.

**`pull_request` is excluded because the map is reconciled after merge** — Maintenance rule 8 says
so — making a PR-time run stale by design and red on nearly every pull request.

**`tracker.yml` is excluded by its own ratified reasoning.** It is where a relabel is visible, and
its header carries [#260](https://github.com/mshamblin5150-code/clinical-skills/issues/260)'s ruling:
re-harvesting the whole tracker on every comment would replay already-triaged findings until a new
one became one more line in an always-red report. A map grader **cannot** be incremental, and its
findings persist until somebody reconciles.

**`tracker.yml`'s merge-receipt job is excluded too**, though it is merge-time and already privileged:
it fires on `pull_request_target: closed`, and changes land here by local `git merge --no-ff` and a
push, so a gate on the merge button watches the wrong door.

The window is declared rather than closed: **a disagreement entering between pushes is detected at
the next push, not at the relabel.** Closing it means a scheduled run, which adds a cron to a repository that
has none and re-creates the always-red report on a page nobody opens.

### 5. Findings are advisory; a check that could not run fails the job

On `push: main` GitHub has already merged, so there is nothing to refuse, and ADR 0002 makes nothing
here a required status check. The one live lever is whether the step fails the job.

**Failing on a finding is refused because it fails correct work.** Five findings were pending at the
base and would have been pending for days, which is #260's always-red report arriving on a second
workflow. Worse, a session that declines to invent a packet placement during an unrelated
implementation has behaved **correctly** and would have its merge marked red for it — the
false-alarm-on-correct-work shape refused on `spelling_scan`'s suffix rules, `case_study_scan`'s
stop-criterion row and [#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215).

**The ticket's own clause is a statement about exit 2, not exit 1.** *An advisory check that crashed
is indistinguishable from one that passed* is answered by failing the job when the check could not
run; [#150](https://github.com/mshamblin5150-code/clinical-skills/issues/150) is the recorded
instance, a traceback exiting 1 and reading as a genuine zero.

**The posture is carried by a flag on the tool, never by logic in the YAML.** The tool keeps the
house convention — 0 clean, 1 finding, 2 did not scan — and the workflow passes a flag that converts
1 to 0 and leaves 2 alone. That is `--allow-no-corpus`'s precedent and it exists for the reason
`checks.yml` already states in a comment: interpreting an exit status in YAML is a judgment about the
tool that the tool does not make and nothing re-derives. The flag in the file **is** the record that
this job knowingly treats findings as advisory, and a local run gets the un-laundered status.

The weakness is named rather than argued away: **an advisory finding on a page nobody opens is #214
one level up.** What distinguishes it from the map's own ignored self-declaration is where it lands —
the summary of the merge whose session owed the reconciliation, rather than an issue nobody re-read.

### 6. Nothing attaches in session; the map's prose gains a pointer, and the hook is a follow-on

Maintenance rules 3 and 8 are edited to name the gate and what it cannot see, so the prose stops
asking to be remembered and starts naming what will catch it.

**No new written closeout step.** A written step in a skill is exactly what #214 says cannot fail and
is the mechanism that went eighteen ADRs without firing; adding a second one at a new address
re-creates the defect rather than closing it.

**A `PreToolUse` hook matching `git push` is the right in-session mechanism and is a different
ticket.** ADR 0083 ruling 1 measured `additionalContext` as the one spelling that reaches the model,
so the hook would be a mechanism rather than an instruction, and it would narrow the detection window
from *the next merge* to *this push*. It is deferred because it depends on `P670+706` landing first
and because it puts a whole-tracker harvest in front of every `git push`; building it here would make
#679 block on a packet that is only on the frontier, while #679 is unblocked today.

### 7. The map holds a pointer to the declared limits, never a copy, and the address is checked at run time

Every precedent binding a limits object to its prose binds **tracked files**, and #596's body is not
one: no tool in `tools/` opens a socket, so no test here can read it.

The map's Maintenance rule names the module's limits object and carries no rows of it. The two
in-tree copies — the module docstring and `CLAUDE.md` — bind to the object by test as usual. Because
a pointer can still rot at the **address**, the grader asserts at run time that #596's body names the
module, which is the only binding available for a remote artifact.

Having the grader check a **copy** in the map body is refused: it buys the disagreement in order to
police it, against this ticket's own prohibition on a second copy of the state. Check the address,
which nothing else can re-derive, and refuse to have content there to check.

### 8. Readiness and startability are two properties and are written down as two terms

The conflation is not cosmetic; **it is why defect 2 exists.** `packet_status` computes a packet's
standing from blockers, gates, assignees and rebuild-saving predecessors and never reads a ticket's
readiness label, so a packet can be startable while holding a ticket nobody may build. The map
renders one property and this gate enforces the other.

Five terms land in `CONTEXT.md`'s `### Tracker` section — **ready ticket**, **startable packet**,
**packet**, **reconciliation**, **map disagreement**. The pair that earns its place is the first two: with them
written down, defect 2 is a sentence anyone can state — *the map renders startability and never
checks readiness* — instead of a bug found by reading a `continue`.

The module is named for the vocabulary rather than for one limb: **`tools/map_scan.py`**, on
`tracker_scan.py` and `block_scan.py`'s naming. A name built on *readiness* would describe one of its
three limbs and mislead about the other two.

### 9. `Drift` stays clinical, and ADR 0037's mechanical half is overridden by the clinician it names

The glossary gate refused the first draft: **`Drift` is already defined**, in `### Defects`, as *a
finding documented in the shorthand, carried into the Objective, and absent from both the Assessment
and the Plan* — the sense `clinical-note`'s drift rows are named for.

[ADR 0037](0037-a-contested-glossary-term-goes-to-the-higher-adr-number.md) resolves a contested term
in two halves: the higher ADR number keeps it, **and the losing concept is renamed by a clinician**.
Applied literally the first half hands the term to this record, 0089 being higher than 0037, and
renames the clinical concept. **The clinician ruled the opposite on 2026-08-31**: the tracker-side
concept is the loser and is renamed, and `Drift` stays clinical.

That is a departure from 0037's mechanical half rather than an application of it, recorded here
because a reader comparing the two will otherwise read this record as having broken the rule. The
half that held is the second one — the resolution is a clinician's, and the file position was never
what decided it. The tie-break by number is what a clinician overrides when the older concept is the
load-bearing one.

The term is **map disagreement**, borrowing #596's own verb — *"when this page and GitHub disagree,
GitHub wins and this page gets rebuilt."* `Map drift` was refused despite passing the gate: that
check compares heading to heading and its own docstring names the hole — *a term heading that
collides with a word already live in the file's prose is a heading-against-prose collision, and this
check does not see it* — so the compound buys precisely the ambiguity the gate would have refused if
it could read prose, and would have put a clinical word on a tracker tool's filename.

## Derived from precedent rather than ruled

**The report is bounded by construction and there is no `--show`.** A finding names the row kind, the
ticket number, the label names and the packet id, and never a body or a title. That is
`tracker_bodies.py`'s arrangement and its reason — the output is safe to paste — and it is load
bearing here because the step writes to a step summary on a **public** repository. It is not
`reference_scan.py`'s exception being extended; it is that this tool's findings can draw on nothing
else.

**The tests build synthetic harvests in a temporary directory.** The real tracker is fetched over the
network and changes every time anybody comments, so no count of issues, packets or findings is
asserted anywhere, on `test_tracker_scan.py`'s position.

## What must not come out of this

**A machine that writes packets.** The helper's refusal to infer an edge from prose or shared
filenames is what makes the map worth reading. A gate that placed work to go green would produce a
map that is current and wrong, which is strictly worse than one that is stale and says so. Nothing
here places work; the grader reports and the delta stays a person's.

**A second copy of the state.** The map is one issue body and the rendered views are derived. The
harvest is a disposable file under `scratch/`, `reconciled_through` is a fact about the map's own
reconciliation, and the declared limits live in the module with a pointer in the map.

**A count of packets, ADRs or tickets written into prose outside this record.** Every figure above is
dated to `7744c80` and re-derived by `git log`, the documented harvest and the helper's own `check`.
