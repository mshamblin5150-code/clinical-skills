# A directed over-the-counter agent is drug management, and modifier 25 joins the committed CPT sheet

[#1417](https://github.com/mshamblin5150-code/clinical-skills/issues/1417) was filed from the
after-action review of a `batch-shift` run, after four coding misses that no sentence
of `icd10-cpt` addressed: directed over-the-counter agents graded outside prescription drug
management, modifier 25 left off a same-day `96372`, `E11.9` plus `G62.9` where `E11.42` applies
with no `Z79.01` beside a continued anticoagulant, and proposed tests counted toward the data
element. A later shift's after-action review added a modifier-25 send-back. Grilled
2026-10-08 against `main` at `aae64b0390e32cefdfa70794eb3808be12265b59`, where the freshness gate
read `FRESH`; the clinician ruled every point below in that session. **Nothing is built here; this
is the record the build reads.**

## Measured before ruling

**The over-the-counter ruling existed only in private memory.** On 2026-09-17 the clinician said of
over-the-counter agents, *"I always give them a prescription for it."* No tracked file carried that
sentence. `reference/cpt-em-mdm-2026.md` names "Prescription drug management" as a risk example and
says nothing about over-the-counter agents.

**The modifier-25 page had been read and was never committed.** Two private worksheets from earlier
shifts record a rendered read of CPT Professional 2026 Appendix A. No
tracked file holds that text, so [ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md)
ruling 3 sends every same-day procedure back to a live book read.

**The alphabetic index ships and traces `with` links directly.** Since
[ADR 0248](0248-the-index-tables-ship-and-an-index-path-carries-only-a-code-s-stem.md),
`python tools/icd10_lookup.py --index polyneuropathy` prints
`Diabetes, diabetic (mellitus) (sugar) > type 2 > with > polyneuropathy -> code E11.42`, and
`--index "chronic kidney disease"` prints the `E11.22` path the same way. During the grilling the
question put to the clinician said the database lacked the index; that premise was false, and the
ruling below is written against the measured tree.

**The code set already asks for some long-term-drug codes.** Under `E11`, the tabular's own
instruction reads "use additional code to identify control using" `Z79.4`, `Z79.84` and `Z79.85`.
The `Z79` family holds 35 codes, including the catch-all `Z79.899`.

**The note writes skill-proposed orders as Plan orders.** `clinical-note` writes an order the givens
call for into the Plan and records it under `FILLED·proposed`. A recommendation left for the
preceptor is a separate, future-tense line. The MDM sheet counts "Ordering of each unique test" and
cannot tell whose order a Plan line is.

## Ruling 1 — a directed over-the-counter agent is prescription drug management

Where the Plan directs an over-the-counter agent with a dose and directions, the risk element counts
it as prescription drug management, because the clinician writes a prescription for every agent he
directs. A Plan line that names an over-the-counter option without a dose and directions, such as
*may use acetaminophen or ibuprofen as needed*, is general advice and does not count. Never grade
risk low on the ground that a directed agent needs no prescription.

This ruling reaches agents the clinician directs. How a drug the skill itself proposes counts toward
risk is not decided here.

## Ruling 2 — `clinical-note` writes every directed over-the-counter agent with its dose and directions

So that ruling 1 never turns on how loosely a note was drafted, `clinical-note` writes each
over-the-counter agent the clinician's shorthand directs as he would write its prescription: agent,
dose, route, frequency and duration where one applies. A dose or sig the shorthand omits is filled
under the skill's existing filled-content rules and marked as filled. The build checks every worked
Plan example in `clinical-note` against this rule.

## Ruling 3 — modifier 25 is read once into the committed CPT sheet and applied from it

The CPT Professional 2026 Appendix A modifier-25 entry, printed page 969, joins
`reference/cpt-em-mdm-2026.md` under ADR 0251 ruling 5's procedure: a first reader transcribes it
from the rendered page, a blind second reader transcribes it independently, and
`tools/cpt_mdm_sheet.py` grades their exact agreement. `cpt_mdm_sheet.py` is extended to read and
grade that entry. Once it passes, a worksheet applies `-25` from the committed entry, as it applies
the MDM grid, and no live read is needed. Same-day modifier 25 leaves the list of guidance the sheet
does not hold, both in `icd10-cpt` step 5 and in `clinical-note`'s coding-worksheet requirement.

Until that entry merges, ADR 0251 ruling 3 governs unchanged, with one clarification: a pending E/M
line waits for the read and never drops `-25`. Pending is not omission.

## Ruling 4 — the ICD-10-CM `with` convention is a general rule

Where a code-set entry links two documented conditions by `with`, the link is presumed and the
combination code is used unless the note states that the conditions are unrelated. The worksheet
traces each documented condition through `python tools/icd10_lookup.py --index <term>` and through
`--find` over descriptors, and takes a `with` path whose subterm is another documented condition.
The skill gives type 2 diabetes with polyneuropathy (`E11.42`, not `E11.9` plus `G62.9`) and
hypertension with heart disease or chronic kidney disease (`I11.-`, `I12.-`) as worked examples. The
guideline sentence is cited from a committed source reading of the Official Guidelines edition that
applies to the service date, on ADR 0248's precedent; `--index` is an exact-term trace, so a
condition written in words the index does not use is a limit the skill states.

## Ruling 5 — every medication in a class with its own long-term-use code gets that code

A medication the patient takes long term and that falls in a `Z79` class with its own specific code
gets that code, anchored to the medication line. That includes anticoagulants (`Z79.01`),
antiplatelets, aspirin, insulin, oral hypoglycemics, inhaled and systemic steroids, opiate
analgesics, NSAIDs and the other named classes, and it covers the diabetes control codes the tabular
already requests. The catch-all `Z79.899` is never proposed.

*Superseded 2026-10-08.* **The reach of "A medication the patient takes long term" to a medication
the writer filled is superseded by
[ADR 0297](0297-a-history-condition-is-coded-only-where-it-affected-this-visit-and-a-filled-medication-never-vouches-for-it.md)
ruling 3 and is left as written.** A filled drug earns its long-term-use code only where filled
reasoning changes something concrete in this visit. A drug named in the shorthand is unchanged, as
are the classes, the diabetes control codes and the refusal of `Z79.899`.

## Ruling 6 — a drug started at this visit for ongoing use counts, and a short course never does

Ruling 5 reaches a drug the patient arrived on and a drug started at this visit for ongoing use,
meaning a chronic condition or no stated end. A short course never counts: an antibiotic for a fixed
number of days, a steroid burst, an as-needed drug for an acute problem. Where the Plan leaves the
duration unclear, the code is proposed with a `needs:` specificity flag naming the missing duration.
The guideline wording that grounds the long-term-use reading is cited from a committed source reading
of the applicable Official Guidelines edition, not from recall.

## Ruling 7 — a skill-proposed order counts toward data, and the E/M line is marked when the level rests on it

A test the clinician's shorthand orders, results or reviews counts toward the data element. A test
the skill proposed that the note writes as a Plan order also counts. When the level depends on
skill-proposed orders, meaning re-deriving two of three elements without them gives a lower level,
the E/M line carries a filled mark naming the element and those tests, on the same principle as
`SOURCE: filled` on a diagnosis code. A recommendation left for the preceptor to rule on never
counts.

## Ruling 8 — skill prose names sheet entries and never restates them

`icd10-cpt` states how to read the clinician's notes against the committed sheet: which lines count,
whose they are and what is marked. For every CPT definition it names the sheet entry and does not
restate its wording. The ticket's draft paragraph restating the sheet's data definitions is
therefore not adopted; rulings 1 and 7 are the text that replaces it.

## Consequences

- `skills/icd10-cpt/SKILL.md` gains rulings 1 and 3 through 8; `skills/clinical-note/SKILL.md`
  gains ruling 2 and drops same-day modifier 25 from its list of guidance the sheet lacks once
  ruling 3's entry merges.
- `reference/cpt-em-mdm-2026.md` and `tools/cpt_mdm_sheet.py` gain the modifier-25 entry and its
  grading, through one two-reader VitalSource session.
- Committed source readings of the `with` convention and the long-term-use guideline are recorded
  before the skill cites them.
- The #1417 *Done when* worksheet carries `-25` beside a same-day procedure, `E11.42` for documented
  type 2 diabetes with polyneuropathy, `Z79.01` for a long-term anticoagulant, and a filled mark
  where the level rests on proposed tests.

## What none of this reaches

Whether a modifier-25 encounter's E/M work is significant and separately identifiable remains a
reading of the note; the committed entry states the rule, not the verdict. Whether a drug is
intended long term remains a reading of the Plan; ruling 6's `needs:` flag surfaces doubt and does
not resolve it. How a skill-proposed drug counts toward risk is outside ruling 1.

## Supersedes

- [ADR 0251](0251-the-cpt-mdm-table-is-a-committed-two-reader-sheet-and-the-cpt-edition-is-judged-by-service-date.md)
  ruling 3, its listing of "modifier 25 on a same-day procedure" among the guidance that keeps the
  line pending. That limb leaves the list once ruling 3's committed entry merges; the out-of-edition
  case, total time, critical care and prolonged services stay book-only.
