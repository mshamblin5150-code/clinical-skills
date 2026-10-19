"""The commit-time interpreter comparison is advisory. #1890.

phi-scan: synthetic
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


COMMAND = Path(__file__).resolve().with_name("maintainer_python.py")


class MaintainerPythonCommand(unittest.TestCase):
    def compare(self, version):
        with tempfile.TemporaryDirectory() as directory:
            pin = Path(directory) / "python-version"
            if version is not None:
                pin.write_text(version, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(COMMAND), "--pin", str(pin)],
                capture_output=True, text=True, encoding="utf-8",
            )

    def test_matching_release_is_silent_and_successful(self):
        result = self.compare(".".join(map(str, sys.version_info[:3])) + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_each_release_component_can_trigger_one_advisory_line(self):
        for component in range(3):
            version = list(sys.version_info[:3])
            version[component] += 1
            pinned = ".".join(map(str, version))
            with self.subTest(component=component):
                result = self.compare(pinned)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(result.stdout.splitlines()), 1)
                self.assertIn(pinned, result.stdout)
                self.assertIn(".".join(map(str, sys.version_info[:3])), result.stdout)
                self.assertIn("advisory", result.stdout.lower())
                self.assertEqual(result.stderr, "")

    def test_unreadable_or_invalid_pin_reports_comparison_not_made(self):
        for version in (None, "3.14", "invalid\n", "3.14.4\n3.14.8\n"):
            with self.subTest(version=version):
                result = self.compare(version)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(result.stdout.splitlines()), 1)
                self.assertIn("comparison not made", result.stdout.lower())
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
