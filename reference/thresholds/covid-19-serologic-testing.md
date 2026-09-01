# COVID-19 serologic testing — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the source** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2024 | IDSA | IDSA/ciae121 | guideline | 2024 update | 2024-03-15 | https://doi.org/10.1093/cid/ciae121 | stated | bound |

## Scope

**Read:** all 28 pages, including every recommendation, remark, figure, table, evidence profile, discussion, disclosure, and reference page. The spans below account for the complete document.

**Not read:** nothing. Prose spans without a retained numeric patient-action decision point carry completed first-read and blind markers. Reference-only pages are exempt.

| span | pages | read |
| --- | --- | --- |
| abstract, introduction, executive recommendations, and remarks | 1-4 | yes |
| background and methods | 5-6 | read 2026-08-31; blind 2026-08-31 |
| acute-diagnosis, negative-NAAT, MIS-C, and prior-infection recommendations and evidence | 7-13 | yes |
| antibody-target recommendation and diagnostic-performance evidence tables | 14-20 | read 2026-08-31; blind 2026-08-31 |
| prior-infection or vaccination recommendation and evidence | 21-22 | read 2026-08-31; blind 2026-08-31 |
| assay-performance implementation guidance | 23 | yes |
| discussion, notes, and disclosures | 24-26 | read 2026-08-31; blind 2026-08-31 |
| references | 27-28 | exempt: reference list; no first-read or blind marker required |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 92e88b2ef5bcb1f87fd3d617ea696b10e3b1141f08214c61dedcd4a0e79ae9fd; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| symptomatic-suspected-acute-covid | symptomatic individuals being evaluated for acute SARS-CoV-2 infection |
| prior-infection-evidence-desired | individuals for whom evidence of previous SARS-CoV-2 infection is desired |
| repeatedly-negative-naat-serology | symptomatic unvaccinated individuals without prior SARS-CoV-2 infection who have repeatedly negative NAAT results and a negative serologic test |
| suspected-misc-cdc-laboratory-evidence | patients being evaluated under the 2023 CDC confirmed MIS-C case definition |
| serology-assay-selection | patients for whom SARS-CoV-2 serologic testing is clinically indicated |

## Quantities

| key | verbatim |
| --- | --- |
| acute-serology-exclusion-window | period after symptom onset during which serology should not be used to diagnose SARS-CoV-2 infection |
| prior-infection-serology-window | timing for seeking evidence of previous SARS-CoV-2 infection |
| negative-serology-alternative-evaluation | timing after which persistent symptoms and negative serology should prompt evaluation for alternative etiologies in the narrow evidence population |
| cdc-misc-infection-evidence-window | CDC window for RNA or antigen evidence used in the confirmed MIS-C case definition |
| serology-assay-performance | minimum sensitivity and specificity for a serologic assay when testing is performed |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| acute-serology-exclusion-window | symptomatic-suspected-acute-covid | do not use serologic testing to diagnose SARS-CoV-2 infection during the first 2 weeks after symptom onset | "recommends against serologic testing to diagnose SARS-CoV-2 infection in the first 2 weeks after symptom onset" | idsa-2024 | p1 | p1/grade-spelled-out/1 | strong recommendation, low certainty of evidence |
| acute-serology-exclusion-window | symptomatic-suspected-acute-covid | do not use serologic testing to diagnose SARS-CoV-2 infection during the first 2 weeks after symptom onset | RENDERED: "recommends against using serologic testing to diagnose SARS-CoV-2 infection during the first 2 weeks following symptom onset" | idsa-2024 | p2 | p2/grade-spelled-out/1 | strong recommendation, low certainty of evidence |
| acute-serology-exclusion-window | symptomatic-suspected-acute-covid | do not use serologic testing to diagnose SARS-CoV-2 infection during the first 2 weeks after symptom onset | RENDERED: "recommends against using serologic testing to diagnose SARS-CoV-2 infection during the first 2 weeks following symptom onset" | idsa-2024 | p7 | p7/grade-spelled-out/1 | strong recommendation, low certainty of evidence |
| prior-infection-serology-window | prior-infection-evidence-desired | test 3-5 weeks after symptom onset | "testing for immunoglobulin G (IgG), IgG/IgM, or total antibodies to nucleocapsid protein 3 to 5 weeks after symptom onset" | idsa-2024 | p1 | p1/grade-spelled-out/4 | conditional recommendation, low certainty of evidence |
| prior-infection-serology-window | prior-infection-evidence-desired | test 3-5 weeks after symptom onset | RENDERED: "testing for SARS-CoV-2 IgG, IgG/IgM, or total antibodies 3 to 5 weeks after symptom onset and against testing for SARS-CoV-2 IgM" | idsa-2024 | p3 | p3/grade-spelled-out/2 | conditional recommendation, low certainty of evidence |
| prior-infection-serology-window | prior-infection-evidence-desired | test 3-5 weeks after symptom onset | RENDERED: "testing for SARS-CoV-2 IgG, IgG/IgM, or total antibodies 3 to 5 weeks after symptom onset and suggests against testing for SARS-CoV-2 IgM" | idsa-2024 | p13 | p13/grade-spelled-out/1 | conditional recommendation, low certainty of evidence |
| negative-serology-alternative-evaluation | repeatedly-negative-naat-serology | when serology performed >2 weeks after symptom onset is negative and symptoms persist, evaluate for alternative etiologies | "the negative predictive value of a SARS-CoV-2 serologic test is high when performed more than 2 weeks after symptom onset. In this instance, negative serologic results should prompt further evaluation of the patients' symptoms for alternative etiologies, if symptoms persist" | idsa-2024 | p12 | p12/narrative/negative-serology-alternative-evaluation | narrative |
| cdc-misc-infection-evidence-window | suspected-misc-cdc-laboratory-evidence | CDC confirmed-case laboratory evidence includes SARS-CoV-2 RNA or antigen detected up to 60 days before or during hospitalization or postmortem | RENDERED: "the 2023 CDC definition of a confirmed case of MIS-C requires meeting clinical and laboratory criteria; the latter include detection of SARS-CoV-2 RNA or antigen in a specimen up to 60 days before or during hospitalization or postmortem" | idsa-2024 | p13 | p13/narrative/cdc-misc-infection-evidence-window | narrative |
| serology-assay-performance | serology-assay-selection | whenever possible, use assays with established sensitivity and specificity >=99.5% | "Whenever possible, serologic assays with established high sensitivity and specificity (ie, ≥99.5%) should be employed" | idsa-2024 | p23 | p23/narrative/assay-performance | narrative |

## Conflicts

None. The page-1 abstract includes the nucleocapsid target in the same sentence as the 3-5-week window, while Recommendations 4 and 5 separate timing and antibody target. The threshold rows retain only their common timing value, so the qualitative assay choices do not create a false numeric conflict.

## Coverage

The bound recommendation file contains exactly 17 recommendation records: 6 are cited above and 11 are scoped below.

- `p1/grade-spelled-out/2` - scoped out because the recommendation against using serology after repeatedly negative NAAT results is qualitative.
- `p1/grade-spelled-out/3` - scoped out because serology to assist MIS-C diagnosis is qualitative.
- `p1/grade-spelled-out/5` - scoped out because the recommendation against routine testing after infection or vaccination is qualitative.
- `p2/grade-spelled-out/2` - scoped out because it repeats the qualitative recommendation against IgG testing after repeatedly negative NAAT results.
- `p3/grade-spelled-out/1` - scoped out because using both IgG testing and NAAT for suspected MIS-C is qualitative.
- `p4/grade-spelled-out/1` - scoped out because selecting nucleocapsid rather than spike assays is qualitative.
- `p4/grade-spelled-out/2` - scoped out because routine testing after infection or vaccination is discouraged without a numeric boundary.
- `p8/grade-spelled-out/1` - scoped out because it repeats the qualitative recommendation against IgG testing after repeatedly negative NAAT results.
- `p12/grade-spelled-out/1` - scoped out because it repeats the qualitative MIS-C testing recommendation.
- `p14/grade-spelled-out/1` - scoped out because it repeats the qualitative nucleocapsid-versus-spike assay recommendation.
- `p21/grade-spelled-out/1` - scoped out because it repeats the qualitative recommendation against routine serology after infection or vaccination.

ADR 0009 disposition: the 2-week exclusion and 3-5-week prior-infection testing window are the source's numeric patient-action decisions and are retained. The separate nucleocapsid-versus-spike selection and the recommendation against IgM alone remain represented in source-faithful snippets and recommendation dispositions without inventing additional numeric cutoffs.

ADR 0009 disposition: study-specific diagnostic sensitivity and specificity estimates, pretest probabilities, effects per 1,000 tested, study sample sizes, seroprevalence, assay turnaround times, follow-up intervals, vaccination schedules, and other study or epidemiologic numbers in Figures 1-2 and Tables 1A-2D are evidence descriptors rather than additional adopted testing thresholds and are scoped out. This exclusion does not include the adopted assay-selection floor of sensitivity and specificity >=99.5%, which is retained above.

ADR 0009 disposition: the negative-spike-antibody discussion for immunocompromised candidates for immune therapy is explicitly framed as a potentially useful metric and not as an assay cutoff or routine testing recommendation; no numeric action is inferred from it.

ADR 0009 disposition: the 2023 CDC MIS-C 60-day RNA-or-antigen window is external case-definition guidance quoted and adopted as a laboratory-evidence boundary in the IDSA discussion; its CDC provenance is preserved in the population, quantity, value, and snippet.

Source: `C:/codeing/guidelines-recs/IDSA/ciae121.json` (mode `bound`, counted from text markers). Source PDF SHA-256: `92e88b2ef5bcb1f87fd3d617ea696b10e3b1141f08214c61dedcd4a0e79ae9fd`.
