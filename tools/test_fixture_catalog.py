"""Gate ``fixtures/README.md``'s ``Sets`` catalog against every assertion set.

Issue #202 copies #143's hybrid: glob ``fixtures/*/assertions.md`` for the
population, explicitly declare each member's row prefixes, and fail until a new
member is declared. Population and coverage are separate ratchets, because a
set with no row identifiers would otherwise satisfy a per-row check vacuously.

The ``Last run`` denominator is current unless explicitly historical. Issue
#159 is the exception: day-a holds 35 rows now, but its catalog correctly keeps
run 2's historical ``31 of 34``. Never-run sets carry no fraction. This gate
binds only the denominator, not the numerator or the sentence around it.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import NamedTuple

from assertion_record import ROW_ID

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "fixtures"
FIXTURES_README = FIXTURES / "README.md"

SET_LINK = re.compile(r"^\[([a-z0-9-]+)\]\([^)]*/assertions\.md\)$")
ROW_TOTAL = re.compile(
    r"\b(?:\d+|[a-z]+(?:-[a-z]+)?) of "
    r"(?P<total>\d+|[a-z]+(?:-[a-z]+)?) rows\b",
    re.I,
)

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}


class SetDeclaration(NamedTuple):
    """One set's row grammar and catalog-denominator policy."""

    prefixes: frozenset[str]
    has_run: bool
    historical_denominator: int | None = None


# The glob discovers the population; this map declares how each discovered
# member is read. Only day-a is historical: #159 appended unscored F8 after
# run 2, and the clinician ruled that 31 of 34 must not become 31 of 35.
SET_DECLARATIONS = {
    "day-a": SetDeclaration(frozenset("ADFR"), True, 34),
    "day-b": SetDeclaration(frozenset("BCDGR"), True),
    "peds-bp": SetDeclaration(frozenset("DPR"), True),
    "obesity-bmi": SetDeclaration(frozenset("O"), False),
    "filled-anchor": SetDeclaration(frozenset("ACFR"), True),
    "hedged-dx": SetDeclaration(frozenset("CDFNR"), True),
    "duration-span": SetDeclaration(frozenset("S"), False),
}


def _assertion_rows() -> dict[str, set[str]]:
    return {
        path.parent.name: set(ROW_ID.findall(path.read_text(encoding="utf-8")))
        for path in FIXTURES.glob("*/assertions.md")
    }


def _population_errors(rows: dict[str, set[str]]) -> list[str]:
    """Check the globbed population and its non-vacuity, independent of rows."""
    errors: list[str] = []
    actual = set(rows)
    declared = set(SET_DECLARATIONS)
    if actual != declared:
        errors.append(
            "assertion sets %r do not equal declared sets %r"
            % (sorted(actual), sorted(declared))
        )
    for name in sorted(actual & declared):
        if not rows[name]:
            errors.append(name + " has no assertion rows")
    return errors


def _prefix_errors(rows: dict[str, set[str]]) -> list[str]:
    """Check every declared member's row identifiers against its own grammar."""
    errors: list[str] = []
    for name, declaration in SET_DECLARATIONS.items():
        if name not in rows:
            continue
        prefixes = frozenset(row_id[0] for row_id in rows[name])
        if prefixes != declaration.prefixes:
            errors.append(
                "%s prefixes %r do not equal declared prefixes %r"
                % (name, sorted(prefixes), sorted(declaration.prefixes))
            )
    return errors


def _number(value: str) -> int:
    """Parse a catalog number written as digits or an American English word."""
    if value.isdigit():
        return int(value)
    try:
        return sum(NUMBER_WORDS[part] for part in value.lower().split("-"))
    except KeyError as error:
        raise AssertionError("unknown number word in Sets table: " + value) from error


def _catalog_denominators(text: str) -> dict[str, int | None]:
    """Parse set names and row denominators from the Markdown ``Sets`` table."""
    denominators: dict[str, int | None] = {}
    in_sets = False
    for line in text.splitlines():
        if line == "## Sets":
            in_sets = True
            continue
        if in_sets and line.startswith("## "):
            break
        if not in_sets or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 6:
            continue
        match = SET_LINK.fullmatch(cells[0])
        if not match:
            continue
        row_total = ROW_TOTAL.search(cells[5])
        denominators[match.group(1)] = (
            _number(row_total.group("total")) if row_total else None
        )
    return denominators


def _denominator_errors(text: str, rows: dict[str, set[str]]) -> list[str]:
    """Compare each parsed catalog denominator with its declared policy."""
    catalog = _catalog_denominators(text)
    errors: list[str] = []
    if set(catalog) != set(SET_DECLARATIONS):
        errors.append(
            "catalog sets %r do not equal declared sets %r"
            % (sorted(catalog), sorted(SET_DECLARATIONS))
        )
    for name, declaration in SET_DECLARATIONS.items():
        expected = declaration.historical_denominator
        if expected is None and declaration.has_run and name in rows:
            expected = len(rows[name])
        actual = catalog.get(name)
        if actual != expected:
            errors.append(
                "%s catalog denominator %r does not equal %r"
                % (name, actual, expected)
            )
    return errors


class TheFixtureSetPopulationIsDeclared(unittest.TestCase):
    """The population ratchet, separate from every per-row assertion."""

    def setUp(self):
        self.rows = _assertion_rows()

    def test_every_globbed_set_is_declared_and_nonempty(self):
        self.assertEqual(_population_errors(self.rows), [])

    def test_an_undeclared_set_fails_before_its_rows_are_covered(self):
        changed = dict(self.rows, new_set={"X1"})
        self.assertTrue(_population_errors(changed))

    def test_an_empty_set_fails_instead_of_passing_vacuously(self):
        changed = dict(self.rows, **{"day-a": set()})
        self.assertIn("day-a has no assertion rows", _population_errors(changed))


class EverySetDeclaresItsRowPrefixes(unittest.TestCase):
    def setUp(self):
        self.rows = _assertion_rows()

    def test_every_prefix_is_declared_per_set(self):
        self.assertEqual(_prefix_errors(self.rows), [])

    def test_a_new_prefix_fails_until_it_is_declared(self):
        changed = {name: set(row_ids) for name, row_ids in self.rows.items()}
        changed["day-a"].add("Z1")
        self.assertIn(
            "day-a prefixes ['A', 'D', 'F', 'R', 'Z'] do not equal declared "
            "prefixes ['A', 'D', 'F', 'R']",
            _prefix_errors(changed),
        )


class TheSetsCatalogDenominatorsAreGated(unittest.TestCase):
    def setUp(self):
        self.readme = FIXTURES_README.read_text(encoding="utf-8")
        self.rows = _assertion_rows()

    def test_every_denominator_agrees_with_its_policy(self):
        self.assertEqual(_denominator_errors(self.readme, self.rows), [])

    def test_a_stale_denominator_fails_the_gate(self):
        changed = self.readme.replace("7 of 14 rows", "7 of 13 rows", 1)
        self.assertNotEqual(changed, self.readme, "mutation target is absent")
        self.assertIn(
            "hedged-dx catalog denominator 13 does not equal 14",
            _denominator_errors(changed, self.rows),
        )

    def test_a_missing_denominator_on_a_run_set_fails_the_gate(self):
        changed = self.readme.replace("6 of 13 rows", "six scored rows", 1)
        self.assertNotEqual(changed, self.readme, "mutation target is absent")
        self.assertIn(
            "peds-bp catalog denominator None does not equal 13",
            _denominator_errors(changed, self.rows),
        )

    def test_day_a_keeps_its_historical_denominator(self):
        self.assertEqual(len(self.rows["day-a"]), 35)
        self.assertEqual(_catalog_denominators(self.readme)["day-a"], 34)


if __name__ == "__main__":
    unittest.main()
