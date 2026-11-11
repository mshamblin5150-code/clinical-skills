# E/M point systems

**This sheet never selects a professional E/M level.** `icd10-cpt` step 5
selects the clinician's ED and office levels from the passing `reference/cpt-em-mdm-<edition>.md` sheet whose
edition covers the service date, or from the rendered CPT book where step 5
sends it. "E/M point system" names two different things. One is the 1995/1997
professional audit score sheet: this sheet explains why it does not select a
professional level and where its habits miscount under the CPT table. The other
is a hospital's ED facility-level sheet, which scores nursing and facility
resources for the hospital's own claim; see *ED facility-level point sheets*
below. It cites the CPT sheet's entries by name; where a
summary below and an entry differ, the entry governs.

## What a point sheet is

The CMS 1995 and 1997 *Documentation Guidelines for Evaluation and Management
Services* recognize four types of medical decision making: straightforward,
low complexity, moderate complexity and high complexity. Each type is graded on
three elements, and two of the three must be met or exceeded (1997 guidelines,
printed p. 43; 1995 guidelines, printed p. 11). In short form, the element
labels are:

| Type of decision making | Number of diagnoses or management options | Amount and/or complexity of data to be reviewed | Risk of complications and/or morbidity or mortality |
| --- | --- | --- | --- |
| Straightforward | Minimal | Minimal or none | Minimal |
| Low complexity | Limited | Limited | Low |
| Moderate complexity | Multiple | Moderate | Moderate |
| High complexity | Extensive | Extensive | High |

**The guidelines assign no points.** Their MDM sections (1997, printed
pp. 43–47; 1995, printed pp. 11–15) describe each element in prose. The 1997
Table of Risk gives "common clinical examples rather than absolute measures of
risk" in three categories (presenting problems, diagnostic procedures ordered,
management options selected), and the highest level in any one category
determines the overall risk (printed p. 46). Neither document carries a numeric
score.

Secondary sources attribute the point values on circulated audit worksheets
(points per problem type, per data item, and point thresholds per element) to
an audit tool developed by Marshfield Clinic staff and a Medicare carrier. They
also report that contractors such as Novitas describe their own score sheets as
aids only. No primary copy of either was read.

**This sheet records no point values, on purpose.** No primary copy of a point
worksheet could be opened in this research: the Novitas score-sheet pages
returned no readable worksheet, and ACEP's FAQ refused the request. Every value
found was a search-engine summary of a private or secondary copy, and some
values were not stated by any source found. A guessed point value is worse
than a blank one.

## Why it does not select a level here

CMS's MLN006764 booklet, May 2026 edition (PDF page 24), says that as of
January 1, 2023, for most E/M visit families, the level is chosen by the level
of MDM or by time. It says that for some visits, like ED visits, only MDM or
only time is used, and that the CPT E/M guidelines for MDM apply. It says
history and exam must meet the code descriptors but do not affect level
selection. In this repository, `icd10-cpt` step 5 selects ED levels by MDM
alone.

So a point sheet built on the 1995 or 1997 table does not select an ED or
office level here, and history and exam bullet counts select no level.

## Where point-sheet habits miscount

Each row names the CPT sheet entries that decide the question. The right-hand
column summarizes them; read the entries.

| Point-sheet habit | Governing CPT sheet entries | Under the CPT table |
| --- | --- | --- |
| Score the number of possible diagnoses considered. | `definition-problem-addressed`, `problem-counting-guidance`, `definition-undiagnosed-new` | Count problems addressed, by type. The number of diagnoses in a differential is not itself a count, but a member of the differential can make the presenting problem an undiagnosed new problem with uncertain prognosis. Under ADR 0308, `icd10-cpt` step 5 adds that the note pass's own differential cannot supply the clinician's decision. |
| Score a test category once: "lab", "radiology", "medicine section". | `definition-data-test`, `definition-data-unique` | Count each unique test. A panel is one test, and tests with overlapping elements are not unique. Multiple results of one test compared in the same E/M service count as one unique test. |
| Credit a *decision* to obtain old records or outside history. | `table-low`, `table-moderate`, `definition-external`, `definition-data-unique`, `definition-independent-historian` | The grid credits review of external notes and assessment requiring an independent historian; it lists no credit for a decision to obtain them. Review of all materials from one unique source counts once. An independent historian counts where the patient cannot give a complete or reliable history, where a confirmatory history is necessary, or where conflict or poor communication between historians requires more than one. Translation services do not count. |
| Credit discussing a result with the physician who performed the test. | `table-moderate`, `definition-discussion`, `definition-appropriate-source`, `definition-external-clinician` | This still counts in Category 3 when the exchange meets the CPT terms: an interactive, direct discussion of management or test interpretation with an external clinician or appropriate source, not separately reported. An exchange through intermediaries such as clinical staff or trainees does not count, and sending chart notes or written exchanges within progress notes is not an interactive exchange. Family and informal caregivers are not an appropriate source. |
| Credit personally viewing an image, tracing or specimen. | `definition-independent-interpretation`, `definition-data-analyzed` | Category 2 applies to a test that has a CPT code and for which an interpretation or report is customary. It applies only when the E/M clinician is not reporting and has not previously reported that test, and a form of interpretation is documented. |
| Grade risk by a single highest category in a Table of Risk. | `mdm-selection`, `condition-management-risk`, `definition-risk`, `table-straightforward`, `table-low`, `table-moderate`, `table-high` | The element is the risk of complications and/or morbidity or mortality of patient management. Its level rests on the consequences of the problems addressed when appropriately treated, and includes decisions to initiate or forgo further testing, treatment or hospitalization. Condition risk is distinct from management risk. The grid's examples are examples, not a table where the highest single column wins. |
| Count history and exam bullets. | none; MLN006764 | History and exam must meet the code descriptors but do not select the level. |

## Questions secondary sources disagree on, settled by the CPT text

The research found secondary commentary disagreeing on three counting
questions. The committed CPT 2026 text answers each one:

- **When an ordered test counts.** `definition-data-analyzed`: tests ordered
  are presumed to be analyzed when the results are reported, so a test ordered
  during an encounter is counted in that encounter. A test ordered outside an
  encounter may be counted in the encounter where it is analyzed, and each new
  result of a recurring order may be counted in the encounter where it is
  analyzed.
- **Whether ordering plus independent interpretation is one credit or two.**
  `definition-independent-interpretation`: a test that is ordered and
  independently interpreted may count both as a test ordered and as an
  interpretation. `icd10-cpt` step 5's ECG rule already applies this.
- **What a separately reported test loses.** `definition-data-analyzed`: a
  service whose professional component the E/M clinician reports separately is
  not counted as a data element ordered, reviewed, analyzed or independently
  interpreted.

Vendor articles found in search claim a 2026 revision of the MDM risk table and
cite no AMA or CMS source. The committed sheet transcribes the 2026 book, so it
describes the 2026 table.

## ED facility-level point sheets

A hospital reports its own ED visit level (99281–99285) on the facility claim,
separately from the clinician's professional level. For that facility level,
CMS has not adopted national guidelines. The CY 2008 OPPS final rule says
hospitals report clinic and ED visits by their own internal guidelines
(72 FR 66805–66807). These guidelines are typically a point sheet that scores
nursing interventions, monitoring, procedures assisted, medications given and
disposition, then maps the point total to a level band.

The rule lists 11 principles those guidelines should meet (72 FR 66805). They
include that the guidelines:

- reasonably relate the intensity of hospital resources to the different
  levels of effort the code represents;
- are based on hospital facility resources, not physician resources;
- are clear enough for accurate payment, compliance and audits;
- require only documentation that is clinically necessary for patient care;
- do not facilitate upcoding or gaming;
- are written or recorded, and provide the basis for selecting a specific code;
- are applied consistently across patients in the department;
- produce coding decisions that other hospital staff and outside sources can
  verify.

The same rule says hospitals may decide whether separately payable services
count as a proxy for hospital resource use (72 FR 66806). It says 99291 still
requires 30 minutes or more of critical care, and that with less, the hospital
reports the ED visit level its internal guidelines support (72 FR 66806–66807).
Later rules keep that position. The CY 2014 OPPS final rule collapsed
hospital clinic visits into the single code G0463 but did not finalize
discontinuing "five distinct visit levels for Type A ED visits"
(78 FR 75042). The CY 2016 rule declined national guidelines as "disruptive
and administratively burdensome" to hospitals with working internal guidelines
(80 FR 70449). The CY 2023 rule repeats that one national set is unlikely to fit
all ED visits (87 FR 71992). The CY 2026 and CY 2027 rules continue the current
clinic and ED visit policies (90 FR 53770; 91 FR 70561). The Medicare Claims
Processing Manual, chapter 4, section 160, tells hospitals to "continue to apply
their current internal guidelines to the existing CPT codes." Because Medicare
pays a hospital clinic visit as one code, a clinic point sheet does not change
the Medicare level; the ED keeps five levels.

**Separately payable services are where published practice divides.** CMS
first objected that counting them "could result in the double counting of
hospital resources" (72 FR 66800), then left the choice to hospitals as a
proxy for resource use not associated with those services (72 FR 66806).
Two consultant guides read for this sheet say a separately billable service
should not factor into the level (CorroHealth, December 2023 and January 2025).
A 2023 payer intervention grid credits parenteral medication once, at Level 4
(BCBS Texas CPCP003). An uncapped per-dose count of a service that is also
billed separately has no counterpart in any tool read.

**Payers now check facility levels by algorithm.** Two 2026 payer policies
read for this sheet re-level discharged ED claims from the diagnoses and the
services billed, not from the hospital's sheet: Kaiser Permanente Washington
uses Optum's EDC Analyzer, which it says derives from a hospital product used
by more than 1,500 hospitals, and Premera's program adjusts discharged 99284
and 99285 claims by one or two levels. Both exclude admitted patients. A
facility level that rests on items leaving no trace on the claim is the level
such a program is most likely to lower.

**Which ED services Medicare pays separately decides whether a point is a
proxy or a second payment.** In the October 2026 OPPS Addendum B, ED visits
99281–99285 and critical care 99291 carry status indicator J2; IV push and
infusion codes carry S; the IV start and pulse oximetry carry N (packaged);
clinical laboratory tests carry Q4, conditionally packaged when billed with a
J2 service; and the EKG tracing, nebulizer treatment, simple laceration repair
and Foley placement carry Q1. The CMS status-indicator definitions addendum defines Q1 as packaged when billed with a status S, T or V
service. The public I/OCE specification v17.1 (the 2016 release that
introduced J2) settles how an ED visit counts: when a claim does not qualify
for comprehensive observation, "the visit code(s) is/are assigned their
standard APC and SI," and its flowchart notes such claims "are processed as
visits under standard APC assignment (SI = V)." So on an ED claim without 8 or
more hours of observation the visit is status V, and those Q1 services are
packaged into it. Points for them, for the IV start, for pulse oximetry and for
labs therefore count resources Medicare pays only through the visit; points for
IV pushes and infusions, and for procedures such as a lumbar puncture,
cardioversion or intubation, count services Medicare also pays separately. The
current I/OCE release (v27.3) is distributed under an AHA license and was not
read, so this rests on the 2016 logic, whose C-APC 8011 criteria the CY 2026
rule restates unchanged (90 FR 53460). An ACEP
2023 facility-coding talk describes ED visits as status V, which matches the
processed status rather than the status published in Addendum B.
When the ED visit is followed by 8 or more hours of observation, the claim is
paid as one comprehensive payment (C-APC 8011) and the ED level does not change
the Medicare payment. These files are licensed from the AMA for internal use;
this sheet records status indicators only, no CPT descriptors.

**What this means for checking a facility sheet.** A facility level is
correct when it matches the hospital's own written sheet, applied to what the
nursing and ED record documents. It is not checked against the CPT MDM table,
and the professional level does not decide it. A human check re-tallies each
documented item at the sheet's value, applies the sheet's count limits (for
example, items marked "once"), and recomputes the total and band. It also
confirms the sheet's exclusions and order requirements and routes critical care
to its own rules.

**A site's sheet is account-owned and is not tracked here.** Each hospital's
items, point values and bands are its own. Like other practicum-site details,
they belong in the account's private material, not in this public repository.
The skills in this repository select the professional level only; none of them
selects a facility level.

## The tested sheets this repository carries

[ADR 0444](../docs/adr/0444-the-repository-carries-a-tested-ed-facility-grid-and-office-mdm-check-sheet.md)
adopted two sheets after testing them with independent coders on two synthetic
65-case panels drawn to the national visit mix:

- [ed-facility-grid.md](ed-facility-grid.md), a hospital facility-level grid
  built on the BCBS Texas CPCP003 items (each departure marked). A grid sets
  the level from the highest item documented, so it has no bands to tune; a
  point sheet in this test scored lower agreement and was not adopted.
- [office-mdm-check.md](office-mdm-check.md), the clinician's house rules and
  counting notes for an office level, citing the committed CPT entries by id.
  `icd10-cpt` step 5 applies it.

**What the research found on the questions the grid had to decide**
(each answer checked by a second reader, 2026-11-10):

- **Imaging.** No source says whether staff "preparation" for imaging must be
  charted separately. Payer algorithms (Kaiser Permanente Washington, Premera)
  read the diagnostic lines billed, and a CorroHealth example sheet scores
  "diagnostics ordered—imaging," so the grid takes an ordered-and-performed
  study as the evidence. CMS permits the proxy (72 FR 66806).
- **Moderate sedation.** The sedation codes 99151–99157 are packaged (status N)
  in the October 2026 Addendum B; BCBS Texas lists procedural sedation at
  Level 5 with no exclusion for a separately paid procedure.
- **Serial cardiac studies and temperature instability.** BCBS Texas names
  both at Level 5 and defines neither; no other source read does. The count
  and the thresholds are the grid's stated choices.
- **The office ECG.** CPT settles the global code (93000 counts nothing toward
  data); a tracing-only claim's interpretation credit is unsettled, which is
  [ADR 0443](../docs/adr/0443-an-office-ecg-the-clinician-reads-is-billed-with-its-interpretation-and-counts-nothing-toward-data.md).

## Sources

Read on 2026-11-10. CMS documents came from cms.gov and the OPPS rules from
govinfo.gov; the consultant guides and the payer policy came from their
publishers' sites. The 1995 and 1997 guidelines and the OPPS rules are federal
works; the consultant guides and the payer policy are not and are summarized,
not reproduced. MLN006764 is a CMS publication whose CPT content is copyrighted by the
American Medical Association; this sheet quotes none of that content.

| Document | URL | SHA-256 of the file read |
| --- | --- | --- |
| 1997 Documentation Guidelines for E/M Services | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnedwebguide/downloads/97docguidelines.pdf | `105e2b1e6e802a5020a4454ed5b9e4bfa356822bef0031682d72c7f1883d56ab` |
| 1995 Documentation Guidelines for E/M Services | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnedwebguide/downloads/95docguidelines.pdf | `186a217526c8b0fae16151ee69344c7073c80bdd78b612aa991a5911c604ff05` |
| MLN006764, Evaluation and Management Services, May 2026 | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnproducts/downloads/eval-mgmt-serv-guide-icn006764.pdf | `2b2f327d70a599cfedad8b30c7112e66073ca9c60b9a3823c4a4224392f45c82` |
| CY 2008 OPPS final rule, 72 FR 66580 (Nov. 27, 2007), ED and clinic visit guidelines at 66805–66807 | https://www.govinfo.gov/content/pkg/FR-2007-11-27/html/07-5507.htm | `716a1483c3eb1090cf48ae4b689a0241426817714c64387077b9f122d265c468` |
| CY 2014 OPPS final rule, FR Doc 2013-28737, 78 FR 75038–75042 | https://www.govinfo.gov/content/pkg/FR-2013-12-10/html/2013-28737.htm | `04886eab6bb98b18187ad6465c5835cc84b9730be8bfc426f0976fa1cfcd6125` |
| CY 2016 OPPS final rule, FR Doc 2015-27943, 80 FR 70448–70449 | govinfo.gov, FR Doc 2015-27943 | `8d9e33a2420824c5b3c70b9c62d246fdec670f2fdf37fc124084a9f75b033939` |
| CY 2023 OPPS final rule, FR Doc 2022-23918, 87 FR 71992 | govinfo.gov, FR Doc 2022-23918 | `59d837e6a363eede8e352e6e3b5bd90d3f703b8485509c4397cbc54d98c3c970` |
| CY 2026 OPPS final rule, FR Doc 2025-20907, 90 FR 53770 | govinfo.gov, FR Doc 2025-20907 | `d4d123d1c099b7be2ad64833f2d40242b0208eedb1d308dc7ec1f32f864f0973` |
| CY 2027 OPPS final rule, FR Doc 2026-22739, 91 FR 70561 | govinfo.gov, FR Doc 2026-22739 | `969f79354c72b08ea322bab3be911a5c7f6382460e861baa58da611dd5c4aeb0` |
| Medicare Claims Processing Manual, chapter 4, section 160 | https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/downloads/clm104c04.pdf | `579dcaf4e8fc851846556666a2c4c24f265ea634e924097bd9e60169f5802ba6` |
| CorroHealth, Emergency Department – Charge Process, December 2023 (private consultant) | https://apps.para-hcfs.com/pde/documents/Emergency%20Charge%20Process%20-June%202022%20Update%20edited.pdf | `237c689f0196b7a18c14c85085e7379c63ada98f9290293092098560ff0c996e` |
| CorroHealth, Facility Fee E/M Coding and Billing, January 2025 (private consultant) | https://apps.para-hcfs.com/pde/documents/Facility%20EM%20Visit%20Coding%20and%20Billing%202023.pdf | `1e5fd2822ecab9dc6d28105275323345ca3d11484de2db6dca5a50c507a75804` |
| BCBS Texas CPCP003, ED E/M Coding – Facility, effective 2023-10-25 (payer policy) | https://www.bcbstx.com/docs/provider/tx/standards/clinical-pay-coding/2023/cpcp003-ed-em-coding-facility-10252023.pdf | `47cbbab4060e02fded3ea26c17497ca15f90fc971d800264fd4e7d6f514a5e39` |
| Kaiser Permanente Washington, ED Facility E/M Coding Policy, revised 2024-01-09 (payer policy) | https://wa-provider.kaiserpermanente.org/static/pdf/provider/billing-claims/emergency-department.pdf | `230ddfffeadd72fdae40a04449b5ed392ccd0c386999aa036d16858d11204a6c` |
| Premera, ED Facility Coding Program provider guide, 2026-07-23 (payer guide) | https://www.premera.com/documents/071777.pdf | `5689dc41348baa4352de1b170202aa3f577c811f387d7c6311d11029687d344b` |
| ACEP, Facility Reimbursement for ED Services: Key 2023 Updates (Granovsky; copy supplied by the clinician) | https://www.acep.org/siteassets/sites/rc/media/presentations/coding/lightningrounds2023facility_granovsky.pdf | `f086c39ef3737a0c160c8e094636ec82f9059a6e5ac5d4d352028de293969fac` |
| CMS OPPS Addendum B, October 2026 (license-gated; read under the AMA end-user agreement) | https://www.cms.gov/files/zip/October-2026-OPPS-Addendum-B.zip | `2fc507a1fa6715eb2c702049a18912a33017003606550f61345ae1b48b00bf5b` |
| CMS CY 2026 OPPS final rule addenda, including the status-indicator definitions addendum (license-gated) | https://www.cms.gov/files/zip/2026-nfrm-opps-addenda.zip | `602a0d556468ce036f1d2f0bce8872ec8610c526504893ba0fa0fb414212cff0` |
| CMS Integrated OCE Specifications v17.1 (public) | https://www.cms.gov/files/document/integocespecsv171508-v2pdf | `bc6e1e50058b24981a36aab1c85c56bf188f491250bb81f9f5813d4d4fb1a10f` |
| Medicare Claims Processing Manual, chapter 4, section 10.4 (same file as above) | https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/downloads/clm104c04.pdf | `579dcaf4e8fc851846556666a2c4c24f265ea634e924097bd9e60169f5802ba6` |

**What rests on secondary or unopened sources:** the Marshfield provenance and
the Novitas "aids only" description; the existence and content of point
worksheets; the three disagreements in the section above, which the CPT text
settles regardless; and the vendor claims about a 2026 revision. Nothing in
this repository depends on any of them.
