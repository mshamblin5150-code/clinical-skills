# Cardiovascular disease prevention, aspirin — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2022 | USPSTF | USPSTF/aspirin-use-cvd-prevention-final-rec | recommendation-statement | 2022 | 2022 | https://doi.org/10.1001/jama.2022.4983 | stated | exact |

## Scope

**Read:** pages 1-7, including the recommendation, clinical considerations, supporting evidence, response to public comment, recommendations of others, and article information; the reference list was retired by class.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| recommendation through supporting-evidence text | 1-7 | yes |
| references | 8 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| primary-prevention-adults | adults 40 years or older without signs or symptoms of CVD or known CVD and who are not at increased risk for bleeding |

## Quantities

| key | verbatim |
| --- | --- |
| aspirin-initiation-age-and-risk | decision to initiate low-dose aspirin use for the primary prevention of CVD |
| aspirin-dose | use 81 mg/d for patients initiating aspirin use |
| aspirin-stop-age | stopping aspirin use around age 75 years |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aspirin-initiation-age-and-risk | primary-prevention-adults | age 40 to 59 years and 10-year CVD risk >=10%: individual decision | The decision to initiate low-dose aspirin use for the primary prevention of CVD in adults aged 40 to 59 years who have a 10% or greater 10-year CVD risk should be an individual one. | uspstf-2022 | p1 | p1/aspirin-use-to-prevent-cardiovascular-disease/1 | C |
| aspirin-initiation-age-and-risk | primary-prevention-adults | age >=60 years: do not initiate | The USPSTF recommends against initiating low-dose aspirin use for the primary prevention of CVD in adults 60 years or older. | uspstf-2022 | p1 | p1/aspirin-use-to-prevent-cardiovascular-disease/2 | D |
| aspirin-dose | primary-prevention-adults | 81 mg daily is reasonable when initiating | A pragmatic approach would be to use 81 mg/d, which is the most commonly prescribed dose in the US. | uspstf-2022 | p2 | p2/narrative/aspirin-dose | narrative |
| aspirin-stop-age | primary-prevention-adults | consider stopping around age 75 years | it may be reasonable to consider stopping aspirin use around age 75 years. | uspstf-2022 | p4 | p4/narrative/aspirin-stop-age | narrative |

## Conflicts

**CONFLICT: aspirin-initiation-age-and-risk** — `age 40 to 59 years and 10-year CVD risk >=10%: individual decision` and `age >=60 years: do not initiate` are the source's age-stratified action branches.

## Coverage

Every exact recommendation record is cited above.
