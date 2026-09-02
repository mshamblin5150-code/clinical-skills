# Threshold-sheet subject ledger

<!-- schema: threshold-subjects/1 -->

This is the committed evidence ledger for clinical-subject groups authored in
[`coverage.md`](coverage.md)'s `subject` column. Every group with more than one
member has exactly one record below. Membership is not transitive: one catalog
topic may appear in several records, representing overlapping maximal cliques
rather than a connected component.

## SUBJECT: abdominal aortic aneurysm screening
DATE: 2026-09-01
ELECTED: abdominal aortic aneurysm screening
ELECTION: The member-authored key "abdominal aortic aneurysm screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: abdominal aortic aneurysm screening / aortic disease: The aortic-disease sheet substantively covers aneurysm definition, surveillance, and intervention, while the USPSTF sheet covers detection of the abdominal aneurysm subtype; broader management versus screening does not separate the aortic aneurysm subject.

### MEMBERS
- abdominal aortic aneurysm screening
- aortic disease

### EVIDENCE
- abdominal aortic aneurysm screening: Catalog row(s): USPSTF 2019 recommendation-statement, population adult, citation 10.1001/jama.2019.18928. Complete threshold sheet: first retained decision aaa-defining-diameter = >=3.0 cm for asymptomatic-adults; population record asymptomatic-adults.
- aortic disease: Catalog row(s): AHA ACC 2022 guideline, population ?, citation 10.1161/CIR.0000000000001106. Complete threshold sheet: first retained decision aneurysm-definition = >=1.5 times the expected normal diameter for aortic-aneurysm-general; population record aortic-disease-complex.

## SUBJECT: acute ischemic stroke, early management
DATE: 2026-09-01
ELECTED: acute ischemic stroke, early management
ELECTION: The member-authored key "acute ischemic stroke, early management" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: acute ischemic stroke, early management / secondary stroke prevention: Both AHA/ASA sheets concern ischemic stroke in patients, covering acute management and prevention after stroke or TIA; care phase does not create a different stroke subject. acute ischemic stroke, early management / stroke primary prevention: The sheets govern the same stroke outcome before and after onset, with primary prevention versus acute ischemic management as explicit phases; the stroke subject remains substantive in both. secondary stroke prevention / stroke primary prevention: Both AHA/ASA sheets prevent stroke, separated by absence versus presence of prior stroke or TIA; that population distinction does not create a different stroke-prevention subject.

### MEMBERS
- acute ischemic stroke, early management
- secondary stroke prevention
- stroke primary prevention

### EVIDENCE
- acute ischemic stroke, early management: Catalog row(s): AHA ACC 2019 guideline, population adult, citation 10.1161/STR.0000000000000211; AHA ACC 2026 guideline, population pediatric, adult, citation 10.1161/STR.0000000000000513. Complete threshold sheet: first retained decision prehospital-sbp-target = target 130-140 mm Hg: no benefit for suspected-ais; population record suspected-ais.
- secondary stroke prevention: Catalog row(s): AHA ACC 2021 guideline, population ?, citation 10.1161/STR.0000000000000375. Complete threshold sheet: first retained decision diagnostic-evaluation-continued-6 = In patients with cryptogenic stroke, echocardiography with or without contrast is reasonable to evaluate for possible cardiac sources of or transcardiac pathways for cerebral embolism. for cryptogenic; population record stroke-tia.
- stroke primary prevention: Catalog row(s): AHA ACC 2024 guideline, population adult, citation 10.1161/STR.0000000000000475. Complete threshold sheet: first retained decision risk-estimate = every 1-5 years for age-40-79; population record age-40-79.

## SUBJECT: childhood and adolescent immunization schedule
DATE: 2026-09-01
ELECTED: childhood and adolescent immunization schedule
ELECTION: The member-authored key "childhood and adolescent immunization schedule" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: adult immunization schedule / childhood and adolescent immunization schedule: Both CDC schedule sheets govern routine vaccine timing and catch-up by age; adult versus older-child population is the substantive distinction within immunization. adult immunization schedule / childhood immunization schedule: The complete CDC schedule captures address the same routine immunization subject across adult versus young-child age bands. childhood and adolescent immunization schedule / childhood immunization schedule: The two CDC schedule captures govern contiguous pediatric age bands and the same routine vaccine series, so age population does not split the immunization subject.

### MEMBERS
- adult immunization schedule
- childhood and adolescent immunization schedule
- childhood immunization schedule

### EVIDENCE
- adult immunization schedule: Catalog row(s): ACIP ? web-capture, population adult, citation https://www.cdc.gov/vaccines/imz-schedules/adult-easyread.html. Complete threshold sheet: first retained decision schedule-applicability-age = age >=19 years for adults-19-plus; population record adults-19-plus.
- childhood and adolescent immunization schedule: Catalog row(s): ACIP ? web-capture, population pediatric, adolescent, citation https://www.cdc.gov/vaccines/imz-schedules/adolescent-easyread.html. Complete threshold sheet: first retained decision schedule-applicability-age = age 7 through 18 years for children-7-18; population record children-7-18.
- childhood immunization schedule: Catalog row(s): ACIP ? web-capture, population pediatric, citation https://www.cdc.gov/vaccines/imz-schedules/child-easyread.html. Complete threshold sheet: first retained decision young-schedule-applicability = birth through age 6 years for children-birth-through-6; population record children-birth-through-6.

## SUBJECT: anemia in chronic kidney disease
DATE: 2026-09-01
ELECTED: anemia in chronic kidney disease
ELECTION: The member-authored key "anemia in chronic kidney disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: anemia in chronic kidney disease / chronic kidney disease: The anemia sheet substantively defines CKD stages and manages a CKD complication in people with CKD, while the general CKD sheet covers anemia among CKD progression and complications; this is legitimate nested membership.

### MEMBERS
- anemia in chronic kidney disease
- chronic kidney disease

### EVIDENCE
- anemia in chronic kidney disease: Catalog row(s): KDIGO 2026 guideline, population ?, citation 10.1016/j.kint.2025.06.006. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function present for >=3 months for people-ckd; population record adult-men-ckd.
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.

## SUBJECT: antibiotic stewardship program implementation
DATE: 2026-09-01
ELECTED: antibiotic stewardship program implementation
ELECTION: The member-authored key "antibiotic stewardship program implementation" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: antibiotic stewardship program implementation / antimicrobial stewardship leadership: Both complete guidelines substantively concern operation of antimicrobial stewardship programs, including leadership, staffing, preauthorization, audit, and feedback; leader competencies are a focused implementation branch.

### MEMBERS
- antibiotic stewardship program implementation
- antimicrobial stewardship leadership

### EVIDENCE
- antibiotic stewardship program implementation: Catalog row(s): IDSA 2016 guideline, population ?, citation 10.1093/cid/ciw118. Complete threshold sheet: first retained decision preauthorization-approver-availability = provide 24-hour availability for the person giving approval for institutions-using-preauthorization; population record institutions-using-preauthorization.
- antimicrobial stewardship leadership: Catalog row(s): IDSA 2026 guideline, population general, citation 10.1017/ash.2026.10344. Complete threshold sheet: first retained decision preauthorization-first-review-window = implement preauthorization within the first 24 hours of therapy, or after a locally specified number of days based on staffing for asp-leaders; population record asp-leaders.

## SUBJECT: anxiety disorder screening
DATE: 2026-09-01
ELECTED: anxiety disorder screening
ELECTION: The member-authored key "anxiety disorder screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: anxiety disorder screening / anxiety screening: Both complete USPSTF sheets screen asymptomatic people for anxiety disorders and differ principally by adult/perinatal versus pediatric population; neither sheet introduces a different anxiety condition.

### MEMBERS
- anxiety disorder screening
- anxiety screening

### EVIDENCE
- anxiety disorder screening: Catalog row(s): USPSTF 2023 recommendation-statement, population adult, pregnancy, postpartum, citation 10.1001/jama.2023.9301. Complete threshold sheet: first retained decision adult-screening-age = age >=19 and <65 years: screen for asymptomatic-adults-19-to-64; population record asymptomatic-adults-19-to-64.
- anxiety screening: Catalog row(s): USPSTF 2022 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2022.16936. Complete threshold sheet: first retained decision uspstf-screening-age = age 8 to 18 years: screen for asymptomatic-youth; population record asymptomatic-youth.

## SUBJECT: atrial fibrillation
DATE: 2026-09-01
ELECTED: atrial fibrillation
ELECTION: The member-authored key "atrial fibrillation" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: atrial fibrillation / atrial fibrillation screening: The USPSTF sheet screens for atrial fibrillation and the AHA/ACC sheet diagnoses and manages the same rhythm disorder; detection versus management does not split AF.

### MEMBERS
- atrial fibrillation
- atrial fibrillation screening

### EVIDENCE
- atrial fibrillation: Catalog row(s): AHA ACC 2023 guideline, population ?, citation 10.1161/CIR.0000000000001193. Complete threshold sheet: first retained decision intermediate-risk-anticoagulation = annual risk >=1% and <2%, equivalent to CHA2DS2-VASc 1 in men or 2 in women: anticoagulation reasonable for intermediate-stroke-risk; population record adults-af.
- atrial fibrillation screening: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2021.23732. Complete threshold sheet: first retained decision uspstf-screening-applicability-age = age >=50 years: evidence insufficient to recommend for or against screening for asymptomatic-adults-50-or-older; population record asymptomatic-adults-50-or-older.

## SUBJECT: blood cholesterol
DATE: 2026-09-01
ELECTED: blood cholesterol
ELECTION: The member-authored key "blood cholesterol" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: blood cholesterol / cardiovascular disease prevention, statins: The blood-cholesterol guideline substantively makes statin and other lipid-lowering decisions for ASCVD prevention, and the USPSTF statement makes the corresponding primary-prevention statin decision; the shared lipid-management scope is clinical, not lexical.

### MEMBERS
- blood cholesterol
- cardiovascular disease prevention, statins

### EVIDENCE
- blood cholesterol: Catalog row(s): AHA ACC 2018 guideline, population adult, citation 10.1161/CIR.0000000000000625. Complete threshold sheet: first retained decision baseline-lipid-profile-age = age >=20 years: fasting or nonfasting lipid profile for adults-20plus-not-on-lipid-therapy; population record adults-20plus-not-on-lipid-therapy.
- cardiovascular disease prevention, statins: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2022.13044. Complete threshold sheet: first retained decision statin-initiation-age-and-risk = age 40 to 75 years and 10-year CVD risk >=10%: prescribe a statin for adults-40-to-75-with-cvd-risk-factor; population record adults-40-to-75-with-cvd-risk-factor.

## SUBJECT: dyslipidemia
DATE: 2026-09-01
ELECTED: dyslipidemia
ELECTION: The member-authored key "dyslipidemia" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: blood cholesterol / dyslipidemia: Both full guidelines define, detect, and manage abnormal cholesterol, LDL-C, and triglycerides; the newer dyslipidemia wording broadens rather than changes the lipid-disorder subject. blood cholesterol / lipid disorder screening: The complete sheets address detection and clinical interpretation of lipid disorders, with the general adult management sheet and pediatric screening statement differing by population and care phase rather than condition. blood cholesterol / lipid management in chronic kidney disease: The CKD sheet substantively assesses and treats cholesterol and triglyceride disorders with statins and statin-ezetimibe; CKD is an added population and second membership, not a replacement for the lipid subject. dyslipidemia / lipid disorder screening: Both complete sheets address detection and classification of lipid disorders, with comprehensive pediatric/adult dyslipidemia management versus pediatric screening as phase and population differences. dyslipidemia / lipid management in chronic kidney disease: The CKD sheet substantively assesses and treats cholesterol and triglyceride disorders, while CKD adds a nested population and second membership to the general dyslipidemia subject. lipid disorder screening / lipid management in chronic kidney disease: Both sheets substantively assess cholesterol and triglyceride disorders, with pediatric population screening versus CKD-specific assessment and treatment; the CKD sheet legitimately adds a second membership.

### MEMBERS
- blood cholesterol
- dyslipidemia
- lipid disorder screening
- lipid management in chronic kidney disease

### EVIDENCE
- blood cholesterol: Catalog row(s): AHA ACC 2018 guideline, population adult, citation 10.1161/CIR.0000000000000625. Complete threshold sheet: first retained decision baseline-lipid-profile-age = age >=20 years: fasting or nonfasting lipid profile for adults-20plus-not-on-lipid-therapy; population record adults-20plus-not-on-lipid-therapy.
- dyslipidemia: Catalog row(s): AHA ACC 2026 guideline, population pediatric, adult, citation 10.1161/CIR.0000000000001423. Complete threshold sheet: first retained decision screening = begin at age 19 years and repeat at least every 5 years; screen more often with additional ASCVD risk factors for adults-screening; population record adults-screening.
- lipid disorder screening: Catalog row(s): USPSTF 2023 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2023.11330. Complete threshold sheet: first retained decision screening-evidence-conclusion = evidence is insufficient to assess the balance of benefits and harms of screening for lipid disorders for asymptomatic-child-adolescent-through-20; population record asymptomatic-child-adolescent-through-20.
- lipid management in chronic kidney disease: Catalog row(s): KDIGO 2013 guideline, population pediatric, adult, citation 10.1038/kisup.2013.27. Complete threshold sheet: first retained decision adult-baseline-lipid-profile = obtain total cholesterol, LDL cholesterol, HDL cholesterol, and triglycerides at initial evaluation; Grade 1C for adults-new-ckd; population record adults-new-ckd.

## SUBJECT: blood pressure in chronic kidney disease
DATE: 2026-09-01
ELECTED: blood pressure in chronic kidney disease
ELECTION: The member-authored key "blood pressure in chronic kidney disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: blood pressure in chronic kidney disease / chronic kidney disease: The BP-in-CKD sheet substantively defines CKD stages and manages a central CKD progression risk, while the general CKD sheet itself includes BP targets and renin-angiotensin therapy; nested CKD membership is supported by both scopes.

### MEMBERS
- blood pressure in chronic kidney disease
- chronic kidney disease

### EVIDENCE
- blood pressure in chronic kidney disease: Catalog row(s): KDIGO 2021 guideline, population ?, citation 10.1016/j.kint.2020.11.003. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function present for >3 months for people-ckd; population record people-ckd.
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.

## SUBJECT: high blood pressure
DATE: 2026-09-01
ELECTED: high blood pressure
ELECTION: The member-authored key "high blood pressure" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: blood pressure in chronic kidney disease / high blood pressure: Both complete guidelines substantively measure and treat high blood pressure, with the KDIGO sheet narrowing the population to CKD and adding a second CKD membership. blood pressure in chronic kidney disease / high blood pressure screening: The KDIGO sheet and pediatric USPSTF sheet address BP measurement, confirmation, and high-BP thresholds; CKD and age are population branches within the high-blood-pressure subject. blood pressure in chronic kidney disease / hypertension screening: Both sheets substantively cover accurate BP measurement and confirmation of hypertension, with CKD-specific management versus adult population screening as the scope difference. high blood pressure / high blood pressure screening: Both complete sheets address high blood pressure, with pediatric asymptomatic screening versus adult prevention, detection, evaluation, and management as population and phase differences. high blood pressure / hypertension screening: Hypertension and high blood pressure are the same condition in the sheets, and adult screening feeds the general adult management pathway. high blood pressure screening / hypertension screening: Both USPSTF sheets screen asymptomatic people for the same high-blood-pressure/hypertension condition and differ by pediatric versus adult population.

### MEMBERS
- blood pressure in chronic kidney disease
- high blood pressure
- high blood pressure screening
- hypertension screening

### EVIDENCE
- blood pressure in chronic kidney disease: Catalog row(s): KDIGO 2021 guideline, population ?, citation 10.1016/j.kint.2020.11.003. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function present for >3 months for people-ckd; population record people-ckd.
- high blood pressure: Catalog row(s): AHA ACC 2025 guideline, population adult, citation 10.1161/CIR.0000000000001356. Complete threshold sheet: first retained decision initial-combination-agent-count = 2 agents of different classes for adults-htn; population record adults.
- high blood pressure screening: Catalog row(s): USPSTF 2020 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2020.20122. Complete threshold sheet: first retained decision screening-evidence-conclusion = evidence is insufficient to assess the balance of benefits and harms for asymptomatic-age-3-18; population record asymptomatic-age-3-18.
- hypertension screening: Catalog row(s): USPSTF 2021 recommendation-statement, population adult, citation 10.1001/jama.2021.4987. Complete threshold sheet: first retained decision hypertension-screening = age >=18 years: office blood pressure measurement for adults-without-known-hypertension; population record adults-without-known-hypertension.

## SUBJECT: breast cancer risk-reducing medication
DATE: 2026-09-01
ELECTED: breast cancer risk-reducing medication
ELECTION: The member-authored key "breast cancer risk-reducing medication" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: breast cancer risk-reducing medication / breast cancer screening: Both USPSTF sheets govern prevention and early detection of breast cancer in asymptomatic women, with chemoprevention versus screening as care branches of the same cancer subject.

### MEMBERS
- breast cancer risk-reducing medication
- breast cancer screening

### EVIDENCE
- breast cancer risk-reducing medication: Catalog row(s): USPSTF 2019 recommendation-statement, population adult, citation 10.1001/jama.2019.11885. Complete threshold sheet: first retained decision risk-reducing-medication-use = offer tamoxifen, raloxifene, or an aromatase inhibitor for women-increased-risk-low-harm-risk; population record women-increased-risk-low-harm-risk.
- breast cancer screening: Catalog row(s): USPSTF 2024 recommendation-statement, population adult, citation 10.1001/jama.2024.5534. Complete threshold sheet: first retained decision mammography-start-age = age 40 to 74 years: screen for uspstf-average-risk-population; population record uspstf-average-risk-population.

## SUBJECT: cardiovascular disease prevention, aspirin
DATE: 2026-09-01
ELECTED: cardiovascular disease prevention, aspirin
ELECTION: The member-authored key "cardiovascular disease prevention, aspirin" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: cardiovascular disease prevention, aspirin / cardiovascular disease prevention, diet and physical activity counseling: Both USPSTF statements target primary prevention of cardiovascular morbidity and mortality in adults without established CVD; aspirin versus behavioral counseling is an intervention branch within that subject. cardiovascular disease prevention, aspirin / cardiovascular disease prevention, statins: Both sheets use baseline cardiovascular risk to select a preventive medication for adults without established CVD; distinct drugs do not create distinct clinical subjects. cardiovascular disease prevention, aspirin / cardiovascular disease risk assessment, nontraditional risk factors: The risk-assessment sheet and aspirin sheet both substantively operate on primary CVD-risk estimation in asymptomatic adults, with assessment feeding prevention rather than naming an unrelated condition. cardiovascular disease prevention, aspirin / cardiovascular disease risk screening, electrocardiography: Both sheets address primary CVD prevention decisions in asymptomatic adults stratified by cardiovascular risk; ECG screening versus aspirin is a screening/intervention distinction within the same prevention subject. cardiovascular disease prevention, diet and physical activity counseling / cardiovascular disease prevention, statins: Both sheets target primary prevention of cardiovascular events in adults and select intervention intensity using risk status; behavioral counseling versus statins is not a different disease subject. cardiovascular disease prevention, diet and physical activity counseling / cardiovascular disease risk assessment, nontraditional risk factors: Risk assessment and lifestyle counseling are substantive steps in primary CVD prevention for asymptomatic adults; differing tools and actions do not split the cardiovascular-prevention subject. cardiovascular disease prevention, diet and physical activity counseling / cardiovascular disease risk screening, electrocardiography: Both USPSTF statements address primary CVD prevention in adults without established disease, one counseling on behavior and the other assessing ECG screening; the outcome subject is shared. cardiovascular disease prevention, statins / cardiovascular disease risk assessment, nontraditional risk factors: The statin statement and nontraditional-risk statement both substantively use primary CVD-risk estimation to guide prevention in asymptomatic adults; assessment versus therapy is a care-phase distinction. cardiovascular disease prevention, statins / cardiovascular disease risk screening, electrocardiography: Both sheets address cardiovascular-risk evaluation and primary prevention in adults without known CVD, using ECG screening versus statin treatment as distinct actions within the same subject. cardiovascular disease risk assessment, nontraditional risk factors / cardiovascular disease risk screening, electrocardiography: The two complete USPSTF statements evaluate additional methods for cardiovascular-risk assessment in asymptomatic adults and use the same primary-prevention risk strata; the tested modality is the substantive difference.

### MEMBERS
- cardiovascular disease prevention, aspirin
- cardiovascular disease prevention, diet and physical activity counseling
- cardiovascular disease prevention, statins
- cardiovascular disease risk assessment, nontraditional risk factors
- cardiovascular disease risk screening, electrocardiography

### EVIDENCE
- cardiovascular disease prevention, aspirin: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2022.4983. Complete threshold sheet: first retained decision aspirin-initiation-age-and-risk = age 40 to 59 years and 10-year CVD risk >=10%: individual decision for primary-prevention-adults; population record primary-prevention-adults.
- cardiovascular disease prevention, diet and physical activity counseling: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2022.10951; USPSTF 2020 recommendation-statement, population adult, citation 10.1001/jama.2020.21749. Complete threshold sheet: first retained decision counseling-offer = individualize the decision to offer or refer for adults-no-known-cvd-risk-factors; population record adults-no-known-cvd-risk-factors.
- cardiovascular disease prevention, statins: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2022.13044. Complete threshold sheet: first retained decision statin-initiation-age-and-risk = age 40 to 75 years and 10-year CVD risk >=10%: prescribe a statin for adults-40-to-75-with-cvd-risk-factor; population record adults-40-to-75-with-cvd-risk-factor.
- cardiovascular disease risk assessment, nontraditional risk factors: Catalog row(s): USPSTF 2018 recommendation-statement, population adult, citation 10.1001/jama.2018.8359. Complete threshold sheet: first retained decision framingham-risk-band = <10% low; 10% to 20% intermediate; >20% high for asymptomatic-adults; population record asymptomatic-adults.
- cardiovascular disease risk screening, electrocardiography: Catalog row(s): USPSTF 2018 recommendation-statement, population adult, citation 10.1001/jama.2018.6848. Complete threshold sheet: first retained decision framingham-risk-band = <10% low; 10% to 20% intermediate; >20% high for asymptomatic-adults; population record asymptomatic-adults.

## SUBJECT: vitamin and mineral supplementation for cardiovascular disease and cancer prevention
DATE: 2026-09-01
ELECTED: vitamin and mineral supplementation for cardiovascular disease and cancer prevention
ELECTION: The member-authored key "vitamin and mineral supplementation for cardiovascular disease and cancer prevention" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: cardiovascular disease prevention, statins / vitamin and mineral supplementation for cardiovascular disease and cancer prevention: The supplementation sheet substantively evaluates prevention of cardiovascular disease in adults, while also carrying cancer as a second subject; statins versus supplements are preventive interventions under the shared CVD-prevention scope.

### MEMBERS
- cardiovascular disease prevention, statins
- vitamin and mineral supplementation for cardiovascular disease and cancer prevention

### EVIDENCE
- cardiovascular disease prevention, statins: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2022.13044. Complete threshold sheet: first retained decision statin-initiation-age-and-risk = age 40 to 75 years and 10-year CVD risk >=10%: prescribe a statin for adults-40-to-75-with-cvd-risk-factor; population record adults-40-to-75-with-cvd-risk-factor.
- vitamin and mineral supplementation for cardiovascular disease and cancer prevention: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2022.8970. Complete threshold sheet: first retained decision beta-carotene-vitamin-e-prevention = do not use beta carotene or vitamin E supplements to prevent cardiovascular disease or cancer; Grade D for community-adults-beta-carotene-or-vitamin-e; population record community-dwelling-nonpregnant-adults.

## SUBJECT: chronic hepatitis B
DATE: 2026-09-01
ELECTED: chronic hepatitis B
ELECTION: The member-authored key "chronic hepatitis B" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic hepatitis B / hepatitis B screening: The sheets cover detection and treatment phases of HBV infection, including screening markers that establish the population entering chronic-HBV management; screening versus established infection does not separate HBV.

### MEMBERS
- chronic hepatitis B
- hepatitis B screening

### EVIDENCE
- chronic hepatitis B: Catalog row(s): IDSA 2026 guideline, population ?, citation 10.1097/HEP.0000000000001549. Complete threshold sheet: first retained decision chb-phase = HBeAg positive, HBV DNA >=10,000,000 IU/mL, ALT <25 U/L women or <35 U/L men for immune-tolerant; population record hbsag-positive.
- hepatitis B screening: Catalog row(s): USPSTF 2019 recommendation-statement, population pregnancy, citation 10.1001/jama.2019.9365; USPSTF 2020 recommendation-statement, population adolescent, adult, citation 10.1001/jama.2020.22980. Complete threshold sheet: first retained decision hbv-screening = first prenatal visit for pregnant-persons; population record pregnant-persons.

## SUBJECT: chronic kidney disease
DATE: 2026-09-01
ELECTED: chronic kidney disease
ELECTION: The member-authored key "chronic kidney disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic kidney disease / chronic kidney disease in HIV infection: The HIV-specific guideline substantively defines, detects, stages, and manages CKD and its progression, making HIV an added population and second subject rather than reducing CKD to a passing mention.

### MEMBERS
- chronic kidney disease
- chronic kidney disease in HIV infection

### EVIDENCE
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.
- chronic kidney disease in HIV infection: Catalog row(s): IDSA 2014 guideline, population pediatric, adult, citation 10.1093/cid/ciu617. Complete threshold sheet: first retained decision ckd-duration = >3 months for hiv-adults-children-us; population record hiv-adults-children-us.

## SUBJECT: chronic kidney disease-mineral and bone disorder
DATE: 2026-09-01
ELECTED: chronic kidney disease-mineral and bone disorder
ELECTION: The member-authored key "chronic kidney disease-mineral and bone disorder" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic kidney disease / chronic kidney disease-mineral and bone disorder: CKD-MBD is a substantive complication of CKD stratified by CKD stages, and the general CKD sheet covers evaluation and complications; the narrower sheet legitimately belongs to the CKD subject as well as MBD.

### MEMBERS
- chronic kidney disease
- chronic kidney disease-mineral and bone disorder

### EVIDENCE
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.
- chronic kidney disease-mineral and bone disorder: Catalog row(s): KDIGO 2017 guideline, population ?, citation 10.1016/j.kisu.2017.04.001. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities present for >3 months for people-ckd; population record people-ckd.

## SUBJECT: diabetes in chronic kidney disease
DATE: 2026-09-01
ELECTED: diabetes in chronic kidney disease
ELECTION: The member-authored key "diabetes in chronic kidney disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic kidney disease / diabetes in chronic kidney disease: The diabetes-in-CKD sheet substantively stages CKD and manages kidney-protective therapy and CKD progression in people with diabetes; it supports both diabetes and CKD memberships.

### MEMBERS
- chronic kidney disease
- diabetes in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.
- diabetes in chronic kidney disease: Catalog row(s): KDIGO 2022 guideline, population ?, citation 10.1016/j.kint.2022.06.008. Complete threshold sheet: first retained decision ckd-definition = ACR >=30 mg/g (>=3 mg/mmol) and/or eGFR <60 mL/min/1.73 m², persistent for >3 months for people-diabetes-ckd; population record people-diabetes-ckd.

## SUBJECT: heart failure in chronic kidney disease
DATE: 2026-09-01
ELECTED: heart failure in chronic kidney disease
ELECTION: The member-authored key "heart failure in chronic kidney disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic kidney disease / heart failure in chronic kidney disease: Although the heart-failure artifact is a declared non-source, its complete scope is expressly for heart failure in people with CKD and future CKD-specific management; the nested CKD subject is substantive in the document form available.

### MEMBERS
- chronic kidney disease
- heart failure in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.
- heart failure in chronic kidney disease: Catalog row(s): KDIGO ? scope-of-work, population ?, citation no catalog citation. Complete threshold sheet: source kdigo-scope (scope-of-work, version ?); the complete source, including the proposed guideline topics, work-group scope, and development plan. The read found no quantity-shaped token that changes what is done to a patient.

## SUBJECT: hepatitis C in chronic kidney disease
DATE: 2026-09-01
ELECTED: hepatitis C in chronic kidney disease
ELECTION: The member-authored key "hepatitis C in chronic kidney disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic kidney disease / hepatitis C in chronic kidney disease: The HCV-in-CKD guideline substantively evaluates CKD stages, dialysis, transplant, and HCV-associated renal disease; it therefore supports CKD membership in addition to HCV.

### MEMBERS
- chronic kidney disease
- hepatitis C in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.
- hepatitis C in chronic kidney disease: Catalog row(s): KDIGO 2022 guideline, population ?, citation 10.1016/j.kint.2022.07.013. Complete threshold sheet: first retained decision initial-hcv-screen = screen for HCV at initial CKD evaluation; use immunoassay followed by NAT when immunoassay is positive for initial-ckd; population record all-ckd.

## SUBJECT: lipid management in chronic kidney disease
DATE: 2026-09-01
ELECTED: lipid management in chronic kidney disease
ELECTION: The member-authored key "lipid management in chronic kidney disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic kidney disease / lipid management in chronic kidney disease: The lipid sheet substantively stratifies assessment and treatment across CKD, dialysis, pediatric, and transplant populations, supporting nested CKD membership as well as dyslipidemia.

### MEMBERS
- chronic kidney disease
- lipid management in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Catalog row(s): KDIGO 2024 guideline, population ?, citation 10.1016/j.kint.2023.10.018. Complete threshold sheet: first retained decision ckd-minimum-duration = abnormalities of kidney structure or function for >=3 months for people-ckd; population record people-ckd.
- lipid management in chronic kidney disease: Catalog row(s): KDIGO 2013 guideline, population pediatric, adult, citation 10.1038/kisup.2013.27. Complete threshold sheet: first retained decision adult-baseline-lipid-profile = obtain total cholesterol, LDL cholesterol, HDL cholesterol, and triglycerides at initial evaluation; Grade 1C for adults-new-ckd; population record adults-new-ckd.

## SUBJECT: chronic kidney disease in HIV infection
DATE: 2026-09-01
ELECTED: chronic kidney disease in HIV infection
ELECTION: The member-authored key "chronic kidney disease in HIV infection" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic kidney disease in HIV infection / HIV preexposure prophylaxis: The CKD guideline substantively manages HIV-infected people and antiretroviral exposure, while PrEP prevents acquisition; CKD adds a nested condition but does not erase the shared HIV clinical subject across prevention and established infection. chronic kidney disease in HIV infection / HIV primary care: Both IDSA sheets provide care for people with HIV, and the primary-care sheet includes renal monitoring while the CKD sheet expands that HIV complication; nested kidney disease supports multi-membership. chronic kidney disease in HIV infection / HIV screening: The sheets address detection and subsequent management of HIV infection, with the CKD sheet adding a substantive renal complication and second membership rather than a different infection. HIV preexposure prophylaxis / HIV primary care: The sheets cover prevention before HIV acquisition and longitudinal care after infection, both substantively organized around HIV risk, testing, antiretroviral use, and prevention; care phase does not split the HIV subject. HIV preexposure prophylaxis / HIV screening: Both USPSTF sheets operate in people without known HIV and substantively link HIV risk assessment, testing, and prevention; PrEP versus screening is an action distinction within HIV prevention. HIV primary care / HIV screening: The USPSTF statement detects HIV infection and the IDSA sheet provides longitudinal primary care after diagnosis; screening and management phases address the same infection.

### MEMBERS
- chronic kidney disease in HIV infection
- HIV preexposure prophylaxis
- HIV primary care
- HIV screening

### EVIDENCE
- chronic kidney disease in HIV infection: Catalog row(s): IDSA 2014 guideline, population pediatric, adult, citation 10.1093/cid/ciu617. Complete threshold sheet: first retained decision ckd-duration = >3 months for hiv-adults-children-us; population record hiv-adults-children-us.
- HIV preexposure prophylaxis: Catalog row(s): USPSTF 2023 recommendation-statement, population adolescent, adult, citation 10.1001/jama.2023.14461. Complete threshold sheet: first retained decision prep-prescribing = prescribe PrEP using effective antiretroviral therapy for increased-risk-no-hiv; population record increased-risk-no-hiv.
- HIV primary care: Catalog row(s): IDSA 2024 guideline, population pediatric, adolescent, adult, pregnancy, citation 10.1093/cid/ciae479. Complete threshold sheet: first retained decision rapid-art = provide patient-centered routine and urgent access and begin Rapid ART at entry when feasible; same day or within 7 days is Rapid ART, except when a clinical reason to delay exists for entering-care; population record all-hiv.
- HIV screening: Catalog row(s): USPSTF 2019 recommendation-statement, population adolescent, adult, pregnancy, citation 10.1001/jama.2019.6587. Complete threshold sheet: first retained decision routine-hiv-screening = age 15 to 65 years: screen for adolescents-adults-15-65; population record adolescents-adults-15-65.

## SUBJECT: chronic obstructive pulmonary disease
DATE: 2026-09-01
ELECTED: chronic obstructive pulmonary disease
ELECTION: The member-authored key "chronic obstructive pulmonary disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic obstructive pulmonary disease / COPD screening: Both complete sheets concern COPD, with USPSTF addressing case finding in asymptomatic adults and GOLD covering diagnosis, management, and prevention; screening versus management is the only subject-level distinction.

### MEMBERS
- chronic obstructive pulmonary disease
- COPD screening

### EVIDENCE
- chronic obstructive pulmonary disease: Catalog row(s): GOLD 2026 guideline, population ?, citation no catalog citation. Complete threshold sheet: first retained decision diagnosis-ratio = post-bronchodilator FEV1/FVC <0.7 for suspected-copd; population record suspected-copd.
- COPD screening: Catalog row(s): USPSTF 2022 recommendation-statement, population adult, citation 10.1001/jama.2022.5692. Complete threshold sheet: first retained decision postbronchodilator-fev1-fvc-ratio = <0.70: confirms persistent airway obstruction and COPD diagnosis for symptomatic-or-exposed-persons; population record symptomatic-or-exposed-persons.

## SUBJECT: chronic pain in HIV infection
DATE: 2026-09-01
ELECTED: chronic pain in HIV infection
ELECTION: The member-authored key "chronic pain in HIV infection" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: chronic pain in HIV infection / HIV preexposure prophylaxis: The pain guideline is substantively care of people living with HIV, and the PrEP statement prevents that same infection; chronic pain adds a second nested subject while prevention versus established infection remains an HIV care-phase distinction. chronic pain in HIV infection / HIV primary care: Both sheets care for people with HIV, with chronic-pain assessment and treatment a focused complication within the broader HIV primary-care subject. chronic pain in HIV infection / HIV screening: HIV screening and downstream care of chronic pain in people with HIV are detection and nested-management phases of the HIV subject; the pain sheet retains a second condition membership. HIV preexposure prophylaxis / HIV primary care: The sheets cover prevention before HIV acquisition and longitudinal care after infection, both substantively organized around HIV risk, testing, antiretroviral use, and prevention; care phase does not split the HIV subject. HIV preexposure prophylaxis / HIV screening: Both USPSTF sheets operate in people without known HIV and substantively link HIV risk assessment, testing, and prevention; PrEP versus screening is an action distinction within HIV prevention. HIV primary care / HIV screening: The USPSTF statement detects HIV infection and the IDSA sheet provides longitudinal primary care after diagnosis; screening and management phases address the same infection.

### MEMBERS
- chronic pain in HIV infection
- HIV preexposure prophylaxis
- HIV primary care
- HIV screening

### EVIDENCE
- chronic pain in HIV infection: Catalog row(s): IDSA 2017 guideline, population ?, citation 10.1093/cid/cix636. Complete threshold sheet: first retained decision chronic-pain-duration = pain lasting longer than 3-6 months for plwh; population record plwh.
- HIV preexposure prophylaxis: Catalog row(s): USPSTF 2023 recommendation-statement, population adolescent, adult, citation 10.1001/jama.2023.14461. Complete threshold sheet: first retained decision prep-prescribing = prescribe PrEP using effective antiretroviral therapy for increased-risk-no-hiv; population record increased-risk-no-hiv.
- HIV primary care: Catalog row(s): IDSA 2024 guideline, population pediatric, adolescent, adult, pregnancy, citation 10.1093/cid/ciae479. Complete threshold sheet: first retained decision rapid-art = provide patient-centered routine and urgent access and begin Rapid ART at entry when feasible; same day or within 7 days is Rapid ART, except when a clinical reason to delay exists for entering-care; population record all-hiv.
- HIV screening: Catalog row(s): USPSTF 2019 recommendation-statement, population adolescent, adult, pregnancy, citation 10.1001/jama.2019.6587. Complete threshold sheet: first retained decision routine-hiv-screening = age 15 to 65 years: screen for adolescents-adults-15-65; population record adolescents-adults-15-65.

## SUBJECT: Clostridioides difficile infection
DATE: 2026-09-01
ELECTED: Clostridioides difficile infection
ELECTION: The member-authored key "Clostridioides difficile infection" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: Clostridioides difficile infection / Clostridium difficile infection: Both IDSA sheets manage the same C. difficile infection; Clostridioides is the renamed genus, while the population and update scope explain the remaining differences.

### MEMBERS
- Clostridioides difficile infection
- Clostridium difficile infection

### EVIDENCE
- Clostridioides difficile infection: Catalog row(s): IDSA 2021 guideline, population adult, citation 10.1093/cid/ciab549. Complete threshold sheet: first retained decision initial-fidaxomicin-regimen = fidaxomicin 200 mg by mouth twice daily for 10 days for adults-initial-cdi; population record adults-initial-cdi.
- Clostridium difficile infection: Catalog row(s): IDSA 2018 guideline, population pediatric, adult, citation 10.1093/cid/cix1085. Complete threshold sheet: first retained decision pediatric-surveillance-age = exclude cases age <2 years for inpatient-pediatric-surveillance; population record inpatient-pediatric-surveillance.

## SUBJECT: community-acquired pneumonia
DATE: 2026-09-01
ELECTED: community-acquired pneumonia
ELECTION: The member-authored key "community-acquired pneumonia" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: community-acquired pneumonia / hospital-acquired and ventilator-associated pneumonia: Both ATS/IDSA sheets diagnose and treat pneumonia in adults; acquisition setting changes pathogen risk, testing, and empiric therapy but remains a clinically substantive subtype distinction within pneumonia.

### MEMBERS
- community-acquired pneumonia
- hospital-acquired and ventilator-associated pneumonia

### EVIDENCE
- community-acquired pneumonia: Catalog row(s): IDSA 2019 guideline, population adult, citation 10.1164/rccm.201908-1581ST. Complete threshold sheet: first retained decision severe-cap-count = one major criterion or three or more minor criteria for adults-cap-severity-assessment; population record adults-cap-severity-assessment.
- hospital-acquired and ventilator-associated pneumonia: Catalog row(s): IDSA 2016 guideline, population adult, citation 10.1093/cid/ciw353. Complete threshold sheet: first retained decision applicability = applies to nonimmunocompromised adults with HAP/VAP; immunosuppressed patients at risk for opportunistic pulmonary infection may require an alternative approach for guideline-adults; population record guideline-adults.

## SUBJECT: COVID-19 infection prevention for healthcare personnel
DATE: 2026-09-01
ELECTED: COVID-19 infection prevention for healthcare personnel
ELECTION: The member-authored key "COVID-19 infection prevention for healthcare personnel" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: COVID-19 infection prevention for healthcare personnel / COVID-19 serologic testing: Both IDSA sheets substantively concern suspected or known COVID-19, with occupational infection-control measures versus serologic diagnosis as prevention and detection branches of the same infection subject. COVID-19 infection prevention for healthcare personnel / COVID-19 treatment: The complete sheets address prevention of SARS-CoV-2 transmission during care and treatment of infected patients; personnel population and action differ, but COVID-19 remains the substantive disease driving both. COVID-19 serologic testing / COVID-19 treatment: Both complete IDSA sheets concern SARS-CoV-2 infection in patients, one delimiting serologic diagnosis and the other treatment by COVID-19 severity; diagnostic versus therapeutic scope does not split the disease.

### MEMBERS
- COVID-19 infection prevention for healthcare personnel
- COVID-19 serologic testing
- COVID-19 treatment

### EVIDENCE
- COVID-19 infection prevention for healthcare personnel: Catalog row(s): IDSA 2021 guideline, population general, citation 10.1093/cid/ciab953. Complete threshold sheet: first retained decision n95-extended-use-limit = CDC maximum extended-use period 8-12 hours for hcp-extended-n95-shortage; population record hcp-extended-n95-shortage.
- COVID-19 serologic testing: Catalog row(s): IDSA 2024 guideline, population ?, citation 10.1093/cid/ciae121. Complete threshold sheet: first retained decision acute-serology-exclusion-window = do not use serologic testing to diagnose SARS-CoV-2 infection during the first 2 weeks after symptom onset for symptomatic-suspected-acute-covid; population record symptomatic-suspected-acute-covid.
- COVID-19 treatment: Catalog row(s): IDSA 2022 guideline, population adult, citation 10.1093/cid/ciac724. Complete threshold sheet: first retained decision covid-severe-oxygen-threshold = severe illness: SpO2 <=94% on room air, including supplemental oxygen for covid-severity; population record hospitalized-critical-covid.

## SUBJECT: dental caries prevention
DATE: 2026-09-01
ELECTED: dental caries prevention
ELECTION: The member-authored key "dental caries prevention" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: dental caries prevention / oral health screening and prevention: The broader oral-health sheets substantively include dental caries screening and preventive interventions, while the younger-child sheet focuses on caries; this is legitimate nested oral-health membership.

### MEMBERS
- dental caries prevention
- oral health screening and prevention

### EVIDENCE
- dental caries prevention: Catalog row(s): USPSTF 2021 recommendation-statement, population pediatric, citation 10.1001/jama.2021.20007. Complete threshold sheet: first retained decision recommendation-applicability-age = <5 years for asymptomatic-children; population record asymptomatic-children.
- oral health screening and prevention: Catalog row(s): USPSTF 2023 recommendation-statement, population adult, citation 10.1001/jama.2023.21409; USPSTF 2023 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2023.21408. Complete threshold sheet: first retained decision primary-care-oral-health-screening = evidence insufficient for asymptomatic-adults; population record asymptomatic-adults.

## SUBJECT: depression and suicide risk screening
DATE: 2026-09-01
ELECTED: depression and suicide risk screening
ELECTION: The member-authored key "depression and suicide risk screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: depression and suicide risk screening / perinatal depression prevention: The screening sheet expressly includes pregnant and postpartum people and depression, while the prevention sheet targets the same perinatal depressive illness before diagnosis; suicide-risk content adds a second scope but does not erase the shared depression subject.

### MEMBERS
- depression and suicide risk screening
- perinatal depression prevention

### EVIDENCE
- depression and suicide risk screening: Catalog row(s): USPSTF 2023 recommendation-statement, population adult, pregnancy, postpartum, citation 10.1001/jama.2023.9297; USPSTF 2022 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2022.16946. Complete threshold sheet: first retained decision depression-screening = screen for adults; population record adults.
- perinatal depression prevention: Catalog row(s): USPSTF 2019 recommendation-statement, population pregnancy, postpartum, citation 10.1001/jama.2019.0007. Complete threshold sheet: first retained decision prevention-recommendation = provide or refer to counseling interventions for increased-risk-pregnant-postpartum-person; population record increased-risk-pregnant-postpartum-person.

## SUBJECT: prediabetes and type 2 diabetes screening
DATE: 2026-09-01
ELECTED: prediabetes and type 2 diabetes screening
ELECTION: The member-authored key "prediabetes and type 2 diabetes screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: diabetes in chronic kidney disease / diabetes mellitus: The KDIGO sheet substantively manages diabetes with glycemic monitoring, targets, lifestyle, and glucose-lowering drugs, adding CKD as a nested population to the general diabetes subject. diabetes in chronic kidney disease / prediabetes and type 2 diabetes screening: Both sheets substantively address type 2 diabetes, with USPSTF case finding and KDIGO management after diabetes and CKD coexist; screening versus nested management supports one diabetes subject. diabetes mellitus / prediabetes and type 2 diabetes screening: The USPSTF sheets detect prediabetes and type 2 diabetes and ADA manages the same diabetes continuum; screening versus comprehensive management and age branches do not split the subject.

### MEMBERS
- diabetes in chronic kidney disease
- diabetes mellitus
- prediabetes and type 2 diabetes screening

### EVIDENCE
- diabetes in chronic kidney disease: Catalog row(s): KDIGO 2022 guideline, population ?, citation 10.1016/j.kint.2022.06.008. Complete threshold sheet: first retained decision ckd-definition = ACR >=30 mg/g (>=3 mg/mmol) and/or eGFR <60 mL/min/1.73 m², persistent for >3 months for people-diabetes-ckd; population record people-diabetes-ckd.
- diabetes mellitus: Catalog row(s): ADA 2026 guideline, population ?, citation no catalog citation. Complete threshold sheet: first retained decision post-pancreatitis-initial-screening-interval = 3-6 months for post-acute-pancreatitis; population record post-acute-pancreatitis.
- prediabetes and type 2 diabetes screening: Catalog row(s): USPSTF 2022 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2022.14543; USPSTF 2021 recommendation-statement, population adult, citation 10.1001/jama.2021.12531. Complete threshold sheet: first retained decision adult-bmi-definitions-overweight-obesity = overweight BMI >=25; obesity BMI >=30 for adults-35-70-overweight-obesity; population record adults-35-70-overweight-obesity.

## SUBJECT: diabetes-related foot infection
DATE: 2026-09-01
ELECTED: diabetes-related foot infection
ELECTION: The member-authored key "diabetes-related foot infection" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: diabetes mellitus / diabetes-related foot infection: The foot-infection guideline substantively addresses a diabetes complication and its management in people with diabetes, while ADA covers foot assessment and complication prevention; the narrow sheet legitimately belongs to both diabetes and infection subjects.

### MEMBERS
- diabetes mellitus
- diabetes-related foot infection

### EVIDENCE
- diabetes mellitus: Catalog row(s): ADA 2026 guideline, population ?, citation no catalog citation. Complete threshold sheet: first retained decision post-pancreatitis-initial-screening-interval = 3-6 months for post-acute-pancreatitis; population record post-acute-pancreatitis.
- diabetes-related foot infection: Catalog row(s): IDSA 2023 guideline, population ?, citation 10.1093/cid/ciad527. Complete threshold sheet: first retained decision dfi-diagnosis = diagnose clinically from local or systemic inflammatory signs and symptoms for person-with-diabetes-foot-infection; population record person-with-diabetes-foot-infection.

## SUBJECT: gestational diabetes screening
DATE: 2026-09-01
ELECTED: gestational diabetes screening
ELECTION: The member-authored key "gestational diabetes screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: diabetes mellitus / gestational diabetes screening: The comprehensive ADA sheet substantively covers diabetes in pregnancy, while USPSTF detects gestational diabetes; pregnancy and screening add a subtype and phase within the broader diabetes subject.

### MEMBERS
- diabetes mellitus
- gestational diabetes screening

### EVIDENCE
- diabetes mellitus: Catalog row(s): ADA 2026 guideline, population ?, citation no catalog citation. Complete threshold sheet: first retained decision post-pancreatitis-initial-screening-interval = 3-6 months for post-acute-pancreatitis; population record post-acute-pancreatitis.
- gestational diabetes screening: Catalog row(s): USPSTF 2021 recommendation-statement, population pregnancy, citation 10.1001/jama.2021.11922. Complete threshold sheet: first retained decision uspstf-screening-timing = screen at >=24 weeks of gestation for asymptomatic-pregnant-24-weeks-or-after; population record asymptomatic-pregnant-24-weeks-or-after.

## SUBJECT: drug-susceptible tuberculosis treatment
DATE: 2026-09-01
ELECTED: drug-susceptible tuberculosis treatment
ELECTION: The member-authored key "drug-susceptible tuberculosis treatment" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: drug-susceptible tuberculosis treatment / tuberculosis diagnosis: The diagnosis guideline substantively establishes active pulmonary and extrapulmonary TB and drug-resistance workup that leads to the drug-susceptible treatment guideline; diagnostic versus therapeutic phase does not split active tuberculosis.

### MEMBERS
- drug-susceptible tuberculosis treatment
- tuberculosis diagnosis

### EVIDENCE
- drug-susceptible tuberculosis treatment: Catalog row(s): IDSA 2016 guideline, population pediatric, adult, citation 10.1093/cid/ciw376. Complete threshold sheet: first retained decision empiric-initial-regimen = INH + RIF + PZA + EMB promptly for presumed-pulmonary-tb; population record presumed-pulmonary-tb.
- tuberculosis diagnosis: Catalog row(s): IDSA 2017 guideline, population pediatric, adult, citation 10.1093/cid/ciw694. Complete threshold sheet: first retained decision ltbi-test-bcg-return = prefer IGRA over TST; TST remains acceptable if IGRA is unavailable, too costly, or too burdensome for ltbi-likely-low-intermediate-bcg-or-no-return; population record ltbi-likely-low-intermediate-bcg-or-no-return.

## SUBJECT: fracture prevention, vitamin D and calcium supplementation
DATE: 2026-09-01
ELECTED: fracture prevention, vitamin D and calcium supplementation
ELECTION: The member-authored key "fracture prevention, vitamin D and calcium supplementation" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: fracture prevention, vitamin D and calcium supplementation / osteoporosis screening, fracture prevention: Both USPSTF sheets center on preventing fragility fractures in community-dwelling adults; supplementation versus osteoporosis screening is a preventive-action distinction within the shared fracture-prevention subject.

### MEMBERS
- fracture prevention, vitamin D and calcium supplementation
- osteoporosis screening, fracture prevention

### EVIDENCE
- fracture prevention, vitamin D and calcium supplementation: Catalog row(s): USPSTF 2018 recommendation-statement, population adult, citation 10.1001/jama.2018.3185. Complete threshold sheet: first retained decision uspstf-vitamin-d-lower-dose = <=400 IU/day: recommend against for community-postmenopausal-women; population record community-postmenopausal-women.
- osteoporosis screening, fracture prevention: Catalog row(s): USPSTF 2025 recommendation-statement, population adult, citation 10.1001/jama.2024.27154. Complete threshold sheet: first retained decision women-65-recommendation = screen for osteoporosis to prevent osteoporotic fractures; Grade B for women-65-or-older; population record eligible-adults-40-or-older.

## SUBJECT: heart failure
DATE: 2026-09-01
ELECTED: heart failure
ELECTION: The member-authored key "heart failure" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: heart failure / heart failure in chronic kidney disease: The CKD artifact is a scope of work rather than a decision source, but its complete text is substantively and expressly about diagnosis and management of heart failure in CKD; CKD creates nested membership without changing the heart-failure subject.

### MEMBERS
- heart failure
- heart failure in chronic kidney disease

### EVIDENCE
- heart failure: Catalog row(s): AHA ACC 2022 guideline, population ?, citation 10.1161/CIR.0000000000001063. Complete threshold sheet: first retained decision hf-ef-classification = HFrEF: LVEF <=40% for hfr-ef; population record all-hf.
- heart failure in chronic kidney disease: Catalog row(s): KDIGO ? scope-of-work, population ?, citation no catalog citation. Complete threshold sheet: source kdigo-scope (scope-of-work, version ?); the complete source, including the proposed guideline topics, work-group scope, and development plan. The read found no quantity-shaped token that changes what is done to a patient.

## SUBJECT: hepatitis C screening
DATE: 2026-09-01
ELECTED: hepatitis C screening
ELECTION: The member-authored key "hepatitis C screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: hepatitis C in chronic kidney disease / hepatitis C screening: The KDIGO sheet includes HCV detection and screening in CKD and dialysis populations, while USPSTF covers population screening generally; CKD is a nested population within the HCV subject. hepatitis C in chronic kidney disease / hepatitis C virus infection: Both sheets substantively diagnose and treat HCV infection; KDIGO adds renal-stage, dialysis, and transplant branches and therefore retains both HCV and CKD memberships. hepatitis C screening / hepatitis C virus infection: The USPSTF sheet detects HCV infection and the AASLD-IDSA sheet tests, stages, and treats that same infection; screening and management phases support one HCV subject.

### MEMBERS
- hepatitis C in chronic kidney disease
- hepatitis C screening
- hepatitis C virus infection

### EVIDENCE
- hepatitis C in chronic kidney disease: Catalog row(s): KDIGO 2022 guideline, population ?, citation 10.1016/j.kint.2022.07.013. Complete threshold sheet: first retained decision initial-hcv-screen = screen for HCV at initial CKD evaluation; use immunoassay followed by NAT when immunoassay is positive for initial-ckd; population record all-ckd.
- hepatitis C screening: Catalog row(s): USPSTF 2020 recommendation-statement, population adult, citation 10.1001/jama.2020.1123. Complete threshold sheet: first retained decision screening-age = screen age 18-79 years for asymptomatic-adults-18-79; population record asymptomatic-adults-18-79.
- hepatitis C virus infection: Catalog row(s): IDSA 2023 guideline, population pediatric, adult, citation 10.1093/cid/ciad319. Complete threshold sheet: first retained decision screening-eligibility = screen all adults age >=18 years for all-adults; population record all-adults.

## SUBJECT: high body mass index intervention
DATE: 2026-09-01
ELECTED: high body mass index intervention
ELECTION: The member-authored key "high body mass index intervention" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: high body mass index intervention / obesity, behavioral weight loss intervention: Both USPSTF sheets prescribe intensive behavioral weight-management interventions for elevated BMI/obesity, separated primarily by pediatric versus adult population wording.

### MEMBERS
- high body mass index intervention
- obesity, behavioral weight loss intervention

### EVIDENCE
- high body mass index intervention: Catalog row(s): USPSTF 2024 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2024.11146. Complete threshold sheet: first retained decision intervention-eligibility = provide or refer at age >=6 years and BMI >=95th percentile for age and sex for age-6plus-high-bmi; population record age-6plus-high-bmi.
- obesity, behavioral weight loss intervention: Catalog row(s): USPSTF 2018 recommendation-statement, population adult, citation 10.1001/jama.2018.13022. Complete threshold sheet: first retained decision obesity-intervention-recommendation = offer or refer to intensive, multicomponent behavioral interventions; Grade B for adults-bmi-30-or-higher; population record adults-bmi-30-or-higher.

## SUBJECT: hypertensive disorders of pregnancy screening
DATE: 2026-09-01
ELECTED: hypertensive disorders of pregnancy screening
ELECTION: The member-authored key "hypertensive disorders of pregnancy screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: hypertensive disorders of pregnancy screening / preeclampsia prevention, low-dose aspirin: Preeclampsia is a substantive hypertensive disorder of pregnancy in the screening sheet, and both statements govern detection or prevention of that pregnancy-specific condition; the broader screening sheet legitimately has nested membership.

### MEMBERS
- hypertensive disorders of pregnancy screening
- preeclampsia prevention, low-dose aspirin

### EVIDENCE
- hypertensive disorders of pregnancy screening: Catalog row(s): USPSTF 2023 recommendation-statement, population pregnancy, citation 10.1001/jama.2023.16991. Complete threshold sheet: first retained decision chronic-hypertension-timing = before pregnancy or within first 20 weeks of gestation for pregnant-without-known-hdp-or-chronic-htn; population record pregnant-without-known-hdp-or-chronic-htn.
- preeclampsia prevention, low-dose aspirin: Catalog row(s): USPSTF 2021 recommendation-statement, population pregnancy, citation 10.1001/jama.2021.14781. Complete threshold sheet: first retained decision preventive-aspirin-regimen = prescribe low-dose aspirin 81 mg once daily after 12 weeks of gestation for asymptomatic-pregnant-high-risk-no-aspirin-boundary; population record asymptomatic-pregnant-high-risk-no-aspirin-boundary.

## SUBJECT: illicit drug use prevention
DATE: 2026-09-01
ELECTED: illicit drug use prevention
ELECTION: The member-authored key "illicit drug use prevention" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: illicit drug use prevention / unhealthy drug use screening: Both USPSTF statements address primary-care prevention or detection of nonmedical drug use, with age and pregnancy branches and a prevention-versus-screening distinction rather than different substances or conditions.

### MEMBERS
- illicit drug use prevention
- unhealthy drug use screening

### EVIDENCE
- illicit drug use prevention: Catalog row(s): USPSTF 2020 recommendation-statement, population pediatric, adolescent, adult, pregnancy, citation 10.1001/jama.2020.6774. Complete threshold sheet: first retained decision prevention-recommendation-age-scope = children <=11 years; adolescents 12 to 17 years; young adults 18 to 25 years; includes pregnant persons for defined-age-population; population record defined-age-population.
- unhealthy drug use screening: Catalog row(s): USPSTF 2020 recommendation-statement, population adolescent, adult, pregnancy, postpartum, citation 10.1001/jama.2020.8020. Complete threshold sheet: first retained decision adult-screening-recommendation = screen by asking questions about unhealthy drug use at age 18 years or older only when accurate diagnosis, effective treatment, and appropriate care can be offered or referred; screening means questions, not biologic specimens; Grade B for adults-primary-care; population record adults-primary-care.

## SUBJECT: iron deficiency anemia screening
DATE: 2026-09-01
ELECTED: iron deficiency anemia screening
ELECTION: The member-authored key "iron deficiency anemia screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: iron deficiency anemia screening / iron deficiency anemia screening and supplementation: Both USPSTF sheets address detection of iron deficiency anemia, with young children versus pregnancy and added maternal iron supplementation as population and intervention branches.

### MEMBERS
- iron deficiency anemia screening
- iron deficiency anemia screening and supplementation

### EVIDENCE
- iron deficiency anemia screening: Catalog row(s): USPSTF 2015 recommendation-statement, population pediatric, citation 10.1542/peds.2015-2567. Complete threshold sheet: first retained decision screening-evidence-conclusion = evidence is insufficient to assess the balance of benefits and harms of screening for iron deficiency anemia for asymptomatic-us-children-6-to-24-months; population record asymptomatic-us-children-6-to-24-months.
- iron deficiency anemia screening and supplementation: Catalog row(s): USPSTF 2024 recommendation-statement, population pregnancy, citation 10.1001/jama.2024.15196. Complete threshold sheet: first retained decision screening-evidence-conclusion = evidence is insufficient to assess the balance of benefits and harms of screening for iron deficiency and iron deficiency anemia to prevent adverse maternal and infant health outcomes for asymptomatic-pregnant-adolescents-adults; population record asymptomatic-pregnant-adolescents-adults.

## SUBJECT: kidney transplant recipient care
DATE: 2026-09-01
ELECTED: kidney transplant recipient care
ELECTION: The member-authored key "kidney transplant recipient care" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: kidney transplant recipient care / kidney transplantation candidate evaluation: The complete KDIGO sheets govern successive pretransplant-candidate and posttransplant-recipient phases for the kidney transplant patient, with substantive continuity in eligibility, risk evaluation, and recipient management.

### MEMBERS
- kidney transplant recipient care
- kidney transplantation candidate evaluation

### EVIDENCE
- kidney transplant recipient care: Catalog row(s): KDIGO 2009 guideline, population transplant, citation 10.1111/j.1600-6143.2009.02834.x. Complete threshold sheet: first retained decision cni-monitoring-frequency = measure CNI levels every other day during the immediate postoperative period until target is reached; remeasure whenever medication or patient status may alter levels or kidney function declines for stable-ktrs; population record kidney-transplant-recipients.
- kidney transplantation candidate evaluation: Catalog row(s): KDIGO 2020 guideline, population transplant, citation 10.1097/TP.0000000000003136. Complete threshold sheet: first retained decision referral-gfr-and-lead-time = CKD G4-G5, GFR <30 mL/min/1.73 m2, expected to reach ESKD: inform, educate, and consider transplantation; refer 6-12 months before anticipated dialysis for advanced-ckd; population record advanced-ckd.

## SUBJECT: latent tuberculosis infection screening
DATE: 2026-09-01
ELECTED: latent tuberculosis infection screening
ELECTION: The member-authored key "latent tuberculosis infection screening" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: latent tuberculosis infection screening / tuberculosis diagnosis: The diagnosis guideline substantively covers TST and IGRA evaluation, interpretation, and exclusion of active disease, while USPSTF covers case finding for latent infection; both share the latent-TB diagnostic subject.

### MEMBERS
- latent tuberculosis infection screening
- tuberculosis diagnosis

### EVIDENCE
- latent tuberculosis infection screening: Catalog row(s): USPSTF 2023 recommendation-statement, population adult, citation 10.1001/jama.2023.4899. Complete threshold sheet: first retained decision screening-recommendation = screen for latent tuberculosis infection for asymptomatic-increased-risk-adult; population record asymptomatic-increased-risk-adult.
- tuberculosis diagnosis: Catalog row(s): IDSA 2017 guideline, population pediatric, adult, citation 10.1093/cid/ciw694. Complete threshold sheet: first retained decision ltbi-test-bcg-return = prefer IGRA over TST; TST remains acceptable if IGRA is unavailable, too costly, or too burdensome for ltbi-likely-low-intermediate-bcg-or-no-return; population record ltbi-likely-low-intermediate-bcg-or-no-return.

## SUBJECT: lower extremity peripheral artery disease
DATE: 2026-09-01
ELECTED: lower extremity peripheral artery disease
ELECTION: The member-authored key "lower extremity peripheral artery disease" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: lower extremity peripheral artery disease / peripheral artery disease screening, ankle-brachial index: Both sheets concern lower-extremity PAD and use the ankle-brachial index for detection or evaluation, with screening versus full disease management as the scope difference.

### MEMBERS
- lower extremity peripheral artery disease
- peripheral artery disease screening, ankle-brachial index

### EVIDENCE
- lower extremity peripheral artery disease: Catalog row(s): AHA ACC 2024 guideline, population ?, citation 10.1161/CIR.0000000000001251. Complete threshold sheet: first retained decision history-and-physical-examination-to-assess-1 = In patients at increased risk of PAD (Table 5), a comprehensive medical history and review of symptoms to assess for exertional leg symptoms, lower extremity rest pain, and lower extremity wounds or other ischemic skin changes should be performed. for patients-at-increased-risk-of-pad-table-5; population record patients-at-increased-risk-of-pad-table-5.
- peripheral artery disease screening, ankle-brachial index: Catalog row(s): USPSTF 2018 recommendation-statement, population adult, citation 10.1001/jama.2018.8357. Complete threshold sheet: first retained decision screening-evidence-conclusion = evidence is insufficient to assess the balance of benefits and harms of screening for PAD and CVD risk with ABI for asymptomatic-adults-no-pad-cvd-severe-ckd; population record asymptomatic-adults-no-pad-cvd-severe-ckd.

## SUBJECT: skin cancer prevention counseling
DATE: 2026-09-01
ELECTED: skin cancer prevention counseling
ELECTION: The member-authored key "skin cancer prevention counseling" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: skin cancer prevention counseling / skin cancer screening: Both USPSTF sheets address prevention or early detection of skin cancer in asymptomatic populations, with UV-risk counseling versus visual screening as distinct preventive actions.

### MEMBERS
- skin cancer prevention counseling
- skin cancer screening

### EVIDENCE
- skin cancer prevention counseling: Catalog row(s): USPSTF 2018 recommendation-statement, population pediatric, adolescent, adult, citation 10.1001/jama.2018.1623. Complete threshold sheet: first retained decision young-person-uv-counseling = counsel young adults, adolescents, children, and parents of young children to minimize UV exposure; Grade B for fair-skin-age-6-months-to-24-years; population record fair-skin-age-6-months-to-24-years.
- skin cancer screening: Catalog row(s): USPSTF 2023 recommendation-statement, population adolescent, adult, citation 10.1001/jama.2023.4342. Complete threshold sheet: first retained decision screening-evidence-conclusion = evidence is insufficient to assess the balance of benefits and harms of clinician visual skin examination for skin-cancer screening for asymptomatic-adolescents-adults-no-lesion-history; population record asymptomatic-adolescents-adults-no-lesion-history.

## SUBJECT: tobacco smoking cessation
DATE: 2026-09-01
ELECTED: tobacco smoking cessation
ELECTION: The member-authored key "tobacco smoking cessation" was selected uniquely to preserve overlapping maximal-clique identity; it is a key, not a clinical-priority label.
REFUTATION: Independent refutation findings: tobacco smoking cessation / tobacco use prevention and cessation: Both USPSTF sheets address preventing or stopping tobacco use, with adults and pregnancy versus children and adolescents as population branches.

### MEMBERS
- tobacco smoking cessation
- tobacco use prevention and cessation

### EVIDENCE
- tobacco smoking cessation: Catalog row(s): USPSTF 2021 recommendation-statement, population adult, pregnancy, citation 10.1001/jama.2020.25019. Complete threshold sheet: first retained decision adult-cessation-action = ask about tobacco use, advise stopping tobacco, and provide behavioral interventions plus FDA-approved pharmacotherapy for nonpregnant-adults-tobacco; population record all-adults.
- tobacco use prevention and cessation: Catalog row(s): USPSTF 2020 recommendation-statement, population pediatric, adolescent, citation 10.1001/jama.2020.4679. Complete threshold sheet: first retained decision prevention-recommendation = primary care clinicians should provide interventions, including education or brief counseling, to prevent tobacco-use initiation for youth-not-using-tobacco; population record school-aged-children-adolescents-under-18.
