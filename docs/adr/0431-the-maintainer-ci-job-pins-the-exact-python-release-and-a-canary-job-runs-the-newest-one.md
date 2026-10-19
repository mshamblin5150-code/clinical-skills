# The maintainer CI job pins the exact Python release and a canary job runs the newest one

**Measured at:** 592067b0598e89b7fae3429b31459b713ce157e8

[#1890](https://github.com/mshamblin5150-code/clinical-skills/issues/1890) was filed from the
tracker sweep closing #1818's grilling. It found that the maintainer job in
`.github/workflows/checks.yml` asks `setup-python` for `'3.14'`, which installs the newest 3.14 patch
release, while the comment above that request says the job matches the machine the repository is
worked on. Grilled 2026-10-19 against `main` at the commit above, where the freshness gate read
`FRESH`. The clinician ruled every point below in that session, one question at a time. **Nothing is
built here; this is the record the build reads.**

## Measured before ruling

**The claim had stopped being true.** The maintainer's interpreter is 3.14.4, installed by the Python
install manager at `pythoncore-3.14-64`, measured in the grilling session. The CI runner had moved to
3.14.8, recorded on #1818. #1818's test failed twelve times on 3.14.8 and passed on 3.14.4, a
difference that traced to a CPython change between those patch releases (gh-102475, in
`ntpath.realpath`). PR #1900 repaired the test; the policy stayed open.

**The newer release also earned something.** #1818 surfaced gh-102475 before the maintainer's machine
reached it, so the floating request was an early warning as well as a reproducibility defect.

**Three jobs float, not one.** Both jobs in `.github/workflows/tracker.yml` request `'3.14'`. They
grade tracker records and, after a merge, publish receipts and remove the `in flight` label, so a
patch-level change can refuse or block a tracker action that the same command performs locally.

**The workflow comment cites a decision that does not exist.** It cites a third numbered decision of ADR 0002, and
[ADR 0002](0002-ci-runs-the-suite-at-the-merge.md) declares `no-numbered-rulings`. The claim it means
is ADR 0002's paragraph beginning "`windows-latest` because CI red must mean the maintainer's machine
red", whose last sentences say Python 3.14 is chosen for the same reason.

**No committed file records the maintainer's interpreter.** The only place that can derive it is the
maintainer's machine.

## Ruling 1 — the maintainer job pins the exact release, and a canary runs the newest

The maintainer job installs one exact patch release, recorded in one committed file. A second job,
the canary, runs `python tools/suite.py` on the newest 3.14 release on `windows-latest`. The canary's
job name and step summary say that a failure there means a newer Python release breaks the code and
that the maintainer's machine will not show it yet. A red maintainer job again means the maintainer's
machine would go red. Pinning alone was declined because it gives up the early warning #1818
demonstrated. Floating with a narrowed claim was declined because it leaves red runs the maintainer
cannot reproduce and weakens the reason the job exists. Floating with both versions reported was
declined because the expected version must be recorded somewhere, which is the pin without its
guarantee. The canary's cost is one more Windows job per run, which a public repository does not pay
for.

## Ruling 2 — the commit hook says when the local interpreter differs from the pin

The pre-commit hook prints one advisory line when the interpreter running it differs from the pinned
release in major, minor or micro version, and prints nothing when they match. It never changes the
hook's exit status. A pin file it cannot read produces a line saying the comparison was not made,
never silence. The commit boundary was chosen because Claude, Codex and the maintainer all pass
through it, and the repetition until the pin is edited is the reminder to edit it. Session-start
context was declined because only Claude sees it. A test-suite header was declined because a session
that never runs the suite never sees it. Both together was declined as the same fact twice.

## Ruling 3 — the tracker jobs read the same pin

Both jobs in `.github/workflows/tracker.yml` install the release named in the same committed file.
They act on the live tracker, so the same command should behave the same way there as on the
maintainer's machine. The canary already runs the suite that covers their tools on the newest
release. Leaving them floating was declined because a patch-level change could stop a receipt or
refuse a record with no local reproduction. Repeating the number in each job was declined because an
upgrade would then update one copy and miss the others.

## Ruling 4 — the 3.10 floor job keeps requesting the minor version

The floor job's request stays `'3.10'`. Its claim, under
[ADR 0187](0187-the-python-floor-is-two-numbers-held-equal-and-a-job-on-the-floor-settles-it.md), is
a minor-version floor with no machine to match, and the 3.10 line's scheduled end of life is October
2026 under PEP 619, so its newest release has stopped moving. The build records that reason beside
the request. Pinning 3.10.0 was declined because it tests a release almost nobody runs and the runner
may not supply it, so the job could fail for a reason unrelated to the code. Pinning today's newest
3.10 was declined as a guard against drift that has stopped.

## Ruling 5 — a red canary is shown and does not hold a merge

Raised by the tracker sweep closing this grilling and ruled in the same session. The canary runs on
pull requests and its failure turns the run red, but a merge does not wait for it: the merge practice
ADR 0382 relies on, that a merge waits until every check succeeds, names the canary as the one check
allowed to be red. A failure therefore shows where the maintainer already looks without stalling
work on a Python release the maintainer has not installed. Marking the canary `continue-on-error`
was declined because the checkmark stays green and the early warning is easy to miss. Letting it
block like any check was declined because it makes #1818's stall a policy. Running it only on a
schedule and on pushes to `main` was declined because the warning would land where nobody checks.

## Build checklist

- One committed pin file holding the exact release, `3.14.4` at this grilling. It lives under
  `.github/` rather than as a root `.python-version`, because tools that honor a root
  `.python-version`, `uv` among them, would steer a consumer toward the maintainer's patch release
  instead of the declared 3.10 floor.
- `checks.yml`: the maintainer job reads the pin through `setup-python`'s `python-version-file`
  input. Its comment cites this record and ADR 0002's `windows-latest` paragraph by content, not a
  decision number. The canary job is added per ruling 1, runs the suite only, and its step summary
  prints the pinned and installed releases side by side. The floor job's comment carries ruling 4's
  reason.
- `tracker.yml`: both jobs read the pin through the same input.
- `docs/agents/issue-tracker.md`: state ruling 5's merge exception beside the pre-merge checks,
  naming the canary job by its fixed job name, which `tools/test_ci_workflow.py` asserts.
- `tools/hooks/pre-commit`: ruling 2's advisory comparison, from a tools module with a direct
  command that calls `use_utf8()` then `require_python_floor()`.
- `tools/test_ci_workflow.py`: derive the maintainer version from the pin file instead of the
  `PYTHON_VERSION = "3.14"` literal; assert the pin is an exact `3.14.N`; assert the maintainer job and
  both tracker jobs read it; assert the canary floats on `3.14` and runs `python tools/suite.py`;
  assert the floor job still requests `'3.10'`.
- Tests for the comparison through its public command: matching interpreter silent, differing
  interpreter one line, unreadable pin one line, exit status unchanged in all three.
- `CLAUDE.md`, section *Continuous integration*: the sentence "Python 3.14 for the same reason: it
  matches the machine every commit here is made from" names the pin and the canary, and the
  *Console codec* section gains a dated correction naming the new direct command.
- When the maintainer upgrades, the pin file is the one edit, and the hook line is what prompts it.

## What this record does not reach

- **The pin's agreement between commits.** The hook compares only when a commit is made, so an
  upgrade followed by CI runs on an older commit is not reported until the next commit.
- **Differences inside one patch release.** The comparison reads major, minor and micro only; two
  builds of 3.14.4 that differ in compiler or installer are treated as the same.
- **Whether the runner can supply the pinned release.** If `setup-python` cannot install it, the
  maintainer job fails at setup, visibly, rather than at a test.
- **Another contributor's machine.** The hook compares the interpreter that runs it, so any machine
  other than the maintainer's will report a difference; the line is advisory for that reason. Which
  interpreter that is depends on the hook's `python`, `python3`, `py` order on `PATH`; the
  maintainer's machine also has 3.11 installed.
- **A worktree commit before the build reaches the owning checkout.** `core.hooksPath` is absolute
  here, so a worktree commit runs the owning checkout's hook files, and the line appears there only
  once the owning checkout carries this build. #1875's ruled post-commit hook touches the same
  directory; whichever build lands second keeps both.
- **A pin edit on a branch, for the tracker jobs.** Both tracker jobs check out the default branch
  before `setup-python`, so they read the pin as it stands on `main`.
- **The floor job's patch release.** A consumer on an early 3.10 release could lack a fix that a later
  3.10 release carries; ruling 4 accepts that.

[#773](https://github.com/mshamblin5150-code/clinical-skills/issues/773) decision 1 argues against a
macOS job partly because its red runs would not reproduce on the maintainer's machine. This record
repairs that claim for the maintainer job only, and ruling 1 accepts one labeled job whose red is
deliberately not reproducible locally. It rules nothing about macOS.

## Overturned passage

Ruling 1 overturns the words of [ADR 0002](0002-ci-runs-the-suite-at-the-merge.md) that read
"Python 3.14 for the same reason: matching the machine every commit is made from is worth more than
proving a floor." The choice was a minor version; this record replaces it with an exact pinned patch
release plus a canary, so under [ADR 0390](0390-an-overturned-passage-with-no-ruling-number-is-located-by-its-exact-quote-and-a-repair-s-mislabeled-opening-is-restored.md)
ruling 3 it is a supersession, not a correction. ADR 0002's `windows-latest` reasoning and its
advisory posture survive.

ADR 0002 has no numbered rulings. ADR 0390 ruling 1 already rules this case: the exact quote is the
coordinate, and the quoted words occur once in ADR 0002. `tools/test_adr_supersession.py` does not
read that quote form yet; building it is
[#1706](https://github.com/mshamblin5150-code/clinical-skills/issues/1706). Until then the
overturning is stated in this record alone. Whichever lands second, #1706's build or this record's
build, adds the marker beneath that ADR 0002 paragraph and the quote-form `## Supersedes` declaration
here.
