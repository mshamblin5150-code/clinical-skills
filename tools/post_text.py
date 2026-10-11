#!/usr/bin/env python3
"""Build the plain Canvas comment from the shared Markdown subset. #1502."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import docx_write
from console_codec import require_python_floor, use_utf8

USAGE = "usage: post_text.py <in.md> <out.txt>"
ESCAPE = re.compile(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])")


def protect_url(url: str, escaped: list[str]) -> str:
    escaped.append(ESCAPE.sub(lambda match: match.group(1), url))
    return chr(0xE000 + len(escaped) - 1)


def render(markdown: str) -> str:
    """Keep text and paragraph spacing; refuse shapes outside the plain-box grammar."""
    escaped: list[str] = []

    def protect(match: re.Match[str]) -> str:
        escaped.append(match.group(1))
        return chr(0xE000 + len(escaped) - 1)

    if any(0xE000 <= ord(char) <= 0xF8FF for char in markdown):
        raise ValueError("line 1: reserved escape character")
    # A reference URL is literal text, including Markdown-looking punctuation.
    protected = re.sub(r"https?://[^\s<>]+", lambda match: protect_url(match.group(0), escaped), markdown)
    protected = ESCAPE.sub(protect, protected)
    # Validate before blocks can classify unfamiliar syntax as ordinary prose.
    for number, line in enumerate(protected.splitlines(), 1):
        if docx_write.OWN_LINE_COMMENT.fullmatch(line):
            continue
        if re.search(r"!?\[[^\]]*\](?:\(|\[)|^\s*\[[^\]]+\]:|<[^>]*>|~~|__|(?<!\w)_[^_]+_|^\s*(?:>|\||```|~~~|\+ |\* |#{5,}| {4}\S|\t)", line):
            raise ValueError(f"line {number}: unsupported Markdown shape")
    output: list[str] = []
    for block in docx_write.blocks(protected):
        if block.kind == "blank":
            output.append("")
            continue
        if block.kind not in {"heading", "paragraph", "bullet", "numbered"} or block.level and block.kind in {"bullet", "numbered"}:
            raise ValueError(f"line {block.line}: unsupported {block.kind}")
        parts = []
        for span in docx_write.inline_spans(block.text):
            if not span.monospace and re.search(r"[*`\\]", span.text):
                raise ValueError(f"line {block.line}: unrecognized inline shape")
            text = span.text
            for index, char in enumerate(escaped):
                text = text.replace(chr(0xE000 + index), char)
            parts.append(text)
        prefix = "- " if block.kind == "bullet" else protected.splitlines()[block.line - 1].strip().split(".", 1)[0] + ". " if block.kind == "numbered" else ""
        output.append(prefix + "".join(parts))
    return "\n".join(output)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or any(value.startswith("--") for value in argv):
        print(USAGE)
        return 2
    source, destination = map(Path, argv)
    try:
        text = render(source.read_text(encoding="utf-8"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8", newline="")
    except (OSError, UnicodeError, ValueError) as failure:
        print(f"plain-text build refused: {failure}", file=sys.stderr)
        return 2
    print(f"wrote {destination} ({destination.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
