"""The catalog's ``class`` vocabulary and the one the index carries are one set.

phi-scan: synthetic

The pragma is above because ``TheTwoClassifiersAgree`` pins the browser print
timestamp that tells an ACIP print-to-PDF capture apart from a guideline, and the
ordering rule it exists for cannot be exercised without a timestamp-shaped literal.
It is an artifact of a public CDC page and no patient is near it, but the shape layer
cannot know that -- ``test_guidelines_extract.py`` declares the same pragma for the
same literal and for the same reason. Writing it in pieces would dodge the scanner
without declaring anything, which is worse than saying so here. The corpus layer is
untouched: no name and no corpus date is exempted by this.

**It shipped once without the pragma and the reason is worth keeping.**
``phi_scan --all`` ran clean over this change minutes before the commit, because this
file was still **untracked** and ``--all`` walks ``git ls-files``. ``git add`` turned
the same tree red. That is
[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)'s window
exactly, arriving on the firewall rather than on a step citation, and the hook is what
caught it.

[#185](https://github.com/mshamblin5150-code/clinical-skills/issues/185). They were
two. ``reference/guidelines-catalog.md`` documented ``guideline``,
``recommendation-statement`` and ``web-capture``; ``guidelines_extract.py`` emitted
``guideline``, ``print-capture`` and ``unknown`` into ``manifest.json``, which is what
``guidelines_index.py`` stores and what ``guidelines_search.py --class`` filters on.
They overlapped on one string, so **93 of 179 documents carried a class the retrieval
tool could not be asked about** -- every USPSTF recommendation statement and all three
ACIP captures.

**Those two figures are stated here and deliberately nowhere else.** They are facts
about a tree that no longer exists: nothing committed re-derives them, and the corpus
they were counted against lives outside every checkout. Everywhere else that reasoning
appears -- ``CLAUDE.md``, ``reference/guidelines-catalog.md``, ``guidelines_extract.py``,
``guidelines_search.py`` -- names the set qualitatively and cites the ticket, on
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143)'s terms. A
first draft published both across four files each, inside the change whose subject is
a vocabulary copied into two.

**What made it worse than a naming mismatch is the exit status.** ``guidelines_search``
reserves 2 for every way of not having searched precisely so silence cannot read as a
settled negative; a filter value no document carries is, to that tool, a correctly
answered question with an empty answer, and it exited **1** -- the documented code for
a genuine zero. So the tool did not merely fail to answer, it certified that no
recommendation statement in the corpus mentions screening.

**The check needs no corpus, no manifest, no PDF and no built index.** Both
vocabularies are tracked: one is a legend row in a Markdown table, the other a tuple of
constants. The artifacts that would otherwise have to be read to see the disagreement
all live outside every checkout and are absent on most machines, so a check that needed
them would be a check that mostly did not run.

**The parsing lives in ``guidelines_catalog.check_legend`` rather than here**, so the
command and the suite cannot come to hold different answers -- and so a legend edited
to publish a fourth value fails ``python tools/guidelines_catalog.py`` on any machine
rather than only the suite. That is the ticket's own *Done when*: *"tools/
guidelines_catalog.py already audits the catalog's mechanical columns against the
corpus and is the obvious home."* It is the home; what the ticket had wrong is that it
needed to read the manifest to get there.

**Two checks, not one, and they catch different things.** A **row** carrying a value
the index cannot answer is one document unreachable. A **legend** publishing one is an
instruction to every reader to ask an unanswerable question, and no row has to be wrong
for that to be true -- which is why the shipped table passing every row check is not
the same as the file being right.

## What this cannot reach

**Whether the vocabulary is the right one.** Three values that agree across both files
and describe the corpus badly pass every assertion below. #107 is the open question of
whether ``class`` should record document *form* or document *standing*, and a scope of
work, an errata and a public review draft are all ``guideline`` today because the
vocabulary has nowhere better to put them.

**Whether a row's cell is the *correct* value for that document.** That is
``guidelines_catalog.py --check``'s job and it needs the corpus. This reaches only that
the value is one the index could answer.

**And the two classifiers' shared ordering is pinned by agreement, not by one copy.**
``guidelines_extract.classify`` and ``guidelines_catalog.classify`` read different
inputs -- pre-strip line lists against page strings -- so neither can call the other,
and the capture rule stays written twice. What the class below asserts is that they
return the same answer on the same document, including on the case the order exists
for. [#108](https://github.com/mshamblin5150-code/clinical-skills/issues/108) is where
the duplication itself is reconciled.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import guidelines_catalog
import guidelines_extract
import guidelines_index

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "reference" / "guidelines-catalog.md"


class TheCatalogPublishesOnlyValuesTheIndexCanAnswer(unittest.TestCase):
    def setUp(self) -> None:
        self.text = CATALOG.read_text(encoding="utf-8")

    def test_the_shipped_legend_is_the_producers_vocabulary(self) -> None:
        self.assertEqual(guidelines_catalog.check_legend(self.text), [])

    def test_every_shipped_row_carries_a_value_the_index_can_answer(self) -> None:
        rows, _, problems = guidelines_catalog.parse_catalog(self.text)
        self.assertEqual(problems, [], "the shipped catalog does not parse")
        self.assertTrue(rows, "no rows parsed out of the shipped catalog")
        offenders = sorted({row.cls for row in rows} - set(guidelines_extract.CLASSES))
        self.assertEqual(
            offenders,
            [],
            "rows carry a class no document in the index can carry, so "
            "`guidelines_search.py --class <value>` answers them with a certified zero",
        )

    def test_the_auditor_holds_no_copy_of_the_vocabulary(self) -> None:
        """``guidelines_catalog.CLASSES`` is the producer's tuple, not a copy of it.

        ``reference_scan.py`` importing ``docx_write.REFERENCE_HEADING`` rather than
        restating it, for that module's reason: an auditor holding its own copy of the
        rule can pass a catalog the producer disagrees with, which is the one failure
        the check exists to catch.
        """
        self.assertIs(guidelines_catalog.CLASSES, guidelines_extract.CLASSES)


class TheInstrumentIsLive(unittest.TestCase):
    """A check that says yes to everything is worth less than none.

    ``test_build_artifacts_ignored.py``'s arrangement: assert the predicate fails on
    something it should fail on, before trusting that it passed on the shipped file.
    """

    LEGEND = "| Column | What it is |\n| --- | --- |\n| `class` | {values} |\n"

    def legend(self, *values: str) -> str:
        return self.LEGEND.format(values=", ".join(f"`{v}`" for v in values))

    def test_a_legend_publishing_a_value_the_index_cannot_answer_fails(self) -> None:
        failures = guidelines_catalog.check_legend(
            self.legend(*guidelines_extract.CLASSES, "print-capture")
        )
        self.assertEqual(len(failures), 1)
        self.assertIn("print-capture", failures[0])

    def test_a_legend_omitting_a_value_the_index_carries_fails(self) -> None:
        """The direction the pre-#185 tree was wrong in, and the cheaper half to miss.

        The catalog published three and the index carried three; the sets simply were
        not the same one. A subset test in either direction alone would have passed on
        one of the two arrangements this ticket has seen.
        """
        failures = guidelines_catalog.check_legend(
            self.legend(guidelines_extract.CLASS_GUIDELINE)
        )
        self.assertEqual(len(failures), 2)

    def test_a_file_with_no_class_legend_row_is_a_failure_and_not_a_pass(self) -> None:
        failures = guidelines_catalog.check_legend("# A catalog with no column legend\n")
        self.assertEqual(len(failures), 1)
        self.assertIn("cannot be read", failures[0])


class TheTwoClassifiersAgree(unittest.TestCase):
    """One ordering rule, written twice, and nothing asserted it until #185.

    The marks moved to the producer and the auditor imports them, but the *order* --
    a capture that says "recommendation statement" is still a capture -- stayed in both
    ``classify`` functions, and so did the capture test itself, because the two read
    different inputs and neither can call the other. Reversing either copy alone left
    the whole suite green.

    So the pin is behavioral: the same document, in each module's own input shape,
    must come back the same class. The stamped-and-titled case is the one the order
    exists for and is why this is not merely three tidy cases.
    """

    CAPTURE = "8/12/26, 10:25 AM Recommended Vaccinations | CDC"
    URL = "https://www.cdc.gov/vaccines/index.html"
    USPSTF = "US Preventive Services Task Force Recommendation Statement"

    def both(self, pages: list[list[str]]) -> tuple[str, str]:
        """``classify`` from each module, over one document in each one's own shape."""
        return (
            guidelines_extract.classify(pages),
            guidelines_catalog.classify(["\n".join(page) for page in pages]),
        )

    def assert_agree(self, pages: list[list[str]], expected: str) -> None:
        produced, audited = self.both(pages)
        self.assertEqual(produced, expected)
        self.assertEqual(audited, expected, "the auditor disagrees with the producer")

    def test_a_guideline(self) -> None:
        self.assert_agree(
            [["KDIGO 2024 Clinical Practice Guideline"], ["body"], ["body"], ["body"]],
            guidelines_extract.CLASS_GUIDELINE,
        )

    def test_a_recommendation_statement(self) -> None:
        self.assert_agree(
            [[self.USPSTF, "Screening for Colorectal Cancer"], ["body"], ["body"], ["body"]],
            guidelines_extract.CLASS_RECOMMENDATION_STATEMENT,
        )

    def test_a_web_capture(self) -> None:
        self.assert_agree(
            [[self.CAPTURE, self.URL, "body"] for _ in range(4)],
            guidelines_extract.CLASS_WEB_CAPTURE,
        )

    def test_a_capture_of_a_recommendation_statement_is_a_capture_in_both(self) -> None:
        """The case the shared ordering exists for.

        Live in the other direction in this corpus: the catalog's own prose records a
        JAMA article page saved from a browser that is classed
        ``recommendation-statement`` because that is what the document *is*.
        """
        pages = [[self.CAPTURE, self.URL, self.USPSTF]] + [
            [self.CAPTURE, self.URL, "body"] for _ in range(3)
        ]
        self.assert_agree(pages, guidelines_extract.CLASS_WEB_CAPTURE)


class TheVocabularyIsBoundedInBothDirections(unittest.TestCase):
    def test_every_class_classify_can_return_is_published(self) -> None:
        """``CLASS_UNKNOWN`` is deliberately unreachable from ``classify``.

        It is what a document that failed to read carries, and a document that failed
        to read is never classified. So it is a manifest value only, and never a filter
        value.
        """
        title = ["US Preventive Services Task Force Recommendation Statement"]
        for pages in (
            [],
            [["8/12/26, 10:25 AM Adult Schedule | CDC", "body"] for _ in range(4)],
            [title, ["body"], ["body"], ["body"]],
            [["KDIGO 2024 Clinical Practice Guideline"], ["body"], ["body"]],
        ):
            with self.subTest(pages=pages[:1]):
                self.assertIn(guidelines_extract.classify(pages), guidelines_extract.CLASSES)

    def test_every_published_class_is_one_classify_can_return(self) -> None:
        """The other direction, and it is this ticket's own defect in miniature.

        A value in ``CLASSES`` that nothing can ever emit is a filter the catalog
        publishes and the index cannot answer -- which is what
        ``recommendation-statement`` was for the whole of #185's life. A subset test
        would have passed on it.
        """
        title = ["US Preventive Services Task Force Recommendation Statement"]
        reachable = {
            guidelines_extract.classify([["KDIGO 2024 Guideline"], ["body"], ["body"]]),
            guidelines_extract.classify([title, ["body"], ["body"], ["body"]]),
            guidelines_extract.classify(
                [["8/12/26, 10:25 AM Adult Schedule | CDC", "body"] for _ in range(4)]
            ),
        }
        self.assertEqual(reachable, set(guidelines_extract.CLASSES))

    def test_the_index_carries_one_class_the_catalog_does_not_publish(self) -> None:
        """``unclassified`` is real, is outside ``CLASSES``, and is not a hole.

        ``guidelines_index.py`` writes it where a document has no manifest entry at
        all, so it is a fourth value ``--class`` can be asked about and the catalog
        never names. That is correct -- it describes a *build*, not a document, and a
        catalog row carrying it would be meaningless -- and it does not reopen #185,
        because a manifest that went missing puts every document under it and
        ``guidelines_search`` then exits 2 on every catalog class rather than
        certifying a zero. Pinned so the distinction is a known behavior.
        """
        self.assertNotIn(guidelines_index.UNCLASSIFIED, guidelines_extract.CLASSES)
        self.assertNotIn(guidelines_extract.CLASS_UNKNOWN, guidelines_extract.CLASSES)


if __name__ == "__main__":
    unittest.main()
