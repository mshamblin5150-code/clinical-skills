"""Record selected office status and fingerprint its private evidence (ADR 0427)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from console_codec import require_python_floor, use_utf8
from encounter_openers import digest, private_target, read_openers
from run_record_reader import (DamagedRecord, damaged_record_result, RecordUpdate, UnreadableRecord, fault_report,
                               object_record, read_tool_record, update_tool_record)

DECLARED_LIMITS = (
    "The operator selects the evidence and status; a fingerprint proves unchanged evidence, not that its words establish earlier care or identify the correct patient.",
    "A pointer records the selected row, portal reading or answer; it is not a semantic parser of that evidence. Clinician answers retain the whole reply and source path for coding_freshness transcript verification.",
    "Writes use the shared locked transaction; evidence and opener files are checked again by the manifest, without a cross-file snapshot guarantee.",
)


def decode_record(text: str) -> dict:
    record = object_record(text)
    if record.get("schema") != 1 or not isinstance(record.get("encounters"), dict):
        raise ValueError("invalid status record")
    for key, item in record["encounters"].items():
        if not key.isdigit() or int(key) < 1 or not isinstance(item, dict):
            raise ValueError("invalid status encounter")
        if item.get("value") not in {"new", "established"} or item.get("evidence") not in {"identity-map", "medatrax", "clinician-answer"}:
            raise ValueError("invalid status fields")
        if any(not isinstance(item.get(k), str) or not item[k].strip() for k in ("evidence_path", "pointer", "evidence_sha256")):
            raise ValueError("missing status evidence")
        if not re.fullmatch(r"[0-9a-f]{64}", item["evidence_sha256"]):
            raise ValueError("invalid evidence fingerprint")
        if item["evidence"] == "clinician-answer" and any(not isinstance(item.get(k), str) or not item[k].strip() for k in ("clinician_reply", "source_path")):
            raise ValueError("missing whole reply or source")
    return record


def status_for(run: Path, note: int) -> dict:
    record = read_tool_record(run / "encounter-status.json", decode_record)
    item = record["encounters"].get(str(note)) if record else None
    if item is None:
        raise ValueError("office encounter has no recorded patient status")
    evidence = Path(item["evidence_path"])
    if digest(evidence.read_bytes()) != item["evidence_sha256"]:
        raise ValueError("patient-status evidence changed")
    return dict(item)


def record_status(run: Path, note: int, value: str, evidence: str,
                  evidence_path: Path, pointer: str, clinician_reply: str | None = None) -> dict:
    run = private_target(run)
    openers = read_openers(run)
    if note not in [item["note"] for item in openers["encounters"]]:
        raise ValueError("status note is outside opener population")
    item = dict(value=value, evidence=evidence, evidence_path=str(evidence_path.resolve()),
                pointer=pointer, evidence_sha256=digest(evidence_path.read_bytes()))
    if evidence == "clinician-answer":
        item.update(clinician_reply=clinician_reply, source_path=openers["source"])
        # The fingerprinted evidence must actually retain the whole answer.
        if not clinician_reply or clinician_reply not in evidence_path.read_text(encoding="utf-8"):
            raise ValueError("whole clinician reply is absent from evidence")
    decode_record(json.dumps({"schema": 1, "encounters": {str(note): item}}))
    def change(previous):
        result = previous or {"schema": 1, "encounters": {}}
        result["encounters"][str(note)] = item
        return RecordUpdate((json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), item)
    return update_tool_record(run / "encounter-status.json", decode_record, change)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--note", type=int, required=True)
    parser.add_argument("--value", choices=("new", "established"), required=True)
    parser.add_argument("--evidence", choices=("identity-map", "medatrax", "clinician-answer"), required=True)
    parser.add_argument("--evidence-path", type=Path, required=True)
    parser.add_argument("--pointer", required=True)
    parser.add_argument("--reply-file", type=Path)
    args = parser.parse_args(argv)
    try:
        reply = args.reply_file.read_text(encoding="utf-8") if args.reply_file else None
        record_status(args.run, args.note, args.value, args.evidence, args.evidence_path, args.pointer, reply)
    except UnreadableRecord as error:
        print(fault_report(error, check="patient status")); return 2
    except DamagedRecord as error:
        print(damaged_record_result(error, check="patient status", force=True)[1]); return 1
    except (OSError, UnicodeError, ValueError):
        print("encounter-status: refused — invalid or unreadable evidence"); return 2
    print("encounter-status: recorded 1 encounter")
    return 0


if __name__ == "__main__":
    use_utf8(); require_python_floor(); raise SystemExit(main())
