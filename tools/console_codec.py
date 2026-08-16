"""One line of process-level policy: the console takes UTF-8, and never raises.

    from console_codec import use_utf8

    if __name__ == "__main__":
        use_utf8()
        raise SystemExit(main(sys.argv[1:]))

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

**Called from ``__main__``, never at import.** Reconfiguring ``sys.stdout`` is a
decision about a process, and a module that made it on import would make it for every
test that imports it and for any tool that imports another -- and several here do
(``guidelines_search`` imports ``guidelines_index``, ``icd10_lookup`` imports
``icd10_build``, ``harvest_review`` imports ``phi_scan``). ``tools/test_console_codec.py``
parses every command line in ``tools/`` and asserts the call is there, so this is a
mechanism rather than a habit -- which is the part #150 left open, and the part a
sixteenth tool would otherwise be missing.

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
