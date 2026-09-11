"""Drive the generic Markdown readers through their public interfaces."""

from __future__ import annotations

import unittest
from pathlib import Path

import markdown_read
from markdown_read import StepCitation, dead_links, markdown_targets, step_citations
from prose_bind import NAMING, bind


REPO_ROOT = Path(__file__).resolve().parent.parent


class DeclaredLimitsAreBound(unittest.TestCase):
    def test_the_reader_names_its_declared_limits_object(self) -> None:
        self.assertTrue(markdown_read.DECLARED_LIMITS)
        self.assertEqual(
            (),
            bind(markdown_read.DECLARED_LIMITS, markdown_read.__doc__, mode=NAMING),
        )


class TheStepResolverIsLive(unittest.TestCase):
    """A resolver that named nothing would pass every assertion in the class below.

    Each case here is a shape taken off the real tree rather than invented, and
    the two marked *false alarm* are lines a simpler rule failed. They are the
    reason the resolver has three limbs instead of one.
    """

    NAMES = ["setup-clinical-skills", "practicum-case-study", "clinical-note", "batch-shift"]

    def resolve(self, text: str, owner: str | None = None) -> list[StepCitation]:
        return list(step_citations(text, owner, self.NAMES))

    def test_a_link_beside_the_words_names_the_skill(self) -> None:
        cite, = self.resolve("See [batch-shift](../batch-shift/SKILL.md) step 6.", "clinical-note")
        self.assertEqual((cite.subject, cite.number, cite.how), ("batch-shift", 6, "beside"))

    def test_a_backticked_name_beside_the_words_names_the_skill(self) -> None:
        """``anchor_scan.py`` and ``corpus_census.py`` cite this way, from ``tools/``."""
        cite, = self.resolve("``clinical-note`` step 1 rests on whole day files.")
        self.assertEqual((cite.subject, cite.how), ("clinical-note", "beside"))

    def test_a_bare_path_beside_the_words_names_the_skill(self) -> None:
        """``docx_write.py``'s form, and it is one of the citations #233 was filed over."""
        cite, = self.resolve("``skills/practicum-case-study/SKILL.md`` step 9's sentence.")
        self.assertEqual((cite.subject, cite.number), ("practicum-case-study", 9))

    def test_a_bare_citation_takes_the_skill_whose_file_it_is(self) -> None:
        cite, = self.resolve("| **Neither** | Report it -- see ste" "p 4 |", "batch-shift")
        self.assertEqual((cite.subject, cite.how), ("batch-shift", "owner"))

    def test_a_second_citation_carries_the_first_ones_subject(self) -> None:
        """``voice.md``'s citations of its fifth and ninth steps.

        The first resolves by ``owner`` rather than ``beside``, and that is the
        point of the case: a **relative** link back to the skill's own file
        spells no skill name anywhere, so only the directory settles it. The
        second then carries the first's subject.
        """
        first, second = self.resolve(
            "[SKILL.md](../SKILL.md) ste" "p 5, before drafting, and ste" "p 9, where the draft is read.",
            "practicum-case-study",
        )
        self.assertEqual((first.subject, first.how), ("practicum-case-study", "owner"))
        self.assertEqual((second.subject, second.how), ("practicum-case-study", "carried"))

    def test_a_relative_self_link_is_not_a_named_skill(self) -> None:
        """``[SKILL.md](../SKILL.md)`` names nothing, so outside ``skills/`` it is unresolved."""
        cite, = self.resolve("[SKILL.md](../SKILL.md) ste" "p 5, before drafting.", None)
        self.assertIsNone(cite.subject)

    def test_the_subject_carries_across_a_hard_wrap(self) -> None:
        """The paragraph is the scope, so a wrapped line does not restart it."""
        first, second = self.resolve(
            "[setup-clinical-skills](../setup-clinical-skills/SKILL.md) step 9 collects it,\n"
            "on the same terms as the voice model in step 8.",
            "clinical-note",
        )
        self.assertEqual(first.subject, "setup-clinical-skills")
        self.assertEqual((second.subject, second.line, second.how), ("setup-clinical-skills", 2, "carried"))

    def test_a_hard_wrapped_citation_is_still_read(self) -> None:
        """No line in the tree wraps between the word and the number. One will."""
        cite, = self.resolve("...which is [batch-shift](../batch-shift/SKILL.md) step\n3.", "clinical-note")
        self.assertEqual((cite.subject, cite.number), ("batch-shift", 3))

    def test_a_name_in_between_breaks_the_carry(self) -> None:
        """False alarm 1, from ``setup-clinical-skills/SKILL.md``.

        *"[clinical-note]'s second step and [batch-shift], for the ninth step's shorthand"* --
        the ninth step is ``setup``'s own, and both a nearest-name rule and a
        carry with no interruption clause resolve it to a skill with 7 steps and
        fail a correct line.
        """
        first, second = self.resolve(
            "**Hard** -- [clinical-note](../clinical-note/SKILL.md) step 2 and "
            "[batch-shift](../batch-shift/SKILL.md), for ste" "p 9's shorthand.",
            "setup-clinical-skills",
        )
        self.assertEqual(first.subject, "clinical-note")
        self.assertEqual((second.subject, second.how), ("setup-clinical-skills", "owner"))

    def test_a_sentence_boundary_does_not_carry_a_stale_subject(self) -> None:
        """False alarm 2, the other ``setup-clinical-skills`` line a nearest-name rule failed."""
        cites = self.resolve(
            "[clinical-note](../clinical-note/SKILL.md) expands shorthand at ste" "p 2. Read it\n"
            "before asking; it is not restated here, on ste" "p 8's arrangement.",
            "setup-clinical-skills",
        )
        self.assertEqual(cites[-1].subject, "setup-clinical-skills")

    def test_a_bare_citation_outside_a_skill_stays_unresolved(self) -> None:
        """``anchor_scan.py``'s fourth-step form meant ``icd10-cpt`` and nothing here could know it.

        The line is that module's, as it stood before #238 named the skill beside
        it. Kept verbatim: the shape is what this grades, and a repaired tree is
        not a reason to stop testing the shape it was repaired out of.
        """
        cite, = self.resolve("# Ste" "p 4's heading. The lookbehind is load-bearing.", None)
        self.assertIsNone(cite.subject)

    def test_the_plural_opener_is_a_floor_and_says_so(self) -> None:
        """A plural opener is read as a citation of 1; the 2 is deliberately missed."""
        self.assertEqual(
            [c.number for c in self.resolve("if ste" "ps 1 and 2 move", "batch-shift")],
            [1],
        )


class TheDeadLinkResolverIsLive(unittest.TestCase):
    """#538's relative-link resolver is driven against synthetic text."""

    OWNER = Path("docs/adr/0054-relative-links.md")

    def test_a_good_slug_passes(self) -> None:
        existing = {Path("docs/adr/0016-real-record.md")}
        exists = existing.__contains__

        self.assertEqual(
            dead_links("[ADR 0016](0016-real-record.md)", self.OWNER, exists),
            [],
        )

    def test_a_plausible_wrong_slug_fails(self) -> None:
        existing = {Path("docs/adr/0016-real-record.md")}
        cases = (
            (
                "[ADR 0016](0016-plausible-record.md)",
                [(1, "0016-plausible-record.md")],
            ),
            (
                '[ADR 0016](0016-plausible-record.md "title")',
                [(1, "0016-plausible-record.md")],
            ),
            (
                "[ADR 0016](<0016 plausible record.md>)",
                [(1, "0016 plausible record.md")],
            ),
            (
                "[ADR 0016](0016-plausible(record).md)",
                [(1, "0016-plausible(record).md")],
            ),
            (
                "[ADR 0016][plausible]\n\n[plausible]: 0016-plausible-record.md",
                [(3, "0016-plausible-record.md")],
            ),
        )
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(dead_links(text, self.OWNER, existing.__contains__), expected)

    def test_an_anchor_is_dropped_without_hiding_a_missing_file(self) -> None:
        existing = {Path("docs/adr/0016-real-record.md")}
        exists = existing.__contains__

        self.assertEqual(
            dead_links("[section](0016-real-record.md#ruling)", self.OWNER, exists),
            [],
        )
        self.assertEqual(
            dead_links("[section](0016-missing.md#ruling)", self.OWNER, exists),
            [(1, "0016-missing.md#ruling")],
        )

    def test_an_absolute_url_is_skipped_without_hiding_a_relative_target(self) -> None:
        exists = set().__contains__

        self.assertEqual(
            dead_links("[ticket](https://github.com/example/repo/issues/1)", self.OWNER, exists),
            [],
        )
        self.assertEqual(
            dead_links("[record](missing.md)", self.OWNER, exists),
            [(1, "missing.md")],
        )

    def test_code_targets_are_skipped_without_shifting_line_numbers(self) -> None:
        text = (
            "Inline example: `[record](missing.md)`\n"
            "```markdown\n"
            "[record](missing.md)\n"
            "```\n"
            "[record](missing.md)\n"
        )

        self.assertEqual(
            dead_links(text, self.OWNER, set().__contains__),
            [(5, "missing.md")],
        )

    def test_a_code_target_is_reported_when_unquoted(self) -> None:
        self.assertEqual(
            dead_links("[record](missing.md)", self.OWNER, set().__contains__),
            [(1, "missing.md")],
        )

    def test_resolution_uses_the_linking_files_directory(self) -> None:
        asked: list[Path] = []

        def record(path: Path) -> bool:
            asked.append(path)
            return True

        self.assertEqual(
            dead_links(
                "[fixture set](../README.md)",
                Path("fixtures/day-a/shorthand/README.md"),
                record,
            ),
            [],
        )
        self.assertEqual(asked, [Path("fixtures/day-a/README.md")])


class TheCommittedADRLinkPopulationIsLive(unittest.TestCase):
    def test_committed_adr_records_hold_a_nontrivial_destination_floor(self) -> None:
        records = sorted((REPO_ROOT / "docs" / "adr").glob("*.md"))
        destinations = sum(
            len(list(markdown_targets(record.read_text(encoding="utf-8"))))
            for record in records
        )
        self.assertGreaterEqual(destinations, 1500)


if __name__ == "__main__":
    unittest.main()
