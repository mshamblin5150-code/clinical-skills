# case-09

## Step 1 — FILLED and DERIVED, read first

Tier block is present. `DERIVED`, `FILLED·asserted` and `FILLED·proposed` all read.

**Filled vitals and body measurements, with their values:**

| Value | Tier |
| --- | --- |
| BP 146/90 | FILLED·asserted |
| HR 88 | FILLED·asserted |
| T 99.2 °F | FILLED·asserted |
| RR 18 | FILLED·asserted |
| SpO2 96% on room air | FILLED·asserted |
| Height 5'4" (64 in) | FILLED·asserted |
| Weight 205 lb | FILLED·asserted |

**Derived values checked for a filled input:**

- **BMI 35.2** — `DERIVED  BMI 35.2 = 703 x 205 / 64^2 = 144,115 / 4,096 = 35.18 -> 35.2`. Both inputs are filled: `HEIGHT 5'4" (64 in) filled` and `WEIGHT 205 lb filled`. **Treated as filled here.**
- Patient Time, Visit Time and Case Type are derived from the given age, the estimated times and the final diagnoses. None is an input to a code.

Age 44 is **given**, so the adult `Z68` band applies and is not itself recalled.

No vital sign was transcribed this encounter — the entire vital set is filled.

## Step 2 — Codable elements

**Diagnoses (Assessment):**

| Element | Status |
| --- | --- |
| Acute rhinosinusitis, favored | codable |
| Acute suppurative otitis media, bilateral | codable |
| Acute infective otitis externa, right ear | codable |
| Acute pharyngitis | codable |
| COVID-19 household exposure, untested | codable as exposure; the disease code is refused in step 4 |
| Xerosis of both lower extremities | codable |
| Diminished breath sounds bilaterally, addressed in the Assessment | codable as a sign |
| Hypertension (PMH) | codable — anchored to the history, not to the filled reading |
| Peripheral artery disease (PMH) | codable |
| Depression (PMH) | codable |
| Hyperlipidemia (PMH) | codable |
| Hypothyroidism (PMH) | codable |
| Arthritis of both knees (PMH) | codable, type not documented; the specific code is refused in step 4 |
| Lymphedema (PMH) | codable |
| Healed right hip fracture (PSH) | codable |
| Cholecystectomy (PSH) | codable |
| Tubal ligation (PSH) | codable |
| Left lower leg surgery and dilation and curettage (PSH) | codable |
| Obesity, class 2 | **filled-anchored** — rests only on the filled height and filled weight |
| BMI band 35.0–35.9 | **filled-anchored** — same two inputs |
| Streptococcal pharyngitis, allergic rhinitis, odontogenic facial pain, peritonsillar or deep neck space infection | differential entries |

**Procedures (Plan and Objective):**

- Methylprednisolone 125 mg IM administered in clinic today — codable.
- No laboratory study, imaging or point-of-care test was performed, so nothing else in the Plan is a performed procedure. The otic drops, the oral antibiotic and the dose pack are prescriptions, not procedures.

## Step 3 — Proposed codes

```
ICD-10  J01.90  Acute sinusitis, unspecified
  ANCHOR: "tenderness over the maxillary and frontal sinuses on the reported side of worst
    pain" / "sinus pressure with facial pain, nasal congestion, rhinorrhea"
  SPECIFICITY: needs: the sinus involved (maxillary, frontal, ethmoidal, sphenoidal or
    pansinusitis) and whether the episode is recurrent — J01.90 declines all of it, and the
    note does not localize which side the facial pain is worse on
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  H66.003  Acute suppurative otitis media without spontaneous rupture of ear drum, bilateral
  ANCHOR: "bilateral tympanic membranes bulging" / "No spontaneous otorrhea documented"
  SPECIFICITY: complete — laterality documented as bilateral, and the absence of spontaneous
    rupture is documented, which are the two axes H66.00 carries
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  H60.391  Other infective otitis externa, right ear
  ANCHOR: "Right external auditory canal swollen and erythematous." / "Left canal patent."
  SPECIFICITY: needs: confirmation the canal inflammation is infective rather than reactive —
    laterality is documented as right, but the note itself names H60.501 as the reading if it
    is non-infective
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  J02.9  Acute pharyngitis, unspecified
  ANCHOR: "Oropharynx — pharyngeal erythema." / "sore throat"
  SPECIFICITY: needs: an organism — no rapid strep and no culture was done, so nothing
    separates this from J02.0 or J02.8
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z20.822  Contact with and (suspected) exposure to COVID-19
  ANCHOR: "Exposure: her daughter-in-law tested positive for COVID-19."
  SPECIFICITY: complete — Z20.822 names the contact and the suspected exposure and carries no
    further axis; the disease itself is refused in step 4
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  L85.3  Xerosis cutis
  ANCHOR: "Xerosis of both lower extremities." / "Skin: dry skin + (lower extremities)"
  SPECIFICITY: complete — L85.3 carries no site, laterality or severity axis
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  R09.89  Other specified symptoms and signs involving the circulatory and respiratory systems
  ANCHOR: "Breath sounds diminished bilaterally." / "Diminished breath sounds — addressed,
    not filed."
  SPECIFICITY: complete — R09.89 is the residual for a respiratory sign with no named code of
    its own, and it carries no site, laterality or severity axis. The exam finding is
    recorded; the respiratory system is not among the systems the tier block declares filled
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  I10  Essential (primary) hypertension
  ANCHOR: "PMH: Hypertension." / "Explained by known hypertension"
  SPECIFICITY: complete — I10 has no further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
```

`I10` is anchored to the documented history and **not** to the filled 146/90, so it carries no `SOURCE` line. A single reading does not diagnose hypertension, filled or measured. `R03.0` is not proposed: its own tabular note reads *"This category is to be used to record an episode of elevated blood pressure in a patient in whom no formal diagnosis of hypertension has been made"*, and this patient carries one.

```
ICD-10  I73.9  Peripheral vascular disease, unspecified
  ANCHOR: "PMH: ... Peripheral artery disease."
  SPECIFICITY: needs: whether the disease is atherosclerotic and which extremity — I70.2- to
    I70.7- name both, and I73.9 declines both
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  F32.A  Depression, unspecified
  ANCHOR: "PMH: ... Depression." / "she carries a depression diagnosis"
  SPECIFICITY: needs: single versus recurrent episode and severity — F32.0 to F32.5 and F33.-
    turn on both, and neither is documented
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  E78.5  Hyperlipidemia, unspecified
  ANCHOR: "PMH: ... Hyperlipidemia."
  SPECIFICITY: needs: the lipid fraction — a lipid panel separates E78.0 through E78.4, and
    the Plan proposes one
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  E03.9  Hypothyroidism, unspecified
  ANCHOR: "PMH: ... Hypothyroidism."
  SPECIFICITY: needs: the cause — E03.2 through E03.8 name drug-induced, postinfectious and
    other specified causes, and nothing here names one
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  M19.90  Unspecified osteoarthritis, unspecified site
  ANCHOR: "PMH: ... Arthritis of both knees." / "Musculoskeletal: chronic knee pain +
    (baseline)"
  SPECIFICITY: needs: site and the arthritis type — the source records only arthritis of both
    knees, and the note states the osteoarthritis reading is assumed rather than documented.
    A documented type plus the knee site moves this to M17.0
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  I89.0  Lymphedema, not elsewhere classified
  ANCHOR: "PMH: ... Lymphedema." / "Non-pitting edema of both lower extremities."
  SPECIFICITY: complete — I89.0 carries no laterality or site axis, and the hereditary and
    postmastectomy alternatives it excludes are neither documented nor suggested
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z87.81  Personal history of (healed) traumatic fracture
  ANCHOR: "PSH: ... Repair of a broken right hip." / "Right hip with healed fracture; no acute
    tenderness."
  SPECIFICITY: complete — Z87.81 carries no site or laterality axis; the traumatic-versus-
    nontraumatic split it does carry is documented by the repair of a broken hip
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z90.49  Acquired absence of other specified parts of digestive tract
  ANCHOR: "PSH: Cholecystectomy." / "Well-healed cholecystectomy scars."
  SPECIFICITY: complete — the code set ships no acquired-absence code naming the gallbladder,
    so Z90.49 is the specific one available and carries no further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z98.51  Tubal ligation status
  ANCHOR: "PSH: ... Bilateral tubal ligation."
  SPECIFICITY: complete — Z98.51 has no further axis
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z98.890  Other specified postprocedural states
  ANCHOR: "PSH: ... Left lower leg surgery. Dilation and curettage." / "Well-healed left lower
    leg surgical scar."
  SPECIFICITY: needs: what the left lower leg surgery was — a named procedure may map to a
    specific status code rather than this residual, and the source names a site and not an
    operation
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  E66.812  Obesity, class 2
  ANCHOR: "BMI 35.2 — addressed, not filed. Class 2 obesity by the derived value."
  SOURCE: filled — HEIGHT 5'4" (64 in) and WEIGHT 205 lb are both filled; BMI 35.2 is derived
    from those two filled inputs and from nothing measured; confirm before submitting
  SPECIFICITY: complete — class 2 is set by the BMI value and E66.812 carries no further axis.
    E66 instructs "code to identify body mass index (BMI), if known", which is why Z68.35
    follows
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z68.35  Body mass index [BMI] 35.0-35.9, adult
  ANCHOR: "Ht 5'4" (64 in) · Wt 205 lb → BMI 35.2"
  SOURCE: filled — HEIGHT 5'4" (64 in) and WEIGHT 205 lb are both filled; the band is a
    readout of an invented inch, not a measurement; confirm before submitting
  SPECIFICITY: complete — the band is fixed by the BMI value, Z68.35 carries no further axis,
    and the adult range applies because the given age of 44 is 20 or older
  CONFIDENCE: verified against ICD-10-CM FY2026
```

The note's Assessment holds E66.812 and Z68.35 back on the grounds that *"a code is not carried on a filled value."* That was the previous rule. Under the current one both are **proposed and marked**, so this worksheet and the note's `Preexisting diagnoses` and `Final diagnosis` fields no longer disagree about a number.

**CPT**

```
CPT  96372  Therapeutic, prophylactic, or diagnostic injection (specify substance or drug);
             subcutaneous or intramuscular
  ANCHOR: "Treatments administered in clinic today: Methylprednisolone 125 mg IM, given now."
  REQUIREMENTS THE CODE HINGES ON: route documented as IM; substance documented as
    methylprednisolone 125 mg; administration documented as performed in clinic today, not
    prescribed. No infusion, no hydration, no second injection is documented
  SPECIFICITY: complete — 96372 is selected by route and by the injection being therapeutic;
    both are documented, and the drug supply is a separate HCPCS Level II item rather than a
    further axis on this code
  CONFIDENCE: verify this number — no CPT code set ships in this repo, so this is recalled
    rather than looked up
```

--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

The two favored entries carry codes that are proposed for entry above: acute bacterial rhinosinusitis with concurrent bilateral acute otitis media (J01.90, H66.003) and acute infective otitis externa of the right ear (H60.391). The remaining five entries are documentation of reasoning only.

Acute viral upper respiratory infection, including COVID-19, less likely as the whole explanation and not excluded

```
ICD-10  J06.9  Acute upper respiratory infection, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

Streptococcal pharyngitis, less likely on a low Centor score with cough, sneezing and rhinorrhea present and no cervical lymphadenopathy

```
ICD-10  J02.9  Acute pharyngitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

Allergic rhinitis, less likely

```
ICD-10  J30.9  Allergic rhinitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

Odontogenic source of maxillary facial pain, less likely

```
ICD-10  K08.89  Other specified disorders of teeth and supporting structures   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

Peritonsillar or deep neck space infection, excluded on exam

```
ICD-10  J36  Peritonsillar abscess   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

`J02.0 Streptococcal pharyngitis` names the organism and nothing tested for it, so the strep entry carries `J02.9` here and the refusal is recorded in step 4. `U07.1 COVID-19` is refused the same way and the COVID limb of the viral entry carries `Z20.822`, which is proposed for entry on its own anchor.

## Step 4 — Missing documentation

```
--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---
Which sinus is involved, and which side the facial pain is worse on
  affects: J01.90

The infectious agent, per J01's "use additional code (B95-B97) to identify infectious agent"
  affects: J01.90

Whether the right canal inflammation is infective or non-infective
  affects: H60.391 — the note names H60.501 as the alternative reading

A rapid strep test or a throat culture
  affects: J02.9

The arthritis type, and the knee site recorded as a coded site rather than as history
  affects: M19.90

Whether the peripheral artery disease is atherosclerotic, and which extremity
  affects: I73.9

Single versus recurrent depressive episode, and severity
  affects: F32.A

A lipid panel naming the fraction
  affects: E78.5

The cause of the hypothyroidism
  affects: E03.9

What the left lower leg surgery was
  affects: Z98.890

A measured height and a measured weight
  affects: E66.812, Z68.35

--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---
E66.812 — Obesity, class 2, from BMI 35.2 derived from a filled height (5'4") and a filled
weight (205 lb). Neither input was measured
  needs: a measured height and a measured weight. At 5'5" the BMI is 34.1, which is class 1
  and moves this to E66.811

Z68.35 — BMI 35.2 derived from a filled height (5'4") and a filled weight (205 lb)
  needs: a measured height. One inch moves this to Z68.34

--- NOT CODED, NOTHING ESTABLISHED IT ---
COVID-19, suspected from a documented COVID-positive daughter-in-law and a congruent
1-to-2-day upper respiratory syndrome; no SARS-CoV-2 test was performed or recorded
  NOT CODED: U07.1  COVID-19
  needs: a positive SARS-CoV-2 antigen or PCR. The household contact alone does not establish
  the disease, and the Plan proposes the test that was never ordered
  proposed instead: Z20.822  Contact with and (suspected) exposure to COVID-19

Streptococcal pharyngitis, considered on the sore throat and pharyngeal erythema and argued
against on a low Centor score; no rapid strep was done
  NOT CODED: J02.0  Streptococcal pharyngitis
  needs: a positive rapid strep or throat culture. The descriptor names the organism and
  nothing here identified one
  proposed instead: J02.9  Acute pharyngitis, unspecified

Primary osteoarthritis of both knees, assumed in the Assessment from age and pattern; the
source records only arthritis of both knees
  NOT CODED: M17.0  Bilateral primary osteoarthritis of knee
  needs: the joint pathology named — an imaging report, a prior rheumatology diagnosis, or an
  inflammatory workup. The Assessment states the osteoarthritis reading is an assumption and
  says to recode if the type is inflammatory
  proposed instead: M19.90  Unspecified osteoarthritis, unspecified site, which the tabular
  gives the inclusion term "Arthritis NOS"
```

**Every filled value accounted for:**

| Filled value | What it supports |
| --- | --- |
| BP 146/90 | **No code.** I10 is anchored to the documented history, not to this reading, and R03.0 is barred by its own tabular note because a formal hypertension diagnosis exists |
| HR 88 | No code — within range |
| T 99.2 °F | No code — below the 100.4 °F fever threshold, and the note says so |
| RR 18 | No code — within range; R06.82 has no anchor |
| SpO2 96% on room air | No code — within range |
| Height 5'4" (64 in) | Input to BMI 35.2 → E66.812, Z68.35, both marked `SOURCE: filled` and both listed above |
| Weight 205 lb | Input to BMI 35.2 → E66.812, Z68.35, both marked `SOURCE: filled` and both listed above |
| BMI 35.2 (derived, both inputs filled) | E66.812, Z68.35, both marked `SOURCE: filled` and both listed above |

The filled exam systems the tier block declares — eyes, neck, abdomen, musculoskeletal, neurologic and psychiatric — are all recorded normal and support no code. The filled home medication list, the filled NKDA and the filled social history support no code either. The respiratory, ear, nose, oropharynx, cardiovascular and skin findings that do carry codes are not among the filled systems.

## Step 5 — E/M level

**No E/M level is selected and no E/M CPT code is proposed.** None was requested, and this skill does not assign one unprompted. The supporting elements are offered for the clinician to map:

- **Problems addressed** — two acute concurrent infections treated today (rhinosinusitis with bilateral otitis media, right otitis externa), an acute pharyngitis, a documented household COVID-19 exposure left untested, a new bilaterally diminished breath sound addressed with a spirometry plan, and seven chronic conditions of which hypertension and depression were actively managed against the corticosteroids started today. The differential runs seven deep, and three of its entries could not be excluded on this encounter.
- **Data reviewed** — none. No laboratory study, no imaging and no point-of-care test was performed or recorded, including no SARS-CoV-2 test despite the documented exposure. The data column rests on history and exam only.
- **Risk** — a systemic corticosteroid given in clinic plus a six-day oral taper, started against documented hypertension and documented depression; an ototoxic otic drop prescribed across bulging tympanic membranes; a prescription antibiotic; and an unidentified medication the patient took today that is held pending identification. Three drug-condition conflicts are named in the Plan.

**This phrasing is recalled.** No coding guidelines ship in this repo, and nothing here verifies the MDM element definitions or their mapping to a level.

## Completion

- 20 codes proposed for entry. Each carries a number, a descriptor, an anchor, a specificity flag and a confidence flag. **E66.812 and Z68.35 carry the sixth part, `SOURCE: filled`**, and both appear again under `CODED, ANCHOR WAS FILLED`.
- 1 CPT code proposed, carrying `verify this number` because no CPT set ships here.
- 5 differential codes, three parts each plus `NOT FOR ENTRY` on the code's own line. None is a candidate for entry anywhere, and none belongs in the Medatrax `ICD-10-CM` category.
- 3 codes refused, each named inline with `NOT CODED` and each carrying the code the encounter does support.
- Every value the FILLED block declared is accounted for in the table above.
- Every ICD-10 code on this worksheet, proposed or refused, was looked up in `reference/icd10cm-2026.sqlite` and every descriptor is the verbatim official string. All 27 distinct codes are billable, as are the four alternatives
  named in passing (H60.501, E66.811, Z68.34, R03.0), which were looked up as well.
