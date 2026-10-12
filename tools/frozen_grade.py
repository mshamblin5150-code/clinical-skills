"""Per-approval terminal grades and bounded historical adoption. ADR 0346.

The retained approval revision is the authority. Source drift is reported,
never regraded. Adoption reads retained evidence without asserting its quality.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile

RECORD = "frozen-grades.json"
DECLARED_LIMITS = (
    "A freeze records a successful public terminal command; it cannot establish the truth of reader judgments.",
    "Adoption checks retained readback and review existence, not their quality, and labels that exemption.",
    "Source comparisons cannot detect a change subsequently reverted to identical bytes.",
)


def _read(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, ValueError):
        return {}


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
        digest = item.get("sha256") if approved else source_sha256(paths)
    except OSError:
        digest = None
    return {"paths": [str(path) for path in paths], "sha256": digest}


def freeze(run: Path, skill: str, item: dict, *, adoption: bool = False) -> None:
    revision = item.get("approval_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        return
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
    if adopt_history:
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
                                capture_output=True, text=True, check=True, timeout=10)
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
    from discussion_artifact import read_posted_readings
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
        readings = {reading.artifact for reading in read_posted_readings(
            (run / "reread.md").read_text(encoding="utf-8"))}
    except (OSError, UnicodeError, ValueError):
        readings = set()
    clean = adopted = 0
    lines = []
    for spec, item in population:
        timestamp = item.get("recorded_at", item.get("reply_matched_at"))
        if isinstance(timestamp, (int, float)) and timestamp >= boundary:
            continue
        if timestamp is None and (run / spec.approval_record).stat().st_mtime >= boundary:
            continue
        key, revision = item["submission"], item.get("approval_revision")
        graded = [spec.skill, key, revision] in covered
        posted = item.get("posting_route") in {"agent", "clinician"} or item.get("upload_route") in {"agent", "clinician"}
        retained = key in readings and review_path(run, key).is_file()
        if graded or posted and retained:
            freeze(run, spec.skill, item, adoption=not graded)
            clean += graded
            adopted += not graded
            lines.append(report(run, key, adopt_history=False) or key)
    payload = _read(run / RECORD)
    payload["adoption_done"] = True
    payload["adoption_counts"] = dict(graded_clean=clean, never_graded_clean=adopted)
    _write(run, payload)
    return Adoption(clean, adopted, tuple(lines))


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
    for path in args.runs:
        runs = (path,) if path.name != "runs" else tuple(p for p in path.iterdir() if p.is_dir())
        for run in runs:
            result = adopt(run)
            clean += result.clean
            adopted += result.adopted
            for line in result.lines:
                print(line)
    print(f"adoption: graded clean {clean}; frozen at adoption, never graded clean {adopted}")
    return 0


if __name__ == "__main__":
    import sys
    from console_codec import use_utf8, require_python_floor
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
