# case-07

## 1. FILLED and DERIVED values, read first

The note carries a tier block, so nothing here has to be assumed filled by default.

**DERIVED**

| | value | filled input? |
| --- | --- | --- |
| D1 | Pack-years <0.75 (<0.25 packs/day × 3 years) | no — the smoking history is given |
| D2 | BMI 29.5 = 703 × 172 / 64² | **yes — both inputs (F6 height, F7 weight)** |
| D3 | Threshold check, BMI 30.5 at 63 in | **yes — same filled inputs** |
| D4 | Patient Time = Gerontology, from age 67 | no — age is given |
| D5 | Visit Time 0:40 | inputs are estimated times (F24), not a clinical value |

**FILLED·asserted — vitals and body measurements**

| | value |
| --- | --- |
| F1 | BP 138/84 |
| F2 | HR 98 |
| F3 | T 100.9 °F oral |
| F4 | RR 20 |
| F5 | SpO2 95% on room air |
| F6 | Height 5'4" (64 in) |
| F7 | Weight 172 lb |
| F8 | BMI 29.5 — derived at D2 from F6 and F7; nothing about it was measured |

**The rest of FILLED·asserted is not a vital or a measurement** and is recorded here so it is
visibly accounted for rather than skipped: F9–F11 inferred medication agents and sigs, F12–F16
inferred social and family history, F17–F18 filled normal exam and ROS, F19 inferred nutrition,
F20–F24 declared administrative values and estimated times. **FILLED·proposed** P1–P18 is the
note's own reasoning, including P2, *every ICD-10-CM code in this document* — which is why the
codes below are looked up here rather than carried across.

**The set whose codes carry `SOURCE: filled`:** F1 (BP 138/84), F6 (height 64 in),
F7 (weight 172 lb), F8/D2 (BMI 29.5). F2, F3, F4 and F5 are filled and are checked in step 4
for whether they support a code at all.

---

## 2. Codable elements

**Diagnoses — Assessment, coded**

| element | supporting text is | codable |
| --- | --- | --- |
| COVID-19 | recorded (positive test) | yes |
| Constipation | recorded (abdominal x-ray) | yes |
| Nonsuppurative otitis media, left | recorded (left TM effusion) | yes |
| Acute pharyngitis | recorded (pharyngeal erythema) | yes |
| Right costovertebral angle tenderness | recorded (exam) | yes |
| Right upper quadrant pain | recorded (exam) | yes |
| Epigastric pain | recorded (exam) | yes |
| Transaminase elevation | recorded (AST 48) | yes |
| Other serum enzyme abnormality | recorded (ALP 136) | yes |
| Headache 7/10 | recorded (history) | yes |
| Fever | recorded (history — fever, chills) | yes |
| Hyperlipidemia, GERD, arthritis | recorded (PMH) | yes |
| Absence of cervix and uterus | recorded (PSH) | yes |
| History of nicotine dependence | recorded (SH) | yes |
| Underimmunization | recorded (PMH) | yes |
| Long-term statin therapy | recorded ("on statin") | yes |
| Six drug allergies | recorded (allergy list) | yes |

**Diagnoses — Assessment, filled-anchored**

| element | its only support | |
| --- | --- | --- |
| Overweight band, BMI 29.5 | F8 / D2, from filled height and filled weight | **filled-anchored** |
| BMI band code | same | **filled-anchored** |
| Elevated blood-pressure reading 138/84 | F1 | **filled-anchored** |

**Procedures — Objective and Plan**

SARS-CoV-2 testing; abdominal radiograph; chest radiograph; influenza antigen; rapid
streptococcal antigen; RSV antigen; complete blood count; comprehensive metabolic panel;
amylase; lipase; urinalysis with microscopic; urine culture and sensitivity. **No treatment
was administered in clinic**, so nothing in the Plan is an in-office procedure.

**Not codable this encounter, recorded so it is not read as an omission.** The age-appropriate
screening list is written as *"screening to consider"* and the immunization plan is written as
*"Defer all of them until the acute febrile illness has resolved."* Nothing on either list was
performed, ordered or administered at this visit, so no screening or immunization encounter
code is proposed. They become codable at the visit that performs them.

---

## 3. Proposed codes

### ICD-10-CM — this encounter

```
ICD-10  U07.1  COVID-19
  ANCHOR: "SARS-CoV-2 testing — **POSITIVE**"
  SPECIFICITY: complete — U07.1 has no further axis; its useAdditionalCode notes point outward
    to manifestations (J12.82 for pneumonia), which the chest film has not established
  CONFIDENCE: verified against ICD-10-CM FY2026
```

*The organism-specific limit in step 3 does not fire here. It fires where the descriptor names
an organism the encounter never established; this encounter tested and the test returned
positive, so `U07.1` is anchored to a result rather than to a suspicion.*

```
ICD-10  K59.00  Constipation, unspecified
  ANCHOR: "Abdominal x-ray — **stool burden consistent with constipation**"
  SPECIFICITY: needs: the type of constipation — K59.0 has slow transit (K59.01), outlet
    dysfunction (K59.02), chronic idiopathic (K59.04) and drug-induced (K59.03) beneath it,
    and none is documented
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  H65.92  Unspecified nonsuppurative otitis media, left ear
  ANCHOR: "**Left tympanic membrane with an effusion** — fluid behind the drum; no perforation,
    no purulent drainage, landmarks visible."
  SPECIFICITY: needs: the type of nonsuppurative otitis media — H65 separates acute serous
    (H65.0-), other acute nonsuppurative (H65.1-) and chronic forms, and the note documents an
    effusion without characterizing it. Laterality is documented as left and is not the gap
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J02.9  Acute pharyngitis, unspecified
  ANCHOR: "**Pharyngeal erythema** present; no tonsillar exudate, no asymmetry, no uvular
    deviation, no trismus."
  SPECIFICITY: needs: the causative organism — the rapid streptococcal test was sent and no
    result is recorded, so J02.0 cannot be reached or excluded
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R39.851  Costovertebral (angle) tenderness, right side
  ANCHOR: "**Right costovertebral angle tenderness** to percussion. Left costovertebral angle
    non-tender."
  SPECIFICITY: complete — laterality documented as right, and R39.85 has no axis beyond side
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R10.11  Right upper quadrant pain
  ANCHOR: "**Tenderness in the epigastrium and the right upper quadrant** on palpation."
  SPECIFICITY: complete — R10.11 names the quadrant, which is the only axis R10.1 carries
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R10.13  Epigastric pain
  ANCHOR: "**Tenderness in the epigastrium and the right upper quadrant** on palpation."
  SPECIFICITY: complete — R10.13 names the site, which is the only axis R10.1 carries
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R74.01  Elevation of levels of liver transaminase levels
  ANCHOR: "Aspartate aminotransferase **48** (elevated)"
  SPECIFICITY: complete — R74.01 covers AST and ALT by its own inclusion terms and has no
    further axis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R74.8  Abnormal levels of other serum enzymes
  ANCHOR: "Alkaline phosphatase **136** (elevated)"
  SPECIFICITY: complete — alkaline phosphatase is a named inclusion term under R74.8, and
    "other" here is a residual naming the enzyme group rather than an undocumented axis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R51.9  Headache, unspecified
  ANCHOR: "Severity — headache 7/10."
  SPECIFICITY: needs: the headache pattern — R51.0 separates headache with orthostatic
    component, and no positional or postural detail is documented
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R50.9  Fever, unspecified
  ANCHOR: "Pertinent positives the shorthand states: fever, chills, cough, sore throat, sinus
    pain, left ear pain, 7/10 headache, epigastric pain, right upper quadrant pain."
  SPECIFICITY: needs: whether the fever is being documented as presenting with an established
    underlying condition — R50.81 Fever presenting with conditions classified elsewhere exists
    and COVID-19 is established here, so which of R50.9 and R50.81 applies is a documentation
    question this note leaves open
  CONFIDENCE: verified against ICD-10-CM FY2026
```

*The anchor for `R50.9` is the history, not the temperature.* T 100.9 °F is filled (F3), but
fever and chills are given by the shorthand, so this code rests on recorded text and takes no
`SOURCE` line. Had the history been silent, the code would rest on F3 alone and would be marked.

### ICD-10-CM — preexisting and status

```
ICD-10  E78.5  Hyperlipidemia, unspecified
  ANCHOR: "PMH — hyperlipidemia (on a statin)"
  SPECIFICITY: needs: a lipid panel naming the fraction — E78.0 through E78.4 separate pure
    hypercholesterolemia, hyperglyceridemia and mixed hyperlipidemia, and no lipid values are
    recorded this visit
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  K21.9  Gastro-esophageal reflux disease without esophagitis
  ANCHOR: "PMH — hyperlipidemia (on a statin); gastro-esophageal reflux disease; arthritis;"
  SPECIFICITY: complete — K21's single axis is whether esophagitis is present, and no
    esophagitis is documented anywhere in the note
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M19.90  Unspecified osteoarthritis, unspecified site
  ANCHOR: "Chronic degenerative changes without acute findings."
  SPECIFICITY: needs: the joint and the type — the descriptor declines two axes, site and
    whether primary, secondary or post-traumatic, and the note records only "arthritis"
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z90.710  Acquired absence of both cervix and uterus
  ANCHOR: "PSH — total hysterectomy; dilation and curettage ×2."
  SPECIFICITY: complete — Z90.71 separates uterus-with-cervix, uterus-with-remaining-cervix and
    cervix-alone, and "total hysterectomy" names the first
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z87.891  Personal history of nicotine dependence
  ANCHOR: "Tobacco — former smoker, less than 0.25 packs per day for 3 years, quit;"
  SPECIFICITY: complete — Z87.891 has no further axis, and its excludes1 for current nicotine
    dependence (F17.2-) is satisfied by the documented quit
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z28.39  Other underimmunization status
  ANCHOR: "vaccinations **not** up to date."
  SPECIFICITY: complete — Z28.3 splits into delinquent/lapsed status (Z28.39) and immunization
    not carried out for a stated reason (Z28.0- through Z28.8-); the note records the status and
    no refusal or contraindication, so the residual is the correct limb rather than a gap
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z79.899  Other long term (current) drug therapy
  ANCHOR: "PMH — hyperlipidemia (on a statin)"
  SPECIFICITY: complete — no Z79 subcategory names statin therapy, so the residual is the only
    limb available. The agent and dose are filled (F9) but the fact of long-term therapy is
    given, and the code turns on the fact rather than the agent
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z88.2  Allergy status to sulfonamides
  ANCHOR: "Sulfamethoxazole-trimethoprim (Bactrim) — reaction not documented"
  SPECIFICITY: complete — Z88.2 names the drug class and has no further axis; the missing
    reaction is a documentation gap on the allergy, not on the code
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z88.1  Allergy status to other antibiotic agents
  ANCHOR: "Doxycycline — reaction not documented" / "Norfloxacin (Noroxin) — reaction not
    documented"
  SPECIFICITY: complete — Z88.0 through Z88.4 name penicillin, sulfonamide, anesthetic and
    narcotic status; a tetracycline and a fluoroquinolone fall to the antibiotic residual
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z88.8  Allergy status to other drugs, medicaments and biological substances
  ANCHOR: "Prednisone — reaction not documented"
  SPECIFICITY: complete — a corticosteroid, an antihistamine and a urinary analgesic have no
    named Z88 subcategory, so the residual is the only limb
  CONFIDENCE: verified against ICD-10-CM FY2026
```

### ICD-10-CM — filled anchor

```
ICD-10  E66.3  Overweight
  ANCHOR: "Ht 5'4" (64 in) · Wt 172 lb → **BMI 29.5**" / "**Weight and BMI:** BMI 29.5 is in
    the overweight band."
  SOURCE: filled — height 5'4" (F6) and weight 172 lb (F7) were both filled, so the BMI derived
    from them at D2 is filled throughout; confirm before submitting
  SPECIFICITY: complete — E66.3 is the leaf for the overweight band, and the BMI axis E66 asks
    for by useAdditionalCode is carried by Z68.29 below
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z68.29  Body mass index [BMI] 29.0-29.9, adult
  ANCHOR: "Ht 5'4" (64 in) · Wt 172 lb → **BMI 29.5**"
  SOURCE: filled — the band is a readout of D2, whose height (F6) and weight (F7) inputs were
    both filled; confirm before submitting
  SPECIFICITY: complete — the adult series applies at age 67 (Z68's own note sets the boundary
    at 20 years), and 29.5 falls inside 29.0-29.9 with no finer band available
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R03.0  Elevated blood-pressure reading, without diagnosis of hypertension
  ANCHOR: "**Blood pressure:** 138/84 is at the stage-1 threshold in a patient with **no
    documented hypertension**"
  SOURCE: filled — the reading itself (F1) was filled; the code's own tabular note asks for "an
    episode of elevated blood pressure", and no episode was recorded; confirm before submitting
  SPECIFICITY: complete — R03 holds only R03.0 and R03.1 (low reading), and R03.0 has no
    further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**`I10` is not proposed, and this is not a `SOURCE` question.** The note itself says *"Do not
diagnose hypertension on a single reading during an acute illness"*. No single reading
diagnoses hypertension, real or filled, so confirming the measurement would not produce `I10`
either — it would produce a second reading. The limit is clinical and marking does not reach it.

### CPT

**No CPT code set ships in this repo**, so every code below is worked from recall and every one
reads `verify this number`. None was looked up against anything.

```
CPT  87811  Infectious agent antigen detection by immunoassay with direct optical (i.e.,
             visual) observation; severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)
  ANCHOR: "SARS-CoV-2 testing — **POSITIVE**"
  SPECIFICITY: needs: the test method — an amplified probe (nucleic acid) assay is 87635 and an
    antigen assay is 87811, and the note records neither the platform nor the method
  CONFIDENCE: verify this number

CPT  74018  Radiologic examination, abdomen; 1 view
  ANCHOR: "Abdominal x-ray — **stool burden consistent with constipation**"
  SPECIFICITY: needs: the number of views — 74018 is 1 view, 74019 is 2 views, 74021 is 3 or
    more, and 74022 is a complete acute abdomen series; the note records no view count
  CONFIDENCE: verify this number

CPT  71045  Radiologic examination, chest; single view
  ANCHOR: "Chest x-ray — ordered, result not recorded; the clinic will telephone with x-ray
    results"
  SPECIFICITY: needs: the number of views, and whether the study was performed — 71046 is 2
    views, and the note documents the order and a promised telephone call without recording
    that the film was taken
  CONFIDENCE: verify this number

CPT  87804  Infectious agent antigen detection by immunoassay with direct optical (i.e.,
             visual) observation; Influenza
  ANCHOR: "Influenza testing — sent, result not recorded"
  SPECIFICITY: needs: the method, and whether A and B were separately reported — 87804 is
    reported per type when both are tested
  CONFIDENCE: verify this number

CPT  87880  Infectious agent antigen detection by immunoassay with direct optical (i.e.,
             visual) observation; Streptococcus, group A
  ANCHOR: "Rapid streptococcal testing — sent, result not recorded"
  SPECIFICITY: complete — group A streptococcus is named in the note and the rapid antigen
    method is what "rapid streptococcal testing" states
  CONFIDENCE: verify this number

CPT  87807  Infectious agent antigen detection by immunoassay with direct optical (i.e.,
             visual) observation; respiratory syncytial virus
  ANCHOR: "Respiratory syncytial virus testing — sent, result not recorded"
  SPECIFICITY: needs: the method — a nucleic acid RSV assay codes elsewhere, and the note names
    no platform
  CONFIDENCE: verify this number

CPT  85025  Blood count; complete (CBC), automated and automated differential WBC count
  ANCHOR: "Complete blood count — sent, result not recorded"
  SPECIFICITY: needs: whether a differential was included — 85027 is the CBC without
    differential, and no result at all is recorded
  CONFIDENCE: verify this number

CPT  80053  Comprehensive metabolic panel
  ANCHOR: "Comprehensive metabolic panel — sent; the AST and ALP above are the only values
    recorded"
  SPECIFICITY: complete — the note names the panel by its CPT panel name, and the panel code is
    the whole of what a named panel documents
  NOTE ON REQUIREMENTS: the AST and the alkaline phosphatase are constituents of this panel.
    Reporting 84450 and 84075 alongside 80053 would unbundle it. They are not proposed
    separately for that reason, and R74.01 and R74.8 above code the abnormal findings
  CONFIDENCE: verify this number

CPT  82150  Amylase
  ANCHOR: "Amylase — sent, result not recorded"
  SPECIFICITY: complete — 82150 has no further axis; amylase is a single named analyte
  CONFIDENCE: verify this number

CPT  83690  Lipase
  ANCHOR: "Lipase — sent, result not recorded"
  SPECIFICITY: complete — 83690 has no further axis; lipase is a single named analyte
  CONFIDENCE: verify this number

CPT  81001  Urinalysis, by dip stick or tablet reagent for bilirubin, glucose, hemoglobin,
             ketones, leukocytes, nitrite, pH, protein, specific gravity, urobilinogen, any
             number of these constituents; automated, with microscopy
  ANCHOR: "Urinalysis with microscopic — sent, result not recorded"
  SPECIFICITY: needs: whether the analysis was automated — 81000 is the non-automated form of
    the same with-microscopy service, and the note records neither
  CONFIDENCE: verify this number

CPT  87086  Culture, bacterial; quantitative colony count, urine
  ANCHOR: "Urine culture and sensitivity — sent, result not recorded"
  SPECIFICITY: needs: whether an isolate was identified — 87088 covers identification of each
    isolate and is reportable only once an organism grows; nothing has resulted
  CONFIDENCE: verify this number

CPT  87186  Susceptibility studies, antimicrobial agent; microdilution or agar dilution
            (minimum inhibitory concentration [MIC] or breakpoint), each multi-antimicrobial,
            per plate
  ANCHOR: "Urine culture and sensitivity — sent, result not recorded"
  SPECIFICITY: needs: the susceptibility method — disk diffusion is 87184 and MIC is 87186, and
    "sensitivity" alone names neither. This is reportable only if an organism grows
  CONFIDENCE: verify this number
```

### Differential

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

ICD-10  U07.1  COVID-19   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  K59.00  Constipation, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J12.82  Pneumonia due to coronavirus disease 2019   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  N10  Acute pyelonephritis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  N39.0  Urinary tract infection, site not specified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  H65.92  Unspecified nonsuppurative otitis media, left ear   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J02.9  Acute pharyngitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J02.0  Streptococcal pharyngitis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J11.1  Influenza due to unidentified influenza virus with other respiratory
               manifestations   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J01.90  Acute sinusitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  K80.20  Calculus of gallbladder without cholecystitis without obstruction
                NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R74.01  Elevation of levels of liver transaminase levels   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z79.899  Other long term (current) drug therapy   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  K21.9  Gastro-esophageal reflux disease without esophagitis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  B97.4  Respiratory syncytial virus as the cause of diseases classified elsewhere
               NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  N23  Unspecified renal colic   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

Sixteen codes across the note's fourteen differential entries — item 4 carries two
(pyelonephritis and urinary tract infection) and item 11 carries two (the transaminase
elevation and the statin therapy). Item 13, respiratory syncytial virus, **carries no code in
the note**; `B97.4` is supplied here, and it is a secondary code by its own codeFirst
instruction rather than a standalone diagnosis.

`U07.1`, `K59.00`, `H65.92`, `J02.9`, `R74.01`, `Z79.899` and `K21.9` appear both here and in
the proposed lists above. That is not a duplication to reconcile: the entries above are the
diagnoses this encounter established, and the lines here are the reasoning that placed them.
The seven remaining differential codes appear nowhere in the proposed lists and must not be
entered anywhere.

---

## 4. What documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---

The type of nonsuppurative otitis media — serous, mucoid or other acute
  affects: H65.92

The causative organism of the pharyngitis
  affects: J02.9

The type of constipation — slow transit, outlet dysfunction, chronic idiopathic, drug-induced
  affects: K59.00

The headache pattern, specifically whether there is an orthostatic component
  affects: R51.9

Whether the fever is documented as presenting with the established COVID-19 rather than as an
isolated finding
  affects: R50.9

A lipid panel naming the affected fraction
  affects: E78.5

The joint involved and whether the osteoarthritis is primary, secondary or post-traumatic
  affects: M19.90

A reaction for each of the six documented drug allergies — severity is unknown for all six,
which matters most for the prednisone entry against the standard corticosteroid escalation
  affects: Z88.2, Z88.1, Z88.8

The number of radiographic views, for both films; and whether the chest film was performed at
all rather than only ordered
  affects: 74018, 71045

The SARS-CoV-2 test method — antigen or amplified probe
  affects: 87811

Whether the complete blood count included an automated differential
  affects: 85025

Whether the urinalysis was automated
  affects: 81001

Whether the sent studies were performed in this clinic or referred to an outside laboratory —
a referred study is reported by the performing laboratory, not here
  affects: 87804, 87807, 87880, 85025, 80053, 82150, 83690, 81001, 87086, 87186

A serum creatinine — the comprehensive metabolic panel returned an AST and an alkaline
phosphatase and nothing else is recorded. It is the value the flank finding and the ibuprofen
recommendation both turn on
  affects: N10 and N39.0 below, and the analgesic conflict named in the Plan
```

```
--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---

E66.3 — the overweight band, from BMI 29.5 derived at D2 from a filled height (5'4") and a
filled weight (172 lb). Neither input was measured
  needs: a measured height and a measured weight. This one is the more robust of the pair —
  at 172 lb, heights from about 5'4" to 5'6" all land in the overweight band — but the note's
  own F8 records that 5'3" gives BMI 30.5 and moves this to obesity (E66.9), one inch away

Z68.29 — BMI 29.0-29.9, from the same filled height and filled weight
  needs: a measured height. The band is the invention carried to one decimal place: 5'3" gives
  30.5 and Z68.30, and nothing in the finished note distinguishes the two

R03.0 — the elevated reading 138/84, filled at F1
  needs: a measured blood pressure. The code's own tabular note asks for "an episode of
  elevated blood pressure"; a filled value records no episode, which is why this is proposed
  marked rather than asserted
```

**The note declines to code these three and this worksheet proposes them.** Its Assessment says
the BMI *"is not coded, because both the height and the weight it rests on are filled, and a
code may not rest on a generated value."* That was the rule and it is not the rule now — a
filled-anchored code is proposed marked rather than withheld, so that the note and this
worksheet cannot hold different answers about one number. The marks above are what the old
refusal was protecting, carried on the code rather than applied against it.

**Every filled value is accounted for.** F1 supports `R03.0`, marked. F6, F7 and F8/D2 support
`E66.3` and `Z68.29`, both marked. **F2 (HR 98), F3 (T 100.9 °F), F4 (RR 20) and F5 (SpO2 95%)
support no proposed code**: 98 is not tachycardia and 20 is not tachypnea in an adult, so
`R06.82` is not reached; 95% on room air is not hypoxemia; and the fever code `R50.9` rests on
the given history rather than on F3, so it is unmarked. F9–F24 are inferred medication detail,
social and family history, filled normal exam and ROS, and declared administrative values —
where a code touches one of them (`Z79.899` on the statin) the underlying fact is given and only
the detail is filled, so the code is unmarked.

```
--- NOT CODED, NOTHING ESTABLISHED IT ---

COVID-19 pneumonia / lower respiratory involvement, suspected on diminished breath sounds at
both bases in a SARS-CoV-2-positive patient; chest x-ray ordered, no result recorded
  NOT CODED: J12.82  Pneumonia due to coronavirus disease 2019
  needs: a chest film that resulted. Clear apices, no crackles, no egophony, no dullness and
  an SpO2 of 95% argue against it; the exam does not settle it
  proposed instead: U07.1  COVID-19 — already proposed above on the positive test

Acute pyelonephritis, suspected on right costovertebral angle tenderness with fever and
chills; urinalysis, microscopic urinalysis and urine culture all sent, none resulted
  NOT CODED: N10  Acute pyelonephritis
  needs: a urinalysis or culture that resulted, and a creatinine
  proposed instead: R39.851  Costovertebral (angle) tenderness, right side

Urinary tract infection, suspected alongside the above and argued partly against by the absence
of dysuria, frequency and hematuria and by an alternative documented cause for the fever
  NOT CODED: N39.0  Urinary tract infection, site not specified
  needs: a urinalysis or culture that resulted
  proposed instead: R39.851  Costovertebral (angle) tenderness, right side

Group A streptococcal pharyngitis, suspected on sore throat with pharyngeal erythema; rapid
streptococcal test sent, no result recorded
  NOT CODED: J02.0  Streptococcal pharyngitis
  needs: a rapid strep or culture that resulted. Prominent cough, coryzal sinus pain and absent
  cervical lymphadenopathy already argue against it
  proposed instead: J02.9  Acute pharyngitis, unspecified

Influenza, suspected on the same febrile respiratory syndrome in a patient whose vaccinations
are not up to date; influenza test sent, no result recorded
  NOT CODED: J11.1  Influenza due to unidentified influenza virus with other respiratory
    manifestations
  needs: an influenza test that resulted. The descriptor asserts influenza even in its
  unidentified-virus form; the positive SARS-CoV-2 result argues against it but co-infection is
  not excluded
  proposed instead: U07.1  COVID-19 — already proposed above

Respiratory syncytial virus infection, tested and displaced by the positive SARS-CoV-2 result;
no RSV result recorded
  NOT CODED: B97.4  Respiratory syncytial virus as the cause of diseases classified elsewhere
  needs: an RSV test that resulted
  proposed instead: U07.1  COVID-19 — already proposed above

Acute bacterial rhinosinusitis, suspected on sinus pain with headache
  NOT CODED: J01.90  Acute sinusitis, unspecified
  needs: 10 days of persistence or a double-worsening pattern, or purulent nasal discharge on
  exam. At two days with no purulent discharge observed, none of the three is present
  proposed instead: U07.1  COVID-19 — the sinus pain is attributed to the established viral
  illness, and R51.9 codes the headache

Cholelithiasis or biliary colic, suspected on right upper quadrant pain with an alkaline
phosphatase of 136; no right upper quadrant ultrasound obtained
  NOT CODED: K80.20  Calculus of gallbladder without cholecystitis without obstruction
  needs: a right upper quadrant ultrasound. A negative Murphy's sign, a non-colicky pain
  description and no fatty-food trigger argue against it without excluding it
  proposed instead: R10.11  Right upper quadrant pain, with R74.8 for the enzyme

Nephrolithiasis or renal colic, suspected on right costovertebral angle tenderness alone
  NOT CODED: N23  Unspecified renal colic
  needs: imaging that reports a calculus. The abdominal film showed stool and reported none,
  the pain is not described as colicky, and no hematuria is reported
  proposed instead: R39.851  Costovertebral (angle) tenderness, right side
```

---

## 5. E/M level — supporting elements only

**No level is selected**, and none should be read into what follows. The elements are offered so
the clinician can assign one. **The MDM phrasing below is recalled — no coding guidelines ship
in this repo and nothing here verifies it.**

**Problems addressed.** Fourteen differential entries with rationale attached. Two are settled
by results obtained today (COVID-19 on a positive test, constipation on an abdominal film). Two
are supported and treated (left nonsuppurative otitis media, acute pharyngitis). **Five could
not be excluded and each drove an order**: COVID-19 pneumonia, pyelonephritis, urinary tract
infection, cholelithiasis, and the statin-associated enzyme elevation. Two chronic problems are
carried and bear on the prescribing (GERD, osteoarthritis), and one chronic problem is under
long-term drug therapy that is itself a candidate cause of the abnormal enzymes.

**Data reviewed and ordered.** Two results returned and reviewed today (SARS-CoV-2, abdominal
radiograph) plus two abnormal laboratory values (AST 48, ALP 136). Twelve further studies
ordered with no result recorded, each attached to a named differential entry and each with a
follow-up mechanism stated.

**Risk.** Two prescribing conflicts are named against documented findings rather than dissolved
— acetaminophen against elevated liver enzymes, with the daily ceiling lowered to 2 g and the
course capped; and ibuprofen against documented GERD, epigastric and right upper quadrant
tenderness, elevated enzymes and unresolved flank tenderness with no creatinine recorded. A
third is a contingency to resolve in advance: a documented prednisone allergy against the
standard corticosteroid escalation should the COVID-19 progress. An antibiotic contingency is
worked against a six-drug allergy list with nitrofurantoin specifically excluded on
pharmacologic grounds.

**The undiagnosed problems are the weight-bearing element.** An acute illness with systemic
symptoms, plus a flank finding and a cholestatic enzyme pattern neither of which the encounter
could settle, is not a low-complexity presentation however routine the visit read.

**Time is not available as a basis.** The start and end times are estimated (F24), not recorded,
so a time-based level would rest on a filled value and would need a `SOURCE` mark it cannot
carry into a level selection.
