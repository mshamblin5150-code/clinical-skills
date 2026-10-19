r"""Check that .claude/skills/ mirrors skills/ by link, and repair it when it does not.

`.claude/skills/` is how Claude Code loads this repo's skills natively. README.md
tells you to make each entry a **junction** to the canonical `skills/<name>/`, so
the mirror cannot hold a different answer than the skill does. That directory is
gitignored, so nothing about it is checked by anything git does.

**A junction that becomes a copy is the failure this exists for.** It reads exactly
like a working install -- same names, same files, same frontmatter -- and it answers
questions with whatever the skill said on the day the copy was made. An agent that
opens `.claude/skills/clinical-note/SKILL.md` instead of `skills/clinical-note/SKILL.md`
follows retired rules and has no way to notice. That is not hypothetical: it is how
this file came to exist. `git worktree` materialized `.claude/` by copying it, the
copy followed the junctions instead of recreating them, and the resulting worktree
carried the exact paragraph issue #23 had been filed to remove.

**Resolution, not readlink, is the test.** `os.path.islink` is False for a Windows
junction, and `os.path.isjunction` only exists on 3.12+. `os.path.realpath` resolves
junctions, symlinks and plain directories alike on every platform, so a mirror entry
is correct when it resolves to the same real path as the canonical skill and wrong
otherwise. Nothing here needs to know which link flavor made it.

**A copy that currently matches is still reported.** It is right by luck and by luck
only until the next edit to `skills/`; `identical` and `stale` differ in how much time
is left, not in whether the wiring is broken.

**A difference in line endings alone is named rather than normalized away.** `filecmp`
is byte-exact, so a mirror copy made before anything rewrote a skill file with `\n`
reads `copy-stale` on carriage returns and nothing else -- and `copy-stale` is the word
this repo cites as evidence that an agent has *already* followed a retired rule. #93's
one citable instance is in a worktree that is gone, so it can no longer be told apart
from three carriage returns, which is the cost. Normalizing the comparison was declined:
a copy that differs on disk is still a copy, and a byte check is the thing that cannot
be argued with. **So the comparison is untouched and every differing file carries its
reason** -- `content` or `line endings only` -- with both counts printed on every run,
whether or not each fired.

**`_normalized` is where the rule that decides the word lives**, and it is the only
authoritative statement of it -- every other one in the tree, this paragraph included,
describes that line. A file the copy does not hold at all counts as content, because it
is not carriage returns, which is the whole question the split answers; and the partition
is two-way so the two counts sum to the total, which is the one thing a reader checks the
summary line against.

**Output is paths and status words only.** It reads `skills/` and `.claude/skills/`,
neither of which may contain PHI under standing rule 1, and it never prints file
contents. The reason beside a differing file is one of two fixed strings held here
rather than anything read out of the file. Its output is safe to paste into a ticket,
like `corpus_census.py` and unlike `harvest_review.py`.

**Session start repairs before a skill is invoked.** The main-session hook records the
full pre-repair report under `.claude/skills-mirror-reports/`, moves mirror-only files
under `.claude/skills-orphaned/<name>/<UTC stamp>/`, and then relinks the entry. A
subagent payload returns without inspecting or writing because its parent already owns
the repair. Its context also reports the checkout's base distance from the cached
`origin/main`, including the derived run-relevant subset and when that ref last moved.
The Base distance read remains local and advisory. Worktree starts additionally refresh
the main checkout and compare its served files; neither changes the hook's status.
Hook output is JSON carrying `hookSpecificOutput.additionalContext`; plain stdout text
does not reach the model.

What a clean run does not establish belongs to ``skills_mirror.NOT_REACHED`` below.
This docstring points at that object and deliberately copies none of its rows.
"""

from __future__ import annotations

import argparse
import datetime
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable, NamedTuple

import git_paths
from console_codec import require_python_floor, use_utf8
from repo_root import checkout_git_dir, enclosing_checkout
from tree_walk import is_link as _is_link

MIRROR = Path(".claude") / "skills"
CANONICAL = Path("skills")

# A directory under skills/ is mirrored when it carries a SKILL.md or when this
# explicit set names shared instruction that has no owning skill. Skill names stay
# discovered from their files; the exception is named because widening to every
# directory would silently make a future non-instruction directory loadable.
SKILL_FILE = "SKILL.md"
SHARED_INSTRUCTION_DIRECTORIES = {"_shared"}

LINKED = "linked"
MISSING = "missing"
IDENTICAL = "copy-identical"
STALE = "copy-stale"
FOREIGN = "linked-elsewhere"
NOT_A_DIR = "not-a-directory"
TRACKED_SKILL_MISSING = "tracked-skill-missing"

# Everything except LINKED is a finding. MISSING is the mildest -- the skill simply
# does not load -- and STALE is the one that answers questions wrongly.
OK_STATUSES = {LINKED}

# Why a file under a STALE copy differs. Two values and no third, so the counts in
# the report sum to the number of differing files. #198.
CONTENT = "content"
LINE_ENDINGS = "line endings only"
REPORTS = Path(".claude") / "skills-mirror-reports"
ORPHANS = Path(".claude") / "skills-orphaned"
NO_SKILLS = "no skills found under skills/"
POPULATION_NOT_READ = (
    "skills mirror: DID NOT INSPECT -- tracked skill population read failed"
)
UNSUPPRESSED_LINES = (
    "empty-population",
    "population-not-read",
    "broken-mirror",
    "repair-failure",
    "session-start-artifact",
)
TOOL_PATH = re.compile(r"(?<![A-Za-z0-9_])tools/([A-Za-z0-9_]+\.py)")


def _quiet_keeps(name: str) -> bool:
    return name in UNSUPPRESSED_LINES

NOT_REACHED = (
    (
        "link traversal in the copy-stale comparison",
        "The comparison enters junctions deliberately and surfaces a dangling one "
        "as a difference; an ancestor junction can prevent termination.",
    ),
    (
        "a sibling checkout's mirror",
        "Ordinary inspection is confined to the selected checkout. Session start "
        "also reads the main checkout's served mirror, never other sibling mirrors.",
    ),
    (
        "the state after another worktree is materialized",
        "The result is a momentary reading, and a later worktree creation can replace "
        "junctions with copies without this invocation observing it.",
    ),
    (
        "a CI representation of the local mirror",
        "The mirror is gitignored, so a repository runner has no tracked installation "
        "state to inspect.",
    ),
    (
        "wiring when the skill population is empty",
        "Exit 2 establishes only that no skill entry was found under the selected "
        "root; it establishes no link or copy status.",
    ),
    (
        "a verdict from session-start status",
        "Session start remains advisory and returns success so its structured context "
        "can be consumed.",
    ),
    (
        "that a checkout is current",
        "Base distance reads the cached origin/main without fetching; a zero means "
        "only that the local copy names no newer commit.",
    ),
    (
        "the complete set of files a clinical run reads",
        "The run-relevant path set reaches named tool modules and the declared roots, "
        "not files reached through an unnamed import or another indirect path.",
    ),
    (
        "instruction files Git ignores",
        "The run-relevant citation read opens only files Git lists under skills, "
        "tracked or new but not ignored; an ignored instruction contributes no citation.",
    ),
    (
        "citations whose letters are not single UTF-8 bytes",
        "Replacement decoding reports invalid UTF-8 files but cannot recover tool "
        "citations from UTF-16 or other encodings whose ASCII letters span bytes.",
    ),
    (
        "when origin/main was last checked",
        "The timestamp comes from the cached ref's last movement; a fetch that found "
        "nothing records no movement.",
    ),
    (
        "the state of the issue tracker",
        "Commit distance reads repository refs only and does not inspect tracker "
        "records that may have changed independently.",
    ),
    (
        "link traversal in the session-start comparison",
        "The comparison deliberately enters the main mirror's junctions through "
        "_differing_files; dangling served files differ, and an ancestor loop may not terminate.",
    ),
    (
        "skill edits after the startup snapshot",
        "The file comparison cannot observe an edit followed by an invocation later in the session.",
    ),
    (
        "the current session's loaded skill text",
        "The 2026-10-19 CLI trials returned different live-edit outcomes; desktop reload "
        "was not driven. Refreshes promise the next session, not reliable current-session replacement.",
    ),
    (
        "another agent on a clean main checkout",
        "The fast-forward can move files beneath that agent; guards see tracked edits only. "
        "They do not lock out concurrent checkout changes after the guard read.",
    ),
    (
        "Claude Code configuration and worktree creation behavior",
        "Desktop and bridged source premises are the dated ADR 0426/0429 measurements. "
        "Terminal-created sessions, the unexplained /aar route, bridge creation timing, "
        "and changes to Claude Code's configuration loading are not verified here.",
    ),
    (
        "a bridged session's branch-specific skill text",
        "The report redirects differences but does not make the bridge's skill folder exist earlier.",
    ),
)


class Difference(NamedTuple):
    """One file the copy gets wrong, and which of the two ways it gets it wrong.

    A plain pair would compare and sort identically; naming the fields is what stops
    `differs` reading as a list of paths at the one signature a reader checks.
    """

    rel: str
    reason: str


class FileComparison(NamedTuple):
    differs: list[Difference]
    extra: list[str]
    population: int


class MainRefresh(NamedTuple):
    summary: str
    changed: int | None


class RepairResult(NamedTuple):
    repaired: int
    drained: list[Path]
    failures: list[str]


class RunRelevantPaths(NamedTuple):
    paths: list[str]
    read_with_replacement: int
    unopenable: int


class BaseDistance(NamedTuple):
    branch: str
    behind: int
    ahead: int
    run_behind: int
    run_ahead: int
    moved_at: datetime.datetime
    read_with_replacement: int = 0
    unopenable: int = 0


class BaseReadFailed(Exception):
    def __init__(
        self,
        label: str,
        branch: str = "<branch>",
        moved_at: datetime.datetime | None = None,
    ):
        super().__init__(label)
        self.label = label
        self.branch = branch
        self.moved_at = moved_at


def _normalized(data: bytes) -> bytes:
    r"""`\r\n` -> `\n`, and nothing else. **This function is the rule.**

    Deliberately not *strip every* `\r`, so a lone carriage return sitting inside
    content stays a content difference -- under-claiming that a difference is
    harmless is the safe direction. Every other statement of this in the tree is a
    description of this line and none of them is authoritative.
    """
    return data.replace(b"\r\n", b"\n")


def difference_reason(canonical_file: Path, mirror_file: Path) -> str | None:
    """CONTENT, LINE_ENDINGS, or None when the two files are byte-identical.

    The byte comparison comes first and decides *whether* they differ. Normalization
    only ever names a difference the byte check has already found, which is what
    keeps `copy-stale` byte-exact.
    """
    if not canonical_file.is_file() or not mirror_file.is_file():
        return CONTENT
    if filecmp.cmp(canonical_file, mirror_file, shallow=False):
        return None
    if _normalized(canonical_file.read_bytes()) == _normalized(mirror_file.read_bytes()):
        return LINE_ENDINGS
    return CONTENT


def repo_root() -> Path:
    """The checkout this script belongs to -- worktree root, not the main checkout.

    ``tools/`` sits one level under that root. A worktree is a different checkout
    than the one it was branched from, and resolving from this module keeps the
    answer local without consulting redirectable process state.
    """
    return Path(__file__).resolve().parent.parent


def run_relevant_paths(root: Path) -> RunRelevantPaths:
    """Read tracked and untracked, unignored instructions and report unread files.

    A clean read covers that Git-listed population, including not-yet-staged
    drafts; ignored instructions contribute no citations.
    """
    try:
        listed = git_paths.read_path_records(
            root, "ls-files", "--cached", "--others", "--exclude-standard", "-z",
            "--", "skills",
        )
    except git_paths.GitPathError as exc:
        raise BaseReadFailed("run-relevant path-set") from exc
    prose = {"AGENTS.md", *listed}
    cited_tools = set()
    replaced = unopenable = 0
    for relative in sorted(prose):
        try:
            data = (root / relative).read_bytes()
        except OSError:
            unopenable += 1
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
            replaced += 1
        for name in TOOL_PATH.findall(text):
            if not name.startswith("test_"):
                cited_tools.add(f"tools/{name}")

    return RunRelevantPaths(
        sorted({"AGENTS.md", "reference", "skills", *cited_tools}), replaced, unopenable,
    )


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()


def _distance_pair(value: str) -> tuple[int, int]:
    left, right = value.split()
    return int(left), int(right)


def _git_read(root: Path, label: str, *arguments: str) -> str:
    try:
        return _git(root, *arguments)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BaseReadFailed(label) from exc


def checkout_label(root: Path) -> str:
    """Branch name from the checkout's HEAD file, or a detached commit label."""
    try:
        git_dir = checkout_git_dir(root)
        if git_dir is None:
            raise ValueError("no enclosing checkout")
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    except (OSError, ValueError) as exc:
        raise BaseReadFailed("branch-name") from exc

    prefix = "ref: refs/heads/"
    if head.startswith(prefix):
        return head.removeprefix(prefix)
    if re.fullmatch(r"[0-9a-fA-F]{40,64}", head):
        return f"detached@{head[:12]}"
    raise BaseReadFailed("branch-name")


def read_base_distance(root: Path) -> BaseDistance:
    branch_failure = None
    try:
        branch = checkout_label(root)
    except BaseReadFailed as exc:
        branch = exc.branch
        branch_failure = exc
    try:
        moved = _git_read(
            root,
            "origin/main movement-time",
            "log",
            "-g",
            "-1",
            "--date=iso-strict",
            "--format=%gD",
            "refs/remotes/origin/main",
        )
        match = re.search(r"@\{(.+)\}$", moved)
        if match is None:
            raise ValueError("no dated reflog selector")
        moved_at = datetime.datetime.fromisoformat(
            match.group(1).replace("Z", "+00:00")
        )
    except BaseReadFailed as exc:
        if branch_failure is not None:
            raise BaseReadFailed(
                f"{branch_failure.label} and {exc.label}", branch
            ) from exc
        raise BaseReadFailed(exc.label, branch) from exc
    except ValueError as exc:
        raise BaseReadFailed("origin/main movement-time", branch) from exc
    if branch_failure is not None:
        raise BaseReadFailed(branch_failure.label, branch, moved_at)
    try:
        behind, ahead = _distance_pair(
            _git_read(
                root,
                "raw distance",
                "rev-list",
                "--left-right",
                "--count",
                "origin/main...HEAD",
            )
        )
    except BaseReadFailed as exc:
        raise BaseReadFailed(exc.label, branch, moved_at) from exc
    except ValueError as exc:
        raise BaseReadFailed("raw distance", branch, moved_at) from exc
    try:
        relevant_paths = run_relevant_paths(root)
    except (BaseReadFailed, OSError, UnicodeError) as exc:
        raise BaseReadFailed(
            "run-relevant path-set", branch, moved_at
        ) from exc
    try:
        run_behind, run_ahead = _distance_pair(
            _git_read(
                root,
                "run-relevant distance",
                "rev-list",
                "--left-right",
                "--count",
                "origin/main...HEAD",
                "--",
                *relevant_paths.paths,
            )
        )
    except BaseReadFailed as exc:
        raise BaseReadFailed(exc.label, branch, moved_at) from exc
    except ValueError as exc:
        raise BaseReadFailed("run-relevant distance", branch, moved_at) from exc
    return BaseDistance(
        branch,
        behind,
        ahead,
        run_behind,
        run_ahead,
        moved_at,
        relevant_paths.read_with_replacement,
        relevant_paths.unopenable,
    )


def _age_words(then: datetime.datetime, now: datetime.datetime) -> str:
    seconds = max(0, int((now - then).total_seconds()))
    if seconds < 60:
        return "less than a minute ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


def _commits(value: int) -> str:
    return f"{value} commit{'s' if value != 1 else ''}"


def _run_changes(value: int) -> str:
    verb = "changes" if value == 1 else "change"
    return f"{value} {verb} what a clinical run reads"


def _render_base_distances(reading: BaseDistance, now: datetime.datetime) -> str:
    age = _age_words(reading.moved_at, now)
    if reading.ahead:
        lines = [
            f"base: {reading.branch} -- carrying at most {_commits(reading.ahead)} "
            "not in origin/main",
            f"      ({_run_changes(reading.run_ahead)})",
        ]
        if reading.behind:
            lines[-1] += f", and at least {_commits(reading.behind)} behind it"
            lines.append(
                f"      ({_run_changes(reading.run_behind)}); "
                f"origin/main last moved {age}"
            )
        else:
            lines[-1] += f"; origin/main last moved {age}"
        return "\n".join(lines)
    if reading.behind:
        return (
            f"base: {reading.branch} -- at least {_commits(reading.behind)} "
            "behind origin/main\n"
            f"      ({_run_changes(reading.run_behind)}); "
            f"origin/main last moved {age}"
        )
    return (
        f"base: {reading.branch} -- no newer commit known;\n"
        f"      origin/main last moved {age}"
    )


def render_base_distance(reading: BaseDistance, now: datetime.datetime) -> str:
    line = _render_base_distances(reading, now)
    counts = []
    if reading.read_with_replacement:
        counts.append(f"{reading.read_with_replacement} file(s) read with replacement")
    if reading.unopenable:
        counts.append(f"{reading.unopenable} file(s) could not be opened")
    if counts:
        line += "; " + "; ".join(counts)
    return line


def base_context(root: Path) -> str:
    try:
        return render_base_distance(read_base_distance(root), utc_now())
    except BaseReadFailed as exc:
        context = (
            f"base: {exc.branch} -- NOT ESTABLISHED: {exc.label} read failed"
        )
        if exc.moved_at is not None:
            context += (
                f"; origin/main last moved {_age_words(exc.moved_at, utc_now())}"
            )
        return context


def tracked_skill_names(root: Path) -> set[str]:
    """Skill directories whose ``SKILL.md`` is present in the index.

    A non-checkout keeps the disk-only behavior used by isolated consumers and
    tests. In a checkout, the index is the independent population that lets a
    missing working-tree file remain visible to the report. A clean result means
    no tracked ``SKILL.md`` is missing; an untracked skill is outside that claim.
    """
    if enclosing_checkout(root) is None:
        return set()
    paths = git_paths.read_path_records(
        root,
        "ls-files",
        "--cached",
        "-z",
        "--",
        "skills/*/SKILL.md",
    )
    return {
        parts[1]
        for path in paths
        if len(parts := PurePosixPath(path).parts) == 3
        and parts[0] == "skills"
        and parts[2] == SKILL_FILE
    }


def disk_skill_names(root: Path) -> set[str]:
    canonical = root / CANONICAL
    return {
        p.name for p in canonical.iterdir()
        if p.is_dir()
        and (
            (p / SKILL_FILE).is_file()
            or p.name in SHARED_INSTRUCTION_DIRECTORIES
        )
    } if canonical.is_dir() else set()


def skill_population(root: Path) -> tuple[list[str], set[str]]:
    tracked = tracked_skill_names(root)
    return sorted(disk_skill_names(root) | tracked), tracked


def skill_names(root: Path) -> list[str]:
    names, _ = skill_population(root)
    return names


def _differing_files(
    canonical: Path, mirror: Path,
) -> FileComparison:
    """Differences, mirror-only files, and the union of the enumerated file paths.

    The second list is the population repair drains before relinking. A file present
    only in the copy is either someone's stray edit or work that never reached
    `skills/`, and either way it is moved rather than deleted.

    A file the mirror does not hold is CONTENT rather than a third reason -- see the
    module docstring for why the partition is two-way.
    """
    differs: list[Difference] = []
    extra: list[str] = []

    def unread(error):
        raise error

    populations = []
    for directory in (canonical, mirror):
        paths = set()
        if directory.exists():
            for parent, _, files in os.walk(directory, followlinks=True, onerror=unread):
                for filename in files:
                    path = Path(parent) / filename
                    paths.add(path.relative_to(directory).as_posix())
        populations.append(paths)
    canonical_rel, mirror_rel = populations

    for rel in sorted(canonical_rel - mirror_rel):
        differs.append(Difference(rel, CONTENT))
    for rel in sorted(mirror_rel - canonical_rel):
        extra.append(rel)
    for rel in sorted(canonical_rel & mirror_rel):
        reason = difference_reason(canonical / rel, mirror / rel)
        if reason is not None:
            differs.append(Difference(rel, reason))

    return FileComparison(sorted(differs), extra, len(canonical_rel | mirror_rel))


class Entry:
    def __init__(
        self,
        name: str,
        status: str,
        differs: Iterable[Difference] = (),
        extra: Iterable[str] = (),
        target: Path | None = None,
    ):
        self.name = name
        self.status = status
        self.differs = list(differs)
        self.extra = list(extra)
        self.target = target

    @property
    def ok(self) -> bool:
        return self.status in OK_STATUSES

    def _differs_for(self, reason: str) -> list[str]:
        return [d.rel for d in self.differs if d.reason == reason]

    @property
    def content_differs(self) -> list[str]:
        """The files a reader has to act on. This is the drift `copy-stale` means."""
        return self._differs_for(CONTENT)

    @property
    def endings_differs(self) -> list[str]:
        """The files that differ and say nothing about drift. Still a copy, still
        a finding, and not evidence that a rule was answered wrongly."""
        return self._differs_for(LINE_ENDINGS)


def inspect(root: Path) -> list[Entry]:
    entries = []
    names, tracked = skill_population(root)
    for name in names:
        canonical = (root / CANONICAL / name).resolve()
        mirror = root / MIRROR / name

        if name in tracked and not (canonical / SKILL_FILE).is_file():
            entries.append(Entry(name, TRACKED_SKILL_MISSING))
            continue

        if not mirror.exists():
            entries.append(Entry(name, MISSING))
            continue
        if not mirror.is_dir():
            entries.append(Entry(name, NOT_A_DIR))
            continue

        resolved = mirror.resolve()
        if resolved == canonical:
            entries.append(Entry(name, LINKED))
            continue

        # It resolves somewhere else. Either it is a real copy sitting inside
        # .claude/skills/, or it is a link aimed at another checkout -- a worktree
        # pointing back at the main tree reads current today and diverges the moment
        # the branch does. Both answer with the wrong file; only the repair differs.
        differs, extra, _ = _differing_files(canonical, mirror)
        if _is_link(mirror):
            entries.append(Entry(name, FOREIGN, differs, extra, target=resolved))
        else:
            status = IDENTICAL if not differs and not extra else STALE
            entries.append(Entry(name, status, differs, extra))

    return entries


def link(mirror_entry: Path, canonical: Path) -> None:
    """Point mirror_entry at canonical, using whatever this platform links with.

    Windows gets a junction rather than a symlink deliberately: `mklink /J` is what
    README documents and it needs no Developer Mode and no elevation, which a
    directory symlink does.
    """
    mirror_entry.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(mirror_entry), str(canonical)],
            check=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
    else:
        os.symlink(canonical, mirror_entry, target_is_directory=True)


def repair(
    root: Path,
    entries: list[Entry],
    stamp: str | None = None,
) -> RepairResult:
    """Drain mirror-only files, then relink every broken entry.

    Returns ``(repaired, drain_directories, failures)``. A drain is a move,
    never a deletion, and is scoped by skill name and one UTC run stamp.
    """
    repaired = 0
    drained = []
    failures = []
    run_stamp = stamp or _utc_stamp()

    for entry in entries:
        if entry.ok:
            continue
        if entry.status == TRACKED_SKILL_MISSING:
            failures.append(
                f"{entry.name}: tracked {SKILL_FILE} is missing from disk"
            )
            continue
        canonical = (root / CANONICAL / entry.name).resolve()
        mirror_entry = root / MIRROR / entry.name

        try:
            # A FOREIGN entry resolves into another checkout. Its apparent
            # extras belong to that target, not to this checkout's mirror, so
            # unlink the local junction without moving anything through it.
            if entry.extra and entry.status != FOREIGN:
                drain = root / ORPHANS / entry.name / run_stamp
                for rel in entry.extra:
                    destination = drain / rel
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(mirror_entry / rel), str(destination))
                drained.append(drain)

            if mirror_entry.exists() or _is_link(mirror_entry):
                if _is_link(mirror_entry):
                    # Removing the link, never what it points at.
                    try:
                        os.rmdir(mirror_entry)
                    except OSError:
                        os.unlink(mirror_entry)
                elif mirror_entry.is_dir():
                    shutil.rmtree(mirror_entry)
                else:
                    mirror_entry.unlink()

            link(mirror_entry, canonical)
            repaired += 1
        except (OSError, subprocess.CalledProcessError) as exc:
            failures.append(f"{entry.name}: {exc}")

    return RepairResult(repaired, drained, failures)


def render(entries: list[Entry], root: Path, verbose: bool) -> list[str]:
    if not entries:
        return [NO_SKILLS]

    lines = [f"skills mirror: {root}"]

    width = max(len(e.name) for e in entries)
    for entry in entries:
        mark = "ok  " if entry.ok else "WARN"
        detail = ""
        if entry.status == STALE:
            # Both counts on every run, whether or not each fired. A reader who has
            # learned to read one of them reads its absence as the other being zero,
            # which is checks_ledger.py's argument for naming its rows unconditionally.
            detail = (
                f" ({len(entry.differs)} file(s) differ: "
                f"{len(entry.content_differs)} {CONTENT}, "
                f"{len(entry.endings_differs)} {LINE_ENDINGS})"
            )
        elif entry.status == FOREIGN:
            detail = f" -> {entry.target}"
        elif entry.status == IDENTICAL:
            detail = " (matches today, will drift)"
        lines.append(f"  {mark} {entry.name:<{width}}  {entry.status}{detail}")
        if verbose and entry.differs:
            for difference in entry.differs:
                lines.append(
                    f"         differs ({difference.reason}): {difference.rel}"
                )
        if entry.extra:
            for rel in entry.extra:
                lines.append(f"         only in mirror: {rel}")

    broken = [e for e in entries if not e.ok]
    if broken:
        lines.append("")
        lines.append(
            f"{len(broken)} of {len(entries)} skill(s) are not linked. An agent "
            "reading the mirror may follow a retired rule."
        )
        # That sentence is what `copy-stale` is cited for, and it is the claim a
        # CRLF-only difference cannot support. The rows above already say which kind
        # each file is; this qualifies the sentence a skimming reader actually reads,
        # which is #198's stated harm rather than the row. Withdrawn by a single
        # content difference anywhere, because the sentence is about the whole report.
        found = [d for e in entries for d in e.differs]
        if found and not any(d.reason == CONTENT for d in found):
            lines.append(
                "No copy differs in content: every difference found is line endings "
                "only, which is not evidence a rule has been answered wrongly."
            )
        lines.append("Repair with: python tools/skills_mirror.py --repair")
    return lines


def _utc_stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y%m%dT%H%M%S.%fZ"
    )


def record_report(root: Path, lines: list[str], stamp: str | None = None) -> Path:
    directory = root / REPORTS
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{stamp or _utc_stamp()}.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def hook_response(context: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


def refresh_main_checkout(root: Path) -> MainRefresh:
    """Fetch within the startup budget, then move only a clean main branch."""
    try:
        subprocess.run(
            ["git", "fetch", "origin", "main"], cwd=root,
            capture_output=True, check=True, timeout=5,
        )
    except subprocess.TimeoutExpired:
        return MainRefresh("main checkout declined: fetch timed out; skill files not measured", None)
    except (OSError, subprocess.CalledProcessError):
        return MainRefresh("main checkout declined: fetch failed; skill files not measured", None)
    try:
        target = _git(root, "rev-parse", "origin/main")
        changed = len(git_paths.read_path_records(
            root, "diff", "--name-only", "-z", "HEAD", target, "--", "skills/",
        ))
        if _git(root, "rev-parse", "--abbrev-ref", "HEAD") != "main":
            reason = "not on main"
        elif _git(root, "status", "--porcelain", "--untracked-files=no"):
            reason = "tracked files have uncommitted edits"
        else:
            try:
                _git(root, "merge-base", "--is-ancestor", "HEAD", target)
            except subprocess.CalledProcessError:
                reason = "main cannot fast-forward"
            else:
                _git(root, "merge", "--ff-only", target)
                return MainRefresh(f"main checkout fast-forwarded to {target}; "
                                   f"{changed} skill file(s) changed", changed)
        return MainRefresh(f"main checkout declined: {reason}; {changed} skill file(s) differ from origin/main", changed)
    except (OSError, subprocess.CalledProcessError, git_paths.GitPathError):
        return MainRefresh("main checkout declined: Git read or fast-forward failed; skill files not measured", None)


def worktree_session_context(root: Path, payload: dict) -> tuple[Path, list[str]] | None:
    """Resolve both session kinds through cwd's common Git directory (ADRs 0426/0429)."""
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        return None
    try:
        session = Path(_git(Path(cwd), "rev-parse", "--show-toplevel")).resolve()
        common = Path(_git(session, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        git_dir = Path(_git(session, "rev-parse", "--absolute-git-dir"))
        if common.resolve() == git_dir.resolve():
            return None
        owner = common.resolve().parent
        script_common = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        if script_common.resolve() != common.resolve():
            return None
    except (OSError, subprocess.CalledProcessError):
        return None

    kind = "bridged" if root == session else "desktop"
    refreshed = refresh_main_checkout(owner)
    try:
        names = skill_names(session)
        if not names:
            raise OSError("empty skill population")
        count = 0
        population = 0
        for name in names:
            if not (session / CANONICAL / name).is_dir():
                raise OSError("unread skill directory")
            different, extra, files = _differing_files(session / CANONICAL / name, owner / MIRROR / name)
            count += len(different) + len(extra)
            population += files
        comparison = f"{count} served skill file(s) differ of {population} compared; unread remainder 0"
    except (OSError, git_paths.GitPathError):
        count = None
        comparison = "served skill files not measured"
    line = (f"Worktree skills ({kind}): {session}; served from {owner / MIRROR}; "
            f"{refreshed.summary}; {comparison}. Updates serve the next session.")
    lines = [line]
    if count or refreshed.changed:
        lines.append(
            f"WARNING: Read each skill from {session / CANONICAL}/<name>/ "
            "rather than the invocation's base directory."
        )
    return owner, lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that .claude/skills/ links to skills/, and repair it.",
    )
    parser.add_argument(
        "--repair", action="store_true",
        help="replace copies and wrong links with junctions to skills/",
    )
    parser.add_argument(
        "--session-start", action="store_true",
        help="repair at main-session start and emit Claude hook context",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="name the files that differ (paths only, never contents)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help=(
            "print nothing when every skill is linked; an empty skill population "
            "still prints its diagnostic and exits non-zero"
        ),
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="checkout to inspect (default: the one this script lives in)",
    )
    args = parser.parse_args(argv)
    if args.session_start:
        payload = json.load(sys.stdin)
        if "agent_id" in payload:
            return 0

    root = args.root.resolve() if args.root else repo_root()
    worktree_context = worktree_session_context(root, payload) if args.session_start else None
    worktree_lines = worktree_context[1] if worktree_context else []
    if worktree_context and worktree_context[0] != root:
        record_report(worktree_context[0], worktree_lines)

    try:
        entries = inspect(root)
    except git_paths.GitPathError:
        if args.session_start:
            stamp = _utc_stamp()
            record_report(root, [POPULATION_NOT_READ, *worktree_lines], stamp=stamp)
            context = f"{POPULATION_NOT_READ}\n\n{base_context(root)}"
            context = "\n".join([context, *worktree_lines])
            if _quiet_keeps("session-start-artifact"):
                print(json.dumps(hook_response(context)))
            return 0
        if _quiet_keeps("population-not-read"):
            print(POPULATION_NOT_READ, file=sys.stderr)
        return 2

    if args.session_start:
        stamp = _utc_stamp()
        report = render(entries, root, verbose=True)
        record_report(root, [*report, *worktree_lines], stamp=stamp)
        broken = [entry for entry in entries if not entry.ok]
        failures = []
        if not entries:
            context = NO_SKILLS
        elif not broken:
            context = f"skills mirror: {len(entries)} of {len(entries)} linked"
        else:
            repaired, drained, failures = repair(root, entries, stamp=stamp)
            context_lines = [*report, "", f"relinked {repaired} skill(s)."]
            context_lines.extend(
                f"DRAINED  {path.relative_to(root).as_posix()}"
                for path in drained
            )
            context_lines.extend(f"FAILED  {failure}" for failure in failures)
            context = "\n".join(context_lines)
        context = f"{context}\n\n{base_context(root)}"
        context = "\n".join([context, *worktree_lines])
        if _quiet_keeps("session-start-artifact"):
            print(json.dumps(hook_response(context)))
        # SessionStart is advisory. Returning success is what lets Claude Code
        # consume the structured failure context instead of turning a fired
        # hook back into silence.
        return 0

    if not entries:
        if _quiet_keeps("empty-population"):
            print(NO_SKILLS)
        return 2

    if args.repair:
        repaired, drained, failures = repair(root, entries)
        try:
            entries = inspect(root)
        except git_paths.GitPathError:
            if _quiet_keeps("population-not-read"):
                print(POPULATION_NOT_READ, file=sys.stderr)
            return 2
        broken = [entry for entry in entries if not entry.ok]
        if (broken and _quiet_keeps("broken-mirror")) or not args.quiet:
            for line in render(entries, root, args.verbose):
                print(line, file=sys.stderr if broken else sys.stdout)
        if not args.quiet:
            if repaired:
                print(f"\nrelinked {repaired} skill(s).")
            for path in drained:
                print(f"DRAINED  {path.relative_to(root).as_posix()}")
        if failures and _quiet_keeps("repair-failure"):
            for failure in failures:
                print(f"FAILED  {failure}", file=sys.stderr)
        return 1 if failures or broken else 0

    broken = [e for e in entries if not e.ok]
    if (broken and _quiet_keeps("broken-mirror")) or not args.quiet:
        for line in render(entries, root, args.verbose):
            print(line, file=sys.stderr if broken else sys.stdout)
    return 1 if broken else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    sys.exit(main())
