"""Keep ``scratch/name-index.json`` covering the corpus it is harvested from.

``phi_scan``'s corpus layer harvests every patient name it will ever scan for
from that index -- ``harvest_entries`` to ``harvested_names`` to ``kept_names``.
An encounter with no entry contributes no name, so a patient named **only**
inside it is scanned for by neither layer: the corpus layer has never heard of
them, and the shape layer does not catch a name. That is
[#141](https://github.com/mshamblin5150-code/clinical-skills/issues/141), and it
is narrower than the hole ``phi_scan``'s docstring already states -- there the
name is nowhere in the corpus, here it *is* in the corpus and the harvest did
not reach it.

    python tools/name_index.py            # report; exits 1 if the index is short
    python tools/name_index.py --write    # merge the missing encounters in

**Until this existed the index had two consumers and no producer** -- this module
and ``harvest_review.py`` read it, and nothing wrote it. So the shortfall was not
fixable by running anything, and whether the skill that quoted its size had
copied the figure from it or arrived at the same number independently is not
recoverable.

**It merges and never rebuilds, and that is the whole safety argument.** The
``name`` field is hand-curated: most entries carry the line they were harvested
from verbatim, and a minority carry a human's correction of it, which nothing
mechanical can re-derive. A from-scratch rebuild would silently replace every one
of those with whatever a parser picked. So an existing entry is copied through
byte for byte and the merge only ever appends -- ``merge`` states that as a
prefix property and ``test_name_index`` asserts it. The corollary is the one #141
worried about and it falls out for free: no harvested string disappears, so no
ruling in ``scratch/harvest-reviewed.json`` is invalidated and the #12 review is
not reopened.

**The gap is not a backlog, it is a rate.** The clinician still scans every shift
for the current course, so new day files keep arriving and each one is
unindexed until something regenerates. Run this after adding a day file, and
before trusting a clean ``phi_scan``.

The parser
----------

`batch-shift` step 3 is the written spec and this is it made runnable. ``Note N``
opens an encounter, matched case-insensitively -- real files carry ``Note 3`` and
``NOte 4`` in one document -- and ``N`` is the number the file *declares*, never
the encounter's position: the numbering skips and repeats in this catalog, and
that step's instruction is to report it rather than renumber it tidy. Keying on
position would re-file every encounter after a skip.

**The name is not reliably the line after ``Note N``.** It can sit below the
vitals, or below a remark the clinician wrote to themselves. That is exactly what
defeated the index: each of the three encounters with no entry put something else
there -- one a stray punctuation character and a blank line, two a parenthetical
annotation. So this reads a **window** and takes the first line shaped like a
name, which is that step's own remedy.

**``looks_like_a_name`` lives here and ``phi_scan`` imports it**, rather than each
module holding a copy. A generator with its own answer could write a ``name`` the
harvest will not scan for, which is the one failure this tool exists to prevent
-- ``reference_scan`` importing ``REFERENCE_HEADING`` from the renderer instead
of restating it, for that reason.

**``LOOKAHEAD`` is a bound and not a formality.** Two words of clinical
vocabulary have a name's exact shape -- ``sore throat`` passes the predicate --
so every extra line searched is another chance to file a symptom as a patient.
Measured 2026-08-19 by running this parser over every entry the index already
carried: the name is the encounter's first non-blank line in the large majority,
and never deeper than the seventh. **No figure is stated for that** -- it is
counted against the gitignored corpus, nothing committed re-derives it, and this
tool's own ``--write`` moves the denominator on first use, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) arriving
inside the module that would have stated it.

**The direction is the durable half and it is the opposite of the intuition.**
In not one case did this parser pick a line *above* the one the index already
carries, so widening the search is what costs and narrowing it is what loses a
patient.

What it cannot reach
--------------------

**A name the predicate does not recognize** -- a single word, a spelling with a
digit in it. A minority of the entries the index already carried were harvested
from such a line, and the report prints that count on every run rather than this
paragraph stating it. Such an encounter gets an entry with ``name: None``, which
covers it for the corpus layer's *denominator* and contributes nothing to its
*harvest*. **That is not this parser being lax**: ``harvested_names`` applies the
same predicate to the window, so such a name has never been scanned for by
anything, and the only path for one is the curated field a human fills in.
``harvest_review.py`` is where it goes next.

**Which harvested strings a new window adds, beyond the names.** #141 expected a
rebuild to reopen [#12](https://github.com/mshamblin5150-code/clinical-skills/issues/12)'s
vocabulary review, and merging answers only the *discard* half of that: nothing
already ruled on disappears. The *addition* half does not fall out -- a window is
the name plus the shorthand lines under it, ``harvested_names`` takes every
name-shaped line in it, and clinical shorthand is full of two-word letters-only
phrases. On the three encounters this was built for the addition was zero, and
**that is a fact about those three and not a property of the mechanism**; the
next shift can break it. So the report counts the further name-shaped lines each
proposed window contributes, and they go to ``harvest_review.py`` like any other.

**Whether a picked name is a patient's.** Nothing here reads a note. A clean run
means every encounter has an entry, never that every entry names the right
person.

**A patient named nowhere in the corpus**, which is the hole ``phi_scan``'s own
docstring states and which no widening of this index reaches.

**A date the corpus holds written in another format elsewhere** --
[#261](https://github.com/mshamblin5150-code/clinical-skills/issues/261). That is
a form the index has and cannot recognize restated, not an entry the index lacks,
and the two remedies do not overlap.

PHI
---

The corpus is the patient record itself. **Counts only by default**, on
``corpus_census.py``'s terms and for its reason: the report is integers, its own
fixed labels and the corpus directory's name, so it is safe to paste into a
ticket. **``--show`` output is PHI** -- it prints the names this run proposes to
add. Read it, do not paste it.

The index it writes is a list of patient names, so the target must be under
``scratch/`` unless it is outside every checkout altogether -- ``refuse_target``
is that guard, and it is the one thing here that can stop a write.

Exit status
-----------

0 the index covers the corpus, 1 it does not, **2 every way of not having
scanned**: no corpus directory, no file in it, no ``Note N`` line in any file
read, and an index file that is present and will not parse. That last limb is the
one that protects the curation. ``phi_scan.harvest_entries`` falls back to ``[]``
for a file that is absent *and* for one that is malformed -- correct there, since
a scanner with no names finds none -- and the same fallback here would read a
damaged index as a cold start and write a from-scratch one over it. An index that
is genuinely absent is a cold start and exits 1, because the corpus is uncovered
and that is the true statement about it.

**A refused write is not a refused scan.** ``refuse_target`` turning a ``--write``
away leaves the report standing and the status at 1, because the shortfall is
what the run found and the refusal is a note beside it. Returning 2 there was the
first version, and it filed the strongest thing known about the run under the
weakest heading -- ``differential_scan.py``'s ordering, caught by review.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import corpus_census as cc
from console_codec import use_utf8
from repo_root import enclosing_checkout, scratch_root

# `guidelines_search.py`'s convention, already in `specificity_scan`,
# `differential_scan`, `anchor_scan`, `block_scan` and `phi_scan`: a status that
# says *did not scan* rather than *found nothing*.
NOT_SCANNED = 2

# **The delimiter is imported, not restated**, and the first version of this
# module restated it. ``corpus_census.NOTE_DELIMITER`` is what counts the
# encounters every figure in this repo is measured against, so the denominator
# printed here has to be the same denominator -- and a copy that drifts is not a
# cosmetic defect. Measured against the copy: ``Note`` and its number split by a
# **newline** and a number with a letter welded to it (``Note 5a``) both matched
# the census and not the copy, so those encounters were invisible to the
# generator *and* to the denominator at once. Coverage reads 100% while a patient
# is unindexed -- which is this ticket's own failure mode, rebuilt inside its fix.
# `reference_scan` importing ``REFERENCE_HEADING`` rather than keeping a copy,
# for that reason and caught the same way.
#
# It is case-insensitive because the corpus carries "Note 3", "NOte 3" and
# "NOte 4" in one document, and a case-sensitive match silently merges
# encounters -- `batch-shift` step 3.
NOTE_DELIMITER = cc.NOTE_DELIMITER

# The number inside a matched delimiter. The delimiter carries no capture group
# -- the census only ever splits on it -- so the one thing this module needs
# beyond the split is read back out of the matched text rather than by holding a
# second pattern for the whole shape.
DELIMITER_NUMBER = re.compile(r"\d+")

# How many lines an entry keeps, and how far down the encounter the name is
# looked for. Four is the index's existing shape; the search bound is measured
# rather than chosen -- see the module docstring.
WINDOW = 4
LOOKAHEAD = 8

# What the census reads, so the denominator here is the census's denominator.
DAY_FILE_SUFFIXES = (".txt", ".md")


def looks_like_a_name(text: str) -> bool:
    """Two or three capitalizable words of letters, longer than five characters.

    **The one home for this predicate.** ``phi_scan`` imports it rather than
    keeping a copy, because a generator that recognized a name the harvest does
    not would write a ``name`` field nothing ever scans for -- an entry that
    covers an encounter and protects nobody. ``test_name_index`` asserts the two
    modules hold the same object.
    """
    return bool(
        len(text) > 5
        and re.fullmatch(r"[A-Za-z][A-Za-z'\-]+(?: [A-Za-z][A-Za-z'\-.]+){1,2}", text)
    )


@dataclass(frozen=True)
class Encounter:
    """One ``Note N`` block, reduced to what an index entry holds.

    ``name`` is ``None`` where no line in the lookahead is name-shaped. That is a
    real state and not a parse failure -- see the module docstring.
    """

    stem: str
    note: int
    window: tuple[str, ...]
    name: str | None

    @property
    def raw(self) -> str:
        """``win[0]``, which is what every entry in the index already carries."""
        return self.window[0] if self.window else ""

    @property
    def key(self) -> tuple[str, int]:
        return (self.stem, self.note)

    def as_entry(self) -> dict:
        """The index's own record shape, in the index's own key order."""
        return {
            "file": f"{self.stem}.txt",
            "note": self.note,
            "raw": self.raw,
            "win": list(self.window),
            "name": self.name,
        }


@dataclass(frozen=True)
class Corpus:
    """The day files, byte-identical copies already dropped.

    ``aliases`` maps **every** stem on disk to the one kept for its content. The
    catalog holds one day file twice under two different names, so an entry filed
    under the dropped twin covers the kept file -- without that the whole shift
    reads as unindexed. ``corpus_census.read_corpus`` drops the copy the same way
    and for the same reason, which is what makes the two denominators comparable.

    **This holds note text**, the one thing here that does, so it never reaches
    ``format_report``; ``coverage`` reduces it to integers first.
    """

    directory: Path
    files: int
    kept: tuple[tuple[str, str], ...]
    aliases: dict


@dataclass(frozen=True)
class Coverage:
    """Integers only, so it can be printed."""

    files: int
    unique_files: int
    encounters: int
    covered: int
    entries: int
    orphans: int
    unrecognized: int
    proposed: int
    proposed_named: int
    proposed_extra_strings: int

    @property
    def uncovered(self) -> int:
        return self.encounters - self.covered


def read_corpus(directory: Path) -> Corpus:
    """Every day file in ``directory``, deduplicated by content.

    Deduplication is by digest and not by filename, because the copy in the
    catalog does not share a name with its original.
    """
    kept: list[tuple[str, str]] = []
    aliases: dict = {}
    seen: dict = {}
    files = 0
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in DAY_FILE_SUFFIXES or not path.is_file():
            continue
        files += 1
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest not in seen:
            seen[digest] = path.stem
            kept.append((path.stem, path.read_text(encoding="utf-8", errors="replace")))
        aliases[path.stem] = seen[digest]
    return Corpus(directory=directory, files=files, kept=tuple(kept), aliases=aliases)


def encounters_in(corpus: Corpus) -> list[Encounter]:
    found: list[Encounter] = []
    for stem, text in corpus.kept:
        found.extend(_split(stem, text))
    return found


def encounters(directory: Path) -> list[Encounter]:
    """Convenience for a caller that has a path and wants the blocks."""
    return encounters_in(read_corpus(directory))


def _split(stem: str, text: str) -> list[Encounter]:
    """The ``Note N`` blocks of one day file.

    Text before the first delimiter is a day header and belongs to no encounter,
    which is `batch-shift` step 3's rule -- it goes nowhere rather than being
    folded into the first patient.

    Worked in character offsets rather than in lines, because the delimiter is
    the census's and the census's spans a newline between the token and its
    number. Reading it line by line cannot see that shape at all.
    """
    opens = list(NOTE_DELIMITER.finditer(text))
    found: list[Encounter] = []
    for position, match in enumerate(opens):
        end = opens[position + 1].start() if position + 1 < len(opens) else len(text)
        number = int(DELIMITER_NUMBER.search(match.group(0)).group(0))
        body = [line.strip() for line in text[match.end():end].splitlines() if line.strip()]
        found.append(_read_window(stem, number, body))
    return found


def _read_window(stem: str, number: int, body: Sequence[str]) -> Encounter:
    """Anchor the window at the first name-shaped line, or at the top if none.

    Anchoring on the name is what makes ``raw == win[0]``, which holds for every
    entry the index already carries and is what ``phi_scan.name_position_names``
    reads as positional evidence that a string is a name at all.
    """
    searched = body[:LOOKAHEAD]
    at = next((i for i, line in enumerate(searched) if looks_like_a_name(line)), None)
    if at is None:
        return Encounter(stem, number, tuple(body[:WINDOW]), None)
    return Encounter(stem, number, tuple(body[at:at + WINDOW]), searched[at])


def covered_keys(entries: Iterable[dict], aliases: dict) -> set:
    """The ``(kept stem, declared note)`` pairs the index already speaks for."""
    keys = set()
    for record in entries:
        stem = Path(str(record.get("file", ""))).stem
        note = record.get("note")
        if isinstance(note, int):
            keys.add((aliases.get(stem, stem), note))
    return keys


def merge(entries: Sequence[dict], found: Sequence[Encounter], aliases: dict = None) -> list:
    """The existing entries, unchanged and in order, then the uncovered ones.

    **The prefix property is the design.** Nothing here edits, reorders or drops
    an existing record, so every hand-corrected ``name`` survives, no harvested
    string disappears, and no ruling in ``scratch/harvest-reviewed.json`` is
    invalidated. A rebuild could promise none of those.

    Idempotent by construction: a second run finds the added encounters already
    covered and appends nothing.

    ``aliases`` is optional only because a caller whose stems already agree needs
    none. **A caller reading a real corpus must pass ``Corpus.aliases``** -- the
    catalog holds one day file twice under two names, and without the map the
    entries filed under the dropped twin cover nothing and the whole shift is
    appended a second time.
    """
    if aliases is None:
        aliases = {}
    covered = covered_keys(entries, aliases)
    added = []
    for encounter in found:
        key = (aliases.get(encounter.stem, encounter.stem), encounter.note)
        if key in covered:
            continue
        covered.add(key)
        added.append(encounter.as_entry())
    return list(entries) + added


def coverage_in(entries: Sequence[dict], corpus: Corpus, found: Sequence[Encounter]) -> Coverage:
    covered = covered_keys(entries, corpus.aliases)
    keys = {(corpus.aliases.get(e.stem, e.stem), e.note) for e in found}
    uncovered = [e for e in found if (corpus.aliases.get(e.stem, e.stem), e.note) not in covered]
    return Coverage(
        files=corpus.files,
        unique_files=len(corpus.kept),
        encounters=len(found),
        covered=len(found) - len(uncovered),
        entries=len(entries),
        orphans=len(covered - keys),
        # Counted over the entries the index already holds, so the parser's own
        # blind spot is a printed number rather than a claim in a docstring.
        unrecognized=sum(
            1 for record in entries
            if not looks_like_a_name(str(record.get("raw", "")).strip())
        ),
        proposed=len(uncovered),
        proposed_named=sum(1 for e in uncovered if e.name),
        # The #12 surface a merge *adds*: every further name-shaped line a
        # proposed window carries under the name. `harvested_names` will scan for
        # each of them, and clinical shorthand is full of two-word letters-only
        # phrases that are not patients.
        proposed_extra_strings=sum(
            sum(1 for line in e.window[1:] if looks_like_a_name(line))
            for e in uncovered
        ),
    )


def coverage(entries: Sequence[dict], directory: Path) -> Coverage:
    """Convenience for a caller that has a path -- ``phi_scan``'s, and the tests'."""
    corpus = read_corpus(directory)
    return coverage_in(entries, corpus, encounters_in(corpus))


def load_index(path: Path):
    """``(entries, refusal)`` -- and an absent file is not a refusal.

    **The two absences are not the same claim**, which is the whole reason this
    does not reuse ``phi_scan.harvest_entries``. A file that is not there is a
    cold start and the corpus is simply uncovered. A file that is there and will
    not parse is an index whose contents are unknown, and treating it as empty
    would write a from-scratch index over hand-corrected names.
    """
    if not path.is_file():
        return [], None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as problem:
        return None, f"{path} will not parse ({problem.__class__.__name__})"
    if not isinstance(loaded, list):
        return None, f"{path} is not a JSON list"
    if any(not isinstance(record, dict) for record in loaded):
        return None, f"{path} holds a member that is not a record"
    return loaded, None


def refuse_target(path: Path, scratch: Path | None = None) -> str | None:
    """Why this path may not be written, or ``None``.

    The index is a list of patient names. It belongs under ``scratch/``, which is
    gitignored and which ``phi_scan``'s path layer refuses a commit from even
    under ``git add -f``. Anywhere else inside a checkout it is one ``git add -A``
    from being tracked with no net under it -- [#176](https://github.com/mshamblin5150-code/clinical-skills/issues/176)
    and [#223](https://github.com/mshamblin5150-code/clinical-skills/issues/223)'s
    subject, arriving on a file this tool creates.

    Outside every checkout there is nothing to commit it to, which is what lets
    the tests write into a temp directory.
    """
    target = (scratch_root() if scratch is None else scratch).resolve()
    return _refuse(path.resolve(), target)


def _refuse(target: Path, scratch: Path) -> str | None:
    # **A reason string and no raise, deliberately** -- the one convention here
    # that #176 did not consolidate away. A refused write is not a refused scan:
    # the run read the whole corpus and knows exactly how short the index is, so
    # the refusal is a note beside that finding rather than instead of it.
    #
    # **The repo's own ``scratch/``, not any directory so named.** The first
    # version tested for a path component called ``scratch`` anywhere, which
    # blesses ``~/scratch/`` in somebody else's checkout on the strength of a
    # coincidence. ``permitted`` takes the resolved directory ``phi_scan``'s path
    # layer actually covers, and that parameter is the one thing a shared guard
    # needed that a single rule could not have: the other three writers refuse
    # every path inside a checkout, and this one blesses exactly one.
    checkout = enclosing_checkout(target, permitted=[scratch])
    if checkout is None:
        return None
    return (
        f"refusing to write {target}: it is inside the checkout at {checkout} "
        "and not under scratch/. The index is a list of patient names."
    )


def write_atomically(path: Path, text: str) -> None:
    """Write through a temp file in the same directory, then replace.

    **For a file whose whole argument is that curated names are never
    destroyed**, a half-written index is the one outcome worse than a short one:
    ``load_index`` would refuse it on the next run, correctly, and the names
    would be gone. ``os.replace`` is atomic on the same volume, which is why the
    temp file is made beside the target rather than in the system temp
    directory.
    """
    handle, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def format_report(found: Coverage, source: str, added, show: bool = False) -> list:
    """Integers, fixed labels and the corpus directory's name. Nothing else.

    ``--show`` is the one aperture, and it prints the names this run proposes to
    add. That output is PHI on ``harvest_review.py``'s terms.
    """
    lines = [
        f"name-index coverage ({source}):",
        f"  day files                    {found.files} read, {found.unique_files} unique",
        f"  encounters                   {found.encounters}",
        f"  entries                      {found.entries}, covering {found.covered}",
        f"  encounters with no entry     {found.uncovered}",
    ]
    if found.orphans:
        lines.append(
            f"  entries for no encounter     {found.orphans}   "
            "(counted, never dropped -- a name harvested from one is still a patient's)"
        )
    # Counted, never graded, on `filled_vitals_census.py`'s arrangement: it is a
    # standing property of the corpus rather than a defect in this run, and
    # failing on it would refuse every index the repo has ever had.
    lines.append(
        f"  entries this parser could not have named   {found.unrecognized}   "
        "(counted, not graded -- their names came from a human)"
    )
    if found.proposed:
        nameless = found.proposed - found.proposed_named
        lines.append(
            f"  proposed entries             {found.proposed}, a name found in {found.proposed_named}"
        )
        if nameless:
            lines.append(
                f"  proposed with no name        {nameless}   "
                "(covers the encounter, harvests nothing -- rule on it with harvest_review.py)"
            )
        lines.append(
            f"  further strings they harvest {found.proposed_extra_strings}   "
            "(the #12 surface a merge adds -- rule on them with harvest_review.py)"
        )
    if show and added:
        lines.append("")
        lines.append("  -- --show output is PHI: read it, do not paste it --")
        for record in added:
            lines.append(f"  {record['file']} note {record['note']}: {record['name']}")
    return lines


def main(argv: list) -> int:
    show = write = False
    # Walked rather than filtered, because ``--index``'s *value* is a path and a
    # filter that dropped it by string comparison would have to compare a
    # ``Path`` back to what was typed. ``Path("./x")`` and ``"./x"`` do not
    # compare equal, so a relative ``--index`` would have fallen through and been
    # read as the corpus directory instead.
    index = scratch_root() / "name-index.json"
    positional: list[str] = []
    rest = list(argv)
    while rest:
        argument = rest.pop(0)
        if argument == "--show":
            show = True
        elif argument == "--write":
            write = True
        elif argument == "--index" and rest and not rest[0].startswith("--"):
            index = Path(rest.pop(0))
        elif not argument.startswith("--"):
            positional.append(argument)
    directory = Path(positional[0]) if positional else scratch_root() / "day-file-text"

    if not directory.is_dir():
        print(f"no corpus at {directory}", file=sys.stderr)
        return NOT_SCANNED

    entries, refusal = load_index(index)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        print(
            "Refusing to treat it as empty. An index that will not parse is an index\n"
            "whose contents are unknown, and a rebuild would overwrite every\n"
            "hand-corrected name in it. Fix or move the file and run again.",
            file=sys.stderr,
        )
        return NOT_SCANNED

    corpus = read_corpus(directory)
    if not corpus.kept:
        print(f"no day file in {directory}", file=sys.stderr)
        return NOT_SCANNED

    found = encounters_in(corpus)
    if not found:
        print(f"no encounter opens with a Note line in {directory}", file=sys.stderr)
        return NOT_SCANNED

    merged = merge(entries, found, corpus.aliases)
    added = merged[len(entries):]

    # **A refused write does not become a refused scan**, which is what the first
    # version did: it returned NOT_SCANNED here, before the report, so a run that
    # had read the whole corpus and knew exactly how short the index was printed
    # nothing and said it had not scanned. `differential_scan.py`'s ordering --
    # returning 2 would file the strongest thing known about the run under the
    # weakest heading. The shortfall is the finding; the refusal is a note beside
    # it, and it is on stderr where a refusal belongs.
    refused = refuse_target(index) if write and added else None
    if write and added and refused is None:
        write_atomically(index, json.dumps(merged, indent=1))
        entries = merged

    print("\n".join(format_report(
        coverage_in(entries, corpus, found), directory.name, added, show
    )))
    # Flushed before the hints, so the two streams land in the order a person
    # reads them rather than in the order the buffers happen to drain.
    sys.stdout.flush()
    if refused is not None:
        print(f"\n{refused}", file=sys.stderr)
    elif not write and added:
        print(
            f"\nThe index is {len(added)} encounter(s) short. Merge them in with:\n"
            "    python tools/name_index.py --write",
            file=sys.stderr,
        )
    return 1 if len(entries) < len(merged) else 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
