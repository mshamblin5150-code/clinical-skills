"""Formatting-robust membership assertions for prose-backed tests."""

import re
from collections.abc import Iterable


GLUE = re.compile(r"[\"'#>*`]")


def normalized(text: str | Iterable[str]) -> str:
    """Remove prose glue and collapse whitespace for one membership operand."""

    if not isinstance(text, str):
        text = "\n".join(text)
    return re.sub(r"\s+", " ", GLUE.sub(" ", text)).strip()


class ProseBind:
    """Assert membership after normalizing both the needle and the haystack.

    This mixin makes a prose bind robust to hard wrapping, Markdown emphasis,
    comment marks, and quotes split across adjacent literals. It does not make
    prose inspection complete: tests that enumerate or count prose can still
    undercount silently, and detecting those sites would require data-flow
    analysis outside this helper's declared ceiling.
    """

    def assertProseIn(
        self,
        needle: str | Iterable[str],
        haystack: str | Iterable[str],
        msg: str | None = None,
    ) -> None:
        self.assertIn(normalized(needle), normalized(haystack), msg)

    def assertProseNotIn(
        self,
        needle: str | Iterable[str],
        haystack: str | Iterable[str],
        msg: str | None = None,
    ) -> None:
        self.assertNotIn(normalized(needle), normalized(haystack), msg)
