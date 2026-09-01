# Lipid management in chronic kidney disease — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2013-lipids | KDIGO | KDIGO/KDIGO-2013-Lipids-Guideline | guideline | 2013 final guideline | 2013-11 | https://kdigo.org/guidelines/lipids-in-ckd/ | chosen | bound |

## Scope

**Read:** all 56 pages: front matter, the complete summary and adult algorithm, every
adult and pediatric assessment and treatment chapter, all clinical tables and figures,
the complete methods section, disclosures, and references.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's patient-action rule:** publication years, study sizes,
baseline cohort characteristics, confidence intervals, evidence-grading mechanics,
search strategies, author and disclosure details, and bibliography numbers. Trial effect
estimates were read; the sheet retains their benefit or harm direction and the source's
care boundary, while omitting estimates that do not independently change a patient
action. Tables 6–16 are evidence-profile, evidence-search, quality-assessment, or voting
tables and add no patient-action threshold beyond the retained clinical chapters.

**Source: `kdigo-2013-lipids`**

| span | pages | read |
| --- | --- | --- |
| cover, sponsor, contents, boards, reference keys, nomenclature, conversions, abbreviations, and notice | 1-10 | read 2026-09-01; blind 2026-09-01 |
| foreword, work group, and abstract | 11-13 | read 2026-09-01; blind 2026-09-01 |
| summary recommendations and adult algorithm | 14-16 | yes |
| introduction | 17-18 | read 2026-09-01; blind 2026-09-01 |
| adult lipid assessment | 19-21 | yes |
| adult pharmacological cholesterol treatment | 22-30 | yes |
| pediatric lipid assessment | 31-32 | yes |
| pediatric pharmacological cholesterol treatment | 33-34 | yes |
| adult triglyceride treatment | 35-36 | yes |
| pediatric triglyceride treatment | 37 | yes |
| guideline-development methods and evidence tables | 38-47 | read 2026-09-01; blind 2026-09-01 |
| disclosures and administrative matter | 48-53 | read 2026-09-01; blind 2026-09-01 |
| references | 54-56 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults-new-ckd | adults with newly identified CKD, including those treated with chronic dialysis or kidney transplantation |
| adults-ckd | adults with CKD, including those treated with chronic dialysis or kidney transplantation |
| adults-ckd-followup-selected | adults with CKD for whom lipid measurement would alter management, including assessment of adherence, a change in kidney replacement modality, a new secondary cause, or cardiovascular risk assessment in a younger untreated adult |
| adults-50-plus-egfr-below60 | adults aged 50 years or older with eGFR less than 60 ml/min per 1.73 m2 who are not treated with chronic dialysis or kidney transplantation |
| adults-50-plus-egfr-atleast60 | adults aged 50 years or older with CKD and eGFR at least 60 ml/min per 1.73 m2 |
| adults-18-49-nondialysis-nontransplant | adults aged 18 to 49 years with CKD who are not treated with chronic dialysis or kidney transplantation |
| adults-dialysis-no-statin | adults with dialysis-dependent CKD who are not receiving a statin or statin/ezetimibe when dialysis begins |
| adults-dialysis-existing-statin | adults already receiving a statin or statin/ezetimibe when dialysis treatment begins |
| adults-kidney-transplant | adult kidney transplant recipients |
| adults-kidney-transplant-younger-low-risk | kidney transplant recipients younger than 30 years without traditional cardiovascular risk factors |
| adults-ckd-egfr-below60-treated | adults with eGFR less than 60 ml/min per 1.73 m2 or receiving renal replacement therapy, including chronic dialysis and kidney transplantation, who receive a statin-containing regimen |
| adults-ckd-egfr-atleast60-nontransplant | adults with CKD and eGFR at least 60 ml/min per 1.73 m2 who have not received a kidney transplant |
| adults-statin-candidate | adults with CKD being considered for statin-containing treatment |
| adults-statin-treated | adults with CKD receiving a statin-containing regimen |
| adults-isolated-low-hdl | adults with CKD whose only lipid abnormality is low HDL cholesterol |
| adults-near-statin-decision | adults with CKD not receiving a statin for whom estimated cardiovascular risk is close to the threshold for initiating statin treatment |
| adults-known-severe-hypertriglyceridemia | adults with CKD and known severe hypertriglyceridemia for whom follow-up triglyceride measurement could alter care |
| children-new-ckd | children with newly identified CKD, including those treated with chronic dialysis or kidney transplantation |
| children-ckd | children with CKD, including those treated with chronic dialysis or kidney transplantation |
| children-ckd-dyslipidemia | children with CKD and dyslipidemia |
| children-ckd-dyslipidemia-obesity | children with CKD and dyslipidemia who are overweight or obese |
| children-under18-ckd | children younger than 18 years with CKD, including those treated with chronic dialysis or kidney transplantation |
| selected-children-severe-ldl | boys older than 10 years or postmenarchal girls with CKD, severely elevated LDL cholesterol, and strong preference for pharmacological prevention, particularly with a family history of premature coronary disease, diabetes, hypertension, smoking, or end-stage kidney disease |
| adults-ckd-hypertriglyceridemia | adults with CKD, including those treated with chronic dialysis or kidney transplantation, and hypertriglyceridemia |
| adults-ckd-marked-hypertriglyceridemia | adults with CKD and fasting triglycerides above 11.3 mmol/L (1000 mg/dL) |
| children-ckd-hypertriglyceridemia | children with CKD, including those treated with chronic dialysis or kidney transplantation, and hypertriglyceridemia |
| children-ckd-very-severe-triglycerides | children with CKD and fasting triglycerides above 11.3 mmol/L (1000 mg/dL) |

## Quantities

| key | verbatim |
| --- | --- |
| adult-baseline-lipid-profile | baseline adult lipid-profile assessment |
| adult-routine-lipid-followup | routine adult follow-up lipid measurement boundary |
| adult-selected-lipid-followup | circumstances in which adult follow-up measurement may change management |
| severe-lipid-evaluation | severe triglyceride or LDL cholesterol trigger for specialist referral or further evaluation |
| fasting-lipid-boundary | fasting versus nonfasting sampling boundary |
| secondary-dyslipidemia-review | secondary causes to identify during lipid assessment |
| adult-age50-low-egfr-statin | statin-containing treatment for older adults with lower eGFR |
| adult-age50-preserved-egfr-statin | statin treatment for older adults with preserved eGFR |
| younger-adult-statin-indications | statin indications for adults aged 18 to 49 years |
| dialysis-statin-initiation | initiation of statin-containing treatment in dialysis-dependent CKD |
| dialysis-statin-continuation | continuation and reassessment of statin-containing treatment after dialysis begins |
| transplant-statin | statin treatment after adult kidney transplantation |
| fire-and-forget-strategy | treatment strategy without LDL targets or routine dose escalation |
| statin-regimen-selection | selection of regimens tested for safety in CKD |
| statin-dose-table | daily statin-containing regimens tested in advanced CKD |
| statin-laboratory-monitoring | baseline and symptom-triggered laboratory monitoring |
| statin-contraindications | contraindications to statin treatment |
| statin-interaction-management | management of medications that increase statin exposure |
| statin-fibrate-combination | statin and fibrate combination boundary |
| ezetimibe-monotherapy | ezetimibe monotherapy boundary |
| adult-statin-benefit | cardiovascular benefit and kidney-progression boundary |
| dialysis-statin-benefit | uncertainty and individualization of benefit in dialysis |
| pediatric-baseline-lipid-profile | baseline pediatric lipid-profile assessment |
| pediatric-lipid-followup | pediatric fasting lipid follow-up interval |
| pediatric-lipid-categories | pediatric total, LDL, and non-HDL cholesterol categories |
| pediatric-statin-initiation | formal pediatric statin-initiation boundary |
| selected-pediatric-statin-context | narrative selected-case statin context |
| pediatric-statin-regimen | pediatric dose and combination-treatment boundary |
| adult-triglyceride-lifestyle | adult therapeutic lifestyle changes for hypertriglyceridemia |
| adult-triglyceride-diet | adult dietary measures for severe hypertriglyceridemia |
| adult-fibrate-use | adult fibrate boundary for very severe triglycerides |
| adult-niacin-use | adult niacin boundary |
| pediatric-triglyceride-lifestyle | pediatric therapeutic lifestyle changes for hypertriglyceridemia |
| pediatric-triglyceride-pharmacotherapy | pediatric pharmacological-treatment and referral boundary |
| isolated-low-hdl-treatment | treatment boundary for isolated low HDL cholesterol |
| specialized-lipid-markers | routine-use boundary for lipoprotein(a) and other specialized markers |
| optional-lipid-markers | optional apolipoprotein B, non-HDL cholesterol, and HDL cholesterol assessment near a statin decision |
| triglyceride-followup | severe-triglyceride follow-up and routine-fasting boundary |
| younger-adult-statin-preference | preference-sensitive treatment around the ten-year coronary-risk threshold |
| grapefruit-statin-interaction | grapefruit exposure during statin treatment |
| statin-dose-country-note | source note on lower statin doses in Asian countries |
| pediatric-nutrition-diet | pediatric nutrition and dietary counseling boundary |
| pediatric-obesity-weight-loss | pediatric obesity and weight-loss action |
| pediatric-secondary-causes | pediatric secondary-dyslipidemia action |
| pediatric-tlc-all | therapeutic lifestyle changes for all children with CKD |
| pediatric-triglyceride-diet | pediatric dietary and implementation measures for severe triglycerides |
| adult-fibrate-cv-prevention | fibrate boundary for cardiovascular-risk reduction |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| adult-baseline-lipid-profile | adults-new-ckd | obtain total cholesterol, LDL cholesterol, HDL cholesterol, and triglycerides at initial evaluation; Grade 1C | RENDERED: In adults with newly identified CKD (including those treated with chronic dialysis or kidney transplantation), we recommend evaluation with a lipid profile (total cholesterol, LDL cholesterol, HDL cholesterol, triglycerides). (1C) | kdigo-2013-lipids | 14 | p14/narrative/recommendation-1-1 | narrative |
| adult-routine-lipid-followup | adults-ckd | follow-up lipid measurement is not required for most adults; Not Graded | RENDERED: In adults with CKD (including those treated with chronic dialysis or kidney transplantation), follow-up measurement of lipid levels is not required for the majority of patients. (Not Graded) | kdigo-2013-lipids | 14 | p14/narrative/recommendation-1-2 | narrative |
| adult-selected-lipid-followup | adults-ckd-followup-selected | repeat only when results would alter management; frequency follows clinical status, and cardiovascular risk should be reassessed annually | RENDERED: follow-up measurement ... for whom these measurements are judged to favorably influence adherence ... or other processes of care ... frequency ... determined by ... clinical status ... assessment of cardiovascular risk should be considered annually | kdigo-2013-lipids | 20 | p20/narrative/followup-indications-and-frequency | narrative |
| severe-lipid-evaluation | adults-new-ckd | consider specialist referral or further evaluation for fasting triglycerides above 11.3 mmol/L (1000 mg/dL) or LDL cholesterol above 4.9 mmol/L (190 mg/dL) | RENDERED: consider specialist referral for further evaluation ... fasting triglycerides ... 11.3 mmol/l (1000 mg/dl) or LDL-C ... 4.9 mmol/l (190 mg/dl) | kdigo-2013-lipids | 19 | p19/narrative/severe-dyslipidemia | narrative |
| fasting-lipid-boundary | adults-new-ckd | either fasting or nonfasting sampling may be used initially; fasting chiefly improves triglyceride assessment and Friedewald LDL estimation | RENDERED: fasting status does not affect HDL-C ... and has only a small effect on LDL-C ... Fasting will mainly affect triglyceride values and ... LDL-C values calculated using the Friedewald formula. | kdigo-2013-lipids | 19 | p19/narrative/fasting-boundary | narrative |
| isolated-low-hdl-treatment | adults-isolated-low-hdl | do not use specific treatment for isolated low HDL cholesterol | RENDERED: Isolated low HDL-C does not imply specific therapy. | kdigo-2013-lipids | 19 | p19/narrative/isolated-low-hdl | narrative |
| specialized-lipid-markers | adults-new-ckd | do not routinely measure lipoprotein(a) or other specialized lipid markers | RENDERED: Measurement of lipoprotein(a) and other markers of dyslipidemia require further research before routine use can be recommended. | kdigo-2013-lipids | 19 | p19/narrative/specialized-lipid-markers | narrative |
| secondary-dyslipidemia-review | adults-new-ckd | assess for nephrotic syndrome, excess alcohol use, hypothyroidism, liver disease, diabetes, and medication causes including retinoids, androgens, anticonvulsants, oral contraceptives, antiretroviral therapy, corticosteroids, diuretics, cyclosporine, beta-blockers, and sirolimus | RENDERED: TABLE 1. Secondary causes of dyslipidemias ... Nephrotic syndrome ... Excessive alcohol consumption ... Hypothyroidism ... Liver disease ... Diabetes ... 13-cis-retinoic acid ... Androgens ... Anticonvulsants ... Oral contraceptives ... Highly active antiretroviral therapy ... Corticosteroids ... Diuretics ... Cyclosporine ... Beta-blockers ... Sirolimus | kdigo-2013-lipids | 20 | p20/narrative/table-1-secondary-causes | narrative |
| optional-lipid-markers | adults-near-statin-decision | when a statin decision remains uncertain, apolipoprotein B, non-HDL cholesterol, or HDL cholesterol may be measured if the result could change treatment | RENDERED: measurement of apoB and/or non-HDL-C and HDL-C could be considered in people for whom such results might influence the decision to prescribe statin treatment | kdigo-2013-lipids | 20 | p20/narrative/optional-markers-near-statin-decision | narrative |
| triglyceride-followup | adults-known-severe-hypertriglyceridemia | follow triglycerides when severe hypertriglyceridemia is already known; routine fasting triglyceride measurement is not recommended | RENDERED: routine measurement of fasting TG levels is not recommended. However, clinicians may consider following serum TG levels in patients with known severe hypertriglyceridemia. | kdigo-2013-lipids | 20 | p20/narrative/severe-triglyceride-followup | narrative |
| adult-age50-low-egfr-statin | adults-50-plus-egfr-below60 | treat with a statin or statin/ezetimibe combination; Grade 1A | RENDERED: In adults aged 50 years and older with eGFR <60 ml/min/1.73 m2 but not treated with chronic dialysis or kidney transplantation ... treatment with a statin or statin/ezetimibe combination. (1A) | kdigo-2013-lipids | 14 | p14/narrative/recommendation-2-1-1 | narrative |
| adult-age50-preserved-egfr-statin | adults-50-plus-egfr-atleast60 | treat with a statin; Grade 1B | RENDERED: In adults aged 50 years and older with CKD and eGFR ≥60 ml/min/1.73 m2 ... treatment with a statin. (1B) | kdigo-2013-lipids | 14 | p14/narrative/recommendation-2-1-2 | narrative |
| younger-adult-statin-indications | adults-18-49-nondialysis-nontransplant | suggest a statin for known coronary disease, diabetes mellitus, prior ischemic stroke, or estimated ten-year coronary death or nonfatal myocardial-infarction risk above 10%; Grade 2A | RENDERED: In adults aged 18-49 years with CKD but not treated with chronic dialysis or kidney transplantation, we suggest statin treatment in people with one or more of the following: known coronary disease ... diabetes mellitus ... prior ischemic stroke ... estimated 10-year incidence of coronary death or non-fatal myocardial infarction >10%. (2A) | kdigo-2013-lipids | 14 | p14/narrative/recommendation-2-2 | narrative |
| younger-adult-statin-preference | adults-18-49-nondialysis-nontransplant | a person with ten-year coronary risk below 10% may still choose a statin, and a person with risk above 10% may decline after an informed preference-sensitive discussion | RENDERED: people with 10-year risk of coronary death or non-fatal MI <10% could choose to receive statin treatment, while patients with risk >10% might choose not to receive statin treatment | kdigo-2013-lipids | 27 | p27/narrative/younger-adult-statin-preference | narrative |
| dialysis-statin-initiation | adults-dialysis-no-statin | do not initiate a statin or statin/ezetimibe combination; Grade 2A | RENDERED: In adults with dialysis-dependent CKD, we suggest that statins or statin/ezetimibe combination not be initiated. (2A) | kdigo-2013-lipids | 14 | p14/narrative/recommendation-2-3-1 | narrative |
| dialysis-statin-continuation | adults-dialysis-existing-statin | continue the statin or statin/ezetimibe combination when dialysis begins; Grade 2C, with periodic reassessment against pill burden, toxicity, comorbidity, and patient preference | RENDERED: patients already receiving statins or statin/ezetimibe combination at the time of dialysis initiation ... continued. (2C) ... periodically reviewed ... discontinue ... depending on ... preferences ... competing risk ... pill burden and drug toxicity | kdigo-2013-lipids | 28 | p28/narrative/dialysis-continuation-and-reassessment | narrative |
| transplant-statin | adults-kidney-transplant | suggest treatment with a statin; Grade 2B | RENDERED: In adult kidney transplant recipients, we suggest treatment with a statin. (2B) | kdigo-2013-lipids | 14 | p14/narrative/recommendation-2-4 | narrative |
| transplant-statin | adults-kidney-transplant-younger-low-risk | a recipient younger than 30 years without traditional cardiovascular risk factors may reasonably choose not to receive a statin | RENDERED: patients who place a relatively low value on a small absolute reduction ... For example, a young kidney transplant recipient (say <30 years of age) without other cardiovascular risk factors could rationally choose not to receive statin treatment | kdigo-2013-lipids | 28 | p28/narrative/young-transplant-preference | narrative |
| fire-and-forget-strategy | adults-statin-treated | use a fire-and-forget strategy: do not treat to an LDL target and do not escalate solely to reach a target | RENDERED: The KDIGO Work Group does not recommend the treat-to-target strategy ... higher doses of statins have not been proven to be safe in the setting of CKD. Therefore, the Work Group recommends a fire-and-forget strategy | kdigo-2013-lipids | 25 | p25/narrative/fire-and-forget | narrative |
| statin-regimen-selection | adults-ckd-egfr-below60-treated | use a regimen and dose shown beneficial in randomized CKD trials; a patient tolerating another regimen need not automatically switch, but dose reduction may be prudent if severe kidney dysfunction develops | RENDERED: prescription of statins in high cardiovascular risk people with eGFR <60 ml/min/1.73 m2 or RRT should be based on regimens and doses ... in randomized trials ... Patients with progressive renal dysfunction who are tolerating an alternative regimen do not necessarily need to be switched ... dose reduction may be prudent | kdigo-2013-lipids | 25 | p25/narrative/regimen-selection | narrative |
| statin-regimen-selection | adults-ckd-egfr-atleast60-nontransplant | use any statin regimen approved for the general population | RENDERED: Given less concern about drug toxicity in the setting of better kidney function, patients with eGFR ≥60 ml/min/1.73 m2 ... may be treated with any statin regimen that is approved for use in the general population. | kdigo-2013-lipids | 25 | p25/narrative/preserved-egfr-regimens | narrative |
| statin-dose-table | adults-ckd-egfr-below60-treated | tested daily regimens are fluvastatin 80 mg, atorvastatin 20 mg, rosuvastatin 10 mg, simvastatin/ezetimibe 20/10 mg, pravastatin 40 mg, simvastatin 40 mg, and pitavastatin 2 mg; lovastatin was not studied | RENDERED: TABLE 4. Recommended doses ... eGFR G3a-G5, including patients on dialysis or with a kidney transplant ... Fluvastatin 80 ... Atorvastatin 20 ... Rosuvastatin 10 ... Simvastatin/Ezetimibe 20/10 ... Pravastatin 40 ... Simvastatin 40 ... Pitavastatin 2 ... Lovastatin nd | kdigo-2013-lipids | 25 | p25/narrative/table-4-statin-doses | narrative |
| statin-dose-table | adults-ckd-egfr-atleast60-nontransplant | rosuvastatin 40 mg daily is not recommended even in CKD stages G1-G2 because it may increase adverse renal events | RENDERED: Rosuvastatin 40 mg daily is not recommended for use in CKD 1-2 non-transplant patients, as it may increase the risk of adverse renal events. | kdigo-2013-lipids | 25 | p25/narrative/rosuvastatin-40-warning | narrative |
| statin-dose-table | adults-kidney-transplant | cyclosporine inhibits statin metabolism and can increase statin blood concentrations | RENDERED: Cyclosporin inhibits the metabolism of certain statins resulting in higher blood levels. | kdigo-2013-lipids | 25 | p25/narrative/cyclosporine-statin-interaction | narrative |
| statin-dose-country-note | adults-ckd-egfr-below60-treated | lower statin doses than the table lists may be appropriate in Asian countries | RENDERED: Lower doses than those used in major trials of statins in CKD populations may be appropriate in Asian countries. | kdigo-2013-lipids | 25 | p25/narrative/lower-dose-asian-countries | narrative |
| statin-laboratory-monitoring | adults-statin-candidate | measure transaminases before treatment; do not routinely repeat transaminases or creatine kinase in asymptomatic patients, and check creatine kinase when muscle symptoms occur | RENDERED: baseline levels of transaminases be measured before initiating statin treatment. Routine follow-up measurements ... are not recommended ... does not recommend measurement of CK levels ... unless the patient develops symptoms suggestive of myopathy. | kdigo-2013-lipids | 25 | p25/narrative/statin-laboratory-monitoring | narrative |
| statin-contraindications | adults-statin-candidate | do not use during pregnancy or breastfeeding, active liver disease, or when transaminases are at least three times the upper limit of normal | RENDERED: Statins are contraindicated in pregnant or breastfeeding females, in people with active liver disease, and in people with transaminase levels that are three times or more the upper limit of normal. | kdigo-2013-lipids | 25 | p25/narrative/statin-contraindications | narrative |
| statin-interaction-management | adults-statin-treated | temporarily stop the statin for a short interacting-drug course; for longer treatment, switch to a safer statin or reduce the dose | RENDERED: temporarily discontinued for the duration of therapy. For medications that will be required for more than a few days, a switch to an alternative statin or reducing the statin dose could be considered | kdigo-2013-lipids | 25 | p25/narrative/statin-interaction-management | narrative |
| grapefruit-statin-interaction | adults-statin-treated | grapefruit juice may increase blood levels of statins | RENDERED: consumption of grapefruit juice may increase blood levels of statins | kdigo-2013-lipids | 25 | p25/narrative/grapefruit-statin-interaction | narrative |
| statin-fibrate-combination | adults-ckd | do not combine a fibrate with a statin; prefer a statin when choosing between the two | RENDERED: recommends that fibrates not be used concomitantly with statins in patients with CKD ... statins be prescribed in preference to fibrates | kdigo-2013-lipids | 25 | p25/narrative/statin-fibrate-boundary | narrative |
| ezetimibe-monotherapy | adults-ckd | do not use ezetimibe monotherapy because clinical benefit is unproven | RENDERED: There is no evidence that ezetimibe monotherapy will improve clinically relevant outcomes ... ezetimibe monotherapy is not recommended. | kdigo-2013-lipids | 26 | p26/narrative/ezetimibe-monotherapy | narrative |
| adult-statin-benefit | adults-50-plus-egfr-below60 | statin-containing treatment reduces major atherosclerotic events but was not shown to prevent progression to end-stage kidney disease | RENDERED: SHARP showed a significant decrease in major atherosclerotic events with simvastatin plus ezetimibe; treatment did not reduce the risk of progression to end-stage renal disease. | kdigo-2013-lipids | 26 | p26/narrative/sharp-benefit-kidney-boundary | narrative |
| dialysis-statin-benefit | adults-dialysis-no-statin | average cardiovascular benefit is smaller and uncertain in dialysis; initiation may still be considered when LDL cholesterol is unusually high, myocardial infarction is recent, or life expectancy is longer, while severe comorbidity or high pill burden favors not starting | RENDERED: Very high LDL-C might favor treatment, while more severe comorbidity or higher pill burden would favor not treating. Recent myocardial infarction or greater life expectancy would favor treatment. | kdigo-2013-lipids | 28 | p28/narrative/dialysis-benefit-individualization | narrative |
| pediatric-baseline-lipid-profile | children-new-ckd | obtain total cholesterol, LDL cholesterol, HDL cholesterol, and triglycerides at initial evaluation; Grade 1C | RENDERED: In children with newly identified CKD ... evaluation with a lipid profile (total cholesterol, LDL cholesterol, HDL cholesterol, triglycerides). (1C) | kdigo-2013-lipids | 15 | p15/narrative/recommendation-3-1 | narrative |
| pediatric-lipid-followup | children-ckd | measure a fasting lipid profile annually; Not Graded, with more or less frequent testing according to clinical status and another assessment when dialysis or transplant modality changes | RENDERED: annual measurement of fasting lipid levels. (Not Graded) ... More frequent follow-up may be appropriate ... Less frequent follow-up may be appropriate ... evaluated after a change in RRT modality or other changes that may impact the secondary causes of dyslipidemia | kdigo-2013-lipids | 32 | p32/narrative/pediatric-annual-followup | narrative |
| pediatric-lipid-categories | children-ckd | total cholesterol is acceptable below 4.4 mmol/L (170 mg/dL), borderline 4.4-5.2 mmol/L (170-199 mg/dL), and high above 5.2 mmol/L (at least 200 mg/dL) | RENDERED: TABLE 5 ... Total cholesterol ... Acceptable <4.4 (<170) ... Borderline-high 4.4-5.2 (170-199) ... High >5.2 (≥200) | kdigo-2013-lipids | 32 | p32/narrative/table-5-total-cholesterol | narrative |
| pediatric-lipid-categories | children-ckd | LDL cholesterol is acceptable below 2.8 mmol/L (110 mg/dL), borderline 2.8-3.3 mmol/L (110-129 mg/dL), and high at least 3.4 mmol/L (130 mg/dL) | RENDERED: TABLE 5 ... LDL-C ... Acceptable <2.8 (<110) ... Borderline-high 2.8-3.3 (110-129) ... High ≥3.4 (≥130) | kdigo-2013-lipids | 32 | p32/narrative/table-5-ldl-cholesterol | narrative |
| pediatric-lipid-categories | children-ckd | non-HDL cholesterol is acceptable below 3.1 mmol/L (120 mg/dL), borderline 3.1-3.7 mmol/L (120-144 mg/dL), and high at least 3.8 mmol/L (145 mg/dL) | RENDERED: TABLE 5 ... Non-HDL-C ... Acceptable <3.1 (<120) ... Borderline-high 3.1-3.7 (120-144) ... High ≥3.8 (≥145) | kdigo-2013-lipids | 32 | p32/narrative/table-5-non-hdl-cholesterol | narrative |
| pediatric-statin-initiation | children-under18-ckd | do not initiate a statin or statin/ezetimibe combination; Grade 2C | RENDERED: In children less than 18 years of age with CKD ... we suggest that statins or statin/ezetimibe combination not be initiated. (2C) | kdigo-2013-lipids | 15 | p15/narrative/recommendation-4-1 | narrative |
| selected-pediatric-statin-context | selected-children-severe-ldl | despite the formal noninitiation recommendation, selected older children may be considered after individualized discussion when they strongly value prevention; adult cardiovascular risk calculators are not valid in children | RENDERED: Boys aged >10 years and post-menarchal girls with severely elevated LDL-C who place a high value on the potential for preventing cardiovascular events ... may be considered for statin therapy ... risk calculators developed for use in adults are not valid in children | kdigo-2013-lipids | 33 | p33/narrative/selected-pediatric-statin-context | narrative |
| pediatric-nutrition-diet | children-ckd-dyslipidemia | begin treatment with nutrition and dietary counseling; use diets judiciously, or not at all, in children who are malnourished | RENDERED: Treatment for dyslipidemia in children should first include nutrition and dietary counseling ... Diets, however, should be used judiciously, or not at all, in children who are malnourished. | kdigo-2013-lipids | 33 | p33/narrative/pediatric-nutrition-diet | narrative |
| pediatric-obesity-weight-loss | children-ckd-dyslipidemia-obesity | address obesity with a weight-loss regimen when necessary | RENDERED: Treatment for dyslipidemia in children should ... address obesity with weight loss regimens if necessary. | kdigo-2013-lipids | 33 | p33/narrative/pediatric-obesity-weight-loss | narrative |
| pediatric-secondary-causes | children-ckd-dyslipidemia | treat secondary causes of dyslipidemia first | RENDERED: Secondary causes of dyslipidemias should also be treated first. | kdigo-2013-lipids | 33 | p33/narrative/pediatric-secondary-causes | narrative |
| pediatric-tlc-all | children-ckd | adopt therapeutic lifestyle changes | RENDERED: Therapeutic lifestyle changes (TLC) should be adopted among all children with CKD. | kdigo-2013-lipids | 33 | p33/narrative/pediatric-tlc-all | narrative |
| pediatric-statin-regimen | selected-children-severe-ldl | if prescribed, use the lowest available dose; do not target a specific LDL level, do not escalate based on LDL, and do not combine a statin with bile-acid resins, colestipol, or ezetimibe | RENDERED: If a statin is prescribed, the Work Group suggests the lowest available dose. There is no direct evidence ... a specific LDL-C target ... statin dose escalation based on LDL-C levels is not recommended ... statin in combination with other lipid-lowering medication in children with CKD should be avoided | kdigo-2013-lipids | 33 | p33/narrative/pediatric-statin-regimen | narrative |
| adult-triglyceride-lifestyle | adults-ckd-hypertriglyceridemia | advise therapeutic lifestyle changes; Grade 2D, particularly when fasting triglycerides exceed 5.65 mmol/L (500 mg/dL): dietary modification, weight reduction when overweight, increased physical activity, reduced alcohol, and treatment of hyperglycemia | RENDERED: In adults with CKD ... and hypertriglyceridemia, we suggest that therapeutic lifestyle changes be advised. (2D) ... reasonable to advise patients with high fasting levels of serum TGs (>5.65 mmol/l [>500 mg/dl]) ... dietary modification, weight reduction ... increased physical activity, reducing alcohol intake, and treatment of hyperglycemia | kdigo-2013-lipids | 35 | p35/narrative/adult-triglyceride-tlc | narrative |
| adult-triglyceride-diet | adults-ckd-hypertriglyceridemia | consider dietary fat below 15% of total calories, reduced mono- and disaccharides and total carbohydrate, and fish oils replacing some long-chain triglycerides; use caution when malnutrition is possible | RENDERED: Dietary changes that may reduce serum TGs include a low-fat diet (<15% total calories), reduction of monosaccharide and disaccharide intake, reducing total dietary carbohydrates, and use of fish oils to replace some long-chain TGs; use should be approached judiciously in individuals at risk of malnutrition. | kdigo-2013-lipids | 35 | p35/narrative/adult-triglyceride-diet | narrative |
| adult-fibrate-use | adults-ckd-marked-hypertriglyceridemia | do not use fibrates routinely; a renally adjusted fibrate may be considered only for rare triglycerides above 11.3 mmol/L (1000 mg/dL) after weighing weak evidence and patient preference, and never with a statin | RENDERED: Evidence supporting fibric acid derivatives for prevention of pancreatitis is extremely weak; values and preferences should be considered. They could be considered for rare fasting serum TG >11.3 mmol/l (>1000 mg/dl), must be dose-adjusted for kidney function, and should not be combined with a statin. | kdigo-2013-lipids | 35 | p35/narrative/adult-fibrate-boundary | narrative |
| adult-niacin-use | adults-ckd-hypertriglyceridemia | do not recommend nicotinic acid for severe hypertriglyceridemia because advanced CKD may magnify flushing and hyperglycemia | RENDERED: Nicotinic acid has not been well studied in advanced CKD and therefore is not recommended for treatment of severe hypertriglyceridemia, given the risk of adverse events, especially flushing and hyperglycemia. | kdigo-2013-lipids | 35 | p35/narrative/adult-niacin-boundary | narrative |
| adult-fibrate-cv-prevention | adults-ckd | do not recommend fibrates to reduce cardiovascular risk in CKD | RENDERED: fibric acid derivatives are not recommended to prevent cardiovascular disease in adults with CKD | kdigo-2013-lipids | 36 | p36/narrative/fibrate-cardiovascular-prevention | narrative |
| pediatric-triglyceride-lifestyle | children-ckd-hypertriglyceridemia | advise therapeutic lifestyle changes; Grade 2D, particularly when fasting triglycerides exceed 5.65 mmol/L (500 mg/dL), using dietary modification, weight reduction when overweight, activity, reduced alcohol, and treatment of hyperglycemia | RENDERED: In children with CKD ... and hypertriglyceridemia, we suggest that therapeutic lifestyle changes be advised. (2D) ... high fasting levels of serum TGs (>5.65 mmol/l [>500 mg/dl]) ... dietary modification, weight reduction ... increased physical activity, reducing alcohol intake, and treatment of hyperglycemia | kdigo-2013-lipids | 37 | p37/narrative/pediatric-triglyceride-tlc | narrative |
| pediatric-triglyceride-diet | children-ckd-hypertriglyceridemia | consider fat below 15% of calories, medium-chain triglycerides, and fish oil replacing long-chain triglycerides; use dietary modification judiciously, if at all, in children who are malnourished, and involve a social worker when safe implementation is a concern | RENDERED: a very low-fat diet (<15% total calories), medium-chain TGs, and fish oils to replace some long-chain TGs. Dietary modification should be used judiciously, if at all, in children who are malnourished. Input from a social worker may be helpful if there are concerns that the patient or parents are unable to safely implement TLC. | kdigo-2013-lipids | 37 | p37/narrative/pediatric-triglyceride-diet | narrative |
| pediatric-triglyceride-pharmacotherapy | children-ckd-very-severe-triglycerides | do not use pharmacological treatment routinely; when fasting triglycerides exceed 11.3 mmol/L (1000 mg/dL), treatment may be considered, refer to a pediatric lipid specialist, and evaluate for familial hypertriglyceridemia, lipoprotein-lipase deficiency, or apolipoprotein C-II deficiency | RENDERED: Pharmacological treatment is not recommended routinely. Children with fasting TG >11.3 mmol/l (>1000 mg/dl) should be considered for treatment and referral to a pediatric lipid specialist; familial hypertriglyceridemia, lipoprotein lipase deficiency, and apolipoprotein C-II deficiency should be considered. | kdigo-2013-lipids | 37 | p37/narrative/pediatric-triglyceride-pharmacotherapy | narrative |

## Conflicts

CONFLICT: pediatric-lipid-categories — total cholesterol is acceptable below 4.4 mmol/L (170 mg/dL), borderline 4.4-5.2 mmol/L (170-199 mg/dL), and high above 5.2 mmol/L (at least 200 mg/dL); LDL cholesterol is acceptable below 2.8 mmol/L (110 mg/dL), borderline 2.8-3.3 mmol/L (110-129 mg/dL), and high at least 3.4 mmol/L (130 mg/dL); non-HDL cholesterol is acceptable below 3.1 mmol/L (120 mg/dL), borderline 3.1-3.7 mmol/L (120-144 mg/dL), and high at least 3.8 mmol/L (145 mg/dL)

| quantity | population | values | resolution |
| --- | --- | --- | --- |
| pediatric-statin-initiation | selected-children-severe-ldl | formal KDIGO recommendation: do not initiate a statin or statin/ezetimibe in children younger than 18 years; narrative KDIGO context: selected boys older than 10 years or postmenarchal girls with severely elevated LDL cholesterol and strong preventive preference may be considered for the lowest-dose statin | Preserve both source positions. Treat the formal Grade 2C recommendation as the default and the narrative passage as a narrow, preference-sensitive exception requiring individualized specialist judgment; do not generalize it to all children. |
| dialysis-statin-initiation | adults-dialysis-existing-statin | do not initiate statin-containing treatment after dialysis dependence; continue treatment already in use when dialysis begins, with periodic reassessment | These are complementary timing branches rather than interchangeable actions: treatment status at dialysis initiation selects the branch. |
| adult-fibrate-use | adults-ckd-marked-hypertriglyceridemia | fibrates are not routinely recommended for CKD hypertriglyceridemia; a renally adjusted fibrate may be considered for rare fasting triglycerides above 11.3 mmol/L (1000 mg/dL), never with a statin | Preserve the rare severe-triglyceride exception and the combination prohibition; do not convert consideration into a routine indication. |
| pediatric-lipid-categories | children-ckd | total cholesterol, LDL cholesterol, and non-HDL cholesterol each use distinct acceptable, borderline-high, and high cutoffs | These are complementary analyte-specific category values, not competing thresholds; retain all three and select the row for the measured analyte. |

## Coverage

The bound extraction records **9 marker occurrences comprising 8 unique identifiers**.
They are contents, quick-guide, cross-reference, or worked-example fragments rather than
complete formal recommendations. All formal patient-changing recommendations are retained
from the fully read source as page-bound narrative rows above. Exact recommendation
accounting is **9 = 0 cited + 9 scoped out**.

- `p4/recommendation/1.2` — scoped out: contents-page fragment; no additional patient-action threshold
- `p16/recommendation/1.2` — scoped out: quick-guide cross-reference fragment; the complete follow-up boundary is retained from pp14 and 20
- `p21/recommendation/1.2` — scoped out: Table 2 worked-example fragment; no additional patient-action threshold beyond the retained follow-up rule
- `p21/recommendation/2.1.1` — scoped out: Table 2 worked-example fragment; no additional patient-action threshold beyond the retained age/eGFR statin rule
- `p21/recommendation/2.1.2` — scoped out: Table 2 worked-example fragment; no additional patient-action threshold beyond the retained age/eGFR statin rule
- `p21/recommendation/2.1.3` — scoped out first occurrence: Table 2 diabetes worked-example fragment; no additional patient-action threshold beyond the retained younger-adult statin indications
- `p21/recommendation/2.1.3` — scoped out second occurrence: Table 2 lower-risk worked-example fragment; no additional patient-action threshold beyond the retained younger-adult preference boundary
- `p32/recommendation/6.1` — scoped out: pediatric narrative cross-reference fragment; the complete triglyceride action is retained from p37
- `p32/recommendation/4.1` — scoped out: pediatric narrative cross-reference fragment; the complete statin boundary is retained from pp15 and 33–34

## ADR 0009 disposition

Every page was read. The sheet retains the complete formal recommendations, all numeric
values that define a population, test, treatment, dose, interval, contraindication,
monitoring action, referral, or selected-case exception, and the clinical benefit and harm
boundaries that change counseling. Trial-relative effect estimates without an independent
action are omitted. Table 1 secondary causes, Table 4 CKD-tested doses, and
Table 5 pediatric lipid categories are retained. Table 2's hypothetical patients are
implementation examples rather than additional rules; Table 3's age/eGFR event-rate matrix,
trial-effect estimates, study sizes and follow-up, methods Tables 6–16, research priorities,
administrative matter, disclosures, and references are scoped out because they do not add
an independent patient action. The extraction's nine fragments are individually accounted
for above rather than treated as complete recommendations.
