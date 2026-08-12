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
        self.assertEqual(entry.differs, ["SKILL.md"])

    def test_a_file_added_to_the_canonical_skill_makes_the_copy_stale(self):
        """The row-13 case: the copy is not wrong about what it holds, it is
        missing a file the skill gained afterwards."""
        make_skill(self.root, "clinical-note")
        copy_into_mirror(self.root, "clinical-note")
        (self.root / "skills" / "clinical-note" / "SOAP.md").write_text("s", encoding="utf-8")
        entry = status_of(self.root, "clinical-note")
        self.assertEqual(entry.status, sm.STALE)
        self.assertEqual(entry.differs, ["SOAP.md"])

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
        self.assertIn("differs: SKILL.md", out)
        self.assertNotIn("respiratory", out)
        self.assertNotIn("hypertensive", out)

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


if __name__ == "__main__":
    unittest.main()
