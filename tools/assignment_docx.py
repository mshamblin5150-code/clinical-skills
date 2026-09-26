#!/usr/bin/env python3
"""Build the rich Word artifact owned by the course-assignment DOCX branch."""

from __future__ import annotations

import binascii
import json
import os
import struct
import sys
import zipfile
import zlib
from dataclasses import dataclass
from pathlib import Path

import docx_write
from console_codec import require_python_floor, use_utf8
from repo_root import ensure_main_checkout, main_repo_root, output_root


PALE_BLUE = "EAF2F8"
FINGERPRINT_FILE = "assignment-docx.sha256"


@dataclass(frozen=True)
class TitlePage:
    title: str
    author: str
    credentials: str
    institution: str
    course: str
    instructor: str
    due_date: str


@dataclass(frozen=True)
class Section:
    heading: str
    paragraphs: tuple[str, ...]


@dataclass(frozen=True)
class CommandRow:
    role: str
    responsibility: str
    decision_right: str


@dataclass(frozen=True)
class AssignmentSpec:
    title_page: TitlePage
    sections: tuple[Section, ...]
    command_rows: tuple[CommandRow, ...]
    relationship_labels: tuple[str, str, str]
    references: tuple[str, ...]
    figure_alt_text: str


def fixture_spec() -> AssignmentSpec:
    """Return a generic, PII-free fixture that exercises every rich feature."""

    return AssignmentSpec(
        title_page=TitlePage(
            "[DOCUMENT TITLE]",
            "[AUTHOR]",
            "[CREDENTIAL ONE] | [CREDENTIAL TWO] | [CREDENTIAL THREE] | [CREDENTIAL FOUR]",
            "[INSTITUTION]",
            "[COURSE]",
            "[INSTRUCTOR]",
            "[DUE DATE]",
        ),
        sections=(
            Section(
                "Purpose and Scope",
                (
                    "This generic fixture demonstrates a reusable academic document structure.",
                    "The example connects authority, coordination, and feedback (Example Agency, 2025).",
                ),
            ),
        ),
        command_rows=(
            CommandRow("Sponsor", "Sets intent", "Approves direction"),
            CommandRow("Coordinator", "Aligns work", "Resolves dependencies"),
            CommandRow("Team", "Executes work", "Escalates constraints"),
        ),
        relationship_labels=("Intent", "Coordination", "Feedback"),
        references=(
            "Example Agency. (2025). *Systems coordination brief*. https://example.invalid/brief",
        ),
        figure_alt_text="Generic system relationship diagram",
    )


def _xml_paragraph(
    text: str,
    *,
    style: str = "",
    align: str = "",
    first_line: bool = False,
    keep_next: bool = False,
    page_break_before: bool = False,
    fit_text: bool = False,
) -> str:
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if keep_next:
        props.append("<w:keepNext/>")
    if page_break_before:
        props.append("<w:pageBreakBefore/>")
    if first_line:
        props.append('<w:ind w:firstLine="720"/>')
    if align:
        props.append(f'<w:jc w:val="{align}"/>')
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>" if props else ""
    run_props = '<w:fitText w:val="9000"/>' if fit_text else ""
    rpr = f"<w:rPr>{run_props}</w:rPr>" if run_props else ""
    if fit_text:
        body = (
            f"<w:r>{rpr}<w:t xml:space=\"preserve\">"
            f"{docx_write.esc(text)}</w:t></w:r>"
        )
    else:
        body = docx_write.runs(text)
    return f"<w:p>{ppr}{body}</w:p>"


def _command_narrative(rows: tuple[CommandRow, ...]) -> tuple[str, ...]:
    return tuple(
        f"{row.role}: {row.responsibility}. Decision right: {row.decision_right}."
        for row in rows
    )


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _relationship_png() -> bytes:
    """Return a deterministic three-node relationship diagram."""

    width, height = 640, 220
    pixels = [bytearray([255, 255, 255] * width) for _ in range(height)]

    def rect(left: int, top: int, right: int, bottom: int, color: tuple[int, int, int]) -> None:
        for y in range(top, bottom):
            row = pixels[y]
            for x in range(left, right):
                row[x * 3 : x * 3 + 3] = bytes(color)

    def line(x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int]) -> None:
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for step in range(steps + 1):
            x = round(x1 + (x2 - x1) * step / steps)
            y = round(y1 + (y2 - y1) * step / steps)
            rect(max(0, x - 2), max(0, y - 2), min(width, x + 3), min(height, y + 3), color)

    node = (35, 78, 112)
    accent = (90, 151, 197)
    for left in (40, 240, 440):
        rect(left, 60, left + 160, 160, node)
        rect(left + 8, 68, left + 152, 152, (234, 242, 248))
    line(200, 110, 240, 110, accent)
    line(400, 110, 440, 110, accent)
    line(436, 106, 440, 110, accent)
    line(436, 114, 440, 110, accent)
    line(236, 106, 240, 110, accent)
    line(236, 114, 240, 110, accent)
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )


def _drawing(alt_text: str) -> str:
    return (
        '<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="5486400" cy="1885950"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="1" name="System relationship figure" descr="{alt}"/>'
        '<wp:cNvGraphicFramePr/><a:graphic><a:graphicData '
        'uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="relationship.png"/>'
        '<pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rId4"/>'
        '<a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr>'
        '<a:xfrm><a:off x="0" y="0"/><a:ext cx="5486400" cy="1885950"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
        '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
    ).format(alt=docx_write.esc(alt_text))


def _styles() -> str:
    additions = (
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
        '<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:jc w:val="center"/>'
        '<w:spacing w:before="0" w:after="240"/></w:pPr><w:rPr><w:b/>'
        '<w:color w:val="000000"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/>'
        '<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr>'
        '<w:rPr><w:color w:val="30343B"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/>'
        '<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="80" '
        'w:after="200"/><w:jc w:val="center"/></w:pPr><w:rPr><w:i/>'
        '<w:color w:val="30343B"/><w:sz w:val="20"/></w:rPr></w:style>'
    )
    return docx_write.STYLES.replace("</w:styles>", additions + "</w:styles>")


def _body(spec: AssignmentSpec) -> str:
    title = spec.title_page
    out = [
        _xml_paragraph(title.title, style="Title"),
        _xml_paragraph(title.author, style="Subtitle"),
        _xml_paragraph(
            title.credentials,
            align="center",
            fit_text=len(title.credentials) > 55,
        ),
        _xml_paragraph(title.institution, align="center"),
        _xml_paragraph(title.course, align="center"),
        _xml_paragraph(title.instructor, align="center"),
        _xml_paragraph(title.due_date, align="center"),
    ]
    for index, section in enumerate(spec.sections):
        out.append(
            _xml_paragraph(
                section.heading,
                style="Heading1",
                page_break_before=index == 0,
            )
        )
        out.extend(_xml_paragraph(text, first_line=True) for text in section.paragraphs)
    out.extend(
        (
            _xml_paragraph("Command Matrix", style="Heading1"),
            *(_xml_paragraph(text, first_line=True) for text in _command_narrative(spec.command_rows)),
            _xml_paragraph("System Relationships", style="Heading1"),
            _xml_paragraph(
                "Figure 1 " + " to ".join(spec.relationship_labels), style="Caption"
            ),
            _drawing(spec.figure_alt_text),
            _xml_paragraph(
                "The figure connects " + ", ".join(spec.relationship_labels) + ".",
                first_line=True,
            ),
            _xml_paragraph("References", style="Heading1", page_break_before=True),
        )
    )
    out.extend(_xml_paragraph(reference, style="Reference") for reference in spec.references)
    return "".join(out)


def parts(spec: AssignmentSpec) -> dict[str, str | bytes]:
    body = _body(spec)
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<w:body>{body}<w:sectPr><w:headerReference w:type="default" r:id="rId3"/>'
        '<w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" '
        'w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
        '</w:sectPr></w:body></w:document>'
    )
    content_types = docx_write.CONTENT_TYPES.replace(
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    )
    root_rels = docx_write.ROOT_RELS.replace(
        "</Relationships>",
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>",
    )
    doc_rels = docx_write.DOC_RELS.replace(
        "</Relationships>",
        '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/relationship.png"/>'
        "</Relationships>",
    )
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>{title}</dc:title>'
        '<dc:creator>{author}</dc:creator></cp:coreProperties>'
    ).format(
        title=docx_write.esc(spec.title_page.title),
        author=docx_write.esc(spec.title_page.author),
    )
    app = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        '<Application>Clinical Skills Course Assignment</Application></Properties>'
    )
    return {
        "[Content_Types].xml": content_types,
        "_rels/.rels": root_rels,
        "docProps/core.xml": core,
        "docProps/app.xml": app,
        "word/_rels/document.xml.rels": doc_rels,
        "word/styles.xml": _styles(),
        "word/numbering.xml": docx_write.numbering_xml(0),
        "word/header1.xml": docx_write.HEADER,
        "word/document.xml": document,
        "word/media/relationship.png": _relationship_png(),
    }


def build(spec: AssignmentSpec, destination: Path, *, force: bool = False) -> Path:
    """Atomically write one deterministic rich DOCX package."""

    destination = ensure_main_checkout(destination)
    root = main_repo_root().resolve()
    allowed = (output_root() / "course-assignments").resolve()
    if destination.is_relative_to(root) and not destination.is_relative_to(allowed):
        raise ValueError(
            "finished course assignments belong under output/course-assignments"
        )
    if destination.exists() and not force:
        raise ValueError(
            f"refusing to overwrite {destination}; recover any edits, then pass --force"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(f"{destination.name}.{os.getpid()}.building")
    partial.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, payload in parts(spec).items():
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, payload.encode("utf-8") if isinstance(payload, str) else payload)
        os.replace(partial, destination)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return destination


def from_mapping(value: object) -> AssignmentSpec:
    """Read the narrow JSON-compatible interface for one assignment artifact."""

    if not isinstance(value, dict):
        raise ValueError("assignment specification must be an object")
    try:
        title = TitlePage(**value["title_page"])
        sections = tuple(
            Section(item["heading"], tuple(item["paragraphs"]))
            for item in value["sections"]
        )
        command_rows = tuple(CommandRow(**item) for item in value["command_rows"])
        relationship_labels = tuple(value["relationship_labels"])
        references = tuple(value["references"])
        figure_alt_text = value["figure_alt_text"]
    except (KeyError, TypeError) as failure:
        raise ValueError(f"invalid assignment specification: {failure}") from failure
    if len(relationship_labels) != 3:
        raise ValueError("relationship_labels must contain exactly three labels")
    string_values = (
        *title.__dict__.values(),
        *(section.heading for section in sections),
        *(paragraph for section in sections for paragraph in section.paragraphs),
        *(field for row in command_rows for field in row.__dict__.values()),
        *relationship_labels,
        *references,
        figure_alt_text,
    )
    if not all(isinstance(item, str) and item.strip() for item in string_values):
        raise ValueError("every assignment specification text value must be nonempty")
    if not sections or not command_rows or not references:
        raise ValueError("sections, command_rows, and references must be nonempty")
    return AssignmentSpec(
        title,
        sections,
        command_rows,
        relationship_labels,
        references,
        figure_alt_text,
    )


def main(argv: list[str]) -> int:
    force = argv.count("--force") == 1
    if argv.count("--force") > 1:
        print("--force may appear only once", file=sys.stderr)
        return 2
    positional = [value for value in argv if value != "--force"]
    if len(positional) != 2:
        print(
            "usage: assignment_docx.py <assignment.json> <output.docx> [--force]",
            file=sys.stderr,
        )
        return 2
    source, destination = Path(positional[0]), Path(positional[1])
    if not source.is_file():
        print(f"no assignment specification at {source}", file=sys.stderr)
        return 2
    if destination.suffix.casefold() != ".docx":
        print("output must end in .docx", file=sys.stderr)
        return 2
    try:
        spec = from_mapping(json.loads(source.read_text(encoding="utf-8")))
        build(spec, destination, force=force)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as failure:
        print(f"document was not written: {failure}", file=sys.stderr)
        return 2
    print(f"wrote {destination}")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
