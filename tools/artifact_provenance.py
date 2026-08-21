"""Identity and trust checks for shared, out-of-repo build artifacts.

A clean artifact is reusable at a descendant commit when its caller names the files
that produced it and those files are unchanged. During a merge, either parent is a
valid ancestor; the comparison is still against the merged working tree, so a
changed producer cannot pass through the second parent.
"""

from __future__ import annotations

import hashlib
import subprocess
import warnings
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class UntrustedProvenance(ValueError):
    """An artifact cannot be tied to the checkout that is consuming it."""


@dataclass(frozen=True)
class ProvenanceCheck:
    producer: dict[str, object] | None
    reasons: tuple[str, ...]

    @property
    def trusted(self) -> bool:
        return not self.reasons


def current_producer(repo_root: Path = REPO_ROOT) -> dict[str, str | bool]:
    """Return the commit and dirty state of the checkout running a producer."""
    commit = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain", "--untracked-files=normal"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout
    )
    return {"commit": commit, "dirty": dirty}


def _is_checkout_ancestor(commit: str, repo_root: Path) -> bool:
    """Whether ``commit`` belongs to either side of the checkout's live history."""
    candidates = ["HEAD", "MERGE_HEAD"]
    return any(
        subprocess.run(
            ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", commit, candidate],
            capture_output=True,
        ).returncode
        == 0
        for candidate in candidates
    )


def _paths_unchanged(commit: str, paths: tuple[str, ...], repo_root: Path) -> bool:
    """Whether the checkout is running the producer paths recorded by ``commit``."""
    return (
        subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--quiet", commit, "--", *paths],
            capture_output=True,
        ).returncode
        == 0
    )


def _content_inputs(
    value: object, repo_root: Path, required_paths: tuple[str, ...] = ()
) -> tuple[bool | None, list[dict[str, str]]]:
    """Whether an explicit producer-file identity matches this checkout."""
    if value is None:
        return None, []
    if not isinstance(value, list) or not value:
        return False, []
    normalized: list[dict[str, str]] = []
    for row in value:
        if not isinstance(row, dict):
            return False, []
        relative = row.get("path")
        expected = row.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            return False, []
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            return False, []
        target = (repo_root / path).resolve()
        if not target.is_relative_to(repo_root.resolve()) or not target.is_file():
            return False, []
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != expected:
            return False, []
        normalized.append({"path": path.as_posix(), "sha256": expected})
    recorded_paths = {row["path"] for row in normalized}
    if not {Path(path).as_posix() for path in required_paths} <= recorded_paths:
        return False, []
    return True, normalized


def check_producer(
    producer: object,
    artifact: Path | str,
    *,
    allow_untrusted: bool = False,
    expected_commit: str | None = None,
    repo_root: Path = REPO_ROOT,
    unchanged_paths: tuple[str, ...] = (),
) -> ProvenanceCheck:
    """Validate a producer stamp against the checkout consuming the artifact."""
    expected = expected_commit or str(current_producer(repo_root)["commit"])
    reasons: list[str] = []
    normalized: dict[str, object] | None = None
    if not isinstance(producer, dict):
        reasons.append("has no producer provenance stamp")
    else:
        commit = producer.get("commit")
        dirty = producer.get("dirty")
        inputs_match, inputs = _content_inputs(
            producer.get("inputs"), repo_root, unchanged_paths
        )
        if not isinstance(commit, str) or not commit:
            reasons.append("has no producer commit")
        if not isinstance(dirty, bool):
            reasons.append("has no producer dirty-state flag")
        if inputs_match is False:
            reasons.append("producer inputs do not match the current checkout")
        unchanged_ancestor = (
            isinstance(commit, str)
            and bool(commit)
            and bool(unchanged_paths)
            and _is_checkout_ancestor(commit, repo_root)
            and _paths_unchanged(commit, unchanged_paths, repo_root)
        )
        if (
            isinstance(commit, str)
            and commit
            and commit != expected
            and not unchanged_ancestor
            and inputs_match is not True
        ):
            reasons.append(f"was produced by a different commit ({commit}; current is {expected})")
        if (
            isinstance(commit, str)
            and commit == expected
            and unchanged_paths
            and not _paths_unchanged(commit, unchanged_paths, repo_root)
            and inputs_match is not True
        ):
            reasons.append("producer code has changed since the artifact was built")
        if dirty is True:
            reasons.append("was produced by a dirty checkout")
        if isinstance(commit, str) and commit and isinstance(dirty, bool):
            normalized = {"commit": commit, "dirty": dirty}
            if inputs_match is True:
                normalized["inputs"] = inputs

    check = ProvenanceCheck(normalized, tuple(reasons))
    if check.reasons:
        message = f"untrusted artifact {artifact}: " + "; ".join(check.reasons)
        if not allow_untrusted:
            raise UntrustedProvenance(message)
        warnings.warn(message, RuntimeWarning, stacklevel=2)
    return check


def check_derived(
    provenance: object,
    artifact: Path | str,
    *,
    allow_untrusted: bool = False,
) -> ProvenanceCheck:
    """Validate a derived artifact without erasing distrust in its source."""
    if not isinstance(provenance, dict):
        return check_producer(
            None, artifact, allow_untrusted=allow_untrusted
        )

    producer_check = check_producer(
        provenance.get("producer"),
        artifact,
        allow_untrusted=allow_untrusted,
        unchanged_paths=("tools/guidelines_index.py",),
    )
    source_check = check_producer(
        provenance.get("source"),
        f"{artifact} source manifest",
        allow_untrusted=allow_untrusted,
        unchanged_paths=("tools/guidelines_extract.py",),
    )
    inherited = provenance.get("untrusted_reasons")
    reasons: list[str] = []
    if not isinstance(inherited, list):
        reasons.append("has no provenance trust record")
    else:
        reasons.extend(str(reason) for reason in inherited if reason)
    if reasons:
        message = f"untrusted artifact {artifact}: " + "; ".join(reasons)
        if not allow_untrusted:
            raise UntrustedProvenance(message)
        warnings.warn(message, RuntimeWarning, stacklevel=2)
    return ProvenanceCheck(
        producer_check.producer,
        producer_check.reasons + source_check.reasons + tuple(reasons),
    )
