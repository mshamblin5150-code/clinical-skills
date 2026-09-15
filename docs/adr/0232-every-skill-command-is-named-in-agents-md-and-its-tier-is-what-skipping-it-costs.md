# Every skill command is named in AGENTS.md and its tier is what skipping it costs

[#1130](https://github.com/mshamblin5150-code/clinical-skills/issues/1130) was filed out of
[#927](https://github.com/mshamblin5150-code/clinical-skills/issues/927)'s grilling: nine modules a
skill file tells a consumer to run are named nowhere in `AGENTS.md`. Grilled 2026-09-14 at
`origin/main` `9770b1a0`; freshness gate `FRESH`. The clinician ruled every point below, one at a
time, on that date. Nothing is built here; this is the record the build reads.

**The line anchors are dated, not durable**: the build this record orders moves the lines it cites,
so a builder resolves each coordinate by the quoted text or symbol named beside it.

## Measured before ruling

### The nine reproduce

`python tools/python_floor.py` at `9770b1a0` exits 0 and prints `skill-command roots undeclared in
AGENTS.md=9`: `aar_scan`, `case_study_scan`, `docx_read`, `docx_word_probe`, `docx_write`,
`guidelines_search`, `name_index`, `peer_critique_scan`, `voice_model_scan`. Its population is every
literal `python tools/X.py` in a `.md` or `.json` file under `skills/` (`python_floor.SKILL_COMMAND`),
against every `tools/` module named anywhere in `AGENTS.md`. *Had any of the nine been named in
`AGENTS.md`, it would have been absent from that list.*

### `AGENTS.md` does not sort its own tools by its own test

The optional paragraph (`AGENTS.md` line 44, *"Skip every one of those and the skill still works"*)
lists `tools/checks_ledger.py`, `tools/reference_scan.py` and `tools/research_ledger.py` for
`practicum-case-study`, and `tools/filled_vitals_census.py`, `tools/differential_scan.py` and
`tools/specificity_scan.py` for the note skills. Every one of them is a clean exit its skill
requires:

- `practicum-case-study`'s completion list asks whether `reference_scan.py` and `checks_ledger.py`
  exit 0, and its step 3 grader handoff *"must report the ledger clean before drafting starts."*
- `aar_scan.COMPLETION_GRADERS` pairs `batch-shift` with `filled_vitals_census`, `clinical-note`
  with `differential_scan`, `icd10-cpt` with `specificity_scan` and `practicum-case-study` with
  `checks_ledger`; each of those skills requires the `--submission` run to exit 0 with
  `the after-action review: clean`, and `batch-shift` says *"the shift is not complete without it."*

Meanwhile `discussion_reply_scan.py` and `discussion_post_scan.py`, whose every row is also written
out for a by-eye walk, are declared as tools their skills *depend on*. Two tools of one shape sat in
opposite groups.

### The completion requirement predates ADR 0181 ruling 15

`git log -S 'the after-action review: clean' -- skills/batch-shift/SKILL.md` returns `3936ee12`,
2026-09-02 (#814). ADR 0181's first commit is `d3cf077a`, 2026-09-11. Ruling 15's *"`batch-shift` is
not moved into the depends-on-a-tool group, because the notes are still written without it"* was
therefore written while the shift's completion exit was already required. *Had the requirement
arrived after ruling 15, the first command would have returned a later date than the second.*

### Where each of the nine is invoked

- `aar_scan.py`: `skills/aar/SKILL.md`, the extract and the grade; *"Return to the invoking skill's
  completion grader only after exit 0."*
- `peer_critique_scan.py`: `peer-critique` step 5's grader handoff and its completion grader.
  `peer-critique` is tabled in `AGENTS.md` and has no tool paragraph.
- `voice_model_scan.py`: `peer-critique` and `discussion-reply` (*"Exit 0 is required to draft
  against the model"*) and `setup-clinical-skills` (*"Exit 0 is required"*).
- `case_study_scan.py`: `practicum-case-study` step 9's house-style grader handoff.
- `docx_write.py`: `practicum-case-study` step 8 renders the submitted `.docx`; `discussion-post`
  step 7 renders the archival `.docx`.
- `docx_read.py`: `practicum-case-study` step 3 (`--normalize` on the evidence paste, *"not
  optional on an UpToDate paste"*), the faculty document read, and step 9's `--numbering` readback
  given to the numbering reader; `skills/_shared/reference/voice.md` §3 for a writing sample.
- `name_index.py`: `batch-shift` step 3, report and `--write`; nothing requires its exit.
- `guidelines_search.py`: `skills/_shared/reference/rubric.md`, against an index built outside every
  checkout from a corpus no consumer has.
- `docx_word_probe.py`: `skills/_shared/reference/apa7.md` §6 (*"the maintainer-only command"*) and
  the `"command"` field of `skills/_shared/reference/word-renderer-calibration.json`. No module in
  `tools/` reads or writes that field, and no test pins its value.

### A printed count repaired nothing

#1130 carries seven sweep comments dated 2026-09-12 through 2026-09-14. Each re-ran the floor walk,
confirmed a named module was still undeclared, and changed nothing.

## Ruled 2026-09-14

### 1. The tier is what skipping the command costs

A skill **depends on** a command when skipping it changes what the run can claim: the skill requires
its clean exit, it produces the deliverable, or it produces the readback a required check reads. A
command whose skipping changes nothing the run claims, because it only saves reading by eye or
records where a figure came from, is **named**. A command whose skipping costs the PHI check's
coverage rather than the run's claim is declared with that cost beside it, as `day_file_text.py`
already is. Line 44's *"skip every one of those and the skill still works"* is rewritten to this test,
and `practicum-case-study`'s three sentences that `AGENTS.md` *"keeps the two classes of tool
citation apart deliberately"* are rewritten with it.

### 2. Five of the nine are depends-on

`aar_scan.py` (`aar`), `peer_critique_scan.py` (`peer-critique`), `voice_model_scan.py`
(`peer-critique`, `discussion-reply`, `setup-clinical-skills`), `case_study_scan.py`
(`practicum-case-study`) and `docx_write.py` (`practicum-case-study`, `discussion-post`). Each
declaration says what skipping costs in the file's existing words: a reader walks the rows by eye
after the install has been tried and cannot call the run mechanically verified; for `docx_write.py`,
written *to produce* as `case_study_render.py` is, there is no document; for `voice_model_scan.py`,
the draft is not written against the model. `peer-critique`'s paragraph is created by this, so the
ticket's decision 2 was an oversight rather than a separate defect.

### 3. The test reaches the tools already in the optional paragraph

`research_ledger.py`, `reference_scan.py` and `checks_ledger.py` are depends-on for
`practicum-case-study`; `filled_vitals_census.py` for `batch-shift`, `differential_scan.py` for
`clinical-note` and `specificity_scan.py` for `icd10-cpt`. A tool keeps its named citation where a
different skill cites it without requiring its exit. This supersedes the final sentence of
[ADR 0181](0181-a-day-file-reaches-the-corpus-through-one-command-and-a-rendered-page-waits-for-a-reading.md)
ruling 15 and only that sentence: it asked whether the notes are written, while the skill says the
run is not complete. The `day_file_text.py` clause stands word for word.

### 4. `name_index.py` is declared by its firewall cost

Beside the `day_file_text.py` clause: `batch-shift` step 3 runs `python tools/name_index.py --write`,
and skipping it leaves that shift's patient names out of the PHI name check. `batch-shift`'s exit
rules do not change, which keeps the 2026-08-19 ruling that a short index is declared and never
enforced.

### 5. `docx_read.py` is depends-on for `practicum-case-study` only

The cost clause names both limbs: without `--normalize` a search of the evidence misses words the
page contains and reads as a settled negative, and without `--numbering` the numbering check has no
readback. The `voice.md` writing-sample read stays a named citation.

### 6. `guidelines_search.py` is named, with its index clause

It needs a guideline index built locally outside the repository; without one the command reports it
did not search, and `reference/guidelines-catalog.md` remains the committed way to find a document.

### 7. `docx_word_probe.py` stops being a skill command

`apa7.md` names the module as a maintainer instrument and points at `CLAUDE.md`'s *Word documents,
both directions* section and [ADR 0008](0008-word-is-a-one-time-calibration-instrument.md) for its
command; the calibration JSON's `"command"` field records `tools/docx_word_probe.py --word`.
`AGENTS.md` does not name it, on `CLAUDE.md`'s rule that maintainer tooling is not cited there.

### 8. A suite test refuses an unnamed skill command

A test separate from the floor walk reuses `python_floor.py`'s skill-command population and fails
when a module in it is named nowhere in `AGENTS.md`. Any tier satisfies it; choosing the tier stays a
person's reading. It runs in the suite and CI, with no pre-commit gate, and its failure names both
remedies: name the command, or stop handing consumers a command they must not run. ADR 0187
ruling 11's printed count and the walk's exit status are unchanged.

## Consequences

`AGENTS.md` gains paragraphs for `aar`, `peer-critique` and the three note skills, widens the
`practicum-case-study`, `discussion-post`, `discussion-reply` and `setup-clinical-skills`
declarations, adds the `name_index.py` clause beside `day_file_text.py`, and keeps an optional
paragraph holding only citations that pass ruling 1's named test. After the build,
`python tools/python_floor.py` prints `skill-command roots undeclared in AGENTS.md=0`.

Test comments that say `AGENTS.md` classes a tool as one a skill names move with the tool:
`tools/test_research_ledger.py`, `tools/test_checks_ledger.py`, `tools/test_reference_scan.py` and
`tools/test_case_study_scan.py` each carry one. A builder searches `tools/` and `CLAUDE.md` for the
old two-class wording rather than trusting this list.

[ADR 0187](0187-the-python-floor-is-two-numbers-held-equal-and-a-job-on-the-floor-settles-it.md)
ruling 3's premise that declaring every invocation *"would legislate that distinction away"* no
longer holds once any tier satisfies a declaration; a dated correction there names this record.

## Not superseded

- **ADR 0187 ruling 3's population** stays every module a skill file invokes, closed over imports,
  and the floor still ignores tiers.
- **ADR 0187 ruling 11** stays: the count prints on every run and the walk never grades it.
- **ADR 0181 ruling 15's clause** naming `day_file_text.py` and its firewall cost stays.
- **The 2026-08-19 ruling that a short name index is declared and never enforced** stays.

## Rejected options

- **Keeping line 44's words as the test.** It already placed required completion graders in the
  optional paragraph, and sorting nine more on it copies that nine times.
- **A third group between depends-on and named.** It relabels paragraphs without changing what a
  consumer learns.
- **Scoping ruling 1 to coursework skills.** It leaves one file with two tests.
- **Holding ruling 15's sentence for `batch-shift` alone.** Its premise was about output, not
  completion, for all three note skills alike.
- **Requiring `name_index.py`'s exit.** It would reverse the declared-never-enforced ruling through a
  side door.
- **Declaring `docx_read.py` everywhere it is invoked.** The voice-sample read is ordinary reading.
- **Removing `guidelines_search.py`'s command from `rubric.md`.** It deletes a working step from the
  one machine that has the index, to shrink a count.
- **Declaring `docx_word_probe.py` in `AGENTS.md`, or leaving it as a standing exception.** The first
  breaks the maintainer-tooling boundary; the second keeps a command a consumer must never run in
  consumer material.
- **A ratchet on the count.** With no exception left after ruling 7, it is ruling 8 plus a hatch
  around a question that already has an answer.
- **Nothing beyond the printed count.** Seven sweep comments show it does not repair the gap.

## What this does not reach

**Whether a tier is right.** Ruling 8 grades that a command is named, never where. A command filed in
the wrong group passes.

**A command a skill tells a reader to run without the literal `python tools/X.py` shape.** It is
outside `python_floor.SKILL_COMMAND`'s population and so outside ruling 8's.

## What must not come out of this

**A test that grades the tier.** That is the reading ADR 0181 ruling 15 and ADR 0187 ruling 3 kept
for a person, and nothing ruled here moves it to a machine.

**A change to the floor walk's grading.** Ruling 8's test reuses its population and leaves its report
and exit status alone.
