# Adult Immunization Schedule — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete consumer schedule below. **Not a substitute for the schedule** and not a clinical instruction. The source states that the posted July 2, 2025 schedule was amended on April 27, 2026 and is the current CDC adult schedule under the court order described on page 1.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| acip-adult-2025 | ACIP | ACIP/Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC | web-capture | July 2, 2025 schedule amended April 27, 2026 | 2025-07-02 | https://www.cdc.gov/vaccines/imz-schedules/adult-easyread.html | stated |  |

## Scope

**Read:** the complete 7-page web capture, page by page, including the court-order notice and amendment statement, schedule purpose and applicability, the full age-based schedule and key, the complete vaccine-preventable-disease and dose table, footnotes, page controls, related resources, and site footer. The age-based schedule and dose tables on pages 2 through 5 were also read from rendered pages because their color bands and table geometry carry meaning that is not preserved completely in extracted text.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| court-order notice, amendment statement, purpose, and schedule applicability | 1 | yes |
| age-based adult vaccination schedule and key | 2-3 | yes |
| vaccine-preventable-disease dose table and footnotes | 3-5 | yes |
| page controls, related resources, and site footer | 6-7 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults-19-plus | adults aged 19 years and older |
| high-risk-adults-50-59 | high risk adults 50 - 59 |
| adults-65-plus | aged 65 years or older |
| adults-50-74 | aged 50 through 74 years |
| adults-75-plus | aged 75 years or older |
| all-adults | all adults |
| adults-68-or-younger | aged 68 years or younger |
| us-born-adults-45-or-younger | U.S. born and aged 45 years or younger |
| adults-27-45 | Aged 27-45 years |
| not-already-vaccinated | not already vaccinated |
| dirty-wound-patients | dirty wounds |
| pregnant-adults | pregnant |

## Quantities

| key | verbatim |
| --- | --- |
| schedule-applicability-age | Adults Aged 19 Years and Older |
| rsv-amendment-age-band | RSV recommendation for vaccination of high risk adults 50 - 59 |
| covid-age-schedule | COVID-19 |
| influenza-schedule-interval | Influenza/Flu |
| rsv-age-schedule | RSV |
| tdap-pregnancy-interval | Tdap every pregnancy |
| td-tdap-booster-interval | Td/Tdap every 10 years |
| mmr-age-schedule | MMR |
| chickenpox-age-schedule | Chickenpox |
| shingles-age-schedule | Shingles |
| hpv-age-schedule | HPV |
| pneumococcal-age-schedule | Pneumococcal |
| hepatitis-a-age-schedule | Hepatitis A |
| hepatitis-b-age-schedule | Hepatitis B |
| meningococcal-age-schedule | Meningococcal |
| hib-age-schedule | Hib |
| mpox-age-schedule | Mpox |
| covid-dose-count | Number of Vaccine Doses: COVID-19 |
| influenza-dose-count-and-interval | Number of Vaccine Doses: Influenza (Flu) |
| rsv-dose-count | Number of Vaccine Doses: RSV |
| tetanus-primary-dose-count | Number of Vaccine Doses: Tetanus |
| tetanus-booster-dose-and-interval | Tetanus: 1 booster every 10 years |
| tetanus-dirty-wound-dose | Tetanus: 1 dose for dirty wounds |
| diphtheria-primary-dose-count | Number of Vaccine Doses: Diphtheria |
| diphtheria-booster-dose-and-interval | Diphtheria: 1 booster every 10 years |
| pertussis-primary-dose-count | Number of Vaccine Doses: Pertussis |
| pertussis-pregnancy-dose | Pertussis: 1 dose every pregnancy |
| measles-dose-count | Number of Vaccine Doses: Measles |
| mumps-dose-count | Number of Vaccine Doses: Mumps |
| rubella-dose-count | Number of Vaccine Doses: Rubella |
| varicella-dose-count | Number of Vaccine Doses: Chickenpox |
| zoster-dose-count | Number of Vaccine Doses: Shingles |
| hpv-dose-count | Number of Vaccine Doses: HPV |
| pneumococcal-dose-count | Number of Vaccine Doses: Pneumococcal |
| hepatitis-a-dose-count | Number of Vaccine Doses: Hepatitis A |
| hepatitis-b-dose-count | Number of Vaccine Doses: Hepatitis B |
| meningococcal-dose-count | Number of Vaccine Doses: Meningococcal |
| hib-dose-count | Number of Vaccine Doses: Hib |
| mpox-dose-count | Number of Vaccine Doses: Mpox |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| schedule-applicability-age | adults-19-plus | age >=19 years | Recommended Immunizations for Adults Aged 19 Years and Older, United States, 2025 | acip-adult-2025 | p1 | p1/narrative/schedule-applicability-age | narrative |
| rsv-amendment-age-band | high-risk-adults-50-59 | age 50 to 59 years | vaccination of high risk adults 50 - 59 | acip-adult-2025 | p1 | p1/narrative/rsv-amendment-age-band | narrative |
| covid-age-schedule | adults-19-plus | age 19 to 64 years: at least 1 current dose | RENDERED: COVID-19, ages 19-26 years, 27-49 years, and 50-64 years: At least 1 dose of the current COVID-19 vaccine | acip-adult-2025 | p2 | p2/narrative/covid-age-19-64 | narrative |
| covid-age-schedule | adults-65-plus | age >=65 years: at least 2 current doses | RENDERED: COVID-19, 65 years or older: At least 2 doses | acip-adult-2025 | p2 | p2/narrative/covid-age-65-plus | narrative |
| influenza-schedule-interval | all-adults | every year | RENDERED: Influenza/Flu, all adult age groups: Every Year | acip-adult-2025 | p2 | p2/narrative/influenza-every-year | narrative |
| rsv-age-schedule | pregnant-adults | pregnant adults age 19 to 49 years during RSV season: some adults should receive vaccine | RENDERED: RSV, ages 19-26 years and 27-49 years, if pregnant during RSV season: SOME adults in age group should get the vaccine | acip-adult-2025 | p2 | p2/narrative/rsv-pregnancy-age-19-49 | narrative |
| rsv-age-schedule | adults-50-74 | age 50 to 74 years: some adults should receive vaccine | RENDERED: RSV, ages 50 through 74 years: SOME adults in age group should get the vaccine | acip-adult-2025 | p2 | p2/narrative/rsv-age-50-74 | narrative |
| rsv-age-schedule | adults-75-plus | age >=75 years: all adults should receive vaccine | RENDERED: RSV, if aged 75 years or older: ALL adults in age group should get the vaccine | acip-adult-2025 | p2 | p2/narrative/rsv-age-75-plus | narrative |
| tdap-pregnancy-interval | pregnant-adults | every pregnancy | Tdap every pregnancy. Td/Tdap every 10 years for all adults. | acip-adult-2025 | p2 | p2/narrative/tdap-every-pregnancy | narrative |
| td-tdap-booster-interval | all-adults | every 10 years | Tdap every pregnancy. Td/Tdap every 10 years for all adults. | acip-adult-2025 | p2 | p2/narrative/td-tdap-every-10-years | narrative |
| mmr-age-schedule | adults-68-or-younger | age <=68 years: some adults should receive vaccine | RENDERED: MMR, if aged 68 years or younger: SOME adults in age group should get the vaccine | acip-adult-2025 | p2 | p2/narrative/mmr-age-68-or-younger | narrative |
| chickenpox-age-schedule | us-born-adults-45-or-younger | U.S. born and age <=45 years: some adults should receive vaccine | RENDERED: Chickenpox, if U.S. born and aged 45 years or younger: SOME adults in age group should get the vaccine | acip-adult-2025 | p2 | p2/narrative/chickenpox-age-45-or-younger | narrative |
| shingles-age-schedule | adults-19-plus | age 19 to 49 years: some adults; age >=50 years: all adults | RENDERED: Shingles, ages 19-26 years and 27-49 years: SOME adults; ages 50-64 years and 65 years or older: ALL adults | acip-adult-2025 | p2 | p2/narrative/shingles-age-schedule | narrative |
| hpv-age-schedule | adults-19-plus | age 19 to 26 years: all adults; age 27 to 45 years: discuss with health care provider | RENDERED: HPV, ages 19-26 years: ALL adults; aged 27-45 years: adults should talk to their health care provider to decide if this vaccine is right for them | acip-adult-2025 | p2 | p2/narrative/hpv-age-schedule | narrative |
| pneumococcal-age-schedule | adults-19-plus | age 19 to 49 years: some adults; age >=50 years: all adults | RENDERED: Pneumococcal, ages 19-26 years and 27-49 years: SOME adults; ages 50-64 years and 65 years or older: ALL adults | acip-adult-2025 | p2 | p2/narrative/pneumococcal-age-schedule | narrative |
| hepatitis-a-age-schedule | adults-19-plus | age >=19 years: some adults should receive vaccine | RENDERED: Hepatitis A, ages 19-26 years, 27-49 years, 50-64 years, and 65 years or older: SOME adults in age group should get the vaccine | acip-adult-2025 | p2 | p2/narrative/hepatitis-a-age-schedule | narrative |
| hepatitis-b-age-schedule | adults-19-plus | age <=59 years: all adults; age >=60 years: some adults | RENDERED: Hepatitis B: ALL adults through 59 years; SOME adults aged 60 years or older | acip-adult-2025 | p3 | p3/narrative/hepatitis-b-age-schedule | narrative |
| meningococcal-age-schedule | adults-19-plus | age >=19 years: some adults should receive vaccine | RENDERED: Meningococcal, all adult age groups from age 19 years: SOME adults in age group should get the vaccine | acip-adult-2025 | p3 | p3/narrative/meningococcal-age-schedule | narrative |
| hib-age-schedule | adults-19-plus | age >=19 years: some adults should receive vaccine | RENDERED: Hib, all adult age groups from age 19 years: SOME adults in age group should get the vaccine | acip-adult-2025 | p3 | p3/narrative/hib-age-schedule | narrative |
| mpox-age-schedule | adults-19-plus | age >=19 years: some adults should receive vaccine | RENDERED: Mpox, all adult age groups from age 19 years: SOME adults in age group should get the vaccine | acip-adult-2025 | p3 | p3/narrative/mpox-age-schedule | narrative |
| covid-dose-count | adults-19-plus | >=1 current dose depending on age or health status | 1 or more doses of the current COVID-19 vaccine depending on age or health status | acip-adult-2025 | p3 | p3/narrative/covid-dose-count | narrative |
| influenza-dose-count-and-interval | adults-19-plus | 1 dose each year | 1 dose each year | acip-adult-2025 | p3 | p3/narrative/influenza-dose-count | narrative |
| rsv-dose-count | adults-19-plus | 1 dose | 1 dose | acip-adult-2025 | p3 | p3/narrative/rsv-dose-count | narrative |
| tetanus-primary-dose-count | not-already-vaccinated | 3 doses | 3 doses if not already vaccinated | acip-adult-2025 | p3 | p3/narrative/tetanus-primary-dose-count | narrative |
| tetanus-booster-dose-and-interval | adults-19-plus | 1 booster every 10 years | 1 booster every 10 years | acip-adult-2025 | p3 | p3/narrative/tetanus-booster | narrative |
| tetanus-dirty-wound-dose | dirty-wound-patients | 1 dose | 1 dose for dirty wounds | acip-adult-2025 | p3 | p3/narrative/tetanus-dirty-wound-dose | narrative |
| diphtheria-primary-dose-count | not-already-vaccinated | 3 doses | 3 doses if not already vaccinated | acip-adult-2025 | p4 | p4/narrative/diphtheria-primary-dose-count | narrative |
| diphtheria-booster-dose-and-interval | adults-19-plus | 1 booster every 10 years | 1 booster every 10 years | acip-adult-2025 | p4 | p4/narrative/diphtheria-booster | narrative |
| pertussis-primary-dose-count | not-already-vaccinated | 3 doses | 3 doses if not already vaccinated | acip-adult-2025 | p4 | p4/narrative/pertussis-primary-dose-count | narrative |
| pertussis-pregnancy-dose | pregnant-adults | 1 dose every pregnancy | 1 dose every pregnancy | acip-adult-2025 | p4 | p4/narrative/pertussis-pregnancy-dose | narrative |
| measles-dose-count | adults-19-plus | 1 or 2 doses | RENDERED: Measles (Rubeola): 1 or 2 doses | acip-adult-2025 | p4 | p4/narrative/measles-dose-count | narrative |
| mumps-dose-count | adults-19-plus | 1 or 2 doses | RENDERED: Mumps: 1 or 2 doses | acip-adult-2025 | p4 | p4/narrative/mumps-dose-count | narrative |
| rubella-dose-count | adults-19-plus | 1 or 2 doses | RENDERED: Rubella (German Measles): 1 or 2 doses | acip-adult-2025 | p4 | p4/narrative/rubella-dose-count | narrative |
| varicella-dose-count | adults-19-plus | 2 doses | RENDERED: Chickenpox (Varicella): 2 doses | acip-adult-2025 | p4 | p4/narrative/varicella-dose-count | narrative |
| zoster-dose-count | adults-19-plus | 2 doses | RENDERED: Shingles (Zoster): 2 doses | acip-adult-2025 | p4 | p4/narrative/zoster-dose-count | narrative |
| hpv-dose-count | adults-19-plus | 2 or 3 doses | RENDERED: HPV (Human papillomavirus): 2 or 3 doses | acip-adult-2025 | p4 | p4/narrative/hpv-dose-count | narrative |
| pneumococcal-dose-count | adults-19-plus | 1 or 2 doses | RENDERED: Pneumococcal: 1 or 2 doses | acip-adult-2025 | p5 | p5/narrative/pneumococcal-dose-count | narrative |
| hepatitis-a-dose-count | adults-19-plus | 2, 3, or 4 doses depending on vaccine used | 2, 3, or 4 doses depending on vaccine used | acip-adult-2025 | p5 | p5/narrative/hepatitis-a-dose-count | narrative |
| hepatitis-b-dose-count | adults-19-plus | 2, 3, or 4 doses depending on vaccine used | 2, 3, or 4 doses depending on vaccine used | acip-adult-2025 | p5 | p5/narrative/hepatitis-b-dose-count | narrative |
| meningococcal-dose-count | adults-19-plus | >=1 dose depending on vaccine, medical condition, and where patient lives or works | 1 or more doses depending on vaccine used, medical condition, where patient lives or works | acip-adult-2025 | p5 | p5/narrative/meningococcal-dose-count | narrative |
| hib-dose-count | adults-19-plus | 1 or 3 doses depending on medical condition | 1 or 3 doses depending on medical condition | acip-adult-2025 | p5 | p5/narrative/hib-dose-count | narrative |
| mpox-dose-count | adults-19-plus | 2 doses | RENDERED: Mpox: 2 doses | acip-adult-2025 | p5 | p5/narrative/mpox-dose-count | narrative |

## Conflicts

## Coverage

No recommendation record was available for this web capture. The complete source is accounted for by the span table above; rows use reserved narrative locators.
