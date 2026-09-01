# COVID-19 treatment — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the source** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2022 | IDSA | IDSA/ciac724 | guideline | September 2022 | 2022 | https://doi.org/10.1093/cid/ciac724 | stated | bound |

## Scope

**Read:** all 100 pages, including every recommendation, remark, table, figure, treatment section, pediatric discussion, disclosure, and reference page. The spans below account for the complete document.

**Not read:** nothing. Spans without a retained numeric patient-action decision point carry completed first-read and blind markers. Reference-only pages are exempt.

| span | pages | read |
| --- | --- | --- |
| title, abstract, executive recommendations, definitions, and methods | 1-9 | yes |
| hydroxychloroquine and lopinavir/ritonavir | 10-21 | read 2026-08-31; blind 2026-08-31 |
| repeated systemic-glucocorticoid recommendations | 22 | yes |
| systemic-glucocorticoid evidence and inhaled corticosteroids | 23-28 | read 2026-08-31; blind 2026-08-31 |
| interleukin-6 inhibitors through remdesivir | 29-43 | yes |
| famotidine, neutralizing antibodies, and convalescent plasma | 44-59 | yes |
| repeated baricitinib regimen and JAK-inhibitor evidence | 60 | yes |
| JAK-inhibitor evidence through fluvoxamine | 61-75 | read 2026-08-31; blind 2026-08-31 |
| nirmatrelvir/ritonavir, molnupiravir, ivermectin, and colchicine | 76-83 | yes |
| summary figures, pediatric considerations, and MIS-C discussion | 84-90 | yes |
| notes, disclosures, and initial references | 91 | read 2026-08-31; blind 2026-08-31 |
| references | 92-100 | exempt: reference list; no first-read or blind marker required |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 1da6304a8829b3c8c24345992bb26a0048a3455d13af4d1a87576e68723f549c; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| hospitalized-critical-covid | hospitalized critically ill patients with COVID-19 |
| hospitalized-severe-covid | hospitalized patients with severe COVID-19 |
| hospitalized-no-oxygen | hospitalized patients with mild-to-moderate COVID-19 without hypoxemia requiring supplemental oxygen |
| progressive-severe-critical-inflammation | hospitalized adults with progressive severe or critical COVID-19 and elevated systemic inflammatory markers |
| ambulatory-high-risk-no-options | ambulatory patients with mild-to-moderate COVID-19 at high risk for progression and no other treatment options |
| high-risk-mild-moderate-covid | ambulatory or hospitalized patients with mild-to-moderate COVID-19 at high risk for progression |
| hospitalized-oxygen-no-ventilation | patients receiving supplemental oxygen but not mechanical ventilation or ECMO |
| immunocompromised-preexposure | moderately or severely immunocompromised individuals eligible for susceptible-variant preexposure prophylaxis |
| hospitalized-severe-baricitinib | hospitalized adults with severe COVID-19 receiving baricitinib |
| ambulatory-high-risk-nirmatrelvir | ambulatory patients with mild-to-moderate COVID-19 at high risk for progression receiving nirmatrelvir/ritonavir |
| ambulatory-high-risk-molnupiravir | ambulatory adults with mild-to-moderate COVID-19 at high risk for progression, no other options, receiving molnupiravir |
| ambulatory-high-risk-mab | ambulatory patients with mild-to-moderate COVID-19 at high risk for progression receiving an active monoclonal antibody |
| nirmatrelvir-renal | patients receiving nirmatrelvir/ritonavir, stratified by eGFR |
| covid-severity | patients whose COVID-19 severity is being classified |
| ambulatory-remdesivir | high-risk patients with mild-to-moderate COVID-19 receiving the 3-day intravenous remdesivir regimen |
| pediatric-remdesivir | pediatric outpatients considered for remdesivir under the source's 2022 regulatory discussion |
| nirmatrelvir-pediatric | pediatric patients considered for nirmatrelvir/ritonavir under the source's authorization discussion |
| nirmatrelvir-hepatic | patients with hepatic impairment considered for nirmatrelvir/ritonavir |
| molnupiravir-reproductive | patients receiving molnupiravir who could conceive a pregnancy or whose sexual partner could conceive |
| covid-treatment-monitoring | patients receiving COVID-19 treatments listed in the source's monitoring table |
| hospitalized-severe-tocilizumab | hospitalized patients receiving tocilizumab whose treatment monitoring follows the source's Table 41 |
| hospitalized-severe-sarilumab | hospitalized patients receiving sarilumab whose treatment monitoring follows the source's Table 41 |
| pediatric-treatment-age | pediatric patients considered for the source's age-bounded COVID-19 treatments |
| critically-ill-steroid-alternative | critically ill patients receiving a higher dexamethasone dose for another indication or a studied hydrocortisone alternative |

## Quantities

| key | verbatim |
| --- | --- |
| covid-severe-oxygen-threshold | oxygen-saturation definition of severe COVID-19 |
| dexamethasone-regimen | dexamethasone dose, duration, and equivalent glucocorticoid doses |
| tocilizumab-trial-inflammation | systemic-inflammation criterion used in the largest tocilizumab trial |
| convalescent-plasma-window | latest symptom-onset timing for high-titer convalescent plasma |
| remdesivir-start-window | latest symptom-onset timing for remdesivir initiation |
| remdesivir-duration | remdesivir duration on oxygen without ventilation or ECMO |
| tixagevimab-cilgavimab-dose | preexposure prophylaxis dose and injection count |
| baricitinib-regimen | baricitinib dose and maximum duration |
| nirmatrelvir-start-window | latest symptom-onset timing for nirmatrelvir/ritonavir |
| nirmatrelvir-renal-regimen | nirmatrelvir/ritonavir dose and renal boundaries |
| molnupiravir-eligibility-window | adult age and latest symptom-onset timing for molnupiravir |
| molnupiravir-regimen | molnupiravir dose and duration |
| monoclonal-antibody-window | latest symptom-onset timing for an active monoclonal antibody |
| remdesivir-three-day-regimen | outpatient remdesivir loading and subsequent doses |
| remdesivir-renal-boundary | renal boundary for remdesivir use |
| remdesivir-hepatic-stop | aminotransferase threshold for considering remdesivir discontinuation |
| nirmatrelvir-pediatric-eligibility | age and weight authorization boundary for nirmatrelvir/ritonavir |
| nirmatrelvir-hepatic-boundary | Child-Pugh boundary for nirmatrelvir/ritonavir |
| molnupiravir-contraception | contraception period during and after molnupiravir |
| il6-monitoring-cutoffs | hepatic, neutrophil, and platelet precautions for IL-6 inhibitors |
| jak-monitoring-cutoffs | blood-count precautions for JAK inhibitors |
| jak-renal-boundary | renal threshold for baricitinib or tofacitinib dose adjustment |
| pediatric-treatment-age-boundary | age boundary and provenance for selected treatments |
| critical-steroid-other-indication | higher dexamethasone dose for other indications and studied hydrocortisone alternative |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| covid-severe-oxygen-threshold | covid-severity | severe illness: SpO2 <=94% on room air, including supplemental oxygen | RENDERED: "Severe illness is defined as patients with SpO2 ≤94% on room air, including patients on supplemental oxygen." | idsa-2022 | p2 | p2/narrative/severity-definition | narrative |
| dexamethasone-regimen | hospitalized-critical-covid | dexamethasone 6 mg IV or orally daily for 10 days or until discharge; equivalents methylprednisolone 32 mg/day or prednisone 40 mg/day | RENDERED: "Dexamethasone 6 mg IV or orally for 10 days (or until discharge). Equivalent total daily doses are methylprednisolone 32 mg and prednisone 40 mg." | idsa-2022 | p2 | p2/grade-spelled-out/7 | strong recommendation, moderate certainty |
| dexamethasone-regimen | hospitalized-severe-covid | dexamethasone 6 mg IV or orally daily for 10 days or until discharge; equivalents methylprednisolone 32 mg/day or prednisone 40 mg/day | RENDERED: "Dexamethasone 6 mg IV or PO for 10 days (or until discharge). Equivalent total daily doses are methylprednisolone 32 mg and prednisone 40 mg." | idsa-2022 | p2 | p2/grade-spelled-out/8 | conditional recommendation, moderate certainty |
| dexamethasone-regimen | hospitalized-critical-covid | dexamethasone 6 mg IV or orally daily for 10 days or until discharge; equivalents methylprednisolone 32 mg/day or prednisone 40 mg/day | RENDERED: "Dexamethasone 6 mg IV or PO for 10 days (or until discharge); methylprednisolone 32 mg or prednisone 40 mg daily are equivalent" | idsa-2022 | p22 | p22/narrative/critical-dexamethasone-regimen | narrative |
| dexamethasone-regimen | hospitalized-severe-covid | dexamethasone 6 mg IV or orally daily for 10 days or until discharge; equivalents methylprednisolone 32 mg/day or prednisone 40 mg/day | RENDERED: "Dexamethasone 6 mg IV or PO for 10 days (or until discharge); methylprednisolone 32 mg or prednisone 40 mg daily are equivalent" | idsa-2022 | p22 | p22/narrative/severe-dexamethasone-regimen | narrative |
| tocilizumab-trial-inflammation | progressive-severe-critical-inflammation | largest trial criterion CRP >=75 mg/L; trial-derived, not an IDSA eligibility mandate | "criterion for systemic inflammation was defined as C-reactive protein (CRP) ≥75 mg/L" | idsa-2022 | p3 | p3/grade-spelled-out/2 | conditional recommendation, low certainty |
| convalescent-plasma-window | ambulatory-high-risk-no-options | FDA-qualified high-titer COVID-19 convalescent plasma within 8 days of symptom onset | RENDERED: "FDA-qualified high-titer COVID-19 convalescent plasma within 8 days of symptom onset" | idsa-2022 | p3 | p3/grade-spelled-out/4 | conditional recommendation, low certainty |
| remdesivir-start-window | high-risk-mild-moderate-covid | initiate within 7 days of symptom onset | RENDERED: "remdesivir initiated within 7 days of symptom onset" | idsa-2022 | p3 | p3/grade-spelled-out/5 | conditional recommendation, low certainty |
| remdesivir-duration | hospitalized-oxygen-no-ventilation | 5 days rather than 10 days | "treatment with 5 days of remdesivir rather than 10 days" | idsa-2022 | p4 | p4/grade-spelled-out/1 | conditional recommendation, low certainty |
| remdesivir-duration | hospitalized-oxygen-no-ventilation | 5 days rather than 10 days | "treatment with 5 days of remdesivir rather than 10 days" | idsa-2022 | p4 | p4/grade-spelled-out/2 | conditional recommendation, low certainty |
| remdesivir-duration | hospitalized-oxygen-no-ventilation | 5 days rather than 10 days | "treatment with 5 days of remdesivir rather than 10 days" | idsa-2022 | p4 | p4/grade-spelled-out/3 | conditional recommendation, low certainty |
| tixagevimab-cilgavimab-dose | immunocompromised-preexposure | tixagevimab 300 mg plus cilgavimab 300 mg as 2 separate consecutive IM injections once | RENDERED: "300 mg of tixagevimab and 300 mg of cilgavimab administered as 2 separate consecutive intramuscular injections once" | idsa-2022 | p4 | p4/grade-spelled-out/6 | conditional recommendation, low certainty |
| baricitinib-regimen | hospitalized-severe-baricitinib | 4 mg/day or appropriate renal dose for up to 14 days or hospital discharge | RENDERED: "Baricitinib 4 mg/day (or appropriate renal dosing) up to 14 days or until discharge from hospital" | idsa-2022 | p5 | p5/grade-spelled-out/3 | conditional recommendation, moderate certainty |
| nirmatrelvir-start-window | ambulatory-high-risk-nirmatrelvir | initiate within 5 days of symptom onset | RENDERED: "nirmatrelvir/ritonavir initiated within 5 days of symptom onset" | idsa-2022 | p6 | p6/grade-spelled-out/1 | conditional recommendation, low certainty |
| molnupiravir-eligibility-window | ambulatory-high-risk-molnupiravir | age >=18 years and initiate within 5 days of symptom onset | RENDERED: "ambulatory patients (≥18 years) with mild-to-moderate COVID-19" and "molnupiravir initiated within 5 days of symptom onset" | idsa-2022 | p6 | p6/grade-spelled-out/2 | conditional recommendation, low certainty |
| remdesivir-start-window | high-risk-mild-moderate-covid | initiate within 7 days of symptom onset | RENDERED: "remdesivir be initiated within 7 days of symptom onset" | idsa-2022 | p37 | p37/grade-spelled-out/1 | conditional recommendation, low certainty |
| remdesivir-duration | hospitalized-oxygen-no-ventilation | 5 days rather than 10 days | "treatment with 5 days of remdesivir rather than 10 days" | idsa-2022 | p38 | p38/grade-spelled-out/1 | conditional recommendation, low certainty |
| remdesivir-duration | hospitalized-oxygen-no-ventilation | 5 days rather than 10 days | "treatment with 5 days of remdesivir rather than 10 days" | idsa-2022 | p38 | p38/grade-spelled-out/2 | conditional recommendation, low certainty |
| remdesivir-duration | hospitalized-oxygen-no-ventilation | 5 days rather than 10 days | "treatment with 5 days of remdesivir rather than 10 days" | idsa-2022 | p38 | p38/grade-spelled-out/3 | conditional recommendation, low certainty |
| monoclonal-antibody-window | ambulatory-high-risk-mab | administer an active monoclonal antibody within 7 days of symptom onset | RENDERED: "monoclonal antibodies with activity against the predominant regional variants within 7 days of symptom onset" | idsa-2022 | p52 | p52/grade-spelled-out/1 | conditional recommendation, moderate certainty |
| nirmatrelvir-start-window | ambulatory-high-risk-nirmatrelvir | initiate within 5 days of symptom onset | RENDERED: "nirmatrelvir/ritonavir initiated within 5 days of symptom onset" | idsa-2022 | p76 | p76/grade-spelled-out/1 | conditional recommendation, low certainty |
| molnupiravir-eligibility-window | ambulatory-high-risk-molnupiravir | age >=18 years and initiate within 5 days of symptom onset | RENDERED: "ambulatory patients (≥18 years) with mild-to-moderate COVID-19" and "molnupiravir initiated within 5 days of symptom onset" | idsa-2022 | p77 | p77/grade-spelled-out/1 | conditional recommendation, low certainty |
| nirmatrelvir-renal-regimen | nirmatrelvir-renal | eGFR >60: nirmatrelvir 300 mg plus ritonavir 100 mg every 12 hours for 5 days; eGFR 30-60: nirmatrelvir 150 mg plus ritonavir 100 mg every 12 hours for 5 days; eGFR <30: not recommended | RENDERED: "eGFR >60 mL/minute: 300 mg nirmatrelvir/100 mg ritonavir every 12 hours for 5 days; eGFR ≤60 and ≥30 mL/minute: 150 mg nirmatrelvir/100 mg ritonavir every 12 hours for 5 days; eGFR <30 mL/minute: not recommended" | idsa-2022 | p6 | p6/narrative/nirmatrelvir-renal-regimen | narrative |
| nirmatrelvir-renal-regimen | nirmatrelvir-renal | later discussion says eGFR <=30 mL/min is severe renal disease and nirmatrelvir/ritonavir is not recommended | RENDERED: "eGFR ≤30 mL/minute is considered severe renal impairment and nirmatrelvir/ritonavir is not recommended" | idsa-2022 | p77 | p77/narrative/nirmatrelvir-renal-boundary | narrative |
| molnupiravir-regimen | ambulatory-high-risk-molnupiravir | molnupiravir 800 mg for 5 days | "Molnupiravir 800 mg for 5 days" | idsa-2022 | p6 | p6/narrative/molnupiravir-regimen | narrative |
| remdesivir-three-day-regimen | ambulatory-remdesivir | remdesivir 200 mg IV on day 1, then 100 mg IV on days 2 and 3 | RENDERED: "3 days of IV remdesivir (200 mg on day 1 followed by 100 mg on days 2 and 3) initiated within 7 days of symptom onset" | idsa-2022 | p37 | p37/narrative/outpatient-remdesivir-regimen | narrative |
| remdesivir-renal-boundary | ambulatory-remdesivir | US prescribing information recommends against use when eGFR <30 mL/min | RENDERED: "prescribing information recommends against use of remdesivir in patients with eGFR less than 30 mL per minute" | idsa-2022 | p44 | p44/narrative/remdesivir-renal-against | narrative |
| remdesivir-renal-boundary | ambulatory-remdesivir | use with caution when creatinine clearance <30 mL/min | RENDERED: "Remdesivir: use with caution when CrCl <30 mL/min" | idsa-2022 | p83 | p83/narrative/table-41-remdesivir-renal | narrative |
| remdesivir-hepatic-stop | covid-treatment-monitoring | consider discontinuing remdesivir if ALT or AST >10 times the upper limit of normal | RENDERED: "Consider discontinuation if ALT/AST >10 times the upper limit of normal" | idsa-2022 | p83 | p83/narrative/table-41-remdesivir-hepatic | narrative |
| remdesivir-three-day-regimen | pediatric-remdesivir | pediatric dosing 5 mg/kg on day 1 then 2.5 mg/kg on subsequent days | RENDERED: "Pediatric dose: 5 mg/kg on day 1, followed by 2.5 mg/kg on subsequent days" | idsa-2022 | p3 | p3/narrative/pediatric-remdesivir-dose | narrative |
| remdesivir-three-day-regimen | pediatric-remdesivir | pediatric dosing 5 mg/kg on day 1 then 2.5 mg/kg on subsequent days | RENDERED: "Pediatric dose: 5 mg/kg on day 1, followed by 2.5 mg/kg on subsequent days" | idsa-2022 | p38 | p38/narrative/pediatric-remdesivir-dose | narrative |
| pediatric-treatment-age-boundary | pediatric-remdesivir | outpatient remdesivir use supported down to weight 3.5 kg | RENDERED: "data support outpatient remdesivir use down to 3.5 kg" | idsa-2022 | p89 | p89/narrative/pediatric-remdesivir-eligibility | narrative |
| nirmatrelvir-pediatric-eligibility | nirmatrelvir-pediatric | not authorized when age <12 years or weight <40 kg | RENDERED: "not authorized for patients younger than 12 years or weighing less than 40 kg" | idsa-2022 | p90 | p90/narrative/nirmatrelvir-pediatric | narrative |
| nirmatrelvir-hepatic-boundary | nirmatrelvir-hepatic | no adjustment for Child-Pugh A or B; not recommended for Child-Pugh C | RENDERED: "No dosage adjustment for Child-Pugh Class A or B; not recommended in Child-Pugh Class C" | idsa-2022 | p77 | p77/narrative/nirmatrelvir-hepatic | narrative |
| molnupiravir-contraception | molnupiravir-reproductive | patients who could become pregnant: reliable contraception during treatment and 4 days after; sexually active males with partners who could become pregnant: during treatment and at least 3 months after | RENDERED: "use reliable contraception during treatment and for 4 days after; sexually active males with partners of childbearing potential during treatment and for at least 3 months after" | idsa-2022 | p78 | p78/narrative/molnupiravir-contraception | narrative |
| il6-monitoring-cutoffs | covid-treatment-monitoring | sarilumab: avoid baseline ALT/AST >1.5 times ULN and discontinue at 5 times ULN; chronic-use precautions avoid tocilizumab if ANC <2000/mm3 or platelets <100000/mm3 and sarilumab if ANC <2000/mm3 or platelets <150000/mm3 | RENDERED: "Sarilumab avoid if baseline ALT/AST >1.5 × ULN; discontinue at 5 × ULN. Tocilizumab avoid ANC <2000/mm3 or platelets <100000/mm3; sarilumab avoid ANC <2000/mm3 or platelets <150000/mm3." | idsa-2022 | p83 | p83/narrative/table-41-il6-monitoring | narrative |
| jak-monitoring-cutoffs | covid-treatment-monitoring | chronic-rheumatology-derived precautions; COVID-associated cytopenias may still warrant use: baricitinib lymphocytes <500/mm3, neutrophils <1000/mm3, hemoglobin <8 g/dL; tofacitinib lymphocytes <500/mm3, neutrophils <1000/mm3, hemoglobin <9 g/dL | RENDERED: "Baricitinib: lymphocytes <500/mm3, neutrophils <1000/mm3, hemoglobin <8 g/dL. Tofacitinib: lymphocytes <500/mm3, neutrophils <1000/mm3, hemoglobin <9 g/dL." | idsa-2022 | p83 | p83/narrative/table-41-jak-monitoring | narrative |
| jak-renal-boundary | hospitalized-severe-baricitinib | adjust baricitinib when creatinine clearance <60 mL/min | RENDERED: "Baricitinib: adjust dose when CrCl <60 mL/min" | idsa-2022 | p83 | p83/narrative/baricitinib-renal | narrative |
| jak-renal-boundary | covid-treatment-monitoring | adjust tofacitinib when creatinine clearance <50 mL/min | RENDERED: "Tofacitinib: adjust dose when CrCl <50 mL/min" | idsa-2022 | p83 | p83/narrative/tofacitinib-renal | narrative |
| pediatric-treatment-age-boundary | pediatric-treatment-age | historical/extrapolated age branches: tocilizumab >=2 years; sarilumab >=18 years; baricitinib >=2 years; tofacitinib >=2 years; neutralizing antibodies >=12 years | RENDERED: "Tocilizumab ≥2 years; sarilumab ≥18 years; baricitinib ≥2 years; tofacitinib ≥2 years; neutralizing antibodies ≥12 years" | idsa-2022 | p83 | p83/narrative/pediatric-treatment-ages | narrative |
| critical-steroid-other-indication | critically-ill-steroid-alternative | dexamethasone doses up to 20 mg/day only when indicated for other reasons; hydrocortisone 50 mg IV every 6 hours is a studied alternative | RENDERED: "dexamethasone 6 mg/day is preferred, but doses up to 20 mg/day can be used if indicated for other reasons. Hydrocortisone 50 mg IV every 6 hours is an alternative" | idsa-2022 | p87 | p87/narrative/critical-steroid-alternatives | narrative |
| baricitinib-regimen | hospitalized-severe-baricitinib | 4 mg/day or appropriate renal dose for up to 14 days or hospital discharge | RENDERED: "Baricitinib 4 mg per day for 14 days or until hospital discharge" | idsa-2022 | p60 | p60/narrative/baricitinib-regimen | narrative |
| covid-severe-oxygen-threshold | covid-severity | rendered summary: severe COVID-19 is SpO2 <94% on room air or need for low-flow supplemental oxygen | RENDERED: "Severe but not critical COVID-19 (SpO2 <94% on room air or needing low-flow supplemental oxygen)" | idsa-2022 | p84 | p84/narrative/severe-summary | narrative |
| covid-severe-oxygen-threshold | covid-severity | rendered summary: mild-to-moderate COVID-19 is SpO2 >=94% on room air without supplemental oxygen | RENDERED: "Mild-to-moderate COVID-19 (SpO2 ≥94% on room air and not needing supplemental oxygen)" | idsa-2022 | p84 | p84/narrative/mild-moderate-summary | narrative |

## Conflicts

CONFLICT: covid-severe-oxygen-threshold — `severe illness: SpO2 <=94% on room air, including supplemental oxygen; rendered summary: severe COVID-19 is SpO2 <94% on room air or need for low-flow supplemental oxygen; rendered summary: mild-to-moderate COVID-19 is SpO2 >=94% on room air without supplemental oxygen`.

CONFLICT: remdesivir-renal-boundary — `US prescribing information recommends against use when eGFR <30 mL/min; use with caution when creatinine clearance <30 mL/min`.

CONFLICT: nirmatrelvir-renal-regimen — `eGFR >60: nirmatrelvir 300 mg plus ritonavir 100 mg every 12 hours for 5 days; eGFR 30-60: nirmatrelvir 150 mg plus ritonavir 100 mg every 12 hours for 5 days; eGFR <30: not recommended; later discussion says eGFR <=30 mL/min is severe renal disease and nirmatrelvir/ritonavir is not recommended`.

## Coverage

The bound recommendation file contains exactly 59 marker records: 19 are cited above and 40 are scoped below. The source separately describes 32 guideline recommendations; marker records include cumulative and damaged extraction shapes and are accounted as stored.

- `p2/grade-spelled-out/1` - scoped: qualitative recommendation without an additional numeric action.
- `p2/grade-spelled-out/2` - scoped: qualitative recommendation without an additional numeric action.
- `p2/grade-spelled-out/3` - scoped: qualitative recommendation without an additional numeric action.
- `p2/grade-spelled-out/4` - scoped: qualitative recommendation without an additional numeric action.
- `p2/grade-spelled-out/5` - scoped: qualitative recommendation without an additional numeric action.
- `p2/grade-spelled-out/6` - scoped: qualitative recommendation without an additional numeric action.
- `p2/grade-spelled-out/9` - scoped: qualitative recommendation against glucocorticoids in patients without hypoxemia requiring supplemental oxygen; the dose preface is represented in the retained steroid rows.
- `p3/grade-spelled-out/1` - scoped: damaged qualitative tail without an additional numeric action.
- `p3/grade-spelled-out/3` - scoped: qualitative recommendation against hospitalized convalescent plasma.
- `p4/grade-spelled-out/4` - scoped: qualitative famotidine recommendation.
- `p4/grade-spelled-out/5` - scoped: susceptible-variant preexposure recommendation without an additional numeric action.
- `p5/grade-spelled-out/1` - scoped: damaged certainty-only fragment.
- `p5/grade-spelled-out/2` - scoped: qualitative JAK-inhibitor recommendation without an additional numeric action.
- `p5/grade-spelled-out/4` - scoped: qualitative JAK-inhibitor recommendation without an additional numeric action.
- `p5/grade-spelled-out/5` - scoped: qualitative ivermectin recommendation without an additional numeric action.
- `p5/grade-spelled-out/6` - scoped: qualitative recommendation; tofacitinib trial dosing is not adopted.
- `p7/grade-spelled-out/1` - scoped: damaged colchicine-against recommendation.
- `p7/grade-spelled-out/2` - scoped: qualitative colchicine-against recommendation.
- `p10/grade-spelled-out/1` - scoped: qualitative hydroxychloroquine recommendation.
- `p10/grade-spelled-out/2` - scoped: qualitative hydroxychloroquine recommendation.
- `p16/grade-spelled-out/1` - scoped: qualitative hydroxychloroquine recommendation.
- `p17/grade-spelled-out/1` - scoped: qualitative recommendation against lopinavir/ritonavir.
- `p17/grade-spelled-out/2` - scoped: qualitative recommendation against lopinavir/ritonavir.
- `p17/grade-spelled-out/3` - scoped: qualitative recommendation against lopinavir/ritonavir.
- `p22/grade-spelled-out/1` - scoped: qualitative critical-illness steroid recommendation; its numeric regimen is represented from the executive remarks and narrative.
- `p22/grade-spelled-out/2` - scoped: qualitative severe-illness steroid recommendation; its numeric regimen is represented from the executive remarks and narrative.
- `p27/grade-spelled-out/1` - scoped: qualitative steroid recommendation without an additional numeric action.
- `p29/grade-spelled-out/1` - scoped: qualitative IL-6-inhibitor recommendation; CRP 75 mg/L is retained separately as a trial criterion.
- `p29/grade-spelled-out/2` - scoped: qualitative IL-6-inhibitor recommendation without an additional numeric action.
- `p30/grade-spelled-out/1` - scoped: qualitative hospitalized-plasma recommendation.
- `p44/grade-spelled-out/1` - scoped: qualitative famotidine recommendation.
- `p44/grade-spelled-out/2` - scoped: qualitative famotidine recommendation.
- `p48/grade-spelled-out/1` - scoped: variant-susceptibility recommendation; executive tixagevimab/cilgavimab dosing is retained separately.
- `p48/grade-spelled-out/2` - scoped: variant-susceptibility recommendation without an additional numeric action.
- `p60/grade-spelled-out/1` - scoped: qualitative baricitinib recommendation; regimen is retained from the narrative.
- `p69/grade-spelled-out/1` - scoped: qualitative remdesivir recommendation without an additional numeric action.
- `p70/grade-spelled-out/1` - scoped: qualitative tofacitinib recommendation without an additional numeric action.
- `p70/grade-spelled-out/2` - scoped: qualitative ivermectin recommendation.
- `p83/grade-spelled-out/1` - scoped: qualitative ivermectin recommendation.
- `p83/grade-spelled-out/2` - scoped: qualitative colchicine recommendation.

ADR 0009 disposition: all guideline-adopted numeric dose, duration, timing, age, oxygen-saturation, and renal boundaries identified in the 100-page read are retained. Qualitative recommendations against ineffective therapies remain in the source and are not converted into numeric rows.

ADR 0009 disposition: trial doses and eligibility criteria, outcome rates, effect estimates, confidence intervals, follow-up intervals, sample sizes, pharmacokinetic measurements, adverse-event counts, historical section-review dates, recommendation numbers, and figure/table numbers are evidence or locators and are scoped out. The CRP >=75 mg/L row is retained but explicitly labeled as the largest-trial criterion rather than an IDSA eligibility mandate.

ADR 0009 disposition: the document predates subsequent variant susceptibility changes and authorization withdrawals. Variant-dependent antibodies are reported only with the source's susceptibility qualifier; this historical sheet does not assert present availability or activity.

ADR 0009 disposition: the pediatric age branches in the source's 2022 treatment table are historical and largely extrapolated from adult COVID-19 data or pediatric experience in other indications. Neutralizing-antibody eligibility was also agent-, authorization-, and variant-specific; the retained age floor does not imply current availability.

ADR 0009 disposition: Table 41 states that the cytopenia warnings come from chronic rheumatology use and that virus-associated cytopenias, particularly lymphocytopenia, may not preclude use of these agents for COVID treatment. The retained JAK-inhibitor cutoffs therefore preserve that context rather than presenting chronic-use warnings as automatic exclusions.

ADR 0009 disposition: the Table 41 baricitinib renal line has a corrupted or missing operator at the 15 mL/min threshold in extracted text. No operator is silently repaired and no 15 mL/min baricitinib action row is created without reliable rendered support.

Source: `C:/codeing/guidelines-recs/IDSA/ciac724.json` (mode `bound`, counted from text markers). Source PDF SHA-256: `1da6304a8829b3c8c24345992bb26a0048a3455d13af4d1a87576e68723f549c`.
