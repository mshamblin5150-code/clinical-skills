#!/usr/bin/env python3
"""Dispatch one course-assignment grade through its signed artifact branch.

The shared completion rows' ceilings belong to
``voice_model_identity.DECLARED_LIMITS`` and
``voice_read.DECLARED_LIMITS`` and
``project_context.DECLARED_LIMITS``; this dispatcher copies no row.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import assignment_bar
import aar_scan
import run_grader
import voice_model_identity
import voice_read
import project_context
from console_codec import require_python_floor, use_utf8


EXPECTED_COMPLETION_CHECKS = (
    aar_scan.EXPECTED_ROW,
    voice_model_identity.EXPECTED_ROW,
    voice_read.EXPECTED_ROW,
    voice_read.PROFANITY_EXPECTED_ROW,
    project_context.EXPECTED_ROW,
)


def _import_adapter(name: str) -> ModuleType:
    return importlib.import_module(name)


def _adapter_arguments(argv: list[str], artifact: str) -> list[str]:
    if "--artifact" not in argv:
        raise run_grader.SourceError("--artifact needs the assignment artifact file")
    index = argv.index("--artifact")
    if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
        raise run_grader.SourceError("--artifact needs the assignment artifact file")
    option = "--pptx" if artifact == "deck" else "--docx"
    return [*argv[:index], option, argv[index + 1], *argv[index + 2 :]]


def main(argv: list[str]) -> int:
    try:
        if not argv or argv[0].startswith("--"):
            raise run_grader.SourceError("course_assignment_scan.py needs a run directory")
        run = Path(argv[0])
        envelope = assignment_bar.parse((run / "bar.md").read_text(encoding="utf-8"))
        adapter = _import_adapter(assignment_bar.adapter_name(envelope))
        if "--bar-only" in argv:
            if argv != [argv[0], "--bar-only"]:
                raise run_grader.SourceError("--bar-only accepts no artifact or grader options")
            adapter.validate_bar(envelope)
            print(f"assignment bar: clean - {envelope.artifact}")
            return 0
        return adapter.main(_adapter_arguments(argv, envelope.artifact), envelope=envelope)
    except (OSError, UnicodeError, run_grader.SourceError) as failure:
        print(f"run not scanned: {failure}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    use_utf8()
    require_python_floor()
    raise SystemExit(main(sys.argv[1:]))
