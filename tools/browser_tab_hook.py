#!/usr/bin/env python3
"""Refuse a browser page action that names no tab. #1120.

The page-action roster is derived from the committed ``tools/list`` schema
snapshot exposed as ``BROWSER_TOOL_SCHEMAS``: a nonmanagement tool is
addressable by tab when its input schema carries the singular ``tabId``
property. ``browser_batch`` embeds those same named actions. Schema-adjacent
roles distinguish management and creation operations without a second action
roster in code.

``DECLARED_LIMITS`` is the complete boundary of this refusing hook. ``CLAUDE.md``
points at that object and copies none of its rows.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Any, Mapping

from console_codec import require_python_floor, use_utf8


BROWSER_FAMILIES = (
    "mcp__claude-in-chrome__",
    "mcp__Claude_Browser__",
)


SCHEMA_SNAPSHOT = Path(__file__).resolve().parent.parent / "reference" / "browser-tool-schemas.json"


def _load_tool_schemas(
    path: Path = SCHEMA_SNAPSHOT,
) -> tuple[
    Mapping[str, Mapping[str, Mapping[str, object]]],
    Mapping[str, Mapping[str, object]],
]:
    document = json.loads(path.read_text(encoding="utf-8"))
    families = document.get("families")
    if not isinstance(families, dict) or set(families) != set(BROWSER_FAMILIES):
        raise ValueError("browser tool schema snapshot has the wrong family set")
    loaded: dict[str, Mapping[str, Mapping[str, object]]] = {}
    loaded_roles: dict[str, Mapping[str, object]] = {}
    for family, tools in families.items():
        if not isinstance(tools, dict):
            raise ValueError("browser tool schema snapshot has no tools object")
        schemas: dict[str, Mapping[str, object]] = {}
        roles = tools.get("$roles")
        if not isinstance(roles, dict):
            raise ValueError("browser tool schema snapshot has no family roles")
        management = roles.get("management")
        if not isinstance(management, list) or not all(
            isinstance(item, str) for item in management
        ):
            raise ValueError("browser tool schema snapshot has invalid management roles")
        for name, properties in tools.items():
            if name == "$roles":
                continue
            if not isinstance(name, str) or not isinstance(properties, list) or not all(
                isinstance(item, str) for item in properties
            ):
                raise ValueError("browser tool schema snapshot has an invalid tool row")
            schemas[name] = MappingProxyType(
                {
                    "inputSchema": MappingProxyType(
                        {
                            "type": "object",
                            "properties": MappingProxyType(
                                {item: MappingProxyType({}) for item in properties}
                            ),
                        }
                    )
                }
            )
        loaded[family] = MappingProxyType(schemas)
        loaded_roles[family] = MappingProxyType(
            {
                **roles,
                "management": frozenset(management),
            }
        )
    return MappingProxyType(loaded), MappingProxyType(loaded_roles)


BROWSER_TOOL_SCHEMAS, BROWSER_TOOL_ROLES = _load_tool_schemas()
PAGE_ACTIONS_BY_FAMILY = MappingProxyType(
    {
        family: frozenset(
            name
            for name, schema in schemas.items()
            if "tabId" in schema["inputSchema"].get("properties", {})
            and name not in BROWSER_TOOL_ROLES[family]["management"]
        )
        for family, schemas in BROWSER_TOOL_SCHEMAS.items()
    }
)
PAGE_ACTIONS = frozenset(
    name for actions in PAGE_ACTIONS_BY_FAMILY.values() for name in actions
)

DECLARED_LIMITS = (
    (
        "schema snapshot currency",
        "a new or renamed browser tool is not classified until its reviewed schema is added",
    ),
    (
        "Codex REPL browser actions",
        "a tab choice inside REPL code is invisible to this parameter-level hook",
    ),
    (
        "tab ownership",
        "a named tab can belong to another context and is reported only by the after-action review",
    ),
)

REMEDY = "open your own tab and name its id"


def local_tool_name(tool_name: str) -> str | None:
    return next(
        (tool_name[len(prefix) :] for prefix in BROWSER_FAMILIES if tool_name.startswith(prefix)),
        None,
    )


def tool_family(tool_name: str) -> str | None:
    return next((prefix for prefix in BROWSER_FAMILIES if tool_name.startswith(prefix)), None)


def _has_tab_id(tool_input: Mapping[str, Any]) -> bool:
    value = tool_input.get("tabId")
    return value is not None and value != ""


def batch_actions(
    tool_name: str, tool_input: Mapping[str, Any]
) -> tuple[tuple[str, Mapping[str, Any]], ...]:
    """Return every structurally valid inner action from this family's batch tool."""
    family = tool_family(tool_name)
    local = local_tool_name(tool_name)
    if family is None or local != BROWSER_TOOL_ROLES[family]["batch"]:
        return ()
    actions = tool_input.get("actions")
    if not isinstance(actions, list):
        return ()
    recognized = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        name = action.get("name")
        action_input = action.get("input", action.get("params"))
        if isinstance(name, str):
            recognized.append(
                (name, action_input if isinstance(action_input, dict) else {})
            )
    return tuple(recognized)


def page_actions(
    tool_name: str, tool_input: Mapping[str, Any]
) -> tuple[tuple[str, Mapping[str, Any]], ...]:
    """Return direct or batched page actions recognized by the schema snapshot."""
    local = local_tool_name(tool_name)
    family = tool_family(tool_name)
    if local is None or family is None:
        return ()
    page_action_names = PAGE_ACTIONS_BY_FAMILY[family]
    if local in page_action_names:
        return ((local, tool_input),)
    return tuple(
        (name, action_input)
        for name, action_input in batch_actions(tool_name, tool_input)
        if name in page_action_names
    )


def _denial(detail: str) -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"{detail}; {REMEDY}.",
        }
    }


def handle(payload: Mapping[str, Any]) -> int:
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_name, str) or not isinstance(tool_input, dict):
        return 0
    for index, (name, action_input) in enumerate(page_actions(tool_name, tool_input), 1):
        if _has_tab_id(action_input):
            continue
        local = local_tool_name(tool_name)
        detail = (
            f"browser_batch action {index} ({name}) names no tab"
            if local == "browser_batch"
            else f"{name} names no tab"
        )
        print(json.dumps(_denial(detail)))
        return 0
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    return handle(payload if isinstance(payload, dict) else {})


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
