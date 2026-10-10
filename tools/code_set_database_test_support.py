"""Pin tests that read a Code-set database to its committed bytes."""

from __future__ import annotations

import hashlib
from pathlib import Path


ICD10_DATABASE_SHA256 = "e81230d32601595ebe3cf7d34e0202d31bba740f0804d67a5f26e63a9ae2eb40"
PROCEDURE_CODES_DATABASE_SHA256 = (
    "3e8f3d60c554f3582bfb817bb79ead0c649973faacc9c4c8ba5451f31b2bc778"
)


def assert_code_set_database_digest(
    database: Path,
    expected_sha256: str,
    name: str,
) -> None:
    """Fail when a Code-set database no longer has the reviewed bytes."""
    actual_sha256 = hashlib.sha256(database.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        raise AssertionError(
            f"{name} was rebuilt; re-derive this module's hand-typed expectations "
            "before the digest constant moves"
        )
