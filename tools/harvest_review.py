"""Print the harvested strings nobody has ruled on yet, so a human can. Issue #12.

**This prints PHI. Never paste its output anywhere -- not into a ticket, not
into an agent session, not into a commit message.** That is the opposite of
``tools/corpus_census.py``, which reads the same corpus and can only emit
integers precisely so its output is safe to quote. Use ``--count`` here when a
number is all that is needed.

The problem it exists for
=========================

``phi_scan`` harvests names from ``scratch/name-index.json``: the ``name`` field,
and any window line that looks lexically like a name. ``win[0]`` is the name's
own line, so harvesting it is sound. ``win[1..3]`` are the shorthand lines that
follow, and clinical shorthand is full of two-word letters-only phrases -- an
allergy label, a history prefix, a medication. Those get indexed as patient
names, and each one will eventually refuse a fixture that contains no PHI at
all. ``fixtures/day-b/shorthand/case-10.md`` was refused for exactly this.

The reverse also happens: a real name the index only ever caught mid-note, with
no entry of its own. So the class cannot be dropped wholesale, and it cannot be
allowlisted wholesale either.

Why this is not automated
=========================

Nothing here can tell the two apart, and two plausible discriminators were tried
and rejected on 2026-08-11:

- **Recurrence.** A phrase in many notes looks like vocabulary and a phrase in
  one note looks like a person -- but a frequently-seen patient appears across
  many day files, so this classifies the most-seen patient as vocabulary.
- **Name-position collision.** Refusing to allowlist anything the index puts in
  a name position is a sound guard, and it is worth having for future edits to
  ``NOT_NAMES`` -- but every string listed here is by construction absent from
  every name position. It can never fire on one of them.

So this prints, and a human decides. It writes nothing: an allowlist that can be
written without a human keystroke is one that can put a patient name on the safe
list without a human keystroke.

Deciding
========

For each string below, one of two things is true.

- **Clinical vocabulary.** Add it lowercase to ``NOT_NAMES`` in
  ``tools/phi_scan.py``, with the date you ruled on it. It stops being scanned
  for, and stops refusing innocent lines.
- **A real name.** Add it to ``scratch/harvest-reviewed.json`` -- gitignored,
  because it is a list of patient names. It keeps refusing, and stops appearing
  here.

**Anything you do neither to stays exactly as it is: scanned for, and refused.**
An abandoned review leaves the firewall at full strength, never weaker.

Usage:

    python tools/harvest_review.py           # the strings, with their context
    python tools/harvest_review.py --count    # just how many, safe to paste
"""

from __future__ import annotations

import json
import sys
from typing import NamedTuple, Sequence

import phi_scan

from console_codec import use_utf8


class Sighting(NamedTuple):
    """One appearance of an unruled string, with what surrounds it."""

    text: str
    source: str
    position: int
    window: tuple[str, ...]


def sightings(entries: Sequence[dict], unruled: set[str]) -> list[Sighting]:
    """Where each unruled string was harvested from, in reading order.

    One per appearance rather than one per string: the same phrase under two
    different patients is the strongest evidence it is vocabulary, and that is
    invisible if the sightings are collapsed.
    """
    wanted = {name.casefold(): name for name in unruled}
    found: list[Sighting] = []
    for entry in entries:
        window = tuple(entry.get("win", []))
        for position, line in enumerate(window):
            match = wanted.get(line.strip().casefold())
            if match is not None:
                found.append(Sighting(
                    text=match,
                    source=str(entry.get("file", "?")),
                    position=position,
                    window=window,
                ))
    return sorted(found, key=lambda s: (s.text.casefold(), s.source, s.position))


def render(found: Sequence[Sighting], unruled: set[str]) -> str:
    if not unruled:
        return "harvest review: nothing unruled. Every harvested string has been decided.\n"

    seen: list[str] = []
    lines = [
        f"harvest review: {len(unruled)} strings have never been ruled on.",
        "",
        "*** This is PHI. Do not paste it anywhere. ***",
        "",
    ]
    for sighting in found:
        if sighting.text not in seen:
            seen.append(sighting.text)
            lines.append(f"[{len(seen)}] {sighting.text!r}")
        lines.append(f"      {sighting.source}, window position {sighting.position}")
        for index, line in enumerate(sighting.window):
            marker = "    >" if index == sighting.position else "     "
            lines.append(f"{marker} {line.strip()}")
        lines.append("")

    # A string can be harvested from a window this pass no longer walks. The
    # index gained a producer on #141 -- `name_index.py` -- but that one merges
    # rather than rebuilds, so every entry predating it keeps whatever shape it
    # was written with and none of them is guaranteed. Say so rather than
    # silently listing fewer than the count.
    unsighted = sorted(unruled - {s.text for s in found})
    if unsighted:
        lines.append(f"{len(unsighted)} with no window to show:")
        lines.extend(f"      {text!r}" for text in unsighted)
        lines.append("")

    lines.extend([
        "Vocabulary  -> add lowercase to NOT_NAMES in tools/phi_scan.py, with today's date.",
        "A real name -> add to scratch/harvest-reviewed.json, the gitignored ledger.",
        "Neither     -> it keeps being scanned for, and keeps refusing.",
        "",
        "Nothing was written. Paste-ready ledger of everything above, if every one",
        "of them is a name -- trim the vocabulary out before using it:",
        "",
        json.dumps(sorted(unruled), indent=2),
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    entries = phi_scan.harvest_entries()
    if not entries:
        print(
            "harvest review: no name index under scratch/ -- nothing to review.\n"
            "The corpus layer is inactive on this clone.",
            file=sys.stderr,
        )
        return 0

    unruled = phi_scan.unreviewed_names(entries, phi_scan.reviewed_names())
    if "--count" in argv:
        print(len(unruled))
        return 0

    print(render(sightings(entries, unruled), unruled))
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
