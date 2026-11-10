# E/M point systems

**This sheet never selects an E/M level.** `icd10-cpt` step 5 selects ED and
office levels only from the passing `reference/cpt-em-mdm-<edition>.md` sheet.
This sheet explains what an "E/M point system" or audit score sheet is, why it
does not apply to those families, and where habits learned from one give a
wrong answer under the CPT table. It cites the CPT sheet's entries by name and
copies none of their text.

## What a point sheet is

The CMS 1995 and 1997 *Documentation Guidelines for Evaluation and Management
Services* define four types of medical decision making (MDM): straightforward,
low, moderate and high. Each type is graded on three elements, and two of the
three must be met or exceeded (1997 guidelines, printed p. 43). The element labels
in those guidelines are:

| Type of MDM | Diagnoses or management options | Data to be reviewed | Risk |
| --- | --- | --- | --- |
| Straightforward | Minimal | Minimal or none | Minimal |
| Low | Limited | Limited | Low |
| Moderate | Multiple | Moderate | Moderate |
| High | Extensive | Extensive | High |

**The guidelines assign no points.** Read in full on 2026-11-10, their MDM
section (1997, printed pp. 43–47) describes each element in prose. It also gives a
three-column Table of Risk (presenting problems, diagnostic procedures ordered,
management options selected) and says the highest level in any one column
determines the overall risk. It contains no numeric score.

The point values on circulated audit worksheets (points per problem type, per
data item, and point thresholds per element) come from an audit tool that
Marshfield Clinic staff and a Medicare carrier developed. Contractors such as
Novitas later published their own score sheets and described them as aids only.

**This sheet records no point values, on purpose.** No primary copy of any
point worksheet could be opened. The Novitas pages served only a script shell,
and ACEP's FAQ refused the request. Every value the research found was a search
summary of a private or secondary copy, and some values were not stated by any
source. A guessed point value is worse than a blank one.

## Why it does not apply here

CMS's MLN006764 booklet, May 2026 edition, says that as of January 1, 2023,
for most E/M visit families, the level is chosen by the level of MDM or by
time. It says some visits, such as ED visits, use only MDM or only time. It
says the CPT E/M guidelines for MDM apply, and that history and exam must meet
the code descriptors but do not affect level selection. Office and outpatient
visits 99202–99215 changed on January 1, 2021. ED visits 99281–99285 and the
other families changed on January 1, 2023.

So a point sheet built on the 1995 or 1997 table cannot select an ED or office
level for a service date after those changes. Using one would also
reintroduce the history and exam bullet counts that no longer select a level.

## Where point-sheet habits give a wrong answer

Each row names the CPT sheet entry that decides the question. Read the entry;
the right-hand column here is a summary, not the rule.

| Point-sheet habit | Governing CPT sheet entry | What changes |
| --- | --- | --- |
| Score the number of possible diagnoses considered, so a broad differential raises the element. | `definition-problem-addressed`, the problem grid entries | Count problems addressed, by type. A differential is not a count of problems addressed (ADR 0308). |
| Score a test category once: "lab", "radiology", "medicine section". | `definition-data-test`, `definition-data-unique` | Count each unique test. A panel is one test, and overlapping tests are not unique. Serial results of one test count once. |
| Credit a *decision* to obtain old records or outside history. | `table-low`, `definition-external`, `definition-data-unique`, `definition-independent-historian` | A decision earns nothing. Review of external notes counts once per unique source. An independent historian counts only when the patient cannot give a reliable history or confirmation is needed. A translator is not one. |
| Credit discussing a result with the physician who performed the test. | `definition-discussion`, `definition-appropriate-source`, `definition-external-clinician` | Category 3 requires an interactive, direct exchange about management or test interpretation with an external clinician or appropriate source. Family members do not qualify, and notes passed through staff do not count. |
| Credit personally viewing an image, tracing or specimen. | `definition-independent-interpretation`, `definition-data-analyzed` | Category 2 applies only to a test that has a CPT code and customarily gets a report, and only when the E/M clinician does not report that test. |
| Put the presenting problem's severity in the risk column, with the highest single column deciding. | `definition-risk`, the risk grid entries | Risk is the risk of the clinician's management decisions for the problems addressed, including decisions to start or forgo testing, treatment or hospitalization. Problem severity belongs to the problems element. |
| Count history and exam bullets. | none; MLN006764 | History and exam must meet the code descriptors but do not select the level. |

## Questions secondary sources disagree on, settled by the CPT text

The research found commentary that disagrees on three counting questions. The
committed CPT 2026 text answers each one, so no secondary source governs:

- **When an ordered test counts.** `definition-data-analyzed` counts a test
  ordered during an encounter in that encounter, because a result is presumed
  to be analyzed when reported. A test ordered outside an encounter counts in
  the encounter where it is analyzed. Each new result of a recurring order
  counts in the encounter where it is analyzed.
- **Whether ordering plus independent interpretation is one credit or two.**
  `definition-independent-interpretation` says a test ordered and independently
  interpreted may count both as a test ordered and as an interpretation.
  `icd10-cpt` step 5's ECG rule already applies this.
- **What a separately reported test loses.** `definition-data-analyzed` says a
  service whose professional component the E/M clinician reports separately is
  not counted as any data element: ordered, reviewed, analyzed or independently
  interpreted. It loses all data credit, not only Category 2.

Vendor articles claiming a 2026 revision of the MDM risk table cited no AMA or
CMS source. The committed sheet is the 2026 book's own text, so it, not those
articles, describes the 2026 table.

## Sources

Read on 2026-11-10 from cms.gov. Both are federal works in the public domain.

| Document | URL | SHA-256 of the file read |
| --- | --- | --- |
| 1997 Documentation Guidelines for E/M Services | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnedwebguide/downloads/97docguidelines.pdf | `105e2b1e6e802a5020a4454ed5b9e4bfa356822bef0031682d72c7f1883d56ab` |
| 1995 Documentation Guidelines for E/M Services | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnedwebguide/downloads/95docguidelines.pdf | `186a217526c8b0fae16151ee69344c7073c80bdd78b612aa991a5911c604ff05` |
| MLN006764, Evaluation and Management Services, May 2026 | https://www.cms.gov/outreach-and-education/medicare-learning-network-mln/mlnproducts/downloads/eval-mgmt-serv-guide-icn006764.pdf | `2b2f327d70a599cfedad8b30c7112e66073ca9c60b9a3823c4a4224392f45c82` |

Two things here rest on secondary or unopened sources. One is the Marshfield
provenance and the Novitas "aid only" description. The other is the existence
of payer worksheets that translate the CPT table into tallies, published by
First Coast, Novitas and AAPC among others. Nothing in this repository depends
on either beyond the statement that such sheets exist.
