# Hypertension — threshold sheet

<!-- schema: threshold-sheet/2 -->

phi-scan: synthetic

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

**Every `snippet` cell is verbatim AHA/ACC text, deliberately.** It is what the citation
gates check against — paraphrase it and a fabricated citation stops being detectable — and
that trade was ruled against a public repo on 2026-08-18,
[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223). How much is
quoted, and why it is not a taste call, is measured in
[README.md](README.md#the-quoting-posture-ruled-against-a-public-repo) and re-derived from
this file by a test, so the figures cannot go stale here.


## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| aha-2025 | AHA/ACC | AHA ACC/jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection | 2025 | 2025 | https://doi.org/10.1161/HYP.0000000000000249 | exact |

## Scope

**Read:** every `Recommendations for ...` table in the source — **103 numbered
recommendations**, extracted by `tools/guidelines_recs.py`, each one either a row
below or listed under [Coverage](#coverage). That 103 is the load-bearing figure
here and it is exact: 103 unique identifiers, none unparsed.

The tool groups those 103 under **27** table headings, which is what it prints and
the only table figure re-derivable from it. **It is not the count of tables**: two
headings are `(Continued)` continuations of tables it also lists separately, so the
guideline presents **25**. This line said `33` until it was re-derived, which is the
count of `Recommendations for` heading *occurrences* in the extracted text and so
counts a header reprinted after a page break as another table.

The appendices (pp. 98-105) were read on 2026-08-23 and yielded no patient-care
decision point. The reference list (pp. 75-97) is retired by class because a
citation list contains no clinical prose.

The front matter, methods, recommendation tables, narrative sections, figures, and
clinical tables on pp. 1-74 were read in full on 2026-08-29. Numeric study results
that do not direct patient care remain outside this decision-point sheet.

**Not read:** none of the clinical-content spans. References remain exempt as a
citation list, and the appendices have a dated null read below.

| span | pages | read |
| --- | --- | --- |
| front matter and methods | 1-10 | yes |
| recommendation tables, narrative sections, figures, and clinical tables | 11-74 | yes |
| references | 75-97 | exempt: citation list contains no clinical prose |
| appendices | 98-105 | read 2026-08-23 |

citations resolved against C:/codeing/guidelines-src on 2026-08-29
extraction identity: producer e0e241393b3cf92231a7c40123046db47cdcb57b; tools/guidelines_extract.py sha256 f8e95baf7e4e74328a752d89e1e7b617217ba1e43c4368fba92f789840e21cf9


## Populations

| key | verbatim |
| --- | --- |
| adults | adults |
| adults-htn | adults with hypertension |
| adults-htn-cvd | adults with hypertension and clinical cardiovascular disease |
| adults-htn-highrisk | adults with hypertension, no clinical CVD, with diabetes or CKD or 10-year PREVENT risk >=7.5% |
| adults-htn-lowrisk | adults with hypertension, no clinical CVD, 10-year PREVENT risk <7.5% |
| adults-dm | adults with diabetes |
| adults-ckd | adults with chronic kidney disease |
| adults-pregnancy | pregnant individuals |
| adults-resistant-htn | adults with resistant hypertension |
| adults-overweight | adults with overweight or obesity |
| adults-women | adult women who consume alcohol |
| adults-men | adult men who consume alcohol |
| adults-ich | adults with acute spontaneous intracerebral hemorrhage |
| adults-htn-emergency | adults with hypertensive emergency |
| adults-htn-emergency-compelling | adults with hypertensive emergency and a compelling condition |
| adults-htn-emergency-dissection | adults with hypertensive emergency and acute aortic dissection |
| adults-htn-emergency-nocompelling | adults with hypertensive emergency without a compelling condition |
| adults-hospitalized-severe-htn | adults hospitalized for noncardiac conditions without acute target organ damage |
| adults-preop | patients scheduled for elective major surgery |
| adults-home-bp | adults monitoring blood pressure at home |
| adults-aldosteronism-screening | adults undergoing primary aldosteronism screening |
| adults-htn-medication | adults starting or titrating antihypertensive medication |
| adults-hfrEF | adults with hypertension and heart failure with reduced ejection fraction |
| adults-hfpef | adults with hypertension and heart failure with preserved ejection fraction |
| adults-pad | adults with hypertension and peripheral artery disease |
| adults-pregnancy-postpartum | postpartum individuals with a hypertensive disorder of pregnancy |
| adults-rdn | adults undergoing renal denervation |
| adults-aortic-dissection | adults with acute aortic dissection |

## Quantities

| key | verbatim |
| --- | --- |
| acute-ich-bp-control-duration | lower SBP to 130 to <140 mm Hg for at least 7 days |
| acute-ich-sbp-lowering-floor | SBP should not be lowered below 130 mm Hg |
| acute-ich-sbp-target | immediately lower SBP to 130 to <140 mm Hg |
| acute-stroke-bp-reduction-target | it might be reasonable to lower BP by 15% during the first 24 hours |
| acute-stroke-bp-treatment-threshold | In patients with BP of ≥220/120 mm Hg who did not receive IV |
| alcohol-limit | reduce alcohol intake to ≤1 drink/d for women |
| antihypertensive-dosing-frequency | dosing once daily rather than multiple times daily |
| aspirin-preeclampsia-prophylaxis-dose | counseled about the benefits of low-dose (81 mg/day) aspirin to reduce the risk |
| bariatric-surgery-bmi-threshold | obesity with a BMI ≥35.0 kg/m2, bariatric surgery |
| bp-stage-1-range-dbp | and DBP 80-89 mm Hg), initiation of antihypertensive drug therapy |
| bp-stage-1-range-sbp | In adults with stage 1 hypertension (SBP 130- 139 mm Hg |
| bp-stage-2-threshold-dbp | and DBP ≥90 mm Hg), initiation of antihypertensive drug therapy |
| bp-stage-2-threshold-sbp | In adults with stage 2 hypertension (SBP ≥ 140 mm Hg |
| bp-treatment-goal-dbp | a DBP target of <80 mm Hg is recommended |
| bp-treatment-goal-sbp | an SBP goal of at least <130 mm Hg |
| bp-treatment-threshold-dbp | initiation of medications to lower BP is recommended when average DBP is ≥90 mm Hg |
| bp-treatment-threshold-sbp | initiation of medications to lower BP is recommended when average SBP is ≥140 mm Hg |
| chronic-htn-pregnancy-staging-cutoff | SBP 140 to 159 mm Hg and/or DBP 90 to 109 mm Hg prior to |
| dietary-sodium-ideal-limit | moving toward an ideal limit of <1500 mg/d |
| dietary-sodium-limit | reduction of dietary sodium intake* is recommended to <2300 mg/d |
| egfr-threshold-mra | with an eGFR of ≥45 mL/min/1.73 m2), addition of a MRA is recommended |
| egfr-threshold-rdn | eGFR ≥40 mL/ min/1.73 m2 who have resistant hypertension despite optimal treatment |
| follow-up-interval | follow-up evaluations for medication adherence and response to treatment at monthly intervals |
| hypertensive-emergency-bp-reduction-first-hour | reduced with oral or parenteral therapy by no more than 25% within the first hour |
| hypertensive-emergency-bp-target-2-6h | then, if stable, to <160/100 mm Hg within the next 2 to 6 hours |
| hypertensive-emergency-bp-target-24-48h | to 130 to 140 mm Hg during the next 24 to 48 hours |
| hypertensive-emergency-bp-threshold | (BP >180 and/or >120 mm Hg and evidence of acute target organ damage) |
| hypertensive-emergency-sbp-target | SBP should be reduced to <140 mm Hg for most conditions |
| incretin-mimetic-bmi-threshold | obesity with a BMI ≥27 kg/m2 |
| lifestyle-trial-duration | after a 3- to 6-month trial of lifestyle intervention |
| masked-htn-exclusion-bp-threshold | untreated office SBP <130 mm Hg and DBP <80 mm Hg |
| post-reperfusion-sbp-floor | lowering SBP <140 mm Hg within the first 24 to 72 hours after reperfusion |
| post-thrombolysis-bp-ceiling | maintained below 180/105 mm Hg for at least the first 24 hours |
| pregnancy-acute-bp-target | lower BP to <160/<110 mm Hg within 30 to 60 minutes |
| pregnancy-bp-treatment-goal | should receive antihypertensive therapy to achieve BP <140/90 mm Hg to prevent maternal |
| pregnancy-severe-bp-treatment-threshold | Pregnant individuals with SBP ≥160 mm Hg or DBP ≥110 mm Hg confirmed on repeat |
| primary-aldo-screening-stroke-age-cutoff | or stroke at a young age (<40 years) |
| raasi-indication-egfr-threshold | as identified by eGFR <60 mL/min/1.73 m2 |
| rdn-eligibility-bp | office SBP 140-180 mm Hg and DBP ≥90 mm Hg |
| severe-hypertension-threshold | severe hypertension (>180/120 mm Hg) who are hospitalized for noncardiac conditions |
| surgery-deferral-bp-threshold | elective major surgery with SBP ≥180 mm Hg or DBP ≥110 mm Hg |
| thrombolysis-eligibility-bp-threshold | their BP lowered to SBP <185 mm Hg and DBP <110 mm Hg before IV |
| weight-loss-goal | weight loss is recommended with a goal of at least 5% of body weight reduction |
| white-coat-exclusion-bp-threshold | untreated office SBP ≥130 mm Hg or DBP ≥80 mm Hg |
| white-coat-exclusion-bp-upper-limit | without office SBP ≥160 mm Hg or DBP ≥100 mm Hg |
| bp-treatment-goal | blood pressure treatment goal is <130/80 mm Hg |
| office-bp-normal | normal blood pressure is defined as <120/<80 mm Hg |
| office-bp-elevated | elevated blood pressure is 120-129/<80 mm Hg |
| office-bp-stage-1 | stage 1 hypertension is 130-139/80-89 mm Hg |
| office-bp-stage-2 | stage 2 hypertension is ≥140/90 mm Hg |
| prevent-age-range | PREVENT is applicable to adults aged 30 to 79 years |
| office-bp-reading-count | average of ≥2 BP measurements obtained on ≥2 separate occasions |
| bp-measurement-trigger-avoidance | avoid caffeine, exercise, and smoking for at least 30 minutes |
| bp-measurement-rest-period | more than 5 minutes of rest |
| bp-measurement-repeat-interval | 2 or more measurements at least 1 minute apart |
| bp-measurement-competency-interval | competency checks every 6 to 12 months |
| routine-laboratory-repeat-interval | repeated at least annually |
| abpm-monitoring-duration | period of 24 hours |
| abpm-daytime-interval | daytime 15-30 minutes |
| abpm-nighttime-interval | nighttime 30-60 minutes |
| hbpm-daily-reading-count | 2 readings 1 minute apart twice a day |
| hbpm-monitoring-duration | 3 days minimum to 7 days preferred |
| hbpm-threshold-office-120 | office 120/80 corresponds to HBPM 120/80 |
| daytime-abpm-threshold-office-120 | office 120/80 corresponds to daytime ABPM 120/80 |
| nighttime-abpm-threshold-office-120 | office 120/80 corresponds to nighttime ABPM 100/65 |
| full-day-abpm-threshold-office-120 | office 120/80 corresponds to 24-hour ABPM 115/75 |
| hbpm-threshold-office-130 | office 130/80 corresponds to HBPM 130/80 |
| daytime-abpm-threshold-office-130 | office 130/80 corresponds to daytime ABPM 130/80 |
| nighttime-abpm-threshold-office-130 | office 130/80 corresponds to nighttime ABPM 110/65 |
| full-day-abpm-threshold-office-130 | office 130/80 corresponds to 24-hour ABPM 125/75 |
| hbpm-threshold-office-140 | office 140/90 corresponds to HBPM 135/85 |
| daytime-abpm-threshold-office-140 | office 140/90 corresponds to daytime ABPM 135/85 |
| nighttime-abpm-threshold-office-140 | office 140/90 corresponds to nighttime ABPM 120/70 |
| full-day-abpm-threshold-office-140 | office 140/90 corresponds to 24-hour ABPM 130/80 |
| hbpm-threshold-office-160 | office 160/100 corresponds to HBPM 145/90 |
| daytime-abpm-threshold-office-160 | office 160/100 corresponds to daytime ABPM 145/90 |
| nighttime-abpm-threshold-office-160 | office 160/100 corresponds to nighttime ABPM 140/85 |
| full-day-abpm-threshold-office-160 | office 160/100 corresponds to 24-hour ABPM 145/90 |
| secondary-htn-screening-age | early-onset hypertension age <30 years |
| osa-neck-size-men | neck size >17 inches for men |
| osa-neck-size-women | neck size >16 inches for women |
| primary-aldo-confirmatory-mra-withdrawal | withdrawal of MRA for 4-6 weeks |
| primary-aldo-oral-loading-duration | 24-hour urine aldosterone |
| primary-aldo-iv-infusion-duration | aldosterone at 4 hours of infusion |
| cushing-dexamethasone-dose | overnight 1-mg dexamethasone suppression test |
| acromegaly-gh-threshold | growth hormone ≥1 ng/mL during oral glucose load |
| caffeine-limit | caffeine <300 mg/d |
| acetaminophen-limit | acetaminophen less than 4 g/d |
| contraceptive-ethinyl-estradiol-dose | 20-30 mcg ethinyl estradiol |
| primary-aldo-renin-threshold | renin activity <1 ng/mL/h |
| primary-aldo-aldosterone-threshold | aldosterone at least 10 ng/dL |
| primary-aldo-ratio-threshold | aldosterone to renin ratio 30 |
| primary-aldo-mra-withdrawal | MRA withdrawn for at least 4 weeks |
| primary-aldo-repeat-testing-washout | at least 2 to 4 weeks before repeat testing |
| adrenal-mass-surgery-threshold | size >4 cm |
| dietary-potassium-goal | dietary potassium 3500 to 5000 mg/day |
| aerobic-activity-goal | ≥150 minutes/week |
| resistance-activity-goal | ≥2 days/week |
| potassium-supplementation-upper-limit | <80 mmol/d |
| standard-drink-alcohol-content | 12 to 14 g alcohol |
| aerobic-exercise-prescription | 90-150 min/wk at 65%-75% heart rate reserve |
| dynamic-resistance-prescription | 90-150 min/wk at 50%-80% one-repetition maximum |
| isometric-resistance-prescription | 4 by 2 min, 1 min rest, 30%-40%, 3 sessions/wk |
| meditation-prescription | 2 by 20 min sessions/d |
| breathing-control-prescription | <10 breaths/min for 15 min/d |
| non-asian-overweight-bmi-range | BMI 25.0-29.9 kg/m2 |
| asian-overweight-bmi-range | BMI 23.0-27.4 kg/m2 |
| potassium-supplementation-optimal-dose | approximately 30 mmol/day |
| potassium-supplementation-high-dose | above 80 mmol/day |
| alcohol-reduction-goal | at least 50% or abstinence |
| combination-therapy-distance-from-goal | SBP ≥20 and DBP ≥10 from target |
| metabolic-panel-monitoring-interval | 2 to 4 weeks after initiation or titration |
| egfr-monitoring-interval | 2 to 4 weeks after initiation or titration |
| egfr-expected-dip | eGFR dip up to 30% |
| egfr-hold-threshold | eGFR decline persistently >30% |
| patiromer-separation-interval | at least 3 hours before or after |
| sodium-zirconium-separation-interval | separation by 2 hours |
| ccd-dbp-goal-range | DBP 70 to 80 mm Hg |
| hfref-ejection-fraction-cutoff | ejection fraction ≤40% |
| mra-hfref-egfr-threshold | eGFR >30 mL/min/1.73 m2 |
| mra-hfref-potassium-threshold | potassium <5.0 mEq/L |
| home-bp-treatment-goal | home BP <135/85 mm Hg |
| normal-bp-reassessment-interval | reassess in 1 year |
| elevated-bp-reassessment-interval | reassess in 3-6 months |
| medication-bp-reassessment-interval | reassess in 1 month |
| controlled-bp-reassessment-interval | reassess in 3-6 months |
| preeclampsia-aspirin-start-week | aspirin after 12 weeks gestation |
| postpartum-bp-check-interval | BP check within 3 to 10 days of discharge |
| postpartum-bp-monitoring-interval | BP measured at least annually |
| resistant-htn-medication-count | above goal despite 3 medications |
| controlled-resistant-htn-medication-count | at goal requiring ≥4 medications |
| rdn-artery-diameter-range | artery diameters 3 to 8 mm |
| rdn-referral-duration | uncontrolled >6 months |
| rdn-surveillance-high-risk-period | first 6 months |
| aortic-dissection-target-time | SBP ≤120 mm Hg within 20 minutes |
| perioperative-hypertension-duration | persists >15 minutes |
| perioperative-raasi-hold-interval | stopped 24 hours before surgery |
| severe-htn-follow-up-interval | follow-up in 4 weeks |
| initial-combination-agent-count | 2 first-line agents of different classes |
| prevent-highrisk-treatment-threshold | PREVENT risk ≥7.5% and BP ≥130/80 mm Hg |
| ckd-albuminuria-raasi-threshold | eGFR <60 or albuminuria ≥30 mg/g |
| diabetes-mild-albuminuria-threshold | mild albuminuria <30 mg/g |
| acute-ich-presenting-sbp-range | presenting SBP 150 to 220 mm Hg |
| cognitive-prevention-sbp-goal | SBP goal <130 mm Hg |
| pregnancy-severe-bp-confirmation-interval | confirmed within 15 minutes |
| awake-out-of-office-high-bp-threshold | awake BP ≥130/80 mm Hg |
| full-day-out-of-office-high-bp-threshold | 24-hour BP ≥125/75 mm Hg |
| prompt-treatment-office-bp-threshold | office BP ≥160/100 mm Hg |
| secondary-diastolic-onset-age | diastolic hypertension onset at age ≥65 years |
| cpap-adherence-duration | CPAP use ≥4 hours/night |
| older-adult-treatment-age | age ≥80 years |
| young-adult-treatment-age | age <30 years |
| ckd-raasi-monitoring-interval | recheck electrolytes 2 to 4 weeks after starting or intensifying ACEi or ARB |
| ckd-raasi-egfr-continuation-threshold | ACEi or ARB can continue at eGFR <30 mL/min/1.73 m2 |
| gestational-htn-onset-week | begins at ≥20 weeks |
| gestational-severe-bp-threshold | persistent SBP ≥160 or DBP ≥110 mm Hg |

| chlorthalidone-dose-frequency | Chlorthalidone 12.5-25 mg/d; frequency 1 |
| hydrochlorothiazide-dose-frequency | Hydrochlorothiazide 25-50 mg/d; frequency 1 |
| indapamide-dose-frequency | Indapamide 1.25-2.5 mg/d; frequency 1 |
| benazepril-dose-frequency | Benazepril 10-40 mg/d; frequency 1 or 2 |
| captopril-dose-frequency | Captopril 12.5-150 mg/d; frequency 2 or 3 |
| enalapril-dose-frequency | Enalapril 5-40 mg/d; frequency 1 or 2 |
| fosinopril-dose-frequency | Fosinopril 10-40 mg/d; frequency 1 |
| lisinopril-dose-frequency | Lisinopril 10-40 mg/d; frequency 1 |
| moexipril-dose-frequency | Moexipril 7.5-30 mg/d; frequency 1 or 2 |
| perindopril-dose-frequency | Perindopril 4-16 mg/d; frequency 1 |
| quinapril-dose-frequency | Quinapril 10-80 mg/d; frequency 1 or 2 |
| ramipril-dose-frequency | Ramipril 2.5-20 mg/d; frequency 1 or 2 |
| trandolapril-dose-frequency | Trandolapril 1-4 mg/d; frequency 1 |
| azilsartan-dose-frequency | Azilsartan 40-80 mg/d; frequency 1 |
| candesartan-dose-frequency | Candesartan 8-32 mg/d; frequency 1 |
| eprosartan-dose-frequency | Eprosartan 600-800 mg/d; frequency 1 or 2 |
| irbesartan-dose-frequency | Irbesartan 150-300 mg/d; frequency 1 |
| losartan-dose-frequency | Losartan 50-100 mg/d; frequency 1 or 2 |
| olmesartan-dose-frequency | Olmesartan 20-40 mg/d; frequency 1 |
| telmisartan-dose-frequency | Telmisartan 20-80 mg/d; frequency 1 |
| valsartan-dose-frequency | Valsartan 80-320 mg/d; frequency 1 |
| amlodipine-dose-frequency | Amlodipine 2.5-10 mg/d; frequency 1 |
| felodipine-dose-frequency | Felodipine 2.5-10 mg/d; frequency 1 |
| isradipine-dose-frequency | Isradipine 5-10 mg/d; frequency 2 |
| nicardipine-sr-dose-frequency | Nicardipine SR 60-120 mg/d; frequency 2 |
| nifedipine-la-dose-frequency | Nifedipine LA 30-90 mg/d; frequency 1 |
| nisoldipine-dose-frequency | Nisoldipine 17-34 mg/d; frequency 1 |
| diltiazem-er-dose-frequency | Diltiazem ER 120-360 mg/d; frequency 1 |
| verapamil-ir-dose-frequency | Verapamil IR 120-360 mg/d; frequency 3 |
| verapamil-sr-dose-frequency | Verapamil SR 120-360 mg/d; frequency 1 or 2 |
| verapamil-delayed-onset-er-dose-frequency | Verapamil-delayed onset ER 100-300 mg/d; frequency 1 in the evening |
| bumetanide-dose-frequency | Bumetanide 0.5-2 mg/d; frequency 2 |
| furosemide-dose-frequency | Furosemide 20-80 mg/d; frequency 2 |
| torsemide-dose-frequency | Torsemide 5-10 mg/d; frequency 1 |
| amiloride-dose-frequency | Amiloride 5-10 mg/d; frequency 1 or 2 |
| triamterene-dose-frequency | Triamterene 50-100 mg/d; frequency 1 or 2 |
| eplerenone-dose-frequency | Eplerenone 50-100 mg/d; frequency 1 or 2 |
| spironolactone-dose-frequency | Spironolactone 25-100 mg/d; frequency 1 |
| atenolol-dose-frequency | Atenolol 25-100 mg/d; frequency 2 |
| betaxolol-dose-frequency | Betaxolol 5-20 mg/d; frequency 1 |
| bisoprolol-dose-frequency | Bisoprolol 2.5-10 mg/d; frequency 1 |
| metoprolol-tartrate-dose-frequency | Metoprolol tartrate 100-200 mg/d; frequency 2 |
| metoprolol-succinate-dose-frequency | Metoprolol succinate 50-200 mg/d; frequency 1 |
| nebivolol-dose-frequency | Nebivolol 5-40 mg/d; frequency 1 |
| nadolol-dose-frequency | Nadolol 40-120 mg/d; frequency 1 |
| propranolol-ir-dose-frequency | Propranolol IR 80-160 mg/d; frequency 2 |
| propranolol-la-dose-frequency | Propranolol LA 80-160 mg/d; frequency 1 |
| acebutolol-dose-frequency | Acebutolol 200-800 mg/d; frequency 2 |
| penbutolol-dose-frequency | Penbutolol 10-40 mg/d; frequency 1 |
| pindolol-dose-frequency | Pindolol 10-60 mg/d; frequency 2 |
| carvedilol-dose-frequency | Carvedilol 12.5-50 mg/d; frequency 2 |
| carvedilol-phosphate-dose-frequency | Carvedilol phosphate 20-80 mg/d; frequency 1 |
| labetalol-dose-frequency | Labetalol 200-1200 mg/d; frequency 2 |
| aliskiren-dose-frequency | Aliskiren 150-300 mg/d; frequency 1 |
| doxazosin-dose-frequency | Doxazosin 1-16 mg/d; frequency 1 |
| prazosin-dose-frequency | Prazosin 2-20 mg/d; frequency 2 or 3 |
| terazosin-dose-frequency | Terazosin 1-20 mg/d; frequency 1 or 2 |
| clonidine-oral-dose-frequency | Clonidine oral 0.1-0.8 mg/d; frequency 2 |
| clonidine-patch-dose-frequency | Clonidine patch 0.1-0.3 mg/d; frequency 1 weekly |
| methyldopa-dose-frequency | Methyldopa 250-1000 mg/d; frequency 2 |
| guanfacine-dose-frequency | Guanfacine 0.5-2 mg/d; frequency 1 |
| hydralazine-dose-frequency | Hydralazine 100-200 mg/d; frequency 2 or 3 |
| minoxidil-dose-frequency | Minoxidil 5-40 mg/d; frequency 1-2 |
| aprocitentan-dose-frequency | Aprocitentan 12.5 mg/d; frequency 1 |

| benazepril-hctz-dose | Benazepril + HCTZ 10/12.5; 20/12.5; 20/25 mg |
| captopril-hctz-dose | Captopril + HCTZ 25/15; 25/25; 50/15; 50/25 mg |
| enalapril-hctz-dose | Enalapril + HCTZ 5/12.5; 10/25 mg |
| fosinopril-hctz-dose | Fosinopril + HCTZ 10/12.5; 20/12.5 mg |
| lisinopril-hctz-dose | Lisinopril + HCTZ 10/12.5; 20/12.5; 20/25 mg |
| moexipril-hctz-dose | Moexipril + HCTZ 7.5/12.5; 15/12.5; 15/25 mg |
| quinapril-hctz-dose | Quinapril + HCTZ 10/12.5; 20/12.5; 20/25 mg |
| azilsartan-chlorthalidone-dose | Azilsartan + chlorthalidone 40/12.5; 40/25 mg |
| candesartan-hctz-dose | Candesartan + HCTZ 16/12.5; 32/12.5; 32/25 mg |
| irbesartan-hctz-dose | Irbesartan + HCTZ 150/12.5; 300/12.5; 300/25 mg |
| losartan-hctz-dose | Losartan + HCTZ 50/12.5; 100/12.5; 100/25 mg |
| olmesartan-hctz-dose | Olmesartan + HCTZ 20/12.5; 40/12.5; 40/25 mg |
| telmisartan-hctz-dose | Telmisartan + HCTZ 40/12.5; 80/12.5; 80/25 mg |
| valsartan-hctz-dose | Valsartan + HCTZ 80/12.5; 160/12.5; 160/25; 320/12.5; 320/25 mg |
| benazepril-amlodipine-dose | Benazepril + amlodipine 10/2.5; 10/5; 20/5; 20/10; 40/5; 40/10 mg |
| perindopril-amlodipine-dose | Perindopril + amlodipine 3.5/2.5; 7/5; 14/10 mg |
| trandolapril-verapamil-dose | Trandolapril + verapamil 1/240; 2/180; 2/240; 4/240 mg |
| olmesartan-amlodipine-dose | Olmesartan + amlodipine 20/5; 20/10; 40/5; 40/10 mg |
| telmisartan-amlodipine-dose | Telmisartan + amlodipine 40/5; 40/10; 80/5; 80/10 mg |
| valsartan-amlodipine-dose | Valsartan + amlodipine 160/5; 160/10; 320/5; 320/10 mg |
| valsartan-nebivolol-dose | Valsartan + nebivolol 80/5 mg |
| atenolol-chlorthalidone-dose | Atenolol + chlorthalidone 50/25; 100/25 mg |
| bisoprolol-hctz-dose | Bisoprolol + HCTZ 2.5/6.25; 4/6.25; 10/6.25 mg |
| metoprolol-hctz-dose | Metoprolol tartrate + HCTZ 50/25; 100/25; 100/50 mg |
| amiloride-hctz-dose | Amiloride + HCTZ 5/50 mg |
| triamterene-hctz-dose | Triamterene + HCTZ 37.5/25; 75/50 mg |
| spironolactone-hctz-dose | Spironolactone + HCTZ 25/25 mg |
| olmesartan-amlodipine-hctz-dose | Olmesartan + amlodipine + HCTZ 20/5/12.5; 40/5/12.5; 40/5/25; 40/10/12.5; 40/10/25 mg |
| valsartan-amlodipine-hctz-dose | Valsartan + amlodipine + HCTZ 160/5/12.5; 160/5/25; 160/10/12.5; 160/10/25; 320/10/25 mg |

| pregnancy-labetalol-maintenance-dose | Labetalol maintenance 200-2400 mg/d in 2-3 doses; start 100-200 mg twice daily |
| pregnancy-nifedipine-maintenance-dose | Nifedipine maintenance 30-120 mg/d; start 30-60 mg once daily |
| pregnancy-methyldopa-maintenance-dose | Methyldopa maintenance 500-3000 mg/d in 2-4 doses; start 250 mg 2-3 times daily |
| pregnancy-hctz-maintenance-dose | Hydrochlorothiazide 12.5-50 mg daily |
| pregnancy-labetalol-urgent-dose | Labetalol urgent dose 10-20 mg IV then 20-80 mg every 10-30 min, max 300 mg, or 1-3 mg/min |
| pregnancy-hydralazine-urgent-dose | Hydralazine urgent dose 5 mg then 5-10 mg every 20-40 min, max 20 mg, or 0.5-10 mg/h |
| pregnancy-nifedipine-urgent-dose | Nifedipine urgent dose 10-20 mg repeat in 20 min then every 2-6 h, max 180 mg/d |
| preeclampsia-bp-diagnostic-threshold | Preeclampsia BP ≥140/90 on 2 occasions at least 4 hours apart after 20 weeks |
| preeclampsia-proteinuria-24h-threshold | Proteinuria ≥300 mg per 24 hours |
| preeclampsia-protein-creatinine-threshold | Protein/creatinine ratio ≥0.3 |
| preeclampsia-dipstick-threshold | Dipstick 2+ |
| preeclampsia-platelet-threshold | Platelet count <100 × 109/L |
| preeclampsia-creatinine-threshold | Creatinine >1.1 mg/dL or doubling |
| preeclampsia-transaminase-threshold | Transaminases twice normal |
| resistant-spironolactone-dose | Spironolactone 25-50 mg/day as fourth drug |
| resistant-eplerenone-dose | Eplerenone 25-100 mg daily |
| resistant-amiloride-dose | Amiloride 10-20 mg |
| resistant-aprocitentan-dose | Aprocitentan 12.5 mg |
| emergency-nicardipine-dose | Nicardipine 5 mg/h plus 2.5 every 5 min, max 15 |
| emergency-clevidipine-dose | Clevidipine 1-2 mg/h, double every 90 seconds, max 21 mg/h for 72 hours |
| emergency-nitroprusside-dose | Nitroprusside 0.3-0.5 mcg/kg/min plus 0.5 every 5 min, max 10 |
| emergency-nitroglycerin-dose | Nitroglycerin 5 mcg/min plus 5 every 3-5 min, max 200 |
| emergency-hydralazine-dose | Hydralazine 10 mg IV, max initial 20, every 4-6 hours, max 200 mg/24 h |
| emergency-esmolol-dose | Esmolol 500-1000 mcg/kg/min over 1 min then 50 mcg/kg/min |
| emergency-labetalol-dose | Labetalol 0.3-1.0 mg/kg max 20 every 10 min or 0.4-1.0 mg/kg/h max 3 |
| emergency-phentolamine-dose | Phentolamine 5 mg IV every 10 min |
| emergency-fenoldopam-dose | Fenoldopam 0.1-0.3 mcg/kg/min increments 0.05-0.1 every 15 min max 1.6 |
| emergency-enalaprilat-dose | Enalaprilat 1.25 mg over 5 min up to 5 mg every 6 h |
| acute-coronary-bradycardia-cutoff | Bradycardia <60 beats/min |
| acute-coronary-hypotension-cutoff | Hypotension SBP <100 mm Hg |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| initial-combination-agent-count | adults-htn | 2 agents of different classes | "RENDERED: 2 first-line agents of different classes" | aha-2025 | p3 | p3/narrative/30 | narrative |
| severe-hypertension-threshold | adults | >180/120 mm Hg | "Severe hypertension in nonpregnant individuals, defined as blood pressure >180/120 mm Hg" | aha-2025 | p3 | p3/narrative/31 | narrative |
| prevent-highrisk-treatment-threshold | adults-htn-highrisk | PREVENT >=7.5% and BP >=130/80 mm Hg | "RENDERED: 10-year CVD risk ≥7.5% based on PREVENT, average systolic blood pressure ≥130 mm Hg, and average diastolic blood pressure ≥80 mm Hg" | aha-2025 | p4 | p4/narrative/1 | narrative |
| ckd-albuminuria-raasi-threshold | adults-ckd | eGFR <60 mL/min/1.73 m2 or albuminuria >=30 mg/g | "RENDERED: eGFR <60 mL/min/1.73 m2 or albuminuria ≥30 mg/g" | aha-2025 | p4 | p4/narrative/2 | narrative |
| diabetes-mild-albuminuria-threshold | adults-dm | <30 mg/g | "RENDERED: mild albuminuria <30 mg/g" | aha-2025 | p4 | p4/narrative/3 | narrative |
| acute-ich-presenting-sbp-range | adults-ich | 150-220 mm Hg | "RENDERED: presenting systolic blood pressure 150 to 220 mm Hg" | aha-2025 | p4 | p4/narrative/4 | narrative |
| cognitive-prevention-sbp-goal | adults-htn | <130 mm Hg | "RENDERED: systolic blood pressure goal <130 mm Hg" | aha-2025 | p5 | p5/narrative/1 | narrative |
| pregnancy-severe-bp-confirmation-interval | adults-pregnancy | within 15 minutes | "RENDERED: systolic blood pressure ≥160 mm Hg or diastolic blood pressure ≥110 mm Hg, confirmed within 15 minutes" | aha-2025 | p5 | p5/narrative/2 | narrative |
| awake-out-of-office-high-bp-threshold | adults | >=130/80 mm Hg | "RENDERED: awake SBP ≥130 mm Hg or DBP ≥80 mm Hg" | aha-2025 | p19 | p19/narrative/1 | narrative |
| full-day-out-of-office-high-bp-threshold | adults | >=125/75 mm Hg | "RENDERED: 24-hour SBP ≥125 mm Hg or DBP ≥75 mm Hg" | aha-2025 | p19 | p19/narrative/2 | narrative |
| prompt-treatment-office-bp-threshold | adults | >=160/100 mm Hg | "RENDERED: Office BP ≥160/100 mm Hg should prompt treatment and medication titration" | aha-2025 | p19 | p19/narrative/3 | narrative |
| secondary-diastolic-onset-age | adults-htn | >=65 years | "RENDERED: onset of diastolic hypertension at age ≥65 years" | aha-2025 | p23 | p23/narrative/1 | narrative |
| cpap-adherence-duration | adults-htn | >=4 hours/night | "RENDERED: CPAP use ≥4 hours/night" | aha-2025 | p27 | p27/narrative/1 | narrative |
| older-adult-treatment-age | adults-htn | >=80 years | "RENDERED: For age ≥80 years, initiate at ≥130/80 mm Hg when benefits outweigh harms" | aha-2025 | p35 | p35/narrative/1 | narrative |
| young-adult-treatment-age | adults-htn | <30 years | "RENDERED: For age <30 years, medication may be considered at average SBP ≥130 mm Hg after lifestyle intervention" | aha-2025 | p35 | p35/narrative/2 | narrative |
| ckd-raasi-monitoring-interval | adults-ckd | 2-4 weeks | "RENDERED: recheck electrolytes 2 to 4 weeks after starting or intensifying ACEi or ARB" | aha-2025 | p51 | p51/narrative/1 | narrative |
| ckd-raasi-egfr-continuation-threshold | adults-ckd | <30 mL/min/1.73 m2 | "RENDERED: ACEi or ARB can continue at eGFR <30 mL/min/1.73 m2" | aha-2025 | p51 | p51/narrative/2 | narrative |
| gestational-htn-onset-week | adults-pregnancy | >=20 weeks | "RENDERED: Gestational hypertension begins at ≥20 weeks" | aha-2025 | p61 | p61/narrative/1 | narrative |
| gestational-severe-bp-threshold | adults-pregnancy | persistent >=160/110 mm Hg | "RENDERED: Severe-range gestational BP is persistent SBP ≥160 or DBP ≥110 mm Hg" | aha-2025 | p61 | p61/narrative/2 | narrative |
| pregnancy-labetalol-maintenance-dose | adults-pregnancy | 200-2400 mg/d in 2-3 doses; start 100-200 mg twice daily | "Labetalol 200-2400 mg/d orally in 2 to 3 divided doses. Commonly initiated at 100-200 mg twice daily." | aha-2025 | p62 | p62/narrative/301 | narrative |
| pregnancy-nifedipine-maintenance-dose | adults-pregnancy | 30-120 mg/d; start 30-60 mg once daily | "RENDERED: Nifedipine 30-120 mg/d orally of an extended-release preparation. Commonly initiated at 30-60 mg once daily" | aha-2025 | p62 | p62/narrative/302 | narrative |
| pregnancy-methyldopa-maintenance-dose | adults-pregnancy | 500-3000 mg/d in 2-4 doses; start 250 mg 2-3 times daily | "Methyldopa 500-3000 mg/d orally in 2 to 4 divided doses. Commonly initiated at 250 mg 2 or 3 times daily." | aha-2025 | p62 | p62/narrative/303 | narrative |
| pregnancy-hctz-maintenance-dose | adults-pregnancy | 12.5-50 mg daily | "Hydrochlorothiazide 12.5-50 mg daily" | aha-2025 | p62 | p62/narrative/304 | narrative |
| pregnancy-labetalol-urgent-dose | adults-pregnancy | 10-20 mg IV; then 20-80 mg every 10-30 min; max 300 mg; or 1-3 mg/min | "Labetalol 10-20 mg IV, then 20-80 mg every 10-30 min to a maximum cumulative dosage of 300 mg; or constant infusion 1-3 mg/min IV" | aha-2025 | p62 | p62/narrative/305 | narrative |
| pregnancy-hydralazine-urgent-dose | adults-pregnancy | 5 mg IV or IM; then 5-10 mg every 20-40 min; max 20 mg; or 0.5-10 milligrams/hour | "Hydralazine 5 mg IV or IM, then 5-10 mg IV every 20-40 min to a maximum cumulative dosage of 20 mg; or constant infusion of 0.5-10 mg/h" | aha-2025 | p62 | p62/narrative/306 | narrative |
| pregnancy-nifedipine-urgent-dose | adults-pregnancy | 10-20 mg; repeat in 20 min; then every 2-6 h; max 180 mg/d | "RENDERED: Nifedipine (immediate release) 10-20 mg orally, repeat in 20 min if needed; then 10-20 mg every 2-6 h; maximum daily dose is 180 mg" | aha-2025 | p62 | p62/narrative/307 | narrative |
| preeclampsia-bp-diagnostic-threshold | adults-pregnancy | >=140/90 mm Hg on 2 occasions >=4 h apart after 20 weeks | "RENDERED: SBP ≥140 mm Hg or DBP ≥90 mm Hg on 2 occasions at least 4 h apart after 20 wks of gestation" | aha-2025 | p63 | p63/narrative/301 | narrative |
| preeclampsia-proteinuria-24h-threshold | adults-pregnancy | >=300 mg/24 h | "Proteinuria ≥300 mg per 24-h urine collection" | aha-2025 | p63 | p63/narrative/302 | narrative |
| preeclampsia-protein-creatinine-threshold | adults-pregnancy | >=0.3 | "RENDERED: Protein/creatinine ratio ≥0.3" | aha-2025 | p63 | p63/narrative/303 | narrative |
| preeclampsia-dipstick-threshold | adults-pregnancy | 2+ | "Dipstick reading of 2+" | aha-2025 | p63 | p63/narrative/304 | narrative |
| preeclampsia-platelet-threshold | adults-pregnancy | <100 x 109/L | "Platelet count <100 × 109/L" | aha-2025 | p63 | p63/narrative/305 | narrative |
| preeclampsia-creatinine-threshold | adults-pregnancy | >1.1 mg/dL or doubling | "RENDERED: Serum creatinine concentrations >1.1 mg/dL or a doubling of serum creatinine concentration" | aha-2025 | p63 | p63/narrative/306 | narrative |
| preeclampsia-transaminase-threshold | adults-pregnancy | twice normal | "RENDERED: liver transaminases to twice normal concentration" | aha-2025 | p63 | p63/narrative/307 | narrative |
| resistant-spironolactone-dose | adults-resistant-htn | 25-50 mg/day | "RENDERED: addition of spironolactone (25-50 mg/day) as the fourth drug" | aha-2025 | p64 | p64/narrative/301 | narrative |
| resistant-eplerenone-dose | adults-resistant-htn | 25-100 mg daily | "doses between 25 and 100 mg daily" | aha-2025 | p64 | p64/narrative/302 | narrative |
| resistant-amiloride-dose | adults-resistant-htn | 10-20 mg | "amiloride (10-20 mg) has been shown to be as effective as spironolactone" | aha-2025 | p64 | p64/narrative/303 | narrative |
| resistant-aprocitentan-dose | adults-resistant-htn | 12.5 mg | "12.5 mg (FDA-approved dose)" | aha-2025 | p64 | p64/narrative/304 | narrative |
| emergency-nicardipine-dose | adults-htn-emergency | initial 5 mg/h; +2.5 mg/h every 5 min; max 15 mg/h | "Nicardipine Initial 5 mg/h, increasing every 5 min by 2.5 mg/h to maximum 15 mg/h" | aha-2025 | p69 | p69/narrative/301 | narrative |
| emergency-clevidipine-dose | adults-htn-emergency | initial 1-2 mg/h; double every 90 s; max 21 mg/h for 72 h | "Clevidipine Initial 1-2 mg/h, doubling every 90 s until BP approaches target, then increasing by less than double every 5-10 min; maximum dose 21 mg/h; maximum duration 72 h" | aha-2025 | p69 | p69/narrative/302 | narrative |
| emergency-nitroprusside-dose | adults-htn-emergency | initial 0.3-0.5 mcg/kg/min; +0.5 every 5 min; max 10 | "RENDERED: Initial 0.3-0.5 mcg/kg/min; increase in increments of 0.5 mcg/kg/min every 5 min to achieve BP target; maximum dose 10 mcg/kg/min" | aha-2025 | p69 | p69/narrative/303 | narrative |
| emergency-nitroglycerin-dose | adults-htn-emergency | initial 5 mcg/min; +5 every 3-5 min; max 200 | "Nitroglycerin Initial 5 mcg/min; increase in increments of 5 mcg/min every 3-5 min to a maximum rate of 200 mcg/min" | aha-2025 | p69 | p69/narrative/304 | narrative |
| emergency-hydralazine-dose | adults-htn-emergency | initial 10 mg IV; max initial 20 mg; every 4-6 h; max 200 mg/24 h | "Hydralazine Initial 10 mg via slow IV infusion (maximum initial dose 20 mg); repeat every 4-6 h as needed. Adjust rate up to total cumulative dose of 200 mg/24 h" | aha-2025 | p69 | p69/narrative/305 | narrative |
| emergency-esmolol-dose | adults-htn-emergency | 500-1000 mcg/kg/min over 1 min; then 50 mcg/kg/min | "Esmolol Loading dose 500-1000 mcg/kg/min over 1 min followed by a 50-mcg/kg/min infusion" | aha-2025 | p69 | p69/narrative/306 | narrative |
| emergency-labetalol-dose | adults-htn-emergency | 0.3-1.0 milligrams/kilogram; max 20 mg; every 10 min or 0.4-1.0 milligrams/kilogram/hour; max 3 mg/kg/h | "RENDERED: Labetalol Initial 0.3- to 1.0-mg/kg dose (maximum 20 mg) slow IV injection at 10-min intervals or 0.4-1.0-mg/kg/h IV infusion up to 3 mg/kg/h" | aha-2025 | p69 | p69/narrative/307 | narrative |
| emergency-phentolamine-dose | adults-htn-emergency | 5 mg IV; repeat every 10 min | "Phentolamine IV bolus dose 5 mg. Additional bolus doses every 10 min as needed to lower BP to target." | aha-2025 | p69 | p69/narrative/308 | narrative |
| emergency-fenoldopam-dose | adults-htn-emergency | initial 0.1-0.3 mcg/kg/min; +0.05-0.1 every 15 min; max 1.6 | "RENDERED: Fenoldopam Initial 0.1-0.3 mcg/kg/min; may be increased in increments of 0.05-0.1 mcg/kg/min every 15 min until target BP is reached. Maximum infusion rate 1.6 mcg/kg/min" | aha-2025 | p69 | p69/narrative/309 | narrative |
| emergency-enalaprilat-dose | adults-htn-emergency | 1.25 mg over 5 min; up to 5 mg every 6 h | "Enalaprilat Initial 1.25 mg over a 5-min period. Doses can be increased up to 5 mg every 6 h as needed" | aha-2025 | p69 | p69/narrative/310 | narrative |
| acute-coronary-bradycardia-cutoff | adults-htn-emergency | <60 beats/min | "bradycardia (<60 beats/min)" | aha-2025 | p70 | p70/narrative/301 | narrative |
| acute-coronary-hypotension-cutoff | adults-htn-emergency | SBP <100 mm Hg | "hypotension (SBP <100 mm Hg)" | aha-2025 | p70 | p70/narrative/302 | narrative |
| benazepril-hctz-dose | adults-htn | 10/12.5; 20/12.5; 20/25 milligram combinations | "RENDERED: Benazepril + HCTZ 10/12.5; 20/12.5; 20/25 mg" | aha-2025 | p42 | p42/narrative/201 | narrative |
| captopril-hctz-dose | adults-htn | 25/15; 25/25; 50/15; 50/25 milligram combinations | "RENDERED: Captopril + HCTZ 25/15; 25/25; 50/15; 50/25 mg" | aha-2025 | p42 | p42/narrative/202 | narrative |
| enalapril-hctz-dose | adults-htn | 5/12.5; 10/25 milligram combinations | "RENDERED: Enalapril + HCTZ 5/12.5; 10/25 mg" | aha-2025 | p42 | p42/narrative/203 | narrative |
| fosinopril-hctz-dose | adults-htn | 10/12.5; 20/12.5 milligram combinations | "RENDERED: Fosinopril + HCTZ 10/12.5; 20/12.5 mg" | aha-2025 | p42 | p42/narrative/204 | narrative |
| lisinopril-hctz-dose | adults-htn | 10/12.5; 20/12.5; 20/25 milligram combinations | "RENDERED: Lisinopril + HCTZ 10/12.5; 20/12.5; 20/25 mg" | aha-2025 | p42 | p42/narrative/205 | narrative |
| moexipril-hctz-dose | adults-htn | 7.5/12.5; 15/12.5; 15/25 milligram combinations | "RENDERED: Moexipril + HCTZ 7.5/12.5; 15/12.5; 15/25 mg" | aha-2025 | p42 | p42/narrative/206 | narrative |
| quinapril-hctz-dose | adults-htn | 10/12.5; 20/12.5; 20/25 milligram combinations | "RENDERED: Quinapril + HCTZ 10/12.5; 20/12.5; 20/25 mg" | aha-2025 | p42 | p42/narrative/207 | narrative |
| azilsartan-chlorthalidone-dose | adults-htn | 40/12.5; 40/25 milligram combinations | "RENDERED: Azilsartan + chlorthalidone 40/12.5; 40/25 mg" | aha-2025 | p42 | p42/narrative/208 | narrative |
| candesartan-hctz-dose | adults-htn | 16/12.5; 32/12.5; 32/25 milligram combinations | "RENDERED: Candesartan + HCTZ 16/12.5; 32/12.5; 32/25 mg" | aha-2025 | p42 | p42/narrative/209 | narrative |
| irbesartan-hctz-dose | adults-htn | 150/12.5; 300/12.5; 300/25 milligram combinations | "RENDERED: Irbesartan + HCTZ 150/12.5; 300/12.5; 300/25 mg" | aha-2025 | p42 | p42/narrative/210 | narrative |
| losartan-hctz-dose | adults-htn | 50/12.5; 100/12.5; 100/25 milligram combinations | "RENDERED: Losartan + HCTZ 50/12.5; 100/12.5; 100/25 mg" | aha-2025 | p42 | p42/narrative/211 | narrative |
| olmesartan-hctz-dose | adults-htn | 20/12.5; 40/12.5; 40/25 milligram combinations | "RENDERED: Olmesartan + HCTZ 20/12.5; 40/12.5; 40/25 mg" | aha-2025 | p42 | p42/narrative/212 | narrative |
| telmisartan-hctz-dose | adults-htn | 40/12.5; 80/12.5; 80/25 milligram combinations | "RENDERED: Telmisartan + HCTZ 40/12.5; 80/12.5; 80/25 mg" | aha-2025 | p42 | p42/narrative/213 | narrative |
| valsartan-hctz-dose | adults-htn | 80/12.5; 160/12.5; 160/25; 320/12.5; 320/25 milligram combinations | "RENDERED: Valsartan + HCTZ 80/12.5; 160/12.5; 160/25; 320/12.5; 320/25 mg" | aha-2025 | p42 | p42/narrative/214 | narrative |
| benazepril-amlodipine-dose | adults-htn | 10/2.5; 10/5; 20/5; 20/10; 40/5; 40/10 milligram combinations | "RENDERED: Benazepril + amlodipine 10/2.5; 10/5; 20/5; 20/10; 40/5; 40/10 mg" | aha-2025 | p42 | p42/narrative/215 | narrative |
| perindopril-amlodipine-dose | adults-htn | 3.5/2.5; 7/5; 14/10 milligram combinations | "RENDERED: Perindopril + amlodipine 3.5/2.5; 7/5; 14/10 mg" | aha-2025 | p43 | p43/narrative/201 | narrative |
| trandolapril-verapamil-dose | adults-htn | 1/240; 2/180; 2/240; 4/240 milligram combinations | "RENDERED: Trandolapril + verapamil 1/240; 2/180; 2/240; 4/240 mg" | aha-2025 | p43 | p43/narrative/202 | narrative |
| olmesartan-amlodipine-dose | adults-htn | 20/5; 20/10; 40/5; 40/10 milligram combinations | "RENDERED: Olmesartan + amlodipine 20/5; 20/10; 40/5; 40/10 mg" | aha-2025 | p43 | p43/narrative/203 | narrative |
| telmisartan-amlodipine-dose | adults-htn | 40/5; 40/10; 80/5; 80/10 milligram combinations | "RENDERED: Telmisartan + amlodipine 40/5; 40/10; 80/5; 80/10 mg" | aha-2025 | p43 | p43/narrative/204 | narrative |
| valsartan-amlodipine-dose | adults-htn | 160/5; 160/10; 320/5; 320/10 milligram combinations | "RENDERED: Valsartan + amlodipine 160/5; 160/10; 320/5; 320/10 mg" | aha-2025 | p43 | p43/narrative/205 | narrative |
| valsartan-nebivolol-dose | adults-htn | 80/5 milligram combinations | "RENDERED: Valsartan + nebivolol 80/5 mg" | aha-2025 | p43 | p43/narrative/206 | narrative |
| atenolol-chlorthalidone-dose | adults-htn | 50/25; 100/25 milligram combinations | "RENDERED: Atenolol + chlorthalidone 50/25; 100/25 mg" | aha-2025 | p43 | p43/narrative/207 | narrative |
| bisoprolol-hctz-dose | adults-htn | 2.5/6.25; 4/6.25; 10/6.25 milligram combinations | "RENDERED: Bisoprolol + HCTZ 2.5/6.25; 4/6.25; 10/6.25 mg" | aha-2025 | p43 | p43/narrative/208 | narrative |
| metoprolol-hctz-dose | adults-htn | 50/25; 100/25; 100/50 milligram combinations | "RENDERED: Metoprolol tartrate + HCTZ 50/25; 100/25; 100/50 mg" | aha-2025 | p43 | p43/narrative/209 | narrative |
| amiloride-hctz-dose | adults-htn | 5/50 milligram combinations | "RENDERED: Amiloride + HCTZ 5/50 mg" | aha-2025 | p43 | p43/narrative/210 | narrative |
| triamterene-hctz-dose | adults-htn | 37.5/25; 75/50 milligram combinations | "RENDERED: Triamterene + HCTZ 37.5/25; 75/50 mg" | aha-2025 | p43 | p43/narrative/211 | narrative |
| spironolactone-hctz-dose | adults-htn | 25/25 milligram combinations | "RENDERED: Spironolactone + HCTZ 25/25 mg" | aha-2025 | p43 | p43/narrative/212 | narrative |
| olmesartan-amlodipine-hctz-dose | adults-htn | 20/5/12.5; 40/5/12.5; 40/5/25; 40/10/12.5; 40/10/25 milligram combinations | "RENDERED: Olmesartan + amlodipine + HCTZ 20/5/12.5; 40/5/12.5; 40/5/25; 40/10/12.5; 40/10/25 mg" | aha-2025 | p43 | p43/narrative/213 | narrative |
| valsartan-amlodipine-hctz-dose | adults-htn | 160/5/12.5; 160/5/25; 160/10/12.5; 160/10/25; 320/10/25 milligram combinations | "RENDERED: Valsartan + amlodipine + HCTZ 160/5/12.5; 160/5/25; 160/10/12.5; 160/10/25; 320/10/25 mg" | aha-2025 | p43 | p43/narrative/214 | narrative |
| chlorthalidone-dose-frequency | adults-htn | 12.5-25 milligrams/day; frequency 1 | "RENDERED: Chlorthalidone 12.5-25 mg/d 1" | aha-2025 | p37 | p37/narrative/101 | narrative |
| hydrochlorothiazide-dose-frequency | adults-htn | 25-50 milligrams/day; frequency 1 | "RENDERED: Hydrochlorothiazide 25-50 mg/d 1" | aha-2025 | p37 | p37/narrative/102 | narrative |
| indapamide-dose-frequency | adults-htn | 1.25-2.5 milligrams/day; frequency 1 | "RENDERED: Indapamide 1.25-2.5 mg/d 1" | aha-2025 | p37 | p37/narrative/103 | narrative |
| benazepril-dose-frequency | adults-htn | 10-40 milligrams/day; frequency 1 or 2 | "RENDERED: Benazepril 10-40 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/104 | narrative |
| captopril-dose-frequency | adults-htn | 12.5-150 milligrams/day; frequency 2 or 3 | "RENDERED: Captopril 12.5-150 mg/d 2 or 3" | aha-2025 | p37 | p37/narrative/105 | narrative |
| enalapril-dose-frequency | adults-htn | 5-40 milligrams/day; frequency 1 or 2 | "RENDERED: Enalapril 5-40 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/106 | narrative |
| fosinopril-dose-frequency | adults-htn | 10-40 milligrams/day; frequency 1 | "RENDERED: Fosinopril 10-40 mg/d 1" | aha-2025 | p37 | p37/narrative/107 | narrative |
| lisinopril-dose-frequency | adults-htn | 10-40 milligrams/day; frequency 1 | "RENDERED: Lisinopril 10-40 mg/d 1" | aha-2025 | p37 | p37/narrative/108 | narrative |
| moexipril-dose-frequency | adults-htn | 7.5-30 milligrams/day; frequency 1 or 2 | "RENDERED: Moexipril 7.5-30 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/109 | narrative |
| perindopril-dose-frequency | adults-htn | 4-16 milligrams/day; frequency 1 | "RENDERED: Perindopril 4-16 mg/d 1" | aha-2025 | p37 | p37/narrative/110 | narrative |
| quinapril-dose-frequency | adults-htn | 10-80 milligrams/day; frequency 1 or 2 | "RENDERED: Quinapril 10-80 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/111 | narrative |
| ramipril-dose-frequency | adults-htn | 2.5-20 milligrams/day; frequency 1 or 2 | "RENDERED: Ramipril 2.5-20 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/112 | narrative |
| trandolapril-dose-frequency | adults-htn | 1-4 milligrams/day; frequency 1 | "RENDERED: Trandolapril 1-4 mg/d 1" | aha-2025 | p37 | p37/narrative/113 | narrative |
| azilsartan-dose-frequency | adults-htn | 40-80 milligrams/day; frequency 1 | "RENDERED: Azilsartan 40-80 mg/d 1" | aha-2025 | p37 | p37/narrative/114 | narrative |
| candesartan-dose-frequency | adults-htn | 8-32 milligrams/day; frequency 1 | "RENDERED: Candesartan 8-32 mg/d 1" | aha-2025 | p37 | p37/narrative/115 | narrative |
| eprosartan-dose-frequency | adults-htn | 600-800 milligrams/day; frequency 1 or 2 | "RENDERED: Eprosartan 600-800 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/116 | narrative |
| irbesartan-dose-frequency | adults-htn | 150-300 milligrams/day; frequency 1 | "RENDERED: Irbesartan 150-300 mg/d 1" | aha-2025 | p37 | p37/narrative/117 | narrative |
| losartan-dose-frequency | adults-htn | 50-100 milligrams/day; frequency 1 or 2 | "RENDERED: Losartan 50-100 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/118 | narrative |
| olmesartan-dose-frequency | adults-htn | 20-40 milligrams/day; frequency 1 | "RENDERED: Olmesartan 20-40 mg/d 1" | aha-2025 | p37 | p37/narrative/119 | narrative |
| telmisartan-dose-frequency | adults-htn | 20-80 milligrams/day; frequency 1 | "RENDERED: Telmisartan 20-80 mg/d 1" | aha-2025 | p37 | p37/narrative/120 | narrative |
| valsartan-dose-frequency | adults-htn | 80-320 milligrams/day; frequency 1 | "RENDERED: Valsartan 80-320 mg/d 1" | aha-2025 | p37 | p37/narrative/121 | narrative |
| amlodipine-dose-frequency | adults-htn | 2.5-10 milligrams/day; frequency 1 | "RENDERED: Amlodipine 2.5-10 mg/d 1" | aha-2025 | p37 | p37/narrative/122 | narrative |
| felodipine-dose-frequency | adults-htn | 2.5-10 milligrams/day; frequency 1 | "RENDERED: Felodipine 2.5-10 mg/d 1" | aha-2025 | p37 | p37/narrative/123 | narrative |
| isradipine-dose-frequency | adults-htn | 5-10 milligrams/day; frequency 2 | "RENDERED: Isradipine 5-10 mg/d 2" | aha-2025 | p37 | p37/narrative/124 | narrative |
| nicardipine-sr-dose-frequency | adults-htn | 60-120 milligrams/day; frequency 2 | "RENDERED: Nicardipine SR 60-120 mg/d 2" | aha-2025 | p37 | p37/narrative/125 | narrative |
| nifedipine-la-dose-frequency | adults-htn | 30-90 milligrams/day; frequency 1 | "RENDERED: Nifedipine LA 30-90 mg/d 1" | aha-2025 | p37 | p37/narrative/126 | narrative |
| nisoldipine-dose-frequency | adults-htn | 17-34 milligrams/day; frequency 1 | "RENDERED: Nisoldipine 17-34 mg/d 1" | aha-2025 | p37 | p37/narrative/127 | narrative |
| diltiazem-er-dose-frequency | adults-htn | 120-360 milligrams/day; frequency 1 | "RENDERED: Diltiazem ER 120-360 mg/d 1" | aha-2025 | p37 | p37/narrative/128 | narrative |
| verapamil-ir-dose-frequency | adults-htn | 120-360 milligrams/day; frequency 3 | "RENDERED: Verapamil IR 120-360 mg/d 3" | aha-2025 | p37 | p37/narrative/129 | narrative |
| verapamil-sr-dose-frequency | adults-htn | 120-360 milligrams/day; frequency 1 or 2 | "RENDERED: Verapamil SR 120-360 mg/d 1 or 2" | aha-2025 | p37 | p37/narrative/130 | narrative |
| verapamil-delayed-onset-er-dose-frequency | adults-htn | 100-300 milligrams/day; frequency 1 in the evening | "RENDERED: Verapamil-delayed onset ER 100-300 mg/d 1 in the evening" | aha-2025 | p37 | p37/narrative/131 | narrative |
| bumetanide-dose-frequency | adults-htn | 0.5-2 milligrams/day; frequency 2 | "RENDERED: Bumetanide 0.5-2 mg/d 2" | aha-2025 | p37 | p37/narrative/132 | narrative |
| furosemide-dose-frequency | adults-htn | 20-80 milligrams/day; frequency 2 | "RENDERED: Furosemide 20-80 mg/d 2" | aha-2025 | p37 | p37/narrative/133 | narrative |
| torsemide-dose-frequency | adults-htn | 5-10 milligrams/day; frequency 1 | "RENDERED: Torsemide 5-10 mg/d 1" | aha-2025 | p37 | p37/narrative/134 | narrative |
| amiloride-dose-frequency | adults-htn | 5-10 milligrams/day; frequency 1 or 2 | "RENDERED: Amiloride 5-10 mg/d 1 or 2" | aha-2025 | p38 | p38/narrative/101 | narrative |
| triamterene-dose-frequency | adults-htn | 50-100 milligrams/day; frequency 1 or 2 | "RENDERED: Triamterene 50-100 mg/d 1 or 2" | aha-2025 | p38 | p38/narrative/102 | narrative |
| eplerenone-dose-frequency | adults-htn | 50-100 milligrams/day; frequency 1 or 2 | "RENDERED: Eplerenone 50-100 mg/d 1 or 2" | aha-2025 | p38 | p38/narrative/103 | narrative |
| spironolactone-dose-frequency | adults-htn | 25-100 milligrams/day; frequency 1 | "RENDERED: Spironolactone 25-100 mg/d 1" | aha-2025 | p38 | p38/narrative/104 | narrative |
| atenolol-dose-frequency | adults-htn | 25-100 milligrams/day; frequency 2 | "RENDERED: Atenolol 25-100 mg/d 2" | aha-2025 | p38 | p38/narrative/105 | narrative |
| betaxolol-dose-frequency | adults-htn | 5-20 milligrams/day; frequency 1 | "RENDERED: Betaxolol 5-20 mg/d 1" | aha-2025 | p38 | p38/narrative/106 | narrative |
| bisoprolol-dose-frequency | adults-htn | 2.5-10 milligrams/day; frequency 1 | "RENDERED: Bisoprolol 2.5-10 mg/d 1" | aha-2025 | p38 | p38/narrative/107 | narrative |
| metoprolol-tartrate-dose-frequency | adults-htn | 100-200 milligrams/day; frequency 2 | "RENDERED: Metoprolol tartrate 100-200 mg/d 2" | aha-2025 | p38 | p38/narrative/108 | narrative |
| metoprolol-succinate-dose-frequency | adults-htn | 50-200 milligrams/day; frequency 1 | "RENDERED: Metoprolol succinate 50-200 mg/d 1" | aha-2025 | p38 | p38/narrative/109 | narrative |
| nebivolol-dose-frequency | adults-htn | 5-40 milligrams/day; frequency 1 | "RENDERED: Nebivolol 5-40 mg/d 1" | aha-2025 | p38 | p38/narrative/110 | narrative |
| nadolol-dose-frequency | adults-htn | 40-120 milligrams/day; frequency 1 | "RENDERED: Nadolol 40-120 mg/d 1" | aha-2025 | p38 | p38/narrative/111 | narrative |
| propranolol-ir-dose-frequency | adults-htn | 80-160 milligrams/day; frequency 2 | "RENDERED: Propranolol IR 80-160 mg/d 2" | aha-2025 | p38 | p38/narrative/112 | narrative |
| propranolol-la-dose-frequency | adults-htn | 80-160 milligrams/day; frequency 1 | "RENDERED: Propranolol LA 80-160 mg/d 1" | aha-2025 | p38 | p38/narrative/113 | narrative |
| acebutolol-dose-frequency | adults-htn | 200-800 milligrams/day; frequency 2 | "RENDERED: Acebutolol 200-800 mg/d 2" | aha-2025 | p38 | p38/narrative/114 | narrative |
| penbutolol-dose-frequency | adults-htn | 10-40 milligrams/day; frequency 1 | "RENDERED: Penbutolol 10-40 mg/d 1" | aha-2025 | p38 | p38/narrative/115 | narrative |
| pindolol-dose-frequency | adults-htn | 10-60 milligrams/day; frequency 2 | "RENDERED: Pindolol 10-60 mg/d 2" | aha-2025 | p38 | p38/narrative/116 | narrative |
| carvedilol-dose-frequency | adults-htn | 12.5-50 milligrams/day; frequency 2 | "RENDERED: Carvedilol 12.5-50 mg/d 2" | aha-2025 | p38 | p38/narrative/117 | narrative |
| carvedilol-phosphate-dose-frequency | adults-htn | 20-80 milligrams/day; frequency 1 | "RENDERED: Carvedilol phosphate 20-80 mg/d 1" | aha-2025 | p38 | p38/narrative/118 | narrative |
| labetalol-dose-frequency | adults-htn | 200-1200 milligrams/day; frequency 2 | "RENDERED: Labetalol 200-1200 mg/d 2" | aha-2025 | p38 | p38/narrative/119 | narrative |
| aliskiren-dose-frequency | adults-htn | 150-300 milligrams/day; frequency 1 | "RENDERED: Aliskiren 150-300 mg/d 1" | aha-2025 | p38 | p38/narrative/120 | narrative |
| doxazosin-dose-frequency | adults-htn | 1-16 milligrams/day; frequency 1 | "RENDERED: Doxazosin 1-16 mg/d 1" | aha-2025 | p38 | p38/narrative/121 | narrative |
| prazosin-dose-frequency | adults-htn | 2-20 milligrams/day; frequency 2 or 3 | "RENDERED: Prazosin 2-20 mg/d 2 or 3" | aha-2025 | p38 | p38/narrative/122 | narrative |
| terazosin-dose-frequency | adults-htn | 1-20 milligrams/day; frequency 1 or 2 | "RENDERED: Terazosin 1-20 mg/d 1 or 2" | aha-2025 | p38 | p38/narrative/123 | narrative |
| clonidine-oral-dose-frequency | adults-htn | 0.1-0.8 milligrams/day; frequency 2 | "RENDERED: Clonidine oral 0.1-0.8 mg/d 2" | aha-2025 | p39 | p39/narrative/101 | narrative |
| clonidine-patch-dose-frequency | adults-htn | 0.1-0.3 milligrams/day; frequency 1 weekly | "RENDERED: Clonidine patch 0.1-0.3 mg/d 1 weekly" | aha-2025 | p39 | p39/narrative/102 | narrative |
| methyldopa-dose-frequency | adults-htn | 250-1000 milligrams/day; frequency 2 | "RENDERED: Methyldopa 250-1000 mg/d 2" | aha-2025 | p39 | p39/narrative/103 | narrative |
| guanfacine-dose-frequency | adults-htn | 0.5-2 milligrams/day; frequency 1 | "RENDERED: Guanfacine 0.5-2 mg/d 1" | aha-2025 | p39 | p39/narrative/104 | narrative |
| hydralazine-dose-frequency | adults-htn | 100-200 milligrams/day; frequency 2 or 3 | "RENDERED: Hydralazine 100-200 mg/d 2 or 3" | aha-2025 | p39 | p39/narrative/105 | narrative |
| minoxidil-dose-frequency | adults-htn | 5-40 milligrams/day; frequency 1-2 | "RENDERED: Minoxidil 5-40 mg/d 1-2" | aha-2025 | p39 | p39/narrative/106 | narrative |
| aprocitentan-dose-frequency | adults-htn | 12.5 milligrams/day; frequency 1 | "RENDERED: Aprocitentan 12.5 mg/d 1" | aha-2025 | p39 | p39/narrative/107 | narrative |
| bp-treatment-goal | adults | <130/80 mm Hg | "blood pressure treatment goal is <130/80 mm Hg for all adults" | aha-2025 | p3 | p3/narrative/1 | narrative |
| office-bp-normal | adults | <120/<80 mm Hg | "normal blood pressure is defined as <120 mm Hg systolic and <80 mm Hg diastolic" | aha-2025 | p3 | p3/narrative/2 | narrative |
| office-bp-elevated | adults | 120-129/<80 mm Hg | "elevated blood pressure as 120 to 129 mm Hg systolic and <80 mm Hg diastolic" | aha-2025 | p3 | p3/narrative/3 | narrative |
| office-bp-stage-1 | adults | 130-139/80-89 mm Hg | "RENDERED: stage 1 hypertension as 130 to 139 mm Hg systolic or 80 to 89 mm Hg diastolic" | aha-2025 | p3 | p3/narrative/4 | narrative |
| office-bp-stage-2 | adults | >=140/90 mm Hg | "stage 2 hypertension as ≥140 mm Hg systolic or ≥90 mm Hg diastolic" | aha-2025 | p3 | p3/narrative/5 | narrative |
| prevent-age-range | adults-htn | 30-79 years | "PREVENT is applicable to adults aged 30 to 79 years" | aha-2025 | p9 | p9/narrative/1 | narrative |
| office-bp-reading-count | adults | >=2 measurements on >=2 occasions | "RENDERED: an average of ≥2 BP measurements obtained on ≥2 separate occasions" | aha-2025 | p14 | p14/narrative/1 | narrative |
| bp-measurement-trigger-avoidance | adults | >=30 minutes | "RENDERED: avoid caffeine, exercise, and smoking for at least 30 minutes before measurement" | aha-2025 | p14 | p14/narrative/2 | narrative |
| bp-measurement-rest-period | adults | >5 minutes | "RENDERED: Have the patient relax, sitting in a chair (feet on floor, legs uncrossed, and back supported) for more than 5 minutes of rest" | aha-2025 | p14 | p14/narrative/3 | narrative |
| bp-measurement-repeat-interval | adults | >=2 measurements >=1 minute apart | "RENDERED: Take 2 or more blood pressure measurements at least 1 minute apart" | aha-2025 | p14 | p14/narrative/4 | narrative |
| bp-measurement-competency-interval | adults | every 6-12 months | "competency checks ideally every 6 to 12 months" | aha-2025 | p14 | p14/narrative/5 | narrative |
| routine-laboratory-repeat-interval | adults-htn | at least annually | "Basic laboratory testing should be repeated in patients with hypertension at least annually" | aha-2025 | p15 | p15/narrative/1 | narrative |
| abpm-monitoring-duration | adults | 24 hours | "usually over a period of 24 hours" | aha-2025 | p16 | p16/narrative/1 | narrative |
| abpm-daytime-interval | adults | 15-30 minutes | "daytime (ie, 15-30 minutes)" | aha-2025 | p16 | p16/narrative/2 | narrative |
| abpm-nighttime-interval | adults | 30-60 minutes | "nighttime (ie, 30-60 minutes)" | aha-2025 | p16 | p16/narrative/3 | narrative |
| hbpm-daily-reading-count | adults-home-bp | 2 readings 1 minute apart twice daily | "RENDERED: You should take 2 readings 1 min apart twice a day (for a total of 4 readings)" | aha-2025 | p17 | p17/narrative/1 | narrative |
| hbpm-monitoring-duration | adults-home-bp | 3-7 days | "RENDERED: Check blood pressure for 3 days (minimum) to 7 days (preferred)" | aha-2025 | p17 | p17/narrative/2 | narrative |
| hbpm-threshold-office-120 | adults | 120/80 mm Hg | "120/80 120/80 120/80 100/65 115/75" | aha-2025 | p17 | p17/narrative/3 | narrative |
| daytime-abpm-threshold-office-120 | adults | 120/80 mm Hg | "120/80 120/80 120/80 100/65 115/75" | aha-2025 | p17 | p17/narrative/4 | narrative |
| nighttime-abpm-threshold-office-120 | adults | 100/65 mm Hg | "120/80 120/80 120/80 100/65 115/75" | aha-2025 | p17 | p17/narrative/5 | narrative |
| full-day-abpm-threshold-office-120 | adults | 115/75 mm Hg | "120/80 120/80 120/80 100/65 115/75" | aha-2025 | p17 | p17/narrative/6 | narrative |
| hbpm-threshold-office-130 | adults | 130/80 mm Hg | "130/80 130/80 130/80 110/65 125/75" | aha-2025 | p17 | p17/narrative/7 | narrative |
| daytime-abpm-threshold-office-130 | adults | 130/80 mm Hg | "130/80 130/80 130/80 110/65 125/75" | aha-2025 | p17 | p17/narrative/8 | narrative |
| nighttime-abpm-threshold-office-130 | adults | 110/65 mm Hg | "130/80 130/80 130/80 110/65 125/75" | aha-2025 | p17 | p17/narrative/9 | narrative |
| full-day-abpm-threshold-office-130 | adults | 125/75 mm Hg | "130/80 130/80 130/80 110/65 125/75" | aha-2025 | p17 | p17/narrative/10 | narrative |
| hbpm-threshold-office-140 | adults | 135/85 mm Hg | "140/90 135/85 135/85 120/70 130/80" | aha-2025 | p17 | p17/narrative/11 | narrative |
| daytime-abpm-threshold-office-140 | adults | 135/85 mm Hg | "140/90 135/85 135/85 120/70 130/80" | aha-2025 | p17 | p17/narrative/12 | narrative |
| nighttime-abpm-threshold-office-140 | adults | 120/70 mm Hg | "140/90 135/85 135/85 120/70 130/80" | aha-2025 | p17 | p17/narrative/13 | narrative |
| full-day-abpm-threshold-office-140 | adults | 130/80 mm Hg | "140/90 135/85 135/85 120/70 130/80" | aha-2025 | p17 | p17/narrative/14 | narrative |
| hbpm-threshold-office-160 | adults | 145/90 mm Hg | "160/100 145/90 145/90 140/85 145/90" | aha-2025 | p17 | p17/narrative/15 | narrative |
| daytime-abpm-threshold-office-160 | adults | 145/90 mm Hg | "160/100 145/90 145/90 140/85 145/90" | aha-2025 | p17 | p17/narrative/16 | narrative |
| nighttime-abpm-threshold-office-160 | adults | 140/85 mm Hg | "160/100 145/90 145/90 140/85 145/90" | aha-2025 | p17 | p17/narrative/17 | narrative |
| full-day-abpm-threshold-office-160 | adults | 145/90 mm Hg | "160/100 145/90 145/90 140/85 145/90" | aha-2025 | p17 | p17/narrative/18 | narrative |
| secondary-htn-screening-age | adults-htn | <30 years | "early-onset hypertension (age <30 years)" | aha-2025 | p20 | p20/narrative/1 | narrative |
| osa-neck-size-men | adults-men | >17 inches | "neck size (eg, >17 inches [men]" | aha-2025 | p21 | p21/narrative/1 | narrative |
| osa-neck-size-women | adults-women | >16 inches | ">16 inches [women]" | aha-2025 | p21 | p21/narrative/2 | narrative |
| primary-aldo-confirmatory-mra-withdrawal | adults-aldosteronism-screening | 4-6 weeks | "withdrawal of MRA for 4-6 wks" | aha-2025 | p21 | p21/narrative/3 | narrative |
| primary-aldo-oral-loading-duration | adults-aldosteronism-screening | 24 hours | "Oral sodium loading test (with 24-h urine aldosterone)" | aha-2025 | p21 | p21/narrative/4 | narrative |
| primary-aldo-iv-infusion-duration | adults-aldosteronism-screening | 4 hours | "plasma aldosterone at 4 h of infusion" | aha-2025 | p21 | p21/narrative/5 | narrative |
| cushing-dexamethasone-dose | adults-htn | 1 mg | "RENDERED: Overnight 1-mg dexamethasone suppression test" | aha-2025 | p22 | p22/narrative/1 | narrative |
| acromegaly-gh-threshold | adults-htn | >=1 ng/mL | "RENDERED: Serum growth hormone ≥1 ng/mL during oral glucose load" | aha-2025 | p22 | p22/narrative/2 | narrative |
| alcohol-limit | adults-women | <=1 drink/d | "limit alcohol to ≤1 drink daily for women" | aha-2025 | p24 | p24/narrative/1 | narrative |
| alcohol-limit | adults-men | <=2 drinks/d | "≤2 drinks daily for men" | aha-2025 | p24 | p24/narrative/2 | narrative |
| caffeine-limit | adults | <300 mg/d | "Limit caffeine intake to <300 mg/d" | aha-2025 | p24 | p24/narrative/3 | narrative |
| acetaminophen-limit | adults | <4 g/d | "Limit acetaminophen to less than 4 g/d" | aha-2025 | p24 | p24/narrative/4 | narrative |
| contraceptive-ethinyl-estradiol-dose | adults-women | 20-30 mcg | "low-dose (eg, 20-30 mcg ethinyl estradiol) agents" | aha-2025 | p24 | p24/narrative/5 | narrative |
| primary-aldo-renin-threshold | adults-aldosteronism-screening | <1 ng/mL/h | "RENDERED: suppressed renin activity (<1 ng/mL/h)" | aha-2025 | p25 | p25/narrative/1 | narrative |
| primary-aldo-aldosterone-threshold | adults-aldosteronism-screening | >=10 ng/dL | "RENDERED: plasma aldosterone concentration should be at least 10 ng/dL" | aha-2025 | p25 | p25/narrative/2 | narrative |
| primary-aldo-ratio-threshold | adults-aldosteronism-screening | 30 | "cutoff value for the aldosterone to renin activity ratio is 30" | aha-2025 | p25 | p25/narrative/3 | narrative |
| primary-aldo-mra-withdrawal | adults-aldosteronism-screening | >=4 weeks | "MRA (eg, spironolactone or eplerenone) withdrawn for at least 4 weeks before testing" | aha-2025 | p25 | p25/narrative/4 | narrative |
| primary-aldo-repeat-testing-washout | adults-aldosteronism-screening | 2-4 weeks | "for at least 2 to 4 weeks prior to repeat testing" | aha-2025 | p26 | p26/narrative/1 | narrative |
| adrenal-mass-surgery-threshold | adults-aldosteronism-screening | >4 cm | "features suggestive of malignancy are present (size >4 cm" | aha-2025 | p26 | p26/narrative/2 | narrative |
| dietary-potassium-goal | adults | 3500-5000 mg/day | "dietary potassium 3500 to 5000 mg per day" | aha-2025 | p28 | p28/narrative/1 | narrative |
| aerobic-activity-goal | adults | >=150 min/week | "RENDERED: ≥150 minutes of moderate physical activity per week" | aha-2025 | p28 | p28/narrative/2 | narrative |
| resistance-activity-goal | adults | >=2 days/week | "resistance exercise ≥2 days per week" | aha-2025 | p28 | p28/narrative/3 | narrative |
| potassium-supplementation-upper-limit | adults | <80 mmol/d | "Moderate potassium supplementation is <80 mmol/d (<80 mEq/d)" | aha-2025 | p28 | p28/narrative/4 | narrative |
| standard-drink-alcohol-content | adults | 12-14 g alcohol | "One standard drink (12 to 14 g alcohol)" | aha-2025 | p28 | p28/narrative/5 | narrative |
| aerobic-exercise-prescription | adults | 90-150 min/wk at 65%-75% heart rate reserve | "Aerobic exercise 90-150 min/wk 65%-75% heart rate reserve" | aha-2025 | p29 | p29/narrative/1 | narrative |
| dynamic-resistance-prescription | adults | 90-150 min/wk at 50%-80% 1 rep maximum | "Dynamic resistance 90-150 min/wk 50%-80% 1 rep maximum" | aha-2025 | p29 | p29/narrative/2 | narrative |
| isometric-resistance-prescription | adults | 4 x 2 min; 1 min rest; 30%-40%; 3 sessions/wk | "Isometric resistance 4 × 2 min (hand grip), 1 min rest between exercises, 30%-40% maximum voluntary contraction, 3 sessions/wk" | aha-2025 | p29 | p29/narrative/3 | narrative |
| meditation-prescription | adults | 2 x 20 min/day | "2 × 20 min sessions/d" | aha-2025 | p29 | p29/narrative/4 | narrative |
| breathing-control-prescription | adults | <10 breaths/min for 15 min/day | "<10 breaths/min for 15 min/d" | aha-2025 | p29 | p29/narrative/5 | narrative |
| non-asian-overweight-bmi-range | adults | 25.0-29.9 kg/m2 | "RENDERED: BMI 25.0-29.9 and ≥30 kg/m2 for non-Asian populations" | aha-2025 | p30 | p30/narrative/1 | narrative |
| asian-overweight-bmi-range | adults | 23.0-27.4 kg/m2 | "BMI 23.0-27.4 and ≥27.5 kg/m2 for individuals of Asian heritage" | aha-2025 | p30 | p30/narrative/2 | narrative |
| potassium-supplementation-optimal-dose | adults | approximately 30 mmol/day | "maximal lowering of BP at approximately 30 mmol/day supplementation" | aha-2025 | p31 | p31/narrative/1 | narrative |
| potassium-supplementation-high-dose | adults | >80 mmol/day | "increase in BP above 80 mmol/day supplementation" | aha-2025 | p31 | p31/narrative/2 | narrative |
| alcohol-reduction-goal | adults | >=50% or abstinence | "reduction of alcohol intake by at least 50% or to abstinence" | aha-2025 | p31 | p31/narrative/3 | narrative |
| combination-therapy-distance-from-goal | adults-htn | SBP >=20 and DBP >=10 relative to target | "SBP ≥20 mm Hg and DBP ≥10 mm Hg from target" | aha-2025 | p39 | p39/narrative/1 | narrative |
| metabolic-panel-monitoring-interval | adults-htn-medication | 2-4 weeks | "RENDERED: basic metabolic panel should be checked 2 to 4 weeks after initiation or dose titration" | aha-2025 | p44 | p44/narrative/1 | narrative |
| egfr-monitoring-interval | adults-htn-medication | 2-4 weeks | "Estimated GFR using serum creatinine should be measured 2 to 4 weeks after initiation or dose titration" | aha-2025 | p45 | p45/narrative/1 | narrative |
| egfr-expected-dip | adults-htn-medication | up to 30% | "expected reduction, or dip, in eGFR of up to 30%" | aha-2025 | p45 | p45/narrative/2 | narrative |
| egfr-hold-threshold | adults-htn-medication | >30% | "RENDERED: unless the decline in eGFR is persistently >30%" | aha-2025 | p45 | p45/narrative/3 | narrative |
| patiromer-separation-interval | adults-htn-medication | >=3 hours before or after | "administer the antihypertensives at least 3 h before or after taking the potassium binder" | aha-2025 | p45 | p45/narrative/4 | narrative |
| sodium-zirconium-separation-interval | adults-htn-medication | 2 hours | "effect diminished with separation of administration by 2 h" | aha-2025 | p45 | p45/narrative/5 | narrative |
| ccd-dbp-goal-range | adults-htn-cvd | 70-80 mm Hg | "a DBP between 70 and 80 mm Hg is associated with reduced cardiovascular events" | aha-2025 | p48 | p48/narrative/1 | narrative |
| hfref-ejection-fraction-cutoff | adults-hfrEF | <=40% | "RENDERED: HFrEF, defined as left ventricular ejection fraction ≤40%" | aha-2025 | p49 | p49/narrative/1 | narrative |
| bp-treatment-goal-sbp | adults-hfrEF | <130 mm Hg | "a goal SBP <130 mm Hg should at least be attained" | aha-2025 | p49 | p49/narrative/2 | narrative |
| bp-treatment-goal-sbp | adults-hfpef | <130 mm Hg | "RENDERED: attain an SBP of <130 mm Hg" | aha-2025 | p49 | p49/narrative/3 | narrative |
| mra-hfref-egfr-threshold | adults-hfrEF | >30 mL/min/1.73 m2 | "eGFR is >30 mL/min/1.73 m2" | aha-2025 | p50 | p50/narrative/301 | narrative |
| mra-hfref-potassium-threshold | adults-hfrEF | <5.0 mEq/L | "potassium is <5.0 mEq/L" | aha-2025 | p50 | p50/narrative/302 | narrative |
| bp-treatment-goal-sbp | adults-pad | <130 mm Hg | "Treatment of hypertension to a goal BP of <130/80 mm Hg in adults with PAD" | aha-2025 | p55 | p55/narrative/1 | narrative |
| bp-treatment-goal-dbp | adults-pad | <80 mm Hg | "Treatment of hypertension to a goal BP of <130/80 mm Hg in adults with PAD" | aha-2025 | p55 | p55/narrative/2 | narrative |
| home-bp-treatment-goal | adults-home-bp | <135/85 mm Hg | "lower home BP targets (<135/85 mm Hg)" | aha-2025 | p58 | p58/narrative/1 | narrative |
| normal-bp-reassessment-interval | adults | 1 year | "RENDERED: Reassess in 1 y" | aha-2025 | p59 | p59/narrative/1 | narrative |
| elevated-bp-reassessment-interval | adults | 3-6 months | "RENDERED: Reassess in 3-6 mo" | aha-2025 | p59 | p59/narrative/2 | narrative |
| medication-bp-reassessment-interval | adults-htn-medication | 1 month | "RENDERED: Reassess in 1 mo" | aha-2025 | p59 | p59/narrative/3 | narrative |
| controlled-bp-reassessment-interval | adults-htn | 3-6 months | "RENDERED: Reassess in 3-6 mo" | aha-2025 | p59 | p59/narrative/4 | narrative |
| preeclampsia-aspirin-start-week | adults-pregnancy | 12 weeks gestation | "daily low-dose aspirin taken during pregnancy after 12 weeks’ gestation" | aha-2025 | p60 | p60/narrative/1 | narrative |
| postpartum-bp-check-interval | adults-pregnancy-postpartum | 3-10 days after discharge | "RENDERED: BP check for individuals with an HDP within 3 to 10 days of discharge" | aha-2025 | p62 | p62/narrative/1 | narrative |
| postpartum-bp-monitoring-interval | adults-pregnancy-postpartum | at least annually | "BP measured at least annually" | aha-2025 | p62 | p62/narrative/2 | narrative |
| preeclampsia-aspirin-start-week | adults-pregnancy | 12 weeks gestation | "RENDERED: starting at 12 weeks of gestation during subsequent pregnancies" | aha-2025 | p62 | p62/narrative/3 | narrative |
| resistant-htn-medication-count | adults-resistant-htn | 3 medications | "BP above goal despite treatment with 3 antihypertensive medications" | aha-2025 | p63 | p63/narrative/1 | narrative |
| controlled-resistant-htn-medication-count | adults-resistant-htn | >=4 medications | "BP at goal but requiring ≥4 medications" | aha-2025 | p63 | p63/narrative/2 | narrative |
| rdn-artery-diameter-range | adults-rdn | 3-8 mm | "artery diameters between 3 and 8 mm" | aha-2025 | p64 | p64/narrative/1 | narrative |
| rdn-referral-duration | adults-resistant-htn | >6 months | "RENDERED: If BP remains uncontrolled >6 months of treatment" | aha-2025 | p65 | p65/narrative/1 | narrative |
| rdn-surveillance-high-risk-period | adults-rdn | first 6 months | "highest risk within the first 6 months" | aha-2025 | p66 | p66/narrative/1 | narrative |
| aortic-dissection-target-time | adults-aortic-dissection | <=120 mm Hg within 20 minutes | "SBP ≤120 mm Hg should be achieved within 20 min" | aha-2025 | p70 | p70/narrative/1 | narrative |
| perioperative-hypertension-duration | adults-preop | BP >=160/90 or SBP >=20% for >15 min | "RENDERED: Perioperative hypertension (BP ≥160/90 mm Hg or SBP elevation ≥20% of the preoperative value that persists for >15 min)" | aha-2025 | p70 | p70/narrative/2 | narrative |
| perioperative-raasi-hold-interval | adults-preop | 24 hours | "stopped their ACEi or ARB 24 hours before noncardiac surgery" | aha-2025 | p71 | p71/narrative/1 | narrative |
| severe-htn-follow-up-interval | adults-hospitalized-severe-htn | 4 weeks | "RENDERED: Close follow-up in the outpatient setting in 4 weeks" | aha-2025 | p72 | p72/narrative/1 | narrative |
| white-coat-exclusion-bp-threshold | adults | >=130/80 mm Hg | "untreated office SBP ≥130 mm Hg or DBP ≥80 mm Hg" | aha-2025 | p18 | p18/white-coat-hypertension-and-masked/1 | 2a |
| white-coat-exclusion-bp-upper-limit | adults | <160/100 mm Hg | "without office SBP ≥160 mm Hg or DBP ≥100 mm Hg" | aha-2025 | p18 | p18/white-coat-hypertension-and-masked/1 | 2a |
| white-coat-exclusion-bp-threshold | adults-htn | >=130/80 mm Hg | "elevated office BP (office SBP ≥130 mm Hg or DBP ≥80 mm Hg)" | aha-2025 | p18 | p18/white-coat-hypertension-and-masked/4 | 2a |
| white-coat-exclusion-bp-upper-limit | adults-htn | <160/100 mm Hg | "office SBP ≥160 mm Hg or DBP ≥100 mm Hg" | aha-2025 | p18 | p18/white-coat-hypertension-and-masked/4 | 2a |
| masked-htn-exclusion-bp-threshold | adults | <130/80 mm Hg | "untreated office SBP <130 mm Hg and DBP <80 mm Hg" | aha-2025 | p18 | p18/white-coat-hypertension-and-masked/5 | 2b |
| masked-htn-exclusion-bp-threshold | adults-htn | <130/80 mm Hg | "office SBP <130 mm Hg and DBP <80 mm Hg" | aha-2025 | p18 | p18/white-coat-hypertension-and-masked/6 | 2b |
| primary-aldo-screening-stroke-age-cutoff | adults-htn | <40 years | "or stroke at a young age (<40 years)" | aha-2025 | p22 | p22/primary-aldosteronism/1 | 1 |
| bp-treatment-threshold-sbp | adults-htn | >=140 mm Hg | "initiation of medications to lower BP is recommended when average SBP is ≥140 mm Hg" | aha-2025 | p32 | p32/bp-treatment-threshold-and-the-use-of-cvd/1 | 1 |
| bp-treatment-threshold-dbp | adults-htn | >=90 mm Hg | "initiation of medications to lower BP is recommended when average DBP is ≥90 mm Hg" | aha-2025 | p32 | p32/bp-treatment-threshold-and-the-use-of-cvd/2 | 1 |
| bp-treatment-threshold-sbp | adults-htn-cvd | >=130 mm Hg | "recommended when average SBP is ≥130 mm Hg" | aha-2025 | p32 | p32/bp-treatment-threshold-and-the-use-of-cvd/3 | 1 |
| bp-treatment-threshold-dbp | adults-htn-cvd | >=80 mm Hg | "recommended when average DBP is ≥80 mm Hg" | aha-2025 | p32 | p32/bp-treatment-threshold-and-the-use-of-cvd/4 | 1 |
| bp-treatment-threshold-sbp | adults-htn-highrisk | >=130 mm Hg | "initiation of medications to lower BP is recommended when average SBP is ≥130 mm Hg" | aha-2025 | p33 | p33/bp-treatment-threshold-and-the-use-of-cvd/5 | 1 |
| bp-treatment-threshold-dbp | adults-htn-highrisk | >=80 mm Hg | "recommended when average DBP is ≥80 mm Hg" | aha-2025 | p33 | p33/bp-treatment-threshold-and-the-use-of-cvd/6 | 1 |
| bp-treatment-threshold-sbp | adults-htn-lowrisk | >=130 mm Hg | "recommended if average SBP remains ≥130 mm Hg" | aha-2025 | p33 | p33/bp-treatment-threshold-and-the-use-of-cvd/7 | 1 |
| lifestyle-trial-duration | adults-htn-lowrisk | 3-6 months | "after a 3- to 6-month trial of lifestyle intervention" | aha-2025 | p33 | p33/bp-treatment-threshold-and-the-use-of-cvd/7 | 1 |
| bp-treatment-threshold-dbp | adults-htn-lowrisk | >=80 mm Hg | "recommended if average DBP ≥80 mm Hg" | aha-2025 | p33 | p33/bp-treatment-threshold-and-the-use-of-cvd/8 | 1 |
| lifestyle-trial-duration | adults-htn-lowrisk | 3-6 months | "after a 3- to 6-month trial of lifestyle intervention" | aha-2025 | p33 | p33/bp-treatment-threshold-and-the-use-of-cvd/8 | 1 |
| bp-stage-2-threshold-sbp | adults-htn | >=140 mm Hg | "In adults with stage 2 hypertension (SBP ≥ 140 mm Hg" | aha-2025 | p36 | p36/choice-of-initial-monotherapy-versus-initial/1 | 1 |
| bp-stage-2-threshold-dbp | adults-htn | >=90 mm Hg | "and DBP ≥90 mm Hg), initiation of antihypertensive drug therapy" | aha-2025 | p36 | p36/choice-of-initial-monotherapy-versus-initial/1 | 1 |
| bp-stage-1-range-sbp | adults-htn | 130-139 mm Hg | "In adults with stage 1 hypertension (SBP 130- 139 mm Hg" | aha-2025 | p36 | p36/choice-of-initial-monotherapy-versus-initial/2 | 2a |
| bp-stage-1-range-dbp | adults-htn | 80-89 mm Hg | "and DBP 80-89 mm Hg), initiation of antihypertensive drug therapy" | aha-2025 | p36 | p36/choice-of-initial-monotherapy-versus-initial/2 | 2a |
| dietary-sodium-limit | adults | <2300 mg/d | "reduction of dietary sodium intake* is recommended to <2300 mg/d" | aha-2025 | p28 | p28/lifestyle-and-psychosocial-approaches/3 | 1 |
| dietary-sodium-ideal-limit | adults | <1500 mg/d | "moving toward an ideal limit of <1500 mg/d" | aha-2025 | p28 | p28/lifestyle-and-psychosocial-approaches/3 | 1 |
| alcohol-limit | adults-women | <=1 drink/d | "reduce alcohol intake to ≤1 drink/d for women" | aha-2025 | p28 | p28/lifestyle-and-psychosocial-approaches/6 | 1 |
| alcohol-limit | adults-men | <=2 drinks/d | "≤2 drinks/d for men to prevent or treat elevated BP" | aha-2025 | p28 | p28/lifestyle-and-psychosocial-approaches/6 | 1 |
| weight-loss-goal | adults-overweight | >=5% of body weight | "weight loss is recommended with a goal of at least 5% of body weight reduction" | aha-2025 | p28 | p28/lifestyle-and-psychosocial-approaches/1 | 1 |
| antihypertensive-dosing-frequency | adults-htn | once daily | "dosing once daily rather than multiple times daily" | aha-2025 | p40 | p40/antihypertensive-medication-adherence/1 | 1 |
| bp-treatment-goal-sbp | adults-htn-cvd | <130 mm Hg | "an SBP goal of at least <130 mm Hg" | aha-2025 | p41 | p41/bp-goal-for-patients-with-hypertension/1 | 1 |
| bp-treatment-goal-sbp | adults-htn | <130 mm Hg | "an SBP goal of <130 mm Hg" | aha-2025 | p41 | p41/bp-goal-for-patients-with-hypertension/2 | 2b |
| bp-treatment-goal-dbp | adults-htn-cvd | <80 mm Hg | "a DBP target of <80 mm Hg is recommended" | aha-2025 | p41 | p41/bp-goal-for-patients-with-hypertension/3 | 1 |
| bp-treatment-goal-dbp | adults-htn | <80 mm Hg | "a DBP target of <80 mm Hg may be reasonable" | aha-2025 | p41 | p41/bp-goal-for-patients-with-hypertension/4 | 2b |
| bp-treatment-threshold-sbp | adults-dm | >=130 mm Hg | "should be initiated at an SBP of ≥130 mm Hg" | aha-2025 | p46 | p46/diabetes/1 | 1 |
| bp-treatment-goal-sbp | adults-dm | <130 mm Hg | "with a treatment goal of <130 mm Hg" | aha-2025 | p46 | p46/diabetes/1 | 1 |
| bp-treatment-threshold-dbp | adults-dm | >=80 mm Hg | "initiated at a DBP of ≥80 mm Hg" | aha-2025 | p46 | p46/diabetes/2 | 1 |
| bp-treatment-goal-dbp | adults-dm | <80 mm Hg | "with a treatment goal of <80 mm Hg to reduce CVD morbidity" | aha-2025 | p46 | p46/diabetes/2 | 1 |
| raasi-indication-egfr-threshold | adults-dm | <60 mL/min/1.73 m2 | "as identified by eGFR <60 mL/min/1.73 m2" | aha-2025 | p46 | p46/diabetes/4 | 1 |
| incretin-mimetic-bmi-threshold | adults-htn | >=27 kg/m2 | "obesity with a BMI ≥27 kg/m2" | aha-2025 | p47 | p47/obesity-and-metabolic-syndrome/1 | 2b |
| bariatric-surgery-bmi-threshold | adults-htn | >=35.0 kg/m2 | "obesity with a BMI ≥35.0 kg/m2, bariatric surgery" | aha-2025 | p47 | p47/obesity-and-metabolic-syndrome/2 | 2b |
| bp-treatment-goal-sbp | adults-htn | <130 mm Hg | "treating SBP to <130 mm Hg is recommended" | aha-2025 | p48 | p48/the-prevention-of-hf-in-adults-with/1 | 1 |
| bp-treatment-goal-dbp | adults-htn | <80 mm Hg | "treating DBP to <80 mm Hg is recommended" | aha-2025 | p48 | p48/the-prevention-of-hf-in-adults-with/2 | 1 |
| bp-treatment-goal-sbp | adults-ckd | <130 mm Hg | "treatment should target an SBP goal of <130 mm Hg" | aha-2025 | p50 | p50/hypertension-treatment-in-patients-with-ckd/1 | 1 |
| raasi-indication-egfr-threshold | adults-ckd | <60 mL/min/1.73 m2 | "as identified by eGFR <60 mL/min/1.73 m2 with albuminuria of ≥30 mg/g" | aha-2025 | p50 | p50/hypertension-treatment-in-patients-with-ckd/2 | 1 |
| acute-ich-sbp-target | adults-ich | 130 to <140 mm Hg | "immediately lower SBP to 130 to <140 mm Hg" | aha-2025 | p52 | p52/acute-intracerebral-hemorrhage/1 | 2a |
| acute-ich-bp-control-duration | adults-ich | >=7 days | "lower SBP to 130 to <140 mm Hg for at least 7 days" | aha-2025 | p52 | p52/acute-intracerebral-hemorrhage/1 | 2a |
| acute-ich-sbp-lowering-floor | adults-ich | >=130 mm Hg | "SBP should not be lowered below 130 mm Hg" | aha-2025 | p52 | p52/acute-intracerebral-hemorrhage/3 | 3 |
| thrombolysis-eligibility-bp-threshold | adults-htn-cvd | <185/110 mm Hg | "their BP lowered to SBP <185 mm Hg and DBP <110 mm Hg before IV" | aha-2025 | p52 | p52/acute-ischemic-stroke/2 | 1 |
| post-thrombolysis-bp-ceiling | adults-htn-cvd | <180/105 mm Hg | "maintained below 180/105 mm Hg for at least the first 24 hours" | aha-2025 | p52 | p52/acute-ischemic-stroke/2 | 1 |
| post-thrombolysis-bp-ceiling | adults-htn-cvd | <=180/105 mm Hg | "reasonable to maintain the BP at ≤180/105 mm Hg during and for 24 hours" | aha-2025 | p52 | p52/acute-ischemic-stroke/3 | 2a |
| acute-stroke-bp-treatment-threshold | adults-htn-cvd | >=220/120 mm Hg | "In patients with BP of ≥220/120 mm Hg who did not receive IV" | aha-2025 | p52 | p52/acute-ischemic-stroke/4 | 2b |
| acute-stroke-bp-reduction-target | adults-htn-cvd | 15% in 24 h | "it might be reasonable to lower BP by 15% during the first 24 hours" | aha-2025 | p52 | p52/acute-ischemic-stroke/4 | 2b |
| acute-stroke-bp-treatment-threshold | adults-htn-cvd | <220/120 mm Hg | "In patients with BP <220/120 mm Hg who do not receive IV thrombolysis" | aha-2025 | p53 | p53/acute-ischemic-stroke-continued/5 | 3 |
| post-reperfusion-sbp-floor | adults-htn-cvd | <140 mm Hg | "lowering SBP <140 mm Hg within the first 24 to 72 hours after reperfusion" | aha-2025 | p53 | p53/acute-ischemic-stroke-continued/6 | 3 |
| bp-treatment-goal-sbp | adults-htn-cvd | <130 mm Hg | "goal of <130/80 mm Hg is recommended to reduce the risk of recurrent stroke" | aha-2025 | p54 | p54/secondary-stroke-prevention/2 | 1 |
| bp-treatment-goal-dbp | adults-htn-cvd | <80 mm Hg | "goal of <130/80 mm Hg is recommended to reduce the risk of recurrent stroke" | aha-2025 | p54 | p54/secondary-stroke-prevention/2 | 1 |
| bp-treatment-threshold-sbp | adults-htn-cvd | >=130 mm Hg | "have an average office SBP/DBP of ≥130/80 mm Hg, antihypertensive medication treatment can be beneficial" | aha-2025 | p54 | p54/secondary-stroke-prevention/3 | 2a |
| bp-treatment-threshold-dbp | adults-htn-cvd | >=80 mm Hg | "have an average office SBP/DBP of ≥130/80 mm Hg, antihypertensive medication treatment can be beneficial" | aha-2025 | p54 | p54/secondary-stroke-prevention/3 | 2a |
| follow-up-interval | adults-htn | monthly | "follow-up evaluations for medication adherence and response to treatment at monthly intervals" | aha-2025 | p56 | p56/plan-of-care-for-hypertension/4 | 1 |
| aspirin-preeclampsia-prophylaxis-dose | adults-pregnancy | 81 mg/day | "counseled about the benefits of low-dose (81 mg/day) aspirin to reduce the risk" | aha-2025 | p58 | p58/individuals-with-hypertension-and-pregnancy/2 | 1 |
| pregnancy-severe-bp-treatment-threshold | adults-pregnancy | >=160/110 mm Hg | "Pregnant individuals with SBP ≥160 mm Hg or DBP ≥110 mm Hg confirmed on repeat" | aha-2025 | p58 | p58/individuals-with-hypertension-and-pregnancy/3 | 1 |
| pregnancy-acute-bp-target | adults-pregnancy | <160/110 mm Hg within 30-60 min | "lower BP to <160/<110 mm Hg within 30 to 60 minutes" | aha-2025 | p58 | p58/individuals-with-hypertension-and-pregnancy/3 | 1 |
| chronic-htn-pregnancy-staging-cutoff | adults-pregnancy | 140-159/90-109 mm Hg | "SBP 140 to 159 mm Hg and/or DBP 90 to 109 mm Hg prior to" | aha-2025 | p58 | p58/individuals-with-hypertension-and-pregnancy/4 | 1 |
| pregnancy-bp-treatment-goal | adults-pregnancy | <140/90 mm Hg | "should receive antihypertensive therapy to achieve BP <140/90 mm Hg to prevent maternal" | aha-2025 | p58 | p58/individuals-with-hypertension-and-pregnancy/4 | 1 |
| egfr-threshold-mra | adults-resistant-htn | >=45 mL/min/1.73 m2 | "with an eGFR of ≥45 mL/min/1.73 m2), addition of a MRA is recommended" | aha-2025 | p63 | p63/resistant-hypertension-and-renal-denervation/2 | 1 |
| rdn-eligibility-bp | adults-resistant-htn | SBP 140-180 mm Hg and DBP >=90 mm Hg | "office SBP 140-180 mm Hg and DBP ≥90 mm Hg" | aha-2025 | p63 | p63/resistant-hypertension-and-renal-denervation/4 | 2b |
| egfr-threshold-rdn | adults-resistant-htn | >=40 mL/min/1.73 m2 | "eGFR ≥40 mL/ min/1.73 m2 who have resistant hypertension despite optimal treatment" | aha-2025 | p63 | p63/resistant-hypertension-and-renal-denervation/4 | 2b |
| bp-treatment-goal-sbp | adults-htn | <130 mm Hg | "treatment with a goal of SBP <130 mm Hg is reasonable" | aha-2025 | p66 | p66/management-of-oh/2 | 2a |
| hypertensive-emergency-bp-threshold | adults-htn-emergency | >180 and/or >120 mm Hg | "(BP >180 and/or >120 mm Hg and evidence of acute target organ damage)" | aha-2025 | p67 | p67/hypertensive-emergencies-and-severe/1 | 1 |
| hypertensive-emergency-sbp-target | adults-htn-emergency-compelling | <140 mm Hg | "SBP should be reduced to <140 mm Hg for most conditions" | aha-2025 | p67 | p67/hypertensive-emergencies-and-severe/2 | 1 |
| hypertensive-emergency-sbp-target | adults-htn-emergency-dissection | <120 mm Hg in first hour | "to <120 mm Hg in aortic dissection during the first hour" | aha-2025 | p67 | p67/hypertensive-emergencies-and-severe/2 | 1 |
| hypertensive-emergency-bp-reduction-first-hour | adults-htn-emergency-nocompelling | <=25% within first hour | "reduced with oral or parenteral therapy by no more than 25% within the first hour" | aha-2025 | p67 | p67/hypertensive-emergencies-and-severe/3 | 1 |
| hypertensive-emergency-bp-target-2-6h | adults-htn-emergency-nocompelling | <160/100 mm Hg within 2 to 6 hours | "then, if stable, to <160/100 mm Hg within the next 2 to 6 hours" | aha-2025 | p67 | p67/hypertensive-emergencies-and-severe/3 | 1 |
| hypertensive-emergency-bp-target-24-48h | adults-htn-emergency-nocompelling | 130 to 140 mm Hg during 24 to 48 hours | "to 130 to 140 mm Hg during the next 24 to 48 hours" | aha-2025 | p67 | p67/hypertensive-emergencies-and-severe/3 | 1 |
| severe-hypertension-threshold | adults-hospitalized-severe-htn | >180/120 mm Hg | "severe hypertension (>180/120 mm Hg) who are hospitalized for noncardiac conditions" | aha-2025 | p67 | p67/hypertensive-emergencies-and-severe/4 | 3 |
| surgery-deferral-bp-threshold | adults-preop | SBP >=180 or DBP >=110 mm Hg | "elective major surgery with SBP ≥180 mm Hg or DBP ≥110 mm Hg" | aha-2025 | p70 | p70/patients-scheduled-for-surgical-procedures/4 | 2b |

## Conflicts

**CONFLICT: post-thrombolysis-bp-ceiling** — The guideline states this ceiling twice for the same patients at two strengths. p52 rec 3 recommends BP maintained below 180/105 mm Hg for at least the first 24 hours after IV thrombolysis (Class 1); p52 rec 4 says maintaining at <=180/105 mm Hg during and for 24 hours after mechanical thrombectomy is reasonable (Class 2a). The numbers agree; the strictness and the procedure differ. Read the class column, not the value alone.

**CONFLICT: acute-stroke-bp-treatment-threshold** — Two rows, opposite directions, and they are complementary rather than contradictory. p52 rec 4 says that at BP >=220/120 mm Hg without thrombolysis it MAY be reasonable to lower BP by 15% in the first 24 hours (Class 2b); p53 rec 5 says that below 220/120 mm Hg without thrombolysis, lowering BP in the first 48 to 72 hours is NOT recommended (Class 3). One number, two sides of it, two different actions. A sheet listing only one of them would read as an instruction to treat.


## Coverage

Every recommendation in the source that is not cited by a row above, with why. The
source is an `exact` mode document, so a recommendation appearing in neither place
is a refusal rather than a warning.

- `p13/accurate-measurement-of-in-office-bp/1` - recommends standardized measurement technique, no number
- `p13/accurate-measurement-of-in-office-bp/2` - prefers oscillometric over auscultatory method, no number
- `p16/abpm-and-hbpm/1` - recommends out-of-office confirmation modality, no number
- `p16/abpm-and-hbpm/2` - recommends HBPM for titration monitoring, no number
- `p18/white-coat-hypertension-and-masked/2` - recommends ongoing monitoring for transition, no number
- `p18/white-coat-hypertension-and-masked/3` - exclude white-coat effect in resistant hypertension, no number
- `p20/secondary-forms-of-hypertension/1` - screen on clinical suspicion, no numeric trigger
- `p20/secondary-forms-of-hypertension/2` - screen resistant hypertension for aldosteronism, no number
- `p20/secondary-forms-of-hypertension/3` - referral to expert clinician, no number
- `p22/primary-aldosteronism/2` - names stage 2 category, no numeric cutoff in the text
- `p23/primary-aldosteronism-continued/3` - names screening assays, no threshold value
- `p23/primary-aldosteronism-continued/4` - continue medications before screening, no number
- `p23/primary-aldosteronism-continued/5` - referral to specialist, no number
- `p26/renal-artery-stenosis/1` - recommends medical therapy, no number
- `p26/renal-artery-stenosis/2` - referral for revascularization, no numeric trigger
- `p26/renal-artery-stenosis/3` - referral for angioplasty, no number
- `p27/osa/1` - weight loss plus CPAP, no number stated
- `p27/osa/2` - CPAP recommended, no number stated
- `p28/lifestyle-and-psychosocial-approaches/2` - DASH eating pattern, no number stated
- `p28/lifestyle-and-psychosocial-approaches/4` - salt substitute use, amount only in footnote
- `p28/lifestyle-and-psychosocial-approaches/5` - moderate potassium supplementation, amount only in footnote
- `p28/lifestyle-and-psychosocial-approaches/7` - increase physical activity, no dose or duration stated
- `p28/lifestyle-and-psychosocial-approaches/8` - transcendental meditation, no number stated
- `p28/lifestyle-and-psychosocial-approaches/9` - breathing techniques or yoga, no number stated
- `p36/choice-of-initial-monotherapy-versus-initial/3` - harm warning against ACEi/ARB/renin-inhibitor combination, no number
- `p40/antihypertensive-medication-adherence/2` - single-pill combination recommended, no number stated
- `p40/antihypertensive-medication-adherence/3` - reminder aids and education, no number stated
- `p46/diabetes/3` - all first-line drug classes effective, no number stated
- `p52/acute-intracerebral-hemorrhage/2` - smooth nonlabile titration principle, no number stated
- `p52/acute-ischemic-stroke/1` - corrective principle, no numeric threshold stated
- `p54/secondary-stroke-prevention/1` - names drug classes, no numeric value
- `p56/plan-of-care-for-hypertension/1` - team-based care approach, no number
- `p56/plan-of-care-for-hypertension/2` - care-plan principle, no number
- `p56/plan-of-care-for-hypertension/3` - integrated treatment model, no number
- `p56/plan-of-care-for-hypertension/5` - health information technology use, no number
- `p56/plan-of-care-for-hypertension/6` - EHR and registry screening, no number
- `p56/plan-of-care-for-hypertension/7` - telehealth intervention, no number
- `p58/individuals-with-hypertension-and-pregnancy/1` - names preferred agents, no dose stated
- `p58/individuals-with-hypertension-and-pregnancy/5` - contraindicated agents listed, no number
- `p63/resistant-hypertension-and-renal-denervation/1` - evaluate secondary causes, review medications, no number
- `p63/resistant-hypertension-and-renal-denervation/3` - alternative drug classes named, no number
- `p63/resistant-hypertension-and-renal-denervation/5` - multidisciplinary team evaluation only, no number stated
- `p63/resistant-hypertension-and-renal-denervation/6` - shared decision-making principle, no number stated
- `p66/management-of-oh/1` - improved BP control to reduce OH risk, no number
- `p66/management-of-oh/3` - assess for symptomatic orthostatic hypotension, no number of its own
- `p70/patients-scheduled-for-surgical-procedures/1` - continue chronic beta blockers perioperatively, no number
- `p70/patients-scheduled-for-surgical-procedures/2` - continue most antihypertensives perioperatively, no number
- `p70/patients-scheduled-for-surgical-procedures/3` - consider stopping ACEi or ARB preoperatively, no number
- `p70/patients-scheduled-for-surgical-procedures/5` - harm of abrupt beta blocker or clonidine withdrawal, no number
- `p70/patients-scheduled-for-surgical-procedures/6` - do not start beta blocker on surgery day, no number
