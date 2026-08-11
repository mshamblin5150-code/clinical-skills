---
name: batch-shift
description: Split one shift's worth of clinical shorthand into separate encounters and process them all in one run. Use when the user pastes a whole shift, several patients at once, or says "here's my shift", "do all of these", "batch these".
---

A shift dump is many **encounters** run together in one paste. The unit of work is the encounter; this skill's whole job is getting the boundaries right before any note is written.

**A wrong boundary merges two patients.** One patient's vitals land in another's note, and the error is invisible downstream — every note reads fine. Splitting is therefore confirmed with the clinician before anything is processed, not after.

## Steps

### 1. Read the day header

A day's file carries the date and the **preceptor**, in the filename, in a header at the top of the file, or both:

The convention is `<date> <preceptor>_<scan timestamp>.pdf`, and it varies:

- `<date> <preceptor> Final Round_<timestamp>.pdf` — preceptor in the filename only.
- `<preceptor> <date>_<timestamp>.pdf` — the two swap places in about a fifth of the catalog.
- `<date> <preceptor>, <preceptor>_<timestamp>.pdf` — **two** preceptors, and the file itself opens with only the first.
- `Notes_<timestamp>.pdf` — no date and no preceptor at all. Both must be asked for.

Read both sources. A comma in the preceptor position means a **dual-preceptor day**, and the file header decides which encounters belong to which — if it does not say, that is a question for the clinician, not a guess. Preceptor attribution is what makes the hours count.

Day files name preceptors by first name; Medatrax wants `Last,First` exactly.

**The mapping is per-clinician and lives in `scratch/medatrax-profile.md`**, written by [setup-clinical-skills](../setup-clinical-skills/SKILL.md). Read it there rather than from this file — a preceptor list belongs to one account and does not travel.

**A name that maps to nobody is reported, never substituted.** In this clinician's catalog three of them do not map: one is a physician who was present but is not the preceptor of record, and two are a first name whose nearest picklist entry has a different surname. Guessing the nearest match is how a shift's hours get attributed to someone who was not there, and nothing downstream will catch it. Only the clinician knows.

Where an unmapped preceptor is known to work a single population — a pediatrician, say — that still settles the `Patient Time` band for the whole day even while the preceptor field stays open. Record the band, hold the name.

### 2. Get the text out

Day files are PDFs, and they come in two kinds. Check before parsing:

- **Text layer present** — extract directly with PyMuPDF. **32 of the 49 files** in this clinician's catalog are like this, and they are the newer ones.
- **Image-only scan** — `page.get_text()` returns nothing and each page holds a single image. **17 of 49**, all from one stretch of 2025. No OCR tool is needed: render each page and read it visually.

```python
import fitz
d = fitz.open(path)
if not "".join(p.get_text() for p in d).strip():
    for i, pg in enumerate(d):
        pg.get_pixmap(dpi=140).save(f"page{i+1}.png")   # then read the PNGs
```

140 DPI renders these legibly. A zero-length extraction is a scan, never an empty file — never report a scanned day as containing no notes.

### 3. Find the boundaries

`Note N` is the delimiter. Each encounter opens with `Note 1`, `Note 2`, … followed by the patient name, then the demographic line, then some order of `hx:`, `meds:`, `cc:`, and a narrative.

**It held for all 548 encounters in the clinician's catalog** — 48 unique day files, both halves. No encounter opened any other way, so the fallback below is genuinely a fallback.

**The name is not reliably the line after `Note N`.** It can sit below the vitals, or below a remark the clinician wrote to themselves. Both of these are real:

```
Note 1                          Note 22
8yo F                           i saw this patient last week
124/65 HR 115 SpO2 99% T 99.6   [PT]
[PT]                            dob [DOB]
```

Read a **window** of the first few lines and take the first one shaped like a name. Reading exactly one line loses both patients above, and a patient whose name is lost is a patient who gets a second Patient Reference — see [setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 6.

**The demographic line takes four shapes, and only two of them state an age:**

| Shape | Share | What it means |
| --- | --- | --- |
| `48 yo F`, `10 F`, `13 month male` | **69%** | Age given |
| Both age and `dob` | 15% | Cross-check them; a disagreement is a question, not a rounding choice |
| `dob <date>` and no age | 12% | Age is derived from the date of birth and the visit date, and must be computed **before** the date of birth is redacted |
| **Neither** | **5%** | Report it — see step 4 |

**The mix differs sharply between the two halves of this catalog**, so do not carry a share from one into the other: the image-only 2025 scans nearly always state an age outright, while the 2026 text files lean on `dob`. Measure the file in front of you. The derive-age-before-redacting rule matters wherever `dob` appears, whatever the share.

**Match case-insensitively.** Real files carry `Note 3`, `NOte 3`, and `NOte 4` in the same document. A case-sensitive match silently merges encounters.

Split on `Note N` and nothing else. Fall back to heuristics — a new age/sex opener, an unconnected new chief complaint — only where the numbering is broken or absent, and say so when you do.

Assign **every line** to exactly one encounter. The day header, and anything else belonging to no encounter, goes to an **Unassigned** list — never folded into the nearest patient.

**The numbering is not trustworthy, and that is not a parsing bug.** In this catalog one file skips from `Note 8` to `Note 10` with no encounter missing, and another numbers two consecutive encounters `Note 2`. Completion is therefore: every line lands in exactly one encounter or in Unassigned. **Report a gap or a repeated number; never renumber to make the sequence tidy.**

### 4. Confirm the split — stop here

Present the proposed split and wait for the clinician. Do not process.

```
Found N encounters:
  1. <age/sex> — <chief complaint> — <first line, verbatim> … <last line, verbatim>
  2. …
Unassigned lines: <verbatim, or "none">
Low-confidence boundaries: <which splits you are unsure about, and why>
Openers missing age or sex: <which encounters, and which field>
```

Show the first and last line of each encounter verbatim — that is what lets the clinician spot a bad boundary at a glance. Naming a low-confidence boundary explicitly is part of the output; silence there reads as certainty you do not have.

**An opener that omits age or sex is reported here, not later.** It is not a boundary problem, so it does not belong on the low-confidence line, and it is not the kind of gap that survives to be filled downstream — age sets `Patient Time`, and no amount of reading the encounter recovers it. This stop is the cheapest moment it can be answered: the clinician still remembers the patient. After this, the only source left is the Medatrax record.

Resume only on the clinician's confirmation or correction.

### 5. Process each encounter

Run [clinical-note](../clinical-note/SKILL.md) against each confirmed encounter independently, on the branch the user named — the whole shift takes the same branch unless they say otherwise. Independently means **no carry-over**: a glossary expansion resolved in encounter 2 applies to encounter 5, but a clinical finding never crosses an encounter boundary. If encounter 4's shorthand omits vitals, encounter 4 fills its own from its own age — it never borrows encounter 3's.

Number the output and keep the source order.

### 6. Roll up the shift

First the **schedule table** — the Medatrax entry view, one row per encounter in visit order:

```
| # | Age/Sex | Start–End | Len | Case Type | Patient Time |
```

Fields constant across the day — Course, Site, Preceptor, Interaction Level — are stated once above the table, not repeated on every row. **No patient name column.** Medatrax generates its own Patient Reference and never accepts a name, so the table has no use for one and standing rule 1 forbids it.

This is a **roll-up of** the per-encounter Medatrax blocks from `clinical-note` step 5, not a replacement for them. Every note still emits its own block; the table is the tabbing view across the day. Dropping the per-note blocks is what previously hid `Race/Ethnicity` — a field never reported missing because it was never reported at all.

Then consolidate:

```
--- SHIFT SUMMARY ---
Encounters: N
Notes clean (no flags, no gaps): <numbers>
Notes needing attention: <number — the flag or the gap, one line each>

--- FLAGS ACROSS THE SHIFT ---
<note number — the finding, and what was not done with it>

NEW GLOSSARY CANDIDATES: <unknown tokens seen across the shift, with frequency>
```

Completion: every encounter appears in exactly one of the two note lists.

**Read FLAGS first.** A gap is work outstanding and announces itself. A flag is a note that reads perfectly well and acted on only part of what it documented — nothing about it looks wrong. The roll-up is the only place the pattern is visible: one flag in one note looks like a hard case, five across a shift is what a twelve-hour day does to documentation.

The glossary candidates are the compounding part. Tokens that appeared more than once are the ones worth adding to [GLOSSARY.md](../clinical-note/GLOSSARY.md) — offer to add them, and the next shift needs less input than this one.

### 7. Offer the shift document

**Offer a `.docx` of the shift. Produce it only when the clinician asks.**

The shift is the unit that leaves the machine — a single encounter is never handed over on its own, which is why the emit lives here and [clinical-note](../clinical-note/SKILL.md) has no document branch at all.

It is offered rather than produced because of what step 6 just printed. The FILLED block is generated content awaiting confirmation, and standing rule 2 puts that confirmation before submission. A document written straight off the roll-up is a document of unconfirmed content that looks finished. So the offer comes after the FLAGS, and the file comes after the clinician has read them.

**One file per shift. The finished notes and nothing else.**

Head it with the constants step 6 already states once — course, date, preceptor, site — then the notes, numbered, in source order, one per page.

What stays out, and this is the whole point of the step:

| Kept out | Because |
| --- | --- |
| The tier blocks — `DERIVED`, `FILLED`, `FLAG`, `GAPS`, `UNKNOWN` | Working output. A FLAG says *this note failed to act on what it documented*; traveling inside the file it describes, it is a defect report stapled to the work |
| The per-encounter Medatrax field blocks | Portal data entry. They are tabbed into a form, not read |
| The schedule table and the shift summary | The tabbing and triage views of the day, for the chat |

**The document carries exactly what the notes carry.** Writing it is not a second pass at de-identification and it is not the moment to restore anything: `[PT]`, `[DOB]`, `[MRN]`, `[SITE]` stay as placeholders. It is, though, the last point at which a leaked identifier is still cheap to catch and the first at which it becomes a file that gets opened somewhere else — so read the notes for real names before writing, not after.

**Write it into `output/notes/`.** Standing rule 1: `output/` is the gitignored home for finished work, as `scratch/` is for working material, and `.gitignore` excludes both along with `*.docx`. Name it by date; a filename is text like any other and carries no patient name and no Patient Reference.

Completion: every confirmed encounter from step 4 appears in the document exactly once, and no tier block, Medatrax block, schedule row or summary line appears in it at all.
