"""The shared grammar for one ``icd10-cpt`` worksheet.

This module has no command line.  It owns the line shapes and the lower bound
used by graders that attribute an indented detail line to a code entry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from cpt_identity import CPT_CODE, EM_CODES


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

    A field, an E/M element line or the next entry closes the header. This retains
    readable historical worksheets whose official descriptor wrapped before the
    line-scoped marker; an element line's free text is never read as the marker.
    """

    start = entries[index].start()
    end = entries[index + 1].start() if index + 1 < len(entries) else len(text)
    closers = [match.start() for pattern in (FIELD, EM_LINE_START) if (match := pattern.search(text, start, end))]
    header = text[start : min(closers) if closers else end]
    return NOT_FOR_ENTRY.search(header) is None


@dataclass(frozen=True)
class WorksheetEntry:
    """One code entry, including entries whose required specificity line is absent."""

    start: int
    system: str
    code: str
    descriptor: str
    for_entry: bool


def read_entries(text: str) -> list[WorksheetEntry]:
    """Every code entry and its for-entry classification; specificity_scan re-exports this name."""
    found = list(ENTRY.finditer(text))
    return [
        WorksheetEntry(
            start=match.start(),
            system=match.group("system"),
            code=match.group("code"),
            descriptor=match.group("descriptor"),
            for_entry=entry_is_for_entry(text, found, index),
        )
        for index, match in enumerate(found)
    ]


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
# The E/M code label, as review_manifest.selected_codes reads it when it selects the final code.
EM_CODE_LABEL = re.compile(r"(?mi)^[ \t]*(?:\*\*)?E/M(?:\*\*)?[ \t]*:[ \t]*(?P<code>\d{5})\b")


def entry_region(text: str) -> str:
    """The private worksheet before its differential and icd10-cpt step 4 blocks: the for-entry codes."""
    boundaries = [match.start() for pattern in (DIFFERENTIAL_HEADING, STEP_FOUR_START)
                  if (match := pattern.search(text)) is not None]
    return text[:min(boundaries)] if boundaries else text


def selected_em_lines(lines: list[str], em_codes: frozenset[str] = EM_CODES) -> frozenset[int]:
    """The indexes of the selected E/M lines, read in one pass over the worksheet.

    A selected E/M line sits at the margin, the placement em-elements.md defines, and is the
    line ``review_manifest.selected_codes`` selects the E/M code from: an ``E/M:`` label line, or
    an E/M-family ``CPT`` entry of the for-entry region that ``read_entries`` marks for entry. An
    indented anchor, an entry marked ``NOT FOR ENTRY`` and a ``CPT`` entry outside that region are
    never the line an element block, a block skip or the check-off's E/M section is anchored to.
    """
    selected = {index for index, line in enumerate(lines) if line[:1].strip() and EM_CODE_LABEL.match(line)}
    region = entry_region("\n".join(lines))
    for match, entry in zip(ENTRY.finditer(region), read_entries(region)):
        if (entry.for_entry and entry.system.upper() == "CPT" and entry.code.upper() in em_codes
                and match.group(0)[:1].strip()):
            selected.add(region.count("\n", 0, match.start()))
    return frozenset(selected)


def physical_lines(text: str) -> list[str]:
    """The lines of ``text`` split on LF alone, each without a trailing CR.

    ``str.splitlines`` also splits on U+2028, U+2029 and U+0085, which the handwritten reader lets
    through, so a line counted by LF would drift against it and an element line would break apart.
    """
    return [line.removesuffix("\r") for line in text.split("\n")]


# The line anchor_scan ends its icd10-cpt step 4 block at; refusal_scan ends its own at ANY_HEADING.
OTHER_HEADING = re.compile(r"^[ \t]*(?:-{3,}|#{1,6}[ \t])")


def opens_element_block(lines: list[str], index: int, selected: frozenset[int]) -> bool:
    """Whether the margin line at ``index`` is a selected E/M line whose indented body holds an EM- line.

    em-elements.md places the element block indented directly under an E/M line, so an entry
    written inside an icd10-cpt step 4 block with no element line beneath it never qualifies, and
    neither does a margin code that is not a selected E/M line.
    """
    return element_body_end(lines, index, selected) is not None


def element_body_end(lines: list[str], index: int, selected: frozenset[int]) -> int | None:
    """The index after the indented body of a selected E/M line (``selected_em_lines``) holding an EM- line.

    None when the line is not such an anchor. The body is the contiguous indented lines below it.
    """
    if index not in selected:
        return None
    follower, holds_element = index + 1, False
    while follower < len(lines) and lines[follower].strip() and lines[follower][0] in " \t":
        holds_element = holds_element or bool(EM_CANDIDATE.match(lines[follower]))
        follower += 1
    return follower if holds_element else None


def step_four_block(lines: list[str], heading: re.Pattern[str], end: re.Pattern[str], *,
                    every: bool = False) -> tuple[list[str], bool]:
    """The lines under an icd10-cpt step 4 heading, and whether the heading was found.

    The caller supplies the lines, split as it splits them, and the terminator it grades by:
    refusal_scan reads to ``ANY_HEADING`` from the first heading, anchor_scan to ``OTHER_HEADING``
    under ``every`` heading. The one shared addition is the E/M section: a selected E/M line that
    opens its element block is skipped with its indented body and the block reads on, so nothing
    after it is dropped. A worksheet without an element block never has one.
    """
    collected: list[str] = []
    found = inside = False
    selected = selected_em_lines(lines)
    index = 0
    while index < len(lines):
        line = lines[index]
        if heading.match(line) and (every or not found):
            found = inside = True
        elif inside and (skip := element_body_end(lines, index, selected)) is not None:
            index = skip
            continue
        elif inside and end.match(line):
            inside = False
            if not every:
                break
        elif inside:
            collected.append(line)
        index += 1
    return collected, found


# How the check-off quotes each block: with the terminator, iteration and line splitting of the
# grader that grades it. The undocumented block has no grader and takes refusal_scan's rule.
BLOCK_READERS = {
    "filled": (OTHER_HEADING, True),
    "refusal": (ANY_HEADING, False),
    "undocumented": (ANY_HEADING, False),
}


def block_text(text: str, heading: re.Pattern[str], kind: str) -> str | None:
    """One icd10-cpt step 4 block as its grader reads it (``BLOCK_READERS``); None when the heading is absent."""
    end, every = BLOCK_READERS[kind]
    collected, found = step_four_block(text.splitlines(), heading, end, every=every)
    return "\n".join(collected).strip("\n") if found else None

# Every line that tries to be an element line: any upper-case EM- name, and the eight element
# names in any case, after an optional bullet or bold. A near miss is a candidate the strict
# reader refuses, so it is counted unread and fingerprinted, never silently skipped.
ELEMENT_NAMES = r"PROBLEM|DATA|RISK|RULE|ANSWER|ECG|MDM|LEVEL"
EM_CANDIDATE = re.compile(rf"^[ \t]*(?:[-+*][ \t]+)?(?:\*\*)?(?:EM-[A-Z]+|(?i:EM-(?:{ELEMENT_NAMES})))\b")
EM_LINE_START = re.compile("(?m)" + EM_CANDIDATE.pattern)
_EM_LINE = re.compile(r"^[ \t]*EM-(?P<kind>[A-Z]+)[ \t]*:[ \t]*(?P<value>.*?)[ \t]*$")
_EM_ITEM = re.compile(
    r"^(?P<entry>[a-z0-9][a-z0-9-]*|none)[ \t]*\|[ \t]*(?P<counted>counted|not counted)[ \t]*\|"
    r"[ \t]*(?P<text>\".*\"|none)[ \t]*\|[ \t]*(?P<reason>[^|]*\S)$"
)
_EM_MDM = re.compile(
    r"^problems (?P<problems>[a-z]+); data (?P<data>[a-z]+); risk (?P<risk>[a-z]+); mdm (?P<mdm>[a-z]+)$"
)
# A refused element line still names its element and, in its first field, usually its entry id.
_EM_LOOSE_ITEM = re.compile(r"EM-(?P<kind>PROBLEM|DATA|RISK)\b[ \t*]*:?(?P<entry>[^|]*)", re.IGNORECASE)
_EM_KIND = re.compile(r"EM-(?P<kind>[A-Za-z]+)\b")
_EM_ENTRY = re.compile(r"[a-z0-9][a-z0-9-]*|none")
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
    # (element, entry id) of each refused PROBLEM, DATA or RISK line; None where the id is unreadable.
    unread_items: tuple[tuple[str, str | None], ...] = ()

    def two_of_three(self) -> str | None:
        """The MDM level two of the three elements meet: the middle of the three."""
        if self.mdm is None:
            return None
        ranks = sorted(MDM_LEVELS.index(self.mdm[element]) for element in ("problems", "data", "risk"))
        return MDM_LEVELS[ranks[1]]


def em_block(text: str) -> EmBlock | None:
    """Read every EM- line in ``text``; None when the text holds no EM- candidate.

    A block missing a PROBLEM, DATA, RISK, ANSWER or ECG line, or not holding exactly one MDM
    and one LEVEL line, adds one to ``unread``: an incomplete block is not a clean one. A refused
    PROBLEM, DATA or RISK line keeps its element and, where readable, its entry id in
    ``unread_items``, so a comparison can leave its counterpart out.
    """
    lines = [line for line in physical_lines(text) if EM_CANDIDATE.match(line)]
    if not lines:
        return None
    items: list[EmItem] = []
    free: dict[str, list[str]] = {"RULE": [], "ANSWER": [], "ECG": []}
    mdms: list[dict[str, str]] = []
    levels: list[str] = []
    unread = 0
    unread_items: list[tuple[str, str | None]] = []
    refused: set[str] = set()
    for line in lines:
        loose = _EM_LOOSE_ITEM.search(line)
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
            named = _EM_KIND.search(line)
            refused.add(named.group("kind").upper() if named else "")
            if loose is not None:
                entry = loose.group("entry").strip(" \t*")
                unread_items.append((loose.group("kind").upper(), entry if _EM_ENTRY.fullmatch(entry) else None))
    # A required line that is present but refused is already counted once; only an absent one adds.
    present = {item.kind for item in items} | {kind for kind, values in free.items() if values} | refused
    present |= {"MDM"} if mdms else set()
    present |= {"LEVEL"} if levels else set()
    complete = (present >= {*ITEM_KINDS, "ANSWER", "ECG", "MDM", "LEVEL"}
                and len(mdms) <= 1 and len(levels) <= 1)
    return EmBlock(tuple(items), tuple(free["RULE"]), tuple(free["ANSWER"]), tuple(free["ECG"]),
                   mdms[0] if len(mdms) == 1 else None, levels[0] if len(levels) == 1 else None,
                   unread + (0 if complete else 1), tuple(unread_items))


@dataclass(frozen=True)
class WorksheetElements:
    """The element block of one private worksheet, and where its EM- lines sat."""

    block: EmBlock | None
    outside: int
    blocks: int


def worksheet_em_block(text: str, em_codes: frozenset[str]) -> WorksheetElements:
    """Read the element block under whichever E/M line carries it, counting each EM- line once.

    An E/M line is one of ``selected_em_lines``: a margin ``EM_CODE_LABEL`` line, or a margin
    for-entry ``ENTRY`` whose CPT code is in ``em_codes``; EM- lines under an indented anchor or a
    ``NOT FOR ENTRY`` E/M entry are outside. An anchor nested in another anchor body adds no
    block of its own. ``blocks`` counts the distinct blocks; when it exceeds one the first is
    returned and the caller reports the rest. EM- candidates under no anchor are ``outside``. A
    worksheet written before the block existed reads ``(None, 0, 0)``.
    """
    lines = physical_lines(text)
    candidates = {index for index, line in enumerate(lines) if EM_CANDIDATE.match(line)}
    selected = selected_em_lines(lines, em_codes)
    claimed: set[int] = set()
    groups: list[list[int]] = []
    for index, line in enumerate(lines):
        if index in claimed or index not in selected:
            continue
        body = []
        for follower in range(index + 1, len(lines)):
            if not lines[follower].strip() or lines[follower][0] not in " \t":
                break
            body.append(follower)
        claimed.update(body)
        if candidates.intersection(body):
            groups.append(body)
    within = candidates & claimed
    block = em_block("\n".join(lines[index] for index in groups[0])) if groups else None
    return WorksheetElements(block, len(candidates - within), len(groups))
