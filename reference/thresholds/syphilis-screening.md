# Syphilis screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from both source documents below. **Not a substitute
for either guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2022 | USPSTF | USPSTF/syphilis-nonpregnant-adults-screening-final-recommendation | recommendation-statement | 2022 | 2022 | https://doi.org/10.1001/jama.2022.15322 | stated | exact |
| uspstf-2025 | USPSTF | USPSTF/syphilis-pregnancy-screening-final-rec-statement | recommendation-statement | 2025 | 2025 | https://doi.org/10.1001/jama.2025.5009 | stated | exact |

## Scope

**Read:** both complete recommendation statements. The nonpregnant source includes
the recommendation, risk assessment, screening tests and intervals, treatment,
implementation, supporting evidence, response, research needs, and recommendations
of others on pp. 1-5. The pregnancy source includes the recommendation, screening
tests and timing, treatment, supporting evidence, response, research needs, and
recommendations of others on pp. 1-5. Both reference lists are retired by class
because they contain citations rather than clinical prose.

**Not read:** nothing in either source page range.

**Source: `uspstf-2022`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations and screening tests | 2-3 | yes |
| screening intervals, treatment, and implementation | 4 | yes |
| supporting evidence | 4-5 | read 2026-08-30; blind 2026-08-30 |
| response, research needs, recommendations of others, and article information | 5 | read 2026-08-30; blind 2026-08-30 |
| references | 6-7 | exempt: citation list has no clinical prose |

**Source: `uspstf-2025`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations and screening | 2-3 | yes |
| treatment and recommendations of others | 4 | yes |
| supporting evidence | 4-5 | read 2026-08-30; blind 2026-08-30 |
| response and repeat-screening decision | 5 | yes |
| research needs, recommendations of others, and article information | 5 | read 2026-08-30; blind 2026-08-30 |
| references | 6-7 | exempt: citation list has no clinical prose |

**Second read:** completed 2026-08-30. A separate reader blind-corroborated the
marked spans as containing no additional current USPSTF decision point.

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| increased-risk-nonpregnant-adolescents-and-adults | asymptomatic, nonpregnant adolescents and adults who are at increased risk for syphilis infection |
| continued-high-risk-msm-or-hiv | men who have sex with men or persons with HIV infection who continue to be at high risk |
| pregnant-persons | all adolescents and adults who are pregnant, whether or not risk factors for syphilis are present |
| pregnant-persons-second-half-diagnosis | pregnant women diagnosed with syphilis during the second half of pregnancy |
| pregnant-persons-penicillin-allergy | pregnant women with a penicillin allergy |
| pregnant-persons-with-syphilis | pregnant women with syphilis |
| pregnant-persons-other-organization-rescreening | pregnant women subject to repeat-screening recommendations from the CDC, WPSI, AAP, or ACOG |

## Quantities

| key | verbatim |
| --- | --- |
| syphilis-screening | screening for syphilis infection |
| increased-risk-assessment | factors associated with increased risk of syphilis infection |
| syphilis-screening-interval | screening frequency for persons at increased risk |
| syphilis-screening-tests-traditional | traditional screening and confirmatory test sequence |
| syphilis-screening-tests-reverse | reverse-sequence screening and confirmatory test sequence |
| pregnancy-screening-test-pair | tests included in pregnancy screening |
| repeat-pregnancy-screening | USPSTF recommendation position on repeat screening during pregnancy |
| other-organization-repeat-pregnancy-screening-third-trimester | third-trimester repeat-screening schedule attributed to other organizations |
| other-organization-repeat-pregnancy-screening-delivery | delivery repeat-screening schedule attributed to other organizations |
| pregnancy-syphilis-treatment | treatment for syphilis during pregnancy |
| second-half-pregnancy-management | management after diagnosis during the second half of pregnancy |
| penicillin-allergy-management | management of penicillin allergy during pregnancy |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| syphilis-screening | increased-risk-nonpregnant-adolescents-and-adults | screen | The USPSTF recommends screening for syphilis infection in persons who are at increased risk for infection. | uspstf-2022 | p1 | p1/screening-for-syphilis-infection-in-nonpregnant/1 | A |
| increased-risk-assessment | increased-risk-nonpregnant-adolescents-and-adults | consider community prevalence | clinicians should consider the prevalence of infection in the communities they serve | uspstf-2022 | p2 | p2/narrative/increased-risk-assessment | narrative |
| syphilis-screening-tests-traditional | increased-risk-nonpregnant-adolescents-and-adults | initial nontreponemal test followed by a confirmatory treponemal antibody detection test | initial nontreponemal test | uspstf-2022 | p3 | p3/narrative/traditional-screening-algorithm | narrative |
| syphilis-screening-tests-reverse | increased-risk-nonpregnant-adolescents-and-adults | initial automated treponemal test followed by a nontreponemal test for reactive samples | initial automated treponemal test | uspstf-2022 | p3 | p3/narrative/reverse-sequence-algorithm | narrative |
| syphilis-screening-interval | continued-high-risk-msm-or-hiv | at least annually; every 3 to 6 months if high risk continues | Men who have sex with men or persons with HIV infection may benefit from screening at least annually or more frequently (eg, every 3 to 6 months) if they continue to be at high risk. | uspstf-2022 | p4 | p4/narrative/screening-interval | narrative |
| syphilis-screening | pregnant-persons | early universal screening; first available opportunity if not screened early | The USPSTF recommends early, universal screening for syphilis infection during pregnancy; if an individual is not screened early in pregnancy, the USPSTF recommends screening at the first available opportunity. | uspstf-2025 | p1 | p1/screening-for-syphilis-infection-during-pregnanc/1 | A |
| pregnancy-screening-test-pair | pregnant-persons | treponemal and nontreponemal test | Screening should include both a treponemal and nontreponemal test. | uspstf-2025 | p3 | p3/narrative/pregnancy-screening-test-pair | narrative |
| other-organization-repeat-pregnancy-screening-third-trimester | pregnant-persons-other-organization-rescreening | approximately 28 weeks | 28 weeks of gestation | uspstf-2025 | p4 | p4/narrative/other-organization-repeat-screening-third-trimester | narrative |
| other-organization-repeat-pregnancy-screening-delivery | pregnant-persons-other-organization-rescreening | again at delivery | again at delivery | uspstf-2025 | p4 | p4/narrative/other-organization-repeat-screening-delivery | narrative |
| pregnancy-syphilis-treatment | pregnant-persons-with-syphilis | CDC recommends parenteral penicillin G as the only treatment with documented efficacy | The CDC recommends parenteral penicillin G as the only treatment with documented efficacy during pregnancy. | uspstf-2025 | p4 | p4/narrative/pregnancy-syphilis-treatment | narrative |
| second-half-pregnancy-management | pregnant-persons-second-half-diagnosis | sonographic fetal evaluation for signs of congenital syphilis | sonographic fetal evaluation | uspstf-2025 | p4 | p4/narrative/second-half-pregnancy-management | narrative |
| penicillin-allergy-management | pregnant-persons-penicillin-allergy | desensitize and treat with penicillin | Pregnant women with a penicillin allergy should be desensitized and then treated with penicillin. | uspstf-2025 | p4 | p4/narrative/penicillin-allergy-management | narrative |
| repeat-pregnancy-screening | pregnant-persons | no recommendation for or against repeat screening | is not making a recommen- dation for or against repeat screening. | uspstf-2025 | p5 | p5/narrative/repeat-screening-decision | narrative |

## Conflicts

## Coverage
