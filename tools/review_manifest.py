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
from encounter_openers import (OpenerChanged, OpenerRecordMissing, digest, no_longer_a_file, private_target,
                               read_openers)
from encounter_status import EvidenceChanged, StatusMissing, status_for
from worksheet_grammar import ENTRY_CANDIDATE, em_identity, entry_reading, entry_region, read_entries, selected_em
from run_record_reader import (DamagedRecord, damaged_record_result, RecordUpdate, UnreadableRecord, fault_report, object_record,
                               read_handwritten_record, read_tool_record, update_tool_record)

DECLARED_LIMITS = (
    "Normalization is UTF-8, LF, per-line trailing-whitespace removal and exactly one final newline; it does not reinterpret prose or collapse internal spaces. Review layout changes do not alter the manifest.",
    "Named Markdown or plain Medatrax, tier, schedule, summary and technical-receipt boundaries and fenced tier blocks are excluded. Unrecognized boundaries are retained rather than silently discarded; exactly one Medatrax field block is required. A visible worksheet embedded in a note must equal its separately selected worksheet.",
    "The caller supplies final code populations and visible worksheet paths. Shared worksheet entry parsing binds the selected identities in both the visible and canonical private worksheet; it does not compare MDM support prose, descriptors, anchors or other provenance. Those remain the clinical code graders' authority.",
    "The whole private worksheet is fingerprinted for the E/M audit check-off in a separate record beside the manifest, never in the approval-bound manifest: a provenance-only edit and rebuild leave the manifest byte-identical and update only that record, which em_audit compares. The manifest and that record are written one after the other, not as one transaction.",
    "A matching passing receipt establishes its recorded currency check, not perpetual publisher currency. Run coding_freshness visibly whenever the manifest changes.",
    "The locked manifest write is atomic, not a cross-file snapshot. Approval and rendering re-read current sources; a source changing after validation remains an ordinary concurrent-edit risk.",
)

MANIFEST = "batch-codes.json"
# The private worksheet fingerprints the E/M audit check-off compares, beside the manifest and never
# in it, so a provenance-only edit and rebuild leave the approved manifest byte-identical.
PRIVATE_FINGERPRINTS = "em-audit/private-worksheets.json"
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


class StaleRecord(ValueError):
    """The manifest or its freshness receipt no longer matches the run it was built from.

    A reader can tell a stale record, which is a defect of the run, from one that cannot be read
    or that the manifest never bound, which leaves coverage incomplete; every other caller reads a
    ``ValueError``. A file the manifest was built from that is now missing (a note, worksheet,
    opener record, opener source or encounter file, patient-status record or evidence) changed
    after the manifest and is stale; a missing freshness receipt, written after the manifest, is
    not.
    """


def read_text(path: Path) -> str:
    return read_handwritten_record(path, "text").require_text(force=True)


def recorded_text(path: Path, recorded: bool) -> str:
    """``read_text`` of a file a recorded manifest item names; no longer a file there is a change after it."""
    try:
        return read_text(path)
    except OSError as error:
        if recorded and no_longer_a_file(path):
            raise StaleRecord(f"{path.name} is no longer a file where the manifest recorded it") from error
        raise


def _codes_or_refusal(text: str, *, private: bool) -> tuple[dict | None, ValueError | None]:
    """``selected_codes``, or None with the refusal where its grammar refuses the worksheet."""
    try:
        return selected_codes(text, private=private), None
    except ValueError as error:
        return None, error


def _disagreement(kind: str, refusal: ValueError | None) -> str:
    """The message of a worksheet whose codes disagree, naming a grammar refusal as its cause."""
    if refusal is not None:
        return f"{kind} worksheet refused by the code grammar: {refusal}"
    return f"{kind} worksheet selected codes disagree with manifest"


def _content(run: Path, item: dict, private_sha256: str | None = None) -> tuple[str, str, str, str, str]:
    """Note, visible worksheet and private worksheet text, each read once, with the two fingerprints.

    For a recorded manifest item, a disagreement is ``StaleRecord`` when the record it reads changed
    after the manifest: the embedded worksheet copy, which ``build`` refuses to bind in
    disagreement and no fingerprint covers; the visible worksheet, when the note and worksheet no
    longer match ``normalized_sha256``; the private worksheet, when it no longer matches
    ``private_sha256``, its recorded fingerprint (``PRIVATE_FINGERPRINTS``). A disagreement over
    unchanged records means the manifest never matched them, and stays a plain ``ValueError``, as
    does a private worksheet disagreement read without a recorded fingerprint, where a change cannot
    be told from a manifest never valid.
    """
    recorded = "normalized_sha256" in item
    note, fields, embedded = note_parts(recorded_text(resolve(run, item["note_path"]), recorded))
    worksheet = visible_worksheet(recorded_text(resolve(run, item["worksheet_path"]), recorded))
    code_hash = digest((note + worksheet).encode("utf-8"))
    if any(visible_worksheet(value).strip() != worksheet.strip() for value in embedded):
        raise (StaleRecord if recorded else ValueError)("embedded and selected visible worksheets disagree")
    expected = clean_codes(item["codes"])
    codes, refusal = _codes_or_refusal(worksheet, private=False)
    if codes != expected:
        moved = recorded and code_hash != item["normalized_sha256"]
        raise (StaleRecord if moved else ValueError)(_disagreement("visible", refusal)) from refusal
    private = recorded_text(resolve(run, item["private_worksheet_path"]), recorded)
    codes, refusal = _codes_or_refusal(private, private=True)
    if codes != expected:
        # A recorded fingerprint binds this worksheet to a build: a worksheet that changed after it,
        # or one it already binds because build wrote the record and then failed to write the
        # manifest, means the manifest is the stale record.
        moved = private_sha256 is not None
        raise (StaleRecord if moved else ValueError)(_disagreement("private", refusal)) from refusal
    return note, worksheet, private, code_hash, digest(fields.encode("utf-8"))


def content(run: Path, item: dict) -> tuple[str, str, str, str]:
    note, worksheet, _, code_hash, field_hash = _content(run, item)
    return note, worksheet, code_hash, field_hash


def private_worksheet_sha256(private: str) -> str:
    """The fingerprint of the whole private worksheet, normalized as ``normalized`` normalizes.

    ``normalized_sha256`` binds the note and the visible worksheet, which the receipt carries;
    this fingerprint covers everything the E/M audit check-off renders from the private worksheet
    (entries, anchors and provenance, the icd10-cpt step 4 blocks and the element block). It lives
    in ``PRIVATE_FINGERPRINTS`` beside the manifest, never in it: provenance-only edits keep the
    approval identity, as the selected-code projection rules. ``em_audit`` compares it and refuses
    a check-off whose private worksheet changed after it was recorded.
    """
    return digest(normalized(private).encode("utf-8"))


def clean_codes(codes: dict) -> dict:
    return {"icd10": coding_freshness.normalize_codes(codes.get("icd10"), "icd10"),
            "em": str(codes.get("em", "")).strip().upper(),
            "cpt": coding_freshness.normalize_codes(codes.get("cpt", []), "cpt"),
            "hcpcs": coding_freshness.normalize_codes(codes.get("hcpcs", []), "hcpcs")}


def code_key(system: str, code: str) -> str:
    """The code population an entry selects into: icd10, em, cpt or hcpcs."""
    if system.upper().startswith("ICD"):
        return "icd10"
    return "em" if em_identity(system, code) else system.lower()


def selected_codes(text: str, *, private: bool) -> dict:
    """Project code identities through shared strict entry/for-entry grammar.

    Visible colon labels are the SOAP/HP worksheet adapter. Private differential
    and reconciliation regions do not add final selections; E/M remains an
    explicit code label or a shared-parsed CPT entry from the E/M families, as
    ``worksheet_grammar.selected_em`` selects it: the one rule the E/M audit check-off anchors to.
    """
    entry_text = entry_region(text) if private else entry_reading(text, private=False)
    entries = read_entries(entry_text)
    if len(list(ENTRY_CANDIDATE.finditer(entry_text))) != len(entries):
        raise ValueError("worksheet has unread selected-code lines")
    em = {code for _, code in selected_em(text, entry_text, entries, private=private)}
    result = {"icd10": set(), "em": em, "cpt": set(), "hcpcs": set()}
    for entry in entries:
        if not entry.for_entry or em_identity(entry.system, entry.code):
            continue
        result[code_key(entry.system, entry.code)].add(entry.code.upper())
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


def manifest_for(run: Path, *, batch: bool | None) -> dict:
    """The manifest in the clinical mode asked for; ``batch=None`` accepts the mode it records."""
    value = read_tool_record(run / MANIFEST, decode_manifest)
    if value is None or (batch is not None and value["batch"] != batch):
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
    fingerprints = []
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
        _, _, private, item["normalized_sha256"], item["field_block_sha256"] = _content(run, item)
        fingerprints.append({"private_worksheet_path": item["private_worksheet_path"],
                             "private_worksheet_sha256": private_worksheet_sha256(private)})
        value["encounters"].append(item)
    payload = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    decode_manifest(payload.decode("utf-8"))
    record = dict(schema=1, producer="review_manifest", worksheets=fingerprints)
    record_payload = (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    decode_private_fingerprints(record_payload.decode("utf-8"))

    def change(previous):
        # An unchanged rebuild leaves the approval identity and timestamp untouched.
        return RecordUpdate(None if previous == value else payload, value)

    def change_record(previous):
        return RecordUpdate(None if previous == record else record_payload, record)

    # The fingerprint record first: it records only the worksheets as they are now, so a manifest
    # write that then fails leaves a stale manifest, refused as stale, and never a new manifest
    # beside an old record, which would read as a private worksheet edited after the manifest.
    (run / PRIVATE_FINGERPRINTS).parent.mkdir(parents=True, exist_ok=True)
    update_tool_record(run / PRIVATE_FINGERPRINTS, decode_private_fingerprints, change_record)
    return update_tool_record(run / MANIFEST, decode_manifest, change)


def decode_private_fingerprints(text: str) -> dict:
    """The private worksheet fingerprint record ``build`` writes beside the manifest."""
    value = object_record(text)
    if (value.get("producer") != "review_manifest" or type(value.get("schema")) is not int
            or value["schema"] != 1 or not isinstance(value.get("worksheets"), list)):
        raise ValueError("invalid private worksheet fingerprint record")
    paths = []
    for entry in value["worksheets"]:
        if (not isinstance(entry, dict) or set(entry) != {"private_worksheet_path", "private_worksheet_sha256"}
                or not isinstance(entry["private_worksheet_path"], str) or not entry["private_worksheet_path"]
                or not SHA.fullmatch(str(entry["private_worksheet_sha256"]))):
            raise ValueError("invalid private worksheet fingerprint entry")
        paths.append(entry["private_worksheet_path"])
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate private worksheet fingerprint")
    return value


def private_fingerprints(run: Path) -> dict[str, str] | None:
    """Each recorded private worksheet path with its fingerprint; None when no record was written.

    An unreadable record raises ``UnreadableRecord``, as every tool-written run record does.
    """
    value = read_tool_record(Path(run) / PRIVATE_FINGERPRINTS, decode_private_fingerprints)
    if value is None:
        return None
    return {entry["private_worksheet_path"]: entry["private_worksheet_sha256"] for entry in value["worksheets"]}


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


@dataclass(frozen=True)
class ValidatedEncounter:
    item: dict
    note: str
    worksheet: str
    private: str


@dataclass(frozen=True)
class ValidatedRun:
    """What one validation read: the manifest, its receipt and each encounter text."""

    manifest: dict
    receipt: dict
    encounters: tuple[ValidatedEncounter, ...]


def _validated(run: Path, *, batch: bool | None,
               fingerprints: dict[str, str] | None = None) -> tuple[Binding, ValidatedRun]:
    """Validate once; ``batch=None`` takes the mode the manifest records.

    ``fingerprints`` (``private_fingerprints``) only lets a private-worksheet code disagreement be
    told stale from never valid; approval passes none and its rule is unchanged.
    """
    run = run.resolve()
    manifest = manifest_for(run, batch=batch)
    try:
        openers = read_openers(run)
    except OpenerRecordMissing as error:
        raise StaleRecord("opener record went missing after the manifest recorded its encounters") from error
    except OpenerChanged as error:
        raise StaleRecord(f"{error}, after the manifest") from error
    if manifest["service_date"] != openers["service_date"] or len(manifest["encounters"]) != len(openers["encounters"]):
        raise StaleRecord("opener population or service date changed")
    notes, worksheets, encounters = [], [], []
    for item, opener in zip(manifest["encounters"], openers["encounters"]):
        note, worksheet, private_text, code_hash, field_hash = _content(
            run, item, (fingerprints or {}).get(item["private_worksheet_path"]))
        encounters.append(ValidatedEncounter(item, note, worksheet, private_text))
        if code_hash != item["normalized_sha256"] or field_hash != item["field_block_sha256"]:
            raise StaleRecord("manifest is stale against current notes or worksheets")
        if item["opener"] != {key: opener[key] for key in ("name", "age", "sex")}:
            raise StaleRecord("opener details changed")
        if item["setting"] == "office":
            try:
                current = status_for(run, item["order"])
            except EvidenceChanged as error:
                raise StaleRecord(f"{error}, after the manifest") from error
            except StatusMissing as error:
                raise StaleRecord("patient-status record went missing after the manifest recorded it") from error
            if item["patient_status"] != current:
                raise StaleRecord("patient status changed")
        notes.append(resolve(run, item["note_path"]))
        private = run / "worksheets" / (notes[-1].stem + ".md")
        if resolve(run, item["private_worksheet_path"]) != private:
            # The same filename in another folder is a run that moved after the manifest; another
            # filename is a manifest that never named the note's own pair.
            moved = Path(item["private_worksheet_path"]).name == private.name
            raise (StaleRecord if moved else ValueError)("private worksheet is not the canonical note pair")
        worksheets.extend((resolve(run, item["worksheet_path"]), private))
    receipt_path = resolve(run, manifest["receipt_path"])
    receipt = read_tool_record(receipt_path, decode_receipt)
    findings = []
    population = coding_freshness.read_encounters(manifest, findings)
    if receipt is None:
        raise ValueError("freshness receipt is missing")
    if receipt["service_date"] != manifest["service_date"] or receipt["encounters"] != population or findings:
        raise StaleRecord("freshness receipt is stale")
    sources = (run / MANIFEST, receipt_path)
    binding = Binding(sources, tuple(notes), tuple(worksheets), (*notes, *worksheets, *sources))
    return binding, ValidatedRun(manifest, receipt, tuple(encounters))


def _validated_binding(run: Path, *, batch: bool) -> tuple[Binding, dict, list[tuple[str, str]]]:
    binding, validated = _validated(run, batch=batch)
    return binding, validated.manifest, [(item.note, item.worksheet) for item in validated.encounters]


def approval_binding(run: Path, *, batch: bool) -> Binding:
    return _validated_binding(run, batch=batch)[0]


def validated_population(run: Path, fingerprints: dict[str, str] | None = None) -> ValidatedRun:
    """The run as approval validates it, with every text the validation read.

    A reader that renders the coding decisions of a run uses this, so the text it renders is the
    text that was validated and a stale manifest or receipt refuses. ``fingerprints`` is
    ``private_fingerprints``, read by the caller, as ``_validated`` takes it.
    """
    return _validated(run, batch=None, fingerprints=fingerprints)[1]


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
