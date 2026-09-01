# Kidney transplantation candidate evaluation — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](../../../../../reference/thresholds/README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kdigo-2020 | KDIGO | KDIGO/KDIGO-2020-Transplant-Candidate-Guideline | guideline | 2020 | 2020 | https://doi.org/10.1097/TP.0000000000003136 | stated | bound |

## Scope

**Read:** the complete 106-page guideline, including front matter, abbreviations,
summary recommendations, methods, all 19 detailed clinical sections, tables and
figures, evidence discussions, implementation considerations, research
recommendations, references, and contributor disclosures. The source contains 268
unique source-numbered candidate-evaluation actions; they were read in both their
summary and detailed settings. The bound recommendation record is a deliberately
narrow 21-occurrence extraction: ten HCV cross-reference markers appear twice and
one cognitive-function cross-reference mention appears once. It is therefore not a
complete inventory of the guideline's recommendations.

**Not read:** nothing in the source page range. Reference pages were inspected for
scope and retired by class because they contain citations rather than clinical
prose.

**Scoped out under ADR 0009's numeric decision-point rule:** bibliographic years,
study sizes, prevalence, event rates, effect estimates, confidence intervals,
historical practice, and research-method numbers that do not alter candidate care.
Qualitative source actions without a numeric cutoff are retained in the clinical
action inventory below; exact bound-record disposition is in `## Coverage`.

**Source: `kdigo-2020`**

| span | pages | read |
| --- | --- | --- |
| title, work group, abbreviations, tables, introduction, and summary preamble | 1-13 | read 2026-09-01; blind 2026-09-01 |
| summary recommendations, sections 1-19 | 14-25 | yes |
| methods, evidence grading, and guideline development | 26-35 | read 2026-09-01; blind 2026-09-01 |
| detailed sections 1-4 | 36-41 | read 2026-09-01; blind 2026-09-01 |
| detailed sections 5-8 | 42-49 | yes |
| detailed section 9, cause of kidney failure | 50-57 | yes |
| detailed section 10, infections | 58-65 | yes |
| detailed sections 11-13, malignancy, pulmonary, and cardiac disease | 66-74 | yes |
| detailed sections 14-17, peripheral arterial, neurologic, gastrointestinal, and hematologic disease | 75-79 | yes |
| detailed sections 18-19, mineral-bone and immunologic assessment | 80-86 | read 2026-09-01; blind 2026-09-01 |
| references | 87-101 | exempt: references contain citations rather than clinical prose |
| work-group biographies, disclosures, acknowledgments, and administrative material | 102-106 | read 2026-09-01; blind 2026-09-01 |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| advanced-ckd | adults and children with CKD G4-G5 who are expected to reach ESKD |
| adult-preemptive-candidate | adult candidate being considered for preemptive transplantation |
| pediatric-preemptive-candidate | pediatric candidate being considered for preemptive transplantation |
| tobacco-user-candidate | candidate who uses tobacco products |
| heavy-tobacco-user-candidate | current or former heavy tobacco user with at least 30 pack-years |
| candidate-on-antiplatelet | candidate receiving a non-aspirin antiplatelet agent |
| pediatric-nephrectomy-candidate | pediatric candidate being assessed for native nephrectomy |
| hiv-positive-candidate | candidate with HIV infection |
| hcv-positive-candidate | candidate with HCV infection |
| hcv-positive-living-donor-candidate | HCV-positive candidate with an identified living kidney donor |
| hcv-nat-positive-candidate | HCV NAT-positive candidate who may receive an HCV-positive deceased-donor kidney |
| infection-screening-candidate | kidney transplant candidate undergoing initial or repeat infection screening |
| vaccine-candidate | kidney transplant candidate whose vaccination status is being completed |
| cancer-history-candidate | candidate in complete remission after cancer treatment |
| rcc-risk-candidate | candidate at increased risk for renal cell carcinoma |
| pulmonary-hypertension-candidate | candidate with pulmonary hypertension detected by echocardiography or right-heart catheterization |
| severe-heart-failure-candidate | candidate with uncorrectable symptomatic NYHA class III/IV heart disease |
| neurologic-event-candidate | candidate after stroke or transient ischemic attack |
| pancreatitis-candidate | candidate after acute pancreatitis |
| hla-sensitized-candidate | candidate with HLA sensitization or sensitizing events |
| nonadherence-graft-loss-candidate | candidate seeking relisting or retransplantation after graft loss due to overt nonadherence |
| obese-candidate | transplant candidate assessed by BMI or waist-to-hip ratio |
| lupus-nephritis-candidate | candidate whose kidney failure was caused by lupus nephritis |
| aps-candidate | candidate with antiphospholipid syndrome |
| anti-gbm-candidate | candidate with anti-GBM disease |
| high-risk-ahus-candidate | candidate with a complement-regulation abnormality conferring high recurrent aHUS risk |
| myeloma-midd-candidate | candidate with multiple myeloma, LCDD, HCDD, or LHCDD |
| al-amyloidosis-candidate | candidate with AL amyloidosis |
| aa-amyloidosis-candidate | candidate with AA amyloidosis |
| active-tb-candidate | candidate receiving therapy for active tuberculosis |
| latent-tb-candidate | candidate with latent tuberculosis infection |
| anti-hbc-positive-candidate | anti-HBc-positive, HBsAg-negative candidate |
| cancer-screening-candidate | transplant candidate undergoing age- and risk-appropriate cancer screening |
| active-malignancy-candidate | candidate with active malignancy being assessed for a stated indolent exception |
| post-mi-or-coronary-intervention-candidate | candidate after myocardial infarction, balloon angioplasty, or coronary stent insertion |
| coronary-stent-candidate | candidate with a coronary stent continuing perioperative aspirin |
| adpkd-aneurysm-candidate | candidate with ADPKD and an identified intracranial aneurysm |
| adpkd-family-history-no-aneurysm | candidate with an intracranial-aneurysm family history but no aneurysm on screening |
| ulcer-symptom-candidate | candidate with symptoms suggesting active peptic ulcer disease |
| cholecystitis-history-candidate | candidate with a history of cholecystitis |

## Quantities

| key | verbatim |
| --- | --- |
| referral-gfr-and-lead-time | kidney transplant education and referral threshold and lead time |
| preemptive-transplant-gfr | GFR threshold for preemptive transplantation |
| tobacco-abstinence-and-screening | abstinence interval and heavy-use imaging threshold |
| antiplatelet-hold | preoperative non-aspirin antiplatelet interruption |
| pediatric-nephrectomy-output | urine-output threshold supporting native nephrectomy consideration |
| hiv-eligibility | immune and opportunistic-infection stability criteria |
| hcv-testing-sequence | HCV screening and confirmatory testing sequence |
| hcv-transplant-eligibility | kidney transplantation eligibility despite HCV infection |
| hcv-preacceptance-liver-assessment | preacceptance HCV liver-disease and portal-hypertension assessment |
| hcv-compensated-cirrhosis-branch | isolated kidney transplantation for compensated HCV cirrhosis without portal hypertension |
| hcv-decompensated-cirrhosis-branch | combined liver-kidney transplantation and post-transplant HCV treatment for decompensated cirrhosis |
| hcv-treatment-selection-factors | factors controlling HCV treatment before versus after transplantation |
| hcv-daa-treatment-eligibility | DAA treatment eligibility before or after transplantation |
| hcv-living-donor-treatment-timing | HCV treatment timing with an identified living donor |
| hcv-positive-donor-post-treatment | HCV-positive donor use followed by post-transplant treatment |
| hbv-screening-tests | HBV screening tests in the linked viral branch |
| hcv-figure-wait-time | Figure 3 short versus long expected wait-time branch |
| annual-viral-repeat-testing | annual and transplant-time repeat testing for HIV, HCV, and HBV |
| transplant-time-serology-repeat | transplant-time repeat serology for CMV, EBV, HSV, VZV, and MMR |
| post-vaccine-and-tb-repeat-testing | post-vaccination VZV/MMR and exposure-qualified TB repeat testing |
| live-vaccine-delay | minimum interval from live vaccine to transplantation |
| pneumococcal-influenza-vaccine-series | pneumococcal and influenza vaccine schedule |
| hepatitis-vaccine-series | hepatitis A and B vaccine schedule and anti-HBs booster threshold |
| mmr-varicella-zoster-vaccine-series | MMR, varicella, and recombinant zoster vaccine schedule |
| rcc-screening-risk | dialysis-duration and other RCC-risk triggers |
| cancer-no-wait-exceptions | cancers requiring no waiting time after curative treatment |
| breast-colorectal-bladder-wait | breast, colorectal, and invasive-bladder cancer waiting times |
| kidney-uterine-cervical-wait | kidney, uterine, and cervical cancer waiting times |
| lung-testicular-melanoma-wait | lung, testicular, and melanoma waiting times or contraindication |
| prostate-cancer-wait | prostate-cancer waiting time by Gleason score |
| thyroid-cancer-wait | thyroid-cancer waiting time or contraindication by stage/type |
| lymphoma-ptld-wait | lymphoma and post-transplant lymphoproliferative-disease waiting times |
| cardiac-screening | dialysis duration and pulmonary-pressure evaluation thresholds |
| severe-cardiac-exclusion | left-ventricular ejection-fraction and symptom boundary |
| neurologic-event-wait | waiting period after stroke or TIA |
| pancreatitis-wait | minimum post-pancreatitis symptom-free interval |
| hla-monitoring | timing of HLA-antibody testing |
| nonadherence-relisting-demonstration | minimum demonstrated adherence before relisting or retransplantation |
| obesity-intervention-boundaries | BMI and waist-to-hip intervention and caution boundaries |
| lupus-quiescence | lupus activity required before transplantation |
| aps-activation-management | APS quiescence and anticoagulation at waitlist activation |
| anti-gbm-serologic-remission | anti-GBM antibody boundary for transplantation |
| ahus-high-risk-transplant-condition | treatment or combined-organ condition for high-risk aHUS |
| myeloma-curative-remission | curative-treatment and stable-remission condition for multiple myeloma |
| midd-curative-remission | curative-treatment and stable-remission condition for LCDD, HCDD, and LHCDD |
| al-amyloidosis-eligibility | extrarenal, curative-treatment, and remission conditions for AL amyloidosis |
| aa-amyloidosis-eligibility | underlying-cause and extrarenal conditions for AA amyloidosis |
| active-tb-transplant-timing | active-TB treatment and response boundary for transplantation |
| latent-tb-treatment-deadline | latest post-transplant start for latent-TB therapy |
| hbv-post-transplant-monitoring | minimum HBsAg and HBV-DNA monitoring duration |
| hpv-vaccine-series | HPV dose schedule and age range |
| meningococcal-vaccine-series | quadrivalent and serogroup-B meningococcal schedules |
| zoster-vaccine-boundaries | live and recombinant zoster age and sequencing boundaries |
| hbv-vaccine-dose-and-response | dialysis-dose HBV vaccine and anti-HBs response timing |
| inactivated-vaccine-immunity | time needed to establish immunity after an inactivated vaccine |
| breast-screening-boundaries | breast-screening start choice, interval, and longevity boundary |
| colorectal-screening-boundaries | colorectal test intervals and stopping boundaries |
| cervical-screening-boundaries | cervical screening start, intervals, and stopping age |
| lung-screening-boundaries | lung LDCT age, pack-year, and quit-time boundaries |
| prostate-screening-boundaries | preference-sensitive prostate screening age and stopping age |
| active-renal-tumor-exception | incidental renal-tumor size exception during active malignancy evaluation |
| post-mi-and-pci-delay | elective-surgery delay after MI or coronary intervention |
| coronary-stent-aspirin-dose | aspirin continuation dose after coronary stenting |
| intracranial-aneurysm-reevaluation | identified aneurysm reevaluation and negative family-history rescreening intervals |
| peptic-ulcer-diagnostic-action | endoscopy and H. pylori testing for ulcer symptoms |
| post-cholecystitis-action | cholecystectomy before transplantation after cholecystitis |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| referral-gfr-and-lead-time | advanced-ckd | CKD G4-G5, GFR <30 mL/min/1.73 m2, expected to reach ESKD: inform, educate, and consider transplantation; refer 6-12 months before anticipated dialysis | "RENDERED: All patients with CKD G4-G5 (GFR < 30 ml/min/1.73 m2) who are expected to reach ESKD should be informed of, educated about, and considered for kidney transplantation; refer potential kidney transplant candidates for evaluation at least 6 to 12 months before anticipated dialysis initiation" | kdigo-2020 | p14 | p14/narrative/referral-gfr-and-lead-time | narrative |
| preemptive-transplant-gfr | adult-preemptive-candidate | consider preemptive transplantation when GFR is <10 mL/min/1.73 m2 or earlier with symptoms | "RENDERED: We suggest that preemptive transplantation in adults be considered when the GFR is < 10 ml/min/1.73 m2 or earlier with symptoms" | kdigo-2020 | p14 | p14/narrative/adult-preemptive-gfr | narrative |
| preemptive-transplant-gfr | pediatric-preemptive-candidate | consider preemptive transplantation when GFR is <15 mL/min/1.73 m2 or earlier with symptoms | "RENDERED: We suggest that preemptive transplantation in children be considered when the GFR is < 15 ml/min/1.73 m2 or earlier with symptoms" | kdigo-2020 | p14 | p14/narrative/pediatric-preemptive-gfr | narrative |
| tobacco-abstinence-and-screening | tobacco-user-candidate | abstain at least 1 month before waitlisting or living-donor transplantation and continue abstinence indefinitely | "RENDERED: We recommend that candidates abstain from tobacco use, at a minimum 1 month prior to waitlisting or living donor transplantation, and continue abstinence after transplantation" | kdigo-2020 | p15 | p15/narrative/tobacco-abstinence | narrative |
| tobacco-abstinence-and-screening | heavy-tobacco-user-candidate | >=30 pack-years: screen for occult lung cancer with chest CT according to local guidance | "RENDERED: We suggest chest computed tomography for current or former heavy tobacco users (>= 30 pack-years) as per local guidelines to screen for occult lung cancer" | kdigo-2020 | p15 | p15/narrative/heavy-tobacco-ct | narrative |
| antiplatelet-hold | candidate-on-antiplatelet | stop non-aspirin antiplatelet agents 5 days before living-donor transplantation and during the perioperative period for deceased-donor transplantation unless contraindicated | "RENDERED: We suggest that non-aspirin antiplatelet agents be stopped 5 days prior to living donor transplantation and during the perioperative period for deceased donor transplantation, unless cessation is contraindicated" | kdigo-2020 | p16 | p16/narrative/nonaspirin-antiplatelet-hold | narrative |
| pediatric-nephrectomy-output | pediatric-nephrectomy-candidate | consider native nephrectomy for urine output >2.5 mL/kg/hour or heavy proteinuria with severe hypoalbuminemia | "RENDERED: We suggest that native nephrectomy be considered in pediatric candidates with large urine volumes (> 2.5 ml/kg/hour) or heavy proteinuria with severe hypoalbuminemia" | kdigo-2020 | p16 | p16/narrative/pediatric-nephrectomy-output | narrative |
| hiv-eligibility | hiv-positive-candidate | CD4 count >=200/microliter and stable for 3 months, undetectable viral load, and no opportunistic infection in the prior 6 months, with adherence and defined neurologic exclusions | "RENDERED: HIV positive transplant candidates should be considered if: (a) CD4+ T-cell count is >= 200/microliter and stable for the past 3 months; (b) the viral load is undetectable; (c) no opportunistic infections in the past 6 months; (d) compliant with antiretroviral regimen; (e) no cognitive impairment; (f) no history of progressive multifocal leukoencephalopathy; and (g) no history of central nervous system lymphoma." | kdigo-2020 | p59 | p59/narrative/hiv-eligibility | narrative |
| hcv-testing-sequence | hcv-positive-candidate | use immunoassay followed by NAT when immunoassay is positive | "RENDERED: 10.5.2.2: We recommend using an immunoassay followed by nucleic acid testing (NAT) if immunoassay is positive (1A)." | kdigo-2020 | p60 | p60/recommendation/1.1.4 |  |
| hcv-transplant-eligibility | hcv-positive-candidate | kidney transplantation is the preferred therapeutic option for CKD G5 irrespective of HCV infection | "RENDERED: 10.5.2.3: We recommend kidney transplantation as the best therapeutic option for patients with CKD G5 irrespective of presence of HCV infection (1A)." | kdigo-2020 | p60 | p60/recommendation/1.1.1.1 |  |
| hcv-preacceptance-liver-assessment | hcv-positive-candidate | evaluate liver-disease severity and portal hypertension before acceptance | "We suggest that all candidates with HCV infection be evaluated for severity of liver disease and presence of portal hypertension" | kdigo-2020 | p60 | p60/recommendation/4.1.1 |  |
| hcv-compensated-cirrhosis-branch | hcv-positive-candidate | compensated cirrhosis without portal hypertension: isolated kidney transplantation | "RENDERED: 10.5.2.4.1: We recommend that patients with HCV and compensated cirrhosis (without portal hypertension) undergo isolated kidney transplantation (1B)." | kdigo-2020 | p60 | p60/recommendation/4.1.2 |  |
| hcv-decompensated-cirrhosis-branch | hcv-positive-candidate | decompensated cirrhosis: refer for combined liver-kidney transplantation and defer HCV treatment until after transplantation | "RENDERED: 10.5.2.4.2: We recommend referring patients with HCV and decompensated cirrhosis for combined liver-kidney transplantation (1B) and deferring HCV treatment until after transplantation (1D)." | kdigo-2020 | p60 | p60/recommendation/4.1.2.1 |  |
| hcv-treatment-selection-factors | hcv-positive-candidate | base treatment before versus after transplantation on donor type, wait time, center policy, HCV genotype, and liver fibrosis | "RENDERED: 10.5.2.5: Timing of HCV treatment in relation to kidney transplantation (before vs. after) should be based on donor type (living vs. deceased donor), waitlist times by donor type, center-specific policies governing the use of kidneys from HCV-infected deceased donors, HCV genotype, and severity of liver fibrosis (Not Graded)." | kdigo-2020 | p60 | p60/recommendation/4.1.2.2 |  |
| hcv-daa-treatment-eligibility | hcv-positive-candidate | consider DAA therapy either before or after transplantation | "RENDERED: 10.5.2.5.1: We recommend that all patients with HCV who are candidates for kidney transplantation be considered for direct-acting antiviral (DAA) therapy, either before or after transplantation (1A)." | kdigo-2020 | p60 | p60/recommendation/4.1.3 |  |
| hcv-living-donor-treatment-timing | hcv-positive-living-donor-candidate | treat before or after transplantation according to genotype and anticipated timing | "RENDERED: 10.5.2.5.2: We suggest that candidates with HCV with a living kidney donor can be considered for treatment before or after transplantation according to HCV genotype and anticipated timing of transplantation (2B)." | kdigo-2020 | p60 | p60/recommendation/4.1.3.1 |  |
| hcv-positive-donor-post-treatment | hcv-nat-positive-candidate | if an HCV-positive kidney improves access, transplant with that kidney and treat HCV afterward | "RENDERED: 10.5.2.5.3: We suggest that if receiving a kidney from an HCV-positive donor improves the chances for transplantation, the HCV NAT-positive patient can undergo transplantation with an HCV-positive kidney and be treated for HCV infection after transplantation (2B)." | kdigo-2020 | p60 | p60/recommendation/4.1.3.2 |  |
| hbv-screening-tests | hcv-positive-candidate | screen for HBV with HBsAg, anti-HBs, and anti-HBc as the next linked viral branch | "We recommend screening for HBV infection with HBsAg, anti-HBs, and anti-HBc" | kdigo-2020 | p61 | p61/recommendation/4.1.3.3 |  |
| hcv-figure-wait-time | hcv-positive-candidate | Figure 3 deceased-donor branch: expected wait <24 weeks with possible rapid HCV-positive kidney favors no pretreatment; expected wait >24 weeks without rapid HCV-positive kidney favors treatment before transplantation | "RENDERED: FIGURE 3. Algorithm for the evaluation of kidney transplant candidates with HCV; Short time to transplantation < 24 weeks; Expected time to transplantation > 24 weeks; No treatment prior to transplantation; Treatment before transplantation" | kdigo-2020 | p61 | p61/narrative/hcv-figure-3-wait-time | narrative |
| annual-viral-repeat-testing | infection-screening-candidate | if HIV, HCV, or HBV initial testing is negative, repeat annually and at transplantation | "RENDERED: HIV, HCV, HBV: If negative, repeat annually and at time of transplant" | kdigo-2020 | p60 | p60/narrative/table-11-annual-viral-repeat | narrative |
| transplant-time-serology-repeat | infection-screening-candidate | if CMV, EBV, HSV, VZV, or MMR serology is negative, repeat at transplantation | "RENDERED: CMV, EBV, HSV, VZV, Measles, Mumps, Rubella: If negative, repeat at time of transplant" | kdigo-2020 | p60 | p60/narrative/table-11-transplant-time-serology | narrative |
| post-vaccine-and-tb-repeat-testing | infection-screening-candidate | negative VZV or MMR serology: also repeat 4 weeks after vaccination; tuberculosis testing repeats annually only with ongoing exposure risk | "RENDERED: VZV and Measles, Mumps, Rubella: repeat 4 weeks post-vaccination; Tuberculosis: Annually if ongoing risk of exposure" | kdigo-2020 | p60 | p60/narrative/table-11-vaccine-and-tb-retesting | narrative |
| live-vaccine-delay | vaccine-candidate | complete live vaccines and delay transplantation for at least 4 weeks after the final dose | "RENDERED: We recommend that live vaccines be completed prior to kidney transplantation and transplantation should be delayed for at least 4 weeks after the final dose" | kdigo-2020 | p21 | p21/narrative/live-vaccine-delay | narrative |
| pneumococcal-influenza-vaccine-series | vaccine-candidate | PCV13 once then PPV23 after at least 8 weeks; repeat PPV23 after five years; influenza annually | "RENDERED: Pneumococcal Vaccination: PCV13, PPV23; One dose of PCV13 followed by one dose of PPV23 with a minimum of 8-week interval in between; One booster of PPV23 five years from previous PPV23; Influenza: One dose annually" | kdigo-2020 | p64 | p64/narrative/table-12-pneumococcal-influenza | narrative |
| hepatitis-vaccine-series | vaccine-candidate | hepatitis B at 0, 1, and 6 months; monitor anti-HBs annually and boost if <10 IU/mL; hepatitis A at 0 and 2 months, repeat if no response | "RENDERED: Hepatitis B: Three doses at 0, 1, 6 months; Monitor annually and give booster dose if titers decline <10 IUs/ml; Hepatitis A: Two doses at 0, 2 months" | kdigo-2020 | p64 | p64/narrative/table-12-hepatitis-vaccines | narrative |
| mmr-varicella-zoster-vaccine-series | vaccine-candidate | MMR and varicella: 2 doses 4 weeks apart; recombinant zoster age >=50 and VZV IgG-positive: 2 doses at 0 and 2-6 months | "RENDERED: Measles, Mumps, Rubella: Two doses given 4 weeks apart; Varicella: Two doses given 4 weeks apart; Shingles (Herpes Zoster Subunit): Two doses at 0, 2-6 months for those age >= 50 years and VZV IgG positive" | kdigo-2020 | p64 | p64/narrative/table-12-live-zoster-series | narrative |
| rcc-screening-risk | rcc-risk-candidate | screen by ultrasonography when at increased risk, including >=3 years on dialysis, family history, acquired cystic disease, or analgesic nephropathy | "RENDERED: We suggest screening candidates at increased risk for renal cell carcinoma (eg >= 3 years dialysis, family history of renal cancer, acquired cystic disease or analgesic nephropathy) with ultrasonography" | kdigo-2020 | p21 | p21/narrative/rcc-screening-risk | narrative |
| cancer-no-wait-exceptions | cancer-history-candidate | no waiting time after curative treatment for basal/squamous skin cancer, melanoma in situ, RCC <3 cm, prostate Gleason <=6, low-grade thyroid papillary/follicular <2 cm, in situ cancers, or superficial bladder cancer | "RENDERED: no waiting time for basal and squamous cell carcinoma of the skin; melanoma in situ; small renal cell carcinoma (< 3 cm); prostate cancer (Gleason score <= 6); carcinoma in situ; thyroid cancer papillary or follicular < 2 cm of low grade histology; and superficial bladder cancer" | kdigo-2020 | p21 | p21/narrative/no-cancer-wait | narrative |
| breast-colorectal-bladder-wait | cancer-history-candidate | breast early >=2 years, advanced >=5; colorectal Dukes A/B >=2, C 2-5, D >=5; invasive bladder >=2 years | "RENDERED: Breast Early At least 2 years; Advanced At least 5 years; Colorectal Dukes A/B At least 2 years; Duke C 2-5 years; Duke D At least 5 years; Bladder Invasive At least 2 years" | kdigo-2020 | p68 | p68/narrative/table-14-breast-colorectal-bladder | narrative |
| kidney-uterine-cervical-wait | cancer-history-candidate | kidney incidentaloma <3 cm none, early >=2 years, large/invasive >=5; uterine or cervical localized >=2 and invasive >=5 years | "RENDERED: Kidney Incidentaloma (< 3 cm) No waiting time; Early At least 2 years; Large and invasive At least 5 years; Uterine Localized At least 2 years, Invasive At least 5 years; Cervical Localized At least 2 years, Invasive At least 5 years" | kdigo-2020 | p68 | p68/narrative/table-14-kidney-uterine-cervical | narrative |
| lung-testicular-melanoma-wait | cancer-history-candidate | lung localized 2-5 years; testicular localized >=2 and invasive 2-5; melanoma localized >=5 and invasive contraindicated | "RENDERED: Lung Localized 2-5 years; Testicular Localized At least 2 years, Invasive 2-5 years; Melanoma Localized At least 5 years, Invasive Contraindicated" | kdigo-2020 | p68 | p68/narrative/table-14-lung-testicular-melanoma | narrative |
| prostate-cancer-wait | cancer-history-candidate | prostate Gleason <=6 none, Gleason 7 >=2 years, Gleason 8-10 >=5 years | "RENDERED: Prostate Gleason <=6 No waiting time; Gleason 7 At least 2 years; Gleason 8-10 At least 5 years" | kdigo-2020 | p68 | p68/narrative/table-14-prostate | narrative |
| thyroid-cancer-wait | cancer-history-candidate | thyroid stage 1 none, stage 2 >=2 years, stage 3 >=5 years, stage 4 or anaplastic contraindicated | "RENDERED: Thyroid Stage 1 No waiting time; Stage 2 At least 2 years; Stage 3 At least 5 years; Stage 4 Contraindicated; Anaplastic Contraindicated" | kdigo-2020 | p68 | p68/narrative/table-14-thyroid | narrative |
| lymphoma-ptld-wait | cancer-history-candidate | Hodgkin or non-Hodgkin lymphoma localized >=2, regional 3-5, distant >=5 years; post-transplant lymphoproliferative disease nodal >=2 and extranodal/cerebral >=5 years | "RENDERED: Hodgkin Lymphoma and Non-Hodgkin Lymphoma: Localized At least 2 years, Regional 3-5 years, Distant At least 5 years; Post-transplant lymphoproliferative disease: Nodal At least 2 years, Extranodal and cerebral At least 5 years" | kdigo-2020 | p68 | p68/narrative/table-14-lymphoma | narrative |
| cardiac-screening | pulmonary-hypertension-candidate | echocardiography for candidates on dialysis for at least two years or with pulmonary-hypertension risk; cardiology if estimated pulmonary artery systolic pressure >45 mm Hg; right-heart pressure >60 mm Hg does not automatically exclude | "RENDERED: asymptomatic candidates who have been on dialysis for at least two years or have risk factors for pulmonary hypertension undergo echocardiography; pulmonary artery systolic pressure is greater than 45 mm Hg be assessed by a cardiologist; right heart catheterization with a systolic pulmonary arterial pressure greater than 60 mm Hg should not be excluded" | kdigo-2020 | p22 | p22/narrative/pulmonary-hypertension-thresholds | narrative |
| severe-cardiac-exclusion | severe-heart-failure-candidate | uncorrectable symptomatic NYHA III/IV disease, including LVEF <30%, severe CAD, or severe valvular disease: exclude from kidney-alone transplantation unless mitigating factors support survival | "RENDERED: We suggest that patients with uncorrectable, symptomatic NYHA III/IV heart disease (severe CAD; left ventricular dysfunction with ejection fraction < 30%; severe valvular disease) be excluded from kidney transplantation unless there are mitigating factors" | kdigo-2020 | p22 | p22/narrative/severe-cardiac-exclusion | narrative |
| neurologic-event-wait | neurologic-event-candidate | wait at least 6 months after stroke or 3 months after TIA | "We suggest waiting at least 6 months after a stroke or 3 months after a transient ischemic attack" | kdigo-2020 | p23 | p23/narrative/stroke-tia-wait | narrative |
| pancreatitis-wait | pancreatitis-candidate | delay transplantation until at least 3 months after symptoms resolve | "RENDERED: We suggest candidates with acute pancreatitis be excluded from kidney transplantation for at least 3 months after symptoms have resolved" | kdigo-2020 | p23 | p23/narrative/pancreatitis-wait | narrative |
| hla-monitoring | hla-sensitized-candidate | test HLA antibodies at evaluation, regularly before transplantation, and after sensitizing or other clinical events that may change antibody status | "RENDERED: We recommend HLA antibody testing at transplant evaluation, at regular intervals prior to transplantation and after a sensitizing event or other clinical event that can impact the panel reactive antibody" | kdigo-2020 | p25 | p25/narrative/hla-antibody-monitoring | narrative |
| nonadherence-relisting-demonstration | nonadherence-graft-loss-candidate | document adherence to dialysis, laboratory testing, appointments, medications, diet, and phosphate binders for at least 6 months before successful relisting or retransplantation | "RENDERED: FIGURE 2. Reevaluation protocol after graft loss to nonadherence. Letter from dialysis center or treating nephrologist documenting adherence (eg, diet, phosphate binders, attendance) for at least 6 months; Successful completion requires: Relisting or retransplant" | kdigo-2020 | p45 | p45/narrative/nonadherence-relisting-demonstration | narrative |
| obesity-intervention-boundaries | obese-candidate | BMI >=35 kg/m2: consider dietary or bariatric intervention; BMI >=40 kg/m2: approach transplantation with caution; obesity by waist-to-hip ratio is >0.85 for women or >0.9 for men | "RENDERED: class II or class III obesity (BMI >= 35 kg/m2) should be considered for intervention such as dietary counseling or bariatric surgery; Transplantation in patients with a BMI >= 40 kg/m2 should be approached with caution; Waist-to-hip ratios > 0.85 for women or > 0.9 for men is considered obese" | kdigo-2020 | p47 | p47/narrative/obesity-intervention-boundaries | narrative |
| lupus-quiescence | lupus-nephritis-candidate | lupus activity should be clinically quiescent on no or minimal immunosuppression before transplantation | "RENDERED: 9.7.2: We recommend that lupus activity should be clinically quiescent on no or minimal immunosuppression prior to transplantation (1D)." | kdigo-2020 | p53 | p53/narrative/lupus-quiescence | narrative |
| aps-activation-management | aps-candidate | APS should be clinically quiescent before transplantation and anticoagulation such as aspirin or warfarin should continue when the candidate is activated on the waitlist | "RENDERED: 9.8.2: We suggest that APS should be clinically quiescent prior to transplantation (2D). 9.8.3: Continue anticoagulation (eg, aspirin, warfarin) at the time of activation on the transplant waitlist (Not Graded)." | kdigo-2020 | p53 | p53/narrative/aps-activation-management | narrative |
| anti-gbm-serologic-remission | anti-gbm-candidate | perform transplantation only when anti-GBM antibodies are undetectable | "RENDERED: 9.10.2: We recommend that anti-GBM antibody titers be measured in candidates and that transplantation is only performed when antibodies are undetectable (1D)." | kdigo-2020 | p54 | p54/narrative/anti-gbm-serologic-remission | narrative |
| ahus-high-risk-transplant-condition | high-risk-ahus-candidate | do not proceed with kidney transplantation unless a complement inhibitor can be administered or combined liver-kidney transplantation can be performed | "RENDERED: 9.11.3.1: We recommend that if the candidate has an abnormality in complement regulation placing them at high risk of recurrence, kidney transplantation should not proceed unless a complement inhibitor can be administered or combined liver-kidney transplant can be performed (1B)." | kdigo-2020 | p54 | p54/narrative/ahus-high-risk-condition | narrative |
| myeloma-curative-remission | myeloma-midd-candidate | multiple myeloma: exclude unless potentially curative treatment was received and stable remission achieved | "RENDERED: 9.13.1.1: We suggest that candidates with multiple myeloma be excluded from kidney transplantation unless they have received a potentially curative treatment regimen and are in stable remission (2D)." | kdigo-2020 | p54 | p54/narrative/myeloma-remission | narrative |
| midd-curative-remission | myeloma-midd-candidate | LCDD, HCDD, or LHCDD: exclude unless potentially curative treatment was received and stable remission achieved | "RENDERED: 9.13.2 Monoclonal immunoglobulin deposition disease (MIDD): candidates with light chain deposition disease (LCDD), heavy chain deposition disease (HCDD), or light and heavy chain deposition disease (LHCDD) be excluded from kidney transplantation unless they have received a potentially curative treatment regimen and are in stable remission (2D)." | kdigo-2020 | p55 | p55/narrative/midd-remission | narrative |
| al-amyloidosis-eligibility | al-amyloidosis-candidate | exclude unless extrarenal disease is minimal, a potentially curative regimen was received, and stable remission was achieved | "RENDERED: 9.13.3.1: We suggest that candidates with AL amyloidosis be excluded from kidney transplantation unless they have minimal extrarenal disease (eg, cardiac amyloid), have received a potentially curative treatment regimen and are in stable remission (2D)." | kdigo-2020 | p55 | p55/narrative/al-amyloidosis-eligibility | narrative |
| aa-amyloidosis-eligibility | aa-amyloidosis-candidate | do not exclude after adequate treatment of the underlying cause and in the absence of severe extrarenal organ involvement | "RENDERED: 9.14.1: We recommend not excluding candidates with AA amyloidosis from kidney transplantation after adequate treatment of the underlying cause and in the absence of severe extrarenal organ involvement (1D)." | kdigo-2020 | p56 | p56/narrative/aa-amyloidosis-eligibility | narrative |
| active-tb-transplant-timing | active-tb-candidate | transplantation can occur after 3-6 months of active-TB therapy only with culture negativity plus clinical and radiologic improvement; otherwise complete treatment beforehand when feasible | "RENDERED: transplantation can successfully occur after 3-6 months of therapy for active TB with completion of therapy in the post-transplant setting. At a minimum, the patient should be documented as culture-negative, and have clinical as well as radiologic improvement." | kdigo-2020 | p59 | p59/narrative/active-tb-transplant-timing | narrative |
| latent-tb-treatment-deadline | latent-tb-candidate | if not started before transplantation, institute latent-TB therapy no later than 1-2 weeks after transplantation | "RENDERED: therapy for latent TB should be instituted no later than 1-2 weeks post-transplant if it was not started in the pre-transplant period" | kdigo-2020 | p59 | p59/narrative/latent-tb-treatment-deadline | narrative |
| hbv-post-transplant-monitoring | anti-hbc-positive-candidate | plan HBsAg and HBV-DNA monitoring for a minimum of 1 year after transplantation | "RENDERED: 10.5.3.5.2: We suggest that anti-HBc antibody positive (HBsAg negative) patients have a plan in place for post-transplant monitoring of HBsAg and HBV DNA for a minimum of 1-year post-transplantation (2C)." | kdigo-2020 | p62 | p62/narrative/hbv-post-transplant-monitoring | narrative |
| hpv-vaccine-series | vaccine-candidate | HPV vaccine: 3-dose schedule for males and females age 9-45 years if not previously given | "RENDERED: Human papillomavirus vaccine is inactivated and can be given using the 3-dose schedule to males and females over age 9 years; Table 12 specifies ages 9 to 45 and no boosters." | kdigo-2020 | p64 | p64/narrative/table-12-hpv-series | narrative |
| meningococcal-vaccine-series | vaccine-candidate | quadrivalent meningococcal conjugate: 2 doses 8 weeks apart and repeat one dose every 5 years while at risk; give serogroup-B vaccine when eculizumab is planned | "RENDERED: Meningococcal quadrivalent conjugate (Serogroups A,C,Y,W-135): 2 doses given 8 weeks apart; repeat one dose every 5 years in patients at risk. Meningococcal B vaccine: one dose if planned use of eculizumab." | kdigo-2020 | p64 | p64/narrative/table-12-meningococcal-series | narrative |
| zoster-vaccine-boundaries | vaccine-candidate | VZV-IgG-positive candidate age >=50 years: recombinant zoster 2 doses at 0 and 2-6 months or live zoster once; if live zoster was already given, recombinant vaccine may be given at least 1 year later | "RENDERED: Shingles (Herpes Zoster Subunit): 2 doses at 0, 2-6 months for those age >= 50 years and VZV IgG positive. Shingles (Herpes Zoster Live): one dose in those age >= 50 years and VZV IgG positive. If the live vaccine has already been administered, the candidate can be reimmunized with the inactivated vaccine a minimum of 1 year after the live vaccine." | kdigo-2020 | p64 | p64/narrative/table-12-zoster-boundaries | narrative |
| hbv-vaccine-dose-and-response | vaccine-candidate | use 40 micrograms dialysis-dose HBV vaccine in a 3-dose series and measure anti-HBs 4-6 weeks after completion | "RENDERED: A 40 microgram preparation ('dialysis dose') should be used with a 3-dose interval. Anti-HBs titer should be measured 4-6 weeks after series completion." | kdigo-2020 | p64 | p64/narrative/hbv-vaccine-dose-response | narrative |
| inactivated-vaccine-immunity | vaccine-candidate | no pretransplant wait is required after an inactivated vaccine, but at least 2 weeks is needed to establish immunity | "RENDERED: For inactivated vaccines, no specific wait period is required pre-transplantation; however, at least 2 weeks is required for establishment of vaccine immunity." | kdigo-2020 | p64 | p64/narrative/inactivated-vaccine-immunity | narrative |
| breast-screening-boundaries | cancer-screening-candidate | age 40-49: choice to start annual screening; age >=50: biennial mammography; continue while in good health with expected survival >=10 years | "RENDERED: Women ages 40 to 49 should have the choice to start annual breast cancer screening; Biennial mammography is recommended for women age 50 and above; Screening should continue as long as woman is in good health and is expected to live 10 more years or longer" | kdigo-2020 | p67 | p67/narrative/table-13-breast-screening | narrative |
| colorectal-screening-boundaries | cancer-screening-candidate | age >=50: FIT every 2 years; flexible sigmoidoscopy every 5 or 10 years; stop after age 75 or when life expectancy is <10 years | "RENDERED: Biennial fecal immunochemical testing (FIT), meaning every 2 years, is recommended for all people age 50 years and above; Flexible sigmoidoscopy every 5 or 10 years; screening can be stopped for people older than 75 years or with life expectancy less than 10 years." | kdigo-2020 | p67 | p67/narrative/table-13-colorectal-screening | narrative |
| cervical-screening-boundaries | cancer-screening-candidate | start Pap testing at age 21 every 3 years, or HPV testing every 5 years through age 65; after age 65 individualize stopping based on prior negative results | "RENDERED: Papanicolaou (Pap) test is recommended for women starting at the age of 21 and screening should be done every 3 years. Alternately, screening using HPV testing should be done every 5 years up to age 65 years. Women older than 65 should talk to their doctors about whether or not they need to have regular cervical screening." | kdigo-2020 | p67 | p67/narrative/table-13-cervical-screening | narrative |
| lung-screening-boundaries | cancer-screening-candidate | annual LDCT may be used at age 55-80 with >=30 pack-years and current smoking or quitting within 15 years | "RENDERED: annual screening for people at high risk of lung cancer using LDCT. Individuals at high risk are adults aged 55 to 80 years who have a smoking history of at least 30 pack-years and currently smoke or have quit within the past 15 years" | kdigo-2020 | p67 | p67/narrative/table-13-lung-screening | narrative |
| prostate-screening-boundaries | cancer-screening-candidate | age 55-69: periodic PSA only after preference-sensitive risk-benefit discussion; stop at age 70 | "RENDERED: Men between the ages of 55 to 69 can undergo periodic screening for prostate cancer using prostate specific antigen if they wish to do so after understanding risks and benefits; screening should stop at the age of 70" | kdigo-2020 | p67 | p67/narrative/table-13-prostate-screening | narrative |
| active-renal-tumor-exception | active-malignancy-candidate | active-malignancy exclusion has a distinct exception for an incidentally detected renal tumor <=1 cm in maximum diameter | "RENDERED: We recommend that candidates with active malignancy be excluded from kidney transplantation, except for those with indolent and low-grade cancers such as prostate cancer (Gleason score <= 6), and incidentally detected renal tumors (<= 1 cm in maximum diameter)" | kdigo-2020 | p15 | p15/narrative/active-renal-tumor-exception | narrative |
| post-mi-and-pci-delay | post-mi-or-coronary-intervention-candidate | elective surgery: wait 4-6 weeks after MI, >=14 days after balloon angioplasty, >=30 days after bare-metal stent, and generally >=1 year after drug-eluting stent, although newer evidence permits consideration after 6 months | "RENDERED: waiting for 4-6 weeks after a MI prior to elective surgery; delaying non-cardiac surgery at least 14 days after balloon angioplasty and at least 30 days after a bare metal stent; delaying elective surgery at least 1 year after a drug eluting stent, although more recent data suggests surgery after 6 months may be possible." | kdigo-2020 | p73 | p73/narrative/post-mi-and-pci-delay | narrative |
| coronary-stent-aspirin-dose | coronary-stent-candidate | continue aspirin 75-100 mg daily after coronary stenting | "RENDERED: In patients who have had coronary artery stenting, both the ESC and ACC/AHA guidelines recommend continuation of aspirin at a dose of 75-100 mg daily." | kdigo-2020 | p73 | p73/narrative/coronary-stent-aspirin-dose | narrative |
| intracranial-aneurysm-reevaluation | adpkd-aneurysm-candidate | reevaluate an identified intracranial aneurysm every 6-24 months | "Individuals with ICAs should be reevaluated every 6-24 months." | kdigo-2020 | p77 | p77/narrative/identified-aneurysm-reevaluation | narrative |
| intracranial-aneurysm-reevaluation | adpkd-family-history-no-aneurysm | if family history is present but screening shows no aneurysm, rescreen every 5-10 years | "Patients with a family history of ICA but no ICA on screening should be rescreened at 5 to 10-year intervals." | kdigo-2020 | p77 | p77/narrative/family-history-aneurysm-rescreen | narrative |
| peptic-ulcer-diagnostic-action | ulcer-symptom-candidate | perform esophagogastroscopy and H. pylori testing before transplantation | "RENDERED: 16.2.1: We recommend that candidates with symptoms suggestive of active peptic ulcer disease undergo esophagogastroscopy and H. pylori testing prior to kidney transplantation (1C)." | kdigo-2020 | p78 | p78/narrative/peptic-ulcer-diagnostic-action | narrative |
| post-cholecystitis-action | cholecystitis-history-candidate | perform cholecystectomy before kidney transplantation | "RENDERED: 16.5.2: We recommend that candidates with a history of cholecystitis undergo cholecystectomy before kidney transplantation (1C)." | kdigo-2020 | p78 | p78/narrative/post-cholecystitis-action | narrative |

## Clinical action inventory

The following preserves the patient-changing qualitative actions that do not create
additional numeric threshold rows. Numbering is the guideline's, not the bound
record's marker numbering.

- **Access and organization (sections 1-3):** educate and consider every expected
  ESKD patient without demographic exclusion; evaluate stable patients already on
  dialysis; prefer preemptive living-donor transplantation; use a multidisciplinary
  team and document any nonreferral; consider age with comorbidity and frailty, never
  age alone; assess neurocognition after ESKD before age 5 and academic function when
  school difficulty is apparent. Kidney-alone referral is inappropriate for active
  or irreversible conditions for which the source directs curative remission,
  combined-organ transplantation, or exclusion.
- **Psychosocial, adherence, and substance use (sections 4-6):** perform expert
  psychosocial assessment for every candidate; use standardized tools only as
  supplements; offer counseling/services for psychiatric disease, substance use, or
  nonadherence; defer unstable disease or ongoing health-compromising nonadherence,
  but do not exclude a candidate merely for absent social support when self-care and
  an adequate plan are present. Assess tobacco repeatedly and provide cessation
  programming.
- **Surgical, anticoagulation, obesity, frailty, and diabetes (sections 7-8):** assess
  body habitus, obesity-related risk, frailty, vascular anatomy, polycystic-kidney
  space, urologic risk, and dysfunctional voiding. Anticoagulation, antiplatelet need,
  or prior HIT alone is not exclusion; single antiplatelet therapy can continue on a
  deceased-donor waitlist, mandated dual therapy may require delay, and DOAC use
  requires center expertise and reversal capacity or conversion to warfarin. Use a
  nonheparin anticoagulant for HIT. Diabetes alone is not exclusion; assess candidates
  without known diabetes by oral glucose tolerance testing and consider simultaneous
  pancreas-kidney transplantation for type 1 diabetes where available. For obesity,
  route class II/III disease to intervention, use special caution at BMI >=40, and
  preserve the sex-specific waist-to-hip boundaries. After graft loss caused by overt
  nonadherence, use the multidisciplinary reevaluation protocol and require the stated
  adherence demonstration before relisting or retransplantation.
- **Cause of kidney failure and recurrence (section 9):** determine etiology and
  recurrence risk. Counsel and individualize FSGS, membranous nephropathy, IgA
  nephropathy/vasculitis, immune-complex MPGN, C3 glomerulopathy, lupus nephritis,
  antiphospholipid syndrome, ANCA vasculitis, anti-GBM disease, HUS/aHUS, systemic
  sclerosis, plasma-cell dyscrasias, AA/fibrillary amyloidosis, primary hyperoxaluria,
  cystinosis, Fabry disease, sickle cell disease, sarcoidosis, and Alport syndrome.
  Lupus must be clinically quiescent on no or minimal immunosuppression; APS must be
  quiescent with anticoagulation continued at waitlist activation; anti-GBM antibodies
  must be undetectable. High-risk complement-mediated aHUS requires complement
  inhibition or combined liver-kidney transplantation. Multiple myeloma and each MIDD
  subtype require potentially curative treatment and stable remission. AL amyloidosis
  additionally requires minimal extrarenal disease, whereas AA amyloidosis requires
  adequate treatment of its cause and absence of severe extrarenal involvement. Use
  all other disease-specific genetic, antibody, complement, extrarenal, remission,
  combined-organ, inhibitor, and prior-graft-loss branches; do not use routine
  prophylactic plasma exchange or rituximab for primary FSGS.
- **Infections (section 10):** delay active infection but do not exclude colonization;
  treat symptomatic UTI without routine nephrectomy. Complete active-TB therapy and
  screen/treat latent TB according to prevalence and exposure. Obtain dental,
  HIV/HCV/HBV/HDV/CMV/EBV/HSV/VZV/MMR/HTLV, syphilis, Strongyloides, Chagas, malaria,
  and travel/endemic testing as source-defined. Manage HIV with an HIV specialist;
  HBsAg or HBV-DNA positivity with a liver specialist; do not exclude isolated
  anti-HBc positivity and monitor HBsAg/HBV DNA for the stated minimum period after
  transplantation. Active TB may cross the transplant boundary only after the stated
  treatment and culture/clinical/radiologic response; latent-TB therapy has a firm
  post-transplant start deadline when not begun beforehand. Do not routinely screen
  for BK virus. Accelerate inactive vaccines when needed; incomplete vaccination alone
  does not preclude transplantation. Preserve the HPV, meningococcal, zoster, dialysis-
  dose HBV, response-testing, and immunity-establishment branches and use risk-based
  splenectomy, complement-inhibitor, and travel vaccines.
- **Cancer (section 11):** use general-population screening when appropriate plus
  risk-triggered chest CT, RCC ultrasound, cystoscopy, HCC surveillance, and IBD bowel
  screening with Table 13's age, interval, preference, quit-time, and stopping
  boundaries. Defer active malignancy except the source's indolent/low-grade exceptions,
  including the distinct incidental renal-tumor <=1 cm active-evaluation exception.
  Start a required wait after completion of potentially curative therapy; use oncology
  consultation, stage, molecular features, competing risks, and patient preference.
  Hematologic malignancies require stable curative remission and specialist agreement;
  chronic or low-grade marrow disorders require individualized hematology review.
- **Pulmonary and cardiac disease (sections 12-13):** obtain pulmonary-specialist
  assessment, chest imaging, and PFTs for known or suspected disease; exclude severe
  irreversible lung disease from kidney-alone transplantation. Obtain history,
  examination, and ECG for all; refer active cardiac disease; use noninvasive CAD
  screening for asymptomatic high-risk or poor-functional-capacity candidates. Do not
  revascularize stable asymptomatic CAD solely to reduce perioperative events. Assess
  severe multivessel CAD, valve disease, pulmonary hypertension, heart failure,
  cardiac amyloidosis, MI, and coronary-stent timing with cardiology; preserve the
  post-MI, balloon, bare-metal-stent, drug-eluting-stent, and dual-antiplatelet timing
  branches. Consider combined heart-kidney transplantation where appropriate; continue
  aspirin at the stated post-stent dose and continue beta-blockers and statins as
  locally directed.
- **Peripheral arterial and neurologic disease (sections 14-15):** assess PAD by
  history/exam, use noninvasive testing when high risk, obtain vascular-surgeon review
  and noncontrast CT for clinically apparent PAD, defer active nonhealing infection,
  and do not automatically exclude severe aortoiliac or distal disease after explicit
  progression-risk counseling. Do not screen asymptomatic carotids. Screen intracranial
  aneurysm in ADPKD only with personal/family subarachnoid-hemorrhage history; when an
  aneurysm is found or family history persists despite a negative screen, apply the
  distinct reevaluation intervals. Exclude
  progressive central neurodegenerative disease but not nonprogressive cognitive or
  developmental disability; investigate progressive neuropathy and expedite when
  uremia is the likely cause.
- **Gastrointestinal, hematologic, bone, and immunologic assessment (sections 16-19):**
  evaluate ulcer-suggestive symptoms with esophagogastroscopy and H. pylori testing,
  and require pretransplant cholecystectomy after cholecystitis. Delay active peptic
  ulcer disease, diverticulitis, pancreatitis, gallbladder disease,
  IBD, or acute hepatitis until treated/resolved; do not routinely screen or perform
  prophylactic surgery in asymptomatic disease. Refer cirrhosis for combined-organ
  expertise. Do not routinely thrombophilia-screen; test when VTE, recurrent access
  thrombosis, nonatherosclerotic arterial thrombosis, family history, SLE, or APS
  features justify it. Assess cytopenias, hemoglobinopathy, MGUS/smoldering myeloma,
  and malignancy with specialists. Measure PTH and treat severe hyperparathyroidism;
  do not routinely measure BMD. Communicate sensitizing events, use solid-phase HLA
  testing and molecular typing, avoid routine non-HLA or complement-binding testing,
  and improve access through larger pools, exchange, and antibody-avoidance before
  considering desensitization.

## Benefits, harms, and uncertainty

- Transplantation generally improves survival and quality of life versus remaining on
  dialysis, but perioperative and early post-transplant mortality, immunosuppression,
  infection, malignancy, recurrence, cardiovascular events, wound complications, and
  graft loss must be weighed against individualized waitlist prognosis.
- Exclusion and delay can prevent futile or unsafe transplantation but also prolong
  dialysis exposure and inequity. The guideline repeatedly requires shared decisions,
  multidisciplinary expertise, a second opinion where appropriate, and transparent
  communication of why a candidate is deferred or excluded.
- Screening can detect actionable infection, cancer, vascular disease, or sensitization,
  but false-positive tests, invasive follow-up, contrast/procedure harms, and delay are
  material. Many screening and waiting-time recommendations rest on low-quality or
  indirect evidence rather than transplant-candidate trials.
- Obesity, frailty, PAD, cognitive disability, infection colonization, diabetes,
  anticoagulation, MGUS, and many recurrent kidney diseases alter risk but are not
  automatic exclusions. The sheet preserves the source's conditional branches rather
  than converting risk factors into absolute contraindications.
- Cancer waiting times in Table 14 are consensus parameters; tumor biology, stage,
  molecular testing, curative status, competing mortality, and oncology advice may
  alter the individualized decision. Invasive melanoma and stage 4/anaplastic thyroid
  cancer are printed as contraindicated in that table.
- Direct oral anticoagulants can create an unpredictable deceased-donor operative
  window; cessation can cause thrombosis. Dual antiplatelet interruption can cause
  stent thrombosis, while continuation increases bleeding. Cardiology/hematology and
  center reversal capacity determine the safe branch.
- Live vaccination close to transplant risks vaccine-derived infection under
  immunosuppression; delaying transplant also has risk. Vaccine schedules in Table 12
  are explicitly suggestive and may vary by region, so local guidance controls.

## Conflicts and provenance

Reconciliation — recommendation 11.2.3's `cancer-no-wait-exceptions` branch gives no
waiting time for low-grade papillary or follicular thyroid cancer `<2 cm`, while
Table 14's distinct `thyroid-cancer-wait` grid gives no wait for thyroid stage 1
without repeating the size or histology restriction. These are complementary
recommendation-specific and table-stage populations, not interchangeable values;
oncology review reconciles them for an individual candidate.

Reconciliation — Figure 3's `hcv-figure-wait-time` branch uses expected wait `<24
weeks` versus `>24 weeks` to route pretreatment, while the distinct
`hcv-treatment-selection-factors` recommendation requires donor type, center policy,
genotype, wait time, and fibrosis. The figure operationalizes one branch and does not
replace the full multivariable recommendation.

SOURCE-PRINTED EXTERNAL: HCV recommendations 10.5.2.1-10.5.2.5.3 and Figure 3 are
adapted from the 2018 KDIGO HCV guideline. Their values remain because the candidate
guideline expressly adopts them; the bound record uses the external HCV
recommendation identifiers rather than the candidate guideline's 10.5.x identifiers.

SOURCE-PRINTED EXTERNAL: Table 14 states that its cancer waiting times are derived
from prior transplant guidance. They are preserved as this guideline's adopted
consensus parameters, with oncology consultation and individualized tumor biology as
the implementation boundary.

SOURCE-PRINTED EXTERNAL: Table 12 labels vaccine doses and durations as suggestive,
variable by region, and subject to local guidance. They are not universal dosing
orders.

SOURCE-PRINTED EXTERNAL: Table 13 prints general-population cancer-screening ages,
intervals, and stopping rules from the cited screening organizations and directs
potential transplant candidates to those general-population practices. The table's
own risk-triggered kidney, bladder, and lung branches remain transplant-specific.

SOURCE-PRINTED EXTERNAL: the BMI/waist-to-hip definitions are attributed to the World
Health Organization, and the post-MI, coronary-intervention, and aspirin timing/dose
values are attributed to ACC/AHA and ESC perioperative guidance. They are retained
because KDIGO prints them to operationalize candidate evaluation, not because this
sheet independently endorses the external sources.

## Coverage

Bound record accounting: **21 = 10 cited + 11 disposed**. The 10 detailed HCV
cross-reference occurrences are cited above. The following 11 record occurrences are
individually disposed:

- `p19/recommendation/1.1.4` - summary duplicate of the detailed p60 HCV testing occurrence cited above.
- `p19/recommendation/1.1.1.1` - summary duplicate of the detailed p60 CKD G5/HCV occurrence cited above.
- `p19/recommendation/4.1.1` - summary duplicate of the detailed p60 liver-severity occurrence cited above.
- `p19/recommendation/4.1.2` - summary duplicate of the detailed p60 compensated-cirrhosis occurrence cited above.
- `p19/recommendation/4.1.2.1` - summary duplicate of the detailed p60 decompensated-cirrhosis occurrence cited above.
- `p19/recommendation/4.1.2.2` - summary duplicate of the detailed p60 treatment-timing occurrence cited above.
- `p19/recommendation/4.1.3` - summary duplicate of the detailed p60 DAA-eligibility occurrence cited above.
- `p19/recommendation/4.1.3.1` - summary duplicate of the detailed p60 living-donor timing occurrence cited above.
- `p20/recommendation/4.1.3.2` - summary duplicate of the detailed p60 HCV-positive donor occurrence cited above.
- `p20/recommendation/4.1.3.3` - summary duplicate of the detailed p61 HBV-screening occurrence cited above.
- `p39/recommendation/15.5.1` - narrative cross-reference mention, not the recommendation itself; the actual nonprogressive cognitive-disability action is retained in the clinical inventory from summary p24 and detailed section 15.

The full-source accounting is distinct from the bound-marker accounting: **268 unique
source-numbered actions across sections 1-19 were read and retained** through the
threshold rows and clinical action inventory. Section totals are 13, 2, 2, 8, 4, 5,
18, 3, 49, 52, 19, 6, 15, 7, 9, 25, 19, 3, and 9 respectively, totaling 268.
Summary repetitions are not counted again.

## ADR 0009 disposition

Kept: patient-changing GFR, timing, abstinence, pack-year, adherence, BMI/waist-to-hip,
medication-hold, urine-output, recurrence/remission, HIV/TB/HBV stability and monitoring,
viral-testing, HCV-treatment, vaccine dose/age/interval, cancer screening/wait,
post-MI/intervention, aspirin-dose, aneurysm-follow-up, gastrointestinal testing/surgery,
cardiopulmonary, neurologic, and immunologic monitoring decision points, plus
qualitative actions needed to preserve exclusions and conditional
branches. Excluded: study-only numbers, epidemiology, effect estimates, historical
figures, citation numbers, and operational detail that does not alter candidate care.
External HCV, oncology-wait, and vaccine values were retained only because this
guideline expressly adopts or prints them, and their external/local-guidance
boundaries are declared above.
