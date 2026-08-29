# Prediabetes and type 2 diabetes screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from both source documents below. **Not a substitute
for either guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | version | published | url | mode |
| --- | --- | --- | --- | --- | --- | --- |
| uspstf-2021 | USPSTF | USPSTF/prediabetes-type2-diabetes-adult-final-recommendation | 2021 | 2021 | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/screening-for-prediabetes-and-type-2-diabetes | exact |
| uspstf-2022 | USPSTF | USPSTF/diabetes-child-final-recommendation | 2022 | 2022 | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/prediabetes-type2-diabetes-children-adolescents-screening | exact |

## Scope

**Read:** both recommendation statements represented by the two source records, plus
the 2022 article information and references (null read independently confirmed
2026-08-23). The 2021 reference list is retired by class because it is a citation
list with no clinical prose.

**Not read:** the 2021 importance and rationale; both practice-consideration spans;
and both supporting-evidence spans, including research needs and recommendations of
others. Each contains narrative decision points that cannot be represented under the
current exact-source contract while #464 remains open.

**Source: `uspstf-2021`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement | 1 | yes |
| importance and rationale | 1-2 | no |
| practice considerations | 3-4 | no |
| supporting evidence, research needs, and recommendations of others | 4-6 | no |
| references | 6-8 | exempt: citation list has no clinical prose |

**Source: `uspstf-2022`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | read 2026-08-22 |
| practice considerations | 2-3 | no |
| supporting evidence | 3-4 | no |
| article information and references | 5 | read 2026-08-23 |

citations resolved against C:/codeing/guidelines-src on 2026-08-22
extraction identity: producer 794297463096430132fc936043438fd64a607dd7; tools/guidelines_extract.py sha256 f8e95baf7e4e74328a752d89e1e7b617217ba1e43c4368fba92f789840e21cf9

## Populations

| key | verbatim |
| --- | --- |
| adults-35-70-overweight-obesity | adults aged 35 to 70 years who have overweight or obesity |

## Quantities

| key | verbatim |
| --- | --- |
| screening-age-range | aged 35 to 70 years |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| screening-age-range | adults-35-70-overweight-obesity | 35-70 years | "aged 35 to 70 years" | uspstf-2021 | p1 | p1/screening-for-prediabetes-and-type-2-diabetes/1 | B |

## Conflicts

None.

## Coverage

- `p1/screening-for-prediabetes-and-type-2-diabetes-in/1` - pediatric statement gives no numeric decision point
