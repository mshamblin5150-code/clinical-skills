# An E/M audit check-off is rendered from the coding records and every level gets a blind re-derivation

**Measured at:** 798837cfdf85946f17a9c44d53c1b8581154e80e

On 2026-11-10 the clinician asked for something he could hand to an auditor that shows, element by
element, how the professional E/M level on a finished note was derived. His codes feed an academic
clinical-hours record, so the packet answers for each level he logs. Over 2026-11-10 and 2026-11-11
he was shown the options below with their costs and ruled on each. **This record carries those
rulings; the build is named under Consequences.**

## Measured before ruling

**The coding run already wrote most of what a check-off needs, as machine records.** The manifest
`batch-codes.json` and its freshness receipt carry each encounter's setting, office status
evidence and final code populations; the private worksheet `worksheets/<note stem>.md` carries every
code with its anchor, source, specificity and confidence, and the filled-anchor, refusal and
undocumented blocks. `tools/review_manifest.py` validates that population for approval.

**Two things existed only as prose.** The manifest's `em` value is the code alone, and the
problems, data and risk behind it lived in the visible worksheet and the E/M paragraph of the note,
with no CPT entry id, note text or rule per element. The answers to step 5's level-changing
questions had no record of their own; `skills/icd10-cpt/SKILL.md` named "the run's private
pre-approval answers" without a file or format.

## Ruling 1 — a separate skill renders the run's own decisions, for the professional level only

`em-audit` renders a per-note check-off from the coding run's machine records, so the readable packet
and the records cannot disagree. It covers the clinician's professional MDM level, office
99202–99215 and emergency department 99281–99285. The ED facility grid stays a reference under
ADR 0444; the skill marks where a facility section could be added if he asks.

Shown alternatives: folding the packet into `icd10-cpt` (cost: a longer coding skill every run
reads, for an artifact only an audit needs); a packet written separately from the records (cost: two
accounts of one decision that can drift); including the facility level (cost: it is the hospital's
level, not his, and ADR 0444 keeps the grid off his).

## Ruling 2 — `icd10-cpt` records each E/M element as structured data

Step 5 writes an element block under the private worksheet's E/M line: one line per problem, data
item and risk weighed, counted or not, with its CPT MDM sheet entry id and verbatim note text, plus
the rules, answers, ECG limb, MDM line and level. The line format is defined once in
`skills/_shared/reference/em-elements.md`; the re-derivation record uses the same lines.

Shown alternatives: (a) the block, chosen (cost: a line format the coding run must write and every
worksheet grader must tolerate); (b) keep the prose and rely on the re-derivation for element
detail (cost: none to build, but the run's own reasoning reaches the auditor only as prose).

## Ruling 3 — a private record keeps every pre-approval question and the whole reply

`pre-approval-answers.json` keeps, per run, each coding question step 5 puts before approval, the
note it concerns, the levels it names and the clinician's whole reply, matched against the
transcript as approval matches a reply. It records questions that change no level too. Element
blocks refer to its entries by id.

Shown alternatives: (a) the record, chosen (cost: one more private record per run and one command
at each answer); (b) leave the answers in the transcript and the worksheet prose (cost: an auditor
sees a level resting on an answer nobody can show him).

## Ruling 4 — the check-off identifies a note without the patient's name

The check-off names the encounter number, service date and note filename only.

Shown alternatives: (a) add the opener name (cost: a direct identifier on every sheet, in exchange
for easier matching to a chart); (b) the three identifiers, chosen (cost: the clinician matches the
sheet to his chart by date and encounter number).

## Ruling 5 — a Word copy is written only on request

Markdown in the private run is the check-off. `python tools/em_audit.py <run> --docx` renders chosen
notes to Word through `docx_write.write_docx`, into the main checkout's `output/`, keeping that
renderer's overwrite refusal and `--force`. Nothing writes a Word copy by default.

Shown alternatives: (a) Markdown only (cost: he converts by hand when an audit arrives); (b) an
on-demand export, chosen (cost: one more patient file in `output/` only when he asks); (c) a Word
copy with every render (cost: a patient file per note per run whether or not anyone is audited).

## Ruling 6 — every coded note needs a blind re-derivation before completion

A second reader re-derives each note's level from the note and the recorded answers before it sees
the worksheet, writes an element block, and the check-off compares the two element by element. A
coded run is complete only with a placed re-derivation and a current check-off for every note;
each difference is shown to the clinician before approval and changes no code.

Shown alternatives: (a) required for every note, chosen (cost: one reader pass per note);
(b) optional, with the sheet saying "Not performed" (cost: a packet whose level was checked by the
same pass that chose it).

## Consequences

- `skills/em-audit/SKILL.md` and `skills/em-audit/rederivation.md` hold the procedure;
  `reference/em-audit-checkoff.md` is the blank template; `skills/_shared/reference/em-elements.md`
  defines both record shapes.
- `tools/em_audit.py` renders, compares and exports; `tools/preapproval_answers.py` writes the
  answers record; `tools/worksheet_grammar.py` reads the element block for every worksheet reader.
- `skills/icd10-cpt/SKILL.md` step 5 writes the block and records each answer; its completion
  requires the re-derivations and a current check-off for every note, graded by
  `tools/specificity_scan.py` as the row `the E/M audit check-offs`. That check starts at this
  record, through `reference/completion-check-starts.tsv`, so runs approved earlier are not graded
  by it.

## What none of this reaches

The check-off restates the run; it does not decide whether a level is right. Nothing establishes
that a re-derivation was written before its reader saw the worksheet beyond the brief that withholds
it, and nothing establishes that a difference was shown to the clinician beyond the skill's
instruction. A level selected by total time is not represented by the MDM line.
