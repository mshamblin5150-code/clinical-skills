# Hepatitis B screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from both source documents below. **Not a substitute
for either guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2019 | USPSTF | USPSTF/hepatitis-b-pregnant-women-final-rec-statement | recommendation-statement | 2019 | 2019 | https://doi.org/10.1001/jama.2019.9365 | stated | exact |
| uspstf-2020 | USPSTF | USPSTF/hepatitis-b-screening-adults-adolescents-final-rec-statement | recommendation-statement | 2020 | 2020 | https://doi.org/10.1001/jama.2020.22980 | stated | exact |

## Scope

**Read:** both complete recommendation statements. The pregnancy source includes the
recommendation, practice considerations, screening test and interval, implementation,
supporting evidence, response, research needs, and recommendations of others on pp.
1-5. The nonpregnant adolescent and adult source includes those classes of material
on pp. 1-7. Both reference lists are retired by class because they contain citations
rather than clinical prose.

**Not read:** nothing in either source page range.

**Source: `uspstf-2019`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement | 1 | yes |
| grades and methods | 2 | read 2026-08-30; blind 2026-08-30 |
| practice considerations and implementation | 3-4 | yes |
| supporting evidence | 4-5 | read 2026-08-30; blind 2026-08-30 |
| response, research needs, recommendations of others, and article information | 5 | read 2026-08-30; blind 2026-08-30 |
| references | 5-6 | exempt: citation list has no clinical prose |

**Source: `uspstf-2020`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations, screening, treatment, and implementation | 2-3 | yes |
| supporting evidence | 4-6 | read 2026-08-30; blind 2026-08-30 |
| response and research needs | 6 | read 2026-08-30; blind 2026-08-30 |
| recommendations of others and article information | 7 | read 2026-08-30; blind 2026-08-30 |
| references | 7-8 | exempt: citation list has no clinical prose |

**Second read:** a blind independent read dated 2026-08-30 corroborated that the
marked null spans contain no additional current USPSTF decision point.

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| pregnant-persons | all pregnant persons |
| pregnant-persons-unknown-or-continuing-risk | women with unknown HBsAg status or with new or continuing risk factors for HBV infection |
| hbsag-positive-pregnant-persons | HBV-positive mothers |
| infants-hbsag-positive-mother | infants born to mothers who test positive for HBsAg |
| infants-unknown-maternal-hbsag | infants born to mothers with unknown HBsAg status |
| infants-hbsag-negative-mother | infants born to HBV-negative mothers |
| increased-risk-adolescents-and-adults | asymptomatic, nonpregnant adolescents and adults at increased risk for HBV infection |
| persons-born-hbsag-prevalence-2-percent | adolescents and adults born in countries or regions with an HBsAg prevalence of 2% or greater |
| us-born-unvaccinated-parental-region-8-percent | US-born adolescents and adults not vaccinated as infants whose parents were born in regions with an HBsAg prevalence of 8% or greater |
| continued-risk-unvaccinated-adolescents-and-adults | patients with negative HBsAg results who have not received the HBV vaccine series and report continued risk |

## Quantities

| key | verbatim |
| --- | --- |
| hbv-screening | screening for HBV infection |
| hbv-screening-repeat | screening in each pregnancy |
| hbv-delivery-screening | screening at admission to a hospital or other delivery setting |
| positive-maternal-follow-up | case management during pregnancy |
| newborn-prophylaxis-timing | HBV vaccination and hepatitis B immune globulin prophylaxis |
| infant-serologic-testing-age | serologic testing for infection and immunity |
| increased-risk-prevalence | prevalence of positive HBsAg |
| hbv-screening-test | HBsAg screening and confirmation |
| continued-risk-periodic-screening | whether periodic screening may be useful for continued risk |
| continued-risk-screening-frequency | frequency of screening for continued risk |
| infant-vaccination-timing | timing of HBV vaccination after birth |
| infant-vaccine-series-completion | age by which to complete the HBV vaccination series |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hbv-screening | pregnant-persons | first prenatal visit | The USPSTF recommends screening for HBV infection in pregnant women at their first prenatal visit. | uspstf-2019 | p1 | p1/screening-for-hepatitis-b-virus-infection-in-pre/1 | A |
| hbv-screening-repeat | pregnant-persons | every pregnancy regardless of vaccination or previous negative result | Screening should be performed in each pregnancy, regardless of previous HBV vaccination or previous negative HBsAg test results. | uspstf-2019 | p3 | p3/narrative/screen-each-pregnancy | narrative |
| hbv-delivery-screening | pregnant-persons-unknown-or-continuing-risk | admission to hospital or other delivery setting | Women with unknown HBsAg status or with new or continuing risk factors for HBV infection (eg, injection drug use or a sexually transmitted infection) should be screened at the time of admission to a hospital or other delivery setting. | uspstf-2019 | p3 | p3/narrative/delivery-screening | narrative |
| positive-maternal-follow-up | hbsag-positive-pregnant-persons | HBV DNA viral load testing and specialty referral | For HBV-positive mothers, case management during pregnancy includes HBV DNA viral load testing and referral to specialty care for counseling and medical management of HBV infection. | uspstf-2019 | p3 | p3/narrative/positive-maternal-follow-up | narrative |
| infant-vaccination-timing | infants-hbsag-negative-mother | within 24 hours of birth | vaccinating infants born to HBV-negative mothers within 24 hours of birth | uspstf-2019 | p3 | p3/narrative/hbsag-negative-infant-vaccination | narrative |
| infant-vaccine-series-completion | infants-hbsag-negative-mother | by age 18 months | completing the HBV vaccination series in infants by age 18 months | uspstf-2019 | p3 | p3/narrative/infant-vaccine-series-completion | narrative |
| newborn-prophylaxis-timing | infants-hbsag-positive-mother | vaccine and HBIG within 12 hours of birth | HBV vaccination and hepatitis B immune globulin (HBIG) prophylaxis within 12 hours of birth | uspstf-2019 | p3 | p3/narrative/newborn-positive-maternal-prophylaxis | narrative |
| infant-serologic-testing-age | infants-hbsag-positive-mother | age 9 to 12 months | completing the vaccine series and serologic testing for infection and immunity at age 9 to 12 months | uspstf-2019 | p3 | p3/narrative/infant-serologic-testing-age | narrative |
| newborn-prophylaxis-timing | infants-unknown-maternal-hbsag | vaccine within 12 hours of birth, followed by HBIG | For infants born to mothers with unknown HBsAg status, current guidelines for case management include HBV vaccination within 12 hours of birth, followed by HBIG prophylaxis. | uspstf-2019 | p3 | p3/narrative/newborn-unknown-maternal-prophylaxis | narrative |
| hbv-screening | increased-risk-adolescents-and-adults | screen | The USPSTF recommends screening for HBV infection in adolescents and adults at increased risk for infection. | uspstf-2020 | p1 | p1/screening-for-hepatitis-b-virus-infection-in-ado/1 | B |
| increased-risk-prevalence | persons-born-hbsag-prevalence-2-percent | HBsAg prevalence >=2% | 2% or greater | uspstf-2020 | p2 | p2/narrative/birth-region-prevalence | narrative |
| increased-risk-prevalence | us-born-unvaccinated-parental-region-8-percent | parental-region HBsAg prevalence >=8% | 8% or greater | uspstf-2020 | p2 | p2/narrative/parental-region-prevalence | narrative |
| hbv-screening-test | increased-risk-adolescents-and-adults | confirm an initially reactive HBsAg result | confirmatory test for initially reactive results | uspstf-2020 | p2 | p2/narrative/hbsag-confirmation | narrative |
| continued-risk-periodic-screening | continued-risk-unvaccinated-adolescents-and-adults | periodic screening may be useful | periodic screening may be useful | uspstf-2020 | p3 | p3/narrative/continued-risk-periodic-screening | narrative |
| continued-risk-screening-frequency | continued-risk-unvaccinated-adolescents-and-adults | frequency by clinical judgment | Clinical judgment should be used | uspstf-2020 | p3 | p3/narrative/continued-risk-screening-frequency | narrative |

## Conflicts

## Coverage
