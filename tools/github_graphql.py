"""Judge a GitHub GraphQL read from its response payload alone.

This module opens no socket.  Callers own the process boundary and their own
completeness checks; this reader accounts only for GraphQL complaints.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import NamedTuple, Sequence


PathPart = str | int


class EvidenceDisposition(Enum):
    """How one declared reader limit is supported."""

    BEHAVIOR = "behavior"
    DECLARED_READING = "declared-reading"


class DeclaredLimit(NamedTuple):
    """One stable name and one boundary the reader does not cross."""

    key: str
    limit: str
    evidence: EvidenceDisposition


DECLARED_LIMITS = (
    DeclaredLimit(
        "literal-command-walk",
        "The consumer walk sees literal GraphQL command lists in Python modules; assembled commands, shell and workflow routes, and docstring commands are invisible.",
        EvidenceDisposition.BEHAVIOR,
    ),
    DeclaredLimit(
        "caller-completeness",
        "A complaint-free response passes even when it is short; pagination and denominator completeness remain with the caller.",
        EvidenceDisposition.BEHAVIOR,
    ),
)
NOT_REACHED = tuple(row.limit for row in DECLARED_LIMITS)


class DeclaredAbsence(NamedTuple):
    """One exact GitHub complaint type and response-data path."""

    type: str
    path: tuple[PathPart, ...]


class GraphQLResult(NamedTuple):
    """Response data and the declared absences used to accept it."""

    data: object
    accounted_absences: tuple[DeclaredAbsence, ...]


class GraphQLResponseError(Exception):
    """A malformed payload or GraphQL complaints that were not accounted for."""

    def __init__(self, message: str, complaints: Sequence[object] = ()) -> None:
        self.complaints = tuple(complaints)
        super().__init__(message)


def _value_at_path(data: object, path: tuple[PathPart, ...]) -> object:
    value = data
    for part in path:
        if isinstance(value, dict) and isinstance(part, str) and part in value:
            value = value[part]
        elif (
            isinstance(value, list)
            and isinstance(part, int)
            and not isinstance(part, bool)
            and 0 <= part < len(value)
        ):
            value = value[part]
        else:
            return _MISSING
    return value


def _describe_complaint(complaint: object) -> str:
    if not isinstance(complaint, dict):
        return repr(complaint)
    complaint_type = complaint.get("type", "<missing type>")
    path = complaint.get("path", "<missing path>")
    message = complaint.get("message", "<missing message>")
    return f"type={complaint_type!r} path={path!r} message={message!r}"


_MISSING = object()


def read_response(
    text: str,
    declared_absences: Sequence[DeclaredAbsence] = (),
) -> GraphQLResult:
    """Return response data when every complaint is an exact declared absence."""
    try:
        document = json.loads(text)
    except (json.JSONDecodeError, TypeError) as error:
        raise GraphQLResponseError(f"GitHub GraphQL response was not JSON: {error}") from error
    if not isinstance(document, dict):
        raise GraphQLResponseError("GitHub GraphQL response was not an object")

    complaints = document.get("errors", [])
    if not isinstance(complaints, list):
        raise GraphQLResponseError("GitHub GraphQL errors member was not a list")
    if "data" not in document:
        if complaints:
            names = "; ".join(_describe_complaint(row) for row in complaints)
            raise GraphQLResponseError(
                f"unaccounted GitHub GraphQL complaints: {names}", complaints
            )
        raise GraphQLResponseError("GitHub GraphQL response had no data member")

    data = document["data"]
    declared = tuple(declared_absences)
    accounted: list[DeclaredAbsence] = []
    unaccounted: list[object] = []
    for complaint in complaints:
        if not isinstance(complaint, dict):
            unaccounted.append(complaint)
            continue
        complaint_type = complaint.get("type")
        complaint_path = complaint.get("path")
        if (
            not isinstance(complaint_type, str)
            or not isinstance(complaint_path, list)
            or any(
                not isinstance(part, (str, int)) or isinstance(part, bool)
                for part in complaint_path
            )
        ):
            unaccounted.append(complaint)
            continue
        absence = DeclaredAbsence(complaint_type, tuple(complaint_path))
        if absence not in declared or _value_at_path(data, absence.path) is not None:
            unaccounted.append(complaint)
            continue
        accounted.append(absence)

    if unaccounted:
        names = "; ".join(_describe_complaint(row) for row in unaccounted)
        raise GraphQLResponseError(
            f"unaccounted GitHub GraphQL complaints: {names}", unaccounted
        )
    return GraphQLResult(data, tuple(accounted))
