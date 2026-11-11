"""Record the whole replies of the clinician to the coding pre-approval questions of a run.

``python tools/preapproval_answers.py RUN --note N --question TEXT [--level CODE ...] --reply TEXT``
adds one keyed entry to ``RUN/pre-approval-answers.json`` through the shared locked
transaction. The reply is matched as a whole clinician message in the run transcript after the
opener source, through ``approval_record.verify_clinician_reply``: a verified reply is recorded
``verified``, an unreadable transcript is recorded ``unreadable``, and a reply no later whole
message matches writes nothing. An identical question and reply already recorded writes nothing,
except that an unreadable entry is upgraded to verified once the transcript matches.

Exit 0 when the entry is recorded or already present; 2 when nothing could be recorded. Output
names the entry id and its reply check and never repeats the question or the reply.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import time

import approval_record
from console_codec import require_python_floor, use_utf8
from encounter_openers import private_target, read_openers
from run_record_reader import RecordUpdate, UnreadableRecord, fault_report, object_record, read_tool_record, update_tool_record

DECLARED_LIMITS = (
    "A verified entry proves its reply was a whole clinician message after the run opened. It "
    "does not prove which question the message answered, or that the question text recorded is "
    "the one he was shown.",
    "An unreadable transcript records the entry as unreadable rather than refusing it, and every "
    "reader of the record shows that state.",
    "Entries only accumulate, through one locked replacement of the JSON file. A correction is a "
    "later entry, and nothing reconciles two entries about one question. The one change in place "
    "upgrades an unreadable entry to verified when the same question and reply are recorded with a "
    "readable transcript; a verified entry is never downgraded.",
    "A delegated run records nothing: a delegate cannot supply the clinician answer, and the "
    "lower level stands.",
)

RECORD = "pre-approval-answers.json"
PRODUCER = "preapproval_answers"
KEYS = frozenset({"id", "note", "question", "levels", "clinician_reply", "verification",
                  "reply_matched_at", "recorded_at"})
IDENTIFIER = re.compile(r"note-[1-9][0-9]*\.q[1-9][0-9]*")
CODE = re.compile(r"[0-9]{5}")
VERIFICATIONS = frozenset({"verified", "unreadable"})


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def decode(text: str) -> dict:
    """The whole record, refused rather than partly read."""
    value = object_record(text)
    if (value.get("schema") != 1 or value.get("producer") != PRODUCER
            or not isinstance(value.get("answers"), list)):
        raise ValueError("invalid pre-approval answers header")
    seen = set()
    for entry in value["answers"]:
        if not isinstance(entry, dict) or set(entry) != KEYS:
            raise ValueError("invalid pre-approval answer fields")
        number = entry["note"]
        if (type(number) is not int or number < 1 or not isinstance(entry["id"], str)
                or not IDENTIFIER.fullmatch(entry["id"]) or not entry["id"].startswith(f"note-{number}.")
                or entry["id"] in seen or not _text(entry["question"]) or not _text(entry["clinician_reply"])
                or not isinstance(entry["levels"], list)
                or not all(isinstance(code, str) and CODE.fullmatch(code) for code in entry["levels"])
                or entry["verification"] not in VERIFICATIONS
                or not isinstance(entry["recorded_at"], (int, float))
                or (entry["verification"] == "verified") != isinstance(entry["reply_matched_at"], (int, float))):
            raise ValueError("invalid pre-approval answer")
        seen.add(entry["id"])
    return value


def read(run: Path) -> dict | None:
    """The record, or None for a run that has none; an unreadable record raises."""
    return read_tool_record(Path(run) / RECORD, decode)


def entries_for(record: dict, note: int) -> list[dict]:
    return [entry for entry in record["answers"] if entry["note"] == note]


def record(run: Path, note: int, question: str, levels: list[str], reply: str, *,
           transcripts=None) -> tuple[str, str]:
    """Add one verified or unreadable-transcript entry; return its id and reply check."""
    run = private_target(Path(run))
    openers = read_openers(run)
    if note not in [item["note"] for item in openers["encounters"]]:
        raise ValueError("note is outside the opener population")
    if not _text(question) or not _text(reply) or not all(CODE.fullmatch(code) for code in levels):
        raise ValueError("a question, a whole reply and five-digit levels are required")
    verification = approval_record.verify_clinician_reply(
        run, reply, (Path(openers["source"]),), transcripts=transcripts)
    if verification.state not in ("verified", "unreadable"):
        raise ValueError("no later whole clinician message matches the reply")
    state = "verified" if verification.state == "verified" else "unreadable"

    def change(previous: dict | None) -> RecordUpdate:
        value = previous or {"schema": 1, "producer": PRODUCER, "answers": []}
        for index, entry in enumerate(value["answers"]):
            same = (entry["note"], entry["question"], entry["clinician_reply"], set(entry["levels"]))
            if same != (note, question, reply, set(levels)):
                continue
            if entry["verification"] == "verified" or state != "verified":
                return RecordUpdate(None, (entry["id"], entry["verification"]))
            # A transcript readable now upgrades the same answer in place; nothing downgrades it.
            upgraded = dict(entry, verification="verified", reply_matched_at=verification.matched_at)
            answers = [*value["answers"][:index], upgraded, *value["answers"][index + 1:]]
            payload = (json.dumps(dict(value, answers=answers), indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            decode(payload.decode("utf-8"))
            return RecordUpdate(payload, (entry["id"], "verified"))
        number = 1 + len(entries_for(value, note))
        entry = {"id": f"note-{note}.q{number}", "note": note, "question": question, "levels": levels,
                 "clinician_reply": reply, "verification": state,
                 "reply_matched_at": verification.matched_at if state == "verified" else None,
                 "recorded_at": time.time()}
        updated = dict(value, answers=[*value["answers"], entry])
        payload = (json.dumps(updated, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        decode(payload.decode("utf-8"))
        return RecordUpdate(payload, (entry["id"], state))

    return update_tool_record(run / RECORD, decode, change)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--note", type=int, required=True, help="one-based note order")
    parser.add_argument("--question", required=True, help="the question exactly as shown to the clinician")
    parser.add_argument("--level", action="append", default=[], help="an E/M level the question names")
    parser.add_argument("--reply", required=True, help="the whole reply of the clinician, verbatim")
    args = parser.parse_args(argv)
    try:
        identifier, state = record(args.run, args.note, args.question, args.level, args.reply)
    except UnreadableRecord as error:
        print(fault_report(error, check="pre-approval answers"))
        return 2
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        print("pre-approval answers: refused - nothing recorded; check the run, note, levels and whole reply")
        return 2
    print(f"pre-approval answers: {identifier} recorded; reply check {state}")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
