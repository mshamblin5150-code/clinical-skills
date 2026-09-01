# Chest pain evaluation — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction. Testing must be individualized to the
patient, the assay, local expertise, and contraindications.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aha-2021 | AHA ACC | AHA ACC/gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a | guideline | 2021 | 2021 | https://doi.org/10.1161/CIR.0000000000001029 | stated | exact |

## Scope

**Read:** the complete 87-page source, including front matter, recommendations,
supportive text, pathways, tables, figures, evidence gaps, article information,
references, and relationship disclosures. Clinical tables and figures on pages 17-25,
29, 32, 38, 40, 42, and 46-50 were inspected from rendered pages. The assay
coefficient-of-variation statement on page 17 was dispositioned as an analytical assay
performance characteristic rather than a patient-action threshold.

**Not read:** nothing in the source page range. The reference list was inspected for
scope and retired by class because it contains no guideline-authored clinical decision
prose.

**Source: `aha-2021`**

| span | pages | read |
| --- | --- | --- |
| front matter, methods, take-home messages, definitions, and populations | 1-11 | read 2026-08-31; blind 2026-08-31 |
| older-patient and diverse-population considerations | 12 | yes |
| patient-centric considerations and physical examination | 13 | read 2026-08-31; blind 2026-08-31 |
| ECG and biomarker evaluation | 14-17 | yes |
| testing considerations, contraindications, acute pathways, and risk tables | 18-25 | yes |
| acute intermediate- and high-risk evaluation and known CAD | 26-33 | yes |
| aortic, pulmonary, inflammatory, valvular, and noncardiac causes | 34-39 | yes |
| stable chest pain, known CAD, prior CABG, and INOCA | 40-50 | yes |
| cost-value considerations, evidence gaps, and future research | 51-53 | read 2026-08-31; blind 2026-08-31 |
| article information | 54 | read 2026-08-31; blind 2026-08-31 |
| references | 55-77 | exempt: reference list |
| author and reviewer relationship disclosures | 78-87 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

source sha256 7cee2d8818175b5c867a5e287202d9a7aaed1a46e9ae9d1d77f07ea698ec9255

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| acute-chest-pain | patients with acute chest pain |
| acute-suspected-acs | patients with acute chest pain and suspected ACS |
| acute-low-risk | low-risk patients with acute chest pain |
| acute-intermediate-no-cad | intermediate-risk patients with acute chest pain and no known CAD |
| acute-intermediate-known-cad | intermediate-risk patients with acute chest pain and known CAD |
| acute-high-risk | high-risk patients with acute chest pain |
| older-chest-pain | patients with chest pain who are older than 75 years |
| acute-prior-cabg-no-acs | patients with prior CABG who present with acute chest pain without ACS and are candidates for revascularization |
| stable-intermediate-high | intermediate-high-risk patients with stable chest pain and no known CAD |
| stable-obstructive-cad | patients with obstructive CAD who present with stable chest pain despite GDMT |
| stable-prior-stent | patients with prior coronary stents who present with stable chest pain |
| stable-nonobstructive-cad | patients with known nonobstructive CAD and stable chest pain |
| exercise-candidate | patients undergoing exercise ECG testing |
| pharmacologic-stress-candidate | patients undergoing pharmacologic stress testing |
| suspected-myocardial-injury | patients being evaluated for myocardial injury |
| stable-chest-pain | patients with stable chest pain and no known CAD |
| stable-younger-no-prevention | patients with stable chest pain, no known CAD, age younger than 65 years, and not receiving optimal preventive therapies |
| stable-older | patients with stable chest pain and no known CAD aged 65 years or older |
| symptomatic-pretest | symptomatic patients with no known CAD undergoing pretest-probability estimation |
| suspected-inoCA | patients with persistent stable chest pain and nonobstructive CAD undergoing INOCA evaluation |
| prior-negative-test | patients with a prior negative cardiac test |
| prior-cabg-stable | patients with prior CABG and stable chest pain |
| gi-red-flags | patients with chest pain and gastrointestinal alarm features |

## Quantities

| key | verbatim |
| --- | --- |
| ecg-time | time to acquire and review an ECG |
| myocardial-injury-cutoff | cardiac troponin threshold defining myocardial injury |
| older-acs-consideration | age threshold for considering ACS with accompanying symptoms |
| troponin-repeat-time | repeat troponin sampling interval |
| single-hsctn-eligibility | symptom duration for a single high-sensitivity troponin strategy |
| acute-low-risk | estimated 30-day risk of death or major adverse cardiac events |
| stress-warranty | period during which a prior negative test is considered recent |
| exercise-capacity | exercise capacity needed for exercise ECG |
| stress-blood-pressure | severe hypertension contraindicating stress testing |
| nuclear-stress-vitals | heart rate and blood pressure contraindications to vasodilator stress |
| stress-methylxanthine-wait | methylxanthine or caffeine avoidance before vasodilator stress |
| cmr-kidney-function | kidney-function contraindication to contrast stress CMR |
| cad-stenosis-class | coronary stenosis classification |
| high-risk-cad | anatomic definition of high-risk CAD |
| cdp-heart-score | HEART pathway score category |
| cdp-edacs-score | EDACS pathway score category |
| cdp-esc-troponin | ESC high-sensitivity troponin category |
| cdp-adapt | ADAPT and modified ADAPT low-risk threshold |
| cdp-notr | No Objective Testing Rule low-risk threshold |
| cdp-grace | 2016 ESC/GRACE low-risk threshold |
| prior-stress-severity | severity and recency of a prior stress test |
| ccta-stenosis-ffrct | stenosis range prompting FFR-CT |
| acute-high-risk-lvef | LVEF feature identifying high-risk acute chest pain |
| acute-cabg-high-risk | high-risk features after CABG prompting invasive coronary angiography |
| stable-pretest-probability | pretest probability at which testing is most beneficial |
| pretest-probability-strata | age-, sex-, symptom-, and CAC-informed pretest probability strata |
| test-selection-age | age-guided preference for CCTA versus stress testing |
| ffr-ischemia | FFR-CT or invasive FFR threshold for lesion-specific ischemia |
| stable-high-risk-anatomy | anatomy prompting invasive coronary angiography |
| stent-diameter | stent diameter suitable for CCTA patency assessment |
| cabg-stress-high-risk | stress-test features prompting invasive coronary angiography after CABG |
| gi-evaluation-time | timing of evaluation for gastrointestinal alarm features |
| inoca-entry-ffr | FFR prerequisite for INOCA endotype evaluation |
| inoca-noncardiac | noncardiac endotype criteria |
| inoca-vasospasm | epicardial vasospasm criteria |
| inoca-cmd | coronary microvascular dysfunction criteria |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ecg-time | acute-chest-pain | within 10 min of arrival | RENDERED: acquisition and review for ST-segment-elevation myocardial infarction (STEMI) within 10 minutes of arrival | aha-2021 | p14 | p14/setting-considerations/3 | 1 |
| myocardial-injury-cutoff | suspected-myocardial-injury | cTn >99th percentile upper reference limit indicates myocardial injury | RENDERED: the assay-specific 99th percentile upper reference limit | aha-2021 | p16 | p16/biomarkers/3 | 1 |
| older-acs-consideration | older-chest-pain | age >75 y: consider ACS with shortness of breath, syncope, acute delirium, or unexplained fall | RENDERED: In patients with chest pain who are >75 years of age, ACS should be considered when accompanying symptoms such as shortness of breath, syncope, or acute delirium are present, or when an unexplained fall has occurred | aha-2021 | p12 | p12/narrative/older-patients-acs | narrative |
| cad-stenosis-class | acute-chest-pain | obstructive CAD >=50%; nonobstructive CAD <50% | RENDERED: obstructive CAD (≥50% stenosis) and nonobstructive CAD (<50% stenosis) | aha-2021 | p18 | p18/narrative/cad-definitions | narrative |
| high-risk-cad | acute-chest-pain | left main >=50% or 3-vessel obstructive disease >=70% | RENDERED: left main stenosis ≥50% or anatomically significant 3-vessel disease (≥70% stenosis) | aha-2021 | p18 | p18/narrative/high-risk-cad | narrative |
| test-selection-age | stable-younger-no-prevention | age <65 y and not on optimal preventive therapy: CCTA is preferable | RENDERED: CCTA preferable in those <65 years of age and not on optimal preventive therapies | aha-2021 | p19 | p19/narrative/figure-6-ccta-age | narrative |
| test-selection-age | stable-older | age >=65 y: stress testing is favored | RENDERED: stress testing favored in those ≥65 years of age | aha-2021 | p42 | p42/narrative/figure-12-stress-age | narrative |
| exercise-capacity | exercise-candidate | must be able to achieve >=5 METs | Unable to achieve ≥5 METs or unsafe to exercise | aha-2021 | p21 | p21/narrative/table-5-exercise-capacity | narrative |
| stress-blood-pressure | exercise-candidate | severe systemic hypertension >=200/110 mm Hg is a contraindication | Severe systemic arterial hypertension (eg, ≥200/110 mm Hg) | aha-2021 | p21 | p21/narrative/table-5-exercise-hypertension | narrative |
| nuclear-stress-vitals | pharmacologic-stress-candidate | sinus bradycardia <45 bpm or SBP <90 mm Hg is a contraindication | RENDERED: sinus bradycardia at <45 bpm; significant hypotension (SBP <90 mm Hg) | aha-2021 | p21 | p21/narrative/table-5-vasodilator-vitals | narrative |
| stress-methylxanthine-wait | pharmacologic-stress-candidate | avoid methylxanthines or caffeine within 12 h | RENDERED: Use of methylxanthines such as aminophylline and caffeine within 12 hours | aha-2021 | p21 | p21/narrative/table-5-methylxanthines | narrative |
| cmr-kidney-function | pharmacologic-stress-candidate | GFR <30 mL/min/1.73 m² is a contraindication to gadolinium stress CMR | RENDERED: Reduced GFR (<30 mL/min/1.73 m²) | aha-2021 | p21 | p21/narrative/table-5-cmr-kidney | narrative |
| troponin-repeat-time | acute-suspected-acs | hs-cTn 1-3 h; conventional cTn 3-6 h after time zero | RENDERED: recommended time intervals after the initial sample collection (time zero) for repeat measurements are: 1 to 3 hours for hs-cTn and 3 to 6 hours for conventional cTn assays | aha-2021 | p22 | p22/patients-with-acute-chest-pain-and-suspected/2 | 1 |
| single-hsctn-eligibility | acute-suspected-acs | symptoms began >=3 h before arrival and initial hs-cTn is below assay limit of detection | RENDERED: symptoms of ACS began at least 3 hours before ED arrival, a single hs-cTn concentration that is below the limit of detection on initial measurement | aha-2021 | p22 | p22/patients-with-acute-chest-pain-and-suspected/5 | 2a |
| cdp-heart-score | acute-suspected-acs | low <=3; intermediate 4-6; high 7-10 | RENDERED: HEART score ≤3; HEART score 4-6; HEART score 7-10 | aha-2021 | p24 | p24/narrative/table-6-heart | narrative |
| cdp-edacs-score | acute-suspected-acs | low-risk EDACS <16 | EDACS score <16 | aha-2021 | p24 | p24/narrative/table-6-edacs | narrative |
| cdp-adapt | acute-suspected-acs | ADAPT TIMI 0 or mADAPT TIMI 0-1, negative serial troponins at 0 and 2 h, and no ischemic ECG changes: low risk | RENDERED: TIMI score 0 (or 0-1 for mADAPT); Neg 0, 2-h cTn or hs-cTn; No ischemic ECG changes | aha-2021 | p24 | p24/narrative/table-6-adapt | narrative |
| cdp-notr | acute-suspected-acs | age <50 y, <3 risk factors, no previous AMI or CAD, and negative cTn or hs-cTn at 0 and 2 h: low risk | RENDERED: Age <50 y; <3 risk factors; No previous AMI or CAD; Neg cTn or hs-cTn (0, 2 h) | aha-2021 | p24 | p24/narrative/table-6-notr | narrative |
| cdp-grace | acute-suspected-acs | chest-pain free and GRACE <140; if symptoms <6 h, hs-cTn <ULN at 0 and 3 h; if symptoms >6 h, arrival hs-cTn <ULN | RENDERED: Chest pain free, GRACE <140; Sx <6 h - hs-cTn <ULN (0, 3 h); Sx >6 h - hs-cTn <ULN (arrival) | aha-2021 | p24 | p24/narrative/table-6-grace | narrative |
| cdp-esc-troponin | acute-suspected-acs | T0 hs-cTn 12-52 ng/L intermediate and >52 ng/L high; 1-h delta 3-5 ng/L intermediate and >5 ng/L high | RENDERED: T0 hs-cTn = 12-52 ng/L; 1-h delta = 3-5 ng/L; T0 hs-cTn >52 ng/L; 1-h delta >5 ng/L | aha-2021 | p24 | p24/narrative/table-6-esc | narrative |
| acute-low-risk | acute-low-risk | <1% 30-day risk of death or MACE | RENDERED: <1% 30-day risk of death or MACE | aha-2021 | p25 | p25/low-risk-patients-with-acute-chest-pain/1 | 1 |
| acute-low-risk | acute-low-risk | discharge without admission or urgent cardiac testing is reasonable when <1% 30-day risk of death or MACE | RENDERED: patients with acute chest pain and a <1% 30-day risk of death or MACE may be designated as low risk and discharged home without admission or urgent cardiac testing | aha-2021 | p25 | p25/low-risk-patients-with-acute-chest-pain/2 | 2a |
| stress-warranty | prior-negative-test | normal coronary angiogram or CCTA with no plaque: 2 y; normal adequate stress test: 1 y | RENDERED: Normal coronary angiogram CCTA with no stenosis or plaque 2 y; Normal stress test (given adequate stress) 1 y | aha-2021 | p25 | p25/narrative/table-7-warranty | narrative |
| prior-stress-severity | acute-intermediate-no-cad | moderate-severe ischemia on stress testing <=1 y: ICA recommended | RENDERED: moderate-severe ischemia on current or prior (≤1 year) stress testing, ICA is recommended | aha-2021 | p27 | p27/intermediate-risk-patients-with-no-known-cad/2 | 1 |
| prior-stress-severity | acute-intermediate-no-cad | mildly abnormal stress test within the past year: CCTA is reasonable | RENDERED: mildly abnormal stress test within the past year, CCTA is reasonable | aha-2021 | p27 | p27/intermediate-risk-patients-with-no-known-cad/3 | 2a |
| ccta-stenosis-ffrct | acute-intermediate-no-cad | CCTA stenosis 40%-90% in proximal or middle segment: FFR-CT is useful | RENDERED: coronary artery stenosis of 40% to 90% in a proximal or middle coronary segment on CCTA, FFR-CT can be useful | aha-2021 | p27 | p27/intermediate-risk-patients-with-no-known-cad/5 | 2a |
| ccta-stenosis-ffrct | acute-intermediate-known-cad | CCTA stenosis 40%-90% in proximal or middle segment: FFR-CT is useful | RENDERED: stenosis of 40% to 90% in a proximal or middle coronary artery on CCTA, FFR-CT can be useful | aha-2021 | p29 | p29/intermediate-risk-patients-with-acute-chest/4 | 2a |
| acute-high-risk-lvef | acute-high-risk | new LVEF <40% is a high-risk feature | RENDERED: new-onset left ventricular (LV) systolic dysfunction (ejection fraction <40%) | aha-2021 | p31 | p31/high-risk-patients-with-acute-chest-pain/1 | 1 |
| acute-cabg-high-risk | acute-prior-cabg-no-acs | new resting LVEF <35%, 2 mm ST depression at low workload or persisting into recovery, or perfusion abnormality >=10% myocardium: refer for ICA | RENDERED: left ventricular ejection fraction <35%; 2 mm of ST-segment depression at low workload or persisting into recovery; stress-induced perfusion abnormalities involving ≥10% of the myocardium; referral for ICA is useful | aha-2021 | p32 | p32/narrative/acute-cabg-high-risk | narrative |
| stable-pretest-probability | stable-chest-pain | testing is most beneficial when pretest probability >15%; testing may be considered when <=15% | RENDERED: groups in which noninvasive testing is most beneficial (pretest probability >15%); testing for CAD may be considered based on clinical judgment | aha-2021 | p40 | p40/narrative/figure-11-pretest-probability | narrative |
| pretest-probability-strata | symptomatic-pretest | age-, sex-, and anginal-symptom grid: >15%-50% and >50% strata are above the testing-benefit threshold | RENDERED: Pretest Probabilities of Obstructive CAD in Symptomatic Patients According to Age, Sex, and Symptoms; >15%-50%; >50% | aha-2021 | p40 | p40/narrative/figure-11-age-sex-symptoms | narrative |
| pretest-probability-strata | symptomatic-pretest | age 30-39 y: chest pain men <=4%, women <=5%; dyspnea men 0%, women 3%; age 40-49 y: chest pain men <=22%, women <=10%; dyspnea men 12%, women 3%; age 50-59 y: chest pain men <=32%, women <=13%; dyspnea men 20%, women 9%; age 60-69 y: chest pain men <=44%, women <=16%; dyspnea men 27%, women 14%; age >=70 y: chest pain men <=52%, women <=27%; dyspnea men 32%, women 12% | RENDERED: 30-39: chest pain men ≤4, women ≤5; dyspnea men 0, women 3. 40-49: chest pain men ≤22, women ≤10; dyspnea men 12, women 3. 50-59: chest pain men ≤32, women ≤13; dyspnea men 20, women 9. 60-69: chest pain men ≤44, women ≤16; dyspnea men 27, women 14. 70+: chest pain men ≤52, women ≤27; dyspnea men 32, women 12 | aha-2021 | p40 | p40/narrative/figure-11-displayed-cells | narrative |
| pretest-probability-strata | symptomatic-pretest | CAC 1-99, 100-999, and >=1000 are retained CAC strata for estimating pretest probability | RENDERED: CAC score 1-99; 100-999; ≥1000 | aha-2021 | p40 | p40/narrative/figure-11-cac-strata | narrative |
| exercise-capacity | stable-intermediate-high | ability to achieve >=5 METs: exercise ECG is reasonable | RENDERED: ability to achieve maximal levels of exercise (≥5 metabolic equivalents [METs]) | aha-2021 | p41 | p41/intermediate-high-risk-patients-with-stable/4 | 2a |
| ccta-stenosis-ffrct | stable-intermediate-high | CCTA stenosis 40%-90% in proximal or middle segment: FFR-CT is useful | RENDERED: stenosis of 40% to 90% in a proximal or middle coronary artery on CCTA, FFR-CT can be useful | aha-2021 | p41 | p41/intermediate-high-risk-patients-with-stable/7 | 2a |
| ffr-ischemia | stable-obstructive-cad | FFR-CT <=0.80 supports ICA for therapeutic decision-making | RENDERED: FFR-CT ≤0.80 | aha-2021 | p45 | p45/patients-with-obstructive-cad-who-present/3 | 1 |
| stable-high-risk-anatomy | stable-obstructive-cad | left main >=50% or all 3 vessels >=70%: ICA is effective for risk stratification | RENDERED: stenosis ≥50% in the left main coronary artery or obstructive CAD with FFR-CT ≤0.80, or severe stenosis (≥70%) in all 3 main vessels | aha-2021 | p45 | p45/patients-with-obstructive-cad-who-present/3 | 1 |
| stent-diameter | stable-prior-stent | stent diameter >=3 mm: CCTA is reasonable to evaluate patency | RENDERED: stent diameter ≥3 mm, CCTA is reasonable to evaluate stent patency | aha-2021 | p45 | p45/patients-with-obstructive-cad-who-present/4 | 2a |
| cabg-stress-high-risk | prior-cabg-stable | stress perfusion ischemia >=10% of myocardium or exercise ECG ST depression >=2 mm supports ICA | RENDERED: ≥10% ischemic myocardium or ≥2-mm horizontal or downsloping ST-segment depression | aha-2021 | p48 | p48/narrative/cabg-high-risk-stress | narrative |
| ccta-stenosis-ffrct | stable-nonobstructive-cad | CCTA stenosis 40%-90% in proximal or middle segment: FFR-CT can guide vessel-specific ischemia decisions | RENDERED: stenosis of 40% to 90% in a proximal or middle coronary artery on CCTA, FFR-CT can be useful | aha-2021 | p48 | p48/patients-with-known-nonobstructive-cad/2 | 2a |
| inoca-entry-ffr | suspected-inoCA | FFR >=0.80: proceed with INOCA endotype evaluation | RENDERED: FFR ≥0.80 | aha-2021 | p50 | p50/narrative/figure-14-ffr-entry | narrative |
| inoca-noncardiac | suspected-inoCA | CFR >=2.0, IMR <25, and negative provocative testing: noncardiac endotype | RENDERED: CFR ≥2.0; IMR <25; Negative provocative testing; Noncardiac | aha-2021 | p50 | p50/narrative/figure-14-noncardiac | narrative |
| inoca-vasospasm | suspected-inoCA | >90% epicardial diameter reduction with acetylcholine plus angina and ischemic ECG changes: vasospastic angina | RENDERED: >90% diameter reduction with ACh; Angina; Ischemic ECG changes; Vasospastic angina | aha-2021 | p50 | p50/narrative/figure-14-vasospasm | narrative |
| inoca-cmd | suspected-inoCA | IMR >=25, CFR <2.0, or angina with ST depression during acetylcholine testing: CMD | RENDERED: IMR ≥25; CFR <2.0; Angina and ST depression with ACh; Coronary microvascular dysfunction | aha-2021 | p50 | p50/narrative/figure-14-cmd | narrative |
| gi-evaluation-time | gi-red-flags | early endoscopic evaluation usually within 2 weeks | RENDERED: early endoscopic evaluation (usually within 2 weeks) | aha-2021 | p38 | p38/narrative/gi-alarm-features | narrative |

## Conflicts

**CONFLICT: cad-stenosis-class** - The same source classifies coronary stenosis as
`obstructive CAD >=50%` and `nonobstructive CAD <50%`; these are complementary sides
of the source's 50% boundary.

**CONFLICT: acute-low-risk** - Distinct values are `<1% 30-day risk of death or MACE` and `discharge without admission or urgent cardiac testing is reasonable when <1% 30-day risk of death or MACE`; the second value states the action attached to the first value's low-risk boundary.

**CONFLICT: acute-high-risk-lvef** - General high-risk acute chest pain uses `new LVEF <40% is a high-risk feature`, whereas the distinct prior-CABG acute population uses `new resting LVEF <35%` among features prompting referral for ICA; population and pathway explain the different LVEF cutoffs.

**CONFLICT: cdp-heart-score** - The same acute suspected-ACS population has `low <=3`,
`intermediate 4-6`, and `high 7-10`; the distinct values are mutually exclusive HEART
Pathway strata.

**CONFLICT: cdp-esc-troponin** - The same acute suspected-ACS population has T0 hs-cTn
`12-52 ng/L` versus `>52 ng/L`, and 1-hour delta `3-5 ng/L` versus `>5 ng/L`; the
distinct values define intermediate- and high-risk ESC pathway strata.

**CONFLICT: prior-stress-severity** - Distinct values are `moderate-severe ischemia on stress testing <=1 y: ICA recommended` and `mildly abnormal stress test within the past year: CCTA is reasonable`; the different actions follow different prior-test severity in the same acute intermediate-risk population with no known CAD.

**CONFLICT: pretest-probability-strata** - Distinct values are `age-, sex-, and anginal-symptom grid: >15%-50% and >50% strata are above the testing-benefit threshold`, `age 30-39 y: chest pain men <=4%, women <=5%; dyspnea men 0%, women 3%; age 40-49 y: chest pain men <=22%, women <=10%; dyspnea men 12%, women 3%; age 50-59 y: chest pain men <=32%, women <=13%; dyspnea men 20%, women 9%; age 60-69 y: chest pain men <=44%, women <=16%; dyspnea men 27%, women 14%; age >=70 y: chest pain men <=52%, women <=27%; dyspnea men 32%, women 12%`, and `CAC 1-99, 100-999, and >=1000 are retained CAC strata for estimating pretest probability`; clinical presentation and CAC are alternative inputs to the source's probability estimate.

**CONFLICT: stress-warranty** - A prior negative test has `2 y` after a normal coronary
angiogram or plaque-free CCTA and `1 y` after an adequate normal stress test; the
modality explains the different warranty periods.

**CONFLICT: stable-high-risk-anatomy** - The combined value is exactly `left main >=50%
or all 3 vessels >=70%: ICA is effective for risk stratification`; `FFR-CT <=0.80` is an
additional physiologic route in the cited recommendation.

## Coverage

The exact recommendation index contains 90 distinct records. Threshold rows cite 16
distinct exact recommendation locators. The remaining 74 records are accounted for
individually below; narrative locators do not discharge exact-index accounting.

- `p8/defining-chest-pain/1` - No additional numeric patient-action threshold retained.
- `p8/defining-chest-pain/2` - No additional numeric patient-action threshold retained.
- `p11/a-focus-on-the-uniqueness-of-chest-pain/1` - No additional numeric patient-action threshold retained.
- `p11/a-focus-on-the-uniqueness-of-chest-pain/2` - No additional numeric patient-action threshold retained.
- `p12/considerations-for-diverse-patient-populations/1` - No additional numeric patient-action threshold retained.
- `p12/considerations-for-diverse-patient-populations/2` - No additional numeric patient-action threshold retained.
- `p14/setting-considerations/1` - No additional numeric patient-action threshold retained.
- `p14/setting-considerations/2` - No additional numeric patient-action threshold retained.
- `p14/setting-considerations/4` - No additional numeric patient-action threshold retained.
- `p14/setting-considerations/5` - No additional numeric patient-action threshold retained.
- `p15/electrocardiogram/1` - No additional numeric patient-action threshold retained.
- `p15/electrocardiogram/2` - No additional numeric patient-action threshold retained.
- `p15/electrocardiogram/3` - No additional numeric patient-action threshold retained.
- `p16/biomarkers/1` - No additional numeric patient-action threshold retained.
- `p16/biomarkers/2` - No additional numeric patient-action threshold retained.
- `p16/biomarkers/4` - No additional numeric patient-action threshold retained.
- `p22/patients-with-acute-chest-pain-and-suspected/4` - No additional numeric patient-action threshold retained.
- `p22/patients-with-acute-chest-pain-and-suspected/1` - No additional numeric patient-action threshold retained.
- `p22/patients-with-acute-chest-pain-and-suspected/3` - No additional numeric patient-action threshold retained.
- `p26/intermediate-risk-patients-with-acute-chest/1` - No additional numeric patient-action threshold retained.
- `p26/intermediate-risk-patients-with-acute-chest/2` - No additional numeric patient-action threshold retained.
- `p27/intermediate-risk-patients-with-no-known-cad/1` - No additional numeric patient-action threshold retained.
- `p27/intermediate-risk-patients-with-no-known-cad/4` - No additional numeric patient-action threshold retained.
- `p27/intermediate-risk-patients-with-no-known-cad/6` - No additional numeric patient-action threshold retained.
- `p27/intermediate-risk-patients-with-no-known-cad/7` - No additional numeric patient-action threshold retained.
- `p28/intermediate-risk-patients-with-acute-chest/1` - No additional numeric patient-action threshold retained.
- `p29/intermediate-risk-patients-with-acute-chest/2` - No additional numeric patient-action threshold retained.
- `p29/intermediate-risk-patients-with-acute-chest/3` - No additional numeric patient-action threshold retained.
- `p29/intermediate-risk-patients-with-acute-chest/5` - No additional numeric patient-action threshold retained.
- `p31/high-risk-patients-with-acute-chest-pain/2` - No additional numeric patient-action threshold retained.
- `p31/high-risk-patients-with-acute-chest-pain/3` - No additional numeric patient-action threshold retained.
- `p31/acute-chest-pain-in-patients-with-prior-cabg/1` - No additional numeric patient-action threshold retained.
- `p31/acute-chest-pain-in-patients-with-prior-cabg/2` - No additional numeric patient-action threshold retained.
- `p33/shared-decision-making-in-patients-with-acute/1` - No additional numeric patient-action threshold retained.
- `p33/shared-decision-making-in-patients-with-acute/2` - No additional numeric patient-action threshold retained.
- `p34/acute-chest-pain-with-suspected-acute-aortic/1` - No additional numeric patient-action threshold retained.
- `p34/acute-chest-pain-with-suspected-acute-aortic/2` - No additional numeric patient-action threshold retained.
- `p35/acute-chest-pain-with-suspected/1` - No additional numeric patient-action threshold retained.
- `p35/acute-chest-pain-with-suspected/2` - No additional numeric patient-action threshold retained.
- `p35/acute-chest-pain-with-suspected/3` - No additional numeric patient-action threshold retained.
- `p35/acute-chest-pain-with-suspected/4` - No additional numeric patient-action threshold retained.
- `p35/acute-chest-pain-with-suspected-pe/1` - No additional numeric patient-action threshold retained.
- `p35/acute-chest-pain-with-suspected-pe/2` - No additional numeric patient-action threshold retained.
- `p36/acute-chest-pain-with-vhd/1` - No additional numeric patient-action threshold retained.
- `p36/acute-chest-pain-with-vhd/2` - No additional numeric patient-action threshold retained.
- `p36/acute-chest-pain-with-vhd/3` - No additional numeric patient-action threshold retained.
- `p39/evaluation-of-acute-chest-pain-in-patients-with/1` - No additional numeric patient-action threshold retained.
- `p39/evaluation-of-acute-chest-pain-in-patients-with/2` - No additional numeric patient-action threshold retained.
- `p40/low-risk-patients-with-stable-chest-pain-and/1` - No additional numeric patient-action threshold retained.
- `p40/low-risk-patients-with-stable-chest-pain-and/2` - No additional numeric patient-action threshold retained.
- `p40/low-risk-patients-with-stable-chest-pain-and/3` - No additional numeric patient-action threshold retained.
- `p41/intermediate-high-risk-patients-with-stable/1` - No additional numeric patient-action threshold retained.
- `p41/intermediate-high-risk-patients-with-stable/2` - No additional numeric patient-action threshold retained.
- `p41/intermediate-high-risk-patients-with-stable/3` - No additional numeric patient-action threshold retained.
- `p41/intermediate-high-risk-patients-with-stable/5` - No additional numeric patient-action threshold retained.
- `p41/intermediate-high-risk-patients-with-stable/6` - No additional numeric patient-action threshold retained.
- `p41/intermediate-high-risk-patients-with-stable/8` - No additional numeric patient-action threshold retained.
- `p41/intermediate-high-risk-patients-with-stable/9` - No additional numeric patient-action threshold retained.
- `p44/patients-with-known-cad-presenting-with/1` - No additional numeric patient-action threshold retained.
- `p44/patients-with-known-cad-presenting-with/2` - No additional numeric patient-action threshold retained.
- `p45/patients-with-obstructive-cad-who-present/1` - No additional numeric patient-action threshold retained.
- `p45/patients-with-obstructive-cad-who-present/2` - No additional numeric patient-action threshold retained.
- `p45/patients-with-obstructive-cad-who-present/5` - No additional numeric patient-action threshold retained.
- `p45/patients-with-obstructive-cad-who-present/6` - No additional numeric patient-action threshold retained.
- `p45/patients-with-obstructive-cad-who-present/7` - No additional numeric patient-action threshold retained.
- `p45/patients-with-obstructive-cad-who-present/8` - No additional numeric patient-action threshold retained.
- `p47/patients-with-prior-cabg-surgery-with-stable/1` - No additional numeric patient-action threshold retained.
- `p47/patients-with-prior-cabg-surgery-with-stable/2` - No additional numeric patient-action threshold retained.
- `p48/patients-with-known-nonobstructive-cad/1` - No additional numeric patient-action threshold retained.
- `p48/patients-with-known-nonobstructive-cad/3` - No additional numeric patient-action threshold retained.
- `p49/patients-with-inoca/1` - No additional numeric patient-action threshold retained.
- `p49/patients-with-inoca/2` - No additional numeric patient-action threshold retained.
- `p49/patients-with-inoca/3` - No additional numeric patient-action threshold retained.
- `p49/patients-with-inoca/4` - No additional numeric patient-action threshold retained.
