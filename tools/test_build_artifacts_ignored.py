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

Artifact names are **derived from their producing tools** rather than typed here,
on ``test_ci_workflow.py``'s reasoning: a list of names copied into a test goes
stale the first time a default or convention moves, and reads as coverage while
it does. The recommendation record was the weak one until #518:
#177 renamed ``recs-<sheet stem>.json`` to ``recs-<source key>.json`` with this
file left green throughout because the test had restated the prefix by hand.

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

from collections.abc import Sequence
import subprocess
import unittest
from pathlib import Path

import guidelines_extract
import guidelines_index
import guidelines_recs
import docx_write
import git_paths
from repo_root import main_repo_root

REPO_ROOT = Path(__file__).resolve().parent.parent


def _ignored(paths: Sequence[str]) -> set[str]:
    """Return the members of ``paths`` ignored by the repository's rules."""
    stdin = b"".join(
        path.encode("utf-8", errors="surrogateescape") + b"\0" for path in paths
    )
    return set(
        git_paths.read_path_records(
            REPO_ROOT,
            "check-ignore",
            "--no-index",
            "--stdin",
            "-z",
            stdin=stdin,
            accepted_returncodes=(0, 1),
        )
    )


def _check_ignore(relative: str) -> bool:
    """Would git ignore ``relative`` if it appeared at the repo root?

    ``--no-index`` so the answer is about the rules rather than about whether the
    path happens to exist or be tracked right now.
    """
    return relative in _ignored((relative,))


def _ignore_source(relative: str) -> str | None:
    """Which file holds the rule that ignores ``relative``, if any.

    **``_check_ignore`` is not enough for a rule this repo is adding**, because
    ``.git/info/exclude`` can already cover the same path on the machine the test
    runs on -- and that file being neither tracked nor cloned is the entire defect
    [#178]'s comment 8 records. The first version of
    ``AWorktreeIsNotPartOfItsParent`` asserted only that git ignored the path, and
    it **passed with the ``.gitignore`` line deleted**: a machine-local exclude
    read as though it were the committed rule. That is this file's own
    ``TheInstrumentIsLive`` lesson arriving one class later, and the fix is to ask
    git *which* file answered rather than whether one did.
    """
    finished = subprocess.run(
        ["git", "check-ignore", "--no-index", "-v", "--", relative],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if finished.returncode != 0 or not finished.stdout.strip():
        return None
    # `<source>:<line>:<pattern>	<path>`. The source is a Windows path here, so
    # it carries a colon of its own -- the split comes off the tab first and then
    # off the *last* two colons rather than the first.
    return finished.stdout.strip().split("	", 1)[0].rsplit(":", 2)[0]


class TheInstrumentIsLive(unittest.TestCase):
    """A path nothing covers must come back not-ignored, or the rest proves nothing."""

    def test_a_population_returns_only_the_ignored_paths(self) -> None:
        paths = (
            "tools/guidelines_extract.py",
            "scratch/day-file-text/anything.md",
            "output/a-finished-note.md",
        )
        self.assertEqual(
            _ignored(paths),
            {"scratch/day-file-text/anything.md", "output/a-finished-note.md"},
        )

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


class AWorktreeIsNotPartOfItsParent(unittest.TestCase):
    """[#178]: the only rule covering ``.claude/worktrees/`` was one git never clones.

    ``.git/info/exclude`` is not tracked and not cloned, so on this machine the
    tooling scratch under a worktree was invisible and on a fresh clone the same
    run left it untracked, visible and one ``git add -A`` from being committed --
    which for this repo's tooling means society-derived threshold text, and
    ``phi_scan`` will never flag it because guideline text is not PHI.

    **This does not reach the worse half of that finding and is not claimed to.**
    A generator whose ``OUT`` points at a path under a tracked directory writes a
    **modification to a tracked file**, which no ignore rule suppresses. That
    stays a write guard's job, on ``repo_root.ensure_outside_checkout``'s
    terms.
    """

    def _assert_gitignore_covers(self, relative: str) -> None:
        """The rule has to come from ``.gitignore`` and from nowhere else.

        ``.git/info/exclude`` covers this prefix on the maintainer's machine, so an
        assertion that git merely ignores the path is satisfied by the very file
        whose absence from a clone is the defect being fixed.
        """
        source = _ignore_source(relative)
        self.assertIsNotNone(source, f"nothing ignores {relative}")
        # The repo root's own `.gitignore` and not merely a file of that name: a
        # nested one somewhere in the tree would satisfy a name comparison while
        # saying nothing about the rule a fresh clone gets. `check-ignore` runs
        # with `cwd=REPO_ROOT` and names an in-tree source relative to it, so that
        # is what the path resolves against -- an absolute answer, which is what
        # `.git/info/exclude` comes back as, survives the join unchanged.
        self.assertEqual(
            (REPO_ROOT / source).resolve(),
            (REPO_ROOT / ".gitignore").resolve(),
            f"{relative} is ignored by {source}, which a fresh clone does not have",
        )

    def test_a_worktrees_own_checkout_is_ignored(self) -> None:
        self._assert_gitignore_covers(".claude/worktrees/some-branch/README.md")

    def test_the_artifact_that_prompted_it(self) -> None:
        """A regenerated threshold sheet under a dead worktree path -- the shape
        ``build_htn_sheet.py`` writes, and the one that reads as a curated
        artifact rather than as scratch."""
        self._assert_gitignore_covers(
            ".claude/worktrees/gone/reference/thresholds/hypertension.md"
        )

    def test_it_does_not_reach_the_real_reference_directory(self) -> None:
        """The rule is about the worktree prefix and nothing else. A committed
        sheet at its real path must stay visible, or the net would hide the
        artifact it exists to protect."""
        self.assertFalse(_check_ignore("reference/thresholds/hypertension.md"))

    def test_the_local_settings_file_is_covered_by_the_tracked_boundary(self) -> None:
        self._assert_gitignore_covers(".claude/settings.local.json")

    def test_the_retrieval_log_is_covered_by_the_tracked_boundary(self) -> None:
        """The log is written by machinery outside this repository's control.

        Ignoring it is a publication boundary, not a claim about what the file
        contains or about whether another scanner could interpret it.
        """
        self._assert_gitignore_covers(".claude/live-retrieval-log.jsonl")

    def test_a_future_claude_file_is_covered_without_enumerating_it(self) -> None:
        self._assert_gitignore_covers(".claude/future-tool-output.bin")

    def test_the_committed_project_settings_exception_stays_visible(self) -> None:
        """The tracked-file walk below is vacuous until this file is committed.

        This direct assertion holds the forward-looking negation before then;
        once the file exists, ``TheNetDoesNotSwallowWhatIsCommitted`` holds it
        again as part of the repository's complete tracked population.
        """
        self.assertFalse(_check_ignore(".claude/settings.json"))


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
            "guidelines-index/ holds the index and recommendation records, and .gitignore misses it",
        )

    def test_a_recommendation_record(self) -> None:
        """The producer guarantees the ``recs-`` prefix on every JSON it writes."""
        name = f"{guidelines_recs.RECS_PREFIX}some-guideline.json"
        self.assertTrue(
            _check_ignore(name),
            "a recommendation record holds the society's text in full and is not ignored",
        )
        self.assertTrue(
            _check_ignore(f"reference/{name}"),
            "the pattern must reach a subdirectory, which is where a mis-typed --json lands",
        )


class TheTransientBuildArtifactsAreIgnored(unittest.TestCase):
    """[#302]: a crashed atomic build must not leave a committable sibling.

    ``docx_write`` exposes ``partial_name``, so that producer's full transient
    name is derived here. ``guidelines_index`` constructs its sibling inside
    ``build`` and exposes no naming helper; its ``.building`` name has to be
    restated. The shared suffix is the public convention this ignore net covers.
    """

    def test_a_docx_partial_derived_from_the_producer(self) -> None:
        partial = docx_write.partial_name(Path("reference/paper.docx"))
        self.assertTrue(
            _check_ignore(partial.as_posix()),
            f"{partial} is docx_write's partial archive and .gitignore does not cover it",
        )

    def test_the_guideline_index_partial_the_producer_does_not_expose(self) -> None:
        self.assertTrue(
            _check_ignore("tools/guidelines.sqlite.building"),
            "guidelines_index's partial database is not covered by .gitignore",
        )


class TheNetDoesNotSwallowWhatIsCommitted(unittest.TestCase):
    """A pattern wide enough to hide a tracked file is worse than the gap.

    ``reference/icd10cm-2026.sqlite`` is committed deliberately, and an index
    landing anywhere is a build artifact -- so this is the boundary a bare
    ``*.sqlite`` rule would cross, and the reason there is not one.
    """

    def test_every_tracked_file_is_still_visible(self) -> None:
        """No **tracked** file is hidden by ``.gitignore``, and that is the whole claim.

        [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254)
        names this walk beside two others as reporting a clean result about a
        tree it cannot fully see. **It is the one of the three that is already
        honest in its name**, and worth saying why rather than leaving the
        reader to re-derive it: the subject is files git is carrying, so
        ``--cached`` is the population and not a sample of it.

        **Widening it is a tautology rather than a stronger check.**
        ``--others --exclude-standard`` means *untracked and not ignored*, so
        every path it added would pass this assertion by definition. There is
        no version of this test that sees more by seeing untracked files.
        """
        tracked = git_paths.read_path_records(
            REPO_ROOT, "ls-files", "--cached", "-z"
        )
        self.assertGreater(len(tracked), 100, "git ls-files returned too little to be a checkout")
        ignored_set = _ignored(tracked)
        ignored = [path for path in tracked if path in ignored_set]
        self.assertEqual(
            ignored,
            [],
            "these files are tracked and .gitignore now hides them: " + ", ".join(ignored),
        )


if __name__ == "__main__":
    unittest.main()
