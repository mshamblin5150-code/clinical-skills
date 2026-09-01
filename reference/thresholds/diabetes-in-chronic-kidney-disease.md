# Diabetes in chronic kidney disease — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2022-diabetes-ckd | KDIGO | KDIGO/KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD | guideline | 2022 guideline | 2022-11 | https://doi.org/10.1016/j.kint.2022.06.008 | stated | bound |

## Scope

**Read:** all 128 source pages, including the cover; contents; reference keys;
CKD nomenclature and conversions; notice; foreword; membership; abstract;
introduction; the complete summary of recommendation statements and practice
points; all five clinical chapters; every table and figure; research
recommendations; guideline-development methods; biographic and disclosure
material; acknowledgments; and references. Rows retain numeric values that
define eligibility, monitoring, dosing, titration, withholding, restarting,
diet, activity, glycemic targets, education, or follow-up. Effect estimates,
trial eligibility or follow-up not adopted as care, prevalence, publication
years, and bibliography numbers were read but do not produce threshold rows.

Rows marked `RENDERED:` were read from the rendered page structure before their
values were retained: pp21, 23, 32, 35, 48, 49, 53, 58-60, 62-67, 69, 71-74,
80-82, 88, and 97.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| cover, contents, reference keys, nomenclature, conversions, notice, foreword, membership, abstract, and introduction | 1-19 | read 2026-08-31; blind 2026-08-31 |
| summary of recommendation statements, practice points, tables, and figures | 20-29 | yes |
| chapter 1: comprehensive care | 30-55 | yes |
| chapter 2: glycemic monitoring and targets | 56-63 | yes |
| chapter 3: lifestyle interventions | 64-75 | yes |
| chapter 4: glucose-lowering therapies | 76-89 | yes |
| chapter 5: management approaches | 90-97 | yes |
| guideline-development methods | 98-106 | read 2026-08-31; blind 2026-08-31 |
| biographic and disclosure information and acknowledgments | 107-117 | read 2026-08-31; blind 2026-08-31 |
| references | 118-128 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 d2889a8b699ea103129c9f8f8df56c53557993741702e3140e3bd37fb96eb1fb; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| people-diabetes-ckd | people with diabetes and CKD |
| people-diabetes-ckd-no-dialysis | people with diabetes and CKD not treated with dialysis |
| people-diabetes-ckd-dialysis | people with diabetes and CKD treated with dialysis |
| people-t2d-ckd | people with type 2 diabetes and CKD |
| people-t2d-ckd-transplant | kidney transplant recipients with type 2 diabetes and CKD |
| people-diabetes-ckd-rasi | people with diabetes and CKD receiving an ACE inhibitor or ARB |
| people-diabetes-ckd-rasi-high-k-risk | people with diabetes and CKD receiving an ACE inhibitor or ARB who have low eGFR, prior hyperkalemia, or borderline-high potassium |
| people-t2d-ckd-sglt2 | people with type 2 diabetes and CKD considered for an SGLT2 inhibitor |
| people-t2d-ckd-sglt2-procedure | people with type 2 diabetes and CKD receiving an SGLT2 inhibitor around a procedure or surgery |
| people-t2d-ckd-finerenone | people with type 2 diabetes and CKD receiving finerenone |
| people-diabetes-ckd-cgm | people with diabetes and CKD using continuous glucose monitoring |
| people-diabetes-ckd-low-hba1c | people with diabetes and CKD for whom a lower HbA1c target is selected |
| people-diabetes-ckd-high-hypoglycemia-risk | people with diabetes and CKD at higher risk of hypoglycemia |
| people-diabetes-ckd-nutrition | people with diabetes and CKD receiving nutrition care |
| adults-diabetes-ckd-nondialysis | adults with diabetes and CKD not treated with dialysis |
| adults-diabetes-ckd-activity | adults with diabetes and CKD receiving physical-activity advice |
| asian-adults-diabetes-ckd | Asian adults with diabetes and CKD |
| adults-obesity-diabetes-ckd | adults with obesity, diabetes, and CKD |
| people-t2d-ckd-metformin | people with type 2 diabetes and CKD receiving metformin |
| people-t2d-ckd-glp1 | people with type 2 diabetes and CKD receiving a GLP-1 receptor agonist |
| people-diabetes-ckd-integrated-care | people with diabetes and CKD receiving team-based integrated care |
| people-diabetes-ckd-acei-arb | people with diabetes and CKD receiving the named ACE inhibitor or ARB |
| people-diabetes-hypertension-albuminuria | patients with diabetes, hypertension, and albuminuria |
| people-diabetes-albuminuria-normal-bp | patients with diabetes, albuminuria, and normal blood pressure |
| women-diabetes-ckd-rasi | women with diabetes and CKD receiving an ACE inhibitor or ARB |
| people-t2d-ckd-sglt2-volume-risk | patients with type 2 diabetes and CKD at risk for hypovolemia before SGLT2 inhibitor treatment |
| kidney-transplant-t2d-ckd | kidney transplant recipients with type 2 diabetes and CKD |
| people-diabetes-ckd-tobacco | patients with diabetes and CKD who use tobacco products |
| people-diabetes-ckd-secondhand-smoke | patients with diabetes and CKD exposed to secondhand smoke |
| people-diabetes-ckd-hba1c-discordant | people with diabetes and CKD whose HbA1c is discordant with directly measured glucose or symptoms |
| people-diabetes-ckd-hypoglycemia-therapy | people with diabetes and CKD using glucose-lowering therapies associated with hypoglycemia |
| people-t2d-ckd-no-daily-monitoring | patients with type 2 diabetes and CKD who choose not to monitor daily with CGM or SMBG |
| people-diabetes-ckd-high-fall-risk | people with diabetes and CKD at higher risk of falls |
| people-t2d-ckd-additional-glycemic-therapy | people with type 2 diabetes and CKD needing additional glycemic therapy |
| people-t2d-ckd-glp1-dpp4 | people with type 2 diabetes and CKD receiving a GLP-1 receptor agonist and a DPP-4 inhibitor |
| people-t2d-ckd-glp1-insulin-su | people with type 2 diabetes and CKD receiving a GLP-1 receptor agonist with insulin or a sulfonylurea |

## Quantities

| key | verbatim |
| --- | --- |
| ckd-definition | albuminuria, eGFR, and persistence thresholds defining CKD |
| risk-factor-reassessment | comprehensive risk-factor reassessment interval |
| rasi-monitoring | laboratory monitoring after ACE inhibitor or ARB initiation or dose increase |
| rasi-creatinine-change | creatinine-change threshold for continuation or reassessment |
| rasi-low-egfr-action | eGFR threshold supporting ACE inhibitor or ARB dose reduction or discontinuation for uremic symptoms |
| rasi-dose | named ACE inhibitor or ARB starting, maximum, and kidney-adjusted dose |
| rasi-benazepril-dose | benazepril starting, maximum, and kidney-adjusted dose |
| rasi-captopril-dose | captopril starting, maximum, and kidney-adjusted dose |
| rasi-enalapril-dose | enalapril starting, maximum, and kidney-adjusted dose |
| rasi-fosinopril-dose | fosinopril starting, maximum, and kidney-adjusted dose |
| rasi-lisinopril-dose | lisinopril starting, maximum, and kidney-adjusted dose |
| rasi-perindopril-dose | perindopril starting, maximum, and kidney-adjusted dose |
| rasi-quinapril-dose | quinapril starting, maximum, and kidney-adjusted dose |
| rasi-ramipril-dose | ramipril starting, maximum, and kidney-adjusted dose |
| rasi-trandolapril-dose | trandolapril starting, maximum, and kidney-adjusted dose |
| rasi-azilsartan-dose | azilsartan starting, maximum, and kidney-adjusted dose |
| rasi-candesartan-dose | candesartan starting, maximum, and kidney-adjusted dose |
| rasi-irbesartan-dose | irbesartan starting, maximum, and kidney-adjusted dose |
| rasi-losartan-dose | losartan starting, maximum, and kidney-adjusted dose |
| rasi-olmesartan-dose | olmesartan starting, maximum, and kidney-adjusted dose |
| rasi-telmisartan-dose | telmisartan starting, maximum, and kidney-adjusted dose |
| rasi-valsartan-dose | valsartan starting, maximum, and kidney-adjusted dose |
| sglt2-eligibility | eGFR and high-priority albuminuria thresholds for SGLT2 inhibitor treatment |
| sglt2-periprocedural | SGLT2 inhibitor withholding, ketone, and restart thresholds around procedures |
| sglt2-dose | named SGLT2 inhibitor dose and kidney-function threshold |
| sglt2-dapagliflozin-dose | dapagliflozin dose and kidney-function threshold |
| sglt2-empagliflozin-dose | empagliflozin dose and kidney-function threshold |
| sglt2-canagliflozin-dose | canagliflozin dose and kidney-function threshold |
| sglt2-egfr-drop | acute eGFR decrease prompting continuation or evaluation |
| finerenone-eligibility | eGFR, albuminuria, and potassium thresholds for nonsteroidal MRA treatment |
| finerenone-dose | eGFR-based finerenone initiation and titration dose |
| finerenone-monitoring | potassium monitoring interval during finerenone treatment |
| finerenone-hold-restart | potassium thresholds and timing for finerenone continuation, hold, and restart |
| hba1c-monitoring | HbA1c monitoring frequency |
| hba1c-target | individualized HbA1c target |
| cgm-target | CGM time-in-range and hypoglycemia thresholds |
| protein-intake | protein intake target |
| protein-by-weight | protein grams per day corresponding to body weight at 0.8 g/kg/day |
| nutrition-education | nutrition-education timing |
| sodium-intake | sodium and sodium-chloride intake target |
| sodium-serving | sodium per serving to avoid |
| physical-activity | moderate-intensity physical-activity target |
| activity-intensity | MET thresholds defining activity intensity |
| obesity-threshold | BMI threshold used for obesity in weight-loss advice |
| metformin-eligibility | eGFR threshold for metformin treatment |
| metformin-formulation-dose | metformin formulation starting, maintenance, and maximum dose |
| metformin-egfr-dose | eGFR-based metformin initiation, dose adjustment, and discontinuation |
| metformin-monitoring | kidney-function and vitamin B12 monitoring frequency |
| glp1-dose | named GLP-1 receptor agonist dose and kidney-function restriction |
| education-contact | structured self-management education contact time |
| integrated-care-monitoring | comprehensive, cardiometabolic, and kidney assessment intervals |
| integrated-comprehensive-assessment | comprehensive blood, urine, eye, and foot assessment interval |
| integrated-cardiometabolic-assessment | cardiometabolic assessment interval |
| integrated-kidney-assessment | kidney-function assessment interval |
| rasi-indication | indication and titration of ACE inhibitor or ARB therapy |
| rasi-normal-bp | ACE inhibitor or ARB use with albuminuria and normal blood pressure |
| rasi-pregnancy | contraception and pregnancy action during ACE inhibitor or ARB therapy |
| rasi-hyperkalemia | management of hyperkalemia during ACE inhibitor or ARB therapy |
| rasi-combination | number of concurrent RAS-blocking agents |
| rasi-potassium-monitoring | potassium monitoring at low eGFR |
| sglt2-sick-day | SGLT2 inhibitor action during prolonged fasting, illness, or excess exercise or alcohol |
| sglt2-volume-management | volume-risk action before and after SGLT2 inhibitor initiation |
| sglt2-transplant | applicability of the SGLT2 inhibitor recommendation to transplant recipients |
| sglt2-continuation | continuation threshold after SGLT2 inhibitor initiation |
| sglt2-procedure-hold | preprocedure SGLT2 inhibitor withholding interval |
| sglt2-procedure-readiness | ketone and oral-intake thresholds for proceeding and restarting |
| finerenone-initiation-potassium | serum-potassium threshold for finerenone initiation |
| finerenone-potassium-recheck | potassium recheck timing after finerenone is withheld |
| tobacco-cessation | tobacco cessation action |
| secondhand-smoke | secondhand smoke exposure action |
| glycemic-monitoring-method | primary glycemic monitoring method |
| glycemic-management-indicator | use of a CGM-derived glucose management indicator |
| daily-glycemic-monitoring | daily CGM or SMBG use |
| low-hypoglycemia-agent-selection | glucose-lowering agent choice without daily monitoring |
| cgm-time-in-range | CGM time-in-range target |
| cgm-glucose-ranges | CGM hypo- and hyperglycemia thresholds |
| individualized-diet | dietary pattern |
| sedentary-behavior | sedentary-behavior advice |
| fall-risk-activity | activity advice for people at higher fall risk |
| weight-loss | weight-loss advice and eGFR priority |
| asian-obesity-threshold | BMI threshold associated with adverse outcomes in Asian populations |
| activity-met-minutes | MET-minute activity target |
| metformin-ir-dose | immediate-release metformin dose |
| metformin-er-dose | extended-release metformin dose |
| metformin-initiation-titration | eGFR-based metformin initiation and titration |
| metformin-dose-adjustment | eGFR-based metformin dose adjustment and stopping |
| metformin-kidney-monitoring | kidney-function monitoring during metformin therapy |
| metformin-b12-monitoring | vitamin B12 monitoring during metformin therapy |
| initial-glucose-lowering-therapy | initial glucose-lowering therapy for type 2 diabetes and CKD |
| additional-glucose-lowering-therapy | additional drug selection when glycemic control is needed |
| glp1-dpp4-combination | concurrent GLP-1 receptor agonist and DPP-4 inhibitor use |
| glp1-insulin-su-adjustment | insulin or sulfonylurea adjustment with GLP-1 receptor agonist use |
| glp1-indication | indication for a long-acting GLP-1 receptor agonist |
| self-management-education | structured self-management education program |
| team-based-care | team-based integrated care |
| glp1-dulaglutide-dose | dulaglutide dose and kidney restriction |
| glp1-exenatide-dose | exenatide dose and kidney restriction |
| glp1-exenatide-er-dose | extended-release exenatide dose and kidney restriction |
| glp1-liraglutide-dose | liraglutide dose and kidney restriction |
| glp1-lixisenatide-dose | lixisenatide dose and kidney restriction |
| glp1-semaglutide-injection-dose | injectable semaglutide dose and kidney restriction |
| glp1-semaglutide-oral-dose | oral semaglutide dose and kidney restriction |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-definition | people-diabetes-ckd | ACR >=30 mg/g (>=3 mg/mmol) and/or eGFR <60 mL/min/1.73 m², persistent for >3 months | RENDERED: CKD is defined as persistently elevated urine albumin excretion (≥30 mg/g [≥3 mg/mmol]), persistently reduced eGFR (eGFR <60 ml/min per 1.73 m²), or both, for more than 3 months | kdigo-2022-diabetes-ckd | p32 | p32/narrative/ckd-definition | narrative |
| risk-factor-reassessment | people-diabetes-ckd | every 3-6 months | RENDERED: Regular risk factor reassessment (every 3-6 months) | kdigo-2022-diabetes-ckd | p21 | p21/narrative/risk-factor-reassessment | narrative |
| rasi-indication | people-diabetes-hypertension-albuminuria | initiate an ACE inhibitor or ARB and titrate to the highest approved tolerated dose | RENDERED: treatment with an angiotensin-converting enzyme inhibitor (ACEi) or an angiotensin II receptor blocker (ARB) be initiated in patients with diabetes, hypertension, and albuminuria, and that these medications be titrated to the highest approved dose that is tolerated | kdigo-2022-diabetes-ckd | p21 | p21/narrative/rasi-indication | narrative |
| rasi-normal-bp | people-diabetes-albuminuria-normal-bp | ACE inhibitor or ARB treatment may be considered | For patients with diabetes, albuminuria, and normal blood pressure, treatment with an ACEi or ARB may be considered | kdigo-2022-diabetes-ckd | p21 | p21/narrative/rasi-normal-bp | narrative |
| rasi-monitoring | people-diabetes-ckd-rasi | monitor BP, creatinine, and potassium within 2-4 weeks after initiation or dose increase | Monitor for changes in blood pressure, serum creatinine, and serum potassium within 2-4 weeks of initiation or increase in the dose of an ACEi or ARB | kdigo-2022-diabetes-ckd | p36 | p36/narrative/rasi-monitoring | narrative |
| rasi-monitoring | people-diabetes-ckd-rasi-high-k-risk | earlier monitoring, for example within 1 week | RENDERED: Earlier laboratory monitoring (e.g., within 1 week) may be indicated for patients at high risk of hyperkalemia | kdigo-2022-diabetes-ckd | p36 | p36/narrative/rasi-early-monitoring | narrative |
| rasi-creatinine-change | people-diabetes-ckd-rasi | continue unless creatinine rises >30% within 4 weeks; evaluate contributing factors for an acute rise >30% | Continue ACEi or ARB therapy unless serum creatinine rises by more than 30% within 4 weeks following initiation of treatment or an increase in dose | kdigo-2022-diabetes-ckd | p36 | p36/narrative/rasi-creatinine-rise | narrative |
| rasi-low-egfr-action | people-diabetes-ckd-rasi | eGFR <15 mL/min/1.73 m²: reduce or discontinue to reduce uremic symptoms when indicated | RENDERED: to reduce uremic symptoms while treating kidney failure (estimated glomerular filtration rate [eGFR] <15 ml/min per 1.73 m²) | kdigo-2022-diabetes-ckd | p38 | p38/narrative/rasi-low-egfr | narrative |
| rasi-potassium-monitoring | people-diabetes-ckd-rasi | eGFR <30 mL/min/1.73 m² requires close potassium monitoring | RENDERED: When these drugs are used in patients with eGFR <30 ml/min per 1.73 m², close monitoring of serum potassium level is required | kdigo-2022-diabetes-ckd | p38 | p38/narrative/rasi-low-egfr-monitoring | narrative |
| rasi-pregnancy | women-diabetes-ckd-rasi | advise contraception; discontinue when considering pregnancy or pregnant | Advise contraception in women who are receiving ACEi or ARB therapy and discontinue these agents in women who are considering pregnancy or who become pregnant | kdigo-2022-diabetes-ckd | p21 | p21/narrative/rasi-pregnancy | narrative |
| rasi-hyperkalemia | people-diabetes-ckd-rasi | manage potassium-lowering measures rather than immediately decreasing or stopping ACE inhibitor or ARB | Hyperkalemia associated with the use of an ACEi or ARB can often be managed by measures to reduce serum potassium levels rather than decreasing the dose or stopping the ACEi or ARB immediately | kdigo-2022-diabetes-ckd | p21 | p21/narrative/rasi-hyperkalemia | narrative |
| rasi-combination | people-diabetes-ckd-rasi | use only one RAS-blocking agent at a time; ACE inhibitor plus ARB or either with direct renin inhibitor is harmful | Use only one agent at a time to block the RAS | kdigo-2022-diabetes-ckd | p22 | p22/narrative/rasi-single-agent | narrative |
| rasi-benazepril-dose | people-diabetes-ckd-acei-arb | benazepril start 10 mg once daily, maximum 80 mg; CrCl <30: start 5 mg once daily | RENDERED: Benazepril 10 mg once daily; 80 mg; CrCl <30 ml/min: Reduce initial dose to 5 mg PO once daily | kdigo-2022-diabetes-ckd | p35 | p35/narrative/benazepril-dose | narrative |
| rasi-captopril-dose | people-diabetes-ckd-acei-arb | captopril start 12.5-25 mg 2-3 times daily; usual maximum 50 mg 3 times daily, up to 450 mg/day; CrCl 10-50 use 75% every 12-18 hours; CrCl <10 use 50% every 24 hours | RENDERED: Captopril 12.5 mg to 25 mg 2 to 3 times daily; Usually 50 mg 3 times daily (may go up to 450 mg/day); CrCl 10-50 ml/min: administer 75% of normal dose every 12-18 hours; CrCl <10 ml/min: administer 50% of normal dose every 24 hours | kdigo-2022-diabetes-ckd | p35 | p35/narrative/captopril-dose | narrative |
| rasi-enalapril-dose | people-diabetes-ckd-acei-arb | enalapril start 5 mg once daily, maximum 40 mg; CrCl <=30 start 2.5 mg once daily; hemodialysis 2.5 mg after dialysis | RENDERED: Enalapril 5 mg once daily; 40 mg; CrCl ≤30 ml/min: reduce initial dose to 2.5 mg PO once daily; 2.5 mg PO after hemodialysis on dialysis days | kdigo-2022-diabetes-ckd | p35 | p35/narrative/enalapril-dose | narrative |
| rasi-fosinopril-dose | people-diabetes-ckd-acei-arb | fosinopril start 10 mg once daily, maximum 80 mg; no kidney adjustment | RENDERED: Fosinopril 10 mg once daily; 80 mg; No dosage adjustment necessary | kdigo-2022-diabetes-ckd | p35 | p35/narrative/fosinopril-dose | narrative |
| rasi-lisinopril-dose | people-diabetes-ckd-acei-arb | lisinopril start 10 mg once daily, maximum 40 mg; CrCl 10-30 reduce start 50%; CrCl <10 start 2.5 mg once daily | RENDERED: Lisinopril 10 mg once daily; 40 mg; CrCl 10-30 ml/min: Reduce initial recommended dose by 50% for adults; CrCl <10 ml/min: Reduce initial dosage to 2.5 mg PO once daily | kdigo-2022-diabetes-ckd | p35 | p35/narrative/lisinopril-dose | narrative |
| rasi-perindopril-dose | people-diabetes-ckd-acei-arb | perindopril start 2 mg once daily, maximum 8 mg; not recommended CrCl <30 | RENDERED: Perindopril 2 mg once daily; 8 mg; Use is not recommended when CrCl <30 ml/min | kdigo-2022-diabetes-ckd | p35 | p35/narrative/perindopril-dose | narrative |
| rasi-quinapril-dose | people-diabetes-ckd-acei-arb | quinapril start 10 mg once daily, maximum 80 mg; CrCl 61-89 start 10 mg, 30-60 start 5 mg, 10-29 start 2.5 mg; insufficient data <10 | RENDERED: Quinapril 10 mg once daily; 80 mg; CrCl 61-89 ml/min: start at 10 mg once daily; CrCl 30-60 ml/min: start at 5 mg once daily; CrCl 10-29 ml/min: start at 2.5 mg once daily; CrCl <10 ml/min: insufficient data | kdigo-2022-diabetes-ckd | p35 | p35/narrative/quinapril-dose | narrative |
| rasi-ramipril-dose | people-diabetes-ckd-acei-arb | ramipril start 2.5 mg once daily, maximum 20 mg; CrCl <40 use 25% of normal dose | RENDERED: Ramipril 2.5 mg once daily; 20 mg; Administer 25% of normal dose when CrCl <40 ml/min | kdigo-2022-diabetes-ckd | p35 | p35/narrative/ramipril-dose | narrative |
| rasi-trandolapril-dose | people-diabetes-ckd-acei-arb | trandolapril start 1 mg once daily, maximum 4 mg; CrCl <30 start 0.5 mg/day | RENDERED: Trandolapril 1 mg once daily; 4 mg; CrCl <30 ml/min: reduce initial dose to 0.5 mg/day | kdigo-2022-diabetes-ckd | p35 | p35/narrative/trandolapril-dose | narrative |
| rasi-azilsartan-dose | people-diabetes-ckd-acei-arb | azilsartan 20-80 mg once daily, maximum 80 mg; no adjustment for mild-to-severe impairment or kidney failure | RENDERED: Azilsartan 20-80 mg once daily; 80 mg; Dose adjustment is not required in patients with mild-to-severe kidney impairment or kidney failure | kdigo-2022-diabetes-ckd | p35 | p35/narrative/azilsartan-dose | narrative |
| rasi-candesartan-dose | people-diabetes-ckd-acei-arb | candesartan start 16 mg once daily, maximum 32 mg; no stated adjustment, exposure approximately doubles at CrCl <30 | RENDERED: Candesartan 16 mg once daily; 32 mg; CrCl <30 ml/min, AUC and Cmax were approximately doubled; Not removed by hemodialysis | kdigo-2022-diabetes-ckd | p35 | p35/narrative/candesartan-dose | narrative |
| rasi-irbesartan-dose | people-diabetes-ckd-acei-arb | irbesartan start 150 mg once daily, maximum 300 mg; no adjustment | RENDERED: Irbesartan 150 mg once daily; 300 mg; No dosage adjustment necessary | kdigo-2022-diabetes-ckd | p35 | p35/narrative/irbesartan-dose | narrative |
| rasi-losartan-dose | people-diabetes-ckd-acei-arb | losartan start 50 mg once daily, maximum 100 mg; no adjustment | RENDERED: Losartan 50 mg once daily; 100 mg; No dosage adjustment necessary | kdigo-2022-diabetes-ckd | p35 | p35/narrative/losartan-dose | narrative |
| rasi-olmesartan-dose | people-diabetes-ckd-acei-arb | olmesartan start 20 mg once daily, maximum 40 mg; no initial adjustment with CrCl <40; not studied in dialysis | RENDERED: Olmesartan 20 mg once daily; 40 mg; No initial dosage adjustment is recommended for patients with moderate to marked kidney impairment (CrCl <40 ml/min); Has not been studied in dialysis patients | kdigo-2022-diabetes-ckd | p35 | p35/narrative/olmesartan-dose | narrative |
| rasi-telmisartan-dose | people-diabetes-ckd-acei-arb | telmisartan start 40 mg once daily, maximum 80 mg; no adjustment | RENDERED: Telmisartan 40 mg once daily; 80 mg; No dosage adjustment necessary | kdigo-2022-diabetes-ckd | p35 | p35/narrative/telmisartan-dose | narrative |
| rasi-valsartan-dose | people-diabetes-ckd-acei-arb | valsartan start 80 mg once daily, maximum 320 mg; no adjustment available at CrCl <30, use caution | RENDERED: Valsartan 80 mg once daily; 320 mg; No dosage adjustment available for CrCl <30 ml/min - to use with caution | kdigo-2022-diabetes-ckd | p35 | p35/narrative/valsartan-dose | narrative |
| sglt2-eligibility | people-t2d-ckd-sglt2 | initiate when eGFR >=20 mL/min/1.73 m²; high-priority features ACR >=200 mg/g (>=20 mg/mmol) or heart failure | RENDERED: Eligible patients: eGFR ≥20 ml/min/1.73 m²; High priority features: ACR ≥200 mg/g [≥20 mg/mmol]; Heart failure | kdigo-2022-diabetes-ckd | p48 | p48/narrative/sglt2-eligibility | narrative |
| sglt2-procedure-hold | people-t2d-ckd-sglt2-procedure | day-stay procedure: withhold on procedure day; procedure/surgery requiring >=1 hospital day and/or bowel preparation: withhold >=2 days in advance and procedure day | RENDERED: withhold SGLT2i the day of day-stay procedures; withhold SGLT2i at least 2 days in advance and the day of procedures/surgery requiring 1 or more days in hospital and/or bowel preparation | kdigo-2022-diabetes-ckd | p48 | p48/narrative/sglt2-procedure-hold | narrative |
| sglt2-procedure-readiness | people-t2d-ckd-sglt2-procedure | proceed if clinically well and ketones <1.0 mmol/L; restart only when eating and drinking normally | RENDERED: proceed with procedure/surgery if the patient is clinically well and ketones are <1.0 mmol/l, and restart SGLT2i after procedure/surgery only when eating and drinking normally | kdigo-2022-diabetes-ckd | p48 | p48/narrative/sglt2-procedure-ketones | narrative |
| sglt2-dapagliflozin-dose | people-t2d-ckd-sglt2 | dapagliflozin 10 mg daily; FDA dosing eGFR >=25 mL/min/1.73 m² | RENDERED: Dapagliflozin 10 mg daily; eGFR ≥25 ml/min per 1.73 m² | kdigo-2022-diabetes-ckd | p48 | p48/narrative/dapagliflozin-dose | narrative |
| sglt2-empagliflozin-dose | people-t2d-ckd-sglt2 | empagliflozin 10 mg daily, may increase to 25 mg for glucose control; FDA eGFR >=30 for T2D/ASCVD glucose control or >=20 for HF | RENDERED: Empagliflozin 10 mg daily (Can increase to 25 mg daily if needed for glucose control); eGFR ≥30 ml/min per 1.73 m² for T2D and ASCVD for glucose control; eGFR ≥20 ml/min per 1.73 m² for HF | kdigo-2022-diabetes-ckd | p48 | p48/narrative/empagliflozin-dose | narrative |
| sglt2-canagliflozin-dose | people-t2d-ckd-sglt2 | canagliflozin 100 mg daily; 300 mg not recommended for CKD; FDA eGFR >=30 mL/min/1.73 m² | RENDERED: Canagliflozin 100 mg daily (The higher dose of 300 mg is not recommended for CKD); eGFR ≥30 ml/min per 1.73 m² | kdigo-2022-diabetes-ckd | p48 | p48/narrative/canagliflozin-dose | narrative |
| sglt2-egfr-drop | people-t2d-ckd-sglt2 | tolerate acute eGFR decrease <=30%; if >30%, assess hypovolemia, adjust diuretic, stop nephrotoxins, and evaluate other causes | RENDERED: one should tolerate an acute eGFR decrease of ≤30% with initiation of therapy; If there is a >30% decline in eGFR, ensure that the patient is not hypovolemic | kdigo-2022-diabetes-ckd | p49 | p49/narrative/sglt2-egfr-drop | narrative |
| sglt2-continuation | people-t2d-ckd-sglt2 | continue below eGFR 20 mL/min/1.73 m² unless not tolerated or kidney replacement therapy begins | RENDERED: continue an SGLT2i even if the eGFR falls below 20 ml/min per 1.73 m², unless it is not tolerated or kidney replacement therapy is initiated | kdigo-2022-diabetes-ckd | p49 | p49/narrative/sglt2-continuation | narrative |
| sglt2-sick-day | people-t2d-ckd-sglt2 | during illness, excessive exercise, or alcohol intake temporarily withhold SGLT2 inhibitor, maintain food and fluids if possible, check glucose and ketones more often, and seek help early | RENDERED: Sick day protocol (for illness or excessive exercise or alcohol intake): temporarily withhold SGLT2i, keep drinking and eating (if possible), check blood glucose and blood ketone levels more often, and seek medical help early | kdigo-2022-diabetes-ckd | p23 | p23/narrative/sglt2-sick-day | narrative |
| sglt2-volume-management | people-t2d-ckd-sglt2-volume-risk | consider decreasing thiazide or loop diuretic before SGLT2 inhibitor; advise volume-depletion and low-BP symptoms; follow up volume status after initiation | If a patient is at risk for hypovolemia, consider decreasing thiazide or loop diuretic dosages before commencement of SGLT2i treatment | kdigo-2022-diabetes-ckd | p22 | p22/narrative/sglt2-volume | narrative |
| sglt2-transplant | kidney-transplant-t2d-ckd | SGLT2 inhibitor recommendation does not apply because recipients were not adequately studied and may have increased infection risk | the recommendation to use SGLT2i does not apply to kidney transplant recipients | kdigo-2022-diabetes-ckd | p22 | p22/narrative/sglt2-transplant | narrative |
| finerenone-eligibility | people-t2d-ckd-finerenone | eGFR >=25, albuminuria >=30 mg/g (>=3 mg/mmol), normal potassium, despite maximum tolerated RAS inhibitor | patients with T2D, an eGFR ≥25 ml/min per 1.73 m2, normal serum potassium concentration, and albuminuria (≥30 mg/g [≥3 mg/mmol]) despite maximum tolerated dose of RAS inhibitor | kdigo-2022-diabetes-ckd | p49 | p49/narrative/finerenone-eligibility | narrative |
| finerenone-initiation-potassium | people-t2d-ckd-finerenone | trial-based initiation target K <=4.8 mmol/L | RENDERED: K+ ≤4.8 mmol/l | kdigo-2022-diabetes-ckd | p53 | p53/narrative/finerenone-trial-potassium | narrative |
| finerenone-initiation-potassium | people-t2d-ckd-finerenone | FDA-approved initiation K <5.0 mmol/L | RENDERED: The United States Food and Drug Administration (FDA) has approved initiation of K+ <5.0 mmol/l | kdigo-2022-diabetes-ckd | p53 | p53/narrative/finerenone-fda-potassium | narrative |
| finerenone-dose | people-t2d-ckd-finerenone | start 10 mg daily if eGFR 25-59 mL/min/1.73 m² or 20 mg daily if eGFR >=60 mL/min/1.73 m²; increase 10 to 20 mg when potassium permits | RENDERED: 10 mg daily if eGFR 25-59 ml/min per 1.73 m²; 20 mg daily if eGFR ≥60 ml/min per 1.73 m²; Increase dose to 20 mg daily, if on 10 mg daily | kdigo-2022-diabetes-ckd | p53 | p53/narrative/finerenone-initiation | narrative |
| finerenone-monitoring | people-t2d-ckd-finerenone | monitor potassium 1 month after initiation, then every 4 months | RENDERED: Monitor K+ at 1 month after initiation and then every 4 months | kdigo-2022-diabetes-ckd | p53 | p53/narrative/finerenone-monitoring | narrative |
| finerenone-hold-restart | people-t2d-ckd-finerenone | K 4.9-5.5: continue 10 or 20 mg and monitor every 4 months; K >5.5: hold and recheck; restart 10 mg when K <=5.0 | RENDERED: K+ 4.9-5.5 mmol/l: Continue finerenone 10 mg or 20 mg; Monitor K+ every 4 months. K+ >5.5 mmol/l: Hold finerenone; Recheck K+; Consider reinitiation if/when K+ ≤5.0 mmol/l | kdigo-2022-diabetes-ckd | p53 | p53/narrative/finerenone-hold-restart | narrative |
| finerenone-potassium-recheck | people-t2d-ckd-finerenone | when K >5.5 mmol/L, recheck within 72 hours | RENDERED: With serum potassium >5.5 mmol/l, the drug was temporarily withheld and serum potassium was rechecked within 72 hours | kdigo-2022-diabetes-ckd | p53 | p53/narrative/finerenone-recheck | narrative |
| tobacco-cessation | people-diabetes-ckd-tobacco | advise quitting tobacco products | We recommend advising patients with diabetes and CKD who use tobacco to quit using tobacco products | kdigo-2022-diabetes-ckd | p23 | p23/narrative/tobacco-cessation | narrative |
| secondhand-smoke | people-diabetes-ckd-secondhand-smoke | counsel to reduce secondhand smoke exposure | Physicians should counsel patients with diabetes and CKD to reduce secondhand smoke exposure | kdigo-2022-diabetes-ckd | p23 | p23/narrative/secondhand-smoke | narrative |
| glycemic-monitoring-method | people-diabetes-ckd | use HbA1c to monitor glycemic control | We recommend using hemoglobin A1c (HbA1c) to monitor glycemic control in patients with diabetes and CKD | kdigo-2022-diabetes-ckd | p24 | p24/narrative/hba1c-method | narrative |
| hba1c-monitoring | people-diabetes-ckd | twice per year; up to 4 times per year if target not met or therapy changes | RENDERED: Monitoring long-term glycemic control by HbA1c twice per year is reasonable for patients with diabetes. HbA1c may be measured as often as 4 times per year | kdigo-2022-diabetes-ckd | p58 | p58/narrative/hba1c-frequency | narrative |
| hba1c-target | people-diabetes-ckd-no-dialysis | individualized target from <6.5% to <8.0% | RENDERED: individualized HbA1c target ranging from <6.5% to <8.0% in patients with diabetes and CKD not treated with dialysis | kdigo-2022-diabetes-ckd | p60 | p60/narrative/hba1c-target | narrative |
| hba1c-target | people-diabetes-ckd-low-hba1c | lower examples <6.5% or <7.0% | Safe achievement of lower HbA1c targets (e.g., <6.5% or <7.0%) may be facilitated by CGM or SMBG | kdigo-2022-diabetes-ckd | p63 | p63/narrative/lower-hba1c-target | narrative |
| hba1c-target | people-diabetes-ckd-high-hypoglycemia-risk | higher examples <7.5% or <8%; may be higher in some patients with short life expectancy and multiple comorbidities | RENDERED: A higher HbA1c target (e.g., <7.5% or <8%) may be selected for patients at higher risk for hypoglycemia | kdigo-2022-diabetes-ckd | p62 | p62/narrative/higher-hba1c-target | narrative |
| glycemic-management-indicator | people-diabetes-ckd-hba1c-discordant | use a CGM-derived GMI to index glycemia | A glucose management indicator (GMI) derived from continuous glucose monitoring (CGM) data can be used to index glycemia | kdigo-2022-diabetes-ckd | p24 | p24/narrative/gmi | narrative |
| daily-glycemic-monitoring | people-diabetes-ckd-hypoglycemia-therapy | daily CGM or SMBG may prevent hypoglycemia and improve control | Daily glycemic monitoring with CGM or self-monitoring of blood glucose (SMBG) may help prevent hypoglycemia | kdigo-2022-diabetes-ckd | p24 | p24/narrative/daily-monitoring | narrative |
| low-hypoglycemia-agent-selection | people-t2d-ckd-no-daily-monitoring | prefer lower-hypoglycemia-risk agents dosed for eGFR | glucose-lowering agents that pose a lower risk of hypoglycemia are preferred and should be administered in doses that are appropriate for the level of eGFR | kdigo-2022-diabetes-ckd | p24 | p24/narrative/no-daily-monitoring | narrative |
| cgm-time-in-range | people-diabetes-ckd-cgm | target range 70-180 mg/dL (3.9-10.0 mmol/L) for >70% of readings | RENDERED: Commonly accepted ranges are 70-180 mg/dl (3.9-10.0 mmol/l) at >70% of readings | kdigo-2022-diabetes-ckd | p59 | p59/narrative/cgm-time-in-range | narrative |
| cgm-glucose-ranges | people-diabetes-ckd-cgm | hypoglycemia <70 mg/dL (3.9 mmol/L); clinically significant hypoglycemia <54 mg/dL (3.0 mmol/L); hyperglycemia >180 and >250 mg/dL (10.0 and 13.9 mmol/L) | RENDERED: >250 mg/dl (13.9 mmol/l); >180 mg/dl (10.0 mmol/l); <70 mg/dl (3.9 mmol/l); <54 mg/dl (3.0 mmol/l) | kdigo-2022-diabetes-ckd | p59 | p59/narrative/cgm-ranges | narrative |
| protein-intake | adults-diabetes-ckd-nondialysis | 0.8 g/kg/day | RENDERED: maintaining a protein intake of 0.8 g protein/kg (weight)/d for those with diabetes and CKD not treated with dialysis | kdigo-2022-diabetes-ckd | p64 | p64/narrative/protein-intake | narrative |
| protein-intake | people-diabetes-ckd-dialysis | 1.0-1.2 g/kg/day, particularly with peritoneal dialysis | RENDERED: Patients treated with hemodialysis, and particularly peritoneal dialysis, should consume between 1.0 and 1.2 g protein/kg (weight)/d | kdigo-2022-diabetes-ckd | p67 | p67/narrative/dialysis-protein | narrative |
| individualized-diet | people-diabetes-ckd | individualize a diet high in vegetables, fruits, whole grains, fiber, legumes, plant proteins, unsaturated fats, and nuts, and lower in processed meats, refined carbohydrates, and sweetened beverages | RENDERED: Patients with diabetes and CKD should consume an individualized diet high in vegetables, fruits, whole grains, fiber, legumes, plant-based proteins, unsaturated fats, and nuts; and lower in processed meats, refined carbohydrates, and sweetened beverages | kdigo-2022-diabetes-ckd | p25 | p25/narrative/individualized-diet | narrative |
| protein-by-weight | adults-diabetes-ckd-nondialysis | body weight kg -> protein g/day: 35->28, 40->32, 50->40, 55->44, 60->48, 65->52, 70->56, 75->60, 80->64, 85->68, 90->72, 95->76, 100->80 | RENDERED: Weight (kg): 35, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100; Grams of protein per day (wt × 0.8 g/kg): 28, 32, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80 | kdigo-2022-diabetes-ckd | p66 | p66/narrative/protein-by-weight | narrative |
| nutrition-education | people-diabetes-ckd-nutrition | at diabetes diagnosis; yearly for longstanding diabetes and CKD and at critical times | Patients with newly diagnosed diabetes should be referred for individualized nutrition education at diagnosis. Patients with longstanding diabetes and CKD should have access to nutrition education yearly, as well as at critical times | kdigo-2022-diabetes-ckd | p66 | p66/narrative/nutrition-education | narrative |
| sodium-intake | people-diabetes-ckd | <2 g sodium/day, or <90 mmol sodium/day, or <5 g sodium chloride/day | sodium intake be <2 g of sodium per day (or <90 mmol of sodium per day, or <5 g of sodium chloride per day) | kdigo-2022-diabetes-ckd | p67 | p67/narrative/sodium-intake | narrative |
| sodium-serving | people-diabetes-ckd-nutrition | avoid foods with >400 mg sodium per serving | RENDERED: Avoid foods with more than 400 mg sodium per serving | kdigo-2022-diabetes-ckd | p69 | p69/narrative/sodium-serving | narrative |
| physical-activity | adults-diabetes-ckd-activity | moderate intensity for at least 150 minutes/week or compatible tolerance | RENDERED: undertake moderate-intensity physical activity for a cumulative duration of at least 150 minutes per week | kdigo-2022-diabetes-ckd | p71 | p71/narrative/activity-target | narrative |
| physical-activity | adults-diabetes-ckd-activity | rendered algorithm branches: physically active >150 min/week versus physically active <150 min/week | RENDERED: Physically active for >150 min/wk; Physically active for <150 min/wk | kdigo-2022-diabetes-ckd | p74 | p74/narrative/activity-algorithm | narrative |
| activity-intensity | adults-diabetes-ckd-activity | sedentary <1.5 MET; light 1.6-2.9; moderate 3.0-5.9; vigorous >6 | RENDERED: Sedentary <1.5; Light 1.6-2.9; Moderate 3.0-5.9; Vigorous >6 | kdigo-2022-diabetes-ckd | p72 | p72/narrative/activity-mets | narrative |
| activity-met-minutes | adults-diabetes-ckd-activity | minimum recommended goal 450-750 MET-min/week | RENDERED: minimum recommended goal of physical activity (450-750 metabolic equivalents [METs]/min/wk) | kdigo-2022-diabetes-ckd | p73 | p73/narrative/activity-met-minutes | narrative |
| sedentary-behavior | adults-diabetes-ckd-activity | advise avoiding sedentary behavior and encourage short bouts spread throughout the week | Patients should be advised to avoid sedentary behavior | kdigo-2022-diabetes-ckd | p74 | p74/narrative/sedentary-behavior | narrative |
| fall-risk-activity | people-diabetes-ckd-high-fall-risk | advise individualized intensity and aerobic, resistance, or both exercise types | For patients at higher risk of falls, healthcare providers should provide advice on the intensity of physical activity | kdigo-2022-diabetes-ckd | p74 | p74/narrative/fall-risk-activity | narrative |
| weight-loss | adults-obesity-diabetes-ckd | advise or encourage weight loss, particularly with eGFR >=30 mL/min/1.73 m² | RENDERED: Physicians should consider advising/encouraging patients with obesity, diabetes, and CKD to lose weight, particularly patients with eGFR ≥30 ml/min per 1.73 m² | kdigo-2022-diabetes-ckd | p74 | p74/narrative/weight-loss | narrative |
| obesity-threshold | adults-obesity-diabetes-ckd | BMI >30 kg/m² | RENDERED: Obesity (defined by body mass index [BMI] >30 kg/m²) | kdigo-2022-diabetes-ckd | p74 | p74/narrative/obesity-threshold | narrative |
| asian-obesity-threshold | asian-adults-diabetes-ckd | BMI >27.5 kg/m² increases adverse-outcome risk | RENDERED: Among Asian populations, having a BMI >27.5 kg/m² increases the risk for adverse outcomes | kdigo-2022-diabetes-ckd | p74 | p74/narrative/asian-obesity-threshold | narrative |
| metformin-eligibility | people-t2d-ckd-metformin | treat at eGFR >=30 mL/min/1.73 m² | treating patients with T2D, CKD, and an eGFR ≥30 ml/min per 1.73 m2 with metformin | kdigo-2022-diabetes-ckd | p78 | p78/narrative/metformin-eligibility | narrative |
| metformin-eligibility | kidney-transplant-t2d-ckd | treat according to other type 2 diabetes and CKD recommendations when eGFR >=30 mL/min/1.73 m² | Treat kidney transplant recipients with T2D and an eGFR ≥30 ml/min per 1.73 m2 with metformin | kdigo-2022-diabetes-ckd | p27 | p27/narrative/metformin-transplant | narrative |
| metformin-ir-dose | people-t2d-ckd-metformin | immediate release start 500 mg once/twice daily or 850 mg once daily; maintenance 1 g twice daily or 850 mg twice daily; maximum 2.55 g/day | RENDERED: Metformin, Immediate Release: 500 mg once or twice daily OR 850 mg once daily; Usual maintenance dose: 1 g twice daily OR 850 mg twice daily; Maximum: 2.55 g/day | kdigo-2022-diabetes-ckd | p80 | p80/narrative/metformin-ir-dose | narrative |
| metformin-er-dose | people-t2d-ckd-metformin | extended release start 500 mg or 1 g once daily; maximum 2 g/day | RENDERED: Metformin, Extended Release: 500 mg once daily OR 1 g once daily; 2 g/day | kdigo-2022-diabetes-ckd | p80 | p80/narrative/metformin-er-dose | narrative |
| metformin-initiation-titration | people-t2d-ckd-metformin | eGFR >=60: start immediate release 500 or 850 mg once daily and titrate by 500 or 850 mg/day every 7 days; extended release start 500 mg daily and titrate by 500 mg/day every 7 days | RENDERED: eGFR ≥60: Immediate release initial 500 mg or 850 mg once daily; titrate upwards by 500 mg/d or 850 mg/d every 7 days; Extended release initial 500 mg daily; titrate upwards by 500 mg/d every 7 days | kdigo-2022-diabetes-ckd | p82 | p82/narrative/metformin-initiation-dose | narrative |
| metformin-dose-adjustment | people-t2d-ckd-metformin | eGFR 45-59: continue same dose and consider reduction in certain hypoperfusion/hypoxemia conditions; eGFR 30-44: initiate at half dose and titrate to half maximum, or halve existing dose; eGFR <30: stop and do not initiate | RENDERED: eGFR 45-59: Continue same dose; Consider dose reduction in certain conditions. eGFR 30-44: Initiate at half the dose and titrate upwards to half of maximum recommended dose; Halve the dose. eGFR <30: Stop metformin; do not initiate metformin | kdigo-2022-diabetes-ckd | p82 | p82/narrative/metformin-egfr-dose | narrative |
| metformin-dose-adjustment | people-t2d-ckd-metformin | narrative: halve maximum dose when eGFR declines to 30-45 mL/min/1.73 m² | RENDERED: The maximum dose should be halved when the eGFR declines to 30-45 ml/min per 1.73 m² | kdigo-2022-diabetes-ckd | p81 | p81/narrative/metformin-half-dose | narrative |
| metformin-kidney-monitoring | people-t2d-ckd-metformin | eGFR >=60: at least annually; eGFR 45-59 or 30-44: at least every 3-6 months | RENDERED: eGFR ≥60: At least annually; eGFR 45-59: At least every 3-6 months; eGFR 30-44: At least every 3-6 months | kdigo-2022-diabetes-ckd | p82 | p82/narrative/metformin-kidney-monitoring | narrative |
| metformin-b12-monitoring | people-t2d-ckd-metformin | monitor vitamin B12 annually after >4 years of metformin or when at risk | RENDERED: Annually if on metformin for more than 4 years or at risk of vitamin B12 deficiency | kdigo-2022-diabetes-ckd | p82 | p82/narrative/metformin-b12-monitoring | narrative |
| initial-glucose-lowering-therapy | people-t2d-ckd | include lifestyle therapy and first-line treatment with both metformin and an SGLT2 inhibitor | RENDERED: Glycemic management for patients with T2D and CKD should include lifestyle therapy, first-line treatment with both metformin and a sodium-glucose cotransporter-2 inhibitor | kdigo-2022-diabetes-ckd | p25 | p25/narrative/initial-glucose-lowering | narrative |
| additional-glucose-lowering-therapy | people-t2d-ckd-additional-glycemic-therapy | guide selection by preferences, comorbidities, eGFR, and cost; generally prefer a GLP-1 receptor agonist | Patient preferences, comorbidities, eGFR, and cost should guide selection of additional drugs to manage glycemia, when needed, with glucagon-like peptide-1 receptor agonist (GLP-1 RA) generally preferred | kdigo-2022-diabetes-ckd | p25 | p25/narrative/additional-glucose-lowering | narrative |
| glp1-dpp4-combination | people-t2d-ckd-glp1-dpp4 | do not use together | GLP-1 RA should not be used in combination with dipeptidyl peptidase-4 (DPP-4) inhibitors | kdigo-2022-diabetes-ckd | p28 | p28/narrative/glp1-dpp4 | narrative |
| glp1-insulin-su-adjustment | people-t2d-ckd-glp1-insulin-su | reduce insulin and/or sulfonylurea dose when needed for hypoglycemia risk | The doses of sulfonylurea and/or insulin may need to be reduced | kdigo-2022-diabetes-ckd | p28 | p28/narrative/glp1-insulin-su | narrative |
| glp1-indication | people-t2d-ckd-additional-glycemic-therapy | use a long-acting GLP-1 receptor agonist when individualized targets are unmet despite metformin and SGLT2 inhibitor, or when those drugs cannot be used | In patients with T2D and CKD who have not achieved individualized glycemic targets despite use of metformin and SGLT2i treatment, or who are unable to use those medications, we recommend a long-acting GLP-1 RA | kdigo-2022-diabetes-ckd | p27 | p27/narrative/glp1-indication | narrative |
| glp1-indication | kidney-transplant-t2d-ckd | the long-acting receptor-agonist recommendation also applies to kidney transplant recipients | RENDERED: This recommendation applies to kidney transplant recipients | kdigo-2022-diabetes-ckd | p87 | p87/narrative/glp1-transplant | narrative |
| glp1-dulaglutide-dose | people-t2d-ckd-glp1 | dulaglutide 0.75 or 1.5 mg weekly; no adjustment; use eGFR >15 | RENDERED: Dulaglutide 0.75 mg and 1.5 mg once weekly; No dosage adjustment; Use with eGFR >15 ml/min per 1.73 m² | kdigo-2022-diabetes-ckd | p88 | p88/narrative/dulaglutide-dose | narrative |
| glp1-exenatide-dose | people-t2d-ckd-glp1 | exenatide 10 micrograms twice daily; use CrCl >30 | RENDERED: Exenatide 10 μg twice daily; Use with CrCl >30 ml/min | kdigo-2022-diabetes-ckd | p88 | p88/narrative/exenatide-dose | narrative |
| glp1-exenatide-er-dose | people-t2d-ckd-glp1 | exenatide extended-release 2 mg weekly; use eGFR >45 | RENDERED: Exenatide extended-release 2 mg once weekly; Use with eGFR >45 ml/min per 1.73 m² | kdigo-2022-diabetes-ckd | p88 | p88/narrative/exenatide-er-dose | narrative |
| glp1-liraglutide-dose | people-t2d-ckd-glp1 | liraglutide 1.2 or 1.8 mg daily; no adjustment; limited severe-CKD data | RENDERED: Liraglutide 1.2 mg and 1.8 mg once daily; No dosage adjustment; Limited data for severe CKD | kdigo-2022-diabetes-ckd | p88 | p88/narrative/liraglutide-dose | narrative |
| glp1-lixisenatide-dose | people-t2d-ckd-glp1 | lixisenatide 10 or 20 micrograms daily; no adjustment; not recommended eGFR <15 | RENDERED: Lixisenatide 10 μg and 20 μg once daily; No dosage adjustment; Not recommended with eGFR <15 ml/min per 1.73 m² | kdigo-2022-diabetes-ckd | p88 | p88/narrative/lixisenatide-dose | narrative |
| glp1-semaglutide-injection-dose | people-t2d-ckd-glp1 | injectable semaglutide 0.5 or 1 mg weekly; no adjustment; limited severe-CKD data | RENDERED: Semaglutide (injection) 0.5 mg and 1 mg once weekly; No dosage adjustment; Limited data for severe CKD | kdigo-2022-diabetes-ckd | p88 | p88/narrative/semaglutide-injection-dose | narrative |
| glp1-semaglutide-oral-dose | people-t2d-ckd-glp1 | oral semaglutide 3, 7, or 14 mg daily; no adjustment; limited severe-CKD data | RENDERED: Semaglutide (oral) 3 mg, 7 mg, or 14 mg daily; No dosage adjustment; Limited data for severe CKD | kdigo-2022-diabetes-ckd | p88 | p88/narrative/semaglutide-oral-dose | narrative |
| nutrition-education | people-diabetes-ckd | self-management education available at diagnosis, annually, when complications arise, and at transitions in care | is available to patients at critical times (i.e., at diagnosis, annually, when complications arise, and when transitions in care occur) | kdigo-2022-diabetes-ckd | p91 | p91/narrative/self-management-timing | narrative |
| self-management-education | people-diabetes-ckd | implement a structured self-management educational program tailored to local context, culture, and resources | We recommend that a structured self-management educational program be implemented for care of people with diabetes and CKD | kdigo-2022-diabetes-ckd | p90 | p90/narrative/self-management-program | narrative |
| team-based-care | people-diabetes-ckd-integrated-care | implement team-based integrated care focused on risk evaluation, patient empowerment, and comprehensive care | RENDERED: implement team-based, integrated care focused on risk evaluation and patient empowerment to provide comprehensive care in patients with diabetes and CKD | kdigo-2022-diabetes-ckd | p94 | p94/narrative/team-based-care | narrative |
| integrated-comprehensive-assessment | people-diabetes-ckd-integrated-care | comprehensive blood/urine and eye/foot assessment every 12-18 months | RENDERED: comprehensive risk assessment, including blood/urine and eye/foot examination every 12-18 months | kdigo-2022-diabetes-ckd | p97 | p97/narrative/comprehensive-risk-assessment | narrative |
| integrated-cardiometabolic-assessment | people-diabetes-ckd-integrated-care | cardiometabolic factors every 2-3 months | RENDERED: Assess cardiometabolic risk factors (e.g., blood pressure, glycated hemoglobin, body weight) every 2-3 months | kdigo-2022-diabetes-ckd | p97 | p97/narrative/cardiometabolic-assessment | narrative |
| integrated-kidney-assessment | people-diabetes-ckd-integrated-care | kidney function every 3-12 months | RENDERED: Assess kidney function (e.g., eGFR and ACR) every 3-12 months | kdigo-2022-diabetes-ckd | p97 | p97/narrative/kidney-assessment | narrative |

## Conflicts

CONFLICT: finerenone-initiation-potassium | people-t2d-ckd-finerenone | `trial-based initiation target K <=4.8 mmol/L` versus `FDA-approved initiation K <5.0 mmol/L`; the guideline tells clinicians to focus on the trial target while also reporting the FDA-approved initiation threshold; source p52-p53.
CONFLICT: physical-activity | adults-diabetes-ckd-activity | `moderate intensity for at least 150 minutes/week or compatible tolerance` versus `rendered algorithm branches: physically active >150 min/week versus physically active <150 min/week`; the recommendation includes exactly 150 minutes, while neither rendered algorithm branch does; source p71 and p74.
CONFLICT: metformin-dose-adjustment | people-t2d-ckd-metformin | `eGFR 45-59: continue same dose and consider reduction in certain hypoperfusion/hypoxemia conditions; eGFR 30-44: initiate at half dose and titrate to half maximum, or halve existing dose; eGFR <30: stop and do not initiate` versus `narrative: halve maximum dose when eGFR declines to 30-45 mL/min/1.73 m²`; the narrative includes eGFR 45 in its halving interval while Figure 27 assigns 45 to the 45-59 branch; source p81-p82.

## Coverage

The bound recommendation artifact contains **145 recommendation-marker occurrences representing 144 unique identifiers**. This sheet cites **0** marker occurrences in threshold rows and individually dispositions **145** occurrences below; **145 = 0 + 145**. The duplicated identifier `p22/recommendation/1.3.1` occurs twice in the bound record and therefore appears in two separate bullets.

ADR 0009 disposition: all guideline-adopted eligibility, monitoring, medication, lifestyle, glycemic-monitoring, education, and team-care actions identified in the full read are retained. Pivotal-trial enrollment eGFR cutoffs that are not adopted prescribing thresholds and the study observation that education programs with more than 10 contact hours had the best outcomes are evidence only and are not converted into patient-action rows.

- `p20/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p21/recommendation/1.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p21/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p21/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p21/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p21/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p21/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/recommendation/1.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/recommendation/1.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p22/practice-point/10` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/recommendation/1.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/recommendation/1.5.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p23/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/recommendation/2.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/recommendation/2.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p24/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/recommendation/3.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/recommendation/3.1.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/recommendation/3.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/10` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/11` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p25/practice-point/12` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p27/recommendation/4.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p27/recommendation/4.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p27/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p27/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p27/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p27/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p27/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p28/recommendation/5.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p28/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p28/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p28/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p28/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p29/recommendation/5.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p29/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p29/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p32/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p33/recommendation/1.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p34/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p36/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p36/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p37/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p37/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p38/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p39/recommendation/1.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p46/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/recommendation/1.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p47/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p48/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/recommendation/1.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/recommendation/1.4.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p49/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p52/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/recommendation/1.3.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p53/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p54/recommendation/1.5.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p54/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p54/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p55/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p56/recommendation/2.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p58/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p58/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p58/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p58/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p60/recommendation/2.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p60/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p60/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p63/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p63/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p64/recommendation/3.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p64/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p66/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p67/recommendation/3.1.2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p67/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p67/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p70/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p70/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p71/recommendation/3.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p71/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p73/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p74/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p74/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p74/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p76/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p76/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p78/recommendation/4.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p78/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p81/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p81/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p81/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p81/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p82/recommendation/4.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p87/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p88/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p88/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p88/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p88/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p90/recommendation/5.1.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p92/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p94/recommendation/5.2.1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p94/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
- `p97/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from source tables, figures, narrative, or a duplicate summary/body occurrence
