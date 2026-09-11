# A threshold root is always a path and a missing root is one that does not exist

[#1089](https://github.com/mshamblin5150-code/clinical-skills/issues/1089) was filed during
[#1078](https://github.com/mshamblin5150-code/clinical-skills/issues/1078)'s grilling
([ADR 0176](0176-a-gate-result-field-has-a-production-reader-or-it-is-a-local.md)): with no text
root, `gate_watermark` in `tools/threshold_sheet.py` prints
`WATERMARK       NOT RUN -- extracted corpus not found at None`, formatting a variable its own branch
has just established is `None`. The ticket asked which sentence replaces it, and whether one constant
should hold that sentence for watermark and extraction identity.

Grilled 2026-09-11 to an empty frontier. **Four rulings, by the clinician, on that date.** Nothing is
built here; this is the record the build reads. It extends
[ADR 0159](0159-the-sheet-grammar-leaves-as-a-pure-module-and-gate-results-split-per-gate.md)
ruling 4, which fixed `Roots(pdf_root, recs_root, text_root, recs_alias)` and said nothing about
whether a field may be `None`, and it answers the watermark wording ADR 0176 left to #1089.

## Measured before ruling, at `d096104`

Freshness gate `FRESH` at `d096104` before any reading and at `b9565ae` before recording;
`tools/threshold_sheet.py`, `tools/guidelines_recs.py` and `tools/test_threshold_sheet.py` did not
change between the two.

**The command never prints the line the ticket was filed over.**
`python tools/threshold_sheet.py reference/thresholds/diabetes.md --pdf-root C:/nowhere-1089-src`,
run with `CLINICAL_GUIDELINES_TEXT` unset and no `--text-root`, printed
`EXTRACTION IDENTITY NOT RUN -- extracted corpus not found at C:\nowhere-1089-text` and the same reason
on watermark's line. `text_root_for` derives a root from `--pdf-root` whenever none is given, and
`guidelines_extract.default_output` always returns a path. *Had the command been able to reach the
empty branch, that run would have printed `at None`; it printed a derived path.* So the ticket's
sentence that a person running the command without `--quiet` reads the line is false as filed. The
line reaches only a caller that builds `Roots` in process, which is how #1078's grilling found it.

**No production constructor produces an empty root, for any of the four fields.** `Roots` is built in
production only in `threshold_sheet.main`, from argparse values that are paths, and in
`Roots.defaults()`, which `threshold_draft` also uses. An empty-string argument becomes `Path(".")`,
not `None`. Every call passing `None` for a root is in `tools/test_threshold_sheet.py`, most of them
through the defaults of its `survey_inputs` and `grade` helpers.

**Three messages format the empty value into prose**, each after a `None` check: watermark's
`extracted corpus not found at None`, citation tier 2's `source PDFs not found at None`, and
`guidelines_recs.locate_recommendation_record`'s `no sweep alias at None`. Watermark's empty branch
also emits the diagnostic `WATERMARK       1 manifest problem(s)` though no manifest was read.

**An empty `recs_root` is a separate state, and the tests pin an exit status the command cannot
produce.** In process, an empty root gives a source no lookup path, so `bind_recs` records
`no --recs given for this source, so omission was not checked`, the source is not counted as a missing
record, `gate_coverage` treats it as blocking, and the run exits 2. From the command, `diabetes.md`
with no `--recs`, a missing `--recs-root` and a missing `--recs-alias` printed
`no recommendation record at C:\nowhere-1089-recs\recs-ada-2026.json` and
`The missing recommendation record(s) above are a warning, not a clean COVERAGE pass.`, and exited 0.
*Had that run reached the blocking state, it would have printed the omission-not-checked paragraph and
exited 2; it printed the warning and exited 0.* `test_no_recs_at_all_is_also_2`,
`test_no_recs_at_all_does_not_print_a_zero_count_either` and
`test_no_argument_and_no_root_says_none_was_given` are named for the command's situation and pass on
the in-process one.

## Ruling 1. Every `Roots` field is a `Path`

`pdf_root`, `recs_root`, `text_root` and `recs_alias` are typed `Path`. **A missing root is a path that
does not exist**, and every gate already reports that case with the path it looked at.

The empty-root branches are deleted: watermark's, with its manifest-problem diagnostic; `survey`'s
`no --text-root was available` fallback for extraction identity; citation tier 2's `None` check; and
`locate_recommendation_record`'s `None` checks on both the sweep alias and the recs root, together
with the `no automatic recommendation-record root` wording and the `bind_recs` branch that writes
`no --recs given for this source`. A function whose parameter is typed `Path | None` only to carry one
of these fields takes `Path`.

**Keeping the empty state for in-process callers and rewording it is declined.** A sentence naming no
flag, held in one constant, would describe a state no production caller produces, and the
manifest-problem diagnostic would still need its own repair.

**The ticket's two candidate sentences are declined.** Both name a command-line route, `--text-root`
or `CLINICAL_GUIDELINES_TEXT`, for a state the command line cannot reach.

**Narrowing the ruling to `text_root`, or filing `recs_root` apart, is declined.** A `Roots` with one
required field and three optional ones is not a coherent seam, and `recs_root` is the field where
leaving the state in place keeps the suite asserting command behavior this record measured as false.

## Ruling 2. `Roots` refuses a non-path when it is built

`Roots.__post_init__` raises `ValueError` naming the field when its value is not a `Path`, on
`guidelines_recs.Marker.__post_init__`'s precedent, and the message says a missing root is passed as a
path that does not exist. One test drives each field. The gates keep no `None` check of their own, and
the `Roots` docstring points at this record rather than restating it.

**Annotations alone are declined.** A `None` would fail at its first use, as an `AttributeError`
inside a gate or a `TypeError` from `Path(None)`, naming neither the field nor the rule, and the
in-process caller is exactly who meets it.

**A check in each gate is declined.** That is three copies of one rule, and the rule is about the
shared inputs rather than about any gate.

## Ruling 3. The tests follow the command

The test helpers that default a root to `None` default it to a temporary directory that does not
exist.

- `test_no_recs_at_all_is_also_2` and `test_no_argument_and_no_root_says_none_was_given` are deleted.
  The state they pin no longer exists, and
  `test_a_record_never_built_under_the_lookup_root_warns_and_exits_0` already pins what the command
  does with no `--recs`.
- `test_the_lookup_never_falls_back_to_the_sheet_directory` loses its empty-root limb and keeps its
  empty-real-root limb, which its own docstring names as the one that discriminates.
- `test_no_recs_at_all_does_not_print_a_zero_count_either` is driven with an empty real root, because
  a warning-only `COVERAGE NOT RUN` must not print `0 refusing` either.
- `test_a_missing_recs_file_says_so_by_name` keeps its assertion, and its docstring stops describing a
  run that never meant to check omission.
- A call that passed `None` only for convenience takes the helper's new default.

A new test drives a missing text root through `survey` and asserts that watermark and extraction
identity both print the reason `guidelines_manifest.read` writes for it.

## Ruling 4. The ticket's two decisions are answered by the removal

With the empty state gone, watermark and extraction identity report a missing text root with the
sentence `tools/guidelines_manifest.py` already owns, `extracted corpus not found at <path>`. There is
no second sentence to choose between, and no constant to hold one.

**A shared constant is declined.** It would be a second owner for a sentence that already has one.

## What the build verifies

- `python tools/threshold_sheet.py --all` and `--all --quiet` produce byte-identical output and the
  same exit status before and after, against the committed sheets. That is a no-change check on the
  command, and it cannot see the in-process branches this build removes.
- The two driven command runs above produce the same bytes and exit status before and after. *Had the
  build changed what the command reports for a missing root, those bytes would differ.*
- Building `Roots` with `None` in any field raises `ValueError` naming that field.
- The suite, run through `python tools/suite.py`, is green.

## What this record does not settle

**Which lines survive `--quiet`** is
[#986](https://github.com/mshamblin5150-code/clinical-skills/issues/986)'s question and is not moved.

**How the command derives a text root** is unchanged: `text_root_for` still falls back to
`guidelines_extract.default_output` over `--pdf-root`.

**Extraction identity's own fallback reason**, used when a handoff yields neither an identity nor a
problem, is not an empty-root branch and is untouched.

**Whether other command input objects in `tools/` carry optional fields that no production path leaves
empty.** Only `threshold_sheet.Roots` and the functions it feeds were measured.
