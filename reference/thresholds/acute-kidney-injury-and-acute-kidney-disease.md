# Acute kidney injury and acute kidney disease — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. This source is explicitly a
public-review draft. Graded by `tools/threshold_sheet.py`; what that grader cannot
see is written out in [README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2026 | KDIGO | KDIGO/KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026 | draft | Public Review Draft | 2026-03 | https://kdigo.org/guidelines/acute-kidney-injury/ | chosen | bound |

## Scope

**Read:** all 499 source pages: front matter and contents; the complete summary of
recommendations and practice points; all six clinical chapters, including every table
and figure; the complete guideline-development methods; and the reference list. The
threshold rows below retain only numbers that define, classify, dose, time, monitor,
refer, start, stop, or otherwise change an action for a patient. Evidence-effect
estimates, cohort characteristics, publication years, and bibliography numbers were
read but do not produce rows.

Table 53 on pp312–313 was read in full. Its product-by-product electrolyte composition
matrix is descriptive inventory, not a patient-action cutoff: the surrounding text requires
individualized selection based on the patient's metabolic, electrolyte, and acid-base
abnormalities and supplies no product-specific start, stop, or target threshold. The numeric
patient-action decision from that passage—the 6–12-hour reassessment interval—is retained
below.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| front matter, contents, and lists | 1-14 | read 2026-08-31; blind 2026-08-31 |
| summary of recommendations and practice points | 15-48 | yes |
| chapter 1: definition, identification, and classification | 49-79 | yes |
| chapter 2: prediction, risk stratification, and diagnostic evaluation | 80-131 | yes |
| chapter 3: prevention and treatment | 132-207 | yes |
| chapter 4: drug- and nephrotoxin-associated AKI | 208-259 | yes |
| chapter 5: renal replacement therapy | 260-332 | yes |
| chapter 6: follow-up care | 333-367 | yes |
| guideline-development methods | 368-391 | read 2026-08-31; blind 2026-08-31 |
| references | 392-499 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| children-adults | children and adults |
| adults-aki | adults with AKI |
| children-aki | children with AKI |
| neonates | neonates |
| adults-suspected-confirmed-aki | all patients with suspected or confirmed AKI |
| children-except-neonates | children (except neonates) |
| critically-ill-adults-aki-risk | critically ill adults at high risk of or with AKI |
| adults-elective-abdominal-surgery | adults undergoing elective major abdominal surgery |
| critically-ill-children-adults-aki-akd | critically ill children and adults with or at risk of AKI or AKD |
| adults-stage1-2-aki-euvolemic-hypervolemic | adults with Stage 1 or 2 AKI who are euvolemic or hypervolemic |
| children-stage1-2-aki-euvolemic-hypervolemic | children with Stage 1 or 2 AKI who are euvolemic or hypervolemic |
| community-adults-aki-risk | adults at risk for community-acquired acute kidney injury |
| critically-ill-children-aki-risk | critically ill children at risk for AKI |
| adults-aki-volume-overload | adults with AKI-related volume overload |
| adults-cardiac-surgery-no-advanced-ckd | adults without advanced CKD having cardiac surgery |
| cardiac-surgery-high-risk-no-propofol | patients at high risk for AKI undergoing cardiac surgery without propofol anesthesia |
| adults-hrs-aki | adults with hepatorenal syndrome-associated AKI |
| tumor-lysis-risk | children and adults with or at risk of tumor lysis syndrome |
| children-aki-akd-crrt | children with AKI or AKD receiving CRRT |
| people-crrt | people receiving CRRT |
| adults-high-risk-ca-aki | adults at high risk of AKI without fluid overload undergoing intravascular iodinated contrast-based procedures |
| adults-high-risk-ca-aki-broad | adults at high risk of CA-AKI |
| adults-sick-day-guidance | adults using sick day medication guidance |
| adults-crrt | adults receiving CRRT |
| adults-irrt-pirrt-aki | adults receiving IRRT or PIRRT for AKI |
| adults-acute-pd-aki | adults with AKI receiving acute PD |
| adults-rrt-deferred | adults with AKI managed with deferred RRT initiation |
| adults-starting-irrt | adults starting or transitioning to IRRT |
| adults-rrt-discontinuation | adults being assessed for successful RRT discontinuation |
| critically-ill-children-severe-aki | critically ill children with severe AKI |
| children-rrt | children receiving acute RRT |
| children-crrt | children receiving CRRT |
| children-acute-pd | children with AKI receiving acute PD |
| children-hyperammonemia | children with hyperammonemia receiving CRRT |
| children-rrt-discontinuation | children being assessed for successful RRT discontinuation |
| children-adults-after-aki-akd | children and adults after AKI or AKD |
| adults-post-aki-medications | adults after AKI or AKD with an indication for kidney- or cardiovascular-protective medication |
| adults-after-outpatient-dialysis | adults after discontinuation of outpatient dialysis for AKI |
| pediatric-low-risk-survivors | children with Stage 1 AKI resolved in less than 48 hours and normal urinalysis and SCr at discharge |
| pediatric-high-risk-survivors | children with Stage 2-3 AKI, AKI lasting more than 48 hours, proteinuria, residual creatinine or cystatin C elevation, RRT requirement, or birth before 28 weeks' gestation |
| adults-children-aki-akd | adults and children with AKI or AKD |
| newborns-nephrotoxin-exposed | newborns exposed to nephrotoxic medications |
| adults-critically-ill-rrt | critically ill adults receiving RRT |
| adults-crrt-liberation | critically ill adults being assessed for CRRT discontinuation |
| children-adults-post-aki-akd-follow-up | children and adults requiring follow-up after AKI or AKD |
| adults-post-aki-mra | adults after AKI with an indication for MRA treatment, stable kidney function, and no contraindication |
| adults-outpatient-dialysis-aki | adults receiving outpatient dialysis after AKI |
| children-iga-proteinuria | children with IgA nephropathy and proteinuria |
| very-low-birth-weight-infants-pd | extreme and very-low birth weight infants receiving acute PD |
| neonates-small-children-crrt | neonates and small children receiving CRRT |
| adults-aki-akd | adults with AKI or AKD |
| adults-major-surgery-rasi-withholding | adults undergoing major surgery who are appropriate candidates for temporary RASi withholding, typically those having high-risk surgery or with elevated AKI risk |
| critically-ill-children-rrt | critically ill children receiving RRT |
| predominantly-adults-post-aki-akd-follow-up | predominantly adults requiring follow-up after AKI or AKD |
| predominantly-children-post-aki-akd-follow-up | predominantly children requiring follow-up after AKI or AKD |
| children-post-aki-akd-follow-up | children requiring follow-up after AKI or AKD |

## Quantities

| key | verbatim |
| --- | --- |
| aki-scr-absolute-definition | Increase in SCr by ≥0.3 mg/dl within 48 hours |
| aki-scr-relative-definition | Increase in SCr by ≥1.5 times baseline within the prior 7 days |
| aki-cystatin-relative-definition | Increase in serum cystatin C by ≥1.5 times baseline within the prior 7 days |
| aki-urine-output-definition | Mean urine volume of less than 0.5 ml/kg/h for ≥6 hours |
| adult-baseline-scr-window | representative primary care/outpatient serum creatinine |
| adult-baseline-back-calculation | assuming an estimated GFR of 75 ml/min per 1.73 m2 |
| aki-scr-stage-c1 | C1 serum creatinine criteria |
| aki-scr-stage-c2 | C2 serum creatinine criteria |
| aki-scr-stage-c3 | C3 serum creatinine criteria |
| aki-urine-stage-u1 | U1 urine output criteria |
| aki-urine-stage-u2 | U2 urine output criteria |
| aki-urine-stage-u3 | U3 urine output criteria |
| transient-aki-duration | Transient AKI |
| persistent-aki-duration | Persistent AKI |
| akd-duration | Criteria for AKD |
| akd-gfr-level | GFR <60 ml/min per 1.73 m2 |
| akd-gfr-decrease | Decrease in GFR by ≥35 ml/min per 1.73 m2 from baseline |
| akd-scr-increase | Increase in SCr by >50% |
| aki-complete-resolution | Complete resolution of AKI |
| aki-partial-resolution | Partial resolution of AKI |
| akd-complete-resolution | Complete resolution of AKD |
| akd-partial-resolution | Partial resolution of AKD |
| pediatric-baseline-window | representative outpatient SCr |
| pediatric-back-calculated-gfr | baseline creatinine estimation methods in children |
| neonatal-aki-scr-decline | No decline in SCr from birth to 7 days of life |
| neonatal-aki-scr-absolute | Increase in SCr by ≥0.3 mg/dl within 48 hours |
| neonatal-aki-scr-relative | Increase in SCr by ≥1.5 times baseline within the prior 7 days |
| neonatal-aki-cystatin-relative | Increase in serum cystatin C by 1.25 times baseline within the prior 7 days |
| neonatal-aki-cystatin-level | Serum cystatin C >2.2 mg/dl |
| neonatal-aki-urine-output | Urine output of less than 1.0 ml/kg/h for ≥24 hours |
| neonatal-scr-stage-c1 | neonatal C1 serum creatinine criteria |
| neonatal-scr-stage-c2 | neonatal C2 serum creatinine criteria |
| neonatal-scr-stage-c3 | neonatal C3 serum creatinine criteria |
| neonatal-urine-stage-u1 | neonatal U1 urine output criteria |
| neonatal-urine-stage-u2 | neonatal U2 urine output criteria |
| neonatal-urine-stage-u3 | neonatal U3 urine output criteria |
| community-aki-risk-score | Clinical risk score for community-acquired acute kidney injury |
| biomarker-assessment-window | within the first 12 hours of ICU admission |
| fst-dose | protocolized dose of intravenous furosemide |
| fst-adult-response | limited volume of urine |
| fst-child-response | urine output criterion |
| rai-high-risk-threshold | high RAI |
| rai-injury-score | Kidney Injury or Volume overload |
| severe-acidemia-bicarbonate-threshold | severe metabolic acidosis with acidemia |
| postoperative-fluid-balance | positive fluid balance gain |
| map-target | mean arterial pressure target |
| glucose-target | plasma glucose level |
| pediatric-protein-minimum | minimum daily protein intake |
| theophylline-administration | single dose of theophylline |
| furosemide-assessment-dose | furosemide assessment dose |
| furosemide-response-goal | urine output goal after furosemide |
| furosemide-escalation | loop-diuretic escalation |
| thiazide-synergism | thiazide-like diuretic dose and timing |
| furosemide-infusion | continuous furosemide infusion |
| amino-acid-prophylaxis | prophylactic intravenous amino acid administration |
| remote-ischemic-preconditioning | principles of remote ischemic preconditioning |
| terlipressin-infusion | continuous terlipressin infusion |
| terlipressin-bolus | terlipressin intravenous bolus |
| norepinephrine-hrs | norepinephrine continuous intravenous infusion |
| midodrine-hrs | midodrine oral dose |
| octreotide-hrs | octreotide subcutaneous dose |
| tumor-lysis-urine-flow | goal of increasing urine flow |
| crrt-drug-removal-supplement | supplemental doses for drugs removed by hemodialysis |
| crrt-loading-dose | loading dose during fluid resuscitation and capillary leak |
| residual-urine-clearance | residual urine volume added to RRT clearance calculations |
| ca-aki-risk-egfr | risk factors for CA-AKI following intravenous contrast |
| max-allowable-contrast | maximum allowable contrast dose |
| contrast-crcl-ratio | contrast-volume-to-creatinine-clearance ratio |
| lvedp-hydration | LVEDP-guided hydration protocol |
| cvp-hydration | CVP-guided hydration protocol |
| biva-hydration | bioimpedance-guided hydration protocol |
| forced-diuresis-hydration | matched hydration with forced diuresis |
| contrast-nephrotoxin-hold | withdrawal of nonessential potentially nephrotoxic medications |
| contrast-metformin-hold | metformin management around contrast |
| sick-day-weight-trigger | decreased weight trigger |
| sick-day-medication-hold | temporary medication hold duration |
| sick-day-insulin-increase | empirical insulin increase |
| sick-day-support-trigger | timing to seek healthcare assistance |
| rrt-hyperkalemia-indication | severe hyperkalemia indication for RRT |
| rrt-acidemia-indication | severe acidemia indication for RRT |
| rrt-hepatic-encephalopathy | hepatic encephalopathy threshold for CRRT consideration |
| adult-crrt-effluent | effluent volume for adults receiving CRRT |
| adult-irrt-ktv | weekly Kt/V for adults receiving IRRT or PIRRT |
| adult-high-bmi | high body mass index |
| adult-pd-dose | weekly Kt/V and PD fluid volume |
| irrt-albumin | supplemental albumin before IRRT |
| irrt-midodrine | midodrine before or during IRRT |
| irrt-blood-flow | initial IRRT blood flow titration |
| irrt-dialysate-temperature | initial dialysate temperature |
| irrt-sodium | initial dialysate sodium concentration |
| rrt-catheter-size | pediatric dialysis catheter size |
| citrate-anticoagulation | regional citrate anticoagulation dose |
| heparin-anticoagulation | unfractionated heparin dose |
| lmwh-anticoagulation | low molecular weight heparin dose |
| nafamostat-anticoagulation | nafamostat dose |
| argatroban-anticoagulation | argatroban dose |
| bivalirudin-anticoagulation | bivalirudin dose |
| epoprostenol-anticoagulation | epoprostenol dose |
| ultrafiltration-review | ultrafiltration prescription review interval |
| adult-rrt-urine-output | urine output predicting RRT discontinuation |
| adult-rrt-creatinine-clearance | timed creatinine clearance predicting RRT discontinuation |
| pediatric-rrt-initiation | timing of RRT initiation in severe pediatric AKI |
| pediatric-crrt-effluent | initial CRRT effluent volume for children |
| pediatric-pd-prescription | initial pediatric PD prescription |
| pediatric-hyperammonemia-crrt | augmented CRRT dose-intensity for hyperammonemia |
| pediatric-hyperammonemia-start | ammonia threshold and response window for CRRT |
| pediatric-ufnet | pediatric net ultrafiltration ceiling |
| pediatric-fluid-review | pediatric fluid-balance assessment interval |
| pediatric-rrt-urine-output | urine output predicting pediatric RRT discontinuation |
| medication-resumption-review | starting or resuming guideline-indicated medications |
| post-aki-kidney-assessment | assessment of kidney function and kidney damage |
| post-dialysis-nephrology-assessment | nephrology assessment after outpatient dialysis discontinuation |
| pediatric-low-risk-follow-up | low-risk pediatric follow-up interval |
| pediatric-high-risk-follow-up | high-risk pediatric follow-up interval |
| pediatric-high-risk-definition | high-risk pediatric AKI survivor criteria |
| pediatric-kidney-health-check | kidney health assessment after AKI |
| aki-damage-biomarker-stage | damage-biomarker stage |
| epidemiology-baseline-scr-window | baseline SCr for epidemiological research |
| isn-0by25-risk-score-components | ISN 0by25 clinical risk-score points |
| pediatric-rai-application-window | timing of the pediatric renal angina index |
| adult-protein-intake-comparison | high versus usual protein intake |
| gentamicin-trough | gentamicin target trough concentration |
| amikacin-trough | amikacin target trough concentration |
| methotrexate-glucarpidase-window | glucarpidase timing after methotrexate |
| perioperative-rasi-hold | general timing when RASi are withheld before surgery |
| post-sick-day-medication-review | medication review after an acute illness medication hold |
| neonatal-urine-ngal-ruleout | urine NGAL value with reported negative predictive value |
| neonatal-urine-ngal-rulein | urine NGAL value with reported positive likelihood ratio |
| adult-rrt-modality-parameters | adult RRT modality parameter matrix |
| irrt-dialysate-flow | initial IRRT dialysate flow rate |
| irrt-initial-ultrafiltration | initial IRRT ultrafiltration |
| adult-rrt-catheter-size | adult dialysis catheter size |
| adult-rrt-catheter-flow | adult dialysis catheter blood flow |
| right-ij-catheter-length-formula | Peres right internal jugular catheter formula |
| left-ij-catheter-length-formula | Peres left internal jugular catheter formula |
| right-subclavian-catheter-length-formula | Peres right subclavian catheter formula |
| left-subclavian-catheter-length-formula | Peres left subclavian catheter formula |
| irrt-dialysate-bacteria-limit | maximum dialysate bacterial contamination |
| irrt-dialysate-endotoxin-limit | maximum dialysate endotoxin contamination |
| ultrapure-dialysate-bacteria-target | ultrapure dialysate bacterial target |
| ultrapure-dialysate-endotoxin-target | ultrapure dialysate endotoxin target |
| crrt-solution-reassessment | CRRT solution reassessment interval |
| scheduled-ihd-stop-urine-no-diuretic | urine output criterion to stop scheduled IHD without diuretics |
| scheduled-ihd-stop-urine-diuretic | urine output criterion to stop scheduled IHD with diuretics |
| scheduled-ihd-stop-creatinine-clearance | creatinine clearance criterion to stop scheduled IHD |
| crrt-liberation-score-urine | urine output in a CRRT liberation score |
| crrt-liberation-score-map | MAP in a CRRT liberation score |
| crrt-liberation-score-potassium | serum potassium in a CRRT liberation score |
| crrt-liberation-score-bun | BUN in a CRRT liberation score |
| liberate-ihd-bun-indication | LIBERATE-D BUN indication for IHD |
| liberate-ihd-potassium-indication | LIBERATE-D potassium indication for IHD |
| liberate-ihd-acidemia-indication | LIBERATE-D acidemia indication for IHD |
| crrt-stop-low-urine | urine output associated with lower likelihood of CRRT liberation |
| crrt-stop-minimum-urine | minimum urine output associated with CRRT liberation |
| crrt-stop-hourly-urine | hourly urine output associated with CRRT liberation |
| pediatric-rrt-modality-parameters | pediatric RRT modality parameter matrix |
| vlbw-pd-fill | acute PD fill volume for very-low birth weight infants |
| vlbw-pd-dwell | acute PD dwell time for very-low birth weight infants |
| pediatric-extracorporeal-circuit-volume | extracorporeal circuit volume that may cause instability |
| post-aki-mra-egfr | eGFR for cautious MRA reinitiation after AKI |
| outpatient-aki-dialysis-kidney-monitoring | kidney-function monitoring during the first outpatient month |
| pediatric-iga-proteinuria | pediatric IgA nephropathy proteinuria threshold for RAS blockade |
| early-post-aki-follow-up-window | early follow-up interval after AKI or AKD |
| later-post-aki-follow-up-window | later follow-up interval after AKI or AKD |
| later-post-aki-cardiovascular-follow-up | later cardiovascular follow-up after AKI or AKD |
| later-post-aki-neurocognitive-follow-up | later neurocognitive follow-up after AKI or AKD |
| later-post-aki-growth-nutrition-follow-up | later growth and nutrition follow-up after AKI or AKD |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aki-scr-absolute-definition | children-adults | increase >=0.3 mg/dl (>=26.5 µmol/l) within 48 hours | Increase in SCr by ≥0.3 mg/dl (≥26.5 µmol/l) within 48 hours | kdigo-2026 | p15 | p15/narrative/aki-scr-absolute | narrative |
| aki-scr-relative-definition | children-adults | increase >=1.5 times baseline within 7 days | Increase in SCr by ≥1.5 times baseline that is known or presumed to have occurred within the prior 7 days | kdigo-2026 | p15 | p15/narrative/aki-scr-relative | narrative |
| aki-cystatin-relative-definition | children-adults | increase >=1.5 times baseline within 7 days | Increase in serum cystatin C by ≥1.5 times baseline that is known or presumed to have occurred within the prior 7 days | kdigo-2026 | p15 | p15/narrative/aki-cystatin-relative | narrative |
| aki-urine-output-definition | children-adults | <0.5 ml/kg/h for >=6 hours | Mean urine volume of less than 0.5 ml/kg/h (based on ideal body weight) for ≥6 hours | kdigo-2026 | p15 | p15/narrative/aki-urine-output | narrative |
| adult-baseline-scr-window | adults-suspected-confirmed-aki | mean, median, or most recent value 8-365 days before admission or acute event | may be a mean, median, or most recent value between 8–365 days before a hospital admission (or acute event) | kdigo-2026 | p16 | p16/narrative/adult-baseline-window | narrative |
| adult-baseline-back-calculation | adults-suspected-confirmed-aki | if no measurement: assume eGFR 75 ml/min per 1.73 m2 | In the absence of any available measurements, we advise back calculating, assuming an estimated GFR (eGFR) of 75 ml/min per 1.73 m2 for adults | kdigo-2026 | p63 | p63/narrative/adult-baseline-back-calculation | narrative |
| aki-scr-stage-c1 | children-adults | C1: increase >=0.3 mg/dl (>=26.5 µmol/l) or 1.5-1.9 times baseline | RENDERED: C1: ≥0.3 mg/dl (≥26.5 µmol/l) increase, or 1.5-1.9 times baseline | kdigo-2026 | p17 | p17/narrative/aki-stage-c1 | narrative |
| aki-scr-stage-c2 | children-adults | C2: 2-2.9 times baseline | 2–2.9 times baseline | kdigo-2026 | p17 | p17/narrative/aki-stage-c2 | narrative |
| aki-scr-stage-c3 | children-adults | C3: >=3 times baseline or SCr >=4.0 mg/dl (>=353.6 µmol/l) or RRT initiation | RENDERED: C3: ≥3.0 times baseline, or increase in SCr to ≥4.0 mg/dl (≥353.6 µmol/l), or initiation of RRT | kdigo-2026 | p17 | p17/narrative/aki-stage-c3 | narrative |
| aki-urine-stage-u1 | children-adults | U1: <0.5 ml/kg/h for 6-12 hours | RENDERED: U1: <0.5 ml/kg/h for 6–12 hours | kdigo-2026 | p17 | p17/narrative/aki-stage-u1 | narrative |
| aki-urine-stage-u2 | children-adults | U2: <0.5 ml/kg/h for >12 hours | RENDERED: U2: <0.5 ml/kg/h for >12 hours | kdigo-2026 | p17 | p17/narrative/aki-stage-u2 | narrative |
| aki-urine-stage-u3 | children-adults | U3: <0.3 ml/kg/h for >24 hours or anuria >12 hours | RENDERED: U3: <0.3 ml/kg/h for >24 hours or anuria for >12 hours | kdigo-2026 | p17 | p17/narrative/aki-stage-u3 | narrative |
| transient-aki-duration | children-adults | <=48 hours | ≤48 hour increase in SCr or cystatin C or reduced urine output | kdigo-2026 | p17 | p17/practice-point/1 | Practice Point |
| persistent-aki-duration | children-adults | >48 hours and up to 7 days | >48 hour and up to 7 days increase in SCr or cystatin C or reduced urine output | kdigo-2026 | p17 | p17/narrative/persistent-aki | narrative |
| akd-duration | children-adults | <=3 months | Criteria for AKD (any one or more of the following with a duration ≤3 months) | kdigo-2026 | p18 | p18/narrative/akd-duration | narrative |
| akd-gfr-level | children-adults | GFR <60 ml/min per 1.73 m2; criterion does not apply below age 2 years | GFR <60 ml/min per 1.73 m2 criterion does not apply to children younger than 2 years old | kdigo-2026 | p18 | p18/narrative/akd-gfr-level | narrative |
| akd-gfr-decrease | children-adults | decrease >=35 ml/min per 1.73 m2 from baseline | Decrease in GFR by ≥35 ml/min per 1.73 m2 from baseline | kdigo-2026 | p18 | p18/narrative/akd-gfr-decrease | narrative |
| akd-scr-increase | children-adults | SCr increase >50% | Increase in SCr by >50% | kdigo-2026 | p18 | p18/narrative/akd-scr-increase | narrative |
| aki-complete-resolution | children-adults | SCr or cystatin C <1.2 times baseline within 7 days | SCr or serum cystatin C <1.2 times higher than baseline within 7 days | kdigo-2026 | p18 | p18/narrative/aki-complete-resolution | narrative |
| aki-partial-resolution | children-adults | SCr or cystatin C >=1.2 to <1.5 times baseline within 7 days | SCr or serum cystatin C ≥1.2 to <1.5 times higher than baseline within 7 days | kdigo-2026 | p18 | p18/narrative/aki-partial-resolution | narrative |
| akd-complete-resolution | children-adults | SCr or cystatin C <1.2 times baseline or eGFR >80% baseline within 3 months | SCr or serum cystatin C <1.2 times higher than baseline, Or eGFR >80% of baseline within 3 months | kdigo-2026 | p18 | p18/narrative/akd-complete-resolution | narrative |
| akd-partial-resolution | children-adults | SCr or cystatin C >=1.2 to <1.5 times baseline or eGFR <80% to >66% baseline within 3 months | SCr or serum cystatin C ≥1.2 to <1.5 times higher than baseline, Or eGFR <80% to >66% of baseline within 3 months | kdigo-2026 | p18 | p18/narrative/akd-partial-resolution | narrative |
| pediatric-baseline-window | children-except-neonates | mean, median, or most recent outpatient SCr within 3 months | reflect the mean, median, or most recent value within 3 months of admission or acute event | kdigo-2026 | p19 | p19/narrative/pediatric-baseline-window | narrative |
| pediatric-back-calculated-gfr | children-except-neonates | assumed eGFR 100-120 ml/min per 1.73 m² | assuming an eGFR of 100–120 ml/min per 1.73 m² | kdigo-2026 | p75 | p75/narrative/pediatric-back-calculated-gfr | narrative |
| neonatal-aki-scr-decline | neonates | no decline from birth to day 7 | No decline in SCr from birth to 7 days of life | kdigo-2026 | p19 | p19/narrative/neonatal-no-decline | narrative |
| neonatal-aki-scr-absolute | neonates | increase >=0.3 mg/dl (>=26.5 µmol/l) within 48 hours | Increase in SCr by ≥0.3 mg/dl (≥26.5 µmol/l) within 48 hours | kdigo-2026 | p19 | p19/narrative/neonatal-scr-absolute | narrative |
| neonatal-aki-scr-relative | neonates | increase >=1.5 times baseline within 7 days | Increase in SCr by ≥1.5 times baseline that is known or presumed to have occurred within the prior 7 days | kdigo-2026 | p19 | p19/narrative/neonatal-scr-relative | narrative |
| neonatal-aki-cystatin-relative | neonates | increase 1.25 times baseline within 7 days | Increase in serum cystatin C by 1.25 times baseline that is known or presumed to have occurred within the prior 7 days | kdigo-2026 | p19 | p19/narrative/neonatal-cystatin-relative | narrative |
| neonatal-aki-cystatin-level | neonates | >2.2 mg/dl | Serum cystatin C >2.2 mg/dl | kdigo-2026 | p19 | p19/narrative/neonatal-cystatin-level | narrative |
| neonatal-aki-urine-output | neonates | <1.0 ml/kg/h for >=24 hours | Urine output of less than 1.0 ml/kg/h for ≥24 hours | kdigo-2026 | p19 | p19/narrative/neonatal-urine-output | narrative |
| neonatal-scr-stage-c1 | neonates | C1: no decline by day 7, increase >=0.3 mg/dl, or 1.5-1.9 times baseline | RENDERED: C1: No decline in SCr from birth to 7 days of life, or ≥0.3 mg/dl (26.5 µmol/l) increase, or 1.5–1.9 times baseline | kdigo-2026 | p20 | p20/narrative/neonatal-stage-c1 | narrative |
| neonatal-scr-stage-c2 | neonates | C2: 2-2.9 times baseline | 2–2.9 times baseline | kdigo-2026 | p20 | p20/narrative/neonatal-stage-c2 | narrative |
| neonatal-scr-stage-c3 | neonates | C3: >=3 times baseline, SCr >=2.5 mg/dl (220 µmol/l), or RRT initiation | ≥3 times baseline Or Increase in SCr to ≥2.5 mg/dl (220 µmol/l), Or Initiation of RRT | kdigo-2026 | p20 | p20/narrative/neonatal-stage-c3 | narrative |
| neonatal-urine-stage-u1 | neonates | U1: >0.5 and <=1.0 ml/kg/h for 24 hours | RENDERED: U1: >0.5 and ≤1.0 ml/kg/h for 24 h | kdigo-2026 | p20 | p20/narrative/neonatal-stage-u1 | narrative |
| neonatal-urine-stage-u2 | neonates | U2: >0.3 and <=0.5 ml/kg/h for 24 hours | RENDERED: U2: >0.3 and ≤0.5 ml/kg/h for 24 h | kdigo-2026 | p20 | p20/narrative/neonatal-stage-u2 | narrative |
| neonatal-urine-stage-u3 | neonates | U3: <=0.3 ml/kg/h for 24 hours | RENDERED: U3: ≤0.3 ml/kg/h for 24 h | kdigo-2026 | p20 | p20/narrative/neonatal-stage-u3 | narrative |
| community-aki-risk-score | community-adults-aki-risk | score >=3 prompts point-of-care SCr and urine dipstick testing | screened as moderate-to-high risk (score ≥3) | kdigo-2026 | p89 | p89/narrative/community-aki-risk-score | narrative |
| biomarker-assessment-window | critically-ill-children-adults-aki-akd | especially within first 12 hours of ICU admission or after high-risk events | especially within the first 12 hours of ICU admission or after high-risk events | kdigo-2026 | p22 | p22/practice-point/2 | Practice Point |
| fst-dose | adults-stage1-2-aki-euvolemic-hypervolemic | furosemide 1 mg/kg or 1.5 mg/kg IV | protocolized (1 mg/kg or 1.5 mg/kg) dose of intravenous furosemide | kdigo-2026 | p100 | p100/narrative/fst-dose | narrative |
| fst-adult-response | adults-stage1-2-aki-euvolemic-hypervolemic | <200 ml urine in 2 hours predicts progression within 14 days | <200 ml in the 2 hours after the receipt of intravenous furosemide) are more likely to experience AKI progression to Stage 3 AKI (including the need for RRT) in the next 14 days | kdigo-2026 | p100 | p100/narrative/fst-adult-response | narrative |
| fst-child-response | children-stage1-2-aki-euvolemic-hypervolemic | <2 ml/kg/hour over 2 hours | urine output criterion of <2 ml/kg/hour over 2 hours | kdigo-2026 | p101 | p101/narrative/fst-child-response | narrative |
| rai-high-risk-threshold | critically-ill-children-aki-risk | RAI >=8: kidney-protective strategies, closer monitoring, and RRT preparedness | high RAI (≥8) has moderate accuracy to predict incident AKI | kdigo-2026 | p129 | p129/narrative/rai-high-risk-threshold | narrative |
| rai-injury-score | critically-ill-children-aki-risk | no eCrCl decrease or <5% overload=1; eCrCl decrease 0-25% or >5%=2; decrease 25-50% or >10%=4; decrease >50% or >15%=8 | No decrease in eCrCl or < 5% FO • eCrCl decrease 0-25% or >5% FO • eCrCl decrease 25-50% or >10% FO • eCrCl decrease >50% or >15% FO 1 point 2 points 4 points 8 points | kdigo-2026 | p129 | p129/narrative/rai-injury-score | narrative |
| severe-acidemia-bicarbonate-threshold | children-adults | pH <7.20: intravenous bicarbonate over RRT unless another urgent RRT indication | severe metabolic acidosis with acidemia (pH <7.20), we suggest the use of intravenous bicarbonate over RRT | kdigo-2026 | p24 | p24/recommendation/3.1.3 | 2C |
| postoperative-fluid-balance | adults-elective-abdominal-surgery | positive 1-2 kg at 24 hours after surgery | aiming for a positive fluid balance gain of 1–2 kg at 24 hours after surgery | kdigo-2026 | p24 | p24/recommendation/3.1.4 | 1B |
| map-target | critically-ill-adults-aki-risk | >65 mm Hg | mean arterial pressure (MAP) of >65 mm Hg as a target | kdigo-2026 | p24 | p24/recommendation/3.2.1 | 2C |
| glucose-target | critically-ill-children-adults-aki-akd | 140-180 mg/dl (7.8-10 mmol/l) | targeting a plasma glucose level of 140–180 mg/dl (7.8–10 mmol/) | kdigo-2026 | p25 | p25/practice-point/3 | Practice Point |
| pediatric-protein-minimum | children-aki-akd-crrt | >=2.5 g/kg/day | a minimum daily protein intake of 2.5 grams/kg should be maintained for children receiving CRRT | kdigo-2026 | p27 | p27/practice-point/9 | Practice Point |
| theophylline-administration | neonates | single dose | a single dose of theophylline be given to neonates with severe perinatal asphyxia | kdigo-2026 | p28 | p28/recommendation/3.12.4.1 | 1A |
| furosemide-assessment-dose | adults-aki-volume-overload | 1.0 mg/kg IV bolus; 1.5 mg/kg if previously on diuretics | Furosemide 1.0 mg/kg (i.v. bolus). Use 1.5mg/kg if patient was previously on diuretics. | kdigo-2026 | p166 | p166/narrative/furosemide-assessment-dose | narrative |
| furosemide-response-goal | adults-aki-volume-overload | >200 ml urine within 2 hours | Goal: >200 ml urine output within 2 hours. | kdigo-2026 | p166 | p166/narrative/furosemide-response-goal | narrative |
| furosemide-escalation | adults-aki-volume-overload | double dose every 6-12 hours; 160-200 mg IV bolus example; maximum bolus 200 mg | double the dose (e.g., 160–200 mg i.v. bolus) every 6–12 hours. Maximize bolus dose before switching to infusion. Max bolus: 200 mg. | kdigo-2026 | p166 | p166/narrative/furosemide-escalation | narrative |
| thiazide-synergism | adults-aki-volume-overload | metolazone 5-10 mg PO or chlorothiazide 500 mg IV, 30-60 minutes before loop diuretic | metolazone 5–10 mg p.o. or chlorothiazide 500 mg i.v.). Administer 30–60 minutes before the loop diuretic | kdigo-2026 | p166 | p166/narrative/thiazide-synergism | narrative |
| furosemide-infusion | adults-aki-volume-overload | start 5-10 mg/hour; titrate to 20 mg/hour | Start at 5-10mg/hr. Titrate up to 20 mg/hr | kdigo-2026 | p166 | p166/narrative/furosemide-infusion | narrative |
| amino-acid-prophylaxis | adults-cardiac-surgery-no-advanced-ckd | 2 g/kg ideal body weight/day from operating-room admission for up to 3 days | balanced amino acids at a dose of 2 g/kg ideal body weight/day or placebo starting at operating room admission for up to 3 days | kdigo-2026 | p171 | p171/narrative/amino-acid-prophylaxis | narrative |
| remote-ischemic-preconditioning | cardiac-surgery-high-risk-no-propofol | 3 cycles; cuff pressure >200 mm Hg; 5 minutes ischemia and reperfusion | RENDERED: 3 cycles of limb ischemia and reperfusion (i.e., cuff pressure >200 mm Hg for 5 minutes) | kdigo-2026 | p174 | p174/narrative/remote-ischemic-preconditioning | narrative |
| terlipressin-infusion | adults-hrs-aki | start 2 mg/24 hours; if SCr does not decrease >25% after 48 hours increase every 24-48 hours to 12 mg/24 hours; stop day 4 if no response; maximum 14 days | RENDERED: Start at 2 mg/24h. If SCr does not decrease by >25% after 48h, increase every 24–48h up to a maximum of 12 mg/24h. Continue until SCr returns to baseline (<1.5 mg/dl) or for a maximum of 14 days; discontinue if no response by Day 4. | kdigo-2026 | p179 | p179/narrative/terlipressin-infusion | narrative |
| terlipressin-bolus | adults-hrs-aki | 0.5-1 mg every 4-6 hours; increase to 2 mg every 4-6 hours if SCr does not decrease | 0.5–1 mg every 4–6 hours. Increased to 2 mg every 4–6 hours if SCr does not decrease significantly. | kdigo-2026 | p179 | p179/narrative/terlipressin-bolus | narrative |
| norepinephrine-hrs | adults-hrs-aki | 0.5-3.0 mg/hour; target MAP increase >=10 mm Hg or MAP >65-70 mm Hg; maximum 14 days | 0.5–3.0 mg/h titrated to achieve an increase in MAP of at least 10 mm Hg or to achieve a MAP >65–70 mm Hg. Until reversal of hepatorenal syndrome or for a maximum of 14 days. | kdigo-2026 | p179 | p179/narrative/norepinephrine-hrs | narrative |
| midodrine-hrs | adults-hrs-aki | 7.5-15 mg every 8 hours | 7.5–15 mg every 8 hours | kdigo-2026 | p179 | p179/narrative/midodrine-hrs | narrative |
| octreotide-hrs | adults-hrs-aki | 100-200 mcg every 8 hours | 100-200 mcg every 8 hrs | kdigo-2026 | p179 | p179/narrative/octreotide-hrs | narrative |
| tumor-lysis-urine-flow | tumor-lysis-risk | adult urine flow >=100 ml/hour | goal of increasing urine flow to at least 100 ml/hour in adults | kdigo-2026 | p183 | p183/narrative/tumor-lysis-urine-flow | narrative |
| crrt-drug-removal-supplement | people-crrt | supplemental dosing if >30%-40% removed after hemodialysis | Administering supplement doses for drugs with >30%–40% post-hemodialysis removal is suggested. | kdigo-2026 | p32 | p32/narrative/crrt-drug-removal-supplement | narrative |
| crrt-loading-dose | people-crrt | loading dose 25% more than usual may be required | This may require a loading dose in the range of 25% more than usual. | kdigo-2026 | p32 | p32/narrative/crrt-loading-dose | narrative |
| residual-urine-clearance | people-crrt | add residual clearance if urine output >20 ml/hour or 500 ml/day | People with significant urine output (e.g., >20 ml/hr or 500 ml/day), should have clearance from the residual urine volume added to RRT clearance calculations | kdigo-2026 | p32 | p32/narrative/residual-urine-clearance | narrative |
| ca-aki-risk-egfr | adults-high-risk-ca-aki-broad | AKI or eGFR <30; or eGFR 30-44 ml/min per 1.73 m2 with multiple risk factors | defined risk factors for CA-AKI following intravenous contrast as eGFR<30 ml/min per 1.73 m2 or AKI, or eGFR 30–44 ml/min per 1.73 m2 with multiple risk factors | kdigo-2026 | p235 | p235/narrative/ca-aki-risk-egfr | narrative |
| max-allowable-contrast | adults-high-risk-ca-aki-broad | maximum allowable contrast dose = 3 times eGFR in ml/min per 1.73 m² | RENDERED: maximum allowable contrast dose (MACD) = 3 × eGFR in ml/min per 1.73 m² | kdigo-2026 | p239 | p239/narrative/max-allowable-contrast | narrative |
| contrast-crcl-ratio | adults-high-risk-ca-aki-broad | contrast volume/CrCl >3.7 increases CA-AKI risk | CV/CrCl of >3.7 | kdigo-2026 | p239 | p239/narrative/contrast-crcl-ratio | narrative |
| lvedp-hydration | adults-high-risk-ca-aki | 0.9% saline 3 ml/kg for 1 hour before; then 5 ml/kg/hour if LVEDP <13, 3 if 13-18, 1.5 if >18 for 4 hours after | RENDERED: 0.9% sodium chloride i.v. bolus infusion at 3 ml/kg for 1 h before the procedure, then rate adjusted according to LVEDP: 5 ml/kg/h for LVEDP <13 mm Hg, 3 ml/kg/h for LVEDP 13–18 mm Hg, and 1.5 ml/kg/h for LVEDP >18 mm Hg for 4 h after procedure | kdigo-2026 | p241 | p241/narrative/lvedp-hydration | narrative |
| cvp-hydration | adults-high-risk-ca-aki | 3 ml/kg/hour if CVP <6, 1.5 if 6-12, 1 if >12 for 6 hours before and 12 hours after | 3 ml/kg/h for CVP <6 cm H2O, 1.5 ml/kg/h for CVP 6–12 cm H2O), and 1 ml/kg/h for CVP >12 cm H2O for 6 hours pre-procedure and 12 hours post-procedure | kdigo-2026 | p241 | p241/narrative/cvp-hydration | narrative |
| biva-hydration | adults-high-risk-ca-aki | 0.9% saline 2 ml/kg/hour for 12 hours before and after if BIVA <315 Ohm/m male or <380 female; halve if EF <40% | RENDERED: 0.9% sodium chloride at 2 ml/kg/h for 12 h before and after the procedure for people with a low BIVA level (<315 Ohm/m for males, <380 Ohm/m for females); the infusion rate was halved for people with an ejection fraction <40%. | kdigo-2026 | p241 | p241/narrative/biva-hydration | narrative |
| forced-diuresis-hydration | adults-high-risk-ca-aki | saline 250 ml over 30 minutes, furosemide 0.5 mg/kg; defer contrast until urine >300 ml/hour; start 200 ml/hour and match every 5 minutes through 4 hours after | RENDERED: 0.9% sodium chloride i.v. bolus of 250 ml over 30 min followed by an i.v. furosemide bolus of 0.5 mg/kg preprocedure. Injection of contrast media deferred until urine flow rate >300 ml/h. Matched hydration during and up to 4 hours post-procedure achieved by initial i.v. infusion 200 ml/h, followed by adjustment of infusion rate to match urine output after every 5 min. | kdigo-2026 | p241 | p241/narrative/forced-diuresis-hydration | narrative |
| contrast-nephrotoxin-hold | adults-high-risk-ca-aki-broad | if AKI or eGFR <30: hold 24-48 hours before and 48 hours after contrast | RENDERED: Withdrawal of nonessential potentially nephrotoxic medications in people with AKI or eGFR <30 ml/min per 1.73 m2 for 24–48 hours before and 48 hours after radiocontrast exposure | kdigo-2026 | p247 | p247/narrative/contrast-nephrotoxin-hold | narrative |
| contrast-metformin-hold | adults-high-risk-ca-aki-broad | if no AKI and eGFR >30 continue; if AKI or eGFR <=30 stop and restart no sooner than 48 hours if GFR stable | RENDERED: In people with eGFR >30 ml/min per 1.73 m2 and without evidence of AKI, metformin need not be stopped. For people with AKI or an eGFR ≤30 ml/min per 1.73 m2, stop metformin and do not restart for at least 48 hours and only then if GFR remains stable. | kdigo-2026 | p247 | p247/narrative/contrast-metformin-hold | narrative |
| sick-day-weight-trigger | adults-sick-day-guidance | weight decrease 3 kg in 2 days | Decreased weight (3 kg in 2 days) | kdigo-2026 | p257 | p257/narrative/sick-day-weight-trigger | narrative |
| sick-day-medication-hold | adults-sick-day-guidance | until symptoms resolve or up to 3 days, whichever first | Medications that should be temporarily stopped (until symptoms are resolved or up to 3 days, whichever is earliest) | kdigo-2026 | p257 | p257/narrative/sick-day-medication-hold | narrative |
| sick-day-insulin-increase | adults-sick-day-guidance | if glucose elevated, increase basal and bolus insulin 10%-20% | empirical 10%–20% increase in basal and bolus insulin doses | kdigo-2026 | p257 | p257/narrative/sick-day-insulin-increase | narrative |
| sick-day-support-trigger | adults-sick-day-guidance | seek help if symptoms persist 72 hours or glucose remains high after 24 hours adjustment | RENDERED: Seek healthcare-professional support if signs and symptoms have not resolved within 72 hours or a significant increase in blood glucose is not coming down with self-adjustment after 24 hours. | kdigo-2026 | p257 | p257/narrative/sick-day-support-trigger | narrative |
| rrt-hyperkalemia-indication | adults-rrt-deferred | K >=6.0 mmol/l, rapidly rising, or cardiac toxicity refractory to therapy | Severe hyperkalemia (K+ ≥6.0 mmol/l, rapidly rising, or cardiac toxicity) refractory to medical therapy | kdigo-2026 | p263 | p263/narrative/rrt-hyperkalemia-indication | narrative |
| rrt-acidemia-indication | adults-rrt-deferred | pH <=7.2 or bicarbonate <=12 mmol/l refractory to therapy | Severe acidemia or metabolic acidosis (pH ≤7.2 or serum bicarbonate ≤12 mmol/l despite normal or low arterial pCO2) refractory to medical therapy | kdigo-2026 | p263 | p263/narrative/rrt-acidemia-indication | narrative |
| rrt-hepatic-encephalopathy | adults-rrt-deferred | grade >=2: consider CRRT for hyperammonemia | hepatic encephalopathy (grade ≥2) due to acute or acute-on-chronic liver failure, initiation of continuous RRT | kdigo-2026 | p38 | p38/practice-point/4 | Practice Point |
| adult-crrt-effluent | adults-crrt | 20-25 ml/kg/hour | effluent volume of 20-25 ml/kg/h | kdigo-2026 | p39 | p39/recommendation/5.3.1 | 1B |
| adult-irrt-ktv | adults-irrt-pirrt-aki | Kt/V 3.9 per week | a Kt/V of 3.9 per week | kdigo-2026 | p39 | p39/recommendation/5.3.1 | 1B |
| adult-high-bmi | adults-crrt | BMI >=30 kg/m2: use ideal or adjusted rather than actual body weight | high body mass index (BMI; e.g., ≥30 kg/m2) based on ideal or adjusted body weight, rather than actual body weight | kdigo-2026 | p39 | p39/practice-point/5 | Practice Point |
| adult-pd-dose | adults-acute-pd-aki | weekly Kt/V 2.2 using 18-24 l PD fluid/day | deliver a weekly Kt/V of 2.2 (18-24 l PD fluid/day) | kdigo-2026 | p39 | p39/practice-point/7 | Practice Point |
| irrt-albumin | adults-starting-irrt | albumin 25% 100 ml IV over 15-20 minutes before IRRT if hypoalbuminemic | Give albumin 25% 100 ml i.v. over 15–20 minutes prior to planned initiation of IRRT | kdigo-2026 | p276 | p276/narrative/irrt-albumin | narrative |
| irrt-midodrine | adults-starting-irrt | 2.5-10 mg PO 30 minutes before or during IRRT | Give a single dose of midodrine 2.5–10 mg po 30 minutes prior to or during planned initiation of IRRT. | kdigo-2026 | p276 | p276/narrative/irrt-midodrine | narrative |
| irrt-blood-flow | adults-starting-irrt | start about 100 ml/min; increase every 2-5 minutes by 50-100 ml/min | Initiate IRRT at a lower blood flow rate (QB ~ 100 ml/min) and increase every 2–5 min by increments of 50–100 ml/min | kdigo-2026 | p276 | p276/narrative/irrt-blood-flow | narrative |
| irrt-dialysate-temperature | adults-starting-irrt | <37.0 C and/or <0.5 C below body temperature | initial dialysate temperature <37.0oC and/or <0.5oC below measured body temperature | kdigo-2026 | p276 | p276/narrative/irrt-dialysate-temperature | narrative |
| irrt-sodium | adults-starting-irrt | dialysate sodium >=145 mmol/l | higher dialysate [Na] (≥145 mmol/l) | kdigo-2026 | p276 | p276/narrative/irrt-sodium | narrative |
| rrt-catheter-size | children-rrt | <5 kg: 4.5-6 Fr; 5-15 kg: 7-8 Fr; 15-30 kg: 8-10 Fr; >30 kg: 10-12 Fr | RENDERED: Patient weight <5 kg: catheter size 4.5–6 French; 5–15 kg: 7–8 French; 15–30 kg: 8–10 French; >30 kg: 10–12 French. | kdigo-2026 | p288 | p288/narrative/pediatric-catheter-size | narrative |
| citrate-anticoagulation | people-crrt | citrate 3-4 mmol/l blood flow; postfilter calcium 0.25-0.5 mmol/l | Citrate 3–4 mmol/l blood flow; Ca 0.25–0.5 mmol/l postfilter | kdigo-2026 | p298 | p298/narrative/citrate-anticoagulation | narrative |
| heparin-anticoagulation | people-crrt | bolus 500-1000 IU then 5-10 IU/kg/hour | RENDERED: Bolus 500–1000 IU then infusion 5–10 IU/kg/h | kdigo-2026 | p298 | p298/narrative/heparin-anticoagulation | narrative |
| lmwh-anticoagulation | people-crrt | 40-60 IU/kg SC or 1 mg/kg IV bolus predialysis | 40–60 IU/kg SC or 1 mg/kg i.v. bolus predialysis | kdigo-2026 | p298 | p298/narrative/lmwh-anticoagulation | narrative |
| nafamostat-anticoagulation | people-crrt | 0.2-0.5 mg/kg/hour continuous infusion | 0.2–0.5 mg/kg/h continuous infusion | kdigo-2026 | p298 | p298/narrative/nafamostat-anticoagulation | narrative |
| argatroban-anticoagulation | people-crrt | start 0.5-1 µg/kg/min IV and titrate to aPTT | RENDERED: Starting 0.5–1 µg/kg/min i.v., titrate to aPTT target | kdigo-2026 | p298 | p298/narrative/argatroban-anticoagulation | narrative |
| bivalirudin-anticoagulation | people-crrt | start 0.03-0.1 mg/kg/hour and adjust for kidney function | Starting 0.03–0.1 mg/kg/h, adjust for kidney function | kdigo-2026 | p298 | p298/narrative/bivalirudin-anticoagulation | narrative |
| epoprostenol-anticoagulation | people-crrt | 4-10 ng/kg/min IV infusion | 4–10 ng/kg/min i.v. infusion | kdigo-2026 | p299 | p299/narrative/epoprostenol-anticoagulation | narrative |
| ultrafiltration-review | adults-crrt | review every 12-24 hours or more frequently | regular review of the ultrafiltration prescription every 12–24 hours (or more frequently) | kdigo-2026 | p313 | p313/narrative/ultrafiltration-review | narrative |
| adult-rrt-urine-output | adults-rrt-discontinuation | >450 ml/24 hours without diuretics or >2300 ml/24 hours with diuretics | Urine output >450 ml/24 hours without exposure to diuretics or >2300 ml/24 hours with exposure to diuretics | kdigo-2026 | p42 | p42/practice-point/7 | Practice Point |
| adult-rrt-creatinine-clearance | adults-rrt-discontinuation | 2-hour creatinine clearance >=23 ml/min | 2-hour timed creatinine clearance ≥23 ml/min | kdigo-2026 | p42 | p42/practice-point/7 | Practice Point |
| pediatric-rrt-initiation | critically-ill-children-severe-aki | consider within 2 days of ICU admission or AKI onset | RRT initiation within 2 days of intensive care unit (ICU) admission or AKI onset should be considered | kdigo-2026 | p43 | p43/practice-point/6 | Practice Point |
| pediatric-crrt-effluent | children-crrt | initial 25-30 ml/kg/hour | initial CRRT effluent volume for children can be 25–30 ml/kg/h | kdigo-2026 | p44 | p44/practice-point/2 | Practice Point |
| pediatric-pd-prescription | children-acute-pd | fill 10-20 ml/kg; cycles 60-90 minutes; continuous 24 hours for first 1-3 days | RENDERED: In children with AKI, PD can be initiated with a fill volume of 10–20 ml/kg and short cycle times (60–90 minutes), with continuous therapy over 24 hours for the first 1–3 days. | kdigo-2026 | p44 | p44/practice-point/4 | Practice Point |
| pediatric-hyperammonemia-crrt | children-hyperammonemia | CRRT up to 200 ml/kg/hour | CRRT dose-intensity up to 200 ml/kg/h may be acceptable | kdigo-2026 | p44 | p44/practice-point/5 | Practice Point |
| pediatric-hyperammonemia-start | children-hyperammonemia | ammonia >400-500 µmol/l not responsive after 4 hours aggressive therapy | RENDERED: CRRT (CVVHDF) has been recommended for children with serum ammonia >400–500 µmol/l and not responsive after 4 hours of aggressive medical therapy. | kdigo-2026 | p329 | p329/narrative/pediatric-hyperammonemia-start | narrative |
| pediatric-ufnet | children-crrt | <=2.5 ml/kg/hour | net ultrafiltration (UFNET) should not exceed 2.5 ml/kg/h | kdigo-2026 | p45 | p45/practice-point/1 | Practice Point |
| pediatric-fluid-review | children-crrt | every 4-6 hours | Frequent assessment of fluid balance (i.e., every 4-6 hours) | kdigo-2026 | p45 | p45/practice-point/1 | Practice Point |
| pediatric-rrt-urine-output | children-rrt-discontinuation | >0.5 ml/kg/hour over 6 hours | Urine output exceeding >0.5 ml/kg/h over 6 hours | kdigo-2026 | p45 | p45/practice-point/2 | Practice Point |
| medication-resumption-review | adults-post-aki-medications | at discharge and by 3 months | at hospital discharge and by 3 months after AKI/AKD | kdigo-2026 | p46 | p46/practice-point/6 | Practice Point |
| post-aki-kidney-assessment | children-adults-after-aki-akd | 3 months after AKI or AKD | Assess kidney function and markers of kidney damage 3 months after AKI or AKD | kdigo-2026 | p47 | p47/practice-point/2 | Practice Point |
| post-dialysis-nephrology-assessment | adults-after-outpatient-dialysis | within 7 days and again at 90 days | comprehensive assessment within 7 days, followed by an additional evaluation of kidney function at 90 days | kdigo-2026 | p47 | p47/practice-point/8 | Practice Point |
| pediatric-low-risk-follow-up | pediatric-low-risk-survivors | 1-3 months | Low 1–3 months | kdigo-2026 | p362 | p362/narrative/pediatric-low-risk-follow-up | narrative |
| pediatric-high-risk-follow-up | pediatric-high-risk-survivors | 1, 3, and 12 months | High 1, 3, and 12 months | kdigo-2026 | p362 | p362/narrative/pediatric-high-risk-follow-up | narrative |
| pediatric-high-risk-definition | pediatric-high-risk-survivors | Stage 2-3 or duration >48 hours; proteinuria/residual elevation; infants born <28 weeks | High: Stage 2–3 or AKI >48h, proteinuria or residual elevation in creatinine or cystatin C discharge, infants born <28 weeks | kdigo-2026 | p363 | p363/narrative/pediatric-high-risk-definition | narrative |
| pediatric-kidney-health-check | pediatric-high-risk-survivors | at discharge and one year after AKI | kidney health assessments at hospital discharge and one year following an AKI episode | kdigo-2026 | p48 | p48/practice-point/3 | Practice Point |
| aki-damage-biomarker-stage | children-adults | B0 = negative; B1 = positive | RENDERED: B0 indicates absence and B1 indicates presence of an elevated damage biomarker; B0 Negative; B1 Positive. | kdigo-2026 | p17 | p17/narrative/aki-damage-biomarker-stage | narrative |
| epidemiology-baseline-scr-window | adults-suspected-confirmed-aki | median outpatient SCr 7-365 days before admission or acute event | RENDERED: For the purpose of epidemiological research, use the median of outpatient values 7–365 days prior to admission or an acute event is advised. | kdigo-2026 | p63 | p63/narrative/epidemiology-baseline-scr-window | narrative |
| isn-0by25-risk-score-components | community-adults-aki-risk | kidney disease 1; oliguria 4; infection with fever 1; hypotension or shock 2; pregnancy with hypertension/seizures 2; whole-body swelling 2; loss of appetite 1; HIV on HAART 1; coma/confusion 2; anemia/pallor 1; maximum 17; moderate-to-high risk >=3 | RENDERED: History of kidney disease 1; Presence of oliguria 4; Infection with fever 1; Hypotension or shock 2; Pregnancy with hypertension/seizures 2; Whole body swelling 2; Loss of appetite 1; HIV on HAART 1; Coma/confusion 2; Anemia/pallor 1; Max total 17; moderate-to-high risk score ≥3. | kdigo-2026 | p89 | p89/narrative/isn-0by25-risk-score-components | narrative |
| pediatric-rai-application-window | critically-ill-children-aki-risk | apply within first 12-24 hours of admission or onset of critical illness | The RAI is most effectively applied early during hospitalization, particularly within the first 12–24 hours of admission or onset of critical illness. | kdigo-2026 | p130 | p130/narrative/pediatric-rai-application-window | narrative |
| adult-protein-intake-comparison | adults-aki-akd | avoid excessive intake represented in the cited trial by >=2.2 g/kg/day versus usual <=1.2 g/kg/day | A large, pragmatic RCT compared the impact of high protein intake (≥2.2 g/kg/day) versus usual protein intake (≤1.2 g/kg/day) in critically ill adults on mechanical ventilation. | kdigo-2026 | p190 | p190/narrative/adult-protein-intake-comparison | narrative |
| gentamicin-trough | children-adults | target trough concentration <2 mg/l | target trough concentrations (Cmin) <2 mg/l for gentamicin | kdigo-2026 | p213 | p213/narrative/gentamicin-trough | narrative |
| amikacin-trough | children-adults | target trough concentration <10 mg/l | Cmin <10 mg/l for amikacin may reduce the risk of nephrotoxicity | kdigo-2026 | p213 | p213/narrative/amikacin-trough | narrative |
| methotrexate-glucarpidase-window | children-adults | glucarpidase <60 hours after methotrexate | glucarbidase (<60 h after methotrexate) | kdigo-2026 | p220 | p220/narrative/methotrexate-glucarpidase-window | narrative |
| perioperative-rasi-hold | adults-major-surgery-rasi-withholding | when withholding is selected, generally withhold 24 hours before surgery | Timing is also critical; RASi are generally withheld 24 hours prior to surgery | kdigo-2026 | p253 | p253/narrative/perioperative-rasi-hold | narrative |
| post-sick-day-medication-review | adults-sick-day-guidance | medication review within a month | RENDERED: Patients may additionally benefit from medication review within a month to ensure appropriate medications are restarted at the correct dose. | kdigo-2026 | p258 | p258/narrative/post-sick-day-medication-review | narrative |
| neonatal-urine-ngal-ruleout | newborns-nephrotoxin-exposed | urine NGAL <=250 ng/ml had negative predictive value 96.8%; ideal threshold requires further validation | RENDERED: The negative predictive value of a urine NGAL value ≤250 ng/ml was 96.8%; however, more research is needed and the ideal urine NGAL thresholds require further validation. | kdigo-2026 | p258 | p258/narrative/neonatal-urine-ngal-ruleout | narrative |
| neonatal-urine-ngal-rulein | newborns-nephrotoxin-exposed | urine NGAL >=400 ng/ml had positive likelihood ratio 2.76; ideal threshold requires further validation | RENDERED: urine NGAL ≥400 ng/ml demonstrated a positive likelihood ratio of 2.76; however, more research is needed and the ideal urine NGAL thresholds require further validation. | kdigo-2026 | p258 | p258/narrative/neonatal-urine-ngal-rulein | narrative |
| adult-rrt-modality-parameters | adults-critically-ill-rrt | IHD QB 300-500 ml/min, UFNET 0-15 ml/kg/h, QD 300-500 ml/min, clearance 200-350 ml/min; SLED QB 100-300, UFNET 0-8, QD 100-300, QR 0, clearance 80-90; SCUF QB 100-200, UFNET 0-8, clearance 1-5; CVVH QB 80-200, UFNET 0-3, QR 250-4000 ml/h, clearance 25-33; CVVHD QB 80-200, UFNET 0-3, QD 250-2000 ml/h, QR 0, clearance 25-33; CVVHDF QB 80-200, UFNET 0-3, QD 250-2000 ml/h, QR 250-4000 ml/h, clearance 25-33; PD QD 1-2 l/exchange, QR 0, clearance 15-25 | RENDERED: Table 43: IHD QB 300–500 ml/min, UFNET 0–15 ml/kg/h, QD 300–500 ml/min, CLUrea 200–350 ml/min; SLED QB 100–300, UFNET 0–8, QD 100–300, QR 0, CLUrea 80–90; SCUF QB 100–200, UFNET 0–8, CLUrea 1–5; CVVH QB 80-200, UFNET 0–3, QR 250–4000 ml/h, CLUrea 25–33; CVVHD QB 80-200, UFNET 0–3, QD 250–2000 ml/h, QR 0, CLUrea 25–33; CVVHDF QB 80-200, UFNET 0–3, QD 250–2000 ml/h, QR 250–4000 ml/h, CLUrea 25–33; PD QD 1–2 l per exchange, QR 0, CLUrea 15-25. | kdigo-2026 | p272 | p272/narrative/adult-rrt-modality-parameters | narrative |
| irrt-dialysate-flow | adults-starting-irrt | start QD 300 ml/min and titrate to target | Initiate IRRT at a lower dialysate flow rate (QD 300 ml/min) and titrate to target. | kdigo-2026 | p276 | p276/narrative/irrt-dialysate-flow | narrative |
| irrt-initial-ultrafiltration | adults-starting-irrt | start with zero ultrafiltration and titrate to target | Initiate IRRT with zero ultrafiltration and titrate to target. | kdigo-2026 | p276 | p276/narrative/irrt-initial-ultrafiltration | narrative |
| adult-rrt-catheter-size | adults-critically-ill-rrt | catheter at least 12 French | catheters of at least 12 French (F) in size are recommended | kdigo-2026 | p287 | p287/narrative/adult-rrt-catheter-size | narrative |
| adult-rrt-catheter-flow | adults-critically-ill-rrt | blood flow ideally >=200-250 ml/min | allow sufficient blood flow rates (ideally ≥200–250 ml/min) | kdigo-2026 | p287 | p287/narrative/adult-rrt-catheter-flow | narrative |
| right-ij-catheter-length-formula | adults-critically-ill-rrt | height/10 cm; reported accuracy 90% | RENDERED: Right internal jugular: Height/10 cm; Accuracy 90%. | kdigo-2026 | p288 | p288/narrative/right-ij-catheter-length-formula | narrative |
| left-ij-catheter-length-formula | adults-critically-ill-rrt | height/10 + 4 cm; reported accuracy 94% | RENDERED: Left internal jugular: Height/10+4 cm; Accuracy 94%. | kdigo-2026 | p288 | p288/narrative/left-ij-catheter-length-formula | narrative |
| right-subclavian-catheter-length-formula | adults-critically-ill-rrt | height/10 - 2 cm; reported accuracy 96% | RENDERED: Right subclavian: Height/10-2 cm; Accuracy 96%. | kdigo-2026 | p288 | p288/narrative/right-subclavian-catheter-length-formula | narrative |
| left-subclavian-catheter-length-formula | adults-critically-ill-rrt | height/10 + 2 cm; reported accuracy 97% | RENDERED: Left subclavian: Height/10+2 cm; Accuracy 97%. | kdigo-2026 | p288 | p288/narrative/left-subclavian-catheter-length-formula | narrative |
| irrt-dialysate-bacteria-limit | adults-irrt-pirrt-aki | dialysate <200 CFU/ml bacteria | dialysate used in hemodialysis contains <200 colony-forming units (CFU)/ml of bacteria | kdigo-2026 | p310 | p310/narrative/irrt-dialysate-bacteria-limit | narrative |
| irrt-dialysate-endotoxin-limit | adults-irrt-pirrt-aki | dialysate <2 EU/ml endotoxin | RENDERED: dialysate used in hemodialysis contains <2 endotoxin units (EU)/ml | kdigo-2026 | p310 | p310/narrative/irrt-dialysate-endotoxin-limit | narrative |
| ultrapure-dialysate-bacteria-target | adults-irrt-pirrt-aki | target <100 CFU/ml bacteria | target values of <100 CFU/ml | kdigo-2026 | p310 | p310/narrative/ultrapure-dialysate-bacteria-target | narrative |
| ultrapure-dialysate-endotoxin-target | adults-irrt-pirrt-aki | target <0.25 EU/ml endotoxin | RENDERED: target values of <0.25 EU/ml for ultrapure dialysate | kdigo-2026 | p310 | p310/narrative/ultrapure-dialysate-endotoxin-target | narrative |
| crrt-solution-reassessment | people-crrt | reassess every 6-12 hours | Frequent reassessment, ideally every 6 to 12 hours, is essential | kdigo-2026 | p312 | p312/narrative/crrt-solution-reassessment | narrative |
| scheduled-ihd-stop-urine-no-diuretic | adults-rrt-discontinuation | continue scheduled IHD 3 times/week until urine output >1 l/day without diuretics | RENDERED: continuing scheduled IHD session 3 times per week until specific urine output (>1 l/d in the absence of diuretics) criteria were met | kdigo-2026 | p315 | p315/narrative/scheduled-ihd-stop-urine-no-diuretic | narrative |
| scheduled-ihd-stop-urine-diuretic | adults-rrt-discontinuation | continue scheduled IHD 3 times/week until urine output >2 l/day with diuretics | RENDERED: continuing scheduled IHD session 3 times per week until specific urine output (>2 l/d with diuretics) criteria were met | kdigo-2026 | p315 | p315/narrative/scheduled-ihd-stop-urine-diuretic | narrative |
| scheduled-ihd-stop-creatinine-clearance | adults-rrt-discontinuation | continue scheduled IHD 3 times/week until creatinine clearance >20 ml/min | RENDERED: continuing scheduled IHD session 3 times per week until creatinine clearance (>20 ml/min) criteria were met | kdigo-2026 | p315 | p315/narrative/scheduled-ihd-stop-creatinine-clearance | narrative |
| crrt-liberation-score-urine | adults-crrt-liberation | urine output >=300 ml/24 hours favored successful discontinuation | Factors associated with successful CRRT discontinuation were greater urine output (≥300 ml/24h) | kdigo-2026 | p316 | p316/narrative/crrt-liberation-score-urine | narrative |
| crrt-liberation-score-map | adults-crrt-liberation | MAP 50-78 mm Hg favored successful discontinuation | RENDERED: Factors associated with successful CRRT discontinuation were MAP (50–78 mm Hg) | kdigo-2026 | p316 | p316/narrative/crrt-liberation-score-map | narrative |
| crrt-liberation-score-potassium | adults-crrt-liberation | serum potassium <4.1 mmol/l favored successful discontinuation | RENDERED: Factors associated with successful CRRT discontinuation were serum potassium <4.1 mmol/l | kdigo-2026 | p316 | p316/narrative/crrt-liberation-score-potassium | narrative |
| crrt-liberation-score-bun | adults-crrt-liberation | BUN <35 mg/dl or serum urea <12.5 mmol/l favored successful discontinuation | RENDERED: Factors associated with successful CRRT discontinuation were BUN <35 mg/dl (serum urea <12.5 mmol/l). | kdigo-2026 | p316 | p316/narrative/crrt-liberation-score-bun | narrative |
| liberate-ihd-bun-indication | adults-rrt-discontinuation | give IHD when BUN >=112 mg/dl or serum urea >=40 mmol/l | participants received IHD only when one of the following indications were met: BUN ≥112 mg/dl (serum urea ≥40 mmol/l) | kdigo-2026 | p316 | p316/narrative/liberate-ihd-bun-indication | narrative |
| liberate-ihd-potassium-indication | adults-rrt-discontinuation | give IHD for potassium >=6 mmol/l or >5.5 despite treatment | hyperkalemia ≥6 mmol/l (>5.5 mmol/l if despite medical treatment) | kdigo-2026 | p316 | p316/narrative/liberate-ihd-potassium-indication | narrative |
| liberate-ihd-acidemia-indication | adults-rrt-discontinuation | give IHD for arterial pH <7.15 from metabolic acidosis or bicarbonate <12 mEq/l | arterial pH <7.15 from metabolic acidosis (or bicarbonate level <12 mEq/l) | kdigo-2026 | p316 | p316/narrative/liberate-ihd-acidemia-indication | narrative |
| crrt-stop-low-urine | adults-crrt-liberation | urine output <0.5 ml/kg/hour over 6 hours after stopping CRRT lowers likelihood of successful liberation | urine output <0.5 ml/kg/h over 6 hours after CRRT was stopped was associated with lower likelihood of successful liberation | kdigo-2026 | p317 | p317/narrative/crrt-stop-low-urine | narrative |
| crrt-stop-minimum-urine | adults-crrt-liberation | urine output 178 ml/6 hours was the minimum threshold predicting success | urine output of 178 ml/6 hours appears to be the minimum threshold to predict success | kdigo-2026 | p317 | p317/narrative/crrt-stop-minimum-urine | narrative |
| crrt-stop-hourly-urine | adults-crrt-liberation | urine output >30 ml/hour at discontinuation predicted success | greater urine output (>30 ml/h) at the time of discontinuation was the best predictor of success | kdigo-2026 | p317 | p317/narrative/crrt-stop-hourly-urine | narrative |
| pediatric-rrt-modality-parameters | critically-ill-children-rrt | IHD QB 5-8 ml/kg/min, UFNET 0-2.5 ml/kg/h, QD individualized and sometimes QD/QB >2:1; SCUF QB 3-5 and UFNET 0-2.5; CVVH QB 3-5, UFNET 0-2.5, QR 20-30 ml/kg/h; CVVHD QB 3-5, UFNET 0-2.5, QD 20-30, QR 0; CVVHDF QB 3-5, UFNET 0-2.5, QD 20-30, QR 20-30; PD QD 8-20 ml/kg or 800-1100 ml/m2 per exchange and QR 0 | RENDERED: Table 56: IHD QB 5–8 ml/kg/min, UFNET 0–2.5 ml/kg/h, QD individualized sometimes exceeding QD/QB >2:1 to maximize urea clearance; SCUF QB 3–5, UFNET 0–2.5; CVVH QB 3–5, UFNET 0–2.5, QR 20–30 ml/kg/h; CVVHD QB 3–5, UFNET 0–2.5, QD 20–30, QR 0; CVVHDF QB 3–5, UFNET 0–2.5, QD 20–30, QR 20–30; PD QD 8–20 ml/kg or 800–1100 ml/m2 per exchange, QR 0. | kdigo-2026 | p327 | p327/narrative/pediatric-rrt-modality-parameters | narrative |
| vlbw-pd-fill | very-low-birth-weight-infants-pd | lower fill volume 7-14 ml may be necessary | RENDERED: in extreme and very-low birth weight infants, lower fill volumes (7–14 ml) may be necessary | kdigo-2026 | p328 | p328/narrative/vlbw-pd-fill | narrative |
| vlbw-pd-dwell | very-low-birth-weight-infants-pd | shorter dwell time 10-20 minutes may be necessary | RENDERED: in extreme and very-low birth weight infants, shorter dwell times (10–20 minutes) may be necessary | kdigo-2026 | p328 | p328/narrative/vlbw-pd-dwell | narrative |
| pediatric-extracorporeal-circuit-volume | neonates-small-children-crrt | avoid oversized circuit volume that may exceed 8-10 ml/kg | extracorporeal circuit volume, which may exceed 8–10 ml/kg and increase the risk of hemodynamic instability, particularly in neonates and small children | kdigo-2026 | p330 | p330/narrative/pediatric-extracorporeal-circuit-volume | narrative |
| post-aki-mra-egfr | adults-post-aki-mra | consider cautious reinitiation when eGFR >25 ml/min per 1.73 m2 | cautious reinitiation of these medications after AKI in those with a clinical indication for treatment, no contraindications, stable kidney function, and an eGFR >25 ml/min per 1.73 m2 should be considered | kdigo-2026 | p350 | p350/narrative/post-aki-mra-egfr | narrative |
| outpatient-aki-dialysis-kidney-monitoring | adults-outpatient-dialysis-aki | assess kidney function at least weekly during the first month | Assessment of kidney function should occur at regular intervals, at least weekly during the first month. | kdigo-2026 | p357 | p357/narrative/outpatient-aki-dialysis-kidney-monitoring | narrative |
| pediatric-iga-proteinuria | children-iga-proteinuria | proteinuria >200 mg/day or UPCR >200 mg/g (>20 mg/mmol): receive RAS blockade | all children with IgA nephropathy and proteinuria >200 mg/d or UPCR >200 mg/g (>20 mg/mmol) should receive RAS blockade | kdigo-2026 | p364 | p364/narrative/pediatric-iga-proteinuria | narrative |
| early-post-aki-follow-up-window | children-adults-post-aki-akd-follow-up | within 3 months assess kidney, cardiovascular, physical, psychosocial, utilization, and quality-of-life domains | RENDERED: Table 57: Within 3 months, kidney health, cardiovascular health, physical function, psychosocial, healthcare utilization, and quality of life apply to children and adults. | kdigo-2026 | p335 | p335/narrative/early-post-aki-follow-up-window | narrative |
| later-post-aki-follow-up-window | children-adults-post-aki-akd-follow-up | at 3 months or beyond assess kidney health | RENDERED: Table 57: At 3 months or beyond, kidney health applies to children and adults. | kdigo-2026 | p335 | p335/narrative/later-post-aki-follow-up-window | narrative |
| later-post-aki-cardiovascular-follow-up | predominantly-adults-post-aki-akd-follow-up | at 3 months or beyond assess cardiovascular health | RENDERED: Table 57: At 3 months or beyond, cardiovascular follow-up applies predominantly to adults. | kdigo-2026 | p335 | p335/narrative/later-post-aki-cardiovascular-follow-up | narrative |
| later-post-aki-neurocognitive-follow-up | predominantly-children-post-aki-akd-follow-up | at 3 months or beyond assess neurocognitive function | RENDERED: Table 57: At 3 months or beyond, neurocognitive follow-up applies predominantly to children. | kdigo-2026 | p335 | p335/narrative/later-post-aki-neurocognitive-follow-up | narrative |
| later-post-aki-growth-nutrition-follow-up | children-post-aki-akd-follow-up | at 3 months or beyond assess growth and nutrition | RENDERED: Table 57: At 3 months or beyond, growth and nutrition follow-up applies to children. | kdigo-2026 | p335 | p335/narrative/later-post-aki-growth-nutrition-follow-up | narrative |

## Conflicts

No within-population, within-quantity conflict is represented. Method-specific quantities
separate diagnostic criteria, hydration protocols, RRT modalities, and drug regimens that
the source presents as distinct decisions rather than interchangeable cutoffs.

## Coverage

The source is `bound`: marker records delimit recommendation-shaped text but do not
prove a complete recommendation denominator. Every marker occurrence not discharged
by a recommendation-backed threshold row is listed below after the row set is finalized.


**Marker occurrence accounting.** The bound artifact contains 406 marker records under 406 distinct locators. 0 locators occur more than once; each repeated occurrence receives the same disposition as its locator below. Threshold rows cite 23 locators. The remaining 383 locators were read and contain no additional numeric patient-action decision point beyond rows already represented from source tables, figures, or narrative.

- `p15/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p15/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p15/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p15/recommendation/1.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p16/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p17/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p17/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p18/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p18/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p18/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p18/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p18/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p19/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p19/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p20/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p21/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p21/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p21/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p21/recommendation/2.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p21/recommendation/2.1.2` - no additional numeric patient-action decision point in this marker occurrence
- `p21/recommendation/2.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p21/recommendation/2.3.1` - no additional numeric patient-action decision point in this marker occurrence
- `p21/recommendation/2.3.2` - no additional numeric patient-action decision point in this marker occurrence
- `p22/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p22/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p22/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p22/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p22/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p22/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p22/recommendation/2.4.1` - no additional numeric patient-action decision point in this marker occurrence
- `p22/recommendation/2.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p23/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p23/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p23/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p23/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p23/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p23/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p23/recommendation/2.6.1` - no additional numeric patient-action decision point in this marker occurrence
- `p24/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p24/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p24/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p24/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p24/recommendation/3.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p24/recommendation/3.1.2` - no additional numeric patient-action decision point in this marker occurrence
- `p25/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p25/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p25/recommendation/3.2.2` - no additional numeric patient-action decision point in this marker occurrence
- `p25/recommendation/3.2.3` - no additional numeric patient-action decision point in this marker occurrence
- `p25/recommendation/3.3.1` - no additional numeric patient-action decision point in this marker occurrence
- `p25/recommendation/3.3.2` - no additional numeric patient-action decision point in this marker occurrence
- `p26/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p26/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p26/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p26/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p26/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p26/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p26/recommendation/3.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p26/recommendation/3.5.2` - no additional numeric patient-action decision point in this marker occurrence
- `p26/recommendation/3.6.1` - no additional numeric patient-action decision point in this marker occurrence
- `p26/recommendation/3.7.1` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/8` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/10` - no additional numeric patient-action decision point in this marker occurrence
- `p27/practice-point/11` - no additional numeric patient-action decision point in this marker occurrence
- `p28/recommendation/3.12.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p29/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p29/recommendation/4.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/8` - no additional numeric patient-action decision point in this marker occurrence
- `p30/practice-point/9` - no additional numeric patient-action decision point in this marker occurrence
- `p31/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p31/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p31/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p34/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p34/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p34/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p34/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p34/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p34/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p35/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p35/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p35/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p35/recommendation/4.9.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p36/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p36/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p36/recommendation/4.9.3.1` - no additional numeric patient-action decision point in this marker occurrence
- `p37/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p37/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p37/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p37/recommendation/4.10.1` - no additional numeric patient-action decision point in this marker occurrence
- `p37/recommendation/4.11.1` - no additional numeric patient-action decision point in this marker occurrence
- `p38/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p38/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p38/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p38/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p38/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p38/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p38/recommendation/5.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p38/recommendation/5.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p39/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p39/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p39/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p39/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p39/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p39/practice-point/8` - no additional numeric patient-action decision point in this marker occurrence
- `p39/recommendation/5.3.2` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/8` - no additional numeric patient-action decision point in this marker occurrence
- `p40/practice-point/9` - no additional numeric patient-action decision point in this marker occurrence
- `p40/recommendation/5.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/8` - no additional numeric patient-action decision point in this marker occurrence
- `p41/practice-point/9` - no additional numeric patient-action decision point in this marker occurrence
- `p42/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p42/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p42/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p42/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p42/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p42/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p42/practice-point/8` - no additional numeric patient-action decision point in this marker occurrence
- `p43/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p43/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p43/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p43/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p43/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p43/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p44/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p44/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p44/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p44/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p44/practice-point/8` - no additional numeric patient-action decision point in this marker occurrence
- `p46/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p46/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p46/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p46/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p46/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p46/recommendation/6.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p46/recommendation/6.1.2` - no additional numeric patient-action decision point in this marker occurrence
- `p46/recommendation/6.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p47/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p47/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p47/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p47/practice-point/5` - no additional numeric patient-action decision point in this marker occurrence
- `p47/practice-point/6` - no additional numeric patient-action decision point in this marker occurrence
- `p47/practice-point/7` - no additional numeric patient-action decision point in this marker occurrence
- `p48/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p48/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p48/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p49/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p50/recommendation/1.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p59/recommendation/1.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p61/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p62/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p63/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p63/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p66/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p67/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p69/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p70/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p71/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p72/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p73/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p73/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p76/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p76/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p78/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p82/recommendation/2.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p85/recommendation/2.6.1` - no additional numeric patient-action decision point in this marker occurrence
- `p86/recommendation/2.1.2` - no additional numeric patient-action decision point in this marker occurrence
- `p89/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p90/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p92/recommendation/2.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p95/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p98/recommendation/2.3.1` - no additional numeric patient-action decision point in this marker occurrence
- `p102/recommendation/2.3.2` - no additional numeric patient-action decision point in this marker occurrence
- `p105/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p109/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p109/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p109/recommendation/2.4.1` - no additional numeric patient-action decision point in this marker occurrence
- `p115/recommendation/2.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p119/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p120/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p121/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p122/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p123/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p123/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p124/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p126/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p126/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p127/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p128/recommendation/2.6.1` - no additional numeric patient-action decision point in this marker occurrence
- `p132/recommendation/3.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p136/recommendation/3.1.2` - no additional numeric patient-action decision point in this marker occurrence
- `p141/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p141/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p141/recommendation/3.1.3` - no additional numeric patient-action decision point in this marker occurrence
- `p141/recommendation/4.9.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p144/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p144/recommendation/3.1.4` - no additional numeric patient-action decision point in this marker occurrence
- `p148/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p149/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p150/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p150/recommendation/3.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p156/recommendation/3.2.2` - no additional numeric patient-action decision point in this marker occurrence
- `p158/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p158/recommendation/3.2.3` - no additional numeric patient-action decision point in this marker occurrence
- `p163/recommendation/3.3.1` - no additional numeric patient-action decision point in this marker occurrence
- `p166/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p167/recommendation/3.3.2` - no additional numeric patient-action decision point in this marker occurrence
- `p169/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p170/recommendation/3.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p173/recommendation/3.5.2` - no additional numeric patient-action decision point in this marker occurrence
- `p176/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p176/recommendation/3.6.1` - no additional numeric patient-action decision point in this marker occurrence
- `p183/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p184/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p184/recommendation/3.7.1` - no additional numeric patient-action decision point in this marker occurrence
- `p188/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p189/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p189/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p190/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p190/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p191/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p191/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p192/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p195/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p199/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p199/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p200/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p201/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p201/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p202/recommendation/3.12.4.1` - no additional numeric patient-action decision point in this marker occurrence
- `p204/recommendation/3.12.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p208/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p212/recommendation/4.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p216/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p216/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p217/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p219/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p222/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p225/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p225/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p225/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p226/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p226/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p227/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p227/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p230/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p230/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p231/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p231/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p231/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p235/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p236/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p236/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p237/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p238/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p239/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p241/recommendation/4.9.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p246/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p246/recommendation/3.1.2` - no additional numeric patient-action decision point in this marker occurrence
- `p247/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p248/recommendation/4.9.3.1` - no additional numeric patient-action decision point in this marker occurrence
- `p250/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p250/recommendation/4.10.1` - no additional numeric patient-action decision point in this marker occurrence
- `p253/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p253/recommendation/4.11.1` - no additional numeric patient-action decision point in this marker occurrence
- `p258/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p258/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p258/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p260/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p261/recommendation/5.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p266/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p266/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p266/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p266/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p267/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p270/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p270/recommendation/5.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p274/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p274/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p275/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p276/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p276/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p277/recommendation/5.3.1` - no additional numeric patient-action decision point in this marker occurrence
- `p279/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p280/recommendation/5.3.2` - no additional numeric patient-action decision point in this marker occurrence
- `p282/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p284/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p285/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p286/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p288/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p289/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p289/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p290/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p291/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p291/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p292/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p292/recommendation/5.5.1` - no additional numeric patient-action decision point in this marker occurrence
- `p300/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p301/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p301/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p302/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p303/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p303/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p305/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p307/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p308/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p308/recommendation/5.7.1` - no additional numeric patient-action decision point in this marker occurrence
- `p310/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p311/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p311/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p313/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p314/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p314/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p315/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p316/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p317/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p318/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p319/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p320/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p324/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p324/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p324/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p325/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p326/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p327/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p327/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p328/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p328/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p328/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p328/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p329/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p329/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p330/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p331/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p332/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p333/recommendation/6.1.1` - no additional numeric patient-action decision point in this marker occurrence
- `p341/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p342/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p343/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p344/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p345/recommendation/6.1.2` - no additional numeric patient-action decision point in this marker occurrence
- `p348/recommendation/6.2.1` - no additional numeric patient-action decision point in this marker occurrence
- `p350/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p351/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p351/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p351/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p351/practice-point/4` - no additional numeric patient-action decision point in this marker occurrence
- `p352/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p353/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p354/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p354/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p354/practice-point/3` - no additional numeric patient-action decision point in this marker occurrence
- `p360/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p360/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p364/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
- `p364/practice-point/2` - no additional numeric patient-action decision point in this marker occurrence
- `p366/practice-point/1` - no additional numeric patient-action decision point in this marker occurrence
