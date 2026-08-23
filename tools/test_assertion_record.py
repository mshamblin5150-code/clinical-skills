"""Exercise the shared grammar for assertion-record row identifiers."""

from __future__ import annotations

import unittest

from assertion_record import ROW_ID


class AssertionRecordRowIdentifiers(unittest.TestCase):
    """The grammar reads cell zero and accepts every declared row shape."""

    def test_latent_identifier_shapes_are_read(self) -> None:
        table = """\
| Identifier | Verdict |
| --- | --- |
| Z1 | PASS |
| A123 | FAIL |
|   P4   | PASS |
"""

        self.assertEqual(ROW_ID.findall(table), ["Z1", "A123", "P4"])

    def test_non_row_text_is_not_read(self) -> None:
        self.assertEqual(ROW_ID.findall("The assertion mentions | A1 | inline."), [])


if __name__ == "__main__":
    unittest.main()
