"""Public-contract tests for the cheap Bash pre-publication stub."""

from __future__ import annotations

import json
import unittest
from unittest import mock

import tracker_publish_stub as stub
import artifact_lock_test_support  # noqa: F401


class BashRegistrationStub(unittest.TestCase):
    def test_decoded_command_without_gh_returns_an_empty_response(self) -> None:
        payload = json.dumps({"tool_input": {"command": "python tools/suite.py"}}).encode()

        with mock.patch.object(stub.subprocess, "run") as run:
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
