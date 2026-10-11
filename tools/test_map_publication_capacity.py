"""Lossless map compaction and complete publication readback, without a tracker."""
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock
from pathlib import Path

from test_implementation_map import FakeTracker, args, imap, issue, map_issue, packet, state_with


class MapPublicationCapacity(unittest.TestCase):
    def setUp(self):
        self.state = state_with(
            [packet("PA", [1], title="Unicode café", outcome="Keep spaces and\nlines")],
            adr_reviews=[{
                "adr": "docs/adr/0001-example.md", "commit": "a" * 40,
                "no_work": "Historical annotation only.",
            }],
            extra={"nested": [True, None, 7, {"text": "quotes \" and café"}]},
        )

    def historical_block(self):
        # The historical wire format is reproduced independently of the new helper.
        payload = json.dumps(self.state, indent=2, sort_keys=True, ensure_ascii=False)
        return (
            "<details><summary>Machine state (do not hand-edit; "
            "use implementation_map.py)</summary>\n\n"
            f"{imap.STATE_BEGIN}\n```json\n{payload}\n```\n{imap.STATE_END}\n\n</details>"
        )

    def test_compaction_preserves_all_state_and_historical_fingerprint(self):
        historical = self.historical_block()
        compact = imap.state_block(self.state)
        self.assertEqual(imap.extract_state(historical), self.state)
        self.assertEqual(imap.extract_state(compact), self.state)
        self.assertLess(len(compact.encode("utf-8")), len(historical.encode("utf-8")))
        expected = hashlib.sha256(historical.encode("utf-8")).hexdigest()
        self.assertEqual(imap.state_hash(historical), expected)
        self.assertEqual(imap.state_hash(compact), expected)

    def publish(self, transform):
        class Tracker(FakeTracker):
            def update_issue_body(self, number, body):
                super().update_issue_body(number, transform(body))

        tracker = Tracker([map_issue(self.state, 596)])
        output = io.StringIO()
        with (
            mock.patch.object(imap, "snapshot_for", return_value={"commit": "a" * 40, "date": "2026-10-11"}),
            mock.patch.object(imap.tracker_publish_hook, "authorize_issue_body", return_value="graded"),
            redirect_stdout(output),
        ):
            result = imap.publish_body(tracker, 596, self.state, args())
        return result, output.getvalue()

    def test_packet_table_padding_preserves_cells_columns_and_state_hash(self):
        state = state_with([packet("PA", [1], outcome="Keep internal  spaces and café")])
        tracker = FakeTracker([issue(1, labels=["ready"])])
        live = imap.Live(tracker, state)
        body = imap.render(state, live, {"commit": "a" * 40, "date": "2026-10-11"})
        table = body.split("## Packet table\n\n", 1)[1].split("\n\n## Waiting work", 1)[0]
        historical = "\n".join([
            "| Packet | Tickets | Status | Blocked by | Outcome | Collisions |",
            "| --- | --- | --- | --- | --- | --- |",
            "| PA | #1 | " + imap.packet_status(state, live, "PA")
            + " | - | Keep internal  spaces and café | - |",
        ])
        def cells(text):
            return [[cell.strip() for cell in line.split("|")[1:-1]] for line in text.splitlines()]
        self.assertEqual(cells(table), cells(historical))
        self.assertEqual([len(row) for row in cells(table)], [6, 6, 6])
        self.assertLess(len(table.encode("utf-8")), len(historical.encode("utf-8")))
        self.assertEqual(imap.state_hash(body), imap.state_hash(body.replace(table, historical, 1)))

    def test_exact_full_body_readback_succeeds(self):
        result, output = self.publish(lambda body: body)
        self.assertEqual(result.exit_status, 0, output)
        self.assertEqual(result.outcome, imap.PublishOutcome.PUBLISHED)

    def test_same_state_with_changed_derived_text_refuses(self):
        result, output = self.publish(lambda body: body.replace("## Snapshot", "## Altered snapshot", 1))
        self.assertEqual(result.exit_status, 1, output)
        self.assertEqual(result.outcome, imap.PublishOutcome.READ_BACK_FAILED)
        self.assertIn("full body", output)
        self.assertNotIn("published: issue", output)

    def test_same_state_with_changed_trailing_bytes_refuses(self):
        result, output = self.publish(lambda body: body + "\n")
        self.assertEqual(result.exit_status, 1, output)
        self.assertEqual(result.outcome, imap.PublishOutcome.READ_BACK_FAILED)
        self.assertIn("full body", output)

    def init_with_readback(self, transform):
        class Tracker(FakeTracker):
            def get_issue(self, number):
                row = super().get_issue(number)
                row["body"] = transform(row["body"])
                return row

        tracker = Tracker([])
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            initial = Path(directory) / "state.json"
            initial.write_text(json.dumps(state_with([])), encoding="utf-8")
            options = args(state=str(initial), adopt=None, title="Map", label=[])
            with (
                mock.patch.object(imap, "snapshot_for", return_value={"commit": "a" * 40, "date": "2026-10-11"}),
                mock.patch.object(imap.tracker_publish_hook, "authorize_issue_body", return_value="graded"),
                redirect_stdout(output),
            ):
                status = imap._init_under_lock(tracker, options)
        return status, tracker, output.getvalue()

    def test_created_issue_same_state_changed_body_returns_one(self):
        status, tracker, output = self.init_with_readback(lambda body: body + "\n")
        self.assertEqual(len(tracker.created), 1)
        self.assertEqual(status, 1, output)
        self.assertIn("full body differs", output)
        self.assertIn("write result is unconfirmed", output)

    def test_created_issue_unparsable_readback_returns_one(self):
        status, tracker, output = self.init_with_readback(lambda body: "missing state")
        self.assertEqual(len(tracker.created), 1)
        self.assertEqual(status, 1, output)
        self.assertIn("READ-BACK FAILED", output)
        self.assertIn("write result is unconfirmed", output)


if __name__ == "__main__":
    unittest.main()
