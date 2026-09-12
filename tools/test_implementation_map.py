"""Fixture tests for implementation_map.py -- no network, ever.

FakeTracker mirrors the five-method surface of the live GitHub adapter
(issues, blocked_by, default_branch_head, get_issue, update_issue_body,
create_issue), so every command can be driven end to end against an
in-memory tracker. The required cases (from the skill's spec): a hard
chain; independent frontier packets; a cycle; an unmapped ready ticket; a
collision edge that never becomes a hard blocker; a declared HARD edge
missing from GitHub; a closed blocker unlocking a packet; malformed or
duplicated state markers; a semantic delta placing new work; and
render -> read-back preserving machine state byte for byte.
"""
from __future__ import annotations

import ast
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artifact_lock_test_support  # noqa: E402, F401
from prose_bind import NAMING, bind  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "implementation_map", HERE / "implementation_map.py"
)
imap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(imap)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def issue(number, *, title="ticket", state="open", labels=(), assignees=(),
          body=""):
    return {
        "number": number,
        "title": title,
        "state": state,
        "labels": sorted(labels),
        "assignees": sorted(assignees),
        "body": body,
    }


class FakeTracker:
    """In-memory mirror of implementation_map.GitHub's method surface."""

    def __init__(self, rows, blocked=None, head="abc1234"):
        self.rows = {row["number"]: row for row in rows}
        self.blocked = {k: sorted(v) for k, v in (blocked or {}).items()}
        self.head = head
        self.created = []

    def issues(self):
        return [dict(row) for row in self.rows.values()]

    def blocked_by(self, number):
        return list(self.blocked.get(number, []))

    def default_branch_head(self):
        return self.head

    def get_issue(self, number):
        return dict(self.rows[number])

    def update_issue_body(self, number, body):
        self.rows[number]["body"] = body

    def create_issue(self, title, body, labels):
        number = max(self.rows, default=100) + 1
        self.rows[number] = issue(number, title=title, labels=labels, body=body)
        self.created.append(number)
        return number


def packet(pid, tickets, title="", outcome=""):
    return {"id": pid, "tickets": list(tickets), "title": title,
            "outcome": outcome}


def state_with(packets_, edges=None, groups=None, exclusions=None, **extra):
    state = {
        "schema": imap.SCHEMA,
        "repo": "o/r",
        "packets": packets_,
        "edges": edges or [],
        "collision_groups": groups or [],
        "exclusions": exclusions or [],
        "ready_labels": ["ready"],
        "in_flight_labels": ["in-flight"],
    }
    state.update(extra)
    return state


def hard(src, dst):
    return {"type": "HARD", "from_ticket": src, "to_ticket": dst}


def saving(src, dst):
    return {"type": "REBUILD-SAVING", "from": src, "to": dst}


def gate(on, to):
    return {"type": "EXTERNAL-GATE", "on": on, "to": to}


def map_issue(state, number=1):
    live = FakeTracker([])  # placeholder; render needs a Live over the state
    del live
    body = imap.state_block(state)
    return issue(number, title="Implementation map", body=body)


def args(**kw):
    defaults = {"commit": "abc1234", "date": "2026-08-27", "packet": None,
                "ticket": None, "dry_run": False, "delta": None,
                "outcome": None}
    defaults.update(kw)
    return SimpleNamespace(**defaults)


def run(fn, tracker, ns):
    out = io.StringIO()
    with redirect_stdout(out):
        rc = fn(tracker, ns)
    return rc, out.getvalue()


def revision_body(state, writer, superseded):
    return (
        imap.state_block(state)
        + "\n\n## Snapshot\n\n"
        + f"- writer: `{writer}`\n"
        + f"- superseded state: `sha256:{superseded}`\n"
    )


def replace_in_function(source, function_name, old, new):
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    lines = source.splitlines(keepends=True)
    start = function.lineno - 1
    end = function.end_lineno
    segment = "".join(lines[start:end])
    if old not in segment:
        raise AssertionError(f"{old!r} not found in {function_name}")
    lines[start:end] = [segment.replace(old, new, 1)]
    return "".join(lines)


def map_overwriter_obligations(source):
    """Walk direct call sites; calls assembled by indirection are invisible."""
    tree = ast.parse(source)
    functions = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    calls = {}
    for name, function in functions.items():
        called = set()
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                called.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)
        calls[name] = called

    def reachable(name):
        found = set()
        pending = [name]
        while pending:
            current = pending.pop()
            if current in found:
                continue
            found.add(current)
            pending.extend(calls.get(current, ()) & functions.keys())
        return found

    def has_lock(names):
        for name in names:
            for node in ast.walk(functions[name]):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr != "hold" or not node.args:
                    continue
                artifact = node.args[0]
                if (
                    isinstance(artifact, ast.Call)
                    and isinstance(artifact.func, ast.Name)
                    and artifact.func.id == "map_artifact"
                    and len(artifact.args) == 2
                    and not (
                        isinstance(artifact.args[1], ast.Constant)
                        and artifact.args[1].value == 0
                    )
                ):
                    return True
        return False

    def has_keyword(names, function_name, keyword):
        return any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == function_name
            and any(item.arg == keyword for item in node.keywords)
            for name in names
            for node in ast.walk(functions[name])
        )

    def has_call(names, function_name):
        return any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == function_name
            for name in names
            for node in ast.walk(functions[name])
        )

    overwriters = {}
    for root in sorted(name for name in functions if name.startswith("cmd_")):
        names = reachable(root)
        if not any("update_issue_body" in calls.get(name, ()) for name in names):
            continue
        label = "cmd_init --adopt" if root == "cmd_init" else root
        overwriters[label] = {
            "map-lock": has_lock(names),
            "state-hash": has_keyword(names, "publish_body", "expected_state_hash"),
            "revalidation": has_call(names, "revalidate_after_publish"),
        }
    return overwriters


# ---------------------------------------------------------------------------
# State block round trip
# ---------------------------------------------------------------------------

class TheStateBlockRoundTrips(unittest.TestCase):
    def test_state_block_alone(self):
        state = state_with([packet("PA", [1])], edges=[hard(1, 1)])
        body = "prose above\n" + imap.state_block(state) + "\nprose below"
        self.assertEqual(imap.extract_state(body), state)

    def test_full_render_preserves_state(self):
        """Case 10: render -> extract gives back the exact machine state."""
        state = state_with(
            [packet("PA", [1], title="first"), packet("PB", [2])],
            edges=[hard(1, 2), saving("PA", "PB")],
            groups=[{"name": "seam", "packets": ["PA", "PB"], "why": "shared"}],
            exclusions=[{"ticket": 9, "why": "grilling"}],
        )
        tracker = FakeTracker(
            [issue(1), issue(2), issue(9, labels=["ready"])],
            blocked={2: [1]},
        )
        live = imap.Live(tracker, state)
        body = imap.render(state, live, {"commit": "abc1234", "date": "D"})
        self.assertEqual(imap.extract_state(body), state)

    def test_render_is_deterministic(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])],
                           edges=[hard(1, 2)])
        tracker = FakeTracker([issue(1), issue(2)], blocked={2: [1]})
        one = imap.render(state, imap.Live(tracker, state),
                          {"commit": "c", "date": "d"})
        two = imap.render(state, imap.Live(tracker, state),
                          {"commit": "c", "date": "d"})
        self.assertEqual(one, two)


# ---------------------------------------------------------------------------
# Malformed and duplicated markers (case 8)
# ---------------------------------------------------------------------------

class MalformedStateMarkers(unittest.TestCase):
    def test_no_marker(self):
        with self.assertRaises(imap.MapError):
            imap.extract_state("a body with no state block at all")

    def test_duplicated_markers(self):
        block = imap.state_block(state_with([]))
        with self.assertRaises(imap.MapError):
            imap.extract_state(block + "\n" + block)

    def test_unterminated_block(self):
        with self.assertRaises(imap.MapError):
            imap.extract_state(imap.STATE_BEGIN + "\n```json\n{}\n```")

    def test_end_before_begin(self):
        with self.assertRaises(imap.MapError):
            imap.extract_state(imap.STATE_END + "\n" + imap.STATE_BEGIN)

    def test_no_fence(self):
        with self.assertRaises(imap.MapError):
            imap.extract_state(imap.STATE_BEGIN + " {} " + imap.STATE_END)

    def test_json_does_not_parse(self):
        body = f"{imap.STATE_BEGIN}\n```json\nnot json\n```\n{imap.STATE_END}"
        with self.assertRaises(imap.MapError):
            imap.extract_state(body)

    def test_wrong_schema(self):
        body = f"{imap.STATE_BEGIN}\n```json\n{{\"schema\": 99}}\n```\n{imap.STATE_END}"
        with self.assertRaises(imap.MapError):
            imap.extract_state(body)

    def test_zero_maps_is_did_not_run(self):
        tracker = FakeTracker([issue(1)])
        with self.assertRaises(imap.MapError):
            imap.locate_map(tracker)

    def test_two_maps_is_did_not_run(self):
        state = state_with([])
        tracker = FakeTracker([map_issue(state, 1), map_issue(state, 2)])
        with self.assertRaises(imap.MapError):
            imap.locate_map(tracker)


# ---------------------------------------------------------------------------
# A hard chain (case 1)
# ---------------------------------------------------------------------------

class AHardChain(unittest.TestCase):
    """PA(#1) -> PB(#2) -> PC(#3), every HARD edge mirrored natively."""

    def setUp(self):
        self.state = state_with(
            [packet("PA", [1]), packet("PB", [2]), packet("PC", [3])],
            edges=[hard(1, 2), hard(2, 3)],
        )
        self.tracker = FakeTracker(
            [issue(1, labels=["ready"]), issue(2, labels=["ready"]),
             issue(3, labels=["ready"])],
            blocked={2: [1], 3: [2]},
        )
        self.live = imap.Live(self.tracker, self.state)

    def test_statuses(self):
        self.assertEqual(imap.packet_status(self.state, self.live, "PA"), "ready")
        self.assertEqual(imap.packet_status(self.state, self.live, "PB"), "blocked")
        self.assertEqual(imap.packet_status(self.state, self.live, "PC"), "blocked")

    def test_frontiers_peel_one_at_a_time(self):
        self.assertEqual(imap.frontiers(self.state, self.live),
                         [["PA"], ["PB"], ["PC"]])

    def test_check_is_clean(self):
        findings = (imap.validate_shape(self.state)
                    + imap.validate_against_live(self.state, self.live))
        self.assertEqual(findings, [])

    def test_claim_refuses_the_blocked_middle(self):
        tracker = FakeTracker(self.tracker.issues() + [map_issue(self.state, 50)],
                              blocked=self.tracker.blocked)
        rc, out = run(imap.cmd_claim, tracker, args(packet="PB"))
        self.assertEqual(rc, 1)
        self.assertIn("REFUSED", out)
        self.assertIn("#1", out)


# ---------------------------------------------------------------------------
# Independent packets share a frontier (case 2)
# ---------------------------------------------------------------------------

class IndependentFrontierPackets(unittest.TestCase):
    def test_all_startable_at_once(self):
        state = state_with([packet("PA", [1]), packet("PB", [2]),
                            packet("PC", [3])])
        tracker = FakeTracker([
            issue(1, labels=["ready"]),
            issue(2, labels=["ready"]),
            issue(3, labels=["ready"]),
        ])
        live = imap.Live(tracker, state)
        self.assertEqual(imap.frontiers(state, live), [["PA", "PB", "PC"]])


# ---------------------------------------------------------------------------
# A cycle (case 3)
# ---------------------------------------------------------------------------

class ACycleIsAFindingNotAHang(unittest.TestCase):
    def setUp(self):
        self.state = state_with(
            [packet("PA", [1]), packet("PB", [2]), packet("PC", [3])],
            edges=[hard(1, 2), hard(2, 3), hard(3, 1)],
        )

    def test_cycle_reported(self):
        kinds = [f.kind for f in imap.validate_shape(self.state)]
        self.assertIn("cycle", kinds)

    def test_frontiers_terminate(self):
        tracker = FakeTracker([issue(1), issue(2), issue(3)],
                              blocked={1: [3], 2: [1], 3: [2]})
        live = imap.Live(tracker, self.state)
        self.assertEqual(imap.frontiers(self.state, live), [])

    def test_a_delta_may_not_create_one(self):
        clean = state_with(
            [packet("PA", [1]), packet("PB", [2])], edges=[hard(1, 2)]
        )
        with self.assertRaises(imap.MapError):
            imap.apply_delta(clean, {"add_edges": [hard(2, 1)]})


# ---------------------------------------------------------------------------
# Unmapped ready ticket (case 4)
# ---------------------------------------------------------------------------

class AnUnmappedReadyTicket(unittest.TestCase):
    def test_reported_unless_excluded(self):
        state = state_with([packet("PA", [1])])
        tracker = FakeTracker([issue(1, labels=["ready"]),
                               issue(2, labels=["ready"])])
        live = imap.Live(tracker, state)
        kinds = [f.kind for f in imap.validate_against_live(state, live)]
        self.assertIn("unmapped-ready", kinds)

        excused = state_with([packet("PA", [1])],
                             exclusions=[{"ticket": 2, "why": "grilling"}])
        live = imap.Live(tracker, excused)
        self.assertEqual(imap.validate_against_live(excused, live), [])

    def test_the_map_issue_itself_is_not_unmapped(self):
        state = state_with([packet("PA", [1])])
        rows = [issue(1, labels=["ready"]),
                issue(7, labels=["ready"], body=imap.state_block(state))]
        live = imap.Live(FakeTracker(rows), state)
        self.assertEqual(imap.validate_against_live(state, live), [])

    def test_in_flight_without_a_packet_is_reported(self):
        state = state_with([packet("PA", [1])])
        tracker = FakeTracker([issue(1), issue(3, assignees=["someone"])])
        live = imap.Live(tracker, state)
        kinds = [f.kind for f in imap.validate_against_live(state, live)]
        self.assertIn("unmapped-in-flight", kinds)

    def test_a_mapped_ticket_missing_from_the_tracker_is_reported(self):
        state = state_with([packet("PA", [1, 2])])
        live = imap.Live(FakeTracker([issue(1)]), state)
        kinds = [f.kind for f in imap.validate_against_live(state, live)]
        self.assertIn("unknown-ticket", kinds)

    def test_open_mapped_ticket_without_a_ready_label_is_reported(self):
        state = state_with([packet("PA", [1, 2])])
        live = imap.Live(
            FakeTracker([issue(1), issue(2, state="closed")]),
            state,
        )

        findings = imap.validate_against_live(state, live)
        mapped_not_ready = [
            finding for finding in findings
            if finding.kind == "mapped-not-ready"
        ]

        self.assertEqual(len(mapped_not_ready), 1)
        self.assertIn("#1", mapped_not_ready[0].detail)
        self.assertNotIn("#2", mapped_not_ready[0].detail)


class AnUnreadyPacketCannotBeClaimed(unittest.TestCase):
    def setUp(self):
        state = state_with([packet("PA", [1, 2, 3])])
        rows = [
            issue(1, labels=["ready"]),
            issue(2, assignees=["someone"]),
            issue(3, state="closed"),
            map_issue(state, 50),
        ]
        self.state = state
        self.tracker = FakeTracker(rows)
        self.live = imap.Live(self.tracker, state)

    def test_readiness_names_only_open_unready_tickets(self):
        self.assertEqual(
            imap.packet_readiness(self.state, self.live, "PA"),
            [2],
        )

    def test_claim_refuses_before_the_in_flight_warning(self):
        rc, out = run(imap.cmd_claim, self.tracker, args(packet="PA"))

        self.assertEqual(rc, 1)
        self.assertIn("REFUSED", out)
        self.assertIn("unready", out)
        self.assertNotIn("WARN", out)
        self.assertIn("#2", out)
        self.assertNotIn("#3", out)

    def test_blocked_refusal_precedes_unready(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            edges=[hard(1, 2)],
        )
        rows = [issue(1), issue(2), map_issue(state, 50)]
        tracker = FakeTracker(rows, blocked={2: [1]})

        rc, out = run(imap.cmd_claim, tracker, args(packet="PB"))

        self.assertEqual(rc, 1)
        self.assertIn("blocked", out)
        self.assertNotIn("unready", out)

    def test_gated_refusal_precedes_unready(self):
        state = state_with(
            [packet("PA", [1])],
            edges=[gate("issue:99", "PA")],
        )
        rows = [issue(1), issue(99), map_issue(state, 50)]
        tracker = FakeTracker(rows)

        rc, out = run(imap.cmd_claim, tracker, args(packet="PA"))

        self.assertEqual(rc, 1)
        self.assertIn("gated", out)
        self.assertNotIn("unready", out)


# ---------------------------------------------------------------------------
# Collision edges never block (case 5)
# ---------------------------------------------------------------------------

class ACollisionIsNotABlocker(unittest.TestCase):
    def setUp(self):
        self.state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared_file.py", "kind": "unordered",
                     "packets": ["PA", "PB"],
                     "why": "same module"}],
        )

    def test_both_stay_ready_and_share_the_frontier(self):
        tracker = FakeTracker([
            issue(1, labels=["ready"]),
            issue(2, labels=["ready"]),
        ])
        live = imap.Live(tracker, self.state)
        self.assertEqual(imap.packet_status(self.state, live, "PA"), "ready")
        self.assertEqual(imap.packet_status(self.state, live, "PB"), "ready")
        self.assertEqual(imap.frontiers(self.state, live), [["PA", "PB"]])

    def test_claim_warns_but_allows_when_the_other_is_in_flight(self):
        rows = [issue(1, labels=["ready"], assignees=["someone"]),
                issue(2, labels=["ready"]),
                map_issue(self.state, 50)]
        rc, out = run(imap.cmd_claim, FakeTracker(rows), args(packet="PB"))
        self.assertEqual(rc, 0)
        self.assertIn("WARN", out)
        self.assertIn("collision", out)
        self.assertIn("CLAIMABLE", out)

    def test_no_native_edge_is_demanded(self):
        tracker = FakeTracker([
            issue(1, labels=["ready"]),
            issue(2, labels=["ready"]),
        ])
        live = imap.Live(tracker, self.state)
        self.assertEqual(imap.validate_against_live(self.state, live), [])


class CollisionKindControlsStartability(unittest.TestCase):
    def test_unclassified_group_over_constrains_by_its_stored_order(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared", "packets": ["PA", "PB"]}],
        )
        live = imap.Live(FakeTracker([
            issue(1, labels=["ready"]), issue(2, labels=["ready"]),
        ]), state)

        self.assertEqual(imap.frontiers(state, live), [["PA"], ["PB"]])

    def test_claim_refuses_an_unmet_ruled_sequence(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{
                "name": "shared", "kind": "sequence", "packets": ["PA", "PB"],
            }],
        )
        rows = [
            issue(1, labels=["ready"]), issue(2, labels=["ready"]),
            map_issue(state, 50),
        ]

        rc, out = run(imap.cmd_claim, FakeTracker(rows), args(packet="PB"))

        self.assertEqual(rc, 1)
        self.assertIn("REFUSED", out)
        self.assertIn("sequence", out)
        self.assertIn("shared", out)
        self.assertIn("PA", out)

    def test_claim_warns_on_an_unclassified_predecessor(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared", "packets": ["PA", "PB"]}],
        )
        rows = [
            issue(1, labels=["ready"]), issue(2, labels=["ready"]),
            map_issue(state, 50),
        ]

        rc, out = run(imap.cmd_claim, FakeTracker(rows), args(packet="PB"))

        self.assertEqual(rc, 0)
        self.assertIn("WARN", out)
        self.assertIn("unclassified", out)
        self.assertIn("shared", out)
        self.assertIn("CLAIMABLE", out)

    def test_two_not_done_members_demand_a_collision_kind(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared", "packets": ["PA", "PB"]}],
        )
        live = imap.Live(FakeTracker([issue(1), issue(2)]), state)

        findings = imap.validate_against_live(state, live)

        finding = next(f for f in findings if f.kind == "unclassified-collision")
        self.assertIn("shared", finding.detail)
        self.assertIn("PA", finding.detail)
        self.assertIn("PB", finding.detail)

    def test_one_not_done_member_does_not_demand_a_collision_kind(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared", "packets": ["PA", "PB"]}],
        )
        live = imap.Live(FakeTracker([
            issue(1, state="closed"), issue(2),
        ]), state)

        kinds = [f.kind for f in imap.validate_against_live(state, live)]

        self.assertNotIn("unclassified-collision", kinds)

    def test_live_sequence_cycle_is_a_collision_finding(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            edges=[hard(2, 1)],
            groups=[{
                "name": "shared", "kind": "sequence", "packets": ["PA", "PB"],
            }],
        )
        live = imap.Live(FakeTracker([issue(1), issue(2)]), state)

        kinds = [f.kind for f in imap.validate_against_live(state, live)]

        self.assertIn("collision-cycle", kinds)

    def test_finished_member_removes_a_collision_derived_cycle(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            edges=[hard(2, 1)],
            groups=[{
                "name": "shared", "kind": "sequence", "packets": ["PA", "PB"],
            }],
        )
        live = imap.Live(FakeTracker([
            issue(1), issue(2, state="closed"),
        ]), state)

        kinds = [f.kind for f in imap.validate_against_live(state, live)]

        self.assertNotIn("collision-cycle", kinds)


# ---------------------------------------------------------------------------
# HARD-vs-native drift (case 6)
# ---------------------------------------------------------------------------

class HardEdgeNativeDrift(unittest.TestCase):
    def test_declared_but_not_native(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])],
                           edges=[hard(1, 2)])
        live = imap.Live(FakeTracker([issue(1), issue(2)]), state)
        findings = imap.validate_against_live(state, live)
        kinds = [f.kind for f in findings]
        self.assertIn("hard-edge-not-native", kinds)
        remedy = next(f for f in findings if f.kind == "hard-edge-not-native").remedy
        self.assertIn("gh api", remedy)

    def test_native_but_not_declared(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])])
        live = imap.Live(FakeTracker([issue(1), issue(2)], blocked={2: [1]}),
                         state)
        kinds = [f.kind for f in imap.validate_against_live(state, live)]
        self.assertIn("native-edge-undeclared", kinds)

    def test_native_edge_from_off_map_ticket_is_not_drift(self):
        """A native blocker outside the map is a gate, not drift."""
        state = state_with([packet("PA", [1])])
        live = imap.Live(FakeTracker(
            [issue(1, labels=["ready"]), issue(99)],
            blocked={1: [99]},
        ),
                         state)
        self.assertEqual(imap.validate_against_live(state, live), [])

    def test_an_open_off_map_blocker_gates_the_packet(self):
        state = state_with([packet("PA", [1])])
        live = imap.Live(FakeTracker([issue(1), issue(99)], blocked={1: [99]}),
                         state)
        self.assertEqual(imap.packet_status(state, live, "PA"), "gated")


# ---------------------------------------------------------------------------
# A closed blocker unlocks a packet (case 7)
# ---------------------------------------------------------------------------

class AClosedBlockerUnlocks(unittest.TestCase):
    def test_done_predecessor_frees_the_successor(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])],
                           edges=[hard(1, 2)])
        tracker = FakeTracker([
            issue(1, state="closed"),
            issue(2, labels=["ready"]),
        ],
                              blocked={2: [1]})
        live = imap.Live(tracker, state)
        self.assertEqual(imap.packet_status(state, live, "PA"), "done")
        self.assertEqual(imap.packet_status(state, live, "PB"), "ready")
        self.assertEqual(imap.frontiers(state, live), [["PB"]])

    def test_gate_on_a_closed_issue_is_cleared(self):
        state = state_with([packet("PA", [1])],
                           edges=[gate("issue:99", "PA")])
        live = imap.Live(FakeTracker([issue(1), issue(99, state="closed")]),
                         state)
        self.assertEqual(imap.packet_status(state, live, "PA"), "ready")

    def test_gate_on_an_open_issue_holds(self):
        state = state_with([packet("PA", [1])],
                           edges=[gate("issue:99", "PA")])
        live = imap.Live(FakeTracker([issue(1), issue(99)]), state)
        self.assertEqual(imap.packet_status(state, live, "PA"), "gated")

    def test_a_non_issue_gate_never_clears_mechanically(self):
        state = state_with([packet("PA", [1])],
                           edges=[gate("clinician ruling", "PA")])
        live = imap.Live(FakeTracker([issue(1)]), state)
        self.assertEqual(imap.packet_status(state, live, "PA"), "gated")


# ---------------------------------------------------------------------------
# Rebuild-saving edges defer, never block
# ---------------------------------------------------------------------------

class RebuildSavingDefersButNeverBlocks(unittest.TestCase):
    def setUp(self):
        self.state = state_with([packet("PA", [1]), packet("PB", [2])],
                                edges=[saving("PA", "PB")])

    def test_status_and_frontier(self):
        live = imap.Live(FakeTracker([
            issue(1, labels=["ready"]),
            issue(2, labels=["ready"]),
        ]), self.state)
        self.assertEqual(imap.packet_status(self.state, live, "PB"), "deferred")
        self.assertEqual(imap.frontiers(self.state, live), [["PA"], ["PB"]])

    def test_claim_warns_but_allows(self):
        rows = [issue(1, labels=["ready"]), issue(2, labels=["ready"]),
                map_issue(self.state, 50)]
        rc, out = run(imap.cmd_claim, FakeTracker(rows), args(packet="PB"))
        self.assertEqual(rc, 0)
        self.assertIn("WARN", out)
        self.assertIn("rebuild", out)

    def test_done_predecessor_lifts_the_deferral(self):
        live = imap.Live(FakeTracker([issue(1, state="closed"), issue(2)]),
                         self.state)
        self.assertEqual(imap.packet_status(self.state, live, "PB"), "ready")


# ---------------------------------------------------------------------------
# Gated predecessors hold their successors back
# ---------------------------------------------------------------------------

class AGatedPredecessorHoldsItsSuccessors(unittest.TestCase):
    def test_successor_never_reads_startable(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])],
                           edges=[hard(1, 2), gate("issue:99", "PA")])
        tracker = FakeTracker([issue(1), issue(2), issue(99)],
                              blocked={2: [1]})
        live = imap.Live(tracker, state)
        fronts = imap.frontiers(state, live)
        for layer in fronts:
            self.assertNotIn("PA", layer)
            self.assertNotIn("PB", layer)


# ---------------------------------------------------------------------------
# Deltas (case 9)
# ---------------------------------------------------------------------------

class ADeltaPlacesNewWork(unittest.TestCase):
    """The semantic placement an ADR's closeout supplies: new packet, new
    ticket, new edges -- validated, applied, and refused when incoherent."""

    def setUp(self):
        self.state = state_with([packet("PA", [1]), packet("PB", [2])],
                                edges=[hard(1, 2)])

    def test_add_a_packet_with_edges(self):
        delta = {
            "note": "ADR 0099 opened #3",
            "add_packets": [packet("PC", [3], outcome="Build the ruled tool")],
            "add_edges": [hard(2, 3), saving("PA", "PC")],
        }
        new = imap.apply_delta(self.state, delta)
        self.assertEqual(imap.packet_of(new, 3), "PC")
        self.assertEqual(len(new["edges"]), 3)
        # the original is untouched (pure function)
        self.assertEqual(len(self.state["edges"]), 1)

    def test_add_ticket_to_existing_packet(self):
        new = imap.apply_delta(
            self.state, {"add_tickets": [{"packet": "PA", "ticket": 4}]}
        )
        self.assertEqual(imap.packet_of(new, 4), "PA")

    def test_duplicate_membership_refused(self):
        with self.assertRaises(imap.MapError):
            imap.apply_delta(
                self.state, {"add_tickets": [{"packet": "PB", "ticket": 1}]}
            )
        with self.assertRaises(imap.MapError):
            imap.apply_delta(self.state, {"add_packets": [packet("PD", [1])]})

    def test_unknown_keys_refused(self):
        with self.assertRaises(imap.MapError):
            imap.apply_delta(self.state, {"packets": []})

    def test_removing_a_packet_takes_its_edges_along(self):
        new = imap.apply_delta(self.state, {"remove_packets": ["PB"]})
        self.assertEqual(imap.packet_ids(new), ["PA"])
        self.assertEqual(new["edges"], [])

    def test_removing_a_packet_in_a_collision_group(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "g", "packets": ["PA", "PB"]}],
        )
        new = imap.apply_delta(state, {"remove_packets": ["PB"]})
        self.assertEqual(new["collision_groups"][0]["packets"], ["PA"])

    def test_exclusions_add_and_remove(self):
        new = imap.apply_delta(
            self.state, {"add_exclusions": [{"ticket": 9, "why": "grilling"}]}
        )
        self.assertIn(9, imap.excluded_tickets(new))
        back = imap.apply_delta(new, {"remove_exclusions": [9]})
        self.assertNotIn(9, imap.excluded_tickets(back))
        with self.assertRaises(imap.MapError):
            imap.apply_delta(self.state, {"remove_exclusions": [9]})

    def test_excluding_a_mapped_ticket_refused(self):
        with self.assertRaises(imap.MapError):
            imap.apply_delta(
                self.state, {"add_exclusions": [{"ticket": 1, "why": "no"}]}
            )

    def test_hard_edge_to_an_unmapped_ticket_refused(self):
        with self.assertRaises(imap.MapError):
            imap.apply_delta(self.state, {"add_edges": [hard(2, 77)]})

    def test_a_new_packet_needs_an_authored_outcome(self):
        for outcome in ("", "   "):
            with self.subTest(outcome=outcome):
                with self.assertRaisesRegex(imap.MapError, "blank outcome"):
                    imap.apply_delta(
                        self.state,
                        {"add_packets": [packet("PC", [3], outcome=outcome)]},
                    )

    def test_replaying_the_same_additive_placement_is_inert(self):
        delta = {
            "add_packets": [packet("PC", [3], outcome="Build ruled work")],
            "add_edges": [hard(2, 3)],
        }
        once = imap.apply_delta(self.state, delta)

        twice = imap.apply_delta(once, delta)

        self.assertEqual(twice, once)

    def test_reusing_a_packet_id_for_different_work_still_refuses(self):
        placed = imap.apply_delta(
            self.state,
            {"add_packets": [packet("PC", [3], outcome="First judgment")]},
        )

        with self.assertRaisesRegex(imap.MapError, "already exists"):
            imap.apply_delta(
                placed,
                {"add_packets": [packet("PC", [4], outcome="Different judgment")]},
            )

    def test_set_collision_kind_can_author_sequence_order(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared", "packets": ["PA", "PB"]}],
        )

        new = imap.apply_delta(state, {"set_collision_kind": [{
            "name": "shared", "kind": "sequence", "packets": ["PB", "PA"],
        }]})

        self.assertEqual(new["collision_groups"][0]["kind"], "sequence")
        self.assertEqual(new["collision_groups"][0]["packets"], ["PB", "PA"])

    def test_set_collision_kind_refuses_membership_changes(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2]), packet("PC", [3])],
            groups=[{"name": "shared", "packets": ["PA", "PB"]}],
        )

        with self.assertRaisesRegex(imap.MapError, "permutation"):
            imap.apply_delta(state, {"set_collision_kind": [{
                "name": "shared", "kind": "sequence", "packets": ["PA", "PC"],
            }]})

    def test_set_collision_kind_refuses_non_packet_id_members(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared", "packets": ["PA", "PB"]}],
        )

        with self.assertRaisesRegex(imap.MapError, "permutation"):
            imap.apply_delta(state, {"set_collision_kind": [{
                "name": "shared", "kind": "sequence", "packets": ["PA", 7],
            }]})

    def test_unordered_collision_members_are_stored_by_packet_id(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{"name": "shared", "packets": ["PB", "PA"]}],
        )

        new = imap.apply_delta(state, {"set_collision_kind": [{
            "name": "shared", "kind": "unordered",
        }]})

        self.assertEqual(new["collision_groups"][0], {
            "name": "shared", "kind": "unordered", "packets": ["PA", "PB"],
        })


# ---------------------------------------------------------------------------
# Publish and read-back (case 10, mutating half)
# ---------------------------------------------------------------------------

class PublishReadsItselfBack(unittest.TestCase):
    def setUp(self):
        self.state = state_with([packet("PA", [1]), packet("PB", [2])],
                                edges=[hard(1, 2)])
        self.rows = [issue(1, labels=["ready"]), issue(2, labels=["ready"]),
                     map_issue(self.state, 50)]

    def test_publish_round_trips(self):
        tracker = FakeTracker(self.rows, blocked={2: [1]})
        rc, out = run(imap.cmd_publish, tracker, args())
        self.assertEqual(rc, 0)
        self.assertIn("read-back", out)
        self.assertRegex(
            out,
            r"Mermaid coverage: \d+ of \d+ nonblank lines accounted; unread remainder 0",
        )
        self.assertIn(
            "Packet coverage: 2 drawn + 0 omitted free-standing = 2 of 2; "
            "unread remainder 0",
            out,
        )
        self.assertEqual(imap.extract_state(tracker.rows[50]["body"]),
                         self.state)

    def test_publish_acquires_the_shared_artifact_lock(self):
        tracker = FakeTracker(self.rows, blocked={2: [1]})
        with mock.patch.object(
            imap.artifact_lock, "hold", wraps=imap.artifact_lock.hold
        ) as hold:
            rc, out = run(imap.cmd_publish, tracker, args())

        self.assertEqual(rc, 0, out)
        hold.assert_called_once()
        self.assertEqual(hold.call_args.kwargs, {"mode": "write"})

    def test_publish_crosses_the_shared_tracker_body_gate(self):
        tracker = FakeTracker(
            [
                issue(1, labels=["ready"]),
                issue(2, labels=["ready"]),
                map_issue(self.state, 596),
            ],
            blocked={2: [1]},
        )
        with mock.patch.object(
            imap.tracker_publish_hook, "authorize_issue_body"
        ) as authorize:
            rc, out = run(imap.cmd_publish, tracker, args())

        self.assertEqual(rc, 0, out)
        authorize.assert_called_once()
        self.assertEqual(authorize.call_args.args[1], "issue #596")
        self.assertEqual(authorize.call_args.kwargs, {"issue_number": 596})

    def test_publish_revalidates_and_names_an_unmapped_ready_ticket(self):
        tracker = FakeTracker(
            self.rows + [issue(3, labels=["ready"])],
            blocked={2: [1]},
        )

        rc, out = run(imap.cmd_publish, tracker, args())

        self.assertEqual(rc, 1, out)
        self.assertIn("FINDING unmapped-ready", out)
        self.assertIn("#3", out)

    def test_successful_publish_harvests_the_revision_chain(self):
        tracker = FakeTracker(self.rows, blocked={2: [1]})
        tracker.user_content_edits = mock.Mock(return_value="history")
        with mock.patch.object(imap, "harvest_revision_chain") as harvest:
            rc, out = run(imap.cmd_publish, tracker, args())

        self.assertEqual(rc, 0, out)
        harvest.assert_called_once_with("history")

    def test_apply_delta_without_an_adr_review_does_not_move_the_floor(self):
        tracker = FakeTracker(self.rows, blocked={2: [1]}, head="feed123")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "delta.json"
            path.write_text(json.dumps({"note": "reviewed placement"}), encoding="utf-8")
            rc, out = run(
                imap.cmd_apply_delta,
                tracker,
                args(delta=str(path), commit=None),
            )
        self.assertEqual(rc, 0, out)
        written = imap.extract_state(tracker.rows[50]["body"])
        self.assertNotIn("reconciled_through", written)

    def test_apply_delta_places_one_newly_ready_ticket_without_json_surgery(self):
        state = state_with(
            [packet("PA", [1], outcome="Build predecessor")],
            reconciled_through="old1234",
        )
        tracker = FakeTracker(
            [
                issue(1, title="Predecessor", labels=["ready"]),
                issue(3, title="New ruled work", labels=["ready"]),
                map_issue(state, 50),
            ],
            blocked={3: [1]},
            head="feed123",
        )

        rc, out = run(
            imap.cmd_apply_delta,
            tracker,
            args(
                commit=None,
                ticket=3,
                outcome="Build the newly ruled behavior",
            ),
        )

        self.assertEqual(rc, 0, out)
        written = imap.extract_state(tracker.rows[50]["body"])
        self.assertEqual(
            next(row for row in written["packets"] if row["id"] == "P3"),
            packet(
                "P3",
                [3],
                title="New ruled work",
                outcome="Build the newly ruled behavior",
            ),
        )
        self.assertIn(hard(1, 3), written["edges"])
        self.assertIn("packets written: 1", out)
        self.assertIn("ready tickets still unmapped: 0", out)

    def test_partial_reconciliation_writes_progress_but_holds_the_anchor(self):
        state = state_with(
            [packet("PA", [1], outcome="Build predecessor")],
            reconciled_through="old1234",
        )
        tracker = FakeTracker(
            [
                issue(1, labels=["ready"]),
                issue(3, labels=["ready"]),
                issue(4, labels=["ready"]),
                map_issue(state, 50),
            ],
            head="feed123",
        )

        rc, out = run(
            imap.cmd_apply_delta,
            tracker,
            args(
                commit=None,
                ticket=3,
                outcome="Build one of the ruled packets",
            ),
        )

        self.assertEqual(rc, 1, out)
        written = imap.extract_state(tracker.rows[50]["body"])
        self.assertEqual(imap.packet_of(written, 3), "P3")
        self.assertEqual(written["reconciled_through"], "old1234")
        self.assertIn("ready ticket population: 3", out)
        self.assertIn("ready tickets still unmapped: 1: #4", out)
        self.assertIn("reconciled_through: old1234", out)

    def test_adr_review_advances_the_floor_while_another_ready_ticket_is_unmapped(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Map Tests"], cwd=root, check=True)
            (root / "seed.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
            floor = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            ).stdout.strip()
            adr = root / "docs" / "adr" / "0168-decision.md"
            adr.parent.mkdir(parents=True)
            adr.write_text("# Decision\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "ADR"], cwd=root, check=True)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            ).stdout.strip()
            state = state_with(
                [packet("PA", [1], outcome="Existing work")],
                reconciled_through=floor,
            )
            tracker = FakeTracker(
                [
                    issue(1, labels=["ready"]),
                    issue(3, title="Reviewed work", labels=["ready"]),
                    issue(4, labels=["ready"]),
                    map_issue(state, 50),
                ],
                head=head,
            )
            with mock.patch.object(imap, "REPO_ROOT", root):
                rc, out = run(
                    imap.cmd_apply_delta,
                    tracker,
                    args(
                        ticket=3,
                        outcome="Build the reviewed behavior",
                        review_adr=["docs/adr/0168-decision.md"],
                        no_work=None,
                        commit=head,
                    ),
                )

        written = imap.extract_state(tracker.rows[50]["body"])
        self.assertEqual(rc, 1, out)
        self.assertEqual(written["reconciled_through"], head)
        self.assertIn("ready tickets still unmapped: 1: #4", out)

    def test_review_records_derive_changed_packets_and_require_no_work_prose(self):
        before = state_with(
            [packet("PA", [1], outcome="Existing work")],
            reconciled_through="old1234",
        )
        delta = {
            "review_adrs": [{"adr": "docs/adr/0168-decision.md", "commit": "f" * 40}],
            "add_packets": [packet("PB", [2], outcome="New work")],
        }

        after = imap.apply_delta(before, delta)

        self.assertEqual(
            after["adr_reviews"],
            [{"adr": "docs/adr/0168-decision.md", "commit": "f" * 40, "packets": ["PB"]}],
        )
        with self.assertRaisesRegex(imap.MapError, "no-work sentence is blank"):
            imap.apply_delta(
                before,
                {"review_adrs": [{"adr": "docs/adr/0169-no-work.md", "commit": "f" * 40}]},
            )

    def test_review_records_name_removed_and_resequenced_packets(self):
        before = state_with(
            [packet("PA", [1], outcome="A"), packet("PB", [2], outcome="B")],
            groups=[{"name": "shared seam", "packets": ["PA", "PB"]}],
        )
        after = imap.apply_delta(
            before,
            {
                "remove_packets": ["PA"],
                "set_collision_kind": [
                    {"name": "shared seam", "kind": "sequence", "packets": ["PB"]}
                ],
                "review_adrs": [
                    {"adr": "docs/adr/0168-decision.md", "commit": "f" * 40}
                ],
            },
        )

        self.assertEqual(after["adr_reviews"][0]["packets"], ["PA", "PB"])

    def test_review_records_implicit_relationship_changes_from_packet_removal(self):
        before = state_with(
            [packet("PA", [1], outcome="A"), packet("PB", [2], outcome="B")],
            edges=[
                {"type": "HARD", "from_ticket": 1, "to_ticket": 2},
                {"type": "EXTERNAL-GATE", "on": "issue:99", "to": "PB"},
            ],
            groups=[{"name": "shared seam", "packets": ["PA", "PB"]}],
        )

        after = imap.apply_delta(
            before,
            {
                "remove_packets": ["PA"],
                "review_adrs": [
                    {"adr": "docs/adr/0168-decision.md", "commit": "f" * 40}
                ],
            },
        )

        self.assertEqual(after["adr_reviews"][0]["packets"], ["PA", "PB"])

    def test_review_never_records_external_gate_identity_as_a_packet(self):
        before = state_with([packet("PB", [2], outcome="B")])

        after = imap.apply_delta(
            before,
            {
                "add_edges": [
                    {"type": "EXTERNAL-GATE", "on": "issue:99", "to": "PB"}
                ],
                "review_adrs": [
                    {"adr": "docs/adr/0168-decision.md", "commit": "f" * 40}
                ],
            },
        )

        self.assertEqual(after["adr_reviews"][0]["packets"], ["PB"])

    def test_refused_write_preserves_authored_no_work_sentences(self):
        args_ = args(delta=None, ticket=None, outcome=None)
        args_.review_adr = ["docs/adr/0169-no-work.md"]
        args_.no_work = "The decision changes no implementation packet."

        self.assertIn(
            args_.no_work,
            imap.authored_outcomes(args_),
        )

    def test_no_work_review_needs_no_packet_delta(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Map Tests"], cwd=root, check=True)
            (root / "seed.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
            floor = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            ).stdout.strip()
            adr = root / "docs" / "adr" / "0169-no-work.md"
            adr.parent.mkdir(parents=True)
            adr.write_text("# No work\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "ADR"], cwd=root, check=True)
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=root, check=True,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            ).stdout.strip()
            state = state_with([], reconciled_through=floor)
            tracker = FakeTracker([map_issue(state, 50)], head=head)
            with mock.patch.object(imap, "REPO_ROOT", root):
                rc, out = run(
                    imap.cmd_apply_delta,
                    tracker,
                    args(
                        delta=None,
                        ticket=None,
                        outcome=None,
                        review_adr=["docs/adr/0169-no-work.md"],
                        no_work="This decision creates no implementation work.",
                        commit=head,
                    ),
                )

        written = imap.extract_state(tracker.rows[50]["body"])
        self.assertEqual(rc, 0, out)
        self.assertEqual(written["reconciled_through"], head)
        self.assertEqual(written["adr_reviews"], [])

    def test_a_server_created_default_branch_commit_is_fetched_before_review(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            remote = root / "remote.git"
            source = root / "source"
            consumer = root / "consumer"
            subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
            subprocess.run(["git", "init", "-q", "-b", "main", str(source)], check=True)
            subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=source, check=True)
            subprocess.run(["git", "config", "user.name", "Map Tests"], cwd=source, check=True)
            (source / "seed.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=source, check=True)
            subprocess.run(["git", "commit", "-qm", "seed"], cwd=source, check=True)
            subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=source, check=True)
            subprocess.run(["git", "push", "-q", "-u", "origin", "main"], cwd=source, check=True)
            subprocess.run(["git", "clone", "-q", "-b", "main", str(remote), str(consumer)], check=True)
            (source / "server.txt").write_text("server merge\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=source, check=True)
            subprocess.run(["git", "commit", "-qm", "server merge"], cwd=source, check=True)
            subprocess.run(["git", "push", "-q"], cwd=source, check=True)
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=source, check=True,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            ).stdout.strip()

            resolved = imap.ensure_local_commit(consumer, commit)

        self.assertEqual(resolved, commit)

    def test_direct_placement_is_inert_when_the_ticket_is_already_mapped(self):
        state = state_with(
            [packet("P3", [3], outcome="Keep authored judgment")],
            reconciled_through="feed123",
        )
        tracker = FakeTracker(
            [issue(3, labels=["ready"]), map_issue(state, 50)],
            head="feed123",
        )
        before = imap.extract_state(tracker.rows[50]["body"])

        rc, out = run(
            imap.cmd_apply_delta,
            tracker,
            args(
                commit=None,
                ticket=3,
                outcome="A later invocation must not replace this",
            ),
        )

        self.assertEqual(rc, 0, out)
        self.assertEqual(imap.extract_state(tracker.rows[50]["body"]), before)
        self.assertIn("packets written: 0", out)

    def test_a_tampered_write_is_caught(self):
        class Tampering(FakeTracker):
            def __init__(self, rows, blocked=None):
                super().__init__(rows, blocked)
                self.updated = False

            def update_issue_body(self, number, body):
                super().update_issue_body(number, body)
                self.updated = True

            def get_issue(self, number):
                row = dict(self.rows[number])
                if self.updated:
                    row["body"] = row["body"].replace('"PA"', '"PX"')
                return row

        tracker = Tampering(self.rows, blocked={2: [1]})
        rc, out = run(imap.cmd_publish, tracker, args())
        # 1, not 2: the write DID happen, and 2 would claim it had not.
        self.assertEqual(rc, 1)
        self.assertIn("READ-BACK FAILED", out)
        self.assertIn("DID happen", out)

    def test_state_hash_ignores_derived_render_changes(self):
        first = "first render\n" + imap.state_block(self.state) + "\nold graph"
        second = "second render\n" + imap.state_block(self.state) + "\nnew graph"

        self.assertEqual(imap.state_hash(first), imap.state_hash(second))

    def test_concurrent_state_change_refuses_and_preserves_the_authored_outcome(self):
        concurrent = state_with(
            [
                packet("PA", [1]),
                packet("PB", [2]),
                packet("PX", [9], outcome="Concurrent judgment"),
            ],
            edges=[hard(1, 2)],
        )

        class ConcurrentWrite(FakeTracker):
            def __init__(self, rows, blocked=None):
                super().__init__(rows, blocked)
                self.updated = False

            def get_issue(self, number):
                row = dict(self.rows[number])
                row["body"] = imap.state_block(concurrent)
                return row

            def update_issue_body(self, number, body):
                self.updated = True
                super().update_issue_body(number, body)

        tracker = ConcurrentWrite(self.rows, blocked={2: [1]})
        desired = imap.apply_delta(
            self.state,
            {"add_packets": [packet(
                "P3", [3], outcome="Authored judgment that must survive"
            )]},
        )

        rc, out = run(
            lambda target, ns: imap.publish_body(
                target,
                50,
                desired,
                ns,
                expected_state_hash=imap.state_hash(imap.state_block(self.state)),
                refused_outcomes=("Authored judgment that must survive",),
            ),
            tracker,
            args(),
        )

        self.assertEqual(rc, 1, out)
        self.assertFalse(tracker.updated)
        self.assertIn("STATE CHANGED", out)
        match = re.search(r"outcome record: (.+)", out)
        self.assertIsNotNone(match, out)
        record_path = Path(match.group(1).strip())
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertEqual(
                record["outcomes"], ["Authored judgment that must survive"]
            )
        finally:
            record_path.unlink(missing_ok=True)

    def test_apply_delta_rederives_after_one_state_hash_mismatch(self):
        concurrent = state_with(
            [
                packet("PA", [1]),
                packet("PB", [2]),
                packet("PX", [9], outcome="Concurrent judgment"),
            ],
            edges=[hard(1, 2)],
        )

        class ChangesOnce(FakeTracker):
            def __init__(self, rows, blocked=None, head="abc1234"):
                super().__init__(rows, blocked, head)
                self.get_calls = 0
                self.head_calls = 0

            def default_branch_head(self):
                self.head_calls += 1
                return super().default_branch_head()

            def get_issue(self, number):
                self.get_calls += 1
                if self.get_calls == 2:
                    self.rows[number]["body"] = imap.state_block(concurrent)
                return super().get_issue(number)

        tracker = ChangesOnce(
            self.rows + [issue(3, labels=["ready"]), issue(9, state="closed")],
            blocked={2: [1]},
            head="feed123",
        )

        rc, out = run(
            imap.cmd_apply_delta,
            tracker,
            args(commit=None, ticket=3, outcome="Authored placement"),
        )

        self.assertEqual(rc, 0, out)
        written = imap.extract_state(tracker.rows[50]["body"])
        self.assertEqual(imap.packet_of(written, 3), "P3")
        self.assertEqual(imap.packet_of(written, 9), "PX")
        self.assertEqual(tracker.head_calls, 1)

    def test_apply_delta_exhausts_three_state_hash_attempts_and_preserves_once(self):
        class AlwaysChanges(FakeTracker):
            def __init__(self, rows, blocked=None, head="abc1234"):
                super().__init__(rows, blocked, head)
                self.get_calls = 0
                self.head_calls = 0

            def default_branch_head(self):
                self.head_calls += 1
                return super().default_branch_head()

            def get_issue(self, number):
                self.get_calls += 1
                if self.get_calls % 2 == 0:
                    changed = imap.extract_state(self.rows[number]["body"])
                    changed["in_flight_labels"] = [f"remote-{self.get_calls}"]
                    self.rows[number]["body"] = imap.state_block(changed)
                return super().get_issue(number)

        tracker = AlwaysChanges(
            self.rows + [issue(3, labels=["ready"])],
            blocked={2: [1]},
            head="feed123",
        )
        with mock.patch.object(
            imap, "preserve_refused_outcomes", return_value=Path("record.json")
        ) as preserve:
            rc, out = run(
                imap.cmd_apply_delta,
                tracker,
                args(commit=None, ticket=3, outcome="Authored placement"),
            )

        self.assertEqual(rc, 1, out)
        self.assertEqual(tracker.get_calls, 6)
        self.assertEqual(tracker.head_calls, 1)
        self.assertIn("3 attempts", out)
        preserve.assert_called_once()
        self.assertEqual(preserve.call_args.args[0], ("Authored placement",))

    def test_busy_lock_refusal_preserves_the_directly_authored_outcome(self):
        tracker = FakeTracker(self.rows, blocked={2: [1]})
        with mock.patch.object(
            imap.artifact_lock,
            "hold",
            side_effect=imap.artifact_lock.ArtifactBusy("another writer"),
        ):
            rc, out = run(
                imap.cmd_apply_delta,
                tracker,
                args(ticket=3, outcome="Judgment typed before the lock refused"),
            )

        self.assertEqual(rc, 1, out)
        match = re.search(r"outcome record: (.+)", out)
        self.assertIsNotNone(match, out)
        record_path = Path(match.group(1).strip())
        try:
            self.assertIn(
                "Judgment typed before the lock refused",
                record_path.read_text(encoding="utf-8"),
            )
        finally:
            record_path.unlink(missing_ok=True)

    def test_refused_outcomes_are_accounted_and_check_enumerates_them(self):
        tracker = FakeTracker(self.rows, blocked={2: [1]})
        with tempfile.TemporaryDirectory() as temporary:
            scratch = Path(temporary) / "scratch"
            with mock.patch.object(
                imap.repo_root, "scratch_root", return_value=scratch
            ):
                record = imap.preserve_refused_outcomes(
                    ("Authored placement",),
                    issue_number=50,
                    reason="busy",
                )
                rc, out = run(imap.cmd_check, tracker, args())

            self.assertIsNotNone(record)
            self.assertEqual(record.parent, scratch / "runs" / "map-refusals")
            self.assertEqual(rc, 0, out)
            self.assertIn("pending outcome records: 1", out)

    def test_init_creates_once_and_only_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text(json.dumps(self.state), encoding="utf-8")
            tracker = FakeTracker([
                issue(1, labels=["ready"]),
                issue(2, labels=["ready"]),
            ], blocked={2: [1]})
            ns = args(state=str(path), title="Map", label=["triage"],
                      adopt=None)
            rc, out = run(imap.cmd_init, tracker, ns)
            self.assertEqual(rc, 0)
            self.assertEqual(len(tracker.created), 1)
            number = tracker.created[0]
            self.assertEqual(
                imap.extract_state(tracker.rows[number]["body"]), self.state
            )
            self.assertEqual(tracker.rows[number]["labels"], ["triage"])
            self.assertIn(
                "- superseded state: none",
                tracker.rows[number]["body"],
            )
            # a second init refuses: one map per repository
            with self.assertRaises(imap.MapError):
                run(imap.cmd_init, tracker, ns)

    def test_init_adopt_locks_the_adopted_issue_and_compares_its_hash(self):
        original = imap.state_block(self.state)

        class AdoptTarget(FakeTracker):
            def issues(self):
                return [row for row in super().issues() if row["number"] != 77]

        tracker = AdoptTarget(
            [
                issue(1, labels=["ready"]),
                issue(2, labels=["ready"]),
                issue(77, title="Adopt me", body=original),
            ],
            blocked={2: [1]},
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text(json.dumps(self.state), encoding="utf-8")
            ns = args(state=str(path), title="Map", label=[], adopt=77)
            with mock.patch.object(
                imap.artifact_lock, "hold", wraps=imap.artifact_lock.hold
            ) as hold, mock.patch.object(
                imap, "publish_body", wraps=imap.publish_body
            ) as publish:
                rc, out = run(imap.cmd_init, tracker, ns)

        self.assertEqual(rc, 0, out)
        self.assertEqual(
            hold.call_args.args[0],
            imap.map_artifact(tracker, 77),
        )
        self.assertEqual(
            publish.call_args.kwargs["expected_state_hash"],
            imap.state_hash(original),
        )

    def test_render_previews_a_state_file_before_any_map_exists(self):
        tracker = FakeTracker([issue(1), issue(2)], blocked={2: [1]})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text(json.dumps(self.state), encoding="utf-8")
            rc, out = run(imap.cmd_render, tracker, args(state=str(path)))
        self.assertEqual(rc, 0)
        self.assertEqual(imap.extract_state(out), self.state)

    def test_render_preview_refuses_an_invalid_state_file(self):
        bad = state_with([packet("PA", [1]), packet("PB", [1])])
        tracker = FakeTracker([issue(1)])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(imap.MapError):
                run(imap.cmd_render, tracker, args(state=str(path)))

    def test_apply_delta_dry_run_mutates_nothing(self):
        tracker = FakeTracker(self.rows, blocked={2: [1]})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "delta.json"
            path.write_text(json.dumps({"add_packets": [packet(
                "PC", [3], outcome="Build the ruled packet"
            )]}),
                            encoding="utf-8")
            before = tracker.rows[50]["body"]
            rc, out = run(imap.cmd_apply_delta, tracker,
                          args(delta=str(path), dry_run=True))
            self.assertEqual(tracker.rows[50]["body"], before)
            # #3 is not on the fake tracker: the dry run says so
            self.assertIn("unknown-ticket", out)


# ---------------------------------------------------------------------------
# Claim's refusals and warnings
# ---------------------------------------------------------------------------

class ClaimRefusals(unittest.TestCase):
    def setUp(self):
        self.state = state_with(
            [packet("PA", [1]), packet("PB", [2]), packet("PD", [4])],
            edges=[hard(1, 2)],
            exclusions=[{"ticket": 9, "why": "still grilling"}],
        )
        self.rows = [issue(1, labels=["ready"]),
                     issue(2, labels=["ready"]), issue(4, state="closed"),
                     issue(9, labels=["ready"]), map_issue(self.state, 50)]
        self.tracker = FakeTracker(self.rows, blocked={2: [1]})

    def test_neither_packet_nor_ticket(self):
        rc, out = run(imap.cmd_claim, self.tracker, args())
        self.assertEqual(rc, 1)
        self.assertIn("REFUSED", out)

    def test_unknown_packet(self):
        rc, out = run(imap.cmd_claim, self.tracker, args(packet="PX"))
        self.assertEqual(rc, 1)

    def test_excluded_ticket(self):
        rc, out = run(imap.cmd_claim, self.tracker, args(ticket=9))
        self.assertEqual(rc, 1)
        self.assertIn("excluded", out)

    def test_unmapped_ticket(self):
        rc, out = run(imap.cmd_claim, self.tracker, args(ticket=77))
        self.assertEqual(rc, 1)
        self.assertIn("no packet", out)

    def test_done_packet(self):
        rc, out = run(imap.cmd_claim, self.tracker, args(packet="PD"))
        self.assertEqual(rc, 1)
        self.assertIn("done", out)

    def test_claim_by_ticket_resolves_its_packet(self):
        rc, out = run(imap.cmd_claim, self.tracker, args(ticket=1))
        self.assertEqual(rc, 0)
        self.assertIn("CLAIMABLE", out)
        self.assertIn("PA", out)


# ---------------------------------------------------------------------------
# The drift window and other status subtleties
# ---------------------------------------------------------------------------

class TheDriftWindowStillRefuses(unittest.TestCase):
    """A declared HARD edge whose native mirror the agent has not yet
    applied must still block: claim passing during exactly the drift
    `check` reports would defeat the gate."""

    def setUp(self):
        self.state = state_with([packet("PA", [1]), packet("PB", [2])],
                                edges=[hard(1, 2)])
        self.rows = [issue(1), issue(2), map_issue(self.state, 50)]

    def test_declared_only_edge_blocks(self):
        live = imap.Live(FakeTracker(self.rows), self.state)
        self.assertEqual(imap.packet_status(self.state, live, "PB"), "blocked")

    def test_claim_refuses_on_the_declared_edge(self):
        rc, out = run(imap.cmd_claim, FakeTracker(self.rows),
                      args(packet="PB"))
        self.assertEqual(rc, 1)
        self.assertIn("#1", out)

    def test_closed_declared_blocker_frees(self):
        rows = [issue(1, state="closed"), issue(2)]
        live = imap.Live(FakeTracker(rows), self.state)
        self.assertEqual(imap.packet_status(self.state, live, "PB"), "ready")


class AnAssigneeDoesNotLaunderABlocker(unittest.TestCase):
    def test_blocked_beats_in_flight(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])],
                           edges=[hard(1, 2)])
        rows = [issue(1), issue(2, assignees=["someone"]),
                map_issue(state, 50)]
        live = imap.Live(FakeTracker(rows, blocked={2: [1]}), state)
        self.assertEqual(imap.packet_status(state, live, "PB"), "blocked")
        rc, out = run(imap.cmd_claim, FakeTracker(rows, blocked={2: [1]}),
                      args(packet="PB"))
        self.assertEqual(rc, 1)
        self.assertIn("REFUSED", out)


class AnInFlightPredecessorIsNotSatisfied(unittest.TestCase):
    """Branch progress is not a moved default branch: the successor of an
    in-flight packet is not buildable, and neither shows in any frontier."""

    def test_successor_waits_outside_every_frontier(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])],
                           edges=[hard(1, 2)])
        tracker = FakeTracker([issue(1, assignees=["someone"]), issue(2)],
                              blocked={2: [1]})
        live = imap.Live(tracker, state)
        self.assertEqual(imap.packet_status(state, live, "PA"), "in-flight")
        for layer in imap.frontiers(state, live):
            self.assertNotIn("PA", layer)
            self.assertNotIn("PB", layer)


class AnUnreadyPredecessorIsNotSatisfied(unittest.TestCase):
    def test_packet_and_successor_stay_outside_every_frontier(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            edges=[hard(1, 2)],
        )
        tracker = FakeTracker(
            [issue(1), issue(2, labels=["ready"])],
            blocked={2: [1]},
        )
        live = imap.Live(tracker, state)

        fronts = imap.frontiers(state, live)

        for layer in fronts:
            self.assertNotIn("PA", layer)
            self.assertNotIn("PB", layer)


class UndeclaredNativeDriftNeverRendersBuildable(unittest.TestCase):
    """A native blocker with no declared HARD edge is invisible to the
    graph; the first frontier must still hold the blocked packet back."""

    def test_first_frontier_is_held_to_startable_status(self):
        state = state_with([packet("PA", [1]), packet("PB", [2])])
        tracker = FakeTracker(
            [issue(1, labels=["ready"]), issue(2, labels=["ready"])],
            blocked={2: [1]},
        )
        live = imap.Live(tracker, state)
        self.assertEqual(imap.packet_status(state, live, "PB"), "blocked")
        fronts = imap.frontiers(state, live)
        # Frontier 1 ("buildable immediately") holds PB back; it may appear
        # in a later, speculative frontier, and check reports the drift.
        self.assertNotIn("PB", fronts[0])
        self.assertEqual(fronts[0], ["PA"])


class AGateOnAMissingIssueIsAFinding(unittest.TestCase):
    def test_typoed_gate_reported(self):
        state = state_with([packet("PA", [1])],
                           edges=[gate("issue:9999", "PA")])
        live = imap.Live(FakeTracker([issue(1)]), state)
        kinds = [f.kind for f in imap.validate_against_live(state, live)]
        self.assertIn("gate-unknown-issue", kinds)

    def test_existing_gate_issue_is_not(self):
        state = state_with([packet("PA", [1])],
                           edges=[gate("issue:99", "PA")])
        live = imap.Live(FakeTracker([issue(1), issue(99)]), state)
        kinds = [f.kind for f in imap.validate_against_live(state, live)]
        self.assertNotIn("gate-unknown-issue", kinds)


class NothingEscapesAsExitOne(unittest.TestCase):
    """Every way of not having run is 2 -- a traceback would exit 1, the
    findings status (#150's shape)."""

    def test_field_level_malformed_state_is_a_map_error(self):
        for bad in (
            {"schema": imap.SCHEMA, "packets": [{"id": "PA"}]},
            {"schema": imap.SCHEMA, "packets": [{"tickets": [1]}]},
            {"schema": imap.SCHEMA, "packets": "not a list"},
            {"schema": imap.SCHEMA, "packets": [],
             "edges": [{"type": "HARD", "from_ticket": "x", "to_ticket": 2}]},
            {"schema": imap.SCHEMA, "packets": [],
             "collision_groups": [{"packets": ["PA"]}]},
            {"schema": imap.SCHEMA, "packets": [], "exclusions": [{}]},
        ):
            body = (f"{imap.STATE_BEGIN}\n```json\n{json.dumps(bad)}\n```\n"
                    f"{imap.STATE_END}")
            with self.assertRaises(imap.MapError, msg=repr(bad)):
                imap.extract_state(body)

    def test_a_delta_adding_a_malformed_packet_is_refused(self):
        state = state_with([packet("PA", [1])])
        with self.assertRaises(imap.MapError):
            imap.apply_delta(state, {"add_packets": [{"id": "PB"}]})

    def test_main_converts_not_run_exceptions_to_2(self):
        real = dict(imap.COMMANDS)
        try:
            for exc in (imap.MapError("x"), FileNotFoundError("no file"),
                        json.JSONDecodeError("bad", "doc", 0)):
                def boom(tracker, ns, _exc=exc):
                    raise _exc
                imap.COMMANDS["check"] = boom
                err = io.StringIO()
                stderr, sys.stderr = sys.stderr, err
                try:
                    rc = imap.main(["--repo", "o/r", "check"])
                finally:
                    sys.stderr = stderr
                self.assertEqual(rc, 2, f"{_exc_name(exc)} did not become 2")
                self.assertIn("did not run", err.getvalue())
        finally:
            imap.COMMANDS.clear()
            imap.COMMANDS.update(real)


class TheInTreeToolDeclaresItsBoundary(unittest.TestCase):
    def test_declared_limits_are_owned_once_and_pointed_to_from_claude(self):
        prose = HERE.parent.joinpath("CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("implementation_map.DECLARED_LIMITS", imap.__doc__)
        self.assertEqual(prose.count("implementation_map.DECLARED_LIMITS"), 1)
        self.assertGreater(len(imap.DECLARED_LIMITS), 0)
        for row in imap.DECLARED_LIMITS:
            self.assertTrue(row.key)
            self.assertTrue(row.limit)
        self.assertEqual((), bind(imap.DECLARED_LIMITS, imap.__doc__, mode=NAMING))
        self.assertEqual((), bind(imap.DECLARED_LIMITS, prose, mode=NAMING))
        row = imap.DECLARED_LIMITS[0]
        self.assertTrue(bind(imap.DECLARED_LIMITS, f"See the object. {row.key}.", mode=NAMING))
        self.assertTrue(bind(imap.DECLARED_LIMITS, f"See the object. {row.limit}", mode=NAMING))
        self.assertEqual(
            [row.key for row in imap.DECLARED_LIMITS].count(
                "revision-attribution-window"
            ),
            1,
        )
        self.assertIn("Every map overwrite takes", prose)

    def test_the_ratified_command_split_stays_public(self):
        parser = imap.build_parser()
        action = next(
            action
            for action in parser._actions
            if isinstance(action, imap.argparse._SubParsersAction)
        )
        self.assertEqual(
            set(action.choices),
            {"init", "check", "claim", "render", "publish", "apply-delta", "audit"},
        )
        self.assertIs(imap.COMMANDS["publish"], imap.cmd_publish)
        self.assertIs(imap.COMMANDS["apply-delta"], imap.cmd_apply_delta)

    def test_the_overwriter_walk_binds_all_three_obligations(self):
        source = (HERE / "implementation_map.py").read_text(encoding="utf-8")

        obligations = map_overwriter_obligations(source)

        self.assertEqual(
            set(obligations),
            {"cmd_publish", "cmd_apply_delta", "cmd_init --adopt"},
        )
        self.assertNotIn("create_issue", obligations)
        self.assertTrue(all(all(rows.values()) for rows in obligations.values()))

    def test_removing_any_overwriter_obligation_turns_the_walk_red(self):
        source = (HERE / "implementation_map.py").read_text(encoding="utf-8")
        cases = (
            ("cmd_publish", "cmd_publish", "map-lock", 'map_artifact(tracker, issue["number"])', "map_artifact(tracker, 0)"),
            ("cmd_apply_delta", "cmd_apply_delta", "map-lock", 'map_artifact(tracker, issue["number"])', "map_artifact(tracker, 0)"),
            ("cmd_init --adopt", "cmd_init", "map-lock", "map_artifact(tracker, lock_number)", "map_artifact(tracker, 0)"),
            ("cmd_publish", "cmd_publish", "state-hash", "expected_state_hash=expected,", ""),
            ("cmd_apply_delta", "_apply_delta_attempt", "state-hash", "expected_state_hash=expected,", ""),
            ("cmd_init --adopt", "_init_under_lock", "state-hash", "expected_state_hash=state_hash(current[\"body\"]),", ""),
            ("cmd_publish", "cmd_publish", "revalidation", "revalidate_after_publish(", "skipped_revalidation("),
            ("cmd_apply_delta", "_apply_delta_attempt", "revalidation", "revalidate_after_publish(", "skipped_revalidation("),
            ("cmd_init --adopt", "_init_under_lock", "revalidation", "revalidate_after_publish(", "skipped_revalidation("),
        )
        for writer, function, obligation, old, new in cases:
            with self.subTest(writer=writer, obligation=obligation):
                mutated = replace_in_function(source, function, old, new)
                self.assertFalse(
                    map_overwriter_obligations(mutated)[writer][obligation]
                )

    def test_a_fourth_overwriter_is_discovered_without_joining_a_name_list(self):
        source = (HERE / "implementation_map.py").read_text(encoding="utf-8")
        source += """
def cmd_fourth(tracker, args):
    with artifact_lock.hold(map_artifact(tracker, args.issue), "fourth", mode="write"):
        return publish_body(
            tracker,
            args.issue,
            {},
            args,
            expected_state_hash="hash",
        )
"""

        obligations = map_overwriter_obligations(source)

        self.assertIn("cmd_fourth", obligations)
        self.assertFalse(obligations["cmd_fourth"]["revalidation"])


class RevisionChainAttribution(unittest.TestCase):
    def setUp(self):
        self.first = state_with([packet("PA", [1], outcome="first")])
        self.second = state_with([packet("PA", [1], outcome="second")])
        self.third = state_with([packet("PA", [1], outcome="third")])

    def test_one_planted_break_appends_one_row_naming_both_writers(self):
        first_body = revision_body(self.first, "writer-a", "0" * 64)
        second_body = revision_body(
            self.second,
            "writer-b",
            imap.state_hash(first_body),
        )
        third_body = revision_body(self.third, "writer-c", "f" * 64)
        history = imap.RevisionHistory(
            revisions=(
                imap.Revision("r3", "2026-09-12T03:00:00Z", third_body),
                imap.Revision("r2", "2026-09-12T02:00:00Z", second_body),
                imap.Revision("r1", "2026-09-12T01:00:00Z", first_body),
            ),
            older_remainder=False,
        )
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Path(temporary) / "breaks.md"
            with mock.patch.object(imap, "REVISION_LEDGER", ledger):
                summary = imap.harvest_revision_chain(history)
            text = ledger.read_text(encoding="utf-8")

        self.assertEqual(summary.breaks_appended, 1)
        self.assertEqual(text.count("| r2 | writer-b | r3 | writer-c |"), 1)
        self.assertIn("- high-water revision: `r3`", text)
        self.assertIn("- unread remainder: 0", text)

    def test_a_prior_high_water_outside_the_window_reports_a_remainder(self):
        first_body = revision_body(self.first, "writer-a", "0" * 64)
        second_body = revision_body(
            self.second,
            "writer-b",
            imap.state_hash(first_body),
        )
        history = imap.RevisionHistory(
            revisions=(
                imap.Revision("r2", "2026-09-12T02:00:00Z", second_body),
                imap.Revision("r1", "2026-09-12T01:00:00Z", first_body),
            ),
            older_remainder=True,
        )
        with tempfile.TemporaryDirectory() as temporary:
            ledger = Path(temporary) / "breaks.md"
            ledger.write_text(
                imap.render_revision_ledger(
                    high_water="r0",
                    unread_remainder="0",
                    rows=(),
                ),
                encoding="utf-8",
            )
            with mock.patch.object(imap, "REVISION_LEDGER", ledger):
                summary = imap.harvest_revision_chain(history)
            text = ledger.read_text(encoding="utf-8")

        self.assertNotEqual(summary.unread_remainder, "0")
        self.assertIn("prior high-water revision r0 was not retained", text)

    def test_a_full_host_window_declares_an_older_remainder(self):
        nodes = [
            {"id": f"r{index}", "editedAt": "2026-09-12T00:00:00Z", "diff": "body"}
            for index in range(imap.REVISION_WINDOW)
        ]
        payload = json.dumps(
            {
                "data": {
                    "repository": {
                        "issue": {
                            "userContentEdits": {
                                "pageInfo": {"hasNextPage": False},
                                "nodes": nodes,
                            }
                        }
                    }
                }
            }
        )
        tracker = imap.GitHub("owner/repo")
        with mock.patch.object(tracker, "_run", return_value=payload) as run_:
            history = tracker.user_content_edits(596)

        query_argument = next(
            argument for argument in run_.call_args.args[0] if argument.startswith("query=")
        )
        queried_window = int(re.search(r"first:(\d+)", query_argument).group(1))
        limit = next(
            row.limit
            for row in imap.DECLARED_LIMITS
            if row.key == "revision-attribution-window"
        )
        self.assertEqual(queried_window, imap.REVISION_WINDOW)
        self.assertIn(str(imap.REVISION_WINDOW), limit)
        self.assertEqual(len(history.revisions), imap.REVISION_WINDOW)
        self.assertTrue(history.older_remainder)


def _exc_name(exc):
    return type(exc).__name__


# ---------------------------------------------------------------------------
# Stage packets: a split ticket lives in the packet that closes it
# ---------------------------------------------------------------------------

class AStagePacketMayHoldNoTickets(unittest.TestCase):
    """A two-stage ticket keeps unique membership: the ticket sits in the
    closing stage's packet; the earlier stage is a ticketless packet whose
    scope lives in its title, retired by a delta once merged."""

    def setUp(self):
        self.state = state_with(
            [packet("PXa", [], title="stage 1 of #5"),
             packet("PXb", [5], title="stage 2 of #5")],
            edges=[gate("issue:6", "PXb")],
        )
        self.rows = [issue(5), issue(6), map_issue(self.state, 50)]

    def test_empty_packet_is_ready_not_done(self):
        live = imap.Live(FakeTracker(self.rows), self.state)
        self.assertEqual(imap.packet_status(self.state, live, "PXa"), "ready")
        self.assertIn("PXa", imap.frontiers(self.state, live)[0])

    def test_empty_packet_is_claimable(self):
        rc, out = run(imap.cmd_claim, FakeTracker(self.rows),
                      args(packet="PXa"))
        self.assertEqual(rc, 0)

    def test_retired_by_a_delta(self):
        new = imap.apply_delta(self.state, {"remove_packets": ["PXa"]})
        self.assertEqual(imap.packet_ids(new), ["PXb"])

    def test_duplicate_membership_across_stages_is_a_finding(self):
        dup = state_with([packet("PXa", [5]), packet("PXb", [5])])
        kinds = [f.kind for f in imap.validate_shape(dup)]
        self.assertIn("duplicate-ticket", kinds)


# ---------------------------------------------------------------------------
# Shape findings
# ---------------------------------------------------------------------------

class ShapeFindings(unittest.TestCase):
    def test_duplicate_packet_id(self):
        state = state_with([packet("PA", [1]), packet("PA", [2])])
        kinds = [f.kind for f in imap.validate_shape(state)]
        self.assertIn("duplicate-packet", kinds)

    def test_excluded_and_mapped(self):
        state = state_with([packet("PA", [1])],
                           exclusions=[{"ticket": 1, "why": "no"}])
        kinds = [f.kind for f in imap.validate_shape(state)]
        self.assertIn("excluded-and-mapped", kinds)

    def test_hard_edge_off_map(self):
        state = state_with([packet("PA", [1])], edges=[hard(1, 99)])
        kinds = [f.kind for f in imap.validate_shape(state)]
        self.assertIn("hard-edge-off-map", kinds)

    def test_rebuild_edge_off_map(self):
        state = state_with([packet("PA", [1])], edges=[saving("PA", "PX")])
        kinds = [f.kind for f in imap.validate_shape(state)]
        self.assertIn("edge-off-map", kinds)

    def test_bad_edge_type(self):
        state = state_with([packet("PA", [1])],
                           edges=[{"type": "SOFT", "from": "PA", "to": "PA"}])
        kinds = [f.kind for f in imap.validate_shape(state)]
        self.assertIn("bad-edge-type", kinds)

    def test_collision_group_off_map(self):
        state = state_with([packet("PA", [1])],
                           groups=[{"name": "g", "packets": ["PA", "PX"]}])
        kinds = [f.kind for f in imap.validate_shape(state)]
        self.assertIn("collision-off-map", kinds)

    def test_unknown_collision_kind_is_a_live_finding(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{
                "name": "future classifier",
                "kind": "a-kind-this-version-does-not-know",
                "packets": ["PA", "PB"],
            }],
        )

        self.assertEqual(imap.validate_shape(state), [])
        live = imap.Live(FakeTracker([issue(1), issue(2)]), state)
        findings = imap.validate_against_live(state, live)
        bad_kind = next(f for f in findings if f.kind == "bad-collision-kind")
        self.assertIn("a-kind-this-version-does-not-know", bad_kind.detail)
        body = imap.render(
            state,
            live,
            {"commit": "c", "date": "d"},
        )
        derived = body.split(imap.STATE_END, 1)[1]
        self.assertNotIn("a-kind-this-version-does-not-know", derived)
        table = derived.split("## Collision groups", 1)[1].split("##", 1)[0]
        self.assertIn("| Constraint | Kind | Packets | Why |", table)
        self.assertIn("| future classifier | unclassified | PA, PB | - |", table)

    def test_non_integer_ticket(self):
        state = state_with([packet("PA", ["#1"])])
        kinds = [f.kind for f in imap.validate_shape(state)]
        self.assertIn("bad-ticket", kinds)


# ---------------------------------------------------------------------------
# Rendering details a reader depends on
# ---------------------------------------------------------------------------

class TheRenderedViews(unittest.TestCase):
    def setUp(self):
        self.state = state_with(
            [packet("P497+532", [497, 532], outcome="two PRs"),
             packet("PB", [2])],
            edges=[hard(497, 532), hard(497, 2)],
            groups=[{"name": "seam", "packets": ["P497+532", "PB"]}],
        )
        self.tracker = FakeTracker(
            [issue(497), issue(532), issue(2)],
            blocked={532: [497], 2: [497]},
        )
        self.live = imap.Live(self.tracker, self.state)

    def test_mermaid_node_ids_are_sanitized(self):
        """`P497+532` is a fine packet id and an illegal Mermaid node id;
        the graph must sanitize ids while labels keep the real name."""
        graph = imap.mermaid(self.state, self.live)
        for line in graph.splitlines():
            if "-->" in line or "-.->" in line or line.strip().startswith("class "):
                self.assertNotIn("+", line, f"unsanitized node id in {line!r}")
        self.assertIn("P497+532", graph)  # the label still names the packet

    def test_intra_packet_hard_edges_stay_off_the_graph(self):
        graph = imap.mermaid(self.state, self.live)
        self.assertEqual(graph.count("|HARD|"), 1)

    def test_packet_table_lists_open_blockers(self):
        body = imap.render(self.state, self.live, {"commit": "c", "date": "d"})
        table = body.split("## Packet table")[1].split("##")[0]
        row = next(line for line in table.splitlines() if "| PB |" in line)
        self.assertIn("#497", row)

    def test_snapshot_counts_ready_labels_live(self):
        rows = [issue(497, labels=["ready"]), issue(532), issue(2)]
        live = imap.Live(FakeTracker(rows, blocked=self.tracker.blocked),
                         self.state)
        body = imap.render(self.state, live, {"commit": "c", "date": "d"})
        self.assertIn("live ready-for-agent tickets: 1", body)

    def test_snapshot_names_the_repository_relative_producer_hash_and_commit(self):
        body = imap.render(
            self.state,
            self.live,
            {
                "commit": "abc1234",
                "producer_identity": "d" * 64,
                "date": "d",
            },
        )
        snapshot = body.partition("## Snapshot")[2].partition("\n## ")[0]

        self.assertIn(
            f"- producer: `tools/implementation_map.py sha256:{'d' * 64}`",
            snapshot,
        )
        self.assertIn("- default-branch commit: `abc1234`", snapshot)
        self.assertNotIn(str(HERE.parent), snapshot)

    def test_snapshot_names_its_writer_and_the_state_it_supersedes(self):
        expected = imap.state_hash(imap.state_block(self.state))
        body = imap.render(
            self.state,
            self.live,
            {
                "commit": "abc1234",
                "producer_identity": "d" * 64,
                "writer_identity": "writer-7",
                "superseded_state_hash": expected,
                "date": "d",
            },
        )
        snapshot = body.partition("## Snapshot")[2].partition("\n## ")[0]

        self.assertIn("- writer: `writer-7`", snapshot)
        self.assertIn(f"- superseded state: `sha256:{expected}`", snapshot)
        without_stamp = body.replace("- writer: `writer-7`\n", "").replace(
            f"- superseded state: `sha256:{expected}`\n", ""
        )
        self.assertEqual(imap.state_hash(body), imap.state_hash(without_stamp))

    def test_producer_stamp_predicate_reads_the_derived_snapshot_once(self):
        identity = "d" * 64
        with mock.patch.object(imap, "producer_identity", return_value=identity):
            valid = imap.render(
                self.state,
                self.live,
                {
                    "commit": "abc1234",
                    "producer_identity": identity,
                    "date": "d",
                },
            )
        missing = valid.replace(
            f"- producer: `tools/implementation_map.py sha256:{identity}`\n",
            "",
        ).replace(
            '"outcome": "two PRs"',
            f'"outcome": "tools/implementation_map.py sha256:{identity}"',
        )
        mismatched = valid.replace(
            f"tools/implementation_map.py sha256:{identity}",
            f"tools/implementation_map.py sha256:{'a' * 64}",
            1,
        )

        with mock.patch.object(imap, "producer_identity", return_value=identity):
            self.assertIsNone(imap.producer_stamp_problem(valid))
            self.assertIn("exactly one", imap.producer_stamp_problem(missing))
            self.assertIn("does not match", imap.producer_stamp_problem(mismatched))

    def test_an_uncommitted_emitter_edit_invalidates_the_stamp(self):
        with tempfile.TemporaryDirectory() as temporary:
            emitter = Path(temporary) / "implementation_map.py"
            emitter.write_text("first emitter\n", encoding="utf-8")
            with mock.patch.object(imap, "__file__", str(emitter)):
                identity = imap.producer_identity()
                body = imap.render(
                    self.state,
                    self.live,
                    {"commit": "abc1234", "producer_identity": identity, "date": "d"},
                )
                emitter.write_text("edited emitter\n", encoding="utf-8")

                self.assertIn("does not match", imap.producer_stamp_problem(body))

    def test_snapshot_separates_default_branch_and_producer_identity(self):
        with mock.patch.object(imap, "producer_identity", return_value="d" * 64):
            snapshot = imap.snapshot_for(self.tracker, args(commit="abc1234", date="d"))

        self.assertEqual(snapshot["commit"], "abc1234")
        self.assertEqual(snapshot["producer_identity"], "d" * 64)

    def test_maintenance_names_the_offline_gate_and_its_limits_pointer(self):
        live = imap.Live(FakeTracker([
            issue(1, labels=["ready"]), issue(2, labels=["ready"])
        ], blocked={2: [1]}), self.state)
        body = imap.render(self.state, live, {"commit": "c", "date": "d"})
        maintenance = body.partition("## Maintenance rule")[2]
        self.assertIn("tools/map_scan.py", maintenance)
        self.assertIn("map_scan.DECLARED_LIMITS", maintenance)

    def test_the_emitter_accounts_for_every_line_and_every_packet(self):
        coverage = imap.verify_mermaid(self.state, imap.mermaid(self.state, self.live))

        self.assertEqual(coverage.unread, ())
        self.assertEqual(
            coverage.total,
            coverage.nodes + coverage.edges + coverage.directives,
        )
        self.assertEqual(coverage.packet_nodes, len(self.state["packets"]))

    def test_the_emitter_refuses_undefined_nodes_and_unknown_lines(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            edges=[hard(1, 2)],
        )
        malformed = (
            "graph TD\n    PA[\"PA: #1\"]\n    PB[\"PB: #2\"]\n"
            "    PA -->|HARD| PX\n    mystery"
        )

        with self.assertRaisesRegex(imap.MapError, "undefined node"):
            imap.verify_mermaid(state, malformed)

        with self.assertRaisesRegex(imap.MapError, "unaccounted Mermaid"):
            imap.verify_mermaid(state, malformed.replace("PX", "PB"))

    def test_collision_groups_are_a_table_and_not_graph_edges(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[
                {"name": "first", "packets": ["PA", "PB"], "why": "one seam"},
                {"name": "second", "packets": ["PA", "PB"], "why": "another seam"},
            ],
        )
        live = imap.Live(FakeTracker([issue(1), issue(2)]), state)

        graph = imap.mermaid(state, live)
        body = imap.render(state, live, {"commit": "c", "date": "d"})
        table = body.split("## Collision groups", 1)[1].split("##", 1)[0]

        self.assertNotIn("-.-", graph)
        self.assertEqual(imap.verify_mermaid(state, graph).unread, ())
        self.assertIn("| first | unclassified | PA, PB | one seam |", table)
        self.assertIn("| second | unclassified | PA, PB | another seam |", table)
        self.assertNotIn("collision sequencing", body)

    def test_free_standing_packets_stay_in_the_table_and_off_the_graph(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2]), packet("PC", [3])],
            edges=[hard(1, 2)],
        )
        live = imap.Live(FakeTracker([issue(1), issue(2), issue(3)]), state)

        graph = imap.mermaid(state, live)
        body = imap.render(state, live, {"commit": "abc1234", "date": "d"})
        table = body.split("## Packet table", 1)[1].split("##", 1)[0]

        self.assertNotIn('PC["PC: #3"]', graph)
        self.assertIn("| PC | #3 |", table)

    def test_graph_packet_coverage_is_a_complete_partition(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2]), packet("PC", [3])],
            edges=[hard(1, 2)],
        )
        live = imap.Live(FakeTracker([issue(1), issue(2), issue(3)]), state)
        graph = imap.mermaid(state, live)

        coverage = imap.verify_mermaid(state, graph)
        body = imap.render(state, live, {"commit": "abc1234", "date": "d"})

        self.assertEqual(coverage.packet_nodes, 2)
        self.assertEqual(coverage.omitted_packet_nodes, 1)
        self.assertEqual(coverage.packet_population, 3)
        self.assertEqual(coverage.packet_remainder, ())
        self.assertIn(
            "dependency graph packets: 2 drawn + 1 omitted free-standing = "
            "3 of 3; unread remainder 0",
            body,
        )

    def test_graph_partition_refuses_an_unrepresented_edge_packet(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2]), packet("PC", [3])],
            edges=[hard(1, 2)],
        )
        live = imap.Live(FakeTracker([issue(1), issue(2), issue(3)]), state)
        partial = "\n".join(
            line
            for line in imap.mermaid(state, live).splitlines()
            if not line.strip().startswith("PB")
            and "-->|HARD| PB" not in line
        )

        with self.assertRaisesRegex(
            imap.MapError, "edge-carrying packet has no Mermaid node"
        ):
            imap.verify_mermaid(state, partial)


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

class AuditComparesPublishedToFresh(unittest.TestCase):
    def setUp(self):
        self.state = state_with([packet("PA", [1]), packet("PB", [2])],
                                edges=[hard(1, 2)])

    def _published_tracker(self):
        tracker = FakeTracker(
            [issue(1, labels=["ready"]), issue(2, labels=["ready"]),
             map_issue(self.state, 50)],
            blocked={2: [1]}, head="abc1234",
        )
        rc, _ = run(imap.cmd_publish, tracker, args())
        assert rc == 0
        return tracker

    def test_clean_after_publish(self):
        tracker = self._published_tracker()
        rc, out = run(imap.cmd_audit, tracker, args())
        self.assertEqual(rc, 0)

    def test_check_and_audit_name_their_different_walked_populations(self):
        tracker = self._published_tracker()

        check_code, check_output = run(imap.cmd_check, tracker, args())
        audit_code, audit_output = run(imap.cmd_audit, tracker, args())

        self.assertEqual(check_code, 0)
        self.assertEqual(audit_code, 0)
        self.assertIn("state block and live tracker", check_output)
        self.assertIn("derived views were not read", check_output)
        self.assertIn("run audit", check_output)
        section_count = len(imap.derived_sections(tracker.rows[50]["body"]))
        self.assertIn(
            f"{section_count} published derived sections; 0 differed",
            audit_output,
        )
        self.assertNotEqual(check_output, audit_output)

    def test_a_missing_producer_stamp_is_an_audit_finding(self):
        tracker = self._published_tracker()
        tracker.rows[50]["body"] = re.sub(
            r"^- producer: `tools/implementation_map\.py sha256:[0-9a-f]+`\n",
            "",
            tracker.rows[50]["body"],
            flags=re.MULTILINE,
        )

        rc, out = run(imap.cmd_audit, tracker, args())

        self.assertEqual(rc, 1)
        self.assertIn("producer-stamp", out)

    def test_a_closed_ticket_makes_the_view_stale(self):
        tracker = self._published_tracker()
        tracker.rows[1]["state"] = "closed"
        rc, out = run(imap.cmd_audit, tracker, args())
        self.assertEqual(rc, 1)
        self.assertIn("stale-derived-view", out)

    def test_a_moved_head_is_informational_not_a_stale_snapshot_finding(self):
        tracker = self._published_tracker()
        tracker.head = "fffffff"
        rc, out = run(imap.cmd_audit, tracker, args())
        self.assertEqual(rc, 0, out)
        self.assertNotIn("stale-snapshot", out)


if __name__ == "__main__":
    unittest.main()
