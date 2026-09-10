#!/usr/bin/env python3
"""Render the repository's Markdown subset as a Canvas HTML submission.

The block and inline grammars belong to ``docx_write``. This module chooses
HTML tags and writes the exact bytes loaded into Canvas's raw editor; it does
not parse Markdown independently.

A URL outside a code span becomes an anchor whose text is the URL itself, so
every reference can be followed from the board rather than depending on the
editor to link it (#1039).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import docx_write
from console_codec import use_utf8


USAGE = "usage: post_html.py <in.md> <out.html>"
URL = re.compile(r"https?://[^\s<>\"]+")
URL_TRAILING_PUNCTUATION = ".,;:!?"


def _text_node(text: str) -> str:
    """Escape text while retaining comment delimiters for residue grading."""

    return docx_write.esc(text).replace("&lt;!--", "<!--").replace("--&gt;", "-->")


def _url_end(url: str) -> str:
    """Drop sentence punctuation and an unbalanced closing parenthesis from a URL's tail."""

    while url and (
        url[-1] in URL_TRAILING_PUNCTUATION
        or (url[-1] == ")" and url.count(")") > url.count("("))
    ):
        url = url[:-1]
    return url


def _linked_text(text: str) -> str:
    """Escape text and wrap each URL in an anchor whose text is the URL."""

    out: list[str] = []
    cursor = 0
    for match in URL.finditer(text):
        url = _url_end(match.group(0))
        if not url:
            continue
        out.append(_text_node(text[cursor : match.start()]))
        href = docx_write.esc(url).replace('"', "&quot;")
        out.append(f'<a href="{href}">{docx_write.esc(url)}</a>')
        cursor = match.start() + len(url)
    out.append(_text_node(text[cursor:]))
    return "".join(out)


def inline_html(text: str, *, bold: bool = False, italic: bool = False) -> str:
    out: list[str] = []
    for span in docx_write.inline_spans(text, bold=bold, italic=italic):
        rendered = _text_node(span.text) if span.monospace else _linked_text(span.text)
        if span.monospace:
            rendered = f"<code>{rendered}</code>"
        if span.italic:
            rendered = f"<em>{rendered}</em>"
        if span.bold:
            rendered = f"<strong>{rendered}</strong>"
        out.append(rendered)
    return "".join(out)


def _table(block: docx_write.Block) -> str:
    header, *body = block.rows
    head = "".join(f"<th>{inline_html(cell)}</th>" for cell in header)
    rows = "".join(
        "<tr>" + "".join(f"<td>{inline_html(cell)}</td>" for cell in row) + "</tr>"
        for row in body
    )
    return (
        f"<table><thead><tr>{head}</tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def render(markdown: str) -> str:
    """Return the HTML fragment loaded into Canvas's raw editor."""

    out: list[str] = []
    open_list: str | None = None

    def close_list() -> None:
        nonlocal open_list
        if open_list is not None:
            out.append(f"</{open_list}>")
            open_list = None

    for block in docx_write.blocks(markdown):
        list_tag = {"bullet": "ul", "numbered": "ol"}.get(block.kind)
        if list_tag is not None:
            if open_list != list_tag:
                close_list()
                open_list = list_tag
                out.append(f"<{list_tag}>")
            out.append(f"<li>{inline_html(block.text)}</li>")
            continue

        close_list()
        if block.kind == "heading":
            out.append(f"<p><strong>{inline_html(block.text)}</strong></p>")
        elif block.kind == "paragraph":
            out.append(f"<p>{inline_html(block.text)}</p>")
        elif block.kind == "block-quotation":
            out.append(f"<blockquote>{inline_html(block.text)}</blockquote>")
        elif block.kind == "table":
            out.append(_table(block))
        elif block.kind == "separator":
            out.append("<hr>")
        elif block.kind != "blank":  # pragma: no cover - Block owns the vocabulary
            raise ValueError(f"unsupported block kind: {block.kind}")
    close_list()
    return "".join(out) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 2 or any(argument.startswith("--") for argument in argv):
        print(USAGE)
        return 2
    source = Path(argv[0])
    destination = Path(argv[1])
    if not source.is_file():
        print(f"not a file: {source}")
        return 2
    try:
        rendered = render(source.read_text(encoding="utf-8"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="")
    except (OSError, UnicodeError, ValueError) as failure:
        print(f"could not write {destination}: {failure}", file=sys.stderr)
        return 2
    print(f"wrote {destination} ({destination.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
