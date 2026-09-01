# Community-acquired pneumonia — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ats-idsa-2019 | ATS/IDSA | IDSA/ajrccm_200_7_e45 | guideline | 2019 guideline | 2019-10-01 | https://doi.org/10.1164/rccm.201908-1581ST | stated | bound |

## Scope

**Read:** all 23 source pages, including every table, figure, recommendation,
evidence summary, rationale, implementation consideration, article-information
section, disclosure, and reference page. The bound recommendation artifact contains
48 marker occurrences.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| title, abstract, introduction, methods, and overview | 1-2 | read 2026-08-31; blind 2026-08-31 |
| microbiological diagnosis and severe-CAP criteria | 3-5 | yes |
| viral testing, biomarkers, and outpatient regimens | 6-10 | yes |
| inpatient regimens, aspiration, and resistant-pathogen risk | 11-13 | yes |
| corticosteroids, influenza therapy, duration, and follow-up imaging | 14-16 | yes |
| article information, disclosures, and references | 17-23 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults-cap-severity-assessment | adults with community-acquired pneumonia being assessed for severe CAP |
| hospitalized-cap-recent-parenteral-antibiotics | hospitalized adults with CAP who were hospitalized and received parenteral antibiotics in the last 90 days |
| adults-cap-site-of-care | adults diagnosed with CAP whose initial treatment site is being determined |
| healthy-outpatient-cap | healthy outpatient adults without comorbidities or risk factors for antibiotic-resistant pathogens |
| healthy-outpatient-low-macrolide-resistance | healthy outpatient adults without comorbidities or risk factors for antibiotic-resistant pathogens in areas with pneumococcal resistance to macrolides less than 25% |
| comorbid-outpatient-cap | outpatient adults with comorbidities |
| healthy-outpatient-doxycycline | healthy outpatient adults with CAP for whom doxycycline is selected |
| nonsevere-inpatient-standard | inpatient adults with nonsevere CAP without risk factors for MRSA or Pseudomonas aeruginosa |
| severe-inpatient-standard | inpatient adults with severe CAP without risk factors for MRSA or Pseudomonas aeruginosa |
| inpatient-macrolide-fluoro-contraindicated | inpatient adults with nonsevere CAP who have contraindications to both macrolides and fluoroquinolones |
| inpatient-cap-mrsa-risk | inpatient adults with CAP who have locally validated risk factors for MRSA |
| inpatient-cap-pseudomonas-risk | inpatient adults with CAP who have locally validated risk factors for Pseudomonas aeruginosa |
| aspiration-pneumonitis | patients who have aspiration pneumonitis |
| cap-prior-mrsa-pseudomonas-isolation | adults with CAP and prior respiratory tract isolation of MRSA or Pseudomonas aeruginosa within the prior year |
| cap-recent-hospital-parenteral | adults with CAP who were hospitalized and received parenteral antibiotics in the last 90 days |
| influenza-positive-inpatient-cap | adults with CAP who test positive for influenza in the inpatient setting |
| influenza-positive-outpatient-cap | adults with CAP who test positive for influenza in the outpatient setting |
| influenza-positive-cap-early-stable | adults with CAP, a positive influenza test, no evidence of a bacterial pathogen, and early clinical stability |
| improving-cap | adults with CAP improving toward clinical stability |
| cap-unstable-day-five | adults with CAP who fail to achieve clinical stability within 5 days |
| cap-mrsa-pseudomonas | adults with CAP due to suspected or proven MRSA or Pseudomonas aeruginosa |
| resolved-cap | adults with CAP whose symptoms have resolved within 5 to 7 days |

## Quantities

| key | verbatim |
| --- | --- |
| severe-cap-count | one major criterion or three or more minor criteria |
| severe-cap-minor-thresholds | respiratory rate, oxygenation ratio, blood urea nitrogen, white blood cell count, platelet count, and core temperature thresholds |
| sputum-culture-risk-window | hospitalization and receipt of parenteral antibiotics in the last 90 days |
| blood-culture-risk-window | hospitalization and receipt of parenteral antibiotics in the last 90 days |
| curb65-age-component | age component of CURB-65 |
| psi-sbp-component | systolic blood pressure interpreted as abnormal in the Pneumonia Severity Index |
| healthy-outpatient-amoxicillin | outpatient amoxicillin regimen |
| healthy-outpatient-doxycycline | outpatient doxycycline regimen |
| healthy-outpatient-macrolide | outpatient macrolide regimens |
| macrolide-resistance-threshold | local pneumococcal resistance threshold for macrolide monotherapy |
| comorbid-outpatient-beta-lactam-combination | outpatient beta-lactam plus macrolide or doxycycline regimens |
| comorbid-outpatient-fluoroquinolone | outpatient respiratory fluoroquinolone regimens |
| expert-doxycycline-loading | optional first doxycycline dose described by some experts |
| nonsevere-inpatient-beta-lactam-macrolide | inpatient beta-lactam plus macrolide regimens |
| nonsevere-inpatient-fluoroquinolone | inpatient respiratory fluoroquinolone monotherapy regimens |
| nonsevere-inpatient-beta-lactam-doxycycline | inpatient beta-lactam plus doxycycline regimen |
| severe-inpatient-beta-lactam-macrolide | severe inpatient beta-lactam plus macrolide regimens |
| severe-inpatient-beta-lactam-fluoroquinolone | severe inpatient beta-lactam plus respiratory fluoroquinolone regimens |
| mrsa-empiric-regimen | empiric MRSA regimens |
| pseudomonas-empiric-regimen | empiric Pseudomonas aeruginosa regimens |
| aspiration-pneumonitis-resolution | expected resolution without antibiotic therapy |
| prior-isolation-window | prior respiratory isolation window triggering cultures and empiric coverage |
| recent-hospitalization-coverage-window | hospitalization and parenteral antibiotic window used with severity to select testing and empiric coverage |
| resistant-pathogen-deescalation-time | culture-guided deescalation time when clinically improving |
| influenza-antiviral-timing | timing of influenza antiviral benefit |
| influenza-antibacterial-stop-time | time to consider stopping antibacterial therapy when early stable and without bacterial evidence |
| cap-minimum-antibiotic-duration | minimum total antibiotic duration after stability assessment |
| clinical-stability-failure-time | time without stability prompting reassessment |
| mrsa-pseudomonas-duration | antibiotic duration for CAP due to MRSA or Pseudomonas aeruginosa |
| followup-imaging-resolution-window | symptom-resolution window after which routine follow-up chest imaging is not suggested |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| severe-cap-count | adults-cap-severity-assessment | one major criterion or three or more minor criteria | RENDERED: Validated definition includes either one major criterion or three or more minor criteria | ats-idsa-2019 | 4 | p4/narrative/table-1-definition | narrative |
| severe-cap-minor-thresholds | adults-cap-severity-assessment | respiratory rate >=30 breaths/min; PaO2/FiO2 <=250; BUN >=20 mg/dL; WBC <4,000 cells/µL; platelets <100,000/µL; core temperature <36°C | RENDERED: Respiratory rate ≥30 breaths/min PaO2/FiO2 ratio ≤250 Blood urea nitrogen level ≥20 mg/dl Leukopenia (white blood cell count <4,000 cells/µl) Thrombocytopenia (platelet count <100,000/µl) Hypothermia (core temperature <36°C) | ats-idsa-2019 | 4 | p4/narrative/table-1 | narrative |
| sputum-culture-risk-window | hospitalized-cap-recent-parenteral-antibiotics | last 90 days | were hospitalized and received parenteral antibiotics, whether during the hospitalization event or not, in the last 90 days | ats-idsa-2019 | 3 | p3/grade-spelled-out/5 | strong recommendation and very low quality of evidence |
| blood-culture-risk-window | hospitalized-cap-recent-parenteral-antibiotics | last 90 days | were hospitalized and received parenteral antibiotics, whether during the hospitalization event or not, in the last 90 days | ats-idsa-2019 | 4 | p4/grade-spelled-out/6 | strong recommendation and very low quality of evidence |
| curb65-age-component | adults-cap-site-of-care | age >=65 years | RENDERED: CURB-65 (tool based on confusion, urea level, respiratory rate, blood pressure, and age ≥65) | ats-idsa-2019 | 8 | p8/grade-spelled-out/2 | conditional recommendation and low quality of evidence |
| psi-sbp-component | adults-cap-site-of-care | systolic blood pressure <90 mmHg is abnormal | RENDERED: all systolic blood pressures <90 mm Hg are considered abnormal | ats-idsa-2019 | 8 | p8/narrative/1 | narrative |
| healthy-outpatient-amoxicillin | healthy-outpatient-cap | amoxicillin 1 g three times daily | RENDERED: Amoxicillin 1 g three times daily | ats-idsa-2019 | 9 | p9/grade-spelled-out/2 | strong recommendation and moderate quality of evidence |
| healthy-outpatient-doxycycline | healthy-outpatient-cap | doxycycline 100 mg twice daily | RENDERED: Doxycycline 100 mg twice daily | ats-idsa-2019 | 9 | p9/grade-spelled-out/3 | conditional recommendation and low quality of evidence |
| healthy-outpatient-macrolide | healthy-outpatient-low-macrolide-resistance | azithromycin 500 mg first day then 250 mg daily; clarithromycin 500 mg twice daily; or clarithromycin ER 1,000 mg daily | RENDERED: azithromycin 500 mg on first day then 250 mg daily clarithromycin 500 mg twice daily or extended release 1,000 mg daily | ats-idsa-2019 | 9 | p9/grade-spelled-out/4 | conditional recommendation and moderate quality of evidence |
| macrolide-resistance-threshold | healthy-outpatient-low-macrolide-resistance | local pneumococcal macrolide resistance <25% | RENDERED: macrolide if local pneumococcal resistance is <25% | ats-idsa-2019 | 9 | p9/grade-spelled-out/4 | conditional recommendation and moderate quality of evidence |
| comorbid-outpatient-beta-lactam-combination | comorbid-outpatient-cap | amoxicillin/clavulanate 500/125 mg three times daily, 875/125 mg twice daily, or 2,000/125 mg twice daily; or cefpodoxime 200 mg twice daily or cefuroxime 500 mg twice daily; plus azithromycin 500 mg first day then 250 mg daily, clarithromycin 500 mg twice daily, clarithromycin ER 1,000 mg daily, or doxycycline 100 mg twice daily | RENDERED: amoxicillin/clavulanate 500 mg/125 mg three times daily 875 mg/125 mg twice daily 2,000 mg/125 mg twice daily cefpodoxime 200 mg twice daily cefuroxime 500 mg twice daily AND azithromycin 500 mg on first day then 250 mg daily clarithromycin 500 mg twice daily extended release 1,000 mg daily or doxycycline 100 mg twice daily | ats-idsa-2019 | 9 | p9/grade-spelled-out/6 | strong recommendation and moderate quality of evidence for macrolide combination therapy; conditional recommendation and low quality of evidence for doxycycline combination therapy |
| comorbid-outpatient-fluoroquinolone | comorbid-outpatient-cap | levofloxacin 750 mg daily, moxifloxacin 400 mg daily, or gemifloxacin 320 mg daily | RENDERED: levofloxacin 750 mg daily moxifloxacin 400 mg daily or gemifloxacin 320 mg daily | ats-idsa-2019 | 9 | p9/grade-spelled-out/7 | strong recommendation and moderate quality of evidence |
| expert-doxycycline-loading | healthy-outpatient-doxycycline | some experts advise first dose 200 mg; no data demonstrate improved outcomes | RENDERED: Some experts recommend that the first dose of oral doxycycline be 200 mg, to achieve adequate serum levels more rapidly. There are no data documenting improved outcomes with this approach. | ats-idsa-2019 | 10 | p10/narrative/1 | narrative |
| nonsevere-inpatient-beta-lactam-macrolide | nonsevere-inpatient-standard | ampicillin/sulbactam 1.5-3 g every 6 hours, cefotaxime 1-2 g every 8 hours, ceftriaxone 1-2 g daily, or ceftaroline 600 mg every 12 hours; plus azithromycin 500 mg daily or clarithromycin 500 mg twice daily | RENDERED: ampicillin + sulbactam 1.5–3 g every 6 h cefotaxime 1–2 g every 8 h ceftriaxone 1–2 g daily ceftaroline 600 mg every 12 h AND azithromycin 500 mg daily or clarithromycin 500 mg twice daily | ats-idsa-2019 | 11 | p11/grade-spelled-out/1 | strong recommendation and high quality of evidence |
| nonsevere-inpatient-fluoroquinolone | nonsevere-inpatient-standard | levofloxacin 750 mg daily or moxifloxacin 400 mg daily | RENDERED: Levofloxacin 750 mg daily or moxifloxacin 400 mg daily | ats-idsa-2019 | 11 | p11/grade-spelled-out/2 | strong recommendation and high quality of evidence |
| nonsevere-inpatient-beta-lactam-doxycycline | inpatient-macrolide-fluoro-contraindicated | beta-lactam doses above plus doxycycline 100 mg twice daily | RENDERED: A third option for adults with CAP who have contraindications to both macrolides and fluoroquinolones is combination therapy with a beta-lactam and doxycycline 100 mg twice daily | ats-idsa-2019 | 11 | p11/narrative/1 | narrative |
| severe-inpatient-beta-lactam-macrolide | severe-inpatient-standard | beta-lactam doses above plus azithromycin 500 mg daily or clarithromycin 500 mg twice daily | RENDERED: Severe inpatient pneumonia β-Lactam + macrolide ampicillin + sulbactam 1.5–3 g every 6 h cefotaxime 1–2 g every 8 h ceftriaxone 1–2 g daily ceftaroline 600 mg every 12 h azithromycin 500 mg daily clarithromycin 500 mg twice daily | ats-idsa-2019 | 11 | p11/grade-spelled-out/4 | strong recommendation and moderate quality of evidence |
| severe-inpatient-beta-lactam-fluoroquinolone | severe-inpatient-standard | beta-lactam doses above plus levofloxacin 750 mg daily or moxifloxacin 400 mg daily | RENDERED: Severe inpatient pneumonia β-Lactam + fluoroquinolone levofloxacin 750 mg daily or moxifloxacin 400 mg daily | ats-idsa-2019 | 11 | p11/grade-spelled-out/5 | strong recommendation and low quality of evidence |
| mrsa-empiric-regimen | inpatient-cap-mrsa-risk | vancomycin 15 mg/kg every 12 hours adjusted by levels or linezolid 600 mg every 12 hours | RENDERED: MRSA vancomycin 15 mg/kg every 12 h adjust based on levels or linezolid 600 mg every 12 h | ats-idsa-2019 | 7 | p7/narrative/table-4-mrsa-regimens | narrative |
| pseudomonas-empiric-regimen | inpatient-cap-pseudomonas-risk | piperacillin/tazobactam 4.5 g every 6 hours, cefepime 2 g every 8 hours, ceftazidime 2 g every 8 hours, imipenem 500 mg every 6 hours, meropenem 1 g every 8 hours, or aztreonam 2 g every 8 hours | RENDERED: P. aeruginosa piperacillin + tazobactam 4.5 g every 6 h cefepime 2 g every 8 h ceftazidime 2 g every 8 h imipenem 500 mg every 6 h meropenem 1 g every 8 h or aztreonam 2 g every 8 h | ats-idsa-2019 | 7 | p7/narrative/table-4-pseudomonas-regimens | narrative |
| aspiration-pneumonitis-resolution | aspiration-pneumonitis | 24-48 hours | RENDERED: Patients who have aspiration pneumonitis typically have resolution of symptoms within 24 to 48 hours and require only supportive treatment, without antibiotics | ats-idsa-2019 | 12 | p12/narrative/1 | narrative |
| prior-isolation-window | cap-prior-mrsa-pseudomonas-isolation | prior year | RENDERED: prior identification of MRSA or P. aeruginosa in the respiratory tract within the prior year predicts a very high risk of these pathogens being identified in patients presenting with CAP | ats-idsa-2019 | 13 | p13/narrative/1 | narrative |
| recent-hospitalization-coverage-window | cap-recent-hospital-parenteral | last 90 days; nonsevere: test without empiric extended-spectrum therapy; severe: test plus empiric extended-spectrum therapy | RENDERED: hospitalization and parenteral antibiotic exposure in the last 90 days In patients with recent hospitalization and exposure to parenteral antibiotics, we recommend microbiological testing without empiric extended-spectrum therapy for treatment of nonsevere CAP and microbiological testing with extended-spectrum empiric therapy for treatment of severe CAP | ats-idsa-2019 | 13 | p13/narrative/2 | narrative |
| resistant-pathogen-deescalation-time | cap-prior-mrsa-pseudomonas-isolation | deescalate at 48 hours if cultures negative | RENDERED: empiric therapy for these pathogens in patients with CAP in addition to coverage for standard CAP pathogens, with deescalation at 48 hours if cultures are negative | ats-idsa-2019 | 13 | p13/narrative/3 | narrative |
| resistant-pathogen-deescalation-time | cap-recent-hospital-parenteral | deescalate at 48 hours if cultures negative and patient improving | RENDERED: deescalation at 48 hours if cultures are negative and the patient is improving | ats-idsa-2019 | 13 | p13/narrative/4 | narrative |
| influenza-antiviral-timing | influenza-positive-inpatient-cap | prescribe regardless of illness duration; greatest benefit within 48 hours, with evidence supporting later initiation | RENDERED: Although benefits are strongest when therapy is started within 48 hours of symptoms, studies also support later initiation of therapy | ats-idsa-2019 | 14 | p14/narrative/1 | narrative |
| influenza-antiviral-timing | influenza-positive-outpatient-cap | prescribe regardless of illness duration; greatest benefit within 48 hours, with evidence of benefit up to 4-5 days | RENDERED: benefits are strongest when therapy is started within 48 hours of symptoms, but there may be benefits up to 4 or 5 days after symptoms begin | ats-idsa-2019 | 14 | p14/narrative/2 | narrative |
| influenza-antibacterial-stop-time | influenza-positive-cap-early-stable | consider discontinuation at 48-72 hours | RENDERED: in patients with CAP, a positive influenza test, no evidence of a bacterial pathogen, and early clinical stability, consideration could be given to earlier discontinuation of antibiotic treatment at 48 to 72 hours | ats-idsa-2019 | 15 | p15/narrative/1 | narrative |
| cap-minimum-antibiotic-duration | improving-cap | >=5 total days and until clinically stable | antibiotic therapy should be continued until the patient achieves stability and for no less than a total of 5 days | ats-idsa-2019 | 15 | p15/grade-spelled-out/2 | strong recommendation and moderate quality of evidence |
| clinical-stability-failure-time | cap-unstable-day-five | no stability within 5 days | Failure to achieve clinical stability within 5 days is associated with higher mortality and worse clinical outcomes | ats-idsa-2019 | 15 | p15/narrative/2 | narrative |
| mrsa-pseudomonas-duration | cap-mrsa-pseudomonas | 7 days | We believe that the duration of therapy for CAP due to suspected or proven MRSA or P. aeruginosa should be 7 days | ats-idsa-2019 | 16 | p16/narrative/1 | narrative |
| followup-imaging-resolution-window | resolved-cap | symptoms resolved within 5-7 days: do not routinely obtain follow-up chest imaging | In adults with CAP whose symptoms have resolved within 5 to 7 days, we suggest not routinely obtaining follow-up chest imaging | ats-idsa-2019 | 16 | p16/grade-spelled-out/1 | conditional recommendation and low quality of evidence |

## Conflicts

No conflicts. Alternative antimicrobial regimens are choices within one recommendation,
not contradictory thresholds. Testing and empiric-coverage branches use distinct
severity and risk-factor populations.

## Coverage

The bound recommendation record contains 48 markers: 14 are cited by threshold rows
above and 34 are explicitly dispositioned below. Narrative and rendered rows account
for action-bearing numbers not represented by recommendation markers.

- `p3/grade-spelled-out/1` - scoped out because it is a qualitative recommendation against routine sputum culture.
- `p3/grade-spelled-out/2` - scoped out because its severe-CAP action is qualitative; the numeric severe-CAP definition is retained from Table 1.
- `p3/grade-spelled-out/3` - scoped out because its MRSA/Pseudomonas culture action is qualitative; the numeric risk windows are retained separately.
- `p3/grade-spelled-out/4` - scoped out because its empiric-coverage branch is qualitative; its numeric risk window is retained separately.
- `p4/grade-spelled-out/1` - scoped out because it is a qualitative recommendation against routine blood culture.
- `p4/grade-spelled-out/2` - scoped out because its severe-CAP action is qualitative; the numeric severe-CAP definition is retained from Table 1.
- `p4/grade-spelled-out/3` - scoped out because its MRSA/Pseudomonas culture action is qualitative; the numeric risk windows are retained separately.
- `p4/grade-spelled-out/4` - scoped out because its empiric-coverage branch is qualitative; its numeric risk window is retained separately.
- `p4/grade-spelled-out/5` - scoped out because its empiric-coverage branch is qualitative; its numeric risk window is retained separately.
- `p5/grade-spelled-out/1` - scoped out because it is a qualitative recommendation against routine pneumococcal urinary antigen testing.
- `p5/grade-spelled-out/2` - scoped out because it is a qualitative severe-CAP exception to urinary antigen testing.
- `p5/grade-spelled-out/3` - scoped out because it is a qualitative recommendation against routine Legionella urinary antigen testing.
- `p5/grade-spelled-out/4` - scoped out because it is a qualitative epidemiologic exception to Legionella testing.
- `p5/grade-spelled-out/5` - scoped out because it is a qualitative severe-CAP exception to Legionella testing.
- `p5/grade-spelled-out/6` - scoped out because it is a qualitative action to obtain lower-respiratory-tract material.
- `p6/grade-spelled-out/1` - scoped out because the influenza-testing recommendation contains no numeric patient-action decision point.
- `p6/grade-spelled-out/2` - scoped out because antibiotics are recommended regardless of the initial procalcitonin level; proposed cutoffs are evidence-only and explicitly not adequate to withhold therapy.
- `p8/grade-spelled-out/1` - scoped out because the PSI preference is qualitative; its numeric blood-pressure component is retained from the rationale.
- `p8/grade-spelled-out/3` - scoped out because the direct-ICU recommendation is qualitative; the numeric severe-CAP criteria are retained from Table 1.
- `p9/grade-spelled-out/1` - scoped out because it introduces the outpatient population; the actionable regimen doses are retained in the following records.
- `p9/grade-spelled-out/5` - scoped out because its beta-lactam and macrolide doses are retained in the following cumulative combination-therapy record.
- `p10/recommendation/9.1` - scoped out because it is the page-break continuation marker for the outpatient-regimen question; its doses are retained from Table 3 and the recommendation records.
- `p11/recommendation/9.2` - scoped out because it introduces the severe-inpatient branch; its regimen doses are retained from Table 4.
- `p11/grade-spelled-out/3` - scoped out because its dose-bearing option is retained through a page-bound narrative row.
- `p12/grade-spelled-out/1` - scoped out because the recommendation against routine anaerobic coverage is qualitative; the 24-48-hour aspiration-pneumonitis course is retained from the rationale.
- `p12/grade-spelled-out/2` - scoped out because the former HCAP category is abandoned; its historical hospitalization definition is not a current action threshold.
- `p12/grade-spelled-out/3` - scoped out because its empiric-coverage recommendation is qualitative; the MRSA and Pseudomonas regimen doses are retained separately from rendered Table 4.
- `p12/grade-spelled-out/4` - scoped out because “the first few days” is not an exact threshold; the explicit 48-hour deescalation action is retained from the rationale.
- `p14/grade-spelled-out/1` - scoped out because the recommendation against routine corticosteroids in nonsevere CAP is qualitative; study exposure doses are evidence, not prescribed regimens.
- `p14/grade-spelled-out/2` - scoped out because the recommendation against routine corticosteroids in severe CAP is qualitative; study exposure doses are evidence, not prescribed regimens.
- `p14/grade-spelled-out/3` - scoped out because the corticosteroid recommendation for refractory septic shock is qualitative.
- `p14/grade-spelled-out/4` - scoped out because inpatient antiviral treatment is recommended regardless of illness duration; the quantified evidence timing is retained from the rationale.
- `p14/grade-spelled-out/5` - scoped out because outpatient antiviral treatment is recommended regardless of illness duration; the quantified evidence timing is retained from the rationale.
- `p15/grade-spelled-out/1` - scoped out because starting antibacterial therapy for influenza-positive CAP is qualitative; the quantified early-discontinuation branch is retained from the rationale.

ADR 0009 disposition: all numeric patient-action doses, intervals, resistance
cutoffs, risk windows, reassessment times, duration floors, and imaging windows were
retained. Epidemiologic rates, diagnostic-performance estimates, outcome effect
sizes, study enrollment criteria, trial-only follow-up schedules, historical HCAP
definitions, proposed procalcitonin cutoffs that the guideline rejects for withholding
therapy, and corticosteroid exposures reported only as evidence were scoped out.
