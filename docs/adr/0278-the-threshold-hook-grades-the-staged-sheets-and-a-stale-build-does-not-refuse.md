# The threshold hook grades the staged sheets and a stale build does not refuse

**Measured at:** fffeccc58fd22afe7bb2505844e98a5970ff7ff6

[#1198](https://github.com/mshamblin5150-code/clinical-skills/issues/1198) measured the threshold
gate at roughly 100 seconds on every commit touching one sheet and left three questions to settle
before building. Grilled 2026-09-30 against `main`, where the freshness gate read `FRESH`; the
clinician ruled every point below in that session and widened the ticket to carry ruling 4.
**Nothing is built here; this is the record the build reads.**

## Measured before ruling

Every figure below was taken on the maintainer's machine with the guideline corpus present, over
the 169 clinical sheets under `reference/thresholds/`. They are dated readings of one machine and
are stated here once.

**No gate compares two sheets.** `threshold_sheet.survey` takes one sheet path and the run's shared
inputs, and `main` calls it once per sheet. The conflict rule inside `gate_schema` groups
`sheet.rows` by quantity and population, so it compares rows of one sheet; its docstring says it
*"Needs nothing but the sheet"*. The hook comment's reason for `--all`, *"a sheet's conflict rule is
a statement about the whole directory, and grading one file in isolation would miss a disagreement
introduced between two of them"*, is therefore false of the code, and
[ADR 0076](0076-the-cross-sheet-reading-is-a-substantiated-row-and-the-reader-derives-the-join-per-patient.md)
had already assigned the cross-sheet reading to a reader rather than to a gate.

**One sheet costs seconds.** `python tools/threshold_sheet.py --all --quiet` took 1m46.7s of wall
time. Twelve sheets run one at a time through the same command took between 0.6 and 2.2 seconds
each, and `hypertension.md` took 3.8.

**Where the full run's time goes**, from one `cProfile` run of `main(['--all', '--quiet'])`, 121.8
seconds under the profiler. The rows overlap where one function calls another, so they do not sum.

| Function | Calls | Cumulative seconds |
| --- | ---: | ---: |
| `gate_citation_tier2`, opening the source PDFs | 169 | 83.9 |
| `artifact_provenance.check_producer` | 350 | 32.8 |
| `subprocess.run`, every one a `git` call under that check | 1,051 | 32.3 |
| `guidelines_manifest.read` | 169 | 16.8 |

So the ticket's second question is answered: the provenance question is asked of `git` once per
sheet and per record although its answer cannot change within a run, and
[#871](https://github.com/mshamblin5150-code/clinical-skills/issues/871)'s repair does not reach
this path.

**The gate exits 2 today, for one sheet or for all of them.** The extracted text and the
recommendation records on disk were produced at `fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56`, dated
2026-08-30, and `tools/guidelines_extract.py`, `tools/guidelines_recs.py` and `tools/page_text.py`
have changed since. `gate_coverage` sets `not_graded` for an untrusted record, `survey` turns that
into status 2, and the hook turns any non-zero status into a refusal. A record that is *missing* is
already a warning and does not reach status 2; the grilling described both as refusing, and only
the untrusted one does.

**What can flip a sheet nobody staged.** `survey` reads the catalog's page counts and source
classes, so a catalog edit can. The source PDFs and the recommendation records can, and they live
outside the repository, so no commit carries that change. `gate_edition_currency` cannot: its
docstring says it never enforces the registry verdict. A catalog-only commit runs
`threshold_coverage.py` today and not this gate.

## Ruling 1 — the hook grades the staged sheets and no others

When a clinical sheet is staged, the pre-commit hook grades each staged sheet and nothing else.
The verdict for those sheets is the one `--all` gives them, because no gate reads a second sheet.
The hook comment is corrected to say so.

Keeping `--all` with the repeated work removed was refused. It leaves more than a minute on every
sheet commit, because reading the PDFs is most of the time, and the hook's own design constraint is
that this check must not become the one people learn to skip. What the full run gave an untouched
sheet was incidental: none of the events that can flip one triggers this hook.

## Ruling 2 — the events that can flip an untouched sheet run the full gate

A staged `reference/guidelines-catalog.md` runs the full gate over every sheet in the hook.
`tools/guidelines_build.py` runs the full gate when its build finishes and prints the report; that
run is report-only and leaves the build command's own exit status alone.

A documented manual step was refused as an instruction that cannot fail. A catalog trigger alone was
refused because a corpus refresh is the one event that can invalidate a page citation, and it
produces no commit. Continuous integration is unchanged and still runs every sheet at each merge
without the PDFs.

## Ruling 3 — the repeated work is removed and no cache is added

The provenance check and the manifest read happen once per run rather than once per sheet. No
verdict moves. Nothing here reads or writes the build cache, so
[ADR 0049](0049-the-sweep-alias-and-the-recs-root-are-two-lookup-roots-with-two-resolution-rules-and-the-producer-guarantees-the-prefix-it-writes.md)
is untouched and the ticket's third question does not arise.

## Ruling 4 — a stale build does not refuse a commit, and a sheet the gate could not read still does

A build artifact outside the repository that is untrusted because its producer code has moved is a
property of the machine. In the hook it prints its `NOT RUN` lines and does not refuse. The remedy
is a rebuild that ADR 0049 measured at 56 minutes, and refusing on it is a stronger pressure to skip
the check than the 100 seconds the ticket was filed over.

A state whose remedy is an edit to a committed file still refuses: a sheet that cannot be parsed, a
sheet declaring no source, and a scope table whose pages cannot be reconciled with the catalog. The
build classifies every remaining route to status 2 by that test, and a route it cannot show to be
machine state keeps refusing.

Letting every did-not-run state through was refused: an unparseable sheet would commit with nothing
checked. The price of the ruling is named: while the build is stale, a citation only the
record-backed gates would catch can be committed, and the printed lines are the only notice.

## Ruling 5 — the command keeps exit 2 and the hook converts it with a flag

`threshold_sheet.py` keeps returning 2 for ruling 4's machine state. The hook passes a flag that
converts that state to a pass, and the flag suppresses no line of the report. Both hook invocations
pass it, the staged-sheet run and ruling 2's catalog run. This is `phi_scan.py`'s
`--allow-no-corpus` arrangement for its reason.

Returning 0 from the command itself was refused. Continuous integration would show a passing check
over a run whose record-backed gates never ran, a manual run on a stale machine would report
success, and this would become the one grader whose 0 does not mean everything ran.

## What this record does not settle

**Which gates a stale artifact really invalidates.** Ruling 4 passes the whole stale state. A
narrower rule that refuses only for the gates reading the stale artifact was offered and not taken;
it needs a per-gate map nobody has measured.

**Figures after the build.** The share of the run that ruling 3 removes is a prediction from one
profile and is not stated as a result.
