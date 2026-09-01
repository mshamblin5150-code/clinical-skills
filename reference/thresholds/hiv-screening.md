# HIV screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[`reference/thresholds/README.md`](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2019 | USPSTF | USPSTF/hiv-screening-final-rec-statement | recommendation-statement | 2019 | 2019 | https://doi.org/10.1001/jama.2019.6587 | stated | exact |

## Scope

**Read:** the complete recommendation statement, including the recommendation,
clinical considerations, screening tests and intervals, implementation, supporting
evidence, response, research needs, and recommendations of others on pp. 1-8. The
reference list on pp. 9-11 is retired by class because it contains citations rather
than clinical prose.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| complete recommendation-statement narrative | 1-8 | yes |
| references | 9-11 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adolescents-adults-15-65 | adolescents and adults aged 15 to 65 years |
| younger-adolescents-under-15-increased-risk | adolescents younger than 15 years at increased risk |
| older-adults-over-65-increased-risk | adults older than 65 years at increased risk |
| increased-risk-persons | persons known to be at increased risk of HIV infection |
| increased-risk-msm | high-risk men who have sex with men |
| new-partner-unknown-status-risk | persons having 1 or more new sex partners whose HIV status is unknown |
| prenatal-risk-or-high-incidence | women with risk factors for HIV acquisition and women living or receiving care in high-incidence settings |
| prenatal-all-negative-early | all women who test negative early in pregnancy |
| subsequent-pregnancy | women screened during a previous pregnancy |
| all-persons-cdc | all persons |
| all-adolescents-adults-cdc | all adolescents and adults aged 13 to 64 years |
| all-females-13-64-acog | all females aged 13 to 64 years |
| at-risk-females-13-64-acog | females aged 13 to 64 years assessed to have risk factors for HIV infection |
| adolescents-15-18-aap | adolescents between the ages of 15 and 18 years |
| increased-risk-persons-aap | persons at increased risk |
| aafp-routine | adults aged 18 years and older |
| adolescents-under-18-increased-risk-aafp | adolescents at increased risk tested at younger ages than 18 years |
| vaginal-intercourse-unknown-status-risk | persons having vaginal intercourse without a condom and with more than 1 partner whose HIV status is unknown |
| high-risk-hiv-acquisition-without-hiv | persons who do not have HIV and are at high risk of acquiring HIV infection |

## Quantities

| key | verbatim |
| --- | --- |
| routine-hiv-screening | screening for HIV infection |
| outside-age-increased-risk-screening | testing patients outside the routine screening age range who are at increased risk |
| new-partner-repeat-screening | repeat screening for persons having 1 or more new sex partners whose HIV status is unknown |
| cdc-risk-screening-frequency | screening frequency for persons at increased risk |
| cdc-msm-screening-frequency | screening frequency for high-risk men who have sex with men |
| prenatal-repeat-screening | repeat prenatal screening |
| subsequent-pregnancy-rescreening | screening in subsequent pregnancies |
| increased-risk-factor | factor placing a person at increased risk of HIV infection |
| preexposure-prophylaxis | preexposure prophylaxis for persons at high risk of HIV acquisition |
| cdc-routine-screening-age | CDC routine screening age range and prevalence exception |
| cdc-lifetime-screening-frequency | CDC lifetime screening frequency for all persons |
| acog-lifetime-screening-frequency | ACOG screening at least once in a lifetime |
| acog-risk-screening-frequency | ACOG annual screening for females assessed to have risk factors |
| aap-universal-screening | American Academy of Pediatrics universal screening once between the ages of 15 and 18 years |
| aap-risk-screening-frequency | American Academy of Pediatrics annual reassessment and testing of persons at increased risk |
| aafp-routine-screening | American Academy of Family Physicians routine screening age |
| aafp-younger-adolescent-risk-screening | American Academy of Family Physicians testing of adolescents at increased risk at younger ages |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| routine-hiv-screening | adolescents-adults-15-65 | age 15 to 65 years: screen | The USPSTF recommends screening for HIV infection in adolescents and adults aged 15 to 65 years. | uspstf-2019 | p1 | p1/screening-for-hiv-infection/1 | A |
| outside-age-increased-risk-screening | younger-adolescents-under-15-increased-risk | age <15 years and increased risk: screen | The USPSTF recommends screening for HIV infection in adolescents and adults aged 15 to 65 years. Younger adolescents and older adults who are at increased risk of infection should also be screened. | uspstf-2019 | p1 | p1/screening-for-hiv-infection/1 | A |
| outside-age-increased-risk-screening | older-adults-over-65-increased-risk | age >65 years and increased risk: screen | The USPSTF recommends screening for HIV infection in adolescents and adults aged 15 to 65 years. Younger adolescents and older adults who are at increased risk of infection should also be screened. | uspstf-2019 | p1 | p1/screening-for-hiv-infection/1 | A |
| new-partner-repeat-screening | new-partner-unknown-status-risk | >=1 new sex partner whose HIV status is unknown: repeat screening is reasonable | Repeat screening is reasonable for persons known to be at increased risk of HIV infection, such as sexually active men who have sex with men; persons with a sex partner who is living with HIV; or persons who engage in behaviors that may convey an increased risk of HIV infection, such as injection drug use, transactional sex or commercial sex work, having 1 or more new sex partners whose HIV status is unknown, or having other factors that can place a person at increased risk of HIV infection | uspstf-2019 | p4 | p4/narrative/new-partner-repeat-screening | narrative |
| increased-risk-factor | vaginal-intercourse-unknown-status-risk | >1 partner whose HIV status is unknown plus vaginal intercourse without a condom: increased risk | RENDERED: having vaginal intercourse without a condom and with more than 1 partner whose HIV status is unknown | uspstf-2019 | p4 | p4/narrative/vaginal-intercourse-unknown-status-risk | narrative |
| cdc-risk-screening-frequency | increased-risk-persons | annually | RENDERED: The CDC recommends annual screening in persons at increased risk | uspstf-2019 | p5 | p5/narrative/cdc-annual-screening | narrative |
| cdc-msm-screening-frequency | increased-risk-msm | every 3 or 6 months depending on risk factors, local prevalence, and local policies | RENDERED: every 3 or 6 months) depending on the patient's risk factors, local HIV prevalence, and local policies. | uspstf-2019 | p5 | p5/narrative/cdc-msm-screening-frequency | narrative |
| prenatal-repeat-screening | prenatal-risk-or-high-incidence | third trimester | recommend repeat prenatal screening for HIV during the third trimester of pregnancy | uspstf-2019 | p5 | p5/narrative/prenatal-third-trimester-risk | narrative |
| prenatal-repeat-screening | prenatal-all-negative-early | third trimester may be considered | repeat screening for HIV during the third trimester in all women who test negative early in pregnancy may be considered | uspstf-2019 | p5 | p5/narrative/prenatal-third-trimester-all | narrative |
| subsequent-pregnancy-rescreening | subsequent-pregnancy | every subsequent pregnancy: rescreen | Women screened during a previous pregnancy should be rescreened in subsequent pregnancies. | uspstf-2019 | p5 | p5/narrative/subsequent-pregnancy-rescreening | narrative |
| preexposure-prophylaxis | high-risk-hiv-acquisition-without-hiv | antiretroviral medication every day before potential exposure; offer to persons at high risk | RENDERED: Preexposure prophylaxis is used in persons who do not have HIV and are at high risk of acquiring HIV infection. It consists of antiretroviral medication taken every day, before potential exposure. The USPSTF recommends offering preexposure prophylaxis to persons at high risk of HIV acquisition. | uspstf-2019 | p5 | p5/narrative/daily-preexposure-prophylaxis | narrative |
| cdc-routine-screening-age | all-adolescents-adults-cdc | age 13 to 64 years unless community prevalence <0.1% | all adolescents and adults aged 13 to 64 years, regardless of other recognized risk factors, unless HIV prevalence was documented to be less than 0.1% | uspstf-2019 | p8 | p8/narrative/cdc-routine-screening-age | narrative |
| cdc-lifetime-screening-frequency | all-persons-cdc | at least once in lifetime | RENDERED: The CDC recommends that all persons should be screened at least once in their lifetime and those with risk factors be screened more frequently (eg, annually); | uspstf-2019 | p8 | p8/narrative/cdc-lifetime-risk-frequency | narrative |
| cdc-risk-screening-frequency | increased-risk-persons | more frequently, such as annually | RENDERED: The CDC recommends that all persons should be screened at least once in their lifetime and those with risk factors be screened more frequently (eg, annually); | uspstf-2019 | p8 | p8/narrative/cdc-risk-frequency-other-organizations | narrative |
| cdc-msm-screening-frequency | increased-risk-msm | every 3 to 6 months based on risk behaviors, community prevalence, and other considerations | RENDERED: every 3 to 6 months) based on risk behaviors, community HIV prevalence, and other considerations. | uspstf-2019 | p8 | p8/narrative/cdc-msm-other-organizations | narrative |
| acog-lifetime-screening-frequency | all-females-13-64-acog | age 13 to 64 years: at least once in lifetime | RENDERED: In 2017, ACOG reaffirmed a previous recommendation that all females aged 13 to 64 years be tested at least once in their lifetime and annually thereafter if they are assessed to have risk factors for HIV infection. | uspstf-2019 | p8 | p8/narrative/acog-lifetime-screening-frequency | narrative |
| acog-risk-screening-frequency | at-risk-females-13-64-acog | annually thereafter | RENDERED: In 2017, ACOG reaffirmed a previous recommendation that all females aged 13 to 64 years be tested at least once in their lifetime and annually thereafter if they are assessed to have risk factors for HIV infection. | uspstf-2019 | p8 | p8/narrative/acog-risk-screening-frequency | narrative |
| aap-universal-screening | adolescents-15-18-aap | once between ages 15 and 18 years | universal screening for HIV infection once between the ages of 15 and 18 years, and annual reassessment and testing of persons at increased risk | uspstf-2019 | p8 | p8/narrative/aap-universal-screening | narrative |
| aap-risk-screening-frequency | increased-risk-persons-aap | annual reassessment and testing | universal screening for HIV infection once between the ages of 15 and 18 years, and annual reassessment and testing of persons at increased risk | uspstf-2019 | p8 | p8/narrative/aap-risk-screening-frequency | narrative |
| aafp-routine-screening | aafp-routine | routine screening begins at age 18 | RENDERED: The American Academy of Family Physicians supports the 2013 USPSTF recommendations, except it recommends that routine screening begin at age 18 years and that only adolescents at increased risk be tested at younger ages. | uspstf-2019 | p8 | p8/narrative/aafp-routine-screening | narrative |
| aafp-younger-adolescent-risk-screening | adolescents-under-18-increased-risk-aafp | age <18 years and increased risk: test | RENDERED: The American Academy of Family Physicians supports the 2013 USPSTF recommendations, except it recommends that routine screening begin at age 18 years and that only adolescents at increased risk be tested at younger ages. | uspstf-2019 | p8 | p8/narrative/aafp-younger-adolescent-risk-screening | narrative |

## Conflicts

CONFLICT: cdc-msm-screening-frequency — "every 3 or 6 months depending on risk factors, local prevalence, and local policies" is the p5 wording; "every 3 to 6 months based on risk behaviors, community prevalence, and other considerations" is the p8 summary of the CDC position.

CONFLICT: cdc-risk-screening-frequency — "annually" is the p5 interval for persons at increased risk; "more frequently, such as annually" is the p8 summary of the CDC position for the same population.

## Coverage

- `p1/screening-for-hiv-infection/2` - The recommendation states whom to screen but no number that changes what is done to a patient.
