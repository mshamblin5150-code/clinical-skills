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
import tracker_event_checks
import tracker_measurements as measurements
import tracker_publish_hook as publish_hook


CURRENT = "a" * 40
STALE = "b" * 40
REPO_ROOT = Path(__file__).resolve().parent.parent


class CommittedBodyReadFailuresRetainGitEvidence(unittest.TestCase):
    def test_long_object_path_reads_exact_blob_without_filesystem_disambiguation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def git(*args, body=None):
                return subprocess.run(
                    ["git", *args], cwd=root,
                    input=None if body is None else body.encode("utf-8"),
                    capture_output=True, check=True,
                ).stdout.decode("utf-8", errors="replace").strip()
            git("init", "--initial-branch=main")
            git("config", "user.name", "Fixture Writer")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "core.longpaths", "false")
            name = "0121-" + "long-object-name-" * 13 + ".md"
            relative = f"docs/adr/{name}"
            body = "# Immutable public fixture\n\nExact blob words.\n"
            blob = git("hash-object", "-w", "--stdin", body=body)
            adr = git("mktree", body=f"100644 blob {blob}\t{name}\n")
            docs = git("mktree", body=f"040000 tree {adr}\tadr\n")
            tree = git("mktree", body=f"040000 tree {docs}\tdocs\n")
            commit = git("commit-tree", tree, body="Public fixture\n")
            self.assertGreater(len(f"{commit}:{relative}"), 260)
            with mock.patch.object(measurements.subprocess, "run", wraps=subprocess.run) as run:
                self.assertEqual(body, measurements._committed_text(root, commit, relative))
            run.assert_called_once_with(
                ["git", "show", "--end-of-options", f"{commit}:{relative}", "--"],
                cwd=root, capture_output=True,
            )

    def test_nonzero_git_show_refuses_with_commit_status_and_bounded_stderr(self):
        relative = "docs/adr/0121-example.md"
        result = subprocess.CompletedProcess(
            ["git", "show"], 128, stdout=b"partial body",
            stderr=b"fatal: missing blob\n\xff" + b"x" * 2000,
        )
        with mock.patch.object(measurements.subprocess, "run", return_value=result) as run:
            with self.assertRaises(measurements.SourceError) as raised:
                measurements._committed_text(REPO_ROOT, CURRENT, relative)
        run.assert_called_once_with(
            ["git", "show", "--end-of-options", f"{CURRENT}:{relative}", "--"],
            cwd=REPO_ROOT, capture_output=True,
        )
        message = str(raised.exception)
        self.assertTrue(message.startswith(f"ADR body unreadable: {relative};"))
        self.assertIn(f"commit={CURRENT}; git show exit=128;", message)
        detail = message.split("stderr=", 1)[1]
        self.assertTrue(detail.startswith("fatal: missing blob \ufffd"))
        self.assertEqual(1000, len(detail))
        self.assertNotIn("partial body", message)

    def test_git_launch_error_preserves_refusal_and_exception_context(self):
        error = FileNotFoundError("git executable missing\n" + "x" * 2000)
        with mock.patch.object(measurements.subprocess, "run", side_effect=error):
            with self.assertRaises(measurements.SourceError) as raised:
                measurements._committed_text(REPO_ROOT, STALE, "docs/adr/0121-example.md")
        message = str(raised.exception)
        self.assertIn(f"commit={STALE};", message)
        self.assertIn("git show could not start (FileNotFoundError):", message)
        self.assertEqual(1000, len(message.split("FileNotFoundError): ", 1)[1]))
        self.assertIs(error, raised.exception.__cause__)


class ThePublicTextGrade(unittest.TestCase):
    def test_a_declaration_directly_after_a_quote_line_is_refused(self):
        for quote in ("> quoted scope", ">"):
            with self.subTest(quote=quote):
                findings = measurements.grade(
                    f"{quote}\n**Measured at:** {CURRENT}", "comment", CURRENT
                )
                self.assertEqual(
                    [measurements.INSIDE_QUOTE], [row.rule for row in findings]
                )

        self.assertEqual(
            (),
            measurements.grade(
                f"> quoted scope\n\n**Measured at:** {CURRENT}", "comment", CURRENT
            ),
        )

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
    def test_command_analysis_denies_a_declaration_directly_under_a_quote(self):
        body = f"> quoted claim\n**Measured at:** {CURRENT}"
        with mock.patch.object(measurements, "current_head", return_value=CURRENT):
            result = publish_hook.analyze(
                publish_hook.Publication("body", body),
                index=phi_scan.build_index(set(), set()),
                issue=None,
                remote_fresh=True,
            )

        rows = [row for row in result.findings if row.rule == measurements.INSIDE_QUOTE]
        self.assertEqual(1, len(rows))
        self.assertEqual("deny", rows[0].posture)

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


class AmendDeclarationsAtTheCommand(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Fixture Writer")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("commit", "--allow-empty", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.adr = self.root / "docs/adr/0197-example.md"
        self.adr.parent.mkdir(parents=True)

    def git(self, *args):
        return StagedAdrsUseTheCheckoutHead._git(self.root, *args)

    def stage(self, sha, words="Example words."):
        self.adr.write_text(f"# Example\n\n**Measured at:** {sha}\n\n{words}\n", encoding="utf-8")
        self.git("add", ".")

    def command(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = measurements.main(list(args), root=self.root)
        return status, stdout.getvalue() + stderr.getvalue()

    def test_amend_redeclaring_at_its_parent_passes_both_commands(self):
        self.stage(self.base)
        self.assertEqual(0, self.command("--staged-adrs")[0])
        self.git("commit", "-m", "new ADR")
        self.stage(self.base, "Edited words.")
        # Control: the unpatched staged command refuses this ordinary amend.
        self.assertEqual(0, self.command("--staged-adrs")[0])
        self.git("commit", "--amend", "-m", "edited ADR")
        self.assertEqual(0, self.command()[0])

    def test_plain_commit_using_parent_passes_staged_but_exact_audit_reports_it(self):
        self.git("commit", "--allow-empty", "-m", "advance tip")
        self.stage(self.base)
        self.assertEqual(0, self.command("--staged-adrs")[0])
        self.git("commit", "-m", "one base too far back")
        status, report = self.command("--commit", "HEAD")
        self.assertEqual(1, status)
        self.assertIn(measurements.STALE_BASE, report)
        self.assertEqual(1, self.command()[0])
        stale_commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.stage(stale_commit)
        self.git("commit", "-m", "fresh declaration")
        self.assertEqual(0, self.command("--commit", "HEAD")[0])
        self.assertEqual(1, self.command("--commit", stale_commit)[0])

    def test_neither_candidate_is_refused_and_both_candidates_are_reported(self):
        self.git("commit", "--allow-empty", "-m", "advance tip")
        tip = self.git("rev-parse", "HEAD").stdout.strip()
        self.stage(STALE)
        status, report = self.command("--staged-adrs")
        self.assertEqual(1, status)
        self.assertIn(self.base, report)
        self.assertIn(tip, report)

    def test_squash_discards_the_declared_base_and_merge_preserves_the_repair(self):
        self.git("checkout", "-b", "side")
        self.git("commit", "--allow-empty", "-m", "branch measurement base")
        declared_base = self.git("rev-parse", "HEAD").stdout.strip()
        self.stage(declared_base)
        self.git("commit", "-m", "branch declaration")
        self.assertEqual(0, self.command("--commit", "HEAD")[0])
        self.assertEqual(0, self.command()[0])

        self.git("checkout", "main")
        self.git("commit", "--allow-empty", "-m", "different integration base")
        squash_parent = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("merge", "--squash", "side")
        self.git("commit", "-m", "squashed declaration")
        squash_commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(declared_base, squash_parent)
        for arguments in (("--commit", squash_commit), ()):
            with self.subTest(arguments=arguments):
                status, report = self.command(*arguments)
                self.assertEqual(1, status)
                self.assertIn(measurements.STALE_BASE, report)
                self.assertIn(f"expected {squash_parent}", report)

        self.git("checkout", "-b", "repair")
        self.stage(squash_commit)
        self.git("commit", "-m", "redeclare at repair parent")
        repair_commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(0, self.command("--commit", repair_commit)[0])
        self.assertEqual(0, self.command()[0])
        self.git("checkout", "main")
        self.git("merge", "--no-ff", "repair", "-m", "preserve repair history")
        parents = self.git("rev-list", "--parents", "-n", "1", "HEAD").stdout.split()
        self.assertEqual([squash_commit, repair_commit], parents[1:])
        self.assertEqual(0, self.command("--commit", repair_commit)[0])
        self.assertEqual(0, self.command()[0])

    def test_commit_mode_refuses_unreadable_revision_and_accepts_no_adr_changes(self):
        self.assertEqual(2, self.command("--commit", "missing-revision")[0])
        self.assertEqual(2, self.command("--commit", "--all")[0])
        self.assertEqual(0, self.command("--commit", "HEAD")[0])

    def test_commit_mode_excludes_deleted_adrs_and_reports_root_without_parent(self):
        self.stage(self.base)
        tree = self.git("write-tree").stdout.strip()
        root_commit = self.git("commit-tree", tree, "-m", "root with declaration").stdout.strip()
        status, report = self.command("--commit", root_commit)
        self.assertEqual(1, status)
        self.assertIn(measurements.CURRENT_BASE_UNREADABLE, report)
        self.git("commit", "-m", "new ADR")
        self.git("rm", "docs/adr/0197-example.md")
        self.git("commit", "-m", "remove ADR")
        self.assertEqual(0, self.command("--commit", "HEAD")[0])

    def test_merge_mode_grades_the_first_parent_and_ignores_unrelated_old_adrs(self):
        self.stage(STALE)
        self.git("commit", "-m", "existing stale ADR")
        self.git("checkout", "-b", "side")
        self.git("commit", "--allow-empty", "-m", "side commit")
        self.git("checkout", "main")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("merge", "--no-ff", "--no-commit", "side")
        self.adr = self.adr.with_name("0198-merge.md")
        self.stage(base)
        self.git("commit", "-m", "merge with ADR")
        status, report = self.command("--commit", "HEAD")
        self.assertEqual(0, status)
        self.assertIn("records read 1", report)
        self.assertEqual(1, self.command()[0])

    def test_post_commit_hook_reports_without_refusing_and_uses_checkout_tool(self):
        hooks = self.root / "owning-hooks"
        hooks.mkdir()
        hook = hooks / "post-commit"
        hook.write_bytes((REPO_ROOT / "tools/hooks/post-commit").read_bytes())
        hook.chmod(0o755)
        self.git("config", "core.hooksPath", hooks.as_posix())
        tools = self.root / "tools"
        tools.mkdir()
        # The hook lives elsewhere; its command must resolve from this checkout.
        (tools / "tracker_measurements.py").write_text(
            "import sys\nfrom pathlib import Path\n"
            f"sys.path.insert(0, {str(REPO_ROOT / 'tools')!r})\n"
            "from tracker_measurements import main\n"
            "raise SystemExit(main(sys.argv[1:], root=Path.cwd()))\n",
            encoding="utf-8",
        )
        self.git("commit", "--allow-empty", "-m", "advance tip")
        self.stage(self.base)
        result = self.git("commit", "-m", "advisory finding")
        self.assertIn(measurements.STALE_BASE, result.stderr)
        result = self.git("commit", "--allow-empty", "-m", "unrelated")
        self.assertNotIn("publication measurements", result.stderr)
        self.stage(self.git("rev-parse", "HEAD").stdout.strip())
        result = self.git("commit", "-m", "clean declaration")
        self.assertIn("findings 0", result.stderr)
        (tools / "tracker_measurements.py").write_text(
            "import sys\nprint('fixture scan unavailable', file=sys.stderr)\nraise SystemExit(2)\n",
            encoding="utf-8",
        )
        self.stage(self.git("rev-parse", "HEAD").stdout.strip())
        result = self.git("commit", "-m", "unreadable advisory still permits commit")
        self.assertIn("fixture scan unavailable", result.stderr)


class SupersessionOnlyAdrProof(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "docs/adr").mkdir(parents=True)
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Fixture Writer")
        self.git("config", "user.email", "fixture@example.invalid")
        self.old_path = "docs/adr/0197-old.md"
        self.new_path = "docs/adr/0280-new.md"
        self.original = f"# Old record\n\n**Measured at:** {STALE}\n\n## Ruling 1 — original\n\nOld words.\n\nMeasured population: 44 records.\n"
        self.overturner = "# Later record\n\n## Ruling 1 — replacement\n\nReplacement words.\n"
        self.marker = '*Superseded 2099-04-17.* The words "Old words." are replaced by [ADR 0280](0280-new.md) ruling 1. The measurement remains historical.'
        self.binding = "\n## Supersedes\n\n- [ADR 0197](0197-old.md) ruling 1, the original wording is replaced.\n"
        self.write(self.old_path, self.original)
        self.write(self.new_path, self.overturner)
        self.write("docs/adr/supersession-classification-1518.json", "{}\n")
        self.commit("original historical records")

    def git(self, *args):
        return StagedAdrsUseTheCheckoutHead._git(self.root, *args)

    def write(self, path, text):
        (self.root / path).write_text(text, encoding="utf-8")

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-m", message)

    def annotate(self, body=None, binding=None):
        self.write(self.old_path, self.original + "\n" + self.marker + "\n" if body is None else body)
        self.write(self.new_path, self.overturner + self.binding if binding is None else binding)
        self.git("add", ".")

    def test_staged_and_committed_annotation_keeps_historical_declaration(self):
        self.annotate()
        self.assertEqual((), measurements.grade_staged_adrs(self.root).findings)
        self.assertIn(f"**Measured at:** {STALE}", (self.root / self.old_path).read_text(encoding="utf-8"))
        self.commit("supersession annotations")
        self.assertEqual((), measurements.grade_adrs(self.root).findings)
        # Tracker publications retain their existing current-base check.
        self.assertEqual([measurements.STALE_BASE],
                         [row.rule for row in measurements.grade(self.original, "issue", CURRENT)])

    def test_annotation_amend_can_prove_preservation_against_tip_parent(self):
        self.write(self.old_path, self.original.replace("Old words.", "Draft words."))
        self.commit("draft edit to replace by amend")
        self.annotate()
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(0, measurements.main(["--staged-adrs"], root=self.root))
        self.git("commit", "--amend", "-m", "annotations only")
        with redirect_stdout(stdout):
            self.assertEqual(0, measurements.main(["--commit", "HEAD"], root=self.root))
            self.assertEqual(0, measurements.main([], root=self.root))

    def test_changed_measurement_declaration_or_arbitrary_body_is_refused(self):
        for body in (
            self.original.replace("44 records", "45 records"),
            self.original.replace(STALE, "c" * 40),
            self.original + "\nA new body claim.\n",
        ):
            with self.subTest(body=body):
                self.annotate(body + "\n" + self.marker + "\n")
                self.assertTrue(measurements.grade_staged_adrs(self.root).findings)

    def test_malformed_unbound_invented_or_unattributed_annotation_is_refused(self):
        for marker in (
            self.marker.replace("2099-04-17", "2099-99-99"),
            self.marker.replace("ruling 1", "ruling 2"),
            self.marker.replace("Old words.", "Invented words."),
        ):
            with self.subTest(marker=marker):
                self.annotate(self.original + "\n" + marker + "\n")
                self.assertTrue(measurements.grade_staged_adrs(self.root).findings)
        self.annotate(self.marker + "\n\n" + self.original)
        self.assertTrue(measurements.grade_staged_adrs(self.root).findings)
        self.annotate(binding=self.overturner)
        self.assertTrue(measurements.grade_staged_adrs(self.root).findings)

    def test_new_adr_and_unreadable_git_proof_cannot_be_exempted(self):
        self.annotate()
        self.write("docs/adr/0199-brand-new.md", self.original + "\n" + self.marker + "\n")
        self.git("add", ".")
        self.assertTrue(measurements.grade_staged_adrs(self.root).findings)
        with mock.patch.object(measurements, "_adr_snapshot", side_effect=measurements.SourceError("unreadable")):
            self.assertFalse(measurements._annotation_only_proof(
                self.root, self.old_path, self.git("rev-parse", "HEAD").stdout.strip(),
                ":", self.original + "\n" + self.marker + "\n"))

    def test_existing_invalid_declaration_and_inside_quote_findings_survive(self):
        for original in (
            self.original.replace(STALE, "short"),
            self.original.replace("**Measured at:**", "> Quote\n**Measured at:**"),
        ):
            with self.subTest(original=original):
                self.annotate(original + "\n" + self.marker + "\n")
                rules = [row.rule for row in measurements.grade_staged_adrs(self.root).findings]
                self.assertTrue(set(rules) & {measurements.INVALID_DECLARATION, measurements.INSIDE_QUOTE})

    def test_closed_legacy_normalization_preserves_all_original_body_words(self):
        legacy = '*Superseded grounding marked 2099-04-17.* The words "Old words." were replaced by [ADR 0280](0280-new.md) ruling 1. The measurement remains historical.'
        original = self.original + "\n" + legacy + "\n"
        self.write(self.old_path, original)
        self.commit("historical legacy marker")
        self.git("commit", "--allow-empty", "-m", "retain legacy in both candidate bases")
        normalized = legacy.replace("Superseded grounding marked", "Superseded")
        self.annotate(self.original + "\n" + normalized + "\n")
        self.assertEqual((), measurements.grade_staged_adrs(self.root).findings)
        self.annotate(self.original + "\n" + normalized.replace("remains historical", "is freshly measured") + "\n")
        self.assertTrue(measurements.grade_staged_adrs(self.root).findings)

    def test_fenced_examples_and_tables_cannot_be_changed_or_laundered(self):
        for addition, old, new in (
            ("\n```text\n\n## Supersedes\n\n- Existing example: 44 findings.\n\n```\n", "44 findings", "45 findings"),
            ("\n| property | value |\n| --- | --- |\n| findings | 44 |\n", "| findings | 44 |", "| findings | 45 |"),
            ("\n```text\n\n" + self.marker + "\n\n```\n", "measurement remains historical", "measurement is current"),
        ):
            with self.subTest(addition=addition):
                baseline = self.original + addition
                self.write(self.old_path, baseline)
                self.commit("retain original examples")
                self.annotate(baseline.replace(old, new) + "\n" + self.marker + "\n")
                self.assertTrue(measurements.grade_staged_adrs(self.root).findings)

    def test_literal_whitespace_change_refuses_staged_and_committed_reads(self):
        for addition in (
            '\n```python\nmeasured = "a  b"\n\nprint(measured)\n```\n',
            '\nThe measured literal is `a  b`.\n',
            '\n| measured string | value |\n| --- | --- |\n| literal | a  b |\n',
        ):
            with self.subTest(addition=addition):
                baseline = self.original + addition
                self.write(self.old_path, baseline)
                self.commit("retain exact measured literal")
                self.annotate(baseline.replace("a  b", "a b") + "\n" + self.marker + "\n")
                self.assertTrue(measurements.grade_staged_adrs(self.root).findings)
                self.commit("changed literal must remain a finding")
                self.assertTrue(measurements.grade_adrs(self.root).findings)

    def test_corrected_opening_normalizes_only_with_exact_body_and_date(self):
        legacy = '*Corrected 2099-04-17.* The words "Old words." were replaced by [ADR 0280](0280-new.md) ruling 1. The measurement remains historical.'
        self.write(self.old_path, self.original + "\n" + legacy + "\n")
        self.commit("dated historical correction")
        self.git("commit", "--allow-empty", "-m", "retain correction in both candidate bases")
        normalized = legacy.replace("*Corrected ", "*Superseded ", 1)
        self.annotate(self.original + "\n" + normalized + "\n")
        self.assertEqual((), measurements.grade_staged_adrs(self.root).findings)
        for changed in (
            normalized.replace("2099-04-17", "2098-04-17"),
            normalized.replace("remains historical", "is current"),
        ):
            with self.subTest(changed=changed):
                self.annotate(self.original + "\n" + changed + "\n")
                self.assertTrue(measurements.grade_staged_adrs(self.root).findings)


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

    def test_an_opened_record_does_not_grade_a_measurement_label_in_its_title(self):
        event = {
            "action": "opened",
            "issue": {
                "number": 1152,
                "title": "**Measured at:** not-a-commit",
                "body": "Ordinary body.",
                "labels": [],
                "html_url": "https://example.invalid/issues/1152",
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "event.json"
            path.write_text(json.dumps(event), encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                status = measurements.main(
                    [
                        "--github-event",
                        str(path),
                        "--event-name",
                        "issues",
                    ]
                )

        self.assertEqual(measurements.CLEAN, status)
        self.assertIn("records read 1", stdout.getvalue())
        self.assertNotIn(measurements.INVALID_DECLARATION, stdout.getvalue())

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
        self.assertIn("python tools/tracker_event_checks.py", tracker)
        selected = tracker_event_checks.select_checks(
            {
                "action": "created",
                "issue": {"number": 1, "labels": []},
                "comment": {"body": "text"},
            },
            "issue_comment",
        )
        self.assertIn(tracker_event_checks.MEASUREMENTS, selected)
        self.assertIn("### Publication measurement base", checks)
        self.assertEqual(
            tracker_event_checks.MEASUREMENTS.heading,
            "Publication measurement base",
        )


if __name__ == "__main__":
    unittest.main()
