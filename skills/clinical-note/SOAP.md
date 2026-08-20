# Comprehensive SOAP — template

The default branch of [clinical-note](SKILL.md). Tiering rules live in the skill; this file is the shape.

Structure verified against submitted notes. This is **not** a four-paragraph prose note — it carries OLDCARTS, a three-generation family history, coded diagnoses and age-appropriate screening, the same as the H&P. The branches differ in headings and depth, not in rigor.

```
S:

CC: "<the patient's own words, quoted>"

HPI (OLDCARTS):
Onset, Location, Duration, Character, Aggravating, Relieving, Timing, Severity
<one line, semicolon separated. All eight carry a value; severity is N/10
 followed by the complaint it belongs to; then pertinent negatives the
 shorthand states>
<Onset and Duration may name more than one symptom's timeline, each written
 duration-first as "<duration> for <symptoms>". Their clauses take a comma
 here, never a semicolon — that is the element separator on this line.
 See SKILL.md>

Allergies (reaction): <Drug - allergen - reaction, or NKDA;
                      Food - allergen - reaction, or none reported;
                      Environmental - allergen - reaction, or none reported;
                      one category per line>
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
Labs/Tests today: <given results; given orders carrying no result, marked as ordered;
                  treatments administered in clinic>

A:

Differential:
1. <Diagnosis - CODE: the findings that support it. Favored.>
2. <Diagnosis - CODE: the specific findings that argue against it. Less likely.>
3. <Diagnosis - CODE: same. Less likely.>

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

**`Allergies (reaction)` and every `SH:` clause are boxes too, and none of them is ever a hedge.** `Allergies (reaction): Not documented this visit` is a sentence defending the note rather than reporting on the patient, which drift row 12 has forbidden since issue #28. Same for `tobacco status not documented`, and same for a blank clause. Which value each box takes is [SKILL.md](SKILL.md)'s business under *Which way a social or allergy slot reads*: the drug-allergy and tobacco defaults are settled by corpus counts, while #168 supplies the silent Food and Environmental values. Drift row 17 checks them. Do not restate those rules here; do apply them, and declare every filled box in `FILLED·asserted` carrying its value. Issues #29 and #168.

**The Allergies field always carries Drug, Food, and Environmental lines in that order.** Every allergen the shorthand names reaches the line for its kind under issue #96. Under issue #168, silence fills `Drug - NKDA`, `Food - none reported`, and `Environmental - none reported`; a stated item replaces only its category's negative. Each filled line is declared in `FILLED·asserted` carrying its value. The category label takes a hyphen, never a second colon. Where an allergen goes and what a food intolerance takes are [SKILL.md](SKILL.md)'s under *Which way a social or allergy slot reads*.
**The `- reaction` half of that line is written even where the shorthand supplies only the allergen.** It is inferred and declared like any other filled value, and **the box itself carries no marker** — `Penicillin - rash`, never `reaction not documented` and never a tier word. After obvious misspellings are corrected, **each distinct allergen gets its own declaration**, naming what the reaction was **reasoned from for that allergen**; one rationale for the list is not several reasoned reactions. The rule, the drug-and-food disclosure floor and what it costs are [SKILL.md](SKILL.md)'s under *The reaction beside a given allergen*; the one clause worth carrying in a reader's head here is that **an inferred reaction never licenses a drug the allergen would otherwise bar.** Issues #94 and #205.

**Screening keys to a *given* tobacco history and never to a filled one.** The pack-year note below computes from a history the shorthand supplied. A **positive** tobacco status is never filled into the `SH:` clause in the first place, so there is no case where this note's screening line rests on a smoking history the skill invented.

**Codes belong in this note, in three places.** Preexisting diagnoses, **every differential entry**, and the final diagnosis all carry ICD-10-CM. Route them through [icd10-cpt](../icd10-cpt/SKILL.md) so each is anchored and flagged, then place them here. **Give it the tier assignment along with the text** — it marks a code resting on a filled value `SOURCE: filled`, and it cannot see which values those are from the note body alone.

**Only two of the three leave the note.** The preexisting diagnoses and the final diagnosis go on to Medatrax's `ICD-10-CM` category; the differential's codes stay on this page, because they document medical decision-making rather than record what the patient had. What that costs if it is got wrong is in [icd10-cpt](../icd10-cpt/SKILL.md), with the rule.

**Generic names in the Plan.** Shorthand records brands; the note records generics — Toradol → ketorolac, Decadron → dexamethasone, Duoneb → ipratropium-albuterol, Phenergan DM → promethazine DM. Keep the dose and route exactly as given, and fill the duration where the drug has a standard course.

**A Plan parenthetical, where there is one, is the trade name and nothing else.** `Amoxicillin-clavulanate (Augmentin) 875/125 mg PO twice daily x 10 days`. Not which parts of the sig came from the shorthand and which were supplied, not why the duration was chosen, not which ear is inflamed — that reasoning goes in the Assessment and the tier accounting goes in the tier block. The trade name is permitted here, not required; `Home meds` is the one line whose parenthetical carries something else, and what it carries is the reason for taking. The rule itself is drift row 12 in [SKILL.md](SKILL.md).

**The differential is graded work.** Each entry names the findings that place it, and every rejected entry names the specific finding that rejects it — *afebrile, no focal crackles or egophony*. A bare list of diagnoses scores nothing.

**It is a numbered list, ranked most likely first, and one entry per line.** `1.` is the favored entry. The rule is [SKILL.md](SKILL.md)'s under *The shape of the differential* and binds both branches; what this template adds is the rendering, which on this branch puts the whole item on one line. **A diagnosis argued down inside a paragraph is a defect rather than an entry** — three diagnoses rejected in prose are three numbered items here, each with its own code and its own rejecting finding. Drift row 23 walks it. Issue [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70).

**And every entry carries a code, on one line with the rationale.** The code is pinned to its label with a hyphen and the colon still introduces the clause, which is the punctuation rule in [SKILL.md](SKILL.md) applied unchanged:

```
1. Acute bronchitis - J20.9: cough three weeks, clear lungs, afebrile. Favored.
```

[HP.md](HP.md) puts the code on a line of its own because the school's template does. **What has to match across the branches is the codes, not the layout** — the same encounter codes the same way whichever branch it is written in. This template's shape was verified against submitted notes and it keeps it. Issue #19.

**The `Differential:` heading is where the list starts and not where the count stops.** A second block written after the conclusion — `Also addressed this visit`, `Additional problems addressed today`, `Reasoning carried forward` — is inside the count if its lines are diagnosis-shaped, because a rule a run can escape by moving a line one heading down is not a rule. **A measurement of the patient's own body is a diagnosis here** and carries its code, `Body mass index 28.6, in the overweight range - Z68.28`. **A line of reasoning is not**, and does not get a line of its own: a drug-against-condition conflict goes in the rationale of the entry it concerns, where drift row 11 is still satisfied by its being named in the Assessment. [SKILL.md](SKILL.md)'s *The shape of the differential* carries the ruling; drift row 13 counts it. Issue [#70](https://github.com/mshamblin5150-code/clinical-skills/issues/70).

**Every entry gets a code, and no diagnosis the encounter did not establish gets one that overstates it.** That reaches the favored entry and the `Final diagnosis` line too, not only the entries argued against — a hedge is most often on the conclusion. `icd10-cpt` declines a descriptor naming a confirmed organism or disease where nothing established either: a suspected COVID-19 with no swab takes `Z20.822 Contact with and (suspected) exposure to COVID-19`, never `U07.1`. Drift row 13 in [SKILL.md](SKILL.md) is what checks it.

**And once a code is declined, the entry is named for the one that survives.** The rule is [SKILL.md](SKILL.md)'s under *Naming a differential entry* and is not restated here; what this template adds is where it lands, which is inside the one-line form above — the label before the hyphen, the surviving code after it, and the refusal inside the rationale the colon opens, written as the welded `NOT CODED: <code> <descriptor>, <reason>` pair [SKILL.md](SKILL.md) requires:

```
2. Pain in left elbow - M25.522: 5/10 pain after a fall, elbow radiographs ordered today to rule out a radial head fracture, no result. NOT CODED: S52.125A Nondisplaced fracture of head of left radius, initial encounter for closed fracture, nothing established it. Less likely.
```

**The `Favored.` entry and the `Final diagnosis` line keep the hedge instead**, so on this template the two forms sit four lines apart and are meant to:

```
1. Community-acquired pneumonia, pneumococcal organism suspected - J18.9: five days of fever and focal crackles; film ordered today with no result. NOT CODED: J13 Pneumonia due to Streptococcus pneumoniae, nothing tested for the organism. Favored.
2. Acute bronchitis - J20.9: cough is productive, but the focal crackles argue for consolidation. Less likely.

Final diagnosis: Community-acquired pneumonia, pneumococcal organism suspected - J18.9
```

Drift row 22 walks it, and `python tools/differential_scan.py <a run directory>` checks the limb that is mechanical. Issues #68 and [#153](https://github.com/mshamblin5150-code/clinical-skills/issues/153).

**The `Final diagnosis` line is read by position and not by punctuation**, which is the one thing this template's own hyphen rule does not govern: every code on it that is not inside a `NOT CODED:` clause is read as asserted, so a code pinned there with a colon, or floated as an alternative, is a diagnosis this note claims. [SKILL.md](SKILL.md) carries the case that produced the rule.

**Screening keys to risk, not just age.** A 0.5 PPD × 40 year history is 20 pack-years, which crosses the LDCT lung-cancer screening threshold — so the derived value earns a screening line. Compute the pack-years and say so.

**Labs/Tests today is never filled.** Only what was given, plus treatments administered in clinic. Where there is none, say so rather than leave the line to be completed by someone else.

**Never filled does not mean results only, and this line used to say it did.** An order the encounter recorded belongs here as an order with no result — `Monospot, sent, no result recorded` — because a given order is a given and dropping it because it has no value to report is how one goes missing. `No new testing today` describes an encounter that ordered nothing; it is **false** of one whose plan line names a test, however few answers came back. [SKILL.md](SKILL.md)'s *A given order is a given* is the rule and drift row 18 is what counts it. Issue #66.

## Intervention and Evaluation

Medatrax's `2. FNP: Comprehensive Soap Note` has **six** boxes — `Intervention` and `Evaluation` follow `Plan`. **Leave both empty.** All 25 submitted notes sampled fill S/O/A/P and leave these blank; that is established practice and the notes are being accepted.

Generate them only when the clinician asks.
