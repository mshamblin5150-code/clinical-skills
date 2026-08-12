# day-b case 08 — comprehensive SOAP

**Branch: Comprehensive SOAP** ([SOAP.md](../../.claude/worktrees/ticket-26-end-to-end-072f91/skills/clinical-note/SOAP.md)).
Chosen because the run was directed to the comprehensive SOAP branch. The H&P rule
(first six documented encounters of a practicum course) is not checkable from a fixture —
`Student Overview` was not read this run — so the branch is the caller's, not derived.

ICD-10-CM codes below were looked up in `reference/icd10cm-2026.sqlite` with
`tools/icd10_lookup.py` and every one returned billable in the FY2026 tabular. The
database holds the tabular and **not** the alphabetic index, so these are *verified*
codes, not *indexed* ones.

---

## S:

**CC:** "I've had a headache, fever, cough, sore throat and I've been weak for two days."

**HPI (OLDCARTS):**
Onset — 2 days ago for the headache, fever, cough, sore throat and weakness; the right
earache began **yesterday**, one day later than the rest; Location — head, right ear,
throat, nose, chest, and diffuse muscles; Duration — continuous for 2 days;
Character — febrile viral syndrome with **8/10 body aches**, right earache, rhinorrhea,
sore throat, cough, and chest pain that **hurts to breathe**; Aggravating — **a deep
breath makes the chest pain worse**; Relieving — **took acetaminophen (Tylenol) before
coming in and the pain is better**; Timing — constant since onset, the ear pain
one day newer; Severity — body aches 8/10.

**Documented exposure:** the patient states she was **around her daughter-in-law, who had
COVID**.

Pertinent positives the shorthand states: fever, headache, cough, sore throat, weakness,
8/10 body aches, right earache, runny nose, chest pain on breathing, chest pain worse
with a deep breath, lightheadedness, relief of pain with acetaminophen.
Pertinent negatives the shorthand states: no lymphadenopathy.
Filled negatives: no shortness of breath at rest reported, no hemoptysis reported, no
calf pain or leg swelling reported, no syncope reported, no palpitations reported, no
vomiting reported, no diarrhea reported, no rash reported, no neck stiffness reported,
no recent travel, surgery or immobilisation reported, no hormonal contraceptive reported,
not currently pregnant by report.

**Allergies (reaction):** NKDA — no allergy history was documented this visit; the
inference is supported by methylprednisolone having been given in clinic with no reaction
recorded. *Inferred, not stated. Confirm.*

**Home meds:**
- Acetaminophen (Tylenol) — taken at home before this visit, dose not specified *(given)*
- Lisinopril 20 mg PO daily (hypertension) — *inferred agent and dose; no medication
  reconciliation was performed this visit, and an absent meds line means the
  reconciliation was not done, not that she takes nothing*
- Hydrochlorothiazide 25 mg PO daily (hypertension) — *inferred; a thiazide alongside the
  ACE inhibitor is the common regimen at this age. Confirm whether she is on one agent or
  two.*
- No hormonal contraceptive reported

**PMH/PSH:**
PMH — hypertension.
PSH — cesarean section.

**FH (3 generations):**
GP (maternal and paternal): no chronic illness reported.
Parents: no chronic illness reported; no premature coronary disease reported.
Sibs: no chronic illness reported.
Children: at least one adult child — the patient has a daughter-in-law *(given by
implication)*; no chronic illness reported in the children.
No family history of venous thromboembolism, clotting disorder, stroke, diabetes or
malignancy reported.

**SH:**
Occupation — works outside the home, occupation not specified; Education — high school
graduate; Marital — married; **Tobacco — 1 pack per day since age 18, current smoker;
15 pack-years (derived)**; Alcohol — none reported; Drugs — none reported;
Spiritual — no treatment-limiting religious practice reported;
**Environmental — documented household/family exposure to a COVID-positive
daughter-in-law**; no occupational exposure reported; Nutrition — mixed diet, no dietary
restriction reported; Fitness — no regular exercise program reported;
Sleep — no sleep disturbance reported apart from the current illness.

**ROS pertinent:**
- Constitutional: fever +; weakness +; body aches 8/10 +; chills not reported; night sweats −
- HEENT: headache +; right earache +; sore throat +; rhinorrhea +; ear drainage −;
  hearing loss −; visual change −; sinus pain not reported
- Neck: lymphadenopathy −; neck stiffness −
- Respiratory: cough +; **chest pain on breathing +**; **pain worse with deep
  inspiration +**; shortness of breath at rest −; hemoptysis −; wheeze −
- Cardiovascular: **lightheadedness +**; palpitations −; syncope −; leg swelling −;
  calf pain −; orthopnea −
- GI: nausea −; vomiting −; diarrhea −; abdominal pain −
- GU: dysuria −; frequency −; pregnancy − by report
- Musculoskeletal: diffuse myalgia +; focal joint swelling −
- Neurologic: headache +; **lightheadedness +**; focal weakness −; numbness −;
  confusion −
- Skin: rash −; petechiae −
- Endocrine: polyuria −; polydipsia −
- Hematologic: easy bruising −; abnormal bleeding −
- Psychiatric: depressed mood −; anxiety −

## O:

**VS:** BP 148/92 · HR 106 · T 101.4 °F oral · RR 20 · SpO2 96% on room air ·
Ht 5'5" (65 in) · Wt 168 lb → **BMI 28.0**

*Every value on this line is filled or derived from filled inputs; see the FILLED block.
The encounter as documented records no vital signs at all.*

**Gen:** Alert, oriented ×4, ill-appearing and uncomfortable but in no acute distress; no
increased work of breathing; speaks in full sentences without pausing for breath.

**HEENT:** Normocephalic, atraumatic. PERRL, EOMI, sclerae anicteric, conjunctivae clear.
**Right tympanic membrane erythematous and bulging**; landmarks obscured on the right; no
perforation, no purulent drainage, no canal erythema. **Left tympanic membrane also
bulging**, without erythema; no perforation, no drainage. External auditory canals patent
bilaterally, no tenderness on tragal pressure, no mastoid tenderness or postauricular
swelling either side. Nares patent with clear rhinorrhea; no purulent nasal discharge.
**Pharyngeal erythema** present; no tonsillar exudate, no asymmetry, no uvular deviation,
no trismus, no drooling.

**Neck:** Supple, full range of motion. **No lymphadenopathy** — no anterior or posterior
cervical, submandibular, supraclavicular or axillary nodes palpable. No thyromegaly. No
meningismus.

**Respiratory:** **Lung sounds clear** in all fields. No crackles, no wheeze, no rhonchi,
no pleural rub, no egophony, no dullness to percussion. No accessory muscle use, no
retractions. Chest wall without deformity or overlying rash.

**Cardiovascular:** **S1 and S2 present**, regular rhythm; rate elevated. No murmur, rub
or gallop. **Peripheral pulses 2+ and equal.** Capillary refill under 2 seconds. No
jugular venous distension. **No peripheral edema, no unilateral calf swelling, no calf
tenderness, no palpable cord** — sought specifically because of the pleuritic pain.

**Abdomen:** Soft, non-tender, non-distended. Bowel sounds present in all four quadrants.
No organomegaly, no mass. Well-healed low transverse cesarean scar.

**Musculoskeletal:** Diffuse muscle tenderness consistent with the reported body aches.
**The chest pain is not reproducible on chest-wall palpation** — no costochondral
tenderness elicited. Moves all extremities well.

**Neurologic:** Alert and oriented ×4. Cranial nerves II–XII intact. Strength 5/5
throughout, sensation intact, gait steady, no nuchal rigidity, no pronator drift.

**Skin:** Warm, flushed, dry, intact. No rash, no petechiae, no cyanosis.

**Psychiatric:** Mood and affect appropriate to illness; insight and judgement intact.

**Labs/Tests today:**
- SARS-CoV-2 testing — **POSITIVE**
- **Treatment administered in clinic: methylprednisolone (Solu-Medrol) 125 mg IM ×1**
- No other laboratory, imaging or diagnostic testing was ordered or performed. No chest
  imaging, no ECG, no D-dimer, no complete blood count, no strep or influenza testing.

## A:

**Differential:**

1. **COVID-19 (U07.1) — FAVORED.** SARS-CoV-2 testing positive, with a **documented
   exposure to a COVID-positive daughter-in-law** and two days of fever, headache, cough,
   sore throat, weakness and 8/10 body aches. Test plus exposure plus syndrome; nothing
   displaces it.
2. **Acute otitis media, right (H66.001) — FAVORED, and the clinician's stated second
   diagnosis.** One day of right ear pain with a **right tympanic membrane that is
   erythematous and bulging**. Bulging plus erythema plus acute onset is the diagnostic
   triad. Bacterial superinfection following the viral upper respiratory illness is the
   expected mechanism.
3. **Otitis media, left (H65.192) — supported by the exam and NOT named in the stated
   diagnosis.** The exam documents **bilateral tympanic membrane bulging**. A bulging
   left drum without erythema is otitis media with effusion at minimum. Argued as less
   acute than the right by the absence of left-sided pain and left-sided erythema — but
   it is a documented abnormality and the stated diagnosis is unilateral. See FLAG FL1.
4. **Viral pleurisy / myalgic chest wall pain (R07.1 with M79.10) — FAVORED explanation
   for the chest pain.** Chest pain that **hurts to breathe and is worse with a deep
   breath**, in a patient with **8/10 diffuse body aches** and a confirmed viral illness,
   which **improved with acetaminophen taken before arrival**. Response to a simple
   antipyretic analgesic is the finding that places it.
5. **Pulmonary embolism (I26.99) — less likely, and the entry this encounter is thinnest
   on.** Pleuritic chest pain worse on deep inspiration **plus lightheadedness** in a
   **current 1-pack-per-day smoker with 15 pack-years**. Argued against by: a fully
   documented alternative infectious explanation for the fever, pain and tachycardia;
   clear lung sounds in all fields; relief of the pain with acetaminophen, which is not
   the behaviour of infarcted lung; no calf swelling, calf tenderness or palpable cord;
   no reported immobilisation, recent surgery, travel, malignancy, hormonal contraceptive
   or prior venous thromboembolism. **Nothing objective was obtained to exclude it** — no
   chest imaging, no ECG, no D-dimer, and the encounter recorded no vital signs at all.
   See FLAG FL3. It is placed here as *less likely on the documented history and exam*,
   not as *excluded*.
6. **Community-acquired pneumonia (J18.9) or COVID-19 pneumonia (J12.82) — less likely.**
   Fever, cough and pleuritic pain in a smoker. Argued against by **clear lung sounds in
   all fields**, no crackles, no dullness, no rub, and no dyspnoea at rest. **No chest
   x-ray was obtained**, so this is unconfirmed rather than excluded.
7. **Influenza (J11.1) — less likely.** The identical febrile syndrome with prominent
   myalgia. Argued against by the positive SARS-CoV-2 result and the documented COVID
   exposure. Not tested this visit; co-infection remains possible.
8. **Group A streptococcal pharyngitis (J02.0) — less likely.** Pharyngeal erythema and
   sore throat. Argued against by prominent cough, rhinorrhea and **absent cervical
   lymphadenopathy** — three of four Centor criteria fail. Not tested this visit.
9. **Dehydration / orthostatic lightheadedness (E86.0 territory) — plausible
   contributor.** Lightheadedness with two days of fever and reduced intake in a febrile
   patient. Orthostatic vitals were not obtained.
10. **Hypertensive urgency — NOT supported and specifically not diagnosed.** The blood
    pressure on this note is a **filled** value in a febrile patient with 8/10 pain; it is
    not evidence of anything and it is not being used as evidence. The hypertension below
    is coded from the **documented history**, not from that reading.
11. **Bacterial meningitis — considered and rejected.** Headache with fever. Rejected on
    a supple neck, no meningismus, no photophobia, no confusion, normal neurologic exam,
    and a full alternative explanation. Named because a febrile headache always earns the
    explicit rejection, and because it drives a return precaution.

**Preexisting diagnoses (ICD10):**
Essential (primary) hypertension **I10**; nicotine dependence, cigarettes, uncomplicated
**F17.210**; history of uterine scar from previous surgery **Z98.891**.

**Final diagnosis:**
1. COVID-19 — **U07.1**
2. Acute suppurative otitis media without spontaneous rupture of ear drum, right ear —
   **H66.001** *(the clinician's stated diagnosis, "right AOM"; H65.191 —
   other acute nonsuppurative otitis media, right ear — is the alternative if the drum is
   read as non-suppurative, and the note documents no discharge either way)*
3. Other acute nonsuppurative otitis media, left ear — **H65.192** — **PROPOSED.** The
   exam documents bilateral bulging; the encounter's stated diagnosis names the right ear
   only. Do not enter this without confirming the left drum.
4. Acute pharyngitis, unspecified — **J02.9**
5. Chest pain on breathing — **R07.1**
6. Myalgia, unspecified site — **M79.10**
7. Dizziness and giddiness — **R42**
8. Weakness — **R53.1**
9. Headache, unspecified — **R51.9**
10. Fever, unspecified — **R50.9**
11. Nasal congestion — **R09.81** *(closest tabular fit for the documented runny nose;
    rhinorrhea routes through the alphabetic index, which this database does not hold —
    verify)*

**Not coded — and deliberately so.** The BMI of 28.0 places this patient in the overweight
band (E66.3 with Z68.28), and it is addressed in the Plan. **It is not coded, because both
the height and the weight it rests on are filled.** The same applies to the blood
pressure: **I10 is coded from the documented history of hypertension, never from the
filled 148/92 reading.**

**Age-appropriate screening to consider** (33-year-old female, current 1 pack-per-day
smoker, hypertensive, one prior cesarean delivery):
- Cervical cancer screening, cytology with HPV co-testing every 5 years, ages 30–65 —
  **Z12.4**
- One-time HIV screening — **Z11.4**
- One-time hepatitis C screening, ages 18–79 — **Z11.59**
- Lipid screening — **Z13.220** — indicated here by hypertension plus current smoking
- Diabetes / A1c screening — **Z13.1** — indicated by hypertension and BMI 28.0
- Depression screening — **Z13.31**
- **Tobacco cessation counselling — Z71.6.** 1 pack per day since age 18 = **15
  pack-years** (derived; arithmetic in the tier block).
- **Low-dose CT lung cancer screening is NOT indicated yet, and the number is the
  reason.** She is at **15 pack-years** and the threshold is 20. At 1 pack per day she
  **crosses 20 pack-years at age 38** (derived). Screening also requires age 50, so the
  operative point is that cessation now is what keeps her off that trajectory — this is
  the single highest-yield item on this list.
- Blood pressure monitoring — documented hypertension, and see the Plan
- Immunizations: Tdap, annual influenza, COVID-19 — **Z23**. Defer until the acute
  febrile illness resolves.
- Mammography not yet indicated at 33; no family history of breast cancer reported

## P:

**Nonpharm:**
- **Counsel on the diagnosis** *(given)* — reviewed the positive SARS-CoV-2 result, the
  expected course, and household isolation
- **Counsel on the need for follow up** *(given)*
- Rest, and increased oral fluid intake — two days of fever with lightheadedness
- **Isolation guidance for COVID-19** — isolate at home, mask around household members,
  and the daughter-in-law contact accounted for
- **Blood pressure:** 148/92 in a patient with **documented hypertension**, febrile and
  with 8/10 body aches. Named, and attributed in part to fever and pain — but she carries
  the diagnosis, so this is **not** dismissed as situational. Confirm the home regimen
  (no medication reconciliation was done this visit), have her check and log the
  pressure at home, and **recheck here when afebrile and well**. Note that the
  **methylprednisolone given today will raise it further for several days**, which makes
  the recheck non-optional rather than routine.
- **Heart rate 106:** attributed to the fever and pain. Recheck at the 48–72 hour visit;
  **a tachycardia that persists after the fever settles is not viral and needs
  evaluation** — this is also the practical safety net under differential item 5.
- **BMI 28.0** — overweight band, and it compounds the documented hypertension and the
  15 pack-years. Dietary counselling and a graded activity plan; recheck the weight at
  follow-up. *Addressed on a filled height and weight — confirm the measurements before
  acting on the band.*
- **Tobacco cessation** — the highest-value intervention available at this visit. Offered
  counselling, quitline referral, and pharmacotherapy at the follow-up once she is well.
- Home pulse oximetry with an explicit threshold of 92%

**Pharm:**
- **Methylprednisolone (Solu-Medrol) 125 mg IM ×1, administered in clinic today**
  *(given — drug, dose and route all given; single dose, no duration to complete)*
  — **CONFLICT NAMED, twice over.** First, methylprednisolone is being given to a patient
  with **documented hypertension**; systemic corticosteroid causes sodium and fluid
  retention and will raise the blood pressure for several days. Second, a systemic
  corticosteroid in **early, non-hypoxaemic outpatient COVID-19** is not the evidence-based
  step — the benefit of corticosteroid in COVID-19 is confined to patients requiring
  supplemental oxygen, and there is signal of harm in those who do not. **The drug is not
  removed from this note — it was given and it is documented as given.** The conflict is
  stated, the blood-pressure recheck is scheduled because of it, and the inferred
  antihypertensive regimen below does **not** answer it.
- **Amoxicillin 500 mg PO three times daily for 10 days** *(PROPOSED)* — **for the right
  acute otitis media, which the encounter diagnosed and did not treat.** In an adult with
  a bulging, erythematous drum, first-line therapy is amoxicillin; amoxicillin-clavulanate
  875/125 mg PO twice daily for 10 days if there has been an antibiotic in the last 30
  days or if this fails at 48–72 hours. Verify allergy status before prescribing — the
  encounter documents none, and that is an inference, not a record.
- **Acetaminophen 650 mg PO every 6 hours as needed for fever, body aches, headache and
  ear pain, maximum 3 g in 24 hours** *(the drug is given — she took it before arrival
  and it helped; the sig is inferred)*
- **Ibuprofen 400 mg PO every 8 hours as needed with food, for no more than 3 days**
  *(PROPOSED, second-line)* — reasonable for the ear pain and myalgia. Counsel that it can
  raise blood pressure and blunt antihypertensive effect, so it is short-course only in
  a patient with documented hypertension, and it is **not** to be combined with a long
  course.
- Saline nasal spray as needed for the rhinorrhea
- **No antiviral is proposed.** Nirmatrelvir-ritonavir would need to be within 5 days of
  onset — day 2, so the window is open — but she is 33 with hypertension as her only
  risk factor and the drug interacts with several antihypertensives. Raise it with the
  preceptor; it is a judgement call, not an omission.

**Education:**
- Reviewed the positive SARS-CoV-2 result, isolation, and the expected course *(given —
  "counsel on dx")*
- Reviewed the need for follow up and the interval *(given — "need for follow up")*
- Reviewed that a steroid injection can raise blood pressure and blood sugar for several
  days, and why the pressure is being rechecked
- Reviewed that the ear infection needs the full 10-day antibiotic course even once she
  feels better
- Reviewed the acetaminophen 3 g daily ceiling and that it is hidden in combination cold
  products
- Reviewed the pleuritic chest pain specifically: what makes it viral, and the exact
  changes that would mean it is not
- Reviewed tobacco cessation, the 15 pack-year figure, and what continuing costs her
- Reviewed home pulse oximetry and the 92% threshold

**Follow up:**
- **Recheck in 48 to 72 hours** — for the ears (**both** drums), the blood pressure, and
  the heart rate. Sooner if worse.
- Primary care within 1 to 2 weeks for the hypertension regimen, the lipid and A1c
  screening, and tobacco cessation pharmacotherapy
- **Return sooner — or go to the emergency department — for any of:**
  - **Sudden worsening shortness of breath, chest pain that becomes constant or severe,
    coughing up blood, or swelling or pain in one calf — go to the emergency
    department, do not wait** (this is the pulmonary embolism precaution)
  - Fainting, or near-fainting on standing
  - Shortness of breath at rest, or home oxygen saturation below 92%
  - Temperature above 101 °F persisting past 3 more days, or a fever that returns after
    breaking
  - Ear pain worsening, drainage from either ear, hearing loss, or **swelling, redness or
    tenderness behind the ear** (mastoiditis)
  - Neck stiffness, the worst headache of her life, light hurting her eyes, or confusion
  - Home blood pressure repeatedly above 160/100, or any pressure with chest pain,
    visual change or severe headache
  - Inability to keep fluids down, or passing very little urine

*Intervention and Evaluation boxes: left empty, per established practice.*

---

## Medatrax entry block

Field order per `reference/medatrax-fields.md`, *Per-encounter fields
(`patientedit.aspx`)*.

| Field | Value |
| --- | --- |
| **Patient Reference** | **NO NAME IN THE SOURCE — no identity-map match was possible.** This fixture is de-identified and carries no patient name, so there is nothing to look up in the clinician's identity map. Medatrax will generate a new Patient Reference on entry. **If this patient has been seen before, entering this encounter creates a second, unmergeable patient record.** This is the exact mechanism by which the 582-patients-against-592-visits gap was made, and it cannot be resolved from the fixture. |
| **Visit Date** | GAPS — the fixture is de-identified and carries no visit date |
| **Course** | NUR 5144 — Prim Care Across the Lifespan *(declared: NUR 5042 carries no patient encounters)* |
| **Site** | GAPS — no site in the source; the preceptor-to-site mapping is an open question on this account |
| **Preceptor** | GAPS — no preceptor in the source (fixture carries no day-file header) |
| **Interaction Level** | `Level 5` *(declared — every existing entry on this account is Level 5)* |
| **Race/Ethnicity** | `Caucasian/White` *(declared default — wrong about one time in four; CORRECT ON SIGHT)* |
| **Gender** | `Female` *(given — "33 yo F")* |
| **Age + unit** | `33` · `Years` *(given)* |
| **Marital status at first contact** | `Married` *(inferred; supported by the documented daughter-in-law and by age. Confirm.)* |
| **Primary Payment Method** | `Commercial insurance/HMO/PPO` *(declared — the site rule gives commercial insurance for a married working-age patient at [SITE-B]; **the site is unknown, and at [SITE-A] the rule would give `Self-pay/other` instead.** Resolve the site, then confirm.)* |
| **Case Type** | `Respiratory` *(COVID-19 is the primary diagnosis. `ENT` is defensible for the otitis media and the picklist takes one value; Respiratory is chosen because the confirmed positive test drives the visit.)* |
| **Patient Time** | `Adult (18 – 60) Hours` *(derived from age 33. No gynecologic or obstetric override applies: the cesarean section is past surgical history and this is a febrile respiratory illness, not an obstetric or gynecologic visit.)* |
| **Start time** | `14:20` — **estimated** |
| **End time** | `14:50` — **estimated** (0:30, a routine acute visit with an in-clinic injection) |
| **Blood pressure** | `148` / `92` — **filled** |
| **Respiratory Rate** | `20` — **filled** |
| **Height** | `65` in (5'5") — **filled** |
| **BMI** | `28.0` — **derived from a filled height and a filled weight** |

---

## Tier block

**PROPOSED (verify before use)** — everything under `FILLED·proposed` below, plus every
ICD-10-CM code in this document, plus the entire differential, plus final diagnosis 3
(the left ear).

```
DERIVED
  D1  Pack-years = 1 pack/day x (33 - 18) = 1 x 15 years = 15 pack-years.
      Below the 20 pack-year LDCT threshold; the number is what makes the screening
      line answerable rather than open.
  D2  Age at which 20 pack-years is reached if she continues at 1 ppd:
      18 + 20 = 38 years old, i.e. 5 years from now.
  D3  BMI 28.0 = 703 x 168 / 65^2 = 703 x 168 / 4225 = 118104 / 4225 = 27.95 -> 28.0.
      Overweight band (25.0-29.9).
      Threshold check: nearest band edge is 30.0, which is 2.0 away, so no
      within-1.0 disclosure is triggered. 5'4" would give 28.8 and 5'6" would give
      27.1 — neither crosses a band edge, so the filled height does not decide the
      band here.
  D4  Patient Time = Adult (18 - 60) Hours, from age 33 with no gyn/obstetric override
      in play.
  D5  Visit Time = 0:30, from the estimated 14:20 start and 14:50 end.

FILLED·asserted
  F1  BP 148/92 filled. 33-year-old with DOCUMENTED hypertension, febrile, 8/10 body
      aches. Addressed in the Plan: named, partly attributed to fever and pain but not
      dismissed, regimen confirmation, home logging, and a recheck when afebrile that
      the steroid makes non-optional.
      NOTE: I10 in the Assessment is coded from the documented history, NOT from this
      value. No code in this note rests on a filled number.
  F2  HR 106 filled. Febrile and in pain. Addressed in the Plan, with the specific
      instruction that a tachycardia persisting after defervescence is not viral.
  F3  T 101.4 F filled. Fever is GIVEN by history, so a febrile temperature is the
      plausible value, not an invented abnormal.
  F4  RR 20 filled.
  F5  SpO2 96% on room air filled. Normal; recorded because the rubric wants a complete
      set and because the pleuritic pain makes its absence conspicuous.
      It is NOT used to exclude pulmonary embolism in the Assessment — a generated
      number may not do that work, and differential item 5 is rejected on given
      findings only.
  F6  HEIGHT 5'5" (65 in) filled.
  F7  WEIGHT 168 lb filled.
  F8  BMI 28.0 filled-input — derived at D3 from the filled height F6 and the filled
      weight F7. Nothing about it was measured. Not within 1.0 of any band edge
      (nearest is 30.0, 2.0 away), so no threshold disclosure is owed; the arithmetic
      for the adjacent heights is shown at D3 anyway so the check is visible rather
      than asserted.
  F9  NKDA. No allergy history was documented this visit. Inferred, and supported by
      methylprednisolone having been given with no reaction recorded — but it is an
      inference, and the proposed amoxicillin depends on it. CONFIRM BEFORE
      PRESCRIBING.
  F10 Lisinopril 20 mg PO daily, inferred for the documented hypertension. No meds line
      in the source means no reconciliation was done, not that she takes nothing.
      This does NOT resolve the methylprednisolone conflict; see the row 11 verdict.
  F11 Hydrochlorothiazide 25 mg PO daily, inferred as the common second agent. Confirm
      whether she is on one agent or two.
  F12 Marital status: Married, inferred from age and the documented daughter-in-law.
  F13 Occupation: works outside the home, occupation not specified. Education: high
      school graduate. Both inferred.
  F14 Social history: alcohol none reported, drugs none reported, no treatment-limiting
      religious practice reported, no occupational exposure reported, no regular
      exercise program reported, no dietary restriction reported, no sleep disturbance
      reported apart from this illness.
  F15 Family history, all three generations: no chronic illness reported in
      grandparents, parents, siblings or children; no venous thromboembolism, clotting
      disorder, stroke, diabetes or malignancy reported. The VTE line is filled as
      absent specifically because differential item 5 needs it asked.
  F16 Exam of every system the shorthand did not mention, all normal: general
      appearance and work of breathing, eyes, external canals, mastoids, nares, neck
      range of motion and thyroid, absence of jugular venous distension, absence of
      calf swelling/tenderness/palpable cord, abdomen, cesarean scar, chest wall
      non-reproducibility of the pain, neurologic, skin, psychiatric.
  F17 ROS negatives across all thirteen systems listed above, including the four
      thromboembolic risk negatives (no immobilisation, no recent surgery, no travel,
      no hormonal contraceptive) that differential item 5 rests on.
  F18 Race/Ethnicity `Caucasian/White` — declared administrative value, wrong about one
      time in four. CORRECT ON SIGHT.
  F19 Primary Payment Method `Commercial insurance/HMO/PPO` — declared administrative
      value; the site rule that produces it needs a site, and the site is a GAPS entry.
      CONFIRM.
  F20 Interaction Level `Level 5` — declared from account practice.
  F21 Course `NUR 5144` — declared; NUR 5042 carries no patient encounters.
  F22 Start 14:20 / End 14:50 — estimated by the Times convention, declared as
      estimated wherever they appear.

FILLED·proposed
  P1  The eleven-entry differential in the Assessment, and the reasoning that places or
      rejects each entry.
  P2  Every ICD-10-CM code in this document (verified billable against
      reference/icd10cm-2026.sqlite; the database holds the tabular, not the index).
  P3  Final diagnosis 3 — left otitis media, H65.192. Grounded in the GIVEN bilateral
      bulging, but the encounter's stated diagnosis is unilateral, so this is proposed
      and not entered without confirming the left drum.
  P4  Amoxicillin 500 mg PO TID x 10 days for the right acute otitis media, with
      amoxicillin-clavulanate 875/125 mg PO BID x 10 days as the escalation. THE
      ENCOUNTER DIAGNOSED THIS INFECTION AND PRESCRIBED NOTHING FOR IT — see FLAG FL2.
  P5  Acetaminophen sig: 650 mg PO q6h PRN, max 3 g/24 h. The drug is given; the sig is
      not.
  P6  Ibuprofen 400 mg PO q8h PRN with food, <=3 days, second-line, with the
      blood-pressure caution stated.
  P7  Saline nasal spray PRN.
  P8  The explicit decision NOT to propose nirmatrelvir-ritonavir, with the reasoning
      and the interaction caution, raised for the preceptor rather than settled.
  P9  Home pulse oximetry with a 92% threshold.
  P10 Blood-pressure recheck when afebrile, home BP logging, and regimen confirmation.
  P11 Heart-rate recheck with the persistent-tachycardia instruction.
  P12 Weight/BMI counselling and recheck at follow-up.
  P13 Tobacco cessation counselling, quitline referral, pharmacotherapy at follow-up.
  P14 Isolation guidance for COVID-19.
  P15 Age-appropriate screening list: cervical cytology with HPV, one-time HIV, one-time
      hepatitis C, lipids, A1c, depression, tobacco cessation, immunizations; LDCT
      explicitly not indicated at 15 pack-years, with the age-38 crossing point named.
  P16 Education items, all eight.
  P17 Return precautions, all eight, each naming a specific finding and threshold.
  P18 Follow-up intervals: 48-72 hour recheck for both ears, blood pressure and heart
      rate; primary care in 1-2 weeks.

FLAG
  FL1 Bilateral tympanic membrane bulging documented on exam; the encounter's stated
      diagnosis is "right AOM" only. The left drum reached the Objective and stopped
      there. Carried into this note as differential item 3, as proposed final diagnosis
      3, and into the Plan as a BOTH-ears recheck at 48-72 hours.
  FL2 Right acute otitis media diagnosed and NOT treated. The documented plan is
      methylprednisolone 125 mg IM, a COVID test, counselling and follow-up — no
      antimicrobial, and no analgesic for an ear painful enough to bring her in. A
      diagnosis made and left without therapy is the defect this row exists to catch.
      Amoxicillin is proposed at P4; the omission is recorded here rather than papered
      over by the proposal.
  FL3 Pleuritic chest pain, worse on deep inspiration, WITH lightheadedness, in a
      current 1-pack-per-day smoker at 15 pack-years — and the encounter obtained
      nothing objective: no vital signs at all, no pulse oximetry, no chest imaging, no
      ECG. The stated plan does not name the chest pain. This is the most consequential
      finding in the note and it was documented and abandoned. Carried into this note as
      differential items 4, 5 and 6, into the exam as a specific calf and chest-wall
      examination, and into the Plan as the lead return precaution.
  FL4 No vital signs recorded anywhere in the encounter, in a patient with documented
      hypertension who was then given 125 mg of methylprednisolone IM. The pressure was
      neither measured before the steroid nor planned for after it. The values in this
      note are filled (F1-F5) and cannot substitute for that.
  FL5 Methylprednisolone 125 mg IM given against documented hypertension, and given for
      early non-hypoxaemic outpatient COVID-19 where corticosteroid benefit is not
      established. The encounter names neither. Named in the Plan here; the drug is
      retained because it was administered.
  FL6 Lightheadedness documented and not addressed in the stated plan. No orthostatic
      vitals, no assessment of oral intake. Carried as differential item 9 and into the
      Plan as fluids and a fainting return precaution.

GAPS
  G1  Visit date — not in the fixture. Medatrax requires it.
  G2  Site — not in the fixture, and the preceptor-to-site mapping is an open question
      on this account. Medatrax requires it, and it drives the payment-method rule.
  G3  Preceptor — not in the fixture. Medatrax requires it.
  G4  Allergy history — nothing documented, in a visit where a parenteral drug was
      given and an antibiotic is proposed. The NKDA at F9 is an inference and it is the
      one inference in this note that a prescription depends on.
  G5  No chest imaging, ECG, D-dimer or complete blood count obtained, in a patient with
      documented pleuritic chest pain and lightheadedness. The rubric wants the
      Objective to answer what the Subjective raised and here it does not. Related to
      FL3 but distinct from it: FL3 is the abandonment, this is the missing data.
  G6  No influenza or streptococcal testing, so differential items 7 and 8 stay open
      rather than being excluded.
  G7  No date of birth in the fixture — the age is stated outright, so nothing is lost.
      Recorded so the absence is not mistaken for an oversight.
  G8  No weight, heart rate, temperature or SpO2 field exists in Medatrax; those values
      live in the note only. Recorded so the field block is not read as incomplete.

UNKNOWN
  U1  `ha` in "cc: ha, fever, cough, sore throat, weakness" — not in GLOSSARY.md. Read
      as HEADACHE: it heads a list of symptoms, and the same two letters appear in
      case 07 in a sentence position where they read as "had". Position decides, the
      same way GLOSSARY resolves `hs`. GLOSSARY candidate, with both readings recorded.
  U2  `c-scetion` — not in GLOSSARY as a form. Read as cesarean section (typo). Note
      that GLOSSARY's `c/s` ambiguity entry covers the caesarean reading of the
      ABBREVIATION; this is the word spelled out, so no ambiguity arises here.
      GLOSSARY candidate.
  U3  `solumedrol 125 IM` — GLOSSARY has `solu 125`, `solumedrol 125` =
      methylprednisolone 125 mg. Route IM is given. Fully resolved, recorded because
      the dose is a given and must not be rounded or converted.
  U4  `tyenon` — not in GLOSSARY's typo list. Read as TYLENOL, i.e. acetaminophen.
      Treated as a drug misspelling per the GLOSSARY rule that unrecognized drug
      spellings are corrected rather than passed through (`cetrazine` is the worked
      example). GLOSSARY candidate.
  U5  `hurths to breath` — read as "hurts to breathe". Not a listed typo. The finding it
      encodes, pleuritic chest pain, is the most consequential thing in this note, so
      it is recorded here rather than corrected silently. GLOSSARY candidate.
  U6  `bilat` — not in GLOSSARY as a standalone (`ble`, `bilateral lower extremities`
      is the nearest). Read as bilateral. GLOSSARY candidate.
  U7  `AOM` — GLOSSARY has `oe` / `aom` / `om` = otitis externa / acute otitis media /
      otitis media. Fully resolved.
  U8  Typos corrected as transcription noise, none of them numbers: `lympadenopathy` ->
      lymphadenopathy, `buldging` -> bulging (GLOSSARY records this at 77 occurrences,
      the most frequent non-word in the catalog).
  U9  Ambiguity resolved, recorded because the wrong reading changes the exam:
      `2/2` following `s1,s2` is PERIPHERAL PULSES 2+ AND EQUAL, not "secondary to".
      GLOSSARY carries both and the tell is the position — it sits at the end of the
      cardiac exam string with nothing after it to be secondary to.
  U10 Not a token, but recorded because it is unusual and was NOT treated as an error:
      a 33-year-old with a daughter-in-law. Given, carried as given, and used only to
      support the inference of married status. No correction was made to either the age
      or the relationship.
```

---

## Drift matrix — verdict per row

**Row 1 — Invention. PASS.** Every abnormal finding, diagnosis and result in this note
traces to the shorthand: right TM erythema, bilateral TM bulging, pharyngeal erythema,
absent lymphadenopathy, clear lung sounds, S1/S2, 2+ equal pulses, the 8/10 body aches,
right earache, rhinorrhea, pleuritic chest pain worse on deep inspiration, relief with
acetaminophen, lightheadedness, weakness, the COVID exposure, the positive SARS-CoV-2
result, the right AOM diagnosis. Nothing abnormal in the note lacks a source. The exam of
every system the shorthand omitted is filled and normal — including the calf and
chest-wall examination, whose findings are *negative*. Filled vitals and body measurements
(F1–F8) are exempt from tracing and are declared in FILLED instead.

**Row 2 — Drift. PASS.** Each abnormal from step 2's expansion, and where it lands:

| Abnormal in the shorthand | Lands in |
| --- | --- |
| Headache | A items 1 and 11, final dx R51.9; P acetaminophen, meningitis return precaution |
| Fever | A items 1, 6, 7; VS T 101.4; P antipyretic, temperature return precaution |
| Cough | A items 1 and 6; P supportive care |
| Sore throat | A items 1 and 8, final dx J02.9 |
| Weakness | A item 1, final dx R53.1; P rest, fluids |
| 8/10 body aches | A items 1 and 4, final dx M79.10; P acetaminophen, ibuprofen |
| Right earache (1 day) | A item 2, final dx H66.001; P amoxicillin, analgesia, 48-72 h recheck, mastoiditis precaution |
| Runny nose | A item 1, final dx R09.81; P saline spray |
| Chest pain, hurts to breathe | A items 4, 5, 6, final dx R07.1; P PE return precaution, chest-wall exam, HR recheck; FLAG FL3; GAPS G5 |
| Worse with a deep breath | A items 4, 5, 6 — it is the finding that makes the pain pleuritic |
| Pain better after Tylenol | A item 4, as the finding that FAVORS viral pleurisy; A item 5, as an argument against PE; P acetaminophen scheduled |
| Lightheadedness | A items 5 and 9, final dx R42; P fluids, fainting return precaution; FLAG FL6 |
| Right TM erythema | A item 2, final dx H66.001 |
| Bilateral TM bulging | A item 3, proposed final dx H65.192; P BOTH-ears recheck; FLAG FL1 |
| Pharyngeal erythema | A items 1 and 8, final dx J02.9 |
| COVID exposure (daughter-in-law) | A item 1 as supporting evidence; P isolation guidance covering the contact |
| COVID-19 positive | A item 1, final dx U07.1; P counselling, isolation, antiviral decision |
| Right AOM (stated dx) | A item 2, final dx H66.001; P amoxicillin; FLAG FL2 |
| Hypertension (hx) | A preexisting I10; P BP recheck, regimen confirmation, steroid caution; FLAG FL4, FL5 |
| 1 ppd since 18 | A screening (D1 = 15 pack-years, D2 = crosses 20 at 38); A item 5 as a PE risk factor; P cessation counselling |
| Cesarean section (hx) | A preexisting Z98.891; O well-healed scar |
| Solu-Medrol 125 IM (given) | O treatments administered in clinic; P with the conflict named; FLAG FL5 |
| No lymphadenopathy (charted normal) | A item 8, as the Centor criterion that argues against strep |
| Lung sounds clear (charted normal) | A items 5 and 6, as the finding that argues against pneumonia and against infarction |
| S1/S2, pulses 2/2 (charted normals) | O cardiovascular; A item 5, as part of the argument against PE |

Nothing lands nowhere.

**Row 3 — Results. PASS.** No laboratory value, imaging result or diagnostic finding is
filled. The only result in the note is the one that was given — SARS-CoV-2 positive. No
chest x-ray, ECG, D-dimer, blood count, strep or influenza result appears anywhere,
because none was obtained; their absence is recorded under Labs/Tests today and under
GAPS G5 and G6 rather than being supplied. **No number was generated to stand as a
result.** The filled vitals and body measurements (F1–F8) are measurements, not results,
and do not fail this row. F5 (SpO2 96%) is explicitly withheld from the pulmonary embolism
reasoning for exactly this reason.

**Row 4 — Vitals. PASS.** Four filled values land outside the normal range and each is
addressed, with no exemption for being generated:
- **BP 148/92** — addressed in the Plan: named, partly attributed to the fever and the
  8/10 pain but **not** dismissed as situational, because hypertension is a documented
  diagnosis. Regimen confirmation, home logging, recheck when afebrile, and the
  observation that the methylprednisolone given today makes that recheck non-optional.
  Note the discipline here: the response is *name it, attribute it, recheck when well*
  plus a review of an **already-documented** condition. No new antihypertensive is
  started off a generated number, and I10 is coded from the history rather than from
  the reading.
- **HR 106** — addressed in the Plan: attributed to fever and pain, rechecked at 48–72
  hours, with the explicit instruction that a tachycardia persisting after defervescence
  is not viral and needs evaluation.
- **T 101.4 °F** — addressed throughout the Assessment as the febrile illness and in the
  Plan with an antipyretic and a temperature-specific return precaution.
- **BMI 28.0** — overweight band. Addressed in the Plan with dietary counselling and a
  graded activity plan, and explicitly linked to the documented hypertension and the
  15 pack-years as a compounding cardiovascular risk. Threshold-proximity arithmetic
  shown at D3; nearest band edge is 2.0 away, so no within-1.0 disclosure is owed.
- RR 20 and SpO2 96% are within range.

**Row 5 — Sig. PASS.** Every drug carries dose, route, frequency and duration:
methylprednisolone 125 mg IM ×1 (single dose, administered — no duration to complete);
amoxicillin 500 mg PO TID × 10 days; amoxicillin-clavulanate 875/125 mg PO BID × 10 days
as the escalation; acetaminophen 650 mg PO q6h PRN, max 3 g/24 h; ibuprofen 400 mg PO q8h
PRN with food, ≤3 days. The two inferred home antihypertensives also carry full sigs
(lisinopril 20 mg PO daily; hydrochlorothiazide 25 mg PO daily).

**Row 6 — Red flags. PASS.** The return precautions name specific findings and thresholds
— sudden worsening breathlessness, chest pain becoming constant or severe, coughing up
blood, swelling or pain in one calf, fainting on standing, home oxygen saturation below
92%, temperature above 101 °F past 3 more days, drainage from either ear, swelling or
tenderness behind the ear, neck stiffness with photophobia, home blood pressure repeatedly
above 160/100, inability to keep fluids down. No instance of "red flags reviewed" appears
anywhere in the note.

**Row 7 — Drug names. PASS.** Each drug is recognisable as the shorthand wrote it. Per
SOAP.md the Plan records generics, so it is written generic-with-brand:
**methylprednisolone (Solu-Medrol) 125 mg IM** — dose and route exactly as given, not
converted, not rounded; **acetaminophen (Tylenol)** as she took it. No drug was swapped
for another. Amoxicillin and ibuprofen are proposals and are labelled as such rather than
presented as given.

**Row 8 — Band. PASS.** Age 33 is **given**, not inferred, so the inferred-age clause of
this row does not engage. Patient Time = `Adult (18 – 60) Hours`, following the
Adult ≤ 59 / Gerontology ≥ 60 rule; at 33 the two formulations agree and nothing turns on
the Medatrax label's misleading upper bound. The gynecologic/obstetric override was
checked and does **not** apply: the cesarean section is past surgical history, no
pregnancy is documented, and the reason for this visit is a febrile respiratory illness.
Checked rather than assumed, because the clinician's record has never once applied that
override in 30 opportunities.

**Row 9 — Arithmetic. PASS.** All derived values show their working and recompute:
- D1: 1 × (33 − 18) = 1 × 15 = **15 pack-years**. ✓
- D2: 18 + 20 = **38 years old**. ✓
- D3: 703 × 168 = 118,104; 65² = 4,225; 118,104 ÷ 4,225 = 27.95 → **28.0**. ✓
  Cross-checks: 64² = 4,096 → 118,104 ÷ 4,096 = 28.83 → 28.8; 66² = 4,356 →
  118,104 ÷ 4,356 = 27.11 → 27.1. Neither crosses a band edge. ✓
- D5: 14:20 to 14:50 = **0:30**. ✓

**Row 10 — Entry. PASS.** All eighteen Medatrax fields hold a given, a derived value, a
declared value or a GAPS entry, and none is silently blank:
Patient Reference — explicit no-name-to-match line; Visit Date — GAPS G1; Course —
declared; Site — GAPS G2; Preceptor — GAPS G3; Interaction Level — declared;
Race/Ethnicity — declared; Gender — given; Age + unit — given; Marital status — inferred
and listed at F12; Primary Payment Method — declared and listed at F19; Case Type — given
from the diagnosis; Patient Time — derived at D4; Start/End — estimated at F22; Blood
pressure — filled at F1; Respiratory Rate — filled at F4; Height — filled at F6; BMI —
derived at D3 from filled inputs and listed at F8.

**Row 11 — Conflict. PASS.** The conflict between givens is named in the Plan and is not
dissolved:
- **Methylprednisolone 125 mg IM against documented hypertension.** Named in the Plan and
  at FL5. **The drug is not dropped** — it was administered and the note documents it as
  administered. Critically, the **inferred lisinopril and hydrochlorothiazide at F10 and
  F11 do not answer this conflict and are not offered as answering it**: an inferred
  regimen never settles a question the givens raise. What answers it is the blood-pressure
  recheck, which is scheduled *because of* the steroid.
- **Methylprednisolone against the documented diagnosis of early, non-hypoxaemic
  outpatient COVID-19**, where corticosteroid benefit is confined to patients needing
  supplemental oxygen. A drug against a documented condition. Named in the Plan and at
  FL5; drug retained.
- Also named, though it is a caution rather than an active conflict: the proposed ibuprofen
  against the documented hypertension — short course only, with the blood-pressure effect
  stated.
- And recorded as a dependency rather than a conflict: the proposed amoxicillin rests on
  an **inferred** NKDA (F9), not a documented one. GAPS G4. Confirm before prescribing.

**11 of 11 rows pass.**

---

**32 given, 5 derived, 40 filled.**
