"""Check approved patient/visit fields, retain their ordered list, generate page scripts.

No browser or network operations occur here. All inputs and outputs stay private.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

import approval_record
import review_manifest
import visit_times
from console_codec import require_python_floor, use_utf8
from encounter_openers import atomic_write, digest, private_target, read_openers
from run_record_reader import (DamagedRecord, RecordUpdate, UnreadableRecord,
    damaged_record_result, fault_report, object_record, read_handwritten_record,
    read_tool_record, require_outbound_text, update_tool_record, locked_record)

DECLARED_LIMITS = (
    "Field blocks use complete named Markdown table or colon rows. Unknown, repeated, absent or empty fields refuse; clinical correctness of a supplied value remains the clinician's reading.",
    "Profile choices use named Course, Site and Preceptor sections with bullet, code-span or table values, or named rows in a Picklists table. Unsupported prose refuses rather than guessing a choice.",
    "An omitted opener age or sex cannot be compared and refuses; the builder never infers a demographic replacement. It compares the explicit age, any stated unit and sex-to-Gender reading only; a bare age attests no unit.",
    "The generated script resolves associated visible labels and exact select-option text, preflights the whole list and reads back assigned values. Synthetic DOM proof does not establish live Medatrax control compatibility or saved values; Patient Detail readback remains required.",
    "Checked bookkeeping uses the shared locked strict-read/atomic-replace transaction. Scripts are derived from that retained record under its artifact lock, but output files are not a cross-file transaction and later source edits require a new build.",
)

FIELDS = (
    "Visit Date", "Course", "Site", "Preceptor", "Interaction Level", "Race/Ethnicity",
    "Gender", "Age", "Age unit", "Marital status at first contact", "Primary Payment Method",
    "Case Type", "Patient Time", "Start time", "End time", "Blood pressure systolic",
    "Blood pressure diastolic", "Respiratory Rate", "Height", "BMI",
)
PICKLISTS = {"Course", "Site", "Preceptor", "Interaction Level", "Race/Ethnicity", "Gender",
    "Age unit", "Marital status at first contact", "Primary Payment Method", "Case Type", "Patient Time"}
REFERENCE = Path(__file__).resolve().parent.parent / "reference/medatrax-fields.md"
RECORD = "fill-fields.json"


def label(value: str) -> str:
    return value.strip().strip("*").strip().removesuffix(":").casefold()


def field_values(block: str) -> dict[str, str]:
    """Parse a bounded field grammar, never silently discard an unknown row."""
    values = {}
    canonical = {label(key): key for key in FIELDS}
    for line in block.splitlines()[1:]:
        if not line.strip() or re.fullmatch(r"\s*---\s*", line):
            continue
        if line.lstrip().startswith("|"):
            cells = [part.strip() for part in line.strip().strip("|").split("|")]
            if len(cells) != 2:
                raise ValueError("field block needs two-column rows")
            key, value = cells
            if label(key) == "field" and label(value) == "value" or all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                continue
        else:
            match = re.fullmatch(r"\s*(?:[-*] )?(?:\*\*)?([^:]+?)(?:\*\*)?:\s*(.*?)\s*", line)
            if match is None:
                raise ValueError("unread field-block line")
            key, value = match.groups()
        key = canonical.get(label(key))
        if key is None or key in values or not value:
            raise ValueError("unknown, duplicate or empty field")
        # Check before any per-value interpretation, including select values.
        require_outbound_text(value)
        values[key] = value
    if set(values) != set(FIELDS):
        raise ValueError("field block is incomplete")
    return values


def choices(text: str) -> list[str]:
    quoted = re.findall(r"`([^`]+)`", text)
    if quoted:
        return quoted
    return [part.strip() for part in text.split("·") if part.strip()]


def profile_choices(text: str, field: str) -> set[str]:
    aliases = {"Course": {"course", "courses"}, "Site": {"site", "sites", "location / site", "locations / sites"},
               "Preceptor": {"preceptor", "preceptors"}}[field]
    found = []
    active = False
    depth = 0
    lines = text.splitlines()
    for index, line in enumerate(lines):
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading[1])
            if active and level <= depth:
                active = False
            if label(heading[2]) in aliases:
                active, depth = True, level
            continue
        if line.lstrip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if index + 1 < len(lines) and re.fullmatch(r"\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*", lines[index + 1]):
                continue  # Column names are not account choices.
            if len(cells) >= 2 and label(cells[0]) in aliases:
                found.extend(choices(" · ".join(cells[1:])))
            elif active and len(cells) >= 1 and not re.fullmatch(r"[: -]+", cells[0]) and label(cells[0]) not in {"value", "name", "preceptor", "site", "course"}:
                found.extend(choices(cells[0]))
        elif active and (re.match(r"^\s*[-*]\s+", line) or re.fullmatch(r"\s*`[^`]+`\s*", line)):
            value = re.sub(r"^\s*[-*]\s+", "", line).strip()
            found.extend(choices(value))
        else:
            match = re.fullmatch(r"\s*(?:[-*] )?(?:\*\*)?([^:]+?)(?:\*\*)?:\s*(.+)", line)
            if match and label(match[1]) in aliases:
                found.extend(choices(match[2]))
    if not found or any(not value or "\n" in value for value in found):
        raise ValueError(f"profile has no readable {field} choices")
    return set(found)


def reference_choices(text: str, field: str) -> set[str]:
    match = re.search(r"(?m)^\*\*" + re.escape(field) + r":\*\* (.+)$", text)
    if match is None:
        raise ValueError("reference picklist unreadable")
    if field == "Interaction Level":
        scale = re.search(r"`Level (\d+)` … `Level (\d+)`", match[1])
        if scale is None:
            raise ValueError("reference scale unreadable")
        return {f"Level {number}" for number in range(int(scale[1]), int(scale[2]) + 1)}
    if field == "Patient Time":
        tail = text[match.end():]
        fence = re.search(r"```\s*\n(.*?)\n```", tail, re.S)
        if fence is None:
            raise ValueError("reference time buckets unreadable")
        return set(re.split(r"\s{2,}|\n", fence[1].strip()))
    return {value.strip().strip("` ").removesuffix(".") for value in match[1].split(" · ")}


def check_demographics(values: dict, opener: dict) -> None:
    age, sex = opener["age"], opener["sex"]
    if age is None or sex is None:
        raise ValueError("opener demographics omitted; source comparison unavailable")
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(days?|weeks?|months?|years?|[dwmy])?", age, re.I)
    units = {"d": "Days", "w": "Weeks", "m": "Months", "y": "Years"}
    unit = units.get(match[2].lower()[0]) if match and match[2] else None
    if match is None or values["Age"] != match[1] or unit is not None and values["Age unit"] != unit:
        raise ValueError("field age disagrees with opener")
    genders = {"f": "Female", "female": "Female", "m": "Male", "male": "Male",
               "transgender": "Transgender", "non-binary": "Non-binary"}
    if values["Gender"] != genders.get(sex.casefold()):
        raise ValueError("field gender disagrees with opener")


def decode_record(text: str) -> dict:
    value = object_record(text)
    if (value.get("producer") != "medatrax_fill" or type(value.get("schema")) is not int
            or value["schema"] != 1 or type(value.get("batch")) is not bool
            or not isinstance(value.get("submission"), str) or not value["submission"]
            or not re.fullmatch(r"[0-9a-f]{64}", str(value.get("approval_sha256", "")))
            or type(value.get("approval_revision")) is not int or value["approval_revision"] < 1
            or not isinstance(value.get("encounters"), list) or not value["encounters"]):
        raise ValueError("invalid fill record header")
    for number, item in enumerate(value["encounters"], 1):
        if (not isinstance(item, dict) or item.get("note") != number or type(item.get("note")) is not int
                or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("field_block_sha256", "")))
                or not isinstance(item.get("fields"), list) or len(item["fields"]) != len(FIELDS)):
            raise ValueError("invalid fill encounter")
        for field, row in zip(FIELDS, item["fields"]):
            if (not isinstance(row, dict) or set(row) != {"field", "value", "kind"}
                    or row["field"] != field or row["kind"] != ("select" if field in PICKLISTS else "text")
                    or not isinstance(row["value"], str) or not row["value"]):
                raise ValueError("invalid ordered field")
            require_outbound_text(row["value"])
    if not value["batch"] and len(value["encounters"]) != 1:
        raise ValueError("standalone fill population")
    return value


def page_script(fields: list[dict]) -> str:
    """Generate only from the retained checked ordered list."""
    return "(() => {\nconst fields = " + json.dumps(fields, ensure_ascii=False) + r""";
const norm = text => text.trim().replace(/:$/, '').trim().toLowerCase();
const plan = fields.map(field => {
  const labels = [...document.querySelectorAll('label')].filter(label => norm(label.textContent) === norm(field.field));
  const controls = [...new Set(labels.map(label => label.control || (label.htmlFor && document.getElementById(label.htmlFor)) || label.querySelector('input,select')).filter(Boolean))];
  if (controls.length !== 1) throw new Error('Missing or ambiguous control: ' + field.field);
  const element = controls[0];
  if (element.disabled || element.readOnly || (field.kind === 'select' ? element.tagName !== 'SELECT' : element.tagName !== 'INPUT')) throw new Error('Unusable control: ' + field.field);
  let value = field.value;
  if (field.kind === 'select') {
    const options = [...element.options].filter(option => option.textContent === value && !option.disabled);
    if (options.length !== 1) throw new Error('Missing or ambiguous option: ' + field.field);
    value = options[0].value;
  }
  return {element, value, field};
});
if (new Set(plan.map(row => row.element)).size !== plan.length) throw new Error('A control is shared by distinct fields');
for (const {element, value, field} of plan) {
  const prototype = field.kind === 'select' ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(prototype, 'value').set.call(element, value);
  element.dispatchEvent(new Event('input', {bubbles: true}));
  element.dispatchEvent(new Event('change', {bubbles: true}));
}
if (plan.some(({element, value}) => element.value !== value)) throw new Error('Field assignment readback mismatch');
return {checked: fields.length, assigned: plan.length};
})();
"""


def build(run: Path, *, submission: str, batch: bool, profile: Path, notes: tuple[Path, ...] = ()) -> dict:
    run = private_target(run)
    # One build owns the list and all scripts. The nested per-record transaction
    # remains responsible for strict existing reads and atomic list replacement.
    with locked_record(run / "medatrax-fill"):
        return _build(run, submission=submission, batch=batch, profile=profile, notes=notes)


def _build(run: Path, *, submission: str, batch: bool, profile: Path, notes: tuple[Path, ...]) -> dict:
    run = private_target(run)
    binding, approval = approval_record.current_clinical_approval(run, batch=batch, submission=submission)
    if notes and tuple(path.resolve() for path in notes) != binding.notes:
        raise ValueError("selected note differs from approved population")
    profile_text = read_handwritten_record(profile, "text").require_text(force=True)
    reference_text = REFERENCE.read_text(encoding="utf-8")
    allowed = {field: profile_choices(profile_text, field) if field in {"Course", "Site", "Preceptor"}
               else reference_choices(reference_text, field) for field in PICKLISTS}
    manifest = review_manifest.manifest_for(run, batch=batch)
    openers = read_openers(run)
    encounters, pairs = [], []
    for item, note, opener in zip(manifest["encounters"], binding.notes, openers["encounters"]):
        source = read_handwritten_record(note, "text").require_text(force=True)
        # The existing boundary reader normalizes whitespace. Check raw field
        # content first so normalization cannot hide an outbound control.
        raw = note.read_bytes().decode("utf-8")
        headings = list(review_manifest.HEADING.finditer(raw))
        for index, heading in enumerate(headings):
            if review_manifest.section_kind(heading.group(1) or heading.group(2)) == "fields":
                require_outbound_text(raw[heading.start():headings[index + 1].start() if index + 1 < len(headings) else len(raw)].replace("\r\n", "\n"))
        _, block = review_manifest.split_note(source)
        block_sha256 = digest(block.encode("utf-8"))
        if block_sha256 != item["field_block_sha256"]:
            raise ValueError("exact fill-read field fingerprint differs from approved manifest")
        values = field_values(block)
        check_demographics(values, opener)
        supplied_date = values["Visit Date"]
        if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", supplied_date):
            month, day, year = map(int, supplied_date.split("/"))
            visit_date = date(year, month, day)
        else:
            try:
                visit_date = date.fromisoformat(supplied_date)
            except ValueError:
                raise ValueError("visit date needs ISO or US month/day/year form") from None
        if visit_date.isoformat() != manifest["service_date"]:
            raise ValueError("visit date differs from run service date")
        for field, permitted in allowed.items():
            if values[field] not in permitted:
                raise ValueError(f"field outside exact {field} choices")
        for field in ("Start time", "End time"):
            if not re.fullmatch(r"\d{4}", values[field]):
                raise ValueError("visit time must be HHMM")
        pairs.append(tuple(visit_times.clock(values[field]) for field in ("Start time", "End time")))
        encounters.append(dict(note=item["order"], field_block_sha256=block_sha256,
            fields=[dict(field=field, value=values[field], kind="select" if field in PICKLISTS else "text") for field in FIELDS]))
    window = visit_times.read_window(run)
    if window is None:
        raise ValueError("readable shift start and duration required")
    if visit_times.check_pairs(tuple(pairs), window):
        raise ValueError("visit times fail shared duration, step, spacing or shift-window checks")
    record = dict(schema=1, producer="medatrax_fill", batch=batch, submission=submission,
                  approval_sha256=approval["sha256"], approval_revision=approval["approval_revision"], encounters=encounters)
    destination = run / "medatrax-fill" / RECORD
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    decode_record(payload.decode("utf-8"))
    def change(previous):
        return RecordUpdate(payload if previous != record else None, record)
    update_tool_record(destination, decode_record, change)
    retained = read_tool_record(destination, decode_record)
    if retained != record:
        raise ValueError("retained checked list changed before script generation")
    for encounter in retained["encounters"]:
        script = page_script(encounter["fields"])
        require_outbound_text(script)
        atomic_write(destination.with_name(f"fill-note-{encounter['note']}.js"), script.encode("utf-8"))
    return retained


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--submission", required=True)
    parser.add_argument("--profile", type=Path, required=True)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--batch", action="store_true")
    selection.add_argument("--notes", type=Path, nargs="+")
    args = parser.parse_args(argv)
    try:
        value = build(args.run, submission=args.submission, batch=args.batch, profile=args.profile, notes=tuple(args.notes or ()))
    except UnreadableRecord as failure:
        print(fault_report(failure, check="Medatrax fill"))
        print("unread remainder 1")
        return 2
    except DamagedRecord as failure:
        _, report = damaged_record_result(failure, check="Medatrax fill", force=True)
        print(report)
        return 1
    except (OSError, UnicodeError, ValueError) as failure:
        # Exception texts are fixed labels, never patient field values.
        print(f"Medatrax fill: refused - {failure}" if isinstance(failure, ValueError) else "Medatrax fill: refused - source or output unavailable")
        return 2
    print(f"Medatrax fill: {len(value['encounters'])} encounters checked; scripts generated")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
