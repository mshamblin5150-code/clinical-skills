# A claim record is spent by a citation and a number only has to be traced, and a contended shortfall names its deficiency rather than a victim

[#713](https://github.com/mshamblin5150-code/clinical-skills/issues/713) was filed because
`discussion_post_scan` blames a citation whenever a post runs short of claim records: the loser of a
contended allocation is decided by list position, and every number requirement is appended before
every citation requirement.

Grilled 2026-09-01 at `origin/main` `f05cedf`, freshness gate `FRESH` at both checkpoints. The gate
failed mid-session at `2dcbf69` and the branch was brought forward before anything was published;
every measurement below was re-derived at the later base and re-derives byte-identically.
**Eight decisions, ruled by the clinician on that date.** Nothing is built here; this is the record
the build reads. It does not supersede
[ADR 0085](0085-a-section-number-carries-its-subsection-suffix-and-the-section-grammar-is-one-shared-rule-while-the-citation-and-statute-readers-stay-two.md)
ruling 5, which said this defect gets its own ticket. This is that ticket's ruling.

## What the grilling found that the ticket did not

Five measurements, each of which moved a decision, and three of them falsify something the ticket
or the code's own row descriptions state.

**The bias is total, not merely predictable.** The ticket says the ordering "always falls the same
way." It is stronger than that: once a requirement is matched at its own step of the augmenting
walk it can be re-routed but never dropped, so the matched set is the lexicographically first
maximum matching. `((0,), (0,1), (1,))` returns `{0, 1}` -- requirement 2 loses even though
requirement 0 could have moved aside. There is no candidate structure in which a citation displaces
a number.

**An unmatched requirement is unmatched for two structurally different reasons and only one of them
is order dependent.** Given `((), (0,), (0,))` the matcher returns `{1}`. Requirement 0 has no
candidate record at all; requirement 2 has one and lost a race. Both emit the same sentence. For the
first, *"citation occurrence 1 has no source-matched claim record"* is true and stays true under
every ordering. For the second it is **false**: the record exists, matches on source and year, and
was taken by something else. So one class of these findings does not merely name the wrong row, it
asserts something untrue about the artifact.

**The two Quill records in `tools/test_discussion_post_scan.py` are not there for the reason the
ticket gives.** The ticket says that shape exists because of the distinctness rule. It exists
because the pools are shared. The fixture body states a figure and cites its source in one sentence,
so the number takes the record that carries the figure and the citation needs a second one whose
`RESTATEMENT` paraphrases the first. Deleting that second record makes the shared pool report the
correctly sourced citation as untraced, and makes a split pool report nothing. Citation to citation
distinctness survives a split intact, measured directly: Quill cited twice against one Quill record
still fails under split pools.

**The victim is arbitrary, not just biased.** Three citations of one source against one record, with
every ordering of the requirement list enumerated, reaches every pair of losers. The deficiency is
the same under all six orderings.

**The discussion pair already disagrees with itself, under one name.** `discussion_reply_scan`'s
`untraced-number` dedupes occurrences and tests set membership; `discussion_post_scan`'s row of the
same name builds one requirement per occurrence and matches them into distinct records. On identical
prose and an identical ledger -- a figure restated once, one record carrying it -- the post scanner
reports a finding and the reply scanner's rule reports nothing. Their own row descriptions already
say different things: *"has its own claim record"* against *"traces to claims.md"*. The reply
scanner implements the post scanner's sentence; the post scanner does not.

## Ruling 1 -- existence and distinctness are two rows, because only one of them is a fact

The citation row's stated sentence carries two rules and the split follows the two failure shapes
above. `untraced-citation` narrows to existence: a citation whose source has no claim record at all.
A new `respent-record` carries distinctness. The zero-candidate case is honest, per row, order
independent, and keeps the detail that makes it actionable; it was collateral damage of an
allocation policy it was never subject to.

**Declined: one row with two wordings, and one row reporting only a global shortfall.** The first
makes a single kind mean two defects with different repairs and different truth conditions, which is
what forced this measurement in the first place. The second discards per row detail in the
zero-candidate case, which never needed to lose it.

## Ruling 2 -- a number does not contend with its own citation

Numbers leave the shared pool. A claim record spent by a number is still available to a citation, so
a sentence stating a figure and citing its source needs one record rather than two.
`CONTEXT.md`'s claim ledger is defined as *one entry per claim*, and the shared pool made that
definition false of this grader. The fixture's second Quill record is deleted as ceremonial; its
restatement adds nothing a refutation pass could act on.

The distinctness rule ADR 0085 protects is stated about citations and is untouched. The build adds
direct coverage for it -- two citations of one source against one record -- because deleting the
fixture record removes the only live instance.

## Ruling 3 -- a contended shortfall names its deficiency and no victim

The finding is the maximal deficiency witness: the requirements reachable from an unmatched
requirement by alternating paths, together with the records those reach. The union of two Hall
violators is a violator, so that set is unique and order independent. It reads
*"3 citations of Quill (2024) share 2 claim records -- 1 short."*

**Declined: grouping on the source key instead.** It is exact under every candidate structure that
could be constructed from real post prose -- a multi-author `(Quill & Vale, 2024)` folds to one
combined key and a multi-work `(Quill, 2024; Vale, 2024)` splits into separate occurrences -- but
`matching_record_indices` ORs over a citation's key set and `citation_occurrence_keys` can emit a
multi-key occurrence through the abbreviation-alias path, which would give two citations overlapping
but unequal candidate sets. The grouping would then describe a contention that did not happen. That
is a declared limit for which no worked instance could be produced, which is the kind
`CLAUDE.md`'s extractor rule says goes stale unwatched. The exact walk needs no such row.

**Declined: naming a victim and calling it contended.** It prints a number whose only property is
that it is reproducible, which is the trap this ticket was filed over. Predictable is not honest.

## Ruling 4 -- a number is traced, not owned

`untraced-number` becomes membership of a distinct value in the union of every record's traced
numbers. Restating a figure costs nothing. `ClaimRecord.numbers` is already built from heading and
`RESTATEMENT`, the identical population to the reply scanner's set, so the parity closes with no
new predicate and without editing the sibling. The row's documented sentence is unchanged; the code
stops exceeding it. Its detail adopts the sibling's wording, *"12% is absent from claims.md"*.

**The cost is named rather than left to be found.** Two occurrences of one value that are genuinely
different facts -- twelve percent of patients, and a twelve percent cost rise -- are covered by one
record. It is a real false negative, it already exists unfiled in the reply scanner, and it goes in
`DECLARED_LIMITS` with a behavior disposition and a positive control.

The trade is a false positive on ordinary prose against a false negative on coincident values, and
this repository rules that direction consistently: the spelling table refusing `seizure`,
`no-stop-criterion` firing on correct orders,
[#215](https://github.com/mshamblin5150-code/clinical-skills/issues/215) three times over. A writer
who restates their own figure is writing well, and a rule that charges them a ledger entry for it
teaches them to write around the grader.

**Declined: per-occurrence distinctness for numbers with the reply scanner changed to match.** It
keeps the coincident-value case and charges every restated figure a duplicate ledger entry, which is
the charge ruling 2 refuses one row over. **Declined: keeping the divergence and declaring it.** One
kind string meaning two rules in a pair with shared conformance machinery is
[#185](https://github.com/mshamblin5150-code/clinical-skills/issues/185)'s defect, and it is what
made the measurement necessary.

## Ruling 5 -- `untraced-citation` keeps its name and the cost is taken

`respent-record` echoes the sibling's `respent-source` -- the same verb for the same act at a
different scope -- and *carries its own claim record* matches `borrowed-locator`'s phrasing. ADR
0085's protected sentence lands verbatim on `respent-record`, so it is provably not removed.

The cost: `untraced-citation` keeps its name while its meaning narrows, so a report line from before
this change could have been either rule with nothing saying the name moved. Taken, because the
ambiguity window is a console report rather than a durable artifact -- the name appears in three
tracked files, none of them a record of a run.

**Declined: renaming the existence row to `unsourced-citation`.** It buys clarity about old reports
at the price of colliding with `research_ledger`'s `STATUS: unsourced`, which means a claim with no
source at all. That is the more expensive confusion and the one #185 was about.

## Ruling 6 -- a finding names the graded artifact unless only the ledger can repair it

`respent-record` and `untraced-citation` name the draft, because the draft is being graded and is a
live candidate for the repair: a writer may add a record, or may have over-leaned on one source, or
may drop a citation.

`legal-reference-name` moves to `"claims.md"`. A `REFERENCE:` line carrying a section with no
regulation name is entirely inside the ledger and nothing in the draft can repair it, while the row
today reports `source.draft.name` beside a detail saying the defect is in a claim record. **It is
folded in rather than filed**, on ADR 0085 ruling 4's own test: the predicate is already written and
already correct and is being handed the wrong argument, so filing it separately produces a ticket
carrying a one-token diff. It gets its own named test and its own line in the build spec, because a
behavior that arrives for free is a behavior nothing pins.

## Ruling 7 -- the report states the claim-record count

Both citation rows and `untraced-number` are graded against the record set, and the counts block
never printed it. A run one record short and a run with records to spare printed the same clean row.
`claim records` joins the counts block and the `reference_boundary_graded` field tuple in
`GATED_ROW_SETS`, so a refused reference label prints `not graded` rather than `0` and the ADR 0080
conformance walk grades the new field without being asked.

This is [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s ruling: a count
visible only when something is wrong trains a reader to read its absence as the stronger claim. It
also makes ruling 2's fixture edit legible in a diff, as `claim records` falling by one, rather than
as a silent deletion from a file that still passes.

## Ruling 8 -- `numeric claims` counts distinct values

The field sits beside a denominator now, and a numerator that is not the thing being divided is
worse than no numerator. `numeric claims` and `claim records` read as a ratio a reader can check.

**Declined: leaving it counting occurrences for alignment with the reply scanner.** That is
alignment on a field name whose neighbors differ anyway -- the sibling prints no `claim records`
line, so its `numeric claims` is not half of a ratio and does not have to answer the same question.

## What must not come out of this

**The distinctness rule stays.** Rulings 1 and 5 relocate it to `respent-record` and rulings 2 and 4
narrow it to citations; neither removes it, and the build adds the direct coverage the fixture edit
takes away.

**No reordering that lets citations win.** Ruling 3 removes the victim rather than moving it.

**No new grouping heuristic in place of the exact walk.** The declined option in ruling 3 is the one
a later pass will re-propose because it is simpler; it buys a declared limit nobody can write a test
for.

## What this hands to ADR 0092's object

[ADR 0092](0092-a-glossary-sense-collision-is-recorded-on-the-entry-standing-alone-and-the-candidate-population-is-a-declared-object.md)
merged while this session was open and rules the shape of the two glossary entries added here. Both
are named now rather than left for that build to meet unruled, since its ruling 4 fails the suite on
a fire with no row.

**`Claim record` against `Claim ledger` is a narrowing, not a collision.** They share a first word,
so 0092's predicate derives the pair as a candidate; the senses are compositional -- a record is one
entry in the ledger -- so the ruled word is **narrowing**, which ruling 5 says is the majority case
and is not a defect.

**`Spend` is outside that predicate's reach and its clause is placed by 0092's rule anyway.** The
second sense sits in the body of `Invoked source`, where a domain's behavior is spent as the
argument and nothing is used up. That is a term against a usage rather than two entries sharing a
first word, so candidacy derived by name cannot see it. Ruling 2's fallback governs the placement --
neither term stands alone, so the clause goes on the newer -- and the newer is `Spend`, where it
sits. **This is a declared gap in that predicate and not a claim that the pair is safe:** a sense
divergence between an entry and another entry's prose is invisible to a name-keyed derivation, and
0092's ruling 5 already states its tally is a floor.

## Consequences

The build is [#713](https://github.com/mshamblin5150-code/clinical-skills/issues/713). The affected
surfaces are `tools/discussion_post_scan.py`, `tools/test_discussion_post_scan.py`, the distinctness
sentence at `skills/discussion-post/SKILL.md:259`, and that skill's row table.
`tools/discussion_reply_scan.py` is not edited: ruling 4 closes the divergence from this side.
