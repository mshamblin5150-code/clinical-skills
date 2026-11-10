# An office ECG the clinician reads is billed with its interpretation and counts nothing toward data

**Measured at:** 0ce2ad21f7b5bc5aa04ecaa328a8d6e08573dc8d

On 2026-11-10 a research pass, run while building private E/M check sheets, tested the office limb
of [ADR 0308](0308-the-e-m-level-rests-on-what-the-clinician-did.md) ruling 6 against CPT text and
published guidance. Shown the evidence and three options, the clinician chose the one the CPT text
settles. The freshness gate read `FRESH` against `main` before this record was written. **Nothing is
built here beyond the prose changes named under Consequences.**

## Measured before ruling

**CPT settles the global code.** `reference/cpt-em-mdm-2026.md` entry `definition-data-analyzed`:
"Any service for which the professional component is separately reported by the physician ...
reporting the E/M services is not counted as a data element ordered, reviewed, analyzed, or
independently interpreted." 93000 includes the interpretation and report, so an ECG billed with it
counts for nothing toward data.

**CPT does not settle the tracing-only route ADR 0308 ruling 6 chose.** With only 93005 billed, two
phrases of the committed sheet weigh against counting the clinician's own read as an independent
interpretation: `definition-independent-interpretation` "does not apply when the physician or other
qualified health care professional who reports the E/M service is reporting or has previously
reported the test," and the MDM table's Category 2 names "a test performed by another
physician/other qualified health care professional (not separately reported)." The AMA's 2023
guidelines exclude an interpretation only "When the physician ... is reporting a separate CPT code
that includes interpretation and/or report," which 93005 does not
(https://www.ama-assn.org/system/files/2023-e-m-descriptors-guidelines.pdf, SHA-256
`5f6165e7c6370ed477889ff6db05369285bba364a4ef5f4012a40de0ab5360b2`). No source read resolves the
conflict.

**Secondary sources bill the global code when the office reads its own ECG.** AAPC Cardiology
Coding Alert (2021-08-27): "You should use code 93000 when your cardiologist performs an ECG in his
office. In this case, the cardiologist owns the ECG machine and performs the interpretation and
report." AAPC Primary Care Coding Alert (2003-06-01, older) assigns 93005 only where the office
"does not issue a report of his or her findings." Read from
https://www.aapc.com/codes/coding-newsletters/my-cardiology-coding-alert/ecgs-5-quick-tips-help-boost-your-electrocardiogram-reporting-skills-170054-article
(SHA-256 `d7ae9cab25b770c0fa484446bfb47afac1a34a20449358a548df3869475e8bc2`) and
https://www.aapc.com/codes/coding-newsletters/my-primary-care-coding-alert/you-be-the-coder-to-interpret-and-to-read-is-what-matters-article
(SHA-256 `96ae54bc42b10615d975e5c44416a2dac776064b06deb9635d798922c4a907b9`).

**A billed interpretation needs a report.** Medicare Claims Processing Manual ch. 13 §100.1, written
for emergency room patients: "a notation in the medical records saying 'fx-tibia' or EKG-normal
would not suffice as a separately payable interpretation and report"
(https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/downloads/clm104c13.pdf, SHA-256
`708f24fcbc2c1bb40ab8ff03aacd6dbd83159e7dea855d5a4b21b533ca8f1dd6`). Its office application is
inferred, not stated.

## Ruling 1 — an office ECG the clinician reads is billed as 93000 and counts nothing toward data

In an office or clinic encounter where the clinician's shorthand records his own read of an ECG
traced at that office, the worksheet bills 93000 and counts the ECG toward nothing in the data
element. The note carries his read as a written interpretation and report, not a bare "normal."
Where the shorthand records only "normal" or no findings, `icd10-cpt` puts one question in the run's
existing pre-approval questions asking for his findings; until he answers, it bills 93005 and counts
the ECG as one test ordered. Where the tracing came from elsewhere, nothing changes from ADR 0308
ruling 6.

Keeping ADR 0308 ruling 6's office limb was declined because the level it supports rests on a
reading two phrases of the committed CPT sheet weigh against and no source confirms. Billing 93005
and counting the order alone was declined because it leaves the clinician's read unbilled for no
gain in certainty over the global code.

## Consequences

- `skills/icd10-cpt/SKILL.md` step 5's *The clinician's own ECG read* paragraph and its office-ECG
  worked case apply ruling 1; the emergency department limb is unchanged.
- ADR 0308 ruling 6's emergency department limb stands: there the facility performs the tracing,
  the clinician bills no ECG code, and his read counts as an independent interpretation of a test
  performed by another and not separately reported.

## What none of this reaches

Whether a payer's fee schedule pays 93000, 93005 or 93010 to a given practice is a contract
question this record does not answer. A hospital-owned clinic, where the hospital bills the tracing
on its own claim, is a different case and is not ruled here.

## Supersedes

- [ADR 0308](0308-the-e-m-level-rests-on-what-the-clinician-did.md) ruling 6, the office or clinic limb: an office ECG the clinician reads is billed as 93000 and counts nothing toward data.
