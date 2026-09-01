"""Grade implementation-map disagreement from one offline issue harvest.

The harvest is fetched by the caller; this module opens no socket. It checks
the two readiness directions, the reconciliation anchor against committed ADRs,
and the map issue's pointer to this module. The complete boundary is
``map_scan.DECLARED_LIMITS``; its rows are not copied into this docstring or
the maintainer documentation.

Exit status is 0 clean, 1 findings, and 2 when the scan could not run. When a
finding and a not-scanned limb coexist, 1 wins and both reports print. The
``--advisory`` flag converts only 1 to 0, leaving 2 unchanged.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Sequence

from console_codec import use_utf8

CLEAN = 0
FOUND = 1
NOT_SCANNED = 2

STATE_BEGIN = "<!-- implementation-map:v1:state:begin -->"
STATE_END = "<!-- implementation-map:v1:state:end -->"
LIMITS_POINTER = "map_scan.DECLARED_LIMITS"
MAP_ISSUE = 596


class DeclaredLimit(NamedTuple):
    key: str
    limit: str


DECLARED_LIMITS = (
    DeclaredLimit(
        "edge-agreement",
        "Native and declared HARD-edge agreement is not graded.",
    ),
    DeclaredLimit(
        "gate-targets",
        "External-gate targets and whether they have cleared are not graded.",
    ),
    DeclaredLimit(
        "packet-status",
        "Packet status is not recomputed or certified.",
    ),
    DeclaredLimit(
        "frontiers",
        "Rendered or actual implementation frontiers are not graded.",
    ),
    DeclaredLimit(
        "readiness-predicate-binding",
        "The out-of-tree helper has a duplicate readiness predicate with no binding to this module; both read only ready_labels from the map state.",
    ),
    DeclaredLimit(
        "blocked-invariant",
        "Neither direction of ADR 0072's blocked-label invariant is certified.",
    ),
)


class Finding(NamedTuple):
    kind: str
    ticket: int
    labels: tuple[str, ...]
    packet: str
    detail: str = ""


class ScanResult(NamedTuple):
    findings: tuple[Finding, ...]
    not_scanned: tuple[str, ...]


class ScanError(Exception):
    """A malformed input that prevents every row from being graded."""


def _decode_arrays(text: str) -> list[dict]:
    """Decode the concatenated JSON arrays emitted by ``gh --paginate``."""
    decoder = json.JSONDecoder()
    rows: list[dict] = []
    index = 0
    saw_payload = False
    while index < len(text):
        while index < len(text) and text[index] in " \r\n\t":
            index += 1
        if index >= len(text):
            break
        try:
            payload, index = decoder.raw_decode(text, index)
        except json.JSONDecodeError as error:
            raise ScanError(f"harvest is not parseable JSON: {error}") from error
        saw_payload = True
        if not isinstance(payload, list):
            raise ScanError("harvest payload is not a JSON list")
        if not all(isinstance(row, dict) for row in payload):
            raise ScanError("harvest holds a non-object issue row")
        rows.extend(payload)
    if not saw_payload or not rows:
        raise ScanError("harvest contains no issue records")
    return rows


def read_harvest(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        raise ScanError(f"cannot read harvest {path}: {error}") from error
    return _decode_arrays(text)


def _state_segment(body: str) -> tuple[str, str]:
    begins = body.count(STATE_BEGIN)
    ends = body.count(STATE_END)
    if begins != 1 or ends != 1:
        raise ScanError(
            f"map state markers are not unique: {begins} begin, {ends} end"
        )
    start = body.index(STATE_BEGIN)
    finish = body.index(STATE_END)
    if finish < start:
        raise ScanError("map state end marker precedes its begin marker")
    outside = body[:start] + body[finish + len(STATE_END):]
    return body[start + len(STATE_BEGIN):finish], outside


def extract_state(body: str) -> tuple[dict, str]:
    segment, outside = _state_segment(body)
    fence = re.search(r"```json\s*\n(.*?)\n```", segment, re.DOTALL)
    if fence is None:
        raise ScanError("map state block holds no JSON fence")
    try:
        value = json.loads(fence.group(1))
    except json.JSONDecodeError as error:
        raise ScanError(f"map state is not parseable JSON: {error}") from error
    if not isinstance(value, dict):
        raise ScanError("map state is not an object")
    if value.get("schema") != 1:
        raise ScanError(f"map state schema {value.get('schema')!r} is not 1")
    for key in ("packets", "exclusions", "ready_labels"):
        if not isinstance(value.get(key), list):
            raise ScanError(f"map state {key} is not a list")
    for packet in value["packets"]:
        if not isinstance(packet, dict):
            raise ScanError("map state holds a non-object packet")
        if not isinstance(packet.get("id"), str) or not isinstance(
            packet.get("tickets"), list
        ):
            raise ScanError("map packet needs a string id and a tickets list")
        if not all(isinstance(ticket, int) for ticket in packet["tickets"]):
            raise ScanError(f"packet {packet.get('id')} holds a non-integer ticket")
    return value, outside


def _label_names(row: dict) -> tuple[str, ...]:
    names: list[str] = []
    for label in row.get("labels", []):
        if isinstance(label, dict) and isinstance(label.get("name"), str):
            names.append(label["name"])
        elif isinstance(label, str):
            names.append(label)
    return tuple(sorted(set(names)))


def _git_log_after(anchor: str, repo_root: Path) -> tuple[str, ...]:
    process = subprocess.run(
        ["git", "log", "--format=%H", f"{anchor}..HEAD", "--", "docs/adr/"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if process.returncode != 0:
        reason = process.stderr.strip().splitlines()
        suffix = f": {reason[0][:200]}" if reason else ""
        raise ScanError(f"git log could not compare reconciled_through{suffix}")
    return tuple(line for line in process.stdout.splitlines() if line.strip())


def scan(rows: Sequence[dict], repo_root: Path) -> ScanResult:
    maps = [row for row in rows if STATE_BEGIN in str(row.get("body") or "")]
    if len(maps) != 1:
        raise ScanError(f"expected one implementation map issue; found {len(maps)}")
    map_row = maps[0]
    map_number = map_row.get("number")
    if not isinstance(map_number, int):
        raise ScanError("map issue has no integer ticket number")
    if map_number != MAP_ISSUE:
        raise ScanError(
            f"implementation map state is on ticket #{map_number}, not #{MAP_ISSUE}"
        )
    state, prose = extract_state(str(map_row.get("body") or ""))

    ready_labels = tuple(
        label for label in state["ready_labels"] if isinstance(label, str)
    )
    if not ready_labels or len(ready_labels) != len(state["ready_labels"]):
        raise ScanError("map state ready_labels is empty or malformed")

    membership: dict[int, str] = {}
    for packet in state["packets"]:
        for ticket in packet["tickets"]:
            if ticket in membership:
                raise ScanError(f"ticket #{ticket} belongs to more than one packet")
            membership[ticket] = packet["id"]
    excluded = {
        row.get("ticket")
        for row in state["exclusions"]
        if isinstance(row, dict) and isinstance(row.get("ticket"), int)
    }

    findings: list[Finding] = []
    issue_rows = {
        row.get("number"): row
        for row in rows
        if isinstance(row.get("number"), int) and "pull_request" not in row
    }
    ready_set = set(ready_labels)
    for number, row in sorted(issue_rows.items()):
        if str(row.get("state", "open")).lower() != "open":
            continue
        labels = set(_label_names(row))
        actual_ready = tuple(sorted(labels & ready_set))
        if actual_ready and number not in membership and number not in excluded:
            findings.append(
                Finding("unmapped-ready", number, actual_ready, "-")
            )
    for ticket, packet_id in sorted(membership.items()):
        row = issue_rows.get(ticket)
        if row is None or str(row.get("state", "open")).lower() != "open":
            continue
        if not (set(_label_names(row)) & ready_set):
            findings.append(
                Finding("mapped-not-ready", ticket, ready_labels, packet_id)
            )

    maintenance = prose.partition("## Maintenance rule")[2].partition("\n## ")[0]
    if (
        "`tools/map_scan.py`" not in maintenance
        or f"`{LIMITS_POINTER}`" not in maintenance
    ):
        findings.append(
            Finding("missing-limits-pointer", map_number, ("-",), "-")
        )

    not_scanned: list[str] = []
    anchor = state.get("reconciled_through")
    if not isinstance(anchor, str) or not anchor.strip():
        not_scanned.append("map state carries no reconciled_through commit")
    else:
        try:
            commits = _git_log_after(anchor, repo_root)
        except ScanError as error:
            not_scanned.append(str(error))
        else:
            if commits:
                findings.append(
                    Finding(
                        "unreconciled-adr",
                        map_number,
                        ("-",),
                        "-",
                        detail=f"commits {len(commits)}",
                    )
                )
    return ScanResult(tuple(findings), tuple(not_scanned))


def format_finding(finding: Finding) -> str:
    labels = ",".join(finding.labels)
    suffix = f" {finding.detail}" if finding.detail else ""
    return (
        f"FINDING {finding.kind}: ticket #{finding.ticket} "
        f"labels [{labels}] packet {finding.packet}{suffix}"
    )


def _arguments(argv: Sequence[str]):
    parser = argparse.ArgumentParser(description="Grade an offline issue harvest")
    parser.add_argument("harvest", nargs="?")
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="print findings but convert exit 1 to exit 0",
    )
    try:
        return parser.parse_args(argv)
    except SystemExit as error:
        if error.code == 0:
            raise
        return None


def main(argv: Sequence[str], *, repo_root: Path | None = None) -> int:
    args = _arguments(argv)
    if args is None or not args.harvest:
        print("did not scan: name one harvested issues file", file=sys.stderr)
        return NOT_SCANNED
    try:
        rows = read_harvest(Path(args.harvest))
        result = scan(rows, repo_root or Path.cwd())
    except ScanError as error:
        print(f"did not scan: {error}", file=sys.stderr)
        return NOT_SCANNED

    for finding in result.findings:
        print(format_finding(finding))
    for reason in result.not_scanned:
        print(f"did not scan: {reason}", file=sys.stderr)

    if result.findings:
        print(f"{len(result.findings)} finding(s)")
        return CLEAN if args.advisory else FOUND
    if result.not_scanned:
        return NOT_SCANNED
    print("clean: no findings")
    return CLEAN


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
