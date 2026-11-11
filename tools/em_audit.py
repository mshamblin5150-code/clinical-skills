"""Render the coding decisions of a run as a human-readable E/M audit check-off.

``python tools/em_audit.py RUN [--note N ...] [--submission KEY] [--write] [--docx [--output-dir DIR] [--force]]``
reads the validated coding manifest of the run, its passing freshness receipt, the private
worksheet of each encounter with its E/M element block, the pre-approval answers record, and
any re-derivation record under ``RUN/em-audit/rederivation/<note stem>.md``. ``--write`` writes
one Markdown check-off per selected note to ``RUN/em-audit/<note stem>.md``. ``--docx`` renders
the same text to Word through ``docx_write.write_docx`` with ``literal=True``, so copied note
text, reasons, questions and replies keep their asterisks and backticks, by default under the
owning checkout ``output/em-audit/<run name>-<path fingerprint>/``; nothing writes a Word copy unless asked, and
``--output-dir`` or ``--force`` without ``--docx`` is refused.

The check-off is derived from the records the coding run wrote, so the two cannot disagree: a
manifest or receipt that approval would refuse is refused here too. Output is counts only; the
written check-offs carry patient information.

Exit 0 when every selected note rendered with no finding; 1 for a finding: a note without an
element block or a placed re-derivation (ADR 0445) in a run approved on or after the E/M audit
start in ``reference/completion-check-starts.tsv`` (``--submission`` reads the approval; without it
the run is judged current), an element block that contradicts itself or the selected code or the
billed ECG code, an unknown CPT entry id, an answer id this note lacks, a re-derivation that
differs element by element, or a damaged handwritten record; 2 when the run could not be read, a
note number is unknown, a private worksheet changed after its fingerprint was recorded, the CPT MDM
sheet version the receipt bound does not parse, a Word option was given without ``--docx``, a
check-off or Word copy was refused (naming the note number that stopped it and the copies already
written; a refused check-off leaves the Word copies unattempted), or a candidate went unread
(``unread remainder``), such as no committed sheet version matching the receipt. A finding
outranks an unread remainder.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from contextlib import nullcontext
from pathlib import Path
import re
from typing import NamedTuple

import coding_freshness
import cpt_mdm_sheet
from cpt_identity import MDM_LEVEL_OF
import em_audit_scope
import preapproval_answers
import repo_root
import review_manifest
from console_codec import require_python_floor, use_utf8
from encounter_openers import private_target
from run_grader import format_unread_remainder
from run_record_reader import (DamagedRecord, OutboundTextError, RecordUpdate, UnreadableRecord,
                               collecting_errors, damaged_record_result, fault_report, read_handwritten_record,
                               read_tool_record, update_tool_record)
from worksheet_grammar import (BLOCK_HEADING, EM_CANDIDATE, EM_CODE_LABEL, EM_LABEL, ENTRY, FIELD,
                               REFUSAL_HEADING, UNDOCUMENTED_HEADING, ANY_HEADING, OTHER_HEADING, Anchored,
                               EmBlock, WorksheetEntry, anchored, body_end, element_body_end, em_block,
                               entry_region, indented_line, physical_lines, read_entries, selected_em_lines,
                               step_four_lines, worksheet_em_block)


DECLARED_LIMITS = (
    "A check-off names its note by encounter number, service date and note filename (ADR 0445 "
    "ruling 4), and the patient status by value, evidence kind and evidence fingerprint; it never "
    "renders the opener record, identity rows, the status pointer, evidence path or status reply, "
    "or note headers. Worksheet, note E/M paragraph, re-derivation and answers text is quoted as "
    "recorded, so a name written into that text is not removed.",
    "The check-off restates what the run recorded. It establishes neither that a code is correct "
    "nor that the documentation supports the level; those remain readings for the clinician and "
    "the coding graders.",
    "An element block is checked for its line shape, counted items with an entry id and quoted "
    "note text, entry ids known to the CPT MDM sheet the receipt names, an MDM line whose level is "
    "the middle of its three elements, and a LEVEL its MDM selects; the worksheet block is also "
    "checked for a LEVEL equal to the selected code, answer ids present in the pre-approval answers "
    "record, the billed ECG codes, and one block per worksheet. A re-derivation takes only the "
    "first set: its level or elements against the worksheet show as differences, never findings. "
    "It is not checked that the code follows from the setting and status, that a quotation is "
    "faithful to the note, or that every element weighed was written down.",
    "Entry ids are read by cpt_mdm_sheet.read_entries from the committed version of the sheet the "
    "receipt names whose fingerprint, by coding_freshness.sheet_sha256, equals the receipt's, found "
    "in that path's git history. No matching version, or no git, leaves them unchecked and counts "
    "once as unread; a matching version the parser refuses refuses the check-off.",
    "An answer recorded as unreadable is shown and counted as incomplete coverage; the record "
    "itself does not establish which question a reply answered. An answers record that exists but "
    "cannot be read leaves the block's answer ids unchecked and counts once as unread; an absent "
    "record is a finding for a block that names an answer.",
    "A re-derivation is compared with the lines of the worksheet block that were read, on the "
    "counted and not-counted (element, entry id) population, each MDM element and the level; an "
    "unread worksheet line is counted in the unread remainder and stays outside the comparison, "
    "with every re-derivation line of its element and entry id, or of its whole element where its "
    "entry id is unreadable. A refused line is mapped to its element by name in any case and with "
    "a suffix; one no element can be named for withholds the PROBLEM, DATA and RISK comparison. A "
    "required line that is missing rather than refused excludes nothing. "
    "Note text, reasons, rules, answers and ECG lines are rendered side by side but not compared, "
    "and nothing establishes that the re-derivation was written before its author read the "
    "worksheet.",
    "A worksheet without an element block renders the visible worksheet and the E/M paragraph of "
    "the note verbatim, with the governing rules for the setting, and a re-derivation of it is "
    "compared on the level alone. A missing block or re-derivation is not graded only for a run "
    "whose approval predates the em_audit start; the command reads that approval only through "
    "--submission, and missing evidence grants no exemption. A re-derivation file with no element "
    "candidate line is not a placed re-derivation; one whose candidates are all refused is unread.",
    "Codes for entry are read from the private worksheet region and with the readers the "
    "manifest validation uses; the icd10-cpt step 4 blocks are copied as quotations with blank "
    "lines dropped, not parsed, through worksheet_grammar.step_four_lines with the terminator, "
    "iteration and line splitting of the grader that grades each block (BLOCK_READERS); the "
    "undocumented block, which no grader reads, takes refusal_scan's. Every line the E/M section "
    "renders (a selected E/M line that opens its element block, its wrapped header, its fields and "
    "its EM- lines) is shown there once and left out of the quotation; a line that section leaves "
    "unplaced, and any other line, an E/M entry marked NOT FOR ENTRY included, stays the block's "
    "text as the grader reads it. The graders read the same plain lines, the E/M section included, "
    "which is measured to grade nothing on the placement em-elements.md defines; another placement "
    "is not measured.",
    "Element candidates are any upper-case EM- name and the eight element names in any case and "
    "with a letter suffix, after an optional bullet or bold; a candidate the strict reader refuses "
    "is unread, counted once, and fingerprinted. A misspelled element name in another case is not "
    "a candidate.",
    "A wrapped descriptor or field value is joined from the contiguous indented lines below its "
    "entry, the bound worksheet_grammar pairs a detail by; a field or indented line no entry or "
    "E/M line owns, such as one after a blank line, and any line after an element block, are counted "
    "unread. A code marked NOT FOR ENTRY in the region is rendered, marked, with its fields. A "
    "continuation that a "
    "reader would place under a different field than its author meant cannot be told apart.",
    "Every selected E/M line (an E/M: label, or a for-entry E/M-family CPT entry) of the for-entry "
    "region, and every later one that opens an element block, is rendered with its own provenance "
    "fields in the E/M section. EM- lines under an E/M entry marked NOT FOR ENTRY anchor no block "
    "and are counted unread as outside lines.",
    "The private worksheet is bound only through its whole-file fingerprint, which "
    "review_manifest.build records beside the manifest and never in it; the check-off compares it "
    "and approval validation does not, and a changed file refuses the check-off. A run with no "
    "recorded fingerprint is counted unread on each check-off, or not graded for a run whose "
    "approval predates the em_audit start; building again records it. At submission, a changed private "
    "worksheet, a stale manifest or receipt, or a bound sheet version the parser refuses is a "
    "finding, and a missing or unreadable record is incomplete. At submission, a run "
    "with no manifest is incomplete only on the note path, marked by its encounter opener record, "
    "and only where a worksheet carries a selected E/M line; a direct consultation with no opener "
    "record is not graded, so a note-path run whose opener record is lost reads the same way.",
    "The ECG line is mechanical only for 93000 and 93005 on the worksheet. A billed one needs an "
    "EM-ECG limb other than not applicable, and a single billed code a limb naming it rather than "
    "only the other code; with no ECG code billed, the limb's text is not graded.",
    "Validation re-reads the opener source, notes, worksheets, status evidence and receipt; a "
    "moved or edited source refuses the check-off even long after the shift.",
    "Each check-off is written through run_record_reader.update_tool_record: the exclusive "
    "run-record lock covers the strict read of the existing check-off and its atomic replacement, "
    "one file at a time with no transaction across notes. An existing check-off that cannot be "
    "read refuses its replacement, as every tool-written run record does. Word copies are outbound "
    "artifacts written by docx_write under its own overwrite refusal.",
)


OUTPUT_DIRECTORY = "em-audit"
REDERIVATION_DIRECTORY = "rederivation"
WORD_DIRECTORY = "em-audit"
REPOSITORY = coding_freshness.ROOT  # the checkout whose reference/ holds the CPT MDM sheet
SECTIONS = (
    "Encounter",
    "Codes for entry",
    "Codes resting on a filled anchor",
    "Codes refused, with what would establish them",
    "Documentation that would support a more specific code",
    "E/M level, element by element",
    "Pre-approval questions and replies",
    "Independent re-derivation",
    "Clinician attestation",
)
FILLED_MARK = re.compile(r"\[SOURCE: filled - (?:data|risk): [^\]\n]+\]")
# The note's E/M paragraph, opened by the label the manifest reads (worksheet_grammar.EM_LABEL).
EM_PARAGRAPH = re.compile(rf"(?msi){EM_LABEL}.*?(?=\n[ \t]*\n|\Z)")
SHARED_RULES = (
    "reference/cpt-em-mdm-2026.md entries, by id, for the service-date edition",
    "ADR 0308: problems addressed, level-changing questions, proposed drugs, threat to life",
    "ADR 0376: element reasons say what is documented; the drug question",
    "ADR 0442: directed over-the-counter agents",
    "ADR 0443: the ECG read by the clinician",
)
GOVERNING = {
    "office": SHARED_RULES[:1] + (
        "reference/office-mdm-check.md house rules, counting notes and documentation checks (ADR 0444)",
    ) + SHARED_RULES[1:],
    "emergency-department": SHARED_RULES,
}
ECG_RULES = {
    "93000": "ADR 0443: 93000 reports the clinician reading an ECG traced at this office, so the "
             "ECG counts toward nothing in the data element.",
    "93005": "ADR 0443: 93005 is billed while the written findings of the clinician are pending, "
             "so the ECG counts as one test ordered.",
}
NO_ECG_CODE = "No ECG code is on the worksheet."
ATTESTATION = (
    "I have reviewed this check-off against my note. The codes and level above reflect the "
    "services I documented for this encounter.",
    "",
    "Clinician signature: ______________________________    Date: ______________",
)


class Tally:
    """Counts only: every printed figure is an integer, never record text."""

    def __init__(self) -> None:
        self.systems = {"icd10": 0, "cpt": 0, "hcpcs": 0, "em": 0}
        self.unanchored = self.filled_blocks = self.refusal_blocks = self.undocumented_blocks = 0
        self.marks = self.blocks_present = self.blocks_absent = self.block_findings = 0
        self.answers_shown = 0
        self.agree = self.differ = self.differences = self.damaged = self.absent = 0
        self.rederivation_findings = 0
        self.unread = 0
        # A run approved before the em_audit start (completion-check-starts.tsv): a missing element
        # block or re-derivation is shown and counted here, never as a finding.
        self.predates = False
        # Coverage faults a capturing command counts itself, kept so the gate knows the render was partial.
        self.faults = 0
        self.blocks_predating = self.absent_predating = 0


def entry_walk(lines: list[str], index: int) -> tuple[list[str], dict[str, list[str]], list[int], int]:
    """The wrapped header tail, field values, unplaced line positions and body end of the entry at ``index``.

    The body is ``worksheet_grammar.body_end``'s, the one body rule the element block's extent is
    read by too: indented lines, and a field line while every body line before it is indented text,
    as ``detail_belongs_to_entry`` pairs a detail. A line continues the field above it, or the
    header before the first field. Element lines and an indented E/M label belong to the element
    block, and any line after them, a field line included, is unplaced.
    """
    tail: list[str] = []
    fields: dict[str, list[str]] = {}
    unplaced: list[int] = []
    state, end = "header", body_end(lines, index)
    for position in range(index + 1, end):
        line = lines[position]
        field = FIELD.match(line)
        if EM_CANDIDATE.match(line) or EM_CODE_LABEL.match(line):
            state = "element"
        elif state == "element":
            unplaced.append(position)  # after an element block nothing is provenance, a field line included
        elif field:
            state = field.group("field").upper()
            fields.setdefault(state, []).append(line[field.end():].strip())
        elif state == "header":
            tail.append(line.strip())
        else:
            fields[state][-1] = (fields[state][-1] + " " + line.strip()).strip()
    return tail, fields, unplaced, end


class EmSection(NamedTuple):
    """One E/M line the check-off's E/M section renders, from ``entry_walk``."""

    index: int
    tail: list[str]
    fields: dict[str, list[str]]
    unplaced: list[int]
    end: int

    def rendered(self) -> set[int]:
        """The physical lines the E/M section shows: the line, its wrapped header, fields and EM- lines."""
        return {self.index, *range(self.index + 1, self.end)} - set(self.unplaced)


class PrivateWorksheet(NamedTuple):
    """One private worksheet, parsed once for its check-off.

    ``physical`` is the worksheet split on LF alone (``physical_lines``), an ``Anchored`` value
    carrying the selected E/M lines; ``split`` is the worksheet as the graders split it
    (``str.splitlines``), and ``split_starts`` where each physical line starts among those lines (a
    line holding another separator splits there). ``region`` is the for-entry region with its
    ``ENTRY`` matches and ``read_entries``, and ``region_lines`` the number of physical lines inside
    it. ``owners`` are the region's entry and E/M label lines, ``walks`` each walked body by line
    and ``sections`` the E/M lines the E/M section renders (``parse_private``). The handwritten
    reader turns every CR into LF, so the physical lines joined by LF are ``text``.
    """

    text: str
    physical: Anchored
    split: tuple[str, ...]
    split_starts: tuple[int, ...]
    region: str
    matches: list[re.Match[str]]
    entries: list[WorksheetEntry]
    region_lines: int
    owners: tuple[int, ...]
    walks: dict[int, tuple[list[str], dict[str, list[str]], list[int], int]]
    sections: tuple[EmSection, ...]


def parse_private(text: str) -> PrivateWorksheet:
    """The worksheet parsed once for its check-off: lines, region, every body walk and the E/M lines.

    Each entry and E/M label line of the region is walked once over the region's lines, and each
    E/M line the check-off renders after the region once over all of them; ``walks`` holds them
    by line, and ``sections`` the E/M lines the E/M section renders, in order. An E/M line after
    the region renders only when it opens its element block (an entry written inside an icd10-cpt
    step 4 block with no block is that block's text), and a selected line inside another one's
    body is part of it.
    """
    lines = physical_lines(text)
    region = entry_region(text)
    matches, entries = list(ENTRY.finditer(region)), read_entries(region)
    starts, position = [], 0
    for line in lines:
        starts.append(position)
        position += len((line + "\n").splitlines())
    starts.append(position)
    region_lines = region.count("\n") if len(region) < len(text) else len(lines)
    physical = anchored(lines, (region, entries))
    owners = sorted({region.count("\n", 0, match.start()) for match in matches}
                    | {index for index in range(region_lines) if EM_CODE_LABEL.match(lines[index])})
    walks = {index: entry_walk(lines[:region_lines], index) for index in owners}
    sections: list[EmSection] = []
    claimed: set[int] = set()
    for index in sorted(physical.selected):
        if index in claimed:
            continue
        if index >= region_lines:
            if element_body_end(lines, index, physical.selected) is None:
                continue
            walks[index] = entry_walk(lines, index)
        section = EmSection(index, *walks[index])
        claimed.update(range(index + 1, section.end))
        sections.append(section)
    return PrivateWorksheet(text, physical, tuple(text.splitlines()), tuple(starts), region, matches, entries,
                            region_lines, tuple(owners), walks, tuple(sections))


# How the check-off quotes each block: with the terminator, iteration and line splitting of the
# grader that grades it. The undocumented block has no grader and takes refusal_scan's rule.
BLOCK_READERS = {
    "filled": (OTHER_HEADING, True),
    "refusal": (ANY_HEADING, False),
    "undocumented": (ANY_HEADING, False),
}


EM_ONLY_BLOCK = "The block holds only an E/M line, shown in the E/M section below."


def block_quote(private: PrivateWorksheet, heading: re.Pattern[str], kind: str) -> str | None:
    """One icd10-cpt step 4 block as its grader reads it, less the lines the E/M section renders.

    ``worksheet_grammar.step_four_lines`` reads the block with its grader's terminator and line
    splitting (``BLOCK_READERS``); every line a ``sections`` E/M line renders (the line, its
    wrapped header, its fields and its EM- lines) is shown there once and left out here. A line the
    E/M section leaves unplaced stays quoted. None when the heading is absent; ``EM_ONLY_BLOCK``
    when the E/M section shows every line the block holds.
    """
    end, every = BLOCK_READERS[kind]
    indexes, found = step_four_lines(list(private.split), heading, end, every=every)
    if not found:
        return None
    starts = private.split_starts
    shown = {split for section in private.sections for line in section.rendered()
             for split in range(starts[line], starts[line + 1])}
    quoted_lines = [index for index in indexes if index not in shown]
    if set(indexes) & shown and not any(private.split[index].strip() for index in quoted_lines):
        return EM_ONLY_BLOCK  # the block is present, and the E/M section shows its every line
    return "\n".join(private.split[index] for index in quoted_lines).strip("\n")


def for_entry_codes(private: PrivateWorksheet) -> tuple[list[tuple[str, str, str, str, dict[str, list[str]], bool]], int]:
    """Each non-E/M region code as the manifest validation reads it, and the detail lines left unread.

    A code is (key, system, code, descriptor, fields, for entry), each value joined across its
    wrapped lines; a code marked NOT FOR ENTRY, an E/M one included, comes back with for entry
    False so its recorded lines are rendered once rather than dropped.
    The region, the entries and the for-entry split are the readers ``review_manifest.selected_codes``
    uses. A detail or indented line no entry or E/M line's body owns (``entry_walk``), or one a
    body leaves unplaced, is counted unread rather than dropped; E/M lines are read by
    ``em_entry_lines``.
    """
    region, matches = private.region, private.matches
    lines = list(private.physical.lines[:private.region_lines])
    # Every entry and E/M label line of the region owns the body entry_walk gave it; a detail or
    # indented line no body owns, such as one after a blank line, is unread rather than dropped.
    owned = set(private.owners).union(*(range(index + 1, private.walks[index][3]) for index in private.owners))
    unread = sum(1 for index, line in enumerate(lines)
                 if index not in owned and (indented_line(line) or FIELD.match(line))
                 and not EM_CANDIDATE.match(line))
    codes = []
    for match, entry in zip(matches, private.entries):
        key = review_manifest.code_key(entry.system, entry.code)
        if entry.for_entry and key == "em":
            continue  # a selected E/M line, read by em_entry_lines
        tail, fields, unplaced, _ = private.walks[region.count("\n", 0, match.start())]
        unread += len(unplaced)
        codes.append((key, entry.system.upper(), entry.code.upper(),
                      " ".join([entry.descriptor.strip(), *tail]), fields, entry.for_entry))
    return codes, unread


def field_lines(fields: dict[str, list[str]], *, defaults: bool) -> list[str]:
    """The provenance lines of one entry; ``defaults`` names an absent anchor and source."""
    out = []
    anchors = fields.get("ANCHOR") or (["not recorded"] if defaults else [])
    out += ["  - Anchor: " + anchor for anchor in anchors]
    if "SOURCE" in fields or defaults:
        out.append("  - Source: " + ("; ".join(fields["SOURCE"]) if "SOURCE" in fields else "recorded (no SOURCE line)"))
    for label in ("SPECIFICITY", "CONFIDENCE", "NOTE"):
        out += ["  - " + label.title() + ": " + value for value in fields.get(label, ())]
    return out


def em_entry_lines(private: PrivateWorksheet, tally: Tally) -> list[str]:
    """Every E/M line of the private worksheet with its wrapped header and provenance fields.

    An E/M line is one in the for-entry region, or one after it that opens its element block; an
    entry written inside an icd10-cpt step 4 block is that block's text, never an E/M line.
    """
    out: list[str] = []
    for section in private.sections:
        tally.unread += len(section.unplaced)
        out.append("- E/M line: " + " ".join([private.physical.lines[section.index].strip(), *section.tail]))
        out += field_lines(section.fields, defaults=False)
    return out


def quoted(text: str | None, empty: str = "", *, paragraphs: bool = False) -> list[str]:
    """Copied text as quotation lines, which the Markdown sheet and the Word renderer both read.

    Every line is quoted, so a line opening with a heading, bullet or quotation mark stays inside
    the quotation. ``paragraphs`` keeps a blank line as a paragraph break (a verbatim value);
    otherwise blank lines are dropped (a copied worksheet block).
    """
    if text is None or not text.strip():
        return [empty]
    lines = text.strip("\n").splitlines()
    if paragraphs:
        return ["> " + line.rstrip() if line.strip() else "" for line in lines]
    return ["> " + line.rstrip() for line in lines if line.strip()]


class SheetMoved(ValueError):
    """The committed CPT MDM sheet version the receipt fingerprinted does not parse."""


def sheet_ids(receipt: dict) -> set[str] | None:
    """The entry ids of the sheet version the receipt bound, through ``cpt_mdm_sheet.read_entries``.

    ``coding_freshness.bound_sheet_version`` finds that version in the path's git history with the
    rule that wrote the receipt's ``mdm_sheet_sha256``, so a later commit to the sheet does not
    block an older run. None when no version matches or git cannot be run, which the caller counts
    as unread. A matching version the sheet parser refuses refuses the check-off.
    ``Context`` calls it once per render or gate call and holds the result for that call only;
    nothing is remembered across calls.
    """
    cpt = receipt["sources"]["cpt"]
    path = REPOSITORY / "reference" / Path(cpt["mdm_sheet_filename"]).name
    content = coding_freshness.bound_sheet_version(path, cpt["mdm_sheet_sha256"])
    try:
        return None if content is None else set(cpt_mdm_sheet.read_entries(content.decode("utf-8")))
    except (UnicodeError, ValueError) as error:
        raise SheetMoved("the CPT MDM sheet version the receipt bound does not parse") from error


def item_lines(block_: EmBlock) -> list[str]:
    lines = []
    for item in block_.items:
        state = "counted" if item.counted else "not counted"
        lines.append(f"- [ ] {item.kind.title()}: {item.entry}, {state}; note text {item.text}; reason: {item.reason}")
    lines += ["- Rule applied: " + rule for rule in block_.rules]
    lines += ["- Answer relied on: " + answer for answer in block_.answers]
    lines += ["- ECG: " + ecg for ecg in block_.ecg]
    if block_.mdm is not None:
        problems, data, risk = (block_.mdm[element] for element in ("problems", "data", "risk"))
        lines.append(f"- MDM: problems {problems}; data {data}; risk {risk}; two of three {block_.two_of_three()}")
    if block_.level is not None:
        lines.append("- Level: " + block_.level)
    return lines


def rederivation_findings(block_: EmBlock, ids: set[str] | None) -> list[str]:
    """What an element block states against itself: the only checks a blind re-derivation takes.

    Counted items name an entry id and quote note text, ``none`` reads only ``none | not counted |
    none``, entry ids are in the bound CPT MDM sheet, the MDM line is the middle of its three
    elements, and the level is the one that MDM level selects (``cpt_identity.MDM_LEVEL_OF``).
    Nothing here compares the block with the worksheet's decisions, so a blind reader who reaches
    another level shows only as a difference.
    """
    found = []
    stated, computed = (block_.mdm or {}).get("mdm"), block_.two_of_three()
    if stated is not None and stated != computed:
        found.append(f"the MDM line states {stated}, but two of its three elements meet {computed}")
    required = MDM_LEVEL_OF.get(block_.level or "")
    if required is not None and computed is not None and required != computed:
        found.append(f"the level {block_.level} is {required} MDM, but the block's elements meet {computed}")
    for item in block_.items:
        # em-elements.md: none is written only as none | not counted | none.
        if item.entry == "none" and (item.counted or item.text != "none"):
            found.append(f"a {item.kind.title()} line with no entry id reads other than none | not counted | none")
        elif item.counted and item.text == "none":
            found.append(f"counted {item.kind.title()} {item.entry} quotes no note text")
    if ids is not None:
        found += [f"entry id {item.entry} is not in the CPT MDM sheet"
                  for item in block_.items if item.entry != "none" and item.entry not in ids]
    return found


def block_findings(block_: EmBlock, selected: str, ids: set[str] | None, note_answers: set[str] | None,
                   *, answers_unread: bool = False, billed: frozenset[str] = frozenset()) -> list[str]:
    """What the worksheet's element block states against itself and against the worksheet's decisions.

    ``rederivation_findings``, then the level against the selected code, the answer ids against the
    pre-approval answers of the note and the ECG limb against the billed codes. ``answers_unread``
    leaves the answer ids ungraded: an unreadable answers record is incomplete coverage, not a
    record shown to lack them.
    """
    found = rederivation_findings(block_, ids)
    if block_.level is not None and block_.level != selected:
        found.append(f"the block level {block_.level} differs from the selected code {selected}")
    named = [answer for answer in block_.answers if answer != "none"]
    if named and not answers_unread:
        if note_answers is None:
            found.append("the block names a pre-approval answer, but the run has no readable answers record")
        else:
            found += [f"answer {answer} is not a pre-approval answer of this note"
                      for answer in named if answer not in note_answers]
    found += ecg_findings(block_, billed)
    return found


def ecg_findings(block_: EmBlock, billed: frozenset[str]) -> list[str]:
    """Where the EM-ECG limb does not name each ADR 0443 ECG code the worksheet bills.

    em-elements.md: where the worksheet bills 93000 or 93005, the line names that code, so with
    both billed it names both. With no ECG code billed, the limb is free text and is not graded;
    a block with no EM-ECG line is already incomplete. A code is named as a whole token, and a
    billed code the line says is not billed is a finding.
    """
    codes = sorted(billed & ECG_RULES.keys())
    if not codes or not block_.ecg:
        return []
    if all(line.strip().lower() == "not applicable" for line in block_.ecg):
        return [f"the worksheet bills {', '.join(codes)}, but its EM-ECG line says not applicable"]
    found = []
    for code in codes:
        token = re.compile(rf"(?<![0-9A-Za-z]){code}(?![0-9A-Za-z])")
        named = [line for line in block_.ecg if token.search(line)]
        if any(re.search(rf"(?<![0-9A-Za-z]){code}[ \t,;:]*(?:is[ \t]+)?not[ \t]+billed", line, re.IGNORECASE)
               for line in named):
            found.append(f"the worksheet bills {code}, but its EM-ECG line says {code} is not billed")
        elif not named:
            found.append(f"the worksheet bills {code}, but its EM-ECG line does not name it")
    return found


def differences(worksheet: EmBlock | None, rederived: EmBlock, selected: str) -> list[str]:
    """Each element of the re-derivation that differs from the worksheet block."""
    found = []
    if worksheet is not None:
        # An unread worksheet line stays outside the comparison on both sides, keyed by element and
        # entry id; a line whose entry id is unreadable leaves its whole element out.
        unread = set(worksheet.unread_items)

        def population(source: EmBlock) -> Counter:
            return Counter((item.kind, item.entry, item.counted) for item in source.items
                           if (item.kind, item.entry) not in unread and (item.kind, None) not in unread)
        ours, theirs = population(worksheet), population(rederived)
        for label, extra in (("the worksheet block only", ours - theirs), ("the re-derivation only", theirs - ours)):
            for kind, entry, counted in sorted(extra.elements()):
                state = "counted" if counted else "not counted"
                found.append(f"{kind.title()} {entry} {state}: in {label}")
        if worksheet.mdm is not None and rederived.mdm is not None:
            for element in ("problems", "data", "risk", "mdm"):
                first, second = worksheet.mdm[element], rederived.mdm[element]
                if first != second:
                    found.append(f"MDM {element}: worksheet {first}, re-derivation {second}")
    if rederived.level != selected:
        found.append(f"Level: selected {selected}, re-derived {rederived.level}")
    return found


def answer_lines(answers: dict | None, unreadable: bool, order: int, tally: Tally) -> list[str]:
    """Every recorded question and reply of the note, verbatim, from the answers record alone.

    Each unverified one is unread coverage. The patient-status reply is never shown: it answers who
    the patient is, and the status line names its evidence by kind and fingerprint instead.
    """
    lines: list[str] = []
    if unreadable:
        return lines + ["The pre-approval answers record could not be read; its entries are not shown."]
    if answers is None:
        return lines + ["No pre-approval answers record exists for this run."]
    entries = preapproval_answers.entries_for(answers, order)
    if not entries:
        lines.append("No pre-approval question is recorded for this note.")
    for entry in entries:
        tally.answers_shown += 1
        levels = ", ".join(entry["levels"]) or "none named"
        if entry["verification"] == "verified":
            state = "verified as a whole clinician message"
        else:
            tally.unread += 1
            state = ("not verified: the transcript was unreadable when it was recorded, so this coverage "
                     "is incomplete")
        identifier = entry["id"]
        lines += [f"- Question {identifier}; levels named: {levels}; reply check: {state}", "",
                  *quoted(entry["question"], paragraphs=True), "", "Reply:", "",
                  *quoted(entry["clinician_reply"], paragraphs=True), ""]
    return lines


def absent_rederivation(tally: Tally, line: str) -> list[str]:
    if tally.predates:
        tally.absent_predating += 1
        return [line + " Not graded: the run's approval predates the E/M audit check."]
    tally.absent += 1
    return [line]


def rederivation_lines(run: Path, stem: str, selected: str, worksheet: EmBlock | None, tally: Tally,
                       context: Context) -> list[str]:
    path = run / OUTPUT_DIRECTORY / REDERIVATION_DIRECTORY / (stem + ".md")
    if not path.exists():
        return absent_rederivation(tally, "No re-derivation record is placed for this note.")
    try:
        text = read_handwritten_record(path, "text").require_text(force=True)
    except DamagedRecord:
        tally.damaged += 1
        return ["The re-derivation record carries content damage and was not read. Repair it and render again."]
    except (OSError, UnicodeError):
        tally.unread += 1
        return ["The re-derivation record could not be read."]
    rederived = em_block(text)
    if rederived is None:
        return absent_rederivation(tally, "The re-derivation record holds no element line, so no "
                                          "re-derivation is placed for this note.")
    if rederived.unread:
        tally.unread += rederived.unread
        return ["The re-derivation record is not a complete element block and was not compared."]
    lines = item_lines(rederived)
    # The re-derivation is held to its own consistency, so an agreement between two flawed blocks
    # cannot hide either flaw; its level against the selected code shows only as a difference.
    flaws = rederivation_findings(rederived, context.ids)
    if flaws:
        tally.rederivation_findings += len(flaws)
        lines += ["", *["- FINDING (re-derivation): " + flaw for flaw in flaws]]
    found = differences(worksheet, rederived, selected)
    if worksheet is None:
        scope = "level only, because the worksheet has no element block"
    elif worksheet.unread:
        scope = (f"elements, MDM and level on the worksheet lines read; {worksheet.unread} worksheet "
                 "element line(s) or required line(s) unread and left out")
    else:
        scope = "elements, MDM and level"
    if found:
        tally.differ += 1
        tally.differences += len(found)
        lines += ["", f"Compared ({scope}): {len(found)} difference(s), flagged for the clinician; "
                  "no code, note or worksheet was changed.", ""]
        lines += ["- DIFFERS: " + difference for difference in found]
    else:
        tally.agree += 1
        lines += ["", f"Compared ({scope}): the re-derivation agrees with the worksheet."]
    return lines


# The status evidence kinds, named for the auditor. The pointer and the status reply can carry a
# patient name or chart line (ADR 0445 ruling 4), so neither is ever rendered.
EVIDENCE_KINDS = {"identity-map": "identity map", "medatrax": "Medatrax", "clinician-answer": "clinician answer"}


def status_text(item: dict) -> str:
    """The patient status by value, evidence kind and evidence fingerprint, all from the manifest."""
    if item["setting"] != "office":
        return "not applicable; emergency department levels have no new or established axis"
    status = item["patient_status"]
    kind = EVIDENCE_KINDS.get(status["evidence"], "unrecognized")
    return f"{status['value']}; evidence: {kind}; fingerprint {status['evidence_sha256']}"


def code_lines(private: PrivateWorksheet, tally: Tally) -> list[str]:
    out: list[str] = []
    codes, unread = for_entry_codes(private)
    tally.unread += unread
    if unread:
        out.append(f"{unread} detail line(s) could not be placed under an entry and are counted in the "
                   "unread remainder.")
    for key, system, code, descriptor, fields, for_entry in codes:
        if not for_entry:
            out.append(f"- Not for entry: {system} {code} {descriptor}")
            out += field_lines(fields, defaults=False)
            continue
        tally.systems[key] += 1
        if not fields.get("ANCHOR"):
            tally.unanchored += 1
        out.append(f"- [ ] {system} {code} {descriptor}")
        out += field_lines(fields, defaults=True)
    return out or ["None recorded in the worksheet."]


class Context:
    """Run-wide records each check-off reads once."""

    def __init__(self, run: Path, receipt: dict, tally: Tally) -> None:
        self.ids = sheet_ids(receipt)
        if self.ids is None:
            tally.unread += 1  # no committed sheet version matches the receipt: entry ids are not graded
        self.unreadable = False
        try:
            self.answers = preapproval_answers.read(run)
        except UnreadableRecord:
            self.answers, self.unreadable = None, True
            tally.faults += 1
            if not collecting_errors():  # a capturing command counts the record once itself
                tally.unread += 1
        self.answer_states = ({} if self.answers is None
                              else {entry["id"]: entry["verification"] for entry in self.answers["answers"]})


def note_answer_ids(context: Context, order: int) -> set[str] | None:
    """The pre-approval answer ids of one note, or None when the run has no readable answers record."""
    if context.answers is None:
        return None
    return {entry["id"] for entry in preapproval_answers.entries_for(context.answers, order)}


def em_lines(item: dict, note: str, worksheet: str, private: PrivateWorksheet, receipt: dict, context: Context,
             tally: Tally, fingerprinted: bool) -> tuple[list[str], EmBlock | None]:
    # The manifest codes as approval reads them: stripped and upper-cased, so " 93005 " is 93005.
    codes = review_manifest.clean_codes(item["codes"])
    selected = codes["em"]
    cpt_source = receipt["sources"]["cpt"]
    mdm_name, mdm_digest = cpt_source["mdm_sheet_filename"], cpt_source["mdm_sheet_sha256"]
    marks = sorted(set(FILLED_MARK.findall(worksheet + "\n" + note)))
    tally.marks += len(marks)
    tally.systems["em"] += 1
    cpt = set(codes["cpt"])
    ecg = [ECG_RULES[code] for code in sorted(ECG_RULES) if code in cpt] or [NO_ECG_CODE]
    lines = ["- [ ] E/M code: " + selected, f"- MDM sheet: {mdm_name}, SHA-256 {mdm_digest}",
             "- Filled marks: " + ("; ".join(marks) if marks else "none"),
             *["- ECG code: " + line for line in ecg], *em_entry_lines(private, tally)]
    if not fingerprinted:
        if tally.predates:
            lines.append("- Private worksheet: no fingerprint is recorded for it; not graded, because the "
                         "run's approval predates the E/M audit check.")
        else:
            tally.unread += 1
            lines.append("- Private worksheet: no fingerprint is recorded for it, so an edit is not "
                         "detected and this note is counted in the unread remainder. Build the manifest "
                         "again to record it; an unchanged manifest stays byte-identical, so its approval "
                         "holds.")
    elements = worksheet_em_block(private.text, private.physical)
    block_ = elements.block
    tally.unread += elements.outside
    if block_ is None:
        if tally.predates:
            tally.blocks_predating += 1
        else:
            tally.blocks_absent += 1
        paragraph = EM_PARAGRAPH.search(note)
        return lines + [
            "", "The private worksheet has no element block; the run states its support below.", "",
            "Governing rules for this setting:", "", *["- " + rule for rule in GOVERNING[item["setting"]]],
            "", "The E/M paragraph of the note:", "",
            *quoted(paragraph.group(0) if paragraph else None, "Not found in the note."),
            "", "The visible Coding worksheet, as approved:", "", *quoted(worksheet, "Empty."),
        ], None
    tally.blocks_present += 1
    if block_.unread:
        tally.unread += block_.unread
        lines += ["", f"{block_.unread} element line(s) or required line(s) could not be read and are counted "
                  "in the unread remainder; the lines read follow."]
    lines += ["", "Element block from the private worksheet:", "", *item_lines(block_)]
    note_answers = note_answer_ids(context, item["order"])
    # Only an answer of this note is listed and counted below; another note's answer is a finding.
    unverified = [answer for answer in block_.answers
                  if answer in (note_answers or ()) and context.answer_states.get(answer) == "unreadable"]
    lines += [f"- Answer {answer} is recorded unverified: the transcript was unreadable, so this "
              "coverage is incomplete (counted with the answers below)" for answer in unverified]
    found = block_findings(block_, selected, context.ids, note_answers, answers_unread=context.unreadable,
                           billed=frozenset(cpt))
    if context.unreadable:
        lines.append("- Answer ids: not checked; the pre-approval answers record could not be read")
    if elements.blocks > 1:
        found.append(f"the private worksheet carries {elements.blocks} element blocks; the first is shown")
    if context.ids is None:
        lines.append("- Entry ids: not checked; no committed version of the CPT MDM sheet the receipt names "
                     "matches its fingerprint, counted once in the unread remainder")
    if found:
        tally.block_findings += len(found)
        lines += ["", *["- FINDING: " + finding for finding in found]]
    return lines, block_


def sheet(run: Path, manifest: dict, receipt: dict, item: dict, note: str, worksheet: str,
          private_text: str, context: Context, tally: Tally, fingerprinted: bool) -> str:
    private = parse_private(private_text)
    stem = Path(item["note_path"]).stem
    identifier, order, total = item["id"], item["order"], len(manifest["encounters"])
    setting = "office" if item["setting"] == "office" else "emergency department"
    visible_name = Path(item["worksheet_path"]).name
    out = [f"# E/M audit check-off: {identifier}", ""]
    out += ["## " + SECTIONS[0], "",
            f"- Encounter: {identifier} (order {order} of {total})",
            "- Note file: " + Path(item["note_path"]).name,
            "- Service date: " + manifest["service_date"],
            "- Setting: " + setting,
            "- Patient status: " + status_text(item),
            "- Coding freshness: PASS",
            f"- Rendered from {review_manifest.MANIFEST}, worksheets/{stem}.md and {visible_name}",
            "- Coding content fingerprint: " + item["normalized_sha256"], ""]
    out += ["## " + SECTIONS[1], "", *code_lines(private, tally), ""]
    blocks = ((BLOCK_HEADING, "filled"), (REFUSAL_HEADING, "refusal"), (UNDOCUMENTED_HEADING, "undocumented"))
    for index, (heading, kind) in enumerate(blocks, start=2):
        # Each block is quoted with its grader's terminator and line splitting, less the E/M section.
        text = block_quote(private, heading, kind)
        attribute = kind + "_blocks"
        setattr(tally, attribute, getattr(tally, attribute) + (text is not None))
        shown = [EM_ONLY_BLOCK] if text == EM_ONLY_BLOCK else quoted(text, "None recorded in the worksheet.")
        out += ["## " + SECTIONS[index], "", *shown, ""]
    lines, worksheet_block = em_lines(item, note, worksheet, private, receipt, context, tally, fingerprinted)
    out += ["## " + SECTIONS[5], "", *lines, ""]
    out += ["## " + SECTIONS[6], "", *answer_lines(context.answers, context.unreadable, order, tally), ""]
    selected = review_manifest.clean_codes(item["codes"])["em"]
    out += ["## " + SECTIONS[7], "", *rederivation_lines(run, stem, selected, worksheet_block, tally, context), ""]
    out += ["## " + SECTIONS[8], "", *ATTESTATION, ""]
    return "\n".join(out)


class Sheet(NamedTuple):
    order: int
    stem: str
    text: str


class PrivateWorksheetMoved(ValueError):
    """A private worksheet differs from the fingerprint ``review_manifest.build`` recorded for it."""


class UnknownNote(ValueError):
    """A --note number names no encounter of the run."""


class WordTargetRefused(ValueError):
    """A Word copy aimed inside a checkout but outside its output/ tree."""


def render(run: Path, notes: list[int]) -> tuple[Tally, int, list[Sheet]]:
    """Every selected check-off as a ``Sheet``, rendered from the validated read itself."""
    run = run.resolve()
    fingerprints = review_manifest.private_fingerprints(run) or {}
    validated = review_manifest.validated_population(run, fingerprints)
    manifest, receipt = validated.manifest, validated.receipt
    orders = [encounter.item["order"] for encounter in validated.encounters]
    if any(number not in orders for number in notes):
        raise UnknownNote("unknown note number")
    moved = [encounter.item["order"] for encounter in validated.encounters
             if encounter.item["private_worksheet_path"] in fingerprints
             and fingerprints[encounter.item["private_worksheet_path"]]
             != review_manifest.private_worksheet_sha256(encounter.private)]
    if moved:
        raise PrivateWorksheetMoved(f"private worksheet of note {moved[0]} changed after its fingerprint")
    tally = Tally()
    import completion_checks
    # Reached only on the command's --submission path: completion_gate returns its exemption for a
    # pre-start run before it renders, so inside the gate predates is always False.
    tally.predates = not completion_checks.active("em_audit:" + EXPECTED_ROW)
    context = Context(run, receipt, tally)
    sheets = []
    for encounter in validated.encounters:
        item = encounter.item
        if notes and item["order"] not in notes:
            continue
        text = sheet(run, manifest, receipt, item, encounter.note, encounter.worksheet, encounter.private,
                     context, tally, item["private_worksheet_path"] in fingerprints)
        sheets.append(Sheet(item["order"], Path(item["note_path"]).stem, text))
    return tally, len(orders), sheets


def write_markdown(run: Path, sheets: list[Sheet]) -> int:
    """Write each check-off into the private run under its run-record lock.

    Each is one ``update_tool_record`` transaction: the exclusive lock covers the strict read of
    the existing check-off and its atomic replacement, and an unchanged check-off is not rewritten.
    A failed write, an existing check-off that cannot be read included, stops with
    ``CheckOffsStopped``.
    """
    written = 0
    for sheet_ in sheets:
        payload = sheet_.text.encode("utf-8")
        try:
            path = private_target(run.resolve() / OUTPUT_DIRECTORY / (sheet_.stem + ".md"))
            path.parent.mkdir(parents=True, exist_ok=True)
            update_tool_record(path, str, lambda previous: RecordUpdate(
                None if previous == sheet_.text else payload, None))
        except (OSError, ValueError) as error:
            raise CheckOffsStopped(written, sheet_.order, error) from error
        written += 1
    return written


class WritesStopped(Exception):
    """A run of writes failed part way: how many were written, and the note number that stopped it."""

    def __init__(self, written: int, order: int, cause: BaseException) -> None:
        super().__init__(f"stopped at note {order} after {written} written")
        self.written, self.order, self.cause = written, order, cause


class CheckOffsStopped(WritesStopped):
    """A Markdown check-off write stopped."""


class WordExportStopped(WritesStopped):
    """A Word copy stopped."""


def word_folder(run: Path, output_dir: Path | None) -> Path:
    """The Word destination: under the main checkout output/ tree, or outside every checkout.

    The default folder is the run's name and a short fingerprint of its resolved path, so two runs
    sharing a name never share a folder. A destination that cannot be resolved is refused as one
    that is not permitted.
    """
    try:
        output = repo_root.output_root().resolve()
        resolved = run.resolve()
        tag = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:10]
        folder = (output / WORD_DIRECTORY / f"{resolved.name}-{tag}" if output_dir is None
                  else output_dir.expanduser().resolve())
        inside = repo_root.enclosing_checkout(folder) is not None
    except (OSError, ValueError, RuntimeError) as error:
        raise WordTargetRefused("the Word destination could not be resolved") from error
    if inside and not folder.is_relative_to(output):
        raise WordTargetRefused(str(folder))
    return folder


def export_word(run: Path, sheets: list[Sheet], output_dir: Path | None, force: bool) -> int:
    """Render the same check-off text to Word through the one shared renderer, only when asked.

    A copy that fails stops the export with ``WordExportStopped``, naming its note number and how
    many copies were already written; copies written earlier stay where they are.
    """
    from docx_write import RefusedToOverwrite, write_docx
    folder = word_folder(run, output_dir)
    written = 0
    for sheet_ in sheets:
        try:
            # literal: note text, reasons, questions and replies carry asterisks and backticks verbatim.
            write_docx(sheet_.text, folder / (sheet_.stem + ".docx"), force=force, bold_headings=True,
                       layout="plain", literal=True)
        except (RefusedToOverwrite, repo_root.ForeignCheckout, OutboundTextError, OSError) as error:
            raise WordExportStopped(written, sheet_.order, error) from error
        written += 1
    return written


def report(tally: Tally, total: int, selected: int, written: str) -> str:
    icd10, cpt, hcpcs, em = (tally.systems[key] for key in ("icd10", "cpt", "hcpcs", "em"))
    return "\n".join((
        f"em-audit: notes in run {total}; selected {selected}",
        f"codes rendered: icd10 {icd10}, cpt {cpt}, hcpcs {hcpcs}, em {em}",
        f"codes without an anchor {tally.unanchored}",
        f"worksheet blocks: filled-anchor {tally.filled_blocks}, refusal {tally.refusal_blocks}, "
        f"undocumented {tally.undocumented_blocks}",
        f"element blocks: present {tally.blocks_present}, absent {tally.blocks_absent}; findings {tally.block_findings}",
        f"E/M filled marks {tally.marks}",
        f"pre-approval answers shown {tally.answers_shown}",
        f"re-derivations: agree {tally.agree}; differ {tally.differ}; damaged {tally.damaged}; absent {tally.absent}; "
        f"findings {tally.rederivation_findings}",
        f"element differences {tally.differences}",
        *([f"not graded, approval predates the check: element blocks {tally.blocks_predating}, "
           f"re-derivations {tally.absent_predating}"] if tally.predates else []),
        written,
        format_unread_remainder(tally.unread),
    ))


def has_finding(tally: Tally, *, differences: bool, stale: int) -> bool:
    """The one finding predicate of the command and the completion gate.

    A note missing its block or re-derivation, a block finding and a damaged record are findings
    for both (ADR 0445). ``differences`` makes a re-derivation difference one: the command exits
    1 so the clinician sees it, while the gate counts it, since icd10-cpt shows it before
    approval. ``stale`` counts check-offs missing or unequal to a fresh render, which only the gate
    reads.
    """
    return bool(tally.block_findings or tally.rederivation_findings or tally.damaged or tally.blocks_absent
                or tally.absent or stale
                or (differences and tally.differ))


def status_of(tally: Tally) -> int:
    """The command's exit status: 1 for a finding, 2 for an unread remainder, else 0."""
    if has_finding(tally, differences=True, stale=0):
        return 1
    return 2 if tally.unread else 0


EXPECTED_ROW = em_audit_scope.ROW


def selects_em_level(run: Path) -> bool:
    """Whether a private worksheet of the run carries a selected E/M line; an unreadable one counts."""
    for path in sorted((run / "worksheets").glob("*.md")):
        try:
            lines = physical_lines(review_manifest.read_text(path))
        except (DamagedRecord, UnreadableRecord, OSError, UnicodeError):
            return True
        if selected_em_lines(lines):
            return True
    return False


STALE_FINDINGS = {
    review_manifest.StaleRecord: "the manifest or its freshness receipt is stale against the run",
    PrivateWorksheetMoved: "a private worksheet changed after its fingerprint was recorded",
    SheetMoved: "the CPT MDM sheet version the receipt bound does not parse",
}


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str, int]:
    """Grade every note of a coded run at its terminal submission: finding, report, unread.

    A note needs its element block, a placed re-derivation record and a written check-off equal
    to a fresh render. Differences from the re-derivation are counted, not failed: icd10-cpt
    shows each one to the clinician before approval.
    """
    skipped = em_audit_scope.not_graded(run, submission)
    if skipped is not None:
        return False, skipped, 0
    run = run.resolve()
    import completion_checks
    frozen = completion_checks.exemption(run, submission, "em_audit", EXPECTED_ROW)
    if frozen is not None:
        return False, frozen, 0
    if not (run / review_manifest.MANIFEST).exists():
        if selects_em_level(run):
            return False, (f"{EXPECTED_ROW}: incomplete - a worksheet selects an E/M level, but the run has "
                           "no coding manifest to render its check-offs from"), 1
        return False, f"{EXPECTED_ROW}: not graded - the run has no coding manifest and no E/M worksheet", 0
    try:
        tally, total, sheets = render(run, [])
    except UnreadableRecord:
        # A capturing command counts the record once itself; counting it here would count it twice.
        return False, f"{EXPECTED_ROW}: incomplete - a coding record is unreadable", 0 if collecting_errors() else 1
    except DamagedRecord:
        return True, f"{EXPECTED_ROW}: finding - a coding record carries content damage", 0
    except (review_manifest.StaleRecord, PrivateWorksheetMoved, SheetMoved) as error:
        # A record that read but no longer matches the run is a defect of the run, not unread coverage.
        return True, f"{EXPECTED_ROW}: finding - {STALE_FINDINGS[type(error)]}", 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        return False, f"{EXPECTED_ROW}: incomplete - the coding records are missing or cannot be read", 1
    stale = unreadable = 0
    # A fresh render that left something unread is not the check-off a complete read would write, so
    # a difference from it is incomplete coverage, never a stale check-off.
    compared = not (tally.unread or tally.faults)
    for sheet_ in sheets:
        try:
            current = read_tool_record(run / OUTPUT_DIRECTORY / (sheet_.stem + ".md"), str)
        except UnreadableRecord:
            unreadable += 1  # present but not read: incomplete coverage, not a missing check-off
            continue
        stale += current is None or (compared and current != sheet_.text)
    unread = tally.unread + (0 if collecting_errors() else unreadable)
    counts = (f"{total} note(s); element blocks absent {tally.blocks_absent}; block findings "
              f"{tally.block_findings}; re-derivations absent {tally.absent}, damaged {tally.damaged}, findings "
              f"{tally.rederivation_findings}, "
              f"differing {tally.differ}; check-offs missing or stale {stale}, unreadable {unreadable}"
              + ("" if compared else "; check-offs not compared, the fresh render left a record unread"))
    if has_finding(tally, differences=False, stale=stale):
        return True, f"{EXPECTED_ROW}: finding - {counts}", unread
    # A capturing command counts a fault itself, so unread can be zero while the render was partial.
    partial = unread or tally.faults or unreadable
    return False, f"{EXPECTED_ROW}: " + ("incomplete - " if partial else "clean - ") + counts, unread


WORD_REFUSALS = {
    "overwrite": "a Word copy is there that this renderer did not write; recover any edit, then pass --force",
    "target": "a Word copy goes under the output folder of the main checkout or outside every checkout",
    "character": "the Word renderer refuses a character in the check-off text",
    "write": "the file could not be written",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--note", type=int, action="append", default=[],
                        help="one-based note order; repeat for several, omit for every note")
    parser.add_argument("--write", action="store_true", help="write the Markdown check-offs into the run")
    parser.add_argument("--docx", action="store_true", help="also render the check-offs to Word")
    parser.add_argument("--output-dir", type=Path,
                        help="Word destination under the main checkout output/ or outside every checkout")
    parser.add_argument("--force", action="store_true", help="replace a Word copy docx_write would refuse")
    parser.add_argument("--submission", help="the run's submission key; a run approved before the E/M audit "
                                             "check started is not graded on missing blocks or re-derivations")
    args = parser.parse_args(argv)
    if not args.docx and (args.force or args.output_dir is not None):
        parser.error("--force and --output-dir apply only to a Word copy; pass --docx with them")
    from docx_write import RefusedToOverwrite
    import completion_checks
    try:
        with (completion_checks.grading(args.run, args.submission) if args.submission else nullcontext()):
            tally, total, sheets = render(args.run, args.note)
    except UnknownNote:
        print("em-audit: refused - a --note number is not an encounter of this run")
        return 2
    except PrivateWorksheetMoved:
        print("em-audit: refused - a private worksheet changed after its fingerprint was recorded; restore it, "
              "or build the manifest again, which records the new fingerprint and leaves the approved manifest "
              "unchanged when only provenance moved")
        return 2
    except SheetMoved:
        print("em-audit: refused - the committed CPT MDM sheet version the receipt fingerprinted does not "
              "parse with the current sheet reader; report it to a maintainer as a tool defect, since the "
              "receipt still binds that version")
        return 2
    except UnreadableRecord as error:
        print(fault_report(error, check="em-audit"))
        return 2
    except DamagedRecord as error:
        print(damaged_record_result(error, check="em-audit", force=True)[1])
        return 1
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        print("em-audit: refused - missing, invalid, or stale coding records")
        return 2
    written, refusal = [], None
    if args.write:
        try:
            written.append(f"check-offs written {write_markdown(args.run, sheets)}")
        except CheckOffsStopped as stopped:
            written.append(f"check-offs written {stopped.written}")
            refusal = f"check-offs refused at note {stopped.order} - it could not be written into the private run"
            if args.docx:
                written.append("Word copies not attempted, because a check-off was refused")
    if args.docx and refusal is None:
        try:
            written.append(f"Word copies written {export_word(args.run, sheets, args.output_dir, args.force)}")
        except WordTargetRefused:
            written.append("Word copies written 0")
            refusal = "Word copy refused - " + WORD_REFUSALS["target"]
        except WordExportStopped as stopped:
            written.append(f"Word copies written {stopped.written}")
            reason = next(text for kind, text in ((RefusedToOverwrite, WORD_REFUSALS["overwrite"]),
                                                  (repo_root.ForeignCheckout, WORD_REFUSALS["target"]),
                                                  (OutboundTextError, WORD_REFUSALS["character"]),
                                                  (OSError, WORD_REFUSALS["write"]))
                          if isinstance(stopped.cause, kind))
            refusal = f"Word copy refused at note {stopped.order} - {reason}"
    selected = len(set(args.note)) if args.note else total
    print(report(tally, total, selected, "; ".join(written) or "nothing written (pass --write or --docx)"))
    status = status_of(tally)
    if refusal is not None:
        print("em-audit: " + refusal)
        return 1 if status == 1 else 2
    return status


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
