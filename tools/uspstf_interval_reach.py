"""Measure the sentence-level reach ruled permanent by ADR 0028.

The committed USPSTF table derives ``interval`` from one recommendation statement.
This maintainer-only instrument asks what the documents in that table's ``not stated``
population contain outside those statements. It reports counts only: the guideline
corpus stays outside the repo and no source text crosses this command boundary.

The broad whole-document read and the two narrower reads are measurements, not
production parsers. The narrower reads are deliberately declined discriminators whose
false positives are part of ADR 0028's ruling. They live here so a corpus refresh or a
change to ``uspstf_table.INTERVAL_PHRASE`` can re-run the question without quietly
turning either discriminator into a live derivation rule.

Usage::

    python tools/uspstf_interval_reach.py C:/codeing/guidelines-text
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import artifact_provenance
import guidelines_recs
from console_codec import use_utf8
from guidelines_manifest import read_or_raise
from uspstf_table import INTERVAL_ABSENCES, INTERVAL_PHRASE, normalize, split_sentences


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TABLE = REPO_ROOT / "reference" / "guidelines-uspstf.md"
NOT_STATED = "not stated"

# Declined discriminator 1: the standalone section heading through the next section.
# These stops are the section forms met by this region across the USPSTF corpus. The
# matcher is intentionally narrow: widening it is the rejected proposal this module
# measures, not a production capability to improve speculatively.
SCREENING_INTERVAL_REGION = re.compile(
    r"^[ \t]*Screening Intervals?[ \t]*\n"
    r"(?P<body>.*?)"
    r"(?=^[ \t]*(?:(?:Treatment|Preventive Interventions|Screening Implementation|"
    r"Implementation|Suggestions for Practice|Additional Tools and Resources)"
    r"(?: or Interventions?)?|Figure\.)[^\n]*$|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

# Declined discriminator 2: a deliberately naive grammatical-attribution proxy. It
# admits adjective and neighboring-society false positives; those are the measurement's
# finding. Tightening the proxy into a production rule is what ADR 0028 declines.
ATTRIBUTED_RECOMMENDATION = re.compile(
    r"\b(?:USPSTF|Preventive Services Task Force)\W+(?:now\W+)?"
    r"(?:recommended|recommends|suggested|suggests)\b",
    re.IGNORECASE,
)
UNHEDGED_RECOMMENDATION = re.compile(
    r"\bUSPSTF\W+(?:now\W+)?(?:recommends|suggests)\b",
    re.IGNORECASE,
)
NAIVE_ABSENCE = re.compile(
    r"\bfound no evidence\b.{0,160}\b(?:screening )?(?:intervals?|frequency)\b",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class TableRow:
    filename: str
    interval: str
    statement: str


@dataclass(frozen=True)
class Measurement:
    rows: int
    not_stated_rows: int
    files_with_not_stated: int
    files_all_not_stated: int
    naive_files: int
    region_files: int
    attributed_files: int
    unhedged_files: int
    naive_absence_files: int
    committed_absence_files: int


def interval_phrases(text: str) -> frozenset[str]:
    """Distinct service-interval phrases recognized by the production vocabulary."""
    return frozenset(match.group(0).casefold() for match in INTERVAL_PHRASE.finditer(text))


def declined_region_phrases(text: str) -> frozenset[str]:
    """Phrases reached by the declined ``Screening Interval(s)`` region rule."""
    return frozenset(
        phrase
        for match in SCREENING_INTERVAL_REGION.finditer(text)
        for phrase in interval_phrases(match.group("body"))
    )


def _attributed_phrases(text: str, attribution: re.Pattern[str]) -> frozenset[str]:
    normalized = normalize(text)
    return frozenset(
        phrase
        for sentence in split_sentences(normalized)
        if attribution.search(sentence)
        for phrase in interval_phrases(sentence)
    )


def _new_phrases(found: frozenset[str], statements: tuple[str, ...]) -> frozenset[str]:
    stated = frozenset(
        phrase for statement in statements for phrase in interval_phrases(statement)
    )
    return found - stated


def measure(rows: tuple[TableRow, ...], documents: dict[str, str]) -> Measurement:
    """Count each declined read over the table's file population."""
    target_rows = tuple(row for row in rows if row.interval == NOT_STATED)
    target_files = {row.filename for row in target_rows}
    missing = sorted(target_files - documents.keys())
    if missing:
        raise ValueError(
            "extracted corpus is missing USPSTF table files: " + ", ".join(missing)
        )

    rows_by_file: dict[str, list[TableRow]] = {}
    for row in rows:
        rows_by_file.setdefault(row.filename, []).append(row)

    naive_files = region_files = attributed_files = unhedged_files = 0
    for filename in sorted(target_files):
        text = documents[filename]
        # "New" is relative to every recommendation statement the file contributed,
        # not only to its ``not stated`` rows. A file can carry both kinds; comparing
        # only the target rows would count a phrase the table already represents.
        statements = tuple(row.statement for row in rows_by_file[filename])
        naive_files += bool(_new_phrases(interval_phrases(text), statements))
        region_files += bool(_new_phrases(declined_region_phrases(text), statements))
        attributed_files += bool(
            _new_phrases(_attributed_phrases(text, ATTRIBUTED_RECOMMENDATION), statements)
        )
        unhedged_files += bool(
            _new_phrases(_attributed_phrases(text, UNHEDGED_RECOMMENDATION), statements)
        )

    absence_candidates = {
        filename
        for filename, text in documents.items()
        if NAIVE_ABSENCE.search(normalize(text))
    }
    committed_absences = {entry.filename for entry in INTERVAL_ABSENCES}

    return Measurement(
        rows=len(rows),
        not_stated_rows=len(target_rows),
        files_with_not_stated=len(target_files),
        files_all_not_stated=sum(
            all(row.interval == NOT_STATED for row in file_rows)
            for file_rows in rows_by_file.values()
        ),
        naive_files=naive_files,
        region_files=region_files,
        attributed_files=attributed_files,
        unhedged_files=unhedged_files,
        naive_absence_files=len(absence_candidates),
        committed_absence_files=len(absence_candidates & committed_absences),
    )


def read_table(path: Path) -> tuple[TableRow, ...]:
    grouped = guidelines_recs.parse_curated_table(path.read_text(encoding="utf-8"))
    return tuple(
        TableRow(row.filename, row.interval, row.statement)
        for group in grouped.values()
        for row in group
    )


def read_documents(
    source: Path,
    *,
    expected_commit: str,
    allow_untrusted_provenance: bool = False,
) -> dict[str, str]:
    handoff = read_or_raise(
        source,
        expected_commit=expected_commit,
        allow_untrusted_provenance=allow_untrusted_provenance,
    )
    documents: dict[str, str] = {}
    for doc_id, document in handoff.documents.items():
        if document.society != "USPSTF":
            continue
        filename = Path(document.source).name
        if filename in documents:
            raise ValueError(f"duplicate USPSTF source filename: {filename}")
        documents[filename] = "\n".join(handoff.pages[doc_id])
    return documents


def render(measurement: Measurement) -> str:
    file_population = measurement.files_with_not_stated
    return "\n".join(
        (
            f"recommendation rows: {measurement.rows}",
            f"not stated rows: {measurement.not_stated_rows}",
            f"files carrying at least one: {file_population}",
            f"files where every row is one: {measurement.files_all_not_stated}",
            f"naive whole-document phrase: {measurement.naive_files} of {file_population}",
            f"declined Screening Interval region: {measurement.region_files} of {file_population}",
            f"declined attributed sentence: {measurement.attributed_files} of {file_population}",
            f"declined attributed sentence, unhedged: {measurement.unhedged_files} of {file_population}",
            f"naive interval-evidence absence candidates: {measurement.naive_absence_files}",
            "candidates already in the committed reading: "
            f"{measurement.committed_absence_files} of {measurement.naive_absence_files}",
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "source", type=Path, help="directory holding extracted text and manifest"
    )
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument(
        "--allow-untrusted-provenance",
        action="store_true",
        help=(
            "read a dirty, foreign, or unstamped extracted corpus; "
            f"{artifact_provenance.FLAG_HELP_EFFECT}"
        ),
    )
    args = parser.parse_args(argv)
    expected_commit = artifact_provenance.checkout_commit(REPO_ROOT)
    try:
        rows = read_table(args.table)
        documents = read_documents(
            args.source,
            expected_commit=expected_commit,
            allow_untrusted_provenance=args.allow_untrusted_provenance,
        )
        result = measure(rows, documents)
    except (OSError, ValueError, guidelines_recs.DidNotScan) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(render(result))
    return 0


if __name__ == "__main__":
    use_utf8()
    sys.exit(main())
