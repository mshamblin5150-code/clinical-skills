# A grader refuses a second source and the option to accept one is deleted

[#1085](https://github.com/mshamblin5150-code/clinical-skills/issues/1085) was filed out of
[#1006](https://github.com/mshamblin5150-code/clinical-skills/issues/1006)'s closing sweep: a
`run_grader` member handed two sources grades the first and exits clean. Grilled 2026-09-14 at
`origin/main` `90b16be0`; freshness gate `FRESH`. The clinician ruled every point below, one at a
time, on that date. Nothing is built here; this is the record the build reads.

**The line anchors are dated, not durable**: the build this record orders moves the lines it cites,
so a builder resolves each coordinate by the symbol named beside it.

## Measured before ruling

### The drop reproduces, and the refusal already exists

`run_grader.parse` keeps `positionals[0]` as `Parsed.source` and refuses the rest with
`"one source at a time"` only when `Grader.allow_extra_positionals` is `False`; the field defaults to
`True` (`tools/run_grader.py:527`, `:592-593`). Driven at `90b16be0`:

| command | exit |
| --- | ---: |
| `python tools/block_scan.py fixtures/filled-anchor/notes /no/such/second/directory` | 0 |
| `python tools/block_scan.py /no/such/second/directory` | 2 |
| `python tools/refusal_scan.py fixtures/filled-anchor/run-2 /no/such` | 2, `one source at a time` |

*Had `block_scan` read its second positional, the first command would have exited 2, as the second
does on that same path.*

### Ten of eighteen members accept a second positional

Importing each name in `run_grader.MEMBERS` and reading its `GRADER.allow_extra_positionals`: 18
members, 10 accepting. `aar_scan` and `filled_vitals_census` set `True` explicitly; `anchor_scan`,
`block_scan`, `checks_ledger`, `differential_scan`, `reference_scan`, `render_scan`,
`research_ledger` and `specificity_scan` inherit the default. The other eight set `False`. The
ticket's filing count of 17 members predates one more refusing member.

### Nothing passes two positionals, and nothing pins either behavior

A read-only agent searched every skill file, `AGENTS.md`, `CLAUDE.md`, `docs/`, `tools/hooks/`,
`.github/workflows/`, `.claude/settings.json` and the test modules, including
`grader_conformance.py`. Of 57 command-line invocations of the ten members, none carries a second
positional once option values are classified against each member's declared options, and no shell
glob follows a member path. No test argv carries two non-option items, and no test asserts the
drop or the refusal: the string `one source at a time` occurs only in `run_grader.parse` and in ADR
0159's prose. The session re-derived the member count and the string's occurrences itself.

### Neither explicit `True` has a reason

Both lines arrived in `cee74e42`, the commit that migrated the deferred graders to the runner. The
hand-rolled parsers they replaced already took the first positional and ignored the rest, so the
setting copied a silent drop rather than choosing one. [ADR
0117](0117-a-member-s-obligations-outside-the-graded-path-stay-in-main-and-the-crash-posture-gains-a-finding-sibling.md)
says `allow_extra_positionals` stays `True` *"preserving measured behavior rather than choosing"*,
and `filled_vitals_census`'s comment beside its `GRADER` concerns `exit_2_limbs`, not this field.

### One member branch runs before the runner

Sixteen members' `main` hands its arguments straight to `run_grader.run`. `voice_model_scan.main`
supplies a default path only when no positional was given, so a second positional still reaches
`parse`. `research_ledger.main` handles `--heading-digests` itself, before the runner, and returns 2
unless its arguments are exactly one path and that flag (`tools/research_ledger.py:2169`). No test
pins that refusal.

Four members declare an exit-2 vocabulary, and `run_grader.run` already routes a parse refusal
through each one's `invalid invocation` limb, so a refusal needs no per-member wiring.

## Ruled 2026-09-14

### 1. The option is deleted

`Grader.allow_extra_positionals` is removed, and `run_grader.parse` refuses every positional after
the first with `"one source at a time"`, exit 2, for every member. The two explicit `True` lines and
the eight explicit `False` lines go with it.

### 2. The two explicit settings carried no reason

They were migration-era preservation of hand-rolled parsers that already dropped a second argument.
No caller depends on the drop, so removing them changes no invocation anything in the tree makes.

### 3. No declared limit is needed

Once the option is gone no member can accept a second source and drop it, so there is no drop left
to declare. The ticket's decision 3 is moot rather than answered either way.

### 4. The refusal is pinned at the parser and at every member's entry point

`tools/test_run_grader.py` asserts that `parse` refuses a second positional. `grader_conformance.for_module`
gains a case that drives each member's real `main` with that member's own test argv plus a second
positional and asserts exit 2 and `one source at a time`. The parser test alone cannot see a member
whose `main` pre-processes its arguments and keeps the first itself; two already pre-process. The
message assertion is what keeps a pass from being a first source that failed to load.

### 5. The pre-runner branch is pinned and the case's ceiling is declared

`tools/test_research_ledger.py` pins that the `--heading-digests` branch refuses a second
positional. `grader_conformance.DECLARED_LIMITS` gains a row stating that the second-positional case
covers only the path its argv takes through `main`, and never a branch a member handles before the
runner on arguments the case does not pass.

## Consequences

The build is one branch. ADR 0159's sentence *"refusing extras with `"one source at a time"` only for
a grader that sets `allow_extra_positionals=False`"*, under *#410 decision 3's two grounds both
stand*, becomes false when it lands and is corrected in place there, naming this record. The dated
measurements in ADR 0174 and ADR 0178, and ADR 0159's own 2026-09-11 correction note, stay as
written: each is true of the commit it names.

## Not superseded

- **ADR 0174's refusal of `threshold_sheet` and `tracker_bodies`** stands. A parser that refuses a
  second positional is still a parser that carries one source, which is one of those refusals'
  grounds.
- **ADR 0178 ruling 9** stands; its `run_grader.DECLARED_LIMITS` entry covers which files one run
  directory's reader opens and is unrelated.

## Rejected options

- **Flipping the default to `False` and keeping the option.** The only thing `True` has ever done is
  drop a source, and a kept option reopens decision 3 for the next member to set it.
- **Ruling each of the ten members separately.** No member has a reason, so each ruling would read
  the same.
- **A parser test alone.** It cannot see a member's own pre-processing in `main`.
- **Declaring the `--heading-digests` ceiling without pinning its one live instance**, or pinning it
  without declaring the ceiling, so a clean conformance run reads as covering every entry point.

## What this does not reach

**A member whose `main` pre-processes its arguments on a flag its conformance argv does not pass.**
Ruling 5 declares it; only `research_ledger`'s branch exists today and it is pinned.

**Whether any other command outside `run_grader.MEMBERS` drops a second positional.** Nothing here
measures one.

## What must not come out of this

**Multi-source grading.** Grading several sources to one status is a runner feature `threshold_sheet`
and `tracker_bodies` are refused on under ADR 0174; a future need for it is a feature with its own
ruling, never a parser setting restored.
