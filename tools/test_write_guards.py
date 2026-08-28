"""The write guards agree, and nobody has written a fifth rule -- issue #176.

Three modules held three answers to *is this path inside a git checkout*, under
three names, with two exception types, and one of the three detection rules was
weaker than the other two. A fourth arrived after the ticket was filed and chose
none of them. ``repo_root.enclosing_checkout`` is the one rule now, and
``test_repo_root.py`` grades the rule itself.

**This file grades the thing sharing the rule does not fix.** #218's counter-
instance to this ticket is the reason it exists: when ``reference_scan`` was made
to import ``docx_write.REFERENCE_HEADING`` rather than restate it, an identity
test asserted the two were the same object and passed -- and a *behavioral* test
driving both then found they still disagreed about where a reference list ends.
Sharing the object was necessary and not sufficient. So the first class here
drives the call sites, each through its own entry point, and asserts they reach
the same verdict about the same paths.

``TheRuleLivesInOnePlace`` is the parity instrument the ticket's scope names as
optional (*"if that is judged worth doing"*), keyed on what the ticket is
actually about: not that every writer takes a guard, but that nobody
re-implements the rule.

**And the divergences that survive are intentional rather than discovered.**
They include a module that blesses a directory inside a checkout, one that returns a
reason string instead of raising, and the command lines do not agree on the exit
status a refusal produces. #303 ruled that each command keeps the status its own
boundary gives the refusal. Each is argued where it lives; this file is where a
reader finds out they exist.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import guidelines_extract
import guidelines_index
import artifact_provenance
import docx_write
import guidelines_recs
import name_index
import voice_corpus
import repo_root
import threshold_sheet
from repo_root import InsideCheckout

TOOLS = Path(__file__).resolve().parent

# The one module allowed to know how a checkout is recognized.
RULE_HOLDER = "repo_root.py"

# The marker the rule is keyed on. Held here rather than spelled inline in the
# predicate so this module can explain itself without the check tripping over its
# own explanation -- ``spelling_scan.py``'s mention-versus-use problem, which has
# broken the thing doing the checking three times in this repo.
GIT_MARKER = ".git"

# What a run that got *past* the guard says instead of refusing. Named so an
# adapter can tell "the guard allowed this" from "the run died before reaching
# the guard" -- without it a False verdict means either, and an allow assertion
# would pass for the wrong reason on a machine with no PDF library.
PAST_THE_GUARD = ("no PDFs under", "pymupdf")


def module_sources() -> list[Path]:
    """Every non-test module in ``tools/``.

    Test modules are out of scope, and that is a real exclusion rather than a
    convenience: a test that builds a fake checkout has to create the marker, and
    ``test_repo_root.py`` and this file both do. What the ticket is about is a
    *tool* deciding for itself what a checkout looks like.
    """
    return sorted(
        path for path in TOOLS.glob("*.py") if not path.name.startswith("test_")
    )


def names_the_marker(source: str) -> bool:
    """Whether this module's source contains the marker as a literal.

    By AST rather than by substring, on ``test_console_codec.py``'s instrument and
    for its reason: every paragraph explaining this rule contains the string the
    rule is keyed on, and a text search cannot tell a comment about the rule from
    the rule. ``repo_root``'s own docstring names it several times.
    """
    return any(
        isinstance(node, ast.Constant) and node.value == GIT_MARKER
        for node in ast.walk(ast.parse(source))
    )


def imported_from_repo_root(source: str) -> set[str]:
    return {
        alias.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module == "repo_root"
        for alias in node.names
    }


class Checkout:
    """A throwaway tree holding a plain clone, a worktree and two innocents."""

    def __init__(self, case: unittest.TestCase) -> None:
        tmp = tempfile.TemporaryDirectory()
        case.addCleanup(tmp.cleanup)
        self.case = case
        self.root = Path(tmp.name).resolve()

        self.clone = self.root / "clinical_skills"
        (self.clone / ".git").mkdir(parents=True)

        # A worktree's .git is a *file*. Each of the copies had to get that right
        # on its own, and the known-roots rule could not see this tree at all.
        self.worktree = self.root / "sibling-worktree"
        self.worktree.mkdir()
        pointer = (self.clone / ".git").as_posix() + "/worktrees/x"
        (self.worktree / ".git").write_text("gitdir: " + pointer + "\n", encoding="utf-8")

        self.source = self.root / "guidelines-src"
        self.source.mkdir()
        self.text_dir = self.root / "guidelines-text"
        self.text_dir.mkdir()
        (self.text_dir / "IDSA-uti.txt").write_text("a page\n", encoding="utf-8")
        self.producer = artifact_provenance.current_producer()
        self.producer["dirty"] = False
        self.producer["inputs"] = artifact_provenance.producer_file_identity(
            artifact_provenance.TRUST_FLOOR["extraction"]
        )
        (self.text_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "producer": self.producer,
                    "documents": [{"doc_id": "IDSA-uti"}],
                }
            ),
            encoding="utf-8",
        )

    def _allowed(self, message: str) -> bool:
        """A verdict of *not refused* has to be earned, never inferred from silence.

        The two command lines both exit non-zero on the allow path -- one for
        having no PDFs, one for having no PDF library -- so an adapter that read
        any non-refusal as *allowed* would report the same thing for a run that
        died before the guard was ever consulted. Anything unrecognized fails
        loudly instead.
        """
        self.case.assertTrue(
            any(marker in message for marker in PAST_THE_GUARD),
            "neither a refusal nor a recognized post-guard outcome: " + message,
        )
        return False

    def refused_by_extract(self, target: Path) -> bool:
        try:
            guidelines_extract.main([str(self.source), "--out", str(target)])
        except SystemExit as stop:
            message = str(stop)
            return True if "git checkout" in message else self._allowed(message)
        raise AssertionError("guidelines_extract.main returned on an empty source")

    def refused_by_index(self, target: Path) -> bool:
        try:
            with mock.patch.object(
                artifact_provenance,
                "current_producer",
                return_value=self.producer,
            ):
                guidelines_index.build(self.text_dir, target / "guidelines.sqlite")
        except InsideCheckout:
            return True
        return False

    def refused_by_recs(self, target: Path) -> bool:
        stderr = io.StringIO()
        try:
            with contextlib.redirect_stderr(stderr):
                status = guidelines_recs.main(
                    [str(self.root / "absent.pdf"), "--json", str(target / "recs-x.json")]
                )
        except SystemExit as stop:
            return "git checkout" in str(stop)
        # Earned rather than inferred, on `_allowed`'s reasoning: the allow path
        # reaches the *next* check and reports 2 for the absent PDF.
        self.case.assertEqual(status, 2, "recs did not reach its input check")
        return False

    def refused_by_name_index(self, target: Path) -> bool:
        return name_index.refuse_target(target / "name-index.json") is not None

    def refused_by_voice_corpus(self, target: Path) -> bool:
        return voice_corpus.refuse_target(target / "mined.md") is not None

    def verdicts(self, target: Path) -> dict[str, bool]:
        return {
            "guidelines_extract": self.refused_by_extract(target),
            "guidelines_index": self.refused_by_index(target),
            "guidelines_recs": self.refused_by_recs(target),
            "name_index": self.refused_by_name_index(target),
            "voice_corpus": self.refused_by_voice_corpus(target),
        }

    def refused_by_docx(self, target: Path) -> bool:
        source = self.root / "case.md"
        source.write_text("# Case\n", encoding="utf-8")
        stderr = io.StringIO()
        with mock.patch.object(repo_root, "main_repo_root", return_value=self.clone):
            with contextlib.redirect_stderr(stderr):
                status = docx_write.main([str(source), str(target / "case.docx")])
        if status == 2 and "foreign checkout" in stderr.getvalue():
            return True
        self.case.assertEqual(status, 0, "docx writer did not reach the allow path")
        return False


class EveryWriteSiteReachesTheSameVerdict(unittest.TestCase):
    """Driven through each site's own entry point, never through the helper.

    Calling ``ensure_outside_checkout`` several times and comparing would prove
    only that a function equals itself. What can still go wrong after the
    extraction is a caller consulting the guard on a path other than the one it
    writes, or after it has already written -- which is exactly the class of
    divergence #218's behavioral cross-check found and its identity test could
    not.
    """

    def setUp(self):
        self.tree = Checkout(self)

    def assert_all(self, target: Path, expected: bool):
        verdicts = self.tree.verdicts(target)
        self.assertEqual(
            verdicts,
            dict.fromkeys(verdicts, expected),
            "the write sites disagree about " + str(target),
        )

    def test_a_path_inside_a_plain_clone_is_refused_everywhere(self):
        self.assert_all(self.tree.clone / "reference", True)

    def test_a_path_inside_a_sibling_worktree_is_refused_everywhere(self):
        """The case the weaker rule could not see. ``guidelines_index`` compared
        against this worktree and the clone that owns it, so a *sibling* worktree
        -- the ordinary shape under ``.claude/worktrees/`` -- was outside its
        vocabulary entirely."""
        self.assert_all(self.tree.worktree / "guidelines-text", True)

    def test_a_sibling_of_the_clone_is_allowed_everywhere(self):
        self.assert_all(self.tree.root / "guidelines-index", False)

    def test_a_path_that_only_shares_a_name_prefix_is_allowed_everywhere(self):
        """``clinical_skills-notes`` is not inside ``clinical_skills``. The rule
        the extraction kept had to keep this property, which the known-roots one
        was explicitly careful about."""
        self.assert_all(self.tree.root / "clinical_skills-notes", False)

    def test_a_directory_under_no_checkout_at_all_is_allowed_everywhere(self):
        self.assert_all(self.tree.root / "elsewhere", False)


class TheOutputSiteReachesTheOppositeVerdict(unittest.TestCase):
    """The submission writer permits only the main checkout, plus external exports."""

    def setUp(self):
        self.tree = Checkout(self)

    def test_the_main_checkout_is_allowed(self):
        self.assertFalse(self.tree.refused_by_docx(self.tree.clone / "output"))

    def test_a_sibling_worktree_is_refused(self):
        self.assertTrue(self.tree.refused_by_docx(self.tree.worktree / "output"))

    def test_a_sibling_of_the_clone_is_allowed(self):
        self.assertFalse(self.tree.refused_by_docx(self.tree.root / "guidelines-index"))

    def test_a_name_prefix_is_not_the_main_checkout(self):
        self.assertFalse(
            self.tree.refused_by_docx(self.tree.root / "clinical_skills-notes")
        )

    def test_a_directory_under_no_checkout_is_allowed(self):
        self.assertFalse(self.tree.refused_by_docx(self.tree.root / "elsewhere"))


class TheIntentionalDivergences(unittest.TestCase):
    """What the consolidation deliberately did not make uniform, said out loud.

    #303 kept each command's existing status because the status belongs to the
    command's run contract, not to the shared library refusal. Declared here so
    a reader of *one rule for every writer* is corrected by a test rather than
    by a surprise, and so widening any of the three has to answer for it in a
    diff.
    """

    def setUp(self):
        self.tree = Checkout(self)

    def test_two_sites_permit_the_repos_own_scratch(self):
        """The parameter a shared rule needed and a single rule could not have.

        The index is a list of patient names and a mined voice record is the
        clinician's own writing out of a corpus that carries patient material:
        under ``scratch/`` both are gitignored and ``phi_scan``'s path layer
        refuses a commit from them even under ``git add -f``, which is a stronger
        net than being outside the tree.

        **This read *one* site until #388 added the second**, and the sentence was
        the stale half rather than the code -- a fifth write site joined the tree
        while this class still described four, which is the
        [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
        shape the parity tests exist to refuse.
        """
        scratch = self.tree.clone / "scratch"
        self.assertIsNone(
            name_index.refuse_target(scratch / "name-index.json", scratch=scratch)
        )
        self.assertIsNone(
            voice_corpus.refuse_target(scratch / "mined.md", scratch=scratch)
        )

    def test_the_other_sites_have_no_such_permission(self):
        """And that is right: a build artifact and a society's copyrighted text
        are not patient records, and ``scratch/`` is the corpus rather than a
        spare directory."""
        scratch = self.tree.clone / "scratch"
        self.assertTrue(self.tree.refused_by_extract(scratch))
        self.assertTrue(self.tree.refused_by_index(scratch))
        self.assertTrue(self.tree.refused_by_recs(scratch))

    def test_one_site_returns_a_reason_and_raises_nothing(self):
        """``name_index`` is the third refusal convention #141's comment named,
        and it survived the consolidation deliberately: *a refused write is not a
        refused scan*. The run read the whole corpus and knows exactly how short
        the index is, so the refusal is a note beside that finding rather than
        instead of it -- ``differential_scan``'s ordering."""
        reason = name_index.refuse_target(self.tree.clone / "name-index.json")
        self.assertIsInstance(reason, str)
        self.assertIn("checkout", reason)

    def test_each_command_keeps_its_own_exit_status(self):
        """**A shared refusal does not imply a shared command status.**
        ``guidelines_extract`` and ``guidelines_recs`` convert the
        refusal to ``SystemExit``, which is 1; ``guidelines_index`` lets it reach
        ``main``'s existing ``ValueError`` handler, which returns 2 on this
        command's *did not scan* convention. #303 ruled the divergence
        intentional: exit status is part of each command's run contract, and
        other consumers already show that one shared refusal naturally reaches
        different command boundaries differently. ``name_index`` remains the
        explicit exception to any convergence because its status 1 reports the
        shortfall the completed scan found, not the refused write by itself.
        """
        inside = self.tree.clone / "reference"

        # A ``SystemExit`` carrying a string prints it and exits **1** -- which is
        # what both of these produce, and is checkable here without a subprocess.
        with self.assertRaises(SystemExit) as extract_stop:
            guidelines_extract.main([str(self.tree.source), "--out", str(inside)])
        self.assertIsInstance(extract_stop.exception.code, str)

        with self.assertRaises(SystemExit) as recs_stop:
            with contextlib.redirect_stderr(io.StringIO()):
                guidelines_recs.main(
                    [str(self.tree.root / "absent.pdf"), "--json", str(inside / "recs-x.json")]
                )
        self.assertIsInstance(recs_stop.exception.code, str)

        with contextlib.redirect_stderr(io.StringIO()):
            status = guidelines_index.main(
                [str(self.tree.text_dir), str(inside / "guidelines.sqlite")]
            )
        self.assertEqual(status, 2)


class TheRefusalWinsOverTheInputCheck(unittest.TestCase):
    """``guidelines_recs`` decides where the JSON may land before it looks at the PDF.

    That ordering changed on #176 and it changes an exit status, so it is pinned
    rather than left to be noticed. Two arguments for it, neither of which is the
    cross-check: a run that reads a document and *then* refuses to write it has
    spent the expensive half for nothing, and the document it read is the
    society's copyrighted expression. Where the output goes is a question about
    the arguments alone, so it is answered first -- which means an unusable
    ``--json`` beats an absent PDF, and the status is the refusal's 1 rather than
    the input check's 2.
    """

    def setUp(self):
        self.tree = Checkout(self)

    def test_an_unusable_json_path_beats_an_absent_pdf(self):
        with self.assertRaises(SystemExit) as stop:
            with contextlib.redirect_stderr(io.StringIO()):
                guidelines_recs.main(
                    [
                        str(self.tree.root / "absent.pdf"),
                        "--json",
                        str(self.tree.clone / "recs-x.json"),
                    ]
                )
        self.assertIn("git checkout", str(stop.exception))

    def test_a_nonconforming_json_stem_beats_an_absent_pdf(self):
        with self.assertRaises(SystemExit) as stop:
            guidelines_recs.main(
                [
                    str(self.tree.root / "absent.pdf"),
                    "--json",
                    str(self.tree.root / "verify-recs.json"),
                ]
            )
        self.assertIn("must start with 'recs-'", str(stop.exception))

    def test_a_conforming_json_stem_reaches_the_existing_input_check(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = guidelines_recs.main(
                [
                    str(self.tree.root / "absent.pdf"),
                    "--json",
                    str(self.tree.root / f"{guidelines_recs.RECS_PREFIX}x.json"),
                ]
            )
        self.assertEqual(status, 2)
        self.assertIn("not a file", stderr.getvalue())

    def test_an_absent_pdf_alone_is_still_two(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = guidelines_recs.main([str(self.tree.root / "absent.pdf")])
        self.assertEqual(status, 2)

    def test_extract_refuses_before_it_needs_a_pdf_library(self):
        """The same ordering one module over, and the only way to see it here.

        ``guidelines_extract`` asked where the output goes *after*
        ``require_pymupdf()``, so on a machine with no PDF library a path inside a
        checkout got the dependency error rather than the placement one. The
        maintainer's machine has the library, so no ordinary run can show the
        difference -- which is why the dependency is stubbed to fail rather than
        the ordering being asserted by reading the source.
        """
        def refuse():
            raise SystemExit("pymupdf is not installed.")

        original = guidelines_extract.require_pymupdf
        guidelines_extract.require_pymupdf = refuse
        self.addCleanup(setattr, guidelines_extract, "require_pymupdf", original)

        with self.assertRaises(SystemExit) as stop:
            guidelines_extract.main(
                [str(self.tree.source), "--out", str(self.tree.clone / "guidelines-text")]
            )
        self.assertIn("git checkout", str(stop.exception))

    def test_the_stub_is_live(self):
        """Without this the test above passes on a machine that has the library
        whatever the ordering is, which is the shape it was written to catch."""
        def refuse():
            raise SystemExit("pymupdf is not installed.")

        original = guidelines_extract.require_pymupdf
        guidelines_extract.require_pymupdf = refuse
        self.addCleanup(setattr, guidelines_extract, "require_pymupdf", original)

        with self.assertRaises(SystemExit) as stop:
            guidelines_extract.main(
                [str(self.tree.source), "--out", str(self.tree.root / "guidelines-text")]
            )
        self.assertIn("pymupdf", str(stop.exception))


class TheRuleLivesInOnePlace(unittest.TestCase):
    """No tool outside ``repo_root.py`` decides for itself what a checkout is.

    Keyed on re-implementation rather than on coverage, because that is what the
    ticket is about: three modules each spelling out the walk, one of them
    spelling it differently. A predicate over *who takes a guard* would have to
    guess which tools write, and the tree already shows that judgment is not
    mechanical -- ``guidelines_catalog.py`` gained 90 lines and correctly stayed
    guardless, because ``--draft`` goes to stdout.

    **What it cannot reach, named rather than left to be discovered.** A marker
    assembled by indirection -- a module-level constant, a concatenation, a name
    read from the environment -- is invisible to a predicate that looks for a
    literal. So is a guard that shells out to ``git rev-parse``. The honest claim
    is a floor on the shapes in the tree, never *a fifth rule cannot arrive
    quietly*. That is ``test_ls_files_coverage.py``'s ceiling, and #254 priced it
    in that module before this one inherited it.
    """

    def test_only_the_rule_holder_names_the_marker(self):
        offenders = [
            path.name
            for path in module_sources()
            if path.name != RULE_HOLDER
            and names_the_marker(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(
            offenders,
            [],
            "these modules decide for themselves what a git checkout looks like; "
            "import repo_root.enclosing_checkout instead: " + repr(offenders),
        )

    def test_the_rule_holder_does_name_it(self):
        """The exclusion has to be doing work. Without this the class passes just
        as well over a tree where nobody recognizes a checkout at all -- which is
        #254's third warning, that a grading function replaced by ``return []``
        left every assertion green."""
        source = (TOOLS / RULE_HOLDER).read_text(encoding="utf-8")
        self.assertTrue(names_the_marker(source))

    def test_the_population_is_not_empty(self):
        """A glob that matched nothing would report a clean tree it never read."""
        names = [path.name for path in module_sources()]
        self.assertIn(RULE_HOLDER, names)
        self.assertNotIn("test_write_guards.py", names)
        self.assertGreater(len(names), 20)

    def test_the_predicate_finds_a_planted_marker(self):
        planted = 'def guard(p):\n    return (p / "' + GIT_MARKER + '").exists()\n'
        self.assertTrue(names_the_marker(planted))

    def test_the_predicate_is_not_a_substring_search(self):
        """A module explaining the rule in a comment or a docstring is not a module
        implementing it. Every paragraph about this check contains the marker."""
        prose = '"""Walks up for a ' + GIT_MARKER + ' entry."""\n# and a ' + GIT_MARKER + ' comment\n'
        self.assertFalse(names_the_marker(prose))

    def test_the_predicate_ignores_a_marker_that_is_not_the_one(self):
        self.assertFalse(names_the_marker('x = ".gitignore"\n'))


class EveryWriteSiteImportsTheRule(unittest.TestCase):
    """The sites that need the rule are wired to it, and none holds a copy.

    **The list is typed, and that is a ceiling rather than coverage** -- the
    distinction ``test_build_artifacts_ignored.py`` records about its own third
    name, which went stale under a rename with the check green throughout. A
    new writer that took no guard at all is invisible here, and deriving the
    list is not available: the predicate would have to decide which tools write,
    which the class above explains is not mechanical. What catches another
    *rule* is that class; what this catches is a listed site being unwired.
    """

    WRITERS = {
        "guidelines_extract.py": "ensure_outside_checkout",
        "guidelines_index.py": "ensure_outside_checkout",
        "guidelines_recs.py": "ensure_outside_checkout",
        "name_index.py": "enclosing_checkout",
        "voice_corpus.py": "enclosing_checkout",
        "docx_write.py": "ensure_main_checkout",
    }

    def test_every_writer_imports_the_rule_from_repo_root(self):
        for module, expected in self.WRITERS.items():
            with self.subTest(module=module):
                source = (TOOLS / module).read_text(encoding="utf-8")
                self.assertIn(expected, imported_from_repo_root(source))

    def test_each_writer_states_its_own_reason(self):
        """The rule is shared and the sentence is not. One is protecting an
        artifact from being materialized into every worktree, one a society's
        copyrighted expression, one a list of patient names -- and a shared
        message would have had to say all three or none."""
        reasons = {
            guidelines_extract.WHY_OUTSIDE,
            guidelines_index.WHY_OUTSIDE,
            guidelines_recs.WHY_OUTSIDE,
        }
        self.assertEqual(len(reasons), 3)
        for reason in reasons:
            self.assertTrue(reason.strip())

    def test_the_helper_is_one_object_and_not_a_copy_per_caller(self):
        self.assertIs(
            guidelines_extract.ensure_outside_checkout, repo_root.ensure_outside_checkout
        )
        self.assertIs(
            guidelines_index.ensure_outside_checkout, repo_root.ensure_outside_checkout
        )
        self.assertIs(
            guidelines_recs.ensure_outside_checkout, repo_root.ensure_outside_checkout
        )
        self.assertIs(name_index.enclosing_checkout, repo_root.enclosing_checkout)
        self.assertIs(voice_corpus.enclosing_checkout, repo_root.enclosing_checkout)


class TheReaderTakesNoGuardAndSaysSo(unittest.TestCase):
    """``threshold_sheet.py`` is the fifth site, and its absent guard is a ruling.

    The ticket named it in the body -- *"its `--recs-root` default has to agree
    with the rule, which is a fourth place the convention is encoded"* -- and its
    first comment asked that the absence be settled rather than inherited:
    *"an absent guard is easy to read as an oversight when it is a choice."*

    The choice: this module only ever *reads* a ``recs-<key>.json``, and a write
    guard refuses a write. Guarding the read would refuse a record that already
    exists, which prevents nothing -- whatever put it there was the guarded step.
    What is enforceable is the one property of the default that is a fact about
    the convention rather than about the maintainer's machine.
    """

    def test_it_takes_no_write_guard(self):
        source = (TOOLS / "threshold_sheet.py").read_text(encoding="utf-8")
        self.assertNotIn("ensure_outside_checkout", imported_from_repo_root(source))

    def test_the_absence_is_declared(self):
        """A ruling nothing states is indistinguishable from an oversight, which
        is the whole of what the ticket's comment asked for."""
        self.assertIn("never writes one", threshold_sheet.WHY_NO_WRITE_GUARD)

    def test_the_recs_root_default_is_absolute(self):
        """A *relative* default resolves against the working directory, and the
        working directory when these tools are run is a checkout -- so a relative
        default is the convention encoded wrong, silently, in the one place the
        ticket named as encoding it without enforcing it.

        The *value* is deliberately not graded. It names a directory on the
        maintainer's machine, so asserting ``enclosing_checkout`` finds nothing
        above it would be asserting a fact about that machine: on a POSIX runner
        the drive-letter form resolves under the working directory and the check
        would fail for a reason that has nothing to do with the convention.
        """
        self.assertTrue(Path(threshold_sheet.DEFAULT_RECS_ROOT).is_absolute())

    def test_the_declaration_and_the_default_are_one_object_each(self):
        """Read off the module rather than restated here, on
        ``docx_write.NOT_APPLIED``'s precedent: a copy of either in this file
        could go out of step with the module and nothing would fail."""
        source = (TOOLS / "threshold_sheet.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        assigned = {
            target.id
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        self.assertIn("DEFAULT_RECS_ROOT", assigned)
        self.assertIn("WHY_NO_WRITE_GUARD", assigned)


if __name__ == "__main__":
    unittest.main()
