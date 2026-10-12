#!/usr/bin/env python3
"""Print the sentence changes between two privately retained Markdown showings."""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from docx_write import REFERENCE_HEADING, blocks


DECLARED_LIMITS = (
    "The Markdown subset is docx_write.blocks; discarded formatting is invisible.",
    "Sentence boundaries use punctuation followed by whitespace, not a language parser; "
    "abbreviations can split and punctuation-free sentences can remain together.",
    "Reference entries stay whole as parsed blocks; hard-wrapped entries remain separate blocks.",
    "Reworded pairing is a positional heuristic: a reworded sentence may instead appear "
    "as one removal and one addition, which keeps the list complete.",
    "Sequence alignment chooses one match for repeated sentences; it cannot establish edit intent.",
    "This command does not prove the list was shown or read, and does not gate approval.",
)


def sentences(markdown: str) -> tuple[str, ...]:
    """Read visible blocks, retaining reference entries as single comparison units."""
    result: list[str] = []
    pending: list[str] = []
    in_references = False

    def flush() -> None:
        if pending:
            text = " ".join(" ".join(pending).split())
            result.extend(re.split(r'(?<=[.!?])\s+', text))
            pending.clear()

    for block in blocks(markdown):
        if block.kind == "paragraph" and not in_references:
            pending.append(block.text)
            continue
        flush()
        if block.kind in {"blank", "separator"}:
            continue
        if block.kind == "heading":
            in_references = bool(REFERENCE_HEADING.match(block.text))
        texts = (
            [cell for row in block.rows for cell in row]
            if block.kind == "table" else [block.text]
        )
        for text in texts:
            text = " ".join(text.split())
            if text:
                result.extend((text,) if in_references else re.split(r'(?<=[.!?])\s+', text))
    flush()
    return tuple(result)


def changes(before: tuple[str, ...], after: tuple[str, ...]) -> tuple[str, ...]:
    """Compare in order; exact sentences crossing alignment are removals and additions."""
    output: list[str] = []
    before_set, after_set = set(before), set(after)
    for tag, first, last, new_first, new_last in difflib.SequenceMatcher(
        None, before, after, autojunk=False
    ).get_opcodes():
        if tag == "equal":
            continue
        old, new = before[first:last], after[new_first:new_last]
        if tag == "replace":
            # Pair only sentences absent from the other version. An exact move
            # must retain its removed/added labels even inside a replacement hunk.
            old_indices = [index for index, text in enumerate(old) if text not in after_set]
            new_indices = [index for index, text in enumerate(new) if text not in before_set]
            pairs = dict(zip(old_indices, new_indices))
            paired_new = set(pairs.values())
            for index, text in enumerate(old):
                if index in pairs:
                    output.extend(("Reworded:", f"  Before: {text}", f"  After: {new[pairs[index]]}"))
                else:
                    output.append(f"Removed: {text}")
            for index, text in enumerate(new):
                if index not in paired_new:
                    output.append(f"Added: {text}")
        else:
            output.extend(f"Removed: {text}" for text in old)
            output.extend(f"Added: {text}" for text in new)
    return tuple(output) or ("No sentence changed.",)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shown_before", type=Path)
    parser.add_argument("shown_now", type=Path)
    args = parser.parse_args(argv)
    try:
        before = sentences(args.shown_before.read_text(encoding="utf-8"))
        after = sentences(args.shown_now.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        print(f"Change list not computed: {exc}", file=sys.stderr)
        return 2
    print("\n".join(changes(before, after)))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
