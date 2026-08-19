"""``.gitignore`` covers every guideline build artifact, as a second net.

The three write guards refuse a target inside a git checkout, and [#176] records
that they are three implementations with different detection rules -- the one in
``guidelines_index.py`` compares against known roots, so it catches this worktree
and the clone that owns it and **misses a sibling worktree or any other repo
nearby**. In a private repo a mis-typed ``--out`` was clutter. Public, it is
publication of society-copyrighted expression, which is [#223]'s second bullet and
what re-priced #176's *"Not urgent"*.

**This is the second net and not a replacement for the guards.** A guard refuses
the write; this only stops the result being committed if one is missed.

Two of the three artifact names are **derived from the tools' own defaults**
rather than typed here, on ``test_ci_workflow.py``'s reasoning: a list of names
copied into a test goes stale the first time a default moves, and reads as
coverage while it does. **The third is typed, and it is the weak one** --
``guidelines_recs.py`` has no default ``--json`` path to derive from, so
``recs-<stem>.json`` is read off ``threshold_sheet.py``'s tier-2 lookup by a human
and restated below. A rename there would leave this passing.

**Every query is a file path and never a directory with a trailing slash**, and
``TheInstrumentIsLive`` is why. Asked about ``tools/``, ``git check-ignore``
answers *ignored* and cites a blank line -- so the first version of this file
passed three of its four assertions against a check that says yes to everything.
That is this repo's recurring shape with the sign flipped: not a search that could
not have worked answering like a settled negative, but one answering like a
settled positive.

**Which blank line is deliberately not named here.** The first draft said line 29,
and the ``.gitignore`` block this same commit adds pushed it to 33 -- a figure
stale inside the commit that wrote it, which is [#143] happening in the paragraph
warning about it. The durable claim is that a trailing-slash query matches
something and a file path does not, and ``TheInstrumentIsLive`` asserts that
rather than restating it.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import guidelines_extract
import guidelines_index
from repo_root import main_repo_root

REPO_ROOT = Path(__file__).resolve().parent.parent


def _check_ignore(relative: str) -> bool:
    """Would git ignore ``relative`` if it appeared at the repo root?

    ``--no-index`` so the answer is about the rules rather than about whether the
    path happens to exist or be tracked right now.
    """
    finished = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", "--", relative],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return finished.returncode == 0


class TheInstrumentIsLive(unittest.TestCase):
    """A path nothing covers must come back not-ignored, or the rest proves nothing."""

    def test_an_uncovered_path_is_not_ignored(self) -> None:
        self.assertFalse(_check_ignore("zzz-nothing-covers-this/afile.txt"))

    def test_a_tracked_directorys_contents_are_not_ignored(self) -> None:
        self.assertFalse(_check_ignore("tools/guidelines_extract.py"))

    def test_the_phi_firewall_lines_do_fire(self) -> None:
        """Standing rule 1's own lines, so a broken query cannot read as a pass.

        All four, because the firewall is what a wrong answer here would hide, and
        because a claim about it elsewhere should rest on an assertion rather than
        on one of the four being spot-checked.
        """
        for path in (
            "scratch/day-file-text/anything.md",
            "output/a-finished-note.md",
            "cases/anything.md",
            "patients/anything.md",
        ):
            with self.subTest(path=path):
                self.assertTrue(_check_ignore(path))


class TheGuidelineBuildArtifactsAreIgnored(unittest.TestCase):
    def test_the_extractor_default_output_directory(self) -> None:
        """``guidelines-src`` -> ``guidelines-text``, the name #80 actually writes."""
        source = main_repo_root().parent / "guidelines-src"
        name = guidelines_extract.default_output(source).name
        self.assertEqual(name, "guidelines-text")
        self.assertTrue(
            _check_ignore(f"{name}/manifest.json"),
            f"{name}/ is the extractor's default output name and .gitignore does not cover it",
        )

    def test_any_source_directory_the_extractor_is_pointed_at(self) -> None:
        """The default is ``<stem>-text`` for whatever the source is called.

        Pinning only ``guidelines-text`` would leave a second corpus uncovered, and
        the suffix is the part the tool guarantees.
        """
        for source_name in ("guidelines-src", "kdigo-src", "society"):
            source = main_repo_root().parent / source_name
            name = guidelines_extract.default_output(source).name
            with self.subTest(source=source_name):
                self.assertTrue(name.endswith("-text"))
                self.assertTrue(
                    _check_ignore(f"{name}/manifest.json"),
                    f"{name}/ is a default output name and .gitignore does not cover it",
                )

    def test_an_extracted_page_file_and_not_only_the_manifest(self) -> None:
        """The manifest is metadata; the ``.txt`` is the society's page text."""
        self.assertTrue(_check_ignore("guidelines-text/KDIGO/KDIGO-2024-CKD-Guideline.txt"))

    def test_the_index_default_database_directory(self) -> None:
        database = guidelines_index.default_database()
        self.assertEqual(database.parent.name, "guidelines-index")
        self.assertTrue(
            _check_ignore(f"{database.parent.name}/{database.name}"),
            "guidelines-index/ holds the index and the recs dumps, and .gitignore misses it",
        )

    def test_a_recommendation_dump(self) -> None:
        """``threshold_sheet.py`` looks for ``recs-<stem>.json``, so that is the shape.

        ``guidelines_recs.py`` has no default ``--json`` path -- the naming
        convention lives on the reading side, at ``threshold_sheet.py``'s tier 2.
        """
        self.assertTrue(
            _check_ignore("recs-some-guideline.json"),
            "a recs dump holds the society's recommendation text in full and is not ignored",
        )
        self.assertTrue(
            _check_ignore("reference/recs-some-guideline.json"),
            "the pattern must reach a subdirectory, which is where a mis-typed --json lands",
        )


class TheNetDoesNotSwallowWhatIsCommitted(unittest.TestCase):
    """A pattern wide enough to hide a tracked file is worse than the gap.

    ``reference/icd10cm-2026.sqlite`` is committed deliberately, and an index
    landing anywhere is a build artifact -- so this is the boundary a bare
    ``*.sqlite`` rule would cross, and the reason there is not one.
    """

    def test_every_tracked_file_is_still_visible(self) -> None:
        finished = subprocess.run(
            ["git", "ls-files", "--cached"],
            cwd=REPO_ROOT,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        tracked = [line for line in finished.stdout.splitlines() if line.strip()]
        self.assertGreater(len(tracked), 100, "git ls-files returned too little to be a checkout")
        ignored = [path for path in tracked if _check_ignore(path)]
        self.assertEqual(
            ignored,
            [],
            "these files are tracked and .gitignore now hides them: " + ", ".join(ignored),
        )


if __name__ == "__main__":
    unittest.main()
