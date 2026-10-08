# Code-label descriptor-agreement control

Historical run recorded 2026-10-08 for #1459 and ADR 0301. A fresh generating agent read the
amended clinical-note and icd10-cpt skills and received the deidentified shorthand from
`fixtures/day-b/shorthand/case-01.md` pasted into its brief, without fixture identity or access
to earlier controls. It wrote the note and private worksheet in separate directories and
completed its writer self-grade. A separate fresh reader received only the first-round blind
brief, shared sourcing instructions, and committed ICD-10 lookup access. Private writer
self-records were withheld. No reader retry occurred.

First-round wrong-place count: 0.
First-round code-label finding count: 0.

These counts are derived by:

```bash
python tools/anchor_scan.py fixtures/descriptor-agreement-code-label-control/worksheets --notes fixtures/descriptor-agreement-code-label-control/notes --agreement-read fixtures/descriptor-agreement-code-label-control/agreement-read.json
```

`first-round-report.txt` retains that command's first-round reading. The test regrades the
retained files and binds these two recorded counts to its report. Descriptor-words agreement
and reader independence remain readings; a clean mechanical result does not settle every
clinical judgment in the note. No CPT or HCPCS subject was generated: the given incision and
drainage remained a plan, not a completed act. This control establishes no procedure-placement
coverage and is not a completed portal workflow or finalized coding batch.

The coordinator read the complete note and worksheet for identifiers before retaining them.
They contain no patient name, visit date, site, or account identity. The generated artifacts,
generator record, and reader record are preserved byte for byte with no redaction or correction.
The source shorthand already withheld identifiers. Limitations and generation-time corrections
are recorded in `generation-record.md`; they are not independent-reader retries.
