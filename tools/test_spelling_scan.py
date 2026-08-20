"""Tests for the spelling scan.

Three jobs, and the middle one is the reason this file is longer than the module.

**The mention rule.** A British spelling inside a code span is being named, not
used -- that is how standing rule 4 gets written down at all. Every test of it is
inline text, because the discriminator has to hold for text nobody has seen.

**Parity with the skill.** ``skills/clinical-note/SKILL.md`` carries the table
under *Conventions > Spelling*, and this file parses it and asserts the scanner
covers every row of it, mapped the same way. A scanner that quietly disagreed
with the skill would be the ``.claude/skills/`` mirror problem again: two files
holding two answers, and no way to tell which one a reader got.

**The run record's tally.** ``fixtures/filled-anchor/notes/`` is day-b run 1 byte
for byte apart from two redacted site names, and keeps the British spellings
that run emitted. The counts below are the evidence for issue #73, pinned here
for the same reason
``test_filled_vitals_census`` pins #67's: an edit that "tidied" the record would
otherwise void an argument in three files without failing anything.

This file is Python and deliberately holds the scanner's hostile examples.
Each test statement that names listed forms carries the exact counted declaration
the scanner recognizes; changing a fixture without updating its declaration
fails the repository-wide scan.
"""

import ast
import contextlib
import io
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

import spelling_scan as scan

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"
RECORD_README = REPO_ROOT / "fixtures" / "filled-anchor" / "notes" / "README.md"

# day-b run 1, byte for byte apart from two redacted site names. Issue #73.
#
# **These moved twice on 2026-08-20 in opposite directions, and the record did
# not move at all.** #278's second round put four evidenced forms on the table
# and three of them were already sitting in these notes, uncounted, because the
# table did not hold them. #103 removed one in the same window, on the same
# evidence-only rule read the other way. The run produced exactly what it always
# produced; the instrument gained three rows here and lost one.
RECORD_FORMS = 13
RECORD_OCCURRENCES = 43
RECORD_NOTES = 7


def reader(**files: str):
    """A ``read`` callable over inline text, keyed by path with ``/`` for ``__``."""
    table = {path.replace("__", "/"): text for path, text in files.items()}
    return lambda path: table.get(path)


class CodeSpans(unittest.TestCase):
    """A form in a code span is a mention. In running prose it is a use."""

    # spelling-scan: mentions 1
    def test_a_backticked_form_is_not_a_finding(self):
        findings = scan.scan_text("Never write `dyspnoea` here.", "a.md")
        self.assertEqual(findings, [])

    # spelling-scan: mentions 1
    def test_a_double_backticked_form_is_not_a_finding(self):
        findings = scan.scan_text("British ``apnoea`` is not carried.", "a.md")
        self.assertEqual(findings, [])

    # spelling-scan: mentions 2
    def test_the_same_form_in_prose_is_a_finding(self):
        findings = scan.scan_text("No dyspnoea at rest.", "a.md")
        self.assertEqual([f.form for f in findings], ["dyspnoea"])
        self.assertEqual(findings[0].american, "dyspnea")
        self.assertEqual(findings[0].line, 1)

    # spelling-scan: mentions 3
    def test_a_span_shields_only_itself(self):
        findings = scan.scan_text("`grey` is out; the TMs were grey.", "a.md")
        self.assertEqual([f.form for f in findings], ["grey"])

    # spelling-scan: mentions 3
    def test_a_table_row_of_mentions_is_clean(self):
        row = "| `grey`, `behaviour`, `colour` | `gray`, `behavior`, `color` |"
        self.assertEqual(scan.scan_text(row, "a.md"), [])

    # spelling-scan: mentions 2
    def test_a_fenced_block_is_not_shielded(self):
        text = "```\nHt 5'10\", no dyspnoea at rest\n```\n"
        self.assertEqual([f.form for f in scan.scan_text(text, "a.md")], ["dyspnoea"])


class Matching(unittest.TestCase):
    # spelling-scan: mentions 2
    def test_line_numbers_are_one_based(self):
        findings = scan.scan_text("clean\nclean\nthe grey membrane\n", "a.md")
        self.assertEqual([(f.line, f.form) for f in findings], [(3, "grey")])

    # spelling-scan: mentions 10
    def test_inflections_are_caught(self):
        for text, form in (
            ("give 5 millilitres", "millilitre"),
            ("increase dietary fibres", "fibre"),
            ("proposals are labelled", "labelled"),
            ("the wound was catheterised", "catheterise"),
            ("behavioural change", "behaviour"),
        ):
            with self.subTest(text=text):
                self.assertEqual([f.form for f in scan.scan_text(text, "a.md")], [form])

    # spelling-scan: mentions 2
    def test_a_stem_change_is_carried_explicitly(self):
        findings = scan.scan_text("labelling the proposals", "a.md")
        self.assertEqual([(f.form, f.american) for f in findings],
                         [("labelling", "labeling")])

    def test_a_form_inside_a_longer_word_is_not_matched(self):
        self.assertEqual(scan.scan_text("a greyhound", "a.md"), [])

    # spelling-scan: mentions 5
    def test_millilitres_is_one_finding_not_two(self):
        """``litre`` must not fire inside ``millilitre``."""
        findings = scan.scan_text("10 millilitres", "a.md")
        self.assertEqual([f.form for f in findings], ["millilitre"])

    # spelling-scan: mentions 2
    def test_matching_ignores_case(self):
        self.assertEqual([f.form for f in scan.scan_text("Grey TMs", "a.md")], ["grey"])

    # spelling-scan: mentions 4
    def test_drug_names_take_the_us_generic(self):
        findings = scan.scan_text("gave paracetamol and adrenaline", "a.md")
        self.assertEqual([(f.form, f.american) for f in findings],
                         [("paracetamol", "acetaminophen"),
                          ("adrenaline", "epinephrine")])


class PythonMentions(unittest.TestCase):
    # spelling-scan: mentions 2
    def test_backticks_do_not_exempt_python_without_a_counted_declaration(self):
        findings = scan.scan_python_text("# `grey` is still Python source\n", "tools/x.py")
        self.assertEqual([(finding.line, finding.form) for finding in findings],
                         [(1, "grey")])

    # spelling-scan: mentions 4
    def test_a_counted_declaration_exempts_the_exact_next_statement(self):
        text = textwrap.dedent(
            """\
            # spelling-scan: mentions 2
            examples = {"grey": "gray", "labelled": "labeled"}
            grey_value = 1
            """
        )
        findings = scan.scan_python_text(text, "tools/example.py")
        self.assertEqual([(f.line, f.form) for f in findings], [(3, "grey")])

    # spelling-scan: mentions 1
    def test_a_stale_count_fails_instead_of_widening_the_exemption(self):
        text = "# spelling-scan: mentions 2\nvalue = 'grey'\n"
        with self.assertRaisesRegex(scan.MentionDeclarationError, "declares 2.*contains 1"):
            scan.scan_python_text(text, "tools/example.py")


class StagedChanges(unittest.TestCase):
    # spelling-scan: mentions 6
    def test_staged_python_additions_and_filenames_are_scanned(self):
        additions = {"tools/grey-helper.py": [(1, "labelled_value = 1")]}
        with (
            mock.patch.object(scan, "staged_paths", return_value=["tools/grey-helper.py"]),
            mock.patch.object(scan, "staged_additions", return_value=additions),
            mock.patch.object(scan, "read_staged", return_value="labelled_value = 1\n"),
        ):
            report = scan.scan_staged()
        self.assertEqual([(f.line, f.form) for f in report.findings],
                         [(0, "grey"), (1, "labelled")])


class Ticket103Ruling(unittest.TestCase):
    """The evidence-grown table excludes an encounter-unreachable derivative."""

    def test_the_unloaded_derivative_is_outside_the_documented_cli_vocabulary(self):
        excluded_derivative = "recognis" + "able"
        pairs = dict(scan.parse_skill_table(SKILL.read_text(encoding="utf-8")))
        self.assertNotIn(excluded_derivative, pairs)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = scan.main(["--record"])

        self.assertEqual(exit_code, 0, output.getvalue())
        self.assertNotIn(excluded_derivative, output.getvalue())
        self.assertIn(f"{RECORD_FORMS} forms, {RECORD_OCCURRENCES} occurrences",
                      output.getvalue())


class Evidence(unittest.TestCase):
    """The run record is evidence. It is counted and never refused."""

    # spelling-scan: mentions 1
    def test_a_note_in_the_record_yields_no_findings(self):
        report = scan.scan(
            ["fixtures/filled-anchor/notes/case-07.md"],
            reader(**{"fixtures__filled-anchor__notes__case-07.md": "no dyspnoea"}),
        )
        self.assertEqual(report.findings, [])

    # spelling-scan: mentions 5
    def test_the_record_is_counted_instead(self):
        report = scan.scan(
            ["fixtures/filled-anchor/notes/case-07.md"],
            reader(**{
                "fixtures__filled-anchor__notes__case-07.md": "grey TMs, no dyspnoea, grey",
            }),
        )
        self.assertEqual(report.evidence.occurrences, 3)
        self.assertEqual(report.evidence.forms, {"grey": 2, "dyspnoea": 1})
        self.assertEqual(report.evidence.files, ("fixtures/filled-anchor/notes/case-07.md",))

    # spelling-scan: mentions 2
    def test_the_records_own_readme_is_not_evidence(self):
        """It is prose about the record, so it takes the mention rule like any prose."""
        report = scan.scan(
            ["fixtures/filled-anchor/notes/README.md"],
            reader(**{"fixtures__filled-anchor__notes__README.md": "it wrote dyspnoea"}),
        )
        self.assertEqual([f.form for f in report.findings], ["dyspnoea"])
        self.assertEqual(report.evidence.occurrences, 0)

    # spelling-scan: mentions 2
    def test_the_record_exemption_does_not_cover_a_filename(self):
        path = "fixtures/filled-anchor/notes/case-grey.md"
        report = scan.scan([path], lambda _path: "clean prose")
        self.assertEqual([(f.line, f.form) for f in report.findings], [(0, "grey")])
        self.assertEqual(report.evidence.occurrences, 0)

    # spelling-scan: mentions 2
    def test_python_identifiers_are_read(self):
        report = scan.scan(["tools/x.py"], lambda _path: "grey_value = 1")
        self.assertEqual([(f.path, f.line, f.form) for f in report.findings],
                         [("tools/x.py", 1, "grey")])

    # spelling-scan: mentions 3
    def test_a_tracked_filename_is_read(self):
        report = scan.scan(["docs/grey-guide.md"], lambda _path: "clean prose")
        self.assertEqual([(f.path, f.line, f.form) for f in report.findings],
                         [("docs/grey-guide.md", 0, "grey")])


class ARunDirectory(unittest.TestCase):
    """Grading a run's output, which is the only thing that exercises the rule."""

    # spelling-scan: mentions 3
    def test_markdown_is_collected_recursively_and_nothing_else_is(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "notes").mkdir()
            (root / "notes" / "case-01.md").write_text("pearly grey", encoding="utf-8")
            (root / "notes" / "case-02.md").write_text("pearly gray", encoding="utf-8")
            (root / "notes" / "log.txt").write_text("grey", encoding="utf-8")

            report = scan.scan(scan.markdown_under([root]), scan.read_file)

        self.assertEqual([f.form for f in report.findings], ["grey"])
        self.assertEqual(report.evidence.occurrences, 0)

    # spelling-scan: mentions 2
    def test_a_run_directory_is_never_read_as_the_run_record(self):
        """Even one laid out with the record's own path inside it."""
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "fixtures" / "filled-anchor" / "notes"
            root.mkdir(parents=True)
            (root / "case-01.md").write_text("no dyspnoea", encoding="utf-8")

            report = scan.scan(scan.markdown_under([root]), scan.read_file)

        self.assertEqual([f.form for f in report.findings], ["dyspnoea"])


class Output(unittest.TestCase):
    """Findings name the table's entry, never the bytes matched. Safe to paste."""

    # spelling-scan: mentions 3
    def test_a_finding_renders_path_line_and_form_only(self):
        findings = scan.scan_text("Marked GREY on the left, per [PT].", "a.md")
        rendered = findings[0].render()
        self.assertIn("a.md:1", rendered)
        self.assertIn("grey", rendered)
        self.assertNotIn("GREY", rendered)
        self.assertNotIn("[PT]", rendered)


class ParityWithTheSkill(unittest.TestCase):
    """The scanner's table and the skill's table are one table.

    Parsed rather than trusted: the skill's is the one a human reads and the
    scanner's is the one that runs, and a difference between them is invisible
    from either side.
    """

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.rows = scan.parse_skill_table(cls.text)

    def test_the_table_was_found(self):
        self.assertGreaterEqual(len(self.rows), 6, "the Spelling table moved or changed shape")

    def test_every_row_of_the_skills_table_is_covered(self):
        for british, american in self.rows:
            with self.subTest(form=british):
                self.assertIn(british, scan.FORMS)
                self.assertEqual(scan.FORMS[british], american)

    def test_the_skill_carries_every_form_the_scanner_holds(self):
        """The reverse direction, and #278 is what exercised it. Parity was one
        way -- every skill row covered by the scanner -- so adding a new form
        to ``TABLE`` left the whole suite green with the file a reader opens
        never mentioning it. That is the ``.claude/skills/`` mirror problem
        again: two files, two answers, and no way to tell which one a reader
        got. ``STEM_CHANGES`` and ``DRUGS`` are deliberately outside it -- the
        skill names those in prose, which the class below asserts.
        """
        pairs = dict(scan.parse_skill_table(SKILL.read_text(encoding="utf-8")))
        for british, american in scan.TABLE.items():
            with self.subTest(form=british):
                self.assertEqual(pairs.get(british), american)

    def test_every_drug_form_is_named_by_the_skill(self):
        for british, american in scan.DRUGS.items():
            with self.subTest(form=british):
                self.assertIn(british, self.text)
                self.assertIn(american, self.text)


class TheRunRecord(unittest.TestCase):
    """Issue #73's evidence, recomputed from the committed notes."""

    @classmethod
    def setUpClass(cls):
        cls.report = scan.scan(scan.tracked_files(), scan.read_tracked)

    def test_the_tally_is_unchanged(self):
        evidence = self.report.evidence
        self.assertEqual(len(evidence.forms), RECORD_FORMS)
        self.assertEqual(evidence.occurrences, RECORD_OCCURRENCES)
        self.assertEqual(len(evidence.files), RECORD_NOTES)

    # spelling-scan: mentions 22
    def test_the_listed_forms_are_the_ones_the_ticket_names(self):
        # **Eight until 2026-08-18, then nine, then ten within the hour.** The run
        # record has not changed and cannot -- ``fixtures/filled-anchor/notes/``
        # is a byte-for-byte record of what a day-b run produced, apart from two
        # redacted site names. What changed is the *table*: ``neighbour`` was
        # never a listed form, so two occurrences of it sat in these notes
        # unseen and uncounted, and adding the form to ``FORMS`` is what made
        # them visible. #73's evidence set got larger without the evidence
        # moving, which is the distinction this class exists to hold.
        #
        # **``judgement`` was the tenth and it was named in the repo's own docs
        # the whole time.** ``docs/agents/issue-tracker.md`` lists it beside
        # ``neighbouring`` as a British form the table does not hold -- written
        # to warn about ticket text, while three occurrences sat in these
        # committed notes. **A form documented as invisible is still invisible**,
        # and naming one in prose is not the same as adding it to the table.
        #
        # **Four more on 2026-08-20, and three of them are here.** #278's second
        # round is the same distinction a fourth time: ``counselling``,
        # ``hypoxaemia``, ``hypoxaemic`` and ``immobilisation`` were written by
        # the run that produced these notes and were invisible to every scan
        # until the table held them. ``millimetre`` went on the table in the
        # same change and is **not** in this list -- that run never wrote it,
        # which is ``manoeuvre``'s shape and is why the two facts are kept
        # apart.
        #
        # **And #103 removed ``recognisable`` in the same window**, its only
        # appearances being the run's self-audit boilerplate rather than
        # vocabulary an encounter can exercise. So this list gained four and
        # lost one while the twelve notes did not move a byte, which is the
        # growth rule read in both directions at once.
        self.assertEqual(
            sorted(self.report.evidence.forms),
            ["behaviour", "caesarean", "counselling", "dyspnoea", "fibre",
             "grey", "hypoxaemia", "hypoxaemic", "immobilisation", "judgement",
             "labelled", "neighbour", "programme"],
        )

    def test_no_tracked_source_or_filename_uses_a_listed_british_spelling(self):
        """#104 widens #73's permanent tree check to every local source surface."""
        rendered = "\n".join(f.render() for f in self.report.findings)
        self.assertEqual(self.report.findings, [], "\n" + rendered)


class TheRecordView(unittest.TestCase):
    """``--record``, which is what the set's README cites rather than restates."""

    @classmethod
    def setUpClass(cls):
        cls.rows = scan.record_rows(scan.tracked_markdown(), scan.read_tracked)

    def test_one_row_per_form(self):
        self.assertEqual(len(self.rows), RECORD_FORMS)
        self.assertEqual(sum(row.british for row in self.rows), RECORD_OCCURRENCES)

    # spelling-scan: mentions 6
    def test_the_run_wrote_both_spellings_of_the_same_word(self):
        """The counterpart column is #73's argument: drift, not a British register."""
        rows = {row.form: row for row in self.rows}
        self.assertEqual((rows["caesarean"].british, rows["caesarean"].american_count), (2, 8))
        self.assertEqual((rows["dyspnoea"].british, rows["dyspnoea"].american_count), (3, 7))
        self.assertEqual((rows["fibre"].british, rows["fibre"].american_count), (4, 3))

    # spelling-scan: mentions 7
    def test_the_largest_pair_in_the_set_is_partitioned_by_note(self):
        """``counselling`` is #73's argument at its sharpest, and the table not
        holding the form is the only reason nobody had seen it.

        **The mechanism is a between-note partition, not a within-note ratio**,
        and the skill's prose said the opposite for the length of one sweep: the
        two notes carrying the British form carry **no** occurrence of the
        American one, and the ten carrying the American form carry none of the
        British. So a reader of any single note sees perfect internal
        consistency and the drift exists only across the twelve -- which is
        precisely why #73 needed twelve outputs in front of one reader.

        Pinned in both directions because the prose states the pair and names
        the two exceptions. **The count was right and the reading of it was
        invented**, which no assertion on the count alone would have caught --
        the version of this test that shipped first asserted exactly the two
        numbers below and would have passed the wrong sentence unchanged.
        """
        rows = {row.form: row for row in self.rows}
        row = rows["counselling"]
        self.assertEqual((row.british, row.american_count), (12, 57))
        self.assertGreater(
            row.american_count,
            max(r.american_count for r in self.rows if r.form != "counselling"),
        )
        self.assertEqual(self._notes_carrying_both("counselling"), [])
        # The two the prose names as the genuine within-note case, and the
        # reason ``slip`` is the wrong word for the pair above.
        both = sorted(r.form for r in self.rows if self._notes_carrying_both(r.form))
        self.assertEqual(both, ["caesarean", "fibre"])
        # **Bound to the prose, not merely pinned here**, which is the same
        # #220 gap the stated tally had. The three pairs beside this one in the
        # skill are prose nothing can fail against; they predate this and are
        # left alone, but a pair added *by* the change that fixed the tally may
        # not repeat the defect one sentence over. Written in digits so the
        # assertion can be built from the values rather than transcribed.
        self.assertIn(
            f"`counseling` {row.american_count} against "
            f"`counselling` {row.british}",
            SKILL.read_text(encoding="utf-8"),
        )

    # spelling-scan: mentions 1
    def _notes_carrying_both(self, form):
        """The record notes containing this form *and* its American counterpart."""
        american = scan.ALL_FORMS[form]
        british = re.compile(r"\b" + re.escape(form) + scan._SUFFIX + r"\b", re.I)
        counterpart = re.compile(r"\b" + re.escape(american) + scan._SUFFIX + r"\b", re.I)
        found = []
        for path in scan.tracked_markdown():
            if not scan.is_evidence(path):
                continue
            text = scan.read_tracked(path) or ""
            if british.search(text) and counterpart.search(text):
                found.append(path)
        return found
        # **Bound to the prose, not merely pinned here**, which is the same
        # #220 gap the stated tally had. The three pairs beside this one in the
        # skill are prose nothing can fail against; they predate this and are
        # left alone, but a pair added *by* the change that fixed the tally may
        # not repeat the defect one sentence over. Written in digits so the
        # assertion can be built from the values rather than transcribed.
        self.assertIn(
            f"`counseling` {row.american_count} against "
            f"`counselling` {row.british}",
            SKILL.read_text(encoding="utf-8"),
        )

    def test_the_records_stated_tally_is_the_one_the_scanner_computes(self):
        """The figure in the withheld record, bound rather than typed.

        Issue #147 moved fixture-derived counts out of required generation
        instructions.  The record's own README is both the natural home and a
        file withheld from a generating pass.  The other half of #220 still
        binds the prose to the computed value so a reviewer cannot mutate it to
        a triple the record has never held with every spelling test green.

        **Only the current value is bound, and that asymmetry is deliberate.**
        The three before it are what the paragraph *used to read*; they are
        history and no reader can act on them. This one is a claim about the
        tree.

        **The parser lives here rather than in the module**, which is where
        ``parse_skill_table`` sits. That one parses a **rule the scanner
        enforces** and the scanner is its caller. This parses a **figure the
        test pins**, and ``spelling_scan`` has no use for it -- a public
        function with no production caller is Speculative Generality, and the
        constants it checks against are this file's already.

        The wording is the command's own, so the sentence a reader checks and
        the line the tool prints are the same shape.
        """
        stated = re.search(
            r"\*\*(\d+) forms / (\d+) occurrences / (\d+) of the twelve notes\*\*",
            RECORD_README.read_text(encoding="utf-8"),
        )
        self.assertIsNotNone(
            stated,
            "the withheld record's stated tally moved or changed shape",
        )
        self.assertEqual(
            tuple(int(n) for n in stated.groups()),
            (RECORD_FORMS, RECORD_OCCURRENCES, RECORD_NOTES),
        )

    # spelling-scan: mentions 2
    def test_the_form_column_fits_the_longest_form_it_renders(self):
        """The width is derived, so a longer form cannot push its own count out
        of the column. It was a literal ``13`` and was already too narrow for
        ``catheterisation`` -- invisibly, because that form is not in the record
        and so was never rendered. #278's ``immobilisation`` is the first
        14-character form the record holds, and it is what made the defect
        visible rather than what introduced it."""
        rendered = scan.render_record(self.rows)
        counts = [
            line[2 + max(len(row.form) for row in self.rows):]
            for line, row in zip(rendered[2:2 + len(self.rows)], self.rows)
        ]
        for line in counts:
            with self.subTest(line=line):
                self.assertTrue(line.startswith(" "), "the form column overflowed")

    def test_the_view_names_cases_and_counts_only(self):
        rendered = "\n".join(scan.render_record(self.rows))
        for row in self.rows:
            self.assertIn(row.form, rendered)
        for case, _ in (pair for row in self.rows for pair in row.cases):
            self.assertRegex(case, r"^case-\d\d$")


class TheWalkedPopulation(unittest.TestCase):
    """#258: what a clean result covers, on the page rather than in a docstring.

    #254 ruled that every ``git ls-files`` walk states what a clean result
    covers, and `tracked_files` carries that statement in its docstring. This
    scanner prints ``no listed British spelling found.`` -- an unqualified clean
    result, in the one walk with the **recorded** instance rather than the
    hypothetical one: ``CLAUDE.md`` carries a listed form landing in a skill file
    because the staged scan had crashed and ``--all`` cannot see a file until
    the commit that makes it tracked.

    **Advisory cuts both ways and the clinician ruled it cuts toward saying so**
    (2026-08-19, #258 open question 3). A line read past costs nothing; an
    unqualified clean line is what let the recorded instance through.

    **Every mode, not only ``--all``.** A reader who has learned to read the
    ``--all`` qualifier would read its absence anywhere else as a stronger
    claim, which is the defect one level down.
    """

    def clean(self):
        return scan.Report([], scan.Evidence({}, ()))

    # spelling-scan: mentions 1
    def dirty(self):
        return scan.Report(scan.scan_text("no dyspnoea at rest\n", "a.md"),
                           scan.Evidence({}, ()))

    def population(self, lines):
        found = [line for line in lines if "scanned" in line]
        self.assertEqual(len(found), 1, f"expected one population line in:\n{lines}")
        return found[0]

    def test_every_mode_names_what_it_walked(self):
        for mode in scan.POPULATIONS:
            with self.subTest(mode=mode):
                line = self.population(scan.render(self.clean(), False, mode))
                self.assertTrue(line.strip())

    # spelling-scan: mentions 1
    def test_the_all_walk_includes_non_source_filenames(self):
        with mock.patch.object(scan, "_git", return_value="docs/clean.md\ngrey-data.csv\n"):
            self.assertEqual(scan.tracked_files(), ["docs/clean.md", "grey-data.csv"])

    def test_the_all_mode_line_names_tracked_and_what_that_excludes(self):
        """Both limbs, on #254's reasoning: *tracked* alone is what the walk's
        name already said, and *untracked* alone never says what a pass means."""
        line = self.population(scan.render(self.clean(), False, "--all"))
        self.assertRegex(line, r"(?<!un)tracked")
        self.assertRegex(line, r"(?i)untracked")

    def test_the_all_mode_names_both_source_types_and_filenames(self):
        line = self.population(scan.render(self.clean(), False, "--all"))
        self.assertIn(".md", line)
        self.assertIn(".py", line)
        self.assertRegex(line, r"(?i)filename")

    def test_an_unrecognized_mode_fails_rather_than_printing_a_bare_clean(self):
        """`research_ledger.py`'s ruling on an unrecognized ``STATUS``, for its
        reason: the value picks which claim is printed, so a third one would
        silently drop the qualifier and print the exact line this ticket is
        about."""
        with self.assertRaises(KeyError):
            scan.render(self.clean(), False, "everything")

    def test_a_clean_run_carries_the_qualifier_beside_the_clean_line(self):
        lines = scan.render(self.clean(), False, "--all")
        self.assertTrue(any("no listed British spelling found" in line for line in lines))
        self.assertIn(self.population(lines), lines)

    def test_findings_do_not_suppress_it(self):
        """A finding is a floor rather than the whole, so the population still
        has to be stated -- `differential_scan.py`'s ordering, one scanner over."""
        lines = scan.render(self.dirty(), False, "--all")
        self.assertTrue(any("a.md:1" in line for line in lines))
        self.assertRegex(self.population(lines), r"(?i)untracked")

    def test_quiet_and_clean_still_prints_nothing(self):
        """``--quiet`` means *print nothing when clean*, and the hook runs it on
        every commit. Widening it into *print one line when clean* would make
        this advisory scanner noisy on the one path where noise is paid for
        every time."""
        self.assertEqual(scan.render(self.clean(), True, "staged"), [])

    def test_quiet_with_findings_still_states_its_coverage(self):
        """The hook's own case. Where the scanner is already speaking, the floor
        has to be stated -- otherwise the one report a committer reads is the
        one with no qualifier on it."""
        lines = scan.render(self.dirty(), True, "staged")
        self.assertTrue(lines)
        self.assertTrue(self.population(lines).strip())


class TheCheckedVocabulary(unittest.TestCase):
    """#278: the *other* axis of what a clean result covers, on the page.

    #258 put the walked **population** on the page -- which files were read.
    That is half of what a clean line means, and the half this scanner is
    weakest on is the other one: it holds a table rather than the language, so
    a clean result is ``no form on an N-entry table appears in the walked set``
    and reads as ``American English``.

    **The recorded instance is two forms in one commit, minutes apart.** One was
    on the table and caught; the other was absent and found only by looking
    afterwards. Nothing in the clean run said the second had never been checked.

    **Declared rather than widened**, which is the clinician's #254 ruling and
    the one he re-ruled here: adding the evidenced form closes today's instance and
    the productive families (``-ise``, ``-our``, ``-re``) would fire on correct
    words. What generalizes is saying so.
    """

    def clean(self):
        return scan.Report([], scan.Evidence({}, ()))

    # spelling-scan: mentions 1
    def dirty(self):
        return scan.Report(scan.scan_text("no dyspnoea at rest\n", "a.md"),
                           scan.Evidence({}, ()))

    def vocabulary(self, lines):
        found = [line for line in lines if "listed form" in line]
        self.assertEqual(len(found), 1, f"expected one vocabulary line in:\n{lines}")
        return found[0]

    def test_every_mode_states_the_vocabulary(self):
        """Every mode, on #258's reasoning for the population line: a reader who
        learns to read the qualifier in one mode reads its absence in another as
        a stronger claim."""
        for mode in scan.POPULATIONS:
            with self.subTest(mode=mode):
                self.assertTrue(self.vocabulary(scan.render(self.clean(), False, mode)).strip())

    def test_the_count_is_the_one_the_scanner_matches_with(self):
        """Derived from ``_PATTERNS`` rather than typed, so the printed number
        cannot disagree with what actually ran -- which is the whole defect one
        level down. A hand-typed figure here is #143 with a table that grows."""
        line = self.vocabulary(scan.render(self.clean(), False, "--all"))
        self.assertIn(str(len(scan._PATTERNS)), line)

        # Asserting the two agree cannot tell a derived number from a typed one
        # that happens to be right today -- which is the whole failure being
        # guarded against, since the table grows and the literal would not. So
        # the table is moved and the line has to follow it.
        original = scan._PATTERNS
        try:
            scan._PATTERNS = original[:3]
            moved = self.vocabulary(scan.render(self.clean(), False, "--all"))
        finally:
            scan._PATTERNS = original
        self.assertIn("3 listed forms", moved)
        self.assertNotEqual(line, moved)

    def test_the_line_says_what_being_absent_from_the_table_means(self):
        """Both limbs, on #254's reasoning. The count alone is what the table
        already says about itself; what says *what a pass means* is that a form
        the table does not hold was never looked for."""
        line = self.vocabulary(scan.render(self.clean(), False, "--all"))
        self.assertRegex(line, r"(?i)not (?:hold|a finding)")

    def test_it_is_stated_once_and_beside_the_population(self):
        """Two qualifiers, two rows, both present. Stated once on its own row is
        #258's discipline; restating it on the population row is #220 -- two
        copies of one claim, each editable without failing anything."""
        lines = scan.render(self.clean(), False, "--all")
        population = [line for line in lines if "scanned" in line]
        self.assertEqual(len(population), 1)
        self.assertNotIn("listed form", population[0])
        self.assertIn(self.vocabulary(lines), lines)

    def test_findings_do_not_suppress_it(self):
        """A finding is a floor rather than the whole: the forms *not* checked
        are exactly what a reader of a short finding list needs told."""
        lines = scan.render(self.dirty(), False, "--all")
        self.assertTrue(any("a.md:1" in line for line in lines))
        self.assertTrue(self.vocabulary(lines).strip())

    def test_quiet_and_clean_still_prints_nothing(self):
        """#258's one kept silence, unchanged: what the ruling qualifies is a
        **printed** clean result, and this pair prints none."""
        self.assertEqual(scan.render(self.clean(), True, "staged"), [])

    def test_quiet_with_findings_still_states_the_vocabulary(self):
        """The hook's own case, and the one report a committer actually reads."""
        self.assertTrue(self.vocabulary(scan.render(self.dirty(), True, "staged")).strip())

    def test_an_unrecognized_mode_fails_before_printing_either_qualifier(self):
        with self.assertRaises(KeyError):
            scan.render(self.clean(), False, "everything")

    def test_the_record_view_carries_the_same_line_rather_than_a_copy(self):
        """``--record`` needs no *population* line -- #258 ruled that, and its
        first printed line already names the one directory it reports on. It
        does need this one: its tally is bounded by the same set, and adding a
        form has moved it while the twelve notes did not move at all.

        **The same object, not a second sentence.** Two hand-written copies of
        one claim, each editable without failing anything, is #220 -- and a
        substring assertion on each would let them diverge with the suite green.
        The instance itself is stated once, in the skill's Conventions section,
        which tells a reader to re-derive with ``--record`` rather than quote
        it; printing it here would be the command quoting that sentence.
        """
        rows = scan.record_rows(scan.tracked_markdown(), scan.read_tracked)
        self.assertIn(scan.vocabulary_covered(), scan.render_record(rows))

    def test_both_renderers_call_it_rather_than_holding_the_sentence(self):
        """By AST, and the substring test above is why it has to be.

        ``assertIn(vocabulary_covered(), ...)`` catches a copy that has *drifted*
        and passes a copy that agrees today -- so a typed literal lands green and
        goes stale on the next form added, which is the whole defect. Mutation-
        tested in exactly that direction: replacing the call with a byte-
        identical literal left the suite green until this test existed.

        `reference_scan.py` importing ``docx_write.REFERENCE_HEADING`` rather
        than restating it is the precedent, and `test_console_codec.py` is the
        instrument -- a walk rather than a search, because a docstring naming
        the function satisfies a substring check while proving nothing.
        """
        tree = ast.parse(Path(scan.__file__).read_text(encoding="utf-8"))
        callers = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and any(
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Name)
                and inner.func.id == "vocabulary_covered"
                for inner in ast.walk(node)
            )
        }
        self.assertEqual({"render", "render_record"}, callers)

    def test_the_parts_reconcile_to_the_total(self):
        """A reader who counts the skill's table gets fewer rows than this set
        has patterns -- the stem changes and the drug names are not rows of it.
        A bare total is therefore a figure the file a reader opens disagrees
        with, which is the two-files-two-answers failure the parity test exists
        to close. So the line names its parts, and they have to add up."""
        line = self.vocabulary(scan.render(self.clean(), False, "--all"))
        self.assertEqual(
            len(scan.TABLE) + len(scan.STEM_CHANGES) + len(scan.DRUGS),
            len(scan._PATTERNS),
        )
        for part in (len(scan.TABLE), len(scan.STEM_CHANGES), len(scan.DRUGS)):
            with self.subTest(part=part):
                self.assertIn(str(part), line)

    def test_the_table_row_count_is_the_one_the_skill_publishes(self):
        """The half a reader can check by eye, and the reason the parts are
        printed at all: the number this line attributes to the table has to be
        the number of rows in the table itself."""
        pairs = scan.parse_skill_table(SKILL.read_text(encoding="utf-8"))
        self.assertEqual(len(pairs), len(scan.TABLE))


class TheTicketsOwnInstance(unittest.TestCase):
    """#278's finding, pinned. Two variants were written into skill files in one
    commit minutes apart and the scanner caught only the listed one.

    On the table's documented growth rule, which is evidence and not families:
    the missed form was written in this repo, as earlier additions were. Medical
    variants nobody has written here were **not** added; #278 settled that
    vocabulary question as evidence-only.
    """

    # spelling-scan: mentions 2
    def test_the_form_that_passed_clean_is_now_a_finding(self):
        findings = scan.scan_text("Dix-Hallpike manoeuvres were negative.", "a.md")
        self.assertEqual([(f.form, f.american) for f in findings],
                         [("manoeuvre", "maneuver")])

    # spelling-scan: mentions 1
    def test_naming_it_inside_backticks_is_still_a_mention(self):
        self.assertEqual(scan.scan_text("Never write `manoeuvre` here.", "a.md"), [])

    # spelling-scan: mentions 2
    def test_the_inflection_it_actually_arrived_as_is_the_one_caught(self):
        """It arrived as ``manoeuvres``. ``manoeuvring`` drops the ``e`` and is a
        stem change, so the suffix rule cannot reach it and ``STEM_CHANGES``
        does not carry it -- that table is two entries because two are what this
        repo has produced. **The declaration above is the answer to that**, not
        a guess at English."""
        self.assertTrue(scan.scan_text("repeated manoeuvres", "a.md"))
        self.assertEqual(scan.scan_text("repeated manoeuvring", "a.md"), [])


# spelling-scan: mentions 31
class TheSecondRoundOfEvidence(unittest.TestCase):
    """#278's four evidenced forms, ruled by the clinician 2026-08-20.

    The growth rule is **evidence** -- settled on #104 when the clinician
    declined the productive families and the medical vocabulary nobody had
    written. These four had been written here and were on no table, which is the
    rule firing rather than the rule being widened.

    **They are three different classes of evidence and the difference is the
    point of this class.** ``counselling`` was live in tracked Markdown prose in
    a skill a consumer reads; ``hypoxaemia``, ``hypoxaemic`` and
    ``immobilisation`` were in the preserved run record, which is how
    ``neighbour`` and ``judgement`` arrived; ``millimetre`` was written four
    times in ``.py``, a surface this scanner did not then read. The last is
    the one worth naming, and it is asserted below rather than left to be
    rediscovered.
    """

    # spelling-scan: mentions 10
    def test_every_evidenced_form_is_now_a_finding(self):
        for sentence, expected in (
            ("Dietary counselling was offered.", ("counselling", "counseling")),
            ("Induration measured in millimetres.", ("millimetre", "millimeter")),
            ("If it progresses to hypoxaemia, escalate.", ("hypoxaemia", "hypoxemia")),
            ("Early non-hypoxaemic outpatient disease.", ("hypoxaemic", "hypoxemic")),
            ("No recent immobilisation reported.", ("immobilisation", "immobilization")),
        ):
            with self.subTest(sentence=sentence):
                findings = scan.scan_text(sentence, "a.md")
                self.assertEqual([(f.form, f.american) for f in findings], [expected])

    def test_none_of_them_fires_on_the_american_form(self):
        """The bar every widening here is priced against, and the reason the
        productive families were declined: a scanner that refuses ``seizure``
        and ``figure`` is worse than one that says what it holds. Each of these
        five turns a listed form into another spelling of the same wrong word
        and never into a right one, which is what ``_SUFFIX`` promises."""
        american = (
            "Dietary counseling, induration in millimeters, progresses to "
            "hypoxemia, early non-hypoxemic disease, no immobilization."
        )
        self.assertEqual(scan.scan_text(american, "a.md"), [])

    # spelling-scan: mentions 7
    def test_the_adjective_is_a_stem_change_and_needs_its_own_entry(self):
        """``hypoxaemic`` is not reachable from ``hypoxaemia``: the suffix rule
        appends, and ``-ia`` to ``-ic`` replaces. So it sits in
        ``STEM_CHANGES`` beside ``catheterisation``, which is the same shape.

        This is the mirror of ``manoeuvring``, which is **not** carried -- there
        the repo had written only the one inflection, and here it wrote both.
        Evidence decides which, not English."""
        self.assertIn("hypoxaemic", scan.STEM_CHANGES)
        self.assertNotIn("hypoxaemic", scan.TABLE)
        without_the_entry = {
            form: pattern
            for form, _, pattern in scan._PATTERNS
            if form != "hypoxaemic"
        }
        self.assertFalse(
            any(p.search("non-hypoxaemic") for p in without_the_entry.values()),
            "the entry is redundant: something else already reaches the adjective",
        )

    # spelling-scan: mentions 5
    def test_the_live_instance_was_in_tracked_markdown_prose(self):
        """``counselling`` is the sharpest of the four: it sat at
        ``skills/clinical-note/HP.md:106``, in prose rather than a code span, in
        a tracked file, with ``--all`` green over it and both nets working. That
        is ``licence`` again with nothing broken -- the form was simply not on
        the table, which is this ticket's whole subject."""
        findings = scan.scan_text(
            "matters for counselling and future care", "skills/clinical-note/HP.md"
        )
        self.assertEqual([f.form for f in findings], ["counselling"])
        self.assertEqual(scan.scan_text("write `counselling` here", "a.md"), [])

    def test_the_form_whose_evidence_this_scanner_could_not_then_read(self):
        """``millimetre``'s four instances were all in ``.py`` -- three in
        ``tools/corpus_census.py`` and one in its test -- and when the form went
        on the table this scanner read Markdown only. So the row rests on
        evidence the instrument holding the table could not have produced:
        #104's limit 1 handing a vocabulary row to #278's limit 2.

        **The two limbs then met.** #104's local surfaces landed on ``main`` in
        the same window, so ``.py`` is a scanned surface now and the same
        evidence today is a finding rather than something somebody noticed by
        hand. The claim is asserted in both halves because the sentence in the
        skill is **historical**, and a reader needs to know which half still
        holds: the row's provenance does not change, and the gap that made it
        notable is closed."""
        self.assertIn("millimetre", scan.TABLE)
        self.assertTrue(scan.is_scannable_source("tools/corpus_census.py"))
        clean = "# a skin test result, in the unit it is read in\n"
        self.assertEqual(scan.scan_python_text(clean, "tools/example.py"), [])


class Reporting(unittest.TestCase):
    def test_a_clean_scan_exits_zero(self):
        report = scan.Report([], scan.Evidence({}, ()))
        self.assertEqual(scan.render(report, quiet=True, mode='staged'), [])

    # spelling-scan: mentions 2
    def test_findings_are_rendered_one_per_line(self):
        text = textwrap.dedent(
            """\
            no dyspnoea at rest
            pearly grey membrane
            """
        )
        report = scan.Report(scan.scan_text(text, "a.md"), scan.Evidence({}, ()))
        lines = scan.render(report, quiet=False, mode='staged')
        self.assertTrue(any("a.md:1" in line for line in lines))
        self.assertTrue(any("a.md:2" in line for line in lines))

    # spelling-scan: mentions 1
    def test_commit_message_mode_scans_the_supplied_file(self):
        with tempfile.TemporaryDirectory() as raw:
            message = Path(raw) / "COMMIT_EDITMSG"
            message.write_text("Describe the neighbouring row\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = scan.main(["--commit-message", str(message), "--quiet"])
        self.assertEqual(status, 1)
        self.assertIn("COMMIT_EDITMSG:1", output.getvalue())


class CommandLineModes(unittest.TestCase):
    # spelling-scan: mentions 1
    def test_default_mode_routes_through_the_staged_scan(self):
        dirty = scan.Report([scan.Finding("a.py", 1, "grey", "gray")],
                            scan.Evidence({}, ()))
        output = io.StringIO()
        with mock.patch.object(scan, "scan_staged", return_value=dirty):
            with contextlib.redirect_stdout(output):
                status = scan.main(["--quiet"])
        self.assertEqual(status, 1)
        self.assertIn("a.py:1", output.getvalue())

    # spelling-scan: mentions 2
    def test_all_mode_routes_tracked_filenames_through_the_scanner(self):
        output = io.StringIO()
        with (
            mock.patch.object(scan, "tracked_files", return_value=["grey-data.csv"]),
            contextlib.redirect_stdout(output),
        ):
            status = scan.main(["--all", "--quiet"])
        self.assertEqual(status, 1)
        self.assertIn("grey-data.csv", output.getvalue())

    # spelling-scan: mentions 2
    def test_path_mode_scans_the_named_files(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "grey.py"
            path.write_text("clean_value = 1\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = scan.main([str(path), "--quiet"])
        self.assertEqual(status, 1)
        self.assertIn("grey.py", output.getvalue())

    def test_paths_cannot_silently_override_an_explicit_mode(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                scan.main(["--all", "."])


class CommitMessageHook(unittest.TestCase):
    # spelling-scan: mentions 2
    def test_the_hook_warns_and_keeps_the_advisory_exit_status(self):
        with tempfile.TemporaryDirectory() as raw:
            message = Path(raw) / "COMMIT_EDITMSG"
            message.write_text("Describe the neighbouring row\n", encoding="utf-8")
            result = subprocess.run(
                ["sh", (REPO_ROOT / "tools" / "hooks" / "commit-msg").as_posix(),
                 message.as_posix()],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("neighbour", result.stderr)


if __name__ == "__main__":
    unittest.main()
