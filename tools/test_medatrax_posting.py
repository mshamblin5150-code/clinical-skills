"""Contract tests for Medatrax note-population fingerprints."""

# phi-scan: synthetic

from __future__ import annotations

import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import medatrax_posting as posting


SUBMISSION = "shift-2026-08-17"


def reading(digest: str) -> str:
    return (
        f"## REREAD: {SUBMISSION}\n"
        "POST-URL: https://example.org/patient-visits\n"
        "POSTED: 08/17/2026 21:14\n"
        "READ: 1 of 1 read\n"
        "VERDICT: matches - The saved visit and note form matched.\n"
        f"SUBMISSION-SHA256: {digest}\n"
        "VISIT: 1 | patient 1 | reference matched P-17 | patient-detail=/patients/17 | "
        "note-view=/forms/view?resultid=31 | visit-date=08/17/2026 | matches\n"
    )


class BatchNotePopulation(unittest.TestCase):
    def test_numbered_notes_are_ordered_numerically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            (run / "note-10.md").write_bytes(b"ten")
            (run / "note-2.md").write_bytes(b"two")

            paths = posting.note_paths(run, batch=True)

            self.assertEqual(["note-2.md", "note-10.md"], [path.name for path in paths])
            self.assertEqual(sha256(b"twoten").hexdigest(), posting.source_sha256(paths))

    def test_nonmatching_markdown_is_outside_a_partial_batch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            (run / "note-1.md").write_text("included", encoding="utf-8")
            (run / "notes-2.md").write_text("excluded", encoding="utf-8")
            (run / "reread.md").write_text("excluded", encoding="utf-8")

            self.assertEqual((run / "note-1.md",), posting.note_paths(run, batch=True))

    def test_zero_numbered_notes_is_not_a_population(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            (run / "encounter.md").write_text("not a batch note", encoding="utf-8")

            self.assertEqual((), posting.note_paths(run, batch=True))


class StandaloneNotePopulation(unittest.TestCase):
    def test_readme_and_reread_are_excluded_from_the_one_note_population(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            note = run / "encounter.md"
            note.write_text("the note", encoding="utf-8")
            (run / "README.md").write_text("instructions", encoding="utf-8")
            (run / "reread.md").write_text("record", encoding="utf-8")

            self.assertEqual((note,), posting.note_paths(run, batch=False))

    def test_zero_or_multiple_candidates_is_not_a_population(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            self.assertEqual((), posting.note_paths(run, batch=False))
            (run / "one.md").write_text("one", encoding="utf-8")
            (run / "two.md").write_text("two", encoding="utf-8")
            self.assertEqual((), posting.note_paths(run, batch=False))


class FingerprintRefusals(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.run = Path(self.temporary.name)
        self.note = self.run / "note-1.md"
        self.note.write_bytes(b"approved note")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_malformed_hash_is_refused(self) -> None:
        (self.run / "reread.md").write_text(reading("not-a-digest"), encoding="utf-8")

        failed, report = posting.completion_gate(
            self.run, SUBMISSION, batch=True
        )

        self.assertTrue(failed)
        self.assertIn("SUBMISSION-SHA256 is malformed", report)

    def test_unreadable_note_bytes_are_refused(self) -> None:
        digest = sha256(self.note.read_bytes()).hexdigest()
        (self.run / "reread.md").write_text(reading(digest), encoding="utf-8")

        with patch.object(posting, "source_sha256", side_effect=OSError("unreadable")):
            failed, report = posting.completion_gate(
                self.run, SUBMISSION, batch=True
            )

        self.assertTrue(failed)
        self.assertIn("could not read the note bytes", report)

    def test_missing_exact_submission_record_is_refused(self) -> None:
        (self.run / "reread.md").write_text(
            reading(sha256(self.note.read_bytes()).hexdigest()).replace(
                SUBMISSION, "another-shift", 1
            ),
            encoding="utf-8",
        )

        failed, report = posting.completion_gate(
            self.run, SUBMISSION, batch=True
        )

        self.assertTrue(failed)
        self.assertIn("no readable REREAD record", report)

    def test_missing_visit_line_is_refused(self) -> None:
        digest = sha256(self.note.read_bytes()).hexdigest()
        (self.run / "reread.md").write_text(
            reading(digest).replace(
                "VISIT: 1 | patient 1 | reference matched P-17 | patient-detail=/patients/17 | note-view=/forms/view?resultid=31 | visit-date=08/17/2026 | matches\n",
                "",
            ),
            encoding="utf-8",
        )

        failed, report = posting.completion_gate(self.run, SUBMISSION, batch=True)

        self.assertTrue(failed)
        self.assertIn("0 VISIT line(s)", report)

    def test_read_count_and_visit_count_must_agree(self) -> None:
        (self.run / "note-2.md").write_bytes(b"second note")
        digest = posting.source_sha256(posting.note_paths(self.run, batch=True))
        (self.run / "reread.md").write_text(
            reading(digest).replace("READ: 1 of 1 read", "READ: 2 of 2 read"),
            encoding="utf-8",
        )

        failed, report = posting.completion_gate(self.run, SUBMISSION, batch=True)

        self.assertTrue(failed)
        self.assertIn("2 visit(s) but 1 VISIT line(s)", report)

    def test_zero_read_cannot_cover_one_fingerprinted_note(self) -> None:
        digest = sha256(self.note.read_bytes()).hexdigest()
        record = reading(digest).replace("READ: 1 of 1 read", "READ: 0 of 0 read")
        record = record[: record.index("VISIT:")]
        (self.run / "reread.md").write_text(record, encoding="utf-8")

        failed, report = posting.completion_gate(self.run, SUBMISSION, batch=True)

        self.assertTrue(failed)
        self.assertIn("0 visit(s) but the fingerprint covers 1 note(s)", report)

    def test_one_read_cannot_cover_two_fingerprinted_notes(self) -> None:
        (self.run / "note-2.md").write_bytes(b"second note")
        digest = posting.source_sha256(posting.note_paths(self.run, batch=True))
        (self.run / "reread.md").write_text(reading(digest), encoding="utf-8")

        failed, report = posting.completion_gate(self.run, SUBMISSION, batch=True)

        self.assertTrue(failed)
        self.assertIn("1 visit(s) but the fingerprint covers 2 note(s)", report)

    def test_each_visit_token_is_required(self) -> None:
        digest = sha256(self.note.read_bytes()).hexdigest()
        valid = reading(digest)
        mutations = {
            "ordered number": ("VISIT: 1 |", "VISIT: 2 |"),
            "patient number": ("patient 1 |", "subject |"),
            "reference": ("reference matched P-17 |", "reference P-17 |"),
            "patient detail": ("patient-detail=/patients/17 |", "detail=/patients/17 |"),
            "note resultid": ("note-view=/forms/view?resultid=31 |", "note-view=/forms/view |"),
            "date": ("visit-date=08/17/2026 |", "date=08/17/2026 |"),
            "visit verdict": ("| matches\n", "| checked\n"),
        }
        for label, (old, new) in mutations.items():
            with self.subTest(label=label):
                (self.run / "reread.md").write_text(
                    valid.replace(old, new), encoding="utf-8"
                )
                failed, report = posting.completion_gate(
                    self.run, SUBMISSION, batch=True
                )
                self.assertTrue(failed)
                self.assertIn("VISIT 1 is missing", report)

    def test_verdict_requires_matches_and_detail(self) -> None:
        digest = sha256(self.note.read_bytes()).hexdigest()
        for verdict in ("VERDICT: diverges - mismatch remains", "VERDICT: matches"):
            with self.subTest(verdict=verdict):
                (self.run / "reread.md").write_text(
                    reading(digest).replace(
                        "VERDICT: matches - The saved visit and note form matched.",
                        verdict,
                    ),
                    encoding="utf-8",
                )
                failed, report = posting.completion_gate(
                    self.run, SUBMISSION, batch=True
                )
                self.assertTrue(failed)
                self.assertIn("VERDICT must be matches", report)


if __name__ == "__main__":
    unittest.main()
