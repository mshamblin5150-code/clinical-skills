"""Grade the pre-draft recorded-image choice without making the fit judgment."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path
import re
from typing import Mapping, TypeVar, TYPE_CHECKING

import completion_checks
import run_grader
from console_codec import require_python_floor, use_utf8
from run_record_reader import DamagedRecord, damaged_record_result, read_handwritten_record
from voice_model_observation import ModelObservation, observe

if TYPE_CHECKING:
    import voice_read

TScan = TypeVar("TScan")


RECORD_NAME = "recorded-image-match.json"
EXPECTED_ROW = "recorded image match"
CHECK = "recorded_image_match:completion_gate"
DECLARED_LIMITS = (
    ("fit is a reader judgment", "The match row checks a recorded point and exact whitespace-normalized whole image membership, not whether the image fits the point or whether the reason none fits is persuasive."),
    ("before-prose order", "The pre-draft command reads the match before drafting when invoked at the skill's stated step; a later record cannot prove retrospectively that the check preceded the first prose."),
    ("model read population", "The canonical model is one unread member even when multiple imagery consumers cannot read it; transcript observations remain a separate population."),
    ("absence-banner limitation", "Only the existing absent-model banner identifies the named unmodeled drafting door; an unreadable or unrecognized model inventory is not that door, and neither state establishes a mechanically verified match."),
)


@dataclass(frozen=True)
class Match:
    central_point: str
    image: str | None
    reason: str


@dataclass(frozen=True)
class CompletionGate:
    finding: bool
    coverage: bool
    report: str
    model_unread: int = 0
    model_absent: bool = False
    record_unread: int = 0


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def active_for_artifact(check: str, artifact: str) -> bool:
    """An unknown key never inherits an older global or sibling approval."""
    moment = completion_checks.ITEM_MOMENTS.get().get(artifact)
    return True if moment is None else completion_checks.active(check, moment)


def read_match(run: Path, artifact: str, *, force: bool = False) -> Match | None:
    """Check the shared handwritten record before interpreting one keyed choice."""
    try:
        value = read_handwritten_record(run / RECORD_NAME, "json").require_json(artifact=artifact, force=force)
    except FileNotFoundError:
        return None
    if not isinstance(value, dict) or set(value) != {"matches"} or not isinstance(value["matches"], dict):
        raise ValueError("match record needs a matches object")
    entry = value["matches"].get(artifact)
    if entry is None:
        return None
    if not isinstance(entry, dict) or set(entry) != {"central_point", "image", "reason"}:
        raise ValueError("match needs central_point, image and reason")
    if not isinstance(entry["central_point"], str) or not entry["central_point"].strip():
        raise ValueError("match needs a nonempty central point")
    if not isinstance(entry["reason"], str) or (entry["image"] is None and not entry["reason"].strip()):
        raise ValueError("a no-image match needs a reason")
    if entry["image"] is not None and (not isinstance(entry["image"], str) or not entry["image"].strip()):
        raise ValueError("image must be whole text or null")
    return Match(entry["central_point"], entry["image"], entry["reason"])


def completion_gate(
    run: Path,
    artifacts: Mapping[str, str] | None,
    *,
    model: ModelObservation | None = None,
    before_drafting: bool = False,
) -> CompletionGate:
    """Continue other keyed records after damage; count the model only once."""
    if artifacts is None:
        return CompletionGate(False, False, f"{EXPECTED_ROW}: not graded - --submission was not supplied")
    import frozen_grade
    if not before_drafting:
        frozen = frozen_grade.all_reports(run, ",".join(artifacts))
        if frozen is not None:
            return CompletionGate(False, False, frozen)
    active = tuple(key for key in artifacts if before_drafting or (
        frozen_grade.all_reports(run, key) is None and active_for_artifact(CHECK, key)))
    if not active:
        return CompletionGate(False, False, f"{EXPECTED_ROW}: not graded - approval predates check")
    observation = model if model is not None else observe()
    findings: list[str] = []
    reports: list[str] = []
    coverage = bool(observation.unread)
    read = 0
    record_unread = 0
    for key in active:
        try:
            match = read_match(run, key, force=before_drafting)
        except DamagedRecord as failure:
            failed, report = damaged_record_result(failure, check=EXPECTED_ROW, artifact=key, force=before_drafting)
            if failed:
                findings.append("damaged match record")
            reports.append(report)
            continue
        except (ValueError, UnicodeError):
            findings.append("match record is invalid")
            continue
        except OSError:
            reports.append("the match record: not graded - could not be opened")
            coverage = True
            record_unread = 1
            continue
        if match is None:
            findings.append("match record is missing")
            continue
        read += 1
        if match.image is not None:
            if observation.unread == 0 and normalized(match.image) not in {normalized(image) for image in observation.imagery.images}:
                findings.append("matched image is absent from canonical recorded imagery")
            if not before_drafting and normalized(match.image) not in normalized(artifacts[key]):
                findings.append("matched image is absent from the finished artifact")
    if observation.absent:
        import voice_model_scan
        reports.append(voice_model_scan.absent_model_banner(observation.path))
    elif observation.unread:
        reports.append("canonical recorded imagery: not graded - model imagery unreadable")
    if observation.unread:
        reports.append("unread canonical voice models: 1")
    if observation.text is None or observation.imagery.missing:
        reports.append("recorded imagery: not measured - inventory unavailable or format incomplete")
    else:
        reports.append(f"recorded imagery: candidates {observation.imagery.candidates}; read {observation.imagery.read}; unread {observation.imagery.unread}")
    if record_unread:
        reports.append("unread recorded-image match records: 1")
    detail = "; finding - " + "; ".join(dict.fromkeys(findings)) if findings else ""
    report = f"{EXPECTED_ROW}: read {read} of {len(active)} match records{detail}"
    return CompletionGate(bool(findings), coverage, "\n".join((report, *dict.fromkeys(reports))), observation.unread, observation.absent, record_unread)


def apply_coursework_gates(
    grade: run_grader.Grade[TScan], run: Path, submission: str | None,
    surface: voice_read.DraftSurface | Mapping[str, voice_read.DraftSurface], artifacts: Mapping[str, str], *,
    partial: bool = False, known_artifacts: set[str] | frozenset[str] | None = None,
    voice_coverage_limb: str | None = None, imagery_coverage_limb: str | None = None,
) -> run_grader.Grade[TScan]:
    """Compose the three readers and union their one canonical-model member."""
    import imagery_proposals
    import voice_read
    import frozen_grade
    if submission is not None and frozen_grade.all_reports(run, submission) is not None:
        # Existing frozen gates retain their own reports and bypass every new read.
        grade = voice_read.apply_completion_gate(grade, run, submission, surface,
            coverage_limb=voice_coverage_limb)
        return imagery_proposals.apply_completion_gate(grade, run, artifacts,
            partial=partial, known_artifacts=known_artifacts, terminal=True,
            coverage_limb=imagery_coverage_limb)
    model = observe() if submission is not None else None
    proposal = imagery_proposals.completion_gate(run, artifacts, partial=partial,
        known_artifacts=known_artifacts, terminal=submission is not None, model=model)
    grade = voice_read.apply_completion_gate(grade, run, submission, surface,
        model=model, approved_points=proposal.approved_points, coverage_limb=voice_coverage_limb)
    grade = imagery_proposals.apply_completion_gate(grade, run, artifacts, partial=partial,
        known_artifacts=known_artifacts, terminal=submission is not None,
        model=model, result=proposal, coverage_limb=imagery_coverage_limb)
    matched = completion_gate(run, artifacts if submission is not None else None, model=model)
    unread = max(matched.model_unread, proposal.model_unread,
                 int(model is not None and model.text is None))
    counts = {}
    if hasattr(grade.scan, "model_unread"):
        counts["model_unread"] = unread
    if hasattr(grade.scan, "image_match_unread"):
        counts["image_match_unread"] = matched.record_unread
    scan = replace(grade.scan, **counts) if counts else grade.scan
    limbs = grade.coverage_limbs
    if matched.coverage and imagery_coverage_limb is not None:
        limbs += (imagery_coverage_limb,)
    return replace(grade, scan=scan, findings_failed=grade.findings_failed or matched.finding,
        coverage_failed=grade.coverage_failed or matched.coverage, coverage_limbs=limbs,
        reports=grade.reports + (matched.report,))


def main(argv: list[str] | None = None) -> int:
    use_utf8()
    require_python_floor()
    parser = argparse.ArgumentParser(description="Check a keyed recorded-image match before the first prose.")
    parser.add_argument("run", type=Path)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args(argv)
    result = completion_gate(args.run, {args.artifact: ""}, before_drafting=True)
    print(result.report)
    print(run_grader.format_unread_remainder(result.model_unread + result.record_unread))
    return 1 if result.finding else 2 if result.coverage else 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
