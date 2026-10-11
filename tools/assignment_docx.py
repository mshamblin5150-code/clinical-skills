#!/usr/bin/env python3
"""Build the rich Word artifact owned by the course-assignment DOCX branch."""

from __future__ import annotations

import json
import os
import struct
import sys
import zipfile
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
    figure_image: str
    references: tuple[str, ...]
    figure_alt_text: str
    figure_title: str = ""
    figure_note: str = ""

    @property
    def has_figure(self) -> bool:
        """A figure is supplied by the run, or omitted."""
        return bool(self.figure_image)


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
        figure_image=str(Path(__file__).resolve().parent.parent / "fixtures/assignment-figure.png"),
        references=(
            "Example Agency. (2025). *Systems coordination brief*. https://example.invalid/brief",
        ),
        figure_alt_text="Generic system relationship diagram",
        figure_title="Intent, Coordination, and Feedback",
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


def image_dimensions(data: bytes) -> tuple[str, int, int]:
    """Read PNG or JPEG dimensions without a consumer imaging dependency."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 33 and data[12:16] == b"IHDR":
        width, height = struct.unpack(">II", data[16:24])
        if width and height:
            return "png", width, height
    if data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 4 <= len(data):
            if data[offset] != 0xFF:
                break
            while offset < len(data) and data[offset] == 0xFF:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                continue
            if marker in (0xD9, 0xDA) or offset + 2 > len(data):
                break
            size = int.from_bytes(data[offset:offset + 2], "big")
            if size < 2 or offset + size > len(data):
                break
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF) and size >= 8:
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                if width and height:
                    return "jpeg", width, height
            offset += size
    raise ValueError("figure_image must be a PNG or JPEG with readable positive dimensions")


def _drawing(alt_text: str, extension: str, width: int, height: int) -> str:
    cx = 5943600  # 6.5 inch text width at one inch margins.
    cy = round(cx * height / width)
    return (
        '<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="1" name="System relationship figure" descr="{alt}"/>'
        '<wp:cNvGraphicFramePr/><a:graphic><a:graphicData '
        'uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="figure.{extension}"/>'
        '<pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rId4"/>'
        '<a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr>'
        '<a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
        '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
    ).format(alt=docx_write.esc(alt_text), cx=cx, cy=cy, extension=extension)


def _styles() -> str:
    additions = (
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
        '<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:jc w:val="center"/>'
        '<w:spacing w:before="0" w:after="0"/></w:pPr><w:rPr><w:b/>'
        '<w:color w:val="000000"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/>'
        '<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr>'
        '<w:rPr><w:color w:val="000000"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/>'
        '<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="0" '
        'w:after="0"/></w:pPr><w:rPr>'
        '<w:color w:val="000000"/></w:rPr></w:style>'
    )
    return docx_write.STYLES.replace("</w:styles>", additions + "</w:styles>")


def _body(spec: AssignmentSpec, image: tuple[str, int, int] | None = None) -> str:
    title = spec.title_page
    out = [
        *(_xml_paragraph("", keep_next=True) for _ in range(3)),
        _xml_paragraph(title.title, style="Title"),
        _xml_paragraph("", keep_next=True),
        _xml_paragraph(title.author, style="Subtitle"),
        *([_xml_paragraph(
            title.credentials,
            align="center",
            fit_text=len(title.credentials) > 55,
        )] if title.credentials else []),
        _xml_paragraph(title.institution, align="center"),
        _xml_paragraph(title.course, align="center"),
        _xml_paragraph(title.instructor, align="center"),
        _xml_paragraph(title.due_date, align="center"),
        _xml_paragraph(title.title, style="Title", page_break_before=True),
    ]
    for index, section in enumerate(spec.sections):
        out.append(
            _xml_paragraph(
                section.heading,
                style="Heading1",
            )
        )
        out.extend(_xml_paragraph(text, first_line=True) for text in section.paragraphs)
    if spec.command_rows:
        out.append(_xml_paragraph("Command Matrix", style="Heading1"))
        out.extend(
            _xml_paragraph(text, first_line=True)
            for text in _command_narrative(spec.command_rows)
        )
    if spec.has_figure:
        out.extend(
            (
                _xml_paragraph("**Figure 1**", style="Caption"),
                _xml_paragraph("*" + spec.figure_title + "*", style="Caption"),
                _drawing(spec.figure_alt_text, *image),
            )
        )
        if spec.figure_note:
            out.append(_xml_paragraph("*Note.* " + spec.figure_note, style="Caption"))
    out.append(_xml_paragraph("References", style="Heading1", page_break_before=True))
    out.extend(_xml_paragraph(reference, style="Reference") for reference in spec.references)
    return "".join(out)


def parts(spec: AssignmentSpec) -> dict[str, str | bytes]:
    image_bytes = Path(spec.figure_image).read_bytes() if spec.has_figure else None
    image = image_dimensions(image_bytes) if image_bytes is not None else None
    body = _body(spec, image)
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
        '<Default Extension="xml" ContentType="application/xml"/>' +
        (f'<Default Extension="{image[0]}" ContentType="image/{image[0]}"/>' if image else '') +
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    )
    root_rels = docx_write.ROOT_RELS.replace(
        "</Relationships>",
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>",
    )
    doc_rels = docx_write.DOC_RELS
    if spec.has_figure:
        doc_rels = doc_rels.replace(
            "</Relationships>",
            f'<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/figure.{image[0]}"/>'
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
    package: dict[str, str | bytes] = {
        "[Content_Types].xml": content_types,
        "_rels/.rels": root_rels,
        "docProps/core.xml": core,
        "docProps/app.xml": app,
        "word/_rels/document.xml.rels": doc_rels,
        "word/styles.xml": _styles(),
        "word/numbering.xml": docx_write.numbering_xml(0),
        "word/header1.xml": docx_write.HEADER,
        "word/document.xml": document,
    }
    if spec.has_figure:
        package[f"word/media/figure.{image[0]}"] = image_bytes
    return package


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
    if "relationship_labels" in value:
        raise ValueError("relationship_labels is retired; supply figure_image, figure_title, and figure_alt_text")
    figure_keys = ("figure_image", "figure_title", "figure_alt_text")
    if any(key in value for key in figure_keys) and not all(key in value for key in figure_keys):
        raise ValueError("figure_image, figure_title, and figure_alt_text are supplied together or not at all")
    try:
        title = TitlePage(**value["title_page"])
        sections = tuple(
            Section(item["heading"], tuple(item["paragraphs"]))
            for item in value["sections"]
        )
        command_rows = tuple(CommandRow(**item) for item in value.get("command_rows", ()))
        figure_image = value.get("figure_image", "")
        references = tuple(value["references"])
        figure_alt_text = value.get("figure_alt_text", "")
        figure_title = value.get("figure_title", "")
        figure_note = value.get("figure_note", "")
    except (KeyError, TypeError) as failure:
        raise ValueError(f"invalid assignment specification: {failure}") from failure
    if "figure_note" in value and "figure_image" not in value:
        raise ValueError("figure_note requires figure_image, figure_title, and figure_alt_text")
    string_values = (
        *(text for key, text in title.__dict__.items() if key != "credentials"),
        *(section.heading for section in sections),
        *(paragraph for section in sections for paragraph in section.paragraphs),
        *(field for row in command_rows for field in row.__dict__.values()),
        *references,
        *((figure_image, figure_title, figure_alt_text) if "figure_image" in value else ()),
        *((figure_note,) if "figure_note" in value else ()),
    )
    if not all(isinstance(item, str) and item.strip() for item in string_values):
        raise ValueError("every assignment specification text value must be nonempty")
    if not isinstance(title.credentials, str):
        raise ValueError("title_page credentials must be text; an empty string omits the line")
    if not sections or not references:
        raise ValueError("sections and references must be nonempty")
    return AssignmentSpec(
        title,
        sections,
        command_rows,
        figure_image,
        references,
        figure_alt_text,
        figure_title,
        figure_note,
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
        value = json.loads(source.read_text(encoding="utf-8"))
        spec = from_mapping(value)
        if spec.has_figure and not Path(spec.figure_image).is_absolute():
            from dataclasses import replace
            spec = replace(spec, figure_image=str(source.parent / spec.figure_image))
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
