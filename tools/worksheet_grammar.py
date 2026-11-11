"""The shared grammar for one ``icd10-cpt`` worksheet.

This module has no command line.  It owns the line shapes and the lower bound
used by graders that attribute an indented detail line to a code entry.
"""

from __future__ import annotations

from bisect import bisect_right
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

    A field, an E/M element line, an ``E/M:`` label line or the next entry closes the header, so
    a label's own NOT FOR ENTRY never rejects the entry above it. This retains
    readable historical worksheets whose official descriptor wrapped before the
    line-scoped marker; an element line's free text is never read as the marker.
    EM- lines exist only in worksheets written with the element block, which put NOT
    FOR ENTRY on the code's own line, so the element-line closer moves no historical one.
    """

    start = entries[index].start()
    end = entries[index + 1].start() if index + 1 < len(entries) else len(text)
    closers = [match.start() for pattern in (FIELD, EM_LINE_START, EM_LABEL_START)
               if (match := pattern.search(text, start, end))]
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
    after that and before the detail must contain text, begin with indentation, and not end a
    body (``ends_body``): the one body rule ``body_end`` reads too. An element block in the body
    ends nothing: em-elements.md puts an entry's fields before its block, and a field written
    after the block is still the entry's, as the E/M audit check-off reads it.
    """

    if detail.start() <= entry.end():
        return False
    between = text[entry.end() : detail.start()]
    lines = between.splitlines()
    intervening = lines[1:] if lines else ()
    return all(indented_line(line) and not ends_body(line) for line in intervening)


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
# The E/M label, indented or not and bold or not; EM_CODE_LABEL is the label followed by its code,
# as selected_em reads it when it selects the final code.
EM_LABEL = r"^[ \t]*(?:\*\*)?E/M(?:\*\*)?[ \t]*:"
EM_CODE_LABEL = re.compile(rf"(?mi){EM_LABEL}[ \t]*(?P<code>\d{{5}})\b")
# Where an E/M label line opens; it closes the header of the entry above it (``entry_is_for_entry``).
EM_LABEL_START = re.compile(rf"(?mi){EM_LABEL}")


def entry_region(text: str) -> str:
    """The private worksheet before its differential and icd10-cpt step 4 blocks: the for-entry codes."""
    boundaries = [match.start() for pattern in (DIFFERENTIAL_HEADING, STEP_FOUR_START)
                  if (match := pattern.search(text)) is not None]
    return text[:min(boundaries)] if boundaries else text


def em_identity(system: str, code: str) -> bool:
    """Whether a code entry names an E/M identity: a ``CPT`` code of the office or ED E/M families."""
    return system.upper() == "CPT" and code.upper() in EM_CODES


# The visible worksheet's colon labels (``CPT: 99213``), read as entries in the visible mode.
VISIBLE_CODE_LABEL = re.compile(r"(?mi)^(ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]*:[ \t]*")


def entry_reading(text: str, *, private: bool) -> str:
    """The text a worksheet's entries are read in, by mode: the private worksheet as written, the
    visible worksheet with its colon labels read as entries. No line break moves, so every line
    keeps its number."""
    return text if private else VISIBLE_CODE_LABEL.sub(r"\1 ", text)


def selected_em(text: str, region: str, entries: list[WorksheetEntry],
                lines: list[str] | None = None, *, private: bool = True) -> tuple[tuple[int, str], ...]:
    """Every selected E/M line of ``text`` with its code: the one rule that selects the E/M identity.

    ``review_manifest.selected_codes`` takes the worksheet's E/M identity from these codes and the
    E/M audit check-off anchors its element block to these lines. A selected line is an
    ``EM_CODE_LABEL`` line anywhere in ``text`` whose code is an ``em_identity``, or a for-entry
    ``em_identity`` entry of ``region`` (``text`` itself, or its for-entry region), indented or not.
    ``entries`` are ``read_entries`` of ``region``, whose lines are ``text``'s, so each line is
    numbered over ``text`` split on LF. An entry marked ``NOT FOR ENTRY``, an entry outside
    ``region``, and a label inside the body (``body_end``) of an E/M entry marked ``NOT FOR ENTRY``
    are never selected: a rejected level is never the final one, and neither is a label whose own
    line is marked ``NOT FOR ENTRY``. A label inside the body of a rejected diagnosis or procedure
    is selected as anywhere else. Rejected entries are found in
    ``entry_reading`` of the worksheet's mode, so a visible ``CPT: 99285 ... NOT FOR ENTRY`` rejects
    a label beneath it as its private copy does. ``lines`` is ``physical_lines(text)`` for the
    private mode, passed by a caller that already split it; the visible mode splits its own
    reading and refuses ``lines`` rather than discard it.
    """
    if lines is not None and not private:
        raise ValueError("lines is the private worksheet's split; the visible mode splits its own reading")
    reading = entry_reading(text, private=private)
    lines = physical_lines(reading) if lines is None else lines
    # ``region`` is a prefix of ``reading``, which keeps every line break of ``text``.
    reading_starts, text_starts = line_starts(reading), line_starts(text)
    every = list(ENTRY.finditer(reading))
    rejected: set[int] = set()
    for index, match in enumerate(every):
        # Only a rejected level rejects a label inside it; a rejected diagnosis rejects no level.
        if not entry_is_for_entry(reading, every, index) and em_identity(match.group("system"), match.group("code")):
            start = line_of(reading_starts, match.start())
            rejected.update(range(start + 1, body_end(lines, start)))
    found = set()
    for match in EM_CODE_LABEL.finditer(text):
        line = line_of(text_starts, match.start())
        # A label whose own line is marked NOT FOR ENTRY is a rejected level too.
        own = text[match.start():text_starts[line + 1] if line + 1 < len(text_starts) else len(text)]
        if em_identity("CPT", match.group("code")) and line not in rejected and not NOT_FOR_ENTRY.search(own):
            found.add((line, match.group("code")))
    found |= {(line_of(reading_starts, entry.start), entry.code.upper()) for entry in entries
              if entry.for_entry and em_identity(entry.system, entry.code)}
    return tuple(sorted(found))


def line_starts(text: str) -> list[int]:
    """The offset where each line of ``text`` split on LF starts, for ``line_of``."""
    starts = [0]
    position = text.find("\n")
    while position >= 0:
        starts.append(position + 1)
        position = text.find("\n", position + 1)
    return starts


def line_of(starts: list[int], offset: int) -> int:
    """The LF line holding ``offset``: one bisect over ``line_starts`` instead of a count per match."""
    return bisect_right(starts, offset) - 1


def selected_em_lines(lines: list[str], read: tuple[str, list[WorksheetEntry]] | None = None) -> frozenset[int]:
    """The indexes of ``selected_em``'s lines among ``lines``, the worksheet split on LF.

    ``read`` is the ``entry_region`` of these lines joined by LF with its ``read_entries``, passed
    by a caller that already parsed them.
    """
    text = "\n".join(lines)
    if read is None:
        region = entry_region(text)
        read = region, read_entries(region)
    return frozenset(index for index, _ in selected_em(text, *read, lines))


@dataclass(frozen=True)
class Anchored:
    """A worksheet's lines with its selected E/M lines numbered over them, built together.

    ``anchored`` is its constructor, so ``worksheet_em_block`` can never be handed one splitting's
    lines with another splitting's anchors.
    """

    lines: tuple[str, ...]
    selected: frozenset[int]


def anchored(lines: list[str], read: tuple[str, list[WorksheetEntry]] | None = None, *,
             selected: tuple[tuple[int, str], ...] | None = None) -> Anchored:
    """``lines`` with ``selected_em_lines`` of them; ``read`` as ``selected_em_lines`` takes it.

    ``selected`` is ``selected_em`` of these same lines (its ``lines`` argument), from a caller that
    already selected them, so nothing is selected twice.
    """
    if selected is not None:
        return Anchored(tuple(lines), frozenset(index for index, _ in selected))
    return Anchored(tuple(lines), selected_em_lines(list(lines), read))


def physical_lines(text: str) -> list[str]:
    """The lines of ``text`` split on LF alone, each without a trailing CR.

    ``str.splitlines`` also splits on U+2028, U+2029 and U+0085, which the handwritten reader lets
    through, so a line counted by LF would drift against it and an element line would break apart.
    """
    return [line.removesuffix("\r") for line in text.split("\n")]


# The line anchor_scan ends its icd10-cpt step 4 block at; refusal_scan ends its own at ANY_HEADING.
OTHER_HEADING = re.compile(r"^[ \t]*(?:-{3,}|#{1,6}[ \t])")


def indented_line(line: str) -> bool:
    """Whether ``line`` continues an indented body: it holds text and opens with a space or tab."""
    return bool(line.strip()) and line[0] in " \t"


def block_heading_line(line: str) -> bool:
    """Whether ``line`` is an icd10-cpt step 4 block heading, at the margin or indented."""
    return any(pattern.match(line) for pattern in _BLOCKS)


def ends_body(line: str) -> bool:
    """Whether ``line`` ends a body however it is indented: a blank line, an entry line, or an
    icd10-cpt step 4 block heading. Any other indented line, a ``#`` line included, is body text.

    ``body_end`` and ``detail_belongs_to_entry`` both stop at these lines, so the check-off and the
    graders draw one body.
    """
    return not line.strip() or bool(ENTRY.match(line)) or block_heading_line(line)


def indented_pieces(line: str) -> bool:
    """Whether every line ``str.splitlines`` makes of this LF line, its ending included, is indented.

    ``detail_belongs_to_entry`` requires exactly this of each line between an entry and its detail,
    so a reader walking an entry's lines can own a field from the lines it already consumed.
    """
    return all(indented_line(piece) for piece in (line + "\n").splitlines())


def body_end(lines: list[str], index: int) -> int:
    """The index after the body of the entry or E/M line at ``index``: the one body rule.

    A body line is an indented line, or a field line while every body line before it is indented
    text (``indented_pieces``), so a field may sit at the margin directly after the line or after
    an indented run, as ``detail_belongs_to_entry`` pairs a detail. A line that ends any body
    (``ends_body``: a blank line, an entry line, an icd10-cpt step 4 block heading indented or not),
    or any other margin line ends it; an indented ``#`` line that is no step 4 heading is body text.
    The E/M audit check-off reads an entry's provenance and the element block's extent through this
    rule alike.
    """
    owned = True
    position = index + 1
    while position < len(lines):
        line = lines[position]
        if ends_body(line):
            break
        if FIELD.match(line):
            if not owned:
                break
        elif not indented_line(line):
            break
        owned = owned and indented_pieces(line)
        position += 1
    return position


def element_body_end(lines: list[str], index: int, selected: frozenset[int]) -> int | None:
    """The index after the body of a selected E/M line (``selected_em_lines``) holding an EM- line.

    None when the line is not such an anchor. The body is ``body_end``'s, the rule an entry's
    provenance is read by too.
    """
    if index not in selected:
        return None
    end = body_end(lines, index)
    return end if any(EM_CANDIDATE.match(lines[follower]) for follower in range(index + 1, end)) else None


def step_four_lines(lines: list[str], heading: re.Pattern[str], end: re.Pattern[str], *,
                    every: bool = False) -> tuple[list[int], bool]:
    """The indexes of the lines under an icd10-cpt step 4 heading, and whether it was found.

    The one block reader. The caller supplies the lines, split as it splits them, and its
    terminator: refusal_scan reads to ``ANY_HEADING`` from the first heading, anchor_scan to
    ``OTHER_HEADING`` under ``every`` heading. Every line is block text, the E/M section included;
    on the placement em-elements.md defines that grades nothing in either grader (measured in
    test_em_audit). The E/M audit check-off filters its own quotation from these indexes.
    """
    collected: list[int] = []
    found = inside = False
    for index, line in enumerate(lines):
        if heading.match(line) and (every or not found):
            found = inside = True
        elif inside and end.match(line):
            inside = False
            if not every:
                break
        elif inside:
            collected.append(index)
    return collected, found


def step_four_block(lines: list[str], heading: re.Pattern[str], end: re.Pattern[str], *,
                    every: bool = False) -> tuple[list[str], bool]:
    """``step_four_lines``'s lines themselves, as the graders read them."""
    indexes, found = step_four_lines(lines, heading, end, every=every)
    return [lines[index] for index in indexes], found


# Every line that tries to be an element line: any upper-case EM- name, and the eight element
# names in any case, after an optional bullet or bold. A near miss is a candidate the strict
# reader refuses, so it is counted unread and fingerprinted, never silently skipped.
ELEMENT_NAMES = r"PROBLEM|DATA|RISK|RULE|ANSWER|ECG|MDM|LEVEL"
EM_CANDIDATE = re.compile(rf"^[ \t]*(?:[-+*][ \t]+)?(?:\*\*)?(?:EM-[A-Z]+|(?i:EM-(?:{ELEMENT_NAMES})[a-z]*))\b")
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
# A refused candidate's name and first field, read in any case so it can be mapped to its element.
_EM_LOOSE = re.compile(r"EM-(?P<kind>[A-Z]+)\b[ \t*]*:?(?P<entry>[^|]*)", re.IGNORECASE)
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


def element_of(name: str) -> str | None:
    """The element a candidate's name stands for, in any case and with a suffix such as a plural."""
    upper = name.upper()
    return next((element for element in EM_KINDS if upper.startswith(element)), None)


def em_block(text: str) -> EmBlock | None:
    """Read every EM- line in ``text``; None when the text holds no EM- candidate.

    A block missing a PROBLEM, DATA, RISK, ANSWER or ECG line, or not holding exactly one MDM
    and one LEVEL line, adds one to ``unread``: an incomplete block is not a clean one. A refused
    PROBLEM, DATA or RISK line keeps its element and, where readable, its entry id in
    ``unread_items``, so a comparison can leave its counterpart out. A refused MDM or LEVEL line
    leaves the block's MDM or level unknown (None), even beside a readable copy.
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
        loose = _EM_LOOSE.search(line)
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
            element = element_of(loose.group("kind")) if loose else None
            refused.add(element or "")
            if element in ITEM_KINDS:
                entry = loose.group("entry").strip(" \t*")
                unread_items.append((element, entry if _EM_ENTRY.fullmatch(entry) else None))
            elif element is None:
                # A refused line no element can be named for may be any counted element.
                unread_items.extend((kind, None) for kind in ITEM_KINDS)
    # A required line that is present but refused is already counted once; only an absent one adds.
    present = {item.kind for item in items} | {kind for kind, values in free.items() if values} | refused
    present |= {"MDM"} if mdms else set()
    present |= {"LEVEL"} if levels else set()
    complete = (present >= {*ITEM_KINDS, "ANSWER", "ECG", "MDM", "LEVEL"}
                and len(mdms) <= 1 and len(levels) <= 1)
    # A refused copy of the MDM or LEVEL line leaves that line unknown: the readable copy is not
    # known to be the one the author meant, so nothing is graded against it.
    mdm = mdms[0] if len(mdms) == 1 and "MDM" not in refused else None
    level = levels[0] if len(levels) == 1 and "LEVEL" not in refused else None
    return EmBlock(tuple(items), tuple(free["RULE"]), tuple(free["ANSWER"]), tuple(free["ECG"]),
                   mdm, level, unread + (0 if complete else 1), tuple(unread_items))


@dataclass(frozen=True)
class WorksheetElements:
    """The element block of one private worksheet, and where its EM- lines sat."""

    block: EmBlock | None
    outside: int
    blocks: int


def worksheet_em_block(text: str, lines: Anchored | None = None) -> WorksheetElements:
    """Read the element block under whichever E/M line carries it, counting each EM- line once.

    An E/M line is one of ``selected_em_lines``, by ``selected_em``'s rule: an ``EM_CODE_LABEL``
    line or a for-entry ``em_identity`` entry, indented or not; EM- lines under a ``NOT FOR ENTRY``
    E/M entry are outside. A block is
    ``element_body_end``'s body under such a line; a selected line inside another one's body, such
    as an indented label under the selected entry, belongs to that block rather than opening a
    second. ``blocks`` counts the distinct blocks; when it exceeds one the first is returned and
    the caller reports the rest.
    EM- candidates under no anchor are ``outside``. A worksheet written before the block existed
    reads ``(None, 0, 0)``. ``lines`` is the CR-free ``text`` split on LF with its anchors, passed by
    a caller that already holds them; lines that do not join back to ``text`` are refused with
    ``ValueError``.
    """
    if lines is None:
        lines = anchored(physical_lines(text))
    elif "\n".join(lines.lines) != text:
        raise ValueError("the anchored lines are not this text split on LF")
    lines, selected = list(lines.lines), lines.selected
    candidates = {index for index, line in enumerate(lines) if EM_CANDIDATE.match(line)}
    groups: list[range] = []
    for index in sorted(selected):
        if groups and index in groups[-1]:
            continue
        end = element_body_end(lines, index, selected)
        if end is not None:
            groups.append(range(index + 1, end))
    within = candidates & {follower for group in groups for follower in group}
    block = em_block("\n".join(lines[index] for index in groups[0])) if groups else None
    return WorksheetElements(block, len(candidates - within), len(groups))
