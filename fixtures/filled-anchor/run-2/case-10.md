# case-10

## Step 1 — filled and derived values held through this worksheet

The tier block is present, so nothing has to be treated as filled by default.

`DERIVED`

- BMI 30.1 = 703 x 210 / 70^2 = 147,630 / 4,900 = 30.13 -> 30.1. **Both inputs are filled**, so this value is treated as filled here.
- Patient Time band, Visit Time 0:35, Case Type ENT — administrative, no code rests on any of them.

`FILLED·asserted` — every vital and body measurement in the note

- BP 142/86 filled
- HR 96 filled
- T 100.2 °F filled
- RR 18 filled
- SpO2 96% on room air filled
- HEIGHT 5'10" (70 in) filled
- WEIGHT 210 lb filled
- BMI 30.1 filled inputs: HEIGHT 5'10" and WEIGHT 210 lb

**No vital sign was transcribed this encounter. The entire vital set and both body measurements are filled.**

`FILLED·proposed` — inferred medications, inferred sigs, proposed orders and proposed counseling. None of these is a documented procedure, so none carries a CPT code; the proposed ECG, troponin, basic metabolic panel, A1c and chest radiograph are accounted for in step 4.

Values in this list that support a code: BP 142/86, HEIGHT 5'10", WEIGHT 210 lb, BMI 30.1. Values that support no code: HR 96, T 100.2 °F (below the 100.4 °F threshold and stated as such in the note), RR 18, SpO2 96%.

## Step 2 — codable elements

**Diagnoses documented in the Assessment**

| element | support | mark |
| --- | --- | --- |
| Acute sinusitis, the stated working diagnosis | recorded | codable |
| Acute pharyngitis | recorded | codable |
| Left nonsuppurative otitis media / middle-ear effusion | recorded | codable |
| Hypomagnesemia, magnesium 1.6 mg/dL | recorded (given result) | codable |
| Sharp chest pain | recorded | codable |
| Generalized weakness | recorded | codable |
| Diffuse myalgia | recorded | codable |
| Diminished breath sounds in all fields | recorded (exam finding) | codable |
| Type 2 diabetes mellitus | recorded (history) | codable |
| History of diverticulitis | recorded (history) | codable |
| Acquired absence of part of the colon | recorded (history) | codable |
| Elevated blood pressure reading | **BP 142/86 filled** | filled-anchored |
| Class 1 obesity | **BMI 30.1 from a filled height and a filled weight** | filled-anchored |
| BMI band, adult | **BMI 30.1 from a filled height and a filled weight** | filled-anchored |

**Procedures documented in the Objective and Plan as performed**

| element | support | mark |
| --- | --- | --- |
| Ceftriaxone 1 g IM administered in clinic | recorded (drug and dose given; route inferred) | codable |
| Methylprednisolone 125 mg IM administered in clinic | recorded | codable |
| Rapid streptococcal antigen, resulted | recorded | codable |
| Rapid influenza antigen, resulted | recorded | codable |
| SARS-CoV-2 test, resulted | recorded (method not documented) | codable |
| Serum magnesium, resulted | recorded | codable |

The 12-lead ECG, troponin, chest radiograph, basic metabolic panel, point-of-care glucose and hemoglobin A1c are **proposed additions, not performed**, and are not coded.

## Step 3 — proposed codes

```
ICD-10  J01.90  Acute sinusitis, unspecified
  ANCHOR: "Acute bacterial rhinosinusitis — the documented working diagnosis, and favored
           here." and "maxillary and frontal sinuses tender to percussion consistent with
           the documented sinusitis."
  SPECIFICITY: needs: the sinus, and whether recurrent. Maxillary and frontal tenderness
               are documented on exam (J01.00, J01.10), but the diagnosis names no sinus
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  J02.9  Acute pharyngitis, unspecified
  ANCHOR: "Oropharynx — pharyngeal erythema." and "Acute pharyngitis, unspecified — J02.9"
  SPECIFICITY: needs: the organism. The rapid streptococcal antigen is negative, which
               removes J02.0 but names nothing in its place
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  H65.92  Unspecified nonsuppurative otitis media, left ear
  ANCHOR: "Ears — left tympanic membrane with an effusion."
  SPECIFICITY: needs: the episode — acute, subacute or chronic, and serous or mucoid. The
               note itself names the alternative: H65.02 if read as acute. Laterality is
               documented as left
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  E83.42  Hypomagnesemia
  ANCHOR: "Magnesium 1.6 mg/dL — below the reference range (reference approximately 1.7 to
           2.2 mg/dL)"
  SPECIFICITY: complete — E83.42 has no further axis; severity and cause are not axes of
               this code
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R07.89  Other chest pain
  ANCHOR: "Cardiovascular: sharp chest pain +" and "It is coded as R07.89, other chest
           pain, which is the honest code for a symptom that was documented and not
           characterized."
  SPECIFICITY: complete — R07.89 is the "other specified" residual and is what a documented
               sharp chest pain with no further character earns; R07.9 would understate what
               the note does say
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R53.1  Weakness
  ANCHOR: "Generalized weakness reported subjectively; no focal motor deficit on exam."
  SPECIFICITY: needs: whether this is asthenia or generalized muscle weakness. R53.1 carries
               excludes1: muscle weakness (generalized) (M62.81), and the note records the
               weakness as subjective with no motor testing documented
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  M79.10  Myalgia, unspecified site
  ANCHOR: "Musculoskeletal: diffuse myalgia +; focal joint swelling −" and "body aches all
           over"
  SPECIFICITY: needs: site. The note documents the aches as generalized, and the code set's
               site axis (M79.11, M79.12, M79.18) has no generalized member, so this may not
               be reducible at the bedside
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R09.89  Other specified symptoms and signs involving the circulatory and respiratory systems
  ANCHOR: "Respiratory: Breath sounds diminished in all fields." and "Diminished breath
           sounds in all fields — addressed, not filed."
  SPECIFICITY: complete — R09.89 is the "other specified" residual for an abnormal
               auscultatory finding, and the finding is documented as diffuse rather than
               focal, so no site axis is open. The code set ships no descriptor reading
               "diminished breath sounds" and no alphabetic index ships with it, so the
               selection is recalled even though the number is verified
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  E11.9  Type 2 diabetes mellitus without complications
  ANCHOR: "PMH: Diabetes mellitus. Diverticulitis." and "the shorthand records only "DM" in
           a history line, which is diabetes and not "diminished"; type is not stated, and
           E11 is the convention where the type is undocumented — recode if type 1"
  SPECIFICITY: needs: the documented diabetes type, and a control code if an oral agent is
               confirmed (Z79.84). Type 2 is a convention here, not documentation, and the
               metformin is inferred rather than reconciled
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z87.19  Personal history of other diseases of the digestive system
  ANCHOR: "personal history of other diseases of the digestive system Z87.19
           (diverticulitis, currently quiescent — the abdomen is soft, non-tender and
           non-distended today)"
  SPECIFICITY: complete — Z87.19 is the "other" residual under Z87.1 and diverticular
               disease has no dedicated history code; the condition is documented as past
               and today's abdominal exam is normal
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z90.49  Acquired absence of other specified parts of digestive tract
  ANCHOR: "PSH: Colon resection." and "Well-healed colon resection scar."
  SPECIFICITY: complete — Z90.49 is the "other specified" residual and the code set carries
               no segment axis for a colon resection; the resected segment would not move
               the number
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R03.0  Elevated blood-pressure reading, without diagnosis of hypertension
  ANCHOR: "Blood pressure 142/86 — addressed, not filed. This value is filled, not measured,
           and it lands above range for a 48-year-old."
  SOURCE: filled — BP 142/86 is filled; no blood pressure was transcribed this encounter;
          confirm before submitting
  SPECIFICITY: complete — R03.0 has no further axis, and the note documents no diagnosis of
               hypertension, which is the condition the descriptor names
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**`I10` is not proposed.** No single reading diagnoses hypertension, and the note says so itself — no hypertension is diagnosed and no antihypertensive is started. That limit is clinical and would hold against a measured 142/86 exactly as it holds here.

```
ICD-10  E66.811  Obesity, class 1
  ANCHOR: "BMI 30.1 — addressed, not filed. Class 1 obesity by the derived value, in a man
           with documented diabetes."
  SOURCE: filled — BMI 30.1 is derived from a filled HEIGHT (5'10") and a filled WEIGHT
          (210 lb); confirm before submitting
  SPECIFICITY: complete — the class axis is documented by the BMI itself, which places the
               value in class 1 (30.0-34.9) rather than E66.9
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z68.30  Body mass index [BMI] 30.0-30.9, adult
  ANCHOR: "BMI 30.1 = 703 x 210 / 70^2 = 147,630 / 4,900 = 30.13 -> 30.1"
  SOURCE: filled — both inputs to the BMI are filled: HEIGHT 5'10" and WEIGHT 210 lb;
          confirm before submitting
  SPECIFICITY: complete — the band matches the derived 30.1, and the adult series is correct
               at a given age of 48, which is 20 years or older
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**The note withheld E66.811 and Z68.30 and this worksheet proposes them.** That is the current rule rather than a disagreement with the note: a filled anchor is marked, not refused. Both carry `SOURCE: filled` and both appear again in step 4.

**The two filled codes are not equally exposed to the invented inch.** At a filled weight of 210 lb, 5'11" gives BMI 29.3 — which moves `Z68.30` to `Z68.29` **and deletes `E66.811` entirely**, because 29.3 is not obesity at all. The note's own tier block discloses this. So here the invented inch decides both codes, not only the band, which is the harder case and the reason the mark matters on this encounter.

### CPT

**No CPT descriptor here was looked up.** `reference/icd10cm-2026.sqlite` holds the ICD-10-CM tabular only; no CPT code set ships in this repo. Every descriptor below is recalled and every one carries `verify this number`.

```
CPT  96372  Therapeutic, prophylactic, or diagnostic injection (specify substance or drug);
             subcutaneous or intramuscular
  ANCHOR: "Ceftriaxone (Rocephin) 1 g IM once — administered in clinic today (1 g is given;
           the IM route and the single dose are inferred from the walk-in setting)"
  SPECIFICITY: needs: the documented route. The IM route is inferred, and 96372 is the code
               only if the injection was intramuscular or subcutaneous; an intravenous push
               is a different code
  CONFIDENCE: verify this number — recalled, not looked up; no CPT set ships in this repo
```

```
CPT  96372  Therapeutic, prophylactic, or diagnostic injection (specify substance or drug);
             subcutaneous or intramuscular
  ANCHOR: "Methylprednisolone (Solu-Medrol) 125 mg IM once — administered in clinic today
           (given)"
  SPECIFICITY: complete — the route is documented as IM in the source, so this second
               administration needs no further axis. Whether a second unit is separately
               reportable is a payer rule, not a code axis
  CONFIDENCE: verify this number — recalled, not looked up; no CPT set ships in this repo
```

**The drug supply itself is HCPCS Level II, not CPT** — a J-code per unit for the ceftriaxone and the methylprednisolone. Neither is proposed here, because no HCPCS set ships in this repo either and a recalled J-code with a recalled unit definition is two guesses stacked.

```
CPT  87880  Infectious agent antigen detection by immunoassay with direct optical (ie,
             visual) observation; Streptococcus, group A
  ANCHOR: "Rapid streptococcal antigen — negative"
  SPECIFICITY: complete — the organism is named in the source and the code is
               organism-specific, so no further axis is open. A negative result does not
               change the code for the test performed
  CONFIDENCE: verify this number — recalled, not looked up; no CPT set ships in this repo
```

```
CPT  87804  Infectious agent antigen detection by immunoassay with direct optical (ie,
             visual) observation; Influenza
  ANCHOR: "Influenza — negative"
  SPECIFICITY: needs: whether influenza A and B were reported separately. The code is
               commonly reported per type, and the source records one undifferentiated
               "Influenza" result
  CONFIDENCE: verify this number — recalled, not looked up; no CPT set ships in this repo
```

```
CPT  87811  Infectious agent antigen detection by immunoassay with direct optical (ie,
             visual) observation; severe acute respiratory syndrome coronavirus 2
             (SARS-CoV-2) (Coronavirus disease [COVID-19])
  ANCHOR: "SARS-CoV-2 — negative"
  SPECIFICITY: needs: the test method. The source names no method, and an amplified probe
               assay is a different code (87635) from a direct-optical antigen assay
  CONFIDENCE: verify this number — recalled, not looked up; no CPT set ships in this repo
```

```
CPT  83735  Magnesium
  ANCHOR: "Magnesium 1.6 mg/dL — below the reference range (reference approximately 1.7 to
           2.2 mg/dL)"
  SPECIFICITY: needs: whether the magnesium was drawn as part of a panel. The source records
               the rest of the studies only as "labs good" with no test names, and a panel
               code would supersede a standalone magnesium
  CONFIDENCE: verify this number — recalled, not looked up; no CPT set ships in this repo
```

**No E/M code is proposed** — see step 5.

### Differential

--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

All eleven differential entries in the note are accounted for below. **Eight of them carry no code here**, because the code naming each of those diagnoses asserts an organism or a disease this encounter either tested negative for or never evaluated at all. Each refused number is named inline with `NOT CODED` attached and appears again in step 4.

```
Acute bacterial rhinosinusitis — the favored entry and the documented working diagnosis.
  Coded for entry above at J01.90. Not repeated here.
```

```
Hypomagnesemia as a contributor to the weakness — supported by a given.
  Coded for entry above at E83.42. Not repeated here.
```

```
ICD-10  J06.9  Acute upper respiratory infection, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
Acute coronary syndrome or other cardiac cause of the chest pain — cannot be excluded, and
was not evaluated
  NOT CODED: I24.9  Acute ischemic heart disease, unspecified — the descriptor asserts
  ischemic heart disease and no ECG, troponin or chest radiograph was obtained. See step 4.
  The chest pain itself is coded for entry above at R07.89
```

```
Musculoskeletal or costochondral chest wall pain from coughing
  NOT CODED: M94.0  Chondrocostal junction syndrome [Tietze] — no chest wall palpation is
  documented, which is the finding that would place it. See step 4. The chest pain itself is
  coded for entry above at R07.89
```

```
Pneumonia or lower respiratory tract infection — less likely
  NOT CODED: J18.9  Pneumonia, unspecified organism — no chest radiograph was obtained, so
  the entry is neither established nor excluded. See step 4. The auscultatory finding is
  coded for entry above at R09.89
```

```
Pulmonary embolism — less likely
  NOT CODED: I26.99  Other pulmonary embolism without acute cor pulmonale — no imaging and
  no D-dimer; pretest probability is documented as low. See step 4
```

```
Streptococcal pharyngitis — excluded by test
  NOT CODED: J02.0  Streptococcal pharyngitis — the descriptor names the organism the rapid
  antigen ruled out. See step 4. The pharyngitis is coded for entry above at J02.9
```

```
Influenza — excluded by test, with the sensitivity caveat the note records
  NOT CODED: J11.1  Influenza due to unidentified influenza virus with other respiratory
  manifestations — the descriptor asserts influenza and the rapid antigen was negative. See
  step 4
```

```
COVID-19 — excluded by test, with the same caveat
  NOT CODED: U07.1  COVID-19 — the descriptor asserts the disease and the test was negative.
  See step 4
```

```
Peritonsillar or deep neck space infection — excluded
  NOT CODED: J36  Peritonsillar abscess — no trismus, no uvular deviation, no muffled voice,
  no unilateral bulge. See step 4. The pharyngitis is coded for entry above at J02.9
```

**`Z20.822` is not proposed anywhere in this worksheet.** Its descriptor is `Contact with and (suspected) exposure to COVID-19`, and this note documents **no sick contacts** as a pertinent negative. There is no exposure here to code, so the usual substitute for a refused `U07.1` is unavailable and the documented respiratory diagnoses carry the encounter instead.

## Step 4 — what documentation is missing

--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---

```
Which sinus, and whether the episode is recurrent
  affects: J01.90 — maxillary and frontal tenderness are on the exam but the diagnosis names
  no sinus (J01.00, J01.10)

The organism behind the pharyngitis, or a throat culture
  affects: J02.9

Whether the left middle-ear effusion is acute, subacute or chronic, and serous or mucoid
  affects: H65.92 — the note names H65.02 as the acute reading

Motor testing, to separate subjective asthenia from generalized muscle weakness
  affects: R53.1 — the code carries excludes1: muscle weakness (generalized) (M62.81)

The site of the myalgia
  affects: M79.10 — the aches are documented as generalized, which may be irreducible

The documented diabetes type, its duration, the most recent A1c, and the actual home regimen
  affects: E11.9, and Z79.84 if an oral agent is confirmed. "DM" is the entire diabetic
  record for this encounter and the metformin is inferred, not reconciled

Chest pain duration, onset, radiation, exertional relationship and reproducibility on
palpation
  affects: R07.89, and the refused I24.9 and M94.0 below

The documented route of the ceftriaxone
  affects: CPT 96372 — 1 g is given, the IM route is inferred

The SARS-CoV-2 test method, and whether influenza A and B resulted separately
  affects: CPT 87811 and CPT 87804

The names and values of the remaining studies recorded only as "labs good"
  affects: CPT 83735, which may be part of a panel rather than a standalone magnesium

The colon resection indication, pathology and date
  affects: Z90.49 and Z87.19 — none of them moves either number, but all three are needed to
  set the colonoscopy surveillance interval the note asks for
```

--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---

```
R03.0 — BP 142/86, filled. No blood pressure was transcribed this encounter
  needs: a measured blood pressure, taken when he is well. The note attributes the elevation
  to an acute febrile illness and two corticosteroids given today

E66.811 — Obesity class 1 from BMI 30.1, derived from a filled height (5'10") and a filled
weight (210 lb)
  needs: a measured height and weight. At the same weight, 5'11" gives BMI 29.3 and this code
  disappears entirely — the diagnosis, not just its class

Z68.30 — BMI 30.1 from the same filled height and filled weight
  needs: a measured height and weight. One inch moves this to Z68.29
```

Every other filled value is accounted for and supports no code: HR 96, T 100.2 °F (documented as below the 100.4 °F fever threshold, so `R50.9` is not proposed), RR 18 (normal, so `R06.82` is not proposed) and SpO2 96%. The filled HEIGHT and WEIGHT support no code of their own; they reach the worksheet through the BMI codes above.

--- NOT CODED, NOTHING ESTABLISHED IT ---

```
Acute coronary syndrome or another cardiac cause of the chest pain, suspected in a
48-year-old man with documented diabetes reporting sharp chest pain, weakness graded 8/10
and a magnesium of 1.6; no ECG, no troponin, no chest radiograph and no chest wall palpation
were obtained
  NOT CODED: I24.9  Acute ischemic heart disease, unspecified
  needs: a 12-lead ECG and a troponin. The cardiac exam recorded is S1, S2 and 2+ equal
  pulses, and a normal exam does not exclude ischemia
  proposed instead: R07.89  Other chest pain

Musculoskeletal or costochondral chest wall pain, suspected on a sharp quality with a new
cough and diffuse myalgia
  NOT CODED: M94.0  Chondrocostal junction syndrome [Tietze]
  needs: chest wall palpation reproducing the pain. It was not obtained
  proposed instead: R07.89  Other chest pain

Pneumonia or lower respiratory tract infection, suspected on cough, chest pain and breath
sounds diminished in all fields; no chest radiograph was obtained
  NOT CODED: J18.9  Pneumonia, unspecified organism
  needs: a chest radiograph. The diminution is diffuse rather than focal, with no crackles,
  rhonchi or dullness, SpO2 96% and RR 18 — but two of those four are filled values
  proposed instead: R09.89  Other specified symptoms and signs involving the circulatory and
  respiratory systems

Pulmonary embolism, raised by sharp chest pain with weakness and argued down on a low
documented pretest probability
  NOT CODED: I26.99  Other pulmonary embolism without acute cor pulmonale
  needs: a D-dimer, or CT pulmonary angiography if suspicion rises. No imaging is proposed on
  this presentation alone
  proposed instead: R07.89  Other chest pain

Streptococcal pharyngitis, suspected on a sore throat with pharyngeal erythema
  NOT CODED: J02.0  Streptococcal pharyngitis
  needs: nothing pending — the rapid antigen resulted negative. A throat culture is the
  confirmatory step if the suspicion returns
  proposed instead: J02.9  Acute pharyngitis, unspecified

Influenza, suspected on abrupt onset with generalized body aches, sore throat, cough and
congestion
  NOT CODED: J11.1  Influenza due to unidentified influenza virus with other respiratory
  manifestations
  needs: a molecular test. The rapid antigen was negative and the note records that a
  negative rapid antigen does not exclude the organism
  proposed instead: J01.90  Acute sinusitis, unspecified, and J02.9  Acute pharyngitis,
  unspecified — the documented upper respiratory diagnoses, both proposed above

COVID-19, suspected on a congruent respiratory presentation
  NOT CODED: U07.1  COVID-19
  needs: a positive test. The rapid antigen was negative, with the same sensitivity caveat
  proposed instead: J01.90  Acute sinusitis, unspecified, and J02.9  Acute pharyngitis,
  unspecified. Z20.822 is not available here — the note documents no sick contacts, so there
  is no exposure to code

Peritonsillar or deep neck space infection, considered on a sore throat with pharyngeal
erythema
  NOT CODED: J36  Peritonsillar abscess
  needs: nothing pending — excluded on exam, with no trismus, no uvular deviation, no muffled
  voice and no unilateral bulge documented
  proposed instead: J02.9  Acute pharyngitis, unspecified
```

## Step 5 — E/M level

**No E/M level was requested, so none is selected.** The supporting elements are available on request; they are not assigned to a level here, and the phrasing that would map them is recalled rather than verified, because no coding guidelines ship in this repo.
