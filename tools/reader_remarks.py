"""Reader remarks and the pre-ask approval receipt required by ADR 0330.

The transcript reader recognizes the same main-session messages as ADR 0318.
Free text cannot establish whether a fix resolves a remark, whether a reader
noticed every problem, or whether an affirmative reply expresses informed
consent. The caller supplies its existing content-approval decision; this module
checks explicit leave decisions and the exact surface shown before that reply.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import time
import coursework_run


SCOPED_SKILLS = frozenset({"course-assignment", "discussion-post", "discussion-reply", "peer-critique", "practicum-case-study"})
PREFIX = "READER-REMARK: "
DECLARED_LIMITS = (
    "Remarks concealed in a folded field or a substance-only reason cannot be distinguished from ordinary reader text.",
    "The transcript comparison collapses whitespace and does not prove visual presentation or clinician attention.",
    "A fixed outcome records the change shown and accepted; it does not mechanically establish that the change resolves the remark.",
    "Explicit leaves recognize leave, keep, or accept followed by remark numbers or all remarks; other wording requires a new explicit reply.",
    "The printed reply forms must appear before the reply; another question asked beside them is not detected.",
    "Coverage selection is a wording floor: gap lines outside the selector vocabulary are not selected.",
)


@dataclass(frozen=True)
class Remark:
    origin: str
    text: str


@dataclass(frozen=True)
class Outcome:
    status: str
    detail: str


class RemarkError(ValueError):
    pass


def report(remarks: tuple[Remark, ...]) -> str:
    return "\n".join(PREFIX + json.dumps({"origin": r.origin, "text": r.text}, ensure_ascii=True) for r in remarks)


def apply_readers(grade, claims, headings, artifacts: tuple[str, ...], visuals=(), *, coverage_limb=None):
    """Carry only the caller's bound records to its completion report."""
    from dataclasses import replace
    import run_grader
    records = tuple(("CLAIM", r.claim, r) for r in claims)
    records += tuple(("HEADING-READ", r.artifact, r) for r in headings if r.artifact in artifacts)
    records += tuple(("RENDERED", name, r) for r in visuals for name in (getattr(r, "deck", getattr(r, "artifact", "")),) if name in artifacts)
    remarks = tuple(Remark(f"{kind}: {name}", text) for kind, name, r in records for text in r.remarks)
    unread = sum(r.unread for _, _, r in records)
    import completion_checks
    if not completion_checks.active("reader_remarks:unread-reader-record"):
        unread = 0
    details = tuple(f"unread reader record: {kind}: {name}" for kind, name, r in records if r.unread)
    limbs = grade.coverage_limbs + ((coverage_limb,) if unread and coverage_limb and coverage_limb not in grade.coverage_limbs else ())
    return replace(grade, coverage_failed=grade.coverage_failed or bool(unread), coverage_limbs=limbs,
                   reports=grade.reports + (report(remarks), run_grader.format_unread_remainder(unread), *details))


def voice_remarks(run: Path, artifacts: tuple[str, ...]) -> tuple[Remark, ...]:
    import voice_read
    results = []
    for artifact in artifacts:
        records = coursework_run.voice_records_directory(run, artifact)
        key = records.name
        payload = voice_read._read_json(records / voice_read.READER_RECORD_NAME)
        if isinstance(payload, dict) and isinstance(payload.get("remarks"), list):
            results.extend(Remark(f"VOICE-READ: {key}", text) for text in payload["remarks"] if isinstance(text, str) and text.strip())
    return tuple(results)


def read_report(text: str) -> tuple[Remark, ...]:
    result = []
    for line in text.splitlines():
        if not line.startswith(PREFIX):
            continue
        try:
            value = json.loads(line[len(PREFIX):])
            if set(value) != {"origin", "text"} or not all(isinstance(v, str) and v.strip() for v in value.values()):
                raise ValueError("invalid remark")
            result.append(Remark(**value))
        except (ValueError, TypeError) as failure:
            raise RemarkError("grader returned an invalid reader remark") from failure
    return tuple(dict.fromkeys(result))


def coverage_lines(report_text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(line for line in report_text.splitlines() if not line.startswith(PREFIX) and re.search(
        r"\bunread\b|not[ -](?:graded|scanned|checked|compared|run|verified)|never[ -]graded|incomplete coverage", line, re.I)))


def _receipt_path(run: Path, skill: str, key: str) -> Path:
    return run / "approval-prepares" / (sha256(f"{skill}\0{key}".encode()).hexdigest() + ".json")


def _digest(sources: tuple[Path, ...]) -> str:
    value = sha256()
    for path in sources:
        value.update(str(path.resolve()).encode())
        value.update(b"\0")
        value.update(path.read_bytes())
    return value.hexdigest()


@dataclass(frozen=True)
class Prepared:
    report: str
    remarks: tuple[Remark, ...]
    coverage: tuple[str, ...]


def prepare(run: Path, skill: str, key: str, sources: tuple[Path, ...], report_text: str,
            *, coverage_only: bool = False) -> Prepared:
    import approval_record
    path = _receipt_path(run, skill, key)
    current = () if coverage_only else read_report(report_text)
    previous = ()
    if path.exists() and not coverage_only:
        try:
            previous = read_report(json.loads(path.read_text(encoding="utf-8"))["report"])
        except (OSError, ValueError, KeyError, TypeError) as failure:
            raise RemarkError("the preceding pre-ask remark receipt is unreadable") from failure
    retained = tuple(r for r in previous if r not in current)
    complete_report = report_text + ("\n" + report(retained) if retained else "")
    prepared = Prepared(complete_report, () if coverage_only else read_report(complete_report), coverage_lines(complete_report))
    path.parent.mkdir(parents=True, exist_ok=True)
    approval_record._write(path, {"prepared_at": time.time(), "source_digest": _digest(sources),
                                  "grader_report": report_text, "report": complete_report})
    return prepared


def leave_request(outcomes: tuple[Outcome, ...]) -> str | None:
    """Name the reply forms that answer every leave proposal, or None when there is none."""
    numbers = ", ".join(str(n) for n, outcome in enumerate(outcomes, 1) if outcome.status == "leave")
    if not numbers:
        return None
    return f'Proposed to leave: {numbers}. To leave them, reply "leave all of them" or "leave {numbers}".'


def surface(prepared: Prepared, outcomes: tuple[Outcome, ...] = (), *, request_leaves: bool = True) -> str:
    if len(outcomes) != len(prepared.remarks):
        raise RemarkError("every reader remark needs a fixed outcome or a proposal to leave it")
    lines = []
    for number, (remark, outcome) in enumerate(zip(prepared.remarks, outcomes), 1):
        if outcome.status not in {"fixed", "leave"} or not outcome.detail.strip():
            raise RemarkError(f"remark {number} needs a substantive fixed or leave outcome")
        label = "Fixed" if outcome.status == "fixed" else "Propose to leave"
        lines.append(f"{number}. {remark.origin} — {remark.text} — {label}: {outcome.detail}")
    request = leave_request(outcomes) if request_leaves else None
    return "\n".join((*lines, *((request,) if request else ()), *prepared.coverage))


def _left_numbers(reply: str, population: int) -> set[int]:
    # A negated leave never authorizes a waiver. Unrecognized wording fails closed.
    text = reply.casefold()
    if re.search(r"\b(?:don't|do not|not|never)\b", text):
        return set()
    if re.search(r"\b(?:leave|keep|accept)\s+(?:all(?:\s+of)?\s+(?:them|these|the remarks|remarks)|all\b|them all|everything|every remark)\b", text):
        return set(range(1, population + 1))
    result = set()
    for match in re.finditer(r"\b(?:leave|keep|accept)\s+(?:(?:remarks?|numbers?)\s+)?((?:\d+\s*(?:,|and|&)\s*)*\d+)\b", text):
        result.update(int(value) for value in re.findall(r"\d+", match.group(1)))
    return result


def _prepared_receipt(run: Path, skill: str, key: str, sources: tuple[Path, ...],
                      report_text: str, reply_at: float | None, *, accepted: bool = False,
                      transcript_unread: bool = False):
    """Keep the same grade, source and ordering comparison for every go-ahead."""
    try:
        receipt = json.loads(_receipt_path(run, skill, key).read_text(encoding="utf-8"))
        boundary = max(path.stat().st_mtime for path in sources)
        prepared_at = receipt["prepared_at"]
        if receipt["source_digest"] != _digest(sources) or (not accepted and receipt["grader_report"] != report_text):
            raise RemarkError("the prepared grade or source changed; prepare and show the approval again")
        if not boundary < prepared_at or (reply_at is None and not transcript_unread) or (reply_at is not None and not prepared_at < reply_at):
            raise RemarkError("the paired grader must run after the last source change and before the approval reply")
    except (OSError, ValueError, KeyError, TypeError) as failure:
        if isinstance(failure, RemarkError):
            raise
        raise RemarkError("approval needs a readable pre-ask grade receipt") from failure
    return receipt, boundary, prepared_at


def _missing_lines(required, shown):
    shown_lines = {" ".join(line.split()) for message in shown for line in message.splitlines()}
    return [line for line in required if " ".join(line.split()) not in shown_lines]


def verify_coverage(run: Path, skill: str, key: str, sources: tuple[Path, ...],
                    report_text: str, reply_at: float | None, *, transcripts):
    """Verify clinical coverage without inheriting coursework reader remarks."""
    import approval_record
    _, _, prepared_at = _prepared_receipt(run, skill, key, sources, report_text, reply_at,
                                          transcript_unread=reply_at is None)
    if reply_at is None:
        return approval_record.ReplyVerification("unreadable", "coverage-line transcript unreadable")
    shown, unread = approval_record.assistant_text(run, after=prepared_at, before=reply_at,
                                                  transcripts=transcripts)
    if unread:
        return approval_record.ReplyVerification("unreadable", "coverage-line transcript unreadable")
    if _missing_lines(coverage_lines(report_text), shown):
        raise RemarkError("coverage lines were not shown before approval")
    return approval_record.ReplyVerification("verified", "paired-grader coverage lines shown")


def verify(run: Path, skill: str, key: str, sources: tuple[Path, ...], report_text: str,
           reply: str, reply_at: float | None, outcomes: tuple[Outcome, ...],
           *, accepted: list[dict] | None = None) -> list[dict]:
    import approval_record
    receipt, boundary, prepared_at = _prepared_receipt(run, skill, key, sources, report_text,
                                                      reply_at, accepted=accepted is not None)
    prepared = Prepared(receipt["report"], read_report(receipt["report"]), coverage_lines(report_text))
    inherited_leaves = set()
    if accepted is not None:
        stored = tuple(Remark(row["origin"], row["text"]) for row in accepted)
        if any(remark not in stored for remark in read_report(report_text)):
            raise RemarkError("reader remarks changed; prepare and show the content approval again")
        prepared = Prepared(report_text, stored, coverage_lines(report_text))
        outcomes = tuple(Outcome("fixed" if row["outcome"] == "fixed" else "leave", row["detail"])
                         for row in accepted)
        inherited_leaves = {n for n, row in enumerate(accepted, 1) if row["outcome"] == "left on clinician's word"}
    # A posting inherits answered leaves, so only the content ask must carry the reply forms.
    required = surface(prepared, outcomes, request_leaves=accepted is None).splitlines()
    shown, unread = approval_record.assistant_text(run, after=boundary if accepted is not None else prepared_at, before=reply_at)
    missing = _missing_lines(required, shown)
    if missing:
        raise RemarkError("reader remarks or coverage lines were not shown before approval" + ("; transcript unreadable" if unread else "") + ": " + " | ".join(missing))
    leaves = _left_numbers(reply, len(prepared.remarks)) | inherited_leaves
    open_remarks = [str(n) for n, outcome in enumerate(outcomes, 1) if outcome.status == "leave" and n not in leaves]
    if open_remarks:
        raise RemarkError("unanswered leave proposals for reader remarks: " + ", ".join(open_remarks))
    return [{"number": n, "origin": remark.origin, "text": remark.text,
             "outcome": "fixed" if outcome.status == "fixed" else "left on clinician's word",
             "detail": outcome.detail} for n, (remark, outcome) in enumerate(zip(prepared.remarks, outcomes), 1)]

def approval_report(report_text: str, context_report: str, run: Path, artifacts: tuple[str, ...]) -> str:
    """Assemble the same report before the ask and during approval."""
    return report_text + "\n" + context_report + "\n" + report(voice_remarks(run, artifacts))
