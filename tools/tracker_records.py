"""Typed tracker records and adapters for the three publication inputs."""

from __future__ import annotations

from typing import NamedTuple


EVENT_RECORD_KEYS = {
    "issues": "issue",
    "issue_comment": "comment",
    "pull_request_target": "pull_request",
    "pull_request_review": "review",
    "pull_request_review_comment": "comment",
}


class TrackerRecord(NamedTuple):
    body: str
    url: str
    number: int | None
    labels: tuple[str, ...]
    container: str
    surface: str


def from_actions_event(
    document: object, event_name: str, *, require_container: bool = False
) -> TrackerRecord | None:
    """Adapt one supported Actions tracker event; return None out of scope."""
    if not isinstance(document, dict):
        raise ValueError("GitHub event JSON must be an object")
    key = EVENT_RECORD_KEYS.get(event_name)
    if key is None:
        return None
    container_key = "issue" if event_name in ("issues", "issue_comment") else "pull_request"
    container = document.get(container_key)
    record_candidate = document.get(key)
    if not isinstance(container, dict) and require_container:
        raise ValueError(f"GitHub event has no {container_key} object")
    if not isinstance(container, dict):
        container = record_candidate if isinstance(record_candidate, dict) else {}
    record = container if key == container_key else record_candidate
    if not isinstance(record, dict):
        raise ValueError(f"GitHub {event_name} event has no {key} object")
    labels = container.get("labels", [])
    if not isinstance(labels, list) or any(not isinstance(row, dict) for row in labels):
        raise ValueError("GitHub issue labels must be objects")
    body = record.get("body")
    semantic_container = (
        "pull_request"
        if container_key == "pull_request" or "pull_request" in container
        else "issue"
    )
    return TrackerRecord(
        body=body if isinstance(body, str) else "",
        url=record.get("html_url") or container.get("html_url") or "unknown record",
        number=container.get("number"),
        labels=tuple(row.get("name") for row in labels if isinstance(row.get("name"), str)),
        container=semantic_container,
        surface={"issues": "body", "pull_request_target": "body",
                 "issue_comment": "comment", "pull_request_review_comment": "comment",
                 "pull_request_review": "review"}[event_name],
    )


def from_command(
    body: str, *, url: str, number: int | None, labels: tuple[str, ...],
    route: tuple[str, ...], field: str = "body",
) -> TrackerRecord:
    """Adapt a parsed ``gh`` publication and its optional readback context."""
    container = "pull_request" if route[:1] == ("pr",) else "issue"
    if field == "title":
        surface = "title"
    elif route in (("issue", "create"), ("issue", "edit"),
                   ("issue", "view"), ("pr", "create"),
                   ("pr", "edit"), ("pr", "view")):
        surface = "body"
    elif route == ("pr", "review"):
        surface = "review"
    else:
        surface = "comment"
    return TrackerRecord(body, url, number, labels, container, surface)


def from_graphql(record: object, *, surface: str = "body") -> TrackerRecord | None:
    """Adapt one GraphQL Issue/PullRequest reply used for publication readback."""
    if record is None:
        return None
    if not isinstance(record, dict):
        raise ValueError("tracker readback record had the wrong type")
    url = record.get("url")
    if not isinstance(url, str):
        raise ValueError("tracker readback record URL had the wrong type")
    nodes = record.get("labels", {}).get("nodes", []) if isinstance(record.get("labels"), dict) else []
    labels = tuple(row["name"] for row in nodes if isinstance(row, dict) and isinstance(row.get("name"), str))
    body = record.get("body")
    return TrackerRecord(
        body if isinstance(body, str) else "", url, record.get("number"), labels,
        "pull_request" if "/pull/" in url else "issue", surface,
    )
