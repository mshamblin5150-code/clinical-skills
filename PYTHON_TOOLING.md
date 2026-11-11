# Python development tooling

Ruff and mypy are permanent development dependencies in the PEP 735 `dev`
group in `pyproject.toml`, each pinned to one exact release. This repository is not a distributable Python package.
Consumer commands remain standard-library-only with Python 3.10 as their floor.
The maintainer interpreter pin and existing advisory CI workflow are unchanged.

Create an isolated environment with a working Python interpreter:

    python -I -m venv scratch/python-quality-venv
    scratch/python-quality-venv/Scripts/python -I -m pip install pip==26.3
    scratch/python-quality-venv/Scripts/python -I -m pip install --group dev
    scratch/python-quality-venv/Scripts/python -I -m pip install -r tools/pdf-requirements.txt

The PDF engine is installed beside the dev group because mypy reads its type
information; without it mypy reports the PDF engine's import as unresolved.
On POSIX, use `bin/python` instead of `Scripts/python`. Never use a bare pip
that could install into a global interpreter. The environment lives under the
already ignored scratch directory; do not point checks at scratch itself.
Use isolated mode (`-I`) to prevent machine-level PYTHONPATH settings and user
site packages from leaking into these development commands.

Run advisory, nonmutating checks from the repository root:

    scratch/python-quality-venv/Scripts/python -I -m ruff check --no-cache tools skills
    scratch/python-quality-venv/Scripts/python -I -m mypy

Only maintained Python code in tools and skills is selected. Do not scan private
patient artifacts, licensed reference corpora, or nested worktrees. Static checks
do not execute clinical workflows. Existing lint and typing debt should be reported
and repaired in separately reviewed changes, not hidden with global error ignores
or mass automatic fixes. These tools introduce no required CI gate and do not
replace the existing test suite or clinical review.
