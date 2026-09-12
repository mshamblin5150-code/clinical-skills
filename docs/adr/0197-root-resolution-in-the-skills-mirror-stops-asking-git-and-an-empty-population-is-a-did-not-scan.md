# Root resolution in the skills mirror stops asking git and an empty population is a did-not-scan

**Measured at:** 7037edb456bfc35c204579ce6688798fa57b1b09

[#978](https://github.com/mshamblin5150-code/clinical-skills/issues/978) reports that
`skills_mirror.repo_root()` is redirected by an inherited Git environment and reports a clean scan of
`tools/`. Grilled 2026-09-12; the clinician ruled every point below on the same day.

**The defect is real and the account of it was wrong in three places.** The body and
[ADR 0152](0152-the-skills-mirror-is-repaired-at-session-start-and-its-orphans-are-drained.md)
ruling 9 both name `GIT_WORK_TREE` as the vector and both name `post-checkout` as an affected hook.
Git exports neither variable to `post-checkout`, and the one it does export is `GIT_DIR`. Every
figure below was taken by driving the code and the environment rather than by reading either.

## What was measured before ruling, on 2026-09-12

Git 2.54.0.windows.1. A throwaway repository outside every checkout, with hooks whose whole body is
`env | grep -E '^GIT_'`, so the population is what git sets rather than what a reader expects.

### What git actually exports to a hook

| hook | context | `GIT_DIR` | `GIT_WORK_TREE` |
| --- | --- | --- | --- |
| `pre-commit` | main checkout | not exported | not exported |
| `pre-commit` | linked worktree | **exported, absolute** | not exported |
| `post-checkout` | `git worktree add` | not exported | not exported |
| `post-rewrite`, `reference-transaction` | linked worktree | **exported, absolute** | not exported |

**`GIT_WORK_TREE` is never exported.** The reproduction in #978's body and in ADR 0152 ruling 9 is a
real reproduction and is not the shape git produces. The live vector is an absolute `GIT_DIR`, and it
is **worktree-only**: the same hook in the main checkout receives no `GIT_*` at all.

### Either variable alone redirects, and only a subdirectory ask is reachable

`git rev-parse --show-toplevel`, asked two ways inside this worktree, one environment variable at a
time:

```
                                   asked from tools/                      asked from cwd
clean                              <worktree>                             <worktree>
GIT_WORK_TREE=.                    <worktree>/tools   REDIRECTED          <worktree>
GIT_DIR=<absolute>                 <worktree>/tools   REDIRECTED          <worktree>
GIT_DIR=<abs> + GIT_WORK_TREE=.    <worktree>/tools   REDIRECTED          <worktree>
GIT_DIR=.git   (relative)          exit 128                               <worktree>
```

This confirms the 2026-09-10 sweep comment on #978 and retires the body's original
*"both variables are needed"*. It adds the row that decides the mechanism: **the cwd ask is correct
under every poisoning**, because with `GIT_DIR` set and `GIT_WORK_TREE` unset git treats the process
working directory as the work tree root. A subdirectory ask lands in the subdirectory; a root ask
lands on the root.

### The loss is silent rather than misleading, and it is a lost repair

One mirror entry was replaced with a copy carrying a retired rule, and the three invocations driven:

```
clean,          --quiet            11 rows, WARN aar copy-stale       exit 1
GIT_WORK_TREE=. --quiet            no output at all                   exit 0
GIT_DIR=<abs>   --repair --quiet   no output at all                   exit 0
                                   the copy survived, unrepaired
```

*Under the claim's negation — correct root resolution — the first row is what all three print.*

**`--quiet` is what both git hooks pass**, so the string #978 treats as the misleading part —
*"no skills found under `skills/` -- nothing to mirror"* — never reaches a reader on the affected
path. The caller sees nothing, and `|| true` would have hidden a status anyway. The third row is the
sharper half: under `--repair` the loss is not a wrong report but a **repair that did not happen**,
at exit 0, with no line printed.

### The subprocess has no measured behavior its own fallback lacks

`repo_root()` already falls back to the script's parent directory when git fails. The two agree in
both configurations that exist:

```
worktree:  git answer == Path(tools).resolve().parent    True
main:      git answer == Path(tools).resolve().parent    True
```

No configuration was found in which they differ and git's answer is the one this module wants. The
nested-checkout case makes git's answer worse rather than better: `skills/` sits beside `tools/`, not
beside an outer `.git`. `tools/repo_root.py`'s own docstring already states the rule the subprocess is
reaching for — *"`Path(__file__).resolve().parent.parent` is the **worktree** root"*.

### One call site passes a subdirectory, and it is the only one

Every `git` subprocess in a non-test `tools/` module passes the **checkout root** as `-C` or as
`cwd` — `artifact_provenance.py`, `spelling_scan.py`, `tracker_scan.py`, `tracker_measurements.py`
and the rest. One passes a directory below the root — `tools/skills_mirror.py:156-157`, inside
`repo_root()`, where `here` is the `tools/` directory:

```python
        out = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--show-toplevel"],
```

#978's *"the only affected module"* is therefore right, and the property that makes it
right is not the one the ticket gives: it is not that this module asks from the script's directory
rather than from cwd, it is that the directory it asks from is **below the root**.

### Exposure, and the part of it that cannot be measured

`tools/skills_mirror.py`, its `-C` form and the `pre-commit` invocation all arrived in one commit —
`d62f6f75`, 2026-08-11, *"Stop the skills mirror answering with a rule that was retired"*. The check
has been inert on commits made from a linked worktree since the day it was written. **How many
commits that is cannot be measured**: git records no working directory, so nothing in the history
distinguishes a worktree commit from a main-checkout one. Recorded as unmeasurable rather than
estimated.

### `repo_root()` has no test

`tools/test_skills_mirror.py` references it once, to patch it with a `side_effect` proving the
subagent branch returns before root resolution. Every command-line test supplies `--root`. No test
calls it, and no test sets a `GIT_*` variable.

## Ruling 1. `repo_root()` stops asking git

The body becomes the answer its own `except` branch already returns — the script's parent directory,
resolved. No subprocess, and therefore nothing for an inherited environment to redirect.

**Rejected: scrubbing `GIT_DIR` and `GIT_WORK_TREE` from the subprocess environment.** It keeps git
as the resolver in order to obtain an answer measured identical to the one-line form, and it silently
overrides an operator who set those variables on purpose. It would also have to scrub each variable
independently rather than as a pair, which is the trap the original account fell into.

**Rejected: the hooks passing `--root "$repo_root"`.** Sound — both hooks already compute that value
from cwd, and the cwd ask was measured correct under every poisoning — but it leaves the library
defect standing for the `SessionStart` caller and for every future one.

**The git call is not kept as a cross-check.** A second resolver that cannot disagree is not a belt
and braces; it is a line that costs a test, which is this repository's own recorded finding about
`docx_write`'s duplicated placement guard.

## Ruling 2. An empty population is a did-not-scan, and `--quiet` breaks its contract for one line

Ruling 1 closes the poisoned root. Two paths to an empty entry list survive it: a `--root` aimed at
something that is not a checkout, and a renamed or emptied `skills/`. On those paths the command
exits **2**, on `block_scan.py`'s terms, and the diagnostic prints **even under `--quiet`**.

That is a deliberate breach of `--quiet`'s documented contract, *"print nothing when every skill is
linked"*, for exactly one line, and the help text changes with it. The ground is the measurement
above: a quiet run that said nothing is what hid this, and a vacuous *every skill is linked* over
zero skills is the clean-looking report the whole ticket is about.

`--session-start` prints `no skills found under skills/` in place of `0 of 0 linked` and **still
returns 0**. ADR 0152 ruling 1 keeps that path advisory so Claude Code consumes the structured
failure context instead of the fired hook turning back into silence, and nothing here moves it. The
string is the correction: `0 of 0 linked` is produced by one `len(entries)` on both sides of the
comparison, so it can never disagree with itself and reads as *fine* and *never looked* at once.

**The exit-2 limb is not the unreachable belt ruling 1 refuses.** It is reachable by a different
input, it is drivable by a test, and it covers a population failure rather than the resolution
failure ruling 1 closes.

**The two git hooks are unchanged and keep `|| true`.** Advisory was ruled on
[#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93) and is not reopened. That the
hooks discard the status is an argument about those two callers and not about what the status means
to a person running the command, to the `SessionStart` path, or to a future caller — and splitting
the rule so the number is honest in one mode and not the others is the two-files-two-answers shape
this repository keeps paying for.

## Ruling 3. The durable lesson is enforced by an AST walk, with its ceiling declared

The lesson is that **a git subprocess asked from a subdirectory of the checkout is redirected by an
inherited `GIT_DIR`, because git then treats the working directory as the work tree root.** A walk
over non-test modules in `tools/` asserts no `git` subprocess is given a directory below the
checkout root, by AST rather than by substring, on `test_console_codec.py`'s instrument and for its
reason: every paragraph explaining this rule contains the strings a text search would key on, this
one included.

**Its ceiling is stated beside it rather than left to be discovered.** A directory assembled at run
time, or a command built by indirection, is invisible to a predicate that reads one call. The claim
is a floor on the shapes in the tree and never *a second one cannot arrive quietly* — the
overstatement `test_ls_files_coverage.py` and `test_guidelines.py` have each already recorded paying
for.

**The walk starts green, so it is mutation-tested before it is believed.** Asserting the tree is
clean today proves only that the walk found nothing, which is `test_skill_agreement.py`'s reasoning.

**Declaring the lesson and enforcing nothing was available and is refused.**
[ADR 0165](0165-tests-list-git-paths-through-git-paths-and-no-shared-tree-reader-is-built.md) ruling 6
declares git reads outside the `ls-files` / `ls-tree` / `diff` / `rev-list` vocabulary unchecked, and
that declaration is precisely what let this one sit for a month while two sweeps re-derived the line
number and neither could fail.

## Ruling 4. ADR 0152 ruling 9 is corrected in place, and this record does not supersede it

What is wrong in ruling 9 is the **measurement** beneath the ruling, not the ruling. *"The defense is
the vulnerability"* and *"the fix is a resolution that cannot be redirected by inherited
environment"* are both exactly right and are what ruling 1 builds. The correction is dated, sits
where the claim stands on [ADR 0191](0191-a-carried-claim-is-corrected-where-it-stands-and-436-never-ruled-it.md)'s
rule, and names three rows: `GIT_WORK_TREE` is not exported, the live vector is an absolute `GIT_DIR`
and it is worktree-only, and `post-checkout` is **not** an affected hook while `pre-commit` inside a
worktree is.

**That last row retires the 2026-09-10 sweep comment's *"new gap: the affected hook runs
`--repair`"*.** The hook that runs `--repair` is the one measured clean. The `--repair` finding
survives in a different place: it is reachable from any caller under a poisoned environment, and it
is why ruling 2 exists.

**Superseding ADR 0152 was available and is refused.** Its subject is the session-start repair and
the draining of orphans. Ruling 9 is a finding it explicitly scoped out — *"Filed separately; the fix
is a resolution that cannot be redirected by inherited environment, not a change to any ruling
above"* — and folding three new rulings into it would make a note it declined to weigh retroactively
load-bearing for them.

## Ruling 5. The module takes a `NOT_REACHED`, and every other statement points at it

Ruling 2 makes the command state a coverage claim it has never made. This repository's rule is that
such a claim gets a declared boundary beside the implementation, and `refusal_scan.py` is the worked
precedent for a module that had no limits object, had its absence asserted in prose, and then earned
one on a measurement.

The complete boundary belongs to `skills_mirror.NOT_REACHED`. This ADR, the module docstring, and
`CLAUDE.md` point at that object and copy no row; the object is the one inventory a reader checks.

**`--session-start` is not given a `--root` of its own.** `CLAUDE_PROJECT_DIR` is available in the
settings registration and passing it would be a second mechanism against a failure ruling 1 has
already closed by construction, which is the line ruling 1 draws.

## What this record does not settle

**Whether the mirror can ever be graded.** It cannot while `.claude/` is gitignored, and nothing here
narrows that. It is ADR 0152's open question and stays open.

**How many commits ran the inert check.** Unmeasurable, above, and no estimate is substituted.

**Whether any other repository's git version exports `GIT_WORK_TREE` to a hook.** Everything here was
measured on git 2.54.0.windows.1 on the maintainer's machine. The rulings do not depend on which
variable is exported — ruling 1 is immune to both and to any third — but the account in the
correction is dated to that reading.

**Whether `tools/hooks/pre-commit` should stop discarding advisory statuses.** Ruling 2 changes what
the status means and deliberately changes nothing about who reads it.

**The cutoff, scope and home of ruling 3's walk beyond `tools/`.** Hook scripts and
`.github/workflows/` also run git, and neither is Python; whether they take an equivalent check is
not decided here.
