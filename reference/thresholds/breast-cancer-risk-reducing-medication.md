# Breast cancer risk-reducing medication — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2019 | USPSTF | USPSTF/breast-cancer-meds-final-recommendation | recommendation-statement | 2019 | 2019 | https://doi.org/10.1001/jama.2019.11885 | stated | exact |

## Scope

**Read:** pages 1-9, including the recommendation, rationale, clinical considerations, risk assessment, medication selection and duration, evidence discussion, public-comment response, recommendations of others, and article information; the reference list was retired by class.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| recommendation through article information | 1-9 | yes |
| references | 9-11 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| women-increased-risk-low-harm-risk | women who are at increased risk for breast cancer and at low risk for adverse medication effects |
| women-not-increased-risk | women who are not at increased risk for breast cancer |
| asymptomatic-women-35-or-older | asymptomatic women 35 years and older |
| women-current-or-previous-breast-cancer-or-dcis | women who have a current or previous diagnosis of breast cancer or ductal carcinoma in situ |
| women-being-assessed-for-increased-risk | women at increased risk |
| women-with-low-five-year-risk | women with a low 5-year risk of breast cancer |
| postmenopausal-women | postmenopausal women |
| premenopausal-women | premenopausal women |
| trial-participants | participants |

## Quantities

| key | verbatim |
| --- | --- |
| risk-reducing-medication-use | prescribe risk-reducing medications |
| recommendation-applicability-age | asymptomatic women 35 years and older |
| recommendation-exclusion | does not apply to women who have a current or previous diagnosis of breast cancer or ductal carcinoma in situ |
| risk-cutoff-universality | There is no single cutoff for defining increased risk for all women |
| five-year-risk-benefit-example | at least a 3% risk for breast cancer in the next 5 years |
| increased-risk-example | examples of combinations of multiple risk factors in women at increased risk |
| lower-risk-example | women with a low 5-year risk of breast cancer should not be routinely offered medications to reduce risk of breast cancer |
| risk-reassessment | repeat risk assessment when there is a significant change in breast cancer risk factors |
| medication-selection-by-menopause | primary breast cancer risk in postmenopausal women |
| medication-use-duration | participants typically used risk-reducing medications for 3 to 5 years |
| tamoxifen-benefit-persistence | Benefits of tamoxifen have been found to persist up to 8 years beyond discontinuation |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| risk-reducing-medication-use | women-increased-risk-low-harm-risk | offer tamoxifen, raloxifene, or an aromatase inhibitor | offer to prescribe risk-reducing medications, such as tamoxifen, raloxifene, or aromatase inhibitors | uspstf-2019 | p1 | p1/medication-use-to-reduce-risk-of-breast-cancer/1 | B |
| risk-reducing-medication-use | women-not-increased-risk | do not routinely use tamoxifen, raloxifene, or an aromatase inhibitor | recommends against the routine use of risk-reducing medications, such as tamoxifen, raloxifene, or aromatase inhibitors | uspstf-2019 | p1 | p1/medication-use-to-reduce-risk-of-breast-cancer/2 | D |
| recommendation-applicability-age | asymptomatic-women-35-or-older | age >=35 years: recommendation applies | applies to asymptomatic women 35 years and older | uspstf-2019 | p1 | p1/narrative/applicability-age | narrative |
| recommendation-exclusion | women-current-or-previous-breast-cancer-or-dcis | recommendation does not apply | does not apply to women who have a current or previous diagnosis of breast cancer or ductal carcinoma in situ | uspstf-2019 | p1 | p1/narrative/recommendation-exclusion | narrative |
| risk-cutoff-universality | women-being-assessed-for-increased-risk | no single universal cutoff defines increased risk | There is no single cutoff for defining increased risk for all women. | uspstf-2019 | p4 | p4/narrative/no-single-risk-cutoff | narrative |
| five-year-risk-benefit-example | women-being-assessed-for-increased-risk | example: 5-year breast cancer risk >=3%: likely more benefit than harm; offer medication if medication-harm risk is low | RENDERED: at least a 3% risk for breast cancer in the next 5 years, are likely to derive more benefit than harm from risk-reducing medications and should be offered these medications if their risk of harms is low. | uspstf-2019 | p4 | p4/narrative/five-year-risk-benefit | narrative |
| increased-risk-example | women-being-assessed-for-increased-risk | example: age >=65 years with >=1 first-degree relative with breast cancer | age 65 years or older with 1 first-degree relative with breast cancer | uspstf-2019 | p4 | p4/narrative/risk-example-65 | narrative |
| increased-risk-example | women-being-assessed-for-increased-risk | example: age >=45 years with >1 first-degree relative, or >=1 first-degree relative diagnosed before age 50 years | 45 years or older with more than 1 first-degree relative with breast cancer or 1 first-degree relative who developed breast cancer before age 50 years | uspstf-2019 | p4 | p4/narrative/risk-example-45 | narrative |
| increased-risk-example | women-being-assessed-for-increased-risk | example: age >=40 years with a first-degree relative with bilateral breast cancer | 40 years or older with a first-degree relative with bilateral breast cancer | uspstf-2019 | p4 | p4/narrative/risk-example-40 | narrative |
| increased-risk-example | women-being-assessed-for-increased-risk | example: atypical ductal or lobular hyperplasia, or lobular carcinoma in situ, on prior biopsy | presence of atypical ductal or lobular hyperplasia or lobular carcinoma in situ on a prior biopsy | uspstf-2019 | p4 | p4/narrative/risk-example-biopsy | narrative |
| lower-risk-example | women-with-low-five-year-risk | low 5-year breast cancer risk: do not routinely offer medication | women with a low 5-year risk of breast cancer should not be routinely offered medications to reduce risk of breast cancer | uspstf-2019 | p5 | p5/narrative/lower-risk-example | narrative |
| risk-reassessment | women-being-assessed-for-increased-risk | no evidence-based fixed interval; repeat when risk factors change significantly | repeat risk assessment when there is a significant change in breast cancer risk factors | uspstf-2019 | p5 | p5/narrative/risk-reassessment | narrative |
| medication-selection-by-menopause | postmenopausal-women | tamoxifen, raloxifene, or an aromatase inhibitor | Tamoxifen, raloxifene, and aromatase inhibitors all reduce primary breast cancer risk in postmenopausal women. | uspstf-2019 | p4 | p4/narrative/postmenopausal-medications | narrative |
| medication-selection-by-menopause | premenopausal-women | tamoxifen only | only tamoxifen is indicated for risk-reduction of primary breast cancer in premenopausal women. | uspstf-2019 | p5 | p5/narrative/premenopausal-medication | narrative |
| medication-use-duration | trial-participants | 3 to 5 years | participants typically used risk-reducing medications for 3 to 5 years | uspstf-2019 | p5 | p5/narrative/medication-duration | narrative |
| tamoxifen-benefit-persistence | trial-participants | up to 8 years beyond discontinuation | Benefits of tamoxifen have been found to persist up to 8 years beyond discontinuation | uspstf-2019 | p5 | p5/narrative/tamoxifen-benefit-persistence | narrative |

## Conflicts

**CONFLICT: increased-risk-example** — `example: age >=65 years with >=1 first-degree relative with breast cancer`, `example: age >=45 years with >1 first-degree relative, or >=1 first-degree relative diagnosed before age 50 years`, `example: age >=40 years with a first-degree relative with bilateral breast cancer`, and `example: atypical ductal or lobular hyperplasia, or lobular carcinoma in situ, on prior biopsy` are alternative examples of combinations that may identify increased risk, not competing universal cutoffs.

## Coverage

Every exact recommendation record is cited above.
