"""Contract tests for ADR number allocation and its declared boundary. #831."""

from __future__ import annotations

import unittest

import adr_next


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_the_test_suite_names_the_declared_limits_object(self):
        self.assertTrue(adr_next.DECLARED_LIMITS)
        self.assertTrue(
            all(isinstance(limit, str) and limit for limit in adr_next.DECLARED_LIMITS)
        )


if __name__ == "__main__":
    unittest.main()
