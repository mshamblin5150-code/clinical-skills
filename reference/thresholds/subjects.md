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
ELECTION: This key names the abdominal aneurysm subtype that makes the pair cohere; `aortic disease` is the broader host guideline and would erase the clique's specific screening-and-AAA focus.
REFUTATION: Independent refutation findings: abdominal aortic aneurysm screening / aortic disease: The aortic-disease sheet substantively covers aneurysm definition, surveillance, and intervention, while the USPSTF sheet covers detection of the abdominal aneurysm subtype; broader management versus screening does not separate the aortic aneurysm subject.

### MEMBERS
- abdominal aortic aneurysm screening
- aortic disease

### EVIDENCE
- abdominal aortic aneurysm screening: Read the catalog row(s) whose topic is abdominal aortic aneurysm screening, followed the artifact binding in coverage.md to [abdominal-aortic-aneurysm-screening.md](abdominal-aortic-aneurysm-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- aortic disease: Read the catalog row(s) whose topic is aortic disease, followed the artifact binding in coverage.md to [aortic-disease.md](aortic-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: acute ischemic stroke, early management
DATE: 2026-09-01
ELECTED: acute ischemic stroke, early management
ELECTION: This key identifies the index ischemic stroke event around which acute care and both prevention phases are organized; either prevention key would foreground one temporal branch and hide the clique's full stroke-care span.
REFUTATION: Independent refutation findings: acute ischemic stroke, early management / secondary stroke prevention: Both AHA/ASA sheets concern ischemic stroke in patients, covering acute management and prevention after stroke or TIA; care phase does not create a different stroke subject. acute ischemic stroke, early management / stroke primary prevention: The sheets govern the same stroke outcome before and after onset, with primary prevention versus acute ischemic management as explicit phases; the stroke subject remains substantive in both. secondary stroke prevention / stroke primary prevention: Both AHA/ASA sheets prevent stroke, separated by absence versus presence of prior stroke or TIA; that population distinction does not create a different stroke-prevention subject.

### MEMBERS
- acute ischemic stroke, early management
- secondary stroke prevention
- stroke primary prevention

### EVIDENCE
- acute ischemic stroke, early management: Read the catalog row(s) whose topic is acute ischemic stroke, early management, followed the artifact binding in coverage.md to [acute-ischemic-stroke-early-management.md](acute-ischemic-stroke-early-management.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- secondary stroke prevention: Read the catalog row(s) whose topic is secondary stroke prevention, followed the artifact binding in coverage.md to [secondary-stroke-prevention.md](secondary-stroke-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- stroke primary prevention: Read the catalog row(s) whose topic is stroke primary prevention, followed the artifact binding in coverage.md to [stroke-primary-prevention.md](stroke-primary-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: childhood and adolescent immunization schedule
DATE: 2026-09-01
ELECTED: childhood and adolescent immunization schedule
ELECTION: This is the member-authored name with the broadest explicit pediatric life-stage scope, covering both childhood and adolescence; the adult key and the young-child key each anchor the schedule to one narrower age branch.
REFUTATION: Independent refutation findings: adult immunization schedule / childhood and adolescent immunization schedule: Both CDC schedule sheets govern routine vaccine timing and catch-up by age; adult versus older-child population is the substantive distinction within immunization. adult immunization schedule / childhood immunization schedule: The complete CDC schedule captures address the same routine immunization subject across adult versus young-child age bands. childhood and adolescent immunization schedule / childhood immunization schedule: The two CDC schedule captures govern contiguous pediatric age bands and the same routine vaccine series, so age population does not split the immunization subject.

### MEMBERS
- adult immunization schedule
- childhood and adolescent immunization schedule
- childhood immunization schedule

### EVIDENCE
- adult immunization schedule: Read the catalog row(s) whose topic is adult immunization schedule, followed the artifact binding in coverage.md to [adult-immunization-schedule.md](adult-immunization-schedule.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- childhood and adolescent immunization schedule: Read the catalog row(s) whose topic is childhood and adolescent immunization schedule, followed the artifact binding in coverage.md to [childhood-and-adolescent-immunization-schedule.md](childhood-and-adolescent-immunization-schedule.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- childhood immunization schedule: Read the catalog row(s) whose topic is childhood immunization schedule, followed the artifact binding in coverage.md to [childhood-immunization-schedule.md](childhood-immunization-schedule.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: anemia in chronic kidney disease
DATE: 2026-09-01
ELECTED: anemia in chronic kidney disease
ELECTION: The complication-specific key preserves the anemia-CKD intersection that defines this clique; `chronic kidney disease` is a shared host member of several distinct CKD complication groups and cannot uniquely identify this one.
REFUTATION: Independent refutation findings: anemia in chronic kidney disease / chronic kidney disease: The anemia sheet substantively defines CKD stages and manages a CKD complication in people with CKD, while the general CKD sheet covers anemia among CKD progression and complications; this is legitimate nested membership.

### MEMBERS
- anemia in chronic kidney disease
- chronic kidney disease

### EVIDENCE
- anemia in chronic kidney disease: Read the catalog row(s) whose topic is anemia in chronic kidney disease, followed the artifact binding in coverage.md to [anemia-in-chronic-kidney-disease.md](anemia-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: antibiotic stewardship program implementation
DATE: 2026-09-01
ELECTED: antibiotic stewardship program implementation
ELECTION: Program implementation covers the operational whole—staffing, preauthorization, audit, and feedback—within which leadership competencies sit; the leadership key would narrow the group to one implementation role.
REFUTATION: Independent refutation findings: antibiotic stewardship program implementation / antimicrobial stewardship leadership: Both complete guidelines substantively concern operation of antimicrobial stewardship programs, including leadership, staffing, preauthorization, audit, and feedback; leader competencies are a focused implementation branch.

### MEMBERS
- antibiotic stewardship program implementation
- antimicrobial stewardship leadership

### EVIDENCE
- antibiotic stewardship program implementation: Read the catalog row(s) whose topic is antibiotic stewardship program implementation, followed the artifact binding in coverage.md to [antibiotic-stewardship-program-implementation.md](antibiotic-stewardship-program-implementation.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- antimicrobial stewardship leadership: Read the catalog row(s) whose topic is antimicrobial stewardship leadership, followed the artifact binding in coverage.md to [antimicrobial-stewardship-leadership.md](antimicrobial-stewardship-leadership.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: anxiety disorder screening
DATE: 2026-09-01
ELECTED: anxiety disorder screening
ELECTION: The adult statement's key explicitly names anxiety disorders as the screened condition and is not tied to the youth wording; `anxiety screening` is less diagnostically specific and would make the cross-population group less precise.
REFUTATION: Independent refutation findings: anxiety disorder screening / anxiety screening: Both complete USPSTF sheets screen asymptomatic people for anxiety disorders and differ principally by adult/perinatal versus pediatric population; neither sheet introduces a different anxiety condition.

### MEMBERS
- anxiety disorder screening
- anxiety screening

### EVIDENCE
- anxiety disorder screening: Read the catalog row(s) whose topic is anxiety disorder screening, followed the artifact binding in coverage.md to [anxiety-disorder-screening.md](anxiety-disorder-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- anxiety screening: Read the catalog row(s) whose topic is anxiety screening, followed the artifact binding in coverage.md to [anxiety-screening.md](anxiety-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: atrial fibrillation
DATE: 2026-09-01
ELECTED: atrial fibrillation
ELECTION: The condition name accommodates detection, diagnosis, anticoagulation, and longitudinal management; `atrial fibrillation screening` would incorrectly make the screening phase the identity of a group that includes full disease management.
REFUTATION: Independent refutation findings: atrial fibrillation / atrial fibrillation screening: The USPSTF sheet screens for atrial fibrillation and the AHA/ACC sheet diagnoses and manages the same rhythm disorder; detection versus management does not split AF.

### MEMBERS
- atrial fibrillation
- atrial fibrillation screening

### EVIDENCE
- atrial fibrillation: Read the catalog row(s) whose topic is atrial fibrillation, followed the artifact binding in coverage.md to [atrial-fibrillation.md](atrial-fibrillation.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- atrial fibrillation screening: Read the catalog row(s) whose topic is atrial fibrillation screening, followed the artifact binding in coverage.md to [atrial-fibrillation-screening.md](atrial-fibrillation-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: blood cholesterol
DATE: 2026-09-01
ELECTED: blood cholesterol
ELECTION: This key names the lipid substrate assessed and treated across the pair, while `cardiovascular disease prevention, statins` names one drug-use purpose and also participates in other prevention cliques; the cholesterol key keeps this lipid-focused overlap distinct.
REFUTATION: Independent refutation findings: blood cholesterol / cardiovascular disease prevention, statins: The blood-cholesterol guideline substantively makes statin and other lipid-lowering decisions for ASCVD prevention, and the USPSTF statement makes the corresponding primary-prevention statin decision; the shared lipid-management scope is clinical, not lexical.

### MEMBERS
- blood cholesterol
- cardiovascular disease prevention, statins

### EVIDENCE
- blood cholesterol: Read the catalog row(s) whose topic is blood cholesterol, followed the artifact binding in coverage.md to [blood-cholesterol.md](blood-cholesterol.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- cardiovascular disease prevention, statins: Read the catalog row(s) whose topic is cardiovascular disease prevention, statins, followed the artifact binding in coverage.md to [cardiovascular-disease-prevention-statins.md](cardiovascular-disease-prevention-statins.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: dyslipidemia
DATE: 2026-09-01
ELECTED: dyslipidemia
ELECTION: `Dyslipidemia` is the canonical condition-level umbrella spanning adult and pediatric detection, classification, and treatment; the alternatives are an older analyte-centered term, a screening phase, or a CKD-specific management branch.
REFUTATION: Independent refutation findings: blood cholesterol / dyslipidemia: Both full guidelines define, detect, and manage abnormal cholesterol, LDL-C, and triglycerides; the newer dyslipidemia wording broadens rather than changes the lipid-disorder subject. blood cholesterol / lipid disorder screening: The complete sheets address detection and clinical interpretation of lipid disorders, with the general adult management sheet and pediatric screening statement differing by population and care phase rather than condition. blood cholesterol / lipid management in chronic kidney disease: The CKD sheet substantively assesses and treats cholesterol and triglyceride disorders with statins and statin-ezetimibe; CKD is an added population and second membership, not a replacement for the lipid subject. dyslipidemia / lipid disorder screening: Both complete sheets address detection and classification of lipid disorders, with comprehensive pediatric/adult dyslipidemia management versus pediatric screening as phase and population differences. dyslipidemia / lipid management in chronic kidney disease: The CKD sheet substantively assesses and treats cholesterol and triglyceride disorders, while CKD adds a nested population and second membership to the general dyslipidemia subject. lipid disorder screening / lipid management in chronic kidney disease: Both sheets substantively assess cholesterol and triglyceride disorders, with pediatric population screening versus CKD-specific assessment and treatment; the CKD sheet legitimately adds a second membership.

### MEMBERS
- blood cholesterol
- dyslipidemia
- lipid disorder screening
- lipid management in chronic kidney disease

### EVIDENCE
- blood cholesterol: Read the catalog row(s) whose topic is blood cholesterol, followed the artifact binding in coverage.md to [blood-cholesterol.md](blood-cholesterol.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- dyslipidemia: Read the catalog row(s) whose topic is dyslipidemia, followed the artifact binding in coverage.md to [dyslipidemia.md](dyslipidemia.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- lipid disorder screening: Read the catalog row(s) whose topic is lipid disorder screening, followed the artifact binding in coverage.md to [lipid-disorder-screening.md](lipid-disorder-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- lipid management in chronic kidney disease: Read the catalog row(s) whose topic is lipid management in chronic kidney disease, followed the artifact binding in coverage.md to [lipid-management-in-chronic-kidney-disease.md](lipid-management-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: blood pressure in chronic kidney disease
DATE: 2026-09-01
ELECTED: blood pressure in chronic kidney disease
ELECTION: The nested-condition name uniquely identifies blood-pressure management within CKD; the general `chronic kidney disease` key belongs to many complication cliques and would not distinguish this intersection.
REFUTATION: Independent refutation findings: blood pressure in chronic kidney disease / chronic kidney disease: The BP-in-CKD sheet substantively defines CKD stages and manages a central CKD progression risk, while the general CKD sheet itself includes BP targets and renin-angiotensin therapy; nested CKD membership is supported by both scopes.

### MEMBERS
- blood pressure in chronic kidney disease
- chronic kidney disease

### EVIDENCE
- blood pressure in chronic kidney disease: Read the catalog row(s) whose topic is blood pressure in chronic kidney disease, followed the artifact binding in coverage.md to [blood-pressure-in-chronic-kidney-disease.md](blood-pressure-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: high blood pressure
DATE: 2026-09-01
ELECTED: high blood pressure
ELECTION: This is the broad condition-level key that naturally covers pediatric and adult screening, confirmation, and treatment; the other members are population- or CKD-specific care branches rather than suitable names for the whole group.
REFUTATION: Independent refutation findings: blood pressure in chronic kidney disease / high blood pressure: Both complete guidelines substantively measure and treat high blood pressure, with the KDIGO sheet narrowing the population to CKD and adding a second CKD membership. blood pressure in chronic kidney disease / high blood pressure screening: The KDIGO sheet and pediatric USPSTF sheet address BP measurement, confirmation, and high-BP thresholds; CKD and age are population branches within the high-blood-pressure subject. blood pressure in chronic kidney disease / hypertension screening: Both sheets substantively cover accurate BP measurement and confirmation of hypertension, with CKD-specific management versus adult population screening as the scope difference. high blood pressure / high blood pressure screening: Both complete sheets address high blood pressure, with pediatric asymptomatic screening versus adult prevention, detection, evaluation, and management as population and phase differences. high blood pressure / hypertension screening: Hypertension and high blood pressure are the same condition in the sheets, and adult screening feeds the general adult management pathway. high blood pressure screening / hypertension screening: Both USPSTF sheets screen asymptomatic people for the same high-blood-pressure/hypertension condition and differ by pediatric versus adult population.

### MEMBERS
- blood pressure in chronic kidney disease
- high blood pressure
- high blood pressure screening
- hypertension screening

### EVIDENCE
- blood pressure in chronic kidney disease: Read the catalog row(s) whose topic is blood pressure in chronic kidney disease, followed the artifact binding in coverage.md to [blood-pressure-in-chronic-kidney-disease.md](blood-pressure-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- high blood pressure: Read the catalog row(s) whose topic is high blood pressure, followed the artifact binding in coverage.md to [hypertension.md](hypertension.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- high blood pressure screening: Read the catalog row(s) whose topic is high blood pressure screening, followed the artifact binding in coverage.md to [high-blood-pressure-screening.md](high-blood-pressure-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- hypertension screening: Read the catalog row(s) whose topic is hypertension screening, followed the artifact binding in coverage.md to [hypertension-screening.md](hypertension-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: breast cancer risk-reducing medication
DATE: 2026-09-01
ELECTED: breast cancer risk-reducing medication
ELECTION: The chemoprevention key identifies the added clinical branch that makes this pair more than a screening-only subject; electing `breast cancer screening` would obscure the risk-reducing medication decision that distinguishes the clique.
REFUTATION: Independent refutation findings: breast cancer risk-reducing medication / breast cancer screening: Both USPSTF sheets govern prevention and early detection of breast cancer in asymptomatic women, with chemoprevention versus screening as care branches of the same cancer subject.

### MEMBERS
- breast cancer risk-reducing medication
- breast cancer screening

### EVIDENCE
- breast cancer risk-reducing medication: Read the catalog row(s) whose topic is breast cancer risk-reducing medication, followed the artifact binding in coverage.md to [breast-cancer-risk-reducing-medication.md](breast-cancer-risk-reducing-medication.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- breast cancer screening: Read the catalog row(s) whose topic is breast cancer screening, followed the artifact binding in coverage.md to [breast-cancer-screening.md](breast-cancer-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: cardiovascular disease prevention, aspirin
DATE: 2026-09-01
ELECTED: cardiovascular disease prevention, aspirin
ELECTION: The aspirin key uniquely states the shared primary cardiovascular-prevention purpose while naming a concrete risk-conditioned action: counseling, statins, and vitamin/mineral supplementation are peer intervention branches, and nontraditional-risk assessment and electrocardiography are decision-support branches. Unlike the vitamin/mineral member, it does not add cancer as a second endpoint; unlike the statin member, it does not also key the separate blood-cholesterol clique; and unlike the counseling and assessment members, it is concise without narrowing the subject to behavior or a testing modality.
REFUTATION: Independent refutation findings: cardiovascular disease prevention, aspirin / cardiovascular disease prevention, diet and physical activity counseling: Both USPSTF statements target primary prevention of cardiovascular morbidity and mortality in adults without established CVD; aspirin versus behavioral counseling is an intervention branch within that subject. cardiovascular disease prevention, aspirin / cardiovascular disease prevention, statins: Both sheets use baseline cardiovascular risk to select a preventive medication for adults without established CVD; distinct drugs do not create distinct clinical subjects. cardiovascular disease prevention, aspirin / cardiovascular disease risk assessment, nontraditional risk factors: The risk-assessment sheet and aspirin sheet both substantively operate on primary CVD-risk estimation in asymptomatic adults, with assessment feeding prevention rather than naming an unrelated condition. cardiovascular disease prevention, aspirin / cardiovascular disease risk screening, electrocardiography: Both sheets address primary CVD prevention decisions in asymptomatic adults stratified by cardiovascular risk; ECG screening versus aspirin is a screening/intervention distinction within the same prevention subject. cardiovascular disease prevention, aspirin / vitamin and mineral supplementation for cardiovascular disease and cancer prevention: Both sheets make direct primary-CVD-prevention intervention decisions; supplementation's additional cancer outcome creates another substantive scope rather than excluding its CVD membership. cardiovascular disease prevention, diet and physical activity counseling / cardiovascular disease prevention, statins: Both sheets target primary prevention of cardiovascular events in adults and select intervention intensity using risk status; behavioral counseling versus statins is not a different disease subject. cardiovascular disease prevention, diet and physical activity counseling / cardiovascular disease risk assessment, nontraditional risk factors: Risk assessment and lifestyle counseling are substantive steps in primary CVD prevention for asymptomatic adults; differing tools and actions do not split the cardiovascular-prevention subject. cardiovascular disease prevention, diet and physical activity counseling / cardiovascular disease risk screening, electrocardiography: Both USPSTF statements address primary CVD prevention in adults without established disease, one counseling on behavior and the other assessing ECG screening; the outcome subject is shared. cardiovascular disease prevention, diet and physical activity counseling / vitamin and mineral supplementation for cardiovascular disease and cancer prevention: Counseling and supplementation are different preventive modalities whose primary patient-facing decisions directly address the same CVD outcome. cardiovascular disease prevention, statins / cardiovascular disease risk assessment, nontraditional risk factors: The statin statement and nontraditional-risk statement both substantively use primary CVD-risk estimation to guide prevention in asymptomatic adults; assessment versus therapy is a care-phase distinction. cardiovascular disease prevention, statins / cardiovascular disease risk screening, electrocardiography: Both sheets address cardiovascular-risk evaluation and primary prevention in adults without known CVD, using ECG screening versus statin treatment as distinct actions within the same subject. cardiovascular disease prevention, statins / vitamin and mineral supplementation for cardiovascular disease and cancer prevention: Both sheets directly select interventions for primary CVD prevention; the products differ, but the clinical subject does not. cardiovascular disease risk assessment, nontraditional risk factors / cardiovascular disease risk screening, electrocardiography: The two complete USPSTF statements evaluate additional methods for cardiovascular-risk assessment in asymptomatic adults and use the same primary-prevention risk strata; the tested modality is the substantive difference. cardiovascular disease risk assessment, nontraditional risk factors / vitamin and mineral supplementation for cardiovascular disease and cancer prevention: Risk assessment and intervention selection are different phases of the same primary-CVD-prevention pathway. cardiovascular disease risk screening, electrocardiography / vitamin and mineral supplementation for cardiovascular disease and cancer prevention: ECG screening and supplement decisions both perform primary patient-facing work within CVD prevention; screening versus intervention does not split that subject.

### MEMBERS
- cardiovascular disease prevention, aspirin
- cardiovascular disease prevention, diet and physical activity counseling
- cardiovascular disease prevention, statins
- cardiovascular disease risk assessment, nontraditional risk factors
- cardiovascular disease risk screening, electrocardiography
- vitamin and mineral supplementation for cardiovascular disease and cancer prevention

### EVIDENCE
- cardiovascular disease prevention, aspirin: Read the catalog row(s) whose topic is cardiovascular disease prevention, aspirin, followed the artifact binding in coverage.md to [cardiovascular-disease-prevention-aspirin.md](cardiovascular-disease-prevention-aspirin.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- cardiovascular disease prevention, diet and physical activity counseling: Read the catalog row(s) whose topic is cardiovascular disease prevention, diet and physical activity counseling, followed the artifact binding in coverage.md to [cardiovascular-disease-prevention-diet-and-physical-activity-counseling.md](cardiovascular-disease-prevention-diet-and-physical-activity-counseling.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- cardiovascular disease prevention, statins: Read the catalog row(s) whose topic is cardiovascular disease prevention, statins, followed the artifact binding in coverage.md to [cardiovascular-disease-prevention-statins.md](cardiovascular-disease-prevention-statins.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- cardiovascular disease risk assessment, nontraditional risk factors: Read the catalog row(s) whose topic is cardiovascular disease risk assessment, nontraditional risk factors, followed the artifact binding in coverage.md to [cardiovascular-disease-risk-assessment-nontraditional-risk-factors.md](cardiovascular-disease-risk-assessment-nontraditional-risk-factors.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- cardiovascular disease risk screening, electrocardiography: Read the catalog row(s) whose topic is cardiovascular disease risk screening, electrocardiography, followed the artifact binding in coverage.md to [cardiovascular-disease-risk-screening-electrocardiography.md](cardiovascular-disease-risk-screening-electrocardiography.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- vitamin and mineral supplementation for cardiovascular disease and cancer prevention: Read the catalog row(s) whose topic is vitamin and mineral supplementation for cardiovascular disease and cancer prevention, followed the artifact binding in coverage.md to [vitamin-and-mineral-supplementation-for-cardiovascular-disease-and-cancer-prevention.md](vitamin-and-mineral-supplementation-for-cardiovascular-disease-and-cancer-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: chronic hepatitis B
DATE: 2026-09-01
ELECTED: chronic hepatitis B
ELECTION: The established disease name spans screening, phase classification, and treatment without privileging case finding; `hepatitis B screening` is a care-phase key and cannot represent the chronic-infection management content.
REFUTATION: Independent refutation findings: chronic hepatitis B / hepatitis B screening: The sheets cover detection and treatment phases of HBV infection, including screening markers that establish the population entering chronic-HBV management; screening versus established infection does not separate HBV.

### MEMBERS
- chronic hepatitis B
- hepatitis B screening

### EVIDENCE
- chronic hepatitis B: Read the catalog row(s) whose topic is chronic hepatitis B, followed the artifact binding in coverage.md to [chronic-hepatitis-b.md](chronic-hepatitis-b.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- hepatitis B screening: Read the catalog row(s) whose topic is hepatitis B screening, followed the artifact binding in coverage.md to [hepatitis-b-screening.md](hepatitis-b-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: chronic kidney disease
DATE: 2026-09-01
ELECTED: chronic kidney disease
ELECTION: The general CKD key is population-neutral and covers the disease definition and management shared across the pair; the HIV-specific member is a nested population branch that would unnecessarily restrict the group's CKD identity.
REFUTATION: Independent refutation findings: chronic kidney disease / chronic kidney disease in HIV infection: The HIV-specific guideline substantively defines, detects, stages, and manages CKD and its progression, making HIV an added population and second subject rather than reducing CKD to a passing mention.

### MEMBERS
- chronic kidney disease
- chronic kidney disease in HIV infection

### EVIDENCE
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- chronic kidney disease in HIV infection: Read the catalog row(s) whose topic is chronic kidney disease in HIV infection, followed the artifact binding in coverage.md to [chronic-kidney-disease-in-hiv-infection.md](chronic-kidney-disease-in-hiv-infection.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: chronic kidney disease-mineral and bone disorder
DATE: 2026-09-01
ELECTED: chronic kidney disease-mineral and bone disorder
ELECTION: The CKD-MBD name identifies the mineral-and-bone complication that distinguishes this clique from other CKD groups; the general CKD member is deliberately reused across those groups and is therefore not a unique key here.
REFUTATION: Independent refutation findings: chronic kidney disease / chronic kidney disease-mineral and bone disorder: CKD-MBD is a substantive complication of CKD stratified by CKD stages, and the general CKD sheet covers evaluation and complications; the narrower sheet legitimately belongs to the CKD subject as well as MBD.

### MEMBERS
- chronic kidney disease
- chronic kidney disease-mineral and bone disorder

### EVIDENCE
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- chronic kidney disease-mineral and bone disorder: Read the catalog row(s) whose topic is chronic kidney disease-mineral and bone disorder, followed the artifact binding in coverage.md to [chronic-kidney-disease-mineral-and-bone-disorder.md](chronic-kidney-disease-mineral-and-bone-disorder.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: diabetes in chronic kidney disease
DATE: 2026-09-01
ELECTED: diabetes in chronic kidney disease
ELECTION: This intersection key preserves both diabetes and kidney disease in the group's identity; `chronic kidney disease` alone would lose the diabetes-specific treatment and progression scope and collide with other nested CKD cliques.
REFUTATION: Independent refutation findings: chronic kidney disease / diabetes in chronic kidney disease: The diabetes-in-CKD sheet substantively stages CKD and manages kidney-protective therapy and CKD progression in people with diabetes; it supports both diabetes and CKD memberships.

### MEMBERS
- chronic kidney disease
- diabetes in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- diabetes in chronic kidney disease: Read the catalog row(s) whose topic is diabetes in chronic kidney disease, followed the artifact binding in coverage.md to [diabetes-in-chronic-kidney-disease.md](diabetes-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: heart failure in chronic kidney disease
DATE: 2026-09-01
ELECTED: heart failure in chronic kidney disease
ELECTION: The nested name uniquely identifies the heart-failure/CKD scope represented by the scope-of-work artifact; the general CKD key would be indistinguishable from the repository's other CKD complication groups.
REFUTATION: Independent refutation findings: chronic kidney disease / heart failure in chronic kidney disease: Although the heart-failure artifact is a declared non-source, its complete scope is expressly for heart failure in people with CKD and future CKD-specific management; the nested CKD subject is substantive in the document form available.

### MEMBERS
- chronic kidney disease
- heart failure in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- heart failure in chronic kidney disease: Read the catalog row(s) whose topic is heart failure in chronic kidney disease, followed the artifact binding in coverage.md to [heart-failure-in-chronic-kidney-disease.md](heart-failure-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: hepatitis C in chronic kidney disease
DATE: 2026-09-01
ELECTED: hepatitis C in chronic kidney disease
ELECTION: This key retains the HCV, dialysis, transplant, and CKD intersection that defines the record; the general CKD member is too broad and is already the host of several separate complication cliques.
REFUTATION: Independent refutation findings: chronic kidney disease / hepatitis C in chronic kidney disease: The HCV-in-CKD guideline substantively evaluates CKD stages, dialysis, transplant, and HCV-associated renal disease; it therefore supports CKD membership in addition to HCV.

### MEMBERS
- chronic kidney disease
- hepatitis C in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- hepatitis C in chronic kidney disease: Read the catalog row(s) whose topic is hepatitis C in chronic kidney disease, followed the artifact binding in coverage.md to [hepatitis-c-in-chronic-kidney-disease.md](hepatitis-c-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: lipid management in chronic kidney disease
DATE: 2026-09-01
ELECTED: lipid management in chronic kidney disease
ELECTION: The elected name captures both the lipid-management action and its CKD population, preserving the intersection's distinct identity; `chronic kidney disease` would erase the lipid focus and duplicate the key of unrelated CKD complication records.
REFUTATION: Independent refutation findings: chronic kidney disease / lipid management in chronic kidney disease: The lipid sheet substantively stratifies assessment and treatment across CKD, dialysis, pediatric, and transplant populations, supporting nested CKD membership as well as dyslipidemia.

### MEMBERS
- chronic kidney disease
- lipid management in chronic kidney disease

### EVIDENCE
- chronic kidney disease: Read the catalog row(s) whose topic is chronic kidney disease, followed the artifact binding in coverage.md to [chronic-kidney-disease.md](chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- lipid management in chronic kidney disease: Read the catalog row(s) whose topic is lipid management in chronic kidney disease, followed the artifact binding in coverage.md to [lipid-management-in-chronic-kidney-disease.md](lipid-management-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: chronic kidney disease in HIV infection
DATE: 2026-09-01
ELECTED: chronic kidney disease in HIV infection
ELECTION: The CKD-in-HIV member is the differentiator for this maximal clique: its other HIV members are also grouped with chronic pain, so electing PrEP, primary care, or screening would not distinguish the renal-complication overlap.
REFUTATION: Independent refutation findings: chronic kidney disease in HIV infection / HIV preexposure prophylaxis: The CKD guideline substantively manages HIV-infected people and antiretroviral exposure, while PrEP prevents acquisition; CKD adds a nested condition but does not erase the shared HIV clinical subject across prevention and established infection. chronic kidney disease in HIV infection / HIV primary care: Both IDSA sheets provide care for people with HIV, and the primary-care sheet includes renal monitoring while the CKD sheet expands that HIV complication; nested kidney disease supports multi-membership. chronic kidney disease in HIV infection / HIV screening: The sheets address detection and subsequent management of HIV infection, with the CKD sheet adding a substantive renal complication and second membership rather than a different infection. HIV preexposure prophylaxis / HIV primary care: The sheets cover prevention before HIV acquisition and longitudinal care after infection, both substantively organized around HIV risk, testing, antiretroviral use, and prevention; care phase does not split the HIV subject. HIV preexposure prophylaxis / HIV screening: Both USPSTF sheets operate in people without known HIV and substantively link HIV risk assessment, testing, and prevention; PrEP versus screening is an action distinction within HIV prevention. HIV primary care / HIV screening: The USPSTF statement detects HIV infection and the IDSA sheet provides longitudinal primary care after diagnosis; screening and management phases address the same infection.

### MEMBERS
- chronic kidney disease in HIV infection
- HIV preexposure prophylaxis
- HIV primary care
- HIV screening

### EVIDENCE
- chronic kidney disease in HIV infection: Read the catalog row(s) whose topic is chronic kidney disease in HIV infection, followed the artifact binding in coverage.md to [chronic-kidney-disease-in-hiv-infection.md](chronic-kidney-disease-in-hiv-infection.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- HIV preexposure prophylaxis: Read the catalog row(s) whose topic is HIV preexposure prophylaxis, followed the artifact binding in coverage.md to [hiv-preexposure-prophylaxis.md](hiv-preexposure-prophylaxis.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- HIV primary care: Read the catalog row(s) whose topic is HIV primary care, followed the artifact binding in coverage.md to [hiv-primary-care.md](hiv-primary-care.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- HIV screening: Read the catalog row(s) whose topic is HIV screening, followed the artifact binding in coverage.md to [hiv-screening.md](hiv-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: chronic obstructive pulmonary disease
DATE: 2026-09-01
ELECTED: chronic obstructive pulmonary disease
ELECTION: The fully expanded disease name is the canonical condition-level key and covers diagnosis, prevention, and treatment; `COPD screening` is an abbreviated, phase-specific member that cannot represent the management guideline's breadth.
REFUTATION: Independent refutation findings: chronic obstructive pulmonary disease / COPD screening: Both complete sheets concern COPD, with USPSTF addressing case finding in asymptomatic adults and GOLD covering diagnosis, management, and prevention; screening versus management is the only subject-level distinction.

### MEMBERS
- chronic obstructive pulmonary disease
- COPD screening

### EVIDENCE
- chronic obstructive pulmonary disease: Read the catalog row(s) whose topic is chronic obstructive pulmonary disease, followed the artifact binding in coverage.md to [chronic-obstructive-pulmonary-disease.md](chronic-obstructive-pulmonary-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- COPD screening: Read the catalog row(s) whose topic is COPD screening, followed the artifact binding in coverage.md to [copd-screening.md](copd-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: chronic pain in HIV infection
DATE: 2026-09-01
ELECTED: chronic pain in HIV infection
ELECTION: The chronic-pain-in-HIV member uniquely distinguishes this maximal clique from the parallel CKD-in-HIV clique, which shares the same PrEP, primary-care, and screening members.
REFUTATION: Independent refutation findings: chronic pain in HIV infection / HIV preexposure prophylaxis: The pain guideline is substantively care of people living with HIV, and the PrEP statement prevents that same infection; chronic pain adds a second nested subject while prevention versus established infection remains an HIV care-phase distinction. chronic pain in HIV infection / HIV primary care: Both sheets care for people with HIV, with chronic-pain assessment and treatment a focused complication within the broader HIV primary-care subject. chronic pain in HIV infection / HIV screening: HIV screening and downstream care of chronic pain in people with HIV are detection and nested-management phases of the HIV subject; the pain sheet retains a second condition membership. HIV preexposure prophylaxis / HIV primary care: The sheets cover prevention before HIV acquisition and longitudinal care after infection, both substantively organized around HIV risk, testing, antiretroviral use, and prevention; care phase does not split the HIV subject. HIV preexposure prophylaxis / HIV screening: Both USPSTF sheets operate in people without known HIV and substantively link HIV risk assessment, testing, and prevention; PrEP versus screening is an action distinction within HIV prevention. HIV primary care / HIV screening: The USPSTF statement detects HIV infection and the IDSA sheet provides longitudinal primary care after diagnosis; screening and management phases address the same infection.

### MEMBERS
- chronic pain in HIV infection
- HIV preexposure prophylaxis
- HIV primary care
- HIV screening

### EVIDENCE
- chronic pain in HIV infection: Read the catalog row(s) whose topic is chronic pain in HIV infection, followed the artifact binding in coverage.md to [chronic-pain-in-hiv-infection.md](chronic-pain-in-hiv-infection.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- HIV preexposure prophylaxis: Read the catalog row(s) whose topic is HIV preexposure prophylaxis, followed the artifact binding in coverage.md to [hiv-preexposure-prophylaxis.md](hiv-preexposure-prophylaxis.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- HIV primary care: Read the catalog row(s) whose topic is HIV primary care, followed the artifact binding in coverage.md to [hiv-primary-care.md](hiv-primary-care.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- HIV screening: Read the catalog row(s) whose topic is HIV screening, followed the artifact binding in coverage.md to [hiv-screening.md](hiv-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: Clostridioides difficile infection
DATE: 2026-09-01
ELECTED: Clostridioides difficile infection
ELECTION: This key uses the current genus name carried by the newer IDSA update; `Clostridium difficile infection` is the superseded taxonomic wording for the same infection and is retained as a member, not the elected key.
REFUTATION: Independent refutation findings: Clostridioides difficile infection / Clostridium difficile infection: Both IDSA sheets manage the same C. difficile infection; Clostridioides is the renamed genus, while the population and update scope explain the remaining differences.

### MEMBERS
- Clostridioides difficile infection
- Clostridium difficile infection

### EVIDENCE
- Clostridioides difficile infection: Read the catalog row(s) whose topic is Clostridioides difficile infection, followed the artifact binding in coverage.md to [clostridioides-difficile-infection.md](clostridioides-difficile-infection.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- Clostridium difficile infection: Read the catalog row(s) whose topic is Clostridium difficile infection, followed the artifact binding in coverage.md to [clostridium-difficile-infection.md](clostridium-difficile-infection.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: community-acquired pneumonia
DATE: 2026-09-01
ELECTED: community-acquired pneumonia
ELECTION: The community-acquired key anchors the initial pneumonia diagnosis and severity pathway that contrasts with the narrower hospital- and ventilator-defined acquisition branch; the combined HAP/VAP name would make the shared pneumonia group appear limited to inpatient acquisition.
REFUTATION: Independent refutation findings: community-acquired pneumonia / hospital-acquired and ventilator-associated pneumonia: Both ATS/IDSA sheets diagnose and treat pneumonia in adults; acquisition setting changes pathogen risk, testing, and empiric therapy but remains a clinically substantive subtype distinction within pneumonia.

### MEMBERS
- community-acquired pneumonia
- hospital-acquired and ventilator-associated pneumonia

### EVIDENCE
- community-acquired pneumonia: Read the catalog row(s) whose topic is community-acquired pneumonia, followed the artifact binding in coverage.md to [community-acquired-pneumonia.md](community-acquired-pneumonia.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- hospital-acquired and ventilator-associated pneumonia: Read the catalog row(s) whose topic is hospital-acquired and ventilator-associated pneumonia, followed the artifact binding in coverage.md to [hospital-acquired-and-ventilator-associated-pneumonia.md](hospital-acquired-and-ventilator-associated-pneumonia.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: COVID-19 infection prevention for healthcare personnel
DATE: 2026-09-01
ELECTED: COVID-19 infection prevention for healthcare personnel
ELECTION: This key names the transmission-prevention context that links testing and treatment decisions to safe clinical care; the serology and treatment alternatives each identify only one downstream patient-care phase.
REFUTATION: Independent refutation findings: COVID-19 infection prevention for healthcare personnel / COVID-19 serologic testing: Both IDSA sheets substantively concern suspected or known COVID-19, with occupational infection-control measures versus serologic diagnosis as prevention and detection branches of the same infection subject. COVID-19 infection prevention for healthcare personnel / COVID-19 treatment: The complete sheets address prevention of SARS-CoV-2 transmission during care and treatment of infected patients; personnel population and action differ, but COVID-19 remains the substantive disease driving both. COVID-19 serologic testing / COVID-19 treatment: Both complete IDSA sheets concern SARS-CoV-2 infection in patients, one delimiting serologic diagnosis and the other treatment by COVID-19 severity; diagnostic versus therapeutic scope does not split the disease.

### MEMBERS
- COVID-19 infection prevention for healthcare personnel
- COVID-19 serologic testing
- COVID-19 treatment

### EVIDENCE
- COVID-19 infection prevention for healthcare personnel: Read the catalog row(s) whose topic is COVID-19 infection prevention for healthcare personnel, followed the artifact binding in coverage.md to [covid-19-infection-prevention-for-healthcare-personnel.md](covid-19-infection-prevention-for-healthcare-personnel.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- COVID-19 serologic testing: Read the catalog row(s) whose topic is COVID-19 serologic testing, followed the artifact binding in coverage.md to [covid-19-serologic-testing.md](covid-19-serologic-testing.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- COVID-19 treatment: Read the catalog row(s) whose topic is COVID-19 treatment, followed the artifact binding in coverage.md to [covid-19-treatment.md](covid-19-treatment.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: dental caries prevention
DATE: 2026-09-01
ELECTED: dental caries prevention
ELECTION: Dental caries is the specific condition nested within the broader oral-health source, and prevention is the shared action; `oral health screening and prevention` would broaden the key beyond the condition that makes this pair a clique.
REFUTATION: Independent refutation findings: dental caries prevention / oral health screening and prevention: The broader oral-health sheets substantively include dental caries screening and preventive interventions, while the younger-child sheet focuses on caries; this is legitimate nested oral-health membership.

### MEMBERS
- dental caries prevention
- oral health screening and prevention

### EVIDENCE
- dental caries prevention: Read the catalog row(s) whose topic is dental caries prevention, followed the artifact binding in coverage.md to [dental-caries-prevention.md](dental-caries-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- oral health screening and prevention: Read the catalog row(s) whose topic is oral health screening and prevention, followed the artifact binding in coverage.md to [oral-health-screening-and-prevention.md](oral-health-screening-and-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: depression and suicide risk screening
DATE: 2026-09-01
ELECTED: depression and suicide risk screening
ELECTION: This key spans youth, adults, pregnancy, and postpartum care and names the broader detection scope; `perinatal depression prevention` is restricted to one population and one prediagnostic intervention branch.
REFUTATION: Independent refutation findings: depression and suicide risk screening / perinatal depression prevention: The screening sheet expressly includes pregnant and postpartum people and depression, while the prevention sheet targets the same perinatal depressive illness before diagnosis; suicide-risk content adds a second scope but does not erase the shared depression subject.

### MEMBERS
- depression and suicide risk screening
- perinatal depression prevention

### EVIDENCE
- depression and suicide risk screening: Read the catalog row(s) whose topic is depression and suicide risk screening, followed the artifact binding in coverage.md to [depression-and-suicide-risk-screening.md](depression-and-suicide-risk-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- perinatal depression prevention: Read the catalog row(s) whose topic is perinatal depression prevention, followed the artifact binding in coverage.md to [perinatal-depression-prevention.md](perinatal-depression-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: prediabetes and type 2 diabetes screening
DATE: 2026-09-01
ELECTED: prediabetes and type 2 diabetes screening
ELECTION: This member identifies the general prediabetes-to-type-2-diabetes continuum shared by the clique and separates it from the complication-specific diabetes cliques; `diabetes mellitus` also belongs to foot-infection and gestational-diabetes groups, while the CKD member is population-specific.
REFUTATION: Independent refutation findings: diabetes in chronic kidney disease / diabetes mellitus: The KDIGO sheet substantively manages diabetes with glycemic monitoring, targets, lifestyle, and glucose-lowering drugs, adding CKD as a nested population to the general diabetes subject. diabetes in chronic kidney disease / prediabetes and type 2 diabetes screening: Both sheets substantively address type 2 diabetes, with USPSTF case finding and KDIGO management after diabetes and CKD coexist; screening versus nested management supports one diabetes subject. diabetes mellitus / prediabetes and type 2 diabetes screening: The USPSTF sheets detect prediabetes and type 2 diabetes and ADA manages the same diabetes continuum; screening versus comprehensive management and age branches do not split the subject.

### MEMBERS
- diabetes in chronic kidney disease
- diabetes mellitus
- prediabetes and type 2 diabetes screening

### EVIDENCE
- diabetes in chronic kidney disease: Read the catalog row(s) whose topic is diabetes in chronic kidney disease, followed the artifact binding in coverage.md to [diabetes-in-chronic-kidney-disease.md](diabetes-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- diabetes mellitus: Read the catalog row(s) whose topic is diabetes mellitus, followed the artifact binding in coverage.md to [diabetes.md](diabetes.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- prediabetes and type 2 diabetes screening: Read the catalog row(s) whose topic is prediabetes and type 2 diabetes screening, followed the artifact binding in coverage.md to [prediabetes-type-2-diabetes-screening.md](prediabetes-type-2-diabetes-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: diabetes-related foot infection
DATE: 2026-09-01
ELECTED: diabetes-related foot infection
ELECTION: The complication-specific key uniquely identifies the diabetes/foot-infection intersection; `diabetes mellitus` is the shared host condition and also belongs to other maximal cliques, so it cannot distinguish this record.
REFUTATION: Independent refutation findings: diabetes mellitus / diabetes-related foot infection: The foot-infection guideline substantively addresses a diabetes complication and its management in people with diabetes, while ADA covers foot assessment and complication prevention; the narrow sheet legitimately belongs to both diabetes and infection subjects.

### MEMBERS
- diabetes mellitus
- diabetes-related foot infection

### EVIDENCE
- diabetes mellitus: Read the catalog row(s) whose topic is diabetes mellitus, followed the artifact binding in coverage.md to [diabetes.md](diabetes.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- diabetes-related foot infection: Read the catalog row(s) whose topic is diabetes-related foot infection, followed the artifact binding in coverage.md to [diabetes-related-foot-infection.md](diabetes-related-foot-infection.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: gestational diabetes screening
DATE: 2026-09-01
ELECTED: gestational diabetes screening
ELECTION: This key preserves the pregnancy-specific diabetes subtype and screening phase that define the pair; `diabetes mellitus` is a broad host member reused in separate diabetes complication groups.
REFUTATION: Independent refutation findings: diabetes mellitus / gestational diabetes screening: The comprehensive ADA sheet substantively covers diabetes in pregnancy, while USPSTF detects gestational diabetes; pregnancy and screening add a subtype and phase within the broader diabetes subject.

### MEMBERS
- diabetes mellitus
- gestational diabetes screening

### EVIDENCE
- diabetes mellitus: Read the catalog row(s) whose topic is diabetes mellitus, followed the artifact binding in coverage.md to [diabetes.md](diabetes.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- gestational diabetes screening: Read the catalog row(s) whose topic is gestational diabetes screening, followed the artifact binding in coverage.md to [gestational-diabetes-screening.md](gestational-diabetes-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: drug-susceptible tuberculosis treatment
DATE: 2026-09-01
ELECTED: drug-susceptible tuberculosis treatment
ELECTION: The treatment key identifies active, drug-susceptible tuberculosis and separates this clique from latent-TB screening, which shares the `tuberculosis diagnosis` member; electing the diagnosis key would collapse those overlapping identities.
REFUTATION: Independent refutation findings: drug-susceptible tuberculosis treatment / tuberculosis diagnosis: The diagnosis guideline substantively establishes active pulmonary and extrapulmonary TB and drug-resistance workup that leads to the drug-susceptible treatment guideline; diagnostic versus therapeutic phase does not split active tuberculosis.

### MEMBERS
- drug-susceptible tuberculosis treatment
- tuberculosis diagnosis

### EVIDENCE
- drug-susceptible tuberculosis treatment: Read the catalog row(s) whose topic is drug-susceptible tuberculosis treatment, followed the artifact binding in coverage.md to [drug-susceptible-tuberculosis-treatment.md](drug-susceptible-tuberculosis-treatment.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- tuberculosis diagnosis: Read the catalog row(s) whose topic is tuberculosis diagnosis, followed the artifact binding in coverage.md to [tuberculosis-diagnosis.md](tuberculosis-diagnosis.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: fracture prevention, vitamin D and calcium supplementation
DATE: 2026-09-01
ELECTED: fracture prevention, vitamin D and calcium supplementation
ELECTION: This key names the common fracture-prevention outcome without making osteoporosis detection a prerequisite and preserves the supplementation branch; the osteoporosis-screening key would narrow the group to one route to fracture prevention.
REFUTATION: Independent refutation findings: fracture prevention, vitamin D and calcium supplementation / osteoporosis screening, fracture prevention: Both USPSTF sheets center on preventing fragility fractures in community-dwelling adults; supplementation versus osteoporosis screening is a preventive-action distinction within the shared fracture-prevention subject.

### MEMBERS
- fracture prevention, vitamin D and calcium supplementation
- osteoporosis screening, fracture prevention

### EVIDENCE
- fracture prevention, vitamin D and calcium supplementation: Read the catalog row(s) whose topic is fracture prevention, vitamin D and calcium supplementation, followed the artifact binding in coverage.md to [fracture-prevention-vitamin-d-and-calcium-supplementation.md](fracture-prevention-vitamin-d-and-calcium-supplementation.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- osteoporosis screening, fracture prevention: Read the catalog row(s) whose topic is osteoporosis screening, fracture prevention, followed the artifact binding in coverage.md to [osteoporosis-screening-and-fracture-prevention.md](osteoporosis-screening-and-fracture-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: heart failure
DATE: 2026-09-01
ELECTED: heart failure
ELECTION: The general disease name is the canonical umbrella for diagnosis and management across populations; `heart failure in chronic kidney disease` is a nested population branch and is separately needed as the key of its CKD intersection clique.
REFUTATION: Independent refutation findings: heart failure / heart failure in chronic kidney disease: The CKD artifact is a scope of work rather than a decision source, but its complete text is substantively and expressly about diagnosis and management of heart failure in CKD; CKD creates nested membership without changing the heart-failure subject.

### MEMBERS
- heart failure
- heart failure in chronic kidney disease

### EVIDENCE
- heart failure: Read the catalog row(s) whose topic is heart failure, followed the artifact binding in coverage.md to [heart-failure.md](heart-failure.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- heart failure in chronic kidney disease: Read the catalog row(s) whose topic is heart failure in chronic kidney disease, followed the artifact binding in coverage.md to [heart-failure-in-chronic-kidney-disease.md](heart-failure-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: hepatitis C screening
DATE: 2026-09-01
ELECTED: hepatitis C screening
ELECTION: Screening is the action substantively shared across the USPSTF, CKD, and infection-management sheets, and this population-neutral key avoids adopting the CKD branch; it also distinguishes the group from the separate CKD-host clique carried by the nested member.
REFUTATION: Independent refutation findings: hepatitis C in chronic kidney disease / hepatitis C screening: The KDIGO sheet includes HCV detection and screening in CKD and dialysis populations, while USPSTF covers population screening generally; CKD is a nested population within the HCV subject. hepatitis C in chronic kidney disease / hepatitis C virus infection: Both sheets substantively diagnose and treat HCV infection; KDIGO adds renal-stage, dialysis, and transplant branches and therefore retains both HCV and CKD memberships. hepatitis C screening / hepatitis C virus infection: The USPSTF sheet detects HCV infection and the AASLD-IDSA sheet tests, stages, and treats that same infection; screening and management phases support one HCV subject.

### MEMBERS
- hepatitis C in chronic kidney disease
- hepatitis C screening
- hepatitis C virus infection

### EVIDENCE
- hepatitis C in chronic kidney disease: Read the catalog row(s) whose topic is hepatitis C in chronic kidney disease, followed the artifact binding in coverage.md to [hepatitis-c-in-chronic-kidney-disease.md](hepatitis-c-in-chronic-kidney-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- hepatitis C screening: Read the catalog row(s) whose topic is hepatitis C screening, followed the artifact binding in coverage.md to [hepatitis-c-screening.md](hepatitis-c-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- hepatitis C virus infection: Read the catalog row(s) whose topic is hepatitis C virus infection, followed the artifact binding in coverage.md to [hepatitis-c-virus-infection.md](hepatitis-c-virus-infection.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: high body mass index intervention
DATE: 2026-09-01
ELECTED: high body mass index intervention
ELECTION: This wording accommodates pediatric percentile-based eligibility and adult BMI-defined obesity without imposing the adult `obesity` label on every population; the alternative also narrows the intervention to behavioral weight loss.
REFUTATION: Independent refutation findings: high body mass index intervention / obesity, behavioral weight loss intervention: Both USPSTF sheets prescribe intensive behavioral weight-management interventions for elevated BMI/obesity, separated primarily by pediatric versus adult population wording.

### MEMBERS
- high body mass index intervention
- obesity, behavioral weight loss intervention

### EVIDENCE
- high body mass index intervention: Read the catalog row(s) whose topic is high body mass index intervention, followed the artifact binding in coverage.md to [high-body-mass-index-intervention.md](high-body-mass-index-intervention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- obesity, behavioral weight loss intervention: Read the catalog row(s) whose topic is obesity, behavioral weight loss intervention, followed the artifact binding in coverage.md to [obesity-behavioral-weight-loss-intervention.md](obesity-behavioral-weight-loss-intervention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: hypertensive disorders of pregnancy screening
DATE: 2026-09-01
ELECTED: hypertensive disorders of pregnancy screening
ELECTION: The broader pregnancy-specific syndrome key includes preeclampsia alongside other hypertensive disorders and their detection; the low-dose-aspirin member names one preventive intervention for one disorder within that scope.
REFUTATION: Independent refutation findings: hypertensive disorders of pregnancy screening / preeclampsia prevention, low-dose aspirin: Preeclampsia is a substantive hypertensive disorder of pregnancy in the screening sheet, and both statements govern detection or prevention of that pregnancy-specific condition; the broader screening sheet legitimately has nested membership.

### MEMBERS
- hypertensive disorders of pregnancy screening
- preeclampsia prevention, low-dose aspirin

### EVIDENCE
- hypertensive disorders of pregnancy screening: Read the catalog row(s) whose topic is hypertensive disorders of pregnancy screening, followed the artifact binding in coverage.md to [hypertensive-disorders-of-pregnancy-screening.md](hypertensive-disorders-of-pregnancy-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- preeclampsia prevention, low-dose aspirin: Read the catalog row(s) whose topic is preeclampsia prevention, low-dose aspirin, followed the artifact binding in coverage.md to [preeclampsia-prevention-low-dose-aspirin.md](preeclampsia-prevention-low-dose-aspirin.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: illicit drug use prevention
DATE: 2026-09-01
ELECTED: illicit drug use prevention
ELECTION: The prevention key spans children, adolescents, young adults, and pregnancy, giving the group a life-course anchor; `unhealthy drug use screening` is centered on adult question-based case finding and is narrower in both population and action.
REFUTATION: Independent refutation findings: illicit drug use prevention / unhealthy drug use screening: Both USPSTF statements address primary-care prevention or detection of nonmedical drug use, with age and pregnancy branches and a prevention-versus-screening distinction rather than different substances or conditions.

### MEMBERS
- illicit drug use prevention
- unhealthy drug use screening

### EVIDENCE
- illicit drug use prevention: Read the catalog row(s) whose topic is illicit drug use prevention, followed the artifact binding in coverage.md to [illicit-drug-use-prevention.md](illicit-drug-use-prevention.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- unhealthy drug use screening: Read the catalog row(s) whose topic is unhealthy drug use screening, followed the artifact binding in coverage.md to [unhealthy-drug-use-screening.md](unhealthy-drug-use-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: iron deficiency anemia screening
DATE: 2026-09-01
ELECTED: iron deficiency anemia screening
ELECTION: Screening for iron deficiency anemia is the common action across the pediatric and pregnancy statements; the longer alternative adds pregnancy-specific supplementation, so it is not the neutral key for the cross-population group.
REFUTATION: Independent refutation findings: iron deficiency anemia screening / iron deficiency anemia screening and supplementation: Both USPSTF sheets address detection of iron deficiency anemia, with young children versus pregnancy and added maternal iron supplementation as population and intervention branches.

### MEMBERS
- iron deficiency anemia screening
- iron deficiency anemia screening and supplementation

### EVIDENCE
- iron deficiency anemia screening: Read the catalog row(s) whose topic is iron deficiency anemia screening, followed the artifact binding in coverage.md to [iron-deficiency-anemia-screening.md](iron-deficiency-anemia-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- iron deficiency anemia screening and supplementation: Read the catalog row(s) whose topic is iron deficiency anemia screening and supplementation, followed the artifact binding in coverage.md to [iron-deficiency-anemia-screening-and-supplementation.md](iron-deficiency-anemia-screening-and-supplementation.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: kidney transplant recipient care
DATE: 2026-09-01
ELECTED: kidney transplant recipient care
ELECTION: Recipient care names the transplant state that candidate evaluation is intended to reach and continues through postoperative management; the candidate key would confine the group to the pretransplant phase.
REFUTATION: Independent refutation findings: kidney transplant recipient care / kidney transplantation candidate evaluation: The complete KDIGO sheets govern successive pretransplant-candidate and posttransplant-recipient phases for the kidney transplant patient, with substantive continuity in eligibility, risk evaluation, and recipient management.

### MEMBERS
- kidney transplant recipient care
- kidney transplantation candidate evaluation

### EVIDENCE
- kidney transplant recipient care: Read the catalog row(s) whose topic is kidney transplant recipient care, followed the artifact binding in coverage.md to [kidney-transplant-recipient-care.md](kidney-transplant-recipient-care.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- kidney transplantation candidate evaluation: Read the catalog row(s) whose topic is kidney transplantation candidate evaluation, followed the artifact binding in coverage.md to [kidney-transplantation-candidate-evaluation.md](kidney-transplantation-candidate-evaluation.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: latent tuberculosis infection screening
DATE: 2026-09-01
ELECTED: latent tuberculosis infection screening
ELECTION: This key explicitly identifies latent infection and preserves the clique's distinction from active drug-susceptible tuberculosis treatment; `tuberculosis diagnosis` participates in both groups and cannot uniquely key either overlap.
REFUTATION: Independent refutation findings: latent tuberculosis infection screening / tuberculosis diagnosis: The diagnosis guideline substantively covers TST and IGRA evaluation, interpretation, and exclusion of active disease, while USPSTF covers case finding for latent infection; both share the latent-TB diagnostic subject.

### MEMBERS
- latent tuberculosis infection screening
- tuberculosis diagnosis

### EVIDENCE
- latent tuberculosis infection screening: Read the catalog row(s) whose topic is latent tuberculosis infection screening, followed the artifact binding in coverage.md to [latent-tuberculosis-infection-screening.md](latent-tuberculosis-infection-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- tuberculosis diagnosis: Read the catalog row(s) whose topic is tuberculosis diagnosis, followed the artifact binding in coverage.md to [tuberculosis-diagnosis.md](tuberculosis-diagnosis.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: lower extremity peripheral artery disease
DATE: 2026-09-01
ELECTED: lower extremity peripheral artery disease
ELECTION: The condition-level name covers history, examination, physiologic testing, and management and states the anatomic scope; the ankle-brachial-index screening key is limited to one test and care phase.
REFUTATION: Independent refutation findings: lower extremity peripheral artery disease / peripheral artery disease screening, ankle-brachial index: Both sheets concern lower-extremity PAD and use the ankle-brachial index for detection or evaluation, with screening versus full disease management as the scope difference.

### MEMBERS
- lower extremity peripheral artery disease
- peripheral artery disease screening, ankle-brachial index

### EVIDENCE
- lower extremity peripheral artery disease: Read the catalog row(s) whose topic is lower extremity peripheral artery disease, followed the artifact binding in coverage.md to [lower-extremity-peripheral-artery-disease.md](lower-extremity-peripheral-artery-disease.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- peripheral artery disease screening, ankle-brachial index: Read the catalog row(s) whose topic is peripheral artery disease screening, ankle-brachial index, followed the artifact binding in coverage.md to [peripheral-artery-disease-screening-ankle-brachial-index.md](peripheral-artery-disease-screening-ankle-brachial-index.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: skin cancer prevention counseling
DATE: 2026-09-01
ELECTED: skin cancer prevention counseling
ELECTION: The counseling key carries the affirmative UV-risk-reduction intervention across a wider age span, whereas `skin cancer screening` names a single visual-examination question with an insufficient-evidence conclusion.
REFUTATION: Independent refutation findings: skin cancer prevention counseling / skin cancer screening: Both USPSTF sheets address prevention or early detection of skin cancer in asymptomatic populations, with UV-risk counseling versus visual screening as distinct preventive actions.

### MEMBERS
- skin cancer prevention counseling
- skin cancer screening

### EVIDENCE
- skin cancer prevention counseling: Read the catalog row(s) whose topic is skin cancer prevention counseling, followed the artifact binding in coverage.md to [skin-cancer-prevention-counseling.md](skin-cancer-prevention-counseling.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- skin cancer screening: Read the catalog row(s) whose topic is skin cancer screening, followed the artifact binding in coverage.md to [skin-cancer-screening.md](skin-cancer-screening.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.

## SUBJECT: tobacco smoking cessation
DATE: 2026-09-01
ELECTED: tobacco smoking cessation
ELECTION: This key anchors the established-use treatment pathway with behavioral and pharmacologic cessation actions, while `tobacco use prevention and cessation` is the youth-focused source whose principal affirmative action is preventing initiation.
REFUTATION: Independent refutation findings: tobacco smoking cessation / tobacco use prevention and cessation: Both USPSTF sheets address preventing or stopping tobacco use, with adults and pregnancy versus children and adolescents as population branches.

### MEMBERS
- tobacco smoking cessation
- tobacco use prevention and cessation

### EVIDENCE
- tobacco smoking cessation: Read the catalog row(s) whose topic is tobacco smoking cessation, followed the artifact binding in coverage.md to [tobacco-smoking-cessation.md](tobacco-smoking-cessation.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
- tobacco use prevention and cessation: Read the catalog row(s) whose topic is tobacco use prevention and cessation, followed the artifact binding in coverage.md to [tobacco-use-prevention-and-cessation.md](tobacco-use-prevention-and-cessation.md), and read that complete threshold sheet; the catalog wording and the sheet's clinical decision scope substantiate this member's inclusion in the elected subject.
