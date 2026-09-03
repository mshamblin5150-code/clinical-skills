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

import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
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
            groups=[{"name": "shared_file.py", "packets": ["PA", "PB"],
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
        tracker = FakeTracker(self.rows, blocked={2: [1]})
        with mock.patch.object(
            imap.tracker_publish_hook, "authorize_issue_body"
        ) as authorize:
            rc, out = run(imap.cmd_publish, tracker, args())

        self.assertEqual(rc, 0, out)
        authorize.assert_called_once()
        self.assertEqual(authorize.call_args.args[1], "issue #50")

    def test_apply_delta_records_the_default_branch_commit_reviewed(self):
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
        self.assertEqual(written["reconciled_through"], "feed123")

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
            # a second init refuses: one map per repository
            with self.assertRaises(imap.MapError):
                run(imap.cmd_init, tracker, ns)

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
            with self.subTest(key=row.key):
                self.assertTrue(row.key)
                self.assertTrue(row.limit)
                self.assertNotIn(row.limit, imap.__doc__)
                self.assertNotIn(row.limit, prose)

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

    def test_unknown_collision_kind_is_forward_compatible_and_ignored(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[{
                "name": "future classifier",
                "kind": "a-kind-this-version-does-not-know",
                "packets": ["PA", "PB"],
            }],
        )

        self.assertEqual(imap.validate_shape(state), [])
        body = imap.render(
            state,
            imap.Live(FakeTracker([issue(1), issue(2)]), state),
            {"commit": "c", "date": "d"},
        )
        derived = body.split(imap.STATE_END, 1)[1]
        self.assertNotIn("a-kind-this-version-does-not-know", derived)

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
        state = state_with([packet("PA", [1])])
        malformed = "graph TD\n    PA[\"PA: #1\"]\n    PA -->|HARD| PX\n    mystery"

        with self.assertRaisesRegex(imap.MapError, "undefined node"):
            imap.verify_mermaid(state, malformed)

        with self.assertRaisesRegex(imap.MapError, "unaccounted Mermaid"):
            imap.verify_mermaid(state, malformed.replace("PX", "PA"))

    def test_duplicate_collision_edges_are_emitted_once(self):
        state = state_with(
            [packet("PA", [1]), packet("PB", [2])],
            groups=[
                {"name": "first", "packets": ["PA", "PB"]},
                {"name": "second", "packets": ["PA", "PB"]},
            ],
        )
        live = imap.Live(FakeTracker([issue(1), issue(2)]), state)

        graph = imap.mermaid(state, live)

        self.assertEqual(graph.count("PA -.- PB"), 1)
        self.assertEqual(imap.verify_mermaid(state, graph).unread, ())


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

    def test_a_closed_ticket_makes_the_view_stale(self):
        tracker = self._published_tracker()
        tracker.rows[1]["state"] = "closed"
        rc, out = run(imap.cmd_audit, tracker, args())
        self.assertEqual(rc, 1)
        self.assertIn("stale-derived-view", out)

    def test_a_moved_head_makes_the_snapshot_stale(self):
        tracker = self._published_tracker()
        tracker.head = "fffffff"
        rc, out = run(imap.cmd_audit, tracker, args())
        self.assertEqual(rc, 1)
        self.assertIn("stale-snapshot", out)


if __name__ == "__main__":
    unittest.main()
