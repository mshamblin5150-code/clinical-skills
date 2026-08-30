# A bound label reads to its own recommendation and every window ADR 0029 measured was forward

[ADR 0029](0029-a-bound-recommendation-record-is-a-label-and-its-marker-anchor-decides-which-way-it-reads.md) ruled [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436) on 2026-08-24 and its body became the build spec. **Six tracker sweeps since have found five of its six build items unbuildable as written**, and the ticket has carried `grilling` on that ground five times without the residue being settled.

Grilled 2026-08-27. The clinician ruled every point below on the same day. This record **supersedes the paragraphs of ADR 0029 named below** rather than amending them: 0029 is cited by URL from #436's body and from [#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438), and a reader landing there from an old link must not be reading a falsified ground with no marker on it. That is [ADR 0056](0056-the-one-row-object-refusal-was-a-claim-about-a-module-s-prose-population-and-it-expired-for-every-queued-row.md)'s arrangement, which superseded a paragraph of ADR 0052 as its own record.

## Measured before ruling, at `f4b868c`

**Every figure below was taken against a corpus outside this repo and against a recommendation-record root that twelve worktrees write with no lock. Nothing committed re-derives one, and they are stated here and in [the ruling comment](https://github.com/mshamblin5150-code/clinical-skills/issues/436) and nowhere else** — [#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms.

**The registry's fourth column is a partition and the 46 are its only unnamed family.**

| rows | `record` cell | which topics |
| ---: | --- | --- |
| 101 | `exact recommendation index available; full-document read pending` | 82 USPSTF, 19 AHA/ACC |
| 46 | `blocked on #436: bound recommendation records are incomplete` | 29 IDSA, 16 KDIGO, 1 GOLD |
| 18 | `no recommendation record; full-document read pending` | 3 ACIP, 11 IDSA, 1 GINA, 2 KDIGO, 1 CDC |
| 3 | `partial artifact; full-document read pending` | — |

169 rows, 168 `unread` plus one `sheet`. The three surviving strings name *an exact index*, *nothing*, and *a partial artifact*; the 46 are the entire `bound` family and no existing string is true of them. [ADR 0057](0057-the-corpus-sweep-is-comprehensive-and-every-ruling-it-needs-is-already-ruled.md) reached the same rows independently: *"46 rows of the registry carry `blocked on #436` for a block discharged on 2026-08-23 … nothing can fail on a retired reason."*

**Re-drafting the one shipped bound sheet rejects 345 of its 357 rows, and item 2 as written reaches 13 of them.**

```
diabetes.md seeded against recs-ada-2026.json (bound, 126 records):
  332  threshold_draft.py:249  "not in its recommendation record"   -- every one a narrative locator
   13  threshold_draft.py:253  "seeded snippet is not in its record"
         p45/2.23  p62/3.17  p183/8.29 x2  p228/10.13  p256/11.3
         p261/11.8 x2  p261/11.9 x2  p284/13.3  p336/15.23 x2
  ---
  345 rejected, 12 survive
```

ADR 0029 measured p261 alone and #436's *Done when* inherited that scope as though it were the sheet's total. **The containment figure is 13, not 4.**

**A 160-character backward window does not reach the recommendation it belongs to.** Four IDSA documents — `ciu617`, `ciaa1215`, `amr-guidance-update`, `ajrccm_200_7_e45` — 158 trailing-marker hits, read through `get_text("text")`, which is the reader `guidelines_recs.py` itself calls:

| distance from the sentence's start back to the marker | |
| --- | ---: |
| min | 13 |
| p25 | 132 |
| median | 226.5 |
| p75 | 284 |
| p90 | 431 |
| max | 936 |

| backward window | reaches the sentence start for |
| ---: | ---: |
| 160 | 30.4% |
| 200 | 44.9% |
| 260 | 66.5% |
| 320 | 84.2% |
| 400 | 89.9% |

The baseline finds the *nearest* preceding boundary, so it is a **lower bound** on the distance to the recommendation's start and the 30.4% is generous rather than harsh.

**Scanning back for a terminator plus whitespace plus a capital finds a boundary inside 320 for 141 of 158 (89.2%); 17 take the raw cap.** Whether the boundary found is the *right* one was sampled by eye and **not measured**. A first pass bucketed the remainder against a cruder baseline and reported a 43.7% false-stop rate; reading the samples showed most were clean sentence openers, so **the baseline was wrong rather than the rule under test**, and that figure is withdrawn rather than corrected.

**ADA's changelog is a shape, not a vocabulary.** All 98 records on pp.12-18, by the words following the reference:

```
was added 20 | was updated 16 | was revised 15 | was modified 13 | was amended 5
was changed 4 | was divided 2 | was clarified 2 | was broadened 1 | was enhanced 1     -> 79
states that 4 | discusses / dis cusses / briefly discusses 3 | describes 1
now provides 1 | now includes 1 | is now 1 | on treatment 1 | (no match) 4              -> 19
```

Every one of the 79 is `was` followed by a participle. ADR 0029's probe caught **53**. The record contains `dis cusses` and soft hyphens, so **the census is spacing-dependent**.

**Tier 2 is marker-gated even though it is not mode-gated.** `tools/threshold_sheet.py:1301` skips any snippet opening `RENDERED:`. 36 of `diabetes.md`'s 357 rows do, **2 of them `/recommendation/` locators**. So **321 rows were graded, not 357**, and a skipped row did not pass.

**The class check is not mode-guarded.** `tools/threshold_sheet.py:2268`'s `if mode == MODE_EXACT:` has exactly one statement in its body — the membership loop at `:2269`. The class check at `:2282` sits outside it and runs on a bound source; it can never fire because `guidelines_recs.py:354` writes `cor=None` on every marker record.

**`tools/guidelines_recs.py` states six ceilings in prose and holds no object.** `grep -c "NOT_REACHED\|DECLARED_LIMITS"` returns **0**. The six: the bound count is an over-report (`:34`), the strength stays out of `cor` (`:94`), what the curated limb does not reach (`:99`), `Superseded by` is unread (`:102`), eleven IDSA documents come back at nothing (`:108`), a marker is a marker wherever it is written (`:112`).

**One bound record exists in the recs root**, `recs-ada-2026.json`; the other seven are `exact`, and a `recs-sweep.json` from another worktree's in-flight [#510](https://github.com/mshamblin5150-code/clinical-skills/issues/510) work sits beside them. #438's *"the five bound records"* is not re-derivable here, and the root is shared and unlocked, so **its contents are a fact about one machine at one hour.**

## Ruled 2026-08-27

**1. The 46 registry cells take a fourth reason string, not one of the three that exist.**

`bound recommendation record available; full-document read pending`. The `record` column states **which kind of recommendation record a topic has**, and the partition above is exact. Reusing `exact recommendation index available` asserts the opposite of what `bound` means; reusing `no recommendation record` would make one string mean *no record* and *a bound record* at once and delete the distinction the column exists to draw. The topics stay `unread` — only the stated reason changes, as ADR 0029 point 8 requires.

**2. ADR 0029's marker prohibition binds the producer, not the column.**

`tools/threshold_draft.py` writes nothing into a bound row's `snippet`. [ADR 0043](0043-a-rendered-cell-is-a-page-transcription-and-its-marker-records-the-read-rather-than-an-extraction-failure.md) ruling 6's `RENDERED:` is a **different actor's claim at a different time** — a reader asserting they rendered and transcribed a page — and is untouched. The two have coexisted in the shipped tree since before ADR 0029; that record's rejection paragraph did not notice the 36 rows sitting under it.

**3. A blank snippet refusing structure is the mechanism, and it is declared rather than softened.**

`tools/threshold_sheet.py:967` refuses a row with no snippet. On a drafted bound sheet that fires on every row until the page read fills them, which is what makes ADR 0029 point 1's *snippets on a bound source are read off the page* mandatory rather than advisory. **#436 states it so a non-zero on a fresh scaffold is not read as breakage.**

**4. Tier 0's bound line names both denominators and derives every figure.**

```
CITATION tier 0 NOT RUN -- ada-2026 (source mode is 'bound': 357 row(s) ungraded here;
  25 cite a recommendation identifier and lose its membership pin, and their class
  cell is ungraded because a bound record carries no class; all 357 keep tier 1, and
  tier 2 grades all but the 36 that declare RENDERED: -- 2 of those 25)
```

`25` alone under-reports what the skip covers; `357` alone claims 332 rows lost a pin they never had, `narrative` being ADR 0026's reserved kind. Both, or a reader takes one for the other. **The class clause attributes the outcome to the record and not to a guard**, because the guard the spec described does not exist.

**5. The drafter skips both rejection limbs on a bound source, and the seam is by mode.**

`bound` → neither membership nor containment; `exact` → both, with `narrative` left to [#464](https://github.com/mshamblin5150-code/clinical-skills/issues/464). The membership skip is not new policy: ADR 0029 already rejected *requiring a bound row's `rec` to be present in its record* for `gate_coverage`, on the ground that a bound record **under**-reports so a real recommendation can legitimately be absent. `threshold_draft.py:249` is that identical rule in a second function. Repairing one and not the other leaves a rejected ruling live where the drafter can still act on it.

It does not collide with #464. That ticket's ADR 0026 ruling 2 governs what a middle segment must mean **on an exact source**; on a bound source the membership question is already void.

**6. The changelog qualifier lands on the README's bound row, and `diabetes.md` is untouched.**

`reference/thresholds/README.md:225` tells a reader a bound record can **under**-report and says nothing about the other direction, so `4,618` reads as 4,618 recommendations. The over-report clause exists only at `guidelines_recs.py:35`, which nobody consulting the coverage table opens. The qualifier states the shape generally, names ADA as the measured instance, and **points at `diabetes.md` rather than copying its accounting**, which that sheet already carries at `:29` more precisely than #436's *"roughly 28"*.

**#436 item 5's `1 ADA | 126` row has never existed** — `git log -S` is empty for it. The `1 ADA` is one fragment of a composite cell over 48 documents; the `126` belongs to a different artifact.

**7. Whichever of #436 and #438 lands first builds `guidelines_recs.DECLARED_LIMITS` whole; the other appends.**

Neither ships a one-row version, and **both rows are unconditional** — never *a row if the object exists, prose if not*, which is ADR 0056 ruling 2's declined accommodation and makes one specification produce two trees. *Build-if-absent, append-if-present* produces the same tree either way. Two branches writing the tuple conflict rather than merging silently, which is [#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180)'s safe direction.

**The population is the six ceilings the docstring already states, each as [ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md) ruling 8's `key` / `limit` / `evidence` shape, and the object declares that as a floor.** ADR 0053 built `research_ledger.DECLARED_LIMITS` by reading the module end to end and found thirty-six limits against the five its prose claimed. Requiring that here turns a ruled ticket into an open-ended audit; taking the six silently would publish the over-claim ADR 0053 was filed to correct. **The end-to-end derivation is its own ticket.**

**8. An undeclared marker anchor fails at definition time and at run time, and a test pins both.**

`TEXT_MARKERS` entries carry `anchor` as a **required positional**, so a fifth marker written the old way is a `TypeError` when the module is defined and cannot be papered over; the value is validated against a declared set. `read_marker_recommendations` **dispatches with no reading `else`** — leading and trailing are two named branches and anything else raises. *"Never a default"* is a statement about the code's shape: `if trailing: … else: forward` is a default wearing a conditional.

The blast radius is stated rather than discovered: `tools/threshold_sheet.py:230` imports this module, so a malformed marker refuses every commit through the pre-commit hook. That is correct for a code defect and the suite goes red in the same breath.

A test-only walk was declined. It is the right instrument where a property **cannot** be made structural — `test_console_codec.py`'s and `test_ls_files_coverage.py`'s AST walks each declare a floor on the shapes they recognize — and a required constructor argument has no floor to declare.

**9. The census keys on a shape, is fixed at the sub-reference anchor, and is declared a figure #446 moves.**

`Recommendation <ref> was <participle>` reaches 79 of ADA's 98 against the probe's 53, and **has no vocabulary to keep**. That answers ADR 0029's own objection — *the verb vocabulary is open* — better than the record did: a list answers it by going stale, a shape answers it by having nothing to enumerate. It stays a declared floor because `states that`, `discusses`, `describes` and `now includes` sit outside it, and the declaration names the shape it holds rather than the words it does not.

The `11.8a` sub-reference miss ADR 0029 catalogued is an **anchor defect, not a vocabulary gap**, and is repaired.

**#436 declares the census as spacing-dependent.** The ticket declares the 83% mid-word rate and the median-5-character backoff as figures [#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) moves, and says *"the 44.5% marker-anchor split is spacing-independent."* That is true of the split and **false of the census**: `dis cusses` is in the shipped record and rerouting through `rebuild_text` repairs exactly that. It composes in the helpful direction, as the backoff does, and must be named or the next re-derivation reads a moved number as a regression.

Placement: a per-document integer in the record's existing `totals`, printed per document in the run summary, **never a gate**. It is additive and does not disturb #438's producer stamp.

**10. Two window constants, not one, and the backward value comes from a measurement.**

ADR 0029 measured the window **forward** and validated the backward **direction**; it never measured the backward **distance**. One constant makes 160 the answer to a question nobody asked, and on the sample above a trailing label at 160 starts mid-sentence about seven times in ten. The forward defect was reading into the *next* recommendation; a backward 160 drops the front of the *right* one — and the front is the identifying clause, `We recommend X in patients with Y`, which is the one thing a label exists to carry.

This repo has ruled the general form already, on `filled_vitals_census`'s block boundaries: **the safe direction of a rule is a property of the rule and not of the pair it belongs to, so a boundary is not the mirror of its twin.** One constant is the symmetry assumption wearing a name.

**The build measures across every trailing-marker document and takes a value on a plateau, not at an edge** — `SPACE_ADVANCE_FRACTION`'s recorded failure is that #83 named a value at an edge and picked the one setting worse than not changing anything. Four documents establish only that the value is **materially above 160**; where the plateau sits is the build's to measure and the constant's own docstring to state.

**This is not the widening ADR 0029 rejected, and #436 says so in as many words.** That rejection was of *widening the window so a record carries its numbers*, which edges toward a second prose-derived record family and is foreclosed by ADR 0026 ruling 8. This widens one direction so a **label begins at its own recommendation**, which is ADR 0029 point 1's stated purpose for the text.

**11. The backward read stops at the nearest preceding sentence boundary, with the window as a cap.**

Widening backward with no stop means a label opens with the **previous** recommendation's tail — the original defect rotated 180°, and the outcome a sweep would file within the week. ADR 0029's rejection of *ending a label at a sentence terminator* was measured on the forward **end**, where a terminator buys little over 160 and needs a second rule for the 13.8% that have none. Backward it is not deciding where the label ends; it is the only thing keeping the label from starting inside its neighbor. Same mechanism, different question — ruling 10's precedent again.

**The rule is declared a floor, not asserted correct.** A terminator followed by whitespace and a capital rejects `1.73 m2` and `1.5 mg`; it does not reject `e.g. Streptococcus` or a citation marker. The build measures the false-stop rate against every trailing-marker document and declares it beside the constant. **A stop with no boundary found takes the cap**, which is the pre-existing behavior and is why the cap is still needed.

## What ADR 0029 said that this supersedes

| paragraph | what falsified it |
| --- | --- |
| Point 8 — the 46 cells are corrected *"to the reason the other 122 rows use"* | There are three such reasons and none is true of a bound source. Ruling 1. |
| *"`gate_coverage`'s membership refusal **and the class check** are both guarded by `if mode == MODE_EXACT`"* | Only the membership refusal is. The class cell is ungraded because the record carries no class. Ruling 4. |
| *"Its `## Scope` declares tier 2 resolved … so all 357 rows were graded on the page and passed"* | Tier 2 is marker-gated. **321 were graded**, 36 skipped, 2 of them recommendation locators. Ruling 4. |
| *"All four of `diabetes.md`'s p261 snippets fail `_normalize` containment"* — true, and inherited into #436's *Done when* as the sheet's total | **13 rows fail containment**, and 332 more fail membership, which item 2 as written never reached. Ruling 5. |
| Point 4 — *"the 160 becomes a named constant"*, singular, on evidence taken entirely forward | The backward distance was never measured and 160 reaches the sentence start for 30.4%. Rulings 10 and 11. |
| The rejection of *ending a label at a sentence terminator* | Scoped to the forward end. Backward it is a different question and the answer reverses. Ruling 11. |
| Point 9 — *"Both #446 and #438 carry `grilling` and neither is ruled"* | Both are `bug, ready-for-agent`; #446 is ruled by [ADR 0032](0032-the-marker-limb-reads-the-repaired-text-the-other-two-limbs-declare-that-they-do-not-and-every-citation-gate-reads-one-reader.md) and #438 by [ADR 0030](0030-a-recommendation-record-is-owned-like-every-other-artifact-its-trust-floor-is-keyed-on-the-limb-that-built-it-and-the-drafter-takes-no-escape-hatch.md). **The conclusion survives on the three-functions ground and the ground does not.** |
| Declared limit — *"a fifth marker arrives with no anchor declared, and the build must make that a failure"* | Narrowed rather than reversed: it names no site, and the three candidate sites produce different trees. Ruling 8. |

**What is not superseded is every ruling ADR 0029 made about what a bound label *is*.** Points 1, 2, 3, 5 and 6 stand as written, and this record is an extension of them rather than a reversal — the label reads from its marker's end, and rulings 10 and 11 are about how far, which 0029 did not ask.

## What was rejected

- **One reason string across all 168 unread rows.** It discards what three strings currently encode about record kind, and it is a larger edit than the ticket it would arrive in.
- **Reading ADR 0029's marker prohibition as a rule about the `snippet` column.** It contradicts ADR 0043 ruling 6 and invalidates 36 rows already shipped.
- **Seeding the label and marking it so a drafted scaffold passes structure.** It resurrects the marker convention ADR 0029 rejected, and it makes a label look like a citation at exactly the moment a reader is deciding whether to go and look.
- **Skipping containment only and filing the 332 as a blocker on #464.** Honest about ownership and it makes the ticket's own *Done when* unreachable — you cannot re-draft the sheet — which is the defect this whole grilling was about.
- **Designating #438 the builder of the limits object.** It makes a ruled ticket's buildability depend on an unrelated one shipping first, which ADR 0029 point 9 refused.
- **Deriving `guidelines_recs`' limit population end to end here.** ADR 0053-scale work; neither #436 nor #438 is scoped for it, and folding it in is how a ready-for-agent ticket stops being one.
- **A test-only anchor check.** The property is structural and a required argument has no floor to declare.
- **An enumerated editorial-verb list.** It goes stale against an open vocabulary; a shape has nothing to enumerate.
- **One window constant at 160 with the truncation declared.** Cheaper and honest, and it ships a label that omits what is being recommended.
- **Taking the full backward window with no boundary stop.** The grade parenthetical still anchors *which* recommendation the label is for, so identification survives — but the label opens with a neighbor's text, which is this ticket's own subject.
- **An addendum on ADR 0029.** Right where the original's reasoning stands and only its scope moves. Here its evidence base moves: a forward-only window measurement cannot support a rule that reads both ways.

## Declared limits

**`CONTEXT.md:315` is corrected by the build and not by this record.** The term **Recommendation label** reads *"a fixed-length window of the page around the marker"*, which rulings 10 and 11 falsify — two lengths and a boundary stop. The glossary states what the code does, so correcting it today publishes a definition the tree does not satisfy. **The ADR carries the wording the build installs and a test binds the two**, so the edit can neither be forgotten nor land early.

**The backward figures are four documents, not the corpus.** 30 IDSA files carry these markers, plus the GOLD and USPSTF strays. What is established is the *direction* of the error and that 160 is materially too small; every constant is the build's to measure.

**Whether a boundary the backward stop finds is the right one is unmeasured.** It was sampled by eye. The false-stop rate is the build's to measure and to declare beside the constant.

**Nothing here reaches whether a label identifies the right recommendation.** Ruling 10 makes it likelier by starting the label at its own sentence; no gate compares a label to the recommendation it names, and none is proposed. **A correctly anchored label is still not a checked one.**

**The census counts a shape and can only ever be a floor.** A society whose changelog is written in a form outside `was` + participle arrives silently, exactly as ADA did.

## Corrected in place, 2026-08-27, by this record's own tracker sweep

Six agents swept all 59 open tickets the evening this record merged. Under
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md),
facts are corrected above and **the deciding paragraphs are untouched** — so the two items below that
would change a ruling are recorded here and left for the clinician rather than edited into the rulings.

**Facts corrected above.** Ruling 5 and the evidence block cited the containment limb at
`threshold_draft.py:252`; `:252` builds `record_text` and the **test** is `:253`. That anchor was
inherited from #436's original body and carried into this record unchecked. The `## Measured` list
cited the over-report ceiling at `:35` and the `cor` ceiling at `:96`; both are mid-sentence and the
claims open at `:34` and `:94`. `ADR 0026 rule 8` is now `ruling 8`, matching this record's other
citation of the same plainly-numbered record.

**Ruling 7's claimant population is two and the tree holds four.** `guidelines_recs.DECLARED_LIMITS`
is specified by [#436](https://github.com/mshamblin5150-code/clinical-skills/issues/436) item 1,
[#438](https://github.com/mshamblin5150-code/clinical-skills/issues/438) done-when 6,
[#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) deliverable 2 —
*"a named object in `tools/guidelines_recs.py` states which limbs skip the space reconstruction"* —
and [#510](https://github.com/mshamblin5150-code/clinical-skills/issues/510) item 7. All four are
open; #446 and #510 are `ready-for-agent` and neither is named by ruling 7. **A builder on either
one, following its own body to the letter, ships the single-row object ruling 7 refuses while
breaking no instruction it was given** — which is the failure ruling 7 exists to prevent, reproduced
by ruling 7's own scope.

**And #510 item 7 fixes a different row shape**, deliberately and with a stated reason: *"The shape
is `case_study_scan.DECLARED_LIMITS`'s — a tuple of `(text, disposition)` pairs — and not
`reference_scan.NOT_REACHED`'s `(name, prose)`."* Ruling 7 fixes ADR 0053 ruling 8's three-field
`key` / `limit` / `evidence`. **Two ratified-or-specified shapes for one tuple is a decision rather
than a fact**, so nothing here overrides #510; it is recorded and put to the clinician.

**The sequencing conclusion is contradicted by a ratified record this session did not read.**
[ADR 0032](0032-the-marker-limb-reads-the-repaired-text-the-other-two-limbs-declare-that-they-do-not-and-every-citation-gate-reads-one-reader.md)
ruling 4 is titled *"this lands before #438 and #436"* and rules **Order: #446, then #438, then
#436**, on measurement validity rather than merge cost: *"#436, whose headline figure — the 83.0%
mid-word cut rate — was measured on damaged text. Grilling it after this lands measures the text that
will exist rather than the text being replaced."* ADR 0032 is dated 2026-08-25 and ADR 0029 2026-08-24,
so **ADR 0029 point 9 was already superseded when this record restated it**, and the supersession
table's row — *"the conclusion survives on the three-functions ground and the ground does not"* — is
wrong about the conclusion. This record cited ADR 0032 in that very row, as the record ruling #446,
without reading the ruling that contradicts it.

**Ruling 10 makes that ordering more necessary rather than less, which is the part ADR 0032 could not
have weighed.** Its Consequences analysed #436's exposure and concluded *"#436's two measurements move
in the helpful direction"* — true of the mid-word rate and the backoff, both of which are **declared
figures**. Ruling 10 introduces a **committed constant**: a backward window taken on a plateau. #446
moves character distances in **both** directions — a glued run gains spaces and grows, `dis cusses`
and a soft hyphen collapse and shrink — so the plateau can move either way and a constant measured
before #446 can land on the wrong side of it with nothing failing.

**Not resolved here.** By recency and by
[ADR 0037](0037-a-contested-glossary-term-goes-to-the-higher-adr-number.md)'s higher-number rule this
record would govern; by substance ADR 0032 ruling 4 is right and this record restated a retired
conclusion without knowing it existed. **A ruling made in ignorance of a contrary ratified ruling is
not a considered reversal**, so the ordering goes back to the clinician rather than being decided by
a tie-break neither record was written against.

## Addendum, 2026-08-28 — the ordering, ruled by the clinician

**Order: #446, then #438, then #436.** [ADR 0032](0032-the-marker-limb-reads-the-repaired-text-the-other-two-limbs-declare-that-they-do-not-and-every-citation-gate-reads-one-reader.md)
ruling 4 stands and this record's restatement of ADR 0029 point 9 is **retired**. The corrections
section above put the question to the clinician rather than resolving it by the higher-number
tie-break; this is the answer, and it goes here rather than into ruling 10 or the supersession table,
which stay as they were written under
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md).

**What it costs this record is one deliverable's timing and nothing else.** Rulings 1 through 9 and 11
are unaffected — the label direction, the word backoff, the sentence-boundary stop, the drafter's
mode seam, the registry string, the census shape and the tier-0 line are all independent of what the
extractor feeds the marker limb. **Ruling 10 is the one that moves**: the backward window's plateau is
measured **after #446 lands**, against the text that will exist, and the constant committed from that
measurement. Measuring it earlier is the defect ADR 0032 ruling 4 named — a figure taken against the
text being replaced — with the aggravation this record added, that ruling 10 commits a constant where
ADR 0032 weighed only declared figures.

**And it makes the row-shape question urgent rather than academic.** Ruling 7 says the object is built
whole by whichever ticket lands first. Under this ordering that is determinate: **#446 builds
`guidelines_recs.DECLARED_LIMITS`**, and #438, #436 and #510 append. But #446 deliverable 2 names
`reference_scan.NOT_REACHED` as its precedent, which is **#510's `(name, prose)` side of the split and
not ruling 7's ADR 0053 ruling 8 three-field row**. So the ticket that now builds the object is
specified with the shape ruling 7 did not choose, and the disagreement is the first thing its builder
meets rather than a late reconciliation. Still the clinician's, and still not decided here.

## Second addendum, 2026-08-28 — the row shape and the registry's owner, ruled by the clinician

*Corrected in place 2026-08-30 under ADR 0075 ruling 3: this addendum continues the record's
ruling sequence at 12 rather than restarting it; the ruling text is unchanged.*

**12. The row is three-field.** `guidelines_recs.DECLARED_LIMITS` takes
[ADR 0053](0053-a-declared-limit-is-a-keyed-sentence-and-its-reasoning-stays-at-the-code-point.md)
ruling 8's `key` / `limit` / `evidence` shape, so ruling 7 stands unqualified and the two tickets
specified against it are corrected rather than accommodated:
[#446](https://github.com/mshamblin5150-code/clinical-skills/issues/446) deliverable 2, which names
`reference_scan.NOT_REACHED` as its precedent, and
[#510](https://github.com/mshamblin5150-code/clinical-skills/issues/510) item 7, which names
`case_study_scan.DECLARED_LIMITS`'s `(text, disposition)` pairs.

**#510 item 7's stated reason is answered rather than overridden.** It chose its shape *"because the
tree holds both and #535 is open on which counts as one"* — a deliberate move to stop the item being
a reasonable-choice fork. That reason was sound when written and is now spent: the fork is closed by
a ruling rather than by a ticket's guess, which is what item 7 wanted. **The `NOT_REACHED` name may
still be exported as a derived view** — ADR 0053 ruling 8 governs the row, not what a module exposes
beside it, and `case_study_scan` already publishes both.

**Under the first addendum's ordering this is not academic.** #446 lands first and therefore builds
the object whole, so the shape is the first thing its builder meets. Correcting deliverable 2 is what
makes the ordering safe rather than merely settled.

**13. The 46 registry cells are [#582](https://github.com/mshamblin5150-code/clinical-skills/issues/582)'s.**
Ruling 1 fixed the *string* and said nothing about the owner; #436's own 2026-08-27 sweep comment had
ruled #582 and its respec kept item 4 without recording a reason, leaving two open tickets specifying
one 46-line edit. **Item 4 and its `Done when` bullet are struck in favor of #582**, and ruling 1's
string is unchanged.

**The ordering is what makes the ownership matter.** #436 is now third of three, so an edit left there
keeps 46 topics telling the next agent they are blocked on a block discharged 2026-08-23 through two
further builds — while #582 is 46 lines of Markdown with no code, no rebuild and no recs-root
dependency.

**What #582 carries that ruling 1 did not reach**, and which is why it is the better home rather than
merely the earlier one: `tools/threshold_coverage.py:91` grades that cell for non-emptiness only,
which is *why nothing caught it*; and `coverage.md:78` — the `diabetes mellitus` **`sheet`** row — is
the 47th `#436` reference and must not be swept, because it is not a blocker claim, it stays true
after the build, and *full-document read pending* would be false of a `sheet` row.
