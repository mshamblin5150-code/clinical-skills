# Dental caries prevention - threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source document below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2021-dental-caries-young-children | USPSTF | USPSTF/dental-caries-young children-final-rec-statement | recommendation-statement | 2021 | 2021 | https://doi.org/10.1001/jama.2021.20007 | stated | exact |

## Scope

**Read:** the complete recommendation statement on pp. 1-6, including the summary
and recommendations, assessment and rationale, practice considerations, clinician
summary, timing and dosage, supporting evidence, response to public comment,
research needs, and recommendations of others. The references on p. 7 are retired
by class because they contain citations rather than clinical prose.

**Not read:** nothing in the clinical page range.

| span | pages | read |
| --- | --- | --- |
| summary, recommendations, assessment, and rationale | 1-2 | yes |
| clinician summary | 3 | read 2026-08-31; blind 2026-08-31 |
| timing and dosage, suggestions for practice, and beginning of supporting evidence | 4 | yes |
| supporting evidence, response to public comment, and beginning of research needs | 5 | read 2026-08-31; blind 2026-08-31 |
| research needs, recommendations of others, and article information | 6 | yes |
| references | 7 | exempt: citation list has no clinical prose |

**Second read:** a blind independent read dated 2026-08-31 corroborated that the
clinician summary on p. 3 and the supporting-evidence span on p. 5 contain no
additional numeric patient-action decision point.

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-children | asymptomatic children |
| children-water-supply-deficient-in-fluoride | children whose water supply is deficient in fluoride |
| young-children | young children |
| children-younger-than-5 | children younger than 5 years |
| all-children | all children |
| children-high-risk-for-caries | children at high risk for caries |
| children | children |
| children-younger-than-6-at-risk-for-caries | children younger than 6 years who are at risk for developing dental caries |
| children-at-risk-drinking-fluoride-deficient-water | children at risk for caries who drink fluoride-deficient (<0.6 ppm F) water |
| children-increased-risk-for-caries | children at increased risk for caries |

## Quantities

| key | verbatim |
| --- | --- |
| recommendation-applicability-age | recommendation applies to |
| oral-fluoride-supplementation-starting-age | oral fluoride supplementation starting at age |
| deficient-water-fluoridation-threshold | deficient water fluoridation |
| varnish-sodium-fluoride-concentration | sodium fluoride |
| varnish-fluoride-concentration | fluoride |
| varnish-typical-administration-interval | fluoride varnish was most commonly administered |
| aap-risk-assessment-starting-age | oral health risk assessments on all children at every routine well-child visit beginning at age |
| aap-varnish-minimum-interval | applied at least once every 6 months for all children |
| aap-varnish-high-risk-interval | every 3 months for children at high risk for caries |
| aap-first-dental-visit-age | first dental visit by age |
| ada-dental-visit-after-first-tooth-interval | seen by a dentist within 6 months of eruption of the first tooth |
| ada-latest-dental-visit-age | no later than age 12 months |
| ada-varnish-eligibility-age | children younger than 6 years |
| ada-varnish-fluoride-concentration | fluoride varnish |
| aapd-fluoride-deficient-water-threshold | fluoride-deficient water |
| aapd-sodium-fluoride-varnish-concentration | sodium fluoride varnish |
| aapd-acidulated-phosphate-fluoride-concentration | acidulated phosphate fluoride |
| aapd-professional-fluoride-treatment-interval | professional fluoride treatment |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| recommendation-applicability-age | asymptomatic-children | <5 years | This recommendation applies to asymptomatic children younger than 5 years. | uspstf-2021-dental-caries-young-children | p2 | p2/narrative/recommendation-applicability-age | narrative |
| oral-fluoride-supplementation-starting-age | children-water-supply-deficient-in-fluoride | 6 months | The USPSTF recommends that primary care clinicians prescribe oral fluoride supplementation starting at age 6 months for children whose water supply is deficient in fluoride. | uspstf-2021-dental-caries-young-children | p1 | p1/screening-and-interventions-to-prevent-dental-ca/2 | B |
| deficient-water-fluoridation-threshold | children-younger-than-5 | <0.6 ppm F | RENDERED: Oral fluoride supplementation prevents dental caries in patients with deficient water fluoridation (<0.6 parts fluoride per million parts water [ppm F]). | uspstf-2021-dental-caries-young-children | p2 | p2/narrative/deficient-water-fluoridation-threshold | narrative |
| varnish-sodium-fluoride-concentration | young-children | 5% sodium fluoride | Topical fluoride is applied as a varnish with a small brush in young children (typically available as 5% sodium fluoride [2.26% fluoride]). | uspstf-2021-dental-caries-young-children | p2 | p2/narrative/varnish-sodium-fluoride-concentration | narrative |
| varnish-fluoride-concentration | young-children | 2.26% fluoride | Topical fluoride is applied as a varnish with a small brush in young children (typically available as 5% sodium fluoride [2.26% fluoride]). | uspstf-2021-dental-caries-young-children | p2 | p2/narrative/varnish-fluoride-concentration | narrative |
| varnish-typical-administration-interval | children-younger-than-5 | 6 months | In studies, fluoride varnish was most commonly administered as 5% sodium fluoride, every 6 months. | uspstf-2021-dental-caries-young-children | p4 | p4/narrative/varnish-typical-administration-interval | narrative |
| aap-risk-assessment-starting-age | all-children | 6 months | The American Academy of Pediatrics (AAP) recommends that pediatricians perform oral health risk assessments on all children at every routine well-child visit beginning at age 6 months. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aap-risk-assessment-starting-age | narrative |
| aap-varnish-minimum-interval | all-children | 6 months | RENDERED: The AAP also recommends fluoride varnish application according to the AAP/Bright Futures Periodicity Schedule (applied at least once every 6 months for all children and every 3 months for children at high risk for caries) and dietary fluoride supplements for all children who do not have an adequate supply of fluoride in their primary drinking water. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aap-varnish-minimum-interval | narrative |
| aap-varnish-high-risk-interval | children-high-risk-for-caries | 3 months | RENDERED: The AAP also recommends fluoride varnish application according to the AAP/Bright Futures Periodicity Schedule (applied at least once every 6 months for all children and every 3 months for children at high risk for caries) and dietary fluoride supplements for all children who do not have an adequate supply of fluoride in their primary drinking water. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aap-varnish-high-risk-interval | narrative |
| aap-first-dental-visit-age | children | 1 year | The AAP recommends a first dental visit by age 1 year. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aap-first-dental-visit-age | narrative |
| ada-dental-visit-after-first-tooth-interval | children | 6 months | The American Dental Association recommends that children be seen by a dentist within 6 months of eruption of the first tooth and no later than age 12 months. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/ada-dental-visit-after-first-tooth-interval | narrative |
| ada-latest-dental-visit-age | children | 12 months | The American Dental Association recommends that children be seen by a dentist within 6 months of eruption of the first tooth and no later than age 12 months. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/ada-latest-dental-visit-age | narrative |
| ada-varnish-eligibility-age | children-younger-than-6-at-risk-for-caries | <6 years | RENDERED: It also recommends 2.26% fluoride varnish for children younger than 6 years who are at risk for developing dental caries. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/ada-varnish-eligibility-age | narrative |
| ada-varnish-fluoride-concentration | children-younger-than-6-at-risk-for-caries | 2.26% fluoride | RENDERED: It also recommends 2.26% fluoride varnish for children younger than 6 years who are at risk for developing dental caries. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/ada-varnish-fluoride-concentration | narrative |
| aapd-fluoride-deficient-water-threshold | children-at-risk-drinking-fluoride-deficient-water | <0.6 ppm F | RENDERED: The American Academy of Pediatric Dentistry states that fluoride dietary supplements should be considered for children at risk for caries who drink fluoride-deficient (<0.6 ppm F) water. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aapd-fluoride-deficient-water-threshold | narrative |
| aapd-sodium-fluoride-varnish-concentration | children-increased-risk-for-caries | 5% sodium fluoride varnish | It also states that children at increased risk for caries should receive a professional fluoride treatment (eg, 5% sodium fluoride varnish or 1.23% acidulated phosphate fluoride) every 6 months. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aapd-sodium-fluoride-varnish-concentration | narrative |
| aapd-acidulated-phosphate-fluoride-concentration | children-increased-risk-for-caries | 1.23% acidulated phosphate fluoride | It also states that children at increased risk for caries should receive a professional fluoride treatment (eg, 5% sodium fluoride varnish or 1.23% acidulated phosphate fluoride) every 6 months. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aapd-acidulated-phosphate-fluoride-concentration | narrative |
| aapd-professional-fluoride-treatment-interval | children-increased-risk-for-caries | 6 months | It also states that children at increased risk for caries should receive a professional fluoride treatment (eg, 5% sodium fluoride varnish or 1.23% acidulated phosphate fluoride) every 6 months. | uspstf-2021-dental-caries-young-children | p6 | p6/narrative/aapd-professional-fluoride-treatment-interval | narrative |

## Conflicts

## Coverage

- `p1/screening-and-interventions-to-prevent-dental-ca/1` - The recommendation uses the event of primary tooth eruption rather than a numeric patient-action decision point.
- `p1/screening-and-interventions-to-prevent-dental-ca/3` - The I statement contains no numeric patient-action decision point.
