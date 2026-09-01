# Chronic obstructive pulmonary disease — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the source** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gold-2026 | GOLD | GOLD/GOLD-REPORT-2026-v1.3-8Dec2025_WMV2 | guideline | 2026 v1.3 | 2025-12-08 | https://goldcopd.org/2026-gold-report/ | chosen | bound |

## Scope

**Read:** all 248 pages, including every figure, table, appendix, disclosure, and reference page. The page spans below account for the entire document.

**Not read:** nothing. Two spans yielded no patient-action numeric decision point and carry completed first-read and blind markers. Reference pages are exempt from decision-point extraction.

| span | pages | read |
| --- | --- | --- |
| cover, committees, methodology, contents, and introduction | 1-14 | read 2026-08-31; blind 2026-08-31 |
| definition, burden, etiology, pathogenesis, and clinical manifestations | 15-31 | yes |
| diagnosis, case-finding, initial assessment, and monitoring | 32-60 | yes |
| prevention and stable-COPD management | 61-102 | yes |
| exacerbation definition, assessment, treatment, discharge, and prevention | 103-121 | yes |
| multimorbidity and comorbidity management | 122-139 | yes |
| artificial intelligence and telehealth | 140-148 | read 2026-08-31; blind 2026-08-31 |
| appendices: abbreviations, assessment form, pharmacotherapy, nonpharmacologic care, rehabilitation, and nutrition | 149-174 | yes |
| references | 175-248 | exempt: reference list; no first-read or blind marker required |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| suspected-copd | patients with suspected COPD |
| younger-suspected | younger adults (age < 50 years) with suspected COPD and repeated fixed ratio >= 0.7 |
| borderline-ratio | patients with a single post-bronchodilator FEV1/FVC ratio between 0.6 and 0.8 |
| symptomatic-risk | individuals with symptoms and/or risk factors for COPD |
| copd | patients with COPD |
| copd-treatment-symptoms | patients with diagnosed COPD being assessed for regular symptom treatment |
| copd-ct | patients with COPD being considered for chest CT imaging |
| copd-respiratory-failure-signs | patients with COPD and clinical signs suggestive of respiratory failure or right heart failure |
| aatd-assessment | patients with COPD undergoing assessment for alpha-1 antitrypsin deficiency |
| nicotine-dependent | patients with COPD who smoke |
| copd-cold-heat | patients with COPD living in temperate and colder climates |
| vaccine-general | people eligible for routine vaccination |
| pneumococcal-indication | adults aged >=50 years and adults aged 19-49 years with an underlying medical condition including COPD |
| rsv-older | adults eligible for RSV vaccination |
| group-b | treatment-naive patients with COPD in GOLD Group B |
| group-e-high-eos | treatment-naive patients with COPD in GOLD Group E with high blood eosinophils |
| laba-lama-exacerbation | patients with a moderate or severe exacerbation on LABA+LAMA |
| persistent-exacerbations-low-eos | patients treated with LABA+LAMA who still have exacerbations and eosinophils <100 cells/microliter |
| triple-persistent-high-eos | patients treated with LABA+LAMA+ICS who still have exacerbations and eosinophils >=300 cells/microliter |
| stable-hypoxemia | patients with stable COPD and chronic hypoxemia |
| stable-severe-hypoxemia | patients with stable COPD and severe resting hypoxemia receiving LTOT |
| air-travel | patients with chronic respiratory failure who are on LTOT and plan air travel |
| pulmonary-rehab | people with COPD entering pulmonary rehabilitation |
| lvrs-high-risk | patients with severe emphysema being considered for lung volume reduction surgery |
| transplant-referral | patients with progressive COPD despite maximal treatment who are not candidates for lung volume reduction surgery |
| transplant-listing | patients with COPD being considered for lung-transplant listing |
| acute-exacerbation | patients with an acute COPD exacerbation |
| hospitalized-exacerbation | patients hospitalized with a COPD exacerbation |
| ambulatory-exacerbation | outpatients with a COPD exacerbation |
| niv-improved | patients receiving NIV for acute COPD respiratory failure who have improved |
| post-discharge | patients discharged after hospitalization for a COPD exacerbation |
| exacerbation-discharge-eos | patients with at least one moderate or severe COPD exacerbation and elevated blood eosinophils at discharge |
| copd-hypertension | patients with COPD undergoing cardiovascular assessment |
| copd-ph | patients with COPD and pulmonary hypertension |
| lung-cancer-screening | adults with COPD and a tobacco smoking history who meet lung-cancer screening criteria |
| copd-bronchiectasis | patients with COPD and bronchiectasis |
| copd-ild | patients with COPD and interstitial lung disease |
| copd-metabolic | patients with COPD undergoing metabolic and nutritional assessment |
| copd-low-vitamin-d | patients with COPD and very low baseline vitamin D levels |
| copd-frequent-exacerbations | people with COPD, particularly those with a history of frequent exacerbations |
| copd-mental-screen | patients with COPD undergoing depression or anxiety screening |
| copd-diabetes-screen | patients with COPD whose hemoglobin A1c and fasting glucose have not been tested for more than one year |
| copd-renal | patients with COPD undergoing renal assessment |
| copd-polycythemia | patients with COPD and secondary polycythemia |
| lung-resection | patients with COPD being considered for lung resection |
| ics-candidates | patients with COPD being considered for ICS-containing therapy |
| ics-pneumonia-risk | patients with COPD receiving or being considered for ICS treatment |
| exacerbation-prone | patients with COPD prone to exacerbations |
| aatd-treatment | individuals with AATD-related COPD being considered for augmentation therapy |
| aatd-never-ex | never-smokers or ex-smokers with AATD-related COPD |
| post-cv-event-smoker | patients with COPD requiring nicotine replacement after a cardiovascular event |

## Quantities

| key | verbatim |
| --- | --- |
| diagnosis-ratio | spirometric criterion for airflow obstruction |
| chronic-bronchitis-definition | classical definition of chronic bronchitis |
| repeat-spirometry | confirm airflow obstruction by repeat spirometry |
| case-finding | perform spirometry in individuals with symptoms and/or risk factors |
| caat-threshold | CAAT symptom threshold |
| mmrc-threshold | mMRC breathlessness threshold |
| regular-treatment-threshold | threshold for considering regular treatment for symptoms |
| airflow-grade | GOLD grade of airflow obstruction |
| abe-group | combined symptom and exacerbation-risk group |
| blood-gas-trigger | arterial blood gas measurement trigger |
| chest-ct | consider chest CT imaging |
| aatd-marker | alpha-1 antitrypsin concentration highly suggestive of homozygous deficiency |
| nicotine-dependence | indicators of high nicotine dependence |
| cold-bedroom-temperature | cold-weather bedroom temperature precaution |
| heatwave-indoor-temperature | heatwave indoor temperature precaution |
| influenza-eligibility | influenza vaccine eligibility |
| pneumococcal-eligibility | pneumococcal vaccine eligibility |
| pneumococcal-regimen-pcv20 | PCV13/PCV15/PPSV23 or PCV20 regimen |
| pneumococcal-regimen-pcv21 | PCV21 regimen |
| rsv-universal | universal RSV vaccination |
| rsv-risk | risk-based RSV vaccination |
| group-b-treatment | initial Group B pharmacotherapy |
| group-b-evidence | Group B supporting-trial population |
| group-e-treatment | initial Group E pharmacotherapy |
| escalation | maintenance pharmacotherapy escalation |
| roflumilast | add roflumilast |
| biologic | add biologic therapy |
| ltot-eligibility-low | LTOT eligibility by severe hypoxemia |
| ltot-eligibility-complication | LTOT eligibility with complications |
| ltot-duration | LTOT daily duration |
| inflight-pao2-target | in-flight oxygen target |
| air-travel-no-assessment | air travel without further assessment |
| oxygen-reassessment | reassess LTOT |
| spirometry-monitoring | repeat spirometry |
| rehabilitation-duration | pulmonary rehabilitation program duration |
| rehabilitation-minimum-duration | pulmonary rehabilitation minimum program duration |
| rehabilitation-frequency | pulmonary rehabilitation supervised frequency |
| rehabilitation-intensity-work | pulmonary rehabilitation work intensity |
| rehabilitation-intensity-borg | pulmonary rehabilitation Borg intensity |
| lvrs | avoid lung volume reduction surgery in high-risk patients |
| transplant | transplant referral or listing |
| exacerbation-mild | classify mild acute exacerbation |
| exacerbation-moderate | classify moderate acute exacerbation |
| exacerbation-severe | classify severe acute exacerbation |
| no-respiratory-failure | classify no respiratory failure during hospitalized exacerbation |
| respiratory-failure | classify respiratory failure during hospitalized exacerbation |
| ventilatory-failure | classify ventilatory failure during hospitalized exacerbation |
| bronchodilator-acute | acute bronchodilator frequency |
| corticosteroid-acute | systemic corticosteroid treatment |
| antibiotic-indication-symptoms | symptom-based antibiotic indication |
| antibiotic-indication-other | culture- or ventilation-based antibiotic indication |
| antibiotic-duration | antibiotic duration |
| niv-stop | discontinue NIV |
| discharge-followup-early | early post-discharge follow-up |
| discharge-followup-three-months | three-month post-discharge follow-up |
| discharge-ics | add ICS to dual bronchodilator treatment at discharge |
| vitamin-d | investigate and supplement severe vitamin D deficiency |
| blood-pressure | blood-pressure measurement and treatment threshold |
| ph-definition | pulmonary hypertension definition |
| ph-severe-definition | severe pulmonary hypertension definition |
| ph-referral | pulmonary hypertension referral |
| lung-cancer-ldct | annual low-dose CT screening |
| phq2-screen | depression screening score |
| gad2-screen | anxiety screening score |
| diabetes-screen | diabetes laboratory interval |
| renal-definition | renal-failure definition |
| renal-medication-review | renal measurement and medication review |
| polycythemia-definition | secondary polycythemia definition |
| polycythemia-evaluation | secondary polycythemia evaluation |
| ild-followup | interstitial lung disease monitoring |
| bmi-monitoring | BMI monitoring |
| bmi-goal | BMI nutrition goal |
| lung-resection-assessment | lung-resection risk assessment |
| lung-resection-postponement | postponement of lung resection |
| vitamin-d-outcome-subgroup | vitamin D supplementation outcome subgroup |
| vitamin-d-checking | consider checking vitamin D deficiency |
| bronchiectasis-ics | ICS use with bronchiectasis |
| ics-low-eosinophils | low-eosinophil ICS benefit threshold |
| ics-high-eosinophils | high-eosinophil ICS benefit threshold |
| ics-pneumonia-clinical-risk | clinical pneumonia risk factors with ICS |
| ics-pneumonia-eosinophils | eosinophil pneumonia risk threshold |
| macrolide-prevention | chronic macrolide regimen |
| aatd-effect-range | AATD augmentation observational effect range |
| aatd-suitable-range | AATD augmentation observational suitability range |
| aatd-genotype-zz | AATD augmentation ZZ genotype evidence |
| aatd-genotype-null | AATD augmentation Z/null and null/null assessment |
| aatd-genotype-other | AATD augmentation other-genotype disposition |
| aatd-progressive | AATD progressive-disease indication |
| aatd-low-fev1 | AATD augmentation at lower FEV1 |
| aatd-high-fev1 | AATD augmentation at higher FEV1 |
| aatd-cost-discussion | AATD augmentation individual cost-benefit discussion |
| nicotine-replacement | start nicotine replacement after cardiovascular event |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| diagnosis-ratio | suspected-copd | post-bronchodilator FEV1/FVC <0.7 | "FEV1/FVC < 0.7" | gold-2026 | p40 | p40/narrative/diagnosis-ratio | narrative |
| chronic-bronchitis-definition | suspected-copd | cough and sputum production for >=3 months/year for two consecutive years, absent another explanatory condition | "The classic description defines chronic bronchitis as chronic cough and sputum production for at least 3 months per year for two consecutive years, in the absence of other conditions that can explain these symptoms (an important caveat that is often ignored)." | gold-2026 | p26 | p26/narrative/chronic-bronchitis-definition | narrative |
| diagnosis-ratio | younger-suspected | if age <50 years and repeated ratio >=0.7, compare with LLN or use z-scores | "If COPD is suspected in younger adults (age < 50 years) who have a repeated fixed ratio ≥ 0.7, comparing the ratio to a predicted LLN or using z-scores (see below) may help when deciding how to best manage this small number of patients." | gold-2026 | p41 | p41/narrative/younger-ratio | narrative |
| repeat-spirometry | borderline-ratio | repeat on a separate occasion when ratio 0.6-0.8 | RENDERED: "Assessment of the presence or absence of airflow obstruction based on a single measurement of the post-bronchodilator FEV1/FVC ratio should be confirmed by repeat spirometry on a separate occasion if the value is between 0.6 and 0.8, as in some cases the ratio may change as a result of biological variation when measured at a later interval." | gold-2026 | p41 | p41/narrative/repeat-spirometry | narrative |
| repeat-spirometry | suspected-copd | initial ratio <0.6 is very unlikely to rise spontaneously above 0.7 | "ratio is less than 0.6 it is very unlikely to rise spontaneously above 0.7" | gold-2026 | p41 | p41/narrative/low-ratio | narrative |
| case-finding | symptomatic-risk | unexplained dyspnea, >20 pack-years, recurrent chest infections, or early-life events prompt targeted spirometry | "In active case-finding, respiratory symptoms and risks for COPD (e.g. unexplained dyspnea, or > 20 pack-years of smoking, or history of recurrent chest infections, or history of early life events) are elicited from the individual via questionnaire and based on positive responses they are targeted to receive spirometry." | gold-2026 | p45 | p45/narrative/case-finding | narrative |
| regular-treatment-threshold | copd-treatment-symptoms | SGRQ >=25 | "Therefore, it is recommended that a symptom score equivalent to SGRQ score ≥ 25 should be used as the threshold for considering regular treatment for symptoms including breathlessness, particularly since this corresponds to the range of severity seen in patients recruited to the trials that have provided the evidence base for treatment recommendations." | gold-2026 | p51 | p51/narrative/sgrq-threshold | narrative |
| caat-threshold | copd | CAAT >=10 | "The equivalent cut-point for the CAAT™ is 10." | gold-2026 | p51 | p51/narrative/caat-threshold | narrative |
| mmrc-threshold | copd | mMRC >=2 separates less from more breathlessness | "an mMRC of ≥ 2 is still included as a threshold" | gold-2026 | p51 | p51/narrative/mmrc-threshold | narrative |
| airflow-grade | copd | GOLD 1: FEV1 >=80%; GOLD 2: 50% <=FEV1 <80%; GOLD 3: 30% <=FEV1 <50%; GOLD 4: FEV1 <30% predicted | RENDERED: "In patients with COPD (FEV1/FVC < 0.7): GOLD 1, FEV1 ≥ 80% predicted; GOLD 2, 50% ≤ FEV1 < 80% predicted; GOLD 3, 30% ≤ FEV1 < 50% predicted; GOLD 4, FEV1 < 30% predicted" | gold-2026 | p49 | p49/narrative/airflow-grade | narrative |
| abe-group | copd | E: >=1 moderate or severe exacerbation in prior year; with 0 exacerbations, A if mMRC 0-1 and CAAT <10, B if mMRC >=2 or CAAT >=10 | RENDERED: "One or more (≥1) moderate or severe exacerbations in the previous year; Zero (0) moderate or severe exacerbations in the previous year; mMRC 0-1, CAAT < 10; mMRC ≥ 2, CAAT ≥ 10" | gold-2026 | p54 | p54/narrative/abe-group | narrative |
| blood-gas-trigger | copd-respiratory-failure-signs | if peripheral oxygen saturation <=92%, measure arterial blood gases | "If peripheral oxygen saturation is ≤ 92%, arterial blood gases should be measured" | gold-2026 | p56 | p56/narrative/blood-gas-trigger | narrative |
| chest-ct | copd-ct | consider for persistent exacerbations, symptoms disproportionate to lung-function severity or refractory to treatment, FEV1 15%-45% with significant hyperinflation and gas trapping, or lung-cancer screening eligibility | "In summary, chest CT imaging should be considered for patients with COPD who have persistent exacerbations, symptoms out of proportion to disease severity on lung function testing or refractory to medical management, FEV1 between 15% and 45% predicted with significant hyperinflation and gas trapping, or for those who meet criteria for lung cancer screening" | gold-2026 | p58 | p58/narrative/chest-ct | narrative |
| aatd-marker | aatd-assessment | AAT concentration <20% normal is highly suggestive of homozygous deficiency | "A low concentration (< 20% normal) is highly suggestive of homozygous deficiency." | gold-2026 | p59 | p59/narrative/aatd-marker | narrative |
| nicotine-dependence | nicotine-dependent | smoking within 30 minutes of waking; >=20 cigarettes/day; Fagerstrom 7-10; Heaviness of Smoking Index 5-6 | "smoking within 30 min of waking up, smoking at night, consuming ≥ 20 cigarettes per day, a score of 7 to 10 on the Fagerström scale or 5 to 6 on the Heaviness of Smoking Index" | gold-2026 | p65 | p65/narrative/nicotine-dependence | narrative |
| cold-bedroom-temperature | copd-cold-heat | bedroom >18 C during cold weather | "keep bedroom temperatures above 18°C during cold weather" | gold-2026 | p68 | p68/narrative/cold-bedroom-temperature | narrative |
| heatwave-indoor-temperature | copd-cold-heat | living spaces <32 C and sleeping spaces <24 C | "try to keep living spaces < 32°C and sleeping spaces < 24°C" | gold-2026 | p68 | p68/narrative/heatwave-indoor-temperature | narrative |
| influenza-eligibility | vaccine-general | annual influenza for everyone age >=6 months without contraindications | "Routine annual influenza vaccination is recommended for all people aged ≥ 6 months who do not have contraindications, and should be prioritized in individuals with chronic conditions like COPD." | gold-2026 | p68 | p68/narrative/influenza-vaccine | narrative |
| pneumococcal-eligibility | pneumococcal-indication | indicated for adults >=50 and adults 19-49 with an underlying medical condition | "Pneumococcal vaccinations, pneumococcal conjugated vaccine (PCV21, PCV20, PCV15 or PCV13) and pneumococcal polysaccharide vaccine (PPSV23), are indicated for all adults aged ≥ 50 years, and adults aged 19-49 years with an underlying medical condition such as chronic lung disease (including COPD, emphysema, cystic fibrosis, and asthma) or solid organ transplant etc." | gold-2026 | p68 | p68/narrative/pneumococcal-eligibility | narrative |
| pneumococcal-regimen-pcv20 | pneumococcal-indication | PCV13 or PCV15 followed by PPSV23, or one-dose PCV20 | "The current recommendation is PCV13 or PCV15 followed by PPSV23 or one-dose PCV20" | gold-2026 | p68 | p68/narrative/pneumococcal-regimen-pcv20 | narrative |
| pneumococcal-regimen-pcv21 | pneumococcal-indication | one-dose PCV21 | "one-dose PCV21" | gold-2026 | p68 | p68/narrative/pneumococcal-regimen-pcv21 | narrative |
| rsv-universal | rsv-older | universal if age >=75 and not previously vaccinated | "For adults aged ≥75 years, the vaccination is universally recommended for if they have not been previously vaccinated." | gold-2026 | p70 | p70/narrative/rsv-universal | narrative |
| rsv-risk | rsv-older | age 50-74 if risk factor for severe RSV disease | "For adults aged 50-74 years, vaccination is recommended if they have a risk factor or other indication that increases their risk for severe RSV disease" | gold-2026 | p70 | p70/narrative/rsv-risk | narrative |
| spirometry-monitoring | copd | repeat at least annually | "Spirometry should be repeated at least annually." | gold-2026 | p74 | p74/narrative/annual-spirometry | narrative |
| group-b-treatment | group-b | initiate LABA+LAMA | "Treatment should be initiated with a LABA+LAMA combination." | gold-2026 | p75 | p75/narrative/group-b | narrative |
| group-b-evidence | group-b | supporting trial population: <=1 moderate exacerbation in prior year and CAAT >=10 | "It has been shown in a RCT that in patients with ≤ 1 moderate exacerbation in the year before the study and a CAAT™ ≥ 10 LABA+LAMA is superior to a LAMA with regard to several endpoints." | gold-2026 | p75 | p75/narrative/group-b-evidence-population | narrative |
| group-e-treatment | group-e-high-eos | consider LABA+LAMA+ICS when eosinophils >=300 cells/microliter | "Consider LABA+LAMA+ICS as initial therapy in group E if eosinophil counts are ≥ 300 cells/µL" | gold-2026 | p75 | p75/narrative/group-e-triple | narrative |
| escalation | laba-lama-exacerbation | add ICS after moderate or severe exacerbation; benefit may begin at eosinophils >=100 cells/microliter | "In patients who have a moderate or severe exacerbation on LABA+LAMA therapy we suggest escalation to LABA+LAMA+ICS (Figure 3.10). A beneficial response after the addition of ICS may be observed at blood eosinophil counts ≥ 100 cells/µL, with a greater magnitude of response more likely with higher eosinophil counts." | gold-2026 | p77 | p77/narrative/escalate-triple | narrative |
| roflumilast | persistent-exacerbations-low-eos | consider if FEV1 <50%, chronic bronchitis, and prior exacerbation hospitalization | "Among those with FEV1 < 50%, symptoms of chronic bronchitis and history of a prior exacerbation resulting in hospitalization, consider adding roflumilast." | gold-2026 | p77 | p77/narrative/roflumilast | narrative |
| biologic | triple-persistent-high-eos | consider dupilumab with chronic bronchitis or mepolizumab with or without chronic bronchitis when eosinophils >=300 cells/microliter | "Among patients with blood eosinophils ≥ 300 cells/µL, consider adding dupilumab (if chronic bronchitis) or mepolizumab (with and without chronic bronchitis)" | gold-2026 | p77 | p77/narrative/biologic | narrative |
| ltot-eligibility-low | stable-hypoxemia | PaO2 <=55 mmHg or SaO2 <=88%, confirmed twice over three weeks | "PaO2 at or below 55 mmHg (7.3 kPa) or SaO2 at or below 88%, with or without hypercapnia confirmed twice over a three-week period" | gold-2026 | p87 | p87/narrative/ltot-low | narrative |
| ltot-eligibility-complication | stable-hypoxemia | PaO2 55-60 mmHg or SaO2 88% with pulmonary hypertension, edema, or hematocrit >55% | "PaO2 between 55 mmHg (7.3 kPa) and 60 mmHg (8.0 kPa), or SaO2 of 88%, if there is evidence of pulmonary hypertension, peripheral edema suggesting congestive cardiac failure, or polycythemia (hematocrit > 55%)." | gold-2026 | p87 | p87/narrative/ltot-complication | narrative |
| ltot-duration | stable-severe-hypoxemia | >15 hours/day is indicated | "The long-term administration of oxygen (> 15 hours per day; LTOT) is indicated for patients with stable COPD" | gold-2026 | p87 | p87/narrative/ltot-duration-indication | narrative |
| ltot-duration | stable-severe-hypoxemia | newer evidence did not support >15 hours/day: 24 hours/day was not better than 15 hours/day within one year | "LTOT used for 24 hours per day did not result in a lower risk of hospitalization or death within one year compared to therapy for 15 hours per day. Thus, the recommendation to use oxygen > 15 hours per day is not supported by newer evidence." | gold-2026 | p87 | p87/narrative/ltot-newer-evidence | narrative |
| inflight-pao2-target | air-travel | maintain in-flight PaO2 >=50 mmHg; for moderate-to-severe sea-level hypoxemia use oxygen 3 L/min by nasal cannula or 31% by Venturi mask | "patients should ideally maintain an in-flight PaO2 of at least 6.7 kPa (50 mmHg). Studies indicate that this can be achieved in those with moderate to severe hypoxemia at sea level by supplementary oxygen at 3 liters/min by nasal cannula or 31% by Venturi facemask." | gold-2026 | p88 | p88/narrative/inflight-pao2 | narrative |
| air-travel-no-assessment | air-travel | resting oxygen saturation >95% and walking-test oxygen saturation >84% may travel without further assessment | "Those with a resting oxygen saturation > 95% and 6MWD oxygen saturation > 84% may travel without further assessment" | gold-2026 | p88 | p88/narrative/air-travel-no-assessment | narrative |
| oxygen-reassessment | stable-hypoxemia | reassess 60-90 days after starting LTOT | "Once placed on LTOT the patient should be re-evaluated after 60 to 90 days" | gold-2026 | p88 | p88/narrative/ltot-reassessment | narrative |
| rehabilitation-duration | pulmonary-rehab | optimum 6-8 weeks; no additional benefit at 12 weeks | "Optimum benefits are achieved from programs lasting 6 to 8 weeks. Available evidence indicates that there are no additional benefits from extending pulmonary rehabilitation to 12 weeks." | gold-2026 | p86 | p86/narrative/rehab-duration | narrative |
| rehabilitation-frequency | pulmonary-rehab | supervised exercise at least twice weekly | "Supervised exercise training at least twice weekly is recommended" | gold-2026 | p86 | p86/narrative/rehab-frequency | narrative |
| lvrs | lvrs-high-risk | FEV1 <=20% predicted plus homogeneous emphysema or DLCO <=20% predicted identifies higher mortality with LVRS | "LVRS has been demonstrated to result in higher mortality than medical management in patients with severe emphysema who have FEV1 ≤ 20% predicted and either homogeneous emphysema on HRCT or a DLco ≤ 20% of predicted." | gold-2026 | p98 | p98/narrative/lvrs-high-risk | narrative |
| transplant | transplant-referral | referral: BODE 5-6, PaCO2 >50 mmHg and/or PaO2 <60 mmHg, and FEV1 <25% | "Patients with COPD should be referred for consideration of lung transplantation when they have progressive disease despite maximal medical treatment, are not candidates for lung volume reduction surgery, have a BODE index of 5 to 6, a PaCO2 > 50 mmHg (6.6 kPa) and/or PaO2 < 60 mmHg (8 kPa) and FEV1 < 25%." | gold-2026 | p102 | p102/narrative/transplant-referral | narrative |
| transplant | transplant-listing | BODE >=7, FEV1 <15%-20%, three or more severe exacerbations in prior year, one severe exacerbation with hypercapnic respiratory failure, or moderate-to-severe pulmonary hypertension | "They should be considered for listing for lung transplantation when: the BODE index is ≥ 7; FEV1 is < 15% to 20%; they have had three or more severe exacerbations during the previous year; one severe exacerbation with hypercapnic respiratory failure; or have moderate to severe pulmonary hypertension." | gold-2026 | p102 | p102/narrative/transplant-listing | narrative |
| discharge-ics | exacerbation-discharge-eos | consider adding ICS to dual bronchodilator treatment at discharge after >=1 moderate or severe exacerbation with elevated eosinophils | "In patients with ≥ 1 moderate or severe exacerbation and elevated blood eosinophil levels, the addition of ICSs to a dual bronchodilator regimen should be considered at discharge." | gold-2026 | p103 | p103/narrative/discharge-ics | narrative |
| antibiotic-duration | acute-exacerbation | total 5 days for patients with purulent sputum, prior lung infections, or similar bacterial features | "Antibiotics are recommended for a total of 5 days in patients with purulent sputum, prior history of lung infections, etc." | gold-2026 | p103 | p103/narrative/antibiotic-five-days | narrative |
| exacerbation-mild | acute-exacerbation | VAS <5, RR <24, HR <95, SaO2 >=92% and change <=3%, CRP <10 mg/L | RENDERED: "Mild: Dyspnea VAS < 5; Respiratory rate < 24 breaths/min; Heart rate < 95 bpm; Resting SaO2 ≥ 92% breathing ambient air (or patient's usual oxygen prescription) AND change ≤ 3% (when known); CRP < 10 mg/L (if available)" | gold-2026 | p105 | p105/narrative/rome-mild | narrative |
| exacerbation-moderate | acute-exacerbation | moderate when at least three of five: VAS >=5, RR >=24, HR >=95, SaO2 <92% and/or change >3%, CRP >=10 mg/L | RENDERED: "Moderate (meets at least three of five*): Dyspnea VAS ≥ 5; Respiratory rate ≥ 24 breaths/min; Heart rate ≥ 95 bpm; Resting SaO2 < 92% breathing ambient air (or patient's usual oxygen prescription) AND/OR change > 3% (when known); CRP ≥ 10 mg/L (if available)" | gold-2026 | p105 | p105/narrative/rome-moderate | narrative |
| exacerbation-severe | acute-exacerbation | moderate clinical features plus PaO2 <=60 and/or PaCO2 >45 with pH <7.35 | RENDERED: "Severe: Dyspnea, respiratory rate, heart rate, SaO2 and CRP same as moderate; If obtained, ABG may show hypoxemia (PaO2 ≤ 60 mmHg) and/or hypercapnia and acidosis (PaCO2 > 45 mmHg and pH < 7.35)" | gold-2026 | p105 | p105/narrative/rome-severe | narrative |
| no-respiratory-failure | hospitalized-exacerbation | RR <=24, HR <=95, Venturi 24%-35% FiO2 | "No respiratory failure: Respiratory rate: ≤ 24 breaths per minute; heart rate ≤ 95 bpm, no use of accessory respiratory muscles; no changes in mental status; hypoxemia improved with supplemental oxygen given via Venturi mask 24-35% FiO2; no increase in PaCO2." | gold-2026 | p105 | p105/narrative/no-respiratory-failure | narrative |
| respiratory-failure | hospitalized-exacerbation | RR >24, HR >95, Venturi >35% FiO2, PaCO2 50-60 mmHg | "Respiratory failure: Respiratory rate: > 24 breaths per minute; heart rate > 95 bpm, using accessory respiratory muscles; appropriate mental status; hypoxemia improved with supplemental oxygen via Venturi mask > 35% FiO2; hypercapnia i.e., PaCO2 increased compared with baseline or elevated 50-60 mmHg." | gold-2026 | p105 | p105/narrative/respiratory-failure | narrative |
| ventilatory-failure | hospitalized-exacerbation | RR >24, HR >95, FiO2 >40%, PaCO2 >60 mmHg, pH <=7.25 | "Ventilatory Failure: Respiratory rate: > 24 breaths per minute; heart rate > 95 bpm, using accessory respiratory muscles; acute changes in mental status; hypoxemia not improved with supplemental oxygen via Venturi mask or requiring FiO2 > 40%; hypercapnia i.e., PaCO2 increased compared with baseline or elevated > 60 mmHg and the presence of acidosis (pH ≤ 7.25)." | gold-2026 | p105 | p105/narrative/ventilatory-failure | narrative |
| bronchodilator-acute | acute-exacerbation | one nebulized dose hourly for 2-3 doses, or pMDI one or two puffs hourly for two or three doses, then every 2-4 hours by response | "one dose of nebulized medication every hour for 2-3 doses or use a pMDI one or two puffs every one hour for two or three doses and then every 2-4 hours" | gold-2026 | p114 | p114/narrative/acute-bronchodilator | narrative |
| corticosteroid-acute | acute-exacerbation | prednisone-equivalent 40 mg/day for 5 days | "A dose of 40 mg prednisone-equivalent per day for 5 days is recommended." | gold-2026 | p114 | p114/narrative/acute-steroid | narrative |
| antibiotic-indication-symptoms | acute-exacerbation | give for at least two of increased dyspnea, fever, sputum volume, and sputum purulence when purulence is one | "Have these at least two of these symptoms: increase in dyspnea, fever, sputum volume, and sputum purulence, if increased purulence of sputum is one of these symptoms" | gold-2026 | p115 | p115/narrative/antibiotic-indication | narrative |
| antibiotic-indication-other | acute-exacerbation | also give for prior positive sputum culture or need for invasive or noninvasive mechanical ventilation | RENDERED: "Prior positive sputum culture during prior exacerbation; Require mechanical ventilation (invasive or noninvasive)." | gold-2026 | p115 | p115/narrative/antibiotic-other-indications | narrative |
| antibiotic-duration | acute-exacerbation | recommended length 5-7 days | "The recommended length of antibiotic therapy is 5-7 days." | gold-2026 | p116 | p116/narrative/antibiotic-duration-general | narrative |
| antibiotic-duration | ambulatory-exacerbation | <=5 days | "We recommend a duration of ≤ 5 days of antibiotic treatment for outpatient treatment of COPD exacerbations." | gold-2026 | p116 | p116/narrative/antibiotic-duration-outpatient | narrative |
| niv-stop | niv-improved | directly discontinue after patient tolerates >=4 hours unassisted breathing | "Once patients improve and can tolerate at least 4 hours of unassisted breathing, NIV can be directly discontinued" | gold-2026 | p118 | p118/narrative/niv-stop | narrative |
| discharge-followup-early | post-discharge | follow up within 1 month | "Further, early follow-up (within 1 month) following discharge to review patient status and therapy should be undertaken when possible" | gold-2026 | p121 | p121/narrative/discharge-followup-early | narrative |
| discharge-followup-three-months | post-discharge | additional follow-up at 3 months | "Additional follow-up at 3 months is recommended to ensure a return to the stable clinical state" | gold-2026 | p121 | p121/narrative/discharge-followup-three-months | narrative |
| vitamin-d | hospitalized-exacerbation | assess for severe deficiency <10 ng/mL or <25 nM and supplement if required | "all patients hospitalized for exacerbations should be assessed and investigated for severe deficiency (< 10 ng/ml or < 25 nM) followed by supplementation if required" | gold-2026 | p111 | p111/narrative/vitamin-d | narrative |
| blood-pressure | copd-hypertension | measure at every evaluation; >130/80 mmHg is abnormal and merits treatment | "All patients should have their blood pressure measured at each medical evaluation, potentially complemented with home monitoring, with values > 130/80 mmHg abnormal and meriting treatment." | gold-2026 | p126 | p126/narrative/blood-pressure | narrative |
| ph-definition | copd-ph | PH is mPAP >20 mmHg | "PH is defined by an elevated mPAP > 20 mmHg" | gold-2026 | p128 | p128/narrative/ph-definition | narrative |
| ph-severe-definition | copd-ph | severe PH-COPD is PVR >5 Wood units | "increased peripheral vascular resistance > 5 Wood Units" | gold-2026 | p128 | p128/narrative/severe-ph-definition | narrative |
| ph-referral | copd-ph | refer to a PH center for right-heart catheterization and multidisciplinary assessment | "Patients with PH-COPD should be referred to a PH center with experience in respiratory diseases where they will undergo right heart catheterization and multidisciplinary assessment to guide treatment decision" | gold-2026 | p129 | p129/narrative/ph-referral | narrative |
| lung-cancer-ldct | lung-cancer-screening | ACS: consider age 50-80 with 20 pack-years regardless of years since quitting | "The American Cancer Society now suggests individuals aged 50-80 with 20 pack years smoking history regardless of years since quitting should be considered for lung cancer with CT imaging" | gold-2026 | p57 | p57/narrative/acs-lung-cancer-screening | narrative |
| lung-cancer-ldct | lung-cancer-screening | USPSTF: annual LDCT age 50-80 with 20 pack-years and current smoking or quit within 15 years | "The USPSTF now recommends annual screening for lung cancer with low-dose CT in adults aged 50-80 years who have a 20-pack year smoking history and currently smoke, or who quit smoking within the past 15 years." | gold-2026 | p130 | p130/narrative/uspstf-lung-cancer-screening | narrative |
| lung-cancer-ldct | lung-cancer-screening | USPSTF stop when not smoked for 15 years or a health problem substantially limits life expectancy or curative-surgery ability/willingness | "They recommend stopping screening once either the person has not smoked for 15 years or develops a health problem that substantially limits life expectancy or the ability or willingness to have curative lung surgery." | gold-2026 | p130 | p130/narrative/uspstf-stop-screening | narrative |
| bronchiectasis-ics | copd-bronchiectasis | eosinophils >=300 cells/microliter may support ICS; frequent lower respiratory infections support considering cessation | "A blood eosinophil threshold of 300 cells/µL could be used to support ICS use, although if lower respiratory tract infections are frequent, ICS cessation should be considered." | gold-2026 | p132 | p132/narrative/bronchiectasis-ics | narrative |
| ild-followup | copd-ild | assess DLCO every 6-12 months | "we recommend intermittent follow-up, including assessment of DLco every 6-12 months" | gold-2026 | p133 | p133/narrative/ild-followup | narrative |
| phq2-screen | copd-mental-screen | scores less than three suggest no important depression | RENDERED: "The Patient Health Questionnaire-2 for depression, with scores less than three suggesting no important depression" | gold-2026 | p133 | p133/narrative/phq2-screen | narrative |
| gad2-screen | copd-mental-screen | use the same score threshold as PHQ-2 | RENDERED: "the Generalized Anxiety Disorder-2 for anxiety, with the same score threshold, can be used as a screening tool" | gold-2026 | p134 | p134/narrative/gad2-screen | narrative |
| diabetes-screen | copd-diabetes-screen | measure hemoglobin A1c and fasting glucose when not tested for >1 year | "Measurement of hemoglobin A1c and fasting blood glucose for patients who have not had these tests in more than a year can help verify a diagnosis and monitor disease control." | gold-2026 | p134 | p134/narrative/diabetes-screen | narrative |
| bmi-monitoring | copd-metabolic | measure BMI at all visits | "BMI should be measured at all visits, and changes monitored over time." | gold-2026 | p135 | p135/narrative/bmi-monitoring | narrative |
| bmi-goal | copd-metabolic | attain and maintain BMI 21-30 kg/m2 | "Optimization of BMI includes lifestyle management implementing regular exercise, adequate nutrition to attain and maintain BMI 21-30 kg/m2." | gold-2026 | p135 | p135/narrative/bmi-target | narrative |
| renal-definition | copd-renal | renal failure defined as GFR <60 mL/min/1.73 m2 | "The prevalence of renal failure, defined as GFR < 60 mL/min/1.73 m2" | gold-2026 | p136 | p136/narrative/renal-definition | narrative |
| renal-medication-review | copd-renal | measure estimated GFR and review potentially nephrotoxic or renally eliminated medications | "Estimated GFR should be measured, and the use of medication should be checked, since patients with COPD frequently receive potentially nephrotoxic drugs, such as non-steroidal anti-inflammatory drugs, or treatments that are eliminated via the kidney." | gold-2026 | p136 | p136/narrative/renal-action | narrative |
| polycythemia-definition | copd-polycythemia | hemoglobin >=17 g/dL in males or >=15 g/dL in females | "when defined as hemoglobin ≥ 17g/dL in males and ≥ 15g/dL in females" | gold-2026 | p137 | p137/narrative/polycythemia-definition | narrative |
| polycythemia-evaluation | copd-polycythemia | evaluate for uncorrected hypoxemia and comorbidities needing specific intervention | "if secondary polycythemia is present a careful evaluation should be performed to determine uncorrected hypoxemia or to rule out the presence of any comorbidities that require a specific intervention." | gold-2026 | p137 | p137/narrative/polycythemia-action | narrative |
| lung-resection-assessment | lung-resection | further assessment if predicted postoperative FEV1 or DLCO <30%-40%, or peak VO2 <10 mL/kg/min or 35% predicted; the source does not state an operator for 35% | RENDERED: "The risk of postoperative complications from lung resection appears to be increased in patients with decreased predicted postoperative pulmonary function (FEV1 or DLco < 30-40% predicted) or exercise capacity (peak VO2 < 10 mL/kg/min or 35% predicted)." | gold-2026 | p138 | p138/narrative/lung-resection-risk | narrative |
| lung-resection-postponement | lung-resection | postpone surgery if an exacerbation is present | "Surgery should be postponed if an exacerbation is present." | gold-2026 | p138 | p138/narrative/postpone-surgery | narrative |
| vitamin-d-outcome-subgroup | copd-low-vitamin-d | supplementation reduced moderate/severe exacerbations when baseline vitamin D <25 nmol/L | "A meta-analysis of RCTs found that vitamin D supplementation significantly reduced moderate/severe exacerbations in patients with very low baseline levels (< 25 nmol/L)." | gold-2026 | p138 | p138/narrative/vitamin-d-outcome | narrative |
| vitamin-d-checking | copd-frequent-exacerbations | consider checking for vitamin D deficiency, particularly with frequent exacerbations | "checking for vitamin D deficiency in people with COPD, particularly if the patient has a history of frequent exacerbations." | gold-2026 | p139 | p139/narrative/vitamin-d-checking | narrative |
| nicotine-replacement | post-cv-event-smoker | start >2 weeks after cardiovascular event | "the evidence suggests that this treatment can and should be started > 2 weeks after a cardiovascular event." | gold-2026 | p153 | p153/narrative/nrt-after-cv-event | narrative |
| ics-low-eosinophils | ics-candidates | <100 cells/microliter predicts little or no effect | "ICS containing regimens have little or no effect at a blood eosinophil count < 100 cells/µL" | gold-2026 | p161 | p161/narrative/ics-low-eosinophils | narrative |
| ics-high-eosinophils | ics-candidates | >=300 cells/microliter predicts greatest likelihood of benefit | "The threshold of a blood eosinophil count ≥ 300 cells/µL identifies the top of the continuous relationship between eosinophils and ICS, and can be used to identify patients with the greatest likelihood of treatment benefit with ICS." | gold-2026 | p161 | p161/narrative/ics-high-eosinophils | narrative |
| ics-pneumonia-clinical-risk | ics-pneumonia-risk | higher risk includes current smoking, age >=55, prior exacerbation or pneumonia, BMI <25, poor mMRC grade, or severe obstruction | "Patients at higher risk of pneumonia include those who currently smoke, are aged ≥ 55 years, have a history of prior exacerbations or pneumonia, a BMI < 25 kg/m2, a poor mMRC dyspnea grade and/or severe airflow obstruction." | gold-2026 | p161 | p161/narrative/ics-pneumonia-risk | narrative |
| ics-pneumonia-eosinophils | ics-pneumonia-risk | eosinophils <2% independently increase pneumonia risk | "Independent of ICS use, there is evidence that a blood eosinophil count < 2% increases the risk of developing pneumonia." | gold-2026 | p161 | p161/narrative/eosinophil-pneumonia-risk | narrative |
| macrolide-prevention | exacerbation-prone | azithromycin 250 mg/day or 500 mg three times/week, or erythromycin 250 mg two times/day, for one year | "Azithromycin (250 mg/day or 500 mg three times per week) or erythromycin (250 mg two times per day) for one year in patients prone to exacerbations reduced the risk of exacerbations compared to usual care." | gold-2026 | p163 | p163/narrative/macrolide | narrative |
| aatd-effect-range | aatd-treatment | observational effect was most marked at FEV1 35%-49% predicted | "this reduction is most effective for patients with FEV1 35% to 49% predicted" | gold-2026 | p166 | p166/narrative/aatd-effect-range | narrative |
| aatd-suitable-range | aatd-never-ex | FEV1 35%-60% predicted suggested as most suitable | "an FEV1 of 35% to 60% predicted have been suggested as those most suitable for AATD augmentation therapy" | gold-2026 | p166 | p166/narrative/aatd-suitable-range | narrative |
| aatd-genotype-zz | aatd-treatment | evidence focused almost exclusively on ZZ genotype | RENDERED: "clinical trial and registry data have almost exclusively been focused on patients with the ZZ (ZZ-AATD/PiZZ) genotype" | gold-2026 | p166 | p166/narrative/aatd-genotype-zz | narrative |
| aatd-genotype-null | aatd-treatment | Z/null and null/null genotypes are usually assessed | "people with the Z/null or null/null genotypes have even lower levels of plasma AAT and are usually assessed for augmentation therapy" | gold-2026 | p166 | p166/narrative/aatd-genotype-null | narrative |
| aatd-genotype-other | aatd-treatment | other genotypes are not considered likely to benefit | "Other genotypes are not considered at risk or likely to benefit from augmentation therapy." | gold-2026 | p166 | p166/narrative/aatd-genotype-other | narrative |
| aatd-progressive | aatd-treatment | progressive lung disease despite optimal therapy extends the indication | "patients with evidence of progressive lung disease despite other optimal therapy" | gold-2026 | p166 | p166/narrative/aatd-progressive | narrative |
| aatd-low-fev1 | aatd-treatment | IV augmentation recommended if FEV1 <=65% predicted | "Intravenous augmentation therapy has been recommended for individuals with AATD and an FEV1 ≤ 65% predicted based on previous observational studies." | gold-2026 | p167 | p167/narrative/aatd-low-fev1 | narrative |
| aatd-high-fev1 | aatd-treatment | consider if progressive AATD lung disease and FEV1 >65% | "all patients with evidence of progressive lung disease related to AATD, and an FEV1 > 65% should be considered for augmentation." | gold-2026 | p167 | p167/narrative/aatd-high-fev1 | narrative |
| aatd-cost-discussion | aatd-treatment | individual discussion should consider cost and limited evidence of benefit | "Individual discussion is recommended with consideration of the cost of therapy and lack of evidence for much benefit" | gold-2026 | p167 | p167/narrative/aatd-cost-discussion | narrative |
| rehabilitation-intensity-work | pulmonary-rehab | endurance exercise 60%-80% symptom-limited maximum work or heart rate | "Where possible, endurance exercise training to 60-80% of the symptom-limited maximum work or heart rate is preferred" | gold-2026 | p170 | p170/narrative/rehab-work-intensity | narrative |
| rehabilitation-intensity-borg | pulmonary-rehab | Borg dyspnea or fatigue score 4-6 | "or to a Borg-rated dyspnea or fatigue score of 4 to 6 (moderate to severe)." | gold-2026 | p170 | p170/narrative/rehab-borg-intensity | narrative |
| rehabilitation-minimum-duration | pulmonary-rehab | recommended minimum program length 6 weeks | "The recommended length of pulmonary rehabilitation (minimum of 6" | gold-2026 | p172 | p172/narrative/rehab-minimum-duration | narrative |

## Conflicts

CONFLICT: ltot-duration — `>15 hours/day is indicated; newer evidence did not support >15 hours/day: 24 hours/day was not better than 15 hours/day within one year`.

CONFLICT: antibiotic-duration — `total 5 days for patients with purulent sputum, prior lung infections, or similar bacterial features; recommended length 5-7 days; <=5 days`.

CONFLICT: lung-cancer-ldct — `ACS: consider age 50-80 with 20 pack-years regardless of years since quitting; USPSTF: annual LDCT age 50-80 with 20 pack-years and current smoking or quit within 15 years; USPSTF stop when not smoked for 15 years or a health problem substantially limits life expectancy or curative-surgery ability/willingness`.

## Coverage

The bound recommendation file contains exactly 1 recommendation record. All threshold rows use page-bound narrative locators.

- `p148/grade-spelled-out/1` - scoped out because the recommendation to offer adults with stable chronic respiratory disease a choice between center-based pulmonary rehabilitation and telerehabilitation is nonnumeric and contains no patient-action decision threshold.

ADR 0009 disposition: p102's statement that bilateral lung transplantation has longer survival especially in patients younger than 60 years is an outcome association, not a stated referral, listing, or modality-selection instruction; it is therefore scoped out rather than converted into an inferred action threshold.

ADR 0009 disposition: p172's pulmonary-rehabilitation windows (during hospitalization or within 4 weeks, within 90 days, and before discharge) describe study timing and associated outcomes rather than directives. They are scoped out as evidence and do not create a rehabilitation action conflict.

Source: `C:/codeing/guidelines-recs/GOLD/GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.json` (mode `bound`, counted from text marker). Source PDF SHA-256: `fa12e8e2dbd2090ea84d1a05ba48ab6d967fb1ce9a54d987e54249475714ddac`.
