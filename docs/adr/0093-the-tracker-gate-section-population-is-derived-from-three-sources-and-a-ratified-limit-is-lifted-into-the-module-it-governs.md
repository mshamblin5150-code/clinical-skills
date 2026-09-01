# The tracker gate section population is derived from three sources and a ratified limit is lifted into the module it governs

[#707](https://github.com/mshamblin5150-code/clinical-skills/issues/707) was filed because
`CLAUDE.md` gives no `###` section to three tracker gates, and because the person building the
neighbouring tracker tools described one of them wrongly, twice, in one thread — naming one of its
four triggers each time.

Grilled 2026-09-01 at `origin/main` `ca318be`, freshness gate `FRESH` at both checkpoints.
**Six decisions, ruled by the clinician on that date.** Nothing is built here; this is the record
the build reads.

## What the grilling found that the ticket did not

Four measurements, each of which moved a decision, and three of them falsify something the ticket
or its triage comment states.

**The body's premise does not re-derive.** It opens *"`CLAUDE.md` gives a `###` section to almost
every module in `tools/`."* Counting occurrences of every non-test module name against that file at
this base, nine modules carrying their own command line have no section, and two of them are named
zero times. The premise is a generalization made from the files the pass had open — [#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137)'s
subject, arriving in the premise of a ticket about a documentation gap. That population is
[#743](https://github.com/mshamblin5150-code/clinical-skills/issues/743)'s and is deliberately not
this record's; the counts are stated there once, dated, with the command that re-derives them.

**The closed set of three has gone stale twice on the ticket's own thread.** `map_scan` landed with
a section; `tracker_publish_hook` landed without one. Neither was predicted by a body that names
three modules by hand. A hand-kept list in a ticket is a set nothing re-derives, which is the
failure this ticket is filed about arriving one level up.

**Two of the three unsectioned gates already have their limit rows ruled, so the triage comment's
pricing is wrong.** That comment says authoring a limits object for them would be *"new authored
content about what those gates cannot reach, which is a grilling-sized job of its own."* It is a
lift, not an authorship: `tracker_merge_receipt`'s rows are ratified in
[ADR 0051](0051-a-binding-owns-its-line-and-an-empty-plan-is-a-finding-rather-than-a-valid-result.md)
and [ADR 0060](0060-a-no-ticket-declaration-is-scoped-to-its-authored-message-and-a-bound-pull-request-may-contain-one.md),
and `tracker_publish_hook`'s in
[ADR 0083](0083-the-pre-publish-hook-grades-the-record-rather-than-the-body-and-the-branch-scope-rule-refuses-per-trigger.md).
Only `tracker_freshness` needs a judgment nobody has made, and that judgment is
[#728](https://github.com/mshamblin5150-code/clinical-skills/issues/728)'s open grilling.

**And the merge-receipt rows are a live [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220).**
Three of ADR 0051's four rows are restated in ADR 0060 in different words. Two ratified prose copies
of one limit set, already differing in wording, with nothing between them that fails. That is the
defect `docx_write.NOT_APPLIED` and `reference_scan.NOT_REACHED` exist to end, standing in two
ratified records.

**The triage comment's second gap is false of the repository.** It records that `tracker_freshness`
documents no exit statuses, so the new section would be the *first* written record of that contract.
`docs/agents/issue-tracker.md` already states it completely — the fetch limb and the containment
limb, both as exit 2. `CLAUDE.md` states it too, and only the containment limb. The section would be
a **third** copy of a contract already written twice with different completeness, which is #220
before the fix rather than after it.

## Ruled 2026-09-01

### 1. The obligation attaches to tracker gates as a class, not to three named modules

#707's *Done when* reads *"`CLAUDE.md` carries a section for each of the three modules."* That
sentence has been satisfiable-while-wrong twice inside a week. The obligation attaches to the
class, and the class is derived rather than listed.

The wider population — every command-bearing module in `tools/` without a section — was refused
here and split to #743. #707's evidence is a measured cost inside one thread about the tracker
family; extending it to `threshold_coverage` or `voice_model_scan` would widen the rule past its
own evidence.

### 2. The derivation is the union of three declared sources, each reported, and the floor is declared

Three sources exist in the tree and **two of them are individually wrong**:

| source | misses |
| --- | --- |
| module name prefixed `tracker_` | `closing_keyword_scan`, `map_scan` — tracker gates by function |
| named as a command in `docs/agents/issue-tracker.md` | `tracker_publish_hook`, which that file never names |
| invoked by `tracker.yml` or the pre-publish hook in `.claude/settings.json` | `tracker_freshness` and `tracker_bodies`, which no workflow invokes |

Measured at this base, the union derives seven members and the prefix source alone derives exactly
the sectionless four. **The union is taken anyway**, because a single-source derivation produced two
of the three wrong answers above, and because the extractor-coverage rule requires the population,
the extraction and the liveness case to be three independent pieces of evidence rather than one
matcher grading itself.

The walk **reports what each source contributed**, and its docstring **declares the floor**: a
tracker gate reachable by none of the three sources is outside it. That is stated first rather than
after the fact, because `test_ls_files_coverage.py`'s *"a sixth walk cannot arrive quietly"* and
`EveryFilterHasAVocabularyGuard`'s *"a third filter cannot arrive unguarded"* both had to be walked
back to a floor once written as guarantees.

### 3. A ratified limit is lifted into a `NOT_REACHED` in the module it governs

`tracker_merge_receipt` and `tracker_publish_hook` each gain a `NOT_REACHED`, and the section points
at the object. ADR 0051's and ADR 0060's rows are **merged into one set** — that merge is a reading
of two ratified lists, not a new ruling — and ADR 0083's are lifted as they stand. The ADR sections
remain the ratified reasoning; the object becomes the one live population.

This is [ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 3's position that a declared limit is a keyed sentence whose reasoning stays at the code
point, and [ADR 0074](0074-a-module-s-limit-population-is-one-object-and-the-shapes-it-replaces-survive-as-views-and-pointers.md)
ruling 1's that a module's limit population is one object. Leaving `tracker_merge_receipt` as prose
in two ratified records would leave the standing counter-example to a rule this repository has had
to state three times.

**What the lift does not buy is stated rather than sold.** The bind test asserts the pointer is
present and no row is copied. It cannot tell that a row has stopped being true: widen the module so
a listed limit no longer holds and the test stays green. What the lift buys is one place to edit
instead of two-plus-a-section, and a reader holding the module who can find the boundary without
knowing which of five ADRs ruled it.

### 4. `tracker_freshness` ships a section with no limits object, and the walk grades the two cases apart

Its section carries what it reads, what its exit statuses distinguish, and what a clean run does not
establish, points at `docs/agents/issue-tracker.md` for the exit contract, and **names #728 as the
open owner of its coverage boundary**. No `NOT_REACHED` is authored here.

Authoring one would pre-empt an open grilling whose own first decision is *whether this is worth a
mechanism at all or is declared* — so the rows could be void within a ticket, and changing a ruling
needs the clinician while recording a finding does not. Blocking #707 on #728 would trade a measured
cost for an unmeasured one. Handing the fourth section to #728 would ship a deliberately red walk,
since ruling 2's walk goes red exactly when a derived gate has no section.

**So the walk distinguishes *has no section* from *has a section and no limits object*, and only the
first fails.** The alternative asserts that every tracker gate must carry a limits object, which is
a rule nobody has ruled and which `tracker_freshness` would be the first case of.

### 5. The new sections take the mechanism prose, and one paragraph is exempt

`### Tracker scan` currently carries the pre-publish hook's mechanism welded into a paragraph whose
subject is its own shape-layer run and #260's declined pre-push hook. The mechanism moves to
`### Tracker publish hook`; `### Tracker scan` keeps #260's ruling, which is its own history, and
ends with one sentence handing off. `CLAUDE.md`'s partial statement of the freshness exit contract
becomes a pointer to the new section.

**The console-codec chronology is untouched in every case.** It makes a different claim — which tool
called `use_utf8` when — and this repository documents why that paragraph's pairing must stay
together: it is where the byte-identical merge was caught.

Coexisting was refused as #220 adopted on purpose. Complementing — sections carrying only the exit
contract and the pointer, with the mechanism left where it is — was refused because a section that
does not say what the module does is one a reader can open and learn nothing from, which is #670's
recorded failure with the file already open.

### 6. #707 takes a `blocked_by` edge on #740 and not the `blocked` label

Two-thirds of the build — both lifts, both bind tests, and ruling 2's walk — touches no file in the
in-flight package of
[#739](https://github.com/mshamblin5150-code/clinical-skills/issues/739),
[#740](https://github.com/mshamblin5150-code/clinical-skills/issues/740) and
[#741](https://github.com/mshamblin5150-code/clinical-skills/issues/741), and is startable today.
`docs/agents/triage-labels.md` states that an open edge does not by itself require the label when a
ticket has an independently startable piece.

**The reason to sequence #740 first is correctness rather than conflict.** #707's *Done when* tells
the builder to write sections *on the shape its siblings use*, and the newest sibling is the one
#740 is filed against: its final paragraph belongs to a different module and it names no test of its
own. Building against that copies a known-bad exemplar. The textual adjacency is real too and is the
weaker argument — whichever lands second re-reads the merged region rather than trusting the merge,
on this repository's own record that the merge is the unguarded moment.

## Rejected options

- **A prose section enumerating a gate's triggers or limit rows.** #707's own prohibition, and
  #220 with no test between the copies. The section says what the module is, what its statuses
  distinguish, and points.
- **A single-source derivation.** Two of the three available sources are individually wrong at this
  base, and the one that is right today is a name prefix — a matcher, which the extractor-coverage
  rule does not let stand as a population.
- **Extending the obligation to every module in `tools/`.** Split to #743 rather than folded in,
  because #707's evidence does not reach it.
- **Authoring `tracker_freshness.NOT_REACHED` here.** Pre-empts #728.

## Consequences

A tracker gate landing without a section fails a walk on the day it lands rather than four days
later in a sweep comment, which is what happened to `tracker_publish_hook`. `tracker_merge_receipt`
and `tracker_publish_hook` gain one editable limit population each, and ADR 0051's and ADR 0060's
duplicated rows stop being the live copy. `CLAUDE.md` stops carrying a second description of the
pre-publish hook inside a section about a different module.

The price is that the derivation is a floor: a tracker gate named without the prefix, absent from
`docs/agents/issue-tracker.md`, and invoked by no workflow is invisible to it, and that is written
in the walk's own docstring rather than discovered.

## What none of it reaches

Whether a section is **correct**. Every mechanism here grades presence, pointer and non-duplication;
a section that names the right object and describes the module wrongly passes all of it. #670's
recorded defect was a wrong description, not a missing one, and nothing ruled here would have caught
it — what this changes is that the section exists to be wrong in, where today there is nothing.

Whether a lifted row is **still true**, per ruling 3.

And `tracker_freshness`'s coverage boundary, which is #728's and is deliberately left open.
