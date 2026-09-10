# A generated conformance class takes its test module and a fixed name so its id re-runs

[#873](https://github.com/mshamblin5150-code/clinical-skills/issues/873) was filed out of an
architecture review of the repository gate, 2026-09-04. `tools/grader_conformance.py` builds one
`unittest.TestCase` per grader through `for_module` and `gate_conformance`, then renames the class
`<scan module>GraderConformance` or `<scan module>GateConformance`. A test module binds the result to
a plain attribute, `GraderConformance = for_module(scan)`. `unittest` builds a test's id from the
class's `__module__` and `__qualname__`, so the id the runner prints is not a name the loader can
resolve, and a failing conformance test cannot be re-run by the id it was just shown.
[ADR 0080](0080-a-gated-row-set-is-declared-per-gate-and-guarded-by-an-opt-in-walk-in-the-shared-conformance-kit.md)
and
[ADR 0118](0118-the-conformance-kit-shapes-a-migrating-grader-s-value-and-vocabulary-and-the-fixture-row-is-the-finding-kind.md)
rule on the kit's shape and are not reopened; this record rules two attributes inside it and the
one limit that ruling leaves.

Grilled 2026-09-10. The session began at `origin/main` `2314b4c` and was fast-forwarded to `63528f2`,
where every figure below was re-derived unless it names another commit. It was then brought forward
to `ed2c33a` and to `8582e2e`, which carry #1036's and #867's builds; at each the same instrument found
the same 108 ids in the same 19 classes. **Three questions were ruled by the clinician on that date.**
The first two settled the naming; the third was put after the session's tracker sweep found this
record stating a limit only in its own prose, which is
[#921](https://github.com/mshamblin5150-code/clinical-skills/issues/921)'s arrival shape. An
adversarial read of the first draft found one wrong figure, the composition of the prototype's 102,
and several places the build spec left a builder to guess; they are corrected in place below. Nothing
is built here; this is the record the build reads. Every count below is a dated measurement, not a
current property of the suite, which grew each time `main` was brought in while this record was
written.

## Measured before ruling

### Every id that does not re-run is a generated conformance class

The instrument discovers `tools/` as the CI command does,
`TestLoader().discover("tools", top_level_dir="tools")`, flattens the result, and loads each test's
`id()` back through a fresh `TestLoader().loadTestsFromName`. A test re-runs when exactly one test
comes back whose class is the same class object and whose method name is the same.

At `63528f2` discovery returns 5,231 tests and no loader error. 5,123 re-run and 108 do not. All 108
belong to the 19 classes the kit generates: 17 from `for_module`, six tests each, and 2 from
`gate_conformance`, three each. No other shape fails. The test classes built on the
`ReadingManifestConformance` mixin re-run, because their ids use the subclass's own module.

*Under the negation, every id re-running, the instrument prints 0 failures; it printed 108, and it
prints 0 under the fix measured below, so it can print both.*

The ticket's *"the remaining ~2% is the same class of naming mismatch not yet chased down"* is this
defect and nothing else. On a full-tree `git archive` of the ticket's base, `e3defa1`, the same
instrument discovers 4,724 tests with no loader error. 4,622 re-run, which is the prototype's figure,
and the 102 that do not are that tree's 18 generated classes: 16 from `for_module` and 2 from
`gate_conformance`.

### Both attributes are wrong, and each of the ticket's options moves only one

The printed id today is `grader_conformance.refusal_scanGraderConformance.<method>`. `__module__` is
`grader_conformance` and `__qualname__` is `refusal_scanGraderConformance`; the class is bound in
`test_refusal_scan` as `GraderConformance`. Each candidate below was applied in memory after
discovery, with no file edited.

| class attributes set | generated tests that re-run |
| --- | --- |
| as shipped | 0 of 108 |
| `__qualname__` to the binding name only (the ticket's decision 1) | 0 of 108 |
| `__module__` to the binding test module only | 0 of 108 |
| both | 108 of 108 |

The ticket's decision 3, binding a module-specific name such as `AarScanConformance`, changes only the
attribute name. `test_aar_scan` and `test_filled_vitals_census` already do it, and both still print
`grader_conformance.aar_scanGraderConformance` and `grader_conformance.filled_vitals_censusGraderConformance`,
because the kit overwrites `__qualname__` regardless of the binding.

### The kit can learn the calling module and cannot learn the binding name

`for_module(module)` and `gate_conformance(module)` receive only the scan module. Read from the
caller's frame, `sys._getframe(1).f_globals["__name__"]` named the binding test module in all 19 calls,
across 17 modules. Every call is at module level, and the attribute form `grader_conformance.for_module`
gives the same frame as the imported name. The binding name is assigned after the function returns,
so no call can observe it.

Of the 19 bindings, 15 are `GraderConformance`, 2 are `GateConformance`, and the two above use their
own names. `test_discussion_post_scan` and `test_discussion_reply_scan` each bind one of each kind; no
module binds two of one kind. Simulating ruling 1 below left 12 tests unable to re-run, all in the two
modules with their own names; renaming those two bindings left none.

### A module binding one kind twice loses a class, and no check sees it

A throwaway test module outside the tree bound `GraderConformance = for_module(refusal_scan)` and then
`GraderConformance = for_module(block_scan)`, with the kit simulated as ruling 1 sets it. Two generated
classes of six tests each should give 12. Discovery returned 6 with no loader error, and all 6 re-ran
by id, so ruling 3's test would pass while the first class's tests never ran. `test_run_grader`'s
adoption walk checks only that a `for_module` call exists, so it passes too. *Had the first class
survived, discovery would have returned 12.* Ruling 2's single fixed name makes the collision easier to
write than the per-module names it replaces.

### Nothing outside the kit reads the generated names, and the scanner stays legible

Outside the kit's own two assignment pairs, no file in `tools/` or `.github/` reads a generated class's
`__name__`, `__qualname__` or `__module__`. The five `loadTestsFromName` call sites each build
`test_<module>.<name>` from their own `HANDLERS`, and no handler names a conformance class.
`test_run_grader`'s adoption walk matches the call name `for_module`, not a class name.

The ticket's decision 2 supposed the rename bought a legible verbose line. Under ruling 1 the line reads
`test_x (test_refusal_scan.GraderConformance.test_x)` where it read
`test_x (grader_conformance.refusal_scanGraderConformance.test_x)`: the scanner's name moves from the
class into the module part, and nothing is lost.

## Ruled 2026-09-10

### 1. The kit names the class after its binding: the calling module and a fixed name

`for_module` sets the generated class's `__module__` to the calling module's `__name__`, read from the
caller's frame, and its `__name__` and `__qualname__` to `GraderConformance`. `gate_conformance` does the
same with `GateConformance`. Neither signature changes and no call site gains an argument. The
module-derived rename at `grader_conformance.py`'s two assignment pairs is removed.

### 2. Every binding uses the fixed name

A test module binds `GraderConformance = for_module(scan)` and `GateConformance = gate_conformance(scan)`.
`test_aar_scan` renames `AarScanConformance` and `test_filled_vitals_census` renames
`FilledVitalsCensusConformance`; no other binding changes. The kit's module docstring states the
convention, and `CLAUDE.md`'s **Grader conformance** section gains one sentence naming the two binding
names, `tools/test_suite_ids.py` and `grader_conformance.DECLARED_LIMITS`. That sentence copies no row
of the object and leaves intact the three phrases
`test_discussion_post_scan.TheSharedConformanceKitStatesItsBoundary` asserts in the section.

### 3. One test requires every discovered id in the suite to re-run

`tools/test_suite_ids.py` discovers the suite with both the start and the top-level directory set to
the directory holding the test module itself, which is what the CI command's `-s tools -t tools` names
from the repository root, so the result does not depend on the working directory. For every
discovered test it requires that a fresh `loadTestsFromName(test.id())` returns exactly one test whose
class is the same class object and whose method name is the same. The population is discovery, never
the kit, so a class generated elsewhere or a future shape is graded too. A loader error during
discovery fails the test rather than shrinking its population. Its module docstring states that the
population is the CI command's, `test*.py` under `tools/`; a test module carries no limits object.

On failure the report states the denominator and, for each id that does not re-run, the module
discovery found it in and every attribute name that module binds the class to. For today's defect that
reads `test_refusal_scan` binding `GraderConformance`, which is the binding ruling 1 makes the id match.

The build shows the test failing against the kit as it stands, before ruling 1 is applied, and passing
after. It is the whole-suite form because nothing downstream checks that a printed id re-runs. Run on
its own it measured 2.3 seconds on the maintainer's machine, 0.9 to discover and 1.4 to load every id;
inside the full suite a second discovery reuses the imported modules and measured about 0.1 seconds.

### 4. #873 is a prerequisite of #874's re-run by id

[#874](https://github.com/mshamblin5150-code/clinical-skills/issues/874)'s stated motive includes a gate
that can re-run one failing test by the id it printed. No gate module can make a generated class's id
resolve while the kit overwrites both attributes, so #874 gains a native blocked-by edge on #873 when
this record lands. The edge decides none of #874's own questions.

### 5. The kit earns `DECLARED_LIMITS` for the double binding, and the limit stays open

`grader_conformance.DECLARED_LIMITS` is a tuple of `(subject, reason, EvidenceDisposition)` triples
using `run_grader.EvidenceDisposition`, as `render_scan` and `discussion_post_scan` hold. It holds one
row: **whether every generated class a test module creates is bound where discovery can find it**; a
second binding of one kind in one module replaces the first, so the first class's tests never run and
neither ruling 3's test nor the adoption walk can count them; behavior. It is earned by the measurement
above, not by symmetry, on
[ADR 0162](0162-render-scan-earns-its-limits-object-on-a-measurement-and-counts-exactly-one-image-per-page.md)
ruling 1's terms.

`tools/test_suite_ids.py` names the object and holds its evidence:

- a partition test: every row carries one disposition, and the behavior rows are exactly the
  double-binding row;
- a control: a synthetic test module written to a temporary directory binds one kind twice, discovery
  of that directory returns only the second class's tests, and the id requirement passes over them.

The control asserts the boundary still holds, so a build that closes it fails the control and must
retire the row in the same change. The kit's docstring and `CLAUDE.md` point at the object and copy
no row; `test_claude_pointers` covers the section's pointer by construction.

## Rejected options

- **The ticket's decision 1 alone, `__qualname__` set to the binding.** Measured above: no id re-runs,
  the 15 `GraderConformance` bindings would print one identical class path across modules, and the 2
  `GateConformance` bindings another.
- **The ticket's decision 3, module-specific binding names.** Measured above: the binding name never
  reaches the id while the kit overwrites it, so it is not an alternative to ruling 1.
- **Keeping the descriptive name with the module corrected.** The id would read
  `test_refusal_scan.refusal_scanGraderConformance`, which re-runs only if every module binds that
  underscore-joined name.
- **Passing the binding name to the kit, `for_module(scan, "GraderConformance")`.** It edits all 19 call
  sites to type each name twice, where 15 of 17 `for_module` bindings already follow the fixed name.
- **Passing the calling module, `for_module(scan, __name__)`.** It edits all 19 call sites to supply
  what the frame already reports; a call routed through a helper is caught by ruling 3 either way.
- **Grading only the kit's classes, found by walking `for_module(` and `gate_conformance(` calls.** A
  call through a helper is invisible to that walk, and the claim #874 needs, that any printed id
  re-runs, would stay unmeasured.
- **Leaving the classes alone and sharding by discovery objects.** It fixes one runner and leaves a
  failing test unaddressable by the id a person was shown.
- **Making the kit refuse a second call of one kind from one module.** It closes the hole with a new
  rule the ticket did not name, and a future test of the kit that builds two classes from one module
  would need a way around it.
- **Leaving the double binding in this record's prose.** A limit written only in an ADR fails nothing
  when it stops being true, and it lands outside `test_declared_limits.declarers()`, which is #921's
  recorded shape.

## What this does not reach

**Whether a module binds one kind twice.** Declared by ruling 5 and closed by nothing here. No module
does it at `63528f2`.

**Tests outside discovery's reach.** Ruling 3's population is the CI command's, `test*.py` under
`tools/`, and nothing else.

**Sharding, job counts and timing weights.** Those are #874's.
