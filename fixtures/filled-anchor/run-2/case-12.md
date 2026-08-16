# case-12

## 1. Filled and derived values held before reading the note

The tier block is present, so nothing here is being treated as filled by default. `FILLED·asserted` items 1 through 8 are the vitals and body measurements; `DERIVED` item 1 is the BMI, whose two inputs are both filled, so it is treated as filled here.

| Value | Tier | Codes it supports |
| --- | --- | --- |
| BP 112/68 | filled | none — normal for a 16-year-old female, so no `R03.0` |
| HR 98 | filled | none — upper-normal for age, no tachycardia code |
| T 100.6 F | filled | `R50.9`, marked |
| RR 18 | filled | none — normal for age, so no `R06.82` |
| SpO2 99% on room air | filled | none — normal, and the lung exam is clear |
| Ht 5'5" (65 in) | filled | input to the BMI only |
| Wt 130 lb | filled | input to the BMI only |
| BMI 21.6 | derived from two filled inputs | `Z68.52`, marked |

Non-vital filled items (`FILLED·asserted` 9 through 24 and the whole of `FILLED·proposed`) are history, negatives, administrative fields and the proposed plan. None of them is the sole anchor of a proposed code: every diagnosis coded below is anchored to a given.

Accounting: eight filled values and one derived-from-filled value. Six support no code. Two support one code each, and both of those codes carry `SOURCE: filled` in step 3 and appear again in step 4.

## 2. Codable elements

Diagnoses, from the Assessment:

- Acute sinusitis, frontal and sphenoid — given, recorded in the source and carried as the final diagnosis
- Acute pharyngitis — given, sore throat with pharyngeal erythema on exam
- Cough — given
- Nasal congestion and rhinorrhea — given
- Right cervical lymphadenopathy — given, on exam
- Right costovertebral angle tenderness — given, on exam
- Vulvovaginal candidiasis — given as a recorded diagnosis, supported by nothing else in the record (FLAG 1)
- Documented sick contact — given, her coach was sick on Saturday
- History of urinary tract infection — given
- History of bilateral acute otitis media — given
- Former vaper — given
- Fever — **filled-anchored**, the only temperature in the record is the filled 100.6 F
- BMI 21.6 — **filled-anchored**, both inputs filled

Differential entries carrying codes: ten, coded in their own section below.

Procedures, from the Plan and Objective: none. Seven tests were ordered and the note states no treatment was administered in clinic; nothing documents that any test was performed on site rather than sent, so no laboratory CPT code is proposed. No E/M level is selected, because none was requested — step 5 offers the elements instead.

## 3. Proposed codes

```
ICD-10  J01.80  Other acute sinusitis
  ANCHOR: "Tenderness to palpation over the frontal and sphenoid sinuses." and
          "Final diagnosis: acute sinusitis involving more than one sinus but not
          pansinusitis, frontal and sphenoid"
  SPECIFICITY: complete — two sinuses are documented and neither is pansinusitis, which is
               what J01.80's inclusion term names; J01's remaining axis is recurrence, and
               the PMH documents no prior sinusitis, so the non-recurrent member is the
               documented one rather than J01.81
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  J02.9  Acute pharyngitis, unspecified
  ANCHOR: "Oropharynx with pharyngeal erythema; no tonsillar exudate" and
          "CC: \"sore throat, cough, runny nose, congestion. started Saturday\""
  SPECIFICITY: needs: the organism. A rapid group A streptococcus antigen with reflex
               culture is ordered and unresulted; a positive result moves this to J02.0
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R05.9  Cough, unspecified
  ANCHOR: "Respiratory: cough, present."
  SPECIFICITY: needs: duration. R05.1 acute cough and R05.3 chronic cough both exist; the
               visit date is absent from the source, so the elapsed days from Saturday do
               not compute and the acute member cannot be asserted
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R09.81  Nasal congestion
  ANCHOR: "Nares with rhinorrhea and mucosal swelling." and "Nasal congestion, rhinorrhea
          and sneezing, present."
  SPECIFICITY: complete — R09.81 has no further axis; it subdivides by neither laterality,
               severity nor timing
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R59.0  Localized enlarged lymph nodes
  ANCHOR: "Neck: supple. Right sided cervical lymphadenopathy, mobile. No posterior
          cervical chain enlargement"
  SPECIFICITY: complete — R59's only axis is localized against generalized (R59.1), and the
               note documents a single right cervical chain with no other region enlarged.
               R59 does not subdivide by site or side
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R39.851  Costovertebral (angle) tenderness, right side
  ANCHOR: "Right costovertebral angle tenderness on percussion. No left costovertebral
          angle tenderness."
  SPECIFICITY: complete — laterality documented as right, and R39.85's own excludes2 sends
               abdominal and pelvic pain (R10.-) away from this code, so R10.A1 flank pain
               is not the more specific option here: the note documents tenderness elicited
               on examination rather than pain the patient reported
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  B37.31  Acute candidiasis of vulva and vagina
  ANCHOR: "Vulvovaginal candidiasis. Recorded as a given diagnosis, and unsupported by
          anything else in the record." and the final diagnosis line "acute candidiasis of
          vulva and vagina B37.31, flagged as unsupported and not to be entered until a
          supporting finding is documented"
  SPECIFICITY: needs: whether the episode is acute or recurrent. B37.32 covers recurrent
               and chronic candidiasis of vulva and vagina, and the source documents
               neither a first episode nor a recurrence
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z20.9  Contact with and (suspected) exposure to unspecified communicable disease
  ANCHOR: "Sick contact: her coach was sick on Saturday."
  SPECIFICITY: needs: what the contact's illness was. The source records only that the
               coach was sick, so no named-disease Z20.- child is supported — notably not
               Z20.822, since nothing documents that the contact had COVID-19
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z87.440  Personal history of urinary (tract) infections
  ANCHOR: "PMH/PSH: bilateral acute otitis media; urinary tract infection, number of
          episodes and date not documented"
  SPECIFICITY: complete — Z87.440 is the billable child under the Z87.44 header, and the
               history axis it carries is the infection type, which the note documents
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z87.898  Personal history of other specified conditions
  ANCHOR: "PMH/PSH: bilateral acute otitis media" and "History of bilateral acute otitis
          media."
  SPECIFICITY: complete — Z87.898 is the residual for a resolved condition with no
               dedicated personal-history code, and acute otitis media has none. An
               "other specified" residual is not an unspecified one; laterality is not an
               axis of a Z87 history code
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z87.891  Personal history of nicotine dependence
  ANCHOR: "tobacco and nicotine: former vaper, does not currently vape or smoke"
  SPECIFICITY: complete — Z87.891 has no further axis and does not subdivide by product;
               its only excludes1 is current nicotine dependence (F17.2-), which the note
               rules out by documenting that she does not currently vape or smoke
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R50.9  Fever, unspecified
  ANCHOR: "T 100.6 F is a filled abnormal and is worked up below." and "Constitutional:
          chills, present. Fever, present on the filled vital set today."
  SOURCE: filled — the temperature of 100.6 F is filled (FILLED·asserted 3); the chills are
          a given, but chills alone code to R68.83 Chills (without fever), which R50.9
          excludes1 against. The fever half of this code exists only in the filled vital
          set; confirm before submitting
  SPECIFICITY: needs: the fever's origin. R50.81 fever presenting with conditions
               classified elsewhere requires an established underlying condition, and the
               seven ordered tests are all unresulted, so the residual is what the record
               supports
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z68.52  Body mass index [BMI] pediatric, 5th percentile to less than 85th percentile for age
  ANCHOR: "Ht 5'5\" (65 in), Wt 130 lb, BMI 21.6. All eight values are filled" and
          "BMI 21.6 = 703 x 130 / 65^2 = 91,390 / 4,225 = 21.63, rounds to 21.6."
  SOURCE: filled — both inputs are filled, the height (5'5") and the weight (130 lb), so
          the BMI and therefore the percentile band rest on two invented numbers; confirm
          before submitting
  SPECIFICITY: complete — laterality, episode and site are not axes of Z68; the code set's
               own note fixes the pediatric range at ages 2 to 19 and the patient is 16, so
               the adult Z68.1-Z68.45 band is excluded outright
  CONFIDENCE: verify this number. The descriptor and the age rule are from the code set,
              but the band itself is a CDC growth-chart percentile and the charts are not
              shipped in reference/icd10cm-2026.sqlite, so which of Z68.51, Z68.52 and
              Z68.53 a BMI of 21.6 falls in at age 16 is recalled rather than looked up
```

### CPT

No CPT code is proposed.

- No procedure is documented. The Objective records seven tests as **ordered**, states that no result exists for any of them, and states that no treatment was administered in clinic. Nothing documents that a point-of-care test was performed on site, and an in-office laboratory CPT code asserts that it was.
- No E/M level is selected, because none was requested. Step 5 offers the elements.

## Differential, documents MDM, not for entry

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---
```

Entry 1, acute rhinosinusitis, frontal and sphenoid, most likely viral — FAVORED. Coded `J01.80  Other acute sinusitis` in the proposed list above, where it is the final diagnosis. It is not repeated here, because a code proposed for entry cannot also read NOT FOR ENTRY.

```
ICD-10  J01.90  Acute sinusitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 2, acute bacterial rhinosinusitis, cannot be settled from this record. The code set does not subdivide J01 by organism class, so the bacterial question does not reach the code number at all; the unspecified member is what an unsettled sinus entry renders as.

```
ICD-10  J02.0  Streptococcal pharyngitis   NOT CODED   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 3, streptococcal pharyngitis, less likely. The descriptor names the organism and the rapid strep with reflex culture is unresulted. Refusal recorded in step 4.

```
ICD-10  B27.90  Infectious mononucleosis, unspecified without complication   NOT CODED   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 4, infectious mononucleosis, less likely. The descriptor asserts the disease and the monospot is unresulted. Refusal recorded in step 4.

```
ICD-10  J11.1  Influenza due to unidentified influenza virus with other respiratory manifestations   NOT CODED   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 5, influenza, possible. "Unidentified influenza virus" waives the organism, not the disease — the descriptor still asserts influenza, and the rapid influenza A and B antigen is unresulted. Refusal recorded in step 4.

```
ICD-10  U07.1  COVID-19   NOT CODED   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 6, COVID-19, possible. The descriptor asserts the disease and the rapid antigen is unresulted. Refusal recorded in step 4.

```
ICD-10  N10  Acute pyelonephritis   NOT CODED   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 7, acute pyelonephritis, right — the finding that must not be lost. The descriptor asserts the infection; the urinalysis, microscopic urinalysis and urine culture are all unresulted. Refusal recorded in step 4.

```
ICD-10  S39.012A  Strain of muscle, fascia and tendon of lower back, initial encounter   NOT CODED   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 8, musculoskeletal right flank strain, plausible alternative. No injury, mechanism or strain is documented — only that the illness began after volleyball practice, which is temporal rather than causal. Refusal recorded in step 4.

Entry 9, vulvovaginal candidiasis, recorded as a given diagnosis. Coded `B37.31  Acute candidiasis of vulva and vagina` in the proposed list above, because the source charted it as a diagnosis and the note carries it into its final diagnosis field. It is not repeated here for the same reason as entry 1. What it is missing is in step 4 under UNDOCUMENTED.

```
ICD-10  J30.9  Allergic rhinitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 10, allergic rhinitis, less likely. Argued against by the acute onset with chills, the documented sick contact and the fever.

## 4. What documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
The infectious agent. J01 carries "code (B95-B97) to identify infectious agent" and no
organism is documented anywhere in the source
  affects: J01.80

The rapid group A streptococcus result with its reflex culture
  affects: J02.9 — a positive result moves this to J02.0

The visit date, which is what makes the symptom duration compute at all. Onset is given as
Saturday and the visit date is absent, so no day count exists
  affects: R05.9 — a duration moves this to R05.1 acute cough or R05.3 chronic cough. It
           also affects the withheld antibiotic decision, since the 10-day bacterial
           rhinosinusitis criterion cannot be evaluated without it

Any genital or pelvic examination finding, and a wet mount, KOH preparation or vaginal pH.
No vaginal discharge, itching, odor, irritation or dysuria is documented, no genitourinary
examination is documented, and none of the seven ordered tests is confirmatory for this
diagnosis. FLAG 1 says confirm or remove before entry, and that flag reaches the code
  affects: B37.31 — and the acute-against-recurrent axis, which would settle B37.31 against
           B37.32, needs the same visit

Whether the vaping met nicotine dependence, and its duration and quit date
  affects: Z87.891 — the record documents a former vaper, which is a use history; the
           descriptor says dependence

What the sick contact's illness was
  affects: Z20.9 — a named disease moves this to a specific Z20.- child

Whether any of the seven ordered tests was performed in clinic or sent out, and by whom
  affects: no proposed CPT code. Nothing on-site is documented, so none was proposed
```

```
--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
R50.9 — T 100.6 F, a filled temperature (FILLED·asserted 3). The chills are a given; the
fever is not
  needs: a measured temperature. If the temperature is not confirmed, the given chills
         alone code to R68.83 Chills (without fever), which is the excludes1 partner of
         this code — so the measurement decides which of the two applies, not merely
         whether this one stands

Z68.52 — BMI 21.6 derived from a filled height (5'5", 65 in) and a filled weight (130 lb)
  needs: a measured height and a measured weight. Both inputs are invented, and the band is
         a CDC percentile rather than a BMI threshold, so nothing here can be checked
         arithmetically the way an adult Z68 band can
```

```
--- NOT CODED, NOTHING ESTABLISHED IT ---
Streptococcal pharyngitis, suspected on pharyngeal erythema and right cervical
adenopathy; argued against by prominent cough, rhinorrhea and sneezing, and by a low
modified Centor. Rapid strep with reflex throat culture ordered, no result
  NOT CODED: J02.0  Streptococcal pharyngitis
  needs: a positive rapid antigen or throat culture
  proposed instead: J02.9  Acute pharyngitis, unspecified (proposed above)

Infectious mononucleosis, suspected on right cervical adenopathy in an adolescent; argued
against by the unilateral distribution without posterior chain involvement, no tonsillar
exudate and no splenomegaly. Monospot ordered, no result
  NOT CODED: B27.90  Infectious mononucleosis, unspecified without complication
  needs: a positive monospot or EBV serology
  proposed instead: R59.0  Localized enlarged lymph nodes (proposed above)

Influenza, suspected on abrupt onset, chills and a documented sick contact; argued against
by prominent nasal and sinus localization. Rapid influenza A and B antigen ordered, no
result
  NOT CODED: J11.1  Influenza due to unidentified influenza virus with other respiratory
             manifestations
  needs: a positive influenza antigen or PCR. "Unidentified influenza virus" waives the
         organism and still asserts the disease
  proposed instead: R05.9, R09.81 and J02.9 (proposed above), plus Z20.9 Contact with and
                    (suspected) exposure to unspecified communicable disease

COVID-19, suspected on a congruent presentation with a documented sick contact. Rapid
COVID-19 antigen ordered, no result
  NOT CODED: U07.1  COVID-19
  needs: a positive test
  proposed instead: Z20.9  Contact with and (suspected) exposure to unspecified
                    communicable disease (proposed above). NOT Z20.822 — the source
                    documents that the coach was sick, not that the coach had COVID-19, so
                    the specific exposure code would assert a contact nobody recorded

Acute pyelonephritis, right, suspected on right costovertebral angle tenderness with
chills, a filled temperature of 100.6 F and a documented history of urinary tract
infection; argued against by no documented dysuria, frequency, urgency or hematuria and a
soft non-tender abdomen. Urinalysis, microscopic urinalysis and urine culture and
sensitivity ordered, no result
  NOT CODED: N10  Acute pyelonephritis
  needs: a urinalysis that resulted, and a culture. N39.0 is refused on the same ground —
         coding a urinary tract infection with no urinalysis result invents the result
  proposed instead: R39.851  Costovertebral (angle) tenderness, right side (proposed above)

Musculoskeletal right flank strain, raised as the alternative for the right costovertebral
angle tenderness because the illness began after volleyball practice; argued against by the
concurrent fever and chills, which it does not explain
  NOT CODED: S39.012A  Strain of muscle, fascia and tendon of lower back, initial encounter
  needs: a documented mechanism or injury. Onset after practice is temporal, not causal,
         and the 7th character A asserts an initial encounter for an injury nobody recorded
  proposed instead: R39.851  Costovertebral (angle) tenderness, right side (proposed above)

Chills, documented as a given, with the only temperature in the record a filled one
  NOT CODED: R68.83  Chills (without fever)
  needs: a measured temperature. This code and R50.9 are excludes1 partners, so the
         measurement decides between them; R50.9 is proposed and marked filled meanwhile,
         and its inclusion term "Fever with chills" is what carries the given symptom
  proposed instead: R50.9  Fever, unspecified, with SOURCE: filled (proposed above)
```

## 5. E/M supporting elements

No level is selected, because none was requested. The elements the encounter documents:

- **Problems addressed.** One acute illness charted as the final diagnosis, one incidental charted diagnosis resting on nothing else in the record, and an examination finding — right costovertebral angle tenderness — that appears in no source diagnosis. Ten differential entries are argued with rationale attached, and two of them, acute pyelonephritis and infectious mononucleosis, are undiagnosed new problems the encounter could not exclude.
- **Data reviewed and analyzed.** Seven tests ordered: rapid COVID-19 antigen, rapid group A streptococcus antigen with reflex throat culture, rapid influenza A and B antigen, urinalysis, microscopic urinalysis, urine culture and sensitivity, and monospot. None resulted at the time of the note, and no callback plan is documented (FLAG 4).
- **Risk.** Antibiotics deliberately withheld pending the urine results and a bedside determination of symptom duration; a named agent exclusion, nitrofurantoin, if pyelonephritis is confirmed; activity restriction pending the monospot for splenic rupture risk; and return precautions naming orbital and intracranial complications of sinusitis.

The MDM phrasing above is **recalled**. No coding guidelines ship in this repo, and `reference/icd10cm-2026.sqlite` holds the tabular alone, so nothing here verifies the element names or how they map to a level. The clinician assigns the level.
