# day-b case 07 — comprehensive SOAP

**Branch: Comprehensive SOAP** ([SOAP.md](../../.claude/worktrees/ticket-26-end-to-end-072f91/skills/clinical-note/SOAP.md)).
Chosen because the run was directed to the comprehensive SOAP branch. The H&P rule
(first six documented encounters of a practicum course) is not checkable from a fixture —
`Student Overview` was not read this run — so the branch is the caller's, not derived.

ICD-10-CM codes below were looked up in `reference/icd10cm-2026.sqlite` with
`tools/icd10_lookup.py` and every one returned billable in the FY2026 tabular. The
database holds the tabular and **not** the alphabetic index, so these are *verified*
codes, not *indexed* ones — a code that verifies is still the wrong code if the
condition maps elsewhere in the index.

---

## S:

**CC:** "I've had a cough, a sore throat, sinus pain, fever and chills, and my left ear
has been hurting for two days."

**HPI (OLDCARTS):**
Onset — 2 days ago, abrupt; Location — throat, sinuses, left ear, chest, and separately
the epigastrium and right upper quadrant; Duration — continuous for 2 days; Character —
cough with sore throat and sinus pressure, left ear pain, generalized febrile
malaise, and a 7/10 headache; Aggravating — not documented; Relieving — not documented;
Timing — constant since onset, no diurnal pattern documented; Severity — headache 7/10.

Pertinent positives the shorthand states: fever, chills, cough, sore throat, sinus pain,
left ear pain, 7/10 headache, epigastric pain, right upper quadrant pain.
Pertinent negatives the shorthand states: no lymphadenopathy.
Filled negatives: no shortness of breath at rest reported, no chest pain reported, no
hemoptysis reported, no vomiting reported, no diarrhea reported, no dysuria reported,
no hematuria reported, no rash reported, no syncope reported, no confusion reported.

**Allergies (reaction):**
- Prednisone — reaction not documented
- Sulfamethoxazole-trimethoprim (Bactrim) — reaction not documented
- Doxycycline — reaction not documented
- Cetirizine (Zyrtec) — reaction not documented
- Norfloxacin (Noroxin) — reaction not documented
- Phenazopyridine (Pyridium) — reaction not documented

Six documented drug allergies, no reaction recorded for any of them. See GAPS.

**Home meds:**
- Statin, agent and dose not specified in the source — "on statin" (hyperlipidemia)
- Atorvastatin 40 mg PO daily (hyperlipidemia) — *inferred agent and dose for the
  documented statin; confirm before entry*
- Omeprazole 20 mg PO daily (gastro-esophageal reflux disease) — *inferred*
- Acetaminophen 650 mg PO q6h PRN (arthritis pain) — *inferred*
- Diclofenac 1% topical gel, apply to affected joints QID PRN (arthritis) — *inferred*
- No medication reconciliation was performed this visit; the list above is the likely
  regimen for the documented conditions, not a reconciled list.

**PMH/PSH:**
PMH — hyperlipidemia (on a statin); gastro-esophageal reflux disease; arthritis;
seasonal allergies; vaccinations **not** up to date.
PSH — total hysterectomy; dilation and curettage ×2.

**FH (3 generations):**
GP (maternal and paternal): no chronic illness reported.
Parents: no chronic illness reported; no premature coronary disease reported.
Sibs: no chronic illness reported.
Children: no chronic illness reported.
No family history of malignancy, stroke, diabetes or liver disease reported.

**SH:**
Occupation — retired; Education — high school graduate; Marital — married;
Tobacco — former smoker, less than 0.25 packs per day for 3 years, quit; less than 0.75
pack-years; Alcohol — none reported; Drugs — none reported; Spiritual — no
treatment-limiting religious practice reported; Environmental — no occupational or
household exposure reported, no smoke exposure reported; Nutrition — mixed diet, low
fiber and low fluid intake reported in the context of the constipation; Fitness — no
regular exercise program reported, limited by arthritis; Sleep — no sleep disturbance
reported apart from the current illness.

**ROS pertinent:**
- Constitutional: fever +; chills +; fatigue +; weight loss −
- HEENT: sinus pain +; sore throat +; left ear pain +; headache 7/10 +; rhinorrhea not
  reported; visual change −; hearing loss −; ear drainage −
- Neck: lymphadenopathy −
- Respiratory: cough +; shortness of breath at rest −; hemoptysis −; pleuritic pain −
- Cardiovascular: chest pain −; palpitations −; edema −; orthopnea −
- GI: epigastric pain +; right upper quadrant pain +; constipation +; nausea −;
  vomiting −; melena −; hematochezia −; jaundice −
- GU: right flank pain +; dysuria −; frequency −; hematuria −; incontinence −
- Musculoskeletal: chronic joint pain +, at baseline; new joint swelling −
- Neurologic: headache +; focal weakness −; numbness −; syncope −; confusion −
- Skin: rash −; jaundice −
- Endocrine: hyperlipidemia +; polyuria −; polydipsia −
- Hematologic: easy bruising −; bleeding −
- Psychiatric: depressed mood −; anxiety −

## O:

**VS:** BP 138/84 · HR 98 · T 100.9 °F oral · RR 20 · SpO2 95% on room air ·
Ht 5'4" (64 in) · Wt 172 lb → **BMI 29.5**

*Every value on this line is filled or derived from filled inputs; see the FILLED block.*

**Gen:** Alert, oriented ×4, ill-appearing but in no acute distress; no increased work of
breathing; speaks in full sentences.

**HEENT:** Normocephalic, atraumatic. PERRL, EOMI, sclerae anicteric, conjunctivae clear.
**Left tympanic membrane with an effusion** — fluid behind the drum; no perforation, no
purulent drainage, landmarks visible. Right tympanic membrane pearly grey, mobile, normal
landmarks. External auditory canals patent, no canal erythema or tenderness. Nares patent,
nasal mucosa without edema, no purulent nasal discharge observed. Maxillary and frontal
sinuses without overlying swelling or erythema; sinus pain is reported rather than
elicited. **Pharyngeal erythema** present; no tonsillar exudate, no asymmetry, no uvular
deviation, no trismus. Dentition in adequate repair.

**Neck:** Supple, full range of motion. **No lymphadenopathy** — no anterior or posterior
cervical, submandibular, supraclavicular or axillary nodes palpable. No thyromegaly. No
meningismus.

**Respiratory:** **Lungs clear in the apices, diminished in the bases**, bilaterally. No
crackles, no wheeze, no rhonchi, no egophony, no dullness to percussion documented. No
accessory muscle use, no retractions. Cough non-productive on observation.

**Cardiovascular:** Regular rate and rhythm, S1 and S2 present, no murmur, rub or gallop.
Peripheral pulses 2+ and equal. Capillary refill under 2 seconds. No jugular venous
distension. No peripheral edema.

**Abdomen:** Soft, non-distended. Bowel sounds present in all four quadrants.
**Tenderness in the epigastrium and the right upper quadrant** on palpation. No rebound,
no guarding, no rigidity. Murphy's sign negative. McBurney's point non-tender, Rovsing's
sign negative, psoas and obturator signs negative. No hepatosplenomegaly appreciated, no
mass, no hernia.

**Back/flank:** **Right costovertebral angle tenderness** to percussion. Left
costovertebral angle non-tender. Thoracolumbar spine non-tender to midline palpation.

**Musculoskeletal:** Moves all extremities well. No new joint effusion, warmth or
erythema. Chronic degenerative changes without acute findings.

**Neurologic:** Alert and oriented ×4. Cranial nerves II–XII intact. Strength 5/5 in all
four extremities, sensation intact, gait steady, no pronator drift, no nuchal rigidity.

**Skin:** Warm, dry, intact. No rash, no petechiae, no jaundice, no cyanosis.

**Psychiatric:** Mood and affect appropriate to illness; insight and judgement intact.

**Labs/Tests today:**
- SARS-CoV-2 testing — **POSITIVE**
- Abdominal x-ray — **stool burden consistent with constipation**
- Aspartate aminotransferase **48** (elevated)
- Alkaline phosphatase **136** (elevated)
- Influenza testing — sent, result not recorded
- Rapid streptococcal testing — sent, result not recorded
- Respiratory syncytial virus testing — sent, result not recorded
- Complete blood count — sent, result not recorded
- Comprehensive metabolic panel — sent; the AST and ALP above are the only values
  recorded
- Amylase — sent, result not recorded
- Lipase — sent, result not recorded
- Urinalysis with microscopic — sent, result not recorded
- Urine culture and sensitivity — sent, result not recorded
- Chest x-ray — ordered, result not recorded; the clinic will telephone with x-ray results
- No treatment was administered in clinic.

## A:

**Differential:**

1. **COVID-19 (U07.1) — FAVORED.** SARS-CoV-2 testing positive; two days of fever,
   chills, cough, sore throat, sinus pain and a 7/10 headache; pharyngeal erythema on
   exam. The positive test plus the matching syndrome places this and nothing displaces
   it.
2. **Constipation (K59.00) — FAVORED, second problem.** Abdominal x-ray shows a stool
   burden. Explains at least part of the epigastric discomfort. Confirmed on imaging, not
   inferred.
3. **COVID-19 with lower respiratory tract involvement / early viral pneumonia (J12.82) —
   cannot be excluded.** Breath sounds are **diminished at both bases** in a
   SARS-CoV-2-positive 67-year-old. Argued against by clear apices, no crackles, no
   egophony, no dullness to percussion, no dyspnoea at rest and an oxygen saturation of
   95%. **The chest x-ray is the arbiter and its result is not recorded** — this is not
   settled by the exam.
4. **Acute pyelonephritis or urinary tract infection (N10 / N39.0) — cannot be excluded.**
   **Right costovertebral angle tenderness** with fever and chills. Argued partly against
   by an alternative documented explanation for the fever and by the absence of dysuria,
   frequency or hematuria. **Urinalysis, microscopic urinalysis and urine culture were all
   sent and none has returned**, so this diagnosis is open, not rejected.
5. **Acute otitis media with effusion, left (H65.92) — supported.** Left ear pain of two
   days with a left tympanic membrane effusion in the setting of a viral upper respiratory
   infection. Argued against being suppurative by the absence of bulging, drum erythema,
   perforation and purulent drainage.
6. **Acute pharyngitis, viral (J02.9) — supported, and attributed to the COVID-19.**
   Pharyngeal erythema with sore throat.
7. **Group A streptococcal pharyngitis (J02.0) — less likely.** Argued against by
   prominent cough, coryzal sinus pain, **absent cervical lymphadenopathy** and no
   tonsillar exudate — three of the four Centor criteria fail. Rapid strep was sent;
   result not recorded.
8. **Influenza (J11.1) — less likely.** Same febrile respiratory syndrome, and this
   patient's **vaccinations are not up to date**. Argued against by the positive
   SARS-CoV-2 result; co-infection remains possible and the influenza test result is not
   recorded.
9. **Acute bacterial rhinosinusitis (J01.90) — less likely.** Sinus pain and headache
   are present, but at **two days** the illness is far short of the 10-day persistence or
   double-worsening pattern that distinguishes bacterial from viral rhinosinusitis, and
   no purulent nasal discharge was observed.
10. **Biliary disease — cholelithiasis or biliary colic (K80.20) — less likely but not
    excluded.** **Right upper quadrant pain with an alkaline phosphatase of 136** is the
    combination that raises it. Argued against by a negative Murphy's sign, a
    non-colicky pain description and no fatty-food trigger documented. **No right upper
    quadrant ultrasound was obtained**, so this is unresolved.
11. **Statin-associated hepatocellular injury (R74.01 with Z79.899) — plausible
    contributor.** **AST 48 on a statin.** Argued incompletely: statin injury is
    typically transaminase-predominant, and the **concurrent alkaline phosphatase of 136
    is a cholestatic pattern a statin does not usually produce** — which is why the
    referral back to the primary care provider matters and why item 10 stays open.
12. **GERD-related epigastric pain (K21.9) — plausible contributor, not sufficient
    alone.** Documented reflux disease with epigastric tenderness. Does not account for
    the right upper quadrant pain or the alkaline phosphatase.
13. **Respiratory syncytial virus infection — less likely.** Tested, result not recorded;
    displaced by the positive SARS-CoV-2 result.
14. **Nephrolithiasis / renal colic (N23) — least likely.** Right costovertebral angle
    tenderness is the only support. Argued against by non-colicky pain, no hematuria
    reported, and an abdominal film that showed stool and did not report a calculus.

**Preexisting diagnoses (ICD10):**
Hyperlipidemia **E78.5**; gastro-esophageal reflux disease without esophagitis **K21.9**;
unspecified osteoarthritis **M19.90**; acquired absence of both cervix and uterus
**Z90.710**; personal history of nicotine dependence **Z87.891**; other underimmunization
status **Z28.39**; other long term (current) drug therapy **Z79.899** (statin);
allergy status to sulfonamides **Z88.2**; allergy status to other antibiotic agents
**Z88.1** (doxycycline, norfloxacin); allergy status to other drugs **Z88.8**
(prednisone, cetirizine, phenazopyridine).

**Final diagnosis:**
1. COVID-19 — **U07.1**
2. Constipation, unspecified — **K59.00**
3. Unspecified nonsuppurative otitis media, left ear — **H65.92**
4. Acute pharyngitis, unspecified — **J02.9**
5. Costovertebral (angle) tenderness, right side — **R39.851**
6. Right upper quadrant pain — **R10.11**
7. Epigastric pain — **R10.13**
8. Elevation of levels of liver transaminase levels — **R74.01**
9. Abnormal levels of other serum enzymes (alkaline phosphatase) — **R74.8**
10. Headache, unspecified — **R51.9**
11. Fever, unspecified — **R50.9**

**Not coded — and deliberately so.** The BMI of 29.5 places this patient in the
overweight band (E66.3 with Z68.29), and it is addressed in the Plan. **It is not coded,
because both the height and the weight it rests on are filled**, and a code may not rest
on a generated value. Confirm the measurements and the code follows.

**Age-appropriate screening to consider** (67-year-old female, former minimal smoker,
hyperlipidemia on a statin, status post total hysterectomy, vaccinations not up to date):
- Colorectal cancer screening through age 75 — **Z12.11**
- Screening mammography — **Z12.31**
- Osteoporosis screening / DEXA, indicated for all women at 65 and over — **Z13.820**
- **Cervical cancer screening is not indicated** — total hysterectomy for benign
  indication (Z90.710); no cervix. **Z12.4 does not apply.**
- Lipid monitoring on statin therapy — **Z13.220**
- Diabetes screening, A1c — **Z13.1** (hyperlipidemia as a risk factor)
- **Low-dose CT lung cancer screening is NOT indicated.** Less than 0.25 packs per day
  for 3 years is **less than 0.75 pack-years** (derived, arithmetic in the tier block) —
  far below the 20 pack-year threshold, and she is a former smoker with a trivial burden.
  Stating the number is what closes the question rather than leaving it open.
- Abdominal aortic aneurysm ultrasound not indicated — female
- Depression screening — **Z13.31**
- Fall-risk assessment, hearing and vision screening — appropriate at 67
- **Immunizations: vaccinations are documented as not up to date (Z28.39).** Influenza,
  COVID-19, pneumococcal, recombinant zoster, Tdap, and RSV by shared decision-making at
  60–74 — **Z23**. Defer all of them until the acute febrile illness has resolved.

## P:

**Nonpharm:**
- Supportive care *(given)*
- Rest *(given)*
- Drink plenty of fluids *(given)* — and specifically to support both the febrile illness
  and the constipation
- Increase dietary fibre and daily fluid intake for the constipation; regular ambulation
  as arthritis allows
- **Isolation guidance for COVID-19** — isolate at home, mask around household members,
  day-0 counting explained
- **Home pulse oximetry**, with a threshold given (below 92%) — the bases are diminished
  and the chest x-ray has not returned
- **Weight and BMI:** BMI 29.5 is in the overweight band. Dietary counselling and a
  graded activity plan compatible with arthritis; recheck the weight at the primary care
  follow-up. *This is addressed on a filled height and weight — confirm the measurements
  before acting on the band.*
- **Blood pressure:** 138/84 is at the stage-1 threshold in a patient with **no
  documented hypertension**, febrile and with a 7/10 headache. Do not diagnose
  hypertension on a single reading during an acute illness — **recheck when afebrile and
  well**, and again at the primary care visit.
- Do not drive or make important decisions while febrile and headachy

**Pharm:**
- **Docusate sodium (Colace) 100 mg PO twice daily for up to 7 days, then as needed**
  *(drug given; dose, route, frequency and duration inferred)*
- **Polyethylene glycol 3350 (Miralax) 17 g dissolved in 8 oz of liquid, PO once daily
  for up to 7 days** *(drug given; sig inferred)*
- **Acetaminophen (Tylenol) 650 mg PO every 6 hours as needed for fever and headache,
  maximum 2 g in 24 hours, for no more than 3 days** *(drug given; sig inferred)*
  — **CONFLICT NAMED:** acetaminophen is being recommended against a documented
  **AST of 48 and alkaline phosphatase of 136**. The drug is not withdrawn — it was
  prescribed and it is the safer of the two analgesics offered here — but the ceiling is
  lowered from the usual 3 g to **2 g in 24 hours**, the course is capped at 3 days, and
  the patient is told to avoid all other acetaminophen-containing products. The elevated
  liver enzymes are the reason, and the primary care follow-up is where the enzymes get
  rechecked.
- **Ibuprofen (Motrin) 200–400 mg PO every 6 to 8 hours as needed, with food, for no more
  than 3 days** *(drug given; sig inferred)*
  — **CONFLICT NAMED, and this one is the serious one:** ibuprofen is being recommended
  to a 67-year-old with **documented gastro-esophageal reflux disease**, **documented
  epigastric and right upper quadrant tenderness**, **elevated liver enzymes**, and
  **right costovertebral angle tenderness with the urinalysis and creatinine not yet
  returned**. An NSAID against that combination risks gastric injury and, if the flank
  finding is renal, acute kidney injury. **The drug is not dropped from the list** — it
  was given — but the conflict is stated in the note, the omeprazole in the inferred
  regimen does **not** settle it, and the recommendation is that acetaminophen be used
  first and ibuprofen only if acetaminophen fails, at the lowest dose, with food, and
  **not at all** if the urinalysis returns abnormal.
- **No antibiotic is prescribed today**, and that is correct — the documented diagnosis is
  COVID-19.

**Contingency — read the allergy list before prescribing:**
- **If the urinalysis or urine culture returns positive**, this patient's allergy list
  removes **sulfamethoxazole-trimethoprim, doxycycline and norfloxacin** — and
  norfloxacin's presence is a reason to treat the whole fluoroquinolone class with
  caution — and removes **phenazopyridine** for symptomatic relief. **Nitrofurantoin is
  the obvious remaining oral agent and it must not be used here**: it does not achieve
  therapeutic concentrations in the renal parenchyma, and the documented finding is
  **costovertebral angle tenderness**, i.e. the exact site it does not reach. A
  beta-lactam such as cefpodoxime or cefdinir, or amoxicillin-clavulanate, is the
  workable choice pending sensitivities.
- **If the COVID-19 illness progresses to hypoxaemia**, the standard step is a systemic
  corticosteroid — and **prednisone is a documented allergy**. The reaction is not
  recorded, so the severity is unknown. This must be resolved before any steroid is
  given, not discovered at the point of need.

**Education:**
- Reviewed the positive SARS-CoV-2 result, the expected course, and isolation
- Reviewed how to use home pulse oximetry and the 92% threshold
- Reviewed the acetaminophen daily ceiling and the reason it is lowered, and that
  acetaminophen is hidden in many combination cold products
- Reviewed why ibuprofen carries extra risk for her specifically — reflux, epigastric
  tenderness, liver enzymes, flank tenderness — and that acetaminophen comes first
- Reviewed the constipation regimen and that Miralax takes 1–3 days to work
- Reviewed that the **clinic will telephone with the x-ray results** *(given)*
- Reviewed that her **vaccinations are not up to date** and that catch-up happens once
  she is well
- Reviewed that the six drug allergies must be repeated to every prescriber

**Follow up:**
- **Follow up with the primary care provider for the elevated liver enzymes — AST 48,
  alkaline phosphatase 136, on a statin** *(given)*. Repeat the hepatic panel; the
  cholestatic component warrants considering a right upper quadrant ultrasound and a
  review of the statin.
- The clinic will telephone with the abdominal and chest x-ray results *(given)*
- Recheck here in 3 to 4 days if not improving, and in all cases for the ear
- **Return sooner — or go to the emergency department — for any of:**
  - Temperature above 101 °F persisting past 3 more days, or a fever that returns after
    breaking
  - Shortness of breath at rest, home oxygen saturation below 92%, or chest pain
  - Worsening right flank pain, or flank pain with vomiting or inability to keep fluids
    down
  - Right upper quadrant pain becoming constant or severe, yellowing of the eyes or
    skin, dark urine, or pale stools
  - No bowel movement in 3 days despite Miralax and Colace, abdominal swelling, or
    vomiting
  - Left ear pain worsening, drainage from the ear, hearing loss, or swelling and
    redness behind the ear
  - Confusion, fainting, new weakness on one side, or a stiff neck
  - Black or bloody stools, or vomiting material that looks like coffee grounds (on
    ibuprofen)

*Intervention and Evaluation boxes: left empty, per established practice.*

---

## Medatrax entry block

Field order per `reference/medatrax-fields.md`, *Per-encounter fields
(`patientedit.aspx`)*.

| Field | Value |
| --- | --- |
| **Patient Reference** | **NO NAME IN THE SOURCE — no identity-map match was possible.** This fixture is de-identified and carries no patient name, so there is nothing to look up in the clinician's identity map. Medatrax will generate a new Patient Reference on entry. **If this patient has been seen before, entering this encounter creates a second, unmergeable patient record.** This is the exact mechanism by which the 582-patients-against-592-visits gap was made, and it cannot be resolved from the fixture. |
| **Visit Date** | GAPS — the fixture is de-identified and carries no visit date |
| **Course** | NUR 5144 — Prim Care Across the Lifespan *(declared: NUR 5042 carries no patient encounters, so a patient encounter can only belong to 5144)* |
| **Site** | GAPS — no site in the source. Day files name the preceptor and never the site, and the preceptor-to-site mapping is an open question on this account. |
| **Preceptor** | GAPS — no preceptor in the source (fixture carries no day-file header) |
| **Interaction Level** | `Level 5` *(declared — every existing entry on this account is Level 5)* |
| **Race/Ethnicity** | `Caucasian/White` *(declared default — wrong about one time in four; CORRECT ON SIGHT)* |
| **Gender** | `Female` *(given — "67 yo F")* |
| **Age + unit** | `67` · `Years` *(given — no inference, no date of birth needed)* |
| **Marital status at first contact** | `Married` *(inferred from age 67 per the Conventions; confirm)* |
| **Primary Payment Method** | `Medicare` *(declared — the site rule gives Medicare from about 60 at [SITE-B]; **the site is unknown, and at [SITE-A] the rule would give `Self-pay/other` instead.** Resolve the site, then confirm this field.)* |
| **Case Type** | `Respiratory` *(COVID-19 is the primary diagnosis; the ENT and GI findings are secondary and the picklist takes one value)* |
| **Patient Time** | `Gerontology (60 and>) Hours` *(derived from age 67. **Not** `Adult (18 – 60) Hours` — the Medatrax label's own upper bound of 60 is misleading and the clinician's record has put an 82-year-old on Adult. No gynecologic or obstetric override applies: the hysterectomy is history, not the reason for this visit.)* |
| **Start time** | `13:20` — **estimated** |
| **End time** | `14:00` — **estimated** (0:40, the top of the band — multi-problem visit: respiratory, ENT, abdominal, flank, and abnormal liver enzymes) |
| **Blood pressure** | `138` / `84` — **filled** |
| **Respiratory Rate** | `20` — **filled** |
| **Height** | `64` in (5'4") — **filled** |
| **BMI** | `29.5` — **derived from a filled height and a filled weight** |

---

## Tier block

**PROPOSED (verify before use)** — everything under `FILLED·proposed` below, plus every
ICD-10-CM code in this document, plus the entire differential. These are the agent's
clinical reasoning, offered for the clinician and preceptor to accept or drop.

```
DERIVED
  D1  Pack-years = <0.25 packs/day x 3 years = <0.75 pack-years.
      Below the 20 pack-year LDCT lung-cancer screening threshold by a wide margin;
      that is what makes the screening line answerable instead of open.
  D2  BMI 29.5 = 703 x 172 / 64^2 = 703 x 172 / 4096 = 120916 / 4096 = 29.52 -> 29.5.
      Overweight band (25.0-29.9).
  D3  Threshold check for D2: 703 x 172 / 63^2 = 120916 / 3969 = 30.47 -> 30.5.
      One inch of filled height moves this across the obesity line. See F8.
  D4  Patient Time = Gerontology (60 and>) Hours, from age 67 (given) with no
      gyn/obstetric override in play.
  D5  Visit Time = 0:40, from the estimated 13:20 start and 14:00 end.

FILLED·asserted
  F1  BP 138/84 filled. 67-year-old female, no documented hypertension, febrile, 7/10
      headache. Sits at the stage-1 threshold; addressed in the Plan (recheck when
      afebrile and well; not diagnosed on one acute-illness reading).
  F2  HR 98 filled. Febrile.
  F3  T 100.9 F filled. Fever and chills are GIVEN by history, so a febrile temperature
      is the plausible value, not an invented abnormal.
  F4  RR 20 filled. Febrile, with diminished bases.
  F5  SpO2 95% on room air filled. Low-normal in a COVID-positive 67-year-old with
      diminished bases; addressed in the Plan (home pulse oximetry, 92% threshold,
      chest x-ray pending).
  F6  HEIGHT 5'4" (64 in) filled.
  F7  WEIGHT 172 lb filled.
  F8  BMI 29.5 filled-input — derived at D2 from the filled height F6 and the filled
      weight F7. Nothing about it was measured.
      **Within 1.0 of the obesity threshold — 5'3" gives 30.5, and an obesity
      diagnosis with its full workup appears.** Disclosed rather than avoided: 5'4" and
      172 lb remain the most plausible values for this patient, and the disclosure is
      what makes them safe to act on.
  F9  Statin agent and dose: atorvastatin 40 mg PO daily. The source says "on statin"
      and names no agent. CONFIRM.
  F10 Omeprazole 20 mg PO daily, inferred for the documented GERD. No meds line in the
      source means no reconciliation was done, not that she takes nothing.
      This does NOT resolve the ibuprofen conflict; see the row 11 verdict.
  F11 Acetaminophen PRN and topical diclofenac, inferred for the documented arthritis.
  F12 Marital status: Married, inferred from age 67.
  F13 Occupation: retired, inferred from age 67.
  F14 Education: high school graduate, inferred.
  F15 Social history: alcohol none reported, drugs none reported, no smoke exposure
      reported, no treatment-limiting religious practice reported, no regular exercise
      program reported, no sleep disturbance reported apart from this illness.
  F16 Family history, all three generations: no chronic illness reported in
      grandparents, parents, siblings or children; no premature coronary disease,
      stroke, diabetes, malignancy or liver disease reported.
  F17 Exam of every system the shorthand did not mention, all normal: general
      appearance and work of breathing, eyes, right ear, nose, dentition, neck range of
      motion and thyroid, cardiovascular, the remainder of the abdominal exam
      (bowel sounds, absence of rebound/guarding/rigidity, negative Murphy's,
      McBurney's, Rovsing's, psoas and obturator), left costovertebral angle,
      thoracolumbar spine, musculoskeletal, neurologic, skin, psychiatric.
  F18 ROS negatives across all thirteen systems listed above.
  F19 Nutrition: low fibre and low fluid intake, inferred from the documented
      constipation.
  F20 Race/Ethnicity `Caucasian/White` — declared administrative value, wrong about one
      time in four. A claim about the patient, so it sits here. CORRECT ON SIGHT.
  F21 Primary Payment Method `Medicare` — declared administrative value; the site rule
      that produces it needs a site, and the site is a GAPS entry. CONFIRM.
  F22 Interaction Level `Level 5` — declared from account practice.
  F23 Course `NUR 5144` — declared; NUR 5042 carries no patient encounters.
  F24 Start 13:20 / End 14:00 — estimated by the Times convention, declared as
      estimated wherever they appear.

FILLED·proposed
  P1  The fourteen-entry differential in the Assessment, and the reasoning that places
      or rejects each entry.
  P2  Every ICD-10-CM code in this document (verified billable against
      reference/icd10cm-2026.sqlite; the database holds the tabular, not the index).
  P3  Colace sig: docusate sodium 100 mg PO BID for up to 7 days.
  P4  Miralax sig: polyethylene glycol 3350 17 g in 8 oz liquid PO daily for up to
      7 days.
  P5  Tylenol sig: acetaminophen 650 mg PO q6h PRN, max 2 g/24 h, <=3 days — ceiling
      lowered from 3 g because of the given AST 48 and ALP 136.
  P6  Motrin sig: ibuprofen 200-400 mg PO q6-8h PRN with food, <=3 days, second-line
      after acetaminophen, withheld if the urinalysis is abnormal.
  P7  Antibiotic contingency if the urine studies return positive, worked against the
      six-drug allergy list, with nitrofurantoin explicitly excluded because it does not
      reach the renal parenchyma and the documented finding is CVA tenderness.
  P8  Corticosteroid contingency flagged: prednisone allergy versus the standard steroid
      step if COVID-19 progresses to hypoxaemia. Resolve before the point of need.
  P9  Home pulse oximetry with a 92% threshold.
  P10 Blood-pressure recheck when afebrile and well.
  P11 Weight/BMI counselling and recheck at follow-up.
  P12 Isolation guidance for COVID-19.
  P13 Age-appropriate screening list: colorectal, mammography, DEXA, lipid monitoring,
      diabetes screening, depression screening, fall-risk, hearing and vision; cervical
      screening explicitly not indicated post-hysterectomy; LDCT explicitly not
      indicated at <0.75 pack-years.
  P14 Immunization catch-up plan, deferred until the acute illness resolves.
  P15 Non-pharmacologic care: fibre, fluids, ambulation, activity restriction while
      febrile.
  P16 Education items, all seven.
  P17 Return precautions, all eight, each naming a specific finding and threshold.
  P18 Follow-up intervals: PCP for the hepatic panel, clinic recheck in 3-4 days,
      ear recheck.

FLAG
  FL1 Right costovertebral angle tenderness documented; the encounter's own stated
      assessment names constipation and COVID-19 only. The urinalysis, microscopic
      urinalysis and urine culture that would settle it were all sent and none is
      recorded, so the finding was investigated and then left without a disposition.
      Carried into this note's Assessment as differential item 4 and into the Plan as an
      antibiotic contingency and a specific return precaution.
  FL2 Diminished breath sounds at both bases documented in a SARS-CoV-2-positive
      67-year-old; the encounter's stated plan orders a chest x-ray and promises a
      telephone call, and the stated assessment does not name a respiratory diagnosis
      beyond COVID-19. Carried into this note as differential item 3 with the chest
      x-ray named as the arbiter.
  FL3 Right upper quadrant tenderness with an alkaline phosphatase of 136 documented;
      the encounter's disposition is a primary-care referral for "elevated LFT" with no
      biliary imaging ordered. A cholestatic enzyme pattern with right upper quadrant
      tenderness is a specific question and the referral does not ask it. Carried as
      differential item 10 with a right upper quadrant ultrasound recommended.
  FL4 Ibuprofen recommended against documented GERD, documented epigastric and right
      upper quadrant tenderness, elevated liver enzymes, and unresolved right flank
      tenderness. The encounter names none of these against the drug. Named in the Plan
      here; the drug is retained because it was given.
  FL5 Acetaminophen recommended against a documented AST of 48 and ALP of 136, with no
      dose ceiling stated in the encounter. Named in the Plan here; ceiling lowered,
      drug retained.
  FL6 Prednisone allergy documented in a patient diagnosed with COVID-19, where the
      standard escalation is a systemic corticosteroid. The encounter does not connect
      the two. Named in the Plan here as a contingency to resolve now rather than later.
  FL7 Six drug allergies documented, no reaction recorded for any of them. Severity is
      therefore unknown for all six, which matters most for the prednisone entry.
      See also GAPS G8.

GAPS
  G1  Visit date — not in the fixture. Medatrax requires it.
  G2  Site — not in the fixture, and the preceptor-to-site mapping is an open question
      on this account. Medatrax requires it, and it also drives the payment-method rule.
  G3  Preceptor — not in the fixture. Medatrax requires it.
  G4  Chest x-ray ordered; result not recorded. The clinic undertook to telephone with
      it. This is the arbiter for differential item 3.
  G5  Urinalysis, microscopic urinalysis and urine culture and sensitivity all sent;
      no result recorded for any of the three. These are the arbiter for differential
      item 4.
  G6  Influenza, rapid streptococcal and RSV testing all sent; no result recorded for
      any of the three.
  G7  Complete blood count, amylase and lipase sent; no result recorded. The
      comprehensive metabolic panel returned an AST and an alkaline phosphatase and
      nothing else is recorded — notably no creatinine, which the flank finding and the
      ibuprofen recommendation both need.
  G8  Reaction not documented for any of the six drug allergies.
  G9  No date of birth in the fixture — but the age is stated outright, so nothing is
      lost. Recorded here only so the absence is not mistaken for an oversight.
  G10 No weight, heart rate, temperature or SpO2 field exists in Medatrax; those values
      live in the note only. Not a defect, recorded so the field block is not read as
      incomplete.

UNKNOWN
  U1  `ha` in "states she has ha a 7/10 headache" — not in GLOSSARY.md. Read as a
      transcription slip for "had": "states she has had a 7/10 headache". The competing
      reading, `ha` = headache, yields the same finding on this line because "headache"
      is spelled out immediately after it, so nothing turns on the choice. Carried
      forward as a 7/10 headache either way. GLOSSARY candidate.
  U2  `vax not utd` — GLOSSARY has `vaccs utd` (vaccinations up to date) but not `vax`.
      Read as the same word negated: vaccinations not up to date. GLOSSARY candidate.
  U3  `ruq` — GLOSSARY lists `llq`, `rll`, `rle` and `ble` but not `ruq`. Read as right
      upper quadrant, consistent with the documented quadrant-abbreviation pattern.
      GLOSSARY candidate.
  U4  `ALP` — not in GLOSSARY. Read as alkaline phosphatase; standard, and consistent
      with the CMP that was ordered in the same line. GLOSSARY candidate.
  U5  Brand names not in GLOSSARY, carried forward and expanded from standard usage:
      `colace` (docusate sodium), `miralax` (polyethylene glycol 3350), `motrin`
      (ibuprofen), `noroxin` (norfloxacin), `pyridium` (phenazopyridine), `bactrim`
      (sulfamethoxazole-trimethoprim), `zyrtec` (cetirizine — note that GLOSSARY
      records the clinician's `cetrazine` misspelling of the generic 17 times),
      `doxy` (doxycycline). GLOSSARY candidates, all eight.
  U6  `<0.25 ppd x 3 yrs` — the `<` is not a documented shorthand form. Read as a
      strict upper bound and carried as such: the derived pack-year figure at D1 is
      written "<0.75", not "0.75". Nothing downstream turns on the difference here,
      since either value is far below every screening threshold.
  U7  Typos corrected as transcription noise, none of them numbers: `thraot` -> throat,
      `erythemia` -> erythema, `apeces` -> apices (GLOSSARY records `apces`),
      `consitipation` -> constipation, `urnie` -> urine, `ASt` -> AST.
  U8  Ambiguity resolved, recorded because the wrong reading invents a diagnosis:
      `R cva tenderness` is COSTOVERTEBRAL ANGLE tenderness, not cerebrovascular
      accident. The tell is the neighbouring word `tenderness` and the exam context.
      Reading it the other way would invent a stroke.
```

---

## Drift matrix — verdict per row

**Row 1 — Invention. PASS.** Every abnormal finding, diagnosis and result in this note
traces to the shorthand: left TM effusion, pharyngeal erythema, diminished bases, absent
lymphadenopathy, epigastric and RUQ tenderness, right CVA tenderness, the 7/10 headache,
fever and chills, the positive SARS-CoV-2 result, the constipation on abdominal x-ray,
AST 48 and ALP 136. Nothing abnormal in the note lacks a source. The exam of every system
the shorthand omitted is filled and normal. Filled vitals and body measurements (F1–F8)
are exempt from tracing and are declared in FILLED instead.

**Row 2 — Drift. PASS.** Each abnormal from step 2's expansion, and where it lands:

| Abnormal in the shorthand | Lands in |
| --- | --- |
| Cough | A item 1 (COVID-19); P supportive care |
| Sore throat | A items 1, 6, 7; P analgesia |
| Sinus pain | A item 9 (bacterial rhinosinusitis, rejected on 2-day duration) |
| Fever | A items 1, 4, 8; VS T 100.9; P antipyretic, return precaution on temperature |
| Chills | A items 1, 4 |
| Left ear pain | A item 5 (H65.92); P ear recheck, ear return precaution |
| 7/10 headache | A item 1 and final dx R51.9; P analgesia, return precaution on stiff neck/confusion |
| Left TM effusion | A item 5, final dx H65.92; P ear recheck |
| Pharyngeal erythema | A items 6 and 7, final dx J02.9 |
| Diminished bases | A item 3 (J12.82); P home pulse oximetry, CXR pending; FLAG FL2; GAPS G4 |
| Epigastric pain | A items 2 and 12, final dx R10.13; P constipation regimen, NSAID caution |
| RUQ pain | A items 10 and 11, final dx R10.11; P RUQ ultrasound recommended; FLAG FL3 |
| Right CVA tenderness | A items 4 and 14, final dx R39.851; P antibiotic contingency, flank return precaution; FLAG FL1; GAPS G5 |
| Constipation on abdominal x-ray | A item 2, final dx K59.00; P Colace, Miralax, fibre, fluids |
| COVID-19 positive | A item 1, final dx U07.1; P isolation, supportive care, steroid contingency |
| AST 48 | A item 11, final dx R74.01; P PCP referral, acetaminophen ceiling |
| ALP 136 | A items 10 and 11, final dx R74.8; P PCP referral, RUQ ultrasound |
| Vaccinations not up to date | A screening section (Z28.39); P immunization catch-up |
| Former smoker <0.25 ppd x 3 yr | A screening section (LDCT explicitly not indicated, D1) |
| No lymphadenopathy (a charted normal) | A item 7, as the Centor criterion that argues against strep |

Nothing lands nowhere.

**Row 3 — Results. PASS.** No laboratory value, imaging result or diagnostic finding is
filled. The only results in the note are the four that were given — SARS-CoV-2 positive,
constipation on abdominal x-ray, AST 48, ALP 136 — and thirteen sent-with-no-result
entries recorded as such under Labs/Tests today and again under GAPS G4–G7. No number was
generated to stand as a result. The filled vitals and body measurements (F1–F8) are
measurements, not results, and do not fail this row.

**Row 4 — Vitals. PASS.** Three filled values land outside the normal range and each is
addressed, with no exemption for being generated:
- **T 100.9 °F** — addressed throughout the Assessment as the febrile illness, and in the
  Plan with an antipyretic and a temperature-specific return precaution.
- **BP 138/84** — at the stage-1 threshold. Addressed in the Plan: named, attributed to
  the fever and the 7/10 headache, explicitly not diagnosed as hypertension on a single
  acute-illness reading, and scheduled for recheck when afebrile and well and again at
  the primary care visit. Note this is the *name it, attribute it, recheck when well*
  response, not an antihypertensive — no condition was documented and inventing a
  hypertension workup would rest a second invention on the first.
- **SpO2 95% on room air** — low-normal against diminished bases. Addressed with home
  pulse oximetry, an explicit 92% threshold, a chest x-ray already pending, and a
  dyspnoea return precaution.
- **BMI 29.5** — overweight band. Addressed in the Plan with dietary counselling, a graded
  activity plan compatible with arthritis, and a recheck at follow-up; and the
  1.0-of-threshold disclosure is made at F8.
- HR 98 and RR 20 are consistent with the documented fever and are not separately abnormal.

**Row 5 — Sig. PASS.** Every drug carries dose, route, frequency and duration:
docusate 100 mg PO BID × 7 days; polyethylene glycol 3350 17 g PO daily × 7 days;
acetaminophen 650 mg PO q6h PRN, ≤2 g/24 h, ≤3 days; ibuprofen 200–400 mg PO q6-8h PRN
with food, ≤3 days. The four inferred home medications also carry full sigs
(atorvastatin 40 mg PO daily; omeprazole 20 mg PO daily; acetaminophen 650 mg PO q6h PRN;
diclofenac 1% gel QID PRN).

**Row 6 — Red flags. PASS.** The return precautions name specific findings and thresholds
— temperature above 101 °F, home oxygen saturation below 92%, worsening right flank pain
with vomiting, jaundice with dark urine and pale stools, no bowel movement in 3 days,
drainage from the left ear, swelling behind the ear, stiff neck, black or bloody stools.
No instance of "red flags reviewed" appears anywhere in the note.

**Row 7 — Drug names. PASS.** Each drug is recognisable as the shorthand wrote it. Per
SOAP.md the Plan records generics, so each is written generic-with-brand:
docusate sodium (Colace), polyethylene glycol 3350 (Miralax), acetaminophen (Tylenol),
ibuprofen (Motrin). No drug was swapped for another. The allergy list is expanded
identically — Bactrim, Zyrtec, Noroxin and Pyridium are all carried with their brand names
beside the generic so the list still reads as the clinician wrote it.

**Row 8 — Band. PASS.** Age 67 is **given**, not inferred, so the inferred-age clause of
this row does not engage. Patient Time = `Gerontology (60 and>) Hours`, following the
Adult ≤ 59 / Gerontology ≥ 60 rule and **overriding the Medatrax label's own
`Adult (18 – 60)`**, which would otherwise pull a 60-year-old the wrong way. The
gynecologic/obstetric override was checked and does **not** apply: the total hysterectomy
and the two D&Cs are past surgical history, and the reason for this visit is a febrile
respiratory illness. This is the row the clinician's own record fails most often — an
82-year-old on `Adult`, and the gyn/ob override never once applied in 30 opportunities —
so it was checked rather than assumed.

**Row 9 — Arithmetic. PASS.** Both derived values show their working and recompute:
- D1: <0.25 × 3 = <0.75 pack-years. ✓
- D2: 703 × 172 = 120,916; 64² = 4,096; 120,916 ÷ 4,096 = 29.52 → **29.5**. ✓
- D3: 703 × 172 = 120,916; 63² = 3,969; 120,916 ÷ 3,969 = 30.47 → **30.5**. ✓
- D5: 13:20 to 14:00 = 0:40. ✓

**Row 10 — Entry. PASS.** All eighteen Medatrax fields hold a given, a derived value, a
declared value or a GAPS entry, and none is silently blank:
Patient Reference — explicit no-name-to-match line; Visit Date — GAPS G1; Course —
declared; Site — GAPS G2; Preceptor — GAPS G3; Interaction Level — declared; Race/Ethnicity
— declared; Gender — given; Age + unit — given; Marital status — inferred and listed at
F12; Primary Payment Method — declared and listed at F21; Case Type — given from the
diagnosis; Patient Time — derived at D4; Start/End — estimated at F24; Blood pressure —
filled at F1; Respiratory Rate — filled at F4; Height — filled at F6; BMI — derived at D2
from filled inputs and listed at F8.

**Row 11 — Conflict. PASS.** Three conflicts between givens are named in the Plan and none
is dissolved:
- **Ibuprofen against documented GERD, documented epigastric and RUQ tenderness, elevated
  liver enzymes, and unresolved right flank tenderness with no creatinine recorded.**
  Named in the Plan and at FL4. **The drug is not dropped** — it was given. Critically,
  the inferred omeprazole at F10 does **not** answer this conflict and is not offered as
  answering it: an inferred regimen never settles a question the givens raise.
- **Acetaminophen against a documented AST of 48 and ALP of 136.** Named in the Plan and
  at FL5; drug retained, ceiling lowered to 2 g/24 h with the reason stated.
- **Prednisone allergy against the standard corticosteroid escalation for COVID-19.**
  Named in the Plan and at FL6 as a contingency to resolve before the point of need.
- Also named, though it is a contingency rather than an active conflict: the six-drug
  allergy list against the antibiotic choices a positive urine culture would call for,
  with nitrofurantoin excluded on pharmacologic grounds against the documented CVA
  tenderness.

**11 of 11 rows pass.**

---

**59 given, 5 derived, 42 filled.**
