# case-02

Codes below are **proposed, not asserted**. Every one is a suggestion for the clinician to verify before it is entered anywhere.

---

## Step 1 — FILLED and DERIVED, read first

**`DERIVED`** carries five entries. Checked one at a time for a filled input:

| Derived value | Inputs | Any input filled? |
| --- | --- | --- |
| Pack-years 7.5 = 0.5 pack/day × 15 years | pack/day and duration, both given in the shorthand | No |
| BMI 24.0 = 703 × 131 ÷ 62² | Ht 62 in, Wt 131 lb | No — the tier block states both are given |
| Pulse pressure 60 = 121 − 61 | BP 121/61, given | No |
| Patient Time = Gerontology (60 and>) | age 71, given | No |
| Visit Time 0:25 = 12:34 − 12:09 | start given, end estimated | End time filled — supports no code |

**`FILLED·asserted`** — 43 entries, read in full. Not one is a vital or a body measurement. The block says so outright: *"NO VITAL OR BODY MEASUREMENT WAS FILLED IN THIS ENCOUNTER. The shorthand supplies BP, HR, T, RR, SpO2, height and weight, and every one of them is carried through unchanged."* The filled entries are history negatives, exam normals, inferred home medications, declared Medatrax fields, and the estimated end time.

**`FILLED·proposed`** — 19 entries, read in full. All are plan content — reassurance, referral redirect, vaccine schedule, education, follow-up intervals. None is a measured value. The last line, *"All ICD-10-CM codes above,"* names the note's own code proposals as filled; that is this skill's subject rather than an anchor for it, and every code below was re-derived from the note text and looked up independently.

**Filled vitals and body measurements: none. Value list is empty.**

**This is the case where the mark does not fire, and that is a finding rather than an omission.** BMI 24.0 sits one decimal from the `Z68.25` band, and had either input been filled, `Z68.24` would carry `SOURCE: filled` and a step-4 entry. Both are given, so it codes unmarked — see the `CODED, ANCHOR WAS FILLED` block in step 4, which is empty and says why.

---

## Step 2 — codable elements

**Diagnoses, from the Assessment**

| Element | Anchor source | Filled-anchored? |
| --- | --- | --- |
| Ganglion, right hand — favored final diagnosis | exam of the right thumb IP joint | No — given exam finding |
| Localized mass of the right upper limb, presenting sign pending tissue | HPI and exam | No — given |
| Immunizations not up to date | stated in PMH | No — given |
| BMI 24.0 | given height, given weight | No — both inputs given |
| Essential hypertension | PMH, and the continued lisinopril | No — given |
| Former nicotine use, 7.5 pack-years | SH and PMH | No — given |
| Seasonal allergic rhinitis | stated allergy history | No — given |
| Tubal ligation status | PSH | No — given |

**Differential entries, from the Assessment** — seven, all coded in their own block below.

**Procedures, from the Plan and Objective** — none performed. `Labs/Tests today` reads *"No new laboratory or imaging testing today. No specimen was taken and no result is available at the time of this note."* The vaccines in the Plan are written conditionally (*"if not previously given"*, *"annually"*, *"if Tdap has never been given"*) and the Follow-up line reads *"immunization catch-up if not completed today"* — so **no vaccine is documented as administered at this encounter**, and no administration code is proposed. This is raised in step 4.

**No element in this encounter is filled-anchored.**

---

## Step 3 — proposed codes

```
ICD-10  M67.441  Ganglion, right hand
  ANCHOR: "A small cyst is noted at the medial aspect of the interphalangeal joint of the
           right thumb. Mobile on palpation."
  SPECIFICITY: complete — laterality documented as right, and M67.44- carries site plus
           laterality as its only axes; the thumb IP joint is inside "hand" and the code
           set offers no digit-level child
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R22.31  Localized swelling, mass and lump, right upper limb
  ANCHOR: "Localized swelling, mass and lump, right upper limb (the presenting sign,
           pending tissue diagnosis)"
  SPECIFICITY: complete — laterality documented as right; R22.3- resolves only to
           limb and side, and there is no hand- or digit-level child beneath it
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z28.39  Other underimmunization status
  ANCHOR: "Immunizations not up to date (stated)."
  SPECIFICITY: complete — Z28.39 is the "Other" residual under Z28.3 and has no further
           axis of its own. Z28.3 carries a useAdditionalCode note asking for the reason
           the immunization was not carried out; nothing in the note documents one, so
           that sits in step 4 as a second code rather than as a more specific one
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z68.24  Body mass index [BMI] 24.0-24.9, adult
  ANCHOR: "Ht 62 in (5'2") · Wt 131 lb → BMI 24.0"
  SPECIFICITY: complete — the band is the code's only axis and 24.0 lands inside
           24.0-24.9; age 71 is given, which puts her in the adult series rather than
           the Z68.5- pediatric percentiles
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**No `SOURCE` line on `Z68.24`, and that is the checked answer rather than the default.** Both inputs are given — the tier block's `DERIVED` entry says *"BOTH INPUTS ARE GIVEN"* and its `FILLED·asserted` block says no body measurement was filled at all. A BMI computed from a recorded height and a recorded weight is a measurement, not an invention, and codes unmarked.

```
ICD-10  I10  Essential (primary) hypertension
  ANCHOR: "PMH — hypertension." and "Continue lisinopril 20 mg PO daily, ongoing — blood
           pressure is at goal at 121/61 for a 71-year-old; no change today."
  SPECIFICITY: complete — I10 has no further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**`I10` is earned here by the charted history, not by the reading.** BP 121/61 is a given, and a given pressure diagnoses hypertension no more than a filled one does. What supports `I10` is that the patient carries the diagnosis in her history and is on lisinopril for it.

```
ICD-10  Z87.891  Personal history of nicotine dependence
  ANCHOR: "Former smoker, 0.5 pack per day for 15 years, 7.5 pack-years."
  SPECIFICITY: complete — Z87.891 is a leaf with no further axis, and the excludes1 for
           current nicotine dependence (F17.2-) is satisfied: the note documents a former
           smoker in every place it names tobacco
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  J30.2  Other seasonal allergic rhinitis
  ANCHOR: "Environmental: seasonal allergies (stated), reaction pattern not documented."
  SPECIFICITY: needs: the specific seasonal allergen — the note records "seasonal
           allergies" with no trigger named. A documented pollen trigger moves this to
           J30.1
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z98.51  Tubal ligation status
  ANCHOR: "PSH — bilateral tubal ligation."
  SPECIFICITY: complete — Z98.51 has no further axis, and it carries no laterality
           element for the documented bilateral procedure to fill
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**Every code above was checked for billability against the shipped code set. All eight are billable; none is a header.**

---

### --- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

The Assessment runs seven entries. Five carry a code in this block; the other two are accounted for on their own lines below.

**Entry 1 — Ganglion cyst of the right thumb interphalangeal joint, Favored.** This is the note's final diagnosis and is proposed for entry above as `M67.441`. It is named here so the differential is accounted for in full, and it does not take a `NOT FOR ENTRY` line, because it is for entry.

```
ICD-10  M71.341  Other bursal cyst, right hand   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 2, digital mucous (myxoid) cyst. `M71.3` carries the inclusion term *Synovial cyst NOS*, and `M67.4`'s excludes2 for cyst of bursa and cyst of synovium points here rather than at the ganglion code.

```
ICD-10  L72.0  Epidermal cyst   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 3, epidermal inclusion cyst.

```
ICD-10  M12.241  Villonodular synovitis (pigmented), right hand   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 4, giant cell tumor of the tendon sheath — the entry the note names as the reason the referral is appropriate rather than optional. The code number and descriptor are looked up; **the mapping from the entity to this code is not**, because the database holds the tabular and not the alphabetic index, and `--find "giant cell tumor"` returns nothing. `D48.1` was checked as the alternative and is a header, not billable.

```
ICD-10  M19.041  Primary osteoarthritis, right hand   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 5, Heberden/Bouchard-type osteophyte of the interphalangeal joint. `M15.1 Heberden's nodes (with arthropathy)` was checked and sits under polyosteoarthritis; the note describes one joint, so the single-site code is the closer read.

```
ICD-10  M1A.9XX1  Chronic gout, unspecified, with tophus (tophi)   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```
Entry 7, gouty tophus.

**Entry 6 — cutaneous or soft-tissue malignancy of the hand.** NOT CODED, nothing established it. The refused code, what it needs and what is proposed in its place are in the step-4 block below.

**Where these must not go.** These are documentation of medical decision-making. None belongs in a Medatrax `ICD-10-CM` category, which takes preexisting and final diagnoses only — the entities the patient had, not the ones the note argued against.

---

## Step 4 — what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
The specific seasonal allergen. The note records "seasonal allergies" with no trigger
named and no reaction pattern.
  affects: J30.2 — a documented pollen trigger moves this to J30.1

The reason the immunizations were not carried out — contraindication, patient decision,
or another reason. Z28.3 carries a useAdditionalCode note asking for it, and the note
records the gap without a cause.
  affects: Z28.39 — this adds a second code (Z28.0-, Z28.1, Z28.2-, Z28.8-), it does not
  replace Z28.39

A tissue diagnosis. No specimen was taken, no imaging obtained, and the excision is a
referral rather than a result.
  affects: M67.441, which rests on the clinical findings of mobility and joint-line
  origin; and R22.31, which the note itself labels "pending tissue diagnosis"

Whether any vaccine was administered at this encounter. The Plan writes every dose
conditionally and Follow-up says "immunization catch-up if not completed today", so the
note does not say whether anything was given.
  affects: no code — it is the reason no CPT immunization administration code is
  proposed. A documented administration would earn one

The lesion's dimensions. The exam records "small" and no measurement.
  affects: no proposed code today. It is the baseline the referral visit needs to say
  whether the lesion grew, and growth is what would move R22.31 toward a different entity
```

```
--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
EMPTY — no proposed code rests on a filled value.

This block is written out rather than dropped, because an absent block and an empty one
read the same on the page and mean different things. The tier block declares that no
vital and no body measurement was filled in this encounter: BP, HR, T, RR, SpO2, height
and weight are all carried through from the shorthand unchanged. Z68.24 is the code that
would normally land here, and it does not — its BMI is derived from a given 62 in and a
given 131 lb, so nothing about it was invented.
```

```
--- NOT CODED, NOTHING ESTABLISHED IT ---
Cutaneous or soft-tissue malignancy of the hand, suspected by the patient herself and
addressed directly in the Assessment; no specimen taken, no imaging, no tissue diagnosis
  NOT CODED: C49.11  Malignant neoplasm of connective and soft tissue of right upper
             limb, including shoulder
  needs: histopathology from the referral excision. The exam argues against malignancy —
  2 to 3 months without growth, mobility, no fixation to skin or deeper tissue, intact
  and undiscolored skin, no ulceration, no regional lymphadenopathy — and none of that
  establishes the diagnosis in either direction. The descriptor asserts a malignancy
  nothing tested for
  proposed instead: R22.31  Localized swelling, mass and lump, right upper limb
```

**The note's own differential names this entry for the disease it argues against; this block names it for the suspicion.** That difference is intended — the note is read by a grader and by whoever treats her next, and this worksheet is read by the clinician looking for what to chase. `proposed instead` is where the two documents meet.

**No hedged diagnosis was dropped.** The Assessment carries one favored diagnosis and six alternatives. The favored one is coded, five alternatives are coded in the differential block, and the sixth is refused here with a code proposed in its place.

---

## Step 5 — E/M level

**No level is selected, and none was asked for.** The supporting elements, for the clinician to map:

- **Problems addressed** — a new undiagnosed mass with an uncertain prognosis, worked seven entities deep with a rationale on each, plus two stable chronic conditions (hypertension at goal, seasonal allergic rhinitis) and a documented immunization gap acted on.
- **Data reviewed** — none ordered and none resulted. No laboratory, no imaging, no specimen. The screening set in the Assessment is a list of confirmations to obtain, not data reviewed at this visit.
- **Risk** — referral for excision with histopathology requested; medication continued unchanged; a vaccine schedule offered. No prescription change, no procedure performed.
- **Time** — start 12:09 is a given read from the shorthand; end 12:34 is estimated by this pipeline's Times convention. **A time-based level cannot rest on that**, because half the interval was generated rather than recorded. If the level is to be assigned on time, the end time has to be confirmed against the source day file first — the note says the same thing at its top.

**The differential is where the first element is documented.** Six entities the encounter could not exclude on physical examination alone, one of them driving the referral, is what "problems addressed" is counting.

**This MDM phrasing is recalled. Nothing in this repo verifies it** — no coding guidelines ship here, and `reference/icd10cm-2026.sqlite` holds the tabular alone.

---

## CPT

**No CPT code is proposed.**

- No procedure was performed. No specimen, no imaging, no injection, no lesion removal — `Labs/Tests today` states it outright, and the excision is somebody else's visit.
- No vaccine is documented as administered today, so no administration code and no vaccine product code is earned. Named in step 4 as the thing to document.
- No E/M code, because step 5 does not select a level unprompted and the elements are offered above instead.

---

## Counts

Proposed for entry: **8 ICD-10 codes**, all billable, all looked up.
Differential: **5 ICD-10 codes**, none for entry — plus one entry proposed for entry above and one refused.
CPT: **0**.
Codes resting on a filled anchor: **0**.
