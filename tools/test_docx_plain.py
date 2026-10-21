"""ADR 0427: Review sheets share the guarded writer and use explicit page breaks."""

import contextlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import artifact_lock_test_support
import docx_write
import docx_word_probe
from repo_root import ForeignCheckout


class PlainReviewLayout(unittest.TestCase):
    def test_public_command_selects_plain_and_preserves_regular_numbered_content(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder) / "review.md", Path(folder) / "review.docx"
            source.write_text(docx_word_probe.REVIEW_PROBE, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(docx_write.main([str(source), str(target), "--layout", "plain"]), 0)
            with zipfile.ZipFile(target) as archive:
                document = ET.fromstring(archive.read("word/document.xml"))
                styles = ET.fromstring(archive.read("word/styles.xml"))
                self.assertEqual(set(archive.namelist()), docx_write.PART_NAMES)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = document.findall(".//w:body/w:p", ns)
            text = lambda p: "".join(p.itertext())
            numbered = next(p for p in paragraphs if text(p) == "Regular numbered entry")
            self.assertIsNone(numbered.find(".//w:b", ns))
            self.assertEqual(len(document.findall('.//w:br[@w:type="page"]', ns)), 1)
            self.assertIsNone(document.find(".//w:headerReference", ns))
            self.assertFalse(document.findall(".//w:ind", ns))
            self.assertFalse(document.findall(".//w:pageBreakBefore", ns))
            spacing = styles.find("w:docDefaults/w:pPrDefault/w:pPr/w:spacing", ns)
            self.assertEqual(spacing.get("{" + ns["w"] + "}line"), "240")

    def test_plain_retains_all_three_writer_protections(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "review.docx"
            with patch.object(docx_write, "ensure_main_checkout", side_effect=ForeignCheckout(target, Path(folder) / "main")):
                with self.assertRaises(ForeignCheckout):
                    docx_write.write_docx("body", target, layout="plain")
            target.write_bytes(b"human work")
            with self.assertRaises(docx_write.RefusedToOverwrite):
                docx_write.write_docx("body", target, layout="plain")
            from run_record_reader import OutboundTextError
            with self.assertRaises(OutboundTextError):
                docx_write.write_docx("bad\x01text", target, force=True, layout="plain")
            self.assertEqual(target.read_bytes(), b"human work")

    def test_invalid_layout_refuses_before_output(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(docx_write.main(["unused.md", "unused.docx", "--layout", "wrong"]), 2)

    def test_page_break_is_explicit_and_shared_by_the_parser(self):
        self.assertEqual([b.kind for b in docx_write.blocks(docx_write.PAGE_BREAK)], ["page-break"])
        self.assertIn('<w:br w:type="page"/>', docx_write.body_xml(docx_write.PAGE_BREAK))
        self.assertEqual(docx_write.parts("ordinary"), docx_write.parts("ordinary", layout="apa"))

    def test_plain_shape_stays_within_the_dated_word_measurement(self):
        record = Path(__file__).resolve().parents[1] / "skills/_shared/reference/word-renderer-calibration.json"
        row = json.loads(record.read_text(encoding="utf-8"))["review_rows"][docx_word_probe.REVIEW_KEY]
        self.assertEqual(row["renderer_shape"], docx_word_probe.review_renderer_shapes()[docx_word_probe.REVIEW_KEY])
        self.assertEqual(row["instrument"], "Microsoft Word COM")
        reading = row["word_observation"]
        self.assertEqual(reading["pages"], 2)
        paragraphs = {p["text"]: p for p in reading["paragraphs"]}
        for heading in ("Encounter One", "Encounter Two", "References"):
            self.assertEqual(paragraphs[heading]["bold"], -1)
            self.assertEqual(paragraphs[heading]["alignment"], 0)
        self.assertEqual(paragraphs["Encounter One"]["page"], 1)
        self.assertEqual(paragraphs["Encounter Two"]["page"], 2)
        for body in ("Regular body paragraph.", "Regular numbered entry", "Regular reference content."):
            self.assertEqual(paragraphs[body]["bold"], 0)
            self.assertEqual(paragraphs[body]["first_line_indent_points"],
                             -18 if body == "Regular numbered entry" else 0)
            self.assertEqual(paragraphs[body]["line_spacing_rule"], 0)
        self.assertEqual(reading["header"]["page_numbers"], 0)


if __name__ == "__main__":
    unittest.main()
