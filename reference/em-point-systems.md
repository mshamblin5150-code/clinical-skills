# E/M point systems

**This sheet never selects an E/M level.** `icd10-cpt` step 5 selects ED and
office levels from the passing `reference/cpt-em-mdm-<edition>.md` sheet whose
edition covers the service date, or from the rendered CPT book where step 5
sends it. This sheet explains what an "E/M point system" or audit score sheet
is, why it does not select those levels, and where habits learned from one
miscount under the CPT table. It cites the CPT sheet's entries by name; where a
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

## Sources

Read on 2026-11-10 from cms.gov. The 1995 and 1997 guidelines are federal
works. MLN006764 is a CMS publication whose CPT content is copyrighted by the
American Medical Association; this sheet quotes none of that content.

| Document | URL | SHA-256 of the file read |
| --- | --- | --- |
| 1997 Documentation Guidelines for E/M Services | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnedwebguide/downloads/97docguidelines.pdf | `105e2b1e6e802a5020a4454ed5b9e4bfa356822bef0031682d72c7f1883d56ab` |
| 1995 Documentation Guidelines for E/M Services | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnedwebguide/downloads/95docguidelines.pdf | `186a217526c8b0fae16151ee69344c7073c80bdd78b612aa991a5911c604ff05` |
| MLN006764, Evaluation and Management Services, May 2026 | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnproducts/downloads/eval-mgmt-serv-guide-icn006764.pdf | `2b2f327d70a599cfedad8b30c7112e66073ca9c60b9a3823c4a4224392f45c82` |

**What rests on secondary or unopened sources:** the Marshfield provenance and
the Novitas "aids only" description; the existence and content of point
worksheets; the three disagreements in the section above, which the CPT text
settles regardless; and the vendor claims about a 2026 revision. Nothing in
this repository depends on any of them.
