# Prose binds share one normalizer and a raw assertion declares its reason

[#412](https://github.com/mshamblin5150-code/clinical-skills/issues/412) shipped `tools/prose_bind.py` so a prose bind survives hard wrapping, Markdown emphasis and quotes split across adjacent literals. [#445](https://github.com/mshamblin5150-code/clinical-skills/issues/445) found two sites that did not adopt it: `test_run_record_claim.normalized`, byte-identical to the helper and holding its own copy of `GLUE`, and `test_skill_agreement.squashed`, the whitespace-only subset.

`prose_bind` is now the repo's one prose normalizer. `squashed` is deleted. A bind that keeps a raw assertion declares why.

## This overrides a standing default, which is why it needs a record

[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253) refused exactly this extraction for `research_ledger` and `checks_ledger`'s copied field parser, on the ground that **a helper two modules happen to have written the same way is not one that exists to be depended on, and a test pinning the agreement would forbid the divergence the copy exists to permit.** A reader who finds #253 first will conclude this consolidation was a mistake.

What earns the override is a measurement rather than an argument, taken 2026-08-23 on `9389070`:

- `prose_bind.GLUE` and `test_run_record_claim.GLUE` are **byte-identical**, and the two `normalized` functions produce **identical output over all 268 tracked `.md` and `.py` files — zero differences.** There is no divergence for the copy to permit. #253's test finds nothing to protect.
- Moving every `squashed` site to `prose_bind` changes **no verdict**: 90 constant needles against 7 haystacks, 0 changes.
- The two sites feeding *regexes* rather than assertions — `BLANKET_STANDING.finditer` and `NOT_IN_FORCE_FORMS` — carry no glue characters in their patterns, so they call `prose_bind.normalized` directly.

`prose_bind` is `console_codec`'s class of module: infrastructure, not a tool another tool happens to need. That is the test #253 states and this passes it where `keyword_of` failed it.

## The safe direction is opposite for the two assertions

#445 states the weakness for absence only. It runs both ways, and the distinction decides the policy:

- For **`assertNotIn`**, a *weak* normalizer is unsafe. A needle wearing a backtick is invisible to `squashed`, so the absence passes for the wrong reason.
- For **`assertIn`**, a *strong* normalizer is the loose one. Strip the emphasis and the bind stops caring whether the phrase was bolded at all.

Adopting `prose_bind` wholesale therefore tightens every absence bind and loosens eleven presence binds in `test_skill_agreement.py` alone. This is `filled_vitals_census`'s recorded lesson verbatim: **the safe direction of a rule is a property of the rule and not of the pair it belongs to, so a boundary is not the mirror of its twin.**

## Considered options

**Adopt `prose_bind` everywhere, delete the raw path.** Rejected: silently loosens eleven presence binds, including ones whose subject *is* the formatting.

**Split by assertion kind — absence normalized, presence raw.** Rejected: refuses the long hard-wrapped definitions `assertProseIn` was built for.

**Declare the split that already exists.** Chosen. `test_ruling_cohort.py` already mixes them on purpose — plain `assertIn("**Ruling cohort**:", ...)` for the short formatted marker, `assertProseIn(...)` for the definition beneath it. Formatting-as-subject raw, formatting-as-glue normalized. Nothing declared that rule; it is declared now, and each raw site carries a reason. The two entries in `DECLARED_RAW_ASSERT_NOT_IN` reading *"the module owns squashed"* get real reasons, because that one dissolves the moment `squashed` does.

## The declared-raw walk keeps its population, and its floor is renamed

`test_prose_bind.repository_survivors` refuses raw `assertNotIn` at a 40-character floor. That population is **exactly 2** across all 71 tracked test modules. Dropping the floor to catch short glue-carrying needles pulls in 26 sites, of which:

| | |
| ---: | --- |
| **18** | `test_docx.py` raw OOXML — `<w:jc w:val="center"/>`, `<w:i/>`, `w:val="28"`, where `<`, `>`, `"` and `*` are **XML syntax, not prose glue** |
| **2** | `test_case_study_scan.py` regex patterns — `#{1,4}`, `[-*+]` |
| **1** | a run-key template — `<course>-<module>-<date>` |
| **5** | genuinely prose |

`prose_bind.normalized('<w:i/>')` returns `< w:i/`. The transform is meaningless on 21 of the 26, so the widening is refused on the measurement.

**The 40-character floor is not a length rule; it is a cheap stand-in for *the haystack is prose*, and it works today only because at that length the tree holds two sites and both are prose.** The walk does not move, and its docstring now says that rather than presenting a floor on length. Discriminating on the haystack instead — firing only where the second argument reads a tracked `.md` or `.py` — reaches none of these five prose sites because none reads a tracked file. ADR 0023 records the different population that the resolver does reach. The change was correctly filed as its own ticket rather than folded in: it is a second instrument with its own ceiling, and one arriving inside a change whose subject is a claim that went stale is one nobody has driven a mutant through.

## Consequences

`test_run_record_claim.GLUE` carries a comment recording that a backslash was in that set and came out, measured both ways over every tracked `.md` and `.py`. **That reasoning is about the shared object and moves with it**, or it is lost when the copy is deleted.

`squashed`'s weakness stays latent rather than live. All three declared raw needles were driven through `prose_bind.normalized` against their real haystacks and **no verdict flipped**. #445's *"no defect is recorded"* survives the mutant; what changes is that the two can no longer drift.

Correction, 2026-08-23: the 26-site breakdown formerly said 19 raw OOXML sites and 4 prose sites, called the transform meaningless on 22, and said the proposed tracked-file discriminator reached all four prose sites. ADR 0023 re-derived 18 raw OOXML sites, 5 prose sites and 21 meaningless transforms, and found that none of those five haystacks reads a tracked file. The ruling to keep the second instrument separate is unchanged.
