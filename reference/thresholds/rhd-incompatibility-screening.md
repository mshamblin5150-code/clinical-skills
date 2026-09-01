# Rh(D) incompatibility screening — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute for the recommendation statement** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-rhd | USPSTF | USPSTF/rhrs | recommendation-statement | version not stated | not stated | http://www.preventiveservices.ahrq.gov | stated | exact |

The catalog records the source title and year as unknown. Those fields are not reconstructed from surrounding material.

## Scope

**Read:** all 3 source pages, including both summary recommendations, evidence assessments, update context, clinical considerations, references, recommendation-grade and evidence-quality appendices, publication information, and Task Force membership.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| recommendations, evidence assessments, update context, and publication information | 1 | yes |
| clinical considerations | 2 | yes |
| references | 2 | exempt: citation list has no patient-action prose |
| recommendation-grade and evidence-quality appendices, publication information, and membership | 3 | read 2026-09-01; blind 2026-09-01 |

citations resolved against C:/codeing/guidelines-src on 2026-09-01

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| all-pregnant-first-visit | all pregnant women during their first visit for pregnancy-related care |
| unsensitized-rhd-negative-24-28-father-not-known-negative | unsensitized Rh(D)-negative pregnant women at 24-28 weeks' gestation unless the biological father is known to be Rh(D)-negative |
| unsensitized-rhd-negative-postpartum-positive-infant | unsensitized Rh(D)-negative women who deliver an Rh(D)-positive or weakly Rh(D)-positive infant |
| unsensitized-rhd-negative-procedure-13plus-father-not-known-negative | unsensitized Rh(D)-negative women at 13 or more weeks' gestation after amniocentesis or induced or spontaneous abortion unless the biological father is known to be Rh(D)-negative |
| unsensitized-rhd-negative-procedure-under-13-father-not-known-negative | unsensitized Rh(D)-negative women at less than 13 weeks' gestation after amniocentesis or induced or spontaneous abortion unless the biological father is known to be Rh(D)-negative |
| unsensitized-rhd-negative-other-obstetric-event | unsensitized Rh(D)-negative women after another listed obstetric procedure or complication |

## Quantities

| key | verbatim |
| --- | --- |
| initial-rhd-screening | initial maternal Rh(D) blood typing and antibody testing |
| repeat-rhd-antibody-testing | repeated maternal Rh(D) antibody-testing timing and paternal-status exception |
| routine-antepartum-rhig-dose | Rh(D) immunoglobulin dose after repeat antibody testing |
| postpartum-rhig-dose | postpartum Rh(D) immunoglobulin repeat-dose indication |
| postpartum-rhig-timing | preferred postpartum Rh(D) immunoglobulin timing and interval uncertainty |
| procedure-rhig-dose | Rh(D) immunoglobulin dose after amniocentesis or induced or spontaneous abortion |
| other-event-rhig-uncertainty | evidence uncertainty for routine Rh(D) immunoglobulin after other obstetric procedures or complications |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| initial-rhd-screening | all-pregnant-first-visit | perform Rh(D) blood typing and antibody testing at the first pregnancy-related visit | The U.S. Preventive Services Task Force (USPSTF) strongly recommends Rh (D) blood typing and antibody testing for all pregnant women during their first visit for pregnancy-related care. | uspstf-rhd | p1 | p1/screening-for-rh-d-incompatibility/1 | A |
| repeat-rhd-antibody-testing | unsensitized-rhd-negative-24-28-father-not-known-negative | repeat Rh(D) antibody testing at 24-28 weeks' gestation unless the biological father is known Rh(D)-negative | The USPSTF recommends repeated Rh (D) antibody testing for all unsensitized Rh (D)-negative women at 24-28 weeks' gestation, unless the biological father is known to be Rh (D)-negative. | uspstf-rhd | p1 | p1/screening-for-rh-d-incompatibility/2 | B |
| routine-antepartum-rhig-dose | unsensitized-rhd-negative-24-28-father-not-known-negative | administer a full 300 µg dose after repeat antibody testing at 24-28 weeks | RENDERED: Administration of a full (300µg) dose of Rh (D) immunoglobulin is recommended for all unsensitized Rh (D)-negative women after repeated antibody testing at 24-28 weeks' gestation. | uspstf-rhd | p2 | p2/narrative/routine-antepartum-rhig | narrative |
| postpartum-rhig-dose | unsensitized-rhd-negative-postpartum-positive-infant | repeat a dose postpartum when the infant is Rh(D)-positive or weakly Rh(D)-positive | RENDERED: If an Rh (D)-positive or weakly Rh (D)-positive ... infant is delivered, a dose of Rh (D) immunoglobulin should be repeated postpartum | uspstf-rhd | p2 | p2/narrative/postpartum-rhig-dose | narrative |
| postpartum-rhig-timing | unsensitized-rhd-negative-postpartum-positive-infant | preferably administer within 72 hours after delivery; other postdelivery intervals have not been studied | RENDERED: preferably within 72 hours after delivery. Administering Rh (D) immunoglobulin at other intervals after delivery has not been studied. | uspstf-rhd | p2 | p2/narrative/postpartum-rhig-timing | narrative |
| procedure-rhig-dose | unsensitized-rhd-negative-procedure-13plus-father-not-known-negative | administer a full dose after amniocentesis or induced or spontaneous abortion | RENDERED: Unless the biological father is known to be Rh (D)-negative, a full dose of Rh (D) immunoglobulin is recommended ... after amniocentesis and after induced or spontaneous abortion | uspstf-rhd | p2 | p2/narrative/procedure-rhig-full-dose | narrative |
| procedure-rhig-dose | unsensitized-rhd-negative-procedure-under-13-father-not-known-negative | 50 µg is sufficient after amniocentesis or induced or spontaneous abortion before 13 weeks | RENDERED: if the pregnancy is less than 13 weeks, a 50 µg dose is sufficient. | uspstf-rhd | p2 | p2/narrative/procedure-rhig-under-13 | narrative |
| other-event-rhig-uncertainty | unsensitized-rhd-negative-other-obstetric-event | benefit of routine Rh(D) immunoglobulin is uncertain after chorionic villus sampling, ectopic pregnancy termination, cordocentesis, fetal surgery or manipulation including external version, antepartum placental hemorrhage, abdominal trauma, antepartum fetal death, or stillbirth | RENDERED: The benefit of routine administration of Rh (D) immunoglobulin after other obstetric procedures or complications such as chorionic villus sampling, ectopic pregnancy termination, cordocentesis, fetal surgery or manipulation (including external version), antepartum placental hemorrhage, abdominal trauma, antepartum fetal death, or stillbirth is uncertain due to inadequate evidence. | uspstf-rhd | p2 | p2/narrative/other-event-rhig-uncertainty | narrative |

## Conflicts

No same-population, same-quantity conflict was identified. First-visit testing and repeat testing at 24-28 weeks are sequential actions. The 300 µg and 50 µg procedure doses apply to complementary gestational-age populations, and the preferred 72-hour postpartum timing is paired with an evidence gap rather than a contradictory alternative interval.

## Coverage

The exact recommendation artifact contains **2 recommendation identifiers**. This sheet cites both and scopes out **0**; **2 = 2 + 0**.

ADR 0009 disposition:

- retained actions include first-visit Rh(D) typing and antibody testing for all pregnant women; repeat antibody testing and the paternal Rh(D)-negative exception at 24-28 weeks; antepartum, postpartum, postamniocentesis, and postabortion Rh(D) immunoglobulin dosing; the less-than-13-week dose branch; preferred postpartum timing; and uncertainty after other obstetric events;
- the source's clinical-consideration actions are presented as USPSTF-statement narrative. The three-page document does not quote a separate professional society's guidance, so no external recommendation was invented or merged;
- the phrase `full dose` is tied to the source's explicit full-dose definition of 300 µg on the same clinical-considerations page; the 50 µg branch is preserved only for pregnancies less than 13 weeks;
- evidence grades, evidence-quality definitions, prior-guideline dates, publication and contact information, Task Force membership, citation numbers, reference-list values, and evidence statements that do not add a patient action were not interpreted as separate thresholds.
