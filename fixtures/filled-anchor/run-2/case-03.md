# case-03

## Step 1 — the FILLED and DERIVED lines, read first

**DERIVED**

- Height 61 in = 5 ft × 12 + 1 in — inputs: Ht 5'1", **given**
- BMI 20.4 = 703 × 108 ÷ 61² — inputs: height 61 in and Wt 108 lb, **both given**
- BMI band Z68.20 (20.0–20.9, adult) from BMI 20.4 — input: the derived BMI, itself from two given inputs
- Patient Time = Adult (18 – 60) Hours, from age 57 — age is given outright
- Symptom duration ≥ 7 days, from the visit one week ago to today — both endpoints given
- Pack-years **NOT derivable** — 1 ppd given, duration not. No value exists, so nothing codes off it

**FILLED·asserted** — every entry, with the vital/measurement question answered explicitly

- Home meds lisinopril 20 mg PO daily and hydrochlorothiazide 25 mg PO daily — inferred; no med rec
- Three-generation family history, expanded from the given hypertension, tobacco use and age
- Social history — marital status Married, inferred from age 57
- Social history — occupation, education, alcohol, nutrition, fitness, sleep, spiritual clauses
- ROS negatives across all systems
- Exam filled as normal: general appearance, oropharynx, lymph nodes, tympanic membranes, canal
  edema and discharge, abdomen, neuro, psych, absence of secondary cellulitis, absence of edema
  and murmur
- Race/Ethnicity, Primary Payment Method, Interaction Level, Course — declared administrative values
- Dog kept in the home is recorded in this block as a **GIVEN, not filled**

**The tier block states outright: `NO VITAL OR BODY MEASUREMENT WAS FILLED.`** BP 147/81, HR 59,
T 97.6 °F, RR 18, SpO2 98%, Ht 5'1" and Wt 108 lb are all given, and BMI 20.4 is derived from two
given inputs.

**Values whose codes carry `SOURCE: filled`: none.** Every proposed code below rests on given text
or on a derived value with no filled input, so no code in this worksheet takes a sixth part, and
the step-4 `CODED, ANCHOR WAS FILLED` block is empty by measurement rather than by omission. This
includes `Z68.20`, which is the sharpest instance of the rule and does not fire here: the height
was measured, so the band code is not sitting on an invented inch.

**FILLED·proposed** — none of it supports a proposed code. The plan items, the screening list and
the follow-up interval are orders and counseling, not documented procedures. One entry does bear on
step 3: *"Differential entries not stated by the clinician — canine sarcoptic mange, delusional
infestation/formication, asteatotic eczema, systemic pruritus, eczematous otitis externa, contact
dermatitis."* Six of the seven differential entries are the upstream skill's, not the clinician's;
that is recorded at the head of the differential block, where those codes live.

## Step 2 — codable elements

Diagnoses, from the Assessment:

| Element | Support | Mark |
| --- | --- | --- |
| Scabies | clinician's stated working and final diagnosis | given |
| Generalized itching | HPI, ROS Skin, Assessment | given |
| Crawling sensation in the ears | CC, HPI, ROS ENT and Psych | given |
| Xerosis of both ankles | Objective Skin, final diagnosis list | given |
| Essential hypertension | PMH, and the final diagnosis list | given (charted history) |
| Bradycardia, HR 59 | Objective vitals, Assessment paragraph | given vital |
| Cigarette smoking, 1 ppd | PMH/SH | given |
| BMI 20.4 band | derived from a given height and a given weight | given for this purpose |
| Substance use disorder | PMH, substance and status absent | given but incomplete |
| Status post total hysterectomy | PSH | given |
| Status post cholecystectomy and appendectomy | PSH | given |

Procedures, from the Plan and Objective: **none performed.** *"Labs/Tests today: No new testing
today. No skin scraping, no dermoscopy and no laboratory studies are recorded in the source."* The
skin scraping, dermoscopy, 12-lead ECG, TSH and the deferred pruritus panel are all orders with no
result attached, and the permethrin, hydroxyzine, triamcinolone and mineral oil are prescriptions
rather than administrations. Nothing here earns a procedure code.

## Step 3 — proposed codes

```
ICD-10  B86  Scabies
  ANCHOR: "Scabies — the clinician's documented working diagnosis, and a given." and
          "Final diagnosis: Scabies — B86."
  SPECIFICITY: complete — B86 carries no subdivision at all; the tabular returns it billable with
    no child codes, so there is no laterality, severity or organism axis left to document
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  L29.9  Pruritus, unspecified
  ANCHOR: "Skin: generalized itching +, excoriations +, dry skin +" and
          "Location generalized itching with both ear canals the site she volunteers first"
  SPECIFICITY: needs: site — the descriptor's open axis is the sited siblings L29.0 Pruritus ani,
    L29.1 Pruritus scroti, L29.2 Pruritus vulvae and L29.3 Anogenital pruritus, unspecified. The
    note documents generalized itching, so none of them applies and the axis stays open
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R20.2  Paresthesia of skin
  ANCHOR: "ENT: itching in both ear canals +, sensation of movement in the ears +" and
          CC: "I itch, and I can feel [insects] in my ears."
  SPECIFICITY: complete — Formication is R20.2's own inclusion term, which is the documented
    finding, and the code carries no site or laterality axis to narrow
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  L85.3  Xerosis cutis
  ANCHOR: "Xerosis of both ankles."
  SPECIFICITY: complete — L85.3 has no site, laterality or severity axis, so the bilateral ankle
    distribution the exam records has nowhere in the code to go
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  I10  Essential (primary) hypertension
  ANCHOR: "PMH/PSH: Hypertension." and "essential hypertension I10, uncontrolled at today's
          reading"
  SPECIFICITY: complete — I10 has no further axis; ICD-10-CM does not stage or grade essential
    hypertension, and "uncontrolled" is not a codable axis of it
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: this rests on the charted history, not on today's BP 147/81. A single reading does not
    diagnose hypertension; the reading is what makes the documented disease uncontrolled
```

```
ICD-10  R00.1  Bradycardia, unspecified
  ANCHOR: "VS: BP 147/81 · HR 59" and "HR 59 is below the normal range."
  SPECIFICITY: needs: the rhythm characterized — the 12-lead ECG already in the Plan is what
    separates a sinus bradycardia from atrioventricular block (I44.-) or sick sinus syndrome
    (I49.5). Note the limit: sinus, sinoatrial and vagal bradycardia are all inclusion terms of
    R00.1 itself, so a resulted ECG may confirm the code rather than move it
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  F17.210  Nicotine dependence, cigarettes, uncomplicated
  ANCHOR: "Current tobacco use, 1 pack per day; duration not recorded." and
          "Tobacco: current cigarette smoker, 1 pack per day (given)"
  SPECIFICITY: complete — the product is documented as cigarettes, and "uncomplicated" is the
    documented state: no remission (F17.211), no withdrawal (F17.213) and no other nicotine-induced
    disorder (F17.218) is recorded. The missing smoking duration is an LDCT eligibility question,
    not an axis of this code
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z68.20  Body mass index [BMI] 20.0-20.9, adult
  ANCHOR: "Ht 5'1" (61 in) · Wt 108 lb → BMI 20.4"
  SPECIFICITY: complete — BMI 20.4 falls inside the 20.0-20.9 band, and age 57 satisfies the
    tabular's own note that "BMI adult codes are for use for persons 20 years of age or older",
    so the adult/pediatric axis is settled and the band has no further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: no SOURCE line, and this is the code where that has to be checked rather than assumed.
    The height was measured and the weight recorded, so the band is not a readout of an invented
    inch. Had either been filled, one inch would have moved this code
```

```
ICD-10  F19.20  Other psychoactive substance dependence, uncomplicated
  ANCHOR: "Substance use disorder — substance not specified in the source." and
          "the source records `sud` with no substance and no status, so the substance, the
          severity and whether it is current or remote are all undocumented; confirm before this
          code is entered"
  SPECIFICITY: needs: the substance, the severity and the remission status — a named substance
    takes F10-F16 or F18 rather than the F19 residual; a mild disorder takes F19.1- (abuse), since
    F19.20's own inclusion terms are the moderate and severe forms; and a remote disorder takes
    F19.21. Three open axes, all of them absent from the source
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z90.710  Acquired absence of both cervix and uterus
  ANCHOR: "Past surgical: appendectomy, cholecystectomy, total hysterectomy."
  SPECIFICITY: complete — total hysterectomy is documented, and "Status post total hysterectomy"
    is this code's own inclusion term. The axis Z90.71- opens is which organ remains, and the
    partial forms (Z90.711 uterus removed with cervical stump, Z90.712 cervix removed with uterus
    remaining) are both excluded by the word "total"
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z90.49  Acquired absence of other specified parts of digestive tract
  ANCHOR: "Past surgical: appendectomy, cholecystectomy, total hysterectomy." and
          "Abdomen: Soft, non-tender, non-distended. Well-healed surgical scars."
  SPECIFICITY: complete — this is a residual rather than an unspecified code. Within Z90.4 the only
    sited child is Z90.41- (pancreas), and neither the gallbladder nor the appendix has a code of
    its own, so both procedures land here and no further axis exists to document
  CONFIDENCE: verified against ICD-10-CM FY2026
```

### CPT

**No CPT procedure code is proposed.** Nothing was performed today — the Objective records *"No new
testing today"* — and every study named in the Plan is an order without a result. No E/M level is
selected: step 5 makes that the clinician's, and none was requested here.

### Differential

**Six of these seven entries are the upstream skill's, not the clinician's.** The tier block lists
*"Differential entries not stated by the clinician — canine sarcoptic mange, delusional
infestation/formication, asteatotic eczema, systemic pruritus, eczematous otitis externa, contact
dermatitis"* under `FILLED·proposed`. Only the scabies entry is the clinician's own. That is
recorded here rather than as a line part, because these codes are documentation of reasoning and
none of them is proposed for entry on its own account.

**Four entries carry a code that is already proposed for entry above, on its own given anchor.**
Those lines read `ALSO PROPOSED ABOVE` rather than `NOT FOR ENTRY`, because writing `NOT FOR ENTRY`
on `B86` would refuse this encounter's final diagnosis. The three parts are unchanged.

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

Scabies — favored, and the clinician's stated diagnosis
ICD-10  B86  Scabies   ALSO PROPOSED ABOVE — for entry on its own anchor
  CONFIDENCE: verified against ICD-10-CM FY2026

Canine sarcoptic mange transmitted from the dog
ICD-10  B88.09  Other acariasis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
  (B88.0 is a header and not billable; B88.09 is its billable child, and its excludes2 for
   scabies (B86) is what makes this a distinct differential line rather than a restatement)

Delusional infestation (Ekbom syndrome) or drug-associated formication
ICD-10  R20.2  Paresthesia of skin   ALSO PROPOSED ABOVE — for entry on its own anchor
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOT CODED: F22  Delusional disorders — the descriptor asserts a psychiatric disease, and the
   encounter contains no psychiatric assessment. See step 4

Asteatotic (xerotic) eczema
ICD-10  L85.3  Xerosis cutis   ALSO PROPOSED ABOVE — for entry on its own anchor
  CONFIDENCE: verified against ICD-10-CM FY2026
  (L85.3's own inclusion term is "Dry skin dermatitis", and L30's excludes2 sends dry skin
   dermatitis here rather than to L30.8, so the residual dermatitis code is not the one to use)

Pruritus secondary to a systemic cause
ICD-10  L29.9  Pruritus, unspecified   ALSO PROPOSED ABOVE — for entry on its own anchor
  CONFIDENCE: verified against ICD-10-CM FY2026
  (The named candidates — cholestasis, chronic kidney disease, iron deficiency, thyroid disease,
   polycythemia, lymphoma — take no code here. Nothing in the encounter argues for any one of
   them and no study was obtained, so coding any would assert a disease the note explicitly
   leaves open)

Eczematous otitis externa from repeated digital trauma
ICD-10  H60.543  Acute eczematoid otitis externa, bilateral   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Allergic contact dermatitis
ICD-10  L23.9  Allergic contact dermatitis, unspecified cause   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

## Step 4 — what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
The substance, the severity, and whether use is current or in remission. A named substance moves
this out of the F19 residual entirely; a mild disorder is F19.1-; a remote one is F19.21
  affects: F19.20

The rhythm behind HR 59, characterized. The 12-lead ECG is already ordered; a conduction
abnormality reads I44.-, sick sinus syndrome reads I49.5, and a sinus bradycardia leaves the code
where it is
  affects: R00.1

A sited pruritus, if there is one. The descriptor leaves the site axis open and the sited siblings
are anogenital; generalized itching is what is documented, so this axis will most likely stay open
however well the next visit is written
  affects: L29.9

The scabies distribution, and a confirmatory study. The Assessment says it outright — "What would
ordinarily place it — burrows, finger web spaces, flexor wrists, axillae, periumbilical or genital
lesions — was not documented, so the diagnosis rests on the impression and not on a recorded
distribution." The code does not change, and this is the entry in this block that is not about an
axis: it is about what the record would need for B86 to rest on the exam rather than on the
impression
  affects: B86

Time spent on tobacco cessation counseling. "Smoking cessation counseling; cessation
pharmacotherapy offered" is documented with no duration, and the counseling CPT codes are
time-banded from 3 minutes. Without a documented time no cessation counseling code can be proposed
at all
  affects: no proposed code — this is a CPT that could not be written

Smoking duration. Not a coding axis, and it is carried here because it is the same bedside
omission: 1 ppd with no years means pack-years cannot be computed and LDCT eligibility cannot be
settled
  affects: no proposed code
```

```
--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
None. The tier block declares "NO VITAL OR BODY MEASUREMENT WAS FILLED", and BMI 20.4 is derived
from a given height (5'1") and a given weight (108 lb), so Z68.20 rests on measured inputs and
carries no SOURCE line. This block is empty because the note's own source record says so, not
because nothing was checked.
```

```
--- NOT CODED, NOTHING ESTABLISHED IT ---
Delusional infestation (Ekbom syndrome) or drug-associated formication, suspected on a crawling
sensation localized to the ears, self-inflicted excoriations, an admitted habit of digging in the
canals with fingernails, a documented substance use disorder, and failure to resolve one week
after a visit for the same complaint. The Assessment marks the entry "PROPOSED reasoning — verify
before use" and "not excludable on it either"
  NOT CODED: F22  Delusional disorders
  needs: a psychiatric assessment establishing a fixed false belief, or a substance history
    establishing current use of an agent that produces formication. Neither exists in this
    encounter, and the substance itself is undocumented
  proposed instead: R20.2  Paresthesia of skin
```

## Step 5 — E/M level

**Not selected, and not requested.** The supporting elements, offered for the clinician to map:

- **Problems addressed** — one chronic disease uncontrolled at today's reading (hypertension,
  BP 147/81), one new abnormal vital worked up rather than recorded (HR 59, with an ECG and a TSH
  ordered), and a dermatologic complaint on its second presentation in a week that the encounter
  could not place on the exam. The differential above is where that last one is documented: seven
  entries with rationale, two of which the note states are not excludable on the record as it
  stands.
- **Data reviewed or ordered** — no results exist to review. Ordered today: skin scraping or
  dermoscopy, 12-lead ECG, TSH, a repeat blood pressure with a home log, and a contingent pruritus
  panel. The medication reconciliation is itself outstanding data, and the Assessment turns on it.
- **Risk** — prescription drug management (permethrin, hydroxyzine, triamcinolone), an explicit
  decision *not* to start an antihypertensive on a single reading, and a named diagnosis in the
  differential that a second course of permethrin would delay.

**This phrasing is recalled.** No coding guideline ships in this repo, and `reference/icd10cm-2026.sqlite`
holds the tabular alone, so the mapping of these elements to an E/M level is the clinician's and
no section number is cited here.
