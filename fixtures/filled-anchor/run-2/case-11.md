# case-11

## Step 1 — FILLED and DERIVED, read first

The tier block is present, so nothing has to be treated as filled by default.

`DERIVED` entries:

1. BMI 28.1 = 703 x 190 / 69^2. **Both inputs are filled**, so this derived value is treated as filled here.
2. Pack-years = 1. Inputs are given (1 pack per day, 1 year). Not filled. Supports no code.
3. Patient Time = Adult (18 – 60) Hours, from a given age. Administrative, not codable.
4. Visit Time = 0:30, from filled start and end times. Administrative, not codable.

`FILLED·asserted` vitals and body measurements, with their values as written in the note body:

| # | Value | Supports a code? |
| --- | --- | --- |
| 1 | BP 128/78 filled | No. Not an elevated reading, so no `R03.0`. |
| 2 | HR 86 filled | No. Within range. |
| 3 | T 98.6 F filled | No. Afebrile. |
| 4 | RR 18 filled | No. Not tachypneic, so no `R06.82`. |
| 5 | SpO2 97% on room air filled | No. Within range. |
| 6 | HEIGHT 5'9" (69 in) filled | Yes, as an input to the BMI. |
| 7 | WEIGHT 190 lb filled | Yes, as an input to the BMI. |
| 8 | BMI 28.1, both inputs filled | Yes — `E66.3` and `Z68.28`. |

`FILLED·proposed` entries 28 through 40 are plan content — drug durations, counseling, return precautions, the differential itself. None of them is a measured value, and none of them anchors a diagnosis code. Entries 32 and 33 (incision and drainage, wound culture) are **proposed for a future visit**, not performed, so neither produces a CPT code today.

**The set carrying `SOURCE: filled`: BMI 28.1 and its two inputs.** Everything else the note codes rests on given history or given exam findings.

**One thing in the input is superseded and is not followed.** The note's own coding note states that `E66.3` and `Z68.28` are "deliberately NOT coded" because "icd10-cpt declines to code off a filled value." That was the rule under [#10](https://github.com/mshamblin5150-code/clinical-skills/issues/10); [#46](https://github.com/mshamblin5150-code/clinical-skills/issues/46) replaced refusing with marking. Both codes are therefore **proposed and marked** below, and both appear again in step 4.

---

## Step 2 — codable elements

**Diagnoses, from the Assessment.**

| Element | Filled-anchored? |
| --- | --- |
| Infected cyst of the penis, left | no — given exam and given history |
| Sebaceous cyst as the underlying lesion | no — given history of a recurrent penile cyst |
| Right testicular pain | no — given history |
| Asthma | no — given history |
| Restless legs syndrome | no — given history |
| Current smokeless tobacco use | no — given social history |
| Seasonal allergic rhinitis | no — given history |
| Levofloxacin allergy status | no — given allergy list |
| Overweight | **yes** — filled height and filled weight only |
| BMI band | **yes** — filled height and filled weight only |
| Wheezing | no — given exam finding, but see step 4 |
| Former cigarette use | no — given social history, but see step 4 |

**Procedures, from the Plan and Objective.** None. `Labs/Tests today: none. No new testing today, and no in-clinic treatment was administered.` Incision and drainage and a wound culture are proposed for the Thursday follow-up and were not performed at this encounter.

---

## Step 3 — proposed codes

```
ICD-10  N48.29  Other inflammatory disorders of penis
  ANCHOR: "a large cyst is present on the left side of the penis, swollen, with a white head,
           draining white fluid. No surrounding erythema."
  SPECIFICITY: complete — N48.29 is an "Other specified" residual rather than an unspecified
    one, and N48.2- carries no laterality, episode or severity axis, so the documented left
    side is not expressible in this code. The organism the tabular asks for is a separate
    B95-B97 code, not a further axis of N48.29 — see step 4.
  CONFIDENCE: verified against ICD-10-CM FY2026
  USE ADDITIONAL: the tabular carries "code (B95-B97), to identify infectious agent" on N48.2.
    No culture was obtained, so no B-code is added and none is invented.
```

```
ICD-10  L72.3  Sebaceous cyst
  ANCHOR: "with sebaceous cyst L72.3 as the underlying lesion" and "cyst on the penis,
           recurrent, with an identical episode 11 to 12 years ago"
  SPECIFICITY: complete — L72.3 is a leaf with no laterality, site or episode axis. Its two
    excludes2 neighbors, pilar cyst (L72.11) and trichilemmal cyst (L72.12), are different
    lesions rather than axes of this one.
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  N50.811  Right testicular pain
  ANCHOR: "separate intermittent pain in the right testicle" and "Secondary: right
           testicular pain N50.811"
  SPECIFICITY: complete — laterality documented as right, and N50.81- has no further axis
    below laterality.
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  J45.909  Unspecified asthma, uncomplicated
  ANCHOR: "PMH/PSH: asthma" and "Inspiratory wheezing in all lung fields against a documented
           history of asthma"
  SPECIFICITY: needs: severity classification — intermittent versus mild, moderate or severe
    persistent. The descriptor's own "Unspecified" is that axis, and the encounter documents
    no severity. Exacerbation status is settled: the note states the shorthand does not say
    "exacerbation", so the uncomplicated fifth character stands.
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: the note itself records the tension between an uncomplicated code and inspiratory
    wheezing in all fields, and leaves it for the clinician. Nothing here resolves it.
```

```
ICD-10  G25.81  Restless legs syndrome
  ANCHOR: "PMH/PSH: asthma; restless legs syndrome"
  SPECIFICITY: complete — G25.81 is a named leaf with no laterality, severity or episode
    axis. Its excludes2 neighbor, sleep related movement disorders (G47.6-), is a different
    condition rather than an axis of this one.
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  F17.220  Nicotine dependence, chewing tobacco, uncomplicated
  ANCHOR: "tobacco: former cigarette smoker, 1 pack per day for 1 year, currently uses
           smokeless tobacco (dips)"
  SPECIFICITY: complete — the product axis is documented as chewing tobacco, and the sixth
    character is uncomplicated because no withdrawal, no nicotine-induced disorder and no
    remission is documented.
  CONFIDENCE: verified against ICD-10-CM FY2026
  EXCLUDES1: F17 carries excludes1 against history of tobacco dependence (Z87.891). That
    blocks the note's Z87.891 — see step 4.
```

```
ICD-10  J30.2  Other seasonal allergic rhinitis
  ANCHOR: "Allergies (reaction): seasonal allergies, reaction not documented" and "Seasonal
           nasal symptoms by history."
  SPECIFICITY: needs: the specific seasonal allergen. "Seasonal" is documented and the
    allergen is not; pollen would move this to J30.1 Allergic rhinitis due to pollen.
  CONFIDENCE: verified against ICD-10-CM FY2026
  EXCLUDES1: J30 carries excludes1 against allergic rhinitis with asthma (bronchial)
    (J45.909), and J45.909 is proposed above. The two are documented as separate long-
    standing conditions rather than as one combined diagnosis, so both are proposed — but
    this pair is the kind that reads correct up to a rejection. Confirm before submitting.
```

```
ICD-10  Z88.1  Allergy status to other antibiotic agents
  ANCHOR: "levofloxacin (Levaquin), reaction not documented"
  SPECIFICITY: complete — the drug class is documented. Levofloxacin is a fluoroquinolone
    antibiotic and not a penicillin (Z88.0) or a sulfonamide (Z88.2), so Z88.1 is the
    named class rather than a residual.
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: the note's own preexisting list carries Z88.8 Allergy status to other drugs,
    medicaments and biological substances. Z88.8 is the residual for drugs with no named
    class; an antibiotic has one. Z88.1 is proposed in its place, and this is a real
    disagreement with the note rather than a restatement of it.
```

```
ICD-10  E66.3  Overweight
  ANCHOR: "Ht 5'9" (69 in), Wt 190 lb, BMI 28.1" and "weight and nutrition counseling for a
           BMI of 28.1 (overweight range)"
  SOURCE: filled — the height (5'9", 69 in) and the weight (190 lb) are both filled, so the
    BMI derived from them is filled throughout; confirm before submitting
  SPECIFICITY: complete — E66.3 is the named overweight leaf and has no severity or cause
    axis below it. The BMI value E66 asks for is supplied by the Z68 code beside it, not by
    a further character of E66.3.
  CONFIDENCE: verified against ICD-10-CM FY2026
  NOTE: E66 carries "code to identify body mass index (BMI), if known". The BMI here is not
    known, it is generated. Z68.28 is proposed alongside anyway, marked, because a code on
    this worksheet is proposed rather than asserted.
```

```
ICD-10  Z68.28  Body mass index [BMI] 28.0-28.9, adult
  ANCHOR: "BMI 28.1" and "Age + unit | 32 Years (given)"
  SOURCE: filled — the band is a readout of a filled height (5'9") and a filled weight
    (190 lb); the age fixing the adult branch is given; confirm before submitting
  SPECIFICITY: complete — the band is fixed to one decimal by the BMI value, and the adult
    versus pediatric axis is settled by a given age of 32, above the 20-year boundary the
    tabular states on Z68.
  CONFIDENCE: verified against ICD-10-CM FY2026
```

**CPT: none proposed.** No procedure was performed. `Labs/Tests today: none. No new testing today, and no in-clinic treatment was administered.` The incision and drainage and the wound culture are `FILLED·proposed` items 32 and 33, contingent on findings at a future visit, and a procedure that has not happened has no code. No E/M level is selected — step 5 below.

---

```
--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---
```

The note runs nine differential entries. Two of them name conditions the encounter **established**, and their codes are proposed for entry above; they are named here so no entry is silently dropped, and their numbers are not repeated under a `NOT FOR ENTRY` line, because a code cannot be both.

Entry 1 — *Infected epidermal inclusion cyst of the penis, left. Favored.* Established and coded for entry above as `N48.29` with `L72.3`.

Entry 8 — *Referred pain from the penile lesion. Plausible alternative* for the intermittent right testicular pain. The finding it explains is coded for entry above as `N50.811`; the entry is an explanation of that symptom, not a second diagnosis.

Entry 9 — *Asthma with wheezing. Present.* Established and coded for entry above as `J45.909`.

The remaining six entries carry codes that document reasoning only:

```
ICD-10  N48.21  Abscess of corpus cavernosum and penis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  L73.9  Follicular disorder, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  A60.01  Herpesviral infection of penis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  A51.0  Primary genital syphilis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  B08.1  Molluscum contagiosum   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  N45.1  Epididymitis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  N45.2  Orchitis   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

`N45.1` and `N45.2` both sit under the single entry *Epididymitis or orchitis, right*, which names two conditions with an `or`. `N45.3 Epididymo-orchitis` is not used, because it asserts both at once and the entry asserts neither.

**The organism-specific-descriptor limit was applied here and produced no substitution.** `A60.01`, `A51.0` and `B08.1` all name an organism, and none of the three was tested for. Each is argued against in the note rather than suspected, and nothing in the encounter documents an exposure — `Sexual history and STI risk assessment: not documented, despite a genital lesion` is GAPS 14 — so there is no `Z20.-` contact code the encounter earns and none is invented. The three stay as differential codes carrying `NOT FOR ENTRY`, which is the whole of what they assert.

---

## Step 4 — what documentation is missing

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
The infectious agent of the draining penile lesion. No wound culture was obtained, so the
B95-B97 "use additional code" instruction on N48.2 cannot be satisfied.
  affects: N48.29

Asthma severity classification — intermittent, or mild, moderate or severe persistent. This
is the axis the descriptor's own "Unspecified" leaves open.
  affects: J45.909

The specific seasonal allergen. Pollen would move this to J30.1.
  affects: J30.2

The reaction and severity of the levofloxacin allergy. Nothing distinguishes intolerance
from true allergy, and the note records that this constrains future antibiotic choice.
  affects: Z88.1

Scrotal and testicular examination. A right testicular complaint is charted and no
examination of that region is documented, so the symptom cannot be closed out and the
epididymitis differential cannot be excluded.
  affects: N50.811, and the N45.1 / N45.2 differential entries

Induration or fluctuance of the lesion. "No induration or fluctuance documented" is the
absence of a finding rather than a negative finding, and it is what separates N48.29 from
N48.21 Abscess of corpus cavernosum and penis.
  affects: N48.29
```

```
--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
E66.3 — Overweight, from a BMI of 28.1 derived from a filled height (5'9", 69 in) and a
filled weight (190 lb). Neither input was measured.
  needs: a measured height and a measured weight. At the filled weight of 190 lb this code
    survives the invention: every height from 5'7" to 6'0" lands in the overweight band
    (29.8 down to 25.8), so it is not the invented inch that produced E66.3.

Z68.28 — Body mass index [BMI] 28.0-28.9, adult, from the same filled height and filled
weight. This is the code the invented inch decided.
  needs: a measured height. Those same six heights at 190 lb produce five different codes —
    5'7" Z68.29, 5'8" and 5'9" Z68.28, 5'10" Z68.27, 5'11" Z68.26, 6'0" Z68.25. One inch
    taller moves this to Z68.27.
```

```
--- NOT CODED, NOTHING ESTABLISHED IT ---
Personal history of nicotine dependence, taken by the note from a former cigarette history of
1 pack per day for 1 year
  NOT CODED: Z87.891  Personal history of nicotine dependence
  needs: documentation that the former cigarette use met criteria for nicotine dependence
    rather than tobacco use, and a clinician's ruling that it is a condition unrelated to the
    current chewing-tobacco dependence. The tabular carries excludes1 in both directions —
    Z87.891 excludes1 current nicotine dependence (F17.2-), and F17 excludes1 history of
    tobacco dependence (Z87.891).
  proposed instead: F17.220  Nicotine dependence, chewing tobacco, uncomplicated — the
    current use is documented outright. Z72.0 Tobacco use is not the alternative either; it
    carries the same excludes1 against F17.2-.

Wheezing as a separately reported finding, documented as inspiratory wheezing in all fields
  NOT CODED: R06.2  Wheezing
  needs: nothing at the bedside. R06.2 carries excludes1 against Asthma (J45.-), so while
    J45.909 is reported the wheezing is captured by the asthma code and cannot be reported
    beside it. This is the note's own coding note, re-derived from the tabular rather than
    taken on its word.
  proposed instead: J45.909  Unspecified asthma, uncomplicated — already proposed above.
```

---

## Step 5 — E/M level

**Not selected, because none was requested.** The supporting elements, offered for the clinician to map:

- **Problems addressed.** One acute illness with a local infection, plus three chronic conditions carried on the problem list (asthma, restless legs syndrome, seasonal allergic rhinitis), plus an intermittent right testicular pain that the encounter could **not** exclude, since no scrotal examination is documented. That last one is an undiagnosed new problem with an uncertain prognosis, and it carries more weight in this column than the visit's routine feel suggests. The nine-entry differential with its rationale is where those problems are documented.
- **Data reviewed.** Thin, and honestly so. No laboratory, imaging or diagnostic testing was performed or resulted. The wound culture, the STI panel and the possible pulmonary function testing are orders contemplated for a future visit, not data reviewed at this one.
- **Risk.** Prescription drug management — three prescriptions, one of them a systemic antibiotic with a documented allergy list that had to be checked against it. Return precautions naming Fournier gangrene and testicular torsion criteria are the risk the differential is guarding against.

**This phrasing is recalled, and nothing in this repo verifies it.** No coding guidelines ship here; `reference/icd10cm-2026.sqlite` holds the tabular alone. Map these to a level yourself.

---

## Counts

- **10** ICD-10 codes proposed for entry, 2 of them carrying `SOURCE: filled`.
- **7** differential codes, none for entry.
- **0** CPT codes.
- **2** codes withheld, each named inline with `NOT CODED`.
