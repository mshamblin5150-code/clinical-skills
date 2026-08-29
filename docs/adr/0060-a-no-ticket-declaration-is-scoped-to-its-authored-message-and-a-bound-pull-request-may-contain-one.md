# A no-ticket declaration is scoped to its authored message and a bound pull request may contain one

[ADR 0051](0051-a-binding-owns-its-line-and-an-empty-plan-is-a-finding-rather-than-a-valid-result.md)
decision 7 created the no-ticket declaration and ruled that it returns `0` and still prints its
reason. The build derived one more rule from it that the record does not contain: a declaration
anywhere in a pull request conflicts with a binding anywhere else in it, every artifact flattened
into one set. **That predicate is in no ruling.** It appears in ADR 0051 nowhere, in
`docs/agents/issue-tracker.md` nowhere, and in the CLAUDE.md paragraph naming the allowed forms
nowhere; and no test pinned it in either direction — both limbs were deleted during triage and
`test_tracker_merge_receipt` plus `test_tracker_workflow` ran 37 tests green.

Filed as [#629](https://github.com/mshamblin5150-code/clinical-skills/issues/629) while closing PR
#628, whose sync merge commit wrote the documented sentence for an intentionally unbound commit and
turned a required check red on an otherwise correct merge. Grilled 2026-08-29 against
`8dbf1a12ddcbfa701cbf515de3dabe0c0b38333b`. **Five decisions, ruled by the clinician on that date.**
Nothing is built here; this is the record the build reads.

**`main` advanced twice between the last ruling and this record being posted** — to `bf5b93c` and
then to `1face6f` — so the freshness gate refused twice and every figure below was re-derived twice
rather than carried across. **Figures moved on both occasions**, while nothing touching this
ticket's subject changed either time: the window is the last 40 merges, so it slides on every merge
in the repository regardless of what the merge was about. That is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) with a schedule, caught by
the second checkpoint rather than by a reader, and it is the reason that checkpoint exists.

**So the durable claim here is a ratio and not a count**, and it is the one that survived all three
measurements unchanged: **7 of the 8 sync merge commits in the window are bare and merged green, and
the 1 that declared honestly turned a required check red.** Every absolute below is dated to
`1face6f` and decays.

**This record narrows the predicate the build derived and reads ADR 0051 decision 7's scope as
message-scoped from this date.** That paragraph stays as written, being the dated record of what was
decided on 2026-08-27;
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
holds that a deciding paragraph is untouchable. Decision 7's own subject — that a legitimate absence
is a different row from an omission — is untouched, and decision 4 below is what keeps it true.

## Measured before ruling, re-derived at `1face6f`

Every figure was driven through the real `tracker_merge_receipt.REFERENCE` and `NO_BINDING` over
`gh pr list --state merged --limit 40 --json number,body,commits`, across PR #597 to PR #638, and
re-derives by re-running that command. **The window moves with every merge, so a figure here is
dated rather than durable** — which is the whole reason the count is stated with its base commit
beside it.

- **99 commits across the 40 merged pull requests; 77 carry neither a binding nor a declaration.**
  A silent commit inside a bound pull request is the ordinary shape and always has been.
- **8 sync merge commits, across 7 pull requests** — #604, #606, #611, #614, #620, #628, #638.
  **7 of the 8 are bare and merged green. One wrote the true sentence and went red.** The predicate
  passes silence and fails the honest form, which is the ticket in one measurement.
- **21 commits carry a parsable binding in `messageBody`; 0 carry one in `messageHeadline`.** A
  headline is a summary sentence and a binding has to own its line, so nobody titles a commit with a
  reference.
- **0 commits split a binding into one half of a message and a declaration into the other.** The
  shape decision 2 covers is unobserved, and is covered on ADR 0051 decision 5's own reading of a
  zero: a form nobody has written is not a form nobody will write, and here the cost of reaching it
  is a grouping key rather than a grammar widening.
- **Exactly one merged pull request carries a commit-level declaration: #628 itself.** Rarity is a
  fact about the frequency and not about the cost — the documented form was unusable inside a bound
  pull request, which is every pull request this repository has merged.

## The decisions

**1. The conflict is scoped to one artifact, not to the pull request.** A declaration is a finding
only against a binding in the same text. A pull request that binds a ticket may contain a commit
that binds nothing, and #628's author was right. `docs/agents/issue-tracker.md` is the copy that
survives; the CLAUDE.md paragraph's *when the pull request intentionally changes no ticket* is the
copy that moves. The limb is kept rather than deleted because one text saying both things is a real
self-contradiction and the only shape a conflict finding is worth anything on.

**2. The unit is the authored message and not the source string.** GitHub serializes one commit
message as `messageHeadline` and `messageBody`; they are halves of one text a person wrote, and
`git log` shows them as one. So a commit whose headline binds and whose body declares no ticket is
**one** artifact contradicting itself and fails. Scoping to the source string instead would make
that defect reachable by pressing Enter twice, which is the cheapest available way to buy out of a
rule and would be reachable in silence. The pull request body is one unit; each commit message is
one unit.

**3. A declaration on an unbound commit is permitted and never required.** Silence stays legal.
Requiring one would need a per-commit check that at this shape fires on 77 of 99 commits, or on 7 of
the 8 sync merges if scoped to those — refused on ADR 0051 decision 6's own argument that a step
going red on more than half of its subjects is one people stop reading, and it would grow this
ticket a check nobody filed for. Discouraging it is also refused: silence and the declaration
already produce the same green result, so guidance against it would spend prose asking authors to
prefer the version that says less. The declaration is decision 7's evidence affordance, and keeping
it available and never mandatory is what keeps it evidence rather than ceremony.

**4. A printed declaration says whether it stands alone or sits beside bindings.** Decision 7 put
that line on the page so the next rate measurement could report three buckets instead of two, and
that reasoning assumed a declaration only ever appears where the merge binds nothing — which
decisions 1 and 3 just stopped being true. After this record a declaration line no longer determines
a bucket, so it names which case it is. **This record creates that ambiguity and closing it is part
of the ruling**, because a line that reads as a settled claim about a bucket it no longer decides is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s shape with a schedule.

**5. The conflict finding names the authored message and cites each half by its own field and
line.** The unit is the message and the addresses stay per-field, so the finding names the message
and then points at the binding and the declaration in the coordinates `PlanLine` already carries.
The generic string is what produced this ticket: #628's author read that bindings conflicted with a
declaration and had to reconstruct which of four texts was meant. A synthetic line number spanning
the joined halves is refused — it would point at nothing a person can open.

## What this does not reach

- **The declaration is graded for shape and not for truth**, which is ADR 0051 decision 7's
  inherited limit and `specificity_scan.py`'s R2. One stock sentence satisfies it, at either scope.
- **A binding that parses and names the wrong ticket.** Unchanged: a clean run is not a correct
  binding.
- **The three-bucket rate is read off the status and the bindings, never off a declaration line
  alone.** Decision 4 makes the line say which; it does not make the line the measurement.
- **Publication ordering is untouched.** ADR 0051 decision 6's publish-before-status reorder stands
  exactly as ruled, and #628's receipt to #518 was posted correctly throughout.
- **The pre-merge limb still watches a door some merges skip**, and stays advisory on
  `continue-on-error`. Decision 1's second limb is what reports the local merge-and-push route.

## Consequences

`tools/tracker_merge_receipt.py` moves: `PlanAssessment.status` and `report_assessment` stop testing
`self.bindings and self.declarations` as flat sets and group by authored message, which means
bindings gain the source identity they are discarded with today while declarations keep theirs. The
two halves of a commit message join for grouping and keep their own field and line for reporting.

**The rule is unpinned in both directions today and must not stay that way.** Three cases have to
fail or pass on purpose: a single message that both binds and declares fails; a bound pull request
containing a commit that declares nothing passes; and a commit whose headline binds while its body
declares fails, which is decision 2 and the one case the corpus does not contain.

`docs/agents/issue-tracker.md` keeps its per-artifact sentence and gains the message-scope rule.
The CLAUDE.md paragraph naming the allowed forms drops its pull-request-scoped clause. `CONTEXT.md`
redefines **Declared no-binding** off the message rather than the merge and adds **Authored
message**, since decision 2 named a unit the glossary had no word for.
