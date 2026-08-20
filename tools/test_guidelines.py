"""Tests for guidelines_index.py and guidelines_search.py, the pair.

One file for both, the way test_icd10.py covers icd10_build.py and icd10_lookup.py:
the builder and the reader agree on a schema, and a test that exercised one without
the other would pass on an index no query could read.

Every test builds a throwaway text directory and a throwaway index in a temp
directory, the way test_skills_mirror.py builds throwaway checkouts. **Nothing
here reads the real corpus or the real index** -- the corpus is 179 copyrighted
PDFs outside the repo and the index is a build artifact that may not exist on
the machine running the tests, so a test that touched either would pass or fail
on the state of that machine.

The corpus is also the reason no page text here is real guideline text: these
fixtures are invented sentences shaped like guideline prose, not excerpts.
"""

import io
import json
import os
import sqlite3
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import guidelines_index as gi
import guidelines_search as gs
from repo_root import InsideCheckout

TOOLS = Path(__file__).resolve().parent

# Invented prose, shaped like a threshold table so the line-attribution tests
# have something with a number in it to find.
HYPERTENSION_PAGE = """\
Table 6. Blood pressure thresholds for initiating therapy
Stage 1 hypertension 130-139 mmHg systolic or 80-89 mmHg diastolic
Stage 2 hypertension 140 mmHg or higher systolic
Confirm with out-of-office measurement before starting a medication.
"""

PYELONEPHRITIS_PAGE = """\
Acute uncomplicated pyelonephritis in an outpatient adult
An oral fluoroquinolone remains an option where local resistance is below ten percent.
Obtain a urine culture in every patient before the first dose.
"""

# Issue #150. Invented prose like the rest, but carrying the characters cp1252 has
# no code point for -- the greater-or-equal sign a threshold is written with, an en
# dash, a typographic apostrophe and a mu. `>=` is the one that found the defect,
# because it is how every guideline writes a cut point.
THRESHOLD_PAGE = """\
Grading systemic inflammation at the first assessment
Classify the foot as grade 3 with fewer than two SIRS criteria, or grade 4 if ≥2.
The 2019–2024 cohort’s median clearance was 40 μmol/L.
"""


def write_single(text_dir: Path, doc_id: str, pages):
    """Whole-document layout: <text-dir>/<doc_id>.txt, pages split on form feed."""
    path = text_dir / f"{doc_id}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\f".join(pages), encoding="utf-8")
    return path


def write_manifest(text_dir: Path, documents):
    path = text_dir / "manifest.json"
    path.write_text(json.dumps({"documents": documents}), encoding="utf-8")
    return path


class TempCorpus(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        # addCleanup rather than tearDown, and registered first so it runs last:
        # cleanups are LIFO, and Windows refuses to delete a database file that a
        # test's still-open connection is holding.
        self.addCleanup(self._tmp.cleanup)
        # resolve() so comparisons survive macOS /var -> /private/var and any
        # Windows short-name form of the temp path.
        self.root = Path(self._tmp.name).resolve()
        self.text_dir = self.root / "guidelines-text"
        self.text_dir.mkdir()
        self.db = self.root / "guidelines-index" / "guidelines.sqlite"

    def build_default_corpus(self):
        write_single(self.text_dir, "AHA ACC/2017-hypertension", ["cover page", HYPERTENSION_PAGE])
        write_single(self.text_dir, "IDSA/2010-uti", ["cover page", PYELONEPHRITIS_PAGE])
        return gi.build(self.text_dir, self.db)


class DiscoveryTests(TempCorpus):
    def test_a_single_txt_is_one_document_split_on_form_feed(self):
        write_single(self.text_dir, "GOLD/2026-copd", ["one", "two"])
        documents = list(gi.discover(self.text_dir))
        self.assertEqual([d.doc_id for d in documents], ["GOLD/2026-copd"])
        self.assertEqual([p.number for p in documents[0].pages], [1, 2])

    def test_society_is_the_top_directory_segment(self):
        write_single(self.text_dir, "AHA ACC/2017-hypertension", ["one"])
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        self.assertEqual(
            sorted(d.society for d in gi.discover(self.text_dir)), ["AHA ACC", "IDSA"]
        )

    def test_a_document_at_the_root_has_no_society(self):
        write_single(self.text_dir, "loose", ["one"])
        self.assertIsNone(list(gi.discover(self.text_dir))[0].society)

    def test_blank_pages_are_kept_so_page_numbers_stay_true(self):
        """A page that extracted to nothing still occupies its page number. Dropping
        it would slide every later page's citation by one."""
        write_single(self.text_dir, "USPSTF/screening", ["one", "   \n", "three"])
        pages = list(gi.discover(self.text_dir))[0].pages
        self.assertEqual([p.number for p in pages], [1, 2, 3])

    def test_non_txt_files_are_ignored(self):
        write_single(self.text_dir, "USPSTF/screening", ["one"])
        (self.text_dir / "USPSTF" / "notes.md").write_text("x", encoding="utf-8")
        write_manifest(self.text_dir, [{"doc_id": "USPSTF/screening"}])
        documents = list(gi.discover(self.text_dir))
        self.assertEqual([d.doc_id for d in documents], ["USPSTF/screening"])

    def test_a_bare_numeric_stem_is_a_document_not_a_page(self):
        """USPSTF/2021.txt and USPSTF/2022.txt are two documents. Read as page numbers
        they collapse into one document called USPSTF carrying pages 2021 and 2022 --
        two documents lost and two citations invented, with nothing downstream able to
        tell. The `page` prefix is what separates the cases."""
        write_single(self.text_dir, "USPSTF/2021", ["prediabetes"])
        write_single(self.text_dir, "USPSTF/2022", ["hypertension"])
        documents = list(gi.discover(self.text_dir))
        self.assertEqual([d.doc_id for d in documents], ["USPSTF/2021", "USPSTF/2022"])
        self.assertEqual([p.number for d in documents for p in d.pages], [1, 1])

    def test_documents_come_back_in_a_stable_order(self):
        for doc_id in ("USPSTF/b", "IDSA/a", "AHA ACC/c"):
            write_single(self.text_dir, doc_id, ["one"])
        self.assertEqual(
            [d.doc_id for d in gi.discover(self.text_dir)],
            ["AHA ACC/c", "IDSA/a", "USPSTF/b"],
        )

    def test_a_missing_text_directory_is_loud(self):
        with self.assertRaises(FileNotFoundError):
            list(gi.discover(self.root / "nowhere"))


class ManifestTests(TempCorpus):
    def test_manifest_supplies_title_and_class(self):
        write_single(self.text_dir, "ACIP/2026-schedule", ["one"])
        write_manifest(
            self.text_dir,
            [
                {
                    "doc_id": "ACIP/2026-schedule",
                    "title": "Child and adolescent immunization schedule",
                    "document_class": "browser-capture",
                    "society": "CDC",
                }
            ],
        )
        document = list(gi.discover(self.text_dir))[0]
        self.assertEqual(document.title, "Child and adolescent immunization schedule")
        self.assertEqual(document.document_class, "browser-capture")
        self.assertEqual(document.society, "CDC")

    def test_no_manifest_is_not_an_error(self):
        write_single(self.text_dir, "ACIP/2026-schedule", ["one"])
        document = list(gi.discover(self.text_dir))[0]
        self.assertIsNone(document.title)
        self.assertEqual(document.document_class, gi.UNCLASSIFIED)

    def test_a_manifest_entry_for_a_document_with_no_text_is_reported(self):
        """#80 records an extraction failure rather than skipping silently. The index
        has nothing to index for it, and must say so rather than swallow it."""
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        write_manifest(self.text_dir, [{"doc_id": "IDSA/2010-uti"}, {"doc_id": "IDSA/2014-ssti"}])
        report = gi.build(self.text_dir, self.db)
        self.assertEqual(report.manifest_only, ["IDSA/2014-ssti"])

    def test_an_unreadable_manifest_is_loud(self):
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        (self.text_dir / "manifest.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            gi.read_manifest(self.text_dir)

    def test_a_manifest_of_the_wrong_shape_is_loud_not_empty(self):
        """Read as empty, it would blank every title and document class while looking
        exactly like a corpus that never had them. #80 owns this file's shape, so a
        mismatch has to arrive as a failure rather than as missing metadata."""
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        (self.text_dir / "manifest.json").write_text('{"files": {}}', encoding="utf-8")
        with self.assertRaises(ValueError):
            gi.read_manifest(self.text_dir)

    def test_a_manifest_keyed_by_something_else_is_loud_not_empty(self):
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        write_manifest(self.text_dir, [{"document": "IDSA/2010-uti", "title": "UTI"}])
        with self.assertRaises(ValueError):
            gi.read_manifest(self.text_dir)


class RepoContainmentTests(TempCorpus):
    """The index is large and every worktree materializes what lands in one.
    Writing it inside a checkout is the failure this guard exists for, and `git status` being clean
    after a build is a done-when on #84.

    **The detection rule is not tested here any more** -- it moved to
    ``repo_root.enclosing_checkout`` on #176, and ``test_repo_root.py`` grades it.
    What stays is the thing that is this module's own: that ``build`` consults it
    before it writes, and that the refusal reaches a caller as one exception type.
    ``repo_roots`` went with the rule; the seam is a real ``.git`` entry now,
    which is a truer fixture than a list of paths asserted to be roots.
    """

    def checkout(self, name: str = "clinical_skills") -> Path:
        repo = self.root / name
        (repo / ".git").mkdir(parents=True)
        return repo

    def test_build_refuses_a_database_inside_a_checkout(self):
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        repo = self.checkout()
        with self.assertRaises(InsideCheckout):
            gi.build(self.text_dir, repo / "reference" / "g.sqlite")

    def test_build_refuses_before_it_writes_anything(self):
        """A guard consulted after ``mkdir`` leaves the directory behind, which is
        the artifact the ticket is about arriving in the tree anyway."""
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        repo = self.checkout()
        with self.assertRaises(InsideCheckout):
            gi.build(self.text_dir, repo / "reference" / "g.sqlite")
        self.assertFalse((repo / "reference").exists())

    def test_the_command_line_reports_a_refusal_as_did_not_scan(self):
        """``main`` needed no new handler: ``InsideCheckout`` is a ``ValueError``
        and lands on the one already there, which returns 2 -- did not build."""
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        repo = self.checkout()
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            status = gi.main([str(self.text_dir), str(repo / "reference" / "g.sqlite")])
        self.assertEqual(status, 2)
        self.assertIn("git checkout", stderr.getvalue())

    def test_a_sibling_of_the_checkout_is_built(self):
        write_single(self.text_dir, "IDSA/2010-uti", ["one"])
        self.checkout()
        report = gi.build(self.text_dir, self.root / "guidelines-index" / "g.sqlite")
        self.assertTrue(report.database.exists())

    def test_the_main_checkout_is_found_from_inside_a_worktree(self):
        """A worktree's .git is a file pointing at the main checkout. Resolving it
        wrong puts the default index under .claude/worktrees/, which is in the repo."""
        main = self.root / "clinical_skills"
        (main / ".git" / "worktrees" / "ticket-84").mkdir(parents=True)
        (main / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        worktree = main / ".claude" / "worktrees" / "ticket-84"
        (worktree / "tools").mkdir(parents=True)
        (worktree / ".git").write_text(
            f"gitdir: {(main / '.git' / 'worktrees' / 'ticket-84').as_posix()}\n", encoding="utf-8"
        )
        self.assertEqual(gi.main_repo_root(worktree / "tools"), main)

    def test_a_plain_checkout_is_its_own_main_root(self):
        main = self.root / "clinical_skills"
        (main / ".git").mkdir(parents=True)
        (main / "tools").mkdir()
        self.assertEqual(gi.main_repo_root(main / "tools"), main)


class BuildTests(TempCorpus):
    def test_the_report_counts_what_went_in(self):
        report = self.build_default_corpus()
        self.assertEqual(report.documents, 2)
        self.assertEqual(report.pages, 4)
        self.assertEqual(
            report.characters, len(HYPERTENSION_PAGE) + len(PYELONEPHRITIS_PAGE) + len("cover page") * 2
        )

    def test_the_database_lands_where_it_was_asked_to(self):
        self.build_default_corpus()
        self.assertTrue(self.db.exists())

    def test_meta_records_what_it_was_built_from(self):
        self.build_default_corpus()
        connection = gs.open_index(self.db)
        try:
            meta = dict(connection.execute("SELECT key, value FROM meta").fetchall())
        finally:
            connection.close()
        self.assertEqual(meta["text_dir"], str(self.text_dir))
        self.assertEqual(meta["schema_version"], str(gi.SCHEMA_VERSION))
        self.assertEqual(meta["documents"], "2")

    def test_rebuilding_replaces_rather_than_doubles(self):
        self.build_default_corpus()
        report = self.build_default_corpus()
        self.assertEqual(report.pages, 4)
        connection = gs.open_index(self.db)
        try:
            self.assertEqual(connection.execute("SELECT count(*) FROM page").fetchone()[0], 4)
        finally:
            connection.close()

    def test_an_empty_text_directory_is_loud(self):
        """Building an index over nothing produces a file that answers every query
        with zero hits. That is the failure this ticket names."""
        with self.assertRaises(ValueError):
            gi.build(self.text_dir, self.db)


class SearchTests(TempCorpus):
    def setUp(self):
        super().setUp()
        self.build_default_corpus()
        self.connection = gs.open_index(self.db)
        self.addCleanup(self.connection.close)

    def test_a_hit_carries_filename_page_and_line(self):
        hits = gs.search(self.connection, "stage 1 hypertension")
        self.assertEqual(len(hits), 1)
        hit = hits[0]
        self.assertEqual(hit.doc_id, "AHA ACC/2017-hypertension")
        self.assertEqual(hit.page, 2)
        self.assertIn("130-139 mmHg", hit.line)

    def test_the_line_is_the_matching_line_not_the_first_one(self):
        hits = gs.search(self.connection, "urine culture")
        self.assertEqual(hits[0].line, "Obtain a urine culture in every patient before the first dose.")

    def test_a_query_is_a_phrase_by_default(self):
        """`culture urine` is not `urine culture`. Treating the query as a phrase is
        what makes a hit a literal string on a literal page."""
        self.assertEqual(gs.search(self.connection, "urine culture before"), [])

    def test_punctuation_in_a_query_does_not_blow_up_the_parser(self):
        """`130-139 mmHg` is a threshold, and the tokenizer drops the hyphen on both
        sides -- so a mangled en dash in the source still matches."""
        hits = gs.search(self.connection, "130-139 mmHg")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].page, 2)
        hits = gs.search(self.connection, "130–139 mmHg")
        self.assertEqual(len(hits), 1)

    def test_a_quote_in_a_query_does_not_blow_up_the_parser(self):
        self.assertEqual(gs.search(self.connection, 'say "confirm" twice'), [])

    def test_a_query_with_no_searchable_token_is_loud(self):
        with self.assertRaises(ValueError):
            gs.search(self.connection, "-- ??")

    def test_fts_syntax_is_available_when_asked_for(self):
        hits = gs.search(self.connection, "pyelonephritis OR hypertension", raw=True)
        self.assertEqual(sorted(h.doc_id for h in hits), ["AHA ACC/2017-hypertension", "IDSA/2010-uti"])

    def test_bad_fts_syntax_is_loud_rather_than_zero_hits(self):
        with self.assertRaises(gs.BadQuery):
            gs.search(self.connection, "hypertension AND (", raw=True)

    def test_a_society_filter_narrows(self):
        hits = gs.search(self.connection, "cover page", society="IDSA")
        self.assertEqual([h.doc_id for h in hits], ["IDSA/2010-uti"])

    def test_a_document_class_filter_narrows(self):
        """The ACIP files are browser captures of schedule pages, not guidelines. The
        class is indexed so a hit from one is separable from a hit from a guideline."""
        self.assertEqual(
            sorted(h.doc_id for h in gs.search(self.connection, "cover page", document_class=gi.UNCLASSIFIED)),
            ["AHA ACC/2017-hypertension", "IDSA/2010-uti"],
        )
        self.assertEqual(gs.search(self.connection, "cover page", document_class="browser-capture"), [])

    def test_the_limit_is_honored(self):
        self.assertEqual(len(gs.search(self.connection, "cover page", limit=1)), 1)

    def test_a_real_zero_is_zero_hits_and_not_an_error(self):
        self.assertEqual(gs.search(self.connection, "aortic dissection"), [])


class LineAttributionTests(TempCorpus):
    def test_an_fts_keyword_is_an_ordinary_word_in_phrase_mode(self):
        """`near syncope` is a complaint, not a NEAR operator. Dropping `near` from
        attribution would score the hit on `syncope` alone and print whichever line
        happened to mention it -- a real line from the right page, and the wrong one."""
        write_single(
            self.text_dir,
            "AHA ACC/syncope",
            [
                "Syncope is a transient loss of consciousness.\n"
                "Patients reporting near syncope are evaluated the same way.\n"
            ],
        )
        gi.build(self.text_dir, self.db)
        connection = gs.open_index(self.db)
        self.addCleanup(connection.close)
        hits = gs.search(connection, "near syncope")
        self.assertEqual(len(hits), 1)
        self.assertIn("near syncope", hits[0].line)


class MissingIndexTests(TempCorpus):
    """`Zero hits and no index must not look alike` is a done-when on #84."""

    def test_no_index_file_is_loud(self):
        with self.assertRaises(FileNotFoundError):
            gs.open_index(self.db)

    def test_a_file_that_is_not_an_index_is_loud(self):
        self.db.parent.mkdir(parents=True)
        self.db.write_text("this is not a database", encoding="utf-8")
        with self.assertRaises(gs.NotAnIndex):
            gs.open_index(self.db)

    def test_a_database_without_the_schema_is_loud(self):
        self.db.parent.mkdir(parents=True)
        sqlite3.connect(self.db).close()
        with self.assertRaises(gs.NotAnIndex):
            gs.open_index(self.db)

    def test_a_schema_from_another_version_is_loud(self):
        self.build_default_corpus()
        connection = sqlite3.connect(self.db)
        connection.execute("UPDATE meta SET value = '0' WHERE key = 'schema_version'")
        connection.commit()
        connection.close()
        with self.assertRaises(gs.NotAnIndex):
            gs.open_index(self.db)


class CommandLineTests(TempCorpus):
    def run_search(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = gs.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_a_hit_exits_zero_and_prints_filename_page_and_line(self):
        self.build_default_corpus()
        status, out, _ = self.run_search(["--db", str(self.db), "urine culture"])
        self.assertEqual(status, 0)
        self.assertIn("IDSA/2010-uti", out)
        self.assertIn("p.2", out)
        self.assertIn("Obtain a urine culture", out)

    def test_zero_hits_exits_one(self):
        self.build_default_corpus()
        status, out, _ = self.run_search(["--db", str(self.db), "aortic dissection"])
        self.assertEqual(status, 1)
        self.assertIn("0 match(es)", out)

    def test_a_missing_index_exits_two_and_says_how_to_build_it(self):
        status, _, err = self.run_search(["--db", str(self.db), "aortic dissection"])
        self.assertEqual(status, 2)
        self.assertIn("guidelines_index.py", err)

    def test_several_queries_are_reported_separately(self):
        """Query expansion is the answer to `keyword search cannot find a concept`,
        so firing six exact queries has to be one command."""
        self.build_default_corpus()
        status, out, _ = self.run_search(
            ["--db", str(self.db), "urine culture", "stage 1 hypertension"]
        )
        self.assertEqual(status, 0)
        self.assertIn("IDSA/2010-uti", out)
        self.assertIn("AHA ACC/2017-hypertension", out)

    def test_a_hit_in_one_of_several_queries_still_exits_zero(self):
        self.build_default_corpus()
        status, _, _ = self.run_search(["--db", str(self.db), "aortic dissection", "urine culture"])
        self.assertEqual(status, 0)

    # ------------------------------------------------------------------
    # A class no document carries is not a genuine zero, #185
    # ------------------------------------------------------------------

    def test_a_class_no_document_carries_exits_two_and_names_what_is_there(self):
        """The whole of #185 in one status.

        The catalog published ``recommendation-statement`` while the extractor
        emitted ``print-capture``, so the filter returned an empty set and this
        tool exited **1** -- its documented code for *nothing in the corpus
        matches*. That is not a failure to answer, it is an affirmative
        certification of an absence, and it was false of every USPSTF document in
        the corpus. A caller obeying the documented convention would have taken it
        as evidence. The counts are in ``test_class_vocabulary.py`` and deliberately
        not restated here.
        """
        self.build_default_corpus()
        status, out, err = self.run_search(
            ["--db", str(self.db), "--class", "recommendation-statement", "cover page"]
        )
        self.assertEqual(status, 2)
        self.assertEqual(out, "", "nothing may be reported about a search that did not run")
        self.assertIn("recommendation-statement", err)
        self.assertIn(gi.UNCLASSIFIED, err, "the message says what the index does hold")

    def test_a_class_the_index_carries_still_reports_its_hits(self):
        self.build_default_corpus()
        status, out, _ = self.run_search(
            ["--db", str(self.db), "--class", gi.UNCLASSIFIED, "urine culture"]
        )
        self.assertEqual(status, 0)
        self.assertIn("IDSA/2010-uti", out)

    def test_a_carried_class_with_no_hits_is_still_a_genuine_zero(self):
        """The two limbs have to stay apart. A class the index knows about, asked a
        question nothing answers, is 1 -- that is a real finding about the corpus."""
        self.build_default_corpus()
        status, out, _ = self.run_search(
            ["--db", str(self.db), "--class", gi.UNCLASSIFIED, "aortic dissection"]
        )
        self.assertEqual(status, 1)
        self.assertIn("0 match(es)", out)


class Cp1252ConsoleTests(TempCorpus):
    """Issue #150, end to end and in a real process.

    The defect lives at the ``__main__`` seam, which no in-process test reaches:
    ``redirect_stdout(StringIO())`` has no codec to be wrong about, so every test in
    ``CommandLineTests`` passed throughout. So these run the script the way a person
    does, with ``PYTHONIOENCODING`` forcing the console Windows hands you by default.

    **The assertion that matters is the exit status, not the glyph.** An uncaught
    ``UnicodeEncodeError`` exits 1, and this tool's contract reads 1 as *a genuine
    zero* -- so before the fix, a query that matched a page with a threshold on it
    was indistinguishable from one that matched nothing.
    """

    def run_script(self, argv, encoding="cp1252"):
        environment = {**os.environ, "PYTHONIOENCODING": encoding}
        finished = subprocess.run(
            [sys.executable, str(TOOLS / "guidelines_search.py"), *argv],
            capture_output=True,
            env=environment,
        )
        return (
            finished.returncode,
            finished.stdout.decode("utf-8", "replace"),
            finished.stderr.decode("utf-8", "replace"),
        )

    def build_threshold_corpus(self):
        write_single(self.text_dir, "IDSA/2023-foot", ["cover page", THRESHOLD_PAGE])
        return gi.build(self.text_dir, self.db)

    def test_a_hit_carrying_a_non_cp1252_character_exits_zero(self):
        self.build_threshold_corpus()
        status, out, err = self.run_script(["--db", str(self.db), "SIRS criteria"])
        self.assertEqual(status, 0, f"stderr was: {err}")
        self.assertNotIn("UnicodeEncodeError", err)
        self.assertIn("IDSA/2023-foot", out)

    def test_the_line_arrives_whole_rather_than_truncated_at_the_character(self):
        """Partial output that looks complete is the half a reader cannot see: the
        header prints, some hits print, then it dies mid-list."""
        self.build_threshold_corpus()
        _, out, _ = self.run_script(["--db", str(self.db), "SIRS criteria"])
        self.assertIn("≥2", out)
        self.assertIn("match(es)", out)  # the closing tally, so nothing died mid-list

    def test_a_genuine_zero_still_exits_one_on_the_same_console(self):
        """The other side of the contract. The fix must not make everything exit 0."""
        self.build_threshold_corpus()
        status, out, _ = self.run_script(["--db", str(self.db), "aortic dissection"])
        self.assertEqual(status, 1)
        self.assertIn("0 match(es)", out)

    def test_a_missing_index_still_exits_two_on_the_same_console(self):
        status, _, err = self.run_script(["--db", str(self.db), "SIRS criteria"])
        self.assertEqual(status, 2)
        self.assertIn("guidelines_index.py", err)

    # There is deliberately no test here for the `errors="replace"` fallback -- the
    # limb that runs when a stream will not take UTF-8 at all. `PYTHONIOENCODING`
    # cannot produce that stream: whatever codec it names, `reconfigure` moves off it
    # and the run passes with or without the fix. A test like that reads as pinning
    # the fallback while pinning nothing, so the fallback is tested against a stub in
    # `test_console_codec.py`, where being a stub is visible.


class BuildCommandLineTests(TempCorpus):
    def run_build(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = gi.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_a_build_reports_its_counts(self):
        write_single(self.text_dir, "IDSA/2010-uti", ["one", PYELONEPHRITIS_PAGE])
        status, out, _ = self.run_build([str(self.text_dir), str(self.db)])
        self.assertEqual(status, 0)
        self.assertIn("1 document", out)
        self.assertIn("2 page", out)

    def test_a_missing_text_directory_exits_nonzero(self):
        status, _, err = self.run_build([str(self.root / "nowhere"), str(self.db)])
        self.assertEqual(status, 2)
        self.assertIn("nowhere", err)


if __name__ == "__main__":
    unittest.main()
