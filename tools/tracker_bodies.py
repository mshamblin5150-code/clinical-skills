"""Grade a tracker harvest for bodies malformed at filing time.

[#130](https://github.com/mshamblin5150-code/clinical-skills/issues/130). Records
in this repo carry a body that is the literal two characters ``@-`` -- what
``gh`` writes when a heredoc collapses, or when ``gh api -f body=@-`` is typed
for ``-F``. **`gh` exits 0 every time.** The ticket is created, labeled
correctly, and looks fine in ``gh issue list``; nothing in the loop can tell a
successful write of the wrong thing from a successful write of the right thing.

**How many there are is what this command prints, and it was eight on
2026-08-19.** The figure is dated wherever it is written rather than stated flat,
because the harvest it is counted from is gitignored, nothing committed
re-derives it, and a ninth arriving moves it -- which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143). Two
other files carry it and both do so as the *denominator* of the finding below,
where dropping it would cost the finding its meaning.

**Decision 2 of that ticket was answered in prose four days before it was
asked** -- ``docs/agents/issue-tracker.md`` has carried both ``--body-file -``
and the read-back since 2026-08-11 -- and the bodies kept being lost anyway.
This module is #214's *what a written instruction cannot do is fail* arriving at
the tracker: the rule is written out there **and** a command grades it.

**Decision 3 is ruled: an empty body is a failure here.** Clinician, 2026-08-19.
Those three rows ask one question three ways -- did text land. #155 adds the
fourth row: did text land with UTF-8 decoded through cp1252, or with a literal
``\\uXXXX`` escape left undecoded. The row counts affected records, not damaged
sequences, so a report can be compared across both mechanisms.

Harvest first, then scan::

    gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" \\
        > scratch/tracker-issues.json
    gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" \\
        > scratch/tracker-comments.json
    gh api --paginate "repos/OWNER/REPO/pulls/comments?per_page=100" \\
        > scratch/tracker-reviews.json
    python tools/tracker_bodies.py scratch/tracker-*.json

**Three surfaces, which is `tracker_scan.py`'s set and not a subset of it.** The
review-comment endpoint is the one easiest to leave out, and it carries bodies
like any other. It holds no lost body today; a harvest that omitted it would
report that as a clean scan of it rather than as not having read it.

**It opens no socket**, which is `tracker_scan.py`'s ruling adopted whole and
`research_ledger.py`'s before it: the fetch is a documented ``gh`` command whose
output is a file, so the scanner stays offline, stdlib-only and testable, and
the harvest is a thing a reader can keep and re-scan.

**Into ``scratch/`` for `tracker_scan.py`'s reason** -- the harvest is the
tracker's entire text, and ``scratch/`` is the PHI firewall's own directory.

**The ``issues`` REST payload and never ``gh issue list``, which is the ticket's
own finding rather than a preference.** That command excludes pull requests. Two
of the eight it found on 2026-08-19 are pull requests -- #98 and #71 -- so
**every sweep that ran #130's own reproduce command re-derived *six, not eight*
and concluded
the title was stale.** Its **count** was right -- the *three are still open*
half
really had gone stale, which is what made the whole title easy to dismiss -- and
the instrument could not see two of its members, and said six with no way to
know it. That is this repo's recurring shape once more: a search that could not
have worked, answering like a settled negative. The REST endpoint returns both,
and a ``pull_request`` key is which.

**`tracker_scan.records_from_github` cannot be reused, and the reason is
exact:** it drops a body that is empty or whitespace -- correct for a PHI scan,
since there is no text to find -- and that is precisely the record this module
exists to report. A test asserts the sibling still drops it, so the duplication
stays justified rather than merely inherited.

**No ``--show``.** The report names the record's URL and the row's own name and
never the body, so **its output is safe to paste**. The encoding row inspects
prose but reports none of it; a shape inside inline or fenced code is a mention
and does not fire.

**What it cannot reach**, named rather than left to be discovered:

- **A body that landed and is wrong in any other way.** Truncated at a shell
  metacharacter, half a heredoc, the right words about the wrong ticket -- every
  one of those has text and matches no mechanically bounded row here.
- **A harvest goes stale the moment anybody files**, which is `tracker_scan.py`'s
  limit inherited whole.
- **A record edited to remove its body after filing** reads identically to one
  that never had one.

**It is also the read-back, and ``-`` is how.** ``records_from_github`` takes a
single JSON object as well as a list, so ``gh issue view <n> --json
number,body,url | python tools/tracker_bodies.py -`` grades one record the
moment it is filed -- which catches what ``--jq '.body | length'`` does not,
since a lost body has a length of 2 and reads as a number rather than as a
failure.

**Nothing runs any of this, and that limit is declared rather than left to be
found.** #130's decision 2 asked whether the documented step is enough or needs
enforcing, and comment 16 grounded it: *nothing mechanical checks a body*, and
``tools/hooks/`` holds only ``pre-commit``. **That sentence is still true.** A
hook cannot help -- a commit is not a filing, and the tracker is not in the tree
-- so this narrows the gap to *a check exists and somebody has to run it* and
does not close it. **A command nobody runs is a written instruction with extra
steps**, which is #214's own thesis pointed back at this module.

**A clean scan is not a body worth reading**, ``docs/agents/issue-tracker.md``
says so beside the command, and a test asserts that sentence is still there.

Exit status distinguishes not having scanned from having found nothing -- 0
clean, 1 for a failed body, **2 for every way of not having scanned**: no
argument, **an argument this module does not have**, a harvest file absent or
unreadable, a payload that is neither a JSON list nor a JSON object, and **no
record in any file read**. That last limb is the one that matters and it is
`differential_scan.py`'s reasoning: an empty payload would otherwise report zero
lost bodies and read exactly like a tracker that has none. **One unreadable file
among several is a 2 and not a partial scan**, which is the same rule one level
up.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import NamedTuple, Sequence

from console_codec import use_utf8

CLEAN = 0
FOUND = 1
NOT_SCANNED = 2

# Which surface a record came from. Printed, so a reader knows whether to open an
# issue, a pull request or a comment -- and kept apart in the counts because
# #130's whole finding is that one of the three was invisible to the instrument
# every sweep used.
ISSUE = "issue"
PULL = "pull request"
COMMENT = "comment"

LOST_AT_DASH = "lost-at-dash"
EMPTY_BODY = "empty-body"
LITERAL_AT_PATH = "literal-at-path"
DOUBLE_ENCODED = "double-encoded"

# Every row, in report order. One tuple, so the report, the counter and the
# ticket map cannot drift into listing different sets.
KINDS = (
    LOST_AT_DASH,
    EMPTY_BODY,
    LITERAL_AT_PATH,
    DOUBLE_ENCODED,
)

# Which ruling each row belongs to, so a reader knows which ticket to go and
# read. **Spelled out rather than built from ``KINDS``**, on `checks_ledger.py`'s
# reasoning: a comprehension would assign #130 to a row the next ticket adds, so
# the map could never fail.
ROW_TICKET = {
    LOST_AT_DASH: "#130",
    EMPTY_BODY: "#130",
    LITERAL_AT_PATH: "#130",
    DOUBLE_ENCODED: "#155",
}

# Wide enough for the longest kind and the longest surface, so both stay
# columns. ``research_ledger.py`` learned this the hard way: a row one
# character over the pad went ragged in the one output meant to be pasted.
KIND_COLUMN = 18
SURFACE_COLUMN = 13
# The report's own label column, wide enough for the longest surface plural.
COUNT_COLUMN = 29

# The exact two characters, and nothing that merely contains them. A body
# *about* the trap quotes it by nature -- this module's own docstring does -- so
# the test is equality on the stripped body and never a substring.
AT_DASH = "@-"

# One token, beginning with ``@``, no whitespace anywhere in the body. The
# narrowest form that catches ``--body @notes.md`` while leaving ``@someone
# please look`` alone. **Zero occurrences across the tracker on 2026-08-19**, so
# this row is grounded in the trap ``issue-tracker.md`` documents rather than in
# a measured instance -- which is exactly why it is not widened. What it costs is
# that a body which is only a bare at-mention fires; that body is worth a look
# here anyway.
LONE_AT_TOKEN = re.compile(r"\A@\S+\Z")
LITERAL_UNICODE_ESCAPE = re.compile(r"\\u[0-9a-fA-F]{4}")
FENCED_CODE = re.compile(
    r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$"
)
CODE_SPAN = re.compile(r"`+[^`\n]*`+")


def _has_cp1252_mojibake(text: str) -> bool:
    """Whether a UTF-8 sequence in ``text`` was decoded through cp1252."""
    for start in range(len(text)):
        for width in (2, 3, 4):
            candidate = text[start:start + width]
            if len(candidate) != width:
                continue
            try:
                encoded = candidate.encode("cp1252")
            except UnicodeEncodeError:
                continue
            lead = encoded[0]
            expected = (2 if 0xC2 <= lead <= 0xDF else
                        3 if 0xE0 <= lead <= 0xEF else
                        4 if 0xF0 <= lead <= 0xF4 else 0)
            if expected != width:
                continue
            try:
                encoded.decode("utf-8")
            except UnicodeDecodeError:
                continue
            return True
    return False


class Record(NamedTuple):
    """One tracker record's body, with a label a reader can open."""

    harvest: str
    label: str
    surface: str
    body: str | None


class Finding(NamedTuple):
    """One failed body. Carries no text from the record -- see the docstring."""

    kind: str
    label: str
    surface: str


class Scan(NamedTuple):
    records: int
    by_surface: tuple[tuple[str, int], ...]
    counts: tuple[tuple[str, int], ...]
    findings: tuple[Finding, ...]


class HarvestError(Exception):
    """A harvest file that cannot be read as one. Always a not-scanned."""


def records_from_github(data: object, source: str) -> list[Record]:
    """Records from one parsed ``gh`` payload.

    One code path for issues, pull requests and comments, because GitHub's
    shapes differ only in which of the same keys are present. **A single object
    is accepted as well as a list**, and that is where this departs from
    `tracker_scan.records_from_github`, which refuses anything but a list:
    ``gh issue view N --json number,body`` emits an object, so accepting one
    makes this module the read-back step ``issue-tracker.md`` already asks for
    rather than only a sweep tool.

    **Every record is kept whatever its body is**, including absent and null.
    Filtering here is what makes the sibling unusable for this job.
    """
    if isinstance(data, dict):
        items: Sequence[object] = [data]
    elif isinstance(data, list):
        items = data
    else:
        raise HarvestError(f"{source}: not a JSON list or object")

    records = []
    for item in items:
        if not isinstance(item, dict):
            continue
        body = item.get("body")
        records.append(Record(
            harvest=source,
            label=_label(item, source),
            surface=_surface(item),
            body=body if isinstance(body, str) else None,
        ))
    return records


def _surface(item: dict) -> str:
    """Issue, pull request or comment.

    The ``pull_request`` key is GitHub's own marker on the ``issues`` endpoint,
    and reading it is the whole of #130's finding: without it a pull request is
    reported as an issue, and with ``gh issue list`` it is not reported at all.
    A comment has no ``number``.
    """
    if "pull_request" in item:
        return PULL
    return ISSUE if "number" in item else COMMENT


def _label(item: dict, source: str) -> str:
    """The most openable name the payload offers.

    ``html_url`` first because it is the one a reader can paste into a browser;
    ``url`` next because that is the key ``gh issue view --json url`` writes.
    """
    for key in ("html_url", "url"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    number = item.get("number") or item.get("id")
    return f"{source}#{number}" if number else source


STDIN = "-"


def read_stdin(stream=None) -> list[Record]:
    """The read-back limb: one record piped straight from ``gh issue view``.

    **``-`` and never a path to a device.** The documented form was
    ``/dev/stdin``, which does not exist on the platform every commit here is
    made from -- ``Path('/dev/stdin').is_file()`` is ``False``, so the module
    answered *no harvest file named dev/stdin* and exited 2. A documented
    command that cannot run is worse than none, because it reads as a checked
    one; caught by review before it merged, and it is why this is a named
    argument rather than a path the caller has to spell.
    """
    raw = (stream if stream is not None else sys.stdin).read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise HarvestError(f"standard input: {error.msg}") from error
    return records_from_github(data, "standard input")


def load_harvest(paths: Sequence[Path]) -> list[Record]:
    """Every record across every file.

    **One unreadable file raises rather than being skipped**, because a partial
    read reported as a clean scan is the failure this whole directory exists to
    refuse.
    """
    records: list[Record] = []
    for path in paths:
        try:
            # ``errors="replace"`` is #150's rule at the input end of the same
            # boundary, and it is load-bearing rather than tidy here.
            # ``UnicodeDecodeError`` is a ``ValueError`` and not an ``OSError``,
            # so a bare read let it escape ``main`` -- and a traceback exits
            # **1**, which this module's contract reads as *a lost body found*.
            # A replaced byte fails ``json.loads`` instead, which is a 2.
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            # ``strerror`` and not ``str(error)``: the latter carries the full
            # path, and a harvest sits under ``scratch/``.
            raise HarvestError(f"{path.name}: {error.strerror or 'unreadable'}") from error
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise HarvestError(f"{path.name}: {error.msg}") from error
        records.extend(records_from_github(data, path.name))
    return records


def grade(records: Sequence[Record]) -> list[Finding]:
    """One finding per failed body, at most one per record.

    The order is ``KINDS``'s and the first match wins, which is what keeps
    ``@-`` off the literal-path row: it is a lone ``@`` token too, and grading it
    twice would double every count the eight known instances contribute.

    **Each branch names its own row rather than assigning one to a variable**,
    which looks like repetition and is what makes the row set checkable: the
    completeness walk in the test reads ``Finding(...)``'s first argument, and a
    local variable is opaque to it. A walk that cannot see the row it is
    counting reads as coverage while providing none -- which is
    ``test_console_codec.py``'s substring-search lesson, and it was caught here
    the same way, by the walk going green on a set containing nothing.
    """
    found = []
    for record in records:
        text = (record.body or "").strip()
        prose = CODE_SPAN.sub(" ", FENCED_CODE.sub(" ", text))
        if text == AT_DASH:
            found.append(Finding(LOST_AT_DASH, record.label, record.surface))
        elif not text:
            found.append(Finding(EMPTY_BODY, record.label, record.surface))
        elif LONE_AT_TOKEN.match(text):
            found.append(Finding(LITERAL_AT_PATH, record.label, record.surface))
        elif (_has_cp1252_mojibake(prose)
              or LITERAL_UNICODE_ESCAPE.search(prose)):
            found.append(Finding(DOUBLE_ENCODED, record.label, record.surface))
    return found


def survey(records: Sequence[Record]) -> Scan:
    found = grade(records)
    return Scan(
        records=len(records),
        by_surface=tuple(
            (surface, sum(1 for r in records if r.surface == surface))
            for surface in (ISSUE, PULL, COMMENT)
        ),
        counts=tuple(
            (kind, sum(1 for f in found if f.kind == kind)) for kind in KINDS
        ),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str) -> str:
    """The report, as one string.

    **Carries no text from any record**, and there is no flag that widens it. A
    finding prints the row's own name -- this module's text -- and the record's
    URL, which is what a reader has to open to repair it.
    """
    # Plain ASCII throughout, on ``icd10_lookup.py``'s reasoning: this prints to
    # a Windows console where anything outside cp1252 reads like corruption in
    # the one output meant to be pasted.
    lines = [
        f"tracker bodies over {source}",
        "",
        f"  records read                   {scan.records}",
    ]
    for surface, count in scan.by_surface:
        lines.append(f"    {surface + 's':<{COUNT_COLUMN}}{count}")
    lines.append("")
    for kind, count in scan.counts:
        lines.append(f"  {ROW_TICKET[kind]} - {kind:<{KIND_COLUMN}} {count}")
    lines.append("")
    lines.append(f"  bodies failed                  {len(scan.findings)}")
    if scan.findings:
        lines.append("")
        lines.append("  each one, by the row it failed and the record to open:")
        for finding in scan.findings:
            lines.append(
                f"    {finding.kind:<{KIND_COLUMN}} "
                f"{finding.surface:<{SURFACE_COLUMN}} {finding.label}"
            )
    return "\n".join(lines)


USAGE = "usage: tracker_bodies.py <a gh api harvest .json> [more ...] | -"


def main(argv: list[str], stdin=None) -> int:
    """``argv`` is the argument list without the program name."""
    # **Every unrecognized argument is refused rather than filtered out**, and
    # that is not tidiness. The first version dropped anything starting with
    # ``--`` from the path list, so ``--show`` was accepted, ignored, and
    # answered with the ordinary report and the ordinary status -- a caller
    # believing it had asked for something. On a module whose central claim is
    # that no such flag exists, a silent no-op is the one behavior worse than
    # an error.
    unknown = [a for a in argv if a.startswith("-") and a != STDIN]
    if unknown:
        print(f"unknown option {' '.join(unknown)}\n{USAGE}", file=sys.stderr)
        return NOT_SCANNED
    if not argv:
        print(USAGE, file=sys.stderr)
        return NOT_SCANNED
    if STDIN in argv:
        if len(argv) > 1:
            print(f"- reads one payload and takes no other argument\n{USAGE}",
                  file=sys.stderr)
            return NOT_SCANNED
        source = "standard input"
        try:
            records = read_stdin(stdin)
        except HarvestError as error:
            print(str(error), file=sys.stderr)
            return NOT_SCANNED
    else:
        paths = [Path(a) for a in argv]
        missing = [p for p in paths if not p.is_file()]
        if missing:
            # The name, never the path: a harvest sits under ``scratch/``.
            print(
                "no harvest file named " + ", ".join(p.name for p in missing),
                file=sys.stderr,
            )
            return NOT_SCANNED
        source = ", ".join(p.name for p in paths)
        try:
            records = load_harvest(paths)
        except HarvestError as error:
            print(str(error), file=sys.stderr)
            return NOT_SCANNED
    if not records:
        # The limb that matters. An empty payload would otherwise report zero
        # failed bodies and read exactly like a tracker that has none.
        print(f"no record in {source}", file=sys.stderr)
        return NOT_SCANNED
    scan = survey(records)
    print(format_report(scan, source=source))
    if scan.findings:
        print(
            f"{len(scan.findings)} body/bodies failed tracker checks."
            " Rewrite each with 'gh issue edit <n> --body-file -'"
            " and read it back.",
            file=sys.stderr,
        )
        return FOUND
    return CLEAN


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
