# Diabetes — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

**Every `snippet` cell is the shortest verbatim ADA fragment that carries the
decision point.** It is what the citation gates check against — paraphrase it and a
fabricated citation stops being detectable. The quotation quantity for this sheet is
measured independently in [README.md](README.md#the-quoting-posture-ruled-against-a-public-repo)
and re-derived by a test.


## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| ada-2026 | ADA | ADA/standards-of-care-2026 | 2026 | 2026 | https://diabetesjournals.org/care/issue/49/Supplement_1 | bound |

## Scope

**Read:** all 377 source pages. The complete page read covered front matter and
methodology, chapter narrative, evidence tables, reference lists, disclosures, and
the index in addition to every record emitted by `tools/guidelines_recs.py` from the
source's `Recommendation` markers. The marker-bound extraction remains separately
accounted under [Coverage](#coverage): **126 records carrying 116 distinct
identifiers**. Its 98 change-summary records from pages 12–18 carry 88 distinct
identifiers, while 14 of the 28 remaining identifiers produce the 25 marker-derived
decision-point rows and 14 are scoped out by identifier. Ten duplicate occurrences
are audited separately, so that accounting remains record-level: 116 first
occurrences + 10 duplicate occurrences = 126 records.

**Not read:** nothing in the source page range. The recommendation record remains
`bound`, so its identifier accounting warns rather than refuses and does not claim
that the extraction is a complete recommendation index.

| span | pages | read |
| --- | --- | --- |
| recommendation markers | 12-363 | yes |
| front matter and methodology | 1-11 | yes |
| chapter narrative, evidence tables, and references | 12-363 | yes |
| disclosures | 364-368 | read 2026-08-23 |
| index | 369-377 | read 2026-08-23 |

**Second read:** blind reads dated 2026-08-23 covered the front matter and methodology,
the chapter narrative/evidence/reference span, the disclosures, and the index. The
front-matter and narrative reads produced the positive decision points; the
disclosures and index were independently confirmed as null spans. A fresh
non-authoring check accepted the corrected narrative inventory against the PDF, and a
separate fresh check accepted the corrected null index record.

The automatic second-read pairing still reports smoke-test warnings where its numeric
matcher cannot pair a word-only interval or where the independent inventory did not
repeat an already-bound row. The word-only intervals on pp. 56, 95, 115–118, 144,
268, 283, 304–305, 316, and 333 have matching rows below. The summary values on pp.
13 and 16 are represented by their underlying chapter rows rather than duplicated,
and the hypertension measurement rule on p. 223 also has a matching row. Bound rows
for the adult BMI treatment thresholds, CKD stage and eGFR limits, and the pediatric
age boundary independently pass the real-PDF citation gates even though the blind
narrative inventory did not repeat them. These are manual reconciliations of the two
directions, not edits to make the blind records agree. A clean gate would still be a
smoke test, never proof.

citations resolved against C:/codeing/guidelines-src on 2026-08-23


## Populations

| key | verbatim |
| --- | --- |
| post-acute-pancreatitis | Screen people for diabetes within 3–6 months following an episode of acute pancreatitis |
| chronic-pancreatitis | people with chronic pancreatitis |
| stage2-t1d-age8plus | selected individuals aged ≥8 years with stage 2 type 1 diabetes |
| diabetes-household | people with diabetes, caregivers, and family members |
| adults-t1d-obesity | adults with type 1 diabetes who have obesity |
| asian-adults-t1d-obesity | Asian American individuals |
| people-diabetes | people with diabetes |
| people-diabetes-htn | Individuals with hypertension |
| people-ckd-albuminuria300 | people with CKD and albuminuria ≥300 mg/g |
| people-ckd-g3plus | people with CKD stage G3 or higher |
| people-dialysis | individuals on dialysis |
| people-ckd-albuminuria | people with CKD and albuminuria |
| adults-t2d-uacr100-egfr30-90 | adults with type 2 diabetes and UACR ≥100 mg/g with eGFR 30–90 mL/min/1.73 m2 |
| people-egfr-under20-nondialysis | individuals with eGFR <20 mL/min/1.73 m2 and not on dialysis |
| adults-diabetes-age65plus | adults 65 years of age or older |
| pediatric-diabetes | children and adolescents with diabetes and their parents or caregivers |
| pregnancy-t1d-t2d | pregnant individuals with type 1 or type 2 diabetes |
| scope-children | children (aged birth to 11 years) |
| scope-adolescents | adolescents (aged 12–17 years) |
| scope-adults | adults (aged 18–64 years) |
| scope-older-adults | older adults (aged ≥65 years) |
| nonpregnant-individuals | nonpregnant individuals |
| people-prediabetes | people with prediabetes |
| pregnant-diabetes | pregnant individuals with diabetes |
| history-gdm | individuals with a history of gestational diabetes mellitus |
| people-diabetes-ckd | people with diabetes and chronic kidney disease |
| people-t1d | people with type 1 diabetes |
| people-t2d | people with type 2 diabetes |
| people-diabetes-overweight-obesity | people with diabetes and overweight or obesity |
| hospitalized-diabetes-hyperglycemia | hospitalized individuals with diabetes or hyperglycemia |
| people-cystic-fibrosis | people with cystic fibrosis |
| people-hiv | people with HIV |

## Quantities

| key | verbatim |
| --- | --- |
| albuminuria-eligibility-threshold | ≥300 mg/g |
| albuminuria-reduction-target | reduce urinary albumin by ≥30% |
| caregiver-dsmes-age-threshold | aged <18 years |
| chronic-pancreatitis-screening-interval | annually |
| cognitive-screening-age-threshold | 65 years of age or older |
| cognitive-screening-interval | annually |
| diabetes-distress-screening-interval | at least annually |
| dialysis-protein-intake | 1.0–1.2 g/kg/day |
| lifestyle-counseling-bp-threshold | blood pressure >120/80 mmHg |
| mra-consideration-medication-threshold | three classes of antihypertensive medications (including a diuretic) |
| nondialysis-ckd-stage-threshold | CKD stage G3 or higher |
| nondialysis-protein-intake | 0.8 g/kg body weight per day |
| nsmra-egfr-threshold | eGFR is ≥25 mL/min/1.73 m2 |
| nsmra-potassium-follow-up | 1 month after initiation |
| obesity-bmi-threshold | BMI ≥30.0 kg/m2 |
| post-pancreatitis-initial-screening-interval | within 3–6 months |
| post-pancreatitis-ongoing-screening-interval | and annually thereafter |
| pregnancy-aspirin-alternative-dose | 162 mg/day |
| pregnancy-aspirin-dose | 100–150 mg/day |
| pregnancy-aspirin-start | 12–16 weeks of gestation |
| sglt2-continuation-egfr-threshold | eGFR <20 mL/min/1.73 m2 |
| sglt2-nsmra-egfr-range | eGFR 30–90 mL/min/1.73 m2 |
| sglt2-nsmra-uacr-threshold | UACR ≥100 mg/g |
| teplizumab-discussion-age-threshold | aged ≥8 years |
| scope-child-age-band | aged birth to 11 years |
| scope-adolescent-age-band | aged 12–17 years |
| scope-adult-age-band | aged 18–64 years |
| scope-older-adult-age-threshold | aged ≥65 years |
| weight-loss-level-associated-greater-disease-modifying-benefit-type | sustained weight loss of >10% |
| early-response-supporting-continuation-chronic-obesity-pharmacotherapy | >5% weight loss after 3 months of use |
| safety-efficacy-monitoring-interval-after-starting-obesity-medication | at least monthly for the first 3 months and at least quarterly thereafter |
| age-threshold-highlighted-pad-screening-asymptomatic-diabetes | aged >=65 years |
| diagnostic-threshold-diabetes-nonpregnant-individuals | A1C >=6.5% (>=48 mmol/mol) |
| fasting-plasma-glucose-diagnostic-threshold-diabetes | FPG >=126 mg/dL (>=7.0 mmol/L) |
| defines-fasting-diagnostic-fasting-plasma-glucose | no caloric intake for at least 8 h |
| two-hour-oral-glucose-tolerance-diagnostic-threshold-diabetes | 2-h PG >=200 mg/dL (>=11.1 mmol/L) during OGTT |
| glucose-load-required-diagnostic-oral-glucose-tolerance-testing | 75 g anhydrous glucose |
| diagnostic-threshold-classic-hyperglycemic-symptoms-crisis-are-present | random plasma glucose >=200 mg/dL (>=11.1 mmol/L) |
| impaired-fasting-glucose-prediabetes-range | FPG 100-125 mg/dL (5.6-6.9 mmol/L) |
| impaired-glucose-tolerance-prediabetes-range-after-75-g-ogtt | 2-h PG 140-199 mg/dL (7.8-11.0 mmol/L) |
| a1c-range-defining-prediabetes | A1C 5.7-6.4% (39-47 mmol/mol) |
| repeat-antibody-testing-interval-single-confirmed-islet-autoantibody | every 6 months to 3 years (depending on age) |
| routine-adult-screening-start-age-earlier-risk-based-testing | screening should begin at age 35 years |
| minimum-repeat-diabetes-screening-interval-after-normal-screen | at a minimum of 3-year intervals |
| minimum-carbohydrate-intake-preparation-period-before-ogtt | at least 150 g/day ; for 3 days prior to testing |
| start-point-risk-based-type-2-diabetes-screening-youth | after the onset of puberty or after 10 years of age, whichever occurs earlier |
| youth-overweight-threshold-used-diabetes-screening-eligibility | BMI >=85th percentile |
| youth-obesity-threshold-used-diabetes-screening-eligibility | BMI >=95th percentile |
| diabetes-screening-schedule-second-generation-antipsychotics | baseline and repeat 12-16 weeks after medication initiation ; and annually thereafter |
| fasting-glucose-monitoring-schedule-people-hiv | 3–6 months after starting or switching antiretroviral therapy, then annually |
| glucose-a1c-monitoring-schedule-during-pi3k-alpha-inhibitor-therapy | weekly for the first 2 weeks ; every 4 weeks ; A1C every 3 months |
| glucose-a1c-monitoring-schedule-during-mtor-inhibitor-therapy | at each visit ; A1C every 3 months |
| start-age-interval-cystic-fibrosis-related-diabetes-screening | Annual screening ; begin by age 10 years |
| a1c-trigger-follow-up-interval-cystic-fibrosis-related-diabetes | A1C values between 5.5% and 6.4% ; OGTT within 3 months |
| a1c-diagnostic-threshold-consistent-cystic-fibrosis-related-diabetes | A1C value of >=6.5% (>=48 mmol/mol) |
| start-point-interval-complication-monitoring-cystic-fibrosis-related-diabetes | Beginning 5 years after the diagnosis of CFRD, annual monitoring |
| trigger-neonatal-diabetes-genetic-testing | diagnosed with diabetes in the first 6 months of life |
| stable-mild-glycemia-pattern-supporting-consideration-monogenic-diabetes | fasting hyperglycemia (100-150 mg/dL [5.6-8.5 mmol/L]) ; A1C between 5.6 and 7.6% |
| timing-early-pregnancy-testing-undiagnosed-diabetes-abnormal-glucose-metabolism | Before 15 weeks of gestation |
| early-pregnancy-abnormal-glucose-metabolism-definition | A1C 5.9-6.4% [41-47 mmol/mol] or FPG 110-125 mg/dL [6.1-6.9 mmol/L] |
| routine-gestational-diabetes-screening-window | 24-28 weeks of gestation |
| postpartum-diabetes-screening-window-test-after-gestational-diabetes | 4-12 weeks postpartum ; 75-g OGTT |
| lifelong-diabetes-screening-interval-after-gestational-diabetes | every 1-3 years |
| minimum-diabetes-monitoring-interval-people-prediabetes | at least annually |
| monitoring-schedule-presymptomatic-type-1-diabetes | A1C approximately every 6 months and 75-g oral glucose tolerance test ; annually |
| weight-reduction-goal-diabetes-prevention-programs | at least 5-7% of initial body weight |
| physical-activity-goal-diabetes-prevention-programs | >=150 min/week of moderate-intensity physical activity |
| age-bmi-profile-favoring-metformin-diabetes-prevention | aged 25-59 years with BMI >=35 kg/m2 |
| higher-glycemia-profile-favoring-metformin-diabetes-prevention | FPG >=110 mg/dL [>=6 mmol/L] ; A1C >=6.0% [>=42 mmol/mol] |
| bmi-marker-particularly-high-progression-risk-warranting-intensive-prevention | BMI >=35 kg/m2 |
| glycemic-markers-particularly-high-diabetes-progression-risk | fasting plasma glucose 110-125 mg/dL ; 2-h postchallenge glucose 173-199 mg/dL ; A1C >=6.0% |
| follow-up-interval-comprehensive-medical-evaluation | at least every 3-6 months ; and then at least annually |
| minimum-age-updated-covid-19-vaccination | aged 6 months and older |
| age-at-which-hepatitis-b-vaccination-becomes-discretionary-based | adults aged >=60 years |
| minimum-age-annual-influenza-vaccination | >=6 months of age |
| age-pregnancy-limits-live-attenuated-influenza-vaccine-chronic-condition | 2-49 years of age and are not pregnant |
| eligibility-single-rsv-vaccine-dose | all adults aged >=75 years and adults aged 60-74 years who are at increased risk |
| age-interval-dxa-bone-density-monitoring-older-adults-diabetes | aged >=65 years ; every 2-3 years |
| calcium-intake-target-people-at-fracture-risk | calcium (1,000-1,200 mg/day) |
| bone-density-threshold-supporting-osteoporosis-drug-therapy | T-score <=-2.5 |
| frax-thresholds-supporting-osteoporosis-drug-therapy | >=3% for hip fracture or >=20% for major osteoporotic fracture |
| age-fracture-pattern-considered-diagnostic-osteoporosis-regardless-bmd | low-trauma fracture ; in adults aged >=65 years |
| glucocorticoid-exposure-used-as-bone-density-testing-risk-factor | prednisone at doses >2.5 mg per day for >=3 months |
| vitamin-d-target-people-receiving-antiresorptive-therapy | 25-hydroxyvitamin D level of >30 ng/mL |
| age-specific-daily-vitamin-d-allowances | 600 IU for people aged 51-70 years and 800 IU for people aged >70 years |
| required-dosing-interval-whose-disruption-risks-rebound-bone-loss | every 6-month denosumab injection schedule |
| duration-triggering-evaluation-other-liver-disease-causes-fib-4 | persistently elevated plasma aminotransferase levels for >6 months |
| threshold-additional-liver-fibrosis-risk-stratification | FIB-4 >=1.3 |
| high-risk-threshold-warranting-direct-liver-specialist-referral | FIB-4 >2.67 |
| higher-age-adjusted-fib-4-threshold-older-adults | in diabetes >=65 years ; 1.9-2.0 rather than >=1.3 |
| transient-elastography-level-indicating-lower-advanced-fibrosis-risk | LSM <8.0 kPa |
| follow-up-interval-after-low-risk-liver-stiffness-result | repeat surveillance testing every >=2 years |
| liver-stiffness-threshold-warranting-hepatology-referral | LSM >=8.0 kPa |
| elf-thresholds-separating-lower-from-high-advanced-fibrosis-risk | ELF <9.8 ; ELF >=9.8 |
| intermediate-elf-range-that-may-require-more-frequent-repeat | ELF ; between 9.2 and 9.7 |
| weight-loss-needed-liver-histology-improvement-larger-loss-favored | minimum weight loss goal of 5%, preferably >=10% |
| critical-times-provide-reassess-diabetes-self-management-education-support | at diagnosis, annually ; when not meeting treatment goals ; and when transitions ; occur |
| weight-loss-aim-overweight-obesity-treatment-plan | at least 5-7% weight loss |
| recommended-sodium-intake-ceiling | <2,300 mg/day |
| dietary-fiber-density-target | at least 14 g fiber per 1,000 kcal |
| daily-alcohol-ceiling | <=2 drinks a day for men or <=1 drink a day for women |
| defines-one-alcoholic-drink | 12-oz beer, a 5-oz glass of wine, or 1.5 oz of distilled spirits |
| medication-assisted-weight-loss-goal-people-at-risk-type | 7-10% weight loss |
| maximum-uninterrupted-sitting-interval | interrupted at least every 30 min |
| youth-aerobic-strengthening-activity-targets | 60 min/day ; muscle-strengthening and bone-strengthening ; at least 3 days/week |
| adult-aerobic-activity-target-distribution | 150 min or more ; per week, spread over at least 3 days/week, with no more than 2 consecutive days without activity |
| alternative-vigorous-activity-duration-more-physically-fit-adults | minimum 75 min/week |
| adult-resistance-exercise-frequency | 2-3 sessions/week ; on nonconsecutive days |
| flexibility-balance-training-frequency-most-older-adults | 2-3 times/week |
| suggested-glyburide-adjustment-during-religious-fasting | reduce dose by 50% |
| suggested-basal-insulin-adjustment-during-religious-fasting | Reduce dose by 25-35% |
| suggested-prandial-mixed-insulin-reduction-meal-followed-by-fasting | Reduce dose ; 35-50% |
| recommended-recreational-screen-time-ceiling-children-adolescents | less than 2 h per day |
| level-prompting-carbohydrate-insulin-precautions-before-exercise | pre-exercise glucose levels are <90 mg/dL (<5.0 mmol/L) |
| diagnostic-criteria-proposed-hyperglycemic-ketosis-cannabis-hyperemesis-syndrome | blood glucose >=250 mg/dL ; anion gap >10 ; beta-hydroxybutyrate >0.6 mmol/L ; pH >=7.4 ; bicarbonate >=15 mmol/L |
| psychosocial-screening-interval-event-triggers | at least annually or when there is a change in health status, treatment, or life circumstances |
| anxiety-fear-hypoglycemia-screening-interval | at least annually |
| depression-screening-interval | at least annually and more frequently among those with a history of depression |
| monitoring-interval-glycemia-weight-lipids-second-generation-antipsychotics | every 12-16 weeks |
| glycemic-assessment-interval-stable-versus-not-at-goal-recently | at least two times a year ; every 3 months |
| minimum-cgm-data-duration-completeness-glycemic-assessment | 10- to 14-day CGM assessment ; wear of 70% or higher |
| general-glycemic-goal-many-nonpregnant-adults | A1C goal of <7% (<53 mmol/mol) |
| general-cgm-time-range-goal-many-nonpregnant-adults | goal time in range of >70% |
| cgm-hypoglycemia-exposure-limits | time <70 mg/dL ; <4% (or <1% for older adults) ; time <54 mg/dL ; <1% |
| example-lower-glycemic-goal-healthy-low-risk-individuals | A1C ; <6.5% [<48 mmol/mol] |
| capillary-glucose-goals-many-nonpregnant-adults | Preprandial ; 80-130 mg/dL ; Peak postprandial ; <180 mg/dL |
| timing-postprandial-glucose-measurement | 1-2 h after the beginning of the meal |
| example-less-stringent-goal-complex-health-limited-life-expectancy | A1C up to 8% [64 mmol/mol] |
| impaired-awareness-fear-hypoglycemia-screening-interval | at least annually |
| hypoglycemia-treatment-trigger-repeat-treatment-interval | glucose <70 mg/dL ; Fifteen minutes after initial treatment, repeat |
| level-1-hypoglycemia-classification | Level 1 Glucose <70 mg/dL ; and >=54 mg/dL |
| level-2-hypoglycemia-classification-requiring-immediate-action | Level 2 Glucose <54 mg/dL |
| recency-window-making-level-2-3-hypoglycemia-major-future | within the past 3-6 months |
| age-counted-among-hypoglycemia-risk-factors | Age >=75 years |
| usual-initial-oral-carbohydrate-treatment-hypoglycemia | 15 g carbohydrates |
| typical-lower-carbohydrate-treatment-amount-automated-insulin-delivery | 5-10 g carbohydrates |
| glucose-level-strengthening-indication-measure-ketones-at-risk-people | glucose levels exceed 200 mg/dL (11.1 mmol/L) |
| acetaminophen-cgm-interference-threshold | Acetaminophen >4 g/day |
| ascorbic-acid-cgm-interference-threshold | Ascorbic acid (vitamin C), >500 mg/day |
| ascorbic-acid-plus-cgm-interference-threshold | Ascorbic acid (vitamin C), >1,000 mg/day |
| typical-use-duration-insulin-pens-after-first-use-depending | usually for 28 days, ranging from 14 to 56 days |
| bmi-ranges-classifying-overweight-obesity-classes-1-3 | BMI 25-29.9 ; 30-34.9 ; 35-39.9 ; >=40 kg/m2 |
| anthropometric-monitoring-interval-routinely-during-active-weight-treatment | at least annually ; at least every 3 months |
| high-frequency-counseling-intensity-effective-lifestyle-weight-intervention | >=16 sessions in 6 months |
| recommended-energy-deficit-weight-loss | 500-750 kcal/day energy deficit |
| weight-maintenance-program-duration | long-term (≥1 year) |
| weight-maintenance-contact-interval | monthly contact and support |
| weight-maintenance-activity-target | regular physical activity (200–300 min/week) |
| very-low-calorie-meal-range-reserved-selected-closely-monitored | 800-1,000 kcal/day |
| usual-maximum-short-term-duration-intensive-very-low-calorie | generally up to 3 months |
| weight-loss-thresholds-prompting-micronutrient-deficiency-screening | significant (>20%) or rapid (>4% per month) weight loss |
| eligibility-threshold-fda-approved-obesity-medications | BMI >=30 kg/m2 or >=27 kg/m2 with one or more obesity-associated comorbid conditions |
| duration-added-nonoral-contraception-tirzepatide | for 4 weeks after initiation and for 4 weeks after each dose escalation |
| example-insulin-reductions-adding-glp-1-dual-gip-glp | reduce bolus by 10-20%, basal approximately 10% if A1C <7.5% |
| obesity-medication-effectiveness-safety-review-schedule | at least monthly for the first 3 months and at least quarterly thereafter |
| typical-early-response-boundary-informing-continuation-versus-reassessment-obesity | >5% weight loss after 3 months ; <5% weight loss after 3 months |
| bmi-threshold-considering-metabolic-surgery-type-2-diabetes | BMI >=30.0 kg/m2 (or >=27.5 kg/m2 in Asian American individuals) |
| monitoring-interval-inadequate-loss-weight-recurrence-after-metabolic-surgery | at least every 6-12 months |
| regular-reassessment-interval-insulin-taking-behavior-treatment-plans | every 3-6 months |
| typical-total-daily-insulin-requirement-range-type-1-diabetes | 0.4 to 1 unit/kg/day |
| typical-stable-adult-type-1-diabetes-starting-dose-basal | 0.5 units/kg/day ; approximately one-half ; prandial ; remaining ; basal |
| typical-initial-insulin-range-newly-diagnosed-type-1-diabetes | 0.2 to 0.6 units/kg/day |
| medication-plan-adherence-reevaluation-interval-type-2-diabetes | every 3-6 months |
| very-high-glycemia-prompting-consideration-insulin-initiation | A1C >10% ; or blood glucose >=300 mg/dL |
| sglt2-inhibitor-preoperative-withholding-interval | discontinue before scheduled surgery (e.g., 3-4 days) |
| level-at-which-dual-therapy-more-potent-agent-is | A1C is >=1.5% above the individualized glycemic goal |
| basal-insulin-initiation-dose-type-2-diabetes | Start 10 units per day or 0.1-0.2 units/kg per day |
| example-basal-insulin-titration-step-interval | increase 2 units every 3 days |
| insulin-dose-reduction-unexplained-hypoglycemia-occurs | lower dose by 10-20% |
| kidney-function-threshold-avoiding-lixisenatide-exenatide | eGFR <=30 mL/min/1.73 m2 |
| metformin-kidney-function-initiation-dose-reduction-stopping-thresholds | metformin should not be started ; eGFR <45 ; reduced once eGFR is <45 ; stopped once eGFR is <30 |
| signal-prompting-assessment-insulin-overbasalization | bedtime-to-morning glucose differential >=50 mg/dL |
| suggested-starting-prandial-insulin-dose-at-largest-meal | 4 units or 10% of the amount of basal insulin |
| duration-on-tirzepatide-maintenance-dose-before-ending-backup-contraception | at least 4 weeks |
| level-at-which-basal-insulin-should-be-considered-during | blood glucose >250 mg/dL |
| definition-elevated-blood-pressure | 120-129 mmHg with ; <80 mmHg |
| definition-hypertension | >=130 mmHg or ; >=80 mmHg |
| blood-pressure-measurement-interval | every routine clinical visit, or at least every 6 months |
| measurement-requirement-diagnose-hypertension | average of two or more measurements obtained on two or more occasions |
| level-permitting-hypertension-diagnosis-at-single-visit | blood pressure >=180/110 mmHg and cardiovascular disease |
| general-treated-blood-pressure-goal-encouraged-systolic-goal-high | <130/80 mmHg ; systolic ; <120 mmHg |
| office-blood-pressure-threshold-pharmacologic-therapy | >=130/80 mmHg |
| threshold-prompt-initiation-two-antihypertensive-agents | >=150/90 mmHg |
| electrolyte-monitoring-interval-after-starting-changing-diuretic | 7-14 days after initiation or after a dose change |
| lipid-monitoring-schedule-after-lipid-lowering-treatment-starts-changes | 4-12 weeks after initiation or a change in dose, and annually thereafter |
| lipid-assessment-interval-younger-adults-not-otherwise-needing-more | at least every 5 years ; <40 years of age |
| age-range-routine-primary-prevention-statin-therapy-diabetes | aged 40-75 years |
| age-risk-group-which-statin-initiation-may-be-reasonable | aged 20-39 years with additional ASCVD risk factors |
| high-risk-primary-prevention-ldl-reduction-level-goals | LDL cholesterol by >=50% ; goal of <70 mg/dL |
| age-threshold-individualized-initiation-continuation-statin-therapy | aged >75 years |
| secondary-prevention-ldl-reduction-level-goals-ascvd | LDL ; >=50% ; goal of <55 mg/dL |
| threshold-prompting-secondary-cause-evaluation-pancreatitis-prevention-therapy-consideration | fasting triglyceride levels >=500 mg/dL |
| hypertriglyceridemia-thresholds-prompting-treatment-lifestyle-secondary-factors | fasting >150 mg/dL or nonfasting >175 mg/dL |
| triglyceride-range-which-icosapent-ethyl-may-be-considered-on | 150-499 mg/dL |
| severe-triglyceride-level-strengthening-need-drug-therapy-dietary-fat | especially >1,000 mg/dL |
| aspirin-dose-range-secondary-prevention-selected-primary-prevention | aspirin therapy (75-162 mg/day) |
| dose-ascvd-aspirin-allergy | clopidogrel (75 mg/day) |
| combination-regimen-selected-stable-coronary-pad-patients-low-bleeding | 81 mg aspirin daily plus 2.5 mg rivaroxaban twice daily |
| age-risk-profile-considering-primary-prevention-aspirin | aged >=50 years ; at least one additional major risk factor |
| age-criterion-pad-screening-ankle-brachial-index-results-would | age >=65 years |
| age-risk-threshold-ace-inhibitor-arb-cardiovascular-prevention | aged >=55 years with established ASCVD or multiple ASCVD risk factors |
| abnormal-biomarker-thresholds-used-heart-failure-screening | BNP >=50 pg/mL and NT-proBNP >=125 pg/mL |
| kidney-function-component-ckd-diagnosis | eGFR <60 mL/min/1.73 m2 |
| kidney-screening-start-point-interval | at least annually ; type 1 diabetes duration >=5 years ; all type 2 diabetes |
| ckd-monitoring-frequency-based-on-stage | 1-4 times per year |
| normal-mild-moderate-severe-albuminuria-categories | <30 ; >=30 to <300 ; >=300 mg/g creatinine |
| confirmation-requirement-albuminuria | two of three specimens ; within a 3- to 6-month period |
| laboratory-monitoring-intervals-by-advanced-ckd-stage | every 6-12 months for stage G3 ; every 3-5 months for stage G4 ; every 1-3 months for stage G5 |
| high-protein-intake-avoid-ckd | >20% of daily calories ; or >1.3 g/kg/day |
| serum-creatinine-rise-within-which-renin-angiotensin-blockade-should | <=30% |
| kidney-function-threshold-initiate-sglt2-inhibitor-ckd-benefit | eGFR >=20 mL/min/1.73 m2 |
| range-requiring-temporary-metformin-discontinuation-iodinated-contrast-procedures | eGFR 30-60 mL/min/1.73 m2 |
| kidney-function-threshold-nephrology-referral | eGFR <30 mL/min/1.73 m2 |
| timing-initial-dilated-eye-exam-adult-type-1-diabetes | 5 years after the onset of diabetes |
| eye-screening-interval-after-normal-exams-goal-glycemia | every 1-2 years |
| eye-examination-interval-any-diabetic-retinopathy-is-present | at least annually |
| retinopathy-monitoring-period-during-after-pregnancy-indicated | every trimester and for 1 year postpartum |
| typical-initial-anti-vegf-dosing-interval-center-involved-diabetic | every 4-8 weeks during the first 12 months |
| extended-dosing-interval-achievable-faricimab-aflibercept-8-mg | up to every 16 weeks |
| neuropathy-screening-start-points-interval | starting at diagnosis of type 2 diabetes and 5 years after ; type 1 diabetes and at least annually thereafter |
| foot-sensory-screening-interval-monofilament-force | annual 10-g monofilament testing |
| resting-tachycardia-orthostatic-blood-pressure-changes-supporting-autonomic-neuropathy | >100 bpm ; fall ; >20 mmHg or >10 mmHg |
| gastric-emptying-scintigraphy-measurement-schedule-gastroparesis-diagnosis | 15-min intervals for 4 h |
| duration-beyond-which-metoclopramide-treatment-gastroparesis-is-not-fda | beyond 12 weeks |
| threshold-prompting-formal-vascular-evaluation-angiography | toe pressures <30 mmHg with foot ulcers |
| foot-screening-interval-very-low-risk | Annually |
| foot-screening-interval-low-risk | Every 6–12 months |
| foot-screening-interval-moderate-risk | Every 3–6 months |
| foot-screening-interval-high-risk | Every 1–3 months |
| age-repeat-interval-noninvasive-arterial-screening-diabetes | >50 years of age ; repeated every 5 years |
| wound-response-threshold-prompting-advanced-wound-therapy-consideration | fails to show a reduction of 50% or more after 4 weeks |
| geriatric-syndrome-hypoglycemia-polypharmacy-screening-interval | at least annually |
| glycemic-goals-healthy-older-adults | A1C <7.0-7.5% ; TIR ; >=70% ; time below ; <=4% |
| less-stringent-glycemic-goals-older-adults-complex-health | A1C <8.0% ; TIR ; >=50% ; time below ; <1% |
| glucose-goals-healthy-older-adults | fasting 80-130 ; bedtime 80-180 mg/dL |
| glucose-goals-complex-intermediate-older-adults | fasting 90-150 ; bedtime 100-180 mg/dL |
| glucose-ranges-very-complex-poor-health-older-adults | fasting 100-180 ; bedtime 110-200 mg/dL |
| minimum-protein-intake-older-adults | at least 0.8 g/kg body weight/day |
| lower-dose-metformin-range-kidney-monitoring-interval-older-adults | eGFR 30-45 ; monitored every 3-6 months |
| duration-trigger-interval-b12-monitoring | metformin long term (>4 years), vitamin B12 levels ; annually |
| minimum-assessment-schedule-post-acute-long-term-care | every 30 days for the first 90 days ; once every 60 days |
| long-term-care-glucose-patterns-requiring-prompt-clinician-notification | two or more ; >250 mg/dL within 24 h ; consistently >300 mg/dL over 2 consecutive days |
| pediatric-diabetes-education-support-schedule | at diagnosis and routinely ; at each follow-up visit |
| pediatric-nutrition-education-schedule | at diagnosis, and at least annually |
| pediatric-aerobic-strengthening-activity-goals | 60 min ; daily ; at least 3 days per week |
| initial-medication-doses-youth-type-2-diabetes-algorithm | Metformin ; up to 2,000 mg per day ; long-acting insulin 0.5 units/kg/day |
| age-at-which-diabetes-distress-screening-may-begin | as early as 7 or 8 years of age |
| start-age-routine-depression-screening-youth | beginning at age 12 years |
| age-threshold-supporting-routine-anxiety-screening | aged 8 years and above |
| examples-less-stringent-pediatric-glycemic-goals | A1C <7% ; or <7.5% |
| more-stringent-glycemic-goal-selected-children-adolescents | A1C ; <6.5% |
| cgm-lookback-period-recommended-pediatric-metrics | most recent 14 days |
| hyperglycemia-ketone-levels-at-which-physical-activity-should-be | glucose >=350 mg/dL ; beta-hydroxybutyrate >1.5 mmol/L |
| pre-exercise-blood-glucose-goal-youth | 126-180 mg/dL |
| carbohydrate-replacement-during-exercise-after-insulin-boluses | 0.5-1.0 g of carbohydrates/kg per h ; approximately 30-60 g |
| age-bmi-criteria-pediatric-type-2-diabetes-risk-screening | after 10 years of age ; BMI >=85th to <95th ; BMI >=95th percentile |
| pediatric-type-2-diabetes-lifestyle-weight-goal | at least a 7-10% decrease in excess weight |
| pediatric-type-2-diabetes-glycemic-assessment-interval | at least every 3 months |
| boundary-between-metformin-only-initial-treatment-initial-long-acting | A1C >=8.5% |
| level-prompting-evaluation-treatment-hyperglycemic-hyperosmolar-state | blood glucose >=600 mg/dL |
| class-2-obesity-criterion-considering-adolescent-metabolic-surgery | BMI 35 to <40 kg/m2 or 120% to <140% percentile |
| celiac-disease-rescreening-schedule-after-type-1-diabetes-diagnosis | repeated at 2 and then 5 years |
| pediatric-type-1-diabetes-lipid-screening-start-repeat-schedule | age is >=2 years ; at 9-11 years ; every 3 years |
| pediatric-ldl-treatment-goal | LDL cholesterol goal is <100 mg/dL |
| pediatric-dyslipidemia-nutrition-limits | saturated fat to <7% ; cholesterol to <200 mg/day |
| threshold-nutrition-trial-duration-starting-pediatric-statin-therapy | LDL ; >130 mg/dL after 6 months ; goal ; <100 mg/dL |
| pediatric-threshold-starting-fibrate-reduce-pancreatitis-risk | triglycerides >400 mg/dL fasting or >1,000 mg/dL nonfasting |
| pediatric-confirmed-hypertension-definition | BP consistently >=95th percentile ; or aged >=13 years, BP >=130/80 mmHg |
| pediatric-hypertension-treatment-goal | BP <90th percentile ; or aged >=13 years, BP <130/80 mmHg |
| type-1-diabetes-pediatric-nephropathy-screening-start-interval | at puberty or at age >=11 years ; diabetes for 5 years and annually thereafter |
| pediatric-elevated-uacr-confirmation-requirement | two of three samples over a 6-month period |
| monitoring-interval-pediatric-nephropathy | every 3-6 months |
| timing-age-puberty-condition-initial-pediatric-retinal-exam | type 1 diabetes for 3-5 years ; aged >=11 years or puberty |
| pediatric-retinal-follow-up-intervals-after-initial-type-1 | every 2 years ; every 4 years may be acceptable ; A1C <8% |
| sleep-apnea-symptom-screening-interval-youth-diabetes | at least annually |
| latest-start-point-pediatric-adult-transition-preparation | at least 1 year before the anticipated transfer |
| preconception-glycemic-goal | A1C <6.5% (<48 mmol/mol) |
| eye-monitoring-schedule-preexisting-diabetes-pregnancy | every trimester and for 1 year postpartum |
| recommended-preconception-prenatal-supplement-amounts | 400-800 micrograms of folic acid ; 150 micrograms of potassium iodide |
| advised-preconception-glucose-goals | preprandial glucose 80-110 mg/dL ; 2 h postprandial <155 mg/dL |
| level-at-which-prandial-insulin-dose-should-be-reduced | postprandial glucose <100 mg/dL |
| suggested-discontinuation-intervals-before-planned-pregnancy | semaglutide at least 2 months before ; tirzepatide at least 1 month before pregnancy |
| pregnancy-glucose-goals | fasting <95 mg/dL ; 1-h <140 mg/dL or 2-h <120 mg/dL |
| preferred-relaxed-a1c-goals-during-pregnancy | A1C ; <6% ; relaxed to <7% |
| current-hypoglycemia-thresholds-pregnancy | blood glucose <70 mg/dL ; sensor glucose <63 mg/dL |
| pregnancy-fasting-glucose-target | 70–95 mg/dL |
| pregnancy-one-hour-postprandial-glucose-target | 110–140 mg/dL |
| pregnancy-two-hour-postprandial-glucose-target | 100–120 mg/dL |
| early-pregnancy-fasting-testing-frequency-escalation-threshold | 3-4 times per week ; predominantly >=110 mg/dL ; testing ; daily |
| pregnancy-cgm-target-range | 63–140 mg/dL, >70% |
| pregnancy-cgm-level-one-low-limit | <63 mg/dL, <4% |
| pregnancy-cgm-level-two-low-limit | <54 mg/dL, <1% |
| pregnancy-cgm-high-limit | >140 mg/dL, <25% |
| pregnancy-dietary-reference-intakes | minimum of 175 g carbohydrate ; 71 g protein ; 28 g fiber |
| stop-point-metformin-used-induce-ovulation-pcos | discontinued by the end of the first trimester |
| pregnancy-postpartum-aerobic-activity-target | at least 150 min ; each week during pregnancy and postpartum |
| recommended-pregnancy-weight-gain-overweight-obesity-respectively | 15-25 lbs ; 10-20 lbs |
| blood-pressure-threshold-initiating-titrating-chronic-hypertension-therapy-pregnancy | 140/90 mmHg |
| blood-pressure-level-prompting-deintensification-during-pregnancy | <90/60 mmHg |
| postpartum-gdm-initial-screening-interval | 4–12 weeks postpartum |
| postpartum-gdm-lifelong-screening-interval | every 1–3 years |
| alternative-later-postpartum-test-ogtt-is-declined-not-completed | A1C performed at 6-12 months postpartum |
| admission-hyperglycemia-threshold-lookback-window-requiring-a1c | random blood glucose >140 mg/dL ; prior 3 months |
| persistent-inpatient-hyperglycemia-threshold-starting-intensifying-therapy | >=180 mg/dL ; two occasions within 24 h |
| glycemic-goal-most-critically-ill-inpatients | 140-180 mg/dL |
| glycemic-goal-most-noncritically-ill-inpatients | 100-180 mg/dL |
| more-stringent-inpatient-goal-that-may-suit-selected-critical | 110-140 mg/dL |
| inpatient-glucose-monitoring-frequencies-eating-not-eating-receiving-iv | before meals ; every 4-6 h ; every 30 min to every 2 h |
| timing-subcutaneous-basal-insulin-before-stopping-iv-insulin | 2 h before intravenous infusion is discontinued |
| usual-starting-total-daily-inpatient-insulin-dose | 0.3-0.6 units/kg/day |
| one-approach-estimating-initial-inpatient-total-daily-insulin | 80% of the home insulin dose |
| total-daily-dose-cutoffs-selecting-correction-insulin-scale-intensity | low ; <40 units/day, medium ; 40-80 units/day, and high ; >80 units/day |
| typical-threshold-correction-insulin-dosing | start at 140 or 150 mg/dL |
| preoperative-sglt2-inhibitor-withholding-interval | 3 days before scheduled surgeries (4 days for ertugliflozin) |
| inpatient-hypoglycemia-carbohydrate-dose | 15 g of fast-acting carbohydrate |
| inpatient-hypoglycemia-recheck-interval | every 15 min |
| inpatient-hypoglycemia-treatment-stop-threshold | above 70 mg/dL |
| insulin-carbohydrate-starting-ratio-enteral-parenteral-nutrition | 1 unit ; every 10-15 g of carbohydrate |
| correction-insulin-intervals-during-continuous-nutrition | regular human insulin every 6 h or rapid-acting insulin every 4 h |
| preoperative-a1c-goal-recency-requirement | A1C goal <8% ; within 3 months |
| alternative-cgm-evidence-adequate-preoperative-glycemia | 14-day glucose management indicator <8% and/or time in range >50% |
| perioperative-glucose-target | between 100 and 180 mg/dL |
| glucose-monitoring-interval-while-npo-perioperatively | at least every 2-4 h |
| preoperative-basal-insulin-reduction | 25% |
| preoperative-nph-insulin-dose | one-half of the dose |
| preoperative-long-acting-basal-insulin-dose | 75–80% of the dose |
| risk-mitigation-delayed-gastric-emptying-glp-1-therapy | liquid nutrition protocol for 24 h before the procedure |
| subcutaneous-rapid-acting-insulin-regimen-mild-dka | 0.1 units/kg ; every 1 h or 0.2 units/kg every 2 h |
| dka-initial-iv-insulin-rate | 0.1 units/kg/h |
| dka-reduced-iv-insulin-rate | 0.05 units/kg/h |
| dka-insulin-rate-reduction-glucose-threshold | <250 mg/dL |
| hyperglycemic-crisis-potassium-insulin-hold-threshold | K+ <3.5 mmol/L |
| hyperglycemic-crisis-potassium-target | between 4 and 5 mmol/L |
| severe-biochemical-thresholds-considering-bicarbonate-phosphate-dka | Bicarbonate ; only ; pH <7.0 ; phosphate <1.0 mmol/L |
| dka-glucose-diagnostic-threshold | >=200 mg/dL |
| dka-beta-hydroxybutyrate-diagnostic-threshold | >=3.0 mmol/L |
| dka-ph-diagnostic-threshold | <7.3 |
| dka-bicarbonate-diagnostic-threshold | <18 mmol/L |
| hhs-glucose-diagnostic-threshold | >=600 mg/dL |
| hhs-effective-osmolality-diagnostic-threshold | >300 mOsm/kg |
| hhs-total-osmolality-diagnostic-threshold | >320 mOsm/kg |
| hhs-beta-hydroxybutyrate-diagnostic-threshold | <3.0 mmol/L |
| hhs-ph-diagnostic-threshold | >=7.3 |
| hhs-bicarbonate-diagnostic-threshold | >=15 mmol/L |
| transition-timing-from-iv-subcutaneous-insulin-after-dka | basal insulin 2-4 h before the intravenous insulin is stopped |
| subcutaneous-rapid-acting-insulin-interval-mild-uncomplicated-dka | every 1-2 h |
| postdischarge-follow-up-after-inpatient-dysglycemia | within 1 month of discharge |
| earlier-postdischarge-follow-up-after-treatment-change-or-poor-control | in 1-2 weeks |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| post-pancreatitis-initial-screening-interval | post-acute-pancreatitis | 3-6 months | "within 3–6 months" | ada-2026 | p45 | p45/recommendation/2.23 | E |
| post-pancreatitis-ongoing-screening-interval | post-acute-pancreatitis | annually | "RENDERED: and annually thereafter" | ada-2026 | p45 | p45/recommendation/2.23 | E |
| chronic-pancreatitis-screening-interval | chronic-pancreatitis | annually | "annually" | ada-2026 | p45 | p45/recommendation/2.23 | E |
| teplizumab-discussion-age-threshold | stage2-t1d-age8plus | >=8 years | "aged ≥8 years" | ada-2026 | p62 | p62/recommendation/3.17 | B |
| diabetes-distress-screening-interval | diabetes-household | at least annually | "at least annually" | ada-2026 | p116 | p116/recommendation/5.45 | B |
| obesity-bmi-threshold | adults-t1d-obesity | >=30.0 kg/m2 | "BMI ≥30.0 kg/m2" | ada-2026 | p183 | p183/recommendation/8.29 | B/C |
| obesity-bmi-threshold | asian-adults-t1d-obesity | >=27.5 kg/m2 | "≥27.5 kg/m2" | ada-2026 | p183 | p183/recommendation/8.29 | B/C |
| lifestyle-counseling-bp-threshold | people-diabetes | >120/80 mmHg | "blood pressure >120/80 mmHg" | ada-2026 | p227 | p227/recommendation/10.5 | A |
| mra-consideration-medication-threshold | people-diabetes-htn | three antihypertensive classes including a diuretic | "RENDERED: three classes of antihypertensive medications (including a diuretic)" | ada-2026 | p228 | p228/recommendation/10.13 | A |
| albuminuria-reduction-target | people-ckd-albuminuria300 | >=30% | "reduce urinary albumin by ≥30%" | ada-2026 | p255 | p255/recommendation/11.2 | B |
| albuminuria-eligibility-threshold | people-ckd-albuminuria300 | >=300 mg/g | "≥300 mg/g" | ada-2026 | p255 | p255/recommendation/11.2 | B |
| nondialysis-ckd-stage-threshold | people-ckd-g3plus | G3 or higher | "CKD stage G3 or higher" | ada-2026 | p256 | p256/recommendation/11.3 | A |
| nondialysis-protein-intake | people-ckd-g3plus | 0.8 g/kg/day | "0.8 g/kg body weight per day" | ada-2026 | p256 | p256/recommendation/11.3 | A |
| dialysis-protein-intake | people-dialysis | 1.0-1.2 g/kg/day | "1.0–1.2 g/kg/day" | ada-2026 | p256 | p256/recommendation/11.3 | B |
| nsmra-egfr-threshold | people-ckd-albuminuria | >=25 mL/min/1.73 m2 | "eGFR is ≥25 mL/min/1.73 m2" | ada-2026 | p261 | p261/recommendation/11.8 | A |
| nsmra-potassium-follow-up | people-ckd-albuminuria | 1 month | "1 month after initiation" | ada-2026 | p261 | p261/recommendation/11.8 | A |
| sglt2-nsmra-uacr-threshold | adults-t2d-uacr100-egfr30-90 | >=100 mg/g | "UACR ≥100 mg/g" | ada-2026 | p261 | p261/recommendation/11.9 | B |
| sglt2-nsmra-egfr-range | adults-t2d-uacr100-egfr30-90 | 30-90 mL/min/1.73 m2 | "eGFR 30–90 mL/min/1.73 m2" | ada-2026 | p261 | p261/recommendation/11.9 | B |
| sglt2-continuation-egfr-threshold | people-egfr-under20-nondialysis | <20 mL/min/1.73 m2 | "eGFR <20 mL/min/1.73 m2" | ada-2026 | p262 | p262/recommendation/11.11 | B/C |
| cognitive-screening-age-threshold | adults-diabetes-age65plus | >=65 years | "65 years of age or older" | ada-2026 | p284 | p284/recommendation/13.3 | B |
| cognitive-screening-interval | adults-diabetes-age65plus | annually | "annually" | ada-2026 | p284 | p284/recommendation/13.3 | B |
| caregiver-dsmes-age-threshold | pediatric-diabetes | <18 years | "aged <18 years" | ada-2026 | p304 | p304/recommendation/14.1 | B |
| pregnancy-aspirin-dose | pregnancy-t1d-t2d | 100-150 mg/day | "100–150 mg/day" | ada-2026 | p336 | p336/recommendation/15.23 | E |
| pregnancy-aspirin-start | pregnancy-t1d-t2d | 12-16 weeks gestation | "12–16 weeks of gestation" | ada-2026 | p336 | p336/recommendation/15.23 | E |
| pregnancy-aspirin-alternative-dose | pregnancy-t1d-t2d | 162 mg/day | "162 mg/day" | ada-2026 | p336 | p336/recommendation/15.23 | E |
| scope-child-age-band | scope-children | birth-11 years | "aged birth to 11 years" | ada-2026 | p7 | p7/narrative/scope | narrative |
| scope-adolescent-age-band | scope-adolescents | 12-17 years | "aged 12–17 years" | ada-2026 | p7 | p7/narrative/scope | narrative |
| scope-adult-age-band | scope-adults | 18-64 years | "aged 18–64 years" | ada-2026 | p7 | p7/narrative/scope | narrative |
| scope-older-adult-age-threshold | scope-older-adults | >=65 years | "aged ≥65 years" | ada-2026 | p7 | p7/narrative/scope | narrative |
| weight-loss-level-associated-greater-disease-modifying-benefit-type | people-t2d | sustained weight loss of >10% | "Sustained loss of >10% of" | ada-2026 | p173 | p173/narrative/002 | narrative |
| early-response-supporting-continuation-chronic-obesity-pharmacotherapy | people-diabetes-overweight-obesity | >5% weight loss after 3 months of use | "fined as >5% weight loss after 3 months" | ada-2026 | p180 | p180/narrative/003 | narrative |
| safety-efficacy-monitoring-interval-after-starting-obesity-medication | people-diabetes-overweight-obesity | at least monthly for the first 3 months and at least quarterly thereafter | "monthly for the first 3 months and at least quarterly thereafter. Modeling from" | ada-2026 | p180 | p180/narrative/004 | narrative |
| age-threshold-highlighted-pad-screening-asymptomatic-diabetes | people-diabetes | aged >=65 years | "diabetes and age ≥65 years" | ada-2026 | p237 | p237/narrative/005 | narrative |
| diagnostic-threshold-diabetes-nonpregnant-individuals | nonpregnant-individuals | A1C >=6.5% (>=48 mmol/mol) | "A1C ≥6.5% (≥48 mmol/mol). The test" | ada-2026 | p34 | p34/narrative/008 | narrative |
| fasting-plasma-glucose-diagnostic-threshold-diabetes | nonpregnant-individuals | FPG >=126 mg/dL (>=7.0 mmol/L) | "FPG ≥126 mg/dL (≥7.0 mmol/L). Fasting is" | ada-2026 | p34 | p34/narrative/009 | narrative |
| defines-fasting-diagnostic-fasting-plasma-glucose | nonpregnant-individuals | no caloric intake for at least 8 h | "for at least 8 h.*" | ada-2026 | p34 | p34/narrative/010 | narrative |
| two-hour-oral-glucose-tolerance-diagnostic-threshold-diabetes | nonpregnant-individuals | 2-h PG >=200 mg/dL (>=11.1 mmol/L) during OGTT | "2-h PG ≥200 mg/dL (≥11.1 mmol/L) during OGTT." | ada-2026 | p34 | p34/narrative/011 | narrative |
| glucose-load-required-diagnostic-oral-glucose-tolerance-testing | nonpregnant-individuals | 75 g anhydrous glucose | "2-h PG during 75-g OGTT, and A1C" | ada-2026 | p34 | p34/narrative/012 | narrative |
| diagnostic-threshold-classic-hyperglycemic-symptoms-crisis-are-present | nonpregnant-individuals | random plasma glucose >=200 mg/dL (>=11.1 mmol/L) | "random plasma glucose ≥200 mg/dL [≥11.1 mmol/L]). In these" | ada-2026 | p34 | p34/narrative/013 | narrative |
| impaired-fasting-glucose-prediabetes-range | people-prediabetes | FPG 100-125 mg/dL (5.6-6.9 mmol/L) | "* IFG: FPG 100–125 mg/dL (5.6–6.9 mmol/L) or" | ada-2026 | p38 | p38/narrative/014 | narrative |
| impaired-glucose-tolerance-prediabetes-range-after-75-g-ogtt | people-prediabetes | 2-h PG 140-199 mg/dL (7.8-11.0 mmol/L) | "* IGT: 2-h PG 140–199 mg/dL (7.8–11.0 mmol/L) or" | ada-2026 | p38 | p38/narrative/015 | narrative |
| a1c-range-defining-prediabetes | people-prediabetes | A1C 5.7-6.4% (39-47 mmol/mol) | "* A1C 5.7–6.4% (39–47 mmol/mol)" | ada-2026 | p38 | p38/narrative/016 | narrative |
| repeat-antibody-testing-interval-single-confirmed-islet-autoantibody | people-diabetes | every 6 months to 3 years (depending on age) | "every 6 months for 3 years and then" | ada-2026 | p39 | p39/narrative/017 | narrative |
| routine-adult-screening-start-age-earlier-risk-based-testing | people-diabetes | screening should begin at age 35 years | "begin at age 35 years. B" | ada-2026 | p41 | p41/narrative/018 | narrative |
| minimum-repeat-diabetes-screening-interval-after-normal-screen | people-diabetes | at a minimum of 3-year intervals | "a minimum of 3-year intervals is reasonable" | ada-2026 | p41 | p41/narrative/019 | narrative |
| minimum-carbohydrate-intake-preparation-period-before-ogtt | people-diabetes | at least 150 g/day ; for 3 days prior to testing | "150 g/day) should be assured for 3 days prior to" | ada-2026 | p41 | p41/narrative/020 | narrative |
| start-point-risk-based-type-2-diabetes-screening-youth | pediatric-diabetes | after the onset of puberty or after 10 years of age, whichever occurs earlier | "berty or after 10 years of age" | ada-2026 | p41 | p41/narrative/021 | narrative |
| youth-overweight-threshold-used-diabetes-screening-eligibility | pediatric-diabetes | BMI >=85th percentile | "adolescents with overweight (BMI ≥ 85th percentile) or obesity (BMI ≥" | ada-2026 | p41 | p41/narrative/022 | narrative |
| youth-obesity-threshold-used-diabetes-screening-eligibility | pediatric-diabetes | BMI >=95th percentile | "85th percentile) or obesity (BMI ≥ 95th percentile) and who have one" | ada-2026 | p41 | p41/narrative/023 | narrative |
| diabetes-screening-schedule-second-generation-antipsychotics | people-diabetes | baseline and repeat 12-16 weeks after medication initiation ; and annually thereafter | "baseline and repeat 12–16 weeks after medication initiation or sooner, if clinically indicated, and annually thereafter. B" | ada-2026 | p41 | p41/narrative/024 | narrative |
| fasting-glucose-monitoring-schedule-people-hiv | people-hiv | 3-6 months, then annually | "3–6 months after starting or switching antiretroviral therapy. If initial screening results are normal, FPG should be checked annu­ ally" | ada-2026 | p41 | p41/narrative/025 | narrative |
| glucose-a1c-monitoring-schedule-during-pi3k-alpha-inhibitor-therapy | people-diabetes | weekly for the first 2 weeks ; every 4 weeks ; A1C every 3 months | "weekly for the first 2 weeks of treat­ ment and then every 4 weeks during treatment. C Consider testing A1C ev­ ery 3 months during treatment." | ada-2026 | p44 | p44/narrative/026 | narrative |
| glucose-a1c-monitoring-schedule-during-mtor-inhibitor-therapy | people-diabetes | at each visit ; A1C every 3 months | "ing A1C every 3 months during treat­" | ada-2026 | p44 | p44/narrative/027 | narrative |
| start-age-interval-cystic-fibrosis-related-diabetes-screening | people-cystic-fibrosis | Annual screening ; begin by age 10 years | "2.24a Annual screening for cystic fibrosis–related diabetes (CFRD) should begin by age 10 years in all" | ada-2026 | p45 | p45/narrative/029 | narrative |
| a1c-trigger-follow-up-interval-cystic-fibrosis-related-diabetes | people-cystic-fibrosis | A1C values between 5.5% and 6.4% ; OGTT within 3 months | "Individuals with A1C values between 5.5% and 6.4% (37 and 47 mmol/mol, respectively) should undergo an OGTT within 3 months. C An" | ada-2026 | p45 | p45/narrative/030 | narrative |
| a1c-diagnostic-threshold-consistent-cystic-fibrosis-related-diabetes | people-cystic-fibrosis | A1C value of >=6.5% (>=48 mmol/mol) | "months. C An A1C value of ≥6.5% (≥48 mmol/mol) is consistent" | ada-2026 | p45 | p45/narrative/031 | narrative |
| start-point-interval-complication-monitoring-cystic-fibrosis-related-diabetes | people-cystic-fibrosis | Beginning 5 years after the diagnosis of CFRD, annual monitoring | "2.25 Beginning 5 years after the di­ agnosis of CFRD, annual monitoring" | ada-2026 | p45 | p45/narrative/032 | narrative |
| trigger-neonatal-diabetes-genetic-testing | people-diabetes | diagnosed with diabetes in the first 6 months of life | "in the first 6 months of life" | ada-2026 | p47 | p47/narrative/033 | narrative |
| stable-mild-glycemia-pattern-supporting-consideration-monogenic-diabetes | people-diabetes | fasting hyperglycemia (100-150 mg/dL [5.6-8.5 mmol/L]) ; A1C between 5.6 and 7.6% | "mild fasting hyperglycemia (100–150 mg/dL [5.6–8.5 mmol/L]), stable A1C between 5.6 and 7.6%" | ada-2026 | p47 | p47/narrative/034 | narrative |
| timing-early-pregnancy-testing-undiagnosed-diabetes-abnormal-glucose-metabolism | pregnant-diabetes | Before 15 weeks of gestation | "2.31b Before 15 weeks of gestation" | ada-2026 | p48 | p48/narrative/035 | narrative |
| early-pregnancy-abnormal-glucose-metabolism-definition | pregnant-diabetes | A1C 5.9-6.4% [41-47 mmol/mol] or FPG 110-125 mg/dL [6.1-6.9 mmol/L] | "tabolism (defined as A1C 5.9–6.4% [41–47 mmol/mol] or FPG 110–125 mg/dL [6.1–6.9 mmol/L]) to identify" | ada-2026 | p48 | p48/narrative/036 | narrative |
| routine-gestational-diabetes-screening-window | pregnant-diabetes | 24-28 weeks of gestation | "for GDM at 24–28 weeks of gestation" | ada-2026 | p48 | p48/narrative/037 | narrative |
| postpartum-diabetes-screening-window-test-after-gestational-diabetes | history-gdm | 4-12 weeks postpartum ; 75-g OGTT | "or diabetes at 4–12 weeks postpartum, using the 75-g" | ada-2026 | p48 | p48/narrative/038 | narrative |
| lifelong-diabetes-screening-interval-after-gestational-diabetes | history-gdm | every 1-3 years | "tes every 1–3 years. B" | ada-2026 | p48 | p48/narrative/039 | narrative |
| minimum-diabetes-monitoring-interval-people-prediabetes | people-prediabetes | at least annually | "Standards of Care annually, or more frequently" | ada-2026 | p56 | p56/narrative/040 | narrative |
| monitoring-schedule-presymptomatic-type-1-diabetes | people-t1d | A1C approximately every 6 months and 75-g oral glucose tolerance test ; annually | "sion using A1C approximately every 6 months and 75-g oral glucose tolerance test (i.e., fasting and 2-h plasma glucose) annually; modify frequency of" | ada-2026 | p56 | p56/narrative/041 | narrative |
| weight-reduction-goal-diabetes-prevention-programs | people-prediabetes | at least 5-7% of initial body weight | "of at least 5–7% of initial body" | ada-2026 | p57 | p57/narrative/042 | narrative |
| physical-activity-goal-diabetes-prevention-programs | people-prediabetes | >=150 min/week of moderate-intensity physical activity | "tern and ≥150 min/week of mod­" | ada-2026 | p57 | p57/narrative/043 | narrative |
| age-bmi-profile-favoring-metformin-diabetes-prevention | people-prediabetes | aged 25-59 years with BMI >=35 kg/m2 | "25–59 years with BMI ≥35 kg/m2" | ada-2026 | p59 | p59/narrative/044 | narrative |
| higher-glycemia-profile-favoring-metformin-diabetes-prevention | people-prediabetes | FPG >=110 mg/dL [>=6 mmol/L] ; A1C >=6.0% [>=42 mmol/mol] | "≥110 mg/dL [≥6 mmol/L]), and higher A1C (e.g., ≥6.0% [≥42 mmol/mol])" | ada-2026 | p59 | p59/narrative/045 | narrative |
| bmi-marker-particularly-high-progression-risk-warranting-intensive-prevention | people-prediabetes | BMI >=35 kg/m2 | "individuals with BMI ≥35 kg/m2" | ada-2026 | p62 | p62/narrative/047 | narrative |
| glycemic-markers-particularly-high-diabetes-progression-risk | people-prediabetes | fasting plasma glucose 110-125 mg/dL ; 2-h postchallenge glucose 173-199 mg/dL ; A1C >=6.0% | "fasting plasma glucose 110–125 mg/dL [6.1–6.9 mmol/L], 2-h postchal­ lenge glucose 173–199 mg/dL [9.6– 11.0 mmol/L], and A1C ≥6.0%" | ada-2026 | p62 | p62/narrative/048 | narrative |
| follow-up-interval-comprehensive-medical-evaluation | people-diabetes | at least every 3-6 months ; and then at least annually | "at least every 3–6 months individual­ ized to the person and then at least annually." | ada-2026 | p69 | p69/narrative/049 | narrative |
| minimum-age-updated-covid-19-vaccination | people-diabetes | aged 6 months and older | "everyone aged 6 months and older" | ada-2026 | p70 | p70/narrative/050 | narrative |
| age-at-which-hepatitis-b-vaccination-becomes-discretionary-based | people-diabetes | adults aged >=60 years | "For adults aged ≥60 years" | ada-2026 | p70 | p70/narrative/051 | narrative |
| minimum-age-annual-influenza-vaccination | people-diabetes | >=6 months of age | "for all individuals ≥6 months of age" | ada-2026 | p71 | p71/narrative/052 | narrative |
| age-pregnancy-limits-live-attenuated-influenza-vaccine-chronic-condition | pregnant-diabetes | 2-49 years of age and are not pregnant | "2–49 years of age" | ada-2026 | p71 | p71/narrative/053 | narrative |
| eligibility-single-rsv-vaccine-dose | people-diabetes | all adults aged >=75 years and adults aged 60-74 years who are at increased risk | "all adults aged ≥75 years and adults aged 60–74 years who are" | ada-2026 | p71 | p71/narrative/054 | narrative |
| age-interval-dxa-bone-density-monitoring-older-adults-diabetes | adults-diabetes-age65plus | aged >=65 years ; every 2-3 years | "≥65 years) and younger individuals with diabetes and multiple risk factors every 2–3 years (Table 4.4)." | ada-2026 | p72 | p72/narrative/055 | narrative |
| calcium-intake-target-people-at-fracture-risk | people-diabetes | calcium (1,000-1,200 mg/day) | "intake of calcium (1,000–1,200 mg/day)" | ada-2026 | p72 | p72/narrative/056 | narrative |
| bone-density-threshold-supporting-osteoporosis-drug-therapy | people-diabetes | T-score <=-2.5 | "eral density (T-score ≤−2.5), history" | ada-2026 | p72 | p72/narrative/057 | narrative |
| frax-thresholds-supporting-osteoporosis-drug-therapy | people-diabetes | >=3% for hip fracture or >=20% for major osteoporotic fracture | "Assessment Tool score (≥3% for hip fracture or ≥20% for major osteoporotic" | ada-2026 | p72 | p72/narrative/058 | narrative |
| age-fracture-pattern-considered-diagnostic-osteoporosis-regardless-bmd | nonpregnant-individuals | low-trauma fracture ; in adults aged >=65 years | "in adults aged ≥65 years is diagnos­" | ada-2026 | p74 | p74/narrative/059 | narrative |
| glucocorticoid-exposure-used-as-bone-density-testing-risk-factor | people-diabetes | prednisone at doses >2.5 mg per day for >=3 months | "prednisone at doses >2.5 mg per day for ≥3 months" | ada-2026 | p75 | p75/narrative/060 | narrative |
| vitamin-d-target-people-receiving-antiresorptive-therapy | people-diabetes | 25-hydroxyvitamin D level of >30 ng/mL | "apy), a 25-hydroxyvitamin D level of >30 ng/mL has been" | ada-2026 | p76 | p76/narrative/061 | narrative |
| age-specific-daily-vitamin-d-allowances | people-diabetes | 600 IU for people aged 51-70 years and 800 IU for people aged >70 years | "vitamin D is 600 IU for people aged 51–70 years and 800 IU for people aged >70 years (59). In" | ada-2026 | p76 | p76/narrative/062 | narrative |
| required-dosing-interval-whose-disruption-risks-rebound-bone-loss | people-diabetes | every 6-month denosumab injection schedule | "every 6-month denosumab injection" | ada-2026 | p77 | p77/narrative/063 | narrative |
| duration-triggering-evaluation-other-liver-disease-causes-fib-4 | people-diabetes | persistently elevated plasma aminotransferase levels for >6 months | "aminotransferase levels for >6 months and low" | ada-2026 | p82 | p82/narrative/064 | narrative |
| threshold-additional-liver-fibrosis-risk-stratification | people-diabetes | FIB-4 >=1.3 | "prediabetes with a FIB-4 ≥ 1.3 should" | ada-2026 | p82 | p82/narrative/065 | narrative |
| high-risk-threshold-warranting-direct-liver-specialist-referral | people-diabetes | FIB-4 >2.67 | "If FIB-4 >2.67" | ada-2026 | p83 | p83/narrative/066 | narrative |
| higher-age-adjusted-fib-4-threshold-older-adults | adults-diabetes-age65plus | in diabetes >=65 years ; 1.9-2.0 rather than >=1.3 | "with diabetes ≥65 years of age, higher cutoffs for FIB-4 have been recommended (1.9–2.0 rather than ≥1.3) (217). In some" | ada-2026 | p83 | p83/narrative/067 | narrative |
| transient-elastography-level-indicating-lower-advanced-fibrosis-risk | people-diabetes | LSM <8.0 kPa | "value of <8.0 kPa has a" | ada-2026 | p83 | p83/narrative/068 | narrative |
| follow-up-interval-after-low-risk-liver-stiffness-result | people-diabetes | repeat surveillance testing every >=2 years | "testing ev­ ery ≥2 years, although the" | ada-2026 | p83 | p83/narrative/069 | narrative |
| liver-stiffness-threshold-warranting-hepatology-referral | people-diabetes | LSM >=8.0 kPa | "Is LSM ≥8.0 kPa* ?" | ada-2026 | p83 | p83/narrative/070 | narrative |
| elf-thresholds-separating-lower-from-high-advanced-fibrosis-risk | people-diabetes | ELF <9.8 ; ELF >=9.8 | "with ELF <9.8 are considered at low risk for adverse liver outcomes. Individuals with ELF ≥9.8 are considered at" | ada-2026 | p83 | p83/narrative/071 | narrative |
| intermediate-elf-range-that-may-require-more-frequent-repeat | people-diabetes | ELF ; between 9.2 and 9.7 | "ELF is between 9.2 and 9.7." | ada-2026 | p84 | p84/narrative/072 | narrative |
| weight-loss-needed-liver-histology-improvement-larger-loss-favored | people-diabetes-overweight-obesity | minimum weight loss goal of 5%, preferably >=10% | "loss goal of 5%, preferably ≥10%, is needed to" | ada-2026 | p84 | p84/narrative/073 | narrative |
| critical-times-provide-reassess-diabetes-self-management-education-support | nonpregnant-individuals | at diagnosis, annually ; when not meeting treatment goals ; and when transitions ; occur | "DSMES at diagnosis, annually and/or when not" | ada-2026 | p95 | p95/narrative/074 | narrative |
| weight-loss-aim-overweight-obesity-treatment-plan | people-diabetes-overweight-obesity | at least 5-7% weight loss | "for at least 5–7% weight loss. A" | ada-2026 | p99 | p99/narrative/075 | narrative |
| recommended-sodium-intake-ceiling | people-diabetes | <2,300 mg/day | "sodium consumption to <2,300 mg/day, as clinically" | ada-2026 | p99 | p99/narrative/076 | narrative |
| dietary-fiber-density-target | people-diabetes | at least 14 g fiber per 1,000 kcal | "carbohydrate (at least 14 g ﬁber per 1,000 kcal). B" | ada-2026 | p99 | p99/narrative/077 | narrative |
| daily-alcohol-ceiling | people-diabetes | <=2 drinks a day for men or <=1 drink a day for women | "iting intake to ≤2 drinks a day for men or ≤1 drink a day" | ada-2026 | p104 | p104/narrative/078 | narrative |
| defines-one-alcoholic-drink | people-diabetes | 12-oz beer, a 5-oz glass of wine, or 1.5 oz of distilled spirits | "equal to a 12-oz beer, a 5-oz glass of wine, or 1.5 oz of distilled" | ada-2026 | p104 | p104/narrative/079 | narrative |
| medication-assisted-weight-loss-goal-people-at-risk-type | people-t2d | 7-10% weight loss | "achieve and sustain 7–10% weight loss (185,186)" | ada-2026 | p104 | p104/narrative/080 | narrative |
| maximum-uninterrupted-sitting-interval | people-diabetes | interrupted at least every 30 min | "at least every 30 min for blood" | ada-2026 | p108 | p108/narrative/081 | narrative |
| youth-aerobic-strengthening-activity-targets | pediatric-diabetes | 60 min/day ; muscle-strengthening and bone-strengthening ; at least 3 days/week | "to engage in 60 min/day or more of moderate- or vigorous-in- tensity aerobic activity, with muscle- strengthening and bone-strengthen- ing activities at least 3 days/week" | ada-2026 | p108 | p108/narrative/082 | narrative |
| adult-aerobic-activity-target-distribution | people-diabetes | 150 min or more ; per week, spread over at least 3 days/week, with no more than 2 consecutive days without activity | "engage in 150 min or more of mod- erate- to vigorous-intensity aerobic activity per week, spread over at least 3 days/week, with no more than 2 con- secutive days" | ada-2026 | p108 | p108/narrative/083 | narrative |
| alternative-vigorous-activity-duration-more-physically-fit-adults | people-diabetes | minimum 75 min/week | "durations (minimum 75 min/week) of" | ada-2026 | p108 | p108/narrative/084 | narrative |
| adult-resistance-exercise-frequency | people-diabetes | 2-3 sessions/week ; on nonconsecutive days | "in 2–3 sessions/week of resistance" | ada-2026 | p108 | p108/narrative/085 | narrative |
| flexibility-balance-training-frequency-most-older-adults | adults-diabetes-age65plus | 2-3 times/week | "and balance training 2–3 times/ week. C" | ada-2026 | p108 | p108/narrative/086 | narrative |
| suggested-glyburide-adjustment-during-religious-fasting | people-diabetes | reduce dose by 50% | "reduce dose by 50%." | ada-2026 | p109 | p109/narrative/087 | narrative |
| suggested-basal-insulin-adjustment-during-religious-fasting | people-diabetes | Reduce dose by 25-35% | "Reduce dose by 25–35% if not well" | ada-2026 | p109 | p109/narrative/088 | narrative |
| suggested-prandial-mixed-insulin-reduction-meal-followed-by-fasting | people-diabetes | Reduce dose ; 35-50% | "followed by fasting (35–50%)." | ada-2026 | p109 | p109/narrative/089 | narrative |
| recommended-recreational-screen-time-ceiling-children-adolescents | pediatric-diabetes | less than 2 h per day | "than 2 h per day" | ada-2026 | p110 | p110/narrative/090 | narrative |
| level-prompting-carbohydrate-insulin-precautions-before-exercise | people-diabetes | pre-exercise glucose levels are <90 mg/dL (<5.0 mmol/L) | "glucose levels are <90 mg/dL (<5.0 mmol/L), depending on" | ada-2026 | p112 | p112/narrative/091 | narrative |
| diagnostic-criteria-proposed-hyperglycemic-ketosis-cannabis-hyperemesis-syndrome | nonpregnant-individuals | blood glucose >=250 mg/dL ; anion gap >10 ; beta-hydroxybutyrate >0.6 mmol/L ; pH >=7.4 ; bicarbonate >=15 mmol/L | "glucose of ≥250 mg/dL, an anion gap of >10, a serum β-hydroxybutyrate level of >0.6 mmol/L, a pH level of ≥7.4, and a bicarbonate level of ≥15 mmol/L (363)." | ada-2026 | p114 | p114/narrative/092 | narrative |
| psychosocial-screening-interval-event-triggers | people-diabetes | at least annually or when there is a change in health status, treatment, or life circumstances | "annually or when there" | ada-2026 | p115 | p115/narrative/093 | narrative |
| anxiety-fear-hypoglycemia-screening-interval | people-diabetes | at least annually | "poglycemia at least annually and when" | ada-2026 | p117 | p117/narrative/095 | narrative |
| depression-screening-interval | people-diabetes | at least annually and more frequently among those with a history of depression | "annually and more frequently" | ada-2026 | p118 | p118/narrative/096 | narrative |
| monitoring-interval-glycemia-weight-lipids-second-generation-antipsychotics | people-diabetes | every 12-16 weeks | "monitored every 12–16 weeks, unless clin-" | ada-2026 | p121 | p121/narrative/097 | narrative |
| glycemic-assessment-interval-stable-versus-not-at-goal-recently | people-diabetes | at least two times a year ; every 3 months | "frequently (e.g., every 3 months) for individuals" | ada-2026 | p138 | p138/narrative/098 | narrative |
| minimum-cgm-data-duration-completeness-glycemic-assessment | people-diabetes | 10- to 14-day CGM assessment ; wear of 70% or higher | "glycemic status. A 10- to 14-day CGM assessment of TIR, with CGM wear of 70% or higher, and" | ada-2026 | p140 | p140/narrative/099 | narrative |
| general-glycemic-goal-many-nonpregnant-adults | nonpregnant-individuals | A1C goal of <7% (<53 mmol/mol) | "6.3a An A1C goal of <7% (<53 mmol/" | ada-2026 | p141 | p141/narrative/100 | narrative |
| general-cgm-time-range-goal-many-nonpregnant-adults | nonpregnant-individuals | goal time in range of >70% | "in range of >70% in" | ada-2026 | p141 | p141/narrative/101 | narrative |
| cgm-hypoglycemia-exposure-limits | adults-diabetes-age65plus | time <70 mg/dL ; <4% (or <1% for older adults) ; time <54 mg/dL ; <1% | "goal percent time <70 mg/dL (<3.9 mmol/L) of <4% (or <1% for older adults) and a goal percent time <54 mg/dL (<3.0 mmol/L) of <1% are" | ada-2026 | p141 | p141/narrative/102 | narrative |
| example-lower-glycemic-goal-healthy-low-risk-individuals | people-diabetes | A1C ; <6.5% [<48 mmol/mol] | "6.4 Lower A1C goals (e.g., <6.5% [<48 mmol/mol]) may be" | ada-2026 | p141 | p141/narrative/103 | narrative |
| capillary-glucose-goals-many-nonpregnant-adults | nonpregnant-individuals | Preprandial ; 80-130 mg/dL ; Peak postprandial ; <180 mg/dL | "capillary plasma glucose 80–130 mg/dL* (4.4–7.2 mmol/L) Peak postprandial capillary plasma glucose‡ <180 mg/dL* (<10.0 mmol/L)" | ada-2026 | p141 | p141/narrative/104 | narrative |
| timing-postprandial-glucose-measurement | people-diabetes | 1-2 h after the beginning of the meal | "should be made 1–2 h after the" | ada-2026 | p141 | p141/narrative/105 | narrative |
| example-less-stringent-goal-complex-health-limited-life-expectancy | people-diabetes | A1C up to 8% [64 mmol/mol] | "stringent goals (e.g., A1C up to 8% [64 mmol/mol]) may be" | ada-2026 | p144 | p144/narrative/106 | narrative |
| impaired-awareness-fear-hypoglycemia-screening-interval | people-diabetes | at least annually | "hypoglycemia at least annually and" | ada-2026 | p144 | p144/narrative/107 | narrative |
| hypoglycemia-treatment-trigger-repeat-treatment-interval | people-diabetes | glucose <70 mg/dL ; Fifteen minutes after initial treatment, repeat | "glucose <70 mg/dL (<3.9 mmol/L)" | ada-2026 | p144 | p144/narrative/108 | narrative |
| level-1-hypoglycemia-classification | people-diabetes | Level 1 Glucose <70 mg/dL ; and >=54 mg/dL | "Level 1 Glucose <70 mg/dL (<3.9 mmol/L) and ≥54 mg/dL (≥3.0 mmol/L)" | ada-2026 | p145 | p145/narrative/109 | narrative |
| level-2-hypoglycemia-classification-requiring-immediate-action | people-diabetes | Level 2 Glucose <54 mg/dL | "Level 2 Glucose <54 mg/dL (<3.0 mmol/L)" | ada-2026 | p145 | p145/narrative/110 | narrative |
| recency-window-making-level-2-3-hypoglycemia-major-future | people-diabetes | within the past 3-6 months | "(within the past 3–6 months)" | ada-2026 | p146 | p146/narrative/111 | narrative |
| age-counted-among-hypoglycemia-risk-factors | people-diabetes | Age >=75 years | "• Age ≥75 years†" | ada-2026 | p146 | p146/narrative/112 | narrative |
| usual-initial-oral-carbohydrate-treatment-hypoglycemia | people-diabetes | 15 g carbohydrates | "For most individuals, 15 g carbohydrates" | ada-2026 | p147 | p147/narrative/113 | narrative |
| typical-lower-carbohydrate-treatment-amount-automated-insulin-delivery | people-diabetes | 5-10 g carbohydrates | "cally ingest 5–10 g carbohydrates unless" | ada-2026 | p147 | p147/narrative/114 | narrative |
| glucose-level-strengthening-indication-measure-ketones-at-risk-people | people-diabetes | glucose levels exceed 200 mg/dL (11.1 mmol/L) | "els exceed 200 mg/dL (11.1 mmol/L). Use" | ada-2026 | p149 | p149/narrative/115 | narrative |
| acetaminophen-cgm-interference-threshold | people-diabetes | >4 g/day | "Acetaminophen >4 g/day" | ada-2026 | p162 | p162/narrative/116a | narrative |
| ascorbic-acid-cgm-interference-threshold | people-diabetes | >500 mg/day | "Ascorbic acid (vitamin C), >500 mg/day" | ada-2026 | p162 | p162/narrative/116b | narrative |
| ascorbic-acid-plus-cgm-interference-threshold | people-diabetes | >1,000 mg/day | "Ascorbic acid (vitamin C), >1,000 mg/day" | ada-2026 | p162 | p162/narrative/116c | narrative |
| typical-use-duration-insulin-pens-after-first-use-depending | people-diabetes | usually for 28 days, ranging from 14 to 56 days | "usually for 28 days, ranging from 14 to 56 days. Needle thickness" | ada-2026 | p163 | p163/narrative/117 | narrative |
| bmi-ranges-classifying-overweight-obesity-classes-1-3 | people-diabetes-overweight-obesity | BMI 25-29.9 ; 30-34.9 ; 35-39.9 ; >=40 kg/m2 | "obesity (overweight: BMI 25–29.9 kg/m2; obesity class 1: BMI 30–34.9 kg/m2; obesity class 2: BMI 35–39.9 kg/m2; obesity class 3: BMI ≥40 kg/m2). Despite its" | ada-2026 | p173 | p173/narrative/118 | narrative |
| anthropometric-monitoring-interval-routinely-during-active-weight-treatment | people-diabetes | at least annually ; at least every 3 months | "least annually to aid the diagnosis of obe­ sity. More frequent assessments (at least every 3 months) should be" | ada-2026 | p173 | p173/narrative/119 | narrative |
| high-frequency-counseling-intensity-effective-lifestyle-weight-intervention | people-diabetes | >=16 sessions in 6 months | "frequency of counseling (≥16 ses­ sions in 6 months) with focus" | ada-2026 | p174 | p174/narrative/120 | narrative |
| recommended-energy-deficit-weight-loss | people-diabetes-overweight-obesity | 500-750 kcal/day energy deficit | "a 500–750 kcal/day energy deficit" | ada-2026 | p174 | p174/narrative/121 | narrative |
| weight-maintenance-program-duration | people-diabetes-overweight-obesity | >=1 year | "long-term (≥1 year) weight mainte­ nance programs" | ada-2026 | p174 | p174/narrative/122a | narrative |
| weight-maintenance-contact-interval | people-diabetes-overweight-obesity | monthly | "provide monthly contact and support" | ada-2026 | p174 | p174/narrative/122b | narrative |
| weight-maintenance-activity-target | people-diabetes-overweight-obesity | 200-300 min/week | "regular physical activity (200–300 min/week)" | ada-2026 | p174 | p174/narrative/122c | narrative |
| very-low-calorie-meal-range-reserved-selected-closely-monitored | people-diabetes | 800-1,000 kcal/day | "(800–1,000 kcal/day) should be" | ada-2026 | p174 | p174/narrative/123 | narrative |
| usual-maximum-short-term-duration-intensive-very-low-calorie | people-diabetes | generally up to 3 months | "(generally up to 3 months)." | ada-2026 | p175 | p175/narrative/124 | narrative |
| weight-loss-thresholds-prompting-micronutrient-deficiency-screening | people-diabetes-overweight-obesity | significant (>20%) or rapid (>4% per month) weight loss | "ing significant (>20%) or rapid (>4% per month) weight" | ada-2026 | p175 | p175/narrative/125 | narrative |
| eligibility-threshold-fda-approved-obesity-medications | people-diabetes-overweight-obesity | BMI >=30 kg/m2 or >=27 kg/m2 with one or more obesity-associated comorbid conditions | "individuals with BMI ≥30 kg/m2 or ≥27 kg/m2 with one or" | ada-2026 | p177 | p177/narrative/126 | narrative |
| duration-added-nonoral-contraception-tirzepatide | people-diabetes | for 4 weeks after initiation and for 4 weeks after each dose escalation | "of contraception for 4 weeks after initiation and for 4 weeks after each" | ada-2026 | p177 | p177/narrative/127 | narrative |
| example-insulin-reductions-adding-glp-1-dual-gip-glp | people-diabetes | reduce bolus by 10-20%, basal approximately 10% if A1C <7.5% | "reduce bolus by 10–20%, basal ∼10% if A1C <7.5% [58 mmol/mol]). The" | ada-2026 | p180 | p180/narrative/128 | narrative |
| obesity-medication-effectiveness-safety-review-schedule | people-diabetes-overweight-obesity | at least monthly for the first 3 months and at least quarterly thereafter | "monthly for the first 3 months and at least quarterly thereafter. Modeling from" | ada-2026 | p180 | p180/narrative/129 | narrative |
| typical-early-response-boundary-informing-continuation-versus-reassessment-obesity | people-diabetes-overweight-obesity | >5% weight loss after 3 months ; <5% weight loss after 3 months | "fined as >5% weight loss after 3 months of use) should continue the medication long-term. When early weight loss results are modest (typically <5% weight loss after 3 months of use)" | ada-2026 | p180 | p180/narrative/130 | narrative |
| bmi-threshold-considering-metabolic-surgery-type-2-diabetes | people-t2d | BMI >=30.0 kg/m2 (or >=27.5 kg/m2 in Asian American individuals) | "betes with BMI ≥30.0 kg/m2 (or ≥27.5 kg/m2 in Asian American" | ada-2026 | p181 | p181/narrative/131 | narrative |
| monitoring-interval-inadequate-loss-weight-recurrence-after-metabolic-surgery | people-diabetes-overweight-obesity | at least every 6-12 months | "at least every 6–12 months. E In" | ada-2026 | p181 | p181/narrative/132 | narrative |
| regular-reassessment-interval-insulin-taking-behavior-treatment-plans | people-diabetes | every 3-6 months | "ular intervals (every 3–6 months)." | ada-2026 | p193 | p193/narrative/133 | narrative |
| typical-total-daily-insulin-requirement-range-type-1-diabetes | people-t1d | 0.4 to 1 unit/kg/day | "doses ranging from 0.4 to 1 unit/" | ada-2026 | p193 | p193/narrative/134 | narrative |
| typical-stable-adult-type-1-diabetes-starting-dose-basal | people-t1d | 0.5 units/kg/day ; approximately one-half ; prandial ; remaining ; basal | "notes 0.5 units/kg/day as a" | ada-2026 | p193 | p193/narrative/135 | narrative |
| typical-initial-insulin-range-newly-diagnosed-type-1-diabetes | people-t1d | 0.2 to 0.6 units/kg/day | "typically range from 0.2 to 0.6 units/kg/day, with lower" | ada-2026 | p193 | p193/narrative/136 | narrative |
| medication-plan-adherence-reevaluation-interval-type-2-diabetes | people-t2d | every 3-6 months | "3–6 months) and adjusted" | ada-2026 | p198 | p198/narrative/137 | narrative |
| very-high-glycemia-prompting-consideration-insulin-initiation | people-diabetes | A1C >10% ; or blood glucose >=300 mg/dL | "very high (i.e., A1C >10% [>86 mmol/mol] or blood glucose ≥300 mg/dL [≥16.7 mmol/L])." | ada-2026 | p198 | p198/narrative/138 | narrative |
| sglt2-inhibitor-preoperative-withholding-interval | people-diabetes | discontinue before scheduled surgery (e.g., 3-4 days) | "uled surgery (e.g., 3–4" | ada-2026 | p199 | p199/narrative/139 | narrative |
| level-at-which-dual-therapy-more-potent-agent-is | people-diabetes | A1C is >=1.5% above the individualized glycemic goal | "When A1C is ≥1.5% above the indi­" | ada-2026 | p203 | p203/narrative/140 | narrative |
| basal-insulin-initiation-dose-type-2-diabetes | people-t2d | Start 10 units per day or 0.1-0.2 units/kg per day | "these are not 0.1–0.2 units/ For hypoglycemia: determine cause; if no clear reason, lower dose by 10–20%" | ada-2026 | p204 | p204/narrative/141 | narrative |
| example-basal-insulin-titration-step-interval | people-diabetes | increase 2 units every 3 days | "algorithm, e.g., increase 2 units every 3 days to" | ada-2026 | p204 | p204/narrative/142 | narrative |
| insulin-dose-reduction-unexplained-hypoglycemia-occurs | people-diabetes | lower dose by 10-20% | "corresponding dose by 10–20%" | ada-2026 | p204 | p204/narrative/143 | narrative |
| kidney-function-threshold-avoiding-lixisenatide-exenatide | people-diabetes-ckd | eGFR <=30 mL/min/1.73 m2 | "uals with eGFR ≤30 mL/min/1.73 m2 or" | ada-2026 | p205 | p205/narrative/144 | narrative |
| metformin-kidney-function-initiation-dose-reduction-stopping-thresholds | people-diabetes-ckd | metformin should not be started ; eGFR <45 ; reduced once eGFR is <45 ; stopped once eGFR is <30 | "whose eGFR is <45 mL/min/1.73 m2. For those already treated with metformin, the dose of metformin should be reduced once eGFR is <45 mL/min/1.73 m2 and should be stopped once eGFR is <30" | ada-2026 | p205 | p205/narrative/145 | narrative |
| signal-prompting-assessment-insulin-overbasalization | people-diabetes | bedtime-to-morning glucose differential >=50 mg/dL | "bedtime-to-morning glucose differential ≥50 mg/dL [≥2.8 mmol/L])" | ada-2026 | p207 | p207/narrative/146 | narrative |
| suggested-starting-prandial-insulin-dose-at-largest-meal | people-diabetes | 4 units or 10% of the amount of basal insulin | "insulin dose of 4 units or 10% of the amount" | ada-2026 | p207 | p207/narrative/147 | narrative |
| duration-on-tirzepatide-maintenance-dose-before-ending-backup-contraception | people-diabetes | at least 4 weeks | "least 4 weeks (242)." | ada-2026 | p212 | p212/narrative/148 | narrative |
| level-at-which-basal-insulin-should-be-considered-during | people-diabetes | blood glucose >250 mg/dL | "with blood glucose >250 mg/dL while further" | ada-2026 | p212 | p212/narrative/149 | narrative |
| definition-elevated-blood-pressure | people-diabetes | 120-129 mmHg with ; <80 mmHg | "blood pressure 120–129 mmHg and diastolic blood pressure <80 mmHg)" | ada-2026 | p223 | p223/narrative/150 | narrative |
| definition-hypertension | people-diabetes | >=130 mmHg or ; >=80 mmHg | "≥130 mmHg or a diastolic blood pres­ sure ≥80 mmHg based on" | ada-2026 | p223 | p223/narrative/151 | narrative |
| blood-pressure-measurement-interval | people-diabetes | every routine clinical visit, or at least every 6 months | "at least every 6 months. Individuals found" | ada-2026 | p223 | p223/narrative/152 | narrative |
| measurement-requirement-diagnose-hypertension | people-diabetes | average of two or more measurements obtained on two or more occasions | "of two or more measurements obtained on two or more occasions. A Individuals" | ada-2026 | p223 | p223/narrative/153 | narrative |
| level-permitting-hypertension-diagnosis-at-single-visit | nonpregnant-individuals | blood pressure >=180/110 mmHg and cardiovascular disease | "with blood pressure ≥180/110 mmHg and cardiovascular" | ada-2026 | p223 | p223/narrative/154 | narrative |
| general-treated-blood-pressure-goal-encouraged-systolic-goal-high | people-diabetes-ckd | <130/80 mmHg ; systolic ; <120 mmHg | "<130/80 mmHg; a systolic blood pressure goal <120 mmHg should" | ada-2026 | p224 | p224/narrative/155 | narrative |
| office-blood-pressure-threshold-pharmacologic-therapy | people-diabetes | >=130/80 mmHg | "office-based blood pressure ≥130/ 80 mmHg, pharmacologic therapy" | ada-2026 | p227 | p227/narrative/157 | narrative |
| threshold-prompt-initiation-two-antihypertensive-agents | people-diabetes | >=150/90 mmHg | "based blood pressure ≥150/90 mmHg" | ada-2026 | p227 | p227/narrative/158 | narrative |
| electrolyte-monitoring-interval-after-starting-changing-diuretic | people-diabetes | 7-14 days after initiation or after a dose change | "routine visits and 7–14 days after ini­" | ada-2026 | p227 | p227/narrative/159 | narrative |
| lipid-monitoring-schedule-after-lipid-lowering-treatment-starts-changes | people-diabetes | 4-12 weeks after initiation or a change in dose, and annually thereafter | "therapy, 4–12 weeks after initiation or a change in dose, and annually there­" | ada-2026 | p229 | p229/narrative/160 | narrative |
| lipid-assessment-interval-younger-adults-not-otherwise-needing-more | people-diabetes | at least every 5 years ; <40 years of age | "at least every 5 years thereafter in indi­ viduals <40 years of age." | ada-2026 | p229 | p229/narrative/161 | narrative |
| age-range-routine-primary-prevention-statin-therapy-diabetes | people-diabetes | aged 40-75 years | "40–75 years without ASCVD" | ada-2026 | p229 | p229/narrative/162 | narrative |
| age-risk-group-which-statin-initiation-may-be-reasonable | people-diabetes | aged 20-39 years with additional ASCVD risk factors | "20–39 years with additional" | ada-2026 | p229 | p229/narrative/163 | narrative |
| high-risk-primary-prevention-ldl-reduction-level-goals | people-diabetes | LDL cholesterol by >=50% ; goal of <70 mg/dL | "LDL cholesterol by ≥50% of baseline and to obtain an LDL cholesterol goal of <70 mg/dL" | ada-2026 | p229 | p229/narrative/164 | narrative |
| age-threshold-individualized-initiation-continuation-statin-therapy | people-diabetes | aged >75 years | ">75 years, it may" | ada-2026 | p229 | p229/narrative/165 | narrative |
| secondary-prevention-ldl-reduction-level-goals-ascvd | people-diabetes | LDL ; >=50% ; goal of <55 mg/dL | "≥50% from baseline and an LDL cholesterol goal of <55 mg/dL (<1.4" | ada-2026 | p229 | p229/narrative/166 | narrative |
| threshold-prompting-secondary-cause-evaluation-pancreatitis-prevention-therapy-consideration | people-diabetes | fasting triglyceride levels >=500 mg/dL | "triglyc­ eride levels ≥500 mg/dL (≥5.7 mmol/L)" | ada-2026 | p233 | p233/narrative/167 | narrative |
| hypertriglyceridemia-thresholds-prompting-treatment-lifestyle-secondary-factors | people-diabetes | fasting >150 mg/dL or nonfasting >175 mg/dL | "mia (fasting triglycerides >150 mg/dL [>1.7 mmol/L] or nonfasting triglycer­ ides >175 mg/dL [>2.0 mmol/L])" | ada-2026 | p233 | p233/narrative/168 | narrative |
| triglyceride-range-which-icosapent-ethyl-may-be-considered-on | people-diabetes | 150-499 mg/dL | "vated triglycerides (150–499 mg/dL" | ada-2026 | p233 | p233/narrative/169 | narrative |
| severe-triglyceride-level-strengthening-need-drug-therapy-dietary-fat | people-diabetes | especially >1,000 mg/dL | "mmol/L] and especially >1,000 mg/dL" | ada-2026 | p234 | p234/narrative/170 | narrative |
| aspirin-dose-range-secondary-prevention-selected-primary-prevention | people-diabetes | aspirin therapy (75-162 mg/day) | "10.36 Aspirin therapy (75–162 mg/day)" | ada-2026 | p235 | p235/narrative/171 | narrative |
| dose-ascvd-aspirin-allergy | people-diabetes | clopidogrel (75 mg/day) | "dogrel (75 mg/day) should be" | ada-2026 | p235 | p235/narrative/172 | narrative |
| combination-regimen-selected-stable-coronary-pad-patients-low-bleeding | people-diabetes | 81 mg aspirin daily plus 2.5 mg rivaroxaban twice daily | "Combination therapy with 81 mg aspirin daily plus 2.5 mg rivaroxa­ ban twice daily should be considered" | ada-2026 | p235 | p235/narrative/173 | narrative |
| age-risk-profile-considering-primary-prevention-aspirin | people-diabetes | aged >=50 years ; at least one additional major risk factor | "and women aged ≥50 years with diabe­" | ada-2026 | p235 | p235/narrative/174 | narrative |
| age-criterion-pad-screening-ankle-brachial-index-results-would | people-diabetes | age >=65 years | "diabetes and age ≥65 years" | ada-2026 | p237 | p237/narrative/175 | narrative |
| age-risk-threshold-ace-inhibitor-arb-cardiovascular-prevention | people-diabetes | aged >=55 years with established ASCVD or multiple ASCVD risk factors | "aged ≥55 years with established" | ada-2026 | p237 | p237/narrative/176 | narrative |
| abnormal-biomarker-thresholds-used-heart-failure-screening | people-diabetes | BNP >=50 pg/mL and NT-proBNP >=125 pg/mL | "level ≥50 pg/mL and NT-proBNP level ≥125 pg/mL. Use clinical" | ada-2026 | p238 | p238/narrative/177 | narrative |
| kidney-function-component-ckd-diagnosis | people-diabetes-ckd | eGFR <60 mL/min/1.73 m2 | "ﬁltration rate (eGFR) <60 mL/min/1.73 m2" | ada-2026 | p252 | p252/narrative/178 | narrative |
| kidney-screening-start-point-interval | people-diabetes-ckd | at least annually ; type 1 diabetes duration >=5 years ; all type 2 diabetes | "(eGFR) at least annually in people with type 1 diabetes with duration of ≥5 years and in all people with type 2 diabetes regardless of" | ada-2026 | p252 | p252/narrative/179 | narrative |
| ckd-monitoring-frequency-based-on-stage | people-diabetes-ckd | 1-4 times per year | "UACR) and eGFR 1–4 times per year" | ada-2026 | p252 | p252/narrative/180 | narrative |
| normal-mild-moderate-severe-albuminuria-categories | people-diabetes-ckd | <30 ; >=30 to <300 ; >=300 mg/g creatinine | "<30 mg/g creatinine, moderately ele- vated albuminuria is deﬁned as ≥30 to <300 mg/g creatinine, and severely ele- vated albuminuria is deﬁned as ≥300 mg/g creatinine. However" | ada-2026 | p253 | p253/narrative/181 | narrative |
| confirmation-requirement-albuminuria | people-diabetes-ckd | two of three specimens ; within a 3- to 6-month period | "collected within a 3- to 6-month period should be" | ada-2026 | p253 | p253/narrative/182 | narrative |
| laboratory-monitoring-intervals-by-advanced-ckd-stage | people-diabetes-ckd | every 6-12 months for stage G3 ; every 3-5 months for stage G4 ; every 1-3 months for stage G5 | "generally indicated every 6–12 months for stage G3 CKD, every 3–5 months for stage G4 CKD, and every 1–3 months for stage G5 CKD, or as" | ada-2026 | p255 | p255/narrative/184 | narrative |
| high-protein-intake-avoid-ckd | people-diabetes-ckd | >20% of daily calories ; or >1.3 g/kg/day | "tein intake (>20% of daily calories from protein or >1.3 g/kg/day) have" | ada-2026 | p256 | p256/narrative/187 | narrative |
| serum-creatinine-rise-within-which-renin-angiotensin-blockade-should | people-diabetes | <=30% | "in serum creatinine (≤30%) in" | ada-2026 | p257 | p257/narrative/188 | narrative |
| kidney-function-threshold-initiate-sglt2-inhibitor-ckd-benefit | people-diabetes-ckd | eGFR >=20 mL/min/1.73 m2 | "≥20 mL/min/1.73 m2 but can safely" | ada-2026 | p258 | p258/narrative/189 | narrative |
| range-requiring-temporary-metformin-discontinuation-iodinated-contrast-procedures | people-diabetes-ckd | eGFR 30-60 mL/min/1.73 m2 | "individuals with eGFR 30–60 mL/min/ 1.73 m2." | ada-2026 | p259 | p259/narrative/190 | narrative |
| kidney-function-threshold-nephrology-referral | people-diabetes-ckd | eGFR <30 mL/min/1.73 m2 | "(eGFR <30 mL/min/1.73 m2) has been" | ada-2026 | p263 | p263/narrative/194 | narrative |
| timing-initial-dilated-eye-exam-adult-type-1-diabetes | people-t1d | 5 years after the onset of diabetes | "mologist or optometrist 5 years after the" | ada-2026 | p268 | p268/narrative/195 | narrative |
| eye-screening-interval-after-normal-exams-goal-glycemia | people-diabetes | every 1-2 years | "1–2 years may be" | ada-2026 | p268 | p268/narrative/196 | narrative |
| eye-examination-interval-any-diabetic-retinopathy-is-present | people-diabetes | at least annually | "repeated at least annually" | ada-2026 | p268 | p268/narrative/197 | narrative |
| retinopathy-monitoring-period-during-after-pregnancy-indicated | history-gdm | every trimester and for 1 year postpartum | "trimester and for 1 year postpartum as" | ada-2026 | p268 | p268/narrative/198 | narrative |
| typical-initial-anti-vegf-dosing-interval-center-involved-diabetic | people-diabetes | every 4-8 weeks during the first 12 months | "anti-VEGF agents every 4–8 weeks dur- ing the ﬁrst 12 months of treatment" | ada-2026 | p270 | p270/narrative/199 | narrative |
| extended-dosing-interval-achievable-faricimab-aflibercept-8-mg | people-diabetes | up to every 16 weeks | "up to every 16 weeks (50,51). For" | ada-2026 | p270 | p270/narrative/200 | narrative |
| neuropathy-screening-start-points-interval | people-t1d | starting at diagnosis of type 2 diabetes and 5 years after ; type 1 diabetes and at least annually thereafter | "diagnosis of type 2 diabetes and 5 years after the diagnosis of type 1 diabetes and at least annually thereafter. B" | ada-2026 | p271 | p271/narrative/201 | narrative |
| foot-sensory-screening-interval-monofilament-force | people-diabetes | annual 10-g monofilament testing | "have annual 10-g monoﬁlament testing" | ada-2026 | p271 | p271/narrative/202 | narrative |
| resting-tachycardia-orthostatic-blood-pressure-changes-supporting-autonomic-neuropathy | people-diabetes | >100 bpm ; fall ; >20 mmHg or >10 mmHg | "dia (>100 bpm) and orthostatic hypoten- sion (a fall in systolic or diastolic blood pressure by >20 mmHg or >10 mmHg" | ada-2026 | p271 | p271/narrative/203 | narrative |
| gastric-emptying-scintigraphy-measurement-schedule-gastroparesis-diagnosis | nonpregnant-individuals | 15-min intervals for 4 h | "digestible solids at 15-min intervals for 4 h after food" | ada-2026 | p272 | p272/narrative/204 | narrative |
| duration-beyond-which-metoclopramide-treatment-gastroparesis-is-not-fda | people-diabetes | beyond 12 weeks | "yond 12 weeks is no" | ada-2026 | p274 | p274/narrative/205 | narrative |
| threshold-prompting-formal-vascular-evaluation-angiography | people-diabetes | toe pressures <30 mmHg with foot ulcers | "and toe pressures <30 mmHg with" | ada-2026 | p275 | p275/narrative/206 | narrative |
| foot-screening-interval-very-low-risk | people-diabetes | annually | "Annually" | ada-2026 | p275 | p275/narrative/207a | narrative |
| foot-screening-interval-low-risk | people-diabetes | 6-12 months | "Every 6–12 months" | ada-2026 | p275 | p275/narrative/207b | narrative |
| foot-screening-interval-moderate-risk | people-diabetes | 3-6 months | "Every 3–6 months" | ada-2026 | p275 | p275/narrative/207c | narrative |
| foot-screening-interval-high-risk | people-diabetes | 1-3 months | "Every 1–3 months" | ada-2026 | p275 | p275/narrative/207d | narrative |
| age-repeat-interval-noninvasive-arterial-screening-diabetes | people-diabetes | >50 years of age ; repeated every 5 years | "people with diabetes >50 years of age should undergo screening via non- invasive arterial studies (125,127). If nor- mal, these should be repeated every 5 years (125). The" | ada-2026 | p276 | p276/narrative/208 | narrative |
| wound-response-threshold-prompting-advanced-wound-therapy-consideration | people-diabetes | fails to show a reduction of 50% or more after 4 weeks | "re- duction of 50% or more after 4 weeks of" | ada-2026 | p277 | p277/narrative/209 | narrative |
| geriatric-syndrome-hypoglycemia-polypharmacy-screening-interval | adults-diabetes-age65plus | at least annually | "Screen at least annually for geriatric syndromes" | ada-2026 | p283 | p283/narrative/210 | narrative |
| glycemic-goals-healthy-older-adults | adults-diabetes-age65plus | A1C <7.0-7.5% ; TIR ; >=70% ; time below ; <=4% | "goals (such as A1C <7.0–7.5% [<53–58 mmol/mol]) and/or time in range [TIR] 70–180 mg/dL [3.9– 10.0 mmol/L] of ≥70% and time be­ low range ≤70 mg/dL [≤3.9 mmol/L] of ≤4%) if CGM is" | ada-2026 | p288 | p288/narrative/212 | narrative |
| less-stringent-glycemic-goals-older-adults-complex-health | adults-diabetes-age65plus | A1C <8.0% ; TIR ; >=50% ; time below ; <1% | "as A1C <8.0% [<64 mmol/mol] and/or TIR 70–180 mg/dL [3.9–10.0 mmol/L] of ≥50% and time below range <70 mg/dL [3.9 mmol/L] of <1%)" | ada-2026 | p288 | p288/narrative/213 | narrative |
| glucose-goals-healthy-older-adults | adults-diabetes-age65plus | fasting 80-130 ; bedtime 80-180 mg/dL | "80–130 mg/dL (4.4–7.2 mmol/L) 80–180 mg/dL" | ada-2026 | p290 | p290/narrative/214 | narrative |
| glucose-goals-complex-intermediate-older-adults | adults-diabetes-age65plus | fasting 90-150 ; bedtime 100-180 mg/dL | "90–150 mg/dL (5.0–8.3 mmol/L) 100–180 mg/dL" | ada-2026 | p290 | p290/narrative/215 | narrative |
| glucose-ranges-very-complex-poor-health-older-adults | adults-diabetes-age65plus | fasting 100-180 ; bedtime 110-200 mg/dL | "- 100–180 mg/dL (5.6–10.0 mmol/L) 110–200 mg/dL" | ada-2026 | p290 | p290/narrative/216 | narrative |
| minimum-protein-intake-older-adults | adults-diabetes-age65plus | at least 0.8 g/kg body weight/day | "0.8 g/kg body weight/day)" | ada-2026 | p291 | p291/narrative/217 | narrative |
| lower-dose-metformin-range-kidney-monitoring-interval-older-adults | adults-diabetes-age65plus | eGFR 30-45 ; monitored every 3-6 months | "those with eGFR 30–45 mL/min/1.73 m2. eGFR should be monitored every 3–6" | ada-2026 | p292 | p292/narrative/218 | narrative |
| duration-trigger-interval-b12-monitoring | people-diabetes | metformin long term (>4 years), vitamin B12 levels ; annually | "metformin long term (>4 years), vitamin B12 levels should be monitored annually (117)." | ada-2026 | p292 | p292/narrative/219 | narrative |
| minimum-assessment-schedule-post-acute-long-term-care | adults-diabetes-age65plus | every 30 days for the first 90 days ; once every 60 days | "at least every 30 days for the first 90 days after admission and then at least once every 60 days and as" | ada-2026 | p297 | p297/narrative/220 | narrative |
| long-term-care-glucose-patterns-requiring-prompt-clinician-notification | people-diabetes | two or more ; >250 mg/dL within 24 h ; consistently >300 mg/dL over 2 consecutive days | "values are consistently >250 mg/dL (>13.9 mmol/L) within a 24-h period, d. glucose values are consistently >300 mg/dL (>16.7 mmol/L) over 2 consecutive days" | ada-2026 | p297 | p297/narrative/221 | narrative |
| pediatric-diabetes-education-support-schedule | pediatric-diabetes | at diagnosis and routinely ; at each follow-up visit | "and routinely (e.g., at each follow-up visit)" | ada-2026 | p304 | p304/narrative/222 | narrative |
| pediatric-nutrition-education-schedule | pediatric-diabetes | at diagnosis, and at least annually | "and at least annually and ideally more" | ada-2026 | p305 | p305/narrative/223 | narrative |
| pediatric-aerobic-strengthening-activity-goals | pediatric-diabetes | 60 min ; daily ; at least 3 days per week | "the goal of 60 min of moderate- to vigorous-intensity aero­ bic activity daily, with vigorous muscle- strengthening and bone-strengthening activities at least 3 days per week." | ada-2026 | p305 | p305/narrative/224 | narrative |
| initial-medication-doses-youth-type-2-diabetes-algorithm | pediatric-diabetes | Metformin ; up to 2,000 mg per day ; long-acting insulin 0.5 units/kg/day | "◦Titrate up to 2,000 mg per day as tolerated • Long-acting insulin: start at 0.5 units/kg/day" | ada-2026 | p306 | p306/narrative/225 | narrative |
| age-at-which-diabetes-distress-screening-may-begin | people-diabetes | as early as 7 or 8 years of age | "as early as 7 or 8 years of" | ada-2026 | p307 | p307/narrative/226 | narrative |
| start-age-routine-depression-screening-youth | pediatric-diabetes | beginning at age 12 years | "beginning at age 12 years and con­" | ada-2026 | p307 | p307/narrative/227 | narrative |
| age-threshold-supporting-routine-anxiety-screening | people-diabetes | aged 8 years and above | "lescents aged 8 years and above" | ada-2026 | p307 | p307/narrative/228 | narrative |
| examples-less-stringent-pediatric-glycemic-goals | pediatric-diabetes | A1C <7% ; or <7.5% | "14.21 Less stringent A1C goals (such as <7% [<53 mmol/mol] or <7.5%" | ada-2026 | p308 | p308/narrative/229 | narrative |
| more-stringent-glycemic-goal-selected-children-adolescents | pediatric-diabetes | A1C ; <6.5% | "suggest more stringent A1C goals (such as <6.5% [<48 mmol/mol])" | ada-2026 | p309 | p309/narrative/230 | narrative |
| cgm-lookback-period-recommended-pediatric-metrics | pediatric-diabetes | most recent 14 days | "are needed. Though 14 days" | ada-2026 | p309 | p309/narrative/231 | narrative |
| hyperglycemia-ketone-levels-at-which-physical-activity-should-be | people-diabetes | glucose >=350 mg/dL ; beta-hydroxybutyrate >1.5 mmol/L | "hyperglycemia (glucose ≥350 mg/dL [≥19.4 mmol/L]), moderate to large urine ketones, and/or β-hydroxybutyrate >1.5 mmol/L in the" | ada-2026 | p310 | p310/narrative/232 | narrative |
| pre-exercise-blood-glucose-goal-youth | pediatric-diabetes | 126-180 mg/dL | "and exercise are 126–180 mg/dL" | ada-2026 | p310 | p310/narrative/233 | narrative |
| carbohydrate-replacement-during-exercise-after-insulin-boluses | people-diabetes | 0.5-1.0 g of carbohydrates/kg per h ; approximately 30-60 g | "consider 0.5–1.0 g of carbohydrates/kg per h of exercise (∼30–60 g), similar to" | ada-2026 | p310 | p310/narrative/234 | narrative |
| age-bmi-criteria-pediatric-type-2-diabetes-risk-screening | pediatric-diabetes | after 10 years of age ; BMI >=85th to <95th ; BMI >=95th percentile | "ter 10 years of age, whichever occurs earlier, in children with overweight (BMI ≥85th to <95th percentile) or obesity (BMI ≥95th percentile) and" | ada-2026 | p310 | p310/narrative/235 | narrative |
| pediatric-type-2-diabetes-lifestyle-weight-goal | pediatric-diabetes | at least a 7-10% decrease in excess weight | "7–10% decrease in excess" | ada-2026 | p311 | p311/narrative/236 | narrative |
| pediatric-type-2-diabetes-glycemic-assessment-interval | pediatric-diabetes | at least every 3 months | "at least every 3 months or as" | ada-2026 | p311 | p311/narrative/237 | narrative |
| boundary-between-metformin-only-initial-treatment-initial-long-acting | pediatric-diabetes | A1C >=8.5% | "marked hyperglycemia (A1C ≥8.5%" | ada-2026 | p311 | p311/narrative/238 | narrative |
| level-prompting-evaluation-treatment-hyperglycemic-hyperosmolar-state | people-diabetes | blood glucose >=600 mg/dL | "hyperglycemia (blood glucose ≥600 mg/dL [≥33.3 mmol/L])" | ada-2026 | p311 | p311/narrative/239 | narrative |
| class-2-obesity-criterion-considering-adolescent-metabolic-surgery | pediatric-diabetes | BMI 35 to <40 kg/m2 or 120% to <140% percentile | "or higher (BMI 35 to <40 kg/m2 or 120% to <140% percentile for age" | ada-2026 | p312 | p312/narrative/240 | narrative |
| celiac-disease-rescreening-schedule-after-type-1-diabetes-diagnosis | people-t1d | repeated at 2 and then 5 years | "and repeated at 2 and then 5 years" | ada-2026 | p313 | p313/narrative/241 | narrative |
| pediatric-type-1-diabetes-lipid-screening-start-repeat-schedule | pediatric-diabetes | age is >=2 years ; at 9-11 years ; every 3 years | "and age is ≥2 years. If initial LDL cholesterol is ≤100 mg/dL (≤2.6 mmol/L), subsequent testing should be performed at 9–11 years of age B and repeated every 3 years. E" | ada-2026 | p314 | p314/narrative/242 | narrative |
| pediatric-ldl-treatment-goal | pediatric-diabetes | LDL cholesterol goal is <100 mg/dL | "cholesterol goal is <100 mg/dL (<2.6 mmol/L)." | ada-2026 | p314 | p314/narrative/243 | narrative |
| pediatric-dyslipidemia-nutrition-limits | pediatric-diabetes | saturated fat to <7% ; cholesterol to <200 mg/day | "saturated fat to <7%, limit cholesterol to <200 mg/day, avoid trans" | ada-2026 | p314 | p314/narrative/244 | narrative |
| threshold-nutrition-trial-duration-starting-pediatric-statin-therapy | pediatric-diabetes | LDL ; >130 mg/dL after 6 months ; goal ; <100 mg/dL | "remains >130 mg/dL (>3.4 mmol/L) after 6 months of nutrition intervention, initiate therapy with a statin, with a goal of LDL <100 mg/dL (<2.6 mmol/L)." | ada-2026 | p314 | p314/narrative/245 | narrative |
| pediatric-threshold-starting-fibrate-reduce-pancreatitis-risk | pediatric-diabetes | triglycerides >400 mg/dL fasting or >1,000 mg/dL nonfasting | "are >400 mg/dL (>4.7 mmol/L) fasting or >1,000 mg/dL" | ada-2026 | p314 | p314/narrative/246 | narrative |
| pediatric-confirmed-hypertension-definition | pediatric-diabetes | BP consistently >=95th percentile ; or aged >=13 years, BP >=130/80 mmHg | "as BP consistently ≥95th percentile for age, sex, and height or, in adolescents aged ≥13 years, BP ≥130/80 mmHg). Due to" | ada-2026 | p315 | p315/narrative/247 | narrative |
| pediatric-hypertension-treatment-goal | pediatric-diabetes | BP <90th percentile ; or aged >=13 years, BP <130/80 mmHg | "treatment is BP <90th percentile for age, sex, and height or, in adolescents aged ≥13 years, BP <130/80 mmHg. C" | ada-2026 | p315 | p315/narrative/248 | narrative |
| type-1-diabetes-pediatric-nephropathy-screening-start-interval | pediatric-diabetes | at puberty or at age >=11 years ; diabetes for 5 years and annually thereafter | "or at age ≥11 years, whichever is earlier, once the youth have had diabetes for 5 years and annually thereafter. B" | ada-2026 | p315 | p315/narrative/249 | narrative |
| pediatric-elevated-uacr-confirmation-requirement | pediatric-diabetes | two of three samples over a 6-month period | "samples over a 6-month period. B" | ada-2026 | p315 | p315/narrative/250 | narrative |
| monitoring-interval-pediatric-nephropathy | pediatric-diabetes | every 3-6 months | "monitoring (every 3–6 months and/or as" | ada-2026 | p315 | p315/narrative/251 | narrative |
| timing-age-puberty-condition-initial-pediatric-retinal-exam | pediatric-diabetes | type 1 diabetes for 3-5 years ; aged >=11 years or puberty | "have had type 1 diabetes for 3–5 years, provided they are aged ≥11 years or puberty" | ada-2026 | p315 | p315/narrative/252 | narrative |
| pediatric-retinal-follow-up-intervals-after-initial-type-1 | pediatric-diabetes | every 2 years ; every 4 years may be acceptable ; A1C <8% | "recommended every 2 years. Less frequent examinations, every 4 years, may be acceptable on the advice of an eye care professional and based on risk factor assessment, including a history of A1C <8% (<64 mmol/mol). B" | ada-2026 | p316 | p316/narrative/253 | narrative |
| sleep-apnea-symptom-screening-interval-youth-diabetes | pediatric-diabetes | at least annually | "diagnosis and annually. The examination" | ada-2026 | p316 | p316/narrative/254 | narrative |
| latest-start-point-pediatric-adult-transition-preparation | pediatric-diabetes | at least 1 year before the anticipated transfer | "latest, at least 1 year be­ fore" | ada-2026 | p319 | p319/narrative/255 | narrative |
| preconception-glycemic-goal | pregnant-diabetes | A1C <6.5% (<48 mmol/mol) | "A1C <6.5% (<48 mmol/mol), to reduce" | ada-2026 | p327 | p327/narrative/256 | narrative |
| eye-monitoring-schedule-preexisting-diabetes-pregnancy | history-gdm | every trimester and for 1 year postpartum | "trimester and for 1 year postpar­" | ada-2026 | p329 | p329/narrative/257 | narrative |
| recommended-preconception-prenatal-supplement-amounts | pregnant-diabetes | 400-800 micrograms of folic acid ; 150 micrograms of potassium iodide | "400–800 μg of folic acid (28) and 150 μg of potassium" | ada-2026 | p329 | p329/narrative/258 | narrative |
| advised-preconception-glucose-goals | pregnant-diabetes | preprandial glucose 80-110 mg/dL ; 2 h postprandial <155 mg/dL | "dial glucose 80–110 mg/dL (4.4–6.1 mmol/L) and 2 h postprandial glucose <155 mg/dL" | ada-2026 | p330 | p330/narrative/259 | narrative |
| level-at-which-prandial-insulin-dose-should-be-reduced | pregnant-diabetes | postprandial glucose <100 mg/dL | "dial glucose <100 mg/dL (5.6 mmol/L)." | ada-2026 | p330 | p330/narrative/260 | narrative |
| suggested-discontinuation-intervals-before-planned-pregnancy | pregnant-diabetes | semaglutide at least 2 months before ; tirzepatide at least 1 month before pregnancy | "type 1 or type 2 diabetes are shown" | ada-2026 | p330 | p330/narrative/261 | narrative |
| pregnancy-glucose-goals | pregnant-diabetes | fasting <95 mg/dL ; 1-h <140 mg/dL or 2-h <120 mg/dL | "fasting plasma glucose <95 mg/dL (<5.3 mmol/L) and either 1-h post­ prandial glucose <140 mg/dL (<7.8 mmol/L) or 2-h postprandial glucose <120 mg/dL (<6.7 mmol/L)." | ada-2026 | p330 | p330/narrative/262 | narrative |
| preferred-relaxed-a1c-goals-during-pregnancy | pregnant-diabetes | A1C ; <6% ; relaxed to <7% | "diabetes. Ideally, the A1C goal in pregnancy is <6% (<42 mmol/mol) if this can be achieved without signifi­ cant hypoglycemia, but the goal may be relaxed to <7% (<53 mmol/mol) if" | ada-2026 | p330 | p330/narrative/263 | narrative |
| current-hypoglycemia-thresholds-pregnancy | pregnant-diabetes | blood glucose <70 mg/dL ; sensor glucose <63 mg/dL | "include blood glucose <70 mg/dL (<3.9 mmol/L) and sensor glu­ cose <63 mg/dL (<3.5 mmol/L)" | ada-2026 | p331 | p331/narrative/264 | narrative |
| pregnancy-fasting-glucose-target | pregnant-diabetes | 70-95 mg/dL | "Fasting glucose 70–95 mg/dL" | ada-2026 | p331 | p331/narrative/265a | narrative |
| pregnancy-one-hour-postprandial-glucose-target | pregnant-diabetes | 110-140 mg/dL | "1-h postprandial glucose 110–140 mg/dL" | ada-2026 | p331 | p331/narrative/265b | narrative |
| pregnancy-two-hour-postprandial-glucose-target | pregnant-diabetes | 100-120 mg/dL | "2-h postprandial glucose 100–120 mg/dL" | ada-2026 | p331 | p331/narrative/265c | narrative |
| early-pregnancy-fasting-testing-frequency-escalation-threshold | pregnant-diabetes | 3-4 times per week ; predominantly >=110 mg/dL ; testing ; daily | "(e.g., 3–4 times per week) are suggested. Testing frequency may proceed to daily, and treatment may be intensified, if fasting plasma glucose is predominantly ≥110" | ada-2026 | p332 | p332/narrative/266 | narrative |
| pregnancy-cgm-target-range | pregnant-diabetes | 63-140 mg/dL and >70% | "Goal sensor glucose range 63–140 mg/dL (3.5–7.8 mmol/L): TIR, goal >70%" | ada-2026 | p333 | p333/narrative/267a | narrative |
| pregnancy-cgm-level-one-low-limit | pregnant-diabetes | <63 mg/dL and <4% | "Time below range (TBR) (<63 mg/dL [<3.5 mmol/L]): level 1 TBR, goal <4%" | ada-2026 | p333 | p333/narrative/267b | narrative |
| pregnancy-cgm-level-two-low-limit | pregnant-diabetes | <54 mg/dL and <1% | "TBR (<54 mg/dL [<3.0 mmol/L]): level 2 TBR, goal <1%" | ada-2026 | p333 | p333/narrative/267c | narrative |
| pregnancy-cgm-high-limit | pregnant-diabetes | >140 mg/dL and <25% | "TAR (>140 mg/dL [>7.8 mmol/L]): TAR, goal <25%" | ada-2026 | p333 | p333/narrative/267d | narrative |
| pregnancy-dietary-reference-intakes | pregnant-diabetes | minimum of 175 g carbohydrate ; 71 g protein ; 28 g fiber | "mum of 175 g of carbohydrate (∼35% of a 2,000-calorie diet), a minimum of 71 g of protein, and 28 g of fiber" | ada-2026 | p333 | p333/narrative/268 | narrative |
| stop-point-metformin-used-induce-ovulation-pcos | pregnant-diabetes | discontinued by the end of the first trimester | "ovulation, should be discontinued by the end of the first trimester. A" | ada-2026 | p333 | p333/narrative/269 | narrative |
| pregnancy-postpartum-aerobic-activity-target | history-gdm | at least 150 min ; each week during pregnancy and postpartum | "do at least 150 min of moderate-" | ada-2026 | p334 | p334/narrative/270 | narrative |
| recommended-pregnancy-weight-gain-overweight-obesity-respectively | pregnant-diabetes | 15-25 lbs ; 10-20 lbs | "status is 15–25 lbs (6.8–11.3 kg) and for those with obesity is 10–20 lbs (4.5–9.1 kg)" | ada-2026 | p336 | p336/narrative/271 | narrative |
| blood-pressure-threshold-initiating-titrating-chronic-hypertension-therapy-pregnancy | pregnant-diabetes | 140/90 mmHg | "blood pressure of 140/90 mmHg as the" | ada-2026 | p337 | p337/narrative/273 | narrative |
| blood-pressure-level-prompting-deintensification-during-pregnancy | pregnant-diabetes | <90/60 mmHg | "blood pressure is <90/60 mmHg. E" | ada-2026 | p337 | p337/narrative/274 | narrative |
| postpartum-gdm-initial-screening-interval | history-gdm | 4-12 weeks postpartum | "GDM at 4–12 weeks postpartum" | ada-2026 | p338 | p338/narrative/275a | narrative |
| postpartum-gdm-lifelong-screening-interval | history-gdm | every 1-3 years | "prediabetes every 1–3 years" | ada-2026 | p338 | p338/narrative/275b | narrative |
| alternative-later-postpartum-test-ogtt-is-declined-not-completed | history-gdm | A1C performed at 6-12 months postpartum | "tolerance test, an A1C performed at 6–12 months postpartum may" | ada-2026 | p339 | p339/narrative/276 | narrative |
| admission-hyperglycemia-threshold-lookback-window-requiring-a1c | people-diabetes | random blood glucose >140 mg/dL ; prior 3 months | "dom blood glucose >140 mg/dL [>7.8 mmol/L]) at the time of admission to the hospital if no A1C test result is available from the prior 3 months. B" | ada-2026 | p345 | p345/narrative/277 | narrative |
| persistent-inpatient-hyperglycemia-threshold-starting-intensifying-therapy | hospitalized-diabetes-hyperglycemia | >=180 mg/dL ; two occasions within 24 h | "of ≥180 mg/dL (≥10.0 mmol/L) (con­ firmed on two occasions within 24 h)" | ada-2026 | p346 | p346/narrative/278 | narrative |
| glycemic-goal-most-critically-ill-inpatients | hospitalized-diabetes-hyperglycemia | 140-180 mg/dL | "glycemic goal of 140–180 mg/dL" | ada-2026 | p346 | p346/narrative/279 | narrative |
| glycemic-goal-most-noncritically-ill-inpatients | hospitalized-diabetes-hyperglycemia | 100-180 mg/dL | "of 100–180 mg/dL (5.6–10.0 mmol/L)" | ada-2026 | p346 | p346/narrative/280 | narrative |
| more-stringent-inpatient-goal-that-may-suit-selected-critical | hospitalized-diabetes-hyperglycemia | 110-140 mg/dL | "110–140 mg/dL (6.1–7.8 mmol/L)" | ada-2026 | p347 | p347/narrative/281 | narrative |
| inpatient-glucose-monitoring-frequencies-eating-not-eating-receiving-iv | hospitalized-diabetes-hyperglycemia | before meals ; every 4-6 h ; every 30 min to every 2 h | "is advised every 4–6 h (36). More frequent POC blood glucose moni­ toring typically ranging from every 30 min to every 2 h is recommended" | ada-2026 | p347 | p347/narrative/282 | narrative |
| timing-subcutaneous-basal-insulin-before-stopping-iv-insulin | people-diabetes | 2 h before intravenous infusion is discontinued | "2 h before intravenous" | ada-2026 | p348 | p348/narrative/283 | narrative |
| usual-starting-total-daily-inpatient-insulin-dose | hospitalized-diabetes-hyperglycemia | 0.3-0.6 units/kg/day | "to insulin, with 0.3–0.6 units/kg/day" | ada-2026 | p349 | p349/narrative/284 | narrative |
| one-approach-estimating-initial-inpatient-total-daily-insulin | hospitalized-diabetes-hyperglycemia | 80% of the home insulin dose | "or calculated as 80% of the home" | ada-2026 | p349 | p349/narrative/285 | narrative |
| total-daily-dose-cutoffs-selecting-correction-insulin-scale-intensity | people-diabetes | low ; <40 units/day, medium ; 40-80 units/day, and high ; >80 units/day | "for insulin dose <40 units/day, medium for 40–80 units/day, and high for >80 units/day. Correctional insulin" | ada-2026 | p349 | p349/narrative/286 | narrative |
| typical-threshold-correction-insulin-dosing | people-diabetes | start at 140 or 150 mg/dL | "typically start at 140 or 150 mg/dL" | ada-2026 | p349 | p349/narrative/287 | narrative |
| preoperative-sglt2-inhibitor-withholding-interval | people-diabetes | 3 days before scheduled surgeries (4 days for ertugliflozin) | "inhibitors be stopped 3 days be­ fore scheduled surgeries (4 days for ertu­" | ada-2026 | p350 | p350/narrative/288 | narrative |
| inpatient-hypoglycemia-carbohydrate-dose | hospitalized-diabetes-hyperglycemia | 15 g | "administering 15 g of fast-acting carbohy­ drate" | ada-2026 | p350 | p350/narrative/289a | narrative |
| inpatient-hypoglycemia-recheck-interval | hospitalized-diabetes-hyperglycemia | every 15 min | "Blood glucose should be monitored every 15 min" | ada-2026 | p350 | p350/narrative/289b | narrative |
| inpatient-hypoglycemia-treatment-stop-threshold | hospitalized-diabetes-hyperglycemia | above 70 mg/dL | "until it is stabilized above 70 mg/dL" | ada-2026 | p350 | p350/narrative/289c | narrative |
| insulin-carbohydrate-starting-ratio-enteral-parenteral-nutrition | hospitalized-diabetes-hyperglycemia | 1 unit ; every 10-15 g of carbohydrate | "calculated as 1 unit of insulin for every 10–15 g of carbohydrate" | ada-2026 | p351 | p351/narrative/290 | narrative |
| correction-insulin-intervals-during-continuous-nutrition | people-diabetes | regular human insulin every 6 h or rapid-acting insulin every 4 h | "tered subcutaneously every 6 h with regu­ lar human insulin or rapid-acting insulin every 4 h. If enteral" | ada-2026 | p351 | p351/narrative/291 | narrative |
| preoperative-a1c-goal-recency-requirement | people-diabetes | A1C goal <8% ; within 3 months | "tive A1C goal <8% (<64 mmol/mol) is recommended within 3 months, with" | ada-2026 | p352 | p352/narrative/292 | narrative |
| alternative-cgm-evidence-adequate-preoperative-glycemia | people-diabetes | 14-day glucose management indicator <8% and/or time in range >50% | "sessment. C The 14-day glucose man­ agement indicator goal <8% and/or time in range >50% can also be" | ada-2026 | p352 | p352/narrative/293 | narrative |
| perioperative-glucose-target | hospitalized-diabetes-hyperglycemia | between 100 and 180 mg/dL | "and maintained between 100 and 180 mg/dL (5.6 and" | ada-2026 | p352 | p352/narrative/294 | narrative |
| glucose-monitoring-interval-while-npo-perioperatively | hospitalized-diabetes-hyperglycemia | at least every 2-4 h | "at least every 2–4 h while the" | ada-2026 | p352 | p352/narrative/295 | narrative |
| preoperative-basal-insulin-reduction | people-diabetes | 25% | "25% of basal insulin dose" | ada-2026 | p352 | p352/narrative/296a | narrative |
| preoperative-nph-insulin-dose | people-diabetes | one-half | "NPH insulin to one-half of the dose" | ada-2026 | p352 | p352/narrative/296b | narrative |
| preoperative-long-acting-basal-insulin-dose | people-diabetes | 75-80% | "long-acting basal insulin analogs to 75–80% of the dose" | ada-2026 | p352 | p352/narrative/296c | narrative |
| risk-mitigation-delayed-gastric-emptying-glp-1-therapy | people-diabetes | liquid nutrition protocol for 24 h before the procedure | "pro­ tocol for 24 h before the" | ada-2026 | p353 | p353/narrative/297 | narrative |
| subcutaneous-rapid-acting-insulin-regimen-mild-dka | hospitalized-diabetes-hyperglycemia | 0.1 units/kg ; every 1 h or 0.2 units/kg every 2 h | "0.1 units/kg rapid-acting insulin analog every 1 h or 0.2 units/kg every 2 h" | ada-2026 | p354 | p354/narrative/298 | narrative |
| dka-initial-iv-insulin-rate | hospitalized-diabetes-hyperglycemia | 0.1 units/kg/h | "0.1 units/kg/h" | ada-2026 | p354 | p354/narrative/299a | narrative |
| dka-reduced-iv-insulin-rate | hospitalized-diabetes-hyperglycemia | 0.05 units/kg/h | "insulin dose to 0.05 units/kg/h" | ada-2026 | p354 | p354/narrative/299b | narrative |
| dka-insulin-rate-reduction-glucose-threshold | hospitalized-diabetes-hyperglycemia | <250 mg/dL | "When glucose reaches <250 mg/dL" | ada-2026 | p354 | p354/narrative/299c | narrative |
| hyperglycemic-crisis-potassium-insulin-hold-threshold | hospitalized-diabetes-hyperglycemia | <3.5 mmol/L | "K+ <3.5 mmol/L" | ada-2026 | p354 | p354/narrative/300a | narrative |
| hyperglycemic-crisis-potassium-target | hospitalized-diabetes-hyperglycemia | 4-5 mmol/L | "keep serum K+ between 4 and 5 mmol/L" | ada-2026 | p354 | p354/narrative/300b | narrative |
| severe-biochemical-thresholds-considering-bicarbonate-phosphate-dka | hospitalized-diabetes-hyperglycemia | Bicarbonate ; only ; pH <7.0 ; phosphate <1.0 mmol/L | "if pH is <7.0 phosphate <1.0 mmol/L or <0.32" | ada-2026 | p354 | p354/narrative/301 | narrative |
| dka-glucose-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | >=200 mg/dL | "Glucose ≥200 mg/dL" | ada-2026 | p355 | p355/narrative/302a | narrative |
| dka-beta-hydroxybutyrate-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | >=3.0 mmol/L | "β-Hydroxybutyrate concentration ≥3.0 mmol/L" | ada-2026 | p355 | p355/narrative/302b | narrative |
| dka-ph-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | <7.3 | "pH <7.3" | ada-2026 | p355 | p355/narrative/302c | narrative |
| dka-bicarbonate-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | <18 mmol/L | "bicarbonate concentration <18 mmol/L" | ada-2026 | p355 | p355/narrative/302d | narrative |
| hhs-glucose-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | >=600 mg/dL | "Plasma glucose ≥600 mg/dL" | ada-2026 | p355 | p355/narrative/303a | narrative |
| hhs-effective-osmolality-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | >300 mOsm/kg | "Calculated effective serum osmolality >300 mOsm/kg" | ada-2026 | p355 | p355/narrative/303b | narrative |
| hhs-total-osmolality-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | >320 mOsm/kg | "total serum osmolality >320 mOsm/kg" | ada-2026 | p355 | p355/narrative/303c | narrative |
| hhs-beta-hydroxybutyrate-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | <3.0 mmol/L | "β-Hydroxybutyrate concentration <3.0 mmol/L" | ada-2026 | p355 | p355/narrative/303d | narrative |
| hhs-ph-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | >=7.3 | "pH ≥7.3" | ada-2026 | p355 | p355/narrative/303e | narrative |
| hhs-bicarbonate-diagnostic-threshold | hospitalized-diabetes-hyperglycemia | >=15 mmol/L | "bicarbonate concentration ≥15 mmol/L" | ada-2026 | p355 | p355/narrative/303f | narrative |
| transition-timing-from-iv-subcutaneous-insulin-after-dka | hospitalized-diabetes-hyperglycemia | basal insulin 2-4 h before the intravenous insulin is stopped | "insulin 2–4 h before the" | ada-2026 | p355 | p355/narrative/304 | narrative |
| subcutaneous-rapid-acting-insulin-interval-mild-uncomplicated-dka | hospitalized-diabetes-hyperglycemia | every 1-2 h | "doses given every 1–2 h (180), and" | ada-2026 | p355 | p355/narrative/305 | narrative |
| postdischarge-follow-up-after-inpatient-dysglycemia | hospitalized-diabetes-hyperglycemia | within 1 month of discharge | "within 1 month of discharge" | ada-2026 | p356 | p356/narrative/306a | narrative |
| earlier-postdischarge-follow-up-after-treatment-change-or-poor-control | hospitalized-diabetes-hyperglycemia | in 1-2 weeks | "1–2 weeks) is preferred" | ada-2026 | p356 | p356/narrative/306b | narrative |

## Conflicts

No duplicate `(quantity, population)` pair carries different values in this sheet.


## Coverage

Every distinct recommendation identifier in the bound extraction that is not cited
by a marker-derived row, with why. The 126 extracted records carry 116 distinct
identifiers; 25 marker-derived rows cite 14 of them and the 102 unique identifiers in
the main list below account for the rest. Because
the source is `bound`, an identifier absent from both places warns rather than
refuses.

**Duplicate marker records.**

The extractor emitted ten additional records under nine identifiers it had already
used. Each occurrence is a separate change-summary marker and receives the same
disposition as its first occurrence in the main list; naming the groups and their
record counts is what keeps 126 records from reading as though 116 identifiers were
the whole input.

- `p13/recommendation/2.24` - 2 change-summary records; both scoped out
- `p13/recommendation/4.13` - 2 change-summary records; both scoped out
- `p14/recommendation/7.25` - 2 change-summary records; both scoped out
- `p14/recommendation/7.3` - 3 change-summary records; all three scoped out
- `p15/recommendation/9.9` - 2 change-summary records; both scoped out
- `p16/recommendation/10.44` - 2 change-summary records; both scoped out
- `p16/recommendation/11.11` - 2 change-summary records; both scoped out
- `p16/recommendation/11.6` - 2 change-summary records; both scoped out
- `p17/recommendation/13.11` - 2 change-summary records; both scoped out

**Main identifier list.**

- `p12/recommendation/1.1` - change-summary entry, not a recommendation statement
- `p12/recommendation/1.5` - change-summary entry, not a recommendation statement
- `p12/recommendation/1.8` - change-summary entry, not a recommendation statement
- `p12/recommendation/1.9` - change-summary entry, not a recommendation statement
- `p12/recommendation/2.8` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.18` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.19` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.20` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.21` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.22` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.24` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.31` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.8` - change-summary entry, not a recommendation statement
- `p13/recommendation/2.9` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.1` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.2` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.3` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.4` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.6` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.8` - change-summary entry, not a recommendation statement
- `p13/recommendation/3.9` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.13` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.26` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.27` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.3` - change-summary entry, not a recommendation statement
- `p13/recommendation/4.5` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.12` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.23` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.4` - change-summary entry, not a recommendation statement
- `p13/recommendation/5.5` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.32` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.34` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.40` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.45` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.46` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.47` - change-summary entry, not a recommendation statement
- `p14/recommendation/5.56` - change-summary entry, not a recommendation statement
- `p14/recommendation/6.17` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.15` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.17` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.25` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.3` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.6` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.7` - change-summary entry, not a recommendation statement
- `p14/recommendation/7.8` - change-summary entry, not a recommendation statement
- `p14/recommendation/8.2` - change-summary entry, not a recommendation statement
- `p15/recommendation/10.10` - change-summary entry, not a recommendation statement
- `p15/recommendation/10.4` - change-summary entry, not a recommendation statement
- `p15/recommendation/10.6` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.14` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.15` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.20` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.21` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.29` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.5` - change-summary entry, not a recommendation statement
- `p15/recommendation/8.8` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.11` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.12` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.13` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.24` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.25` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.27` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.33` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.36` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.37` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.38` - change-summary entry, not a recommendation statement
- `p15/recommendation/9.9` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.11` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.32` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.40` - change-summary entry, not a recommendation statement
- `p16/recommendation/10.44` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.1` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.10` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.11` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.5` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.6` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.8` - change-summary entry, not a recommendation statement
- `p16/recommendation/11.9` - change-summary entry, not a recommendation statement
- `p16/recommendation/12.22` - change-summary entry, not a recommendation statement
- `p16/recommendation/13.9` - change-summary entry, not a recommendation statement
- `p166/recommendation/7.27` - no numeric decision point in the recommendation
- `p166/recommendation/7.28` - no numeric decision point in the recommendation
- `p17/recommendation/13.11` - change-summary entry, not a recommendation statement
- `p17/recommendation/14.1` - change-summary entry, not a recommendation statement
- `p17/recommendation/14.2` - change-summary entry, not a recommendation statement
- `p17/recommendation/14.3` - change-summary entry, not a recommendation statement
- `p17/recommendation/15.24` - change-summary entry, not a recommendation statement
- `p17/recommendation/15.25` - change-summary entry, not a recommendation statement
- `p17/recommendation/15.3` - change-summary entry, not a recommendation statement
- `p18/recommendation/16.14` - change-summary entry, not a recommendation statement
- `p256/recommendation/11.4` - no numeric decision point in the recommendation
- `p262/recommendation/11.10` - no numeric decision point in the recommendation
- `p287/recommendation/13.3` - narrative cross-reference, not a recommendation statement
- `p331/recommendation/2.32` - narrative cross-reference, not a recommendation statement
- `p346/recommendation/16.3` - no numeric decision point in the recommendation
- `p348/recommendation/16.7` - no numeric decision point in the recommendation
- `p349/recommendation/16.11` - no numeric decision point in the recommendation
- `p355/recommendation/16.18` - no numeric decision point in the recommendation
- `p36/recommendation/2.5` - no numeric decision point in the recommendation
- `p70/recommendation/4.5` - no numeric decision point in the recommendation
- `p78/recommendation/4.14` - no numeric decision point in the recommendation
- `p79/recommendation/4.17` - no numeric decision point in the recommendation
