# A submission's voice-read records live under its key stem and one function names the directory

**Measured at:** fb7c9b93a59baed1477a5ada185213b07b7d17b8

[#1556](https://github.com/mshamblin5150-code/clinical-skills/issues/1556) was filed from the
after-action review of a `discussion-reply` run on 2026-10-04: the identity gate refused a capture
the voice grader would have read, and the run worked around it by writing the capture twice.
Grilled 2026-10-12 against `main`, where the freshness gate read `FRESH`; the clinician ruled all
three points below in that session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

**Three readers name the directory and two spellings answer.** `tools/voice_model_identity.py`'s
`write_record` requires `voice-reads/<submission>/supplied-voice.json` with the terminal key
verbatim, extension included. `tools/voice_read.py`'s completion gate and
`tools/reader_remarks.py`'s `voice_remarks` both read `voice-reads/<Path(key).stem>/`. So for any
key carrying an extension the identity gate and the grader disagree about where one file lives.
That is every `discussion-reply` key (`response-<name>.md`) and `peer-critique`'s `critique.md`, not
replies alone as the ticket body says.

**The written rule is split the same way.** `skills/_shared/reference/voice-read.md` states the
stem rule: the directory is the terminal `--submission` value with its file extension removed. The
five coursework skill files (`course-assignment`, `discussion-post`, `discussion-reply`,
`peer-critique`, `practicum-case-study`) and `skills/_shared/reference/sourcing.md` each write
`voice-reads/<submission-key>/supplied-voice.json`, which sides with the identity gate.

**Two stem rules exist in the tree.** `voice_read` and `reader_remarks` use `Path(key).stem`, which
strips any final dotted suffix. `coursework_run.draft_files` strips only `.md`, `.pptx` and `.docx`
and otherwise keeps the key verbatim. They agree on every key the coursework skills produce today.

**The workaround is on disk and has not drifted.** Across 164 registered checkouts, eight runs carry
a `voice-reads` directory: twelve subdirectories are named by stem and four by the full key. Each of
the four has a stem-named twin, and all four twin captures are byte-identical. Counts only; no file
under `scratch/` was opened beyond the byte comparison.

**The test suite encodes the bug.** `tools/test_predraft_order.py`'s `supplied` helper writes the
capture under the key verbatim and drives `voice_model_identity` with `critique.md`, so the suite
pins the full-key spelling the grader never reads.

## Ruling 1 — the key stem is the only directory name

Every coursework submission keeps its voice-read records in `voice-reads/<key stem>/`, where the key
stem is the terminal `--submission` value with a `.md`, `.pptx` or `.docx` extension removed and any
other key used verbatim. One function in `tools/coursework_run.py` computes that directory and is the
only place the rule lives; `voice_model_identity`, `voice_read`, `reader_remarks` and
`coursework_run.draft_files` all call it. The six prose surfaces write `<key-stem>`, matching
`voice-read.md`.

The full key everywhere was declined: it moves the grader, the protocol and the reader-remark lookup,
and all twelve existing stem-named records would regrade as a missing capture unless moved.
Accepting either spelling, refusing only when the two disagree, was declined because it keeps two
names alive for good and turns the drift the ticket is about into a graded condition rather than an
impossible one. The extension-limited stem is chosen over `Path.stem` because it is the rule
`draft_files` already applies and the one `voice-read.md` states, and a key with some other dot in it
then keeps its whole name rather than losing a fragment.

## Ruling 2 — no check watches for a full-key directory

No grader counts, reports or refuses a `voice-reads` subdirectory named by the full key. Once ruling
1 lands, no tool writes that name and none reads it, so a hand-made copy there cannot change any
grade; the two-copies drift the ticket feared needed both copies to be read.

A report-only count was declined as a line that almost always reads zero and obliges nobody to act.
A refusing finding was declined because it would stop a run, and fail a regrade of the four existing
runs, over a file nothing reads.

## Ruling 3 — the four existing full-key copies stay in place

The four full-key directories left by the 2026-10-04 workaround are expected leftovers and are not
moved or deleted. Each is byte-identical to its stem twin, they sit inside run directories rather
than at the scratch top level, so `scratch_census` never counts them, and disposing of anything under
`scratch/` is the clinician's word per file. Moving them into a holding directory inside each run
was declined as cleanup code for a one-time event that gains nothing.

## Build checklist

- `tools/coursework_run.py`: one public function returns `run / "voice-reads" / <key stem>` for one
  key, using the extension-limited stem; `draft_files` uses the same stem computation rather than its
  inline expression.
- `tools/voice_model_identity.py`: `write_record`'s capture check calls that function.
- `tools/voice_read.py`: both `Path(raw_key).stem` lookups in the completion gate and the surface
  mapping call it; `RECORDS_DIRECTORY` stays as the name the function joins.
- `tools/reader_remarks.py`: `voice_remarks` calls it in place of `Path(artifact).stem`.
- `tools/test_predraft_order.py`: the `supplied` helper writes under the stem directory, and the
  `critique.md` and `response-<name>.md` cases pass the identity gate with only that copy present.
  A full-key-only capture is refused by the identity gate.
- `tools/test_coursework_run.py` (or the nearest existing coursework test): the function maps
  `response-x.md`, `critique.md`, a `.pptx` and a `.docx` key to their stems and leaves an
  extensionless dated key verbatim.
- `skills/course-assignment/SKILL.md`, `skills/discussion-post/SKILL.md`,
  `skills/discussion-reply/SKILL.md`, `skills/peer-critique/SKILL.md`,
  `skills/practicum-case-study/SKILL.md` and `skills/_shared/reference/sourcing.md`:
  `voice-reads/<submission-key>/` becomes `voice-reads/<key-stem>/`, with the key-stem definition
  left to `voice-read.md` rather than restated.

## What this record does not reach

- **Other per-submission records.** Only the `voice-reads` directory is ruled. Records keyed by the
  submission elsewhere, such as the identity record's observations or the project-context go-ahead,
  keep their own keying.
- **Whether a stem collides.** Two terminal keys differing only by extension in one run would share
  a directory. No skill produces such a pair today, and none was measured for.
- **The contents of the leftover copies.** Ruling 3 rests on a byte comparison of the four captures;
  nothing else in those directories was compared.
