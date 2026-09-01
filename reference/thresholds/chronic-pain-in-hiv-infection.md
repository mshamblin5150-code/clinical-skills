# Chronic pain in HIV infection — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| idsa-2017 | HIVMA of IDSA | IDSA/cix636 | guideline | 2017 guideline | 2017 | https://doi.org/10.1093/cid/cix636 | stated | bound |

## Scope

**Read:** all 37 source pages: title and executive-summary recommendations; introduction,
methods, definitions, and complete body; every recommendation, remark, evidence summary,
figure, and table; conflict-of-interest material; and references. The rows retain numbers
that define or screen chronic pain, set a dose or application regimen, schedule monitoring,
trigger follow-up, or otherwise change care for a patient. Prevalence, diagnostic accuracy,
effect estimates, trial enrollment and follow-up, study-only regimens not adopted by the
guideline, publication years, and bibliography numbers were read but do not produce rows.
Figure 1 and Tables 1-3 were also read as rendered page structures; their numeric labels or
qualitative cells add no patient-action decision point beyond the rows below.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| title and executive summary | 1-5 | yes |
| introduction and chronic-pain definition | 6 | yes |
| background, methods, and nonnumeric clinical discussion | 7-9 | read 2026-08-31; blind 2026-08-31 |
| chronic-pain screening recommendation and evidence | 10 | yes |
| assessment, palliative care, and nonpharmacologic therapy | 11-13 | yes |
| neuropathic-pain pharmacotherapy | 14 | yes |
| neuropathic-pain evidence without an adopted numeric action | 15-16 | read 2026-08-31; blind 2026-08-31 |
| study-only alpha-lipoic-acid evidence from diabetic-neuropathy meta-analysis | 17 | read 2026-08-31; blind 2026-08-31 |
| opioid evidence without an adopted numeric action | 18 | read 2026-08-31; blind 2026-08-31 |
| musculoskeletal treatment and tramadol | 19-20 | yes |
| opioid-risk discussion without a numeric action | 21 | read 2026-08-31; blind 2026-08-31 |
| substance-use screening and opioid-monitoring intervals | 22-23 | yes |
| pain agreement and rendered Table 1 | 24 | yes |
| urine-drug-testing intervals | 25 | yes |
| adverse-effect discussion and rendered Tables 2-3 | 26 | read 2026-08-31; blind 2026-08-31 |
| methadone, buprenorphine, and mental-health decision points | 27-30 | yes |
| neurocognitive evidence, methods, and disclosures | 31-32 | read 2026-08-31; blind 2026-08-31 |
| references | 33-37 | exempt: reference list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

recommendation identity: source sha256 5be456e384ae34bc3956af4f3e721fe6abac60deb46e5fd8c4c82065275bc0a1; tools/guidelines_recs.py sha256 0a0f1c776b0146ab1484c3f92ff557278ee73bfb0530d47619b1caca2821c8ac

## Populations

| key | verbatim |
| --- | --- |
| plwh | persons living with HIV |
| plwh-chronic-pain | persons living with HIV and chronic pain |
| adults-hiv-neuropathic-pain | adults with chronic HIV-associated neuropathic pain |
| hiv-peripheral-neuropathic-pain | persons with chronic HIV-associated peripheral neuropathic pain |
| plwh-musculoskeletal-pain | persons living with HIV with musculoskeletal pain |
| plwh-liver-disease-pain | persons living with HIV and liver disease who use acetaminophen for pain |
| plwh-osteoarthritis | persons living with HIV and osteoarthritis |
| plwh-opioid-candidates | persons living with HIV being assessed before opioid analgesic prescribing |
| new-clinic-patients | all new patients in a clinical practice |
| established-clinic-patients | established patients in a clinical practice |
| single-question-substance-screen | patients receiving the single-question alcohol and drug-use screens |
| stable-opioid-patients | stable persons living with HIV receiving opioids for chronic pain |
| high-risk-opioid-patients | persons living with HIV receiving opioids who have active mental health disorders or substance use within the last 6 months |
| plwh-opioid-therapy | persons living with HIV receiving opioid analgesics for chronic pain |
| methadone-patients | persons living with HIV receiving methadone |
| methadone-addiction-start | persons living with HIV starting methadone for addiction |
| methadone-oud-chronic-pain | persons living with HIV receiving methadone for opioid use disorder who also have chronic pain |
| methadone-split-eligible | methadone-maintained patients whose substance use disorder is in remission and who demonstrate good adherence |
| buprenorphine-chronic-pain | persons living with HIV receiving buprenorphine who have chronic noncancer pain |
| plwh-chronic-pain-depression-screen | persons living with HIV and chronic pain screened for depression |
| plwh-pain-assessment | persons living with HIV undergoing multidimensional pain assessment |

## Quantities

| key | verbatim |
| --- | --- |
| chronic-pain-duration | duration used to describe chronic pain |
| chronic-pain-positive-screen | duration and severity defining a positive chronic-pain screen |
| gabapentin-regimen | typical adult gabapentin titration target |
| capsaicin-regimen | capsaicin concentration, application time, and expected relief duration |
| precapsaicin-lidocaine | lidocaine concentration and application time before capsaicin |
| acetaminophen-dose | acetaminophen daily dose |
| tramadol-duration | maximum duration of a tramadol trial |
| tramadol-dose-range | studied tramadol regimen |
| alcohol-screen | single-question alcohol-screen timeframe and drinking threshold |
| drug-use-screen | single-question drug-use-screen timeframe |
| substance-use-screen-frequency | frequency of routine unhealthy alcohol and drug-use screening |
| substance-use-positive-screen | response count defining a positive single-question screen |
| opioid-monitoring-frequency | frequency of monitoring during opioid therapy |
| urine-drug-testing-schedule | baseline and follow-up urine-drug-testing schedule |
| urine-drug-testing-evidence | evidence limitation governing urine-drug-testing frequency |
| methadone-ecg-followup | timing of follow-up electrocardiography during methadone treatment |
| methadone-split-dose | methadone analgesic split-dose interval |
| methadone-split-eligibility | adherence example supporting split-dose eligibility |
| methadone-supplement | percentage increase used to begin split methadone dosing |
| buprenorphine-divided-dose | buprenorphine dose range and interval |
| buprenorphine-off-label-interval | off-label sublingual buprenorphine split-dose interval |
| peg-assessment-window | symptom window assessed by the three-item PEG instrument |
| depression-screen-window | timeframe covered by the two-question depression screen |
| phq9-followup | PHQ-9 result triggering psychiatric follow-up |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| chronic-pain-duration | plwh | pain lasting longer than 3-6 months | Chronic pain or pain that lasts longer than 3-6 months | idsa-2017 | 6 | p6/narrative/chronic-pain-duration | narrative |
| chronic-pain-positive-screen | plwh | moderate pain or more during the last week plus bodily pain for >3 months | RENDERED: moderate pain or more during the last week combined with bodily pain for more than 3 months can be considered a positive screen result | idsa-2017 | 1 | p1/grade-terse/1 | strong, low |
| chronic-pain-positive-screen | plwh | moderate pain or more during the last week plus bodily pain for >3 months | moderate pain or more during the last week combined with bodily pain for more than 3 months can be considered a positive screen result | idsa-2017 | 10 | p10/grade-terse/1 | strong, low |
| gabapentin-regimen | adults-hiv-neuropathic-pain | titrate to 2400 mg/day in divided doses | A typical adult regimen will titrate to 2400 mg per day in divided doses | idsa-2017 | 2 | p2/grade-terse/13 | strong, moderate |
| gabapentin-regimen | adults-hiv-neuropathic-pain | titrate to 2400 mg/day in divided doses | A typical adult regimen will titrate to 2400 mg per day in divided doses | idsa-2017 | 14 | p14/grade-terse/2 | strong, moderate |
| capsaicin-regimen | hiv-peripheral-neuropathic-pain | single 30-minute application of 8% patch or cream may provide relief for >=12 weeks | A single 30-minute application of an 8% dermal patch or cream administered at the site of pain can provide pain relief for at least 12 weeks | idsa-2017 | 2 | p2/grade-terse/18 | strong, high |
| capsaicin-regimen | hiv-peripheral-neuropathic-pain | single 30-minute application of 8% patch or cream may provide relief for >=12 weeks | A single 30-minute application of an 8% dermal patch or cream administered at the site of pain can provide pain relief for at least 12 weeks | idsa-2017 | 14 | p14/grade-terse/7 | strong, high |
| precapsaicin-lidocaine | hiv-peripheral-neuropathic-pain | apply 4% lidocaine for 60 minutes and wipe off before capsaicin | a 60-minute application of 4% lidocaine can be applied and wiped off before applying capsaicin | idsa-2017 | 2 | p2/grade-terse/19 | strong, high |
| precapsaicin-lidocaine | hiv-peripheral-neuropathic-pain | apply 4% lidocaine for 60 minutes and wipe off before capsaicin | a 60-minute application of 4% lidocaine can be applied and wiped off before applying capsaicin | idsa-2017 | 14 | p14/grade-terse/8 | strong, high |
| acetaminophen-dose | plwh-musculoskeletal-pain | studies used 4 g/day; use lower dosing with liver disease | Studies typically used 4 g/day dosing of acetaminophen; lower dosing is recommended for patients with liver disease | idsa-2017 | 3 | p3/grade-terse/6 | strong, high |
| acetaminophen-dose | plwh-musculoskeletal-pain | studies used 4 g/day; use lower dosing with liver disease | Studies typically used 4 g/day dosing of acetaminophen; lower dosing is recommended for patients with liver disease | idsa-2017 | 19 | p19/grade-terse/1 | strong, high |
| acetaminophen-dose | plwh-liver-disease-pain | no more than 2 g/day | Current recommendations limit the dose of acetaminophen to no more than 2 g/day in patients with liver disease | idsa-2017 | 19 | p19/narrative/acetaminophen-liver-dose | narrative |
| tramadol-duration | plwh-osteoarthritis | up to 3 months | Tramadol taken for up to 3 months may decrease pain and improve stiffness, function, and overall well-being | idsa-2017 | 3 | p3/grade-terse/8 | weak, moderate |
| tramadol-duration | plwh-osteoarthritis | up to 3 months | Tramadol taken for up to 3 months may decrease pain and improve stiffness, function, and overall well-being | idsa-2017 | 20 | p20/grade-terse/2 | weak, moderate |
| tramadol-dose-range | plwh-osteoarthritis | 37.5 mg with 325 mg acetaminophen once daily to 400 mg in divided doses | The range of tramadol dosing studied is 37.5 mg (combined with 325 mg of acetaminophen) once daily to 400 mg in divided doses | idsa-2017 | 3 | p3/grade-terse/8 | weak, moderate |
| tramadol-dose-range | plwh-osteoarthritis | 37.5 mg with 325 mg acetaminophen once daily to 400 mg in divided doses | The range of tramadol dosing studied is 37.5 mg (combined with 325 mg of acetaminophen) once daily to 400 mg in divided doses | idsa-2017 | 20 | p20/grade-terse/2 | weak, moderate |
| alcohol-screen | plwh-opioid-candidates | during the past year, ask about >5 standard drinks for men or >4 for women in 1 day | How many times in the past year have you had more than 5 (4 for women) standard drinks in 1 day? | idsa-2017 | 22 | p22/narrative/alcohol-screen | narrative |
| drug-use-screen | plwh-opioid-candidates | during the past year, ask about illegal-drug use or prescription-medication use for nonmedical reasons | How many times in the past year have you used an illegal drug or used a prescription medication for nonmedical reasons? | idsa-2017 | 22 | p22/narrative/drug-use-screen | narrative |
| substance-use-screen-frequency | new-clinic-patients | screen routinely at entry | conducted routinely as a clinic-wide practice with all new patients | idsa-2017 | 22 | p22/narrative/substance-screen-new | narrative |
| substance-use-screen-frequency | established-clinic-patients | screen annually | annually in established patients | idsa-2017 | 22 | p22/narrative/substance-screen-established | narrative |
| substance-use-positive-screen | single-question-substance-screen | >=1 response is positive for unhealthy alcohol and/or drug use | Responses of 1 or more are positive screens for unhealthy alcohol and/or drug use | idsa-2017 | 22 | p22/narrative/substance-screen-positive | narrative |
| opioid-monitoring-frequency | stable-opioid-patients | every 3-6 months | Some authors have suggested every 3-6 months for stable patients | idsa-2017 | 23 | p23/narrative/stable-opioid-monitoring | narrative |
| opioid-monitoring-frequency | high-risk-opioid-patients | monthly or even weekly; high risk includes last substance use <6 months | monthly or even weekly monitoring for high-risk patients such as those with recent histories of substance use (last use <6 months) | idsa-2017 | 23 | p23/narrative/high-risk-opioid-monitoring | narrative |
| urine-drug-testing-evidence | plwh-opioid-therapy | insufficient evidence to recommend a testing frequency | RENDERED: there is insufficient evidence to recommend the frequency with which UDT should be performed | idsa-2017 | 24 | p24/narrative/udt-frequency-evidence | narrative |
| urine-drug-testing-schedule | stable-opioid-patients | Christo practical approach that may be reasonable: baseline before opioids; adherence monitoring within 1-3 months; random monitoring about every 6-12 months | baseline UDT of all patients prior to the initiation of opioids for chronic pain; adherence monitoring within 1-3 months after baseline monitoring; and routine, random monitoring approximately every 6-12 months | idsa-2017 | 25 | p25/narrative/udt-schedule | narrative |
| methadone-ecg-followup | methadone-patients | external 2014 APS/CPDD/HRS low-quality guidance: follow-up as early as 2-4 weeks for higher QTc and no later than when dose reaches 100 mg/day | RENDERED: 2014 clinical practice guidelines on methadone safety from the American Pain Society, College on Problems of Drug Dependence, and Heart Rhythm Society; higher QTc intervals requiring closer follow-up as early as 2 to 4 weeks and as late as when the patient reaches 100 mg/day of methadone; most recommendations are based on a low quality of evidence | idsa-2017 | 27 | p27/narrative/methadone-ecg-followup | narrative |
| methadone-ecg-followup | methadone-addiction-start | pretreatment ECG and follow-up within 30 days | A pretreatment electrocardiogram (ECG) is recommended for all patients starting methadone for addiction to measure the baseline QTc, and a follow-up ECG should be performed within 30 days | idsa-2017 | 29 | p29/narrative/methadone-addiction-ecg | narrative |
| methadone-split-dose | methadone-oud-chronic-pain | divide into doses every 6-8 hours | RENDERED: The splitting of methadone into 6- to 8-hour doses is recommended | idsa-2017 | 5 | p5/grade-terse/2 | strong, low |
| methadone-split-dose | methadone-oud-chronic-pain | divide into doses every 6-8 hours | RENDERED: The splitting of methadone into 6- to 8-hour doses is recommended | idsa-2017 | 28 | p28/grade-terse/3 | strong, low |
| methadone-split-eligibility | methadone-split-eligible | adherence example: graduated to at least once-weekly pickups or take-homes | RENDERED: they have graduated to at least once weekly “pickups” or “take homes” | idsa-2017 | 28 | p28/narrative/methadone-split-eligibility | narrative |
| methadone-supplement | methadone-oud-chronic-pain | add 5%-10% of current dose as afternoon and evening doses for a total 10%-20% increase | RENDERED: 5%-10% of the current methadone dose should be added, usually as an afternoon and evening dose for a total 10%-20% increase | idsa-2017 | 5 | p5/grade-terse/3 | strong, very low |
| methadone-supplement | methadone-oud-chronic-pain | add 5%-10% of current dose as afternoon and evening doses for a total 10%-20% increase | RENDERED: 5%-10% of the current methadone dose should be added, usually as an afternoon and evening dose for a total 10%-20% increase | idsa-2017 | 28 | p28/grade-terse/4 | strong, very low |
| buprenorphine-divided-dose | buprenorphine-chronic-pain | 4-16 mg divided into doses every 8 hours | RENDERED: Dosing ranges of 4-16 mg divided into 8-hour doses have shown benefit | idsa-2017 | 5 | p5/grade-terse/7 | strong, very low |
| buprenorphine-divided-dose | buprenorphine-chronic-pain | 4-16 mg divided into doses every 8 hours | Dosing ranges of 4-16 mg divided into 8-hour doses have shown benefit | idsa-2017 | 29 | p29/grade-terse/2 | strong, very low |
| buprenorphine-off-label-interval | buprenorphine-chronic-pain | sublingual tablet or film may be prescribed off label every 6-8 hours; the recommended studied regimen is every 8 hours | The tablet or film can be prescribed off label in split doses (ie, every 6-8 hours) for the treatment of pain | idsa-2017 | 29 | p29/narrative/buprenorphine-off-label-interval | narrative |
| peg-assessment-window | plwh-pain-assessment | 3-item PEG assesses the past week | RENDERED: The ultra-brief, 3-item PEG is used to assess average pain intensity (P), interference with enjoyment of life (E), and interference with general activity (G) in the past week | idsa-2017 | 11 | p11/narrative/peg-window | narrative |
| depression-screen-window | plwh-chronic-pain-depression-screen | ask 2 questions about symptoms during the past 2 weeks | RENDERED: All patients should be screened for depression with the following 2 questions: During the past 2 weeks | idsa-2017 | 5 | p5/grade-terse/13 | strong, high |
| depression-screen-window | plwh-chronic-pain-depression-screen | ask 2 questions about symptoms during the past 2 weeks | All patients should be screened for depression with the following 2 questions: During the past 2 weeks | idsa-2017 | 30 | p30/grade-terse/2 | strong, high |
| phq9-followup | plwh-chronic-pain-depression-screen | PHQ-9 >=10: psychiatric follow-up | RENDERED: patient health questionnaire-9 (PHQ-9); Psychiatric follow-up for a result that is ≥10 | idsa-2017 | 5 | p5/grade-terse/14 | strong, high |
| phq9-followup | plwh-chronic-pain-depression-screen | PHQ-9 >=10: psychiatric follow-up | RENDERED: patient health questionnaire-9 (PHQ-9); Psychiatric follow-up for a result that is ≥10 | idsa-2017 | 30 | p30/grade-terse/3 | strong, high |

## Conflicts

None. The source's different values apply to different quantities or populations: the
3-6-month description of chronic pain is not the >3-month positive-screen rule; the
4-g/day acetaminophen study regimen is narrowed to no more than 2 g/day for people with
liver disease; and general opioid monitoring is distinct from urine-drug-testing cadence.

## Coverage

The source is bound: marker records delimit recommendation-shaped text but do not prove a complete recommendation denominator. The artifact contains 116 marker records under 116 distinct locators. Threshold rows cite 22 locators; the remaining 94 locators were read and contain no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative.

- `p1/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p1/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/6` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/7` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/8` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/9` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/10` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/11` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/12` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/14` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/15` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/16` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p2/grade-terse/17` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p3/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p3/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p3/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p3/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p3/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p3/grade-terse/7` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p3/grade-terse/9` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/6` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/7` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/8` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/9` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/10` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p4/grade-terse/11` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/6` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/8` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/9` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/10` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/11` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/12` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/15` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p5/grade-terse/16` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p10/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p10/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p11/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p11/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/6` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/7` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/8` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p12/grade-terse/9` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p14/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p14/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p14/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p14/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p14/grade-terse/6` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p14/grade-terse/9` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p15/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p15/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p18/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p18/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p20/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p21/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p22/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p22/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p23/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p25/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p25/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p25/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p25/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p25/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p27/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p27/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p28/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p28/grade-terse/2` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p28/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p28/grade-terse/6` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p29/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p29/grade-terse/3` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p29/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p29/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p29/grade-terse/6` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p30/grade-terse/1` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p30/grade-terse/4` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
- `p30/grade-terse/5` - no additional numeric patient-action decision point beyond a row represented from the summary, body recommendation, or narrative
