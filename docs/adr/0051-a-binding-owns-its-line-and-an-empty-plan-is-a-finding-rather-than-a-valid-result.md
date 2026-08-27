# A binding owns its line and an empty plan is a finding rather than a valid result

[#530](https://github.com/mshamblin5150-code/clinical-skills/issues/530) was filed off three merges
that carried an explicit ticket binding and produced no receipt, with the workflow green on all
three. Nine tracker sweeps then added instance after instance, and the ticket's three decisions —
widen the grammar for a trailing period, widen it for a comma list, or report the silence — stayed
open because the grammar is a ruled thing.

Grilled 2026-08-27 against `cea7963`. **Seven decisions, ruled by the clinician on that date.**
Nothing is built here; this is the record the build reads.

## Measured before ruling, at `cea7963`

Every figure below was driven through the real `tracker_merge_receipt.REFERENCE` and
`_artifact_texts`, over `gh pr view --json body,commits` — the two surfaces the module reads. The
pull request title is fetched by the workflow and read by nothing.

- **The rate the thread recorded has moved.** Over the current 20 first-parent merges: **9** produced
  a parsable binding, **3** wrote a keyword that did not parse, **8** wrote no keyword at all. The
  #502 and #516 sweeps measured 5 parsable, 2 unparsed and 13 silent over earlier windows.
  Compliance has roughly doubled while omission remains the plurality shape.
- **No merged pull request in this repository binds nothing on purpose.** Across **35** harvested
  merged pull requests, **0** carry no ticket reference of any kind. Every one of the 26 unbound
  merges names between two and seven tickets somewhere in its body or commits.
- **So *contains a reference* is not a signal.** Those references are overwhelmingly *pattern
  citations* — #143, #137, #83, #320 — because this repo's prose names a defect shape by ticket
  number. A predicate keyed on them fires on 26 of 26 and cannot say which of PR #546's five tickets
  was meant. It is *the plan is empty* wearing a disguise.
- **The third alternative has never bound anything.** Of **46** merge receipts posted across
  **2,222** tracker comments: **31** whole-ticket, **15** partial, **0** of the third form. The
  possessive-lead phrase appears in four comments in the repository's history and every one is
  documentation of the form rather than a use of it.
- **The noun is the reason, not the punctuation.** The word `lead` followed by a number appears **0**
  times across 47 open ticket bodies and 35 pull request bodies. What this project writes is
  `decision N` (40 occurrences) and `option N` (9). Two authors reached for the form and were
  silently dropped: PR #508 wrote a possessive `decisions 1-3` and PR #559 wrote a possessive
  `option 1`.
- **A typographic apostrophe also fails**, in a repo whose own tooling carries a homoglyph map
  because this material arrives curly.
- **Sixteen unparsed keyword lines across the harvested set**, separating by what would recover them:
  trailing punctuation **5**, comma list **1**, line-opening with prose following **3**, mid-line
  **2**, wrong noun **2**.

## The decisions

**1. The check fires at two moments, not one.** A pre-merge limb on `checks.yml`'s existing
`pull_request` trigger, which already fetches the same JSON for the closing-keyword scan, and a
merge-time limb in `tracker_merge_receipt.py`. They are not redundant. Every recorded instance
arrived through a GitHub pull request merge, so the pre-merge limb reaches all of them and reaches
them while a finding is still one edit from fixed; but this repo's documented landing route includes
`git merge --no-ff` and a push, which opens no pull request, and the merge-time limb is what makes an
omission visible on that route. This is `checks.yml`'s own recorded asymmetry between `push` and
`pull_request` arriving on a second subject.

**2. The predicate is an empty plan, and nothing narrower.** Not *a near-miss was written*, which
reaches 3 of the 26; not *a reference appears*, which reaches 26 of 26 by firing on everything. The
honest name of the trigger is **the plan came out empty**, and a near-miss earns a second, sharper
line naming the declined text. Dressing the predicate in a reference limb would let the next reader
take a silent run for *no intent detected* when it only ever meant *nothing bound* — the standing
ruling to declare the coverage rather than widen the instrument.

**3. A binding owns its line.** `REFERENCE` widens to tolerate what a writer puts *around* a
reference that is still alone on its line — terminal punctuation, a comma-separated list of further
references, and the emphasis and list decoration this repo writes constantly, none of which binds
today. It does **not** widen to a reference that shares its line with prose, in either direction.

**4. Line-opening is refused, and PR #560 is the argument for refusing it.** That merge, which landed
during the grilling, opens a line with a partial binding to #521 and continues *"the build is still
to come, so this does not close it."* It is a binding whose point is the qualification following it.
A line-opening grammar would publish the bare partial claim and discard that qualification — an
immutable receipt asserting less carefully than its author wrote — and it would admit the ticket's
own named hazard, a partial binding followed by *once the sheet lands*, which opens its line and is a
plan. The mid-line direction has a measured over-bind besides: PR #558's body describes a *missing*
binding in prose, with the reference in backticks, and a mid-line grammar publishes a receipt on the
wrong ticket. `REFERENCE` has no mention-versus-use exemption, deliberately, any more than
`closing_keyword_scan.BINDING` does.

**5. The third alternative keeps its slot and loses its noun.** The noun widens to the vocabulary in
use — `decision`, `option`, `lead`, singular or plural — followed by a number, a range, or a list,
held as a declared module constant with the measurement beside it so a fourth noun fails visibly
rather than being dropped. Zero uses is not evidence of no demand here; it is evidence of a silent
drop, which is the whole subject of the ticket. The receipt must carry **the author's own noun**:
normalizing someone who wrote `option 1` into the `lead` spelling would publish an immutable receipt
naming a unit that does not exist on that ticket, and `parse_merge_receipt` round-trips the claim, so
the noun is captured and re-rendered rather than normalized.

**6. `1` means a finding, on both limbs, and the workflow publishes before it checks.** The module
gains the status every sibling scanner in `tools/` already has and it alone lacks: `0` clean, `1` the
plan is empty or a reference-shaped line was declined, `2` unchanged as *could not establish a
completed merge*. **The reorder is not optional.** `tracker.yml` today pipes the planner into a file
and then tests `$LASTEXITCODE` **before** posting anything, so a status change alone would make a
pull request that bound one ticket correctly and carried one declined line destroy the receipt that
works. Publication moves ahead of the status check. The pre-merge step takes `continue-on-error:
true`, as the closing-keyword step beside it already does: at today's rate the check fires on **11 of
20** merges, and a step that goes red on more than half of them is one people stop reading before it
can change anything.

**7. A pull request that legitimately binds no ticket declares it, with a reason.**
`Binds no ticket: <reason>`, alone on its line — parsed by the same own-the-line property as a
binding, so the hatch obeys the rule it exempts. It returns `0`, and the report **still prints the
declaration and its reason** rather than going silent. A bare marker with no reason does not count,
on `specificity_scan.py`'s rule that the reason is the evidence the check happened: nobody writes one
without having asked whether a ticket exists, and anybody can write a marker.

This is not a silencer. #530's own #500 sweep records the root defect as *"a merge with no binding is
indistinguishable from a merge that correctly belongs to no ticket, and the job cannot tell them
apart by construction."* A declaration is the only thing that makes them different rows, so the next
rate measurement reports three buckets instead of two and the omission figure stops carrying the
legitimate case inside it.

## What this does not reach

- **A binding that parses and names the wrong ticket.** A well-formed partial binding to #143 on a
  pull request about #530 owns its line and publishes a receipt nothing here grades. A clean run is
  not a correct binding.
- **The pre-merge limb watches a door some merges skip.** A local `git merge --no-ff` and push opens
  no pull request; decision 1's second limb reports that case after the fact and cannot prevent it.
- **The declaration in decision 7 is graded for shape and not for truth**, which is
  `specificity_scan.py`'s own R2 limit inherited whole. One stock sentence satisfies it.
- **The receipt still asserts only a bounded relation.** Nothing here makes any other claim on the
  ticket current, which is [ADR 0048](0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md)'s
  position and #290's.

## Consequences

`tools/tracker_merge_receipt.py`, `.github/workflows/tracker.yml` and `.github/workflows/checks.yml`
all move. `docs/agents/issue-tracker.md` and the CLAUDE.md paragraph naming the allowed forms both
state the noun vocabulary and the own-the-line rule, and a test binds them to the module's own
constants rather than to a typed copy.

**The test population is derived from `REFERENCE`'s own alternatives rather than typed beside them**,
which the #499 sweep argued on the ticket and which this record adopts. Every alternative is driven
at both punctuations and both positions, and the recorded instances are named in the test as the
cases they came from: `1956c7d`, `5b0a465` and `da4fee2` for the original three, and PR #508, #522,
#543, #559 and #560 for the sub-shapes the sweeps and this grilling added.

**A ticket about a reference parser cannot quote the reference forms it is about.** Every keyword
beside a live number in this record is described rather than written, for that reason:
`closing_keyword_scan.py` has no mention-versus-use exemption because GitHub has none either, which
is #153's *describing the rule broke the tool that checks the rule* arriving on the tracker.
