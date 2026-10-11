"""ADR 0326 at the public research-ledger and reply commands.

phi-scan: synthetic
"""

import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import research_ledger
import file_digest
import discussion_reply_scan
from test_discussion_reply_scan import Run
from test_research_ledger import CLEAN, write_bar, replace_field, bind_tested_heading


def command(main, *args):
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        status = main(list(args))
    return status, output.getvalue()


class ClaimQualifiers(unittest.TestCase):
    def ledger(self, record, stamp="2026-10-11"):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_bar(root)
            path = root / "claims.md"
            path.write_text(f"DATE: {stamp}\n\n{record}", encoding="utf-8")
            return command(research_ledger.main, str(path), "--show")

    def qualified(self):
        text = replace_field(CLEAN, "PASSAGE", 'Table 1: "third-trimester" reference ranges in "normal pregnancy".')
        return text + 'QUALIFIERS: "third-trimester" | "normal pregnancy"\n'

    def test_a_dropped_heading_qualifier_fails_the_command(self):
        text = self.qualified().replace("within the third-trimester reference", "within the reference")
        status, report = self.ledger(bind_tested_heading(text))
        self.assertEqual(1, status)
        self.assertIn("qualifier-heading-missing", report)

    def test_a_dropped_restatement_or_passage_qualifier_fails(self):
        for field, kind in (("RESTATEMENT", "restatement"), ("PASSAGE", "passage")):
            with self.subTest(field=field):
                text = replace_field(self.qualified(), field, "A third-trimester range.")
                status, report = self.ledger(text)
                self.assertEqual(1, status)
                self.assertIn(f"qualifier-{kind}-missing", report)

    def test_none_is_explicit_and_absence_obeys_the_cutoff(self):
        self.assertEqual(0, self.ledger(CLEAN + "QUALIFIERS: none\n")[0])
        status, report = self.ledger(CLEAN)
        self.assertEqual(1, status)
        self.assertIn("qualifier-field", report)
        status, report = self.ledger(CLEAN, "2026-10-10")
        self.assertEqual(0, status)
        self.assertRegex(report, r"qualifier-field\s+not graded - unread 1")

    def test_matching_ignores_only_case_and_whitespace(self):
        text = self.qualified().replace('"normal pregnancy"\n', '"NORMAL   PREGNANCY"\n')
        self.assertEqual(0, self.ledger(text)[0])

    def test_a_committed_real_claim_is_the_positive_control(self):
        skill = (Path(__file__).resolve().parents[1] / "skills/practicum-case-study/SKILL.md").read_text(encoding="utf-8")
        block = re.search(r"```\nDATE: 2026-08-19\n\n(## CLAIM: .*?)\n```", skill, re.S).group(1)
        block = re.sub(r"(?m)^DROPPED:.*\n?", "", block)
        status, report = self.ledger(block + '\nQUALIFIERS: "third-trimester"\n')
        self.assertEqual(0, status, report)

    def test_malformed_qualifiers_and_sourceless_fields_fail(self):
        for value in ('', 'third-trimester', '""', '"third-trimester" | none'):
            with self.subTest(value=value):
                status, report = self.ledger(CLEAN + f"QUALIFIERS: {value}\n")
                self.assertEqual(1, status)
                self.assertIn("qualifier-field", report)
        for status in ("unsourced - searched and found no support", "unreadable - routes failed"):
            text = f"## CLAIM: A question.\nSTATUS: {status}\nQUALIFIERS: none\n"
            _, report = self.ledger(text)
            self.assertIn("sourceless-with-source-field", report)

    def test_a_dropped_record_owes_no_qualifier_field(self):
        self.assertEqual(0, self.ledger(CLEAN + "DROPPED: draft no longer claims it\n")[0])


class HeadingQualifiersAndItems(unittest.TestCase):
    def reply(self, *, count="1 of 1", items=("opened-post",), item_count=1, stamp="2026-10-11", qualifier=True, finding="", sentence_line=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            Run(root)
            claims = root / "claims.md"
            text = re.sub(r"(?m)^DATE:.*$", f"DATE: {stamp}", claims.read_text(encoding="utf-8"))
            if qualifier:
                text += 'QUALIFIERS: "combined"\n'
            claims.write_text(text, encoding="utf-8")
            context = root / "project-context.md"
            context.write_text(context.read_text(encoding="utf-8") + '\n## PLACE: posts\nSTATE: read\nOPENED: opened-post | SHA256: ' + "a" * 64 + "\n", encoding="utf-8")
            draft = root / "response-maren.md"
            suffix = f" | qualifiers {count}" if count is not None else ""
            sentences = sentence_line or f"1 factual, 0 clinician's own, {item_count} item"
            (root / "heading-read.md").write_text(
                f"## HEADING-READ: {draft.name}\nDRAFT: {file_digest.sha256(draft)}\n"
                "ROUTE: separate context\n"
                + f"SENTENCES: {sentences}\n"
                + f"PAIR: paragraph 1 -> fd25d4de{suffix}\n"
                + "".join(f"ITEM: paragraph {index + 2} -> {item}\n" for index, item in enumerate(items))
                + "CONTEXT-DIGEST: e9480117c1477001f65666233ed4ef160c1544873d6184ff730a83380429f1bf\nCONTEXT-VERDICT: agrees\nVERDICT: clean\n"
                + (f"FINDINGS: {finding}\n" if finding else ""), encoding="utf-8")
            return command(discussion_reply_scan.main, folder)

    def test_a_complete_pair_and_opened_item_pass(self):
        status, report = self.reply()
        self.assertEqual(0, status, report)

    def test_short_pair_count_needs_a_finding(self):
        status, report = self.reply(count="0 of 1")
        self.assertEqual(1, status)
        self.assertIn("heading-read-qualifier-count: 1", report)

    def test_missing_item_or_unopened_item_is_refused(self):
        for kwargs, kind in (({"items": ()}, "item-count"), ({"items": ("unopened",)}, "unopened-item")):
            with self.subTest(kind=kind):
                status, report = self.reply(**kwargs)
                self.assertEqual(1, status)
                self.assertIn(f"heading-read-{kind}: 1", report)

    def test_missing_wrong_and_impossible_pair_counts_fail(self):
        for count in (None, "1 of 2", "2 of 1"):
            with self.subTest(count=count):
                status, report = self.reply(count=count)
                self.assertEqual(1, status)
                self.assertIn("heading-read-qualifier-count: 1", report)

    def test_a_reported_shortfall_is_a_finding_without_double_counting(self):
        status, report = self.reply(count="0 of 1", finding="drifted - paragraph 1, combined was dropped")
        self.assertEqual(1, status)
        self.assertIn("heading-read-finding: 1", report)
        self.assertIn("heading-read-qualifier-count: 0", report)
        self.assertIn("heading-read-sentence-count: 0", report)

    def test_the_third_class_obeys_the_ledger_cutoff(self):
        line = "1 factual, 0 clinician's own"
        status, report = self.reply(sentence_line=line, items=(), item_count=0)
        self.assertEqual(1, status)
        self.assertIn("heading-read-item-count: 1", report)
        status, report = self.reply(sentence_line=line, items=(), item_count=0, stamp="2026-10-10", qualifier=False, count=None)
        self.assertEqual(0, status, report)
        self.assertIn("item-description comparisons: not graded - unread 1", report)
        self.assertIn("qualifier pair counts: not graded - unread 1", report)

    def test_legacy_pairs_owe_a_count_when_the_claim_has_the_field(self):
        status, report = self.reply(stamp="2026-10-10", count=None)
        self.assertEqual(1, status)
        self.assertIn("heading-read-qualifier-count: 1", report)

    def test_legacy_item_lines_are_not_graded(self):
        status, report = self.reply(stamp="2026-10-10", qualifier=False, count=None, items=("unopened",))
        self.assertEqual(0, status, report)
        self.assertIn("item-description comparisons: not graded - unread 1", report)


if __name__ == "__main__":
    unittest.main()
