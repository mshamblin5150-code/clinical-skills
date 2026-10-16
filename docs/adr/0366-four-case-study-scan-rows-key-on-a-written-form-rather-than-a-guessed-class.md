# Four case study scan rows key on a written form rather than a guessed class

**Measured at:** 1b66dd9054ab84f3d517d4c00ea11be573d17b52

*Re-declared from `8276712c` on 2026-10-16 after a rebase. Between the two bases only ADR 0365 and
the `CONTEXT.md` **Titled copy** entry changed; neither touches `case_study_scan`,
`research_ledger`, `style.md` section 8 or the skill's cross-reference rule, so the measurements
below stand.*

[#1579](https://github.com/mshamblin5150-code/clinical-skills/issues/1579) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4). Readers caught four
prescription and cross-reference defects round after round, and the ticket proposed a
`tools/case_study_scan.py` row for each. Grilled 2026-10-16 against `main`; the clinician ruled
every point below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Each candidate was run over the clinician's finished case-study drafts before it was put to
the clinician**, through the scanner's own section reader and `research_ledger`'s prescription
reader, printing counts only. Those drafts live under `output/` and are written about a patient,
so no committed file re-derives the counts and none is stated here. What the census decided is
stated beside each ruling as a shape, because a shape is what the build can test against.

**Three of the ticket's proposed forms failed on correct finished work.** Keying a maintenance
order on a reassessment endpoint flagged an IV antibiotic reassessed daily during an admission and
an as-needed fever reducer stopped when afebrile, both correctly written `Refill: none`. Comparing
an as-needed order's interval with its daily maximum in both directions flagged a correct order
capping a drug at three doses on a six-hour interval. Matching a dosed Plan item's leading token
failed on items opening with an order verb and flagged a dose quoted inside a cited guideline
sentence about a drug the Plan had not started.

**One spelling the scanner treats as unnamed is named.** A pointer whose section name is set in
italics and followed by a colon reads as a bare `item N` to `UNNAMED_CROSS_REFERENCE`, because
`CROSS_REFERENCE_PATTERNS` requires the section words directly beside the number.

**The recorded defects were read in the review's extract**, so each ruling's planted control is
the shape a reader actually caught rather than one invented here.

## Ruling 1 — a labeled home medication carries the house maintenance refill count

A drug row declaring `Continued home medication:` whose order is not as-needed, not IV or IM, and
not a one-time dose must read exactly `Refill: 3`; any other refill cell is a finding, including a
spelled-out `Refill: three`. The label is the classifier, on
[#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289)'s ground that a drug-row
declaration is stated and never inferred, and the row reads the same label `research_ledger`
already reads. An unlabeled drug the run started stays with the Rx reader. Keying on
[ADR 0362](0362-a-case-study-s-routing-walk-is-a-written-record-and-a-red-flag-exception-goes-to-the-clinician.md)
Ruling 3's reassessment split was declined because its endpoint words also close correct admission,
IV and as-needed orders. ADR 0362 Ruling 3's decline of a mechanical supply check does not reach
this row, which reads one cell and does no supply arithmetic.

## Ruling 2 — no reverse refill row is built under this ticket

The sibling sentence in `style.md` section 8, that acute, one-time and IV drugs take
`Refill: none`, gets no row here. No reader round has recorded that defect, and a row with no
recorded failure behind it is a guess at what will go wrong. A recorded instance makes it a
one-line addition beside Ruling 1's row.

## Ruling 3 — an as-needed order's count-unit maximum must be reachable

An as-needed order whose drug row or `Sig:` states a per-dose amount, a minimum interval and a daily
maximum in doses, or in tablets or capsules with a per-dose tablet count, is a finding when that
maximum exceeds what the shortest stated interval allows in 24 hours. A maximum below what the
interval allows is a correct cap and never fires. A milligram maximum is not graded, because a
safety ceiling such as one stated across all sources can correctly sit above what one order gives;
the build declares that in `DECLARED_LIMITS`. The row is internal arithmetic on the order and
leaves whether the dose is correct to the reader, inside #289's prohibition.

## Ruling 4 — two daily limits side by side stay a reading

The recorded instance was a label ceiling beside a clinical stop rule in the Patient Education
section, telling the patient to call after two doses. The two do not contradict arithmetically,
and choosing which one the patient is told is a wording judgment. No row is built, and the build
adds a `DECLARED_LIMITS` entry naming the shape as a `declared-reading`.

## Ruling 5 — a bare cross-reference is a finding

A bare `item N` or `entry N` pointer is a finding rather than a count, enforcing the
`skills/practicum-case-study/SKILL.md` rule that a cross-reference names its section. The named
patterns widen so a section name set in italics or bold, or followed by a colon, still counts as
named. The declared limit that an unnamed cross-reference is never resolved stays true: the shape
is refused rather than resolved. A Plan item pointing at another Plan item writes `Plan item N`.

## Ruling 6 — a Plan order with no prescription table is a finding

A sentence in the Plan carrying a dose with its unit (percent counts), a route word and a frequency
or one-dose word is an order. Such a sentence is a finding when none of the five words before the
dose names a drug that a prescription table's drug row names. The route words are a closed
vocabulary of routes, not of drugs, so
[#300](https://github.com/mshamblin5150-code/clinical-skills/issues/300)'s refusal of a drug
vocabulary stands. A mention, a withheld drug and a dose quoted in a cited sentence carry no route
and frequency together and do not fire. A full order written as reasoning for a contraindicated
drug fires; `style.md` section 8 already places that decision in the Plan and the MDM as
reasoning, so the remedy is to state the decision without writing the order. A drug named by brand
in the Plan and by generic name in its table fires, and the build declares that limit.

## Ruling 7 — a `PROPOSED` entry excuses no table

The row reads the draft alone. A contingency drug dosed in the Plan takes the `Delayed order:`
table `style.md` section 8 already prescribes, or the dose leaves the Plan. A `PROPOSED` entry
describes an open question rather than the order's shape, and every open question is settled
before the go-ahead, so a finding on an unsettled dose clears when it should. Reading the
`proposed-<date>.md` file was declined: a second input, and a stale entry would let a dosed order
ship with no table.

## Ruling 8 — each row is believed on a planted recorded shape and a real correct order

Each of Rulings 1, 3, 5 and 6 is tested on a planted copy of the defect a reader recorded: a
labeled home medication with its refills cut; two tablets every six hours under a ten-tablet
ceiling; a bare `item 12`; and a conditional cream order with no table. Each is also tested on a
correct control taken from real finished text: a three-dose cap on a six-hour interval, the
withheld aspirin quoted in a cited sentence, and the italic named pointer. Every row also runs
clean over the shapes `style.md` publishes. At build time a counts-only census over the finished
drafts is reported in the pull request and never committed as a figure. This is the extractor
coverage rule's population, extraction and liveness evidence; the planted shapes are retyped
rather than real bytes, which is the declared ceiling of the controls.
