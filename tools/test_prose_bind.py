"""Contract checks for issue #412's prose assertion helper."""

import unittest

from prose_bind import ProseBind


class ProseAssertionsNormalizeBothSides(ProseBind, unittest.TestCase):
    def test_assert_prose_in_reads_across_hard_wraps_and_literal_glue(self):
        self.assertProseIn(
            'a phrase split across two adjacent string literals',
            'a phrase split across two adjacent "string"\n"literals"',
        )

    def test_assert_prose_not_in_fails_when_only_formatting_differs(self):
        with self.assertRaises(AssertionError):
            self.assertProseNotIn(
                "a retired clinician ruling",
                "a retired clinician\n'ruling'",
            )

    def test_the_needle_is_normalized_too(self):
        self.assertProseIn(
            "the needle is\n**hard wrapped**",
            "the needle is hard wrapped",
        )

    def test_a_prose_line_population_is_one_haystack(self):
        with self.assertRaises(AssertionError):
            self.assertProseNotIn(
                "a retired clinician ruling",
                ["a retired clinician", "ruling"],
            )


if __name__ == "__main__":
    unittest.main()
