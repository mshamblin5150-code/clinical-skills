#!/usr/bin/env python3
"""Grade the declared base of publication-time measurements.

The public ``grade`` seam reads one supplied record and compares an opted-in
declaration with the caller's publication base. A clean result establishes
only the bounded properties in ``tracker_measurements.DECLARED_LIMITS``. A
title is not a declaration surface, so both publication hosts keep this grade
body-only.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import NamedTuple
import re
import subprocess
import sys

from console_codec import require_python_floor, use_utf8
from git_paths import GitPathError, read_path_records
import tracker_bodies
import tracker_branch_scope


STALE_BASE = "measurement:stale-base"
INVALID_DECLARATION = "measurement:invalid-declaration"
INSIDE_QUOTE = "measurement:inside-quote"
CURRENT_BASE_UNREADABLE = "measurement:current-base-unreadable"
RULES = (
    STALE_BASE,
    INVALID_DECLARATION,
    INSIDE_QUOTE,
    CURRENT_BASE_UNREADABLE,
)
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
    "The staged-ADR reader accepts pre-commit HEAD or its first parent because no hook signal distinguishes an amend; it still fires on branch drift and leaves which value is correct to the post-commit and committed-ADR audits.",
    "The post-commit mode reads only ADRs the named commit touched; whether the hook runs during a rebase is not established.",
    "Local hooks and PR-time checks cannot detect a later server-side squash or rebase merge that discards the declared base; the committed-ADR audit reports that drift after integration.",
    "Docstrings and CLAUDE.md prose are outside the tracker-record and staged-ADR readers.",
    "The ADR annotation-only exception proves preservation and supersession binding, not the semantic truth of an annotation's account.",
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

    lines = text.splitlines()
    declarations = tuple(
        (index, line)
        for index, line in enumerate(lines)
        if line.startswith(LABEL)
    )
    if not declarations:
        return ()
    declaration_lines = tuple(line for _, line in declarations)
    findings = [
        Finding(INSIDE_QUOTE, locator, "", expected_sha.lower())
        for index, _ in declarations
        if tracker_branch_scope.directly_follows_quote_line(lines, index)
    ]
    matches = tuple(FULL_SHA.fullmatch(line) for line in declaration_lines)
    if len(matches) != 1 or matches[0] is None:
        findings.append(
            Finding(
                INVALID_DECLARATION,
                locator,
                declaration_lines[0],
                expected_sha.lower(),
            )
        )
        return tuple(findings)
    declared = matches[0].group(1).lower()
    expected = expected_sha.lower()
    if declared == expected:
        return tuple(findings)
    findings.append(Finding(STALE_BASE, locator, declared, expected))
    return tuple(findings)


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


def _adr_snapshot(root: Path, revision: str) -> dict[str, str]:
    """Read tracked numbered ADR files in the selected index or Git revision.

    A successful read covers that tracked population; untracked files remain
    invisible. Index mode reads staged blobs and excludes unstaged worktree
    edits. Read errors provide no proof of an annotation-only change.
    """
    names = (read_path_records(root, "ls-files", "--cached", "-z", "--", "docs/adr/*.md")
             if revision == ":" else
             read_path_records(root, "ls-tree", "-r", "--name-only", "-z", revision, "--", "docs/adr"))
    names = tuple(name for name in names if re.fullmatch(r"docs/adr/\d{4}-[^/\r\n]+\.md", name))
    queries = "".join((":" if revision == ":" else revision + ":") + name + "\n" for name in names)
    result = subprocess.run(["git", "cat-file", "--batch"], cwd=root,
                            input=queries.encode("utf-8"), capture_output=True, check=False)
    if result.returncode:
        raise SourceError("annotation population unreadable")
    offset = 0
    records = {}
    for name in names:
        end = result.stdout.find(b"\n", offset)
        header = result.stdout[offset:end].split()
        if end < 0 or len(header) != 3 or header[1] != b"blob":
            raise SourceError("annotation population unreadable")
        size = int(header[2])
        offset = end + 1
        raw = result.stdout[offset:offset + size]
        if len(raw) != size or result.stdout[offset + size:offset + size + 1] != b"\n":
            raise SourceError("annotation population unreadable")
        records[Path(name).name] = raw.decode("utf-8")
        offset += size + 1
    return records


def _annotation_report(root: Path, revision: str) -> dict:
    relative = "docs/adr/supersession-classification-1518.json"
    body = _staged_text(root, relative) if revision == ":" else _committed_text(root, revision, relative)
    report = json.loads(body)
    if not isinstance(report, dict):
        raise ValueError("annotation proof is not an object")
    return report


def _preserves_annotated_record(before: str, after: str) -> bool:
    """Remove only read annotations and literal retained legacy paragraphs.

    Original declarations and every retained nonblank line must agree exactly;
    paragraph separators may move outside code as annotations are placed. Legacy
    paragraphs may relocate only when their whole original body survives.
    """
    from adr_supersession_population import normalize_legacy_opening
    from markdown_read import CODE_FENCE, paragraphs
    from prose_bind import _is_closing_fence, _opening_fence, prose_outside_code
    from test_adr_supersession import OPENING

    before = before.replace("\r\n", "\n")
    after = after.replace("\r\n", "\n")
    if "\ufffd" in before or "\ufffd" in after:
        return False
    declarations = lambda text: tuple(line for line in text.splitlines() if line.startswith(LABEL))
    if declarations(before) != declarations(after):
        return False
    visible_lines = prose_outside_code(after).splitlines()
    original_lines = prose_outside_code(before).splitlines()
    original_visible = {block for line, block in paragraphs(before)
                        if original_lines[line - 1].strip()}
    markers = [block for line, block in paragraphs(after)
               if visible_lines[line - 1].startswith("*Superseded")
               and not any(CODE_FENCE.match(row) or row.lstrip().startswith("|") for row in block.splitlines())
               and OPENING.match(" ".join(block.splitlines()))]
    if not markers and "\n## Supersedes\n" not in after:
        return False
    def remove_visible_block(text, wanted):
        lines = text.splitlines(keepends=True)
        visible = prose_outside_code(text).splitlines()
        for line, block in paragraphs(text):
            if block == wanted and visible[line - 1].strip():
                start = sum(len(row) for row in lines[:line - 1])
                return text[:start] + text[start + len(block):]
        return text
    clean_before, clean_after = before, after
    for marker in markers:
        if marker not in before:
            normalized = " ".join(marker.split())
            quotes = re.findall(r'"([^"\n]+)"', normalized)
            if quotes and any(" ".join(quote.split()) not in " ".join(before.split()) for quote in quotes):
                return False
        if marker in clean_before:
            clean_before = remove_visible_block(clean_before, marker)
        clean_after = remove_visible_block(clean_after, marker)
    # Supersedes is a closed list checked against real markers separately.
    section = re.compile(r"(?m)^## Supersedes[ \t]*\n.*?(?=^## |\Z)", re.S)
    def section_match(text):
        match = section.search(prose_outside_code(text))
        if match and any(CODE_FENCE.match(line) or line.lstrip().startswith("|")
                         for line in text[match.start():match.end()].splitlines()):
            raise ValueError("fenced or tabular material is not a Supersedes annotation")
        return match
    old_section = section_match(before)
    new_section = section_match(after)
    if old_section:
        if not new_section:
            return False
        old_entries = re.split(r"\n(?=- )", before[old_section.start():old_section.end()].split("\n", 1)[1].strip("\n"))
        new_entries = {tuple(line for line in entry.splitlines() if line.strip())
                       for entry in re.split(r"\n(?=- )", after[new_section.start():new_section.end()].split("\n", 1)[1].strip("\n"))}
        if any(tuple(line for line in entry.splitlines() if line.strip()) not in new_entries
               for entry in old_entries if entry.strip()):
            return False
    old_clean_section = section_match(clean_before)
    new_clean_section = section_match(clean_after)
    if old_clean_section:
        clean_before = clean_before[:old_clean_section.start()] + clean_before[old_clean_section.end():]
    if new_clean_section:
        clean_after = clean_after[:new_clean_section.start()] + clean_after[new_clean_section.end():]
    for _line, original in paragraphs(clean_before):
        if original not in original_visible:
            continue
        normalized = normalize_legacy_opening(original, before)
        old_opening = re.match(r"^\*(?:Superseded|Corrected)[^*\n]*\.\*\s*", original)
        legacy = normalized is not None or re.match(r"^\*Corrected \d{4}-\d{2}-\d{2}\.\*\s+", original) is not None or original.startswith((
            "Superseded by", "**Superseded", "**Point 3 is narrowed", "> **Reconciled",
            "> **Ruling 5's rationale", "Correction, ",
        ))
        if not legacy:
            continue
        retained = original[old_opening.end():] if old_opening else original
        original_date = re.search(r"\b\d{4}-\d{2}-\d{2}\b", old_opening.group() if old_opening else "")
        if any(original in marker or (normalized and normalized in marker)
               or (retained and retained in marker and original_date
                   and marker.startswith(f"*Superseded {original_date.group()}.*"))
               for marker in markers):
            clean_before = remove_visible_block(clean_before, original)
    def retained_lines(text):
        # Use the existing Markdown reader's fence attribution; no second fence
        # grammar. Blank lines inside code are literal evidence too. Inline
        # literals and tables retain their entire line, including every space.
        result = []
        fence = None
        for line in text.splitlines():
            if fence is not None:
                result.append(line)
                if _is_closing_fence(line, fence):
                    fence = None
            else:
                opening = _opening_fence(line)
                if opening is not None:
                    fence = opening
                    result.append(line)
                elif line.strip():
                    result.append(line)
        return tuple(result)
    return retained_lines(clean_before) == retained_lines(clean_after)


def _annotation_only_proof(root: Path, relative: str, base: str, revision: str,
                           body: str) -> bool:
    """Exempt existing ADR annotations only after independent Git preservation proof."""
    try:
        if not re.fullmatch(r"docs/adr/\d{4}-[^/]+\.md", relative):
            return False
        before = _committed_text(root, base, relative)  # absent/new ADR fails closed
        if not _preserves_annotated_record(before, body):
            return False
        from test_adr_supersession import supersession_findings
        records = _adr_snapshot(root, revision)
        if records.get(Path(relative).name) != body:
            return False
        report = _annotation_report(root, revision)
        return not supersession_findings(records, report, root=root)
    except (OSError, SourceError, GitPathError, ValueError, KeyError, TypeError):
        return False


def _grade_adr(root: Path, relative: str, body: str, base: str, revision: str,
               alternate_base: str = "") -> tuple[Finding, ...]:
    bases = (base, alternate_base) if alternate_base else (base,)
    grades = tuple(grade(body, relative, candidate) for candidate in bases)
    if any(not findings for findings in grades):
        return ()
    findings = grades[0]
    if (findings and all(finding.rule == STALE_BASE for finding in findings)
            and any(_annotation_only_proof(root, relative, candidate, revision, body)
                    for candidate in bases)):
        return ()
    if alternate_base:
        return tuple(finding._replace(expected=" or ".join(bases)) for finding in findings)
    return findings


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
    expected, parent = "", ""
    if relatives:
        expected, _stamp, parent = _commit_info(root, "HEAD")
    declarations = 0
    findings: list[Finding] = []
    for relative in relatives:
        body = _staged_text(root, relative)
        if any(line.startswith(LABEL) for line in body.splitlines()):
            declarations += 1
        findings.extend(_grade_adr(root, relative, body, expected, ":", parent))
    return AdrScan(len(relatives), declarations, tuple(findings))


def _commit_info(root: Path, revision: str) -> tuple[str, datetime, str]:
    try:
        completed = subprocess.run(
            ["git", "show", "--no-patch", "--format=%H%x00%cI%x00%P",
             "--end-of-options", revision, "--"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError as error:
        raise SourceError(f"ADR commit unreadable: {revision}") from error
    fields = completed.stdout.strip().split("\0")
    if (completed.returncode or len(fields) != 3
            or re.fullmatch(r"[0-9a-fA-F]{40}", fields[0]) is None):
        raise SourceError(f"ADR commit unreadable: {revision}")
    try:
        stamp = datetime.fromisoformat(fields[1].replace("Z", "+00:00"))
    except ValueError as error:
        raise SourceError(f"ADR commit unreadable: {revision}") from error
    parents = fields[2].split()
    return fields[0], stamp, parents[0] if parents else ""


def grade_commit(revision: str, root: Path = REPO_ROOT) -> CommittedAdrScan:
    """Audit only surviving ADRs touched by one commit, against its first parent."""
    commit, stamp, parent = _commit_info(root, revision)
    try:
        relatives = tuple(sorted(read_path_records(
            root, "diff-tree", "--root", "--no-commit-id", "-r", "--name-only",
            "--no-renames", "--diff-filter=ACM", "-z",
            *((parent, commit) if parent else (commit,)), "--", "docs/adr/*.md",
        )))
    except GitPathError as error:
        raise SourceError("commit ADR population unreadable") from error
    declarations = 0
    findings: list[Finding] = []
    eligible = len(relatives) if stamp >= CUTOFF else 0
    for relative in relatives if eligible else ():
        body = _committed_text(root, commit, relative)
        if not any(line.startswith(LABEL) for line in body.splitlines()):
            continue
        declarations += 1
        if not parent:
            findings.append(Finding(CURRENT_BASE_UNREADABLE, relative, "", ""))
        else:
            findings.extend(_grade_adr(root, relative, body, parent, commit))
    return CommittedAdrScan(len(relatives), eligible, declarations, tuple(findings))


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
            ["git", "show", "--end-of-options", f"{commit}:{relative}", "--"],
            cwd=root, capture_output=True
        )
    except OSError as error:
        detail = " ".join(str(error).split())[:1000]
        raise SourceError(
            f"ADR body unreadable: {relative}; commit={commit}; "
            f"git show could not start ({type(error).__name__}): {detail}"
        ) from error
    if completed.returncode != 0:
        detail = " ".join(completed.stderr.decode("utf-8", errors="replace").split())[:1000]
        raise SourceError(
            f"ADR body unreadable: {relative}; commit={commit}; "
            f"git show exit={completed.returncode}; stderr={detail or '(empty)'}"
        )
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
        findings.extend(_grade_adr(root, relative, body, parent, commit))
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
        lines.extend(
            f"    {row.rule} {row.locator}"
            + (f" expected {row.expected}" if row.rule == STALE_BASE else "")
            for row in findings
        )
    return "\n".join(lines)


USAGE = (
    "usage: tracker_measurements.py [--staged-adrs | --commit <revision> | "
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
        elif len(argv) == 2 and argv[0] == "--commit":
            scan = grade_commit(argv[1], root)
            report = format_report(
                scan.findings, f"ADRs touched by commit {argv[1]}",
                scan.records, scan.declarations, eligible=scan.eligible,
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
            records = tuple(
                record
                for record in records
                if record.surface != tracker_bodies.TITLE
            )
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
