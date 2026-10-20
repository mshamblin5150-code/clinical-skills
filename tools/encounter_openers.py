"""Split source text and retain agent-read openers; append identity rows (ADR 0427).

Private inputs and outputs contain patient information. Reports contain counts only.
The JSON contract and its validation live here; handwritten inputs and machine
bookkeeping retain their separate shared reader boundaries.
"""
from __future__ import annotations

import argparse
from run_record_reader import read_handwritten_record, DamagedRecord, damaged_record_result
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid

import artifact_lock
from console_codec import require_python_floor, use_utf8
from corpus_census import NOTE_DELIMITER
from repo_root import enclosing_checkout
from run_record_reader import (read_tool_record, outbound_text_damage, object_record, UnreadableRecord,
                               fault_report, update_tool_record, RecordUpdate)


DECLARED_LIMITS = (
    "Opener creation and answers use the shared exclusive read/change/atomic replace transaction. Encounter artifacts publish before the opener record, not as a cross-file transaction. The account identity map retains its existing exclusive map lock and atomic replacement.",
    "Existing opener bookkeeping uses the shared strict decoder; an unreadable record refuses record, answer and identity operations without replacing it and contributes one unread record.",
    ("clinical reading", "Names are checked for literal presence, not patient identity; age and sex are supplied readings, never extracted or inferred."),
    ("hand boundaries", "Full character coverage is checked; clinical correctness of a supplied cut and its reason remains a reader's judgment."),
    ("collision judgments", "Each same-name reference needs a reason; the writer cannot establish that two people are different."),
    ("identity map grammar", "Rows are Markdown pipe-table rows. A name outside a table or a name spelled differently is not a same-name match."),
    ("publication interruption", "The opener JSON is published last. Interrupted encounter-file writes can leave files without a record; readers refuse missing or changed evidence."),
)


def private_target(path: Path) -> Path:
    path = path.resolve()
    checkout = enclosing_checkout(path)
    if checkout is not None and not path.is_relative_to(checkout / "scratch"):
        raise ValueError("private output must be under scratch")
    return path


def atomic_write(path: Path, content: bytes) -> None:
    """Keep private bytes beside their destination, never in the system temp folder."""
    path = private_target(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    created_temporary = False
    try:
        with temporary.open("xb") as stream:
            created_temporary = True
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        created_temporary = False
        if path.read_bytes() != content:
            raise ValueError("written artifact did not read back")
    finally:
        if created_temporary:
            temporary.unlink(missing_ok=True)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_cell(value: object, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("invalid text field")
    if any(c in value for c in "|\r\n") or outbound_text_damage(value):
        raise ValueError("invalid text field characters")
    return value


def clean_reply(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or outbound_text_damage(value):
        raise ValueError("invalid clinician answer")
    return value


def population(items: object) -> list[dict]:
    if not isinstance(items, list) or not items:
        raise ValueError("empty encounter population")
    for position, item in enumerate(items, 1):
        if not isinstance(item, dict) or type(item.get("note")) is not int or item["note"] != position:
            raise ValueError("encounter numbering must start at one and remain contiguous")
        for key in ("name", "age", "sex"):
            clean_cell(item.get(key), nullable=True)
        if item.get("name_source", "shorthand") not in ("shorthand", "clinician-answer"):
            raise ValueError("invalid name source")
        if type(item.get("name_asked", False)) is not bool:
            raise ValueError("invalid name question state")
        if item.get("name_source") == "clinician-answer":
            clean_reply(item.get("clinician_reply"))
            if not item.get("name_asked") or item.get("name") is None:
                raise ValueError("clinician name answer requires a question and a name")
    return items


def decode_record(text: str) -> dict:
    record = object_record(text)
    if type(record.get("version")) is not int or record["version"] != 1:
        raise ValueError("invalid opener record version")
    date.fromisoformat(record["service_date"])
    if record["mode"] not in ("split", "hand", "single"):
        raise ValueError("invalid split mode")
    if record["mode"] == "hand":
        clean_cell(record["reason"])
    population(record["encounters"])
    if (not isinstance(record.get("source"), str) or not record["source"]
            or not isinstance(record.get("source_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", record["source_sha256"])
            or type(record.get("unassigned_end")) is not int):
        raise ValueError("invalid opener source fields")
    for item in record["encounters"]:
        if (any(key not in item for key in ("name", "age", "sex", "name_source", "name_asked"))
                or not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
            raise ValueError("invalid opener item fields")
        if type(item.get("start")) is not int or type(item.get("end")) is not int:
            raise ValueError("invalid source span")
        if item["file"] != f"encounters/encounter-{item['note']}.txt":
            raise ValueError("invalid encounter path")
    return record


def read_openers(run: Path) -> dict:
    record = read_tool_record(run / "openers.json", decode_record)
    if record is None:
        raise ValueError("opener record is missing")
    source = Path(record["source"]).read_bytes()
    if digest(source) != record["source_sha256"]:
        raise ValueError("source changed since opener reading")
    text = source.decode("utf-8")
    cursor = record["unassigned_end"]
    if type(cursor) is not int or not 0 <= cursor <= len(text):
        raise ValueError("invalid unassigned span")
    for item in record["encounters"]:
        if item["start"] != cursor or not cursor < item["end"] <= len(text):
            raise ValueError("source coverage is incomplete")
        expected = text[cursor:item["end"]].encode("utf-8")
        if (run / item["file"]).read_bytes() != expected or digest(expected) != item["sha256"]:
            raise ValueError("encounter changed since opener reading")
        check_name(item, expected.decode("utf-8"))
        cursor = item["end"]
    if cursor != len(text):
        raise ValueError("source coverage is incomplete")
    if (run / "encounters/unassigned.txt").read_bytes() != text[:record["unassigned_end"]].encode("utf-8"):
        raise ValueError("unassigned text changed")
    return record


def check_name(item: dict, text: str) -> None:
    if item.get("name") is not None and item.get("name_source", "shorthand") == "shorthand" and item["name"] not in text:
        raise ValueError("supplied shorthand name is absent from its encounter")


def create(run: Path, source: Path, supplied: Path, service_date: str, mode: str, reason: str | None) -> dict:
    run = private_target(run)
    date.fromisoformat(service_date)
    raw = source.read_bytes()
    text = raw.decode("utf-8")
    if not text.strip():
        raise ValueError("empty source")
    items = population(read_handwritten_record(supplied, "json").require_json(force=True))
    if items is None:
        raise ValueError("supplied opener readings are missing")
    if mode == "split":
        matches = list(NOTE_DELIMITER.finditer(text))
        numbers = [int(re.search(r"\d+", m.group()).group()) for m in matches]
        if not matches or numbers != list(range(1, len(matches) + 1)):
            raise ValueError("broken or absent numbering; supply hand cuts with a reason")
        spans = [(m.start(), matches[i + 1].start() if i + 1 < len(matches) else len(text)) for i, m in enumerate(matches)]
    elif mode == "single":
        if len(items) != 1:
            raise ValueError("single mode needs exactly one encounter")
        spans = [(0, len(text))]
    else:
        clean_cell(reason)
        spans = [(item.get("start"), item.get("end")) for item in items]
    if len(spans) != len(items):
        raise ValueError("opener population differs from source encounter population")
    cursor = spans[0][0]
    if type(cursor) is not int or not 0 <= cursor < len(text):
        raise ValueError("invalid first cut")
    unassigned_end = cursor
    records = []
    for item, (start, end) in zip(items, spans):
        if type(start) is not int or type(end) is not int or start != cursor or not start < end <= len(text):
            raise ValueError("cuts must cover the source without gaps or overlaps")
        body = text[start:end]
        check_name(item, body)
        records.append({**item, "name_source": item.get("name_source", "shorthand"), "name_asked": item.get("name_asked", False),
                        "start": start, "end": end, "file": f"encounters/encounter-{item['note']}.txt", "sha256": digest(body.encode("utf-8"))})
        cursor = end
    if cursor != len(text):
        raise ValueError("cuts dropped source text")
    record = {"version": 1, "mode": mode, "reason": reason, "source": str(source.resolve()), "source_sha256": digest(raw),
              "service_date": service_date, "unassigned_end": unassigned_end, "encounters": records}
    path = private_target(run / "openers.json")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as failure:
        raise UnreadableRecord(path, "could not be opened") from failure
    def change(existing):
        if existing is not None and existing != record:
            # Later missing-name answers may change readings; never silently replace evidence.
            raise ValueError("opener record exists; use the answer command for a missing name")
        try:
            for item in records:
                atomic_write(run / item["file"], text[item["start"]:item["end"]].encode("utf-8"))
            atomic_write(run / "encounters/unassigned.txt", text[:unassigned_end].encode("utf-8"))
        except OSError as failure:
            raise UnreadableRecord(path, "could not be opened") from failure
        return RecordUpdate((json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    update_tool_record(path, decode_record, change)
    return read_openers(run)


def answer(run: Path, note: int, name: str | None, reply: str) -> None:
    private_target(run)
    clean_reply(reply)
    clean_cell(name, nullable=True)
    def change(previous):
        record = read_openers(run)
        item = next((item for item in record["encounters"] if item["note"] == note), None)
        if item is None or item["name"] is not None:
            raise ValueError("answer requires an encounter with an omitted name")
        item.update(name=name, name_source="clinician-answer" if name else "shorthand", name_asked=True, clinician_reply=reply)
        return RecordUpdate((json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    update_tool_record(private_target(run / "openers.json"), decode_record, change)


REFERENCE = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{15}(?![0-9a-fA-F])")


def insert_section(raw: bytes, heading: str, row: str, header: str) -> bytes:
    """Insert bytes at a section end; preserve every existing byte, including CRLF."""
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    marker = re.compile(rb"(?m)^## " + re.escape(heading.encode()) + rb"\r?$")
    found = list(marker.finditer(raw))
    if len(found) > 1:
        raise ValueError("duplicate identity-map section")
    if found:
        following = re.search(rb"(?m)^#{1,2} ", raw[found[0].end():])
        offset = found[0].end() + following.start() if following else len(raw)
        prefix = b"" if not raw[:offset] or raw[:offset].endswith(b"\n") else newline
        return raw[:offset] + prefix + row.encode() + newline + raw[offset:]
    prefix = b"" if not raw or raw.endswith(b"\n") else newline
    block = f"## {heading}\n\n{header}\n{row}\n"
    return raw + prefix + block.replace("\n", newline.decode()).encode()


def append_identity(run: Path, note: int, reference: str, target: Path, collision_file: Path | None) -> None:
    target = private_target(target)
    if not REFERENCE.fullmatch(reference):
        raise ValueError("reference must be 15 hexadecimal characters")
    record = read_openers(run)
    item = next((item for item in record["encounters"] if item["note"] == note), None)
    if item is None:
        raise ValueError("note is not in the opener record")
    if item["name"] is None and not item["name_asked"]:
        raise ValueError("missing name must first be asked at the confirmation stop")
    rulings = {} if collision_file is None else read_handwritten_record(collision_file, "json").require_json(force=True)
    if not isinstance(rulings, dict):
        raise ValueError("collision rulings must map references to reasons")
    for key, value in rulings.items():
        if not REFERENCE.fullmatch(key):
            raise ValueError("invalid collision reference")
        clean_cell(value)
    with artifact_lock.hold(target, "append identity-map row"):
        raw = target.read_bytes() if target.exists() else b""
        text = raw.decode("utf-8")
        if reference.lower() in text.lower():
            raise ValueError("reference already exists in identity map")
        collisions = set()
        for line in text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = [cell.strip().strip("*`_") for cell in line.strip().strip("|").split("|")]
            if item["name"] and any(cell.casefold() == item["name"].casefold() for cell in cells):
                references = REFERENCE.findall(line)
                if not references:
                    raise ValueError("same-name row lacks a valid reference")
                collisions.update(value.lower() for value in references)
        if collisions != {key.lower() for key in rulings}:
            raise ValueError("each same-name row needs exactly one different-person ruling")
        source = clean_cell(Path(record["source"]).name)
        row = f"| {item['name'] or 'Unnamed'} | {reference} | {record['service_date']} | {item['age'] or 'omitted'} | {item['sex'] or 'omitted'} | {source}, note {note} |"
        section = "Newly entered patients" if item["name"] else "Cannot be matched"
        result = insert_section(raw, section, row, "| Name | Patient Reference | Date first seen | Age | Sex | Source |\n| --- | --- | --- | --- | --- | --- |")
        for existing, reason in rulings.items():
            result = insert_section(result, "Collisions", f"| {reference} | {existing} | different person: {reason} |", "| New reference | Existing reference | Ruling |\n| --- | --- | --- |")
        atomic_write(target, result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create_parser = commands.add_parser("record")
    create_parser.add_argument("--run", type=Path, required=True)
    create_parser.add_argument("--source", type=Path, required=True)
    create_parser.add_argument("--readings", type=Path, required=True)
    create_parser.add_argument("--service-date", required=True)
    create_parser.add_argument("--mode", choices=("split", "hand", "single"), default="split")
    create_parser.add_argument("--reason")
    answer_parser = commands.add_parser("answer")
    answer_parser.add_argument("--run", type=Path, required=True)
    answer_parser.add_argument("--note", type=int, required=True)
    answer_parser.add_argument("--name")
    answer_parser.add_argument("--reply", required=True)
    identity = commands.add_parser("identity")
    identity.add_argument("--run", type=Path, required=True)
    identity.add_argument("--note", type=int, required=True)
    identity.add_argument("--reference", required=True)
    identity.add_argument("--map", type=Path, required=True)
    identity.add_argument("--collisions", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            record = create(args.run, args.source, args.readings, args.service_date, args.mode, args.reason)
            print(f"encounters {len(record['encounters'])}")
            print(f"source characters {len(args.source.read_bytes().decode('utf-8'))}")
            for key in ("name", "age", "sex"):
                print(f"openers missing {key} {sum(item[key] is None for item in record['encounters'])}")
            print("unread remainder 0")
        elif args.command == "answer":
            answer(args.run, args.note, args.name, args.reply)
            print("answers recorded 1")
        else:
            append_identity(args.run, args.note, args.reference, args.map, args.collisions)
            print("identity rows added 1")
        return 0
    except DamagedRecord as failure:
        print(damaged_record_result(failure, check="encounter openers", force=True)[1], file=sys.stderr)
        return 1
    except UnreadableRecord as failure:
        print(fault_report(failure, check="encounter openers"), file=sys.stderr)
        print("unread remainder 1")
        return 2
    except (OSError, ValueError, TypeError, KeyError, IndexError):
        print("encounter-openers: refused; invalid, missing, changed, busy, or incomplete evidence", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
