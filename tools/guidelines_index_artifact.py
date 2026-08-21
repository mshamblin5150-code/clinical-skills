"""Write cache-specific provenance into a guideline index artifact."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path


def stamp(
    database: Path,
    producer: dict[str, object],
    source: dict[str, object],
) -> None:
    with closing(sqlite3.connect(database)) as connection:
        row = connection.execute(
            "SELECT value FROM meta WHERE key = 'provenance'"
        ).fetchone()
        if row is None:
            raise ValueError("index database has no provenance record")
        provenance = json.loads(row[0])
        if not isinstance(provenance, dict):
            raise ValueError("index provenance is not a JSON object")
        provenance["producer"] = producer
        provenance["source"] = source
        connection.execute(
            "UPDATE meta SET value = ? WHERE key = 'provenance'",
            (json.dumps(provenance, sort_keys=True),),
        )
        connection.commit()
