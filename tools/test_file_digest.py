"""Public-interface tests for streamed raw-file fingerprints."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import file_digest


class TheRawFileDigest(unittest.TestCase):
    def test_sha256_hashes_the_file_bytes_without_text_normalization(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.bin"
            payload = b"first\r\nsecond\n\x00" + (b"x" * (1024 * 1024 + 7))
            source.write_bytes(payload)

            self.assertEqual(hashlib.sha256(payload).hexdigest(), file_digest.sha256(source))

    def test_a_recorded_digest_is_read_or_reported_unavailable(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.sha256"
            source.write_text("f" * 64 + "\n", encoding="ascii")

            self.assertEqual("f" * 64, file_digest.recorded_sha256(source))
            self.assertIsNone(file_digest.recorded_sha256(source.with_name("missing.sha256")))

    def test_a_recorded_digest_writer_uses_the_reader_format(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "artifact.sha256"
            digest = file_digest.sha256_bytes(b"captured once")
            file_digest.write_recorded_sha256(destination, digest)

            self.assertEqual(digest, file_digest.recorded_sha256(destination))


if __name__ == "__main__":
    unittest.main()
