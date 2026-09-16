#!/usr/bin/env python3
"""Gate finalized batch coding on source currency and service-date validity.

The private manifest names every encounter in Review-sheet order, binds the
normalized note-and-worksheet content by SHA-256, and carries that encounter's
account-backed patient status and final code populations. A clean run writes a
technical receipt; the rendered Review sheet carries only the compact pass line.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlopen

from console_codec import require_python_floor, use_utf8
import icd10_lookup
import procedure_codes_lookup
import cpt_mdm_sheet


ROOT = Path(__file__).resolve().parent.parent
ICD_RELEASE_URL = "https://www.cdc.gov/nchs/icd/icd-10-cm/files.html"
HCPCS_RELEASE_URL = (
    "https://www.cms.gov/medicare/coding-billing/"
    "healthcare-common-procedure-system/quarterly-update"
)
STATUS_VALUES = frozenset({"new", "established"})
STATUS_EVIDENCE = frozenset({"identity-map", "medatrax"})
SHA256 = re.compile(r"[0-9a-f]{64}")
OFFICE_EM = frozenset(f"992{number:02d}" for number in range(2, 16))
ED_EM = frozenset(f"992{number}" for number in range(81, 86))
MONTH = (
    r"(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December)"
)
DATE_TEXT = rf"{MONTH}\s+\d{{1,2}},\s+20\d{{2}}"

DECLARED_LIMITS = (
    "The caller supplies each normalized-content digest and code population; the gate binds those declarations but does not derive them from notes or worksheets.",
    "The live pages establish which named release applies or was most recently published; the gate does not download and byte-compare the authority's release archive with the committed database.",
    "The CPT receipt proves that its declared edition, fingerprint, and derived boundary match the database; it cannot prove that the authenticated book reading which authored the private receipt occurred.",
    "Code identity, completeness, billability, and date status do not establish medical necessity, descriptor agreement with the note, CPT instructions, or the E/M level.",
    "The MDM sheet gate checks agreement digests and edition coverage, not the clinical support for a selected level or whether its readers viewed the book.",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_url(url: str) -> str:
    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def today() -> date:
    return date.today()


def plain_text(source: str) -> str:
    without_markup = re.sub(r"<[^>]*>", " ", html.unescape(source))
    return re.sub(r"\s+", " ", without_markup).strip()


def parse_date(value: str) -> date:
    for pattern in ("%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    raise ValueError(f"unreadable date: {value}")


def month_date(value: str) -> date:
    match = re.fullmatch(r"(January|April|July|October) (20\d{2})", value)
    if match is None:
        raise ValueError(f"unreadable quarterly release: {value}")
    month = {"January": 1, "April": 4, "July": 7, "October": 10}[match.group(1)]
    return date(int(match.group(2)), month, 1)


def icd_release_token(connection: sqlite3.Connection) -> str:
    row = connection.execute("SELECT value FROM meta WHERE key = 'release'").fetchone()
    if row is None:
        raise ValueError("ICD-10-CM database has no release metadata")
    match = re.search(r"(april|october)[-_ ]1[-_ ](20\d{2})", row[0], re.I)
    if match is None:
        raise ValueError(f"ICD-10-CM release metadata is unreadable: {row[0]}")
    return f"{match.group(1).title()} 1, {match.group(2)}, ICD-10-CM release"


def applicable_icd_release(source: str, service_date: date) -> str | None:
    text = plain_text(source)
    pattern = re.compile(
        rf"((?:April|October) 1, 20\d{{2}}), ICD-10-CM release.*?"
        rf"codes should be used.*?from ({DATE_TEXT}), through ({DATE_TEXT})",
        re.I,
    )
    applicable: list[tuple[date, str]] = []
    for heading, first_text, last_text in pattern.findall(text):
        first, last = parse_date(first_text), parse_date(last_text)
        if first <= service_date <= last:
            applicable.append((first, f"{heading}, ICD-10-CM release"))
    return max(applicable)[1] if applicable else None


def current_hcpcs_release(source: str, as_of: date) -> str | None:
    text = plain_text(source)
    pattern = re.compile(
        r"((?:January|April|July|October) 20\d{2}) Alpha-Numeric HCPCS File"
        r".*?Updated (\d{2}/\d{2}/20\d{2})",
        re.I,
    )
    released: list[tuple[date, date, str]] = []
    for title, updated_text in pattern.findall(text):
        updated = parse_date(updated_text)
        effective = month_date(title.title())
        if updated <= as_of:
            released.append((updated, effective, title.title()))
    return max(released)[2] if released else None


def source_row(connection: sqlite3.Connection, system: str) -> dict[str, str | None]:
    row = connection.execute(
        "SELECT id, edition, sha256, effective_date FROM source WHERE system = ?",
        (system,),
    ).fetchone()
    if row is None:
        raise ValueError(f"procedure database has no {system} source")
    return dict(zip(("id", "edition", "sha256", "effective_date"), row, strict=True))


def normalize_codes(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a JSON list of code strings")
    return sorted({item.strip().upper() for item in value if item.strip()})


def read_encounters(manifest: dict[str, object], findings: list[str]) -> list[dict[str, object]]:
    if manifest.get("schema") != 1:
        findings.append("batch manifest schema is unreadable")
    population = manifest.get("encounters")
    if not isinstance(population, list) or not population:
        findings.append("batch has no encounter population")
        return []

    encounters: list[dict[str, object]] = []
    for position, raw in enumerate(population, 1):
        if not isinstance(raw, dict):
            findings.append(f"encounter {position} is unreadable")
            continue
        encounter_id = raw.get("id")
        order = raw.get("order")
        normalized = raw.get("normalized_sha256")
        status = raw.get("patient_status")
        codes = raw.get("codes")
        em_code = str(codes.get("em", "")).strip().upper() if isinstance(codes, dict) else ""
        setting = raw.get("setting")
        expected_family = {
            "emergency-department": ED_EM,
            "office": OFFICE_EM,
        }.get(setting) if isinstance(setting, str) else None
        if expected_family is None or em_code not in expected_family:
            findings.append(f"encounter {position} E/M code disagrees with stated place of service")
        if not isinstance(encounter_id, str) or not encounter_id.strip():
            findings.append(f"encounter {position} has no stable id")
        if not isinstance(order, int):
            findings.append(f"encounter {position} has no integer order")
        if not isinstance(normalized, str) or SHA256.fullmatch(normalized.lower()) is None:
            findings.append(f"encounter {position} normalized content hash is unreadable")
        if em_code in ED_EM and isinstance(status, dict) and status.get("value") == "not-applicable":
            pass
        elif (
            not isinstance(status, dict)
            or status.get("value") not in STATUS_VALUES
            or status.get("evidence") not in STATUS_EVIDENCE
            or not isinstance(status.get("evidence_sha256"), str)
            or SHA256.fullmatch(str(status.get("evidence_sha256")).lower()) is None
        ):
            findings.append(f"encounter {position} patient status is not account-backed")
        if not isinstance(codes, dict):
            findings.append(f"encounter {position} code population is unreadable")
            continue
        try:
            icd10 = normalize_codes(codes.get("icd10"), "icd10")
            cpt = normalize_codes(codes.get("cpt", []), "cpt")
            hcpcs = normalize_codes(codes.get("hcpcs", []), "hcpcs")
        except ValueError as error:
            findings.append(f"encounter {position}: {error}")
            continue
        em = codes.get("em")
        if not icd10:
            findings.append(f"encounter {position} has no final ICD-10-CM code")
        if not isinstance(em, str) or not em.strip():
            findings.append(f"encounter {position} has no final E/M code")
            em = ""
        clean_id = encounter_id.strip() if isinstance(encounter_id, str) else ""
        clean_order = order if isinstance(order, int) else 0
        clean_normalized = normalized.lower() if isinstance(normalized, str) else ""
        clean_status = status if isinstance(status, dict) else {}
        encounters.append(
            {
                "id": clean_id,
                "order": clean_order,
                "normalized_sha256": clean_normalized,
                "patient_status": clean_status,
                "setting": setting,
                "codes": {
                    "icd10": icd10,
                    "em": em.strip().upper(),
                    "cpt": cpt,
                    "hcpcs": hcpcs,
                },
            }
        )

    ids = [entry["id"] for entry in encounters]
    if len(set(ids)) != len(ids):
        findings.append("encounter ids are not unique")
    orders = [entry["order"] for entry in encounters]
    expected = list(range(1, len(population) + 1))
    if orders != expected:
        findings.append(f"encounter order is not exactly 1 through {len(population)}")
    return encounters


def validate_icd(
    connection: sqlite3.Connection,
    codes: set[str],
    service_date: str,
    release_page: str,
    findings: list[str],
) -> str:
    token = icd_release_token(connection)
    applicable = applicable_icd_release(release_page, date.fromisoformat(service_date))
    if applicable != token:
        findings.append("ICD-10-CM authoritative release is unread or stale")
    for requested in sorted(codes):
        entry = icd10_lookup.describe(connection, requested)
        if entry is None:
            findings.append(f"ICD-10-CM {requested} is absent from the verified release")
        elif not entry.billable:
            findings.append(f"ICD-10-CM {requested} is not billable on {service_date}")
    return token


def derived_cpt_boundary(source: dict[str, str | None]) -> date:
    effective = date.fromisoformat(str(source["effective_date"]))
    return date(effective.year, 12, 31)


def validate_procedures(
    connection: sqlite3.Connection,
    encounters: list[dict[str, object]],
    service_date: str,
    as_of: date,
    hcpcs_page: str,
    cpt_receipt: dict[str, object],
    findings: list[str],
) -> tuple[dict[str, str | None], dict[str, str | None], Path | None]:
    cpt_source = source_row(connection, "CPT")
    hcpcs_source = source_row(connection, "HCPCS")
    hcpcs_effective = date.fromisoformat(str(hcpcs_source["effective_date"]))
    expected_hcpcs = hcpcs_effective.strftime("%B %Y")
    if current_hcpcs_release(hcpcs_page, as_of) != expected_hcpcs:
        findings.append("HCPCS authoritative release is unread or stale")

    if cpt_receipt.get("schema") != 1:
        findings.append("CPT freshness receipt schema is unreadable")
    if cpt_receipt.get("source_id") != cpt_source["id"]:
        findings.append("CPT freshness receipt names a different source")
    if cpt_receipt.get("source_edition") != cpt_source["edition"]:
        findings.append("CPT freshness receipt names a different edition")
    if cpt_receipt.get("source_sha256") != cpt_source["sha256"]:
        findings.append("CPT source fingerprint changed")
    boundary = derived_cpt_boundary(cpt_source)
    try:
        declared_boundary = date.fromisoformat(str(cpt_receipt.get("valid_through")))
    except ValueError:
        findings.append("CPT freshness receipt has no readable edition boundary")
    else:
        if declared_boundary != boundary:
            findings.append("CPT edition boundary does not match its source")
        if date.fromisoformat(service_date) > boundary:
            findings.append("CPT freshness receipt expired at the next edition boundary")
    if date.fromisoformat(service_date) < date.fromisoformat(str(cpt_source["effective_date"])):
        findings.append("CPT source edition does not cover the service date")

    cpt: set[str] = set()
    hcpcs: set[str] = set()
    for encounter in encounters:
        codes = encounter["codes"]
        assert isinstance(codes, dict)
        em = codes["em"]
        if isinstance(em, str) and em:
            cpt.add(em)
        cpt.update(codes["cpt"])
        hcpcs.update(codes["hcpcs"])

    if cpt:
        edition_year = date.fromisoformat(service_date).year
        selected_sheet = ROOT / "reference" / f"cpt-em-mdm-{edition_year}.md"
        if any(
            str(encounter["codes"]["em"]) not in OFFICE_EM | ED_EM
            for encounter in encounters
        ):
            findings.append("E/M family is outside the supported ED and office MDM sheet")
        try:
            entries = cpt_mdm_sheet.grade(selected_sheet)
            if not entries or any(entry.edition != edition_year for entry in entries.values()):
                raise ValueError("edition does not cover the service date")
            if selected_sheet.name != f"cpt-em-mdm-{edition_year}.md":
                raise ValueError("sheet filename does not match service-date edition")
        except (OSError, ValueError) as error:
            findings.append(f"E/M MDM sheet is missing or invalid: {error}")
    else:
        selected_sheet = None

    for system, population in (("CPT", cpt), ("HCPCS", hcpcs)):
        if population and not procedure_codes_lookup.complete(connection, system):
            findings.append(f"{system} code set is incomplete")
        for requested in sorted(population):
            entry = procedure_codes_lookup.describe(connection, requested)
            if entry is None:
                findings.append(f"{system} {requested} is absent from the verified code set")
            elif entry.system != system:
                findings.append(f"{requested} resolves as {entry.system}, not {system}")
            elif not procedure_codes_lookup.valid_on(entry, service_date):
                findings.append(f"{system} {requested} is not active on {service_date}")

    for encounter in encounters:
        codes = encounter["codes"]
        status = encounter["patient_status"]
        if not isinstance(codes, dict) or not isinstance(status, dict):
            continue
        entry = procedure_codes_lookup.describe(connection, str(codes["em"]))
        if entry is not None and str(codes["em"]) in OFFICE_EM and f"{status.get('value')} patient" not in entry.description.lower():
            findings.append(f"encounter {encounter['id']} E/M code disagrees with patient status")
    return cpt_source, hcpcs_source, selected_sheet


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--cpt-receipt", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--icd-database", type=Path, default=icd10_lookup.DEFAULT_DATABASE)
    parser.add_argument(
        "--procedure-database", type=Path, default=procedure_codes_lookup.DEFAULT_DATABASE
    )
    args = parser.parse_args(argv)

    try:
        args.receipt.unlink(missing_ok=True)
    except OSError as error:
        print(f"coding-freshness: BLOCKED: cannot invalidate old receipt: {error}")
        return 2

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        cpt_receipt = json.loads(args.cpt_receipt.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not isinstance(cpt_receipt, dict):
            raise ValueError("manifest and CPT receipt must each be a JSON object")
        service_date = date.fromisoformat(str(manifest["service_date"])).isoformat()
        icd_page = read_url(ICD_RELEASE_URL)
        hcpcs_page = read_url(HCPCS_RELEASE_URL)
        icd_connection = icd10_lookup.open_database(args.icd_database)
        procedure_connection = procedure_codes_lookup.open_database(args.procedure_database)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"coding-freshness: BLOCKED: {error}")
        return 2

    findings: list[str] = []
    try:
        encounters = read_encounters(manifest, findings)
        icd_codes = {
            code
            for encounter in encounters
            for code in encounter["codes"]["icd10"]
        }
        icd_token = validate_icd(
            icd_connection, icd_codes, service_date, icd_page, findings
        )
        cpt_source, hcpcs_source, selected_sheet = validate_procedures(
            procedure_connection,
            encounters,
            service_date,
            today(),
            hcpcs_page,
            cpt_receipt,
            findings,
        )
    finally:
        icd_connection.close()
        procedure_connection.close()

    if findings:
        for finding in findings:
            print(f"coding-freshness: BLOCKED: {finding}")
        return 1

    receipt = {
        "schema": 1,
        "verdict": "PASS",
        "service_date": service_date,
        "checked_as_of": today().isoformat(),
        "encounters": encounters,
        "sources": {
            "icd10": {
                "release": icd_token,
                "database_sha256": sha256(args.icd_database),
                "authoritative_url": ICD_RELEASE_URL,
            },
            "cpt": {
                "source_id": cpt_source["id"],
                "edition": cpt_source["edition"],
                "source_sha256": cpt_source["sha256"],
                "database_sha256": sha256(args.procedure_database),
                "valid_through": derived_cpt_boundary(cpt_source).isoformat(),
                "mdm_sheet_filename": selected_sheet.name if selected_sheet else None,
                "mdm_sheet_sha256": sha256(selected_sheet) if selected_sheet else None,
            },
            "hcpcs": {
                "source_id": hcpcs_source["id"],
                "edition": hcpcs_source["edition"],
                "source_sha256": hcpcs_source["sha256"],
                "database_sha256": sha256(args.procedure_database),
                "authoritative_url": HCPCS_RELEASE_URL,
            },
        },
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("coding-freshness: PASS")
    return 0


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
