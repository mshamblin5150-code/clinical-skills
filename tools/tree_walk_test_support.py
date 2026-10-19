"""OS-backed boundaries for tests of consumers of the shared directory walk."""

from __future__ import annotations

import contextlib
import os
import subprocess
import unittest
from pathlib import Path


@contextlib.contextmanager
def denied_listing(directory: Path):
    """Deny only directory listing; restore the ACL before fixture cleanup."""
    if os.name != "nt":
        raise unittest.SkipTest("Windows icacls directory denial")
    principal = subprocess.run(
        ["whoami"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
    ).stdout.strip()
    result = subprocess.run(
        ["icacls", str(directory), "/deny", f"{principal}:(RD)", "/Q"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode:
        raise unittest.SkipTest(f"icacls denial unavailable: {result.stderr.strip()}")
    try:
        try:
            with os.scandir(directory) as entries:
                list(entries)
        except PermissionError:
            pass
        else:
            raise AssertionError("icacls did not deny directory listing")
        yield
    finally:
        restored = subprocess.run(
            ["icacls", str(directory), "/remove:d", principal, "/Q"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if restored.returncode:
            raise AssertionError(f"could not restore fixture ACL: {restored.stderr.strip()}")


def junctions(root: Path, target: Path) -> tuple[Path, ...]:
    """Create live, dangling, and ancestor junctions below a fixture root."""
    if os.name != "nt":
        raise unittest.SkipTest("Windows junctions")
    paths = []
    for name, destination in (
        ("live-junction", target),
        ("dangling-junction", root / "absent-junction-target"),
        ("ancestor-junction", root),
    ):
        path = root / name
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(path), str(destination)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode:
            raise AssertionError(f"junction fixture failed: {result.stderr.strip()}")
        paths.append(path)
    return tuple(paths)
