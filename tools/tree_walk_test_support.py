"""OS-backed boundaries for tests of consumers of the shared directory walk."""

from __future__ import annotations

import contextlib
import os
import subprocess
import unittest
from pathlib import Path


def short_alias(path: Path) -> Path:
    """Return a real Windows short alias, or skip when the volume has none."""
    if os.name != "nt":
        raise unittest.SkipTest("Windows short paths")
    import ctypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    function = kernel.GetShortPathNameW
    function.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
    function.restype = ctypes.c_uint
    buffer = ctypes.create_unicode_buffer(32768)
    size = function(str(path), buffer, len(buffer))
    if not size:
        raise ctypes.WinError(ctypes.get_last_error())
    if size >= len(buffer):
        raise AssertionError("short path exceeds the Windows path buffer")
    alias = Path(buffer.value)
    if alias == path:
        raise unittest.SkipTest("fixture volume provides no distinct short alias")
    return alias


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
