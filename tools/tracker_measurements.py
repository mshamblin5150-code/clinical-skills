#!/usr/bin/env python3
"""Grade the declared base of publication-time measurements.

The public ``grade`` seam reads one supplied record and compares an opted-in
declaration with the caller's publication base. A clean result establishes
only the bounded properties in ``tracker_measurements.DECLARED_LIMITS``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple
import re
import subprocess
import sys

from console_codec import require_python_floor, use_utf8
from git_paths import GitPathError, read_path_records
import tracker_bodies


STALE_BASE = "measurement:stale-base"
INVALID_DECLARATION = "measurement:invalid-declaration"
CURRENT_BASE_UNREADABLE = "measurement:current-base-unreadable"
CLEAN = 0
FOUND = 1
NOT_SCANNED = 2
LABEL = "**Measured at:**"
REPO_ROOT = Path(__file__).resolve().parent.parent
CUTOFF = datetime(2026, 9, 12, 15, 5, 41, tzinfo=timezone.utc)

DECLARED_LIMITS = (
    "Whether a load-bearing figure names its measured population and matcher is a reader-owned rule and is not graded.",
    "The gate cannot distinguish a fresh re-derivation from an author who writes the current SHA without re-deriving.",
    "The declaration is opt-in; a record with no own-line Measured at label is not graded.",
    "The staged-ADR reader compares with branch HEAD and therefore fires on branch drift.",
    "Docstrings and CLAUDE.md prose are outside the tracker-record and staged-ADR readers.",
)

FULL_SHA = re.compile(rf"^{re.escape(LABEL)} ([0-9a-fA-F]{{40}})$")


class Finding(NamedTuple):
    rule: str
    locator: str
    declared: str
    expected: str


class AdrScan(NamedTuple):
    records: int
    declarations: int
    findings: tuple[Finding, ...]


class CommittedAdrScan(NamedTuple):
    records: int
    eligible: int
    declarations: int
    findings: tuple[Finding, ...]


class Scan(NamedTuple):
    records: int
    declarations: int
    findings: tuple[Finding, ...]


class SourceError(Exception):
    """The current publication base could not be read."""


def current_head(root: Path = REPO_ROOT) -> str:
    """Return the full commit naming the current publication base."""

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
    except OSError as error:
        raise SourceError(CURRENT_BASE_UNREADABLE) from error
    sha = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[0-9a-fA-F]{40}", sha) is None:
        raise SourceError(CURRENT_BASE_UNREADABLE)
    return sha.lower()


def grade(text: str, locator: str, expected_sha: str) -> tuple[Finding, ...]:
    """Compare one record's own-line declaration with ``expected_sha``."""

    declaration_lines = tuple(
        line for line in text.splitlines() if line.startswith(LABEL)
    )
    if not declaration_lines:
        return ()
    matches = tuple(FULL_SHA.fullmatch(line) for line in declaration_lines)
    if len(matches) != 1 or matches[0] is None:
        return (
            Finding(
                INVALID_DECLARATION,
                locator,
                declaration_lines[0],
                expected_sha.lower(),
            ),
        )
    declared = matches[0].group(1).lower()
    expected = expected_sha.lower()
    if declared == expected:
        return ()
    return (Finding(STALE_BASE, locator, declared, expected),)


def grade_current(text: str, locator: str) -> tuple[Finding, ...]:
    """Grade an opted-in record against the current checkout commit."""

    if not any(line.startswith(LABEL) for line in text.splitlines()):
        return ()
    try:
        expected = current_head()
    except SourceError:
        return (Finding(CURRENT_BASE_UNREADABLE, locator, "", ""),)
    return grade(text, locator, expected)


def _staged_text(root: Path, relative: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "show", f":{relative}"],
            cwd=root,
            capture_output=True,
        )
    except OSError as error:
        raise SourceError(f"staged ADR unreadable: {relative}") from error
    if completed.returncode != 0:
        raise SourceError(f"staged ADR unreadable: {relative}")
    return completed.stdout.decode("utf-8", errors="replace")


def grade_staged_adrs(root: Path = REPO_ROOT) -> AdrScan:
    """Grade each added, copied, modified, or renamed ADR in Git's index.

    A clean result means no staged tracked ADR fails. An unstaged or untracked
    ADR remains invisible to this index walk.
    """

    try:
        relatives = tuple(
            sorted(
                read_path_records(
                    root,
                    "diff",
                    "--cached",
                    "--name-only",
                    "--no-renames",
                    "--diff-filter=ACMR",
                    "-z",
                    "--",
                    "docs/adr/*.md",
                )
            )
        )
    except GitPathError as error:
        raise SourceError("staged ADR population unreadable") from error
    expected = current_head(root) if relatives else ""
    declarations = 0
    findings: list[Finding] = []
    for relative in relatives:
        body = _staged_text(root, relative)
        if any(line.startswith(LABEL) for line in body.splitlines()):
            declarations += 1
        findings.extend(grade(body, relative, expected))
    return AdrScan(len(relatives), declarations, tuple(findings))


def _last_touch(root: Path, relative: str) -> tuple[str, datetime, str]:
    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%H%x00%cI%x00%P", "--", relative],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
    except OSError as error:
        raise SourceError(f"ADR last touch unreadable: {relative}") from error
    fields = completed.stdout.strip().split("\0")
    if completed.returncode != 0 or len(fields) != 3 or not fields[0] or not fields[1]:
        raise SourceError(f"ADR last touch unreadable: {relative}")
    try:
        stamp = datetime.fromisoformat(
            fields[1][:-1] + "+00:00" if fields[1].endswith("Z") else fields[1]
        )
    except ValueError as error:
        raise SourceError(f"ADR last touch unreadable: {relative}") from error
    parents = fields[2].split()
    parent = parents[0] if parents else ""
    return fields[0], stamp, parent


def _committed_text(root: Path, commit: str, relative: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "show", f"{commit}:{relative}"], cwd=root, capture_output=True
        )
    except OSError as error:
        raise SourceError(f"ADR body unreadable: {relative}") from error
    if completed.returncode != 0:
        raise SourceError(f"ADR body unreadable: {relative}")
    return completed.stdout.decode("utf-8", errors="replace")


def grade_adrs(root: Path = REPO_ROOT) -> CommittedAdrScan:
    """Audit committed ADR declarations forward from ``CUTOFF``.

    A clean result means no eligible tracked ADR fails. An untracked ADR is
    invisible until it enters Git's index.
    """

    try:
        relatives = tuple(
            sorted(
                read_path_records(
                    root, "ls-files", "--cached", "-z", "--", "docs/adr/*.md"
                )
            )
        )
    except GitPathError as error:
        raise SourceError("tracked ADR population unreadable") from error
    if not relatives:
        raise SourceError("tracked ADR population unreadable")
    eligible = 0
    declarations = 0
    findings: list[Finding] = []
    for relative in relatives:
        commit, stamp, parent = _last_touch(root, relative)
        if stamp < CUTOFF:
            continue
        eligible += 1
        body = _committed_text(root, commit, relative)
        if not any(line.startswith(LABEL) for line in body.splitlines()):
            continue
        declarations += 1
        if not parent:
            findings.append(Finding(CURRENT_BASE_UNREADABLE, relative, "", ""))
            continue
        findings.extend(grade(body, relative, parent))
    return CommittedAdrScan(len(relatives), eligible, declarations, tuple(findings))


def survey(
    records: tuple[tracker_bodies.Record, ...], expected_sha: str
) -> Scan:
    """Grade one completely loaded tracker-event population."""

    if any(record.body is None for record in records):
        raise SourceError("tracker event body unreadable")
    declarations = 0
    findings: list[Finding] = []
    for record in records:
        if any(line.startswith(LABEL) for line in record.body.splitlines()):
            declarations += 1
        findings.extend(grade(record.body, record.label, expected_sha))
    return Scan(len(records), declarations, tuple(findings))


def format_report(
    findings: tuple[Finding, ...],
    source: str,
    records: int,
    declarations: int,
    *,
    eligible: int | None = None,
) -> str:
    lines = [
        f"publication measurements over {source}",
        "",
        f"  records read {records}",
    ]
    if eligible is not None:
        lines.append(f"  records at or after cutoff {eligible}")
    lines.extend(
        (
            f"  declarations read {declarations}",
            f"  findings {len(findings)}",
        )
    )
    if findings:
        lines.extend(("", "  each finding:"))
        lines.extend(f"    {row.rule} {row.locator}" for row in findings)
    return "\n".join(lines)


USAGE = (
    "usage: tracker_measurements.py [--staged-adrs | "
    "--github-event <event.json> --event-name <name>]"
)


def main(argv: list[str], *, root: Path = REPO_ROOT) -> int:
    try:
        if not argv:
            scan = grade_adrs(root)
            report = format_report(
                scan.findings,
                "forward-only committed ADRs",
                scan.records,
                scan.declarations,
                eligible=scan.eligible,
            )
        elif argv == ["--staged-adrs"]:
            scan = grade_staged_adrs(root)
            report = format_report(
                scan.findings,
                "staged ADRs",
                scan.records,
                scan.declarations,
            )
        elif (
            len(argv) == 4
            and argv.count("--github-event") == 1
            and argv.count("--event-name") == 1
        ):
            event_path = Path(argv[argv.index("--github-event") + 1])
            event_name = argv[argv.index("--event-name") + 1]
            if not event_path.is_file():
                raise SourceError(f"GitHub event file unreadable: {event_path.name}")
            try:
                records = tracker_bodies.load_github_event(event_path, event_name)
            except tracker_bodies.HarvestError as error:
                raise SourceError(f"GitHub event shape unreadable: {error}") from error
            if not records:
                raise SourceError(f"GitHub event shape unreadable: {event_path.name}")
            scan = survey(records, current_head(root))
            report = format_report(
                scan.findings,
                f"{event_name} event {event_path.name}",
                scan.records,
                scan.declarations,
            )
        else:
            raise SourceError(USAGE)
    except SourceError as error:
        print(str(error), file=sys.stderr)
        return NOT_SCANNED
    print(report)
    return FOUND if scan.findings else CLEAN


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
