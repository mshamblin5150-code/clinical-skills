# Prostate cancer screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source document below. **Not a substitute
for the recommendation statement** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2018 | USPSTF | USPSTF/prostate-cancer-final-rec-statement-051418 | recommendation-statement | 2018 final recommendation | 2018-05-08 | https://doi.org/10.1001/jama.2018.3710 | stated | exact |

## Scope

**Read:** all 13 pages, including both recommendation branches, applicability,
rationale, informed decision making, risk assessment, screening and diagnostic
methods, screening intervals and PSA thresholds studied, benefits, harms, treatment
options and consequences, African American and family-history sections, research
gaps, review scope, trial evidence, decision models, public comment, update,
recommendations of others, article information, disclosures, and references.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's decision-point rule:** prevalence and burden estimates,
most trial sample sizes, confidence intervals and site-level effect estimates, practice
uptake percentages, research requests, publication metadata, and reference-list
numbers that do not change a screening, diagnostic, treatment, applicability, or
evidence boundary. Selected benefit, harm, and trial-protocol figures are retained as
evidence and are not converted into universal patient-care commands.

**Source: uspstf-2018**

| span | pages | read |
| --- | --- | --- |
| recommendations, rationale, benefits, harms | 1-4 | yes |
| risk, screening methods and trials, older-adult boundary | 4-5 | yes |
| interval and threshold trade-offs, treatment, African American evidence | 6-7 | yes |
| family-history guidance, research gaps, review scope | 7-8 | yes |
| screening and treatment benefits | 8-9 | yes |
| screening, ProbE 35-day biopsy outcomes, age-stratified false positives, overdiagnosis, and treatment harms | 9-10 | yes |
| net benefit, public comment, update, effect table | 10-11 | yes |
| recommendations of others | 12 | yes |
| article information and disclosures | 12 | read 2026-09-01; blind 2026-09-01 |
| references | 12-13 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-men-55-to-69 | men age 55 to 69 years in the general US population without prostate-cancer symptoms or a previous prostate-cancer diagnosis |
| asymptomatic-men-70-or-older | men age 70 years or older without prostate-cancer symptoms or a previous prostate-cancer diagnosis |
| men-older-than-70-harm-evidence | men older than 70 years represented in the source's quantified older-adult harm conclusion |
| men-older-than-70-requesting | men older than 70 years who still request PSA-based screening |
| asymptomatic-adult-men | adult men in the general US population without prostate-cancer symptoms or a previous prostate-cancer diagnosis |
| average-risk-men-under-55 | average-risk asymptomatic men younger than 55 years |
| men-without-screening-preference | asymptomatic men who do not express a preference for PSA-based screening |
| men-unable-unwilling-treatment | men unable or unwilling to tolerate treatment for screen-detected prostate cancer |
| men-positive-psa | men with a positive PSA screening result |
| men-considering-screening | asymptomatic adult men considering PSA-based screening |
| men-screened-55-to-69 | men age 55 to 69 years represented in PSA-screening benefit estimates |
| men-undergoing-biopsy | men undergoing transrectal ultrasound-guided prostate biopsy after a positive PSA result |
| probe-biopsy-participants | men in the ProbE biopsy cohort reporting symptoms within 35 days after prostate biopsy |
| erspc-first-round-age-comparison | men older than 70 years compared with men younger than 55 years in the first ERSPC screening round |
| screen-detected-localized-cancer | men with screen-detected localized prostate cancer |
| screen-detected-low-risk-cancer | men with apparent low-risk screen-detected prostate cancer |
| men-radical-prostatectomy | men receiving radical prostatectomy |
| men-radiation-therapy | men receiving radiation therapy |
| men-active-surveillance | men receiving active surveillance |
| african-american-men | African American men without prostate-cancer symptoms or a previous diagnosis |
| african-american-men-under-55 | African American men younger than 55 years |
| african-american-men-70-or-older | African American men age 70 years or older |
| men-family-history | men with a family history of prostate cancer without prostate-cancer symptoms or a previous diagnosis |
| men-family-history-under-55 | men younger than 55 years with a family history of prostate cancer |
| men-family-history-70-or-older | men age 70 years or older with a family history of prostate cancer |
| men-highest-family-history-likelihood | men with a first-degree relative whose prostate cancer was advanced at diagnosis, became metastatic, or caused death |
| men-multiple-first-degree-relatives | men with multiple first-degree relatives with prostate cancer |
| hereditary-pattern-context | men with 3 first-degree relatives with prostate cancer or 2 close relatives on the same side of the family diagnosed before age 55 years |
| external-men-aafp-ctfphc | men under source-printed AAFP and Canadian Task Force guidance |
| external-acp-men-50-to-69 | men age 50 to 69 years under source-printed ACP guidance |
| external-acp-screening-candidates | men under source-printed ACP guidance who prioritize screening and have life expectancy longer than 10 to 15 years |
| external-aua-men-55-to-69 | men age 55 to 69 years with life expectancy longer than 10 to 15 years under source-printed AUA guidance |
| external-aua-high-risk | African American men and men with a family history under source-printed AUA guidance |
| external-acs-average-risk | men under source-printed ACS average-risk discussion guidance |
| external-acs-higher-risk | African American men and men with a father or brother diagnosed before age 65 years under source-printed ACS guidance |
| men-invited-to-screening-estimate | cohorts of 1000 US men age 55 to 69 years invited to PSA-based screening and followed for 13 years in the source's shared-decision table |

## Quantities

| key | verbatim |
| --- | --- |
| age-55-to-69-screening | USPSTF individualized screening decision |
| age-70-screening | USPSTF recommendation against screening |
| screening-preference-boundary | expressed-preference prerequisite |
| applicability | recommendation population boundary |
| informed-decision-factors | benefits, harms, risks, health, and value considerations |
| age-55-to-69-net-benefit | net-benefit magnitude and value sensitivity |
| age-70-net-benefit | older-adult net-benefit conclusion |
| primary-screening-test | PSA blood-test screening method |
| positive-psa-followup | biopsy diagnostic pathway |
| psa-alternative-methods | evidence boundary for PSA strategy alternatives |
| average-risk-early-screening | evidence boundary for starting average-risk screening before age 55 years |
| baseline-psa-screening | evidence boundary for baseline PSA screening |
| risk-calculator-adjuncts | evidence boundary for prebiopsy calculators and adjuncts |
| dre-screening | digital rectal examination screening position |
| trial-screening-protocols | evidence-only trial intervals and biopsy thresholds |
| screening-benefit-mortality | prostate-cancer mortality benefit estimate |
| screening-benefit-metastatic | metastatic-cancer benefit estimate |
| all-cause-mortality-benefit | all-cause mortality evidence boundary |
| false-positive-harm | false-positive frequency and psychological harm |
| psychological-harm | persistent worry after an abnormal PSA result and benign biopsy |
| biopsy-harm | biopsy complication and hospitalization harm |
| biopsy-short-term-harm-evidence | evidence-only 35-day pain, fever, and hematospermia outcomes after biopsy |
| overdiagnosis-harm | screen-detected overdiagnosis estimate |
| surgery-harm | radical-prostatectomy mortality, complication, continence, and erectile harms |
| radiation-harm | radiation erectile and bowel harms |
| older-adult-harm | age-related increase in screening, biopsy, and treatment harms |
| age-stratified-false-positive-evidence | evidence-only first-round false-positive comparison for older-than-70 versus younger-than-55 men |
| older-request-counseling | counseling boundary when an older man still requests screening |
| screening-interval-boundary | no single endorsed screening interval and interval trade-offs |
| psa-threshold-tradeoff | biopsy-threshold benefit and harm trade-off |
| screening-revisit | revisiting a preference-sensitive decision |
| treatment-willingness | treatment-tolerance prerequisite for screening |
| localized-treatment-options | common treatment options |
| treatment-benefit | active-treatment progression and metastasis evidence |
| treatment-trial-outcome | evidence-only ProtecT treatment outcome |
| active-surveillance-protocol | monitoring and treatment-conversion boundary |
| active-surveillance-harm | repeated-biopsy and later-treatment exposure |
| african-american-risk-counseling | risk disclosure and informed decision action |
| african-american-separate-recommendation | evidence boundary for distinct recommendation |
| african-american-early-screening | evidence boundary before age 55 years |
| african-american-biopsy-harm | evidence-only major-infection disparity |
| high-risk-harm-comparison | evidence boundary for harm comparisons in higher-risk groups |
| family-history-risk-counseling | family-history disclosure and informed decision action |
| family-history-separate-recommendation | evidence boundary for distinct recommendation |
| family-history-early-screening | evidence boundary before age 55 years |
| family-history-benefit-likelihood | source-described family pattern most likely to benefit |
| hereditary-family-pattern | source-described potential inheritable pattern |
| external-aafp-ctfphc | source-printed AAFP and Canadian Task Force position |
| external-acp-screening | source-printed ACP discussion and eligibility boundaries |
| external-aua-screening | source-printed AUA discussion, interval, and high-risk boundaries |
| external-acs-discussion | source-printed ACS discussion ages |
| shared-decision-estimate-horizon | source table cohort and follow-up horizon |
| shared-decision-estimate-positive-psa | source table positive-PSA count |
| shared-decision-estimate-biopsy | source table biopsy count |
| shared-decision-estimate-biopsy-hospitalization | source table biopsy-hospitalization count |
| shared-decision-estimate-diagnosis | source table prostate-cancer diagnosis count |
| shared-decision-estimate-initial-treatment | source table initial active-treatment count |
| shared-decision-estimate-initial-surveillance | source table initial active-surveillance count |
| shared-decision-estimate-surveillance-to-treatment | source table surveillance-to-active-treatment count |
| shared-decision-estimate-sexual-dysfunction | source table treatment-linked sexual-dysfunction count |
| shared-decision-estimate-incontinence | source table treatment-linked incontinence count |
| shared-decision-estimate-other-cause-death | source table non-prostate-cancer death count |
| shared-decision-estimate-prostate-death | source table prostate-cancer death count despite screening and treatment |
| shared-decision-estimate-metastasis-avoided | source table metastatic-cancer avoidance count |
| shared-decision-estimate-prostate-death-avoided | source table prostate-cancer death avoidance count |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| age-55-to-69-screening | asymptomatic-men-55-to-69 | make periodic PSA-based screening an individual decision after benefits-and-harms discussion; Grade C | For men aged 55 to 69 years, the decision to undergo periodic PSA-based screening for prostate cancer should be an individual one | uspstf-2018 | 1 | p1/screening-for-prostate-cancer/1 | C |
| age-70-screening | asymptomatic-men-70-or-older | do not perform PSA-based screening; Grade D | The USPSTF recommends against PSA-based screening for prostate cancer in men 70 years and older. | uspstf-2018 | 1 | p1/screening-for-prostate-cancer/2 | D |
| screening-preference-boundary | men-without-screening-preference | do not screen when the man does not express a preference for screening | Clinicians should not screen men who do not express a preference for screening. | uspstf-2018 | 1 | p1/screening-for-prostate-cancer/1 | C |
| applicability | asymptomatic-adult-men | applies without symptoms or previous prostate-cancer diagnosis, including increased risk by race, ethnicity, or family history | RENDERED: applies to adult men in the general US population without symptoms or a previous diagnosis of prostate cancer. It also applies to men at increased risk ... because of race/ethnicity or family history | uspstf-2018 | 4 | p4/narrative/applicability | narrative |
| informed-decision-factors | men-considering-screening | consider family history, race or ethnicity, comorbid conditions, patient values about screening and treatment outcomes, and other health needs | RENDERED: consider the balance of benefits and harms on the basis of family history, race/ethnicity, comorbid medical conditions, patient values about the benefits and harms of screening and treatment-specific outcomes, and other health needs. | uspstf-2018 | 1 | p1/screening-for-prostate-cancer/1 | C |
| age-55-to-69-net-benefit | asymptomatic-men-55-to-69 | moderate certainty of a small net benefit for some men; individual weighting determines the result | RENDERED: moderate certainty that the net benefit ... in men aged 55 to 69 years is small for some men. How each man weighs specific benefits and harms will determine whether the overall net benefit is small. | uspstf-2018 | 4 | p4/narrative/age-55-69-net-benefit | narrative |
| age-70-net-benefit | asymptomatic-men-70-or-older | moderate certainty that potential benefits do not outweigh expected harms | RENDERED: moderate certainty that the potential benefits ... in men 70 years and older do not outweigh the expected harms. | uspstf-2018 | 4 | p4/narrative/age-70-net-benefit | narrative |
| primary-screening-test | asymptomatic-adult-men | PSA protein measurement in blood is the initial screening method | RENDERED: Screening for prostate cancer begins with a test that measures the amount of PSA protein in the blood. | uspstf-2018 | 2 | p2/narrative/primary-screening-test | narrative |
| positive-psa-followup | men-positive-psa | a positive PSA result may lead to transrectal ultrasound-guided core-needle biopsy for diagnosis | RENDERED: Men with a positive PSA test result may undergo a transrectal ultrasound-guided core-needle biopsy of the prostate to diagnose prostate cancer. | uspstf-2018 | 2 | p2/narrative/positive-psa-biopsy | narrative |
| psa-alternative-methods | asymptomatic-adult-men | evidence is insufficient to favor single-threshold, adjusted-threshold, PSA velocity, or PSA doubling-time screening over another PSA method | RENDERED: evidence is insufficient to support one method of PSA-based screening over another. | uspstf-2018 | 5 | p5/narrative/psa-method-evidence | narrative |
| average-risk-early-screening | average-risk-men-under-55 | inadequate evidence supports starting PSA screening before age 55 years | RENDERED: inadequate evidence on starting screening at a younger age in the average-risk population ... before age 55 years | uspstf-2018 | 5 | p5/narrative/average-risk-early-screening-gap | narrative |
| baseline-psa-screening | asymptomatic-adult-men | inadequate evidence supports obtaining a baseline PSA level as a screening strategy | RENDERED: inadequate evidence ... to obtain a baseline PSA level. | uspstf-2018 | 5 | p5/narrative/baseline-psa-gap | narrative |
| risk-calculator-adjuncts | men-positive-psa | evidence is insufficient that prebiopsy risk calculators, free-PSA measurement, genetic testing, or adjunctive imaging meaningfully change benefits and harms | RENDERED: Evidence is also insufficient that using a prebiopsy risk calculator, with or without measurement of free PSA levels, or using genetic or adjunctive imaging tests meaningfully changes the potential benefits and harms of screening. | uspstf-2018 | 5 | p5/narrative/prebiopsy-adjuncts | narrative |
| dre-screening | asymptomatic-adult-men | do not use digital rectal examination as a screening modality because benefit evidence is lacking | RENDERED: The use of digital rectal examination as a screening modality is not recommended because there is a lack of evidence on the benefits | uspstf-2018 | 5 | p5/narrative/dre-screening | narrative |
| trial-screening-protocols | men-screened-55-to-69 | EVIDENCE ONLY: trials ranged from one-time to every 1 to 4 years and used PSA biopsy thresholds 2.5 to 10.0 ng/mL | RENDERED: varying screening intervals (from 1-time screening to every 1 to 4 years) and PSA thresholds (2.5 to 10.0 ng/mL) for diagnostic biopsy. | uspstf-2018 | 5 | p5/narrative/trial-protocol-range | narrative |
| screening-benefit-mortality | men-screened-55-to-69 | EVIDENCE ONLY: about 1.3 prostate-cancer deaths prevented over about 13 years per 1000 men screened | RENDERED: may prevent approximately 1.3 deaths from prostate cancer over approximately 13 years per 1000 men screened. | uspstf-2018 | 2 | p2/narrative/mortality-benefit | narrative |
| screening-benefit-metastatic | men-screened-55-to-69 | EVIDENCE ONLY: about 3 metastatic prostate-cancer cases prevented per 1000 men screened | RENDERED: prevent approximately 3 cases of metastatic prostate cancer per 1000 men screened. | uspstf-2018 | 2 | p2/narrative/metastatic-benefit | narrative |
| all-cause-mortality-benefit | men-screened-55-to-69 | no all-cause mortality reduction was found in current screening trials | RENDERED: Current results from screening trials show no reductions in all-cause mortality from screening. | uspstf-2018 | 2 | p2/narrative/all-cause-mortality | narrative |
| false-positive-harm | men-screened-55-to-69 | EVIDENCE ONLY: more than 15% had at least 1 false-positive result over 10 years when screened every 2 to 4 years | RENDERED: screened every 2 to 4 years ... over 10 years, more than 15% of men experienced at least 1 false-positive test result. | uspstf-2018 | 2 | p2/narrative/false-positive-frequency | narrative |
| psychological-harm | men-positive-psa | EVIDENCE ONLY: abnormal PSA with benign biopsy increased worry at 6 to 8 weeks and 1 year in two observational studies | RENDERED: abnormal PSA screening results but benign biopsy results had significantly increased worry ... at 6- to 8-week and at 1-year follow-up | uspstf-2018 | 10 | p10/narrative/psychological-harm | narrative |
| biopsy-harm | men-undergoing-biopsy | biopsy may cause pain, hematospermia, or infection; about 1% require hospitalization | RENDERED: complications ... such as pain, hematospermia ... and infection. Approximately 1% of prostate biopsies result in complications requiring hospitalization. | uspstf-2018 | 2 | p2/narrative/biopsy-harms | narrative |
| biopsy-short-term-harm-evidence | probe-biopsy-participants | EVIDENCE ONLY: within 35 days after biopsy, 7.3% reported moderate-or-greater pain, 5.5% moderate-to-severe fever, and 26.6% troublesome hematospermia | RENDERED: In the ProbE trial, 7.3% of men reported moderate or greater pain, 5.5% reported moderate to severe fever, and 26.6% reported troublesome hematospermia within the 35 days after biopsy. | uspstf-2018 | 10 | p10/narrative/probe-biopsy-short-term-harms | narrative |
| overdiagnosis-harm | men-screened-55-to-69 | EVIDENCE ONLY: 20% to 50% of screen-detected prostate cancers may be overdiagnosed; risk increases with age and is highest at age 70 years or older | RENDERED: 20% to 50% of men diagnosed with prostate cancer through screening may be overdiagnosed ... expected to increase with age and to be highest in men 70 years and older | uspstf-2018 | 3 | p3/narrative/overdiagnosis-harm | narrative |
| surgery-harm | men-radical-prostatectomy | EVIDENCE ONLY: about 3 per 1000 die during or soon after surgery; about 50 per 1000 have serious complications; about 1 in 5 have long-term incontinence and 2 in 3 long-term erectile dysfunction | RENDERED: About 3 in 1000 men die during or soon after radical prostatectomy ... 50 in 1000 ... serious surgical complications ... 1 in 5 ... long-term urinary incontinence ... 2 in 3 ... long-term erectile dysfunction. | uspstf-2018 | 6 | p6/narrative/surgery-harms | narrative |
| radiation-harm | men-radiation-therapy | EVIDENCE ONLY: more than half have long-term erectile dysfunction and up to 1 in 6 have long-term bothersome bowel symptoms | RENDERED: More than half of men who receive radiation therapy experience long-term erectile dysfunction, and up to 1 in 6 men experience long-term bothersome bowel symptoms | uspstf-2018 | 6 | p6/narrative/radiation-harms | narrative |
| older-adult-harm | men-older-than-70-harm-evidence | harms are at least moderate and greater than in younger men because false positives, biopsy harms, and treatment harms increase | RENDERED: harms of screening in men older than 70 years are at least moderate and greater than in younger men because of increased risk of false-positive results, harms from diagnostic biopsy, and harms from treatment. | uspstf-2018 | 4 | p4/narrative/older-adult-harms | narrative |
| age-stratified-false-positive-evidence | erspc-first-round-age-comparison | EVIDENCE ONLY: first-round false-positive results were 20.6% in men older than 70 years versus 3.5% in men younger than 55 years | RENDERED: Men older than 70 years in the ERSPC trial had a higher rate of false-positive results than younger men (younger than 55 years) (20.6% vs 3.5% in the first screening round, respectively). | uspstf-2018 | 10 | p10/narrative/age-stratified-false-positive-results | narrative |
| older-request-counseling | men-older-than-70-requesting | explain the lower benefit likelihood and higher risks of false positives and diagnostic and treatment complications; this does not reverse Grade D | RENDERED: Men older than 70 years who request screening should be aware of the reduced likelihood of benefit ... and the increased risk of false-positive test results and complications of diagnosis and treatment. | uspstf-2018 | 5 | p5/narrative/older-request-counseling | narrative |
| screening-interval-boundary | men-considering-screening | EVIDENCE ONLY: decision models suggest screening every 2 or 4 years rather than annually trades less overdiagnosis for a small mortality-benefit reduction; this is not a USPSTF interval mandate | RENDERED: every 2 or 4 years instead of annually appears to provide a good trade-off between a reduction in overdiagnosis and a small reduction in mortality benefit. | uspstf-2018 | 10 | p10/narrative/model-interval-tradeoff | narrative |
| psa-threshold-tradeoff | men-positive-psa | EVIDENCE ONLY: biopsy thresholds below 4.0 ng/mL and more frequent screening may reduce mortality more but increase false positives, biopsies, and overdiagnosis | RENDERED: lower PSA thresholds (<4.0 ng/mL) for biopsy and more frequent screening intervals offered greater potential reductions in prostate cancer mortality but higher rates of overdiagnosis and other harms. | uspstf-2018 | 6 | p6/narrative/threshold-tradeoff | narrative |
| screening-revisit | men-considering-screening | regularly revisit the decision to screen or not because values may change over time | RENDERED: The value a man places on potential benefits and harms may also change over time. It may therefore be useful for clinicians to regularly revisit the decision to screen (or not screen) | uspstf-2018 | 11 | p11/narrative/revisit-decision | narrative |
| treatment-willingness | men-unable-unwilling-treatment | do not screen men who cannot or will not tolerate prostate-cancer treatment | RENDERED: Men not able or willing to tolerate treatment should not be screened for prostate cancer. | uspstf-2018 | 6 | p6/narrative/treatment-willingness | narrative |
| localized-treatment-options | screen-detected-localized-cancer | common options are radical prostatectomy, radiation therapy, and active surveillance | RENDERED: 3 most common treatment options ... radical prostatectomy ... radiation therapy ... and active surveillance. | uspstf-2018 | 6 | p6/narrative/localized-treatment-options | narrative |
| treatment-benefit | screen-detected-localized-cancer | radical prostatectomy or radiation likely reduces clinical progression and metastasis and may reduce prostate-cancer mortality | RENDERED: radical prostatectomy or radiation therapy likely reduces risk of clinical progression and metastatic disease and may reduce prostate cancer mortality. | uspstf-2018 | 6 | p6/narrative/treatment-benefit | narrative |
| treatment-trial-outcome | screen-detected-localized-cancer | EVIDENCE ONLY: ProtecT found no mortality improvement at 10 years; radical prostatectomy reduced metastatic progression by 61% and radiation by 52% versus active surveillance | RENDERED: did not find a significant improvement in all-cause or prostate cancer mortality ... 10 years ... radical prostatectomy (61% reduction ... and radiation therapy (52% reduction ... with active surveillance. | uspstf-2018 | 9 | p9/narrative/protect-treatment-outcome | narrative |
| active-surveillance-protocol | screen-detected-low-risk-cancer | regular repeated PSA testing, often repeated digital rectal examination and biopsy; offer surgery or radiation when cancer changes | RENDERED: active surveillance usually includes regular, repeated PSA testing and often repeated digital rectal examination and prostate biopsy ... Men whose cancer is found to be changing are offered definitive treatment with surgery or radiation therapy. | uspstf-2018 | 6 | p6/narrative/active-surveillance-protocol | narrative |
| active-surveillance-harm | men-active-surveillance | repeated biopsy can repeat biopsy harms and later active treatment adds surgery or radiation harms | RENDERED: may undergo repeated biopsies and be exposed to potential repeated harms from biopsies ... go on to have active treatment with surgery or radiation therapy, with resultant harms | uspstf-2018 | 10 | p10/narrative/active-surveillance-harms | narrative |
| african-american-risk-counseling | african-american-men | inform men of increased development and death risk and discuss potential screening benefits and harms for an informed personal decision | RENDERED: inform African American men about their increased risk of developing and dying of prostate cancer as well as the potential benefits and harms of screening so they can make an informed, personal decision | uspstf-2018 | 7 | p7/narrative/african-american-counseling | narrative |
| african-american-separate-recommendation | african-american-men | evidence does not support a separate specific USPSTF recommendation | RENDERED: not able to make a separate, specific recommendation on PSA-based screening ... in African American men. | uspstf-2018 | 6 | p6/narrative/african-american-no-separate-rec | narrative |
| african-american-early-screening | african-american-men-under-55 | inadequate evidence establishes benefit from starting before age 55 years; models are not direct evidence | RENDERED: inadequate evidence to assess whether there are benefits to starting screening in these high-risk groups before age 55 years. | uspstf-2018 | 2 | p2/narrative/high-risk-before-55-gap | narrative |
| age-70-screening | african-american-men-70-or-older | do not screen; increased racial risk does not override the age-70 recommendation; Grade D | men 70 years and older | uspstf-2018 | 1 | p1/screening-for-prostate-cancer/2 | D |
| african-american-biopsy-harm | african-american-men | EVIDENCE ONLY: PLCO analysis found major infection after biopsy odds ratio 7.1 versus white men | RENDERED: African American men were significantly more likely to have major infections after prostate biopsy than white men (odds ratio [OR], 7.1 | uspstf-2018 | 6 | p6/narrative/african-american-biopsy-infection | narrative |
| high-risk-harm-comparison | african-american-men | evidence is insufficient to compare false positives, overdiagnosis, and treatment-harm magnitude with other men | RENDERED: Evidence is insufficient to compare the risk of false-positive results, potential for overdiagnosis, and magnitude of harms ... in African American vs other men. | uspstf-2018 | 6 | p6/narrative/african-american-harm-gap | narrative |
| family-history-separate-recommendation | men-family-history | evidence does not support a separate specific USPSTF recommendation | RENDERED: not able to make a separate, specific recommendation ... in men with a family history of prostate cancer. | uspstf-2018 | 7 | p7/narrative/family-history-no-separate-rec | narrative |
| high-risk-harm-comparison | men-family-history | no study assessed screening, diagnostic, or treatment harms according to family history | RENDERED: No studies have assessed the risk of harms related to screening for, diagnosis of, or treatment of prostate cancer based on family history | uspstf-2018 | 7 | p7/narrative/family-history-harm-gap | narrative |
| family-history-risk-counseling | men-multiple-first-degree-relatives | inform men, especially those with multiple first-degree relatives, of increased risk, possible earlier onset, and screening benefits and harms for an informed personal decision | RENDERED: inform men with a family history ... particularly those with multiple first-degree relatives ... about their increased risk ... potential earlier age ... include the potential benefits and harms of screening ... informed, personal decision | uspstf-2018 | 7 | p7/narrative/family-history-counseling | narrative |
| family-history-early-screening | men-family-history-under-55 | inadequate evidence establishes benefit from starting before age 55 years | RENDERED: inadequate evidence to assess whether there are benefits to starting screening in these high-risk groups before age 55 years. | uspstf-2018 | 2 | p2/narrative/high-risk-before-55-gap | narrative |
| age-70-screening | men-family-history-70-or-older | do not screen; family history does not override the age-70 recommendation; Grade D | men 70 years and older | uspstf-2018 | 1 | p1/screening-for-prostate-cancer/2 | D |
| family-history-benefit-likelihood | men-highest-family-history-likelihood | probably most likely to benefit when a first-degree relative had advanced disease at diagnosis, developed metastasis, or died of prostate cancer | RENDERED: first-degree relative who had advanced prostate cancer at diagnosis, developed metastatic prostate cancer, or died of prostate cancer are probably the most likely to benefit from screening. | uspstf-2018 | 7 | p7/narrative/family-history-most-likely-benefit | narrative |
| hereditary-family-pattern | hereditary-pattern-context | SOURCE-DESCRIBED CONTEXT: 3 first-degree relatives, or 2 close same-side relatives diagnosed before age 55 years, may indicate inheritable prostate cancer | RENDERED: 3 first-degree relatives with prostate cancer or 2 close relatives on the same side of the family with prostate cancer diagnosed before age 55 years may have an inheritable form | uspstf-2018 | 7 | p7/narrative/hereditary-family-pattern | narrative |
| external-aafp-ctfphc | external-men-aafp-ctfphc | SOURCE-PRINTED EXTERNAL (AAFP and Canadian Task Force): recommend against PSA-based screening | RENDERED: The American Academy of Family Physicians and the Canadian Task Force on Preventive Health Care recommend against PSA-based screening | uspstf-2018 | 12 | p12/narrative/external-aafp-ctfphc | narrative |
| external-acp-screening | external-acp-men-50-to-69 | SOURCE-PRINTED EXTERNAL (ACP): discuss benefits and harms from age 50 through 69 years | RENDERED: recommends that clinicians discuss the benefits and harms of screening with men aged 50 to 69 years | uspstf-2018 | 12 | p12/narrative/external-acp-discussion | narrative |
| external-acp-screening | external-acp-screening-candidates | SOURCE-PRINTED EXTERNAL (ACP): screen only men who prioritize screening and have life expectancy longer than 10 to 15 years | RENDERED: only recommends screening for men who prioritize screening and have a life expectancy of more than 10 to 15 years. | uspstf-2018 | 12 | p12/narrative/external-acp-eligibility | narrative |
| external-aua-screening | external-aua-men-55-to-69 | SOURCE-PRINTED EXTERNAL (AUA): with life expectancy longer than 10 to 15 years, inform about benefits and harms and use shared decision making; use an interval of at least 2 years to reduce harms | RENDERED: men aged 55 to 69 years with a life expectancy of more than 10 to 15 years ... informed ... engage in shared decision making ... screening interval should be 2 or more years. | uspstf-2018 | 12 | p12/narrative/external-aua-main | narrative |
| external-aua-screening | external-aua-high-risk | SOURCE-PRINTED EXTERNAL (AUA): individualize decisions, including possible start before age 55 years | RENDERED: decisions about screening, including potentially starting screening before age 55 years, should be individual ones for African American men and men with a family history | uspstf-2018 | 12 | p12/narrative/external-aua-high-risk | narrative |
| external-acs-discussion | external-acs-average-risk | SOURCE-PRINTED EXTERNAL (ACS): begin screening conversations at age 50 years | RENDERED: recommends conversations about screening beginning at age 50 years | uspstf-2018 | 12 | p12/narrative/external-acs-average-risk | narrative |
| external-acs-discussion | external-acs-higher-risk | SOURCE-PRINTED EXTERNAL (ACS): begin conversations earlier for African American men and men with a father or brother diagnosed before age 65 years | RENDERED: earlier for African American men and men with a father or brother with a history of prostate cancer before age 65 years. | uspstf-2018 | 12 | p12/narrative/external-acs-higher-risk | narrative |
| shared-decision-estimate-horizon | men-invited-to-screening-estimate | EVIDENCE ONLY: estimated effects after 13 years among 1000 men age 55 to 69 years invited to screening | RENDERED: Estimated Effects After 13 Years of Inviting Men Aged 55 to 69 Years ... Men invited to screening 1000 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-horizon | narrative |
| shared-decision-estimate-positive-psa | men-invited-to-screening-estimate | EVIDENCE ONLY: 240 men receive at least 1 positive PSA result | RENDERED: Men who received at least 1 positive PSA test result 240 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-positive-psa | narrative |
| shared-decision-estimate-biopsy | men-invited-to-screening-estimate | EVIDENCE ONLY: 220 men undergo 1 or more transrectal prostate biopsies | RENDERED: Men who have undergone 1 or more transrectal prostate biopsies 220 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-biopsy | narrative |
| shared-decision-estimate-biopsy-hospitalization | men-invited-to-screening-estimate | EVIDENCE ONLY: 2 men are hospitalized for a biopsy complication | RENDERED: Men hospitalized for a biopsy complication 2 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-biopsy-hospitalization | narrative |
| shared-decision-estimate-diagnosis | men-invited-to-screening-estimate | EVIDENCE ONLY: 100 men are diagnosed with prostate cancer | RENDERED: Men diagnosed with prostate cancer 100 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-diagnosis | narrative |
| shared-decision-estimate-initial-treatment | men-invited-to-screening-estimate | EVIDENCE ONLY: 65 men initially receive radical prostatectomy or radiation therapy | RENDERED: Men who initially received active treatment with radical prostatectomy or radiation therapy 65 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-initial-treatment | narrative |
| shared-decision-estimate-initial-surveillance | men-invited-to-screening-estimate | EVIDENCE ONLY: 30 men initially receive active surveillance | RENDERED: Men who initially received active surveillance 30 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-initial-surveillance | narrative |
| shared-decision-estimate-surveillance-to-treatment | men-invited-to-screening-estimate | EVIDENCE ONLY: 15 men initially under surveillance proceed to radical prostatectomy or radiation therapy | RENDERED: Men who initially received active surveillance who went on to receive active treatment with radical prostatectomy or radiation therapy 15 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-surveillance-to-treatment | narrative |
| shared-decision-estimate-sexual-dysfunction | men-invited-to-screening-estimate | EVIDENCE ONLY: 50 men receiving initial or deferred treatment have sexual dysfunction | RENDERED: Men with sexual dysfunction who received initial or deferred treatment 50 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-sexual-dysfunction | narrative |
| shared-decision-estimate-incontinence | men-invited-to-screening-estimate | EVIDENCE ONLY: 15 men receiving initial or deferred treatment have urinary incontinence | RENDERED: Men with urinary incontinence who received initial or deferred treatment 15 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-incontinence | narrative |
| shared-decision-estimate-other-cause-death | men-invited-to-screening-estimate | EVIDENCE ONLY: 200 men die of causes other than prostate cancer | RENDERED: Men who died of causes other than prostate cancer 200 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-other-cause-death | narrative |
| shared-decision-estimate-prostate-death | men-invited-to-screening-estimate | EVIDENCE ONLY: 5 men die of prostate cancer despite screening, diagnosis, and treatment | RENDERED: Men who died of prostate cancer despite screening, diagnosis, and treatment 5 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-prostate-death | narrative |
| shared-decision-estimate-metastasis-avoided | men-invited-to-screening-estimate | EVIDENCE ONLY: 3 men avoid metastatic prostate cancer | RENDERED: Men who avoided metastatic prostate cancer 3 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-metastasis-avoided | narrative |
| shared-decision-estimate-prostate-death-avoided | men-invited-to-screening-estimate | EVIDENCE ONLY: 1.3 men avoid death from prostate cancer | RENDERED: Men who avoided dying of prostate cancer 1.3 | uspstf-2018 | 11 | p11/narrative/shared-decision-table-prostate-death-avoided | narrative |

## Conflicts

The Grade C branch is limited to an individualized decision for asymptomatic men age
55 to 69 years after informed discussion and expressed preference. The Grade D branch
recommends against PSA screening at age 70 years or older, including African American
men and men with a family history. Counseling an older man who still requests screening
about reduced benefit and increased harms is not an exception that reverses Grade D.
The ERSPC first-round false-positive comparison is strictly older than 70 years versus
younger than 55 years; it is evidence for age-related harm, not a redefinition of the
Grade D age boundary.

African American race and family history increase risk, but the USPSTF found inadequate
evidence for a separate recommendation or a benefit from starting before age 55 years.
The source's reasonable counseling approaches, models suggesting possible earlier
benefit, and probable-benefit family patterns remain risk-informed decision support,
not new USPSTF start ages. Source-printed AUA and ACS guidance addresses earlier
high-risk discussions under those organizations' own boundaries.

The trial interval and biopsy-threshold rows are evidence descriptions. Lower thresholds
and more frequent screening can increase modeled mortality benefit while also increasing
false positives, biopsies, and overdiagnosis. The decision-model finding that every 2 or
4 years may trade less overdiagnosis for a small benefit reduction is not converted into
a USPSTF interval prescription. The source supports no single alternative PSA method
over another. The page-11 1000-man, 13-year table is a preference-sensitive shared-
decision estimate: its linked testing, diagnosis, treatment, harm, and outcome counts are
not predictions for an individual patient or a substitute for the Grade C discussion.

Digital rectal examination is not recommended as a screening modality because screening
benefit evidence is lacking. Its use during active surveillance of already diagnosed
low-risk cancer is a monitoring context, not a contradictory screening recommendation.
Similarly, transrectal ultrasound-guided biopsy follows a positive screen and is
diagnostic rather than an alternative population-screening modality. The generic biopsy
complication list and approximate hospitalization frequency are separate from the ProbE
cohort's 35-day pain, fever, and hematospermia outcomes.

The USPSTF Grade C position differs from source-printed AAFP and Canadian Task Force
recommendations against screening, and from ACP, AUA, and ACS age, life-expectancy,
interval, and discussion boundaries. Each remains organization-specific and is not
merged into a consensus schedule.

## Coverage

The exact recommendation record contains **2 recommendation identifiers**. This sheet
cites both and scopes out none: **2 = 2 cited + 0 scoped**.

ADR 0009 disposition:

- Retained the age 55-to-69 Grade C shared decision, expressed-preference prerequisite,
  informed-decision factors, small value-sensitive net benefit, age-70 Grade D branch,
  older-request counseling, and asymptomatic/no-prior-diagnosis applicability.
- Retained PSA blood testing, positive-result biopsy pathway, DRE screening refusal,
  insufficient evidence for starting average-risk screening before age 55 or obtaining
  a baseline PSA, alternative PSA methods and prebiopsy adjuncts, trial protocol ranges,
  and model-based interval and biopsy-threshold trade-offs without inventing a USPSTF
  PSA cutoff or repeat interval.
- Retained mortality and metastatic benefit magnitudes, absent all-cause mortality
  benefit, false-positive and psychological harms, biopsy hospitalization, overdiagnosis,
  the ProbE 35-day biopsy outcomes, the exact older-than-70 versus younger-than-55
  first-round false-positive comparison, age-amplified harms, surgery and radiation
  complications, and treatment-linked consequences as evidence boundaries. Retained
  every page-11 1000-man, 13-year shared-decision-table count from positive PSA through
  prostate-cancer death avoided.
- Retained the treatment-willingness prerequisite, localized treatment options,
  active-treatment evidence, active-surveillance monitoring, repeated-biopsy and
  later-treatment exposure, and the ProtecT outcome without turning a trial protocol
  into a universal treatment command.
- Retained separate African American and family-history counseling, evidence gaps
  before age 55, age-70 continuity, biopsy-infection evidence, likely-benefit family
  pattern, potential inheritable pattern, and subgroup harm-evidence gaps. Risk language
  does not become a separate USPSTF screening recommendation.
- Retained source-printed AAFP, Canadian Task Force, ACP, AUA, and ACS positions with
  their own ages, life-expectancy, interval, preference, and higher-risk boundaries.
- Burden, prevalence, most site-level trial effects, practice uptake, study sizes,
  confidence intervals, research requests, publication details, disclosures, and
  reference-list numerals were not interpreted as additional patient actions.
