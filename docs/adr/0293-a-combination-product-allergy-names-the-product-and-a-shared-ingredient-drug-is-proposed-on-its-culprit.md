# A combination-product allergy names the product and a shared-ingredient drug is proposed on its culprit

Ticket [#1418](https://github.com/mshamblin5150-code/clinical-skills/issues/1418) was filed from
the after-action review of a batch-shift run and records two `clinical-note` framing
defects. Several notes wrote the clinician's own given orders with a `preceptor to rule` tag,
although the preceptor had agreed to them. Separately, an allergy stated to a combination product
whose culprit ingredient the shorthand did not name was guessed at: the pass barred every
ingredient, coded a class-specific allergy status, and removed a first-line drug from the Plan. The
encounter established none of those three things. The clinician ruled both in a grilling on
2026-10-08.

The first defect sits beside
[#1445](https://github.com/mshamblin5150-code/clinical-skills/issues/1445), which records the
clinician's ruling that a note never asks the preceptor to rule on, confirm, weigh, or accept
anything. That ruling already retires the ticket's proposal to reserve `preceptor to rule` for the
note's own proposals and objections. What it does not say is how the given order itself is written.

The second defect falls between two existing rules in `skills/clinical-note/SKILL.md`. A stated
allergen is never dropped and never overwritten, and an inference may tighten a prescribing
decision but never be what makes it safe. A combination product with an unknown culprit is a case
where either guess, *this ingredient is not the culprit* or *every ingredient is*, changes the Plan
and the code population on a fact the encounter does not hold. The examples below use a made-up
allergy to Vicodin, which combines hydrocodone with acetaminophen.

## Ruling 1 — a given order is written plain, as placed, with no preceptor on the order line

An order the clinician gave is written as placed: `Ceftriaxone 1 g IM once, given`. The preceptor
never appears on an order line, whether or not the shorthand records a review with the preceptor.

Writing every given order as *ordered after review with the preceptor* was declined because most
lines would state a review the shorthand never recorded. Naming the review only where the shorthand
records it was also declined in favor of one plain form. The ticket's reservation of
`preceptor to rule` for the note's own proposals and objections was already retired by #1445's
ruling. This ruling is built with #1445 because both rewrite the same paragraph, *A given order is a
given*.

## Ruling 2 — a drug the note proposes that shares an ingredient is proposed conditionally on the culprit

Where the stated allergen is a combination product and the shorthand does not say which ingredient
caused the reaction, a drug the note itself would propose that shares an ingredient with the product
is proposed conditionally on which ingredient was the culprit. The note does not treat any
ingredient as a documented allergen and does not assign the allergy to a drug class.

Two alternatives were declined. Proposing the drug outright with the shared ingredient called out
beside it puts a possible allergen on an order line, where a hurried reader acts on the order and
skips the warning. Withholding the drug and saying why was offered as the recommendation and was
not chosen; the clinician took the conditional, which keeps the first-line drug visible as an
option.

Given orders are unchanged by this ruling. A given order that shares an ingredient stays in the Plan
with its sig, and any objection is written beside it, as *A given order is a given* already
requires.

## Ruling 3 — the condition comes first and a fallback covers the shared ingredient or not known

The conditional proposal states the condition before the drug, and it carries a fallback for the
case where the culprit is the shared ingredient or is not known. The fallback names the drug that is
safe on what the encounter established:

```text
If the Vicodin reaction was to the hydrocodone: acetaminophen 650 mg PO q6h PRN fever.
If to the acetaminophen, or not known: ibuprofen 400 mg PO q6h PRN fever.
```

The reader therefore meets the condition before the dose, and the unanswered state, which is every
note's state when it is written, points at the safe drug. Each half could be accepted or dropped on
its own, so the two are two numbered `FILLED·proposed` items under drift row 21's definition of an
item. Drug-first wording was declined because a reader scanning the Plan for orders meets the dose
before the condition that may bar it. A conditional with no fallback was declined because it leaves
the problem untreated until the question is answered.

This record does not rule the case where nothing is safe on what the encounter established. A run
that meets it raises it in the pre-approval question that ruling 6 requires.

## Ruling 4 — the status code is the shared class, otherwise `Z88.8`

The `Z88` allergy status family is keyed only on drug class. Where every ingredient of the product
falls in one `Z88` class, the note codes that class, because the class is established whichever
ingredient was the culprit. Where the ingredients fall in different classes, the status is `Z88.8`
Allergy status to other drugs, medicaments and biological substances. The note never codes a class
the encounter did not establish, and never codes one class per ingredient.

`Z88.9` Allergy status to unspecified drugs, medicaments and biological substances was declined: it
describes a record that does not know the drug, and this record names it. Always coding `Z88.8` was
declined because it discards a class code that is true when every ingredient shares the class. The
descriptors were read from `reference/icd10cm-2026.sqlite` with `python tools/icd10_lookup.py` on
2026-10-08. The repository carries the tabular list and not the alphabetic index, so the choice
between `Z88.8` and `Z88.9` is a skill ruling resting on the general *other* and *unspecified*
conventions, not a citation of how the index routes a named combination product.

Where the clinician names the culprit, ruling 6 applies and the culprit's class is coded.

## Ruling 5 — the coding rule lives once in clinical-note and icd10-cpt points to it

The rule in ruling 4 is written once, as a qualification of the drug row in the allergy table of
`skills/clinical-note/SKILL.md`, which today reads `Z88.0`–`Z88.9`, keyed on drug class.
`skills/icd10-cpt/SKILL.md` points to that row by path where it selects allergy status codes. On
`main` at the time of the ruling, icd10-cpt contained no allergy rule at all, so an icd10-cpt run on
the same encounter could still have coded a guessed class. A copy in each skill was declined because
an edit to one copy fails nothing in the other.

## Ruling 6 — the culprit ingredient is a pre-approval patient question

The culprit-ingredient question reaches the clinician before approval. In a batch it joins
batch-shift's `PRE-APPROVAL PATIENT QUESTIONS` block beside the Review-sheet go-ahead; a single-note
run asks it before its go-ahead. *Not known* is always a valid answer and resolves the item.

Where the clinician names the culprit, the answer is a given and the note becomes an ordinary
single-allergen case: the allergy line takes the culprit in his words, the culprit's class is coded,
and the conditional proposal collapses into a plain one. Where the answer is *not known*, the
conditional with its fallback and the status from ruling 4 stand.

A `FLAG` was declined because a flag is a documented finding the note abandoned, and the culprit was
never documented. A `GAPS` entry was declined because GAPS holds what the rubric needs, the skill
keeps allergy slots out of GAPS, and the clinician has already ruled that a missing allergy reaction
takes no GAPS entry.

## Ruling 7 — the Allergies box carries the product exactly as stated

The Drug line of the Allergies field reads the product exactly as stated, `Drug - Vicodin`, with its
reaction under the existing reaction rule. It names no ingredients and carries no wording that the
culprit is unknown. Listing the ingredients was declined because, in a field that lists allergens,
the parenthetical reads as an allergy to both. Writing that the culprit is not known was declined
because drift row 17 refuses a hedge in an allergy slot. The uncertainty already lives in the
pre-approval question and the conditional proposal. Drift row 17 is unchanged.
