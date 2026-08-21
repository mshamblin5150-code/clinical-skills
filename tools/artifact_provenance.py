"""Identity and trust checks for shared, out-of-repo build artifacts.

A clean artifact is reusable at a descendant commit when its caller names the files
that produced it and those files are unchanged. During a merge, either parent is a
valid ancestor; the comparison is still against the merged working tree, so a
changed producer cannot pass through the second parent.
"""

from __future__ import annotations

import subprocess
import warnings
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class UntrustedProvenance(ValueError):
    """An artifact cannot be tied to the checkout that is consuming it."""


@dataclass(frozen=True)
class ProvenanceCheck:
    producer: dict[str, str | bool] | None
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


def _trusted_ancestor(commit: str, repo_root: Path) -> bool:
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
    normalized: dict[str, str | bool] | None = None
    if not isinstance(producer, dict):
        reasons.append("has no producer provenance stamp")
    else:
        commit = producer.get("commit")
        dirty = producer.get("dirty")
        if not isinstance(commit, str) or not commit:
            reasons.append("has no producer commit")
        if not isinstance(dirty, bool):
            reasons.append("has no producer dirty-state flag")
        unchanged_ancestor = (
            isinstance(commit, str)
            and bool(commit)
            and bool(unchanged_paths)
            and _trusted_ancestor(commit, repo_root)
            and _paths_unchanged(commit, unchanged_paths, repo_root)
        )
        if isinstance(commit, str) and commit and commit != expected and not unchanged_ancestor:
            reasons.append(f"was produced by a different commit ({commit}; current is {expected})")
        if dirty is True:
            reasons.append("was produced by a dirty checkout")
        if isinstance(commit, str) and commit and isinstance(dirty, bool):
            normalized = {"commit": commit, "dirty": dirty}

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
    )
    source_check = check_producer(
        provenance.get("source"),
        f"{artifact} source manifest",
        allow_untrusted=allow_untrusted,
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
