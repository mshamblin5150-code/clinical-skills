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
from console_codec import require_python_floor, use_utf8
from repo_root import scratch_root

DECLARED_LIMITS = (
    "Whether the remaining words are clinical vocabulary is not proved by identifier and shape checks.",
    "A search typed without the check and without a live-pull record leaves nothing for the grader to find.",
    "Only site strings in the profile's Site or Sites picklist are recognized as account sites.",
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
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("record line must be an object")
    return rows


def completion_gate(run: Path, submission: str | None) -> tuple[bool, str]:
    if submission is None:
        return False, "Outbound searches: not graded - --submission was not supplied"
    try:
        searches = records(run / SEARCHES)
        pulls = records(run / PULLS)
        passed = {row.get("search_id") for row in searches if row.get("passed") is True and isinstance(row.get("query"), str) and row["query"].strip()}
        missing = sum(not row.get("search_id") or row.get("search_id") not in passed or not row.get("dump_id") for row in pulls)
        if missing:
            return True, f"Outbound searches: finding - {missing} live pull(s) lack a passed search-record line"
        return False, f"Outbound searches: clean - {len(pulls)} live pull(s), {len(searches)} search record(s)"
    except (OSError, UnicodeError, ValueError, TypeError):
        return True, "Outbound searches: finding - private record unreadable"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("check")
    check.add_argument("query")
    check.add_argument("--profile", type=Path, default=scratch_root() / "medatrax-profile.md")
    pull = sub.add_parser("pull")
    pull.add_argument("--dump-id", required=True)
    for command in (check, pull):
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
            if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", args.dump_id):
                raise ValueError("invalid dump id")
            path = args.run / PULLS
            row = {"search_id": args.search_id, "dump_id": args.dump_id}
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        print("Outbound search: recorded pass" if args.action == "check" else "UpToDate live pull: recorded")
        return 0
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        reason = str(error) if type(error) is ValueError else "required private input or record unreadable"
        print(f"outbound-search: refused - {reason}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    require_python_floor()
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
