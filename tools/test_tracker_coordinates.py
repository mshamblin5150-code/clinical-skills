"""Behavior checks for the tracker coordinate accompaniment grader."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from datetime import timedelta

import prose_bind
import run_grader
import tracker_coordinates as coordinates
from prose_bind import NAMING, bind, section as markdown_section


REPO_ROOT = Path(__file__).resolve().parent.parent


class ThePublicTextGrade(unittest.TestCase):
    def test_removing_the_anchor_exposes_the_coordinate(self):
        anchored = (
            "`coverage_limbs.append(NO_DIFFERENTIAL_ENTRY)` is at "
            "`tools/differential_scan.py:1484`."
        )
        mutant = "The coverage limb is at `tools/differential_scan.py:1484`."

        self.assertEqual((), coordinates.grade(anchored, "issue #928"))
        self.assertEqual(
            (
                coordinates.Finding(
                    coordinates.UNANCHORED,
                    "issue #928",
                    "tools/differential_scan.py:1484",
                ),
            ),
            coordinates.grade(mutant, "issue #928"),
        )

    def test_the_ruled_anchor_vocabulary_and_window(self):
        clean = (
            "The `named_symbol` remains stable while "
            "`tools/example.py:12` moves.\n"
            "\n"
            "The passage at `tools/example.py:13` says \"return the row\".\n"
            "\n"
            "The output begins at `tools/example.py:14`:\n"
            "\n"
            "```text\n"
            "return the row\n"
            "```\n"
            "\n"
            "The wording at `tools/example.py:15` is:\n"
            "\n"
            "> return the row\n"
            "\n"
            "```text\n"
            "tools/exempt.py:99\n"
            "```\n"
        )

        self.assertIs(
            coordinates.PATH_COORDINATE_CEILING,
            prose_bind.PATH_COORDINATE_CEILING,
        )
        self.assertIs(
            coordinates.prose_outside_fences,
            prose_bind.prose_outside_fences,
        )
        self.assertEqual((), coordinates.grade(clean, "record"))

    def test_coordinates_do_not_anchor_each_other(self):
        text = "Moved from `tools/old.py:12` to `tools/new.py:14`."

        self.assertEqual(
            ["tools/old.py:12", "tools/new.py:14"],
            [row.coordinate for row in coordinates.grade(text, "record")],
        )

    def test_neighboring_list_items_are_distinct_paragraphs(self):
        text = (
            "- `named_symbol` remains at `tools/old.py:12`.\n"
            "- Moved to `tools/new.py:14`."
        )

        self.assertEqual(
            ["tools/new.py:14"],
            [row.coordinate for row in coordinates.grade(text, "record")],
        )

    def test_nested_list_items_are_distinct_but_blockquote_lines_share_a_paragraph(self):
        nested = (
            "    - `nested_symbol` remains at `tools/old.py:12`.\n"
            "    - Moved to `tools/new.py:14`."
        )
        quoted = (
            "> `quoted_symbol` remains stable.\n"
            "> It is used at tools/quoted.py:15."
        )

        self.assertEqual(
            ["tools/new.py:14"],
            [row.coordinate for row in coordinates.grade(nested, "record")],
        )
        self.assertEqual((), coordinates.grade(quoted, "record"))

    def test_list_items_inside_a_blockquote_are_distinct_paragraphs(self):
        text = (
            "> - `first_symbol` remains at `tools/old.py:12`.\n"
            "> - Moved to `tools/new.py:14`."
        )

        self.assertEqual(
            ["tools/new.py:14"],
            [row.coordinate for row in coordinates.grade(text, "record")],
        )

    def test_a_coordinate_cannot_be_its_own_quotation_or_empty_block_anchor(self):
        text = (
            'The locator is "tools/quoted.py:12".\n\n'
            "The next locator is `tools/empty.py:13`:\n\n"
            ">\n"
        )

        self.assertEqual(
            ["tools/quoted.py:12", "tools/empty.py:13"],
            [row.coordinate for row in coordinates.grade(text, "record")],
        )

    def test_punctuation_left_in_a_code_span_is_not_an_anchor(self):
        findings = coordinates.grade(
            "The location is `tools/new.py:14.`", "record"
        )

        self.assertEqual(["tools/new.py:14"], [row.coordinate for row in findings])

    def test_any_separate_nonempty_backticked_span_is_an_anchor(self):
        for anchor in ("==", "404"):
            with self.subTest(anchor=anchor):
                self.assertEqual(
                    (),
                    coordinates.grade(
                        f"`{anchor}` identifies tools/example.py:12.", "record"
                    ),
                )

    def test_the_recognizer_floor_documents_the_unmatched_spellings(self):
        examples = (
            "write_marker() is called at line 1345",
            "the early return at `:1259`",
            "in `tools/tracker_publish_hook.py`, at line 1345",
            "tools/tracker_publish_hook.py:1345",
        )
        self.assertEqual(
            [False, False, False, True],
            [coordinates.PATH_COORDINATE_CEILING.search(text) is not None for text in examples],
        )


class TheGithubEventCommand(unittest.TestCase):
    def test_the_real_event_entry_point_reports_without_echoing_record_text(self):
        marker = "private-prose-must-not-print"
        event = {
            "action": "created",
            "comment": {
                "id": 7,
                "html_url": "https://github.com/O/R/issues/928#issuecomment-7",
                "body": marker + " tools/example.py:12",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "event.json"
            path.write_text(json.dumps(event), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = coordinates.main(
                    [
                        "--github-event",
                        str(path),
                        "--event-name",
                        "issue_comment",
                    ]
                )

        report = stdout.getvalue() + stderr.getvalue()
        self.assertEqual(coordinates.FOUND, status)
        self.assertIn(coordinates.UNANCHORED, report)
        self.assertIn(event["comment"]["html_url"], report)
        self.assertIn("tools/example.py:12", report)
        self.assertNotIn(marker, report)

    def test_a_null_event_body_is_not_scanned(self):
        event = {
            "action": "opened",
            "issue": {
                "number": 928,
                "html_url": "https://github.com/O/R/issues/928",
                "body": None,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "event.json"
            path.write_text(json.dumps(event), encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                status = coordinates.main(
                    ["--github-event", str(path), "--event-name", "issues"]
                )

        self.assertEqual(coordinates.NOT_SCANNED, status)
        self.assertIn(coordinates.EVENT_BODY_UNREADABLE, stderr.getvalue())


class TheForwardOnlyAdrWalk(unittest.TestCase):
    def test_unreadable_git_population_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as temporary:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = coordinates.main([], root=Path(temporary))

        self.assertEqual(coordinates.NOT_SCANNED, status)
        self.assertIn(coordinates.ADR_POPULATION_UNREADABLE, stderr.getvalue())
        self.assertEqual("", stdout.getvalue())

    def test_last_touch_selects_records_on_either_side_of_the_cutoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adr = root / "docs" / "adr"
            adr.mkdir(parents=True)
            subprocess.run(
                ["git", "init", "--initial-branch=main"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test Writer"], cwd=root, check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "writer@example.invalid"],
                cwd=root,
                check=True,
            )

            old = adr / "0001-old.md"
            old.write_text("Unanchored tools/old.py:12\n", encoding="utf-8")
            self._commit(root, "old", coordinates.ADR_CUTOFF - timedelta(seconds=1))

            new = adr / "0002-new.md"
            new.write_text("Unanchored tools/new.py:13\n", encoding="utf-8")
            self._commit(root, "new", coordinates.ADR_CUTOFF + timedelta(seconds=1))

            first = coordinates.grade_adrs(root)
            self.assertEqual((2, 1), (first.records, first.eligible))
            self.assertEqual(["docs/adr/0002-new.md"], [row.locator for row in first.findings])
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(coordinates.FOUND, coordinates.main([], root=root))

            old.write_text("Still unanchored tools/old.py:12\n", encoding="utf-8")
            self._commit(root, "touch old", coordinates.ADR_CUTOFF + timedelta(seconds=2))
            second = coordinates.grade_adrs(root)
            self.assertEqual((2, 2), (second.records, second.eligible))
            self.assertEqual(
                ["docs/adr/0001-old.md", "docs/adr/0002-new.md"],
                sorted(row.locator for row in second.findings),
            )

    @staticmethod
    def _commit(root: Path, message: str, when) -> None:
        stamp = when.isoformat()
        environment = {
            **os.environ,
            "GIT_AUTHOR_DATE": stamp,
            "GIT_COMMITTER_DATE": stamp,
        }
        subprocess.run(["git", "add", "docs/adr"], cwd=root, check=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=root,
            env=environment,
            check=True,
            capture_output=True,
        )


class TheWrittenContract(unittest.TestCase):
    def test_every_surface_points_at_the_declared_limits_and_copies_no_row(self):
        issue_tracker = (REPO_ROOT / "docs" / "agents" / "issue-tracker.md").read_text(
            encoding="utf-8"
        )
        claude = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        maintainer_section = markdown_section(
            claude, "### Tracker coordinate accompaniment"
        )
        surfaces = (issue_tracker, maintainer_section, coordinates.__doc__ or "")

        for surface in surfaces:
            with self.subTest(surface=surface[:40]):
                self.assertIn("tracker_coordinates.DECLARED_LIMITS", surface)
                self.assertEqual((), bind(coordinates.DECLARED_LIMITS, surface, mode=NAMING))

        self.assertIn("coordinate in tracker text is never the locator", issue_tracker.lower())
        self.assertIn(
            "ready ticket's body carries no unanchored coordinate",
            " ".join(issue_tracker.lower().split()),
        )

    def test_adr_0189_is_eligible_and_clean_on_the_command_path(self):
        path = next((REPO_ROOT / "docs" / "adr").glob("0189-*.md"))
        scan = coordinates.grade_adrs(REPO_ROOT)
        self.assertGreater(scan.eligible, 0)
        self.assertNotIn(path.relative_to(REPO_ROOT).as_posix(), [row.locator for row in scan.findings])
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(coordinates.CLEAN, coordinates.main([]))

    def test_the_grader_family_records_its_own_refusal_reason(self):
        reason = run_grader.REFUSED["tracker_coordinates"]
        self.assertTrue(reason)
        self.assertNotEqual(run_grader.REFUSED["tracker_bodies"], reason)
        self.assertIn("ADR", reason)


if __name__ == "__main__":
    unittest.main()
