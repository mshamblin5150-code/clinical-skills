"""Identity and trust checks for shared, out-of-repo build artifacts.

A clean artifact is reusable when its caller names the files that produced it and
those files are unchanged. Legacy stamps establish that through an ancestor commit;
content-addressed stamps carry the exact producer-file hashes, so unrelated commits
with identical producer inputs can reuse the same verified artifact. During a merge,
either parent is a valid ancestor and comparison remains against the merged tree.

``--allow-untrusted-provenance`` is the deliberate escape hatch. This module owns
both halves of what that costs: the *trace*, which announces an accepted distrust
on a channel no warnings filter reaches, and the *publication rule*, which refuses
to let an untrusted read publish inside a git checkout. #406, and docs/adr/0010.

For the two curated artifacts a person can carry a verdict into, this module also
owns the accepted-distrust declaration grammar and the pass/retirement rule. #460,
and docs/adr/0019. What none of those mechanisms reaches is ``NOT_GUARDED``.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import warnings
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from repo_root import ensure_outside_checkout


REPO_ROOT = Path(__file__).resolve().parent.parent

FLAG = "--allow-untrusted-provenance"

# The five parsers that declare the flag differ in their verb and their noun -- one
# reads a corpus, one indexes it, one grades against it, one reads an index. What
# they share is the *consequence*, and the consequence is the half this repo had
# already got wrong: every one of them said "and warn" while the trace was a
# RuntimeWarning that PYTHONWARNINGS=ignore silenced outright. So the shared object
# is the effect clause rather than the whole string, and tools/test_write_guards.py
# asserts no parser spells it out as a bare literal.
FLAG_HELP_EFFECT = "traces to stderr on every check and continues"
FLAG_HELP_NO_PUBLISH = "and refuses publication inside a git checkout"

CACHE_IDENTITY = {
    "extraction": (
        "tools/guidelines_extract.py",
        "tools/guidelines_manifest.py",
        "tools/artifact_provenance.py",
    ),
    "index": (
        "tools/guidelines_index.py",
        "tools/guidelines_index_artifact.py",
        "tools/guidelines_manifest.py",
        "tools/artifact_provenance.py",
    ),
    "recs": (
        "tools/guidelines_recs.py",
        "tools/guidelines_extract.py",
        "tools/artifact_provenance.py",
        "reference/guidelines-uspstf.md",
    ),
}

TRUST_FLOOR = {
    "extraction": (
        "tools/guidelines_extract.py",
        "tools/guidelines_manifest.py",
    ),
    "index": (
        "tools/guidelines_index.py",
        "tools/guidelines_manifest.py",
    ),
    "recs": (
        "tools/guidelines_recs.py",
        "tools/guidelines_extract.py",
        "reference/guidelines-uspstf.md",
    ),
}

# Hand-kept by clinician ruling rather than inferred from flag-bearing commands.
# A mechanical predicate cannot decide whether a command's durable output is a
# human verdict; ADR 0019 rejected that guess explicitly.
ACCEPTED_DISTRUST_COMMANDS = ("guidelines_catalog", "threshold_sheet")

WHY_NO_PUBLISH = (
    f"{FLAG} exists for deliberate development work, and publishing a committed "
    "artifact is not development work -- see issue #406 and docs/adr/0010. Send the "
    "artifact outside every checkout, or drop the flag and read a trusted artifact."
)

# Declared rather than built, on #254's and #141's terms: a limit a reader can find
# beside the mechanism, instead of prose somewhere that fails nothing when it stops
# being true.
NOT_GUARDED = (
    (
        "the guard is on publication, not on the file",
        "--out to a temp path followed by a hand copy into the checkout defeats it, "
        "and always will.",
    ),
    (
        "nothing mechanically catches a further flag-bearing command",
        "#176 refused a predicate over which tools publish. Some commands declaring "
        "this flag produce nothing durable at all, and deciding that mechanically is "
        "the guess that ticket rejected.",
    ),
    (
        "the warning deduplicates and the stderr line does not",
        "Python's default filter prints one warning per unique message and site. The "
        "print is the audit trace and fires on every check, so the dedup is left as "
        "correct warnings semantics for the programmatic hook rather than repaired.",
    ),
)


def _trace(message: str) -> None:
    """Announce an accepted distrust, on a channel no warnings filter reaches.

    **Two channels deliberately.** ``warnings.warn`` stays because a caller may catch
    it programmatically and this repo's own suite does in several places. The print is
    the audit record: ``PYTHONWARNINGS=ignore`` cannot silence it, and it never
    deduplicates, so an artifact checked twice traces twice. An ambient ``error`` filter
    cannot turn the deliberately accepted distrust back into a refusal either.

    **Lowercase rather than a banner**, on #258's register ruling. A shout is what
    ``PATIENT NAMES ARE NOT CHECKED`` spends on a safety check going *unenforced*;
    this one ran, found the problem, and was overridden on purpose by the person
    reading the terminal. The clause naming the flag is the part that matters -- a
    later reader of a scrollback otherwise cannot tell why the run continued.
    """
    print(f"{message} -- continuing because {FLAG} was given", file=sys.stderr)
    try:
        warnings.warn(message, RuntimeWarning, stacklevel=3)
    except RuntimeWarning:
        pass


def refuse_publication(destination: Path | str, *, allow_untrusted: bool) -> Path:
    """The resolved destination, or ``InsideCheckout`` before an untrusted publish.

    A no-op when the flag is off: a trusted read may publish wherever its own guard
    allows, and this rule is about the hatch rather than about placement in general.

    **#383's rule one artifact over** -- *a dirty checkout may reuse a trusted build
    but may not publish a new one*. ``uspstf_table`` is the only caller today because
    it is the only flag-bearing command that can publish inside the repo at all; see
    ``NOT_GUARDED`` for why no walk asserts that stays true.
    """
    resolved = Path(destination)
    if not allow_untrusted:
        return resolved
    return ensure_outside_checkout(resolved, detail=WHY_NO_PUBLISH)


class UntrustedProvenance(ValueError):
    """An artifact cannot be tied to the checkout that is consuming it."""


@dataclass(frozen=True)
class ProvenanceCheck:
    producer: dict[str, object] | None
    reasons: tuple[str, ...]

    @property
    def trusted(self) -> bool:
        return not self.reasons


@dataclass(frozen=True)
class AcceptedDistrust:
    """The human-authored declaration that holds a verdict earned under distrust."""

    corpus: str
    date: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class AcceptedDistrustVerdict:
    """What a passing gate owes the declaration in the artifact it grades."""

    failures: tuple[str, ...] = ()
    not_graded: bool = False
    expected: str | None = None


_ACCEPTED_DISTRUST = re.compile(
    r"^accepted distrust against (?P<corpus>.+) on "
    r"(?P<date>\d{4}-\d{2}-\d{2}):$"
)
_ACCEPTED_DISTRUST_PREFIX = "accepted distrust against "


def render_accepted_distrust(
    corpus: Path | str,
    reasons: tuple[str, ...],
    *,
    on: date | None = None,
) -> str:
    """Render the declaration without paraphrasing any provenance reason."""
    today = on or date.today()
    lines = [f"{_ACCEPTED_DISTRUST_PREFIX}{Path(corpus).resolve()} on {today.isoformat()}:"]
    lines.extend(f"  - {reason}" for reason in reasons)
    return "\n".join(lines)


def parse_accepted_distrust(
    text: str,
) -> tuple[AcceptedDistrust | None, tuple[str, ...]]:
    """Read the one accepted-distrust declaration in a curated Markdown region."""
    lines = text.splitlines()
    starts: list[int] = []
    fence: tuple[str, int] | None = None
    in_comment = False
    for index, line in enumerate(lines):
        visible = line
        if in_comment:
            if "-->" not in visible:
                continue
            visible = visible.split("-->", 1)[1]
            in_comment = False
        while "<!--" in visible:
            before, after = visible.split("<!--", 1)
            if "-->" in after:
                visible = before + after.split("-->", 1)[1]
            else:
                visible = before
                in_comment = True
                break

        if fence is not None:
            character, width = fence
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(character)}{{{width},}}[ \t]*", visible
            )
            if closing:
                fence = None
            continue

        opening = re.match(r"^ {0,3}(?P<fence>`{3,}|~{3,})", visible)
        if opening:
            marker = opening.group("fence")
            fence = (marker[0], len(marker))
            continue
        if visible.startswith(_ACCEPTED_DISTRUST_PREFIX):
            starts.append(index)
    if not starts:
        return None, ()
    if len(starts) != 1:
        return None, ("more than one accepted distrust declaration is present",)
    index = starts[0]
    match = _ACCEPTED_DISTRUST.fullmatch(lines[index])
    if match is None:
        return None, ("the accepted distrust declaration header is malformed",)
    reasons: list[str] = []
    for line in lines[index + 1 :]:
        if line.startswith("  - "):
            reasons.append(line.removeprefix("  - "))
            continue
        break
    if not reasons:
        return None, ("the accepted distrust declaration carries no provenance reasons",)
    return (
        AcceptedDistrust(match.group("corpus"), match.group("date"), tuple(reasons)),
        (),
    )


def grade_accepted_distrust(
    declaration: AcceptedDistrust | None,
    corpus: Path | str,
    provenance: ProvenanceCheck,
    *,
    passed: bool,
    on: date | None = None,
) -> AcceptedDistrustVerdict:
    """Bind a genuine gate pass to its declaration, or retire a superseded one."""
    if not passed:
        return AcceptedDistrustVerdict()
    expected = render_accepted_distrust(corpus, provenance.reasons, on=on)
    if provenance.trusted:
        if declaration is None:
            return AcceptedDistrustVerdict()
        return AcceptedDistrustVerdict(
            failures=(
                "a trusted passing run supersedes the accepted distrust declaration; "
                "delete the accepted distrust declaration",
            ),
        )
    if declaration is None:
        return AcceptedDistrustVerdict(not_graded=True, expected=expected)
    parsed_expected, _ = parse_accepted_distrust(expected)
    if declaration != parsed_expected:
        return AcceptedDistrustVerdict(
            failures=(
                "the accepted distrust declaration describes different distrust than "
                "this run; replace it with:\n" + expected,
            ),
        )
    return AcceptedDistrustVerdict()


def current_producer(repo_root: Path = REPO_ROOT) -> dict[str, str | bool]:
    """Return the commit and dirty state of the checkout running a producer."""
    commit = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain", "--untracked-files=normal"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout
    )
    return {"commit": commit, "dirty": dirty}


def producer_file_identity(
    paths: tuple[str, ...], repo_root: Path = REPO_ROOT
) -> list[dict[str, str]]:
    """Record the exact checkout bytes that determine an artifact's contents."""
    return [
        {
            "path": Path(path).as_posix(),
            "sha256": hashlib.sha256((repo_root / path).read_bytes()).hexdigest(),
        }
        for path in paths
    ]


def _is_checkout_ancestor(commit: str, repo_root: Path) -> bool:
    """Whether ``commit`` belongs to either side of the checkout's live history."""
    candidates = ["HEAD", "MERGE_HEAD"]
    return any(
        subprocess.run(
            ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", commit, candidate],
            capture_output=True,
        ).returncode
        == 0
        for candidate in candidates
    )


def _paths_unchanged(commit: str, paths: tuple[str, ...], repo_root: Path) -> bool:
    """Whether the checkout is running the producer paths recorded by ``commit``."""
    return (
        subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--quiet", commit, "--", *paths],
            capture_output=True,
        ).returncode
        == 0
    )


def _content_inputs(
    value: object, repo_root: Path, required_paths: tuple[str, ...] = ()
) -> tuple[bool | None, list[dict[str, str]]]:
    """Whether an explicit producer-file identity matches this checkout."""
    if value is None:
        return None, []
    if not isinstance(value, list) or not value:
        return False, []
    normalized: list[dict[str, str]] = []
    for row in value:
        if not isinstance(row, dict):
            return False, []
        relative = row.get("path")
        expected = row.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            return False, []
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            return False, []
        target = (repo_root / path).resolve()
        if not target.is_relative_to(repo_root.resolve()) or not target.is_file():
            return False, []
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != expected:
            return False, []
        normalized.append({"path": path.as_posix(), "sha256": expected})
    recorded_paths = {row["path"] for row in normalized}
    if not {Path(path).as_posix() for path in required_paths} <= recorded_paths:
        return False, []
    return True, normalized


def check_producer(
    producer: object,
    artifact: Path | str,
    *,
    allow_untrusted: bool = False,
    expected_commit: str | None = None,
    repo_root: Path = REPO_ROOT,
    unchanged_paths: tuple[str, ...] = (),
) -> ProvenanceCheck:
    """Validate a producer stamp against the checkout consuming the artifact."""
    expected = expected_commit or str(current_producer(repo_root)["commit"])
    reasons: list[str] = []
    normalized: dict[str, object] | None = None
    if not isinstance(producer, dict):
        reasons.append("has no producer provenance stamp")
    else:
        commit = producer.get("commit")
        dirty = producer.get("dirty")
        inputs_match, inputs = _content_inputs(
            producer.get("inputs"), repo_root, unchanged_paths
        )
        if not isinstance(commit, str) or not commit:
            reasons.append("has no producer commit")
        if not isinstance(dirty, bool):
            reasons.append("has no producer dirty-state flag")
        if inputs_match is None and unchanged_paths:
            reasons.append("records no producer-file identity")
        if inputs_match is False:
            reasons.append("producer inputs do not match the current checkout")
        unchanged_ancestor = (
            isinstance(commit, str)
            and bool(commit)
            and bool(unchanged_paths)
            and _is_checkout_ancestor(commit, repo_root)
            and _paths_unchanged(commit, unchanged_paths, repo_root)
        )
        if (
            isinstance(commit, str)
            and commit
            and commit != expected
            and not unchanged_ancestor
            and inputs_match is not True
        ):
            reasons.append(f"was produced by a different commit ({commit}; current is {expected})")
        if (
            unchanged_paths
            and not _paths_unchanged("HEAD", unchanged_paths, repo_root)
            and inputs_match is not True
        ):
            reasons.append(
                "producer files have uncommitted changes in the working tree "
                "since the artifact was built"
            )
        if dirty is True and inputs_match is not True:
            reasons.append("was produced by a dirty checkout")
        if isinstance(commit, str) and commit and isinstance(dirty, bool):
            normalized = {"commit": commit, "dirty": dirty}
            if inputs_match is True:
                normalized["inputs"] = inputs

    check = ProvenanceCheck(normalized, tuple(reasons))
    if check.reasons:
        message = f"untrusted artifact {artifact}: " + "; ".join(check.reasons)
        if not allow_untrusted:
            raise UntrustedProvenance(message)
        _trace(message)
    return check


def check_derived(
    provenance: object,
    artifact: Path | str,
    *,
    allow_untrusted: bool = False,
) -> ProvenanceCheck:
    """Validate a derived artifact without erasing distrust in its source."""
    if not isinstance(provenance, dict):
        return check_producer(
            None, artifact, allow_untrusted=allow_untrusted
        )

    producer_check = check_producer(
        provenance.get("producer"),
        artifact,
        allow_untrusted=allow_untrusted,
        unchanged_paths=TRUST_FLOOR["index"],
    )
    source_check = check_producer(
        provenance.get("source"),
        f"{artifact} source manifest",
        allow_untrusted=allow_untrusted,
        unchanged_paths=TRUST_FLOOR["extraction"],
    )
    inherited = provenance.get("untrusted_reasons")
    reasons: list[str] = []
    if not isinstance(inherited, list):
        reasons.append("has no provenance trust record")
    else:
        reasons.extend(str(reason) for reason in inherited if reason)
    if reasons:
        message = f"untrusted artifact {artifact}: " + "; ".join(reasons)
        if not allow_untrusted:
            raise UntrustedProvenance(message)
        _trace(message)
    return ProvenanceCheck(
        producer_check.producer,
        producer_check.reasons + source_check.reasons + tuple(reasons),
    )
