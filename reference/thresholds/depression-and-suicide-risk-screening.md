# Depression and suicide risk screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from both source documents below. **Not a substitute
for either guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2023 | USPSTF | USPSTF/depression-suicide-risk-adults-rs | recommendation-statement | 2023 | 2023 | https://doi.org/10.1001/jama.2023.9297 | stated | exact |
| uspstf-2022 | USPSTF | USPSTF/screening-depression-suicide-risk-children-final-recommendation | recommendation-statement | 2022 | 2022 | https://doi.org/10.1001/jama.2022.16946 | stated | exact |

## Scope

**Read:** both complete recommendation statements. The adult source includes its
recommendations, practice considerations, screening tests and intervals, treatment,
implementation, supporting evidence, response, research needs, and recommendations
of others on pp. 1-9. The child and adolescent source includes the same classes of
material on pp. 1-7. Both reference lists are retired by class because they contain
citations rather than clinical prose.

**Not read:** nothing in either source page range.

**Source: `uspstf-2023`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations, screening, treatment, and implementation | 2-5 | yes |
| supporting evidence | 6-8 | read 2026-08-30; blind 2026-08-30 |
| response and research needs | 8 | read 2026-08-30; blind 2026-08-30 |
| recommendations of others and article information | 9 | read 2026-08-30; blind 2026-08-30 |
| references | 9-11 | exempt: citation list has no clinical prose |

**Source: `uspstf-2022`**

| span | pages | read |
| --- | --- | --- |
| recommendation statement and assessment | 1-2 | yes |
| practice considerations, screening, treatment, and implementation | 2-5 | yes |
| supporting evidence | 6-7 | read 2026-08-30; blind 2026-08-30 |
| response, research needs, recommendations of others, and article information | 7 | read 2026-08-30; blind 2026-08-30 |
| references | 8-9 | exempt: citation list has no clinical prose |

**Second read:** a blind independent read dated 2026-08-30 corroborated that the
marked null spans contain no additional current USPSTF decision point.

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| adults | adults, including pregnant and postpartum persons, and older adults |
| adults-no-diagnosed-disorder-or-recognized-symptoms | adults 19 years or older who do not have a diagnosed mental health disorder or recognizable signs or symptoms of depression or suicide risk |
| adolescents-12-to-18 | adolescents aged 12 to 18 years |
| children-11-or-younger | children 11 years or younger |
| children-and-adolescents | children and adolescents |
| adolescents-with-depression-risk-factors | adolescents with risk factors for depression |
| children-8-or-older-with-mdd | children 8 years or older with MDD |
| adolescents-12-to-17-with-mdd | adolescents aged 12 to 17 years with MDD |
| postpartum-persons | persons in the postpartum period |
| persons-with-mdd | persons with major depressive disorder |
| older-adults | older adults |
| antidepressant-starters | patients of all ages who start antidepressant therapy |

## Quantities

| key | verbatim |
| --- | --- |
| depression-screening | screening for depression or MDD |
| suicide-risk-screening | screening for suicide risk |
| adult-screening-applicability | adults to whom this recommendation applies |
| positive-screen-follow-up | action after a positive screening result |
| depression-screening-interval | timing for screening for depression |
| mdd-drug-eligibility | FDA-approved medication for treating MDD |
| postpartum-period | postpartum period following delivery |
| mdd-duration | duration used in the definition of MDD |
| older-adult-age | age used to define older adults |
| antidepressant-monitoring | monitoring after antidepressant therapy starts |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depression-screening | adults | screen | The USPSTF recommends screening for depression in the adult population, including pregnant and postpartum persons and older adults. | uspstf-2023 | p1 | p1/screening-for-depression-and-suicide-risk-in-adu/1 | B |
| suicide-risk-screening | adults | evidence insufficient | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of screening for suicide risk in the adult population, including pregnant and postpartum persons and older adults. | uspstf-2023 | p1 | p1/screening-for-depression-and-suicide-risk-in-adu/2 | I |
| adult-screening-applicability | adults-no-diagnosed-disorder-or-recognized-symptoms | age >=19 years | This recommendation applies to adults 19 years or older who do not have a diagnosed mental health disorder or recognizable signs or symptoms of depression or suicide risk. | uspstf-2023 | p2 | p2/narrative/adult-screening-applicability | narrative |
| postpartum-period | postpartum-persons | first 12 months following delivery | first 12 months following delivery | uspstf-2023 | p2 | p2/narrative/postpartum-period | narrative |
| mdd-duration | persons-with-mdd | >=2 weeks | at least 2 weeks | uspstf-2023 | p2 | p2/narrative/mdd-duration | narrative |
| older-adult-age | older-adults | age >=65 years | Older adults are defined as those 65 years or older. | uspstf-2023 | p2 | p2/narrative/older-adult-age | narrative |
| positive-screen-follow-up | adults | additional assessment after a positive screen | positive screening results | uspstf-2023 | p3 | p3/narrative/positive-screen-follow-up | narrative |
| depression-screening-interval | adults-no-diagnosed-disorder-or-recognized-symptoms | screen adults not previously screened | adults who have not been screened previously | uspstf-2023 | p5 | p5/narrative/depression-screening-interval | narrative |
| depression-screening | adolescents-12-to-18 | screen | The USPSTF recommends screening for MDD in adolescents aged 12 to 18 years. | uspstf-2022 | p1 | p1/screening-for-depression-and-suicide-risk-in-chi/1 | B |
| depression-screening | children-11-or-younger | evidence insufficient | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of screening for MDD in children 11 years or younger. | uspstf-2022 | p1 | p1/screening-for-depression-and-suicide-risk-in-chi/2 | I |
| suicide-risk-screening | children-and-adolescents | evidence insufficient | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of screening for suicide risk in children and adolescents. | uspstf-2022 | p1 | p1/screening-for-depression-and-suicide-risk-in-chi/3 | I |
| depression-screening-interval | adolescents-with-depression-risk-factors | repeated or opportunistic screening may be appropriate; optimal interval unknown | The USPSTF found no evidence on appropriate or recommended screening intervals for depression, and the optimal interval is unknown. Repeated screening may be most productive in adolescents with risk factors for depression. Opportunistic screening may be appropriate for adolescents, who may have infrequent health care visits. | uspstf-2022 | p4 | p4/narrative/depression-screening-interval | narrative |
| positive-screen-follow-up | children-and-adolescents | diagnose and treat with evidence-based care after a positive screen | Adequate systems and clinical staff are needed to ensure that patients are screened and, if they screen positive, are appropriately diagnosed and treated with evidence-based care. | uspstf-2022 | p4 | p4/narrative/positive-screen-follow-up | narrative |
| mdd-drug-eligibility | children-8-or-older-with-mdd | fluoxetine at age >=8 years | fluoxetine is the only medication approved by the US Food and Drug Administration (FDA) for use in treating MDD in children 8 years or older | uspstf-2022 | p4 | p4/narrative/fluoxetine-age | narrative |
| mdd-drug-eligibility | adolescents-12-to-17-with-mdd | escitalopram at age 12 to 17 years | aged 12 to 17 years | uspstf-2022 | p4 | p4/narrative/escitalopram-age | narrative |
| antidepressant-monitoring | antidepressant-starters | monitor closely for clinical worsening, suicidality, or unusual behavior changes | The FDA has issued a boxed warning for antidepressants, recommending that patients of all ages who start antidepressant therapy be monitored appropriately and observed closely for clinical worsening, suicidality, or unusual changes in behavior. | uspstf-2022 | p4 | p4/narrative/antidepressant-monitoring | narrative |

## Conflicts

## Coverage
