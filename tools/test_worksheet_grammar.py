"""Tests for the shared ``icd10-cpt`` worksheet grammar."""

import unittest
from pathlib import Path

import worksheet_grammar as grammar


ROOT = Path(__file__).resolve().parents[1]


class EntryLines(unittest.TestCase):
    def test_each_supported_code_system_opens_an_entry(self):
        text = (
            "ICD-10  J02.9  Acute pharyngitis, unspecified\n"
            "CPT  99406  Smoking and tobacco use cessation counseling\n"
            "HCPCS  J1100  Injection, dexamethasone sodium phosphate\n"
        )

        self.assertEqual(
            ["J02.9", "99406", "J1100"],
            [match.group("code") for match in grammar.ENTRY.finditer(text)],
        )

    def test_running_prose_does_not_supply_a_code(self):
        text = "CPT or E/M reference at all.\n"

        self.assertEqual([], list(grammar.ENTRY.finditer(text)))

    def test_not_for_entry_is_line_scoped_inside_the_bounded_entry_header(self):
        own_line = grammar.ENTRY.search(
            "ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY\n"
        )
        continued = grammar.ENTRY.search(
            "ICD-10  K27.9  Peptic ulcer, without\n"
            "               hemorrhage or perforation   NOT FOR ENTRY\n"
        )
        assert own_line is not None and continued is not None

        self.assertFalse(grammar.entry_is_for_entry(own_line.group(0), [own_line], 0))
        self.assertFalse(
            grammar.entry_is_for_entry(continued.string, [continued], 0)
        )


class DetailPairing(unittest.TestCase):
    def setUp(self):
        self.entry = grammar.ENTRY.search("ICD-10  J02.9  Acute pharyngitis, unspecified\n")
        assert self.entry is not None

    def test_indented_contiguous_lines_preserve_the_pair(self):
        text = (
            "ICD-10  J02.9  Acute pharyngitis, unspecified\n"
            '  ANCHOR: "sore throat"\n'
            "  SOURCE: filled - temperature\n"
        )
        entry = grammar.ENTRY.search(text)
        detail = grammar.FIELD.search(text, entry.end()) if entry else None
        assert entry is not None and detail is not None

        self.assertTrue(grammar.detail_belongs_to_entry(text, entry, detail))

    def test_a_blank_line_breaks_the_pair(self):
        text = (
            "ICD-10  J02.9  Acute pharyngitis, unspecified\n"
            "\n"
            "  SPECIFICITY: complete - no further axis\n"
        )
        entry = grammar.ENTRY.search(text)
        detail = grammar.FIELD.search(text, entry.end()) if entry else None
        assert entry is not None and detail is not None

        self.assertFalse(grammar.detail_belongs_to_entry(text, entry, detail))

    def test_an_unindented_line_breaks_the_pair(self):
        text = (
            "ICD-10  J02.9  Acute pharyngitis, unspecified\n"
            "prose between the entry and its detail\n"
            "  SPECIFICITY: complete - no further axis\n"
        )
        entry = grammar.ENTRY.search(text)
        detail = grammar.FIELD.search(text, entry.end()) if entry else None
        assert entry is not None and detail is not None

        self.assertFalse(grammar.detail_belongs_to_entry(text, entry, detail))

    def test_the_nearest_entry_is_the_only_candidate_owner(self):
        text = (
            "ICD-10  I10  Hypertension\n"
            "  ANCHOR: pressure\n"
            "\n"
            "ICD-10  J02.9  Acute pharyngitis, unspecified\n"
            "\n"
            "  SPECIFICITY: complete - no further axis\n"
        )
        entries = list(grammar.ENTRY.finditer(text))
        detail = list(grammar.FIELD.finditer(text))[-1]

        self.assertIsNone(grammar.paired_entry(text, entries, detail))


class OwnershipContract(unittest.TestCase):
    def test_shared_module_stays_a_library_without_console_setup(self):
        source = (ROOT / "tools" / "worksheet_grammar.py").read_text(encoding="utf-8")

        self.assertNotIn("use_utf8", source)
        self.assertNotIn("if __name__", source)

    def test_claude_documents_the_shared_grammar_and_orphan_semantics(self):
        prose = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertIn("### Worksheet grammar", prose)
        self.assertIn("tools/worksheet_grammar.py", prose)
        self.assertIn("orphaned detail line", prose)

    def test_refusal_scanner_intentionally_keeps_its_own_marker(self):
        source = (ROOT / "tools" / "refusal_scan.py").read_text(encoding="utf-8")

        self.assertIn("Intentionally local rather than imported", source)
        self.assertRegex(source, r"NOT_FOR_ENTRY\s*=\s*re\.compile")


if __name__ == "__main__":
    unittest.main()
