"""implementation_map.py -- deterministic helper for the implementation-map skill.

One coordination issue per repository holds the implementation map. Its body
carries a versioned machine-readable state block bounded by unique HTML
markers; everything rendered around it (Mermaid graph, packet table,
frontiers) is a derived view and is never read back as memory.

What the state records (semantic facts GitHub does not hold):
  - packet identifiers and membership;
  - declared HARD edges (ticket -> ticket, mirrored as native blocked-by);
  - REBUILD-SAVING edges (packet -> packet);
  - collision groups (packets that must not build concurrently);
  - EXTERNAL-GATE entries (a packet waiting on something that is not a
    mapped packet: an out-of-map issue, a ruling, a machine -- and also the
    encoding for a hard-by-ruling dependency that must NOT become native,
    e.g. a split ticket's later stage gated on `issue:N` of the blocker);
  - explicit exclusions and their reasons;
  - the coordination issue's own identity and the schema version.

What is derived from GitHub on every run (never stored): issue titles,
open/closed state, labels, native blocked-by relationships, in-flight state,
and the current frontier.

Division of labor: this script mutates ONLY the coordination issue, and only
through `init`, `apply-delta`, and `publish`. It never creates implementation
tickets and never edits native blocked-by relationships -- `check` reports
drift between declared HARD edges and native blocked-by and prints the exact
`gh` command that would reconcile each, for the agent to run after review.
It never infers a semantic edge from prose or shared filenames. Direct
placement derives only the packet shell and native HARD edges; the outcome is
authored judgment. The complete boundary is
``implementation_map.DECLARED_LIMITS`` and is not copied here.

Exit status distinguishes not having run from having found nothing:
0 clean, 1 findings or a refused claim, 2 for every way of not having run
(no map where one is expected, several maps, malformed or duplicated state
markers, an unreadable tracker, a delta that does not validate). A failed
read-back after a write is 1, not 2 -- the mutation DID happen, and 2 would
claim it had not. Callers keying "continue normally" on exit 2 must key on
the `no implementation map` message, never the bare status: every other 2 is
corruption to stop on, not absence to skip.

GitHub access shells out to `gh`.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Callable, NamedTuple

import artifact_lock
from console_codec import use_utf8
import tracker_publish_hook

SCHEMA = 1
STATE_BEGIN = "<!-- implementation-map:v1:state:begin -->"
STATE_END = "<!-- implementation-map:v1:state:end -->"

EDGE_TYPES = ("HARD", "REBUILD-SAVING", "EXTERNAL-GATE")
# COLLISION-SEQUENCING is recorded as collision groups, not as edges: a
# collision is symmetric and n-ary, and an edge encoding of one invites the
# false blocking dependency this skill exists to refuse.


class DeclaredLimit(NamedTuple):
    key: str
    limit: str


DECLARED_LIMITS = (
    DeclaredLimit(
        "semantic-placement",
        "No mechanical check establishes that an authored packet, outcome, edge, collision, gate, or exclusion is the correct judgment.",
    ),
    DeclaredLimit(
        "outcome-substance",
        "A nonblank outcome passes even when its prose is generic, incomplete, or wrong.",
    ),
    DeclaredLimit(
        "cross-machine-prevention",
        "The operating-system lock coordinates only this machine; the state hash can refuse but cannot prevent a remote race.",
    ),
    DeclaredLimit(
        "ready-window",
        "A ready ticket may remain unmapped between its label change and the next reconciliation.",
    ),
    DeclaredLimit(
        "github-renderability",
        "Internal Mermaid consistency does not establish that GitHub will render the graph.",
    ),
    DeclaredLimit(
        "future-mermaid-shapes",
        "The emitter check is complete for the line shapes this module writes and does not recognize a future construct automatically.",
    ),
    DeclaredLimit(
        "collision-kind-forward-compatibility",
        "An unknown collision-group kind is preserved and ignored here; its sequencing meaning belongs to the classifier that introduces the field.",
    ),
)


class MapError(Exception):
    """A reason the run could not happen. Converted to exit 2 at main()."""


class Finding:
    def __init__(self, kind: str, detail: str, remedy: str = "") -> None:
        self.kind = kind
        self.detail = detail
        self.remedy = remedy

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Finding({self.kind}: {self.detail})"


# ---------------------------------------------------------------------------
# State block
# ---------------------------------------------------------------------------

def extract_state(body: str) -> dict:
    """Parse the one state block out of an issue body.

    Raises MapError on zero blocks, several blocks, an unterminated block,
    or JSON that does not parse -- a malformed memory must stop the run, not
    degrade into an empty map.
    """
    begins = body.count(STATE_BEGIN)
    ends = body.count(STATE_END)
    if begins == 0:
        raise MapError("no state block: the begin marker is absent")
    if begins > 1 or ends > 1:
        raise MapError(f"duplicated state markers: {begins} begin, {ends} end")
    if ends == 0:
        raise MapError("unterminated state block: begin marker without end")
    start = body.index(STATE_BEGIN) + len(STATE_BEGIN)
    end = body.index(STATE_END)
    if end < start:
        raise MapError("state end marker precedes its begin marker")
    segment = body[start:end]
    fence = re.search(r"```json\s*\n(.*?)\n```", segment, re.DOTALL)
    if not fence:
        raise MapError("state block holds no ```json fence")
    try:
        state = json.loads(fence.group(1))
    except json.JSONDecodeError as err:
        raise MapError(f"state JSON does not parse: {err}") from err
    if not isinstance(state, dict):
        raise MapError("state JSON is not an object")
    if state.get("schema") != SCHEMA:
        raise MapError(
            f"state schema {state.get('schema')!r} is not {SCHEMA}; "
            "migrate before operating on this map"
        )
    require_well_formed(state)
    return state


def require_well_formed(state: dict) -> None:
    """Field-level shape gate. A state that parsed as JSON can still be
    missing the keys every accessor assumes; that must stop the run as a
    did-not-run, never escape as a traceback wearing exit 1."""
    for key in ("packets", "edges", "collision_groups", "exclusions"):
        rows = state.get(key, [])
        if not isinstance(rows, list):
            raise MapError(f"state.{key} is not a list")
        if not all(isinstance(row, dict) for row in rows):
            raise MapError(f"state.{key} holds a non-object row")
    for p in state.get("packets", []):
        if not isinstance(p.get("id"), str) or not isinstance(p.get("tickets"), list):
            raise MapError(
                f"malformed packet {p!r}: needs a string id and a tickets list"
            )
    for edge in state.get("edges", []):
        kind = edge.get("type")
        if kind == "HARD":
            if not isinstance(edge.get("from_ticket"), int) \
                    or not isinstance(edge.get("to_ticket"), int):
                raise MapError(f"malformed HARD edge {edge!r}")
        elif kind == "REBUILD-SAVING":
            if not isinstance(edge.get("from"), str) or not isinstance(edge.get("to"), str):
                raise MapError(f"malformed REBUILD-SAVING edge {edge!r}")
        elif kind == "EXTERNAL-GATE":
            if not isinstance(edge.get("to"), str):
                raise MapError(f"malformed EXTERNAL-GATE edge {edge!r}")
    for group in state.get("collision_groups", []):
        if not isinstance(group.get("name"), str) or not isinstance(group.get("packets"), list):
            raise MapError(f"malformed collision group {group!r}")
    for row in state.get("exclusions", []):
        if "ticket" not in row:
            raise MapError(f"malformed exclusion {row!r}")


def state_block(state: dict) -> str:
    payload = json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False)
    return (
        "<details><summary>Machine state (do not hand-edit; "
        "use implementation_map.py)</summary>\n\n"
        f"{STATE_BEGIN}\n```json\n{payload}\n```\n{STATE_END}\n\n</details>"
    )


def state_hash(body: str) -> str:
    """Hash only canonical machine state, never the volatile derived views."""
    canonical = state_block(extract_state(body)).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def preserve_refused_outcomes(
    outcomes: tuple[str, ...], *, issue_number: int, reason: str
) -> Path | None:
    """Persist authored judgment that a refused tracker write would strand."""
    kept = [outcome for outcome in outcomes if outcome.strip()]
    if not kept:
        return None
    directory = Path(tempfile.gettempdir()) / "clinical-skills-map-refusals"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"issue-{issue_number}-{uuid.uuid4().hex}.json"
    path.write_text(
        json.dumps(
            {"issue": issue_number, "outcomes": kept, "reason": reason},
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    return path


def map_artifact(tracker, issue_number: int) -> Path:
    """Stable lock identity for one repository's coordination issue."""
    repo = getattr(tracker, "repo", "in-memory")
    identity = hashlib.sha256(f"{repo}#{issue_number}".encode("utf-8")).hexdigest()
    return Path(tempfile.gettempdir()) / "clinical-skills-map-artifacts" / identity


# ---------------------------------------------------------------------------
# Tracker adapters
# ---------------------------------------------------------------------------

class GitHub:
    """Live adapter. Every method mirrors one on the test fake."""

    def __init__(self, repo: str) -> None:
        self.repo = repo

    def _run(self, args: list[str], input_text: str | None = None) -> str:
        try:
            proc = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                input=input_text,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError as err:
            raise MapError("`gh` is not installed or not on PATH") from err
        if proc.returncode != 0:
            raise MapError(f"gh {' '.join(args[:3])}... failed: {proc.stderr.strip()[:400]}")
        return proc.stdout

    def issues(self) -> list[dict]:
        """Every issue (not PRs), open and closed, with bodies."""
        out = self._run([
            "api", "--paginate",
            f"repos/{self.repo}/issues?state=all&per_page=100",
        ])
        rows: list[dict] = []
        # --paginate concatenates JSON arrays; parse them in sequence.
        decoder = json.JSONDecoder()
        index = 0
        while index < len(out):
            while index < len(out) and out[index] in " \r\n\t":
                index += 1
            if index >= len(out):
                break
            chunk, offset = decoder.raw_decode(out, index)
            rows.extend(chunk)
            index = offset
        return [
            {
                "number": row["number"],
                "title": row.get("title", ""),
                "state": row.get("state", "open").lower(),
                "labels": sorted(label["name"] for label in row.get("labels", [])),
                "assignees": sorted(a["login"] for a in row.get("assignees", [])),
                "body": row.get("body") or "",
            }
            for row in rows
            if "pull_request" not in row
        ]

    def blocked_by(self, number: int) -> list[int]:
        out = self._run([
            "api", f"repos/{self.repo}/issues/{number}/dependencies/blocked_by",
            "--jq", "[.[].number]",
        ])
        return sorted(json.loads(out or "[]"))

    def default_branch_head(self) -> str:
        out = self._run([
            "api", f"repos/{self.repo}", "--jq", ".default_branch",
        ]).strip()
        sha = self._run([
            "api", f"repos/{self.repo}/commits/{out}", "--jq", ".sha",
        ]).strip()
        return sha[:7]

    def get_issue(self, number: int) -> dict:
        out = self._run(["api", f"repos/{self.repo}/issues/{number}"])
        row = json.loads(out)
        return {
            "number": row["number"],
            "title": row.get("title", ""),
            "state": row.get("state", "open").lower(),
            "labels": sorted(label["name"] for label in row.get("labels", [])),
            "assignees": sorted(a["login"] for a in row.get("assignees", [])),
            "body": row.get("body") or "",
        }

    def update_issue_body(self, number: int, body: str) -> None:
        payload = json.dumps({"body": body})
        self._run(
            ["api", "-X", "PATCH", f"repos/{self.repo}/issues/{number}",
             "--input", "-"],
            input_text=payload,
        )

    def create_issue(self, title: str, body: str, labels: list[str]) -> int:
        payload = json.dumps({"title": title, "body": body, "labels": labels})
        out = self._run(
            ["api", "-X", "POST", f"repos/{self.repo}/issues", "--input", "-"],
            input_text=payload,
        )
        return json.loads(out)["number"]


# ---------------------------------------------------------------------------
# Live view
# ---------------------------------------------------------------------------

class Live:
    """Everything derived from the tracker on this run."""

    def __init__(self, tracker, state: dict) -> None:
        self.issues = {row["number"]: row for row in tracker.issues()}
        self.blocked_by: dict[int, list[int]] = {}
        for ticket in sorted(all_tickets(state)):
            if ticket in self.issues:
                self.blocked_by[ticket] = tracker.blocked_by(ticket)

    def is_open(self, number: int) -> bool:
        row = self.issues.get(number)
        return bool(row) and row["state"] == "open"

    def is_closed(self, number: int) -> bool:
        row = self.issues.get(number)
        return bool(row) and row["state"] != "open"


def find_map_issues(tracker) -> list[dict]:
    """Every issue whose body carries the begin marker -- found by the
    marker, never by title."""
    return [row for row in tracker.issues() if STATE_BEGIN in row["body"]]


def locate_map(tracker) -> dict:
    found = find_map_issues(tracker)
    if not found:
        raise MapError(
            "no implementation map: no issue body carries "
            f"{STATE_BEGIN!r}. Run `init` to create one."
        )
    if len(found) > 1:
        numbers = ", ".join(f"#{row['number']}" for row in found)
        raise MapError(
            f"{len(found)} issues carry the state marker ({numbers}); "
            "exactly one map is expected. Resolve by hand before operating."
        )
    return found[0]


# ---------------------------------------------------------------------------
# State accessors
# ---------------------------------------------------------------------------

def packets(state: dict) -> list[dict]:
    return state.get("packets", [])


def packet_ids(state: dict) -> list[str]:
    return [p["id"] for p in packets(state)]


def packet_of(state: dict, ticket: int) -> str | None:
    for p in packets(state):
        if ticket in p["tickets"]:
            return p["id"]
    return None


def all_tickets(state: dict) -> list[int]:
    seen: list[int] = []
    for p in packets(state):
        seen.extend(p["tickets"])
    return seen


def excluded_tickets(state: dict) -> dict[int, str]:
    return {row["ticket"]: row.get("why", "") for row in state.get("exclusions", [])}


def edges_of(state: dict, kind: str) -> list[dict]:
    return [e for e in state.get("edges", []) if e.get("type") == kind]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_shape(state: dict) -> list[Finding]:
    """Structural checks that need no tracker."""
    findings: list[Finding] = []
    ids = packet_ids(state)
    for pid in ids:
        if ids.count(pid) > 1:
            findings.append(Finding("duplicate-packet", f"packet id {pid} declared twice"))
    seen: dict[int, str] = {}
    for p in packets(state):
        for ticket in p["tickets"]:
            if not isinstance(ticket, int):
                findings.append(Finding("bad-ticket", f"{p['id']} holds non-integer ticket {ticket!r}"))
                continue
            if ticket in seen:
                findings.append(Finding(
                    "duplicate-ticket",
                    f"#{ticket} belongs to both {seen[ticket]} and {p['id']}",
                ))
            seen[ticket] = p["id"]
    for ticket, why in excluded_tickets(state).items():
        if ticket in seen:
            findings.append(Finding(
                "excluded-and-mapped",
                f"#{ticket} is excluded ({why!r}) and also in {seen[ticket]}",
            ))
    known = set(ids)
    for edge in state.get("edges", []):
        kind = edge.get("type")
        if kind not in EDGE_TYPES:
            findings.append(Finding("bad-edge-type", f"edge type {kind!r} is not one of {EDGE_TYPES}"))
            continue
        if kind == "HARD":
            src, dst = edge.get("from_ticket"), edge.get("to_ticket")
            if src not in seen or dst not in seen:
                findings.append(Finding(
                    "hard-edge-off-map",
                    f"HARD {src} -> {dst}: both ends must be mapped tickets; "
                    "an off-map predecessor is an EXTERNAL-GATE, not a HARD edge",
                ))
        elif kind == "REBUILD-SAVING":
            if edge.get("from") not in known or edge.get("to") not in known:
                findings.append(Finding(
                    "edge-off-map",
                    f"REBUILD-SAVING {edge.get('from')} -> {edge.get('to')}: unknown packet",
                ))
        elif kind == "EXTERNAL-GATE":
            if edge.get("to") not in known:
                findings.append(Finding(
                    "edge-off-map",
                    f"EXTERNAL-GATE on {edge.get('on')!r} -> {edge.get('to')}: unknown packet",
                ))
    for group in state.get("collision_groups", []):
        for pid in group.get("packets", []):
            if pid not in known:
                findings.append(Finding(
                    "collision-off-map",
                    f"collision group {group.get('name')!r} names unknown packet {pid}",
                ))
    findings.extend(cycle_findings(state))
    return findings


def sequencing_graph(state: dict) -> dict[str, set[str]]:
    """Packet -> its predecessor packets, over declared HARD (lifted to
    packet level, intra-packet edges dropped) plus REBUILD-SAVING."""
    graph: dict[str, set[str]] = {pid: set() for pid in packet_ids(state)}
    for edge in edges_of(state, "HARD"):
        src = packet_of(state, edge.get("from_ticket"))
        dst = packet_of(state, edge.get("to_ticket"))
        if src and dst and src != dst:
            graph[dst].add(src)
    for edge in edges_of(state, "REBUILD-SAVING"):
        src, dst = edge.get("from"), edge.get("to")
        if dst in graph and src in graph:
            graph[dst].add(src)
    return graph


def cycle_findings(state: dict) -> list[Finding]:
    graph = sequencing_graph(state)
    color: dict[str, int] = {}
    stack: list[str] = []
    cycles: list[str] = []

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for pred in sorted(graph.get(node, ())):
            if color.get(pred) == 1:
                loop = stack[stack.index(pred):] + [pred]
                cycles.append(" -> ".join(loop))
            elif color.get(pred, 0) == 0:
                visit(pred)
        stack.pop()
        color[node] = 2

    for node in sorted(graph):
        if color.get(node, 0) == 0:
            visit(node)
    return [Finding("cycle", f"sequencing cycle: {loop}") for loop in sorted(set(cycles))]


def validate_against_live(state: dict, live: Live) -> list[Finding]:
    findings: list[Finding] = []
    excluded = excluded_tickets(state)
    mapped = set(all_tickets(state))

    for ticket in sorted(mapped):
        if ticket not in live.issues:
            findings.append(Finding("unknown-ticket", f"#{ticket} is mapped but not on the tracker"))

    # Declared HARD edges must agree with native blocked-by, both directions.
    declared = {(e["from_ticket"], e["to_ticket"]) for e in edges_of(state, "HARD")}
    for src, dst in sorted(declared):
        if dst in live.blocked_by and src not in live.blocked_by[dst]:
            findings.append(Finding(
                "hard-edge-not-native",
                f"declared HARD #{src} -> #{dst} has no native blocked-by",
                remedy=(
                    "mirror it natively (two steps; the API takes the database "
                    f"id, not the number): gh api repos/{state.get('repo', 'OWNER/REPO')}"
                    f"/issues/{src} --jq .id ; then POST that id as "
                    f'{{"issue_id": <id>}} to gh api -X POST '
                    f"repos/{state.get('repo', 'OWNER/REPO')}/issues/{dst}"
                    "/dependencies/blocked_by --input <file>"
                ),
            ))
    for dst, blockers in sorted(live.blocked_by.items()):
        for src in blockers:
            if src in mapped and (src, dst) not in declared:
                same_packet = packet_of(state, src) == packet_of(state, dst)
                findings.append(Finding(
                    "native-edge-undeclared",
                    f"native blocked-by #{src} -> #{dst} is not a declared HARD edge"
                    + (" (same packet; declare it anyway)" if same_packet else ""),
                    remedy="apply a delta declaring it HARD, or investigate why it was recorded",
                ))

    # A gate on an issue that does not exist blocks its packet forever in
    # silence -- a typo'd number must be a finding, not a permanent hold.
    for edge in edges_of(state, "EXTERNAL-GATE"):
        match = re.fullmatch(r"issue:(\d+)", str(edge.get("on", "")))
        if match and int(match.group(1)) not in live.issues:
            findings.append(Finding(
                "gate-unknown-issue",
                f"EXTERNAL-GATE on {edge.get('on')} -> {edge.get('to')}: "
                "no such issue on the tracker",
            ))

    # Readiness must agree with map membership in both directions.
    ready_labels = set(state.get("ready_labels", ["ready-for-agent"]))
    in_flight_labels = set(state.get("in_flight_labels", []))
    for packet in packets(state):
        for number in packet_readiness(state, live, packet["id"]):
            findings.append(Finding(
                "mapped-not-ready",
                f"#{number} is open and mapped but carries no label in "
                f"ready_labels {sorted(ready_labels)}",
            ))

    # Ready or in-flight tickets absent from the map, unless excluded.
    for number, row in sorted(live.issues.items()):
        if row["state"] != "open" or number in mapped or number in excluded:
            continue
        if STATE_BEGIN in row["body"]:
            continue  # the coordination issue itself
        labels = set(row["labels"])
        if labels & ready_labels:
            findings.append(Finding(
                "unmapped-ready",
                f"#{number} carries {sorted(labels & ready_labels)} but is in no packet "
                "and not excluded",
            ))
        elif (labels & in_flight_labels) or row["assignees"]:
            findings.append(Finding(
                "unmapped-in-flight",
                f"#{number} looks in flight "
                f"(labels {sorted(labels & in_flight_labels)}, assignees {row['assignees']}) "
                "but is in no packet and not excluded",
            ))
    return findings


# ---------------------------------------------------------------------------
# Status and frontiers -- derived, never stored
# ---------------------------------------------------------------------------

def hard_blockers_of(state: dict, live: Live, packet: dict) -> list[int]:
    """Open hard blockers of a packet: the union of native blocked-by and
    declared HARD edges. Declared-only covers the window before the agent
    mirrors the edge natively -- claim must refuse there too, or it passes
    during exactly the drift `check` reports."""
    tickets = packet["tickets"]
    candidates: set[int] = set()
    for ticket in tickets:
        candidates.update(live.blocked_by.get(ticket, []))
    for edge in edges_of(state, "HARD"):
        if edge.get("to_ticket") in tickets:
            candidates.add(edge.get("from_ticket"))
    return sorted(
        blocker for blocker in candidates
        if isinstance(blocker, int)
        and blocker not in tickets  # intra-packet sequencing is the packet's own
        and live.is_open(blocker)
    )


def open_blockers(state: dict, live: Live, packet: dict) -> list[str]:
    """Display strings for everything currently holding a packet: open hard
    blockers plus uncleared gates."""
    found = {f"#{b}" for b in hard_blockers_of(state, live, packet)}
    for edge in edges_of(state, "EXTERNAL-GATE"):
        if edge.get("to") == packet["id"] and not gate_cleared(edge, live):
            found.add(str(edge.get("on")))
    return sorted(found)


def packet_status(state: dict, live: Live, pid: str) -> str:
    """done | blocked | gated | in-flight | deferred | ready.

    Blocking is checked before in-flight: a packet that is both assigned and
    hard-blocked reads blocked -- an assignee must not launder a blocker into
    a warning."""
    packet = next(p for p in packets(state) if p["id"] == pid)
    tickets = packet["tickets"]
    if tickets and all(live.is_closed(t) for t in tickets):
        return "done"
    for blocker in hard_blockers_of(state, live, packet):
        return "blocked" if packet_of(state, blocker) else "gated"
    for edge in edges_of(state, "EXTERNAL-GATE"):
        if edge.get("to") == pid and not gate_cleared(edge, live):
            return "gated"
    for ticket in tickets:
        row = live.issues.get(ticket)
        if row and row["assignees"]:
            return "in-flight"
        if row and set(row["labels"]) & set(state.get("in_flight_labels", [])):
            return "in-flight"
    for edge in edges_of(state, "REBUILD-SAVING"):
        if edge.get("to") == pid:
            if packet_status_ignoring_r(state, live, edge.get("from")) != "done":
                return "deferred"
    return "ready"


def packet_readiness(state: dict, live: Live, pid: str) -> list[int]:
    """Open tickets in a packet carrying no configured readiness label."""
    packet = next(p for p in packets(state) if p["id"] == pid)
    ready_labels = set(state.get("ready_labels", ["ready-for-agent"]))
    return sorted(
        ticket for ticket in packet["tickets"]
        if live.is_open(ticket)
        and not set(live.issues[ticket]["labels"]) & ready_labels
    )


def packet_status_ignoring_r(state: dict, live: Live, pid: str) -> str:
    packet = next((p for p in packets(state) if p["id"] == pid), None)
    if packet is None:
        return "open"
    if packet["tickets"] and all(live.is_closed(t) for t in packet["tickets"]):
        return "done"
    return "open"


def gate_cleared(edge: dict, live: Live) -> bool:
    """An `on` of the form 'issue:N' clears when #N closes; anything else
    (a ruling, a machine) never clears mechanically and is lifted by a delta
    that removes the edge."""
    target = edge.get("on", "")
    match = re.fullmatch(r"issue:(\d+)", target)
    if match:
        return live.is_closed(int(match.group(1)))
    return False


def frontiers(state: dict, live: Live) -> list[list[str]]:
    """Peel the H+R packet DAG. Frontier 1 is every packet genuinely
    startable now; each later frontier is unlocked by the ones before it.
    Only done packets are satisfied predecessors. Gated, unready, and
    in-flight packets are unsatisfied non-members: they and their successors
    sit outside every frontier until the gate clears, readiness returns, or
    the merge lands -- branch progress is not a moved default branch. The
    first layer is additionally held to a startable derived status, so a
    native blocker the graph cannot see (undeclared drift) never renders as
    buildable."""
    graph = sequencing_graph(state)
    status = {pid: packet_status(state, live, pid) for pid in graph}
    done = {pid for pid, s in status.items() if s == "done"}
    unready = {pid for pid in graph if packet_readiness(state, live, pid)}
    unavailable = (
        {pid for pid, s in status.items() if s in ("gated", "in-flight")}
        | unready
    )
    remaining = {pid for pid in graph if pid not in done and pid not in unavailable}
    result: list[list[str]] = []
    first = True
    while remaining:
        layer = sorted(
            pid for pid in remaining
            if not (graph[pid] & (remaining | unavailable))
            and not (first and status[pid] not in ("ready", "deferred"))
        )
        if not layer:
            break  # a cycle among the remainder; cycle_findings reports it
        result.append(layer)
        remaining -= set(layer)
        first = False
    return result


# ---------------------------------------------------------------------------
# Rendering -- deterministic function of (state, live, snapshot)
# ---------------------------------------------------------------------------

MAINTENANCE_RULE = """\
1. Native GitHub blocked-by relationships are authoritative. Only HARD edges
   become native blocked-by; REBUILD-SAVING, COLLISION-SEQUENCING, and
   EXTERNAL-GATE relationships live only in this map.
2. This issue's Mermaid graph, packet table, and frontier are derived views.
   The machine-state block above is the only part read back as memory.
3. Whenever a merged ADR creates a new ticket, splits or combines
   implementation work, changes an existing ticket's readiness, introduces,
   removes, or reverses a dependency, or invalidates an artifact another
   ticket would build, the ADR/grilling closeout performs an incremental map
   reconciliation. After merge, `tools/map_scan.py` mechanically grades that
   the reconciliation obligation was discharged.
4. An incremental reconciliation reads: the merged ADR from the current
   default branch; every ticket created by it; every existing ticket changed
   or commented on by its exhaustive sweep; and the current native dependency
   relationships.
5. It then: adds or removes native blocked-by relationships; places new work
   into an existing packet or creates a new packet (via a reviewed delta);
   recalculates the current frontier; updates this issue's graph and packet
   table; and records the new default-branch commit and update date.
6. Do not rebuild the complete map after every ADR unless the ADR changes a
   shared architectural assumption or has repository-wide effects.
7. Run a complete map rebuild (`audit`, then a fresh full reconciliation):
   after the remaining grilling queue is completed; before starting a new
   major implementation wave; whenever an incremental update cannot place the
   new work confidently; and whenever the native dependency graph and this
   issue disagree.
8. Every /implement closeout updates the map after merge when closing its
   ticket changes the frontier. Closing a native blocker updates GitHub's
   dependency state, but the Mermaid graph and written frontier here still
   require an edit (`publish`). The offline gate's complete boundary is
   `map_scan.DECLARED_LIMITS`; no row of it is copied here.
9. Readiness stays separate from packet status: `claim` refuses an unready
   packet, `check` reports every mapped open ticket that is not ready, and
   frontiers omit an unready packet and its successors."""

HOW_TO_UPDATE = """\
This map is maintained by the `implementation-map` skill and the committed
`tools/implementation_map.py` helper. Do not hand-edit the machine-state block
or the derived sections.

- Check without mutating: `python tools/implementation_map.py check --repo <o/r>`
- Verify a packet is startable before building: `... claim --packet <id>`
- Place new/changed work (reviewed delta JSON): `... apply-delta --delta <f>`
- Place one newly-ready ticket without JSON surgery:
  `... apply-delta --ticket <n> --outcome <authored judgment>`
- Refresh the derived views after merges: `... publish`
- Full rebuild-and-compare: `... audit`

A new ADR or ticket cannot be placed by the script alone: write the delta,
review it against the ADR's rulings, then apply it. Semantic edges come from
rulings, never from prose similarity or shared filenames."""


def ticket_label(p: dict) -> str:
    """`#a, #b`, or a stage marker for a ticketless packet."""
    return ", ".join(f"#{t}" for t in p["tickets"]) or "stage packet"


def node_id(pid: str) -> str:
    """A packet id may hold characters Mermaid refuses in a node id
    (`P497+532`); sanitize the id, keep the real name in the label."""
    return re.sub(r"[^A-Za-z0-9_]", "_", pid)


def mermaid_ids(state: dict) -> dict[str, str]:
    """Packet id -> unique Mermaid node id. Sanitization can collide
    (`P497+532` and `P497_532` share a base); collisions take a suffix."""
    ids: dict[str, str] = {}
    for pid in packet_ids(state):
        base = node_id(pid)
        candidate, n = base, 2
        while candidate in ids.values():
            candidate = f"{base}_{n}"
            n += 1
        ids[pid] = candidate
    return ids


class MermaidCoverage(NamedTuple):
    total: int
    nodes: int
    packet_nodes: int
    edges: int
    directives: int
    unread: tuple[str, ...]


MERMAID_NODE = re.compile(
    r'^\s*([A-Za-z0-9_]+)(?:\[".*"\]|\(\[".*"\]\):::gate)\s*$'
)
MERMAID_EDGE = re.compile(
    r'^\s*([A-Za-z0-9_]+)\s+'
    r'(?:-->\|HARD\||-\.->\|saves rebuild\||==>\|GATE\||-\.-)\s+'
    r'([A-Za-z0-9_]+)\s*$'
)


def verify_mermaid(state: dict, graph: str) -> MermaidCoverage:
    """Prove coverage and referential integrity for the emitted block."""
    lines = tuple(line for line in graph.splitlines() if line.strip())
    defined: set[str] = set()
    references: set[str] = set()
    edge_lines: list[str] = []
    unread: list[str] = []
    directives = 0
    for line in lines:
        node = MERMAID_NODE.fullmatch(line)
        if node:
            defined.add(node.group(1))
            continue
        edge = MERMAID_EDGE.fullmatch(line)
        if edge:
            edge_lines.append(line.strip())
            references.update(edge.groups())
            continue
        stripped = line.strip()
        if (
            stripped == "graph TD"
            or stripped.startswith("classDef ")
            or (stripped.startswith("class ") and stripped.endswith(" done"))
        ):
            directives += 1
            continue
        unread.append(line)

    undefined = sorted(references - defined)
    if undefined:
        raise MapError(f"Mermaid edge references undefined node(s): {undefined}")
    duplicates = sorted({line for line in edge_lines if edge_lines.count(line) > 1})
    if duplicates:
        raise MapError(f"duplicate Mermaid edge line(s): {duplicates}")
    expected_packets = set(mermaid_ids(state).values())
    missing_packets = sorted(expected_packets - defined)
    if missing_packets:
        raise MapError(f"state packet has no Mermaid node: {missing_packets}")
    if unread:
        raise MapError(f"unaccounted Mermaid line(s): {unread}")
    return MermaidCoverage(
        total=len(lines),
        nodes=len(defined),
        packet_nodes=len(expected_packets),
        edges=len(edge_lines),
        directives=directives,
        unread=tuple(unread),
    )


def mermaid(state: dict, live: Live) -> str:
    lines = ["graph TD"]
    status = {pid: packet_status(state, live, pid) for pid in packet_ids(state)}
    ids = mermaid_ids(state)
    for p in packets(state):
        tickets = " ".join(f"#{t}" for t in p["tickets"]) or "stage"
        label = f"{ids[p['id']]}[\"{p['id']}: {tickets}\"]"
        lines.append(f"    {label}")
    hard_pairs: set[tuple[str, str]] = set()
    for edge in edges_of(state, "HARD"):
        src = packet_of(state, edge["from_ticket"])
        dst = packet_of(state, edge["to_ticket"])
        if src and dst and src != dst:
            hard_pairs.add((src, dst))
    for src, dst in sorted(hard_pairs):
        lines.append(f"    {ids[src]} -->|HARD| {ids[dst]}")
    for edge in sorted(edges_of(state, "REBUILD-SAVING"),
                       key=lambda e: (e["from"], e["to"])):
        lines.append(
            f"    {ids[edge['from']]} -.->|saves rebuild| {ids[edge['to']]}"
        )
    gate_nodes: set[str] = set()
    for edge in sorted(edges_of(state, "EXTERNAL-GATE"),
                       key=lambda e: (str(e.get("on")), e["to"])):
        node = re.sub(r"[^A-Za-z0-9_]", "_", f"EXT_{edge.get('on', 'gate')}")
        if node not in gate_nodes:
            gate_nodes.add(node)
            lines.append(f"    {node}([\"{edge.get('on')}\"]):::gate")
        lines.append(f"    {node} ==>|GATE| {ids[edge['to']]}")
    for group in sorted(state.get("collision_groups", []), key=lambda g: g["name"]):
        members = group.get("packets", [])
        for left, right in zip(members, members[1:]):
            lines.append(f"    {ids[left]} -.- {ids[right]}")
    done = sorted(ids[pid] for pid, s in status.items() if s == "done")
    if done:
        lines.append("    classDef done fill:#d4edda,stroke:#155724")
        lines.append(f"    class {','.join(done)} done")
    lines.append("    classDef gate stroke-dasharray: 5 5")
    result: list[str] = []
    seen_edges: set[str] = set()
    for line in lines:
        if MERMAID_EDGE.fullmatch(line):
            normalized = line.strip()
            if normalized in seen_edges:
                continue
            seen_edges.add(normalized)
        result.append(line)
    return "\n".join(result)


def render(state: dict, live: Live, snapshot: dict) -> str:
    status = {pid: packet_status(state, live, pid) for pid in packet_ids(state)}
    fronts = frontiers(state, live)
    ready_count = sum(
        1 for row in live.issues.values()
        if row["state"] == "open"
        and set(row["labels"]) & set(state.get("ready_labels", ["ready-for-agent"]))
    )
    graph = mermaid(state, live)
    verify_mermaid(state, graph)
    parts: list[str] = []
    parts.append(
        "This is a coordination artifact, not an implementation ticket: a "
        "derived visualization of the ruled backlog. It duplicates no "
        "acceptance criteria; every packet's spec is its tickets and their "
        "ADRs. Native blocked-by relationships are authoritative; when this "
        "page and GitHub disagree, GitHub wins and this page gets rebuilt."
    )
    parts.append(state_block(state))
    parts.append(
        "## Snapshot\n\n"
        f"- default-branch commit: `{snapshot['commit']}`\n"
        f"- generated: {snapshot['date']}\n"
        f"- live ready-for-agent tickets: {ready_count}"
    )
    front_lines: list[str] = []
    if fronts:
        front_lines.append(
            "Packets buildable immediately (no open hard blocker, no unmet "
            "rebuild-saving predecessor):"
        )
        front_lines.append("")
        for pid in fronts[0]:
            packet = next(p for p in packets(state) if p["id"] == pid)
            front_lines.append(
                f"- **{pid}** ({ticket_label(packet)})"
                f" - {packet.get('title', '')}"
            )
    else:
        front_lines.append("No packet is currently startable.")
    groups = state.get("collision_groups", [])
    if groups:
        front_lines.append("")
        front_lines.append(
            "Must not build concurrently (collision groups; serialize, and "
            "whichever merges later re-runs the earlier one's tests):"
        )
        front_lines.append("")
        for group in sorted(groups, key=lambda g: g["name"]):
            front_lines.append(
                f"- `{group['name']}`: {', '.join(group['packets'])}"
                + (f" - {group['why']}" if group.get("why") else "")
            )
    parts.append("## Current frontier\n\n" + "\n".join(front_lines))
    parts.append(
        "## Dependency graph\n\n"
        "Solid `HARD` arrows are native blocked-by; dashed `saves rebuild` "
        "arrows are preferred orderings; dotted lines are collision "
        "sequencing (no dependency); double `GATE` arrows wait on something "
        "outside the packet queue.\n\n"
        "```mermaid\n" + graph + "\n```"
    )
    rows = [
        "| Packet | Tickets | Status | Blocked by | Outcome | Collisions |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    group_index: dict[str, list[str]] = {}
    for group in state.get("collision_groups", []):
        for pid in group["packets"]:
            group_index.setdefault(pid, []).append(group["name"])
    for p in packets(state):
        pid = p["id"]
        rows.append(
            f"| {pid} | {ticket_label(p)} "
            f"| {status[pid]} | {', '.join(open_blockers(state, live, p)) or '-'} "
            f"| {p.get('outcome', p.get('title', ''))} "
            f"| {', '.join(sorted(group_index.get(pid, []))) or '-'} |"
        )
    parts.append("## Packet table\n\n" + "\n".join(rows))
    waiting: list[str] = []
    for row in sorted(state.get("exclusions", []), key=lambda r: r["ticket"]):
        waiting.append(f"- #{row['ticket']}: {row.get('why', '')}")
    for pid, s in sorted(status.items()):
        if s == "gated":
            waiting.append(f"- {pid}: gated (see graph)")
    parts.append(
        "## Waiting work\n\n"
        + ("\n".join(waiting) if waiting else "Nothing is excluded or gated.")
    )
    if len(fronts) > 1:
        later = [
            f"- Frontier {i + 2}: {', '.join(layer)}"
            for i, layer in enumerate(fronts[1:])
        ]
        parts.append("## Later frontiers\n\n" + "\n".join(later))
    parts.append("## Maintenance rule\n\n" + MAINTENANCE_RULE)
    parts.append("## How to update this map\n\n" + HOW_TO_UPDATE)
    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Delta
# ---------------------------------------------------------------------------

DELTA_KEYS = {
    "note", "add_packets", "remove_packets", "add_tickets", "remove_tickets",
    "add_edges", "remove_edges", "add_collision_groups",
    "remove_collision_groups", "add_exclusions", "remove_exclusions",
}


def apply_delta(state: dict, delta: dict) -> dict:
    """Pure: returns the new state or raises MapError. The delta is the
    agent's reviewed semantic placement; this only validates and applies."""
    unknown = set(delta) - DELTA_KEYS
    if unknown:
        raise MapError(f"unknown delta keys: {sorted(unknown)}")
    new = json.loads(json.dumps(state))  # deep copy
    for pid in delta.get("remove_packets", []):
        target = next((p for p in new.get("packets", []) if p["id"] == pid), None)
        if target is None:
            raise MapError(f"remove_packets: {pid} is not in the map")
        # A ticket leaves the map with its packet, so every edge touching the
        # packet or its tickets goes too -- a dangling HARD edge would fail
        # the final validation and refuse a legitimate removal.
        dropped = set(target["tickets"])
        new["packets"] = [p for p in new["packets"] if p["id"] != pid]
        new["edges"] = [
            e for e in new.get("edges", [])
            if pid not in (e.get("from"), e.get("to"))
            and e.get("from_ticket") not in dropped
            and e.get("to_ticket") not in dropped
        ]
        for group in new.get("collision_groups", []):
            group["packets"] = [g for g in group["packets"] if g != pid]
    for packet in delta.get("add_packets", []):
        outcome = packet.get("outcome")
        if not isinstance(outcome, str) or not outcome.strip():
            raise MapError(
                f"add_packets: {packet.get('id', '<unknown>')} has a blank outcome"
            )
        existing_packet = next(
            (row for row in new.get("packets", []) if row["id"] == packet["id"]),
            None,
        )
        if existing_packet is not None:
            if existing_packet == packet:
                continue
            raise MapError(f"add_packets: {packet['id']} already exists")
        new.setdefault("packets", []).append(packet)
    for row in delta.get("add_tickets", []):
        pid, ticket = row["packet"], row["ticket"]
        target = next((p for p in new["packets"] if p["id"] == pid), None)
        if target is None:
            raise MapError(f"add_tickets: packet {pid} is not in the map")
        if packet_of(new, ticket) == pid:
            continue
        if packet_of(new, ticket):
            raise MapError(f"add_tickets: #{ticket} already belongs to {packet_of(new, ticket)}")
        target["tickets"].append(ticket)
    for ticket in delta.get("remove_tickets", []):
        pid = packet_of(new, ticket)
        if pid is None:
            raise MapError(f"remove_tickets: #{ticket} is in no packet")
        target = next(p for p in new["packets"] if p["id"] == pid)
        target["tickets"] = [t for t in target["tickets"] if t != ticket]
    for edge in delta.get("remove_edges", []):
        before = len(new.get("edges", []))
        new["edges"] = [e for e in new.get("edges", []) if e != edge]
        if len(new["edges"]) == before:
            raise MapError(f"remove_edges: no such edge {edge}")
    for edge in delta.get("add_edges", []):
        if edge in new.get("edges", []):
            continue
        new.setdefault("edges", []).append(edge)
    for name in delta.get("remove_collision_groups", []):
        groups = new.get("collision_groups", [])
        if not any(g["name"] == name for g in groups):
            raise MapError(f"remove_collision_groups: no group named {name!r}")
        new["collision_groups"] = [g for g in groups if g["name"] != name]
    for group in delta.get("add_collision_groups", []):
        existing_group = next(
            (g for g in new.get("collision_groups", []) if g["name"] == group["name"]),
            None,
        )
        if existing_group == group:
            continue
        if existing_group is not None:
            raise MapError(f"add_collision_groups: {group['name']!r} already exists")
        new.setdefault("collision_groups", []).append(group)
    for ticket in delta.get("remove_exclusions", []):
        rows = new.get("exclusions", [])
        if not any(r["ticket"] == ticket for r in rows):
            raise MapError(f"remove_exclusions: #{ticket} is not excluded")
        new["exclusions"] = [r for r in rows if r["ticket"] != ticket]
    for row in delta.get("add_exclusions", []):
        existing_exclusion = next(
            (r for r in new.get("exclusions", []) if r["ticket"] == row["ticket"]),
            None,
        )
        if existing_exclusion == row:
            continue
        if existing_exclusion is not None:
            raise MapError(f"add_exclusions: #{row['ticket']} already excluded")
        new.setdefault("exclusions", []).append(row)
    # Every shape finding is fatal to a delta -- an allowlist here would let
    # a future finding kind become silently non-fatal.
    require_well_formed(new)
    problems = validate_shape(new)
    if problems:
        details = "; ".join(f"{f.kind}: {f.detail}" for f in problems)
        raise MapError(f"delta produces an invalid map: {details}")
    return new


def _direct_placement_delta(
    state: dict, tracker, ticket: int, outcome: str | None
) -> dict:
    """Build the mechanical part of one newly-ready placement.

    The caller authors only the outcome. The issue title, packet identifier,
    and native HARD edges are derived from the live tracker. Repeating the
    same placement is inert.
    """
    if packet_of(state, ticket) is not None:
        return {}
    issues = {row["number"]: row for row in tracker.issues()}
    row = issues.get(ticket)
    if row is None:
        raise MapError(f"cannot place unknown ticket #{ticket}")
    ready_labels = set(state.get("ready_labels", ["ready-for-agent"]))
    if row["state"] != "open" or not (set(row["labels"]) & ready_labels):
        raise MapError(f"cannot place #{ticket}: it is not an open ready ticket")
    if not isinstance(outcome, str) or not outcome.strip():
        raise MapError(f"cannot place #{ticket}: authored outcome is blank")

    base = f"P{ticket}"
    pid = base
    suffix = 2
    while pid in packet_ids(state):
        pid = f"{base}-{suffix}"
        suffix += 1
    packet = {
        "id": pid,
        "tickets": [ticket],
        "title": row.get("title", ""),
        "outcome": outcome,
    }
    candidate = apply_delta(state, {"add_packets": [packet]})
    live = Live(tracker, candidate)
    mapped = set(all_tickets(candidate))
    existing = {
        (edge["from_ticket"], edge["to_ticket"])
        for edge in edges_of(candidate, "HARD")
    }
    derived = []
    for blocked in sorted(mapped):
        for blocker in live.blocked_by.get(blocked, []):
            pair = (blocker, blocked)
            if blocker in mapped and ticket in pair and pair not in existing:
                hard_edge = {
                    "type": "HARD",
                    "from_ticket": blocker,
                    "to_ticket": blocked,
                }
                derived.append(hard_edge)
                existing.add((hard_edge["from_ticket"], hard_edge["to_ticket"]))
    return {
        "note": f"additive placement of ready ticket #{ticket}",
        "add_packets": [packet],
        "add_edges": derived,
    }


def placement_coverage(state: dict, live: Live) -> tuple[int, tuple[int, ...]]:
    """Return the independently derived ready population and unread remainder."""
    ready_labels = set(state.get("ready_labels", ["ready-for-agent"]))
    ready = {
        number
        for number, row in live.issues.items()
        if row["state"] == "open" and set(row["labels"]) & ready_labels
    }
    remainder = tuple(sorted(ready - set(all_tickets(state)) - set(excluded_tickets(state))))
    return len(ready), remainder


def report_placement_coverage(
    before: dict, after: dict, live: Live
) -> tuple[int, tuple[int, ...]]:
    total, remainder = placement_coverage(after, live)
    written = len(set(packet_ids(after)) - set(packet_ids(before)))
    print(f"packets written: {written}")
    print(f"ready ticket population: {total}")
    suffix = "" if not remainder else ": " + ", ".join(f"#{n}" for n in remainder)
    print(f"ready tickets still unmapped: {len(remainder)}{suffix}")
    print(f"reconciled_through: {after.get('reconciled_through', '<unset>')}")
    return total, remainder


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def report(findings: list[Finding]) -> int:
    if not findings:
        print("clean: no findings")
        return 0
    for f in findings:
        print(f"FINDING {f.kind}: {f.detail}")
        if f.remedy:
            print(f"    remedy: {f.remedy}")
    print(f"{len(findings)} finding(s)")
    return 1


def cmd_check(tracker, args) -> int:
    issue = locate_map(tracker)
    state = extract_state(issue["body"])
    live = Live(tracker, state)
    findings = validate_shape(state) + validate_against_live(state, live)
    print(f"map: issue #{issue['number']} ({issue['title']!r})")
    return report(findings)


def cmd_claim(tracker, args) -> int:
    issue = locate_map(tracker)
    state = extract_state(issue["body"])
    live = Live(tracker, state)
    pid = args.packet
    if pid is None and args.ticket is None:
        print("REFUSED: name --packet <id> or --ticket <number>")
        return 1
    if pid is None and args.ticket is not None:
        pid = packet_of(state, args.ticket)
        if pid is None:
            if args.ticket in excluded_tickets(state):
                print(f"REFUSED: #{args.ticket} is explicitly excluded: "
                      f"{excluded_tickets(state)[args.ticket]!r}")
            else:
                print(f"REFUSED: #{args.ticket} is in no packet; reconcile the map first")
            return 1
    if pid not in packet_ids(state):
        print(f"REFUSED: packet {pid!r} is not in the map")
        return 1
    status = packet_status(state, live, pid)
    packet = next(p for p in packets(state) if p["id"] == pid)
    if status in ("blocked", "gated"):
        print(f"REFUSED: {pid} is {status} on "
              f"{', '.join(open_blockers(state, live, packet))}")
        return 1
    if status == "done":
        print(f"REFUSED: {pid} is already done (all tickets closed)")
        return 1
    unready = packet_readiness(state, live, pid)
    if unready:
        print(
            f"REFUSED: {pid} has unready open tickets "
            f"{', '.join(f'#{ticket}' for ticket in unready)}"
        )
        return 1
    if status == "in-flight":
        print(f"WARN: {pid} already looks in flight (assignee or in-flight label)")
    if status == "deferred":
        preds = sorted(
            e["from"] for e in edges_of(state, "REBUILD-SAVING")
            if e["to"] == pid
            and packet_status_ignoring_r(state, live, e["from"]) != "done"
        )
        print(
            f"WARN: {pid} has unmet REBUILD-SAVING predecessors {preds}; "
            "building now is allowed and costs a rebuild, not correctness"
        )
    for group in state.get("collision_groups", []):
        if pid in group["packets"]:
            others = [
                g for g in group["packets"]
                if g != pid and packet_status(state, live, g) == "in-flight"
            ]
            if others:
                print(
                    f"WARN: collision group {group['name']!r}: {', '.join(others)} "
                    "in flight; serialize, do not build concurrently"
                )
    print(f"CLAIMABLE: {pid} ({', '.join(f'#{t}' for t in packet['tickets'])})")
    return 0


def snapshot_for(tracker, args) -> dict:
    commit = getattr(args, "commit", None) or tracker.default_branch_head()
    date = getattr(args, "date", None) or datetime.date.today().isoformat()
    return {"commit": commit, "date": date}


def cmd_render(tracker, args) -> int:
    if getattr(args, "state", None):
        # Preview a proposed body from a local state file (the pre-init dry
        # run); statuses and frontiers still come from the live tracker.
        with open(args.state, encoding="utf-8") as handle:
            state = json.load(handle)
        if state.get("schema") != SCHEMA:
            raise MapError(f"state schema must be {SCHEMA}")
        require_well_formed(state)
        fatal = validate_shape(state)
        if fatal:
            details = "; ".join(f"{f.kind}: {f.detail}" for f in fatal)
            raise MapError(f"state does not validate: {details}")
    else:
        issue = locate_map(tracker)
        state = extract_state(issue["body"])
    live = Live(tracker, state)
    sys.stdout.write(render(state, live, snapshot_for(tracker, args)))
    return 0


def publish_body(
    tracker,
    number: int,
    state: dict,
    args,
    *,
    expected_state_hash: str | None = None,
    refused_outcomes: tuple[str, ...] = (),
) -> int:
    live = Live(tracker, state)
    body = render(state, live, snapshot_for(tracker, args))
    graph_coverage = verify_mermaid(state, mermaid(state, live))
    accounted = (
        graph_coverage.nodes + graph_coverage.edges + graph_coverage.directives
    )
    print(
        f"Mermaid coverage: {accounted} of {graph_coverage.total} nonblank "
        f"lines accounted; unread remainder {len(graph_coverage.unread)}"
    )
    try:
        tracker_publish_hook.authorize_issue_body(body, f"issue #{number}")
    except ValueError as err:
        record = preserve_refused_outcomes(
            refused_outcomes, issue_number=number, reason=str(err)
        )
        print(f"BODY REFUSED: {err}")
        if record is not None:
            print(f"outcome record: {record}")
        return 1
    if expected_state_hash is not None:
        current = tracker.get_issue(number)
        if state_hash(current["body"]) != expected_state_hash:
            reason = "tracker state block changed after this reconciliation read it"
            record = preserve_refused_outcomes(
                refused_outcomes, issue_number=number, reason=reason
            )
            print(f"STATE CHANGED: refusing to overwrite issue #{number}")
            if record is not None:
                print(f"outcome record: {record}")
            return 1
    tracker.update_issue_body(number, body)
    written = tracker.get_issue(number)
    # A failed read-back is 1, not 2: the write already happened, and 2
    # would claim the run never mutated anything.
    try:
        round_tripped = extract_state(written["body"])
    except MapError as err:
        print(f"READ-BACK FAILED (the write DID happen; inspect issue #{number}): {err}")
        return 1
    if round_tripped != state:
        print(
            "READ-BACK FAILED: state on the tracker differs from what was "
            f"sent (the write DID happen; inspect issue #{number})"
        )
        return 1
    print(f"published: issue #{number}, state intact on read-back")
    return 0


def cmd_publish(tracker, args) -> int:
    issue = locate_map(tracker)
    try:
        with artifact_lock.hold(
            map_artifact(tracker, issue["number"]),
            "implementation-map publish",
            mode="write",
        ):
            current = tracker.get_issue(issue["number"])
            expected = state_hash(current["body"])
            state = extract_state(current["body"])
            return publish_body(
                tracker,
                issue["number"],
                state,
                args,
                expected_state_hash=expected,
            )
    except artifact_lock.ArtifactBusy as err:
        raise MapError(str(err)) from err


def cmd_apply_delta(tracker, args) -> int:
    issue = locate_map(tracker)
    try:
        with artifact_lock.hold(
            map_artifact(tracker, issue["number"]),
            "implementation-map reconciliation",
            mode="write",
        ):
            return _apply_delta_under_lock(tracker, args, issue["number"])
    except artifact_lock.ArtifactBusy as err:
        outcomes = authored_outcomes(args)
        record = preserve_refused_outcomes(
            outcomes, issue_number=issue["number"], reason=str(err)
        )
        print(f"LOCK REFUSED: {err}")
        if record is not None:
            print(f"outcome record: {record}")
        return 1


def authored_outcomes(args) -> tuple[str, ...]:
    """Recover authored outcomes before a lock refusal strands the command."""
    if getattr(args, "outcome", None):
        return (args.outcome,)
    delta_path = getattr(args, "delta", None)
    if not delta_path:
        return ()
    try:
        with open(delta_path, encoding="utf-8") as handle:
            delta = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return ()
    if not isinstance(delta, dict):
        return ()
    return tuple(
        row.get("outcome", "")
        for row in delta.get("add_packets", [])
        if isinstance(row, dict) and isinstance(row.get("outcome", ""), str)
    )


def _apply_delta_under_lock(tracker, args, issue_number: int) -> int:
    current = tracker.get_issue(issue_number)
    expected = state_hash(current["body"])
    state = extract_state(current["body"])
    if args.delta:
        if args.ticket is not None or args.outcome is not None:
            raise MapError("--delta cannot be combined with --ticket or --outcome")
        with open(args.delta, encoding="utf-8") as handle:
            delta = json.load(handle)
    else:
        if args.ticket is None:
            raise MapError("apply-delta needs --delta or --ticket with --outcome")
        delta = _direct_placement_delta(state, tracker, args.ticket, args.outcome)
    new_state = apply_delta(state, delta)
    reviewed_through = getattr(args, "commit", None) or tracker.default_branch_head()
    live = Live(tracker, new_state)
    _, remainder = placement_coverage(new_state, live)
    # The delta is the reconciliation. It may advance the anchor only when
    # its independent ready-ticket population has no unread remainder.
    if not remainder:
        new_state["reconciled_through"] = reviewed_through
    args.commit = reviewed_through
    if args.dry_run:
        findings = validate_shape(new_state) + validate_against_live(new_state, live)
        print("dry run: delta validates; resulting map findings follow")
        report_placement_coverage(state, new_state, live)
        rc = report(findings)
        return 1 if remainder and rc == 0 else rc
    outcomes = tuple(
        row.get("outcome", "") for row in delta.get("add_packets", [])
        if isinstance(row, dict)
    )
    rc = publish_body(
        tracker,
        issue_number,
        new_state,
        args,
        expected_state_hash=expected,
        refused_outcomes=outcomes,
    )
    report_placement_coverage(state, new_state, live)
    if rc == 0:
        # Surface what the applied delta now expects of the tracker -- above
        # all a declared HARD edge whose native mirror the agent still owes.
        live = Live(tracker, new_state)
        findings = validate_shape(new_state) + validate_against_live(new_state, live)
        if findings:
            print("delta applied; live findings follow")
            return report(findings)
    return 1 if remainder and rc == 0 else rc


def cmd_init(tracker, args) -> int:
    try:
        with artifact_lock.hold(
            map_artifact(tracker, 0),
            "implementation-map initialization",
            mode="write",
        ):
            return _init_under_lock(tracker, args)
    except artifact_lock.ArtifactBusy as err:
        raise MapError(str(err)) from err


def _init_under_lock(tracker, args) -> int:
    existing = find_map_issues(tracker)
    if existing:
        numbers = ", ".join(f"#{row['number']}" for row in existing)
        raise MapError(
            f"a map already exists ({numbers}); refusing to create another. "
            "Use apply-delta/publish against it, or adopt it explicitly."
        )
    with open(args.state, encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("schema") != SCHEMA:
        raise MapError(f"initial state schema must be {SCHEMA}")
    require_well_formed(state)
    fatal = validate_shape(state)
    if fatal:
        details = "; ".join(f"{f.kind}: {f.detail}" for f in fatal)
        raise MapError(f"initial state does not validate: {details}")
    if args.adopt:
        number = args.adopt
        rc = publish_body(tracker, number, state, args)
    else:
        live = Live(tracker, state)
        body = render(state, live, snapshot_for(tracker, args))
        try:
            tracker_publish_hook.authorize_issue_body(
                body, "new implementation map issue"
            )
        except ValueError as err:
            raise MapError(str(err)) from err
        number = tracker.create_issue(
            args.title, body, [l for l in (args.label or []) if l]
        )
        written = tracker.get_issue(number)
        try:
            if extract_state(written["body"]) != state:
                print("READ-BACK FAILED: created issue's state differs")
                return 2
        except MapError as err:
            print(f"READ-BACK FAILED: {err}")
            return 2
        rc = 0
        print(f"created: issue #{number}, state intact on read-back")
    if rc == 0:
        live = Live(tracker, state)
        findings = validate_shape(state) + validate_against_live(state, live)
        if findings:
            print("map created; live findings follow")
            return report(findings)
    return rc


def cmd_audit(tracker, args) -> int:
    """Full rebuild-and-compare: every check, plus a diff of the published
    derived sections against a fresh deterministic render."""
    issue = locate_map(tracker)
    state = extract_state(issue["body"])
    live = Live(tracker, state)
    findings = validate_shape(state) + validate_against_live(state, live)
    published = issue["body"]
    snapshot_match = re.search(r"default-branch commit: `([0-9a-f]+)`", published)
    recorded_commit = snapshot_match.group(1) if snapshot_match else "?"
    fresh = render(state, live, {"commit": recorded_commit, "date": "AUDIT"})
    fresh_sections = derived_sections(fresh)
    published_sections = derived_sections(published)
    for name in sorted(set(fresh_sections) | set(published_sections)):
        if fresh_sections.get(name) != published_sections.get(name):
            findings.append(Finding(
                "stale-derived-view",
                f"section {name!r} on the tracker differs from a fresh render; "
                "run publish",
            ))
    head = tracker.default_branch_head()
    if recorded_commit not in ("?",) and not head.startswith(recorded_commit[:7]):
        findings.append(Finding(
            "stale-snapshot",
            f"recorded commit {recorded_commit} is not the default-branch head "
            f"{head}; the map has not been reconciled since",
        ))
    print(f"map: issue #{issue['number']}")
    return report(findings)


def derived_sections(body: str) -> dict[str, str]:
    """Split a rendered body into its ## sections, dropping the snapshot
    (whose date legitimately differs between renders)."""
    sections: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current:
                sections[current] = "\n".join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current:
            lines.append(line)
    if current:
        sections[current] = "\n".join(lines).strip()
    sections.pop("Snapshot", None)
    return sections


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic helper for the implementation-map skill."
    )
    parser.add_argument("--repo", help="owner/name; default: gh repo view")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create or adopt the one coordination issue (mutates)")
    p_init.add_argument("--state", required=True, help="initial state JSON file")
    p_init.add_argument("--title", default="Implementation map")
    p_init.add_argument("--label", action="append", default=[])
    p_init.add_argument("--adopt", type=int, help="stamp an existing issue instead of creating")
    p_init.add_argument("--commit")
    p_init.add_argument("--date")

    sub.add_parser("check", help="read-only: validate map against the live tracker")

    p_claim = sub.add_parser("claim", help="read-only: is this packet startable now?")
    p_claim.add_argument("--packet")
    p_claim.add_argument("--ticket", type=int)

    p_render = sub.add_parser("render", help="read-only: print the derived body")
    p_render.add_argument("--state", help="preview from a local state JSON instead of the live map")
    p_render.add_argument("--commit")
    p_render.add_argument("--date")

    p_pub = sub.add_parser("publish", help="re-render and update the issue (mutates)")
    p_pub.add_argument("--commit")
    p_pub.add_argument("--date")

    p_delta = sub.add_parser("apply-delta", help="validate and apply a reviewed delta (mutates)")
    p_delta.add_argument("--delta", help="reviewed delta JSON file")
    p_delta.add_argument("--ticket", type=int, help="additively place one ready ticket")
    p_delta.add_argument("--outcome", help="authored outcome for --ticket")
    p_delta.add_argument("--dry-run", action="store_true")
    p_delta.add_argument("--commit")
    p_delta.add_argument("--date")

    sub.add_parser("audit", help="read-only: full rebuild-and-compare")
    return parser


def resolve_repo(args) -> str:
    if args.repo:
        return args.repo
    try:
        proc = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
            capture_output=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError as err:
        raise MapError("`gh` is not installed or not on PATH") from err
    if proc.returncode != 0 or not proc.stdout.strip():
        raise MapError("no --repo given and `gh repo view` failed")
    return proc.stdout.strip()


COMMANDS: dict[str, Callable] = {
    "init": cmd_init,
    "check": cmd_check,
    "claim": cmd_claim,
    "render": cmd_render,
    "publish": cmd_publish,
    "apply-delta": cmd_apply_delta,
    "audit": cmd_audit,
}


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        tracker = GitHub(resolve_repo(args))
        return COMMANDS[args.command](tracker, args)
    except MapError as err:
        print(f"did not run: {err}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as err:
        # A missing or unparsable --state/--delta file is a way of not
        # having run; a traceback would exit 1, the findings status.
        print(f"did not run: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
