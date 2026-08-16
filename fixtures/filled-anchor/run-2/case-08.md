# case-08

Codes below are **proposed, never asserted**. Every ICD-10-CM code in this worksheet was
looked up in `reference/icd10cm-2026.sqlite` with `tools/icd10_lookup.py`; every descriptor
is the verbatim official string from that lookup and every code returned billable. The
database holds the tabular and not the alphabetic index, so a code here is *verified*, not
*indexed*. No CPT code set ships in this repo, so the one CPT proposal is recalled and says so.

---

## 1. Filled and derived values

The note carries a tier block, so source information is present and nothing has to be
treated as filled by default.

**DERIVED**

| | value | filled input? |
| --- | --- | --- |
| D1 | Pack-years = 1 x (33 - 18) = 15 pack-years | no — 1 ppd since age 18 and age 33 are both given |
| D2 | Age at 20 pack-years = 18 + 20 = 38 | no — same given inputs |
| D3 | BMI 28.0 = 703 x 168 / 65^2 = 27.95 -> 28.0 | **yes — height F6 and weight F7 are both filled** |
| D4 | Patient Time = Adult (18 - 60) Hours, from age 33 | no — age is given |
| D5 | Visit Time 0:30, from 14:20 to 14:50 | **yes — both times are estimated at F22** |

**FILLED - vitals and body measurements**

| | value | supports |
| --- | --- | --- |
| F1 | BP 148/92 | **no code.** R03.0 reads *without diagnosis of hypertension* and this patient carries a documented one, so the category is unavailable; and no single reading diagnoses hypertension, filled or given. I10 below is anchored to the PMH line instead. |
| F2 | HR 106 | **R00.0**, marked |
| F3 | T 101.4 F oral | **no code of its own.** R50.9 below is anchored to the given history of fever, not to this number. |
| F4 | RR 20 | **no code.** Within range; R06.82 Tachypnea is not supported at 20. |
| F5 | SpO2 96% on room air | **no code.** Normal. |
| F6 | Height 5'5" (65 in) | **E66.3, Z68.28**, both marked, through D3 |
| F7 | Weight 168 lb | **E66.3, Z68.28**, both marked, through D3 |
| F8 | BMI 28.0 (filled-input, derived at D3 from F6 and F7) | **E66.3, Z68.28**, both marked |

**FILLED - everything else declared, and what it does to the codes**

F9 (NKDA, inferred), F10 and F11 (lisinopril and hydrochlorothiazide, both inferred),
F12-F14 (marital status, occupation, education, social history), F15 (family history),
F16 (normal exam of unmentioned systems), F17 (ROS negatives), F18-F22 (administrative
fields and the estimated visit times) support **no code in this worksheet.** The two
inferred antihypertensives in particular add nothing: I10 rests on the documented PMH,
not on an inferred regimen. F22 is recorded because an estimated start and end time is a
filled value and a time-based E/M selection would rest on it — see step 4.

The set carried into step 3 as filled-anchored is therefore **F2, F6, F7 and F8 (via D3)**.

---

## 2. Codable elements

**From the Assessment — Final diagnosis and Preexisting diagnoses**

| element | codable / filled-anchored |
| --- | --- |
| COVID-19, SARS-CoV-2 test positive | codable |
| Acute otitis media, right | codable |
| Otitis media, left | codable |
| Acute pharyngitis | codable |
| Chest pain on breathing | codable |
| Myalgia, diffuse | codable |
| Lightheadedness | codable |
| Weakness | codable |
| Headache | codable |
| Fever | codable — anchored to the given history, not to F3 |
| Rhinorrhea / nasal congestion | codable |
| Cough, 2 days | codable |
| Hypertension, by history | codable |
| Nicotine dependence, cigarettes, 1 ppd current | codable |
| Cesarean section, by history | codable |
| Overweight band, BMI 28.0 | **filled-anchored** (F6, F7, F8) |
| BMI value band | **filled-anchored** (F6, F7, F8) |
| Tachycardia, HR 106 | **filled-anchored** (F2) |

**From the Plan and Objective — procedures and services**

| element | codable / filled-anchored |
| --- | --- |
| Methylprednisolone 125 mg IM administered in clinic | codable |
| SARS-CoV-2 testing performed | codable, but the method is not documented — see step 4 |
| Tobacco cessation counseling delivered and documented | codable |
| E/M service | not selected — step 5 was not requested |

Not codable this encounter: the age-appropriate screening list is written as items *to
consider*, and none of them was ordered or performed, so Z12.4, Z11.4, Z11.59, Z13.220,
Z13.1, Z13.31 and Z23 are not proposed. Z71.6 is the one item on that list the note also
documents as actually delivered, in the Plan and in the Education section, so it is
proposed on that anchor rather than on the screening list.

---

## 3. Proposed codes

### Diagnoses proposed for entry

ICD-10  U07.1  COVID-19
  ANCHOR: "SARS-CoV-2 testing — POSITIVE"
  SPECIFICITY: complete — U07.1 has no further axis; its useAdditionalCode for pneumonia due to COVID-19 (J12.82) does not engage, because no chest imaging was obtained
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  H66.001  Acute suppurative otitis media without spontaneous rupture of ear drum, right ear
  ANCHOR: "Right tympanic membrane erythematous and bulging; landmarks obscured on the right; no perforation, no purulent drainage, no canal erythema"
  SPECIFICITY: complete — laterality documented as right, and the rupture axis is documented by "no perforation"; the acute axis by "the right earache began yesterday"
  CONFIDENCE: verified against ICD-10-CM FY2026
  note: H66 instructs an additional tobacco code, which F17.210 below supplies

ICD-10  H65.192  Other acute nonsuppurative otitis media, left ear
  ANCHOR: "Left tympanic membrane also bulging, without erythema; no perforation, no drainage"
  SPECIFICITY: complete — laterality documented as left; the nonsuppurative axis is documented by the absent drainage, and H65.19 is the acute and subacute nonsuppurative group
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J02.9  Acute pharyngitis, unspecified
  ANCHOR: "Pharyngeal erythema present; no tonsillar exudate, no asymmetry, no uvular deviation"
  SPECIFICITY: needs: the organism — no rapid strep antigen and no throat culture was obtained, and J02.0 Streptococcal pharyngitis is what a positive result would earn
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R07.1  Chest pain on breathing
  ANCHOR: "chest pain that hurts to breathe" / "a deep breath makes the chest pain worse"
  SPECIFICITY: complete — R07.1 has no further axis; "Painful respiration" is its own inclusion term and R07 carries no laterality, severity or timing axis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M79.10  Myalgia, unspecified site
  ANCHOR: "8/10 body aches" / "Diffuse muscle tenderness consistent with the reported body aches"
  SPECIFICITY: needs: site — the aches are documented only as diffuse, and M79.18 Myalgia, other site is what a named muscle group or region would earn
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R42  Dizziness and giddiness
  ANCHOR: "Cardiovascular: lightheadedness +"
  SPECIFICITY: complete — R42 has no further axis, and "Light-headedness" is one of its own inclusion terms
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R53.1  Weakness
  ANCHOR: "I've had a headache, fever, cough, sore throat and I've been weak for two days."
  SPECIFICITY: complete — R53.1 has no further axis; its excludes1 entries name other conditions (R54 age-related weakness, M62.81 muscle weakness) rather than axes of this one, and neither is documented
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R51.9  Headache, unspecified
  ANCHOR: "Onset — 2 days ago for the headache" / "Neurologic: headache +"
  SPECIFICITY: needs: an orthostatic or positional component — R51.0 is what documenting one would earn, and no orthostatic vital signs were obtained despite the documented lightheadedness
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R50.9  Fever, unspecified
  ANCHOR: "I've had a headache, fever, cough, sore throat and I've been weak for two days." — the fever is given by history; the 101.4 F on the vitals line is filled and is not this code's anchor
  SPECIFICITY: needs: whether the fever is being recorded as presenting with the confirmed COVID-19 — R50.81 with U07.1 sequenced first is what that would earn
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R09.81  Nasal congestion
  ANCHOR: "Nares patent with clear rhinorrhea; no purulent nasal discharge."
  SPECIFICITY: complete — R09.81 has no further axis; the documented finding is rhinorrhea and R09.81 is the closest tabular fit, but the database holds no alphabetic index so the routing from rhinorrhea itself is unverified here
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R05.1  Acute cough
  ANCHOR: "Respiratory: cough +" / "Onset — 2 days ago for the headache, fever, cough, sore throat and weakness"
  SPECIFICITY: complete — duration documented as 2 days, which is the axis R05 splits on (R05.1 acute against R05.3 chronic), so R05.9 Cough, unspecified is not the code this documentation supports
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  I10  Essential (primary) hypertension
  ANCHOR: "PMH — hypertension." — and the note's own statement, "I10 is coded from the documented history of hypertension, never from the filled 148/92 reading."
  SPECIFICITY: complete — I10 has no further axis; its excludes1 (hypertensive disease complicating pregnancy) does not apply, no pregnancy is documented
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  F17.210  Nicotine dependence, cigarettes, uncomplicated
  ANCHOR: "Tobacco — 1 pack per day since age 18, current smoker; 15 pack-years (derived)"
  SPECIFICITY: complete — the product is documented as cigarettes and no complication is documented, which is exactly what the sixth character carries; "current smoker" excludes the Z87.891 history route
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z98.891  History of uterine scar from previous surgery
  ANCHOR: "PSH — cesarean section." / "Well-healed low transverse cesarean scar."
  SPECIFICITY: complete — Z98.891 has no further axis; its excludes1 (O34.2-, maternal care due to uterine scar) does not apply because no pregnancy is documented
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  E66.3  Overweight
  ANCHOR: "BMI 28.0 — overweight band, and it compounds the documented hypertension and the 15 pack-years."
  SOURCE: filled — height 5'5" (F6) and weight 168 lb (F7) are both filled, and BMI 28.0 is derived from both at D3; the encounter as documented recorded no vital signs at all; confirm before submitting
  SPECIFICITY: complete — E66.3 is the overweight code itself and carries no further axis; E66's useAdditionalCode for a BMI code is satisfied by Z68.28 below
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z68.28  Body mass index [BMI] 28.0-28.9, adult
  ANCHOR: "Ht 5'5\" (65 in) · Wt 168 lb → BMI 28.0"
  SOURCE: filled — the same two filled inputs, F6 and F7, through D3; a band code encodes the invented inch to one decimal place; confirm before submitting
  SPECIFICITY: complete — 28.0 falls in the 28.0-28.9 band, and the adult series is correct on the given age 33, which satisfies Z68's note that adult codes are for persons 20 years of age or older
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R00.0  Tachycardia, unspecified
  ANCHOR: "Heart rate 106: attributed to the fever and pain. Recheck at the 48-72 hour visit; a tachycardia that persists after the fever settles is not viral and needs evaluation" / "S1 and S2 present, regular rhythm; rate elevated."
  SOURCE: filled — HR 106 is filled (F2), and the note's own FL4 records that no vital signs were obtained anywhere in the encounter; confirm before submitting
  SPECIFICITY: needs: a rhythm determination — R00.0's excludes1 routes a stated inappropriate sinus tachycardia to I47.11 and paroxysmal tachycardia to I47.-, and no ECG was obtained this visit
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z71.6  Tobacco abuse counseling
  ANCHOR: "Reviewed tobacco cessation, the 15 pack-year figure, and what continuing costs her"
  SPECIFICITY: complete — Z71.6 has no further axis; its useAdditionalCode for nicotine dependence is satisfied by F17.210 above
  CONFIDENCE: verified against ICD-10-CM FY2026

### Procedures proposed for entry

CPT  96372  Therapeutic, prophylactic, or diagnostic injection (specify substance or drug); subcutaneous or intramuscular
  ANCHOR: "Treatment administered in clinic: methylprednisolone (Solu-Medrol) 125 mg IM ×1" — route documented as intramuscular, one administration, drug and dose both given
  SPECIFICITY: complete — the route axis (subcutaneous or intramuscular against intravenous push) is documented as IM, and one administration is documented, so no additional-sequential code applies
  CONFIDENCE: verify this number — no CPT code set ships in this repo, so both the number and the descriptor are recalled rather than looked up

No E/M code is proposed. Step 5 was not requested, and this skill does not select a level unprompted.

The drug supply itself is billed on a HCPCS Level II J code rather than a CPT code, and no HCPCS set ships here either; it is named as a gap in step 4 rather than guessed at.

### --- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

Eleven entries in the Assessment, each carrying a code. Where the entry's own specific code
asserts an organism or a disease the encounter never established, the line carries the code
the encounter **does** document and the refusal is recorded in step 4. `NOT FOR ENTRY` marks
the differential line; several of these numbers are separately proposed above on their own
anchors, and it is that proposal, not this line, that puts them in the entry list.

ICD-10  U07.1  COVID-19   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  H66.001  Acute suppurative otitis media without spontaneous rupture of ear drum, right ear   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  H65.192  Other acute nonsuppurative otitis media, left ear   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R07.1  Chest pain on breathing   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M79.10  Myalgia, unspecified site   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R07.1  Chest pain on breathing   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R05.1  Acute cough   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R50.9  Fever, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  J02.9  Acute pharyngitis, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R42  Dizziness and giddiness   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  I10  Essential (primary) hypertension   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R51.9  Headache, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Which entry each line documents, in the Assessment's own order: 1 COVID-19 (U07.1);
2 acute otitis media right (H66.001); 3 otitis media left (H65.192); 4 viral pleurisy with
myalgic chest wall pain (R07.1 with M79.10); 5 pulmonary embolism (R07.1, substituted);
6 community-acquired and COVID-19 pneumonia (R05.1, substituted); 7 influenza (R50.9,
substituted); 8 group A streptococcal pharyngitis (J02.9, substituted); 9 dehydration and
orthostatic lightheadedness (R42, substituted); 10 hypertensive urgency (I10, substituted);
11 bacterial meningitis (R51.9, substituted). Twelve code lines across eleven entries,
because entry 4 carries two.

---

## 4. What documentation is missing

### --- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---

The organism of the pharyngitis — no rapid strep antigen and no throat culture
  affects: J02.9

The site or muscle group of the myalgia — the aches are documented only as diffuse
  affects: M79.10

Orthostatic vital signs, supine and standing — they are named as not obtained
  affects: R51.9 (an orthostatic component routes to R51.0) and R42 (orthostatic hypotension is I95.1, a different diagnosis rather than a further axis)

Whether the fever is being recorded as presenting with the confirmed COVID-19
  affects: R50.9 (R50.81, with U07.1 sequenced first)

An ECG or any rhythm determination — none was obtained
  affects: R00.0 (a stated inappropriate sinus tachycardia routes to I47.11, paroxysmal tachycardia to I47.-)

A re-examination of the left tympanic membrane, and whether the left drum is acute otitis media or effusion — the exam documents bilateral bulging and the encounter's stated diagnosis is unilateral (FL1)
  affects: H65.192

The method of the SARS-CoV-2 test — antigen with direct optical observation and amplified probe technique take different CPT codes, and the note records only that testing was done and positive
  affects: no proposed code. No CPT is proposed for the test; the method is what would decide it, and picking one would be a coin flip

The actual start and end times of the visit — 14:20 to 14:50 is estimated (F22), and the note documents no total time and no explicit MDM statement
  affects: no proposed code. No E/M level is selected here (step 5 was not requested), but a time-based selection would rest on a filled value

The HCPCS Level II supply code for the methylprednisolone administered — no HCPCS set ships in this repo
  affects: no proposed code. 96372 covers the administration only

### --- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---

E66.3 — BMI 28.0, derived at D3 from a filled height (5'5") and a filled weight (168 lb)
  needs: a measured height and a measured weight. The band survives the invented inch — D3 shows 5'4" gives 28.8 and 5'6" gives 27.1, and all three are overweight — so this is the robust half of the pair

Z68.28 — BMI 28.0-28.9 band, from the same two filled inputs
  needs: a measured height and a measured weight. This is the fragile half: 5'6" gives BMI 27.1, which is Z68.27 Body mass index [BMI] 27.0-27.9, adult. One invented inch moves this code and moves it silently

R00.0 — HR 106, filled (F2)
  needs: a measured pulse. FL4 records that no vital signs were obtained anywhere in the encounter, so there is no measurement behind this at all

The note's own Assessment states that E66.3 and Z68.28 are "not coded, because both the
height and the weight it rests on are filled." This worksheet codes them and marks them
instead: a filled anchor is a reason to disclose, not to withhold, and withholding would put
this worksheet in disagreement with a note that already writes codes into its diagnosis
fields. The mark is what the note alone cannot carry.

### --- NOT CODED, NOTHING ESTABLISHED IT ---

Pulmonary embolism, suspected on pleuritic chest pain worse with a deep breath together with lightheadedness in a current 1-pack-per-day smoker at 15 pack-years; no chest imaging, no ECG, no D-dimer, and the encounter recorded no vital signs at all
  NOT CODED: I26.99  Other pulmonary embolism without acute cor pulmonale
  needs: a CT pulmonary angiogram, or a D-dimer read against a documented pretest probability
  proposed instead: R07.1  Chest pain on breathing, and R42  Dizziness and giddiness

Community-acquired pneumonia, suspected on fever, cough and pleuritic pain in a smoker; argued against by clear lung sounds in all fields, but no chest x-ray was obtained
  NOT CODED: J18.9  Pneumonia, unspecified organism
  needs: a chest radiograph showing an infiltrate
  proposed instead: R05.1  Acute cough, and R07.1  Chest pain on breathing

COVID-19 pneumonia, raised alongside the community-acquired entry; the COVID-19 is confirmed but the pneumonia is not
  NOT CODED: J12.82  Pneumonia due to coronavirus disease 2019
  needs: a chest radiograph showing an infiltrate. The positive test establishes the infection, not the pneumonia
  proposed instead: U07.1  COVID-19

Influenza, raised on an identical febrile syndrome with prominent myalgia; not tested this visit, and co-infection is named as remaining possible
  NOT CODED: J11.1  Influenza due to unidentified influenza virus with other respiratory manifestations
  needs: an influenza antigen or PCR result. J02.9 also carries an excludes1 to J11.1, so the two cannot both be entered
  proposed instead: R50.9  Fever, unspecified, and M79.10  Myalgia, unspecified site

Group A streptococcal pharyngitis, suspected on pharyngeal erythema and sore throat; argued against by prominent cough, rhinorrhea and absent cervical lymphadenopathy, and not tested this visit
  NOT CODED: J02.0  Streptococcal pharyngitis
  needs: a rapid strep antigen or a throat culture
  proposed instead: J02.9  Acute pharyngitis, unspecified

Dehydration, raised as a plausible contributor to the lightheadedness in a febrile patient with two days of reduced intake; orthostatic vitals were not obtained
  NOT CODED: E86.0  Dehydration
  needs: orthostatic vital signs, a documented oral intake, or a basic metabolic panel
  proposed instead: R42  Dizziness and giddiness

Hypertensive urgency, named in the Assessment and specifically rejected there
  NOT CODED: I16.0  Hypertensive urgency
  needs: a measured blood pressure. The 148/92 in this note is filled (F1) and the Assessment states outright that it is not being used as evidence
  proposed instead: I10  Essential (primary) hypertension, from the documented history

Bacterial meningitis, considered on a febrile headache and rejected on a supple neck, no meningismus, no photophobia, no confusion and a normal neurologic exam
  NOT CODED: G00.9  Bacterial meningitis, unspecified
  needs: a lumbar puncture with cerebrospinal fluid results
  proposed instead: R51.9  Headache, unspecified, and R50.9  Fever, unspecified

---

## 5. E/M supporting elements — level not selected

Step 5 selects no level unprompted, and none was requested. The elements the note documents,
offered for the clinician to map:

**Problems addressed.** Two established acute diagnoses (confirmed COVID-19; right acute
otitis media), one exam abnormality the encounter did not name in its own diagnosis (left
tympanic membrane bulging), one chronic documented condition affected by today's treatment
(hypertension, against which methylprednisolone was given), and one undiagnosed new problem
with an uncertain prognosis that the encounter could not exclude (pleuritic chest pain with
lightheadedness in a smoker, differential item 5). The differential is where these are
documented, which is the work its eleven codes do.

**Data reviewed.** One test ordered and resulted this visit (SARS-CoV-2, positive). Nothing
else was obtained — no imaging, no ECG, no D-dimer, no blood count, no strep or influenza
testing (GAPS G5, G6). No external records reviewed, no independent historian documented.

**Risk.** Parenteral drug administered (methylprednisolone 125 mg IM), given against a
documented hypertension and in early outpatient COVID-19 where corticosteroid benefit is not
established (FL5). Prescription drug management is proposed rather than performed — the
encounter diagnosed the right otitis media and prescribed nothing for it (FL2), and the
amoxicillin proposal rests on an inferred allergy history (F9, G4).

**This MDM framing is recalled, and nothing in this repo verifies it.** No coding guidelines
ship here; `reference/icd10cm-2026.sqlite` holds the ICD-10-CM tabular alone, and there is no
CPT or E/M reference at all. Map these elements to a level against the current guidelines,
not against this paragraph.

---

## Accounting

Every value the FILLED block declared is accounted for in step 1: F1, F3, F4 and F5 support
no code and the table says why for each; F2, F6, F7 and F8 each support codes, and every code
they support carries `SOURCE: filled` in step 3 **and** appears under `CODED, ANCHOR WAS
FILLED` in step 4. F9 through F22 support no code.

Every hedged entry in the Assessment is accounted for: coded where the encounter established
it, or sent to `NOT CODED, NOTHING ESTABLISHED IT` with the code the encounter does support
proposed in its place.

19 diagnosis codes proposed for entry, 3 of them marked `SOURCE: filled`.
12 differential code lines across 11 entries, none for entry.
8 codes withheld under `NOT CODED, NOTHING ESTABLISHED IT`.
1 CPT code proposed, carrying `verify this number`.
