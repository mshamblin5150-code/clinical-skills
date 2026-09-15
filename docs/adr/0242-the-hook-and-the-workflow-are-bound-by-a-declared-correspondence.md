# The hook and the workflow are bound by a declared correspondence

[#1149](https://github.com/mshamblin5150-code/clinical-skills/issues/1149) was filed out of #1124's
grilling and is named in [ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)'s
*What none of this reaches*. The repository states in many places how the pre-publish hook's coverage
and `.github/workflows/tracker.yml`'s coverage relate, and no check re-derives any of it. The claims
were already wrong in both directions: understated about who the workflow reaches, and backwards for
anyone reading *hook ⊇ CI*. Between filing and grilling, seven sweep comments recorded one side's
coverage moving while the other stood still, from #1124, #928, #1014, #961, #1058, #1107 and #1111.

Grilled 2026-09-15. **Fourteen rulings, by the clinician, on that date.** Nothing is built here; this is
the record the build reads.

**Measured at:** 2d28b3f131c997f28ee6041e7e23966115882a48

## Measured before ruling

**Neither host's suite reads the other.** `tools/test_tracker_workflow.py` reads `tracker.yml` as text
with regular expressions and evaluates no step's `if:`; `tools/` holds no evaluator for GitHub's
expression syntax, and which grader runs on which event was decided only by those `if:` lines. The
hook side is Python a test can call.

**The hook already emits the row shape.** `tracker_publish_hook.analyze` returns
`Finding(rule, count, field, posture)` with a `deny` or `advise` posture, so rule, surface and posture
already leave the hook as data.

**The same predicate carries a different rule name on each host.** `tracker_filed_from.grade_publication`
emits `filed-from:create` and `filed-from:edit`; `tracker_filed_from.grade_event` emits
`filed-from:opened` and `filed-from:edited` for the same two losses. A join on the emitted string puts
one predicate in two rows and reads each as absent on the other host.

**Most of the rule population is already derivable.** `tracker_publish_hook.REDACTION_WALK_KINDS`
assembles the hook's rule names from `phi_scan.SHAPE_RULES`, `tracker_bodies.KINDS`,
`tracker_coordinates.UNANCHORED` and `tracker_branch_scope.BRANCH_RULES`, and the measurement rules are
module constants in `tracker_measurements`. The filed-from rules, the AAR quotation gate and the
unreadable and unclassified refusals have no exported vocabulary.

**Which text a host grades is not always the text that changed.** A label-only
`gh issue edit --add-label` carries no title or body, so the hook grades nothing, while the workflow's
`labeled` event runs the PHI and branch-scope steps over the unchanged body and can newly fire
`branch:in-flight`. A title-only edit runs branch scope over the unchanged body and skips the body,
coordinate, measurement and Filed-from steps. A label removal, a close with no comment, and an
approving review with no body reach neither host.

*Correction, 2026-09-15: [ADR 0245](0245-the-tracker-workflow-grades-the-title-that-changed-and-a-label-removal-starts-no-run.md)
rules that a title-only edit grades the changed title through body integrity,
coordinate accompaniment, and branch path triggers, without re-grading the
unchanged body. Measurement and Filed-from remain body-only.*

**Some postures depend on runtime state rather than on the publication.** In `analyze`,
`branch:unresolved-path` advises instead of denying when the `origin/main` fetch failed, while the
workflow's branch-scope run has no such branch. A failed readback leaves `branch:in-flight`
unevaluated and a Filed-from edit `NOT GRADED` at the hook, while the workflow reads labels and the
previous body from the event payload.

**Three sibling records landed while this one was grilled, and each moves rows.**
[ADR 0239](0239-a-tracker-record-cannot-declare-its-own-phi-exemption.md) removes the hook's reading of a
synthetic declaration from tracker text.
[ADR 0240](0240-the-map-s-direct-writer-grades-through-analyze-and-runs-no-readback.md) has the map's
direct writer grade through `analyze` with no readback.
[ADR 0241](0241-a-merge-receipt-is-graded-before-it-posts-and-a-workflow-token-write-is-an-unwatched-write.md)
grades merge receipts before they post, names the **unwatched write**, and rules in its ruling 3 the
same single event command this record needed.

## Ruling 1 — the relationship gets a declared correspondence object and a behavior test

Deleting the pairing sentences so each host states only its own coverage was declined: *refuse at the
hook, report at the workflow* is the arrangement every tracker grader since ADR 0099 has been ruled
into, so it is the design pattern and not incidental wording, and deleting the sentences loses what a
reader most needs while leaving the pattern unchecked. Declaring the gap and closing was declined as
the arrangement ADR 0188 ruling 4 records failing.

## Ruling 2 — the workflow's dispatch is Python, and it is ADR 0241's command

A test can drive the workflow side only where the decision about which checks apply is code. That
command is ADR 0241 ruling 3's, built on #1146; #1149 drives it and builds no second one. An
evaluator for the `if:` subset `tracker.yml` uses was declined as a second parser of a language this
repository does not own, the failure mode ADR 0188 refused for PowerShell. Declaring the conditions in
the object and matching them against the YAML text was declined because it binds strings rather than
behavior, which is #1149's own *what must not come out of this* and
[#218](https://github.com/mshamblin5150-code/clinical-skills/issues/218)'s recorded instance.

## Ruling 3 — the object is two linked tables

One table states which **publication hosts** each writer reaches. The other states, per host, the
posture on each row: `deny`, `advise`, `report` or `absent`. They fail independently — #1146 was wrong
about reach, and the table in #1149's body was wrong about posture — so one flat table keyed on
publication shape, surface and rule was declined for repeating most rows, and a posture table alone was
declined for leaving the most often wrong sentence, *covers both*, unchecked.

## Ruling 4 — `CONTEXT.md` gains Publisher and Publication host

A **publisher** is a harness, in ADR 0241 ruling 8's sense; a **publication host** is a place a grader
runs against a publication. The terms separate what ADR 0183 conflated when it called the hook one of
two publishers. A third term naming the object was declined: it names a mechanism rather than the
domain and invites the coverage reading #1149 forbids.

## Ruling 5 — the object describes the hosts and lives in its own module

Neither host imports it. The hook keeps deciding postures in `analyze`, the event command keeps its own
gating, and a test drives both and fails when a row stops being true. A table the event command reads
as configuration was declined: a wrong row would be obeyed rather than caught, and the hook half could
not work the same way because its postures depend on runtime state. Placing the object in the event
command's module was declined because it makes one host the owner of a relationship both change.

## Ruling 6 — a posture row is keyed on a predicate the object names, over a derived population

Each row names one predicate and lists the rule string each host emits for it. The population is every
rule either host can emit, derived from the graders' exported vocabularies, and a completeness walk
fails on an emitted rule no row names. A grader without an exported vocabulary gains one in the build,
starting with the filed-from literals, the AAR quotation gate and the unreadable and unclassified
refusals. Keying on the hook's rule string was declined because a rename on one host would silently
re-key rows the other host's reading depends on. Declared rows with no walk were declined as a partial
read presented as complete, which `CLAUDE.md`'s extractor-coverage rule forbids.

**The walk grades what the hosts do, never what they should do.** That boundary is a declared limit,
and the object is never presented as coverage.

## Ruling 7 — the trigger is part of the posture row's key

A row is keyed on the predicate, the surface graded and the trigger — create, body edit, title edit,
label added, label removed, comment, review, close — and a combination in which both hosts do nothing
is a row. The test builds each trigger once as a command for the hook and once as an event document
for the event command. A separate trigger-to-surface table was declined because each table can be
true while their product is false, and branch scope's posture on a label event is exactly such a
product.

## Ruling 8 — a named, closed set of runtime conditions qualifies a posture cell

The set is fetch failed, readback failed, and text carrying a **synthetic declaration**. A cell reads,
for example, `deny; advise when fetch-failed`. Every condition is forced against both hosts at each
host's I/O seam, and a host with no seam for that state must return the same posture under it, so a
host's indifference to a state is a checked claim. A condition as a fourth key component was declined
for multiplying rows that repeat their normal row; leaving conditions to a declared limit was declined
because half the rows in #1149's own backwards table are condition rows.

## Ruling 9 — every reach row carries an evidence disposition

A `behavior` row is driven through the real entry point: the hook's registration, and the direct
writer crossing its seam. A `declared-reading` row names the record that measured it and copies no
figure, for the GitHub-side facts no suite can drive, such as an unwatched write starting no workflow
run. The module holds its own disposition enum, declared at its code point, because it sits outside
the grader family. A maintainer command re-measuring the GitHub-side rows was declined here as
speculative.

## Ruling 10 — the first table records the tree as it stands when #1149 builds

No grading decision still open on its own ticket is made inside this build. A sibling ticket built
later changes a row and fails the test until the row is updated, which is the mechanism working.

## Ruling 11 — current prose points at the object, and rationale stands

Every current sentence pairing the two hosts' coverage points at the object and copies no row, held by
a naming bind in the manner `test_tracker_workflow.DeclaredLimitsAreBound` holds `NOT_REACHED`
pointers. A false coverage fact in a ratified record is corrected in place with a dated line beneath,
under [ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
and [ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md)'s
ruling 3. Sentences giving the reason a posture was ruled, such as why the hook refuses and the workflow
reports, are rationale and stay. Under ruling 4's harness sense ADR 0136's and ADR 0183's *one of two
publishers* stay true and are not corrected, as ADR 0241 already found. Nothing detects a new pairing
sentence, and that is a declared limit.

## Ruling 12 — Publisher takes the harness sense

The entry was first written counting a job authenticated with the workflow token as a publisher.
ADR 0241 ruling 8, ratified the same day, declined exactly that count because it invites a fix that
adds a harness to a list while the hourly job stays invisible. The entry follows ruling 8, and an
unwatched write gets reach rows under its own term rather than being counted as a publisher.

## Ruling 13 — the event command keeps a finding and a did-not-scan apart, and carries stderr

Each check's section reports its status with a finding and a did-not-scan distinguishable, and each
check's standard error reaches its section of the step summary. That is findings 3 and 4 of
[#1152](https://github.com/mshamblin5150-code/clinical-skills/issues/1152), and it lands on #1146's
build, because ADR 0241 left the report layout to the builder and a command built without it would be
rebuilt one ticket later. #1152 narrows to its findings 1 and 2. Leaving the distinction to #1152 was
declined because the command it concerns is being built now.

## Ruling 14 — #1149 builds after #1146, and after #1148 and #1145 where that saves a rebuild

#1146 is a hard prerequisite: without its command there is no workflow entry point to drive. #1148 and
#1145 each move rows, so building after them saves writing rows twice; that is a rebuild-saving edge
and not a block. #1151 and #1152 carry no edge, because their builds update rows under ruling 10.

## Consequences recorded as derived rather than ruled

- **The hook is driven at its command boundary.** A label-only edit returns from `handle` before
  `analyze` runs, so an `absent` row driven through `analyze` would be untested.
- **The hosts are four placements.** The hook's command route, the direct-writer seam, and ADR 0241's
  event command after publication in `changed-record` and before posting in the receipt job.
- **The new module is a tracker gate** and takes a `CLAUDE.md` section, which
  `test_tracker_workflow.EveryTrackerGateHasASection` already requires of a `tracker_*` module.
- **ADR 0188's residue bullet on this subject** gains a dated correction pointing here.

## What this does not reach

- **A new sentence pairing the hosts.** Nothing detects one; ruling 11's bind holds only the sentences
  that point at the object.
- **A runtime state a host reads other than through its seam.** Ruling 8's forcing cannot see it.
- **The GitHub side of reach.** Those rows are declared readings and are not driven.
- **Completeness of either host.** The object grades whether the correspondence claims are true, never
  whether either host grades everything it should.
- **ADR 0188 ruling 5's ad-hoc argv-list publications**, which cross neither host.
