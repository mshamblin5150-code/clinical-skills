# Checked Medatrax patient and visit fields

After recorded approval and before entering the patient and visit fields, run the Required builder
from the checkout:

```text
python tools/medatrax_fill.py --run <run> --submission <key> --batch --profile <profile>
```

For a standalone clinical-note, replace `--batch` with `--notes <final-note>`.
Use the current run's configured profile, never a previous run's fill builder or output.
Require exit 0 before using the generated files.

Profile choices are read from named `Course`, `Site` and `Preceptor` sections (plural headings
also work), using bullet values, code spans or tables, or from named rows in a `Picklists` table.
Keep the saved picklist strings exact; unsupported prose refuses rather than guessing a choice.

Write the Medatrax block as a `Field | Value` table or one `Field: Value` per line. Use one
row per control: `Age` and `Age unit`, `Start time` and `End time`, and `Blood pressure systolic`
and `Blood pressure diastolic` are separate rows. The reference's combined display labels describe
their grouping, not a value the builder should split or infer.

The builder reads the approved notes' Medatrax field blocks and checks their fingerprints against
the manifest bound by approval. It validates the current manifest and passing freshness receipt;
an absent, unreadable, changed or unapproved source refuses. Age and sex are checked against
`openers.json`; times must use `HHMM` and satisfy the shared visit-time checks. Preceptor and Site
must match the profile's exact picklist strings. Course comes from the profile. The remaining
picklists use `reference/medatrax-fields.md`'s exact values. In particular, Interaction Level is
checked against `Level 0` through `Level 5`; the profile default supplies the initial choice and
is not an equality constraint on an approved per-shift choice. Every free-text field passes the
shared outbound control-character check. The builder checks supplied values rather than deriving
a second set of patient fields.

The checked, ordered field list is `<run>/medatrax-fill/fill-fields.json`. Each selected encounter
gets `<run>/medatrax-fill/fill-note-N.js`, generated from that list. Keep both private in the run.
Use the script for that encounter on its patient or visit edit form through the available page-script
tool. It locates controls by their associated visible labels and exact select options, refusing
missing or ambiguous targets before typing. It fills fields and dispatches `input` and `change`
events; use the portal's ordinary Create or Submit action after reviewing the filled form.
The separate note-form route still reads `private/form-sections/note-N.json`.

A refusal stops entry. Correct the source, rebuild the manifest and rerun freshness and approval
where the approved content changed, then rerun this builder. Preserve the clinician's separate
Objective-pair rulings, delegated-answer records, coding-remark outcomes and go-ahead disclosures.

The builder and generated scripts have synthetic validation only; their control targeting has
not been verified against a live Medatrax page. A clean local build establishes checked inputs,
not what the portal accepted or saved. Read every saved Patient Detail field against the approved
Medatrax block, correct an ordinary mismatch and reread, and stop for the clinician on any other
discrepancy under the existing entry procedure. The generated files replace neither that readback
nor the saved-note View reading and posted-reading record. Complete mechanical limits belong to
`medatrax_fill.DECLARED_LIMITS`.
