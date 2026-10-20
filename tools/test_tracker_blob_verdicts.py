"""ADR 0438 native controls; all repositories and identifiers are synthetic."""
# phi-scan: synthetic
import hashlib
import json
from pathlib import Path
from unittest import mock

import phi_scan
import tracker_scan
import test_tracker_scan as fixtures


class BlobVerdicts(fixtures.MainInATempRepo):
    def setUp(self):
        super().setUp()
        for name, value in (("corpus_coverage", None), ("harvest_entries", []),
                            ("reviewed_names", set()), ("unreviewed_names", {fixtures.NAME})):
            patch = mock.patch.object(phi_scan, name, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)

    def subject(self, text=None):
        text = text or f"{fixtures.NAME} is synthetic"
        self.checkout.commit("subject.md", text, "synthetic input")
        oid = self.checkout._run("rev-parse", "HEAD:subject.md").stdout.strip()
        return oid, text

    def row(self, oid, text, **changes):
        return {"blob": oid, "line": 1, "rule": "corpus-name",
                "line_sha256": hashlib.sha256(text.splitlines()[0].encode()).hexdigest(),
                "verdict": "noise", "reason": "Synthetic fixture text.", **changes}

    def ledger(self, rows):
        path = self.repo / tracker_scan.RULINGS_PATH
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({"version": 2, "commit_findings": [],
                                    "harvest_findings": [], "blob_findings": rows}), encoding="utf-8")

    def test_exact_blob_row_clears_only_one_version(self):
        oid, text = self.subject()
        self.ledger([self.row(oid, text)])
        status, report = self.run_main("--history", "--no-pull-refs")
        self.assertEqual(0, status, report)
        self.assertRegex(report, r"ruled findings\s+1")
        self.checkout.commit("subject.md", text + "\nA later version.", "later")
        status, report = self.run_main("--history", "--no-pull-refs")
        self.assertEqual(1, status, report)
        self.assertRegex(report, r"corpus-name\s+1")

    def test_each_identity_component_is_required_and_abbreviated_ids_refuse(self):
        oid, text = self.subject()
        for changed in ({"line": 2}, {"rule": "phone"}, {"line_sha256": "0" * 64},
                        {"blob": "0" * 40}, {"blob": oid[:10]}):
            with self.subTest(changed=changed):
                self.ledger([self.row(oid, text, **changed)])
                status, report = self.run_main("--history", "--no-pull-refs")
                self.assertEqual(1, status, report)
                self.assertIn("corpus-name", report)
                if len(changed.get("blob", oid)) != 40:
                    self.assertIn("invalid blob", report)
                else:
                    self.assertRegex(report, r"unmatched verdict rows\s+1")

    def test_blank_and_malformed_blob_rows_fail_closed_without_findings(self):
        oid, text = self.subject("ordinary text")
        for changes in ({"verdict": ""}, {"reason": " "}, {"verdict": []},
                        {"line": True}, {"blob": oid[:10]}):
            with self.subTest(changes=changes):
                self.ledger([self.row(oid, text, **changes)])
                status, report = self.run_main("--history", "--no-pull-refs")
                self.assertEqual(2, status, report)
                self.assertIn("DID NOT APPLY", report)

    def test_unmatched_and_repeated_rows_keep_occurrence_accounting(self):
        oid, text = self.subject()
        self.ledger([self.row(oid, text), self.row(oid, text)])
        status, report = self.run_main("--history", "--no-pull-refs")
        self.assertEqual(0, status, report)
        self.assertRegex(report, r"ruled findings\s+1")
        self.assertRegex(report, r"unmatched verdict rows\s+1")

    def test_closed_verdicts_and_conflicting_rows_keep_the_existing_policy(self):
        oid, text = self.subject()
        self.ledger([self.row(oid, text, verdict="accepted-history")])
        status, report = self.run_main("--history", "--no-pull-refs")
        self.assertEqual(0, status, report)
        self.ledger([self.row(oid, text), self.row(oid, text, verdict="accepted-history")])
        status, report = self.run_main("--history", "--no-pull-refs")
        self.assertEqual(1, status, report)
        self.assertIn("conflicts", report)
        self.assertRegex(report, r"corpus-name\s+1")
        self.ledger(None)
        status, report = self.run_main("--history", "--no-pull-refs")
        self.assertEqual(1, status, report)
        self.assertIn("blob_findings must be a list", report)

    def test_draft_has_full_blob_identity_and_blank_decision_without_matched_text(self):
        oid, text = self.subject()
        draft = Path(self.tmp.name) / "draft.json"
        status, report = self.run_main("--history", "--no-pull-refs", "--draft-verdicts", str(draft))
        self.assertEqual(1, status, report)
        payload = json.loads(draft.read_text(encoding="utf-8"))
        self.assertEqual([self.row(oid, text, verdict="", reason="")], payload["blob_findings"])
        self.assertNotIn(fixtures.NAME, draft.read_text(encoding="utf-8"))

    def test_matching_uses_full_identity_even_when_the_display_label_is_wrong(self):
        oid, text = self.subject()
        records = tracker_scan.blob_records(self.repo)
        records = [r._replace(ref="blob 0000000000 misleading.md") if r.blob_oid == oid else r for r in records]
        self.ledger([self.row(oid, text)])
        with mock.patch.object(tracker_scan, "blob_records", return_value=records):
            status, report = self.run_main("--history", "--no-pull-refs")
        self.assertEqual(0, status, report)

    def test_show_distinguishes_origin_reachable_and_local_only_blobs(self):
        public, _ = self.subject()
        self.checkout._run("update-ref", "refs/remotes/origin/main", "HEAD")
        self.checkout.commit("local.md", f"{fixtures.NAME} local synthetic", "local")
        local = self.checkout._run("rev-parse", "HEAD:local.md").stdout.strip()
        status, report = self.run_main("--history", "--no-pull-refs", "--show")
        self.assertEqual(1, status, report)
        self.assertRegex(report, rf"blob {public[:10]}[^\n]+origin-reachable: yes")
        self.assertRegex(report, rf"blob {local[:10]}[^\n]+origin-reachable: no")

    def test_origin_only_reader_filters_before_content_reads_and_keeps_all_public_paths(self):
        public, text = self.subject()
        self.checkout.commit("fixtures/copy/input.md", text, "public second path")
        self.checkout._run("update-ref", "refs/remotes/origin/main", "HEAD")
        self.checkout.commit("local.md", "unpublished synthetic content", "local")
        local = self.checkout._run("rev-parse", "HEAD:local.md").stdout.strip()
        seen = []
        original = tracker_scan.subprocess.Popen
        def observe(*args, **kwargs):
            process = original(*args, **kwargs)
            if args[0] != ["git", "cat-file", "--batch"]:
                return process
            writer = process.stdin
            class Input:
                def write(self, value):
                    seen.append(value.decode().strip())
                    self.assert_public(value)
                    return writer.write(value)
                def assert_public(self, value):
                    if value.decode().strip() == local:
                        raise AssertionError("local-only content requested")
                def flush(self): return writer.flush()
                def close(self): return writer.close()
            process.stdin = Input()
            return process
        with mock.patch.object(tracker_scan.subprocess, "Popen", side_effect=observe):
            records = tracker_scan.blob_records(self.repo, revisions=("--remotes=origin",))
        self.assertTrue(seen)
        self.assertNotIn(local, {r.blob_oid for r in records})
        record = next(r for r in records if r.blob_oid == public)
        self.assertEqual(frozenset({"subject.md", "fixtures/copy/input.md"}), record.committed_paths)
        self.assertTrue(record.origin_reachable)

    def test_show_marks_clean_blobs_and_selected_metadata_cannot_duplicate_an_oid(self):
        self.subject("ordinary text")
        self.checkout._run("update-ref", "refs/remotes/origin/main", "HEAD")
        status, report = self.run_main("--history", "--no-pull-refs", "--show")
        self.assertEqual(0, status, report)
        self.assertIn("origin-reachable: yes", report)
        original = tracker_scan._git
        def duplicate(repo, *args, **kwargs):
            result = original(repo, *args, **kwargs)
            if "--batch-check=%(objectname) %(objecttype)" in args:
                rows = result.splitlines()
                self.assertGreater(len(rows), 1)
                return "\n".join([rows[0]] * len(rows))
            return result
        with mock.patch.object(tracker_scan, "_git", side_effect=duplicate):
            with self.assertRaises(tracker_scan.GitError):
                tracker_scan.blob_records(self.repo)

    def test_harvest_pointer_reaches_every_name_surface_and_not_clean_reports(self):
        self.subject()
        harvest = self.harvest("one.json", [{"html_url": "https://github.com/example/repo/issues/1",
                                             "body": fixtures.NAME}])
        self.checkout.commit(f"{fixtures.NAME}.md", "ordinary text", fixtures.NAME)
        event = self.harvest("event.json", {"comment": {"id": 7, "body": fixtures.NAME}})
        for args in (("--history", "--no-pull-refs"), ("--commits", "--no-pull-refs"),
                     ("--paths",), ("--harvest", harvest),
                     ("--github-event", event, "--event-name", "issue_comment")):
            with self.subTest(args=args):
                status, report = self.run_main(*args)
                self.assertEqual(1, status, report)
                self.assertIn("python tools/harvest_review.py", report)
        clean = self.harvest("clean.json", [{"html_url": "https://github.com/example/repo/issues/2",
                                             "body": "ordinary text"}])
        status, report = self.run_main("--harvest", clean)
        self.assertEqual(0, status, report)
        self.assertNotIn("python tools/harvest_review.py", report)
        with mock.patch.object(phi_scan, "unreviewed_names", return_value=set()):
            status, report = self.run_main("--harvest", harvest)
        self.assertEqual(1, status, report)
        self.assertNotIn("python tools/harvest_review.py", report)
