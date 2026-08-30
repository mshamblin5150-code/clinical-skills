# Guideline catalog

One row per document in the guideline corpus: 179 PDFs across nine societies,
**7,733 pages**, which is the sum of this file's own `page_count` column and
not a separate claim. **The corpus itself is not in this repo** and is not going
to be — most of it society-copyrighted, and a consumer needs the derived
facts rather than the sources. It lives at `C:/codeing/guidelines-src`. Issue
[#87](https://github.com/mshamblin5150-code/clinical-skills/issues/87).

This file exists because at 179 documents an agent cannot navigate the corpus by
reading it. Something has to choose *which document*, and that is a metadata
problem rather than a retrieval one — so the table is small enough to read in
full, and says what each document **is**, never what it says.

The five hand-read columns are independently audited in
[`guidelines-catalog-audit.md`](guidelines-catalog-audit.md). That ledger was
written blind to the values below, binds every reading to the PDF's SHA-256, and
records a page locator and evidence kind. `tools/guidelines_catalog.py` fails on
an incomplete reading, changed PDF bytes, or a disagreement that has no dated
clinician ruling.

When the mechanical catalog audit passes only because
`--allow-untrusted-provenance` admitted the extracted corpus, the catalog carries
the exact declaration block the command prints:

```text
accepted distrust against <corpus> on <date>:
  - <one artifact_provenance reason, verbatim>
  - <another artifact_provenance reason, verbatim>
```

Without that block the command reports shape-only mode rather than claiming the
corpus audit passed. A block for different distrust refuses, and a later trusted
passing audit refuses until the superseded block is deleted. `--draft` carries no
declaration: it prints values rather than a verdict, and the next audit grades what
a person pastes. This is the **held declaration** for accepted distrust under ADR
0019; ADR 0010's stderr trace and checkout-publication refusal remain unchanged.

## How to read a row

| Column | What it is |
| --- | --- |
| `society` | the source subdirectory, and the only place society is recorded |
| `filename` | as-is, the join key to everything else derived from this corpus |
| `title` | the document's own title, off its title page |
| `topic` | the condition or screening subject, in clinician-facing wording |
| `population` | who the document's front matter says it applies to |
| `year` | the publication year of **this** document |
| `page_count` | extracted, not claimed |
| `class` | `guideline`, `recommendation-statement`, `web-capture`, `draft`, `errata`, or `scope-of-work` |
| `citation` | the DOI, printed URL, or journal citation line this document states for itself |

The limits on what this column and its audit establish live in
`guidelines_catalog.NOT_REACHED`; this file does not maintain a prose copy.

**`year` is the load-bearing column.** The corpus holds a KDIGO 2009 document and
a KDIGO 2013 document sitting beside a 2026 AHA one. There is no common release
event across nine societies, so per-document version is the only staleness signal
that exists here — the same reasoning that put `meta.release` in
`reference/icd10cm-2026.sqlite`, where "2026" was equally true of two revisions
that code differently.

**`population` is the column most worth distrusting a guess in**, because it is
what decides whether a threshold applies to the patient at all. So it records
what the front matter *states*: `general` means the document says it applies
without restriction, and `?` means it does not say. `?` is never a shorthand for
"obviously adults" — several large cardiology and nephrology guidelines carry it
for exactly that reason, and each one is listed at the bottom of this file.

**`class` is the same vocabulary `tools/guidelines_search.py --class` takes.** It was
not: until [#185](https://github.com/mshamblin5150-code/clinical-skills/issues/185) the
extractor emitted `print-capture` and `unknown` where this column says `web-capture`
and nothing, so every row below not classed `guideline` named a filter value the index
answered with a **certified zero** — exit 1, that tool's code for a genuine absence.
`tools/guidelines_catalog.py` reads the legend row above against the extractor's own
constants — no corpus needed — and fails if the two sets part again.

**What that check reaches is the *code*, not a built index**, and the difference is
worth knowing before trusting a class off this table. The index is a build artifact
outside every checkout, so one built by an older extractor still answers the retired
vocabulary and no check here can see it. What says so is the search itself: since #185
a `--class` value no document carries **exits 2 and names what the index does hold**,
rather than reporting a zero. So a stale index is loud, and the honest form of the
claim above is that this table and the tool agree — not that whatever database is on
the machine does.

**`class` is decided by what the document is, not what it covers.**
`recommendation-statement` is USPSTF's document type and nobody else's here: the
90 USPSTF files each title themselves one. `web-capture` is a browser
print-to-PDF of a web page rather than a published document, which is the three
`ACIP/` files and only those — they carry a capture timestamp, a source URL and a
page-of-N footer, and they are CDC schedule pages rather than guideline documents
at all. `draft`, `errata`, and `scope-of-work` are likewise forms the document
names on its own first page. Everything else is `guideline`.

**The three narrower forms exist because calling them guidelines misled retrieval.**
`KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf` is a nine-page scope of
work for a guideline that does not exist yet, `ciab275.pdf` is a two-page errata
correcting two unrelated articles, and
`KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf` says on its own
cover that it is a public review draft. They class `scope-of-work`, `errata`, and
`draft`, respectively — [#107](https://github.com/mshamblin5150-code/clinical-skills/issues/107),
ruled 2026-08-20. Going the other way,
`Screening for Thyroid Cancer ... JAMA JAMA Network.pdf` is a JAMA article page
saved from a browser, so it is a web capture by origin — it is classed
`recommendation-statement` because `class` records what the document is, and what
it is, is a USPSTF recommendation statement.

**One `year` looks wrong against its own filename and is not.**
`KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf` is
dated `2021`, because the file is the 2021 guideline and its cover says so — it
also says, in as many words, that its ANCA vasculitis and lupus nephritis
chapters are **outdated** and that the 2024 updates to them are published
elsewhere. Both of those 2024 chapter updates are separate rows in this table.
Reading `2024` off the filename would date the document by the thing it tells you
it does not contain.

Recheck the mechanical columns, the independent audit, and the corpus digests with:

```bash
python tools/guidelines_catalog.py
```


| society | filename | title | topic | population | year | page_count | class | citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACIP | Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf | Recommended Vaccinations for Adults, Vaccines & Immunizations, CDC | adult immunization schedule | adult | ? | 7 | web-capture | https://www.cdc.gov/vaccines/imz-schedules/adult-easyread.html |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | Recommended Vaccines for Older Children, Vaccines & Immunizations, CDC | childhood and adolescent immunization schedule | pediatric, adolescent | ? | 6 | web-capture | https://www.cdc.gov/vaccines/imz-schedules/adolescent-easyread.html |
| ACIP | Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf | Recommended Vaccines for Young Children, Vaccines & Immunizations, CDC | childhood immunization schedule | pediatric | ? | 4 | web-capture | https://www.cdc.gov/vaccines/imz-schedules/child-easyread.html |
| ADA | standards-of-care-2026.pdf | Standards of Care in Diabetes-2026 | diabetes mellitus | ? | 2026 | 377 | guideline | ? |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | 2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Dyslipidemia | dyslipidemia | pediatric, adult | 2026 | 123 | guideline | 10.1161/CIR.0000000000001423 |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | 2024 Guideline for the Primary Prevention of Stroke | stroke primary prevention | adult | 2024 | 81 | guideline | 10.1161/STR.0000000000000475 |
| AHA ACC | creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of.pdf | 2026 AHA/ACC/ACCP/ACEP/CHEST/SCAI/SHM/SIR/SVM/SVN Guideline for the Evaluation and Management of Acute Pulmonary Embolism in Adults | acute pulmonary embolism | adult | 2026 | 75 | guideline | 10.1161/CIR.0000000000001415 |
| AHA ACC | gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf | 2024 ACC/AHA/AACVPR/APMA/ABC/SCAI/SVM/SVN/SVS/SIR/VESS Guideline for the Management of Lower Extremity Peripheral Artery Disease | lower extremity peripheral artery disease | ? | 2024 | 98 | guideline | 10.1161/CIR.0000000000001251 |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | 2018 AHA/ACC/AACVPR/AAPA/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Blood Cholesterol | blood cholesterol | adult | 2018 | 62 | guideline | 10.1161/CIR.0000000000000625 |
| AHA ACC | gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a.pdf | 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain | chest pain evaluation | adult | 2021 | 87 | guideline | 10.1161/CIR.0000000000001029 |
| AHA ACC | gurvitz-et-al-2025-2025-acc-aha-hrs-isachd-scai-guideline-for-the-management-of-adults-with-congenital-heart-disease-a.pdf | 2025 ACC/AHA/HRS/ISACHD/SCAI Guideline for the Management of Adults With Congenital Heart Disease | congenital heart disease | adult | 2025 | 137 | guideline | 10.1161/CIR.0000000000001402 |
| AHA ACC | heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf | 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure | heart failure | ? | 2022 | 138 | guideline | 10.1161/CIR.0000000000001063 |
| AHA ACC | isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf | 2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease | aortic disease | ? | 2022 | 149 | guideline | 10.1161/CIR.0000000000001106 |
| AHA ACC | joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf | 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation | atrial fibrillation | ? | 2023 | 156 | guideline | 10.1161/CIR.0000000000001193 |
| AHA ACC | jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection.pdf | 2025 AHA/ACC/AANP/AAPA/ABC/ACCP/ACPM/AGS/AMA/ASPC/NMA/PCNA/SGIM Guideline for the Prevention, Detection, Evaluation and Management of High Blood Pressure in Adults | high blood pressure | adult | 2025 | 105 | guideline | 10.1161/CIR.0000000000001356 |
| AHA ACC | kleindorfer-et-al-2021-2021-guideline-for-the-prevention-of-stroke-in-patients-with-stroke-and-transient-ischemic.pdf | 2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack | secondary stroke prevention | ? | 2021 | 104 | guideline | 10.1161/STR.0000000000000375 |
| AHA ACC | kusumoto-et-al-2018-2018-acc-aha-hrs-guideline-on-the-evaluation-and-management-of-patients-with-bradycardia-and.pdf | 2018 ACC/AHA/HRS Guideline on the Evaluation and Management of Patients With Bradycardia and Cardiac Conduction Delay | bradycardia and cardiac conduction delay | ? | 2018 | 101 | guideline | 10.1161/CIR.0000000000000628 |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | 2023 American Heart Association Focused Update on the Management of Patients With Cardiac Arrest or Life-Threatening Toxicity Due to Poisoning | cardiac arrest and life-threatening toxicity due to poisoning | pediatric, adult | 2023 | 36 | guideline | 10.1161/CIR.0000000000001161 |
| AHA ACC | ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf | 2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of Cardiovascular-Kidney-Metabolic Syndrome | cardiovascular-kidney-metabolic syndrome | ? | 2026 | 109 | guideline | 10.1161/CIR.0000000000001453 |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | 2020 AHA/ACC Guideline for the Diagnosis and Treatment of Patients With Hypertrophic Cardiomyopathy | hypertrophic cardiomyopathy | ? | 2020 | 74 | guideline | 10.1161/CIR.0000000000000937 |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | 2020 AHA/ACC Guideline for the Diagnosis and Treatment of Patients With Hypertrophic Cardiomyopathy: Executive Summary | hypertrophic cardiomyopathy | pediatric, adult | 2020 | 25 | guideline | 10.1161/CIR.0000000000000938 |
| AHA ACC | ommen-et-al-2024-2024-aha-acc-amssm-hrs-paces-scmr-guideline-for-the-management-of-hypertrophic-cardiomyopathy-a-report.pdf | 2024 AHA/ACC/AMSSM/HRS/PACES/SCMR Guideline for the Management of Hypertrophic Cardiomyopathy | hypertrophic cardiomyopathy | pediatric, adolescent, adult | 2024 | 73 | guideline | 10.1161/CIR.0000000000001250 |
| AHA ACC | otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf | 2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease | valvular heart disease | ? | 2020 | 156 | guideline | 10.1161/CIR.0000000000000923 |
| AHA ACC | powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018.pdf | Guidelines for the Early Management of Patients With Acute Ischemic Stroke: 2019 Update to the 2018 Guidelines for the Early Management of Acute Ischemic Stroke | acute ischemic stroke, early management | adult | 2019 | 75 | guideline | 10.1161/STR.0000000000000211 |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | 2026 Guideline for the Early Management of Patients With Acute Ischemic Stroke | acute ischemic stroke, early management | pediatric, adult | 2026 | 121 | guideline | 10.1161/STR.0000000000000513 |
| AHA ACC | rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf | 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes | acute coronary syndromes | ? | 2025 | 92 | guideline | 10.1161/CIR.0000000000001309 |
| AHA ACC | virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf | 2023 AHA/ACC/ACCP/ASPC/NLA/PCNA Guideline for the Management of Patients With Chronic Coronary Disease | chronic coronary disease | ? | 2023 | 111 | guideline | 10.1161/CIR.0000000000001168 |
| CDC | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf | CDC Clinical Practice Guideline for Prescribing Opioids for Pain - United States, 2022 | opioid prescribing for pain | adult | 2022 | 43 | guideline | ? |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | Summary Guide for Asthma Management and Prevention: For Adults, Adolescents and Children 6-11 Years | asthma | pediatric, adolescent, adult | 2026 | 47 | guideline | ? |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | Global Strategy for the Diagnosis, Management, and Prevention of Chronic Obstructive Pulmonary Disease: 2026 Report | chronic obstructive pulmonary disease | ? | 2026 | 248 | guideline | ? |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | AASLD IDSA Practice Guideline on treatment of chronic hepatitis B | chronic hepatitis B | ? | 2026 | 24 | guideline | 10.1097/HEP.0000000000001549 |
| IDSA | ajrccm_200_7_e45.pdf | Diagnosis and Treatment of Adults with Community-acquired Pneumonia: An Official Clinical Practice Guideline of the American Thoracic Society and Infectious Diseases Society of America | community-acquired pneumonia | adult | 2019 | 23 | guideline | 10.1164/rccm.201908-1581ST |
| IDSA | amr-guidance-update.pdf | Infectious Diseases Society of America 2026 Guidance on the Treatment of Antimicrobial-Resistant Gram-Negative Infections | antimicrobial-resistant gram-negative infection | pediatric, adult | 2026 | 140 | guideline | www.idsociety.org/practice-guideline/amr-guidance/ |
| IDSA | ciaa1215.pdf | Clinical Practice Guidelines by the Infectious Diseases Society of America, American Academy of Neurology, and American College of Rheumatology: Guidelines for the Prevention, Diagnosis and Treatment of Lyme Disease | Lyme disease | pediatric, adult | 2021 | 48 | guideline | 10.1093/cid/ciaa1215 |
| IDSA | ciaa241.pdf | Treatment of Nontuberculous Mycobacterial Pulmonary Disease: An Official ATS/ERS/ESCMID/IDSA Clinical Practice Guideline | nontuberculous mycobacterial pulmonary disease | adult | 2020 | 36 | guideline | 10.1093/cid/ciaa241 |
| IDSA | ciab275.pdf | Errata | hepatitis C treatment trial, babesiosis treatment tables (corrections) | ? | 2021 | 2 | errata | Clinical Infectious Diseases. 2021;73(1):172–4. |
| IDSA | ciab549.pdf | Clinical Practice Guideline by the Infectious Diseases Society of America (IDSA) and Society for Healthcare Epidemiology of America (SHEA): 2021 Focused Update Guidelines on Management of Clostridioides difficile Infection in Adults | Clostridioides difficile infection | adult | 2021 | 16 | guideline | 10.1093/cid/ciab549 |
| IDSA | ciab953.pdf | Infectious Diseases Society of America Guidelines on Infection Prevention for Healthcare Personnel Caring for Patients With Suspected or Known COVID-19 | COVID-19 infection prevention for healthcare personnel | general | 2021 | 20 | guideline | 10.1093/cid/ciab953 |
| IDSA | ciac724.pdf | Infectious Diseases Society of America Guidelines on the Treatment and Management of Patients With COVID-19 (September 2022) | COVID-19 treatment | adult | 2022 | 100 | guideline | 10.1093/cid/ciac724 |
| IDSA | ciad319.pdf | Hepatitis C Guidance 2023 Update: American Association for the Study of Liver Diseases-Infectious Diseases Society of America Recommendations for Testing, Managing, and Treating Hepatitis C Virus Infection | hepatitis C virus infection | pediatric, adult | 2023 | 18 | guideline | 10.1093/cid/ciad319 |
| IDSA | ciad527.pdf | IWGDF/IDSA Guidelines on the Diagnosis and Treatment of Diabetes-related Foot Infections (IWGDF/IDSA 2023) | diabetes-related foot infection | ? | 2023 | 23 | guideline | 10.1093/cid/ciad527 |
| IDSA | ciae104.pdf | Guide to Utilization of the Microbiology Laboratory for Diagnosis of Infectious Diseases: 2024 Update by the Infectious Diseases Society of America (IDSA) and the American Society for Microbiology (ASM) | microbiology laboratory utilization for infectious disease diagnosis | pediatric, adult | 2024 | 123 | guideline | 10.1093/cid/ciae104 |
| IDSA | ciae121.pdf | Infectious Diseases Society of America Guidelines on the Diagnosis of Coronavirus Disease 2019: Serologic Testing | COVID-19 serologic testing | ? | 2024 | 28 | guideline | 10.1093/cid/ciae121 |
| IDSA | ciae479.pdf | Primary Care Guidance for Providers Who Care for Persons With Human Immunodeficiency Virus: 2024 Update by the HIV Medicine Association of the Infectious Diseases Society of America | HIV primary care | pediatric, adolescent, adult, pregnancy | 2024 | 57 | guideline | 10.1093/cid/ciae479 |
| IDSA | ciu296.pdf | Practice Guidelines for the Diagnosis and Management of Skin and Soft Tissue Infections: 2014 Update by the Infectious Diseases Society of America | skin and soft tissue infection | ? | 2014 | 43 | guideline | 10.1093/cid/ciu296 |
| IDSA | ciu617.pdf | Clinical Practice Guideline for the Management of Chronic Kidney Disease in Patients Infected With HIV: 2014 Update by the HIV Medicine Association of the Infectious Diseases Society of America | chronic kidney disease in HIV infection | pediatric, adult | 2014 | 43 | guideline | 10.1093/cid/ciu617 |
| IDSA | civ482.pdf | 2015 Infectious Diseases Society of America (IDSA) Clinical Practice Guidelines for the Diagnosis and Treatment of Native Vertebral Osteomyelitis in Adults | native vertebral osteomyelitis | adult | 2015 | 21 | guideline | 10.1093/cid/civ482 |
| IDSA | ciw118.pdf | Implementing an Antibiotic Stewardship Program: Guidelines by the Infectious Diseases Society of America and the Society for Healthcare Epidemiology of America | antibiotic stewardship program implementation | ? | 2016 | 27 | guideline | 10.1093/cid/ciw118 |
| IDSA | ciw353.pdf | Management of Adults With Hospital-acquired and Ventilator-associated Pneumonia: 2016 Clinical Practice Guidelines by the Infectious Diseases Society of America and the American Thoracic Society | hospital-acquired and ventilator-associated pneumonia | adult | 2016 | 51 | guideline | 10.1093/cid/ciw353 |
| IDSA | ciw360.pdf | 2016 Infectious Diseases Society of America (IDSA) Clinical Practice Guideline for the Treatment of Coccidioidomycosis | coccidioidomycosis | ? | 2016 | 35 | guideline | 10.1093/cid/ciw360 |
| IDSA | ciw376.pdf | Official American Thoracic Society/Centers for Disease Control and Prevention/Infectious Diseases Society of America Clinical Practice Guidelines: Treatment of Drug-Susceptible Tuberculosis | drug-susceptible tuberculosis treatment | pediatric, adult | 2016 | 49 | guideline | 10.1093/cid/ciw376 |
| IDSA | ciw670.pdf | Diagnosis and Treatment of Leishmaniasis: Clinical Practice Guidelines by the Infectious Diseases Society of America (IDSA) and the American Society of Tropical Medicine and Hygiene (ASTMH) | leishmaniasis | ? | 2016 | 63 | guideline | 10.1093/cid/ciw670 |
| IDSA | ciw694.pdf | Official American Thoracic Society/Infectious Diseases Society of America/Centers for Disease Control and Prevention Clinical Practice Guidelines: Diagnosis of Tuberculosis in Adults and Children | tuberculosis diagnosis | pediatric, adult | 2017 | 33 | guideline | 10.1093/cid/ciw694 |
| IDSA | ciw861.pdf | 2017 Infectious Diseases Society of America's Clinical Practice Guidelines for Healthcare-Associated Ventriculitis and Meningitis | healthcare-associated ventriculitis and meningitis | ? | 2017 | 32 | guideline | 10.1093/cid/ciw861 |
| IDSA | cix1084.pdf | Diagnosis and Treatment of Neurocysticercosis: 2017 Clinical Practice Guidelines by the Infectious Diseases Society of America (IDSA) and the American Society of Tropical Medicine and Hygiene (ASTMH) | neurocysticercosis | ? | 2018 | 27 | guideline | 10.1093/cid/cix1084 |
| IDSA | cix1085.pdf | Clinical Practice Guidelines for Clostridium difficile Infection in Adults and Children: 2017 Update by the Infectious Diseases Society of America (IDSA) and Society for Healthcare Epidemiology of America (SHEA) | Clostridium difficile infection | pediatric, adult | 2018 | 48 | guideline | 10.1093/cid/cix1085 |
| IDSA | cix636.pdf | 2017 HIVMA of IDSA Clinical Practice Guideline for the Management of Chronic Pain in Patients Living With HIV | chronic pain in HIV infection | ? | 2017 | 37 | guideline | 10.1093/cid/cix636 |
| IDSA | cix669.pdf | 2017 Infectious Diseases Society of America Clinical Practice Guidelines for the Diagnosis and Management of Infectious Diarrhea | infectious diarrhea | pediatric, adolescent, adult | 2017 | 36 | guideline | 10.1093/cid/cix669 |
| IDSA | ciy745.pdf | 2018 Infectious Diseases Society of America Clinical Practice Guideline for the Management of Outpatient Parenteral Antimicrobial Therapy | outpatient parenteral antimicrobial therapy | ? | 2019 | 35 | guideline | 10.1093/cid/ciy745 |
| IDSA | ciy866.pdf | Clinical Practice Guidelines by the Infectious Diseases Society of America: 2018 Update on Diagnosis, Treatment, Chemoprophylaxis, and Institutional Outbreak Management of Seasonal Influenza | seasonal influenza | pediatric, adult, pregnancy | 2019 | 47 | guideline | 10.1093/cid/ciy866 |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | 2025 Clinical Practice Guideline Update by the Infectious Diseases Society of America on Group A Streptococcal (GAS) Pharyngitis: Risk assessment using clinical scoring systems in children and adults | group A streptococcal pharyngitis | pediatric, adult | 2025 | 13 | guideline | ? |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | Guidance for the Knowledge and Skills required for Antimicrobial Stewardship Leaders: an update from the Society for Healthcare Epidemiology of America, Infectious Diseases Society of America, Pediatric Infectious Diseases Society, and the Society of Infectious Diseases Pharmacists | antimicrobial stewardship leadership | general | 2026 | 13 | guideline | 10.1017/ash.2026.10344 |
| IDSA | infection-prevention-and-control-of-candida-auris-in-pediatric-settings.pdf | Infection prevention and control of Candida auris in pediatric settings | Candida auris infection prevention and control | pediatric | 2026 | 13 | guideline | 10.1017/ash.2026.10419 |
| IDSA | maternal-immunizations.pdf | Maternal Immunizations: ACOG Committee Statement Number 26 | maternal immunization | pregnancy | 2026 | 6 | guideline | Obstet Gynecol. 2026;147:e123–e128. |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | Consensus Guidance for Beta-Lactam Antibiotic Dose Individualization in Acutely Ill Patients | beta-lactam antibiotic dosing | pediatric, adult | 2026 | 27 | guideline | 10.1002/phar.70181 |
| IDSA | piab027.pdf | Clinical Practice Guideline by the Pediatric Infectious Diseases Society and the Infectious Diseases Society of America: 2021 Guideline on Diagnosis and Management of Acute Hematogenous Osteomyelitis in Pediatrics | acute hematogenous osteomyelitis | pediatric | 2021 | 44 | guideline | 10.1093/jpids/piab027 |
| IDSA | piad089.pdf | Clinical Practice Guideline by the Pediatric Infectious Diseases Society and the Infectious Diseases Society of America: 2023 Guideline on Diagnosis and Management of Acute Bacterial Arthritis in Pediatrics | acute bacterial arthritis | pediatric | 2024 | 59 | guideline | 10.1093/jpids/piad089 |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | Society of Critical Care Medicine and the Infectious Diseases Society of America Guidelines for Evaluating New Fever in Adult Patients in the ICU | new fever in the intensive care unit | adult | 2023 | 17 | guideline | 10.1097/CCM.0000000000006022 |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | Surviving Sepsis Campaign International Guidelines for the Management of Sepsis and Septic Shock in Children 2026 | sepsis and septic shock | pediatric | 2026 | 56 | guideline | 10.1097/PCC.0000000000003927 |
| IDSA | surviving-sepsis-campaign-international-guidelines-for.pdf | Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2026 | sepsis and septic shock | adult | 2026 | 88 | guideline | 10.1097/CCM.0000000000007075 |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | Antimicrobial Prophylaxis for Adult Patients With Cancer-Related Immunosuppression: ASCO and IDSA Clinical Practice Guideline Update | antimicrobial prophylaxis in cancer-related immunosuppression | adult | 2018 | 5 | guideline | 10.1200/JOP.18.00366 |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | ? | kidney transplant recipient care | transplant | 2009 | 168 | guideline | 10.1111/j.1600-6143.2009.02834.x |
| KDIGO | KDIGO-2013-Lipids-Guideline.pdf | KDIGO Clinical Practice Guideline for Lipid Management in Chronic Kidney Disease | lipid management in chronic kidney disease | pediatric, adult | 2013 | 56 | guideline | 10.1038/kisup.2013.27 |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | KDIGO 2017 Clinical Practice Guideline Update for the Diagnosis, Evaluation, Prevention, and Treatment of Chronic Kidney Disease-Mineral and Bone Disorder (CKD-MBD) | chronic kidney disease-mineral and bone disorder | ? | 2017 | 60 | guideline | 10.1016/j.kisu.2017.04.001 |
| KDIGO | KDIGO-2017-Living-Kidney-Donors-Guideline.pdf | KDIGO Clinical Practice Guideline on the Evaluation and Care of Living Kidney Donors | living kidney donor evaluation and care | transplant | 2017 | 115 | guideline | 10.1097/TP.0000000000001769 |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | KDIGO Clinical Practice Guideline on the Evaluation and Management of Candidates for Kidney Transplantation | kidney transplantation candidate evaluation | transplant | 2020 | 106 | guideline | 10.1097/TP.0000000000003136 |
| KDIGO | KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf | KDIGO 2021 Clinical Practice Guideline for the Management of Blood Pressure in Chronic Kidney Disease | blood pressure in chronic kidney disease | ? | 2021 | 92 | guideline | 10.1016/j.kint.2020.11.003 |
| KDIGO | KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf | KDIGO 2021 Clinical Practice Guideline for the Management of Glomerular Diseases | glomerular disease | ? | 2021 | 281 | guideline | 10.1016/j.kint.2021.05.021 |
| KDIGO | KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf | KDIGO 2022 Clinical Practice Guideline for Diabetes Management in Chronic Kidney Disease | diabetes in chronic kidney disease | ? | 2022 | 128 | guideline | 10.1016/j.kint.2022.06.008 |
| KDIGO | KDIGO-2022-Hepatitis-C-in-CKD-Guideline.pdf | KDIGO 2022 Clinical Practice Guideline for the Prevention, Diagnosis, Evaluation, and Treatment of Hepatitis C in Chronic Kidney Disease | hepatitis C in chronic kidney disease | ? | 2022 | 78 | guideline | 10.1016/j.kint.2022.07.013 |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | KDIGO 2024 Clinical Practice Guideline for the Management of Antineutrophil Cytoplasmic Antibody (ANCA)-Associated Vasculitis | ANCA-associated vasculitis | ? | 2024 | 47 | guideline | 10.1016/j.kint.2023.10.008 |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease | chronic kidney disease | ? | 2024 | 199 | guideline | 10.1016/j.kint.2023.10.018 |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | KDIGO 2025 Clinical Practice Guideline for the Evaluation, Management, and Treatment of Autosomal Dominant Polycystic Kidney Disease (ADPKD) | autosomal dominant polycystic kidney disease | ? | 2025 | 240 | guideline | 10.1016/j.kint.2024.07.009 |
| KDIGO | KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children.pdf | KDIGO 2025 Clinical Practice Guideline for the Management of Nephrotic Syndrome in Children | nephrotic syndrome | pediatric | 2025 | 50 | guideline | 10.1016/j.kint.2024.11.007 |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | KDIGO 2025 Clinical Practice Guideline for the Management of Immunoglobulin A Nephropathy (IgAN) and Immunoglobulin A Vasculitis (IgAV) | IgA nephropathy and IgA vasculitis | pediatric, adult | 2025 | 71 | guideline | 10.1016/j.kint.2025.04.004 |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | KDIGO 2026 Clinical Practice Guideline for Acute Kidney Injury (AKI) and Acute Kidney Disease (AKD): Public Review Draft | acute kidney injury and acute kidney disease | pediatric, adult | 2026 | 499 | draft | ? |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | KDIGO 2026 Clinical Practice Guideline for the Management of Anemia in Chronic Kidney Disease (CKD) | anemia in chronic kidney disease | ? | 2026 | 99 | guideline | 10.1016/j.kint.2025.06.006 |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | KDIGO Clinical Practice Guideline for the Management of Heart Failure in Chronic Kidney Disease: Scope of Work | heart failure in chronic kidney disease | ? | ? | 9 | scope-of-work | ? |
| KDIGO | KDIGO_2024_Lupus_Nephritis_Guideline.pdf | KDIGO 2024 Clinical Practice Guideline for the Management of Lupus Nephritis | lupus nephritis | ? | 2024 | 70 | guideline | 10.1016/j.kint.2023.09.002 |
| USPSTF | abdom-aortic-aneurysm-screening-final-rs.pdf | Screening for Abdominal Aortic Aneurysm: US Preventive Services Task Force Recommendation Statement | abdominal aortic aneurysm screening | adult | 2019 | 8 | recommendation-statement | 10.1001/jama.2019.18928 |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | Behavioral Weight Loss Interventions to Prevent Obesity-Related Morbidity and Mortality in Adults: US Preventive Services Task Force Recommendation Statement | obesity, behavioral weight loss intervention | adult | 2018 | 9 | recommendation-statement | 10.1001/jama.2018.13022 |
| USPSTF | afib-screening-final-recommendation-statement.pdf | Screening for Atrial Fibrillation: US Preventive Services Task Force Recommendation Statement | atrial fibrillation screening | adult | 2022 | 8 | recommendation-statement | 10.1001/jama.2021.23732 |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | Screening for Anxiety Disorders in Adults: US Preventive Services Task Force Recommendation Statement | anxiety disorder screening | adult, pregnancy, postpartum | 2023 | 8 | recommendation-statement | 10.1001/jama.2023.9301 |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | Aspirin Use to Prevent Preeclampsia and Related Morbidity and Mortality: US Preventive Services Task Force Recommendation Statement | preeclampsia prevention, low-dose aspirin | pregnancy | 2021 | 6 | recommendation-statement | 10.1001/jama.2021.14781 |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | Aspirin Use to Prevent Cardiovascular Disease: US Preventive Services Task Force Recommendation Statement | cardiovascular disease prevention, aspirin | adult | 2022 | 8 | recommendation-statement | 10.1001/jama.2022.4983 |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | Screening for Asymptomatic Bacteriuria in Adults: US Preventive Services Task Force Recommendation Statement | asymptomatic bacteriuria screening | adult, pregnancy | 2019 | 7 | recommendation-statement | 10.1001/jama.2019.13069 |
| USPSTF | autismfinalrs.pdf | Screening for Autism Spectrum Disorder in Young Children: US Preventive Services Task Force Recommendation Statement | autism spectrum disorder screening | pediatric | 2016 | 6 | recommendation-statement | 10.1001/jama.2016.0018 |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | Screening for Bacterial Vaginosis in Pregnant Persons to Prevent Preterm Delivery: US Preventive Services Task Force Recommendation Statement | bacterial vaginosis screening, preterm delivery prevention | pregnancy | 2020 | 7 | recommendation-statement | 10.1001/jama.2020.2684 |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | Behavioral Counseling Interventions to Promote a Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults Without Cardiovascular Disease Risk Factors: US Preventive Services Task Force Recommendation Statement | cardiovascular disease prevention, diet and physical activity counseling | adult | 2022 | 8 | recommendation-statement | 10.1001/jama.2022.10951 |
| USPSTF | bladcanrs.pdf | Screening for Bladder Cancer: U.S. Preventive Services Task Force Recommendation Statement | bladder cancer screening | adult | 2011 | 7 | recommendation-statement | Ann Intern Med. 2011;155:246-251. |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | Risk Assessment, Genetic Counseling, and Genetic Testing for BRCA-Related Cancer: US Preventive Services Task Force Recommendation Statement | BRCA-related cancer risk assessment and genetic testing | adult | 2019 | 14 | recommendation-statement | 10.1001/jama.2019.10987 |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | Medication Use to Reduce Risk of Breast Cancer: US Preventive Services Task Force Recommendation Statement | breast cancer risk-reducing medication | adult | 2019 | 11 | recommendation-statement | 10.1001/jama.2019.11885 |
| USPSTF | breast-cancer-screening-final-rec.pdf | Screening for Breast Cancer: US Preventive Services Task Force Recommendation Statement | breast cancer screening | adult | 2024 | 13 | recommendation-statement | 10.1001/jama.2024.5534 |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | Primary Care Behavioral Counseling Interventions to Support Breastfeeding: US Preventive Services Task Force Recommendation Statement | breastfeeding support counseling | pregnancy, postpartum | 2025 | 7 | recommendation-statement | 10.1001/jama.2025.3650 |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | Screening for Asymptomatic Carotid Artery Stenosis: US Preventive Services Task Force Recommendation Statement | carotid artery stenosis screening | adult | 2021 | 6 | recommendation-statement | 10.1001/jama.2020.26988 |
| USPSTF | celiacscreening-recstatement.pdf | Screening for Celiac Disease: US Preventive Services Task Force Recommendation Statement | celiac disease screening | pediatric, adolescent, adult | 2017 | 6 | recommendation-statement | 10.1001/jama.2017.1462 |
| USPSTF | cervical-cancer-final-rec-statement.pdf | Screening for Cervical Cancer: US Preventive Services Task Force Recommendation Statement | cervical cancer screening | adult | 2018 | 13 | recommendation-statement | 10.1001/jama.2018.10897 |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | Primary Care Interventions to Prevent Child Maltreatment: US Preventive Services Task Force Recommendation Statement | child maltreatment prevention | pediatric, adolescent | 2024 | 8 | recommendation-statement | 10.1001/jama.2024.1869 |
| USPSTF | child-vision-recstatement.pdf | Vision Screening in Children Aged 6 Months to 5 Years: US Preventive Services Task Force Recommendation Statement | vision screening, amblyopia | pediatric | 2017 | 9 | recommendation-statement | 10.1001/jama.2017.11260 |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | Screening for Chlamydia and Gonorrhea: US Preventive Services Task Force Recommendation Statement | chlamydia and gonorrhea screening | adolescent, adult, pregnancy | 2021 | 8 | recommendation-statement | 10.1001/jama.2021.14081 |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | Screening for Cognitive Impairment in Older Adults: US Preventive Services Task Force Recommendation Statement | cognitive impairment screening | older adult | 2020 | 7 | recommendation-statement | 10.1001/jama.2020.0435 |
| USPSTF | colorectal-cancer-screening-final-recommendation-updated.pdf | Screening for Colorectal Cancer: US Preventive Services Task Force Recommendation Statement | colorectal cancer screening | adult | 2021 | 13 | recommendation-statement | 10.1001/jama.2021.6238 |
| USPSTF | copd-screening-final-recommendation.pdf | Screening for Chronic Obstructive Pulmonary Disease: US Preventive Services Task Force Reaffirmation Recommendation Statement | COPD screening | adult | 2022 | 6 | recommendation-statement | 10.1001/jama.2022.5692 |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | Risk Assessment for Cardiovascular Disease With Nontraditional Risk Factors: US Preventive Services Task Force Recommendation Statement | cardiovascular disease risk assessment, nontraditional risk factors | adult | 2018 | 9 | recommendation-statement | 10.1001/jama.2018.8359 |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | Screening for Cardiovascular Disease Risk With Electrocardiography: US Preventive Services Task Force Recommendation Statement | cardiovascular disease risk screening, electrocardiography | adult | 2018 | 7 | recommendation-statement | 10.1001/jama.2018.6848 |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | Screening and Interventions to Prevent Dental Caries in Children Younger Than 5 Years: US Preventive Services Task Force Recommendation Statement | dental caries prevention | pediatric | 2021 | 7 | recommendation-statement | 10.1001/jama.2021.20007 |
| USPSTF | depression-suicide-risk-adults-rs.pdf | Screening for Depression and Suicide Risk in Adults: US Preventive Services Task Force Recommendation Statement | depression and suicide risk screening | adult, pregnancy, postpartum | 2023 | 11 | recommendation-statement | 10.1001/jama.2023.9297 |
| USPSTF | diabetes-child-final-recommendation.pdf | Screening for Prediabetes and Type 2 Diabetes in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | prediabetes and type 2 diabetes screening | pediatric, adolescent | 2022 | 5 | recommendation-statement | 10.1001/jama.2022.14543 |
| USPSTF | eating-disorders-screening-adults-adolescents-final-recommendation.pdf | Screening for Eating Disorders in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | eating disorder screening | adolescent, adult | 2022 | 7 | recommendation-statement | 10.1001/jama.2022.1806 |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | Interventions to Prevent Falls in Community-Dwelling Older Adults: US Preventive Services Task Force Recommendation Statement | falls prevention | older adult | 2024 | 7 | recommendation-statement | 10.1001/jama.2024.8481 |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | Folic Acid Supplementation to Prevent Neural Tube Defects: US Preventive Services Task Force Reaffirmation Recommendation Statement | neural tube defect prevention, folic acid | pregnancy | 2023 | 6 | recommendation-statement | 10.1001/jama.2023.12876 |
| USPSTF | food-insecurity-screening-final-recommendation.pdf | Screening for Food Insecurity: US Preventive Services Task Force Recommendation Statement | food insecurity screening | pediatric, adolescent, adult | 2025 | 7 | recommendation-statement | 10.1001/jama.2025.0879 |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | Serologic Screening for Genital Herpes Infection: US Preventive Services Task Force Reaffirmation Recommendation Statement | genital herpes serologic screening | adolescent, adult, pregnancy | 2023 | 6 | recommendation-statement | 10.1001/jama.2023.0057 |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | Screening for Gestational Diabetes: US Preventive Services Task Force Recommendation Statement | gestational diabetes screening | pregnancy | 2021 | 8 | recommendation-statement | 10.1001/jama.2021.11922 |
| USPSTF | glaucoma-screening-final-recommendation.pdf | Screening for Primary Open-Angle Glaucoma: US Preventive Services Task Force Recommendation Statement | primary open-angle glaucoma screening | adult | 2022 | 6 | recommendation-statement | 10.1001/jama.2022.7013 |
| USPSTF | GON-final-recommendation.pdf | Ocular Prophylaxis for Gonococcal Ophthalmia Neonatorum: US Preventive Services Task Force Reaffirmation Recommendation Statement | gonococcal ophthalmia neonatorum prophylaxis | newborn | 2019 | 5 | recommendation-statement | 10.1001/jama.2018.21367 |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | Behavioral Counseling Interventions to Promote a Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults With Cardiovascular Risk Factors: US Preventive Services Task Force Recommendation Statement | cardiovascular disease prevention, diet and physical activity counseling | adult | 2020 | 7 | recommendation-statement | 10.1001/jama.2020.21749 |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | Behavioral Counseling Interventions for Healthy Weight and Weight Gain in Pregnancy: US Preventive Services Task Force Recommendation Statement | gestational weight gain counseling | pregnancy | 2021 | 7 | recommendation-statement | 10.1001/jama.2021.6949 |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | Screening for Hearing Loss in Older Adults: US Preventive Services Task Force Recommendation Statement | hearing loss screening | older adult | 2021 | 6 | recommendation-statement | 10.1001/jama.2021.2566 |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | Screening for Hepatitis B Virus Infection in Pregnant Women: US Preventive Services Task Force Reaffirmation Recommendation Statement | hepatitis B screening | pregnancy | 2019 | 6 | recommendation-statement | 10.1001/jama.2019.9365 |
| USPSTF | hepatitis-b-screening-adults-adolescents-final-rec-statement.pdf | Screening for Hepatitis B Virus Infection in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | hepatitis B screening | adolescent, adult | 2020 | 8 | recommendation-statement | 10.1001/jama.2020.22980 |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | Screening for Hepatitis C Virus Infection in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | hepatitis C screening | adult | 2020 | 6 | recommendation-statement | 10.1001/jama.2020.1123 |
| USPSTF | high-blood-pressure-children-screening-final-rec-statement.pdf | Screening for High Blood Pressure in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | high blood pressure screening | pediatric, adolescent | 2020 | 6 | recommendation-statement | 10.1001/jama.2020.20122 |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | Interventions for High Body Mass Index in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | high body mass index intervention | pediatric, adolescent | 2024 | 7 | recommendation-statement | 10.1001/jama.2024.11146 |
| USPSTF | hiv-prep-prevention-final-recommendation.pdf | Preexposure Prophylaxis to Prevent Acquisition of HIV: US Preventive Services Task Force Recommendation Statement | HIV preexposure prophylaxis | adolescent, adult | 2023 | 10 | recommendation-statement | 10.1001/jama.2023.14461 |
| USPSTF | hiv-screening-final-rec-statement.pdf | Screening for HIV Infection: US Preventive Services Task Force Recommendation Statement | HIV screening | adolescent, adult, pregnancy | 2019 | 11 | recommendation-statement | 10.1001/jama.2019.6587 |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | Hormone Therapy for the Primary Prevention of Chronic Conditions in Postmenopausal Persons: US Preventive Services Task Force Recommendation Statement | postmenopausal hormone therapy for chronic disease prevention | adult | 2022 | 7 | recommendation-statement | 10.1001/jama.2022.18625 |
| USPSTF | hypertension-screening-adults-final-rec-statement.pdf | Screening for Hypertension in Adults: US Preventive Services Task Force Reaffirmation Recommendation Statement | hypertension screening | adult | 2021 | 7 | recommendation-statement | 10.1001/jama.2021.4987 |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | Screening for Hypertensive Disorders of Pregnancy: US Preventive Services Task Force Final Recommendation Statement | hypertensive disorders of pregnancy screening | pregnancy | 2023 | 9 | recommendation-statement | 10.1001/jama.2023.16991 |
| USPSTF | idachildrenfinal.pdf | Screening for Iron Deficiency Anemia in Young Children: USPSTF Recommendation Statement | iron deficiency anemia screening | pediatric | 2015 | 7 | recommendation-statement | 10.1542/peds.2015-2567 |
| USPSTF | illicit-drug-use-children-final-rec.pdf | Primary Care-Based Interventions to Prevent Illicit Drug Use in Children, Adolescents, and Young Adults: US Preventive Services Task Force Recommendation Statement | illicit drug use prevention | pediatric, adolescent, adult, pregnancy | 2020 | 7 | recommendation-statement | 10.1001/jama.2020.6774 |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | Screening for Impaired Visual Acuity in Older Adults: US Preventive Services Task Force Recommendation Statement | impaired visual acuity screening | older adult | 2022 | 6 | recommendation-statement | 10.1001/jama.2022.7015 |
| USPSTF | ipv-screening-final-rec-statement.pdf | Screening for Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults: US Preventive Services Task Force Recommendation Statement | intimate partner violence and elder abuse screening | adolescent, adult, older adult, pregnancy, postpartum | 2025 | 10 | recommendation-statement | 10.1001/jama.2025.9009 |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | Screening and Supplementation for Iron Deficiency and Iron Deficiency Anemia During Pregnancy: US Preventive Services Task Force Recommendation Statement | iron deficiency anemia screening and supplementation | pregnancy | 2024 | 8 | recommendation-statement | 10.1001/jama.2024.15196 |
| USPSTF | latent-tuberulosis-screening-final-rec-statement.pdf | Screening for Latent Tuberculosis Infection in Adults: US Preventive Services Task Force Recommendation Statement | latent tuberculosis infection screening | adult | 2023 | 8 | recommendation-statement | 10.1001/jama.2023.4899 |
| USPSTF | lipid-screening-children-adolescents-final-rec.pdf | Screening for Lipid Disorders in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | lipid disorder screening | pediatric, adolescent | 2023 | 8 | recommendation-statement | 10.1001/jama.2023.11330 |
| USPSTF | lung-cancer-screening-final-recommendation.pdf | Screening for Lung Cancer: US Preventive Services Task Force Recommendation Statement | lung cancer screening | adult | 2021 | 9 | recommendation-statement | 10.1001/jama.2021.1117 |
| USPSTF | multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf | Vitamin, Mineral, and Multivitamin Supplementation to Prevent Cardiovascular Disease and Cancer: US Preventive Services Task Force Recommendation Statement | vitamin and mineral supplementation for cardiovascular disease and cancer prevention | adult | 2022 | 8 | recommendation-statement | 10.1001/jama.2022.8970 |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | Screening and Preventive Interventions for Oral Health in Adults: US Preventive Services Task Force Recommendation Statement | oral health screening and prevention | adult | 2023 | 7 | recommendation-statement | 10.1001/jama.2023.21409 |
| USPSTF | oral-health-children-final-recommendation.pdf | Screening and Preventive Interventions for Oral Health in Children and Adolescents Aged 5 to 17 Years: US Preventive Services Task Force Recommendation Statement | oral health screening and prevention | pediatric, adolescent | 2023 | 8 | recommendation-statement | 10.1001/jama.2023.21408 |
| USPSTF | oralcancerfinalrs.pdf | Screening for Oral Cancer: U.S. Preventive Services Task Force Recommendation Statement | oral cancer screening | adult | 2014 | 8 | recommendation-statement | Ann Intern Med. 2014;160:55-60. |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | Screening for Osteoporosis to Prevent Fractures: US Preventive Services Task Force Recommendation Statement | osteoporosis screening, fracture prevention | adult | 2025 | 11 | recommendation-statement | 10.1001/jama.2024.27154 |
| USPSTF | ovarian-cancer-final-rec-statement.pdf | Screening for Ovarian Cancer: US Preventive Services Task Force Recommendation Statement | ovarian cancer screening | adult | 2018 | 7 | recommendation-statement | 10.1001/jama.2017.21926 |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | Screening for Peripheral Artery Disease and Cardiovascular Disease Risk Assessment With the Ankle-Brachial Index: US Preventive Services Task Force Recommendation Statement | peripheral artery disease screening, ankle-brachial index | adult | 2018 | 7 | recommendation-statement | 10.1001/jama.2018.8357 |
| USPSTF | pancreatic-cancer-final-rec-statement.pdf | Screening for Pancreatic Cancer: US Preventive Services Task Force Reaffirmation Recommendation Statement | pancreatic cancer screening | adult | 2019 | 7 | recommendation-statement | 10.1001/jama.2019.10232 |
| USPSTF | perinatal-depression-final-rec-statement.pdf | Interventions to Prevent Perinatal Depression: US Preventive Services Task Force Recommendation Statement | perinatal depression prevention | pregnancy, postpartum | 2019 | 8 | recommendation-statement | 10.1001/jama.2019.0007 |
| USPSTF | prediabetes-type2-diabetes-adult-final-recommendation.pdf | Screening for Prediabetes and Type 2 Diabetes: US Preventive Services Task Force Recommendation Statement | prediabetes and type 2 diabetes screening | adult | 2021 | 8 | recommendation-statement | 10.1001/jama.2021.12531 |
| USPSTF | prostate-cancer-final-rec-statement-051418.pdf | Screening for Prostate Cancer: US Preventive Services Task Force Recommendation Statement | prostate cancer screening | adult | 2018 | 13 | recommendation-statement | 10.1001/jama.2018.3710 |
| USPSTF | rhrs.pdf | ? | Rh(D) incompatibility screening | pregnancy | ? | 3 | recommendation-statement | AHRQ Pub. No. 05-0566-A. |
| USPSTF | scoliosis-final-rec-statement.pdf | Screening for Adolescent Idiopathic Scoliosis: US Preventive Services Task Force Recommendation Statement | adolescent idiopathic scoliosis screening | pediatric, adolescent | 2018 | 8 | recommendation-statement | 10.1001/jama.2017.19342 |
| USPSTF | Screening for Thyroid Cancer US Preventive Services Task Force Recommendation Statement Cancer Screening, Prevention, Control JAMA JAMA Network.pdf | Screening for Thyroid Cancer: US Preventive Services Task Force Recommendation Statement | thyroid cancer screening | adult | 2017 | 14 | recommendation-statement | 10.1001/jama.2017.4011 |
| USPSTF | Screening for Thyroid Dysfunction Final RS_Print_5.5.15.pdf | Screening for Thyroid Dysfunction: U.S. Preventive Services Task Force Recommendation Statement | thyroid dysfunction screening | adult | 2015 | 11 | recommendation-statement | 10.7326/M15-0483 |
| USPSTF | screening-anxiety-children-final-recommendation.pdf | Screening for Anxiety in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | anxiety screening | pediatric, adolescent | 2022 | 7 | recommendation-statement | 10.1001/jama.2022.16936 |
| USPSTF | screening-depression-suicide-risk-children-final-recommendation.pdf | Screening for Depression and Suicide Risk in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | depression and suicide risk screening | pediatric, adolescent | 2022 | 9 | recommendation-statement | 10.1001/jama.2022.16946 |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | Behavioral Counseling to Prevent Skin Cancer: US Preventive Services Task Force Recommendation Statement | skin cancer prevention counseling | pediatric, adolescent, adult | 2018 | 9 | recommendation-statement | 10.1001/jama.2018.1623 |
| USPSTF | skin-cancer-screening-final-recommendation.pdf | Screening for Skin Cancer: US Preventive Services Task Force Recommendation Statement | skin cancer screening | adolescent, adult | 2023 | 6 | recommendation-statement | 10.1001/jama.2023.4342 |
| USPSTF | sleep-apnea-screening-final-rec-statement.pdf | Screening for Obstructive Sleep Apnea in Adults: US Preventive Services Task Force Recommendation Statement | obstructive sleep apnea screening | adult | 2022 | 6 | recommendation-statement | 10.1001/jama.2022.20304 |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | Screening for Speech and Language Delay and Disorders in Children: US Preventive Services Task Force Recommendation Statement | speech and language delay screening | pediatric | 2024 | 6 | recommendation-statement | 10.1001/jama.2023.26952 |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: US Preventive Services Task Force Recommendation Statement | cardiovascular disease prevention, statins | adult | 2022 | 8 | recommendation-statement | 10.1001/jama.2022.13044 |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | Behavioral Counseling Interventions to Prevent Sexually Transmitted Infections: US Preventive Services Task Force Recommendation Statement | sexually transmitted infection prevention counseling | adolescent, adult | 2020 | 8 | recommendation-statement | 10.1001/jama.2020.13095 |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | Screening for Syphilis Infection in Nonpregnant Adolescents and Adults: US Preventive Services Task Force Reaffirmation Recommendation Statement | syphilis screening | adolescent, adult | 2022 | 7 | recommendation-statement | 10.1001/jama.2022.15322 |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | Screening for Syphilis Infection During Pregnancy: US Preventive Services Task Force Reaffirmation Recommendation Statement | syphilis screening | pregnancy | 2025 | 7 | recommendation-statement | 10.1001/jama.2025.5009 |
| USPSTF | testicuprs.pdf | Screening for Testicular Cancer: U.S. Preventive Services Task Force Reaffirmation Recommendation Statement | testicular cancer screening | adolescent, adult | 2011 | 5 | recommendation-statement | Ann Intern Med. 2011;154:483-486. |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | Interventions for Tobacco Smoking Cessation in Adults, Including Pregnant Persons: US Preventive Services Task Force Recommendation Statement | tobacco smoking cessation | adult, pregnancy | 2021 | 15 | recommendation-statement | 10.1001/jama.2020.25019 |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | Primary Care Interventions for Prevention and Cessation of Tobacco Use in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | tobacco use prevention and cessation | pediatric, adolescent | 2020 | 9 | recommendation-statement | 10.1001/jama.2020.4679 |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | Screening and Behavioral Counseling Interventions to Reduce Unhealthy Alcohol Use in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | unhealthy alcohol use screening and counseling | adolescent, adult, pregnancy | 2018 | 11 | recommendation-statement | 10.1001/jama.2018.16789 |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | Screening for Unhealthy Drug Use: US Preventive Services Task Force Recommendation Statement | unhealthy drug use screening | adolescent, adult, pregnancy, postpartum | 2020 | 9 | recommendation-statement | 10.1001/jama.2020.8020 |
| USPSTF | vitamin-d-deficiency-screening-final-recommendation.pdf | Screening for Vitamin D Deficiency in Adults: US Preventive Services Task Force Recommendation Statement | vitamin D deficiency screening | adult | 2021 | 7 | recommendation-statement | 10.1001/jama.2021.3069 |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | Vitamin D, Calcium, or Combined Supplementation for the Primary Prevention of Fractures in Community-Dwelling Adults: US Preventive Services Task Force Recommendation Statement | fracture prevention, vitamin D and calcium supplementation | adult | 2018 | 8 | recommendation-statement | 10.1001/jama.2018.3185 |

## Unsettled cells

Every `?` in the table above, and why it is one. A blank that nobody accounts for
reads as an answer, so this list is checked against the table rather than
maintained beside it — `tools/guidelines_catalog.py` fails if the two disagree.

- `Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf` — `year` — a web capture of a schedule page; the schedule shown is the one in force after a court stay, and carries no edition year
- `Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf` — `year` — a web capture of a schedule page; the schedule shown is the one in force after a court stay, and carries no edition year
- `Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf` — `year` — a web capture of a schedule page; the schedule shown is the one in force after a court stay, and carries no edition year
- `standards-of-care-2026.pdf` — `population` — the front matter states no population
- `gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf` — `population` — the front matter states no population
- `heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf` — `population` — the front matter states no population
- `isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf` — `population` — the front matter states no population
- `joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf` — `population` — the front matter states no population
- `kleindorfer-et-al-2021-2021-guideline-for-the-prevention-of-stroke-in-patients-with-stroke-and-transient-ischemic.pdf` — `population` — the front matter states no population
- `kusumoto-et-al-2018-2018-acc-aha-hrs-guideline-on-the-evaluation-and-management-of-patients-with-bradycardia-and.pdf` — `population` — the front matter states no population
- `ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf` — `population` — the front matter states no population
- `ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf` — `population` — the front matter states no population
- `otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf` — `population` — the front matter states no population
- `rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf` — `population` — the front matter states no population
- `virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf` — `population` — the front matter states no population
- `GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf` — `population` — the front matter states no population
- `aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf` — `population` — the front matter states no population
- `ciab275.pdf` — `population` — an errata document, correcting two unrelated articles
- `ciad527.pdf` — `population` — the front matter states no population
- `ciae121.pdf` — `population` — the front matter states no population
- `ciu296.pdf` — `population` — the front matter states no population
- `ciw118.pdf` — `population` — the front matter states no population
- `ciw360.pdf` — `population` — the front matter states no population
- `ciw670.pdf` — `population` — the front matter states no population
- `ciw861.pdf` — `population` — the front matter states no population
- `cix1084.pdf` — `population` — the front matter states no population
- `cix636.pdf` — `population` — the front matter states no population
- `ciy745.pdf` — `population` — the front matter states no population
- `KDIGO-2009-Transplant-Recipient-Guideline-English.pdf` — `title` — the cover is a supplement masthead and the title is not in the extractable text
- `KDIGO-2017-CKD-MBD-Guideline.pdf` — `population` — the front matter states no population
- `KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf` — `population` — the front matter states no population
- `KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf` — `population` — the front matter states no population
- `KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf` — `population` — the front matter states no population
- `KDIGO-2022-Hepatitis-C-in-CKD-Guideline.pdf` — `population` — the front matter states no population
- `KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf` — `population` — the front matter states no population
- `KDIGO-2024-CKD-Guideline.pdf` — `population` — the front matter states no population
- `KDIGO-2025-ADPKD-Guideline.pdf` — `population` — the front matter states no population
- `KDIGO-2026-Anemia-in-CKD-Guideline.pdf` — `population` — the front matter states no population
- `KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf` — `population` — the front matter states no population
- `KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf` — `year` — the document carries no date of its own
- `KDIGO_2024_Lupus_Nephritis_Guideline.pdf` — `population` — the front matter states no population
- `rhrs.pdf` — `title` — the title page is headed only *Summary of Recommendations*
- `rhrs.pdf` — `year` — no date appears anywhere in its three pages
- `standards-of-care-2026.pdf` — `citation` — the compilation prints a DOI for its introduction, not for the compilation
- `CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf` — `citation` — the document prints a citation for the 2016 edition it replaces, not for itself
- `GINA-Summary-Guide-2026-WEB-WMS.pdf` — `citation` — the document prints no citation for itself; its society masthead is not one
- `GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf` — `citation` — the document prints reference-list DOIs but no citation for itself
- `gas-pharyngitis-pico-a-b-guideline.pdf` — `citation` — the manuscript prints cited-reference locators but no citation for itself
- `KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf` — `citation` — the draft prints reference-list DOIs but no citation for itself
- `KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf` — `citation` — the scope of work prints no citation for itself
