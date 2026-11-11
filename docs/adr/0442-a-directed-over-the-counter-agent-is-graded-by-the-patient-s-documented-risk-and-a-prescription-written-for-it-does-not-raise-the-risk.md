# A directed over-the-counter agent is graded by the patient's documented risk, and a prescription written for it does not raise the risk

**Measured at:** 7ba786b6439d8bf0d212dd79fee30fdcf0be25d1

On 2026-11-10 a guidance check, run while building private E/M check sheets, tested
[ADR 0292](0292-directed-otc-agents-are-drug-management-and-modifier-25-joins-the-committed-cpt-sheet.md)
ruling 1 against published coding guidance and found it contradicted. Shown the evidence, the
clinician ruled the same day: change ADR 0292 to match the guidance. The freshness gate read `FRESH`
against `main` before this record was written. **Nothing is built here beyond the prose changes
named under Consequences.**

## Measured before ruling

**ADR 0292 ruling 1 rests on a premise the guidance rejects.** It counts an over-the-counter agent
directed with a dose and directions as prescription drug management "because the clinician writes a
prescription for every agent he directs." Two published sources say a prescription written for an
over-the-counter agent does not by itself reach that level:

- AAFP, *Family Practice Management*, January/February 2021, page 9 (written by the AAFP's advisors
  to the CPT Editorial Panel and RUC): "over-the-counter (OTC) medications generally don't meet
  moderate complexity. If you use OTC medications in that context, just state why the decision was
  higher risk. A prescription for an OTC medication for insurance coverage purposes does not meet
  this threshold." Read from
  https://www.aafp.org/pubs/fpm/issues/2021/0100/p8.pdf (SHA-256
  `4bb7f701cf21578598a715d1ef33456ae2c901b872e1e44176e5f7ac9b5ba9d2`).
- AMA, CPT E/M webinar FAQ (2022): "There is no 'blanket' guidance for services to represent
  specific levels of risk. The physician is responsible for assessing (and documenting) the level of
  risk of the services to be performed including medicine management, (prescription or OTC), based
  on a specific patient's risk factors and the risks typically seen with the drug. For example, an
  NSAID in a person with kidney disease or on anticoagulant is of greater concern..." Read from
  https://www.ama-assn.org/system/files/cpt-e-m-advancing-landmark-webinar-faq.pdf (SHA-256
  `dc0eb3f79cc7b9e3c3ea56371279d6e325cd6ae21b279ea11ecab29f8270c133`).

**The committed CPT sheet does not settle it.** `reference/cpt-em-mdm-2026.md` names "Prescription
drug management" as a moderate-risk example and says nothing about over-the-counter agents, and its
`definition-risk` entry says the level of risk is based on "consequences of the problem(s) addressed
at the encounter when appropriately treated."

## Ruling 1 — a directed over-the-counter agent is graded by documented patient-specific risk

An over-the-counter agent the clinician directs with a dose and directions counts as prescription
drug management only where his shorthand, or his recorded answer, states why it carries more risk
for this patient, such as an NSAID with kidney disease or anticoagulation. Without that statement
it supports no more than low risk. A prescription written for the agent, for coverage or habit,
does not by itself raise the risk. General advice naming an option without a dose and directions
still counts toward nothing.

Keeping ADR 0292's premise was declined because the guidance names that premise and rejects it.
Grading every directed agent as low risk was declined because the AMA FAQ says patient-specific risk
can make an over-the-counter agent "of greater concern" than most prescription drugs.

## Ruling 2 — the clinician is asked only where his statement would change the level

When moderate risk from a directed over-the-counter agent would raise the E/M level and no
patient-specific risk is stated, `icd10-cpt` selects the lower level and puts one question in the
run's existing pre-approval questions: whether the agent carried a patient-specific risk he
weighed, naming the risk he would state and both levels. A yes with the reason is recorded as his
answer and counts. No question is asked when the level would not change. Where pre-approval
questions are delegated, the lower level stands; the note pass never supplies the reason.

This follows the question pattern of
[ADR 0308](0308-the-e-m-level-rests-on-what-the-clinician-did.md) ruling 2 and
[ADR 0376](0376-a-filled-sig-fits-the-entered-diagnosis-and-the-e-m-reasoning-says-not-documented-rather-than-not-done.md)
ruling 3, so the level rests on what the clinician did and judged.

## Consequences

- `CONTEXT.md` **Directed agent** no longer says the agent is prescription drug management because
  he writes a prescription; it points to this record.
- `skills/icd10-cpt/SKILL.md` step 5's *Directed agents* paragraph applies ruling 1 and ruling 2.
- ADR 0292 ruling 2, which has `clinical-note` write every directed agent with its dose and
  directions, stands: a complete sig is still the clinician's order, and it is what ruling 1 grades.
- ADR 0308 ruling 3 (a proposed drug on an addressed problem counts toward risk) is unchanged for
  prescription drugs; a proposed over-the-counter agent is graded under ruling 1 here.

## What none of this reaches

Whether a given patient-specific risk is enough for moderate risk remains the clinician's clinical
judgment; this record requires only that he states it. The AAFP and AMA texts are guidance, not CPT
text, and a later CPT edition could settle the question differently.

## Supersedes

- [ADR 0292](0292-directed-otc-agents-are-drug-management-and-modifier-25-joins-the-committed-cpt-sheet.md) ruling 1, a directed over-the-counter agent is graded by documented patient-specific risk, and a prescription written for it does not by itself make it prescription drug management.
