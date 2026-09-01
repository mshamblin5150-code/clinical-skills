# Abdominal aortic aneurysm screening - threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's. Graded by `tools/threshold_sheet.py`;
what that grader cannot see is written out in [README.md](README.md).

Every `snippet` cell is a short verbatim USPSTF fragment carrying the decision
point. Evidence-result numbers, test-performance statistics, and recommendations
attributed to other organizations are not represented as USPSTF decision points.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2019 | USPSTF | USPSTF/abdom-aortic-aneurysm-screening-final-rs | recommendation-statement | 2019 | 2019 | https://doi.org/10.1001/jama.2019.18928 | stated | exact |

## Scope

**Read:** all eight source pages. This included the recommendation statements,
Practice Considerations, screening and treatment discussion, supporting evidence,
research needs, recommendations attributed to other organizations, article
information, and references. The attributed recommendations were read but were not
restated as USPSTF decision points.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| recommendations and practice considerations | 1-4 | yes |
| supporting evidence and article information | 4-7 | yes |
| references | 7-8 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-adults | asymptomatic adults |
| asymptomatic-adults-50-or-older | asymptomatic adults 50 years or older |
| men-65-75-ever-smoked | men aged 65 to 75 years who have ever smoked |
| men-65-75-never-smoked | men aged 65 to 75 years who have never smoked |
| women-65-75-ever-smoked-or-family-history | women aged 65 to 75 years who have ever smoked or have a family history of AAA |
| men-initially-normal-ultrasonography | men with initially normal results on ultrasonography |
| men-with-aaa | men with an AAA |
| patients-with-aaa | patients with an AAA |

## Quantities

| key | verbatim |
| --- | --- |
| aaa-defining-diameter | aortic enlargement with a diameter of 3.0 cm or larger |
| recommendation-applicability-lower-age | applies to asymptomatic adults 50 years or older |
| screening-age-range | aged 65 to 75 years |
| screening-frequency-ultrasonography | 1-time screening for AAA with ultrasonography |
| ever-smoker-cigarette-count | defines an "ever smoker" as someone who has smoked 100 or more cigarettes |
| normal-ultrasonography-aaa-diameter | initially normal results on ultrasonography (defined as an AAA <3 cm in diameter) |
| elective-repair-aaa-diameter | AAA of 5.5 cm or larger in diameter |
| rapidly-enlarging-repair-minimum-diameter | AAA larger than 4.0 cm in diameter that has rapidly increased in size |
| rapid-enlargement-amount-and-period | an increase of 1.0 cm in diameter over a 1-year period |
| surgical-referral-aaa-diameter | AAA of 5.5 cm or larger in diameter should be referred for surgical intervention |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aaa-defining-diameter | asymptomatic-adults | >=3.0 cm | "aortic enlargement with a diameter of 3.0 cm or larger" | uspstf-2019 | p2 | p2/narrative/1 | narrative |
| recommendation-applicability-lower-age | asymptomatic-adults-50-or-older | >=50 years | "applies to asymptomatic adults 50 years or older" | uspstf-2019 | p2 | p2/narrative/2 | narrative |
| screening-age-range | men-65-75-ever-smoked | 65-75 years | "men aged 65 to 75 years who have ever smoked" | uspstf-2019 | p1 | p1/screening-for-abdominal-aortic-aneurysm/1 | B |
| screening-frequency-ultrasonography | men-65-75-ever-smoked | 1-time | "The USPSTF recommends 1-time screening for AAA with ultrasonography in men aged 65 to 75 years who have ever smoked." | uspstf-2019 | p1 | p1/screening-for-abdominal-aortic-aneurysm/1 | B |
| screening-age-range | men-65-75-never-smoked | 65-75 years | "men aged 65 to 75 years who have never smoked" | uspstf-2019 | p1 | p1/screening-for-abdominal-aortic-aneurysm/2 | C |
| screening-age-range | women-65-75-ever-smoked-or-family-history | 65-75 years | "women aged 65 to 75 years who have ever smoked or have a family history of AAA" | uspstf-2019 | p1 | p1/screening-for-abdominal-aortic-aneurysm/4 | I |
| ever-smoker-cigarette-count | men-65-75-ever-smoked | >=100 cigarettes | "someone who has smoked 100 or more cigarettes" | uspstf-2019 | p2 | p2/narrative/3 | narrative |
| normal-ultrasonography-aaa-diameter | men-initially-normal-ultrasonography | <3 cm | "defined as an AAA <3 cm in diameter" | uspstf-2019 | p3 | p3/narrative/1 | narrative |
| elective-repair-aaa-diameter | men-with-aaa | >=5.5 cm | "men with an AAA of 5.5 cm or larger in diameter" | uspstf-2019 | p3 | p3/narrative/2 | narrative |
| rapidly-enlarging-repair-minimum-diameter | men-with-aaa | >4.0 cm | "an AAA larger than 4.0 cm in diameter that has rapidly increased in size" | uspstf-2019 | p3 | p3/narrative/3 | narrative |
| rapid-enlargement-amount-and-period | men-with-aaa | >=1.0 cm in 1 year | "defined as an increase of 1.0 cm in diameter over a 1-year period" | uspstf-2019 | p3 | p3/narrative/4 | narrative |
| surgical-referral-aaa-diameter | patients-with-aaa | >=5.5 cm | "patients with an AAA of 5.5 cm or larger in diameter should be referred for surgical intervention" | uspstf-2019 | p4 | p4/narrative/1 | narrative |

## Conflicts

The repeated 65-to-75-year screening range applies to different recommendation
populations and does not represent a conflict. The two 5.5-cm rows distinguish the
source's statement about standard repair practice in men from its general referral
statement for patients with AAA.

## Coverage

- `p1/screening-for-abdominal-aortic-aneurysm/3` - no numeric decision point
