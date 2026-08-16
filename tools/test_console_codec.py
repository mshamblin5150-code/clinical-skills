"""Tests for the console codec helper, and for every tool having taken it.

Two jobs, and the second is the one worth having.

**The helper itself.** A stream on a codec that cannot carry the text must end up
carrying it, and a stream whose codec genuinely cannot be moved must still print a
legible line rather than raise. Nothing here may raise: issue #150 is not really
about a mangled character, it is about a print that raised and exited **1**, which
``guidelines_search.py``'s own contract reads as *a genuine zero*.

**Parity across ``tools/``.** The last test reads every module in ``tools/`` that
has a command line and asserts it calls ``use_utf8`` in its ``__main__`` block.
That is ``test_spelling_scan.py``'s reasoning applied to a habit: a rule kept by
remembering to type a line is a rule the fifteenth tool will not have, and #150
found the fourteenth by crashing on a page with a ``>=`` sign on it.

The forms written out below are real non-cp1252 characters on purpose -- this file
is Python, not Markdown, so the spelling scan does not read it, and nothing here is
corpus text.
"""

import ast
import io
import unittest
from pathlib import Path

from console_codec import use_utf8

TOOLS = Path(__file__).resolve().parent

# The character #150 died on, from a real IDSA hit. cp1252 has no code point for it.
GREATER_EQUAL = "≥"

MAIN_GUARD = 'if __name__ == "__main__":'


def cp1252_stream() -> io.TextIOWrapper:
    """A text stream on the codec a Windows console hands you by default."""
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252")


class Stubborn:
    """A stream whose codec cannot be moved -- the console that is genuinely cp1252.

    ``io.UnsupportedOperation`` is what a real wrapper raises when it will not take a
    new encoding, and it is both a ``ValueError`` and an ``OSError``; raising the
    plain ``ValueError`` here keeps the stub from asserting which one arrives.
    """

    def __init__(self):
        self.encoding = "cp1252"
        self.errors = "strict"

    def reconfigure(self, *, encoding=None, errors=None):
        if encoding is not None:
            raise ValueError("underlying stream will not take a new encoding")
        self.errors = errors


class TheHelper(unittest.TestCase):
    def test_a_cp1252_stream_ends_up_carrying_the_character_that_killed_150(self):
        stream = cp1252_stream()
        use_utf8(stream)
        print(f"grade 4(O) if {GREATER_EQUAL}2 SIRS criteria", file=stream)
        stream.flush()
        written = stream.buffer.getvalue().decode("utf-8")
        self.assertIn(GREATER_EQUAL, written)

    def test_it_replaces_rather_than_raises_when_the_codec_cannot_be_moved(self):
        """The half that keeps the exit status truthful. A `?` in a line is a
        cosmetic loss; a traceback is a run that reported a settled negative."""
        stream = Stubborn()
        use_utf8(stream)
        self.assertEqual(stream.errors, "replace")

    def test_a_stream_with_no_reconfigure_is_left_alone(self):
        """`redirect_stdout(StringIO())` is how this repo's tests read output, and a
        helper that raised on one would fail every command-line test in `tools/`."""
        stream = io.StringIO()
        use_utf8(stream)
        stream.write(GREATER_EQUAL)
        self.assertEqual(stream.getvalue(), GREATER_EQUAL)

    def test_it_takes_several_streams(self):
        out, err = cp1252_stream(), cp1252_stream()
        use_utf8(out, err)
        self.assertEqual(out.encoding, "utf-8")
        self.assertEqual(err.encoding, "utf-8")

    def test_it_defaults_to_stdout_and_stderr(self):
        """Called with no arguments it is a process-level policy, which is why the
        tools call it from `__main__` and never at import."""
        import sys

        out, err = cp1252_stream(), cp1252_stream()
        original = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            use_utf8()
        finally:
            sys.stdout, sys.stderr = original
        self.assertEqual((out.encoding, err.encoding), ("utf-8", "utf-8"))


def main_guard(module: ast.Module) -> ast.If | None:
    """The module-level ``if __name__ == "__main__":`` node, or None."""
    for node in module.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
            and any(getattr(c, "value", None) == "__main__" for c in test.comparators)
        ):
            return node
    return None


def imports_helper(module: ast.Module) -> bool:
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "console_codec"
        and any(alias.name == "use_utf8" for alias in node.names)
        for node in ast.walk(module)
    )


def calls_helper(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
        and child.func.id == "use_utf8"
        for child in ast.walk(node)
    )


class EveryToolTakesIt(unittest.TestCase):
    """Parity, mechanically. Parses the files rather than importing them, because
    three of them need ``pypdf`` or ``fitz`` to import and none needs it to be read.

    **By AST and not by substring, which is not fastidiousness.** The first version
    of this searched the file text, and ``console_codec.py`` passed it on the usage
    example in its own docstring -- a module with no command line at all, graded as
    having one. That is ``spelling_scan``'s mention-versus-use distinction arriving
    uninvited: a tool could satisfy a text check by writing about the call in a
    comment. A parsed call is a call.
    """

    @staticmethod
    def command_line_tools() -> list[tuple[Path, ast.Module]]:
        found = []
        for path in sorted(TOOLS.glob("*.py")):
            if path.name.startswith("test_"):
                continue
            module = ast.parse(path.read_text(encoding="utf-8"))
            if main_guard(module) is not None:
                found.append((path, module))
        return found

    def test_the_repo_still_has_command_line_tools_to_check(self):
        """A glob that quietly matched nothing would pass the next test for the wrong
        reason. **19** of them as of 2026-08-16; the floor is the assertion.

        **It was 15 for about an hour**, then 16, then 17. ``anchor_scan.py`` was
        written on #124's branch while this rule was written on #150's, and the merged
        tree failed this class where neither branch did -- the floor held, the per-tool
        subtest did not. ``block_scan.py`` repeated it one merge later.

        The floor stays deliberately below the count. It is here to catch the glob
        breaking, not to be a second place the tool count has to be kept true -- #94
        and #96 are what one figure copied into ten places becomes."""
        self.assertGreaterEqual(len(self.command_line_tools()), 17)

    def test_the_helper_itself_is_not_counted_as_a_command_line_tool(self):
        """It has no command line, and it says `if __name__ == "__main__":` twice in
        its docstring. This is the false pass the AST exists to refuse."""
        names = [path.name for path, _ in self.command_line_tools()]
        self.assertIn(MAIN_GUARD, (TOOLS / "console_codec.py").read_text(encoding="utf-8"))
        self.assertNotIn("console_codec.py", names)

    def test_every_command_line_tool_calls_use_utf8_from_its_main_block(self):
        for path, module in self.command_line_tools():
            with self.subTest(tool=path.name):
                self.assertTrue(
                    imports_helper(module), f"{path.name} does not import the helper"
                )
                self.assertTrue(
                    calls_helper(main_guard(module)),
                    f"{path.name} imports the helper but does not call it under "
                    f"{MAIN_GUARD}",
                )


if __name__ == "__main__":
    unittest.main()
