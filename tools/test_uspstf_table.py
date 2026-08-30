"""Tests for tools/uspstf_table.py.

Runs against the page excerpts in ``tools/testdata/uspstf/`` and **never against the
shipped table**, for the reason ``tools/test_icd10.py`` gives: a test that read
``reference/guidelines-uspstf.md`` would pass for two reasons, one of them being that the
builder and the test are wrong together.

The excerpts are extracted page text from USPSTF recommendation statements, which are
federal work and public domain. Author names, affiliations and correspondence addresses
are removed from them -- no parser here reads those, and a fixture should carry only the
text it exists to prove.

Each fixture is one document layout the corpus actually contains:

* ``jama-abstract-multi``  -- JAMA structured abstract stating three recommendations
* ``jama-abstract-single`` -- JAMA structured abstract stating one
* ``jama-glued-abstract``  -- the same, but extraction dropped every space glyph
* ``annals-abstract``      -- Annals of Internal Medicine's ``Recommendation:`` field
* ``summary-section``      -- no abstract field; the grade is in the summary section
* ``ahrq-sentence-grade``  -- 2000s AHRQ prose, ``A recommendation.`` as a sentence

Run with::

    python -m unittest discover -s tools -t tools
"""

import json
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import artifact_provenance
import guidelines_extract as extract
import uspstf_table as ut
from guidelines_manifest_test_support import ReadingManifestConformance


def clean_producer():
    producer = artifact_provenance.current_producer()
    producer["dirty"] = False
    return producer

TESTDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata", "uspstf")


def fixture(name):
    """One fixture page, as #80's extracted corpus would provide it."""
    with open(os.path.join(TESTDATA, name + ".txt"), encoding="utf-8") as handle:
        return [handle.read()]


class ReadingTheExtractedCorpus(ReadingManifestConformance, unittest.TestCase):
    """The table builder consumes #80's artifact and its metadata-title contract."""

    def build_conformance_corpus(self, root, producer):
        record = extract.build_document(
            Path("USPSTF/rhrs.pdf"),
            fixture("ahrq-sentence-grade"),
            root,
            "Screening for Rh (D) Incompatibility - Recommendation Statement",
        )
        extract.write_manifest(
            root, [record], Path("C:/outside/guidelines-src"), producer=producer
        )
        path = root / extract.MANIFEST_NAME
        value = json.loads(path.read_text(encoding="utf-8"))
        value["producer"] = producer
        path.write_text(json.dumps(value), encoding="utf-8")

    def conformance_read(self, root, *, allow):
        try:
            ut.build(root, allow_untrusted_provenance=allow)
        except ValueError as failure:
            return False, str(failure)
        return True, ""

    def conformance_command(self, root, *, allow):
        args = [str(root), "--out", str(root / "uspstf.md")]
        if allow:
            args.append("--allow-untrusted-provenance")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return ut.main(args)

    def test_the_manifest_reader_is_the_owner_and_not_a_copy(self):
        import guidelines_manifest

        self.assertIs(ut.read_or_raise, guidelines_manifest.read_or_raise)

    def test_build_reads_uspstf_text_and_title_from_the_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            record = extract.build_document(
                Path("USPSTF/rhrs.pdf"),
                fixture("ahrq-sentence-grade"),
                text_dir,
                "Screening for Rh (D) Incompatibility - Recommendation Statement",
            )
            extract.write_manifest(text_dir, [record], Path("C:/outside/guidelines-src"), producer=clean_producer())

            results = ut.build(text_dir)

            self.assertEqual(len(results), 1)
            self.assertEqual(Path(results[0].filename).name, "rhrs.pdf")
            self.assertEqual(
                results[0].rows[0].topic,
                "Screening for Rh (D) Incompatibility",
            )
            self.assertEqual([row.grade for row in results[0].rows], ["A", "B"])

    def test_build_ignores_other_societies_in_the_extracted_corpus(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            record = extract.build_document(
                Path("KDIGO/guideline.pdf"), ["KDIGO guideline"], text_dir, "KDIGO Guideline"
            )
            extract.write_manifest(text_dir, [record], Path("C:/outside/guidelines-src"), producer=clean_producer())

            self.assertEqual(ut.build(text_dir), [])

    def test_normalized_jama_label_still_opens_the_recommendation_region(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            record = extract.build_document(
                Path("USPSTF/thyroid.pdf"),
                [
                    "title page",
                    "Conclusions and Recommendation  The USPSTF recommends against "
                    "screening for thyroid cancer in asymptomatic adults. (D recommendation)",
                ],
                text_dir,
                "Screening for Thyroid Cancer",
            )
            extract.write_manifest(text_dir, [record], Path("C:/outside/guidelines-src"), producer=clean_producer())

            self.assertIn(
                "Conclusions and Recommendation The USPSTF",
                (text_dir / "USPSTF" / "thyroid.txt").read_text(encoding="utf-8"),
            )
            results = ut.build(text_dir)
            self.assertEqual([row.grade for row in results[0].rows], ["D"])

    def test_the_dated_abstract_citation_wins_after_an_undated_jama_masthead(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            citation = "JAMA. 2017;317(12):1252-1257"
            raw_pages = [
                "JAMA | US Preventive Services Task Force | RECOMMENDATION STATEMENT\n"
                + fixture("ahrq-sentence-grade")[0]
                + "\n"
                + citation
            ]
            record = extract.build_document(
                Path("USPSTF/celiac.pdf"),
                raw_pages,
                text_dir,
                "Screening for Celiac Disease",
            )
            extract.write_manifest(text_dir, [record], Path("C:/outside/guidelines-src"), producer=clean_producer())

            self.assertIn(
                citation,
                (text_dir / "USPSTF" / "celiac.txt").read_text(encoding="utf-8"),
            )
            results = ut.build(text_dir)
            self.assertEqual({row.year for row in results[0].rows}, {"2017"})

    def test_the_manifest_must_carry_the_title_key_even_when_its_value_is_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            text_dir = Path(tmp)
            record = extract.build_document(
                Path("USPSTF/rhrs.pdf"), fixture("ahrq-sentence-grade"), text_dir
            )
            manifest_path = extract.write_manifest(
                text_dir, [record], Path("C:/outside/guidelines-src"),
                producer=clean_producer(),
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            del manifest["documents"][0]["title"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "title"):
                ut.build(text_dir)


class GradeValidationTests(unittest.TestCase):
    """Grades are constrained to A B C D I; anything else fails rather than passing through."""

    def test_the_five_grades_pass(self):
        for letter in "ABCDI":
            self.assertEqual(ut.validate_grade(letter), letter)

    def test_lowercase_is_normalized(self):
        self.assertEqual(ut.validate_grade("b"), "B")

    def test_a_sixth_letter_raises(self):
        for letter in ("E", "F", "X", "1", ""):
            with self.assertRaises(ValueError):
                ut.validate_grade(letter)

    def test_a_marker_carrying_a_sixth_grade_fails_rather_than_vanishing(self):
        """The point of capturing any letter rather than only ``[ABCDI]``.

        Matching only the five would make the constraint a tautology: a bogus grade would
        not pass through, but it would not fail either -- the marker simply would not
        match, and the recommendation would disappear with nothing recorded.
        """
        with self.assertRaises(ValueError):
            ut.split_on_grade_markers(
                "The USPSTF recommends screening in adults. (E recommendation)"
            )

    def test_the_bare_letter_forms_stay_uppercase_so_an_article_is_not_a_grade(self):
        """``unable to make a recommendation.`` is a lowercase letter plus the same word."""
        text = "The USPSTF is unable to make\na recommendation.\n"
        self.assertEqual(ut.split_on_grade_markers(text), [])

    def test_every_row_the_builder_emits_carries_a_valid_grade(self):
        for name in FIXTURES:
            result = ut.parse_document(fixture(name), name + ".pdf")
            for row in result.rows:
                self.assertIn(row.grade, ut.GRADES, f"{name}: {row.grade!r}")


class MarkerSplittingTests(unittest.TestCase):
    def test_parenthetical_markers_split_one_paragraph_into_several_statements(self):
        text = (
            "The USPSTF recommends screening in adults. (B recommendation) "
            "The USPSTF recommends against screening in children. (D recommendation)"
        )
        self.assertEqual(
            [s.grade for s in ut.split_on_grade_markers(text)], ["B", "D"]
        )

    def test_a_bare_marker_on_its_own_line_counts(self):
        text = "The USPSTF recommends screening in adults.\nB recommendation\n"
        statements = ut.usable_statements(text)
        self.assertEqual([s.grade for s in statements], ["B"])

    def test_the_sentence_form_counts(self):
        text = (
            "The USPSTF strongly recommends Rh (D) blood typing for all pregnant women.\n"
            "A recommendation.\n"
        )
        self.assertEqual([s.grade for s in ut.usable_statements(text)], ["A"])

    def test_grade_prefixed_markers_count(self):
        text = "The USPSTF does not recommend screening in adult males. (Grade D recommendation)"
        self.assertEqual([s.grade for s in ut.usable_statements(text)], ["D"])

    def test_a_marker_is_not_counted_twice_by_two_patterns(self):
        text = "The USPSTF recommends screening in adults.\nB recommendation.\n"
        self.assertEqual(len(ut.usable_statements(text)), 1)

    def test_masthead_between_markers_is_not_a_statement(self):
        text = "Volume 328, Number 8 (Reprinted) jama.com (B recommendation)"
        self.assertEqual(ut.usable_statements(text), [])

    def test_text_that_ran_in_from_the_next_column_is_not_a_statement(self):
        """An all-caps abstract label inside a statement means two blocks got joined."""
        text = (
            "(Figure 1). IMPORTANCE More than 35% of men in the United States are obese. "
            "The USPSTF concludes that the evidence is adequate. (B recommendation)"
        )
        self.assertEqual(ut.usable_statements(text), [])

    def test_a_figure_caption_inside_a_statement_disqualifies_it(self):
        text = (
            "The USPSTF recommends screening in adults. "
            "Figure 1. USPSTF Grades and Levels of Certainty (B recommendation)"
        )
        self.assertEqual(ut.usable_statements(text), [])

    def test_a_parenthetical_figure_reference_does_not(self):
        text = "The USPSTF recommends screening in adults (Figure 1). (B recommendation)"
        self.assertEqual(len(ut.usable_statements(text)), 1)

    def test_a_superseded_recommendation_described_in_the_past_tense_is_not_a_row(self):
        """The 2000s AHRQ layout recounts the statement it replaces, with its old grade."""
        text = (
            "In 1996, the USPSTF recommended Rh (D) blood typing and antibody screening "
            "for all pregnant women at their first prenatal visit (A recommendation)."
        )
        self.assertEqual(ut.usable_statements(text), [])


class StatementTrimmingTests(unittest.TestCase):
    def test_leading_evidence_sentences_are_dropped(self):
        """The AHRQ layout prints the rationale before the grade, not after."""
        trimmed = ut.trim_to_recommendation(
            "The USPSTF found good evidence that Rh (D) blood typing prevents maternal "
            "sensitization. The benefits substantially outweigh any potential harms. "
            "The USPSTF recommends repeated Rh (D) antibody testing for all unsensitized "
            "Rh (D)-negative women at 24-28 weeks' gestation."
        )
        self.assertTrue(trimmed.startswith("The USPSTF recommends repeated"))

    def test_a_two_sentence_recommendation_keeps_both_sentences(self):
        """Trimming to the *last* recommending sentence would throw half of this away."""
        statement = (
            "The USPSTF recommends screening for hypertension in adults 18 years or older "
            "with office blood pressure measurement. The USPSTF recommends obtaining blood "
            "pressure measurements outside of the clinical setting for diagnostic "
            "confirmation before starting treatment."
        )
        self.assertEqual(ut.trim_to_recommendation(statement), statement)

    def test_a_statement_with_no_recommending_sentence_is_left_alone(self):
        text = "Something that names no verb at all."
        self.assertEqual(ut.trim_to_recommendation(text), text)


class SentenceSplittingTests(unittest.TestCase):
    def test_an_abbreviation_does_not_end_a_sentence(self):
        """Splitting at ``U.S.`` leaves a statement beginning ``Preventive Services``."""
        self.assertEqual(
            ut.split_sentences(
                "The U.S. Preventive Services Task Force recommends screening in adults."
            ),
            ["The U.S. Preventive Services Task Force recommends screening in adults."],
        )

    def test_an_ordinary_sentence_end_does(self):
        self.assertEqual(
            len(ut.split_sentences("It recommends screening in adults. Evidence is adequate.")),
            2,
        )

    def test_an_acronym_ending_a_sentence_still_ends_it(self):
        self.assertEqual(
            len(ut.split_sentences("The USPSTF recommends screening for AAA. Evidence is good.")),
            2,
        )


class RegionSelectionTests(unittest.TestCase):
    def test_the_abstract_wins_when_it_is_complete_and_spaced(self):
        region, statements = ut.choose_region(fixture("jama-abstract-multi"))
        self.assertEqual(region.kind, "abstract")
        self.assertEqual([s.grade for s in statements], ["B", "I", "I"])

    def test_a_glued_abstract_loses_to_a_spaced_region_stating_as_many(self):
        """The whole reason regions are scored rather than ranked.

        This document's abstract extracts as ``TheUSPSTFrecommendsscreening...`` with no
        space glyphs at all. The page-1 figure states the same two recommendations
        cleanly, so it wins on spacing despite sitting at lower priority.
        """
        pages = fixture("jama-glued-abstract")
        self.assertFalse(ut.spacing_ok(ut.candidate_regions(pages)[0].text))
        region, statements = ut.choose_region(pages)
        self.assertEqual(region.kind, "figure")
        self.assertEqual([s.grade for s in statements], ["B", "I"])
        self.assertIn("unhealthy drug use in adults", statements[0].text)

    def test_a_document_with_no_abstract_field_falls_back_to_the_summary_section(self):
        region, statements = ut.choose_region(fixture("summary-section"))
        self.assertEqual(region.kind, "summary")
        self.assertEqual([s.grade for s in statements], ["A"])

    def test_the_annals_recommendation_field_is_an_abstract_region(self):
        region, statements = ut.choose_region(fixture("annals-abstract"))
        self.assertEqual(region.kind, "abstract")
        self.assertEqual([s.grade for s in statements], ["I"])

    def test_the_masthead_recommendation_statement_line_is_not_an_abstract_label(self):
        """``... Task Force Recommendation Statement`` opens page 1 of every document.

        Matching it as the abstract label makes the masthead the first recommendation.
        """
        for name in FIXTURES:
            for region in ut.candidate_regions(fixture(name)):
                if region.kind == "abstract":
                    self.assertNotIn("Preventive Services Task Force*", region.text[:120], name)


class SpacingTests(unittest.TestCase):
    def test_ordinary_prose_is_spaced(self):
        self.assertTrue(ut.spacing_ok("The USPSTF recommends screening for hypertension in adults."))

    def test_a_paragraph_with_no_space_glyphs_is_not(self):
        self.assertFalse(
            ut.spacing_ok("TheUSPSTFrecommendsscreeningbyaskingquestionsaboutunhealthydruguse.")
        )

    def test_empty_text_is_not_spaced(self):
        self.assertFalse(ut.spacing_ok(""))


class PopulationTests(unittest.TestCase):
    def test_the_trailing_person_phrase_is_the_population(self):
        self.assertEqual(
            ut.derive_population(
                "The USPSTF recommends biennial screening mammography for women aged 40 to 74 years."
            ),
            "women aged 40 to 74 years",
        )

    def test_a_relative_clause_stays_with_the_population(self):
        self.assertEqual(
            ut.derive_population(
                "The USPSTF recommends 1-time screening for AAA with ultrasonography in men "
                "aged 65 to 75 years who have ever smoked."
            ),
            "men aged 65 to 75 years who have ever smoked",
        )

    def test_the_c_grade_predicate_is_cut_off_the_population(self):
        self.assertEqual(
            ut.derive_population(
                "The decision to initiate low-dose aspirin use for the primary prevention of "
                "CVD in adults aged 40 to 59 years who have a 10% or greater 10-year CVD risk "
                "should be an individual one."
            ),
            "adults aged 40 to 59 years who have a 10% or greater 10-year CVD risk",
        )

    def test_an_irregular_plural_is_a_population(self):
        """``... osteoporotic fractures in men.`` otherwise reads as naming nobody."""
        self.assertEqual(
            ut.derive_population(
                "The USPSTF concludes that the evidence is insufficient to assess screening "
                "for osteoporosis to prevent osteoporotic fractures in men."
            ),
            "men",
        )

    def test_a_singular_person_noun_modifying_a_condition_is_not_a_population(self):
        """``adolescent idiopathic scoliosis`` names a disease, not the people screened."""
        self.assertEqual(
            ut.derive_population(
                "The USPSTF concludes that the evidence is insufficient to assess screening "
                "for adolescent idiopathic scoliosis in children and adolescents aged 10 to "
                "18 years."
            ),
            "children and adolescents aged 10 to 18 years",
        )

    def test_a_qualifier_list_stays_with_the_population(self):
        self.assertEqual(
            ut.derive_population(
                "The USPSTF recommends that clinicians refer pregnant and postpartum persons "
                "who are at increased risk of perinatal depression to counseling."
            ),
            "pregnant and postpartum persons who are at increased risk of perinatal "
            "depression to counseling",
        )

    def test_the_first_mention_wins_so_half_a_population_is_never_dropped(self):
        """Taking the last mention silently loses the under-25 half of this one."""
        self.assertEqual(
            ut.derive_population(
                "The USPSTF recommends screening for chlamydia in all sexually active women "
                "24 years or younger and in women 25 years or older who are at increased "
                "risk for infection."
            ),
            "all sexually active women 24 years or younger and in women 25 years or older "
            "who are at increased risk for infection",
        )

    def test_a_trailing_evidence_sentence_is_not_the_population(self):
        self.assertEqual(
            ut.derive_population(
                "The USPSTF recommends that clinicians selectively offer screening for "
                "colorectal cancer in adults aged 76 to 85 years. Evidence indicates that "
                "the net benefit of screening all persons in this age group is small."
            ),
            "adults aged 76 to 85 years",
        )

    def test_a_statement_naming_no_population_falls_back_to_the_document_field(self):
        statement = (
            "The USPSTF concludes that the current evidence is insufficient to assess the "
            "balance of benefits and harms of screening for AF."
        )
        self.assertEqual(
            ut.derive_population(statement, "adults 50 years or older"),
            "adults 50 years or older",
        )

    def test_with_neither_the_cell_says_so_rather_than_guessing(self):
        self.assertEqual(ut.derive_population("The USPSTF concludes ... for AF."), ut.NOT_STATED)

    def test_the_document_population_field_is_read_off_the_abstract(self):
        self.assertEqual(
            ut.document_population(fixture("jama-abstract-single")),
            "Adults 18 years or older without known hypertension",
        )

    def test_the_annals_population_field_drops_its_applies_to_preamble(self):
        self.assertEqual(
            ut.document_population(fixture("annals-abstract")),
            "nonpregnant, asymptomatic adults",
        )


class IntervalTests(unittest.TestCase):
    def test_biennial_is_an_interval(self):
        self.assertEqual(
            ut.derive_interval("The USPSTF recommends biennial screening mammography."), "biennial"
        )

    def test_every_n_years_is_an_interval(self):
        self.assertEqual(
            ut.derive_interval(
                "The USPSTF recommends screening for cervical cancer every 3 years with cytology."
            ),
            "every 3 years",
        )

    def test_one_time_screening_is_an_interval(self):
        self.assertEqual(
            ut.derive_interval("The USPSTF recommends 1-time screening for AAA."), "1-time"
        )

    def test_imprecise_and_count_recurrences_stay_in_the_service_interval_vocabulary(self):
        examples = {
            "repeated": "The USPSTF recommends repeated screening.",
            "periodic": "The USPSTF recommends periodic screening.",
            "1-time": "The USPSTF recommends 1-time screening.",
            "at least once": "The USPSTF recommends screening at least once.",
        }
        for expected, statement in examples.items():
            with self.subTest(expected=expected):
                self.assertEqual(ut.derive_interval(statement), expected)

    def test_each_declared_interval_exclusion_is_outside_the_vocabulary(self):
        for phrase, reason in ut.INTERVAL_EXCLUSIONS:
            with self.subTest(phrase=phrase):
                self.assertIsNone(ut.INTERVAL_PHRASE.search(phrase))
                self.assertTrue(reason)

    def test_daily_dose_frequency_is_not_a_service_interval(self):
        self.assertEqual(
            ut.derive_interval(
                "The USPSTF recommends a daily supplement containing 0.4 to 0.8 mg."
            ),
            ut.NOT_STATED,
        )

    def test_most_statements_name_none_and_say_so(self):
        self.assertEqual(
            ut.derive_interval(
                "The USPSTF recommends against screening for thyroid cancer in asymptomatic adults."
            ),
            ut.NOT_STATED,
        )


class TopicAndYearTests(unittest.TestCase):
    def test_the_title_runs_until_the_task_force_masthead(self):
        self.assertEqual(ut.derive_topic(fixture("jama-abstract-multi"), "x.pdf"), "Screening for Breast Cancer")

    def test_an_annals_title_keeps_the_part_before_the_masthead_on_the_same_line(self):
        self.assertEqual(
            ut.derive_topic(fixture("annals-abstract"), "x.pdf"), "Screening for Thyroid Dysfunction"
        )

    def test_a_running_head_above_the_title_is_skipped_not_stopped_at(self):
        """Four documents print all three of these before the title."""
        pages = ["""Clinical Review & Education
(Reprinted)
JAMA | US Preventive Services Task Force | RECOMMENDATION STATEMENT
Screening for Chlamydia and Gonorrhea
US Preventive Services Task Force Recommendation Statement
"""]
        self.assertEqual(ut.derive_topic(pages, "x.pdf"), "Screening for Chlamydia and Gonorrhea")

    def test_nothing_below_the_masthead_is_collected_as_a_title(self):
        """The AHRQ layout opens with the recommendation itself, under a section heading."""
        pages = ["""Summary of
Recommendations
The U.S. Preventive Services Task Force
(USPSTF) strongly recommends Rh (D) blood
typing and antibody testing for all pregnant women
"""]
        self.assertEqual(
            ut.derive_topic(
                pages,
                "rhrs.pdf",
                "Screening for Rh (D) Incompatibility - Recommendation Statement",
            ),
            "Screening for Rh (D) Incompatibility",
        )

    def test_a_glued_page_title_loses_to_the_metadata_title(self):
        pages = ["VitaminD,CalciumSupplementationforthePrimaryPreventionofFractures"]
        self.assertEqual(
            ut.derive_topic(
                pages,
                "x.pdf",
                "Vitamin D, Calcium, or Combined Supplementation: USPSTF Recommendation Statement",
            ),
            "Vitamin D, Calcium, or Combined Supplementation",
        )

    def test_a_page_and_metadata_with_no_title_fall_back_to_the_filename(self):
        """A print-to-PDF web capture opens with an icon-font glyph, not a title."""
        pages = ["\n\ue900 Metrics\n"]
        self.assertEqual(
            ut.derive_topic(pages, "screening-for-thyroid-cancer.pdf"),
            "screening for thyroid cancer",
        )

    def test_parse_document_records_the_topic_route_used_at_build_time(self):
        page_result = ut.parse_document(
            fixture("jama-abstract-multi"), "page.pdf", "Ignored metadata title"
        )
        declared_result = ut.parse_document(
            fixture("ahrq-sentence-grade"),
            "declared.pdf",
            "Screening for Rh (D) Incompatibility - Recommendation Statement",
        )
        filename_result = ut.parse_document(
            fixture("ahrq-sentence-grade"), "filename-route.pdf"
        )

        self.assertEqual(page_result.topic_route, ut.TOPIC_ROUTE_PAGE)
        self.assertEqual(
            declared_result.topic_route, ut.TOPIC_ROUTE_DECLARED_FIELD
        )
        self.assertEqual(filename_result.topic_route, ut.TOPIC_ROUTE_FILENAME)

    def test_the_year_comes_from_the_journal_citation(self):
        self.assertEqual(ut.derive_year(fixture("jama-abstract-multi")), "2024")
        self.assertEqual(ut.derive_year(fixture("annals-abstract")), "2015")

    def test_the_doi_is_not_mistaken_for_a_year(self):
        """``doi:10.1001/jama.2023.5634`` otherwise reads as the year 1001."""
        self.assertEqual(ut.derive_year(["JAMA. doi:10.1001/jama.2024.27154\nPublished online January 14, 2025.\n"]), "2025")


class NormalizationTests(unittest.TestCase):
    def test_ligatures_are_folded(self):
        self.assertEqual(ut.normalize("insuﬁcient beneﬁts"), "insuficient benefits")

    def test_en_dashes_become_hyphens(self):
        """Cosmetic in a citation range, not cosmetic in ``130-139 mmHg``."""
        self.assertEqual(ut.normalize("130–139 mmHg"), "130-139 mmHg")

    def test_a_hyphenated_line_break_is_rejoined(self):
        self.assertEqual(ut.unwrap("screen-\ning for cancer"), "screening for cancer")


class SupersessionTests(unittest.TestCase):
    def test_the_older_of_two_files_on_one_topic_is_marked(self):
        rows = [
            ut.Row("Screening for Breast Cancer", "women", "B", "biennial", "2016", "old.pdf", 1),
            ut.Row("Screening for Breast Cancer", "women", "B", "biennial", "2024", "new.pdf", 1),
        ]
        ut.mark_superseded(rows)
        self.assertEqual(rows[0].superseded_by, "new.pdf")
        self.assertEqual(rows[1].superseded_by, "")

    def test_a_topic_with_one_file_is_not_marked(self):
        rows = [ut.Row("Screening for Ovarian Cancer", "women", "D", "n/a", "2018", "only.pdf", 1)]
        ut.mark_superseded(rows)
        self.assertEqual(rows[0].superseded_by, "")

    def test_topic_keys_ignore_the_screening_for_prefix_and_case(self):
        self.assertEqual(
            ut.topic_key("Screening for Breast Cancer"), ut.topic_key("BREAST CANCER")
        )

    def test_an_undated_file_is_reported_rather_than_left_silently_unmarked(self):
        """An undated statement is not thereby the older one, so neither row is marked.

        Leaving it at that would read exactly like a topic with no update at all, which is
        the one thing the spec asks supersession not to do.
        """
        rows = [
            ut.Row("Screening for Rh (D) Incompatibility", "women", "A", "n/a", ut.NOT_STATED, "old.pdf", 1),
            ut.Row("Screening for Rh (D) Incompatibility", "women", "A", "n/a", "2024", "new.pdf", 1),
        ]
        _, unresolved = ut.mark_superseded(rows)
        self.assertEqual([r.superseded_by for r in rows], ["", ""])
        self.assertEqual(len(unresolved), 1)
        self.assertIn("old.pdf", unresolved[0])
        self.assertIn("new.pdf", unresolved[0])

    def test_a_dated_pair_is_ordered_and_reports_nothing_unresolved(self):
        rows = [
            ut.Row("Topic", "adults", "B", "n/a", "2016", "old.pdf", 1),
            ut.Row("Topic", "adults", "B", "n/a", "2024", "new.pdf", 1),
        ]
        _, unresolved = ut.mark_superseded(rows)
        self.assertEqual(unresolved, [])

    def test_two_files_of_the_same_year_supersede_neither(self):
        rows = [
            ut.Row("Topic", "adults", "B", "n/a", "2020", "a.pdf", 1),
            ut.Row("Topic", "adults", "B", "n/a", "2020", "b.pdf", 1),
        ]
        ut.mark_superseded(rows)
        self.assertEqual([r.superseded_by for r in rows], ["", ""])


class DocumentTests(unittest.TestCase):
    def test_every_fixture_contributes_at_least_one_row(self):
        for name in FIXTURES:
            result = ut.parse_document(fixture(name), name + ".pdf")
            self.assertTrue(result.rows, f"{name} contributed no rows: {result.reason}")

    def test_every_row_carries_its_filename_and_page(self):
        for name in FIXTURES:
            for row in ut.parse_document(fixture(name), "/corpus/" + name + ".pdf").rows:
                self.assertEqual(row.filename, name + ".pdf")
                self.assertGreaterEqual(row.page, 1)

    def test_a_document_with_no_grade_marker_records_a_reason_rather_than_vanishing(self):
        result = ut.parse_document(["Nothing here resembles a recommendation."], "empty.pdf")
        self.assertEqual(result.rows, [])
        self.assertTrue(result.reason)

    def test_a_document_with_no_pages_records_a_reason(self):
        result = ut.parse_document([], "blank.pdf")
        self.assertEqual(result.rows, [])
        self.assertIn("no extractable text", result.reason)

    def test_the_breast_cancer_fixture_parses_to_its_three_known_rows(self):
        rows = ut.parse_document(fixture("jama-abstract-multi"), "breast.pdf").rows
        self.assertEqual([r.grade for r in rows], ["B", "I", "I"])
        self.assertEqual(rows[0].population, "women aged 40 to 74 years")
        self.assertEqual(rows[0].interval, "biennial")
        self.assertEqual(rows[0].year, "2024")
        self.assertEqual(rows[0].topic, "Screening for Breast Cancer")

    def test_a_document_population_records_the_field_quotation_decision(self):
        pages = [
            "POPULATION Adults 50 years or older.\nRECOMMENDATION The USPSTF "
            "concludes that the evidence is insufficient to assess screening for AF. "
            "(I recommendation)"
        ]

        row = ut.parse_document(pages, "af.pdf").rows[0]

        self.assertEqual(row.population, "Adults 50 years or older")
        self.assertTrue(row.population_from_declared_field)

    def test_not_stated_is_not_a_field_quotation(self):
        row = ut.parse_document(
            ["RECOMMENDATION The USPSTF concludes that the evidence is insufficient to assess AF. "
             "(I recommendation)"],
            "af.pdf",
        ).rows[0]

        self.assertEqual(row.population, ut.NOT_STATED)
        self.assertFalse(row.population_from_declared_field)


class ThresholdSheetJoinTests(unittest.TestCase):
    def test_catalog_filename_joins_to_the_coverage_artifact_through_catalog_topic(self):
        catalog = """| society | filename | title | topic | population | year | page_count | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| USPSTF | cervical.pdf | Cervical title | cervical cancer screening | adult | 2018 | 13 | recommendation-statement |
| USPSTF | breast.pdf | Breast title | breast cancer screening | adult | 2024 | 12 | recommendation-statement |
"""
        coverage = """# Threshold-sheet coverage

<!-- schema: threshold-coverage/2 -->

| topic | state | artifact | record |
| --- | --- | --- | --- |
| breast cancer screening | unread |  | full-document read pending |
| cervical cancer screening | unread | cervical-cancer.md | partial artifact |
"""

        self.assertEqual(
            ut.threshold_sheets_by_filename(catalog, coverage),
            {"cervical.pdf": "cervical-cancer.md"},
        )


class RenderingTests(unittest.TestCase):
    def test_threshold_sheet_column_joins_on_filename_and_leaves_no_match_empty(self):
        with_sheet = ut.DocumentResult(
            "cervical-cancer-final-rec-statement.pdf",
            rows=[
                ut.Row(
                    "Screening for Cervical Cancer",
                    "women aged 21 to 29 years",
                    "A",
                    "every 3 years",
                    "2018",
                    "cervical-cancer-final-rec-statement.pdf",
                    1,
                )
            ],
        )
        without_sheet = ut.DocumentResult(
            "breast-cancer-screening-final-recommendation.pdf",
            rows=[
                ut.Row(
                    "Screening for Breast Cancer",
                    "women aged 40 to 74 years",
                    "B",
                    "biennial",
                    "2024",
                    "breast-cancer-screening-final-recommendation.pdf",
                    1,
                )
            ],
        )

        markdown = ut.render_markdown(
            [with_sheet, without_sheet],
            threshold_sheets={
                "cervical-cancer-final-rec-statement.pdf": "cervical-cancer.md"
            },
        )
        without_pointer = ut.render_markdown([with_sheet, without_sheet])

        self.assertIn("| Threshold sheet | File | Page |", markdown)
        self.assertIn(
            "| [cervical-cancer.md](thresholds/cervical-cancer.md) | "
            "`cervical-cancer-final-rec-statement.pdf` | 1 |",
            markdown,
        )
        self.assertIn(
            "|  | `breast-cancer-screening-final-recommendation.pdf` | 1 |",
            markdown,
        )
        self.assertIn(
            "`Threshold sheet` points to a sheet about the same source document; "
            "it does not claim that the two artifacts agree.",
            markdown,
        )
        self.assertEqual(
            markdown.replace(
                "[cervical-cancer.md](thresholds/cervical-cancer.md)", ""
            ),
            without_pointer,
            "the derived pointer must be the only byte changed by a filename match",
        )

    def test_the_header_points_to_the_generated_disclosure_sections(self):
        markdown = ut.render_markdown(
            [ut.parse_document(fixture("jama-abstract-multi"), "breast.pdf")]
        )
        self.assertIn(
            "Topic and population field quotations and documents stating that the "
            "USPSTF found no interval evidence are listed in sections below.",
            markdown,
        )
        self.assertNotIn("A document may state elsewhere", markdown)
        self.assertIn(
            "Where a recommendation offers alternatives, `interval` names every recurrence "
            "of a recommended service that its statement names, joined with "
            f"`{ut.INTERVAL_ALTERNATIVE_JOIN.strip()}`; the modality that distinguishes them "
            "is in `## Statements` and not in the cell. A dose or supplement frequency is "
            "not a recurrence and is deliberately outside the column.",
            markdown,
        )

    def test_topic_section_includes_declared_fields_and_excludes_filename_slugs(self):
        declared = ut.DocumentResult(
            "declared.pdf",
            rows=[
                ut.Row(
                    "Declared Topic",
                    "adults",
                    "B",
                    ut.NOT_STATED,
                    "2026",
                    "declared.pdf",
                    1,
                )
            ],
            topic_route=ut.TOPIC_ROUTE_DECLARED_FIELD,
        )
        filename = ut.DocumentResult(
            "filename-route.pdf",
            rows=[
                ut.Row(
                    "filename route",
                    "adults",
                    "B",
                    ut.NOT_STATED,
                    "2026",
                    "filename-route.pdf",
                    1,
                )
            ],
            topic_route=ut.TOPIC_ROUTE_FILENAME,
        )

        section = ut.render_markdown([declared, filename]).split(
            "## Topic cells quoted from the declared field", 1
        )[1].split("\n## ", 1)[0]

        self.assertIn("| Declared Topic | `declared.pdf` |", section)
        self.assertNotIn("filename-route.pdf", section)
        self.assertIn("The filename-slug route is excluded", section)

    def test_the_module_contract_points_to_the_column_owners(self):
        contract = " ".join(ut.__doc__.split())
        self.assertIn(
            "When page 1 has no usable title, ``derive_topic`` reads that manifest field",
            contract,
        )
        self.assertNotIn("Three documents have no usable title", contract)
        self.assertIn(
            "``derive_population`` owns the population column's source-selection rule.",
            contract,
        )
        self.assertIn(
            "The ``interval`` column is derived from the statement text alone",
            contract,
        )
        self.assertNotIn("``population`` and ``interval`` columns are", contract)

    def test_population_field_quotation_section_derives_both_counts(self):
        results = [
            ut.DocumentResult(
                "field.pdf",
                rows=[
                    ut.Row(
                        "Topic",
                        "adults",
                        "B",
                        "not stated",
                        "2024",
                        "field.pdf",
                        2,
                        population_from_declared_field=True,
                    ),
                    ut.Row(
                        "Topic",
                        "adults",
                        "I",
                        "not stated",
                        "2024",
                        "field.pdf",
                        2,
                        population_from_declared_field=True,
                    ),
                    ut.Row(
                        "Topic",
                        "older adults",
                        "I",
                        "not stated",
                        "2024",
                        "field.pdf",
                        2,
                    ),
                ],
            )
        ]

        markdown = ut.render_markdown(results)

        self.assertIn("## Population cells quoted from the declared field", markdown)
        self.assertIn("2 recommendation rows form 1 population-and-document pair.", markdown)
        self.assertEqual(markdown.count("| adults | `field.pdf` | 2 |"), 1)

    def test_interval_absence_section_renders_the_declared_reading(self):
        markdown = ut.render_markdown([])

        self.assertIn("## Documents stating no interval evidence was found", markdown)
        for entry in ut.INTERVAL_ABSENCES:
            self.assertIn(f"`{entry.filename}`", markdown)
            self.assertIn(str(entry.page), markdown)
            quotation = f"{'RENDERED: ' if entry.rendered else ''}{entry.quotation}"
            self.assertIn(quotation, markdown)

    def test_a_pipe_in_a_cell_is_escaped_so_it_cannot_break_the_table(self):
        self.assertEqual(ut.escape_cell("a | b"), "a \\| b")

    def test_the_table_names_every_document_that_contributed_nothing(self):
        results = [
            ut.parse_document(fixture("jama-abstract-multi"), "breast.pdf"),
            ut.DocumentResult("broken.pdf", reason="extraction failed: bad xref"),
        ]
        markdown = ut.render_markdown(results)
        self.assertIn("`broken.pdf`", markdown)
        self.assertIn("extraction failed: bad xref", markdown)

    def test_an_empty_supersession_column_says_the_check_ran(self):
        """Otherwise a column of blanks reads the same as a check nobody performed."""
        markdown = ut.render_markdown(
            [ut.parse_document(fixture("jama-abstract-multi"), "breast.pdf")]
        )
        self.assertIn("## Supersession", markdown)
        self.assertIn("**None.** The check ran", markdown)

    def test_a_superseded_row_is_reported_rather_than_dropped(self):
        old = ut.DocumentResult(
            "old.pdf",
            rows=[ut.Row("Screening for Breast Cancer", "women", "B", "annual", "2016", "old.pdf", 1)],
        )
        new = ut.DocumentResult(
            "new.pdf",
            rows=[ut.Row("Screening for Breast Cancer", "women", "B", "biennial", "2024", "new.pdf", 1)],
        )
        markdown = ut.render_markdown([old, new])
        self.assertNotIn("**None.** The check ran", markdown)
        self.assertIn("1 row comes from a file", markdown)
        self.assertIn("| new.pdf |  | `old.pdf` | 1 |", markdown)

    def test_the_table_carries_a_row_per_recommendation(self):
        results = [ut.parse_document(fixture("jama-abstract-multi"), "breast.pdf")]
        markdown = ut.render_markdown(results)
        self.assertIn("| `breast.pdf` | 1 |", markdown)
        self.assertEqual(markdown.count("| `breast.pdf` | 1 |"), 6)  # 3 rows, 2 tables


FIXTURES = (
    "jama-abstract-multi",
    "jama-abstract-single",
    "jama-glued-abstract",
    "annals-abstract",
    "summary-section",
    "ahrq-sentence-grade",
)


if __name__ == "__main__":
    unittest.main()
