"""Tests for issue #96's ruling: which allergens reach the Allergies box.

Three things are pinned here and none of them is a scanner, because there is no
committed ``clinical-note`` run whose allergy box this could be pointed at --
``test_differential_scan.py``'s position, for its reason.

**The two branch templates must agree, and this is the test that would have
caught them not agreeing.** ``HP.md`` has said ``and drug allergies separately``
since it was written and ``SOAP.md`` said nothing of the kind, so two runs
obeying their own branch produced different notes from the same words for
months. Nothing compared the two placeholders, so nothing reported it; #96 was
filed off the *output* divergence rather than off the instruction that caused
it.

**The population must be re-derivable rather than quoted.** #96's ruling turned
on a share -- how many committed inputs put an allergen under a label against
inside an ``hx:`` list -- and that share was published as four of five, then
four of six, then four of eight, as fixture sets landed and nobody re-derived
it. The count here fails when a set lands, which is
`#143 <https://github.com/mshamblin5150-code/clinical-skills/issues/143>`_'s
whole ask.

**And the four fixture rows must still exist**, because the ruling is counted
across four sets and promotable only as a group. A set quietly losing its row
would leave the other three enforcing a rule at a width nobody chose.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import corpus_census
from test_corpus_census import all_fixture_shorthand

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "clinical-note"
SOAP = SKILL_DIR / "SOAP.md"
HP = SKILL_DIR / "HP.md"
SKILL = SKILL_DIR / "SKILL.md"
FIXTURES = REPO_ROOT / "fixtures"

# The eight committed inputs naming an allergen, pinned by path and then
# re-derived below. Both halves are needed: the list alone goes stale silently
# when a set lands, and the derivation alone can drift to matching nothing and
# still report a tidy split.
UNDER_A_LABEL = (
    "day-b/shorthand/case-11.md",
    "duration-span/shorthand/case-01.md",
    "duration-span/shorthand/case-02.md",
    "hedged-dx/shorthand/case-03.md",
)
INSIDE_HX = (
    "day-a/shorthand/case-06.md",
    "day-b/shorthand/case-02.md",
    "day-b/shorthand/case-07.md",
    "peds-bp/shorthand/case-05.md",
)

# The drug and environmental splits are *derived* below with ``corpus_census``'s
# own classifiers rather than pinned, so the counts cannot be a figure this file
# quotes at itself. An input may be in both -- day-b case 11 names a drug and an
# environmental allergen on one line, which is why #96 could not be settled by
# asking which kind a *case* was.
EXPECTED_DRUG = 4
EXPECTED_ENVIRONMENTAL = 6

# Pinned by hand, and it is the one kind that has to be. ``lactose
# intollaerance`` is an enzyme deficiency rather than a food *allergen*, so
# ``has_food_allergy`` returns False for it -- correctly, and a test asserting
# otherwise would be wrong about the immunology to make an arithmetic tidy.
# #96 ruled it into the box anyway, carrying the word ``intolerance``, and it is
# the only committed input of its kind.
FOOD_INTOLERANCE = ("peds-bp/shorthand/case-05.md",)

# The one input where label placement and a drug-only box give *opposite*
# answers. Every other one of the eight is environmental-inside-``hx:`` or
# drug-under-a-label, where both candidate rules agree and neither is tested.
DECIDING_INPUT = "hedged-dx/shorthand/case-03.md"

LABEL = re.compile(r"^\s*allerg(?:y|ies)\s*:", re.IGNORECASE)
NO_ALLERGEN = re.compile(r"^\s*(nkda|none|no known.*)\s*\.?\s*$", re.IGNORECASE)


def committed_inputs():
    """Every committed shorthand input, keyed by its path under ``fixtures/``.

    Borrowed from ``test_corpus_census.py`` rather than re-globbed. That module
    holds two readers and only one is right here: ``all_committed_cases`` names
    four directories and is pinned at 31, so a fifth set landing is invisible to
    it -- which is how #96's own figure went stale twice. ``all_fixture_shorthand``
    reads the tree, and reading the tree is what makes the count below fail
    loudly when a set lands. A second copy of that glob in this file would be the
    same figure derived two ways, which is the defect this module exists over.
    """
    for path, text in all_fixture_shorthand():
        yield path.relative_to(FIXTURES).as_posix(), text


def allergy_line(text: str) -> str:
    """The one line an input's allergy content sits on, label or ``hx:``.

    A labeled line wins over an ``hx:`` mention wherever both appear, which is
    the reading #96 tested and retired as a *rule* while keeping it as a way to
    find the line. Where the words land does not decide which box they go in;
    it still decides which line to read them off.
    """
    for line in text.splitlines():
        if LABEL.match(line):
            return line
    for line in text.splitlines():
        if line.strip().lower().startswith("hx:") and "allerg" in line.lower():
            return line
    return ""


def names_an_allergen(text: str) -> str | None:
    """``"label"``, ``"hx"``, or ``None`` -- where this input names an allergen.

    Written over ``allergy_line`` rather than walking the file again. A labeled
    line naming nothing but a denial is not naming an allergen, which is the
    distinction the whole ruling rests on: ``allergies: nkda`` is a *status*,
    ``allergy: seasonal`` is an allergen.
    """
    line = allergy_line(text)
    if not line:
        return None
    if LABEL.match(line):
        return None if NO_ALLERGEN.match(line.split(":", 1)[1]) else "label"
    return "hx"


def allergy_placeholder(text: str) -> str:
    """The ``<...>`` instruction under a template's Allergies heading.

    Both branches write the heading differently -- ``Allergies (reaction):`` on
    one line in SOAP, ``Allergies (with reaction)`` on its own line in H&P -- so
    the placeholder is found from the heading rather than by line number, and
    whitespace is flattened before the two are compared.
    """
    start = re.search(r"Allergies \((?:with )?reaction\)", text)
    if start is None:  # pragma: no cover - the guard is the failure message
        raise AssertionError("no Allergies heading in this template")
    opened = text.index("<", start.end())
    closed = text.index(">", opened)
    return " ".join(text[opened + 1 : closed].split())


class TheTwoBranchTemplatesGiveTheSameInstruction(unittest.TestCase):
    """The divergence #96 was filed off, made into a failing test."""

    def setUp(self) -> None:
        self.soap = allergy_placeholder(SOAP.read_text(encoding="utf-8"))
        self.hp = allergy_placeholder(HP.read_text(encoding="utf-8"))

    def test_the_placeholders_are_word_for_word_the_same(self) -> None:
        self.assertEqual(self.soap, self.hp)

    def test_both_order_the_drug_status_first(self) -> None:
        for placeholder in (self.soap, self.hp):
            self.assertIn("drug status first, NKDA if none", placeholder)

    def test_both_name_the_other_two_kinds(self) -> None:
        for placeholder in (self.soap, self.hp):
            self.assertIn("environmental and food, each named by its kind", placeholder)

    def test_neither_still_carries_the_pre_96_shape(self) -> None:
        """``<allergen - reaction; NKDA if none>`` was SOAP's for months."""
        for placeholder in (self.soap, self.hp):
            self.assertNotEqual(placeholder, "allergen - reaction; NKDA if none")
            self.assertNotIn("and drug allergies separately", placeholder)


class ThePopulationTheRulingWasMadeOver(unittest.TestCase):
    """Re-derived, not quoted. The share moved four times before it was ruled on."""

    def setUp(self) -> None:
        self.inputs = dict(committed_inputs())
        self.placement = {
            name: names_an_allergen(text)
            for name, text in self.inputs.items()
            if names_an_allergen(text) is not None
        }

    def test_the_denominator_is_every_committed_input(self) -> None:
        self.assertEqual(len(self.inputs), 37)

    def test_exactly_eight_inputs_name_an_allergen(self) -> None:
        self.assertEqual(len(self.placement), 8)

    def test_the_label_placement_split_is_four_and_four(self) -> None:
        """The count that killed the discriminator #96 was filed to test.

        The ticket argued placement on the strength of *four of the five put it
        in the history list*. At four of eight the argument that placement is
        the cheap rule because it settles the bulk does not survive.
        """
        labeled = sorted(k for k, v in self.placement.items() if v == "label")
        in_hx = sorted(k for k, v in self.placement.items() if v == "hx")
        self.assertEqual(labeled, sorted(UNDER_A_LABEL))
        self.assertEqual(in_hx, sorted(INSIDE_HX))
        self.assertEqual(len(labeled), len(in_hx))

    def test_every_pinned_input_still_exists_and_still_qualifies(self) -> None:
        for name in UNDER_A_LABEL + INSIDE_HX:
            with self.subTest(name):
                self.assertIn(name, self.placement)

    def test_the_kind_split_is_derived_by_the_shipped_classifier(self) -> None:
        """Six environmental, four drug -- counted by ``corpus_census``, not typed.

        The two overlap on day-b cases 7 and 11, which is why they sum past
        eight and why #96 could not be settled by asking what kind a *case* was.
        """
        drug = {n for n in self.placement if corpus_census.has_drug_allergy(self.inputs[n])}
        env = {
            n
            for n in self.placement
            if corpus_census.has_environmental_allergy(self.inputs[n])
        }
        self.assertEqual(len(drug), EXPECTED_DRUG)
        self.assertEqual(len(env), EXPECTED_ENVIRONMENTAL)
        self.assertEqual(drug | env, set(self.placement))
        self.assertEqual(len(drug & env), 2)

    def test_no_committed_input_names_a_food_allergen(self) -> None:
        """And the one food *intolerance* is why #96 needed a ruling for it.

        ``has_food_allergy`` is right to return False for ``lactose
        intollaerance``: it is an enzyme deficiency, not an immune reaction. So
        the food limb of the box was ruled with no allergen behind it at all,
        which is what `#168 <https://github.com/mshamblin5150-code/clinical-skills/issues/168>`_
        records about the population and is stated here as a property rather
        than borrowed as an authority.
        """
        for name, text in self.inputs.items():
            with self.subTest(name):
                self.assertFalse(corpus_census.has_food_allergy(text))
        for name in FOOD_INTOLERANCE:
            self.assertIn("intollaerance", self.inputs[name])
            self.assertIn(name, self.placement)

    def test_not_one_of_the_eight_names_a_reaction(self) -> None:
        """Which is why #94 is a separate ticket and #96 does not touch it.

        The template asks for ``allergen - reaction`` and no committed input
        supplies one, so that shape is satisfiable from the shorthand only where
        the answer is a denial. Checked on the *allergy line itself* rather than
        on a slice of the file: neither the hyphen the template pins a reaction
        with nor the word appears on any of the eight.
        """
        for name in self.placement:
            with self.subTest(name):
                line = allergy_line(self.inputs[name])
                self.assertNotIn(" - ", line)
                self.assertNotIn("reaction", line.lower())

    def test_the_deciding_input_is_labeled_and_environmental(self) -> None:
        """Both at once is what makes it the only tie-breaking case in the repo."""
        text = self.inputs[DECIDING_INPUT]
        self.assertEqual(self.placement[DECIDING_INPUT], "label")
        self.assertTrue(corpus_census.has_environmental_allergy(text))
        self.assertFalse(corpus_census.has_drug_allergy(text))
        self.assertIn("allergy: seasonal", text)

    def test_the_deciding_input_proposes_a_drug(self) -> None:
        """Why its box owes a drug status as well as the environmental line."""
        self.assertIn("zithromax", self.inputs[DECIDING_INPUT].lower())


class TheSkillStillSaysWhatWasRuled(unittest.TestCase):
    """A rule nobody restates is a rule the next run does not read."""

    def setUp(self) -> None:
        self.skill = SKILL.read_text(encoding="utf-8")

    def test_the_box_carries_every_allergen_named_by_kind(self) -> None:
        self.assertIn(
            "Never dropped means never moved out of the box either, and the box "
            "names which kind each allergen is.",
            self.skill,
        )

    def test_the_drug_status_is_owed_whether_or_not_a_drug_was_named(self) -> None:
        self.assertIn("Both halves are required", self.skill)
        self.assertIn(
            "The drug status is owed whether or not a drug allergen was named",
            self.skill,
        )

    def test_placement_is_explicitly_retired(self) -> None:
        self.assertIn(
            "**Where the clinician typed the words does not decide it.**", self.skill
        )
        self.assertIn("The kind decides, not the label", self.skill)

    def test_a_food_intolerance_is_carried_and_labeled(self) -> None:
        self.assertIn(
            "the word `intolerance` on the line is what makes it safe to carry",
            self.skill,
        )

    def test_the_reaction_question_is_left_to_94(self) -> None:
        self.assertIn(
            "None of this settles what a named allergen's *reaction* reads",
            self.skill,
        )

    def test_drift_row_17_carries_both_new_limbs(self) -> None:
        row = next(
            line for line in self.skill.splitlines() if line.startswith("| 17 |")
        )
        self.assertIn("named by its kind", row)
        self.assertIn("routing a stated allergen to `pmh` instead fails", row.lower())
        self.assertIn("called an intolerance", row)
        self.assertIn("denies a given the note read", row)


class TheRulingIsHeldAtTheSameWidthInEverySet(unittest.TestCase):
    """Four rows, one ruling, promotable only as a group."""

    ROWS = {
        "day-a": "R15",
        "day-b": "R6",
        "hedged-dx": "R2",
        "peds-bp": "R3",
    }

    def test_each_set_still_carries_its_row(self) -> None:
        for directory, row in self.ROWS.items():
            with self.subTest(directory):
                text = (FIXTURES / directory / "assertions.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(f"| {row} |", text)

    def test_each_row_cites_the_ticket(self) -> None:
        for directory in self.ROWS:
            with self.subTest(directory):
                text = (FIXTURES / directory / "assertions.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn("issues/96", text)

    def test_the_population_is_stated_in_exactly_one_set(self) -> None:
        """#143's rule: a figure lives where it is re-derived, once.

        day-b holds it because it holds the ruling's history. The other three
        link to it rather than repeating it, so a re-derivation cannot leave
        three stale copies behind.
        """
        holding = [
            directory
            for directory in self.ROWS
            if "8 name an allergen"
            in (FIXTURES / directory / "assertions.md").read_text(encoding="utf-8")
        ]
        self.assertEqual(holding, ["day-b"])


if __name__ == "__main__":
    unittest.main()
