"""Contract tests for the owned-browser-tab PreToolUse hook. #1120."""

from __future__ import annotations

import io
import json
from pathlib import Path
import unittest
from contextlib import redirect_stdout

import browser_tab_hook
from prose_bind import NAMING, bind


REPO_ROOT = Path(__file__).resolve().parent.parent


def payload(tool_name: str, tool_input: object) -> dict[str, object]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


class BrowserTabHookContract(unittest.TestCase):
    def decision(self, tool_name: str, tool_input: object) -> dict[str, object] | None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = browser_tab_hook.handle(payload(tool_name, tool_input))
        self.assertEqual(result, 0)
        text = output.getvalue().strip()
        return json.loads(text) if text else None

    def assert_denied(self, tool_name: str, tool_input: object) -> None:
        decision = self.decision(tool_name, tool_input)
        self.assertIsNotNone(decision)
        specific = decision["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("open your own tab and name its id", specific["permissionDecisionReason"])

    def test_claude_in_chrome_navigate_requires_its_tab_id(self) -> None:
        tool = "mcp__claude-in-chrome__navigate"

        self.assert_denied(tool, {"url": "https://example.test"})
        self.assertIsNone(self.decision(tool, {"url": "https://example.test", "tabId": 17}))

    def test_in_app_browser_page_action_requires_its_tab_id(self) -> None:
        tool = "mcp__Claude_Browser__read_page"

        self.assert_denied(tool, {})
        self.assertIsNone(self.decision(tool, {"tabId": 23}))

    def test_file_upload_is_in_the_schema_derived_page_action_population(self) -> None:
        self.assertIn("file_upload", browser_tab_hook.PAGE_ACTIONS)
        self.assert_denied(
            "mcp__claude-in-chrome__file_upload",
            {"paths": ["artifact.txt"], "ref": "ref_1"},
        )

    def test_every_page_action_inside_a_batch_requires_its_tab_id(self) -> None:
        tool = "mcp__claude-in-chrome__browser_batch"
        actions = [
            {"name": "navigate", "input": {"url": "https://example.test", "tabId": 17}},
            {"name": "read_page", "input": {}},
        ]

        self.assert_denied(tool, {"actions": actions})
        actions[1]["input"] = {"tabId": 17}
        self.assertIsNone(self.decision(tool, {"actions": actions}))

    def test_named_batch_page_action_with_no_input_is_denied(self) -> None:
        self.assert_denied(
            "mcp__claude-in-chrome__browser_batch",
            {"actions": [{"name": "read_page"}]},
        )

    def test_a_tab_management_call_is_exempt(self) -> None:
        self.assertIsNone(
            self.decision(
                "mcp__claude-in-chrome__tabs_context_mcp",
                {"createIfEmpty": True},
            )
        )
        self.assertIsNone(
            self.decision(
                "mcp__Claude_Browser__tabs_select",
                {"tabId": 23},
            )
        )

    def test_settings_register_both_browser_families_without_an_if_guard(self) -> None:
        settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        registrations = settings["hooks"]["PreToolUse"]
        registration = next(
            row for row in registrations if "browser_tab_hook.py" in row["hooks"][0]["command"]
        )

        self.assertNotIn("if", registration)
        self.assertIn("mcp__claude-in-chrome__", registration["matcher"])
        self.assertIn("mcp__Claude_Browser__", registration["matcher"])

    def test_page_action_names_are_derived_from_tab_id_schema_properties(self) -> None:
        expected = {
            name
            for schemas in browser_tab_hook.BROWSER_TOOL_SCHEMAS.values()
            for name, schema in schemas.items()
            if "tabId" in schema["inputSchema"].get("properties", {})
            and name not in next(
                roles["management"]
                for family, roles in browser_tab_hook.BROWSER_TOOL_ROLES.items()
                if browser_tab_hook.BROWSER_TOOL_SCHEMAS[family] is schemas
            )
        }

        self.assertEqual(browser_tab_hook.PAGE_ACTIONS, frozenset(expected))

    def test_each_browser_family_uses_its_own_schema_names(self) -> None:
        self.assertIn(
            "tabs_create_mcp",
            browser_tab_hook.BROWSER_TOOL_SCHEMAS["mcp__claude-in-chrome__"],
        )
        self.assertIn(
            "tabs_create",
            browser_tab_hook.BROWSER_TOOL_SCHEMAS["mcp__Claude_Browser__"],
        )

    def test_claude_points_at_the_limits_object_without_copying_its_rows(self) -> None:
        claude = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")

        self.assertIn("browser_tab_hook.DECLARED_LIMITS", claude)
        self.assertEqual((), bind(browser_tab_hook.DECLARED_LIMITS, claude, mode=NAMING))


if __name__ == "__main__":
    unittest.main()
