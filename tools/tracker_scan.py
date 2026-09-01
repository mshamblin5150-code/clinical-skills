"""Scan what a public flip publishes that a file scanner does not read.

[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212). Making
this repository public publishes more than its tracked tree. ``phi_scan --all``
walks ``git ls-files``, which is the tip and nothing else; #212's ruling comment
is blocked on **issue and pull-request text**, **pull-request diffs**, and
**commit messages**, and
[#104](https://github.com/mshamblin5150-code/clinical-skills/issues/104) records
the last of those as scanned by nothing.

**The inputs do not map one-to-one to #212's surfaces:**

- ``--harvest`` reads GitHub's own JSON for issues, pull requests and comments.
- ``--github-event`` reads the one record a GitHub tracker event changed.
  **This tool opens no socket**, which is `research_ledger.py`'s ruling adopted
  whole -- the fetch is a documented ``gh`` command whose output is a file, so
  the scanner stays offline, testable and stdlib-only.
- ``--commits`` reads every commit message reachable from a ref.
- ``--history`` reads every **blob** reachable from a ref. That is the
  pull-request limb: a merged pull request's diff is made of blobs, and every
  one of them is reachable once the merge lands. It is also the limb `phi_scan`
  cannot reach, because a file deleted or rewritten five commits ago is not in
  ``git ls-files``.
- ``--paths`` reads every path ever committed. **#212 never asks for this** --
  it is here because a filename is published too and costs one ``rev-list`` to
  read.

Harvest first, then scan::

    : "${TICKET_NUMBER:?set TICKET_NUMBER to the current ticket number}"
    H=$(python tools/scratch_work.py ticket "$TICKET_NUMBER")
    mkdir -p "$H"
    gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" \\
        > "$H/tracker-issues.json"
    gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" \\
        > "$H/tracker-comments.json"
    gh api --paginate "repos/OWNER/REPO/pulls/comments?per_page=100" \\
        > "$H/tracker-reviews.json"
    python tools/tracker_scan.py --harvest "$H/tracker-issues.json" \
        "$H/tracker-comments.json" "$H/tracker-reviews.json"

    git config --add remote.origin.fetch \
        "+refs/pull/*/head:refs/remotes/origin/pr/*"
    git fetch origin
    python tools/tracker_scan.py --commits --history --paths

**Into ``scratch/`` and not into the checkout, and the reason is that the
harvest is the thing being scanned.** It is the tracker's entire text, so a
finding is *in the file you just wrote*. ``scratch/`` is the PHI firewall's own
directory: gitignored, and `phi_scan`'s path layer refuses to commit from it
even under ``git add -f``. Writing it anywhere else in the tree puts a file full
of tracker prose one ``git add -A`` from being tracked, with no net under it --
[#176](https://github.com/mshamblin5150-code/clinical-skills/issues/176) and
[#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223)'s
subject, arriving on a file this tool tells you to create.

**Reachability is the boundary of publication, and it cuts both ways.** #212's
own scan walked ``git cat-file --batch-all-objects``, which is every object in
the local database including ones no ref reaches -- an amended commit, an
abandoned index write. Those were never pushed, so a finding in one is not an
exposure, and here the unreachable set carries findings the reachable set does
not. **And the same walk under-reads**: a pull request whose branch was deleted
after merging keeps its head at ``refs/pull/N/head`` on GitHub, which an
ordinary clone does not fetch. So a default clone is wrong in both directions at
once, and both directions are silent.

``--history`` prints the reachable and unreachable blob counts side by side, so
the figure behind that paragraph is re-derived rather than quoted. And
``--commits`` and ``--history`` **refuse until the pull-head refspec is in the
remote's persistent configuration and at least one pull-head ref is present**,
printing the setup commands -- `phi_scan.py`'s absent-corpus arrangement, for
its reason: a scan of half the published objects is not a clean scan, and
nothing in a zero says which it was. A one-off fetch is insufficient: its refs
can be pruned and cannot be refreshed by an ordinary fetch. ``--no-pull-refs``
is the acknowledgment for a repository that genuinely has none.

**A record cannot exempt itself and a file can, which is the one asymmetry here
that is not `phi_scan`'s.** A blob **is** a file, so ``--history`` honours a
``phi-scan: synthetic`` declaration exactly as `phi_scan.scan_text` does. An
issue body, a commit message and a path are not files: nobody reviewed them, and
a ticket *about* the pragma quotes the pragma by nature. Those go through
`phi_scan.scan_lines` with the shape layer forced on. `Record.is_file` is which.

**What it cannot reach, named rather than left to be discovered.** A commit
pushed and then force-pushed away is reachable by SHA on GitHub and by nothing
here. A harvest goes stale the moment anybody comments. GitHub keeps a previous
revision of every edited issue and comment and serves it to anyone with read
access, and **the API exposes no way to read or delete one**, so a redaction
this tool prompts is not the same as the text being gone. Date rewriting was a
third limit when this scanner found one real corpus day only as an ordinary
shape hit: the corpus held a dashed two-digit-year literal and two commit
messages used slashes and a four-digit year. **#261 moved that responsibility
to `phi_scan`**, which now normalizes parseable corpus dates across US numeric,
written English and ISO forms. Renderings outside those declared families still
escape unless the shape layer recognizes them. **Naming the literal in this
docstring would have been the same defect**, and the pre-commit hook refused the
commit that did.

**Counts only by default**, on `phi_scan.py`'s terms and for its reason: a
finding here is a patient identifier. **``--show`` output is PHI**: read it, do
not paste it. Deliberately **not** `reference_scan.py`'s exception -- that
module's output is bounded by what its code can draw from, and this one's is
bounded by nothing, because it reads whatever anybody typed.

**A human ruling on a published finding is committed without repeating its
literal.** ``reference/tracker-scan-rulings.json`` keys a commit verdict on the
full commit id, line, rule and SHA-256 digest of the containing line. A harvest
verdict replaces the commit id with the public record locator. The digest makes
a later line edit expire either ruling; it does not conceal a match whose
keyspace is enumerable, on
`ADR 0077 ruling 3 <../docs/adr/0077-a-digest-is-a-redaction-only-where-its-keyspace-is-large-and-a-date-literal-s-is-not.md>`_'s
terms. The full tuple is the finding: ruling a commit alone would let one
reviewed ratio hide another match in the same message. Each row clears one
finding at that line-level key, so repeated findings on one line require
repeated rows. A mismatch stays in the report; a malformed ledger applies no
rulings and makes the run not-scanned unless an unruled finding supplies the
stronger exit 1. The report states how many exact findings the ledger removed,
so a clean result never silently means *nothing was detected before rulings*.

Exit status distinguishes not having scanned from having found nothing -- 0
clean, 1 for a finding, **2 for every way of not having scanned**: no surface
named, a harvest file absent or not a JSON list, no record in any surface, a
git command that failed, no persistent pull-head refspec, no pull-head ref
without the acknowledgment, and no corpus without ``--allow-no-corpus`` or
``clinical.phiAllowNoCorpus``. **Where a finding and a not-scanned limb both
hold, 1 wins**, on `phi_scan.py`'s own ordering -- returning 2 would file the
strongest thing known about the surface under the weakest heading -- and every
banner prints beside it so the finding reads as a floor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date as CalendarDate
from pathlib import Path
from typing import Iterable, NamedTuple, Sequence, TypeVar

import phi_scan
from console_codec import use_utf8
from phi_scan import CorpusIndex, Finding

CLEAN = 0
FOUND = 1
NOT_SCANNED = 2

# `refs/pull/N/head` is the server's own name for a pull request's head, and the
# second marker is what the documented fetch leaves behind locally. Either one
# present means somebody has fetched them.
PULL_REF_MARKERS = ("refs/pull/", "/pr/")

PULL_REFSPEC = "+refs/pull/*/head:refs/remotes/origin/pr/*"
CONFIGURE_PULL_REFS = (
    f'git config --add remote.origin.fetch "{PULL_REFSPEC}"'
)
FETCH_PULL_REFS = "git fetch origin"
RULINGS_PATH = Path("reference/tracker-scan-rulings.json")
FULL_HARVEST_FILES = frozenset({
    "tracker-issues.json",
    "tracker-comments.json",
    "tracker-reviews.json",
})
RULING_VERDICTS = {"noise", "accepted-history"}
COMMIT_FINDING = re.compile(r"^commit ([0-9a-f]{40})$")
HARVEST_RECORD = re.compile(r"^https://github\.com/\S+ (?:title|body)$")


class Record(NamedTuple):
    """One piece of published text, with a label a reader can open.

    ``is_file`` is the pragma question and nothing else: a blob was a file that
    somebody reviewed, so it may declare ``phi-scan: synthetic``; an issue body
    was typed by whoever opened the issue and may not.
    """

    kind: str
    ref: str
    text: str
    is_file: bool = False


class HarvestError(Exception):
    """A harvest file that cannot be read as one. Always a not-scanned."""


class GitError(Exception):
    """A git command that failed.

    Its own class because the alternative is worse than an error: ``for-each-ref``
    returning nothing because it failed is indistinguishable from a repository
    with no pull-head refs, and that reads as *fetch them* rather than as
    *something is wrong here*.
    """


class RulingError(Exception):
    """A committed ruling ledger that cannot safely identify its findings."""


class RulingKey(NamedTuple):
    commit: str
    line: int
    rule: str
    line_sha256: str


class HarvestRulingKey(NamedTuple):
    record: str
    line: int
    rule: str
    line_sha256: str


RulingKeyT = TypeVar("RulingKeyT", RulingKey, HarvestRulingKey)


@dataclass(frozen=True)
class ScannedFinding(Finding):
    """A finding plus the non-enumerable identity of its containing line."""

    line_sha256: str


def _ruling_fields(
    path: Path, row: object, number: int, surface: str = ""
) -> tuple[dict, int, str, str, tuple[str, str]]:
    """Validate the fields shared by every line-level ruling row."""
    label = f"{surface + ' ' if surface else ''}row {number}"
    if not isinstance(row, dict):
        raise RulingError(f"{path}: {label} must be an object")
    line = row.get("line")
    rule = row.get("rule")
    digest = row.get("line_sha256")
    verdict = row.get("verdict")
    reason = row.get("reason")
    if not isinstance(line, int) or isinstance(line, bool) or line < 1:
        raise RulingError(f"{path}: {label} has an invalid line")
    if not isinstance(rule, str) or not rule:
        raise RulingError(f"{path}: {label} has an invalid rule")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise RulingError(f"{path}: {label} has an invalid line_sha256")
    if verdict not in RULING_VERDICTS:
        raise RulingError(f"{path}: {label} has an invalid verdict")
    if not isinstance(reason, str) or not reason.strip():
        raise RulingError(f"{path}: {label} has an invalid reason")
    return row, line, rule, digest, (verdict, reason)


def _add_ruling(
    path: Path,
    key: RulingKeyT,
    decision: tuple[str, str],
    decisions: dict[RulingKeyT, tuple[str, str]],
    rulings: Counter[RulingKeyT],
    conflict: str,
) -> None:
    """Add one verdict while refusing contradictory duplicate rows."""
    if key in decisions and decisions[key] != decision:
        raise RulingError(f"{path}: {conflict}")
    decisions[key] = decision
    rulings[key] += 1


def _run_git(
    repo: Path, *args: str, allowed_statuses: tuple[int, ...] = (0,)
) -> subprocess.CompletedProcess[str]:
    try:
        done = subprocess.run(
            ["git", *args], capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=repo,
        )
    except OSError as error:
        # A working directory that is not one, or no git on PATH. Both are the
        # same thing to a caller: no answer, rather than an empty one.
        raise GitError(f"git {args[0]}: {error}") from error
    if done.returncode not in allowed_statuses:
        first = done.stderr.strip().splitlines()
        raise GitError(f"git {args[0]}: {first[0] if first else 'failed'}")
    return done


def _git(repo: Path, *args: str) -> str:
    done = _run_git(repo, *args)
    return done.stdout


def records_from_github(data: object, source: str) -> list[Record]:
    """Records from one parsed ``gh api`` payload.

    One code path for issues, pull requests and comments, because GitHub's
    shapes differ only in which of the same keys are present -- an issue carries
    ``number``, ``title`` and ``body``; a comment carries ``id``, ``html_url``
    and ``body``. Reading them positionally would need three parsers and a way
    to tell which file is which, and the caller does not know: ``--harvest``
    takes a list of files and never asks what is in them.

    A title and a body become **two** records rather than one, so a finding says
    which of the two a reader has to go and edit.
    """
    if not isinstance(data, list):
        raise HarvestError(f"{source}: not a JSON list")

    records: list[Record] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        label = _label(item, source)
        title = item.get("title")
        if isinstance(title, str) and title.strip():
            records.append(Record("title", f"{label} title", title))
        body = item.get("body")
        if isinstance(body, str) and body.strip():
            records.append(Record("body", f"{label} body", body))
    return records


EVENT_RECORD_KEYS = {
    "issues": "issue",
    "issue_comment": "comment",
    "pull_request_target": "pull_request",
    "pull_request_review": "review",
    "pull_request_review_comment": "comment",
}


def records_from_github_event(
    data: object, event_name: str, source: str
) -> list[Record]:
    """The one record created or edited by a ruled GitHub tracker event.

    Incremental is load-bearing. A full harvest on every comment would replay
    every historical finding from #264, so an old warning would be the normal
    result and a new one would hide inside it. GitHub has already selected the
    changed object; this adapter only gives that object to the existing parser.
    """
    if not isinstance(data, dict):
        raise HarvestError(f"{source}: not a JSON object")
    key = EVENT_RECORD_KEYS.get(event_name)
    if key is None:
        raise HarvestError(f"{source}: unsupported GitHub event {event_name!r}")
    item = data.get(key)
    if not isinstance(item, dict):
        raise HarvestError(f"{source}: event has no {key!r} record")

    if data.get("action") == "edited":
        changes = data.get("changes")
        if not isinstance(changes, dict):
            raise HarvestError(f"{source}: edited event has no changes object")
        changed_item: dict = {
            field: item[field]
            for field in ("html_url", "number", "id")
            if field in item
        }
        for field in ("title", "body"):
            if field in changes and field in item:
                changed_item[field] = item[field]
        item = changed_item

    records = records_from_github([item], source)
    if records or data.get("action") != "edited":
        return records

    # Clearing a body publishes no text, but it is still a record the event
    # path completely scanned. Keep that distinct from an empty full harvest,
    # which remains NOT_SCANNED because it names no record at all.
    label = _label(item, source)
    return [
        Record(field, f"{label} {field}", item.get(field) or "")
        for field in ("title", "body")
        if field in item
    ]


def _label(item: dict, source: str) -> str:
    """The most openable name the payload offers.

    ``html_url`` first because it is the one a reader can paste into a browser,
    and a comment's id is not visible anywhere in the interface.
    """
    url = item.get("html_url")
    if isinstance(url, str) and url:
        return url
    number = item.get("number") or item.get("id")
    return f"{source}#{number}" if number else source


def load_harvest(paths: Sequence[Path]) -> list[Record]:
    records: list[Record] = []
    for path in paths:
        data = load_json(path)
        records.extend(records_from_github(data, path.name))
    return records


def load_json(path: Path) -> object:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as error:
        raise HarvestError(f"{path}: {error}") from error
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise HarvestError(f"{path}: {error}") from error
    return data


def load_github_event(path: Path, event_name: str) -> list[Record]:
    data = load_json(path)
    return records_from_github_event(data, event_name, path.name)


def pull_head_refs(repo: Path) -> list[str]:
    refs = _git(repo, "for-each-ref", "--format=%(refname)").splitlines()
    return [r for r in refs if any(marker in r for marker in PULL_REF_MARKERS)]


def pull_refspec_configured(repo: Path) -> bool:
    """Whether ordinary fetches refresh, and prune preserves, pull heads."""
    done = _run_git(
        repo, "config", "--local", "--get-all", "remote.origin.fetch",
        allowed_statuses=(0, 1),
    )
    wanted = PULL_REFSPEC.removeprefix("+")
    return any(
        value.strip().removeprefix("+") == wanted
        for value in done.stdout.splitlines()
    )


def commit_records(repo: Path) -> list[Record]:
    """Every commit message reachable from a ref, one record each.

    ``git log --all`` rather than ``--batch-all-objects``: see the module
    docstring on why an unreachable object is not a published surface.
    """
    out = _git(repo, "log", "--all", "--format=%H%x00%B%x01")
    records = []
    for chunk in out.split("\x01"):
        if "\x00" not in chunk:
            continue
        oid, message = chunk.split("\x00", 1)
        oid = oid.strip()
        if oid and message.strip():
            records.append(Record("commit", f"commit {oid}", message))
    return records


def load_rulings(
    repo: Path,
) -> tuple[Counter[RulingKey], Counter[HarvestRulingKey]]:
    """Read exact verdicts for immutable commits and published records."""
    path = repo / RULINGS_PATH
    if not path.is_file():
        return Counter(), Counter()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RulingError(f"{path}: {error}") from error
    if not isinstance(data, dict) or data.get("version") != 2:
        raise RulingError(f"{path}: version must be 2")
    commit_rows = data.get("commit_findings")
    if not isinstance(commit_rows, list):
        raise RulingError(f"{path}: commit_findings must be a list")
    harvest_rows = data.get("harvest_findings")
    if not isinstance(harvest_rows, list):
        raise RulingError(f"{path}: harvest_findings must be a list")

    rulings: Counter[RulingKey] = Counter()
    decisions: dict[RulingKey, tuple[str, str]] = {}
    for number, row in enumerate(commit_rows, 1):
        row, line, rule, digest, decision = _ruling_fields(path, row, number)
        commit = row.get("commit")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise RulingError(f"{path}: row {number} has an invalid commit")
        key = RulingKey(commit, line, rule, digest)
        _add_ruling(
            path, key, decision, decisions, rulings,
            f"row {number} conflicts with an earlier line ruling",
        )

    harvest_rulings: Counter[HarvestRulingKey] = Counter()
    harvest_decisions: dict[HarvestRulingKey, tuple[str, str]] = {}
    for number, row in enumerate(harvest_rows, 1):
        row, line, rule, digest, decision = _ruling_fields(
            path, row, number, "harvest"
        )
        record = row.get("record")
        if not isinstance(record, str) or not HARVEST_RECORD.fullmatch(record):
            raise RulingError(
                f"{path}: harvest row {number} has an invalid record"
            )
        key = HarvestRulingKey(record, line, rule, digest)
        _add_ruling(
            path, key, decision, harvest_decisions, harvest_rulings,
            f"harvest row {number} conflicts with an earlier line ruling",
        )
    return rulings, harvest_rulings


def partition_ruled_findings(
    findings: Sequence[ScannedFinding],
    rulings: Counter[RulingKey],
    harvest_rulings: Counter[HarvestRulingKey] | None = None,
) -> tuple[list[ScannedFinding], list[ScannedFinding]]:
    """Separate only findings whose commit or record identity matches exactly."""
    unruled: list[ScannedFinding] = []
    ruled: list[ScannedFinding] = []
    available = rulings.copy()
    available_harvest = (harvest_rulings or Counter()).copy()
    for finding in findings:
        match = COMMIT_FINDING.fullmatch(finding.path)
        key = RulingKey(
            match.group(1), finding.line, finding.rule,
            finding.line_sha256,
        ) if match else None
        if key is not None and available[key] > 0:
            ruled.append(finding)
            available[key] -= 1
        elif not match:
            harvest_key = HarvestRulingKey(
                finding.path, finding.line, finding.rule, finding.line_sha256
            )
            if available_harvest[harvest_key] > 0:
                ruled.append(finding)
                available_harvest[harvest_key] -= 1
            else:
                unruled.append(finding)
        else:
            unruled.append(finding)
    return unruled, ruled


def reachable_objects(repo: Path) -> dict[str, str]:
    """Object id to the one path label ``rev-list`` attaches, for reachable objects.

    One path per object and not one per appearance, because an object is content
    addressed: the same blob under two names is one object with one label. That
    is the harness artefact #212's body records having tripped over, and it is
    kept here as a label rather than trusted as *the* path.
    """
    labeled = {}
    for line in _git(repo, "rev-list", "--all", "--objects").splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].strip():
            labeled[parts[0]] = parts[1].strip()
        elif parts[0].strip():
            labeled.setdefault(parts[0].strip(), "")
    return labeled


def path_records(repo: Path) -> list[Record]:
    """Every distinct path ever committed, one record each."""
    paths = {p for p in reachable_objects(repo).values() if p}
    return [Record("path", path, path) for path in sorted(paths)]


def blob_counts(repo: Path) -> tuple[int, int]:
    """Reachable and unreachable blobs, so the docstring's claim is re-derived.

    The unreachable half is never scanned and is counted anyway. A number beside
    it is the only thing that makes *the walk this tool refuses to do* legible
    as a decision rather than as an omission.
    """
    reachable = set(reachable_objects(repo))
    every = _git(repo, "cat-file", "--batch-all-objects",
                 "--batch-check=%(objectname) %(objecttype)").splitlines()
    blobs = [line.split()[0] for line in every if line.split()[1:2] == ["blob"]]
    inside = sum(1 for oid in blobs if oid in reachable)
    return inside, len(blobs) - inside


def blob_records(repo: Path) -> list[Record]:
    """Every blob reachable from a ref, which is what a merged diff is made of.

    Read one at a time through a single ``cat-file --batch`` rather than by
    writing every id and then reading: the pipe would fill and both ends would
    wait. Binary blobs are dropped on `phi_scan.looks_binary`, which is the same
    NUL test `phi_scan` uses on the tree, so the committed code set is skipped
    here for the reason it is skipped there.
    """
    labels = reachable_objects(repo)
    every = _git(repo, "cat-file", "--batch-all-objects",
                 "--batch-check=%(objectname) %(objecttype)").splitlines()
    oids = [line.split()[0] for line in every
            if line.split()[1:2] == ["blob"] and line.split()[0] in labels]
    if not oids:
        return []

    records = []
    reader = subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=repo,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    try:
        for oid in oids:
            reader.stdin.write(f"{oid}\n".encode())
            reader.stdin.flush()
            header = b""
            while not header.endswith(b"\n"):
                byte = reader.stdout.read(1)
                if not byte:
                    raise GitError("git cat-file: stopped reading")
                header += byte
            size = int(header.decode().split()[2])
            data = reader.stdout.read(size)
            reader.stdout.read(1)
            if phi_scan.looks_binary(data):
                continue
            label = labels.get(oid) or "?"
            records.append(
                Record("blob", f"blob {oid[:10]} {label}",
                       data.decode("utf-8", errors="replace"), is_file=True)
            )
    finally:
        reader.stdin.close()
        reader.stdout.close()
        reader.wait()
    return records


def scan_records(records: Iterable[Record], index: CorpusIndex) -> list[ScannedFinding]:
    """Both layers over every record; only a **file** may switch the shapes off.

    `Record.is_file` decides, and nothing reads the exemption out of a record
    that is not one. A ticket about the ``dob`` shape quotes a ``dob`` and a
    ticket about the pragma quotes the pragma, so the record most likely to
    carry a real identifier is exactly the record that would have carried the
    declaration.
    """
    findings: list[ScannedFinding] = []
    for record in records:
        if record.is_file:
            record_findings = phi_scan.scan_text(record.text, record.ref, index)
        else:
            record_findings = phi_scan.scan_lines(
                record.text, record.ref, index, True
            )
        lines = record.text.splitlines()
        findings.extend(
            ScannedFinding(
                finding.path,
                finding.line,
                finding.rule,
                finding.match,
                hashlib.sha256(
                    lines[finding.line - 1].encode("utf-8")
                ).hexdigest(),
            )
            for finding in record_findings
        )
    return findings


def format_report(
    findings: Sequence[ScannedFinding],
    records: Sequence[Record],
    context: Sequence[tuple[str, int]],
    banners: Sequence[str],
    show: bool,
) -> str:
    lines = ["tracker-scan"]
    for kind, count in sorted(Counter(r.kind for r in records).items()):
        lines.append(f"  {kind + ' records':<30}{count}")
    for label, count in context:
        lines.append(f"  {label:<30}{count}")
    lines.append("")

    by_rule = Counter(f.rule for f in findings)
    if by_rule:
        for rule in sorted(by_rule):
            lines.append(f"  {rule:<30}{by_rule[rule]}")
        lines.append("")
        lines.append(f"  {len({f.path for f in findings})} record(s) carry a finding")
        if show:
            lines.append("")
            lines.extend(finding.render(True) for finding in findings)
        else:
            lines.append("  re-run with --show to see them -- that output is PHI")
    else:
        lines.append("  no finding")

    for banner in banners:
        lines.append("")
        lines.append(banner)
    return "\n".join(lines)


def write_harvest_marker(
    repo: Path,
    findings: Sequence[ScannedFinding],
    ran_on: CalendarDate | None = None,
) -> None:
    """Atomically record one completed full harvest without matched values."""
    target = repo / phi_scan.TRACKER_HARVEST_MARKER
    temporary = target.with_name(target.name + ".tmp")
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "ran_on": (CalendarDate.today() if ran_on is None else ran_on).isoformat(),
        "finding_counts": dict(sorted(Counter(f.rule for f in findings).items())),
    }
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(target)


def is_full_harvest(args: argparse.Namespace) -> bool:
    """Whether this invocation is only the documented three-surface harvest."""
    names = [path.name for path in args.harvest]
    return (
        len(names) == len(FULL_HARVEST_FILES)
        and set(names) == FULL_HARVEST_FILES
        and args.github_event is None
        and not args.commits
        and not args.history
        and not args.paths
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Scan tracker text, commit messages, blobs and paths for PHI.",
    )
    parser.add_argument("--harvest", nargs="+", type=Path, default=[])
    parser.add_argument("--github-event", type=Path)
    parser.add_argument("--event-name", choices=tuple(EVENT_RECORD_KEYS))
    parser.add_argument("--commits", action="store_true")
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--paths", action="store_true")
    parser.add_argument("--no-pull-refs", action="store_true")
    # Declared so argparse accepts it; the decision below reads
    # `phi_scan.allows_no_corpus`, which covers the flag **and** the git config
    # door. Testing `args` here as well would be one of the two doors
    # reimplemented, and the config one would still only work by accident.
    parser.add_argument(phi_scan.ALLOW_NO_CORPUS_FLAG, action="store_true",
                        dest="allow_no_corpus")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)

    if args.github_event and not args.event_name:
        parser.error("--github-event requires --event-name")
    if args.event_name and not args.github_event:
        parser.error("--event-name requires --github-event")

    if not (args.harvest or args.github_event or args.commits or args.history
            or args.paths):
        print("tracker-scan: DID NOT SCAN -- name a surface", file=sys.stderr)
        print("  --harvest <file.json> ... | --github-event <event.json> | "
              "--commits | --history | --paths",
              file=sys.stderr)
        return NOT_SCANNED

    repo = phi_scan.REPO_ROOT
    banners: list[str] = []
    context: list[tuple[str, int]] = []
    records: list[Record] = []
    rulings: Counter[RulingKey] = Counter()
    harvest_rulings: Counter[HarvestRulingKey] = Counter()
    unscanned = False

    try:
        if args.harvest:
            records.extend(load_harvest(args.harvest))
        if args.github_event:
            records.extend(load_github_event(args.github_event, args.event_name))

        if args.commits or args.history:
            refs = pull_head_refs(repo)
            context.append(("pull-head refs", len(refs)))
            configured = pull_refspec_configured(repo)
            if not configured and (refs or not args.no_pull_refs):
                banners.append(
                    "DID NOT SCAN the git surface -- the persistent pull-head\n"
                    "refspec is absent, so existing refs may be stale or removed\n"
                    "by an ordinary prune. Configure it once, then fetch:\n"
                    f"  {CONFIGURE_PULL_REFS}\n"
                    f"  {FETCH_PULL_REFS}"
                    + ("\n  or --no-pull-refs if this repository has none."
                       if not refs else "")
                )
                unscanned = True
            elif not refs and not args.no_pull_refs:
                banners.append(
                    "DID NOT SCAN the git surface -- the persistent pull-head\n"
                    "refspec is configured but no pull-head ref is present, so\n"
                    "every pull request whose branch was deleted is outside this\n"
                    "run.\n"
                    f"  {FETCH_PULL_REFS}\n"
                    "  or --no-pull-refs if this repository has none."
                )
                unscanned = True
            else:
                if not refs:
                    banners.append(
                        "Pull-head refs acknowledged absent. A pull request whose\n"
                        "branch was deleted after merging is NOT in this run."
                    )
                if args.commits:
                    records.extend(commit_records(repo))
                if args.history:
                    reachable, outside = blob_counts(repo)
                    context.append(("blobs never pushed, unread", outside))
                    records.extend(blob_records(repo))

        if args.paths:
            records.extend(path_records(repo))
    except (HarvestError, GitError) as error:
        print(f"tracker-scan: DID NOT SCAN -- {error}", file=sys.stderr)
        return NOT_SCANNED

    if args.commits or args.harvest:
        try:
            rulings, harvest_rulings = load_rulings(repo)
        except RulingError as error:
            banners.append(
                f"DID NOT APPLY commit rulings or harvest rulings -- {error}"
            )
            unscanned = True

    if not records and not unscanned:
        print("tracker-scan: DID NOT SCAN -- no record in any surface named",
              file=sys.stderr)
        return NOT_SCANNED

    # The corpus decision is taken **after** the scan and never before it, on
    # phi_scan.main's ordering. A dead corpus kills the corpus layer and leaves
    # the shape layer working, so returning early here would suppress a real
    # `dob` hit and report it as *did not scan* -- the strongest thing known
    # about the surface, filed under the weakest heading.
    missing = phi_scan.missing_corpus_sources()
    if missing:
        banners.append(phi_scan.no_corpus_hint(missing))
        if not phi_scan.allows_no_corpus(argv):
            unscanned = True

    names, dates = phi_scan.corpus_identifiers()
    coverage = phi_scan.corpus_coverage()
    findings = scan_records(records, phi_scan.build_index(names, dates))
    findings, ruled = partition_ruled_findings(
        findings, rulings, harvest_rulings
    )
    if ruled:
        context.append(("ruled findings", len(ruled)))
    if is_full_harvest(args) and not missing and not unscanned:
        try:
            write_harvest_marker(repo, findings)
        except OSError as error:
            banners.append(
                "DID NOT RECORD the full harvest marker -- " + str(error)
            )
            unscanned = True
    # Assemble this after the write so the producing harvest reports the marker
    # it just established instead of the state that existed at command start.
    banners.extend(phi_scan.shortfall_notice(coverage, missing))
    print(format_report(findings, records, context, banners, args.show))

    if findings:
        return FOUND
    return NOT_SCANNED if unscanned else CLEAN


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
