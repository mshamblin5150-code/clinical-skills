# Comprehensive SOAP — template

The default branch of [clinical-note](SKILL.md). Tiering rules live in the skill; this file is the shape.

Structure verified against submitted notes. This is **not** a four-paragraph prose note — it carries OLDCARTS, a three-generation family history, coded diagnoses and age-appropriate screening, the same as the H&P. The branches differ in headings and depth, not in rigour.

```
S:

CC: "<the patient's own words, quoted>"

HPI (OLDCARTS):
Onset · Location · Duration · Character · Aggravating · Relieving · Timing · Severity
<one line, semicolon separated; then pertinent negatives the shorthand states>

Allergies (reaction): <allergen — reaction; NKDA if none>
Home meds: <drug dose route frequency (reason for taking)>
PMH/PSH: <given>
FH (3 generations): GP: … ; Parents: … ; Sibs: …
SH: <occupation; education; marital; tobacco; alcohol; drugs; spiritual; environmental;
     nutrition; fitness; sleep — one clause each>
ROS pertinent:
<System: finding +/-; finding +/->

O:

VS: BP, HR, T, RR, SpO2, Ht, Wt → BMI
Gen: <appearance, work of breathing>
<then each system examined; state normal for the ones filled>
Labs/Tests today: <given results only; treatments administered in clinic>

A:

Differential:
<Diagnosis — the findings that support it. Favored.>
<Diagnosis — the specific findings that argue against it. Less likely.>
<Diagnosis — same. Less likely.>

Preexisting diagnoses (ICD10): <condition CODE; condition CODE>
Final diagnosis: <condition — CODE>
Age-appropriate screening to consider: <list keyed to age, sex and risk factors>

P:

Nonpharm: <rest, hydration, counselling, red flags>
Pharm:
<Generic name dose route frequency duration — one per line>
Education: <technique, precautions, what was reviewed>
Follow up: <interval, and what would bring them back sooner>
```

## Section notes

**Quote the chief complaint.** The patient's words, in quotation marks.

**Codes belong in this note.** Preexisting diagnoses and the final diagnosis both carry ICD-10-CM. Route them through [icd10-cpt](../icd10-cpt/SKILL.md) so each is anchored and flagged, then place them here.

**Generic names in the Plan.** Shorthand records brands; the note records generics — Toradol → ketorolac, Decadron → dexamethasone, Duoneb → ipratropium-albuterol, Phenergan DM → promethazine DM. Keep the dose and route exactly as given, and fill the duration where the drug has a standard course.

**The differential is graded work.** Each entry names the findings that place it, and every rejected entry names the specific finding that rejects it — *afebrile, no focal crackles or egophony*. A bare list of diagnoses scores nothing.

**Screening keys to risk, not just age.** A 0.5 PPD × 40 year history is 20 pack-years, which crosses the LDCT lung-cancer screening threshold — so the derived value earns a screening line. Compute the pack-years and say so.

**Labs/Tests today is never filled.** Only what was given, plus treatments administered in clinic. Where there is none, say so rather than leave the line to be completed by someone else.

## Intervention and Evaluation

Medatrax's `2. FNP: Comprehensive Soap Note` has **six** boxes — `Intervention` and `Evaluation` follow `Plan`. **Leave both empty.** All 25 submitted notes sampled fill S/O/A/P and leave these blank; that is established practice and the notes are being accepted.

Generate them only when the clinician asks.
