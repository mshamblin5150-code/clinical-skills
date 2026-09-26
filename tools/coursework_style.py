"""Shared mechanical house-style checks for graded coursework bodies."""

from __future__ import annotations

from xml.etree import ElementTree

import docx_write
import run_grader


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PROHIBITED_NARRATIVE_KINDS = frozenset(("bullet", "numbered", "table"))
DECLARED_LIMITS = (
    (
        "style-inherited DOCX numbering",
        "The Word projection reads paragraph-level numPr and cannot recover numbering inherited only through a style.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "nested DOCX body containers",
        "The Word projection reads direct body paragraphs and tables; lists or tables nested in content controls are outside it.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
)


def narrative_blocks(markdown: str) -> tuple[docx_write.Block, ...]:
    """Return list and table blocks from a body using the renderer's parser."""

    return tuple(
        block
        for block in docx_write.blocks(markdown)
        if block.kind in PROHIBITED_NARRATIVE_KINDS
    )


def _paragraph_text(paragraph: ElementTree.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(W + "t")).strip()


def _paragraph_style(paragraph: ElementTree.Element) -> str:
    style = paragraph.find("./" + W + "pPr/" + W + "pStyle")
    return style.get(W + "val", "") if style is not None else ""


def docx_body_markdown(document: ElementTree.Element) -> str:
    """Project a DOCX body into the shared Markdown block grammar.

    The projection begins at the first Heading1 and ends before References. Native
    list paragraphs and tables become canonical Markdown forms; ordinary prose and
    block quotations retain their body role. The renderer parser remains the sole
    classifier of prohibited block kinds.
    """

    body = document.find(".//" + W + "body")
    if body is None:
        return ""
    lines: list[str] = []
    in_body = False
    for child in body:
        if child.tag == W + "p":
            text = _paragraph_text(child)
            style = _paragraph_style(child)
            if style == "Heading1":
                if text.casefold() == "references":
                    break
                in_body = True
                lines.extend((f"# {text}", ""))
                continue
            if not in_body or not text or style == "Caption":
                continue
            numbered = child.find("./" + W + "pPr/" + W + "numPr") is not None
            if style == "BlockQuotation":
                lines.append(f"> {text}")
            elif numbered:
                lines.append(f"- {text}")
            else:
                lines.append(text)
            lines.append("")
        elif child.tag == W + "tbl" and in_body:
            rows = []
            for row in child.findall(W + "tr"):
                cells = [
                    " ".join(
                        _paragraph_text(paragraph)
                        for paragraph in cell.iter(W + "p")
                        if _paragraph_text(paragraph)
                    )
                    for cell in row.findall(W + "tc")
                ]
                rows.append(cells)
            width = max((len(row) for row in rows), default=1)
            if rows:
                header = rows[0] + [""] * (width - len(rows[0]))
                lines.append("| " + " | ".join(header) + " |")
                lines.append("| " + " | ".join("---" for _ in range(width)) + " |")
                for row in rows[1:]:
                    lines.append("| " + " | ".join(row + [""] * (width - len(row))) + " |")
                lines.append("")
    return "\n".join(lines)


def docx_narrative_blocks(document: ElementTree.Element) -> tuple[docx_write.Block, ...]:
    """Return prohibited blocks from the graded DOCX body."""

    return narrative_blocks(docx_body_markdown(document))
