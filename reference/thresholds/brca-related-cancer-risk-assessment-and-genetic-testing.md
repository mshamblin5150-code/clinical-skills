# BRCA-related cancer risk assessment and genetic testing — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction. Each recommendation record is preserved as a separate action so no recommendation is silently collapsed into another.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2019 | USPSTF | USPSTF/brca-related-cancer-final-RS_v2 | recommendation-statement | 2019 | 2019 | https://doi.org/10.1001/jama.2019.10987 | stated | exact |

## Scope

**Read:** pages 1-10, including recommendation tables, supportive narrative, figures, and administrative material; the references are retired by class.

**Not read:** nothing in the source page range.

**Source: `uspstf-2019`**

| span | pages | read |
| --- | --- | --- |
| recommendation, clinical considerations, evidence, response, and recommendations of others | 1-9 | yes |
| article information | 10 | read 2026-08-30; blind 2026-08-30 |
| references | 10-14 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| women-familial-risk-assessment | women who have family members with breast, ovarian, tubal, or peritoneal cancer or have a personal history of these types of cancer |

## Quantities

| key | verbatim |
| --- | --- |
| ontario-tool-referral-score | Ontario Family History Assessment Tool referral score |
| manchester-tool-risk-score | Manchester Scoring System score corresponding to a 10% chance of identifying a BRCA1 or BRCA2 mutation |
| referral-screening-tool-check-count | Referral Screening Tool number of checks that triggers referral |
| pedigree-tool-referral-score | Pedigree Assessment Tool referral score |
| seven-question-positive-count | Seven-Question Family History Screening number of positive responses that initiates referral |
| ibis-mutation-risk | International Breast Cancer Intervention Study model personal mutation-risk level for referral |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ontario-tool-referral-score | women-familial-risk-assessment | >=10 points | "Referral with score of 10 or greater corresponds to doubling of lifetime risk for breast cancer (22%)." | uspstf-2019 | p5 | p5/narrative/ontario-referral-score | narrative |
| manchester-tool-risk-score | women-familial-risk-assessment | 10 points in either column or 15 combined = 10% mutation chance | "A score of 10 in either column or a combined score of 15 for both columns would be equivalent to a 10% chance of identifying a BRCA1 or BRCA2 mutation." | uspstf-2019 | p5 | p5/narrative/manchester-risk-score | narrative |
| referral-screening-tool-check-count | women-familial-risk-assessment | >=2 checks | "Referral if 2 or more checks in table." | uspstf-2019 | p6 | p6/narrative/referral-screening-tool | narrative |
| pedigree-tool-referral-score | women-familial-risk-assessment | >=8 points | "Score 8 or greater is the optimal referral threshold." | uspstf-2019 | p6 | p6/narrative/pedigree-referral-score | narrative |
| seven-question-positive-count | women-familial-risk-assessment | one positive response | "One positive response initiates referral." | uspstf-2019 | p7 | p7/narrative/seven-question-referral | narrative |
| ibis-mutation-risk | women-familial-risk-assessment | >=10% | "Referral for genetic testing if the personal risk level for a mutation in breast cancer susceptibility gene 1 or 2 is 10% or greater." | uspstf-2019 | p7 | p7/narrative/ibis-referral-risk | narrative |

## Conflicts

## Coverage

- `p1/risk-assessment-genetic-counseling-and-genetic-t/1` - recommendation defines the action pathway but states no numeric decision point
- `p1/risk-assessment-genetic-counseling-and-genetic-t/2` - recommendation states no numeric decision point
