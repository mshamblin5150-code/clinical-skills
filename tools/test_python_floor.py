"""Regression checks for the repository's stated Python floor."""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path, PurePosixPath

import test_console_codec
from git_paths import read_path_records


REPO_ROOT = Path(__file__).resolve().parent.parent

# This object declares the check's ceiling: a portable path containing a
# directory separator or filename dot, followed by a positive decimal
# coordinate. Bare words before a colon are not path-shaped.
PATH_COORDINATE_CEILING = re.compile(
    r"(?<![\w./:-])(?:"
    r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+"
    r"|[A-Za-z_][A-Za-z0-9_-]*\.[A-Za-z][A-Za-z0-9_.-]*"
    r"):[1-9][0-9]*\b"
)
FENCE = re.compile(
    r"^(?:(?:[ ]{0,3}>[ ]?)+)?"
    r"(?:[ \t]*(?:[-+*]|[0-9]+[.)])[ \t]+)?"
    r"[ \t]*(`{3,}|~{3,})(.*)$"
)


def prose_outside_fences(text: str) -> str:
    """Return prose outside Markdown fences while preserving line positions."""

    kept: list[str] = []
    marker = ""
    width = 0
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line)
        if not marker:
            if match:
                marker = match.group(1)[0]
                width = len(match.group(1))
                kept.append("\n" if line.endswith("\n") else "")
            else:
                kept.append(line)
            continue
        if (
            match
            and match.group(1)[0] == marker
            and len(match.group(1)) >= width
            and not match.group(2).strip()
        ):
            marker = ""
            width = 0
        kept.append("\n" if line.endswith("\n") else "")
    return "".join(kept)


def tracked_prose(root: Path) -> tuple[str, ...]:
    """Return tracked Markdown outside ``docs/adr/``.

    A clean walk means no tracked Markdown file in that scope carries a line
    coordinate. An untracked or unstaged file is invisible until it enters the
    index.
    """

    return tuple(
        relative
        for relative in read_path_records(
            root, "ls-files", "--cached", "-z", "--", "*.md"
        )
        if PurePosixPath(relative).parts[:2] != ("docs", "adr")
    )


def calls_zip_strict(source: str) -> bool:
    """Return whether source calls the built-in-shaped ``zip(strict=)`` API."""

    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "zip"
        and any(keyword.arg == "strict" for keyword in node.keywords)
        for node in ast.walk(ast.parse(source))
    )


class TheCoordinateInstrumentIsLive(unittest.TestCase):
    def test_inline_code_is_read(self):
        text = "The anchor is `tools/hooks/pre-commit:12`."
        self.assertIsNotNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_fenced_output_is_exempt(self):
        text = "before\n```text\ntools/example.py:12\n```\nafter\n"
        self.assertIsNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_a_block_quoted_fence_is_exempt(self):
        text = "> ```text\n> tools/example.py:12\n> ```\n"
        self.assertIsNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_a_list_continuation_fence_is_exempt(self):
        text = (
            "10. item\n"
            "    ```text\n"
            "    tools/hooks/pre-commit:12\n"
            "    ```\n"
        )
        self.assertIsNone(PATH_COORDINATE_CEILING.search(prose_outside_fences(text)))

    def test_a_real_tracked_member_with_an_injected_coordinate_is_refused(self):
        source = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        mutant = source + "\nThe injected anchor is `tools/hooks/pre-commit:12`.\n"
        matches = PATH_COORDINATE_CEILING.findall(prose_outside_fences(mutant))
        self.assertIn("tools/hooks/pre-commit:12", matches)


class TrackedProseHasNoLineCoordinates(unittest.TestCase):
    def test_the_tracked_population_is_zero(self):
        findings: list[str] = []
        for relative in tracked_prose(REPO_ROOT):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8", errors="replace")
            for match in PATH_COORDINATE_CEILING.finditer(prose_outside_fences(text)):
                findings.append(f"{relative}: {match.group(0)}")
        self.assertEqual([], findings)


class TheStatedFloorHasEvidence(unittest.TestCase):
    def test_non_test_tooling_calls_zip_strict(self):
        sources = (
            path.read_text(encoding="utf-8")
            for path in sorted((REPO_ROOT / "tools").glob("*.py"))
            if not path.name.startswith("test_")
        )
        self.assertTrue(
            any(calls_zip_strict(source) for source in sources),
            "no non-test module under tools/ calls zip(strict=)",
        )

    def test_main_guard_evaluates_its_pep_604_return_annotation(self):
        self.assertEqual(
            ast.If | None,
            test_console_codec.main_guard.__annotations__.get("return"),
        )


if __name__ == "__main__":
    unittest.main()
