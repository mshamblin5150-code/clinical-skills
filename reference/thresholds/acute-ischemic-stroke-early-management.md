# Acute ischemic stroke, early management - threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the sources below. **Not a substitute for the
guidelines** and not a clinical instruction. The 2019 and 2026 documents are retained
as separate sources because later recommendations revise, narrow, or reverse some
earlier decision points.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aha-2019 | AHA ACC | AHA ACC/powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018 | guideline | 2019 | 2019 | https://doi.org/10.1161/STR.0000000000000211 | stated |  |
| aha-2026 | AHA ACC | AHA ACC/prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from | guideline | 2026 | 2026 | https://doi.org/10.1161/STR.0000000000000513 | stated | exact |

## Scope

**Read:** both documents in full as one topic: 2019 pages 1-75 and 2026 pages
1-121. The read included recommendations, algorithms, narrative supportive text,
eligibility and treatment tables, complications, in-hospital management, secondary
prevention begun during the acute admission, knowledge gaps, disclosures, and
references. Tables 6-9 on 2019 pages 23-27 and Tables 4-8 on 2026 pages 40-43 and
49-52 were also read from rendered pages because their structure is clinically
material.

**Not read:** nothing in either source page range. Reference lists were inspected for
scope but are exempt from decision-point extraction because they contain no clinical
prose.

**Source: `aha-2019`**

| span | pages | read |
| --- | --- | --- |
| complete guideline, including recommendations, narrative, clinical tables, complications, in-hospital management, secondary prevention begun during admission, knowledge gaps, disclosures, and references | 1-75 | yes |

**Source: `aha-2026`**

| span | pages | read |
| --- | --- | --- |
| complete guideline, including recommendations, algorithms, narrative, clinical tables, complications, in-hospital management, secondary prevention begun during admission, knowledge gaps, disclosures, and references | 1-121 | yes |

citations resolved against C:/codeing/guidelines-src on 2026-08-30
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

The 2019 recommendation sweep reported `nothing-found`; that is an extraction-mode
limitation, not an empty clinical source. Its rows below therefore use narrative
locators from the complete page read. The 2026 exact index is used for accounting,
with narrative and rendered-table locators added where a decision point lies outside
that index.

## Populations

| key | verbatim |
| --- | --- |
| suspected-ais | patients with suspected AIS |
| ais | patients with AIS |
| adult-ais-ivt | adult patients with AIS presenting within 4.5 hours of symptom onset or last known well and eligible for IVT |
| pediatric-ais | pediatric patients with suspected AIS |
| ais-lvo | patients with suspected AIS and LVO |
| ais-no-reperfusion | patients who did not receive IVT or EVT |
| ais-after-ivt | patients with AIS who have been treated with IVT |
| ais-after-evt | patients who undergo EVT |
| ais-planned-evt-no-ivt | patients for whom EVT is planned and who have not received IVT |
| minor-ais-or-high-risk-tia | patients with minor noncardioembolic AIS or high-risk TIA |
| large-hemispheric-infarction | patients with large hemispheric infarction |
| unilateral-mca-infarction | patients with unilateral MCA infarctions |
| cerebellar-infarction | patients with cerebellar infarction |

## Quantities

| key | verbatim |
| --- | --- |
| imaging-time | emergent brain imaging can be performed as rapidly as possible |
| extended-ivt-window | determine eligibility for extended window IVT |
| evt-imaging-window | evaluation for EVT |
| oxygen-target | maintain oxygen saturation |
| prehospital-sbp-target | intensive BP control in the field |
| pre-evt-hyperoxia | normobaric hyperoxia before EVT |
| head-position | head positioning |
| trendelenburg-head-position | routine Trendelenburg positioning |
| post-ivt-bp | BP should be maintained |
| post-evt-bp | maintain BP |
| no-reperfusion-bp | initiating or reinitiating treatment of hypertension |
| pre-ivt-bp | before IVT therapy is initiated |
| pre-evt-bp | before EVT in patients who have not received IVT |
| glucose-low | hypoglycemia |
| glucose-target | achieve blood glucose levels |
| ivt-agent-dose | choice of thrombolytic agent |
| ivt-window | treatment with IVT |
| evt-eligibility | EVT is recommended |
| pediatric-evt-eligibility | EVT can be effective |
| aspirin-start | administration of aspirin |
| dissection-antithrombotic-duration | antiplatelet or anticoagulant therapy |
| dapt-course | DAPT |
| aspirin-after-ivt | IV aspirin |
| early-anticoagulation | early anticoagulation |
| enteral-start | enteral diet |
| nutrition-screening | nutritional screening |
| feeding-access | use nasogastric tubes initially for feeding |
| mobilization-time | very early mobilization |
| craniectomy-eligibility | decompressive craniectomy |
| glibenclamide-no-benefit | use of IV glibenclamide |
| ivt-eligibility-laboratory | eligibility recommendations for IV alteplase |
| ivt-monitoring | treatment of AIS: IV administration of alteplase |
| ich-reversal | management of symptomatic intracranial bleeding |
| angioedema-treatment | management of orolingual angioedema |
| secondary-prevention | prevention of recurrent stroke |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prehospital-sbp-target | suspected-ais | target 130-140 mm Hg: no benefit | "intensive BP control in the field to a target of 130 to 140 mm Hg systolic does not improve functional outcome" | aha-2026 | p12 | p12/prehospital-assessment-and-management/6 | 3 |
| imaging-time | suspected-ais | within 25 minutes | "within 25 minutes" | aha-2026 | p26 | p26/initial-vascular-and-multimodal-imaging/2 | 1 |
| imaging-time | pediatric-ais | CT/CTA if MRI/MRA unavailable within 25 minutes | "MRI/MRA imaging is not available immediately (within 25 minutes)" | aha-2026 | p26 | p26/initial-vascular-and-multimodal-imaging/5 | 2a |
| extended-ivt-window | suspected-ais | unknown onset >4.5 hours: MRI DWI-FLAIR selection | "unknown time of onset >4.5 hours from last known well" | aha-2026 | p26 | p26/initial-vascular-and-multimodal-imaging/6 | 2a |
| extended-ivt-window | suspected-ais | unknown onset 4.5-24 hours: CTP or MR selection | "unknown time of onset 4.5 to 24 hours from last known well" | aha-2026 | p27 | p27/initial-vascular-and-multimodal-imaging/7 | 2a |
| evt-imaging-window | ais-lvo | within 24 hours | "presenting within 24 hours of last known well" | aha-2026 | p27 | p27/initial-vascular-and-multimodal-imaging/8 | 1 |
| evt-imaging-window | ais-lvo | 6-24 hours: adjunct perfusion imaging if immediately available | "presenting within 6 to 24 hours of last known well" | aha-2026 | p27 | p27/initial-vascular-and-multimodal-imaging/9 | 2a |
| evt-imaging-window | ais-lvo | RACE >4 may support direct-to-angiography triage | "RACE >4" | aha-2026 | p27 | p27/initial-vascular-and-multimodal-imaging/10 | 2b |
| oxygen-target | ais | SpO2 >94% | RENDERED: "oxygen saturation (SpO2) >94%" | aha-2026 | p32 | p32/airway-breathing-and-oxygenation/2 | 1 |
| pre-evt-hyperoxia | ais-lvo | within 6 hours; NIHSS 10-20; CT ASPECTS >=6 | RENDERED: "within 6 hours from onset, NIHSS score 10 to 20, CT ASPECTS of >=6" | aha-2026 | p32 | p32/airway-breathing-and-oxygenation/3 | 2b |
| head-position | ais | routine 0 degrees vs 30 degrees for 24 hours: no benefit | "0-degree head positioning compared with 30 degrees for 24 hours" | aha-2026 | p34 | p34/head-positioning/1 | 3 |
| trendelenburg-head-position | ais | -20 degrees vs 0-30 degrees: no benefit | "routine Trendelenburg positioning (-20 degrees) compared with 0- to 30-degree head positioning" | aha-2026 | p34 | p34/head-positioning/2 | 3 |
| post-ivt-bp | ais-after-ivt | <180/105 mm Hg for at least 24 hours | "<180/105 mm Hg for at least the first 24 hours" | aha-2026 | p35 | p35/blood-pressure-management-continued/7 | 1 |
| post-ivt-bp | ais-after-ivt | target <140 vs <180 mm Hg: not recommended | "target of <140 mm Hg compared with <180 mm Hg" | aha-2026 | p35 | p35/blood-pressure-management-continued/8 | 3 |
| post-evt-bp | ais-after-evt | <=180/105 mm Hg during and 24 hours after EVT | RENDERED: "maintain BP at a level <=180/105 mm Hg during and for 24 hours after the procedure" | aha-2026 | p35 | p35/blood-pressure-management-continued/9 | 2a |
| post-evt-bp | ais-after-evt | after mTICI 2b/2c/3, target <140 mm Hg for 72 hours: harmful | RENDERED: "mTICI 2b, 2c, or 3 and without other indication for blood pressure management target, intensive SBP reduction target of <140 mm Hg for the first 72 hours is harmful" | aha-2026 | p35 | p35/blood-pressure-management-continued/10 | 3 |
| no-reperfusion-bp | ais-no-reperfusion | BP >=220/120 mm Hg: benefit of treatment in 48-72 hours uncertain | RENDERED: "BP >=220/120 mm Hg who did not receive IVT or EVT and have no comorbid conditions requiring urgent antihypertensive treatment, the benefit of initiating or reinitiating treatment of hypertension within the first 48 to 72 hours is uncertain" | aha-2026 | p35 | p35/blood-pressure-management/3 | 2b |
| no-reperfusion-bp | ais-no-reperfusion | BP <220/120 mm Hg: treatment in 48-72 hours not effective | RENDERED: "BP <220/120 mm Hg who did not receive IVT or EVT and do not have a comorbid condition requiring urgent antihypertensive treatment, initiating or reinitiating treatment of hypertension within the first 48 to 72 hours after an AIS is not effective" | aha-2026 | p35 | p35/blood-pressure-management/4 | 3 |
| pre-ivt-bp | ais | SBP <185 and DBP <110 mm Hg | "SBP lowered to <185 mm Hg and diastolic blood pressure (DBP) <110 mm Hg" | aha-2026 | p35 | p35/blood-pressure-management/5 | 1 |
| pre-evt-bp | ais-planned-evt-no-ivt | <=185/110 mm Hg before EVT | RENDERED: "maintain BP <=185/110 mm Hg before the procedure" | aha-2026 | p35 | p35/blood-pressure-management/6 | 2a |
| glucose-low | ais | <60 mg/dL: treat | "blood glucose <60 mg/dL" | aha-2026 | p37 | p37/blood-glucose-management/1 | 1 |
| glucose-target | ais | 140-180 mg/dL | "range of 140 to 180 mg/dL" | aha-2026 | p37 | p37/blood-glucose-management/2 | 2a |
| glucose-target | ais | IV insulin target 80-130 mg/dL: not recommended | "range of 80 to 130 mg/dL" | aha-2026 | p37 | p37/blood-glucose-management/3 | 3 |
| ivt-agent-dose | adult-ais-ivt | TNK 0.25 mg/kg (max 25 mg) or alteplase 0.9 mg/kg (max 90 mg) | "tenecteplase at a dose of 0.25 mg/kg body weight (max 25 mg) or alteplase at a dose of 0.9 mg/kg body weight (max 90 mg)" | aha-2026 | p42 | p42/choice-of-thrombolytic-agent/1 | 1 |
| ivt-agent-dose | adult-ais-ivt | TNK 0.4 mg/kg: not recommended | "tenecteplase at a dose of 0.4 mg/kg body weight is not recommended" | aha-2026 | p42 | p42/choice-of-thrombolytic-agent/2 | 3 |
| ivt-window | ais | unknown onset: within 4.5 hours of recognition; DWI lesion less than one-third MCA and no marked FLAIR change | RENDERED: "within 4.5 hours from symptom recognition and have an MRI-DWI lesion smaller than one-third of the MCA territory and no marked signal change on FLAIR" | aha-2026 | p44 | p44/extended-time-windows-for-intravenous/1 | 2a |
| ivt-window | ais | wake-up within 9 hours of sleep midpoint or 4.5-9 hours LKW with salvageable penumbra | RENDERED: "within 9 hours from the midpoint of sleep or 4.5-9 hours from last known well" | aha-2026 | p44 | p44/extended-time-windows-for-intravenous/2 | 2a |
| ivt-window | ais-lvo | 4.5-24 hours with salvageable penumbra and no EVT | "presenting within 4.5 to 24 hours" | aha-2026 | p44 | p44/extended-time-windows-for-intravenous/3 | 2b |
| ivt-window | ais | reteplase may be considered within 4.5 hours if no EVT | "within 4.5 hours from last known normal" | aha-2026 | p45 | p45/other-iv-fibrinolytics-and-sonothrombolysis/1 | 2b |
| ivt-window | ais | mutant prourokinase may be considered within 4.5 hours if no EVT | "within 4.5 hours from last known normal" | aha-2026 | p45 | p45/other-iv-fibrinolytics-and-sonothrombolysis/2 | 2b |
| ivt-window | ais | desmoteplase at 3-9 hours: not recommended | "presenting within 3 to 9 hours" | aha-2026 | p46 | p46/other-iv-fibrinolytics-and-sonothrombolysis/3 | 3 |
| ivt-window | ais | urokinase or streptokinase within 6 hours: no benefit / do not administer | "within 6 hours from last known normal" | aha-2026 | p46 | p46/other-iv-fibrinolytics-and-sonothrombolysis/5 | 3 |
| ivt-window | ais | CRAO disabling visual loss within 4.5 hours: usefulness uncertain | "within 4.5 hours of time last known well is uncertain" | aha-2026 | p47 | p47/other-specific-circumstances/2 | 2b |
| evt-eligibility | ais-lvo | ICA/M1; <=6 hours; NIHSS >=6; mRS 0-1; ASPECTS 3-10 | RENDERED: "ICA or M1, presenting within 6 hours from onset of symptoms, with NIHSS score >=6, prestroke mRS score of 0 to 1, and ASPECTS 3 to 10" | aha-2026 | p53 | p53/endovascular-thrombectomy-for-adult/1 | 1 |
| evt-eligibility | ais-lvo | ICA/M1; 6-24 hours; NIHSS >=6; mRS 0-1; ASPECTS >=6 | RENDERED: "ICA or M1 presenting between 6 and 24 hours from onset of symptoms, with NIHSS score >=6, prestroke mRS score 0 to 1 and ASPECTS >=6" | aha-2026 | p53 | p53/endovascular-thrombectomy-for-adult/2 | 1 |
| evt-eligibility | ais-lvo | age <80; 6-24 hours; NIHSS >=6; mRS 0-1; ASPECTS 3-5 | RENDERED: "between 6 and 24 hours from onset of symptoms, with age <80 years, NIHSS score >=6, prestroke mRS score 0 to 1, ASPECTS 3 to 5" | aha-2026 | p54 | p54/endovascular-thrombectomy-for-adult/3 | 1 |
| evt-eligibility | ais-lvo | age <80; <=6 hours; NIHSS >=6; mRS 0-1; ASPECTS 0-2 | RENDERED: "within 6 hours from onset of symptoms, with age <80 years, NIHSS score >=6, prestroke mRS score 0 to 1, ASPECTS 0 to 2" | aha-2026 | p54 | p54/endovascular-thrombectomy-for-adult/4 | 2a |
| evt-eligibility | ais-lvo | <=6 hours; NIHSS >=6; ASPECTS >=6; mRS 2 | RENDERED: "within 6 hours from onset of symptoms, with NIHSS score >=6, and ASPECTS >=6, who have a prestroke mRS score of 2" | aha-2026 | p54 | p54/endovascular-thrombectomy-for-adult/5 | 2a |
| evt-eligibility | ais-lvo | <=6 hours; NIHSS >=6; ASPECTS >=6; mRS 3-4 | RENDERED: "within 6 hours from onset of symptoms with NIHSS score >=6, and ASPECTS of >=6, who have a prestroke mRS score of 3 to 4" | aha-2026 | p54 | p54/endovascular-thrombectomy-for-adult/6 | 2b |
| evt-eligibility | ais-lvo | dominant M2; <=6 hours; mRS 0-1; NIHSS >=6; ASPECTS >=6 | RENDERED: "dominant proximal M2 division of the MCA presenting within 6 hours from onset of symptoms with a prestroke mRS score of 0 to 1, NIHSS score of >=6, and ASPECTS of >=6" | aha-2026 | p54 | p54/endovascular-thrombectomy-for-adult/7 | 2a |
| evt-eligibility | ais-lvo | basilar; mRS 0-1; NIHSS >=10; PC-ASPECTS >=6; <=24 hours | RENDERED: "basilar artery occlusion, a baseline mRS score of 0 to 1, NIHSS score >=10 at presentation, and PC-ASPECTS >=6, EVT within 24 hours" | aha-2026 | p57 | p57/posterior-circulation-stroke/1 | 1 |
| evt-eligibility | ais-lvo | basilar; mRS 0-1; NIHSS 6-9; PC-ASPECTS >=6; <=24 hours: uncertain | RENDERED: "basilar artery occlusion, a baseline mRS score of 0 to 1, NIHSS score 6 to 9 at presentation, and PC-ASPECTS >=6, EVT within 24 hours" | aha-2026 | p57 | p57/posterior-circulation-stroke/2 | 2b |
| pediatric-evt-eligibility | pediatric-ais | age >=6 years; <=6 hours; LVO | RENDERED: "pediatric patients >=6 years with acute neurological symptoms and ischemic stroke due to LVO and within 6 hours from symptom onset" | aha-2026 | p60 | p60/endovascular-thrombectomy-in-pediatric/1 | 2a |
| pediatric-evt-eligibility | pediatric-ais | age >=6 years; 6-24 hours; LVO and salvageable tissue | RENDERED: "pediatric patients >=6 years with acute neurological symptoms and ischemic stroke due to LVO, 6 to 24 hours from symptom onset, and with potentially salvageable brain tissue" | aha-2026 | p61 | p61/endovascular-thrombectomy-in-pediatric/2 | 2a |
| pediatric-evt-eligibility | pediatric-ais | age 28 days-6 years; <=24 hours; LVO and salvageable tissue | "pediatric patients aged 28 days to 6 years with acute neurological symptoms, including first-time seizure and AIS due to LVO, within 24 hours from symptom onset" | aha-2026 | p61 | p61/endovascular-thrombectomy-in-pediatric/3 | 2b |
| aspirin-start | ais | within 48 hours | "within 48 hours after stroke onset" | aha-2026 | p61 | p61/antiplatelet-treatment/1 | 1 |
| aspirin-after-ivt | ais-after-ivt | first 24 hours: risk uncertain | "first 24 hours after IVT" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/2 | 2b |
| dissection-antithrombotic-duration | ais | at least 3 months | "for at least 3 months" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/7 | 2a |
| dapt-course | minor-ais-or-high-risk-tia | NIHSS <=3 or ABCD2 >=4: ticagrelor not recommended over aspirin | RENDERED: "minor (NIHSS score <=3) noncardioembolic AIS or high-risk TIA (ABCD2 score >=4), ticagrelor is not recommended over aspirin" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/9 | 3 |
| dapt-course | minor-ais-or-high-risk-tia | NIHSS <=3 or ABCD2 >=4; start <=24 hours; DAPT 21 days then SAPT | RENDERED: "minor (NIHSS score <=3) noncardioembolic AIS or high-risk TIA (ABCD2 score >=4) who did not receive IVT, DAPT should be initiated early (within 24 hours after symptom onset) and continued for 21 days" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/12 | 1 |
| dapt-course | minor-ais-or-high-risk-tia | <24 hours; NIHSS <=5; ABCD2 >=6 or stenosis >=50%; ticagrelor plus aspirin 30 days | RENDERED: "recent (<24 hours) minor (NIHSS score <=5) noncardioembolic AIS or high-risk TIA (ABCD2 score >=6 or symptomatic intracranial or extracranial >=50% stenosis) who did not receive IVT, DAPT with ticagrelor plus aspirin for 30 days" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/13 | 2b |
| dapt-course | minor-ais-or-high-risk-tia | within 24-72 hours; NIHSS <=5 or NIHSS 4-5 within 24 hours; stenosis >=50%; DAPT 21 days | RENDERED: "minor (NIHSS score <=5) noncardioembolic AIS or high-risk TIA (ABCD2 score >=4) within 24 to 72 hours from stroke onset, or NIHSS score of 4 to 5 within 24 hours from onset, who did not receive IVT, with presumed atherosclerotic cause (>=50% stenosis), DAPT for 21 days" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/14 | 2a |
| dapt-course | minor-ais-or-high-risk-tia | NIHSS <=3; ABCD2 >=4; <=24 hours; CYP2C19 LOF: ticagrelor plus aspirin 21 days | RENDERED: "minor (NIHSS score <=3) noncardioembolic AIS or high-risk TIA (ABCD2 score >=4) within 24 hours after symptom onset who did not receive IVT and who carry the CYP2C19 loss-of-function allele, DAPT with ticagrelor and aspirin for 21 days" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/15 | 2b |
| aspirin-after-ivt | ais | concurrent or within 90 minutes after IVT: do not administer | "within 90 minutes after the start of IVT" | aha-2026 | p63 | p63/antiplatelet-treatment-continued/17 | 3 |
| early-anticoagulation | ais | within 48 hours: not recommended | "within 48 hours of stroke onset" | aha-2026 | p69 | p69/anticoagulants/6 | 3 |
| enteral-start | ais | within 7 days | "within 7 days of admission" | aha-2026 | p76 | p76/nutrition/1 | 1 |
| nutrition-screening | ais | preferably within 48 hours | "preferably within 48 hours of admission" | aha-2026 | p76 | p76/nutrition/2 | 1 |
| feeding-access | ais | NG within first 7 days; PEG if unsafe swallow >2-3 weeks | RENDERED: "nasogastric tubes initially for feeding within the first 7 days and to place percutaneous gastrostomy tubes in patients with longer anticipated persistent inability to swallow safely (>2-3 weeks)" | aha-2026 | p76 | p76/nutrition/3 | 2a |
| mobilization-time | ais | high-dose within 24 hours: not recommended | "within 24 hours of stroke onset is not recommended" | aha-2026 | p81 | p81/rehabilitation/3 | 3 |
| glibenclamide-no-benefit | large-hemispheric-infarction | age 18-70 years: IV glibenclamide not recommended | "18 to 70 years of age" | aha-2026 | p83 | p83/brain-swelling-medical-management/2 | 3 |
| craniectomy-eligibility | unilateral-mca-infarction | age <=60; deterioration <=48 hours: beneficial | RENDERED: "patients <=60 years of age with unilateral MCA infarctions who deteriorate neurologically within 48 hours" | aha-2026 | p83 | p83/supratentorial-infarction-surgical-management/2 | 1 |
| craniectomy-eligibility | unilateral-mca-infarction | age >60; deterioration <=48 hours: may consider | "patients >60 years of age with unilateral MCA infarctions who deteriorate neurologically within 48 hours" | aha-2026 | p83 | p83/supratentorial-infarction-surgical-management/3 | 2b |
| craniectomy-eligibility | ais-after-ivt | malignant edema: craniectomy within 48 hours may be considered | "within 48 hours" | aha-2026 | p83 | p83/supratentorial-infarction-surgical-management/4 | 2b |
| craniectomy-eligibility | cerebellar-infarction | deterioration from brainstem compression or volume >=35 mL | RENDERED: "neurological deterioration from brainstem compression or volumes >=35 mL" | aha-2026 | p85 | p85/cerebellar-infarction-surgical-management/2 | 1 |

| ivt-agent-dose | adult-ais-ivt | alteplase 0.9 mg/kg, max 90 mg; 10% bolus over 1 minute, remainder over 60 minutes | "0.9 mg/kg, maximum dose 90 mg over 60 min with initial 10% of dose given as bolus over 1 min" | aha-2019 | p23 | p23/narrative/1 | narrative |
| ivt-window | ais | within 3 hours; selected patients also 3-4.5 hours | RENDERED: "patients who may be treated within 3 h; patients should receive the criteria outlined in this table to determine patient eligibility within 3 and 4.5 h" | aha-2019 | p23 | p23/narrative/2 | narrative |
| pre-ivt-bp | ais | <185/110 mm Hg | "BP <185/110 mm Hg" | aha-2019 | p23 | p23/narrative/3 | narrative |
| glucose-low | ais | initial glucose >50 mg/dL for alteplase eligibility | "initial glucose levels >50 mg/dL" | aha-2019 | p23 | p23/narrative/4 | narrative |
| ivt-window | ais | age >80 in 3-4.5-hour window may be treated | ">80 y of age presenting in the 3- to 4.5-h window" | aha-2019 | p24 | p24/narrative/1 | narrative |
| ivt-window | ais | NIHSS >25 at 3-4.5 hours: benefit uncertain | "benefit of IV alteplase between 3 and 4.5 h from symptom onset for patients with very severe stroke symptoms (NIHSS score >25) is uncertain" | aha-2019 | p24 | p24/narrative/2 | narrative |
| ivt-eligibility-laboratory | ais | glucose <50 or >400 mg/dL: normalize then reassess | "initial glucose levels <50 or >400 mg/dL" | aha-2019 | p24 | p24/narrative/3 | narrative |
| ivt-eligibility-laboratory | ais | warfarin INR <=1.7 or PT <15 seconds | RENDERED: "history of warfarin use and an INR <=1.7 or a PT <15 s" | aha-2019 | p24 | p24/narrative/4 | narrative |
| ivt-window | ais | lumbar dural puncture within preceding 7 days: case-by-case | "preceding 7 d" | aha-2019 | p24 | p24/narrative/5 | narrative |
| ivt-window | ais | recent major trauma or surgery within 14 days: carefully selected | "within 14 d" | aha-2019 | p24 | p24/narrative/6 | narrative |
| ivt-window | ais | unruptured aneurysm <10 mm: reasonable | "small or moderate-sized (<10 mm)" | aha-2019 | p25 | p25/narrative/1 | narrative |
| ivt-window | ais | prior CMBs 1-10: reasonable; >10: uncertain | "small number (1-10) of CMBs" | aha-2019 | p25 | p25/narrative/2 | narrative |
| ivt-window | ais | recent MI within preceding 3 months: individualized | "recent MI in the past 3 mo" | aha-2019 | p25 | p25/narrative/3 | narrative |
| ivt-window | ais | life expectancy >6 months in systemic malignancy: may benefit | RENDERED: "Patients with systemic malignancy and reasonable (>6 mo) life expectancy may benefit from IV alteplase" | aha-2019 | p26 | p26/narrative/1 | narrative |
| ivt-window | ais | postpartum <14 days: safety not established | "early postpartum period (<14 d after delivery)" | aha-2019 | p26 | p26/narrative/2 | narrative |
| ivt-window | ais | mild nondisabling NIHSS 0-5: not recommended | RENDERED: "mild nondisabling stroke (NIHSS score 0-5), IV alteplase is not recommended" | aha-2019 | p26 | p26/narrative/3 | narrative |
| ivt-window | ais | prior ischemic stroke within 3 months: potentially harmful | "prior ischemic stroke within 3 mo" | aha-2019 | p26 | p26/narrative/4 | narrative |
| ivt-window | ais | recent GI bleeding within 21 days: high risk | "recent bleeding event within 21 d" | aha-2019 | p26 | p26/narrative/5 | narrative |
| ivt-eligibility-laboratory | ais | platelets <100,000/mm3; INR >1.7; aPTT >40 seconds; PT >15 seconds: do not administer | RENDERED: "platelets <100,000/mm3, INR >1.7, aPTT >40 s, or PT >15 s" | aha-2019 | p26 | p26/narrative/6 | narrative |
| ivt-eligibility-laboratory | ais | full-treatment LMWH in prior 24 hours: do not administer | "previous 24 h" | aha-2019 | p26 | p26/narrative/7 | narrative |
| ivt-eligibility-laboratory | ais | direct thrombin/factor Xa inhibitor unless normal tests or no dose >48 hours | "not received a dose of these agents for >48 h" | aha-2019 | p27 | p27/narrative/1 | narrative |
| aspirin-after-ivt | ais | IV aspirin within 90 minutes: do not administer | "within 90 min after the start of IV alteplase" | aha-2019 | p27 | p27/narrative/2 | narrative |
| ivt-monitoring | ais-after-ivt | q15 minutes for 2 hours; q30 minutes for 6 hours; hourly through 24 hours | "every 15 min during and after IV alteplase infusion for 2 h, then every 30 min for 6 h, then hourly until 24 h" | aha-2019 | p27 | p27/narrative/3 | narrative |
| ivt-monitoring | ais-after-ivt | more BP checks if SBP >180 or DBP >105 mm Hg; CT/MRI at 24 hours before antithrombotics | RENDERED: "Increase the frequency of BP measurements if SBP is >180 mm Hg or if DBP is >105 mm Hg; Obtain a follow-up CT or MRI scan at 24 h after IV alteplase" | aha-2019 | p27 | p27/narrative/4 | narrative |
| ich-reversal | ais-after-ivt | cryoprecipitate 10 U over 10-30 minutes; redose if fibrinogen <150 mg/dL | RENDERED: "Cryoprecipitate: 10 U infused over 10-30 min; administer additional dose for fibrinogen level of <150 mg/dL" | aha-2019 | p23 | p23/narrative/5 | narrative |
| ich-reversal | ais-after-ivt | TXA 1000 mg over 10 minutes or aminocaproic acid 4-5 g over 1 hour then 1 g IV | RENDERED: "Tranexamic acid 1000 mg IV infused over 10 min OR e-aminocaproic acid 4-5 g over 1 h, followed by 1 g IV" | aha-2019 | p23 | p23/narrative/6 | narrative |
| angioedema-treatment | ais-after-ivt | progression within 30 minutes signals high intubation risk | "rapid progression (within 30 min)" | aha-2019 | p23 | p23/narrative/7 | narrative |
| angioedema-treatment | ais-after-ivt | methylprednisolone 125 mg; diphenhydramine 50 mg; ranitidine 50 mg or famotidine 20 mg | RENDERED: "methylprednisolone 125 mg; diphenhydramine 50 mg; ranitidine 50 mg IV or famotidine 20 mg IV" | aha-2019 | p23 | p23/narrative/8 | narrative |
| angioedema-treatment | ais-after-ivt | epinephrine 0.1% 0.3 mL SC or 0.5 mL nebulized | "epinephrine (0.1%) 0.3 mL subcutaneously or by nebulizer 0.5 mL" | aha-2019 | p23 | p23/narrative/9 | narrative |
| angioedema-treatment | ais-after-ivt | icatibant 30 mg SC q6h, max 3 injections in 24 hours; C1 esterase 20 IU/kg | RENDERED: "Icatibant, 3 mL (30 mg) subcutaneously in abdominal area; additional injection of 30 mg may be administered at intervals of 6 h not to exceed a total of 3 injections in 24 h; C1 esterase inhibitor (20 IU/kg)" | aha-2019 | p23 | p23/narrative/10 | narrative |
| ivt-agent-dose | adult-ais-ivt | TNK 0.25 mg/kg max 25 mg reasonable before thrombectomy | RENDERED: "tenecteplase (single IV bolus of 0.25-mg/kg, maximum 25 mg) over IV alteplase" | aha-2019 | p28 | p28/narrative/1 | narrative |
| ivt-agent-dose | adult-ais-ivt | TNK 0.4 mg/kg might be considered in minor/no-major-occlusion stroke | RENDERED: "Tenecteplase administered as a 0.4-mg/kg single IV bolus" | aha-2019 | p28 | p28/narrative/2 | narrative |
| evt-eligibility | ais-lvo | mRS 0-1; ICA/M1; age >=18; NIHSS >=6; ASPECTS >=6; <=6 hours | RENDERED: "prestroke mRS score of 0 to 1; causative occlusion of the internal carotid artery or MCA segment 1 (M1); age >=18 years; NIHSS score of >=6; ASPECTS of >=6; treatment can be initiated within 6 hours" | aha-2019 | p29 | p29/narrative/1 | narrative |
| evt-eligibility | ais-lvo | 6-16 hours: DAWN/DEFUSE-3 criteria; 16-24 hours: DAWN criteria | RENDERED: "within 6 to 16 hours of last known normal and meet other DAWN or DEFUSE 3 eligibility criteria; within 16 to 24 hours of last known normal and meet other DAWN eligibility criteria" | aha-2019 | p31 | p31/narrative/1 | narrative |
| dapt-course | minor-ais-or-high-risk-tia | NIHSS <=3; start within 24 hours; 21 days | RENDERED: "minor noncardioembolic ischemic stroke (NIHSS score <=3) who did not receive IV alteplase, treatment with dual antiplatelet therapy started within 24 hours and continued for 21 days" | aha-2019 | p34 | p34/narrative/1 | narrative |
| craniectomy-eligibility | unilateral-mca-infarction | age <=60 or >60; deterioration within 48 hours | RENDERED: "patients <=60 years of age or patients >60 years of age who deteriorate neurologically within 48 hours" | aha-2019 | p44 | p44/narrative/1 | narrative |
| secondary-prevention | ais | cardiac monitoring at least 24 hours | RENDERED: "Cardiac monitoring should be performed for at least the first 24 hours" | aha-2019 | p47 | p47/narrative/1 | narrative |
| secondary-prevention | ais | atrial fibrillation: anticoagulation 4-14 days after onset | RENDERED: "initiate oral anticoagulation between 4 and 14 days after the onset" | aha-2019 | p51 | p51/narrative/1 | narrative |
| secondary-prevention | ais | cervical arterial dissection: antithrombotic therapy 3-6 months | "for 3 to 6 months" | aha-2019 | p51 | p51/narrative/2 | narrative |
| secondary-prevention | ais | restart antihypertensive therapy if BP >140/90 mm Hg | "BP >140/90 mm Hg" | aha-2019 | p55 | p55/narrative/1 | narrative |

## Conflicts

**CONFLICT: angioedema-treatment** - These are sequential or alternative parts of one 2019 response table, not competing estimates: `progression within 30 minutes signals high intubation risk`; `methylprednisolone 125 mg; diphenhydramine 50 mg; ranitidine 50 mg or famotidine 20 mg`; `epinephrine 0.1% 0.3 mL SC or 0.5 mL nebulized`; and `icatibant 30 mg SC q6h, max 3 injections in 24 hours; C1 esterase 20 IU/kg`.

**CONFLICT: aspirin-after-ivt** - For population `ais`, the two sources express the same prohibition with different scope: `concurrent or within 90 minutes after IVT: do not administer` and `IV aspirin within 90 minutes: do not administer`; `first 24 hours: risk uncertain` applies to the distinct `ais-after-ivt` population.

**CONFLICT: craniectomy-eligibility** - For `unilateral-mca-infarction`, the source-specific age limbs are retained: `age <=60; deterioration <=48 hours: beneficial`; `age >60; deterioration <=48 hours: may consider`; and the 2019 combined summary `age <=60 or >60; deterioration within 48 hours`; the other populations have separate nonconflicting rows.

**CONFLICT: dapt-course** - These rows describe different agents, risk strata, and start windows: `NIHSS <=3 or ABCD2 >=4: ticagrelor not recommended over aspirin`; `NIHSS <=3 or ABCD2 >=4; start <=24 hours; DAPT 21 days then SAPT`; `<24 hours; NIHSS <=5; ABCD2 >=6 or stenosis >=50%; ticagrelor plus aspirin 30 days`; `within 24-72 hours; NIHSS <=5 or NIHSS 4-5 within 24 hours; stenosis >=50%; DAPT 21 days`; `NIHSS <=3; ABCD2 >=4; <=24 hours; CYP2C19 LOF: ticagrelor plus aspirin 21 days`; and the 2019 row `NIHSS <=3; start within 24 hours; 21 days`.

**CONFLICT: evt-eligibility** - EVT eligibility is stratified, not a single cutoff: `ICA/M1; <=6 hours; NIHSS >=6; mRS 0-1; ASPECTS 3-10`; `ICA/M1; 6-24 hours; NIHSS >=6; mRS 0-1; ASPECTS >=6`; `age <80; 6-24 hours; NIHSS >=6; mRS 0-1; ASPECTS 3-5`; `age <80; <=6 hours; NIHSS >=6; mRS 0-1; ASPECTS 0-2`; `<=6 hours; NIHSS >=6; ASPECTS >=6; mRS 2`; `<=6 hours; NIHSS >=6; ASPECTS >=6; mRS 3-4`; `dominant M2; <=6 hours; mRS 0-1; NIHSS >=6; ASPECTS >=6`; `basilar; mRS 0-1; NIHSS >=10; PC-ASPECTS >=6; <=24 hours`; `basilar; mRS 0-1; NIHSS 6-9; PC-ASPECTS >=6; <=24 hours: uncertain`; the 2019 criteria `mRS 0-1; ICA/M1; age >=18; NIHSS >=6; ASPECTS >=6; <=6 hours`; and `6-16 hours: DAWN/DEFUSE-3 criteria; 16-24 hours: DAWN criteria`.

**CONFLICT: evt-imaging-window** - These are complementary triage decisions: `within 24 hours`; `6-24 hours: adjunct perfusion imaging if immediately available`; and `RACE >4 may support direct-to-angiography triage`.

**CONFLICT: extended-ivt-window** - Imaging selection differs by onset information: `unknown onset >4.5 hours: MRI DWI-FLAIR selection` and `unknown onset 4.5-24 hours: CTP or MR selection`.

**CONFLICT: glucose-low** - The sources address different actions: `<60 mg/dL: treat` is acute hypoglycemia management, while `initial glucose >50 mg/dL for alteplase eligibility` is a 2019 IVT eligibility boundary.

**CONFLICT: glucose-target** - The recommended moderate range `140-180 mg/dL` contrasts with `IV insulin target 80-130 mg/dL: not recommended`.

**CONFLICT: ich-reversal** - These are alternative reversal measures from one table: `cryoprecipitate 10 U over 10-30 minutes; redose if fibrinogen <150 mg/dL` and `TXA 1000 mg over 10 minutes or aminocaproic acid 4-5 g over 1 hour then 1 g IV`.

**CONFLICT: ivt-agent-dose** - Agent and era explain the distinct values: `TNK 0.25 mg/kg (max 25 mg) or alteplase 0.9 mg/kg (max 90 mg)`; `TNK 0.4 mg/kg: not recommended`; `alteplase 0.9 mg/kg, max 90 mg; 10% bolus over 1 minute, remainder over 60 minutes`; the 2019 alternative `TNK 0.25 mg/kg max 25 mg reasonable before thrombectomy`; and its superseded narrow option `TNK 0.4 mg/kg might be considered in minor/no-major-occlusion stroke`.

**CONFLICT: ivt-eligibility-laboratory** - These are separate exclusion or reassessment tests: `glucose <50 or >400 mg/dL: normalize then reassess`; `warfarin INR <=1.7 or PT <15 seconds`; `platelets <100,000/mm3; INR >1.7; aPTT >40 seconds; PT >15 seconds: do not administer`; `full-treatment LMWH in prior 24 hours: do not administer`; and `direct thrombin/factor Xa inhibitor unless normal tests or no dose >48 hours`.

**CONFLICT: ivt-monitoring** - The 2019 protocol separates routine cadence `q15 minutes for 2 hours; q30 minutes for 6 hours; hourly through 24 hours` from escalation and imaging `more BP checks if SBP >180 or DBP >105 mm Hg; CT/MRI at 24 hours before antithrombotics`.

**CONFLICT: ivt-window** - For population `ais`, these values apply to different onset patterns, agents, and risk modifiers: `unknown onset: within 4.5 hours of recognition; DWI lesion less than one-third MCA and no marked FLAIR change`; `wake-up within 9 hours of sleep midpoint or 4.5-9 hours LKW with salvageable penumbra`; `reteplase may be considered within 4.5 hours if no EVT`; `mutant prourokinase may be considered within 4.5 hours if no EVT`; `desmoteplase at 3-9 hours: not recommended`; `urokinase or streptokinase within 6 hours: no benefit / do not administer`; `CRAO disabling visual loss within 4.5 hours: usefulness uncertain`; `within 3 hours; selected patients also 3-4.5 hours`; `age >80 in 3-4.5-hour window may be treated`; `NIHSS >25 at 3-4.5 hours: benefit uncertain`; `lumbar dural puncture within preceding 7 days: case-by-case`; `recent major trauma or surgery within 14 days: carefully selected`; `unruptured aneurysm <10 mm: reasonable`; `prior CMBs 1-10: reasonable; >10: uncertain`; `recent MI within preceding 3 months: individualized`; `life expectancy >6 months in systemic malignancy: may benefit`; `postpartum <14 days: safety not established`; `mild nondisabling NIHSS 0-5: not recommended`; `prior ischemic stroke within 3 months: potentially harmful`; and `recent GI bleeding within 21 days: high risk`; the distinct `ais-lvo` value is `4.5-24 hours with salvageable penumbra and no EVT`.

**CONFLICT: no-reperfusion-bp** - These are opposite sides of one boundary: `BP >=220/120 mm Hg: benefit of treatment in 48-72 hours uncertain` versus `BP <220/120 mm Hg: treatment in 48-72 hours not effective`.

**CONFLICT: pediatric-evt-eligibility** - Age and time strata differ: `age >=6 years; <=6 hours; LVO`; `age >=6 years; 6-24 hours; LVO and salvageable tissue`; and `age 28 days-6 years; <=24 hours; LVO and salvageable tissue`.

**CONFLICT: post-evt-bp** - The general ceiling `<=180/105 mm Hg during and 24 hours after EVT` differs from the harmful intensive target `after mTICI 2b/2c/3, target <140 mm Hg for 72 hours: harmful`.

**CONFLICT: post-ivt-bp** - Routine maintenance `<180/105 mm Hg for at least 24 hours` is retained beside the rejected intensive strategy `target <140 vs <180 mm Hg: not recommended`.

**CONFLICT: pre-ivt-bp** - The sources state the same eligibility boundary in two forms: `SBP <185 and DBP <110 mm Hg` and `<185/110 mm Hg`.

**CONFLICT: secondary-prevention** - These are different acute-admission prevention actions: `cardiac monitoring at least 24 hours`; `atrial fibrillation: anticoagulation 4-14 days after onset`; `cervical arterial dissection: antithrombotic therapy 3-6 months`; and `restart antihypertensive therapy if BP >140/90 mm Hg`.

## Coverage

The 2019 source has no exact recommendation index; its complete narrative and table
read is represented by the locators above. The independent reconciliation initially
found 121 uncited identifiers in the 2026 exact record. Four contained decision points
and are now rows: `p12/prehospital-assessment-and-management/6`,
`p34/head-positioning/2`, `p35/blood-pressure-management/6`, and
`p63/antiplatelet-treatment-continued/9`. The remaining 117 identifiers are accounted
for individually below. A stated number was excluded only when it was a service
identifier, an operational example rather than a recommendation boundary, a study or
outcome statistic, a citation, or did not change the qualitative patient-care action.

- `p10/stroke-awareness-population-level/1` - Qualitative public education recommendation; 9-1-1 is a service identifier, not a clinical threshold.
- `p10/stroke-awareness-population-level/2` - Qualitative design requirement for inclusive public education; no numeric patient-care decision point.
- `p10/stroke-awareness-population-level/3` - Sustained education is recommended without a numeric duration or cadence.
- `p10/stroke-awareness-population-level/4` - Qualitative targeted education recommendation for professionals; no numeric patient-care decision point.
- `p11/ems-systems-continued/3` - Quality-metric monitoring and feedback are recommended without a numeric trigger or target.
- `p11/ems-systems/1` - Regional stroke-system organization recommendation; its lettered facility categories are not numeric thresholds.
- `p11/ems-systems/2` - Qualitative prehospital triage-protocol recommendation; no numeric cutoff is stated.
- `p12/prehospital-assessment-and-management/1` - Telephone assessment is reasonable; 9-1-1 is a service identifier, not a clinical cutoff.
- `p12/prehospital-assessment-and-management/2` - Use of a brief validated assessment tool is qualitative; no score threshold is specified.
- `p12/prehospital-assessment-and-management/3` - Advance hospital notification is recommended without a numeric timing target.
- `p12/prehospital-assessment-and-management/4` - Recommends against ambulance RIC but states no cuff pressure, cycle, or duration threshold.
- `p12/prehospital-assessment-and-management/5` - Recommends against prehospital GTN without a dose or BP boundary; remaining numbers are citations.
- `p12/prehospital-assessment-and-management/7` - Uncertainty about pediatric screening tools is qualitative; study-performance numbers are not recommendation cutoffs.
- `p14/ems-destination-management/1` - Transport to the closest appropriate stroke facility is qualitative; no distance or time boundary is prescribed.
- `p14/ems-destination-management/2` - Direct TSC transport can be beneficial, but no transport-time or distance cutoff is stated.
- `p14/ems-destination-management/3` - Direct TSC transport is conditional on preserving IVT eligibility, without a numeric bypass limit.
- `p15/ems-destination-management-continued/4` - The 45-60-minute distance and 3-month outcome are an example and trial horizon, not recommended cutoffs.
- `p15/ems-destination-management-continued/5` - DIDO transfer prioritization is qualitative; no DIDO target is supplied.
- `p16/role-of-mobile-stroke-units/1` - Recommends MSU use where available without a numeric eligibility boundary.
- `p16/role-of-mobile-stroke-units/2` - MSU equipment capability requirement; no numeric patient-care decision point.
- `p16/role-of-mobile-stroke-units/3` - Qualitative benefit of streamlined MSU care; no numeric trigger or target.
- `p16/role-of-mobile-stroke-units/4` - Qualitative MSU triage recommendation for EVT-eligible patients; no new threshold beyond eligibility defined elsewhere.
- `p18/emergency-evaluation-of-patients-with/1` - Organized emergent evaluation is recommended for all ages without a numeric time target.
- `p18/emergency-evaluation-of-patients-with/2` - Pediatric stroke suspicion criterion is symptom-based and qualitative.
- `p18/emergency-evaluation-of-patients-with/3` - Acute stroke-team designation recommendation; no numeric composition or timing boundary.
- `p18/emergency-evaluation-of-patients-with/4` - Multidisciplinary stroke-team development is qualitative; no numeric decision point.
- `p18/emergency-evaluation-of-patients-with/5` - Fastest achievable treatment is directed without a stated numeric target.
- `p20/telemedicine/1` - Prehospital telemedicine feasibility recommendation; no numeric threshold.
- `p20/telemedicine/2` - Teleradiology availability recommendation; no numeric timing target.
- `p20/telemedicine/3` - Telestroke effectiveness statement; supporting study numbers do not set a decision boundary.
- `p20/telemedicine/4` - Telestroke mortality benefit is qualitative; outcome horizons are evidentiary, not recommendation cutoffs.
- `p20/telemedicine/5` - Telephone consultation can support IVT/EVT decisions without a numeric trigger.
- `p20/telemedicine/6` - 24-hour/day and 7-day/week coverage describe service availability, not a patient-care threshold.
- `p20/telemedicine/7` - Telestroke transfer triage is qualitative and adds no numeric EVT eligibility boundary.
- `p22/organization-and-integration-of-components/1` - Stroke-system organization recommendation; facility abbreviations and categories are nonnumeric.
- `p22/organization-and-integration-of-components/2` - The 24/7 phrase describes thrombectomy service availability, not a clinical decision cutoff.
- `p22/organization-and-integration-of-components/3` - Imaging capability requirement for transfer hospitals; no numeric threshold.
- `p22/organization-and-integration-of-components/4` - Protocol-adoption recommendation; no numeric patient-care decision point.
- `p22/organization-and-integration-of-components/5` - Process and outcome tracking recommendation without a numeric benchmark.
- `p22/organization-and-integration-of-components/6` - Credentialing recommendation; no numeric training or case-volume requirement is stated.
- `p22/organization-and-integration-of-components/7` - Optional vascular-imaging capability recommendation; no numeric threshold.
- `p22/organization-and-integration-of-components/8` - Mobile intervention teams may be considered based on local systems; no numeric trigger.
- `p24/stroke-registries-quality-improvement-and/1` - Multicomponent QI participation is qualitative; references and evidence statistics do not set a threshold.
- `p24/stroke-registries-quality-improvement-and/2` - Registry participation recommendation; no numeric performance target.
- `p24/stroke-registries-quality-improvement-and/3` - Baseline severity documentation is recommended without a score cutoff.
- `p26/initial-vascular-and-multimodal-imaging/1` - Initial NCCT or MRI is recommended without a numeric imaging deadline or burden cutoff.
- `p26/initial-vascular-and-multimodal-imaging/3` - CTA/CTP should not await creatinine, but no creatinine value is stated.
- `p26/initial-vascular-and-multimodal-imaging/4` - Pediatric MRI/MRA preference is qualitative; no age or time boundary is stated.
- `p27/initial-vascular-and-multimodal-imaging/11` - DTAS without repeat imaging is conditional on clinical change or transfer delay, neither quantified.
- `p31/other-diagnostic-tests/1` - Baseline ECG should not delay reperfusion; no delay duration is specified.
- `p31/other-diagnostic-tests/2` - Baseline troponin should not delay reperfusion; no value or delay duration is specified.
- `p32/airway-breathing-and-oxygenation/1` - Airway and ventilatory support are based on clinical ability and course, not a numeric cutoff.
- `p32/airway-breathing-and-oxygenation/4` - HBO for arterial air embolism is qualitative; no pressure, oxygen fraction, or duration is prescribed.
- `p32/airway-breathing-and-oxygenation/5` - Supplemental oxygen is not recommended for nonhypoxic IVT-ineligible patients; hypoxia is quantified in the separate oxygen row.
- `p32/airway-breathing-and-oxygenation/6` - HBO no-benefit statement supplies no new numeric treatment boundary.
- `p35/blood-pressure-management/1` - Correct hypotension and hypovolemia to adequate organ perfusion; no BP or volume target is stated.
- `p35/blood-pressure-management/2` - Comorbidity-driven hypertension treatment is qualitative and diagnosis-dependent.
- `p37/temperature-management/1` - Target normothermia in hyperthermia without a numeric temperature boundary.
- `p37/temperature-management/2` - Identify and treat the source of hyperthermia; no numeric threshold.
- `p37/temperature-management/3` - Recommends against induced hypothermia in normothermia without a temperature or duration target.
- `p46/other-iv-fibrinolytics-and-sonothrombolysis/4` - The 4.5-hour mutant-prourokinase combination boundary is already represented by the adjacent agent-specific IVT-window row; this adds no distinct cutoff.
- `p46/other-iv-fibrinolytics-and-sonothrombolysis/6` - The 6-hour streptokinase no-benefit boundary is already represented by the combined urokinase/streptokinase row; 90 days is an outcome horizon.
- `p46/other-iv-fibrinolytics-and-sonothrombolysis/7` - Sonothrombolysis no-benefit statement has no treatment cutoff; 90 days is an outcome horizon.
- `p47/other-specific-circumstances/1` - Sickle-cell IVT benefit is qualitative; no laboratory, age, or time threshold is added.
- `p53/concomitant-with-ivt/1` - Recommends IVT before EVT when both are eligible; numeric eligibility boundaries are captured in their dedicated rows.
- `p53/concomitant-with-ivt/2` - Recommends immediate IVT without observation; no numeric observation duration is prescribed.
- `p54/endovascular-thrombectomy-for-adult/8` - Recommends against EVT for listed medium/distal vessels without a numeric anatomy, score, or time cutoff.
- `p58/endovascular-techniques/1` - Stent retriever and aspiration thrombectomy are endorsed without a numeric device or procedure threshold.
- `p58/endovascular-techniques/2` - Balloon-guide catheter use is qualitative; no numeric pressure or timing target.
- `p58/endovascular-techniques/3` - Rescue adjuncts may be reasonable without a numeric trigger or dose.
- `p58/endovascular-techniques/4` - Intra-arterial fibrinolysis as salvage is qualitative; no dose or time boundary.
- `p58/endovascular-techniques/5` - General anesthesia or conscious sedation selection is individualized without a numeric cutoff.
- `p58/endovascular-techniques/6` - Rescue balloon angioplasty or stenting is qualitative; no stenosis percentage is prescribed.
- `p58/endovascular-techniques/7` - Rescue intra-arterial tirofiban is qualitative; no dose or infusion duration is prescribed.
- `p58/endovascular-techniques/8` - Adjunct intra-arterial fibrinolytic uncertainty is qualitative; trial doses are evidence, not recommendation values.
- `p58/endovascular-techniques/9` - Preoperative IV tirofiban no-benefit statement supplies no dose or timing threshold.
- `p63/antiplatelet-treatment-continued/3` - IV tirofiban efficacy is not established; no dose or timing threshold is stated.
- `p63/antiplatelet-treatment-continued/4` - IV abciximab is not recommended without a dose or timing boundary.
- `p63/antiplatelet-treatment-continued/5` - Antiplatelet preference over anticoagulation is qualitative.
- `p63/antiplatelet-treatment-continued/6` - Antiplatelet-agent selection is individualized without a numeric cutoff.
- `p63/antiplatelet-treatment-continued/8` - Aspirin dose increase or agent change is uncertain, but no dose is specified.
- `p63/antiplatelet-treatment-continued/10` - Triple-antiplatelet harm is a treatment-count description, not a dose, duration, or clinical threshold.
- `p63/antiplatelet-treatment-continued/11` - Routine antiplatelet addition to anticoagulation is harmful in the stated diagnoses; no numeric boundary.
- `p63/antiplatelet-treatment-continued/16` - Aspirin should not substitute for reperfusion; no numeric decision point.
- `p63/antiplatelet-treatment-continued/18` - Eptifibatide after IVT is not recommended; 3 hours and 3 months describe the studied treatment and outcome horizons already governed by IVT timing, not a new threshold.
- `p69/anticoagulants/1` - Early versus delayed anticoagulation is reasonable in selected patients, but neither interval is quantified.
- `p69/anticoagulants/2` - Urgent anticoagulation benefit in high-grade ICA stenosis is uncertain; high-grade is not numerically defined here.
- `p69/anticoagulants/3` - Short-term anticoagulation uncertainty is stated without a duration.
- `p69/anticoagulants/4` - Anticoagulation after hemorrhagic transformation is scenario-dependent without a numeric trigger.
- `p69/anticoagulants/5` - Argatroban adjunct no-benefit statement supplies no dose or timing threshold.
- `p74/dysphagia/1` - Swallow screening is required before oral intake; no numeric timing or score cutoff.
- `p75/dysphagia-continued/2` - Qualified-personnel requirement for screening; no numeric threshold.
- `p75/dysphagia-continued/3` - Instrumental assessment after failed bedside screening is qualitative.
- `p75/dysphagia-continued/4` - Oral hygiene may reduce pneumonia without a numeric frequency or duration.
- `p75/dysphagia-continued/5` - PES may improve swallowing in non-tracheostomized dysphagia; no stimulation parameter is given.
- `p75/dysphagia-continued/6` - PES after ventilator weaning is reasonable without a numeric ventilation or stimulation threshold.
- `p77/deep-vein-thrombosis-prophylaxis/1` - IPC is recommended for impaired mobility without a numeric mobility or device setting.
- `p77/deep-vein-thrombosis-prophylaxis/2` - Prophylactic UFH or LMWH is reasonable, but no dose or start time is specified.
- `p77/deep-vein-thrombosis-prophylaxis/3` - Survival benefit uncertainty for prophylactic heparin has no dose or duration cutoff.
- `p77/deep-vein-thrombosis-prophylaxis/4` - LMWH-versus-UFH uncertainty has no dose or timing boundary.
- `p77/deep-vein-thrombosis-prophylaxis/5` - Elastic-stockings harm is qualitative; no compression value or duration.
- `p79/depression/1` - Structured depression screening is recommended while timing is explicitly uncertain.
- `p79/depression/2` - Depression treatment modalities are recommended without a numeric severity, dose, or duration threshold.
- `p80/other-in-hospital-management-considerations/1` - Palliative-care referral is individualized without a numeric prognosis boundary.
- `p80/other-in-hospital-management-considerations/2` - Routine prophylactic antibiotics have no benefit; no drug, dose, or duration is prescribed.
- `p80/other-in-hospital-management-considerations/3` - Routine bladder catheterization is discouraged without a duration threshold.
- `p81/rehabilitation/1` - Interdisciplinary rehabilitation assessment and provision are individualized without numeric intensity or timing.
- `p81/rehabilitation/2` - SSRI no-benefit statement supplies no dose or treatment duration.
- `p82/brain-swelling-general-recommendations/1` - Shared decision-making and care-preference discussion are qualitative.
- `p82/brain-swelling-general-recommendations/2` - Close monitoring during the first days is not converted to a numeric cadence or duration.
- `p82/brain-swelling-general-recommendations/3` - Early transfer for neurosurgical expertise is recommended without a numeric deadline.
- `p83/brain-swelling-medical-management/1` - Osmotic therapy as a bridge is reasonable without an osmolality, dose, or timing threshold.
- `p83/brain-swelling-medical-management/3` - Recommends against hypothermia, barbiturates, and corticosteroids without numeric parameters.
- `p83/supratentorial-infarction-surgical-management/1` - Decreased consciousness is a qualitative hemicraniectomy trigger; no score cutoff.
- `p85/cerebellar-infarction-surgical-management/1` - Ventriculostomy and possible decompression are based on clinical and anatomical factors without a numeric cutoff in this recommendation.
- `p85/seizures/1` - Antiseizure treatment after unprovoked seizure is individualized without a dose, recurrence score, or duration.
- `p85/seizures/2` - Prophylactic antiseizure medication is not recommended; no numeric threshold.
