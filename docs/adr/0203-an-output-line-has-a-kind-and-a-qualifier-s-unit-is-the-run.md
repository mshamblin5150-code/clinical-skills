# An output line has a kind and a qualifier's unit is the run

**Measured at:** 00bad566273963c75dc536b9005c8ccc5473d95d

[#986](https://github.com/mshamblin5150-code/clinical-skills/issues/986) reports that
`threshold_sheet.py`'s never-recorded tier-2 line sits inside `format_report`, which `--quiet`
suppresses, and that `--quiet` is what `tools/hooks/pre-commit` passes. Grilled 2026-09-12; the
clinician ruled every point below on the same day.

**The suppression is real and the harm claimed for it is not.** Every figure here was taken by
driving the commands rather than by reading them, and two of the ticket's own load-bearing claims
came back false. The ticket's premise — that the hook's output *"is read only because it is usually
empty"* — is false about the tree it was filed against: a clean `--all --quiet` run prints 1,879
lines and not one of them is a finding.

## What was measured before ruling, on 2026-09-12

At the commit above, on the maintainer's machine, with the guideline corpus present. Every figure
was first taken at `6380b8a6`; `main` advanced twice during the grilling, to the commit above, touching
`tools/implementation_map.py`, its test, and one ADR unrelated to this subject. `tools/threshold_sheet.py`, `tools/apa7_coverage.py`,
`tools/hooks/pre-commit` and `reference/thresholds/` are byte-identical across that advance, and the
AST population and the 169-of-169 walk were re-derived on the new base and are unchanged.

### The suppression, driven

A scratch copy of `reference/thresholds/asthma.md` with its `citations resolved against` line
removed, run both ways:

| run | `NOT RECORDED` on stdout | `FAIL` on stderr |
| --- | --- | --- |
| no flag | yes | yes |
| `--quiet` | **no** | yes |

*Control: the unmodified sheet's quiet run carries zero `corpus-free` matches, so the instrument
discriminates between the claim and its negation.*

### The sentence the ticket says is lost is the refusal

The ticket states that a committer *"sees a `FAIL` and not the sentence explaining that a corpus-free
reader cannot tell checked once from never checked."* That sentence **is** the `FAIL`. It is built as
a finding, not as a report line:

```python
findings.append(
    f"{sheet.path.name}  CITATION tier 2 has no resolution declaration in "
    "## Scope. A corpus-free reader cannot tell checked once from never checked."
)
```

Findings become `  FAIL  ...` entries in `scan.diagnostics`, and `_emit_scan` prints `scan.diagnostics`
to stderr unconditionally — the `if not quiet` branch guards `format_report` alone:

```python
    for line in scan.diagnostics:
        print(line, file=sys.stderr)
```

### The line it would carry is latent on the tree

169 of 169 committed sheets under `reference/thresholds/` parse with `resolved_date` set, excluding
the README, the coverage registry and the subject ledger. *Control: stripping the declaration from
one copy returns `None`, so the walk is live.* A first attempt passed the wrong argument to
`threshold_grammar.parse`, failed all 169 and printed `missing: 0` — a clean-looking zero from an
instrument that never ran. It was discarded and retaken.

### The population every prior sweep measured is wrong

Six sweeps measured the `--quiet` family as **five**, which is the subset `tools/hooks/pre-commit`
invokes. Derived by AST over every non-test module in `tools/`, the members are **seven**:

| command | declares | reads | behavior |
| --- | --- | --- | --- |
| `apa7_coverage` | yes | 0 | inert, deliberately |
| `closing_keyword_scan` | yes | 2 | honored |
| `guidelines_extract` | yes | 1 | honored |
| `skills_mirror` | yes | 2 | honored |
| `spelling_scan` | yes | 4 | honored |
| `threshold_sheet` | yes | 4 | split |
| `uptodate_sheet` | yes | 1 | honored |

A bare text search says nine. `artifact_provenance` matches on git's own `git diff --quiet`, and
`guidelines_build` *passes* `--quiet` to the extractor rather than declaring one — which also
establishes that `--quiet` is not a synonym for hook mode, since a parent process uses it to silence
a child's per-document chatter.

`--quiet` is the only suppressor. The other `store_true` flags in `tools/` either add output
(`--verbose`), reveal redacted detail under the PHI rules (`--show`), or select a different artifact
entirely: `--brief` is documented as `"print the work order for --span and grade nothing"`.

The suppressor set and `run_grader.MEMBERS` are **disjoint**. None of the seven imports
`run_grader`; none of its twenty-two members declares `--quiet`.

### What a clean commit actually prints

`python tools/threshold_sheet.py --all --quiet`, the hook's own invocation, over 169 sheets:
**1,013 stdout lines and 866 stderr lines in 1 minute 40 seconds.**

| lines | stream | content |
| ---: | --- | --- |
| 332 | stdout | rule characters |
| 498 | stdout | the same three-line `WATERMARK DID NOT RUN` text, once per sheet |
| 168 | stdout | blank |
| ~130 | stdout | per-source `PAGE COVERAGE ... unaccounted pages: none` |
| 181 | stderr | `RECOMMENDATION RECORD source 'x' -- sweep alias ...` |
| 181 | stderr | `COVERAGE NOT RUN for source 'x' -- untrusted record ...` |
| 169 | stderr | `The ordinary remedy for the untrusted recommendation record(s) above is ...` |
| 169 | stderr | `EXTRACTION IDENTITY NOT RUN -- untrusted artifact ...` |
| 166 | stderr | `WATERMARK       N manifest problem(s)` |

`FAIL` count: **0**. `WARN` count: **0**. `NOT DIFFED` count: **0**.

**One six-line banner is repeated 166 times, verbatim.** Each copy is individually correct. Together
they are what trains a reader to skip the output, which is the harm the qualifier exists to prevent.

### The mechanical root cause

`threshold_sheet` already carries the two-way split, named by **channel** rather than by kind, so the
call site is asked the wrong question:

```python
def _report_lines(lines: Iterable[str]) -> tuple[Line, ...]:
    return tuple(Line(text) for text in lines)


def _stdout_lines(
    lines: Iterable[str],
    *,
    placement: LinePlacement = LinePlacement.TRAILING,
) -> tuple[Line, ...]:
    return tuple(Line(text, suppressible=False, placement=placement) for text in lines)
```

And the report frame never enters that vocabulary at all. `_report_footer` and `_report_opening`
return raw strings, appended inside `format_report`:

```python
def _report_footer(sheet: Sheet) -> tuple[str, ...]:
```

So the footer is not on the wrong side of `--quiet`. **It was never on a side.** That is why six
sweeps could re-derive the mechanism and none could answer the question.

## Ruling 1. An output line has one of three kinds, and the kind decides the channel

**Finding** — something is wrong. stderr, never suppressible, drives the status.

**Coverage qualifier** — what this run did not establish, for a reason the reader did not choose.
Never suppressible. This is [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
ruling applied to a channel instead of to a report: a reader who learns to read a qualifier reads its
absence as the stronger claim.

**State** — counts, dates, provenance, what was read. Suppressible. This is what `--quiet` is for.

Non-coverage the reader selected by not passing a flag is **state**, not a qualifier. A machine
property the reader cannot see from the command line is a **qualifier**. `SECOND READ NOT RUN -- no
--second-read given` is the first; `CITATION TIER 2 DID NOT RUN` with no corpus on the machine is the
second.

Kind is a property of the line and never of the invocation, or the call site cannot be asked the
question.

## Ruling 2. A qualifier's unit is the run, not the sheet

Under `--all`, each distinct qualifier is emitted **once, with its denominator**. One
`WATERMARK DID NOT RUN for 166 of 169 sheets` replaces 166 identical banners, and the denominator is
a fact that 166 copies do not state.

Per-sheet repetition of a run-scoped qualifier is a defect this record names, not a style question.

**Ruling 1 may not ship without ruling 2.** Classing alone moves several currently-suppressed
`NOT RUN` lines onto the survivor side, so it makes the hook noisier and breaks #986's own
prohibition on its first day.

## Ruling 3. State may not ride the unconditional channel

Of the 866 stderr lines on a clean run, 181 are `RECOMMENDATION RECORD source 'x' -- sweep alias ...`
— provenance, which is state under ruling 1 and is unconditional today. Ruling 1 already forbids
this; it is called out because the unconditional stderr channel was offered on #986's thread as a
home for lines needing to survive `--quiet`, and it is the opposite: the channel is already carrying
state it should not.

## Ruling 4. The rule binds the seven, with a tripwire

The suppressor set is the population, because the rule bites only where something can emit less than
its full output. Over `run_grader`'s members it is vacuous — nothing there suppresses anything.

A test asserts the suppressor population **is** those seven, derived by AST, so an eighth command
declaring `--quiet` fails the suite and its author classes its lines rather than arriving unclassed.
The family grew from five to seven while every sweep re-measured five and nothing failed.

`--brief` is a declared exception: it selects a different artifact, so "which lines survive" is not a
question about it.

## Ruling 5. Each module expresses the rule its own way, and the rule is uniform

`threshold_sheet`'s `Line` gains a `kind`; `suppressible` becomes derived from it rather than set
beside it; the two constructors are renamed to kind names; and the report frame is brought inside
`Line` so it can be classed at all.

The other six declare a module-level tuple naming their unsuppressed lines, on
`reference_scan.BODY_ROWS`'s precedent — a declared subset with a property, bound in both directions
by a walk read off the module rather than off a fixture.

**The mechanism is deliberately non-uniform and that is not drift.** A shared kinds module would make
six modules that behave correctly grow a line abstraction to import it. What is shared is the rule,
on the same footing as `research_ledger` and `checks_ledger` holding separate copies of one keyword
rule.

## Ruling 6. The three decided cases, and they are decided here rather than by the builder

The `NOT RECORDED` footer line is **state** and stays suppressed. Its qualifier claim is already
carried by an unconditional `FAIL`, and it fires for no committed sheet.

The dated footer line is **state** and stays suppressed.

The second-read pairings are **state** and their smoke-test caveat is a **qualifier**, so the
behavior recorded as a defect on #986's thread is already correct and no change is owed.

## Ruling 7. ADR 0154 ruling 8 is narrowed from five rows to two

[ADR 0154](0154-the-apa-sheet-rests-on-the-manual-and-its-coverage-is-a-digest-bound-registry.md)
ruling 8 requires `apa7_coverage`'s counts to print through `--quiet`. Under ruling 1 that is right
for `never-checked` and `gone-stale`, which are qualifiers, and over-broad for `manual items`,
`read-to-root` and `ruled-out`, which are state.

```
manual items   345      <- state
read-to-root   345      <- state
ruled-out      0        <- state
never-checked  0        <- coverage qualifier
gone-stale     0        <- coverage qualifier
```

That paragraph of ruling 8 is superseded. Its reporting half is preserved: the rows that say what was
not established still reach a reader positioned to act on them.

This answers [#1119](https://github.com/mshamblin5150-code/clinical-skills/issues/1119)'s decision 1
— honor the flag — without overturning the ratified route it took. ADR 0159 records that the inert
flag was a deliberate satisfaction of ruling 8 rather than an oversight.

## Ruling 8. The builder applies the classification, and does not re-derive it

The complete measured inventory above is classed in this record. A builder who re-derives the
judgment produces an eighth reading of a question seven readings have already been given, which is
the failure this ticket is an instance of.

## What this record does not settle

**Whether a given line was classed correctly.** The rule constrains an author and a test can assert
that the vocabulary is declared, that the population is the seven, and that no finding is
suppressible. It cannot assert that a line is genuinely a qualifier rather than state. A clean suite
is not a checked classification.

**The 1 minute 40 seconds.** The hook adds roughly 100 seconds to every commit touching a threshold
sheet. That is a property of how much work runs rather than of what prints, it is not entangled with
this ruling, and it is filed separately.

**Exit status.** Nothing here changes what refuses. Findings and not-graded still drive the status,
and #986's absent-declaration finding refuses before and after.

**Whether a reader acts on a qualifier they can now see.** Ruling 2 makes 1,879 lines readable; it
does not make anybody read them.
