"""Lossless readers for Git output whose records carry repository paths.

Git stores paths as bytes.  These readers require NUL-delimited output, split
the bytes first, and decode each record with ``surrogateescape`` so distinct
path byte strings cannot collapse during text decoding.
"""

from __future__ import annotations

from pathlib import Path
import subprocess


class GitPathError(Exception):
    """Git could not provide a complete path population."""


def _run(
    repo: Path,
    arguments: tuple[str, ...],
    *,
    stdin: bytes | None = None,
    accepted_returncodes: tuple[int, ...] = (0,),
) -> bytes:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repo,
            input=stdin,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise GitPathError(f"git {arguments[0]}: {exc}") from exc
    if completed.returncode not in accepted_returncodes:
        first = completed.stderr.decode("utf-8", errors="replace").strip().splitlines()
        raise GitPathError(
            f"git {arguments[0]}: {first[0] if first else 'failed'}"
        )
    return completed.stdout


def read_path_records(
    repo: Path,
    *arguments: str,
    stdin: bytes | None = None,
    accepted_returncodes: tuple[int, ...] = (0,),
) -> tuple[str, ...]:
    """Read NUL-delimited path-bearing records without losing path bytes."""
    if "-z" not in arguments:
        raise ValueError("a path-listing git command must request -z output")
    raw = _run(
        repo,
        tuple(arguments),
        stdin=stdin,
        accepted_returncodes=accepted_returncodes,
    )
    return tuple(
        record.decode("utf-8", errors="surrogateescape")
        for record in raw.split(b"\0")
        if record
    )


def read_rev_list_objects(repo: Path, *revisions: str) -> tuple[tuple[str, str], ...]:
    """Read ``rev-list --objects`` as ``(object id, path)`` records.

    Under ``-z``, Git prefixes path-bearing records with ``path=``.  An object
    with no path remains a bare hexadecimal object id.
    """
    records = read_path_records(repo, "rev-list", "-z", "--objects", *revisions)
    parsed: list[tuple[str, str]] = []
    for record in records:
        if record.startswith("path="):
            if not parsed:
                raise GitPathError("git rev-list: path record has no object id")
            object_id, _ = parsed[-1]
            parsed[-1] = (object_id, record.removeprefix("path="))
        else:
            parsed.append((record, ""))
    return tuple(parsed)
