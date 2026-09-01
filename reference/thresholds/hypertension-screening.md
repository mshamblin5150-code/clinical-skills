# Hypertension screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2021 | USPSTF | USPSTF/hypertension-screening-adults-final-rec-statement | recommendation-statement | 2021 | 2021 | https://doi.org/10.1001/jama.2021.4987 | stated | exact |

## Scope

**Read:** the complete recommendation statement, including the recommendation,
practice considerations, measurement technique, screening intervals, implementation,
supporting evidence, response, research needs, and recommendations of others on pp.
1-5. The reference list on pp. 6-7 is retired by class because it contains citations
rather than clinical prose.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's numeric decision-point rule:** the page 1
recommendation also directs out-of-office blood pressure measurement for diagnostic
confirmation before treatment. That qualitative confirmation instruction was read,
but it states no number that changes patient action and therefore does not produce a
threshold row. The recommendation itself remains accounted for by the age cutoff row
below.

| span | pages | read |
| --- | --- | --- |
| complete recommendation-statement narrative | 1-5 | yes |
| references | 6-7 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults-without-known-hypertension | adults 18 years or older without known hypertension |
| adults-40-or-increased-risk | adults 40 years or older and adults at increased risk for hypertension |
| adults-18-39-low-risk-normal | adults aged 18 to 39 years not at increased risk for hypertension and with a prior normal blood pressure reading |
| adults-screened-for-hypertension | adults undergoing screening for hypertension |
| adults-office-sbp-120-129-or-dbp-75-79 | adults who consistently have systolic blood pressure measurements of 120 to 129 mm Hg or diastolic blood pressure measurements of 75 to 79 mm Hg in the office |
| adults-office-sbp-130-160-or-dbp-80-100 | adults who consistently have systolic blood pressure measurements of 130 to 160 mm Hg or diastolic measurements of 80 to 100 mm Hg in the office |
| adults-bp-below-120-80 | adults with blood pressure less than 120/80 mm Hg |
| adults-bp-120-139-or-80-89 | adults with blood pressure of 120 to 139/80 to 89 mm Hg |

## Quantities

| key | verbatim |
| --- | --- |
| hypertension-screening | screening for hypertension |
| screening-interval | optimal screening interval for hypertension |
| office-measurement-technique | office blood pressure measurement technique |
| ambulatory-measurement-schedule | ambulatory blood pressure monitoring schedule |
| home-measurement-schedule | home blood pressure monitoring schedule |
| hypertension-definition-range | threshold used to define hypertension |
| jnc-screening-interval | Seventh Joint National Committee screening interval |
| masked-hypertension-screening | ACC/AHA screening for masked hypertension |
| white-coat-hypertension-screening | ACC/AHA screening for white coat hypertension |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hypertension-screening | adults-without-known-hypertension | age >=18 years: office blood pressure measurement | The USPSTF recommends screening for hypertension in adults 18 years or older with office blood pressure measurement. | uspstf-2021 | p1 | p1/screening-for-hypertension-in-adults/1 | A |
| screening-interval | adults-40-or-increased-risk | every year | Screening for hypertension every year in adults 40 years or older and in adults at increased risk for hypertension | uspstf-2021 | p2 | p2/narrative/annual-screening | narrative |
| screening-interval | adults-18-39-low-risk-normal | every 3 to 5 years | every 3-5 years | uspstf-2021 | p2 | p2/narrative/low-risk-screening-interval | narrative |
| ambulatory-measurement-schedule | adults-screened-for-hypertension | every 20 to 30 minutes over 12 to 24 hours | typically in 20- to 30-minute intervals over 12 to 24 hours | uspstf-2021 | p2 | p2/narrative/ambulatory-measurement-schedule | narrative |
| home-measurement-schedule | adults-screened-for-hypertension | 1 to 2 times a day or week | 1 to 2 times a day or week | uspstf-2021 | p2 | p2/narrative/home-measurement-schedule | narrative |
| office-measurement-technique | adults-screened-for-hypertension | brachial artery, validated accurate device, seated after 5 minutes rest | taken at the brachial artery (upper arm) with a validated and accurate device in a seated position after 5 minutes of rest | uspstf-2021 | p2 | p2/narrative/office-measurement-technique | narrative |
| hypertension-definition-range | adults-screened-for-hypertension | 130/80 mm Hg to 140/90 mm Hg | ranges from 130/80 mm Hg or greater to 140/90 mm Hg or greater | uspstf-2021 | p3 | p3/narrative/hypertension-definition-range | narrative |
| jnc-screening-interval | adults-bp-below-120-80 | at least every 2 years | at least once every 2 years in adults with blood pressure less than 120/80 mm Hg | uspstf-2021 | p5 | p5/narrative/jnc-low-bp-screening-interval | narrative |
| jnc-screening-interval | adults-bp-120-139-or-80-89 | every year | every year in adults with blood pressure of 120 to 139/80 to 89 mm Hg | uspstf-2021 | p5 | p5/narrative/jnc-high-normal-screening-interval | narrative |
| masked-hypertension-screening | adults-office-sbp-120-129-or-dbp-75-79 | office SBP 120 to 129 mm Hg or DBP 75 to 79 mm Hg: ABPM or HBPM | systolic blood pressure measurements of 120 to 129 mm Hg or diastolic blood pressure measurements of 75 to 79 mm Hg in the office | uspstf-2021 | p5 | p5/narrative/masked-hypertension-screening | narrative |
| white-coat-hypertension-screening | adults-office-sbp-130-160-or-dbp-80-100 | office SBP 130 to 160 mm Hg or DBP 80 to 100 mm Hg: screen for white coat hypertension | RENDERED: systolic blood pressure measurements of 130 to 160 mm Hg or diastolic measurements of 80 to 100 mm Hg in the office | uspstf-2021 | p5 | p5/narrative/white-coat-hypertension-screening | narrative |

## Conflicts

CONFLICT: screening-interval — every year applies to adults age 40 years or older or
at increased risk; every 3 to 5 years applies to adults age 18 to 39 years with a
prior normal result and no increased risk.

CONFLICT: jnc-screening-interval — at least every 2 years applies below 120/80 mm Hg;
every year applies at 120 to 139/80 to 89 mm Hg.

## Coverage
