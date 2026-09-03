# A member's obligations outside the graded path stay in main and the crash posture gains a finding sibling

Found while grilling [#840](https://github.com/mshamblin5150-code/clinical-skills/issues/840) and
[#842](https://github.com/mshamblin5150-code/clinical-skills/issues/842), 2026-09-03. Opened at
`origin/main` `6cd340a`; `main` moved mid-session when
[#839](https://github.com/mshamblin5150-code/clinical-skills/issues/839) and
[#843](https://github.com/mshamblin5150-code/clinical-skills/issues/843) landed as one commit, and
every figure below was re-derived at `3af546c` before ruling. Freshness gate `FRESH` at both
checkpoints. **Ruled by the clinician on that date.** Nothing is built here; this is the record the
build reads. [ADR 0118](0118-the-conformance-kit-shapes-a-migrating-grader-s-value-and-vocabulary-and-the-fixture-row-is-the-finding-kind.md)
is the other half of the same session and carries the thesis both records share.

## Measured before ruling

Every figure was re-derived by running the code rather than by reading it, and three of them
disagree with the ticket that prompted the grilling.

**`aar_scan.main` is called by no test.** `consume_orphans` appears at exactly two sites in `tools/`
— its definition and its one call — and `test_aar_scan.py` exercises `write_extract`, `survey`,
`session_end` and the hook registration, never the command. **#840's `Done when` asks for stdout
byte-identical before and after; there is no baseline to be identical to.**

**#840's decision 2 does not force its decision 1.** The ticket holds that a hook entry point and a
run grader in one file is *what forces decision 1's awkwardness*. `--session-end` needs a branch
**before** delegation; `consume_orphans` needs a side effect **after** it. Splitting the hook out
leaves the drain exactly where it was.

**The byte-identical bar is unachievable as written**, and two of the four movements are forced by
the conformance kit rather than chosen. Measured against `fixtures/filled-anchor/run-2`:

| invocation | today | after migration | forced by |
| --- | --- | --- | --- |
| `<run> --submission k --shwo` | 1, graded | 2, `unrecognized option` | `for_module`'s unrecognized-flag test |
| `<run> --submission --show` | 1, submission is the string `--show` | 2 | `Option(takes_value=True)` refusing a `-`-leading value |
| `--show <run> --submission k` | 2, usage | graded | the shared parser accepts flags in any position |
| `--extract`, bad run directory **and** no `--memory-index` | the directory complaint | the `--memory-index` complaint | `validate` runs inside `parse`, ahead of `load` |

Row 2 is today's behavior being a defect: the command currently grades a submission whose key is
the literal string `--show`.

**Three of fourteen members declare an exit-2 vocabulary** — `differential_scan`, `render_scan`,
`voice_model_scan`. The other eleven, including the freshly migrated `refusal_scan`, declare none.

**`aar_scan` is not the axis-1 crash residue, and the classifier that says so is not a crash
detector.** [ADR 0116](0116-the-read-failure-posture-is-keyed-on-the-input-s-role-and-only-the-crash-is-ruled-family-wide.md)
ruling 3 closes on *`aar_scan` is the whole residue*; ruling 4's map, now on `main` as
`run_grader.UNDECODABLE_BYTE_POSTURES`, files it under `crash` with the reason *an unhandled strict
baseline read remains deferred to #840*. Driven with injected failures at `3af546c` rather than read:

| path | undecodable byte | `open()` refused | write fails |
| --- | --- | --- | --- |
| graded (`survey`) | finding, **1** | finding, **1** | -- |
| `--extract` | **2** | **2** | **2** |
| `--session-end` | **2** | **2** | -- |

Every decoding read carries `errors="replace"` except two. Both — `_read_pointer` and `_baseline` —
sit inside `except (OSError, UnicodeError, json.JSONDecodeError)` and convert to `ValueError`, which
`survey` turns into `Finding("unscannable-review")` and `Finding("bad-orphan-pointer")`. **That is
the posture ADR 0116 ruling 3 permits by name.** `run_grader._converts_read_failure` credits a
handler only when it catches `OSError` **and** `UnicodeError` **and raises `SourceError`**, so a
conversion into a finding counts as crashing. **`TEXT_READ_WALK_CEILING` does not disclose that
requirement**: it names which read calls are invisible and says nothing about what it demands of a
handler.

**The row names one read and the walk finds two.** `walk_text_reads` over `aar_scan.py` returns
`total=5, replacing=3, refusing=0, crashing=2`; the row's reason names the baseline read alone.

**This is the third false classification from that instrument.** ADR 0116 records the first two
inside its own measurement and made the matcher's acceptance conditional on being fed a
partial-match mutant and driven red. `aar_scan` is that mutant, and it was classified rather than
caught.

## Ruled 2026-09-03

### 1. A post-report side effect lives in `main` after delegation, and the shared frame gains nothing

`consume_orphans` runs after the report and before the status, which the runner has no hook for.
Four homes were priced. A mutation inside `grade()` is one line and costs the name: `grade` reads as
a pure survey in every other member, and **no member constructs a `Finding` inside its grade
function** — fourteen of fourteen, measured. A new `Grader` or `Grade` field is the frame change
[ADR 0113](0113-the-per-grader-report-frame-is-affirmed-a-second-time-and-the-shared-report-value-is-declined-on-measurement.md)
says needs its own argument, and #840's own *What must not come out of this* forbids it arriving
quietly. Taking it off the command path abandons the drain.

**So `main` wraps the delegation**, calling `consume_orphans` when `run_grader.run` returned 0 and
the invocation was not `--extract`. It costs one re-parse of an argv the first parse accepted, which
cannot raise; re-deriving the positional by hand instead would be the copied-policy shape
[#839](https://github.com/mshamblin5150-code/clinical-skills/issues/839) exists to delete.
`grader_conformance.for_module`'s delegation check is a substring of `main`'s source, which a
statement below the call satisfies.

**The ordering is the deciding argument and it is about which failure is recoverable.** Under a
mutation in `grade`, a crash between the unlink and the print loses the orphan pointer *and* the
evidence that anything drained. Under today's order and under this ruling, the same crash loses only
the unlink, and the next run redoes it. That the report bytes are identical either way is true and
is not the reason.

### 2. The second entry point stays in the module

Routing `--session-end` through the runner is not available: `parse` raises `ParseError` on
`if not positionals` before `load` and before `validate`, and the mode has no positional — it reads
a JSON payload from stdin. Named as refused rather than left to be rediscovered.

**Splitting it out was refused on [ADR 0112](0112-the-grader-membership-ratchet-grades-adoption-rather-than-source-shape-and-not-members-distinguishes-refused-from-deferred.md).**
That record grades membership on **adoption** rather than on source shape, and a second entry point
is source shape. A new module would import `aar_scan` back for `survey`, `read_review`,
`orphan_paths` and `_safe_submission`, so the coupling does not go away — it becomes two files
holding one mechanism, with a `.claude/settings.json` edit and a new test module besides. Six
graders import `aar_scan` today and none imports `session_end`, so no importer blocks either answer;
the choice is made on the ruling and not on the graph.

**The branch keeps its exact test** — `arguments == ["--session-end"]` — because that is today's
guard and widening it is a change nobody asked for.

**A consequence is recorded rather than left to be found.** `test_console_codec.py` skips the
direct-call check for a module where `delegates_to_run_grader` is true, because `run_grader.run`
owns `use_utf8` for its members. The hook branch returns **before** `run_grader.run` is reached, so
nothing in the runner covers it and the `use_utf8()` call stays in the `__main__` guard. That makes
`aar_scan` the first module in this tree that is a runner member **and** a direct command at once.

### 3. `aar_scan` declares no exit-2 vocabulary, because its surface is not wholly inside the runner

Ruling 2 keeps two exit-2 routes outside `run_grader.run` — a payload that is not a `SessionEnd`
event, and a `transcript_path` or `session_id` that is not a string. A declared vocabulary would
enumerate *every way of not having scanned* while missing both, and its docstring would have to say
so. **That is the partial instrument reading as complete**, which this repository refuses on the
extractor-coverage rule.

**And there is no prose enumeration here to harden.** `CLAUDE.md`'s `aar_scan` section states only
that 0 is clean, 1 is a review finding and 2 means no population was scanned, so declaring would
create a claim rather than hold one. The reason is recorded in the module, because the next reader
will compare against `render_scan` and read the omission as an oversight.

**The coherent form of *yes* is ruling 2 reversed**, splitting the hook so the surface is wholly
inside the runner. That trade was priced and refused above.

### 4. The migration characterizes first, and the bar is restated rather than met

Two commits. The first adds command-level tests pinning today's `main` for every mode; the second
migrates, and the pins that move are the diff's own before-and-after. **Migrating first and pinning
after would pin the new behavior**, so nothing would ever have measured the old, and the two
unforced movements in the table above are exactly the class that ships unnoticed.

The `Done when` bar becomes: the graded report and its status are byte-identical, and the four
invocation-shape movements are declared changes rather than regressions. `NOT_MEMBERS` no longer
exists; the move is `run_grader.DEFERRED` to `MEMBERS`.

**The declaration splits one message into two and that is an improvement rather than a loss.**
`run directory and --submission are required` names both when only one is wrong. Under the runner
`--submission` is an invocation-shape requirement and belongs in `validate`, while the directory
existing is a source question and belongs in `load` raising `SourceError`. `source_error_to_stdout`
stays `False` and `allow_extra_positionals` stays `True`, both preserving measured behavior rather
than choosing.

`--extract` becomes an `EarlyExit`, which `run_grader`'s own docstring names as *a declared
non-grader mode*.

### 5. `aar_scan` is not a crasher; the posture map gains a `finding` key and the walk discloses its requirement

The measurement above stands and the row must move, because the row's own reason says *remains
deferred to #840* and that sentence is false on `main` the day the deferral clears. Leaving it is
therefore not available.

**Two of the three ways to move it are worse than the row.** Adding `errors="replace"` to the two
strict reads drops `crashing` to 0 and moves the row to `grade` — and it introduces a silent pass.
`b'{"MEMORY.md": "a3f\xffc"}'` decoded strictly raises; decoded with replacement it **parses**,
yielding a hash carrying U+FFFD. `_target_changed` is `_hash(path) is not None and _hash(path) !=
baseline.get(str(path))`, so a corrupted baseline never matches, the target reads as changed, and
`Finding("unlanded-memory")` is never raised. **That trades a finding for a false pass on the one
file whose job is proving a correction landed.** Converting the handlers to raise `SourceError`
contradicts the row's own second clause, and does not even work: `run` catches `SourceError` around
`load` only, so one raised from `grade` is uncaught and exits 1, rebuilding the defect.

**So the map gains a fifth key, `finding`**, for a module that grades an undecodable byte by
converting it into a finding rather than by replacement — which ADR 0116 ruling 3 permits
explicitly. Ruling 4 specified the map as *at least* three-valued, so this uses the object as
designed. `TEXT_READ_WALK_CEILING` gains the `SourceError` requirement it presently omits; that is a
disclosure correction and stands on its own. `crash` survives as an empty mapping on
[ADR 0112](0112-the-grader-membership-ratchet-grades-adoption-rather-than-source-shape-and-not-members-distinguishes-refused-from-deferred.md)'s
reasoning for `DEFERRED`: the posture is real and the next module to hold it should not re-argue the
key.

**#840 carries this rather than a separate ticket.** #843 is closed, the row names #840 by number,
and the alternative that keeps the map untouched is the one measured above as introducing a false
pass. **The seam objection is aimed at the wrong part**: what ADR 0116 ruling 5 refused was adopting
a *mechanism* across fourteen modules with no argument, and this adds one key to a declaration
specified as open-ended plus a ceiling correction. The ticket names both subjects rather than
blending them.

**The builder re-derives before writing the new reason.** These figures were taken twice, at
`6cd340a` and again at `3af546c`, and a figure a session reports is a claim rather than a fact —
which is the rule that caught the row.

### 6. `session_end` is not a reader in the grader family, and the family's exit vocabulary does not reach it

**Ruled 2026-09-03, after `8d1b2ee` merged this record with the question standing under *What this
does not reach*.** It was left open there because #843 closed without asking it; the clinician ruled
it on the same day once the rest of the record had landed, and it is finalized in place rather than
in a new record because it is this record's own open item and nothing else depends on it.

`session_end` is a `SessionEnd` **hook** registered in `.claude/settings.json`. Its exit status is
read by Claude Code under the hook contract, not by a person reading a grader's report, and the
family's `0` clean / `1` finding / `2` did-not-scan vocabulary is a vocabulary about graded runs.
The hook grades no run: it reads a transcript, decides whether a sitting drained, and writes or
withholds an orphan pointer. **So ADR 0116 ruling 3 — *no reader exits 1 for a reason that is not a
finding* — does not reach it**, and ruling 3 above was right to keep its two exit-2 routes outside
the runner's vocabulary rather than to enumerate them under it.

**What that costs is named rather than absorbed.** The hook's failure posture is now governed by
Claude Code's hook contract alone, and nothing in this session measured it: the write path was
driven with an `OSError` on `write_text` and `mkdir` and returned 0 only because the synthetic
transcript named no run directory, so **the write-failure column for `--session-end` in the table
above is a blank, not a clean**. What the hook does when a pointer cannot be written is a question
about the hook contract, not about this family, and it is outside every ruling here.

**The one thing it does settle for #840's builder** is that ruling 5's `finding` posture and the
injected-failure table describe the **graded path**, and no part of the migration should try to make
`session_end` conform to a vocabulary it was never inside.

## What this does not reach, declared rather than left to be found

**`session_end`'s own failure posture.** Ruling 6 places the hook outside the family; it does not
say what the hook should do when a pointer cannot be written, and no run in this session reached
that path. That is a question about Claude Code's `SessionEnd` contract, and it is unmeasured here.

**Ruling 5 corrects one row, not the instrument's reach.** `walk_text_reads` remains an AST floor
over direct `read_text` calls, and a fourth posture arriving tomorrow in a module nobody drove with
injected failures is as invisible as this one was. What changed is that a conversion into a finding
now has a key to be filed under, and that the ceiling says what the walk demands.

**No claim is made about the other fifteen modules' rows.** ADR 0116 refused rulings over unread
modules four separate times and nothing measured here reverses that; only `aar_scan` was driven.

**Ruling 1's re-parse is a cost, not a mechanism.** Nothing prevents a later author from letting the
two parses diverge, because `main` cannot read the run path off `run()`, which returns an `int`. A
comment says why; no check holds it.

**Ruling 4's characterization commit does not close the window it measures.** Tests pinning today's
`main` are written against a module about to be rewritten, and what survives the rewrite is the
cases rather than their expected values.
