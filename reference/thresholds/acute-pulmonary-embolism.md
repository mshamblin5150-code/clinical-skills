# Acute pulmonary embolism - threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aha-2026 | AHA ACC | AHA ACC/creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of | guideline | 2026 | 2026 | https://doi.org/10.1161/CIR.0000000000001415 | stated | exact |

## Scope

**Read:** the complete 75-page guideline, including front matter, definitions,
recommendation tables, supportive text, algorithms, clinical classification and
risk-score tables, evidence gaps, article information, references, and disclosure
appendices. Tables 3-10 and Figures 1, 2, 3, and 8 were also read from rendered pages
because their layout carries clinically material relationships.

**Not read:** nothing in the source page range. The reference list was inspected for
scope and retired by class because it contains no clinical prose.

| span | pages | read |
| --- | --- | --- |
| front matter, introduction, scope, definitions, and classifications | 1-6 | yes |
| evaluation and diagnosis | 7-13 | yes |
| PE outcomes risk stratification | 13-20 | yes |
| acute management, hospitalization, pharmacotherapy, support, filters, and advanced therapies | 20-40 | yes |
| monitoring, follow-up, recurrence-risk therapy, and recurrent PE | 41-50 | yes |
| complications, sequelae, and CTEPD evaluation | 49-53 | yes |
| evidence gaps, officers, peer review, and article information | 54-55 | read 2026-08-31; blind 2026-08-31 |
| references | 55-67 | exempt: reference list contains no clinical prose |
| author and reviewer relationship disclosures | 68-75 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adult-acute-pe | adult patient (>=18 years of age) with acute pulmonary embolism |
| suspected-pe | adult patients undergoing evaluation for PE |
| years-suspected-pe | patients with suspected PE assessed with the YEARS algorithm |
| low-probability-suspected-pe | patients with suspected acute PE and low pretest probability (<15%) |
| intermediate-probability-suspected-pe | patients with suspected acute PE and intermediate pretest probability (15%-50%) |
| high-probability-suspected-pe | patients with suspected acute PE and high pretest probability (>50%) |
| no-years-suspected-pe | patients with suspected acute PE who have no YEARS criteria |
| one-or-more-years-suspected-pe | patients with suspected acute PE who have at least 1 YEARS criterion |
| acute-pe | patients with acute PE |
| category-c3-pe | patients with acute PE in AHA/ACC PE Category C3 |
| category-d2-pe | patients with acute PE in AHA/ACC PE Category D2 |
| obese-acute-pe | patients with obesity and acute PE |
| severe-obesity-lmwh-pe | patients with class III obesity and acute PE who are receiving LMWH therapy |
| ckd-acute-pe | patients with chronic kidney disease and acute PE |
| mild-moderate-ckd-acute-pe | patients with mild-to-moderate (stage 2-3) chronic kidney disease and acute PE |
| severe-ckd-acute-pe | patients with severe kidney disease (stage 4-5) or endstage kidney disease on hemodialysis and confirmed PE |
| monitored-lmwh-pe | patients with acute PE in whom LMWH is monitored |
| pregnant-lmwh-pe | pregnant patients treated with LMWH for acute PE |
| high-weight-lmwh-pe | patients receiving LMWH for treatment of acute PE who weigh >150 kg or have a BMI of >40 kg/m2 |
| post-bariatric-pe | patients who have undergone bariatric surgery and require a DOAC for acute PE |
| shock-acute-pe | patients with acute PE and cardiogenic or normotensive shock |
| ivc-filter-patient | patients with retrievable or permanent IVC filters |
| systemic-thrombolysis-pe | patients with acute PE being treated with systemic thrombolysis |
| cdl-acute-pe | patients with acute PE who are undergoing CDL |
| post-acute-pe | patients after acute PE |
| complex-post-acute-pe | select complex patients with acute PE receiving specialized follow-up |
| travel-history-pe | patients with a history of acute PE |
| category-c2-e-travel-pe | patients recovering from acute PE in AHA/ACC PE Categories C2-E |
| travel-related-pe | patients with a history of acute PE related to travel or immobility who are not receiving anticoagulation |
| first-pe-no-major-reversible | patients with a first acute PE and no major reversible risk factor |
| first-pe-major-reversible | patients with a first acute PE due to a major reversible risk factor |
| first-pe-persistent | patients with a first PE due to a persistent risk factor |
| extended-pe | patients with PE offered anticoagulation beyond the initial treatment phase |
| extended-cancer-pe | patients with PE and cancer offered anticoagulation beyond the initial treatment phase |
| extended-no-cancer-no-doac | patients with PE without cancer who have a contraindication to DOAC and are offered extended anticoagulation |
| first-pe-minor-reversible | patients with a first acute PE due to a minor reversible risk factor |
| extended-no-anticoagulant | patients offered extended anticoagulation who have a contraindication to or refuse anticoagulation |
| recurrent-cancer-pe | patients with cancer and recurrent PE despite therapeutic LMWH |
| persistent-symptoms-pe | patients with ongoing dyspnea and/or functional impairment after acute PE |

## Quantities

| key | verbatim |
| --- | --- |
| guideline-age | focus of this clinical practice guideline |
| treatment-phase-duration | Initial Treatment Phase and Extended Treatment Phase |
| age-adjusted-d-dimer | age-adjusted D-dimer value below the threshold |
| years-d-dimer | D-dimer threshold used by the YEARS algorithm |
| figure1-pretest-probability | pretest probability branch in the clinical evaluation algorithm |
| figure1-no-years-d-dimer | D-dimer and imaging branch with no YEARS criteria |
| figure1-one-or-more-years-d-dimer | D-dimer and imaging branch with at least 1 YEARS criterion |
| wells-score-groups | Wells Score for PE probability grouping |
| wells-score-components | Wells Score for PE components and points |
| perc-rule | PE Rule Out Criteria |
| geneva-score-groups | Revised Geneva and Simplified Revised Geneva probability grouping |
| geneva-score-components | Revised Geneva and Simplified Revised Geneva components and points |
| diagnostic-imaging-probability | imaging is recommended |
| ct-rv-lv-risk | RV/LV ratio by CTPA |
| chronic-ctpa-features | chronic features of PE on CTPA |
| pvfr-definition | pulmonary venous flow reduction definition |
| echo-rv-dimension | RV dimension |
| echo-rv-lv-ratio | RV/LV end-diastolic ratio |
| echo-tapse | TAPSE |
| echo-tdi-s | TDI S' velocity |
| echo-tr-velocity | TR velocity |
| pe-category-score-boundary | low and elevated clinical severity score |
| category-d1-hemodynamics | transient hypotension |
| category-e1-hemodynamics | recurrent or persistent hypotension |
| category-d2-hypoperfusion | normotensive shock |
| category-c-respiratory-modifier | respiratory modifier for Category C |
| category-d-respiratory-modifier | respiratory modifier for Category D |
| category-e2-arrest | Category E2 cardiac arrest |
| d2-fluid-trial | trial of intravenous fluids |
| pesi-risk-classes | PESI risk classes |
| pesi-risk-components | PESI risk score components and points |
| spesi-risk-score | sPESI risk score components and classes |
| bova-risk-score | Bova score components and stages |
| hestia-disposition | Hestia criteria and disposition |
| cpes-risk-score | CPES score and normotensive-shock risk |
| news2-risk-score | NEWS2 high-risk cutoff |
| bova-score-range | Bova score range |
| news2-score-range | NEWS2 score range |
| aha-2011-submassive-risk | 2011 AHA submassive PE blood-pressure criterion |
| aha-2011-massive-risk | 2011 AHA massive PE blood-pressure criterion |
| esc-2019-low-risk | 2019 ESC low-risk score and imaging criteria |
| esc-2019-intermediate-low-risk | 2019 ESC intermediate-low score, troponin, and imaging criteria |
| esc-2019-intermediate-high-risk | 2019 ESC intermediate-high score, troponin, and imaging criteria |
| normotensive-shock-markers | markers of isolated hypoperfusion |
| normotensive-shock-lactate | serum lactate marker of isolated hypoperfusion |
| normotensive-shock-urine-output | urine-output marker of isolated hypoperfusion |
| normotensive-shock-creatinine-increase | creatinine-increase marker of isolated hypoperfusion |
| normotensive-shock-cardiac-index | cardiac-index marker of isolated hypoperfusion |
| map-escalation | MAP identifying possible need for escalation |
| category-c3-monitoring | monitoring for worsening clinical status |
| obesity-doac-choice | treatment with a DOAC over a VKA |
| severe-obesity-lmwh-dose | reducing the dose of LMWH |
| severe-obesity-enoxaparin-comparison | enoxaparin doses compared in severe obesity |
| ckd-oral-anticoagulant | oral anticoagulant choice by CKD stage |
| lmwh-peak-anti-xa-time | measuring a peak anti-Xa level |
| severe-ckd-anti-xa | monitor anti-Xa levels |
| pregnancy-anti-xa | monitoring the peak anti-Xa level |
| high-weight-anti-xa | benefit of monitoring anti-Xa levels |
| post-bariatric-doac | DOAC avoidance after bariatric surgery |
| ckd-egfr-stage | eGFR boundaries for CKD stages |
| norepinephrine-dose | norepinephrine dose and addition of a second vasopressor |
| dobutamine-dose | continuous infusion of dobutamine |
| fluid-bolus-volume | small fluid boluses |
| permanent-ivc-filter-size | permanent filter feasibility in mega cava |
| ivc-filter-retrieval | retrieval of an IVC filter |
| systemic-alteplase-standard | standard dose rt-PA |
| systemic-alteplase-low-dose | lower-dose rt-PA |
| systemic-alteplase-six-hour-regimen | extended low-dose rt-PA regimen evaluated in acute PE |
| cdl-alteplase-dose | alteplase dose per pulmonary artery |
| cdl-study-dose-duration-range | rt-PA dose and duration range in CDL studies |
| cdl-bleeding-dose-observation | total rt-PA dose with no demonstrated higher bleeding rate |
| first-follow-up | first clinical follow-up after discharge |
| early-follow-up-program-window | initial follow-up interval used by outpatient programs |
| three-month-visit | clinical visit after diagnosis |
| symptom-screen-duration | symptom and functional-limitation screening |
| extended-reassessment | reassessment during extended anticoagulation |
| performance-test-timing | performance test for persistent symptoms |
| thrombophilia-testing-age | thrombophilia testing by age |
| specialty-clinic-timing | specialized PE-clinic follow-up |
| follow-up-consensus-schedule | longitudinal follow-up schedule after acute PE |
| six-minute-walk-path | walking-path length for the six-minute walk test |
| six-minute-walk-duration | duration of the six-minute walk test |
| shuttle-walk-course | course length for shuttle walk tests |
| compression-travel-duration | compression stockings during long-haul travel |
| travel-prophylaxis-duration | one-time anticoagulant prophylaxis for long-distance travel |
| travel-restriction | restriction of long-haul travel |
| no-major-reversible-duration | anticoagulation with no major reversible risk factor |
| major-reversible-duration | anticoagulation with a major reversible risk factor |
| persistent-risk-duration | anticoagulation with a persistent risk factor |
| extended-doac-duration | DOAC use in the extended phase |
| extended-cancer-duration | DOAC or LMWH use for cancer in the extended phase |
| extended-vka-duration | VKA use when DOAC is contraindicated in the extended phase |
| extended-half-dose-duration | half-dose apixaban or rivaroxaban in the extended phase |
| minor-reversible-duration | shared decision-making after a minor reversible risk factor |
| extended-aspirin-duration | low-dose aspirin when anticoagulation is unavailable |
| apixaban-initiation-dose | apixaban initiation regimen |
| rivaroxaban-initiation-dose | rivaroxaban initiation regimen |
| dabigatran-edoxaban-lead-in | parenteral lead-in before dabigatran or edoxaban |
| vka-initiation-bridge | parenteral anticoagulation with VKA initiation |
| rivaroxaban-extended-dose | half-dose rivaroxaban in extended anticoagulation |
| apixaban-extended-dose | half-dose apixaban in extended anticoagulation |
| major-reversible-risk-duration | duration boundaries defining major reversible risk factors |
| minor-reversible-risk-duration | duration boundaries defining minor reversible risk factors |
| recurrent-lmwh-escalation | LMWH dose escalation after recurrent PE |
| rivaroxaban-meal-dose | rivaroxaban doses requiring a meal |
| ctepd-evaluation-time | diagnostic evaluation for CTEPD |
| pulmonary-rehabilitation-time | pulmonary rehabilitation after acute PE |
| repeat-echo-time | repeated echocardiogram after acute PE |
| ctepd-trv-probability | TRV boundary for echocardiographic probability |
| ph-sign-count | number of echocardiographic sign categories |
| ph-echo-signs | echocardiographic signs suggestive of pulmonary hypertension |
| ph-rv-lv-sign | RV/LV basal diameter or area-ratio sign |
| ph-lvei-sign | left ventricular eccentricity-index sign |
| ph-tapse-spap-sign | TAPSE/sPAP sign |
| ph-rvot-at-sign | RV outflow tract acceleration-time sign |
| ph-pr-velocity-sign | early-diastolic pulmonary-regurgitation velocity sign |
| ph-pa-diameter-sign | pulmonary-artery diameter sign |
| ph-ivc-sign | inferior-vena-cava diameter and collapse sign |
| ph-ra-area-sign | right-atrial area sign |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| guideline-age | adult-acute-pe | age >=18 years | "adult patient (≥18 years of age)" | aha-2026 | p4 | p4/narrative/guideline-scope-age | narrative |
| treatment-phase-duration | adult-acute-pe | initial phase 3-6 months; extended phase >6 months | RENDERED: "Initial Treatment Phase describes the first 3 to 6 months of anticoagulation therapy after an acute PE. Extended Treatment Phase designates more than 6 months of anticoagulation therapy after an acute PE." | aha-2026 | p6 | p6/narrative/treatment-phase-definitions | narrative |
| age-adjusted-d-dimer | suspected-pe | low or intermediate probability <50%; threshold age x 10 micrograms/L for FEU assays | "low or intermediate clinical probability of PE (<50%) by risk assessment, an age-adjusted D-dimer value below the threshold (age × 10 μg/L for fibrinogen equivalent units assays) effectively excludes PE and the need for imaging" | aha-2026 | p7 | p7/clinical-assessment/2 | 2a |
| years-d-dimer | years-suspected-pe | >=1 YEARS criterion: 500 micrograms/L; no YEARS criteria: 1000 micrograms/L | RENDERED: "YEARS algorithm: A D-dimer threshold of 500 μg/L in patients who have ≥1 of the following: 1) clinical signs of DVT; 2) hemoptysis; and/or 3) PE as the most likely diagnosis. A D-dimer threshold of 1000 μg/L is used for patients who have no YEARS criteria." | aha-2026 | p7 | p7/narrative/years-d-dimer-thresholds | narrative |
| figure1-pretest-probability | low-probability-suspected-pe | probability <15%: apply PERC; if PERC is not negative, continue to D-dimer testing | RENDERED: "Low (<15%)"; "PERC"; "D-dimer" | aha-2026 | p8 | p8/narrative/figure1-low-probability-path | narrative |
| figure1-pretest-probability | intermediate-probability-suspected-pe | probability 15%-50%: continue to D-dimer testing | RENDERED: "Intermediate (15%-50%)"; "D-dimer" | aha-2026 | p8 | p8/narrative/figure1-intermediate-probability-path | narrative |
| figure1-pretest-probability | high-probability-suspected-pe | probability >50%: proceed to diagnostic imaging | RENDERED: "High (>50%)"; "Imaging" | aha-2026 | p8 | p8/narrative/figure1-high-probability-path | narrative |
| figure1-no-years-d-dimer | no-years-suspected-pe | YEARS criteria 0 and D-dimer <1000 ng/mL: PE excluded; D-dimer >=1000 ng/mL: diagnostic imaging | RENDERED: "0 YEARS criteria and D-dimer <1000 ng/mL"; "PE diagnosis excluded"; "0 YEARS criteria and D-dimer ≥1000 ng/mL"; "Perform diagnostic imaging" | aha-2026 | p8 | p8/narrative/figure1-no-years-path | narrative |
| figure1-one-or-more-years-d-dimer | one-or-more-years-suspected-pe | YEARS criteria >=1 and D-dimer <500 ng/mL or age-adjusted threshold: PE excluded; D-dimer >=500 ng/mL or age-adjusted threshold: diagnostic imaging | RENDERED: "≥1 YEARS criteria and D-dimer <500 ng/mL or age-adjusted threshold"; "PE diagnosis excluded"; "≥1 YEARS criteria and D-dimer ≥500 ng/mL or age-adjusted threshold"; "Perform diagnostic imaging" | aha-2026 | p8 | p8/narrative/figure1-one-or-more-years-path | narrative |
| wells-score-groups | suspected-pe | standard low <2, moderate 2-6, high >6; modified likely >4, unlikely <=4 | RENDERED: "Low: <2; Moderate: 2-6; High: >6"; "PE likely: >4; PE unlikely: <=4" | aha-2026 | p9 | p9/narrative/wells-score-groups | narrative |
| wells-score-components | suspected-pe | DVT signs 3 points; PE more likely 3; heart rate >100 bpm 1.5; immobilization >=3 days or surgery within 4 weeks 1.5; previous DVT/PE 1.5; hemoptysis 1; cancer 1 | RENDERED: "Clinical signs and symptoms of DVT 3"; "PE is more likely than alternative diagnosis 3"; "Heart rate >100 bpm 1.5"; "Immobilization (≥3 days) or surgery in the previous 4 weeks 1.5"; "Previous DVT/PE 1.5"; "Hemoptysis 1"; "Malignancy 1" | aha-2026 | p9 | p9/narrative/wells-score-components | narrative |
| perc-rule | suspected-pe | apply when pretest probability <15%; all required: age <50 years, heart rate <100 bpm, oxygen saturation >=95%, and no surgery/trauma hospitalization within 4 weeks plus qualitative criteria | RENDERED: "pretest probability <15%"; "Age <50 years"; "Heart rate <100 bpm"; "Oxyhemoglobin saturation ≥95%"; "No surgery or trauma requiring hospitalization within the prior 4 weeks" | aha-2026 | p9 | p9/narrative/perc-rule | narrative |
| geneva-score-groups | suspected-pe | revised low 0-3, intermediate 4-10, high >=11; simplified low 0-1, intermediate 2-4, high 5-7; simplified unlikely 0-2, likely 3-7 | RENDERED: "Revised Geneva Low: 0-3"; "Intermediate: 4-10"; "High: ≥11"; "Simplified Revised Geneva Low: 0-1"; "Intermediate: 2-4"; "High: 5-7"; "Unlikely: 0-2"; "Likely: 3-7" | aha-2026 | p9 | p9/narrative/geneva-score-groups | narrative |
| geneva-score-components | suspected-pe | age >65: 1/1 point; prior DVT/PE 3/1; surgery or fracture within 1 month 2/1; cancer 2/1; unilateral pain 3/1; hemoptysis 2/1; heart rate 75-94: 3/1; heart rate >=95: 5/1; palpation pain and edema 4/1 | RENDERED: "Age >65 1 1"; "Previous DVT or PE 3 1"; "Surgery or fracture within 1 month 2 1"; "Active malignancy 2 1"; "Unilateral lower limb pain 3 1"; "Hemoptysis 2 1"; "Heart rate 75-94 bpm 3 1"; "Heart rate ≥95 bpm 5 1"; "Pain on lower limb deep venous palpation and unilateral edema 4 1" | aha-2026 | p9 | p9/narrative/geneva-score-components | narrative |
| diagnostic-imaging-probability | suspected-pe | >50% probability: imaging recommended | "high probability (>50% probability of PE)" | aha-2026 | p10 | p10/diagnostic-testing/1 | 1 |
| ct-rv-lv-risk | acute-pe | RV/LV ratio >=1.0 is the principal abnormal cut point; >=0.9 is a less specific alternative | RENDERED: "Utilizing a cut-point of ≥1.0 for the RV/LV ratio by CTPA yields sensitivity of 85% (95% CI, 81%-89%) and specificity of 72% (95% CI, 67%-77%), compared with 92% (95% CI, 89%-95%) and 56% (95% CI, 46%-66%), respectively, with a cut-point of ≥0.9 for the RV/LV ratio." | aha-2026 | p12 | p12/narrative/ct-rv-lv-cut-points | narrative |
| chronic-ctpa-features | acute-pe | >=3 listed chronic radiologic parameters identify higher CTEPD risk | "presence of ≥3 of the following radiologic parameters" | aha-2026 | p13 | p13/narrative/chronic-ctpa-feature-count | narrative |
| pvfr-definition | acute-pe | pulmonary-vein filling defect >=2 cm and left-atrial attenuation >160 HU | RENDERED: "PVFR was defined as the presence of a filling defect of at least 2 cm in a pulmonary vein draining into the left atrium and left atrium attenuation (>160 Hounsfield units)." | aha-2026 | p13 | p13/narrative/pvfr-definition | narrative |
| echo-rv-dimension | acute-pe | RV EDD >=30 mm or RV basal EDD >=41 mm | RENDERED: "EDD >=30 mm"; "RV basal EDD >=41 mm" | aha-2026 | p13 | p13/narrative/echo-rv-dimension | narrative |
| echo-rv-lv-ratio | acute-pe | RV/LV >0.9 | RENDERED: "RV/LV >0.9" | aha-2026 | p13 | p13/narrative/echo-rv-lv-ratio | narrative |
| echo-tapse | acute-pe | TAPSE <1.7 cm is abnormal | RENDERED: "TAPSE <1.7 cm is abnormal" | aha-2026 | p13 | p13/narrative/echo-tapse | narrative |
| echo-tdi-s | acute-pe | TDI S' 9.5 cm/s is abnormal; source rendering does not state an operator | RENDERED: "TDI S' 9.5 cm/s is abnormal" | aha-2026 | p13 | p13/narrative/echo-tdi-s | narrative |
| echo-tr-velocity | acute-pe | >=2.9 m/s suggests pulmonary hypertension | RENDERED: ">=2.9 m/sec suggests pulmonary hypertension" | aha-2026 | p13 | p13/narrative/echo-tr-velocity | narrative |
| pe-category-score-boundary | acute-pe | low: PESI <=85, sPESI =0, or Bova <=4; elevated: PESI >85, sPESI >=1, or Bova >4 | RENDERED: "PESI <=85 or sPESI =0 or Bova <=4"; "PESI >85 or sPESI >=1 or Bova >4" | aha-2026 | p14 | p14/narrative/pe-category-score-boundary | narrative |
| category-d1-hemodynamics | acute-pe | SBP <90 mm Hg or decrease >40 mm Hg lasting <15 minutes or responding to IV fluids | RENDERED: "Systolic blood pressure <90 or decrease >40 mm Hg lasting <15 min or responding to IV fluids" | aha-2026 | p14 | p14/narrative/category-d1-hemodynamics | narrative |
| category-e1-hemodynamics | acute-pe | SBP <90 mm Hg or decrease >40 mm Hg lasting >=15 minutes or not responding to IV fluids | RENDERED: "Systolic blood pressure <90 or decrease >40 mm Hg lasting ≥15 min or not responding to IV fluids" | aha-2026 | p14 | p14/narrative/category-e1-hemodynamics | narrative |
| category-d2-hypoperfusion | acute-pe | any: lactate >2 mmol/L, urine output <0.5 mL/kg/h, cardiac index <2.2 L/min/m2, or MAP <60 mm Hg, plus listed nonnumeric markers | RENDERED: "Lactate >2 mmol/L"; "urine output <0.5 mL/kg/hr"; "cardiac index <2.2 L/min/m2"; "mean arterial pressure <60 mm Hg" | aha-2026 | p14 | p14/narrative/category-d2-hypoperfusion | narrative |
| category-c-respiratory-modifier | acute-pe | oxygen saturation <90%, respiratory rate >=30/min, or need for supplemental oxygen | RENDERED: "O2 <90%, RR >=30, need supplemental O2" | aha-2026 | p14 | p14/narrative/category-c-respiratory-modifier | narrative |
| category-d-respiratory-modifier | acute-pe | >6 L nasal cannula or nonrebreather mask | RENDERED: ">6 L nasal cannula or use of an NRB mask" | aha-2026 | p14 | p14/narrative/category-d-respiratory-modifier | narrative |
| category-e2-arrest | acute-pe | no return of spontaneous circulation after 30 minutes of resuscitation | "without restoration of spontaneous circulation after 30 minutes of resuscitation" | aha-2026 | p15 | p15/narrative/category-e2-arrest | narrative |
| d2-fluid-trial | category-d2-pe | 500-1000 mL IV normal saline | "500 to 1000 mL of intravenous normal saline" | aha-2026 | p15 | p15/narrative/d2-fluid-trial | narrative |
| aha-2011-submassive-risk | acute-pe | SBP >=90 mm Hg plus either RV dysfunction or myocardial necrosis | RENDERED: "Submassive"; "Systolic BP ≥90 mm Hg and either right ventricular dysfunction or myocardial necrosis" | aha-2026 | p13 | p13/narrative/table5-aha-2011-submassive | narrative |
| aha-2011-massive-risk | acute-pe | SBP <90 mm Hg for >15 minutes or requiring inotropic support | RENDERED: "Massive"; "Systolic blood pressure <90 mm Hg for >15 minutes or requiring inotropic support" | aha-2026 | p13 | p13/narrative/table5-aha-2011-massive | narrative |
| esc-2019-low-risk | acute-pe | PESI class I-II or sPESI =0 plus normal RV imaging | RENDERED: "Low risk"; "PESI class I-II or sPESI=0"; "Normal right ventricle on imaging" | aha-2026 | p13 | p13/narrative/table5-esc-2019-low | narrative |
| esc-2019-intermediate-low-risk | acute-pe | PESI class III-IV or sPESI >=1 plus none or 1 positive of troponin elevation or RV dysfunction on imaging | RENDERED: "Intermediate-low risk"; "PESI class III-IV or sPESI ≥1"; "None or 1 positive of either troponin or right ventricular dysfunction on imaging" | aha-2026 | p13 | p13/narrative/table5-esc-2019-intermediate-low | narrative |
| esc-2019-intermediate-high-risk | acute-pe | PESI class III-IV or sPESI >=1 plus both positive troponin and RV dysfunction on imaging | RENDERED: "Intermediate-high risk"; "PESI class III-IV or sPESI ≥1"; "Both positive troponin and right ventricular dysfunction on imaging" | aha-2026 | p13 | p13/narrative/table5-esc-2019-intermediate-high | narrative |
| pesi-risk-classes | acute-pe | Class I <=65; II 66-85; III 86-105; IV 106-125; V >=126 points | RENDERED: "Class I (lowest risk): ≤65 pts"; "Class II: 66-85 pts"; "Class III: 86-105 pts"; "Class IV: 106-125 pts"; "Class V (highest risk): ≥126 pts" | aha-2026 | p16 | p16/narrative/pesi-risk-classes | narrative |
| pesi-risk-components | acute-pe | male 10; cancer 30; heart failure 10; chronic lung disease 10; HR >=110 20; SBP <100 30; RR >=30 20; temperature <36 C 20; altered status 60; oxygen saturation <90% 20 points, added to age | RENDERED: "Male (10 pts)"; "History of cancer (30 pts)"; "History of heart failure (10 pts)"; "Chronic lung disease (10 pts)"; "Heart rate ≥110 bpm (20 pts)"; "Systolic blood pressure <100 mm Hg (30 pts)"; "Respiratory rate ≥30 bpm (20 pts)"; "Temperature <36°C (20 pts)"; "Altered mental status (60 pts)"; "Oxygen saturation <90% (20 pts)" | aha-2026 | p16 | p16/narrative/pesi-components | narrative |
| spesi-risk-score | acute-pe | age >80, SBP <100, HR >=110, oxygen saturation <90%, cancer, or chronic cardiopulmonary disease: 1 point each; 0 low risk, >=1 high risk | RENDERED: "Age >80 yrs"; "Systolic blood pressure <100 mm Hg"; "Heart rate ≥110 bpm"; "Arterial oxygen saturation <90%"; "adding 1 pt for each"; "0 points: Low risk"; "≥1 point: High risk" | aha-2026 | p16 | p16/narrative/spesi-score | narrative |
| bova-risk-score | acute-pe | SBP 90-100: 2; troponin elevation 2; RV dysfunction 2; HR >=110: 1; Stage I 0-2, II 3-4, III >4 | RENDERED: "Systolic blood pressure 90-100 mm Hg (2 pts)"; "Cardiac troponin elevation (2 pts)"; "Right ventricular dysfunction (2 pts)"; "Heart rate ≥110 bpm (1 pt)"; "Stage I (lowest risk): 0-2 pts"; "Stage II: 3-4 pts"; "Stage III (highest risk): >4 pts" | aha-2026 | p16 | p16/narrative/bova-score | narrative |
| bova-score-range | acute-pe | total score 0-7 | RENDERED: "Bova Score"; "0 to 7" | aha-2026 | p16 | p16/narrative/bova-score-range | narrative |
| hestia-disposition | acute-pe | all criteria no: outpatient; >=1 yes: hospitalization; numeric criteria include >24 hours oxygen to maintain >90%, >24 hours IV pain therapy/social need, and CrCl <30 mL/min | RENDERED: "If answer to >=1 of the criterion is Yes"; ">24 hours of oxygen to maintain oxygen saturation >90%"; "creatinine clearance of <30 mL/min" | aha-2026 | p16 | p16/narrative/hestia-disposition | narrative |
| cpes-risk-score | acute-pe | 1 point per factor including HR >=100; 0-5 lower risk, 6 higher risk for normotensive shock defined by cardiac index <=2.2 L/min/m2 | RENDERED: "Heart rate ≥100 bpm"; "assigning 1 pt for each"; "0-5 pts: Lower risk"; "6 pts: Higher risk"; "cardiac index ≤2.2 L/min/m2" | aha-2026 | p16 | p16/narrative/cpes-score | narrative |
| news2-risk-score | acute-pe | NEWS2 >=9: high risk | RENDERED: "NEWS2 >=9: High risk" | aha-2026 | p16 | p16/narrative/news2-cutoff | narrative |
| news2-score-range | acute-pe | total score 0-20 | RENDERED: "NEWS and NEWS2"; "0 to 20" | aha-2026 | p16 | p16/narrative/news2-score-range | narrative |
| normotensive-shock-lactate | category-d2-pe | serum lactate >2 mmol/L | "serum lactate >2 mmol/L" | aha-2026 | p17 | p17/narrative/normotensive-shock-markers | narrative |
| normotensive-shock-urine-output | category-d2-pe | urine output <720 mL in 24 hours | "urine output <720 mL in 24 hours" | aha-2026 | p17 | p17/narrative/normotensive-shock-markers | narrative |
| normotensive-shock-creatinine-increase | category-d2-pe | creatinine increase >=0.3 mg/mL in 24 hours; likely source unit error, preserved literally | "creatinine increase ≥0.3 mg/mL in 24 hours" | aha-2026 | p17 | p17/narrative/normotensive-shock-markers | narrative |
| normotensive-shock-cardiac-index | category-d2-pe | cardiac index <=2.2 L/min/m2 | "index ≤2.2 L/min/m2 from peripheral arterial and mixed venous oxygenation saturation values" | aha-2026 | p17 | p17/narrative/normotensive-shock-markers | narrative |
| map-escalation | category-c3-pe | MAP <80 mm Hg may identify need for escalation | "a MAP <80 mm Hg" | aha-2026 | p17 | p17/hemodynamic-assessment/2 | 2a |
| category-c3-monitoring | category-c3-pe | monitor closely during first 24-72 hours | "within the first 24 to 72 hours for worsening clinical status" | aha-2026 | p18 | p18/narrative/category-c3-monitoring | narrative |
| obesity-doac-choice | obese-acute-pe | BMI >30 kg/m²: DOAC over VKA is reasonable | RENDERED: "In patients with obesity (body mass index [BMI] >30 kg/m²) and acute PE who are receiving oral anticoagulant therapy, treatment with a DOAC (unless contraindicated) over a VKA is reasonable to prevent recurrent PE and reduce major bleeding." | aha-2026 | p26 | p26/anticoagulation-therapy/5 | 2a |
| severe-obesity-lmwh-dose | severe-obesity-lmwh-pe | BMI >40 kg/m2: LMWH dose reduction may be reasonable | "BMI >40 kg/m2" | aha-2026 | p26 | p26/anticoagulation-therapy/6 | 2b |
| ckd-oral-anticoagulant | mild-moderate-ckd-acute-pe | stage 2-3: DOAC over VKA recommended | "mild-to-moderate (stage 2-3) chronic kidney disease" | aha-2026 | p26 | p26/anticoagulation-therapy/10 | 1 |
| ckd-oral-anticoagulant | severe-ckd-acute-pe | stage 4-5 or hemodialysis: apixaban benefit over VKA uncertain | "severe kidney disease (stage 4-5)" | aha-2026 | p26 | p26/anticoagulation-therapy-continued/11 | 2b |
| lmwh-peak-anti-xa-time | monitored-lmwh-pe | measure 3-5 hours after dose at steady state >=3 doses | "measuring a peak anti-Xa level 3 to 5 hours after an LMWH dose once a steady state is reached (≥3 doses) is recommended" | aha-2026 | p26 | p26/anticoagulation-therapy-continued/21 | 1 |
| severe-ckd-anti-xa | ckd-acute-pe | CrCl <30 mL/min: anti-Xa monitoring reasonable | "CrCl of <30 mL/min" | aha-2026 | p26 | p26/anticoagulation-therapy-continued/22 | 2a |
| pregnancy-anti-xa | pregnant-lmwh-pe | at least once per trimester: usefulness not established | "at least once per trimester" | aha-2026 | p26 | p26/anticoagulation-therapy-continued/23 | 2b |
| high-weight-anti-xa | high-weight-lmwh-pe | weight >150 kg or BMI >40 kg/m2: monitoring benefit not established | "weigh >150 kg or have a BMI of >40 kg/m2" | aha-2026 | p27 | p27/anticoagulation-therapy-continued/24 | 2b |
| post-bariatric-doac | post-bariatric-pe | avoid DOAC for at least 4 weeks after procedure | "DOACs should be avoided for at least 4 weeks after their procedure" | aha-2026 | p27 | p27/narrative/post-bariatric-doac | narrative |
| ckd-egfr-stage | ckd-acute-pe | stage 2-3 eGFR 30-89; stage 4 eGFR 15-29; stage 5 eGFR <15 mL/min/1.73 m2 | RENDERED: "patients with moderate (stage 2-3; estimated glomerular filtration rate [eGFR] 30-89 mL/min/1.73 m²) kidney dysfunction. Patients with stage 4 (eGFR between 15-29 mL/min/1.73 m²) CKD, stage 5 (eGFR <15 mL/min/1.73 m²) CKD" | aha-2026 | p28 | p28/narrative/ckd-egfr-stages | narrative |
| severe-obesity-enoxaparin-comparison | severe-obesity-lmwh-pe | lower 0.8 mg/kg versus standard 1.0 mg/kg actual body weight twice daily; evidence comparison, not a prescribed dose | RENDERED: "There is 1 small RCT evaluating a lower versus a standard dose of enoxaparin (0.8 mg/kg versus 1.0 mg/kg actual body weight twice daily) in patients with severe obesity (BMI ≥40 kg/m²)." | aha-2026 | p28 | p28/narrative/enoxaparin-severe-obesity-comparison | narrative |
| norepinephrine-dose | shock-acute-pe | <=15 micrograms/min: little effect on PVR; >15 micrograms/min: add a second vasopressor instead of increasing NE | RENDERED: "At doses ≤15 μg/min, NE has little to no effect on PVR. However, at doses exceeding 15 μg/min, NE may increase PVR. Therefore, instead of further increasing the dose of NE, a second vasopressor agent (eg, vasopressin, phenylephrine) should be added." | aha-2026 | p31 | p31/narrative/norepinephrine-dose | narrative |
| dobutamine-dose | shock-acute-pe | up to 10 micrograms/kg/min | "continuous infusion of dobutamine (up to 10 μg/ kg/min)" | aha-2026 | p31 | p31/narrative/dobutamine-dose | narrative |
| fluid-bolus-volume | shock-acute-pe | selected normotensive low-output patients: small boluses <=500 mL | "small boluses (≤500 mL) may be considered" | aha-2026 | p31 | p31/narrative/fluid-bolus-volume | narrative |
| permanent-ivc-filter-size | ivc-filter-patient | permanent filter reserved when retrievable filter not feasible, such as IVC >30 mm | "mega cava [IVC >30 mm]" | aha-2026 | p34 | p34/narrative/permanent-filter-mega-cava | narrative |
| ivc-filter-retrieval | ivc-filter-patient | retrieve within 29-54 days once PE risk has subsided | RENDERED: "The US Food and Drug Administration (FDA) issued a safety communication recommending IVC filter retrieval within 29 and 54 days after placement, once the risk of PE has subsided" | aha-2026 | p34 | p34/narrative/ivc-filter-retrieval-window | narrative |
| systemic-alteplase-standard | systemic-thrombolysis-pe | alteplase 100 mg over 2 hours | RENDERED: "Standard dose rt-PA (100 mg in 2 hours)" | aha-2026 | p36 | p36/narrative/systemic-alteplase-standard | narrative |
| systemic-alteplase-low-dose | systemic-thrombolysis-pe | 25-50 mg rt-PA may be considered versus standard 100 mg | "(25-50 mg rt-PA), compared with standard dose (100 mg rt-PA), may be as efficacious" | aha-2026 | p37 | p37/narrative/systemic-alteplase-low-dose | narrative |
| systemic-alteplase-six-hour-regimen | systemic-thrombolysis-pe | 25 mg rt-PA over 6 hours; retrospective evaluated regimen, not a recommendation | "patients with acute PE and vital sign abnormalities, treated with 25 mg rt-PA over 6 hours" | aha-2026 | p37 | p37/narrative/systemic-alteplase-six-hour-regimen | narrative |
| cdl-alteplase-dose | cdl-acute-pe | <5 mg/PA not recommended over standard 5-10 mg/PA | RENDERED: "In patients with acute PE who are undergoing CDL, a reduced thrombolytic dose of <5 mg of alteplase per PA is not recommended over a standard dose of 5 to 10 mg of alteplase per PA to reduce the risk of bleeding and/or reduce the rate of fatal or nonfatal clinical deterioration." | aha-2026 | p38 | p38/catheter-directed-thrombolysis-continued/5 | 3 |
| cdl-study-dose-duration-range | cdl-acute-pe | rt-PA 4-24 mg total over 2-24 hours in CDL studies; evidence range, not a prescribed regimen | "The range of doses of rt-PA in CDL studies has been 4 mg to 24 mg total over 2 to 24 hours" | aha-2026 | p38 | p38/narrative/cdl-study-dose-duration-range | narrative |
| cdl-bleeding-dose-observation | cdl-acute-pe | total rt-PA doses up to 20 mg have not demonstrated a higher bleeding rate than lower doses | "total doses up to 20 mg have not demonstrated a higher bleeding rate than lower dose regimens" | aha-2026 | p38 | p38/narrative/cdl-bleeding-dose-observation | narrative |
| first-follow-up | post-acute-pe | within first week after discharge | "within the first week of discharge" | aha-2026 | p41 | p41/follow-up-care-for-acute-pe/1 | 1 |
| three-month-visit | post-acute-pe | at or before 3 months after diagnosis | "at or before 3 months after diagnosis" | aha-2026 | p41 | p41/follow-up-care-for-acute-pe/2 | 1 |
| symptom-screen-duration | post-acute-pe | every visit for at least 1 year | "at every visit for at least 1 year" | aha-2026 | p41 | p41/follow-up-care-for-acute-pe/3 | 1 |
| extended-reassessment | post-acute-pe | beyond 3-6 months: periodic risk-benefit reassessment | "extended phase (beyond 3-6 months from diagnosis)" | aha-2026 | p41 | p41/follow-up-care-for-acute-pe/4 | 1 |
| performance-test-timing | persistent-symptoms-pe | symptomatic 3-6 months after PE: performance testing may be reasonable | "remain symptomatic 3 to 6 months after acute PE" | aha-2026 | p41 | p41/follow-up-care-for-acute-pe/7 | 2b |
| thrombophilia-testing-age | post-acute-pe | no major reversible factor plus family history or age <55 years: testing may be reasonable if management changes | RENDERED: "In patients without a major reversible risk factor for acute PE who have a family history of thrombosis or are <55 years of age, it might be reasonable to perform testing for genetic and acquired thrombophilia if the thrombophilia tests results are anticipated to change management or better inform family risk discussions." | aha-2026 | p41 | p41/follow-up-care-for-acute-pe/9 | 2b |
| early-follow-up-program-window | post-acute-pe | 48 hours-7 days in most programs | "between 48 hours and 7 days" | aha-2026 | p42 | p42/narrative/first-follow-up-window | narrative |
| specialty-clinic-timing | complex-post-acute-pe | within 1-3 months | "should occur within 1 to 3 months" | aha-2026 | p43 | p43/narrative/specialty-clinic-timing | narrative |
| follow-up-consensus-schedule | post-acute-pe | evaluate at 3 months, 6 months, 1 year, and annually while under care | "suggests evaluating the patients at 3 months, 6 months, 1 year, and annually as long as the patient is under care" | aha-2026 | p43 | p43/narrative/follow-up-consensus-schedule | narrative |
| six-minute-walk-path | persistent-symptoms-pe | 30-meter walking path | "requires a 30-meter walking path" | aha-2026 | p43 | p43/narrative/six-minute-walk-path | narrative |
| six-minute-walk-duration | persistent-symptoms-pe | walk at a comfortable pace for 6 minutes | "patients walk at a comfortable pace for 6 minutes" | aha-2026 | p43 | p43/narrative/six-minute-walk-duration | narrative |
| shuttle-walk-course | persistent-symptoms-pe | 10-meter shuttle course | "walking distance in a 10-meter shuttle course" | aha-2026 | p43 | p43/narrative/shuttle-walk-course | narrative |
| compression-travel-duration | travel-history-pe | long-haul travel >=5 hours: compression stockings useful | "long-haul (≥5 h) travel can be useful" | aha-2026 | p45 | p45/patient-activity-and-travel/2 | 2a |
| travel-prophylaxis-duration | travel-related-pe | long distance such as >=4-hour flight: one-time prophylactic LMWH or DOAC | "use of a 1-time prophylactic-intensity anticoagulant dose is reasonable when traveling long distances (eg, ≥4-h flight)" | aha-2026 | p45 | p45/narrative/travel-prophylaxis-duration | narrative |
| travel-restriction | category-c2-e-travel-pe | restrict long-haul travel for 4 weeks after treatment starts or when symptoms have resolved | "Categories C2-E, it may be reasonable to restrict long-haul travel for 4 weeks after initiation of treatment or when symptoms have resolved" | aha-2026 | p45 | p45/patient-activity-and-travel/4 | 2b |
| no-major-reversible-duration | first-pe-no-major-reversible | continue beyond initial 3-6 months into extended phase | "beyond the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/1 | 1 |
| major-reversible-duration | first-pe-major-reversible | stop at end of initial 3-6 months | "stopping anticoagulation at the end of the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/2 | 1 |
| persistent-risk-duration | first-pe-persistent | continue after initial 3-6 months into extended phase | "initial treatment phase (3-6 months) into the extended treatment phase" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/3 | 1 |
| extended-doac-duration | extended-pe | beyond 3-6 months: DOAC over VKA | "beyond the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/4 | 1 |
| extended-cancer-duration | extended-cancer-pe | beyond 3-6 months: DOAC or LMWH over VKA | "beyond the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/5 | 1 |
| extended-vka-duration | extended-no-cancer-no-doac | beyond 3-6 months: VKA over aspirin or no therapy | "beyond the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/6 | 1 |
| extended-half-dose-duration | extended-pe | beyond 3-6 months: half-dose apixaban or rivaroxaban | "beyond the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/7 | 1 |
| minor-reversible-duration | first-pe-minor-reversible | at 3-6 months: shared decision to stop or continue | "at the end of the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/8 | 2a |
| extended-aspirin-duration | extended-no-anticoagulant | beyond 3-6 months: low-dose aspirin over no therapy | "beyond the initial treatment phase (3-6 months)" | aha-2026 | p46 | p46/anticoagulation-therapy-by-recurrence-risk/9 | 2a |
| apixaban-initiation-dose | adult-acute-pe | 10 mg twice daily for 7 days | "apixaban 10 mg twice daily for 7 days" | aha-2026 | p46 | p46/narrative/apixaban-initiation-dose | narrative |
| rivaroxaban-initiation-dose | adult-acute-pe | 15 mg twice daily for 21 days | "rivaroxaban 15 mg twice daily for 21 days" | aha-2026 | p46 | p46/narrative/rivaroxaban-initiation-dose | narrative |
| dabigatran-edoxaban-lead-in | adult-acute-pe | >=5 days parenteral anticoagulation before dabigatran or edoxaban | RENDERED: "≥5 days of parenteral anticoagulation before starting dabigatran or edoxaban" | aha-2026 | p46 | p46/narrative/dabigatran-edoxaban-lead-in | narrative |
| vka-initiation-bridge | adult-acute-pe | parenteral anticoagulation with VKA until INR >=2 | "along with a VKA until achieving an international normalized ratio ≥2" | aha-2026 | p46 | p46/narrative/vka-initiation-bridge | narrative |
| rivaroxaban-extended-dose | extended-pe | 10 mg daily half dose; 20 mg daily full dose | "rivaroxaban 20 mg daily or 10 mg daily" | aha-2026 | p47 | p47/narrative/rivaroxaban-extended-doses | narrative |
| apixaban-extended-dose | extended-pe | 2.5 mg twice daily half dose; 5 mg twice daily full dose | "apixaban 2.5 mg twice daily and apixaban 5 mg twice daily" | aha-2026 | p47 | p47/narrative/apixaban-extended-doses | narrative |
| major-reversible-risk-duration | first-pe-major-reversible | major: general anesthesia >=30 minutes or acute-illness hospitalization >=72 hours while bed-confined | RENDERED: "Surgery with general anesthesia >=30 minutes"; "Hospitalization for acute medical illness >=72 hours" | aha-2026 | p47 | p47/narrative/major-reversible-risk-duration | narrative |
| minor-reversible-risk-duration | first-pe-minor-reversible | minor: general anesthesia <30 minutes, hospital acute illness <72 hours, out-of-hospital bed confinement >=72 hours, or trauma with decreased mobility >=72 hours | RENDERED: "Surgery with general anesthesia <30 minutes"; "Trauma with decreased mobility >=72 hours" | aha-2026 | p47 | p47/narrative/minor-reversible-risk-duration | narrative |
| recurrent-lmwh-escalation | recurrent-cancer-pe | increase LMWH by 20%-25% | "dose escalation of LMWH by 20% to 25%" | aha-2026 | p48 | p48/recurrent-pulmonary-embolism/5 | 2a |
| rivaroxaban-meal-dose | adult-acute-pe | 15 mg and 20 mg doses must be taken with a meal | "rivaroxaban (15 mg and 20 mg doses) requires that it be taken with a meal" | aha-2026 | p49 | p49/narrative/rivaroxaban-with-meal | narrative |
| ctepd-evaluation-time | persistent-symptoms-pe | after >=3 months therapeutic anticoagulation: diagnostic evaluation recommended | RENDERED: "In patients with ongoing dyspnea and/or functional impairment after ≥3 months of therapeutic anticoagulation after an acute PE, a diagnostic evaluation is recommended to assess for CTEPD." | aha-2026 | p49 | p49/persistently-symptomatic-patients-after-acute-pe/1 | 1 |
| pulmonary-rehabilitation-time | persistent-symptoms-pe | despite >=3 months therapeutic anticoagulation: pulmonary rehabilitation reasonable after CTEPD excluded | "patients in whom CTEPD has been excluded but who have ongoing dyspnea and/or functional impairment despite ≥3 months of therapeutic anticoagulation after an acute PE, a pulmonary rehabilitation program is reasonable" | aha-2026 | p50 | p50/persistently-symptomatic-patients-after-acute/6 | 1 |
| repeat-echo-time | post-acute-pe | if baseline echocardiogram normal, repeat at 3-6 months is low yield and may be omitted | "repeated echocardiogram at 3 to 6 months is low yield and may be omitted" | aha-2026 | p50 | p50/narrative/repeat-echo-time | narrative |
| ctepd-trv-probability | persistent-symptoms-pe | TRV <=2.8 m/s plus no PH signs: low probability; TRV >=2.8 m/s plus PH signs: higher probability | RENDERED: "TRV <=2.8 m/s"; "TRV >=2.8 m/s" | aha-2026 | p52 | p52/narrative/ctepd-trv-probability | narrative |
| ph-sign-count | persistent-symptoms-pe | signs from at least 2 of categories A/B/C alter echocardiographic PH probability | RENDERED: "Signs from at least 2 categories (A/B/C) must be present" | aha-2026 | p53 | p53/narrative/ph-sign-count | narrative |
| ph-rv-lv-sign | persistent-symptoms-pe | RV/LV basal diameter or area ratio >1.0 | RENDERED: "RV/LV basal diameter/area ratio >1.0" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |
| ph-lvei-sign | persistent-symptoms-pe | LVEI >1.1 in systole or diastole | RENDERED: "Flattening of the interventricular septum (LVEI >1.1 in systole and/or diastole)" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |
| ph-tapse-spap-sign | persistent-symptoms-pe | TAPSE/sPAP ratio <0.55 mm/mm Hg | RENDERED: "TAPSE/sPAP ratio <0.55 mm/mm Hg" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |
| ph-rvot-at-sign | persistent-symptoms-pe | RVOT acceleration time <105 ms or midsystolic notching | RENDERED: "RVOT AT <105 ms and/or midsystolic notching" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |
| ph-pr-velocity-sign | persistent-symptoms-pe | early diastolic PR velocity >2.2 m/s | RENDERED: "Early diastolic pulmonary regurgitation velocity >2.2 m/s" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |
| ph-pa-diameter-sign | persistent-symptoms-pe | PA diameter >25 mm | RENDERED: "PA diameter >25 mm" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |
| ph-ivc-sign | persistent-symptoms-pe | IVC >21 mm with decreased inspiratory collapse <50% with a sniff or <20% with quiet inspiration | RENDERED: "IVC diameter >21 mm with decreased inspiratory collapse (<50% with a sniff or <20% with quiet inspiration)" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |
| ph-ra-area-sign | persistent-symptoms-pe | RA area >18 cm2 at end systole | RENDERED: "RA area (end-systole) >18 cm2" | aha-2026 | p53 | p53/narrative/ph-echo-signs | narrative |

## Conflicts

- The p17 definition literally states `creatinine increase >=0.3 mg/mL in 24 hours`.
  The unit is likely a source error, but this sheet preserves it without correction in
  `normotensive-shock-creatinine-increase`.

## Coverage

- `p7/clinical-assessment/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p7/clinical-assessment/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p7/clinical-assessment/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing-continued/8` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing-continued/9` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing-continued/10` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing-continued/11` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing-continued/12` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing-continued/13` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing/5` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing/6` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p10/diagnostic-testing/7` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p15/risk-assessment-using-clinical-risk-scores/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p15/risk-assessment-using-clinical-risk-scores/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p15/risk-assessment-using-clinical-risk-scores/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p17/hemodynamic-assessment/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p18/risk-stratification-of-pe-using-biomarkers/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p18/risk-stratification-of-pe-using-biomarkers/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p19/right-ventricular-imaging-for-risk-stratificatio/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p19/right-ventricular-imaging-for-risk-stratificatio/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p20/suitability-for-outpatient-management-of-pe/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p20/suitability-for-outpatient-management-of-pe/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p22/triage-and-placement-in-the-hospital/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p22/triage-and-placement-in-the-hospital/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p22/interhospital-transfers/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p22/interhospital-transfers/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/12` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/13` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/14` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/15` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/16` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/17` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/18` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/19` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy-continued/20` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy/7` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy/8` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p26/anticoagulation-therapy/9` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p27/anticoagulation-therapy-continued/25` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p27/anticoagulation-therapy-continued/26` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p30/hemodynamic-pharmacotherapy/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p30/hemodynamic-pharmacotherapy/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p31/hemodynamic-pharmacotherapy-continued/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p31/sedation-and-ventilatory-strategies/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p31/sedation-and-ventilatory-strategies/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p31/sedation-and-ventilatory-strategies/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p32/mechanical-circulatory-support/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p32/mechanical-circulatory-support/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p32/mechanical-circulatory-support/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p33/inferior-vena-cava-filters-continued/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p33/inferior-vena-cava-filters-continued/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p33/inferior-vena-cava-filters-continued/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p33/inferior-vena-cava-filters-continued/5` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p33/inferior-vena-cava-filters-continued/6` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p33/inferior-vena-cava-filters-continued/7` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p33/inferior-vena-cava-filters/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p35/interventional-advanced-management/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p35/interventional-advanced-management/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p36/systemic-thrombolysis/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p36/systemic-thrombolysis/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p36/systemic-thrombolysis/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p36/systemic-thrombolysis/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p36/systemic-thrombolysis/5` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p37/catheter-directed-thrombolysis/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p37/catheter-directed-thrombolysis/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p38/catheter-directed-thrombolysis-continued/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p38/catheter-directed-thrombolysis-continued/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p38/catheter-directed-thrombolysis-continued/6` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p39/mechanical-thrombectomy/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p39/mechanical-thrombectomy/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p39/mechanical-thrombectomy/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p39/mechanical-thrombectomy/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p39/mechanical-thrombectomy/5` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p40/surgical-embolectomy-continued/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p40/surgical-embolectomy-continued/5` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p40/surgical-embolectomy/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p40/surgical-embolectomy/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p40/surgical-embolectomy/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p41/follow-up-care-for-acute-pe/5` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p41/follow-up-care-for-acute-pe/6` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p41/follow-up-care-for-acute-pe/8` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p42/follow-up-care-for-acute-pe-continued/10` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p42/follow-up-care-for-acute-pe-continued/11` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p42/follow-up-care-for-acute-pe-continued/12` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p42/follow-up-care-for-acute-pe-continued/13` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p42/follow-up-care-for-acute-pe-continued/14` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p45/patient-activity-and-travel/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p45/patient-activity-and-travel/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p48/recurrent-pulmonary-embolism/1` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p48/recurrent-pulmonary-embolism/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p48/recurrent-pulmonary-embolism/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p48/recurrent-pulmonary-embolism/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p49/persistently-symptomatic-patients-after-acute-pe/2` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p49/persistently-symptomatic-patients-after-acute-pe/3` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p49/persistently-symptomatic-patients-after-acute-pe/4` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p50/persistently-symptomatic-patients-after-acute/5` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p50/persistently-symptomatic-patients-after-acute/7` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
- `p50/persistently-symptomatic-patients-after-acute/8` - Qualitative recommendation; no distinct numeric dose, duration, cutoff, or target is stated in this record.
