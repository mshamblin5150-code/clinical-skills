"""Streamed fingerprints of raw file bytes."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from console_codec import require_python_floor, use_utf8


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


def main(argv: list[str]) -> int:
    """Print one raw-byte fingerprint, or a readable refusal."""
    if len(argv) != 1:
        print("usage: python tools/file_digest.py <file>", file=sys.stderr)
        return 2
    path = Path(argv[0]).expanduser()
    try:
        digest = sha256(path)
    except OSError:
        spelling = argv[0]
        if len(spelling) >= 3 and spelling[0] == "/" and spelling[1].isascii() and spelling[1].isalpha() and spelling[2] == "/":
            path = Path(spelling[1] + ":/" + spelling[3:])
            try:
                digest = sha256(path)
            except OSError:
                print(f"file digest: cannot read {argv[0]}", file=sys.stderr)
                return 2
        else:
            print(f"file digest: cannot read {argv[0]}", file=sys.stderr)
            return 2
    print(digest)
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
