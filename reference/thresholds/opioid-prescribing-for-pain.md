# Opioid prescribing for pain — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source below. **Not a substitute for the
guideline** and not a clinical instruction: every row is a fact this repo restates,
and choosing among them is the clinician's.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cdc-2022 | CDC | CDC/CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR | guideline | 2022 | 2022-11-04 | https://www.cdc.gov/mmwr/volumes/71/rr/rr7103a1.htm | chosen | nothing-found |

## Scope

**Read:** all 43 source pages, including the introduction, applicability, methods,
all 12 recommendation sections and implementation considerations, special populations,
tables, boxes, article information, disclosures, and references. The recommendation
extractor found no bound markers; the 12 recommendation actions are therefore retained
from the page text without pretending the empty JSON is a negative clinical finding.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| introduction, background, applicability, and definitions | 1-3 | yes |
| methods and evidence framework | 4-6 | read 2026-09-01; blind 2026-09-01 |
| initiating opioids and nonopioid care | 7-12 | yes |
| opioid formulation, dosage, and tapering | 12-17 | yes |
| acute duration and follow-up | 17-20 | yes |
| risk mitigation, special populations, PDMP, and toxicology | 20-25 | yes |
| concurrent depressants, opioid use disorder, and conclusion | 25-28 | yes |
| article information and disclosures | 29 | read 2026-09-01; blind 2026-09-01 |
| references | 30-39 | exempt: reference list has no patient-action prose |
| summary boxes, MME table, and implementation principles | 40-42 | yes |
| research priorities, citation, and disclaimer | 43 | read 2026-09-01; blind 2026-09-01 |

citations resolved against C:/codeing/guidelines-src on 2026-09-01

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| guideline-adults | outpatients aged >=18 years with acute, subacute, or chronic pain |
| excluded-pain-care | pain related to sickle cell disease or cancer or patients receiving palliative or end-of-life care |
| acute-pain-adults | outpatients aged >=18 years with acute pain lasting <1 month |
| subacute-chronic-adults | outpatients aged >=18 years with subacute pain lasting 1-3 months or chronic pain lasting >3 months |
| opioid-naive-adults | opioid-naive patients with acute, subacute, or chronic pain |
| adults-already-opioids | patients already receiving opioid therapy |
| acute-continuous-over-few-days | patients taking opioids around the clock for more than a few days for acute pain |
| acute-continuous-over3-under7 | patients taking opioids continuously for >3 days but <1 week |
| acute-continuous-1week-under1month | patients taking opioids continuously for >=1 week but <1 month |
| long-term-at-least-year | patients taking opioids for longer durations, for example >=1 year |
| shorter-weeks-months | patients taking opioids for weeks to months rather than years |
| acute-opioid-continuation | patients who continue to receive opioids for acute pain |
| subacute-after30days | patients with subacute pain treated with opioid therapy for 30 days |
| long-term-opioid-patients | patients receiving long-term opioid therapy |
| higher-risk-opioid-patients | patients at higher risk for opioid use disorder or overdose |
| increased-overdose-risk | patients with overdose history, substance use disorder, sleep-disordered breathing, >=50 MME/day, concurrent benzodiazepines, or lost tolerance |
| mild-sleep-disordered | patients with mild sleep-disordered breathing |
| moderate-severe-sleep-disordered | patients with moderate or severe sleep-disordered breathing |
| pregnant-pain | pregnant persons with pain |
| reproductive-potential | persons who can become pregnant before long-term opioid therapy |
| pregnant-oud | pregnant persons with opioid use disorder |
| opioid-exposed-infants | infants with long-term opioid exposure |
| renal-hepatic | patients with renal or hepatic insufficiency |
| mme-calculation-users | clinicians calculating morphine milligram equivalents for opioid pain medication |
| tapentadol-tramadol-users | patients receiving tapentadol or tramadol for pain |
| older-adults | patients aged >=65 years |
| safety-critical-workers | patients receiving impairing medication whose jobs involve hazardous tasks |
| initial-or-chronic-opioid | patients receiving an initial opioid prescription or chronic opioid therapy |
| subacute-chronic-opioid | patients prescribed opioids for subacute or chronic pain |
| unexpected-toxicology | patients with unexplained unexpected toxicology results |
| repeatedly-negative-prescribed | patients with repeatedly negative prescribed-opioid tests, including confirmation, verified not taking the opioid |
| concurrent-benzo-cns | patients receiving opioid pain medication with benzodiazepines or other central nervous system depressants |
| diagnosed-oud | patients meeting criteria for opioid use disorder |
| moderate-severe-oud | patients meeting moderate or severe opioid use disorder criteria |
| breastfeeding-oud | persons receiving buprenorphine or methadone for opioid use disorder and considering breastfeeding |
| full-agonist-transition | patients transitioning from full-agonist opioids to buprenorphine |
| naltrexone-initiation | patients starting naltrexone for opioid use disorder |
| pediatric-pain | patients younger than 18 years with pain |
| erla-eligible | patients with severe continuous pain for whom an ER/LA opioid is being considered |
| opioid-tolerant-example | patients who received specified immediate-release opioid dosages daily for at least 1 week |
| inpatient-or-possible-admission | patients hospitalized or in an emergency department or observation setting from which they might be admitted |
| discharge-prescribing | patients prescribed pain medication when discharged from a hospital, emergency department, or other facility |
| all-opioid-patients | all patients before starting and during continuation of opioid therapy |
| unable-taper-high-risk | patients unable to taper who continue a high-dose or otherwise high-risk opioid regimen |
| pain-buprenorphine-transition | patients taking full-agonist opioids for acute or chronic pain who are transitioning to buprenorphine |
| buprenorphine-prescribers | clinicians prescribing buprenorphine for chronic pain or opioid use disorder under the source-era regulatory framework |

## Quantities

| key | verbatim |
| --- | --- |
| applicability-age | outpatient age boundary |
| pain-duration-classification | acute, subacute, and chronic duration boundaries |
| initial-acute-treatment | nonopioid-first acute treatment decision |
| initial-subacute-chronic-treatment | nonopioid-first subacute or chronic treatment decision |
| opioid-formulation | immediate-release versus ER/LA initiation |
| erla-reservation | ER/LA severe-continuous-pain boundary |
| erla-tolerance-example | source examples of opioid tolerance before selected ER/LA products |
| initial-opioid-dose | lowest effective dose |
| dosage-general-caution | caution and benefit-risk evaluation at any opioid dosage |
| dosage-pause | MME guidepost for reassessment before escalation |
| dosage-precautions | MME guidepost for added precautions |
| dose-response-risk | observational overdose-risk bands |
| ongoing-opioid-decision | continue versus taper decision |
| abrupt-discontinuation | life-threatening exception to no abrupt or rapid reduction |
| long-term-taper-rate | taper rate after at least 1 year |
| shorter-taper-rate | taper rate after weeks to months |
| taper-followup | follow-up cadence during taper |
| acute-duration | initial acute opioid quantity and duration |
| acute-followup | acute opioid reevaluation cadence |
| subacute-transition | reassessment threshold before unintended long-term therapy |
| acute-brief-taper | brief taper after continuous acute use |
| acute-taper-over3-under7 | acute taper example after >3 days but <1 week |
| acute-taper-1week-under1month | acute taper example after >=1 week but <1 month |
| chronic-start-followup | follow-up after starting or escalating |
| methadone-start-followup | early methadone follow-up cadence |
| long-term-followup | ongoing reevaluation cadence |
| high-risk-followup | increased follow-up cadence |
| meaningful-improvement | pain and function improvement benchmark |
| naloxone-offer | overdose-risk mitigation threshold |
| opioid-risk-evaluation | risk evaluation, discussion, and mitigation plan before and during opioid therapy |
| sleep-breathing-action | opioid action by sleep-disordered-breathing severity |
| pregnancy-pain-action | pregnancy pain and taper decision |
| infant-observation | neonatal withdrawal observation duration |
| renal-hepatic-action | clearance-based monitoring and interval action |
| erla-renal-hepatic-interval | ER/LA dosing interval in renal or hepatic dysfunction |
| pregnancy-initiation | pregnancy opioid initiation decision |
| pregnancy-acute-dose | acute opioid dose and duration during pregnancy |
| pregnancy-taper | pregnancy opioid taper expertise |
| older-adult-action | age-specific monitoring and prevention action |
| hazardous-work-assessment | safety-critical task assessment |
| pdmp-frequency | PDMP review schedule |
| toxicology-frequency | toxicology consideration schedule |
| toxicology-confirmation | confirmation conditions |
| negative-test-action | discontinuation action after verified nonuse |
| concurrent-depressants | benzodiazepine and CNS-depressant prescribing action |
| benzodiazepine-taper | benzodiazepine discontinuation action |
| oud-diagnosis | DSM-5 diagnostic and severity counts |
| oud-treatment | medication treatment versus detoxification alone |
| pregnancy-oud-treatment | pregnancy OUD medication timing |
| breastfeeding-return-use | breastfeeding action by return-to-use window |
| buprenorphine-transition | withdrawal and waiting interval before standard initiation |
| buprenorphine-low-dose-initiation | low-dose initiation while continuing full agonists |
| buprenorphine-overdose-boundary | comparative overdose-risk boundary and respiratory-depressant exception |
| buprenorphine-waiver-boundary | source-era waiver distinction between pain and OUD prescribing |
| high-risk-continuation-safeguard | monitoring and naloxone when high-risk taper is not possible |
| oud-dose-duration-boundary | pain guidepost inapplicability, OUD treatment duration, and discontinuation risk |
| buprenorphine-oud-taper | taper cadence if OUD buprenorphine is discontinued |
| buprenorphine-pain-frequency | analgesic dosing frequency distinction |
| naltrexone-opioid-free | opioid-free interval before naltrexone |
| naltrexone-dose | injectable naltrexone dose and schedule |
| emergency-oud-administration | emergency methadone or buprenorphine administration limit |
| mme-conversion-factor | source Table conversion factors |
| mme-conversion-use | MME calculation and opioid-conversion safeguards |
| mme-special-cautions | methadone and transdermal fentanyl MME cautions |
| mme-exclusions | buprenorphine and OUD exclusions from Table conversion factors |
| mme-atypical-overdose-relationship | tapentadol and tramadol dose-dependent overdose uncertainty |
| pediatric-boundary | source noncoverage for younger patients |
| setting-applicability | hospital, emergency, observation, and discharge setting boundary |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| applicability-age | guideline-adults | >=18 years | outpatients aged ≥18 years | cdc-2022 | 1 | p1/narrative/applicability | narrative |
| setting-applicability | inpatient-or-possible-admission | recommendations do not apply to inpatient care or emergency or observation care from which admission might occur | RENDERED: The recommendations do not apply to providing care to patients who are hospitalized or in an emergency department or other observational setting from which they might be admitted to inpatient care | cdc-2022 | 40 | p40/box/applicability-settings | box |
| setting-applicability | discharge-prescribing | recommendations apply to prescribing for pain management at discharge | RENDERED: These recommendations do apply to prescribing for pain management when patients are discharged from hospitals, emergency departments, or other facilities | cdc-2022 | 40 | p40/box/discharge-prescribing | box |
| pediatric-boundary | pediatric-pain | not addressed; evidence and labeling data are limited | RENDERED: This clinical practice guideline does not address the use of opioid pain medication in children and adolescents aged <18 years | cdc-2022 | 3 | p3/narrative/pediatric-scope | narrative |
| pain-duration-classification | acute-pain-adults | <1 month | Acute pain is usually sudden in onset and time limited (defined in this clinical practice guideline as having a duration of <1 month) | cdc-2022 | 1 | p1/narrative/acute-definition | narrative |
| pain-duration-classification | subacute-chronic-adults | subacute 1-3 months; chronic >3 months | subacute pain (defined in this clinical practice guideline as pain that has been present for 1-3 months) can evolve into chronic pain (4). Chronic pain typically lasts >3 months | cdc-2022 | 1 | p1/narrative/pain-definitions | narrative |
| initial-acute-treatment | acute-pain-adults | maximize nonpharmacologic and nonopioid therapy; consider opioids only when anticipated benefits outweigh risks and discuss realistic benefits and known risks | Nonopioid therapies are at least as effective as opioids for many common types of acute pain | cdc-2022 | 7 | p7/narrative/recommendation-1 | narrative |
| initial-subacute-chronic-treatment | subacute-chronic-adults | prefer and maximize nonopioid therapies; initiate opioids only when expected pain-and-function benefits outweigh risk; set goals and a discontinuation plan | Nonopioid therapies are preferred for subacute and chronic pain | cdc-2022 | 9 | p9/narrative/recommendation-2 | narrative |
| opioid-formulation | guideline-adults | start immediate-release instead of ER/LA opioids | clinicians should prescribe immediate-release opioids instead of extended-release and long-acting (ER/LA) opioids | cdc-2022 | 12 | p12/narrative/recommendation-3 | narrative |
| erla-reservation | erla-eligible | reserve for severe, continuous pain; do not use for acute pain or intermittent/as-needed use | ER/LA opioids should be reserved for severe, continuous pain | cdc-2022 | 12 | p12/narrative/erla-reservation | narrative |
| erla-tolerance-example | opioid-tolerant-example | oral morphine 60 mg/day or oxycodone 30 mg/day, or equianalgesic dose, for >=1 week | RENDERED: 60 mg daily of oral morphine, 30 mg daily of oral oxycodone, or equianalgesic dosages of other opioids for at least 1 week | cdc-2022 | 13 | p13/narrative/opioid-tolerant-example | narrative |
| initial-opioid-dose | opioid-naive-adults | prescribe the lowest effective dosage | clinicians should prescribe the lowest effective dosage | cdc-2022 | 13 | p13/narrative/recommendation-4 | narrative |
| dosage-general-caution | subacute-chronic-adults | use caution at any dosage, carefully evaluate individual benefits and risks before increasing, and avoid increases likely to yield diminishing returns in benefits relative to risks | RENDERED: clinicians should use caution when prescribing opioids at any dosage, should carefully evaluate individual benefits and risks when considering increasing dosage, and should avoid increasing dosage above levels likely to yield diminishing returns in benefits relative to risks to patients | cdc-2022 | 14 | p14/narrative/recommendation-4-complete | narrative |
| dosage-pause | subacute-chronic-adults | before increasing to >=50 MME/day, pause and carefully reassess benefits and risks | before increasing total opioid dosage to ≥50 MME/day, clinicians should pause and carefully reassess evidence of individual benefits and risks | cdc-2022 | 14 | p14/narrative/50-mme-pause | narrative |
| dosage-precautions | subacute-chronic-adults | at >=50 MME/day, increase follow-up and offer naloxone with household education | RENDERED: If a patient's opioid dosage for all sources of opioids reaches or exceeds 50 MME/day, clinicians should implement additional precautions, including increased frequency of follow-up, and offer naloxone and overdose prevention education to both the patient and the patient's household members | cdc-2022 | 14 | p14/narrative/50-mme-precautions | narrative |
| dose-response-risk | subacute-chronic-adults | 50 to <100 MME/day: 1.9-4.6 times overdose risk; >=100 MME/day: 2.0-8.9 times risk versus 1 to <20 MME/day | RENDERED: dosages of 50 to <100 MME/day ... 1.9-4.6 times ... dosages of ≥100 MME/day ... 2.0-8.9 times ... 1 to <20 MME/day | cdc-2022 | 14 | p14/narrative/observational-overdose-risk | narrative |
| ongoing-opioid-decision | adults-already-opioids | continue and optimize nonopioid care when benefits outweigh risks; otherwise optimize alternatives and collaboratively taper lower or discontinue | RENDERED: If benefits outweigh risks of continued opioid therapy, clinicians should work closely with patients to optimize nonopioid therapies while continuing opioid therapy. If benefits do not outweigh risks of continued opioid therapy, clinicians should optimize other therapies and work closely with patients to gradually taper to lower dosages or, if warranted based on the individual circumstances of the patient, appropriately taper and discontinue opioids | cdc-2022 | 15 | p15/narrative/recommendation-5 | narrative |
| abrupt-discontinuation | adults-already-opioids | do not abruptly discontinue or rapidly reduce unless a life-threatening issue has warning signs such as confusion, sedation, or slurred speech | RENDERED: Unless there are indications of a life-threatening issue such as warning signs of impending overdose (e.g., confusion, sedation, or slurred speech), opioid therapy should not be discontinued abruptly, and clinicians should not rapidly reduce opioid dosages from higher dosages | cdc-2022 | 15 | p15/narrative/abrupt-discontinuation | narrative |
| taper-followup | adults-already-opioids | follow frequently, at least monthly | clinicians should follow up frequently (at least monthly) with patients engaging in opioid tapering | cdc-2022 | 16 | p16/narrative/taper-followup | narrative |
| long-term-taper-rate | long-term-at-least-year | approximately 10% per month or slower | Tapers of approximately 10% per month or slower are likely to be better tolerated than more rapid tapers when patients have been taking opioids for longer durations (e.g., ≥1 year) | cdc-2022 | 17 | p17/narrative/long-term-taper-rate | narrative |
| shorter-taper-rate | shorter-weeks-months | reduce 10% of original dose per week or slower until about 30%, then about 10% of remaining dose weekly | When patients have taken opioids for shorter durations (e.g., weeks to months rather than years), a decrease of 10% of the original dose per week or slower (until approximately 30% of the original dose is reached, followed by a weekly decrease of approximately 10% of the remaining dose) is less likely to trigger withdrawal | cdc-2022 | 17 | p17/narrative/shorter-taper-rate | narrative |
| acute-duration | acute-pain-adults | no greater quantity than needed for expected duration of severe-enough pain; many common nonsurgical causes need a few days or less | clinicians should prescribe no greater quantity than needed for the expected duration of pain severe enough to require opioids | cdc-2022 | 17 | p17/narrative/recommendation-6 | narrative |
| acute-followup | acute-opioid-continuation | evaluate at least every 2 weeks | Patients should be evaluated at least every 2 weeks if they continue to receive opioids for acute pain | cdc-2022 | 18 | p18/narrative/acute-followup | narrative |
| subacute-transition | subacute-after30days | at >=1 month, address reversible causes and make continuation an intentional long-term decision under subacute/chronic recommendations | If opioids are continued for ≥1 month, clinicians should ensure that potentially reversible causes of chronic pain are addressed | cdc-2022 | 18 | p18/narrative/one-month-transition | narrative |
| acute-brief-taper | acute-continuous-over-few-days | prescribe a brief taper | If opioids are used continuously (around the clock) for more than a few days for acute pain, clinicians should prescribe a brief taper | cdc-2022 | 18 | p18/narrative/brief-taper | narrative |
| acute-taper-over3-under7 | acute-continuous-over3-under7 | consider reducing daily dosage to 50% for 2 days | RENDERED: used continuously for >3 days but for <1 week ... reducing the daily dosage to 50% for 2 days | cdc-2022 | 18 | p18/narrative/acute-taper-short | narrative |
| acute-taper-1week-under1month | acute-continuous-1week-under1month | consider reducing daily dosage about 20% every 2 days | RENDERED: continuously for ≥1 week but <1 month ... reducing the daily dosage by approximately 20% every 2 days | cdc-2022 | 18 | p18/narrative/acute-taper-longer | narrative |
| chronic-start-followup | subacute-chronic-adults | evaluate within 1-4 weeks after starting or escalating | Clinicians should evaluate benefits and risks with patients within 1-4 weeks of starting opioid therapy | cdc-2022 | 19 | p19/narrative/recommendation-7 | narrative |
| methadone-start-followup | subacute-chronic-adults | every 2-3 days during the first week after starting or increasing methadone | Shorter follow-up intervals (every 2-3 days for the first week) should be strongly considered | cdc-2022 | 19 | p19/narrative/methadone-followup | narrative |
| long-term-followup | long-term-opioid-patients | every 3 months or more frequently | with a suggested interval of every 3 months or more frequently for most patients | cdc-2022 | 19 | p19/narrative/long-term-followup | narrative |
| high-risk-followup | higher-risk-opioid-patients | more often than every 3 months | RENDERED: Clinicians should reevaluate patients who are at higher risk for opioid use disorder or overdose more frequently than every 3 months | cdc-2022 | 19 | p19/narrative/high-risk-followup | narrative |
| meaningful-improvement | long-term-opioid-patients | 30% improvement in pain and function scores | clinically meaningful improvement has been defined as a 30% improvement in scores for both pain and function | cdc-2022 | 20 | p20/narrative/meaningful-improvement | narrative |
| naloxone-offer | increased-overdose-risk | offer naloxone, provide overdose-prevention education, and offer household education | Clinicians should offer naloxone when prescribing opioids, particularly to patients at increased risk for overdose | cdc-2022 | 20 | p20/narrative/naloxone-risk | narrative |
| opioid-risk-evaluation | all-opioid-patients | before starting and periodically during continuation, evaluate opioid-related-harm risk, discuss risk, and incorporate mitigation strategies including offering naloxone into the management plan | RENDERED: Before starting and periodically during continuation of opioid therapy, clinicians should evaluate risk for opioid-related harms and discuss risk with patients. Clinicians should work with patients to incorporate into the management plan strategies to mitigate risk, including offering naloxone | cdc-2022 | 40 | p40/box/recommendation-8 | box |
| sleep-breathing-action | mild-sleep-disordered | careful monitoring and cautious dose titration | Careful monitoring and cautious dose titration should be used if opioids are prescribed for patients with mild sleep-disordered breathing | cdc-2022 | 21 | p21/narrative/mild-sleep-apnea | narrative |
| sleep-breathing-action | moderate-severe-sleep-disordered | avoid opioids when possible | Clinicians should avoid prescribing opioids to patients with moderate or severe sleep-disordered breathing | cdc-2022 | 21 | p21/narrative/moderate-severe-sleep-apnea | narrative |
| pregnancy-initiation | pregnant-pain | carefully weigh benefits and risks together before initiating opioids | Clinicians and patients together should carefully weigh benefits and risks when making decisions about whether to initiate opioid therapy for pain during pregnancy | cdc-2022 | 21 | p21/narrative/pregnancy-initiation | narrative |
| pregnancy-acute-dose | pregnant-pain | use the lowest effective acute dose for no longer than severe pain requires | RENDERED: When opioids are needed for treatment of acute pain in pregnant persons, the lowest effective dose should be used for no longer than the expected duration of pain severe enough to require opioids | cdc-2022 | 21 | p21/narrative/pregnancy-acute-dose | narrative |
| pregnancy-taper | pregnant-pain | obtain appropriate expertise before considering a taper | For pregnant persons already receiving opioids, clinicians should access appropriate expertise if considering tapering opioids | cdc-2022 | 21 | p21/narrative/pregnancy-taper | narrative |
| infant-observation | opioid-exposed-infants | observe >=72 hours; 4-7 days after buprenorphine or ER/LA exposure; 5-7 days after methadone | RENDERED: observed for at least 72 hours (4-7 days if exposed to buprenorphine or ER/LA opioids and 5-7 days if exposed to methadone) | cdc-2022 | 21 | p21/narrative/infant-observation | narrative |
| renal-hepatic-action | renal-hepatic | use additional caution and increased monitoring | RENDERED: Clinicians should use additional caution and increased monitoring to minimize risks of opioids prescribed for patients with renal or hepatic insufficiency | cdc-2022 | 21 | p21/narrative/renal-hepatic | narrative |
| erla-renal-hepatic-interval | renal-hepatic | consider a longer ER/LA dosing interval | Clinicians should use additional caution with ER/LA opioids and consider a longer dosing interval when prescribing to patients with renal or hepatic dysfunction | cdc-2022 | 13 | p13/narrative/renal-hepatic-interval | narrative |
| older-adult-action | older-adults | additional caution and monitoring; bowel regimen, fall-risk assessment, and cognitive monitoring | RENDERED: Clinicians should use additional caution and increased monitoring to minimize risks of opioids prescribed for patients aged ≥65 years. Clinicians should implement interventions to mitigate common risks of opioid therapy among older adults, such as exercise or bowel regimens to prevent constipation, risk assessment for falls, and patient monitoring for cognitive impairment | cdc-2022 | 20 | p20/narrative/older-adult-action | narrative |
| hazardous-work-assessment | safety-critical-workers | assess ability to perform hazardous tasks safely | clinicians should assess patients' abilities to safely perform the potentially hazardous tasks | cdc-2022 | 20 | p20/narrative/hazardous-work | narrative |
| pdmp-frequency | initial-or-chronic-opioid | ideally before every opioid prescription; at minimum before initial long-term prescription and every 3 months or more frequently | RENDERED: Ideally, PDMP data should be reviewed before every opioid prescription ... At a minimum ... every 3 months or more frequently | cdc-2022 | 22 | p22/narrative/pdmp-frequency | narrative |
| toxicology-frequency | subacute-chronic-opioid | consider before starting and periodically, at least annually | Before starting opioids and periodically (at least annually) during opioid therapy | cdc-2022 | 23 | p23/narrative/toxicology-frequency | narrative |
| toxicology-confirmation | unexpected-toxicology | confirm when results have major implications, a specific unassayed drug is needed, or an unexpected screen is unexplained | confirm unexpected toxicology screening results for which there is no other explanation | cdc-2022 | 24 | p24/narrative/toxicology-confirmation | narrative |
| negative-test-action | repeatedly-negative-prescribed | discontinue prescription without taper and discuss safe disposal | clinicians can discontinue the prescription without a taper and discuss options for safe disposal | cdc-2022 | 25 | p25/narrative/verified-nonuse | narrative |
| concurrent-depressants | concurrent-benzo-cns | use particular caution; consider whether benefits outweigh risks; do not withhold OUD buprenorphine or methadone solely because of CNS depressants | Clinicians should use particular caution when prescribing opioid pain medication and benzodiazepines concurrently | cdc-2022 | 25 | p25/narrative/recommendation-11 | narrative |
| benzodiazepine-taper | concurrent-benzo-cns | taper benzodiazepines gradually at an individualized rate | Clinicians should taper benzodiazepines gradually before discontinuation | cdc-2022 | 25 | p25/narrative/benzodiazepine-taper | narrative |
| oud-diagnosis | diagnosed-oud | DSM-5 >=2 criteria; mild 2-3, moderate 4-5, severe >=6 | RENDERED: Opioid use disorder is defined in DSM-5 as ... at least 2 ... mild (2-3), moderate (4-5), or severe (6 or more) | cdc-2022 | 26 | p26/narrative/dsm5-severity | narrative |
| oud-treatment | diagnosed-oud | offer or arrange evidence-based medication; do not use detoxification alone | Detoxification on its own, without medications for opioid use disorder, is not recommended | cdc-2022 | 25 | p25/narrative/recommendation-12 | narrative |
| pregnancy-oud-treatment | pregnant-oud | offer buprenorphine or methadone as early as possible in pregnancy | should be offered as early as possible in pregnancy | cdc-2022 | 27 | p27/narrative/pregnancy-oud | narrative |
| breastfeeding-return-use | breastfeeding-oud | support if no return to use >=90 days; consider if 30-90 days; discourage active use or return within 30 days | RENDERED: supported ... ≥90 days ... considered ... 30-90 days ... discouraged ... within the last 30 days | cdc-2022 | 27 | p27/narrative/breastfeeding-oud | narrative |
| buprenorphine-transition | full-agonist-transition | standard initiation after mild-moderate withdrawal; wait at least 8-12 hours after short-acting or 12-24 hours after ER/LA, longer after methadone | RENDERED: wait at least 8-12 hours ... at least 12-24 hours ... and longer for methadone | cdc-2022 | 17 | p17/narrative/buprenorphine-transition | narrative |
| buprenorphine-low-dose-initiation | pain-buprenorphine-transition | low-dose initiation before withdrawal is an alternative for patients receiving full agonists for acute or chronic pain | RENDERED: As an alternative for patients not yet in opioid withdrawal, certain studies have described low dose initiation of buprenorphine to allow for initiation of buprenorphine in patients receiving full agonist opioids for acute or chronic pain | cdc-2022 | 17 | p17/narrative/low-dose-buprenorphine-pain | narrative |
| buprenorphine-pain-frequency | full-agonist-transition | pain dosing is typically multiple times daily, unlike once daily for OUD stabilization | dosing of buprenorphine for pain is typically multiple times daily rather than once-a-day dosing | cdc-2022 | 17 | p17/narrative/buprenorphine-pain | narrative |
| buprenorphine-low-dose-initiation | diagnosed-oud | low-dose initiation is a limited-evidence option while full-agonist opioids continue and does not require withdrawal | RENDERED: Low-dose buprenorphine initiation is a potential option for patients with opioid use disorder who are taking opioid medications for pain. With this dosing strategy, full agonist opioids can be continued while buprenorphine is initiated, and the patient does not need to experience opioid withdrawal symptoms | cdc-2022 | 27 | p27/narrative/low-dose-buprenorphine-oud | narrative |
| buprenorphine-overdose-boundary | pain-buprenorphine-transition | overdose risk is lower than with full agonists but not zero, especially with full agonists, benzodiazepines, alcohol, or other respiratory depressants | RENDERED: Although overdose is less likely with buprenorphine than with full agonist opioids, overdose is still possible, particularly if buprenorphine is taken concurrently with other respiratory depressants | cdc-2022 | 17 | p17/narrative/buprenorphine-overdose | narrative |
| buprenorphine-waiver-boundary | buprenorphine-prescribers | source-era rule: OUD prescribing required a SAMHSA waiver, whereas prescribing buprenorphine for chronic pain did not | RENDERED: prescription of buprenorphine for treatment of opioid use disorder requires the clinician to have a waiver from SAMHSA ... prescription of buprenorphine for treatment of chronic pain does not require a waiver | cdc-2022 | 17 | p17/narrative/buprenorphine-waiver | narrative |
| high-risk-continuation-safeguard | unable-taper-high-risk | closely monitor and mitigate overdose risk with overdose education and naloxone | RENDERED: Clinicians should closely monitor patients who are unable to taper and who continue on high-dosage or otherwise high-risk opioid regimens ... and should work with patients to mitigate overdose risk (e.g., by providing overdose education and naloxone) | cdc-2022 | 17 | p17/narrative/continuing-high-dose | narrative |
| oud-dose-duration-boundary | diagnosed-oud | pain dose guideposts do not apply to OUD agonist treatment; no recommended duration limit exists for OUD buprenorphine or methadone; discontinuation raises return-to-use and overdose risks | RENDERED: opioid dosage thresholds for caution in the treatment of pain are not applicable to opioid agonist treatment of opioid use disorder ... No recommended duration limit exists for treatment of opioid use disorder with buprenorphine or methadone, and discontinuation is associated with risks for return to drug use and opioid overdose | cdc-2022 | 27 | p27/narrative/oud-dose-duration | narrative |
| buprenorphine-oud-taper | diagnosed-oud | if discontinued, taper very gradually over several months | RENDERED: If discontinued, buprenorphine should be tapered very gradually (over several months) | cdc-2022 | 27 | p27/narrative/buprenorphine-oud-taper | narrative |
| naltrexone-opioid-free | naltrexone-initiation | opioid-free for 7-10 days before first dose | A minimum of 7-10 days free of opioids is recommended before the first naltrexone dose | cdc-2022 | 27 | p27/narrative/naltrexone-start | narrative |
| naltrexone-dose | naltrexone-initiation | extended-release injection 380 mg every 4 weeks; some rapid metabolizers may benefit every 3 weeks | RENDERED: every 4 weeks ... 380 mg per injection ... as frequently as every 3 weeks | cdc-2022 | 27 | p27/narrative/naltrexone-dose | narrative |
| emergency-oud-administration | diagnosed-oud | any clinician may administer, not prescribe, methadone or buprenorphine for acute withdrawal for up to 3 days while arranging treatment | As short-term exceptions, any clinician may administer (but not prescribe) methadone or buprenorphine to treat acute opioid withdrawal for up to 3 days, while working to refer the patient to opioid use disorder treatment | cdc-2022 | 27 | p27/narrative/three-day-rule | narrative |
| mme-conversion-factor | mme-calculation-users | codeine 0.15; fentanyl transdermal 2.4 mcg/hour; hydrocodone 1.0; hydromorphone 5.0; methadone 4.7; morphine 1.0; oxycodone 1.5; oxymorphone 3.0; tapentadol 0.4; tramadol 0.2 | RENDERED: Codeine 0.15; Fentanyl transdermal (in mcg/hr) 2.4; Hydrocodone 1.0; Hydromorphone 5.0; Methadone 4.7; Morphine 1.0; Oxycodone 1.5; Oxymorphone 3.0; Tapentadol 0.4; Tramadol 0.2 | cdc-2022 | 42 | p42/table/mme-conversion-factors | table |
| mme-conversion-use | mme-calculation-users | multiply each opioid dose by its conversion factor to determine MME; factors are estimates; never use calculated MME to choose a replacement-opioid dose; ordinarily dose the new opioid substantially lower for incomplete cross-tolerance and variability | RENDERED: Multiply the dose for each opioid by the conversion factor to determine the dose in MMEs. Equianalgesic dose conversions are only estimates. Do not use the calculated dose in MMEs to determine the doses to use when converting one opioid to another; the new opioid is typically dosed at a substantially lower dose because of incomplete cross-tolerance and individual variability | cdc-2022 | 42 | p42/table/mme-footnotes-conversion | table |
| mme-special-cautions | mme-calculation-users | use particular caution with methadone because of its long and variable half-life and later, longer respiratory-depressant peak; use particular caution with transdermal fentanyl because heat and other factors affect absorption | RENDERED: Use particular caution with methadone dose conversions because methadone has a long and variable half-life, and peak respiratory depressant effect occurs later and lasts longer than peak analgesic effect. Use particular caution with transdermal fentanyl because it is dosed in mcg/hr instead of mg/day, and its absorption is affected by heat and other factors | cdc-2022 | 42 | p42/table/mme-footnotes-caution | table |
| mme-exclusions | diagnosed-oud | pain-approved buprenorphine products are excluded because partial mu-receptor agonism produces a ceiling effect compared with full agonists; do not apply the factors to OUD dosage decisions | RENDERED: Buprenorphine products approved for the treatment of pain are not included in the table because of their partial µ-receptor agonist activity and resultant ceiling effects compared with full µ-receptor agonists. These conversion factors should not be applied to dosage decisions related to the management of opioid use disorder | cdc-2022 | 42 | p42/table/mme-footnotes-exclusions | table |
| mme-atypical-overdose-relationship | tapentadol-tramadol-users | dose-dependent overdose relationship is unknown for both tapentadol and tramadol | RENDERED: it is unknown whether tapentadol is associated with overdose in the same dose-dependent manner. It is unknown whether tramadol is associated with overdose in the same dose-dependent manner | cdc-2022 | 42 | p42/narrative/tapentadol-tramadol | narrative |

## Conflicts

No same-quantity, same-population action conflict was found. The source explicitly treats
50 MME/day as a guidepost rather than a rigid ceiling, and its taper percentages apply to
different prior-exposure populations. The pregnancy, pediatric, and OUD rows preserve
their distinct scopes rather than being generalized to the adult outpatient pain population.

## Coverage

The source's recommendation record is `nothing-found`: exact accounting is **0 marker
occurrences = 0 cited + 0 scoped out**. This is extractor silence, not evidence that the
guideline contains no recommendations. All 12 numbered recommendation actions and their
decision-changing implementation considerations were read directly and retained above.

ADR 0009 disposition: Retained patient-changing actions, numeric guideposts, regimen
branches, monitoring intervals, special-population safeguards, and explicit insufficiency
or noncoverage boundaries. Scoped out methods, evidence-search mechanics, prevalence,
historical prescribing trends, association-only study outcomes not tied to an action,
research priorities, author information, disclosures, and citations. External society
guidance was retained only where the CDC source itself uses it to define a care branch
(pregnancy, neonatal observation, and breastfeeding) and is labeled by its source context.
