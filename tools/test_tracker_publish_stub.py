"""Public-contract tests for the cheap Bash pre-publication stub."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import tracker_publish_stub as stub
import tracker_publish_marker
import artifact_lock_test_support  # noqa: F401


_REAL_RECORD_RUN = stub.record_run
_RECORD_RUN_PATCHER = None


def setUpModule() -> None:
    global _RECORD_RUN_PATCHER
    _RECORD_RUN_PATCHER = mock.patch.object(stub, "record_run")
    _RECORD_RUN_PATCHER.start()


def tearDownModule() -> None:
    assert _RECORD_RUN_PATCHER is not None
    _RECORD_RUN_PATCHER.stop()


class BashRegistrationStub(unittest.TestCase):
    def test_decoded_command_without_gh_returns_an_empty_response(self) -> None:
        payload = json.dumps({"tool_input": {"command": "python tools/suite.py"}}).encode()

        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "record.json"
            with (
                mock.patch.object(
                    tracker_publish_marker, "marker_path", return_value=target
                ),
                mock.patch.object(stub, "record_run", _REAL_RECORD_RUN),
                mock.patch.object(stub.subprocess, "run") as run,
            ):
                result = stub.dispatch(payload)

            record = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(result, b"{}")
        self.assertEqual(record["version"], tracker_publish_marker.SCHEMA_VERSION)
        run.assert_not_called()

    def test_a_failed_marker_write_does_not_change_the_stub_response(self) -> None:
        payload = json.dumps({"tool_input": {"command": "python tools/suite.py"}}).encode()

        with (
            mock.patch.object(stub, "record_run", _REAL_RECORD_RUN),
            mock.patch.object(
                tracker_publish_marker,
                "write_marker",
                side_effect=OSError("read only"),
            ),
            mock.patch.object(stub.subprocess, "run") as run,
        ):
            result = stub.dispatch(payload)

        self.assertEqual(result, b"{}")
        run.assert_not_called()

    def test_decoded_heredoc_text_with_gh_runs_the_full_hook(self) -> None:
        payload = json.dumps(
            {"tool_input": {"command": "bash <<'SH'\ngh issue view 5\nSH"}}
        ).encode()
        completed = mock.Mock(
            returncode=0, stdout=b'{"hookSpecificOutput": {}}', stderr=b""
        )

        with mock.patch.object(stub.subprocess, "run", return_value=completed) as run:
            result = stub.dispatch(payload)

        self.assertEqual(result, completed.stdout)
        self.assertEqual(run.call_args.kwargs["input"], payload)

    def test_an_undecodable_payload_fails_closed_into_the_full_hook(self) -> None:
        payload = b"{not-json"
        completed = mock.Mock(
            returncode=0, stdout=b'{"hookSpecificOutput": {}}', stderr=b""
        )

        with mock.patch.object(stub.subprocess, "run", return_value=completed) as run:
            result = stub.dispatch(payload)

        self.assertEqual(result, completed.stdout)
        self.assertEqual(run.call_args.kwargs["input"], payload)


if __name__ == "__main__":
    unittest.main()
