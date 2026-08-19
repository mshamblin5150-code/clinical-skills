"""Scan what a public flip publishes that a file scanner does not read.

[#212](https://github.com/mshamblin5150-code/clinical-skills/issues/212). Making
this repository public publishes more than its tracked tree. ``phi_scan --all``
walks ``git ls-files``, which is the tip and nothing else; #212's ruling comment
is blocked on **issue and pull-request text**, **pull-request diffs**, and
**commit messages**, and
[#104](https://github.com/mshamblin5150-code/clinical-skills/issues/104) records
the last of those as scanned by nothing.

**Four limbs, and the mapping to those three is not one-to-one:**

- ``--harvest`` reads GitHub's own JSON for issues, pull requests and comments.
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

    gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" \\
        > scratch/tracker-issues.json
    gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" \\
        > scratch/tracker-comments.json
    gh api --paginate "repos/OWNER/REPO/pulls/comments?per_page=100" \\
        > scratch/tracker-reviews.json
    python tools/tracker_scan.py --harvest scratch/tracker-*.json

    git fetch origin "+refs/pull/*/head:refs/remotes/origin/pr/*"
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
``--commits`` and ``--history`` **refuse until at least one pull-head ref is
present**, printing the fetch command -- `phi_scan.py`'s absent-corpus
arrangement, for its reason: a scan of half the published objects is not a clean
scan, and nothing in a zero says which it was. ``--no-pull-refs`` is the
acknowledgment for a repository that genuinely has none.

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
this tool prompts is not the same as the text being gone. And **a date rewritten
into a format the corpus does not hold escapes the corpus layer entirely** -- a
real day file's date, with slashes and a four-digit year, sits in two commit
messages here where it reads as an ordinary shape hit beside a hundred census
ratios. That was found by reading the shape-layer output, not by the corpus
layer. **Naming the literal in this docstring would have been the same defect**,
and the pre-commit hook refused the commit that did.

**Counts only by default**, on `phi_scan.py`'s terms and for its reason: a
finding here is a patient identifier. **``--show`` output is PHI**: read it, do
not paste it. Deliberately **not** `reference_scan.py`'s exception -- that
module's output is bounded by what its code can draw from, and this one's is
bounded by nothing, because it reads whatever anybody typed.

Exit status distinguishes not having scanned from having found nothing -- 0
clean, 1 for a finding, **2 for every way of not having scanned**: no surface
named, a harvest file absent or not a JSON list, no record in any surface, a
git command that failed, no pull-head ref without the acknowledgment, and no
corpus without ``--allow-no-corpus`` or ``clinical.phiAllowNoCorpus``. **Where a
finding and a not-scanned limb both hold, 1 wins**, on `phi_scan.py`'s own
ordering -- returning 2 would file the strongest thing known about the surface
under the weakest heading -- and every banner prints beside it so the finding
reads as a floor.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
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


def _git(repo: Path, *args: str) -> str:
    try:
        done = subprocess.run(
            ["git", *args], capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=repo,
        )
    except OSError as error:
        # A working directory that is not one, or no git on PATH. Both are the
        # same thing to a caller: no answer, rather than an empty one.
        raise GitError(f"git {args[0]}: {error}") from error
    if done.returncode != 0:
        first = done.stderr.strip().splitlines()
        raise GitError(f"git {args[0]}: {first[0] if first else 'failed'}")
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


def reachable_objects(repo: Path) -> dict[str, str]:
    """Object id to the one path label ``rev-list`` attaches, for reachable objects.

    One path per object and not one per appearance, because an object is content
    addressed: the same blob under two names is one object with one label. That
    is the harness artefact #212's body records having tripped over, and it is
    kept here as a label rather than trusted as *the* path.
    """
    labelled = {}
    for line in _git(repo, "rev-list", "--all", "--objects").splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[1].strip():
            labelled[parts[0]] = parts[1].strip()
        elif parts[0].strip():
            labelled.setdefault(parts[0].strip(), "")
    return labelled


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


def scan_records(records: Iterable[Record], index: CorpusIndex) -> list[Finding]:
    """Both layers over every record; only a **file** may switch the shapes off.

    `Record.is_file` decides, and nothing reads the exemption out of a record
    that is not one. A ticket about the ``dob`` shape quotes a ``dob`` and a
    ticket about the pragma quotes the pragma, so the record most likely to
    carry a real identifier is exactly the record that would have carried the
    declaration.
    """
    findings: list[Finding] = []
    for record in records:
        if record.is_file:
            findings.extend(phi_scan.scan_text(record.text, record.ref, index))
        else:
            findings.extend(
                phi_scan.scan_lines(record.text, record.ref, index, True)
            )
    return findings


def format_report(
    findings: Sequence[Finding],
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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Scan tracker text, commit messages, blobs and paths for PHI.",
    )
    parser.add_argument("--harvest", nargs="+", type=Path, default=[])
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

    if not (args.harvest or args.commits or args.history or args.paths):
        print("tracker-scan: DID NOT SCAN -- name a surface", file=sys.stderr)
        print("  --harvest <file.json> ... | --commits | --history | --paths",
              file=sys.stderr)
        return NOT_SCANNED

    repo = phi_scan.REPO_ROOT
    banners: list[str] = []
    context: list[tuple[str, int]] = []
    records: list[Record] = []
    unscanned = False

    try:
        if args.harvest:
            records.extend(load_harvest(args.harvest))

        if args.commits or args.history:
            refs = pull_head_refs(repo)
            context.append(("pull-head refs", len(refs)))
            if not refs and not args.no_pull_refs:
                banners.append(
                    "DID NOT SCAN the git surface -- no pull-head ref is present,\n"
                    "so every pull request whose branch was deleted is outside\n"
                    "this run.\n"
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
    findings = scan_records(records, phi_scan.build_index(names, dates))
    print(format_report(findings, records, context, banners, args.show))

    if findings:
        return FOUND
    return NOT_SCANNED if unscanned else CLEAN


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
