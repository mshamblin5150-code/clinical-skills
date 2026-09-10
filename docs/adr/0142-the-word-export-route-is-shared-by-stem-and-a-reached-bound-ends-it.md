# The Word export route is shared by stem and a reached bound ends it

[#803](https://github.com/mshamblin5150-code/clinical-skills/issues/803). Grilled 2026-09-06 at
`origin/main` `bd2d9f3`, freshness gate `FRESH` before reading and before publishing. Every claim
below was re-derived in process against the committed tree; the tracker half was read through
`gh api` into a session scratchpad, so **nothing committed re-derives it** and each tracker
statement is a dated floor. The clinician ruled every point below on that date. **Nothing is built
here; this is the record the build reads.**

The ticket is one sentence long in substance: `skills/practicum-case-study/SKILL.md` specifies a
bounded Word export route in prose, `tools/` holds no command implementing it, and the sibling
`discussion-post` has had one since [ADR 0087](0087-the-rendered-page-check-names-a-spawned-word-route-and-its-verdict-is-a-counted-record-backed-by-kept-pixels.md).
That asymmetry re-derives and is not in question. What five tracker sweeps did not settle is where
the route lives, and the grilling found that the two skills specify **different** routes under the
same word.

## What the grilling found that the ticket did not

**1. The word *fails* already means two things in two skill files, and the divergence is live.**
`skills/discussion-post/SKILL.md` writes *"if Word's PDF route fails, it uses `SaveAs2`"* and means
both a returned failure and a timeout, because `office_process.run_owned_process` raises the same
`OwnedProcessError` for both and `discussion_post_render._pages_from_exports` advances its route
loop either way. `skills/practicum-case-study/SKILL.md` writes *"A call that reaches the bound did
not return a failure, does not trigger the XPS attempt, and goes directly to the clinician export."*
Those are two different routes, stated in two skills, with only one of them implemented anywhere.
The case-study rule is written a second time in `CLAUDE.md` and pinned a third time in
`tools/test_render_scan.py` — as a substring assertion on the skill's prose, so **a test today
asserts the wording of a rule for a command that does not exist.** No ADR ruled it.

**2. Decision 2 of the ticket is false in both halves, and no sweep caught it.** It reads
*"`checks_ledger.EXPECTED_CHECKS` fixes the case study's reader set, so a row there makes a run that
never rendered fail."* `EXPECTED_CHECKS` already carries `the rendered document`, so there is no row
to add; and that row cannot fail a run that never rendered, because `checks_ledger`'s `FIELD` is
`(VERDICT|FINDINGS)` and the module opens no directory. That was measured on
[#866](https://github.com/mshamblin5150-code/clinical-skills/issues/866) and the measurement was
never carried back here. Four sweeps caught the body's other three defects and this one survived all
of them.

**3. Decision 1's remaining horn was mispriced as needing a supersession, and does not.**
[ADR 0111](0111-the-word-export-route-names-its-invocation-mechanism-and-the-hanging-methods-are-a-declared-list.md)
ruling 5 keeps *the method list* unshared, and that list is
`word_automation_scan.LATE_BOUND_WORD_METHODS` — the two method names measured to hang. Its stated
reason is that sharing it would *"either walk `deck_render.ps1` looking for nothing … or grow a
PowerPoint entry on a hypothesis."* That is an argument about Word against PowerPoint. It has no
purchase on two **Word** consumers, and ruling 5's other two limbs — ownership shared, bound
parameterized per site — point the other way.

**4. The body inverts [ADR 0087](0087-the-rendered-page-check-names-a-spawned-word-route-and-its-verdict-is-a-counted-record-backed-by-kept-pixels.md)
ruling 9, which four sweeps found and none repaired.** Re-derived: that ruling is titled *"Scope is
`discussion-post`, and the case study is filed rather than folded in"* and closes *"Leaving the case
study unfiled was refused: that is the version of this ruling that loses the finding."* The phrase
the ticket quotes is its justification for **splitting**. The ticket's entire *What must not come out
of this* rests on reading it backwards, which means it argues for a constraint the cited record does
not impose.

## Ruling 1 — the Word route is one script parameterized by stem, and each producer keeps its own loop

`tools/discussion_post_render.ps1` becomes `tools/word_export.ps1` and takes a `-Stem`. Both
producers call it by name rather than deriving it from their own filename. Its consumer-specific
content is two `Join-Path` lines; everything else in it is ADR 0087 ruling 5's route completed by
ADR 0111 ruling 1, with nothing about a discussion post in it.

**[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s test is passed rather
than routed around.** That refusal is *"a helper two modules happen to have written the same way is
not one that exists to be depended on."* These two would not *happen* to match: the route is ruled,
in ADR 0087 and completed in ADR 0111, and both consumers are bound by it. That is
`console_codec`'s side of the line — infrastructure, rather than a tool another tool happens to
need.

**A second script was refused.** It puts `ExportAsFixedFormat2` and `SaveAs2` in a second file, which
ADR 0111 ruling 3's `tools/*.ps1` walk then has to keep honest, and it creates on purpose the second
implementation site this ticket exists about.

**What is shared is the script and not the route loop.** The ordering ruled below differs between the
two consumers, and it lives in Python. Sharing the loop would make ruling 3 a parameter of a shared
helper for no gain, since there are two consumers and they disagree.

## Ruling 2 — nothing new is graded, and the route record goes to #866

The producer makes `render_scan.py` stop exiting 2 for want of evidence. It grades no new property.
In particular **nothing records which route produced a pass**: a run can export by hand, place the
file, rasterize, and produce output identical to the bounded route.

**A `SOURCE` field on `the rendered document` was refused here.** `checks_ledger` takes exactly
`VERDICT` and `FINDINGS` on every row, so a third field on one row would be the only such field in
that grader. More decisively, `tools/deck_render.py` prints `SOURCE:` into nothing and
has the identical hole, so ruling it here settles one artifact of a two-artifact question inside a
ticket about a third thing — which is what ADR 0111's *What this does not reach* declined to do for
this very ticket: *"folding it in here would put a second skill's missing mechanism inside a record
about one call site's invocation."*

**The question goes to #866**, which already owns which artifact carries a record half and already
carries the deck. Its own prohibition — *"inventing a mechanism to prove a command was run"* — is the
neighboring shape and is not disturbed.

**The cost is declared rather than discovered.** After this build the case study still cannot tell a
run that took the bounded route from one that went straight to the clinician. ADR 0087 ruling 7 ruled
the clinician *"the named escalation, not an equal route"* precisely because equal standing *"makes
asking him the cheap path on every run."* That protection is prose here and nothing measures it.

## Ruling 3 — a returned failure advances the route; reaching the bound ends it

The case-study rule stands as written and is implemented rather than corrected away. PDF first; on a
**returned failure** attempt XPS under the same bound; on **reaching the bound**, do not attempt XPS,
and go to the clinician export.

**The reason is that the two outcomes carry different information.** A returned failure is Word
answering. A timeout is Word not answering, and ADR 0111's own declared limit records that *"no arm
in this session exercised the XPS path"* — XPS-after-timeout is the least-evidenced branch of the
whole route.

**Correcting the case study to the post's ordering was refused**, because the rule was written
deliberately, carries its reason in the sentence beside it, and is pinned in three places.
**Correcting the post to the case study's was refused** because the post's ordering is measured
working and this ticket must not change a shipped route.

**The objection is real and is answered by ruling 4 rather than by ordering.** A case study is a far
longer document than a three-page post; if the bound is low, a timeout means *slow* rather than
*wedged*, this ruling skips the fallback, and the clinician becomes the routine path — the outcome
ADR 0087 ruling 7 refused, reached through the bound instead of through standing. The case-study
prose concedes the premise in as many words: *"it does not establish … that the chosen duration is
calibrated."*

## Ruling 4 — the bound is 20 seconds, uncalibrated, and terminal for automation at this site

`case_study_render.EXPORT_TIMEOUT_SECONDS = 20`, the sibling Word site's value.

**It is the only number with a stated basis.** ADR 0111 measures a typed `ExportAsFixedFormat2` to
PDF at **1,187 ms** — that figure is ADR 0111's to state and is quoted here because this ruling rests
on it — against a document that produced a six-figure byte count of PDF. Twenty seconds is roughly
seventeen times the only measured Word PDF export, which is what ruling 3 needs a timeout to mean:
evidence of a wedge rather than of slowness.

**`30` was refused as typed rather than chosen** — the clinician's own words on 2026-09-02 when he
ruled the existing 30-against-20 divergence an accident. ADR 0111 ruling 5's admitted ground for
divergence is *"a deck with many slides may legitimately need longer than a three-page post,"* which
is PowerPoint against Word. This is Word.

**Measuring first was refused**, on ADR 0111's own declared limit: a measurement here is one document
on one machine on one day, and #768's rule stands that a bound cannot be calibrated from hang data,
because where the call does not return there is no distribution to sit inside.

**What is written beside the constant, because nothing else will say it:** the bound is uncalibrated,
it is a safety stop rather than a timing measurement, and reaching it at **this** site ends the
automated route rather than advancing it. That consequence is stronger here than at either sibling
and is invisible from the constant alone.

## Ruling 5 — the clinician export is supplied on a rerun, and there is no `--expected-pages`

The command is `<run-directory> --docx <path>`, with `--clinician-export <PDF-or-XPS>` on a second
invocation after the first exits 2.

**Hand-placing the export into a pass directory is retired.** The current prose says *"place that
export in the new pass directory,"* which means the agent picks the number, creates the directory and
rasterizes by hand, bypassing `render_pass.retain_staged_pass`. That retention exists so a build that
dies leaves **no** pass; hand-placement reintroduces the partial-pass-retained-as-evidence shape
[ADR 0124](0124-the-render-pass-is-one-shared-reader-and-a-gap-is-counted-rather-than-graded.md)
ruling 2 shares the mechanism to prevent.

**The rerun shape also discharges ruling 3 without a conditional route list.** Invocation one attempts
PDF, attempts XPS only on a returned failure, and exits 2. Invocation two is handed the file.

**`--expected-pages` is refused rather than copied.** A `.docx` states no page count — ADR 0124
ruling 2, *"a `.pptx` states its slide count and a `.docx` states nothing"* — the flag appears
nowhere in `skills/discussion-post/SKILL.md`, and
[ADR 0125](0125-render-coverage-and-the-render-record-are-two-properties-and-each-artifact-wires-them-its-own-way.md)
ruling 3 has already filed a defect about it being *"optional at the invocation that decides
completion."* Copying it forward propagates a shape already ruled defective at the site it came from.

## Ruling 6 — the prose is kept, restated as the contract the command implements

`skills/practicum-case-study/SKILL.md` keeps the route paragraph and gains the command beside it,
which is the arrangement the same step already uses for `render_scan.py`. `AGENTS.md` gains the
producer in the paragraph that already classes this skill's render as a dependency.

**Deleting the prose was refused** on the ticket's own terms, and **cutting only the unwalkable half**
— fresh spawn, bound, process ownership — was refused because those sentences are why the clinician
escalation is not an equal route, which ADR 0087 ruling 7 ruled load-bearing. Cut them and the
clinician line reads as an arbitrary fallback.

**The by-eye equivalent is named rather than implied**, in ADR 0087's own words: a consumer that
cannot run the producer has *"`SOURCE: clinician` as the whole route."* That is a real path, not a
dead end.

**This is where the ticket's premise is discharged.** `tools/test_render_scan.py` asserts three
sentences about a command that does not exist. With a producer, ruling 3 becomes assertable as
**behavior** through a stubbed runner, the way `tools/test_discussion_post_render.py` already drives
its route loop. That is [#214](https://github.com/mshamblin5150-code/clinical-skills/issues/214)'s
*what a written instruction cannot do is fail*, closed on the one rule this ticket is named for. The
prose binding stays as well, because it is what keeps the skill and the code from drifting apart.

## Ruling 7 — `CONTEXT.md` gains **Bounded export route**

One entry, holding the distinction finding 1 found written two ways: a returned failure advances the
route, reaching the bound ends it, and the clinician export is the named escalation rather than an
equal route. No module, flag or filename is named, on ADR 0125 ruling 2's precedent, which took
`CONTEXT.md` *"for the vocabulary"* and refused it *"for the wiring."*

**Leaving it to this record was refused.** An ADR ruling is read by whoever opens the record; a
glossary entry is read by whoever writes the next sentence. The distinction has already been written
two ways in two skill files, and
[#165](https://github.com/mshamblin5150-code/clinical-skills/issues/165)'s prediction in this
repository is that the wrong reading is the one a new sentence copies.

## What this does not reach

**Whether the automated route works on any machine.** Every measurement this record rests on is
ADR 0111's, one machine on one day, and that record's own limit says so. Nothing here establishes
that a case study exports under twenty seconds, or at all.

**Which route produced a given pass.** Ruling 2's declared cost, in full: after this build a
hand-exported pass and a bounded-route pass are indistinguishable to every grader in the tree, for
the case study and for the deck alike. #866 owns it.

**Whether the bound is the right length.** Ruling 4 states a basis, not a calibration. Twenty seconds
is a ratio against one measurement of one document, and #768's rule stands that hang data supplies no
distribution.

**Whether the retained images are the pages a reader read.** Unchanged from ADR 0098 ruling 3,
ADR 0124 and ADR 0125: `render_scan` grades coverage, `checks_ledger` grades the substantiated
verdict, and a clean run of both is not a checked render.

**Anything about the deck's missing record half.** ADR 0124 ruling 4 and ADR 0125 ruling 1 rule
placement; #866 owns the record half. Nothing here disturbs either.

**Whether ruling 3's ordering is clinically or mechanically better than the post's.** It is ruled on
the information the two outcomes carry and on which branch is least evidenced. Two artifacts now hold
two orderings deliberately, and no measurement compares them.

---

**Corrected in place 2026-09-10, on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
rule and
[ADR 0022](0022-an-adr-carries-no-status-field-because-no-record-waits-on-main-for-a-decision.md)'s
precedent.** One fact clause in ruling 2 named the wrong source. It read *"a third field on one row
breaks a uniformity that grader's own docstring argues for."* `tools/checks_ledger.py`'s docstring
makes no argument about fields; the uniformity argument is
[ADR 0098](0098-the-case-study-s-rendered-document-coverage-is-derived-from-kept-evidence-and-owned-by-its-own-run-directory-grader.md)
ruling 2's, which rules that `the rendered document` record gains no fields. The clause now states
only the field count. Ruling 2's
decision — refuse `SOURCE` here and hand the route question on — is untouched, and
[ADR 0161](0161-the-deck-and-case-study-render-records-name-the-final-pass-and-route.md) is the
answer to it.
