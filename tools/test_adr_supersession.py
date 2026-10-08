"""Bind declared ADR supersessions in both directions; see DECLARED_LIMITS.

Grammar: an optional exact ``## Supersedes`` section contains hyphen bullets,
each beginning with a relative ``[ADR NNNN](NNNN-slug.md)`` link followed by
``ruling N,`` and explanatory prose. Indented continuation lines are joined.
A marker is a paragraph beginning ``*Superseded YYYY-MM-DD.*`` beneath a
``## Ruling N`` heading, or beneath a ``### N.`` heading inside a ``## Ruled``
section of an older record. It contains a quoted span, the same relative ADR link
followed by ``ruling N``, and an account of what survives. The account's truth
is read at review, not inferred from supersession verbs.
"""

from __future__ import annotations

import re
import unittest
from datetime import date
from pathlib import Path

from adr_read import RULING_SECTION, ruling_ordinals
from markdown_read import unfenced_lines
from prose_bind import NAMING, bind


CUTOFF = 280
DECLARED_LIMITS = (
    "An overturning the author never declared is outside this binding.",
    "Whether a marker's account of what survives is true is a review reading.",
    "Markers linked to overturning records below the cutoff are not bound until #1518 lowers it; target records below the cutoff are read for in-scope declarations.",
    "The unsure-pair remainder has not been derived; #1518 fills it in.",
    "Only the documented relative-link, bullet, paragraph, Ruling-heading, and numbered ruling-subheading grammar is read; alternative Markdown forms are not certified.",
)
LINK = r"\[ADR (\d{4})\]\((\d{4}-[^()\s]+\.md)\)"
DECLARATION = re.compile(r"^- " + LINK + r"\s+ruling (\d+),\s+(.+)$")
MARKER_LINK = re.compile(LINK + r"\s+ruling (\d+)\b")
OPENING = re.compile(r"^\*Superseded (\d{4}-\d{2}-\d{2})\.\*\s+(.+)$")
RULING = re.compile(r"^## Ruling (\d+)\b")
NUMBERED_RULING = re.compile(r"^#{3,4}\s+(\d+)\.\s")


def supersession_findings(records: dict[str, str]) -> tuple[str, ...]:
    """Grade an independently supplied complete ADR filename/text population.

    The cutoff belongs to the overturning record, so an old target can still
    owe a marker for a new declaration. This seam writes nothing.
    """
    findings = []
    declarations: set[tuple[str, str, int]] = set()
    markers: set[tuple[str, str, int]] = set()
    for name, text in sorted(records.items()):
        text = "\n".join(unfenced_lines(text))
        if int(name[:4]) < CUTOFF:
            continue
        section = re.search(r"^## Supersedes\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if section is None:
            continue
        bullets = re.split(r"\n(?=- )", section.group(1).strip())
        for bullet in bullets:
            joined = " ".join(line.strip() for line in bullet.splitlines())
            parsed = DECLARATION.fullmatch(joined)
            if parsed is None or parsed.group(1) != parsed.group(2)[:4]:
                findings.append(f"{name}: unread Supersedes declaration")
                continue
            declarations.add((name, parsed.group(2), int(parsed.group(3))))

    for name, text in sorted(records.items()):
        text = "\n".join(unfenced_lines(text))
        ruling = None
        in_ruling_section = False
        for paragraph in re.split(r"\n\s*\n", text):
            heading = RULING.match(paragraph)
            numbered = NUMBERED_RULING.match(paragraph)
            if heading:
                ruling = int(heading.group(1))
                in_ruling_section = False
            elif paragraph.startswith("## "):
                ruling = None
                in_ruling_section = bool(RULING_SECTION.match(paragraph[3:].strip()))
            elif in_ruling_section and numbered:
                ruling = int(numbered.group(1))
            if not paragraph.startswith("*Superseded"):
                continue
            links = list(MARKER_LINK.finditer(paragraph))
            # Old targets with only old links belong to the repair, not this rule.
            if int(name[:4]) < CUTOFF and links and all(
                int(link.group(1)) < CUTOFF for link in links
            ):
                continue
            opening = OPENING.match(" ".join(paragraph.splitlines()))
            valid_date = False
            if opening:
                try:
                    date.fromisoformat(opening.group(1))
                    valid_date = True
                except ValueError:
                    pass
            if not valid_date or ruling is None or not links or not re.search(r'"[^"\n]+"', " ".join(paragraph.splitlines())):
                findings.append(f"{name}: unread supersession marker")
                continue
            for link in links:
                if link.group(1) != link.group(2)[:4]:
                    findings.append(f"{name}: marker link number disagrees with path")
                    continue
                if int(link.group(3)) not in ruling_ordinals(records.get(link.group(2), "")):
                    findings.append(f"{name}: marker links an absent overturning ruling")
                markers.add((link.group(2), name, ruling))

    for declaring, target, ruling in sorted(declarations - markers):
        findings.append(f"{declaring}: {target} ruling {ruling} has no matching marker")
    for declaring, target, ruling in sorted(markers - declarations):
        findings.append(f"{target}: {declaring} does not declare ruling {ruling}")
    return tuple(findings)


class SupersessionBindingTests(unittest.TestCase):
    def test_declared_limits_are_named_without_copying_rows(self) -> None:
        self.assertEqual(bind(DECLARED_LIMITS, __doc__, mode=NAMING), ())

    def paired_records(self) -> dict[str, str]:
        return {
            "0280-new.md": '## Ruling 1 — new practice\n\nNew words.\n\n## Supersedes\n\n- [ADR 0135](0135-old.md)\n  ruling 8, its practice "Old words." The verdict stands.\n',
            "0135-old.md": '## Ruling 8 — practice\n\nOld words.\n\n*Superseded 2026-10-03.* The practice "Old words." is replaced by [ADR 0280](0280-new.md) ruling 1. The verdict stands.\n',
        }

    def test_declared_pair_is_green(self) -> None:
        self.assertEqual(supersession_findings(self.paired_records()), ())

    def test_committed_adr_population_is_bound(self) -> None:
        directory = Path(__file__).resolve().parent.parent / "docs" / "adr"
        records = {path.name: path.read_text(encoding="utf-8") for path in directory.glob("[0-9][0-9][0-9][0-9]-*.md")}
        self.assertTrue(any(int(name[:4]) >= CUTOFF for name in records))
        self.assertEqual(supersession_findings(records), ())

    def test_declaration_without_marker_is_red(self) -> None:
        records = {
            "0280-new.md": '## Supersedes\n\n- [ADR 0135](0135-old.md) ruling 8, its practice "Old words." The verdict stands.\n',
            "0135-old.md": '## Ruling 8 — practice\n\nOld words.\n',
        }
        self.assertTrue(any("no matching marker" in row for row in supersession_findings(records)))

    def test_marker_linking_a_record_declaring_nothing_is_red(self) -> None:
        records = self.paired_records()
        records["0280-new.md"] = '## Ruling 1 — new practice\n\nNew words.\n'
        self.assertTrue(any("does not declare ruling 8" in row for row in supersession_findings(records)))

    def test_old_corrected_opening_cannot_discharge_a_declaration(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace("*Superseded", "*Corrected")
        self.assertTrue(any("no matching marker" in row for row in supersession_findings(records)))

    def test_a_marker_under_the_wrong_target_ruling_is_red_in_both_directions(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace("## Ruling 8", "## Ruling 7")
        rows = supersession_findings(records)
        self.assertTrue(any("no matching marker" in row for row in rows))
        self.assertTrue(any("does not declare ruling 7" in row for row in rows))

    def test_a_missing_overturning_ruling_is_red(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace("ruling 1.", "ruling 9.")
        self.assertTrue(any("absent overturning ruling" in row for row in supersession_findings(records)))

    def test_the_cutoff_excludes_old_overturnings_but_not_old_targets(self) -> None:
        records = {name.replace("0280", "0279"): text.replace("0280", "0279") for name, text in self.paired_records().items()}
        self.assertEqual(supersession_findings(records), ())

    def test_a_numbered_subheading_in_a_ruled_section_carries_a_marker(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace(
            "## Ruling 8 — practice", "## Ruled 2026-09-12\n\n### 8. Practice"
        )
        self.assertEqual(supersession_findings(records), ())

    def test_a_numbered_subheading_outside_a_ruled_section_carries_no_marker(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace(
            "## Ruling 8 — practice", "## Measured before ruling\n\n### 8. Practice"
        )
        self.assertTrue(
            any("unread supersession marker" in row for row in supersession_findings(records))
        )

    def test_an_unread_declaration_is_a_finding(self) -> None:
        records = self.paired_records()
        records["0280-new.md"] = records["0280-new.md"].replace("- [ADR", "* [ADR")
        self.assertTrue(any("unread Supersedes" in row for row in supersession_findings(records)))


if __name__ == "__main__":
    unittest.main()
