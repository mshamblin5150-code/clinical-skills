---
name: batch-shift
description: Split one shift's worth of clinical shorthand into separate encounters and process them all in one run. Use when the user pastes a whole shift, several patients at once, or says "here's my shift", "do all of these", "batch these".
---

A shift dump is many **encounters** run together in one paste. The unit of work is the encounter; this skill's whole job is getting the boundaries right before any note is written.

**A wrong boundary merges two patients.** One patient's vitals land in another's note, and the error is invisible downstream — every note reads fine. Splitting is therefore confirmed with the clinician before anything is processed, not after.

## Steps

### 1. Read the day header

A day's file carries the date and the **preceptor**, in the filename, in a header at the top of the file, or both:

- `4-8-26 Lindley Final Round_260427_204257.pdf` — preceptor in the filename only.
- `1-12-26 dr frazer, sharon_260112_200412.pdf` — filename lists **two** preceptors, and the file itself opens `1-12-26 / Dr Frazer`.

Read both sources. A comma in the preceptor position means a **dual-preceptor day**, and the file header decides which encounters belong to which — if it does not say, that is a question for the clinician, not a guess. Preceptor attribution is what makes the hours count.

Day files name preceptors by first name; Medatrax wants `Last,First` exactly. Map through [medatrax-fields.md](../../reference/medatrax-fields.md):

| In the filename | Medatrax |
| --- | --- |
| Sharon | `Cecil,Sharon` |
| dr frazer | not on the Medatrax list — **paediatrics only**, so every encounter on a Frazer day is a Pediatric (0–17) Hours entry. Ask which Medatrax preceptor of record applies |
| Marie | `Green,Marie` |
| Miranda | `Lester,Miranda` |
| Lindley | `Lindley,Juddson` |
| Jessica | `Sharp,Jessica` |
| Julie | `Sison,Julie` |

A name that does not map — `dr frazer` appears in `1-12-26 dr frazer, sharon` but is on no Medatrax preceptor list — is **reported, never substituted**. It usually means a physician who was present but is not the preceptor of record, and only the clinician knows which.

### 2. Get the text out

Day files are PDFs, and they come in two kinds. Check before parsing:

- **Text layer present** — extract directly with PyMuPDF. Two of eighteen files are like this.
- **Image-only scan** — `page.get_text()` returns nothing and each page holds a single image. Sixteen of eighteen are like this. No OCR tool is needed: render each page and read it visually.

```python
import fitz
d = fitz.open(path)
if not "".join(p.get_text() for p in d).strip():
    for i, pg in enumerate(d):
        pg.get_pixmap(dpi=140).save(f"page{i+1}.png")   # then read the PNGs
```

140 DPI renders these legibly. A zero-length extraction is a scan, never an empty file — never report a scanned day as containing no notes.

### 3. Find the boundaries

`Note N` is the delimiter. Each encounter opens with `Note 1`, `Note 2`, … followed by the patient name, then age and sex, then some order of `hx:`, `meds:`, `cc:`, and a narrative.

**Match case-insensitively.** Real files carry `Note 3`, `NOte 3`, and `NOte 4` in the same document. A case-sensitive match silently merges encounters.

Split on `Note N` and nothing else. Fall back to heuristics — a new age/sex opener, an unconnected new chief complaint — only where the numbering is broken or absent, and say so when you do.

Assign **every line** to exactly one encounter. The day header, and anything else belonging to no encounter, goes to an **Unassigned** list — never folded into the nearest patient.

Completion: the encounter numbers run consecutively from 1 with no gaps, and line count of all encounters plus Unassigned equals line count of the source. A gap in the numbering is a missing note — report it rather than renumbering.

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
