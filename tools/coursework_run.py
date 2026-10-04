"""Shared identity and population policy for graded coursework runs.

Issue #417 joins a submission to the run directory that produced it. That join
is policy several graders must agree on, so its key parser and path populations
live here rather than as similar local predicates.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from types import MappingProxyType
from pathlib import Path

from repo_root import output_root, scratch_root


TRAILING_DATE = re.compile(r"-\d{4}-\d{2}-\d{2}$")


def key_of(stem: str) -> str:
    """Return the assignment key carried by a submission stem.

    A coursework run key omits the sitting date while each submission carries
    one, so the only syntax removed is a trailing ISO date. Companion phase
    tokens do not exist under ``output/``.
    """
    return TRAILING_DATE.sub("", stem)


def runs_root(start: Path | None = None) -> Path:
    """The canonical container for assignment-owned provenance records."""
    return scratch_root(start) / "runs"


def run_for_submission(path: Path | str, start: Path | None = None) -> Path:
    """Return the canonical run directory joined to a dated submission."""
    return runs_root(start) / key_of(Path(path).stem)


def submission_belongs_to_run(submission: Path | str, run: Path | str) -> bool:
    """Whether ``submission`` carries the exact assignment key of ``run``."""
    return key_of(Path(submission).stem) == Path(run).name


def is_run_directory(path: Path | str, start: Path | None = None) -> bool:
    """Whether ``path`` is one direct assignment directory under ``runs_root``."""
    candidate = Path(path).expanduser().resolve()
    return candidate.parent == runs_root(start).resolve()


def is_submission(path: Path | str, start: Path | None = None) -> bool:
    """Whether ``path`` resolves under the main checkout's ``output/`` tree."""
    candidate = Path(path).expanduser().resolve()
    return candidate.is_relative_to(output_root(start).resolve())


# A submission identifies the sitting, not every draft in the run.
FIRST_PROSE = MappingProxyType({
    "peer-critique": ("critique.md",),
    "discussion-reply": ("{key}",),
    "practicum-case-study": ("output/case-studies/{stem}.md",),
    "discussion-post": ("post.md",),
    "course-assignment": (
        "writer/{key}/**/*.pptx", "writer/{key}/**/*.json",
        "output/course-assignments/{stem}.pptx",
        "output/course-assignments/{stem}.docx",
    ),
})


def submission_keys(submission: str) -> tuple[str, ...]:
    keys = tuple(submission.split(","))
    if not keys or any(
        not key or key in {".", ".."} or any(char in key for char in "/\\*?[]:")
        for key in keys
    ):
        raise ValueError("submission needs a filename or stem, without a directory")
    if len(set(keys)) != len(keys):
        raise ValueError("submission keys are duplicated")
    return keys


def draft_files(run: Path, key: str, start: Path | None = None) -> tuple[Path, ...]:
    """Enumerate mapped prose and keyed staging in both relevant scratch roots."""
    submission_keys(key)
    stem = Path(key).stem if key.endswith((".md", ".pptx", ".docx")) else key
    if key == "critique.md":
        skill = "peer-critique"
    elif key.startswith("response-") and key.endswith(".md"):
        skill = "discussion-reply"
    elif key_of(stem).endswith("-case-study"):
        skill = "practicum-case-study"
    elif key_of(stem).endswith("-course-assignment"):
        skill = "course-assignment"
    elif key_of(stem).endswith("-discussion") or run.name.endswith("-discussion"):
        skill = "discussion-post"
    else:
        raise ValueError("submission has no mapped coursework first-prose location")
    found = set()
    for template in FIRST_PROSE[skill]:
        pattern = template.format(key=key, stem=stem)
        if pattern.startswith("output/"):
            candidates = (output_root(start) / pattern.removeprefix("output/"),)
        else:
            candidates = run.glob(pattern)
        found.update(path.resolve() for path in candidates if path.is_file())
    committing = (start or Path(__file__).resolve().parent).resolve().parent / "scratch"
    for root in {committing, scratch_root(start)}:
        for folder in (root / "sessions").glob("*/" + key):
            found.update(path.resolve() for path in folder.rglob("*") if path.is_file())
    return tuple(sorted(found))


def observe_draft(run: Path, key: str, previous: dict) -> dict:
    """Keep the first observation even when subsequent retrieval refreshes."""
    observations = dict(previous)
    if key not in observations:
        observations[key] = {"paths": [str(path) for path in draft_files(run, key)]}
    validate_observations(observations)
    return observations


def validate_observations(observations: object) -> None:
    if not isinstance(observations, dict):
        raise ValueError("draft observations must be an object")
    for key, value in observations.items():
        if not isinstance(key, str):
            raise ValueError("draft observation key is invalid")
        submission_keys(key)
        if not isinstance(value, dict) or set(value) != {"paths"}:
            raise ValueError("draft observation is invalid")
        paths = value["paths"]
        if not isinstance(paths, list) or any(not isinstance(path, str) or not Path(path).is_absolute() for path in paths):
            raise ValueError("draft observation paths are invalid")
        if len(paths) != len(set(paths)):
            raise ValueError("draft observation paths are duplicated")


@dataclass(frozen=True)
class OrderGrade:
    finding: bool
    report: str


def grade_order(
    observations: object, submission: str, waived: Callable[[str, str], bool]
) -> OrderGrade:
    """Grade historical observations; only the confirmed record grants waivers."""
    try:
        validate_observations(observations)
        keys = submission_keys(submission)
    except ValueError:
        return OrderGrade(True, "finding - draft observation shape is invalid")
    missing = [key for key in keys if key not in observations]
    paths = [
        (key, path)
        for key in keys if key in observations
        for path in observations[key]["paths"]
    ]
    waived_keys = {
        key for key in keys
        if key in observations and observations[key]["paths"]
        and all(waived(key, path) for path in observations[key]["paths"])
    }
    late = [path for key, path in paths if key not in waived_keys]
    states = []
    if missing:
        states.append("finding - first draft observation is missing")
    if late:
        states.append("finding - draft present before gate: " + ", ".join(late))
    return OrderGrade(
        bool(states),
        ("; ".join(states) if states else "draft order clean")
        + f"; waived observations: {len(waived_keys)}",
    )
