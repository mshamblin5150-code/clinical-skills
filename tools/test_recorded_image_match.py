"""Synthetic recorded imagery and canonical observation controls."""
# phi-scan: synthetic
import artifact_lock_test_support
import hashlib
from pathlib import Path
import tempfile
import unittest

import repo_root
import voice_model_observation as models


MODEL = '''## Imagery
### The domains
> Synthetic machinery
### How an image works for the writer
> The synthetic wheel carries the load.

### Scale and consequence
> A synthetic bridge holds the weight.
> The whole span bears it.
'''


class RecordedImagery(unittest.TestCase):
    def test_population_is_derived_without_a_match_record(self):
        result = models.read_images(MODEL)
        self.assertEqual(result.candidates, 2)
        self.assertEqual(result.unread, 0)
        self.assertFalse(result.missing)
        self.assertEqual(result.images, ("The synthetic wheel carries the load.", "A synthetic bridge holds the weight.\nThe whole span bears it."))
        self.assertNotIn("Synthetic machinery", result.images)
        extra = MODEL + '\n"A third complete synthetic image."\n'
        self.assertEqual(models.read_images(extra).candidates, 3)
        self.assertEqual(len(models.read_images(extra).images), 3)

    def test_missing_parts_and_duplicate_sections_cannot_certify_inventory(self):
        for source in ("", MODEL.replace("### Scale and consequence", "### Unrecognized subsection"), MODEL + MODEL):
            with self.subTest(source_length=len(source)):
                self.assertTrue(models.read_images(source).missing)

    def test_observation_hashes_the_same_bytes_it_decodes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic-model.md"
            raw = MODEL.replace("\n", "\r\n").encode("utf-8")
            path.write_bytes(raw)
            result = models.observe(repo_root.VoiceModelResolution(path, "stale-resolution-digest", True))
            self.assertEqual(result.sha256, hashlib.sha256(raw).hexdigest())
            self.assertEqual(result.text, raw.decode("utf-8"))
            self.assertEqual(result.unread, 0)
            path.write_bytes(b"\xff")
            unread = models.observe(repo_root.VoiceModelResolution(path, None, True))
            self.assertEqual(unread.unread, 1)
            self.assertIsNone(unread.text)
            self.assertEqual(models.observe(repo_root.VoiceModelResolution(path, None, False)).unread, 1)
