# Group A streptococcal pharyngitis — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the guideline** and not a clinical instruction: every row is a fact this repo restates, and choosing among them is the clinician's. The source is a focused update about risk assessment and selection for diagnostic testing; it does not address the complete treatment of GAS pharyngitis.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2025-gas-risk | IDSA | IDSA/gas-pharyngitis-pico-a-b-guideline | guideline | 2025 focused update | 2025 | https://www.idsociety.org/globalassets/idsa/practice-guidelines/streptococcal-pharyngitits/gas-pharyngitis-pico-a-b-guideline-manuscript.pdf | chosen | bound |

## Scope

**Read:** all 13 source pages. The complete read covered the abstract, recommendation and remarks, introduction, methods, evidence summary, rationale, all three tables, implementation considerations, research needs, acknowledgments, disclosures, and references. The bound recommendation record contains 1 marker occurrence; bound-marker omissions warn rather than refuse, so the full-page read—not the marker record—establishes this sheet's scope. Table 1's accuracy estimates and study sample sizes and Table 2's validation-cohort probabilities were read but do not create rows because they describe evidence rather than a patient-action cutoff. Table 3's point assignments and risk bands remain because the guideline presents them as clinical decision aids for selecting diagnostic testing.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| abstract, recommendation, remarks, introduction, and methods | 1-3 | yes |
| evidence summary and Table 1 | 4-6 | read 2026-08-31; blind 2026-08-31 |
| rationale, Table 2, and testing-decision context | 6-7 | yes |
| implementation considerations and Table 3 scoring systems | 8-9 | yes |
| acknowledgments and disclosures | 9-11 | read 2026-08-31; blind 2026-08-31 |
| references | 12-13 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| children-adults-sore-throat | children and adults with sore throat |
| low-probability-gas | patients with low probability of GAS pharyngitis |
| high-risk-sore-throat | high-risk individuals presenting with sore throat, including those with household GAS exposure, previous rheumatic fever, or signs or symptoms of complicated local or systemic GAS infection |
| children-under-3 | children under three years of age |
| children-3plus-adults-sore-throat | children aged 3 and older and adults presenting with sore throat |
| centor-age-15plus | patients age 15 years or older assessed with the Centor score |
| mcisaac-age-3plus | patients age 3 years or older assessed with the McIsaac score |
| feverpain-scored | patients with sore throat assessed with the FeverPAIN score |
| school-aged-gas-carriers | school-aged children colonized with GAS and considered carriers |

## Quantities

| key | verbatim |
| --- | --- |
| testing-selection-system | clinical scoring system used to select patients for GAS testing |
| low-probability-testing | diagnostic-testing action at low probability of GAS pharyngitis |
| high-risk-testing-override | testing action for high-risk patients despite a low clinical score |
| scoring-system-laboratory-input | preference for a scoring system without laboratory tests |
| scoring-system-age-applicability | age boundary for applying the recommendation |
| scoring-system-choice | acceptable clinical scoring system choice |
| testing-decision-context | factors considered with the score when deciding on RADT, NAAT, or throat culture |
| low-risk-workflow | workflow action for low-risk patients |
| carrier-antimicrobial-treatment | antimicrobial-treatment action for GAS carriers |
| centor-feature-points | Centor feature point assignments |
| centor-risk-band | Centor score risk classification and observed GAS-positive percentage |
| mcisaac-feature-points | McIsaac clinical-feature point assignments |
| mcisaac-age-points | McIsaac age point assignments |
| mcisaac-risk-band | McIsaac score risk classification and observed GAS-positive percentage |
| feverpain-feature-points | FeverPAIN feature point assignments |
| feverpain-risk-band | FeverPAIN score risk classification and observed streptococcal-positive percentage |
| feverpain-evidence-status | evidence limitation affecting use of FeverPAIN |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| testing-selection-system | children-adults-sore-throat | use a clinical scoring system to determine who should be tested for GAS | RENDERED: In children and adults with sore throat, we suggest using a clinical scoring system to determine who should be tested for GAS | idsa-2025-gas-risk | p2 | p2/grade-spelled-out/1 |  |
| low-probability-testing | low-probability-gas | further diagnostic testing is unlikely to be helpful | RENDERED: Clinical scoring systems are most helpful in identifying patients with low probability of GAS pharyngitis, in whom further evaluation by diagnostic testing is unlikely to be helpful. | idsa-2025-gas-risk | p2 | p2/narrative/low-probability-testing | narrative |
| high-risk-testing-override | high-risk-sore-throat | strongly consider testing even when the clinical score is low | RENDERED: High-risk individuals should be strongly considered for testing even if their clinical scores are low. | idsa-2025-gas-risk | p2 | p2/narrative/high-risk-testing-override | narrative |
| scoring-system-laboratory-input | children-adults-sore-throat | may favor a clinical scoring system that does not include laboratory tests | RENDERED: clinicians and patients may favor clinical scoring systems that do not include laboratory test(s). | idsa-2025-gas-risk | p2 | p2/narrative/no-laboratory-score-preference | narrative |
| scoring-system-age-applicability | children-under-3 | do not apply this scoring-system recommendation to children under three years of age | RENDERED: The recommendation to use a scoring system does not apply to children under three years of age | idsa-2025-gas-risk | p2 | p2/narrative/under-3-exclusion | narrative |
| testing-selection-system | children-3plus-adults-sore-throat | scoring systems may predict GAS culture positivity in children age >=3 years and adults with sore throat | RENDERED: predict the likelihood of a positive throat culture for GAS among children aged 3 and older and adults presenting with sore throat | idsa-2025-gas-risk | p3 | p3/narrative/eligible-age-scope | narrative |
| scoring-system-choice | children-3plus-adults-sore-throat | Centor or McIsaac is an appropriate clinical decision-making aid; neither requires a blood test | RENDERED: both have been validated, and neither requires a blood test, the panel suggests that either one would be an appropriate choice as a clinical decision-making aid. | idsa-2025-gas-risk | p6 | p6/narrative/centor-mcisaac-choice | narrative |
| testing-decision-context | children-3plus-adults-sore-throat | decide on RADT, NAAT, or throat culture using the score together with individual risk factors, local epidemiology, testing and treatment costs, and patient and family preferences | RENDERED: decision-making regarding the need for further testing by RADT, NAAT, or throat culture, together with consideration of individual risk factors, local epidemiology, costs of testing and treatment, and patient and family preferences | idsa-2025-gas-risk | p7 | p7/narrative/testing-decision-context | narrative |
| low-risk-workflow | low-probability-gas | change workflows to use a clinical scoring system and avoid testing low-risk patients | RENDERED: we recommend workflow changes and the use of a clinical scoring system to identify low risk patients who do not require testing. | idsa-2025-gas-risk | p8 | p8/narrative/low-risk-workflow | narrative |
| carrier-antimicrobial-treatment | school-aged-gas-carriers | GAS carriers generally do not require antimicrobial treatment for acute GAS pharyngitis | RENDERED: these children generally do not require antimicrobial treatment for acute GAS pharyngitis. | idsa-2025-gas-risk | p8 | p8/narrative/carrier-treatment | narrative |
| centor-feature-points | centor-age-15plus | add 1 point each for absence of cough, swollen tender anterior cervical nodes, temperature >100.4 F (38 C), and tonsillar exudate or swelling | RENDERED: Absence of Cough 1; Swollen tender anterior cervical nodes 1; >100.4°F (38°C) 1; Tonsillar Exudate or swelling 1 | idsa-2025-gas-risk | p9 | p9/narrative/centor-feature-points | narrative |
| centor-risk-band | centor-age-15plus | score 0-1: low risk, 7%-12%; score 2-3: intermediate risk, 21%-38%; score 4: high risk, 57% | RENDERED: Low Risk 0-1 7-12%; Intermediate Risk 2-3 21-38%; High Risk 4 57% | idsa-2025-gas-risk | p9 | p9/narrative/centor-risk-bands | narrative |
| mcisaac-feature-points | mcisaac-age-3plus | add 1 point each for absence of cough, swollen tender anterior cervical nodes, temperature >100.4 F (38 C), and tonsillar exudate or swelling | RENDERED: Absence of Cough 1; Swollen tender anterior cervical nodes 1; >100.4°F (38°C) 1; Tonsillar Exudate or swelling 1 | idsa-2025-gas-risk | p9 | p9/narrative/mcisaac-feature-points | narrative |
| mcisaac-age-points | mcisaac-age-3plus | age 3-14 years: +1; age 15-44 years: 0; age >45 years: -1 | RENDERED: 3 y - 14 y 1; 15 y - 44 y 0; >45 y -1 | idsa-2025-gas-risk | p9 | p9/narrative/mcisaac-age-points | narrative |
| mcisaac-risk-band | mcisaac-age-3plus | score 0-1: low risk, 7.6%-13.1%; score 2-3: intermediate risk, 20.8%-33.6%; score 4-5: high risk, 50.7%-69.3% | RENDERED: Low Risk 0-1 7.6-13.1%; Intermediate Risk 2-3 20.8-33.6%; High Risk 4-5 50.7-69.3% | idsa-2025-gas-risk | p9 | p9/narrative/mcisaac-risk-bands | narrative |
| feverpain-feature-points | feverpain-scored | add 1 point each for absence of cough or coryza, fever in the past 24 hours, inflamed tonsils, purulent tonsils, and symptom onset <3 days | RENDERED: Absence of Cough or Coyrza 1; Febrile in past 24 h 1; Inflamed Tonsils 1; Purulent Tonsils 1; <3 days since symptom onset 1 | idsa-2025-gas-risk | p9 | p9/narrative/feverpain-feature-points | narrative |
| feverpain-risk-band | feverpain-scored | score 0-1: low risk, 1%-10%; score 2-3: intermediate risk, 11%-35%; score 4-5: high risk, 51%-53% | RENDERED: Low Risk 0-1 1-10%; Intermediate Risk 2-3 11-35%; High Risk 4-5 51%-53% | idsa-2025-gas-risk | p9 | p9/narrative/feverpain-risk-bands | narrative |
| feverpain-evidence-status | feverpain-scored | FeverPAIN was not compared with clinician judgment and was not included in the guideline's analysis | RENDERED: We did not find evidence that FeverPAIN has been compared ... and therefore we did not include this scoring system in our analysis. | idsa-2025-gas-risk | p9 | p9/narrative/feverpain-evidence-caveat | narrative |

## Conflicts

No within-sheet conflict was found. Centor, McIsaac, and FeverPAIN use method-dependent quantities and therefore their different point assignments and risk bands are alternatives rather than population conflicts. The guideline identifies Centor and McIsaac as appropriate aids but explicitly records that FeverPAIN was not compared with clinician judgment and was excluded from its analysis.

## Coverage

The bound source exposes 1 recommendation marker: `p2/grade-spelled-out/1` is cited by a threshold row. Marker accounting is 1 total = 1 cited + 0 disposed. Because the source is bound rather than exact, this accounting does not claim that the marker extractor enumerated every recommendation; the complete 13-page scope read supplies the document-level action accounting.
