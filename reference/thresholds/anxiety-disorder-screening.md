# Anxiety disorder screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2023 | USPSTF | USPSTF/anxiety-adults-screening-final-recommendation | recommendation-statement | 2023 | 2023 | https://doi.org/10.1001/jama.2023.9301 | stated | exact |

## Scope

**Read:** the complete source, page by page, including the recommendations, practice considerations, evidence, recommendations of others, article information, and references; the pure reference list is retired by class.

**Not read:** nothing.

| span | pages | read |
| --- | --- | --- |
| recommendation, practice considerations, evidence, and recommendations of others | 1-6 | yes |
| article information and recommendations of others | 7 | yes |
| references | 7-8 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-adults-19-to-64 | adults aged 19 to 64 years, including pregnant and postpartum persons, who do not have a diagnosed mental health disorder and are not showing recognized signs or symptoms of anxiety disorders |
| asymptomatic-older-adults | older adults |
| perinatal-patients | patients during the perinatal period |
| female-patients-without-anxiety-diagnosis | all female patients 13 years or older not currently diagnosed with an anxiety disorder |

## Quantities

| key | verbatim |
| --- | --- |
| adult-screening-age | adults aged 19 to 64 years |
| older-adult-i-statement-age | older adults (65 years or older) |
| acog-perinatal-screen-count | screening patients at least once during the perinatal period |
| wpsi-screening-age | all female patients 13 years or older |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| adult-screening-age | asymptomatic-adults-19-to-64 | age >=19 and <65 years: screen | RENDERED: adults (19 years or older); older adults (65 years or older) | uspstf-2023 | p2 | p2/narrative/adult-screening-age | narrative |
| older-adult-i-statement-age | asymptomatic-older-adults | age >=65 years: evidence insufficient | 65 years or older | uspstf-2023 | p2 | p2/narrative/older-adult-i-statement-age | narrative |
| acog-perinatal-screen-count | perinatal-patients | screen at least once during the perinatal period | at least once during the perinatal period | uspstf-2023 | p7 | p7/narrative/acog-perinatal-screen-count | narrative |
| wpsi-screening-age | female-patients-without-anxiety-diagnosis | age >=13 years: include in anxiety screening | 13 years or older | uspstf-2023 | p7 | p7/narrative/wpsi-screening-age | narrative |

## Conflicts

## Coverage

- `p1/screening-for-anxiety-disorders-in-adults/1` - the B branch is encoded above by its lower and upper numeric age boundaries.
- `p1/screening-for-anxiety-disorders-in-adults/2` - the I branch is encoded above by its numeric older-adult boundary.
