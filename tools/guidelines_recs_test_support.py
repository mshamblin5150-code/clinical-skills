"""Synthetic trusted recommendation records for public consumer-seam tests."""

from __future__ import annotations

from copy import deepcopy

import artifact_provenance
import guidelines_recs


ABSENT_SOURCE_SHA256 = "0" * 64


def trust_recommendation_record(
    record: dict,
    *,
    counted_from: str = guidelines_recs.SOURCE_RULED_TABLE,
) -> dict:
    """Return a copy trusted by this checkout, with an intentionally absent PDF."""
    trusted = deepcopy(record)
    trusted.setdefault("source", ".")
    trusted.setdefault("source_sha256", ABSENT_SOURCE_SHA256)
    trusted["counted_from"] = counted_from
    producer = artifact_provenance.current_producer()
    producer["inputs"] = artifact_provenance.producer_file_identity(
        guidelines_recs.RECORD_TRUST_FLOOR[counted_from]
    )
    trusted["producer"] = producer
    return trusted
