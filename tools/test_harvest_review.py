"""Tests for the unruled-harvest review tool.

phi-scan: synthetic

Every name below is invented, and no test here reads scratch/ -- the extractors
are handed literal index records, the way test_corpus_census works. A test that
read the real corpus would pass for two reasons, one of them being that the
corpus happens to suit it.
"""

import unittest

import harvest_review as hr
import phi_scan as ps


def entry(name, window, file="day-01.txt"):
    return {"name": name, "win": list(window), "file": file}


# win[0] is the name's own line; win[1..3] is the shorthand that follows.
JORDAN = entry("Jordan Vance", ["Jordan Vance", "reaction latex", "hr 82", "denies fever"])
PRIYA = entry("Priya Raman", ["Priya Raman", "reaction latex", "Ellery Voss", "bp 118/70"],
              file="day-02.txt")


class UnruledNames(unittest.TestCase):
    """Which harvested strings land in front of a human, and which do not."""

    def unruled(self, entries, reviewed=()):
        return ps.unreviewed_names(entries, set(reviewed))

    def test_a_name_field_string_is_never_unruled(self):
        self.assertNotIn("Jordan Vance", self.unruled([JORDAN]))

    def test_a_window_zero_string_is_never_unruled(self):
        """Position 0 is the name's own line, so it carries its own evidence."""
        only_win = {"name": "", "win": ["Ellery Voss", "hr 82", "x", "y"]}
        self.assertNotIn("Ellery Voss", self.unruled([only_win]))

    def test_a_later_window_string_is_unruled(self):
        self.assertIn("reaction latex", self.unruled([JORDAN]))

    def test_a_string_in_a_name_position_anywhere_is_not_unruled(self):
        """`Ellery Voss` sits at win[2] under Priya, which alone would list it.

        It is also the name field of its own entry, and that outranks position:
        the index vouches for it somewhere, so it is not in dispute.
        """
        elsewhere = entry("Ellery Voss", ["Ellery Voss", "cough x3d", "a", "b"])
        self.assertIn("Ellery Voss", self.unruled([PRIYA]))
        self.assertNotIn("Ellery Voss", self.unruled([PRIYA, elsewhere]))

    def test_the_ledger_removes_a_string(self):
        self.assertNotIn("reaction latex",
                         self.unruled([JORDAN], reviewed={"reaction latex"}))

    def test_the_ledger_is_case_insensitive_like_the_match(self):
        self.assertNotIn("reaction latex",
                         self.unruled([JORDAN], reviewed={"REACTION LATEX"}))

    def test_an_allowlisted_string_is_not_unruled(self):
        """Already decided -- it is in NOT_NAMES, so it is not scanned for."""
        self.assertNotIn("allergies nkda", self.unruled(
            [entry("Jordan Vance", ["Jordan Vance", "allergies nkda", "a", "b"])]))

    def test_a_string_too_short_to_be_scanned_is_not_unruled(self):
        """The length floor runs first, so it is not refusing anything either."""
        self.assertNotIn("ab cd", self.unruled(
            [entry("Jordan Vance", ["Jordan Vance", "ab cd", "a", "b"])]))

    def test_a_non_name_shaped_line_never_enters_the_harvest(self):
        self.assertNotIn("bp 118/70", self.unruled([PRIYA]))


class Sightings(unittest.TestCase):
    def test_one_sighting_per_appearance_not_per_string(self):
        """Two patients sharing a phrase is the evidence it is vocabulary, and
        collapsing the sightings is exactly what would hide it."""
        found = hr.sightings([JORDAN, PRIYA], {"reaction latex"})
        self.assertEqual([s.source for s in found], ["day-01.txt", "day-02.txt"])

    def test_a_sighting_carries_its_whole_window(self):
        found = hr.sightings([JORDAN], {"reaction latex"})
        self.assertEqual(found[0].position, 1)
        self.assertEqual(found[0].window, tuple(JORDAN["win"]))

    def test_nothing_unruled_yields_no_sightings(self):
        self.assertEqual(hr.sightings([JORDAN, PRIYA], set()), [])


class Rendering(unittest.TestCase):
    def render(self, entries, unruled):
        return hr.render(hr.sightings(entries, unruled), unruled)

    def test_it_says_the_output_is_phi(self):
        self.assertIn("Do not paste", self.render([JORDAN], {"reaction latex"}))

    def test_it_shows_the_string_and_its_context(self):
        out = self.render([JORDAN], {"reaction latex"})
        self.assertIn("'reaction latex'", out)
        self.assertIn("denies fever", out)      # a neighbouring line
        self.assertIn("    > reaction latex", out)  # the disputed line, marked

    def test_a_clean_review_says_so_and_offers_nothing_to_paste(self):
        out = self.render([JORDAN], set())
        self.assertIn("nothing unruled", out)
        self.assertNotIn("NOT_NAMES", out)

    def test_it_states_that_doing_nothing_keeps_the_refusal(self):
        """The fail-safe default is the property worth asserting: an abandoned
        review must leave the firewall at full strength."""
        self.assertIn("keeps refusing", self.render([JORDAN], {"reaction latex"}))

    def test_a_string_with_no_window_is_reported_rather_than_dropped(self):
        """The index is a scratch artifact with no generator in this repo, so a
        string can be unruled with nothing to show. Silently listing fewer than
        the stated count would be the worst outcome."""
        out = self.render([JORDAN], {"reaction latex", "ghost phrase"})
        self.assertIn("1 with no window to show", out)
        self.assertIn("'ghost phrase'", out)

    def test_the_paste_ready_ledger_holds_every_unruled_string(self):
        out = self.render([JORDAN, PRIYA], {"reaction latex", "Ellery Voss"})
        self.assertIn('"reaction latex"', out)
        self.assertIn('"Ellery Voss"', out)


if __name__ == "__main__":
    unittest.main()
