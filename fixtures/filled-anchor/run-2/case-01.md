# case-01

Codes below are **proposed**, not asserted. Verify before entry anywhere.

Every ICD-10 code on this worksheet was looked up in `reference/icd10cm-2026.sqlite` with `tools/icd10_lookup.py`, and every descriptor is the verbatim official string returned by that lookup. CPT is **not** in that database, so every CPT code here reads `verify this number`.

---

## Step 1 — filled and derived values

The tier block is present, so the source of every vital and body measurement is recoverable.

`FILLED·asserted` gives these vitals and body measurements as filled:

| Value | Filled |
| --- | --- |
| BP | 138/86 |
| HR | 92 |
| T | 98.4 °F |
| RR | 18 |
| SpO2 | 96% on room air |
| Height | 5'10" (70 in) |
| Weight | 185 lb |

`DERIVED` carries one value with a filled input:

- **BMI 26.5** = 703 × 185 / 70², derived from the filled height **and** the filled weight. Both inputs filled, so the BMI is treated as filled here.

The other `DERIVED` entries — pack-years 24, Patient Time, visit duration 0:35 — carry no filled input and support no diagnosis code. Pack-years rests on the given tobacco history, and the two Medatrax values are administrative.

`FILLED·proposed` is the whole plan: orders, drugs, counseling, follow-up intervals, and the line "All ICD-10-CM codes above." Nothing in it is a recorded finding, so nothing in it anchors a diagnosis code. It is where the procedures in step 2 come from, and the missing procedure note is reported in step 4.

**Codes carrying `SOURCE: filled` in step 3, from this list:** anything resting on BP 138/86, on the height, on the weight, or on BMI 26.5.

---

## Step 2 — codable elements

**Diagnoses documented in the Assessment**

| Element | Supporting text | Source |
| --- | --- | --- |
| Cutaneous abscess, plantar left great toe | "Swelling of the plantar aspect of the left great toe. The area is blanched, with the appearance of a collection or a retained object beneath the surface. Exquisitely tender to light palpation." | recorded |
| Pain in the left great toe | "Severity — 8/10 today"; "Antalgic gait, weight shifted off the left forefoot" | recorded |
| Residual foreign body, plantar soft tissue | "Residual foreign body in soft tissue, suspected, to be confirmed at drainage" | recorded, **unestablished** — step 4 |
| Diminished breath sounds in all four fields | "Breath sounds diminished in all four fields." | recorded |
| Nicotine dependence / tobacco use | "Tobacco use, 1 pack per day for 24 years." | recorded |
| Cannabis use | "admits marijuana use, frequency and route not documented" | recorded |
| Heartburn | "Occasional heartburn." | recorded |
| History of elevated troponin | "history of elevated troponin, etiology not documented" | recorded |
| Overweight | "Wt 185 lb → BMI 26.5" | **filled-anchored** |
| BMI band | "BMI 26.5" | **filled-anchored** |
| Elevated blood-pressure reading | "BP 138/86" | **filled-anchored** |

**Differential entries (7)** — cutaneous abscess; residual foreign body; plantar verruca; cellulitis of the left toe; acute gouty arthritis of the first MTP; osteomyelitis of the distal phalanx; diabetic foot infection. Coded in their own block below.

**Procedures documented in the Plan**

| Element | Supporting text | Coded |
| --- | --- | --- |
| Incision and drainage, plantar left great toe | "Incision and drainage of the plantar left great toe wound today, as documented." | yes — 10060 |
| Plain radiograph, left foot, two views | "Plain radiograph of the left foot, two views, before or at the time of drainage" | yes — 73620 |
| Smoking cessation counseling | "Smoking cessation counseling — impaired wound healing and post-procedure infection risk named as the immediate reason" | yes — 99406 |
| Foreign body exploration and removal | "Explore the cavity for a retained foreign body at the time of drainage." | no — nothing recovered; step 4 |
| Local digital block, lidocaine 1% | "Lidocaine 1% without epinephrine, up to 3 mL by local digital block infiltration" | no — anesthesia by the operating clinician is included in the procedure (**recalled**, not verified here) |
| Aerobic wound culture and sensitivity | "Send drainage for aerobic culture and sensitivity" | no — the note does not say whether the specimen is processed in-house or sent out; step 4 |
| Tdap 0.5 mL IM | "Tdap 0.5 mL IM, single dose today, **if** the last tetanus-containing vaccine was more than 5 years ago or is unknown" | no — conditional, not documented as given; step 4 |

Counseling, dressing instruction, offloading, return precautions and follow-up intervals are documentation of the visit rather than separately reportable procedures, and none is proposed.

---

## Step 3 — proposed codes

```
ICD-10  L02.612  Cutaneous abscess of left foot
  ANCHOR: "Swelling of the plantar aspect of the left great toe. The area is blanched,
           with the appearance of a collection or a retained object beneath the surface.
           Exquisitely tender to light palpation."
  SPECIFICITY: complete — laterality documented as left and site as foot; L02.61- has no
               digit-level axis, so the plantar great toe location cannot be coded further.
               The organism axis is an additional code rather than a further specification,
               and it is reported in step 4.
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  M79.675  Pain in left toe(s)
  ANCHOR: "Severity — 8/10 today"; "Aggravating — weight-bearing, direct pressure, light touch"
  SPECIFICITY: complete — laterality documented as left, site documented as toe;
               M79.675 has no further axis, and it does not distinguish which toe
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R06.89  Other abnormalities of breathing
  ANCHOR: "Breath sounds diminished in all four fields."
  SPECIFICITY: complete — "Other" is a residual for a finding that fits no named code,
               not an "unspecified" declining an axis. Diminished breath sounds have no
               named code in R06, and no obstructive or restrictive diagnosis is
               documented that would move this off R06.89
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  E66.3  Overweight
  ANCHOR: "Wt 185 lb → BMI 26.5"
  SOURCE: filled — the height (5'10", 70 in) and the weight (185 lb) are both declared
          filled in FILLED·asserted, and the BMI is derived from the two of them;
          confirm before submitting
  SPECIFICITY: complete — E66.3 is the overweight band itself and has no further axis.
               E66's own instruction to add a BMI code is met by Z68.26 below
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z68.26  Body mass index [BMI] 26.0-26.9, adult
  ANCHOR: "BMI 26.5"
  SOURCE: filled — BMI 26.5 derived from a filled height (5'10") and a filled weight
          (185 lb); neither was measured; confirm before submitting
  SPECIFICITY: complete — the adult band is the axis, age 36 is given and over 20 so the
               adult series applies rather than the pediatric Z68.5- percentiles, and
               26.5 lands inside 26.0-26.9
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R03.0  Elevated blood-pressure reading, without diagnosis of hypertension
  ANCHOR: "BP 138/86"; "a repeat blood pressure once the acute pain has resolved"
  SOURCE: filled — BP 138/86 is declared filled in FILLED·asserted. R03.0's own tabular
          note says the category records "an episode of elevated blood pressure", and a
          filled pressure records no episode; confirm before submitting
  SPECIFICITY: complete — R03.0 has no further axis, and it is the only elevated-reading
               code. The hypertension question is a clinical limit rather than an axis,
               and it is reported in step 4
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  F17.210  Nicotine dependence, cigarettes, uncomplicated
  ANCHOR: "Tobacco use, 1 pack per day for 24 years."; "current daily smoker, 1 pack per
           day for 24 years, 24 pack-years"
  SPECIFICITY: needs: documentation that the pattern meets dependence rather than use.
               The product axis is documented (cigarettes) and no nicotine-induced
               disorder is documented, so "uncomplicated" is supported; what is not
               documented is dependence itself. Z72.0 Tobacco use is the alternative,
               and F17.2- and Z72.0 are excludes1 to each other, so only one may stand
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  F12.90  Cannabis use, unspecified, uncomplicated
  ANCHOR: "admits marijuana use, frequency and route not documented"
  SPECIFICITY: needs: the use pattern — whether use, abuse (F12.1-) or dependence
               (F12.2-), which the descriptor's own "unspecified" leaves open. Frequency
               and route are documented as absent, and no cannabis-induced disorder is
               documented, so "uncomplicated" holds
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R12  Heartburn
  ANCHOR: "Occasional heartburn."; "heartburn + (occasional, stated)"
  SPECIFICITY: complete — R12 is a three-character code with no subdivisions and no
               further axis. No dyspepsia or reflux diagnosis is documented that would
               move it to K21.- or R10.13
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R79.89  Other specified abnormal findings of blood chemistry
  ANCHOR: "history of elevated troponin, etiology not documented; denies myocardial
           infarction"
  SPECIFICITY: complete — "Other specified" is the residual for an abnormal chemistry
               with no named code, and troponin has none in R79. It is not an
               "unspecified" descriptor. The missing value, date and setting would not
               change the code; they are reported in step 4 because they change what the
               finding means
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**CPT**

```
CPT  10060  Incision and drainage of abscess (eg, carbuncle, suppurative hidradenitis,
             cutaneous or subcutaneous abscess, cyst, furuncle, or paronychia);
             simple or single
  ANCHOR: "Incision and drainage of the plantar left great toe wound today, as documented."
  REQUIREMENTS THE CODE HINGES ON: simple or single versus complicated or multiple
           (10061). One lesion is documented — "Swelling of the plantar aspect of the left
           great toe" — and no packing, no loculation and no return for repacking is
           documented, which is what simple rests on here.
  SPECIFICITY: needs: a procedure note. GAPS records "no anesthesia recorded, no
               description of what was drained or extracted, no post-procedure wound
               description", so simple versus complicated is inferred from the plan text
               rather than from an operative description
  CONFIDENCE: verify this number — CPT is not in reference/icd10cm-2026.sqlite and this
              descriptor is recalled, not looked up
```

```
CPT  73620  Radiologic examination, foot; 2 views
  ANCHOR: "Plain radiograph of the left foot, two views, before or at the time of drainage
           — to look for a radiopaque foreign body and for early cortical change of the
           distal phalanx."
  REQUIREMENTS THE CODE HINGES ON: view count. Two views are documented, which is 73620
           rather than 73630 (complete, minimum 3 views).
  SPECIFICITY: needs: whether the film was obtained during this encounter and who
               interpreted it. "Labs/Tests today" states no imaging result is available,
               so this is an order. A professional-component modifier, or no professional
               charge at all, turns on facts the note does not carry
  CONFIDENCE: verify this number — CPT is not in reference/icd10cm-2026.sqlite and this
              descriptor is recalled, not looked up
```

```
CPT  99406  Smoking and tobacco use cessation counseling visit; intermediate,
             greater than 3 minutes up to 10 minutes
  ANCHOR: "Smoking cessation counseling — impaired wound healing and post-procedure
           infection risk named as the immediate reason, ahead of the long-term one.";
           "quitline referral offered, nicotine replacement therapy offered,
           wound-healing rationale given"
  REQUIREMENTS THE CODE HINGES ON: time spent. The note documents the content of the
           counseling and not its duration.
  SPECIFICITY: needs: counseling time in minutes. Over 10 minutes is 99407; 3 minutes or
               less is not separately reportable at all, so the undocumented time decides
               whether any code stands
  CONFIDENCE: verify this number — CPT is not in reference/icd10cm-2026.sqlite and this
              descriptor is recalled, not looked up
```

### Differential

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

ICD-10  L02.612  Cutaneous abscess of left foot   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R22.42  Localized swelling, mass and lump, left lower limb   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  B07.0  Plantar wart   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  L03.032  Cellulitis of left toe   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M10.072  Idiopathic gout, left ankle and foot   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M79.675  Pain in left toe(s)   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z13.1  Encounter for screening for diabetes mellitus   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

Which entry each code carries, named rather than re-quoted, in the note's own order:

1. *Cutaneous abscess of the left foot, plantar great toe* — **L02.612**. Favored, and the only differential code also proposed for entry, because the exam established it and the drainage is being done today.
2. *Residual foreign body of the plantar soft tissue* — **R22.42**, not M79.5. The entry is co-favored and drives the plan, and the descriptor "Residual foreign body in soft tissue" asserts an object nothing has yet found. What the encounter documents is the localized swelling. M79.5 is in step 4.
3. *Plantar verruca* — **B07.0**. Argued against, coded at the level the note argues.
4. *Cellulitis of the left toe* — **L03.032**. Argued against on the absence of spreading erythema, warmth and streaking, and on the afebrile temperature.
5. *Acute gouty arthritis of the first MTP (podagra)* — **M10.072**. Podagra is an inclusion term on M10, and the left ankle-and-foot digit is the site axis the entry names.
6. *Osteomyelitis of the distal phalanx* — **M79.675**, not M86.9. A radiograph was ordered on this entry and nothing resulted, so the code carrying the entry is the documented pain. M86.9 is in step 4.
7. *Diabetic foot infection* — **Z13.1**. The entry exists because an indolent foot lesion raises **undiagnosed** diabetes, so what the encounter documents is a screening decision. The E11 code is in step 4.

Entries 2, 6 and 7 are where the uncertainty limit bites: each names a condition only a result could establish — a film, a bone biopsy, a glucose or A1c — and each ordered that result without having it. Entries 3, 4 and 5 name conditions a clinician establishes on examination rather than on a result, so they carry their own codes.

---

## Step 4 — what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
Causative organism of the abscess. L02 carries "code to identify organism (B95-B96)";
the culture was sent and "No wound culture, radiograph or laboratory result is available
at the time of this note."
  affects: L02.612

Whether the tobacco pattern meets dependence rather than use — pack-years and daily use
are documented, dependence criteria are not. F17.2- and Z72.0 are excludes1 to each other.
  affects: F17.210

Cannabis use pattern — "frequency and route not documented", and nothing distinguishes
use from abuse or dependence.
  affects: F12.90

The prior troponin value, the date, and the setting in which it was drawn.
  affects: R79.89

Character of the diminished breath sounds — spirometry with bronchodilator response is
ordered in the Plan and has no result, so no obstructive or restrictive diagnosis exists.
  affects: R06.89

A procedure note for the incision and drainage — anesthesia given, what was drained,
whether the cavity was packed, single versus multiple. GAPS records all four as absent.
  affects: 10060

Whether the foot radiograph was obtained during this encounter, and who interpreted it.
  affects: 73620

Smoking cessation counseling time in minutes.
  affects: 99406

Whether the wound culture is processed in-house or sent to an outside laboratory. Nothing
in the note says, so no laboratory code is proposed on either side of that question.
  affects: no proposed code — it decides whether one exists

--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
R03.0 — BP 138/86, filled. FILLED·asserted declares the pressure filled, and the note
attributes the stage 1 reading to acute 8/10 pain in a patient who can barely walk.
  needs: a measured pressure, and the recheck the Plan already schedules once the pain
         has resolved. R03.0's own tabular note wants "an episode of elevated blood
         pressure"; a generated number is not an episode

E66.3 — Overweight, from BMI 26.5 derived from a filled height (5'10", 70 in) and a
filled weight (185 lb). Neither was measured.
  needs: a measured height and weight. This code is the more robust half of the pair —
         at 185 lb every height from 5'6" to 6'0" lands in the overweight band, so the
         invented inch is not what produced E66.3

Z68.26 — Body mass index [BMI] 26.0-26.9, adult, from the same filled height and filled
weight. This code is the exposed half of the pair.
  needs: a measured height. One inch moves it in either direction — 5'11" gives BMI 25.8
         and Z68.25, 5'9" gives BMI 27.3 and Z68.27. Nothing in the finished note
         distinguishes any of the three

HR 92, T 98.4 °F, RR 18 and SpO2 96% on room air are filled and support no code. All four
are within range for a 36-year-old adult; RR 18 does not reach R06.82 Tachypnea, and the
afebrile temperature is used in the Assessment to argue against cellulitis and
osteomyelitis rather than to code anything.

--- NOT CODED, NOTHING ESTABLISHED IT ---
Residual foreign body of the plantar soft tissue, suspected on onset at work with a
mechanism the patient cannot recall, an indolent one-month course, and "the appearance
that something may be below the surface"; radiograph ordered and exploration planned, no
result and no operative finding
  NOT CODED: M79.5  Residual foreign body in soft tissue
  needs: a radiograph showing a radiopaque object, or an object actually recovered at
         drainage. The Education section states outright that a negative film does not
         exclude a radiolucent object, so only the exploration settles it
  proposed instead: M79.675  Pain in left toe(s), with L02.612  Cutaneous abscess of left
         foot for the collection itself
  note: the note's own Final diagnosis field carries M79.5 as "suspected, to be confirmed
         at drainage". That field is a field and something goes in it; this worksheet
         withholds the code because the descriptor asserts an object nothing has found.
         Resolve the two before entry

Osteomyelitis of the distal phalanx, suspected on one month of unresolved focal foot
infection in a 24 pack-year smoker; foot radiograph ordered on this basis, no result
  NOT CODED: M86.9  Osteomyelitis, unspecified
  needs: a film that resulted showing early cortical change, or a bone biopsy. The note
         itself makes this the working diagnosis "if the wound fails to close after
         drainage"
  proposed instead: M79.675  Pain in left toe(s)

Diabetic foot infection, considered because an indolent foot lesion in an adult raises
undiagnosed diabetes; screening recommended on BMI 26.5 and age 36, hemoglobin A1c
deferred to the 2-4 week non-acute follow-up
  NOT CODED: E11.622  Type 2 diabetes mellitus with other skin ulcer
  needs: a hemoglobin A1c or a fasting glucose. The Assessment argues against the
         neuropathic picture on "fully preserved and severe pain sensation", and no
         glucose of any kind exists in this encounter
  proposed instead: Z13.1  Encounter for screening for diabetes mellitus, carried on the
         differential line above. The screening is recommended rather than performed
         today, so it is not proposed for entry either

Hypertension, raised only by a single filled reading of 138/86 in the stage 1 range
  NOT CODED: I10  Essential (primary) hypertension
  needs: readings on separate occasions that the clinician documents as hypertension. No
         single reading diagnoses hypertension, filled or measured, so this is a clinical
         limit rather than a provenance one and marking does not reach it
  proposed instead: R03.0  Elevated blood-pressure reading, without diagnosis of
         hypertension, marked SOURCE: filled above

Removal of a retained foreign body, planned as exploration of the cavity at the time of
drainage, with no operative finding recorded
  NOT CODED: 10120  Incision and removal of foreign body, subcutaneous tissues; simple
  needs: an operative note recording that an object was found and removed. Exploration
         that finds nothing is not a removal
  proposed instead: 10060 for the drainage itself
  CONFIDENCE: verify this number — CPT is not in reference/icd10cm-2026.sqlite

Tetanus-containing vaccine administration, written conditionally — "single dose today,
if the last tetanus-containing vaccine was more than 5 years ago or is unknown"
  NOT CODED: 90715 Tdap vaccine, 7 years or older, for intramuscular use, and its
         administration code 90471
  needs: the date of the last tetanus-containing dose, and documentation that the vaccine
         was actually given. GAPS records the immunization date as unknown while a wound
         procedure is being done today
  proposed instead: nothing — the encounter documents a decision rule, not an
         administration
  CONFIDENCE: verify this number — CPT is not in reference/icd10cm-2026.sqlite
```

---

## Step 5 — E/M supporting elements

No E/M level was requested, and none is selected here. The elements are offered so the clinician can assign one. **The MDM framing below is recalled; nothing in this repo verifies it, and no guideline text ships here.**

**Problems addressed.** The differential runs seven deep and is where this element is documented. One acute problem with a procedure performed (the abscess); one undiagnosed problem the encounter could not exclude and which drove an order (osteomyelitis, radiograph ordered on that basis, becoming the working diagnosis if the wound fails to close); one unresolved question the procedure itself is meant to answer (the retained foreign body); and four chronic or incidental problems reaching the Plan from the history rather than the complaint — tobacco at 24 pack-years, cannabis use, heartburn, and a prior elevated troponin with no records retrieved.

**Data reviewed and ordered.** Foot radiograph, two views. Aerobic wound culture with sensitivity reporting methicillin resistance. Hemoglobin A1c and lipid panel with 10-year ASCVD risk estimation. Spirometry with bronchodilator response. Retrieval of outside cardiology or emergency department records for the prior troponin — an order for records held elsewhere, not a test. No result of any kind was available at the time of the note, so every one of these is an order rather than a review.

**Risk.** A minor procedure with identified risk factors, plus prescription drug management. The procedure is incision and drainage under local digital block. Prescription management includes sulfamethoxazole-trimethoprim chosen for community MRSA coverage with a documented narrowing plan, famotidine, and a conditional Tdap. The named risk factors are 24 pack-years of current smoking against wound healing, and a documented drug-versus-condition conflict answered rather than dissolved: the NSAID is withheld for the documented heartburn and the prior elevated troponin, with acetaminophen substituted and the substitution explained to the patient.

---

## Accounting

Every value the FILLED block declared, and what it supports:

| Filled value | Supports |
| --- | --- |
| BP 138/86 | R03.0, marked and listed under `CODED, ANCHOR WAS FILLED`. Does not support I10 |
| HR 92 | no code |
| T 98.4 °F | no code |
| RR 18 | no code — does not reach R06.82 |
| SpO2 96% on room air | no code |
| Height 5'10" (70 in) | E66.3 and Z68.26, both marked and both listed |
| Weight 185 lb | E66.3 and Z68.26, both marked and both listed |
| BMI 26.5 (derived, both inputs filled) | E66.3 and Z68.26, both marked and both listed |

Every hedged element in the Assessment, and what became of it: the abscess is coded L02.612; the residual foreign body, the osteomyelitis and the diabetic foot infection are each in `NOT CODED, NOTHING ESTABLISHED IT` with the code the encounter does document proposed in its place; the verruca, the cellulitis and the gout carry their own codes on the differential and are proposed for entry nowhere.

**10 ICD-10 codes proposed for entry, 3 CPT codes proposed, 7 differential codes documenting MDM and proposed for entry nowhere.**
