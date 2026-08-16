# CI runs the suite at the merge, advisory, and says which PHI layers it could not run

`CLAUDE.md` ruled CI out in one breath with two other things — *"Stdlib only — no package manager, no lockfile, no CI in this repo, and the census is not worth introducing any."* **Those three were never coupled.** The reason written down was about dependency machinery, and CI here carries none: checkout, `setup-python`, one stdlib command. This reverses that clause and leaves the other two standing.

**What CI buys is not detection. It is the guarantee that the detection ran.** The pre-commit hook does not fire on an automatic merge commit at all, and where a merge is hand-resolved the result is a tree neither parent ever had, so `main` can hold a combination nobody ran the suite against. Two branches have already broken it that way:

- `tools/anchor_scan.py` (#124) and the `console_codec` rule (#150) merged an hour apart. Both branches green; the merged tree failed `anchor_scan.py does not import the helper`. `main` was broken about ten minutes and was found only because somebody ran the suite by hand afterwards, having been told to align a checkout.
- `tools/block_scan.py` (#120), the same defect one merge later, on the mechanism built to stop it.

A third merge (#179) had 66 tests that neither side had run, and was green — a near-miss, and identical in kind: nothing required the merged tree to be run either way.

## Considered options

**Leave it as it is, and rewrite the bundled sentence with the real reason.** Rejected. The reason would have had to be *the discretionary passes keep finding things*, and they do — but two of the three recorded instances were caught by luck, and the case rests on a habit rather than a mechanism.

**A required status check on `main`.** Rejected, and not because it is too strong. It would have blocked the route by which changes actually land here: `03f5adf` merged #142 with `git merge --no-ff` locally and then `git push origin main`, and a required check makes that push impossible — `main` could only change through a PR merged in the browser. This repo runs several agent worktrees in parallel and merges them sequentially from the command line, so that is a change to how the work is done, in exchange for blocking a failure that has so far always been visible once anyone looked. **Advisory chosen**: it delivers the guarantee that the detection ran, which is the whole of the stated value, and costs nothing else. Escalating later is a settings change, not a rewrite.

**Suite only, no PHI scan.** Rejected, but it was close, and the argument against it is the ticket's own trap: *a green check on a PHI scan that cannot see the corpus is worse than no check, because it reads as coverage.* `scratch/` is gitignored PHI and must never reach a runner, so the corpus layer — the layer that catches real patient names — is dead in CI permanently and not occasionally. Two things settle it in favor of scanning anyway. **The shape layer is not worthless**: working #64 it caught a real date of birth copied out of a note into a staged file. And **CI is not the weak configuration, it is the ordinary one** — agents here commit from worktrees, where the corpus layer is already dead (#93), so `phi_scan` in CI is no weaker than `phi_scan` where most of this repo's commits are made.

## Decision

`.github/workflows/checks.yml`, one job, `windows-latest`, Python 3.14, running the suite and `phi_scan --all`. Triggers on `push` to `main`, on `pull_request`, and on `workflow_dispatch`.

**`windows-latest` because CI red must mean the maintainer's machine red.** The platform-shaped code here is Windows-shaped: the cp1252 console defect #150 exists for, and `skills_mirror.py`'s `mklink /J` branch, which is the one this repo actually executes. A Linux runner would exercise the `os.symlink` branch nobody uses. Python 3.14 for the same reason — no consumer runs these tools, so the stated 3.11 floor has nobody behind it, and matching the machine is worth more than proving a floor. *(The floor is 3.10 in any case: `int | None` is PEP 604, and there is no 3.11-or-later syntax anywhere in `tools/` — checked, not assumed.)*

**Both triggers, because `main` is reached two ways.** `pull_request` checks out the merge result rather than the branch head, which is the tree this ADR is about; `push` to `main` catches the local-merge-and-push route that `pull_request` never sees.

**The PHI step states its own coverage, and the statement is derived rather than typed.** `phi_scan.py --layers` prints, from the scanner's own inputs, which of the path, corpus and shape layers ran — and adds `A clean result here is NOT "no PHI"` whenever one did not. The job prints it into the step summary, so it is on the page the checkmark is attached to. A banner written into the YAML would have been a claim about `phi_scan` that `phi_scan` does not make and nothing re-derives, which is #143.

## Consequences

**A green check still means less than it looks like, and now says so.** In CI the report reads:

```
phi-scan layers (--all):
  path layer     NOT RUN  -- --all walks tracked files; nothing can be staged from a gitignored directory
  corpus layer   NOT RUN  -- no corpus under scratch/; PATIENT NAMES ARE NOT CHECKED
  shape layer    ACTIVE   -- dob, SSN, phone, MRN, US-style short date
  ** A clean result here is NOT "no PHI": the path and corpus layers did not run. **
```

That is two of three layers dark, permanently, on the rule that matters most. **The report does not fix it — it makes it unreadable as coverage**, which is the most that was available.

**Most of this repo is still ungraded by anything here.** Skill rules, drift rows and `assertions.md` are graded by reading; ADR 0001 exists because of that. CI will not grade a note, will not catch a rule contradicting another skill, and cannot see `.claude/skills/` drift, because the mirror is gitignored. Standing rule 4 is greppable and `spelling_scan.py` now exists with its mention-versus-use rule, but running it in CI would change its posture from advisory to blocking and was left out of scope.

**A malformed workflow is the failure mode this ADR is most exposed to, and it is only half-guarded.** A syntax error means GitHub declines to run the job, so the PR page shows **no failing check at all** rather than a red one — the silent-absence failure this ADR is about, arriving through the mechanism built to fix it. `tools/test_ci_workflow.py` answers it in two tiers, because `tools/` is stdlib only and the cost argument above depends on that. The floor reads the file as text and runs everywhere, pinning the runner, the Python version, the test command and the PHI step's honesty against `CLAUDE.md`, and catching tab characters. Above it, `TheFileIsValidYaml` parses and checks the job's shape **when PyYAML happens to be importable, and skips when it is not** — which validates on the machine the commit is made from and skips on the runner, where the check would be circular anyway. **On a machine without PyYAML the tab test is the whole guard**, and neither tier can tell you the job passed. The first push is still the only end-to-end check.

**A `pull_request` run can go green on a stale merge.** GitHub recomputes the merge commit when the branch moves, not when `main` moves — so a PR opened before another lands and merged after it can be green about a merge that no longer exists. That is exactly the `anchor_scan` / `console_codec` shape. The `push` trigger on `main` catches it on the way in rather than before, which is a narrower guarantee than it first appears and is why "require branches to be up to date" would be the first thing to turn on if this is ever escalated.

**Nothing pins the action versions, and an unresolvable one fails the same silent way.** `actions/checkout@v7` and `actions/setup-python@v7` were the current majors when this landed, checked against the API rather than assumed. If either reference stops resolving, GitHub produces **no check** rather than a red one — the same failure mode as a malformed file, and neither test tier reaches it, because a test that checked would need the network.

**Three things here go slightly beyond what was ruled, and they are named rather than folded in.** `workflow_dispatch` is a third trigger where the ruling said push and pull_request; a `python -VV` step nobody asked for; and the optional PyYAML import, which is the only place in `tools/` where what a test covers depends on what is installed. Each is argued above and none changes a decision, but a reader comparing the ruling to the file should not have to discover them.

**The layer-reporting requirement was answered for CI and not for the hook, which is where the ticket's own comment aimed it.** That comment observed that *print which layers ran* is not sufficient because `tools/hooks/pre-commit` **already** prints exactly that and exits 0 regardless, and drew the corollary that the requirement *"applies to the local hook too"*. It still does. `phi_scan`'s non-`--layers` path prints the same one-line notice it always did, and worktree commits — which is how agents commit here — still pass with the corpus layer dark. Changing that is a ruling about what refuses a commit, so it was left to #93 rather than taken in passing.

**And the class of defect that has actually hurt most is untouched.** #124's first commit landed with the suite green, `anchor_scan` exiting 0 and `specificity_scan` exiting 0, and a hand sweep then found three real defects: the published figures were 214/83 where the answer was 210/87. Every green signal was correct about what it measured. **The suite is a floor on regressions, not a floor on correctness**, and running it more reliably raises neither.
