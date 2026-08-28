"""Shared conformance tests for commands that consume guideline manifests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import artifact_lock
import artifact_provenance


def trusted_extraction_producer() -> dict[str, object]:
    """A producer stamp accepted by the current checkout's extraction trust floor."""

    producer = dict(artifact_provenance.current_producer())
    producer["inputs"] = artifact_provenance.producer_file_identity(
        artifact_provenance.TRUST_FLOOR["extraction"]
    )
    return producer


def write_trusted_extraction_manifest(
    root: Path,
    producer: object | None = None,
) -> dict[str, object] | object:
    """Write the one minimal manifest fixture shared by threshold consumers."""

    selected = producer if producer is not None else trusted_extraction_producer()
    (root / "manifest.json").write_text(
        json.dumps({"producer": selected, "documents": []}),
        encoding="utf-8",
    )
    return selected


class ReadingManifestConformance:
    """Observable obligations every manifest-consuming command inherits.

    Subclasses provide ``build_conformance_corpus``, ``conformance_read``, and
    ``conformance_command``. Reads return ``(accepted, message)`` and commands
    return their process-style status.
    """

    def test_conformance_foreign_provenance_needs_the_explicit_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_conformance_corpus(root, {"commit": "f" * 40, "dirty": False})

            accepted, message = self.conformance_read(root, allow=False)
            with self.assertWarnsRegex(RuntimeWarning, "untrusted"):
                allowed, _ = self.conformance_read(root, allow=True)

            self.assertFalse(accepted)
            self.assertIn("different commit", message)
            self.assertTrue(allowed)

    def test_conformance_command_override_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_conformance_corpus(root, {"commit": "f" * 40, "dirty": False})

            refused = self.conformance_command(root, allow=False)
            with self.assertWarnsRegex(RuntimeWarning, "untrusted"):
                allowed = self.conformance_command(root, allow=True)

            self.assertEqual(refused, 2)
            self.assertEqual(allowed, 0)

    def test_conformance_does_not_read_an_extraction_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with artifact_lock.hold(root, "guideline extraction"):
                accepted, message = self.conformance_read(root, allow=False)

            self.assertFalse(accepted)
            self.assertIn("rebuilding", message)
