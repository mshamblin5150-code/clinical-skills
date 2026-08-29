# Hypertension — threshold sheet

<!-- schema: threshold-sheet/2 -->

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

**Not read:** the front matter and methods, and the narrative sections and evidence
tables. A number stated only in the prose around a recommendation is not here, so
**absent from this sheet does not mean absent from the guideline.**

| span | pages | read |
| --- | --- | --- |
| front matter and methods | 1-10 | no |
| recommendation tables | 11-74 | yes |
| narrative sections and evidence tables | 11-74 | no |
| references | 75-97 | exempt: citation list contains no clinical prose |
| appendices | 98-105 | read 2026-08-23 |

citations resolved against C:/codeing/guidelines-src on 2026-08-16
extraction identity: producer dc7512e01421ded48cc5d8e5f053a840f09b40ea; tools/guidelines_extract.py sha256 d247c269f42141cda14c8cd3d1bb8bce7db91ba66df74d442a3d611c284d251e


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

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
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
