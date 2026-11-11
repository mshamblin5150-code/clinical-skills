"""The shared grammar for one ``icd10-cpt`` worksheet.

This module has no command line.  It owns the line shapes and the lower bound
used by graders that attribute an indented detail line to a code entry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from cpt_identity import CPT_CODE


# icd10-cpt step 4 has one set of phrases. The optional confirmation tail is part of the
# filled-anchor heading, while the old NOT CODED phrase remains a different block.
_PHRASES = {
    "differential": r"DIFFERENTIAL,[ \t]+DOCUMENTS[ \t]+MDM,[ \t]+NOT[ \t]+FOR[ \t]+ENTRY",
    "undocumented": r"UNDOCUMENTED,[ \t]+WOULD[ \t]+SUPPORT[ \t]+A[ \t]+MORE[ \t]+SPECIFIC[ \t]+CODE",
    "filled": r"CODED,[ \t]+ANCHOR[ \t]+WAS[ \t]+FILLED(?:[ \t]+[—-][ \t]+CONFIRM[ \t]+BEFORE[ \t]+SUBMITTING|:[ \t]*CONFIRM[ \t]+BEFORE[ \t]+SUBMITTING)?",
    "refusal": r"NOT[ \t]+CODED,[ \t]+NOTHING[ \t]+ESTABLISHED[ \t]+IT",
}


def _heading(phrase: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?im)^[ \t]*(?:---[ \t]*{phrase}[ \t]*---|"
        rf"#{{1,6}}[ \t]+(?:---[ \t]*{phrase}[ \t]*---|{phrase}))[ \t]*$"
    )


DIFFERENTIAL_HEADING = _heading(_PHRASES["differential"])
UNDOCUMENTED_HEADING = _heading(_PHRASES["undocumented"])
BLOCK_HEADING = _heading(_PHRASES["filled"])
REFUSAL_HEADING = _heading(_PHRASES["refusal"])
STEP_FOUR_START = _heading(
    rf"(?:{_PHRASES['undocumented']}|{_PHRASES['filled']}|{_PHRASES['refusal']})"
)
_BLOCKS = (DIFFERENTIAL_HEADING, UNDOCUMENTED_HEADING, BLOCK_HEADING, REFUSAL_HEADING)
_HEADING_SHAPE = re.compile(r"^[ \t]*(?:(?:#{1,6}[ \t]+)?---[^\r\n]+---|#{1,6}[ \t]+[^\r\n]+)[ \t]*$")
ANY_HEADING = re.compile(r"^[ \t]*(?:#{1,6}[ \t]+|---[ \t]+\S.*---[ \t]*$)")
_STEP_FOUR_WORD = re.compile(
    r"DIFFERENTIAL|NOT[ \t]+FOR[ \t]+ENTRY|NOT[ \t]+CODED|"
    r"ANCHOR[ \t]+WAS[ \t]+FILLED|UNDOCUMENTED",
    re.IGNORECASE,
)
_GENERIC_DIFFERENTIAL = re.compile(r"^[ \t]*#{1,6}[ \t]+DIFFERENTIAL[ \t]*$", re.IGNORECASE)


@dataclass(frozen=True)
class HeadingCounts:
    candidates: int
    unread: int
    off_template: int
    generic_differential: int


def heading_counts(text: str) -> HeadingCounts:
    """Return the keyword-heading population and its three dispositions.

    The candidate floor is limited to heading-shaped keyword lines. A generic
    ``### Differential`` is a known section label, counted separately so the
    preserved worksheets' section scaffolding never masquerades as an icd10-cpt step-4 block.
    Other titles without these words remain outside the population.
    """
    candidates = unread = off_template = generic_differential = 0
    for line in text.splitlines():
        if not _HEADING_SHAPE.fullmatch(line):
            continue
        if any(pattern.fullmatch(line) for pattern in _BLOCKS):
            candidates += 1
            off_template += int(not line.lstrip().startswith("---"))
        elif _STEP_FOUR_WORD.search(line):
            candidates += 1
            if _GENERIC_DIFFERENTIAL.fullmatch(line):
                generic_differential += 1
            else:
                unread += 1
    return HeadingCounts(candidates, unread, off_template, generic_differential)


CODE = rf"(?:[A-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{{1,4}})?|{CPT_CODE}|[A-Z][0-9]{{4}})"

ENTRY = re.compile(
    rf"(?mi)^[ \t]*(?P<system>ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+"
    rf"(?P<code>{CODE})[ \t]+(?P<descriptor>.+?)[ \t]*$"
)

# Candidate forms deliberately admit common Markdown decoration around the same
# entry and field tokens.  Graders subtract their strict reads from these wider
# populations; they do not treat this grammar as a second accepted syntax.
ENTRY_CANDIDATE = re.compile(
    rf"(?mi)^[ \t]*(?:[-+*][ \t]+)?(?:\*\*)?"
    rf"(?P<system>ICD-?10(?:-CM)?|CPT|HCPCS)(?:\*\*)?[ \t]+"
    rf"(?P<code>{CODE})\b[^\r\n]*$"
)

FIELD = re.compile(
    r"(?mi)^[ \t]*(?P<field>ANCHOR|SOURCE|SPECIFICITY|CONFIDENCE|NOTE)[ \t]*:"
)


def field_candidates(text: str, field: str) -> list[re.Match[str]]:
    """Relaxed-prefix physical lines beginning with one named detail field."""
    return list(
        re.finditer(
            rf"(?mi)^[ \t]*(?:[-+*][ \t]+)?(?:\*\*)?"
            rf"{re.escape(field)}(?:\*\*)?[ \t]*:",
            text,
        )
    )

NOT_FOR_ENTRY = re.compile(r"(?mi)[ \t]NOT FOR ENTRY[ \t]*$")


def entry_is_for_entry(
    text: str, entries: list[re.Match[str]], index: int
) -> bool:
    """Whether one entry header lacks a line ending in ``NOT FOR ENTRY``.

    A field or the next entry closes the header. This retains readable historical
    worksheets whose official descriptor wrapped before the line-scoped marker.
    """

    start = entries[index].start()
    end = entries[index + 1].start() if index + 1 < len(entries) else len(text)
    field = FIELD.search(text, start, end)
    header = text[start : field.start() if field else end]
    return NOT_FOR_ENTRY.search(header) is None


def differential_prose(text: str) -> tuple[str, ...]:
    """Retain clinical prose in the differential region, including legacy lists.

    Entry headers are compared separately. ANCHOR, SOURCE, SPECIFICITY and
    CONFIDENCE fields are provenance; NOTE fields and surrounding prose carry
    clinical verdicts and remain protected without guessing their vocabulary.
    """
    start = DIFFERENTIAL_HEADING.search(text)
    if start is None:
        return ()
    stop = STEP_FOUR_START.search(text, start.end())
    region = text[start.end():stop.start() if stop else len(text)]
    result: list[str] = []
    metadata = False
    for line in region.splitlines():
        field = FIELD.match(line)
        if field:
            metadata = field["field"].upper() != "NOTE"
        elif not line.strip() or not line.startswith((" ", "\t")):
            metadata = False
        if metadata or ENTRY.fullmatch(line) or line.strip().startswith(("```", "~~~")):
            continue
        if line.strip():
            result.append(line.strip())
    return tuple(result)


def detail_belongs_to_entry(text: str, entry: re.Match[str], detail: re.Match[str]) -> bool:
    """Whether ``detail`` is in ``entry``'s contiguous indented body.

    The entry line itself ends at ``entry.end()``.  Every complete physical line
    after that and before the detail must contain text and begin with indentation.
    """

    if detail.start() <= entry.end():
        return False
    between = text[entry.end() : detail.start()]
    lines = between.splitlines()
    intervening = lines[1:] if lines else ()
    return all(line.strip() and line[0] in " \t" for line in intervening)


def paired_entry(
    text: str, entries: list[re.Match[str]], detail: re.Match[str]
) -> re.Match[str] | None:
    """Return the nearest entry above a detail when the pairing bound holds."""

    owner = next((entry for entry in reversed(entries) if entry.start() < detail.start()), None)
    if owner is None or not detail_belongs_to_entry(text, owner, detail):
        return None
    return owner


# The E/M element block (skills/_shared/reference/em-elements.md). icd10-cpt step 5 indents it
# under the E/M line of the private worksheet; the em-audit re-derivation record carries the same
# lines. Every EM- line is a candidate, so a line the strict reader refuses is counted as unread.
EM_KINDS = ("PROBLEM", "DATA", "RISK", "RULE", "ANSWER", "ECG", "MDM", "LEVEL")
ITEM_KINDS = ("PROBLEM", "DATA", "RISK")
MDM_LEVELS = ("straightforward", "low", "moderate", "high")
EM_LABEL = re.compile(r"^[ \t]*(?:E/M[ \t]*:|CPT[ \t]+992(?:0[2-5]|1[1-5]|8[1-5])\b)")
EM_CANDIDATE = re.compile(r"^[ \t]*(?:[-+*][ \t]+)?(?:\*\*)?EM-[A-Z]+\b")
_EM_LINE = re.compile(r"^[ \t]*EM-(?P<kind>[A-Z]+)[ \t]*:[ \t]*(?P<value>.*?)[ \t]*$")
_EM_ITEM = re.compile(
    r"^(?P<entry>[a-z0-9][a-z0-9-]*|none)[ \t]*\|[ \t]*(?P<counted>counted|not counted)[ \t]*\|"
    r"[ \t]*(?P<text>\".*\"|none)[ \t]*\|[ \t]*(?P<reason>[^|]*\S)$"
)
_EM_MDM = re.compile(
    r"^problems (?P<problems>[a-z]+); data (?P<data>[a-z]+); risk (?P<risk>[a-z]+); mdm (?P<mdm>[a-z]+)$"
)
_EM_CODE = re.compile(r"^\d{5}$")
_EM_ANSWER = re.compile(r"^(?:note-[1-9][0-9]*\.q[1-9][0-9]*|none)$")


@dataclass(frozen=True)
class EmItem:
    kind: str
    entry: str
    counted: bool
    text: str
    reason: str


@dataclass(frozen=True)
class EmBlock:
    """The strictly read element lines; ``unread`` counts every refused candidate."""

    items: tuple[EmItem, ...]
    rules: tuple[str, ...]
    answers: tuple[str, ...]
    ecg: tuple[str, ...]
    mdm: dict[str, str] | None
    level: str | None
    unread: int

    def two_of_three(self) -> str | None:
        """The MDM level two of the three elements meet: the middle of the three."""
        if self.mdm is None:
            return None
        ranks = sorted(MDM_LEVELS.index(self.mdm[element]) for element in ("problems", "data", "risk"))
        return MDM_LEVELS[ranks[1]]


def em_block(text: str) -> EmBlock | None:
    """Read every EM- line in ``text``; None when the text holds no EM- candidate.

    A block missing a PROBLEM, DATA or RISK line, or not holding exactly one MDM and one
    LEVEL line, adds one to ``unread``: an incomplete block is not a clean one.
    """
    lines = [line for line in text.splitlines() if EM_CANDIDATE.match(line)]
    if not lines:
        return None
    items: list[EmItem] = []
    free: dict[str, list[str]] = {"RULE": [], "ANSWER": [], "ECG": []}
    mdms: list[dict[str, str]] = []
    levels: list[str] = []
    unread = 0
    for line in lines:
        match = _EM_LINE.match(line)
        kind = match.group("kind") if match else ""
        value = match.group("value") if match else ""
        if kind in ITEM_KINDS and (item := _EM_ITEM.match(value)):
            items.append(EmItem(kind, item.group("entry"), item.group("counted") == "counted",
                                item.group("text"), item.group("reason")))
        elif kind == "MDM" and (mdm := _EM_MDM.match(value)) and set(mdm.groupdict().values()) <= set(MDM_LEVELS):
            mdms.append(mdm.groupdict())
        elif kind == "LEVEL" and _EM_CODE.match(value):
            levels.append(value)
        elif kind == "ANSWER" and _EM_ANSWER.match(value):
            free[kind].append(value)
        elif kind in ("RULE", "ECG") and value:
            free[kind].append(value)
        else:
            unread += 1
    complete = {item.kind for item in items} >= set(ITEM_KINDS) and len(mdms) == 1 and len(levels) == 1
    return EmBlock(tuple(items), tuple(free["RULE"]), tuple(free["ANSWER"]), tuple(free["ECG"]),
                   mdms[0] if len(mdms) == 1 else None, levels[0] if len(levels) == 1 else None,
                   unread + (0 if complete else 1))


def worksheet_em_block(text: str) -> tuple[EmBlock | None, int]:
    """The element block indented under the first E/M line, and EM- candidates outside it.

    A worksheet written before the block existed returns ``(None, 0)`` and stays valid.
    """
    lines = text.splitlines()
    inside: list[str] = []
    for index, line in enumerate(lines):
        if EM_LABEL.match(line):
            for follower in lines[index + 1:]:
                if not follower.strip() or follower[0] not in " \t":
                    break
                inside.append(follower)
            break
    total = sum(1 for line in lines if EM_CANDIDATE.match(line))
    within = sum(1 for line in inside if EM_CANDIDATE.match(line))
    return em_block("\n".join(inside)), total - within
