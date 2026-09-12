"""Behavior checks for publication-time measurement declarations."""

from __future__ import annotations

from pathlib import Path
from datetime import timedelta
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import phi_scan
import tracker_measurements as measurements
import tracker_publish_hook as publish_hook


CURRENT = "a" * 40
STALE = "b" * 40
REPO_ROOT = Path(__file__).resolve().parent.parent


class ThePublicTextGrade(unittest.TestCase):
    def test_an_own_line_full_sha_is_compared_with_the_publication_base(self):
        current = f"A load-bearing figure.\n\n**Measured at:** {CURRENT}\n"
        stale = f"A load-bearing figure.\n\n**Measured at:** {STALE}\n"

        self.assertEqual((), measurements.grade(current, "issue #961", CURRENT))
        self.assertEqual(
            (
                measurements.Finding(
                    measurements.STALE_BASE,
                    "issue #961",
                    STALE,
                    CURRENT,
                ),
            ),
            measurements.grade(stale, "issue #961", CURRENT),
        )

    def test_the_declaration_is_opt_in_but_a_malformed_claim_is_refused(self):
        self.assertEqual(
            (),
            measurements.grade("A contextual figure only.", "comment", CURRENT),
        )
        for body in (
            "**Measured at:** abc1234",
            f"**Measured at:** {CURRENT} trailing text",
        ):
            with self.subTest(body=body):
                findings = measurements.grade(body, "comment", CURRENT)
                self.assertEqual(
                    [measurements.INVALID_DECLARATION],
                    [row.rule for row in findings],
                )
        self.assertEqual(
            (),
            measurements.grade(
                f"A mention of **Measured at:** {CURRENT} is not a declaration.",
                "comment",
                CURRENT,
            ),
        )


class TrackerPublicationsUseTheSharedGrade(unittest.TestCase):
    def test_command_analysis_denies_a_stale_declared_base(self):
        body = f"A load-bearing figure.\n\n**Measured at:** {STALE}"
        with mock.patch.object(measurements, "current_head", return_value=CURRENT):
            result = publish_hook.analyze(
                publish_hook.Publication("body", body),
                index=phi_scan.build_index(set(), set()),
                issue=None,
                remote_fresh=True,
            )

        rows = [row for row in result.findings if row.rule == measurements.STALE_BASE]
        self.assertEqual(1, len(rows))
        self.assertEqual("deny", rows[0].posture)

    def test_direct_writer_refuses_the_same_stale_declared_base(self):
        body = f"A load-bearing figure.\n\n**Measured at:** {STALE}"
        with (
            mock.patch.object(measurements, "current_head", return_value=CURRENT),
            self.assertRaisesRegex(ValueError, measurements.STALE_BASE),
        ):
            publish_hook.authorize_issue_body(body, "issue #961")


class StagedAdrsUseTheCheckoutHead(unittest.TestCase):
    def test_a_staged_adr_is_compared_with_its_pre_commit_base(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs" / "adr").mkdir(parents=True)
            self._git(root, "init", "--initial-branch=main")
            self._git(root, "config", "user.name", "Test Writer")
            self._git(root, "config", "user.email", "writer@example.invalid")
            readme = root / "README.md"
            readme.write_text("base\n", encoding="utf-8")
            self._git(root, "add", "README.md")
            self._git(root, "commit", "-m", "base")
            head = self._git(root, "rev-parse", "HEAD").stdout.strip()

            adr = root / "docs" / "adr" / "0197-example.md"
            adr.write_text(f"# Example\n\n**Measured at:** {head}\n", encoding="utf-8")
            self._git(root, "add", "docs/adr/0197-example.md")

            self.assertEqual((), measurements.grade_staged_adrs(root).findings)

            adr.write_text(f"# Example\n\n**Measured at:** {STALE}\n", encoding="utf-8")
            self._git(root, "add", "docs/adr/0197-example.md")
            findings = measurements.grade_staged_adrs(root).findings
            self.assertEqual([measurements.STALE_BASE], [row.rule for row in findings])

    @staticmethod
    def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )


class TheForwardOnlyAdrAudit(unittest.TestCase):
    def test_only_last_touches_at_or_after_the_cutoff_are_graded(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adr_root = root / "docs" / "adr"
            adr_root.mkdir(parents=True)
            StagedAdrsUseTheCheckoutHead._git(root, "init", "--initial-branch=main")
            StagedAdrsUseTheCheckoutHead._git(root, "config", "user.name", "Test Writer")
            StagedAdrsUseTheCheckoutHead._git(
                root, "config", "user.email", "writer@example.invalid"
            )
            base = root / "README.md"
            base.write_text("base\n", encoding="utf-8")
            self._commit(root, "base", measurements.CUTOFF - timedelta(seconds=2))
            old = adr_root / "0001-old.md"
            old.write_text(f"# Old\n\n**Measured at:** {STALE}\n", encoding="utf-8")
            self._commit(root, "old", measurements.CUTOFF - timedelta(seconds=1))
            head = StagedAdrsUseTheCheckoutHead._git(root, "rev-parse", "HEAD").stdout.strip()

            new = adr_root / "0002-new.md"
            new.write_text(f"# New\n\n**Measured at:** {head}\n", encoding="utf-8")
            self._commit(root, "new", measurements.CUTOFF + timedelta(seconds=1))

            scan = measurements.grade_adrs(root)
            self.assertEqual((2, 1, 1), (scan.records, scan.eligible, scan.declarations))
            self.assertEqual((), scan.findings)

    @staticmethod
    def _commit(root: Path, message: str, when) -> None:
        stamp = when.isoformat()
        environment = {
            **os.environ,
            "GIT_AUTHOR_DATE": stamp,
            "GIT_COMMITTER_DATE": stamp,
        }
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=root,
            env=environment,
            check=True,
            capture_output=True,
        )


class TheCommandSurfaces(unittest.TestCase):
    def test_a_tracker_event_reports_the_finding_without_echoing_record_text(self):
        marker = "private-prose-must-not-print"
        event = {
            "action": "created",
            "comment": {
                "id": 7,
                "html_url": "https://github.com/O/R/issues/961#issuecomment-7",
                "body": f"{marker}\n\n**Measured at:** {STALE}",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "event.json"
            path.write_text(json.dumps(event), encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with (
                mock.patch.object(measurements, "current_head", return_value=CURRENT),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                status = measurements.main(
                    [
                        "--github-event",
                        str(path),
                        "--event-name",
                        "issue_comment",
                    ]
                )

        report = stdout.getvalue() + stderr.getvalue()
        self.assertEqual(measurements.FOUND, status)
        self.assertIn(measurements.STALE_BASE, report)
        self.assertIn(event["comment"]["html_url"], report)
        self.assertNotIn(marker, report)

    def test_the_staged_mode_reports_an_empty_index_cleanly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            StagedAdrsUseTheCheckoutHead._git(root, "init", "--initial-branch=main")
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = measurements.main(["--staged-adrs"], root=root)

        self.assertEqual(measurements.CLEAN, status)
        self.assertIn("staged ADRs", stdout.getvalue())

    def test_the_pre_commit_hook_refuses_the_staged_adr_command(self):
        hook = (REPO_ROOT / "tools" / "hooks" / "pre-commit").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            '"$python" "$repo_root/tools/tracker_measurements.py" --staged-adrs >&2 || status=1',
            hook,
        )

    def test_ci_reports_both_committed_adrs_and_changed_tracker_records(self):
        checks = (REPO_ROOT / ".github" / "workflows" / "checks.yml").read_text(
            encoding="utf-8"
        )
        tracker = (REPO_ROOT / ".github" / "workflows" / "tracker.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("python tools/tracker_measurements.py", checks)
        self.assertIn(
            "python tools/tracker_measurements.py --github-event", tracker
        )
        for workflow in (checks, tracker):
            self.assertIn("### Publication measurement base", workflow)


if __name__ == "__main__":
    unittest.main()
