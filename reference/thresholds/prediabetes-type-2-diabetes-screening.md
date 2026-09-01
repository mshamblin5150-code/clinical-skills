# Prediabetes and type 2 diabetes screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from both source documents below. **Not a substitute
for either guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2021 | USPSTF | USPSTF/prediabetes-type2-diabetes-adult-final-recommendation | recommendation-statement | 2021 | 2021 | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/screening-for-prediabetes-and-type-2-diabetes | chosen | exact |
| uspstf-2022 | USPSTF | USPSTF/diabetes-child-final-recommendation | recommendation-statement | 2022 | 2022 | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/prediabetes-type2-diabetes-children-adolescents-screening | chosen | exact |

## Scope

**Read:** both recommendation statements represented by the two source records; the
2021 importance, rationale, practice considerations, and supporting evidence on pp.
1-6; and the 2022 practice considerations and supporting evidence on pp. 2-4. The
2022 article information and references were independently confirmed as a null read
on 2026-08-23. The 2021 reference list is retired by class because it is a citation
list with no clinical prose.

**Not read:** nothing in either source page range.

**Source: `uspstf-2021`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement | 1 | yes |
| importance and rationale | 1-2 | yes |
| practice considerations | 3-4 | yes |
| supporting evidence, research needs, and recommendations of others | 4-6 | read 2026-08-29; blind 2026-08-29 |
| references | 6-8 | exempt: citation list has no clinical prose |

**Source: `uspstf-2022`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations | 2-3 | yes |
| supporting evidence | 3-4 | read 2026-08-29; blind 2026-08-29 |
| article information and references | 5 | read 2026-08-23; blind 2026-08-23 |

**Second read:** a blind independent read dated 2026-08-29 reviewed the 2021 and
2022 supporting-evidence spans and corroborated the current USPSTF decision points recorded below. Its
separate read of the 2021 supporting-evidence span found no additional row beyond the
age-35 decision already represented by the recommendation-statement row; its separate
read of the 2022 supporting-evidence span found no current USPSTF decision point. The
remaining numeric candidates were epidemiology, trial or evidence results, obsolete
prior recommendations, or recommendations attributed to other organizations. A cold
read dated 2026-08-30 of the 2022 recommendation statement and assessment found the
quantity-bearing decision points already represented by its page-2 rows, so that
span is positive rather than retired on a null claim.

citations resolved against C:/codeing/guidelines-src on 2026-08-29
extraction identity: producer e0e241393b3cf92231a7c40123046db47cdcb57b; tools/guidelines_extract.py sha256 f8e95baf7e4e74328a752d89e1e7b617217ba1e43c4368fba92f789840e21cf9

## Populations

| key | verbatim |
| --- | --- |
| adults-35-70-overweight-obesity | adults aged 35 to 70 years who have overweight or obesity |
| adults-normal-blood-glucose | adults with normal blood glucose levels |
| adults-prediabetes | persons with prediabetes |
| asian-american-adults | Asian American persons |
| children-adolescents-under-18-asymptomatic | children and adolescents younger than 18 years without known diabetes or prediabetes or symptoms of diabetes or prediabetes |
| nonpregnant-adults | nonpregnant adults |

## Quantities

| key | verbatim |
| --- | --- |
| adult-bmi-definitions-overweight-obesity | Overweight and obesity are defined as a BMI ≥25 and ≥30, respectively |
| asian-american-screening-bmi-cut-point | a BMI of 23 or greater may be an appropriate cut point in Asian American persons |
| diabetes-diagnostic-glycemic-thresholds | A fasting plasma glucose level of 126 mg/dL (6.99 mmol/L) or greater, an HbA1c level of 6.5% or greater, or a 2-hour postload glucose level of 200 mg/dL (11.1 mmol/L) or greater |
| metformin-favoring-prediabetes-profile | metformin was effective in persons younger than 60 years, in persons with a BMI of 35 or greater, in persons with a fasting plasma glucose level of 110 mg/dL (6.11 mmol/L) or greater, or in persons with a history of gestational diabetes |
| obesity-behavioral-intervention-bmi-threshold | adults with a BMI of 30 or greater |
| oral-glucose-tolerance-test-protocol | blood glucose concentration is measured 2 hours after ingestion of a 75-g oral glucose load |
| pediatric-diabetes-diagnostic-glycemic-thresholds | A fasting plasma glucose level of 126 mg/dL (7.0 mmol/L) or greater, an HbA1c level of 6.5% or greater, or a 2-hour postload glucose level of 200 mg/dL (11.1 mmol/L) or greater |
| pediatric-prediabetes-glycemic-thresholds | A fasting plasma glucose level of 100 to 125 mg/dL (5.6-6.9 mmol/L), an HbA1c level of 5.7% to 6.4%, or a 2-hour postload glucose level of 140 to 199 mg/dL (7.8-11.0 mmol/L) |
| prediabetes-glycemic-thresholds | A fasting plasma glucose level of 100 to 125 mg/dL (5.55-6.94 mmol/L), an HbA1c level of 5.7% to 6.4%, or a 2-hour postload glucose level of 140 to 199 mg/dL (7.77-11.04 mmol/L) |
| screening-age-range | aged 35 to 70 years |
| screening-interval-normal-glucose | Screening every 3 years may be a reasonable approach for adults with normal blood glucose levels |
| screening-population-pediatric-upper-age | children and adolescents younger than 18 years |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| adult-bmi-definitions-overweight-obesity | adults-35-70-overweight-obesity | overweight BMI >=25; obesity BMI >=30 | "Overweight and obesity are defined as a BMI ≥25 and ≥30, respectively" | uspstf-2021 | p2 | p2/narrative/1 | narrative |
| asian-american-screening-bmi-cut-point | asian-american-adults | BMI >=23 | "at a lower BMI (≥23) if the patient is Asian American" | uspstf-2021 | p2 | p2/narrative/2 | narrative |
| screening-interval-normal-glucose | adults-normal-blood-glucose | every 3 years | "Screening every 3 years may be a reasonable approach for adults with normal blood glucose levels" | uspstf-2021 | p2 | p2/narrative/3 | narrative |
| obesity-behavioral-intervention-bmi-threshold | nonpregnant-adults | BMI >=30 | "adults with a BMI ≥30" | uspstf-2021 | p2 | p2/narrative/4 | narrative |
| diabetes-diagnostic-glycemic-thresholds | nonpregnant-adults | fasting plasma glucose >=126 mg/dL (6.99 mmol/L); HbA1c >=6.5%; 2-hour postload glucose >=200 mg/dL (11.1 mmol/L) | "RENDERED: A fasting plasma glucose level of 126 mg/dL (6.99 mmol/L) or greater, an HbA1c level of 6.5% or greater, or a 2-hour postload glucose level of 200 mg/dL (11.1 mmol/L) or greater" | uspstf-2021 | p3 | p3/narrative/1 | narrative |
| prediabetes-glycemic-thresholds | nonpregnant-adults | fasting plasma glucose 100-125 mg/dL (5.55-6.94 mmol/L); HbA1c 5.7%-6.4%; 2-hour postload glucose 140-199 mg/dL (7.77-11.04 mmol/L) | "RENDERED: A fasting plasma glucose level of 100 to 125 mg/dL (5.55-6.94 mmol/L), an HbA1c level of 5.7% to 6.4%, or a 2-hour postload glucose level of 140 to 199 mg/dL (7.77-11.04 mmol/L)" | uspstf-2021 | p3 | p3/narrative/2 | narrative |
| oral-glucose-tolerance-test-protocol | nonpregnant-adults | 2 hours after 75-g oral glucose load | "blood glucose concentration is measured 2 hours after ingestion of a 75-g oral glucose load" | uspstf-2021 | p3 | p3/narrative/3 | narrative |
| metformin-favoring-prediabetes-profile | adults-prediabetes | age <60 years; BMI >=35; fasting plasma glucose >=110 mg/dL (6.11 mmol/L); history of gestational diabetes | "metformin was effective in persons younger than 60 years, in persons with a BMI of 35 or greater, in persons with a fasting plasma glucose level of 110 mg/dL (6.11 mmol/L) or greater, or in persons with a history of gestational diabetes" | uspstf-2021 | p3 | p3/narrative/4 | narrative |
| screening-age-range | adults-35-70-overweight-obesity | 35-70 years | "aged 35 to 70 years" | uspstf-2021 | p1 | p1/screening-for-prediabetes-and-type-2-diabetes/1 | B |
| screening-population-pediatric-upper-age | children-adolescents-under-18-asymptomatic | <18 years | "RENDERED: children and adolescents younger than 18 years" | uspstf-2022 | p2 | p2/narrative/1 | narrative |
| pediatric-prediabetes-glycemic-thresholds | children-adolescents-under-18-asymptomatic | fasting plasma glucose 100-125 mg/dL (5.6-6.9 mmol/L); HbA1c 5.7%-6.4%; 2-hour postload glucose 140-199 mg/dL (7.8-11.0 mmol/L) | "RENDERED: A fasting plasma glucose level of 100 to 125 mg/dL (5.6-6.9 mmol/L), an HbA1c level of 5.7% to 6.4%, or a 2-hour postload glucose level of 140 to 199 mg/dL (7.8-11.0 mmol/L)" | uspstf-2022 | p2 | p2/narrative/2 | narrative |
| pediatric-diabetes-diagnostic-glycemic-thresholds | children-adolescents-under-18-asymptomatic | fasting plasma glucose >=126 mg/dL (7.0 mmol/L); HbA1c >=6.5%; 2-hour postload glucose >=200 mg/dL (11.1 mmol/L) | "RENDERED: A fasting plasma glucose level of 126 mg/dL (7.0 mmol/L) or greater, an HbA1c level of 6.5% or greater, or a 2-hour postload glucose level of 200 mg/dL (11.1 mmol/L) or greater" | uspstf-2022 | p2 | p2/narrative/3 | narrative |
| oral-glucose-tolerance-test-protocol | children-adolescents-under-18-asymptomatic | 2 hours after 75-g oral glucose load | "RENDERED: blood glucose concentration measured 2 hours after ingestion of a 75-g oral glucose load" | uspstf-2022 | p2 | p2/narrative/4 | narrative |

## Conflicts

None.

## Coverage

- `p1/screening-for-prediabetes-and-type-2-diabetes-in/1` - pediatric statement gives no numeric decision point
