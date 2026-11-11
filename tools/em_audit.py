"""Render the coding decisions of a run as a human-readable E/M audit check-off.

``python tools/em_audit.py RUN [--note N ...] [--write] [--docx [--output-dir DIR] [--force]]``
reads the validated coding manifest of the run, its passing freshness receipt, the private
worksheet of each encounter with its E/M element block, the pre-approval answers record, and
any re-derivation record under ``RUN/em-audit/rederivation/<note stem>.md``. ``--write`` writes
one Markdown check-off per selected note to ``RUN/em-audit/<note stem>.md``. ``--docx`` renders
the same text to Word through ``docx_write.write_docx``, by default under the owning checkout
``output/em-audit/<run name>/``; nothing writes a Word copy unless asked.

The check-off is derived from the records the coding run wrote, so the two cannot disagree: a
manifest or receipt that approval would refuse is refused here too. Output is counts only; the
written check-offs carry patient information.

Exit 0 when every selected note rendered with no finding; 1 for a finding: a note without an
element block or a placed re-derivation (ADR 0445), an element block that contradicts itself or
the selected code, an unknown CPT entry id, an answer id this note lacks, a re-derivation that
differs element by element, or a damaged handwritten record; 2 when the run could not be read, a
note number is unknown, a check-off or Word copy was refused, or a candidate went unread
(``unread remainder``). A finding outranks an unread remainder.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re

import coding_freshness
import preapproval_answers
import repo_root
import review_manifest
from console_codec import require_python_floor, use_utf8
from encounter_openers import atomic_write
from run_grader import format_unread_remainder
from run_record_reader import (DamagedRecord, OutboundTextError, UnreadableRecord, damaged_record_result,
                               fault_report, read_handwritten_record, read_tool_record)
from worksheet_grammar import (BLOCK_HEADING, ENTRY, FIELD, REFUSAL_HEADING, UNDOCUMENTED_HEADING, EmBlock,
                               block_text, em_block, entry_region, paired_entry, read_entries,
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
    "Entry ids are checked only when the sheet the receipt names exists under reference/.",
    "An answer recorded as unreadable is shown and counted as incomplete coverage; the record "
    "itself does not establish which question a reply answered.",
    "A re-derivation is compared with the lines of the worksheet block that were read, on the "
    "counted and not-counted (element, entry id) population, each MDM element and the level; an "
    "unread worksheet line is counted in the unread remainder and stays outside the comparison. "
    "Note text, reasons, rules, answers and ECG lines are rendered side by side but not compared, "
    "and nothing establishes that the re-derivation was written before its author read the "
    "worksheet.",
    "A worksheet without an element block renders the visible worksheet and the E/M paragraph of "
    "the note verbatim, with the governing rules for the setting, and a re-derivation of it is "
    "compared on the level alone.",
    "Codes for entry are read from the private worksheet region and with the readers the "
    "manifest validation uses; the icd10-cpt step 4 blocks are copied as quotations with blank "
    "lines dropped, not parsed.",
    "The ECG line is mechanical only for 93000 and 93005 on the worksheet.",
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
SHEET_ENTRY = re.compile(r"(?m)^## Entry: (\S+)[ \t]*$")
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
        self.unread = self.written = self.word = 0


def for_entry_codes(private: str) -> list[tuple[str, str, str, str, dict[str, list[str]]]]:
    """Each for-entry code as the manifest validation reads it: (key, system, code, descriptor, fields).

    The region, the entries and the for-entry split are the readers ``review_manifest.selected_codes``
    uses; each field line is paired to its entry by ``worksheet_grammar.paired_entry``.
    """
    region = entry_region(private)
    matches = list(ENTRY.finditer(region))
    fields: dict[int, dict[str, list[str]]] = {}
    for field in FIELD.finditer(region):
        owner = paired_entry(region, matches, field)
        if owner is not None:
            end = region.find("\n", field.end())
            value = region[field.end():end if end != -1 else len(region)].strip()
            fields.setdefault(owner.start(), {}).setdefault(field.group("field").upper(), []).append(value)
    return [(review_manifest.code_key(entry.system, entry.code), entry.system.upper(), entry.code.upper(),
             entry.descriptor.strip(), fields.get(entry.start, {}))
            for entry in read_entries(region) if entry.for_entry]


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


def sheet_ids(receipt: dict) -> set[str] | None:
    path = REPOSITORY / "reference" / Path(receipt["sources"]["cpt"]["mdm_sheet_filename"]).name
    try:
        return set(SHEET_ENTRY.findall(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError):
        return None


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


def block_findings(block_: EmBlock, selected: str, ids: set[str] | None, note_answers: set[str] | None) -> list[str]:
    """What an element block states against itself, the selected code and its records."""
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
    if named and note_answers is None:
        found.append("the block names a pre-approval answer, but the run has no readable answers record")
    elif named:
        found += [f"answer {answer} is not a pre-approval answer of this note"
                  for answer in named if answer not in note_answers]
    return found


def differences(worksheet: EmBlock | None, rederived: EmBlock, selected: str) -> list[str]:
    """Each element of the re-derivation that differs from the worksheet block."""
    found = []
    if worksheet is not None:
        def population(source: EmBlock) -> Counter:
            return Counter((item.kind, item.entry, item.counted) for item in source.items)
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


def rederivation_lines(run: Path, stem: str, selected: str, worksheet: EmBlock | None, tally: Tally) -> list[str]:
    path = run / OUTPUT_DIRECTORY / REDERIVATION_DIRECTORY / (stem + ".md")
    if not path.exists():
        tally.absent += 1
        return ["No re-derivation record is placed for this note."]
    try:
        text = read_handwritten_record(path, "text").require_text(force=True)
    except DamagedRecord:
        tally.damaged += 1
        return ["The re-derivation record carries content damage and was not read. Repair it and render again."]
    except (OSError, UnicodeError):
        tally.unread += 1
        return ["The re-derivation record could not be read."]
    rederived = em_block(text)
    if rederived is None or rederived.unread:
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
    for key, system, code, descriptor, fields in for_entry_codes(private):
        if key == "em":
            continue
        tally.systems[key] += 1
        anchors = fields.get("ANCHOR") or []
        if not anchors:
            tally.unanchored += 1
        out.append(f"- [ ] {system} {code} {descriptor}")
        out.append("  - Anchor: " + (anchors[0] if anchors else "not recorded"))
        source = "; ".join(fields["SOURCE"]) if "SOURCE" in fields else "recorded (no SOURCE line)"
        out.append("  - Source: " + source)
        for label in ("SPECIFICITY", "CONFIDENCE", "NOTE"):
            out += ["  - " + label.title() + ": " + value for value in fields.get(label, ())]
    return out or ["None recorded in the worksheet."]


class Context:
    """Run-wide records each check-off reads once."""

    def __init__(self, run: Path, receipt: dict, tally: Tally) -> None:
        self.ids = sheet_ids(receipt)
        self.unreadable = False
        try:
            self.answers = preapproval_answers.read(run)
        except UnreadableRecord:
            self.answers, self.unreadable = None, True
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
             *["- ECG code: " + line for line in ecg]]
    elements = worksheet_em_block(private, review_manifest.EM_CODES)
    block_ = elements.block
    tally.unread += elements.outside
    if block_ is None:
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
    unverified = [answer for answer in block_.answers if context.answer_states.get(answer) == "unreadable"]
    lines += [f"- Answer {answer} is recorded unverified: the transcript was unreadable, so this "
              "coverage is incomplete (counted with the answers below)" for answer in unverified]
    note_answers = (None if context.answers is None
                    else {entry["id"] for entry in preapproval_answers.entries_for(context.answers, item["order"])})
    found = block_findings(block_, selected, context.ids, note_answers)
    if elements.blocks > 1:
        found.append(f"the private worksheet carries {elements.blocks} element blocks; the first is shown")
    if context.ids is None:
        lines.append("- Entry ids: not checked; the CPT MDM sheet the receipt names is not under reference/")
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
        text = block_text(private, heading)
        setattr(tally, attribute, getattr(tally, attribute) + (text is not None))
        out += ["## " + SECTIONS[index], "", *quoted(text, "None recorded in the worksheet."), ""]
    lines, worksheet_block = em_lines(item, note, worksheet, private, receipt, context, tally)
    out += ["## " + SECTIONS[5], "", *lines, ""]
    out += ["## " + SECTIONS[6], "", *answer_lines(context.answers, context.unreadable, order, item, tally), ""]
    selected = item["codes"]["em"].strip().upper()
    out += ["## " + SECTIONS[7], "", *rederivation_lines(run, stem, selected, worksheet_block, tally), ""]
    out += ["## " + SECTIONS[8], "", *ATTESTATION, ""]
    return "\n".join(out)


class UnknownNote(ValueError):
    """A --note number names no encounter of the run."""


class WordTargetRefused(ValueError):
    """A Word copy aimed inside a checkout but outside its output/ tree."""


def render(run: Path, notes: list[int]) -> tuple[Tally, int, list[tuple[str, str]]]:
    """Every selected check-off as (note stem, Markdown text), rendered from the validated read itself."""
    run = run.resolve()
    validated = review_manifest.validated_population(run)
    manifest, receipt = validated.manifest, validated.receipt
    orders = [encounter.item["order"] for encounter in validated.encounters]
    if any(number not in orders for number in notes):
        raise UnknownNote("unknown note number")
    tally = Tally()
    context = Context(run, receipt, tally)
    sheets = []
    for encounter in validated.encounters:
        item = encounter.item
        if notes and item["order"] not in notes:
            continue
        text = sheet(run, manifest, receipt, item, encounter.note, encounter.worksheet, encounter.private,
                     context, tally)
        sheets.append((Path(item["note_path"]).stem, text))
    return tally, len(orders), sheets


def write_markdown(run: Path, sheets: list[tuple[str, str]]) -> int:
    for stem, text in sheets:
        atomic_write(run.resolve() / OUTPUT_DIRECTORY / (stem + ".md"), text.encode("utf-8"))
    return len(sheets)


def word_folder(run: Path, output_dir: Path | None) -> Path:
    """The Word destination: under the main checkout output/ tree, or outside every checkout."""
    output = repo_root.output_root().resolve()
    folder = (output / WORD_DIRECTORY / run.resolve().name if output_dir is None
              else output_dir.expanduser().resolve())
    if repo_root.enclosing_checkout(folder) is not None and not folder.is_relative_to(output):
        raise WordTargetRefused(str(folder))
    return folder


def export_word(run: Path, sheets: list[tuple[str, str]], output_dir: Path | None, force: bool) -> int:
    """Render the same check-off text to Word through the one shared renderer, only when asked."""
    from docx_write import write_docx
    folder = word_folder(run, output_dir)
    for stem, text in sheets:
        write_docx(text, folder / (stem + ".docx"), force=force, bold_headings=True, layout="plain")
    return len(sheets)


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
        written,
        format_unread_remainder(tally.unread),
    ))


def status_of(tally: Tally) -> int:
    """The completion gate classes: a note missing its block or re-derivation is a finding (ADR 0445)."""
    if tally.block_findings or tally.differ or tally.damaged or tally.blocks_absent or tally.absent:
        return 1
    return 2 if tally.unread else 0


EXPECTED_ROW = "the E/M audit check-offs"


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
        return False, f"{EXPECTED_ROW}: not graded - the run has no coding manifest", 0
    try:
        tally, total, sheets = render(run, [])
    except UnreadableRecord:
        return False, f"{EXPECTED_ROW}: incomplete - a coding record is unreadable", 1
    except DamagedRecord:
        return True, f"{EXPECTED_ROW}: finding - a coding record carries content damage", 0
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        return False, f"{EXPECTED_ROW}: incomplete - the coding records are missing or stale", 1
    stale = 0
    for stem, text in sheets:
        try:
            current = read_tool_record(run / OUTPUT_DIRECTORY / (stem + ".md"), str)
        except UnreadableRecord:
            current = None
        stale += current != text
    counts = (f"{total} note(s); element blocks absent {tally.blocks_absent}; block findings "
              f"{tally.block_findings}; re-derivations absent {tally.absent}, damaged {tally.damaged}, "
              f"differing {tally.differ}; check-offs missing or stale {stale}")
    if tally.blocks_absent or tally.block_findings or tally.absent or tally.damaged or stale:
        return True, f"{EXPECTED_ROW}: finding - {counts}", tally.unread
    return False, f"{EXPECTED_ROW}: " + ("incomplete - " if tally.unread else "clean - ") + counts, tally.unread


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
    args = parser.parse_args(argv)
    from docx_write import RefusedToOverwrite
    try:
        tally, total, sheets = render(args.run, args.note)
    except UnknownNote:
        print("em-audit: refused - a --note number is not an encounter of this run")
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
        except (OSError, ValueError):
            refusal = "check-offs refused - they could not be written into the private run"
    if args.docx and refusal is None:
        try:
            written.append(f"Word copies written {export_word(args.run, sheets, args.output_dir, args.force)}")
        except RefusedToOverwrite as error:
            refusal = f"Word copy refused - {error}"
        except (WordTargetRefused, repo_root.ForeignCheckout):
            refusal = ("Word copy refused - a Word copy goes under the output folder of the main checkout "
                       "or outside every checkout")
        except OutboundTextError:
            refusal = "Word copy refused - the Word renderer refuses a character in the check-off text"
        except OSError:
            refusal = "Word copy refused - the file could not be written"
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
