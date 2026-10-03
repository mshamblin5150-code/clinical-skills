"""Inspect tracker text immediately before a ``gh`` publication.

The command is a Claude Code ``PreToolUse`` hook: it reads one hook payload as
JSON from stdin and writes one hook response as JSON to stdout. It never prints
the text it scans. Counts, rule names, and the field to edit are the complete
reporting surface.

**A publication whose text cannot be read is refused rather than allowed**, on
every kind in ``UNREADABLE_REMEDIES``, and only on a route in
``command_reader.PUBLISH_ROUTES`` -- an unrecognized command is never touched. #745: the gate
returned *allow* whenever it could not parse its own input, so the one limb
that refuses evaporated exactly when the hook was least able to vouch for the
text. Each kind's remedy names the by-hand command that grades the file.

**What it reads is the command as typed, not the shell's expansion of it.** An
inline body or title is readable only when every segment is single-quoted or an
outside-quote escaped character, so the hook can reproduce exactly what the
shell will deliver. Body-file resolution is reconstructed rather than observed:
same-command assignments are substituted, including where a variable names only
the leading part of a path, and a Git Bash ``/c/...`` path is also tried in its
Windows spelling. What is left unreadable is refused above.

Every readable publication is graded through ``analyze``. On the command route,
each denying row refuses and carries its rule's remedy. The direct writer uses
the same analysis and preserves advisory rows as report lines; its map-specific
producer-stamp check remains on top. A title receives PHI shape, the two
title-scoped integrity predicates, coordinate accompaniment, and branch path
triggers; measurement, Filed-from, and every other body-integrity row remain
body-only. Policy limits belong to ``NOT_REACHED``; reading limits belong to
``command_reader.NOT_REACHED`` rather than copied into this docstring or ``CLAUDE.md``.

**One row advises on a retired citation**: a paragraph stating the
correct-in-place rule beside ``#436``, which rules nothing about corrections.
ADR 0191 ruled it reported rather than refused, because a record discussing the
defect quotes the pairing on purpose and tracker prose carries no
mention-versus-use exemption. It grades one literal pairing, grown on recorded
instances, and how narrow that is belongs to ``NOT_REACHED`` with every other
ceiling.

One anchor-free loose classifier also finds literal publications the precise
single-call reader did not reproduce, including quoted argv lists. A modeled
command carrying such a publication is refused unread before any partial grade;
the same classifier bounds the unmodeled-shell refusal and the implementation-
map post-hook's observation. The reading boundary belongs to ``command_reader.NOT_REACHED``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import NamedTuple

import phi_scan
from github_graphql import DeclaredAbsence, GraphQLResponseError, read_response
import tracker_bodies
import tracker_coordinates
import tracker_measurements
import tracker_branch_scope
import tracker_filed_from
import tracker_readback
import command_reader
import shell_reader
from command_reader import (
    COMMAND_TOOLS, MODELED_SHELL, PUBLISH_ROUTES, Publication, Extraction,
    Unreadable, extract,
)
from tracker_publish_marker import record_run
from console_codec import require_python_floor, use_utf8
from tracker_records import TrackerRecord, from_command, from_graphql
from tracker_bodies import ordinary_paragraph_prose


# Measured before being written, per ADR 0109 ruling 13. Across 371 real issue
# bodies and the text in 11 real run directories on 2026-09-02, an 80-character
# normalized span appeared in seven bodies; shorter floors rapidly admitted
# ordinary overlap. The gate fires only for a body file under
# ``<run>/aar/publications/`` and therefore changes no ordinary publication.
AAR_QUOTE_SPAN_CHARS = 80
AAR_PUBLICATION_PARTS = ("aar", "publications")
AAR_QUOTATION_RULE = "aar-quotation"
AAR_RULES = (AAR_QUOTATION_RULE,)

NOT_REACHED = (
    (
        "the GitHub web UI bypasses the hook",
        "Tracker text published through the GitHub web UI never crosses "
        "this Claude Code pre-publication boundary.",
    ),
    (
        "disabled or overridden hooks bypass the check",
        "A session started with hooks disabled or with overriding settings "
        "can publish without this hook running.",
    ),
    (
        "retained pre-edit revisions remain readable",
        "GitHub retains earlier revisions of edited tracker records, and "
        "this hook cannot read or remove those preserved versions.",
    ),
    (
        "workspace trust can silently suppress registration",
        "An unaccepted workspace trust prompt can silently prevent the "
        "project hook from registering in a new worktree.",
    ),
    (
        "a commit outside a session does not run the marker",
        "No registered session hook runs for a commit made outside a "
        "session, so that checkout's record remains absent or retains an "
        "older date.",
    ),
    (
        "the record belongs to the checkout whose hook module ran",
        "Changing directories into a sibling checkout does not move the "
        "hook module, so the record identifies the session's project "
        "checkout rather than the directory where its command happened to "
        "run.",
    ),
    (
        "disabled or overridden hooks leave the record aging",
        "A session with hooks disabled or project settings overridden "
        "cannot refresh its checkout's record because the marker entry "
        "point never runs.",
    ),
    (
        "the marker is not a publish-time guarantee",
        "The record is a commit-time notice that the hook ran in the "
        "checkout; it cannot establish that later publications still cross "
        "the hook.",
    ),
    (
        "moving or renaming a checkout changes its identity",
        "A checkout path supplies the record identity, so moving or "
        "renaming that checkout makes the notice read never until the hook "
        "runs there.",
    ),
    (
        "no route rule covers the cause side of escape collapse",
        "A residual reproducible inline body is not thereby text-graded for "
        "a partial literal-newline collapse. The body grader declares its "
        "own text boundary; no additional command-form rule refuses that "
        "cause.",
    ),
    (
        "the refusing hook covers one of two publishers",
        "This Claude Code hook prevents a damaged publication from this "
        "publisher only. The GitHub workflow reaches no unwatched write "
        "after publication; merge receipts are graded before they post.",
    ),
    (
        "a failed tracker readback leaves the publication context-blind",
        "When the batched tracker fetch fails, the hook says that current "
        "record state and labels were not read and continues without "
        "claiming that the cited records are current.",
    ),
    (
        "the fetched origin can be a non-canonical repository",
        "Branch-scope grading fetches and reads the remote named origin "
        "even when that remote is not mshamblin5150-code/clinical-skills.",
    ),
    (
        "an AAR paraphrase passes the quotation gate",
        "The AAR gate refuses copied spans and cannot recognize a "
        "paraphrase of private working material.",
    ),
    (
        "a stock discriminator clause can satisfy the verdict form check",
        "The check establishes that the comment carries the declared form "
        "and cannot establish that its counterfactual is true.",
    ),
    (
        "the retired-citation row reaches one literal pairing",
        "It reports the correct-in-place rule stated beside #436 and "
        "nothing else. A paraphrase of the rule, the same rule attributed "
        "to another wrong record, and a citation whose claim about any "
        "other record is false are all outside it. Nothing here can "
        "establish that a cited record says what a sentence claims it says.",
    ),
    (
        "unreadable and unclassified publications are refused",
        "The hook refuses the reader's unreadable fields and unclassified "
        "API calls rather than guessing at their publication text. The "
        "reading boundary belongs to command_reader.NOT_REACHED.",
    ),
)


def with_tracker_record(
    publication: Publication,
    *,
    route: tuple[str, ...],
    context: TrackerRecord | dict | None,
) -> Publication:
    """Bind command text to its semantic record before policy grading."""
    if publication.record is not None:
        return publication
    if isinstance(context, TrackerRecord):
        url = context.url
        number = context.number
        labels = context.labels
    elif isinstance(context, dict):
        url = context.get("url", "draft record")
        number = context.get("number")
        labels = tuple(
            row.get("name") if isinstance(row, dict) else row
            for row in context.get("labels", [])
            if isinstance(row, (dict, str))
        )
    else:
        url = "draft record"
        number = None
        labels = ()
    record = from_command(
        publication.text,
        url=url,
        number=number,
        labels=labels,
        route=route,
        field=publication.field,
    )
    return replace(publication, record=record)


class Finding(NamedTuple):
    rule: str
    count: int
    field: str
    posture: str


class Analysis(NamedTuple):
    findings: tuple[Finding, ...]
    report: str


class CommandGrade(NamedTuple):
    scanned: bool
    denied: bool
    report: str


_USE_ANALYSIS_ROUTE = object()


COMMENT_ROUTES = (
    ("issue", "comment"),
    ("issue", "close"),
    ("pr", "comment"),
    ("pr", "review"),
)
DISCRIMINATOR_CLAUSE = re.compile(
    r"\bunder the claim['’]s negation\b",
    re.IGNORECASE,
)
RETIRED_CITATION = "citation:retired-correction-rule"
#: The correct-in-place rule as the tracker states it, matched without regard to
#: case. Records carrying one of these wordings attribute it to #436, which rules
#: nothing about corrections. Grown on evidence written in this repository, the
#: way ``spelling_scan``'s table grows, rather than by a rule over citations. How
#: many records that was on 2026-09-12 is ADR 0191's to state: it is a count over
#: a live tracker that nothing here re-derives, and the repair that record orders
#: drives it to zero.
CORRECT_IN_PLACE_PHRASES = (
    "below the advice",
    "acts on the advice",
    "acting on the advice",
)
RETIRED_CORRECTION_TICKET = re.compile(r"(?:#|issues/)436\b")
RETIRED_CITATION_REMEDY = (
    "#436 is a 160-char extraction ticket and rules nothing about corrections; "
    "cite ADR 0191, which rules this for the tracker. When repairing a record "
    "written before it, ADR 0016 goes in the sentence and ADR 0191 on the "
    "dated line, because that record's sentence says what a past session "
    "relied on"
)
PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")
REDACTION_WALK_KINDS = (
    "phi:corpus-name",
    "phi:corpus-date",
    *(f"phi:{kind}" for kind in phi_scan.SHAPE_RULES),
    *(f"body:{kind}" for kind in tracker_bodies.KINDS),
    tracker_coordinates.UNANCHORED,
    "verdict:missing-discriminator",
    RETIRED_CITATION,
    *tracker_branch_scope.BRANCH_RULES,
)


def retired_citation_paragraphs(text: str) -> int:
    """Count paragraphs stating the correct-in-place rule beside the retired #436.

    The unit is the paragraph rather than a character window, and that is
    measured rather than chosen: over the population ADR 0191 states, a window is
    flat from the widest observed separation upward and the paragraph rule
    reproduces the identical members with no value to defend. It counts a
    deliberate quotation too -- tracker prose carries no mention-versus-use
    exemption, and the two this repository does have are a Python pragma and an
    own-line marker, neither of which a tracker record can use -- which is why
    the row advises and never denies.
    """
    return sum(
        1
        for paragraph in PARAGRAPH_BREAK.split(text.replace("\r\n", "\n").casefold())
        if any(phrase in paragraph for phrase in CORRECT_IN_PLACE_PHRASES)
        and RETIRED_CORRECTION_TICKET.search(paragraph)
    )


LOST_BODY_REMEDY = (
    "the body did not land; write it to a file and pass that file's "
    "absolute path to --body-file"
)
BODY_REMEDIES = {
    tracker_bodies.LOST_AT_DASH: LOST_BODY_REMEDY,
    tracker_bodies.EMPTY_BODY: LOST_BODY_REMEDY,
    tracker_bodies.LITERAL_AT_PATH: LOST_BODY_REMEDY,
    tracker_bodies.DOUBLE_ENCODED: (
        "rewrite text damaged through a cp1252 path as UTF-8; for a genuine "
        "mention only, put the deliberately named sequence in backticks, "
        "because backticks also hide damage"
    ),
    tracker_bodies.C0_CONTROL_CHARACTER: (
        "remove the raw C0 control character and restore the intended text"
    ),
    tracker_bodies.CARRIAGE_RETURN_FLANKED: (
        "replace the flanked carriage return with the intended text or line break"
    ),
    tracker_bodies.LITERAL_NEWLINE_ESCAPE: (
        "replace the literal newline escape with the intended real line break"
    ),
    tracker_bodies.DOUBLED_PATH_SEPARATOR: (
        "restore the intended single path separator"
    ),
}
COORDINATE_REMEDY = (
    "place an anchor beside the coordinate: a backticked identifier or span, "
    "a prose quotation, or an immediately following fenced or quoted block"
)


def body_remedy(kind: str, route: tuple[str, ...]) -> str:
    """The repair for one body row on the publication route that produced it."""
    if kind == tracker_bodies.EMPTY_BODY and route == ("pr", "review"):
        return (
            "omit the --body flag if this is an approval; otherwise supply "
            "the intended review text"
        )
    return BODY_REMEDIES[kind]


def redaction_walk_report(triggered: set[str]) -> str:
    """Report the declared denominator and any kind the fixtures did not trigger."""
    unread = tuple(kind for kind in REDACTION_WALK_KINDS if kind not in triggered)
    remainder = ", ".join(unread) if unread else "none"
    return (
        f"tracker redaction walk: {len(REDACTION_WALK_KINDS) - len(unread)}/"
        f"{len(REDACTION_WALK_KINDS)} kinds triggered; unread: {remainder}"
    )


def _aar_run_directory(path: Path | None) -> Path | None:
    """The run root for an AAR-owned body file, otherwise ``None``."""
    if path is None or path.parent.name != AAR_PUBLICATION_PARTS[1]:
        return None
    aar = path.parent.parent
    if aar.name != AAR_PUBLICATION_PARTS[0]:
        return None
    return aar.parent


def _normalized_span_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def _quotes_run_material(publication: Publication) -> bool:
    """Whether one AAR body repeats a measured-length span from its run.

    ``aar/`` is excluded because its extract necessarily contains the complete
    reduced conversation. The gate's subject is the working material the review
    was about, not the review record describing conduct.
    """
    run = _aar_run_directory(publication.path)
    body = _normalized_span_text(publication.text)
    if run is None or len(body) < AAR_QUOTE_SPAN_CHARS:
        return False
    spans = {
        body[index : index + AAR_QUOTE_SPAN_CHARS]
        for index in range(len(body) - AAR_QUOTE_SPAN_CHARS + 1)
    }
    for path in run.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in {".md", ".txt", ".json"}:
            continue
        try:
            path.resolve().relative_to((run / "aar").resolve())
        except ValueError:
            pass
        else:
            continue
        try:
            source = _normalized_span_text(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if any(
            source[index : index + AAR_QUOTE_SPAN_CHARS] in spans
            for index in range(len(source) - AAR_QUOTE_SPAN_CHARS + 1)
        ):
            return True
    return False


def aar_quotation_analysis(publications: tuple[Publication, ...]) -> Analysis:
    aar_publications = tuple(
        publication
        for publication in publications
        if _aar_run_directory(publication.path) is not None
    )
    findings = tuple(
        Finding(AAR_QUOTATION_RULE, 1, publication.field, "deny")
        for publication in aar_publications
        if _quotes_run_material(publication)
    )
    if aar_publications:
        report = (
            f"AAR quotation gate: {len(findings)} copied private-run span(s) "
            f"across {len(aar_publications)} AAR publication(s)"
        )
    else:
        report = (
            "AAR quotation gate: not applicable -- no publication under "
            "aar/publications/"
        )
    return Analysis(findings, report)


def analyze(
    publication: Publication,
    *,
    index: phi_scan.CorpusIndex,
    issue: TrackerRecord | dict | None,
    remote_fresh: bool,
    route: tuple[str, ...] = ("issue", "comment"),
    filed_from_route: tuple[str, ...] | None | object = _USE_ANALYSIS_ROUTE,
) -> Analysis:
    """Grade one title or body without returning its text or matched values."""
    publication = with_tracker_record(publication, route=route, context=issue)
    record = publication.record
    if record is None:  # NamedTuple narrowing for type checkers.
        raise ValueError("publication has no tracker record")
    phi_counts = Counter(
        finding.rule
        for finding in phi_scan.scan_lines(
            publication.text, publication.field, index, True
        )
    )
    findings = [
        Finding(f"phi:{rule}", count, publication.field, "advise")
        for rule, count in sorted(phi_counts.items())
    ]
    if publication.field == "body":
        body_findings = tracker_bodies.grade(
            [
                tracker_bodies.Record(
                    "pre-publication",
                    "body being published",
                    tracker_bodies.ISSUE,
                    publication.text,
                )
            ]
        )
        findings.extend(
            Finding(f"body:{row.kind}", 1, publication.field, "deny")
            for row in body_findings
        )
    else:
        if tracker_bodies.has_c0_control_character(publication.text):
            findings.append(Finding(
                "body:c0-control-character", 1, publication.field, "deny"
            ))
        if tracker_bodies.has_carriage_return_flanked(publication.text):
            findings.append(Finding(
                "body:carriage-return-flanked", 1, publication.field, "deny"
            ))
    findings.extend(
        Finding(row.rule, 1, publication.field, "deny")
        for row in tracker_coordinates.grade(
            publication.text, f"{publication.field} being published"
        )
    )
    if publication.field == "body":
        findings.extend(
            Finding(row.rule, 1, publication.field, "deny")
            for row in tracker_measurements.grade_current(
                publication.text, f"{publication.field} being published"
            )
        )
    comment_prose = (
        ordinary_paragraph_prose(publication.text)
        if publication.field == "body" and route in COMMENT_ROUTES
        else ""
    )
    if (
        publication.field == "body"
        and route in COMMENT_ROUTES
        and any(
            line.startswith("**Verdict:**")
            for line in comment_prose.splitlines()
        )
        and not DISCRIMINATOR_CLAUSE.search(comment_prose)
    ):
        findings.append(Finding(
            "verdict:missing-discriminator", 1, publication.field, "advise"
        ))
    retired_citations = retired_citation_paragraphs(publication.text)
    if retired_citations:
        findings.append(Finding(
            RETIRED_CITATION, retired_citations, publication.field, "advise"
        ))

    branch = tracker_branch_scope.grade_record(record, remote_fresh=remote_fresh)
    if publication.field == "title":
        context = (
            "title path triggers evaluated; record-label and completion triggers "
            "apply to bodies"
        )
    else:
        context = (
            "context-blind: record number and labels were not read; the in-flight "
            "trigger was not evaluated"
            if issue is None
            else f"record context: issue #{record.number} labels read"
        )

    positive_unverified = branch.status == 0 and branch.verdict.ancestry_verified is False

    if isinstance(issue, TrackerRecord):
        current_body = issue.body
    elif isinstance(issue, dict) and isinstance(issue.get("body"), str):
        current_body = issue["body"]
    else:
        current_body = None
    policy_route = route if filed_from_route is _USE_ANALYSIS_ROUTE else filed_from_route
    filed_from = tracker_filed_from.grade_publication(
        publication.text,
        policy_route if publication.field == "body" else None,
        current_body=current_body,
    )
    if filed_from.rule is not None:
        findings.append(Finding(
            filed_from.rule, 1, publication.field, filed_from.posture
        ))

    if branch.status == 1:
        rule = branch.verdict.rule
        if rule not in tracker_branch_scope.BRANCH_RULES:
            raise ValueError("branch grader returned an undeclared rule")
        remote_rule = rule in ("branch:unresolved-path", "branch:near-miss")
        posture = (
            "advise"
            if rule == "branch:near-miss" or (remote_rule and not remote_fresh)
            else "deny"
        )
        findings.append(Finding(rule, 1, publication.field, posture))

    lines = [context]
    if not branch.verdict.default_branch_tree_read:
        lines.append(branch.report)
    if not remote_fresh:
        lines.append(
            "origin/main fetch failed: unresolved-path and near-miss rules are advisory"
        )
    if positive_unverified:
        lines.append(
            "positive Branch state accepted without ancestry verification"
        )
    if publication.field == "body":
        lines.append(filed_from.report)
    for row in findings:
        line = (
            f"{row.posture}: {row.rule}: {row.count} finding(s) in {row.field}"
        )
        body_kind = row.rule.removeprefix("body:")
        if body_kind in BODY_REMEDIES:
            line += f"; remedy: {body_remedy(body_kind, route)}"
        if row.rule == tracker_coordinates.UNANCHORED:
            line += f"; remedy: {COORDINATE_REMEDY}"
        if row.rule == RETIRED_CITATION:
            line += f"; remedy: {RETIRED_CITATION_REMEDY}"
        if row.rule == tracker_measurements.INSIDE_QUOTE:
            line += "; remedy: add one blank line above the Measured at declaration"
        lines.append(line)
    if not findings:
        lines.append(f"scanned {publication.field}: 0 findings")
    return Analysis(tuple(findings), "\n".join(lines))


def authorize_issue_body(
    body: str,
    label: str,
    *,
    issue_number: int | None = None,
    issue: TrackerRecord | dict | None = None,
    title: str | None = None,
) -> str:
    """Grade a direct issue publication through the shared analyzer.

    Most tracker writes arrive as a shell command and enter through ``handle``.
    An in-process writer already holds the exact body, so making it reconstruct
    shell quoting would add a second, weaker extraction path. This entry point
    sends its exact fields through ``analyze`` and returns the resulting report
    without running the command route's citation readback.
    """
    if isinstance(issue, TrackerRecord):
        context_number = issue.number
    elif isinstance(issue, dict) and isinstance(issue.get("number"), int):
        context_number = issue["number"]
    else:
        context_number = None
    if (
        issue_number is not None
        and context_number is not None
        and issue_number != context_number
    ):
        raise ValueError(
            f"tracker body refused for {label}: issue number and context disagree"
        )
    publication_number = (
        issue_number if issue_number is not None else context_number
    )
    if publication_number is not None:
        # Lazy import avoids the module-level cycle: implementation_map uses
        # this direct-writer gate when it publishes the same body.
        from implementation_map import MAP_ISSUE, producer_stamp_problem

        if publication_number == MAP_ISSUE:
            problem = producer_stamp_problem(body)
            if problem is not None:
                raise ValueError(
                    f"tracker body refused for {label}: producer stamp: {problem}"
                )
    index, missing = current_index()
    remote_fresh = refresh_default_branch()
    route = (
        ("issue", "edit")
        if publication_number is not None
        else ("issue", "create")
    )
    publications = [Publication("body", body)]
    if title is not None:
        publications.append(Publication("title", title))
    analyses = [
        analyze(
            publication,
            index=index,
            issue=issue,
            remote_fresh=remote_fresh,
            route=route,
        )
        for publication in publications
    ]
    lines = []
    if missing:
        lines.append(
            "PHI corpus layer incomplete: " + ", ".join(missing) + " not available"
        )
    lines.extend(analysis.report for analysis in analyses)
    denied = tuple(
        finding.rule
        for analysis in analyses
        for finding in analysis.findings
        if finding.posture == "deny"
    )
    report = "\n".join(lines)
    if denied:
        rules = ", ".join(dict.fromkeys(denied))
        raise ValueError(f"tracker body refused for {label}: {rules}\n{report}")
    return report


def current_index() -> tuple[phi_scan.CorpusIndex, tuple[str, ...]]:
    names, dates = phi_scan.corpus_identifiers()
    return phi_scan.build_index(names, dates), tuple(phi_scan.missing_corpus_sources())


def refresh_default_branch(repo: Path | None = None) -> bool:
    """Refresh ``origin/main`` without relying on the clone's fetch mapping.

    The destination is explicit because ``_main_ancestry`` reads that ref. The
    leading ``+`` also follows a rewritten remote branch: without it, a stuck
    ref could verify a rewritten-away commit as on ``main``. The freshness gate
    omits ``+`` safely because its failed fetch reaches no ancestry verdict.
    """
    completed = subprocess.run(
        [
            "git",
            "fetch",
            "--no-tags",
            "origin",
            "+refs/heads/main:refs/remotes/origin/main",
        ],
        cwd=repo or Path(__file__).resolve().parent.parent,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.returncode == 0


REPOSITORY_OWNER = "mshamblin5150-code"
REPOSITORY_NAME = "clinical-skills"


def _readback_query(numbers: frozenset[int]) -> str:
    selections = "\n".join(
        f"""record_{number}: issueOrPullRequest(number: {number}) {{
      ... on Issue {{ number state labels(first: 100) {{ nodes {{ name }} }} updatedAt body url }}
      ... on PullRequest {{ number state labels(first: 100) {{ nodes {{ name }} }} updatedAt body url }}
    }}"""
        for number in sorted(numbers)
    )
    return f"""query($owner: String!, $name: String!) {{
  repository(owner: $owner, name: $name) {{
    {selections}
  }}
}}"""


def fetch_readback(
    numbers: frozenset[int],
) -> dict[int, dict | None]:
    """Fetch all current record fingerprints in one GraphQL request.

    ``gh api graphql`` can return status 1 while stdout still contains every
    resolved alias and ``null`` for an unresolved one.  The payload, not the
    process status, therefore decides whether the read succeeded.
    """
    declared_absences = tuple(
        DeclaredAbsence("NOT_FOUND", ("repository", f"record_{number}"))
        for number in sorted(numbers)
    )
    try:
        data = read_response(subprocess.run(
            [
                "gh",
                "api",
                "graphql",
                "-F",
                f"owner={REPOSITORY_OWNER}",
                "-F",
                f"name={REPOSITORY_NAME}",
                "-f",
                "query=" + _readback_query(numbers),
            ],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        ).stdout, declared_absences).data
    except GraphQLResponseError as error:
        raise ValueError(str(error)) from error
    repository = data.get("repository") if isinstance(data, dict) else None
    if not isinstance(repository, dict):
        raise ValueError("tracker readback payload had no repository data")
    records: dict[int, dict | None] = {}
    for number in numbers:
        alias = f"record_{number}"
        if alias not in repository:
            raise ValueError("tracker readback omitted requested record")
        record = repository[alias]
        if record is not None and not isinstance(record, dict):
            raise ValueError("tracker readback record had the wrong type")
        records[number] = record
    return records


def _issue_context(record: dict | None) -> TrackerRecord | None:
    return from_graphql(record)


BRANCH_SCOPE_REFUSAL = (
    "tracker branch-scope text must be corrected before publication"
)
UNSCANNED_REFUSAL = (
    "tracker text could not be read, so this publication was not scanned"
)


def _hook_response(
    decision: str | None,
    report: str,
    reason: str = BRANCH_SCOPE_REFUSAL,
) -> dict:
    specific = {
        "hookEventName": "PreToolUse",
        "additionalContext": report,
    }
    if decision is not None:
        specific["permissionDecision"] = decision
    if decision == "deny":
        specific["permissionDecisionReason"] = reason
    return {"hookSpecificOutput": specific}


def _missing_issue_create_analysis() -> Analysis:
    grade = tracker_filed_from.grade_publication("", ("issue", "create"))
    if grade.rule is None:
        raise ValueError("missing issue body returned no Filed-from finding")
    return Analysis(
        (Finding(grade.rule, 1, "body", grade.posture),),
        grade.report,
    )


UNREADABLE_REMEDIES = {
    "missing-file": (
        "no file was at this path when the hook ran, which is before any part "
        "of this command runs, and a refused command runs none of its stages; "
        "if this command writes the file, write it in a separate command "
        "first, otherwise create it, then save the exact publication command "
        "and run `python tools/tracker_publish_hook.py --command-file <path>` "
        "before retrying"
    ),
    "unrooted-path": (
        'put `cd "<folder>" && ` in front of the command, or write the whole '
        "path in quotes"
    ),
    "external-variable": (
        "resolve the variable in the publication command, save that command, "
        "and run `python tools/tracker_publish_hook.py --command-file <path>` "
        "before retrying"
    ),
    "pipe": (
        "save the piped text to a body file, update and save the publication "
        "command, and run `python tools/tracker_publish_hook.py --command-file "
        "<path>` before retrying"
    ),
    "command-substitution": (
        "run the substitution separately, save the resolved publication command, "
        "and run `python tools/tracker_publish_hook.py --command-file <path>` "
        "before retrying"
    ),
    "expansion-exposed-inline": (
        "single-quote every segment of the body value, escaping an apostrophe "
        "between segments, or write the body to a file and pass its absolute "
        "path to --body-file; the value must be requoted before its content can "
        "be graded"
    ),
    "invalid-input": (
        "repair the JSON input, save the exact publication command, and run "
        "`python tools/tracker_publish_hook.py --command-file <path>` before retrying"
    ),
    "invalid-command": (
        "repair and save the exact publication command, and run `python "
        "tools/tracker_publish_hook.py --command-file <path>` before retrying"
    ),
    "missing-value": (
        "supply the flag value, save the exact publication command, and run "
        "`python tools/tracker_publish_hook.py --command-file <path>` before retrying"
    ),
}
UNREADABLE_RULES = tuple(UNREADABLE_REMEDIES)
UNCLASSIFIED_API_REMEDIES = {
    "unclassified-api-mutation": (
        "a GraphQL mutation is an unclassified API call; publish through `gh issue` "
        "or `gh pr`, or use a named REST `/issues` or `/pulls` endpoint"
    ),
    "unclassified-api-endpoint": (
        "this unclassified API call names neither the route table nor the "
        "non-publication list; add the endpoint to the correct classification "
        "before retrying"
    ),
    "unclassified-api-identifier": (
        "the record identifier cannot be reconstructed; type the literal "
        "identifier in the endpoint before retrying"
    ),
    "unclassified-api-arguments": (
        "an unquoted runtime expansion can change the API argument list; "
        "type the endpoint and options explicitly before retrying"
    ),
}
UNCLASSIFIED_API_RULES = tuple(UNCLASSIFIED_API_REMEDIES)


def unreadable_remedy(row: Unreadable) -> str:
    if row.kind == "expansion-exposed-inline" and row.field == "title":
        return (
            "single-quote every segment of the title value, escaping an "
            "apostrophe between segments; the value must be requoted before "
            "its content can be graded"
        )
    return UNREADABLE_REMEDIES[row.kind]


def _unreadable_report(extracted: Extraction) -> str:
    lines = []
    for row in extracted.unreadable:
        reconstructed = row.reconstructed_path or row.source
        if row.resolved_against is not None:
            resolved_against = row.resolved_against
        elif shell_reader.is_absolute_path(reconstructed):
            resolved_against = "none (path was absolute)"
        else:
            resolved_against = "none readable"
        lines.extend(
            (
                f"tracker pre-publish: NOT SCANNED -- unreadable {row.field} "
                f"({row.kind}); {unreadable_remedy(row)}",
                "tracker pre-publish: resolved against: "
                + resolved_against
                + f"; reconstructed path: {reconstructed}",
            )
        )
    return "\n".join(lines)


def _unclassified_api_report(extracted: Extraction) -> str:
    return "\n".join(
        "tracker pre-publish: NOT SCANNED -- unclassified API call "
        f"({row.kind}); {UNCLASSIFIED_API_REMEDIES[row.kind]}"
        for row in extracted.unclassified_api_calls
    )


def grade_command(command: str) -> CommandGrade | None:
    """Grade one Bash publication command without writing the hook marker."""
    if command_reader._unreproduced_publish_route(command) is not None:
        return CommandGrade(
            False,
            True,
            "tracker pre-publish: NOT SCANNED -- unreproduced publication; "
            "publish one top-level `gh` command per Bash call, and if a script "
            "merely mentions a publication, run that script from a file",
        )
    extracted = extract(command)
    if extracted.route is None:
        return None
    if extracted.unclassified_api_calls:
        return CommandGrade(False, True, _unclassified_api_report(extracted))
    if extracted.unreadable:
        return CommandGrade(False, True, _unreadable_report(extracted))

    quotation = aar_quotation_analysis(extracted.publications)
    if not extracted.publications:
        if (extracted.grade_route or extracted.route) == ("issue", "create"):
            analysis = _missing_issue_create_analysis()
            return CommandGrade(True, True, analysis.report)
        return CommandGrade(
            False,
            False,
            "tracker pre-publish: NOT SCANNED -- no publication fields "
            "recognized in the command",
        )

    index, missing = current_index()
    remote_fresh = refresh_default_branch()
    # ``tracker_scan`` splits title and body so a finding identifies the field
    # to edit. A readback identifies records, not fields, so that reason does
    # not transfer and both fields deliberately form one set.
    publication_text = "\n".join(row.text for row in extracted.publications)
    citations = tracker_readback.citation_numbers(
        publication_text,
        publication_number=extracted.number,
    )
    issue = None
    readback_lines: tuple[str, ...]
    if citations:
        try:
            records = fetch_readback(citations)
            readback_lines = tracker_readback.fingerprint_lines(records)
            if extracted.number is not None:
                issue = _issue_context(records.get(extracted.number))
        except (
            OSError,
            UnicodeError,
            subprocess.SubprocessError,
            json.JSONDecodeError,
            ValueError,
        ):
            readback_lines = (
                "tracker readback: FETCH FAILED; context-blind -- current "
                "record state and labels were not read",
            )
    else:
        readback_lines = (tracker_readback.empty_citation_line(),)

    route = extracted.grade_route or extracted.route
    bound_publications = [
        with_tracker_record(publication, route=route, context=issue)
        for publication in extracted.publications
    ]
    analyses = [
        analyze(
            publication,
            index=index,
            issue=issue,
            remote_fresh=remote_fresh,
            route=route,
        )
        for publication in bound_publications
    ]
    if route == ("issue", "create") and not any(
        row.field == "body" for row in bound_publications
    ):
        analyses.append(_missing_issue_create_analysis())
    analyses.append(quotation)

    lines = [
        f"tracker pre-publish: {publication.field} read from {publication.origin}"
        for publication in extracted.publications
    ]
    if missing:
        lines.append(
            "PHI corpus layer incomplete: " + ", ".join(missing) + " not available"
        )
    lines.extend(readback_lines)
    lines.extend(analysis.report for analysis in analyses)
    denied = any(
        finding.posture == "deny"
        for analysis in analyses
        for finding in analysis.findings
    )
    return CommandGrade(True, denied, "\n".join(lines))


def _handle(payload: dict) -> dict:
    """Analyze one payload after the entry point has recorded its run."""
    try:
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            raise ValueError("tool_input is not an object")
        command = tool_input.get("command")
        if command is None:
            return {}
        if not isinstance(command, str):
            raise ValueError("tool_input.command is not text")
        tool_name = payload.get("tool_name")
        if not isinstance(tool_name, str):
            raise ValueError("tool_name is not text")
        if COMMAND_TOOLS.get(tool_name) != MODELED_SHELL:
            route = command_reader._loose_publish_route(command)
            if route is None:
                return {}
            return _hook_response(
                "deny",
                "tracker pre-publish: NOT SCANNED -- "
                f"{tool_name} carries an unmodeled shell; save the tracker text "
                "to a file and publish it through Bash so the text can be graded",
                UNSCANNED_REFUSAL,
            )
        grade = grade_command(command)
        if grade is None:
            return {}
        if not grade.scanned and not grade.denied:
            return {}
        return _hook_response(
            "deny" if grade.denied else None,
            grade.report,
            UNSCANNED_REFUSAL if not grade.scanned else BRANCH_SCOPE_REFUSAL,
        )
    except Exception as exc:
        return _hook_response(
            "deny",
            "tracker pre-publish HOOK FAILURE: "
            f"analysis failed ({type(exc).__name__})",
        )


def handle(payload: dict) -> dict:
    """Record and return one hook response without echoing tracker text."""
    record_run()
    return _handle(payload)


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) == 2 and arguments[0] == "--command-file":
        try:
            command = Path(arguments[1]).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(
                "tracker pre-publish: NOT SCANNED -- unreadable command file "
                f"({type(exc).__name__})",
                file=sys.stderr,
            )
            return 2
        try:
            grade = grade_command(command)
        except Exception as exc:
            print(
                "tracker pre-publish: NOT SCANNED -- "
                f"analysis failed ({type(exc).__name__})",
                file=sys.stderr,
            )
            return 2
        if grade is None:
            print(
                "tracker pre-publish: NOT SCANNED -- no publication route "
                "recognized in the command file"
            )
            return 2
        print(grade.report)
        if not grade.scanned:
            return 2
        return 1 if grade.denied else 0
    record_run()
    if arguments:
        print("tracker pre-publish: unsupported arguments", file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin)
    except (UnicodeError, json.JSONDecodeError) as exc:
        response = _hook_response(
            None,
            "tracker pre-publish HOOK FAILURE: "
            f"Unreadable body ({type(exc).__name__})",
        )
    else:
        response = _handle(payload)
    print(json.dumps(response, sort_keys=True))
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
