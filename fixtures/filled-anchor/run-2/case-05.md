# case-05

## Step 1 — filled and derived values held while reading the note

The note carries a tier block, so provenance is recorded rather than assumed.

`FILLED·asserted` — vitals and body measurements:

1. BP 146/84 — filled (FILLED·asserted 1)
2. HR 82 — filled (FILLED·asserted 2)
3. T 98.2 °F — filled (FILLED·asserted 3)
4. RR 18 — filled (FILLED·asserted 4)
5. SpO2 94% on room air — filled (FILLED·asserted 5)
6. Ht 5'10" (70 in) — filled (FILLED·asserted 6)
7. Wt 198 lb — filled (FILLED·asserted 7)
8. BMI 28.4 — filled, both inputs filled (FILLED·asserted 8)

`DERIVED`, checked for a filled input:

1. Pack-years 90 = 3 packs/day x 30 years — both inputs given (shorthand "3 ppd", 30 years). Not filled.
2. BMI 28.4 = 703 x 198 / 70^2 — **both inputs filled**, so this is treated as filled here. It is
   the derived value the rule exists for.
3. Patient Time = Gerontology, from the given age 68. Not filled, and codes nothing.
4. Visit length 0:25, from estimated start and end times — both filled, and codes nothing.
5. Antibiotic course day 2 of 7 — from the given "2 days". Not filled.

Two further filled entries are not vitals but are load-bearing for a code, and are carried into
step 3 with the same mark:

- `FILLED·asserted` 21 — type 2 as the diabetes type, inferred from age 68. The shorthand says
  only "dm". This is what `E11.9` rests on.
- `FILLED·proposed` 11 — smokeless tobacco cessation counseling. The note reads as a service
  delivered; the tier block records it as proposed by the upstream skill.

---

## Step 2 — codable elements

Diagnoses (Assessment):

| element | support | status |
| --- | --- | --- |
| Cutaneous abscess, left index finger, resolving | swelling with active drainage, Objective and Assessment | codable |
| Cellulitis of left finger, resolving | erythema at the base of the wound | codable |
| Acute viral upper respiratory infection | cough with nasal drainage | codable |
| Fingertip paresthesia | tingling at the tip of the left index finger | codable |
| Type 2 diabetes mellitus | PMH; **type** inferred | codable, filled-anchored on the type |
| COPD | PMH, inhaler regimen | codable |
| Personal history of prostate cancer | PMH, activity status undocumented | codable |
| Acquired absence of lung, part | absent left lower lobe breath sounds, s/p lobectomy | codable |
| Postprocedural state, hernia repair | PSH, well-healed right inguinal scar | codable |
| Personal history of nicotine dependence | former cigarette smoker, 90 pack-years | codable |
| Current smokeless tobacco dependence | currently uses smokeless tobacco | codable |
| Elevated blood-pressure reading | BP 146/84, addressed in the Plan | **filled-anchored** |
| Overweight | BMI 28.4 | **filled-anchored** |
| BMI band | BMI 28.4 | **filled-anchored** |

Differential entries (11), each coded in the differential block or refused in step 4.

Procedures (Plan and Objective):

- **No procedure performed.** "No point-of-care glucose, no imaging and no laboratory studies
  obtained today. No treatment administered in clinic today." No incision and drainage, no
  debridement, no in-clinic dressing change, no ECG.
- Smokeless tobacco cessation counseling — documented as delivered, **filled-anchored**.
- Wound culture and sensitivity — collected at the prior outside visit, not this encounter's
  service, and not resulted.

---

## Step 3 — proposed codes

```
ICD-10  L02.512  Cutaneous abscess of left hand
  ANCHOR: "left index finger with an area of swelling and active drainage"
  SPECIFICITY: complete — laterality documented as left, and L02.51- has no per-digit axis;
    the index finger is named in the note and is not an axis the code set offers
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  L03.012  Cellulitis of left finger
  ANCHOR: "erythema present around the base of the wound"
  SPECIFICITY: complete — laterality documented as left; L03.01- names the finger and has no
    per-digit or severity axis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J06.9  Acute upper respiratory infection, unspecified
  ANCHOR: "Acute viral upper respiratory infection, second problem. Supported by cough with
    nasal drainage"
  SPECIFICITY: needs: the specific upper respiratory site (sinusitis, pharyngitis, laryngitis),
    or an identified infectious agent for the B95-B97 additional code the tabular asks for
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R20.2  Paresthesia of skin
  ANCHOR: "positive tingling at the tip of the left index finger"
  SPECIFICITY: complete — R20.2 carries no site, laterality or severity axis, and "Tingling
    skin" is its own inclusion term
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  E11.9  Type 2 diabetes mellitus without complications
  ANCHOR: "PMH: type 2 diabetes mellitus"
  SOURCE: filled — the diabetes is given, the **type** is not. Tier block FILLED·asserted 21
    infers type 2 from age 68 and the absence of a type 1 marker; the shorthand says only "dm".
    Confirm before submitting
  SPECIFICITY: complete — no diabetic complication is documented anywhere in the encounter, so
    the without-complications axis is the one the note supports; the type axis rests on the
    inference named in SOURCE
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J44.9  Chronic obstructive pulmonary disease, unspecified
  ANCHOR: "chronic obstructive pulmonary disease" (PMH), with tiotropium and albuterol on the
    medication list
  SPECIFICITY: needs: the COPD subtype axis — J44.0 with acute lower respiratory infection or
    J44.1 with acute exacerbation. The note argues both against, and documents no baseline
    severity or spirometry
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z85.46  Personal history of malignant neoplasm of prostate
  ANCHOR: "prostate cancer, treatment and current activity status not documented"
  SPECIFICITY: complete — the site axis is documented as prostate and Z85.46 has no further
    axis. Whether a history code is the right family at all is a documentation question, not a
    specificity one, and is in step 4
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z90.2  Acquired absence of lung [part of]
  ANCHOR: "breath sounds absent in the left lower lobe, status post lobectomy"
  SPECIFICITY: complete — Z90.2 is the part-of-lung code and carries no laterality or lobe
    axis; the whole-lung absence would be a different code and is not what the note documents
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z98.890  Other specified postprocedural states
  ANCHOR: "Right inguinal region with well-healed surgical scar, no bulge or recurrent hernia
    palpated"
  SPECIFICITY: complete — an "Other specified" residual rather than an unspecified one: the
    hernia repair has no dedicated status code, and its inclusion term is "Personal history of
    surgery, not elsewhere classified"
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z87.891  Personal history of nicotine dependence
  ANCHOR: "Tobacco: former cigarette smoker, 3 packs per day for 30 years, quit date not
    documented"
  SPECIFICITY: complete — Z87.891 carries no product, quantity or quit-date axis. Its excludes1
    against F17.2- is a conflict rather than a missing axis, and is in step 4
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  F17.290  Nicotine dependence, other tobacco product, uncomplicated
  ANCHOR: "currently uses smokeless tobacco (chews), daily amount not reported"
  SPECIFICITY: complete — both axes are documented: the product is smokeless, which is the
    "other tobacco product" branch, and no nicotine-induced complication (withdrawal, disorder)
    is documented, which is the "uncomplicated" branch
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R03.0  Elevated blood-pressure reading, without diagnosis of hypertension
  ANCHOR: "VS: BP 146/84" and "146/84 today is above goal. Hypertension is not in his documented
    history and one reading does not diagnose it"
  SOURCE: filled — BP 146/84 is filled (tier block FILLED·asserted 1); nobody measured this
    pressure. The tabular's own note says the category records "an episode of elevated blood
    pressure", and a filled reading records no episode. Confirm before submitting
  SPECIFICITY: complete — R03.0 has no further axis; it carries neither a severity nor a
    reading-count axis, and the without-a-diagnosis condition is exactly what the Plan states
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  E66.3  Overweight
  ANCHOR: "Ht 5'10" (70 in), Wt 198 lb, BMI 28.4"
  SOURCE: filled — both inputs filled (height 5'10", weight 198 lb; FILLED·asserted 6, 7, 8).
    E66 carries "code to identify body mass index (BMI), if known" and a filled BMI is not
    known. Confirm before submitting
  SPECIFICITY: complete — E66.3 is the band itself; the BMI value is carried by the separate
    Z68 code E66's own use-additional-code note asks for, so no axis is left open on this line
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z68.28  Body mass index [BMI] 28.0-28.9, adult
  ANCHOR: "BMI 28.4"
  SOURCE: filled — derived from a filled height (5'10") and a filled weight (198 lb).
    FILLED·asserted 8 declares both. Confirm before submitting
  SPECIFICITY: complete — the band is fixed by the BMI value and Z68 has no further axis; the
    adult series is correct at age 68, since the tabular restricts Z68.5- to ages 2-19
  CONFIDENCE: verified against ICD-10-CM FY2026
```

CPT:

```
CPT     99406  Smoking and tobacco use cessation counseling visit; intermediate, greater than
               3 minutes up to 10 minutes
  ANCHOR: "Counseling on smokeless tobacco cessation delivered this visit: daily chewing tobacco
    maintains nicotine dependence, impairs wound healing directly, and carries oral and
    pharyngeal cancer risk. Cessation resources and quitline offered."
  SOURCE: filled — the counseling is a FILLED·proposed item (tier block FILLED·proposed 11),
    proposed by the upstream skill rather than recorded as performed. Confirm the counseling
    happened before submitting anything for it
  SPECIFICITY: needs: the counseling duration in minutes. 99406 requires more than 3 minutes,
    and more than 10 minutes is 99407; the note documents no time for the counseling
  CONFIDENCE: verify this number — CPT is not in this repo's code set and nothing here looked
    it up
```

**No E/M service code is proposed.** Selecting one is selecting a level, and step 5 does not do
that unprompted. The supporting elements are offered below.

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

Cutaneous abscess of the left index finger with surrounding cellulitis, FAVORED — coded for
entry above as L02.512 and L03.012. Not repeated here, because those two are for entry.

Paronychia — ICD-10-CM lists "Paronychia" as an inclusion term on L03.0, so this entry carries
the same code the favored entry does rather than one of its own.
ICD-10  L03.012  Cellulitis of left finger   NOT FOR ENTRY — the same number is proposed above
  from the documented cellulitis; enter it once, from there, not from this line
  CONFIDENCE: verified against ICD-10-CM FY2026

Felon, pulp space abscess of the distal phalanx — "Felon" is likewise an inclusion term on
L03.01, so this entry lands on the same code.
ICD-10  L03.012  Cellulitis of left finger   NOT FOR ENTRY — as above; one entry, from the
  proposed list
  CONFIDENCE: verified against ICD-10-CM FY2026

Flexor tenosynovitis — argued against by all four Kanavel signs recorded as absent. Those four
findings are declared filled (tier block FILLED·asserted 16), so the exclusion rests on a
generated exam. Confirm them at the bedside before relying on it.
ICD-10  M65.142  Other infective (teno)synovitis, left hand   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Diabetic sensory peripheral neuropathy contributing to the fingertip tingling — entertained as a
contributor, not as the sole explanation.
ICD-10  E11.42  Type 2 diabetes mellitus with diabetic polyneuropathy   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

COPD exacerbation — argued against by absent wheeze, no increased dyspnea, no increase in rescue
inhaler use and a saturation at his post-lobectomy baseline.
ICD-10  J44.1  Chronic obstructive pulmonary disease with (acute) exacerbation   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Community-acquired pneumonia — named rather than dismissed, given 90 pack-years and an absent
left lower lobe.
ICD-10  J18.9  Pneumonia, unspecified organism   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Acute viral upper respiratory infection, second problem — supported rather than argued against,
and coded for entry above as J06.9. Not repeated here.

Three entries carry no code on this line, because the code each would carry asserts something
the encounter never established. Each is named in step 4 with its number and its refusal
attached:
  Osteomyelitis of the distal phalanx     NOT CODED: M86.142  Other acute osteomyelitis, left hand
  Retained foreign body                   NOT CODED: S60.451A Superficial foreign body of left
                                            index finger, initial encounter
  Herpetic whitlow                        NOT CODED: B00.89   Other herpesviral infection
```

---

## Step 4 — what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
The wound culture and sensitivity result, which names the organism
  affects: L02.512 and L03.012. L02 carries "code to identify organism (B95-B96)"; the specimen
  exists and is pending from the Saturday visit, so this is a result to chase rather than a
  swab to send

The specific upper respiratory site, or an identified infectious agent
  affects: J06.9, whose own descriptor says unspecified

The COPD subtype and any baseline severity or spirometry
  affects: J44.9, whose own descriptor says unspecified

Distal sensory testing of the hand — monofilament, vibration, two-point
  affects: R20.2, and the differential E11.42. Nothing separates a local paresthesia adjacent to
  an infected wound from a diabetic polyneuropathy without it

Prostate cancer activity, treatment and surveillance status
  affects: Z85.46. If the disease is active, the encounter is coding a history of something the
  patient still has, and C61 is the code rather than a Z85 one

The smoking quit date, and which tobacco status the encounter is asserting
  affects: Z87.891 and F17.290. FY2026 puts these two in a mutual excludes1 — F17 excludes1
  "history of tobacco dependence (Z87.891)", Z87.891 excludes1 "current nicotine dependence
  (F17.2-)" — so the pair cannot both stand as written and the clinician has to settle which.
  The quit date is undocumented (GAPS 5) and is also what decides LDCT eligibility

The date and mechanism of the original wound
  affects: whether an injury code with an episode-of-care 7th character belongs alongside
  L02.512 at all. The patient recalls no injury (GAPS 9), and tetanus status is undocumented

The counseling duration in minutes
  affects: 99406 against 99407, which splits at 10 minutes

--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
R03.0 — BP 146/84, a filled blood pressure (FILLED·asserted 1)
  needs: a measured pressure. The Plan's 5-day recheck is that measurement. I10 is not proposed
  and would not be earned by one reading, filled or measured

Z68.28 — BMI 28.4 derived from a filled height (5'10") and a filled weight (198 lb)
  needs: a measured height and weight. One inch either way moves the band code — 5'9" gives 29.2
  and Z68.29, 5'11" gives 27.6 and Z68.27

E66.3 — the same two filled inputs
  needs: a measured height and weight. This one survives one inch and does not survive two: at
  198 lb, 5'8" gives BMI 30.1, which is obesity rather than overweight and takes Z68.30 with it

E11.9 — type 2 as the diabetes type, inferred rather than documented (FILLED·asserted 21)
  needs: the documented diabetes type, and any glycemic datum at all. There is no A1c, no
  glucose and no antidiabetic agent recorded in the source (FLAG 7)

99406 — cessation counseling recorded as a proposed plan item (FILLED·proposed 11)
  needs: documentation that the counseling was delivered, and how long it took

Filled values that support no code, accounted for rather than omitted:
  HR 82 and T 98.2 °F — normal, and code nothing
  RR 18 — upper-normal; not tachypnea, so no R06.82
  SpO2 94% on room air — the note addresses it as his expected post-lobectomy baseline rather
    than a new finding, so no hypoxemia code (R09.02) is proposed. A filled saturation would not
    earn one in any case
  Ht 5'10" and Wt 198 lb — they support no code of their own; what they support is the BMI pair
    above, where they are named

--- NOT CODED, NOTHING ESTABLISHED IT ---
Osteomyelitis of the distal phalanx, kept live by diabetes and a persistent fingertip
paresthesia; no radiograph and no probe-to-bone test performed
  NOT CODED: M86.142  Other acute osteomyelitis, left hand
  needs: a radiograph that resulted, a probe-to-bone test, or a bone biopsy. The Plan already
  contemplates imaging if improvement stalls, so this is the result to chase
  proposed instead: R20.2  Paresthesia of skin, and L03.012  Cellulitis of left finger

Retained foreign body in the left index finger, raised by an unwitnessed onset with no recalled
injury and no documented mechanism; the note says it cannot be excluded without imaging
  NOT CODED: S60.451A  Superficial foreign body of left index finger, initial encounter
  needs: imaging of the digit — a radiograph, or ultrasound for a radiolucent splinter. The
  wound date and mechanism are also undocumented, so the 7th character is unsettled even if
  imaging were positive
  proposed instead: L02.512  Cutaneous abscess of left hand

Herpetic whitlow, argued against by purulent drainage from a discrete wound rather than grouped
vesicles, and by clear improvement on antibacterial therapy; nothing tested for the virus
  NOT CODED: B00.89  Other herpesviral infection
  needs: a viral PCR or Tzanck preparation from a vesicle, if the picture ever changes to one.
  FY2026 also puts B00.89 in an excludes1 with L03.01, so it is one or the other and not both
  proposed instead: L03.012  Cellulitis of left finger
```

---

## Step 5 — E/M level

**Not asked for, so no level is selected and no E/M code appears above.** The supporting
elements, for the clinician to map:

- **Problems addressed** — an acute skin and soft tissue infection of the hand in a diabetic,
  improving but with two entries the encounter could not exclude (osteomyelitis, retained
  foreign body); a second acute problem (viral upper respiratory infection); an elevated blood
  pressure addressed without a diagnosis; and two chronic conditions bearing on both (type 2
  diabetes, COPD with an absent left lower lobe).
- **Data reviewed** — no new testing was obtained today. There is one outstanding external
  result, the wound culture and sensitivity from the Saturday walk-in visit, which is the
  trigger for narrowing therapy. Nothing else was ordered or reviewed this visit.
- **Risk** — prescription drug management: two oral antibiotics running concurrently with a
  stated narrowing trigger, plus a potassium and creatinine caution for
  sulfamethoxazole-trimethoprim in a 68-year-old with diabetes, and a basic metabolic panel
  proposed if therapy extends.

**This phrasing is recalled and nothing in this repo verifies it.** No coding guidelines ship
here; the database holds the ICD-10-CM tabular alone. The mapping from these elements to a level
is the clinician's.
