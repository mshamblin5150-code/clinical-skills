# Blood pressure in chronic kidney disease — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2021 | KDIGO | KDIGO/KDIGO-2021-Blood-Pressure-in-CKD-Guideline | guideline | 2021 guideline | 2021-03 | https://doi.org/10.1016/j.kint.2020.11.003 | stated | bound |

## Scope

**Read:** all 92 source pages: cover and journal matter; title, citation, contents,
tables, nomenclature, conversion factors, abbreviations, notice, foreword, figures,
membership, abstract, introduction, the full summary, all five clinical chapters,
every table and figure, guideline-development methods, biographies, disclosures,
acknowledgments, and references. The rows retain numbers that define or classify CKD,
prepare or repeat a BP measurement, set a diet or activity goal, set or qualify a BP
target, select or monitor therapy, or otherwise change an action for a patient.
Prevalence estimates, effect estimates, trial eligibility and results, research-only
protocols not adopted for clinical reference, publication years, and bibliography
numbers were read but do not produce rows.

Pages 14 and 52 were rendered and read to resolve comparison operators, table cells,
and the branch structure of Figure 5. Figure 5 is retained only where the text on p51
directs clinicians to use it as a reference and modify it as they see fit.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| cover, journal matter, contents, tables, and grading key | 1-13 | read 2026-08-31; blind 2026-08-31 |
| CKD nomenclature and classification | 14 | yes |
| conversion factors, abbreviations, notice, foreword, membership, abstract, and introduction | 15-27 | read 2026-08-31; blind 2026-08-31 |
| summary of recommendations and practice points | 28-30 | read 2026-08-31; blind 2026-08-31 |
| chapter 1: blood pressure measurement | 31-36 | yes |
| chapter 2: lifestyle interventions | 37-41 | yes |
| chapter 3: adults with CKD not receiving dialysis | 42-59 | yes |
| chapter 4: kidney transplant recipients | 60-63 | yes |
| chapter 5: children with CKD | 64-66 | yes |
| guideline-development methods | 67-75 | read 2026-08-31; blind 2026-08-31 |
| biographies, disclosures, and acknowledgments | 76-83 | read 2026-08-31; blind 2026-08-31 |
| references | 84-92 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 3717244e8a539e710f32180720b442cf0d1dda12810cecbe61e4e8cfb54f7b23; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| people-ckd | people with CKD |
| ckd-g1 | CKD G1 |
| ckd-g2 | CKD G2 |
| ckd-g3a | CKD G3a |
| ckd-g3b | CKD G3b |
| ckd-g4 | CKD G4 |
| ckd-g5 | CKD G5 |
| ckd-a1 | CKD A1 |
| ckd-a2 | CKD A2 |
| ckd-a3 | CKD A3 |
| adults-ckd | adults age >=18 years with CKD |
| adults-high-bp-ckd-nondialysis-nontransplant | adults age >=18 years with high BP and CKD not receiving dialysis and without a kidney transplant |
| adults-high-bp-ckd-intolerant | adults with high BP and CKD who cannot tolerate SBP <120 mm Hg after a slow, gradual decrease over months |
| adults-high-bp-ckd-limited-resources | adults with high BP and CKD in settings with limited resources |
| adults-high-bp-ckd-low-baseline-dbp | adults with high BP and CKD and very low baseline DBP, particularly with coronary artery disease |
| adults-high-bp-ckd-severe | adults with CKD and severe hypertension |
| adults-high-bp-ckd-g1-g4-a3-no-diabetes | people with high BP, CKD G1-G4, A3, and no diabetes |
| adults-high-bp-ckd-g1-g4-a2-no-diabetes | people with high BP, CKD G1-G4, A2, and no diabetes |
| adults-high-bp-ckd-g1-g4-a2-a3-diabetes | people with high BP, CKD G1-G4, A2 or A3, and diabetes |
| people-ckd-rasi | people with CKD starting or increasing the dose of an ACE inhibitor or ARB |
| people-ckd-rasi-hyperkalemia-risk | people with CKD at risk for hyperkalemia starting an ACE inhibitor or ARB |
| people-ckd-rasi-kidney-failure | people with CKD receiving an ACE inhibitor or ARB while treating kidney failure |
| people-ckd-resistant-hypertension | people with CKD and resistant hypertension |
| adult-kidney-transplant-high-bp | adult kidney transplant recipients age >=18 years with high BP |
| children-ckd | children with CKD |
| children-high-bp-ckd-no-abpm | children with high BP and CKD when ABPM is unavailable |
| children-ckd-hbpm | children with CKD using home BP monitoring |
| children-ckd-short | children with CKD and height <120 cm |

## Quantities

| key | verbatim |
| --- | --- |
| ckd-minimum-duration | minimum duration defining CKD |
| ckd-gfr-category | GFR category threshold |
| ckd-albuminuria-category | albuminuria category threshold |
| standardized-bp-rest | seated rest before standardized office BP measurement |
| standardized-bp-trigger-avoidance | avoidance period before standardized office BP measurement |
| standardized-bp-cuff-encirclement | cuff bladder encirclement of the arm |
| standardized-bp-repeat-interval | interval between repeated measurements |
| standardized-bp-inflation | cuff inflation above pulse-obliteration pressure |
| standardized-bp-deflation | cuff deflation rate |
| standardized-bp-reading-count | readings and occasions used to estimate BP |
| white-coat-out-of-office-monitoring | out-of-office BP assessment frequency |
| treated-hbpm-before-visit | home BP monitoring before an office visit |
| sodium-intake | daily sodium and sodium-chloride target |
| pediatric-sodium-intake | body-weight adjustment of the adult sodium target |
| physical-activity | cumulative moderate-intensity physical activity |
| standardized-office-sbp-target | standardized office systolic BP target |
| low-dbp-caution | baseline diastolic BP warranting uncertainty about intensive SBP lowering |
| severe-hypertension-definition | severe hypertension outside the pivotal target trial |
| intolerant-sbp-target | tolerated systolic BP target after inability to tolerate the intensive target |
| limited-resource-sbp-target | reasonable systolic BP control in limited-resource settings |
| rasi-initiation-g1-g4-a3 | ACE inhibitor or ARB initiation by CKD stage and albuminuria |
| rasi-initiation-g1-g4-a2 | ACE inhibitor or ARB initiation by CKD stage and albuminuria |
| rasi-initiation-g1-g4-a2-a3-diabetes | ACE inhibitor or ARB initiation by CKD stage, albuminuria, and diabetes |
| combination-therapy-distance | distance above target prompting combination antihypertensive therapy |
| rasi-laboratory-monitoring | BP, creatinine, and potassium check after initiation or dose increase |
| rasi-potassium-high-risk-monitoring | potassium check after initiation in people at risk for hyperkalemia |
| rasi-creatinine-continuation | creatinine rise permitting continuation versus reassessment |
| rasi-kidney-failure-reduction | eGFR threshold for considering dose reduction or discontinuation to reduce uremic symptoms |
| rasi-low-egfr-potassium-monitoring | eGFR threshold requiring close potassium monitoring |
| resistant-hypertension-definition | agents defining resistant hypertension |
| mra-low-egfr-caution | eGFR level associated with greater MRA adverse-effect concern |
| sprint-initial-drug-count | initial number of drugs in the clinical-reference algorithm |
| sprint-intensification-sbp | SBP prompting titration or an added drug |
| sprint-follow-up | follow-up interval during SBP intensification |
| sprint-dbp-current-trigger | current-visit DBP prompting titration or an added drug |
| sprint-dbp-persistent-trigger | DBP on repeated visits prompting titration or an added drug |
| sprint-single-agent-option | age, SBP, and baseline-medication conditions for a single-agent option |
| sprint-second-agent-trigger | interval and SBP prompting a second drug in the single-agent option |
| transplant-sbp-target | kidney-transplant standardized office SBP target |
| transplant-dbp-target | kidney-transplant standardized office DBP target |
| pediatric-map-target | 24-hour MAP target by ABPM |
| pediatric-hbpm-duration | home BP monitoring duration |
| pediatric-hbpm-rest | seated rest before home BP monitoring |
| pediatric-hbpm-repeat-interval | interval between duplicate home BP readings |
| pediatric-hbpm-reading-count | minimum weekly home BP readings |
| pediatric-map-alternative-range | MAP range that may also be considered |
| pediatric-low-clinic-bp-abpm | clinic BP level supporting less-frequent ABPM consideration |
| pediatric-abpm-height-floor | height below which normative ABPM data do not exist |
| pediatric-abpm-monitoring | ABPM monitoring frequency |
| pediatric-office-monitoring | standardized auscultatory office BP monitoring frequency |
| pediatric-office-sbp-fallback | standardized manual office SBP target when ABPM is unavailable |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckd-minimum-duration | people-ckd | abnormalities of kidney structure or function present for >3 months | RENDERED: CKD is defined as abnormalities of kidney structure or function, present for > 3 months | kdigo-2021 | p14 | p14/narrative/ckd-definition | narrative |
| ckd-gfr-category | ckd-g1 | GFR >=90 mL/min/1.73 m² | RENDERED: GFR category G1: ≥90 ml/min/1.73 m² | kdigo-2021 | p14 | p14/narrative/gfr-g1 | narrative |
| ckd-gfr-category | ckd-g2 | GFR 60-89 mL/min/1.73 m² | RENDERED: GFR category G2: 60–89 ml/min/1.73 m² | kdigo-2021 | p14 | p14/narrative/gfr-g2 | narrative |
| ckd-gfr-category | ckd-g3a | GFR 45-59 mL/min/1.73 m² | RENDERED: GFR category G3a: 45–59 ml/min/1.73 m² | kdigo-2021 | p14 | p14/narrative/gfr-g3a | narrative |
| ckd-gfr-category | ckd-g3b | GFR 30-44 mL/min/1.73 m² | RENDERED: GFR category G3b: 30–44 ml/min/1.73 m² | kdigo-2021 | p14 | p14/narrative/gfr-g3b | narrative |
| ckd-gfr-category | ckd-g4 | GFR 15-29 mL/min/1.73 m² | RENDERED: GFR category G4: 15–29 ml/min/1.73 m² | kdigo-2021 | p14 | p14/narrative/gfr-g4 | narrative |
| ckd-gfr-category | ckd-g5 | GFR <15 mL/min/1.73 m² | RENDERED: GFR category G5: <15 ml/min/1.73 m² | kdigo-2021 | p14 | p14/narrative/gfr-g5 | narrative |
| ckd-albuminuria-category | ckd-a1 | ACR <30 mg/g (<3 mg/mmol) | RENDERED: A1: <30 mg/g; <3 mg/mmol | kdigo-2021 | p14 | p14/narrative/albuminuria-a1 | narrative |
| ckd-albuminuria-category | ckd-a2 | ACR 30-300 mg/g (3-30 mg/mmol) | RENDERED: A2: 30–300 mg/g; 3–30 mg/mmol | kdigo-2021 | p14 | p14/narrative/albuminuria-a2 | narrative |
| ckd-albuminuria-category | ckd-a3 | ACR >300 mg/g (>30 mg/mmol) | RENDERED: A3: >300 mg/g; >30 mg/mmol | kdigo-2021 | p14 | p14/narrative/albuminuria-a3 | narrative |
| standardized-bp-rest | adults-ckd | relax seated for >5 minutes | Have the patient relax, sitting in a chair (feet on floor, back supported) for > 5 min | kdigo-2021 | p31 | p31/narrative/standardized-bp-rest | narrative |
| standardized-bp-trigger-avoidance | adults-ckd | avoid caffeine, exercise, and smoking for at least 30 minutes | The patient should avoid caffeine, exercise, and smoking for at least 30 min before measurement | kdigo-2021 | p31 | p31/narrative/standardized-bp-trigger-avoidance | narrative |
| standardized-bp-cuff-encirclement | adults-ckd | cuff bladder encircles 80% of the arm | Use the correct cuff size, such that the bladder encircles 80% of the arm | kdigo-2021 | p31 | p31/narrative/standardized-bp-cuff-encirclement | narrative |
| standardized-bp-repeat-interval | adults-ckd | separate repeated measurements by 1-2 minutes | Separate repeated measurements by 1-2 min | kdigo-2021 | p31 | p31/narrative/standardized-bp-repeat-interval | narrative |
| standardized-bp-inflation | adults-ckd | inflate cuff 20-30 mm Hg above radial-pulse obliteration pressure | Inflate the cuff 20-30 mm Hg above this level for an auscultatory determination of the BP level | kdigo-2021 | p31 | p31/narrative/standardized-bp-inflation | narrative |
| standardized-bp-deflation | adults-ckd | deflate cuff pressure 2 mm Hg per second | deflate the cuff pressure 2 mm Hg per second | kdigo-2021 | p31 | p31/narrative/standardized-bp-deflation | narrative |
| standardized-bp-reading-count | adults-ckd | average >=2 readings obtained on >=2 occasions | Use an average of ≥ 2 readings obtained on ≥ 2 occasions to estimate the individual's level of BP | kdigo-2021 | p31 | p31/narrative/standardized-bp-reading-count | narrative |
| white-coat-out-of-office-monitoring | adults-ckd | annual out-of-office BP assessment may be useful when untreated | RENDERED: For individuals not taking antihypertensive medication identified as having "white-coat" hypertension, annual out-of-office BP assessments may be useful. | kdigo-2021 | p34 | p34/recommendation/1.2 | 2 |
| treated-hbpm-before-visit | adults-ckd | 1 week of daily HBPM before each office visit may be useful | RENDERED: For individuals taking antihypertensive medication, 1 week of daily HBPM prior to each office visit may be useful | kdigo-2021 | p34 | p34/narrative/treated-hbpm | narrative |
| sodium-intake | adults-high-bp-ckd-nondialysis-nontransplant | <2 g sodium/day (<90 mmol sodium/day or <5 g sodium chloride/day) | Recommendation 2.1.1: We suggest targeting a sodium intake <2 g of sodium per day (or <90 mmol of sodium per day, or <5 g of sodium chloride per day) | kdigo-2021 | p37 | p37/recommendation/2.1.1 | 2 |
| pediatric-sodium-intake | children-ckd | adjust the <2 g sodium/day (<90 mmol/day) adult target for body weight | adjusting the <2 g (<90 mmol) daily target for body weight in children would be reasonable | kdigo-2021 | p38 | p38/narrative/pediatric-sodium | narrative |
| physical-activity | adults-high-bp-ckd-nondialysis-nontransplant | moderate intensity for >=150 cumulative minutes/week or compatible with cardiovascular and physical tolerance | RENDERED: moderate-intensity physical activity for a cumulative duration of at least 150 minutes per week, or to a level compatible with their cardiovascular and physical tolerance | kdigo-2021 | p40 | p40/recommendation/2.2.1 | 2 |
| standardized-office-sbp-target | adults-high-bp-ckd-nondialysis-nontransplant | SBP <120 mm Hg when tolerated using standardized office measurement | RENDERED: adults with high BP and CKD be treated with a target systolic blood pressure (SBP) of <120 mm Hg, when tolerated, using standardized office BP measurement | kdigo-2021 | p42 | p42/recommendation/3.1.1 | 2 |
| standardized-office-sbp-target | adults-high-bp-ckd-nondialysis-nontransplant | do not apply SBP <120 mm Hg to nonstandardized measurements | RENDERED: It is potentially hazardous to apply the recommended SBP target of <120 mm Hg to BP measurements obtained in a non-standardized manner. | kdigo-2021 | p49 | p49/practice-point/1 | practice-point |
| low-dbp-caution | adults-high-bp-ckd-low-baseline-dbp | very low baseline DBP example <50 mm Hg creates less certainty about intensive SBP lowering | People with very low baseline DBP (e.g., <50 mm Hg), particularly in the presence of coronary artery disease | kdigo-2021 | p42 | p42/narrative/low-dbp-caution | narrative |
| severe-hypertension-definition | adults-high-bp-ckd-severe | SBP >=180 mm Hg on no or 1 antihypertensive drug, or >=150 mm Hg on >4 antihypertensive drugs | RENDERED: Severe hypertension, such as SBP ≥180 mm Hg on no or 1 antihypertensive drug, or ≥150 mm Hg on >4 antihypertensive drugs | kdigo-2021 | p43 | p43/narrative/severe-hypertension | narrative |
| intolerant-sbp-target | adults-high-bp-ckd-intolerant | maintain SBP <130 mm Hg, <140 mm Hg, or an even higher tolerated goal | If the patient cannot tolerate SBP <120 mm Hg despite a slow, gradual decrease in SBP over months, efforts should be made to maintain SBP <130 mm Hg, <140 mm Hg, or an even higher tolerated SBP goal. | kdigo-2021 | p43 | p43/narrative/intolerant-target | narrative |
| limited-resource-sbp-target | adults-high-bp-ckd-limited-resources | reasonable control example SBP <140 mm Hg | in those settings, it is probably more important to ensure that all eligible patients have at least reasonable BP control (e.g., SBP <140 mm Hg) | kdigo-2021 | p48 | p48/narrative/limited-resource-target | narrative |
| rasi-initiation-g1-g4-a3 | adults-high-bp-ckd-g1-g4-a3-no-diabetes | start ACE inhibitor or ARB for CKD G1-G4 and A3 without diabetes | RENDERED: starting renin-angiotensin-system inhibitors (RASi) (angiotensin-converting enzyme inhibitor [ACEi] or angiotensin II receptor blocker [ARB]) for people with high BP, CKD, and severely increased albuminuria (G1-G4, A3) without diabetes | kdigo-2021 | p51 | p51/recommendation/3.2.1 | 1 |
| rasi-initiation-g1-g4-a2 | adults-high-bp-ckd-g1-g4-a2-no-diabetes | start ACE inhibitor or ARB for CKD G1-G4 and A2 without diabetes | starting RASi (ACEi or ARB) for people with high BP, CKD, and moderately increased albuminuria (G1-G4, A2) without diabetes | kdigo-2021 | p54 | p54/recommendation/3.2.2 | 2 |
| rasi-initiation-g1-g4-a2-a3-diabetes | adults-high-bp-ckd-g1-g4-a2-a3-diabetes | start ACE inhibitor or ARB for CKD G1-G4 and A2 or A3 with diabetes | starting RASi (ACEi or ARB) for people with high BP, CKD, and moderately-to-severely increased albuminuria (G1-G4, A2 and A3) with diabetes | kdigo-2021 | p54 | p54/recommendation/3.2.3 | 1 |
| combination-therapy-distance | adults-high-bp-ckd-nondialysis-nontransplant | BP at least 20 mm Hg above target suggests starting combinations of several antihypertensive drugs | RENDERED: Many people with CKD and BP of at least 20 mm Hg above the target will need combinations of several antihypertensive drugs. Starting antihypertensive therapy in such people with antihypertensive drug combinations is suggested. | kdigo-2021 | p50 | p50/narrative/combination-therapy | narrative |
| rasi-laboratory-monitoring | people-ckd-rasi | check BP, serum creatinine, and serum potassium within 2-4 weeks | Changes in BP, serum creatinine, and serum potassium should be checked within 2-4 weeks of initiation or increase in the dose of a RASi | kdigo-2021 | p57 | p57/practice-point/2 | practice-point |
| rasi-potassium-high-risk-monitoring | people-ckd-rasi-hyperkalemia-risk | measure potassium before and 1-2 weeks after initiation | In patients at risk for hyperkalemia, measuring serum potassium before and at 1-2 weeks after initiation of RASi is recommended | kdigo-2021 | p57 | p57/narrative/potassium-high-risk | narrative |
| rasi-creatinine-continuation | people-ckd-rasi | continue unless creatinine rises >30% within 4 weeks after initiation or dose increase | Continue ACEi or ARB therapy unless serum creatinine rises by more than 30% within 4 weeks following initiation of treatment or an increase in dose. | kdigo-2021 | p57 | p57/practice-point/4 | practice-point |
| rasi-kidney-failure-reduction | people-ckd-rasi-kidney-failure | at eGFR <15 mL/min/1.73 m² consider reducing or discontinuing to reduce uremic symptoms | RENDERED: Consider reducing the dose or discontinuing ACEi or ARB in the setting of either symptomatic hypotension or uncontrolled hyperkalemia despite medical treatment, or to reduce uremic symptoms while treating kidney failure (estimated glomerular filtration rate [eGFR] <15 ml/min per 1.73 m2). | kdigo-2021 | p57 | p57/practice-point/5 | practice-point |
| rasi-low-egfr-potassium-monitoring | people-ckd-rasi | eGFR <30 mL/min/1.73 m² requires close serum-potassium monitoring | RENDERED: When these drugs are used in patients with eGFR <30 ml/min per 1.73 m2, close monitoring of serum potassium is required. | kdigo-2021 | p58 | p58/narrative/low-egfr-potassium | narrative |
| resistant-hypertension-definition | people-ckd-resistant-hypertension | uncontrolled hypertension on 3 antihypertensive agents including a diuretic | RENDERED: resistant hypertension (defined as uncontrolled hypertension on 3 antihypertensive agents including a diuretic) | kdigo-2021 | p58 | p58/practice-point/1 | practice-point |
| mra-low-egfr-caution | people-ckd-resistant-hypertension | MRA adverse-effect concern is greater at eGFR <45 mL/min/1.73 m² | particularly among patients with eGFR <45 ml/min per 1.73 m2 | kdigo-2021 | p58 | p58/narrative/mra-low-egfr | narrative |
| sprint-initial-drug-count | adults-high-bp-ckd-nondialysis-nontransplant | begin with 2- or 3-drug therapy in the referenced algorithm | RENDERED: At randomization visit, begin with 2- or 3-drug therapy | kdigo-2021 | p52 | p52/narrative/sprint-initial-drug-count | narrative |
| sprint-intensification-sbp | adults-high-bp-ckd-nondialysis-nontransplant | SBP >=120 mm Hg at the current visit prompts titration or an added therapy | RENDERED: Is SBP ≥120 mm Hg this visit? ... Titrate or add therapy not already in use | kdigo-2021 | p52 | p52/narrative/sprint-intensification-sbp | narrative |
| sprint-follow-up | adults-high-bp-ckd-nondialysis-nontransplant | see monthly until SBP <120 mm Hg after intensification | RENDERED: See participant monthly until SBP <120 mm Hg | kdigo-2021 | p52 | p52/narrative/sprint-follow-up | narrative |
| sprint-dbp-current-trigger | adults-high-bp-ckd-nondialysis-nontransplant | current DBP >=100 mm Hg prompts titration or an added therapy | RENDERED: Is DBP ≥100 mm Hg at this visit ... Titrate or add therapy not already in use | kdigo-2021 | p52 | p52/narrative/sprint-dbp-current-trigger | narrative |
| sprint-dbp-persistent-trigger | adults-high-bp-ckd-nondialysis-nontransplant | DBP >=90 mm Hg on the last 2 visits prompts titration or an added therapy | RENDERED: is DBP ≥90 mm Hg on last 2 visits? ... Titrate or add therapy not already in use | kdigo-2021 | p52 | p52/narrative/sprint-dbp-persistent-trigger | narrative |
| sprint-single-agent-option | adults-high-bp-ckd-nondialysis-nontransplant | age >=75 years with SBP <140 mm Hg on 0-1 medication may begin with one agent | RENDERED: May begin with a single agent for participants aged ≥75 years with SBP <140 mm Hg on 0–1 medications at study entry. | kdigo-2021 | p52 | p52/narrative/sprint-single-agent-option | narrative |
| sprint-second-agent-trigger | adults-high-bp-ckd-nondialysis-nontransplant | at the 1-month visit, add a second medication if asymptomatic and SBP >=130 mm Hg | RENDERED: A second medication should be added at the 1-month visit if participant is asymptomatic and SBP ≥130 mm Hg. | kdigo-2021 | p52 | p52/narrative/sprint-second-agent-trigger | narrative |
| transplant-sbp-target | adult-kidney-transplant-high-bp | standardized office SBP <130 mm Hg | RENDERED: Treat adult kidney transplant recipients with high BP to a target BP of <130 mm Hg systolic and <80 mm Hg diastolic using standardized office BP measurement | kdigo-2021 | p60 | p60/practice-point/1 | practice-point |
| transplant-dbp-target | adult-kidney-transplant-high-bp | standardized office DBP <80 mm Hg | RENDERED: Treat adult kidney transplant recipients with high BP to a target BP of <130 mm Hg systolic and <80 mm Hg diastolic using standardized office BP measurement | kdigo-2021 | p60 | p60/practice-point/1 | practice-point |
| pediatric-map-target | children-ckd | lower 24-hour MAP by ABPM to <=50th percentile for age, sex, and height | in children with CKD, 24-hour mean arterial pressure (MAP) by ABPM should be lowered to ≤50th percentile for age, sex, and height | kdigo-2021 | p64 | p64/recommendation/5.1 | 2 |
| pediatric-hbpm-duration | children-ckd-hbpm | perform HBPM for 7 days, not less than 3 days | HBPM should be performed for 7 days (not less than 3) | kdigo-2021 | p65 | p65/narrative/hbpm-duration | narrative |
| pediatric-hbpm-rest | children-ckd-hbpm | duplicate morning and evening measurements after 5 minutes seated rest | RENDERED: with duplicate morning and evening measurements after 5 minutes of sitting at rest | kdigo-2021 | p65 | p65/narrative/hbpm-rest | narrative |
| pediatric-hbpm-repeat-interval | children-ckd-hbpm | 1 minute between duplicate measurements | 1 minute between measurements | kdigo-2021 | p65 | p65/narrative/hbpm-repeat | narrative |
| pediatric-hbpm-reading-count | children-ckd-hbpm | at least 12 readings/week | total of at least 12 readings per week | kdigo-2021 | p65 | p65/narrative/hbpm-count | narrative |
| pediatric-map-alternative-range | children-ckd | MAP target range 50th-90th percentile may also be considered | a range of MAP targets, including the 50th-90th percentile, may also be considered | kdigo-2021 | p65 | p65/narrative/map-alternative | narrative |
| pediatric-low-clinic-bp-abpm | children-ckd | consider less-frequent ABPM if clinic BP is <=25th percentile | RENDERED: individuals with clinic BP at ≤25th percentile are unlikely to have elevated ABPM. Individual practitioners may, therefore, consider less-frequent ABPM monitoring if this level of clinic BP is achieved. | kdigo-2021 | p65 | p65/narrative/low-clinic-bp | narrative |
| pediatric-abpm-height-floor | children-ckd-short | no normative ABPM data at height <120 cm | children <120 centimeters in height, for whom no normative ABPM data exist | kdigo-2021 | p65 | p65/narrative/abpm-height | narrative |
| pediatric-abpm-monitoring | children-ckd | monitor once a year with ABPM | RENDERED: We suggest monitoring BP once a year with ABPM, and monitoring every 3-6 months with standardized auscultatory office BP in children with CKD. | kdigo-2021 | p66 | p66/practice-point/1 | practice-point |
| pediatric-office-monitoring | children-ckd | monitor every 3-6 months with standardized auscultatory office BP | RENDERED: We suggest monitoring BP once a year with ABPM, and monitoring every 3-6 months with standardized auscultatory office BP in children with CKD. | kdigo-2021 | p66 | p66/practice-point/1 | practice-point |
| pediatric-office-sbp-fallback | children-high-bp-ckd-no-abpm | target achieved standardized manual auscultatory office SBP <90th percentile for age, sex, and height | RENDERED: when ABPM is not available, manual auscultatory office BP obtained in a protocol-driven standardized setting targeting achieved SBP <90th percentile for age, sex, and height of normal children is a reasonable approach. | kdigo-2021 | p66 | p66/practice-point/2 | practice-point |

## Conflicts

CONFLICT: standardized-office-sbp-target — `SBP <120 mm Hg when tolerated using standardized office measurement`; `do not apply SBP <120 mm Hg to nonstandardized measurements`; `maintain SBP <130 mm Hg, <140 mm Hg, or an even higher tolerated goal`; `reasonable control example SBP <140 mm Hg`. The latter values are explicit measurement-, tolerance-, and resource-dependent alternatives, not silent replacements for the main target.

CONFLICT: pediatric-map-target — `lower 24-hour MAP by ABPM to <=50th percentile for age, sex, and height`; `MAP target range 50th-90th percentile may also be considered`. The guideline presents the first as Recommendation 5.1 and the second as a narrative range that may be considered.

## Coverage

The source is `bound`: marker records delimit recommendation-shaped text but do not
prove a complete recommendation denominator. Every marker occurrence not discharged
by a recommendation-backed threshold row is listed below. The bound artifact contains
72 marker records under 72 distinct locators. Threshold rows cite 16 distinct exact
locators; the remaining 56 locators were read and contain no additional numeric
patient-action decision point beyond rows represented from source tables, figures,
narrative, or a duplicate summary/body occurrence.

- `p28/recommendation/1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/recommendation/1.2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/recommendation/2.1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/recommendation/2.2.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p28/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/recommendation/3.1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/recommendation/3.2.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/recommendation/3.2.2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/recommendation/3.2.3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/recommendation/3.3.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/5` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/6` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/7` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/8` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/9` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p29/practice-point/10` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p30/recommendation/1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p30/recommendation/4.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p30/recommendation/5.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p30/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p30/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p30/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p30/practice-point/4` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p31/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p32/recommendation/1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p32/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p32/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p33/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p34/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p37/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p39/recommendation/2.1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p39/recommendation/2.2.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p39/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p39/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p40/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p40/practice-point/2` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p42/recommendation/1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p50/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p56/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p57/practice-point/1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p57/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p58/recommendation/3.3.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p60/recommendation/1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p60/recommendation/3.1.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p60/recommendation/4.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p66/recommendation/5.1` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
- `p66/practice-point/3` - no additional numeric patient-action decision point beyond rows represented from the source's tables, figures, narrative, or duplicate occurrence
