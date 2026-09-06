# A count inside a declared limit is derived or dropped, and the check walks constants rather than prose
<!-- no-numbered-rulings -->

A declared limit — `NOT_GUARDED`, `NOT_REACHED`, `NOT_APPLIED`, `DECLARED_LIMITS`, `WHY_OUTSIDE` and their family — exists so a limit cannot go stale unnoticed, which is [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s ruling. A **hand-typed count inside one reintroduces exactly the failure the object exists to prevent, one level in**: nothing re-derives it, so nothing fails when the population moves. [#457](https://github.com/mshamblin5150-code/clinical-skills/issues/457) found the first instance and asked whether the fix generalizes.

It does, and the class is live rather than anecdotal. Measured 2026-08-23 on `9389070`:

| site | claim | verdict |
| --- | --- | --- |
| `threshold_sheet.WHY_NO_WRITE_GUARD` | *"the four writers"* | **stale** — five write-guarded commands since `voice_corpus` joined on #388 |
| `differential_scan.NOT_VALIDATED_AGAINST` | *"the four ways of not having scanned"* | **underived and ambiguous** — the module docstring enumerates six exit-2 limbs and the object holds four rows, so the referent cannot be determined |
| `docx_write.NOT_APPLIED` | *"none of the six is in the Markdown"* | **correct** — the six elements are enumerated in the same sentence |

`test_write_guards.py:311` already records the first of those being caught once, in that module's own docstring, on #388. **The `WHY_` object one file over was not repaired**, and nothing failed.

## Considered options

**Change the number.** Rejected, and both originating tickets forbid it in as many words — *"do not fix it by changing six to five and stopping"*, *"do not change three to four"*. The corrected number is as underived as the wrong one and the next arrival makes it wrong again.

**Derive it — `len(...)` over the population.** Available for `threshold_sheet` and not for `differential_scan`, whose referent is unsettled, and not for a test class *name*, which cannot interpolate. It also requires a declared-limit object to compute rather than state, which no such object in this repo does.

**Drop the number.** Chosen. *"the other write-guarded commands"* and *"each way of not having scanned"* make the same claim, and neither can decay. **Drop is available wherever derive is, and in the two cases derive is not.**

**Declare the class and build nothing** — [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s and [#275](https://github.com/mshamblin5150-code/clinical-skills/issues/275)'s *declare the coverage rather than widen the instrument*. Rejected **because the measurement refused it**. Both of those rulings declined a widening for a reason — it fired on correct material. Here it does not. Declining an instrument that was measured to work is not what either ticket ruled.

## What the check walks, and why it is not prose

Predicate: `the|those|these` + a cardinal + a word ending in `s`. Measured over four populations:

| scope | walked | hits | real | false |
| --- | ---: | ---: | ---: | ---: |
| declared-limit objects by name prefix | 38 objects | 2 | 2 | 0 |
| **every module-level uppercase constant** | **793 objects** | **3** | **2** | **1, declared** |
| every docstring in non-test `tools/` | — | 86 | 0 | ≈86 |
| every docstring in `tools/test_*.py` | — | 122 | 1 | ≈121 |

**The boundary has a reason and not only a number.** A declared limit states a claim about a population held **elsewhere in code** — that is what the object is for. A docstring is prose about the thing it sits on, so its counts are enumerated in the same paragraph: *"the two tests"* directly above two tests, *"the three rows"* beside three rows. Those are correct and a check firing on them is noise.

**The population carries no vocabulary, deliberately.** A name-prefix tuple would be a hand-typed enumeration inside the check built to catch hand-typed enumerations, and a limit named `UNREACHED` or `CANNOT_REACH` would escape it in silence. *Module-level uppercase constant* is structural, needs no list, and costs nothing: 793 objects yield the same two findings as 38. A `NOT_ALNUM` regex or a `NOT_SCANNED = 2` has no prose for the predicate to fire on, so **over-inclusion is free because the predicate does the discriminating.**

There is no stopword list either. Dropping it adds exactly one hit — `docx_write`'s *"the six is"*, where `is` matched as a plural noun — which becomes the single **declared** exemption with its reason. A stopword narrows the check silently; a declaration documents the narrowing and fails when it goes stale. That is `test_prose_bind.DECLARED_RAW_ASSERT_NOT_IN`'s arrangement and it is chosen here for its reason.

## Consequences

**After both repairs the live population is one.** A check with nothing to find passes vacuously, which is `test_build_artifacts_ignored.py`'s recorded failure, so the instrument needs a positive control asserting its path is live before the survivor set is believed.

**It is a floor and the module says so.** The predicate reads one grammatical shape. *"Three of the six commands"*, *"these three words"* and a bare *"six commands"* are three different sentences and only some are caught. **The sharpest miss is a count in a class *name*** — `TheGlossaryDefinesTheThreeTerms`, [#458](https://github.com/mshamblin5150-code/clinical-skills/issues/458)'s third instance — which no string walk reaches at all, and which is why #458 is repaired editorially rather than by this check.

**Docstrings stay ungraded, permanently.** 208 hits across the two docstring scopes are overwhelmingly correct prose, and no narrowing separated them from the one real finding among them. Widening later needs a new measurement, not an argument.
