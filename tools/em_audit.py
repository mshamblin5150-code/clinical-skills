"""Render the coding decisions of a run as a human-readable E/M audit check-off.

``python tools/em_audit.py RUN [--note N ...] [--submission KEY] [--write] [--docx [--output-dir DIR] [--force]]``
reads the validated coding manifest of the run, its passing freshness receipt, the private
worksheet of each encounter with its E/M element block, the pre-approval answers record, and
any re-derivation record under ``RUN/em-audit/rederivation/<note stem>.md``. ``--write`` writes
one Markdown check-off per selected note to ``RUN/em-audit/<note stem>.md``. ``--docx`` renders
the same text to Word through ``docx_write.write_docx`` with ``literal=True``, so copied note
text, reasons, questions and replies keep their asterisks and backticks, by default under the
owning checkout ``output/em-audit/<run name>/``; nothing writes a Word copy unless asked, and
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
note number is unknown, the CPT MDM sheet is not the one the receipt fingerprinted, a Word option
was given without ``--docx``, a check-off or Word copy was refused (naming the note number that
stopped it and the copies already written; a refused check-off leaves the Word copies unattempted),
or a candidate went unread (``unread remainder``), such as an absent CPT MDM sheet. A finding
outranks an unread remainder.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
import re
from typing import NamedTuple

import coding_freshness
import cpt_mdm_sheet
import preapproval_answers
import repo_root
import review_manifest
from console_codec import require_python_floor, use_utf8
from encounter_openers import atomic_write
from run_grader import format_unread_remainder
from run_record_reader import (DamagedRecord, OutboundTextError, UnreadableRecord, collecting_errors,
                               damaged_record_result, fault_report, read_handwritten_record, read_tool_record)
from worksheet_grammar import (BLOCK_HEADING, EM_CANDIDATE, EM_CODE_LABEL, ENTRY, FIELD, REFUSAL_HEADING,
                               UNDOCUMENTED_HEADING, EmBlock, block_text, em_anchor, em_block, entry_region,
                               opens_element_block, paired_entry, physical_lines, read_entries,
                               worksheet_em_block)


DECLARED_LIMITS = (
    "The check-off restates what the run recorded. It establishes neither that a code is correct "
    "nor that the documentation supports the level; those remain readings for the clinician and "
    "the coding graders.",
    "An element block is checked for its line shape, entry ids known to the CPT MDM sheet the "
    "receipt names, an MDM line whose level is the middle of its three elements, a LEVEL equal to "
    "the selected code, answer ids present in the pre-approval answers record, and one block per "
    "worksheet. It is not checked that the code follows from the MDM level, setting and status, "
    "that a quotation is faithful to the note, or that every element weighed was written down.",
    "Entry ids are checked only when the sheet the receipt names exists under reference/, read by "
    "cpt_mdm_sheet.read_entries; an absent sheet leaves them unchecked and counts once as unread. "
    "A present sheet that coding_freshness.committed_sheet_sha256 refuses or fingerprints otherwise "
    "than the receipt, or that the parser refuses, refuses the check-off.",
    "An answer recorded as unreadable is shown and counted as incomplete coverage; the record "
    "itself does not establish which question a reply answered. An answers record that exists but "
    "cannot be read leaves the block's answer ids unchecked and counts once as unread; an absent "
    "record is a finding for a block that names an answer.",
    "A re-derivation is compared with the lines of the worksheet block that were read, on the "
    "counted and not-counted (element, entry id) population, each MDM element and the level; an "
    "unread worksheet line is counted in the unread remainder and stays outside the comparison, "
    "with every re-derivation line of its element and entry id, or of its whole element where its "
    "entry id is unreadable. A required line that is missing rather than refused excludes nothing. "
    "Note text, reasons, rules, answers and ECG lines are rendered side by side but not compared, "
    "and nothing establishes that the re-derivation was written before its author read the "
    "worksheet.",
    "A worksheet without an element block renders the visible worksheet and the E/M paragraph of "
    "the note verbatim, with the governing rules for the setting, and a re-derivation of it is "
    "compared on the level alone. A missing block or re-derivation is not graded only for a run "
    "whose approval predates the em_audit start; the command reads that approval only through "
    "--submission, and missing evidence grants no exemption. A re-derivation file with no readable "
    "element line is not a placed re-derivation.",
    "Codes for entry are read from the private worksheet region and with the readers the "
    "manifest validation uses; the icd10-cpt step 4 blocks are copied as quotations with blank "
    "lines dropped, not parsed, through worksheet_grammar.step_four_block, the reader refusal_scan "
    "and anchor_scan grade. A block ends at a heading-shaped line or at a margin E/M line whose "
    "indented body holds an element line; a margin E/M line with no element line beneath it stays "
    "the block's text.",
    "A wrapped descriptor or field value is joined from the contiguous indented lines below its "
    "entry, the bound worksheet_grammar pairs a detail by; a field line no entry or E/M line owns, "
    "and an indented line after an element block, are counted unread. A continuation that a "
    "reader would place under a different field than its author meant cannot be told apart.",
    "Every E/M line of the for-entry region, and every later one that opens an element block, is "
    "rendered with its own provenance fields in the E/M section.",
    "The element block is bound to the approved records only through the manifest element "
    "fingerprint; a manifest without it is counted unread on each check-off, and a run with no "
    "manifest whose worksheets carry an E/M line is incomplete at submission.",
    "The ECG line is mechanical only for 93000 and 93005 on the worksheet. A billed one needs an "
    "EM-ECG limb other than not applicable, and a single billed code a limb naming it rather than "
    "only the other code; with no ECG code billed, the limb's text is not graded.",
    "Validation re-reads the opener source, notes, worksheets, status evidence and receipt; a "
    "moved or edited source refuses the check-off even long after the shift.",
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
EM_PARAGRAPH = re.compile(r"(?ms)^E/M:.*?(?=\n[ \t]*\n|\Z)")
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
        self.unread = 0
        # A run approved before the em_audit start (completion-check-starts.tsv): a missing element
        # block or re-derivation is shown and counted here, never as a finding.
        self.predates = False
        self.blocks_predating = self.absent_predating = 0


def entry_details(lines: list[str], index: int) -> tuple[list[str], dict[str, list[str]], int, int]:
    """The wrapped header tail, field values, unplaced line count and body end of the entry at ``index``.

    The body is the contiguous indented lines below the entry, the bound
    ``worksheet_grammar.detail_belongs_to_entry`` pairs a detail by; a nested entry line ends it.
    A line continues the field above it, or the header before the first field. Element lines and
    an indented E/M label belong to the element block, and an indented line after them is unplaced.
    """
    tail: list[str] = []
    fields: dict[str, list[str]] = {}
    unplaced, state, end = 0, "header", index + 1
    for line in lines[index + 1:]:
        if not line.strip() or line[0] not in " \t" or ENTRY.match(line):
            break
        end += 1
        field = FIELD.match(line)
        if EM_CANDIDATE.match(line) or EM_CODE_LABEL.match(line):
            state = "element"
        elif field:
            state = field.group("field").upper()
            fields.setdefault(state, []).append(line[field.end():].strip())
        elif state == "header":
            tail.append(line.strip())
        elif state == "element":
            unplaced += 1
        else:
            fields[state][-1] = (fields[state][-1] + " " + line.strip()).strip()
    return tail, fields, unplaced, end


def for_entry_codes(private: str) -> tuple[list[tuple[str, str, str, str, dict[str, list[str]]]], int]:
    """Each non-E/M for-entry code as the manifest validation reads it, and the detail lines left unread.

    A code is (key, system, code, descriptor, fields), each value joined across its wrapped lines.
    The region, the entries and the for-entry split are the readers ``review_manifest.selected_codes``
    uses. A field line ``worksheet_grammar.paired_entry`` gives no entry or E/M label, or an indented
    line no field owns, is counted unread rather than dropped; E/M lines are read by ``em_entry_lines``.
    """
    region = entry_region(private)
    matches = list(ENTRY.finditer(region))
    owners = sorted(matches + list(EM_CODE_LABEL.finditer(region)), key=lambda match: match.start())
    unread = sum(paired_entry(region, owners, field) is None for field in FIELD.finditer(region))
    lines = physical_lines(region)
    codes = []
    for match, entry in zip(matches, read_entries(region)):
        key = review_manifest.code_key(entry.system, entry.code)
        if not entry.for_entry or key == "em":
            continue
        tail, fields, unplaced, _ = entry_details(lines, region.count("\n", 0, match.start()))
        unread += unplaced
        codes.append((key, entry.system.upper(), entry.code.upper(),
                      " ".join([entry.descriptor.strip(), *tail]), fields))
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


def em_entry_lines(private: str, tally: Tally) -> list[str]:
    """Every E/M line of the private worksheet with its wrapped header and provenance fields.

    An E/M line is one in the for-entry region, or one after it that opens its element block; an
    entry written inside an icd10-cpt step 4 block is that block's text, never an E/M line.
    """
    lines = physical_lines(private)
    region = entry_region(private)
    region_lines = region.count("\n") if len(region) < len(private) else len(lines)
    out: list[str] = []
    claimed: set[int] = set()
    for index, line in enumerate(lines):
        if index in claimed or not em_anchor(line, review_manifest.EM_CODES):
            continue
        if index >= region_lines and not opens_element_block(lines, index):
            continue
        tail, fields, unplaced, end = entry_details(lines, index)
        claimed.update(range(index + 1, end))
        tally.unread += unplaced
        out.append("- E/M line: " + " ".join([line.strip(), *tail]))
        out += field_lines(fields, defaults=False)
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
    """The CPT MDM sheet the receipt names is not the sheet it fingerprinted, or does not parse."""


def sheet_ids(receipt: dict) -> set[str] | None:
    """The entry ids of the sheet the receipt names, through ``cpt_mdm_sheet.read_entries``.

    None when no file of that name is under reference/, which the caller counts as unread. The
    fingerprint is ``coding_freshness.committed_sheet_sha256``, the rule that wrote the receipt's
    ``mdm_sheet_sha256``; a sheet it refuses or whose fingerprint differs, or that the sheet parser
    refuses, refuses the check-off, as validation refuses any other source the receipt binds.
    """
    cpt = receipt["sources"]["cpt"]
    path = REPOSITORY / "reference" / Path(cpt["mdm_sheet_filename"]).name
    if not path.is_file():
        return None
    try:
        if coding_freshness.committed_sheet_sha256(path) != cpt["mdm_sheet_sha256"]:
            raise SheetMoved("the CPT MDM sheet differs from the receipt fingerprint")
        return set(cpt_mdm_sheet.read_entries(path.read_text(encoding="utf-8")))
    except SheetMoved:
        raise
    except (OSError, UnicodeError) as error:
        raise SheetMoved("the CPT MDM sheet could not be read") from error
    except ValueError as error:
        raise SheetMoved("the CPT MDM sheet is not the committed sheet, or does not parse") from error


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


def block_findings(block_: EmBlock, selected: str, ids: set[str] | None, note_answers: set[str] | None,
                   *, answers_unread: bool = False, billed: frozenset[str] = frozenset()) -> list[str]:
    """What an element block states against itself, the selected code and its records.

    ``answers_unread`` leaves the answer ids ungraded: an unreadable answers record is incomplete
    coverage, not a record shown to lack them.
    """
    found = []
    stated, computed = (block_.mdm or {}).get("mdm"), block_.two_of_three()
    if stated is not None and stated != computed:
        found.append(f"the MDM line states {stated}, but two of its three elements meet {computed}")
    if block_.level is not None and block_.level != selected:
        found.append(f"the block level {block_.level} differs from the selected code {selected}")
    if ids is not None:
        found += [f"entry id {item.entry} is not in the CPT MDM sheet"
                  for item in block_.items if item.entry != "none" and item.entry not in ids]
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
    """Where the EM-ECG limb contradicts the ADR 0443 ECG code the worksheet bills.

    A billed 93000 or 93005 needs an EM-ECG line other than ``not applicable``, and a single
    billed code needs its limb to name it rather than only the other code. With no ECG code
    billed, the limb is free text and is not graded.
    """
    codes = sorted(billed & ECG_RULES.keys())
    if not codes or not block_.ecg:
        return []
    if all(line.strip().lower() == "not applicable" for line in block_.ecg):
        return [f"the worksheet bills {', '.join(codes)}, but its EM-ECG line says not applicable"]
    if len(codes) == 1:
        (code,), (other,) = codes, ECG_RULES.keys() - set(codes)
        if not any(code in line for line in block_.ecg) and any(other in line for line in block_.ecg):
            return [f"the worksheet bills {code}, but its EM-ECG line names the {other} limb"]
    return []


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


def answer_lines(answers: dict | None, unreadable: bool, order: int, item: dict, tally: Tally) -> list[str]:
    """Every recorded question and reply of the note, verbatim; each unverified one is unread coverage."""
    lines = []
    status = item["patient_status"]
    if item["setting"] == "office" and status.get("evidence") == "clinician-answer" and status.get("clinician_reply"):
        lines += ["Patient status question. Reply:", "", *quoted(status["clinician_reply"], paragraphs=True), ""]
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


def rederivation_lines(run: Path, stem: str, selected: str, worksheet: EmBlock | None, tally: Tally) -> list[str]:
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
    if rederived is None or not (rederived.items or rederived.rules or rederived.answers or rederived.ecg
                                 or rederived.mdm or rederived.level):
        return absent_rederivation(tally, "The re-derivation record holds no readable element line, so no "
                                          "re-derivation is placed for this note.")
    if rederived.unread:
        tally.unread += rederived.unread if rederived else 1
        return ["The re-derivation record is not a complete element block and was not compared."]
    lines = item_lines(rederived)
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


def status_text(item: dict) -> str:
    if item["setting"] != "office":
        return "not applicable; emergency department levels have no new or established axis"
    status = item["patient_status"]
    value, evidence, pointer = status["value"], status["evidence"], status.get("pointer", "")
    return f"{value}; evidence: {evidence}" + (f"; pointer: {pointer}" if pointer else "")


def code_lines(private: str, tally: Tally) -> list[str]:
    out: list[str] = []
    codes, unread = for_entry_codes(private)
    tally.unread += unread
    if unread:
        out.append(f"{unread} detail line(s) could not be placed under an entry and are counted in the "
                   "unread remainder.")
    for key, system, code, descriptor, fields in codes:
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
            tally.unread += 1  # the sheet the receipt names is absent: entry ids are not graded
        self.unreadable = False
        try:
            self.answers = preapproval_answers.read(run)
        except UnreadableRecord:
            self.answers, self.unreadable = None, True
            if not collecting_errors():  # a capturing command counts the record once itself
                tally.unread += 1
        self.answer_states = ({} if self.answers is None
                              else {entry["id"]: entry["verification"] for entry in self.answers["answers"]})


def em_lines(item: dict, note: str, worksheet: str, private: str, receipt: dict, context: Context,
             tally: Tally) -> tuple[list[str], EmBlock | None]:
    selected = item["codes"]["em"].strip().upper()
    cpt_source = receipt["sources"]["cpt"]
    mdm_name, mdm_digest = cpt_source["mdm_sheet_filename"], cpt_source["mdm_sheet_sha256"]
    marks = sorted(set(FILLED_MARK.findall(worksheet + "\n" + note)))
    tally.marks += len(marks)
    tally.systems["em"] += 1
    cpt = set(item["codes"].get("cpt", []))
    ecg = [ECG_RULES[code] for code in sorted(ECG_RULES) if code in cpt] or [NO_ECG_CODE]
    lines = ["- [ ] E/M code: " + selected, f"- MDM sheet: {mdm_name}, SHA-256 {mdm_digest}",
             "- Filled marks: " + ("; ".join(marks) if marks else "none"),
             *["- ECG code: " + line for line in ecg], *em_entry_lines(private, tally)]
    if "element_block_sha256" not in item:
        tally.unread += 1
        lines.append("- Element block: not bound to the manifest, which predates the element fingerprint; "
                     "an edit after the manifest is not detected. Rebuild the manifest. Counted in the "
                     "unread remainder.")
    elements = worksheet_em_block(private, review_manifest.EM_CODES)
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
    note_answers = (None if context.answers is None
                    else {entry["id"] for entry in preapproval_answers.entries_for(context.answers, item["order"])})
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
        lines.append("- Entry ids: not checked; the CPT MDM sheet the receipt names is not under reference/, "
                     "counted once in the unread remainder")
    if found:
        tally.block_findings += len(found)
        lines += ["", *["- FINDING: " + finding for finding in found]]
    return lines, block_


def sheet(run: Path, manifest: dict, receipt: dict, item: dict, note: str, worksheet: str,
          private: str, context: Context, tally: Tally) -> str:
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
            "- Coding freshness: PASS, checked " + receipt["checked_as_of"],
            f"- Rendered from {review_manifest.MANIFEST}, worksheets/{stem}.md and {visible_name}",
            "- Coding content fingerprint: " + item["normalized_sha256"], ""]
    out += ["## " + SECTIONS[1], "", *code_lines(private, tally), ""]
    blocks = ((BLOCK_HEADING, "filled_blocks"), (REFUSAL_HEADING, "refusal_blocks"),
              (UNDOCUMENTED_HEADING, "undocumented_blocks"))
    for index, (heading, attribute) in enumerate(blocks, start=2):
        # The filled-anchor block is read under every heading, as anchor_scan grades it.
        text = block_text(private, heading, every=heading is BLOCK_HEADING)
        setattr(tally, attribute, getattr(tally, attribute) + (text is not None))
        out += ["## " + SECTIONS[index], "", *quoted(text, "None recorded in the worksheet."), ""]
    lines, worksheet_block = em_lines(item, note, worksheet, private, receipt, context, tally)
    out += ["## " + SECTIONS[5], "", *lines, ""]
    out += ["## " + SECTIONS[6], "", *answer_lines(context.answers, context.unreadable, order, item, tally), ""]
    selected = item["codes"]["em"].strip().upper()
    out += ["## " + SECTIONS[7], "", *rederivation_lines(run, stem, selected, worksheet_block, tally), ""]
    out += ["## " + SECTIONS[8], "", *ATTESTATION, ""]
    return "\n".join(out)


class Sheet(NamedTuple):
    order: int
    stem: str
    text: str


class UnknownNote(ValueError):
    """A --note number names no encounter of the run."""


class WordTargetRefused(ValueError):
    """A Word copy aimed inside a checkout but outside its output/ tree."""


def render(run: Path, notes: list[int]) -> tuple[Tally, int, list[Sheet]]:
    """Every selected check-off as a ``Sheet``, rendered from the validated read itself."""
    run = run.resolve()
    validated = review_manifest.validated_population(run)
    manifest, receipt = validated.manifest, validated.receipt
    orders = [encounter.item["order"] for encounter in validated.encounters]
    if any(number not in orders for number in notes):
        raise UnknownNote("unknown note number")
    tally = Tally()
    import completion_checks
    tally.predates = not completion_checks.active("em_audit:" + EXPECTED_ROW)
    context = Context(run, receipt, tally)
    sheets = []
    for encounter in validated.encounters:
        item = encounter.item
        if notes and item["order"] not in notes:
            continue
        text = sheet(run, manifest, receipt, item, encounter.note, encounter.worksheet, encounter.private,
                     context, tally)
        sheets.append(Sheet(item["order"], Path(item["note_path"]).stem, text))
    return tally, len(orders), sheets


def write_markdown(run: Path, sheets: list[Sheet]) -> int:
    """Write each check-off into the private run; a failed write stops with ``CheckOffsStopped``."""
    written = 0
    for sheet_ in sheets:
        try:
            atomic_write(run.resolve() / OUTPUT_DIRECTORY / (sheet_.stem + ".md"), sheet_.text.encode("utf-8"))
        except (OSError, ValueError) as error:
            raise CheckOffsStopped(written, sheet_.order, error) from error
        written += 1
    return written


class CheckOffsStopped(Exception):
    """A check-off write failed part way: how many were written, and the note number that stopped it."""

    def __init__(self, written: int, order: int, cause: BaseException) -> None:
        super().__init__(f"stopped at note {order} after {written} written")
        self.written, self.order, self.cause = written, order, cause


class WordExportStopped(Exception):
    """A Word copy failed part way: how many were written, and the note number that stopped it."""

    def __init__(self, written: int, order: int, cause: BaseException) -> None:
        super().__init__(f"stopped at note {order} after {written} written")
        self.written, self.order, self.cause = written, order, cause


def word_folder(run: Path, output_dir: Path | None) -> Path:
    """The Word destination: under the main checkout output/ tree, or outside every checkout."""
    output = repo_root.output_root().resolve()
    folder = (output / WORD_DIRECTORY / run.resolve().name if output_dir is None
              else output_dir.expanduser().resolve())
    if repo_root.enclosing_checkout(folder) is not None and not folder.is_relative_to(output):
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
        f"re-derivations: agree {tally.agree}; differ {tally.differ}; damaged {tally.damaged}; absent {tally.absent}",
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
    return bool(tally.block_findings or tally.damaged or tally.blocks_absent or tally.absent or stale
                or (differences and tally.differ))


def status_of(tally: Tally) -> int:
    """The command's exit status: 1 for a finding, 2 for an unread remainder, else 0."""
    if has_finding(tally, differences=True, stale=0):
        return 1
    return 2 if tally.unread else 0


EXPECTED_ROW = "the E/M audit check-offs"


def selects_em_level(run: Path) -> bool:
    """Whether a private worksheet of the run carries an E/M line; an unreadable one counts.

    icd10-cpt selects an E/M level only on the note path, where ADR 0445 ruling 6 requires the
    manifest and its check-offs, so such a run without a manifest is incomplete coverage.
    """
    for path in sorted((run / "worksheets").glob("*.md")):
        try:
            text = review_manifest.read_text(path)
        except (DamagedRecord, UnreadableRecord, OSError, UnicodeError):
            return True
        if any(em_anchor(line, review_manifest.EM_CODES) for line in text.splitlines()):
            return True
    return False


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str, int]:
    """Grade every note of a coded run at its terminal submission: finding, report, unread.

    A note needs its element block, a placed re-derivation record and a written check-off equal
    to a fresh render. Differences from the re-derivation are counted, not failed: icd10-cpt
    shows each one to the clinician before approval.
    """
    import completion_checks
    frozen = completion_checks.exemption(run, submission, "em_audit", EXPECTED_ROW)
    if frozen is not None:
        return False, frozen, 0
    if submission is None:
        return False, f"{EXPECTED_ROW}: not graded - --submission was not supplied", 0
    run = run.resolve()
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
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        return False, f"{EXPECTED_ROW}: incomplete - the coding records are missing or stale", 1
    stale = unreadable = 0
    for sheet_ in sheets:
        try:
            current = read_tool_record(run / OUTPUT_DIRECTORY / (sheet_.stem + ".md"), str)
        except UnreadableRecord:
            unreadable += 1  # present but not read: incomplete coverage, not a missing check-off
            continue
        stale += current != sheet_.text
    unread = tally.unread + (0 if collecting_errors() else unreadable)
    counts = (f"{total} note(s); element blocks absent {tally.blocks_absent}; block findings "
              f"{tally.block_findings}; re-derivations absent {tally.absent}, damaged {tally.damaged}, "
              f"differing {tally.differ}; check-offs missing or stale {stale}, unreadable {unreadable}")
    if has_finding(tally, differences=False, stale=stale):
        return True, f"{EXPECTED_ROW}: finding - {counts}", unread
    return False, f"{EXPECTED_ROW}: " + ("incomplete - " if unread else "clean - ") + counts, unread


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
    except SheetMoved:
        print("em-audit: refused - the CPT MDM sheet under reference/ is not the one the receipt fingerprinted, "
              "or it does not parse; run coding_freshness again")
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
