"""Grade implementation-map disagreement from a harvest or changed map event.

The harvest is fetched by the caller; this module opens no socket. It checks
the two readiness directions, the reconciliation anchor against committed ADRs,
the map issue's pointer to this module, and its producer stamp. Event mode
grades that same stamp on an edited #596 body. The complete boundary is
``map_scan.DECLARED_LIMITS``; its rows are not copied into this docstring or the
maintainer documentation.
Harvest mode also requires the independent three-surface population manifest
written by ``tracker_population.py`` and refuses a short issues read.

Exit status is 0 clean, 1 refusing findings, and 2 when the scan could not run.
The producer-stamp row is advisory in harvest mode and refusing in changed-map
event mode. When another finding and a not-scanned limb coexist, 1 wins and
both reports print. The ``--advisory`` flag converts only 1 to 0, leaving a
finding-free not-scanned result at 2.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple, Sequence

from console_codec import require_python_floor, use_utf8
import implementation_map
import tracker_scan

CLEAN = 0
FOUND = 1
NOT_SCANNED = 2

STATE_BEGIN = "<!-- implementation-map:v1:state:begin -->"
STATE_END = "<!-- implementation-map:v1:state:end -->"
LIMITS_POINTER = "map_scan.DECLARED_LIMITS"
MAP_ISSUE = implementation_map.MAP_ISSUE


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
        "The live implementation-map helper and this offline grader have duplicate readiness predicates with no mechanical binding; both read only ready_labels from the map state.",
    ),
    DeclaredLimit(
        "blocked-invariant",
        "Neither direction of ADR 0072's blocked-label invariant is certified.",
    ),
    DeclaredLimit(
        "producer-stamp-is-not-a-render",
        "A clean producer-stamp check establishes the declared emitter identity and does not establish that GitHub rendered any derived view.",
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
    stamp_problem = implementation_map.producer_stamp_problem(
        str(map_row.get("body") or "")
    )
    if stamp_problem is not None:
        findings.append(
            Finding(
                "producer-stamp",
                map_number,
                ("-",),
                "-",
                detail=stamp_problem,
            )
        )
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
            adrs = implementation_map.unreconciled_adrs(state, repo_root)
        except implementation_map.MapError as error:
            not_scanned.append(str(error))
        else:
            for adr in adrs:
                findings.append(
                    Finding(
                        "unreconciled-adr",
                        map_number,
                        ("-",),
                        "-",
                        detail=f"ADR {Path(adr).name[:4]} ({adr})",
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


def scan_github_event(path: Path, event_name: str) -> ScanResult:
    """Grade the producer stamp on the one changed issue event body."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ScanError(f"cannot read GitHub event {path}: {error}") from error
    if event_name != "issues":
        raise ScanError(f"producer-stamp event mode does not handle {event_name!r}")
    if not isinstance(payload, dict) or payload.get("action") != "edited":
        raise ScanError("producer-stamp event mode needs one edited issue event")
    row = payload.get("issue")
    if not isinstance(row, dict):
        raise ScanError("edited issue event has no issue object")
    number = row.get("number")
    body = row.get("body")
    if not isinstance(number, int) or not isinstance(body, str):
        raise ScanError("edited issue event needs an integer number and text body")
    if number != MAP_ISSUE:
        return ScanResult((), ())
    problem = implementation_map.producer_stamp_problem(body)
    findings = () if problem is None else (
        Finding("producer-stamp", number, ("-",), "-", detail=problem),
    )
    return ScanResult(findings, ())


def _arguments(argv: Sequence[str]):
    parser = argparse.ArgumentParser(description="Grade an offline issue harvest")
    parser.add_argument("harvest", nargs="?")
    parser.add_argument("--population")
    parser.add_argument("--github-event")
    parser.add_argument("--event-name")
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
    if args is None or (not args.harvest and not args.github_event):
        print("did not scan: name one harvested issues file", file=sys.stderr)
        return NOT_SCANNED
    if args.harvest and args.github_event:
        print("did not scan: choose a harvest or a GitHub event", file=sys.stderr)
        return NOT_SCANNED
    if args.github_event and args.population:
        print("did not scan: --population applies only to a harvest", file=sys.stderr)
        return NOT_SCANNED
    try:
        if args.github_event:
            if not args.event_name:
                raise ScanError("GitHub event mode needs --event-name")
            result = scan_github_event(Path(args.github_event), args.event_name)
        else:
            harvest = Path(args.harvest)
            rows = read_harvest(harvest)
            if not args.population:
                raise ScanError(
                    "DID NOT ESTABLISH the full harvest population -- "
                    "pass --population <tracker-population.json>."
                )
            try:
                manifest_harvest = [
                    harvest.with_name(name)
                    for name in sorted(tracker_scan.FULL_HARVEST_FILES)
                ]
                populations, short = tracker_scan.population_coverage(
                    Path(args.population),
                    manifest_harvest,
                    {"tracker-issues.json": len(rows)},
                )
            except tracker_scan.HarvestError as error:
                raise ScanError(
                    "DID NOT ESTABLISH the full harvest population -- " + str(error)
                ) from error
            population = populations["tracker-issues.json"]
            print(
                f"tracker-issues.json population {population}; unread remainder "
                f"{max(population - len(rows), 0)}; records read {len(rows)}"
            )
            issue_short = [
                item for item in short if item[0] == "tracker-issues.json"
            ]
            if issue_short:
                raise ScanError(
                    "DID NOT ESTABLISH a complete harvest -- "
                    f"{harvest.name}: {len(rows)} of population {population} record(s)."
                )
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
        if args.advisory:
            return CLEAN
        blocking = result.findings if args.github_event else tuple(
            finding
            for finding in result.findings
            if finding.kind != "producer-stamp"
        )
        if blocking:
            return FOUND
        if result.not_scanned:
            return NOT_SCANNED
        return CLEAN
    if result.not_scanned:
        return NOT_SCANNED
    print("clean: no findings")
    return CLEAN


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
