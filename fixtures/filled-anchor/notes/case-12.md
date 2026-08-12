# day-b, case 12 — comprehensive SOAP

**Branch: Comprehensive SOAP** ([SOAP.md](../../skills/clinical-note/SOAP.md)). This regression run was directed to the comprehensive SOAP branch. The six-H&P-per-course rule (SKILL.md step 3) could not be checked against `Student Overview`, since no portal access was used for this run; if the current course holds fewer than six H&P forms, this encounter is an H&P regardless.

---

## S:

CC: "sore throat, cough, runny nose, congestion. started Saturday"

HPI (OLDCARTS):
Onset: Saturday, beginning after volleyball practice; Location: throat, nose, frontal and sphenoid sinuses, right side of the neck, right flank; Duration: from Saturday to the day of this visit. **The visit date is not recorded in the source, so the exact number of days does not compute and is carried as a gap, not as an estimate**; Character: sore throat, cough, nasal congestion, runny nose, sneezing, chills; Aggravating: none reported; Relieving: none reported; Timing: continuous since onset; Severity: not graded by the patient. Sick contact: her coach was sick on Saturday.

Pertinent negatives stated in the source: no abdominal pain. The source also records a bare "no pain", whose scope is ambiguous, see UNKNOWN; it is not read as a denial of the flank tenderness elicited later in the same exam.

Allergies (reaction): NKDA, no known drug allergies (given).

Home meds: no medication list was recorded this visit, so no medication reconciliation was performed. No chronic condition is documented, so no scheduled prescription medication is inferred. Whether over-the-counter cold remedies were taken at home before this visit is not documented. Contraceptive use, last menstrual period and pregnancy status are not documented, and that matters before any antifungal is prescribed, see GAPS.

PMH/PSH: bilateral acute otitis media; urinary tract infection, number of episodes and date not documented; former vaper, duration and quit date not documented. No surgical history documented.

FH (3 generations): GP: no chronic illness reported; Parents: no chronic illness reported; Sibs: no chronic illness reported. No family history was taken this visit.

SH: high school student; lives with parents or guardians; single; tobacco and nicotine: former vaper, does not currently vape or smoke; alcohol: none reported; drugs: no illicit drug use reported; spiritual: no treatment-limiting religious or cultural practice reported; environmental: sick contact at volleyball practice, no smoke exposure in the home reported; nutrition: regular adolescent diet; fitness: plays school volleyball, attends regular practice; sleep: 7 to 8 hours nightly.

ROS pertinent:
Constitutional: chills, present. Fever, present on the filled vital set today. No night sweats or weight loss reported.
HEENT: sore throat, present. Nasal congestion, rhinorrhea and sneezing, present. Frontal and sphenoid sinus pressure, present. No ear pain, no ear drainage, no visual change, no facial swelling, no eye swelling reported. History of bilateral acute otitis media.
Neck: right sided cervical lymphadenopathy, present. No neck stiffness, no difficulty swallowing, no trouble opening the mouth, no drooling reported.
Respiratory: cough, present. No shortness of breath, no wheezing, no chest pain with breathing reported.
Cardiovascular: no chest pain or palpitations reported.
GI: no abdominal pain (stated in the source). No nausea, vomiting or diarrhea reported.
GU: right costovertebral angle tenderness, present on exam. No dysuria, urinary frequency, urgency, hematuria or incontinence reported. **No vaginal discharge, itching, odor or irritation is documented anywhere in the source**, which matters because a yeast infection was diagnosed, see FLAG.
Skin: no rash reported.
Musculoskeletal: no joint pain or swelling reported. Symptoms began after volleyball practice.
Neuro: no headache, dizziness, photophobia or syncope reported.
Psych: no depressed mood or anxiety reported.
Heme/Lymph: right cervical node enlargement, present. No easy bruising or bleeding reported.

## O:

VS: BP 112/68, HR 98, T 100.6 F, RR 18, SpO2 99% on room air, Ht 5'5" (65 in), Wt 130 lb, BMI 21.6. All eight values are filled, see FILLED·asserted; the BMI is derived from the filled height and weight. **T 100.6 F is a filled abnormal and is worked up below.**

Gen: adolescent female, alert, well appearing, mildly ill appearing, no acute distress, no increased work of breathing.
HEENT: normocephalic, atraumatic. Conjunctivae clear, PERRL, EOMI, no periorbital swelling or erythema. TMs pearly grey bilaterally, no bulging, no effusion, no erythema. Nares with rhinorrhea and mucosal swelling. Tenderness to palpation over the frontal and sphenoid sinuses. Oropharynx with pharyngeal erythema; no tonsillar exudate, no asymmetry, no uvular deviation, no palatal petechiae.
Neck: supple. Right sided cervical lymphadenopathy, mobile. No posterior cervical chain enlargement, no meningismus.
Cardiovascular: regular rate and rhythm, S1 and S2 normal, no murmur, rub or gallop. Peripheral pulses 2+ and equal. Capillary refill under 2 seconds.
Respiratory: clear to auscultation bilaterally, no wheezing, no crackles, no rhonchi. Speaking in full sentences.
Abdomen: soft, non-tender, non-distended, bowel sounds present in all four quadrants, no guarding, no rebound. **Right costovertebral angle tenderness on percussion.** No left costovertebral angle tenderness. No hepatosplenomegaly, specifically no splenomegaly.
Genitourinary: **no genitourinary or pelvic examination is documented.** This is deliberately not filled as a normal exam, see FLAG 1 and GAPS.
Skin: warm, flushed, dry, no rash, no petechiae.
Neuro: alert and oriented to person, place and time, cranial nerves II through XII grossly intact, no nuchal rigidity, moves all extremities well.
Psych: normal mood and affect.

Labs/Tests today: rapid COVID-19 antigen, rapid group A streptococcus antigen with reflex throat culture, rapid influenza A and B antigen, urinalysis, microscopic urinalysis, urine culture and sensitivity, and monospot were **ordered**. **No result is recorded for any of them in the source**, so none is reported here and none is invented, see GAPS. No treatment was administered in clinic.

## A:

Differential:

- **Acute rhinosinusitis, frontal and sphenoid, most likely viral. Favored.** Supported by the given exam: positive frontal and sphenoid sinus pressure, rhinorrhea, pharyngeal erythema, nasal congestion, cough, sneezing and chills, with a documented sick contact (her coach was sick on Saturday) and an onset the same day. This is the diagnosis recorded in the source.
- **Acute bacterial rhinosinusitis. Cannot be settled from this record.** The criterion is symptoms persisting 10 days or more without improvement, or worsening after initial improvement, or a severe onset with high fever and purulent discharge for 3 to 4 consecutive days. Symptoms began Saturday, **but the visit date is not recorded, so the elapsed duration does not compute** and the 10-day criterion cannot be evaluated. No purulent nasal discharge is documented and no double-worsening is described. Antibiotics are therefore withheld today with an explicit conditional in the Plan.
- **Streptococcal pharyngitis. Less likely.** Argued against by prominent cough, rhinorrhea and sneezing, all viral features; no tonsillar exudate is documented; the adenopathy is right sided rather than bilateral anterior cervical. Modified Centor is low. Rapid strep with reflex culture is ordered.
- **Infectious mononucleosis. Less likely.** Argued against by unilateral right cervical adenopathy without posterior cervical chain involvement, no tonsillar exudate, no documented fatigue, and no splenomegaly on the abdominal exam. Monospot is ordered. Relevant beyond diagnosis: a positive result would mean no contact sport, and this patient plays volleyball.
- **Influenza. Possible.** Supported by abrupt onset, chills and a sick contact; argued against by prominent nasal and sinus localization. Rapid influenza is ordered.
- **COVID-19. Possible.** Same supporting features; testing is ordered.
- **Acute pyelonephritis, right. The finding that must not be lost.** Raised by **right costovertebral angle tenderness** together with chills, a filled temperature of 100.6 F, and a documented history of urinary tract infection. Argued against by the absence of any documented dysuria, frequency, urgency or hematuria, and by a soft non-tender abdomen. Urinalysis, microscopic urinalysis and urine culture and sensitivity are ordered, which is consistent with this having been the clinician's concern, **although no urinary diagnosis appears anywhere in the source diagnosis list**, see FLAG 2.
- **Musculoskeletal right flank strain. Plausible alternative** for the right costovertebral angle tenderness, since the illness began after volleyball practice and volleyball loads the trunk asymmetrically. Argued against by concurrent fever and chills; it does not explain the febrile illness and does not remove the need for the urinalysis.
- **Vulvovaginal candidiasis. Recorded as a given diagnosis, and unsupported by anything else in the record.** No vaginal discharge, itching, odor, irritation or dysuria is documented; no genitourinary or pelvic examination is documented; no wet mount, KOH preparation or vaginal pH was ordered among the seven tests that were. The diagnosis is carried here because it is a given and givens are not deleted, and it is flagged rather than dressed up, see FLAG 1.
- **Allergic rhinitis. Less likely.** Argued against by acute onset with chills and a documented sick contact rather than a seasonal or exposure pattern, and by the presence of fever.

Preexisting diagnoses (ICD10): personal history of urinary (tract) infections Z87.440; personal history of other specified conditions (bilateral acute otitis media) Z87.898; personal history of nicotine dependence (vaping) Z87.891.

Final diagnosis: acute sinusitis involving more than one sinus but not pansinusitis, frontal and sphenoid, **J01.80**. Secondary, each anchored to a given: acute pharyngitis, unspecified J02.9; cough, unspecified R05.9; nasal congestion R09.81; localized enlarged lymph nodes R59.0; costovertebral (angle) tenderness, right side R39.851; acute candidiasis of vulva and vagina B37.31, **flagged as unsupported and not to be entered until a supporting finding is documented**.

Coding notes, verified against `reference/icd10cm-2026.sqlite` on 2026-08-11:
- J01.80's inclusion term reads "acute sinusitis involving more than one sinus but not pansinusitis", which is exactly what the given exam documents (frontal and sphenoid). J01.10 and J01.30 individually, or J01.90 unspecified, are all less accurate. If the encounter is judged viral upper respiratory infection rather than sinusitis, J06.9 applies instead; the source recorded sinusitis, so J01.80 stands.
- **R50.9 (fever) is deliberately NOT coded.** The fever exists only in the filled vital set, and icd10-cpt declines to code off a filled value. R68.83 (chills without fever) is also not coded: chills is a given, but the filled temperature contradicts "without fever", and it would in any case rest on that filled value.
- **Z68.52 (BMI pediatric, 5th to less than 85th percentile) is deliberately NOT coded.** The BMI of 21.6 recomputes only from a filled height and a filled weight. Note the code set's own rule: pediatric BMI codes apply to persons aged 2 to 19, so a 16-year-old takes Z68.5-, never the adult Z68.1-Z68.45 band.
- R10.A1 (flank pain, right side) was considered and R39.851 chosen instead, because the source documents tenderness elicited on examination rather than pain reported by the patient; R10.- carries an Excludes2 pointing to R39.85 for costovertebral angle tenderness.
- N39.0 (urinary tract infection) is **not** coded. No urinalysis result exists, and coding it would be inventing a result.
- J01.80 carries a Use-Additional-Code instruction for the infectious agent (B95-B97). No organism is documented and none is invented.

Age-appropriate screening to consider (16-year-old female):
- Confidential adolescent psychosocial interview (HEEADSSS), conducted with the guardian out of the room.
- Depression screening annually from age 12 (PHQ-A), and anxiety screening from age 8 (GAD-7 or SCARED).
- Substance use screening (CRAFFT), including alcohol, cannabis and nicotine. She is a former vaper, so abstinence-maintenance counseling is indicated rather than cessation.
- Sexual history, and if sexually active: annual chlamydia and gonorrhea NAAT, and HIV screening once between 15 and 65. This is separately indicated by the recorded candidiasis diagnosis.
- **Cervical cancer screening is NOT indicated before age 21**, whatever the vulvovaginal diagnosis. Stated explicitly so it is not ordered reflexively off the given dx.
- Immunizations: HPV series completion, MenACWY booster at 16, Tdap, annual influenza, COVID-19 per current schedule.
- Blood pressure annually; a single lipid screen between 17 and 21; hearing and vision; scoliosis; dental.
- Sports pre-participation cardiac history and family history of sudden cardiac death, given that she plays school volleyball.
- Iron deficiency risk assessment in a menstruating adolescent athlete.

## P:

Nonpharm: rest; increased oral fluids; saline nasal irrigation or a neti pot with distilled or previously boiled water, 2 to 3 times daily; humidified air; warm salt water gargles for the sore throat; honey for cough; hand hygiene and covering coughs; **hold volleyball practice and play until afebrile for 24 hours without antipyretics**, and hold contact activity entirely until the monospot result is back, because splenic rupture is the risk if it is positive.

Pharm, none of which was prescribed in the source, see FLAG 3:
- Acetaminophen 650 mg PO every 6 hours as needed for fever or pain, maximum 3 g in 24 hours, for 5 days.
- Ibuprofen 400 mg PO every 6 to 8 hours as needed for fever or pain, with food, for 5 days.
- Fluticasone propionate nasal spray 50 mcg, 1 spray in each nostril once daily, for 14 days.
- Sodium chloride 0.65% nasal spray, 1 to 2 sprays in each nostril as needed, for 14 days.
- **No antibiotic today.** Withheld deliberately pending the urinalysis and urine culture, and pending a bedside determination of how many days the sinus symptoms have run, since that is the number the bacterial rhinosinusitis decision turns on and it does not compute from this record. **If pyelonephritis is confirmed, nitrofurantoin must not be the agent**: it does not achieve therapeutic concentrations in the renal parenchyma, and this patient has right costovertebral angle tenderness. Cephalexin 500 mg PO four times daily for 10 to 14 days, or a culture-directed agent, is the proposal instead.
- Fluconazole 150 mg PO as a single dose for the recorded vulvovaginal candidiasis, **conditional and not to be dispensed until a supporting symptom or examination finding is documented and last menstrual period and pregnancy status are established.** The diagnosis currently rests on nothing in the record.

Education: nasal irrigation technique and water safety; the expected viral course, peaking around days 3 to 6 and improving by day 10, and the specific instruction to call if symptoms are still present at day 10 or worsen after initially improving, because that is what changes the antibiotic decision; why no antibiotic was given today; that the seven ordered tests will be called back and roughly when; antipyretic dosing and the maximum daily acetaminophen dose; continued nicotine abstinence; hand hygiene to protect teammates and household members.

Follow up: 3 to 5 days, or sooner on callback of the urine culture, or immediately for any return precaution. Recheck the temperature and the right costovertebral angle at that visit. A callback plan for all seven pending results must be documented; none exists in the source, see FLAG 4.

Return precautions, return same day or go to the emergency department for: **fever above 101 F that persists more than 3 days, or any new fever after 5 days of illness**; **worsening right flank or back pain**; **vomiting or inability to keep fluids down**; **burning with urination, or blood in the urine**; **severe headache with a stiff neck or light sensitivity**; **swelling, redness or pain around the eye, or any change in vision or double vision**; **facial swelling or forehead swelling**; **difficulty breathing or swallowing, drooling, or inability to open the mouth fully**; **a neck lump that is rapidly enlarging, red or exquisitely tender**; **new rash, especially one that does not blanch**; **left upper abdominal or left shoulder pain after any impact, if the monospot returns positive**.

Intervention: (left empty, per SOAP.md.)

Evaluation: (left empty, per SOAP.md.)

---

## Medatrax entry block

Emitted in the field order of [reference/medatrax-fields.md](../../reference/medatrax-fields.md), `patientedit.aspx`.

**PATIENT IDENTITY: no name to match.** The fixture carries `[PT]`, a de-identification placeholder, and no name. There is therefore nothing to look up in the clinician's identity map, and this encounter cannot be matched to an existing Patient Reference. It must be entered as a **NEW PATIENT**, and if this person has been seen before, that will create a second, unmergeable Medatrax record. A documented history of urinary tract infection and of bilateral acute otitis media makes a prior visit to this practice entirely plausible, which makes the unmatchable identity a live risk here rather than a theoretical one.

| Field | Value |
| --- | --- |
| Patient Reference | NEW PATIENT (generated by Medatrax on save). No name in the source, so no identity-map match was possible. |
| Visit Date | GAPS: not stated in the fixture. This also blocks the symptom-duration computation. |
| Course | GAPS: not stated in the fixture. Presumed NUR 5144. |
| Site | GAPS: not stated in the fixture. |
| Preceptor | GAPS: not stated in the fixture. |
| Interaction Level | GAPS: not stated in the fixture. Every existing Medatrax entry is `Level 5`. |
| Race/Ethnicity | `Caucasian/White` (declared default, wrong about once in four, correct on sight) |
| Gender | `Female` (given) |
| Age + unit | `16` `Years` (given) |
| Marital status at first contact | `Single` (age 16) |
| Primary Payment Method | `Medicaid` (declared, pediatric patient under the Welch pattern). The site is a GAPS, so the site-keyed rule could not be applied; if this was Bluestone the value is `Self-pay/other`. Correct on sight. |
| Case Type | `ENT` (given: sinusitis, pharyngitis, cervical lymphadenopathy) |
| Patient Time | `Pediatric (0 – 17) Hours` (derived from age 16). See the row 8 verdict for the gynecologic-override ruling. |
| Start time | `17:50` (estimated) |
| End time | `18:20` (estimated) |
| Visit Time | `0:30` (derived from start and end) |
| Blood pressure | `112` / `68` (filled) |
| Respiratory Rate | `18` (filled) |
| Height | `5'5"` (65 in) (filled) |
| BMI | `21.6` (derived from the filled height and the filled weight of 130 lb; there is no weight field in Medatrax, so the weight lives in the note only) |

---

## Tier block

```
DERIVED           1. BMI 21.6 = 703 x 130 / 65^2 = 91,390 / 4,225 = 21.63, rounds to 21.6.
                     Both inputs are filled, so this line also appears under FILLED·asserted.
                  2. Patient Time = Pediatric (0 – 17) Hours, from age 16.
                  3. Visit Time = 0:30, from 17:50 to 18:20.
                  NOT DERIVED, because it does not compute: symptom duration. Onset is given
                  as Saturday, but the visit date is absent from the source, so the elapsed
                  days cannot be computed. A value that does not compute is a gap, never an
                  estimate, so no duration is asserted anywhere in the note and the 10-day
                  bacterial rhinosinusitis criterion is left explicitly unsettled. GAPS 2.

FILLED·asserted   VITALS AND MEASUREMENTS, each carrying its value as written in the note body:
                  1. BP 112/68 filled. Normal for a 16-year-old female at roughly the 50th to
                     75th height percentile; band set by age, sex and height percentile, and
                     positioned mid-band by an otherwise well adolescent athlete.
                  2. HR 98 filled. Upper-normal for age, consistent with the filled fever.
                  3. T 100.6 F filled. ABNORMAL BY DESIGN AND WORKED UP. Chills are documented
                     as a given, a sick contact is documented, and the encounter is an acute
                     febrile-illness workup, so a low-grade fever is the value this patient
                     most plausibly had. Not the middle of the normal range. Addressed in the
                     Assessment (pyelonephritis consideration, influenza and COVID-19), in the
                     Plan (antipyretics, hold play until afebrile 24 hours, recheck at follow
                     up) and in the return precautions. NOT coded, see the coding notes.
                  4. RR 18 filled. Normal for age.
                  5. SpO2 99% on room air filled. Normal; the lung exam is clear.
                  6. HEIGHT 5'5" (65 in) filled. Plausible for a 16-year-old female,
                     approximately the 50th to 75th percentile.
                  7. WEIGHT 130 lb filled. Plausible for that height and age.
                  8. BMI 21.6 filled inputs (height AND weight both filled); arithmetic on the
                     DERIVED line. Approximately the 60th percentile for a 16-year-old female,
                     which is normal weight, so no drift row 4 workup is triggered by it. NOT
                     within 1.0 of 18.5, 25, 30, 35 or 40: nearest thresholds are 18.5 at a
                     distance of 3.1 and 25.0 at a distance of 3.4, so no threshold-proximity
                     disclosure is required. NOT coded, because icd10-cpt declines to code off
                     a filled value.
                  HISTORY, MEDICATIONS, FAMILY, SOCIAL, ADMINISTRATIVE:
                  9.  Home medications: no scheduled prescription medication inferred, because
                      no chronic condition is documented. This is an inference from the rest
                      of the encounter, not a claim that the patient takes nothing; whether
                      over-the-counter cold remedies were used at home is undocumented and is
                      stated as such rather than written as "none".
                  10. Family history, three generations, grandparents, parents and siblings:
                      no chronic illness reported. No family history was taken this visit.
                  11. Marital status: single, from age 16.
                  12. Education and occupation: high school student.
                  13. Household: lives with parents or guardians.
                  14. Alcohol: none reported.
                  15. Illicit drugs: none reported.
                  16. Spiritual and cultural: no treatment-limiting practice reported.
                  17. Environmental: no smoke exposure in the home reported. The sick contact
                      at volleyball practice is a GIVEN, not part of this fill.
                  18. Nutrition: regular adolescent diet.
                  19. Sleep: 7 to 8 hours nightly.
                  20. ROS negatives across all systems the source does not document
                      (cardiovascular, skin, neuro, psych, and the unmentioned parts of
                      HEENT, respiratory, GI and GU). All normal, absent or not reported.
                  21. Physical examination of every system the source does not document
                      (general, eyes, ears, nose, neck beyond the given node, cardiovascular,
                      respiratory, the non-tender parts of the abdomen, skin, neuro, psych).
                      All normal. NOTE THE ONE DELIBERATE EXCLUSION: the genitourinary and
                      pelvic exam is NOT filled as normal. Filling it would either contradict
                      the given candidiasis diagnosis or manufacture support for it, and a
                      charted diagnosis means an abnormal was charted, so silence about that
                      region is a documentation defect rather than evidence of normality.
                  22. Race/Ethnicity: Caucasian/White. Declared default, wrong about once in
                      four, correct on sight.
                  23. Primary Payment Method: Medicaid. Declared under the Welch pediatric
                      pattern; the Site is a GAPS, so the site key could not be applied and
                      this needs a glance.
                  24. Start time 17:50 and End time 18:20, estimated by the Times convention
                      (12-encounter walk-in shift, 08:00 start, 12 hours; encounter 12 of 12,
                      30 minutes as a routine acute visit). Estimated, not missing.

FILLED·proposed   PROPOSED (verify before use). The source prescribed nothing at all, so the
                  entire pharmacologic plan is proposed.
                  25. Acetaminophen 650 mg PO q6h PRN fever or pain, max 3 g/24 h, x 5 days.
                  26. Ibuprofen 400 mg PO q6-8h PRN fever or pain, with food, x 5 days.
                  27. Fluticasone propionate nasal spray 50 mcg, 1 spray each nostril daily,
                      x 14 days.
                  28. Sodium chloride 0.65% nasal spray, 1 to 2 sprays each nostril PRN,
                      x 14 days.
                  29. Deliberate withholding of any antibiotic today, pending the urine
                      results and a bedside determination of symptom duration.
                  30. Named exclusion of nitrofurantoin if pyelonephritis is confirmed, since
                      it does not reach the renal parenchyma, with cephalexin 500 mg PO four
                      times daily for 10 to 14 days or a culture-directed agent proposed
                      instead.
                  31. Fluconazole 150 mg PO x 1 dose for the recorded candidiasis, CONDITIONAL
                      on a supporting finding being documented first, and on last menstrual
                      period and pregnancy status being established.
                  32. Pelvic or external genital examination with wet mount, KOH and vaginal
                      pH before the candidiasis diagnosis is entered or treated.
                  33. Rest, fluids, saline irrigation, humidified air, salt water gargles,
                      honey for cough, hand hygiene.
                  34. Hold volleyball until afebrile 24 hours, and hold contact activity until
                      the monospot returns, because of splenic rupture risk.
                  35. Age-appropriate screening list for a 16-year-old female, including the
                      explicit statement that cervical cancer screening is not indicated
                      before 21 despite the recorded vulvovaginal diagnosis.
                  36. Return precautions, naming specific findings including orbital and
                      intracranial complications of sinusitis, pyelonephritis progression and
                      post-mononucleosis splenic rupture.
                  37. Follow-up interval of 3 to 5 days or on culture callback, with a
                      temperature and costovertebral angle recheck.
                  38. A documented callback plan for the seven pending results.
                  39. Patient education content: the viral sinus timeline and the day-10
                      rule, why no antibiotic was given, antipyretic dosing, nasal irrigation
                      water safety, nicotine abstinence maintenance.
                  40. The ten-entry differential beyond the two given diagnoses.

FLAG              1. dx `yeast infection` is recorded with NOTHING in the source supporting it.
                     No vaginal discharge, itching, odor, irritation or dysuria is documented;
                     no genitourinary or pelvic examination is documented; and none of the
                     seven ordered tests is a wet mount, KOH or vaginal pH. The diagnosis
                     reached the source Assessment and stopped there, with no treatment and no
                     confirmatory test. It is carried into this note because it is a given and
                     givens are not deleted, and the fluconazole proposed for it is explicitly
                     conditional. CONFIRM OR REMOVE THIS DIAGNOSIS BEFORE ENTRY.
                  2. Right costovertebral angle tenderness undiscussed in the source diagnosis
                     list. It is documented in the exam, and urinalysis, microscopic urinalysis
                     and urine culture and sensitivity were ordered, which shows the concern
                     existed, but neither `sinusitis` nor `yeast infection` accounts for a
                     flank finding and no urinary diagnosis is recorded. Carried here as the
                     pyelonephritis versus flank-strain differential.
                  3. Both given diagnoses were left untreated. The source plan contains seven
                     tests and no medication of any kind, no supportive care and no follow-up
                     interval. The entire pharmacologic and non-pharmacologic plan in this note
                     is PROPOSED.
                  4. Seven tests ordered with no result recorded and no callback plan
                     documented. The result absence is GAPS 7; the absent callback plan is the
                     flag, because a rapid strep, a monospot and a urine culture with nobody
                     assigned to act on them is a finding-in, nothing-out failure by design.
                  5. Internal contradiction in the source: a bare `no pain` in the history
                     against `right cva tenderness` elicited in the same exam. Resolved in the
                     note by reading `no pain` narrowly and not as a denial of the flank
                     finding, and named here rather than smoothed over. See UNKNOWN 1.
                  6. dx `sinusitis` is recorded, but whether it meets acute bacterial criteria
                     cannot be determined, because the visit date is absent and the elapsed
                     duration does not compute. The note does not upgrade it to bacterial and
                     does not prescribe an antibiotic on it.

GAPS              1. Visit Date: not in the fixture.
                  2. Symptom duration in days: does not compute, because onset (Saturday) is
                     given and the visit date is not. Not estimated.
                  3. Course: not in the fixture.
                  4. Site: not in the fixture. This also blocks the site-keyed Primary Payment
                     Method rule.
                  5. Preceptor: not in the fixture.
                  6. Interaction Level: not in the fixture.
                  7. Results for all seven ordered tests: rapid COVID-19, rapid group A strep,
                     rapid influenza, urinalysis, microscopic urinalysis, urine culture and
                     sensitivity, monospot. Ordered and never returned in the source. No value
                     is invented for any of them.
                  8. Genitourinary and pelvic examination: not documented, despite a recorded
                     vulvovaginal diagnosis.
                  9. Vaginal discharge, itching, odor and irritation history: not documented,
                     same reason.
                  10. Last menstrual period, pregnancy status, contraceptive use and sexual
                      history: not documented, and all four are needed before the proposed
                      fluconazole and before any sexually transmitted infection screening.
                  11. Number of prior urinary tract infections and date of the most recent:
                      not documented, which matters for a recurrent-UTI assessment.
                  12. Vaping duration and quit date: not documented.
                  13. Immunization status, including HPV series and the age-16 MenACWY
                      booster: not documented.
                  14. Whether over-the-counter symptom relief was already tried at home: not
                      documented.

UNKNOWN           1. `no pain` — ambiguous scope, carried verbatim. It sits between the
                     history and the exam findings and does not say what is pain free. Read
                     narrowly as a denial of pain at that point in the history; explicitly NOT
                     read as a denial of the right costovertebral angle tenderness elicited in
                     the same exam, nor as contradicting the given sore throat. Flagged, not
                     guessed at silently. FLAG 5.
                  2. `covid`, `strep`, `flu` as ordered tests — not in GLOSSARY.md. Expanded
                     from context to rapid COVID-19 antigen, rapid group A streptococcus
                     antigen and rapid influenza A and B antigen. Belong in the glossary's
                     tests table.
                  3. `right cva tenderness` — RESOLVED, not unknown. GLOSSARY.md lists `CVA`
                     as ambiguous between costovertebral angle and cerebrovascular accident,
                     and the stated tell is the neighboring word: `CVA tenderness` is
                     anatomical. Read as costovertebral angle. Reading it as a stroke would
                     have invented one in a 16-year-old.
                  4. `bilat aom` — bilateral acute otitis media, from the glossary's `aom`.
                     In a history, so it is a past condition, not an active diagnosis.
                  5. `spot mono` — in GLOSSARY.md as monospot. Applied as such.
                  6. `micro urine` and `c/s` — in GLOSSARY.md. `c/s` is ambiguous between
                     culture and sensitivity and caesarean section; it is attached to a
                     specimen here (`urine c/s`), so it is culture and sensitivity. Reading
                     it the other way in a 16-year-old female would have been catastrophic.
                  7. `former vaper` — plain English, carried as a nicotine history.
                  Typos corrected as transcription noise, per the Given rules: `saturdy` and
                  `satufday` to Saturday, `neeezing` to sneezing, `coash` to coach,
                  `lypmadenopathy` to lymphadenopathy, `sinuse` to sinus, `rinorhea` to
                  rhinorrhea. No number was altered. Every other token in the source is
                  expanded or verbatim.
```

---

## Drift matrix, all 11 rows

**Row 1 — Invention. PASS.** Every abnormal finding, diagnosis and result in the note traces to a given: sore throat, cough, runny nose, congestion, Saturday onset, chills, sneezing, the sick contact, onset after volleyball practice, right sided cervical lymphadenopathy, positive frontal and sphenoid sinus pressure, rhinorrhea, pharyngeal erythema, right costovertebral angle tenderness, no abdominal pain, the history of bilateral acute otitis media and of urinary tract infection, the former vaping, NKDA, the seven ordered tests, and both recorded diagnoses. The filled BP, HR, T, RR, SpO2, height, weight and BMI are exempt from tracing and are declared in FILLED with their values. **No exam finding, symptom or result was filled, and the genitourinary exam was specifically left unfilled rather than fabricated in either direction.**

**Row 2 — Drift. PASS, with six FLAGs recorded.** Each abnormal from the step 2 expansion, and where it lands:
- Sore throat: Assessment, acute pharyngitis J02.9 and the strep and mononucleosis entries; Plan, salt water gargles, analgesia, rapid strep.
- Cough: Assessment, R05.9 and the viral entries; Plan, honey, hydration.
- Runny nose, congestion, rhinorrhea, sneezing: Assessment, J01.80 and R09.81; Plan, saline irrigation, intranasal steroid.
- Chills: Assessment, febrile illness, pyelonephritis and influenza entries; Plan, antipyretics.
- Frontal and sphenoid sinus pressure: Assessment, drives the choice of J01.80 over J01.90; Plan, intranasal steroid, irrigation, orbital and intracranial return precautions.
- Pharyngeal erythema: Assessment, pharyngitis and strep entries; Plan, rapid strep with reflex culture.
- Right cervical lymphadenopathy: Assessment, R59.0 with the strep and mononucleosis entries; Plan, monospot, rapid strep, and the rapidly-enlarging-node return precaution.
- **Right costovertebral angle tenderness: Assessment, pyelonephritis versus flank strain, coded R39.851; Plan, urinalysis and culture, the nitrofurantoin exclusion, recheck at follow up, flank return precautions. Landed nowhere in the source diagnosis list, so FLAG 2.**
- Sick contact: Assessment, supports viral etiology; Plan, hand hygiene, hold play.
- Onset after volleyball practice: Assessment, supports the flank-strain alternative; Plan, hold play.
- No abdominal pain (given negative): Assessment, argues against pyelonephritis and appears in the abdominal exam.
- History of UTI: Assessment, preexisting Z87.440 and raises the pyelonephritis pretest probability.
- History of bilateral AOM: Assessment, preexisting Z87.898; Objective, TM exam documented.
- Former vaper: Assessment, Z87.891 and the screening list; Plan, abstinence-maintenance counseling.
- **dx sinusitis: Assessment, final diagnosis J01.80. FLAG 6 for the undeterminable bacterial criterion.**
- **dx yeast infection: Assessment, carried and coded B37.31 with a flag; Plan, conditional fluconazole and a confirmatory exam. Untreated and unsupported in the source, so FLAG 1.**
- Seven ordered tests: all appear in Objective as ordered and in the Plan with a callback requirement. **No result invented; FLAG 4 and GAPS 7.**
- Filled T 100.6 F: Assessment and Plan, as set out in row 4.
Nothing lands nowhere.

**Row 3 — Results. PASS.** No laboratory value, imaging result or diagnostic finding is filled. Seven tests were ordered and **not one result is reported**, because none exists in the source. `Labs/Tests today` says so explicitly rather than leaving the line for someone else to complete, as SOAP.md requires. No urinalysis finding, no strep result, no monospot result and no culture organism appears anywhere in the note, and N39.0 is deliberately not coded for exactly that reason. The eight filled vitals and body measurements are not results and do not fail this row.

**Row 4 — Vitals. PASS.** Of the eight filled values, seven are within the normal range for a 16-year-old female (BP 112/68, HR 98, RR 18, SpO2 99%, the height and weight as inputs, and BMI 21.6 at approximately the 60th percentile). **One is outside it: T 100.6 F.** It is addressed and not merely recorded: it appears in the Assessment as part of the pyelonephritis, influenza and COVID-19 entries; in the Plan as acetaminophen and ibuprofen with doses, as holding volleyball until afebrile 24 hours, and as a temperature recheck at follow up; and in the return precautions with a specific threshold and time course. No exemption was taken for it being generated. And the workup is proportionate: the response is antipyresis, the testing already ordered, and a recheck, not the investigation of a condition nothing documented.

**Row 5 — Sig. PASS.** Acetaminophen 650 mg, PO, every 6 hours as needed, 5 days. Ibuprofen 400 mg, PO, every 6 to 8 hours as needed, 5 days. Fluticasone propionate 50 mcg, 1 spray each nostril, intranasal, once daily, 14 days. Sodium chloride 0.65%, 1 to 2 sprays each nostril, intranasal, as needed, 14 days. Fluconazole 150 mg, PO, single dose, one day. Cephalexin 500 mg, PO, four times daily, 10 to 14 days (conditional). Every drug carries dose, route, frequency and duration. No drug was given in the source, so nothing was carried over incompletely.

**Row 6 — Red flags. PASS.** The return precautions name specific findings: fever above 101 F persisting more than 3 days or any new fever after day 5, worsening right flank or back pain, vomiting or inability to keep fluids down, burning with urination, blood in the urine, severe headache with stiff neck or light sensitivity, swelling or redness around the eye or any vision change or double vision, facial or forehead swelling, difficulty breathing or swallowing, drooling, inability to open the mouth, a rapidly enlarging or red neck lump, a new non-blanching rash, and left upper abdominal or left shoulder pain after impact if the monospot is positive. No phrase of the "red flags reviewed" kind appears.

**Row 7 — Drug names. PASS, vacuously in one direction and honored in the other.** The source names **no drug at all**, so there is nothing to convert and nothing that could read differently from how the shorthand wrote it. Every drug in the note is a proposal and is written generically, as SOAP.md's *Generic names in the Plan* rule requires. The glossary's `macrobid` caution was applied in the other direction: nitrofurantoin is named and explicitly excluded rather than silently omitted, because it does not reach the renal parenchyma and this note carries a costovertebral angle finding.

**Row 8 — Band. PASS.** Age 16 is given outright in the unmarked-adjacent form `16 yo F.`, so no inference and no `FILLED·asserted` age line is required. 16 falls in `Pediatric (0 – 17) Hours`; the Adult-at-or-below-59 and Gerontology-at-60 boundaries do not reach it. **The gynecologic override was checked and deliberately declined, with the reasoning stated rather than skipped**, because the reference records that the override has never once been applied in 30 opportunities and is therefore the row's known failure mode. It does not apply here: the presenting complaint, the entire history, the whole examination and six of the seven ordered tests are for an acute upper respiratory illness, and the recorded `yeast infection` is a single incidental diagnosis with no supporting documentation whatsoever (FLAG 1). The override is for a visit *for* gynecologic care, as the reference's own example of a 35-year-old seen for hormone review shows. **If the clinician confirms that a genuine gynecologic evaluation took place, this band changes to `Women's Health` and the pediatric hours move with it, so this is worth his glance.** Case Type `ENT` is set independently and does not alter the band.

**Row 9 — Arithmetic. PASS.** Two computations, both shown and both recomputed here, plus one refusal:
- BMI: 703 x 130 = 91,390. 65 x 65 = 4,225. 91,390 / 4,225 = 21.63, rounds to **21.6**. Correct.
- Visit Time: 17:50 to 18:20 = **0:30**. Correct.
- Symptom duration: **refused, not estimated.** Onset Saturday is given; the visit date is absent; the subtraction has no second operand. Recorded as GAPS 2, and no day count appears anywhere in the note.

**Row 10 — Entry. PASS.** Every Medatrax field in the reference's order holds a given (Gender, Age, Case Type), a derived value (Patient Time, BMI, Visit Time), a declared value (Race/Ethnicity, Primary Payment Method, Start and End time, and the four filled vital and measurement fields), or a GAPS entry (Visit Date, Course, Site, Preceptor, Interaction Level). Patient Reference holds the explicit NEW PATIENT line with the reason no identity-map match was possible. No field is blank and none is silently skipped.

**Row 11 — Conflict. PASS.** The source contains no medication at all, so there is no drug-against-condition and no drug-against-drug conflict between givens to name. The row is nonetheless honored in both of its prohibitions. **No inferred medication resolves anything:** the unsupported `yeast infection` diagnosis is not made to look reasonable by prescribing fluconazole for it, which is why that prescription is written as conditional on a supporting finding being documented first, and why the diagnosis is carried under FLAG 1 rather than quietly justified. **No given is dropped to dissolve a difficulty:** the `yeast infection` diagnosis is unsupported and awkward, and it stays in the note and in the coded list, flagged; the bare `no pain` contradicts the elicited right costovertebral angle tenderness and both are kept, with the tension named in FLAG 5 rather than one of them deleted. Among the proposed drugs, acetaminophen, ibuprofen, intranasal fluticasone, saline and fluconazole carry no interaction with each other; ibuprofen is compatible with a normal renal picture and is reconsidered if the urinalysis suggests pyelonephritis, which is stated in the Plan.

**11 of 11 rows pass.** Six FLAGs are recorded in the tier block; none of them is a failing row silently repaired, and each names the finding and what was not done with it.

---

**34 given, 3 derived, 39 filled.**

Counting rule: each element is counted once, in its primary tier. The FILLED block carries 40 numbered items; item 8, the BMI, appears on both the `DERIVED` and `FILLED·asserted` lines as SKILL.md requires, and is counted once, as derived. 40 minus 1 = 39 filled. Symptom duration is counted in no tier: it does not compute, so it is a gap.
