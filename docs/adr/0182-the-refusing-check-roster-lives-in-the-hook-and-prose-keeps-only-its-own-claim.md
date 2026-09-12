# The refusing-check roster lives in the hook and prose keeps only its own claim

[#914](https://github.com/mshamblin5150-code/clinical-skills/issues/914) was filed on 2026-09-06
because PR #912 added a seventh check that can refuse a commit while two prose rosters still
enumerated six. Thirteen sweep comments followed. Every one re-derived the count correctly and
**every one undercounted the number of places the roster is written** — the thread moved from "both
prose rosters" to three, four, five, then six surfaces, each correction found by a different pass
looking on purpose. The ticket asked three things: three edits or a bind, whether the hook's
ordinal comments are the right key, and whether `AGENTS.md` needs the roster at all.

Grilled 2026-09-11 to an empty frontier. **Four rulings, by the clinician, on that date.** Nothing
is built here; this is the record the build reads.

## Measured before ruling, at `19f580f` and re-derived at `6db417e`

Freshness gate `FRESH` at `19f580f` before any reading. It reported `STALE` before recording, the
branch was fast-forwarded to `6db417e`, and the count was re-derived on the new base: the merge
touched `tools/guidelines_recs.py`, `tools/test_threshold_sheet.py` and `tools/threshold_sheet.py`
and did not touch the hook. Gate `FRESH` again at `6db417e`.

**Eight refusers.** `grep -c "status=1" tools/hooks/pre-commit` returns 8, at `:65` `threshold_sheet`,
`:74` `threshold_coverage`, `:83` `subject_ledger`, `:89` `scratch_census`, `:98` `uptodate_sheet`,
`:106` `guidelines_currency`, `:115` `apa7_coverage`, `:125` `phi_scan`. *Had the rosters been right,
that count would be 6.* `grep -c guidelines_currency AGENTS.md` and `grep -c apa7_coverage AGENTS.md`
both return 0.

**A module name in the hook is not a refuser.** `guidelines_currency.py` appears twice — advisory at
`:33` with `--hook-summary`, refusing at `:106` — and `phi_scan.py` appears at `:2` in a comment. A
derivation keyed on module names alone reads six advisory or commentary lines as refusers; the join
to `status=1` is what makes the population right.

**Every one of the eight already carries its reason in the hook, beside its own invocation.** Not a
summary: the sixth reads *"A published UpToDate sheet carries citable clinical guidance. Grade the
complete publisher directory only when a topic sheet is staged; its README is the format, not a
topic. The source manifest is gitignored, so this is a local gate."* The hook is a complete,
reasoned, ordinal-numbered inventory that no other file can make stale, because adding a check means
editing it.

**The ordinals are arrival order, not source order, so the ticket's decision-2 worry does not hold.**
It reads *"a hand-kept numbering that renumbers whenever a check is inserted rather than appended."*
`phi_scan` is the first thing that could ever refuse here and sits **last**, at `:125`;
`threshold_sheet` is `# **The second thing in this repo that can refuse a commit**` at `:46`. The
numbers run 2 to 8 down the file while position runs 8, 1, 2, 3. You cannot insert into arrival
order. The real renumbering hazard is the other one: a **removal** leaves a gap or shifts everything
above it. `phi_scan` carries no ordinal at all, named only as *standing rule 1*.

**Six of the eight roster surfaces state more than their own paragraph needs.** `tools/spelling_scan.py:72`
says *"Two things here can refuse one"* inside a bullet whose job is *a spelling is not worth refusing
a commit over*; `CLAUDE.md:2170` lists five siblings inside a sentence whose job is *this check is one
of them*; `AGENTS.md:112` lists six inside a parenthetical whose job is *rule 1's scanner refuses and
this one does not*. A membership claim goes stale only when that check's posture changes. A roster
goes stale every time any check is added, which is why one surface is six behind and the others two.

**Three enumerations exist outside the two root documents, and no comment on the thread named them.**
`docs/adr/0132:150` *"The sixth refuser, joining `phi_scan`, `scratch_census`, `threshold_sheet`,
`threshold_coverage` and `subject_ledger`"* — true when ratified. `docs/adr/0138:237` *"`tools/hooks/pre-commit`
runs seven graders"* and `tools/test_scratch_census.py:466` *"The hook runs seven graders"* — both
present tense about the tree, both now false.

**A reported contradiction did not survive re-derivation.** A sweep agent reported `AGENTS.md:112`'s
*"Rule 1's two checks are still the only ones binding every commit"* as contradicting `CLAUDE.md:2318`.
It does not: the same parenthetical has just listed *"rule 1 via `tools/phi_scan.py`; `tools/scratch_census.py`
on every local commit"*, so **rule 1's two checks** names that pair, which is `CLAUDE.md`'s *"one of
the two that do so unconditionally"*. Ambiguous phrasing, not a wrong claim. Recorded because the
build will read the same sentence and reach for it.

**No detector finds a new roster without firing on correct prose.** Three keys were implemented and
run over every tracked `.md` and `.py`, with the refuser stems derived from the hook rather than typed:

| key | hits | verdict |
| --- | ---: | --- |
| names two or more refuser modules, plus a refusal word | 15 | roughly 2:1 false; hits `tools/test_module_sections.py` on **8 of 8** stems, because that is a table of every command module |
| a count word plus a refusal word | 386 in 161 files | unusable |
| names `pre-commit` plus a refusal word | 22 | 1 true, and **blind to `AGENTS.md:112`, `CLAUDE.md:1549`, `CLAUDE.md:2374` and ADR 0132**, which never name the hook on the line |

The third is the instructive one: it is precise and it misses every surface the ticket exists about.

**A detector keyed on the word *refuser* has a live false-positive population.** `docs/adr/0099:249`
and `docs/adr/0109:150` say *"third refuser"* and *"fourth refuser"* about the **tracker publish
hook's** series, not this one.

## Ruling 1. Each sentence keeps only the claim its own paragraph needs

Six enumerations become one inventory plus five membership claims. A sentence whose job is *this
check refuses*, *this check does not*, or *these two are unconditional* states that and stops. The
drift this ticket is about is caused by sentences carrying a list no reader of that paragraph needed,
and a membership claim is immune to a check being added elsewhere.

This settles the ticket's decision 3 as a by-product. `AGENTS.md:112` becomes a membership claim and
stops being a roster; the file a consumer reads owes them *a commit can be refused, and this scanner
is not one of the things that refuses*, not eight module names.

## Ruling 2. The hook is the inventory, and no prose states a list or a count

`tools/hooks/pre-commit` is the single home. No tracked file outside it enumerates the refusing
checks or states how many there are. `CLAUDE.md` keeps the **principle** — that a fabricated
citation, a false corpus denominator, an unevidenced subject equivalence or a malformed citable
topic sheet is clinical guidance a consumer may rely on — and points at the hook for which checks
and why.

This is `AGENTS.md` standing rule 5 arriving on `AGENTS.md`: *delete an exact figure unless its value
changes a reader's decision; a current figure from a tracked source stays only when the same change
binds it with an equality-backed test.* The delete limb is taken.

**The declined option is a declared Python table the hook is built from.** It is the tidier
architecture and the better fit for this repo's `DECLARED_LIMITS` pattern, and it is refused here
because it moves every staged-path condition out of `git diff --cached | grep -E` and into Python —
a rewrite of the one file guarding standing rule 1, put on a ticket filed about two wrong sentences.

**What the ruling costs, named rather than found later.** The hook carries `#83`, `#93` and ADR 0016
but not `#466`, `#429`, `#689`, `#901`, `#912` or `#976`. Dropping `CLAUDE.md:2374` loses that
provenance, so **each hook comment gains its ticket number as part of the same change.**

## Ruling 3. The hook grades itself, keyed on the ordinal comment

With no prose left to disagree, the failure that matters is a ninth check landing with no comment
beside it: one line of `|| status=1` and the sole inventory is silently incomplete. A test collects
the lines setting `status=1` and the `# **The Nth refusing check.**` comments and asserts each
refusing line has exactly one comment and that no two share one, with `phi_scan` matched by its
*standing rule 1* comment rather than by an ordinal.

**No assertion that the count equals the highest ordinal.** A removal makes a gap and the gap is
correct — arrival order genuinely skips a deleted member.

This is not a new seam. Five checks already assert their own hook line by substring, and two of them
already match on `|| status=1`: `tools/test_scratch_census.py:470` and `tools/test_apa7_coverage.py:296`.
The ruling is the completeness walk over a habit five authors have kept by hand. `tools/shell_reader.py`
exists if structure is ever wanted; a regex read matches what is in the tree.

## Ruling 4. The bind covers a declared surface list, and the blind spot is declared

No walk finds a new roster, so none is built. An explicit list of documents is bound: each must name
`tools/hooks/pre-commit` and, through `prose_bind`'s `NAMING` mode against the stems derived from the
hook, **copy no refuser row**. An entry that stops producing a graded result fails rather than
surviving as a hand-kept promise, which is the arrangement
[#318](https://github.com/mshamblin5150-code/clinical-skills/issues/318) ruled for the allergy gate.
That a roster may arrive in an unlisted file is declared, not closed.

**Graded scope and repair scope are different sets.** Graded: `AGENTS.md`, `CLAUDE.md`,
`tools/spelling_scan.py`. Repaired once and not graded: `docs/adr/0138:237` and
`tools/test_scratch_census.py:466`, whose present-tense claim about the tree is now false —
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)
already rules that a ratified record's facts may be corrected in place, so this is the existing
mechanism rather than a new one. Left alone: `docs/adr/0132:150`, which was true when ratified and is
a ruling's own justification, history the way a fixture note is.

The test that separates 0138 from 0132 is **tense**, which a person applies once and no walk can
read. Grading every ADR that names a count would demand edits to ratified rulings whenever the count
moves, which is how the fix produces a ninth surface.

## What the build verifies

- `grep -c "status=1" tools/hooks/pre-commit` is the only place any count of refusing checks is
  derived, and no tracked file outside the hook enumerates them or states the number.
- Each hook comment carries its ticket number; the eight are `#83`, `#429`, `#689`, `#466`, `#901`,
  `#912`, `#976` and standing rule 1's own.
- The self-grading test fails when a `status=1` line is added with no ordinal comment, when two
  refusing lines share one comment, and passes across a simulated removal that leaves a gap.
- Each graded surface names `tools/hooks/pre-commit` and returns zero copied leaves under
  `bind(stems, section, mode=NAMING)`; an entry whose pointer is gone fails.
- The live-instrument case: a planted roster in a graded surface is caught, on
  `tools/test_claude_pointers.py`'s `TheInstrumentIsLive` precedent.
- `docs/adr/0138:237` and `tools/test_scratch_census.py:466` no longer state a count;
  `docs/adr/0132:150` is unchanged.

## Correction, 2026-09-11, from the tracker sweep of this record's own branch

**Ruling 4's tense test is narrower than it reads, and this record cited neither the ruling that
already governs the adjacent class nor the gap between them.**

[ADR 0131](0131-the-shared-sheet-directory-moves-whole-and-the-mirror-gains-a-non-skill-rule.md)
ruling 6 rules that **a path in a ratified record is a dated statement about the tree at
ratification, and editing one to keep it true would falsify the record.** Ruling 4 above says the
test separating a corrected record from an untouched one is **tense** — and a bare path citation has
no tense. A reader applying ruling 4 literally to `docs/adr/0132`'s sibling class would repair a path
mention that ADR 0131 forbids repairing.

**The two are reconcilable and this record did not do the reconciling.** Ruling 4 was derived from
one class only: a **present-tense assertion about the tree that carries a count** — `runs seven
graders`. ADR 0131 ruling 6 governs a different class, a **path citation**, which asserts nothing
with a verb and is dated by ratification. Ruling 4 does not reach it and never did; the sentence was
written as though it reached every claim in a ratified record.

**So ruling 4 is scoped, here, to the class it measured.** Within this record's own population, the
repaired set is `docs/adr/0138`'s `runs seven graders` and `tools/test_scratch_census.py`'s copy of
it; the untouched set is `docs/adr/0132`'s `The sixth refuser, joining …`. **Nothing here licenses
correcting a path, a link, or any other dated citation in a ratified record**, and ADR 0131 ruling 6
continues to govern those.

**A third class exists that neither record's test reaches**, found on the same sweep against
[#987](https://github.com/mshamblin5150-code/clinical-skills/issues/987): a figure in a ratified
record that was **false when written** rather than made false by drift. Tense does not separate it,
because it was never true; ADR 0131's dated-statement reading does not protect it, because it records
no correct state. It is out of scope here and it is #987's to rule.

**The instrument that found this is worth as much as the finding.** It was a sweep reader pointed at
#987 during this record's own session, re-deriving a ticket whose subject is a copied figure — not a
reading of this record. The first framing it returned was *"ADR 0182 and ADR 0131 ruling 6 give
opposite answers"*, which is wrong: they give answers about different classes. **The claim was taken
as a claim and checked**, which is this repository's rule for a subagent's result, and what survived
the check is the gap rather than the contradiction.

## What this record does not settle

- **Whether a roster has arrived in an unlisted file.** Declared, measured to be undetectable at
  three keys, and not closed.
- **Whether each membership claim is true.** The bind proves a surface copies no row, never that the
  sentence left behind says the right thing about that check.
- **The publish hook's own refuser series.** `docs/adr/0099` and `0109` number a different set; this
  record rules nothing about it and the build must not fold those ordinals in.
- **Whether the hook's staged-path conditions are right.** Untouched here; the inventory is graded
  for completeness, not the patterns for correctness.
