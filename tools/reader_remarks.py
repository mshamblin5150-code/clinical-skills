"""Reader remarks and the pre-ask approval receipt required by ADR 0330.

The transcript reader recognizes the same main-session messages as ADR 0318.
Free text cannot establish whether a fix resolves a remark, whether a reader
noticed every problem, or whether an affirmative reply expresses informed
consent. The caller supplies its existing content-approval decision; this module
checks explicit leave decisions and the exact surface shown before that reply.
"""

from __future__ import annotations

from run_record_reader import (read_tool_record, object_record, RecordShapeError,
                               UnreadableRecord, update_tool_record, RecordUpdate)
from run_record_reader import check_handwritten_text, DamagedRecord, damaged_record_result

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
    "Clinical collection reads canonical per-run coding reader files; legacy shared files outside the run are not bound or attached.",
    'reader_remarks record reads use the shared decoder boundary; damaged bookkeeping leaves its dependent checks not graded and contributes one record per command to coverage. Absence preserves the existing caller meaning.',
    "Remarks concealed in a folded field or a substance-only reason cannot be distinguished from ordinary reader text.",
    "The transcript comparison collapses whitespace and does not prove visual presentation or clinician attention.",
    "A fixed outcome records the change shown and accepted; it does not mechanically establish that the change resolves the remark.",
    "Explicit leaves recognize leave, keep, or accept followed by remark numbers or all remarks; other wording requires a new explicit reply.",
    "The printed reply forms must appear before the reply; another question asked beside them is not detected.",
    "Coverage selection is a wording floor: gap lines outside the selector vocabulary are not selected.",
    "Receipt and coding-reader replacement decisions hold the canonical record lock through history reads and atomic replacement; no cross-file transaction is claimed.",
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


def record_remarks(value: object, origin: str) -> tuple[tuple[Remark, ...], int]:
    """Keep a reader's legal remarks and count every malformed list member."""
    if not isinstance(value, list):
        return (), 1
    return (tuple(Remark(origin, text) for text in value if isinstance(text, str) and text.strip()),
            sum(not isinstance(text, str) or not text.strip() for text in value))


def coding_record(text: str, *, kind: str) -> dict:
    """Require a complete reader container before treating its remarks as evidence."""
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("coding reader record is not an object")
    if kind == "specificity":
        import specificity_scan
        read = specificity_scan.load_second_read_record(value, Path("read.json"))
        if not read.ok or read.unread:
            raise ValueError("specificity reader record is not completely readable")
        return value
    if kind != "agreement" or not isinstance(value.get("pairs"), list):
        raise ValueError("agreement reader record has no pairs")
    import anchor_scan
    if set(value) != {"pairs"}:
        raise ValueError("agreement reader record has unexpected keys")
    stems = set()
    for pair in value["pairs"]:
        if (not isinstance(pair, dict) or not isinstance(pair.get("stem"), str)
                or not pair["stem"] or pair["stem"] in stems
                or set(pair) - {"stem", "codes", "remarks"}
                or not isinstance(pair.get("codes"), list)):
            raise ValueError("agreement reader pair is invalid")
        stems.add(pair["stem"])
        _, unread = record_remarks(pair.get("remarks", []), pair["stem"])
        if unread:
            raise ValueError("agreement reader remarks are invalid")
        identifiers = set()
        for row in pair["codes"]:
            if (not isinstance(row, dict) or set(row) - anchor_scan.AGREEMENT_CODE_FIELDS
                    or any(not isinstance(row.get(name), str) or not row[name]
                           for name in anchor_scan.AGREEMENT_CODE_FIELDS - {"column_ground"})
                    or not isinstance(row.get("column_ground", "none"), str)
                    or not row.get("column_ground", "none")
                    or row["subject_id"] in identifiers):
                raise ValueError("agreement reader code row is invalid")
            identifiers.add(row["subject_id"])
    return value


def replace_coding_record(path: Path, replacement: dict, *, kind: str) -> None:
    """Write a retry while retaining the replaced reader's remarks verbatim."""
    decode = lambda text: coding_record(check_handwritten_text(text, path, "json").require_text(force=True), kind=kind)
    def change(current):
        updated = decode(json.dumps(replacement))
        if current is not None:
            if kind == "specificity":
                updated["remarks"] = list(dict.fromkeys((*current.get("remarks", []), *updated.get("remarks", []))))
            else:
                old = {pair["stem"]: pair.get("remarks", []) for pair in current["pairs"]}
                new_stems = {pair["stem"] for pair in updated["pairs"]}
                if any(remarks and stem not in new_stems for stem, remarks in old.items()):
                    raise RemarkError("replacement cannot drop a note with retained reader remarks")
                for pair in updated["pairs"]:
                    pair["remarks"] = list(dict.fromkeys((*old.get(pair["stem"], []), *pair.get("remarks", []))))
        return RecordUpdate(None if updated == current else (json.dumps(updated, indent=2) + "\n").encode("utf-8"))
    update_tool_record(path, decode, change)


def coding_remarks(run: Path, sources: tuple[Path, ...]) -> tuple[Remark, ...]:
    """Join only the run's canonical coding records and check-generated grounds."""
    import anchor_scan
    result: list[Remark] = []
    agreement = run / "agreement-reader" / "read.json"
    specificity = run / "specificity-reader" / "read.json"
    damage = []
    try:
        payload = read_tool_record(agreement, lambda text: coding_record(
            check_handwritten_text(text, agreement, "json").require_text(force=True), kind="agreement"))
        if payload is not None:
            notes = tuple(path for path in sources if path.suffix == ".md" and path.parent.name != "worksheets")
            rendered_path = run / "agreement" / "cpt-rendered-pages.json"
            rendered = anchor_scan._rendered_descriptors(rendered_path if rendered_path.exists() else None)
            pairs = []
            for parent in dict.fromkeys(path.parent for path in notes):
                selected, _, _ = anchor_scan._pair_agreement_sources(run / "worksheets", parent, rendered,
                    {path.stem for path in notes if path.parent == parent})
                pairs.extend(selected)
            if {pair["stem"] for pair in payload["pairs"]} - {pair.stem for pair in pairs}:
                raise RemarkError("agreement reader records do not match the approved notes")
            grade = anchor_scan._grade_agreement(pairs, 0, [agreement], {pair.stem for pair in pairs})
            result.extend((*grade.remarks, *grade.column_remarks))
    except DamagedRecord as failure:
        damaged_record_result(failure, check="agreement reader remarks", force=True)
        damage.append(failure)
    except UnreadableRecord:
        raise
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as failure:
        raise RemarkError("the run's coding reader record is unreadable") from failure
    try:
        payload = read_tool_record(specificity, lambda text: coding_record(
            check_handwritten_text(text, specificity, "json").require_text(force=True), kind="specificity"))
        if payload is not None:
            result.extend(Remark("SPECIFICITY", text) for text in payload.get("remarks", []))
    except DamagedRecord as failure:
        damaged_record_result(failure, check="specificity reader remarks", force=True)
        damage.append(failure)
    except UnreadableRecord:
        raise
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as failure:
        raise RemarkError("the run's coding reader record is unreadable") from failure
    if damage:
        # This collection feeds approval writers. Finish independent collection,
        # then refuse publication rather than recording a fabricated remark.
        raise damage[0]
    return tuple(dict.fromkeys(result))


def clinical_report(report_text: str, run: Path, sources: tuple[Path, ...]) -> str:
    return report_text + "\n" + report(coding_remarks(run, sources))


def apply_readers(grade, claims, headings, artifacts: tuple[str, ...], visuals=(), *, coverage_limb=None, heading_unread=None):
    """Return the grade and unread members outside the host's heading survey."""
    from dataclasses import replace
    records = tuple(("CLAIM", r.claim, r) for r in claims)
    records += tuple(("HEADING-READ", r.artifact, r) for r in headings if r.artifact in artifacts)
    records += tuple(("RENDERED", name, r) for r in visuals for name in (getattr(r, "deck", getattr(r, "artifact", "")),) if name in artifacts)
    remarks = tuple(Remark(f"{kind}: {name}", text) for kind, name, r in records for text in r.remarks)
    bound_heading_unread = sum(r.unread for kind, _, r in records if kind == "HEADING-READ")
    unread = sum(r.unread for kind, _, r in records if kind != "HEADING-READ")
    import completion_checks
    if not completion_checks.active("reader_remarks:unread-reader-record"):
        unread = 0
    details = tuple(f"unread reader record: {kind}: {name}; unread lines {r.unread}"
                    for kind, name, r in records if r.unread
                    and (kind == "HEADING-READ" or completion_checks.active("reader_remarks:unread-reader-record")))
    if heading_unread is not None and heading_unread > bound_heading_unread:
        details += (f"unread heading-read headings: {heading_unread - bound_heading_unread}",)
    limbs = grade.coverage_limbs + ((coverage_limb,) if unread and coverage_limb and coverage_limb not in grade.coverage_limbs else ())
    return (replace(grade, coverage_failed=grade.coverage_failed or bool(unread), coverage_limbs=limbs,
                    reports=grade.reports + (report(remarks), *details)), unread)


def voice_remarks(run: Path, artifacts: tuple[str, ...]) -> tuple[Remark, ...]:
    import voice_read
    results = []
    for artifact in artifacts:
        records = coursework_run.voice_records_directory(run, artifact)
        key = records.name
        try:
            payload = voice_read._read_json(records / voice_read.READER_RECORD_NAME, artifact=artifact)
        except DamagedRecord as failure:
            damaged_record_result(failure, check="voice reader remarks", artifact=artifact)
            continue
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


def _decode_receipt(text: str) -> dict:
    value = object_record(text)
    if (type(value.get("prepared_at")) not in (int, float)
            or not isinstance(value.get("source_digest"), str) or not re.fullmatch(r"[0-9a-f]{64}", value["source_digest"])
            or not all(isinstance(value.get(key), str) for key in ("report", "grader_report"))):
        raise RecordShapeError("record fields")
    return value


def prepare(run: Path, skill: str, key: str, sources: tuple[Path, ...], report_text: str,
            *, coverage_only: bool = False) -> Prepared:
    path = _receipt_path(run, skill, key)
    current = () if coverage_only else read_report(report_text)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as failure:
        raise UnreadableRecord(path, "could not be opened") from failure
    def change(stored):
        previous = ()
        if stored is not None and not coverage_only:
            try:
                previous = read_report(stored["report"])
            except UnreadableRecord:
                raise
            except (OSError, ValueError, KeyError, TypeError) as failure:
                raise RemarkError("the preceding pre-ask remark receipt is unreadable") from failure
        retained = tuple(r for r in previous if r not in current)
        complete_report = report_text + ("\n" + report(retained) if retained else "")
        prepared = Prepared(complete_report, () if coverage_only else read_report(complete_report), coverage_lines(complete_report))
        payload = {**(stored or {}), "prepared_at": time.time(), "source_digest": _digest(sources),
                   "grader_report": report_text, "report": complete_report}
        return RecordUpdate((json.dumps(payload, indent=2) + "\n").encode("utf-8"), prepared)
    return update_tool_record(path, _decode_receipt, change)


def leave_request(outcomes: tuple[Outcome, ...]) -> str | None:
    """Name the reply forms that answer every leave proposal, or None when there is none."""
    numbers = ", ".join(str(n) for n, outcome in enumerate(outcomes, 1) if outcome.status == "leave")
    if not numbers:
        return None
    return f'Proposed to leave: {numbers}. To leave them, reply "leave all of them" or "leave {numbers}".'


def surface(prepared: Prepared, outcomes: tuple[Outcome, ...] = (), *, request_leaves: bool = True,
            clinical: bool = False) -> str:
    if len(outcomes) != len(prepared.remarks):
        raise RemarkError("every reader remark needs a fixed outcome or a proposal to leave it")
    lines = ["READER REMARKS"] if clinical and prepared.remarks else []
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
    import approval_record
    try:
        receipt = read_tool_record(_receipt_path(run, skill, key), _decode_receipt)
        if receipt is None:
            raise RemarkError("approval needs a readable pre-ask grade receipt")
        time_sources = sources
        if skill in approval_record.CLINICAL_SKILLS:
            time_sources = approval_record._clinical_binding(run, skill).source_times
        boundary = max(path.stat().st_mtime for path in time_sources)
        prepared_at = receipt["prepared_at"]
        if receipt["source_digest"] != _digest(sources) or (not accepted and receipt["grader_report"] != report_text):
            raise RemarkError("the prepared grade or source changed; prepare and show the approval again")
        if not boundary < prepared_at or (reply_at is None and not transcript_unread) or (reply_at is not None and not prepared_at < reply_at):
            raise RemarkError("the paired grader must run after the last source change and before the approval reply")
    except UnreadableRecord:
        raise
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
           *, accepted: list[dict] | None = None, transcripts=None, clinical: bool = False) -> list[dict]:
    import approval_record
    receipt, boundary, prepared_at = _prepared_receipt(run, skill, key, sources, report_text,
                                                      reply_at, accepted=accepted is not None,
                                                      transcript_unread=clinical and reply_at is None)
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
    required = surface(prepared, outcomes, request_leaves=accepted is None, clinical=clinical).splitlines()
    if clinical and not prepared.remarks:
        return []  # The independent clinical coverage check retains its unread posture.
    if reply_at is None:
        raise RemarkError("reader remarks transcript unreadable; show the block before approval")
    shown, unread = approval_record.assistant_text(run, after=boundary if accepted is not None else prepared_at,
        before=reply_at, **({"transcripts": transcripts} if transcripts is not None else {}))
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
