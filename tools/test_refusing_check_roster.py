"""Keep the pre-commit hook as the sole current inventory of refusing checks.

ADR 0182. Membership is derived from lines that set ``status=1``. Each such
line has one local provenance comment, and the declared prose surfaces point
to the hook without copying any derived member name.
"""

from __future__ import annotations

import re
import unittest
from dataclasses import dataclass
from pathlib import Path

from prose_bind import NAMING, bind


REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / "tools" / "hooks" / "pre-commit"
GRADED_SURFACES = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "tools" / "spelling_scan.py",
)
REFUSING_LINE = re.compile(r'^\s*"\$python" "\$repo_root/tools/(?P<stem>[a-z0-9_]+)\.py".*\|\| status=1\s*$')
ORDINAL_MARKER = re.compile(r"^\s*# \*\*The [a-z]+ refusing check\.\*\*")
RULE_ONE_MARKER = re.compile(r"^\s*# \*\*Standing rule 1's refusing check\.\*\*")


@dataclass(frozen=True)
class SurfaceRule:
    path: Path
    anchor: str
    allowed_stems: tuple[str, ...] = ()


SURFACE_RULES = (
    SurfaceRule(REPO_ROOT / "AGENTS.md", "**A scanner reads the same table**"),
    SurfaceRule(
        REPO_ROOT / "CLAUDE.md",
        "**The spelling scanner is advisory and cannot refuse a commit.**",
    ),
    SurfaceRule(
        REPO_ROOT / "CLAUDE.md",
        "**It can refuse a commit.** Since #429",
        ("threshold_coverage",),
    ),
    SurfaceRule(
        REPO_ROOT / "CLAUDE.md",
        "**It can refuse a commit**, and it is one of",
        ("phi_scan", "scratch_census"),
    ),
    SurfaceRule(
        REPO_ROOT / "CLAUDE.md",
        "After that, `tools/hooks/pre-commit`",
        ("phi_scan", "scratch_census"),
    ),
    SurfaceRule(REPO_ROOT / "tools" / "spelling_scan.py", "- Advisory in the pre-commit hook"),
)


def refusing_stems(hook: str) -> tuple[str, ...]:
    return tuple(
        match.group("stem")
        for line in hook.splitlines()
        if (match := REFUSING_LINE.match(line))
    )


def marker_assignments(hook: str) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Pair every refusing line with markers since the preceding refusing line."""

    lines = hook.splitlines()
    refusing = [index for index, line in enumerate(lines) if REFUSING_LINE.match(line)]
    markers = [
        index
        for index, line in enumerate(lines)
        if ORDINAL_MARKER.match(line) or RULE_ONE_MARKER.match(line)
    ]
    assignments = []
    previous = -1
    for index in refusing:
        assignments.append((index, tuple(marker for marker in markers if previous < marker < index)))
        previous = index
    return tuple(assignments)


def surface_findings(stems: tuple[str, ...], prose: str) -> tuple[str, ...]:
    findings = []
    if "tools/hooks/pre-commit" not in prose:
        findings.append("missing tools/hooks/pre-commit pointer")
    findings.extend(leaf for leaf, _occurrences in bind(stems, prose, mode=NAMING))
    return tuple(findings)


def paragraph_containing(text: str, anchor: str) -> str:
    paragraphs = re.split(r"(?:\r?\n){2,}", text)
    matches = tuple(paragraph for paragraph in paragraphs if anchor in paragraph)
    if len(matches) != 1:
        raise AssertionError(f"expected one paragraph for {anchor!r}, found {len(matches)}")
    return matches[0]


class TheHookGradesItsRefusingCheckInventory(unittest.TestCase):
    def test_each_refusing_line_has_exactly_one_unshared_comment(self):
        hook = HOOK.read_text(encoding="utf-8")
        assignments = marker_assignments(hook)
        self.assertTrue(assignments)
        self.assertTrue(all(len(markers) == 1 for _line, markers in assignments), assignments)
        used = [markers[0] for _line, markers in assignments]
        self.assertEqual(len(used), len(set(used)))
        declared = {
            index
            for index, line in enumerate(hook.splitlines())
            if ORDINAL_MARKER.match(line) or RULE_ONE_MARKER.match(line)
        }
        self.assertEqual(declared, set(used))

    def test_each_ordinal_comment_names_its_ticket(self):
        ordinal_comments = tuple(
            line
            for line in HOOK.read_text(encoding="utf-8").splitlines()
            if ORDINAL_MARKER.match(line)
        )
        self.assertTrue(ordinal_comments)
        for comment in ordinal_comments:
            self.assertRegex(comment, r"\*\* #[0-9]+\b")

    def test_a_refusing_line_without_a_comment_fails_the_contract(self):
        hook = '# **The second refusing check.** #83\n"$python" "$repo_root/tools/one.py" || status=1\n'
        hook += '"$python" "$repo_root/tools/two.py" || status=1\n'
        self.assertEqual(((1, (0,)), (2, ())), marker_assignments(hook))

    def test_two_refusing_lines_cannot_share_one_comment(self):
        hook = '# **The second refusing check.** #83\n"$python" "$repo_root/tools/one.py" || status=1\n'
        hook += '"$python" "$repo_root/tools/two.py" || status=1\n'
        assignments = marker_assignments(hook)
        used = [markers[0] for _line, markers in assignments if markers]
        self.assertNotEqual(len(assignments), len(set(used)))

    def test_a_gap_in_arrival_ordinals_is_valid(self):
        hook = '# **The second refusing check.** #83\n"$python" "$repo_root/tools/one.py" || status=1\n'
        hook += '# **The fourth refusing check.** #689\n"$python" "$repo_root/tools/two.py" || status=1\n'
        self.assertTrue(all(len(markers) == 1 for _line, markers in marker_assignments(hook)))


class DeclaredProseSurfacesPointWithoutCopying(unittest.TestCase):
    def test_each_surface_points_to_the_hook_and_copies_no_member(self):
        hook = HOOK.read_text(encoding="utf-8")
        stems = refusing_stems(hook)
        self.assertTrue(stems)
        for path in GRADED_SURFACES:
            with self.subTest(path=path.relative_to(REPO_ROOT), contract="pointer"):
                self.assertIn("tools/hooks/pre-commit", path.read_text(encoding="utf-8"))
        for rule in SURFACE_RULES:
            with self.subTest(path=rule.path.relative_to(REPO_ROOT), anchor=rule.anchor):
                prose = paragraph_containing(rule.path.read_text(encoding="utf-8"), rule.anchor)
                disallowed = tuple(stem for stem in stems if stem not in rule.allowed_stems)
                self.assertEqual((), bind(disallowed, prose, mode=NAMING))

    def test_a_missing_pointer_fails(self):
        self.assertEqual(
            ("missing tools/hooks/pre-commit pointer",),
            surface_findings(("threshold_sheet",), "This surface names no inventory."),
        )

    def test_a_planted_roster_member_is_caught(self):
        findings = surface_findings(
            ("threshold_sheet", "threshold_coverage"),
            "See tools/hooks/pre-commit. The threshold_sheet check refuses.",
        )
        self.assertEqual(("threshold_sheet",), findings)


if __name__ == "__main__":
    unittest.main()
