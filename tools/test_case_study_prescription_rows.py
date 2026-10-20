"""Retyped ADR0366 controls, never copies of private finished drafts."""
# phi-scan: synthetic
import artifact_lock_test_support
import mechanics_test_support
import re
import unittest
from unittest import mock

import case_study_scan as scan
import test_case_study_scan as fixtures
import docx_write
import research_ledger
from grader_conformance import UnreadRemainderInput, unread_remainder_conformance

# Pin only unrelated mechanics rows, following the source fixture's own scope.
# The four ADR0366 rows still run through the native current command.
setUpModule, tearDownModule = mechanics_test_support.module_hooks()


def unread_remainder_input(root):
    partial, twin = root / "partial.md", root / "twin.md"
    partial.write_text(fixtures.CLEAN.replace("| --- | --- | --- |", ""), encoding="utf-8")
    twin.write_text(fixtures.CLEAN, encoding="utf-8")
    return UnreadRemainderInput((str(partial), "--paper-language", "en"),
        (str(twin), "--paper-language", "en"), lambda value: value.unread_remainder)


UnreadRemainderConformance = unread_remainder_conformance(scan)


def prescription(order, sig="Take one tablet daily for symptoms", refill="none"):
    return (fixtures.RX_TABLE.replace("Ceftriaxone 500 mg IM once", order)
            .replace("Inject 500 mg into the muscle one time for pelvic inflammatory disease", sig)
            .replace("Refill: none", "Refill: " + refill))


def draft(table=None, plan=""):
    text = fixtures.CLEAN.replace(fixtures.RX_TABLE, table or fixtures.RX_TABLE)
    return text.replace("1. Obtain a pregnancy test.", "1. " + (plan or "Obtain a pregnancy test."))


class WrittenPrescriptionRows(unittest.TestCase):
    def invoke(self, text, *, proposed=False):
        directory, path = fixtures.draft_file(text)
        self.addCleanup(directory.cleanup)
        if proposed:
            (path.parent / "proposed-2099-01-01.md").write_text(
                "PROPOSED: hydrocortisone dose remains unsettled", encoding="utf-8")
        status, report, error = fixtures.run([str(path), "--paper-language", "en"])
        self.assertFalse(error, error)
        return status, report

    def row_count(self, report, kind):
        match = re.search(r"(?m)^" + re.escape(kind) + r"\s+(\d+)$", report)
        self.assertIsNotNone(match, report)
        return int(match[1])

    def test_home_refills_literal_three_with_narrow_exceptions(self):
        kind = "home-medication-refill"
        base = "Continued home medication: metformin 500 mg PO daily until reassessment"
        for refill, expected in (("0", 1), ("none", 1), ("three", 1), ("3", 0)):
            with self.subTest(refill=refill):
                status, report = self.invoke(draft(prescription(base, refill=refill)))
                self.assertEqual(expected, self.row_count(report, kind))
                self.assertEqual(expected, status)
        for order in (base.replace("Continued home medication: ", ""),
                      base + " PRN", base + " as needed", base.replace("PO", "IV"),
                      base.replace("PO", "IM"), base.replace("daily", "once"),
                      base.replace("daily", "one-time dose")):
            with self.subTest(order=order):
                _, report = self.invoke(draft(prescription(order)))
                self.assertEqual(0, self.row_count(report, kind))
        _, report = self.invoke(draft(prescription(base.replace("daily", "once daily"))))
        self.assertEqual(1, self.row_count(report, kind))

    def test_prn_tablet_capsule_and_dose_limits_are_only_upper_bounds(self):
        kind = "prn-maximum-unreachable"
        for unit in ("tablets", "capsules"):
            for maximum, expected in (("ten", 1), ("8", 0), ("three", 0)):
                with self.subTest(unit=unit, maximum=maximum):
                    sig = f"Take two {unit} every six hours as needed; maximum {maximum} {unit} per day for pain"
                    status, report = self.invoke(draft(prescription("Exampledrug 100 mg PO PRN", sig)))
                    self.assertEqual(expected, self.row_count(report, kind))
                    self.assertEqual(expected, status)
        for maximum, expected in (("five", 1), ("three", 0)):
            status, report = self.invoke(draft(prescription(
                f"Exampledrug 100 mg PO every 6-8 hours PRN; max {maximum} doses/day")))
            self.assertEqual(expected, self.row_count(report, kind))
            self.assertEqual(expected, status)
        _, report = self.invoke(draft(prescription(
            "Exampledrug 100 mg PO every 6 hours PRN",
            "Take one tablet every eight hours as needed; max five doses per day for pain")))
        self.assertEqual(1, self.row_count(report, kind))

    def test_milligram_ceiling_and_unstated_intervals_stay_ungraded(self):
        for sig in ("Take two tablets every six hours as needed; max 4000 mg per day for pain",
                    "Take two tablets as needed; max ten tablets per day for pain"):
            status, report = self.invoke(draft(prescription("Exampledrug 100 mg PO PRN", sig)))
            self.assertEqual(0, status, report)
            self.assertEqual(0, self.row_count(report, "prn-maximum-unreachable"))

    def test_bare_pointer_refuses_and_named_decoration_remains_resolved(self):
        for pointer in ("item 3", "entry 3", "*Patient Education:* item 1",
                        "**Plan:** item 3", "Plan: item 3", "MDM entry 1"):
            with self.subTest(pointer=pointer):
                text = draft().replace("## References", "See " + pointer + ".\n\n## References")
                status, report = self.invoke(text)
                expected = int(pointer in {"item 3", "entry 3"})
                self.assertEqual(expected, status, report)
                self.assertEqual(expected, self.row_count(report, "unnamed-cross-reference"))

    def test_conditional_plan_order_needs_a_table_and_proposed_excuses_nothing(self):
        plan = "If itching persists, apply hydrocortisone 1% topical BID for 7 days."
        status, report = self.invoke(draft(plan=plan))
        self.assertEqual(1, status, report)
        self.assertEqual(1, self.row_count(report, "plan-order-without-table"))
        status, report = self.invoke(draft(plan=plan), proposed=True)
        self.assertEqual(1, status, report)
        self.assertEqual(1, self.row_count(report, "plan-order-without-table"))
        table = prescription("Delayed order: hydrocortisone 1% topical BID x 7 days")
        status, report = self.invoke(draft(table, plan))
        self.assertEqual(0, status, report)
        self.assertEqual(0, self.row_count(report, "plan-order-without-table"))

    def test_five_word_join_is_literal_and_does_not_grade_cited_mentions(self):
        for plan, expected in (("Start ceftriaxone 500 mg IM once.", 0),
                               ("Start Rocephin 500 mg IM once.", 1),
                               ("Ceftriaxone after these five unrelated intervening words 500 mg IM once.", 1),
                               ("Aspirin 81 mg was withheld because of bleeding risk (Example, 2025).", 0),
                               ("A guideline describes aspirin 81 mg for prevention (Example, 2025).", 0)):
            with self.subTest(plan=plan):
                _, report = self.invoke(draft(plan=plan))
                self.assertEqual(expected, self.row_count(report, "plan-order-without-table"))

    def test_unit_words_are_complete_and_attached_amounts_and_percent_still_fire(self):
        for plan, expected in (("Provide oral teaching to 2 groups daily.", 0),
                               ("Provide oral teaching to groups daily.", 0),
                               ("Apply unnameddrug 2 g topical daily.", 1),
                               ("Apply unnameddrug 2g topical daily.", 1),
                               ("Apply unnameddrug 2% topical daily.", 1)):
            with self.subTest(plan=plan):
                status, report = self.invoke(draft(plan=plan))
                self.assertEqual(expected, status, report)
                self.assertEqual(expected, self.row_count(report, "plan-order-without-table"))
                self.assertIn("unread remainder 0", report)

    def test_published_style_tables_and_literal_order_examples_pass_all_new_rows(self):
        style = fixtures.STYLE.read_text(encoding="utf-8")
        section = style[style.index("## 8. Rx"):]
        section = section[:section.index("\n## 9.")]
        tables = docx_write.markdown_tables(section)
        self.assertTrue(tables)
        examples = [text for text in re.findall(r"`([^`]+)`", section)
                    if re.search(r"\b(?:PO|IV|IM)\b", text)
                    and re.search(r"\b(?:mg|tablet)\b", text)
                    and ":" not in text[:text.find(" ")]]
        self.assertTrue(examples)
        examples += ["Continued home medication: " + value for value in examples
                     if value.startswith("prenatal vitamin")]
        for table in [*tables, *(prescription(order, refill="3") for order in examples)]:
            result = fixtures.survey(draft(table))
            self.assertFalse({f.kind for f in result.findings}.intersection({
                "home-medication-refill", "prn-maximum-unreachable", "unnamed-cross-reference",
                "plan-order-without-table"}))

    def test_zero_and_partial_reader_mutants_refuse_without_hiding_independent_findings(self):
        with mock.patch.object(research_ledger, "read_prescription_rows", return_value=[]):
            status, report = self.invoke(draft(plan="Start ceftriaxone 500 mg IM once."))
            self.assertEqual(2, status, report)
            self.assertIn("unread remainder 1", report)
            self.assertRegex(report, r"(?m)^home-medication-refill\s+not graded$")
            status, report = self.invoke(draft() + "\n- Independent bullet finding.\n")
            self.assertEqual(1, status, report)
            self.assertRegex(report, r"(?m)^bullet-marker\s+1$")
            self.assertIn("unread remainder 1", report)
        original = research_ledger.read_prescription_rows
        def one_table_only(rows):
            values = original(rows)
            return [rx for rx in values if rx.drug.lower() == "ceftriaxone"]
        extra = prescription("Continued home medication: metformin 500 mg PO daily until reassessment", refill="3")
        with mock.patch.object(research_ledger, "read_prescription_rows", side_effect=one_table_only):
            status, report = self.invoke(draft() + "\n" + extra)
        self.assertEqual(2, status, report)
        self.assertIn("prescription records: candidates 2, read 1, unread 1", report)
        self.assertIn("home labels: candidates 1, read 0, unread 1", report)
        self.assertIn("unread remainder 1", report)

    def test_renderer_only_table_drop_cannot_borrow_the_ledgers_independent_read(self):
        original = scan.read_sections
        text = draft(prescription("Continued home medication: metformin 500 mg PO daily until reassessment"),
                     "Continue metformin 500 mg PO daily.")
        def without_rx(value):
            sections, every = original(value)
            for section in sections:
                section.blocks[:] = [block for block in section.blocks if block.kind != "table"]
            return sections, [block for block in every if block.kind != "table"]
        with mock.patch.object(scan, "read_sections", side_effect=without_rx):
            status, report = self.invoke(text)
            self.assertEqual(2, status, report)
            self.assertIn("prescription records: candidates 1, read 0, unread 1", report)
            self.assertIn("unread remainder 1", report)
            self.assertRegex(report, r"(?m)^plan-order-without-table\s+not graded$")
            status, report = self.invoke(text + "\n- Independent bullet.\n")
            self.assertEqual(1, status, report)
            self.assertRegex(report, r"(?m)^bullet-marker\s+1$")
            self.assertIn("unread remainder 1", report)
        status, report = self.invoke(text)
        self.assertEqual(1, status, report)
        self.assertEqual(1, self.row_count(report, "home-medication-refill"))
        self.assertIn("prescription records: candidates 1, read 1, unread 0", report)


if __name__ == "__main__":
    unittest.main()
