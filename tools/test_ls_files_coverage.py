"""Every ``git ls-files`` walk in ``tools/`` says what a clean result covers.

[#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254). Found
on [#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240)'s
branch: ``tools/checks_ledger.py`` landed with two ``step N`` citations naming no
skill beside them, ``test_every_citation_in_tools_resolves`` was on the base and
exists to refuse exactly that, and the branch ran the suite three times at
**1788 tests, OK**. The failure appeared only after ``git add``, and a review
agent found it rather than the suite.

**A green run over a new module is a run that never opened it.** The walk is
``git ls-files``, an untracked file is not in it, and the interval in which a new
tool is written is exactly the interval it is invisible for.

## The ruling this implements

#254 offered three answers and the clinician ruled the third on 2026-08-19:
**change nothing about the window, and make the walks state what they cover.**
Not because the window is harmless -- it is where the repair would have been
cheapest -- but because CI catches it at push and the next local run catches it
after the stage, and what it cost was one review cycle.

**The cost of the answer it did not take is measured rather than left open**,
because #254 says nobody had priced it: ``git ls-files --others
--exclude-standard -- '*.md' '*.py'`` returns **0** in the main checkout and in
every worktree ``git worktree list`` reports beside it, on 2026-08-19. The
ignore lines already absorb where working files land, so widening the walk
would have cost no noise at rest. That is recorded because it is the figure the
ruling was made against, and it is deliberately not restated anywhere else.

**A first draft counted 31 and the registry reports seven**, the difference
being stale directories under ``.claude/worktrees/`` that no longer answer to
``git worktree``. Neither number is the finding -- **zero is** -- and the count
of trees it was taken over is not stated for that reason. It is named because a
figure taken over the wrong haystack reads exactly like one taken over the
right one, which is this repo's standing complaint about its own measurements.

**So the deliverable is the honest form**: a clean result from a walk of the
index means *no tracked file fails*, and it never meant *no file fails*. That is
what this module requires every walk to carry, and requiring it is the
difference between a ruling and a comment -- ``CLAUDE.md`` records #220's lesson
that **a prose edit to a claim fails nothing**, so a statement nothing re-derives
is one nobody keeps true.

## The ticket named three walks and the AST finds more

#254's general form is *every check in ``tools/`` that walks ``git ls-files``
inherits this*, and its worked list is three test modules. The AST found **five**
on 2026-08-19 -- dated, with the floor in a test below rather than restated, on
``test_console_codec.py``'s terms. The two it adds are the ones that are not
tests:

- ``phi_scan.scan_all`` -- standing rule 1's ``--all`` mode, which CI runs, and
  which had no docstring at all.
- ``spelling_scan.tracked_markdown`` -- standing rule 4's ``--all`` mode. Its
  **name** carried the qualifier and nothing else did, and ``CLAUDE.md`` already
  records the instance: ``licence`` landed in a skill file because the staged
  scan had crashed and *"``--all`` walks ``git ls-files``, so it cannot see a
  file until the commit that makes it tracked"*.

That is #254's own thesis on #254 -- a list assembled from the files a pass had
open, which is
[#137](https://github.com/mshamblin5150-code/clinical-skills/issues/137) -- and
it is why the check is an AST walk rather than the three edits the ticket asked
for.

## Mention against use, and it is load-bearing here

A substring search for ``ls-files`` over ``tools/`` returns **far more** lines
than there are walks, and the rest are the rule being *described*:
``phi_scan.py``'s comment about what ``--all`` cannot reach, the
``"git ls-files returned too little to be a checkout"`` assertion messages, and
``test_run_record_claim.py``'s docstring recounting the round it shipped red.
Every one of them would satisfy a text check while proving nothing, and
``phi_scan.py``'s comment would have exempted the walk above it by explaining
it. **No line distance is stated and a draft stated one** -- it read *twelve*,
measured against nothing, and the walk and the comment are three dozen lines
apart. A number nobody re-derives is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) whether
or not it happens to be right, and here it was not.

**No ratio is stated, and the draft of this paragraph stated one.** It read
*ten lines, five of them walks*, measured before the commit that wrote it -- and
the same commit's docstrings pushed it past thirty, because a paragraph
explaining the rule contains the string the rule is keyed on. That is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) and
[#180](https://github.com/mshamblin5150-code/clinical-skills/issues/180) arriving
inside the change that cites both, which ``CLAUDE.md`` records happening three
times already. The count of walks is a floor in a test below; the count of
mentions is nobody's, and it moves with every paragraph anybody writes.

That is ``test_console_codec.py``'s instrument adopted for its reason -- the
first version of *that* walk was a substring search and ``console_codec.py``
passed it on the usage example in its own docstring. So a walk here is an
``ast.Call`` carrying the constant ``"ls-files"`` as a whole argument, which
catches both spellings this repo writes (``subprocess.run(["git", "ls-files",
...])`` and ``_git("ls-files", ...)``) and no prose at all.

## What this cannot reach

**Whether the statement is true.** A docstring saying *tracked* and *untracked*
over a walk that has since been widened to ``--others`` passes, and so would one
whose two limbs sit in unrelated sentences. The vocabulary is a floor on *having
addressed it*, not a reading of what was said -- ``test_skill_agreement.py``'s
argument that asserting a paragraph verbatim teaches the next session to delete
the check.

**A walk built by indirection.** The predicate reads one call and never leaves
it, so a module-level ``CMD = ["git", "ls-files"]`` passed as
``subprocess.run(CMD)``, or a command concatenated at run time, is invisible.
Both spellings this repo actually writes are caught, and the keyword form is
caught since a review found it was not -- but **this is a floor on the shapes
in the tree, not a proof that a sixth walk cannot arrive quietly**, and the
stronger sentence was written into ``CLAUDE.md`` before a review caught it.

**And it does not close the window.** That was the ruling. A new module written
this session is still invisible to every walk above until it is staged, this one
included -- which is the joke #254 is entitled to: **this module was untracked
while it was being written, so the walk below could not see itself either.**
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

# The git subcommand, as a whole argument. Not a substring of a sentence about
# it -- see *Mention against use* above.
SUBCOMMAND = "ls-files"

# Limb one: what the clean result covers. ``\b`` does the work on its own --
# there is no word boundary between the ``un`` and the ``tracked`` of
# ``untracked``, so a docstring naming only the blind spot does not satisfy
# this. Asserted below rather than trusted, because the whole vocabulary rests
# on it.
COVERS_TRACKED = re.compile(r"\btracked\b", re.IGNORECASE)

# Limb two: what it cannot see. Both limbs are required, because either alone
# reads as complete -- ``tracked`` alone is what ``tracked_markdown``'s name
# already said, and ``untracked`` alone never says what a pass means.
NAMES_THE_BLIND_SPOT = re.compile(
    r"\b(untracked|unstaged|not yet staged|not staged|never staged)\b",
    re.IGNORECASE,
)


def _is_subcommand(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value == SUBCOMMAND


def passes_subcommand(call: ast.Call) -> bool:
    """``ls-files`` as a whole argument, directly or inside a sequence literal.

    A whole argument and never a substring: ``"git ls-files returned too little
    to be a checkout"`` is an assertion message in three modules here, and a
    substring rule would grade all three as walks.

    Keywords are read as well as positionals, so ``subprocess.run(args=[...])``
    is seen. **What stays out of reach is indirection**: a module-level
    ``CMD = ["git", "ls-files"]`` passed as ``subprocess.run(CMD)`` is invisible
    to a walk that never leaves the call, and so is a concatenation built at run
    time. That is named in *What this cannot reach* rather than left to a reader
    to discover, because the ceiling of an AST predicate is a fact about it.
    """
    supplied = list(call.args) + [keyword.value for keyword in call.keywords]
    for argument in supplied:
        if _is_subcommand(argument):
            return True
        if isinstance(argument, (ast.List, ast.Tuple, ast.Set)):
            if any(_is_subcommand(element) for element in argument.elts):
                return True
        if isinstance(argument, ast.BinOp) and isinstance(argument.op, ast.Add):
            for side in (argument.left, argument.right):
                if isinstance(side, (ast.List, ast.Tuple)) and any(
                    _is_subcommand(element) for element in side.elts
                ):
                    return True
    return False


def walks(source: str) -> list[tuple[int, str | None]]:
    """Every ``git ls-files`` call in one module, with its function's docstring.

    The line number and the **innermost enclosing function's** docstring, or
    ``None`` where the walk sits outside a function or in one with no docstring
    at all. Innermost, and not the class or the module, deliberately: a
    statement one scroll away from the walk is one the next author moves the
    walk out from under, and a module docstring would let a single mention vouch
    for every walk in the file.
    """
    found: list[tuple[int, str | None]] = []

    def visit(node: ast.AST, holder: ast.AST | None) -> None:
        if isinstance(node, ast.Call) and passes_subcommand(node):
            found.append((node.lineno, ast.get_docstring(holder) if holder else None))
        nearest = (
            node
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            else holder
        )
        for child in ast.iter_child_nodes(node):
            visit(child, nearest)

    visit(ast.parse(source), None)
    return sorted(found)


def states_coverage(doc: str | None) -> bool:
    """Both limbs, in the docstring that holds the walk.

    **A seam rather than an inlined condition, and it is here because the
    inlined version was untestable.** ``TheInstrumentIsLive`` drove ``walks``
    and the two regexes and never this decision, so ``uncovered`` returning a
    bare ``[]`` survived the whole module -- and so did dropping either
    conjunct, which is the module's own *both limbs are required* claim
    enforced nowhere. Found by ``/code-review`` mutating it, which is this
    repo's shape arriving inside the instrument built to refuse it.
    """
    text = doc or ""
    return bool(COVERS_TRACKED.search(text) and NAMES_THE_BLIND_SPOT.search(text))


def grade(sources: dict[str, str]) -> list[str]:
    """``name:line`` for every walk in ``sources`` whose function stays silent.

    Takes the text rather than reading the tree, so the tree-wide walk below and
    the synthetic cases in ``TheInstrumentIsLive`` go through the same code. A
    grader the live tests cannot reach is one a mutation walks straight past.
    """
    return [
        f"{name}:{line}"
        for name, source in sorted(sources.items())
        for line, doc in walks(source)
        if not states_coverage(doc)
    ]


def modules() -> list[Path]:
    return sorted(TOOLS.glob("*.py"))


def tree_sources() -> dict[str, str]:
    """Every module in ``tools/``, by name, as text.

    **The only thing between the tree and ``grade``, and it is separate so that
    nothing between them is untested.** A convenience wrapper reading the tree
    and grading it in one step was written first and then removed: mutating it
    to return nothing survived the whole module, because the synthetic tests
    drove ``grade`` and the tree-wide test drove the wrapper, and neither
    reached the other. ``TheInstrumentIsLive`` asserts this is populated;
    ``EveryWalkStatesItsCoverage`` calls ``grade`` on it directly.
    """
    return {path.name: path.read_text(encoding="utf-8") for path in modules()}


COMPLIANT = '''
def tracked_prose():
    """Tracked files only, so an untracked one is invisible until it is staged."""
    return subprocess.run(["git", "ls-files", "--cached"])
'''

BARE = '''
def tracked_prose():
    return subprocess.run(["git", "ls-files", "--cached"])
'''

TRACKED_ONLY = '''
def tracked_prose():
    """Every tracked file in the checkout."""
    return subprocess.run(["git", "ls-files", "--cached"])
'''

BLIND_SPOT_ONLY = '''
def tracked_prose():
    """An untracked file is not in it."""
    return subprocess.run(["git", "ls-files", "--cached"])
'''

HELPER_SPELLING = '''
def tracked_markdown():
    """Tracked Markdown. An untracked file is not in it."""
    return _git("ls-files", "*.md")
'''

KEYWORD_SPELLING = '''
def tracked_prose():
    return subprocess.run(args=["git", "ls-files", "--cached"])
'''

NESTED = '''
def outer():
    """Tracked files, and an untracked one is invisible."""
    def inner():
        return subprocess.run(["git", "ls-files"])
    return inner
'''

PROSE_ONLY = '''
# `--all` walks `git ls-files`, so it cannot see an untracked file.
def unrelated():
    """A module that never walks the index at all."""
    self.assertGreater(len(paths), 50, "git ls-files returned too little to be a checkout")
'''


class TheInstrumentIsLive(unittest.TestCase):
    """A predicate that matched nothing would pass every assertion below."""

    def test_a_bare_walk_is_caught(self) -> None:
        self.assertEqual([line for line, _ in walks(BARE)], [3])
        self.assertIsNone(walks(BARE)[0][1])

    def test_a_stated_walk_clears_it(self) -> None:
        line, doc = walks(COMPLIANT)[0]
        self.assertEqual(line, 4)
        self.assertTrue(COVERS_TRACKED.search(doc))
        self.assertTrue(NAMES_THE_BLIND_SPOT.search(doc))

    def test_untracked_alone_does_not_satisfy_the_tracked_limb(self) -> None:
        r"""The whole vocabulary rests on ``\b`` splitting these two words.

        There is no word boundary between the ``un`` and the ``tracked`` of
        ``untracked``, so a docstring naming only the blind spot fails limb one.
        Asserted rather than reasoned about: if it were wrong, every
        half-written statement would pass.
        """
        _, doc = walks(BLIND_SPOT_ONLY)[0]
        self.assertTrue(NAMES_THE_BLIND_SPOT.search(doc))
        self.assertIsNone(COVERS_TRACKED.search(doc))

    def test_tracked_alone_does_not_satisfy_the_blind_spot_limb(self) -> None:
        """``tracked_markdown``'s name said this much and said nothing about a pass."""
        _, doc = walks(TRACKED_ONLY)[0]
        self.assertTrue(COVERS_TRACKED.search(doc))
        self.assertIsNone(NAMES_THE_BLIND_SPOT.search(doc))

    def test_the_helper_spelling_is_a_walk_too(self) -> None:
        """``_git("ls-files", "*.md")`` passes the subcommand as a bare argument."""
        self.assertEqual([line for line, _ in walks(HELPER_SPELLING)], [4])

    def test_a_nested_function_answers_for_its_own_walk(self) -> None:
        """The innermost holder, so an outer statement cannot vouch for an inner walk."""
        self.assertEqual(walks(NESTED), [(5, None)])

    def test_a_bare_walk_is_reported_by_the_grader(self) -> None:
        """``uncovered`` is the function the tree-wide test asserts on.

        It went untested for one round: ``uncovered`` returning a bare ``[]``
        survived every assertion in this class, because the class drove
        ``walks`` and the regexes and never the decision between them.
        """
        self.assertEqual(grade({"bare.py": BARE}), ["bare.py:3"])

    def test_a_stated_walk_is_not_reported_by_the_grader(self) -> None:
        self.assertEqual(grade({"ok.py": COMPLIANT}), [])

    def test_the_grader_requires_both_limbs(self) -> None:
        """The module's own claim, enforced. Dropping either conjunct survived.

        Each half alone reads as a statement and neither is one: *tracked* alone
        is what a name already said, and *untracked* alone never says what a
        pass means.
        """
        self.assertEqual(grade({"half.py": TRACKED_ONLY}), ["half.py:4"])
        self.assertEqual(grade({"other.py": BLIND_SPOT_ONLY}), ["other.py:4"])
        self.assertFalse(states_coverage(None))

    def test_the_keyword_spelling_is_a_walk_too(self) -> None:
        """``subprocess.run(args=[...])`` is a walk, and was invisible for one round."""
        self.assertEqual(grade({"kw.py": KEYWORD_SPELLING}), ["kw.py:3"])

    def test_prose_about_the_rule_is_not_a_walk(self) -> None:
        """The failure this instrument exists to refuse, and it has live cases.

        A comment about what ``--all`` cannot reach, and an assertion message
        carrying the words ``git ls-files``. A substring check would read both as
        walks -- and would let ``phi_scan.py``'s comment vouch for the walk
        above it. **How many such lines there are is deliberately
        not counted**: every paragraph explaining this rule adds one, this
        docstring included.
        """
        self.assertEqual(walks(PROSE_ONLY), [])


class EveryWalkStatesItsCoverage(unittest.TestCase):
    """#254's honest form, mechanically. ``CLAUDE.md`` records why it is not prose."""

    def test_the_walk_still_finds_walks_to_check(self) -> None:
        """A glob or a predicate that quietly matched nothing passes the next test.

        **Five as of 2026-08-19**, and the floor is deliberately below it on
        ``test_console_codec.py``'s terms: this is here to catch the predicate
        breaking, not to be a second place a count has to be kept true.
        """
        found = [
            f"{name}:{line}"
            for name, source in tree_sources().items()
            for line, _ in walks(source)
        ]
        self.assertGreaterEqual(len(found), 5, f"only found {found}")

    def test_the_walk_reaches_the_two_production_scanners(self) -> None:
        """The two #254 did not name, and the reason the check is an AST walk.

        Named rather than counted: the floor above would still pass if the
        predicate silently stopped seeing the ``_git("ls-files")`` spelling,
        which is the one both of these use and no test module uses.
        """
        walked = {name for name, source in tree_sources().items() if walks(source)}
        self.assertIn("phi_scan.py", walked)
        self.assertIn("spelling_scan.py", walked)

    def test_the_tree_is_actually_read(self) -> None:
        """``grade`` is only as live as what is handed to it.

        The wrapper this replaced could be mutated to return nothing and every
        assertion in the module stayed green, which is the same vacuous-pass
        shape the class above exists for -- one layer further out.
        """
        sources = tree_sources()
        self.assertGreaterEqual(len(sources), 20)
        self.assertIn("phi_scan.py", sources)
        self.assertIn("def scan_all", sources["phi_scan.py"])

    def test_every_walk_says_what_a_clean_result_covers(self) -> None:
        missing = grade(tree_sources())
        self.assertEqual(
            missing,
            [],
            "these walk the index and their function does not say a clean result "
            "means 'no tracked file fails': " + ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main()
