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
PRODUCER_STAMP_RULE = "producer-stamp"
EVENT_RULES = (PRODUCER_STAMP_RULE,)

# Derived by map_scan.scan from the complete harvest at the freeze commit.
GRANDFATHERED_FREEZE_COMMIT = '723eea1851c7a62b805251399683a416e48cc5a4'
GRANDFATHERED_ADRS = (
    'docs/adr/0039-a-legal-reference-entry-keys-on-both-its-name-and-its-section-and-a-narrative-citation-is-read-against-the-reference-set.md',
    'docs/adr/0088-a-legal-reference-is-read-by-its-section-and-never-refused-for-its-name-and-the-sheet-s-authority-is-apa-s-own-page.md',
    'docs/adr/0099-a-control-character-in-a-published-tracker-body-is-refused-at-the-publish-event-and-graded-at-every-one.md',
    'docs/adr/0105-the-branch-scope-vocabulary-gains-a-verified-on-main-sentence-and-the-in-flight-label-is-discharged-at-merge.md',
    'docs/adr/0128-a-read-once-cache-of-a-committed-reference-file-gets-a-public-reset-and-a-declared-limit-and-the-pattern-is-not-generalized.md',
    'docs/adr/0137-a-partial-body-file-path-resolves-against-the-folder-the-command-names.md',
    'docs/adr/0141-a-collapsed-escape-is-repaired-by-mechanical-inverse-and-the-residual-red-needs-no-register.md',
    'docs/adr/0145-the-republished-date-element-is-shared-grammar-keyed-on-its-second-element.md',
    'docs/adr/0153-a-sourceless-record-claims-no-source-and-a-certifier-reads-the-status.md',
    'docs/adr/0155-the-map-render-stamps-its-producer-and-the-graph-draws-only-what-carries-an-edge.md',
    'docs/adr/0159-the-sheet-grammar-leaves-as-a-pure-module-and-gate-results-split-per-gate.md',
    'docs/adr/0166-codebase-architecture-marks-a-lineage-by-descent.md',
    'docs/adr/0168-a-map-obligation-belongs-to-whoever-incurred-it-and-the-producer-stamp-hashes-the-emitter.md',
    'docs/adr/0169-a-ticket-states-what-filed-it-on-an-append-only-line.md',
    'docs/adr/0170-every-grader-declares-the-posture-its-empty-population-takes.md',
    'docs/adr/0177-both-publish-routes-grade-a-body-through-one-grader-and-a-lost-body-refuses.md',
    'docs/adr/0179-a-body-file-absent-when-the-hook-ran-is-one-condition-and-its-remedy-names-both-causes.md',
    'docs/adr/0181-a-day-file-reaches-the-corpus-through-one-command-and-a-rendered-page-waits-for-a-reading.md',
    'docs/adr/0187-the-python-floor-is-two-numbers-held-equal-and-a-job-on-the-floor-settles-it.md',
    'docs/adr/0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md',
    'docs/adr/0189-a-coordinate-is-never-the-locator-and-its-anchor-is-graded-at-publication.md',
    'docs/adr/0192-a-ceiling-names-a-relationship-and-a-count-sits-beside-what-it-counts.md',
    'docs/adr/0196-a-published-figure-names-its-population-and-is-re-derived-at-publication.md',
    'docs/adr/0211-an-uptodate-entry-is-checked-against-its-masthead-and-a-sourced-record-is-cited-or-dropped.md',
    'docs/adr/0213-a-prescription-pad-is-held-on-one-page-by-keep-with-next-and-cantsplit-does-not-do-it.md',
    'docs/adr/0216-a-pre-grade-grades-the-exact-publication-command-and-the-aar-quotation-gate-runs-on-it.md',
    'docs/adr/0217-an-absence-based-refutation-quotes-the-record-s-passage.md',
    'docs/adr/0218-a-slide-s-agreement-with-its-record-is-read-and-every-deck-number-is-traced.md',
    'docs/adr/0222-extract-entries-are-named-by-their-transcript-and-a-review-reads-every-sitting-by-scan-rather-than-by-pointer.md',
    'docs/adr/0224-the-map-s-views-refresh-hourly-and-a-stale-view-is-reported-rather-than-failed.md',
    'docs/adr/0225-a-refused-reference-label-voids-only-its-declared-kinds-and-a-partial-gate-keeps-what-it-read.md',
    'docs/adr/0226-a-non-member-s-empty-read-is-ruled-against-its-own-contract.md',
    'docs/adr/0227-deck-scan-reads-what-the-slide-face-draws.md',
    'docs/adr/0228-the-filed-from-line-sits-one-blank-line-below-the-whole-scope-block.md',
    'docs/adr/0229-a-grader-refuses-a-second-source-and-the-option-to-accept-one-is-deleted.md',
    'docs/adr/0230-a-measured-partial-read-prints-an-admissible-unread-remainder-that-exits-not-scanned-and-is-declared-only-where-no-candidate-count-is-admissible.md',
    'docs/adr/0231-an-unreproduced-publication-is-refused-unread-and-every-gh-command-reaches-the-hook.md',
    'docs/adr/0232-every-skill-command-is-named-in-agents-md-and-its-tier-is-what-skipping-it-costs.md',
    'docs/adr/0233-a-graphql-read-is-judged-by-its-payload-and-every-complaint-must-be-a-declared-absence.md',
    'docs/adr/0234-a-gh-api-call-is-graded-left-alone-or-refused-as-unclassified.md',
    'docs/adr/0235-a-browser-tab-is-a-private-output-location-and-a-page-action-naming-none-is-refused.md',
    'docs/adr/0236-a-peer-scratch-root-is-described-by-its-files-alone-and-no-vocabulary-is-applied-to-it.md',
    'docs/adr/0237-a-missing-worktree-git-reports-as-locked-is-a-locked-registration-and-the-prune-remedy-is-qualified.md',
    'docs/adr/0238-a-worktree-is-removed-only-after-the-census-holds-nothing-back.md',
    'docs/adr/0239-a-tracker-record-cannot-declare-its-own-phi-exemption.md',
    'docs/adr/0240-the-map-s-direct-writer-grades-through-analyze-and-runs-no-readback.md',
    'docs/adr/0241-a-merge-receipt-is-graded-before-it-posts-and-a-workflow-token-write-is-an-unwatched-write.md',
    'docs/adr/0242-the-hook-and-the-workflow-are-bound-by-a-declared-correspondence.md',
    'docs/adr/0244-an-unquoted-backslash-path-is-not-refused.md',
    'docs/adr/0245-the-tracker-workflow-grades-the-title-that-changed-and-a-label-removal-starts-no-run.md',
    'docs/adr/0250-a-review-sheet-carries-final-coding-only-after-the-batch-is-fresh.md',
    'docs/adr/0253-a-guideline-verdict-takes-one-wording-and-a-near-miss-is-a-finding.md',
    'docs/adr/0254-the-note-entered-in-medatrax-is-a-derived-entry-copy-and-its-plan-takes-four-labels.md',
    'docs/adr/0257-reference-scan-reads-a-draft-in-nfc-and-declares-a-mark-with-no-composed-form.md',
    'docs/adr/0258-descriptor-agreement-grades-an-authored-anchor-on-every-role.md',
    'docs/adr/0259-the-form-sections-are-derived-evidence-and-the-agreement-record-composes-per-note.md',
    'docs/adr/0262-the-adversarial-read-moves-after-the-render-and-its-record-names-the-pass-and-the-ledger-it-read.md',
    'docs/adr/0263-reference-scan-resolves-a-no-surname-entry-by-title-proper-prefix-and-reads-apa-8-21-group-abbreviations-through-one-shared-recognizer.md',
    'docs/adr/0264-the-opaque-container-fallback-matches-only-when-its-stripped-element-equals-the-other-side-s-container.md',
    'docs/adr/0266-the-first-name-form-resolves-on-the-first-initial-and-is-built-in-both-citation-readers.md',
    'docs/adr/0268-a-ceiling-carries-its-reason-beside-itself-and-the-ruling-that-sets-a-value-may-state-it.md',
    'docs/adr/0270-the-canonical-voice-model-is-resolved-by-one-owner-and-identity-is-the-graded-row.md',
)
GRANDFATHERED_TICKETS = (1348,)


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
    grandfathered: tuple[Finding, ...] = ()
    landing: tuple[Finding, ...] = ()
    discharged: tuple[str, ...] = ()


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


def landing_commits(pushed_range: str, repo_root: Path) -> set[str]:
    """Resolve both endpoints before reading a first-parent push range."""
    endpoints = pushed_range.split("..")
    if len(endpoints) != 2 or any(not ref or ref.startswith("-") for ref in endpoints):
        raise implementation_map.MapError("pushed range needs before..after")
    resolved = [
        implementation_map._git_text(
            repo_root, ["rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
            "could not resolve pushed range",
        ).strip()
        for ref in endpoints
    ]
    return set(implementation_map._git_text(
        repo_root, ["rev-list", "--first-parent", f"{resolved[0]}..{resolved[1]}"],
        "could not read pushed range",
    ).splitlines())


def scan(rows: Sequence[dict], repo_root: Path, pushed_range: str | None = None) -> ScanResult:
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
                PRODUCER_STAMP_RULE,
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
    landed: set[str] = set()
    if pushed_range is not None:
        try:
            landed = landing_commits(pushed_range, repo_root)
        except implementation_map.MapError as error:
            not_scanned.append(str(error))
    grandfathered: list[Finding] = []
    landing: list[Finding] = []
    discharged: list[str] = []
    owed_tickets = {f.ticket for f in findings if f.kind == "unmapped-ready"}
    grandfathered.extend(
        f for f in findings
        if f.kind == "unmapped-ready" and f.ticket in GRANDFATHERED_TICKETS
    )
    discharged.extend(
        f"ticket #{ticket}" for ticket in GRANDFATHERED_TICKETS if ticket not in owed_tickets
    )
    anchor = state.get("reconciled_through")
    if not isinstance(anchor, str) or not anchor.strip():
        not_scanned.append("map state carries no reconciled_through commit")
    else:
        try:
            adrs = implementation_map.unreconciled_adrs(state, repo_root)
        except implementation_map.MapError as error:
            not_scanned.append(str(error))
        else:
            # Latest triggering first-parent commit dominates an earlier debt
            # on the same path, including a correction after the freeze.
            triggers = {}
            frozen_ancestors: set[str] = set()
            try:
                if adrs:
                    triggers = {
                        path: commit
                        for commit, paths in implementation_map.adr_commits_after(anchor, repo_root)
                        for path in paths
                    }
                if set(adrs) & set(GRANDFATHERED_ADRS):
                    frozen_ancestors = set(implementation_map._git_text(
                        repo_root, ["rev-list", GRANDFATHERED_FREEZE_COMMIT],
                        "could not read grandfathered freeze commit",
                    ).splitlines())
            except implementation_map.MapError as error:
                not_scanned.append(str(error))
            discharged.extend(path for path in GRANDFATHERED_ADRS if path not in adrs)
            for adr in adrs:
                finding = Finding(
                    "unreconciled-adr",
                    map_number,
                    ("-",),
                    "-",
                    detail=f"ADR {Path(adr).name[:4]} ({adr})",
                )
                findings.append(finding)
                trigger = triggers.get(adr)
                if adr in GRANDFATHERED_ADRS and trigger in frozen_ancestors:
                    grandfathered.append(finding)
                elif trigger in landed:
                    landing.append(finding)
    return ScanResult(
        tuple(findings), tuple(not_scanned), tuple(grandfathered),
        tuple(landing), tuple(discharged),
    )


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
        Finding(PRODUCER_STAMP_RULE, number, ("-",), "-", detail=problem),
    )
    return ScanResult(findings, ())


def _arguments(argv: Sequence[str]):
    parser = argparse.ArgumentParser(description="Grade an offline issue harvest")
    parser.add_argument("harvest", nargs="?")
    parser.add_argument("--population")
    parser.add_argument("--github-event")
    parser.add_argument("--event-name")
    parser.add_argument("--pushed-range", help="push event's before..after commit range")
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
    try:
        return _main(argv, repo_root=repo_root)
    except ScanError as error:
        print(f"did not scan: {error}", file=sys.stderr)
        report_counts(ScanResult((), ()), False)
        return NOT_SCANNED


def refusing_findings(result: ScanResult, event: bool) -> tuple[Finding, ...]:
    return tuple(
        finding for finding in result.findings
        if finding not in result.grandfathered and finding not in result.landing
        and (event or finding.kind != PRODUCER_STAMP_RULE)
    )


def report_counts(result: ScanResult, event: bool) -> None:
    print(
        f"grandfathered: {len(result.grandfathered)}; "
        f"owed by this merge: {len(result.landing)}; "
        f"refusing: {len(refusing_findings(result, event))}; "
        f"discharged: {len(result.discharged)}"
    )


def _main(argv: Sequence[str], *, repo_root: Path | None) -> int:
    args = _arguments(argv)
    if args is None or (not args.harvest and not args.github_event):
        raise ScanError("name one harvested issues file")
    if args.harvest and args.github_event:
        raise ScanError("choose a harvest or a GitHub event")
    if args.github_event and args.population:
        raise ScanError("--population applies only to a harvest")
    if args.github_event and args.pushed_range:
        raise ScanError("--pushed-range applies only to a harvest")
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
        result = scan(rows, repo_root or Path.cwd(), args.pushed_range)

    for finding in result.findings:
        posture = (
            " [grandfathered]" if finding in result.grandfathered else
            " [owed by this merge]" if finding in result.landing else ""
        )
        print(format_finding(finding) + posture)
    for entry in result.discharged:
        print(f"discharged: {entry}; due for removal")
    for reason in result.not_scanned:
        print(f"did not scan: {reason}", file=sys.stderr)
    report_counts(result, bool(args.github_event))

    if result.findings:
        print(f"{len(result.findings)} finding(s)")
        if args.advisory:
            return CLEAN
        blocking = refusing_findings(result, bool(args.github_event))
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
