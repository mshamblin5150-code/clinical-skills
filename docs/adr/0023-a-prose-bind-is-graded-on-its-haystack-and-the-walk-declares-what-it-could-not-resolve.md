# A prose bind is graded on its haystack and the walk declares what it could not resolve

[#474](https://github.com/mshamblin5150-code/clinical-skills/issues/474) was split out of [#445](https://github.com/mshamblin5150-code/clinical-skills/issues/445)'s grilling on 2026-08-23, on the ground that a second instrument arriving inside a change about a stale claim is one nobody has driven a mutant through. Grilling it on 2026-08-23 confirmed the finding, **falsified the remedy**, and found a better population than the one the ticket predicted.

The clinician ruled on 2026-08-23.

1. **The discriminator is the haystack, not the needle.** `test_prose_bind.repository_survivors` refuses a raw `assertNotIn` whose constant needle is 40 characters or longer. That is a stand-in for *the haystack is prose*, and the stand-in is retired rather than tuned.
2. **The filter is positive, and unresolvable is its ordinary state.** The walk proves a haystack resolves to a tracked-file read and fires there. It does not refuse what it could not resolve.
3. **The silent-pass prohibition is honored at the walk, not at the site.** The resolved population is pinned as a floor, so a resolver that quietly stops resolving goes red. What it cannot reach is declared, with its size.
4. **A site fires only where normalization can change the outcome** — the needle carries whitespace or glue. A needle with neither is outside the population rather than declared, because there is nothing to declare about a transform that is a no-op on both sides.
5. **`assertIn` is excluded on the direction of failure, never on the count.** Formatting drift can only make `assertIn` fail. The silent direction is the only direction the helper exists for.

## What was measured

Every figure below was measured on `d3e39e6` immediately before the ruling and **re-derived unchanged on `e234687`**, the merge that carries this record — a merged tree is one neither branch produced, which is [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s unguarded moment. The population is the 71 tracked `tools/test_*.py` modules, counting only two-argument `assertNotIn` with a constant string needle. The module owns the live counts; these are the dated evidence the ruling was made from.

**The ticket's headline figures hold.** 233 such sites; exactly 2 at the 40-character floor, both already declared; 26 shorter sites carrying glue.

**The ticket's proposed remedy reaches none of the sites it claims.** It proposes firing where *"the haystack is a read of a tracked `.md` or `.py`"* and asserts *"that reaches all 4 real sites and excludes all 22."* Resolving the second argument of every site shows otherwise:

| site | haystack |
| --- | --- |
| `test_phi_scan.py:922` | `self.report(1, 3)` — the scanner's generated report |
| `test_specificity_scan.py:408` | `scan.brief(...)` — the tool's generated brief |
| `test_uspstf_table.py:730` | `ut.render_markdown([old, new])` — generated Markdown |
| `test_uspstf_table.py:372` | `region.text[:120]` — a PDF fixture slice |
| `test_threshold_sheet.py:1169` | a synthetic sheet the test `re.sub`'d a section out of |

**Not one reads a tracked file.** A haystack rule fires on zero of them, and the only direct-`read` haystacks in the tree are the two the walk already declares. As written, the remedy reproduces the current declared set and adds nothing.

**Its 26-site breakdown is off by one in two places.** `test_docx.py` contributes 18, not 19, and the prose residue is 5, not 4 — the missed site is `test_uspstf_table.py:372`, `'Preventive Services Task Force*'`. The total is unchanged; the split moved.

**The population the measurement does support is different and better.** Resolving the haystack through one hop of assignment finds **20** sites reading tracked files. Eighteen are new and **none is at the 40-character floor**:

```
tools/test_skill_agreement.py:110   'under GAPS'
tools/test_skill_agreement.py:111   'unfilled'
tools/test_research_ledger.py:1141  'five years the outside limit'
tools/test_name_index.py:575        'no generator for the index is committed'
tools/test_guideline_sheets.py:591  'and for the same reason: no guidelines'
```

`'under GAPS'` is ten characters, carries no glue, and is asserted absent from a tracked skill file. Let that file wrap between the two words and the assertion passes vacuously. **That is the silent-pass shape the helper exists for, and both the length floor and the ticket's own glue framing miss it.**

**The real discriminator is neither length nor glue.** It is that the needle spans a point where the haystack may wrap. Sixteen of the 20 carry whitespace; for all sixteen `normalized(needle) == needle`, so the entire benefit is on the **haystack** side, collapsing the file's hard wraps.

**213 of the 233 do not resolve** — 113 to a name assigned to something that is not a read, 40 to an unnamed call, 22 assigned outside the scope, 38 attributes, subscripts and comprehensions.

## The population and what fires

| | |
| ---: | --- |
| **20** | haystack resolves to a tracked-file read — 3 direct, 17 through one assignment hop |
| **17** | of those, the needle carries whitespace or glue — **the firing population** |
| **16** | convert to `assertProseNotIn` |
| **1** | declared: `test_discussion_post_skill.py:80`, `'<course>-<module>-<date>'` |
| **3** | outside the population: `'scratch/claims.md'`, `'scratch/checks.md'`, `'unfilled'` |

The declared one is the ticket's own objection arriving inside its retargeted population. `'<course>-<module>-<date>'` is a run-key template whose angle brackets are **syntax, not emphasis**, and it normalizes to `'<course -<module -<date'`. Converting it still works — both sides mangle identically — but it is meaningless, and it makes the bind match more loosely than the raw one. That is `<w:i/>` one population over.

The three outside carry neither whitespace nor glue, so `normalized()` is a literal no-op on both sides. **The exclusion is self-correcting**: widen `'unfilled'` to `'unfilled vitals'` and the walk picks it up with no rule change.

**A line slice does not earn a limb.** Of the 16, fourteen read a whole document, one reads a multi-line frontmatter block, and exactly one is a single line — `test_skill_agreement.py:110`, a Markdown table row pulled out with `next(... splitlines() ...)`. A line cannot hard-wrap, but collapsing a table row's column padding is a real drift, so converting it is harmless rather than meaningless. One site is a declaration, not a rule.

## Why the filter's direction had to invert

The length floor is a **negative** filter: everything long is suspect, and the declared dict is the escape hatch. That is affordable at N=2.

A haystack rule is a **positive** filter: prove the haystack is a read, then fire. Unresolvable is its ordinary state, not its exception. Carrying the floor's conservative posture across would mean **213 declarations**, each needing a hand-written reason, in a file that holds two. That is not a stricter check; it is a check nobody can land.

So #474's prohibition — *"Do not make it pass silently where it cannot resolve the haystack"* — is honored one level up. The danger it names is real, but it is the **walk** silently reading less than it used to, not any individual site going ungraded. A floor on the resolved-read population catches that; a 213-entry dict does not. Coverage is stated as **20 of 233**, plainly. It reads thin because it is thin, and the alternative is a rule that reads complete while resolving nothing.

The 40-character floor is deleted rather than kept beside it: both sites at the floor are inside the resolved 20, so the haystack rule is a **strict superset** on this tree. Keeping it would preserve the coincidence the ticket was filed against, on the argument that the coincidence might be load-bearing later — which is the reasoning that put it there.

## Considered options

**Widen by needle length** — #474's own *What must not come out of this*. Rejected, and the ticket is right: dropping the floor pulls in 26 sites of which 18 are raw OOXML and 2 are regex patterns, where `<`, `>`, `"` and `*` are syntax. `normalized('<w:i/>')` is `'< w:i/'`. Not a weaker check, a meaningless one.

**Refuse on an unresolvable haystack.** Rejected on the measurement above: 213 declarations.

**Keep the floor beside the haystack rule.** Rejected. Costs nothing today and buys only that a future long needle with an unresolvable haystack is still refused — at the price of keeping the proxy this ADR retires.

**Extend to `assertIn`.** Rejected on direction. 331 constant `assertIn` sites resolve to a read, sixteen times the population, but formatting drift can only make `assertIn` **fail** — loudly, at the site, naming the string. Converting them would buy false-alarm reduction, not correctness, behind an argument that only holds for the 20. The reason lives in the module rather than only here, because *"almost certainly not, they're inline-code identifiers"* is the kind of half-reason that gets re-litigated and *"the silent direction is the only direction"* cannot be. No follow-up ticket is filed: no `assertIn` in this tree has been observed going red from a rewrap, and the day one does is the day it earns one.

## Two rules the implementation does not get to choose

**The resolver is scope-aware: function, then class, then module, first scope wins.** `test_skill_agreement.py` binds `text`, `setup` and `voice` to **both** `read(X)` and `squashed(read(X))` in different functions. A name-level resolver reports three false `squashed` hits on that file; a scope-aware one reports none. This was found by a first pass getting it wrong.

**Any assignment being a read counts, not all of them.** Measured at zero instances — no site has two assignments to one name inside a function — so it is a ruling about the rule's safe direction rather than about this tree. Over-firing costs a declaration; under-firing is a silent gap. [#204](https://github.com/mshamblin5150-code/clinical-skills/issues/204) records that the safe direction of a rule is a property of the rule and not of the pair it belongs to.

## Vocabulary

`prose_bind.GLUE` is renamed. `CONTEXT.md` already glosses **Glued run** — words reaching extracted text with no space between them, because the PDF set no space glyph — which is an unrelated sense of the same root, and the older and more specific one. `test_skill_agreement.py:964` sits on the collision: it asserts a *glued run* is absent while the helper that would grade it is named for the other sense.

**Prose bind**, **needle** and **haystack** are glossed, because after this ADR the last two carry the rule.

The rename lands inside this change rather than as its own ticket. It has five importers rather than fifty, the module is being rewritten anyway, and the alternative documents a collision the repo then keeps paying for. The cost is named: a mechanical rename rides alongside a ruling, and this repo has recorded that a ruling bundled with a rename is one that gets read past.

## What this does not reach

**213 sites, and the number is stated rather than implied.** The walk is a floor on membership binds whose haystack it could prove, and nothing else.

**Whether a converted bind is a *true* claim.** Normalizing makes an assertion robust to formatting; it says nothing about whether the sentence should be absent from that file. A clean walk is not a checked bind.

**Prose enumeration and counting**, which stay outside `prose_bind`'s ceiling exactly as [#412](https://github.com/mshamblin5150-code/clinical-skills/issues/412) declared. A test that counts occurrences in prose can still undercount silently, and no membership helper reaches that.

**A haystack assembled at run time**, or one reached through an imported helper rather than an assignment. That is `tools/test_ls_files_coverage.py`'s ceiling arriving on a second instrument: the honest claim is a floor on the shapes in the tree, never *a further unguarded site cannot arrive*.

## Consequences

- `raw_long_assert_not_in` is deleted. `DECLARED_RAW_ASSERT_NOT_IN` empties — both current entries convert — and becomes a one-entry exception list needing a name that is about neither rawness nor length.
- Sixteen call sites across seven modules move to `assertProseNotIn`.
- The walk gains a floor on its resolved population, and a mutant is driven through both the resolver and the firing predicate before either is believed.
- [#445](https://github.com/mshamblin5150-code/clinical-skills/issues/445) is **disjoint, measured**: all 50 `squashed`-backed assertion sites in `test_skill_agreement.py` are `assertIn`, so no `assertNotIn` haystack passes through `squashed`. Either ticket may land first.
