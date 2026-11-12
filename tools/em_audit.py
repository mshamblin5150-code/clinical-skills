"""Render the coding decisions of a run as a human-readable E/M audit check-off.

``python tools/em_audit.py RUN [--note N ...] [--submission KEY] [--write] [--docx [--output-dir DIR] [--force]]``
reads the validated coding manifest of the run, its passing freshness receipt, the private
worksheet of each encounter with its E/M element block, the pre-approval answers record, and
any re-derivation record under ``RUN/em-audit/rederivation/<note stem>.md``. ``--write`` writes
one Markdown check-off per selected note to ``RUN/em-audit/<note stem>.md``. ``--docx`` renders
the same text to Word through ``docx_write.write_docx`` with ``literal=True``, so copied note
text, reasons, questions and replies keep their asterisks and backticks, by default under the
owning checkout ``output/em-audit/<run name>-<path fingerprint>/`` and never outside that checkout's
``output/``; nothing writes a Word copy unless asked, and
``--output-dir`` or ``--force`` without ``--docx`` is refused.

The check-off is derived from the records the coding run wrote, so the two cannot disagree: a
manifest or receipt that approval would refuse is refused here too. Output is counts only; the
written check-offs carry patient information.

Exit 0 when every selected note rendered with no finding; 1 for a finding: a note without an
element block or a placed re-derivation (ADR 0445) in a run approved on or after the E/M audit
start in ``reference/completion-check-starts.tsv`` (``--submission`` reads the approval; without it
the run is judged current), an element block that contradicts itself or the selected code or the
billed ECG code, an unknown CPT entry id, an answer id this note lacks, a re-derivation that
contradicts itself or differs element by element, a record that changed or went missing after the
manifest (a note, worksheet, opener, patient status or receipt, or a private worksheet against its
recorded fingerprint), or a damaged handwritten record; 2 when the run could not be read, a tool
defect stopped the render (named by its exception type, for a maintainer), a note number is
unknown, the CPT MDM sheet version the receipt bound does not parse (a tool defect), a Word option
was given without ``--docx``, a
check-off or Word copy was refused (naming the note number that stopped it and the copies already
written; a refused check-off leaves the Word copies unattempted), or a candidate went unread
(``unread remainder``), such as no committed sheet version matching the receipt. A finding
outranks an unread remainder.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
import re
import sqlite3
from typing import NamedTuple

import coding_freshness
import cpt_mdm_sheet
from cpt_identity import EM_CODES  # the codes mdm_levels looks up; selection is worksheet_grammar's
import procedure_codes_lookup
import em_audit_scope
import preapproval_answers
import repo_root
import review_manifest
from console_codec import require_python_floor, use_utf8
from encounter_openers import digest, private_target
from run_grader import format_unread_remainder
from run_record_reader import (DamagedRecord, OutboundTextError, RecordUpdate, UnreadableRecord,
                               collecting_errors, damaged_record_result, fault_report, read_handwritten_record,
                               read_tool_record, update_tool_record)
from worksheet_grammar import (BLOCK_HEADING, EM_CANDIDATE, EM_CODE_LABEL, EM_LABEL, ENTRY, FIELD,
                               REFUSAL_HEADING, UNDOCUMENTED_HEADING, ANY_HEADING, OTHER_HEADING, Anchored,
                               EmBlock, WorksheetEntry, anchored, body_end, em_block, em_identity,
                               ecg_listed, element_block_rows, line_of, line_starts, step_four_lines,
                               worksheet_em_block)


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
    "the middle of its three elements, and a LEVEL whose CPT 2026 descriptor names that MDM level, "
    "read through procedure_codes_lookup from the verified descriptors in "
    "reference/procedure-codes-2026.sqlite for the service date (an unverified database or an E/M "
    "code with no descriptor valid on that date leaves it unread; a LEVEL outside the E/M families, "
    "or one the verified database carries no entry for, is a finding; a code whose descriptor "
    "names no MDM level, or a block whose EM-RULE declares the level selected by total time, is not "
    "held to it; a refused copy of the MDM or LEVEL line leaves that line ungraded); the "
    "worksheet block is also "
    "checked for a LEVEL equal to the selected code, answer ids present in the pre-approval answers "
    "record, the billed ECG codes, and one block per worksheet. A re-derivation takes only the "
    "first set: its level or elements against the worksheet show as differences, never findings. "
    "It is not checked that the code follows from the setting and status, that a quotation is "
    "faithful to the note, or that every element weighed was written down.",
    "Entry ids are read by cpt_mdm_sheet.read_entries from the committed version of the sheet the "
    "receipt names whose fingerprint, by coding_freshness.sheet_sha256, equals the receipt's, found "
    "in that path's git history, followed across renames. No matching version, or no git, leaves "
    "them unchecked and counts "
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
    "worksheet. Its order against the note's pre-approval answers is read from the record's "
    "modification time, with a short grace for the file clock: a record placed before the "
    "note's last answer is a finding, but a stale record touched or rewritten after the last answer "
    "passes whatever brief produced it, since nothing binds the record to the answers it read.",
    "A worksheet without an element block renders the visible worksheet and the E/M paragraph of "
    "the note verbatim, with the governing rules for the setting, and a re-derivation of it is "
    "compared on the level alone. A missing block or re-derivation is not graded only for a run "
    "whose approval predates the em_audit start; the command reads that approval only through "
    "--submission, and missing evidence grants no exemption. A re-derivation file with no element "
    "candidate line is not a placed re-derivation; one whose candidates are all refused is unread.",
    "Codes for entry are read from the private worksheet region and with the readers the "
    "manifest validation uses; the icd10-cpt step 4 blocks are copied as quotations with blank "
    "lines dropped, not parsed, through worksheet_grammar.step_four_lines with the terminator and "
    "line splitting of the grader that grades each block, under every heading of its kind "
    "(BLOCK_READERS), so a second refusal block is quoted though refusal_scan grades the first; the "
    "undocumented block, which no grader reads, takes refusal_scan's. Every line the E/M section "
    "renders (a selected E/M line that opens its element block, its wrapped header, its fields, any "
    "selected E/M line nested in its body and its EM- lines) is shown there once and left out of the quotation; a line that section leaves "
    "unplaced, and any other line, an E/M entry marked NOT FOR ENTRY included, stays the block's "
    "text as the grader reads it. The graders read the same plain lines, the E/M section included, "
    "which is measured to grade nothing on the placement em-elements.md defines; another placement "
    "is not measured.",
    "Element candidates are any upper-case EM- name and the element names in "
    "worksheet_grammar.ELEMENT_NAMES in any case and "
    "with a letter suffix, after an optional bullet or bold; a candidate the strict reader refuses "
    "is unread, counted once, and fingerprinted. A misspelled element name in another case is not "
    "a candidate.",
    "A wrapped descriptor or field value is joined from the contiguous indented lines below its "
    "entry, the bound worksheet_grammar pairs a detail by; a field line no entry or E/M line "
    "owns, such as one after a blank line, an E/M label no rule selects with every field under "
    "it, and any line after an element block other than a field of its entry, are counted unread; "
    "a field after the block in the same body is the entry's own, in the graders as in the check-off. "
    "A field under an E/M label written inside another entry's lines is the label's in the check-off "
    "and that entry's in the graders, which read no E/M label. Indented prose no entry owns, "
    "such as a wrapped list item before the entries or the wrapped value of an orphaned field, "
    "is not a detail line and is not counted, so an orphaned field written without a field name "
    "is not seen. A code marked NOT FOR ENTRY in the region is rendered, marked, with its fields. A "
    "continuation that a "
    "reader would place under a different field than its author meant cannot be told apart.",
    "Every selected E/M line (an E/M: label naming an E/M code outside the lines of an entry marked "
    "NOT FOR ENTRY, or a for-entry E/M-family CPT entry) of the for-entry "
    "region, and every later one that opens an element block, is rendered with its own provenance "
    "fields in the E/M section. EM- lines under an E/M entry marked NOT FOR ENTRY, or under a "
    "rejected E/M label inside a selected line's body, anchor no block "
    "and are counted unread as outside lines.",
    "The private worksheet is bound only through its whole-file fingerprint, which "
    "review_manifest.build records beside the manifest and never in it; the check-off compares it "
    "and approval validation does not, and a changed file refuses its own note's check-off, a "
    "finding named by note number, while the other notes render. A run with no "
    "recorded fingerprint is counted unread on each check-off, or not graded for a run whose "
    "approval predates the em_audit start; building again records it. At submission, a changed private "
    "worksheet or a stale manifest or receipt is a finding of the run, and so is a record the "
    "manifest was built from that went missing after it; a bound sheet version the current reader "
    "refuses is a tool defect, incomplete like a missing freshness receipt or an unreadable record. A "
    "check-off written before the last pre-approval answer was recorded is stale until rendered "
    "again; a check-off is compared only when its note's own render read everything, and a record "
    "outside any one note left unread (the sheet version, the CPT 2026 descriptors, the answers "
    "record) stops every comparison, named in the report. At submission, a run "
    "with no manifest is incomplete on the note path, marked by its encounter opener record, "
    "whatever its worksheets select; a direct consultation with no opener record is not graded, "
    "so a note-path run whose opener record is lost reads the same way.",
    "The EM-ECG line is read by its fixed grammar only: the codes before its | (or none, or the "
    "whole line not applicable) must equal the ECG codes (93000, 93005) the worksheet bills, and "
    "the limb text after the | is never read, so whether the limb is true of the ECG is a reading. "
    "A listed code that is no ECG code is named as such. A second EM-ECG line, or a refused one, "
    "leaves the block's ECG ungraded. "
    "A line outside the grammar is unread. A re-derivation's EM-ECG is held to the grammar alone "
    "and is never compared with the billed codes.",
    "An E/M filled mark is read from the visible worksheet and the note across line wraps within "
    "its paragraph; an opener whose bracket never closes there is counted unread. A mark spelled "
    "otherwise than [SOURCE: filled - data: or risk: ...] is not an E/M mark and is not shown.",
    "Validation re-reads the opener source, notes, worksheets, status evidence and receipt; a "
    "moved or edited source refuses the check-off even long after the shift.",
    "Each check-off is written through run_record_reader.update_tool_record: the exclusive "
    "run-record lock covers the strict read of the existing check-off and its atomic replacement, "
    "one file at a time with no transaction across notes. An existing check-off that cannot be "
    "read refuses its replacement, as tool-written run records do, except the private worksheet "
    "fingerprint record, which review_manifest.build sets aside and rebuilds when its content is "
    "damaged (a fingerprint record that cannot be opened still refuses its replacement). Word "
    "copies are outbound "
    "artifacts written by docx_write under its own overwrite refusal; a tab in the copied text "
    "renders as a space there, whitespace rather than a changed word, while the Markdown check-off "
    "keeps it as recorded.",
)


OUTPUT_DIRECTORY = "em-audit"
REDERIVATION_DIRECTORY = "rederivation"
# The one start row of the check: completion_checks.exemption reads it for the gate, and render for
# the command. completion_checks.derive still needs the EXPECTED_ROW row to exist.
START_KEY = "em_audit:completion_gate"
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
# Where a filled mark opens; its bracket may close on a later line of the same paragraph.
FILLED_OPENER = re.compile(r"\[SOURCE:\s*filled\b")
MARK_BREAK = re.compile(r"\n[ \t]*\n|\[")
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
        # Why records outside any one note went unread; any reason stops every check-off comparison.
        self.run_wide: list[str] = []
        # Notes whose private worksheet differs from its recorded fingerprint: refused, a finding.
        self.moved: list[int] = []
        self.blocks_predating = self.absent_predating = 0


def entry_walk(lines: list[str], index: int, selected: frozenset[int] | None = None
               ) -> tuple[list[str], dict[str, list[str]], list[int], int]:
    """The wrapped header tail, field values, unplaced line positions and body end of the entry at ``index``.

    The body is ``worksheet_grammar.body_end``'s, the one body rule the element block's extent is
    read by too: indented lines, and a field line while every body line before it is indented text,
    as ``detail_belongs_to_entry`` pairs a detail. A line continues the field above it, or the
    header before the first field. Element lines and an indented E/M label belong to the element
    block; a field line after the block is still the entry's own field (em-elements.md puts the
    fields first, and either order pairs), and any other line after the block is unplaced. With
    ``selected`` given, an E/M label that is not a selected E/M line is unplaced itself, and so is
    every line under it but its EM- lines, which ``worksheet_em_block`` counts; a selected label
    inside a plain entry's body owns every line under it as its own section, so this walk leaves
    them unplaced and the caller excludes them as sectioned, while inside an E/M line's body it is
    part of that line's block.
    """
    tail: list[str] = []
    fields: dict[str, list[str]] = {}
    unplaced: list[int] = []
    state, end = "header", body_end(lines, index)
    for position in range(index + 1, end):
        line = lines[position]
        field = FIELD.match(line)
        if EM_CODE_LABEL.match(line) and selected is not None and position not in selected:
            unplaced.append(position)
            state = "rejected"
        elif EM_CODE_LABEL.match(line) and selected is not None and index not in selected:
            # A selected label inside a plain entry's body owns the lines under it, its own section;
            # inside an E/M line's body it is part of that line's block.
            state = "label"
        elif EM_CODE_LABEL.match(line) and state == "rejected":
            # A selected label after a rejected one in an E/M line's body resumes that line's block
            # (worksheet_em_block reads its EM- lines as the block).
            state = "element"
        elif state in ("rejected", "label"):
            if not EM_CANDIDATE.match(line):
                unplaced.append(position)  # under another label: nothing here, or that label's section
        elif EM_CANDIDATE.match(line) or EM_CODE_LABEL.match(line):
            state = "element"
        elif state == "element" and not field:
            unplaced.append(position)  # after an element block only a field is the entry's provenance
        elif field:
            state = field.group("field").upper()
            fields.setdefault(state, []).append(line[field.end():].strip())
        elif state == "header":
            tail.append(line.strip())
        else:
            fields[state][-1] = (fields[state][-1] + " " + line.strip()).strip()
    # A field with no non-blank value is no field: an empty ANCHOR is not an anchor.
    return tail, {name: values for name, values in fields.items() if any(values)}, unplaced, end


class EmSection(NamedTuple):
    """One E/M line the check-off's E/M section renders, from ``entry_walk``.

    ``line`` is the E/M line's own physical line; a field named ``index`` would shadow
    ``tuple.index``.
    """

    line: int
    tail: list[str]
    fields: dict[str, list[str]]
    unplaced: list[int]
    end: int

    def rendered(self) -> set[int]:
        """The physical lines the E/M section shows: the line, its wrapped header, fields, nested E/M
        lines and EM- lines."""
        return {self.line, *range(self.line + 1, self.end)} - set(self.unplaced)

    def nested(self, selected: frozenset[int]) -> list[int]:
        """The selected E/M labels inside this line's body, which ``em_entry_lines`` shows as written."""
        return sorted(position for position in selected
                      if self.line < position < self.end and position not in self.unplaced)


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
    region_starts: tuple[int, ...]  # line_starts of ``region``, required so a reader never bisects nothing


def parse_private(text: str, read: review_manifest.PrivateRead | None = None) -> PrivateWorksheet:
    """The worksheet parsed once for its check-off: lines, region, every body walk and the E/M lines.

    Each entry and selected E/M line of the region is walked once over the region's lines, and each
    E/M line the check-off renders after the region once over all of them; ``walks`` holds them
    by line, and ``sections`` the E/M lines the E/M section renders, in order. An E/M line after
    the region renders only when it opens its element block (an entry written inside an icd10-cpt
    step 4 block with no block is that block's text), and a selected line inside another one's
    body is part of it. ``read`` is validation's own read of ``text``
    (``review_manifest.read_private``), so a render parses each private worksheet once.
    """
    if read is None:
        read = review_manifest.read_private(text)
    lines, region, entries = list(read.lines), read.region, read.entries
    matches = list(ENTRY.finditer(region))
    region_starts = line_starts(region)
    starts, position = [], 0
    for line in lines:
        starts.append(position)
        position += len((line + "\n").splitlines())
    starts.append(position)
    region_lines = region.count("\n") if len(region) < len(text) else len(lines)
    physical = anchored(lines, selected=read.selected)
    # Each entry and each selected E/M line of the region owns a body; an unselected label owns none.
    owners = sorted({line_of(region_starts, match.start()) for match in matches}
                    | {index for index in physical.selected if index < region_lines})
    in_region = lines[:region_lines]
    walks = {index: entry_walk(in_region, index, physical.selected) for index in owners}
    sections: list[EmSection] = []
    claimed: set[int] = set()
    for index in sorted(physical.selected):
        if index in claimed:
            continue
        if index >= region_lines:
            if element_block_rows(lines, index, physical.selected) is None:
                continue
            walks[index] = entry_walk(lines, index, physical.selected)
        section = EmSection(index, *walks[index])
        claimed.update(range(index + 1, section.end))
        sections.append(section)
    return PrivateWorksheet(text, physical, tuple(text.splitlines()), tuple(starts), region, matches, entries,
                            region_lines, tuple(owners), walks, tuple(sections), tuple(region_starts))


# How the check-off quotes each block: with the terminator and line splitting of the grader that
# grades it, under every heading of the block's kind. refusal_scan grades its first refusal block and
# counts a later heading unread; the auditor still sees every block. The undocumented block has no
# grader and takes refusal_scan's terminator.
BLOCK_READERS = {
    "filled": (OTHER_HEADING, True),
    "refusal": (ANY_HEADING, True),
    "undocumented": (ANY_HEADING, True),
}


EM_ONLY_BLOCK = "The block holds only an E/M line, shown in the E/M section below."


def block_quote(private: PrivateWorksheet, heading: re.Pattern[str], kind: str) -> str | None:
    """One icd10-cpt step 4 block as its grader reads it, less the lines the E/M section renders.

    ``worksheet_grammar.step_four_lines`` reads the block with its grader's terminator and line
    splitting (``BLOCK_READERS``); every line a ``sections`` E/M line renders (``EmSection.rendered``:
    the line, its wrapped header, its fields, any nested E/M line and its EM- lines) is shown there
    once and left out here. A line the
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
    uses. A detail line (a ``FIELD`` line or an E/M label no rule selects) no entry or E/M line's
    body owns (``entry_walk``), or a line a body leaves unplaced, is counted unread rather than
    dropped; the indented lines that continue a field are that field's, and indented prose no body
    owns, such as a wrapped list item in the steps before the entries, is no detail line and is
    not counted. EM- candidates are counted by ``worksheet_em_block``, and E/M lines are read by
    ``em_entry_lines``.
    """
    matches = private.matches
    lines = list(private.physical.lines[:private.region_lines])
    # Every entry and selected E/M line of the region owns the body entry_walk gave it; a field line
    # no body owns, such as one after a blank line, and an E/M label no rule selects are unread
    # rather than dropped. Only detail-shaped lines are candidates: an orphaned field's wrapped
    # value is the field's own, and indented prose is not a detail line.
    # A label a section claims never renders its own body, so its walk owns nothing past the
    # claiming section's end: a field there is the claimer's to place or counted unread.
    reach = {index: min([private.walks[index][3]]
                        + [section.end for section in private.sections if section.line < index < section.end])
             for index in private.owners}
    owned = set(private.owners).union(*(range(index + 1, reach[index]) for index in private.owners))
    selected = private.physical.selected
    unread = sum(1 for index, line in enumerate(lines)
                 if index not in owned and not EM_CANDIDATE.match(line)
                 and (FIELD.match(line) or EM_CODE_LABEL.match(line))
                 and index not in selected)
    # A line of an E/M section's body is that section's alone, rendered or counted unplaced there,
    # even inside another entry's body.
    sectioned = set().union(*(range(section.line, section.end) for section in private.sections))
    codes = []
    for match, entry in zip(matches, private.entries):
        key = review_manifest.code_key(entry.system, entry.code)
        if entry.for_entry and key == "em":
            continue  # a selected E/M line, read by em_entry_lines
        tail, fields, unplaced, _ = private.walks[line_of(private.region_starts, match.start())]
        unread += len(set(unplaced) - sectioned)
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
        out.append("- E/M line: " + " ".join([private.physical.lines[section.line].strip(), *section.tail]))
        out += field_lines(section.fields, defaults=False)
        # A selected E/M label inside this line's body is part of its block, shown here as written.
        out += ["- Nested E/M line: " + private.physical.lines[position].strip()
                for position in section.nested(private.physical.selected)]
        if section.unplaced:
            out += [f"- {len(section.unplaced)} line(s) in this E/M line's body could not be placed and are "
                    "counted in the unread remainder (after the element block only a field is read):", "",
                    *quoted("\n".join(private.physical.lines[position] for position in section.unplaced)), ""]
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


# em-elements.md: an EM-RULE line reading this phrase whole (time_based) declares the level
# selected by total time, so the level is not held to its own MDM line.
TIME_BASIS = "level selected by total time on the date of the encounter"
MDM_PHRASE = re.compile(r"\b(straightforward|low|moderate|high)[ \t]+(?:level[ \t]+of[ \t]+)?medical decision making",
                        re.IGNORECASE)


class MdmLevels(NamedTuple):
    """Each E/M code's MDM level, read from its verified CPT 2026 descriptor for the service date.

    ``readable`` is False when the committed procedure-code database cannot be opened or its CPT
    descriptors are not ``verified``. ``levels`` holds each code whose descriptor names one level,
    ``unleveled`` each code whose descriptor names none (99211, 99281), and ``absent`` each code of
    the E/M families a verified, complete CPT set carries no entry for at all (99210): no CPT 2026
    code. In a partial CPT set a missing code is unread, never absent.
    Any other E/M code had no readable descriptor on the service date, and its level is unread,
    never guessed.
    """

    readable: bool
    levels: dict[str, str]
    unleveled: frozenset[str]
    absent: frozenset[str] = frozenset()


def mdm_levels(service_date: str) -> MdmLevels:
    """``MdmLevels`` from ``reference/procedure-codes-2026.sqlite`` through ``procedure_codes_lookup``."""
    unreadable = MdmLevels(False, {}, frozenset())
    try:
        connection = procedure_codes_lookup.open_database()
    except (OSError, sqlite3.Error):
        return unreadable
    try:
        if not procedure_codes_lookup.cpt_descriptors_verified(connection):
            return unreadable
        levels: dict[str, str] = {}
        unleveled: set[str] = set()
        absent: set[str] = set()
        # Only a complete CPT set shows a code is not a CPT 2026 code; in a partial one a miss is unread.
        complete = procedure_codes_lookup.complete(connection, "CPT")
        # Each E/M code is looked up by itself (cpt_identity.EM_CODES), valid on the service date.
        for code in sorted(EM_CODES):
            entry = procedure_codes_lookup.describe(connection, code)
            if entry is None:
                if complete:
                    absent.add(code)  # no CPT 2026 code at all: a level naming it is a finding
                continue
            if not procedure_codes_lookup.valid_on(entry, service_date):
                continue  # no descriptor on the service date: unread if a block uses it
            named = {match.group(1).lower() for match in MDM_PHRASE.finditer(entry.description)}
            if len(named) == 1:
                levels[code] = named.pop()
            elif not named:
                unleveled.add(code)
        return MdmLevels(True, levels, frozenset(unleveled), frozenset(absent))
    except sqlite3.Error:
        return unreadable
    finally:
        connection.close()


def time_based(block_: EmBlock) -> bool:
    """Whether an EM-RULE line is the declaration em-elements.md defines, ``TIME_BASIS`` itself.

    The line is read whole, in any case and with a closing period, so a line that only mentions
    the phrase (one denying time selection, say) declares nothing and the level stays held to MDM.
    """
    return any(rule.strip().rstrip(".").strip().lower() == TIME_BASIS for rule in block_.rules)


def level_unread(block_: EmBlock, levels: MdmLevels | None) -> bool:
    """Whether the block's level against its MDM went unchecked for want of a readable descriptor.

    Only a code of the E/M families can be unread; a level naming any other code, or one the
    verified database carries no entry for, is a finding (``level_code_findings``).
    """
    if levels is None or not levels.readable or block_.level is None or time_based(block_):
        return False
    if level_code_findings(block_, levels):
        return False
    return block_.level not in levels.levels and block_.level not in levels.unleveled


def level_code_findings(block_: EmBlock, levels: MdmLevels | None) -> list[str]:
    """Where the block's EM-LEVEL names no E/M code: outside the E/M families, or no CPT 2026 code."""
    if block_.level is None:
        return []
    if not em_identity("CPT", block_.level):
        return [f"EM-LEVEL {block_.level} is not an E/M code"]
    if levels is not None and block_.level in levels.absent:
        return [f"EM-LEVEL {block_.level} is not a CPT 2026 E/M code"]
    return []


def rederivation_findings(block_: EmBlock, ids: set[str] | None, levels: MdmLevels | None = None) -> list[str]:
    """What an element block states against itself: the only checks a blind re-derivation takes.

    Counted items name an entry id and quote note text (an empty quotation quotes none), ``none`` reads only ``none | not counted |
    none``, entry ids are in the bound CPT MDM sheet, the MDM line is the middle of its three
    elements, and the level is the one that MDM level selects: the level its verified CPT 2026
    descriptor names in the committed procedure-code database (``levels``), unless an EM-RULE line
    declares the level selected by total time (``TIME_BASIS``). Nothing here compares the block
    with the worksheet's decisions, so a blind reader who reaches another level shows only as a
    difference.
    """
    found = level_code_findings(block_, levels)
    stated, computed = (block_.mdm or {}).get("mdm"), block_.two_of_three()
    if stated is not None and stated != computed:
        found.append(f"the MDM line states {stated}, but two of its three elements meet {computed}")
    required = None if levels is None or time_based(block_) else levels.levels.get(block_.level or "")
    if required is not None and computed is not None and required != computed:
        found.append(f"the level {block_.level} is {required} MDM, but the block's elements meet {computed}")
    for item in block_.items:
        # em-elements.md: none is written only as none | not counted | none.
        if item.entry == "none" and (item.counted or item.text != "none"):
            found.append(f"a {item.kind.title()} line with no entry id reads other than none | not counted | none")
        elif item.counted and (item.text == "none" or not item.text.strip('"').strip()):
            found.append(f"counted {item.kind.title()} {item.entry} quotes no note text")
    if ids is not None:
        found += [f"entry id {item.entry} is not in the CPT MDM sheet"
                  for item in block_.items if item.entry != "none" and item.entry not in ids]
    return found


def block_findings(block_: EmBlock, selected: str, ids: set[str] | None, note_answers: set[str] | None,
                   *, answers_unread: bool = False, billed: frozenset[str] = frozenset(),
                   levels: MdmLevels | None = None) -> list[str]:
    """What the worksheet's element block states against itself and against the worksheet's decisions.

    ``rederivation_findings``, then the level against the selected code, the answer ids against the
    pre-approval answers of the note and the ECG limb against the billed codes. ``answers_unread``
    leaves the answer ids ungraded: an unreadable answers record is incomplete coverage, not a
    record shown to lack them.
    """
    found = rederivation_findings(block_, ids, levels)
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


def filled_marks(text: str) -> tuple[list[str], int]:
    """The E/M filled marks of ``text`` (``FILLED_MARK``), each read across its line wraps, and
    the openers whose bracket never closes.

    A mark runs from ``[SOURCE: filled`` to the next ``]`` inside its paragraph; its whitespace is
    collapsed before it is matched, so a hard-wrapped mark reads as written on one line. An opener
    with no ``]`` before a blank line or another ``[`` is counted unread. A closed mark of another
    kind (not data or risk) is no E/M mark and is not counted.
    """
    marks: set[str] = set()
    unclosed = 0
    for opener in FILLED_OPENER.finditer(text):
        close = text.find("]", opener.start())
        broken = MARK_BREAK.search(text, opener.start() + 1)
        if close < 0 or (broken is not None and broken.start() < close):
            unclosed += 1
            continue
        mark = " ".join(text[opener.start():close + 1].split())
        if FILLED_MARK.fullmatch(mark):
            marks.add(mark)
    return sorted(marks), unclosed


def ecg_findings(block_: EmBlock, billed: frozenset[str]) -> list[str]:
    """Where the EM-ECG code list differs from the ADR 0443 ECG codes the worksheet bills.

    em-elements.md: ``EM-ECG: <the billed ECG codes, comma-separated, or none> | <the limb>`` or
    ``EM-ECG: not applicable``. The listed codes (``worksheet_grammar.ecg_listed``) must equal the
    billed ECG codes exactly; a billed code the line does not list and a listed code the worksheet
    does not bill are each a finding. The limb text is never read. A line outside the grammar is
    refused by ``em_block`` and counted unread, and a block with no EM-ECG line is already
    incomplete, so neither is graded here.
    """
    if not block_.ecg:
        return []
    billed_ecg = billed & ECG_RULES.keys()
    listed = frozenset().union(*(ecg_listed(value) for value in block_.ecg))
    found = [f"the worksheet bills {code}, but its EM-ECG line does not list it"
             for code in sorted(billed_ecg - listed)]
    found += [f"the EM-ECG line lists {code}, which is not an ECG code" if code not in ECG_RULES
              else f"the EM-ECG line lists {code}, which the worksheet does not bill"
              for code in sorted(listed - billed_ecg)]
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


STALE_REDERIVATION = ("- FINDING (re-derivation): placed before this note's last pre-approval answer was "
                      "recorded, so it never read that answer; re-derive the note (em-audit step 2) and render again")


# A file's modification time comes from the kernel's coarse clock, which can trail time.time() by
# milliseconds, so a re-derivation written just after an answer may carry an earlier stamp. Two
# seconds absorbs that; a re-derivation placed within two seconds before an answer is not one a
# reader could have written from the note and that answer.
CLOCK_GRACE_SECONDS = 2.0


def rederivation_stale(path: Path, context: Context, order: int) -> bool:
    """Whether the re-derivation was last written before the note's newest recorded answer (ADR 0445 ruling 6)."""
    if context.answers is None:
        return False
    times = [entry["recorded_at"] for entry in preapproval_answers.entries_for(context.answers, order)]
    return bool(times) and path.stat().st_mtime + CLOCK_GRACE_SECONDS < max(times)


def rederivation_lines(run: Path, stem: str, selected: str, worksheet: EmBlock | None, tally: Tally,
                       context: Context, order: int) -> list[str]:
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
    try:
        stale = rederivation_stale(path, context, order)
    except OSError:
        tally.unread += 1
        return ["The re-derivation record's time could not be read, so its order against the answers is unknown."]
    tally.rederivation_findings += stale
    prefix: list[str] = []
    if stale:
        prefix = [STALE_REDERIVATION, ""]
    if rederived.unread:
        tally.unread += rederived.unread
        return prefix + ["The re-derivation record is not a complete element block and was not compared."]
    lines = prefix + item_lines(rederived)
    # The re-derivation is held to its own consistency, so an agreement between two flawed blocks
    # cannot hide either flaw; its level against the selected code shows only as a difference.
    flaws = rederivation_findings(rederived, context.ids, context.levels)
    if level_unread(rederived, context.levels):
        tally.unread += 1
        lines += ["", f"- MDM level of {rederived.level} not checked: its CPT 2026 descriptor could not be read "
                  "for the service date; counted in the unread remainder"]
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

    def __init__(self, run: Path, receipt: dict, tally: Tally, service_date: str) -> None:
        self.ids = sheet_ids(receipt)
        if self.ids is None:
            tally.unread += 1  # no committed sheet version matches the receipt: entry ids are not graded
            tally.run_wide.append("no committed CPT MDM sheet version matches the receipt")
        self.levels = mdm_levels(service_date)
        if not self.levels.readable:
            tally.unread += 1  # no verified CPT 2026 descriptors: levels against their MDM are not graded
            tally.run_wide.append("the CPT 2026 descriptors are not verified")
        self.unreadable = False
        try:
            self.answers = preapproval_answers.read(run)
        except UnreadableRecord:
            self.answers, self.unreadable = None, True
            tally.run_wide.append("the pre-approval answers record cannot be read")
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
             tally: Tally, fingerprinted: bool, codes: dict) -> tuple[list[str], EmBlock | None]:
    # ``codes`` are the manifest codes as approval reads them (clean_codes): " 93005 " is 93005.
    selected = codes["em"]
    cpt_source = receipt["sources"]["cpt"]
    mdm_name, mdm_digest = cpt_source["mdm_sheet_filename"], cpt_source["mdm_sheet_sha256"]
    (worksheet_marks, worksheet_open), (note_marks, note_open) = filled_marks(worksheet), filled_marks(note)
    marks, unclosed = sorted(set(worksheet_marks) | set(note_marks)), worksheet_open + note_open
    tally.marks += len(marks)
    tally.unread += unclosed
    tally.systems["em"] += 1
    cpt = set(codes["cpt"])
    ecg = [ECG_RULES[code] for code in sorted(ECG_RULES) if code in cpt] or [NO_ECG_CODE]
    lines = ["- [ ] E/M code: " + selected, f"- MDM sheet: {mdm_name}, SHA-256 {mdm_digest}",
             "- Filled marks: " + ("; ".join(marks) if marks else "none")
             + (f"; {unclosed} could not be read, its bracket never closes" if unclosed else ""),
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
    elements = worksheet_em_block(private.text, private.physical, region_lines=private.region_lines)
    block_ = elements.block
    tally.unread += elements.outside
    if elements.outside:
        lines.append(f"- {elements.outside} element line(s) outside the element block could not be read and "
                     "are counted in the unread remainder; move each under its E/M line and render again")
    # Run-wide checks the re-derivation takes as well, so they are named whether or not a block exists.
    if not context.levels.readable:
        lines.append("- MDM levels: not checked; the committed procedure-code database is unreadable or its "
                     "CPT 2026 descriptors are not verified, counted once in the unread remainder")
    if context.ids is None:
        lines.append("- Entry ids: not checked; no committed version of the CPT MDM sheet the receipt names "
                     "matches its fingerprint, counted once in the unread remainder")
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
                           billed=frozenset(cpt), levels=context.levels)
    if level_unread(block_, context.levels):
        tally.unread += 1
        lines.append(f"- MDM level of {block_.level} not checked: its CPT 2026 descriptor could not be read "
                     "for the service date; counted in the unread remainder")
    if context.unreadable:
        lines.append("- Answer ids: not checked; the pre-approval answers record could not be read")
    if elements.blocks > 1:
        found.append(f"the private worksheet carries {elements.blocks} element blocks; the first is shown")
    if found:
        tally.block_findings += len(found)
        lines += ["", *["- FINDING: " + finding for finding in found]]
    # An outside EM- line is unread like a refused one: the comparison leaves it and its
    # counterpart out and names it in its scope (already counted in the remainder above).
    compared = replace(block_, unread=block_.unread + elements.outside,
                       unread_items=block_.unread_items + elements.outside_items)
    return lines, compared


def sheet(run: Path, manifest: dict, receipt: dict, item: dict, note: str, worksheet: str,
          private_text: str, context: Context, tally: Tally, fingerprinted: bool,
          read: review_manifest.PrivateRead | None = None) -> str:
    private = parse_private(private_text, read)
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
    # The manifest codes as approval reads them, cleaned once for the note.
    codes = review_manifest.clean_codes(item["codes"])
    lines, worksheet_block = em_lines(item, note, worksheet, private, receipt, context, tally, fingerprinted, codes)
    out += ["## " + SECTIONS[5], "", *lines, ""]
    out += ["## " + SECTIONS[6], "", *answer_lines(context.answers, context.unreadable, order, tally), ""]
    out += ["## " + SECTIONS[7], "", *rederivation_lines(run, stem, codes["em"], worksheet_block, tally, context, order), ""]
    out += ["## " + SECTIONS[8], "", *ATTESTATION, ""]
    return "\n".join(out)


class Sheet(NamedTuple):
    order: int
    stem: str
    text: str
    unread: int = 0  # what this note's own render left unread or faulted, run-wide records apart


class UnknownNote(ValueError):
    """A --note number names no encounter of the run."""


class RecordsRefused(ValueError):
    """The coding records are missing or invalid: validation refused them before anything rendered."""


TOOL_DEFECT_REMEDY = "report it to a maintainer; the coding records need no repair for it"


class WordTargetRefused(ValueError):
    """A Word copy aimed anywhere but the main checkout's output/ tree."""


def render(run: Path, notes: list[int]) -> tuple[Tally, int, list[Sheet]]:
    """Every selected check-off as a ``Sheet``, rendered from the validated read itself."""
    run = run.resolve()
    try:
        fingerprints = review_manifest.private_fingerprints(run) or {}
        validated = review_manifest.validated_population(run, fingerprints)
    except (review_manifest.StaleRecord, UnreadableRecord, DamagedRecord):
        raise
    except (OSError, UnicodeError, ValueError) as error:
        # Validation refuses a missing or invalid record deliberately; anything else is a tool defect.
        raise RecordsRefused(str(error)) from error
    manifest, receipt = validated.manifest, validated.receipt
    orders = [encounter.item["order"] for encounter in validated.encounters]
    if any(number not in orders for number in notes):
        raise UnknownNote("unknown note number")
    tally = Tally()
    # A private worksheet that differs from its recorded fingerprint refuses only its own note's
    # check-off, a finding named by note number; the other notes render.
    tally.moved = [encounter.item["order"] for encounter in validated.encounters
                   if (not notes or encounter.item["order"] in notes)
                   and encounter.item["private_worksheet_path"] in fingerprints
                   and fingerprints[encounter.item["private_worksheet_path"]]
                   != review_manifest.private_worksheet_sha256(encounter.private)]
    import completion_checks
    # Reached only on the command's --submission path: the gate returns its exemption for a
    # pre-start run before it renders, so inside the gate predates is always False. START_KEY is
    # the row that exemption reads, so the command and the gate cannot start on different dates.
    tally.predates = not completion_checks.active(START_KEY)
    context = Context(run, receipt, tally, manifest["service_date"])
    sheets = []
    for encounter in validated.encounters:
        item = encounter.item
        if (notes and item["order"] not in notes) or item["order"] in tally.moved:
            continue
        before = tally.unread + tally.faults
        text = sheet(run, manifest, receipt, item, encounter.note, encounter.worksheet, encounter.private,
                     context, tally, item["private_worksheet_path"] in fingerprints, encounter.read)
        sheets.append(Sheet(item["order"], Path(item["note_path"]).stem, text,
                            tally.unread + tally.faults - before))
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
    """The Word destination: under the main checkout output/ tree, and nowhere else.

    The default folder is the run's name and a short fingerprint of its resolved path, so two runs
    sharing a name never share a folder. A relative ``--output-dir`` is read from the main checkout
    root, wherever the command runs; an absolute one stays as given. A destination that cannot be resolved is refused as one
    that is not permitted.
    """
    try:
        resolved = run.resolve()
        tag = digest(str(resolved).encode("utf-8"))[:10]
        folder = (repo_root.output_root() / WORD_DIRECTORY / f"{resolved.name}-{tag}" if output_dir is None
                  else output_dir.expanduser())
        if not folder.is_absolute():
            # Relative to the main checkout root, as the help says, never to the working folder.
            folder = repo_root.main_repo_root() / folder
        # The one destination rule, docx_write's own for a patient-information artifact.
        return repo_root.ensure_main_checkout(folder, under_output=True)
    except (repo_root.ForeignCheckout, repo_root.OutsideOutput) as error:
        raise WordTargetRefused(str(error.target)) from error
    except (OSError, ValueError, RuntimeError) as error:
        raise WordTargetRefused("the Word destination could not be resolved") from error


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
            # A tab is whitespace the Word renderer refuses; it renders as a space, no word changed.
            write_docx(sheet_.text.replace("\t", " "), folder / (sheet_.stem + ".docx"), force=force,
                       bold_headings=True,
                       layout="plain", literal=True, under_output=True)
        except (RefusedToOverwrite, repo_root.ForeignCheckout, repo_root.OutsideOutput, OutboundTextError,
                OSError) as error:
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
        f"private worksheets changed after their fingerprint {len(tally.moved)}",
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
                or tally.absent or tally.moved or stale
                or (differences and tally.differ))


def status_of(tally: Tally) -> int:
    """The command's exit status: 1 for a finding, 2 for an unread remainder, else 0."""
    if has_finding(tally, differences=True, stale=0):
        return 1
    return 2 if tally.unread else 0


EXPECTED_ROW = em_audit_scope.ROW


STALE_FINDING = ("the manifest or its freshness receipt is stale against the run: a record it was built "
                 "from changed or went missing after it")
MOVED_REMEDY = ("restore it, or build the manifest again, which records the new fingerprint and leaves the "
                "approved manifest unchanged when only provenance moved")


def completion_gate(run: Path, submission: str) -> tuple[bool, str, int]:
    """Grade every note of a coded run at its terminal submission: finding, report, unread.

    A note needs its element block, a placed re-derivation record and a written check-off equal
    to a fresh render. Differences from the re-derivation are counted, not failed: icd10-cpt
    shows each one to the clinician before approval. The production path is
    ``specificity_scan.em_audit_gate``: it answers the runs ``em_audit_scope`` never grades
    without loading this module, and calls this for every other run.
    """
    run = run.resolve()
    import completion_checks
    frozen = completion_checks.exemption(run, submission, "em_audit", EXPECTED_ROW)
    if frozen is not None:
        return False, frozen, 0
    # Scope is em_audit_scope's alone: a run it grades with no manifest reads as missing records.
    try:
        tally, total, sheets = render(run, [])
    except UnreadableRecord:
        # A capturing command counts the record once itself; counting it here would count it twice.
        return False, f"{EXPECTED_ROW}: incomplete - a coding record is unreadable", 0 if collecting_errors() else 1
    except DamagedRecord:
        return True, f"{EXPECTED_ROW}: finding - a coding record carries content damage", 0
    except SheetMoved:
        # A committed sheet version the current reader refuses is a defect of the tool, not of the run.
        return False, (f"{EXPECTED_ROW}: incomplete - the committed CPT MDM sheet version the receipt "
                       "fingerprinted does not parse with the current sheet reader, a tool defect for a "
                       "maintainer"), 1
    except review_manifest.StaleRecord:
        # A record that read but no longer matches the run is a defect of the run, not unread coverage.
        return True, f"{EXPECTED_ROW}: finding - {STALE_FINDING}", 0
    except RecordsRefused:
        return False, f"{EXPECTED_ROW}: incomplete - the coding records are missing or cannot be read", 1
    except Exception as error:  # noqa: BLE001 - anything not raised deliberately is the tool's own defect
        return False, (f"{EXPECTED_ROW}: incomplete - a tool defect ({type(error).__name__}) stopped the "
                       f"render; {TOOL_DEFECT_REMEDY}"), 1
    stale = unreadable = uncompared = 0
    # A fresh render that left something unread is not the check-off a complete read would write, so
    # a difference from it is incomplete coverage, never a stale check-off. A note's own unread
    # stops only its comparison; a run-wide record left unread stops every one.
    outside = tally.unread + tally.faults - sum(sheet_.unread for sheet_ in sheets)
    reasons = tally.run_wide or (["a record outside any one note was left unread"] if outside > 0 else [])
    for sheet_ in sheets:
        try:
            current = read_tool_record(run / OUTPUT_DIRECTORY / (sheet_.stem + ".md"), str)
        except UnreadableRecord:
            unreadable += 1  # present but not read: incomplete coverage, not a missing check-off
            continue
        if current is None:
            stale += 1
        elif reasons or sheet_.unread:
            uncompared += 1
        else:
            stale += current != sheet_.text
    unread = tally.unread + (0 if collecting_errors() else unreadable)
    counts = (f"{total} note(s); element blocks absent {tally.blocks_absent}; block findings "
              f"{tally.block_findings}; re-derivations absent {tally.absent}, damaged {tally.damaged}, findings "
              f"{tally.rederivation_findings}, "
              f"differing {tally.differ}; check-offs missing or stale {stale}, unreadable {unreadable}"
              + (f"; private worksheets changed after their fingerprint {len(tally.moved)} "
                 f"({', '.join(f'note {order}' for order in tally.moved)}), {MOVED_REMEDY}" if tally.moved else ""))
    if uncompared:
        counts += (f"; check-offs not compared {uncompared}, because "
                   + ("; ".join(reasons) if reasons else "their notes' fresh render left a record unread"))
    if stale:
        # The answers section reads the pre-approval answers record, so an answer recorded after the
        # render stales every check-off of its note until it is rendered again.
        counts += ("; render the check-offs again with --write after the last pre-approval answer is "
                   "recorded, before approval")
    if has_finding(tally, differences=False, stale=stale):
        return True, f"{EXPECTED_ROW}: finding - {counts}", unread
    # A capturing command counts a fault itself, so unread can be zero while the render was partial.
    partial = unread or tally.faults or unreadable
    return False, f"{EXPECTED_ROW}: " + ("incomplete - " if partial else "clean - ") + counts, unread


WORD_REFUSALS = {
    "overwrite": "a Word copy is there that this renderer did not write; recover any edit, then pass --force",
    "target": "a Word copy goes only under the output folder of the main checkout",
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
                        help="Word destination under the main checkout output/; a relative path "
                             "is read from the main checkout root")
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
    except review_manifest.StaleRecord:
        print("em-audit: finding - a coding record changed or went missing after the manifest (a note, "
              "worksheet, opener, patient status or receipt); restore it, or rebuild the manifest and run "
              "coding_freshness again")
        return 1
    except SheetMoved:
        print("em-audit: refused - the committed CPT MDM sheet version the receipt fingerprinted does not "
              "parse with the current sheet reader; report it to a maintainer as a tool defect, since the "
              "receipt still binds that version")
        return 2
    except UnreadableRecord as error:
        # skills/em-audit/SKILL.md step 1: a record that cannot be read is refused; icd10-cpt rebuilds it.
        print("em-audit: refused - a tool-written coding record cannot be read; have icd10-cpt rebuild it")
        print(fault_report(error, check="em-audit"))
        return 2
    except DamagedRecord as error:
        print(damaged_record_result(error, check="em-audit", force=True)[1])
        return 1
    except RecordsRefused:
        print("em-audit: refused - missing, invalid or unreadable coding records")
        return 2
    except Exception as error:  # noqa: BLE001 - anything not raised deliberately is the tool's own defect
        print(f"em-audit: refused - a tool defect ({type(error).__name__}) stopped the render; {TOOL_DEFECT_REMEDY}")
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
                                                  ((repo_root.ForeignCheckout, repo_root.OutsideOutput),
                                                   WORD_REFUSALS["target"]),
                                                  (OutboundTextError, WORD_REFUSALS["character"]),
                                                  (OSError, WORD_REFUSALS["write"]))
                          if isinstance(stopped.cause, kind))
            # An outbound refusal names only a line and a code point, never the text.
            cause = f" ({stopped.cause})" if isinstance(stopped.cause, OutboundTextError) else ""
            refusal = f"Word copy refused at note {stopped.order} - {reason}{cause}"
    selected = len(set(args.note)) if args.note else total
    print(report(tally, total, selected, "; ".join(written) or "nothing written (pass --write or --docx)"))
    for order in tally.moved:
        print(f"em-audit: finding - the private worksheet of note {order} changed after the manifest recorded "
              f"its fingerprint, so its check-off is refused; {MOVED_REMEDY}")
    status = status_of(tally)
    if refusal is not None:
        print("em-audit: " + refusal)
        return 1 if status == 1 else 2
    return status


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
