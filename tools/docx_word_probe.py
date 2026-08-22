"""Maintainer-only Word calibration for ``docx_write``'s APA renderer claims.

The command surface is added below; the calibration registry lives here first so the
reference sheet, the one-time Word record, and the Word-free renderer tripwires share
one exhaustive identity for every row.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

import docx_write
from console_codec import use_utf8


@dataclass(frozen=True)
class Calibration:
    key: str
    row_phrase: str
    verdict: str


CALIBRATIONS = (
    Calibration("body-defaults", "Times New Roman", "applied"),
    Calibration("reference-hanging-indent", "whole reference list", "applied"),
    Calibration("reference-no-extra-space", "No extra space", "applied"),
    Calibration("reference-heading-bold", "heading bold", "applied"),
    Calibration("reference-heading-centered", "heading centered", "applied"),
    Calibration("reference-heading-body-size", "body size", "applied"),
    Calibration("reference-page-break", "starts on a new page", "applied"),
    Calibration("page-number-header", "Page numbers", "applied"),
    Calibration(
        "singular-reference-hanging-indent",
        "singular `Reference` heading",
        "applied",
    ),
    Calibration("body-first-line-indent", "first-line indent", "applied"),
    Calibration("table-horizontal-rules", "horizontal rules only", "applied"),
    Calibration("title-page", "title page", "not applied"),
    Calibration("run-in-headings", "run-in", "not applied"),
    Calibration("reference-alphabetization", "alphabetized", "not applied"),
    Calibration("reference-single-paragraph", "one paragraph", "not applied"),
)


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
W = "{" + W_NS + "}"
R = "{" + R_NS + "}"

COMMON = (
    "# Clinical Case\n\n"
    "Body paragraph.\n\n"
    "- Bullet item\n\n"
    "| Drug | Dose |\n| --- | --- |\n| Rocephin | 500 mg |\n"
    "| Doxycycline | 100 mg |\n\n"
    "# References\n\nZulu, Z. (2025). Last.\n\nAlpha, A. (2025). First.\n"
)
SINGULAR = "# Clinical Case\n\nBody paragraph.\n\n# Reference\n\nOnly, O. (2025). Entry.\n"
RUN_IN = "#### Follow-up\n\nThe plan continues.\n"
HARD_WRAP = "# References\n\nRoss, J. (2025). Pelvic\ndisease. UpToDate.\n"
TITLE = "# Clinical Case\n\nBody paragraph.\n"

PROBES = {
    "body-defaults": COMMON,
    "reference-hanging-indent": COMMON,
    "reference-no-extra-space": COMMON,
    "reference-heading-bold": COMMON,
    "reference-heading-centered": COMMON,
    "reference-heading-body-size": COMMON,
    "reference-page-break": COMMON,
    "page-number-header": COMMON,
    "singular-reference-hanging-indent": SINGULAR,
    "body-first-line-indent": COMMON,
    "table-horizontal-rules": COMMON,
    "title-page": TITLE,
    "run-in-headings": RUN_IN,
    "reference-alphabetization": COMMON,
    "reference-single-paragraph": HARD_WRAP,
}


def _rendered_parts(markdown: str) -> dict[str, bytes]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "probe.docx"
        docx_write.write_docx(markdown, path)
        with zipfile.ZipFile(path) as archive:
            return {name: archive.read(name) for name in archive.namelist()}


def _root(parts: dict[str, bytes], name: str):
    return ElementTree.fromstring(parts[name])


def _attr(node, name: str, namespace: str = W):
    return None if node is None else node.get(namespace + name)


def _texts(root) -> list[str]:
    return [
        "".join(text.text or "" for text in paragraph.iter(W + "t"))
        for paragraph in root.iter(W + "p")
    ]


def _paragraph(root, text: str):
    for paragraph in root.iter(W + "p"):
        if "".join(node.text or "" for node in paragraph.iter(W + "t")) == text:
            return paragraph
    raise AssertionError("probe paragraph not rendered: " + text)


def _style(root, style_id: str):
    for style in root.findall(W + "style"):
        if _attr(style, "styleId") == style_id:
            return style
    raise AssertionError("probe style not rendered: " + style_id)


def _paragraph_style(paragraph) -> str | None:
    return _attr(paragraph.find("./" + W + "pPr/" + W + "pStyle"), "val")


def renderer_shapes() -> dict[str, dict]:
    """The XML shapes covered by the one-time Word measurements.

    These are deliberately semantic values rather than hashes. When one changes, the
    tripwire can name which renderer property left the measured set and a maintainer can
    decide whether Word must be asked again.
    """

    common = _rendered_parts(COMMON)
    document = _root(common, "word/document.xml")
    styles = _root(common, "word/styles.xml")
    header = _root(common, "word/header1.xml")
    defaults = styles.find("./" + W + "docDefaults")
    default_run = defaults.find("./" + W + "rPrDefault/" + W + "rPr")
    default_para = defaults.find("./" + W + "pPrDefault/" + W + "pPr")
    heading = _style(styles, "Heading1")
    reference = _style(styles, "Reference")
    reference_heading = _paragraph(document, "References")
    references = [
        _paragraph(document, "Zulu, Z. (2025). Last."),
        _paragraph(document, "Alpha, A. (2025). First."),
    ]
    page_margins = document.find(".//" + W + "sectPr/" + W + "pgMar")

    singular_parts = _rendered_parts(SINGULAR)
    singular_document = _root(singular_parts, "word/document.xml")
    singular_heading = _paragraph(singular_document, "Reference")
    singular_entry = _paragraph(singular_document, "Only, O. (2025). Entry.")

    run_in_document = _root(_rendered_parts(RUN_IN), "word/document.xml")
    hard_wrap_document = _root(_rendered_parts(HARD_WRAP), "word/document.xml")
    title_document = _root(_rendered_parts(TITLE), "word/document.xml")

    body_paragraph = _paragraph(document, "Body paragraph.")
    body_first_line = body_paragraph.find("./" + W + "pPr/" + W + "ind")
    table = document.find(".//" + W + "tbl")
    table_borders = table.find("./" + W + "tblPr/" + W + "tblBorders")
    header_cell_border = table.find(
        "./" + W + "tr/" + W + "tc/" + W + "tcPr/" + W + "tcBorders/" + W + "bottom"
    )

    return {
        "body-defaults": {
            "font": _attr(default_run.find(W + "rFonts"), "ascii"),
            "half_points": _attr(default_run.find(W + "sz"), "val"),
            "line_twips": _attr(default_para.find(W + "spacing"), "line"),
            "line_rule": _attr(default_para.find(W + "spacing"), "lineRule"),
            "margins_twips": {
                edge: _attr(page_margins, edge)
                for edge in ("top", "right", "bottom", "left")
            },
        },
        "reference-hanging-indent": {
            "entry_styles": [_paragraph_style(node) for node in references],
            "left_twips": _attr(reference.find("./" + W + "pPr/" + W + "ind"), "left"),
            "hanging_twips": _attr(
                reference.find("./" + W + "pPr/" + W + "ind"), "hanging"
            ),
        },
        "reference-no-extra-space": {
            "entry_styles": [_paragraph_style(node) for node in references],
            "after_twips": _attr(
                reference.find("./" + W + "pPr/" + W + "spacing"), "after"
            ),
            "line_twips": _attr(
                reference.find("./" + W + "pPr/" + W + "spacing"), "line"
            ),
        },
        "reference-heading-bold": {
            "paragraph_style": _paragraph_style(reference_heading),
            "bold_element": heading.find("./" + W + "rPr/" + W + "b") is not None,
        },
        "reference-heading-centered": {
            "paragraph_style": _paragraph_style(reference_heading),
            "style_alignment": _attr(
                heading.find("./" + W + "pPr/" + W + "jc"), "val"
            ),
            "direct_alignment": _attr(
                reference_heading.find("./" + W + "pPr/" + W + "jc"), "val"
            ),
        },
        "reference-heading-body-size": {
            "paragraph_style": _paragraph_style(reference_heading),
            "half_points": _attr(heading.find("./" + W + "rPr/" + W + "sz"), "val"),
        },
        "reference-page-break": {
            "page_break_before": reference_heading.find(
                "./" + W + "pPr/" + W + "pageBreakBefore"
            )
            is not None,
            "preceded_by_body": _texts(document).index("References")
            > _texts(document).index("Body paragraph."),
        },
        "page-number-header": {
            "relationship_id": _attr(
                document.find(".//" + W + "sectPr/" + W + "headerReference"),
                "id",
                R,
            ),
            "alignment": _attr(header.find(".//" + W + "jc"), "val"),
            "field": _attr(header.find(".//" + W + "fldSimple"), "instr"),
            "cached_text": "".join(node.text or "" for node in header.iter(W + "t")),
        },
        "singular-reference-hanging-indent": {
            "heading_style": _paragraph_style(singular_heading),
            "entry_style": _paragraph_style(singular_entry),
            "page_break_before": singular_heading.find(
                "./" + W + "pPr/" + W + "pageBreakBefore"
            )
            is not None,
        },
        "body-first-line-indent": {
            "body_first_line_twips": _attr(body_first_line, "firstLine"),
            "first_line_count": sum(
                paragraph.find("./" + W + "pPr/" + W + "ind") is not None
                and _attr(paragraph.find("./" + W + "pPr/" + W + "ind"), "firstLine")
                is not None
                for paragraph in document.iter(W + "p")
            ),
            "carve_out_styles": {
                text: _paragraph_style(_paragraph(document, text))
                for text in ("Clinical Case", "Bullet item", "Zulu, Z. (2025). Last.")
            },
        },
        "table-horizontal-rules": {
            "table_edges": {
                edge: _attr(table_borders.find(W + edge), "val")
                for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
            },
            "header_cell_bottom": _attr(header_cell_border, "val"),
            "style": _attr(table.find("./" + W + "tblPr/" + W + "tblStyle"), "val"),
        },
        "title-page": {"paragraphs": [text for text in _texts(title_document) if text]},
        "run-in-headings": {
            "paragraphs": [text for text in _texts(run_in_document) if text],
            "heading_style": _paragraph_style(_paragraph(run_in_document, "Follow-up")),
        },
        "reference-alphabetization": {
            "reference_paragraphs": [
                text
                for text in _texts(document)
                if text in ("Zulu, Z. (2025). Last.", "Alpha, A. (2025). First.")
            ]
        },
        "reference-single-paragraph": {
            "reference_paragraphs": [
                text
                for text in _texts(hard_wrap_document)
                if _paragraph_style(_paragraph(hard_wrap_document, text)) == "Reference"
            ]
        },
    }


def word_report() -> dict:
    """Render one probe per row, ask installed Word what it draws, and return JSON data."""

    script = Path(__file__).with_suffix(".ps1")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for key, markdown in PROBES.items():
            docx_write.write_docx(markdown, root / (key + ".docx"))
        docx_write.write_docx(TITLE, root / "word-saved.docx")
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-ProbeDirectory",
                str(root),
            ],
            check=False,
            capture_output=True,
            encoding="utf-8-sig",
        )
        if completed.returncode:
            print(completed.stderr.strip() or "Word COM probe failed", file=sys.stderr)
            raise RuntimeError("Word COM probe exited {n}".format(n=completed.returncode))
        report = json.loads(completed.stdout)
        saved_copy = Path(report.pop("saved_copy"))
        with zipfile.ZipFile(saved_copy) as archive:
            saved_parts = sorted(archive.namelist())
        original_parts = sorted(docx_write.PART_NAMES)
        report["word_save_part_set"] = {
            "original": original_parts,
            "saved": saved_parts,
            "added": sorted(set(saved_parts) - set(original_parts)),
            "removed": sorted(set(original_parts) - set(saved_parts)),
            "destination_guard_would_refuse": set(saved_parts) != set(original_parts),
        }
    report["renderer_shapes"] = renderer_shapes()
    return report


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["--shapes"]:
        print(
            json.dumps(
                {
                    "instrument": "renderer XML shape only; Word not opened",
                    "rows": renderer_shapes(),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args in ([], ["--word"]):
        try:
            print(json.dumps(word_report(), indent=2, sort_keys=True))
        except (OSError, RuntimeError, json.JSONDecodeError) as error:
            print("word probe: {e}".format(e=error), file=sys.stderr)
            return 2
        return 0
    print("usage: docx_word_probe.py [--word | --shapes]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main())
