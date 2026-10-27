"""Read rendered Lexidrug article HTML without guessing plain-text headings.

The live pull retains the page title and topicArticle outer HTML after every
Expand All. Ordinary clipboard text loses the indication/body boundaries; this
reader therefore refuses it rather than claiming the doses were present.

Every ``collapsible-indication-title`` must be expanded. Each one is held to the
dosing-text requirement, except the title inside the brand-names accordion: a div
whose class carries ``brand-names-accordion`` or ``drugBrandNames``. Lexidrug
renders the brand list with the indication accordion markup, so that title stays
a section heading and still counts as folded, but its body is a brand list rather
than an indication. No other heading class is exempt.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser

VERSION_LINE = re.compile(r"(?m)^\s*Topic\s+(\d+)\s+Version\s+([\d.]+)\s*$")
BRAND_NAMES_CLASSES = frozenset({"brand-names-accordion", "drugBrandNames"})
DRUG_HEADER = re.compile(r"(?im)^\s*(?:UpToDate Lexidrug|[^\n]+:\s*(?:Pediatric\s+)?Drug information)\s*$")


@dataclass(frozen=True)
class DrugSection:
    heading: str
    body: str


@dataclass(frozen=True)
class DrugPage:
    title: str
    version: str
    read_on: str
    sections: tuple[DrugSection, ...]
    body: str


def drug_is_current(read_on: str, on: date | None = None) -> bool:
    """A calendar year inclusive, with leap-day anniversary on February 28."""
    read = date.fromisoformat(read_on)
    today = on or date.today()
    anniversary = read.replace(year=read.year + 1, day=min(read.day, 28) if read.month == 2 else read.day)
    return read <= today <= anniversary


class _RenderedDrug(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.headings: list[tuple[str, int, bool, int]] = []
        self.heading: list[str] | None = None
        self.heading_tag = ""
        self.indication = False
        self.heading_start = 0
        self.folded = 0
        self.div_depth = 0
        self.brand_depth: int | None = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if tag == "div":
            self.div_depth += 1
            if self.brand_depth is None and BRAND_NAMES_CLASSES.intersection(classes):
                self.brand_depth = self.div_depth
        accordion = "collapsible-indication-title" in classes
        if accordion and attributes.get("aria-expanded") != "true":
            self.folded += 1
        if tag in {"h1", "h2", "h3", "h4"} or attributes.get("role") == "heading" or accordion:
            self.heading_start = len(self.parts)
            self.heading, self.heading_tag = [], tag
            self.indication = accordion and self.brand_depth is None
            self.parts.append("\n")
        elif tag in {"p", "div", "br", "li", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "div":
            if self.brand_depth == self.div_depth:
                self.brand_depth = None
            self.div_depth = max(self.div_depth - 1, 0)
        if self.heading is not None and tag == self.heading_tag:
            title = " ".join("".join(self.heading).split())
            if title:
                self.headings.append((title, len(self.parts), self.indication, self.heading_start))
            self.heading = None
            self.parts.append("\n")
        elif tag in {"p", "div", "li", "tr"}:
            self.parts.append("\n")

    def handle_data(self, value):
        self.parts.append(value)
        if self.heading is not None:
            self.heading.append(value)


def rendered_drug_text(text: str) -> str:
    """Visible-format text for the unfiled-material candidate census."""
    reader = _RenderedDrug()
    reader.feed(text)
    return "".join(reader.parts)


def parse_drug(text: str, read_on: str) -> DrugPage:
    date.fromisoformat(read_on)
    reader = _RenderedDrug()
    reader.feed(text)
    if reader.folded:
        raise ValueError(f"drug page has {reader.folded} folded indication(s); expand every adult and pediatric group")
    titles = [title for title, _at, _indication, _start in reader.headings if re.fullmatch(r".+: (?:Pediatric )?Drug information", title, re.I)]
    if len(set(titles)) != 1:
        raise ValueError("drug source needs its rendered page title and article HTML")
    body = "".join(reader.parts)
    versions = re.findall(r"Topic\s+(\d+)\s+Version\s+([\d.]+)", body)
    if len(versions) != 1:
        raise ValueError("drug page needs exactly one closing Topic / Version line")
    sections = []
    for index, (heading, start, indication, _heading_start) in enumerate(reader.headings):
        end = reader.headings[index + 1][3] if index + 1 < len(reader.headings) else len(reader.parts)
        section_body = "".join(reader.parts[start:end]).strip()
        if indication and (not section_body or not re.search(r"\d|\b(?:mg|mcg|dose|dosing|administer|avoid|not recommended|refer|see)\b", section_body, re.I)):
            raise ValueError(f"drug indication has no dosing text: {heading}")
        sections.append(DrugSection(heading, section_body))
    if not any(heading.lower().startswith("dosing") for heading, _at, _indication, _start in reader.headings):
        raise ValueError("drug page has no dosing section headings")
    return DrugPage(titles[0], versions[0][1], read_on, tuple(sections), body)
