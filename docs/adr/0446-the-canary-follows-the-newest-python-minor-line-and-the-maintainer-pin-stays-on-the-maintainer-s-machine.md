# The canary follows the newest Python minor line and the maintainer pin stays on the maintainer's machine

**Measured at:** 6b48549afbefc48a987476357ae0e0a171371ff8

On 2026-11-11 the clinician asked for every dependency the repository uses to be pinned to its
newest release. That pass pinned ruff, mypy, pip, PyMuPDF, the case-video packages, the GitHub
Actions and the engineering skills. Python was the one pin with a standing ruling behind it,
[ADR 0431](0431-the-maintainer-ci-job-pins-the-exact-python-release-and-a-canary-job-runs-the-newest-one.md),
so it was asked as its own question. The freshness gate read `FRESH` against `main` before this
record was written.

## Measured before ruling

The maintainer pin in `.github/maintainer-python-version` read `3.14.4`. The newest CPython release
tags were `v3.14.10` on the 3.14 line and `v3.15.2` overall, read from the `python/cpython`
repository's tags. The canary job requested `'3.14'`, so it could no longer warn about the newest
released Python: 3.15 had shipped and no job ran it.

## Ruling 1 — the canary runs the newest Python minor line, and the pin stays

Offered three choices (pin 3.15.2 and upgrade the machine, pin 3.14.10 and update the machine, or
keep 3.14.4 and move only the canary), the clinician kept the pin at 3.14.4. The canary now requests
`'3.15'` and runs `python tools/suite.py` on the newest release of that line. ADR 0431's reason for
the pin stands unchanged: a red maintainer job means the maintainer's machine would go red. The
canary's reason now reaches the line it exists for, because a warning about newer Python that skips
the newest released minor line warns about nothing past the pin's own line.

When a newer minor line ships, the canary's request moves to it; the pin moves only when the
maintainer's machine does.

## Supersedes

- [ADR 0431](0431-the-maintainer-ci-job-pins-the-exact-python-release-and-a-canary-job-runs-the-newest-one.md) ruling 1, the canary limb only: the canary follows the newest released Python minor line, 3.15 at this record, and the maintainer pin stays 3.14.4.

## Consequences

- `checks.yml`: the canary requests `'3.15'`, and its job name and suite step name 3.15.
- `tools/test_ci_workflow.py` and `docs/agents/issue-tracker.md`: the canary's fixed job name names
  3.15.
- `CLAUDE.md`, section *Continuous integration*: the canary is named as floating on 3.15.
- The 3.10 floor job keeps requesting `'3.10'` under ADR 0431 ruling 4, and
  `.github/maintainer-python-version` keeps `3.14.4`.
