# Skin cancer prevention counseling — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the source document below. **Not a substitute
for the guideline** and not a clinical instruction: every row is a fact this repo
restates, and choosing among them is the clinician's. Graded by
`tools/threshold_sheet.py`; what that grader cannot see is written out in
[README.md](README.md).

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2018 | USPSTF | USPSTF/skin-cancer-counseling-final-recommendation | recommendation-statement | 2018 final recommendation | 2018-03-20 | https://doi.org/10.1001/jama.2018.1623 | stated | exact |

## Scope

**Read:** the complete 9-page recommendation statement: all three recommendations,
rationale, risk assessment, counseling components, and applicability on pp. 1-3;
delivery modalities, self-examination considerations, external resources, and
implementation on pp. 3-5; effectiveness, behavior-to-cancer evidence, harms, net
benefit, and update on pp. 5-7; recommendations of others and article information on
p. 8; and references on pp. 8-9.

**Not read:** nothing in the source page range.

**Scoped out under ADR 0009's decision-point rule:** disease-incidence and mortality
counts, trial sample sizes, effect estimates, confidence statistics, publication and
comment dates, author information, and study-only follow-up measurements that do not
change counseling eligibility, a protection behavior, delivery choice, benefit-harm
interpretation, or a prevention-versus-screening boundary. Study formats and timing are
retained when the source uses them to describe implementable counseling modalities.

**Source: `uspstf-2018`**

| span | pages | read |
| --- | --- | --- |
| exact recommendations, findings, rationale, risks, benefits, harms, and applicability | 1-3 | yes |
| counseling delivery, self-examination considerations, resources, and implementation | 3-5 | yes |
| effectiveness, exposure evidence, harms, net benefit, and recommendation update | 5-7 | yes |
| recommendations of others | 8 | yes |
| article information and disclosures | 8 | read 2026-09-01; blind 2026-09-01 |
| references | 8-9 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| fair-skin-age-6-months-to-24-years | asymptomatic persons aged 6 months to 24 years with fair skin types and no history of skin cancer |
| fair-skin-adults-older-than-24 | asymptomatic adults older than 24 years with fair skin types and no history of skin cancer |
| adults-for-self-exam-counseling | asymptomatic adults without a history of skin cancer for whom counseling about skin self-examination is considered |
| asymptomatic-no-skin-cancer-history | asymptomatic persons without a history of skin cancer |
| persons-with-fair-skin-types | persons with ivory or pale skin, light eyes, red or blond hair, freckles, or skin that sunburns easily |
| older-fair-skin-adults-for-selective-counseling | asymptomatic adults older than 24 years with fair skin types and no history of skin cancer, for whom additional risk factors inform selective counseling |
| persons-with-previous-skin-cancer | persons with a personal history of skin cancer, outside the stated asymptomatic/no-history applicability population |
| persons-without-fair-skin-types | persons without fair skin types, for whom counseling evidence was insufficient |
| counseling-eligible-young-persons-and-parents | young adults, adolescents, children, and parents of young children within the age and fair-skin recommendation population |
| parents-of-eligible-young-children | parents of young children within the fair-skin, age-6-months-to-24-years recommendation population |
| children-adolescents-counseling-evidence | children and adolescents represented in counseling studies, most with parent-directed interventions |
| young-adult-counseling-evidence | young adults represented in counseling studies |
| older-adult-counseling-evidence | adults older than 24 years represented in counseling studies |
| children-in-well-child-counseling-studies | children whose parent-directed counseling interventions were delivered with well-child visits |
| children-and-parents-in-counseling-studies | children and parents represented in evidence-described tailored print and in-person counseling interventions |
| parents-and-children-in-one-day-trial | parents and children represented in the one-day, in-person parent-education trial; the source passage does not state the children's ages |
| parents-of-children-age-3-or-younger | parents of children aged 3 years or younger represented in implementation trials |
| children-age-3-to-10-and-parents | children aged 3 to 10 years and their parents represented in implementation trials |
| adolescents-in-counseling-trial | adolescents represented in the clinician and telephone-counseling trial |
| young-adults-age-18-to-25 | young adults aged 18 to 25 years in a web-based counseling study |
| adults-using-sunscreen | adults using sunscreen for skin-cancer prevention |
| women-younger-than-50-who-indoor-tan | women younger than 50 years with indoor-tanning exposure |
| persons-with-indoor-tanning-exposure | persons with indoor-tanning exposure |
| all-persons-for-aad-self-exam | everyone addressed by American Academy of Dermatology self-examination guidance |
| persons-for-monthly-self-exam-guidance | persons addressed by American Cancer Society and Skin Cancer Foundation monthly self-examination guidance |
| patients-for-external-prevention-counseling | patients addressed by external organizations' skin-cancer prevention counseling guidance |
| children-and-communities-for-cpstf | children and community members in child-care, school, recreational, occupational, or community-wide settings |
| patients-and-clinicians-using-fda-guidance | patients and clinicians using FDA sunscreen and indoor-tanning information |
| people-using-epa-sun-safety-tools | people using Environmental Protection Agency sun-safety tools |

## Quantities

| key | verbatim |
| --- | --- |
| young-person-uv-counseling | counseling to minimize UV exposure in the younger fair-skin population |
| parent-young-child-uv-counseling | counseling parents to minimize UV exposure for eligible young children |
| older-adult-uv-counseling | selective counseling to minimize UV exposure in older adults with fair skin |
| adult-self-exam-counseling-evidence | benefit-harm evidence for counseling adults about skin self-examination |
| source-applicability | symptom and skin-cancer-history applicability boundary |
| fair-skin-definition | fair-skin features used for recommendation eligibility |
| additional-risk-assessment | additional factors used in older-adult selective-counseling decisions |
| previous-skin-cancer-boundary | personal skin-cancer history as risk context outside source applicability |
| non-fair-skin-evidence-gap | evidence boundary for persons without fair skin types |
| sun-protection-components | behaviors targeted by UV-exposure counseling |
| younger-counseling-benefit | benefit magnitude in the younger recommendation population |
| older-counseling-benefit | benefit magnitude in adults older than 24 years |
| younger-counseling-net-benefit | net-benefit magnitude in the younger recommendation population |
| older-counseling-net-benefit | net-benefit magnitude in adults older than 24 years |
| counseling-harm-bound | harm magnitude for counseling and sun-protection behaviors |
| self-exam-benefit-gap | evidence gap for benefits of self-examination counseling |
| self-exam-harm-evidence-gap | evidence adequacy for harms of self-examination counseling |
| self-exam-potential-harms | potential psychosocial and biopsy harms following self-examination counseling |
| child-parent-delivery-modalities | source-described child and parent counseling formats |
| well-child-delivery-evidence | evidence-described delivery with well-child visits |
| tailored-child-print-features | evidence-described tailoring of child print materials |
| child-in-person-provider-types | evidence-described in-person counseling provider types |
| adult-delivery-modalities | source-described young-adult and adult counseling formats |
| adult-effective-intervention-modifiers | evidence-described features more common in effective adult interventions |
| young-child-implementation | source-described intervention for children aged 3 years or younger |
| child-mailing-implementation | source-described mail intervention for children aged 3 to 10 years |
| parent-session-implementation | source-described one-day parent education intervention |
| adolescent-implementation | source-described adolescent counseling and follow-up pattern |
| young-adult-web-implementation | source-described web-program age, module, and duration pattern |
| sunscreen-skin-reactions | transient skin reactions associated with sunscreen |
| sunscreen-vitamin-d-harm-evidence | evidence on sunscreen and vitamin D levels |
| sun-protection-activity-harm-evidence | evidence on physical activity and body mass index |
| sunscreen-false-reassurance-evidence | evidence on sunscreen use and increased sun exposure or sunburn |
| self-exam-procedure-harm | procedures and overdiagnosis associated with self-examination |
| indoor-tanning-risk-thresholds | age, frequency, and duration boundaries linked to cancer risk |
| sunscreen-protective-evidence | evidence connecting routine sunscreen use with skin-cancer outcomes |
| minimum-sunscreen-age-rationale | source rationale for the lower counseling age boundary |
| related-uspstf-skin-screening | separate USPSTF skin-cancer screening recommendation |
| fda-sunscreen-use | external FDA sunscreen selection and reapplication guidance |
| fda-indoor-tanning-resource | external FDA indoor-tanning education resource |
| epa-sun-safety-resources | external EPA sun-safety information and UV tools |
| cpstf-setting-interventions | external CPSTF setting and community prevention interventions |
| external-clinician-counseling | external organizations endorsing clinician prevention counseling |
| aad-self-examination | external AAD self-examination guidance |
| monthly-self-examination | external ACS and Skin Cancer Foundation self-examination frequency |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| young-person-uv-counseling | fair-skin-age-6-months-to-24-years | counsel young adults, adolescents, children, and parents of young children to minimize UV exposure; Grade B | The USPSTF recommends counseling young adults, adolescents, children, and parents of young children about minimizing exposure to UV radiation for persons aged 6 months to 24 years with fair skin types to reduce their risk of skin cancer. | uspstf-2018 | p1 | p1/behavioral-counseling-to-prevent-skin-cancer/1 | B |
| parent-young-child-uv-counseling | parents-of-eligible-young-children | counsel parents about minimizing their eligible young child's exposure to UV radiation; Grade B | The USPSTF recommends counseling young adults, adolescents, children, and parents of young children about minimizing exposure to UV radiation for persons aged 6 months to 24 years with fair skin types to reduce their risk of skin cancer. | uspstf-2018 | p1 | p1/behavioral-counseling-to-prevent-skin-cancer/1 | B |
| older-adult-uv-counseling | fair-skin-adults-older-than-24 | selectively offer counseling to minimize UV exposure; net benefit of counseling everyone is small; consider individual skin-cancer risk factors; Grade C | The USPSTF recommends that clinicians selectively offer counseling to adults older than 24 years with fair skin types about minimizing their exposure to UV radiation to reduce risk of skin cancer. Existing evidence indicates that the net benefit of counseling all adults older than 24 years is small. In determining whether this service is appropriate in individual cases, patients and clinicians should consider the presence of risk factors for skin cancer. | uspstf-2018 | p1 | p1/behavioral-counseling-to-prevent-skin-cancer/2 | C |
| adult-self-exam-counseling-evidence | adults-for-self-exam-counseling | evidence insufficient to assess benefits and harms; I statement | The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of counseling adults about skin self-examination to prevent skin cancer. | uspstf-2018 | p1 | p1/behavioral-counseling-to-prevent-skin-cancer/3 | I |
| source-applicability | asymptomatic-no-skin-cancer-history | applies to asymptomatic persons without a history of skin cancer | This recommendation applies to asymptomatic persons without a history of skin cancer | uspstf-2018 | p2 | p2/narrative/source-applicability | narrative |
| fair-skin-definition | persons-with-fair-skin-types | ivory or pale skin, light eye color, red or blond hair, freckles, or skin that sunburns easily | Persons with fair skin types (ivory or pale skin, light eye color, red or blond hair, freckles, those who sunburn easily) are at increased risk of skin cancer and should be counseled. | uspstf-2018 | p3 | p3/narrative/fair-skin-definition | narrative |
| additional-risk-assessment | older-fair-skin-adults-for-selective-counseling | in the Grade C selective-counseling decision, consider sunburn history, previous indoor-tanning use, family history, increased or atypical nevi, HIV, or organ-transplant history; personal skin-cancer history remains outside the recommendation's stated applicability | RENDERED: Other factors that further increase risk include a history of sunburns, previous use of indoor tanning beds, and a family or personal history of skin cancer. Persons with an increased number of nevi and atypical nevi are at increased risk of melanoma. Persons with a compromised immune system (eg, persons living with HIV, persons who have received an organ transplant) are at increased risk of skin cancer. | uspstf-2018 | p3 | p3/narrative/additional-risk-assessment | narrative |
| previous-skin-cancer-boundary | persons-with-previous-skin-cancer | personal skin-cancer history is listed as increased-risk context | RENDERED: Other factors that further increase risk include a history of sunburns, previous use of indoor tanning beds, and a family or personal history of skin cancer. | uspstf-2018 | p3 | p3/narrative/previous-skin-cancer-risk-context | narrative |
| non-fair-skin-evidence-gap | persons-without-fair-skin-types | counseling evidence is insufficient for inclusion in the recommendation | As in 2012, the evidence on persons without a fair skin type remains insufficient for this population to be included in the recommendation statement. | uspstf-2018 | p7 | p7/narrative/non-fair-skin-evidence-gap | narrative |
| sun-protection-components | fair-skin-age-6-months-to-24-years | use broad-spectrum sunscreen with SPF at least 15; wear hats, sunglasses, and protective clothing; avoid sun exposure; seek shade from 10 AM to 4 PM; avoid indoor tanning | RENDERED: Behavioral counseling interventions target sun protection behaviors to reduce UV radiation exposure, including use of broad-spectrum sunscreen with a sun-protection factor of 15 or greater; wearing hats, sunglasses, or sun-protective clothing; avoiding sun exposure; seeking shade during midday hours (10 AM to 4 PM); and avoiding indoor tanning use. | uspstf-2018 | p4 | p4/narrative/sun-protection-components | narrative |
| sun-protection-components | fair-skin-adults-older-than-24 | use broad-spectrum sunscreen with SPF at least 15; wear hats, sunglasses, and protective clothing; avoid sun exposure; seek shade from 10 AM to 4 PM; avoid indoor tanning | RENDERED: Behavioral counseling interventions target sun protection behaviors to reduce UV radiation exposure, including use of broad-spectrum sunscreen with a sun-protection factor of 15 or greater; wearing hats, sunglasses, or sun-protective clothing; avoiding sun exposure; seeking shade during midday hours (10 AM to 4 PM); and avoiding indoor tanning use. | uspstf-2018 | p4 | p4/narrative/sun-protection-components-older-adults | narrative |
| younger-counseling-benefit | fair-skin-age-6-months-to-24-years | moderate increase in sun-protection behavior | RENDERED: The USPSTF found adequate evidence that behavioral counseling interventions available in or referable from a primary care setting result in a moderate increase in the use of sun protection behaviors for persons aged 6 months to 24 years with fair skin types. | uspstf-2018 | p2 | p2/narrative/younger-counseling-benefit | narrative |
| older-counseling-benefit | fair-skin-adults-older-than-24 | small increase in sun-protection behavior | RENDERED: The USPSTF found adequate evidence that behavioral counseling interventions available in or referable from a primary care setting result in a small increase in the use of sun protection behaviors for persons older than 24 years with fair skin types. | uspstf-2018 | p2 | p2/narrative/older-counseling-benefit | narrative |
| younger-counseling-net-benefit | fair-skin-age-6-months-to-24-years | moderate net benefit | RENDERED: The USPSTF concludes with moderate certainty that behavioral counseling interventions have a moderate net benefit for young adults, adolescents, and children aged 6 months to 24 years with fair skin types. | uspstf-2018 | p2 | p2/narrative/younger-counseling-net-benefit | narrative |
| older-counseling-net-benefit | fair-skin-adults-older-than-24 | small benefit | RENDERED: The USPSTF concludes with moderate certainty that behavioral counseling interventions have a small benefit in adults older than 24 years with fair skin types. | uspstf-2018 | p2 | p2/narrative/older-counseling-net-benefit | narrative |
| counseling-harm-bound | asymptomatic-no-skin-cancer-history | counseling and sun-protection behavior harms are small | RENDERED: The USPSTF found adequate evidence that the harms related to behavioral counseling interventions and sun protection behaviors in young persons or adults are small. | uspstf-2018 | p2 | p2/narrative/counseling-harm-bound | narrative |
| self-exam-benefit-gap | adults-for-self-exam-counseling | counseling increases reported examinations, but benefit is uncertain because links to cancer or other health outcomes and incremental benefit beyond sun-protection counseling and current clinician examinations are unproven | RENDERED: Counseling adults about performing skin self-examination appears to result in an increase of such examinations. The potential benefit of behavioral counseling about skin self-examination is uncertain because of the lack of evidence on the link between behavior change and skin cancer or other health outcomes. In addition, there is no evidence about the incremental benefit that might occur with skin self-examination above the benefit from counseling for sun protection behaviors and from current levels of skin examinations being performed by clinicians. | uspstf-2018 | p4 | p4/narrative/self-exam-benefit-gap | narrative |
| self-exam-harm-evidence-gap | adults-for-self-exam-counseling | evidence regarding harms of counseling adults about skin self-examination is inadequate | RENDERED: The USPSTF found inadequate evidence regarding the harms of counseling adults about skin self-examination. | uspstf-2018 | p2 | p2/narrative/self-exam-harm-evidence-gap | narrative |
| self-exam-potential-harms | adults-for-self-exam-counseling | possible anxiety or cancer worry; biopsy may cause pain, bleeding, scarring, or infection | RENDERED: Psychosocial harms, such as anxiety or cancer worry, are possible. If skin self-examination leads to biopsy, procedural harms such as pain, bleeding, scarring, or infection could occur. | uspstf-2018 | p4 | p4/narrative/self-exam-potential-harms | narrative |
| child-parent-delivery-modalities | children-adolescents-counseling-evidence | evidence-described interventions focused on sun protection; most were parent-directed, some provided child-specific materials or messages, and half included face-to-face counseling | RENDERED: All studies conducted in children and adolescents focused on sun protection behaviors; most were directed at parents, and some provided child-specific materials or messages. Half of the interventions included face-to-face counseling. | uspstf-2018 | p3 | p3/narrative/child-parent-delivery-modalities | narrative |
| well-child-delivery-evidence | children-in-well-child-counseling-studies | evidence-described delivery in three studies occurred with well-child visits | RENDERED: Three studies provided the intervention in conjunction with well-child visits. | uspstf-2018 | p4 | p4/narrative/well-child-delivery-evidence | narrative |
| adult-delivery-modalities | young-adult-counseling-evidence | mail, face-to-face or telephone counseling, text messages, online programs or modules, and personal UV facial photographs | RENDERED: The mode of delivery varied and included mail-based, face-to-face or telephone counseling, and technology-based (text messages, online programs and modules, personal UV facial photographs) interventions. | uspstf-2018 | p4 | p4/narrative/adult-delivery-modalities | narrative |
| tailored-child-print-features | children-and-parents-in-counseling-studies | evidence-described print materials were sometimes tailored to the child's risk level, barriers to change, self-efficacy, or other factors | RENDERED: Some print-based interventions included materials tailored to the child's risk level, barriers to change, self-efficacy, or other factors. | uspstf-2018 | p5 | p5/narrative/tailored-child-print-features | narrative |
| child-in-person-provider-types | children-and-parents-in-counseling-studies | evidence-described in-person counseling was provided by primary care clinicians or health educators | RENDERED: Health professionals providing in-person counseling included primary care clinicians and health educators. | uspstf-2018 | p5 | p5/narrative/child-in-person-provider-types | narrative |
| young-child-implementation | parents-of-children-age-3-or-younger | evidence-described clinician counseling and parent print materials with sunscreen samples and a hat | RENDERED: One trial of an intervention involving children 3 years and younger used clinician counseling and print materials for parents promoting child sun protection with sun protection aids (sunscreen samples and hat). | uspstf-2018 | p5 | p5/narrative/young-child-implementation | narrative |
| child-mailing-implementation | children-age-3-to-10-and-parents | evidence-described standard or tailored mailings over 1 to 36 months | Several trials in children aged 3 to 10 years used standard or tailored mailings over 1 to 36 months. | uspstf-2018 | p5 | p5/narrative/child-mailing-implementation | narrative |
| parent-session-implementation | parents-and-children-in-one-day-trial | evidence-described 1-day, in-person parent education with a children's video, print materials, shirt, hat, and sunscreen | RENDERED: One trial used a 1-day, in-person parent education session with a children's video, print materials, and sun protection aids (shirt, hat, and sunscreen). | uspstf-2018 | p5 | p5/narrative/parent-session-implementation | narrative |
| adolescent-implementation | adolescents-in-counseling-trial | evidence-described direct clinician counseling plus 4 follow-up calls from a health educator over 18 months, mailed material, and sunscreen samples | RENDERED: For the single study in adolescents, clinicians directly counseled participants, with 4 follow-up telephone counseling sessions by a health educator over 18 months; mailed materials and sunscreen samples were also used. | uspstf-2018 | p5 | p5/narrative/adolescent-implementation | narrative |
| young-adult-web-implementation | young-adults-age-18-to-25 | evidence-described interactive 12-module program with 10-minute topics | RENDERED: In a web-based study of 18- to 25-year olds, participants viewed an interactive 12-module web program featuring 10-minute topics such as indoor tanning, UV exposure and health, skin cancer, and skin examination. | uspstf-2018 | p6 | p6/narrative/young-adult-web-implementation | narrative |
| adult-effective-intervention-modifiers | older-adult-counseling-evidence | evidence-described effective adult interventions were more often longer or had more frequent participant contacts | RENDERED: Effective interventions were more often of longer duration or had more frequent contacts with participants during the study period. | uspstf-2018 | p6 | p6/narrative/adult-effective-intervention-modifiers | narrative |
| sunscreen-skin-reactions | adults-using-sunscreen | possible transient allergic, irritant, or photoallergic contact dermatitis | Sunscreen use can be associated with numerous transient skin reactions, including allergic, irritant, and photoallergic contact dermatitis. | uspstf-2018 | p7 | p7/narrative/sunscreen-skin-reactions | narrative |
| sunscreen-vitamin-d-harm-evidence | adults-using-sunscreen | studies have not shown decreased vitamin D levels with sunscreen use | Although vitamin D deficiency is a hypothetical harm of sun avoidance, recent studies have not shown an association between sunscreen use and decreased vitamin D levels. | uspstf-2018 | p7 | p7/narrative/sunscreen-vitamin-d-harm-evidence | narrative |
| sun-protection-activity-harm-evidence | asymptomatic-no-skin-cancer-history | sparse evidence suggested no decreased physical activity or increased body mass index | Among the sparse evidence available, 1 study suggested that sun protection behaviors do not lead to decreased physical activity or increased body mass index. | uspstf-2018 | p7 | p7/narrative/sun-protection-activity-harm-evidence | narrative |
| sunscreen-false-reassurance-evidence | adults-using-sunscreen | older studies found no intentional increase in sun exposure, but 2 recent studies associated sunscreen with greater likelihood of multiple sunburns | Older studies reported that sunscreen use did not result in an intentional increase in sun exposure, but 2 recent studies showed that sunscreen use was associated with higher likelihood of multiple sunburns. | uspstf-2018 | p7 | p7/narrative/sunscreen-false-reassurance-evidence | narrative |
| self-exam-procedure-harm | adults-for-self-exam-counseling | self-examination was followed by more skin procedures; rising biopsies and melanoma incidence with stable mortality support overdiagnosis concern | RENDERED: Persons who performed skin self-examination were more likely to subsequently undergo a skin procedure compared with those who did not, as evidenced by 1 trial, indicating a potential harm of skin self-examination. Although melanoma death rates have remained stable, the increasing number of skin biopsies and rising melanoma incidence over recent decades provide evidence for overdiagnosis. | uspstf-2018 | p7 | p7/narrative/self-exam-procedure-harm | narrative |
| indoor-tanning-risk-thresholds | persons-with-indoor-tanning-exposure | indoor tanning before age 35 years, more than 10 lifetime sessions, or longer than 1 year is linked to increased cancer risk | Indoor tanning before age 35 years, for more than 10 tanning sessions over a lifetime, and for longer than 1 year have been linked to increased cancer risk. | uspstf-2018 | p7 | p7/narrative/indoor-tanning-risk-thresholds | narrative |
| indoor-tanning-risk-thresholds | women-younger-than-50-who-indoor-tan | evidence supports a dose-response relationship between melanoma risk and indoor tanning | A meta-analysis provided evidence of a dose-response relationship between melanoma risk and indoor tanning in women younger than 50 years. | uspstf-2018 | p6 | p6/narrative/indoor-tanning-dose-response | narrative |
| sunscreen-protective-evidence | adults-using-sunscreen | routine sunscreen use is supported by evidence of lower squamous-cell-carcinoma and melanoma risk; evidence, not a prescribed trial schedule | RENDERED: At 4.5 years, the intervention group had a decreased risk of squamous cell carcinoma. Ten years after conclusion of the trial, the intervention group had half as many incident melanomas as the control group. Overall, melanoma risk was reduced in the intervention group compared with the control group. | uspstf-2018 | p6 | p6/narrative/sunscreen-protective-evidence | narrative |
| minimum-sunscreen-age-rationale | fair-skin-age-6-months-to-24-years | lower counseling boundary extended to 6 months, the minimum age recommended for sunscreen use | Recent studies in children younger than 10 years resulted in the USPSTF extending the lower end of the age range to 6 months, the minimum age recommended for sunscreen use. | uspstf-2018 | p7 | p7/narrative/minimum-sunscreen-age-rationale | narrative |
| related-uspstf-skin-screening | asymptomatic-no-skin-cancer-history | RELATED USPSTF: separate recommendation addresses clinician screening for skin cancer in adults | RENDERED: The USPSTF has issued a recommendation on screening for skin cancer in adults. | uspstf-2018 | p5 | p5/narrative/related-uspstf-skin-screening | narrative |
| fda-sunscreen-use | patients-and-clinicians-using-fda-guidance | EXTERNAL (FDA): broad-spectrum SPF at least 15, reapplied at least every 2 hours, protects against UVA and UVB and reduces skin-cancer and early-aging risk | RENDERED: The FDA has determined that broad-spectrum sunscreens with a sun-protection factor of 15 or greater, reapplied at least every 2 hours, protect against both UVA and UVB radiation and reduce the risk of skin cancer and early skin aging. | uspstf-2018 | p4 | p4/narrative/fda-sunscreen-use | narrative |
| fda-indoor-tanning-resource | patients-and-clinicians-using-fda-guidance | EXTERNAL (FDA): consumer education materials address indoor-tanning dangers | The FDA also provides consumer education materials on the dangers of indoor tanning. | uspstf-2018 | p4 | p4/narrative/fda-indoor-tanning-resource | narrative |
| epa-sun-safety-resources | people-using-epa-sun-safety-tools | EXTERNAL (EPA): state-specific sun-safety information, UV forecasts by ZIP code or city, and age-appropriate fact sheets and handouts | RENDERED: The Environmental Protection Agency provides a variety of educational tools regarding sun safety, including state-specific information, and interactive widgets and smartphone applications that forecast UV exposure by zip code or city. It also provides sun safety fact sheets and handouts, including age-appropriate materials. | uspstf-2018 | p4 | p4/narrative/epa-sun-safety-resources | narrative |
| cpstf-setting-interventions | children-and-communities-for-cpstf | EXTERNAL (Community Preventive Services Task Force): child-care, school, recreational-site, occupational-setting, and community-wide education or policy interventions | RENDERED: The Community Preventive Services Task Force recommends education and policy approaches to encourage sun protection behaviors in child care centers, schools, recreational sites, and occupational settings. In addition, it recommends community-wide interventions that may or may not involve health care settings to increase protection behavior from UV radiation. | uspstf-2018 | p8 | p8/narrative/cpstf-setting-interventions | narrative |
| external-clinician-counseling | patients-for-external-prevention-counseling | EXTERNAL (US Surgeon General, American Cancer Society, American College of Obstetricians and Gynecologists, American Academy of Pediatrics, Royal Australian College of General Practitioners, and WHO International Agency for Research on Cancer): endorse clinician involvement in skin-cancer prevention counseling | RENDERED: The US Surgeon General, American Cancer Society, American College of Obstetricians and Gynecologists, American Academy of Pediatrics, Royal Australian College of General Practitioners, and the World Health Organization's International Agency for Research on Cancer endorse the involvement of clinicians in counseling patients about skin cancer prevention. | uspstf-2018 | p8 | p8/narrative/external-clinician-counseling | narrative |
| aad-self-examination | all-persons-for-aad-self-exam | EXTERNAL (American Academy of Dermatology): encourage everyone to perform skin self-examination for signs of skin cancer | The American Academy of Dermatology encourages everyone to perform skin self-examination to check for signs of skin cancer. | uspstf-2018 | p8 | p8/narrative/aad-self-examination | narrative |
| monthly-self-examination | persons-for-monthly-self-exam-guidance | EXTERNAL (American Cancer Society and Skin Cancer Foundation): monthly skin self-examination | RENDERED: The American Cancer Society and the Skin Cancer Foundation recommend monthly skin self-examination. | uspstf-2018 | p8 | p8/narrative/monthly-self-examination | narrative |

## Conflicts

No unresolved same-population, same-quantity machine conflict was identified. The Grade
B age range and Grade C older-adult pathway are complementary age branches. The source
lists personal skin-cancer history as risk context while separately limiting its stated
applicability to asymptomatic persons without such a history; the sheet therefore does
not turn personal history into eligibility for this prevention-counseling recommendation.

The USPSTF I statement addresses evidence for *counseling adults* about self-examination;
the external AAD, American Cancer Society, and Skin Cancer Foundation rows directly
recommend self-examination or a monthly frequency. Insufficient evidence is not a
recommendation against the service, and the quantities are kept distinct rather than
reported as a false conflict. The FDA sunscreen interval is source-attributed external
use guidance, whereas the USPSTF counseling row describes which behaviors to discuss.
Clinician screening for skin cancer is a separate related USPSTF service, not this
prevention-counseling intervention.

## Coverage

Exact recommendation accounting: **3 = 3 cited + 0 scoped out**.

ADR 0009 disposition:

- retained the Grade B 6-month-through-24-year branch, including the distinct action of
  counseling parents of eligible young children, the Grade C older-than-24 selective
  branch, adult self-examination I statement, fair-skin definition, asymptomatic/no-
  history applicability, and the risk factors used only in the eligible older-adult
  selective-counseling decision; personal skin-cancer history remains evidence context
  outside the recommendation's no-history applicability;
- retained all UV-minimization components, sunscreen SPF and midday-hour thresholds,
  indoor-tanning risk thresholds, the lower-age rationale, and benefit-harm magnitudes;
- retained child, parent, adolescent, young-adult, adult, print, in-person, telephone,
  mail, web, text, photograph, and counseling-aid modalities with their stated ages,
  contacts, session lengths, and delivery periods as evidence-described examples rather
  than mandatory regimens; this includes well-child-visit delivery, tailoring print
  materials to risk, barriers, and self-efficacy, primary-care-clinician or health-
  educator delivery, and the evidence observation that effective adult interventions
  were more often longer or more frequent;
- retained self-examination benefit and harm uncertainty, possible biopsy and
  psychosocial harms, excess-procedure/overdiagnosis concern, sunscreen skin reactions,
  and the vitamin D, activity, body-mass-index, and false-reassurance harm findings;
- retained the separate USPSTF screening boundary and source-attributed FDA, EPA,
  Community Preventive Services Task Force, professional-organization, and self-
  examination guidance without converting them into USPSTF counseling recommendations;
- excluded prevalence and mortality counts, trial sample sizes, confidence statistics,
  isolated effect estimates, publication/comment dates, author/disclosure information,
  research-needs statements that do not direct care, and study follow-up measurements
  that do not change a counseling, protection, delivery, risk, benefit-harm, or service-
  boundary decision.
