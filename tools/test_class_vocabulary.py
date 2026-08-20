"""The catalog's ``class`` vocabulary and the one the index carries are one set.

phi-scan: synthetic

The classifier-boundary assertions retain the timestamp-shaped browser capture that
distinguishes ``web-capture`` from ``guideline``. It is a public CDC fixture shape;
no patient or corpus date is exempted.

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

**Whether every future document fits the vocabulary.** Agreement across files cannot
prove that. #107 ruled ``class`` records document form and added ``draft``, ``errata``
and ``scope-of-work`` for the three documents that exposed the gap. The shipped-row
assertion below pins those rulings, but a seventh form would still require a reading.

**Whether a row's cell is the *correct* value for that document.** That is
``guidelines_catalog.py --check``'s job and it needs the corpus. This reaches only that
the value is one the index could answer.

**Whether the producer classified a row correctly.** That rule lives only in
``guidelines_extract.classify`` now. #108 removed the catalog's second classifier, so
the manifest value is the value this auditor reads rather than one it re-derives from
already-stripped text.
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

    def test_the_three_non_guidelines_publish_their_document_forms(self) -> None:
        rows, _, problems = guidelines_catalog.parse_catalog(self.text)
        self.assertEqual(problems, [], "the shipped catalog does not parse")
        new_forms = {"draft", "errata", "scope-of-work"}
        published = {row.filename: row.cls for row in rows if row.cls in new_forms}
        self.assertEqual(
            published,
            {
                "KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf": "draft",
                "ciab275.pdf": "errata",
                "KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf": "scope-of-work",
            },
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
        published = [
            value
            for value in guidelines_extract.CLASSES
            if value != guidelines_extract.CLASS_WEB_CAPTURE
        ]
        failures = guidelines_catalog.check_legend(self.legend(*published))
        self.assertEqual(len(failures), 1)
        self.assertIn(guidelines_extract.CLASS_WEB_CAPTURE, failures[0])

    def test_a_file_with_no_class_legend_row_is_a_failure_and_not_a_pass(self) -> None:
        failures = guidelines_catalog.check_legend("# A catalog with no column legend\n")
        self.assertEqual(len(failures), 1)
        self.assertIn("cannot be read", failures[0])


class TheVocabularyIsBoundedInBothDirections(unittest.TestCase):
    def test_the_three_new_document_forms_are_published(self) -> None:
        self.assertTrue(
            {"draft", "errata", "scope-of-work"}.issubset(guidelines_extract.CLASSES)
        )

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
            guidelines_extract.classify([["PUBLIC REVIEW DRAFT"], ["body"]]),
            guidelines_extract.classify([["ERRATA"], ["body"]]),
            guidelines_extract.classify(
                [["KDIGO Guideline", "Scope of Work"], ["body"]]
            ),
        }
        self.assertEqual(reachable, set(guidelines_extract.CLASSES))

    def test_the_index_carries_one_class_the_catalog_does_not_publish(self) -> None:
        """``unclassified`` is real, is outside ``CLASSES``, and is not a hole.

        ``guidelines_index.py`` writes it where a document has no manifest entry at
        all, so it is an additional value ``--class`` can be asked about and the catalog
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
