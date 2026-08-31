# Cardiovascular-kidney-metabolic syndrome — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction: every row is a fact this repo restates, and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`; what that grader cannot see is written out in [README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aha-acc-2026 | AHA/ACC/ADA/ASN | AHA ACC/ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of | guideline | 2026 guideline | 2026-07-28 | https://doi.org/10.1161/CIR.0000000000001453 | stated | exact |

## Scope

**Read:** all 109 source pages, including title, abstract, contents, top messages, associated-publication and grading tables, definitions, all recommendation tables, supportive text, every clinical table and figure, evidence gaps, article information, references, and relationship appendices. Rows retain numbers that stage CKM syndrome, define a risk factor, trigger testing/referral/treatment, select or limit a drug, specify a target, or set follow-up. Prevalence, trial enrollment, effect estimates, costs, publication years, and research-only proposals were read but do not produce patient-action rows. Pages 12, 13, 31, 37, 45, 65, 70, and 71 were rendered to resolve table columns and operators.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| title, abstract, contents, and top messages | 1-4 | read 2026-08-31; blind 2026-08-31 |
| associated publications and grading methods | 5-6 | read 2026-08-31; blind 2026-08-31 |
| definitions, evaluation, diagnosis, risk, and care principles | 7-24 | yes |
| clinical management and monitoring | 25-71 | yes |
| evidence gaps and future directions | 72-74 | read 2026-08-31; blind 2026-08-31 |
| article information | 75 | read 2026-08-31; blind 2026-08-31 |
| references | 76-100 | exempt: citation list has no clinical prose |
| writing-committee and reviewer relationships | 101-109 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 4ab7f18ec7981a7b1aa6735b58f56dac0dafabbd17465bb8945c2a7ba38edb61; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| youth | youth age <18 years |
| adults | adults age >=18 years |
| adults-no-cvd | adults without CVD |
| adults-ckm-risk | adults with or at risk for CKM syndrome |
| youth-ckm-risk | youth with or at risk for CKM syndrome |
| ckm-stage-0 | adults with CKM stage 0 |
| ckm-stage-1 | adults with CKM stage 1 |
| ckm-stage-2-plus | adults with CKM stage 2 or higher |
| ckm-stage-2-4 | adults with CKM stage 2 to 4 |
| ckm-stage-1-3-obesity | people with CKM stage 1 to 3 and obesity |
| adults-overweight-obesity | adults with overweight or obesity |
| adults-stage1-bmi27 | adults with CKM stage 1 and BMI >=27 kg/m² |
| post-mbs-weight-regain | people after MBS with weight regain |
| women-gdm | women diagnosed with gestational diabetes |
| ckm2-3-t2d | adults with CKM stage 2 to 3 and T2D |
| ckm2-3-ckd | adults with CKM stage 2 to 3 and CKD |
| ckm3-pre-hf | adults with CKM stage 3 due to pre-HF |
| ckm4-obesity-ascvd | adults with CKM stage 4, overweight or obesity, and ASCVD |
| ckm4-t2d-ascvd | adults with CKM stage 4, T2D, and ASCVD |
| ckm4-obesity-hf | adults with CKM stage 4, obesity, and HF |
| ckm4-t2d-hf | adults with CKM stage 4, T2D, and HF |
| ckm4-ckd-hf | adults with CKM stage 4, CKD, and HF |
| ckm-masld | adults with CKM syndrome and MASLD |
| ckm-obesity | adults with CKM syndrome and obesity |
| planning-pregnancy-diabetes | persons with diabetes planning pregnancy |
| planning-pregnancy-ckm2-4 | persons planning pregnancy with CKM stage 2 to 4 |
| postpartum-apo | persons who experienced an adverse pregnancy outcome |
| glp1-weight-loss | patients with CKM syndrome starting GLP-1-based therapy for weight loss |
| ckm2-4-t2d-treatment | patients with CKM stage 2 to 4 and T2D after cardioprotective glucose-lowering therapy |
| ckm2-4-albuminuria | patients with CKM stage 2 to 4 and UACR >=30 mg/g starting kidney-protective therapy |
| ckm2-4-raas | patients with CKM stage 2 to 4 starting RASi or MRA |
| youth-under13 | youth age <13 years |
| youth-13-17 | youth age 13 to 17 years |
| adults-stage4b | adults with CKM stage 4b |
| adults-pre-hf | adults being assessed for pre-HF |
| masld-fibrosis-risk | adults at risk for clinically significant MASLD fibrosis |
| t2d-cvd-highrisk | adults with T2D and CVD or high CVD risk |
| stable-hf-t2d | adults with T2D and stable HF |
| adults-stage3 | adults with CKM stage 3 |
| adults-subclinical-atherosclerosis | adults with CKM stage 3 due to subclinical atherosclerosis |
| all-postpartum | all postpartum women after medical clearance |

## Quantities

| key | verbatim |
| --- | --- |
| ckm-stage-action | CKM stage-specific action or definition |
| prevent-risk-action | PREVENT risk threshold or age range |
| monitoring-interval | clinical assessment or monitoring interval |
| weight-action | weight, BMI, or weight-loss decision point |
| ckm-staging-criterion | adult CKM staging criterion |
| youth-staging-criterion | pediatric CKM staging criterion |
| therapy-eligibility | treatment eligibility or selection threshold |
| kidney-therapy-eligibility | albuminuria and eGFR treatment threshold |
| pre-hf-definition | pre-HF imaging or biomarker definition |
| pregnancy-action | pregnancy-related target or follow-up |
| fibrosis-action | MASLD fibrosis testing or referral threshold |
| drug-safety-action | drug dose, withholding, or safety threshold |
| glycemic-action | glycemic target or treatment threshold |
| bp-action | blood pressure treatment threshold or target |
| pulmonary-pressure | pulmonary artery systolic-pressure threshold |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ckm-stage-action | youth | stage youth <18 years and adults >=18 years; add UACR assessment at CKM stage >=2 | RENDERED: Among both youth (<18 y) and adults (≥18 y), CKM syndrome staging should be performed by assessing metabolic risk factors, kidney function (calculating eGFR, with additional UACR assessments in CKM stage ≥2), and CVD status to support prevention of CKM syndrome stage progression, promote regression of CKM syndrome, and personalize treatment of individuals according to their absolute CVD risk and expected net benefit of therapies. | aha-acc-2026 | p9 | p9/diagnostic-approach-to-ckm-staging/1 | 1 |
| prevent-risk-action | adults-no-cvd | use CAC when PREVENT-ASCVD is 5% to <10%, or selected 3% to <5% | PREVENT-ASCVD 5% to <10%) or select adults at borderline risk for ASCVD (PREVENT-ASCVD 3% to <5%) | aha-acc-2026 | p10 | p10/diagnostic-approach-to-ckm-staging-continued/2 | 2a |
| prevent-risk-action | adults-no-cvd | at 10-year PREVENT-HF >=5%, evaluate pre-HF with cardiac biomarkers | adults with increased predicted 10-y risk of HF (PREVENT-HF ≥5%), evaluation for pre-HF using cardiac biomarkers | aha-acc-2026 | p10 | p10/diagnostic-approach-to-ckm-staging-continued/3 | 2a |
| ckm-stage-action | adults-ckm-risk | SDOH screening applies at age >=18 years | In adults with or at risk for CKM syndrome (≥18 y), routine screening with a tool | aha-acc-2026 | p16 | p16/social-determinants-of-health-assessment/1 | 1 |
| ckm-stage-action | youth-ckm-risk | caregiver SDOH screening applies at age <18 years | In youth with or at risk for CKM syndrome (<18 y of age), routine screening of their caregivers | aha-acc-2026 | p16 | p16/social-determinants-of-health-assessment/2 | 1 |
| prevent-risk-action | adults-no-cvd | calculate 30-year risk at age 30-59 years | RENDERED: In adults 30 to 59 y of age without CVD (coronary heart disease, stroke, or HF), calculation of 30-y risk of CVD (and its components of ASCVD and HF) with the PREVENT equations can be useful to quantify risk related to CKM syndrome and to inform prevention strategies. | aha-acc-2026 | p18 | p18/quantitative-assessment-of-cvd-risk-continued/2 | 2a |
| prevent-risk-action | adults-no-cvd | calculate 10-year risk at age 30-79 years | RENDERED: In adults 30 to 79 y of age without CVD (coronary heart disease, stroke, or HF), calculation of 10-y risk of CVD (and its components of ASCVD and HF) with the PREVENT equations is recommended to quantify risk related to CKM syndrome and to inform prevention strategies. | aha-acc-2026 | p18 | p18/quantitative-assessment-of-cvd-risk/1 | 1 |
| ckm-stage-action | ckm-stage-2-4 | use interdisciplinary care at stage 2-4 with >=2 of diabetes, CKD, or CVD | RENDERED: For adults with stage 2 to 4 CKM syndrome with ≥2 CKM conditions of diabetes, CKD, and/or CVD, the use of interdisciplinary care teams with a CKM coordination point person is recommended to facilitate multisystem CKM syndrome care, including lifestyle interventions and optimization of GDMT. | aha-acc-2026 | p21 | p21/interdisciplinary-care/1 | 1 |
| weight-action | adults-overweight-obesity | target at least 5%-10% baseline weight loss | lifestyle modification is recommended as the first-line strategy to facilitate weight loss of at least 5% to 10% of baseline weight | aha-acc-2026 | p26 | p26/overarching-approach-to-obesity-management/1 | 1 |
| weight-action | adults-overweight-obesity | counsel at least annually about 5%-10% weight loss | provide counseling at least annually regarding the benefits of achieving at least 5% to 10% weight loss | aha-acc-2026 | p28 | p28/intensive-lifestyle-modification-for-weight-loss/1 | 1 |
| therapy-eligibility | adults-stage1-bmi27 | at BMI >=27 kg/m², add GLP-1-based therapy to structured lifestyle intervention | RENDERED: In adults with CKM stage 1 (ie, overweight/obesity [BMI ≥27 kg/m²] without other metabolic risk factors, CKD, or subclinical/clinical CVD), the addition of GLP-1–based therapy with proven benefit to structured lifestyle intervention can be beneficial in promoting weight loss and improving glycemia and CKM risk profiles. | aha-acc-2026 | p30 | p30/obesity-pharmacotherapy-for-weight/1 | 2a |
| therapy-eligibility | ckm-stage-1 | non-GLP-1 obesity pharmacotherapy may be used in stage 1 | In adults with CKM stage 1, non-GLP-1-based obesity pharmacotherapy may be reasonable | aha-acc-2026 | p30 | p30/obesity-pharmacotherapy-for-weight/3 | 2b |
| therapy-eligibility | ckm-stage-1-3-obesity | MBS may be used at stage 1-3 after inadequate lifestyle response | RENDERED: Among patients with CKM stage 1 to 3 and obesity without an adequate weight loss response to lifestyle modification, with or without the use of adjunctive obesity pharmacotherapies, MBS can be beneficial to facilitate weight loss and to mitigate CKM syndrome progression. | aha-acc-2026 | p31 | p31/surgical-interventions-for-weight-loss-in-ckm/1 | 2a |
| weight-action | post-mbs-weight-regain | GLP-1-based therapy may be used after regain >=25% of total lost weight | RENDERED: Among patients who have undergone MBS and have regained a significant amount of weight (≥25% or more of total lost weight), GLP-1–based therapies can be useful in promoting weight loss and management of comorbidities. | aha-acc-2026 | p32 | p32/surgical-interventions-for-weight-loss-in-ckm/3 | 2a |
| pregnancy-action | women-gdm | oral glucose tolerance test 4-12 weeks postpartum | RENDERED: In women diagnosed with GDM, an oral glucose tolerance test 4 to 12 wk postpartum is recommended for prediabetes and diabetes screening and to identify increased risk for development of T2D and for CKM stage progression. | aha-acc-2026 | p33 | p33/management-after-gestational-diabetes/1 | 1 |
| ckm-stage-action | ckm2-3-t2d | lifestyle and targeted multifactorial therapy at CKM stage 2-3 with T2D | adults with CKM syndrome stage 2 to 3 with T2D, lifestyle modification | aha-acc-2026 | p34 | p34/t2d-in-ckm-syndrome-stage-2-to-3/1 | 1 |
| ckm-stage-action | ckm2-3-t2d | intensified multifactorial therapy at CKM stage 2-3 with T2D | adults with CKM syndrome stage 2 to 3 with T2D, intensified multifactorial interventions | aha-acc-2026 | p34 | p34/t2d-in-ckm-syndrome-stage-2-to-3/2 | 1 |
| therapy-eligibility | ckm2-3-t2d | PREVENT-CVD >=7.5%: include SGLT2 inhibitor or GLP-1-based therapy | RENDERED: In adults with CKM syndrome stage 2 to 3 with T2D and increased risk for CVD (10-y PREVENT-CVD ≥7.5%), the treatment plan should include a sodium–glucose cotransporter-2 inhibitor (SGLT2i) or a GLP-1–based therapy with demonstrated benefit to reduce cardiovascular events and mortality. | aha-acc-2026 | p34 | p34/t2d-in-ckm-syndrome-stage-2-to-3/3 | 1 |
| glycemic-action | ckm2-3-t2d | A1C 0.5%-1% above individualized goal: combine metformin with cardioprotective therapy | A1C levels 0.5% to 1% above their individualized glycemic goal, metformin therapy can be effective when combined | aha-acc-2026 | p34 | p34/t2d-in-ckm-syndrome-stage-2-to-3/6 | 2a |
| ckm-stage-action | ckm2-3-t2d | combination GLP-1-based therapy and SGLT2 inhibitor may be considered at stage 2-3 | RENDERED: In adults with CKM syndrome stage 2 to 3 with T2D and increased risk for CVD or multiple CKM risk factors, or both, combination therapy with a GLP-1–based therapy with proven benefit and an SGLT2 inhibitor may be considered for reducing the risk of cardiovascular events beyond that conferred by a single cardioprotective antihyperglycemic agent. | aha-acc-2026 | p34 | p34/t2d-in-ckm-syndrome-stage-2-to-3/7 | 2b |
| kidney-therapy-eligibility | ckm2-3-ckd | RASi at maximum tolerated dose when T2D or UACR >=30 mg/g and eGFR >=30 mL/min/1.73 m² | RENDERED: In adults with CKM syndrome stage 2 to 3 who have CKD and T2D, or CKD without T2D but with UACR ≥30 mg/g, and with eGFR ≥30 mL/min/1.73 m², use of a RASi (eg, ACEi or ARB) at the maximum tolerated dose is recommended to reduce the loss of kidney function and to lower the risk of CVD. | aha-acc-2026 | p39 | p39/management-of-ckd-in-ckm-syndrome-stage/1 | 1 |
| kidney-therapy-eligibility | ckm2-3-ckd | SGLT2 inhibitor when T2D or UACR >=200 mg/g and eGFR >=20 mL/min/1.73 m² | RENDERED: In adults with CKM syndrome stage 2 to 3 who have CKD and T2D, or CKD without T2D but with UACR ≥200 mg/g, and with eGFR ≥20 mL/min/1.73 m², use of an SGLT2 inhibitor is recommended to reduce the loss of kidney function and to lower the risks of HF hospitalization and CVD mortality. | aha-acc-2026 | p39 | p39/management-of-ckd-in-ckm-syndrome-stage/2 | 1 |
| kidney-therapy-eligibility | ckm2-3-ckd | without T2D and UACR 30-199 mg/g, consider SGLT2 inhibitor | CKD without T2D but with UACR ≥30 to 199 mg/g, SGLT2i can be considered | aha-acc-2026 | p39 | p39/management-of-ckd-in-ckm-syndrome-stage/3 | 2a |
| kidney-therapy-eligibility | ckm2-3-ckd | with T2D, UACR >=30 mg/g, and eGFR >=25 mL/min/1.73 m² despite ACEi/ARB and SGLT2 inhibitor, add nsMRA | RENDERED: In adults with CKM syndrome stage 2 to 3 who have CKD, T2D, and UACR ≥30 mg/g despite ACEi/ARB and SGLT2 inhibitor as tolerated, with eGFR ≥25 mL/min/1.73 m², the addition of a nonsteroidal mineralocorticoid receptor antagonist (nsMRA) with proven kidney and cardiovascular benefit is recommended to reduce the risks of losing kidney function and kidney failure, and to lower the risk of CVD. | aha-acc-2026 | p39 | p39/management-of-ckd-in-ckm-syndrome-stage/5 | 1 |
| kidney-therapy-eligibility | ckm2-3-ckd | with T2D and UACR >=100 mg/g despite ACEi/ARB and SGLT2 inhibitor, add GLP-1-based therapy | UACR ≥100 mg/g despite ACEi/ARB and SGLT2i as tolerated, treatment with GLP-1-based therapy | aha-acc-2026 | p39 | p39/management-of-ckd-in-ckm-syndrome-stage/7 | 1 |
| ckm-stage-action | ckm3-pre-hf | intensive lifestyle and risk-factor control at CKM stage 3 due to pre-HF | adults with CKM stage 3 due to pre-HF, intensive lifestyle interventions and intensive risk factor control | aha-acc-2026 | p44 | p44/pre-heart-failure/1 | 1 |
| ckm-stage-action | ckm3-pre-hf | at stage 3 due to pre-HF with T2D or CKD, use SGLT2 inhibitor first line | CKM stage 3 due to pre-HF with T2D or CKD, the use of SGLT2i is recommended as first-line therapy | aha-acc-2026 | p44 | p44/pre-heart-failure/2 | 1 |
| kidney-therapy-eligibility | ckm3-pre-hf | diabetes, CKD, UACR >=100 mg/g: add GLP-1-based therapy to SGLT2 inhibitor | RENDERED: In adults with CKM stage 3 due to pre-HF with diabetes, CKD, and UACR ≥100 mg/g, the addition of GLP-1–based therapy with proven benefit to SGLT2 inhibitor therapy is reasonable for the prevention of HF. | aha-acc-2026 | p44 | p44/pre-heart-failure/3 | 2a |
| kidney-therapy-eligibility | ckm3-pre-hf | diabetes, CKD, UACR >=30 mg/g: add nsMRA to SGLT2 inhibitor | RENDERED: In adults with CKM stage 3 due to pre-HF with diabetes, CKD, and UACR ≥30 mg/g, the addition of nsMRA to SGLT2 inhibitor therapy is reasonable for the prevention of HF. | aha-acc-2026 | p44 | p44/pre-heart-failure/4 | 2a |
| therapy-eligibility | ckm4-obesity-ascvd | stage 4: intensive multicomponent lifestyle intervention | RENDERED: In adults with CKM syndrome stage 4 with overweight or obesity and ASCVD, treatment with an intensive, multicomponent, behavioral lifestyle intervention is recommended to promote weight loss and improvement in CKM risk factors. | aha-acc-2026 | p47 | p47/ckm-syndrome-stage-4-with-obesity-and/1 | 1 |
| therapy-eligibility | ckm4-obesity-ascvd | BMI >=27 kg/m²: GLP-1-based therapy | RENDERED: In adults with CKM syndrome stage 4 with overweight or obesity (BMI ≥27 kg/m²) and ASCVD, treatment with a GLP-1–based therapy with proven cardiovascular benefit in addition to counseling to promote healthy dietary intake and regular physical activity is recommended to reduce the risk of cardiovascular events. | aha-acc-2026 | p47 | p47/ckm-syndrome-stage-4-with-obesity-and/2 | 1 |
| weight-action | ckm4-obesity-ascvd | BMI >=30 kg/m² and failed lifestyle goals: MBS for minimum 5%-10% loss | RENDERED: In adults with CKM syndrome stage 4 with obesity (BMI ≥30 kg/m²) and ASCVD who have not reached weight loss goals with lifestyle interventions, with or without maximally tolerated pharmacotherapy, MBS can be beneficial to facilitate a minimum weight loss of 5% to 10% to improve CKM health and to reduce the risk of cardiovascular events. | aha-acc-2026 | p47 | p47/ckm-syndrome-stage-4-with-obesity-and/4 | 2a |
| drug-safety-action | ckm4-obesity-ascvd | BMI >=27 kg/m²: naltrexone/bupropion or phentermine-containing agents potentially harmful | RENDERED: In adults with CKM syndrome stage 4 with overweight or obesity (BMI ≥27 kg/m²) and ASCVD, treatment with naltrexone/bupropion or phentermine-containing agents is potentially harmful as they can increase BP and heart rate. | aha-acc-2026 | p47 | p47/ckm-syndrome-stage-4-with-obesity-and/5 | 3 |
| ckm-stage-action | ckm4-t2d-ascvd | tailored lifestyle plan at CKM stage 4 | adults with CKM syndrome stage 4 with T2D and ASCVD, a tailored lifestyle modification plan | aha-acc-2026 | p51 | p51/ckm-syndrome-stage-4-with-t2d-and-ascvd/1 | 1 |
| ckm-stage-action | ckm4-t2d-ascvd | SGLT2 inhibitor or GLP-1-based therapy at CKM stage 4 | adults with CKM syndrome stage 4 with T2D and ASCVD, the use of either an SGLT2i or a GLP-1-based therapy | aha-acc-2026 | p51 | p51/ckm-syndrome-stage-4-with-t2d-and-ascvd/2 | 1 |
| ckm-stage-action | ckm4-t2d-ascvd | combined SGLT2 inhibitor and GLP-1-based therapy may be beneficial | adults with CKM syndrome stage 4 with T2D and ASCVD, the use of a combination of SGLT2i and a GLP-1-based therapy | aha-acc-2026 | p51 | p51/ckm-syndrome-stage-4-with-t2d-and-ascvd/5 | 2a |
| ckm-stage-action | ckm4-obesity-hf | symptomatic HFpEF: GLP-1-based therapy | CKM syndrome stage 4, obesity, and symptomatic HFpEF, a GLP-1-based therapy | aha-acc-2026 | p55 | p55/ckm-syndrome-stage-4-with-obesity-and-hf/1 | 1 |
| ckm-stage-action | ckm4-obesity-hf | HFpEF: exercise plus caloric-deficit diet | RENDERED: Among adults with CKM syndrome stage 4, obesity, and HFpEF, a combination of exercise training and a caloric deficit diet can be beneficial for improving functional capacity. | aha-acc-2026 | p55 | p55/ckm-syndrome-stage-4-with-obesity-and-hf/3 | 2a |
| ckm-stage-action | ckm4-obesity-hf | symptomatic HFrEF: obesity treatment may be considered | CKM syndrome stage 4, obesity, and symptomatic HFrEF, treatment of obesity may be considered | aha-acc-2026 | p55 | p55/ckm-syndrome-stage-4-with-obesity-and-hf/4 | 2b |
| ckm-stage-action | ckm4-t2d-hf | prioritize SGLT2 inhibitor first line | CKM syndrome stage 4 with T2D and HF, SGLT2i should be prioritized as the first-line | aha-acc-2026 | p56 | p56/ckm-syndrome-stage-4-with-t2d-and-hf/1 | 1 |
| ckm-stage-action | ckm4-t2d-hf | HFpEF: add GLP-1-based therapy to SGLT2 inhibitor | CKM syndrome stage 4 with T2D, HFpEF, and other CKM risk factors, the addition of GLP-1-based therapy | aha-acc-2026 | p57 | p57/ckm-syndrome-stage-4-with-t2d-and-hf/4 | 2a |
| kidney-therapy-eligibility | ckm4-t2d-hf | stable HF, eGFR >=30 mL/min/1.73 m², A1C above goal: add metformin | RENDERED: In patients with CKM syndrome stage 4 with T2D, stable HF, eGFR ≥30 mL/min/1.73 m², and A1C levels above their individualized glycemic goal, the addition of metformin therapy to SGLT2 inhibitor therapy can be beneficial to help achieve glycemic targets. | aha-acc-2026 | p57 | p57/ckm-syndrome-stage-4-with-t2d-and-hf/5 | 2a |
| kidney-therapy-eligibility | ckm4-ckd-hf | eGFR >=30 mL/min/1.73 m² with HFrEF: start ARNI or other RASi | RENDERED: In adults with CKM syndrome stage 4 with CKD, eGFR ≥30 mL/min/1.73 m², and HFrEF, the initiation of an ARNI, or other RASi if an ARNI cannot be initiated, is recommended to reduce the risk of cardiovascular death or HF hospitalization and loss of kidney function. | aha-acc-2026 | p59 | p59/ckm-syndrome-stage-4-with-ckd-and-hf/1 | 1 |
| kidney-therapy-eligibility | ckm4-ckd-hf | eGFR >=20 mL/min/1.73 m² with any EF: start SGLT2 inhibitor | RENDERED: In adults with CKM syndrome stage 4 with CKD and HF with any ejection fraction, who have eGFR ≥20 mL/min/1.73 m², initiation of an SGLT2 inhibitor is recommended to reduce cardiovascular mortality, HF hospitalization, and possibly loss of kidney function. | aha-acc-2026 | p59 | p59/ckm-syndrome-stage-4-with-ckd-and-hf/3 | 1 |
| kidney-therapy-eligibility | ckm4-ckd-hf | T2D, UACR >=30 mg/g, LVEF >40%, eGFR >=25 mL/min/1.73 m²: start nsMRA | RENDERED: In adults with CKM syndrome stage 4 with CKD, T2D, UACR ≥30 mg/g, and HF with LVEF >40% (HFmrEF and HFpEF), who have eGFR ≥25 mL/min/1.73 m², initiation of a nonsteroidal MRA is reasonable to reduce risk of HF hospitalization and loss of kidney function. | aha-acc-2026 | p59 | p59/ckm-syndrome-stage-4-with-ckd-and-hf/6 | 2a |
| kidney-therapy-eligibility | ckm4-ckd-hf | HFrEF and eGFR >30 mL/min/1.73 m²: potassium binder may enable RAAS inhibition | RENDERED: In adults with CKM syndrome stage 4 with CKD and HFrEF, who have eGFR >30 mL/min/1.73 m², use of novel oral potassium-binding agents may be reasonable to reduce risk of hyperkalemia and allow use of RAAS inhibition. | aha-acc-2026 | p59 | p59/ckm-syndrome-stage-4-with-ckd-and-hf/8 | 2b |
| monitoring-interval | ckm-masld | diabetes or >=2 cardiometabolic risks: FIB-4 every 1-2 years | diabetes or ≥2 cardiometabolic risk factors, calculation of the Fibrosis-4 (FIB-4) index is recommended every 1 to 2 y | aha-acc-2026 | p64 | p64/metabolic-dysfunction-associated-steatotic/1 | 1 |
| monitoring-interval | ckm-stage-1 | prediabetes: FIB-4 every 2-3 years | RENDERED: Among adults with CKM stage 1 due to prediabetes, it is reasonable to calculate the FIB-4 index every 2 to 3 y to assess risk for liver fibrosis related to MASLD. | aha-acc-2026 | p64 | p64/metabolic-dysfunction-associated-steatotic/2 | 2a |
| monitoring-interval | ckm-obesity | assess OSA symptoms annually | adults with CKM syndrome and obesity, annual assessments for symptoms of sleep apnea | aha-acc-2026 | p66 | p66/obstructive-sleep-apnea/1 | 2a |
| pregnancy-action | planning-pregnancy-diabetes | target HbA1c <6.5% | optimizing glucose control (with a target HbA1c <6.5%) | aha-acc-2026 | p68 | p68/pregnancy-and-ckm-health-continued/2 | 1 |
| pregnancy-action | planning-pregnancy-ckm2-4 | interdisciplinary care at CKM stage 2-4 | RENDERED: Persons planning pregnancy who have CKM syndrome stage 2 to 4 should receive care from an interdisciplinary care team to reduce the risk of adverse pregnancy outcomes and optimize postpartum CKM health. | aha-acc-2026 | p68 | p68/pregnancy-and-ckm-health-continued/3 | 1 |
| pregnancy-action | postpartum-apo | screen at least once within first postpartum year | RENDERED: Among persons who have experienced an adverse pregnancy outcome, screening for CKM risk factors (BP, lipids, glycemia, CKD, BMI, and waist circumference), at least once within the first postpartum year, and lifestyle counseling are recommended to guide optimization of CKM health. | aha-acc-2026 | p68 | p68/pregnancy-and-ckm-health-continued/4 | 1 |
| weight-action | glp1-weight-loss | reassess within 3-6 months; <5% loss triggers escalation, switch, or referral | reassessed periodically (within 3 to 6 mo), and insufficient weight loss (<5%) should be addressed | aha-acc-2026 | p69 | p69/monitoring-and-follow-up-after-initiation-of/1 | 1 |
| monitoring-interval | ckm2-4-t2d-treatment | assess glycemia every 3-6 months, more often if not at goal | RENDERED: In patients with stage 2 to 4 CKM syndrome and T2D who have initiated a cardioprotective glucose-lowering agent (SGLT2 inhibitor or GLP-1–based therapy), glycemic status should be assessed by A1C, blood glucose monitoring, and/or continuous glucose monitoring metrics every 3 to 6 mo and more frequently in individuals not meeting glycemic goals to guide further glycemic management. | aha-acc-2026 | p69 | p69/monitoring-and-follow-up-after-initiation-of/2 | 1 |
| monitoring-interval | ckm2-4-albuminuria | repeat UACR after 3-6 months | RENDERED: For patients with CKM stage 2 to 4 and albuminuria (UACR ≥30 mg/g) who initiate kidney-protective therapies, it is reasonable to remeasure albuminuria after 3 to 6 mo to assess residual CKM risk and indications for additional kidney-protective therapies to prevent CVD events and loss of kidney function. | aha-acc-2026 | p70 | p70/monitoring-and-follow-up-after-initiation-of/3 | 2a |
| monitoring-interval | ckm2-4-raas | recalculate eGFR and measure potassium after 2-4 weeks | recalculate eGFR and measure potassium after 2 to 4 wk | aha-acc-2026 | p70 | p70/monitoring-and-follow-up-after-initiation-of/4 | 2a |

| ckm-staging-criterion | ckm-stage-1 | BMI >=25 kg/m², or >=23 kg/m² with Asian ancestry | RENDERED: BMI ≥25 kg/m² (or ≥23 kg/m² if Asian ancestry) | aha-acc-2026 | p12 | p12/narrative/stage1-bmi | narrative |
| ckm-staging-criterion | ckm-stage-1 | waist >=88 cm women or >=102 cm men; Asian ancestry >=80/90 cm women/men | RENDERED: waist circumference ≥88/102 cm in women/men (or if Asian ancestry ≥80/90 cm in women/men) | aha-acc-2026 | p12 | p12/narrative/stage1-waist | narrative |
| ckm-staging-criterion | ckm-stage-1 | fasting glucose 100-125 mg/dL or HbA1c 5.7%-6.4% | RENDERED: Fasting blood glucose ≥100 to 125 mg/dL or HbA1c between 5.7% and 6.4% | aha-acc-2026 | p12 | p12/narrative/stage1-glycemia | narrative |
| ckm-staging-criterion | ckm-stage-2-plus | hypertension: SBP >=130, DBP >=80 mm Hg, or antihypertensive use | RENDERED: hypertension (SBP ≥130 mm Hg, DBP ≥80 mm Hg or use of antihypertensive medications) | aha-acc-2026 | p12 | p12/narrative/stage2-bp | narrative |
| ckm-staging-criterion | ckm-stage-2-plus | triglycerides >=150 mg/dL | RENDERED: hypertriglyceridemia (≥150 mg/dL) | aha-acc-2026 | p12 | p12/narrative/stage2-triglycerides | narrative |
| ckm-staging-criterion | ckm-stage-2-plus | T2D: fasting glucose >=126 mg/dL or HbA1c >=6.5% | RENDERED: T2D (fasting blood glucose ≥126 mg/dL or HbA1c ≥6.5%) | aha-acc-2026 | p12 | p12/narrative/stage2-t2d | narrative |
| ckm-staging-criterion | adults-stage3 | CAC >=100 | RENDERED: CAC with Agatston score ≥100 | aha-acc-2026 | p12 | p12/narrative/stage3-cac | narrative |
| ckm-staging-criterion | adults-stage3 | NT-proBNP >=125 pg/mL | RENDERED: NT-proBNP ≥125 pg/mL | aha-acc-2026 | p12 | p12/narrative/stage3-ntprobnp | narrative |
| ckm-staging-criterion | adults-stage3 | hs-cTnT >=14 ng/L women or >=22 ng/L men; hs-cTnI >=10 women or >=12 men | RENDERED: hs-cTnT ≥14 ng/L for women and ≥22 ng/L for men, hs-cTnI ≥10 ng/L for women, and ≥12 ng/L for men | aha-acc-2026 | p12 | p12/narrative/stage3-troponin | narrative |
| ckm-staging-criterion | adults-stage3 | PREVENT-CVD 10-year risk >=20% | RENDERED: Predicted 10-y CVD risk ≥20% using PREVENT-CVD | aha-acc-2026 | p12 | p12/narrative/stage3-prevent | narrative |
| ckm-staging-criterion | adults-stage4b | kidney failure: eGFR <15 mL/min/1.73 m² or chronic kidney replacement therapy | RENDERED: Stage 4b: kidney failure present (eGFR <15 mL/min/1.73m² or need for chronic kidney replacement therapy) | aha-acc-2026 | p12 | p12/narrative/stage4b | narrative |
| youth-staging-criterion | youth | overweight BMI >=85th to <95th percentile; Class 1 obesity >=95th percentile to <120% of 95th; Class 2 obesity >=120% to <140% of 95th or BMI >=35 to <40 kg/m², whichever is lower; Class 3 obesity >=140% of 95th or BMI >=40 kg/m², whichever is lower | RENDERED: Overweight: BMI ≥85th to <95th percentile; Class 1 Obesity: BMI ≥95th percentile to <120% of the 95th percentile; Class 2 Obesity: BMI ≥120% to <140% of the 95th percentile or BMI ≥35 to <40 kg/m², whichever is lower; Class 3 Obesity: BMI ≥140% of the 95th percentile or BMI ≥40 kg/m², whichever is lower | aha-acc-2026 | p13 | p13/narrative/youth-weight | narrative |
| youth-staging-criterion | youth-under13 | normal <90th; elevated >=90th to <95th or 120/80 to <95th, whichever is lower; stage 1 >=95th to <95th+12 or 130/80-139/89, whichever is lower; stage 2 >=95th+12 or >=140/90, whichever is lower | RENDERED: Age <13 y: Normal BP <90th percentile; Elevated BP ≥90th to <95th percentile or 120/80 mm Hg to <95th percentile, whichever is lower; Stage 1 Hypertension ≥95th percentile to <95th percentile + 12 mm Hg, or 130/80 to 139/89 mm Hg, whichever is lower; Stage 2 Hypertension ≥95th percentile + 12 mm Hg, or ≥140/90 mm Hg, whichever is lower | aha-acc-2026 | p13 | p13/narrative/youth-bp-under13 | narrative |
| youth-staging-criterion | youth-13-17 | normal <120/<80; elevated 120/<80 to 129/<80; stage 1 130/80-139/89; stage 2 >=140/90 mm Hg | RENDERED: Age 13 to 17 y: Normal BP <120/<80 mm Hg; Elevated BP 120/<80 to 129/<80 mm Hg; Stage 1 Hypertension 130/80 to 139/89 mm Hg; Stage 2 Hypertension ≥140/90 mm Hg | aha-acc-2026 | p13 | p13/narrative/youth-bp-13plus | narrative |
| youth-staging-criterion | youth | total cholesterol >=200, HDL-C <40, LDL-C >=130, non-HDL-C >=145 mg/dL | RENDERED: Total cholesterol ≥200 mg/dL; HDL-C <40 mg/dL; LDL-C ≥130 mg/dL; Non-HDL-C ≥145 mg/dL | aha-acc-2026 | p13 | p13/narrative/youth-lipids | narrative |
| youth-staging-criterion | youth | triglycerides >=100 mg/dL age 0-9; >=130 mg/dL age 10-19 | RENDERED: Triglycerides 0–9 y: ≥100 mg/dL; 10–19 y: ≥130 mg/dL | aha-acc-2026 | p13 | p13/narrative/youth-triglycerides | narrative |
| monitoring-interval | adults-ckm-risk | BMI and waist at least annually | recommended to measure BMI and waist circumference at least annually | aha-acc-2026 | p14 | p14/narrative/annual-anthropometrics | narrative |
| monitoring-interval | ckm-stage-0 | lipids, glycemia, eGFR every 5 years; BP annually | RENDERED: assess lipids, glycemia, and kidney function at least every 5 y and BP at least annually | aha-acc-2026 | p14 | p14/narrative/stage0-monitoring | narrative |
| monitoring-interval | ckm-stage-1 | lipids, glycemia, eGFR every 2-3 years; BP annually | RENDERED: assess lipids, glycemia, and kidney function at least every 2 to 3 y and BP at least annually | aha-acc-2026 | p14 | p14/narrative/stage1-monitoring | narrative |
| monitoring-interval | ckm-stage-2-plus | lipids, glycemia, BP, eGFR, and UACR at least annually | RENDERED: CKM stages 2 and above: assess lipids, glycemia, and BP at least annually; assess both eGFR and UACR at least annually | aha-acc-2026 | p14 | p14/narrative/stage2-monitoring | narrative |
| bp-action | adults-ckm-risk | goal <130/80 mm Hg for most | BP should ideally be checked at every visit, with a goal of <130/80 mm Hg for most individuals. | aha-acc-2026 | p14 | p14/narrative/bp-goal | narrative |
| drug-safety-action | adults-stage1-bmi27 | tirzepatide 15 mg; semaglutide 2.4 mg; liraglutide 3 mg | RENDERED: Tirzepatide 15 mg; Semaglutide 2.4 mg; Liraglutide 3 mg | aha-acc-2026 | p31 | p31/narrative/glp1-obesity-doses | narrative |
| drug-safety-action | adults-stage1-bmi27 | phentermine/topiramate 15/92 mg; naltrexone/bupropion 32/360 mg; orlistat 120 mg; phentermine 15-37.5 mg | RENDERED: Phentermine/topiramate 15 mg/92 mg; Naltrexone/bupropion 32 mg/360 mg; Orlistat 120 mg; Phentermine 15–37.5 mg | aha-acc-2026 | p31 | p31/narrative/non-glp1-doses | narrative |
| drug-safety-action | adults-stage1-bmi27 | limit phentermine/topiramate and naltrexone/bupropion when GFR <50 | RENDERED: Limit dose with GFR <50 | aha-acc-2026 | p31 | p31/narrative/gfr50-dose-limit | narrative |
| drug-safety-action | ckm2-3-t2d | stop SGLT2 inhibitor 3-4 days before scheduled surgery | RENDERED: discontinue the SGLT2 inhibitor before scheduled surgery (eg, 3–4 d) | aha-acc-2026 | p37 | p37/narrative/sglt2-surgery | narrative |
| drug-safety-action | ckm2-3-t2d | add nonoral or barrier contraception for 4 weeks after initiation and each dose escalation | RENDERED: add a barrier method of contraception for 4 weeks after initiation and for 4 weeks after each dose escalation | aha-acc-2026 | p37 | p37/narrative/glp1-contraception | narrative |
| pre-hf-definition | adults-pre-hf | LAVI >=29 mL/m²; LVMI >116 g/m² men or >95 women; RWT >0.42; wall >=12 mm; LVEF <50%; GLS <16% | RENDERED: LAVI ≥29 mL/m²; LVMI >116 g/m² in men; >95 g/m² in women; RWT >0.42; LV wall thickness ≥12 mm; LVEF <50%; GLS <16% | aha-acc-2026 | p45 | p45/narrative/pre-hf-structure | narrative |
| pre-hf-definition | adults-pre-hf | septal e' <7 cm/s; TR >2.8 m/s; average E/e' >=15 | RENDERED: Septal e′ <7 cm/s; TR velocity >2.8 m/s; Average E/e′ ≥15 | aha-acc-2026 | p45 | p45/narrative/pre-hf-filling | narrative |
| pulmonary-pressure | adults-pre-hf | estimated PA systolic pressure >35 mm Hg | RENDERED: Estimated PA systolic pressure >35 mm Hg | aha-acc-2026 | p45 | p45/narrative/pre-hf-pa-pressure | narrative |
| pre-hf-definition | adults-pre-hf | BNP >=35 pg/mL or NT-proBNP >=125 pg/mL | RENDERED: BNP ≥35 pg/mL; NT-proBNP ≥125 pg/mL | aha-acc-2026 | p45 | p45/narrative/pre-hf-biomarkers | narrative |
| glycemic-action | stable-hf-t2d | HbA1c 7%-8%; metformin normal dose eGFR >=60, 1000-1500 mg/day at 45-59, <=1000 mg/day at 30-44, contraindicated <30 | RENDERED: Maintenance of HbA1c between 7% and 8%; eGFR ≥60 mL/min/1.73 m², normal dose; eGFR 45 to 59 mL/min/1.73 m², 1000 to 1500 mg per day; eGFR 30 to 44 mL/min/1.73 m², ≤1000 mg per day; eGFR <30 mL/min/1.73 m², contraindicated | aha-acc-2026 | p59 | p59/narrative/metformin-hf-dosing | narrative |
| kidney-therapy-eligibility | ckm2-3-ckd | initiation floors: RASi >=30, SGLT2 inhibitor >=20, finerenone >=25 mL/min/1.73 m² | RENDERED: The drug-specific eGFR initiation thresholds for these therapies are RASi ≥30 mL/min/1.73 m², SGLT2i ≥20 mL/min/1.73 m², and finerenone ≥25 mL/min/1.73 m² | aha-acc-2026 | p63 | p63/narrative/initiation-floors | narrative |
| prevent-risk-action | ckm-stage-2-plus | statin support: age >=40 with T2D/CKD or PREVENT-ASCVD 5%-9.9%; consider at 3%-4.9% | RENDERED: adults ≥40 years with T2D or CKD, or with intermediate predicted ASCVD risk (PREVENT-ASCVD 5% to 9.9%), support the use of statins; borderline predicted ASCVD risk (PREVENT-ASCVD 3% to 4.9%) supports consideration | aha-acc-2026 | p63 | p63/narrative/statin-risk | narrative |
| therapy-eligibility | adults-subclinical-atherosclerosis | CAC 100-999: LDL-C <70 mg/dL; CAC >=1000: LDL-C <55 mg/dL | RENDERED: CAC scores of 100 to 999 Agatston units: LDL-C goal <70 mg/dL; CAC score ≥1000 Agatston units: LDL-C goal <55 mg/dL | aha-acc-2026 | p64 | p64/narrative/cac-ldl-goals | narrative |
| fibrosis-action | masld-fibrosis-risk | age 35-64: FIB-4 <1.3 routine, 1.3-2.67 VCTE/ELF, >2.67 hepatology; age >=65: <2.0 routine, 2.0-2.67 VCTE/ELF, >2.67 hepatology | RENDERED: FIB-4, age 35–64: <1.3 Routine monitoring; 1.3–2.67 Refer for VCTE or ELF; >2.67 Refer to hepatology; FIB-4, age ≥65: <2.0 Routine monitoring; 2.0–2.67 Refer for VCTE or ELF; >2.67 Refer to hepatology | aha-acc-2026 | p65 | p65/narrative/fib4-referral | narrative |
| fibrosis-action | masld-fibrosis-risk | VCTE <8 low, 8-12 intermediate referral, >12 high; ELF <7.7 low, 7.7-9.8 intermediate referral, >9.8 high | RENDERED: VCTE <8 Low; 8–12 Intermediate Referral to GI/hepatology; >12 High; ELF <7.7 Low; 7.7–9.8 Intermediate Referral to GI/hepatology; >9.8 High | aha-acc-2026 | p65 | p65/narrative/secondary-fibrosis | narrative |
| fibrosis-action | masld-fibrosis-risk | fast >=3 hours before VCTE; do not use if BMI >=40 kg/m² | RENDERED: The individual must fast for ≥3 hours ... not recommended if BMI ≥40 kg/m² | aha-acc-2026 | p65 | p65/narrative/vcte-preparation | narrative |
| pregnancy-action | all-postpartum | after medical clearance, >=150 minutes/week moderate activity | RENDERED: after medical clearance, all postpartum women are encouraged to participate in ≥150 minutes/week of moderate-intensity activity | aha-acc-2026 | p69 | p69/narrative/postpartum-activity | narrative |
| drug-safety-action | glp1-weight-loss | wait >=2-3 hours after eating before lying down; extend dose phase 2-4 weeks for GI effects | RENDERED: Wait ≥2 to 3 h after eating a meal before lying down ... Extend current phase for 2 to 4 more wk before moving forward to next dose. | aha-acc-2026 | p70 | p70/narrative/glp1-gi-management | narrative |
| glycemic-action | t2d-cvd-highrisk | HbA1c 7%-8.5% add metformin; >8.5% add semaglutide/tirzepatide; >10.0% or glucose >=300 mg/dL refer endocrinology | RENDERED: HbA1c 7% to 8.5%: metformin can be added; HbA1c >8.5%: add semaglutide or tirzepatide; HbA1c >10.0% or blood glucose ≥300 mg/dL: referral to an endocrinologist | aha-acc-2026 | p71 | p71/narrative/glycemic-escalation | narrative |
| drug-safety-action | ckm2-4-raas | eGFR fall <=30% expected; >30% evaluate and consider medication changes; potassium <=5.5 mEq/L may be tolerated, >5.5 requires mitigation or dose change | RENDERED: Decreases in eGFR up to 30% ... expected and acceptable. When eGFR decreases >30% ... medication adjustments should be considered ... potassium (≤5.5 mEq/L) may be tolerated ... (>5.5 mEq/L) may require medications ... dietary changes, or dose reduction or discontinuation | aha-acc-2026 | p71 | p71/narrative/raas-safety | narrative |
| ckm-staging-criterion | ckm-stage-2-plus | metabolic syndrome is >=3 of waist, HDL-C, triglyceride, BP, and glucose criteria | RENDERED: MetS is defined by the presence of 3 or more of the following | aha-acc-2026 | p12 | p12/narrative/mets-count | narrative |
| ckm-staging-criterion | ckm-stage-2-plus | metabolic syndrome HDL-C <40 mg/dL men or <50 mg/dL women | RENDERED: HDL-C <40 mg/dL in men or <50 mg/dL in women | aha-acc-2026 | p12 | p12/narrative/mets-hdl | narrative |
| ckm-staging-criterion | ckm-stage-2-plus | moderate-high CKD: G1-G2 A2-A3, G3a A1-A2, or G3b A1; very high: G3a A3, G3b A2-A3, or G4-G5 | RENDERED: moderate-high-risk CKD: stages G1–G2 with A2–A3, stage G3a with A1–A2, or stage G3b with A1; very high-risk CKD: stages G3a with A3, stage G3b with A2–A3, or stages G4–G5 CKD | aha-acc-2026 | p12 | p12/narrative/ckd-risk-staging | narrative |
| ckm-staging-criterion | ckm-stage-2-plus | A1 UACR <30 mg/g; A2 30 to <300; A3 >=300 mg/g | RENDERED: A1 albuminuria is UACR <30 mg/g; A2 albuminuria is UACR 30 to <300 mg/g; A3 albuminuria is UACR ≥300 mg/g | aha-acc-2026 | p12 | p12/narrative/uacr-categories | narrative |
| youth-staging-criterion | youth | prediabetes: fasting glucose 100-125, HbA1c 5.7%-6.4%, or 2-hour 75-g glucose 140-199 mg/dL | RENDERED: Prediabetes ... Fasting plasma glucose 100–125 mg/dL ... HbA1c 5.7%–6.4% ... 2-h plasma glucose during 75-g oral glucose tolerance test 140–199 mg/dL | aha-acc-2026 | p13 | p13/narrative/youth-prediabetes | narrative |
| youth-staging-criterion | youth | diabetes: fasting glucose >=126, HbA1c >=6.5%, 2-hour 75-g glucose >=200, or symptomatic random glucose >=200 mg/dL | RENDERED: Diabetes ... Fasting plasma glucose ≥126 mg/dL ... HbA1c ≥6.5% ... 2-h plasma glucose during 75-g oral glucose tolerance test ≥200 mg/dL ... Random plasma glucose ≥200 mg/dL | aha-acc-2026 | p13 | p13/narrative/youth-diabetes | narrative |
| weight-action | adults-overweight-obesity | caloric deficit 500-750 kcal/day, >=150 minutes/week activity, and >=14 months behavioral therapy | RENDERED: dietary changes to promote a calorie deficit of 500 to 750 kcal/day; ≥150 minutes per week of moderately vigorous aerobic activity; and ≥14 months of behavioral therapy | aha-acc-2026 | p28 | p28/narrative/intensive-lifestyle-components | narrative |
| therapy-eligibility | ckm2-3-t2d | hypertriglyceridemia fasting >=150 or nonfasting >=175 mg/dL; severe >=500 mg/dL adds pancreatitis-prevention measures | RENDERED: Hypertriglyceridemia is fasting triglycerides ≥150 mg/dL or nonfasting triglycerides ≥175 mg/dL; severe hypertriglyceridemia ≥500 mg/dL adds pancreatitis-prevention measures | aha-acc-2026 | p38 | p38/narrative/hypertriglyceridemia | narrative |
| bp-action | ckm-stage-2-plus | lifestyle plus medication at >=140/90, or >=130/80 with CVD, stroke, diabetes, CKD, or PREVENT-CVD >=7.5%; goal <130/80 mm Hg | RENDERED: lifestyle modification plus antihypertensive pharmacotherapy for average BP ≥140/90 mm Hg, or average BP ≥130/80 mm Hg with clinical CVD, prior stroke, diabetes, CKD, or 10-year PREVENT-CVD ≥7.5%; goal <130/80 mm Hg | aha-acc-2026 | p38 | p38/narrative/hypertension-action | narrative |
| kidney-therapy-eligibility | ckm2-3-ckd | continue safely tolerated kidney-protective treatment after eGFR falls below its drug-specific initiation threshold | whose eGFR falls below drug-specific initiation thresholds, it is reasonable to continue those treatments as safely tolerated | aha-acc-2026 | p63 | p63/narrative/advanced-ckd-continuation | narrative |
| drug-safety-action | ckm4-ckd-hf | do not initiate finerenone if eGFR <25 mL/min/1.73 m² or potassium >5 mmol/L | RENDERED: finerenone initiation does not extend to eGFR <25 mL/min/1.73 m² or potassium >5 mmol/L | aha-acc-2026 | p62 | p62/narrative/finerenone-exclusions | narrative |

## Conflicts

CONFLICT: ckm-stage-action — `lifestyle and targeted multifactorial therapy at CKM stage 2-3 with T2D`; `intensified multifactorial therapy at CKM stage 2-3 with T2D`; `combination GLP-1-based therapy and SGLT2 inhibitor may be considered at stage 2-3`; `intensive lifestyle and risk-factor control at CKM stage 3 due to pre-HF`; `at stage 3 due to pre-HF with T2D or CKD, use SGLT2 inhibitor first line`; `symptomatic HFpEF: GLP-1-based therapy`; `HFpEF: exercise plus caloric-deficit diet`; `symptomatic HFrEF: obesity treatment may be considered`; `tailored lifestyle plan at CKM stage 4`; `SGLT2 inhibitor or GLP-1-based therapy at CKM stage 4`; `combined SGLT2 inhibitor and GLP-1-based therapy may be beneficial`; `prioritize SGLT2 inhibitor first line`; `HFpEF: add GLP-1-based therapy to SGLT2 inhibitor`. Stage, comorbidity, and treatment context determine the applicable action.

CONFLICT: ckm-staging-criterion — `BMI >=25 kg/m², or >=23 kg/m² with Asian ancestry`; `waist >=88 cm women or >=102 cm men; Asian ancestry >=80/90 cm women/men`; `fasting glucose 100-125 mg/dL or HbA1c 5.7%-6.4%`; `CAC >=100`; `NT-proBNP >=125 pg/mL`; `hs-cTnT >=14 ng/L women or >=22 ng/L men; hs-cTnI >=10 women or >=12 men`; `PREVENT-CVD 10-year risk >=20%`; `hypertension: SBP >=130, DBP >=80 mm Hg, or antihypertensive use`; `triglycerides >=150 mg/dL`; `T2D: fasting glucose >=126 mg/dL or HbA1c >=6.5%`; `metabolic syndrome is >=3 of waist, HDL-C, triglyceride, BP, and glucose criteria`; `metabolic syndrome HDL-C <40 mg/dL men or <50 mg/dL women`; `moderate-high CKD: G1-G2 A2-A3, G3a A1-A2, or G3b A1; very high: G3a A3, G3b A2-A3, or G4-G5`; `A1 UACR <30 mg/g; A2 30 to <300; A3 >=300 mg/g`. Stage and risk-factor context determine the criterion.

CONFLICT: drug-safety-action — `tirzepatide 15 mg; semaglutide 2.4 mg; liraglutide 3 mg`; `phentermine/topiramate 15/92 mg; naltrexone/bupropion 32/360 mg; orlistat 120 mg; phentermine 15-37.5 mg`; `limit phentermine/topiramate and naltrexone/bupropion when GFR <50`; `stop SGLT2 inhibitor 3-4 days before scheduled surgery`; `add nonoral or barrier contraception for 4 weeks after initiation and each dose escalation`; `wait >=2-3 hours after eating before lying down; extend dose phase 2-4 weeks for GI effects`; `eGFR fall <=30% expected; >30% evaluate and consider medication changes; potassium <=5.5 mEq/L may be tolerated, >5.5 requires mitigation or dose change`; `do not initiate finerenone if eGFR <25 mL/min/1.73 m² or potassium >5 mmol/L`. Drug and safety context determine the action.

CONFLICT: fibrosis-action — `age 35-64: FIB-4 <1.3 routine, 1.3-2.67 VCTE/ELF, >2.67 hepatology; age >=65: <2.0 routine, 2.0-2.67 VCTE/ELF, >2.67 hepatology`; `VCTE <8 low, 8-12 intermediate referral, >12 high; ELF <7.7 low, 7.7-9.8 intermediate referral, >9.8 high`; `fast >=3 hours before VCTE; do not use if BMI >=40 kg/m²`. Age, test, and preparation context determine the action.

CONFLICT: glycemic-action — `A1C 0.5%-1% above individualized goal: combine metformin with cardioprotective therapy`; `stable T2D and HF HbA1c 7%-8%, with metformin normal dose at eGFR >=60, 1000-1500 mg/day at 45-59, <=1000 mg/day at 30-44, and contraindicated below 30 mL/min/1.73 m²`; `HbA1c 7%-8.5% add metformin`; `HbA1c >8.5% add semaglutide or tirzepatide`; `HbA1c >10.0% or glucose >=300 mg/dL refer to endocrinology`; `pregnancy-planning target HbA1c <6.5%`. Population, kidney function, and treatment context determine the action.

CONFLICT: kidney-therapy-eligibility — `RASi at maximum tolerated dose when T2D or UACR >=30 mg/g and eGFR >=30 mL/min/1.73 m²`; `SGLT2 inhibitor when T2D or UACR >=200 mg/g and eGFR >=20 mL/min/1.73 m²`; `without T2D and UACR 30-199 mg/g, consider SGLT2 inhibitor`; `with T2D, UACR >=30 mg/g, and eGFR >=25 mL/min/1.73 m² despite ACEi/ARB and SGLT2 inhibitor, add nsMRA`; `with T2D and UACR >=100 mg/g despite ACEi/ARB and SGLT2 inhibitor, add GLP-1-based therapy`; `initiation floors: RASi >=30, SGLT2 inhibitor >=20, finerenone >=25 mL/min/1.73 m²`; `continue safely tolerated kidney-protective treatment after eGFR falls below its drug-specific initiation threshold`; `diabetes, CKD, UACR >=100 mg/g: add GLP-1-based therapy to SGLT2 inhibitor`; `diabetes, CKD, UACR >=30 mg/g: add nsMRA to SGLT2 inhibitor`; `eGFR >=30 mL/min/1.73 m² with HFrEF: start ARNI or other RASi`; `eGFR >=20 mL/min/1.73 m² with any EF: start SGLT2 inhibitor`; `T2D, UACR >=30 mg/g, LVEF >40%, eGFR >=25 mL/min/1.73 m²: start nsMRA`; `HFrEF and eGFR >30 mL/min/1.73 m²: potassium binder may enable RAAS inhibition`. Drug, albuminuria, comorbidity, and initiation-versus-continuation context determine the value.

CONFLICT: monitoring-interval — `prediabetes: FIB-4 every 2-3 years`; `lipids, glycemia, eGFR every 2-3 years; BP annually`; `BMI and waist at least annually`; `lipids, glycemia, eGFR every 5 years; BP annually`; `lipids, glycemia, BP, eGFR, and UACR at least annually`; `diabetes or >=2 cardiometabolic risks: FIB-4 every 1-2 years`; `assess OSA symptoms annually`; `assess glycemia every 3-6 months, more often if not at goal`; `repeat UACR after 3-6 months`; `recalculate eGFR and measure potassium after 2-4 weeks`. Stage, treatment, and measured property determine the interval.

CONFLICT: pre-hf-definition — `LAVI >=29 mL/m²; LVMI >116 g/m² men or >95 women; RWT >0.42; wall >=12 mm; LVEF <50%; GLS <16%`; `septal e' <7 cm/s; TR >2.8 m/s; average E/e' >=15`; `BNP >=35 pg/mL or NT-proBNP >=125 pg/mL`. Imaging, functional, and biomarker context determine the definition.

CONFLICT: pregnancy-action — `GDM oral glucose tolerance test 4-12 weeks postpartum`; `pregnancy-planning HbA1c <6.5%`; `stage 2-4 interdisciplinary pregnancy care`; `adverse-pregnancy-outcome screening within 1 postpartum year`; `all postpartum women after clearance >=150 minutes/week activity`. Pregnancy and postpartum population determine the action.

CONFLICT: prevent-risk-action — `use CAC when PREVENT-ASCVD is 5% to <10%, or selected 3% to <5%`; `at 10-year PREVENT-HF >=5%, evaluate pre-HF with cardiac biomarkers`; `calculate 30-year risk at age 30-59 years`; `calculate 10-year risk at age 30-79 years`; `statin support: age >=40 with T2D/CKD or PREVENT-ASCVD 5%-9.9%; consider at 3%-4.9%`. Risk instrument, age, and decision context determine the threshold.

CONFLICT: therapy-eligibility — `PREVENT-CVD >=7.5%: include SGLT2 inhibitor or GLP-1-based therapy`; `hypertriglyceridemia fasting >=150 or nonfasting >=175 mg/dL; severe >=500 mg/dL adds pancreatitis-prevention measures`; `stage 4: intensive multicomponent lifestyle intervention`; `BMI >=27 kg/m²: GLP-1-based therapy`; `at BMI >=27 kg/m², add GLP-1-based therapy to structured lifestyle intervention`; `non-GLP-1 obesity pharmacotherapy may be used in stage 1`; `MBS may be used at stage 1-3 after inadequate lifestyle response`; `CAC 100-999: LDL-C <70 mg/dL; CAC >=1000: LDL-C <55 mg/dL`. Disease, stage, risk, and treatment context determine eligibility.

CONFLICT: weight-action — `target at least 5%-10% baseline weight loss`; `counsel at least annually about 5%-10% weight loss`; `caloric deficit 500-750 kcal/day, >=150 minutes/week activity, and >=14 months behavioral therapy`; `GLP-1-based therapy may be used after regain >=25% of total lost weight`; `BMI >=30 kg/m² and failed lifestyle goals: MBS for minimum 5%-10% loss`; `reassess within 3-6 months; <5% loss triggers escalation, switch, or referral`. Treatment stage and longitudinal context determine the action.

CONFLICT: youth-staging-criterion — `overweight BMI >=85th to <95th percentile; Class 1 obesity >=95th percentile to <120% of 95th; Class 2 obesity >=120% to <140% of 95th or BMI >=35 to <40 kg/m², whichever is lower; Class 3 obesity >=140% of 95th or BMI >=40 kg/m², whichever is lower`; `total cholesterol >=200, HDL-C <40, LDL-C >=130, non-HDL-C >=145 mg/dL`; `triglycerides >=100 mg/dL age 0-9; >=130 mg/dL age 10-19`; `prediabetes: fasting glucose 100-125, HbA1c 5.7%-6.4%, or 2-hour 75-g glucose 140-199 mg/dL`; `diabetes: fasting glucose >=126, HbA1c >=6.5%, 2-hour 75-g glucose >=200, or symptomatic random glucose >=200 mg/dL`. Age and risk-factor context determine the pediatric criterion.

## Coverage

The source is `exact`: the committed recommendation artifact contains 88 unique recommendations across 26 recommendation tables. Threshold rows cite 56 exact locators; the remaining 32 exact locators were read and contain no additional numeric patient-action decision point beyond narrative/table rows or are economic-value or qualitative recommendations.

- `p22/interdisciplinary-care-continued/2` - no additional numeric patient-action decision point
- `p26/overarching-approach-to-obesity-management/2` - no additional numeric patient-action decision point
- `p26/overarching-approach-to-obesity-management/3` - no additional numeric patient-action decision point
- `p28/intensive-lifestyle-modification-for-weight-loss/2` - no additional numeric patient-action decision point
- `p28/intensive-lifestyle-modification-for-weight-loss/3` - no additional numeric patient-action decision point
- `p28/intensive-lifestyle-modification-for-weight-loss/4` - no additional numeric patient-action decision point
- `p28/intensive-lifestyle-modification-for-weight-loss/5` - no additional numeric patient-action decision point
- `p30/obesity-pharmacotherapy-for-weight/2` - economic-value statement; no patient-action decision point
- `p32/surgical-interventions-for-weight-loss-in-ckm/2` - economic-value statement; no patient-action decision point
- `p33/management-after-gestational-diabetes/2` - no additional numeric patient-action decision point
- `p33/management-after-gestational-diabetes/3` - no additional numeric patient-action decision point
- `p34/t2d-in-ckm-syndrome-stage-2-to-3/4` - economic-value statement; no patient-action decision point
- `p34/t2d-in-ckm-syndrome-stage-2-to-3/5` - economic-value statement; no patient-action decision point
- `p39/management-of-ckd-in-ckm-syndrome-stage/4` - economic-value statement; no patient-action decision point
- `p39/management-of-ckd-in-ckm-syndrome-stage/6` - economic-value statement; no patient-action decision point
- `p39/management-of-ckd-in-ckm-syndrome-stage/8` - economic-value statement; no patient-action decision point
- `p47/ckm-syndrome-stage-4-with-obesity-and/3` - economic-value statement; no patient-action decision point
- `p51/ckm-syndrome-stage-4-with-t2d-and-ascvd/3` - economic-value statement; no patient-action decision point
- `p51/ckm-syndrome-stage-4-with-t2d-and-ascvd/4` - economic-value statement; no patient-action decision point
- `p55/ckm-syndrome-stage-4-with-obesity-and-hf/2` - economic-value statement; no patient-action decision point
- `p57/ckm-syndrome-stage-4-with-t2d-and-hf/2` - economic-value statement; no patient-action decision point
- `p57/ckm-syndrome-stage-4-with-t2d-and-hf/3` - economic-value statement; no patient-action decision point
- `p59/ckm-syndrome-stage-4-with-ckd-and-hf/2` - economic-value statement; no patient-action decision point
- `p59/ckm-syndrome-stage-4-with-ckd-and-hf/4` - economic-value statement; no patient-action decision point
- `p59/ckm-syndrome-stage-4-with-ckd-and-hf/5` - economic-value statement; no patient-action decision point
- `p59/ckm-syndrome-stage-4-with-ckd-and-hf/7` - economic-value statement; no patient-action decision point
- `p59/ckm-syndrome-stage-4-with-ckd-and-hf/9` - economic-value statement; no patient-action decision point
- `p64/metabolic-dysfunction-associated-steatotic/4` - no additional numeric patient-action decision point
- `p64/metabolic-dysfunction-associated-steatotic/3` - no additional numeric patient-action decision point
- `p67/obstructive-sleep-apnea-continued/2` - no additional numeric patient-action decision point
- `p67/pregnancy-and-ckm-health/1` - no additional numeric patient-action decision point
- `p68/pregnancy-and-ckm-health-continued/5` - no additional numeric patient-action decision point
