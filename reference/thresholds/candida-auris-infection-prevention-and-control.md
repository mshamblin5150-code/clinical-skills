# Candida auris infection prevention and control — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points only, distilled from the complete source below. **Not a substitute
for the consensus statement** and not a clinical instruction.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shea-2026-cauris | IDSA | IDSA/infection-prevention-and-control-of-candida-auris-in-pediatric-settings | guideline | 2026 consensus statement | 2026 | https://doi.org/10.1017/ash.2026.10419 | stated |  |

## Scope

**Read:** the complete 13-page consensus statement, page by page, including title
material, abstract, purpose, terminology, sponsorship, methods, voting framework,
background, risk factors, all general and pediatric recommendations and remarks,
acute and non-acute healthcare settings, non-healthcare congregate settings,
acknowledgments, disclosures, and references. All screening, isolation, rooming-in,
breastfeeding, visitation, decolonization, equipment, environmental-cleaning,
communication, and facility-setting sections were read. The recommendation artifact
declares `nothing-found` and contains no recommendation identifiers, so that empty
index is not treated as evidence that the document contains no decision point.

**Not read:** the separately hosted supplementary material is outside the cataloged
source PDF and this sheet makes no claim about it. Nothing within the 13-page source
PDF was left unread.

**Scoped out under ADR 0009's numeric patient-action rule:** publication and access
dates, author affiliations, reference numbers, journal volumes and pages, panel size,
vote counts and percentages, outbreak prevalence and sample counts, evidence-study
intervals, organism survival and environmental recontamination observations, and
other epidemiologic figures were read but do not themselves change a patient or IPC
action in this consensus statement. Qualitative actions without a stated numeric
interval, distance, count, dose, cutoff, or target—including actions triggered only
by each use or discharge—remain outside this numeric sheet even though they remain
recommendations in the source.

**Source: `shea-2026-cauris`**

| span | pages | read |
| --- | --- | --- |
| title material, purpose, terminology, methods, voting framework, background, risk factors, and response recommendations | 1-4 | read 2026-08-31; blind 2026-08-31 |
| surveillance and screening intervals, swab collection, Contact Precautions, and hand hygiene | 5-6 | yes |
| room placement, breastfeeding, skin-to-skin care, visitation, decolonization, and environmental controls | 7-8 | yes |
| equipment, environmental cleaning, communication, non-acute healthcare, and non-healthcare congregate settings | 9-11 | yes |
| references | 12-13 | read 2026-08-31; blind 2026-08-31 |

citations resolved against C:/codeing/guidelines-src on 2026-08-31

extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| unit-suspected-ongoing-transmission | a healthcare unit with suspected or ongoing C. auris transmission |
| nicu-infant-colonized-birth-parent | an infant in the NICU whose birth parent is colonized or infected with C. auris |
| open-bay-nicu-infant-cauris | an infant with C. auris colonization or infection in a NICU with open bays or pods |
| stored-ebm-cauris-dyad | stored expressed breast milk for an infant or caregiver affected by C. auris |
| hospitalized-patient-cauris | a hospitalized patient with C. auris colonization or infection |
| child-of-caregiver-cauris | a pediatric patient whose caregiver is colonized or infected with C. auris |

## Quantities

| key | verbatim |
| --- | --- |
| point-prevalence-survey-interval | frequency of point prevalence surveys during suspected or ongoing C. auris transmission |
| nicu-infant-screening-schedule | screening schedule for an infant whose birth parent is colonized or infected with C. auris |
| open-bay-isolette-distance | distance between isolettes or cribs in an open-bay NICU |
| stored-ebm-environment | containment and cleaning cadence for stored expressed breast milk |
| patient-room-cleaning | frequency of room cleaning and disinfection for a patient with C. auris |
| caregiver-associated-environment-cleaning | frequency of cleaning and disinfecting the room and equipment of a child whose caregiver has C. auris |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| point-prevalence-survey-interval | unit-suspected-ongoing-transmission | survey the entire unit every 7-14 days; reduce frequency as transmission decreases | perform point prevalence surveys every 7 to 14 days on the entire unit | shea-2026-cauris | p5 | p5/narrative/point-prevalence-survey-interval | narrative |
| nicu-infant-screening-schedule | nicu-infant-colonized-birth-parent | screen at birth after bathing; on the seventh day if still hospitalized; every 2 weeks thereafter while hospitalized; as needed; discharge; and readmission | RENDERED: At birth, after bathing; on the seventh day of life if the neonate remains hospitalized; every 2 weeks thereafter if the infant remains hospitalized; as needed to inform decision-making; at hospital discharge; and at readmission | shea-2026-cauris | p5 | p5/narrative/nicu-infant-screening-schedule | narrative |
| open-bay-isolette-distance | open-bay-nicu-infant-cauris | AAP/FGI recommend 8 feet between isolettes or cribs; follow local IPC and public-health placement guidance because distance may vary with resources | RENDERED: AAP and FGI recommend 8 feet of distance between isolettes; follow local infection-prevention-and-control and public-health guidance because distance may vary with resources | shea-2026-cauris | p7 | p7/narrative/open-bay-isolette-distance | narrative |
| stored-ebm-environment | stored-ebm-cauris-dyad | double-bag stored EBM and use a separate freezer cleaned and disinfected daily; if unavailable, use a dedicated shelf cleaned and disinfected daily | RENDERED: Double-bag stored EBM and place it in a separate freezer cleaned and disinfected daily; if a separate freezer is unavailable, use a dedicated shelf cleaned and disinfected daily | shea-2026-cauris | p7 | p7/narrative/stored-ebm-environment | narrative |
| patient-room-cleaning | hospitalized-patient-cauris | clean and disinfect at least daily | At least daily, clean and disinfect the rooms of patients with C. auris colonization or infection | shea-2026-cauris | p8 | p8/narrative/patient-room-cleaning | narrative |
| caregiver-associated-environment-cleaning | child-of-caregiver-cauris | clean and disinfect the room and medical and non-medical equipment at least daily | RENDERED: Clean and disinfect the patient's room and medical and non-medical equipment at least daily | shea-2026-cauris | p9 | p9/narrative/caregiver-associated-environment-cleaning | narrative |

## Conflicts

## Coverage

The recommendation artifact for this source declares `nothing-found` and contains no
recommendation identifiers to cite or disposition. That empty index does not establish
document completeness; the complete 13-page span table under `## Scope` is the
coverage instrument. The separately hosted supplementary tables are outside the
cataloged source PDF. All 38 numbered pediatric recommendations and the intervening
general recommendations and remarks in the PDF were read; numeric patient-action
intervals, distances, counts, cutoffs, and targets retained from them are represented
above, while pure event-triggered actions, voting, evidence, epidemiologic, administrative, and reference figures
are explicitly dispositioned under `## Scope`.
