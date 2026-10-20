# Encounter openers and identity-map rows

Before processing an encounter, retain its source and the opening details you read in one
private record. The Required command is `tools/encounter_openers.py`; every later builder reads
patient details from `openers.json`, never by parsing the shorthand again. Its complete boundary
belongs to `encounter_openers.DECLARED_LIMITS`.

Write a private `opener-readings.json` array, in encounter order. Each object has `note` (one-based
integer), `name`, `age`, and `sex`. Each detail is the exact text read, or JSON `null` when omitted.
Do not infer an omitted detail. A name read from shorthand must occur literally in that encounter's
text, including when it appears on the `Note N` line. The command does not decide whose name it is.

For a day file's retained UTF-8 extracted text:

```bash
python tools/encounter_openers.py record --run <run-directory> --source <day-file-text> --readings <opener-readings.json> --service-date <YYYY-MM-DD>
```

It imports the shared `Note N` delimiter, refuses absent, skipped, or repeated numbering with
exit 2, and refuses a different number of readings. It writes `encounters/encounter-N.txt`,
`encounters/unassigned.txt` for the day header before the first encounter, and `openers.json`.
Together the recorded spans must account for the complete source exactly once. Display the
Unassigned text at the split confirmation; it is never silently folded into a patient.

On broken or absent numbering, make the clinical cut yourself and run the same command with
`--mode hand --reason <why-the-cut-was-needed>`. Each reading then also carries `start` and `end`:
zero-based Unicode character offsets into the retained UTF-8 text, end exclusive. Spans must be
contiguous and end at the source's end; text before the first span stays Unassigned. The command
records the hand-cut mode and reason. Check every boundary and Unassigned line with the clinician;
mechanical coverage cannot decide whether a cut is clinically right.

For one pasted encounter, retain it as UTF-8 text and use the same command with `--mode single`
and one reading numbered `1`. It records the whole source without splitting.

Report missing name, age, and sex at batch-shift step 4 (or before standalone processing). Ask
the clinician for a missing name. Record the answer through:

```bash
python tools/encounter_openers.py answer --run <run-directory> --note <N> --name <answered-name> --reply <clinician-answer>
```

The record identifies it as a clinician answer, exempt from the shorthand in-text check. When
the clinician cannot supply a name, omit `--name` and retain that response with `--reply`. This
records that the question was asked; an unasked missing name refuses the identity-map write.
The answer command changes only an omitted name, leaving the source and split intact.

Immediately after Medatrax creates a new Patient Reference, use the Required writer:

```bash
python tools/encounter_openers.py identity --run <run-directory> --note <N> --reference <new-reference> --map <private-identity-map>
```

It rereads the source, encounter files and opener record, refuses changed evidence, takes the
name from that record and the date from its service date, and adds a row with source filename and
note number under `## Newly entered patients`. An unanswered name goes under `## Cannot be
matched`, with its recorded age and sex. Existing map bytes stay unchanged. A reference must be
15 hexadecimal characters and absent everywhere in the map. The map uses Markdown pipe-table
rows; a missing destination or section is created with the documented columns.

For every same-name table row, supply a private JSON object mapping its existing Patient
Reference to the reason it is a different person, and pass `--collisions <file>`. The writer
refuses unless that set exactly covers the matching rows, then writes each ruling under
`## Collisions` beside the new reference. This records a judgment; it cannot establish identity.
Read every matching row and settle which patient fits before creating one in Medatrax. A later
writer refusal cannot undo a duplicate already created there.

Every write is serialized by the artifact lock and atomically renamed with destination readback.
An existing malformed opener record is refused, never replaced by an empty record. Exit 0 means
the command completed its stated checks; exit 2 refuses missing, invalid, changed, busy, or
incomplete evidence. Reports contain counts only; all inputs and generated records remain private.
