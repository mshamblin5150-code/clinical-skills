"""Command-path policy: configure UTF-8, then refuse an old interpreter.

    from console_codec import require_python_floor, use_utf8

    if __name__ == "__main__":
        use_utf8()
        require_python_floor()
        raise SystemExit(main(sys.argv[1:]))

The shared grader family instead delegates ``main()`` to ``run_grader.run()``,
which owns both calls before it parses, loads or prints anything.

**The defect this exists for is an exit status, not a mangled character.** On Windows
the default stdout codec is cp1252, and the text these tools print is full of
characters it has no code point for -- ``>=`` written as its own sign, an en dash, a
typographic quote, a Greek mu. The ``print`` raises ``UnicodeEncodeError``, the
traceback escapes ``main``, and the process exits **1**. ``guidelines_search.py``'s
contract reads 1 as *a genuine zero*, so a query that in fact matched a page gets
recorded as a settled negative -- by a caller checking ``$?``, and by a reader who
sees the ``== query`` header, a few hits, and no scroll bar. Issue #150.

**``errors="replace"`` carries as much of the fix as the encoding does.** A stream
whose codec genuinely will not move still has to print a legible line with a ``?`` in
it rather than raise, because the thing being protected is the exit status and not
the glyph.

**Called from the command path, never at import.** Reconfiguring ``sys.stdout`` and
refusing an interpreter are decisions about a process. Direct tools call both under
``__main__``; grader members reach them through ``run_grader.run()``. UTF-8 is first
so the refusal is one legible line even on the older interpreter. Importing either
module changes no stream and exits no process. ``tools/test_console_codec.py`` parses
both arrangements and asserts the ordered calls are owned on each path, so this is a
mechanism rather than a habit.

**What that placement does not cover, stated rather than discovered later.** A tool
printing *before* ``main`` would print through the old codec; nothing here does, and
``test_console_codec`` is not what would catch it. And **a caller that imports
``main()`` instead of running the script gets none of this** -- which is deliberate,
since such a caller owns its own streams, but it does mean the in-process tests in
this repo exercise the pre-fix path. That is why #150's end-to-end case is a
subprocess: ``redirect_stdout(io.StringIO())`` has no codec to be wrong about, so
every existing command-line test passed throughout the bug's life.

Stdlib only, and it opens nothing.
"""

from __future__ import annotations

import sys
from typing import TextIO

CODEC = "utf-8"
ON_ERROR = "replace"

# What a stream raises when it will not take a new encoding. `io.UnsupportedOperation`
# is both a ValueError and an OSError, and an unknown codec name is a LookupError;
# naming the three is narrower than `except Exception` and covers every way this can
# fail short of a bug in here.
UNMOVABLE = (ValueError, OSError, LookupError)


def use_utf8(*streams: TextIO) -> None:
    """Put ``streams`` -- by default stdout and stderr -- on UTF-8 with replacement.

    Silent, and it swallows every way a stream can refuse to be reconfigured: a
    helper whose whole job is keeping a print from taking a run down would be
    self-defeating if it took the run down itself. A stream with no ``reconfigure``
    is left alone, which is the ``io.StringIO`` this repo's tests redirect into.

    **Not "cannot raise", which is what this said first.** It catches the three types
    in ``UNMOVABLE`` rather than bare ``Exception``, so a stream exotic enough to
    raise a ``TypeError`` out of ``reconfigure`` would still escape. Narrow is the
    right call -- a bug in here should be visible -- but the guarantee is "no
    codec refusal escapes", not "nothing escapes".

    The varargs exist for the tests: production always calls it with none, and the
    alternative was a helper that could only be exercised by monkeypatching ``sys``.
    """
    for stream in streams or (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding=CODEC, errors=ON_ERROR)
        except UNMOVABLE:
            # The codec would not move. Take the error handler on its own, which is
            # the limb that keeps the exit status truthful.
            try:
                reconfigure(errors=ON_ERROR)
            except UNMOVABLE:
                pass


def require_python_floor(version: tuple[int, int] | None = None) -> None:
    """Refuse a command run below the repository's declared consumer floor.

    The import stays inside the command-path helper so importing
    ``console_codec`` remains free of the floor instrument and its Git-facing
    dependencies.  ``version`` is injectable only so the refusal can be tested
    on the maintainer's newer interpreter.
    """

    from python_floor import CONSUMER_FLOOR

    running = version if version is not None else sys.version_info[:2]
    if running >= CONSUMER_FLOOR:
        return
    needed = ".".join(str(part) for part in CONSUMER_FLOOR)
    actual = ".".join(str(part) for part in running)
    print(
        f"Python {needed} or newer is required; this interpreter is Python {actual}.",
        file=sys.stderr,
    )
    raise SystemExit(2)
