"""Grade the independent element coverage read required by ADR 0441.

The complete mechanical boundary belongs to ``DECLARED_LIMITS``.
"""

from dataclasses import dataclass, replace
from hashlib import sha256
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re

from run_record_reader import read_handwritten_record, DamagedRecord, damaged_record_result
import bar_signatures
import run_grader
import reader_remarks
import completion_checks


EXPECTED_ROW = "the assignment element coverage read"
DECLARED_LIMITS = (
    "Two independently written lists cannot expose an element both readers omitted; source capture, semantic coverage, answering locations and omission relevance remain reader judgments.",
    "The command cannot prove separate authorship, blindness or reader execution order; those are workflow obligations. Input hashes bind only the named files, not an independently discovered population of faculty documents or the live assignment's point value.",
)


@dataclass(frozen=True)
class Result:
    failed: bool
    report: str


def _text(value, *, blank=False) -> str:
    if not isinstance(value, str) or (not blank and not value.strip()):
        raise ValueError("text field")
    return value


def _rows(value, keys, *, empty=False):
    if not isinstance(value, list) or (not empty and not value):
        raise ValueError("row population")
    for row in value:
        if not isinstance(row, dict) or set(row) != set(keys):
            raise ValueError("row fields")
    return value


def _ids(rows, field="id"):
    identifiers = [_text(row[field]) for row in rows]
    if len(set(identifiers)) != len(identifiers) or any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value) for value in identifiers):
        raise ValueError("unique identifiers")
    return set(identifiers)


def _points(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
        raise ValueError("points shape")
    return Decimal(value)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _json(path):
    value = json.loads(read_handwritten_record(path, "json").text, object_pairs_hook=_pairs)
    if not isinstance(value, dict):
        raise ValueError("object record")
    return value


def survey(run: Path, artifact: Path) -> Result:
    """Grade one built artifact against its current independent read."""
    try:
        record = _json(run / "element-coverage.json")
        if set(record) != {"artifact", "artifact_sha256", "inputs_sha256", "elements", "reconciliation"}:
            raise ValueError("coverage fields")
        inputs = record["inputs_sha256"]
        if (not isinstance(inputs, dict) or not {"rubric.json", "elements.md", "bar.md"} <= inputs.keys()
                or not any(re.fullmatch(r"assignment-[0-9-]+\.md", name) for name in inputs)):
            raise ValueError("input population")
        for name, digest in inputs.items():
            path = (run / name).resolve()
            if Path(name).is_absolute() or not path.is_relative_to(run.resolve()) or not path.is_file():
                raise ValueError("input path")
            if digest != sha256(path.read_bytes()).hexdigest():
                raise ValueError("input digest")
        rubric = _json(run / "rubric.json")
        if set(rubric) not in ({"assignment_points", "criteria", "points_exception"}, {"assignment_points", "criteria", "points_exception", "no_rubric"}):
            raise ValueError("rubric fields")
        criteria = _rows(rubric["criteria"], ("id", "criterion", "descriptor", "points"), empty=True)
        rubric_ids = _ids(criteria)
        points = _points(rubric["assignment_points"])
        total = sum((_points(row["points"]) for row in criteria), Decimal(0))
        for row in criteria:
            _text(row["criterion"])
            _text(row["descriptor"])
        no_rubric = rubric.get("no_rubric") == "The assignment has no rubric."
        if not criteria and not no_rubric or criteria and rubric.get("no_rubric"):
            raise ValueError("explicit rubric population")
        exception = _text(rubric["points_exception"], blank=True)
        if points <= 0 or (criteria and total != points and not exception.strip()):
            return Result(True, EXPECTED_ROW + ": finding - rubric points do not sum to assignment points")
        elements = _rows(record["elements"], ("id", "requirement", "origin", "rubric_id", "status", "location", "bar_quote", "remark"))
        element_ids = _ids(elements)
        reconciliation = _rows(record["reconciliation"], ("draft_id", "element_ids"))
        for element in elements:
            _text(element["requirement"])
            for name in ("rubric_id", "location", "bar_quote", "remark"):
                _text(element[name], blank=True)
            if element["status"] not in ("answered", "thin", "missing", "omitted") or element["origin"] not in ("prompt", "faculty", "rubric"):
                raise ValueError("element status or origin")
            if element["origin"] != "rubric" and element["rubric_id"]:
                raise ValueError("non-rubric identifier")
            if element["status"] == "thin":
                _text(element["remark"])
        if record["artifact"] != artifact.name or record["artifact_sha256"] != sha256(artifact.read_bytes()).hexdigest():
            return Result(True, EXPECTED_ROW + ": finding - artifact digest or name changed")
        lines = read_handwritten_record(run / "elements.md").text.splitlines()
        draft_ids = []
        for line in lines:
            if not line.strip() or line.startswith("# "):
                continue
            match = re.fullmatch(r"- ([A-Za-z][A-Za-z0-9_-]*): (\S.*)", line)
            if match is None:
                raise ValueError("draft elements shape")
            draft_ids.append(match[1])
        reconciled = _ids(reconciliation, "draft_id")
        for row in reconciliation:
            if not isinstance(row["element_ids"], list) or not row["element_ids"] or any(not isinstance(value, str) for value in row["element_ids"]):
                raise ValueError("reconciliation targets")
        if (not draft_ids or len(set(draft_ids)) != len(draft_ids)
                or set(draft_ids) != reconciled
                or any(not row["element_ids"] or not set(row["element_ids"]) <= element_ids for row in record["reconciliation"])
                or {row["rubric_id"] for row in record["elements"] if row["origin"] == "rubric"} != rubric_ids):
            raise ValueError("identifier reconciliation")
        omitted = []
        for element in record["elements"]:
            if element["status"] == "omitted":
                bar = read_handwritten_record(run / "bar.md").text
                if not bar_signatures.latest_digest(run) or not element["bar_quote"].strip() or element["bar_quote"] not in bar.splitlines():
                    return Result(True, EXPECTED_ROW + ": finding - omission is absent from the current signed bar")
                omitted.append(element["requirement"])
            elif element["status"] == "missing" or not element["location"].strip():
                return Result(True, EXPECTED_ROW + ": finding - unanswered element")
        count = len(record["elements"])
        report = f"{EXPECTED_ROW}: clean; listed {count}; answered {count - len(omitted)}; omitted {len(omitted)}"
        report += "".join("\nelement omission: " + " ".join(requirement.split()) for requirement in omitted)
        report += "\n" + reader_remarks.report(tuple(
            reader_remarks.Remark("ELEMENT-COVERAGE: " + artifact.name, element["remark"])
            for element in record["elements"] if element["status"] == "thin"
        ))
        return Result(False, report)
    except DamagedRecord as failure:
        failed, report = damaged_record_result(failure, check=EXPECTED_ROW, artifact=artifact.name)
        return Result(failed, report)
    except (OSError, ValueError, TypeError, KeyError, InvalidOperation, run_grader.SourceError):
        return Result(True, EXPECTED_ROW + ": finding - coverage record is missing or invalid")


def completion_gate(run: Path, artifact: Path, submission: str | None = None) -> Result:
    """Enforce the read before approval as well as at terminal grading."""
    exemption = completion_checks.exemption(run, submission, "element_coverage", EXPECTED_ROW)
    return Result(False, exemption) if exemption is not None else survey(run, artifact)


def apply_completion_gate(grade, run: Path, artifact: Path, submission: str | None = None):
    result = completion_gate(run, artifact, submission)
    return replace(grade, findings_failed=grade.findings_failed or result.failed,
                   reports=grade.reports + (result.report,))
