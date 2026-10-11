"""Public fingerprint command contracts. #1493.

phi-scan: synthetic
"""
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class FileDigestCommand(unittest.TestCase):
    def test_a_relative_path_prints_the_raw_byte_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.bin").write_bytes(b"synthetic\r\n\x00\xff")
            command = Path(__file__).resolve().with_name("file_digest.py")
            result = subprocess.run(
                [sys.executable, str(command), "sample.bin"], cwd=root,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), hashlib.sha256(b"synthetic\r\n\x00\xff").hexdigest())
            self.assertEqual(result.stderr, "")

    @unittest.skipUnless(os.name == "nt", "Git Bash drive paths require Windows")
    def test_a_git_bash_path_reads_the_windows_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.bin"
            path.write_bytes(b"synthetic Git Bash input")
            spelling = "/" + path.drive[0].lower() + path.as_posix()[2:]
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("file_digest.py")), spelling],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), hashlib.sha256(path.read_bytes()).hexdigest())

    def test_an_unreadable_file_returns_two_and_a_plain_message(self):
        with tempfile.TemporaryDirectory() as directory:
            for path in (Path(directory), Path(directory) / "missing.bin"):
                with self.subTest(path=path):
                    result = subprocess.run(
                        [sys.executable, str(Path(__file__).with_name("file_digest.py")), str(path)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace",
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("cannot read", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
