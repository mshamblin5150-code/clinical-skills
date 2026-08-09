# Medatrax field map

The single source of truth for the Medatrax patient entry. [clinical-note](../skills/clinical-note/SKILL.md) emits these in the order below so they can be tabbed straight into the form.

**Status: partial.** Field names and one real value each were recovered from a completed entry. The **picklist options are still unknown** — those marked `picklist` need their exact option strings recorded from the live form, because a near-miss string is a rejected or misfiled entry.

## Per-encounter fields

| # | Field | Type | Example | Source |
| --- | --- | --- | --- | --- |
| 1 | Visit Date | date | 04/08/2026 | given |
| 2 | Interaction Level | picklist | Level 5 | given — needs option list |
| 3 | Race/Ethnicity | picklist | White / Non-Hispanic | given — needs option list |
| 4 | Gender | picklist | Female | given |
| 5 | Age | number + unit | 35 years | given or derived from DOB |
| 6 | Marital Status at First Contact | picklist | Married | given — needs option list |
| 7 | Primary Payment Method | picklist | Commercial Insurance | given — needs option list |
| 8 | Start Time | time | 16:45 | given |
| 9 | End Time | time | 17:00 | given |
| 10 | Patient Height | number (in) | 64 in | given |
| 11 | BMI | number | 28.7 | derived from height and weight |
| 12 | Case Type | picklist | Endocrine Disorder | given — needs option list |
| 13 | Blood Pressure | text | 122/78 mmHg | given |
| 14 | Respiratory Rate | number | 16/min | given |
| 15 | Patient Time | picklist | Womens Health | given — needs option list |

## What this tells the note

Medatrax carries **BP, RR, Height, and BMI** — but not HR, temperature, SpO2, or weight. The note rubric wants a complete vital set, so those four are routinely **filled** (normal for age) and must appear in the FILLED block for confirmation. Any vital Medatrax *does* carry is a **given** and the note must match it exactly.

`Age`, `Gender`, and `Visit Date` are givens the note's opening line has to agree with.

## Still to confirm

- [ ] Exact option strings for every `picklist` field above
- [ ] Is there a free-text note body field, and does it have a character limit?
- [ ] Does it accept Markdown, or plain text only?
- [ ] Is `Interaction Level` an E/M level, an autonomy scale, or something else? Level 5 on what range?
- [ ] What does `Patient Time` categorise — the clinical hour bucket (Womens Health, Peds, …)?
- [ ] Is `Case Type` single-select or multi-select?
- [ ] Are weight, HR, temp, and SpO2 fields present but unused, or genuinely absent?
- [ ] Where do ICD-10 / CPT codes go, if anywhere?
- [ ] Is there a preceptor sign-off step, and what does it require?
- [ ] How are the 360 clinical hours accumulated — from Start/End Time per encounter, or logged separately per shift?

The last one matters most for the November 20 deadline. If hours come from Start/End Time, then every encounter's time fields are load-bearing and a missing one is lost credit.
