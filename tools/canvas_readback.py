"""Compare a fixed Canvas page-script readback with its built contribution."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from run_record_reader import HandwrittenKind


RECORD_KIND = HandwrittenKind("editor-readback", lambda text: (("", text),),
                              frozenset({"editor_id", "view", "html"}))


@dataclass(frozen=True)
class _EditorShape:
    units: tuple[tuple[str, str], ...]
    anchors: tuple[str, ...]
    read: int
    total: int


class _EditorHTML(HTMLParser):
    UNIT_TAGS = frozenset(("p", "li", "th", "td", "blockquote", "div", "pre", "h1", "h2", "h3", "h4", "h5", "h6"))

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._unit_stack: list[tuple[str, list[str]]] = []
        self.units: list[tuple[str, str]] = []
        self.anchors: list[str] = []
        self.loose_text: list[str] = []
        self.loose_units = 0

    def _flush_loose(self) -> None:
        text = " ".join("".join(self.loose_text).split())
        if text:
            self.units.append(("text", text))
            self.loose_units += 1
        self.loose_text.clear()

    def close(self) -> None:
        super().close()
        self._flush_loose()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        if tag == "a":
            href = next((value for name, value in attrs if name == "href"), None)
            if href is not None:
                self.anchors.append(href)
        if tag in self.UNIT_TAGS:
            if not self._unit_stack:
                self._flush_loose()
            self._unit_stack.append((tag, []))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if self._unit_stack and tag == self._unit_stack[-1][0]:
            unit_tag, unit_text = self._unit_stack.pop()
            self.units.append(
                (unit_tag, " ".join("".join(unit_text).split()))
            )

    def handle_data(self, data: str) -> None:
        if not self._unit_stack:
            self.loose_text.append(data)
        for _tag, unit_text in self._unit_stack:
            unit_text.append(data)


EDITOR_UNIT = re.compile(r"(?i)<(?:p|li|th|td|blockquote|div|pre|h[1-6])(?=[\s>/])")


def _editor_shape(markup: str) -> _EditorShape:
    parser = _EditorHTML()
    parser.feed(markup)
    parser.close()
    return _EditorShape(
        units=tuple(parser.units),
        anchors=tuple(parser.anchors),
        read=len(parser.units),
        total=len(EDITOR_UNIT.findall(markup)) + parser.loose_units,
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    record: dict[str, object] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("duplicate page-script field")
        record[key] = value
    return record


def compare(built_html: str | None, retained: str | None, *, surface: str) -> tuple[str, int, int]:
    """Return a refusal detail and the HTML-unit coverage from both inputs."""
    built = _editor_shape(built_html) if built_html is not None else None
    readback = None
    differences = []
    if built_html is None:
        differences.append("editor readback exists without the built HTML")
    if retained is None:
        differences.append("built HTML has no editor readback")
    else:
        try:
            record = json.loads(retained, object_pairs_hook=_unique_object)
        except (ValueError, TypeError):
            record = None
        if (not isinstance(record, dict)
                or set(record) != {"editor_id", "view", "html"}
                or not all(isinstance(value, str) for value in record.values())):
            differences.append("editor readback is not the fixed page-script JSON output")
        else:
            pattern = r"message-body-root" if surface == "initial" else r"message-body-\d+"
            if re.fullmatch(pattern, record["editor_id"]) is None:
                differences.append("editor readback does not identify the expected Composer")
            if record["view"] != "formatted":
                differences.append(f"Composer view is {record['view'] or 'missing'}, expected formatted")
            readback = _editor_shape(record["html"])
    if built is not None and readback is not None:
        if built.read != built.total:
            differences.append(f"built HTML units read {built.read} of {built.total}")
        if readback.read != readback.total:
            differences.append(f"editor readback units read {readback.read} of {readback.total}")
        if readback.units != built.units:
            differences.append("visible block text differs")
        if len(readback.anchors) != len(built.anchors):
            differences.append(f"anchor count is {len(readback.anchors)}, expected {len(built.anchors)}")
        elif readback.anchors != built.anchors:
            differences.append("anchor destinations differ")
    shapes = tuple(shape for shape in (built, readback) if shape is not None)
    return "; ".join(differences), sum(shape.read for shape in shapes), sum(shape.total for shape in shapes)
