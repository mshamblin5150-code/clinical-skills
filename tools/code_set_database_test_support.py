"""Pin tests that read a Code-set database to its committed bytes."""

from __future__ import annotations

import hashlib
from pathlib import Path


ICD10_DATABASE_SHA256 = "4e56add067465da8ffc8cf88cf6a2222ea94b3e9fedc8738b2c3d38d1612fd92"
PROCEDURE_CODES_DATABASE_SHA256 = (
    "d7fe46bed1826393494b686a39314e72f641391aabd73dfebf3ad54e4bcf7eba"
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
