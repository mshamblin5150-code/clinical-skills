# Oral health screening and prevention — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from both source documents below. **Not a substitute
for either guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2023-oral-health-adults-screening-int-6404fa | USPSTF | USPSTF/oral-health-adults-screening-interventions-final-recommendation | recommendation-statement | 2023 | 2023 | https://doi.org/10.1001/jama.2023.21409 | stated | exact |
| uspstf-2023-oral-health-children-final-recom-ee8ca0 | USPSTF | USPSTF/oral-health-children-final-recommendation | recommendation-statement | 2023 | 2023 | https://doi.org/10.1001/jama.2023.21408 | stated | exact |

## Scope

**Read:** both complete recommendation statements. The adult source includes the
recommendations, practice considerations, screening tests and interventions,
supporting evidence, response, research needs, and recommendations of others on pp.
1-6. The child and adolescent source covers those classes of material on pp. 1-7.
Both reference lists are retired by class because they contain citations rather than
clinical prose.

**Not read:** nothing in either source page range.

**Source: `uspstf-2023-oral-health-adults-screening-int-6404fa`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations and suggestions for practice | 2-4 | yes |
| supporting evidence | 4-5 | read 2026-08-30; blind 2026-08-30 |
| response | 5 | read 2026-08-30; blind 2026-08-30 |
| research needs, recommendations of others, and article information | 6 | read 2026-08-30; blind 2026-08-30 |
| references | 7 | exempt: citation list has no clinical prose |

**Source: `uspstf-2023-oral-health-children-final-recom-ee8ca0`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations and suggestions for practice | 2-4 | yes |
| supporting evidence | 5-6 | read 2026-08-30; blind 2026-08-30 |
| response | 6 | read 2026-08-30; blind 2026-08-30 |
| research needs, recommendations of others, and article information | 7 | read 2026-08-30; blind 2026-08-30 |
| references | 7-8 | exempt: citation list has no clinical prose |

**Second read:** a blind independent read dated 2026-08-30 corroborated that the
marked null spans contain no additional current USPSTF decision point.

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-adults | asymptomatic adults 18 years or older |
| asymptomatic-children-and-adolescents-5-to-17 | asymptomatic children and adolescents aged 5 to 17 years |

## Quantities

| key | verbatim |
| --- | --- |
| primary-care-oral-health-screening | routine screening performed by primary care clinicians for oral health conditions |
| primary-care-oral-health-prevention | preventive interventions performed by primary care clinicians for oral health conditions |
| i-statement-practice | whether to perform screening or preventive services when evidence is insufficient |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary-care-oral-health-screening | asymptomatic-adults | evidence insufficient | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of routine screening performed by primary care clinicians for oral health conditions, including dental caries or periodontal-related disease, in adults. | uspstf-2023-oral-health-adults-screening-int-6404fa | p1 | p1/screening-and-preventive-interventions-for-oral/1 | I |
| primary-care-oral-health-prevention | asymptomatic-adults | evidence insufficient | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of preventive interventions performed by primary care clinicians for oral health conditions, including dental caries or periodontal-related disease, in adults. | uspstf-2023-oral-health-adults-screening-int-6404fa | p1 | p1/screening-and-preventive-interventions-for-oral/2 | I |
| i-statement-practice | asymptomatic-adults | use clinical expertise to decide whether to perform these services | In the absence of evidence, primary care clinicians should use their clinical expertise to decide whether to perform these services. | uspstf-2023-oral-health-adults-screening-int-6404fa | p3 | p3/narrative/i-statement-practice | narrative |
| primary-care-oral-health-screening | asymptomatic-children-and-adolescents-5-to-17 | evidence insufficient | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of routine screening performed by primary care clinicians for oral health conditions, including dental caries, in children and adolescents aged 5 to 17 years. | uspstf-2023-oral-health-children-final-recom-ee8ca0 | p1 | p1/screening-and-preventive-interventions-for-oral/1 | I |
| primary-care-oral-health-prevention | asymptomatic-children-and-adolescents-5-to-17 | evidence insufficient | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of preventive interventions performed by primary care clinicians for oral health conditions, including dental caries, in children and adolescents aged 5 to 17 years. | uspstf-2023-oral-health-children-final-recom-ee8ca0 | p1 | p1/screening-and-preventive-interventions-for-oral/2 | I |
| i-statement-practice | asymptomatic-children-and-adolescents-5-to-17 | use clinical expertise to decide whether to perform these services | In the absence of evidence, primary care clinicians should use their clinical expertise to decide whether to perform these services. | uspstf-2023-oral-health-children-final-recom-ee8ca0 | p3 | p3/narrative/i-statement-practice | narrative |

## Conflicts

## Coverage
