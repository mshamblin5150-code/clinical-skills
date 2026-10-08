# ICD-10-CM FY2027: linked conditions and long-term drug use

Read on 2026-10-08 for [#1417](https://github.com/mshamblin5150-code/clinical-skills/issues/1417).
Source: [CDC/NCHS Official Guidelines for Coding and Reporting, FY2027](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2027/ICD-10-CM-October-1-2026-FY27-Guidelines.pdf).
Service-date scope: October 1, 2026 through September 30, 2027; consult any
applicable replacement release. Earlier services require their own edition.
Reading route: opened the official PDF with web and downloaded the same CDC
document for a direct PyMuPDF page reading. Printed pages are the locators below.

## Section I.A.15 — With, printed page 11

The classification presumes causation for conditions linked by `with` or `in`
in a code title, index, or tabular instruction. Separate provider linkage is
unnecessary unless the note clearly says unrelated or another guideline demands
explicit linkage. Conditions without a classification link still need provider
linkage. An index route never documents a missing condition.

## Section I.C.21.c.3 — Z79, printed pages 95–96

Continuous prescribed therapy for chronic treatment, lengthy treatment, or
prophylaxis supports Z79; aspirin is included. Brief acute treatment does not.
Drug addiction and detoxification or withdrawal-maintenance treatment use the
appropriate drug-use, abuse, or dependence code instead.

## Workflow boundary

[ADR 0292](../docs/adr/0292-directed-otc-agents-are-drug-management-and-modifier-25-joins-the-committed-cpt-sheet.md)
requires named-class codes and excludes `Z79.899` from this workflow. That is a
local ruling, not a prohibition attributed to these guidelines. Intended duration
and code-specific tabular restrictions remain encounter readings.
