---
name: batch-shift
description: Split one shift's worth of clinical shorthand into separate encounters and process them all in one run. Use when the user pastes a whole shift, several patients at once, or says "here's my shift", "do all of these", "batch these".
---

A shift dump is many **encounters** run together in one paste. The unit of work is the encounter; this skill's whole job is getting the boundaries right before any note is written.

**A wrong boundary merges two patients.** One patient's vitals land in another's note, and the error is invisible downstream — every note reads fine. Splitting is therefore confirmed with the clinician before anything is processed, not after.

## Steps

### 1. Find the boundaries

Read the whole dump and locate the split points. Encounters typically separate on a room or bed number, a time stamp, a blank line plus a new age/sex opener (`44M`, `7yo F`), a `pt 3` style marker, or a new chief complaint with no connective tissue to what precedes it.

Assign **every line** of the source to exactly one encounter. A header, a shift note, or a personal reminder that belongs to no encounter goes to an **Unassigned** list — it is never folded into the nearest patient.

Completion: line count of all encounters plus Unassigned equals line count of the source.

### 2. Confirm the split — stop here

Present the proposed split and wait for the clinician. Do not process.

```
Found N encounters:
  1. <age/sex> — <chief complaint> — <first line, verbatim> … <last line, verbatim>
  2. …
Unassigned lines: <verbatim, or "none">
Low-confidence boundaries: <which splits you are unsure about, and why>
```

Show the first and last line of each encounter verbatim — that is what lets the clinician spot a bad boundary at a glance. Naming a low-confidence boundary explicitly is part of the output; silence there reads as certainty you do not have.

Resume only on the clinician's confirmation or correction.

### 3. Process each encounter

Run [soap-note](../soap-note/SKILL.md) against each confirmed encounter independently. Independently means **no carry-over**: a glossary expansion resolved in encounter 2 applies to encounter 5, but a clinical finding never crosses an encounter boundary. If encounter 4's shorthand omits vitals, encounter 4 has no vitals — it does not borrow encounter 3's.

Number the output and keep the source order.

### 4. Roll up the gaps

After the last note, consolidate:

```
--- SHIFT SUMMARY ---
Encounters: N
Notes complete (no gaps): <numbers>
Notes needing input: <number — what it needs, one line each>
NEW GLOSSARY CANDIDATES: <unknown tokens seen across the shift, with frequency>
```

Completion: every encounter appears in exactly one of the two note lists.

The glossary candidates are the compounding part. Tokens that appeared more than once are the ones worth adding to [GLOSSARY.md](../soap-note/GLOSSARY.md) — offer to add them, and the next shift needs less input than this one.
