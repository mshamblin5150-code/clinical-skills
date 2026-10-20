"""Check an encounter search before typing it into UpToDate (ADR 0347).

``check <query> --run <directory> --search-id <id>`` writes only passed searches.
``pull --run <directory> --search-id <id> --dump-id <id>`` records a live pull.
Exit 0 is a recorded pass; exit 2 refuses without recording the requested action.
Private record contents and refused queries are never printed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import phi_scan
import completion_checks
from console_codec import require_python_floor, use_utf8
from repo_root import scratch_path, scratch_root
from run_record_reader import read_tool_record, UnreadableRecord

DECLARED_LIMITS = (
    'outbound_search record reads use the shared decoder boundary; damaged bookkeeping leaves its dependent checks not graded and contributes one record per command to coverage. Absence preserves the existing caller meaning.',
    "Whether the remaining words are clinical vocabulary is not proved by identifier and shape checks.",
    "A search typed without the check and without a live-pull record leaves nothing for the grader to find.",
    "Only site strings in the profile's Site or Sites picklist are recognized as account sites.",
    "Whether a recorded difference is clinically accurate remains a reader's judgment.",
)

SEARCHES = "outbound-searches.jsonl"
PULLS = "uptodate-pulls.jsonl"
POPULATION = re.compile(r"\b(?:older\s+adult|adult|child|infant|adolescent|pregnancy)\b", re.I)
SEX = re.compile(r"\b(?:male|female)\b", re.I)
DATE_WORD = re.compile(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b", re.I)


def site_strings(profile: Path) -> tuple[str, ...]:
    text = profile.read_text(encoding="utf-8")
    blocks = re.findall(r"(?im)^\*\*(?:Location\s*/\s*)?Sites?\*\*[^\n]*\n\s*```[^\n]*\n(.*?)\n```", text, re.S)
    sites = tuple(line.strip() for block in blocks for line in block.splitlines() if line.strip())
    if not sites:
        raise ValueError("profile Site picklist is unread; check was not run")
    return sites


def _contains(query: str, literal: str) -> bool:
    query = " ".join(query.split())
    literal = " ".join(literal.split())
    return bool(re.search(r"(?<!\w)" + re.escape(literal) + r"(?!\w)", query, re.I))


def refusal(query: str, profile: Path) -> str | None:
    if not query.strip() or "\n" in query or "\r" in query:
        return "search must be one nonempty line"
    if any(character.isdigit() for character in query):
        return "digits are refused"
    # ADR 0415 ruling 6 widens these shared patterns to digit boundaries,
    # including T-joined dates. This pretyping refusal inherits that boundary.
    if DATE_WORD.search(query) or any(pattern.search(query) for pattern in (phi_scan.NUMERIC_CORPUS_DATE, phi_scan.ISO_CORPUS_DATE, phi_scan.WRITTEN_CORPUS_DATE)):
        return "date shapes are refused"
    if phi_scan.missing_corpus_sources():
        return "PHI corpus is unread; check was not run"
    names, dates = phi_scan.corpus_identifiers()
    if any(_contains(query, literal) for literal in names | dates if literal.strip()):
        return "corpus identifier is refused"
    if any(_contains(query, site.rstrip(".")) for site in site_strings(profile)):
        return "account site is refused"
    if len(POPULATION.findall(query)) > 1 or len(SEX.findall(query)) > 1:
        return "second population or sex word is refused"
    return None


def records(path: Path) -> list[dict]:
    def decode(text: str) -> list[dict]:
        from run_record_reader import object_record
        rows = []
        for number, line in enumerate(text.splitlines(), 1):
            if line.strip():
                try:
                    rows.append(object_record(line))
                except json.JSONDecodeError as failure:
                    raise UnreadableRecord(path, f"does not decode at line {number} column {failure.colno}") from failure
        if any(not isinstance(row, dict) for row in rows):
            raise ValueError("record line must be an object")
        for row in rows:
            if not isinstance(row.get("search_id"), str) or re.fullmatch(r"[a-z0-9][a-z0-9._-]*", row["search_id"]) is None:
                raise ValueError("record needs a search id")
            if path.name == SEARCHES:
                if row.get("passed") is not True or not isinstance(row.get("query"), str) or not row["query"].strip():
                    raise ValueError("search record needs a passed query")
            elif not valid_outcome(row):
                raise ValueError("pull record needs a complete outcome")
        return rows
    return read_tool_record(path, decode) or []


def private_line(value: str) -> str:
    """Allow numeric clinical differences, but refuse corpus identifiers/dates."""
    if not value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("detail must be one nonempty line without control characters")
    if phi_scan.missing_corpus_sources():
        raise ValueError("PHI corpus is unread; check was not run")
    names, dates = phi_scan.corpus_identifiers()
    if any(_contains(value, literal) for literal in names | dates if literal.strip()):
        raise ValueError("corpus identifier is refused")
    if any(pattern.search(value) for pattern in (phi_scan.NUMERIC_CORPUS_DATE, phi_scan.ISO_CORPUS_DATE, phi_scan.WRITTEN_CORPUS_DATE)):
        raise ValueError("date literal is refused")
    return value


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str]:
    exempt = completion_checks.exemption(run, submission, "outbound_search", "Outbound searches")
    if exempt is not None:
        return False, exempt
    if submission is None:
        return False, "Outbound searches: not graded - --submission was not supplied"
    try:
        searches = records(run / SEARCHES)
        pulls = records(run / PULLS)
        passed = {row.get("search_id") for row in searches if row.get("passed") is True and isinstance(row.get("query"), str) and row["query"].strip()}
        missing = sum(not row.get("search_id") or row.get("search_id") not in passed or not valid_outcome(row) for row in pulls)
        if missing:
            return True, f"Outbound searches: finding - {missing} live pull(s) lack a passed search-record line"
        unfinished = passed - {row.get("search_id") for row in pulls}
        if unfinished:
            return True, f"Outbound searches: finding - {len(unfinished)} passed search(es) have no recorded outcome"
        failed = sum(row.get("outcome") == "failed" for row in pulls)
        mismatched = sum(row.get("outcome") == "mismatched" for row in pulls)
        live = len(pulls) - failed - mismatched
        report = f"Outbound searches: clean - {live} live pull(s), {len(searches)} search record(s)"
        if failed or mismatched:
            report += f", {failed} failed pull(s), {mismatched} mismatched search(es)"
        return False, report
    except UnreadableRecord as failure:
        from run_record_reader import collecting_errors, fault_report
        if not collecting_errors():
            raise
        return False, fault_report(failure, check="Outbound searches")
    except (OSError, UnicodeError, ValueError, TypeError):
        return False, "Outbound searches: unreadable - private record could not be read"


def valid_outcome(row: dict) -> bool:
    outcome = row.get("outcome", "live")
    if outcome == "live":
        return isinstance(row.get("dump_id"), str) and bool(row["dump_id"].strip())
    if outcome == "failed":
        return all(isinstance(row.get(key), str) and bool(row[key].strip()) for key in ("decision", "instrument"))
    if outcome == "mismatched":
        return (isinstance(row.get("query_readback"), str) and bool(row["query_readback"].strip())
                and type(row.get("sent_query_passed")) is bool)
    return False


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("check")
    check.add_argument("query")
    check.add_argument("--profile", type=Path, default=scratch_path(scratch_root(), "medatrax-profile.md"))
    pull = sub.add_parser("pull")
    pull.add_argument("--dump-id", required=True)
    pull.add_argument("--sheet")
    pull.add_argument("--row")
    pull.add_argument("--difference")
    pull.add_argument("--sheet-kept", action="store_true")
    failed = sub.add_parser("failed-pull")
    failed.add_argument("--decision", required=True)
    failed.add_argument("--instrument", required=True)
    for command in (check, pull, failed):
        command.add_argument("--run", type=Path, required=True)
        command.add_argument("--search-id", required=True)
    try:
        args = parser.parse_args(argv)
        if not args.run.is_dir():
            raise ValueError("run directory does not exist")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", args.search_id):
            raise ValueError("search id needs lowercase letters, numbers, dot, underscore, or hyphen")
        if args.action == "check":
            reason = refusal(args.query, args.profile)
            if reason:
                raise ValueError(reason)
            if any(row.get("search_id") == args.search_id for row in records(args.run / SEARCHES)):
                raise ValueError("search id already recorded; use a new id")
            path = args.run / SEARCHES
            row = {"search_id": args.search_id, "query": args.query, "passed": True}
        else:
            if not any(row.get("search_id") == args.search_id and row.get("passed") is True for row in records(args.run / SEARCHES)):
                raise ValueError("live pull has no passed search-record line")
            path = args.run / PULLS
            records(path)  # Refuse an unreadable existing log before appending.
            if args.action == "failed-pull":
                row = {"search_id": args.search_id, "outcome": "failed",
                       "decision": private_line(args.decision), "instrument": private_line(args.instrument)}
            else:
                if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", args.dump_id):
                    raise ValueError("invalid dump id")
                row = {"search_id": args.search_id, "dump_id": args.dump_id}
                if any((args.sheet, args.row, args.difference, args.sheet_kept)):
                    if not all((args.sheet, args.row, args.difference)):
                        raise ValueError("conflict needs sheet, row, and difference")
                    sheet = args.sheet.removeprefix("thresholds/").removesuffix(".md")
                    if not re.fullmatch(r"[a-z0-9-]+", sheet):
                        raise ValueError("invalid threshold sheet")
                    row.update(sheet=sheet, row=private_line(args.row),
                               difference=private_line(args.difference), sheet_kept=args.sheet_kept)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        print("Outbound search: recorded pass" if args.action == "check" else "UpToDate pull outcome: recorded")
        return 0
    except UnreadableRecord as error:
        from run_record_reader import fault_report
        print(fault_report(error, check="Outbound searches"), file=sys.stderr)
        print("unread remainder 1")
        return 2
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        reason = str(error) if type(error) in (ValueError, UnreadableRecord) else "required private input or record unreadable"
        print(f"outbound-search: refused - {reason}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
