"""Give every lock-bearing test process one private artifact-lock root."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


_ROOT_VARIABLE = "CLINICAL_SKILLS_LOCK_ROOT"
_GENERATED_ROOT_VARIABLE = "CLINICAL_SKILLS_TEST_LOCK_ROOT"
_INHERITED_ROOT = os.environ.get(_ROOT_VARIABLE)
_GENERATED_ROOT = os.environ.get(_GENERATED_ROOT_VARIABLE)
if _INHERITED_ROOT and _INHERITED_ROOT != _GENERATED_ROOT:
    _TEMPORARY_ROOT = None
    LOCK_ROOT = Path(_INHERITED_ROOT).resolve()
else:
    _TEMPORARY_ROOT = tempfile.TemporaryDirectory(
        prefix="clinical-skills-test-locks-"
    )
    LOCK_ROOT = Path(_TEMPORARY_ROOT.name).resolve()
    os.environ[_ROOT_VARIABLE] = str(LOCK_ROOT)
    os.environ[_GENERATED_ROOT_VARIABLE] = str(LOCK_ROOT)
