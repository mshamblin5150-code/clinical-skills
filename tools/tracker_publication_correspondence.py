"""Describe the checked correspondence between tracker publication hosts.

This module is evidence, not configuration: neither publication host imports it.
``POSTURE_ROWS`` records what the hosts do and never claims that either host is
complete.  The complete boundary belongs to ``DECLARED_LIMITS``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import map_scan
import tracker_bodies
import tracker_branch_scope
import tracker_coordinates
import tracker_event_checks
import tracker_filed_from
import tracker_measurements
import tracker_publish_hook
import tracker_scan


class EvidenceDisposition(str, Enum):
    """How a writer-reach claim is supported.

    This correspondence module is outside the ``run_grader`` family and
    therefore intentionally owns this local disposition vocabulary.
    """

    BEHAVIOR = "behavior"
    DECLARED_READING = "declared-reading"


class Posture(str, Enum):
    DENY = "deny"
    ADVISE = "advise"
    REPORT = "report"
    ABSENT = "absent"


class RuntimeCondition(str, Enum):
    FETCH_FAILED = "fetch failed"
    READBACK_FAILED = "readback failed"
    SYNTHETIC_DECLARATION = "text carrying a synthetic declaration"


class Host(str, Enum):
    HOOK_COMMAND = "hook command route"
    DIRECT_WRITER = "direct-writer seam"
    CHANGED_RECORD = "changed-record event command"
    RECEIPT_PREPUBLICATION = "receipt prepublication event command"


class Writer(str, Enum):
    PUBLISHER_COMMAND = "publisher command route"
    MAP_SESSION = "publisher in-process map write"
    MERGE_RECEIPT = "merge-receipt unwatched write"
    HOURLY_MAP_REFRESH = "hourly map-refresh unwatched write"


class Surface(str, Enum):
    TITLE = "title"
    BODY = "body"
    LABELS = "labels"
    COMMENT = "comment"
    REVIEW = "review"


class Trigger(str, Enum):
    CREATE = "create"
    BODY_EDIT = "body edit"
    TITLE_EDIT = "title edit"
    LABEL_ADDED = "label added"
    LABEL_REMOVED = "label removed"
    COMMENT = "comment"
    REVIEW = "review"
    CLOSE = "close"


@dataclass(frozen=True)
class PostureCell:
    posture: Posture
    rule: str | None = None
    conditions: tuple[tuple[RuntimeCondition, Posture], ...] = ()

    def __post_init__(self) -> None:
        if (self.posture is Posture.ABSENT) != (self.rule is None):
            raise ValueError("an absent cell alone has no emitted rule")
        if len({condition for condition, _posture in self.conditions}) != len(
            self.conditions
        ):
            raise ValueError("a runtime condition may qualify a cell only once")

    def under(self, condition: RuntimeCondition) -> Posture:
        return dict(self.conditions).get(condition, self.posture)


@dataclass(frozen=True)
class PostureRow:
    predicate: str
    surface: Surface
    trigger: Trigger
    hook_command: PostureCell
    direct_writer: PostureCell
    changed_record: PostureCell
    receipt_prepublication: PostureCell

    def cell(self, host: Host) -> PostureCell:
        return {
            Host.HOOK_COMMAND: self.hook_command,
            Host.DIRECT_WRITER: self.direct_writer,
            Host.CHANGED_RECORD: self.changed_record,
            Host.RECEIPT_PREPUBLICATION: self.receipt_prepublication,
        }[host]


@dataclass(frozen=True)
class WriterReach:
    writer: Writer
    host: Host
    reaches: bool
    disposition: EvidenceDisposition
    record: str | None = None

    def __post_init__(self) -> None:
        if self.disposition is EvidenceDisposition.DECLARED_READING and not self.record:
            raise ValueError("a declared reading names its measuring record")
        if self.disposition is EvidenceDisposition.BEHAVIOR and self.record is not None:
            raise ValueError("a behavior row is driven rather than attributed")


ABSENT = PostureCell(Posture.ABSENT)

# These are declarations, deliberately independent of the exported grader
# vocabularies read by ``hook_rule_population`` and ``event_rule_population``.
# A grader rename therefore leaves a stale row behind and makes the completeness
# walk fail instead of silently rewriting the description.
DECLARED_EVENT_PHI_RULES = (
    "dob-with-date",
    "mrn-with-digits",
    "ssn",
    "phone",
    "us-short-date",
)
DECLARED_BODY_RULES = (
    "lost-at-dash",
    "empty-body",
    "literal-at-path",
    "double-encoded",
    "c0-control-character",
    "carriage-return-flanked",
    "literal-newline-escape",
    "doubled-path-separator",
)
DECLARED_MEASUREMENT_RULES = (
    "measurement:stale-base",
    "measurement:invalid-declaration",
    "measurement:inside-quote",
    "measurement:current-base-unreadable",
)
DECLARED_BRANCH_RULES = (
    "branch:repo-relative-link",
    "branch:near-miss",
    "branch:unresolved-path",
    "branch:self-declares-completion",
    "branch:in-flight",
    "branch:blockquote-missing",
    "branch:ancestry-refused",
)
DECLARED_UNREADABLE_RULES = (
    "missing-file",
    "unrooted-path",
    "external-variable",
    "pipe",
    "command-substitution",
    "expansion-exposed-inline",
    "invalid-input",
    "invalid-command",
    "missing-value",
)
DECLARED_UNCLASSIFIED_API_RULES = (
    "unclassified-api-mutation",
    "unclassified-api-endpoint",
    "unclassified-api-identifier",
    "unclassified-api-arguments",
)


def _cell(
    posture: Posture,
    rule: str,
    *conditions: tuple[RuntimeCondition, Posture],
) -> PostureCell:
    return PostureCell(posture, rule, conditions)


def _row(
    predicate: str,
    surface: Surface,
    trigger: Trigger,
    hook: PostureCell = ABSENT,
    direct: PostureCell = ABSENT,
    changed: PostureCell = ABSENT,
    receipt: PostureCell = ABSENT,
) -> PostureRow:
    return PostureRow(predicate, surface, trigger, hook, direct, changed, receipt)


WRITER_REACH = tuple(
    WriterReach(writer, host, reaches, disposition, record)
    for writer, cells in (
        (
            Writer.PUBLISHER_COMMAND,
            {
                Host.HOOK_COMMAND: (True, EvidenceDisposition.BEHAVIOR, None),
                Host.CHANGED_RECORD: (
                    True,
                    EvidenceDisposition.DECLARED_READING,
                    "ADR 0099 ruling 4",
                ),
            },
        ),
        (
            Writer.MAP_SESSION,
            {
                Host.DIRECT_WRITER: (True, EvidenceDisposition.BEHAVIOR, None),
                Host.CHANGED_RECORD: (
                    True,
                    EvidenceDisposition.DECLARED_READING,
                    "ADR 0240 consequence 'Decision 3 of the ticket'",
                ),
            },
        ),
        (
            Writer.MERGE_RECEIPT,
            {
                Host.RECEIPT_PREPUBLICATION: (
                    True,
                    EvidenceDisposition.BEHAVIOR,
                    None,
                ),
                Host.CHANGED_RECORD: (
                    False,
                    EvidenceDisposition.DECLARED_READING,
                    "ADR 0241 measured trigger gap",
                ),
            },
        ),
        (
            Writer.HOURLY_MAP_REFRESH,
            {
                Host.DIRECT_WRITER: (True, EvidenceDisposition.BEHAVIOR, None),
                Host.CHANGED_RECORD: (
                    False,
                    EvidenceDisposition.DECLARED_READING,
                    "ADR 0240 ruling 3 consequences",
                ),
            },
        ),
    )
    for host in Host
    for reaches, disposition, record in (
        cells.get(
            host,
            (
                False,
                EvidenceDisposition.DECLARED_READING,
                {
                    Writer.PUBLISHER_COMMAND: "ADR 0099 ruling 4 publisher measurement",
                    Writer.MAP_SESSION: "ADR 0240 ruling 3 writer measurement",
                    Writer.MERGE_RECEIPT: "ADR 0241 ruling 8 writer measurement",
                    Writer.HOURLY_MAP_REFRESH: "ADR 0241 ruling 8 unwatched-write measurement",
                }[writer],
            ),
        ),
    )
)

HOOK_TRIGGERS = frozenset(
    (Trigger.CREATE, Trigger.BODY_EDIT, Trigger.TITLE_EDIT, Trigger.COMMENT, Trigger.REVIEW)
)
DIRECT_WRITER_KEYS = frozenset(((Surface.BODY, Trigger.BODY_EDIT),))
EVENT_TRIGGERS = frozenset(
    (
        Trigger.CREATE,
        Trigger.BODY_EDIT,
        Trigger.TITLE_EDIT,
        Trigger.LABEL_ADDED,
        Trigger.COMMENT,
        Trigger.REVIEW,
    )
)
PHI_AND_BRANCH_SCOPES = (
    (Surface.BODY, Trigger.CREATE),
    (Surface.TITLE, Trigger.CREATE),
    (Surface.BODY, Trigger.BODY_EDIT),
    (Surface.TITLE, Trigger.TITLE_EDIT),
    (Surface.BODY, Trigger.LABEL_ADDED),
    (Surface.COMMENT, Trigger.COMMENT),
    (Surface.REVIEW, Trigger.REVIEW),
)
BODY_SCOPES = (
    (Surface.BODY, Trigger.CREATE),
    (Surface.BODY, Trigger.BODY_EDIT),
    (Surface.COMMENT, Trigger.COMMENT),
    (Surface.REVIEW, Trigger.REVIEW),
)
PUBLICATION_SCOPES = (
    *BODY_SCOPES,
    (Surface.TITLE, Trigger.CREATE),
    (Surface.TITLE, Trigger.TITLE_EDIT),
)


def _paired_cells(
    surface: Surface,
    trigger: Trigger,
    hook_rule: str,
    event_rule: str,
    *,
    hook_posture: Posture,
    event_reaches: bool = True,
    conditions: tuple[tuple[RuntimeCondition, Posture], ...] = (),
) -> tuple[PostureCell, PostureCell, PostureCell, PostureCell]:
    hook = (
        PostureCell(hook_posture, hook_rule, conditions)
        if trigger in HOOK_TRIGGERS
        else ABSENT
    )
    direct = (
        PostureCell(hook_posture, hook_rule, conditions)
        if (surface, trigger) in DIRECT_WRITER_KEYS
        else ABSENT
    )
    changed = (
        PostureCell(Posture.REPORT, event_rule, tuple(
            (condition, Posture.REPORT) for condition, _posture in conditions
        ))
        if event_reaches and trigger in EVENT_TRIGGERS
        else ABSENT
    )
    receipt = (
        PostureCell(Posture.REPORT, event_rule, tuple(
            (condition, Posture.REPORT) for condition, _posture in conditions
        ))
        if trigger is Trigger.COMMENT
        else ABSENT
    )
    return hook, direct, changed, receipt


def _paired_row(
    predicate: str,
    surface: Surface,
    trigger: Trigger,
    hook_rule: str,
    event_rule: str,
    *,
    hook_posture: Posture,
    event_reaches: bool = True,
    conditions: tuple[tuple[RuntimeCondition, Posture], ...] = (),
) -> PostureRow:
    return PostureRow(
        predicate,
        surface,
        trigger,
        *_paired_cells(
            surface,
            trigger,
            hook_rule,
            event_rule,
            hook_posture=hook_posture,
            event_reaches=event_reaches,
            conditions=conditions,
        ),
    )


POSTURE_ROWS = (
    _row("no-publication-on-label-removal", Surface.LABELS, Trigger.LABEL_REMOVED),
    _row("no-publication-on-bodyless-review", Surface.REVIEW, Trigger.REVIEW),
    _row("no-publication-on-close", Surface.BODY, Trigger.CLOSE),
    _row(
        "filed-from-presence",
        Surface.BODY,
        Trigger.CREATE,
        _cell(Posture.DENY, "filed-from:create"),
        changed=_cell(Posture.REPORT, "filed-from:opened"),
    ),
    _row(
        "filed-from-preservation",
        Surface.BODY,
        Trigger.BODY_EDIT,
        _cell(
            Posture.DENY,
            "filed-from:edit",
            (RuntimeCondition.READBACK_FAILED, Posture.ABSENT),
        ),
        changed=_cell(Posture.REPORT, "filed-from:edited"),
    ),
    _row("filed-from-not-graded-on-comment", Surface.COMMENT, Trigger.COMMENT),
    _row(
        "aar-working-source-quotation",
        Surface.COMMENT,
        Trigger.COMMENT,
        _cell(Posture.DENY, "aar-quotation"),
    ),
    _row(
        "comment-verdict-discriminator",
        Surface.COMMENT,
        Trigger.COMMENT,
        _cell(Posture.ADVISE, "verdict:missing-discriminator"),
    ),
    _row(
        "retired-correction-citation",
        Surface.COMMENT,
        Trigger.COMMENT,
        _cell(Posture.ADVISE, "citation:retired-correction-rule"),
    ),
    _row(
        "implementation-map-producer-stamp",
        Surface.BODY,
        Trigger.BODY_EDIT,
        direct=_cell(Posture.DENY, "producer-stamp"),
        changed=_cell(Posture.REPORT, "producer-stamp"),
    ),
    *(
        _paired_row(
            rule.removeprefix("phi-").replace(":", "-"),
            surface,
            trigger,
            f"phi:{rule}",
            rule,
            hook_posture=Posture.ADVISE,
            conditions=((RuntimeCondition.SYNTHETIC_DECLARATION, Posture.ADVISE),),
        )
        for rule in DECLARED_EVENT_PHI_RULES
        for surface, trigger in PHI_AND_BRANCH_SCOPES
    ),
    *(
        _paired_row(
            f"body-{kind}",
            surface,
            trigger,
            f"body:{kind}",
            kind,
            hook_posture=Posture.DENY,
        )
        for kind in DECLARED_BODY_RULES
        for surface, trigger in BODY_SCOPES
    ),
    *(
        _paired_row(
            f"title-{kind}",
            surface,
            trigger,
            f"body:{kind}",
            kind,
            hook_posture=Posture.DENY,
            event_reaches=False,
        )
        for kind in ("c0-control-character", "carriage-return-flanked")
        for surface, trigger in (
            (Surface.TITLE, Trigger.CREATE),
            (Surface.TITLE, Trigger.TITLE_EDIT),
        )
    ),
    *(
        _paired_row(
            "coordinate-accompaniment",
            surface,
            trigger,
            "coordinate:unanchored",
            "coordinate:unanchored",
            hook_posture=Posture.DENY,
            event_reaches=surface is not Surface.TITLE,
        )
        for surface, trigger in PUBLICATION_SCOPES
    ),
    *(
        _paired_row(
            rule.replace(":", "-"),
            surface,
            trigger,
            rule,
            rule,
            hook_posture=Posture.DENY,
            event_reaches=surface is not Surface.TITLE,
        )
        for rule in DECLARED_MEASUREMENT_RULES
        for surface, trigger in PUBLICATION_SCOPES
    ),
    *(
        _paired_row(
            rule.replace(":", "-"),
            surface,
            trigger,
            rule,
            rule,
            hook_posture=(
                Posture.ADVISE if rule == "branch:near-miss" else Posture.DENY
            ),
            conditions=(
                ((RuntimeCondition.FETCH_FAILED, Posture.ADVISE),)
                if rule == "branch:unresolved-path"
                else ()
            ),
        )
        for rule in DECLARED_BRANCH_RULES
        for surface, trigger in PHI_AND_BRANCH_SCOPES
    ),
    *(
        _row(
            f"hook-unreadable-{rule}",
            surface,
            trigger,
            _cell(Posture.DENY, rule),
        )
        for rule in DECLARED_UNREADABLE_RULES
        for surface, trigger in PUBLICATION_SCOPES
    ),
    *(
        _row(
            f"hook-{rule}",
            surface,
            trigger,
            _cell(Posture.DENY, rule),
        )
        for rule in DECLARED_UNCLASSIFIED_API_RULES
        for surface, trigger in PUBLICATION_SCOPES
    ),
    *(
        _row(
            rule.replace(":", "-"),
            surface,
            trigger,
            _cell(Posture.ADVISE, rule),
            direct=(
                _cell(Posture.ADVISE, rule)
                if (surface, trigger) in DIRECT_WRITER_KEYS
                else ABSENT
            ),
        )
        for rule in ("phi:corpus-name", "phi:corpus-date")
        for surface, trigger in PUBLICATION_SCOPES
    ),
)


def hook_rule_population() -> frozenset[str]:
    return frozenset(
        (
            *tracker_publish_hook.REDACTION_WALK_KINDS,
            *tracker_measurements.RULES,
            *tracker_filed_from.PUBLICATION_RULES,
            *tracker_publish_hook.AAR_RULES,
            *tracker_publish_hook.UNREADABLE_RULES,
            *tracker_publish_hook.UNCLASSIFIED_API_RULES,
        )
    )


def event_rule_population() -> frozenset[str]:
    selected_modules = {check.module for check in tracker_event_checks.ALL_CHECKS}
    vocabularies = {
        "tracker_scan": tracker_scan.EVENT_RULES,
        "tracker_branch_scope": tracker_branch_scope.BRANCH_RULES,
        "tracker_bodies": tracker_bodies.KINDS,
        "tracker_coordinates": (tracker_coordinates.UNANCHORED,),
        "tracker_measurements": tracker_measurements.RULES,
        "tracker_filed_from": tracker_filed_from.EVENT_RULES,
        "map_scan": map_scan.EVENT_RULES,
    }
    if selected_modules != set(vocabularies):
        raise ValueError("event-check vocabulary does not match the dispatcher")
    return frozenset(rule for rules in vocabularies.values() for rule in rules)


def named_rules(rows: tuple[PostureRow, ...] = POSTURE_ROWS) -> frozenset[str]:
    return frozenset(
        cell.rule
        for row in rows
        for cell in (
            row.hook_command,
            row.direct_writer,
            row.changed_record,
            row.receipt_prepublication,
        )
        if cell.rule is not None
    )


def unnamed_rules(
    population: frozenset[str] | None = None,
    rows: tuple[PostureRow, ...] = POSTURE_ROWS,
) -> frozenset[str]:
    actual = hook_rule_population() | event_rule_population()
    return (actual if population is None else population) - named_rules(rows)


DECLARED_LIMITS = (
    (
        "a new sentence pairing the publication hosts is not discovered",
        "The naming bind covers the current paired-host prose and does not detect a newly authored pairing sentence.",
    ),
    (
        "a runtime state read outside a host seam is not forced",
        "Behavior tests qualify only state supplied through the public input and I/O seams of each host.",
    ),
    (
        "GitHub-side writer reach is a declared reading",
        "GitHub suppresses follow-up workflow events for built-in-token writes, so those reach facts are named from their measuring records rather than driven here.",
    ),
    (
        "publication-host completeness is not graded",
        "The object checks whether its correspondence claims remain true and never establishes that either host grades every publication it should.",
    ),
    (
        "ad-hoc argv-list publications cross neither host",
        "The unmodeled argv-list publications measured by ADR 0188 call neither the command hook nor the direct-writer seam.",
    ),
)

# Ruling 11 deliberately enumerates only the pairing prose that existed when
# #1149 built.  Discovering a future sentence is outside ``DECLARED_LIMITS``.
PAIRING_PROSE = (
    "CLAUDE.md",
    "docs/agents/issue-tracker.md",
    "tools/tracker_bodies.py",
    "docs/adr/0099-a-control-character-in-a-published-tracker-body-is-refused-at-the-publish-event-and-graded-at-every-one.md",
    "docs/adr/0141-a-collapsed-escape-is-repaired-by-mechanical-inverse-and-the-residual-red-needs-no-register.md",
    "docs/adr/0155-the-map-render-stamps-its-producer-and-the-graph-draws-only-what-carries-an-edge.md",
    "docs/adr/0166-codebase-architecture-marks-a-lineage-by-descent.md",
    "docs/adr/0169-a-ticket-states-what-filed-it-on-an-append-only-line.md",
    "docs/adr/0177-both-publish-routes-grade-a-body-through-one-grader-and-a-lost-body-refuses.md",
    "docs/adr/0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md",
    "docs/adr/0189-a-coordinate-is-never-the-locator-and-its-anchor-is-graded-at-publication.md",
)


def prose_row_claims(rows: tuple[PostureRow, ...] = POSTURE_ROWS) -> tuple[str, ...]:
    """Render long row claims solely for the no-copy naming bind."""
    return tuple(
        f"{row.predicate} on {row.surface.value} for {row.trigger.value} has "
        + ", ".join(
            f"{host.value} {row.cell(host).posture.value} {row.cell(host).rule or 'without a rule'}"
            for host in Host
        )
        for row in rows
    )


def posture_row(predicate: str, surface: Surface, trigger: Trigger) -> PostureRow:
    matches = tuple(
        row
        for row in POSTURE_ROWS
        if (row.predicate, row.surface, row.trigger) == (predicate, surface, trigger)
    )
    if len(matches) != 1:
        raise KeyError((predicate, surface, trigger))
    return matches[0]
