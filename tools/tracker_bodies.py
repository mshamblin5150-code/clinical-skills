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
sequences, so a report can be compared across both mechanisms. #723 adds the
fifth row: does the raw body contain a C0 control other than tab, line feed, or
carriage return. It deliberately reads the unstripped body and does not remove
code spans, because a raw control character cannot be a mention.

Harvest first, then scan::

    : "${TICKET_NUMBER:?set TICKET_NUMBER to the current ticket number}"
    H=$(python tools/scratch_work.py ticket "$TICKET_NUMBER")
    mkdir -p "$H"
    gh api graphql -f owner=OWNER -f name=REPO \
        -f query='query($owner:String!,$name:String!){repository(owner:$owner,name:$name){issues{totalCount} pullRequests{totalCount}}}' \
        > "$H/tracker-issues-population.json"
    gh api --include "repos/OWNER/REPO/issues/comments?per_page=1&page=1" \
        > "$H/tracker-comments-population.http"
    gh api --include "repos/OWNER/REPO/pulls/comments?per_page=1&page=1" \
        > "$H/tracker-reviews-population.http"
    python tools/tracker_population.py \
        "$H/tracker-issues-population.json" \
        "$H/tracker-comments-population.http" \
        "$H/tracker-reviews-population.http" \
        --write "$H/tracker-population.json"
    gh api --paginate "repos/OWNER/REPO/issues?state=all&per_page=100" \\
        > "$H/tracker-issues.json"
    gh api --paginate "repos/OWNER/REPO/issues/comments?per_page=100" \\
        > "$H/tracker-comments.json"
    gh api --paginate "repos/OWNER/REPO/pulls/comments?per_page=100" \\
        > "$H/tracker-reviews.json"
    python tools/tracker_bodies.py \
        "$H/tracker-issues.json" "$H/tracker-comments.json" \
        "$H/tracker-reviews.json" --population "$H/tracker-population.json"

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

**What it cannot reach is owned by ``NOT_REACHED`` below.** The object includes
the wider escape-collapse class and the two character exclusions ADR 0099
requires; this docstring deliberately copies no row or dated tracker figure.

**It is also the read-back, and ``-`` is how.** ``records_from_github`` takes a
single JSON object as well as a list, so ``gh issue view <n> --json
number,body,url | python tools/tracker_bodies.py -`` grades one record the
moment it is filed -- which catches what ``--jq '.body | length'`` does not,
since a lost body has a length of 2 and reads as a number rather than as a
failure.

**The complete body grader runs at both publication hosts, with deliberately
asymmetric posture.** ``tracker_publish_hook.py`` passes every readable body
through ``grade`` and refuses each returned row from the Claude Code publisher;
titles keep two predicates outside this body-only interface.
``.github/workflows/tracker.yml`` calls this command's ``--github-event`` mode
for a changed body from either known publisher and reports after publication.
The hook's remaining publisher limit is owned by
``tracker_publish_hook.NOT_REACHED`` rather than restated here.

**A clean scan is not a body worth reading**, ``docs/agents/issue-tracker.md``
says so beside the command, and a test asserts that sentence is still there.

Exit status distinguishes not having scanned from having found nothing -- 0
clean, 1 for a failed body, **2 for every way of not having scanned**: no
argument, an unsupported argument or incomplete event pair, a harvest or event
file absent or unreadable, a payload that is neither a JSON list nor a JSON
object, and **no record in any file read**. That last limb is the one that matters and it is
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

from tracker_records import (
    EVENT_RECORD_KEYS,
    TrackerRecord,
    from_actions_event,
    from_command,
)
import tracker_scan

from console_codec import require_python_floor, use_utf8
from prose_bind import prose_outside_code as _shared_prose_outside_code

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
C0_CONTROL_CHARACTER = "c0-control-character"
CARRIAGE_RETURN_FLANKED = "carriage-return-flanked"
LITERAL_NEWLINE_ESCAPE = "literal-newline-escape"
DOUBLED_PATH_SEPARATOR = "doubled-path-separator"

# Every row, in report order. One tuple, so the report, the counter and the
# ticket map cannot drift into listing different sets.
KINDS = (
    LOST_AT_DASH,
    EMPTY_BODY,
    LITERAL_AT_PATH,
    DOUBLE_ENCODED,
    C0_CONTROL_CHARACTER,
    CARRIAGE_RETURN_FLANKED,
    LITERAL_NEWLINE_ESCAPE,
    DOUBLED_PATH_SEPARATOR,
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
    C0_CONTROL_CHARACTER: "#723",
    CARRIAGE_RETURN_FLANKED: "#777",
    LITERAL_NEWLINE_ESCAPE: "#777",
    DOUBLED_PATH_SEPARATOR: "#777",
}

# Predicate nesting is declared independently of row order. A body of ``@-``
# satisfies the lone-at-token spelling too, but it is one lost-body defect and
# remains one finding. Co-occurring, independently repairable escape-collapse
# symptoms are not suppressed.
SUBSUMED_BY = {
    LITERAL_AT_PATH: LOST_AT_DASH,
}

NOT_REACHED = (
    (
        "an empty, at-dash, literal-at-path, or double-encoded title",
        "Titles stay outside the lost-body rows and double-encoded row. None "
        "of 1,088 titles fired on 2026-09-11, and gh issue and gh pr have no "
        "title-file flag through which the measured file-backed loss occurred. "
        "The dated count comes from ADR 0177's full tracker harvest and title "
        "grade in its measurement section.",
    ),
    (
        "an escape collapse that leaves only lost backticks",
        "A collapse that removes backticks without leaving any other graded "
        "symptom remains outside every row. ADR 0136 records the dated residue.",
    ),
    (
        "a carriage return not flanked by non-space",
        "A carriage return with whitespace or a body edge on either side is "
        "outside the flanked predicate, including ordinary line endings.",
    ),
    (
        "a partial literal-newline collapse or one in a title",
        "A body with any surviving real line break is outside this row, as is "
        "every title; ADR 0136 records both deliberate exclusions.",
    ),
    (
        "a doubled separator in a relative path or title",
        "The predicate requires a drive letter before the doubled separator "
        "and grades bodies only, so relative paths and titles remain outside it.",
    ),
    (
        "DEL U+007F",
        "U+007F is not a C0 control, no escape in the measured collapsing table "
        "produces it, and ADR 0099 did not measure it.",
    ),
    (
        "replacement character U+FFFD",
        "A U+FFFD in a loaded harvest may be this scanner's own substitution "
        "for an undecodable byte, so the published record and input decoding "
        "cannot be distinguished by this row.",
    ),
    (
        "a body that landed with another bounded defect",
        "Truncation at a shell metacharacter, half a heredoc, and the right text "
        "on the wrong ticket can all carry text without matching a row here.",
    ),
    (
        "a harvest that became stale after publication",
        "A saved harvest stops representing the current tracker as soon as "
        "another record is created or edited.",
    ),
    (
        "an edited empty body versus one filed empty",
        "The current GitHub record cannot establish whether an empty body was "
        "empty at filing time or was edited empty afterward.",
    ),
)

# Derived from the declared row names so a newly added longer row cannot make
# the pasteable report ragged. ``research_ledger.py`` learned this the hard way:
# a row one character over the pad went ragged in the one output meant to be
# pasted.
KIND_COLUMN = max(len(kind) for kind in KINDS)
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
LITERAL_NEWLINE = re.compile(r"\\n")
DOUBLED_DRIVE_SEPARATOR = re.compile(r"(?i)[a-z]:\\\\")
LIST_PREFIX = re.compile(r" {0,3}(?:[-+*]|[0-9]{1,9}[.)])[ \t]{1,4}")
LIST_MARKER_PREFIX = re.compile(r" {0,3}(?:[-+*]|[0-9]{1,9}[.)])[ \t]")
QUOTE_PREFIX = re.compile(r" {0,3}>[ \t]?")


def prose_outside_code(text: str, *, preserve_lines: bool = False) -> str:
    """Mask Markdown code with the shared offset-preserving reader."""

    return _shared_prose_outside_code(text)


def has_c0_control_character(text: str) -> bool:
    """Whether raw tracker text contains C0 except tab, LF, and CR."""
    return any(ord(character) < 0x20 and character not in "\t\n\r"
               for character in text)


def has_carriage_return_flanked(text: str) -> bool:
    """Whether a carriage return has non-space on both sides."""
    return any(
        index > 0
        and index + 1 < len(text)
        and not text[index - 1].isspace()
        and not text[index + 1].isspace()
        for index, character in enumerate(text)
        if character == "\r"
    )


def has_literal_newline_escape(text: str) -> bool:
    """Whether a one-line body carries ``\\n`` outside Markdown code."""
    if "\r" in text or "\n" in text:
        return False
    prose = prose_outside_code(text)
    return LITERAL_NEWLINE.search(prose) is not None


def has_doubled_path_separator(text: str) -> bool:
    """Whether a drive letter has a doubled separator outside Markdown code."""
    prose = prose_outside_code(text)
    return DOUBLED_DRIVE_SEPARATOR.search(prose) is not None


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


HTML_BLOCK_TAG = re.compile(
    r"</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|"
    r"col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|"
    r"footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|"
    r"link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|"
    r"section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul)"
    r"(?:[ \t]|/?>|$)", re.IGNORECASE,
)


class HtmlBlock(NamedTuple):
    end_kind: str
    end_value: str
    container: str = "top"
    indent: int = 0


def html_block_opening(visible: str, *, container: str = "top", indent: int = 0) -> HtmlBlock | None:
    if re.match(r"<(?:script|pre|style|textarea)(?:[ \t]|>|$)", visible, re.I):
        return HtmlBlock("tag", "", container, indent)
    for prefix, ending in {"<!--": "-->", "<?": "?>", "<![CDATA[": "]]>",}.items():
        if visible.startswith(prefix):
            return HtmlBlock("marker", ending, container, indent)
    if re.match(r"<![A-Z]", visible):
        return HtmlBlock("marker", ">", container, indent)
    if HTML_BLOCK_TAG.match(visible):
        return HtmlBlock("blank", "", container, indent)
    return None


def html_block_closes(block: HtmlBlock, content: str) -> bool:
    if block.end_kind == "marker":
        return block.end_value in content
    if block.end_kind == "tag":
        return bool(re.search(r"</(?:pre|script|style|textarea)>", content, re.I))
    return not content.strip()


def html_block_continuation(line: str, block: HtmlBlock) -> str | None:
    if block.container == "top":
        return line.lstrip(" ")
    if block.container == "quote":
        match = QUOTE_PREFIX.match(line)
        return None if match is None else line[match.end():]
    if not line.strip():
        return ""
    indentation = len(line) - len(line.lstrip(" "))
    if not line.startswith("\t") and indentation < block.indent:
        return None
    return line[block.indent:]


def starts_html_block(visible: str) -> bool:
    return html_block_opening(visible) is not None


def starts_markdown_block(line: str) -> bool:
    visible = line.lstrip(" ")
    return bool(
        QUOTE_PREFIX.match(line) or LIST_PREFIX.match(line)
        or re.match(r"#{1,6}(?:[ \t]+|$)", visible)
        or re.fullmatch(r"(?:\*[ \t]*){3,}", visible)
        or re.fullmatch(r"(?:-[ \t]*){3,}", visible)
        or re.fullmatch(r"(?:_[ \t]*){3,}", visible)
        or starts_html_block(visible)
    )


def starts_markdown_paragraph(content: str) -> bool:
    return bool(content.strip()) and not starts_markdown_block(content)


def ordinary_paragraph_prose(text: str) -> str:
    """Return unfenced, unquoted, non-list Markdown paragraph lines."""
    lines = []
    list_indent: int | None = None
    lazy_quote = lazy_list = False
    html_block: HtmlBlock | None = None
    for line in prose_outside_code(text, preserve_lines=True).splitlines():
        if html_block is not None:
            content = html_block_continuation(line, html_block)
            if content is not None:
                if html_block_closes(html_block, content):
                    html_block = None
                continue
            html_block = None
        if not line.strip():
            lazy_quote = lazy_list = False
            lines.append("")
            continue
        indentation = len(line) - len(line.lstrip(" "))
        if list_indent is not None and (line.startswith("\t") or indentation >= list_indent):
            content = line[list_indent:]
            opening = html_block_opening(content, container="list", indent=list_indent)
            if opening:
                lazy_list = False
                if not html_block_closes(opening, content):
                    html_block = opening
                continue
            if lazy_list and starts_markdown_block(content):
                lazy_list = False
            continue
        match = QUOTE_PREFIX.match(line)
        if match:
            content = line[match.end():]
            opening = html_block_opening(content, container="quote")
            if opening:
                lazy_quote = False
                if not html_block_closes(opening, content):
                    html_block = opening
            else:
                lazy_quote = starts_markdown_paragraph(content)
            lazy_list = False
            list_indent = None
            continue
        if lazy_quote:
            if not starts_markdown_block(line):
                continue
            lazy_quote = False
        match = LIST_PREFIX.match(line)
        if match:
            marker = LIST_MARKER_PREFIX.match(line)
            list_indent = marker.end() if not line[match.end():].strip() else match.end()
            content = line[list_indent:]
            opening = html_block_opening(content, container="list", indent=list_indent)
            if opening:
                lazy_list = False
                if not html_block_closes(opening, content):
                    html_block = opening
            else:
                lazy_list = starts_markdown_paragraph(content)
            lazy_quote = False
            continue
        if lazy_list:
            if not starts_markdown_block(line):
                continue
            lazy_list = False
            list_indent = None
        if line.startswith("\t") or line.startswith("    "):
            continue
        visible = line.lstrip(" ")
        opening = html_block_opening(visible)
        if opening:
            if not html_block_closes(opening, visible):
                html_block = opening
            continue
        lines.append(visible)
    return "\n".join(lines)


class Record(NamedTuple):
    """One tracker record's body, with a label a reader can open."""

    harvest: str
    label: str
    surface: str
    body: str | None
    tracker: TrackerRecord | None = None


class Finding(NamedTuple):
    """One failed body. Carries no text from the record -- see the docstring."""

    kind: str
    label: str
    surface: str


class Scan(NamedTuple):
    records: int
    by_surface: tuple[tuple[str, int], ...]
    counts: tuple[tuple[str, int], ...]
    failed_records: int
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
        surface = _surface(item)
        label = _label(item, source)
        raw_labels = item.get("labels", [])
        labels = tuple(
            row.get("name") if isinstance(row, dict) else row
            for row in raw_labels
            if isinstance(row, (dict, str))
        ) if isinstance(raw_labels, list) else ()
        pull_request = surface == PULL or "/pull/" in label
        if surface == COMMENT:
            route = ("pr", "comment") if pull_request else ("issue", "comment")
        else:
            route = ("pr", "view") if pull_request else ("issue", "view")
        records.append(Record(
            harvest=source,
            label=label,
            surface=surface,
            body=body if isinstance(body, str) else None,
            tracker=from_command(
                body if isinstance(body, str) else "",
                url=label,
                number=item.get("number"),
                labels=labels,
                route=route,
            ),
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
    if stream is None:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    else:
        raw = stream.read()
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


def records_from_github_event(
    data: object, event_name: str, source: str
) -> list[Record]:
    """The body created or edited by one GitHub tracker event."""
    if not isinstance(data, dict):
        raise HarvestError(f"{source}: not a JSON object")
    typed = from_actions_event(data, event_name)
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
        if "body" not in changes:
            return []
        item = {
            field: item[field]
            for field in ("html_url", "url", "number", "id", "body")
            if field in item
        }
    else:
        item = dict(item)

    if event_name == "pull_request_target":
        item["pull_request"] = {}
    return [row._replace(tracker=typed) for row in records_from_github(item, source)]


def load_github_event(path: Path, event_name: str) -> list[Record]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        raise HarvestError(
            f"{path.name}: {error.strerror or 'unreadable'}"
        ) from error
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise HarvestError(f"{path.name}: {error.msg}") from error
    return records_from_github_event(data, event_name, path.name)


def grade(records: Sequence[Record]) -> list[Finding]:
    """Every matching finding, except predicate nesting declared above.

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
        prose = prose_outside_code(text)
        matches = {
            LOST_AT_DASH: text == AT_DASH,
            EMPTY_BODY: not text,
            LITERAL_AT_PATH: LONE_AT_TOKEN.match(text) is not None,
            DOUBLE_ENCODED: (
                _has_cp1252_mojibake(prose)
                or LITERAL_UNICODE_ESCAPE.search(prose) is not None
            ),
            C0_CONTROL_CHARACTER: has_c0_control_character(record.body or ""),
            CARRIAGE_RETURN_FLANKED: has_carriage_return_flanked(record.body or ""),
            LITERAL_NEWLINE_ESCAPE: has_literal_newline_escape(record.body or ""),
            DOUBLED_PATH_SEPARATOR: has_doubled_path_separator(record.body or ""),
        }
        if matches[LOST_AT_DASH]:
            found.append(Finding(LOST_AT_DASH, record.label, record.surface))
        if matches[EMPTY_BODY]:
            found.append(Finding(EMPTY_BODY, record.label, record.surface))
        if (matches[LITERAL_AT_PATH]
                and not matches[SUBSUMED_BY[LITERAL_AT_PATH]]):
            found.append(Finding(LITERAL_AT_PATH, record.label, record.surface))
        if matches[DOUBLE_ENCODED]:
            found.append(Finding(DOUBLE_ENCODED, record.label, record.surface))
        if matches[C0_CONTROL_CHARACTER]:
            found.append(Finding(
                C0_CONTROL_CHARACTER, record.label, record.surface
            ))
        if matches[CARRIAGE_RETURN_FLANKED]:
            found.append(Finding(
                CARRIAGE_RETURN_FLANKED, record.label, record.surface
            ))
        if matches[LITERAL_NEWLINE_ESCAPE]:
            found.append(Finding(
                LITERAL_NEWLINE_ESCAPE, record.label, record.surface
            ))
        if matches[DOUBLED_PATH_SEPARATOR]:
            found.append(Finding(
                DOUBLED_PATH_SEPARATOR, record.label, record.surface
            ))
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
        failed_records=sum(bool(grade([record])) for record in records),
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
    lines.append(
        f"  bodies failed                  {scan.failed_records}"
        f"    findings {len(scan.findings)}"
    )
    if scan.findings:
        lines.append("")
        lines.append("  each one, by the row it failed and the record to open:")
        for finding in scan.findings:
            lines.append(
                f"    {finding.kind:<{KIND_COLUMN}} "
                f"{finding.surface:<{SURFACE_COLUMN}} {finding.label}"
            )
    return "\n".join(lines)


USAGE = (
    "usage: tracker_bodies.py <a gh api harvest .json> [more ...] "
    "--population <tracker-population.json> | - | "
    "--github-event <event.json> --event-name <name>"
)


def main(argv: list[str], stdin=None) -> int:
    """``argv`` is the argument list without the program name."""
    argv = list(argv)
    population_path = None
    if "--population" in argv:
        index = argv.index("--population")
        if argv.count("--population") != 1 or index + 1 >= len(argv):
            print(f"--population requires one manifest path\n{USAGE}", file=sys.stderr)
            return NOT_SCANNED
        population_path = Path(argv[index + 1])
        del argv[index:index + 2]
    # **Every unrecognized argument is refused rather than filtered out**, and
    # that is not tidiness. The first version dropped anything starting with
    # ``--`` from the path list, so ``--show`` was accepted, ignored, and
    # answered with the ordinary report and the ordinary status -- a caller
    # believing it had asked for something. On a module whose central claim is
    # that no such flag exists, a silent no-op is the one behavior worse than
    # an error.
    event_mode = "--github-event" in argv or "--event-name" in argv
    if event_mode:
        if population_path is not None:
            print(f"--population applies only to a harvest\n{USAGE}", file=sys.stderr)
            return NOT_SCANNED
        if (len(argv) != 4 or argv.count("--github-event") != 1
                or argv.count("--event-name") != 1):
            print(f"--github-event and --event-name are required together\n{USAGE}",
                  file=sys.stderr)
            return NOT_SCANNED
        event_path = Path(argv[argv.index("--github-event") + 1])
        event_name = argv[argv.index("--event-name") + 1]
        if not event_path.is_file():
            print(f"no event file named {event_path.name}", file=sys.stderr)
            return NOT_SCANNED
        source = f"{event_name} event {event_path.name}"
        try:
            records = load_github_event(event_path, event_name)
        except HarvestError as error:
            print(str(error), file=sys.stderr)
            return NOT_SCANNED
    else:
        records = []

    unknown = [a for a in argv if a.startswith("-") and a != STDIN]
    if event_mode:
        unknown = []
    if unknown:
        print(f"unknown option {' '.join(unknown)}\n{USAGE}", file=sys.stderr)
        return NOT_SCANNED
    if not argv:
        print(USAGE, file=sys.stderr)
        return NOT_SCANNED
    if event_mode:
        pass
    elif STDIN in argv:
        if population_path is not None:
            print(f"--population applies only to a harvest\n{USAGE}", file=sys.stderr)
            return NOT_SCANNED
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
        if population_path is None:
            print(
                "DID NOT ESTABLISH the full harvest population -- "
                "pass --population <tracker-population.json>.",
                file=sys.stderr,
            )
            return NOT_SCANNED
        if {path.name for path in paths} != tracker_scan.FULL_HARVEST_FILES:
            print(
                "DID NOT ESTABLISH the full harvest population -- "
                "the harvest must name exactly tracker-issues.json, "
                "tracker-comments.json, and tracker-reviews.json.",
                file=sys.stderr,
            )
            return NOT_SCANNED
        observed = {
            path.name: sum(record.harvest == path.name for record in records)
            for path in paths
        }
        try:
            populations, short = tracker_scan.population_coverage(
                population_path, paths, observed
            )
        except tracker_scan.HarvestError as error:
            print(
                "DID NOT ESTABLISH the full harvest population -- " + str(error),
                file=sys.stderr,
            )
            return NOT_SCANNED
        for name in sorted(populations):
            print(
                f"{name} population {populations[name]}; unread remainder "
                f"{max(populations[name] - observed[name], 0)}; "
                f"records read {observed[name]}"
            )
        if short:
            for name, count, population in short:
                print(
                    "DID NOT ESTABLISH a complete harvest -- "
                    f"{name}: {count} of population {population} record(s).",
                    file=sys.stderr,
                )
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
            " Repair each through its matching GitHub edit path and read it back.",
            file=sys.stderr,
        )
        return FOUND
    return CLEAN


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
