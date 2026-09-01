# Sexually transmitted infection prevention counseling — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source document below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2020 | USPSTF | USPSTF/sti-counseling-final-recommendation-statement | recommendation-statement | 2020 final recommendation | 2020-08-18 | https://doi.org/10.1001/jama.2020.13095 | stated | exact |

## Scope

**Read:** the complete 8-page recommendation statement: recommendation, importance,
and rationale on p. 1; clinician summary, rationale table, and opening practice
considerations on p. 2; risk assessment, counseling interventions, implementation,
resources, related USPSTF recommendations, update, and scope on p. 3; intervention
table and supporting evidence on pp. 4-5; harms, response, research needs,
recommendations of others, and article information on pp. 5-6; and references on
pp. 6-8. Reference-only material is retired by class because it contains citations,
not additional clinical prose.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's decision-point rule:** epidemiologic counts, trial
sample sizes, confidence intervals, heterogeneity statistics, follow-up measurements,
publication dates, author information, and evidence-study schedules that do not change
the population, intervention selection, delivery, benefit-harm boundary, or follow-up
decision. Effect estimates and study characteristics are retained only where the
source uses them to distinguish intervention effectiveness or a decision boundary.

**Source: `uspstf-2020`**

| span | pages | read |
| --- | --- | --- |
| recommendation, importance, and magnitude of net benefit | 1 | yes |
| clinician summary, rationale, and practice considerations | 2 | yes |
| risk assessment, interventions, implementation, resources, related recommendations, update, and review scope | 3 | yes |
| intervention table and supporting evidence | 4 | yes |
| benefits, harms, response, research needs, and recommendations of others | 5-6 | yes |
| article information and disclosures | 6 | read 2026-09-01; blind 2026-09-01 |
| references | 6-8 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| sexually-active-adolescents | all sexually active adolescents |
| adults-increased-sti-risk | adults at increased risk for STIs |
| counseling-eligible-population | all sexually active adolescents and adults at increased risk for STIs |
| adults-for-sti-risk-assessment | adults whose STI risk is being assessed |
| adolescents-for-sexual-activity-assessment | adolescents whose sexual activity is being assessed |
| patients-for-sexual-history | patients whose sexual history is pertinent to STI risk |
| racial-ethnic-groups-with-sti-rate-differences | racial/ethnic groups with observed differences in STI rates |
| increased-risk-counseling-participants | adolescents or adults at increased risk for STIs receiving behavioral counseling |
| nonsexually-active-adolescents-and-adults-not-increased-risk | nonsexually active adolescents and adults not at increased risk for STIs |
| average-sti-risk-adolescents-or-adults | adolescents or adults recruited without respect to individual STI risk factors |
| sti-clinic-patients | persons seeking care for STI symptoms or known or suspected exposure to sex partners with STIs |
| people-experiencing-sexual-violence-or-trafficking | persons experiencing sexual violence, sexual trafficking, or abuse |
| school-aged-youth | school-aged youth |
| men-who-have-sex-with-men | men who have sex with men |
| all-clinical-patients | patients for whom clinicians obtain sexual histories and provide STI risk-reduction counseling or vaccination |
| people-who-have-experienced-sexual-assault | persons who have experienced sexual assault |

## Quantities

| key | verbatim |
| --- | --- |
| behavioral-counseling-recommendation | provision of behavioral counseling to prevent STIs |
| adolescent-risk-classification | STI-risk classification of sexually active adolescents |
| adult-increased-risk-factors | factors identifying adults at increased risk for STIs |
| adult-high-prevalence-populations | populations identified as having high STI prevalence |
| racial-ethnic-sti-rate-context | social-determinants context for racial/ethnic STI-rate differences |
| adolescent-sexual-activity-ascertainment | ascertainment of whether an adolescent is sexually active |
| adult-sti-risk-ascertainment | ascertainment of whether an adult is at increased STI risk |
| sexual-history-ascertainment | routine ascertainment of pertinent sexual history |
| counseling-delivery-options | delivery or referral format for behavioral counseling |
| counseling-core-components | information, motivation, and skills included in counseling |
| group-high-contact-counseling | group counseling with high total contact time |
| brief-single-session-counseling | counseling shorter than 30 minutes in one session |
| intervention-characteristic-uncertainty | independent contribution of tailoring, counselor, and setting characteristics |
| primary-care-implementation | primary care delivery, referral, or media-based implementation |
| behavioral-counseling-benefit | benefit of counseling for STI acquisition |
| behavioral-counseling-harms-bound | upper bound on counseling harms |
| group-counseling-intensity | typical contact time and session duration for group counseling |
| individual-counseling-intensity | typical contact time and sessions for individual counseling |
| media-only-counseling-intensity | typical contact time and sessions for media-only counseling |
| intervention-settings | settings in which counseling was delivered |
| intervention-deliverers | persons or systems delivering counseling |
| pooled-sti-acquisition-effect | pooled reduction in STI acquisition |
| intensity-effect-attribution | whether group format or contact time explains larger effects |
| average-risk-benefit-evidence | evidence of benefit in average-risk populations |
| out-of-population-evidence-gap | benefits and harms outside the recommended population |
| counseling-harm-findings | observed counseling harms |
| durability-evidence-gap | evidence on durability after longer follow-up |
| cdc-implementation-resources | CDC risk-assessment and counseling resources |
| cpstf-community-interventions | Community Preventive Services Task Force community interventions |
| msm-optimal-care-checklist | optimal-care checklist for clinicians serving male patients who have sex with men |
| violence-trafficking-care-boundary | care needs beyond STI-prevention counseling |
| related-uspstf-services | separate USPSTF screening, prevention, and violence recommendations |
| cdc-risk-reduction-guidance | CDC sexual history and risk-reduction guidance |
| cdc-vaccination-guidance | CDC routine HPV and HBV vaccination guidance |
| other-organization-risk-assessment | periodic sexual history, risk assessment, or risk-reduction discussion guidance |
| sexual-assault-sti-care-guidance | STI evaluation and care guidance after sexual assault |
| sti-clinic-counseling-boundary | role of counseling after symptoms, exposure, or a recent/current STI |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| behavioral-counseling-recommendation | counseling-eligible-population | provide behavioral counseling to prevent STIs; Grade B | The USPSTF recommends behavioral counseling for all sexually active adolescents and for adults at increased risk for STIs. | uspstf-2020 | p1 | p1/behavioral-counseling-interventions-to-prevent-s/1 | B |
| behavioral-counseling-benefit | counseling-eligible-population | moderate benefit and moderate net benefit; moderate certainty | RENDERED: The US Preventive Services Task Force (USPSTF) concludes with moderate certainty that behavioral counseling interventions reduce the likelihood of acquiring STIs in sexually active adolescents and in adults at increased risk, resulting in a moderate net benefit. | uspstf-2020 | p1 | p1/narrative/behavioral-counseling-benefit | narrative |
| adolescent-risk-classification | sexually-active-adolescents | all are at increased STI risk and should receive behavioral counseling | RENDERED: All sexually active adolescents are at increased risk for STIs because of the high rates of STIs in this age group and should receive behavioral counseling interventions. | uspstf-2020 | p3 | p3/narrative/adolescent-risk-classification | narrative |
| adult-increased-risk-factors | adults-for-sti-risk-assessment | current STI or STI diagnosed within past year; inconsistent condom use; multiple sex partners; partner in high-prevalence population | Adults at increased risk for STIs include those who currently have an STI or were diagnosed with one within the past year, do not consistently use condoms, have multiple sex partners, or have sex partners within populations with a high prevalence of STIs. | uspstf-2020 | p3 | p3/narrative/adult-increased-risk-factors | narrative |
| adult-high-prevalence-populations | adults-for-sti-risk-assessment | high-prevalence populations include STI testing or clinic attendees, sexual and gender minorities, people living with HIV, people who inject drugs or exchange sex for money or drugs, people entering correctional facilities, and some racial/ethnic minority groups | Populations with a high prevalence of STIs include persons who seek STI testing or attend STI clinics; sexual and gender minorities; persons who are living with HIV, inject drugs, have exchanged sex for money or drugs, or have entered correctional facilities; and some racial/ethnic minority groups. | uspstf-2020 | p3 | p3/narrative/adult-high-prevalence-populations | narrative |
| racial-ethnic-sti-rate-context | racial-ethnic-groups-with-sti-rate-differences | differences may reflect social determinants of health and are context, not an automatic eligibility rule | Difference in STI rates among racial/ethnic groups may reflect differences in social determinants of health. | uspstf-2020 | p3 | p3/narrative/racial-ethnic-sti-rate-context | narrative |
| adolescent-sexual-activity-ascertainment | adolescents-for-sexual-activity-assessment | assess whether the adolescent is sexually active | RENDERED: Assess whether adolescents are sexually active and, for adults, assess risk for STIs. | uspstf-2020 | p2 | p2/narrative/adolescent-sexual-activity-ascertainment | narrative |
| adult-sti-risk-ascertainment | adults-for-sti-risk-assessment | assess adult risk for STIs | RENDERED: Assess whether adolescents are sexually active and, for adults, assess risk for STIs. | uspstf-2020 | p2 | p2/narrative/adult-sti-risk-ascertainment | narrative |
| sexual-history-ascertainment | patients-for-sexual-history | routinely ask pertinent sexual-history questions to determine adolescent sexual activity and adult risk activities | RENDERED: To determine which adolescents are sexually active, and which adults might engage in activities that may increase their risk for STIs, clinicians should routinely ask their patients for pertinent information about their sexual history. | uspstf-2020 | p3 | p3/narrative/sexual-history-ascertainment | narrative |
| counseling-delivery-options | increased-risk-counseling-participants | in-person counseling, videos, websites, written materials, telephone support, or text messages | RENDERED: Intervention approaches include in-person counseling, videos, websites, written materials, telephone support, and text messages. | uspstf-2020 | p3 | p3/narrative/counseling-delivery-options | narrative |
| counseling-core-components | increased-risk-counseling-participants | give STI/transmission information; assess personal risk; increase motivation or commitment to safer sex; train condom use, safer-sex communication, problem solving, and other pertinent skills | RENDERED: Most successful approaches provide information on common STIs and STI transmission; assess the person's risk for acquiring STIs; aim to increase motivation or commitment to safer sex practices; and provide training in condom use, communication about safer sex, problem solving, and other pertinent skills. | uspstf-2020 | p3 | p3/narrative/counseling-core-components | narrative |
| group-high-contact-counseling | increased-risk-counseling-participants | more than 120 minutes, usually multiple sessions; associated with larger STI-prevention effects | RENDERED: Interventions that include group counseling and involve high total contact times (defined in the evidence review as more than 120 minutes), often delivered over multiple sessions, are associated with larger STI prevention effects. | uspstf-2020 | p3 | p3/narrative/group-high-contact-counseling | narrative |
| brief-single-session-counseling | increased-risk-counseling-participants | shorter than 30 minutes, generally one session; some less-intensive interventions reduced STI acquisition, increased condom use, or decreased sex-partner number | RENDERED: However, some less intensive interventions have been shown to reduce STI acquisition, increase condom use, or decrease number of sex partners. Interventions shorter than 30 minutes tended to be delivered in a single session. | uspstf-2020 | p3 | p3/narrative/brief-single-session-counseling | narrative |
| intervention-characteristic-uncertainty | increased-risk-counseling-participants | insufficient evidence that cultural tailoring, counselor characteristics, or setting independently determines effectiveness | RENDERED: There is not enough evidence to determine whether several intervention characteristics were independently related to effectiveness, including degree of cultural tailoring, counselor characteristics, or setting. | uspstf-2020 | p3 | p3/narrative/intervention-characteristic-uncertainty | narrative |
| primary-care-implementation | counseling-eligible-population | primary care clinician may counsel in person, refer to counseling elsewhere, or inform about media-based interventions | RENDERED: Primary care clinicians can deliver in-person behavioral counseling interventions, refer patients to behavioral counseling interventions in other settings, or inform patients about media-based interventions. | uspstf-2020 | p3 | p3/narrative/primary-care-implementation | narrative |
| cdc-implementation-resources | counseling-eligible-population | EXTERNAL (CDC): primary-care STI risk-assessment tool, behavioral-counseling and STI-prevention information, and a compendium of interventions shown to reduce STI acquisition or increase safer sexual behavior | RENDERED: The Centers for Disease Control and Prevention (CDC) provides a tool for STI risk assessment suitable for primary care settings; provides information about behavioral counseling and other STI prevention strategies; and maintains a compendium of evidence-based behavioral counseling interventions that have been shown to reduce STI acquisition or increase safer sexual behaviors. | uspstf-2020 | p3 | p3/narrative/cdc-implementation-resources | narrative |
| cpstf-community-interventions | school-aged-youth | EXTERNAL (Community Preventive Services Task Force): effective individual- and group-level community interventions for HIV, other STIs, and teen-pregnancy prevention | RENDERED: The Community Preventive Services Task Force has issued recommendations on preventing HIV, other STIs, and teen pregnancy and has described effective individual- and group-level community interventions for school-aged youth | uspstf-2020 | p3 | p3/narrative/cpstf-school-aged-community-interventions | narrative |
| cpstf-community-interventions | men-who-have-sex-with-men | EXTERNAL (Community Preventive Services Task Force): effective individual- and group-level community interventions for men who have sex with men | RENDERED: The Community Preventive Services Task Force has issued recommendations on preventing HIV, other STIs, and teen pregnancy and has described effective individual- and group-level community interventions for school-aged youth and for men who have sex with men. | uspstf-2020 | p3 | p3/narrative/cpstf-msm-community-interventions | narrative |
| msm-optimal-care-checklist | men-who-have-sex-with-men | EXTERNAL (National Coalition of Sexually Transmitted Disease Directors and National Alliance of State and Territorial AIDS Directors): optimal-care checklist available to clinicians serving male patients who have sex with men | RENDERED: The National Coalition of Sexually Transmitted Disease Directors and the National Alliance of State and Territorial AIDS Directors have developed optimal care checklists for clinicians serving male patients who have sex with men. | uspstf-2020 | p3 | p3/narrative/msm-optimal-care-checklist | narrative |
| violence-trafficking-care-boundary | people-experiencing-sexual-violence-or-trafficking | helping in these situations goes beyond STI-prevention counseling; the statement links relevant CDC resources | RENDERED: persons in this situation, which goes beyond counseling on how to prevent STIs. The USPSTF added a link to relevant resources provided by the CDC in the Additional Tools and Resources section. | uspstf-2020 | p6 | p6/narrative/violence-trafficking-care-boundary | narrative |
| related-uspstf-services | counseling-eligible-population | separate USPSTF recommendations address chlamydia, gonorrhea, syphilis, HIV, HBV, and HPV screening; cervical-cancer screening; HIV preexposure prophylaxis; and intimate-partner-violence and elder-abuse screening | RENDERED: The USPSTF has issued several recommendations about screening for STIs (chlamydia, gonorrhea, syphilis, HIV, HBV, and HPV) and cervical cancer and offering preexposure prophylaxis to prevent HIV acquisition. The USPSTF has also issued a recommendation on screening for intimate partner violence and elder abuse. | uspstf-2020 | p3 | p3/narrative/related-uspstf-services | narrative |
| group-counseling-intensity | increased-risk-counseling-participants | RENDERED table: more than 120 minutes over multiple sessions during 1 to 12 months | RENDERED: Most interventions with group counseling involved total contact times of more than 120 min and multiple sessions over 1 to 12 mo | uspstf-2020 | p4 | p4/narrative/group-counseling-intensity | narrative |
| individual-counseling-intensity | increased-risk-counseling-participants | RENDERED table: more than 30 minutes total, generally one session | RENDERED: Most individual counseling interventions involved more than 30 min of total contact time and a single session | uspstf-2020 | p4 | p4/narrative/individual-counseling-intensity | narrative |
| media-only-counseling-intensity | increased-risk-counseling-participants | RENDERED table: about half lasted 30 to 90 minutes and others less than 30 minutes; video/computer used fewer sessions than repeated texts/emails over months | RENDERED: Approximately one-half of media-only interventions involved total contact times of 30 to 90 min; others involved less than 30 min. Interventions involving video or computer interaction entailed fewer sessions than those involving repeated text messages or emails over many months. | uspstf-2020 | p4 | p4/narrative/media-only-counseling-intensity | narrative |
| intervention-settings | increased-risk-counseling-participants | RENDERED table: primary care, research, or STI clinics; homes, communities, or STI-clinic waiting areas for persons identified in STI, primary care, family-planning, prenatal, and obstetrics-gynecology settings or through advertisements or community media | RENDERED: Primary care clinics, research clinics, or STI clinics. Persons identified at STI, primary care, family planning, prenatal, and obstetrics-gynecology clinics or through advertisements or community media received interventions in homes, their community, or STI clinic waiting areas. | uspstf-2020 | p4 | p4/narrative/intervention-settings | narrative |
| intervention-deliverers | increased-risk-counseling-participants | RENDERED table: researchers, facilitators, nursing professionals, counselors, health educators, trained peers, or clinicians; media interventions were self-directed or passively received | RENDERED: Researchers, facilitators, nursing professionals, counselors, health educators, trained peer counselors, or clinicians delivered group and individual counseling. Self-directed (such as interactive computer-based intervention) or passively received (such as video). | uspstf-2020 | p4 | p4/narrative/intervention-deliverers | narrative |
| sti-clinic-counseling-boundary | sti-clinic-patients | after symptoms, known or suspected exposure, or a recent/current STI, counseling may focus on preventing a subsequent STI, including reinfection by untreated partners | RENDERED: Studies in STI clinics tested interventions in persons who had sought care for STI symptoms or had known or suspected exposure to sex partners with STIs. Interventions for STI clinic patients with recent or current STIs often focus on reducing the risk for a subsequent STI, including those caused by reinfection by untreated partners. | uspstf-2020 | p4 | p4/narrative/sti-clinic-counseling-boundary | narrative |
| pooled-sti-acquisition-effect | increased-risk-counseling-participants | about 30% reduction in STI acquisition across pooled trials | RENDERED: Behavioral counseling interventions were effective for reducing STI acquisition by approximately 30% based on pooled analysis of 19 trials in persons at increased risk for STIs | uspstf-2020 | p5 | p5/narrative/pooled-sti-acquisition-effect | narrative |
| intensity-effect-attribution | increased-risk-counseling-participants | group counseling and more than 120 minutes had stronger effects, but their independent contributions were unclear | RENDERED: Sexually transmitted infection prevention effects were stronger for interventions involving group counseling than for interventions without group counseling. Effects were also stronger for interventions with high total contact times (>120 minutes). However, it was unclear whether group counseling format, contact time, or both were responsible for intervention effects because all but 1 group counseling intervention entailed more than 120 minutes. | uspstf-2020 | p5 | p5/narrative/intensity-effect-attribution | narrative |
| average-risk-benefit-evidence | average-sti-risk-adolescents-or-adults | four trials found no significant STI-acquisition effect; one early-adolescent family intervention reduced self-reported vaginal intercourse | RENDERED: Four trials evaluated behavioral counseling interventions in adults or adolescents at average STI risk who were recruited without respect to individual STI risk factors from primary care clinics (3 trials) or through community advertising (1 trial). None reported significant effects on STI acquisition. One trial found a significant effect on self-reported sexual behavior in adolescents aged 11 to 14 years. After 9 months of follow-up, adolescents in the intervention group were less likely to report vaginal intercourse than adolescents offered usual care. | uspstf-2020 | p5 | p5/narrative/average-risk-benefit-evidence | narrative |
| out-of-population-evidence-gap | nonsexually-active-adolescents-and-adults-not-increased-risk | evidence lacking on benefits and harms | RENDERED: The USPSTF continues to conclude that the current evidence is lacking on the benefits and harms of behavioral counseling to prevent STIs in nonsexually active adolescents and in adults not at increased risk for STIs. | uspstf-2020 | p3 | p3/narrative/out-of-population-evidence-gap | narrative |
| counseling-harm-findings | increased-risk-counseling-participants | no significant harms reported; no consistent evidence of increased adolescent sexual activity, unintended pregnancy, shame/stigma, or mental-health problems | RENDERED: None of these trials reported significant harms. There was no consistent evidence that interventions increased sexual activity in adolescents, unintended pregnancy, perceptions of shame or stigma, or mental health problems. | uspstf-2020 | p5 | p5/narrative/counseling-harm-findings | narrative |
| behavioral-counseling-harms-bound | counseling-eligible-population | no greater than small | Evidence is adequate to bound the magnitude of the overall harms of interventions as no greater than small | uspstf-2020 | p2 | p2/narrative/behavioral-counseling-harms-bound | narrative |
| durability-evidence-gap | increased-risk-counseling-participants | longer than 12 months of follow-up is needed to assess durability | Trials that follow up participants for longer than 12 months are needed to assess the durability of intervention effects. | uspstf-2020 | p6 | p6/narrative/durability-evidence-gap | narrative |
| cdc-risk-reduction-guidance | all-clinical-patients | EXTERNAL (CDC): routinely obtain sexual history and encourage abstinence, condom use, limiting sex-partner number, and other sexual risk-reduction strategies | The CDC recommends that all clinicians routinely obtain a sexual history and encourage abstinence, condom use, limiting number of sex partners, and other sexual risk-reduction strategies | uspstf-2020 | p6 | p6/narrative/cdc-risk-reduction-guidance | narrative |
| cdc-vaccination-guidance | all-clinical-patients | EXTERNAL (CDC): routine vaccination against HPV and HBV infection | RENDERED: as well as routine vaccination against HPV and HBV infection. | uspstf-2020 | p6 | p6/narrative/cdc-vaccination-guidance | narrative |
| other-organization-risk-assessment | all-clinical-patients | EXTERNAL (American Academy of Pediatrics, American Academy of Family Physicians, American College of Obstetricians and Gynecologists, Society for Adolescent Health and Medicine, National Coalition of Sexually Transmitted Disease Directors, National Alliance of State and Territorial AIDS Directors, and National Health Care for the Homeless Council): periodically obtain sexual histories, conduct sexual-risk assessments, discuss sexual-risk reduction, or combine these actions | RENDERED: Many organizations advise clinicians to periodically obtain sexual histories, conduct sexual risk assessments, discuss sexual risk reduction, or some combination thereof; these organizations include the American Academy of Pediatrics, the American Academy of Family Physicians, the American College of Obstetricians and Gynecologists, the Society for Adolescent Health and Medicine, the National Coalition of Sexually Transmitted Disease Directors and the National Alliance of State and Territorial AIDS Directors, and the National Health Care for the Homeless Council. | uspstf-2020 | p6 | p6/narrative/other-organization-risk-assessment | narrative |
| sexual-assault-sti-care-guidance | people-who-have-experienced-sexual-assault | EXTERNAL (Sexual Assault Forensic Examiner Technical Assistance Organization/SAFEta): guidance addresses STI evaluation and care after sexual assault, not STI-prevention counseling directly | RENDERED: Although it does not address STI prevention counseling directly, the Sexual Assault Forensic Examiner Technical Assistance Organization provides guidance on how to evaluate and provide STI care to persons who have experienced sexual assault. | uspstf-2020 | p6 | p6/narrative/sexual-assault-sti-care-guidance | narrative |

## Conflicts

No unresolved same-population, same-quantity machine conflict was identified. Counseling
format and intensity are retained as distinct quantities because the source does not set
one mandatory duration. Group counseling and high total contact time of more than 120
minutes were associated with the strongest effects and generally used multiple sessions,
but some interventions shorter than 30 minutes also reduced STI acquisition or promoted
safer sexual behavior. The source explicitly says whether group format, contact time, or
both explains the larger effect is unclear.

The USPSTF Grade B counseling recommendation is distinct from its related screening,
HIV-prevention, and violence-screening recommendations. Counseling after a recent or
current STI addresses prevention of a subsequent infection and does not replace clinical
evaluation or treatment. CDC, Community Preventive Services Task Force, professional-
organization, coalition, and SAFEta rows are source-described external guidance or
resources, retain their named provenance, and do not become USPSTF recommendations.

## Coverage

Exact recommendation accounting: **1 = 1 cited + 0 scoped out**.

ADR 0009 disposition:

- retained the exact Grade B recommendation and its two eligibility limbs: all sexually
  active adolescents and adults at increased risk for STIs;
- retained separate adolescent sexual-activity ascertainment and adult STI-risk
  ascertainment, the adult behavioral risk factors, the high-prevalence population list,
  and the separate social-determinants caveat without treating race or ethnicity alone as
  an automatic eligibility rule;
- retained counseling delivery options, information/motivation/skills components,
  primary-care delivery and referral choices, group, individual, and media intensity
  patterns, settings, deliverers, and the uncertainty about which intervention feature
  independently explains effectiveness;
- retained moderate benefit and net benefit, the pooled STI-acquisition effect, the
  no-greater-than-small harm bound, observed harm findings, average-risk and out-of-
  population evidence limits, and the longer-than-12-month durability research need;
- retained the boundary between prevention counseling and separate STI screening,
  diagnostic/treatment care, HIV preexposure prophylaxis, and violence-related care;
- retained CDC implementation resources, Community Preventive Services Task Force
  community interventions, coalition checklists, CDC risk-reduction and vaccination
  guidance, other organizations' risk-assessment guidance, sexual-assault care guidance,
  and violence/trafficking resources only with explicit external provenance;
- excluded annual national case counts, trial sample sizes, odds ratios, confidence
  intervals, heterogeneity values, isolated study follow-up schedules, demographic trial
  composition, publication dates, author/disclosure data, public-comment dates, and
  reference-list numbers when they did not change eligibility, counseling selection,
  delivery, benefit-harm interpretation, or a clinical boundary.
