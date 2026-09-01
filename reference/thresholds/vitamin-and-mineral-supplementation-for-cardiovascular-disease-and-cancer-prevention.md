# Vitamin and mineral supplementation for cardiovascular disease and cancer prevention — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source document below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2022 | USPSTF | USPSTF/multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation | recommendation-statement | 2022 final recommendation | 2022-06-21 | https://doi.org/10.1001/jama.2022.8970 | stated | exact |

## Scope

**Read:** the complete 8-page recommendation statement: recommendation, evidence
assessment, and applicability on pp. 1-3; practice considerations, harms, related
recommendations, and review scope on pp. 3-4; nutrient-specific benefit and harm
evidence on pp. 4-6; recommendations of others and article information on p. 6; and
the reference list on pp. 7-8.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's decision-point rule:** national prevalence and mortality
counts, trial sample sizes, odds and risk ratios, confidence intervals, statistical
heterogeneity, publication and comment dates, author information, and study follow-up
periods that do not alter supplement selection, eligibility, a harm boundary, or the
interpretation of benefit. Trial doses linked to a reported harm are retained as
evidence boundaries, not converted into prescribing instructions.

**Source: `uspstf-2022`**

| span | pages | read |
| --- | --- | --- |
| recommendation, evidence assessment, rationale, and applicability | 1-3 | yes |
| practice considerations, harms, related recommendations, update, and review scope | 3-4 | yes |
| nutrient-specific benefit and harm evidence | 4-6 | yes |
| research needs and recommendations of others | 6 | yes |
| article information and disclosures | 6 | read 2026-09-01; blind 2026-09-01 |
| references | 7-8 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| community-dwelling-nonpregnant-adults | community-dwelling, nonpregnant adults |
| excluded-populations | children; persons who are pregnant or may become pregnant; persons who are chronically ill, hospitalized, or have a known nutritional deficiency |
| persons-planning-or-capable-of-pregnancy | all persons who are planning or capable of pregnancy |
| evidence-review-adults | community-dwelling, nonpregnant adults 18 years or older without known cardiovascular disease or chronic disease other than hypertension, overweight, or obesity, and without nutritional deficiencies |
| persons-with-acute-or-chronic-illness | persons who have an acute or chronic illness |
| community-adults-beta-carotene-or-vitamin-e | community-dwelling, nonpregnant adults considering beta carotene or vitamin E to prevent cardiovascular disease or cancer |
| community-adults-multivitamins | community-dwelling, nonpregnant adults considering multivitamins to prevent cardiovascular disease or cancer |
| community-adults-other-single-paired | community-dwelling, nonpregnant adults considering single- or paired-nutrient supplements other than beta carotene or vitamin E to prevent cardiovascular disease or cancer |
| smokers-or-asbestos-exposed | persons who smoke tobacco or have occupational or workplace exposure to asbestos |
| adults-in-beta-carotene-harm-trials | adults in beta carotene harm trials, including smokers or persons with workplace asbestos exposure |
| adults-in-vitamin-e-harm-trials | adults in trials reporting hemorrhagic stroke with vitamin E supplementation |
| women-in-vitamin-a-cohorts | women in cohort studies of vitamin A supplementation and hip fracture |
| women-in-vitamin-b6-cohort | women in a cohort study comparing high with low vitamin B6 intake |
| persons-taking-vitamin-d | persons taking vitamin D in trials or cohort studies reporting kidney stones |
| men-taking-vitamin-c | men in cohort studies of vitamin C supplementation and kidney stones |
| healthy-persons | healthy persons addressed by the American Heart Association nutrition guidance |
| general-population-nutritional-needs | people addressed by the US Department of Health and Human Services dietary guidance |
| adults-in-nutrient-benefit-evidence | community-dwelling, nonpregnant adults represented in the supplement benefit evidence |
| people-addressed-by-related-uspstf-guidance | people addressed by separate USPSTF cardiovascular disease, cancer, fracture, falls, and neural-tube-defect prevention recommendations |

## Quantities

| key | verbatim |
| --- | --- |
| beta-carotene-vitamin-e-prevention | use of beta carotene or vitamin E supplements to prevent cardiovascular disease or cancer |
| beta-carotene-net-benefit | USPSTF balance of beta carotene benefits and harms |
| vitamin-e-net-benefit | USPSTF balance of vitamin E benefits and harms |
| beta-carotene-harms-magnitude | USPSTF evidence assessment of beta carotene harms |
| vitamin-e-harms-magnitude | USPSTF evidence assessment of vitamin E harms |
| multivitamin-harms-magnitude | USPSTF evidence assessment of multivitamin harms |
| other-single-paired-harms-evidence | USPSTF evidence assessment of harms from other single- or paired-nutrient supplements |
| multivitamin-prevention-evidence | balance of benefits and harms of multivitamins to prevent cardiovascular disease or cancer |
| other-single-paired-prevention-evidence | balance of benefits and harms of single- or paired-nutrient supplements other than beta carotene and vitamin E |
| source-applicability | population to which this recommendation applies and populations it excludes |
| folic-acid-separate-guidance | daily folic acid supplementation under a separate USPSTF recommendation |
| evidence-review-population | population included in the commissioned evidence review |
| individual-judgment-under-i-statement | individual clinical judgment when evidence is insufficient |
| beta-carotene-lung-cancer-harm | lung-cancer harm from beta carotene in higher-risk persons |
| excessive-supplement-dose-harm | general adverse-effect boundary for excessive vitamin doses |
| vitamin-a-dose-harm | bone, liver, and fetal harms associated with vitamin A dose intensity |
| high-dose-vitamin-d-harm | hypercalcemia and kidney-stone harms at high vitamin D doses |
| beta-carotene-harm-trial-doses | beta carotene and co-administered vitamin A doses in trials reporting serious harms |
| beta-carotene-skin-discoloration | orange skin discoloration with beta carotene |
| vitamin-e-hemorrhagic-stroke-doses | vitamin E doses in trials reporting hemorrhagic stroke |
| vitamin-b6-hip-fracture-intake | vitamin B6 intake boundary associated with hip fracture in a cohort study |
| vitamin-d-kidney-stone-dose | vitamin D dose boundary associated with kidney stones in cohort studies |
| vitamin-c-kidney-stone-evidence | kidney-stone association with vitamin C supplementation |
| calcium-kidney-stone-evidence | kidney-stone association with calcium supplementation |
| vitamin-a-hip-fracture-evidence | hip-fracture evidence from vitamin A cohort studies in women |
| beta-carotene-benefit-evidence | cardiovascular disease and cancer benefit evidence for beta carotene |
| vitamin-e-benefit-evidence | cardiovascular disease and cancer benefit evidence for vitamin E |
| multivitamin-benefit-limitations | limitations of multivitamin benefit evidence |
| vitamin-d-pooled-outcome-evidence | pooled cardiovascular disease and cancer outcome evidence for vitamin D with or without calcium |
| vitamin-d-effect-heterogeneity | uncertainty about variation in vitamin D effects by patient characteristics |
| calcium-benefit-evidence | mortality, cardiovascular disease, and cancer benefit evidence for calcium |
| nonpregnant-folic-acid-mortality-cvd-evidence | mortality and cardiovascular disease evidence for folic acid with or without vitamin B12 in nonpregnant adults |
| nonpregnant-folic-acid-cancer-evidence | cancer evidence for folic acid with or without vitamin B12 in nonpregnant adults |
| vitamin-c-benefit-evidence | mortality, cardiovascular disease, and cancer benefit evidence for vitamin C |
| vitamin-b3-b6-benefit-evidence | benefit evidence for vitamins B3 and B6 |
| selenium-benefit-evidence | mortality, cardiovascular disease, and cancer benefit evidence for selenium |
| population-effect-heterogeneity | uncertainty about effect variation across populations and baseline nutrient status |
| illness-management-boundary | supplementation for management of acute or chronic illness |
| related-uspstf-cross-guidance | separate USPSTF prevention recommendations related to cardiovascular disease, cancer, fractures, falls, and neural-tube defects |
| food-first-dietary-guidance | external guidance to meet nutritional needs primarily through foods and beverages |
| aha-nutrient-guidance | external guidance to obtain nutrients from varied foods rather than supplements |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| beta-carotene-vitamin-e-prevention | community-adults-beta-carotene-or-vitamin-e | do not use beta carotene or vitamin E supplements to prevent cardiovascular disease or cancer; Grade D | The USPSTF recommends against the use of beta carotene or vitamin E supplements for the prevention of cardiovascular disease or cancer. | uspstf-2022 | p1 | p1/vitamin-mineral-and-multivitamin-supplementation/1 | D |
| multivitamin-prevention-evidence | community-adults-multivitamins | evidence is insufficient to assess the balance of benefits and harms; I statement | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of the use of multivitamin supplements for the prevention of cardiovascular disease or cancer. | uspstf-2022 | p1 | p1/vitamin-mineral-and-multivitamin-supplementation/2 | I |
| other-single-paired-prevention-evidence | community-adults-other-single-paired | evidence is insufficient to assess the balance of benefits and harms; I statement | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of the use of single- or paired-nutrient supplements (other than beta carotene and vitamin E) for the prevention of cardiovascular disease or cancer. | uspstf-2022 | p1 | p1/vitamin-mineral-and-multivitamin-supplementation/3 | I |
| beta-carotene-net-benefit | community-adults-beta-carotene-or-vitamin-e | harms outweigh benefits; moderate certainty | RENDERED: The US Preventive Services Task Force (USPSTF) concludes with moderate certainty that the harms of beta carotene supplementation outweigh the benefits for the prevention of cardiovascular disease or cancer. | uspstf-2022 | p2 | p2/narrative/beta-carotene-net-benefit | narrative |
| vitamin-e-net-benefit | community-adults-beta-carotene-or-vitamin-e | no net benefit; moderate certainty | RENDERED: The USPSTF also concludes with moderate certainty that there is no net benefit of supplementation with vitamin E for the prevention of cardiovascular disease or cancer. | uspstf-2022 | p2 | p2/narrative/vitamin-e-net-benefit | narrative |
| beta-carotene-harms-magnitude | smokers-or-asbestos-exposed | adequate evidence of small harm from increased lung-cancer risk in persons at increased risk | RENDERED: Adequate evidence that beta carotene causes small harms in increasing the risk for lung cancer in persons at increased risk. | uspstf-2022 | p2 | p2/narrative/beta-carotene-harms-magnitude | narrative |
| vitamin-e-harms-magnitude | community-adults-beta-carotene-or-vitamin-e | adequate evidence of at most small harms | RENDERED: Adequate evidence that vitamin E causes at most small harms. | uspstf-2022 | p2 | p2/narrative/vitamin-e-harms-magnitude | narrative |
| multivitamin-harms-magnitude | community-adults-multivitamins | adequate evidence of at most small harms | RENDERED: Adequate evidence that multivitamins cause at most small harms. | uspstf-2022 | p2 | p2/narrative/multivitamin-harms-magnitude | narrative |
| other-single-paired-harms-evidence | community-adults-other-single-paired | evidence inadequate for harms other than beta carotene or vitamin E | RENDERED: Inadequate evidence on the harms of supplementation with single or paired nutrients (other than beta carotene or vitamin E). | uspstf-2022 | p2 | p2/narrative/other-single-paired-harms-evidence | narrative |
| source-applicability | community-dwelling-nonpregnant-adults | recommendation applies | RENDERED: This recommendation applies to community-dwelling, nonpregnant adults. | uspstf-2022 | p3 | p3/narrative/source-applicability | narrative |
| source-applicability | excluded-populations | recommendation does not apply | RENDERED: It does not apply to children, persons who are pregnant or may become pregnant, or persons who are chronically ill, are hospitalized, or have a known nutritional deficiency. | uspstf-2022 | p3 | p3/narrative/source-exclusions | narrative |
| folic-acid-separate-guidance | persons-planning-or-capable-of-pregnancy | RELATED USPSTF: take a daily supplement containing 400 to 800 μg folic acid | RENDERED: The USPSTF separately recommends that all persons who are planning or capable of pregnancy take a daily supplement containing 0.4 to 0.8 mg (400-800 μg) of folic acid. | uspstf-2022 | p3 | p3/narrative/folic-acid-separate-guidance | narrative |
| individual-judgment-under-i-statement | community-adults-multivitamins | use clinical judgment to decide whether a vitamin supplement should be recommended for an individual patient | RENDERED: Clinicians should ... determine whether vitamin supplements should be recommended for an individual patient. | uspstf-2022 | p3 | p3/narrative/individual-judgment-under-i-statement | narrative |
| individual-judgment-under-i-statement | community-adults-other-single-paired | use clinical judgment to decide whether a vitamin supplement should be recommended for an individual patient | RENDERED: Clinicians should ... determine whether vitamin supplements should be recommended for an individual patient. | uspstf-2022 | p3 | p3/narrative/individual-judgment-under-i-statement-other | narrative |
| evidence-review-population | evidence-review-adults | evidence review focused on adults at least 18 years old in the stated community, pregnancy, disease, and deficiency boundaries | RENDERED: The review focused on community-dwelling, nonpregnant adults 18 years or older without known cardiovascular disease or chronic disease (other than hypertension, overweight, or obesity) or nutritional deficiencies. | uspstf-2022 | p4 | p4/narrative/evidence-review-population | narrative |
| beta-carotene-lung-cancer-harm | smokers-or-asbestos-exposed | increased lung-cancer incidence is an important harm | RENDERED: an important harm of increased lung cancer incidence was reported with the use of beta carotene by persons who smoke tobacco or have occupational exposure to asbestos. | uspstf-2022 | p3 | p3/narrative/beta-carotene-lung-cancer-harm | narrative |
| excessive-supplement-dose-harm | community-dwelling-nonpregnant-adults | excessive vitamin-supplement doses can cause adverse effects | Excessive doses of vitamin supplements can cause several known adverse effects | uspstf-2022 | p4 | p4/narrative/excessive-supplement-dose-harm | narrative |
| vitamin-a-dose-harm | community-dwelling-nonpregnant-adults | moderate doses may reduce bone-mineral density; high doses may be hepatotoxic or teratogenic | moderate doses of vitamin A supplements may reduce bone mineral density, and high doses may be hepatotoxic or teratogenic. | uspstf-2022 | p4 | p4/narrative/vitamin-a-dose-harm | narrative |
| high-dose-vitamin-d-harm | community-dwelling-nonpregnant-adults | high doses may cause hypercalcemia and kidney stones | Vitamin D has potential harms, such as a risk of hypercalcemia and kidney stones, when given at high doses. | uspstf-2022 | p4 | p4/narrative/high-dose-vitamin-d-harm | narrative |
| beta-carotene-benefit-evidence | adults-in-nutrient-benefit-evidence | no benefit for preventing cardiovascular disease or cancer | Adequate evidence that supplementation with beta carotene provides no benefit in preventing cardiovascular disease or cancer. | uspstf-2022 | p2 | p2/narrative/beta-carotene-benefit-evidence | narrative |
| vitamin-e-benefit-evidence | adults-in-nutrient-benefit-evidence | no benefit for preventing cardiovascular disease or cancer | Adequate evidence that supplementation with vitamin E provides no benefit in preventing cardiovascular disease or cancer. | uspstf-2022 | p2 | p2/narrative/vitamin-e-benefit-evidence | narrative |
| multivitamin-benefit-limitations | community-adults-multivitamins | no effect for most outcomes; cancer-incidence and mortality effects were not concordant, limiting certainty about benefit | RENDERED: multivitamin supplementation was not associated with an effect for most outcomes, and the effects on cancer incidence and mortality were not concordant. | uspstf-2022 | p5 | p5/narrative/multivitamin-benefit-limitations | narrative |
| vitamin-d-pooled-outcome-evidence | adults-in-nutrient-benefit-evidence | pooled analyses found no differences in cardiovascular-disease mortality or events, myocardial infarction, stroke, cancer mortality, or cancer incidence | RENDERED: Pooled analyses showed no between-group differences for cardiovascular disease mortality, the composite outcome of any cardiovascular disease event, or myocardial infarction or stroke. Pooled analyses also showed that vitamin D supplementation was not associated with any difference in cancer mortality or cancer incidence compared with placebo. | uspstf-2022 | p5 | p5/narrative/vitamin-d-pooled-outcome-evidence | narrative |
| vitamin-d-effect-heterogeneity | adults-in-nutrient-benefit-evidence | effects may vary by baseline vitamin D level, diet quality, or another unidentified factor | RENDERED: It is unclear whether the effect of vitamin D on health outcomes might vary based on patient population characteristics (eg, baseline vitamin D level or diet quality) or an unidentified factor. | uspstf-2022 | p5 | p5/narrative/vitamin-d-effect-heterogeneity | narrative |
| calcium-benefit-evidence | adults-in-nutrient-benefit-evidence | pooled analyses found no difference in all-cause mortality, cardiovascular-disease events or mortality, or cancer incidence | RENDERED: Pooled analyses found no difference in all-cause mortality, cardiovascular disease events, cardiovascular disease mortality, or any incidence of cancer in persons taking calcium | uspstf-2022 | p5 | p5/narrative/calcium-benefit-evidence | narrative |
| nonpregnant-folic-acid-mortality-cvd-evidence | adults-in-nutrient-benefit-evidence | no association with all-cause mortality; cardiovascular-disease mortality and event rates were too low for conclusions | RENDERED: A pooled analysis showed no association between folic acid supplementation and all-cause mortality over 2 to 6.5 years. Event rates for cardiovascular disease mortality and cardiovascular disease events were too low to draw conclusions. | uspstf-2022 | p5 | p5/narrative/nonpregnant-folic-acid-mortality-cvd-evidence | narrative |
| nonpregnant-folic-acid-cancer-evidence | adults-in-nutrient-benefit-evidence | pooled evidence found higher cancer incidence, but limited populations made generalizability to the general population uncertain | RENDERED: In a pooled analysis, folic acid either alone or with vitamin B12 was associated with higher rates of any cancer incidence at 2 to 6 years of follow-up. However, 1 trial was limited to adults with moderately elevated homocysteine levels, and the others were limited to adults with a history of colorectal adenomas. Thus, the generalizability of this finding to the general population is uncertain. | uspstf-2022 | p5 | p5/narrative/nonpregnant-folic-acid-cancer-evidence | narrative |
| vitamin-c-benefit-evidence | adults-in-nutrient-benefit-evidence | evidence suggested no effect on all-cause mortality, cardiovascular outcomes, or cancer incidence or mortality | RENDERED: Two RCTs suggested that vitamin C supplementation has no effect on all-cause mortality, cardiovascular disease events, or cardiovascular disease mortality. One trial suggested that vitamin C supplementation has no effect on cancer incidence or mortality. | uspstf-2022 | p5 | p5/narrative/vitamin-c-benefit-evidence | narrative |
| vitamin-b3-b6-benefit-evidence | adults-in-nutrient-benefit-evidence | evidence insufficient for all-cause mortality, cardiovascular outcomes, or cancer outcomes | The USPSTF found insufficient evidence to assess the effects of these vitamins on all-cause mortality, cardiovascular disease outcomes, or cancer outcomes. | uspstf-2022 | p5 | p5/narrative/vitamin-b3-b6-benefit-evidence | narrative |
| selenium-benefit-evidence | adults-in-nutrient-benefit-evidence | limited evidence suggests no effect on all-cause mortality, cardiovascular outcomes, or cancer mortality despite conflicting individual studies | RENDERED: Although some individual studies showed conflicting results, the limited overall evidence suggests that selenium supplementation has no effect on all-cause mortality, cardiovascular disease mortality, cardiovascular disease events, or cancer mortality. | uspstf-2022 | p5 | p5/narrative/selenium-benefit-evidence | narrative |
| beta-carotene-harm-trial-doses | adults-in-beta-carotene-harm-trials | study-associated serious-harm doses: beta carotene 30 mg/day and 20 mg/day; one trial also used vitamin A 25 000 IU/day | RENDERED: increased cardiovascular disease mortality and increased risk of lung cancer in persons who smoke or had workplace asbestos exposure, associated with beta carotene supplementation at doses of 30 and 20 mg/d. One of these trials also co-administered vitamin A at a dose of 25 000 IU/d | uspstf-2022 | p5 | p5/narrative/beta-carotene-harm-trial-doses | narrative |
| beta-carotene-skin-discoloration | adults-in-beta-carotene-harm-trials | orange skin discoloration was a minor harm | RENDERED: A minor harm of beta carotene was orange discoloration of the skin. | uspstf-2022 | p5 | p5/narrative/beta-carotene-skin-discoloration | narrative |
| vitamin-a-hip-fracture-evidence | women-in-vitamin-a-cohorts | two cohort studies showed a statistically nonsignificant increased hip-fracture risk | RENDERED: Two cohort studies in women showed a statistically nonsignificant increased risk of hip fracture associated with vitamin A supplementation. | uspstf-2022 | p6 | p6/narrative/vitamin-a-hip-fracture-evidence | narrative |
| vitamin-e-hemorrhagic-stroke-doses | adults-in-vitamin-e-harm-trials | study-associated hemorrhagic-stroke doses: 111 IU daily and 200 IU daily | RENDERED: Two trials showed an increased risk of hemorrhagic stroke associated with vitamin E supplementation at doses of 111 and 200 IU daily | uspstf-2022 | p6 | p6/narrative/vitamin-e-hemorrhagic-stroke-doses | narrative |
| vitamin-b6-hip-fracture-intake | women-in-vitamin-b6-cohort | high intake at least 35 mg/day was associated with increased hip-fracture risk compared with low intake below 2 mg/day | RENDERED: a high intake of vitamin B6 (≥35 mg/d) was associated with an increased risk of hip fracture compared with a low intake (<2 mg/d). | uspstf-2022 | p6 | p6/narrative/vitamin-b6-hip-fracture-intake | narrative |
| vitamin-d-kidney-stone-dose | persons-taking-vitamin-d | cohort-study kidney-stone association only at 1000 IU/day or more | RENDERED: In the cohort studies, this risk was only associated with vitamin D doses of 1000 IU/d or more. | uspstf-2022 | p6 | p6/narrative/vitamin-d-kidney-stone-dose | narrative |
| vitamin-c-kidney-stone-evidence | men-taking-vitamin-c | two cohort studies suggested an association with kidney stones | Two cohort studies in men suggest an association between vitamin C supplementation and kidney stones. | uspstf-2022 | p6 | p6/narrative/vitamin-c-kidney-stone-evidence | narrative |
| calcium-kidney-stone-evidence | adults-in-nutrient-benefit-evidence | evidence of an association with kidney stones was mixed | RENDERED: The evidence on an association between calcium use and kidney stones was mixed. | uspstf-2022 | p6 | p6/narrative/calcium-kidney-stone-evidence | narrative |
| population-effect-heterogeneity | community-dwelling-nonpregnant-adults | uncertain whether effects differ by population, baseline nutrient level, or socioeconomic factors such as food insecurity | RENDERED: It is uncertain whether there might be heterogeneity across populations or by baseline nutrient level, or by socioeconomic factors such as food insecurity, in the effects of vitamin, mineral, and multivitamin supplementation on cardiovascular disease and cancer outcomes. | uspstf-2022 | p3 | p3/narrative/population-effect-heterogeneity | narrative |
| illness-management-boundary | persons-with-acute-or-chronic-illness | acute or chronic illness may require supplementation as disease management, which is outside prevention scope | Persons who have an acute or chronic illness may require additional vitamin, mineral, or multivitamin supplementation as part of management of their condition, which goes beyond supplementation for the prevention purposes addressed by this recommendation. | uspstf-2022 | p6 | p6/narrative/illness-management-boundary | narrative |
| related-uspstf-cross-guidance | people-addressed-by-related-uspstf-guidance | RELATED USPSTF: separate guidance addresses smoking cessation, hypertension screening, statins, aspirin, obesity-related behavioral interventions, breast-cancer risk-reducing medication, skin-cancer counseling, breast/cervical/colorectal/lung/prostate cancer screening, BRCA-related assessment and counseling/testing, fracture supplementation, falls prevention, and folic acid for neural-tube-defect prevention | RENDERED: The USPSTF has published several recommendations for prevention of cardiovascular disease and cancer, including recommendations for smoking cessation, screening for hypertension, statin use to prevent cardiovascular disease, aspirin use to prevent cardiovascular disease, interventions to prevent obesity-related morbidity and mortality, behavioral counseling to prevent cardiovascular disease in adults with risk factors, medication use to reduce breast cancer risk, behavioral counseling to decrease risk of skin cancer, screening for breast, cervical, colorectal, lung, and prostate cancer, and risk assessment, genetic counseling, and genetic testing for BRCA-related cancer. The USPSTF has also published several recommendations related to vitamin and mineral supplementation, including vitamin D, calcium, or combined supplementation to prevent fractures in adults, vitamin D supplementation to prevent falls in community-dwelling older adults, and folic acid to prevent neural tube defects in persons who are planning or capable of pregnancy. | uspstf-2022 | p4 | p4/narrative/related-uspstf-cross-guidance | narrative |
| food-first-dietary-guidance | general-population-nutritional-needs | EXTERNAL (US Department of Health and Human Services 2020-2025 dietary guidelines): meet nutritional needs primarily through nutrient-dense foods and beverages | RENDERED: The US Department of Health and Human Services 2020-2025 dietary guidelines suggest that nutritional needs should be met primarily from foods and beverages—specifically, nutrient-dense foods and beverages. | uspstf-2022 | p6 | p6/narrative/food-first-dietary-guidance | narrative |
| aha-nutrient-guidance | healthy-persons | EXTERNAL (American Heart Association): receive adequate nutrients by eating varied foods in moderation rather than taking supplements | The American Heart Association recommends that healthy persons receive adequate nutrients by eating a variety of foods in moderation, rather than by taking supplements. | uspstf-2022 | p6 | p6/narrative/aha-nutrient-guidance | narrative |

## Conflicts

No unresolved same-population, same-quantity conflict was identified. The Grade D
recommendation against beta carotene and vitamin E and the two I statements concern
different supplement categories, so they are not competing values for one quantity.
The p. 2 benefit-harm assessments explain rather than compete with those recommendation
grades. The separate related USPSTF folic-acid recommendation applies to pregnancy
planning/capability and serves a different preventive purpose. Evidence-associated harm
doses are observations from specific trials or cohorts, not recommended dosing thresholds.
The grouped p. 4 related USPSTF rows and the source-attributed federal and American Heart
Association food guidance are provenance-labeled cross-guidance, not recommendations
issued by this statement.

## Coverage

Exact recommendation accounting: **3 = 3 cited + 0 scoped out**.

ADR 0009 disposition:

- retained all three exact recommendation records, their p. 2 benefit-harm rationale,
  the community-dwelling nonpregnant adult applicability, the narrower evidence-review
  population, every stated exclusion, and the clinical-judgment instruction attached
  to the I statements;
- retained beta carotene's lung-cancer harm in smokers or asbestos-exposed persons,
  the source's harm-magnitude assessments, excessive-dose cautions, nutrient-specific
  adverse effects including the nonsignificant vitamin A hip-fracture finding, and every
  dose or intake boundary tied by the source to a reported harm;
- retained benefit-evidence conclusions for beta carotene, vitamin E, multivitamins,
  vitamin D, calcium, folic acid in nonpregnant adults, vitamin C, vitamins B3 and B6,
  and selenium where they inform the recommendation or its uncertainty;
- retained the separate related USPSTF pregnancy-capable folic-acid recommendation,
  grouped related USPSTF prevention guidance, the acute/chronic-illness management
  boundary, population-effect uncertainty, and source-attributed federal and American
  Heart Association food-first guidance;
- excluded epidemiologic counts, isolated study sizes, effect estimates, confidence
  intervals, publication dates, comment dates, author/disclosure material, and trial
  follow-up durations that do not change supplement selection, applicability, harm
  interpretation, or an evidence boundary.
