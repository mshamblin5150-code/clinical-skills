"""Build clinical coding manifests, then render a batch after visible freshness (ADR 0427).

``build RUN --inputs FILE`` reads a JSON list of {note, worksheet, setting,
codes}; paths are relative to RUN. Patient details come only from openers.json.
Run coding_freshness.py separately. ``render RUN --output FILE`` requires its
passing receipt and uses the same source reader and fingerprint computation.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import re

import coding_freshness
from console_codec import require_python_floor, use_utf8
from encounter_openers import digest, private_target, read_openers
from encounter_status import status_for
from run_record_reader import (DamagedRecord, damaged_record_result, RecordUpdate, UnreadableRecord, fault_report, object_record,
                               read_handwritten_record, read_tool_record, update_tool_record)

DECLARED_LIMITS = (
    "Normalization is UTF-8, LF, per-line trailing-whitespace removal and exactly one final newline; it does not reinterpret prose or collapse internal spaces. Review layout changes do not alter the manifest.",
    "Named Markdown or plain Medatrax, tier, schedule, summary and technical-receipt boundaries and fenced tier blocks are excluded. Unrecognized boundaries are retained rather than silently discarded; exactly one Medatrax field block is required. A visible worksheet embedded in a note must equal its separately selected worksheet.",
    "The caller supplies final code populations and visible worksheet paths. Shared worksheet entry parsing binds the selected identities in both the visible and canonical private worksheet; it does not compare MDM support prose, descriptors, anchors or other provenance. Those remain the clinical code graders' authority.",
    "A matching passing receipt establishes its recorded currency check, not perpetual publisher currency. Run coding_freshness visibly whenever the manifest changes.",
    "The locked manifest write is atomic, not a cross-file snapshot. Approval and rendering re-read current sources; a source changing after validation remains an ordinary concurrent-edit risk.",
)

MANIFEST = "batch-codes.json"
RECEIPT = "batch-freshness.json"
SHA = re.compile(r"[0-9a-f]{64}")
NAMED = r"(?:Medatrax(?: entry)?(?: block| fields)?|Tier block|Coding worksheet|Technical receipts?|Freshness receipt|Schedule(?: table)?|Shift summary)"
HEADING = re.compile(rf"(?m)^(?:#{{1,2}}[ \t]+(.+?)|(?:#{{1,6}}[ \t]+)?(?:\*\*)?({NAMED})(?:\*\*)?:?)[ \t]*$")
TIER_FENCE = re.compile(r"(?ms)^```[^\n]*\n(?=(?:DERIVED|FILLED|FLAG|GAPS|UNKNOWN)\b).*?^```[ \t]*$")


def normalized(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).rstrip("\n") + "\n"


def section_kind(title: str) -> str:
    title = title.strip().strip("*").casefold()
    if title.startswith("medatrax"):
        return "fields"
    if title == "coding worksheet":
        return "worksheet"
    if title.startswith(("tier", "technical receipt", "freshness receipt", "schedule", "shift summary",
                         "drift matrix", "drift verdicts", "proposed (verify before use)")):
        return "private"
    return "visible"


def note_parts(text: str) -> tuple[str, str, list[str]]:
    text = text.replace("\r\n", "\n")
    text = TIER_FENCE.sub("", text)
    headings = list(HEADING.finditer(text))
    visible = [text[:headings[0].start()]] if headings else [text]
    fields = []
    worksheets = []
    for index, heading in enumerate(headings):
        block = text[heading.start():headings[index + 1].start() if index + 1 < len(headings) else len(text)]
        kind = section_kind(heading.group(1) or heading.group(2))
        if kind == "fields":
            fields.append(block)
        elif kind == "worksheet":
            worksheets.append(text[heading.end():headings[index + 1].start() if index + 1 < len(headings) else len(text)])
        elif kind == "visible":
            visible.append(block)
    if len(fields) != 1:
        raise ValueError("note needs exactly one Medatrax field block")
    # A separating horizontal rule belongs to the boundary, not clinical content.
    clean = lambda value: re.sub(r"(?:\n[ \t]*---[ \t]*)+\s*$", "\n", value)
    return normalized(clean("".join(visible))), normalized(clean(fields[0])), [clean(item) for item in worksheets]


def split_note(text: str) -> tuple[str, str]:
    note, fields, _ = note_parts(text)
    return note, fields


def visible_worksheet(text: str) -> str:
    # The sole public receipt line is added at render time, not hashed recursively.
    return normalized(re.sub(r"(?mi)^Coding freshness:[ \t]*PASS[ \t]*\n?", "", text))


def resolve(run: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (run / path).resolve()


def read_text(path: Path) -> str:
    return read_handwritten_record(path, "text").require_text(force=True)


def content(run: Path, item: dict) -> tuple[str, str, str, str]:
    note, fields, embedded = note_parts(read_text(resolve(run, item["note_path"])))
    worksheet = visible_worksheet(read_text(resolve(run, item["worksheet_path"])))
    if any(visible_worksheet(value).strip() != worksheet.strip() for value in embedded):
        raise ValueError("embedded and selected visible worksheets disagree")
    expected = clean_codes(item["codes"])
    if selected_codes(worksheet, private=False) != expected:
        raise ValueError("visible worksheet selected codes disagree with manifest")
    private = resolve(run, item["private_worksheet_path"])
    if selected_codes(read_text(private), private=True) != expected:
        raise ValueError("private worksheet selected codes disagree with manifest")
    return note, worksheet, digest((note + worksheet).encode("utf-8")), digest(fields.encode("utf-8"))


def clean_codes(codes: dict) -> dict:
    return {"icd10": coding_freshness.normalize_codes(codes.get("icd10"), "icd10"),
            "em": str(codes.get("em", "")).strip().upper(),
            "cpt": coding_freshness.normalize_codes(codes.get("cpt", []), "cpt"),
            "hcpcs": coding_freshness.normalize_codes(codes.get("hcpcs", []), "hcpcs")}


def selected_codes(text: str, *, private: bool) -> dict:
    """Project code identities through shared strict entry/for-entry grammar.

    Visible colon labels are the SOAP/HP worksheet adapter. Private differential
    and reconciliation regions do not add final selections; E/M remains an
    explicit code label or a shared-parsed CPT entry from the E/M families.
    """
    from specificity_scan import read_entries
    from worksheet_grammar import DIFFERENTIAL_HEADING, STEP_FOUR_START, ENTRY_CANDIDATE
    em = set(re.findall(r"(?mi)^[ \t]*(?:\*\*)?E/M(?:\*\*)?[ \t]*:[ \t]*(\d{5})\b", text))
    if private:
        boundaries = [match.start() for pattern in (DIFFERENTIAL_HEADING, STEP_FOUR_START)
                      if (match := pattern.search(text)) is not None]
        entry_text = text[:min(boundaries)] if boundaries else text
    else:
        entry_text = re.sub(r"(?mi)^(ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]*:[ \t]*", r"\1 ", text)
    result = {"icd10": set(), "em": em, "cpt": set(), "hcpcs": set()}
    entries = read_entries(entry_text)
    if len(list(ENTRY_CANDIDATE.finditer(entry_text))) != len(entries):
        raise ValueError("worksheet has unread selected-code lines")
    for entry in entries:
        if not entry.for_entry:
            continue
        code = entry.code.upper()
        system = entry.system.upper()
        key = "icd10" if system.startswith("ICD") else system.lower()
        if key == "cpt" and code in coding_freshness.ED_EM | coding_freshness.OFFICE_EM:
            key = "em"
        result[key].add(code)
    if len(result["em"]) != 1:
        raise ValueError("worksheet needs exactly one final E/M identity")
    return {key: next(iter(values)) if key == "em" else sorted(values) for key, values in result.items()}


def decode_manifest(text: str) -> dict:
    value = object_record(text)
    if (value.get("producer") != "review_manifest" or type(value.get("schema")) is not int
            or value["schema"] != 1 or type(value.get("batch")) is not bool):
        raise ValueError("invalid manifest header")
    review_constants(value.get("review_constants"), batch=value["batch"])
    date.fromisoformat(value["service_date"])
    if not isinstance(value.get("receipt_path"), str) or not value["receipt_path"]:
        raise ValueError("invalid receipt path")
    findings = []
    coding_freshness.read_encounters(value, findings)
    if findings:
        raise ValueError("invalid manifest encounter population")
    for item in value["encounters"]:
        if type(item["order"]) is not int:
            raise ValueError("invalid encounter order")
        for key in ("note_path", "worksheet_path", "private_worksheet_path"):
            if not isinstance(item.get(key), str) or not item[key]:
                raise ValueError("invalid artifact path")
        if not SHA.fullmatch(str(item.get("field_block_sha256", ""))):
            raise ValueError("invalid field fingerprint")
        if not isinstance(item.get("opener"), dict) or set(item["opener"]) != {"name", "age", "sex"}:
            raise ValueError("invalid opener binding")
    if not value["batch"] and len(value["encounters"]) != 1:
        raise ValueError("standalone manifest needs one encounter")
    for key in ("note_path", "worksheet_path", "private_worksheet_path"):
        paths = [item[key] for item in value["encounters"]]
        if len(set(paths)) != len(paths):
            raise ValueError("duplicate artifact path")
    return value


def manifest_for(run: Path, *, batch: bool) -> dict:
    value = read_tool_record(run / MANIFEST, decode_manifest)
    if value is None or value["batch"] != batch:
        raise ValueError("missing manifest or wrong clinical mode")
    return value


def review_constants(value: object, *, batch: bool) -> dict:
    from run_record_reader import require_outbound_text
    if not batch and value is None:
        return {}
    if (not isinstance(value, dict) or set(value) != {"course", "preceptor", "site"}
            or any(not isinstance(text, str) or not text.strip() for text in value.values())):
        raise ValueError("batch Review sheet needs current course, preceptor and site")
    for text in value.values():
        require_outbound_text(text)
        if "\n" in text or "\r" in text:
            raise ValueError("Review constants must be single-line values")
    return value


def build(run: Path, inputs: Path, *, batch: bool, receipt: Path | None = None,
          constants: dict | None = None) -> dict:
    run = private_target(run)
    openers = read_openers(run)
    rows = read_handwritten_record(inputs, "json").require_json(force=True)
    if not isinstance(rows, list) or len(rows) != len(openers["encounters"]) or (not batch and len(rows) != 1):
        raise ValueError("input population differs from opener population")
    value = dict(schema=1, producer="review_manifest", batch=batch,
                 review_constants=review_constants(constants, batch=batch) if batch else None,
                 service_date=openers["service_date"], receipt_path=str((receipt or run / RECEIPT).resolve()), encounters=[])
    for order, (row, opener) in enumerate(zip(rows, openers["encounters"]), 1):
        if not isinstance(row, dict) or set(row) != {"note", "worksheet", "setting", "codes"}:
            raise ValueError("inputs need note, worksheet, setting and codes only")
        if row["setting"] not in {"office", "emergency-department"}:
            raise ValueError("unknown setting")
        item = dict(id=f"note-{order}", order=order,
                    note_path=str(resolve(run, row["note"])), worksheet_path=str(resolve(run, row["worksheet"])),
                    private_worksheet_path=str((run / "worksheets" / (resolve(run, row["note"]).stem + ".md")).resolve()),
                    setting=row["setting"], codes=row["codes"],
                    opener={key: opener[key] for key in ("name", "age", "sex")},
                    patient_status=status_for(run, order) if row["setting"] == "office" else {"value": "not-applicable"})
        _, _, item["normalized_sha256"], item["field_block_sha256"] = content(run, item)
        value["encounters"].append(item)
    payload = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    decode_manifest(payload.decode("utf-8"))
    def change(previous):
        # An unchanged rebuild leaves the approval identity and timestamp untouched.
        return RecordUpdate(None if previous == value else payload, value)
    return update_tool_record(run / MANIFEST, decode_manifest, change)


@dataclass(frozen=True)
class Binding:
    sources: tuple[Path, ...]
    notes: tuple[Path, ...]
    worksheets: tuple[Path, ...]
    source_times: tuple[Path, ...]


def note_paths(run: Path, *, batch: bool) -> tuple[Path, ...]:
    return tuple(resolve(run, item["note_path"]) for item in manifest_for(run, batch=batch)["encounters"])


def worksheet_paths(run: Path, *, batch: bool) -> tuple[Path, ...]:
    return tuple(resolve(run, item[key]) for item in manifest_for(run, batch=batch)["encounters"]
                 for key in ("worksheet_path", "private_worksheet_path"))


def decode_receipt(text: str) -> dict:
    return coding_freshness.receipt_record(text)


def _validated_binding(run: Path, *, batch: bool) -> tuple[Binding, dict, list[tuple[str, str]]]:
    run = run.resolve()
    manifest = manifest_for(run, batch=batch)
    openers = read_openers(run)
    if manifest["service_date"] != openers["service_date"] or len(manifest["encounters"]) != len(openers["encounters"]):
        raise ValueError("opener population or service date changed")
    notes, worksheets, contents = [], [], []
    for item, opener in zip(manifest["encounters"], openers["encounters"]):
        note, worksheet, code_hash, field_hash = content(run, item)
        contents.append((note, worksheet))
        if code_hash != item["normalized_sha256"] or field_hash != item["field_block_sha256"]:
            raise ValueError("manifest is stale against current notes or worksheets")
        if item["opener"] != {key: opener[key] for key in ("name", "age", "sex")}:
            raise ValueError("opener details changed")
        if item["setting"] == "office" and item["patient_status"] != status_for(run, item["order"]):
            raise ValueError("patient status changed")
        notes.append(resolve(run, item["note_path"]))
        private = run / "worksheets" / (notes[-1].stem + ".md")
        if resolve(run, item["private_worksheet_path"]) != private:
            raise ValueError("private worksheet is not the canonical note pair")
        worksheets.extend((resolve(run, item["worksheet_path"]), private))
    receipt_path = resolve(run, manifest["receipt_path"])
    receipt = read_tool_record(receipt_path, decode_receipt)
    findings = []
    population = coding_freshness.read_encounters(manifest, findings)
    if (receipt is None or receipt["service_date"] != manifest["service_date"]
            or receipt["encounters"] != population or findings):
        raise ValueError("freshness receipt is missing or stale")
    sources = (run / MANIFEST, receipt_path)
    return Binding(sources, tuple(notes), tuple(worksheets), (*notes, *worksheets, *sources)), manifest, contents


def approval_binding(run: Path, *, batch: bool) -> Binding:
    return _validated_binding(run, batch=batch)[0]


def render(run: Path, output: Path, *, force: bool = False) -> Path:
    from docx_write import PAGE_BREAK, write_docx
    binding, manifest, contents = _validated_binding(run, batch=True)
    pages = []
    for item, (note, worksheet) in zip(manifest["encounters"], contents):
        # Bold only headings and physical field labels; numbered prose stays regular.
        def labels(text):
            plain = text.replace("**", "")
            return re.sub(r"(?m)^([A-Za-z][A-Za-z0-9 /()&+-]{0,64}):", r"**\1:**", plain)
        pages.append(f"# Note {item['order']}\n\n{labels(note)}\n## Coding worksheet\n\n{labels(worksheet)}\n**Coding freshness:** PASS\n")
    # Validation is deliberately independent of Word layout and output bytes.
    assert binding.sources
    constants = manifest["review_constants"]
    header = (f"# Review sheet\n\n**Course:** {constants['course']}\n"
              f"**Date:** {manifest['service_date']}\n**Preceptor:** {constants['preceptor']}\n"
              f"**Site:** {constants['site']}\n\n")
    return write_docx(header + ("\n" + PAGE_BREAK + "\n").join(pages), output,
                      force=force, bold_headings=True, layout="plain")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    builder = sub.add_parser("build")
    builder.add_argument("run", type=Path)
    builder.add_argument("--inputs", type=Path, required=True)
    builder.add_argument("--single", action="store_true")
    builder.add_argument("--receipt", type=Path)
    for field in ("course", "preceptor", "site"):
        builder.add_argument("--" + field)
    renderer = sub.add_parser("render")
    renderer.add_argument("run", type=Path)
    renderer.add_argument("--output", type=Path, required=True)
    renderer.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            constants = {field: getattr(args, field) for field in ("course", "preceptor", "site")}
            build(args.run, args.inputs, batch=not args.single, receipt=args.receipt,
                  constants=constants if not args.single else None)
            print("review-manifest: written; run coding_freshness.py visibly before render or approval")
        else:
            render(args.run, args.output, force=args.force)
            print("review-manifest: rendered")
    except UnreadableRecord as error:
        print(fault_report(error, check="review manifest")); return 2
    except DamagedRecord as error:
        print(damaged_record_result(error, check="review manifest", force=True)[1]); return 1
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        print("review-manifest: refused — missing, invalid, or stale evidence"); return 2
    return 0


if __name__ == "__main__":
    use_utf8(); require_python_floor(); raise SystemExit(main())
