from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import voice_model_scan as scan


TOOLS = Path(__file__).parent
REPO_ROOT = TOOLS.parent
VOICE_SPEC = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "voice.md"
SYNTHETIC = TOOLS / "testdata" / "voice-model-synthetic.md"
DISCUSSION_REPLY = REPO_ROOT / "skills" / "discussion-reply" / "SKILL.md"
SETUP = REPO_ROOT / "skills" / "setup-clinical-skills" / "SKILL.md"


def run(*arguments: str) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        status = scan.main(list(arguments))
    return status, stdout.getvalue(), stderr.getvalue()


class TheSyntheticModelGradesTheGrader(unittest.TestCase):
    def test_the_committed_model_is_clean_and_the_default_report_is_counts_only(self):
        status, stdout, stderr = run(str(SYNTHETIC))

        self.assertEqual(0, status)
        self.assertIn("voice model: ACTIVE", stdout)
        self.assertIn("registers: 3", stdout)
        self.assertIn("observations: 4", stdout)
        self.assertIn("discriminating pairs: 6", stdout)
        self.assertIn("findings: 0", stdout)
        self.assertNotIn("orbital mechanics", stdout)
        self.assertNotIn("Rowan Vale", stdout)
        self.assertEqual("", stderr)

    def test_the_required_item_vocabulary_is_read_from_the_tracked_spec(self):
        items = scan.read_required_items(VOICE_SPEC.read_text(encoding="utf-8"))

        self.assertIn("The invoked source and what it spends", items)
        self.assertEqual(items, scan.REQUIRED_ITEMS)

    def test_the_command_finds_drift_in_the_tracked_item_vocabulary_at_runtime(self):
        spec = VOICE_SPEC.read_text(encoding="utf-8").replace(
            "8. **The invoked source and what it spends.**",
            "8. **Imagery category.**",
            1,
        )

        result = scan.survey(SYNTHETIC.read_text(encoding="utf-8"), spec)

        self.assertIn("required-items", {finding.kind for finding in result.findings})


class ShapeFindingsRefuse(unittest.TestCase):
    def setUp(self):
        self.source = SYNTHETIC.read_text(encoding="utf-8")

    def grade(self, text: str) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "voice-model.md"
            model.write_text(text, encoding="utf-8")
            return run(str(model))

    def test_an_observation_without_a_quote_is_a_finding(self):
        changed = self.source.replace(
            '   > "The alternatives narrow quickly. This one does not fit."\n',
            "",
            1,
        )

        status, stdout, _ = self.grade(changed)

        self.assertEqual(1, status)
        self.assertIn("findings: 1", stdout)

    def test_a_register_without_two_complete_pairs_is_a_finding(self):
        changed = self.source.replace(
            '- *His*: "The first mark gives the second one something honest to beat."',
            "",
            1,
        )

        status, stdout, _ = self.grade(changed)

        self.assertEqual(1, status)
        self.assertIn("findings: 1", stdout)

    def test_the_his_half_must_be_a_visible_quote(self):
        changed = self.source.replace(
            '- *His*: "The alternatives narrow quickly. This one does not fit."',
            "- *His*: The alternatives narrow quickly. This one does not fit.",
            1,
        )

        status, stdout, _ = self.grade(changed)

        self.assertEqual(1, status)
        self.assertIn("findings: 1", stdout)

    def test_the_invoked_observation_requires_both_domain_and_property(self):
        for line in (
            "   Domain: orbital mechanics\n",
            "   Property: an object in orbit keeps falling while its forward motion keeps missing the ground\n",
        ):
            with self.subTest(line=line.split(":", 1)[0].strip()):
                status, stdout, _ = self.grade(self.source.replace(line, "", 1))
                self.assertEqual(1, status)
                self.assertIn("findings: 1", stdout)

    def test_a_finding_wins_over_an_incomplete_register_scan(self):
        changed = self.source.replace(
            '   > "The alternatives narrow quickly. This one does not fit."\n',
            "",
            1,
        )
        changed = changed.split("## Register 3 —", 1)[0]

        status, stdout, stderr = self.grade(changed)

        self.assertEqual(1, status)
        self.assertGreaterEqual(int(stdout.split("findings: ", 1)[1].splitlines()[0]), 1)
        self.assertIn("not completely scanned", stderr)


class TheAbsentModelIsADeclaredDoor(unittest.TestCase):
    def test_default_and_show_both_print_the_unmodeled_banner(self):
        with tempfile.TemporaryDirectory() as directory:
            absent = Path(directory) / "absent.md"
            for arguments in ((str(absent),), (str(absent), "--show")):
                with self.subTest(arguments=arguments):
                    status, stdout, stderr = run(*arguments)
                    self.assertEqual(2, status)
                    self.assertEqual("", stdout)
                    self.assertIn("voice model: NOT RUN", stderr)
                    self.assertIn("voice unmodeled", stderr)

    def test_the_implicit_path_uses_the_account_scratch_root(self):
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory) / "scratch"
            with mock.patch.object(scan.repo_root, "scratch_root", return_value=scratch):
                status, _, stderr = run()

        self.assertEqual(2, status)
        self.assertIn(str(scratch / "voice-model.md"), stderr)

    def test_an_unreadable_shape_and_an_invalid_invocation_are_exit_two(self):
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory) / "voice-model.md"
            empty.write_text("# Voice model\n", encoding="utf-8")
            status, stdout, stderr = run(str(empty))
            self.assertEqual(2, status)
            self.assertIn("registers: 0", stdout)
            self.assertIn("not completely scanned", stderr)

        status, stdout, stderr = run(str(SYNTHETIC), "--unknown")
        self.assertEqual(2, status)
        self.assertEqual("", stdout)
        self.assertIn("unrecognized option", stderr)


def require_live_model(scratch: Path) -> Path:
    model = scratch / "voice-model.md"
    if not model.is_file():
        raise unittest.SkipTest(f"voice unmodeled: no live model at {model}")
    return model


class TheLiveAccountModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = require_live_model(scan.repo_root.scratch_root())

    def test_the_real_model_has_clean_shape(self):
        status, _stdout, _stderr = run(str(self.model))
        self.assertEqual(0, status)


class TheLiveClassSkipsAsAWhole(unittest.TestCase):
    def test_an_absent_scratch_root_names_the_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            absent = Path(directory) / "scratch"
            with self.assertRaisesRegex(unittest.SkipTest, "voice unmodeled"):
                require_live_model(absent)


class BothBuildBoundariesRunTheGate(unittest.TestCase):
    COMMAND = "python tools/voice_model_scan.py"

    def sections(self):
        reply = DISCUSSION_REPLY.read_text(encoding="utf-8")
        reply_step_three = reply.split("## 3.", 1)[1].split("\n## 4.", 1)[0]
        setup = SETUP.read_text(encoding="utf-8")
        setup_step_eight = setup.split("### 8.", 1)[1].split("\n### 9.", 1)[0]
        return {
            "discussion-reply gate": reply_step_three,
            "setup-clinical-skills gate": setup_step_eight,
        }

    def test_each_boundary_requires_a_clean_scan(self):
        for name, section in self.sections().items():
            with self.subTest(boundary=name):
                self.assertIn(self.COMMAND, section)
                self.assertIn("exit 0", section.casefold())
                self.assertIn("required", section)

    def test_a_model_without_the_invoked_observation_fails_the_shared_gate(self):
        source = SYNTHETIC.read_text(encoding="utf-8")
        start = source.index("1. **The invoked source and what it spends.**")
        end = source.index("2. **The claim closes the paragraph.**")
        without_invoked = source[:start] + source[end:]
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "voice-model.md"
            model.write_text(without_invoked, encoding="utf-8")
            for name, section in self.sections().items():
                with self.subTest(boundary=name):
                    self.assertIn(self.COMMAND, section)
                    status, _stdout, _stderr = run(str(model))
                    self.assertEqual(1, status)


if __name__ == "__main__":
    unittest.main()
