# Comprehensive SOAP — template

The default branch of [clinical-note](SKILL.md). Tiering rules live in the skill; this file is the shape.

Structure verified against submitted notes. This is **not** a four-paragraph prose note — it carries OLDCARTS, a three-generation family history, coded diagnoses and age-appropriate screening, the same as the H&P. The branches differ in headings and depth, not in rigor.

```
S:

CC: "<the patient's own words, quoted>"

HPI (OLDCARTS):
Onset, Location, Duration, Character, Aggravating, Relieving, Timing, Severity
<one line, semicolon separated. All eight carry a value and severity is N/10;
 then pertinent negatives the shorthand states>

Allergies (reaction): <allergen - reaction; NKDA if none>
Home meds: <drug dose route frequency (reason for taking)>
PMH/PSH: <given>
FH (3 generations): GP: … ; Parents: … ; Sibs: …
SH: <occupation; education; marital; tobacco; alcohol; drugs; spiritual; environmental;
     nutrition; fitness; sleep — one clause each>
ROS pertinent:
<System: finding +/-; finding +/->

O:

VS: BP, HR, T, RR, SpO2, Ht, Wt ∴ BMI
Gen: <appearance, work of breathing>
<then each system examined; state normal for the ones filled>
Labs/Tests today: <given results only; treatments administered in clinic>

A:

Differential:
<Diagnosis - CODE: the findings that support it. Favored.>
<Diagnosis - CODE: the specific findings that argue against it. Less likely.>
<Diagnosis - CODE: same. Less likely.>

Preexisting diagnoses (ICD10): <condition - CODE; condition - CODE>
Final diagnosis: <condition - CODE>
Age-appropriate screening to consider: <list keyed to age, sex and risk factors>

P:

Nonpharm: <rest, hydration, counseling, red flags>
Pharm:
<Generic name dose route frequency duration — one per line>
Education: <technique, precautions, what was reviewed>
Follow up: <interval, and what would bring them back sooner>
```

## Section notes

**Quote the chief complaint.** The patient's words, in quotation marks.

**No OLDCARTS element is ever blank.** Eight, always eight — `not documented` in any of them is a defect, not a disclosure. Where the shorthand supplies none, infer one that follows from the presenting complaint; that is the same act as the exam of a system the shorthand never mentions, which [SKILL.md](SKILL.md) lists as grounded and expected. Each filled element is declared in `FILLED·asserted` carrying its value.

**Severity is a numeric pain scale.** `6/10 facial pressure`, never a word and never blank. It is the one OLDCARTS element that is not ordinary filled content — it takes the filled-vital treatment, and the reasoning, the 0/10 boundary and the two forms in which the score is a *given* are all in [SKILL.md](SKILL.md) under *Filled vitals, body measurements and the pain score*. Do not restate them here; do apply them.

**`Allergies (reaction)` and every `SH:` clause are boxes too, and none of them is ever a hedge.** `NKDA if none` is what the template above says, and it means it: `Allergies (reaction): Not documented this visit` is a sentence defending the note rather than reporting on the patient, which drift row 12 has forbidden since issue #28. Same for `tobacco status not documented`, and same for a blank clause. Which value each box takes is [SKILL.md](SKILL.md)'s business under *Which way a social or allergy slot reads* — two are settled by a count over the corpus and every other box by the grounding rule — and drift row 16 checks it. Do not restate those rules here; do apply them, and declare every filled box in `FILLED·asserted` carrying its value. Issue #29.

**Screening keys to a *given* tobacco history and never to a filled one.** The pack-year note below computes from a history the shorthand supplied. A **positive** tobacco status is never filled into the `SH:` clause in the first place, so there is no case where this note's screening line rests on a smoking history the skill invented.

**Codes belong in this note, in three places.** Preexisting diagnoses, **every differential entry**, and the final diagnosis all carry ICD-10-CM. Route them through [icd10-cpt](../icd10-cpt/SKILL.md) so each is anchored and flagged, then place them here. **Give it the tier assignment along with the text** — it declines to code off a filled value, and it cannot see which values those are from the note body alone.

**Only two of the three leave the note.** The preexisting diagnoses and the final diagnosis go on to Medatrax's `ICD-10-CM` category; the differential's codes stay on this page, because they document medical decision-making rather than record what the patient had. What that costs if it is got wrong is in [icd10-cpt](../icd10-cpt/SKILL.md), with the rule.

**Generic names in the Plan.** Shorthand records brands; the note records generics — Toradol → ketorolac, Decadron → dexamethasone, Duoneb → ipratropium-albuterol, Phenergan DM → promethazine DM. Keep the dose and route exactly as given, and fill the duration where the drug has a standard course.

**A Plan parenthetical, where there is one, is the trade name and nothing else.** `Amoxicillin-clavulanate (Augmentin) 875/125 mg PO twice daily x 10 days`. Not which parts of the sig came from the shorthand and which were supplied, not why the duration was chosen, not which ear is inflamed — that reasoning goes in the Assessment and the tier accounting goes in the tier block. The trade name is permitted here, not required; `Home meds` is the one line whose parenthetical carries something else, and what it carries is the reason for taking. The rule itself is drift row 12 in [SKILL.md](SKILL.md).

**The differential is graded work.** Each entry names the findings that place it, and every rejected entry names the specific finding that rejects it — *afebrile, no focal crackles or egophony*. A bare list of diagnoses scores nothing.

**And every entry carries a code, on one line with the rationale.** The code is pinned to its label with a hyphen and the colon still introduces the clause, which is the punctuation rule in [SKILL.md](SKILL.md) applied unchanged:

```
Acute bronchitis - J20.9: cough three weeks, clear lungs, afebrile. Favored.
```

[HP.md](HP.md) puts the code on a line of its own because the school's template does. **What has to match across the branches is the codes, not the layout** — the same encounter codes the same way whichever branch it is written in. This template's shape was verified against submitted notes and it keeps it. Issue #19.

**Every entry gets a code, and no diagnosis the encounter did not establish gets one that overstates it.** That reaches the favored entry and the `Final diagnosis` line too, not only the entries argued against — a hedge is most often on the conclusion. `icd10-cpt` declines a descriptor naming a confirmed organism or disease where nothing established either: a suspected COVID-19 with no swab takes `Z20.822 Contact with and (suspected) exposure to COVID-19`, never `U07.1`. Drift row 13 in [SKILL.md](SKILL.md) is what checks it.

**Screening keys to risk, not just age.** A 0.5 PPD × 40 year history is 20 pack-years, which crosses the LDCT lung-cancer screening threshold — so the derived value earns a screening line. Compute the pack-years and say so.

**Labs/Tests today is never filled.** Only what was given, plus treatments administered in clinic. Where there is none, say so rather than leave the line to be completed by someone else.

## Intervention and Evaluation

Medatrax's `2. FNP: Comprehensive Soap Note` has **six** boxes — `Intervention` and `Evaluation` follow `Plan`. **Leave both empty.** All 25 submitted notes sampled fill S/O/A/P and leave these blank; that is established practice and the notes are being accepted.

Generate them only when the clinician asks.
