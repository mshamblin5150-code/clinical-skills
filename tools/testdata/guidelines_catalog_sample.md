# Guideline catalog (fixture)

Prose above the table, including a legend table that is deliberately *not* the
catalog. Taking whichever table came first read this legend as malformed rows.

| Column | What it is |
| --- | --- |
| `society` | the source subdirectory |
| `year` | the publication year of this document |

| society | filename | title | topic | population | year | page_count | class | citation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACIP | schedule-adults.pdf | Recommended Vaccinations for Adults \| Vaccines & Immunizations \| CDC | adult immunization schedule | adult | ? | 7 | web-capture | https://www.cdc.gov/vaccines/imz-schedules/adult-easyread.html |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease | chronic kidney disease | ? | 2024 | 199 | guideline | 10.1016/j.kint.2023.10.018 |
| USPSTF | copd-screening.pdf | Screening for Chronic Obstructive Pulmonary Disease: US Preventive Services Task Force Reaffirmation Recommendation Statement | COPD screening | adult | 2022 | 6 | recommendation-statement | 10.1001/jama.2022.5690 |

Prose after the table, which must not be read as a row.

## Unsettled cells

- `schedule-adults.pdf` — `year` — a web capture of a schedule page carrying no edition year
- `KDIGO-2024-CKD-Guideline.pdf` — `population` — the front matter states no population
