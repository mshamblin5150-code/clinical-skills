# Medatrax readback

After reading the saved visits and note forms, save their copied values as private
`readback.json` beneath the run directory. Use this input shape; replace the placeholders
with the portal's displayed values, never fabricated locators:

```json
{
  "post_url": "<copied visit-list address>",
  "posted": "<displayed posting time>",
  "verdict_detail": "<what was compared and matched>",
  "time_log": {"date": "<displayed-date>", "hours": 12, "minutes": 0, "outcome": "entered"},
  "visits": [{
    "patient": 3,
    "reference_status": "matched",
    "reference": "<copied Patient Reference>",
    "patient_detail": "<copied Patient Detail address>",
    "note_view": "<copied View address including resultid>",
    "visit_date": "<displayed visit date>",
    "finished": "<displayed Date Finished>",
    "verdict": "matches"
  }]
}
```

List visits in actual entry order. `patient` is the note-file number, which may skip numbers.
For a newly created patient use `"reference_status": "new"` and `"created"` instead of
`"visit_date"`. A returning patient uses `visit_date`. Optional `"corrections"` is a list of
`"<field>: <saved value> -> <approved value>"` strings, only after correction and a matching
second read. For no requested Time Log entry, use `"time_log": null`; otherwise supply separate
integer hours and minutes, with outcome `entered` or `matched`. This is the readback, not an
instruction to enter a Time Log.

Run both Required commands before the after-action extract:

```bash
python tools/medatrax_posting.py write --run <run-directory> --submission <key> --batch --input <run-directory>/readback.json
python tools/medatrax_posting.py check --run <run-directory> --submission <key> --batch
```

For a standalone note replace `--batch` in both commands with `--notes <final-output-note>`.
The writer computes the source fingerprint and `N of N read`, formats hours and minutes, and
validates the entire record through the existing posted-reading and Medatrax checks before
replacing the file. It preserves other submission blocks. Replacing an existing keyed block
needs explicit `--replace`; an unreadable or malformed existing record is left untouched.
The standalone check also accepts a hand-written record and writes nothing.

Exit 0 means the record passed. Exit 2 stops the after-action extract: inspect the private
evidence and correct the input or record before trying again. Neither command prints its
contents. The complete boundary belongs to `medatrax_posting.DECLARED_LIMITS`.
