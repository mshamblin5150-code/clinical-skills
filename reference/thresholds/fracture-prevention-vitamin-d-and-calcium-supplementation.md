# Fracture prevention, vitamin D and calcium supplementation — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2018 | USPSTF | USPSTF/vitamind-calcium-fracture-prevention-final-rec-statement | recommendation-statement | 2018 | 2018 | https://doi.org/10.1001/jama.2018.3185 | stated | exact |

## Scope

**Read:** the complete 8-page source, page by page, including the recommendation, clinical considerations, preventive medication evidence, related USPSTF recommendations, recommendations of others, article information, and references.

**Not read:** nothing.

**Scoped out under ADR 0009's numeric decision-point rule:** the preventive medication evidence on page 4 reports that a single study found an annual 500 000 IU vitamin D dose may be associated with more injurious falls and fractures. This evidence observation was read, but it is neither a prescribed dose nor a cutoff that changes patient action, so it does not produce a threshold row.

| span | pages | read |
| --- | --- | --- |
| complete recommendation statement, including interleaved article information and references | 1-8 | yes |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| community-postmenopausal-women | community-dwelling, postmenopausal women |
| community-adults-65-falls | community-dwelling adults 65 years or older |
| women-osteoporosis-screening | women 65 years or older |
| younger-women-increased-risk | younger women at increased risk |
| nof-adults | adults 50 years or older |
| endocrine-older-adults | adults 65 years or older |
| ags-older-adults | adults 65 years or older |

## Quantities

| key | verbatim |
| --- | --- |
| uspstf-vitamin-d-lower-dose | daily vitamin D dose at or below which supplementation is recommended against for fracture prevention |
| uspstf-calcium-lower-dose | daily calcium dose at or below which supplementation is recommended against for fracture prevention |
| uspstf-vitamin-d-higher-dose | daily vitamin D dose above which evidence is insufficient for fracture prevention |
| uspstf-calcium-higher-dose | daily calcium dose above which evidence is insufficient for fracture prevention |
| related-vitamin-d-falls-recommendation-age | age threshold for recommending against vitamin D supplementation to prevent falls |
| related-osteoporosis-screening-age | age threshold for osteoporosis screening in women |
| related-risk-based-osteoporosis-screening-age | age boundary for osteoporosis screening in younger women at increased risk |
| nof-vitamin-d-age-and-dose | National Osteoporosis Foundation age threshold and daily vitamin D intake |
| endocrine-vitamin-d-age-and-dose | Endocrine Society age threshold and daily vitamin D intake |
| ags-vitamin-d-age-and-dose | American Geriatrics Society age threshold and minimum daily vitamin D intake |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-vitamin-d-lower-dose | community-postmenopausal-women | <=400 IU/day: recommend against | daily supplementation with 400 IU or less of vitamin D | uspstf-2018 | p1 | p1/vitamin-d-calcium-or-combined-supplementation-fo/1 | D |
| uspstf-calcium-lower-dose | community-postmenopausal-women | <=1000 mg/day: recommend against | 1000 mg or less of calcium | uspstf-2018 | p1 | p1/vitamin-d-calcium-or-combined-supplementation-fo/1 | D |
| uspstf-vitamin-d-higher-dose | community-postmenopausal-women | >400 IU/day: evidence insufficient | doses greater than 400 IU of vitamin D | uspstf-2018 | p1 | p1/vitamin-d-calcium-or-combined-supplementation-fo/3 | I |
| uspstf-calcium-higher-dose | community-postmenopausal-women | >1000 mg/day: evidence insufficient | greater than 1000 mg of calcium | uspstf-2018 | p1 | p1/vitamin-d-calcium-or-combined-supplementation-fo/3 | I |
| related-vitamin-d-falls-recommendation-age | community-adults-65-falls | age >=65 years: recommend against vitamin D supplementation to prevent falls | RENDERED: recommends against vitamin D supplementation to prevent falls in community-dwelling adults 65 years or older | uspstf-2018 | p4 | p4/narrative/vitamin-d-falls-recommendation-age | narrative |
| related-osteoporosis-screening-age | women-osteoporosis-screening | age >=65 years: screen | screening for osteoporosis in women 65 years or older | uspstf-2018 | p4 | p4/narrative/osteoporosis-screening-age | narrative |
| related-risk-based-osteoporosis-screening-age | younger-women-increased-risk | age <65 years: screen when at increased risk | RENDERED: women 65 years or older and in younger women at increased risk | uspstf-2018 | p4 | p4/narrative/risk-based-osteoporosis-screening-age | narrative |
| nof-vitamin-d-age-and-dose | nof-adults | age >=50 years: 800 to 1000 IU/day | adults 50 years or older consume 800 to 1000 IU of vitamin D daily | uspstf-2018 | p7 | p7/narrative/nof-vitamin-d-age-dose | narrative |
| endocrine-vitamin-d-age-and-dose | endocrine-older-adults | age >=65 years: 800 IU/day | adults 65 years or older consume 800 IU of vitamin D daily | uspstf-2018 | p7 | p7/narrative/endocrine-vitamin-d-age-dose | narrative |
| ags-vitamin-d-age-and-dose | ags-older-adults | age >=65 years: >=1000 IU/day | adults 65 years or older take daily vitamin D supplementation of at least 1000 IU | uspstf-2018 | p7 | p7/narrative/ags-vitamin-d-age-dose | narrative |

## Conflicts

None.

## Coverage

- `p1/vitamin-d-calcium-or-combined-supplementation-fo/2` - the I statement for men and premenopausal women contains no numeric patient-action decision point
