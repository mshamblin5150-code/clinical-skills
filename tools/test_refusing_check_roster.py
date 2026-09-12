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
STATUS_ASSIGNMENT = re.compile(r"(?<![A-Za-z0-9_])status\s*=\s*1(?![0-9])")
TOOL_STEM = re.compile(r"\$repo_root/tools/(?P<stem>[a-z0-9_]+)\.py")
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
    stems = []
    for index, line in refusing_lines(hook):
        matches = TOOL_STEM.findall(line)
        if len(matches) != 1:
            raise AssertionError(
                f"refusing line {index + 1} produced {len(matches)} tool stems"
            )
        stems.append(matches[0])
    return tuple(stems)


def refusing_lines(hook: str) -> tuple[tuple[int, str], ...]:
    return tuple(
        (index, line)
        for index, line in enumerate(hook.splitlines())
        if not line.lstrip().startswith("#") and STATUS_ASSIGNMENT.search(line)
    )


def marker_assignments(hook: str) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Pair every refusing line with its nearest preceding inventory marker."""

    lines = hook.splitlines()
    refusing = [index for index, _line in refusing_lines(hook)]
    markers = [
        index
        for index, line in enumerate(lines)
        if ORDINAL_MARKER.match(line) or RULE_ONE_MARKER.match(line)
    ]
    assignments = []
    for index in refusing:
        preceding = tuple(marker for marker in markers if marker < index)
        assignments.append((index, preceding[-1:] if preceding else ()))
    return tuple(assignments)


def inventory_findings(hook: str) -> tuple[str, ...]:
    findings = []
    lines = hook.splitlines()
    assignments = marker_assignments(hook)
    if not assignments:
        findings.append("no refusing lines")
    for index, markers in assignments:
        if not markers:
            findings.append(f"refusing line {index + 1} has no comment")
    used = [markers[0] for _index, markers in assignments if markers]
    for marker in sorted(set(used)):
        if used.count(marker) > 1:
            findings.append(f"comment line {marker + 1} is shared")
    declared = {
        index
        for index, line in enumerate(lines)
        if ORDINAL_MARKER.match(line) or RULE_ONE_MARKER.match(line)
    }
    for marker in sorted(declared - set(used)):
        findings.append(f"comment line {marker + 1} has no refusing line")
    for index in sorted(declared):
        line = lines[index]
        if ORDINAL_MARKER.match(line) and not re.search(r"\*\* #[0-9]+\b", line):
            findings.append(f"ordinal comment line {index + 1} names no ticket")
    for index, markers in assignments:
        if not markers:
            continue
        stems = TOOL_STEM.findall(lines[index])
        if stems == ["phi_scan"] and not RULE_ONE_MARKER.match(lines[markers[0]]):
            findings.append(f"phi_scan line {index + 1} lacks its standing rule 1 comment")
        if stems and stems != ["phi_scan"] and not ORDINAL_MARKER.match(lines[markers[0]]):
            findings.append(f"refusing line {index + 1} lacks an ordinal comment")
    return tuple(findings)


def paragraph_containing(text: str, anchor: str) -> str:
    paragraphs = re.split(r"(?:\r?\n){2,}", text)
    matches = tuple(paragraph for paragraph in paragraphs if anchor in paragraph)
    if len(matches) != 1:
        raise AssertionError(f"expected one paragraph for {anchor!r}, found {len(matches)}")
    return matches[0]


def document_findings(
    path: Path,
    text: str,
    stems: tuple[str, ...],
    rules: tuple[SurfaceRule, ...] = SURFACE_RULES,
) -> tuple[str, ...]:
    findings = []
    if "tools/hooks/pre-commit" not in text:
        findings.append("missing tools/hooks/pre-commit pointer")
    applicable = tuple(rule for rule in rules if rule.path == path)
    if not applicable:
        findings.append("document has no graded membership surface")
    for rule in applicable:
        try:
            prose = paragraph_containing(text, rule.anchor)
        except AssertionError as error:
            findings.append(str(error))
            continue
        disallowed = tuple(stem for stem in stems if stem not in rule.allowed_stems)
        findings.extend(leaf for leaf, _occurrences in bind(disallowed, prose, mode=NAMING))
    return tuple(findings)


class TheHookGradesItsRefusingCheckInventory(unittest.TestCase):
    def test_each_refusing_line_has_exactly_one_unshared_comment(self):
        hook = HOOK.read_text(encoding="utf-8")
        self.assertEqual((), inventory_findings(hook))

    def test_a_refusing_line_without_a_comment_fails_the_contract(self):
        self.assertEqual(
            ("refusing line 1 has no comment",),
            inventory_findings("some_command || status=1\n"),
        )

    def test_two_refusing_lines_cannot_share_one_comment(self):
        hook = '# **The second refusing check.** #83\n"$python" "$repo_root/tools/one.py" || status=1\n'
        hook += '"$python" "$repo_root/tools/two.py" || status=1\n'
        self.assertEqual(("comment line 1 is shared",), inventory_findings(hook))

    def test_a_gap_in_arrival_ordinals_is_valid(self):
        hook = '# **The second refusing check.** #83\n"$python" "$repo_root/tools/one.py" || status=1\n'
        hook += '# **The fourth refusing check.** #689\n"$python" "$repo_root/tools/two.py" || status=1\n'
        self.assertEqual((), inventory_findings(hook))

    def test_phi_scan_uses_the_standing_rule_one_comment(self):
        hook = '# **The second refusing check.** #93\n"$python" "$repo_root/tools/phi_scan.py" || status=1\n'
        self.assertEqual(
            ("phi_scan line 2 lacks its standing rule 1 comment",),
            inventory_findings(hook),
        )


class DeclaredProseSurfacesPointWithoutCopying(unittest.TestCase):
    def test_each_surface_points_to_the_hook_and_copies_no_member(self):
        hook = HOOK.read_text(encoding="utf-8")
        stems = refusing_stems(hook)
        self.assertTrue(stems)
        for path in GRADED_SURFACES:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertEqual(
                    (),
                    document_findings(path, path.read_text(encoding="utf-8"), stems),
                )

    def test_a_missing_pointer_fails(self):
        path = Path("sample.md")
        rules = (SurfaceRule(path, "Membership"),)
        self.assertEqual(
            ("missing tools/hooks/pre-commit pointer",),
            document_findings(path, "Membership names no inventory.", ("threshold_sheet",), rules),
        )

    def test_a_planted_roster_member_is_caught(self):
        path = Path("sample.md")
        rules = (SurfaceRule(path, "Membership"),)
        findings = document_findings(
            path,
            "Membership: see tools/hooks/pre-commit. The threshold_sheet check refuses.",
            ("threshold_sheet", "threshold_coverage"),
            rules,
        )
        self.assertEqual(("threshold_sheet",), findings)


if __name__ == "__main__":
    unittest.main()
