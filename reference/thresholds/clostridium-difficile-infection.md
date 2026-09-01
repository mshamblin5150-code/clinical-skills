# Clostridium difficile infection — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-shea-2017 | IDSA/SHEA | IDSA/cix1085 | guideline | 2017 update | 2018-04-01 | https://doi.org/10.1093/cid/cix1085 | stated | bound |

## Scope

**Read:** all 48 pages: executive-summary recommendations; adult and pediatric
epidemiology, diagnosis, prevention, and treatment sections; every table and figure;
research gaps, article information, disclosures, and references. Rows retain numeric
definitions, testing and isolation boundaries, drug doses and durations, recurrence
regimens, severity and surgical triggers, and pediatric age and weight-based decisions.
Epidemiologic estimates, study enrollment, effect sizes, outcome rates, and trial-only
regimens not adopted by the guideline were read but do not produce rows. Treatment
Tables 1 and 2 were read as rendered structures before their regimens were retained.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| executive summary and treatment tables | 1-8 | yes |
| introduction, methods, definitions, and epidemiology | 9-14 | yes |
| diagnosis | 15-22 | yes |
| isolation, environmental control, and stewardship | 23-30 | yes |
| adult treatment and recurrence | 31-36 | yes |
| pediatric treatment | 37-38 | yes |
| research gaps, article information, and disclosures | 39-40 | read 2026-08-31; blind 2026-08-31 |
| references | 41-48 | exempt: reference list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 742fc12877df8561b3aa68dc8b317ade1eccd1ce9f0e12492e6b26abb6556799; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| inpatient-pediatric-surveillance | inpatient pediatric facilities conducting healthcare-onset CDI surveillance |
| suspected-cdi | patients with unexplained new-onset diarrhea considered for CDI testing |
| same-diarrhea-episode | patients during the same episode of diarrhea |
| infants-diarrhea | neonates or infants with diarrhea |
| toddlers-diarrhea | children 1-2 years of age with diarrhea |
| children-2plus-risk | children age 2 years or older with prolonged or worsening diarrhea and risk factors or relevant exposures |
| suspected-cdi-isolation | patients with suspected CDI on contact precautions |
| incident-cdi | patients classified as having an incident CDI case |
| recurrent-cdi | patients classified as having recurrent CDI |
| hospitalized-cdi | hospitalized patients classified for healthcare-onset CDI surveillance |
| discharged-facility-patients | patients monitored for postdischarge healthcare-associated CDI |
| adults-initial-cdi | adults with an initial CDI episode |
| adults-nonsevere-cdi | adults with an initial nonsevere CDI episode |
| adults-severe-cdi | adults with an initial severe CDI episode |
| adults-fulminant-cdi | adults with fulminant CDI |
| adults-first-recurrence | adults with a first CDI recurrence |
| adults-first-recurrence-after-metronidazole | adults with a first CDI recurrence whose initial episode was treated with metronidazole |
| adults-first-recurrence-after-vancomycin | adults with a first CDI recurrence whose initial episode was treated with vancomycin |
| adults-multiple-recurrence | adults with more than one CDI recurrence |
| adults-fulminant-surgery | adults with fulminant CDI considered for early surgery |
| adults-systemic-antibiotics-after-cdi | adults with prior CDI receiving systemic antibiotics |
| fmt-candidates | patients preparing for fecal microbiota transplantation |
| stool-donors | potential fecal microbiota donors |
| children-nonsevere-cdi | children with an initial or first recurrent nonsevere CDI episode |
| children-severe-cdi | children with an initial severe or fulminant CDI episode |
| children-multiple-recurrence | children with a second or subsequent CDI recurrence |
| delayed-confirmation-cdi | patients with suspected CDI when laboratory confirmation is expected to be substantially delayed |
| children-severe-fidaxomicin | children with severe CDI considered for fidaxomicin treatment |
| laxative-exposed-testing | patients considered for CDI testing who received a laxative |
| suspected-cdi-delayed-result | patients with suspected CDI whose test result cannot be obtained on the specimen-collection day |
| outbreak-cdi-rooms | rooms housing patients with CDI during outbreaks, hyperendemic settings, or repeated same-room cases |
| pediatric-second-recurrence | children with a second or greater recurrent CDI episode |

## Quantities

| key | verbatim |
| --- | --- |
| pediatric-surveillance-age | age excluded from pediatric healthcare-onset surveillance |
| testing-diarrhea-threshold | stool count and time defining the preferred testing population |
| repeat-testing-window | interval in which repeat testing should not be performed |
| pediatric-testing-age | pediatric age-specific testing boundary |
| contact-precaution-duration | minimum isolation after diarrhea resolves |
| incident-case-window | prior-positive-free interval defining an incident episode |
| recurrent-case-window | interval after a prior positive episode defining recurrence |
| healthcare-onset-day | hospital day defining healthcare-onset CDI |
| postdischarge-window | postdischarge surveillance window |
| adult-severity-threshold | leukocyte and creatinine criteria defining nonsevere or severe CDI |
| adult-initial-regimen | adult initial-episode drug dose and duration |
| adult-metronidazole-alternative | metronidazole alternative regimen when preferred agents are unavailable |
| adult-treatment-extension | duration extension for delayed symptom resolution |
| adult-fulminant-regimen | vancomycin and metronidazole regimen for fulminant CDI |
| adult-vancomycin-taper | tapered and pulsed vancomycin regimen |
| adult-rifaximin-chaser | vancomycin followed by rifaximin regimen |
| recurrence-count | recurrence number changing treatment options |
| early-surgery-trigger | leukocyte count or lactate level supporting early surgery |
| secondary-prophylaxis-dose | low-dose vancomycin or fidaxomicin during systemic antibiotics |
| fmt-induction | vancomycin induction before FMT |
| stool-donor-antibiotic-window | prior antibiotic interval disqualifying a donor |
| pediatric-nonsevere-regimen | pediatric nonsevere CDI dose and maximum |
| pediatric-severe-regimen | pediatric severe or fulminant CDI dose and maximum |
| pediatric-recurrence-regimen | pediatric tapered vancomycin or rifaximin-chaser regimen |
| pediatric-rifaximin-age | age below which rifaximin lacks approval |
| empiric-treatment-delay | expected laboratory-confirmation delay that triggers empiric CDI therapy |
| pediatric-fidaxomicin-age | age below which fidaxomicin was not recommended for routine severe-CDI treatment at publication |
| laxative-testing-window | recent laxative-exposure interval in which routine CDI testing should be avoided |
| preemptive-precaution-result-time | test-result timing that triggers preemptive contact precautions |
| outbreak-room-cleaning-cadence | sporicidal room-cleaning cadence |
| fmt-recurrence-threshold | recurrence and episode count before offering FMT |
| pediatric-recurrence-count | pediatric recurrence ordinal changing preferred therapy |
| adult-first-recurrence-standard | standard-course duration selected by the initial-episode drug |
| adult-first-recurrence-table-regimen | rendered standard-course dose and duration selected by the initial-episode drug |
| adult-multiple-recurrence-fidaxomicin | fidaxomicin regimen for multiple recurrence |
| pediatric-rifaximin-chaser | pediatric vancomycin-then-rifaximin regimen for second or subsequent recurrence |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pediatric-surveillance-age | inpatient-pediatric-surveillance | exclude cases age <2 years | do not include cases <2 years of age | idsa-shea-2017 | 3 | p3/grade-spelled-out/1 | weak recommendation, low quality of evidence |
| pediatric-surveillance-age | inpatient-pediatric-surveillance | exclude cases age <2 years | do not include cases <2 years of age | idsa-shea-2017 | 14 | p14/grade-spelled-out/1 | weak recommendation, low quality of evidence |
| testing-diarrhea-threshold | suspected-cdi | >=3 unformed stools in 24 hours | ≥3 unformed stools in 24 hours | idsa-shea-2017 | 3 | p3/grade-spelled-out/3 | weak recommendation, very low quality of evidence |
| testing-diarrhea-threshold | suspected-cdi | >=3 unformed stools in 24 hours | ≥3 unformed stools in 24 hours | idsa-shea-2017 | 15 | p15/grade-spelled-out/1 | weak recommendation, very low quality of evidence |
| repeat-testing-window | same-diarrhea-episode | do not repeat within 7 days | Do not perform repeat testing (within 7 days) during the same episode of diarrhea | idsa-shea-2017 | 3 | p3/grade-spelled-out/6 | strong recommendation, moderate quality of evidence |
| repeat-testing-window | same-diarrhea-episode | do not repeat within 7 days | Do not perform repeat testing (within 7 days) during the same episode of diarrhea | idsa-shea-2017 | 21 | p21/grade-spelled-out/2 | strong recommendation, moderate quality of evidence |
| pediatric-testing-age | infants-diarrhea | do not routinely test age <=12 months | infants ≤12 months of age with diarrhea | idsa-shea-2017 | 4 | p4/grade-spelled-out/1 | strong recommendation, moderate quality of evidence |
| pediatric-testing-age | toddlers-diarrhea | age 1-2 years: do not routinely test unless other causes excluded | children with diarrhea who are 1–2 years of age unless other infectious or noninfectious causes have been excluded | idsa-shea-2017 | 4 | p4/grade-spelled-out/2 | weak recommendation, low quality of evidence |
| pediatric-testing-age | children-2plus-risk | age >=2 years: test prolonged/worsening diarrhea with risks or exposures | children ≥2 years of age | idsa-shea-2017 | 4 | p4/grade-spelled-out/3 | weak recommendation, moderate quality of evidence |
| pediatric-testing-age | infants-diarrhea | do not routinely test age <=12 months | infants ≤12 months of age with diarrhea | idsa-shea-2017 | 22 | p22/grade-spelled-out/1 | strong recommendation, moderate quality of evidence |
| pediatric-testing-age | toddlers-diarrhea | age 1-2 years: do not routinely test unless other causes excluded | children with diarrhea who are 1–2 years of age unless other infectious or noninfectious causes have been excluded | idsa-shea-2017 | 22 | p22/grade-spelled-out/2 | weak recommendation, low quality of evidence |
| pediatric-testing-age | children-2plus-risk | age >=2 years: test prolonged/worsening diarrhea with risks or exposures | children ≥2 years of age | idsa-shea-2017 | 22 | p22/grade-spelled-out/3 | weak recommendation, moderate quality of evidence |
| contact-precaution-duration | suspected-cdi-isolation | continue >=48 hours after diarrhea resolves | Continue contact precautions for at least 48 hours after diarrhea has resolved | idsa-shea-2017 | 4 | p4/grade-spelled-out/9 | weak recommendation, low quality of evidence |
| contact-precaution-duration | suspected-cdi-isolation | continue >=48 hours after diarrhea resolves | Continue contact precautions for at least 48 hours after diarrhea has resolved | idsa-shea-2017 | 24 | p24/grade-spelled-out/2 | weak recommendation, low quality of evidence |
| incident-case-window | incident-cdi | no positive episode in previous 8 weeks | no episode of symptom onset with positive result within the previous 8 weeks | idsa-shea-2017 | 10 | p10/narrative/incident-case | narrative |
| recurrent-case-window | recurrent-cdi | positive episode in previous 2-8 weeks | positive assay result in the previous 2-8 weeks | idsa-shea-2017 | 10 | p10/narrative/recurrent-case | narrative |
| healthcare-onset-day | hospitalized-cdi | specimen >3 days after admission, on or after day 4 | collected >3 days after admission to the facility (ie, on or after day 4) | idsa-shea-2017 | 10 | p10/narrative/healthcare-onset | narrative |
| postdischarge-window | discharged-facility-patients | monitor CDI occurring within 28 days after discharge | RENDERED: CDI occurring within 28 days after discharge from a healthcare facility | idsa-shea-2017 | 10 | p10/narrative/postdischarge | narrative |
| laxative-testing-window | laxative-exposed-testing | laxative within previous 48 hours: do not routinely test stool for CDI | RENDERED: not routinely performing testing on stool from a patient who has received a laxative within the previous 48 hours | idsa-shea-2017 | 15 | p15/narrative/laxative-testing-window | narrative |
| preemptive-precaution-result-time | suspected-cdi-delayed-result | if result cannot be obtained the same day, use preemptive contact precautions pending the result | if test results cannot be obtained on the same day | idsa-shea-2017 | 4 | p4/grade-spelled-out/8 | strong recommendation, moderate quality of evidence |
| preemptive-precaution-result-time | suspected-cdi-delayed-result | if result cannot be obtained the same day, use preemptive contact precautions pending the result | if test results cannot be obtained on the same day | idsa-shea-2017 | 24 | p24/grade-spelled-out/1 | strong recommendation, moderate quality of evidence |
| adult-severity-threshold | adults-initial-cdi | nonsevere: WBC <=15 000 cells/mL and creatinine <1.5 mg/dL | RENDERED: Initial episode, non-severe: white blood cell count ≤15 000 cells/mL and serum creatinine <1.5 mg/dL | idsa-shea-2017 | 6 | p6/narrative/adult-nonsevere | narrative |
| adult-severity-threshold | adults-initial-cdi | severe: WBC >=15 000 cells/mL or creatinine >1.5 mg/dL | RENDERED: Initial episode, severe: white blood cell count ≥15 000 cells/mL or serum creatinine >1.5 mg/dL | idsa-shea-2017 | 6 | p6/narrative/adult-severe | narrative |
| adult-initial-regimen | adults-initial-cdi | vancomycin 125 mg orally 4 times/day or fidaxomicin 200 mg twice/day for 10 days | vancomycin 125 mg orally 4 times per day or fidaxomicin 200 mg twice daily for 10 days | idsa-shea-2017 | 6 | p6/grade-spelled-out/3 | strong recommendation, high quality of evidence |
| adult-initial-regimen | adults-initial-cdi | vancomycin 125 mg orally 4 times/day or fidaxomicin 200 mg twice/day for 10 days | vancomycin 125 mg orally 4 times per day or fidaxomicin 200 mg twice daily for 10 days | idsa-shea-2017 | 31 | p31/grade-spelled-out/1 | strong recommendation, high quality of evidence |
| adult-metronidazole-alternative | adults-nonsevere-cdi | metronidazole 500 mg orally 3 times/day for 10 days only when preferred agents unavailable | metronidazole 500 mg orally 3 times per day for 10 days | idsa-shea-2017 | 6 | p6/grade-spelled-out/4 | weak recommendation, high quality of evidence |
| adult-metronidazole-alternative | adults-nonsevere-cdi | metronidazole 500 mg orally 3 times/day for 10 days only when preferred agents unavailable | metronidazole 500 mg orally 3 times per day for 10 days | idsa-shea-2017 | 31 | p31/grade-spelled-out/2 | weak recommendation, high quality of evidence |
| adult-treatment-extension | adults-initial-cdi | if improved without resolution by day 10, consider extending to 14 days | RENDERED: If patients have improved, but have not had symptom resolution by 10 days, extension of the treatment duration to 14 days should be considered | idsa-shea-2017 | 31 | p31/narrative/treatment-extension | narrative |
| empiric-treatment-delay | delayed-confirmation-cdi | expected confirmation delay >48 hours: start CDI therapy empirically | RENDERED: Antibiotic therapy should be started empirically if a substantial delay in laboratory confirmation is expected (eg, >48 hours) | idsa-shea-2017 | 31 | p31/narrative/empiric-treatment-delay | narrative |
| adult-fulminant-regimen | adults-fulminant-cdi | vancomycin 500 mg orally or NG 4 times/day; if ileus, 500 mg in about 100 mL saline rectally every 6 hours; add metronidazole 500 mg IV every 8 hours | RENDERED: VAN 500 mg 4 times per day by mouth or nasogastric tube; if ileus, 500 mg in approximately 100 mL normal saline per rectum every 6 hours; metronidazole 500 mg intravenously every 8 hours | idsa-shea-2017 | 6 | p6/grade-spelled-out/5 | strong recommendation, moderate quality of evidence |
| adult-fulminant-regimen | adults-fulminant-cdi | vancomycin 500 mg orally or NG 4 times/day; if ileus, 500 mg in about 100 mL saline rectally every 6 hours; add metronidazole 500 mg IV every 8 hours | RENDERED: vancomycin dosage is 500 mg orally 4 times per day and 500 mg in approximately 100 mL normal saline per rectum every 6 hours; metronidazole dosage is 500 mg intravenously every 8 hours | idsa-shea-2017 | 34 | p34/grade-spelled-out/1 | strong recommendation, moderate quality of evidence |
| early-surgery-trigger | adults-fulminant-surgery | rising WBC >=25 000 or lactate >=5 mmol/L supports early surgery | A rising WBC count (≥25 000) or a rising lactate level (≥5 mmol/L) is associated with high mortality and may be helpful in identifying patients whose best hope for survival lies with early surgery | idsa-shea-2017 | 34 | p34/narrative/early-surgery | narrative |
| adult-vancomycin-taper | adults-first-recurrence | 125 mg 4 times/day for 10-14 days, twice/day for a week, once/day for a week, then every 2-3 days for 2-8 weeks | RENDERED: 125 mg 4 times per day for 10-14 days, 2 times per day for a week, once per day for a week, and then every 2 or 3 days for 2-8 weeks | idsa-shea-2017 | 6 | p6/narrative/adult-vancomycin-taper | narrative |
| adult-vancomycin-taper | adults-multiple-recurrence | 125 mg 4 times/day for 10-14 days, twice/day for a week, once/day for a week, then every 2-3 days for 2-8 weeks | After the usual dosage of 125 mg 4 times per day for 10-14 days, vancomycin is administered at 125 mg 2 times per day for a week, 125 mg once per day for a week, and then 125 mg every 2 or 3 days for 2-8 weeks | idsa-shea-2017 | 35 | p35/narrative/vancomycin-taper | narrative |
| adult-first-recurrence-standard | adults-first-recurrence-after-metronidazole | use a standard 10-day vancomycin course | Treat a first recurrence of CDI with a standard 10-day course of vancomycin rather than a second course of metronidazole if metronidazole was used for the primary episode | idsa-shea-2017 | 7 | p7/grade-spelled-out/6 | weak recommendation, low quality of evidence |
| adult-first-recurrence-standard | adults-first-recurrence-after-metronidazole | use a standard 10-day vancomycin course | Treat a first recurrence of CDI with a standard 10-day course of vancomycin rather than a second course of metronidazole if metronidazole was used for the primary episode | idsa-shea-2017 | 34 | p34/grade-spelled-out/8 | weak recommendation, low quality of evidence |
| adult-first-recurrence-standard | adults-first-recurrence-after-vancomycin | use a 10-day fidaxomicin course | Treat a first recurrence of CDI with a 10-day course of fidaxomicin rather than a standard 10-day course of vancomycin | idsa-shea-2017 | 7 | p7/grade-spelled-out/5 | weak recommendation, moderate quality of evidence |
| adult-first-recurrence-standard | adults-first-recurrence-after-vancomycin | use a 10-day fidaxomicin course | RENDERED: Treat a first recurrence of CDI with a 10-day course of fidaxomicin rather than a standard 10-day course of vancomycin | idsa-shea-2017 | 34 | p34/grade-spelled-out/7 | weak recommendation, moderate quality of evidence |
| adult-first-recurrence-table-regimen | adults-first-recurrence-after-metronidazole | vancomycin 125 mg 4 times/day for 10 days | RENDERED: VAN 125 mg given 4 times daily for 10 days if metronidazole was used for the initial episode | idsa-shea-2017 | 6 | p6/narrative/adult-first-recurrence-vancomycin | narrative |
| adult-first-recurrence-table-regimen | adults-first-recurrence-after-vancomycin | fidaxomicin 200 mg twice/day for 10 days | RENDERED: FDX 200 mg given twice daily for 10 days if VAN was used for the initial episode | idsa-shea-2017 | 6 | p6/narrative/adult-first-recurrence-fidaxomicin | narrative |
| adult-rifaximin-chaser | adults-multiple-recurrence | vancomycin 125 mg 4 times/day for 10 days then rifaximin 400 mg 3 times/day for 20 days | RENDERED: VAN 125 mg 4 times per day by mouth for 10 days followed by rifaximin 400 mg 3 times daily for 20 days | idsa-shea-2017 | 6 | p6/narrative/adult-rifaximin-chaser | narrative |
| adult-multiple-recurrence-fidaxomicin | adults-multiple-recurrence | fidaxomicin 200 mg twice/day for 10 days | RENDERED: FDX 200 mg given twice daily for 10 days | idsa-shea-2017 | 6 | p6/narrative/adult-multiple-recurrence-fidaxomicin | narrative |
| recurrence-count | adults-multiple-recurrence | >1 recurrence enables taper, rifaximin chaser, or fidaxomicin options | RENDERED: patients with >1 recurrence of CDI | idsa-shea-2017 | 7 | p7/grade-spelled-out/9 | weak recommendation, low quality of evidence |
| recurrence-count | adults-multiple-recurrence | >1 recurrence enables taper, rifaximin chaser, or fidaxomicin options | patients with >1 recurrence of CDI | idsa-shea-2017 | 34 | p34/grade-spelled-out/10 | weak recommendation, low quality of evidence |
| secondary-prophylaxis-dose | adults-systemic-antibiotics-after-cdi | if prevention chosen, vancomycin 125 mg or fidaxomicin 200 mg once daily while systemic antibiotics continue | it may be prudent to administer low doses of vancomycin or fidaxomicin (eg, 125 mg or 200 mg, respectively, once daily) while systemic antibiotics are administered | idsa-shea-2017 | 35 | p35/narrative/secondary-prophylaxis | narrative |
| fmt-recurrence-threshold | fmt-candidates | try appropriate antibiotic treatments for >=2 recurrences (3 CDI episodes) before offering FMT | appropriate antibiotic treatments for at least 2 recurrences (ie, 3 CDI episodes) should be tried | idsa-shea-2017 | 36 | p36/narrative/fmt-recurrence-threshold | narrative |
| stool-donor-antibiotic-window | stool-donors | disqualify antibiotic exposure within preceding 3 months | treated with an antibiotic agent during the preceding 3 months of donating stool | idsa-shea-2017 | 36 | p36/narrative/donor-antibiotic-window | narrative |
| fmt-induction | fmt-candidates | oral vancomycin for 3-4 days before FMT | oral vancomycin for 3-4 days prior to FMT administration | idsa-shea-2017 | 36 | p36/narrative/fmt-induction | narrative |
| pediatric-nonsevere-regimen | children-nonsevere-cdi | 10 days: metronidazole 7.5 mg/kg/dose tid or qid, max 500 mg; or vancomycin 10 mg/kg/dose qid, max 125 mg | RENDERED: Metronidazole 7.5 mg/kg/dose tid or qid, maximum 500 mg; vancomycin 10 mg/kg/dose qid, maximum 125 mg; 10 days | idsa-shea-2017 | 7 | p7/narrative/pediatric-nonsevere | narrative |
| pediatric-severe-regimen | children-severe-cdi | 10 days: vancomycin 10 mg/kg/dose qid, max 500 mg, with or without IV metronidazole 10 mg/kg/dose tid, max 500 mg | RENDERED: Vancomycin 10 mg/kg/dose qid, maximum 500 mg; with or without metronidazole 10 mg/kg/dose tid, maximum 500 mg; 10 days | idsa-shea-2017 | 7 | p7/narrative/pediatric-severe | narrative |
| pediatric-recurrence-regimen | children-multiple-recurrence | vancomycin 10 mg/kg/dose, max 125 mg: 4 times/day 10-14 days, twice/day for a week, once/day for a week, then every 2-3 days for 2-8 weeks | RENDERED: vancomycin 10 mg/kg with max of 125 mg 4 times per day for 10-14 days, then 2 times per day for a week, once per day for a week, and then every 2 or 3 days for 2-8 weeks | idsa-shea-2017 | 7 | p7/narrative/pediatric-recurrence | narrative |
| pediatric-recurrence-count | pediatric-second-recurrence | second or greater recurrent episode: prefer oral vancomycin over metronidazole | second or greater episode of recurrent CDI | idsa-shea-2017 | 8 | p8/grade-spelled-out/2 | weak recommendation, low quality of evidence |
| pediatric-recurrence-count | pediatric-second-recurrence | second or greater recurrent episode: prefer oral vancomycin over metronidazole | second or greater episode of recurrent CDI | idsa-shea-2017 | 37 | p37/grade-spelled-out/3 | weak recommendation, low quality of evidence |
| pediatric-rifaximin-chaser | children-multiple-recurrence | vancomycin 10 mg/kg/dose qid, max 500 mg qid, for 10 days; then rifaximin for 20 days with no pediatric dose and listed maximum 400 mg tid | RENDERED: Vancomycin for 10 days followed by rifaximin for 20 days; vancomycin 10 mg/kg/dose qid, maximum 500 mg qid; rifaximin no pediatric dosing, maximum 400 mg tid | idsa-shea-2017 | 7 | p7/narrative/pediatric-rifaximin-chaser | narrative |
| pediatric-rifaximin-age | children-multiple-recurrence | rifaximin not approved for children age <12 years | not approved by the US Food and Drug Administration for use in children <12 years of age | idsa-shea-2017 | 7 | p7/narrative/pediatric-rifaximin-age | narrative |
| pediatric-fidaxomicin-age | children-severe-fidaxomicin | age <18 years: not recommended for routine use at publication | RENDERED: Because fidaxomicin was not approved for use in patients <18 years of age, at the time of this writing, it is not recommended for routine use in the treatment of children with severe CDI | idsa-shea-2017 | 37 | p37/narrative/pediatric-fidaxomicin-age | narrative |
| outbreak-room-cleaning-cadence | outbreak-cdi-rooms | consider daily cleaning with a sporicidal agent | Daily cleaning with a sporicidal agent should be considered | idsa-shea-2017 | 5 | p5/grade-spelled-out/3 | weak recommendation, low quality of evidence |
| outbreak-room-cleaning-cadence | outbreak-cdi-rooms | consider daily cleaning with a sporicidal agent | Daily cleaning with a sporicidal agent should be considered | idsa-shea-2017 | 27 | p27/grade-spelled-out/1 | weak recommendation, low quality of evidence |

## Conflicts

Alternative adult and pediatric regimens otherwise apply to different severity,
recurrence, availability, route, or age branches.

CONFLICT: adult-severity-threshold — for `adults-initial-cdi`, Table 1 gives `nonsevere: WBC <=15 000 cells/mL and creatinine <1.5 mg/dL` and `severe: WBC >=15 000 cells/mL or creatinine >1.5 mg/dL`; the leukocyte criteria overlap at exactly 15 000 cells/mL, while the creatinine criteria do not overlap.

## Coverage

The source is bound: marker records delimit recommendation-shaped text but do not prove a complete recommendation denominator. The artifact contains 89 marker records under 89 distinct locators. Threshold rows cite 32 locators; the remaining 57 locators were read and contain no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, rendered treatment table, or narrative.

- `p2/grade-spelled-out/1` - scoped out because the minimum facility surveillance recommendation is qualitative and states no numeric patient-action decision point.
- `p2/grade-spelled-out/2` - scoped out because location-stratified surveillance in response to an elevated rate, goal, or outbreak is qualitative.
- `p3/grade-spelled-out/2` - scoped out because considering community-associated CDI surveillance is qualitative.
- `p3/grade-spelled-out/4` - scoped out because the multistep laboratory algorithm branch is qualitative and its figure number is a locator, not a clinical threshold.
- `p3/grade-spelled-out/5` - scoped out because the laboratory algorithm branch under preagreed submission criteria is qualitative and its figure number is a locator.
- `p4/grade-spelled-out/4` - scoped out because prioritizing incontinent patients when private rooms are limited states no numeric threshold.
- `p4/grade-spelled-out/5` - scoped out because the cohorting recommendation is qualitative.
- `p4/grade-spelled-out/6` - scoped out because glove use is qualitative.
- `p4/grade-spelled-out/7` - scoped out because glove and gown use is qualitative.
- `p4/grade-spelled-out/10` - scoped out because extending precautions until discharge is event-triggered and states no numeric threshold.
- `p4/grade-spelled-out/11` - scoped out because routine-setting hand hygiene is qualitative.
- `p4/grade-spelled-out/12` - scoped out because outbreak-setting soap-and-water preference is qualitative.
- `p5/grade-spelled-out/1` - scoped out because equipment cleaning and disinfection are qualitative.
- `p5/grade-spelled-out/2` - scoped out because terminal sporicidal cleaning under the stated facility conditions is qualitative.
- `p5/grade-spelled-out/4` - scoped out because minimizing high-risk antibiotic frequency, duration, and agent count states no cutoff.
- `p5/grade-spelled-out/5` - scoped out because the antibiotic-class restriction recommendation states no numeric patient-action threshold.
- `p6/grade-spelled-out/1` - scoped out because stopping the inciting antibiotic as soon as possible states no numeric threshold.
- `p6/grade-spelled-out/2` - scoped out because the summary recommendation is qualitative; the body supplies and is represented by the >48-hour expected-delay threshold.
- `p6/grade-spelled-out/6` - scoped out because rectal administration when ileus is present is a route branch; its numeric regimen is represented from the rendered table and body recommendation.
- `p7/grade-spelled-out/1` - scoped out because this page-break fragment adds no distinct numeric decision point beyond the represented fulminant regimen.
- `p7/grade-spelled-out/2` - scoped out because subtotal colectomy when surgery is necessary is qualitative.
- `p7/grade-spelled-out/3` - scoped out because the alternative diverting-loop-ileostomy approach is qualitative.
- `p7/grade-spelled-out/4` - scoped out because the first-recurrence taper recommendation's 10-day comparator and taper action are represented by the rendered Table 1 taper regimen.
- `p7/grade-spelled-out/7` - scoped out because the >1-recurrence population and tapered-regimen option are represented by the recurrence-count and taper rows.
- `p7/grade-spelled-out/8` - scoped out because the >1-recurrence population, taper, and rifaximin-chaser branches are represented from Table 1 and the adjacent recommendation.
- `p7/grade-spelled-out/10` - scoped out because FMT after failed appropriate antibiotic treatments uses an unnumbered multiple-recurrence population and states no additional numeric cutoff.
- `p8/grade-spelled-out/1` - scoped out because the severe-pediatric vancomycin recommendation is represented with the numeric regimen from rendered Table 2.
- `p8/grade-spelled-out/3` - scoped out because pediatric FMT after multiple recurrences and standard treatment failure states no distinct numeric cutoff.
- `p10/grade-spelled-out/1` - scoped out because the body surveillance recommendation duplicates the qualitative summary recommendation.
- `p10/grade-spelled-out/2` - scoped out because the body location-stratification recommendation duplicates the qualitative summary recommendation.
- `p14/grade-spelled-out/2` - scoped out because considering community-associated CDI surveillance is qualitative.
- `p16/grade-spelled-out/1` - scoped out because the multistep laboratory algorithm branch is qualitative and its figure number is a locator.
- `p21/grade-spelled-out/1` - scoped out because the laboratory algorithm branch under preagreed submission criteria is qualitative and its figure number is a locator.
- `p23/grade-spelled-out/1` - scoped out because prioritizing incontinent patients when private rooms are limited states no numeric threshold.
- `p23/grade-spelled-out/2` - scoped out because the cohorting recommendation is qualitative.
- `p23/grade-spelled-out/3` - scoped out because glove use is qualitative.
- `p23/grade-spelled-out/4` - scoped out because glove and gown use is qualitative.
- `p24/grade-spelled-out/3` - scoped out because extending precautions until discharge is event-triggered and states no numeric threshold.
- `p24/grade-spelled-out/4` - scoped out because routine-setting hand hygiene is qualitative.
- `p24/grade-spelled-out/5` - scoped out because outbreak-setting soap-and-water preference is qualitative.
- `p25/grade-spelled-out/1` - scoped out because equipment cleaning and disinfection are qualitative.
- `p26/grade-spelled-out/1` - scoped out because terminal sporicidal cleaning under the stated facility conditions is qualitative.
- `p28/grade-spelled-out/1` - scoped out because minimizing high-risk antibiotic frequency, duration, and agent count states no cutoff.
- `p28/grade-spelled-out/2` - scoped out because the antibiotic-class restriction recommendation states no numeric patient-action threshold.
- `p30/grade-spelled-out/1` - scoped out because stopping the inciting antibiotic as soon as possible states no numeric threshold.
- `p30/grade-spelled-out/2` - scoped out because the recommendation is qualitative; its body evidence supplies and is represented by the >48-hour expected-delay threshold.
- `p31/grade-spelled-out/3` - scoped out because avoiding repeated or prolonged metronidazole states no numeric duration cutoff.
- `p34/grade-spelled-out/2` - scoped out because rectal vancomycin when ileus is present is a route branch whose numeric regimen is represented from rendered Table 1 and the body.
- `p34/grade-spelled-out/3` - scoped out because adding intravenous metronidazole with ileus is represented within the fulminant numeric regimen.
- `p34/grade-spelled-out/4` - scoped out because subtotal colectomy when surgery is necessary is qualitative.
- `p34/grade-spelled-out/5` - scoped out because the alternative diverting-loop-ileostomy approach is qualitative.
- `p34/grade-spelled-out/6` - scoped out because the first-recurrence taper recommendation's 10-day comparator and taper action are represented by the taper rows.
- `p34/grade-spelled-out/9` - scoped out because the >1-recurrence population, taper, and rifaximin-chaser branches are represented by the adjacent threshold rows.
- `p34/grade-spelled-out/11` - scoped out because FMT after failed appropriate antibiotic treatments uses an unnumbered multiple-recurrence population and states no additional numeric cutoff.
- `p37/grade-spelled-out/1` - scoped out because the pediatric initial and first-recurrence nonsevere recommendation points to dosing that is represented from rendered Table 2.
- `p37/grade-spelled-out/2` - scoped out because the severe-pediatric vancomycin recommendation is represented with the numeric regimen from rendered Table 2.
- `p38/grade-spelled-out/1` - scoped out because pediatric FMT after multiple recurrences and standard treatment failure states no distinct numeric cutoff.

ADR 0009 disposition: the numeric patient-action regimens, testing boundaries, surveillance definitions, isolation timing, room-cleaning cadence, severity criteria, recurrence branches, surgical triggers, donor interval, and FMT preparation and eligibility thresholds in Tables 1 and 2 and the narrative are represented above. Same-day test-result isolation and daily sporicidal cleaning are retained as event- and cadence-bounded actions.

ADR 0009 disposition: epidemiologic rates, prevalence, incidence, attributable deaths, exposure frequencies, colonization estimates, costs, and population burden figures describe disease or systems rather than numbers that change what is done to an individual patient and are scoped out.

ADR 0009 disposition: trial eligibility, enrollment, treatment arms not adopted by the guideline, follow-up periods, response and recurrence rates, effect estimates, confidence intervals, adverse-event rates, and pharmacologic or laboratory-performance measurements are evidence descriptors rather than patient-action thresholds and are scoped out.

ADR 0009 disposition: evidence tables and figures outside rendered treatment Tables 1 and 2 report study characteristics, diagnostic performance, epidemiology, or outcomes. Their numeric contents are scoped out unless the guideline separately adopts the number as an action row above; qualitative infection-control, stewardship, operative, and FMT recommendations remain in the source but do not generate numeric rows.
