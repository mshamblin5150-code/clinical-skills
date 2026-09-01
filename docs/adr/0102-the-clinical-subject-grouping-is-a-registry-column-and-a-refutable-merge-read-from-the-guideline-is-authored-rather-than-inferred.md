# The clinical-subject grouping is a registry column and a refutable merge read from the guideline is authored rather than inferred

[#689](https://github.com/mshamblin5150-code/clinical-skills/issues/689) is the artifact
[ADR 0064](0064-a-threshold-sheet-s-sources-are-not-joined-to-its-topic-because-the-catalog-cell-is-the-guideline-s-wording.md)'s
Consequences named and nothing owned: *nothing in this repo derives which catalog cells are one
clinical topic*. It was grilled on 2026-08-31 and **parked** rather than ruled, on the ground that
[#429](https://github.com/mshamblin5150-code/clinical-skills/issues/429)'s corpus sweep was this
ticket's measuring instrument and the shape should not be ruled against an imagined population.

Grilled again 2026-09-01. **#429 is closed and the sweep has run**, so the population exists.
Eleven rulings, made by the clinician on that date. Nothing is built here; this is the record the
build reads.

## Measured before ruling, at `origin/main` `c32b419`, corpus-free

Freshness gate `FRESH` at both checkpoints. The gate went `STALE` mid-session when `main` advanced
thirteen files; the branch was brought forward and **every figure below was re-derived at the new
base** rather than carried across, on
[#320](https://github.com/mshamblin5150-code/clinical-skills/issues/320)'s ruling.

- `reference/guidelines-catalog.md`: **180 rows, 169 distinct topic cells, `{1: 159, 2: 9, 3: 1}`**.
  The ticket's dated footer re-derives exactly.
- `reference/thresholds/`: **169 sheet files, 169 registry rows**, every row naming a file that
  exists and every file named by a row. States `{sheet: 166, none: 2, non-source: 1}`.
- `tools/threshold_draft.py`: `TOPIC_ALIASES` still holds **one** entry.
- **C(169,2) = 14,196** unordered cell pairs.

**The park's stated instrument did not survive, and that is the first finding.** The ground for
parking was that every draft prints a `## Rejected candidates` list, so a completed sweep *"hands
over a recorded list of the subjects where a sibling document sat under another name"*. **Zero of
the 169 committed sheets carry that section.** Those lists were transient stdout; the sweep consumed
them and they are gone. A park whose release condition is another ticket's *console output* is a
park on evidence nothing preserves.

**What arrived instead is stronger and is not a report — it is the sheet directory.** The synonym
splits the ticket could only name three of are committed files now, and the catalog's `population`
column separates every one:

| catalog cell | society | year | population |
| --- | --- | --- | --- |
| `high blood pressure` | AHA ACC | 2025 | adult |
| `hypertension screening` | USPSTF | 2021 | adult |
| `high blood pressure screening` | USPSTF | 2020 | pediatric, adolescent |
| `anxiety disorder screening` | USPSTF | 2023 | adult, pregnancy, postpartum |
| `anxiety screening` | USPSTF | 2022 | pediatric, adolescent |
| `iron deficiency anemia screening` | USPSTF | 2015 | pediatric |
| `iron deficiency anemia screening and supplementation` | USPSTF | 2024 | pregnancy |
| `Clostridium difficile infection` | IDSA | 2018 | pediatric, adult |
| `Clostridioides difficile infection` | IDSA | 2021 | adult |
| `COPD screening` | USPSTF | 2022 | adult |
| `chronic obstructive pulmonary disease` | GOLD | 2026 | ? |

**And the hazard is live rather than hypothetical.** No sheet links to any other — zero
cross-references across all 169. A reader on a hypertensive adult, handed `coverage.md` and told to
find every sheet whose topic the patient's problems touch, searches `blood pressure`, gets three
rows, and **misses `hypertension screening` entirely** — the adult USPSTF statement. One of the
three they do get is the *pediatric* one.

**Both parties ADR 0064 named have closed and shipped without this artifact.** #648 closed; **#584
closed**, so the per-patient reader row is live today. No ticket, open or closed, owns the
*"mechanical cross-sheet gate"* that
[ADR 0076](0076-the-cross-sheet-reading-is-a-substantiated-row-and-the-reader-derives-the-join-per-patient.md)
names as the one sanctioned consumer.

## What is ruled

1. **The consumer is ADR 0076's shipped reader, not a future gate.**
   The demand the ticket was filed for is spent — every sheet is drafted, so nothing pulls at draft
   time. What the sweep created is a standing reader hazard sitting in committed files, measured
   above. ADR 0076 ruling 2's prohibition is **not** reopened: it forbids a grouping that
   *replaces* the reader's per-patient applicability judgment, and a subject index decides no such
   thing — it stops the reader never opening a sheet, and setting the pediatric sheet aside stays
   entirely theirs. Closing the ticket unbuilt was weighed and refused: the hazard it accepts is a
   reader concluding they have covered blood pressure after reading one of three sheets, one of
   which is about children.

2. **It is a fourth column on `reference/thresholds/coverage.md`, schema `threshold-coverage/3`,
   multi-valued.**
   The registry is keyed 1:1 on the unit the grouping is over — `catalog_topics()` derives its 169
   keys from the catalog and `audit()` refuses `missing topic`, `duplicate topic` and
   `unknown topic`. The catalog is keyed on **documents**, so a column there would state 11 subjects
   twice with nothing forcing the copies to agree. A standalone file was refused as a fourth
   hand-kept list bound to the catalog by nothing. **This does not reopen
   [#689](https://github.com/mshamblin5150-code/clinical-skills/issues/689)'s decision 1**: that
   ruling killed the *unnamed equivalence*, and a comma-separated column **names** subjects, the
   group being recovered by grouping on the name. `record` is already an authored cell checked only
   for non-emptiness, so a subject column is not the registry's first.

3. **An agent may not assert a singleton; it may propose a merge.**
   ADR 0064's prohibition is on a grouping **inferred from the catalog's wording** — the measurement
   behind it is word overlap over topic strings. An agent that reads the guideline and judges what
   it is about is not doing that, and those documents have already been read end to end by agents,
   which is what produced all 169 sheets. So the constraint that survives is about the **claim**,
   not the hand: `subject = own name` asserts *this cell is a member of nothing* with nothing
   compared, unfalsifiable by construction; a merge is two-sided, carries named evidence on both
   sides, and anyone can open both sheets and refute it. **The clinician is not the bottleneck and
   was never the constraint.**

4. **Every proposed merge goes to a second agent briefed to refute.**
   `research_ledger.py`'s arrangement adopted whole, on its stated ground that *an agent asked "is
   this right?" says yes*. ADR 0001 applies unchanged: the sweep grading its own record is a
   baseline, not a verification.

5. **The sweep is exhaustive pairwise over all 14,196 pairs, and a subject is a maximal clique.**
   The alternative — merge proposals only, everything else permanently unruled — was refused because
   under it a reader can never distinguish *nothing shares this subject* from *nobody looked*, which
   is the failure this repository names most often. **Cliques and never connected components:** with
   A–B merged, B–C merged and A–C **not** merged, components give `{A,B,C}` and reproduce exactly
   the transitive collapse #689's decision 1 retired the equivalence over; cliques give `{A,B}` and
   `{B,C}`, and B carries both. **Multi-membership falls out of the clique rule** rather than being
   bolted on, and `blood pressure in chronic kidney disease` belonging to two subjects is the
   catalog's own material demanding it. Taking components is the obvious implementation and it is
   the one that rebuilds the ruled-out failure.

6. **A subject's name is elected from a member cell's own catalog topic string.**
   It is the only form the audit can check: a subject value is then either a real catalog topic or a
   typo, and the registry's auditor already knows the full vocabulary, so a misspelling fails instead
   of silently forming a group of one. It also kills the vocabulary-collision hazard by
   construction — 169 agents inventing `blood pressure` / `hypertension` / `BP management` group
   nothing, and under this rule there is nothing to invent. And it degrades loudly on a refresh: if
   an elected name is reworded out of the catalog, the audit fires on every remaining member at once.
   **The elected name is a key, not a label a reader is expected to guess** — the registry lists
   every member cell verbatim beside its subject, so the group is reachable from any member's own
   wording.

7. **`?` is the unruled value, and it never claims a cell is alone.**
   The catalog's own convention, which carries 45 such cells today. The three legal values are a
   subject name, a comma-list of subject names, and `?`; there is no blank and **no implicit
   identity** — `Lyme disease` carrying its own name is a ruling, not a default. A `?` is read as
   *nobody has ruled whether this has siblings*, which is
   [#85](https://github.com/mshamblin5150-code/clinical-skills/issues/85)'s shape exactly, where an
   absent row is *sheet does not settle it* and never *no guideline applies*. **No
   `## Unsettled subjects` section**: the catalog needs one because its `?` cells are permanent with
   per-cell reasons, and these are transient and drain.

8. **Coverage is `ruled cells / 169`, read off the column.**
   A cell is ruled only once every pair involving it has been judged, so the per-cell state carries
   the coverage figure and no pair bookkeeping is needed. **The grilling's own first answer here was
   wrong and is recorded rather than quietly replaced**: it required the command to report *pairs
   compared against pairs total*, which with no negative records could only ever have been a claim
   the sweep made about itself — ADR 0001's baseline-not-verification, arriving inside the ruling
   that cites ADR 0001. The figure is derived and is stated in no prose, on
   [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms.

9. **A corpus refresh may land with the affected rows carrying `?`.**
   The audit refuses a *missing* row and accepts `?`. The refused alternative — blocking a refresh
   until every affected cell is ruled — couples an externally driven mechanical rebuild to a clinical
   judgment, which is how a check gets learned around. **A reworded cell keeps its ruled subject was
   refused as unbuildable, not as undesirable**: the registry carries `topic | subject | state |
   artifact | record` and **no document identity**, so a rename is mechanically indistinguishable
   from one deletion plus one addition, and there is no subject for a transfer rule to key on. The
   declared price is that a ruled subject is **lost** when its cell is reworded; the mitigation is
   the one the registry already affords — the repairer may carry it across by hand and say so in
   `record`, which is a person looking at both wordings rather than a mechanical transfer. What makes
   this safe rather than merely convenient is ruling 7: a refresh that raises the `?` count degrades
   coverage without ever making the column assert something false.

10. **A merge carries a committed evidence record; `reference/thresholds/subjects.md`.**
    One record per group of size greater than one: its members, the evidence each rests on, the
    elected name and why, the refuting agent's finding, and the date. Singletons get no record —
    there is nothing to justify. **The working-ledger form was refused for a reason specific to this
    artifact**: `claims.md` and `checks.md` are gitignored because their content is a patient record,
    not because a working ledger belongs under `scratch/`. Strip that reason and what is left is an
    authored clinical grouping whose entire justification is deleted the moment it lands. A pull
    request was refused as a surface nothing re-derives. The two-copies hazard is real and the answer
    is a **bind** rather than a promise: every group of size greater than one in the column has a
    record, and every record's members carry that subject.

11. **`TOPIC_ALIASES` is retired in the same ticket.**
    It does two jobs wearing one dict. `_topic()` canonicalizes a typed name to a catalog cell **for
    seeding** — the *sheet-name to cell* join, which `coverage.md`'s `artifact` column already
    publishes for all 169 rows rather than for one. `_topic_alias_groups()` supplies the **near-miss
    report key** — the *clinical subject* join, which the column now supplies. Keeping both was
    refused as two hand-kept answers to one question with no test between them; deferring to a
    follow-on was refused because ADR 0078 ruling 5's refusal message reads *record that grouping in
    ticket #689* and would then name a **closed** ticket with the grouping sitting one file away.
    **ADR 0078 ruling 3 survives by construction, which is what makes the swap safe rather than
    tidy:** that ruling forbids `_topic` becoming two-way, and sourcing the seed from `artifact`
    keeps it one-way for free, since one sheet file names exactly one cell and the map has no reverse
    direction to leak through. The dict was conflating a many-to-many question with a one-to-one one,
    which is why a third name broke it.

## What was closed rather than decided

**Which merges are correct.** This record rules the mechanism and the claim shape; every clinical
call is the sweep's, under ruling 4's refutation. The hardest one visible today is not `hypertension`
— it is whether `iron deficiency anemia screening` (pediatric, 2015) and
`iron deficiency anemia screening and supplementation` (pregnancy, 2024) are one subject, which is a
clinical call and not a string call.

**Whether a mechanical cross-sheet gate is ever built.** ADR 0076 names it as this artifact's
sanctioned consumer and no ticket owns it. Nothing here starts one, and ruling 1 deliberately grounds
the artifact on a reader that exists instead.

## Consequences

**#689 is respecced to the mechanism and moves `grilling` to `ready-for-agent`; `blocked` is
dropped**, its gate having cleared when #429 closed. A new ticket owns the sweep, `blocked_by` #689 —
a real edge, unlike the disjunction correctly refused when this was parked.

**Three surfaces of ADR 0076's reader row are amended, and its name is not.**
`the threshold sheets against this patient` still describes the reading, so
`checks_ledger.EXPECTED_CHECKS`, the step 9 table and the README keep their bind without a rename.
*What it reads* gains the `subject` column; *How* gains one clause — group the registry's rows by
subject, and where the patient's problems touch any cell in a subject, open **every** sheet in that
subject — and one clause stating what `?` means. The word *reader* and the population clause are
untouched.

**Two graders, on `checks_ledger.py`'s own precedent.** `threshold_coverage.py` grades the column,
because it is the registry's auditor and the pre-commit gate on a staged registry; a new
`subject_ledger.py` grades the ledger's record shape and owns the bind, because it is the tool
holding both files open. Folding the ledger into the registry's auditor was refused on
[#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240)'s ground — the two share no
field name, so the module would dispatch on which file it was handed and its exit-2 limbs would stop
saying which artifact could not be read. The ledger grader runs when **either** file is staged, since
the bind is two-directional and staging one without the other is how the two drift.

**`threshold_draft.py` gains a registry dependency and three repairs.** A new exit-2 limb for an
unreadable registry, distinguishable from `unknown topic` and naming
`python tools/threshold_coverage.py` as the remedy. `NEARBY_REPORT_BOUND` re-derived from the column,
so the bound stops being permanently *1 of 169* and becomes a live figure that **drains**. And a `?`
topic must not produce a clean-looking empty list: ADR 0078 ruling 4 made an empty near-miss list mean
*nothing further to consider*, which on an unruled subject is false, so the bound sentence says the
subject is unruled for that topic. The drafter still drafts; it cannot claim the join. No cycle —
`threshold_coverage.py` already imports both modules `threshold_draft.py` imports.

**This record supersedes in part.** ADR 0064's Consequences sentence stops being true, and ruling 1's
refusal of a topic-keyed gate stands. ADR 0076 ruling 3's row text is superseded in part; rulings 1,
2 and 4 stand. ADR 0078 rulings 1, 2 and 5 are superseded — the report key moves to the column, the
bound sentence is re-derived, and the third-name refusal is deleted with the dict it guarded; rulings
3 and 4 stand, ruling 3 by a different mechanism.

## What must not come out of this

**A gate keyed on the column.** Its three consumers are the reader row, `threshold_draft.py`'s
report-only near-miss key, and the registry's audit of the column itself. ADR 0064 ruling 1's refusal
is untouched.

**A grouping inferred from catalog wording.** Ruling 3 licenses an agent that **reads the guideline**;
it licenses nothing read off a topic string. ADR 0078's measurement stands — zero shared significant
words between the USPSTF adult cell and the registry's sheet name, and at a zero cut point the report
is noise.

**Connected components.** Ruling 5. It is the obvious implementation and it rebuilds the collapse
decision 1 retired.

**A mechanical replacement for the reader's per-patient judgment.** ADR 0076 ruling 2's prohibition
survives ruling 1 intact.

**Reading `?` as a checked negative.** Ruling 7. The column is least entitled to authority while it
is mostly unruled, which is exactly when it will first be read.

## Declared limits

**A filled column does not prove a merge was considered — a *ruled* cell does.** The distinction is
carried by ruling 7's `?` and by nothing else, so the column's coverage claim is only ever as good as
the honesty of the sweep that stopped writing `?`.

**Ruling 4 buys refutation, never correctness.** A refuting agent that fails to refute a wrong merge
produces a record indistinguishable from one that could not refute a right one.

**Ruling 6's election has no remedy for a subject whose members are all awkwardly named.** The
mitigation is that the key need not be guessable, and the limit is that it is still the string the
column groups on.

**The bind proves the column and the ledger agree, never that any merge is true.**
