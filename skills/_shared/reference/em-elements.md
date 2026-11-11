# E/M element block and pre-approval answers

Two private run records carry what an E/M level rests on. The **element block** states each
element the selection weighed; the **pre-approval answers** record keeps every coding question put
to the clinician and his whole reply. [icd10-cpt](../../icd10-cpt/SKILL.md) step 5 writes both,
the [em-audit](../../em-audit/SKILL.md) re-derivation writes an element block of its own, and
`tools/em_audit.py` renders and compares them. Both stay in the run under `scratch/`.

## The element block

In the private worksheet `worksheets/<note stem>.md`, write one block, indented two spaces directly
under either E/M line the code reader accepts (an `E/M:` label line naming an office or
emergency department E/M code, or an E/M-family `CPT` entry for entry, each at the margin or
indented), one element per physical line, with no blank line inside the block. A label written
inside that entry's own indented lines belongs to the same block. A heading, indented or not,
ends the block. An E/M entry marked `NOT FOR ENTRY` is a rejected level, and so is a label written
inside its lines: neither is the selected code, and EM- lines under either form no block and are
counted unread:

```text
  EM-PROBLEM: <entry id> | <counted | not counted> | "<verbatim note text>" | <reason>
  EM-DATA: <entry id> | <counted | not counted> | "<verbatim note text>" | <reason>
  EM-RISK: <entry id> | <counted | not counted> | "<verbatim note text>" | <reason>
  EM-RULE: <the house rule, counting note, documentation check or ADR ruling applied>
  EM-ANSWER: <pre-approval answer id | none>
  EM-ECG: <the ADR 0443 limb applied | not applicable>
  EM-MDM: problems <level>; data <level>; risk <level>; mdm <level>
  EM-LEVEL: <the selected E/M code>
```

- **One element line per item the selection weighed, counted or not.** A condition left out under
  ADR 0308 is a `not counted` PROBLEM line whose reason says why; a test or drug the note pass
  proposed names itself in the reason, matching the `[SOURCE: filled - ...]` mark it supports.
- **Entry id** is a `## Entry:` id of the CPT MDM sheet for the service date, such as
  `definition-stable-chronic` or `table-moderate`. Where nothing of a kind is documented, write
  `none | not counted | none | <reason>`. The id carries the CPT meaning; the block copies no CPT text.
- **Note text** is the exact run of note text the element rests on, in double quotes.
- **Reason** describes what the note documents, under ADR 0376 ruling 2, and holds no `|`.
- **Level** in the MDM line is the column each element meets: `straightforward`, `low`,
  `moderate` or `high`. `mdm` is the level two of the three elements meet, the middle of the three,
  and `EM-LEVEL` is the code whose CPT 2026 descriptor names that MDM level; the check-off reads it
  from the verified descriptors in `reference/procedure-codes-2026.sqlite`. Where the level is
  selected by total time instead, write the rule line `EM-RULE: level selected by total time on the
  date of the encounter`; the level is then not held to the MDM line, and the selected code still is.
- Repeat `EM-RULE` and `EM-ANSWER` as needed; write `EM-ANSWER: none` when no recorded answer was
  relied on, and an `EM-ECG` line, `not applicable` where no ECG was weighed; where the worksheet
  bills 93000 or 93005, the line names that code. Exactly one `EM-MDM` and one `EM-LEVEL`. A
  block missing its `EM-ANSWER` or `EM-ECG` line is incomplete.
- The manifest build records a fingerprint of the whole private worksheet in its own file beside
  the manifest; after editing the worksheet, build again, or the E/M audit check-off refuses. An
  edit that changes no selected code leaves the manifest byte-identical.
- A counted line names a real entry id and quotes note text. A field line written after the
  block under the same E/M line is unread, never that line's provenance.

Synthetic example, an established office patient:

```text
E/M: 99213 Office or other outpatient visit, established patient, low MDM
  EM-PROBLEM: definition-stable-chronic | counted | "Diabetes stable, continue metformin" | evaluated and continued
  EM-PROBLEM: definition-stable-chronic | not counted | "History of hypertension" | no evaluation or treatment documented; answer note-1.q1
  EM-DATA: none | not counted | none | no test documented
  EM-RISK: table-moderate | counted | "Continue metformin 500 mg twice daily" | prescription drug management
  EM-RULE: ADR 0308 ruling 1
  EM-ANSWER: note-1.q1
  EM-ECG: not applicable
  EM-MDM: problems low; data straightforward; risk moderate; mdm low
  EM-LEVEL: 99213
```

A worksheet without the block still renders: its check-off shows the visible worksheet and the
E/M paragraph of the note instead. It is valid only for a run approved before the `em_audit` start
in `reference/completion-check-starts.tsv`; there a missing block, or a missing re-derivation, is
shown and not graded. For a run approved on or after that start, a missing block is a finding.
`tools/em_audit.py` reads the approval through `--submission`; without it, a run is judged current.

## The pre-approval answers record

`<run>/pre-approval-answers.json` holds every coding question icd10-cpt step 5 puts in the run's
pre-approval questions, whether or not the answer changes the level: the problems-addressed,
drug, directed-agent and threat-to-life questions, the documentation checks of the office check
sheet, and the ECG findings question. Record each answer when the clinician gives it:

```bash
python tools/preapproval_answers.py <run> --note <order> --question "<the question as shown>" --level <code> --level <code> --reply "<his whole reply>"
```

Pass one `--level` for each E/M level the question names, and none when it names none. The
command matches the reply as a whole clinician message after the run opened, as approval does,
and gives the entry its id, `note-<order>.q<n>`. An element block refers to it with
`EM-ANSWER: note-<order>.q<n>`. A delegated question records nothing; the lower level stands.
The command's complete boundary belongs to `preapproval_answers.DECLARED_LIMITS`.
