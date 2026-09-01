# Breast cancer screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2024 | USPSTF | USPSTF/breast-cancer-screening-final-rec | recommendation-statement | 2024 | 2024 | https://doi.org/10.1001/jama.2024.5534 | stated | exact |

## Scope

**Read:** the complete source, page by page, including the recommendations, practice considerations, evidence, recommendations of others, article information, and references; the pure reference list is retired by class.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| recommendations, practice considerations, evidence, and recommendations of others | 1-10 | yes |
| article information | 11 | read 2026-08-30; blind 2026-08-30 |
| references | 11-13 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| uspstf-average-risk-population | cisgender women and all other persons assigned female at birth aged 40 years or older at average risk of breast cancer |
| average-risk-women | women with an average risk of breast cancer |
| all-individuals | all individuals |

## Quantities

| key | verbatim |
| --- | --- |
| mammography-start-age | age to start screening mammography |
| mammography-interval | screening interval |
| mammography-stop-age | age to stop screening mammography |
| breast-cancer-risk-assessment-age | breast cancer risk assessment by age 25 years |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mammography-start-age | uspstf-average-risk-population | age 40 to 74 years: screen | The USPSTF recommends biennial screening mammography for women aged 40 to 74 years. | uspstf-2024 | p1 | p1/screening-for-breast-cancer/1 | B |
| mammography-interval | uspstf-average-risk-population | biennial screening from age 40 to 74 years | The USPSTF recommends biennial screening mammography for women aged 40 to 74 years. | uspstf-2024 | p1 | p1/screening-for-breast-cancer/1 | B |
| mammography-stop-age | uspstf-average-risk-population | age >=75 years: evidence insufficient | women 75 years or older | uspstf-2024 | p1 | p1/screening-for-breast-cancer/2 | I |
| mammography-start-age | average-risk-women | ACS: start at age 45 years | RENDERED: starting at age 45 years | uspstf-2024 | p10 | p10/narrative/acs-start-age | narrative |
| mammography-start-age | average-risk-women | ACS: ages 40 to 44 years may begin annual screening | RENDERED: between the ages of 40 and 44 years | uspstf-2024 | p10 | p10/narrative/acs-optional-start-age | narrative |
| mammography-start-age | average-risk-women | ACOG: offer at age 40 years | RENDERED: offered screening mammography starting at age 40 years | uspstf-2024 | p10 | p10/narrative/acog-offer-age | narrative |
| mammography-start-age | average-risk-women | ACOG: begin no later than age 50 years | RENDERED: begin screening mammography no later than age 50 years | uspstf-2024 | p10 | p10/narrative/acog-latest-start-age | narrative |
| mammography-start-age | average-risk-women | ACR and SBI: begin annual screening at age 40 years | RENDERED: annual screening mammography beginning at age 40 years | uspstf-2024 | p10 | p10/narrative/acr-start-age | narrative |
| mammography-interval | average-risk-women | ACS: screen annually at ages 45 to 54 years | RENDERED: women aged 45 to 54 years should be screened annually | uspstf-2024 | p10 | p10/narrative/acs-annual-interval | narrative |
| mammography-interval | average-risk-women | ACS: at age >=55 years, screen biennially or annually | RENDERED: women 55 years or older should transition to biennial screening or have the opportunity to continue screening annually | uspstf-2024 | p10 | p10/narrative/acs-older-interval | narrative |
| mammography-interval | average-risk-women | ACOG: screen every 1 or 2 years | RENDERED: screening mammography every 1 or 2 years | uspstf-2024 | p10 | p10/narrative/acog-screening-interval | narrative |
| mammography-interval | average-risk-women | ACR and SBI: screen annually from age 40 years | RENDERED: annual screening mammography beginning at age 40 years | uspstf-2024 | p10 | p10/narrative/acr-screening-interval | narrative |
| mammography-stop-age | average-risk-women | ACS: continue while health is good and life expectancy >=10 years | RENDERED: continue screening mammography as long as their overall health is good and they have a life expectancy of 10 years or longer | uspstf-2024 | p10 | p10/narrative/acs-stop-age | narrative |
| mammography-stop-age | average-risk-women | ACOG: continue until at least age 75 years | RENDERED: continue screening mammography until at least age 75 years | uspstf-2024 | p10 | p10/narrative/acog-minimum-stop-age | narrative |
| mammography-stop-age | average-risk-women | ACOG: after age 75 years use shared decision-making | RENDERED: Beyond age 75 years, the decision to discontinue screening mammography should be based on shared decision-making | uspstf-2024 | p10 | p10/narrative/acog-later-stop-age | narrative |
| mammography-stop-age | average-risk-women | ACR and SBI: continue past age 74 years without an upper limit unless severe comorbidity limits life expectancy | RENDERED: screening should continue past age 74 years, without an upper age limit, unless severe comorbidities limit life expectancy | uspstf-2024 | p10 | p10/narrative/acr-stop-age | narrative |
| breast-cancer-risk-assessment-age | all-individuals | assess risk by age 25 years | RENDERED: recommends breast cancer risk assessment by age 25 years for all individuals | uspstf-2024 | p10 | p10/narrative/acr-risk-assessment-age | narrative |

## Conflicts

**CONFLICT: mammography-start-age** — For average-risk women, the complete values are `ACS: start at age 45 years`, `ACS: ages 40 to 44 years may begin annual screening`, `ACOG: offer at age 40 years`, `ACOG: begin no later than age 50 years`, and `ACR and SBI: begin annual screening at age 40 years`. The values differ because the source is summarizing separate organizations' recommendations.

**CONFLICT: mammography-interval** — For average-risk women, the complete values are `ACS: screen annually at ages 45 to 54 years`, `ACS: at age >=55 years, screen biennially or annually`, `ACOG: screen every 1 or 2 years`, and `ACR and SBI: screen annually from age 40 years`. The values differ because the organizations specify different intervals and age branches.

**CONFLICT: mammography-stop-age** — For average-risk women, the complete values are `ACS: continue while health is good and life expectancy >=10 years`, `ACOG: continue until at least age 75 years`, `ACOG: after age 75 years use shared decision-making`, and `ACR and SBI: continue past age 74 years without an upper limit unless severe comorbidity limits life expectancy`. The values differ because the organizations use different stopping rules.

## Coverage

- `p1/screening-for-breast-cancer/3` - the supplemental-imaging I statement contains no numeric decision point.
