"""Render the coding run decisions as a human-readable E/M audit check-off.

``python tools/em_audit.py RUN [--note N ...] [--write]`` reads the validated coding
manifest of the run, its passing freshness receipt, the visible Coding worksheet and
canonical private worksheet of each encounter, and any independent re-derivation record
under ``RUN/em-audit/rederivation/<note stem>.md``. With ``--write`` it writes one
check-off per selected note to ``RUN/em-audit/<note stem>.md``.

The sheet is derived from the records the coding run already wrote, so the two cannot
disagree: a manifest or receipt that approval would refuse is refused here too. Output
is counts only; the written sheets carry patient information and stay in the run.

Exit 0 when every selected note rendered and no re-derivation disagrees; 1 when a
re-derivation names a different level than the run selected, or a read record carries
content damage; 2 when the run could not be read, its manifest or receipt is missing or
stale, a note number is unknown, or a re-derivation record is unreadable.
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re

import coding_freshness
import review_manifest
from console_codec import require_python_floor, use_utf8
from encounter_openers import atomic_write
from run_grader import format_unread_remainder
from run_record_reader import (DamagedRecord, UnreadableRecord, damaged_record_result, fault_report,
                               read_handwritten_record, read_tool_record)
from worksheet_grammar import (BLOCK_HEADING, DIFFERENTIAL_HEADING, ENTRY, FIELD,
                               REFUSAL_HEADING, STEP_FOUR_START, UNDOCUMENTED_HEADING, entry_is_for_entry)

DECLARED_LIMITS = (
    "The sheet restates what the run recorded. It establishes neither that a code is correct nor "
    "that the documentation supports the level; those remain readings for the clinician and the "
    "coding graders.",
    "Problems, data and risk are rendered as the visible Coding worksheet and the E/M paragraph of "
    "the note state them. The run keeps no separate machine-readable record of each MDM element, "
    "its note text, its CPT entry id, the house rule or ADR applied, or a pre-approval answer other "
    "than office patient status, so the sheet lists the governing rules rather than the ones used.",
    "Codes for entry are read from the private worksheet before its differential and icd10-cpt step 4 "
    "blocks with the shared worksheet grammar; those blocks are copied verbatim, not parsed.",
    "The ECG line is mechanical only for 93000 and 93005 on the worksheet. Whether an emergency "
    "department or outside-tracing read was counted is left to the re-derivation.",
    "Agreement compares the re-derived code with the selected code. It does not compare the "
    "element readings, and it cannot establish that the re-derivation was written before its "
    "author read the worksheet; that order is the procedure of the skill.",
    "Validation re-reads the opener source, notes, worksheets, status evidence and receipt; a "
    "moved or edited source refuses the render even long after the shift.",
)

OUTPUT_DIRECTORY = "em-audit"
REDERIVATION_DIRECTORY = "rederivation"
SECTIONS = (
    "Encounter",
    "Codes for entry",
    "Codes resting on a filled anchor",
    "Codes refused, with what would establish them",
    "Documentation that would support a more specific code",
    "E/M level as the run selected it",
    "Independent re-derivation",
    "Clinician attestation",
)
EM_FAMILIES = coding_freshness.ED_EM | coding_freshness.OFFICE_EM
FILLED_MARK = re.compile(r"\[SOURCE: filled - (?:data|risk): [^\]\n]+\]")
EM_PARAGRAPH = re.compile(r"(?ms)^E/M:.*?(?=\n[ \t]*\n|\Z)")
LEVEL = re.compile(r"(?m)^RE-DERIVED LEVEL:[ \t]*(\d{5})[ \t]*$")
REQUIRED_LABELS = ("PROBLEM", "DATA", "RISK")
MDM_LINE = re.compile(r"(?m)^MDM:[ \t]*\S")
# The shared ANY_HEADING has no multiline flag; an icd10-cpt step 4 block ends at the next heading line.
NEXT_HEADING = re.compile(r"(?m)^[ \t]*(?:#{1,6}[ \t]+\S|---[ \t]+\S.*---[ \t]*$)")
SHARED_RULES = (
    "reference/cpt-em-mdm-2026.md entries, by id, for the service-date edition",
    "ADR 0308: problems addressed, level-changing questions, proposed drugs, threat to life",
    "ADR 0376: element reasons say not documented, never not done; the drug question",
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
NO_ECG_CODE = ("No ECG code is on the worksheet. Where the note records an ECG read, the "
               "re-derivation states which ADR 0443 limb applied.")
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
        self.marks = self.agree = self.disagree = self.damaged = self.absent = self.unread = 0
        self.written = 0


def for_entry_codes(private: str) -> list[tuple[str, str, str, dict[str, list[str]], list[str]]]:
    """Each for-entry code with its fields and any other indented detail line."""
    boundaries = [match.start() for pattern in (DIFFERENTIAL_HEADING, STEP_FOUR_START)
                  if (match := pattern.search(private)) is not None]
    region = private[:min(boundaries)] if boundaries else private
    entries = list(ENTRY.finditer(region))
    result = []
    for index, entry in enumerate(entries):
        if not entry_is_for_entry(region, entries, index):
            continue
        fields: dict[str, list[str]] = {}
        other: list[str] = []
        for line in region[entry.end():].splitlines()[1:]:
            if not line.strip() or line[0] not in " \t" or ENTRY.fullmatch(line):
                break
            field = FIELD.match(line)
            if field:
                fields.setdefault(field.group("field").upper(), []).append(line[field.end():].strip())
            else:
                other.append(line.strip())
        code = entry.group("code").upper()
        result.append((entry.group("system").upper(), code, entry.group("descriptor").strip(), fields, other))
    return result


def block(private: str, heading: re.Pattern[str]) -> str | None:
    """The verbatim text under one icd10-cpt step 4 heading, to the next heading."""
    match = heading.search(private)
    if match is None:
        return None
    following = NEXT_HEADING.search(private, match.end())
    return private[match.end():following.start() if following else len(private)].strip("\n")


def verbatim(text: str | None, empty: str) -> list[str]:
    if text is None or not text.strip():
        return [empty]
    return ["```text", *text.rstrip().splitlines(), "```"]


def system_key(system: str, code: str) -> str:
    if system.startswith("ICD"):
        return "icd10"
    if system == "CPT" and code in EM_FAMILIES:
        return "em"
    return system.lower()


def rederivation(run: Path, stem: str, selected: str, tally: Tally) -> list[str]:
    path = run / OUTPUT_DIRECTORY / REDERIVATION_DIRECTORY / (stem + ".md")
    if not path.exists():
        tally.absent += 1
        return ["Not performed. The em-audit skill describes the independent re-derivation."]
    try:
        text = read_handwritten_record(path, "text").require_text(force=True)
    except DamagedRecord:
        tally.damaged += 1
        return ["The re-derivation record carries content damage and was not read. Repair it and render again."]
    except (OSError, UnicodeError):
        tally.unread += 1
        return ["The re-derivation record could not be read."]
    levels = LEVEL.findall(text)
    has_labels = all(re.search(r"(?m)^" + label + r":[ \t]*\S", text) for label in REQUIRED_LABELS)
    if len(levels) != 1 or not has_labels or len(MDM_LINE.findall(text)) != 1:
        tally.unread += 1
        return ["The re-derivation record does not follow the em-audit record shape and was not read: it needs "
                "PROBLEM, DATA and RISK lines, one MDM line and one RE-DERIVED LEVEL line."]
    level = levels[0]
    lines = verbatim(text, "")
    if level == selected:
        tally.agree += 1
        lines.append(f"Agreement: the re-derived level {level} agrees with the selected level {selected}.")
    else:
        tally.disagree += 1
        lines.append(f"DISAGREES: the re-derived level is {level} and the selected level is {selected}. "
                     "Flagged for the clinician; no code or note was changed.")
    return lines


def status_lines(item: dict) -> tuple[str, list[str]]:
    if item["setting"] != "office":
        return "not applicable; emergency department levels have no new or established axis", []
    status = item["patient_status"]
    value, evidence, pointer = status["value"], status["evidence"], status.get("pointer", "")
    summary = f"{value}; evidence: {evidence}" + (f"; pointer: {pointer}" if pointer else "")
    reply = status.get("clinician_reply")
    answers = []
    if evidence == "clinician-answer" and reply:
        answers.append("patient status, in the words of the clinician: \"" + reply + "\"")
    return summary, answers


def code_lines(private: str, tally: Tally) -> list[str]:
    out: list[str] = []
    for system, code, descriptor, fields, other in for_entry_codes(private):
        key = system_key(system, code)
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
        out += ["  - Other: " + line for line in other]
    return out or ["None recorded in the worksheet."]


def sheet(run: Path, manifest: dict, receipt: dict, item: dict, note: str, worksheet: str,
          private: str, tally: Tally) -> str:
    stem = Path(item["note_path"]).stem
    identifier, order, total = item["id"], item["order"], len(manifest["encounters"])
    selected = item["codes"]["em"].strip().upper()
    status, answers = status_lines(item)
    setting = "office" if item["setting"] == "office" else "emergency department"
    cpt_source = receipt["sources"]["cpt"]
    mdm_name, mdm_digest = cpt_source["mdm_sheet_filename"], cpt_source["mdm_sheet_sha256"]
    visible_name = Path(item["worksheet_path"]).name
    rendered = date.today().isoformat()
    out = [f"# E/M audit check-off: {identifier}", ""]
    out += ["## " + SECTIONS[0], "",
            f"- Encounter: {identifier} (order {order} of {total})",
            "- Note file: " + Path(item["note_path"]).name,
            "- Service date: " + manifest["service_date"],
            "- Setting: " + setting,
            "- Patient status: " + status,
            "- Coding freshness: PASS, checked " + receipt["checked_as_of"],
            f"- Rendered {rendered} from {review_manifest.MANIFEST}, worksheets/{stem}.md and {visible_name}",
            "- Coding content fingerprint: " + item["normalized_sha256"], ""]
    out += ["## " + SECTIONS[1], "", *code_lines(private, tally), ""]
    blocks = ((BLOCK_HEADING, "filled_blocks"), (REFUSAL_HEADING, "refusal_blocks"),
              (UNDOCUMENTED_HEADING, "undocumented_blocks"))
    for index, (heading, attribute) in enumerate(blocks, start=2):
        text = block(private, heading)
        setattr(tally, attribute, getattr(tally, attribute) + (text is not None))
        out += ["## " + SECTIONS[index], "", *verbatim(text, "None recorded in the worksheet."), ""]
    tally.systems["em"] += 1
    marks = sorted(set(FILLED_MARK.findall(worksheet + "\n" + note)))
    tally.marks += len(marks)
    paragraph = EM_PARAGRAPH.search(note)
    cpt = set(item["codes"].get("cpt", []))
    ecg = [ECG_RULES[code] for code in sorted(ECG_RULES) if code in cpt] or [NO_ECG_CODE]
    relied = "; ".join(answers) if answers else (
        "none held in a machine-readable run record; the worksheet below states any answer it relied on")
    out += ["## " + SECTIONS[5], "",
            "- [ ] E/M code: " + selected,
            f"- MDM sheet: {mdm_name}, SHA-256 {mdm_digest}",
            "- Filled marks: " + ("; ".join(marks) if marks else "none"),
            *["- ECG: " + line for line in ecg],
            "- Clinician answers relied on: " + relied,
            "", "Governing rules for this setting:", "",
            *["- " + rule for rule in GOVERNING[item["setting"]]],
            "", "The E/M paragraph of the note:", "",
            *verbatim(paragraph.group(0) if paragraph else None, "Not found in the note."),
            "", "The visible Coding worksheet, as approved:", "", *verbatim(worksheet, "Empty."), ""]
    out += ["## " + SECTIONS[6], "", *rederivation(run, stem, selected, tally), ""]
    out += ["## " + SECTIONS[7], "", *ATTESTATION, ""]
    return "\n".join(out)


def render(run: Path, notes: list[int], write: bool) -> tuple[Tally, int]:
    run = run.resolve()
    header = read_tool_record(run / review_manifest.MANIFEST, review_manifest.decode_manifest)
    if header is None:
        raise ValueError("no coding manifest")
    manifest, contents = review_manifest.validated_population(run, batch=header["batch"])
    receipt = read_tool_record(review_manifest.resolve(run, manifest["receipt_path"]), review_manifest.decode_receipt)
    if receipt is None:
        raise ValueError("no freshness receipt")
    orders = [item["order"] for item in manifest["encounters"]]
    if any(number not in orders for number in notes):
        raise ValueError("unknown note number")
    tally = Tally()
    sheets = []
    for item, (note, worksheet) in zip(manifest["encounters"], contents):
        if notes and item["order"] not in notes:
            continue
        private = review_manifest.read_text(review_manifest.resolve(run, item["private_worksheet_path"]))
        text = sheet(run, manifest, receipt, item, note, worksheet, private, tally)
        sheets.append((Path(item["note_path"]).stem, text))
    if write:
        for stem, text in sheets:
            atomic_write(run / OUTPUT_DIRECTORY / (stem + ".md"), text.encode("utf-8"))
            tally.written += 1
    return tally, len(orders)


def report(tally: Tally, total: int, selected: int, write: bool) -> str:
    icd10, cpt, hcpcs, em = (tally.systems[key] for key in ("icd10", "cpt", "hcpcs", "em"))
    return "\n".join((
        f"em-audit: notes in run {total}; selected {selected}",
        f"codes rendered: icd10 {icd10}, cpt {cpt}, hcpcs {hcpcs}, em {em}",
        f"codes without an anchor {tally.unanchored}",
        f"worksheet blocks: filled-anchor {tally.filled_blocks}, refusal {tally.refusal_blocks}, "
        f"undocumented {tally.undocumented_blocks}",
        f"E/M filled marks {tally.marks}",
        f"re-derivations: agree {tally.agree}; disagree {tally.disagree}; damaged {tally.damaged}; "
        f"absent {tally.absent}",
        f"sheets written {tally.written}" if write else "sheets not written (pass --write)",
        format_unread_remainder(tally.unread),
    ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--note", type=int, action="append", default=[],
                        help="one-based note order; repeat for several, omit for every note")
    parser.add_argument("--write", action="store_true", help="write the check-off sheets into the run")
    args = parser.parse_args(argv)
    try:
        tally, total = render(args.run, args.note, args.write)
    except UnreadableRecord as error:
        print(fault_report(error, check="em-audit"))
        return 2
    except DamagedRecord as error:
        print(damaged_record_result(error, check="em-audit", force=True)[1])
        return 1
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        print("em-audit: refused - missing, invalid, or stale coding records")
        return 2
    selected = len(set(args.note)) if args.note else total
    print(report(tally, total, selected, args.write))
    if tally.disagree or tally.damaged:
        return 1
    return 2 if tally.unread else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
