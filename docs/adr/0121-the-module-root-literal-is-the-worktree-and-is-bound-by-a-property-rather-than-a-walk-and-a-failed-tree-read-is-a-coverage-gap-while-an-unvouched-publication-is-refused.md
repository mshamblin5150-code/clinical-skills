# The module-root literal is the worktree and is bound by a property rather than a walk, and a failed tree read is a coverage gap while an unvouched publication is refused

Found while grilling [#832](https://github.com/mshamblin5150-code/clinical-skills/issues/832),
2026-09-03, at `origin/main` `b058e13c70335ca4732305f4220c9afbc10f1655`, freshness gate `FRESH`
before reading and before publishing. **Ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

#832 was filed as a ticket about `repo_root`'s unheld half — a root literal written out 28 times
while its guard sibling is held by an AST walk. Three of its five decisions were re-derived before
anything was asked, and two of the three measured clean. The ticket's live finding is at the other
end of the same call, and it is larger than the ticket states.

## Measured before ruling

**The ticket's own figure reproduces exactly at its base.** At `7ad784e`, `grep -c` over non-test
`tools/*.py` returns **28 sites across 25 files**, as written. At `b058e13` it returns 29 across 25,
`aar_scan` having gained one.

**Two of those grep hits are prose.** By AST the population is **27 uses across 24 non-test
modules**; `repo_root.py`'s two hits are docstring mentions in the paragraph explaining the rule.
That is `spelling_scan`'s mention-versus-use distinction arriving on the ticket's headline number —
the count is a floor in one direction and an over-count in the other, and neither is visible from the
grep.

**The population is four times the ticket's, because the ticket scoped to non-test.**

| | sites | modules |
| --- | ---: | ---: |
| non-test uses (AST) | 27 | 24 |
| test uses (AST) | 81 | 67 |
| **total** | **108** | **91** |

**Decision 3 measured clean.** Every non-test module that reaches account-owned state already
imports `repo_root` and holds both roots side by side — `phi_scan` carries `REPO_ROOT` for its
tracked-file walks and `SCRATCH = scratch_root()` for the corpus, and `corpus_census`, `aar_scan`,
`voice_model_scan` and `guidelines_build` do the same. **No site is wrong today.** The property
behind the ruling is checkable and its baseline is a genuine zero:

```
non-test modules using the literal:                                24
modules joining a literal-derived root with scratch/ or output/:    0
```

**Decision 4 measured equivalent, and the ticket undercounted its own population.** There are
**four** subprocess `cwd` sites, not three — `tracker_branch_scope._main_ancestry` is the one the
body omits — and all four are in the two tracker gates. `refs/remotes/origin/main` lives in the
**common** git dir rather than the per-worktree one, so the read is the same object from either
cwd:

```
worktree .git dir:       .git/worktrees/grill-with-docs-472-eec18b
worktree common dir:     .git
git ls-tree -r --name-only origin/main:  619 lines from each, IDENTICAL
```

One of the four — the `gh graphql` readback — passes `owner` and `name` as module constants, so its
`cwd` is inert.

**Decision 5 measured one defect and one blind instrument.** Over every `subprocess` call in
`tools/` that decodes:

```
calls that really decode:                                    62
missing errors= :                                             1   tracker_branch_scope.py:150
invisible to TheOtherEndOfTheSameBoundary's predicate:       21
```

The walk's `decodes` predicate keys on `text=`, `universal_newlines=` and `check_output` and **not on
`encoding=`**. A call passing `encoding=` alone decodes and the walk cannot see it. Twenty of the
twenty-one blind calls happen to comply; the twenty-first is the defect. `CLAUDE.md`'s claim that the
walk *"asserts each one that decodes names both its encoding and its `errors`"* has been false since
the walk was written.

**A second, more reachable defect sits on the same call and the ticket does not name it.** Line 150
carries `check=True`. Its immediate sibling `_main_ancestry` carries `check=False` and returns `None`
deliberately, and the module already owns a declared posture for an unreachable remote in
`remote_fresh`. `_default_branch_paths` is the only git read in the module that raises. A clone that
has never fetched `origin/main` reaches it far more readily than an undecodable path byte does.

**Both exceptions open the gate, and the module anticipated neither at this host.**
`tracker_branch_scope.main` explicitly catches `subprocess.CalledProcessError` and `UnicodeError` and
returns 2. Through `tracker_publish_hook.analyze` the same two land in `except Exception` →
`_hook_response(None, ...)`, which omits `permissionDecision` entirely and **allows the
publication**, reported as `HOOK FAILURE: Unreadable body (CalledProcessError)`. The body was fine.

**The same function already implements the correct posture eight lines above the handler that does
not.** `fetch_readback` has a narrow handler that degrades to
`"tracker readback: FETCH FAILED; context-blind"` and lets every gate keep running. `analyze` — which
carries the PHI scan, the branch-scope grade, the C0 check and the body check — has no handler at
all. The module degrades gracefully for the *context* read and catastrophically for the *gates*, and
both are inside one `try`.

## Ruled 2026-09-03

### 1. The root half is a declared non-defect, and the walk does not widen to it

#832's decision 2 is refused. `test_write_guards`'s AST walk stays keyed on the checkout marker and
gains no second subject.

The evidence for widening is a grep count, and every attempt to convert that count into a defect
measured clean. The population is **108 sites across 91 modules** — essentially every module in
`tools/` — of which 107 are correct. Making such a walk pass means either the bulk rewrite #832's own
*What must not come out of this* forbids, or an exemption list longer than the rule.

**A walk whose loudest output is the thing working has no usable baseline, and *the same as last
time* is the only reading anybody takes off one.** That is this repository's argument against the
`check=True` walk in ruling 4 and against the allowlist in
[ADR 0033](0033-the-scratch-baseline-is-a-count-because-the-set-is-phi-and-the-repo-is-public.md),
arriving on the root literal.

`repo_root`'s docstring already states the rule in prose. What it lacked was a binding, and ruling 5
supplies one at a population of 24 rather than 108.

### 2. The four tracker-gate `cwd` sites are correct and are declared, not changed

`Path(__file__).resolve().parent.parent` as a subprocess `cwd` in `tracker_branch_scope` and
`tracker_publish_hook` stays. The four commands name `origin/main` explicitly or are repo-scoped by
literal, and that ref is shared with the owning checkout, so the two cwds cannot disagree.

**Changing them to `main_repo_root()` would be a behavior change with no defect behind it**, and it
would be wrong in one case the literal handles: an exported tree with no `.git` has no owning
checkout, and `main_repo_root` returns its own root there by design.

The ticket's `_default_branch_paths`-only list is corrected to four sites in this record, and the
`gh graphql` site's `cwd` is recorded as inert.

### 3. A failed tree read is a coverage gap, not a finding

`_default_branch_paths` takes `check=False` and `errors="replace"` and returns `None` rather than a
`frozenset` when the read does not complete. The citation row then reports **not graded** with a
banner naming what was not measured, the publication proceeds, and `NOT_REACHED` gains a row that is
true.

**This is the arrangement `_main_ancestry` and `remote_fresh` already use one function below**, so it
costs a return type rather than a posture.

The two rejected answers are recorded because both will be re-proposed. **Allowing silently and
declaring it** re-rules
[ADR 0096](0096-an-unreadable-publication-is-refused-and-expansion-is-reconstructed-from-the-command-as-typed.md)
the other way at the same hook, and #745 records two escapes from getting that wrong. **Refusing**
turns a missing `git fetch` into a blocked publication over an input the author did not supply and
cannot fix, which is the check that gets learned around with `--no-verify`.

**What decides it is how much still ran.** This row is one of several and the others are unaffected,
so an absent input must not masquerade as a passing count — and must not masquerade as a finding
either.

### 4. An `analyze` that raises denies, and that is not ruling 3 contradicting itself

`tracker_publish_hook`'s `except Exception` stops returning a decision-free response. An exception
escaping `analyze` produces `deny`, and the diagnostic stops naming the body for a failure that had
nothing to do with the body.

**The line between this and ruling 3 is how much of the gate ran.** Ruling 3's failure leaves every
other row measured; this one leaves **none** measured. A publication that proceeds with no PHI scan
having executed, reported as a coverage banner, is standing rule 1 going quiet — which is
[#93](https://github.com/mshamblin5150-code/clinical-skills/issues/93)'s defect arriving at the
publication boundary instead of the commit boundary. ADR 0096's subject is literally this: the gate
returned *allow* whenever it could not vouch for the text.

**The next reader will find two opposite rulings on adjacent handlers in one `try`, and that is
deliberate.** The narrow handler above them is the worked precedent for ruling 3; the blanket one is
the worked precedent for ruling 4. Neither generalizes to the other.

### 5. The instrument grows one limb, and its ceiling is stated as a floor

`TheOtherEndOfTheSameBoundary`'s `decodes` predicate gains `encoding=`. That is the whole instrument
change, and it is a live-instrument proof rather than a promise: the widened population is 62, it
goes red on exactly `tracker_branch_scope.py:150` today, and green after ruling 3. Nothing else
moves.

**No `check=` walk is built.** There are 57 `check=True` calls in `tools/`, 56 correct, 55 of them in
test modules, and the one that matters is not distinguishable by the keyword — `spelling_scan`,
`skills_mirror` and `artifact_provenance` all use it correctly because their callers handle it. The
failure-direction rulings are held instead by the thing they are about: a test that `analyze` raising
produces `deny`, a test that a failed `_default_branch_paths` reports *not graded*, and a
`NOT_REACHED` row in each module.

**`CLAUDE.md` line 151's second clause stays false and is corrected to a floor.** *"So a fourth site
cannot arrive quietly"* is not what a predicate reading one call node can promise: a command
assembled by indirection, or a subprocess reached through a wrapper, is invisible to it. That is the
identical overstatement already priced at `test_ls_files_coverage` and at
`EveryFilterHasAVocabularyGuard`. The corrected sentence states the shapes in the tree it reaches and
records that the walk was blind to **21 of its own 62-call population** for the whole time it was
credited with holding this rule.

### 6. `module_root()` is refused; the ruling is bound by a property test

No new function. `repo_root` gains nothing.

**It fails this repository's own test for when a helper may be shared** —
[#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253): *depending on it is the
point, not that two callers currently agree.* `main_repo_root` passes, because it encodes a policy —
the `.git` pointer-file walk with its submodule exclusion. `module_root()` encodes nothing; it is an
alias for a literal. And ruling 1 refused the walk that would drive adoption, so it lands in a tree
where four or five sites call it and 103 do not, which reads as *those five are special* and makes
the choice **more** invisible at the 103, not less.

What replaces it is a test of the property the ruling is actually about: **no non-test module joins a
literal-derived root with an account-owned directory name.** Population 24, zero failures today, and
it fails the day someone writes `Path(__file__).resolve().parent.parent / "scratch"` — which is #93's
original bug, reintroduced.

**Its ceiling is declared rather than discovered.** It reads the direct join, so an intermediate
variable, an `os.path.join`, or a root passed into a function is invisible. **It needs a live
instrument case**, because a check that finds zero for the wrong reason is what this whole directory
exists to avoid — `test_build_artifacts_ignored`'s first version passed three of four assertions
against a `git check-ignore` that said yes to everything.

## What this record does not settle

**Whether `main_repo_root` should be held at all.** Ruling 1 refuses one instrument for it and
ruling 6 supplies a narrower one; neither establishes that the pointer-file walk itself is correct
for every tree shape it can meet.

**The blanket handler's remaining routes.** Ruling 4 changes the direction, not the set. What can
raise inside `analyze` after ruling 3 lands is not enumerated here.

**Whether `errors="replace"` is right for a path listing.** A replaced byte in a filename makes a
tracked path silently unmatchable, so a citation to it would report unresolved. Ruling 3 keeps the
publication moving and the row honest; it does not claim the substituted path is usable.
