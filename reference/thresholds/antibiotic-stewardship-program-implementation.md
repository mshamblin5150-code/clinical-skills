# Antibiotic stewardship program implementation — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-shea-2016 | IDSA | IDSA/ciw118 | guideline | 2016 | 2016 | https://doi.org/10.1093/cid/ciw118 | stated | bound |

## Scope

**Read:** the complete 27-page guideline, including the title material, executive
summary, introduction, methods, all 28 recommendation sections and comments, evidence
summaries, three tables, the GRADE figure, conclusions, acknowledgments, disclosures,
and reference list. Tables 1-3 and Figure 1 were read in their page context. The bound
recommendation record contains 44 extracted occurrences; it is not a complete inventory
of the source's recommendations, so `## Coverage` accounts only for those 44 record
entries while the full-page read accounts for the guideline itself.

**Not read:** nothing in the source page range. The reference list was inspected for
scope and retired by class because it contains citations rather than clinical prose.

**Scoped out under ADR 0009's numeric patient-action rule:** dates, study sizes,
percentages, confidence intervals, risk estimates, costs, utilization and outcome
rates, literature-search and guideline-development numbers, historical policy targets,
diagnostic performance, and program outcome-measure windows were read but do not
themselves change what is done to a patient.
Qualitative recommendations are accounted for under `## Coverage` when they contain no
numeric dose, duration, target, cutoff, or follow-up interval.

**Source: `idsa-shea-2016`**

| span | pages | read |
| --- | --- | --- |
| title material, executive summary, introduction, and methods | 1-7 | read 2026-08-31; blind 2026-08-31 |
| core stewardship interventions and their evidence | 8-12 | yes |
| pharmacokinetic optimization, oral transition, allergy assessment, and treatment duration | 13-15 | yes |
| microbiology and diagnostic interventions | 15-18 | yes |
| measurement and special-population interventions | 18-21 | yes |
| terminal illness and conclusions | 21-22 | yes |
| acknowledgments and disclosures | 22-23 | read 2026-08-31; blind 2026-08-31 |
| references | 23-27 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| institutions-using-preauthorization | Institutions that use preauthorization |
| senior-resident-on-medical-care-team | a senior resident on the medical care team |
| clinicians | clinicians |
| physicians | physicians |
| hospitalized-patients | hospitalized patients |
| community-hospital-253-bed | a 253-bed community hospital |
| patient-location-or-population | patient location or population |
| residents | residents |
| blood-specimens | blood specimens |
| hospitalized-children-with-hematologic-malignancies-and-fever | hospitalized children with hematologic malignancies and fever |
| single-va-long-term-care-facility | a single Veterans Affairs long-term care facility |
| nursing-staff | The nursing staff |
| adult-inpatients-with-cap | adult inpatients with CAP |
| inpatients-with-sstis | inpatients with SSTIs |
| adults-and-children-with-cap | Adults and children with CAP |
| adults-with-vap | Adults with VAP |
| adults-with-cap | Adults with CAP |
| children-with-cap | Children with CAP |
| adults-with-cellulitis | Adults with cellulitis |
| adult-females-with-acute-pyelonephritis | Adult females with acute pyelonephritis |
| women-with-acute-uncomplicated-pyelonephritis | Women with acute uncomplicated pyelonephritis |
| adults-with-spontaneous-bacterial-peritonitis | Adults with spontaneous bacterial peritonitis |
| neonatal-septicemia | Neonatal septicemia |
| adults-with-intra-abdominal-infection | Adults with intra-abdominal infection |
| adults-with-vertebral-osteomyelitis | Adults with vertebral osteomyelitis |
| women-60-years-or-younger | women 60 years or younger |

## Quantities

| key | verbatim |
| --- | --- |
| preauthorization-approver-availability | 24-hour availability |
| preauthorization-overnight-bridge | administration of the restricted antibiotic overnight until approval can be obtained the next day |
| paf-weekly-frequency | PAF intervention conducted 3 days a week |
| prescriber-led-timeout-frequency | antibiotic time-out audit |
| iv-antibiotic-reassessment-time | review IV therapy |
| vancomycin-stop-order-duration | stop orders for vancomycin |
| aminoglycoside-alternative-dosing-frequency | once-daily dosing |
| stratified-antibiogram-isolate-minimum | at least 30 isolates are available for each organism |
| susceptibility-results-reported | antibiotic susceptibility results |
| rapid-blood-test-operating-frequency | rapid testing should be performed continuously |
| pediatric-galactomannan-monitoring-frequency | monitored twice weekly |
| telephone-consultation-availability | 24/7 consultation availability by telephone |
| onsite-case-review-frequency | weekly on-site case review |
| nursing-home-treatment-review-time | record compliance with good practice points |
| adult-inpatient-cap-treatment-duration | duration of antibiotic therapy |
| inpatient-ssti-treatment-duration | duration of therapy |
| adult-cap-treatment-duration | Treatment Duration, d |
| adult-vap-treatment-duration | Treatment Duration, d |
| pediatric-cap-treatment-duration | Treatment Duration, d |
| adult-cellulitis-treatment-duration | Treatment Duration, d |
| acute-pyelonephritis-treatment-duration | Treatment Duration, d |
| spontaneous-bacterial-peritonitis-treatment-duration | Treatment Duration, d |
| neonatal-septicemia-treatment-duration | Treatment Duration, d |
| intra-abdominal-infection-treatment-duration | Treatment Duration, d |
| vertebral-osteomyelitis-treatment-duration | Treatment Duration, d |
| asymptomatic-bacteriuria-antibiotic-treatment | unnecessary antibiotic treatment |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| preauthorization-approver-availability | institutions-using-preauthorization | provide 24-hour availability for the person giving approval | "To provide 24-hour availability" | idsa-shea-2016 | p8 | p8/narrative/preauthorization-approver-availability | narrative |
| preauthorization-overnight-bridge | institutions-using-preauthorization | allow the restricted antibiotic overnight until approval is obtained the next day | "the restricted antibiotic overnight until approval can be obtained the next day" | idsa-shea-2016 | p8 | p8/narrative/preauthorization-overnight-bridge | narrative |
| paf-weekly-frequency | community-hospital-253-bed | conduct pharmacist-driven prospective audit and feedback 3 days a week | "3 days a week at a 253-bed community hospital" | idsa-shea-2016 | p9 | p9/narrative/paf-weekly-frequency | narrative |
| prescriber-led-timeout-frequency | senior-resident-on-medical-care-team | perform the structured antibiotic time-out audit twice weekly | "antibiotic time-out audit to be performed twice weekly" | idsa-shea-2016 | p11 | p11/narrative/prescriber-led-timeout-frequency | narrative |
| iv-antibiotic-reassessment-time | clinicians | prompt review of intravenous therapy at 72 hours | "clinicians were prompted to review IV therapy at 72 hours" | idsa-shea-2016 | p12 | p12/narrative/iv-antibiotic-reassessment-time | narrative |
| vancomycin-stop-order-duration | physicians | pair a 3-day vancomycin stop order with a safety mechanism | "best studied for 3-day stop orders for vancomycin" | idsa-shea-2016 | p12 | p12/narrative/vancomycin-stop-order-duration | narrative |
| aminoglycoside-alternative-dosing-frequency | hospitalized-patients | once-daily aminoglycoside dosing is an example of a pharmacokinetic/pharmacodynamic alternative strategy | "for aminoglycosides, such as once-daily dosing" | idsa-shea-2016 | p13 | p13/narrative/aminoglycoside-alternative-dosing-frequency | narrative |
| stratified-antibiogram-isolate-minimum | patient-location-or-population | use at least 30 isolates for each organism when stratifying the antibiogram | "patient location or population if at least 30 isolates are available for each organism" | idsa-shea-2016 | p15 | p15/narrative/stratified-antibiogram-isolate-minimum | narrative |
| susceptibility-results-reported | residents | selectively report susceptibility results for 2-4 antibiotics rather than all 25 tested antibiotics | "antibiotic susceptibility results for 2-4 antibiotics, or to a control group, which received full-length results for all 25 antibiotics tested" | idsa-shea-2016 | p16 | p16/narrative/susceptibility-results-reported | narrative |
| rapid-blood-test-operating-frequency | blood-specimens | perform rapid testing continuously, 24/7, or at least in frequent batches | "rapid testing should be performed continuously (ie, 24/7) or at least in frequent batches" | idsa-shea-2016 | p17 | p17/narrative/rapid-blood-test-operating-frequency | narrative |
| pediatric-galactomannan-monitoring-frequency | hospitalized-children-with-hematologic-malignancies-and-fever | monitor galactomannan twice weekly when used as an adjunctive tool | "GM assay is a useful adjunctive tool when monitored twice weekly in hospitalized children with hematologic malignancies and fever" | idsa-shea-2016 | p18 | p18/narrative/pediatric-galactomannan-monitoring-frequency | narrative |
| telephone-consultation-availability | single-va-long-term-care-facility | provide infectious diseases consultation availability by telephone 24/7 | "24/7 consultation availability by telephone" | idsa-shea-2016 | p21 | p21/narrative/telephone-consultation-availability | narrative |
| onsite-case-review-frequency | single-va-long-term-care-facility | conduct on-site case review weekly | "weekly on-site case review" | idsa-shea-2016 | p21 | p21/narrative/onsite-case-review-frequency | narrative |
| nursing-home-treatment-review-time | nursing-staff | record compliance at treatment initiation and again 48-72 hours later | "at treatment initiation and 48-72 hours later" | idsa-shea-2016 | p21 | p21/narrative/nursing-home-treatment-review-time | narrative |
| adult-inpatient-cap-treatment-duration | adult-inpatients-with-cap | reduce the median duration from 10 days to 7 days | "median decrease in antibiotic use from 10 to 7 days" | idsa-shea-2016 | p15 | p15/narrative/adult-inpatient-cap-treatment-duration | narrative |
| inpatient-ssti-treatment-duration | inpatients-with-sstis | reduce duration from 13 days to 10 days | "duration of therapy (from 13 to 10 days" | idsa-shea-2016 | p15 | p15/narrative/inpatient-ssti-treatment-duration | narrative |
| adult-cap-treatment-duration | adults-and-children-with-cap | shorter course 3-7 days versus longer course 5-10 days | "Adults and children with CAP 3-7 vs 5-10" | idsa-shea-2016 | p16 | p16/narrative/adult-cap-treatment-duration-meta | narrative |
| adult-vap-treatment-duration | adults-with-vap | shorter course 7-8 days versus longer course 10-15 days | "Adults with VAP 7-8 vs 10-15" | idsa-shea-2016 | p16 | p16/narrative/adult-vap-treatment-duration-meta | narrative |
| adult-vap-treatment-duration | adults-with-vap | shorter course 8 days versus longer course 15 days; except that nonfermenting gram-negative bacilli had more recurrent infection with the shorter course | "Adults with VAP 8 vs 15" | idsa-shea-2016 | p16 | p16/narrative/adult-vap-treatment-duration-rct | narrative |
| adult-cap-treatment-duration | adults-with-cap | shorter course 3 days versus longer course 5 days | "Adults with CAP 3 vs 5" | idsa-shea-2016 | p16 | p16/narrative/adult-cap-treatment-duration-rct | narrative |
| pediatric-cap-treatment-duration | children-with-cap | 5 days was not inferior to 10 days; 3 days was not shown noninferior | "The 5-day, but not the 3-day, course was not inferior to the 10-day course" | idsa-shea-2016 | p16 | p16/narrative/pediatric-cap-treatment-duration | narrative |
| adult-cellulitis-treatment-duration | adults-with-cellulitis | shorter course 5 days versus longer course 10 days | "Adults with cellulitis 5 vs 10" | idsa-shea-2016 | p16 | p16/narrative/adult-cellulitis-treatment-duration | narrative |
| acute-pyelonephritis-treatment-duration | adult-females-with-acute-pyelonephritis | shorter course 7 days versus longer course 14 days | "Adult females with acute pyelonephritis 7 vs 14" | idsa-shea-2016 | p16 | p16/narrative/acute-pyelonephritis-treatment-duration-females | narrative |
| acute-pyelonephritis-treatment-duration | women-with-acute-uncomplicated-pyelonephritis | shorter course 7 days versus longer course 14 days | "Women with acute uncomplicated pyelonephritis 7 vs 14" | idsa-shea-2016 | p16 | p16/narrative/acute-pyelonephritis-treatment-duration-uncomplicated | narrative |
| spontaneous-bacterial-peritonitis-treatment-duration | adults-with-spontaneous-bacterial-peritonitis | shorter course 5 days versus longer course 10 days | "Adults with spontaneous bacterial peritonitis 5 vs 10" | idsa-shea-2016 | p16 | p16/narrative/spontaneous-bacterial-peritonitis-treatment-duration | narrative |
| neonatal-septicemia-treatment-duration | neonatal-septicemia | shorter course 2-4 days versus 7 days when culture is sterile | "Neonatal septicemia 2-4 vs 7 (with sterile culture)" | idsa-shea-2016 | p16 | p16/narrative/neonatal-septicemia-treatment-duration | narrative |
| intra-abdominal-infection-treatment-duration | adults-with-intra-abdominal-infection | shorter course 4 days versus no more than 10 days | "Adults with intra-abdominal infection 4 vs ≤10" | idsa-shea-2016 | p16 | p16/narrative/intra-abdominal-infection-treatment-duration | narrative |
| vertebral-osteomyelitis-treatment-duration | adults-with-vertebral-osteomyelitis | shorter course 42 days versus longer course 84 days | "Adults with vertebral osteomyelitis 42 vs 84" | idsa-shea-2016 | p16 | p16/narrative/vertebral-osteomyelitis-treatment-duration | narrative |
| asymptomatic-bacteriuria-antibiotic-treatment | women-60-years-or-younger | use evidence to reduce unnecessary antibiotic treatment of asymptomatic bacteriuria in women age 60 years or younger | "ASB (eg, in women 60 years or younger" | idsa-shea-2016 | p22 | p22/narrative/asymptomatic-bacteriuria-antibiotic-treatment | narrative |

## Conflicts

CONFLICT: adult-cap-treatment-duration — for `adults-and-children-with-cap`, the meta-analysis compares `3-7 days versus 5-10 days`; for the narrower `adults-with-cap` population, the randomized trial compares `3 days versus 5 days`. These are separate evidence syntheses and populations, not one panel-selected universal course.

CONFLICT: adult-vap-treatment-duration — for `adults-with-vap`, the meta-analyses give `shorter course 7-8 days versus longer course 10-15 days`, while the randomized trial gives `shorter course 8 days versus longer course 15 days; except that nonfermenting gram-negative bacilli had more recurrent infection with the shorter course`.

## Coverage

- `p1/grade-spelled-out/1` - qualitative executive-summary occurrence of the preauthorization and/or prospective-audit recommendation; the numeric availability, overnight bridge, and 3-days-per-week prospective-audit example are cited from the full evidence narrative.
- `p2/grade-spelled-out/1` - qualitative recommendation against relying solely on didactic education states no numeric patient-action point.
- `p2/grade-spelled-out/2` - qualitative facility-specific guideline recommendation states no numeric patient-action point.
- `p3/grade-spelled-out/1` - qualitative syndrome-targeted intervention recommendation states no numeric patient-action point.
- `p3/grade-spelled-out/2` - qualitative high-CDI-risk antibiotic intervention recommendation states no numeric patient-action point.
- `p3/grade-spelled-out/3` - qualitative prescriber-review recommendation; numeric time-out examples are cited from the full evidence narrative.
- `p3/grade-spelled-out/4` - qualitative computerized decision-support recommendation states no numeric patient-action point.
- `p3/grade-spelled-out/5` - qualitative recommendation against antibiotic cycling states no numeric patient-action point.
- `p3/grade-spelled-out/6` - qualitative aminoglycoside pharmacokinetic-monitoring recommendation; the once-daily example is cited from the full evidence narrative.
- `p3/grade-spelled-out/7` - qualitative vancomycin pharmacokinetic-monitoring recommendation states no numeric dose, level, or interval.
- `p3/grade-spelled-out/8` - qualitative alternative broad-spectrum beta-lactam dosing recommendation states no numeric dose or interval.
- `p4/grade-spelled-out/1` - qualitative oral-antibiotic and intravenous-to-oral transition recommendation states no numeric transition criterion.
- `p4/grade-spelled-out/2` - qualitative beta-lactam allergy-assessment recommendation states no numeric testing criterion.
- `p4/grade-spelled-out/3` - qualitative shortest-effective-duration recommendation; the decision-changing comparative treatment durations and qualifying footnotes are cited from the full evidence narrative and Table 2.
- `p4/grade-spelled-out/4` - qualitative stratified-antibiogram recommendation; the isolate minimum is cited from the full evidence narrative.
- `p4/grade-spelled-out/5` - qualitative selective or cascade reporting recommendation; the evidence example comparing 2-4 selectively reported antibiotics with all 25 tested antibiotics is cited from the full narrative.
- `p4/grade-spelled-out/6` - qualitative rapid respiratory-virus testing recommendation states no numeric testing interval.
- `p4/grade-spelled-out/7` - qualitative rapid blood-specimen diagnostic recommendation; the operating frequency is cited from the full evidence narrative.
- `p5/grade-spelled-out/1` - qualitative serial-procalcitonin recommendation states no numeric procalcitonin cutoff or testing interval.
- `p5/grade-spelled-out/2` - qualitative nonculture fungal-marker recommendation; the twice-weekly pediatric galactomannan frequency is cited from the full evidence narrative.
- `p5/grade-spelled-out/3` - qualitative days-of-therapy measurement recommendation states no numeric patient-action point.
- `p5/grade-spelled-out/4` - qualitative antifungal-stewardship recommendation states no numeric dose, duration, target, cutoff, or interval.
- `p7/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative preauthorization and/or prospective-audit recommendation; the numeric availability, overnight bridge, and prospective-audit frequency are cited from narrative rows above.
- `p9/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative recommendation against relying solely on didactic education.
- `p9/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative facility-specific guideline recommendation.
- `p10/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative syndrome-targeted intervention recommendation.
- `p11/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative high-CDI-risk antibiotic intervention recommendation.
- `p11/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative prescriber-review recommendation; the twice-weekly time-out, 72-hour intravenous review, and 3-day vancomycin stop-order examples are cited from narrative rows above.
- `p12/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative computerized decision-support recommendation.
- `p12/grade-spelled-out/2` - duplicate full-text occurrence of the recommendation against antibiotic cycling.
- `p13/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative aminoglycoside pharmacokinetic-monitoring recommendation.
- `p13/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative vancomycin pharmacokinetic-monitoring recommendation.
- `p13/grade-spelled-out/3` - duplicate full-text occurrence of the qualitative alternative broad-spectrum beta-lactam dosing recommendation.
- `p14/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative oral-antibiotic and intravenous-to-oral transition recommendation.
- `p15/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative shortest-effective-duration recommendation; comparative CAP, SSTI, VAP, cellulitis, pyelonephritis, spontaneous bacterial peritonitis, neonatal septicemia, intra-abdominal infection, and vertebral osteomyelitis durations are cited from the narrative and Table 2.
- `p15/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative stratified-antibiogram recommendation; the isolate minimum is cited from narrative above.
- `p15/grade-spelled-out/3` - duplicate full-text occurrence of the qualitative selective or cascade reporting recommendation; the 2-4-versus-25 antibiotic reporting example is cited from narrative above.
- `p16/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative rapid respiratory-virus testing recommendation.
- `p17/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative rapid blood-specimen diagnostic recommendation; the operating frequency is cited from narrative above.
- `p17/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative serial-procalcitonin recommendation.
- `p18/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative nonculture fungal-marker recommendation; the twice-weekly pediatric frequency is cited from narrative above.
- `p18/grade-spelled-out/2` - duplicate full-text occurrence of the qualitative days-of-therapy measurement recommendation.
- `p19/grade-spelled-out/1` - qualitative fever-and-neutropenia guideline recommendation states no numeric patient-action point.
- `p20/grade-spelled-out/1` - duplicate full-text occurrence of the qualitative antifungal-stewardship recommendation.
