# Pancreatic cancer screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for
the recommendation statement** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2019-pancreatic | USPSTF | USPSTF/pancreatic-cancer-final-rec-statement | recommendation-statement | 2019 reaffirmation recommendation | 2019 | https://doi.org/10.1001/jama.2019.10232 | stated | exact |

## Scope

**Read:** all 7 pages, including the recommendation; reaffirmation rationale;
applicability and risk boundaries; imaging, biomarker, and treatment modalities;
screening and treatment benefit and harm evidence; high-risk study evidence; public
comments; external recommendations; article information; disclosures; and references.
The exact record contains one recommendation identifier.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| recommendation, findings, evidence assessment, and rationale | 1 | yes |
| disease statistics, stage-specific surgical-benefit context, and generic USPSTF grade/certainty boilerplate | 2 | yes |
| familial-risk definition, detection, benefits, harms, applicability, and clinician summary | 3 | yes |
| risk assessment, screening modalities, treatment, research, accuracy, and early-treatment evidence | 4 | yes |
| overdiagnosis, screening and surgical harms, net benefit, public comment, and reaffirmation | 5 | yes |
| external guidance, article information, disclosures, and beginning of references | 6 | yes |
| references | 7 | exempt: reference list has no patient-action prose |

citations resolved against C:/codeing/guidelines-src on 2026-09-01

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| asymptomatic-adults-not-known-high-risk | asymptomatic adults not known to be at high risk for pancreatic cancer |
| inherited-syndrome-or-familial-pancreatic-cancer | persons at high risk because of an inherited genetic syndrome or familial pancreatic cancer |
| familial-pancreatic-cancer-kindred | a kindred with at least 2 affected first-degree relatives |
| asymptomatic-lesser-risk-adults | asymptomatic adults with new-onset diabetes, preexisting diabetes, older age, cigarette smoking, obesity, or chronic pancreatitis but no known high-risk syndrome or familial pancreatic cancer |
| symptomatic-adult | adults with signs or symptoms potentially related to pancreatic cancer |
| general-population-screening-candidate | asymptomatic adults in the general population considered for pancreatic-cancer screening |
| high-risk-screening-study-participant | persons with inherited genetic syndromes or familial pancreatic cancer enrolled in high-risk screening studies |
| screen-detected-resectable-pancreatic-cancer | persons with pancreatic cancer deemed resectable at diagnosis |
| advanced-stage-pancreatic-cancer | persons whose pancreatic cancer is detected at an advanced stage |
| diagnosed-pancreatic-cancer | persons with diagnosed pancreatic cancer |
| screen-positive-or-lesion-detected-person | persons with a positive screening result or screen-detected pancreatic lesion |
| person-undergoing-eus | high-risk persons undergoing endoscopic ultrasonography in the cited screening evidence |
| person-undergoing-ercp-diagnostic-test | high-risk persons undergoing endoscopic retrograde cholangiopancreatography as a diagnostic test in the cited evidence |
| person-undergoing-pancreatectomy | persons undergoing pancreatectomy |
| external-acg-certain-high-risk | persons with a known pancreatic-cancer-associated genetic syndrome or from a familial pancreatic cancer kindred with an affected first-degree relative under American College of Gastroenterology guidance |

## Quantities

| key | verbatim |
| --- | --- |
| screening-recommendation | USPSTF pancreatic-cancer screening recommendation |
| screening-applicability | symptom and hereditary/familial-risk applicability |
| familial-pancreatic-cancer-definition | source definition of familial pancreatic cancer |
| lesser-risk-factor-disposition | inclusion of lesser-risk asymptomatic adults in the general-population recommendation |
| general-population-screening-method | screening-method boundary in the general population |
| imaging-screening-provenance | population in which CT, MRI, and EUS were studied as screening tests |
| biomarker-availability | availability of an accurate validated early-detection biomarker |
| imaging-accuracy-evidence | evidence for sensitivity or specificity of CT, MRI, or EUS screening |
| screening-benefit-evidence | evidence that screening or treatment of screen-detected disease improves morbidity or mortality |
| screening-benefit-magnitude | USPSTF upper bound on screening benefit magnitude |
| screening-treatment-harm-magnitude | USPSTF lower bound on screening and treatment harm magnitude |
| net-benefit-assessment | USPSTF balance of screening benefits and harms |
| stage-resection-benefit-boundary | stage-specific likelihood of benefit from surgical intervention or resection |
| resectable-cancer-surgery | surgery for resectable pancreatic cancer |
| chemotherapy-position | neoadjuvant or adjuvant chemotherapy position |
| positive-screen-follow-up-uncertainty | absence of a general-population follow-up algorithm after a positive screening result |
| overdiagnosis-overtreatment-risk | potential overdiagnosis and overtreatment from screening |
| eus-procedure-harm-evidence | procedure-related harm evidence for EUS screening |
| ercp-procedure-harm-evidence | procedure-related harm evidence for diagnostic ERCP |
| pancreatectomy-harm | morbidity and mortality risk of pancreatectomy |
| psychosocial-harm-evidence | psychosocial-harm findings in high-risk screening studies |
| screening-interval | USPSTF pancreatic-cancer screening interval |
| external-general-population-position | externally reported organizational position on general-population screening |
| external-acg-high-risk-surveillance | externally reported ACG high-risk surveillance position and setting |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| screening-recommendation | asymptomatic-adults-not-known-high-risk | do not screen for pancreatic cancer | The USPSTF recommends against screening for pancreatic cancer in asymptomatic adults. | uspstf-2019-pancreatic | 1 | p1/screening-for-pancreatic-cancer/1 | D |
| screening-applicability | asymptomatic-adults-not-known-high-risk | applies to asymptomatic adults not known to be at high risk | RENDERED: This recommendation applies to asymptomatic adults not known to be at high risk of pancreatic cancer. | uspstf-2019-pancreatic | 3 | p3/narrative/applicability | narrative |
| screening-applicability | inherited-syndrome-or-familial-pancreatic-cancer | recommendation does not apply | RENDERED: this recommendation does not apply to persons at high risk of pancreatic cancer due to an inherited genetic syndrome ... or due to a history of familial pancreatic cancer. | uspstf-2019-pancreatic | 4 | p4/narrative/high-risk-exclusion | narrative |
| screening-applicability | symptomatic-adult | this asymptomatic-screening recommendation does not establish a diagnostic pathway | RENDERED: This recommendation applies to asymptomatic adults | uspstf-2019-pancreatic | 3 | p3/narrative/symptom-boundary | narrative |
| familial-pancreatic-cancer-definition | familial-pancreatic-cancer-kindred | at least 2 affected first-degree relatives | RENDERED: Familial pancreatic cancer is defined as a kindred with at least 2 affected first-degree relatives | uspstf-2019-pancreatic | 3 | p3/narrative/familial-definition | narrative |
| lesser-risk-factor-disposition | asymptomatic-lesser-risk-adults | included in the general-population no-screening recommendation | RENDERED: new-onset diabetes, preexisting diabetes, older age, cigarette smoking, obesity, or a history of chronic pancreatitis increase risk to a lesser degree. Asymptomatic persons who have these risk factors are included in this recommendation. | uspstf-2019-pancreatic | 3 | p3/narrative/lesser-risk-inclusion | narrative |
| general-population-screening-method | general-population-screening-candidate | do not screen using any method | RENDERED: The USPSTF does not recommend screening for pancreatic cancer in the general population using any method. | uspstf-2019-pancreatic | 4 | p4/narrative/any-method-boundary | narrative |
| imaging-screening-provenance | high-risk-screening-study-participant | CT, MRI, and EUS have been studied as screening tests in high-risk inherited-syndrome or familial-pancreatic-cancer trials; this is study provenance, not a USPSTF screening action | RENDERED: Imaging-based methods, such as the CT scan, MRI, and EUS, have been studied as screening tests in trials of screening persons at high risk of pancreatic cancer due to inherited genetic syndromes or familial pancreatic cancer. | uspstf-2019-pancreatic | 4 | p4/narrative/imaging-study-provenance | narrative |
| biomarker-availability | general-population-screening-candidate | no accurate validated biomarker currently exists for early detection | RENDERED: There currently are no accurate, validated biomarkers for early detection of pancreatic cancer. | uspstf-2019-pancreatic | 4 | p4/narrative/biomarker-availability | narrative |
| imaging-accuracy-evidence | general-population-screening-candidate | no studies reported sensitivity or specificity for CT, MRI, or EUS as screening tests | RENDERED: The USPSTF found no studies that reported on the sensitivity or specificity of CT scan, MRI, or EUS as screening tests for pancreatic cancer. | uspstf-2019-pancreatic | 4 | p4/narrative/imaging-accuracy-evidence | narrative |
| screening-benefit-evidence | asymptomatic-adults-not-known-high-risk | no evidence that screening or treatment of screen-detected cancer improves disease-specific morbidity, disease-specific mortality, or all-cause mortality | RENDERED: no evidence that screening for pancreatic cancer or treatment of screen-detected pancreatic cancer improves disease-specific morbidity or mortality, or all-cause mortality. | uspstf-2019-pancreatic | 3 | p3/narrative/screening-benefit-evidence | narrative |
| screening-benefit-magnitude | asymptomatic-adults-not-known-high-risk | benefit is no greater than small | RENDERED: bound the benefits of screening for pancreatic cancer in asymptomatic adults as no greater than small. | uspstf-2019-pancreatic | 3 | p3/narrative/benefit-magnitude | narrative |
| screening-treatment-harm-magnitude | asymptomatic-adults-not-known-high-risk | harms are at least moderate, based on potential harms from false-positive results and harms of treatment | RENDERED: bound the magnitude of the harms of screening for pancreatic cancer and treatment of screen-detected pancreatic cancer as at least moderate, based on potential harms from false-positive results and the harms of treatment. | uspstf-2019-pancreatic | 3 | p3/narrative/harm-magnitude | narrative |
| net-benefit-assessment | asymptomatic-adults-not-known-high-risk | potential benefits do not outweigh potential harms | RENDERED: the potential benefits of screening for pancreatic cancer in asymptomatic adults do not outweigh the potential harms. | uspstf-2019-pancreatic | 3 | p3/narrative/net-benefit | narrative |
| stage-resection-benefit-boundary | diagnosed-pancreatic-cancer | early-stage surgical intervention is most likely to improve survival chances; most advanced-stage disease is unlikely to benefit from surgical resection | RENDERED: Surgical intervention at an early stage is the treatment most likely to improve chances of survival; however, most cases of pancreatic cancer are detected at an advanced stage, when surgical resection is not likely to be beneficial. | uspstf-2019-pancreatic | 2 | p2/narrative/stage-resection-benefit-boundary | narrative |
| resectable-cancer-surgery | screen-detected-resectable-pancreatic-cancer | generally use pancreaticoduodenectomy (Whipple procedure), total pancreatectomy, or distal pancreatectomy | RENDERED: Surgery (pancreaticoduodenectomy [known as the Whipple procedure] or total or distal pancreatectomy) is the generally recommended treatment for pancreatic cancer deemed to be resectable at the time of diagnosis. | uspstf-2019-pancreatic | 4 | p4/narrative/resectable-surgery | narrative |
| chemotherapy-position | diagnosed-pancreatic-cancer | neoadjuvant or adjuvant chemotherapy may be recommended based on cancer stage and other factors | RENDERED: Neoadjuvant or adjuvant chemotherapy may be recommended, depending on the stage of cancer and other factors. | uspstf-2019-pancreatic | 4 | p4/narrative/chemotherapy-position | narrative |
| positive-screen-follow-up-uncertainty | screen-positive-or-lesion-detected-person | the USPSTF establishes no general-population positive-screen threshold, confirmatory sequence, or follow-up algorithm because it recommends no screening method | RENDERED: The USPSTF does not recommend screening for pancreatic cancer in the general population using any method. | uspstf-2019-pancreatic | 4 | p4/narrative/positive-screen-follow-up-uncertainty | narrative |
| overdiagnosis-overtreatment-risk | general-population-screening-candidate | screening may cause overdiagnosis and overtreatment because common precursor lesions often do not progress and the cited International Consensus Guidelines criteria had 14.8% specificity for high-grade dysplasia or invasive cancer | RENDERED: Pancreatic intraepithelial neoplasia is common, and most cases do not progress to cancer ... the International Consensus Guidelines criteria for the management of intraductal papillary mucinous neoplasms of the pancreas had high sensitivity (98.4%) but low specificity (14.8%) to predict high-grade dysplasia or invasive cancer. These data suggest the possibility that screening in the general population might lead to overdiagnosis and overtreatment. | uspstf-2019-pancreatic | 5 | p5/narrative/overdiagnosis-overtreatment | narrative |
| eus-procedure-harm-evidence | person-undergoing-eus | high-risk study: 25.5% reported mild postprocedure pain and 6.0% reported anesthesia-related adverse events | RENDERED: 216 persons who underwent EUS, 55 (25.5%) reported mild postprocedure pain, and 13 (6.0%) reported adverse events related to anesthesia. | uspstf-2019-pancreatic | 5 | p5/narrative/eus-harms | narrative |
| ercp-procedure-harm-evidence | person-undergoing-ercp-diagnostic-test | high-risk studies: 10.0% developed acute pancreatitis and 9 of those required hospitalization | RENDERED: 150 persons ... underwent endoscopic retrograde cholangiopancreatography as a diagnostic test, 15 (10.0%) developed acute pancreatitis, 9 of whom required hospitalization. | uspstf-2019-pancreatic | 5 | p5/narrative/ercp-harms | narrative |
| pancreatectomy-harm | person-undergoing-pancreatectomy | pancreatectomy carries significant morbidity and mortality risk | RENDERED: Pancreatectomy carries a significant risk of morbidity and mortality | uspstf-2019-pancreatic | 5 | p5/narrative/pancreatectomy-harm | narrative |
| psychosocial-harm-evidence | high-risk-screening-study-participant | in 2 high-risk screening studies, most participants reported normal distress or worry; this does not establish harms in the general population | RENDERED: In 2 studies ... that assessed the psychosocial harms of screening, the majority of participants reported normal levels of distress or worry at all time points. | uspstf-2019-pancreatic | 5 | p5/narrative/psychosocial-harms | narrative |
| screening-interval | asymptomatic-adults-not-known-high-risk | no routine screening interval applies because screening is not recommended by any method | RENDERED: The USPSTF does not recommend screening for pancreatic cancer in the general population using any method. | uspstf-2019-pancreatic | 4 | p4/narrative/no-screening-interval | narrative |
| external-general-population-position | asymptomatic-adults-not-known-high-risk | EXTERNAL: no organization currently recommends general-population screening | RENDERED: No organization currently recommends screening for pancreatic cancer in the general population of asymptomatic adults. | uspstf-2019-pancreatic | 5 | p5/narrative/external-general-population | narrative |
| external-acg-high-risk-surveillance | external-acg-certain-high-risk | EXTERNAL (ACG): conditionally recommend surveillance in certain high-risk persons; perform it in experienced centers, ideally under research conditions | RENDERED: conditionally recommends surveillance for pancreatic cancer in certain high-risk persons ... and suggests that surveillance should be performed in experienced centers, ideally under research conditions. | uspstf-2019-pancreatic | 6 | p6/narrative/external-acg-surveillance | narrative |

## Conflicts

No same-population, same-quantity conflict was identified. The USPSTF Grade D action
applies to asymptomatic adults not known to be at high hereditary or familial risk. The
external ACG surveillance position applies to a distinct high-risk population excluded
from the USPSTF recommendation and is not imported as an exception for average-risk or
lesser-risk adults.

CT, MRI, and EUS are retained as methods studied in high-risk cohorts, not recommended
USPSTF screening modalities. Likewise, treatment of diagnosed resectable cancer is not
evidence that screening the general population provides benefit.

## Coverage

The exact recommendation record contains **1 recommendation identifier**. This sheet
cites it and scopes out none: **1 = 1 cited + 0 scoped**.

ADR 0009 disposition:

- retained the Grade D no-screening action, asymptomatic and known-high-risk boundaries,
  familial-pancreatic-cancer definition, and explicit inclusion of lesser-risk diabetes,
  age, smoking, obesity, and chronic-pancreatitis groups;
- retained the any-method no-screening boundary, CT/MRI/EUS high-risk-study provenance,
  absence of validated biomarkers, and absent imaging-accuracy evidence without turning
  a studied modality into a recommendation;
- retained absent morbidity and mortality benefit, no-greater-than-small benefit, at-
  least-moderate harms with their false-positive-result and treatment-harm rationale, and
  negative net balance;
- retained p2's early-stage surgical survival opportunity and advanced-stage resection-
  benefit limitation, diagnosed resectable-cancer surgery, and stage-dependent
  chemotherapy as treatment context, not screening benefit, and retained the absence of
  a positive-screen algorithm because the source recommends no screening method;
- retained overdiagnosis/overtreatment context, including the cited management criteria's
  14.8% specificity, high-risk-study EUS and ERCP harm evidence, significant
  pancreatectomy risk, and limited high-risk psychosocial evidence with their exact
  populations rather than generalizing study results;
- inferred no screening interval and kept the no-organization general-population position
  and ACG high-risk surveillance guidance explicitly `EXTERNAL`;
- incidence, survival, prevalence, trial yields, surgical pathology counts, follow-up,
  additional operative complication and mortality rates,
  public-comment and correction dates, article metadata, disclosures, citation numbers,
  and reference-list values were evidence or metadata and were not interpreted as
  additional patient-action thresholds.
