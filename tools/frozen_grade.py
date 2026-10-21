"""Per-approval terminal grades and bounded historical adoption. ADR 0346.

The retained approval revision is the authority. Source drift is reported,
never regraded. Adoption reads retained evidence without asserting its quality.
"""
from __future__ import annotations

from discussion_artifact import read_posted_reading_file

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import subprocess
import tempfile
from run_record_reader import (read_tool_record, frozen_record, state_record,
                               locked_record, UnreadableRecord, fault_report,
                               DamagedRecord, damaged_record_result)

RECORD = "frozen-grades.json"
DECLARED_LIMITS = (
    "Existing unreadable bookkeeping refuses all reads and writes through the shared record reader; freeze and adoption replacement hold the exclusive artifact lock.",
    "A freeze records a successful public terminal command; it cannot establish the truth of reader judgments.",
    "Adoption checks retained readback and review existence, not their quality, and labels that exemption.",
    "Offset-free posting times are compared at their latest possible UTC instant; ambiguous same-day postings remain unfrozen.",
    "Source comparisons cannot detect a change subsequently reverted to identical bytes.",
)


def _read(path: Path) -> dict:
    return read_tool_record(path, frozen_record if path.name == RECORD else state_record) or {}


def _write(run: Path, value: dict) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=run, delete=False) as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, run / RECORD)


def approved(run: Path, submission: str) -> tuple[str, dict] | None:
    from run_status_stop_hook import approvals
    matches = [(spec.skill, item) for spec, item in approvals(run)
               if item.get("submission") == submission]
    return matches[0] if len(matches) == 1 else None


def _sources(skill: str, item: dict) -> tuple[Path, ...]:
    if skill == "course-assignment":
        # Carriers are part of the approved population, including attachments.
        artifact = Path(item["artifact_path"])
        carriers = item.get("approved_carriers", [])
        return tuple(artifact.parent / row["filename"] for row in carriers) or (artifact,)
    return tuple(Path(path) for path in item["sources"])


def _fingerprints(skill: str, item: dict, *, approved: bool = False) -> dict:
    import file_digest
    from approval_record import source_sha256
    paths = _sources(skill, item)
    if skill == "course-assignment":
        stored = {row["filename"]: row["sha256"] for row in item.get("approved_carriers", [])}
        values = {}
        for path in paths:
            try:
                values[str(path)] = stored.get(path.name, item.get("sha256")) if approved else file_digest.sha256(path)
            except OSError:
                values[str(path)] = None
        return values
    try:
        if not approved and item.get("clinical_manifest_binding") is True:
            from approval_record import _bound_sources
            _bound_sources(Path(item["sources"][0]).parent, skill, paths)
        digest = item.get("sha256") if approved else source_sha256(paths)
    except UnreadableRecord:
        raise
    except (OSError, ValueError):
        digest = None
    return {"paths": [str(path) for path in paths], "sha256": digest}


def freeze(run: Path, skill: str, item: dict, *, adoption: bool = False) -> None:
    revision = item.get("approval_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        return
    with locked_record(run / RECORD):
        payload = _read(run / RECORD)
        items = payload.setdefault("items", {})
        key = skill + ":" + item["submission"]
        existing = items.get(key)
        if isinstance(existing, dict) and existing.get("approval_revision") == revision:
            return
        items[key] = dict(approval_revision=revision,
                          frozen_at=datetime.now(timezone.utc).isoformat(),
                          kind="frozen at adoption, never graded clean" if adoption else "graded clean",
                          sources=_fingerprints(skill, item, approved=True))
        payload["version"] = 1
        _write(run, payload)


def report(run: Path, submission: str, *, adopt_history: bool = True) -> str | None:
    """An unreadable retained grade establishes no exemption in a captured command."""
    from run_record_reader import collecting_errors
    try:
        return _report(run, submission, adopt_history=adopt_history)
    except DamagedRecord as failure:
        if not collecting_errors():
            raise
        damaged_record_result(failure, check="historical adoption", artifact=submission, force=True)
        # Existing retained grades remain authoritative; damaged evidence
        # cannot establish a new adoption, nor abort independent fresh checks.
        return _report(run, submission, adopt_history=False)
    except UnreadableRecord:
        if not collecting_errors():
            raise
        return None


def _report(run: Path, submission: str, *, adopt_history: bool = True) -> str | None:
    if adopt_history:
        retained = _report(run, submission, adopt_history=False)
        if retained is not None:
            return retained
        adopt(run)
    approval = approved(run, submission)
    if approval is None:
        return None
    skill, item = approval
    row = _read(run / RECORD).get("items", {}).get(skill + ":" + submission)
    if (not isinstance(row, dict) or row.get("approval_revision") != item.get("approval_revision")
            or row.get("kind") not in {"graded clean", "frozen at adoption, never graded clean"}
            or not isinstance(row.get("frozen_at"), str) or not isinstance(row.get("sources"), dict)):
        return None
    changed = row["sources"] != _fingerprints(skill, item)
    return (f"{submission}: frozen {row['frozen_at'][:10]} ({row['kind']})"
            + ("; note - approved source changed or unreadable" if changed else ""))


def landing_time() -> float:
    """The first-parent commit introducing this build in the active checkout."""
    try:
        result = subprocess.run(["git", "log", "--first-parent", "--diff-filter=A", "--format=%ct",
                                 "--", "tools/frozen_grade.py"],
                                cwd=Path(__file__).resolve().parent.parent,
                                capture_output=True, text=True, encoding="utf-8", errors="replace", check=True, timeout=10)
        return float(result.stdout.splitlines()[0] if result.stdout.strip() else "")
    except (OSError, ValueError, subprocess.SubprocessError):
        # Before the build's first commit there is no historical adoption date.
        return 1791816825.0  # 2026-10-12 14:53:45 UTC, build started


@dataclass(frozen=True)
class Adoption:
    clean: int = 0
    adopted: int = 0
    lines: tuple[str, ...] = ()


def adopt(run: Path) -> Adoption:
    from run_status_stop_hook import approvals, STATE_RECORD
    from aar_scan import review_path
    payload = _read(run / RECORD)
    if payload.get("adoption_done"):
        return Adoption()
    population = approvals(run)
    if not population:
        return Adoption()
    boundary = landing_time()
    state = _read(run / STATE_RECORD)
    try:
        covered = json.loads(state.get("approval_revision", "[]")) if state.get("status") == "complete" else []
    except (TypeError, ValueError):
        covered = []
    try:
        readings = {reading.artifact: reading for reading in read_posted_reading_file(
            run / "reread.md", collect=False, force=True,
            artifacts=tuple(item["submission"] for _spec, item in population))}
    except UnreadableRecord:
        raise
    except (OSError, UnicodeError, ValueError):
        readings = {}
    clean = adopted = 0
    lines = []
    for spec, item in population:
        timestamp = item.get("recorded_at", item.get("reply_matched_at"))
        if isinstance(timestamp, (int, float)) and timestamp >= boundary:
            continue
        key, revision = item["submission"], item.get("approval_revision")
        graded = [spec.skill, key, revision] in covered
        posted = item.get("posting_route") in {"agent", "clinician"} or item.get("upload_route") in {"agent", "clinician"}
        retained = key in readings and review_path(run, key).is_file()
        posted_before = key in readings and _posted_before(readings[key].posted, boundary)
        if graded or posted and retained and posted_before:
            freeze(run, spec.skill, item, adoption=not graded)
            clean += graded
            adopted += not graded
            lines.append(report(run, key, adopt_history=False) or key)
    with locked_record(run / RECORD):
        payload = _read(run / RECORD)
        payload.setdefault("items", {})
        payload["adoption_done"] = True
        payload["adoption_counts"] = dict(graded_clean=clean, never_graded_clean=adopted)
        _write(run, payload)
    return Adoption(clean, adopted, tuple(lines))


def _posted_before(value: str, boundary: float) -> bool:
    """Only historical posting evidence can receive the adoption exemption.

    A portal time without an offset is compared at its latest possible UTC
    instant (UTC-12); a date-only value includes the whole day. This avoids
    assuming the machine's current zone after an account moves.
    """
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if len(value.strip()) == 10:
            timestamp += timedelta(days=1)
    except ValueError:
        try:
            timestamp = datetime.strptime(value, "%m/%d/%Y %H:%M")
        except ValueError:
            return False
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc) + timedelta(hours=12)
    return timestamp.timestamp() < boundary


def command_result(run: Path, submission: str, status: int) -> None:
    if status != 0:
        return
    for key in submission.split(","):
        approval = approved(run, key.strip())
        if approval is not None:
            freeze(run, *approval)


def all_reports(run: Path, submission: str | None) -> str | None:
    if submission is None:
        return None
    keys = tuple(key.strip() for key in submission.split(",") if key.strip())
    lines = tuple(report(run, key) for key in keys)
    return "\n".join(lines) if lines and all(line is not None for line in lines) else None


def main(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    args = parser.parse_args(argv)
    clean = adopted = 0
    damaged = False
    for path in args.runs:
        runs = (path,) if path.name != "runs" else tuple(p for p in path.iterdir() if p.is_dir())
        for run in runs:
            try:
                result = adopt(run)
            except DamagedRecord as failure:
                print(damaged_record_result(failure, check="historical adoption", force=True)[1])
                damaged = True
                continue
            except UnreadableRecord as failure:
                print(fault_report(failure, check="frozen grade"))
                from run_grader import format_unread_remainder
                print(format_unread_remainder(1))
                return 2
            clean += result.clean
            adopted += result.adopted
            for line in result.lines:
                print(line)
    print(f"adoption: graded clean {clean}; frozen at adoption, never graded clean {adopted}")
    return 1 if damaged else 0


if __name__ == "__main__":
    import sys
    from console_codec import use_utf8, require_python_floor
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
