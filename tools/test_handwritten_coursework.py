"""Native ADR 0395 coursework/sourcing controls; synthetic records only."""
# phi-scan: synthetic
import artifact_lock_test_support
import contextlib
from datetime import timedelta
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import claim_ledger_census
import checks_ledger
import completion_checks
import discussion_artifact
import discussion_reply_scan
import peer_critique_scan
import refutation_apply
import research_ledger
import run_record_reader
import run_grader
import approval_record
import bar_signatures
import mechanics_test_support
import test_discussion_post_scan as post_fixtures
import test_discussion_reply_scan as reply_fixtures
import test_peer_critique_scan as critique_fixtures
import test_refutation_apply as return_fixtures
import test_research_ledger as ledger_fixtures


class CourseworkDamage(unittest.TestCase):
    def setUp(self):
        token = mechanics_test_support.begin()
        self.addCleanup(mechanics_test_support.end, token)

    def invoke(self, command, argv):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = command.main(argv)
        return status, output.getvalue() + error.getvalue()

    def test_each_claim_position_refuses_all_six_damage_characters_at_the_command(self):
        for character in ("\t", "\x07", "\x00", "\x0c", "\x0b", "\r"):
            for before, after in (("## CLAIM:", "## CLA" + character + "IM:"),
                                  ("STATUS:", "STA" + character + "TUS:"),
                                  ("STATUS: sourced", "STATUS: so" + character + "urced"),
                                  ("PASSAGE:", "PASSAGE: free" + character + "text ")):
                with self.subTest(code=ord(character), position=before), tempfile.TemporaryDirectory() as name:
                    root = Path(name)
                    ledger_fixtures.write_bar(root)
                    path = root / "claims.md"
                    path.write_bytes(ledger_fixtures.ledger_text(ledger_fixtures.CLEAN).replace(before, after, 1).encode())
                    status, report = self.invoke(research_ledger, [str(path)])
                    self.assertEqual(1, status, report)
                    self.assertIn(f"U+{ord(character):04X}", report)
                    self.assertIn("not graded — damaged text", report)
                    self.assertNotIn("no claim records found", report)

    def test_raw_qualifier_json_string_escapes_are_checked_without_a_second_decoder(self):
        for escaped, code in ((r'"C:\temp"', "0009"), (r'"value\u0000tail"', "0000")):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as name:
                root = Path(name)
                ledger_fixtures.write_bar(root)
                path = root / "claims.md"
                path.write_text(ledger_fixtures.ledger_text(ledger_fixtures.CLEAN) + "QUALIFIERS: " + escaped + "\n", encoding="utf-8")
                status, report = self.invoke(research_ledger, [str(path)])
                self.assertEqual(1, status, report)
                self.assertIn("QUALIFIERS: U+" + code, report)

    def test_folded_mixed_case_and_duplicate_qualifier_fields_keep_decoded_damage(self):
        for value in ('  qUaLiFiErS:\n    "C:\\temp"\n',
                      'QUALIFIERS: "C:\\temp"\nQUALIFIERS: none\n'):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as name:
                root = Path(name)
                ledger_fixtures.write_bar(root)
                path = root / "claims.md"
                path.write_text(ledger_fixtures.ledger_text(ledger_fixtures.CLEAN) + value, encoding="utf-8")
                status, report = self.invoke(research_ledger, [str(path)])
                self.assertEqual(1, status, report)
                self.assertIn("QUALIFIERS: U+0009", report)

    def test_historical_approved_claim_damage_keeps_the_existing_trace_finding(self):
        cutoff = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        for moment in (cutoff - timedelta(microseconds=1), cutoff, None):
            for newline in ("\n", "\r\n"):
                with self.subTest(moment=moment, newline=repr(newline)), tempfile.TemporaryDirectory() as name:
                    run = post_fixtures.APostedInitialEntryHasItsOwnReading().posted_run(Path(name))
                    approvals = run.root / "posting-approvals.json"
                    record = json.loads(approvals.read_text(encoding="utf-8"))
                    if moment is not None:
                        record["items"][0]["recorded_at"] = moment.isoformat()
                    approvals.write_text(json.dumps(record), encoding="utf-8")
                    run.draft.write_text(post_fixtures.BODY.replace("12% improvement", "17% improvement"), encoding="utf-8")
                    claims = post_fixtures.CLAIMS.replace("STATUS: sourced", "STATUS: invented", 1) + "REMARK: free\x07text\n"
                    (run.root / "claims.md").write_bytes(claims.replace("\n", newline).encode())
                    status, report, error = run.grade("--submission", run.draft.stem)
                    self.assertEqual(1, status, report + error)
                    if moment is not None and moment < cutoff:
                        self.assertIn("untraced-number: 1", report)
                        self.assertNotIn("U+0007", report)
                        with completion_checks.grading(run.root, run.draft.stem):
                            old_text = run_record_reader.read_handwritten_record(
                                run.root / "claims.md", research_ledger.CLAIM_RECORD_KIND).require_text(artifact=run.draft.name)
                            old_records = research_ledger.read_records(old_text)
                            self.assertEqual("invented", old_records[0].value("STATUS"))
                            old_scan = research_ledger.survey(old_records, research_ledger.ledger_date(old_text))
                            self.assertIn(research_ledger.UNKNOWN_STATUS, {finding.kind for finding in old_scan.findings})
                    else:
                        self.assertIn("untraced-number: not graded", report)
                        self.assertIn("U+0007", report)

    def test_census_counts_a_damaged_claim_marker_as_unread_in_its_full_population(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            run = root / "scratch" / "runs" / "one"
            run.mkdir(parents=True)
            (run / "claims.md").write_bytes(b"## CLA\x07IM: hidden\nSTATUS: sourced\n")
            with mock.patch.object(claim_ledger_census.scratch_census, "worktree_roots", return_value=(root,)):
                status, report = self.invoke(claim_ledger_census, [])
            self.assertEqual(1, status, report)
            self.assertIn("ledgers read                       1", report)
            self.assertIn("unread remainder 1", report)
            self.assertNotIn("hidden", report)

    def test_refuter_writer_refuses_before_snapshots_or_saved_returns_and_keeps_siblings(self):
        for damaged_ledger in (False, True):
            with self.subTest(ledger=damaged_ledger), tempfile.TemporaryDirectory() as name:
                root = Path(name)
                ledger = root / "claims.md"
                ledger.write_text("## CLAIM: synthetic\nSTATUS: sourced\n", encoding="utf-8")
                returned = root / "return.md"
                returned.write_text(return_fixtures.returned("synthetic"), encoding="utf-8")
                target = ledger if damaged_ledger else returned
                target.write_bytes(target.read_bytes() + b"\x07")
                original = ledger.read_bytes()
                status, report = self.invoke(refutation_apply, [str(ledger), str(returned)])
                self.assertEqual(1, status, report)
                self.assertEqual(original, ledger.read_bytes())
                self.assertFalse((root / "claims-snapshot-1.md").exists())
                self.assertFalse((root / "refutations").exists())

    def test_damaged_return_is_not_saved_and_an_independent_clean_return_still_applies(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            ledger = root / "claims.md"
            ledger.write_text("## CLAIM: synthetic\nSTATUS: sourced\n", encoding="utf-8")
            old = ledger.read_bytes()
            damaged, clean = root / "damaged.md", root / "clean.md"
            damaged.write_bytes(return_fixtures.returned("synthetic").encode() + b"\x07")
            clean.write_text(return_fixtures.returned("synthetic"), encoding="utf-8")
            with mock.patch.object(completion_checks, "active", return_value=False):
                status, report = self.invoke(refutation_apply, [str(ledger), str(damaged), str(clean)])
            self.assertEqual(1, status, report)
            self.assertIn("applied 1", report)
            self.assertFalse((root / "refutations" / damaged.name).exists())
            self.assertEqual(clean.read_bytes(), (root / "refutations" / clean.name).read_bytes())
            self.assertEqual(old, (root / "claims-snapshot-1.md").read_bytes())

    def test_post_claim_damage_does_not_manufacture_missing_trace_or_hide_draft_findings(self):
        with tempfile.TemporaryDirectory() as name:
            run = post_fixtures.Run(Path(name))
            run.draft.write_text("## References\n", encoding="utf-8")
            (run.root / "claims.md").write_bytes(b"## CLAIM: \x07damaged\n")
            status, report, error = run.grade()
            self.assertEqual(1, status, report + error)
            self.assertIn("empty-body: 1", report)
            self.assertIn("not graded — damaged text", report)
            self.assertIn("untraced-number: not graded", report)

    def test_copied_post_tabs_and_crlf_are_clean_but_metadata_tabs_are_not(self):
        with tempfile.TemporaryDirectory() as name:
            run = reply_fixtures.Run(Path(name))
            path = run.root / "posts" / "maren-quill.md"
            text = path.read_text(encoding="utf-8").replace("A synthetic", "A\tsynthetic")
            path.write_bytes(text.replace("\n", "\r\n").encode())
            self.assertEqual(0, self.invoke(discussion_reply_scan, [str(run.root)])[0])
            path.write_bytes(text.replace("AUTHOR:", "AUTHOR:\t").encode())
            status, report = self.invoke(discussion_reply_scan, [str(run.root)])
            self.assertEqual(1, status, report)
            self.assertIn("U+0009", report)

    def test_peer_claim_damage_keeps_independent_reference_and_heading_checks(self):
        with tempfile.TemporaryDirectory() as name:
            run = critique_fixtures.build_run(root=Path(name) / "run")
            (run / "claims.md").write_bytes(b"## CLAIM: \x07damaged\n")
            status, report = self.invoke(peer_critique_scan, [str(run)])
            self.assertEqual(1, status, report)
            self.assertIn("not graded — damaged text", report)
            self.assertNotIn("has no matching reference", report)

    def test_walk_json_damage_is_not_reported_as_missing_and_sibling_walks_still_grade(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            checks = root / "checks.md"
            checks.write_text("FIRST-DRAFT: 2099-01-01T00:00:00Z\n", encoding="utf-8")
            (root / "emergency-walk.json").write_bytes(br'{"sources":["C:\temp"],"entries":[],"none":"synthetic"}')
            (root / "bar-walk.json").write_text('{"entries": [], "none": "synthetic"}', encoding="utf-8")
            (root / "fact-trace.json").write_text('{"entries": [], "none": "synthetic"}', encoding="utf-8")
            status, report = self.invoke(checks_ledger, [str(checks), "--walks-only"])
            self.assertEqual(1, status, report)
            self.assertIn("U+0009", report)
            self.assertIn("routing-walk: 1", report)
            self.assertNotIn("emergency-walk.json: missing", report)

    def test_check_file_damage_does_not_hide_independent_walk_record_findings(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            checks, draft = root / "checks.md", root / "draft.md"
            checks.write_bytes(b"## CHECK: \x07damaged\n")
            draft.write_text("A synthetic document.\n", encoding="utf-8")
            status, report = self.invoke(checks_ledger, [str(checks), "--document", str(draft)])
            self.assertEqual(1, status, report)
            self.assertIn("U+0007", report)
            self.assertRegex(report, r"pre-review-walks\s+3")
            self.assertRegex(report, r"routing-walk\s+1")
            self.assertIn("missing-check", report)
            self.assertNotRegex(report, r"missing-check\s+[1-9]")

    def test_handwritten_reread_damage_precedes_its_machine_shape_and_keeps_independent_draft_grade(self):
        for content, expected in ((b"[]", 2), (b"[]\x07", 1)):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as name:
                run = post_fixtures.APostedInitialEntryHasItsOwnReading().posted_run(Path(name))
                (run.root / "reread.md").write_bytes(content)
                status, report, error = run.grade()
                self.assertEqual(expected, status, report + error)
                if expected == 1:
                    self.assertIn("U+0007", report)
                    self.assertNotIn("wrong shape", report + error)
                    self.assertIn("missing-posted-reading: not graded", report)

    def test_mixed_reread_items_never_inherit_the_old_sibling_approval(self):
        cutoff = completion_checks.registry()["run_record_reader:handwritten-damage"][0]
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "reread.md"
            text = "".join(
                f"## REREAD: {key}\nPOST-URL: https://example.org\nPOSTED: synthetic\nREAD: synthetic\n"
                f"SUBMISSION-SHA256: {'0' * 64}\nVERDICT: matches - synthetic\x07reading\n"
                for key in ("old", "unknown"))
            path.write_bytes(text.encode())
            seen = []
            def command():
                token = completion_checks.MOMENTS.set({"approval": cutoff - timedelta(microseconds=1)})
                items = completion_checks.ITEM_MOMENTS.set({"old": cutoff - timedelta(microseconds=1)})
                try:
                    seen.extend(discussion_artifact.read_posted_reading_file(path, artifacts=("old", "unknown")))
                    self.assertFalse(discussion_artifact.record_unavailable(path, "old"))
                    self.assertTrue(discussion_artifact.record_unavailable(path, "unknown"))
                    return 0
                finally:
                    completion_checks.ITEM_MOMENTS.reset(items)
                    completion_checks.MOMENTS.reset(token)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = run_grader.collect_record_errors(command)
            self.assertEqual(1, status, output.getvalue())
            self.assertEqual(["old"], [reading.artifact for reading in seen])
            self.assertIn("U+0007", output.getvalue())

    def test_heading_damage_withholds_its_own_missing_and_fingerprint_checks(self):
        with tempfile.TemporaryDirectory() as name:
            run = post_fixtures.Run(Path(name))
            path = run.root / "heading-read.md"
            path.write_bytes(path.read_bytes() + b"\x07")
            status, report, error = run.grade(bind_heading_read=False)
            self.assertEqual(1, status, report + error)
            self.assertIn("U+0007", report)
            self.assertIn("missing-heading-read: not graded", report)
            self.assertIn("heading-read-draft-mismatch: not graded", report)

    def test_editor_json_decoded_damage_is_withheld_before_text_comparison(self):
        with tempfile.TemporaryDirectory() as name:
            run = post_fixtures.Run(Path(name))
            html = run.root / "post.html"
            html.write_text(post_fixtures.post_html.render(post_fixtures.BODY), encoding="utf-8")
            run.record_canvas_render(html)
            path = run.root / "render" / "pass-1" / "editor-readback.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["html"] += "\x00"
            path.write_text(json.dumps(payload), encoding="utf-8")
            status, report, error = run.grade("--html", str(html))
            self.assertEqual(1, status, report + error)
            self.assertIn("U+0000", report)
            self.assertNotIn("visible block text differs", report)

    def test_every_walk_reader_refuses_raw_and_decoded_damage_without_fake_shape_findings(self):
        names = ("emergency-walk.json", "bar-walk.json", "fact-trace.json", "routing-walk.json")
        for filename in names:
            for character in ("\t", "\x07", "\x00", "\x0c", "\x0b", "\r"):
                with self.subTest(file=filename, code=ord(character)), tempfile.TemporaryDirectory() as name:
                    root = Path(name)
                    checks = root / "checks.md"
                    checks.write_text("FIRST-DRAFT: 2099-01-01T00:00:00Z\n", encoding="utf-8")
                    (root / 'bar.md').write_text(
                        'SOURCE-CLASSES: government\nRECENCY-WINDOW-YEARS: 5\nSUBMISSION-TYPE: file-upload\n',
                        encoding='utf-8')
                    with mock.patch.object(approval_record, 'verify_clinician_reply', return_value=
                            approval_record.ReplyVerification('not verified', 'synthetic transcript unavailable')):
                        signature = bar_signatures.sign(root, 'synthetic confirmation', skill='practicum-case-study')
                    for member in names:
                        (root / member).write_text(json.dumps({"entries": [], "none": "synthetic", "sources": ["synthetic"],
                            **({'bar_sha256': signature['sha256']} if member == 'bar-walk.json' else {})}), encoding="utf-8")
                    path = root / filename
                    path.write_bytes(path.read_bytes().replace(b'"none"', ('"no' + character + 'ne"').encode()))
                    status, report = self.invoke(checks_ledger, [str(checks), "--walks-only"])
                    self.assertEqual(1, status, report)
                    self.assertIn(f"U+{ord(character):04X}", report)
                    self.assertIn("walk findings 0", report)

    def test_reread_key_vocabulary_free_text_and_heading_refuse_each_damage_character(self):
        for character in ("\t", "\x07", "\x00", "\x0c", "\x0b", "\r"):
            for before, after in (("## REREAD:", "## RE" + character + "READ:"),
                                  ("VERDICT:", "VER" + character + "DICT:"),
                                  ("matches -", "mat" + character + "ches -"),
                                  ("The headings", "The head" + character + "ings")):
                with self.subTest(code=ord(character), position=before), tempfile.TemporaryDirectory() as name:
                    run = post_fixtures.APostedInitialEntryHasItsOwnReading().posted_run(Path(name))
                    path = run.root / "reread.md"
                    path.write_bytes(path.read_text(encoding="utf-8").replace(before, after, 1).encode())
                    status, report, error = run.grade()
                    self.assertEqual(1, status, report + error)
                    self.assertIn(f"U+{ord(character):04X}", report)
                    self.assertIn("missing-posted-reading: not graded", report)

    def test_damaged_policy_does_not_hide_an_independent_unknown_status(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            ledger_fixtures.write_bar(root)
            bar = root / "bar.md"
            bar.write_bytes(bar.read_bytes() + b"\x07")
            claims = root / "claims.md"
            claims.write_text(ledger_fixtures.ledger_text(ledger_fixtures.CLEAN.replace("STATUS: sourced", "STATUS: invented", 1)), encoding="utf-8")
            status, report = self.invoke(research_ledger, [str(claims)])
            self.assertEqual(1, status, report)
            self.assertRegex(report, r"unknown-status\s+1")
            self.assertIn("U+0007", report)

    def test_damaged_post_render_record_does_not_fabricate_an_absent_render(self):
        with tempfile.TemporaryDirectory() as name:
            run = post_fixtures.Run(Path(name))
            html = run.root / "post.html"
            html.write_text(post_fixtures.post_html.render(post_fixtures.BODY), encoding="utf-8")
            run.record_canvas_render(html)
            path = run.root / "post.md"
            path.write_bytes(path.read_bytes() + b"\x07")
            status, report, error = run.grade("--html", str(html), "--show")
            self.assertEqual(1, status, report + error)
            self.assertIn("rendered-pages: not graded", report)
            self.assertNotIn("no RENDERED record", report)

    def test_heading_digest_command_refuses_before_printing_a_damaged_claim(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "claims.md"
            path.write_bytes(b"## CLAIM: private-synthetic\x07heading\nSTATUS: sourced\n")
            status, report = self.invoke(research_ledger, [str(path), "--heading-digests"])
            self.assertEqual(1, status, report)
            self.assertIn("U+0007", report)
            self.assertNotIn("private-synthetic", report)


if __name__ == "__main__":
    unittest.main()
