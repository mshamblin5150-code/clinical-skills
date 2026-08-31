# Childhood Immunization Schedule — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete consumer schedules below. **Not a substitute for the schedules** and not a clinical instruction. The sources state that the posted July 2, 2025 schedules are the current CDC childhood immunization schedules under the court order described on page 1 of each capture.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| acip-young-2025 | ACIP | ACIP/Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC | web-capture | July 2, 2025 | 2025-07-02 | https://www.cdc.gov/vaccines/imz-schedules/child-easyread.html | stated | null |
| acip-older-2025 | ACIP | ACIP/Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC | web-capture | July 2, 2025 | 2025-07-02 | https://www.cdc.gov/vaccines/imz-schedules/adolescent-easyread.html | stated | null |

## Scope

**Read:** both complete web captures, page by page: all 4 pages of the birth-through-age-6 schedule and all 6 pages of the age-7-through-18 schedule. This included each court-order notice; purpose and applicability statement; parent/caregiver escalation criteria; every key; both complete rendered age tables; every vaccine-preventable-disease, complication, and dose row; footnotes; related links; page controls; and both site footers. The rendered age tables and dose tables were read visually because color, bar extent, cell alignment, and table geometry carry decision meaning not preserved completely in extracted text.

**Not read:** nothing.

Source: `acip-young-2025`

| span | pages | read |
| --- | --- | --- |
| court-order notice, purpose, applicability, escalation criteria, key, and rendered birth-through-age-6 schedule start | 1 | yes |
| rendered birth-through-age-6 schedule continuation and dose labels | 2 | yes |
| disease and complication content following the schedule on page 2, disease and complication table continuation, footnotes, page controls, related resources, and footer | 2-4 | read 2026-08-31; blind 2026-08-31 |

Source: `acip-older-2025`

| span | pages | read |
| --- | --- | --- |
| court-order notice, purpose, and applicability | 1 | yes |
| escalation criteria, key, and rendered age-7-through-18 schedule | 2 | yes |
| disease, complication, and dose table and footnotes | 3-4 | yes |
| page controls, related resources, and footer | 5-6 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| children-birth-through-6 | Birth Through 6 Years Old |
| children-7-through-18 | Children 7-18 Years Old |
| young-high-risk | child has any medical condition that puts them at higher risk for infection |
| older-high-risk-or-pregnant | child has any medical condition that puts them at higher risk for infection or is pregnant |
| traveling-child | child is traveling outside the United States |
| young-missed-vaccine | child misses a vaccine recommended for their age |
| older-missed-vaccine | child misses any vaccine recommended for their age or for babies and young children |
| infant-maternal-rsv-status | Depends on mother's RSV vaccine status |
| infant-health-status | Depends on child's health status |
| all-young-children | ALL children should be immunized at this age |
| some-young-children | SOME children should get this dose of vaccine or preventive antibody at this age |
| provider-discussion-young | Parents/caregivers should talk to their health care provider to decide if this vaccine is right for their child |
| all-older-children | ALL children in age group should get the vaccine |
| some-older-children | SOME children in age group should get the vaccine |
| optional-older-children | ALL children in age group can get the vaccine |
| provider-discussion-older | Parents/caregivers should talk to their health care provider to decide if this vaccine is right for their child |
| not-up-to-date | missed childhood doses |
| dirty-wound-child | dirty wounds |
| pregnant-child | every pregnancy |
| healthy-adolescents | Healthy adolescents |
| children-6-months-through-8 | some children aged 6 months through 8 years |
| dengue-eligible-child | living in a place where dengue is common AND has laboratory test confirming past dengue infection |

## Quantities

| key | verbatim |
| --- | --- |
| young-schedule-applicability | Recommended Immunizations for Birth Through 6 Years Old |
| older-schedule-applicability | Recommended Immunizations for Children 7-18 Years Old |
| higher-risk-guidance | Talk to your child's health care provider for more guidance |
| travel-guidance | Talk to your child's health care provider for more guidance |
| missed-vaccine-guidance | Talk to your child's health care provider for more guidance |
| rsv-antibody-age-schedule | RSV antibody |
| hepatitis-b-age-schedule | Hepatitis B |
| rotavirus-age-schedule | Rotavirus |
| dtap-age-schedule | DTaP |
| hib-age-schedule | Hib |
| pneumococcal-age-schedule | Pneumococcal |
| polio-age-schedule | Polio |
| covid-young-age-schedule | COVID-19 |
| influenza-young-age-schedule | Influenza/Flu |
| mmr-age-schedule | MMR |
| varicella-age-schedule | Chickenpox |
| hepatitis-a-age-schedule | Hepatitis A |
| hpv-age-schedule | HPV |
| tdap-age-schedule | Tdap |
| meningococcal-acwy-age-schedule | Meningococcal ACWY |
| meningococcal-b-age-schedule | Meningococcal B |
| influenza-older-age-schedule | Influenza/Flu |
| covid-older-age-schedule | COVID-19 |
| mpox-age-schedule | Mpox |
| dengue-age-schedule | Dengue |
| hpv-dose-count | Number of Vaccine Doses: HPV |
| tetanus-dose-count | Number of Vaccine Doses: Tetanus |
| diphtheria-dose-count | Number of Vaccine Doses: Diphtheria |
| pertussis-dose-count | Number of Vaccine Doses: Pertussis |
| meningococcal-dose-count | Number of Vaccine Doses: Meningococcal |
| influenza-dose-count | Number of Vaccine Doses: Influenza |
| covid-dose-count | Number of Vaccine Doses: COVID-19 |
| mpox-dose-count | Number of Vaccine Doses: Mpox |
| dengue-dose-count | Number of Vaccine Doses: Dengue |
| healthy-adolescent-meningococcal-dose-count | Healthy adolescents |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| young-schedule-applicability | children-birth-through-6 | birth through age 6 years | Recommended Immunizations for Birth Through 6 Years Old, United States, 2025 | acip-young-2025 | p1 | p1/narrative/young-schedule-applicability | narrative |
| higher-risk-guidance | young-high-risk | talk to health care provider for more guidance | Your child has any medical condition that puts them at higher risk for infection. | acip-young-2025 | p1 | p1/narrative/young-higher-risk-guidance | narrative |
| travel-guidance | traveling-child | talk to health care provider for more guidance | Your child is traveling outside the United States. | acip-young-2025 | p1 | p1/narrative/young-travel-guidance | narrative |
| missed-vaccine-guidance | young-missed-vaccine | talk to health care provider for more guidance | Your child misses a vaccine recommended for their age. | acip-young-2025 | p1 | p1/narrative/young-missed-vaccine-guidance | narrative |
| rsv-antibody-age-schedule | infant-maternal-rsv-status | birth through 7 months: preventive antibody depends on maternal RSV vaccine status | RENDERED: RSV antibody, birth through 7 months: Depends on mother's RSV vaccine status | acip-young-2025 | p1 | p1/narrative/rsv-antibody-maternal-status | narrative |
| rsv-antibody-age-schedule | infant-health-status | age 8 through 19 months: preventive antibody depends on child's health status | RENDERED: RSV antibody, ages 8 through 19 months: Depends on child's health status | acip-young-2025 | p1 | p1/narrative/rsv-antibody-child-health-status | narrative |
| hepatitis-b-age-schedule | all-young-children | dose 1 at birth; dose 2 at age 1-2 months; dose 3 at age 6-18 months | RENDERED: Hepatitis B, Dose 1 at Birth; Dose 2 spans 1 Month through 2 Months; Dose 3 spans 6 Months through 18 Months | acip-young-2025 | p2 | p2/narrative/hepatitis-b-age-schedule | narrative |
| rotavirus-age-schedule | all-young-children | dose 1 at 2 months; dose 2 at 4 months | RENDERED: Rotavirus, Dose 1 at 2 Months; Dose 2 at 4 Months | acip-young-2025 | p2 | p2/narrative/rotavirus-doses-1-2 | narrative |
| rotavirus-age-schedule | some-young-children | dose 3 at 6 months | RENDERED: Rotavirus, Dose 3 at 6 Months uses the key for SOME children | acip-young-2025 | p2 | p2/narrative/rotavirus-dose-3 | narrative |
| dtap-age-schedule | all-young-children | doses at 2, 4, and 6 months; dose 4 at 15-18 months; dose 5 at age 4-6 years | RENDERED: DTaP, Dose 1 at 2 Months; Dose 2 at 4 Months; Dose 3 at 6 Months; Dose 4 spans 15 through 18 Months; Dose 5 at 4-6 Years | acip-young-2025 | p2 | p2/narrative/dtap-age-schedule | narrative |
| hib-age-schedule | all-young-children | doses 1 and 2 at 2 and 4 months; dose 4 at 12-15 months | RENDERED: Hib, Dose 1 at 2 Months; Dose 2 at 4 Months; Dose 4 spans 12 through 15 Months | acip-young-2025 | p2 | p2/narrative/hib-routine-doses | narrative |
| hib-age-schedule | some-young-children | dose 3 at 6 months | RENDERED: Hib, Dose 3 at 6 Months uses the key for SOME children | acip-young-2025 | p2 | p2/narrative/hib-dose-3 | narrative |
| pneumococcal-age-schedule | all-young-children | doses at 2, 4, and 6 months; dose 4 at 12-15 months | RENDERED: Pneumococcal, Dose 1 at 2 Months; Dose 2 at 4 Months; Dose 3 at 6 Months; Dose 4 spans 12 through 15 Months | acip-young-2025 | p2 | p2/narrative/pneumococcal-age-schedule | narrative |
| polio-age-schedule | all-young-children | doses at 2 and 4 months; dose 3 at 6-18 months; dose 4 at age 4-6 years | RENDERED: Polio, Dose 1 at 2 Months; Dose 2 at 4 Months; Dose 3 spans 6 through 18 Months; Dose 4 at 4-6 Years | acip-young-2025 | p2 | p2/narrative/polio-age-schedule | narrative |
| covid-young-age-schedule | provider-discussion-young | age 6 months through 6 years: discuss with health care provider | RENDERED: COVID-19, ages 6 Months through 4-6 Years uses the key for parents/caregivers to talk to their health care provider | acip-young-2025 | p2 | p2/narrative/covid-young-age-schedule | narrative |
| influenza-young-age-schedule | all-young-children | age 6 months through 6 years: every year | RENDERED: Influenza/Flu, ages 6 Months through 4-6 Years: Every year | acip-young-2025 | p2 | p2/narrative/influenza-young-every-year | narrative |
| influenza-young-age-schedule | some-young-children | two doses for some children | Every year. Two doses for some children | acip-young-2025 | p2 | p2/narrative/influenza-young-two-doses | narrative |
| mmr-age-schedule | all-young-children | dose 1 at 12-15 months; dose 2 at age 4-6 years | RENDERED: MMR, Dose 1 spans 12 through 15 Months; Dose 2 at 4-6 Years | acip-young-2025 | p2 | p2/narrative/mmr-age-schedule | narrative |
| varicella-age-schedule | all-young-children | dose 1 at 12-15 months; dose 2 at age 4-6 years | RENDERED: Chickenpox, Dose 1 spans 12 through 15 Months; Dose 2 at 4-6 Years | acip-young-2025 | p2 | p2/narrative/varicella-age-schedule | narrative |
| hepatitis-a-age-schedule | all-young-children | 2 doses from age 12 through 23 months, separated by 6 months | RENDERED: Hepatitis A, 2 doses separated by 6 months spanning ages 12 through 20-23 Months | acip-young-2025 | p2 | p2/narrative/hepatitis-a-age-schedule | narrative |
| older-schedule-applicability | children-7-through-18 | age 7 through 18 years | Recommended Immunizations for Children 7-18 Years Old, United States, 2025 | acip-older-2025 | p1 | p1/narrative/older-schedule-applicability | narrative |
| higher-risk-guidance | older-high-risk-or-pregnant | talk to health care provider for more guidance | Your child has any medical condition that puts them at higher risk for infection or is pregnant. | acip-older-2025 | p2 | p2/narrative/older-higher-risk-guidance | narrative |
| travel-guidance | traveling-child | talk to health care provider for more guidance | Your child is traveling outside the United States. | acip-older-2025 | p2 | p2/narrative/older-travel-guidance | narrative |
| missed-vaccine-guidance | older-missed-vaccine | talk to health care provider for more guidance | Your child misses any vaccine recommended for their age or for babies and young children. | acip-older-2025 | p2 | p2/narrative/older-missed-vaccine-guidance | narrative |
| hpv-age-schedule | optional-older-children | age 9-10 years: all children can receive vaccine | RENDERED: HPV, ages 9 through 10 Years uses the key for ALL children in the age group can get the vaccine | acip-older-2025 | p2 | p2/narrative/hpv-age-9-10 | narrative |
| hpv-age-schedule | all-older-children | age 11-12 years: all children should receive vaccine | RENDERED: HPV, ages 11 through 12 Years uses the key for ALL children in the age group should get the vaccine | acip-older-2025 | p2 | p2/narrative/hpv-age-11-12 | narrative |
| tdap-age-schedule | all-older-children | age 11-12 years: all children should receive vaccine | RENDERED: Tdap, ages 11 through 12 Years uses the key for ALL children in the age group should get the vaccine | acip-older-2025 | p2 | p2/narrative/tdap-age-11-12 | narrative |
| meningococcal-acwy-age-schedule | all-older-children | age 11-12 years and age 16 years | RENDERED: Meningococcal ACWY uses the ALL-children key across ages 11 through 12 Years and at 16 Years | acip-older-2025 | p2 | p2/narrative/meningococcal-acwy-age-schedule | narrative |
| meningococcal-b-age-schedule | provider-discussion-older | age 16-18 years: discuss with health care provider | RENDERED: Meningococcal B, ages 16 through 18 Years uses the key for parents/caregivers to talk to their health care provider | acip-older-2025 | p2 | p2/narrative/meningococcal-b-age-schedule | narrative |
| influenza-older-age-schedule | all-older-children | age 7-18 years: every year | RENDERED: Influenza/Flu, ages 7 through 8 Years: Every year, two doses for some children; ages 9 through 18 Years: Every year | acip-older-2025 | p2 | p2/narrative/influenza-older-age-schedule | narrative |
| covid-older-age-schedule | provider-discussion-older | age 7-18 years: discuss with health care provider | RENDERED: COVID-19, ages 7 through 18 Years uses the key for parents/caregivers to talk to their health care provider | acip-older-2025 | p2 | p2/narrative/covid-older-age-schedule | narrative |
| mpox-age-schedule | some-older-children | age 18 years: some children should receive vaccine | RENDERED: Mpox at 18 Years uses the key for SOME children in the age group should get the vaccine | acip-older-2025 | p2 | p2/narrative/mpox-age-18 | narrative |
| dengue-age-schedule | dengue-eligible-child | age 9-16 years: only if both residence and prior-infection criteria are met | RENDERED: Dengue, ages 9 through 16 Years: ONLY if living in a place where dengue is common AND has laboratory test confirming past dengue infection | acip-older-2025 | p2 | p2/narrative/dengue-age-schedule | narrative |
| hpv-dose-count | children-7-through-18 | 2 or 3 doses | RENDERED: HPV (Human papillomavirus): 2 or 3 doses | acip-older-2025 | p3 | p3/narrative/hpv-dose-count | narrative |
| tetanus-dose-count | all-older-children | 1 dose at age 11-12 years | 1 dose at age 11-12 years | acip-older-2025 | p3 | p3/narrative/tetanus-age-dose | narrative |
| tetanus-dose-count | not-up-to-date | additional doses if missed childhood doses | Additional doses if missed childhood doses | acip-older-2025 | p3 | p3/narrative/tetanus-missed-doses | narrative |
| tetanus-dose-count | dirty-wound-child | 1 dose for dirty wounds | 1 dose for dirty wounds | acip-older-2025 | p3 | p3/narrative/tetanus-dirty-wound-dose | narrative |
| diphtheria-dose-count | all-older-children | 1 dose at age 11-12 years | 1 dose at age 11-12 years | acip-older-2025 | p3 | p3/narrative/diphtheria-age-dose | narrative |
| diphtheria-dose-count | not-up-to-date | additional doses if missed childhood doses | Additional doses if missed childhood doses | acip-older-2025 | p3 | p3/narrative/diphtheria-missed-doses | narrative |
| pertussis-dose-count | all-older-children | 1 dose at age 11-12 years | 1 dose at age 11-12 years | acip-older-2025 | p3 | p3/narrative/pertussis-age-dose | narrative |
| pertussis-dose-count | not-up-to-date | additional doses if missed childhood doses | Additional doses if missed childhood doses | acip-older-2025 | p3 | p3/narrative/pertussis-missed-doses | narrative |
| pertussis-dose-count | pregnant-child | 1 dose every pregnancy | 1 dose every pregnancy | acip-older-2025 | p3 | p3/narrative/pertussis-pregnancy-dose | narrative |
| meningococcal-dose-count | children-7-through-18 | 2 doses; additional doses may be needed depending on medical condition or vaccine used | RENDERED: Meningococcal: 2 doses; Additional doses may be needed depending on medical condition or vaccine used | acip-older-2025 | p3 | p3/narrative/meningococcal-dose-count | narrative |
| influenza-dose-count | children-7-through-18 | 1 dose each year | 1 dose each year | acip-older-2025 | p3 | p3/narrative/influenza-dose-count | narrative |
| influenza-dose-count | children-6-months-through-8 | 2 doses in some children age 6 months through 8 years | 2 doses in some children aged 6 months through 8 years | acip-older-2025 | p3 | p3/narrative/influenza-two-dose-age-band | narrative |
| covid-dose-count | children-7-through-18 | >=1 current dose depending on health status | 1 or more doses of the current COVID-19 vaccine depending on health status | acip-older-2025 | p4 | p4/narrative/covid-dose-count | narrative |
| mpox-dose-count | children-7-through-18 | 2 doses | RENDERED: Mpox: 2 doses | acip-older-2025 | p4 | p4/narrative/mpox-dose-count | narrative |
| dengue-dose-count | dengue-eligible-child | 3 doses | RENDERED: Dengue: 3 doses | acip-older-2025 | p4 | p4/narrative/dengue-dose-count | narrative |
| healthy-adolescent-meningococcal-dose-count | healthy-adolescents | meningococcal ACWY 2 doses; meningococcal B 2 doses if needed | RENDERED: Healthy adolescents: Meningococcal ACWY vaccine (2 doses); Meningococcal B vaccine (2 doses if needed) | acip-older-2025 | p4 | p4/narrative/healthy-adolescent-meningococcal-dose-count | narrative |

## Conflicts

CONFLICT: hpv-age-schedule — for `optional-older-children`, the complete value is `age 9-10 years: all children can receive vaccine`; for `all-older-children`, the complete value is `age 11-12 years: all children should receive vaccine`. These are population- and age-conditioned schedule branches.

CONFLICT: meningococcal-acwy-age-schedule — for `all-older-children`, the complete value is `age 11-12 years and age 16 years`; these are two scheduled age points for the same population.

CONFLICT: influenza-dose-count — for `children-7-through-18`, the complete value is `1 dose each year`; for `children-6-months-through-8`, the complete value is `2 doses in some children age 6 months through 8 years`. The second value is the age- and history-conditioned branch.

CONFLICT: meningococcal-dose-count — for `children-7-through-18`, the complete value is `2 doses; additional doses may be needed depending on medical condition or vaccine used`; for `healthy-adolescents`, `healthy-adolescent-meningococcal-dose-count` is `meningococcal ACWY 2 doses; meningococcal B 2 doses if needed`. The values distinguish the generic disease row from vaccine-specific healthy-adolescent branches.

CONFLICT: pertussis-dose-count — for `all-older-children`, the complete value is `1 dose at age 11-12 years`; for `not-up-to-date`, it is `additional doses if missed childhood doses`; for `pregnant-child`, it is `1 dose every pregnancy`. These are population- and indication-conditioned branches.

CONFLICT: tetanus-dose-count — for `all-older-children`, the complete value is `1 dose at age 11-12 years`; for `not-up-to-date`, it is `additional doses if missed childhood doses`; for `dirty-wound-child`, it is `1 dose for dirty wounds`. These are population- and indication-conditioned branches.

## Coverage

The current PDF-bound recommendation sweeps reported nothing-found with 0 recommendations for both `ACIP/Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.json` and `ACIP/Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.json`. Both records are present nothing-found records, not absent records. Source mode is null for each; every row therefore uses a page-bound narrative locator. The complete 4-page and 6-page reads, not the zero-row recommendation records, establish the denominators.
