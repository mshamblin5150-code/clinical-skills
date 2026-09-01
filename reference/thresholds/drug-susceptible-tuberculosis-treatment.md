# Drug-susceptible tuberculosis treatment — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2016 | ATS/CDC/IDSA | IDSA/ciw376 | guideline | 2016 guideline | 2016 | https://doi.org/10.1093/cid/ciw376 | stated | bound |

## Scope

**Read:** all 49 source pages, including the recommendation summary, methods,
regimen and dose tables, supporting narrative, special populations, research
agenda, article information, disclosures, and references. The bound recommendation
record contains 28 marker occurrences and is not treated as a complete index of the
guideline's numeric actions.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| recommendation summary, principles, case management, regimens, doses, and administration frequency | 1-7 | yes |
| interruptions, adverse effects, HIV recommendations, and drug interactions | 8-13 | yes |
| evidence methods and treatment-regimen rationale | 14-19 | yes |
| regimen alternatives, monitoring, adverse-effect management, and pharmacology | 20-24 | yes |
| HIV detailed evidence, drug interactions, IRIS, and pediatric treatment | 25-30 | yes |
| extrapulmonary disease, culture-negative disease, pregnancy, renal disease, hepatic disease, advanced age, and recurrence/failure | 31-38 | yes |
| research agenda and article information | 39-40 | read 2026-08-31; blind 2026-08-31 |
| references | 41-49 | exempt: reference list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| presumed-pulmonary-tb | patients who, on the basis of careful clinical and radiographic evaluation, are thought to have pulmonary tuberculosis |
| drug-susceptible-pulmonary-tb | patients with drug-susceptible pulmonary tuberculosis |
| low-relapse-risk-hiv-negative | HIV-infected or uninfected patients with noncavitary tuberculosis and/or smear-negative at the completion of 2 months of treatment |
| hiv-uninfected-low-risk | HIV-uninfected patients who are also at low risk of relapse (pulmonary tuberculosis caused by drug-susceptible organisms, that at the start of treatment is noncavitary and/or smear negative) |
| cavity-positive-two-month | patients who had cavitation on the initial chest radiograph and positive cultures at completion of 2 months of therapy |
| treatment-interruption | patients who have interrupted tuberculosis treatment |
| hepatic-injury | patients receiving antituberculosis drugs who develop drug-induced liver injury |
| hiv-tb-art | HIV-infected patients receiving antiretroviral therapy during tuberculosis treatment |
| hiv-tb-no-art | HIV-infected patients who do not receive ART during tuberculosis treatment |
| hiv-tb-cd4-under-50 | HIV-infected patients with a CD4 count <50 cells/µL |
| hiv-tb-cd4-at-least-50 | HIV-infected patients with a CD4 count >=50 cells/µL |
| hiv-tb-meningitis | HIV-infected patients with tuberculosis meningitis |
| tb-iris | patients with more severe manifestations of IRIS |
| tb-meningitis | patients with tuberculous meningitis |
| culture-negative-adult | HIV-uninfected adult patients with AFB smear- and culture-negative pulmonary tuberculosis |
| adult-tb | adults with tuberculosis |
| pediatric-tb | infants, children, and adolescents with tuberculosis |
| pediatric-low-risk | HIV-uninfected children with minimal disease and low risk of drug resistance |
| pregnant-tb | pregnant women with drug-susceptible tuberculosis |
| pregnant-or-nursing-inh | pregnant or nursing women receiving INH |
| exclusively-breastfed-infants | exclusively breastfed infants, even those not receiving INH |
| renal-under-30 | adult patients with creatinine clearance <30 mL/min or receiving hemodialysis |
| renal-30-to-50 | patients with 30-50 mL/min creatinine clearance |
| advanced-liver-disease | patients with advanced liver disease or serum ALT >3 times the upper limit of normal at baseline not thought caused by tuberculosis |
| severe-unstable-liver | patients with severe, unstable liver disease |
| older-than-75 | patients >75 years of age with modest disease and low risk of drug resistance |
| extrapulmonary-tb | patients with drug-susceptible extrapulmonary tuberculosis |
| bone-joint-spine-tb | patients with bone, joint, or spinal tuberculosis |
| pericardial-tb | patients with tuberculous pericarditis |
| failure-tb | patients with continuously or recurrently positive cultures after 4 months of appropriate treatment |
| all-tb-patients | all patients with tuberculosis |
| pediatric-moxifloxacin | children for whom moxifloxacin is selected |
| pediatric-emb-omission | HIV-uninfected children with no prior tuberculosis treatment, low local drug resistance, and no exposure to a person from a high-resistance area |
| baseline-hepatitis-risk | patients with injection drug use, birth in Asia or Africa or another hepatitis-endemic region, or HIV infection |
| baseline-diabetes-risk | patients with diabetes risk factors, including age >45 years or body mass index >25 kg/m2 |
| rifampin-boosted-pi | patients receiving rifampin with a ritonavir-boosted protease inhibitor regimen |
| rifampin-nevirapine | patients receiving rifampin with nevirapine |
| rifampin-efavirenz-over-60kg | patients >60 kg receiving rifampin with efavirenz |
| rifampin-raltegravir | patients receiving rifampin with raltegravir |
| rifampin-dolutegravir | patients receiving rifampin with dolutegravir |
| hemodialysis-tb | adult tuberculosis patients receiving hemodialysis |
| poorly-controlled-diabetes-tb | patients with tuberculosis and poorly controlled diabetes mellitus |
| silicotuberculosis | patients with silicotuberculosis |
| solid-organ-transplant-tb | solid organ transplant recipients with tuberculosis |
| tnf-inhibitor-tb | patients receiving a TNF-alpha inhibitor when active tuberculosis is suspected or confirmed |
| relapse-after-dot | patients with relapse after drug-susceptible tuberculosis treated using DOT |
| severe-treatment-failure | patients with treatment failure who are seriously ill or have a positive sputum AFB smear |
| pregnant-severe-tb | pregnant women with tuberculosis and HIV infection, extrapulmonary disease, or severe disease |
| breastfeeding-first-line | women treated with first-line agents who are deemed noninfectious |
| rifampin-lopinavir | patients receiving rifampin with lopinavir/ritonavir |
| pediatric-rifapentine | children receiving rifapentine for active tuberculosis |
| pediatric-pyridoxine-risk | children with malnutrition, HIV infection, or breastfeeding |
| pediatric-meningitis | children with tuberculous meningitis |
| immunocompromising-comorbidity | patients with conditions that alter immune responsiveness |
| neuropathy-risk | persons at risk of neuropathy, including pregnancy, breastfeeding, HIV, diabetes, alcoholism, malnutrition, chronic renal failure, or advanced age |
| peripheral-neuropathy | patients with peripheral neuropathy |
| ethambutol-treated | patients receiving ethambutol |
| rifabutin-boosted-pi | patients receiving rifabutin with a ritonavir-boosted protease inhibitor regimen |
| rifabutin-efavirenz | patients receiving rifabutin with efavirenz |
| returned-after-loss | patients returned to treatment after interim loss to follow-up |
| drug-rash | patients who develop rash during antituberculosis therapy |
| drug-fever | patients with suspected drug fever during antituberculosis therapy |
| obese-tb | patients >20% above ideal body weight |
| itchy-rash-no-systemic | patients with mainly itchy rash without mucous-membrane involvement or systemic signs |
| petechial-rash-low-platelets | patients with petechial rash and thrombocytopenia during rifamycin therapy |
| generalized-rash | patients with a generalized erythematous rash |
| severe-systemic-rash | patients with severe systemic hypersensitivity reactions |
| improved-drug-rash | patients whose antituberculosis-drug rash has substantially improved |
| recurrent-hepatotoxicity | patients whose symptoms recur or ALT rises during sequential DILI rechallenge |
| severe-hepatitis-rif-inh-tolerated | patients with severe hepatitis who tolerate RIF and INH during rechallenge |
| rifamycin-contraception | women of reproductive potential using oral contraceptives while receiving a rifamycin |
| rifamycin-warfarin | patients receiving warfarin with a rifamycin |
| rifamycin-corticosteroid | patients receiving corticosteroids with a rifamycin |
| rifamycin-methadone | patients receiving methadone with RIF or RPT |
| rifamycin-thyroid | patients receiving levothyroxine with a rifamycin |
| rifamycin-immunosuppressant | patients receiving cyclosporine or tacrolimus with a rifamycin |
| rifamycin-anticonvulsant | patients receiving phenytoin or lamotrigine with a rifamycin |
| rifamycin-sulfonylurea | patients receiving a sulfonylurea hypoglycemic with a rifamycin |
| rifamycin-azole | patients receiving an azole antifungal with a rifamycin |
| rifamycin-co-medication | patients receiving the named co-medication with a rifamycin |
| initial-positive-isolate | an initial positive M. tuberculosis culture, regardless of source |
| tdm-patients | patients undergoing therapeutic drug monitoring |
| fluoroquinolone-recipients | patients receiving a fluoroquinolone |

## Quantities

| key | verbatim |
| --- | --- |
| empiric-initial-regimen | empiric initial regimen decision point |
| directly-observed-therapy | directly observed therapy decision point |
| case-management | case management decision point |
| standard-regimen-duration | standard regimen duration decision point |
| pyridoxine-prophylaxis-dose | pyridoxine prophylaxis dose decision point |
| pyridoxine-neuropathy-dose | pyridoxine neuropathy dose decision point |
| daily-regimen-dose-count | daily regimen dose count decision point |
| five-day-regimen-dose-count | five day regimen dose count decision point |
| thrice-weekly-continuation-dose-count | thrice weekly continuation dose count decision point |
| thrice-weekly-whole-regimen-count | thrice weekly whole regimen count decision point |
| twice-weekly-regimen-count | twice weekly regimen count decision point |
| intensive-phase-frequency | intensive phase frequency decision point |
| intensive-phase-frequency-low-risk | intensive phase frequency low risk decision point |
| intensive-phase-frequency-rare | intensive phase frequency rare decision point |
| continuation-phase-frequency | continuation phase frequency decision point |
| continuation-phase-frequency-low-risk | continuation phase frequency low risk decision point |
| once-weekly-continuation-policy | once weekly continuation policy decision point |
| adult-isoniazid-dose | adult isoniazid dose decision point |
| pediatric-isoniazid-dose | pediatric isoniazid dose decision point |
| adult-rifampin-dose | adult rifampin dose decision point |
| pediatric-rifampin-dose | pediatric rifampin dose decision point |
| adult-rifabutin-dose | adult rifabutin dose decision point |
| adult-rifapentine-dose | adult rifapentine dose decision point |
| adult-pyrazinamide-dose | adult pyrazinamide dose decision point |
| pediatric-pyrazinamide-dose | pediatric pyrazinamide dose decision point |
| adult-ethambutol-dose | adult ethambutol dose decision point |
| pediatric-ethambutol-dose | pediatric ethambutol dose decision point |
| adult-levofloxacin-dose | adult levofloxacin dose decision point |
| pediatric-levofloxacin-dose | pediatric levofloxacin dose decision point |
| adult-moxifloxacin-dose | adult moxifloxacin dose decision point |
| pediatric-moxifloxacin-dose | pediatric moxifloxacin dose decision point |
| pediatric-moxifloxacin-serum-target | pediatric moxifloxacin serum target decision point |
| pediatric-emb-omission-regimen | pediatric emb omission regimen decision point |
| adult-dose-definition | adult dose definition decision point |
| pediatric-rifapentine-eligibility | pediatric rifapentine eligibility decision point |
| sputum-monitoring-frequency | sputum monitoring frequency decision point |
| culture-conversion-checkpoint | culture conversion checkpoint decision point |
| baseline-laboratory-assessment | baseline laboratory assessment decision point |
| baseline-hiv-testing | baseline hiv testing decision point |
| ethambutol-vision-monitoring | ethambutol vision monitoring decision point |
| chest-radiograph-monitoring | chest radiograph monitoring decision point |
| weight-monitoring | weight monitoring decision point |
| liver-test-monitoring | liver test monitoring decision point |
| hepatitis-screening | hepatitis screening decision point |
| diabetes-screening | diabetes screening decision point |
| extended-continuation-duration | extended continuation duration decision point |
| intensive-interruption-restart | intensive interruption restart decision point |
| continuation-interruption-restart | continuation interruption restart decision point |
| completion-time-window | completion time window decision point |
| repeat-drug-susceptibility-testing | repeat drug susceptibility testing decision point |
| therapeutic-drug-monitoring-samples | therapeutic drug monitoring samples decision point |
| fluoroquinolone-cation-separation | fluoroquinolone cation separation decision point |
| hepatotoxicity-stop-threshold | hepatotoxicity stop threshold decision point |
| hepatotoxicity-severity | hepatotoxicity severity decision point |
| hepatotoxicity-rechallenge-threshold | hepatotoxicity rechallenge threshold decision point |
| hiv-regimen-duration-with-art | hiv regimen duration with art decision point |
| hiv-regimen-duration-without-art | hiv regimen duration without art decision point |
| art-start-timing-low-cd4 | art start timing low cd4 decision point |
| art-start-timing-higher-cd4 | art start timing higher cd4 decision point |
| art-start-timing-meningitis | art start timing meningitis decision point |
| rifabutin-boosted-pi-dose | rifabutin boosted pi dose decision point |
| nevirapine-rifampin-dose | nevirapine rifampin dose decision point |
| efavirenz-rifampin-dose | efavirenz rifampin dose decision point |
| raltegravir-rifampin-dose | raltegravir rifampin dose decision point |
| dolutegravir-rifampin-dose | dolutegravir rifampin dose decision point |
| lopinavir-ritonavir-rifampin-dose | lopinavir ritonavir rifampin dose decision point |
| rifabutin-boosted-pi-alternative-dose | rifabutin boosted pi alternative dose decision point |
| rifabutin-efavirenz-dose | rifabutin efavirenz dose decision point |
| iris-prednisone-dose | iris prednisone dose decision point |
| meningitis-regimen-duration | meningitis regimen duration decision point |
| meningitis-steroid-duration | meningitis steroid duration decision point |
| culture-negative-regimen-duration | culture negative regimen duration decision point |
| pediatric-standard-regimen | pediatric standard regimen decision point |
| pediatric-sputum-sampling | pediatric sputum sampling decision point |
| pediatric-treatment-frequency | pediatric treatment frequency decision point |
| pediatric-radiograph-resolution | pediatric radiograph resolution decision point |
| pregnancy-no-pza-duration | pregnancy no pza duration decision point |
| pregnancy-pza-decision | pregnancy pza decision decision point |
| pregnancy-pza-severe-disease | pregnancy pza severe disease decision point |
| breastfeeding-first-line-action | breastfeeding first line action decision point |
| pregnancy-pyridoxine-dose | pregnancy pyridoxine dose decision point |
| infant-pyridoxine-dose | infant pyridoxine dose decision point |
| renal-isoniazid-dose | renal isoniazid dose decision point |
| renal-rifampin-dose | renal rifampin dose decision point |
| renal-pyrazinamide-dose | renal pyrazinamide dose decision point |
| renal-ethambutol-dose | renal ethambutol dose decision point |
| renal-levofloxacin-dose | renal levofloxacin dose decision point |
| renal-moxifloxacin-dose | renal moxifloxacin dose decision point |
| renal-cycloserine-dose | renal cycloserine dose decision point |
| renal-ethionamide-dose | renal ethionamide dose decision point |
| renal-pas-dose | renal pas dose decision point |
| renal-injectable-dose | renal injectable dose decision point |
| hemodialysis-administration | hemodialysis administration decision point |
| renal-tdm-timing | renal tdm timing decision point |
| liver-no-pza-regimen | liver no pza regimen decision point |
| liver-no-inh-pza-regimen | liver no inh pza regimen decision point |
| liver-nonhepatotoxic-regimen | liver nonhepatotoxic regimen decision point |
| hepatic-monitoring-frequency | hepatic monitoring frequency decision point |
| advanced-liver-alt-interruption | advanced liver alt interruption decision point |
| older-adult-no-pza-duration | older adult no pza duration decision point |
| extrapulmonary-regimen-duration | extrapulmonary regimen duration decision point |
| lymph-node-tb-duration | lymph node tb duration decision point |
| pleural-tb-duration | pleural tb duration decision point |
| disseminated-tb-duration | disseminated tb duration decision point |
| genitourinary-tb-duration | genitourinary tb duration decision point |
| abdominal-tb-duration | abdominal tb duration decision point |
| bone-joint-spine-duration | bone joint spine duration decision point |
| pericardial-steroid-use | pericardial steroid use decision point |
| treatment-failure-definition | treatment failure definition decision point |
| delayed-response-evaluation | delayed response evaluation decision point |
| poorly-controlled-diabetes-duration | poorly controlled diabetes duration decision point |
| silicotuberculosis-duration | silicotuberculosis duration decision point |
| transplant-duration | transplant duration decision point |
| tnf-inhibitor-resumption | tnf inhibitor resumption decision point |
| relapse-retreatment | relapse retreatment decision point |
| failure-specialist-action | failure specialist action decision point |
| failure-empiric-regimen | failure empiric regimen decision point |
| failing-regimen-additions | failing regimen additions decision point |
| pediatric-ethambutol-vision-monitoring | pediatric ethambutol visual monitoring interval |
| pediatric-pyridoxine-dose | pediatric pyridoxine dose |
| pediatric-meningitis-regimen | pediatric tuberculous meningitis regimen and duration |
| pregnancy-treatment-initiation | pregnancy treatment-initiation threshold |
| liver-no-inh-regimen | hepatic-disease regimen without INH |
| immunocompromised-regimen | regimen for immunocompromising comorbidity |
| transplant-drug-monitoring | transplant immunosuppressant monitoring action |
| expanded-relapse-regimen | expanded empiric relapse regimen |
| adult-cycloserine-dose | adult cycloserine dose decision point |
| pediatric-cycloserine-dose | pediatric cycloserine dose decision point |
| adult-ethionamide-dose | adult ethionamide dose decision point |
| pediatric-ethionamide-dose | pediatric ethionamide dose decision point |
| adult-injectable-dose | adult injectable dose decision point |
| pediatric-injectable-dose | pediatric injectable dose decision point |
| adult-pas-dose | adult pas dose decision point |
| pediatric-pas-dose | pediatric pas dose decision point |
| pediatric-rifabutin-dose | pediatric rifabutin dose decision point |
| obese-initial-dose-basis | obese initial dose basis decision point |
| baseline-sputum-specimens | baseline sputum specimens decision point |
| baseline-rapid-molecular-test | baseline rapid molecular test decision point |
| baseline-first-line-dst | baseline first line dst decision point |
| baseline-rapid-resistance-testing | baseline rapid resistance testing decision point |
| emb-discontinuation | emb discontinuation decision point |
| return-after-loss-testing | return after loss testing decision point |
| return-after-loss-positive | return after loss positive decision point |
| return-after-loss-negative | return after loss negative decision point |
| rash-itchy-action | rash itchy action decision point |
| rash-petechial-action | rash petechial action decision point |
| rash-generalized-action | rash generalized action decision point |
| rash-severe-rechallenge | rash severe rechallenge decision point |
| rash-sequential-rechallenge | rash sequential rechallenge decision point |
| drug-fever-threshold-action | drug fever threshold action decision point |
| dili-rechallenge-recurrence | dili rechallenge recurrence decision point |
| severe-hepatitis-pza-action | severe hepatitis pza action decision point |
| emb-visual-abnormality-action | emb visual abnormality action decision point |
| rifamycin-contraception-action | rifamycin contraception action decision point |
| rifamycin-warfarin-action | rifamycin warfarin action decision point |
| rifamycin-corticosteroid-action | rifamycin corticosteroid action decision point |
| rifamycin-methadone-action | rifamycin methadone action decision point |
| rifamycin-levothyroxine-action | rifamycin levothyroxine action decision point |
| rifamycin-immunosuppressant-action | rifamycin immunosuppressant action decision point |
| rifamycin-anticonvulsant-action | rifamycin anticonvulsant action decision point |
| rifamycin-sulfonylurea-action | rifamycin sulfonylurea action decision point |
| rifamycin-azole-action | rifamycin azole action decision point |
| rifamycin-nnrti-action | rifamycin nnrti action decision point |
| rifamycin-insti-ccr5-action | rifamycin insti ccr5 action decision point |
| rifamycin-macrolide-action | rifamycin macrolide action decision point |
| rifamycin-other-antiinfective-action | rifamycin other antiinfective action decision point |
| rifamycin-tamoxifen-action | rifamycin tamoxifen action decision point |
| rifamycin-cardiovascular-action | rifamycin cardiovascular action decision point |
| rifamycin-theophylline-action | rifamycin theophylline action decision point |
| rifamycin-hypolipidemic-action | rifamycin hypolipidemic action decision point |
| rifamycin-psychotropic-action | rifamycin psychotropic action decision point |
| initial-positive-culture-dst | initial positive-culture susceptibility testing |
| return-after-loss-dot | directly observed therapy after return from loss to follow-up |
| rash-systemic-corticosteroid | systemic corticosteroid action for severe drug rash |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| empiric-initial-regimen | presumed-pulmonary-tb | INH + RIF + PZA + EMB promptly | RENDERED: empiric treatment with a 4-drug regimen is initiated promptly | idsa-2016 | 2 | p2/narrative/empiric-four-drug | narrative |
| directly-observed-therapy | all-tb-patients | use DOT rather than self-administered therapy | RENDERED: We recommend using DOT rather than SAT for routine treatment of patients with all forms of tuberculosis | idsa-2016 | 15 | p15/grade-spelled-out/1 | recommendation |
| case-management | all-tb-patients | use case management interventions during treatment | RENDERED: We suggest using case management interventions during treatment of patients with tuberculosis | idsa-2016 | 15 | p15/grade-spelled-out/2 | recommendation |
| standard-regimen-duration | drug-susceptible-pulmonary-tb | 2 months INH/RIF/PZA/EMB, then 4 months INH/RIF | RENDERED: the preferred regimen consists of an intensive phase of 2 months of INH, RIF, PZA, and EMB followed by a continuation phase of 4 months of INH and RIF | idsa-2016 | 4 | p4/narrative/preferred-regimen | narrative |
| pyridoxine-prophylaxis-dose | neuropathy-risk | 25-50 mg/day | RENDERED: Pyridoxine (vitamin B6), 25-50 mg/day, is given with INH to all persons at risk of neuropathy | idsa-2016 | 4 | p4/narrative/pyridoxine | narrative |
| pyridoxine-neuropathy-dose | peripheral-neuropathy | 100 mg/day | RENDERED: For patients with peripheral neuropathy, experts recommend increasing pyridoxine dose to 100 mg/day. | idsa-2016 | 4 | p4/narrative/pyridoxine-neuropathy | narrative |
| daily-regimen-dose-count | drug-susceptible-pulmonary-tb | intensive 56 doses in 8 weeks; continuation 126 doses in 18 weeks; total 182 doses | RENDERED: 7 d/wk for 56 doses (8 wk) ... 7 d/wk for 126 doses (18 wk) ... 182 | idsa-2016 | 4 | p4/narrative/regimen1-seven-day | narrative |
| five-day-regimen-dose-count | drug-susceptible-pulmonary-tb | intensive 40 doses in 8 weeks; continuation 90 doses in 18 weeks; total 130 doses | RENDERED: 5 d/wk for 40 doses (8 wk) ... 5 d/wk for 90 doses (18 wk) ... 130 | idsa-2016 | 4 | p4/narrative/regimen1-five-day | narrative |
| thrice-weekly-continuation-dose-count | low-relapse-risk-hiv-negative | 54 doses in 18 weeks | RENDERED: 3 times weekly for 54 doses (18 wk) | idsa-2016 | 4 | p4/narrative/regimen2 | narrative |
| thrice-weekly-whole-regimen-count | low-relapse-risk-hiv-negative | intensive 24 doses in 8 weeks; continuation 54 doses in 18 weeks; total 78 doses | RENDERED: 3 times weekly for 24 doses (8 wk) ... 3 times weekly for 54 doses (18 wk) ... 78 | idsa-2016 | 4 | p4/narrative/regimen3 | narrative |
| twice-weekly-regimen-count | hiv-uninfected-low-risk | 14 daily doses, then 12 twice-weekly doses; continuation 36 doses in 18 weeks; total 62 doses | RENDERED: 7 d/wk for 14 doses then twice weekly for 12 doses ... Twice weekly for 36 doses (18 wk) ... 62 | idsa-2016 | 4 | p4/narrative/regimen4 | narrative |
| intensive-phase-frequency | drug-susceptible-pulmonary-tb | daily | RENDERED: We recommend the use of daily rather than intermittent dosing in the intensive phase of therapy | idsa-2016 | 17 | p17/grade-spelled-out/1 | recommendation |
| intensive-phase-frequency-low-risk | low-relapse-risk-hiv-negative | thrice weekly | RENDERED: thrice-weekly dosing during the intensive phase as an alternative to daily dosing | idsa-2016 | 17 | p17/grade-spelled-out/2 | recommendation |
| intensive-phase-frequency-rare | hiv-uninfected-low-risk | twice weekly only after at least 2 weeks daily therapy | RENDERED: twice-weekly dosing after an initial 2 weeks of daily therapy may be considered | idsa-2016 | 17 | p17/grade-spelled-out/3 | recommendation |
| continuation-phase-frequency | drug-susceptible-pulmonary-tb | daily or thrice weekly | RENDERED: We recommend use of daily or thrice-weekly dosing in the continuation phase | idsa-2016 | 17 | p17/grade-spelled-out/4 | recommendation |
| continuation-phase-frequency-low-risk | low-relapse-risk-hiv-negative | twice weekly | RENDERED: twice-weekly dosing may be considered after completion of 2 months of daily therapy | idsa-2016 | 17 | p17/grade-spelled-out/5 | recommendation |
| once-weekly-continuation-policy | hiv-uninfected-low-risk | do not generally use INH 900 mg plus rifapentine 600 mg once weekly | RENDERED: We suggest that use of once-weekly therapy with INH 900 mg and rifapentine 600 mg in the continuation phase be used only in uncommon situations | idsa-2016 | 17 | p17/grade-spelled-out/6 | recommendation |
| once-weekly-continuation-policy | hiv-uninfected-low-risk | INH 900 mg plus rifapentine 600 mg once weekly may be considered only when more frequent DOT is difficult to achieve | RENDERED: once-weekly dosing with INH 900 mg plus rifapentine 600 mg may be considered for continuation phase therapy only in uncommon situations | idsa-2016 | 17 | p17/narrative/once-weekly-exception | narrative |
| adult-isoniazid-dose | adult-tb | daily 5 mg/kg, typically 300 mg; intermittent 15 mg/kg, typically 900 mg | RENDERED: Isoniazid ... Adults 5 mg/kg (typically 300 mg) ... 15 mg/kg (typically 900 mg) | idsa-2016 | 5 | p5/narrative/isoniazid-adult | narrative |
| pediatric-isoniazid-dose | pediatric-tb | daily 10-15 mg/kg; twice weekly 20-30 mg/kg | RENDERED: Children 10-15 mg/kg ... 20-30 mg/kg | idsa-2016 | 5 | p5/narrative/isoniazid-child | narrative |
| adult-rifampin-dose | adult-tb | 10 mg/kg, typically 600 mg | RENDERED: Rifampin ... Adults 10 mg/kg (typically 600 mg) | idsa-2016 | 5 | p5/narrative/rifampin-adult | narrative |
| pediatric-rifampin-dose | pediatric-tb | 10-20 mg/kg | RENDERED: Rifampin ... Children 10-20 mg/kg | idsa-2016 | 5 | p5/narrative/rifampin-child | narrative |
| adult-rifabutin-dose | adult-tb | 5 mg/kg, typically 300 mg daily; intermittent not recommended | RENDERED: Rifabutin ... 5 mg/kg (typically 300 mg) ... Not recommended | idsa-2016 | 5 | p5/narrative/rifabutin | narrative |
| adult-rifapentine-dose | adult-tb | 10-20 mg/kg | RENDERED: Rifapentine ... Adults 10-20 mg/kg | idsa-2016 | 5 | p5/narrative/rifapentine | narrative |
| adult-pyrazinamide-dose | adult-tb | daily 20-25 mg/kg; twice weekly 50 mg/kg; thrice weekly 35 mg/kg | RENDERED: Pyrazinamide ... Adults 20-25 mg/kg ... 50 mg/kg ... 35 mg/kg | idsa-2016 | 5 | p5/narrative/pyrazinamide-adult | narrative |
| pediatric-pyrazinamide-dose | pediatric-tb | daily 30-40 mg/kg; twice weekly 50 mg/kg | RENDERED: Children 35 mg/kg (30-40 mg/kg) ... 50 mg/kg | idsa-2016 | 5 | p5/narrative/pyrazinamide-child | narrative |
| adult-ethambutol-dose | adult-tb | daily 15-20 mg/kg; twice weekly 50 mg/kg; thrice weekly 25-30 mg/kg | RENDERED: Ethambutol ... Adults 15-20 mg/kg ... 50 mg/kg ... 25-30 mg/kg | idsa-2016 | 5 | p5/narrative/ethambutol-adult | narrative |
| pediatric-ethambutol-dose | pediatric-tb | daily 15-25 mg/kg; twice weekly 50 mg/kg | RENDERED: Children 20 mg/kg (15-25 mg/kg) ... 50 mg/kg | idsa-2016 | 5 | p5/narrative/ethambutol-child | narrative |
| adult-levofloxacin-dose | adult-tb | 500-1000 mg daily | RENDERED: Levofloxacin ... 500-1000 mg daily | idsa-2016 | 6 | p6/narrative/levofloxacin-adult | narrative |
| pediatric-levofloxacin-dose | pediatric-tb | optimal dose unknown; clinical data suggest 15-20 mg/kg daily | RENDERED: The optimal dose is not known, but clinical data suggest 15-20 mg/kg | idsa-2016 | 5 | p5/narrative/levofloxacin-child | narrative |
| adult-moxifloxacin-dose | adult-tb | 400 mg daily | RENDERED: Moxifloxacin ... 400 mg daily | idsa-2016 | 6 | p6/narrative/moxifloxacin-adult | narrative |
| adult-cycloserine-dose | adult-tb | 10-15 mg/kg total, usually 250-500 mg once or twice daily; start 250 mg daily and titrate; use serum concentrations; few tolerate 500 mg twice daily; intermittent data inadequate | RENDERED: Cycloserine ... Adults 10-15 mg/kg total (usually 250-500 mg once or twice daily) ... starting with 250 mg once daily and gradually increasing as tolerated. Serum concentrations often are useful ... Few patients tolerate 500 mg twice daily ... inadequate data to support intermittent administration. | idsa-2016 | 5 | p5/narrative/cycloserine-adult | narrative |
| pediatric-cycloserine-dose | pediatric-tb | 15-20 mg/kg total divided 1-2 times daily | RENDERED: Cycloserine ... Children 15-20 mg/kg total (divided 1-2 times daily) | idsa-2016 | 5 | p5/narrative/cycloserine-child | narrative |
| adult-ethionamide-dose | adult-tb | 15-20 mg/kg total, usually 250-500 mg once or twice daily; may give at bedtime or main meal; start 250 mg daily and titrate; use serum concentrations; few tolerate 500 mg twice daily; intermittent data inadequate | RENDERED: Ethionamide ... Adults 15-20 mg/kg total (usually 250-500 mg once or twice daily) ... can be given at bedtime or with a main meal ... starting with 250 mg once daily and gradually increasing as tolerated. Serum concentrations may be useful ... Few patients tolerate 500 mg twice daily ... inadequate data to support intermittent administration. | idsa-2016 | 5 | p5/narrative/ethionamide-adult | narrative |
| pediatric-ethionamide-dose | pediatric-tb | 15-20 mg/kg total divided 1-2 times daily | RENDERED: Ethionamide ... Children 15-20 mg/kg total (divided 1-2 times daily) | idsa-2016 | 5 | p5/narrative/ethionamide-child | narrative |
| adult-injectable-dose | adult-tb | streptomycin, amikacin/kanamycin, or capreomycin 15 mg/kg daily; some use 25 mg/kg 3 times weekly | RENDERED: Adults 15 mg/kg daily. Some clinicians prefer 25 mg/kg 3 times weekly. | idsa-2016 | 5 | p5/narrative/injectables-adult | narrative |
| pediatric-injectable-dose | pediatric-tb | streptomycin, amikacin/kanamycin, or capreomycin 15-20 mg/kg daily or 25-30 mg/kg twice weekly | RENDERED: Children 15-20 mg/kg ... 25-30 mg/kg | idsa-2016 | 5 | p5/narrative/injectables-child | narrative |
| adult-pas-dose | adult-tb | 8-12 g total, usually 4000 mg 2-3 times daily | RENDERED: Adults 8-12 g total (usually 4000 mg 2-3 times daily) | idsa-2016 | 5 | p5/narrative/pas-adult | narrative |
| pediatric-pas-dose | pediatric-tb | 200-300 mg/kg total, usually 100 mg/kg 2-3 times daily | RENDERED: Children 200-300 mg/kg total (usually divided 100 mg/kg given 2 to 3 times daily) | idsa-2016 | 5 | p5/narrative/pas-child | narrative |
| pediatric-rifabutin-dose | pediatric-tb | appropriate dose unknown; estimated 5 mg/kg | RENDERED: Appropriate dosing for children is unknown. Estimated at 5 mg/kg. | idsa-2016 | 5 | p5/narrative/rifabutin-child | narrative |
| obese-initial-dose-basis | obese-tb | actual-weight dosing is acceptable; IBW dosing may be preferred initially; some clinicians prefer modified IBW = IBW + 0.40 x (actual weight - IBW); TDM may be considered | RENDERED: Dosing based on actual weight is acceptable ... For obese patients (>20% above ideal body weight [IBW]), dosing based on IBW may be preferred for initial doses. Some clinicians prefer a modified IBW (IBW + [0.40 × (actual weight - IBW)]) ... therapeutic drug monitoring may be considered | idsa-2016 | 6 | p6/narrative/obese-dosing | narrative |
| pediatric-moxifloxacin-dose | pediatric-moxifloxacin | optimal dose unknown; some experts use 10 mg/kg daily | RENDERED: The optimal dose is not known. Some experts use 10 mg/kg daily dosing | idsa-2016 | 6 | p6/narrative/moxifloxacin-child-dose | narrative |
| pediatric-moxifloxacin-serum-target | pediatric-moxifloxacin | proposed 3-5 µL/mL at 2 hours postdose; source unit retained as printed and uncertain | RENDERED: Aiming for serum concentrations of 3-5 µL/mL 2 h postdose is proposed by experts as a reasonable target. | idsa-2016 | 6 | p6/narrative/moxifloxacin-child-target | narrative |
| pediatric-emb-omission-regimen | pediatric-emb-omission | INH/RIF/PZA for initial 2 months may be used by some clinicians; AAP and most experts include EMB | RENDERED: some clinicians use a 3-drug regimen (INH, rifampin, and pyrazinamide) in the initial 2 months ... the American Academy of Pediatrics and most experts include EMB | idsa-2016 | 6 | p6/narrative/pediatric-emb-omission | narrative |
| adult-dose-definition | pediatric-tb | adult dosing begins at age 15 years or weight >40 kg in a younger child | RENDERED: adult dosing begins at age 15 years or at a weight of >40 kg in younger children | idsa-2016 | 6 | p6/narrative/adult-dose-definition | narrative |
| pediatric-rifapentine-eligibility | pediatric-rifapentine | age >=12 years use adult once-weekly dose; not FDA approved for active tuberculosis under age 12 | RENDERED: for children ≥12 y of age, same dosing as for adults, administered once weekly. Rifapentine is not FDA-approved for treatment of active tuberculosis in children <12 y of age. | idsa-2016 | 5 | p5/narrative/pediatric-rifapentine | narrative |
| sputum-monitoring-frequency | drug-susceptible-pulmonary-tb | monthly until 2 consecutive cultures are negative | RENDERED: obtain sputum for smear and culture at monthly intervals until 2 consecutive specimens are negative on culture | idsa-2016 | 7 | p7/narrative/monthly-culture | narrative |
| culture-conversion-checkpoint | drug-susceptible-pulmonary-tb | culture at completion of 2 months | RENDERED: obtaining a sputum specimen at the time of completion of 2 months of treatment is critical | idsa-2016 | 7 | p7/narrative/two-month-culture | narrative |
| baseline-sputum-specimens | presumed-pulmonary-tb | 3 specimens collected 8-24 hours apart, with at least 1 early-morning specimen | RENDERED: At least 3 sputum specimens are obtained ... each collected in 8- to 24-hour intervals, with at least 1 being an early morning specimen. | idsa-2016 | 20 | p20/narrative/baseline-sputum | narrative |
| baseline-rapid-molecular-test | presumed-pulmonary-tb | at least one baseline specimen | RENDERED: At least one baseline specimen should be tested using a rapid molecular test. | idsa-2016 | 7 | p7/narrative/figure2-rapid-molecular | narrative |
| baseline-first-line-dst | initial-positive-isolate | test initial positive culture for INH, RIF, EMB, and PZA susceptibility regardless of source | RENDERED: Susceptibility testing for INH, RIF, EMB, and PZA is performed on an initial positive culture, regardless of the source. | idsa-2016 | 20 | p20/narrative/baseline-first-line-dst | narrative |
| initial-positive-culture-dst | initial-positive-isolate | perform susceptibility testing on the initial positive culture regardless of source | RENDERED: Susceptibility testing for INH, RIF, EMB, and PZA is performed on an initial positive culture, regardless of the source. | idsa-2016 | 20 | p20/narrative/initial-positive-culture-dst | narrative |
| baseline-rapid-resistance-testing | presumed-pulmonary-tb | molecular resistance testing for patients at risk; consider for all when resources allow | RENDERED: Molecular resistance testing should be performed for patients with risk for drug resistance ... may be considered for all patients when resources permit. | idsa-2016 | 20 | p20/narrative/rapid-resistance | narrative |
| baseline-laboratory-assessment | adult-tb | baseline AST, ALT, bilirubin, alkaline phosphatase, creatinine, and platelet count | RENDERED: Baseline measurements of serum aminotransferases, bilirubin, alkaline phosphatase, creatinine, and a platelet count | idsa-2016 | 7 | p7/narrative/baseline-laboratory | narrative |
| baseline-hiv-testing | all-tb-patients | HIV testing at baseline | RENDERED: HIV serology should be performed on all patients | idsa-2016 | 7 | p7/narrative/hiv-testing | narrative |
| ethambutol-vision-monitoring | ethambutol-treated | baseline visual acuity and color discrimination; monthly color discrimination | RENDERED: Patients on EMB: baseline visual acuity ... and color discrimination tests, followed by monthly inquiry about visual disturbance and monthly color discrimination tests. | idsa-2016 | 7 | p7/narrative/vision | narrative |
| chest-radiograph-monitoring | all-tb-patients | baseline for all; month 2 if baseline cultures negative; end-of-treatment optional | RENDERED: Obtain chest radiograph at baseline for all patients, and also at month 2 if baseline cultures are negative. End-of-treatment chest radiograph is optional. | idsa-2016 | 7 | p7/narrative/figure2-chest-radiograph | narrative |
| weight-monitoring | all-tb-patients | monthly and adjust dose if needed | RENDERED: Monitor weight monthly to assess response to treatment; adjust medication dose if needed. | idsa-2016 | 7 | p7/narrative/figure2-weight | narrative |
| liver-test-monitoring | all-tb-patients | baseline; repeat for baseline abnormality, hepatotoxic symptoms, or hepatic-risk conditions | RENDERED: Liver function tests only at baseline unless there were abnormalities at baseline, symptoms consistent with hepatotoxicity develop, or for patients who chronically consume alcohol | idsa-2016 | 7 | p7/narrative/figure2-liver-tests | narrative |
| hepatitis-screening | baseline-hepatitis-risk | baseline hepatitis B and C screening | RENDERED: Patients with hepatitis B or C risk factor ... should have screening tests for these viruses. | idsa-2016 | 7 | p7/narrative/figure2-hepatitis | narrative |
| diabetes-screening | baseline-diabetes-risk | fasting glucose or hemoglobin A1c | RENDERED: Fasting glucose or hemoglobin A1c for patients with risk factors for diabetes ... age >45 years, body mass index >25 kg/m2 | idsa-2016 | 7 | p7/narrative/figure2-diabetes | narrative |
| extended-continuation-duration | cavity-positive-two-month | continuation phase 7 months; total treatment 9 months | RENDERED: extend the continuation phase with INH and RIF for an additional 3 months (ie, a continuation phase of 7 months in duration, corresponding to a total of 9 months of therapy) | idsa-2016 | 7 | p7/narrative/extension | narrative |
| intensive-interruption-restart | treatment-interruption | restart if lapse >=14 days; continue if lapse <14 days and complete within 3 months | RENDERED: Lapse is <14 d in duration ... Continue treatment to complete planned total number of doses (as long as all doses are completed within 3 mo) ... Lapse is >=14 d in duration ... Restart treatment from the beginning | idsa-2016 | 8 | p8/narrative/intensive | narrative |
| continuation-interruption-restart | treatment-interruption | restart if cumulative lapse >=3 months or if <80% doses and consecutive lapse >2 months | RENDERED: Received <80% of doses and lapse was <3 mo in duration ... If consecutive lapse is >2 mo, restart treatment from the beginning ... Lapse is ≥3 mo in duration ... Restart therapy from the beginning | idsa-2016 | 8 | p8/narrative/continuation | narrative |
| completion-time-window | drug-susceptible-pulmonary-tb | intensive doses within 3 months; 4-month continuation within 6 months; 6-month regimen within 9 months | RENDERED: complete all doses of the intensive phase within 3 months and those of the 4-month continuation phase within 6 months, so that the 6-month regimen is completed within 9 months | idsa-2016 | 22 | p22/narrative/completion-window | narrative |
| repeat-drug-susceptibility-testing | drug-susceptible-pulmonary-tb | repeat when culture remains positive after >=3 months | RENDERED: repeat drug susceptibility tests are indicated for patients with positive cultures after 3 months of treatment | idsa-2016 | 21 | p21/narrative/repeat-dst | narrative |
| emb-discontinuation | drug-susceptible-pulmonary-tb | stop EMB once INH and RIF susceptibility is demonstrated | RENDERED: EMB can be discontinued as soon as the results of drug susceptibility studies demonstrate that the isolate is susceptible to INH and RIF. | idsa-2016 | 18 | p18/narrative/emb-stop | narrative |
| return-after-loss-testing | returned-after-loss | obtain additional sputum for repeat culture and DST | RENDERED: at the time the patient is returned to treatment, additional sputum are obtained for repeat culture and drug susceptibility testing. | idsa-2016 | 21 | p21/narrative/return-testing | narrative |
| return-after-loss-positive | returned-after-loss | restart regimen if cultures remain positive | RENDERED: If the cultures are still positive, the treatment regimen is restarted. | idsa-2016 | 21 | p21/narrative/return-positive | narrative |
| return-after-loss-negative | returned-after-loss | if cultures negative and original isolate susceptible with INH/RIF/PZA intensive phase, give an additional 4 months INH/RIF | RENDERED: If sputum cultures are negative ... given an additional 4 months of INH and RIF chemotherapy, as long as the original specimen was drug susceptible and the original intensive phase regimen included INH, RIF, and PZA. | idsa-2016 | 21 | p21/narrative/return-negative | narrative |
| return-after-loss-dot | returned-after-loss | use DOT subsequently regardless of interruption timing or duration | RENDERED: Regardless of the timing and duration of the interruption, DOT is used subsequently. | idsa-2016 | 21 | p21/narrative/return-dot | narrative |
| therapeutic-drug-monitoring-samples | tdm-patients | collect at 2 and 6 hours after dosing | RENDERED: The first is collected 2 hours after the dose ... a second sample, often collected 6 hours postdose | idsa-2016 | 24 | p24/narrative/tdm-sampling | narrative |
| fluoroquinolone-cation-separation | fluoroquinolone-recipients | separate by at least 2 hours | RENDERED: should not be administered within 2 hours of ingesting milk-based products, antacids, or other medications containing divalent cations | idsa-2016 | 24 | p24/narrative/fluoroquinolone-separation | narrative |
| hepatotoxicity-stop-threshold | hepatic-injury | ALT >=3 times ULN with symptoms or >=5 times ULN without symptoms | RENDERED: suspected when the ALT level is >=3 times the upper limit of normal in the presence of hepatitis symptoms, or >=5 times the upper limit of normal in the absence of symptoms | idsa-2016 | 8 | p8/narrative/dili-stop | narrative |
| hepatotoxicity-severity | hepatic-injury | mild <5 times ULN; moderate 5-10 times ULN; severe >10 times ULN or >500 IU | RENDERED: ALT increases are classified as mild (ALT level <5 times the upper limit of normal), moderate (ALT level 5-10 times normal), or severe (ALT level >10 times normal [ie, >500 IU]) | idsa-2016 | 8 | p8/narrative/dili-severity | narrative |
| hepatotoxicity-rechallenge-threshold | hepatic-injury | resume when ALT <2 times ULN; RIF first, INH about 1 week later, PZA 1 week after INH | RENDERED: once the ALT concentration returns to <2 times the upper limit of normal ... RIF is restarted first ... INH may be restarted ... after approximately 1 week ... PZA can be started 1 week after INH | idsa-2016 | 23 | p23/narrative/dili-rechallenge | narrative |
| rash-itchy-action | itchy-rash-no-systemic | treat with antihistamines and continue all antituberculosis medications | RENDERED: treatment is symptomatic with antihistamines, and all antituberculosis medications can be continued. | idsa-2016 | 22 | p22/narrative/rash-itchy | narrative |
| rash-petechial-action | petechial-rash-low-platelets | permanently stop rifamycin and monitor platelets until definite improvement | RENDERED: If the platelet count is low, the rifamycin is permanently stopped and the platelet count closely monitored until definite improvement is noted. | idsa-2016 | 22 | p22/narrative/rash-petechial | narrative |
| rash-generalized-action | generalized-rash | stop drugs | RENDERED: Drugs are also stopped if the patient has a generalized erythematous rash. | idsa-2016 | 22 | p22/narrative/rash-generalized | narrative |
| rash-severe-rechallenge | severe-systemic-rash | inpatient management may use several days between rechallenges; stop the drug if hypersensitivity markers recur | RENDERED: manage severe systemic reactions in the inpatient setting, using an interval of several days between drug rechallenges ... If any of these markers develop, then the drug is stopped | idsa-2016 | 23 | p23/narrative/rash-severe | narrative |
| rash-systemic-corticosteroid | severe-systemic-rash | systemic corticosteroids may be used | RENDERED: Systemic corticosteroids may be used to treat severe systemic reactions. | idsa-2016 | 23 | p23/narrative/rash-systemic-corticosteroid | narrative |
| rash-sequential-rechallenge | improved-drug-rash | restart individually every 2-3 days: RIF, then INH, then EMB or PZA; stop last-added drug if rash recurs; after first 3 restart, do not restart fourth unless rash was mild and drug essential | RENDERED: medications can be restarted individually at intervals of 2-3 days. RIF is restarted first ... followed by INH, then EMB or PZA. If the rash recurs, the last drug added is stopped. If the first 3 drugs have been restarted without a rash, the fourth drug is not restarted unless the rash was mild and that drug essential. | idsa-2016 | 23 | p23/narrative/rash-rechallenge | narrative |
| drug-fever-threshold-action | drug-fever | diagnosis of exclusion after excluding tuberculosis fever, paradoxical reaction especially with HIV, and superinfection; temperature >=39 °C; stopping drugs usually resolves within 24 hours; restart individually every 2-3 days once afebrile | RENDERED: Drug fever is essentially a diagnosis of exclusion. Other causes of fever such as tuberculosis ... paradoxical reaction, especially in HIV-infected patients ... and superinfection must be excluded ... body temperatures ≥39°C ... Stopping drugs usually resolves the fever within 24 hours. Once afebrile, the patient should restart drugs individually every 2-3 days | idsa-2016 | 23 | p23/narrative/drug-fever | narrative |
| dili-rechallenge-recurrence | recurrent-hepatotoxicity | stop the last drug added | RENDERED: If symptoms recur or ALT increases, the last drug added should be stopped. | idsa-2016 | 23 | p23/narrative/dili-recurrence | narrative |
| severe-hepatitis-pza-action | severe-hepatitis-rif-inh-tolerated | discontinue PZA and consider extending total therapy to 9 months | RENDERED: If RIF and INH are tolerated and hepatitis was severe, PZA ... is discontinued ... total duration of therapy might be extended to 9 months. | idsa-2016 | 23 | p23/narrative/severe-hepatitis | narrative |
| emb-visual-abnormality-action | ethambutol-treated | promptly stop EMB; if vision does not improve, also stop INH | RENDERED: EMB is promptly discontinued if visual abnormalities are found. If vision does not improve with cessation of EMB, experts recommend stopping INH as well | idsa-2016 | 23 | p23/narrative/emb-visual-action | narrative |
| hiv-regimen-duration-with-art | hiv-tb-art | daily 6-month regimen: 2 months INH/RIF/PZA/EMB plus 4 months INH/RIF | RENDERED: standard 6-month daily regimen consisting of an intensive phase of 2 months of INH, RIF, PZA, and EMB followed by a continuation phase of 4 months of INH and RIF | idsa-2016 | 25 | p25/grade-spelled-out/1 | recommendation |
| hiv-regimen-duration-without-art | hiv-tb-no-art | continuation extended 3 months; total 9 months | RENDERED: we suggest extending the continuation phase with INH and RIF for an additional 3 months for a total of 9 months of therapy | idsa-2016 | 25 | p25/grade-spelled-out/2 | recommendation |
| art-start-timing-low-cd4 | hiv-tb-cd4-under-50 | within 2 weeks after tuberculosis treatment starts | RENDERED: ART should be initiated during tuberculosis treatment ... within the first 2 weeks ... in patients with CD4 counts <50 cells/µL | idsa-2016 | 25 | p25/grade-spelled-out/3 | recommendation |
| art-start-timing-higher-cd4 | hiv-tb-cd4-at-least-50 | by 8-12 weeks after tuberculosis treatment starts | RENDERED: by 8-12 weeks of tuberculosis treatment initiation for patients with CD4 counts >=50 cells/µL | idsa-2016 | 25 | p25/grade-spelled-out/3 | recommendation |
| art-start-timing-meningitis | hiv-tb-meningitis | do not initiate ART in first 8 weeks | RENDERED: ART should not be initiated in the first 8 weeks of antituberculosis therapy | idsa-2016 | 11 | p11/grade-spelled-out/1 | recommendation |
| rifabutin-boosted-pi-dose | rifabutin-boosted-pi | use rifabutin 150 mg daily; do not use rifampin with other protease inhibitors | RENDERED: For ritonavir-boosted regimens, give RFB 150 mg daily ... Do not use RIF with other protease inhibitors. | idsa-2016 | 10 | p10/narrative/rifabutin-boosted-pi | narrative |
| nevirapine-rifampin-dose | rifampin-nevirapine | omit 200 mg lead-in; give 400 mg daily | RENDERED: lead-in nevirapine dose of 200 mg daily should be omitted and 400 mg daily nevirapine dosage given | idsa-2016 | 10 | p10/narrative/nevirapine-rifampin | narrative |
| efavirenz-rifampin-dose | rifampin-efavirenz-over-60kg | experts advise efavirenz 600 mg daily | RENDERED: experts advise that efavirenz be given at standard dosage of 600 mg daily | idsa-2016 | 10 | p10/narrative/efavirenz-rifampin-experts | narrative |
| efavirenz-rifampin-dose | rifampin-efavirenz-over-60kg | FDA recommends efavirenz 800 mg daily | RENDERED: FDA recommends increasing efavirenz to 800 mg daily in persons >60 kg | idsa-2016 | 10 | p10/narrative/efavirenz-rifampin-fda | narrative |
| raltegravir-rifampin-dose | rifampin-raltegravir | increase to 800 mg twice daily; trial data show 400 mg twice daily similar | RENDERED: Increase dose of raltegravir to 800 mg twice daily with RIF, although clinical trial data show similar efficacy using 400 mg twice daily. | idsa-2016 | 10 | p10/narrative/raltegravir-rifampin | narrative |
| dolutegravir-rifampin-dose | rifampin-dolutegravir | 50 mg every 12 hours | RENDERED: Dolutegravir dose should be increased to 50 mg every 12 h with RIF. | idsa-2016 | 10 | p10/narrative/dolutegravir-rifampin | narrative |
| rifamycin-contraception-action | rifamycin-contraception | add a barrier contraceptive method | RENDERED: Women of reproductive potential on oral contraceptives should be advised to add a barrier method of contraception when on a rifamycin. | idsa-2016 | 10 | p10/narrative/rifamycin-contraception | narrative |
| rifamycin-warfarin-action | rifamycin-warfarin | monitor prothrombin time; may need 2- to 3-fold warfarin dose increase | RENDERED: Monitor prothrombin time; may require 2- to 3-fold warfarin dose increase. | idsa-2016 | 10 | p10/narrative/rifamycin-warfarin | narrative |
| rifamycin-corticosteroid-action | rifamycin-corticosteroid | monitor clinically; may need 2- to 3-fold corticosteroid dose increase | RENDERED: Monitor clinically; may require 2- to 3-fold increase in corticosteroid dose. | idsa-2016 | 10 | p10/narrative/rifamycin-corticosteroid | narrative |
| rifamycin-methadone-action | rifamycin-methadone | methadone dose increase may be required | RENDERED: RIF and RPT use may require methadone dose increase. | idsa-2016 | 10 | p10/narrative/rifamycin-methadone | narrative |
| rifamycin-levothyroxine-action | rifamycin-thyroid | monitor serum TSH; levothyroxine dose may need increase | RENDERED: Monitoring of serum TSH recommended; may require increased dose of levothyroxine. | idsa-2016 | 10 | p10/narrative/rifamycin-levothyroxine | narrative |
| rifamycin-immunosuppressant-action | rifamycin-immunosuppressant | consider RFB and monitor cyclosporine/tacrolimus serum concentrations | RENDERED: RFB may allow concomitant use of cyclosporine and a rifamycin; monitoring of cyclosporine and tacrolimus serum concentrations may assist with dosing. | idsa-2016 | 10 | p10/narrative/rifamycin-immunosuppressant | narrative |
| rifamycin-anticonvulsant-action | rifamycin-anticonvulsant | TDM; anticonvulsant dose may need increase | RENDERED: TDM recommended; may require anticonvulsant dose increase. | idsa-2016 | 10 | p10/narrative/rifamycin-anticonvulsant | narrative |
| rifamycin-sulfonylurea-action | rifamycin-sulfonylurea | monitor glucose; may need dose increase or alternative drug | RENDERED: Monitor blood glucose; may require dose increase or change to an alternate hypoglycemic drug. | idsa-2016 | 10 | p10/narrative/rifamycin-sulfonylurea | narrative |
| rifamycin-azole-action | rifamycin-azole | itraconazole, ketoconazole, or voriconazole may be subtherapeutic; fluconazole dose may need increase | RENDERED: Itraconazole, ketoconazole, and voriconazole concentrations may be subtherapeutic with any of the rifamycins. Fluconazole can be used with rifamycins, but the dose of fluconazole may have to be increased. | idsa-2016 | 10 | p10/narrative/rifamycin-azole | narrative |
| rifamycin-nnrti-action | rifamycin-co-medication | do not give RIF with rilpivirine or etravirine; do not give rilpivirine with RFB | RENDERED: Rilpivirine and etravirine should not be given with RIF ... Rilpivirine should not be given with RFB. | idsa-2016 | 10 | p10/narrative/rifamycin-nnrti | narrative |
| rifamycin-insti-ccr5-action | rifamycin-co-medication | do not use RIF with elvitegravir or maraviroc; RFB can be used | RENDERED: Do not use RIF with elvitegravir ... RIF should not be used with maraviroc. RFB can be used with maraviroc. | idsa-2016 | 10 | p10/narrative/rifamycin-insti-ccr5 | narrative |
| rifamycin-macrolide-action | rifamycin-co-medication | azithromycin has no significant interaction; clarithromycin plus RFB raises toxicity/uveitis risk | RENDERED: Azithromycin has no significant interaction with rifamycins. Coadministration of clarithromycin and RFB ... can increase RFB to toxic levels increasing the risk of uveitis. | idsa-2016 | 10 | p10/narrative/rifamycin-macrolide | narrative |
| rifamycin-other-antiinfective-action | rifamycin-co-medication | consider alternatives to doxycycline, atovaquone, chloramphenicol, or mefloquine | RENDERED: May require use of a drug other than doxycycline ... Consider alternate form of Pneumocystis jirovecii treatment or prophylaxis ... Consider an alternative antibiotic ... Consider alternate form of malaria prophylaxis. | idsa-2016 | 10 | p10/narrative/rifamycin-other-antiinfective | narrative |
| rifamycin-tamoxifen-action | rifamycin-co-medication | consider alternate therapy or a non-rifamycin regimen | RENDERED: May require alternate therapy or use of a non-rifamycin-containing regimen. | idsa-2016 | 10 | p10/narrative/rifamycin-tamoxifen | narrative |
| rifamycin-cardiovascular-action | rifamycin-co-medication | monitor clinically or by TDM and increase dose or change cardiovascular agent as needed | RENDERED: Clinical monitoring recommended; may require change to an alternate cardiovascular agent ... TDM recommended; may require digoxin or digitoxin dose increase. | idsa-2016 | 10 | p10/narrative/rifamycin-cardiovascular | narrative |
| rifamycin-theophylline-action | rifamycin-co-medication | TDM; theophylline dose may need increase | RENDERED: TDM recommended; may require theophylline dose increase. | idsa-2016 | 10 | p10/narrative/rifamycin-theophylline | narrative |
| rifamycin-hypolipidemic-action | rifamycin-co-medication | monitor lipid-lowering effect; alternative drug may be needed | RENDERED: Monitor hypolipidemic effect; may require use of an alternate antihyperlipidemic drug. | idsa-2016 | 10 | p10/narrative/rifamycin-hypolipidemic | narrative |
| rifamycin-psychotropic-action | rifamycin-co-medication | TDM or clinical monitoring; dose increase or alternative psychotropic may be needed | RENDERED: TDM recommended; may require dose increase or change to alternate psychotropic drug ... Monitor clinically; may require a dose increase or use of an alternate psychotropic drug. | idsa-2016 | 11 | p11/narrative/rifamycin-psychotropic | narrative |
| lopinavir-ritonavir-rifampin-dose | rifampin-lopinavir | increase from 400/100 mg twice daily to 800/200 mg twice daily over 2 weeks, or super-boost with lopinavir 400 mg plus ritonavir 400 mg twice daily | RENDERED: dose of lopinavir/ritonavir is gradually increased from 400 mg/100 mg twice daily to 800 mg/200 mg twice daily over 2 weeks ... super-boosted lopinavir is given as lopinavir 400 mg plus ritonavir 400 mg twice daily | idsa-2016 | 29 | p29/narrative/lopinavir-rifampin | narrative |
| rifabutin-boosted-pi-alternative-dose | rifabutin-boosted-pi | rifabutin 150 mg daily or 300 mg every other day | RENDERED: rifabutin 150 mg daily or 300 mg every other day is recommended | idsa-2016 | 28 | p28/narrative/rifabutin-boosted-pi | narrative |
| rifabutin-efavirenz-dose | rifabutin-efavirenz | rifabutin 600 mg daily with efavirenz | RENDERED: Efavirenz and RFB use requires dose increase of RFB to 600 mg daily | idsa-2016 | 10 | p10/narrative/rifabutin-efavirenz | narrative |
| iris-prednisone-dose | tb-iris | 1.25 mg/kg/day, usually 50-80 mg/day, for 2-4 weeks, then taper over 6-12 weeks or longer | RENDERED: prednisone ... 1.25 mg/kg/day (50-80 mg/day) for 2-4 weeks, with tapering over a period of 6-12 weeks or longer | idsa-2016 | 29 | p29/narrative/iris-prednisone | narrative |
| meningitis-regimen-duration | tb-meningitis | 2 months INH/RIF/PZA/EMB, then INH/RIF for 7-10 months | RENDERED: initiated with INH, RIF, PZA, and EMB in an initial 2-month phase ... INH and RIF continued for an additional 7-10 months | idsa-2016 | 32 | p32/narrative/meningitis-regimen | narrative |
| meningitis-steroid-duration | tb-meningitis | dexamethasone or prednisolone tapered over 6-8 weeks | RENDERED: adjunctive corticosteroid therapy with dexamethasone or prednisolone tapered over 6-8 weeks | idsa-2016 | 31 | p31/grade-spelled-out/2 | recommendation |
| culture-negative-regimen-duration | culture-negative-adult | 4 months total: 2 months INH/RIF/PZA/EMB plus 2 months INH/RIF | RENDERED: after 2 months of intensive phase therapy, the continuation phase with INH and RIF can be shortened to 2 months, for a 4-month treatment regimen | idsa-2016 | 33 | p33/grade-spelled-out/1 | recommendation |
| pediatric-standard-regimen | pediatric-tb | 2 months INH/RIF/PZA/EMB plus 4 months INH/RIF | RENDERED: preferred regimen for treating tuberculosis in children remains a 2-month, 4-drug initial regimen of INH, RIF, PZA, and EMB followed by a 4-month continuation phase of INH and RIF | idsa-2016 | 30 | p30/narrative/pediatric-regimen | narrative |
| pediatric-sputum-sampling | pediatric-tb | 3 early-morning gastric aspirations | RENDERED: collection of 3 early morning gastric aspirations | idsa-2016 | 30 | p30/narrative/pediatric-sampling | narrative |
| pediatric-treatment-frequency | pediatric-tb | daily preferred; continuation twice or thrice weekly may be considered for HIV-uninfected children with DOT | RENDERED: Daily therapy is preferred ... intermittent treatment in the continuation phase ... may be considered for HIV-uninfected children, and DOT should be used | idsa-2016 | 30 | p30/narrative/pediatric-frequency | narrative |
| pediatric-radiograph-resolution | pediatric-tb | may take 1-2 years; do not extend treatment solely for persistent radiographic abnormality when clinically improving | RENDERED: radiographic findings can require 1-2 years to resolve ... treatment is not extended for persistent radiographic findings if the child is asymptomatic and showing clinical improvement. | idsa-2016 | 30 | p30/narrative/pediatric-radiograph | narrative |
| pediatric-ethambutol-vision-monitoring | pediatric-tb | monthly visual acuity and red-green color discrimination when age appropriate | RENDERED: monthly monitoring of visual acuity and red-green color discrimination should be performed when children are treated with EMB and are old enough to cooperate | idsa-2016 | 30 | p30/narrative/pediatric-emb-monitoring | narrative |
| pediatric-pyridoxine-dose | pediatric-pyridoxine-risk | 25-50 mg/day | RENDERED: Pyridoxine, 25-50 mg/day, is given to children with malnutrition, HIV infection, or breastfeeding | idsa-2016 | 30 | p30/narrative/pediatric-pyridoxine | narrative |
| pediatric-meningitis-regimen | pediatric-meningitis | 2 months INH/RIF/PZA plus ethionamide or aminoglycoside, then 7-10 months INH/RIF | RENDERED: initial 4-drug regimen of INH, RIF, PZA, and ethionamide or an aminoglycoside for 2 months ... followed by 7-10 months of INH and RIF | idsa-2016 | 32 | p32/narrative/pediatric-meningitis | narrative |
| pregnancy-no-pza-duration | pregnant-tb | minimum 9 months INH/RIF/EMB | RENDERED: If a decision is made to exclude PZA from the regimen, a minimum of 9 months of INH, RIF, and EMB is used | idsa-2016 | 34 | p34/narrative/pregnancy-no-pza | narrative |
| pregnancy-treatment-initiation | pregnant-tb | initiate when probability of maternal disease is moderate to high | RENDERED: Treatment for tuberculosis is initiated whenever the probability of maternal disease is moderate to high | idsa-2016 | 34 | p34/narrative/pregnancy-initiation | narrative |
| pregnancy-pza-decision | pregnant-tb | evaluate PZA benefits and risks case by case with informed patient decision | RENDERED: evaluate the risks and benefits of prescribing PZA on a case-by-case basis, allowing the patient to make an informed and educated decision | idsa-2016 | 34 | p34/narrative/pregnancy-pza-decision | narrative |
| pregnancy-pza-severe-disease | pregnant-severe-tb | expert opinion favors including PZA | RENDERED: in pregnant women with tuberculosis and HIV, extrapulmonary or severe tuberculosis, it is more beneficial to include PZA | idsa-2016 | 34 | p34/narrative/pregnancy-pza-severe | narrative |
| breastfeeding-first-line-action | breastfeeding-first-line | breastfeeding encouraged | RENDERED: Breastfeeding is encouraged for women who are deemed noninfectious and are being treated with first-line agents. | idsa-2016 | 34 | p34/narrative/breastfeeding | narrative |
| pregnancy-pyridoxine-dose | pregnant-or-nursing-inh | 25-50 mg/day | RENDERED: supplementary pyridoxine, 25-50 mg/day, is prescribed | idsa-2016 | 34 | p34/narrative/maternal-pyridoxine | narrative |
| infant-pyridoxine-dose | exclusively-breastfed-infants | 1-2 mg/kg/day | RENDERED: supplementary pyridoxine (1-2 mg/kg/day) is also prescribed to exclusively breastfed infants | idsa-2016 | 34 | p34/narrative/infant-pyridoxine | narrative |
| renal-isoniazid-dose | renal-under-30 | 300 mg daily or 900 mg 3 times/week | RENDERED: Isoniazid ... 300 mg once daily, or 900 mg 3 times/wk | idsa-2016 | 35 | p35/narrative/isoniazid | narrative |
| renal-rifampin-dose | renal-under-30 | 600 mg daily or 600 mg 3 times/week | RENDERED: Rifampin ... 600 mg once daily, or 600 mg 3 times/wk | idsa-2016 | 35 | p35/narrative/rifampin | narrative |
| renal-pyrazinamide-dose | renal-under-30 | 25-35 mg/kg 3 times/week, not daily | RENDERED: Pyrazinamide ... 25-35 mg/kg/dose 3 times/wk (not daily) | idsa-2016 | 35 | p35/narrative/pyrazinamide | narrative |
| renal-ethambutol-dose | renal-under-30 | 20-25 mg/kg 3 times/week, not daily | RENDERED: Ethambutol ... 20-25 mg/kg/dose 3 times/wk (not daily) | idsa-2016 | 35 | p35/narrative/ethambutol | narrative |
| renal-levofloxacin-dose | renal-under-30 | 750-1000 mg 3 times/week, not daily | RENDERED: Levofloxacin ... 750-1000 mg/dose 3 times/wk (not daily) | idsa-2016 | 35 | p35/narrative/levofloxacin | narrative |
| renal-moxifloxacin-dose | renal-under-30 | 400 mg daily | RENDERED: Moxifloxacin ... 400 mg once daily | idsa-2016 | 35 | p35/narrative/moxifloxacin | narrative |
| renal-cycloserine-dose | renal-under-30 | 250 mg daily or 500 mg 3 times/week; 250 mg daily appropriateness not established | RENDERED: Cycloserine ... 250 mg once daily, or 500 mg/dose 3 times/wk ... appropriateness of 250-mg daily doses has not been established. | idsa-2016 | 35 | p35/narrative/cycloserine | narrative |
| renal-ethionamide-dose | renal-under-30 | 250-500 mg daily | RENDERED: Ethionamide ... 250-500 mg/dose daily | idsa-2016 | 35 | p35/narrative/ethionamide | narrative |
| renal-pas-dose | renal-under-30 | 4 g twice daily | RENDERED: Para-amino salicylic acid ... 4 g/dose twice daily | idsa-2016 | 35 | p35/narrative/pas | narrative |
| renal-injectable-dose | renal-under-30 | streptomycin, capreomycin, kanamycin, or amikacin 15 mg/kg 2-3 times/week, not daily | RENDERED: 15 mg/kg/dose 2-3 times/wk (not daily) | idsa-2016 | 35 | p35/narrative/injectables | narrative |
| hemodialysis-administration | hemodialysis-tb | give medications after hemodialysis on dialysis day | RENDERED: The medications should be given after hemodialysis on the day of hemodialysis. | idsa-2016 | 35 | p35/narrative/hemodialysis-administration | narrative |
| renal-tdm-timing | renal-30-to-50 | serum concentrations 2 and 6 hours after dosing | RENDERED: measurement of serum concentrations 2 and 6 hours after timed administration | idsa-2016 | 35 | p35/narrative/renal-tdm | narrative |
| liver-no-pza-regimen | advanced-liver-disease | INH/RIF/EMB 2 months, then INH/RIF 7 months | RENDERED: INH, RIF, and EMB for 2 months, followed by 7 months of INH and RIF | idsa-2016 | 35 | p35/narrative/liver-no-pza | narrative |
| liver-no-inh-pza-regimen | advanced-liver-disease | RIF/EMB plus fluoroquinolone, injectable, or cycloserine for 12-18 months | RENDERED: RIF and EMB with a fluoroquinolone, injectable, or cycloserine for 12-18 months | idsa-2016 | 35 | p35/narrative/liver-no-inh-pza | narrative |
| liver-no-inh-regimen | advanced-liver-disease | RIF/PZA/EMB with or without fluoroquinolone for at least 6 months | RENDERED: a regimen of RIF, PZA, and EMB with or without a fluoroquinolone ... for a total duration of at least 6 months | idsa-2016 | 35 | p35/narrative/liver-no-inh | narrative |
| liver-nonhepatotoxic-regimen | severe-unstable-liver | EMB plus fluoroquinolone, cycloserine, and injectable for 18-24 months | RENDERED: EMB combined with a fluoroquinolone, cycloserine, and second-line injectable for 18-24 months | idsa-2016 | 35 | p35/narrative/liver-nonhepatotoxic | narrative |
| hepatic-monitoring-frequency | advanced-liver-disease | aminotransferases and bilirubin every 1-4 weeks for first 2-3 months | RENDERED: measuring serum aminotransferases and total bilirubin concentrations every 1-4 weeks for at least the first 2-3 months | idsa-2016 | 36 | p36/narrative/hepatic-monitoring | narrative |
| advanced-liver-alt-interruption | advanced-liver-disease | some experts interrupt at 3-fold ALT elevation even without symptoms, with weekly or twice-weekly ALT monitoring | RENDERED: weekly or twice-weekly ALT monitoring, interrupting treatment for only a 3-fold elevation of ALT, even if asymptomatic | idsa-2016 | 36 | p36/narrative/advanced-liver-alt | narrative |
| older-adult-no-pza-duration | older-than-75 | at least 9 months total if PZA omitted | RENDERED: some experts avoid the use of PZA ... among patients >75 years of age ... total duration ... extended to at least 9 months | idsa-2016 | 36 | p36/narrative/older-adult | narrative |
| extrapulmonary-regimen-duration | extrapulmonary-tb | 6-9 months; meningitis generally 12 months | RENDERED: 6-9 month INH and RIF-containing regimens are effective for the majority ... exception is tuberculous meningitis ... prescribe 12 months | idsa-2016 | 31 | p31/narrative/extrapulmonary-duration | narrative |
| lymph-node-tb-duration | extrapulmonary-tb | 6 months | RENDERED: a 6-month regimen is adequate for initial treatment of all patients with drug-susceptible tuberculous lymphadenitis | idsa-2016 | 31 | p31/narrative/lymph-node-duration | narrative |
| pleural-tb-duration | extrapulmonary-tb | 6 months | RENDERED: A standard 6-month regimen ... is also adequate for treating pleural tuberculosis. | idsa-2016 | 31 | p31/narrative/pleural-duration | narrative |
| disseminated-tb-duration | extrapulmonary-tb | daily 6-month regimen | RENDERED: a standard daily 6-month regimen ... is adequate for tuberculosis at multiple sites and for miliary tuberculosis | idsa-2016 | 32 | p32/narrative/disseminated-duration | narrative |
| genitourinary-tb-duration | extrapulmonary-tb | daily 6-month regimen | RENDERED: a standard daily 6-month regimen ... is adequate | idsa-2016 | 32 | p32/narrative/genitourinary-duration | narrative |
| abdominal-tb-duration | extrapulmonary-tb | 6 months | RENDERED: a 6-month regimen is adequate for patients with peritoneal or intestinal tuberculosis | idsa-2016 | 33 | p33/narrative/abdominal-duration | narrative |
| bone-joint-spine-duration | bone-joint-spine-tb | Six to 9 months; some experts favor 9 months or 12 months with extensive hardware | RENDERED: Six- to 9-month regimens ... some experts tend to favor the 9-month duration ... extensive orthopedic hardware ... 12 months | idsa-2016 | 31 | p31/narrative/bone-joint-spine | narrative |
| pericardial-steroid-use | pericardial-tb | do not routinely use | RENDERED: adjunctive corticosteroids should not be used routinely | idsa-2016 | 31 | p31/grade-spelled-out/1 | recommendation |
| treatment-failure-definition | failure-tb | positive cultures after 4 months; Europe/WHO use 5 months | RENDERED: treatment failure is defined as continuously or recurrently positive cultures after 4 months (5 months in Europe and WHO guidelines) | idsa-2016 | 37 | p37/narrative/failure-definition | narrative |
| delayed-response-evaluation | drug-susceptible-pulmonary-tb | evaluate persistent positive cultures after 3 months | RENDERED: patients with persistently positive cultures after 3 months of chemotherapy ... are evaluated carefully | idsa-2016 | 37 | p37/narrative/delayed-response | narrative |
| poorly-controlled-diabetes-duration | poorly-controlled-diabetes-tb | some experts extend total treatment to 9 months | RENDERED: extending the total duration of tuberculosis treatment to 9 months in poorly controlled diabetes mellitus | idsa-2016 | 36 | p36/narrative/diabetes-duration | narrative |
| silicotuberculosis-duration | silicotuberculosis | extend continuation phase by at least 2 months | RENDERED: continuation phase is extended by at least 2 months | idsa-2016 | 36 | p36/narrative/silicotuberculosis-duration | narrative |
| transplant-duration | solid-organ-transplant-tb | some experts use at least 9 months total | RENDERED: extending the total duration of tuberculosis treatment to at least 9 months for all solid organ transplant recipients | idsa-2016 | 36 | p36/narrative/transplant-duration | narrative |
| immunocompromised-regimen | immunocompromising-comorbidity | standard daily 6-month regimen, individualized by severity, site, and response | RENDERED: tuberculosis treatment for patients with diseases or conditions that alter immune responsiveness ... is based on the standard, daily 6-month regimen | idsa-2016 | 36 | p36/narrative/immunocompromised-regimen | narrative |
| transplant-drug-monitoring | solid-organ-transplant-tb | strict calcineurin-inhibitor or rapamycin serum-concentration monitoring with rifamycin treatment | RENDERED: strict monitoring of serum drug concentrations is needed to prevent rejection | idsa-2016 | 36 | p36/narrative/transplant-drug-monitoring | narrative |
| tnf-inhibitor-resumption | tnf-inhibitor-tb | hold when feasible; case-series support resumption after at least 2 months with good response | RENDERED: safe to resume TNF-alpha inhibitor therapy in patients who complete at least 2 months of antituberculosis treatment and have a good clinical response | idsa-2016 | 36 | p36/narrative/tnf-resumption | narrative |
| relapse-retreatment | relapse-after-dot | standard intensive-phase regimen until susceptibility results | RENDERED: retreatment using the standard intensive phase regimen until the results of susceptibility tests are known | idsa-2016 | 37 | p37/narrative/relapse-retreatment | narrative |
| failure-specialist-action | failure-tb | immediate specialist referral; test recent isolate for first- and second-line susceptibility | RENDERED: Recent mycobacterial isolates should be sent to a reference laboratory for susceptibility testing to both first-and second-line drugs ... immediate referral to, or consultation with a specialty center is indicated. | idsa-2016 | 38 | p38/narrative/failure-referral | narrative |
| failure-empiric-regimen | severe-treatment-failure | start empiric retreatment immediately and continue until susceptibility results | RENDERED: If treatment failure is presumably due to drug resistance and the patient is seriously ill or has a positive sputum AFB smear, an empiric regimen is started immediately and continued until susceptibility tests are available | idsa-2016 | 38 | p38/narrative/failure-empiric | narrative |
| expanded-relapse-regimen | severe-treatment-failure | daily INH/RIF/PZA/EMB plus later-generation fluoroquinolone, injectable, and sometimes another second-line drug, all by DOT | RENDERED: daily INH, RIF, PZA, and EMB, plus a later-generation fluoroquinolone, an injectable, and depending on the severity ... an additional second-line drug ... All drugs are administered using DOT. | idsa-2016 | 37 | p37/narrative/expanded-relapse-regimen | narrative |
| failing-regimen-additions | severe-treatment-failure | never add a single new drug; generally add 2-3 new drugs with inferred susceptibility | RENDERED: A single new drug is never to be added to a failing regimen ... prudent to add 2-3 new drugs to which susceptibility could logically be inferred | idsa-2016 | 38 | p38/narrative/failing-regimen-additions | narrative |

## Conflicts

CONFLICT: once-weekly-continuation-policy uses `do not generally use INH 900 mg plus rifapentine 600 mg once weekly` for the guideline's general recommendation and `INH 900 mg plus rifapentine 600 mg once weekly may be considered only when more frequent DOT is difficult to achieve` for its uncommon exception in the same HIV-uninfected low-relapse-risk population.

The first value preserves the recommendation against routine once-weekly treatment;
the second preserves its narrowly stated feasibility exception.

CONFLICT: efavirenz-rifampin-dose uses `experts advise efavirenz 600 mg daily` and `FDA recommends efavirenz 800 mg daily` for patients >60 kg receiving rifampin with efavirenz.

The source expressly contrasts expert practice with the FDA recommendation, so neither
dose was normalized away.

CONFLICT: treatment-failure-definition uses positive cultures after 4 months in the United States and positive cultures after 5 months in Europe and WHO guidelines for the same treatment-failure quantity.

The source explicitly juxtaposes the United States definition with the Europe/WHO
definition. The row preserves both values and does not select between jurisdictions.

## Coverage

The bound record contains exactly 28 marker occurrences. Fifteen recommendation
occurrences are cited above. The remaining thirteen occurrences are dispositioned
below, for exact accounting of 28 = 15 cited + 13 scoped.

- `p3/grade-spelled-out/1` - summary occurrence of detailed recommendation cited at p15/grade-spelled-out/1
- `p4/grade-spelled-out/1` - summary occurrence of detailed recommendation cited at p15/grade-spelled-out/2
- `p6/grade-spelled-out/1` - summary occurrence of detailed recommendation cited at p17/grade-spelled-out/1
- `p6/grade-spelled-out/2` - summary occurrence of detailed recommendation cited at p17/grade-spelled-out/2
- `p6/grade-spelled-out/3` - summary occurrence of detailed recommendation cited at p17/grade-spelled-out/3
- `p8/grade-spelled-out/1` - summary occurrence of detailed recommendation cited at p17/grade-spelled-out/4
- `p8/grade-spelled-out/2` - summary occurrence of detailed recommendation cited at p17/grade-spelled-out/5
- `p8/grade-spelled-out/3` - summary occurrence of detailed recommendation cited at p17/grade-spelled-out/6
- `p9/grade-spelled-out/1` - summary occurrence of detailed recommendation cited at p25/grade-spelled-out/1
- `p9/grade-spelled-out/2` - summary occurrence of detailed recommendation cited at p25/grade-spelled-out/2
- `p12/grade-spelled-out/1` - summary occurrence of detailed recommendation cited at p31/grade-spelled-out/1
- `p12/grade-spelled-out/2` - summary occurrence of detailed recommendation cited at p31/grade-spelled-out/2
- `p13/grade-spelled-out/1` - summary occurrence of detailed recommendation cited at p33/grade-spelled-out/1

ADR 0009 dispositions were applied as follows:

- pages 14-19: GRADE methods, trial enrollment criteria, adherence and completion
  effects, confidence intervals, and comparative relapse estimates were treated as
  evidence, while the guideline-adopted DOT, case-management, and dosing actions were retained;
- pages 20-30: historical experimental schedules, pharmacokinetic measurements,
  study sample sizes, and outcome-only interaction evidence were excluded, while
  regimen, microbiology/DST, treatment-return, adverse-effect, monitoring, pediatric,
  ART, rifamycin, and IRIS actions were retained. The source's statements that the
  pediatric levofloxacin dose is unknown and that actual-weight dosing is acceptable
  in obesity are preserved; expert dose practices are not rewritten as imperatives;
- every Table 8 management category on pages 10-11 was accounted as an action:
  ART drug selection/dose changes; antibacterial, antifungal, antiprotozoal, and
  Pneumocystis alternatives; contraception and hormone therapy; thyroid replacement;
  methadone; warfarin; transplant immunosuppressants; corticosteroids; anticonvulsants;
  cardiovascular drugs; theophylline; diabetes and lipid drugs; and psychotropics.
  Shared monitor/increase/switch language is consolidated by drug class rather than
  falsely described as trial-only or omitted from the sweep;
- Table 3's adult and pediatric dose schedules, uncertainty statements, administration
  suggestions, poor-tolerance limits, inadequate-intermittent-data statements, obesity
  alternatives, and proposed serum guidance are retained. TDM sampling applies to
  patients selected for TDM, and divalent-cation separation applies to fluoroquinolone
  recipients, without an unsupported adult-only restriction;
- pages 31-38: uncontrolled outcome comparisons and recurrence epidemiology were
  excluded, while site-specific durations, special-population regimens, monitoring,
  failure definitions, referral, susceptibility testing, and retreatment actions were retained;
- the pediatric moxifloxacin dose is explicitly described as not established; the
  expert 10 mg/kg daily practice and the printed proposed 3-5 µL/mL 2-hour target are
  retained with that uncertainty and the unusual printed unit is not silently corrected;
- pages 39-40 contain research priorities and article information rather than current
  patient-action recommendations and are dated blind/null; pages 41-49 are citation-list
  material and are exempt rather than interpreted as clinical thresholds;
- publication years, reference numbers, journal volumes/pages, trial identifiers,
  author disclosures, and descriptive prevalence statements were not converted into actions.
