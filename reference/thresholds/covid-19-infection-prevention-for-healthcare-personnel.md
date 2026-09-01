# COVID-19 infection prevention for healthcare personnel — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the source** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2021 | IDSA | IDSA/ciab953 | guideline | November 2021 | 2021-11-15 | https://doi.org/10.1093/cid/ciab953 | stated | bound |

## Scope

**Read:** all 20 pages, including the full recommendation text, figures, tables, evidence profiles, narrative summaries, discussion, disclosures, and references. The page spans below account for the complete document.

**Not read:** nothing. Every prose span without a retained numeric patient-action decision point carries a completed first-read and blind marker. Pages containing only references are exempt from decision-point extraction.

| span | pages | read |
| --- | --- | --- |
| title, abstract, executive summary, background, methods, and definitions | 1-6 | read 2026-08-31; blind 2026-08-31 |
| routine-care PPE recommendations, eye protection, glove and shoe-cover knowledge gaps, aerosol-generating procedures, and evidence profiles | 7-12 | read 2026-08-31; blind 2026-08-31 |
| extended-use and reuse definitions and CDC limits | 13 | yes |
| fit testing, PAPR and universal-masking narratives, discussion, conclusions, notes, disclosures, and initial references | 14-17 | read 2026-08-31; blind 2026-08-31 |
| references | 18-20 | exempt: reference list; no first-read or blind marker required |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 3a701cd223c58705307d453a73c4b4f08ba5eeb2cf46c48f7100a76ad6f5b908; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| hcp-extended-n95-shortage | healthcare personnel using an N95 respirator for extended use during contingency or crisis capacity settings with N95 respirator shortages |
| hcp-reusing-n95-shortage | healthcare personnel reusing an N95 respirator during contingency or crisis capacity settings with N95 respirator shortages |

## Quantities

| key | verbatim |
| --- | --- |
| n95-extended-use-limit | CDC maximum period for extended use of one N95 respirator without removal between consecutive patient encounters |
| n95-reuse-limit | CDC maximum number of reuses of one N95 respirator when the manufacturer does not specify a limit |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n95-extended-use-limit | hcp-extended-n95-shortage | CDC maximum extended-use period 8-12 hours | "The CDC recommends a maximum extended use period of 8-12 hours" | idsa-2021 | p13 | p13/narrative/cdc-extended-use-limit | narrative |
| n95-reuse-limit | hcp-reusing-n95-shortage | unless the manufacturer specifies otherwise, CDC limit no more than 5 reuses per device | "Unless the manufacturer specifies otherwise, the CDC suggests limiting N95 respirator reuse to no more than 5 times per device" | idsa-2021 | p13 | p13/narrative/cdc-reuse-limit | narrative |

## Conflicts

None. The source's laboratory findings that filtration or fit could remain acceptable through 1-3, 3, or 3-5 decontamination or donning cycles are evidence descriptors, not alternative adopted reuse instructions, and do not conflict with the CDC limit retained above.

## Coverage

The bound recommendation file contains exactly 12 recommendation records. None contains an independent numeric patient-action decision point; all 12 are scoped below. The two retained numeric actions are page-bound narrative statements attributed by the guideline to CDC guidance.

- `p2/grade-spelled-out/1` - scoped out because using a medical/surgical mask or an N95, N99, or PAPR rather than no mask is a qualitative PPE-selection recommendation; digits in respirator product names are not numeric thresholds.
- `p3/grade-spelled-out/1` - scoped out because using eye protection rather than none is qualitative.
- `p3/grade-spelled-out/2` - scoped out because using an N95, N99, or PAPR rather than a medical/surgical mask for aerosol-generating procedures is qualitative; digits in product names are not thresholds.
- `p3/grade-spelled-out/3` - scoped out because using a reprocessed N95 rather than a medical/surgical mask during shortages is qualitative; the adjacent numeric reuse limit is captured through its page-bound CDC narrative locator.
- `p3/grade-spelled-out/4` - scoped out because adding a face shield or medical/surgical mask over an N95 for extended use during shortages is qualitative; the adjacent numeric extended-use limit is captured through its page-bound CDC narrative locator.
- `p3/grade-spelled-out/5` - scoped out because adding a face shield or medical/surgical mask over an N95 for reuse during shortages is qualitative; the adjacent numeric reuse limit is captured through its page-bound CDC narrative locator.
- `p7/grade-spelled-out/1` - scoped out because it repeats the qualitative routine-care mask or respirator recommendation.
- `p9/grade-spelled-out/1` - scoped out because it repeats the qualitative eye-protection recommendation.
- `p12/grade-spelled-out/1` - scoped out because it repeats the qualitative respirator-selection recommendation for aerosol-generating procedures.
- `p12/grade-spelled-out/2` - scoped out because it repeats the qualitative reprocessed-N95 recommendation during shortages.
- `p13/grade-spelled-out/1` - scoped out because covering an N95 to allow extended use is qualitative; the CDC's numeric maximum period is captured separately through the page-bound narrative locator.
- `p13/grade-spelled-out/2` - scoped out because covering an N95 to allow reuse is qualitative; the CDC's numeric maximum reuse count is captured separately through the page-bound narrative locator.

ADR 0009 disposition: the guideline's recommendation-shaped PPE selections are qualitative and remain in the source. N95 and N99 are respirator designations, recommendation numbers 1-8 and figure/table numbers are locators, and none is converted into a numeric clinical threshold.

ADR 0009 disposition: the retained 8-12-hour extended-use maximum and no-more-than-5-times reuse limit are explicitly attributed by the guideline to CDC guidance rather than presented as new IDSA panel recommendations. Their external provenance is preserved in both quantity definitions and values.

ADR 0009 disposition: decontamination temperatures, humidity, particle sizes, reprocessing cycles, consecutive donnings, study follow-up, participant counts, infection rates, effect estimates, confidence intervals, tolerability shifts, and other evidence-profile or laboratory-performance numbers describe studies rather than additional adopted patient or personnel actions and are scoped out.

ADR 0009 disposition: Figures 1-2 and Tables 1-6 contain PPE algorithms, GRADE interpretation, evidence profiles, and study outcomes. They were fully read; no additional numeric patient-action threshold was adopted from their rendered structure.

Source: `C:/codeing/guidelines-recs/IDSA/ciab953.json` (mode `bound`, counted from text markers). Source PDF SHA-256: `3a701cd223c58705307d453a73c4b4f08ba5eeb2cf46c48f7100a76ad6f5b908`.
