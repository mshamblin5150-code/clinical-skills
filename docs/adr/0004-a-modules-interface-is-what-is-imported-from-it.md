# A module's interface is what is imported from it, and `tools/` stays public by default

An architecture review flagged `tools/corpus_census.py` as a shallow module: 2,508 lines offering **117 public module-level names against 3 private**, consumed by two production modules that use **four** of them. Interface nearly as wide as implementation is the textbook signal, and on that reading the module should be narrowed.

**The reading is wrong, and it is wrong in a way that will recur**, which is why it is recorded here rather than closed as a ticket nobody opens.

Depth is leverage per unit of interface a caller has to **learn**. A caller of `corpus_census` learns two names. The 117 are not an interface anybody navigates — they are internals that Python has no way to hide and that nobody has ever reached for.

## What was measured

2026-08-21, on `0c7fa33`, by AST over `tools/`. Every figure re-derives by walking `ast.ImportFrom` and `ast.Import` across the non-test modules; none is quoted from a report.

**Nothing imports a wide surface from anything.** The largest de-facto interface in the directory is five names:

| module | names imported from it |
| --- | --- |
| `repo_root` | `InsideCheckout`, `enclosing_checkout`, `ensure_outside_checkout`, `main_repo_root`, `scratch_root` |
| `icd10_lookup` | `CATEGORY_LENGTH`, `describe`, `normalize`, `notes_for`, `open_database` |
| `guidelines_manifest` | `MANIFEST_NAME`, `Record`, `read_or_raise`, `serialize_record` |
| `docx_write` | `REFERENCE_HEADING`, `blocks`, `markdown_tables`, `split_row` |
| `corpus_census` | `Reading`, `is_normal_bp` |

Across 81 cross-module import edges, every one is a small deliberate set. **No module has ever reached past another's import set into its internals.**

**Public-by-default is a house convention, not a `corpus_census` property.** Every large module carries it, and **no module in the repository declares `__all__`**. `corpus_census` is the extreme of a distribution, not an outlier in kind:

| module | lines | public / private |
| --- | ---: | --- |
| `corpus_census` | 2,508 | 117 / 3 |
| `research_ledger` | 1,871 | 90 / 14 |
| `guidelines_extract` | 1,897 | 82 / 14 |
| `reference_scan` | 1,132 | 61 / 9 |
| `threshold_sheet` | 2,200 | 39 / 22 |

**The counts move and the shape does not.** `threshold_sheet` has the healthiest ratio of the large modules only because [#410](https://github.com/mshamblin5150-code/clinical-skills/issues/410) split its gates and created real private helpers — so these numbers are a snapshot and are meant to be re-derived rather than cited. What survives re-derivation is the claim underneath them: **imports are small everywhere.**

## Considered options

**Narrow `corpus_census` — underscore-prefix the ~113 names nothing imports.** Rejected. It touches a 3,657-line test module that reaches into those names deliberately, because the census's extractors are the thing under test, and it buys no caller anything: the two consumers already learn two names. It also singles out the largest instance of a convention every large module here follows, which teaches the wrong lesson to whoever reads the diff.

**Declare an interface per module — `__all__` or a `PUBLIC` tuple on the eleven modules with two or more importers, plus a walk refusing an import outside it.** Rejected, and it was the closest call. The mechanism is one this repo already uses well: a walk with declared exclusions and a declared ceiling, landed four times in the week this was written. What it lacks is an instance. **One adapter means a hypothetical seam; two means a real one** — and this has zero. Nothing has ever imported an internal, so the walk would be built to refuse a thing that has not happened, and its first effect would be to make eleven modules carry a declaration nobody had needed. If an instance arrives, this is the option to reopen.

**Do nothing and record nothing.** Rejected because the finding is *cheap to re-derive and expensive to re-adjudicate*. `117 public names against 2 imports` looks like a defect from outside; it took a measurement of the whole directory's import graph to establish that it is not. That measurement is worth more than the conclusion, and an unrecorded conclusion gets re-derived by the next reviewer — which is how this one arrived, from a report the same session had written three hours earlier.

## Decision

**A module's interface in `tools/` is the set of names other modules import from it.** Public-by-default stands; `__all__` is not adopted; no module is narrowed on surface-area grounds alone.

Depth here is judged by what a caller has to learn, not by counting `def`s. On that measure the directory is in good shape: eleven modules are imported by two or more others, led by `console_codec` at 28, `run_grader` at 10, `repo_root` at 8, and `guidelines_manifest` at 6 — every one of them a small, named set of names.

## Consequences

**A wide public surface is not, by itself, a finding.** A future review that opens with a public-name count should measure the import graph before proposing work, and this ADR is the thing to cite when declining.

**The protection against reaching into an internal is review, not a mechanism**, and that is accepted rather than overlooked. Nothing fails if a new module imports a helper the author of the target would call private. The cost of that is bounded today by every import being 1–5 names, and it is unbounded in principle.

**Two things would reopen this**, and they are the reason the measurement above is dated rather than stated as permanent:

- **A module reaching past another's small import set** — the first real instance of the coupling the declaration option would prevent.
- **A large module gaining a second consumer that wants a different subset.** One consumer defines an interface by accident; two that disagree about which names matter is the point at which declaring becomes worth its cost.

**And nothing here licenses a module to grow.** `corpus_census` at 2,508 lines with 52 public functions may still be worth splitting — on cohesion, on what its four `survey_*` entry points have to do with each other, or on the 3,657-line test module that shadows it. This ADR says only that **surface area is the wrong reason**, and that whoever proposes the split should bring a different one.
