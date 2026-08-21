"""Write cache-specific provenance into a guideline extraction artifact."""

from __future__ import annotations

import json
from pathlib import Path

import guidelines_extract


def stamp(root: Path, producer: dict[str, object]) -> None:
    path = root / guidelines_extract.MANIFEST_NAME
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("extraction manifest is not a JSON object")
    manifest["producer"] = producer
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
