"""Supply synthetic coverage records to isolate other grader contracts.

This is test data only. It does not perform a coverage read or prove independent
authorship, blindness, semantic completeness, or the reader's execution order.
The production gate still grades these records normally; its missing, stale,
unanswered and omission controls belong to ``test_element_coverage``.
"""

from hashlib import sha256
import json
from pathlib import Path
import re

import assignment_docx
import file_digest


def write_synthetic_element_coverage(run: Path, artifact: Path) -> None:
    """Bind a simulated reader's one-element record to the current fixture."""
    prompt = "assignment-2099-01-01.md"
    (run / prompt).write_text(
        "Synthetic prompt: include the fixture's content. Assignment points: 10.\n",
        encoding="utf-8",
    )
    (run / "elements.md").write_text(
        "- E1: Include the synthetic fixture content.\n", encoding="utf-8"
    )
    (run / "rubric.json").write_text(json.dumps({
        "assignment_points": "10",
        "criteria": [{"id": "R1", "criterion": "Synthetic content",
                      "descriptor": "Include the synthetic fixture content.", "points": "10"}],
        "points_exception": "",
    }), encoding="utf-8")
    record = {
        "artifact": artifact.name,
        "artifact_sha256": sha256(artifact.read_bytes()).hexdigest(),
        "inputs_sha256": {name: sha256((run / name).read_bytes()).hexdigest()
                          for name in (prompt, "rubric.json", "elements.md", "bar.md")},
        "elements": [{"id": "C1", "requirement": "Include the synthetic fixture content.",
                      "origin": "rubric", "rubric_id": "R1", "status": "answered",
                      "location": "slide 1 face text" if artifact.suffix == ".pptx" else "body paragraph 1",
                      "bar_quote": "", "remark": ""}],
        "reconciliation": [{"draft_id": "E1", "element_ids": ["C1"]}],
    }
    (run / "element-coverage.json").write_text(json.dumps(record), encoding="utf-8")


def finalize_current_docx_fixture(run: Path, artifact: Path) -> None:
    """Explicitly refresh the existing synthetic DOCX reader bindings together.

    The fixture producer supplies its current named heading record and retained
    first-pass fingerprint. This refreshes their hashes, not their observations
    or actual reader evidence, and no grader invokes it automatically.
    """
    heading = run / "heading-read.md"
    fingerprint = run / "render" / "pass-1" / assignment_docx.FINGERPRINT_FILE
    text = heading.read_text(encoding="utf-8")
    digest = file_digest.sha256(artifact)
    updated, count = re.subn(r"(?m)^DRAFT:[^\r\n]*", "DRAFT: " + digest, text)
    if count != 1 or f"## HEADING-READ: {artifact.name}" not in text.splitlines():
        raise ValueError("finalization needs one existing named synthetic heading read")
    if not fingerprint.is_file():
        raise ValueError("finalization needs an existing retained synthetic fingerprint")
    heading.write_text(updated, encoding="utf-8")
    file_digest.write_recorded_sha256(fingerprint, digest)
    write_synthetic_element_coverage(run, artifact)
