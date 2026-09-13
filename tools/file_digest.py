"""Streamed fingerprints of raw file bytes."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    """Return the lowercase SHA-256 hex digest of ``path``'s raw bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    """Return the lowercase SHA-256 hex digest of an already captured payload."""
    return hashlib.sha256(payload).hexdigest()


def write_recorded_sha256(path: Path, digest: str) -> None:
    """Write one retained fingerprint in the shared on-disk format."""
    path.write_text(digest + "\n", encoding="ascii")


def recorded_sha256(path: Path) -> str | None:
    """Read a retained ASCII fingerprint, or return ``None`` when unreadable."""
    try:
        return path.read_text(encoding="ascii").strip()
    except (OSError, UnicodeError):
        return None
