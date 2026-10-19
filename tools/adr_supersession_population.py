#!/usr/bin/env python3
"""Derive the ADR 0280 ruling 7 citation population, not supersession verdicts.

The union reads literal ``ADR NNNN`` text and ``NNNN-`` record paths in every
numbered Markdown record. Only a later record citing an existing earlier one
creates a pair. A reader classifies those pairs; no verb matcher decides them.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import tarfile
from pathlib import Path

from console_codec import require_python_floor, use_utf8
from markdown_read import paragraphs, unfenced_lines


DECLARED_LIMITS = (
    "A later record overturning an earlier one while naming it in neither "
    "ADR NNNN text nor a NNNN- record path is outside the population.",
    "Whether a citation overturns a ruling, falsifies its ground, completes it, "
    "or merely mentions it is a reader's classification, never a matcher verdict.",
    "Live historical coverage checks pair identities through the report's last ADR; "
    "it does not certify the historical bytes. Use --revision for that binding.",
    "Revision mode checks banner-disposition spelling and class, not the existence "
    "of a retirement banner that may postdate those bytes; live coverage and the "
    "supersession binding check the banner itself.",
)
RECORD = re.compile(r"^(\d{4})-.+\.md$")
TEXT_CITATION = re.compile(r"\bADR\s+(\d{4})\b")
PATH_CITATION = re.compile(r"(?<![\w-])(\d{4})-[\w-]+\.md\b")
CLASSIFICATIONS = frozenset(("overturned", "ground falsified", "neither", "unsure"))
BANNER_DISPOSITION = "adr-0343-banner"


def banner_population(records: dict[str, str]) -> tuple[set[str], set[tuple[str, str]]]:
    """Read banner targets and explicit pair declarations without classifying prose."""
    banners, declarations = set(), set()
    for name, text in records.items():
        text = "\n".join(unfenced_lines(text))
        prefix = re.split(r"^## ", text, maxsplit=1, flags=re.M)[0]
        if any(
            re.match(r"^\*Superseded \d{4}-\d{2}-\d{2}\.\*", paragraph)
            and re.search(r"\bevery ruling\b", paragraph, re.I)
            and re.search(r"\[ADR 0343\]\(0343-[^()\s]+\.md\)\s+ruling \d+", paragraph)
            for _, paragraph in paragraphs(prefix)
        ):
            banners.add(name[:4])
        section = re.search(r"^## Supersedes\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if section:
            declarations.update((name[:4], target) for target in re.findall(
                r"^- \[ADR (\d{4})\]\(\d{4}-[^()\s]+\.md\)", section.group(1), re.M
            ))
    return banners, declarations


def banner_disposition_findings(banners: set[str] | None, declarations, rows) -> list[str]:
    """Check later banner proof only when the supplied population is live."""
    findings = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = (row.get('later'), row.get('earlier'))
        if not all(isinstance(value, str) for value in key):
            findings.append("classification pair IDs must be strings")
            continue
        disposition = row.get('disposition')
        if disposition is not None:
            if (disposition != BANNER_DISPOSITION
                    or row.get('classification') != 'overturned'
                    or (banners is not None and key[1] not in banners)):
                findings.append(f"{key[0]} -> {key[1]}: invalid banner disposition")
        elif banners is not None and key[1] in banners and key not in declarations and row.get('classification') in ('overturned', 'ground falsified'):
            findings.append(f"{key[0]} -> {key[1]}: no declaration or banner disposition")
    return findings


def normalize_legacy_opening(original: str, source: str) -> str | None:
    """Normalize only closed historical marker families, preserving their bodies.

    Unnumbered legacy annotations remain unread, rather than acquiring invented
    ruling coordinates. Prefix-only families retain every original character;
    the exception validator independently binds the whole original to history.
    """
    old = re.match(r"^\*Superseded(?: [^*\n]*?)? (\d{4}-\d{2}-\d{2})\.\*", original)
    if old:
        return f"*Superseded {old.group(1)}.*" + original[old.end():]
    families = (
        r"^\*\*Superseded by \[ADR 0187\]",
        r"^Superseded in part, \d{4}-\d{2}-\d{2}: ADR 0187 ruling 14",
        r"^\*\*The key gained a third component on \d{4}-\d{2}-\d{2}",
        r"^\*\(Superseded the same day\. Both were read and both take it",
        r"^## Superseded in part by ADR 0216, \d{4}-\d{2}-\d{2}$",
        r"^\*\(Corrected in place \d{4}-\d{2}-\d{2}, per ADR 0016\. This note held while `written-before-publish`",
    )
    subject_amendment = (
        re.match(r"^\*\(Corrected in place \d{4}-\d{2}-\d{2}, on \[ADR 0016\]", original) is not None
        and "ADR 0102 and #689 added the registry's authored `subject` column after this row was ratified." in original
    )
    if not subject_amendment and not any(re.match(pattern, original) for pattern in families):
        return None
    dated = re.search(r"\b\d{4}-\d{2}-\d{2}\b", original)
    if dated is None:
        dated = re.search(r"Superseded in part, (\d{4}-\d{2}-\d{2}): ADR 0187 ruling 14", source)
        if dated is None:
            return None
        day = dated.group(1)
    else:
        day = dated.group()
    return f"*Superseded {day}.* " + original


def legacy_marker_findings(report: dict, records: dict[str, str], *, root: Path | None = None) -> tuple[list[str], set[tuple[str, str]]]:
    """Validate exact historical markers that remain explicitly unattributed.

    Source bytes bind to the report's immutable manifest. When the commit is
    available, Git independently verifies those bytes; shallow checkouts rely
    on the committed manifest and retained source, not on live source bytes.
    These entries remain unread coverage and discharge no declaration.
    """
    from adr_read import ruling_attributions
    from markdown_read import paragraphs, unfenced_lines

    findings = []
    allowed = set()
    rows = report.get("unresolved_legacy_markers", [])
    if not isinstance(rows, list):
        return ["unresolved legacy markers is not a list"], allowed
    manifest = {row.get("path"): row.get("sha256") for row in report.get("records", []) if isinstance(row, dict)}
    revision = report.get("revision", "")
    historical = None
    if rows and re.fullmatch(r"[0-9a-f]{40}", str(revision)) is None:
        findings.append("legacy markers need an immutable historical revision")
    if root is not None and rows:
        available = subprocess.run(["git", "cat-file", "-e", f"{revision}^{{commit}}"], cwd=root, capture_output=True)
        if available.returncode == 0:
            historical = revision
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            findings.append("legacy marker entry is not an object")
            continue
        name = row.get("record")
        original = row.get("original_marker")
        normalized = row.get("normalized_marker")
        source = row.get("source_text")
        valid = True
        def refuse(reason):
            nonlocal valid
            valid = False
            findings.append(f"{name}: unresolved legacy marker {reason}")
        if not all(isinstance(value, str) and value for value in (name, original, normalized, source)):
            refuse("has missing text fields")
            continue
        key = (name, normalized)
        if key in seen:
            refuse("is duplicated")
        seen.add(key)
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if digest != row.get("source_sha256") or digest != manifest.get(name):
            refuse("source differs from historical manifest")
        if historical:
            measured = subprocess.run(["git", "show", f"{historical}:docs/adr/{name}"], cwd=root, capture_output=True)
            if measured.returncode or measured.stdout != source.encode("utf-8"):
                refuse("source differs from historical Git bytes")
        paragraph_source = source.replace("\r\n", "\n")
        expected_normalization = normalize_legacy_opening(original, paragraph_source)
        if expected_normalization is None or original not in paragraph_source:
            refuse("has no exact historical supersession opening")
        elif normalized != expected_normalization:
            refuse("changes more than the opening")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            refuse("has no reason")
        if type(row.get("follow_up")) is not int or row["follow_up"] <= 0:
            refuse("has no follow-up ticket")
        text = "\n".join(unfenced_lines(records.get(name, "")))
        contexts = {item.line: item.number for item in ruling_attributions(text)}
        matches = [(line, paragraph) for line, paragraph in paragraphs(text) if paragraph == normalized]
        if len(matches) != 1:
            refuse("does not match one exact live paragraph")
        elif contexts.get(matches[0][0]) is not None:
            refuse("has an attributable ruling and cannot be exempted")
        if valid:
            allowed.add(key)
    return findings, allowed


def derive_records(sources: list[tuple[str, bytes | Exception]]) -> dict:
    """Derive pairs from an independently supplied numbered record population."""
    records = []
    unread = []
    texts = {}
    identities = {}
    for name, source in sorted(sources, key=lambda entry: entry[0]):
        match = RECORD.fullmatch(name)
        if match is None:
            continue
        number = match.group(1)
        if number in identities:
            unread.append({"path": name, "reason": "duplicate ADR number"})
            continue
        identities[number] = name
        try:
            if isinstance(source, Exception):
                raise source
            data = source
            text = data.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            unread.append({"path": name, "reason": str(exc)})
            continue
        records.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
        texts[number] = text
    pairs = []
    for later, text in sorted(texts.items()):
        cited = {}
        for form, pattern in (("text", TEXT_CITATION), ("path", PATH_CITATION)):
            for match in pattern.finditer(text):
                earlier = match.group(1)
                if earlier not in identities or int(earlier) >= int(later):
                    continue
                entry = cited.setdefault(earlier, {"forms": set(), "lines": set()})
                entry["forms"].add(form)
                entry["lines"].add(text.count("\n", 0, match.start()) + 1)
        for earlier, evidence in sorted(cited.items()):
            pairs.append({
                "later": later, "earlier": earlier,
                "later_path": identities[later], "earlier_path": identities[earlier],
                "forms": sorted(evidence["forms"]),
                "citation_lines": sorted(evidence["lines"]),
            })
    binding = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    banners, declarations = banner_population({identities[number]: text for number, text in texts.items()})
    return {
        "schema": 1,
        "records_read": len(records), "distinct_pairs": len(pairs),
        "unread_remainder": unread, "declared_limits": list(DECLARED_LIMITS),
        "records_sha256": hashlib.sha256(binding).hexdigest(),
        "records": records, "pairs": pairs,
        "banner_records": sorted(banners), "declaration_pairs": sorted(declarations),
    }


def derive_population(directory: Path) -> dict:
    """Read working-tree record bytes, preserving every failed read as unread."""
    sources = []
    for path in sorted(directory.glob("*.md")):
        try:
            source = path.read_bytes()
        except OSError as exc:
            source = exc
        sources.append((path.name, source))
    return derive_records(sources)


def derive_revision(root: Path, revision: str) -> dict:
    """Read immutable Git bytes without touching the working-tree records.

    A missing commit in a shallow checkout is an error, never a live fallback.
    """
    commit = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"], cwd=root,
        check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    archive = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "archive", "--format=tar", commit, "docs/adr"], cwd=root,
        check=True, capture_output=True,
    ).stdout
    sources = []
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream.getmembers():
            path = Path(member.name)
            if member.isfile() and path.parent.as_posix() == "docs/adr":
                content = stream.extractfile(member)
                if content is not None:
                    sources.append((path.name, content.read()))
    population = derive_records(sources)
    population["revision"] = commit
    return population


def classification_findings(population: dict, classification: dict, *, historical_coverage=False) -> list[str]:
    """Bind a reader's complete classification to the current record bytes."""
    findings = []
    if historical_coverage:
        through = classification.get("through")
        if not isinstance(through, str) or re.fullmatch(r"\d{4}", through) is None:
            return ["historical classification needs a four-digit through ADR"]
        if re.fullmatch(r"[0-9a-f]{40}", str(classification.get("revision", ""))) is None:
            findings.append("historical classification needs an immutable commit revision")
    elif classification.get("records_sha256") != population["records_sha256"]:
        findings.append("classification record digest differs from the current population")
    if not historical_coverage and population.get("revision") != classification.get("revision"):
        findings.append("classification revision differs from the derived population")
    expected = {
        (pair["later"], pair["earlier"]) for pair in population["pairs"]
        if not historical_coverage or pair["later"] <= through
    }
    seen = set()
    rows = classification.get("pairs")
    if not isinstance(rows, list):
        return findings + ["classification pairs is not a list"]
    for row in rows:
        if not isinstance(row, dict):
            findings.append("classification row is not an object")
            continue
        key = (row.get("later"), row.get("earlier"))
        if not all(isinstance(value, str) for value in key):
            findings.append("classification pair IDs must be strings")
            continue
        if key in seen:
            findings.append(f"duplicate classification: {key[0]} -> {key[1]}")
        seen.add(key)
        if key not in expected:
            findings.append(f"extra classification: {key[0]} -> {key[1]}")
        if row.get("classification") not in CLASSIFICATIONS:
            findings.append(f"unread classification: {key[0]} -> {key[1]}")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            findings.append(f"classification has no reason: {key[0]} -> {key[1]}")
        evidence = row.get("evidence")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(item, str) or not item.strip() for item in evidence
        ):
            findings.append(f"classification has no evidence quotes: {key[0]} -> {key[1]}")
    for later, earlier in sorted(expected - seen):
        findings.append(f"missing classification: {later} -> {earlier}")
    findings.extend(banner_disposition_findings(
        None if population.get('revision') is not None else set(population.get('banner_records', [])),
        {tuple(pair) for pair in population.get('declaration_pairs', [])}, rows,
    ))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parents[1] / "docs" / "adr")
    parser.add_argument("--json", type=Path, help="write the derived population as JSON")
    parser.add_argument("--classifications", type=Path, help="check a digest-bound classification JSON")
    parser.add_argument("--revision", help="derive from this immutable Git revision instead of live files")
    parser.add_argument("--historical-coverage", action="store_true", help="check live pair coverage through a historical report's through ADR, without certifying its historical bytes")
    args = parser.parse_args(argv)
    if not args.directory.is_dir():
        parser.error(f"ADR directory does not exist: {args.directory}")
    if args.historical_coverage and (not args.classifications or args.revision):
        parser.error("--historical-coverage requires --classifications and live records")
    try:
        population = derive_revision(Path(__file__).resolve().parents[1], args.revision) if args.revision else derive_population(args.directory)
    except subprocess.CalledProcessError as exc:
        print(f"Unread revision: {args.revision}; Git could not read the historical records ({exc.returncode})")
        return 2
    print(f"Records read: {population['records_read']}")
    print(f"Distinct pairs: {population['distinct_pairs']}")
    print(f"Unread remainder: {len(population['unread_remainder'])}")
    for limit in DECLARED_LIMITS:
        print(f"Floor: {limit}")
    for entry in population["unread_remainder"]:
        print(f"Unread: {entry['path']}: {entry['reason']}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(population, indent=2) + "\n", encoding="utf-8")
    findings = []
    if args.classifications:
        try:
            classification = json.loads(args.classifications.read_text(encoding="utf-8"))
            if not isinstance(classification, dict):
                raise ValueError("classification root is not an object")
            findings = classification_findings(population, classification, historical_coverage=args.historical_coverage)
            if args.historical_coverage:
                live_texts = {path.name: path.read_text(encoding="utf-8") for path in args.directory.glob("[0-9][0-9][0-9][0-9]-*.md")}
                legacy_findings, _ = legacy_marker_findings(classification, live_texts, root=Path(__file__).resolve().parents[1])
                findings.extend(legacy_findings)
        except (OSError, ValueError) as exc:
            findings = [str(exc)]
        for finding in findings:
            print(f"Finding: {finding}")
        if not findings:
            unsure = sum(row["classification"] == "unsure" for row in classification["pairs"])
            print(f"Classified pairs: {len(classification['pairs'])}")
            print(f"Unsure remainder: {unsure}")
            print(f"Unattributed legacy markers, unread: {len(classification.get('unresolved_legacy_markers', []))}")
    return int(bool(population["unread_remainder"] or findings))


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main())
