"""Public-contract tests for the per-checkout tracker hook marker."""

from __future__ import annotations

from datetime import date as CalendarDate
import json
from pathlib import Path
import tempfile
import unittest

import tracker_publish_marker as marker
import artifact_lock_test_support  # noqa: F401


class PerCheckoutMarker(unittest.TestCase):
    def test_two_checkout_identities_write_distinct_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runs = root / "scratch" / "runs"
            first_module = root / "first" / "tools" / "tracker_publish_marker.py"
            second_module = root / "second" / "tools" / "tracker_publish_marker.py"

            first = marker.write_marker(
                module_file=first_module,
                runs_root=runs,
                today=CalendarDate(2026, 9, 14),
            )
            second = marker.write_marker(
                module_file=second_module,
                runs_root=runs,
                today=CalendarDate(2026, 9, 15),
            )

            self.assertNotEqual(first, second)
            self.assertEqual(first.parent, second.parent)
            self.assertEqual(
                json.loads(first.read_text(encoding="utf-8")),
                {"ran_on": "2026-09-14", "version": 2},
            )
            self.assertEqual(
                json.loads(second.read_text(encoding="utf-8")),
                {"ran_on": "2026-09-15", "version": 2},
            )


if __name__ == "__main__":
    unittest.main()
