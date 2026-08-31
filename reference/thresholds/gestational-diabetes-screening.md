# Gestational diabetes screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2021 | USPSTF | USPSTF/gestational-diabetes-screening-final-recommendation | recommendation-statement | 2021 | 2021 | https://doi.org/10.1001/jama.2021.11922 | stated | exact |

## Scope

**Read:** the complete recommendation statement, including the recommendation,
assessment, practice considerations, screening tests and intervals, treatment,
current practice, supporting evidence, response to public comment, research needs,
recommendations of others, article information, and references on pp. 1-8.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's numeric decision-point rule:** the complete read also
found prevalence, risk-association, test-accuracy, study-eligibility, trial-size,
effect-estimate, outcome-rate, evidence-review, survey, and biologic-timing numbers.
Those numbers describe evidence or disease rather than changing what is done to a
patient. Qualitative statements about risk assessment, initial treatment, escalation
when glucose is not controlled, test choice, and individualized early screening were
also read but state no numeric action point. `## Coverage` separately accounts for
the source's exact recommendation records; it does not enumerate document prose
outside that index.

| span | pages | read |
| --- | --- | --- |
| summary of recommendations, abstract, and importance | 1 | yes |
| USPSTF assessment of magnitude of net benefit and recommendation rationale | 2 | read 2026-08-31; blind 2026-08-31 |
| practice considerations | 2-3 | yes |
| clinician summary | 3 | yes |
| current practice, other related USPSTF recommendations, and update of previous USPSTF recommendation | 4 | read 2026-08-31; blind 2026-08-31 |
| supporting evidence: scope of review, accuracy of screening tests and risk assessment, and Table 2 | 4 | yes |
| supporting evidence: benefits of early detection and treatment, harms of screening and treatment, and biological understanding | 5-6 | read 2026-08-31; blind 2026-08-31 |
| response to public comment and research needs and gaps | 6 | read 2026-08-31; blind 2026-08-31 |
| recommendations of others | 6 | yes |
| article information | 7 | read 2026-08-31; blind 2026-08-31 |
| references | 7-8 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-pregnant-24-weeks-or-after | asymptomatic pregnant persons at 24 weeks of gestation or after |
| asymptomatic-pregnant-before-24-weeks | asymptomatic pregnant persons before 24 weeks of gestation |
| pregnant-without-prior-type1-type2-diabetes | pregnant persons who have not been previously diagnosed with type 1 or type 2 diabetes |
| late-entry-prenatal-care-after-28-weeks | Pregnant persons whose first prenatal visit happens after 28 weeks of gestation (ie, late entry into prenatal care) |
| all-pregnant-women | all pregnant women |
| all-asymptomatic-pregnant-women | all asymptomatic pregnant women |
| asymptomatic-pregnant-women-after-24-weeks | asymptomatic pregnant women after 24 weeks of gestation |
| asymptomatic-pregnant-women-before-24-weeks | asymptomatic pregnant women before 24 weeks of gestation |

## Quantities

| key | verbatim |
| --- | --- |
| uspstf-screening-timing | screening for gestational diabetes |
| one-time-screening-window | One-time screening should be performed at or after 24 weeks of gestation |
| late-entry-screening-timing | screened as soon as possible |
| nonfasting-ogct-screening-window | A 50-g oral glucose challenge test (OGCT) is performed between 24 and 28 weeks of gestation in a nonfasting state |
| two-step-ogct-positive-threshold | If the OGCT is positive, then proceed with OGTT |
| carpenter-coustan-ogtt-diagnostic-thresholds | Carpenter and Coustan |
| nddg-ogtt-diagnostic-thresholds | National Diabetes Data Group (NDDG) |
| iadpsg-ogtt-diagnostic-thresholds | International Association of Diabetes and Pregnancy Study Group (IADPSG) |
| acog-nih-screening-window-and-method | screening all pregnant women for gestational diabetes using a 2-step screening strategy |
| ada-screening-window-and-method | glucose testing for gestational diabetes in all asymptomatic pregnant women |
| endocrine-society-screening-window-and-method | universal screening for gestational diabetes using the OGTT |
| aafp-screening-timing | screening for gestational diabetes in asymptomatic pregnant women |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-screening-timing | asymptomatic-pregnant-24-weeks-or-after | screen at >=24 weeks of gestation | "The USPSTF recommends screening for gestational diabetes in asymptomatic pregnant persons at 24 weeks of gestation or after." | uspstf-2021 | p1 | p1/screening-for-gestational-diabetes/1 | B |
| uspstf-screening-timing | asymptomatic-pregnant-before-24-weeks | before 24 weeks of gestation: evidence insufficient to assess benefits and harms | "The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of screening for gestational diabetes in asymptomatic pregnant persons before 24 weeks of gestation." | uspstf-2021 | p1 | p1/screening-for-gestational-diabetes/2 | I |
| one-time-screening-window | asymptomatic-pregnant-24-weeks-or-after | one time at >=24 weeks; typically before 28 weeks; may occur later with late prenatal care | "One-time screening should be performed at or after 24 weeks of gestation. Typically in the US, screening occurs prior to 28 weeks of gestation; however, it can occur later in persons who enter prenatal care after 28 weeks of gestation." | uspstf-2021 | p3 | p3/narrative/one-time-screening-window | narrative |
| late-entry-screening-timing | late-entry-prenatal-care-after-28-weeks | first prenatal visit after 28 weeks: screen as soon as possible | "Pregnant persons whose first prenatal visit happens after 28 weeks of gestation (ie, late entry into prenatal care) should be screened as soon as possible." | uspstf-2021 | p3 | p3/narrative/late-entry-screening-timing | narrative |
| nonfasting-ogct-screening-window | pregnant-without-prior-type1-type2-diabetes | 50-g OGCT in a nonfasting state at 24-28 weeks of gestation | "RENDERED: A 50-g oral glucose challenge test (OGCT) is performed between 24 and 28 weeks of gestation in a nonfasting state." | uspstf-2021 | p2 | p2/narrative/nonfasting-ogct-screening-window | narrative |
| two-step-ogct-positive-threshold | pregnant-without-prior-type1-type2-diabetes | 50-g OGCT at 1 hour >=130-140 mg/dL: proceed with OGTT | "an initial screening 50-g OGCT is administered. If the OGCT is positive (≥130-140 mg/dL at 1 h), then proceed with OGTT." | uspstf-2021 | p4 | p4/narrative/two-step-ogct-positive-threshold | narrative |
| carpenter-coustan-ogtt-diagnostic-thresholds | pregnant-without-prior-type1-type2-diabetes | 100-g 3-hour OGTT; diagnose if >=2 thresholds met: fasting >=95 mg/dL; 1-hour >=180 mg/dL; 2-hour >=155 mg/dL; 3-hour >=140 mg/dL | "RENDERED: Two-step screening: diagnosis of gestational diabetes if ≥2 thresholds met on OGTT. Carpenter and Coustan: glucose load of OGTT, 100 g; fasting threshold, 95 mg/dL; 1-hour threshold, 180 mg/dL; 2-hour threshold, 155 mg/dL; 3-hour threshold, 140 mg/dL." | uspstf-2021 | p4 | p4/narrative/carpenter-coustan-ogtt-diagnostic-thresholds | narrative |
| nddg-ogtt-diagnostic-thresholds | pregnant-without-prior-type1-type2-diabetes | 100-g 3-hour OGTT; diagnose if >=2 thresholds met: fasting >=105 mg/dL; 1-hour >=190 mg/dL; 2-hour >=165 mg/dL; 3-hour >=145 mg/dL | "RENDERED: Two-step screening: diagnosis of gestational diabetes if ≥2 thresholds met on OGTT. National Diabetes Data Group (NDDG): glucose load of OGTT, 100 g; fasting threshold, 105 mg/dL; 1-hour threshold, 190 mg/dL; 2-hour threshold, 165 mg/dL; 3-hour threshold, 145 mg/dL." | uspstf-2021 | p4 | p4/narrative/nddg-ogtt-diagnostic-thresholds | narrative |
| iadpsg-ogtt-diagnostic-thresholds | pregnant-without-prior-type1-type2-diabetes | 75-g 2-hour OGTT; diagnose if >=1 threshold met: fasting >=92 mg/dL; 1-hour >=180 mg/dL; 2-hour >=153 mg/dL | "RENDERED: One-step screening: diagnosis of gestational diabetes if ≥1 thresholds met on OGTT. International Association of Diabetes and Pregnancy Study Group (IADPSG): glucose load of OGTT, 75 g; fasting threshold, 92 mg/dL; 1-hour threshold, 180 mg/dL; 2-hour threshold, 153 mg/dL; 3-hour threshold, NA." | uspstf-2021 | p4 | p4/narrative/iadpsg-ogtt-diagnostic-thresholds | narrative |
| acog-nih-screening-window-and-method | all-pregnant-women | 24-28 weeks of gestation: 2-step screening using Carpenter and Coustan or NDDG criteria | "RENDERED: The American College of Obstetricians and Gynecologists and the National Institutes of Health recommend screening all pregnant women for gestational diabetes using a 2-step screening strategy (using either Carpenter and Coustan criteria or NDDG criteria) at 24 to 28 weeks of gestation." | uspstf-2021 | p6 | p6/narrative/acog-nih-screening-window-and-method | narrative |
| ada-screening-window-and-method | all-asymptomatic-pregnant-women | 24-28 weeks of gestation: 1-step IADPSG or 2-step Carpenter and Coustan screening | "RENDERED: The American Diabetes Association recommends glucose testing for gestational diabetes in all asymptomatic pregnant women at 24 to 28 weeks of gestation using either 1-step (using IADPSG criteria) or 2-step (using Carpenter and Coustan criteria) screening." | uspstf-2021 | p6 | p6/narrative/ada-screening-window-and-method | narrative |
| endocrine-society-screening-window-and-method | all-pregnant-women | 24-28 weeks of gestation: universal OGTT screening | "RENDERED: The Endocrine Society recommends universal screening for gestational diabetes using the OGTT at 24 to 28 weeks of gestation." | uspstf-2021 | p6 | p6/narrative/endocrine-society-screening-window-and-method | narrative |
| aafp-screening-timing | asymptomatic-pregnant-women-after-24-weeks | screen after 24 weeks of gestation | "screening for gestational diabetes in asymptomatic pregnant women after 24 weeks of gestation." | uspstf-2021 | p6 | p6/narrative/aafp-screening-timing | narrative |
| aafp-screening-timing | asymptomatic-pregnant-women-before-24-weeks | before 24 weeks of gestation: evidence insufficient to assess benefits and harms | "RENDERED: It also concludes that the evidence is insufficient to assess the balance of benefits and harms of screening for gestational diabetes in asymptomatic pregnant women before 24 weeks of gestation." | uspstf-2021 | p6 | p6/narrative/aafp-before-24-weeks-insufficient | narrative |

## Conflicts

## Coverage
