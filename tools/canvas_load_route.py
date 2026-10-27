"""Require an item-keyed Canvas route and cost at its existing approval gate."""
from pathlib import Path
import re


CONTENT_SKILLS = frozenset({"discussion-post", "discussion-reply"})
DECLARED_LIMITS = (
    "The check reads the latest item-keyed declaration in main-session assistant text before the matched approval; it cannot establish clinician attention, live route availability, first-supported selection, cost accuracy or the route actually used.",
    "A cost is required nonblank text, not a calculated estimate or a semantic assessment of the route's burdens.",
)
ROUTE = re.compile(r"(Raw HTML|Content interface|Typing) — cost: (\S.*)")


class LoadRouteError(ValueError):
    pass


def require_shown(run: Path, key: str, *, after: float, before: float | None, transcripts=None) -> None:
    """Check a strict source/previous-approval-to-reply window without quoting it."""
    from approval_record import assistant_text

    if before is None:
        raise LoadRouteError("Canvas load route approval transcript unreadable")
    shown, unread = assistant_text(run, after=after, before=before, transcripts=transcripts)
    if unread:
        raise LoadRouteError("Canvas load route approval transcript unreadable")
    prefix = f"Canvas load route ({key}): "
    declarations = [
        [line[len(prefix):] for line in message.splitlines() if line.startswith(prefix)]
        for message in shown
    ]
    declarations = [lines for lines in declarations if lines]
    if not declarations or len(declarations[-1]) != 1 or ROUTE.fullmatch(declarations[-1][0]) is None:
        raise LoadRouteError("Canvas load route and nonblank cost were not shown for this item before approval")
