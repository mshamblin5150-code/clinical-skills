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

This file is Python, and the scanner reads Markdown only, so the forms written
out below are out of its scope rather than exempt from it. Nothing here declares
anything.
"""

import tempfile
import textwrap
import unittest
from pathlib import Path

import spelling_scan as scan

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "clinical-note" / "SKILL.md"

# day-b run 1, byte for byte apart from two redacted site names. Issue #73.
RECORD_FORMS = 10
RECORD_OCCURRENCES = 25
RECORD_NOTES = 7


def reader(**files: str):
    """A ``read`` callable over inline text, keyed by path with ``/`` for ``__``."""
    table = {path.replace("__", "/"): text for path, text in files.items()}
    return lambda path: table.get(path)


class CodeSpans(unittest.TestCase):
    """A form in a code span is a mention. In running prose it is a use."""

    def test_a_backticked_form_is_not_a_finding(self):
        findings = scan.scan_text("Never write `dyspnoea` here.", "a.md")
        self.assertEqual(findings, [])

    def test_a_double_backticked_form_is_not_a_finding(self):
        findings = scan.scan_text("British ``apnoea`` is not carried.", "a.md")
        self.assertEqual(findings, [])

    def test_the_same_form_in_prose_is_a_finding(self):
        findings = scan.scan_text("No dyspnoea at rest.", "a.md")
        self.assertEqual([f.form for f in findings], ["dyspnoea"])
        self.assertEqual(findings[0].american, "dyspnea")
        self.assertEqual(findings[0].line, 1)

    def test_a_span_shields_only_itself(self):
        findings = scan.scan_text("`grey` is out; the TMs were grey.", "a.md")
        self.assertEqual([f.form for f in findings], ["grey"])

    def test_a_table_row_of_mentions_is_clean(self):
        row = "| `grey`, `behaviour`, `colour` | `gray`, `behavior`, `color` |"
        self.assertEqual(scan.scan_text(row, "a.md"), [])

    def test_a_fenced_block_is_not_shielded(self):
        text = "```\nHt 5'10\", no dyspnoea at rest\n```\n"
        self.assertEqual([f.form for f in scan.scan_text(text, "a.md")], ["dyspnoea"])


class Matching(unittest.TestCase):
    def test_line_numbers_are_one_based(self):
        findings = scan.scan_text("clean\nclean\nthe grey membrane\n", "a.md")
        self.assertEqual([(f.line, f.form) for f in findings], [(3, "grey")])

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

    def test_a_stem_change_is_carried_explicitly(self):
        findings = scan.scan_text("labelling the proposals", "a.md")
        self.assertEqual([(f.form, f.american) for f in findings],
                         [("labelling", "labeling")])

    def test_a_form_inside_a_longer_word_is_not_matched(self):
        self.assertEqual(scan.scan_text("a greyhound", "a.md"), [])

    def test_millilitres_is_one_finding_not_two(self):
        """``litre`` must not fire inside ``millilitre``."""
        findings = scan.scan_text("10 millilitres", "a.md")
        self.assertEqual([f.form for f in findings], ["millilitre"])

    def test_matching_ignores_case(self):
        self.assertEqual([f.form for f in scan.scan_text("Grey TMs", "a.md")], ["grey"])

    def test_drug_names_take_the_us_generic(self):
        findings = scan.scan_text("gave paracetamol and adrenaline", "a.md")
        self.assertEqual([(f.form, f.american) for f in findings],
                         [("paracetamol", "acetaminophen"),
                          ("adrenaline", "epinephrine")])


class Evidence(unittest.TestCase):
    """The run record is evidence. It is counted and never refused."""

    def test_a_note_in_the_record_yields_no_findings(self):
        report = scan.scan(
            ["fixtures/filled-anchor/notes/case-07.md"],
            reader(**{"fixtures__filled-anchor__notes__case-07.md": "no dyspnoea"}),
        )
        self.assertEqual(report.findings, [])

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

    def test_the_records_own_readme_is_not_evidence(self):
        """It is prose about the record, so it takes the mention rule like any prose."""
        report = scan.scan(
            ["fixtures/filled-anchor/notes/README.md"],
            reader(**{"fixtures__filled-anchor__notes__README.md": "it wrote dyspnoea"}),
        )
        self.assertEqual([f.form for f in report.findings], ["dyspnoea"])
        self.assertEqual(report.evidence.occurrences, 0)

    def test_only_markdown_is_read(self):
        report = scan.scan(["tools/x.py"], reader(tools__x__py="dyspnoea"))
        self.assertEqual(report.findings, [])


class ARunDirectory(unittest.TestCase):
    """Grading a run's output, which is the only thing that exercises the rule."""

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

    def test_every_drug_form_is_named_by_the_skill(self):
        for british, american in scan.DRUGS.items():
            with self.subTest(form=british):
                self.assertIn(british, self.text)
                self.assertIn(american, self.text)


class TheRunRecord(unittest.TestCase):
    """Issue #73's evidence, recomputed from the committed notes."""

    @classmethod
    def setUpClass(cls):
        cls.report = scan.scan(scan.tracked_markdown(), scan.read_tracked)

    def test_the_tally_is_unchanged(self):
        evidence = self.report.evidence
        self.assertEqual(len(evidence.forms), RECORD_FORMS)
        self.assertEqual(evidence.occurrences, RECORD_OCCURRENCES)
        self.assertEqual(len(evidence.files), RECORD_NOTES)

    def test_the_ten_forms_are_the_ones_the_ticket_names(self):
        # **Eight until 2026-08-18, then nine, then ten within the hour.** The run
        # record has not changed and cannot -- ``fixtures/filled-anchor/notes/``
        # is a byte-for-byte record of what a day-b run produced, apart from two
        # redacted site names. What changed is the *table*: ``neighbour`` was
        # never a listed form, so two occurrences of it sat in these notes
        # unseen and uncounted, and adding the form to ``FORMS`` is what made
        # them visible. #73's evidence set got larger without the evidence
        # moving, which is the distinction this class exists to hold.
        #
        # **``judgement`` is the tenth and it was named in the repo's own docs
        # the whole time.** ``docs/agents/issue-tracker.md`` lists it beside
        # ``neighbouring`` as a British form the table does not hold -- written
        # to warn about ticket text, while three occurrences sat in these
        # committed notes. **A form documented as invisible is still invisible**,
        # and naming one in prose is not the same as adding it to the table.
        self.assertEqual(
            sorted(self.report.evidence.forms),
            ["behaviour", "caesarean", "dyspnoea", "fibre", "grey", "judgement",
             "labelled", "neighbour", "programme", "recognisable"],
        )

    def test_no_tracked_markdown_uses_a_british_spelling(self):
        """Item 2 of #73, made permanent: no assertion row quotes one either."""
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

    def test_the_run_wrote_both_spellings_of_the_same_word(self):
        """The counterpart column is #73's argument: drift, not a British register."""
        rows = {row.form: row for row in self.rows}
        self.assertEqual((rows["caesarean"].british, rows["caesarean"].american_count), (2, 8))
        self.assertEqual((rows["dyspnoea"].british, rows["dyspnoea"].american_count), (3, 7))
        self.assertEqual((rows["fibre"].british, rows["fibre"].american_count), (4, 3))

    def test_the_view_names_cases_and_counts_only(self):
        rendered = "\n".join(scan.render_record(self.rows))
        for row in self.rows:
            self.assertIn(row.form, rendered)
        for case, _ in (pair for row in self.rows for pair in row.cases):
            self.assertRegex(case, r"^case-\d\d$")


class TheWalkedPopulation(unittest.TestCase):
    """#258: what a clean result covers, on the page rather than in a docstring.

    #254 ruled that every ``git ls-files`` walk states what a clean result
    covers, and `tracked_markdown`'s statement went into its docstring. This
    scanner prints ``no listed British spelling found.`` -- an unqualified clean
    result, in the one walk with the **recorded** instance rather than the
    hypothetical one: ``CLAUDE.md`` carries ``licence`` landing in a skill file
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

    def test_the_all_mode_line_names_tracked_and_what_that_excludes(self):
        """Both limbs, on #254's reasoning: *tracked* alone is what the walk's
        name already said, and *untracked* alone never says what a pass means."""
        line = self.population(scan.render(self.clean(), False, "--all"))
        self.assertRegex(line, r"(?<!un)tracked")
        self.assertRegex(line, r"(?i)untracked")

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


class Reporting(unittest.TestCase):
    def test_a_clean_scan_exits_zero(self):
        report = scan.Report([], scan.Evidence({}, ()))
        self.assertEqual(scan.render(report, quiet=True, mode='staged'), [])

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


if __name__ == "__main__":
    unittest.main()
