# Clinical status, manifest, and Review sheet

Use this route after the notes and their visible coding worksheets are final, for both a
batch-shift and a standalone clinical-note. Keep its JSON and evidence files private in the run.
Patient details come from `openers.json`; the builders never reread the shorthand for them.

## Record office status

For every office encounter, record the settled `new` or `established` value:

```text
python tools/encounter_status.py <run> --note <number> --value <new|established> --evidence <identity-map|medatrax|clinician-answer> --evidence-path <private-file> --pointer <selected-row-reading-or-answer>
```

The command fingerprints the evidence file itself and retains the selected pointer in
`encounter-status.json`. For `clinician-answer`, also pass `--reply-file <whole-reply.txt>`.
That file carries the clinician's whole verbatim message to whichever stop asked the question;
the evidence file must contain it. The source day file or shorthand comes from the opener record.
The freshness gate still checks the whole reply against the run transcript after that source's
modification time. A delegate never supplies a clinician answer. An ED encounter needs no office
status command and the manifest records `not-applicable`.

Require exit 0. A missing office status, unreadable record, changed evidence, or encounter outside
the opener population refuses. The fingerprint proves unchanged evidence; the operator still
chooses the correct row and decides what its words establish.

## Build, run freshness visibly, then render

Write a private `manifest-inputs.json` list with one object per opener in the same order:

```json
[
  {
    "note": "note-1.md",
    "worksheet": "visible-worksheet-1.md",
    "setting": "emergency-department",
    "codes": {"icd10": ["R05.9"], "em": "99283", "cpt": [], "hcpcs": []}
  }
]
```

The example is synthetic. Supply this encounter's final code selections and its visible worksheet,
never the private anchored worksheet. Paths resolve relative to the run. A standalone note uses
one object and adds `--single` to the build command. Every note needs one named Medatrax field
block. If the note includes its visible worksheet, it must equal the selected worksheet file.
Keep its canonical private worksheet at `<run>/worksheets/<note-stem>.md`. The builder compares
for-entry code identities in that worksheet and the visible selections with the manifest's code
populations. A mismatch refuses; provenance-only edits do not alter the normalized approval identity.

```text
python tools/review_manifest.py build <run> --inputs <manifest-inputs.json> --course <resolved-course> --preceptor <resolved-preceptor> --site <resolved-site>
python tools/coding_freshness.py <run>/batch-codes.json --receipt <run>/batch-freshness.json
```

Require both commands to exit 0 and show the freshness command's output. The builder computes
normalized clinical-note and visible-worksheet fingerprints, separately fingerprints each Medatrax
field block, and writes `batch-codes.json` through the shared locked transaction. It also binds
opener details, status evidence, membership and order. Normalization uses UTF-8, LF, trailing-space
removal per line and one final newline; private tier blocks, Medatrax fields and technical receipts
are excluded from the coding fingerprint. The field fingerprint remains separate.
For a batch, pass this run's constants resolved in batch-shift step 6; the service date comes from the opener
record. The manifest binds these constants, and the renderer prints them once at the top.
A standalone `--single` build omits the three Review-sheet options.

For batch-shift only, then run:

```text
python tools/review_manifest.py render <run> --output <output/notes/review-sheet.docx>
```

The render rereads the same source population and refuses a missing, nonpassing, mismatched or
stale freshness receipt. It calls `docx_write.py` with its plain layout and explicit
`[[PAGE_BREAK]]` marker, preserving that writer's overwrite, main-checkout and outbound-character
guards. Use `--force` only for an intentional replacement under the existing overwrite rule.
Every encounter starts a page and its visible worksheet follows its note. The patient questions,
repairs, delegated answers, coding remarks, coverage lines and UpToDate disclosure stay in chat.
The code graders and examination gate remain required before rendering; the builder is no
substitute for them.

## Bind approval

Use `binding = review_manifest.approval_binding(run, batch=True)` for a shift and `batch=False`
for one note, then pass `sources=binding.sources` to both `approval_record.prepare` and
`approval_record.approve`. Both revalidate the current manifest and passing receipt. Entry-copy
grammar, coding remarks and UpToDate disclosure still read the notes. The latest modification of
any note, selected worksheet, manifest or receipt starts the approval-reply window; delegated
answers keep their own answer-file window.
Both the visible worksheet and canonical private worksheet count in that latest-change window.

Approval binds the manifest and receipt, including field fingerprints. A clinical, coding,
status, membership, order or field change requires rebuilding and fresh approval; a layout-only
Review-sheet render leaves the identity unchanged. The posted reading's `SUBMISSION-SHA256`
continues to fingerprint actual saved note bytes independently of this JSON approval identity.
Earlier approvals without the manifest marker keep their historical raw-note contract.

These commands establish mechanical binding, not clinical correctness, current publisher facts
after the recorded freshness check, or what a portal saved. Their complete boundaries belong to
`encounter_status.DECLARED_LIMITS` and `review_manifest.DECLARED_LIMITS`.
