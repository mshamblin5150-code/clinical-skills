"""Give every lock-bearing test process one private artifact-lock root."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


_INHERITED_ROOT = os.environ.get("CLINICAL_SKILLS_LOCK_ROOT")
if _INHERITED_ROOT:
    _TEMPORARY_ROOT = None
    LOCK_ROOT = Path(_INHERITED_ROOT).resolve()
else:
    _TEMPORARY_ROOT = tempfile.TemporaryDirectory(
        prefix="clinical-skills-test-locks-"
    )
    LOCK_ROOT = Path(_TEMPORARY_ROOT.name).resolve()
    os.environ["CLINICAL_SKILLS_LOCK_ROOT"] = str(LOCK_ROOT)
