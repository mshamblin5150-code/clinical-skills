# Chronic kidney disease — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2024 | KDIGO | KDIGO/KDIGO-2024-CKD-Guideline | guideline | 2024 guideline | 2024-04 | https://doi.org/10.1016/j.kint.2023.10.018 | stated | bound |

## Scope

**Read:** all 199 source pages: cover, contents, reference keys, CKD nomenclature,
conversion factors, notice, foreword, membership, abstract, introduction, special
considerations, relative and absolute risk discussion, the complete summary of
recommendations and practice points, all five clinical chapters and every table and
figure, research recommendations, guideline-development methods, biographic and
disclosure material, acknowledgments, and references. The rows retain numbers that
define, classify, confirm, monitor, refer, start, stop, dose, time, or otherwise
change an action for a patient. Prevalence estimates, effect estimates, trial-only
protocols not adopted by the guideline, study inclusion criteria, publication years,
and bibliography numbers were read but do not produce rows.

Rows marked `RENDERED:` were read from the rendered page structure before their
values were retained: pp11, 38-40, 42-49, 51, 53, 67, 78, 82, 84, 87-88, 92,
96-97, 112, 117, 120-121, 128-129, and 138.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| cover, contents, reference keys, nomenclature, and conversion factors | 1-13 | yes |
| notice, foreword, membership, abstract, introduction, and special considerations | 14-28 | read 2026-08-31; blind 2026-08-31 |
| relative and absolute risk discussion | 29-33 | read 2026-08-31; blind 2026-08-31 |
| summary of recommendations, practice points, tables, and figures | 34-53 | yes |
| chapter 1: evaluation of CKD | 54-80 | yes |
| chapter 2: risk assessment | 81-90 | yes |
| chapter 3: progression and complications | 91-130 | yes |
| chapter 4: medication management and drug stewardship | 131-139 | yes |
| chapter 5: optimal models of care | 140-154 | read 2026-08-31; blind 2026-08-31 |
| research recommendations and guideline-development methods | 155-167 | read 2026-08-31; blind 2026-08-31 |
| biographic information, disclosures, and acknowledgments | 168-179 | read 2026-08-31; blind 2026-08-31 |
| references | 180-199 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 0b77a9e32ca6c7bbccbddf902be4427bf8bc0d2dd7e3ffbc18042f602f371b27; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| people-ckd | people with CKD |
| adults-risk-ckd | adults at risk for CKD |
| children-adolescents | children and adolescents |
| children-ckd | children with CKD |
| adults-ckd | adults with CKD |
| adults-ckd-g3-g5 | adults with CKD G3-G5 |
| adults-ckd-progression-risk | adults with CKD at risk of progression |
| adults-ckd-kidney-failure-risk | adults with CKD at risk of kidney failure |
| adults-high-bp-ckd | adults with high BP and CKD |
| children-high-bp-ckd | children with high BP and CKD |
| ckd-g1-g4-a3-no-diabetes | people with CKD G1-G4, A3, without diabetes |
| ckd-g1-g4-a2-no-diabetes | people with CKD G1-G4, A2, without diabetes |
| ckd-g1-g4-a2-a3-diabetes | people with CKD G1-G4, A2 or A3, with diabetes |
| people-ckd-rasi | people with CKD receiving ACE inhibitor or ARB therapy |
| adults-t2d-ckd | adults with type 2 diabetes and CKD |
| adults-ckd-sglt2 | adults with CKD considered for SGLT2 inhibitor therapy |
| adults-ckd-sglt2-high-acr | adults with CKD, eGFR >=20 mL/min/1.73 m², and ACR >=200 mg/g (>=20 mg/mmol) |
| adults-ckd-sglt2-low-acr | adults with CKD, eGFR 20-45 mL/min/1.73 m², and ACR <200 mg/g (<20 mg/mmol) |
| adults-t2d-ckd-mra | adults with type 2 diabetes and CKD considered for a nonsteroidal MRA |
| people-ckd-acidosis | people with CKD and risk of clinically important acidosis |
| people-ckd-symptomatic-hyperuricemia | people with CKD and symptomatic hyperuricemia |
| adults-50plus-ckd-g3a-g5 | adults age >=50 years with CKD G3a-G5 not receiving chronic dialysis or a transplant |
| adults-50plus-ckd-g1-g2 | adults age >=50 years with CKD G1-G2 |
| adults-18-49-ckd | adults age 18-49 years with CKD not receiving chronic dialysis or a transplant |
| people-af-ckd | people with atrial fibrillation and CKD |
| people-ckd-elective-procedure-noac | people with CKD receiving a NOAC before an elective procedure |
| people-ckd-elective-procedure-dabigatran | people with CKD receiving dabigatran before an elective procedure |
| people-ckd-elective-procedure-fxa | people with CKD receiving apixaban, edoxaban, or rivaroxaban before an elective procedure |
| people-ckd-elective-surgery | people with CKD before elective surgery |
| people-ckd-radiocontrast | people with CKD undergoing elective radiocontrast investigation |
| people-ckd-gadolinium | people with CKD requiring gadolinium-containing contrast |
| adults-ckd-referral | adults with CKD considered for specialist kidney care |
| children-adolescents-ckd-referral | children and adolescents considered for specialist kidney care |
| people-ckd-malnutrition-risk | people with CKD G4-G5, age >65 years, pediatric poor growth, or malnutrition symptoms |
| adolescents-ckd-transition | adolescents with CKD preparing for transfer to adult-oriented care |
| young-adults-ckd-transition | young adults with CKD after transfer from pediatric care |
| people-ckd-dialysis | people with CKD considered for dialysis initiation |
| adults-ckd-krt-planning | adults with CKD considered for transplant or dialysis-access planning |
| children-progressive-ckd | children with progressive and irreversible CKD |
| people-class-iii-obesity | people with class III obesity whose GFR is being evaluated |
| clinical-laboratories | clinical laboratories reporting kidney-function and albuminuria tests |
| ckd-g1 | CKD G1 |
| ckd-g2 | CKD G2 |
| ckd-g3a | CKD G3a |
| ckd-g3b | CKD G3b |
| ckd-g4 | CKD G4 |
| ckd-g5 | CKD G5 |
| ckd-a1 | CKD A1 |
| ckd-a2 | CKD A2 |
| ckd-a3 | CKD A3 |
| people-scr-testing-after-meat-fish | people having serum creatinine measured after meat or fish intake |
| neonates | term and preterm neonates |
| infants-6mo-2yr | infants age 6 months to 2 years |
| children-over-2yr | children over 2 years |
| stored-urine-specimens | urine specimens stored for future albumin analysis |
| people-ckd-gfr-acr-monitoring | people with CKD monitored by GFR and albuminuria category |
| people-ckd-risk-treatment | people with CKD whose predicted risk is used to intensify treatment |
| adults-ckd-vascular-access | adults with CKD considered for vascular-access planning, modality education, or transplant referral |
| people-ckd-progression-model | people with CKD G1-G3 assessed with progression-risk models |
| children-ckd-age-5-17 | children with CKD age 5-17 years |
| children-ckd-age-1-5 | children with CKD age 1-5 years |
| young-children-ckd | young children with CKD using a stroller or carrier |
| children-ckd-g3 | children with CKD G3 |
| children-ckd-g4-g5 | children with CKD G4-G5 |
| older-adults-ckd | older adults with CKD |
| children-sodium-counseling | children with CKD receiving age-based sodium counseling |
| people-high-bp-ckd-home-monitoring | people with high BP and CKD using home BP monitoring |
| people-ckd-hyperkalemia | people with CKD treated with potassium exchange agents |
| people-ckd-polystyrene | people with CKD treated with sodium or calcium polystyrene sulfonate |
| people-ckd-patiromer | people with CKD treated with patiromer |
| people-ckd-szc | people with CKD treated with sodium zirconium cyclosilicate |
| people-ckd-unexpected-hyperkalemia | people with CKD with an unexpected hyperkalemia result |
| people-ckd-acute-gout | people with CKD receiving treatment for an acute gout flare |
| people-ckd-intensive-statin | people with CKD receiving an intensive statin-based regimen |
| people-ckd-established-ischemic-cvd | people with CKD and established ischemic cardiovascular disease |

## Quantities

| key | verbatim |
| --- | --- |
| ckd-minimum-duration | minimum duration defining CKD |
| ckd-gfr-category | GFR category threshold |
| ckd-albuminuria-category | albuminuria category threshold |
| pediatric-egfr-low-flag | pediatric eGFR level to flag as low |
| albuminuria-confirmation | ACR requiring confirmation with a first morning void |
| poct-albuminuria-detection | minimum positive-result detection performance for POCT ACR devices |
| routine-ckd-monitoring | minimum albuminuria and GFR monitoring frequency |
| egfr-change-evaluation | eGFR change warranting evaluation |
| hemodynamic-egfr-change-evaluation | GFR reduction after hemodynamically active therapy warranting evaluation |
| acr-change-evaluation | ACR change warranting evaluation |
| kidney-failure-risk-referral | kidney-failure risk usable for nephrology referral |
| kidney-failure-risk-multidisciplinary | kidney-failure risk usable for timing multidisciplinary care |
| kidney-failure-risk-krt-preparation | kidney-failure risk usable for modality education and KRT preparation |
| adult-physical-activity | moderate-intensity physical-activity target |
| pediatric-physical-activity | pediatric physical-activity target |
| protein-intake | adult protein-intake target |
| high-protein-avoidance | high protein intake to avoid |
| very-low-protein-diet | supervised very-low-protein regimen |
| sodium-intake | sodium and sodium-chloride intake target |
| pediatric-sodium-bp-trigger | pediatric BP percentile triggering age-based sodium counseling |
| adult-sbp-target | standardized office systolic BP target |
| pediatric-map-target | pediatric 24-hour MAP target |
| pediatric-bp-monitoring | pediatric ABPM and office-BP monitoring frequency |
| pediatric-office-sbp-target | pediatric office SBP target when ABPM is unavailable |
| rasi-initiation | CKD and albuminuria categories for ACE inhibitor or ARB initiation |
| rasi-laboratory-monitoring | BP, creatinine, and potassium monitoring after initiation or dose increase |
| rasi-creatinine-rise | creatinine rise prompting reassessment of ACE inhibitor or ARB continuation |
| rasi-kidney-failure-reduction | eGFR threshold for considering dose reduction or discontinuation |
| rasi-low-egfr-continuation | eGFR threshold below which ACE inhibitor or ARB continuation remains advised |
| sglt2-initiation | eGFR and albuminuria thresholds for SGLT2 inhibitor treatment |
| sglt2-continuation | eGFR threshold below which SGLT2 inhibitor continuation remains reasonable |
| mra-eligibility | eGFR, potassium, and albuminuria thresholds for nonsteroidal MRA treatment |
| finerenone-initiation | potassium and eGFR-based finerenone initiation dose |
| finerenone-monitoring | potassium monitoring after finerenone initiation |
| finerenone-hold-restart | potassium thresholds for holding and restarting finerenone |
| metabolic-acidosis-treatment | serum bicarbonate example for considering acidosis prevention |
| gout-ult-initiation | serum uric acid threshold supporting treatment after a first gout episode |
| statin-initiation | age, eGFR, and cardiovascular-risk thresholds for statin therapy |
| af-rate-control | resting ventricular-rate target |
| noac-interruption | minimum NOAC interruption before elective procedures by CrCl and bleeding risk |
| perioperative-medication-hold | planned medication-discontinuation interval before elective surgery |
| post-contrast-metformin-restart | minimum interval before metformin restart after iodinated contrast |
| radiocontrast-consensus-threshold | GFR threshold for radiology-society consensus management |
| gadolinium-agent-threshold | GFR threshold for preferential group II or III gadolinium agents |
| adult-nephrology-referral | adult specialist kidney-care referral thresholds |
| pediatric-nephrology-referral | pediatric specialist kidney-care referral thresholds |
| malnutrition-screening | malnutrition screening frequency |
| pediatric-transition-preparation | age to start transfer preparation |
| post-transfer-risk-age | age defining the high-risk young-adult transition population |
| post-transfer-support-duration | duration of more frequent post-transfer assessment |
| dialysis-initiation-range | GFR range in which dialysis indications often occur |
| krt-planning | GFR or 2-year KRT-risk threshold for planning |
| pediatric-preemptive-transplant | usual eGFR range for pediatric preemptive transplantation |
| class-iii-obesity-gfr-method | obesity threshold supporting combined creatinine-cystatin C eGFR |
| adult-egfr-reporting | adult eGFR reporting precision and low flag |
| filtration-marker-assay-cv | creatinine and cystatin C assay precision limits |
| filtration-marker-assay-bias | creatinine and cystatin C assay bias limits |
| sample-separation | maximum delay before serum or plasma separation |
| urine-albumin-storage | urine-albumin storage temperature and duration |
| urine-acr-reporting | ACR reporting precision and analytic variability |
| scr-meal-wait | minimum wait after meat or fish intake before serum creatinine measurement |
| pediatric-proteinuria-reference | age-specific pediatric PCR, protein, and ACR reference thresholds |
| urine-albumin-stability | refrigerated urine-albumin stability interval |
| gfr-acr-monitoring-grid | annual GFR and albuminuria monitoring frequency by GFR and ACR category |
| risk-based-treatment-intensity | predicted 40%-eGFR-decline risk thresholds for treatment intensity |
| risk-based-referral-intensity | predicted kidney-failure risk thresholds for referral and KRT preparation |
| vascular-access-planning-risk | kidney-failure risk and eGFR thresholds for vascular-access planning and education |
| progression-risk-treatment | annual CKD-progression risk thresholds for treatment and follow-up intensity |
| pediatric-activity-detail | age-specific pediatric physical-activity duration |
| pediatric-restraint-duration | maximum continuous stroller or carrier restraint duration |
| pediatric-protein-intake | pediatric protein intake as a percentage of DRI or SDI |
| geriatric-protein-intake | geriatric protein intake target |
| pediatric-sodium-table | age-specific adequate sodium intake |
| home-bp-monitoring | home BP measurements used for monthly titration |
| potassium-binder-dose | potassium-exchange-agent dose, titration, maintenance, and medication-separation intervals |
| hyperkalemia-repeat-action | potassium thresholds and timing for repeat testing or immediate action |
| acute-gout-dose | colchicine and prednisolone acute-gout regimens |
| intensive-statin-regimen | once-daily intensive statin-based regimens |
| secondary-aspirin | lifelong low-dose aspirin regimen for secondary prevention |
| anticoagulation-refusal-review | minimum frequency for re-evaluating a decision not to anticoagulate |
| noac-dose-by-crcl | anticoagulant dose by creatinine clearance and dose-reduction criteria |
| contrast-medication-hold | medication withholding and restart intervals around iodinated contrast |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-minimum-duration | people-ckd | abnormalities of kidney structure or function for >=3 months | RENDERED: CKD is defined as abnormalities of kidney structure or function, present for a minimum of 3 months | kdigo-2024 | p11 | p11/narrative/ckd-definition | narrative |
| ckd-gfr-category | ckd-g1 | GFR >=90 mL/min/1.73 m² | RENDERED: GFR categories (mL/min/1.73 m²): G1 ≥90 | kdigo-2024 | p11 | p11/narrative/gfr-g1 | narrative |
| ckd-gfr-category | ckd-g2 | GFR 60-89 mL/min/1.73 m² | RENDERED: GFR categories (mL/min/1.73 m²): G2 60-89 | kdigo-2024 | p11 | p11/narrative/gfr-g2 | narrative |
| ckd-gfr-category | ckd-g3a | GFR 45-59 mL/min/1.73 m² | RENDERED: GFR categories (mL/min/1.73 m²): G3a 45-59 | kdigo-2024 | p11 | p11/narrative/gfr-g3a | narrative |
| ckd-gfr-category | ckd-g3b | GFR 30-44 mL/min/1.73 m² | RENDERED: GFR categories (mL/min/1.73 m²): G3b 30-44 | kdigo-2024 | p11 | p11/narrative/gfr-g3b | narrative |
| ckd-gfr-category | ckd-g4 | GFR 15-29 mL/min/1.73 m² | RENDERED: GFR categories (mL/min/1.73 m²): G4 15-29 | kdigo-2024 | p11 | p11/narrative/gfr-g4 | narrative |
| ckd-gfr-category | ckd-g5 | GFR <15 mL/min/1.73 m² | RENDERED: GFR categories (mL/min/1.73 m²): G5 <15 | kdigo-2024 | p11 | p11/narrative/gfr-g5 | narrative |
| ckd-albuminuria-category | ckd-a1 | ACR <30 mg/g (<3 mg/mmol) | RENDERED: A1 Normal to mildly increased <30 mg/g <3 mg/mmol | kdigo-2024 | p11 | p11/narrative/acr-a1 | narrative |
| ckd-albuminuria-category | ckd-a2 | ACR 30-300 mg/g (3-30 mg/mmol) | RENDERED: A2 Moderately increased 30-300 mg/g 3-30 mg/mmol | kdigo-2024 | p11 | p11/narrative/acr-a2 | narrative |
| ckd-albuminuria-category | ckd-a3 | ACR >300 mg/g (>30 mg/mmol) | RENDERED: A3 Severely increased >300 mg/g >30 mg/mmol | kdigo-2024 | p11 | p11/narrative/acr-a3 | narrative |
| class-iii-obesity-gfr-method | people-class-iii-obesity | BMI commonly >40 or >35 kg/m²; eGFRcr-cys is most accurate | Obesity class III varies by region but commonly body mass index >40 or >35 kg/m2 | kdigo-2024 | p37 | p37/narrative/class-iii-obesity | narrative |
| adult-egfr-reporting | clinical-laboratories | report eGFR to nearest whole number per 1.73 m²; flag <60 mL/min/1.73 m² low | RENDERED: Report eGFR rounded to the nearest whole number and relative to a BSA of 1.73 m²; eGFR levels <60 ml/min per 1.73 m² should be flagged as being low | kdigo-2024 | p38 | p38/narrative/adult-egfr-reporting | narrative |
| filtration-marker-assay-cv | clinical-laboratories | assay CV <2.3% for creatinine and <2.0% for cystatin C | RENDERED: desirable imprecision (coefficient of variation [CV] <2.3% for creatinine and <2.0% for cystatin C) | kdigo-2024 | p38 | p38/narrative/filtration-marker-cv | narrative |
| filtration-marker-assay-bias | clinical-laboratories | assay bias <3.7% for creatinine and <3.2% for cystatin C | desirable bias (<3.7% for creatinine and <3.2% for cystatin C) | kdigo-2024 | p38 | p38/narrative/filtration-marker-bias | narrative |
| sample-separation | clinical-laboratories | separate serum/plasma from red blood cells within 12 hours of venipuncture | Separate serum/plasma from red blood cells by centrifugation within 12 hours of venipuncture | kdigo-2024 | p38 | p38/narrative/sample-separation | narrative |
| urine-albumin-storage | clinical-laboratories | analyze fresh or store at 4 °C for <=7 days; do not store frozen at −20 °C | RENDERED: Samples for albumin measurement analyzed fresh or stored at 4 °C for up to 7 days; should not be stored frozen at −20 °C | kdigo-2024 | p40 | p40/narrative/urine-albumin-storage | narrative |
| urine-acr-reporting | clinical-laboratories | report ACR to 1 decimal place; analytic CV <15% | RENDERED: Reporting to 1 decimal place for ACR whether mg/mmol or mg/g; Analytical CV of methods to measure urine albumin should be <15% | kdigo-2024 | p40 | p40/narrative/acr-reporting-quality | narrative |
| pediatric-egfr-low-flag | children-adolescents | eGFRcr <90 mL/min/1.73 m² after age 2 years may be flagged low | RENDERED: An eGFRcr level <90 ml/min per 1.73 m² can be flagged as “low” in children and adolescents over the age of 2 years | kdigo-2024 | p38 | p38/practice-point/9 | practice-point |
| albuminuria-confirmation | people-ckd | confirm ACR >=30 mg/g (>=3 mg/mmol) with a subsequent first morning void | RENDERED: Confirm ACR ≥30 mg/g (≥3 mg/mmol) on a random untimed urine with a subsequent first morning void | kdigo-2024 | p39 | p39/practice-point/5 | practice-point |
| poct-albuminuria-detection | people-ckd | evaluate whether the POCT ACR device is positive in >=85% with ACR >=30 mg/g (>=3 mg/mmol) | RENDERED: produce a positive result in 85% of people with significant albuminuria (ACR ≥30 mg/g or ≥3 mg/mmol) | kdigo-2024 | p40 | p40/practice-point/6 | practice-point |
| routine-ckd-monitoring | people-ckd | assess albuminuria and GFR at least annually | Assess albuminuria in adults, or albuminuria/proteinuria in children, and GFR at least annually in people with CKD | kdigo-2024 | p40 | p40/practice-point/7 | practice-point |
| egfr-change-evaluation | people-ckd | eGFR change >20% on a subsequent test warrants evaluation | a change in eGFR of >20% on a subsequent test exceeds the expected variability and warrants evaluation | kdigo-2024 | p40 | p40/practice-point/9 | practice-point |
| hemodynamic-egfr-change-evaluation | people-ckd | GFR reduction >30% after starting hemodynamically active therapy warrants evaluation | GFR reductions of >30% on subsequent testing exceed the expected variability and warrant evaluation | kdigo-2024 | p40 | p40/practice-point/10 | practice-point |
| acr-change-evaluation | people-ckd | doubling of ACR on a subsequent test warrants evaluation | a doubling of the ACR on a subsequent test exceeds laboratory variability and warrants evaluation | kdigo-2024 | p40 | p40/practice-point/11 | practice-point |
| kidney-failure-risk-referral | adults-ckd-g3-g5 | 5-year kidney-failure risk 3%-5% may guide nephrology referral | A 5-year kidney failure risk of 3%-5% can be used to determine need for nephrology referral | kdigo-2024 | p41 | p41/practice-point/1 | practice-point |
| kidney-failure-risk-multidisciplinary | adults-ckd-g3-g5 | 2-year kidney-failure risk >10% may guide timing of multidisciplinary care | A 2-year kidney failure risk of >10% can be used to determine the timing of multidisciplinary care | kdigo-2024 | p41 | p41/practice-point/2 | practice-point |
| kidney-failure-risk-krt-preparation | adults-ckd-g3-g5 | 2-year kidney-failure risk >40% may guide modality education and KRT preparation | A 2-year kidney failure risk threshold of >40% can be used to determine the modality education, timing of preparation for kidney replacement therapy | kdigo-2024 | p41 | p41/practice-point/3 | practice-point |
| adult-physical-activity | adults-ckd | moderate intensity for >=150 cumulative minutes/week or compatible with cardiovascular and physical tolerance | moderate-intensity physical activity for a cumulative duration of at least 150 minutes per week | kdigo-2024 | p42 | p42/recommendation/3.2.2.1 | 1D |
| pediatric-physical-activity | children-ckd | aim for >=60 minutes daily | aiming for World Health Organization (WHO)-advised levels (i.e., ≥60 minutes daily) | kdigo-2024 | p42 | p42/practice-point/5 | practice-point |
| protein-intake | adults-ckd-g3-g5 | maintain 0.8 g/kg body weight/day | maintaining a protein intake of 0.8 g/kg body weight/d in adults with CKD G3-G5 | kdigo-2024 | p42 | p42/recommendation/3.3.1.1 | 2C |
| high-protein-avoidance | adults-ckd-progression-risk | avoid >1.3 g/kg body weight/day | Avoid high protein intake (>1.3 g/kg body weight/d) in adults with CKD at risk of progression | kdigo-2024 | p42 | p42/practice-point/8 | practice-point |
| very-low-protein-diet | adults-ckd-kidney-failure-risk | consider 0.3-0.4 g/kg body weight/day supplemented to <=0.6 g/kg body weight/day | RENDERED: a very low-protein diet (0.3-0.4 g/kg body weight/d) supplemented with essential amino acids or ketoacid analogs (up to 0.6 g/kg body weight/d) | kdigo-2024 | p42 | p42/practice-point/9 | practice-point |
| sodium-intake | people-ckd | <2 g sodium/day (<90 mmol/day or <5 g sodium chloride/day) | sodium intake be <2 g of sodium per day (or <90 mmol of sodium per day, or <5 g of sodium chloride per day) | kdigo-2024 | p42 | p42/recommendation/3.3.2.1 | 2C |
| pediatric-sodium-bp-trigger | children-high-bp-ckd | follow age-based recommended intake when systolic or diastolic BP >90th percentile for age, sex, and height | blood pressure >90th percentile for age, sex, and height | kdigo-2024 | p43 | p43/practice-point/2 | practice-point |
| adult-sbp-target | adults-high-bp-ckd | standardized office SBP <120 mm Hg when tolerated | RENDERED: target systolic blood pressure (SBP) of <120 mm Hg, when tolerated, using standardized office BP measurement | kdigo-2024 | p43 | p43/recommendation/3.4.1 | 2B |
| pediatric-map-target | children-high-bp-ckd | 24-hour MAP by ABPM <=50th percentile for age, sex, and height | 24-hour mean arterial pressure (MAP) by ambulatory blood pressure monitoring (ABPM) should be lowered to ≤50th percentile | kdigo-2024 | p43 | p43/recommendation/3.4.2 | 2C |
| pediatric-bp-monitoring | children-ckd | ABPM once/year and standardized auscultatory office BP every 3-6 months | RENDERED: Monitor BP once a year with ABPM and every 3-6 months with standardized auscultatory office BP | kdigo-2024 | p43 | p43/practice-point/4 | practice-point |
| pediatric-office-sbp-target | children-high-bp-ckd | when ABPM unavailable, target manual office SBP 50th-75th percentile for age, sex, and height | RENDERED: target manual auscultatory office SBP, obtained in a protocol-driven standardized setting, of 50th-75th percentile | kdigo-2024 | p43 | p43/practice-point/5 | practice-point |
| rasi-initiation | ckd-g1-g4-a3-no-diabetes | start ACE inhibitor or ARB for G1-G4 and A3 without diabetes | RENDERED: starting renin-angiotensin-system inhibitors for people with CKD and severely increased albuminuria (G1-G4, A3) without diabetes | kdigo-2024 | p43 | p43/recommendation/3.6.1 | 1B |
| rasi-initiation | ckd-g1-g4-a2-no-diabetes | start ACE inhibitor or ARB for G1-G4 and A2 without diabetes | starting RASi (ACEi or ARB) for people with CKD and moderately increased albuminuria (G1-G4, A2) without diabetes | kdigo-2024 | p43 | p43/recommendation/3.6.2 | 2C |
| rasi-initiation | ckd-g1-g4-a2-a3-diabetes | start ACE inhibitor or ARB for G1-G4 and A2 or A3 with diabetes | RENDERED: starting RASi for people with CKD and moderately-to-severely increased albuminuria (G1-G4, A2 and A3) with diabetes | kdigo-2024 | p43 | p43/recommendation/3.6.3 | 1B |
| rasi-laboratory-monitoring | people-ckd-rasi | check BP, creatinine, and potassium within 2-4 weeks after initiation or dose increase | Changes in BP, serum creatinine, and serum potassium should be checked within 2-4 weeks of initiation or increase in the dose of a RASi | kdigo-2024 | p44 | p44/practice-point/2 | practice-point |
| rasi-creatinine-rise | people-ckd-rasi | continue unless creatinine rises >30% within 4 weeks | Continue ACEi or ARB therapy unless serum creatinine rises by more than 30% within 4 weeks | kdigo-2024 | p44 | p44/practice-point/4 | practice-point |
| rasi-kidney-failure-reduction | people-ckd-rasi | at eGFR <15 mL/min/1.73 m² consider reduction or discontinuation to reduce uremic symptoms | RENDERED: to reduce uremic symptoms while treating kidney failure (eGFR <15 ml/min per 1.73 m²) | kdigo-2024 | p44 | p44/practice-point/5 | practice-point |
| rasi-low-egfr-continuation | people-ckd-rasi | continue even when eGFR falls below 30 mL/min/1.73 m² | Continue ACEi or ARB in people with CKD even when the eGFR falls below 30 ml/min per 1.73 m2 | kdigo-2024 | p44 | p44/practice-point/7 | practice-point |
| sglt2-initiation | adults-t2d-ckd | T2D, CKD, and eGFR >=20 mL/min/1.73 m²: treat with SGLT2 inhibitor | RENDERED: patients with type 2 diabetes, CKD, and an eGFR ≥20 ml/min per 1.73 m² with an SGLT2i | kdigo-2024 | p44 | p44/recommendation/3.7.1 | 1A |
| sglt2-initiation | adults-ckd-sglt2-high-acr | eGFR >=20 mL/min/1.73 m² with ACR >=200 mg/g (>=20 mg/mmol), or heart failure regardless of albuminuria | RENDERED: eGFR ≥20 ml/min per 1.73 m² with urine ACR ≥200 mg/g (≥20 mg/mmol), or heart failure, irrespective of level of albuminuria | kdigo-2024 | p44 | p44/recommendation/3.7.2 | 1A |
| sglt2-initiation | adults-ckd-sglt2-low-acr | eGFR 20-45 mL/min/1.73 m² with ACR <200 mg/g (<20 mg/mmol): consider SGLT2 inhibitor | adults with eGFR 20 to 45 ml/min per 1.73 m2 with urine ACR <200 mg/g (<20 mg/mmol) with an SGLT2i | kdigo-2024 | p44 | p44/recommendation/3.7.3 | 2B |
| sglt2-continuation | adults-ckd-sglt2 | after initiation, continuation below eGFR 20 mL/min/1.73 m² is reasonable unless not tolerated or KRT starts | continue an SGLT2i even if the eGFR falls below 20 ml/min per 1.73 m2 | kdigo-2024 | p44 | p44/practice-point/8 | practice-point |
| mra-eligibility | adults-t2d-ckd-mra | eGFR >25 mL/min/1.73 m², normal potassium, and ACR >30 mg/g (>3 mg/mmol) despite maximum tolerated RAS inhibitor | adults with T2D, an eGFR >25 ml/min per 1.73 m2, normal serum potassium concentration, and albuminuria (>30 mg/g [>3 mg/mmol]) | kdigo-2024 | p44 | p44/recommendation/3.8.1 | 2A |
| finerenone-initiation | adults-t2d-ckd-mra | if potassium <=4.8 mmol/L: 10 mg/day at eGFR 25-59; 20 mg/day at eGFR >=60 mL/min/1.73 m² | RENDERED: K+ ≤4.8 mmol/l Initiate finerenone - 10 mg daily if eGFR 25-59 ml/min/1.73 m2 - 20 mg daily if eGFR ≥60 ml/min/1.73 m2 | kdigo-2024 | p45 | p45/narrative/finerenone-initiation | narrative |
| finerenone-initiation | adults-t2d-ckd-mra | FDA-approved initiation requires potassium <5.0 mmol/L | RENDERED: The US Food and Drug Administration (FDA) has approved initiation of K+ <5.0 mmol/l | kdigo-2024 | p45 | p45/narrative/finerenone-fda-initiation | narrative |
| finerenone-monitoring | adults-t2d-ckd-mra | monitor potassium 1 month after initiation and every 4 months | RENDERED: Monitor K+ at 1 month after initiation and then every 4 months | kdigo-2024 | p45 | p45/narrative/finerenone-monitoring | narrative |
| finerenone-hold-restart | adults-t2d-ckd-mra | hold if potassium >5.5 mmol/L; consider restart when <=5.0 mmol/L | RENDERED: K+ >5.5 mmol/l Hold finerenone Consider reinitiation if/when K+ ≤5.0 mmol/l | kdigo-2024 | p45 | p45/narrative/finerenone-hold-restart | narrative |
| finerenone-hold-restart | adults-t2d-ckd-mra | continuing MRA may be appropriate at potassium 5.5-6.0 mmol/L | RENDERED: it may be considered appropriate to continue MRAs in people with potassium of 5.5-6.0 mmol/l | kdigo-2024 | p45 | p45/narrative/finerenone-continuation-caveat | narrative |
| metabolic-acidosis-treatment | people-ckd-acidosis | consider treatment to prevent clinically important acidosis, for example bicarbonate <18 mmol/L in adults | serum bicarbonate <18 mmol/l in adults | kdigo-2024 | p45 | p45/practice-point/6 | practice-point |
| gout-ult-initiation | people-ckd-symptomatic-hyperuricemia | after first gout episode, consider treatment particularly if serum uric acid >9 mg/dL (535 micromol/L) | RENDERED: serum uric acid concentration is >9 mg/dL (535 µmol/L) | kdigo-2024 | p46 | p46/practice-point/3 | practice-point |
| statin-initiation | adults-50plus-ckd-g3a-g5 | age >=50 years and eGFR <60 mL/min/1.73 m²: statin or statin/ezetimibe | adults aged ≥50 years with eGFR <60 ml/min per 1.73 m2 | kdigo-2024 | p47 | p47/recommendation/3.15.1.1 | 1A |
| statin-initiation | adults-50plus-ckd-g1-g2 | age >=50 years and eGFR >=60 mL/min/1.73 m²: statin | adults aged ≥50 years with CKD and eGFR ≥60 ml/min per 1.73 m2 | kdigo-2024 | p47 | p47/recommendation/3.15.1.2 | 1B |
| statin-initiation | adults-18-49-ckd | age 18-49 years: statin when coronary disease, diabetes, prior ischemic stroke, or 10-year coronary-death/nonfatal-MI risk >10% | RENDERED: adults aged 18-49 years with CKD; estimated 10-year incidence of coronary death or nonfatal myocardial infarction >10% | kdigo-2024 | p47 | p47/recommendation/3.15.1.3 | 2A |
| af-rate-control | people-af-ckd | ventricular rate <about 90 beats/minute at rest | control ventricular rate to less than about 90 bpm at rest | kdigo-2024 | p48 | p48/narrative/af-rate-control | narrative |
| noac-interruption | people-ckd-elective-procedure-dabigatran | dabigatran: CrCl >=80, 50-80, 30-50 mL/min requires >=24/48, >=36/72, >=48/96 hours before low/high-risk procedure | RENDERED: CrCl ≥80 ml/min ≥24 h ≥48 h CrCl 50-80 ml/min ≥36 h ≥72 h CrCl 30-50 ml/min ≥48 h ≥96 h | kdigo-2024 | p49 | p49/narrative/dabigatran-interruption | narrative |
| noac-interruption | people-ckd-elective-procedure-fxa | apixaban/edoxaban/rivaroxaban: CrCl >=30 requires >=24/48 hours; CrCl 15-30 requires >=36/48 hours before low/high-risk procedure | RENDERED: CrCl 30-50 ml/min ≥24 h ≥48 h CrCl 15-30 ml/min ≥36 h ≥48 h | kdigo-2024 | p49 | p49/narrative/fxa-interruption | narrative |
| perioperative-medication-hold | people-ckd-elective-surgery | consider holding metformin, ACE inhibitor, ARB, and SGLT2 inhibitor 48-72 hours before elective surgery | planned discontinuation of medications (such as metformin, ACEi, ARBs, and SGLT2i) in the 48-72 hours prior to elective surgery | kdigo-2024 | p50 | p50/practice-point/5 | practice-point |
| perioperative-medication-hold | people-ckd-elective-surgery | withhold SGLT2 inhibitor for at least 3-4 days before elective surgery | SGLT2i should be withheld at least 3-4 days before the elective surgery | kdigo-2024 | p136 | p136/narrative/sglt2i-elective-surgery | narrative |
| post-contrast-metformin-restart | people-ckd-radiocontrast | do not restart metformin for at least 48 hours and only if GFR remains stable | should not be restarted for at least 48 hours and only then if GFR remains stable | kdigo-2024 | p138 | p138/narrative/metformin-restart | narrative |
| radiocontrast-consensus-threshold | people-ckd-radiocontrast | AKI or GFR <60 mL/min/1.73 m²: manage elective IV contrast using radiology-society consensus statements | people with AKI or GFR <60 ml/min per 1.73 m2 (CKD G3a-G5) undergoing elective investigation | kdigo-2024 | p50 | p50/practice-point/11 | practice-point |
| gadolinium-agent-threshold | people-ckd-gadolinium | GFR <30 mL/min/1.73 m²: preferentially offer group II or III agents | For people with GFR <30 ml/min per 1.73 m2 (CKD G4-G5) who require gadolinium-containing contrast media | kdigo-2024 | p50 | p50/practice-point/12 | practice-point |
| adult-nephrology-referral | adults-ckd-referral | refer at 5-year KRT risk >3%-5%, eGFR <30 mL/min/1.73 m², sustained GFR fall >20% or >30% after hemodynamic therapy, ACR >700 mg/g, RBC >20/high-power field, or refractory hypertension on >=4 agents | RENDERED: A >3%-5% 5-year risk of requiring KRT eGFR <30 ml/min per 1.73 m2 A sustained fall in GFR of >20% or >30% ACR >700 mg/g RBC >20 per high power field ≥4 antihypertensive agents | kdigo-2024 | p51 | p51/narrative/adult-referral | narrative |
| pediatric-nephrology-referral | children-adolescents-ckd-referral | ACR >=30 mg/g (>=3 mg/mmol) or PCR >=200 mg/g (>=20 mg/mmol), confirmed on repeat first morning void | RENDERED: an ACR of 30 mg/g (3 mg/mmol) or a PCR of 200 mg/g (20 mg/mmol) or more, confirmed on a repeat first morning void sample | kdigo-2024 | p51 | p51/practice-point/2 | practice-point |
| malnutrition-screening | people-ckd-malnutrition-risk | screen twice annually | Screen people with CKD G4-G5, aged >65, poor growth (pediatrics), or symptoms such as involuntary weight loss, frailty, or poor appetite twice annually | kdigo-2024 | p52 | p52/practice-point/2 | practice-point |
| pediatric-transition-preparation | adolescents-ckd-transition | start preparation at age 11-14 years | Prepare adolescents and their families for transfer to adult-oriented care starting at 11-14 years of age | kdigo-2024 | p52 | p52/practice-point/7 | practice-point |
| post-transfer-risk-age | young-adults-ckd-transition | people age <25 years are a high-risk transition population | young people under 25 years of age with CKD | kdigo-2024 | p52 | p52/practice-point/10 | practice-point |
| post-transfer-support-duration | young-adults-ckd-transition | assess more frequently and include caregivers with permission for at least 1-3 years after transfer | RENDERED: at least in the first 1-3 years following transfer from pediatric care | kdigo-2024 | p53 | p53/practice-point/1 | practice-point |
| dialysis-initiation-range | people-ckd-dialysis | indications often but not invariably occur at GFR 5-10 mL/min/1.73 m² | This often but not invariably occurs in the GFR range between 5 and 10 ml/min per 1.73 m2 | kdigo-2024 | p53 | p53/practice-point/3 | practice-point |
| krt-planning | adults-ckd-krt-planning | consider planning at GFR <15-20 mL/min/1.73 m² or 2-year KRT risk >40% | GFR is <15-20 ml/min per 1.73 m2 or risk of KRT is >40% over 2 years | kdigo-2024 | p53 | p53/practice-point/4 | practice-point |
| pediatric-preemptive-transplant | children-progressive-ckd | usually eGFR 5-15 mL/min/1.73 m², individualized by age, size, and progression | will usually be between 5-15 ml/min per 1.73 m2 | kdigo-2024 | p53 | p53/practice-point/6 | practice-point |
| scr-meal-wait | people-scr-testing-after-meat-fish | wait >=12 hours after meat or fish intake before measuring serum creatinine | RENDERED: Waiting for at least 12 hours before the measurement of SCr, after meat or fish intake, best avoids this effect | kdigo-2024 | p67 | p67/narrative/scr-meal-wait | narrative |
| pediatric-proteinuria-reference | neonates | PCR 1000-3000 mg/g (100-300 mg/mmol) in first days and weeks of life | RENDERED: In term and preterm neonates, PCR is high (PCR 1000-3000 mg/g [100-300 mg/mmol]) in the first days and weeks of life | kdigo-2024 | p78 | p78/narrative/neonatal-pcr | narrative |
| pediatric-proteinuria-reference | infants-6mo-2yr | normal PCR <500 mg/g (<50 mg/mmol) or 24-hour protein <150 mg/m²/day | RENDERED: a PCR of <500 mg/g (<50 mg/mmol) or a 24-hour protein of <150 mg/m²/d is considered normal for infants aged 6 months to 2 years | kdigo-2024 | p78 | p78/narrative/infant-proteinuria | narrative |
| pediatric-proteinuria-reference | children-over-2yr | normal first-morning PCR <200 mg/g (<20 mg/mmol), protein <150 mg/m²/day, or first-morning ACR <30 mg/g (<3 mg/mmol) | RENDERED: For children over 2 years, a first morning urine PCR of <200 mg/g (<20 mg/mmol) protein, or <150 mg/m²/d, or a first morning urine ACR <30 mg/g (<3 mg/mmol) is usually considered normal | kdigo-2024 | p78 | p78/narrative/child-proteinuria | narrative |
| urine-albumin-stability | stored-urine-specimens | stable at 2 °C-8 °C for 7 days | RENDERED: Albumin is generally stable in urine stored at 2 °C-8 °C for 7 days | kdigo-2024 | p78 | p78/narrative/urine-stability | narrative |
| gfr-acr-monitoring-grid | people-ckd-gfr-acr-monitoring | times/year by A1/A2/A3: G1 screen 1/treat 1/treat 3; G2 screen 1/treat 1/treat 3; G3a treat 1/2/3; G3b treat 2/3/3; G4 treat 3/3/4+; G5 treat 4+/4+/4+ | RENDERED: A1 A2 A3; G1 Screen 1 Treat 1 Treat 3; G2 Screen 1 Treat 1 Treat 3; G3a Treat 1 Treat 2 Treat 3; G3b Treat 2 Treat 3 Treat 3; G4 Treat* 3 Treat* 3 Treat 4+; G5 Treat 4+ Treat 4+ Treat 4+ | kdigo-2024 | p82 | p82/narrative/gfr-acr-monitoring-grid | narrative |
| risk-based-treatment-intensity | people-ckd-risk-treatment | 40%-eGFR-decline risk >1% optimize medications, >5% consider multiple medications, >10% maximize therapy | RENDERED: Risk of ≥40% decline in eGFR; Thresholds >10%: maximize therapy; >5%: consider multiple medications; >1%: optimize medications | kdigo-2024 | p84 | p84/narrative/treatment-risk-thresholds | narrative |
| risk-based-referral-intensity | people-ckd-risk-treatment | kidney-failure risk >2% nephrology, >10% multidisciplinary care, 20%-40% dialysis access/transplant | RENDERED: Referral thresholds 20%-40%: dialysis access/transplant; >10%: multidisciplinary care; >2%: nephrology | kdigo-2024 | p84 | p84/narrative/referral-risk-thresholds | narrative |
| vascular-access-planning-risk | adults-ckd-vascular-access | KDOQI threshold >50% risk or eGFR <15 mL/min/1.73 m²; >40% risk or eGFR 15 mL/min/1.73 m² acceptable for vascular-access referral; >20% may initiate modality education and presurgical planning | RENDERED: risk-based threshold >50% or eGFR <15 ml/min per 1.73 m²; threshold of >40% risk or an eGFR of 15 ml/min per 1.73 m² is acceptable; Lower risk thresholds, such as >20%, can be used to initiate modality education | kdigo-2024 | p87 | p87/narrative/vascular-access-thresholds | narrative |
| progression-risk-treatment | people-ckd-progression-model | >1%/year may support earlier therapy and closer follow-up; >5%/year may support multidrug therapy | RENDERED: intermediate risk (e.g., >1% per year) may benefit from the earlier initiation of therapy and closer follow-up, and those identified as high risk (e.g., >5% per year) may have the largest benefit from multidrug therapy | kdigo-2024 | p88 | p88/narrative/progression-risk-treatment | narrative |
| pediatric-activity-detail | children-ckd-age-5-17 | 60 minutes/day moderate-to-vigorous physical activity | RENDERED: 60 minutes of moderate-to-vigorous physical activity daily for children 5-17 years old | kdigo-2024 | p92 | p92/narrative/activity-5-17 | narrative |
| pediatric-activity-detail | children-ckd-age-1-5 | 180 minutes/day physical activity | RENDERED: For children 1-5 years of age, 180 minutes per day of physical activity is recommended | kdigo-2024 | p92 | p92/narrative/activity-1-5 | narrative |
| pediatric-restraint-duration | young-children-ckd | do not restrain in stroller or carrier for >60 minutes at a time | RENDERED: should not be restrained (i.e., in a stroller or carrier) for >60 minutes at a time | kdigo-2024 | p92 | p92/narrative/restraint-duration | narrative |
| pediatric-protein-intake | children-ckd-g3 | 100%-140% of DRI or SDI for ideal body weight | RENDERED: dietary protein at 100%-140% of the dietary reference intake (DRI) or the SDI for ideal body weight in children with CKD G3 | kdigo-2024 | p96 | p96/narrative/pediatric-protein-g3 | narrative |
| pediatric-protein-intake | children-ckd-g4-g5 | 100%-120% of DRI or SDI for ideal body weight | RENDERED: 100%-120% of the DRI/SDI in children with CKD G4-G5 | kdigo-2024 | p96 | p96/narrative/pediatric-protein-g4-g5 | narrative |
| geriatric-protein-intake | older-adults-ckd | 1.0-1.2 g/kg body weight/day | RENDERED: Geriatric guidelines recommend protein intakes of 1.0-1.2 g/kg body weight/d | kdigo-2024 | p96 | p96/narrative/geriatric-protein | narrative |
| pediatric-sodium-table | children-sodium-counseling | adequate sodium intake: age 0-6 months 0.110 g/day; 7-12 months 0.370 g/day; 1-3 years 0.370 g/day; 4-8 years 1.0 g/day; 9-13 years 1.2 g/day; 14-70 years 1.5 g/day | RENDERED: Age-based sodium intake recommendations: 0-6 mo 0.110 g/d; 7-12 mo 0.370 g/d; 1-3 yr 0.370 g/d; 4-8 yr 1.0 g/d; 9-13 yr 1.2 g/d; 14-70 yr 1.5 g/d | kdigo-2024 | p97 | p97/narrative/pediatric-sodium-table | narrative |
| home-bp-monitoring | people-high-bp-ckd-home-monitoring | 2 morning and 2 evening BP measurements during first week of every month | RENDERED: 2 morning and evening BP measurements taken during the first week of every month can be used to titrate antihypertensive medication | kdigo-2024 | p97 | p97/narrative/home-bp-monitoring | narrative |
| potassium-binder-dose | people-ckd-polystyrene | polystyrene sulfonate oral 15-60 g/day up to 4 times/day; rectal 30 g/day, SPS maximum 50 g/day; maintenance 15-60 g/day; separate oral medications by >=3 hours before or after, or 6 hours with gastroparesis | RENDERED: Oral: 15-60 g/d (up to 4 times per day); Rectal: 30 g/d (for SPS up to a maximum of 50 g/d); 15-60 g/d orally per day; Separate from oral medications by at least 3 hours before or 3 hours after administration; if gastroparesis, separate other medications by 6 hours | kdigo-2024 | p112 | p112/narrative/polystyrene-dose | narrative |
| potassium-binder-dose | people-ckd-patiromer | patiromer initial 8.4 g once/day, maximum 25.2 g once/day; increase by 8.4 g at 1-week intervals; maintenance 8.4-25.2 g once/day; separate oral medications by >=3 hours before or after | RENDERED: Initial: 8.4 g orally once per day (maximum 25.2 g orally once per day); dose can be increased by 8.4 g increments at 1-week intervals; 8.4-25.2 g orally once per day; Separate from oral medications by at least 3 hours before or 3 hours after administration | kdigo-2024 | p112 | p112/narrative/patiromer-dose | narrative |
| potassium-binder-dose | people-ckd-szc | sodium zirconium cyclosilicate initial 10 g 3 times/day for <=48 hours; maintenance 5 g every second day to 10 g once/day; separate oral products with clinically meaningful gastric pH-dependent bioavailability by >=2 hours before or after | RENDERED: Initial: 10 g orally 3 times per day for up to 48 hours; 5 g every second day to 10 g once per day; administered at least 2 hours before or 2 hours after oral medicinal products with clinically meaningful gastric pH-dependent bioavailability | kdigo-2024 | p112 | p112/narrative/szc-dose | narrative |
| hyperkalemia-repeat-action | people-ckd-unexpected-hyperkalemia | potassium 6.0-6.4 mmol/L: if unexpected and clinically well without AKI, repeat within 24 hours; potassium >=6.5 mmol/L: take immediate action to assess and treat | RENDERED: Moderate K+ 6.0-6.4 mmol/l; Unexpected result Repeat within 24 hours; Severe K+ ≥6.5 mmol/l Take immediate action to assess and treat | kdigo-2024 | p112 | p112/narrative/hyperkalemia-action | narrative |
| acute-gout-dose | people-ckd-acute-gout | colchicine 1.2 mg immediately then 0.6 mg an hour later; alternative prednisolone 30 mg orally for 3-5 days | RENDERED: 1.2 mg immediately followed by 0.6 mg an hour later; 30 mg prednisolone orally for 3-5 days | kdigo-2024 | p117 | p117/narrative/acute-gout-dose | narrative |
| intensive-statin-regimen | people-ckd-intensive-statin | once daily: atorvastatin 20 mg; rosuvastatin 10 mg; simvastatin 20 mg plus ezetimibe 10 mg | RENDERED: once-daily intensive statin-based regimens: atorvastatin 20 mg, rosuvastatin 10 mg, and simvastatin 20 mg combined with ezetimibe 10 mg | kdigo-2024 | p120 | p120/narrative/intensive-statin-regimens | narrative |
| secondary-aspirin | people-ckd-established-ischemic-cvd | lifelong aspirin 75-100 mg for secondary prevention | RENDERED: lifelong use of low-dose aspirin (75-100 mg) for the prevention of recurrence of complications of ischemic CVD | kdigo-2024 | p121 | p121/narrative/lifelong-aspirin | narrative |
| anticoagulation-refusal-review | people-af-ckd | re-evaluate at each consultation and at least every 6 months | RENDERED: re-evaluated at each consultation and at least every 6 months | kdigo-2024 | p128 | p128/narrative/anticoagulation-refusal-review | narrative |
| noac-dose-by-crcl | people-af-ckd | eCrCl >95 or 51-95 mL/min: warfarin INR 2-3, apixaban 5 mg twice/day, dabigatran 150 mg twice/day, edoxaban 60 mg/day, rivaroxaban 20 mg/day; eCrCl 31-50: warfarin INR 2-3, apixaban 5 mg twice/day, dabigatran 150 or 110 mg twice/day, edoxaban 30 mg/day, rivaroxaban 15 mg/day; eCrCl 15-30: consider warfarin INR 2-3, apixaban 2.5 mg twice/day, edoxaban 30 mg/day, rivaroxaban 15 mg/day; dabigatran unknown, 75 mg twice/day in U.S. labeling; eCrCl <15 with or without dialysis: warfarin equipoise, apixaban unknown 2.5 mg twice/day, dabigatran and edoxaban not recommended, rivaroxaban unknown 15 mg/day; reduce apixaban 5 to 2.5 mg twice/day if any 2 of serum creatinine >=1.5 mg/dL (133 µmol/L), age >=80 years, weight <=60 kg; halve edoxaban for eCrCl 30-50 mL/min, weight <=60 kg, or verapamil/quinidine | RENDERED: >95 and 51-95: INR 2-3, apixaban 5 mg b.i.d., dabigatran 150 mg b.i.d., edoxaban 60 mg QD, rivaroxaban 20 mg QD; 31-50: INR 2-3, apixaban 5 mg b.i.d., dabigatran 150 mg b.i.d. or 110 mg b.i.d., edoxaban 30 mg QD, rivaroxaban 15 mg QD; 15-30: INR 2-3 could be considered, apixaban 2.5 mg b.i.d. could be considered, dabigatran Unknown (75 mg b.i.d.), edoxaban 30 mg QD could be considered, rivaroxaban 15 mg QD could be considered; <15 not on dialysis and <15 on dialysis: warfarin Equipoise, apixaban Unknown (2.5 mg b.i.d.), dabigatran Not recommended, edoxaban Not recommended, rivaroxaban Unknown (15 mg QD); apixaban 5 mg twice per day to 2.5 mg b.i.d. if any 2: serum creatinine ≥1.5 mg/dl (133 µmol/l), age ≥80 years, or body weight ≤60 kg; dose was halved if eCrCl 30-50 ml/min, body weight ≤60 kg, or verapamil or quinidine | kdigo-2024 | p129 | p129/narrative/noac-dose-grid | narrative |
| contrast-medication-hold | people-ckd-radiocontrast | with AKI or eGFR <30 mL/min/1.73 m², withhold nonessential nephrotoxic medications 24-48 hours before and 48 hours after contrast; with eGFR >30 and no AKI, metformin need not stop; with AKI or eGFR <=30, stop metformin at or before contrast and restart >=48 hours only if GFR stable; consider withholding RAAS inhibitor >=48 hours before elective contrast-enhanced CT | RENDERED: AKI or eGFR <30 ml/min per 1.73 m² for 24-48 hours before and 48 hours after radiocontrast exposure; eGFR >30 ml/min per 1.73 m² and without evidence of AKI, metformin need not be stopped; AKI or an eGFR ≤30 ml/min per 1.73 m², stop metformin at the time of or before ICM injection and should not be restarted for at least 48 hours and only then if GFR remains stable; consider withholding RAASi for ≥48 hours before elective contrast-enhanced CT | kdigo-2024 | p138 | p138/narrative/contrast-medication-holds | narrative |

## Conflicts

CONFLICT: perioperative-medication-hold — `consider holding metformin, ACE inhibitor, ARB, and SGLT2 inhibitor 48-72 hours before elective surgery` and `withhold SGLT2 inhibitor for at least 3-4 days before elective surgery`.
The summary practice point gives a general 48-72-hour preoperative medication hold,
while the body specifically states that current recommendations support withholding
SGLT2 inhibitors for at least 3-4 days before elective surgery. The sheet retains the
general recommendation-backed interval; the longer SGLT2-specific body interval must
govern where that specific class is being managed.

CONFLICT: finerenone-initiation — `if potassium <=4.8 mmol/L: 10 mg/day at eGFR 25-59; 20 mg/day at eGFR >=60 mL/min/1.73 m²` and `FDA-approved initiation requires potassium <5.0 mmol/L`.
Figure 26 reproduces the conservative trial threshold of potassium <=4.8 mmol/L,
whereas its caption records the U.S. FDA-labeled initiation threshold of potassium
<5.0 mmol/L. The distinct provenance is retained rather than silently reconciling
the trial algorithm with the labeled threshold.

CONFLICT: finerenone-hold-restart — `hold if potassium >5.5 mmol/L; consider restart when <=5.0 mmol/L` and `continuing MRA may be appropriate at potassium 5.5-6.0 mmol/L`. Figure 26 gives
the conservative trial action of holding above 5.5 mmol/L, while its caption states
that continued MRA treatment may be appropriate at 5.5-6.0 mmol/L. The sheet keeps
both because the source itself characterizes the figure thresholds as conservative.

## Coverage

The source is bound: marker records delimit recommendation-shaped text but do not prove a complete recommendation denominator. The artifact contains 343 marker records under 343 distinct locators. Threshold rows cite 49 locators; the remaining 294 locators were read and contain no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence.

- `p34/recommendation/1.1.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p35/recommendation/1.1.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p35/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p35/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p36/recommendation/1.2.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p36/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p36/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p36/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p36/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p39/recommendation/1.2.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p39/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p39/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p39/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p39/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p39/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p40/recommendation/1.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p40/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p40/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p40/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p40/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p40/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p40/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p41/recommendation/2.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p41/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p41/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p41/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p41/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p41/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p41/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/10` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/11` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p42/practice-point/12` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p43/recommendation/3.6.4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p43/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p43/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p44/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p44/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p44/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p44/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p44/practice-point/10` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p44/practice-point/11` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/recommendation/3.9.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p45/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/recommendation/3.14.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/recommendation/3.14.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/recommendation/3.15.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/recommendation/3.15.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p48/recommendation/3.16.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p48/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p48/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p48/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p50/practice-point/10` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p51/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p51/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/11` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p54/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p55/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p56/recommendation/1.1.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p57/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p57/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p57/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p58/recommendation/1.1.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p58/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p58/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p61/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p61/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p62/recommendation/1.2.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p63/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p65/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p66/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p67/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p67/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p68/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p68/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p68/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p69/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p69/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p71/recommendation/1.2.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p71/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p71/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p71/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p71/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p73/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p73/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p75/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p75/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p76/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p76/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p77/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p78/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p78/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p79/recommendation/1.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p79/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p79/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p79/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p81/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p81/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p81/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p82/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p82/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p84/recommendation/2.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p86/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p87/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p87/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p87/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p88/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p88/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p88/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p90/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p90/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/recommendation/3.2.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p93/recommendation/3.3.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p93/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p93/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p93/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p96/recommendation/3.3.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p96/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p96/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p96/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p96/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p97/recommendation/3.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p97/recommendation/3.4.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p97/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p97/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p97/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/recommendation/3.6.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/recommendation/3.6.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/recommendation/3.6.3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/recommendation/3.6.4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p98/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p99/recommendation/3.7.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p99/recommendation/3.7.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p99/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p99/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p99/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p100/recommendation/1.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p102/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p103/recommendation/3.7.3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p105/recommendation/3.8.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p105/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p105/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p105/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p105/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p105/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p106/recommendation/3.9.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p106/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p107/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p107/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p109/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p111/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p111/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p115/recommendation/3.14.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p116/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p116/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p117/recommendation/3.14.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p117/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p117/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p119/recommendation/3.15.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p119/recommendation/3.15.1.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p119/recommendation/3.15.1.3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p119/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p119/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p120/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p121/recommendation/3.15.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p121/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p121/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p123/recommendation/3.15.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p123/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p124/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p125/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p126/recommendation/3.16.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p129/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p129/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p131/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p131/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p131/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p133/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p134/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p134/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p134/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p134/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p134/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p135/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p136/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p136/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p136/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p137/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p137/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p137/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p138/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p138/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p138/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p140/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p142/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p142/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p143/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p144/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p144/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p146/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p147/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p148/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p149/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p149/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p149/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p150/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p150/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p150/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p151/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p151/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p151/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p151/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p152/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p153/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p153/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p153/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
