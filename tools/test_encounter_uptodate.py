"""ADR 0347 citation and replacement tests through the public commands."""
from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import differential_scan
import uptodate_store
from test_uptodate_store import topic


class EncounterUpToDate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.store = self.run / "store"
        self.addCleanup(mock.patch.stopall)
        mock.patch.dict(os.environ, {"CLINICAL_UPTODATE_STORE": str(self.store)}).start()

    def ingest(self, dump_id, text, *extra):
        source = self.run / f"{dump_id}.txt"
        source.write_text(text, encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return uptodate_store.main(["--store", str(self.store), "ingest", str(source), "--dump-id", dump_id, "--module", "synthetic", "--received-on", "2026-10-12", *extra])

    def scan(self, tail):
        # Keep the independent visit-time gate satisfied while these controls
        # discriminate citation identity and freshness.
        (self.run / "shift-values.json").write_text(
            '{"start":"0800","duration":{"hours":8,"minutes":0}}', encoding="utf-8")
        (self.run / "note.md").write_text("Start time 0800\nEnd time 0830\nA:\nDifferential:\n1. Cough - R05.9: Documented symptom. Most likely.\n\nFILLED·proposed 1. Screening reviewed " + tail + "\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            status = differential_scan.main([str(self.run)])
        return status, out.getvalue()

    def test_both_tail_forms_resolve_to_filed_topic(self):
        self.assertEqual(0, self.ingest("live-a", topic("Pneumonia")))
        for prefix in ("uptodate", "uptodate over thresholds/hypertension aha-2025"):
            with self.subTest(prefix=prefix):
                self.assertEqual(0, self.scan(f"[{prefix}: Pneumonia, updated January 2026, live-a]")[0])
        for tail in ("[uptodate: Pneumonia, updated January 2026, absent]", "[uptodate: Pneumonia, updated February 2026, live-a]", "[uptodate: Other topic, updated January 2026, live-a]", "[uptodate: Pneumonia]", "[uptodate over thresholds/absent row: Pneumonia, updated January 2026, live-a]"):
            with self.subTest(tail=tail):
                self.assertEqual(1, self.scan(tail)[0])

    def test_failed_pull_suffix_still_grades_the_sheet_citation(self):
        good = "[thresholds/hypertension: aha-2025 Class 1, adults-htn, SBP >=140; uptodate pull failed]"
        self.assertEqual(0, self.scan(good)[0])
        self.assertEqual(1, self.scan(good.replace("aha-2025", "absent"))[0])

    def test_fresh_pull_replaces_only_shared_topic_in_search_and_snapshot(self):
        self.assertEqual(0, self.ingest("old", topic("Pneumonia") + topic("Cervicitis")))
        self.assertEqual(0, self.ingest("fresh", topic("Pneumonia", updated="Oct 01, 2026"), "--supersedes", "old"))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(0, uptodate_store.main(["--store", str(self.store), "search", "Pneumonia", "Cervicitis"]))
        self.assertIn("fresh: Pneumonia", out.getvalue())
        self.assertNotIn("old: Pneumonia", out.getvalue())
        self.assertIn("old: Cervicitis", out.getvalue())
        details = {row.title: row.last_updated for row in uptodate_store.entitled_topic_details(self.store)}
        self.assertEqual("2026-10-01", details["Pneumonia"])
        self.assertIsNotNone(uptodate_store.source_topic("old", "Pneumonia", self.store))

    def test_bad_supersession_is_refused_without_a_filed_dump(self):
        self.assertEqual(2, self.ingest("fresh", topic("Pneumonia"), "--supersedes", "absent"))
        self.assertFalse((self.store / "dumps/fresh").exists())


if __name__ == "__main__":
    unittest.main()
