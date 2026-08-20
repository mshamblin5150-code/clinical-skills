"""Tests for skills_mirror.py.

Every test builds a throwaway checkout in a temp directory and runs against that.
**Nothing here touches the real `skills/` or `.claude/skills/`** -- a test that
inspected the live mirror would pass or fail on the state of the machine it ran on,
which is the opposite of what a regression test is for, and `--repair` against the
real tree would rewrite the developer's install as a side effect of running tests.
Same reasoning as test_icd10.py never opening the shipped database.
"""

import io
import os
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import skills_mirror as sm


def make_skill(root: Path, name: str, body: str = "# skill\n", extra=None):
    """Create skills/<name>/SKILL.md plus any extra files."""
    d = root / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(body, encoding="utf-8")
    for rel, text in (extra or {}).items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return d


def copy_into_mirror(root: Path, name: str, overrides=None):
    """Put a plain-directory copy of a skill into .claude/skills/, as a dereferenced
    junction leaves behind. `overrides` rewrites or adds files, making it stale."""
    src = root / "skills" / name
    dst = root / ".claude" / "skills" / name
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.rglob("*"):
        if p.is_file():
            target = dst / p.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(p.read_bytes())
    for rel, text in (overrides or {}).items():
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return dst


def write_exact(path: Path, data: bytes):
    r"""Write bytes with no newline translation.

    `Path.write_text` rewrites `\n` as `\r\n` on Windows, which is exactly the
    difference the line-ending tests are about, so nothing measuring one may go
    through it. Every other helper here may, and does.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def copy_with_exact_bytes(root: Path, name: str, files: dict):
    """One skill copied into the mirror, then some files rewritten on both sides.

    `files` maps a relative path to `(canonical bytes, mirror bytes)`. Exact bytes
    throughout, because every other helper here goes through `write_text` and that
    translates newlines on Windows -- which is the difference being measured.
    """
    make_skill(root, name)
    copy_into_mirror(root, name)
    for rel, (canonical, mirror) in files.items():
        write_exact(root / "skills" / name / rel, canonical)
        write_exact(root / ".claude" / "skills" / name / rel, mirror)


def status_of(root: Path, name: str):
    return {e.name: e for e in sm.inspect(root)}[name]


class TempCheckout(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        # resolve() so comparisons survive macOS /var -> /private/var and any
        # Windows short-name form of the temp path.
        self.root = Path(self._tmp.name).resolve()
        (self.root / ".claude" / "skills").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()


class DiscoveryTests(TempCheckout):
    def test_a_directory_with_a_skill_md_is_a_skill(self):
        make_skill(self.root, "clinical-note")
        make_skill(self.root, "icd10-cpt")
        self.assertEqual(sm.skill_names(self.root), ["clinical-note", "icd10-cpt"])

    def test_a_directory_without_a_skill_md_is_not(self):
        make_skill(self.root, "clinical-note")
        (self.root / "skills" / "notes").mkdir()
        (self.root / "skills" / "notes" / "README.md").write_text("x", encoding="utf-8")
        self.assertEqual(sm.skill_names(self.root), ["clinical-note"])

    def test_no_skills_directory_is_empty_not_an_error(self):
        empty = self.root / "nowhere"
        empty.mkdir()
        self.assertEqual(sm.skill_names(empty), [])

    def test_mirror_only_entries_are_ignored(self):
        """.claude/skills/ also holds the maintainer's own skills. They are not
        mirrors of anything and must never be reported."""
        make_skill(self.root, "clinical-note")
        sm.link(self.root / ".claude" / "skills" / "clinical-note",
                self.root / "skills" / "clinical-note")
        (self.root / ".claude" / "skills" / "triage").mkdir()
        names = [e.name for e in sm.inspect(self.root)]
        self.assertEqual(names, ["clinical-note"])


class StatusTests(TempCheckout):
    def test_a_link_to_the_canonical_skill_is_ok(self):
        make_skill(self.root, "clinical-note")
        sm.link(self.root / ".claude" / "skills" / "clinical-note",
                self.root / "skills" / "clinical-note")
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.status, sm.LINKED)
        self.assertTrue(entry.ok)

    def test_an_absent_entry_is_missing(self):
        make_skill(self.root, "setup-clinical-skills")
        entry = status_of(self.root, "setup-clinical-skills")
        self.assertEqual(entry.status, sm.MISSING)
        self.assertFalse(entry.ok)

    def test_a_copy_that_matches_today_is_still_a_finding(self):
        make_skill(self.root, "batch-shift")
        copy_into_mirror(self.root, "batch-shift")
        entry = status_of(self.root, "batch-shift")
        self.assertEqual(entry.status, sm.IDENTICAL)
        self.assertFalse(entry.ok)

    def test_a_copy_whose_content_diverged_is_stale(self):
        make_skill(self.root, "clinical-note", body="rule kept\n")
        copy_into_mirror(self.root, "clinical-note",
                         overrides={"SKILL.md": "rule retired by #23\n"})
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.status, sm.STALE)
        self.assertEqual(entry.differs, [("SKILL.md", sm.CONTENT)])

    def test_a_file_added_to_the_canonical_skill_makes_the_copy_stale(self):
        """The row-13 case: the copy is not wrong about what it holds, it is
        missing a file the skill gained afterwards."""
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note")
        (self.root / "skills" / "clinical-note" / "SOAP.md").write_text("s", encoding="utf-8")
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.status, sm.STALE)
        self.assertEqual(entry.differs, [("SOAP.md", sm.CONTENT)])

    def test_a_file_only_in_the_mirror_is_reported_separately(self):
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note", overrides={"NOTES.md": "mine\n"})
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.status, sm.STALE)
        self.assertEqual(entry.extra, ["NOTES.md"])

    def test_a_link_to_another_checkout_is_foreign(self):
        """A worktree whose mirror points back at the main tree reads correct today
        and answers with the wrong branch from the first divergent commit."""
        other = self.root / "other-checkout"
        make_skill(other, "clinical-note", body="main branch\n")
        make_skill(self.root, "clinical-note", body="this branch\n")
        sm.link(self.root / ".claude" / "skills" / "clinical-note",
                other / "skills" / "clinical-note")
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.status, sm.FOREIGN)
        self.assertEqual(entry.target, (other / "skills" / "clinical-note").resolve())

    def test_a_file_where_a_directory_belongs(self):
        make_skill(self.root, "clinical-note")
        (self.root / ".claude" / "skills" / "clinical-note").write_text("x", encoding="utf-8")
        self.assertEqual(status_of(self.root, "clinical-note").status, sm.NOT_A_DIR)


class LineEndingTests(TempCheckout):
    r"""#198: a CRLF-only difference is a difference, and it is not drift.

    `copy-stale` is the status word this repo cites as evidence that an agent may
    already have read a retired rule -- #93's first comment reasons from one, and
    that worktree is gone, so the instance can no longer be told apart from three
    carriage returns. A mirror copy written before an agent rewrote a skill file
    with `\n` fires it on line endings alone.

    **The comparison stays byte-exact.** Normalizing it away was option 1 and was
    declined: a copy that differs on disk is still a copy, and a byte check is the
    thing that cannot be argued with. What was ruled is that the report says which
    kind of difference it found, so the reader gets the distinction back without
    the check losing its teeth.
    """

    def stale_pair(self, canonical: bytes, mirror: bytes, rel: str = "SKILL.md"):
        """One file written exactly on both sides, and the entry that results."""
        copy_with_exact_bytes(self.root, "clinical-note", {rel: (canonical, mirror)})
        return status_of(self.root, "clinical-note")

    def test_a_crlf_only_difference_is_named_as_line_endings(self):
        entry = self.stale_pair(b"# skill\nrule kept\n", b"# skill\r\nrule kept\r\n")
        self.assertEqual(entry.differs, [("SKILL.md", sm.LINE_ENDINGS)])

    def test_a_crlf_only_difference_is_still_a_stale_copy(self):
        """Option 1's half that was declined. The word changes; the finding does not."""
        entry = self.stale_pair(b"# skill\n", b"# skill\r\n")
        self.assertEqual(entry.status, sm.STALE)
        self.assertFalse(entry.ok)

    def test_content_differing_under_matching_endings_is_content(self):
        entry = self.stale_pair(b"rule kept\r\n", b"rule retired by #23\r\n")
        self.assertEqual(entry.differs, [("SKILL.md", sm.CONTENT)])

    def test_content_and_endings_differing_together_is_content(self):
        """The one that must not read as harmless: #223's real drift arrived in a
        worktree, and a rule that answered *line endings* to any file carrying both
        would have called it one."""
        entry = self.stale_pair(b"rule kept\n", b"rule retired by #23\r\n")
        self.assertEqual(entry.differs, [("SKILL.md", sm.CONTENT)])

    def test_a_lone_cr_that_only_one_side_holds_is_content(self):
        r"""Only CRLF-versus-LF is the ruled question, so the normalization is
        `\r\n` -> `\n` and never *strip every* `\r`.

        **This is the discriminating pair and the obvious one is not.** `a\rb\n`
        against `a\nb\n` reads CONTENT under either rule, so a test written on it
        passes without measuring anything -- caught by mutating `_normalized` to
        strip every `\r` and watching the class stay green. Dropping the `\r`
        outright is what separates them: strip-every-`\r` calls these two files a
        line-ending difference, which is the reason word over-claiming harmlessness
        about a carriage return that is really content.
        """
        entry = self.stale_pair(b"a\rb\n", b"ab\n")
        self.assertEqual(entry.differs, [("SKILL.md", sm.CONTENT)])

    def test_a_file_the_mirror_does_not_hold_is_content(self):
        """The partition is two-way so the counts in the report sum to the total.
        A file the copy is missing is not carriage returns, which is the whole
        question the split answers."""
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note")
        write_exact(self.root / "skills" / "clinical-note" / "SOAP.md", b"s\n")
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.differs, [("SOAP.md", sm.CONTENT)])

    def test_the_two_reasons_partition_the_differing_files(self):
        copy_with_exact_bytes(self.root, "clinical-note", {
            "HP.md": (b"same\n", b"same\r\n"),
            "SKILL.md": (b"kept\r\n", b"retired\r\n"),
        })
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.content_differs, ["SKILL.md"])
        self.assertEqual(entry.endings_differs, ["HP.md"])
        self.assertEqual(
            [(d.rel, d.reason) for d in entry.differs],
            [("HP.md", sm.LINE_ENDINGS), ("SKILL.md", sm.CONTENT)],
        )
        self.assertEqual(
            len(entry.content_differs) + len(entry.endings_differs),
            len(entry.differs),
        )


class RepairTests(TempCheckout):
    def test_repair_replaces_a_stale_copy_with_a_link(self):
        make_skill(self.root, "clinical-note", body="rule kept\n")
        copy_into_mirror(self.root, "clinical-note",
                         overrides={"SKILL.md": "rule retired\n"})
        repaired, refusals = sm.repair(self.root, sm.inspect(self.root))
        self.assertEqual((repaired, refusals), (1, []))
        self.assertEqual(status_of(self.root, "clinical-note").status, sm.LINKED)
        mirrored = self.root / ".claude" / "skills" / "clinical-note" / "SKILL.md"
        self.assertEqual(mirrored.read_text(encoding="utf-8"), "rule kept\n")

    def test_repair_creates_a_missing_entry(self):
        make_skill(self.root, "setup-clinical-skills")
        repaired, refusals = sm.repair(self.root, sm.inspect(self.root))
        self.assertEqual((repaired, refusals), (1, []))
        self.assertEqual(status_of(self.root, "setup-clinical-skills").status, sm.LINKED)

    def test_repair_refuses_a_copy_holding_a_file_of_its_own(self):
        """Relinking deletes the copy. A file that exists nowhere else is not this
        script's to discard."""
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note", overrides={"NOTES.md": "mine\n"})
        repaired, refusals = sm.repair(self.root, sm.inspect(self.root))
        self.assertEqual(repaired, 0)
        self.assertEqual(len(refusals), 1)
        self.assertIn("NOTES.md", refusals[0])
        self.assertTrue((self.root / ".claude" / "skills" / "clinical-note" / "NOTES.md").exists())

    def test_repair_removes_a_foreign_link_and_never_its_target(self):
        other = self.root / "other-checkout"
        make_skill(other, "clinical-note", body="main branch\n")
        make_skill(self.root, "clinical-note", body="this branch\n")
        sm.link(self.root / ".claude" / "skills" / "clinical-note",
                other / "skills" / "clinical-note")
        repaired, refusals = sm.repair(self.root, sm.inspect(self.root))
        self.assertEqual((repaired, refusals), (1, []))
        self.assertEqual(status_of(self.root, "clinical-note").status, sm.LINKED)
        self.assertEqual(
            (other / "skills" / "clinical-note" / "SKILL.md").read_text(encoding="utf-8"),
            "main branch\n",
        )

    def test_repair_leaves_an_already_linked_skill_alone(self):
        make_skill(self.root, "clinical-note")
        sm.link(self.root / ".claude" / "skills" / "clinical-note",
                self.root / "skills" / "clinical-note")
        repaired, refusals = sm.repair(self.root, sm.inspect(self.root))
        self.assertEqual((repaired, refusals), (0, []))


class CliTests(TempCheckout):
    def run_main(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = sm.main([*argv, "--root", str(self.root)])
        return code, buf.getvalue()

    def test_exit_zero_and_silent_when_every_skill_is_linked(self):
        make_skill(self.root, "clinical-note")
        sm.link(self.root / ".claude" / "skills" / "clinical-note",
                self.root / "skills" / "clinical-note")
        code, out = self.run_main("--quiet")
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_exit_one_and_loud_when_a_copy_is_stale(self):
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note", overrides={"SKILL.md": "old\n"})
        code, out = self.run_main("--quiet")
        self.assertEqual(code, 1)
        self.assertIn(sm.STALE, out)

    def test_verbose_names_the_files_and_never_their_contents(self):
        make_skill(self.root, "clinical-note", body="a hypertensive pressure\n")
        copy_into_mirror(self.root, "clinical-note",
                         overrides={"SKILL.md": "a raised respiratory rate\n"})
        code, out = self.run_main("--verbose")
        self.assertEqual(code, 1)
        self.assertIn("differs (content): SKILL.md", out)
        self.assertNotIn("respiratory", out)
        self.assertNotIn("hypertensive", out)

    def test_the_report_names_both_reasons_on_every_run(self):
        """#198's deliverable. The two counts print whether or not each fired, on
        ``checks_ledger.py``'s precedent -- *say which is which* is the clause a
        report drops in silence, and a reader who has learned to read one count
        reads its absence as the other being zero."""
        copy_with_exact_bytes(self.root, "clinical-note", {
            "HP.md": (b"same\n", b"same\r\n"),
            "SKILL.md": (b"kept\r\n", b"retired\r\n"),
        })
        code, out = self.run_main("--verbose")
        self.assertEqual(code, 1)
        self.assertIn("(2 file(s) differ: 1 content, 1 line endings only)", out)
        self.assertIn("differs (content): SKILL.md", out)
        self.assertIn("differs (line endings only): HP.md", out)

    def test_a_line_endings_only_copy_says_zero_content(self):
        """The reading #93's citable instance can no longer be given: this copy is
        stale, and it is stale about nothing a reader would follow."""
        copy_with_exact_bytes(self.root, "clinical-note",
                              {"SKILL.md": (b"# skill\n", b"# skill\r\n")})
        code, out = self.run_main("--quiet")
        self.assertEqual(code, 1)
        self.assertIn(sm.STALE, out)
        self.assertIn("(1 file(s) differ: 0 content, 1 line endings only)", out)

    def test_the_closing_sentence_stops_claiming_a_rule_may_have_been_followed(self):
        """#198's harm is not the row, it is the sentence a skimming reader reads.

        `an agent reading the mirror may follow a retired rule` is what `copy-stale`
        is cited for, and it is the claim a CRLF-only difference cannot support. When
        nothing differs in content the report says so, next to that sentence.
        """
        copy_with_exact_bytes(self.root, "clinical-note",
                              {"SKILL.md": (b"# skill\n", b"# skill\r\n")})
        code, out = self.run_main("--quiet")
        self.assertEqual(code, 1)
        self.assertIn("No copy differs in content", out)

    def test_one_content_difference_withdraws_that_reassurance(self):
        """One file is enough. The sentence is about the whole report, so a run
        holding any content difference gets no qualifier at all."""
        copy_with_exact_bytes(self.root, "clinical-note", {
            "HP.md": (b"same\n", b"same\r\n"),
            "SKILL.md": (b"kept\r\n", b"retired\r\n"),
        })
        code, out = self.run_main("--quiet")
        self.assertEqual(code, 1)
        self.assertNotIn("No copy differs in content", out)

    def test_a_copy_that_matches_today_gets_no_reassurance_either(self):
        """`copy-identical` differs from `copy-stale` in how much time is left, not
        in whether the wiring is broken -- and this line is about differences found,
        so a run that found none must not print it."""
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note")
        code, out = self.run_main("--quiet")
        self.assertEqual(code, 1)
        self.assertIn(sm.IDENTICAL, out)
        self.assertNotIn("No copy differs in content", out)

    def test_repair_flag_fixes_and_exits_zero(self):
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note", overrides={"SKILL.md": "old\n"})
        code, out = self.run_main("--repair")
        self.assertEqual(code, 0)
        self.assertIn("relinked 1", out)
        self.assertEqual(status_of(self.root, "clinical-note").status, sm.LINKED)

    def test_repair_flag_exits_one_when_it_refuses(self):
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note", overrides={"NOTES.md": "mine\n"})
        code, out = self.run_main("--repair")
        self.assertEqual(code, 1)
        self.assertIn("REFUSED", out)


class TheReasonWordsAreStatedInOnePlaceAndDescribedInAnother(unittest.TestCase):
    """#198's two reason words live in the module and are described in `CLAUDE.md`.

    A prose edit to either copy fails nothing on its own, which is [#220]'s lesson,
    and these two are user-visible status vocabulary -- a reader who learns
    `line endings only` from one document and meets a renamed word in the other has
    been told the check reports something it does not. So the needles are derived
    from the module rather than typed here, and what is asserted is the **rendered**
    form: a bare `content` would match the sentence promising the scanner prints no
    file contents, which would be a check that could not fail.
    """

    def section(self) -> str:
        text = (Path(__file__).resolve().parent.parent / "CLAUDE.md").read_text(
            encoding="utf-8"
        )
        start = text.index("### Skills mirror")
        end = text.index("\n### ", start + 1)
        return text[start:end]

    def test_the_section_names_both_reasons_as_the_command_prints_them(self):
        section = self.section()
        for reason in (sm.CONTENT, sm.LINE_ENDINGS):
            self.assertIn(f"differs ({reason}):", section)

    def test_the_section_shows_the_summary_line_both_counts_sit_on(self):
        self.assertIn(f"{sm.LINE_ENDINGS})", self.section())


if __name__ == "__main__":
    unittest.main()
