"""Isolate the pre-existing approval checks from the separately tested builder seam.

These fixtures deliberately keep their raw note identities so their coverage,
whole-reply, coding-remark and entry-grammar controls stay independent of the
manifest producer. test_manifest_approval drives the real binding instead.
"""

from types import SimpleNamespace
from unittest import mock

import approval_record


def isolate_manifest_binding(test):
    bindings = {}

    def bound(run, skill, sources):
        if skill in approval_record.CLINICAL_SKILLS:
            bindings[(run, skill)] = SimpleNamespace(
                sources=sources, notes=sources, source_times=sources)
        return sources, sources, sources

    for name, replacement in (
        ("_bound_sources", bound),
        ("_clinical_binding", lambda run, skill: bindings[(run, skill)]),
    ):
        patch = mock.patch.object(approval_record, name, side_effect=replacement)
        patch.start()
        test.addCleanup(patch.stop)
