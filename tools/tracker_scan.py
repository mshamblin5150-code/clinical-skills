"""Scan the three surfaces a public flip publishes that no other checker reads.

[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212). Making
this repository public publishes more than its files. ``phi_scan --all`` reads
the tracked tree; nothing at all reads the **issue and pull-request text**, the
**commit messages**, or the **paths** -- and #212's own ruling comment names all
three as the surface it is blocked on, with
[#104](https://github.com/mshamblin5150-code/clinical-skills/issues/104)
recording that a commit message is scanned by nothing.

**Three limbs, and each is a different kind of thing to get hold of:**

- ``--harvest`` reads GitHub's own JSON for issues, pull requests and comments.
  **This tool opens no socket**, which is `research_ledger.py`'s ruling adopted
  whole -- the fetch is a documented ``gh`` command whose output is a file, so
  the scanner stays offline, testable and stdlib-only. The command is below.
- ``--commits`` reads every commit message reachable from a ref.
- ``--paths`` reads every path that has ever been committed.

Harvest first, then scan::

    gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" > issues.json
    gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" > comments.json
    gh api --paginate "repos/OWNER/REPO/pulls/comments?per_page=100" > reviews.json
    python tools/tracker_scan.py --harvest issues.json comments.json reviews.json

    git fetch origin "+refs/pull/*/head:refs/remotes/origin/pr/*"
    python tools/tracker_scan.py --commits --paths

**Reachability is the boundary of publication, and it cuts both ways.** #212's
scan walked ``git cat-file --batch-all-objects``, which is every object in the
local database including ones no ref reaches -- an amended commit, an abandoned
index write. Those were never pushed, so a finding in one is not an exposure;
measured here on 2026-08-19, the unreachable set carried findings the reachable
set did not, so the difference is not academic. **And the same walk
under-reads**: a pull request whose branch was deleted after merging keeps its
head at ``refs/pull/N/head`` on GitHub, which an ordinary clone does not fetch.
So this tool reads reachable objects only and **refuses to report on commit
messages until at least one pull-head ref is present**, printing the fetch
command -- `phi_scan.py`'s absent-corpus arrangement, for its reason: a scan of
half the published commits is not a clean scan, and nothing in a zero says which
it was.

``--no-pull-refs`` is the acknowledgment for a repository that genuinely has no
pull requests. Like ``--allow-no-corpus`` it converts the status and suppresses
nothing: the banner prints either way.

**What it cannot reach, named rather than left to be discovered.** A commit
pushed to a branch and then force-pushed away is reachable by SHA on GitHub and
by nothing here. An issue body edited after the harvest was taken is stale in
the file. And **a date rewritten into a format the corpus does not use escapes
the corpus layer entirely** -- a real day file's date, rewritten with slashes
and a four-digit year, was found in two commit messages here by reading the
shape-layer output, not by the corpus layer. **Naming the literal in this
docstring would have been the same defect**, and the pre-commit hook refused
the commit that did.

**Counts only by default**, on `phi_scan.py`'s terms and for its reason: a
finding here is a patient identifier. **``--show`` output is PHI**: read it, do
not paste it.

Exit status distinguishes not having scanned from having found nothing -- 0
clean, 1 for a finding, **2 for every way of not having scanned**: no surface
selected, a harvest file that is absent or is not a JSON list, no record in any
surface named, no corpus to scan against, and no pull-head ref without the
acknowledgment. **Where a finding and a not-scanned limb both hold, 1 wins**, on
`differential_scan.py`'s ordering, and the banner prints beside it so the
finding reads as a floor.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable, NamedTuple, Sequence

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

FETCH_PULL_REFS = 'git fetch origin "+refs/pull/*/head:refs/remotes/origin/pr/*"'


class Record(NamedTuple):
    """One piece of text, with a label a reader can open."""

    kind: str
    ref: str
    text: str


class HarvestError(Exception):
    """A harvest file that cannot be read as one. Always a not-scanned."""


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=repo,
    ).stdout


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
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as error:
            raise HarvestError(f"{path}: {error}") from error
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise HarvestError(f"{path}: {error}") from error
        records.extend(records_from_github(data, path.name))
    return records


def pull_head_refs(repo: Path) -> list[str]:
    refs = _git(repo, "for-each-ref", "--format=%(refname)").splitlines()
    return [r for r in refs if any(marker in r for marker in PULL_REF_MARKERS)]


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
            records.append(Record("commit", f"commit {oid[:10]}", message))
    return records


def path_records(repo: Path) -> list[Record]:
    """Every distinct path ever committed, as one record holding all of them.

    One record rather than one per path, because a path is a single line and a
    thousand records would print a banner longer than the report. A finding's
    line number is the path's position in the sorted list, and its match names
    the path.
    """
    paths = set()
    for line in _git(repo, "rev-list", "--all", "--objects").splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].strip():
            paths.add(parts[1].strip())
    if not paths:
        return []
    return [Record("paths", "paths ever committed", "\n".join(sorted(paths)))]


def scan_records(records: Iterable[Record], index: CorpusIndex) -> list[Finding]:
    """Both layers over every record, and **the shape layer is never optional**.

    `phi_scan.scan_lines` with ``shapes=True`` rather than `phi_scan.scan_text`,
    so a record carrying the synthetic pragma alone on a line does not switch
    the shape layer off. A **file** may make that declaration because a
    maintainer wrote it and a reviewer read it. An issue body is written by
    whoever opened the issue, and a ticket *about* the pragma quotes it by
    nature -- which is the same shape as the ``dob`` ticket that quoted a real
    one.
    """
    findings: list[Finding] = []
    for record in records:
        findings.extend(phi_scan.scan_lines(record.text, record.ref, index, True))
    return findings


def format_report(
    findings: Sequence[Finding],
    counts: Sequence[tuple[str, int]],
    banners: Sequence[str],
    show: bool,
) -> str:
    lines = ["tracker-scan"]
    for label, count in counts:
        lines.append(f"  {label:<32}{count}")
    lines.append("")

    by_rule: dict[str, int] = {}
    for finding in findings:
        by_rule[finding.rule] = by_rule.get(finding.rule, 0) + 1
    if by_rule:
        for rule in sorted(by_rule):
            lines.append(f"  {rule:<32}{by_rule[rule]}")
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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Scan tracker text, commit messages and paths for PHI.",
    )
    parser.add_argument("--harvest", nargs="+", type=Path, default=[])
    parser.add_argument("--commits", action="store_true")
    parser.add_argument("--paths", action="store_true")
    parser.add_argument("--no-pull-refs", action="store_true")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)

    if not (args.harvest or args.commits or args.paths):
        print("tracker-scan: DID NOT SCAN -- name a surface", file=sys.stderr)
        print("  --harvest <file.json> ... | --commits | --paths", file=sys.stderr)
        return NOT_SCANNED

    missing = phi_scan.missing_corpus_sources()
    if missing:
        print(phi_scan.no_corpus_hint(missing), file=sys.stderr)
        return NOT_SCANNED

    repo = phi_scan.REPO_ROOT
    banners: list[str] = []
    counts: list[tuple[str, int]] = []
    records: list[Record] = []

    if args.harvest:
        try:
            harvested = load_harvest(args.harvest)
        except HarvestError as error:
            print(f"tracker-scan: DID NOT SCAN -- {error}", file=sys.stderr)
            return NOT_SCANNED
        counts.append(("tracker records", len(harvested)))
        records.extend(harvested)

    unscanned = False
    if args.commits:
        pull_refs = pull_head_refs(repo)
        counts.append(("pull-head refs", len(pull_refs)))
        if not pull_refs and not args.no_pull_refs:
            banners.append(
                "DID NOT SCAN the commit messages -- no pull-head ref is present,\n"
                "so every pull request whose branch was deleted is outside this run.\n"
                f"  {FETCH_PULL_REFS}\n"
                "  or --no-pull-refs if this repository has none."
            )
            unscanned = True
        else:
            if not pull_refs:
                banners.append(
                    "Pull-head refs acknowledged absent. A pull request whose\n"
                    "branch was deleted after merging is NOT in this run."
                )
            commits = commit_records(repo)
            counts.append(("commit messages", len(commits)))
            records.extend(commits)

    if args.paths:
        walked = path_records(repo)
        counts.append(
            ("paths ever committed",
             len(walked[0].text.splitlines()) if walked else 0)
        )
        records.extend(walked)

    if not records and not unscanned:
        print("tracker-scan: DID NOT SCAN -- no record in any surface named",
              file=sys.stderr)
        return NOT_SCANNED

    names, dates = phi_scan.corpus_identifiers()
    findings = scan_records(records, phi_scan.build_index(names, dates))
    print(format_report(findings, counts, banners, args.show))

    if findings:
        return FOUND
    return NOT_SCANNED if unscanned else CLEAN


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
