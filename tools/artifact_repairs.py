"""Record placement and compare protected populations through every repair.

Run ``--help`` for the placement, comparison, chain and private REPAIRS routes.
Clinical prose outside the populations remains a reader's decision; see DECLARED_LIMITS.
"""

from __future__ import annotations

import completion_checks
import argparse
import json
import re
import sys
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import note_grammar
import worksheet_grammar as worksheet
from run_grader import EvidenceDisposition
from console_codec import use_utf8, require_python_floor

POPULATIONS = ("worksheet-codes", "entry-status", "differential-items",
               "differential-verdicts", "note-codes")
SECTIONS = ("preamble", "S", "O", "A", "P", "tail", "worksheet")
DECLARED_LIMITS = (
    ("clinical prose outside protected populations",
     "Changed sections are reported for a reader; prose outside the compared populations is not graded.",
     EvidenceDisposition.DECLARED_READING),
    ("recorded scope and portal evidence",
     "Records do not prove the brief authorized the scope or that portal values were copied truthfully.",
     EvidenceDisposition.DECLARED_READING),
)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("record must be an object")
    return payload


def scope_record(payload: dict) -> dict:
    if set(payload) != {"fields", "sections"}:
        raise ValueError("scope requires fields and sections")
    for key, vocabulary in (("fields", POPULATIONS), ("sections", SECTIONS)):
        values = payload[key]
        if not isinstance(values, list) or any(not isinstance(v, str) or v not in vocabulary for v in values):
            raise ValueError(f"unknown scope {key}")
        if len(values) != len(set(values)):
            raise ValueError("duplicate scope member")
    return payload


def populations(text: str, kind: str) -> dict:
    # Imports are deferred because the completion graders call this module.
    import differential_scan
    import anchor_scan

    if kind == "worksheet":
        entries = list(worksheet.ENTRY.finditer(text))
        refused = [("CPT" if m["code"].isdigit() else "ICD-10", m["code"].upper())
                   for m in anchor_scan.REFUSAL_MARK.finditer(text)]
        differential = worksheet.DIFFERENTIAL_HEADING.search(text)
        stop = worksheet.STEP_FOUR_START.search(text)
        differential_entries = [
            (m["system"].upper(), m["code"].upper(), m["descriptor"].strip())
            for m in entries
            if differential and m.start() > differential.start()
            and (stop is None or m.start() < stop.start())
        ]
        return {
            "worksheet-codes": sorted({(m["system"].upper(), m["code"].upper()) for m in entries} | set(refused)),
            "entry-status": sorted((m["system"].upper(), m["code"].upper(),
                                    worksheet.entry_is_for_entry(text, entries, i))
                                   for i, m in enumerate(entries)) + sorted((system, code, False) for system, code in refused),
            "differential-items": differential_entries,
            "differential-verdicts": worksheet.differential_prose(text),
        }
    parsed = differential_scan.read_note(text)
    # Slots are read note-wide, including MDM; a verdict cannot escape by moving
    # from the Differential list to its matching numbered MDM entry.
    verdicts = []
    lines = text.splitlines()
    for entry in parsed.entries:
        if entry.conclusion:
            continue
        begin = entry.line - 1
        end = begin + 1
        while end < len(lines) and lines[end].strip() and not re.match(r"\s*\d+\.\s", lines[end]):
            end += 1
        # Preserve the complete item text rather than guessing a closed clinical
        # verdict vocabulary. This also catches an unknown verdict or its removal.
        verdicts.append((entry.label, entry.code, "\n".join(lines[begin:end])))
    codes = {
        heading: sorted(anchor_scan._section_codes(text, heading)[0])
        for heading in ("preexisting diagnoses", "final diagnosis", "differential")
    }
    codes["refused"] = sorted({m["code"].upper() for m in anchor_scan.NOTE_REFUSAL.finditer(text)})
    codes["procedure"] = sorted({(m["system"].upper(), m["code"].upper()) for m in anchor_scan.RENDERED_PROCEDURE.finditer(text)})
    # Include every parsed slot, not only the labeled note regions.
    codes["slots"] = sorted((entry.code, entry.conclusion) for entry in parsed.entries)
    return {
        "note-codes": codes,
        "differential-items": sorted((entry.label, entry.code) for entry in parsed.entries if not entry.conclusion),
        "differential-verdicts": sorted(verdicts),
    }


def compare(before: Path, after: Path, scope: dict, kind: str) -> dict:
    scope_record(scope)
    if kind not in {"note", "worksheet"}:
        raise ValueError("unknown artifact kind")
    old = before.read_text(encoding="utf-8")
    new = after.read_text(encoding="utf-8")
    left, right = populations(old, kind), populations(new, kind)
    changed = [name for name in left if left[name] != right[name]]
    if kind == "worksheet":
        sections = ["worksheet"] if old != new else []
    else:
        left_sections = note_grammar.parse(old).buckets
        right_sections = note_grammar.parse(new).buckets
        sections = [name for name in left_sections if left_sections[name] != right_sections[name]]
    violations = [name for name in changed if name not in scope["fields"]]
    return {"changed": changed, "violations": violations, "sections": sections,
            "outside_scope": [name for name in sections if name not in scope["sections"]],
            "verdict": "fail" if violations else "pass"}


def ledger_path(run: Path) -> Path:
    return run / "private" / "repairs" / "chain.json"


def ledger(run: Path) -> dict:
    path = ledger_path(run)
    return read_json(path) if path.exists() else {"files": {}}


def write_ledger(run: Path, payload: dict) -> None:
    path = ledger_path(run)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{uuid4().hex}.json")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def place(run: Path, artifact: Path, kind: str) -> None:
    payload = ledger(run)
    key = str(artifact.resolve())
    if key in payload["files"]:
        raise ValueError("placement already recorded; use a repair")
    payload["files"][key] = {"kind": kind, "placement": digest(artifact), "repairs": []}
    write_ledger(run, payload)


def record_repair(run: Path, before: Path, after: Path, scope: dict,
                  rescope: bool = False) -> dict:
    payload = ledger(run)
    record = payload["files"][str(after.resolve())]
    previous = record["repairs"][-1] if record["repairs"] else None
    if rescope:
        # A failed comparison is a recorded declaration that turned out to be
        # narrower than the pass. Re-scoping repeats the identical before and
        # after pair under an equal-or-wider declaration and supersedes the
        # failed record without erasing it; the gate and the REPAIRS block
        # keep both. It never widens backwards: the failed scope is a floor,
        # so the audit story only ever declares more, never less.
        if previous is None or previous["comparison"]["verdict"] == "pass":
            raise ValueError("only a recorded failed comparison can be re-scoped")
        if (digest(before) != previous["before"]
                or digest(after) != previous["after"]):
            raise ValueError("re-scope must repeat the recorded before and after pair")
        scope_record(scope)
        if (set(previous["scope"]["fields"]) - set(scope["fields"])
                or set(previous["scope"]["sections"]) - set(scope["sections"])):
            raise ValueError("re-scope must be equal or wider than the failed scope")
    else:
        expected = previous["after"] if previous else record["placement"]
        if digest(before) != expected:
            raise ValueError("before copy does not end the recorded chain")
    result = compare(before, after, scope, record["kind"])
    retained = ledger_path(run).parent / uuid4().hex
    retained.mkdir()
    (retained / "before.md").write_bytes(before.read_bytes())
    (retained / "after.md").write_bytes(after.read_bytes())
    entry = {"before": digest(before), "after": digest(after),
             "scope": scope, "copies": str(retained.relative_to(run)),
             "comparison": result}
    if rescope:
        entry["supersedes"] = previous["copies"]
    record["repairs"].append(entry)
    write_ledger(run, payload)
    return result


def completion_gate(run: Path, submission: str | None, paths: tuple[Path, ...]) -> tuple[bool, str]:
    frozen = completion_checks.exemption(run, submission, "artifact_repairs", "artifact repairs")
    if frozen is not None:
        return False, frozen
    if submission is None:
        return False, "the repair hash chain: NOT GRADED - --submission was not supplied"
    failures = 0
    try:
        payload = ledger(run)
        if not paths:
            raise ValueError("no final artifacts")
        for path in paths:
            record = payload["files"].get(str(path.resolve()))
            if not record:
                failures += 1
                continue
            expected = record["placement"]
            superseded = {repair["supersedes"] for repair in record["repairs"]
                          if "supersedes" in repair}
            for repair in record["repairs"]:
                copies = (run / repair["copies"]).resolve()
                if not copies.is_relative_to(ledger_path(run).parent.resolve()):
                    raise ValueError("copies outside retained repair directory")
                before, after = copies / "before.md", copies / "after.md"
                measured = compare(before, after, repair["scope"], record["kind"])
                if repair["copies"] in superseded:
                    # A superseded comparison keeps its evidence checked and
                    # visible but no longer grades the verdict or advances the
                    # chain; the record that supersedes it re-links the pair.
                    if (digest(before) != repair["before"]
                            or digest(after) != repair["after"]
                            or measured != repair["comparison"]):
                        failures += 1
                    continue
                if "supersedes" in repair:
                    host = next((prior for prior in record["repairs"]
                                 if prior["copies"] == repair["supersedes"]), None)
                    if (host is None or host["copies"] == repair["copies"]
                            or host.get("before") != repair["before"]
                            or host.get("after") != repair["after"]
                            or host.get("comparison", {}).get("verdict") == "pass"):
                        raise ValueError("re-scope does not supersede the failed pair it names")
                if (repair["before"] != expected or digest(before) != repair["before"]
                        or digest(after) != repair["after"] or measured != repair["comparison"]
                        or measured["verdict"] != "pass"):
                    failures += 1
                expected = repair["after"]
            if digest(path) != expected:
                failures += 1
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        failures += 1
    return bool(failures), f"the repair hash chain: {'finding' if failures else 'clean'} - {failures} broken chain(s)"


def repairs_report(run: Path) -> str:
    lines = ["REPAIRS"]
    for key, record in ledger(run)["files"].items():
        superseded = {repair["supersedes"] for repair in record["repairs"]
                      if "supersedes" in repair}
        for repair in record["repairs"]:
            copies = run / repair["copies"]
            result = compare(copies / "before.md", copies / "after.md", repair["scope"], record["kind"])
            sections = [name + (" (outside scope)" if name in result["outside_scope"] else "") for name in result["sections"]]
            mark = " (superseded by a re-scope)" if repair["copies"] in superseded else ""
            lines.append(f"{Path(key).name} | scope={','.join(repair['scope']['fields'] + repair['scope']['sections']) or 'none'} | {result['verdict']}{mark} | sections={','.join(sections) or 'none'}")
    return "\n".join(lines if len(lines) > 1 else lines + ["none"])


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    placement = commands.add_parser("place")
    placement.add_argument("run", type=Path)
    placement.add_argument("artifact", type=Path)
    placement.add_argument("--kind", choices=("note", "worksheet"), required=True)
    comparison = commands.add_parser("compare")
    comparison.add_argument("run", type=Path)
    comparison.add_argument("--before", type=Path, required=True)
    comparison.add_argument("--after", type=Path, required=True)
    comparison.add_argument("--scope", type=Path, required=True)
    comparison.add_argument("--rescope", action="store_true",
                            help="re-record the last failed pair under an equal-or-wider scope, superseding it")
    comparison.add_argument("--show", action="store_true")
    report = commands.add_parser("report", help="private REPAIRS block for the go-ahead")
    report.add_argument("run", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "place":
            place(args.run, args.artifact, args.kind)
            print("placement recorded: 1")
        elif args.command == "report":
            print(repairs_report(args.run))
        else:
            result = record_repair(args.run, args.before, args.after, scope_record(read_json(args.scope)),
                                   rescope=args.rescope)
            print(f"protected populations changed: {len(result['changed'])}; unnamed changes: {len(result['violations'])}")
            if args.show:
                print(json.dumps(result, indent=2))
            return int(result["verdict"] != "pass")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        print("repair record: unreadable or invalid", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
