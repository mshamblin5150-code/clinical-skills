# A published figure names its population and is re-derived at publication

Out of [#961](https://github.com/mshamblin5150-code/clinical-skills/issues/961), grilled on
2026-09-12. Measured at `81ab421`, excluding this record from every population it counts. Nothing is
built here; this is the record the build reads.

[ADR 0149](0149-a-pointer-is-not-a-source-and-a-failed-read-is-not-a-negative.md) ruling 1 split
this subject out of [#818](https://github.com/mshamblin5150-code/clinical-skills/issues/818) and
left it open: *"publication-time binding across ADRs, ticket bodies and tracker comments is a
separate ticket."* This is that record.

The four failures behind it were published by an orchestrating session directly, into an ADR ruling,
a ticket body and a tracker comment. None was produced inside a skill run, so no brief in `skills/`
could have fired on any of them. Three trace to
[ADR 0135](0135-the-session-law-is-one-grammar-limb-the-loose-spelling-is-refused-and-the-legal-reader-states-its-composition.md)
and the fourth to the exhaustive sweep out of
[#771](https://github.com/mshamblin5150-code/clinical-skills/issues/771).

## What was measured before ruling, on 2026-09-12

**The base moved three times while this record was being written, and twice the figures moved with
it.** The gate read `STALE` after the last decision was taken; the branch was brought forward to
`45b0cee` and every count re-taken, and all of them re-derived identically. It read `STALE` a second
time before the merge, at `428d6f2`, and on that base the citation and measured-at counts had both
changed. It read `STALE` a third time, at `1468b4b`, which moved the denominator again. Every figure
below is the third re-derivation, at `81ab421`.

**Part of that second movement was this record entering the population it counts**, which is species
2 arriving inside the ruling on species 2. This ADR cites `extractor-coverage` four times and carries
a measured-at declaration, so an unguarded re-count would have read its own text back as evidence for
its own argument. **Every population below therefore excludes this record**, on `ADR 0135:68`'s
declared form — *"The honest population is every tracked `.md` except the records stating this
measurement."* The denominator is 195 rather than 196 for that reason.

Neither movement was caught by reading. Both were caught by the freshness gate refusing before
publication, which is ruling 6's whole argument arriving before ruling 6 was published.

**Three of the four species are ungoverned, and the fourth is governed by a rule whose trigger stops
one scope short.** Measured by testing each species against `CLAUDE.md`'s extractor-coverage section,
`docs/agents/issue-tracker.md`'s sweep narrowing, and `skills/_shared/reference/sourcing.md`:

| species | verdict | why |
| --- | --- | --- |
| truncated input | not covered | no rule addresses reading a quotation of a record as the record |
| self-inclusion | not covered | `ADR 0135:68`'s exclusion is a carve-out for one table, not a standing rule |
| mixed populations | not covered | caught by the base moving, by no rule |
| unstated instrument | trigger short | remedy at `CLAUDE.md:115`, whose trigger noun is *"Any maintainer tool"* |

**The ticket's own guess was backwards and is corrected here.** #961 reads *"species 2,
self-inclusion, looks closest"* to being already covered. It is the least covered of the four. The
one with an existing remedy is species 4.

**The two rules about figures sit at different scopes and were written days apart.** Both live under
the `### Extractor coverage` heading.
`CLAUDE.md:115` is scoped to a maintainer tool. `CLAUDE.md:119`, the discrimination rule, carries no
scope noun at all — *"Before a figure is allowed to settle a claim"* — and already reaches ADR prose
today. `docs/agents/issue-tracker.md:118` narrows to a sweep confirming or overturning an existing
written claim.

**`extractor-coverage` is a heavily cited name.** 32 of 195 ADRs cite it, 39 mentions; **2** of those
are anchor-bearing markdown links, in `docs/adr/0161` and `docs/agents/issue-tracker.md:117`. The
rest are prose, and most cite the population half. The matcher is the literal string over
`docs/adr/*.md` against a denominator of 195, this record excluded; it is a floor, because an ADR
writing *"CLAUDE.md's population rule"* does not match it.

**The measured-at convention already exists, unstandardized and enforced by nothing.** 15 of 195 ADRs
carry one, in at least four spellings — a capitalized *Measured at* with a short SHA and a full stop,
the same phrase uncapitalized and unpunctuated, and the sentence *Every measurement below was taken
in process at* followed by a short SHA. Same matcher shape, same floor.

**A publication-time claim gate already exists and refuses nothing.**
`tracker_publish_hook.py:264`'s `DISCRIMINATOR_CLAUSE` fires on a comment body carrying a line
starting `**Verdict:**`, requires the literal phrase *"under the claim's negation"*, and emits
`verdict:missing-discriminator` at posture `advise`. Its trigger is a marker the author writes, not a
semantic detector.

**An ADR-grading seam is built and wired to nothing.** `tracker_coordinates.py:218`'s `grade_adrs`
walks tracked ADRs forward from `ADR_CUTOFF = 2026-09-12 09:51:06 UTC`. CI calls only that module's
`--github-event` mode and `tools/hooks/pre-commit` never calls it at all.

**No surface has a claim-accuracy gate, and that is uniform rather than a tracker-versus-ADR split.**
Every publication-time gate in the tree grades PHI, body integrity, branch scope, structural
coverage, or citation-to-page. None grades whether a stated figure is true.

**The recorded incident base lands somewhere other than where the ticket is looking.** A read of
`CLAUDE.md`'s self-recorded incidents found on the order of 20 distinct published-wrong-figure
events; roughly 20 of 23 attributions landed in tracked prose, 3 in a tracker record, 0 in a ratified
ADR, and about 16 of 23 were caught by a discretionary pass rather than by a check. That is a
keyword-driven floor over one file and is not re-derived by anything committed, so it grounds no
ruling below; it is recorded because it bounds what the gate in ruling 6 can be claimed to cover.

**The glossary neighbors were read rather than assumed.** `CONTEXT.md:293`'s **Pointer** already owns
the noun *primary material*, in the sense of the source behind derived material. `CONTEXT.md:793`'s
**Load-bearing population** puts *"primary population"* on its own `_Avoid_` line. **Artifact** is a
taken family.

## Ruling 1. The requirement is two rules with different triggers

A single *state your population and matcher* clause is satisfied by three of the four failures while
they are still wrong. Under it, species 2's author writes `2 / 84, matcher <regex>, population =
tracked .md at 43e0a45` — every clause present, the figure wrong, because the record being written is
itself a tracked `.md` containing three of the forms it counts.

That is ADR 0149 ruling 3's argument unchanged: a widened single clause produces a **compliant and
still false** record, and *"absorbing failures one clause at a time is how a requirement ends up
describing the last failure rather than the class."*

So there are two rules. Rule 1 fires on every load-bearing figure and costs one clause. Rule 2 fires
rarely and is the only one of the two that reaches the three wrong-population species.

## Ruling 2. Rule 1 fires by function and on every surface, and it is a trigger widening

A figure that a ruling, verdict or routing decision **rests on** names its population and its matcher.
It inherits the escape already written under `### Discriminating measurements in sweep verdicts` at
`docs/agents/issue-tracker.md:118`: *a figure reported only for context does not trigger the clause.*

**Scoping it by surface was available and is refused.** ADR 0149 ruling 1 names three surfaces
because that is where the four instances landed, not because the class stops there. A surface-scoped
rule binds 3 of the 23 recorded incidents.

**Scoping it by the sweep trigger was available and is refused on a measurement.** That trigger fires
only on a figure confirming or overturning an **existing written claim**, and `ADR 0135:40`'s *"The
form recurs: 13 parenthetical slash-year spans across 4 corpus documents"* establishes a new claim.
The one species with an existing remedy is the one that trigger cannot reach.

**So this is not new text.** It is `CLAUDE.md:115`'s trigger noun widened from `Any maintainer tool`
to any published figure, which puts the population rule at the scope `CLAUDE.md:119` already
occupies.

**The cost is named rather than discovered.** *Rests on* is a judgment and *is in a tracker comment*
is not. The escape clause is inherited rather than invented, so the fuzziness is precedented; a rule
one can talk oneself out of is still a rule that gets talked out of.

## Ruling 3. Rule 2 is keyed on what the instrument read, not on a list of failure shapes

A figure rule 1 reaches is **re-derived at publication against the thing measured, not against the
draft's copy of it.** It fires where the thing measured can have moved since the reading, or can
contain the record being written.

The three species are one shape: **the population the author believed they measured is not the
population the instrument read**, and the gap is invisible from inside the draft. Truncation read a
quotation of the artifact; self-inclusion read a corpus that excluded the record being written;
mixed populations read two limbs' outputs as one snapshot.

**Enumerating the three was available and is refused**, on ADR 0149 ruling 3's ground: a rule built
from the failures to hand does not fire on the fourth.

**The form is already in the tree.** `ADR 0135:3` states it as that record's method: *"Every
measurement below was taken in process at `0d3d008` with the freshness gate `FRESH`, against the
artifact itself rather than against the citation string the ticket body quotes."*

**A first draft of this ruling asserted a trigger built from species 2 and 3 and claimed species 1**,
which reaches neither limb. It was caught by opening `ADR 0135` rather than by rereading the ticket's
table — this record's own subject, arriving inside its grilling.

## Ruling 4. The section moves whole and keeps its name

`### Extractor coverage` moves from `## Maintainer tooling` to `## Agent skills`, unrenamed.

**Splitting the section was ruled and then reversed on a measurement.** The first ruling moved the
general obligation out and left the tool-specific half behind. 32 ratified ADRs cite
`extractor-coverage` by name and most cite the half that would have moved, so they would name a rule
no longer in the section they name — [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s
shape arriving inside the change whose subject is #143's shape.

**Moving the whole section costs nothing in citations because a markdown anchor is derived from
heading text rather than position.** `#extractor-coverage` still resolves, both live links survive,
and all 32 prose citations stay true.

**Two costs are declared rather than left to be found.** The section name becomes narrower than its
contents, since rule 2 is a re-derivation at publication and not an extraction; renaming would repair
that and break 32 citations, so the name stays and the mismatch is stated in the section. And the
move relocates genuinely tool-facing text onto the agent-skills shelf, which is a smaller wrong than
a publication rule under a heading opening *"not required to use the clinical skills."*

**`AGENTS.md` is not the home.** That file is the consumer contract; this binds agents writing
records rather than agents running skills. `skills/_shared/reference/sourcing.md` is not the home
either, for the same reason inverted: ADR 0149 ruling 4 put its two rules there because a fan-out
brief runs inside a skill, and nothing here does.

## Ruling 5. Rule 1 is declared and rule 2 is graded

**Rule 1 is not gradeable.** *Did this sentence name its population* has no honest matcher, which is
ADR 0042 ruling 2's *"no honest general text pattern"* and ADR 0149 ruling 5's *"refusing to try is
the load-bearing half."* It takes a declared-limit row.

**Grading rule 1 on a self-declared marker was available and is refused.** It is what
`verdict:missing-discriminator` already does, and the escape is not writing the marker — so it grades
the authors who were going to comply and reads as coverage. That is a gate learned around.

**Rule 2 is graded, and not by a text matcher.** Its requirement reduces to a declared commit compared
against the current one, which is a SHA comparison. `tracker_freshness.py` already runs at that
checkpoint and already makes that comparison.

This is ADR 0149 ruling 5's own split arriving one surface over: the declaration rule declared, the
re-derivation rule graded.

## Ruling 6. The gate is two-tier and its ceiling is stated beside it

**Refuse** at `tracker_publish_hook` for tracker text, wired into both `analyze()` and
`authorize_issue_body()` on ADR 0177 ruling 3's terms. **Refuse** at `tools/hooks/pre-commit` for a
staged ADR carrying the declaration, on that hook's existing `|| status=1` posture. **Report** in CI.
That is ADR 0189 ruling 4's established two-tier arrangement.

**The gate does not discriminate against an author who did not re-derive.** One who measured at the
session's start, never re-ran the instrument, and writes today's SHA into `**Measured at:**` passes
cleanly; the gate prints
the same thing under the claim and its negation. That is `CLAUDE.md:119` turned on this gate, and it
is ADR 0149 ruling 6's defect named in advance rather than found later.

**What it does catch is the stale-but-honest case** — measured early, `main` moved, published with the
true older SHA. That is narrow, and it is two of the four measured failures, both of which #961
records as caught only because the freshness gate forced a re-derivation by accident. This makes the
accident into the requirement.

**Three further ceilings.** The declaration is **opt-in**, so a record that never claims a base is
graded by nothing; requiring it on every publication is the boilerplate #961's *what must not come
out of this* forbids. The pre-commit limb **fires on branch drift**, giving the same verdict
`tracker_freshness.py` already gives, and the first time it refuses a typo fix on an ADR someone will
want it gone. And **neither limb reaches a docstring or `CLAUDE.md` prose**, where most of the
recorded incidents landed; rules 1 and 2 bind that surface and no gate does.

## Ruling 7. The declaration is label-anchored and record-level

`**Measured at:** ` followed by a full commit SHA, on its own line, found by the label at line start
and **not** by position. Graded forward from a cutoff, on `tracker_coordinates.ADR_CUTOFF`'s
precedent, so the 15 existing prose declarations stay valid history and are not rewritten.

**A fixed position was available and is refused.** `tracker_filed_from` needs one because its rule is
about preservation — whether an edit dropped the line. This one needs only to be findable, and a
label at line start is sufficient. `docs/agents/issue-tracker.md:283` puts `**Filed from:**` first
after the Branch state blockquote, so the top of a tracker body is already a two-element stack with
no slack; buying position here would compound the one shape in this repository that has repeatedly
cost refused publications.

**Riding inside the Branch state block is refused.** That block's SHA is where the branch stands; this
one is what a figure was measured against. One field answering two questions is the defect ADR 0149
ruling 10 refused `SECOND-ROUTE` for by name.

**It binds the record, not the figure.** A record whose figures were measured at two bases cannot
express that and must re-derive to one before publishing. That is a forcing function, and it is what
`ADR 0135` did unprompted.

**The block is a claim about the base and never about the re-derivation**, restated here so a reader
of the block does not have to find ruling 6 to learn it.

## Ruling 8. The sweep narrowing is scoped to the discrimination rule alone

The narrowing under `### Discriminating measurements in sweep verdicts` —
`docs/agents/issue-tracker.md:116`'s *"In a tracker sweep it applies when a figure is used to confirm
or overturn an existing written claim"* — names the **discrimination** rule and nothing else. Rules 1
and 2 apply in a sweep unnarrowed.

Read otherwise after ruling 4, *"the general requirement"* names a section holding three rules, and a
sweep verdict whose figure establishes a new claim escapes rule 1 — which would give the tracker
sweep the weakest trigger in the tree, on the same gap that let species 4 through.

**This is a tightening and is ruled as one rather than passed off as a pronoun fix.** A sweep verdict
establishing a new load-bearing figure gains an obligation it does not have today. The vocabulary only
that section carries is untouched: *"`Re-derived` means a fresh instrument; `re-run` means the same
command again."*

## Ruling 9. `CONTEXT.md` gains `Measured population`

*The population an instrument actually read, as distinct from the one the record names.* With an
`_Avoid_` row naming primary population, scope, sample and corpus.

**A term is coined rather than avoided**, on ADR 0138 ruling 8 and ADR 0149 ruling 6's recorded
ground: *"there was no word for the state, so the agent writes the nearest one."* An author with no
name for the distinction reports the population they meant.

**Widening `Pointer`'s *primary material* was available and is refused.** Its sense is the source
behind derived material, and species 2's subject is a corpus from which nothing was derived.

**Nothing checks this sense.** `test_glossary_collisions.candidate_headings` fires only on a bare
single-word heading whose word also appears in a compound heading, so a compound entry can never be a
candidate. The verdict is the clinician's, taken on 2026-09-12, and a green suite is what both a right
answer and a wrong one produce — ADR 0149 ruling 6's finding, applying to this record.

## What this record does not settle

**Whether any check can catch a figure whose population was silently wrong.** Ruling 5 declares rule 1
unreachable and ruling 6 states the gate's ceiling; neither narrows it.

**Whether the prose surface should be gated at all.** Most recorded incidents land in docstrings and
`CLAUDE.md`, which ruling 6 leaves to the discretionary passes. Whether that is acceptable or its own
ticket is not decided here.

**The exact module the gate lives in.** `tracker_filed_from.py`'s arrangement — one module owning the
parser and the cutoff, read by the hook, an event mode and a harvest — is the obvious precedent and is
not ruled.

**The cutoff date.** Ruling 7 requires one and does not name it.

**The incident base rate behind ruling 6's third ceiling**, which is a keyword-driven floor over one
file that nothing committed re-derives.
