# The readme gate is a set difference and standing stays distinct from edition currency

[#772](https://github.com/mshamblin5150-code/clinical-skills/issues/772) was filed on 2026-09-01
because `README.md` had no gate over its figures, and it specified a build: a marker-delimited
generated block, `tools/readme_currency.py --write/--check`, a CI step and a pre-commit entry. This
record rules that build out, rules the gate that replaces it, and settles a glossary distinction
that eight tracker sweeps have read the other way.

**The premise the ticket was filed on is spent, and the premise it acquired is wrong.** #401 closed
ninety minutes after #772 was filed, and what it shipped states **no figure at all** — so there was
never a hand-written figure to replace. Then, from 2026-09-05, five successive sweeps recorded
`README.md:53` as a live falsehood on the ground that `reference/guidelines-currency.md` now records
what that line says the repository cannot establish. Under this repository's own glossary that
reading is a conflation of two terms, and this record names which.

## What was measured before ruling, on 2026-09-09

Freshness gate `FRESH` at `eebfd4e` at both checkpoints. Every figure below was re-derived on this
branch. The tracker figures are measurements of a moment; the ones taken from committed files are
not.

**`CONTEXT.md` carries two terms for what looks like one question, and they were written eleven
hours apart by branches that never met.**

| term | says | written in |
| --- | --- | --- |
| **Guideline standing** (`:453`) | *"still the guidance its society issues... It is recorded nowhere... is not [knowable from inside]"* | `bc4b31e`, #401's branch — **the same commit that wrote `README.md:53`** |
| **Edition currency** (`:459`) | *"whether the society... still **lists** that document as what it currently publishes"* | `0bb41a7`, ADR 0134 |

The later commit did not touch the earlier entry. Every sweep since has read the second term's
artifact as an answer to the first term's question.

**The registry's own numbers say it is not that answer.** Parsing
`reference/guidelines-currency.md`:

```
180 document rows      current 170   superseded 2   unjoinable 8
dated `observed`:  2   — and both are the superseded pair, 2026-09-05
blank `observed`: 178  — every `current` row and every `unjoinable` row
  9 society rows        all `read`, all `last observed 2026-09-05`, all `state observed` blank
```

`python tools/guidelines_currency.py --hook-summary` prints `never checked 178. Remedy: run
guidelines_currency.py --read SOCIETY.` **`_run_reads` prints and returns; it writes nothing.** The
only path that stamps `observed` is `--fetch-replacement`, which is why the two dated rows are
exactly the two superseded ones. The remedy the shipped instrument names cannot discharge the
condition it reports.

**The derivation #772 proposed has already been built and deleted, and the reason matters.**
`TheReadmeSocietyStatementMatchesTheCatalog` was added in `2fa0338` at 16:10:37 and deleted in
`8acc95d` at 16:12:51 — **2 minutes 14 seconds**. The deleting commit's README diff removed exactly
two words, `nine societies:`. The helper was welded to that phrase in **two** places, its block
predicate and its regex, so removing the count did not break one assertion — it made the parser
unable to find its paragraph. The class asserted the name set *and* the count; only the count became
unstateable, and the set binding died as collateral with no recorded reason.

**`catalog_societies()` still works verbatim**, returning `ACIP, ADA, AHA ACC, CDC, GINA, GOLD,
IDSA, KDIGO, USPSTF`. It splits on the documents-table header and takes every pipe row below it; the
legend table happens to sit above it and `## Unsettled cells` happens to be bullets.

**A naive path matcher fires on six correct sentences.** `SKILL.md`, and the bare module names
`guidelines_build.py`, `guidelines_catalog.py`, `phi_scan.py` and `threshold_coverage.py`, are prose;
`scratch/voice-model.md` is gitignored and **must** be absent in a clean clone. Markdown link
targets measured 8 of 8 resolving with no false positive.

## Ruling 1. Guideline standing and edition currency are two terms, and the registry answers the second

A currency verdict records whether a society's published index lists a document. Standing is whether
the document is still the guidance that society issues. The two are close and they are not one: a
society can leave a retired document on its list, or drop one still in force, so an index read is
evidence about standing and never standing itself.

`README.md:53`'s first clause is therefore **true as written** and is not edited. Eight sweeps have
now recorded it as false; the conflation is the defect, not the sentence.

`CONTEXT.md`'s **Guideline standing** entry gains one sentence naming edition currency as the
nearest recorded evidence and saying why it stops short, because *"recorded nowhere"* standing
beside a tracked registry is what invited the misreading eight times.

## Ruling 2. The currency pointer is bare, and no figure goes on the public page

`README.md:53`'s pointer to #767 is stale — that issue is closed and `tools/guidelines_currency.py`
shipped — and is replaced by a pointer to `reference/guidelines-currency.md` naming what it records:
what each society's published index currently lists, per document.

**No figure accompanies it.** Publishing `178 of 180 carry no recorded observation date` beside a
heading reading *Which guidelines these rest on* would be read as *178 documents of unknown clinical
validity*, which is false — they are documents whose societies still list them. The count is a
maintainer's signal, printed by `--hook-summary` to the person who can act on it, and a stranger
cannot. This is the ticket's own *a currency claim that reads as a standing claim* prohibition,
biting in the direction nobody expected.

## Ruling 3. The gate is a set difference over authored prose, not a generated block

`tools/readme_currency.py` is not built. No markers, no `--write`, no `--check`, no CI step, no
pre-commit entry.

The ticket's mechanism was specified for a moving figure and ruling 2 puts none on the page. What is
left to bind is a **set** and a **path list**, and this repository already runs the right instrument
on the same file: `TheReadmeNamesEveryShippedSkill` binds the README's skill tables to `skills/*/`
with two directional assertions over prose a human wrote. A set difference against a committed
catalog also satisfies the ticket's *a checker that passes because it compares the block to itself*
prohibition outright, which a generated block satisfies only by argument.

The ticket's decision 2 dissolves rather than resolving: with no command there is nothing to wire
into the hook, so the gate fails the suite and CI at the merge and never refuses a commit. That is
where ADR 0134 ruling 4 already points — a stale guideline never refuses a commit; the registry's
own integrity does.

The ticket's decision 3 is closed rather than deferred. The skill table is not generated. Its
founding defect was a stale count, the count is gone from the README, and the names are already
bound in both directions; the only field generation would reach is the `description` frontmatter,
which is written to make an agent route correctly rather than to tell a stranger what a skill is
for.

## Ruling 4. The target set is the society list and rooted paths, and ignored roots are refused

Two directional assertions bind `README.md`'s nine-society sentence to `reference/guidelines-catalog.md`,
and one walk resolves the README's rooted repository paths.

The society parser **anchors on the link to the catalog, never on a count word** — that is the
recorded cause of the 2-minute-14-second deletion, and no number is load-bearing. The catalog read
is bounded at the next `## ` heading, closing an over-read that is latent today. The `/` in
`AHA/ACC` is a co-publication separator in README prose and a space in the catalog column; that is a
fact about two files' conventions and lives in a named constant with the sentence beside it, because
a loose normalizer is how a wrong name passes.

The path walk resolves rooted, non-ignored, non-placeholder paths. **`scratch/` and `output/` are
refused by name**: a checker requiring `scratch/voice-model.md` to resolve would demand a PHI-bearing
file exist in a clean clone, inverting the guarantee the PHI section makes to the same reader two
headings later. A token with no separator is prose, and a shape carrying a placeholder is not a path.

Refused as targets: the corpus figure, which `reference/guidelines-catalog.md` already carries and
declares a sum of its own column; the latest audit date, which is one constant across all 180 rows
and would read as a currency signal it is not; and `README.md:88`'s Python floor, which
[#927](https://github.com/mshamblin5150-code/clinical-skills/issues/927) owns and which nothing has
yet measured.

## Ruling 5. The gate declares what it does not reach, and says first that it misses its own motivating defect

A top-level `README_NOT_REACHED` in `tools/test_skill_agreement.py` carries six rows, held by a
meta-test in the same module. It is deliberately **not** named `DECLARED_LIMITS`: that name means
*this module's limits* and would assert something false about 27 unrelated classes, so the object
takes no bind from ADR 0119's walk and the meta-test is the only thing holding it.

The first row states that external URLs, issue links and bare filenames are unresolved — **so the
`#767` pointer that opened this ticket is a defect this gate would not catch.** The honest phrasing
is required rather than the accurate-and-burying *external links are not resolved*, because a green
suite otherwise reads as *the README's claims are checked*.

The second row states that ruling 2's new sentence is itself ungraded: nothing checks that its
description of the registry matches what the registry records. It has the same shape as the sentence
it replaces, and declaring that is cheaper than a sweep rediscovering it.

The remaining four: a skill row's description can drift from its skill; a resolving path says nothing
about its contents being current; an ignored path is refused by name, so a *wrong* one passes; and
nine correct society names do not make the sentence around them a true characterization.

## Ruling 6. An observation date is earned by a read, and the read becomes the writer

`--read` stamps `observed` and writes `current` for the documents its join **matched**.
`IndexComparison` already computes that set and discards it; returning it is the change. ADR 0134
ruling 8's own words carry this — *"its documents keep the verdict and date they last earned"* — so
the blank column is an unimplemented write rather than a narrower meaning.

**A corpus-absent document gets neither the date nor a verdict.** Ruling 8 forbids collapsing
`absent` and `superseded`, and stamping a date while leaving a stale `current` on a document the
index no longer lists would publish *looked at on this date, still current* about the one case where
that is false. Those rows are reported for a person to rule.

Never-checked then falls toward the 8 `unjoinable` rows, which carry no value in the key their
society is joined on and which no index read can ever answer. Blank stays where blank is the true
answer, and the printed remedy discharges the condition it names.

ADR 0134 is not amended. Its ruling 2 (the read is per society and joins back) and its ruling 8 (a
row with no observation date has never been looked at) are both preserved, and this record supplies
the write that made them consistent.

## What this record does not settle

Whether any corpus document is still sound guidance. That is **Guideline standing**, ruling 1 keeps
it unrecorded, and no instrument here reaches it.

Whether the nine societies are the right nine, or whether the corpus covers any given topic. The
gate binds a set to a catalog; it does not review the catalog.

Whether `--read` writing to a tracked registry needs the artifact lock the guideline builds take, and
what two concurrent reads of different societies do to one file. Ruling 6 names the write and not its
concurrency.

Whether `README.md:88`'s Python floor is the right floor.
[#927](https://github.com/mshamblin5150-code/clinical-skills/issues/927) owns it, and ruling 4
deliberately leaves it there rather than binding a figure nobody has measured.
