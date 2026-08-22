"""Extract the text of a .docx, with the standard library and nothing else.

    python tools/docx_read.py <file.docx> [--normalize] [--outline] [--numbering]

The faculty material for a practicum case study arrives as a Word document, and so does
the evidence dump the clinician pastes UpToDate topics into. Both have to be read before
anything can be written, and neither is a PDF -- so ``guidelines_extract.py`` and its
PyMuPDF dependency are the wrong tool. A ``.docx`` is a zip of XML parts, which
``zipfile`` and ``xml.etree`` open for nothing. Pairs with ``tools/docx_write.py``.

**``--normalize`` exists because the evidence dump is booby-trapped.** UpToDate salts
its rendered pages with homoglyphs -- a Cyrillic ``с`` inside ``cervicitis``, a Greek
``ο`` inside ``infection`` -- so a paste of a topic is not searchable by the words it
appears to contain. ``grep`` for ``cervicitis`` over a raw paste of the cervicitis topic
misses most of its occurrences, and reports **a clean zero rather than an error**, which
is this repo's recurring shape: a search that could not have worked, answering like a
settled negative. The map folds the lookalikes back to ASCII. It is deliberately narrow
-- letters only, and only the ones observed in the corpus -- because folding every
confusable would corrupt genuine non-Latin text.

**Exit status distinguishes not having read from having found nothing** -- 0 for text,
**2 for every way of not having read**: no argument, no file, a file that is not a zip,
a zip with no ``word/document.xml``. A document whose text landed in a part this does not
know about would otherwise print nothing and read as an empty document.

**``--numbering`` reconstructs the list marker Word draws rather than pretending it is
paragraph text.** The marker lives in ``word/numbering.xml`` and the paragraph carries
only ``numId`` and ``ilvl``. The reader walks both parts, applies each level's start and
``startOverride``, and prefixes the resulting marker to the text. A new ``numId`` sharing
an abstract definition continues that sequence unless its override restarts it, as Word
16.0 was calibrated to do on #422. A document with no numbering part remains a successful
ordinary read.

**The remaining part limit is live rather than theoretical: a header is a part, and this
does not read one.** Since #217 ``docx_write.py`` emits ``word/header1.xml`` for APA 7's
page number, and nothing this reader is pointed at would show it. That costs nothing here
because the part carries a ``PAGE`` field and no prose -- a test pins that the round trip
still returns every word the writer was given -- but a document from elsewhere whose
running head holds real text loses it silently, which is the shape ``--normalize`` exists
for one level up.

**Its output is whatever the document held**, and this reads any document it is pointed
at. Where that is a patient record or faculty material about one, the output is PHI on
``harvest_review.py``'s terms: read it, do not paste it. There is no redaction here
because there is nothing general to redact -- the caller knows what it opened.

Covered by ``tools/test_docx.py``, which builds documents with ``docx_write`` in a temp
directory and reads them back.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from console_codec import use_utf8

NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Observed in the clinician's UpToDate paste. Cyrillic and Greek letters standing in
# for the Latin ones they are drawn identically to. Narrow on purpose -- see the
# module docstring.
HOMOGLYPHS = {
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M",
    "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T",
    "Х": "X", "а": "a", "в": "v", "е": "e", "к": "k",
    "м": "m", "о": "o", "р": "p", "с": "c", "у": "y",
    "х": "x", "і": "i", "ѕ": "s", "ј": "j", "һ": "h",
    "ԁ": "d", "ԛ": "q", "ո": "n", "օ": "o", "Α": "A",
    "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I",
    "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P",
    "Τ": "T", "Υ": "Y", "Χ": "X", "α": "a", "ε": "e",
    "ι": "i", "ν": "v", "ο": "o", "ρ": "p", "ς": "s",
    "σ": "o", "υ": "u", "ϲ": "c", "‐": "-", "‑": "-",
}


def normalize(text: str) -> str:
    """Fold the observed homoglyphs back to ASCII. Leaves everything else alone."""
    return "".join(HOMOGLYPHS.get(character, character) for character in text)


def _text_of(element) -> str:
    """The visible text of one paragraph, with tabs and soft breaks preserved."""
    parts = []
    for node in element.iter():
        tag = node.tag
        if tag == NS + "t":
            parts.append(node.text or "")
        elif tag == NS + "tab":
            parts.append("\t")
        elif tag in (NS + "br", NS + "cr"):
            parts.append("\n")
    return "".join(parts)


class _Numbering:
    """Reconstruct list markers from the document's numbering definitions."""

    def __init__(self, root) -> None:
        self.levels = {}
        self.instances = {}
        self.counters = {}
        self.abstract_counters = {}
        for abstract in root.findall(NS + "abstractNum"):
            abstract_id = abstract.get(NS + "abstractNumId")
            for level in abstract.findall(NS + "lvl"):
                ilvl = int(level.get(NS + "ilvl", "0"))
                start = level.find(NS + "start")
                num_fmt = level.find(NS + "numFmt")
                level_text = level.find(NS + "lvlText")
                self.levels[(abstract_id, ilvl)] = (
                    int(start.get(NS + "val", "1")) if start is not None else 1,
                    num_fmt.get(NS + "val", "decimal") if num_fmt is not None else "decimal",
                    level_text.get(NS + "val", "") if level_text is not None else "",
                )
        for instance in root.findall(NS + "num"):
            num_id = instance.get(NS + "numId")
            abstract = instance.find(NS + "abstractNumId")
            if abstract is None:
                continue
            overrides = {}
            for override in instance.findall(NS + "lvlOverride"):
                start = override.find(NS + "startOverride")
                if start is not None:
                    overrides[int(override.get(NS + "ilvl", "0"))] = int(
                        start.get(NS + "val", "1")
                    )
            self.instances[num_id] = (abstract.get(NS + "val"), overrides)

    def marker(self, paragraph) -> tuple[str, int]:
        properties = paragraph.find(NS + "pPr")
        num_properties = properties.find(NS + "numPr") if properties is not None else None
        if num_properties is None:
            return "", 0
        num_id_node = num_properties.find(NS + "numId")
        level_node = num_properties.find(NS + "ilvl")
        if num_id_node is None:
            return "", 0
        num_id = num_id_node.get(NS + "val")
        ilvl = int(level_node.get(NS + "val", "0")) if level_node is not None else 0
        if num_id not in self.instances:
            return "", ilvl
        abstract_id, overrides = self.instances[num_id]
        definition = self.levels.get((abstract_id, ilvl))
        if definition is None:
            return "", ilvl
        start, _, template = definition
        key = (num_id, ilvl)
        abstract_key = (abstract_id, ilvl)
        for deeper in [row for row in self.counters if row[0] == num_id and row[1] > ilvl]:
            del self.counters[deeper]
        for deeper in [
            row for row in self.abstract_counters
            if row[0] == abstract_id and row[1] > ilvl
        ]:
            del self.abstract_counters[deeper]
        if key in self.counters:
            value = self.counters[key] + 1
        elif ilvl in overrides:
            value = overrides[ilvl]
        else:
            value = self.abstract_counters.get(abstract_key, start - 1) + 1
        self.counters[key] = value
        self.abstract_counters[abstract_key] = value
        def replace(match) -> str:
            referenced_level = int(match.group(1)) - 1
            referenced_value = self.counters.get((num_id, referenced_level))
            if referenced_value is None:
                referenced_value = self.abstract_counters.get(
                    (abstract_id, referenced_level)
                )
            if referenced_value is None:
                return match.group(0)
            referenced = self.levels.get((abstract_id, referenced_level))
            if referenced is None or referenced[1] != "decimal":
                return match.group(0)
            return str(referenced_value)

        marker = re.sub(r"%([1-9])", replace, template)
        return marker, ilvl


def _walk(parent, out: list, numbering: _Numbering | None = None) -> None:
    """Emit paragraphs in document order, joining a table row onto one line."""
    for child in parent:
        if child.tag == NS + "p":
            text = _text_of(child)
            marker, ilvl = numbering.marker(child) if numbering is not None else ("", 0)
            if marker:
                text = "   " * ilvl + marker + " " + text
            out.append(text)
        elif child.tag == NS + "tbl":
            for row in child.findall(NS + "tr"):
                cells = []
                for cell in row.findall(NS + "tc"):
                    inner: list = []
                    _walk(cell, inner, numbering)
                    cells.append(" ".join(part.strip() for part in inner if part.strip()))
                out.append(" | ".join(cells))
        elif child.tag in (NS + "body", NS + "sdt", NS + "sdtContent", NS + "tc"):
            _walk(child, out, numbering)


def read_docx(path, numbering: bool = False) -> list:
    """The document's paragraphs, in order. Raises ``ValueError`` if it is not one."""
    path = Path(path)
    try:
        archive = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as problem:
        raise ValueError("not a readable zip: {p} ({e})".format(p=path, e=problem))
    with archive:
        if "word/document.xml" not in archive.namelist():
            raise ValueError("no word/document.xml in {p}".format(p=path))
        root = ElementTree.fromstring(archive.read("word/document.xml"))
        numbering_part = None
        if numbering and "word/numbering.xml" in archive.namelist():
            numbering_part = _Numbering(
                ElementTree.fromstring(archive.read("word/numbering.xml"))
            )
    out: list = []
    _walk(root, out, numbering_part)
    return [line.replace("﻿", "") for line in out]


HEADING = re.compile(r"^(?:[A-Z][A-Z &/'-]{3,}|[A-Z][\w ,'/-]{2,60}:)$")


def main(argv: list) -> int:
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if not args:
        print("usage: docx_read.py <file.docx> [--normalize] [--outline] [--numbering]")
        return 2
    try:
        lines = read_docx(args[0], numbering="--numbering" in flags)
    except ValueError as problem:
        print(problem)
        return 2
    if "--normalize" in flags:
        lines = [normalize(line) for line in lines]
    if "--outline" in flags:
        lines = [line for line in lines if HEADING.match(line.strip())]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
