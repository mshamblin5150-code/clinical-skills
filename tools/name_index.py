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
Measured against the 548 curated entries on 2026-08-19: the first name-shaped
line is the encounter's first non-blank line in 505 of them, and no deeper than
the seventh in any. **In not one case did this parser pick a line above the one
the index already carries**, so widening the search is what costs and narrowing
it is what loses a patient.

What it cannot reach
--------------------

**A name the predicate does not recognize.** 43 of the 548 curated entries were
harvested from a line this rejects -- a single word, a spelling with a digit in
it. Those get an entry with ``name: None``, which covers the encounter for the
corpus layer's *denominator* and contributes no name to its *harvest*. That is
not this parser being lax: ``harvested_names`` applies the same predicate to the
window, so such a name has never been scanned for, and the only path for one is
the curated field a human fills in. **The count of entries added without a name
is printed on every run** for that reason, and ``harvest_review.py`` is where it
goes next.

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
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from console_codec import use_utf8
from repo_root import scratch_root

# `guidelines_search.py`'s convention, already in `specificity_scan`,
# `differential_scan`, `anchor_scan`, `block_scan` and `phi_scan`: a status that
# says *did not scan* rather than *found nothing*.
NOT_SCANNED = 2

# The delimiter. Case-insensitive because the corpus carries "Note 3", "NOte 3"
# and "NOte 4" in one document, and a case-sensitive match silently merges
# encounters -- `batch-shift` step 3.
NOTE_LINE = re.compile(r"(?i)^[ \t]*note[ \t]*#?[ \t]*(\d+)\b")

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
    proposed: int
    proposed_named: int

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
    """
    lines = text.splitlines()
    opens = [
        (i, int(m.group(1)))
        for i, line in enumerate(lines)
        if (m := NOTE_LINE.match(line))
    ]
    found: list[Encounter] = []
    for position, (start, number) in enumerate(opens):
        end = opens[position + 1][0] if position + 1 < len(opens) else len(lines)
        body = [line.strip() for line in lines[start + 1:end] if line.strip()]
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
        proposed=len(uncovered),
        proposed_named=sum(1 for e in uncovered if e.name),
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


def refuse_target(path: Path):
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
    target = path.resolve()
    if "scratch" in (part.lower() for part in target.parts):
        return None
    for parent in target.parents:
        if (parent / ".git").exists():
            return (
                f"refusing to write {target}: it is inside the checkout at {parent} "
                "and not under scratch/. The index is a list of patient names."
            )
    return None


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
    if show and added:
        lines.append("")
        lines.append("  -- --show output is PHI: read it, do not paste it --")
        for record in added:
            lines.append(f"  {record['file']} note {record['note']}: {record['name']}")
    return lines


def main(argv: list) -> int:
    show = "--show" in argv
    write = "--write" in argv

    # Walked rather than filtered, because ``--index``'s *value* is a path and a
    # filter that dropped it by string comparison would have to compare a
    # ``Path`` back to what was typed. ``Path("./x")`` and ``"./x"`` do not
    # compare equal, so a relative ``--index`` would have fallen through and been
    # read as the corpus directory instead.
    index = scratch_root() / "name-index.json"
    positional: list = []
    rest = list(argv)
    while rest:
        argument = rest.pop(0)
        if argument == "--index" and rest:
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

    if write and added:
        problem = refuse_target(index)
        if problem is not None:
            print(problem, file=sys.stderr)
            return NOT_SCANNED
        index.write_text(json.dumps(merged, indent=1), encoding="utf-8")
        entries = merged

    print("\n".join(format_report(
        coverage_in(entries, corpus, found), directory.name, added, show
    )))
    # Flushed before the hint, so the two streams land in the order a person
    # reads them rather than in the order the buffers happen to drain.
    sys.stdout.flush()
    if not write and added:
        print(
            f"\nThe index is {len(added)} encounter(s) short. Merge them in with:\n"
            "    python tools/name_index.py --write",
            file=sys.stderr,
        )
    return 1 if len(entries) < len(merged) else 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
