"""Contract checks for issue #412's prose assertion helper."""

import ast
import subprocess
from pathlib import Path
import unittest

from prose_bind import ProseBind


REPO_ROOT = Path(__file__).resolve().parent.parent
DECLARED_RAW_ASSERT_NOT_IN = {
    (
        "tools/test_skill_agreement.py",
        "until it lands this example is the only place the distinction is written down",
    ): "the exact staging marker is the retired artifact; paraphrases are outside the regression",
    (
        "tools/test_skill_agreement.py",
        "**declared rule** in ``reference/medatrax-fields.md``",
    ): "the exact Markdown address is retired, not every differently formatted discussion",
}


def raw_long_assert_not_in(source: str) -> set[str]:
    """Return long constant needles used as the proxy for prose haystacks."""

    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "assertNotIn" or not node.args:
            continue
        needle = node.args[0]
        if (
            isinstance(needle, ast.Constant)
            and isinstance(needle.value, str)
            and len(needle.value) >= 40
        ):
            found.add(needle.value)
    return found


def _tracked(root: Path, pathspec: str) -> list[str]:
    """Return tracked paths matching ``pathspec`` from the index.

    A clean walk means no tracked test module fails this check. Untracked or
    unstaged modules remain invisible until they enter the index.
    """

    result = subprocess.run(
        ["git", "ls-files", "--cached", "--", pathspec],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.splitlines()


def repository_survivors(root: Path) -> set[tuple[str, str]]:
    """Walk the silent direction conservatively over all tracked test modules.

    The ticket's required population is modules that read tracked Markdown.
    Proving that relation through imported readers or computed paths would need
    data-flow analysis, so this walk safely refuses every long raw guard. A
    non-Markdown guard can survive only by being declared with its reason.

    The 40-character cutoff is a proxy for *the haystack is prose*, not a length
    rule. A dated measurement on 2026-08-23 at ``d3e39e6`` lowered this function's
    cutoff, classified the 26 returned assertion sites by haystack, and found 22
    non-prose sites where normalization was meaningless. That historical 22-of-26
    observation is why #445 kept this conservative floor and #474 owns haystack
    discrimination instead; it is not a current inventory of the tree.

    This remains a membership floor. Prose enumeration or counting stays beyond
    #412's declared ceiling and can still undercount silently.
    """

    found: set[tuple[str, str]] = set()
    for relative in _tracked(root, "tools/test_*.py"):
        source = (root / relative).read_text(encoding="utf-8")
        found.update((relative, needle) for needle in raw_long_assert_not_in(source))
    return found


class ProseAssertionsNormalizeBothSides(ProseBind, unittest.TestCase):
    def test_assert_prose_in_reads_across_hard_wraps_and_literal_glue(self):
        self.assertProseIn(
            'a phrase split across two adjacent string literals',
            'a phrase split across two adjacent "string"\n"literals"',
        )

    def test_assert_prose_not_in_fails_when_only_formatting_differs(self):
        with self.assertRaises(AssertionError):
            self.assertProseNotIn(
                "a retired clinician ruling",
                "a retired clinician\n'ruling'",
            )

    def test_the_needle_is_normalized_too(self):
        self.assertProseIn(
            "the needle is\n**hard wrapped**",
            "the needle is hard wrapped",
        )

    def test_a_prose_line_population_is_one_haystack(self):
        with self.assertRaises(AssertionError):
            self.assertProseNotIn(
                "a retired clinician ruling",
                ["a retired clinician", "ruling"],
            )


class TheSilentDirectionHasARefusingWalk(unittest.TestCase):
    def test_the_prose_proxy_is_long_constants_and_only_raw_assert_not_in(self):
        forty = "x" * 40
        thirty_nine = "x" * 39
        source = (
            "self.assertNotIn(%r, prose)\n"
            "self.assertNotIn(%r, prose)\n"
            "self.assertProseNotIn(%r, prose)\n"
        ) % (forty, thirty_nine, forty)
        self.assertEqual({forty}, raw_long_assert_not_in(source))

    def test_every_survivor_is_exactly_declared_and_reasoned(self):
        found = repository_survivors(REPO_ROOT)
        self.assertEqual(set(DECLARED_RAW_ASSERT_NOT_IN), found)
        for reason in DECLARED_RAW_ASSERT_NOT_IN.values():
            self.assertTrue(reason.strip())

if __name__ == "__main__":
    unittest.main()
