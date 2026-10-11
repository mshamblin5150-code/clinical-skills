"""A synthetic confirmed none context for approval tests unrelated to retrieval."""

from pathlib import Path

import project_context


def write_none_context(run: Path) -> None:
    path = run / project_context.RECORD_NAME
    path.write_text(
        "PROJECT-CONTEXT: none - synthetic approval has no project\n"
        "OWN-SUBMISSION: none - no earlier synthetic submission\n"
        "CONFIRMED: 2001-01-01\n", encoding="utf-8",
    )
    result = project_context.write_record(run)
    if result.exit_code:
        raise AssertionError(result.report)
