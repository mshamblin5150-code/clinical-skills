# Lung cancer screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source document below. **Not a substitute
for the recommendation statement** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2021 | USPSTF | USPSTF/lung-cancer-screening-final-recommendation | recommendation-statement | 2021 final recommendation | 2021-03-09 | https://doi.org/10.1001/jama.2021.1117 | stated | exact |

## Scope

**Read:** the complete nine-page recommendation statement: exact recommendation,
applicability, rationale, clinician summary, eligibility and stopping rules, screening
tests and interval, cessation and shared decision-making, standardized nodule follow-up,
resources, prior recommendation, accuracy, mortality evidence, modeling boundaries,
harms, public-comment response, biological rationale, research gaps, recommendations of
others, article information, disclosures, and references.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's decision-point rule:** disease-burden counts, author and
publication metadata, study sample sizes, confidence intervals, subgroup estimates,
individual mortality-effect estimates, and research requests that do not change an
eligibility, screening, stopping, referral, follow-up, cessation, benefit-harm, or
evidence boundary. Trial schedules and harm estimates are retained as evidence and are
not converted into prescribed care beyond the USPSTF annual-screening action.

**Source: `uspstf-2021`**

| span | pages | read |
| --- | --- | --- |
| exact recommendation, applicability, rationale, and clinician summary | 1-2 | yes |
| risk, tests, interval, treatment, implementation, cessation, shared decisions, and nodule follow-up | 3 | yes |
| resources, related recommendations, update, review scope, and accuracy | 4 | yes |
| accuracy continuation, benefits, trials, and modeling | 5 | yes |
| model boundary, false positives, procedures, overdiagnosis, and radiation | 6 | yes |
| radiation continuation, psychosocial and incidental harms, comment response, biology, research gaps, and the first AATS recommendation | 7 | yes |
| continuation of recommendations of others | 8 | yes |
| article information and disclosures | 8 | read 2026-09-01; blind 2026-09-01 |
| references | 8-9 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| uspstf-screening-eligible-adults | adults aged 50 to 80 years with at least a 20 pack-year smoking history who currently smoke or quit within the past 15 years |
| eligible-current-smokers | screening-eligible adults who currently smoke |
| primary-care-referred-current-smokers | current smokers referred for lung-cancer screening through primary care |
| current-smokers-entering-any-screening-pathway | current smokers entering screening through primary care or another pathway |
| eligible-former-smokers | screening-eligible adults who formerly smoked |
| former-smokers-quit-15-years | persons who have not smoked for 15 years |
| screening-candidates-limited-health | otherwise eligible adults with a health problem substantially limiting life expectancy or ability or willingness to undergo curative lung surgery |
| eligible-adults-considering-screening | USPSTF-eligible adults deciding whether to undergo LDCT screening |
| screened-adults-with-nodules | adults with lung nodules detected during LDCT screening |
| adults-with-stage-i-ii-nsclc | patients with stage I or II non-small cell lung cancer |
| adults-with-other-risk-factors | adults with environmental exposures, prior radiation, noncancer lung disease, family history, or lower education but who are assessed for USPSTF eligibility by age and smoking history |
| adults-who-never-smoked-or-do-not-meet-criteria | persons who never smoked or who currently or formerly smoked but do not meet USPSTF eligibility criteria |
| ldct-screening-evidence-population | participants represented in LDCT screening trials and modeling studies |
| ldct-vs-no-screen-participants | participants in studies comparing LDCT screening with no screening |
| nlst-screening-participants | participants in the National Lung Screening Trial |
| nelson-screening-participants | participants in the NELSON trial |
| screened-adults-with-false-positive-results | LDCT-screened adults with false-positive results |
| adults-receiving-repeated-ldct | adults exposed to repeated LDCT screening and follow-up imaging |
| screened-adults-with-incidental-findings | LDCT-screened adults with incidental findings |
| children-adolescents-tobacco-prevention | children and adolescents covered by related USPSTF tobacco-initiation prevention guidance |
| adults-tobacco-cessation-including-pregnancy | adults who smoke, including pregnant women, covered by related USPSTF cessation guidance |
| aats-standard-population | North Americans aged 55 to 79 years with a 30 pack-year smoking history |
| aats-additional-risk-population | persons aged at least 50 years with a 20 pack-year smoking history and at least 5% five-year cumulative lung-cancer risk |
| acs-external-population | fairly healthy persons aged 55 to 74 years with at least a 30 pack-year history who currently smoke or quit within 15 years |
| acs-current-smokers | current smokers within the source-printed ACS screening population |
| accp-external-population | asymptomatic current or former smokers aged 55 to 77 years with at least 30 pack-years who currently smoke or quit within 15 years |
| accp-comorbidity-exclusion | persons whose comorbidities impair evaluation or treatment tolerance or substantially limit life expectancy |
| nccn-standard-population | persons aged 55 to 77 years with at least 30 pack-years who currently smoke or quit within 15 years |
| nccn-additional-risk-population | persons aged at least 50 years with at least 20 pack-years and at least one additional lung-cancer risk factor |
| aafp-high-risk-population | persons at high lung-cancer risk based on age and smoking history under the source-printed AAFP position |

## Quantities

| key | verbatim |
| --- | --- |
| lung-screening-recommendation | USPSTF lung-cancer screening eligibility, modality, interval, and stopping action |
| pack-year-definition | cigarette-per-pack equivalence used in the smoking-exposure definition |
| pack-year-duration-equivalence | one-pack-per-day duration equivalence used in the pack-year definition |
| screening-net-benefit | USPSTF net-benefit magnitude and conditions |
| net-benefit-high-risk-condition | high-risk-population condition for realizing screening net benefit |
| net-benefit-interpretation-condition | image-interpretation accuracy condition for realizing screening net benefit |
| net-benefit-false-positive-resolution-condition | serial-imaging condition for realizing screening net benefit |
| screening-detection-rationale | evidence adequacy for LDCT detection of early-stage disease |
| screening-mortality-benefit-rationale | evidence adequacy for annual LDCT mortality benefit |
| screening-overall-harms-rationale | magnitude and categories of LDCT screening harms |
| screening-harm-magnitude | overall magnitude of LDCT screening harms |
| eligibility-risk-method | method used to determine screening eligibility |
| unsupported-screening-modalities | screening tests not recommended because benefit was not found |
| shared-decision-content | required screening decision discussion |
| shared-decision-risk-benefit | risk-dependent screening benefit |
| shared-decision-mortality-cessation-boundary | most-deaths and smoking-cessation boundary |
| shared-decision-harm-content | harms and uncertainty to include in shared decisions |
| shared-decision-anxiety-content | anxiety associated with an indeterminate lung lesion |
| shared-decision-overdiagnosis-radiation-content | overdiagnosis and radiation uncertainty for shared decisions |
| screening-center-referral | referral setting after a decision to screen |
| smoking-cessation-action | cessation action for current smokers entering screening |
| smoking-cessation-primary-care-referral | cessation intervention timing with primary-care referral |
| smoking-cessation-program-integration | cessation integration across screening pathways |
| abnormal-nodule-management | standardized reporting and management of screen-detected nodules |
| abnormal-nodule-suggested-management | source-attributed ACR suggested nodule-management role |
| early-nsclc-treatment | source-described treatment choice for early NSCLC |
| ldct-sensitivity | evidence-only LDCT sensitivity range |
| ldct-specificity | evidence-only LDCT specificity range |
| ldct-positive-predictive-value | evidence-only LDCT positive predictive-value range |
| ldct-negative-predictive-value | evidence-only LDCT negative predictive-value range |
| nodule-threshold-evidence | evidence-only nodule-size thresholds affecting predictive value |
| trial-screening-intervals | evidence-only trial screening schedules |
| risk-model-evidence-boundary | evidence boundary for complex risk-prediction eligibility models |
| false-positive-rates | evidence-only false-positive rates by study and round |
| lungrads-false-positive-effect | evidence-only effect of Lung-RADS on false positives |
| lungrads-false-negative-tradeoff | evidence-only false-negative tradeoff of Lung-RADS |
| false-positive-needle-biopsy-rate | evidence-only needle-biopsy rate after false-positive results |
| false-positive-biopsy-complication-rate | evidence-only biopsy-complication rate after false-positive results |
| false-positive-surgery-rate | evidence-only surgery rate after false-positive results |
| nlst-false-positive-invasive-rate | evidence-only NLST invasive-procedure rate |
| nlst-false-positive-complication-rate | evidence-only NLST complication rate |
| nlst-false-positive-death-rate | evidence-only NLST death rate after false-positive workup |
| overdiagnosis-estimate | evidence-only modeled overdiagnosis estimates |
| ldct-radiation-dose | evidence-only radiation exposure per LDCT scan |
| background-radiation-context | evidence-only annual US background-radiation context |
| radiation-harm-model | evidence-only modeled radiation-induced cancer harm |
| psychosocial-harm-boundary | quality-of-life, anxiety, and distress evidence |
| incidental-finding-boundary | incidental-finding frequency and downstream uncertainty |
| incidental-finding-downstream-actions | downstream evaluation after incidental findings |
| incidental-finding-benefit-harm-balance | uncertainty in benefit-harm balance of incidental detection |
| noneligible-population-boundary | screening evidence boundary outside USPSTF criteria |
| cdc-how-to-quit-resource | source-described CDC How to Quit resource |
| cdc-fast-facts-resource | source-described CDC Smoking Cessation Fast Facts resource |
| cdc-tips-resource | source-described CDC Tips From Former Smokers resource |
| nci-cessation-resource | source-described NCI cessation resource |
| nci-patient-screening-guide | source-described NCI patient screening guide |
| nci-clinician-screening-guide | source-described NCI clinician screening guide |
| related-uspstf-tobacco-initiation | related USPSTF tobacco-initiation prevention action |
| related-uspstf-adult-cessation | related USPSTF adult cessation action |
| prior-uspstf-criteria | superseded 2013 USPSTF screening criteria |
| external-aats-screening | source-printed AATS screening criteria |
| external-aats-additional-action | source-printed AATS additional-risk screening action |
| external-aats-additional-criteria | source-printed AATS additional-risk eligibility criteria |
| external-acs-screening | source-printed ACS screening criteria and implementation |
| external-acs-pack-year-eligibility | source-printed ACS pack-year criterion |
| external-acs-smoking-status-eligibility | source-printed ACS smoking-status and quit-window criterion |
| external-acs-cessation | source-printed ACS cessation action |
| external-acs-shared-decision | source-printed ACS shared-decision action |
| external-acs-screening-center | source-printed ACS screening-center action |
| external-accp-screening | source-printed ACCP screening and exclusion criteria |
| external-accp-pack-year-eligibility | source-printed ACCP pack-year criterion |
| external-accp-smoking-status-eligibility | source-printed ACCP smoking-status and quit-window criterion |
| external-accp-evaluation-tolerance | source-printed ACCP evaluation-tolerance exclusion |
| external-accp-treatment-tolerance | source-printed ACCP treatment-tolerance exclusion |
| external-accp-life-expectancy | source-printed ACCP life-expectancy exclusion |
| external-nccn-screening | source-printed NCCN screening criteria |
| external-nccn-additional-risk-criteria | source-printed NCCN additional-risk eligibility criteria |
| external-nccn-pack-year-eligibility | source-printed NCCN pack-year criterion |
| external-nccn-smoking-status-eligibility | source-printed NCCN smoking-status and quit-window criterion |
| external-aafp-position | source-printed AAFP evidence position |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| lung-screening-recommendation | uspstf-screening-eligible-adults | annual LDCT from age 50 through 80 years with at least 20 pack-years and current smoking or quitting within 15 years; stop after 15 years without smoking or when health substantially limits life expectancy or ability or willingness for curative lung surgery; Grade B | The USPSTF recommends annual screening for lung cancer with LDCT in adults aged 50 to 80 years who have a 20 pack-year smoking history and currently smoke or have quit within the past 15 years. Screening should be discontinued once a person has not smoked for 15 years or develops a health problem that substantially limits life expectancy or the ability or willingness to have curative lung surgery. | uspstf-2021 | 1 | p1/screening-for-lung-cancer/1 | B |
| pack-year-definition | uspstf-screening-eligible-adults | 20 cigarettes equals one pack | RENDERED: One pack-year is the equivalent of smoking an average of 20 cigarettes—1 pack—per day for a year. | uspstf-2021 | 2 | p2/narrative/pack-year-definition | narrative |
| pack-year-duration-equivalence | uspstf-screening-eligible-adults | one pack per day for one year equals one pack-year | RENDERED: One pack-year is the equivalent of smoking an average of 20 cigarettes—1 pack—per day for a year. | uspstf-2021 | 2 | p2/narrative/pack-year-duration-equivalence | narrative |
| screening-net-benefit | uspstf-screening-eligible-adults | moderate net benefit | annual screening for lung cancer with LDCT has a moderate net benefit | uspstf-2021 | 2 | p2/narrative/screening-net-benefit | narrative |
| net-benefit-high-risk-condition | uspstf-screening-eligible-adults | realize net benefit by limiting screening to persons at high risk | limiting screening to persons at high risk | uspstf-2021 | 2 | p2/narrative/net-benefit-high-risk-condition | narrative |
| net-benefit-interpretation-condition | uspstf-screening-eligible-adults | realize net benefit when image-interpretation accuracy is similar to or better than trial accuracy | RENDERED: the accuracy of image interpretation being similar to or better than that found in clinical trials | uspstf-2021 | 2 | p2/narrative/net-benefit-interpretation-condition | narrative |
| net-benefit-false-positive-resolution-condition | uspstf-screening-eligible-adults | net-benefit assessment assumes most false-positive findings are resolved with serial imaging rather than invasive procedures; this is a condition of the evidence, not a universal management command | RENDERED: resolution of most false-positive results with serial imaging rather than invasive procedures. | uspstf-2021 | 2 | p2/narrative/net-benefit-false-positive-resolution-condition | narrative |
| screening-detection-rationale | uspstf-screening-eligible-adults | adequate evidence that LDCT has sufficient sensitivity and specificity to detect early-stage lung cancer | LDCT has sufficient sensitivity and specificity to detect early-stage lung cancer | uspstf-2021 | 2 | p2/narrative/screening-detection-rationale | narrative |
| screening-mortality-benefit-rationale | uspstf-screening-eligible-adults | adequate evidence that annual LDCT in a defined high-risk population prevents a substantial number of lung-cancer deaths | annual screening for lung cancer with LDCT in a defined population of high-risk persons can prevent a substantial number of lung cancer-related deaths | uspstf-2021 | 2 | p2/narrative/screening-mortality-benefit-rationale | narrative |
| screening-overall-harms-rationale | uspstf-screening-eligible-adults | harm categories include false positives with unnecessary tests or invasive procedures, incidental findings, short-term distress from indeterminate results, overdiagnosis, and radiation exposure | The harms associated with LDCT screening include false-positive results leading to unnecessary tests and invasive procedures, incidental findings, short-term increases in distress due to indeterminate results, overdiagnosis, and radiation exposure | uspstf-2021 | 2 | p2/narrative/screening-overall-harms-rationale | narrative |
| screening-harm-magnitude | uspstf-screening-eligible-adults | moderate overall harms | the harms of screening for lung cancer with LDCT are moderate in magnitude | uspstf-2021 | 2 | p2/narrative/screening-harm-magnitude | narrative |
| eligibility-risk-method | adults-with-other-risk-factors | determine eligibility using age and smoking history; evidence is insufficient that complex risk-prediction models improve outcomes for broad primary-care implementation | recommends using age and smoking history to determine screening eligibility rather than more elaborate risk prediction models | uspstf-2021 | 3 | p3/narrative/eligibility-risk-method | narrative |
| unsupported-screening-modalities | uspstf-screening-eligible-adults | do not use sputum cytology, chest radiography, or biomarker measurement as screening modalities because benefit has not been found | RENDERED: Other potential screening modalities that are not recommended because they have not been found to be beneficial include sputum cytology, chest radiography, and measurement of biomarker levels. | uspstf-2021 | 3 | p3/narrative/unsupported-screening-modalities | narrative |
| shared-decision-content | eligible-adults-considering-screening | discuss potential benefits, limitations, and harms before deciding whether to screen | The decision to undertake screening should involve a thorough discussion of the potential benefits, limitations, and harms of screening. | uspstf-2021 | 3 | p3/narrative/shared-decision-content | narrative |
| shared-decision-risk-benefit | eligible-adults-considering-screening | explain that benefit varies with risk and higher-risk persons are more likely to benefit | The benefit of screening varies with risk because persons at higher risk are more likely to benefit. | uspstf-2021 | 3 | p3/narrative/shared-decision-risk-benefit | narrative |
| shared-decision-mortality-cessation-boundary | eligible-adults-considering-screening | explain that screening does not prevent most lung-cancer deaths and smoking cessation remains essential | Screening does not prevent most lung cancer deaths; thus, smoking cessation remains essential. | uspstf-2021 | 3 | p3/narrative/shared-decision-mortality-cessation-boundary | narrative |
| shared-decision-harm-content | eligible-adults-considering-screening | discuss false positives and incidental findings that may lead to subsequent testing and treatment | false-positive results and incidental findings that can lead to subsequent testing and treatment | uspstf-2021 | 3 | p3/narrative/shared-decision-harm-content | narrative |
| shared-decision-anxiety-content | eligible-adults-considering-screening | discuss anxiety from living with a lung lesion that may be cancer | the anxiety of living with a lung lesion that may be cancer. | uspstf-2021 | 3 | p3/narrative/shared-decision-anxiety-content | narrative |
| shared-decision-overdiagnosis-radiation-content | eligible-adults-considering-screening | discuss overdiagnosis and radiation exposure while explaining that their exact magnitude is uncertain | Overdiagnosis of lung cancer and the risks of radiation exposure are harms, although their exact magnitude is uncertain. | uspstf-2021 | 3 | p3/narrative/shared-decision-overdiagnosis-radiation-content | narrative |
| screening-center-referral | eligible-adults-considering-screening | after choosing screening, refer for LDCT ideally at a center experienced and expert in lung-cancer screening | refer them for lung cancer screening with low-dose CT, ideally to a center with experience and expertise in lung cancer screening. | uspstf-2021 | 2 | p2/narrative/screening-center-referral | narrative |
| smoking-cessation-action | eligible-current-smokers | provide smoking-cessation interventions to every current smoker enrolled in screening | RENDERED: All persons enrolled in a screening program who are current smokers should receive smoking cessation interventions. | uspstf-2021 | 3 | p3/narrative/smoking-cessation-action | narrative |
| smoking-cessation-primary-care-referral | primary-care-referred-current-smokers | provide cessation interventions concurrently with the primary-care screening referral | persons referred for lung cancer screening through primary care should receive these interventions concurrent with referral. | uspstf-2021 | 3 | p3/narrative/smoking-cessation-primary-care-referral | narrative |
| smoking-cessation-program-integration | current-smokers-entering-any-screening-pathway | incorporate cessation interventions into all lung-cancer screening programs, including pathways outside primary-care referral | RENDERED: the USPSTF encourages incorporating such interventions into all screening programs. | uspstf-2021 | 3 | p3/narrative/smoking-cessation-program-integration | narrative |
| abnormal-nodule-management | screened-adults-with-nodules | SOURCE-ATTRIBUTED ACR: the ACR developed Lung-RADS and endorses its use in lung-cancer screening | RENDERED: the American College of Radiology developed the Lung Imaging Reporting and Data System (Lung-RADS) classification system and endorses its use in lung cancer screening. | uspstf-2021 | 3 | p3/narrative/abnormal-nodule-management | narrative |
| abnormal-nodule-suggested-management | screened-adults-with-nodules | SOURCE-ATTRIBUTED ACR: Lung-RADS identifies suspicious findings and suggests management of LDCT-detected nodules | RENDERED: Lung-RADS provides guidance to clinicians on which findings are suspicious for cancer and the suggested management of lung nodules detected on LDCT. | uspstf-2021 | 3 | p3/narrative/abnormal-nodule-suggested-management | narrative |
| early-nsclc-treatment | adults-with-stage-i-ii-nsclc | surgical resection is generally the current treatment of choice | Surgical resection is generally considered the current treatment of choice for patients with stage I or II non-small cell lung cancer | uspstf-2021 | 3 | p3/narrative/early-nsclc-treatment | narrative |
| ldct-sensitivity | ldct-screening-evidence-population | EVIDENCE ONLY: sensitivity 59% to 100% | sensitivity ranged from 59% to 100% | uspstf-2021 | 4 | p4/narrative/ldct-sensitivity | narrative |
| ldct-specificity | ldct-screening-evidence-population | EVIDENCE ONLY: specificity 26.4% to 99.7% | RENDERED: specificity ranged from 26.4% to 99.7% | uspstf-2021 | 4 | p4/narrative/ldct-specificity | narrative |
| ldct-positive-predictive-value | ldct-screening-evidence-population | EVIDENCE ONLY: positive predictive value 3.3% to 43.5% | positive predictive value ranged from 3.3% to 43.5% | uspstf-2021 | 4 | p4/narrative/ldct-positive-predictive-value | narrative |
| ldct-negative-predictive-value | ldct-screening-evidence-population | EVIDENCE ONLY: negative predictive value 97.7% to 100% | negative predictive value ranged from 97.7% to 100%. | uspstf-2021 | 4 | p4/narrative/ldct-negative-predictive-value | narrative |
| nodule-threshold-evidence | ldct-screening-evidence-population | EVIDENCE ONLY: average nodule-diameter threshold 5 mm or at least 6 mm increased positive predictive value in retrospective analyses | increase in nodule size threshold to an average diameter of 5 mm, 6 mm, or larger | uspstf-2021 | 5 | p5/narrative/nodule-threshold-evidence | narrative |
| trial-screening-intervals | nlst-screening-participants | EVIDENCE ONLY: annual screening for 3 years | RENDERED: screened annually for 3 years. | uspstf-2021 | 5 | p5/narrative/nlst-screening-interval | narrative |
| trial-screening-intervals | nelson-screening-participants | EVIDENCE ONLY: screening at 1 year, then 2 years, then 2.5 years | The NELSON trial screened at intervals of 1 year, then 2 years, then 2.5 years. | uspstf-2021 | 5 | p5/narrative/nelson-screening-interval | narrative |
| risk-model-evidence-boundary | adults-with-other-risk-factors | complex prediction models may impede implementation and evidence is insufficient that they improve outcomes versus age and smoking history | RENDERED: the use of more complex risk prediction models to determine eligibility might make implementation more difficult, and there is currently insufficient evidence to assess whether risk prediction model-based screening would improve outcomes relative to simply using the risk factors of age and smoking history. | uspstf-2021 | 6 | p6/narrative/risk-model-evidence-boundary | narrative |
| false-positive-rates | nlst-screening-participants | EVIDENCE ONLY: 26.3% baseline, 27.2% year 1, and 15.9% year 2 | The NLST reported false-positive rates of 26.3% for baseline, 27.2% for year 1, and 15.9% for year 2. | uspstf-2021 | 6 | p6/narrative/nlst-false-positive-rates | narrative |
| false-positive-rates | nelson-screening-participants | EVIDENCE ONLY: 19.8% baseline, 7.1% year 1, 9.0% for males at year 3, and 3.9% for males at year 5.5 | The NELSON trial reported false-positive rates of 19.8% at baseline, 7.1% at year 1, 9.0% for males at year 3, and 3.9% for males at year 5.5 of screening. | uspstf-2021 | 6 | p6/narrative/nelson-false-positive-rates | narrative |
| lungrads-false-positive-effect | ldct-screening-evidence-population | EVIDENCE ONLY: baseline false-positive rate 12.8% with Lung-RADS versus 26.6% using the NLST approach | RENDERED: 12.8% (95% CI, 12.4%-13.2%) vs 26.6% (95% CI, 26.1%-27.1%) | uspstf-2021 | 6 | p6/narrative/lungrads-false-positive-effect | narrative |
| lungrads-false-negative-tradeoff | ldct-screening-evidence-population | EVIDENCE ONLY: Lung-RADS may reduce false positives at the cost of some false negatives | RENDERED: may reduce false-positives, albeit at the cost of some false-negatives. | uspstf-2021 | 6 | p6/narrative/lungrads-false-negative-tradeoff | narrative |
| false-positive-needle-biopsy-rate | screened-adults-with-false-positive-results | EVIDENCE ONLY: needle biopsy 0.09% to 0.56% of all screened patients | needle biopsy for false-positive results ranged from 0.09% to 0.56%. | uspstf-2021 | 6 | p6/narrative/false-positive-needle-biopsy-rate | narrative |
| false-positive-biopsy-complication-rate | screened-adults-with-false-positive-results | EVIDENCE ONLY: biopsy complications 0.03% to 0.07% of all screened patients | Complication rates from needle biopsy for false-positive results ranged from 0.03% to 0.07% | uspstf-2021 | 6 | p6/narrative/false-positive-biopsy-complication-rate | narrative |
| false-positive-surgery-rate | screened-adults-with-false-positive-results | EVIDENCE ONLY: surgery 0.5% to 1.3% of all screened participants | RENDERED: Surgical procedures for false-positive results were reported in 0.5% to 1.3% of all screened participants. | uspstf-2021 | 6 | p6/narrative/false-positive-surgery-rate | narrative |
| nlst-false-positive-invasive-rate | nlst-screening-participants | EVIDENCE ONLY: invasive procedures in 1.7% of screened patients | invasive procedures (needle biopsy, thoracotomy, thoracoscopy, mediastinoscopy, and bronchoscopy) in 1.7% of patients screened. | uspstf-2021 | 6 | p6/narrative/nlst-false-positive-invasive-rate | narrative |
| nlst-false-positive-complication-rate | nlst-screening-participants | EVIDENCE ONLY: complications in 0.1% of screened patients | RENDERED: Complications occurred in 0.1% of patients screened | uspstf-2021 | 6 | p6/narrative/nlst-false-positive-complication-rate | narrative |
| nlst-false-positive-death-rate | nlst-screening-participants | EVIDENCE ONLY: death within 60 days after the most invasive false-positive workup in 0.007% of screened patients | RENDERED: death in the 60 days following the most invasive procedure performed to evaluate a false-positive result occurred in 0.007% | uspstf-2021 | 6 | p6/narrative/nlst-false-positive-death-rate | narrative |
| overdiagnosis-estimate | ldct-screening-evidence-population | EVIDENCE ONLY: modeled screen-detected overdiagnosis 6.3% under prior criteria versus 6.0% under current criteria | result in 6.3% of screen-detected cases of lung cancer being over diagnosed lung cancers vs 6.0% | uspstf-2021 | 6 | p6/narrative/overdiagnosis-estimate | narrative |
| ldct-radiation-dose | adults-receiving-repeated-ldct | EVIDENCE ONLY: 0.65 to 2.36 mSv per LDCT scan | radiation exposure associated with 1 LDCT scan ranged from 0.65 to 2.36 mSv. | uspstf-2021 | 6 | p6/narrative/ldct-radiation-dose | narrative |
| background-radiation-context | adults-receiving-repeated-ldct | EVIDENCE ONLY: average annual US background exposure 2.4 mSv | RENDERED: average annual background radiation exposure in the US is 2.4 mSv. | uspstf-2021 | 6 | p6/narrative/background-radiation-context | narrative |
| radiation-harm-model | adults-receiving-repeated-ldct | EVIDENCE ONLY: modeled 1 radiation-caused death per 13.0 lung-cancer deaths avoided under current criteria versus 1 per 18.5 under prior criteria | 1 death caused for every 13.0 vs 18.5 lung cancer deaths avoided by screening. | uspstf-2021 | 7 | p7/narrative/radiation-harm-model | narrative |
| psychosocial-harm-boundary | ldct-vs-no-screen-participants | LDCT screening did not worsen quality of life, anxiety, or distress over 2 years compared with no screening | RENDERED: compared with no screening, persons who receive LDCT screening do not have worse health-related quality of life, anxiety, or distress over 2 years of follow-up. | uspstf-2021 | 7 | p7/narrative/psychosocial-harm-boundary | narrative |
| psychosocial-harm-boundary | screened-adults-with-nodules | true-positive or indeterminate results may worsen quality of life, anxiety, or distress in the short term | true-positive or indeterminate results may experience worse health-related quality of life, anxiety, or distress in the short-term. | uspstf-2021 | 7 | p7/narrative/psychosocial-harm-positive-indeterminate | narrative |
| incidental-finding-boundary | screened-adults-with-incidental-findings | EVIDENCE ONLY: significant or evaluated incidental findings 4.4% to 40.7% | RENDERED: incidental findings that were deemed significant or required further evaluation (4.4% to 40.7%) | uspstf-2021 | 7 | p7/narrative/incidental-finding-boundary | narrative |
| incidental-finding-downstream-actions | screened-adults-with-incidental-findings | downstream evaluation may include consultations, additional imaging, and invasive procedures with associated costs and burdens | RENDERED: Incidental findings led to downstream evaluation, including consultations, additional imaging, and invasive procedures, with associated costs and burdens. | uspstf-2021 | 7 | p7/narrative/incidental-finding-downstream-actions | narrative |
| incidental-finding-benefit-harm-balance | screened-adults-with-incidental-findings | benefits of detecting nonlung-cancer conditions and the balance of benefits versus harms remain uncertain | the balance of benefits and harms of incidental findings on LDCT screening remain uncertain. | uspstf-2021 | 7 | p7/narrative/incidental-finding-benefit-harm-balance | narrative |
| noneligible-population-boundary | adults-who-never-smoked-or-do-not-meet-criteria | evidence does not support incorporating other risk factors as determinants of screening eligibility | RENDERED: current evidence does not support the incorporation of these risk factors as determinants of eligibility for lung cancer screening. | uspstf-2021 | 7 | p7/narrative/noneligible-population-boundary | narrative |
| cdc-how-to-quit-resource | eligible-current-smokers | EXTERNAL RESOURCE AVAILABILITY (CDC): the source lists the How to Quit resource | RENDERED: "How to Quit" resources | uspstf-2021 | 4 | p4/narrative/cdc-how-to-quit-resource | narrative |
| cdc-fast-facts-resource | eligible-current-smokers | EXTERNAL RESOURCE AVAILABILITY (CDC): the source lists Smoking Cessation: Fast Facts | RENDERED: Smoking Cessation: Fast Facts | uspstf-2021 | 4 | p4/narrative/cdc-cessation-fast-facts | narrative |
| cdc-tips-resource | eligible-current-smokers | EXTERNAL RESOURCE AVAILABILITY (CDC): the source lists Tips From Former Smokers | RENDERED: Tips From Former Smokers | uspstf-2021 | 4 | p4/narrative/cdc-tips-resource | narrative |
| nci-cessation-resource | eligible-current-smokers | EXTERNAL RESOURCE AVAILABILITY (NCI): the source identifies resources that help patients stop smoking | RENDERED: resources to help patients stop smoking | uspstf-2021 | 4 | p4/narrative/nci-cessation-resource | narrative |
| nci-patient-screening-guide | eligible-adults-considering-screening | EXTERNAL RESOURCE AVAILABILITY (NCI): the source lists the patient version of the lung-cancer screening guide | RENDERED: Lung Cancer Screening (PDQ)-Patient Version | uspstf-2021 | 4 | p4/narrative/nci-patient-screening-guide | narrative |
| nci-clinician-screening-guide | eligible-adults-considering-screening | EXTERNAL RESOURCE AVAILABILITY (NCI): the source lists the health-professional version of the lung-cancer screening guide | RENDERED: Lung Cancer Screening (PDQ)-Health Professional Version | uspstf-2021 | 4 | p4/narrative/nci-clinician-screening-guide | narrative |
| related-uspstf-tobacco-initiation | children-adolescents-tobacco-prevention | RELATED USPSTF: provide interventions to prevent initiation of tobacco use in children and adolescents | RENDERED: interventions to prevent the initiation of tobacco use in children and adolescents | uspstf-2021 | 4 | p4/narrative/related-uspstf-tobacco-initiation | narrative |
| related-uspstf-adult-cessation | adults-tobacco-cessation-including-pregnancy | RELATED USPSTF: provide behavioral and pharmacotherapy interventions for tobacco-smoking cessation in adults, including pregnant women | behavioral and pharmacotherapy interventions for tobacco smoking cessation in adults, including pregnant women. | uspstf-2021 | 2 | p2/narrative/related-uspstf-adult-cessation | narrative |
| prior-uspstf-criteria | ldct-screening-evidence-population | SUPERSEDED 2013 USPSTF: annual LDCT at age 55 through 80 years with 30 pack-years and current smoking or quitting within 15 years | In 2013 the USPSTF recommended annual screening for lung cancer with LDCT in adults aged 55 to 80 years who have a 30 pack-year smoking history and currently smoke or have quit within the past 15 years | uspstf-2021 | 4 | p4/narrative/prior-uspstf-criteria | narrative |
| external-aats-screening | aats-standard-population | SOURCE-PRINTED EXTERNAL (AATS): annual LDCT at age 55 through 79 years with 30 pack-years | RENDERED: annual lung cancer screening with LDCT for North Americans aged 55 to 79 years with a 30 pack-year history of smoking. | uspstf-2021 | 7 | p7/narrative/external-aats-standard | narrative |
| external-aats-additional-action | aats-additional-risk-population | SOURCE-PRINTED EXTERNAL (AATS): offer annual lung-cancer screening with LDCT to the additional-risk branch | RENDERED: It also recommends offering annual lung cancer screening with LDCT starting at | uspstf-2021 | 7 | p7/narrative/external-aats-additional-action | narrative |
| external-aats-additional-criteria | aats-additional-risk-population | SOURCE-PRINTED EXTERNAL (AATS): start at age 50 years with 20 pack-years when cumulative lung-cancer risk is at least 5% over the following 5 years | age 50 years to persons with a 20 pack-year smoking history if there is an additional cumulative risk of developing lung cancer of 5% or greater over the following 5 years. | uspstf-2021 | 8 | p8/narrative/external-aats-additional-criteria | narrative |
| external-acs-screening | acs-external-population | SOURCE-PRINTED EXTERNAL (ACS): annual LDCT at age 55 through 74 years for persons in fairly good health | annual lung cancer screening with LDCT for persons aged 55 to 74 years who are in fairly good health | uspstf-2021 | 8 | p8/narrative/external-acs-screening | narrative |
| external-acs-pack-year-eligibility | acs-external-population | SOURCE-PRINTED EXTERNAL (ACS): at least 30 pack-years | have at least a 30 pack-year smoking history | uspstf-2021 | 8 | p8/narrative/external-acs-pack-year-eligibility | narrative |
| external-acs-smoking-status-eligibility | acs-external-population | SOURCE-PRINTED EXTERNAL (ACS): current smoking or quitting within 15 years | RENDERED: currently smoke or have quit within the past 15 years. | uspstf-2021 | 8 | p8/narrative/external-acs-smoking-status-eligibility | narrative |
| external-acs-cessation | acs-current-smokers | SOURCE-PRINTED EXTERNAL (ACS): provide smoking-cessation counseling to current smokers | RENDERED: smoking cessation counseling for current smokers | uspstf-2021 | 8 | p8/narrative/external-acs-cessation | narrative |
| external-acs-shared-decision | acs-external-population | SOURCE-PRINTED EXTERNAL (ACS): use shared decision-making about lung-cancer screening | shared decision-making about lung cancer screening | uspstf-2021 | 8 | p8/narrative/external-acs-shared-decision | narrative |
| external-acs-screening-center | acs-external-population | SOURCE-PRINTED EXTERNAL (ACS): conduct screening at a high-volume, high-quality lung-cancer screening and treatment center | screening be conducted in a high-volume, high-quality lung cancer screening and treatment center. | uspstf-2021 | 8 | p8/narrative/external-acs-screening-center | narrative |
| external-accp-screening | accp-external-population | SOURCE-PRINTED EXTERNAL (ACCP): offer annual LDCT to asymptomatic current or former smokers at age 55 through 77 years | RENDERED: annual screening with LDCT should be offered to asymptomatic smokers and former smokers aged 55 to 77 years | uspstf-2021 | 8 | p8/narrative/external-accp-screening | narrative |
| external-accp-pack-year-eligibility | accp-external-population | SOURCE-PRINTED EXTERNAL (ACCP): at least 30 pack-years | smoked 30 pack-years or more | uspstf-2021 | 8 | p8/narrative/external-accp-pack-year-eligibility | narrative |
| external-accp-smoking-status-eligibility | accp-external-population | SOURCE-PRINTED EXTERNAL (ACCP): current smoking or quitting within 15 years | either continue to smoke or have quit within the past 15 years. | uspstf-2021 | 8 | p8/narrative/external-accp-smoking-status-eligibility | narrative |
| external-accp-evaluation-tolerance | accp-comorbidity-exclusion | SOURCE-PRINTED EXTERNAL (ACCP): do not screen when comorbidity impairs ability to tolerate evaluation of screen-detected findings | comorbidities that adversely influence their ability to tolerate the evaluation of screen-detected findings | uspstf-2021 | 8 | p8/narrative/external-accp-evaluation-tolerance | narrative |
| external-accp-treatment-tolerance | accp-comorbidity-exclusion | SOURCE-PRINTED EXTERNAL (ACCP): do not screen when comorbidity impairs ability to tolerate treatment of screen-detected early-stage lung cancer | RENDERED: tolerate treatment of an early-stage screen-detected lung cancer | uspstf-2021 | 8 | p8/narrative/external-accp-treatment-tolerance | narrative |
| external-accp-life-expectancy | accp-comorbidity-exclusion | SOURCE-PRINTED EXTERNAL (ACCP): do not screen when comorbidity substantially limits life expectancy | substantially limit their life expectancy. | uspstf-2021 | 8 | p8/narrative/external-accp-life-expectancy | narrative |
| external-nccn-screening | nccn-standard-population | SOURCE-PRINTED EXTERNAL (NCCN): annual LDCT at age 55 through 77 years | RENDERED: annual screening for lung cancer with LDCT in persons aged 55 to 77 years | uspstf-2021 | 8 | p8/narrative/external-nccn-standard | narrative |
| external-nccn-pack-year-eligibility | nccn-standard-population | SOURCE-PRINTED EXTERNAL (NCCN): at least 30 pack-years | have at least a 30 pack-year smoking history | uspstf-2021 | 8 | p8/narrative/external-nccn-pack-year-eligibility | narrative |
| external-nccn-smoking-status-eligibility | nccn-standard-population | SOURCE-PRINTED EXTERNAL (NCCN): current smoking or quitting within 15 years | RENDERED: currently smoke or have quit within the past 15 years | uspstf-2021 | 8 | p8/narrative/external-nccn-smoking-status-eligibility | narrative |
| external-nccn-screening | nccn-additional-risk-population | SOURCE-PRINTED EXTERNAL (NCCN): annual LDCT for the additional-risk branch | RENDERED: The National Comprehensive Cancer Network recommends annual screening for lung cancer with LDCT | uspstf-2021 | 8 | p8/narrative/external-nccn-additional-risk-action | narrative |
| external-nccn-additional-risk-criteria | nccn-additional-risk-population | SOURCE-PRINTED EXTERNAL (NCCN): age at least 50 years, at least 20 pack-years, and at least one additional lung-cancer risk factor | RENDERED: persons 50 years or older who have at least a 20 pack-year smoking history and have at least 1 additional risk factor for lung cancer. | uspstf-2021 | 8 | p8/narrative/external-nccn-additional-risk-criteria | narrative |
| external-aafp-position | aafp-high-risk-population | SOURCE-PRINTED EXTERNAL (AAFP): evidence insufficient to recommend for or against LDCT screening | evidence is insufficient to recommend for or against screening for lung cancer with LDCT in persons at high risk | uspstf-2021 | 8 | p8/narrative/external-aafp-position | narrative |

## Conflicts

The current USPSTF Grade B criteria (`annual LDCT from age 50 through 80 years with at
least 20 pack-years and current smoking or quitting within 15 years`) replace the
superseded 2013 USPSTF criteria (`annual LDCT at age 55 through 80 years with 30
pack-years and current smoking or quitting within 15 years`). They are historical
versions, not concurrent alternatives.

Source-printed external organizations use different populations and eligibility rules:
AATS uses `age 55 through 79 years with 30 pack-years` or an additional-risk branch;
ACS uses `age 55 through 74 years` plus health status and 30 pack-years; ACCP uses
`age 55 through 77 years` and 30 pack-years; NCCN uses `age 55 through 77 years` and
30 pack-years or an additional-risk branch; and AAFP reports insufficient evidence.
These are preserved with organization-specific populations rather than merged into a
false same-population conflict. The AAFP position is genuinely divergent in conclusion
from the USPSTF Grade B recommendation, but the source does not print an identical
eligibility population for AAFP, so no machine conflict is asserted.

Trial intervals and harm estimates are evidence descriptions, not competing directives.
The annual USPSTF action is based on trial and modeling evidence. Lung-RADS guidance is
source-attributed ACR nodule-management guidance and complements, rather than replaces,
USPSTF eligibility and annual screening.

## Coverage

The exact recommendation artifact contains **1 recommendation identifier**. This sheet
cites it and scopes out **0**: **1 = 1 cited + 0 scoped**.

ADR 0009 disposition:

- retained the full current Grade B age, pack-year, smoking-status, quit-window,
  interval, and both stopping branches, plus the pack-year definition;
- retained the complete shared-decision discussion of risk-dependent benefit, the fact
  that screening does not prevent most lung-cancer deaths, cessation, false positives,
  incidental findings, downstream testing and treatment, anxiety, overdiagnosis,
  radiation, and magnitude uncertainty; retained experienced-center referral and the
  distinct cessation actions for all current smokers, primary-care referral, and every
  screening pathway;
- retained nonbeneficial modalities, early-NSCLC treatment context, ACR-authored and
  endorsed Lung-RADS suggested nodule management, and serial imaging solely as a
  condition underlying the USPSTF net-benefit assessment rather than a universal command;
- retained accuracy, trial-interval, model-selection, false-positive, procedure,
  overdiagnosis, radiation, psychosocial, and incidental-finding evidence as evidence
  boundaries rather than patient eligibility or prescribed schedules;
- retained the boundary for never-smokers and other nonqualifying persons and did not
  infer screening from environmental, family, radiation, lung-disease, education, race,
  ethnicity, sex, biomarker, or model-derived risk outside the stated criteria;
- retained the separate related USPSTF tobacco-initiation action for children and
  adolescents and adult cessation action including pregnant women; retained each named
  CDC cessation resource and NCI cessation, patient-guide, and clinician-guide resource;
- retained superseded 2013 criteria and every source-printed AATS, ACS, ACCP, NCCN, and
  AAFP action with explicit external provenance, including all ACS implementation clauses
  and each ACCP comorbidity exclusion;
- excluded prevalence and mortality counts, study sizes, confidence intervals,
  individual mortality effect estimates, subgroup eligibility simulations, research
  requests, publication metadata, disclosures, and reference-list values that do not
  change a patient action or evidence boundary.
