# A case study's draft label is a reader's walk of the reference list

**Measured at:** 84418797c3451c4f6d5076e0d93ad83958308832

[#1584](https://github.com/mshamblin5150-code/clinical-skills/issues/1584) was filed from the
after-action review of a `practicum-case-study` run (NUR 5144 Module 4) in October 2026. Step 9's check
table row `the draft label on threshold-sheet citations` names `tools/differential_scan.py` as the
command that labels citations backed by a `draft` threshold source. In that run the reader ran the
command, it printed `NOT RUN`, and the reader correctly refused to read that as a pass. The clinician
ruled every point below on 2026-10-16, against `main` at the commit above, where the freshness gate
read `FRESH`. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**The command's draft limb reads a citation form a case study never writes.** `differential_scan.py`
finds a draft-backed citation only inside a physical `FILLED·proposed` opener whose tail reads
`threshold/<sheet>: <strength>, <population>, <value>` or `guideline/<topic>: <class>, ...`. That
shape belongs to `clinical-note`'s tier block. `skills/practicum-case-study/SKILL.md` and
`skills/_shared/reference/style.md` contain no `FILLED` form at all. A case study cites a number to
its guideline in APA form, and the only written link from one of its numbers to a threshold-sheet row
is the free-text `source` field of `<run-directory>/routing-walk.json`, which step 9 requires only for
numeric triggers.

**So the ticket's first option assumed a citation form that does not exist.** Teaching the command
to read a case study would mean a second reader matching APA citations to `## Sources` rows, sharing
no code with the note-side limb, plus passing the skill name through
`approval_record.apply_completion_gate`, which `differential_scan` calls with `"clinical-note"`
written in (the 2026-10-09 comment on the ticket).

**The draft population today is one source.** Across every `## Sources` table in
`reference/thresholds/`, one row carries source class `draft`: the KDIGO 2026 acute kidney injury and
acute kidney disease public review draft, in
`reference/thresholds/acute-kidney-injury-and-acute-kidney-disease.md`.

**The ticket's single-draft complaint is already served.** `differential_scan.py --note <path>`
landed for #1421 before the ticket was filed and reads one file as its population
(the ticket's second comment). Under ruling 1 it no longer matters to this row.

## Ruling 1. The row names only a reader

Step 9's draft-label row stops naming `tools/differential_scan.py`. Its How column names a reader and
nothing else. The command is unchanged and remains the note-side label under
[ADR 0063](0063-a-draft-backed-citation-is-caught-per-row-by-the-parser-the-module-already-shares-and-the-class-set-is-draft-alone.md).

[ADR 0061](0061-a-declared-non-source-is-an-enumerated-class-and-it-earns-a-fourth-sweep-state.md)
ruling 6 stands: `draft` still surfaces through this named row, and `checks_ledger.EXPECTED_CHECKS`
still fails a run that returns no verdict on it.

Teaching `differential_scan.py` the case-study shape was declined. Its matching would be fuzzy,
because an APA entry's wording is not a sheet key, and the "one owner" it promised was nominal
because the case-study reading would share no code with the note reading. A routing-walk floor, which
would give `routing-walk.json`'s `source` field a sheet-row grammar and let `checks_ledger.py` count
draft-backed numeric triggers, was deferred rather than refused. It reaches trigger numbers only, the
corpus holds one draft source, and it can be filed when a count of draft sources warrants it.

## Ruling 2. A `clean` on this row says what it walked

The row's `A clean says what it walked` cell becomes `yes`, and the row joins
`checks_ledger.SUBSTANTIATED_CLEAN`. With the command gone, nothing else stands behind a bare `clean`,
and a number from a public review draft presented as guidance in force is the costly skim
[#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255)'s substantiation exists for.
Most runs cite no draft source, so the `FINDINGS` line is the only evidence the walk happened.

Leaving the cell `no` was declined for that reason.

## Ruling 3. The reader walks the reference list against the draft sources

The reader lists every source whose `source class` is `draft` across the `## Sources` tables in
`reference/thresholds/`, checks each entry of the draft's reference list against that list, and for
each match reads every body sentence citing that entry: is the number identified as coming from a
public review draft, and kept from reading as guidance in force? The citation is never suppressed
solely because its source is a draft. Its `clean` names the reference entries checked, the draft
sources listed, and the matches found.

Tracing every number back to a sheet row through the routing walk and the claims ledger was declined:
the routing walk records trigger numbers only, and most numbers carry no recorded row, so the trace
could not be complete. A number taken from a draft source but cited to another work is a citation
error, which the row `the reference list, the part no command reaches` already owns.

## Corrects

ADR 0063's Consequences paragraph beginning **#587 item 6's check-table row changes before it lands**
ordered the row's command cell flipped to `differential_scan`. That paragraph is corrected in place on
[ADR 0016](0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-ratified-records-facts-may-be-corrected-in-place.md)'s
terms. It is a consequence rather than a numbered ruling, so no supersession marker applies; every
numbered ruling of ADR 0063 stands.

## Build checklist

- `skills/practicum-case-study/SKILL.md` step 9: the draft-label row's How column states ruling 3's
  reader brief and names no command; its last cell becomes `yes`.
- `tools/checks_ledger.py`: the row joins `SUBSTANTIATED_CLEAN`, and the module docstring and report
  wording stay consistent with it.
- `tools/test_checks_ledger.py`: `test_the_draft_source_class_reader_is_a_named_unsubstantiated_check`
  is inverted. It asserts the row names a reader, names no command, and is substantiated. A synthetic
  checks file with a bare `clean` on this row fails, and one whose `FINDINGS` names its walk passes.
- `reference/completion-check-starts.tsv`: the substantiation requirement on this row starts at the
  build's landing time and is compared with approval, under
  [ADR 0346](0346-a-posted-item-s-clean-terminal-grade-is-frozen-and-a-later-check-starts-on-a-recorded-date.md),
  so a run approved earlier is not newly failed by a bare `clean` it wrote before the requirement
  existed.

## What this record does not reach

- **A draft number cited to the wrong work.** The reference-list reading owns it.
- **A mechanical floor on case-study draft labels.** Deferred under ruling 1 until a count of draft
  sources warrants one.
- **Whether a draft's number should stand for this patient.** That stays the reader's judgment, as
  ADR 0063 already records.
