"""Refuse to commit PHI. Standing rule 1, enforced instead of remembered.

Installed as a pre-commit hook (see CLAUDE.md), so it binds every commit in this
clone regardless of who or what makes it.

Two layers, and the difference between them is the whole design:

- **Corpus layer.** Every patient name and every date literal appearing in the
  gitignored corpus under ``scratch/``. This is the layer that catches real PHI,
  and **nothing can exempt a file from it.**
- **Shape layer.** Things that look like PHI whatever the corpus says: a ``dob``
  token followed by a date, an SSN, a phone number, an MRN followed by digits, a
  US-style ``M-D-YY`` short date. A file may exempt itself from this layer only, by
  declaring ``phi-scan: synthetic`` near the top -- which ``test_corpus_census``
  does, because testing a date extractor requires date-shaped literals.

The asymmetry is deliberate. A file can say "my dates are invented"; no file can
say "my patient names are fine".

Known limits, stated so nobody mistakes this for a guarantee:

- ``git commit --no-verify`` bypasses it, as it bypasses any hook.
- The corpus layer is only as good as ``scratch/``. On a fresh clone there is no
  corpus, so that layer finds nothing and the shape layer is all that remains.
- A patient name that appears nowhere in the corpus and is not date-shaped is
  caught by neither layer. All PHI here originates in the corpus, so this is a
  narrow hole, but it is a real one.
- **Binary files are skipped entirely**, so nothing inside ``reference/
  icd10cm-2026.sqlite`` is scanned. Its contents are the public ICD-10-CM
  release and carry no patient data. If a binary that could carry PHI is ever
  tracked here, this scanner will not say so.

Usage:

    python tools/phi_scan.py              # scan staged changes (what the hook runs)
    python tools/phi_scan.py --all        # scan every tracked file
    python tools/phi_scan.py --show       # reveal matches instead of redacting
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories the PHI firewall in .gitignore already covers -- scratch/ is working
# files, output/ is finished notes and case studies. Staging anything under them
# means someone reached for `git add -f`.
PHI_DIRECTORIES = ("scratch/", "output/", "cases/", "patients/")

# A file declaring this near its top is exempt from the SHAPE layer only.
SYNTHETIC_PRAGMA = "phi-scan: synthetic"
PRAGMA_SEARCH_CHARS = 4000

SHAPE_RULES = {
    # Requires an actual date after the token, so a `dob` field named in a
    # documentation table does not trip it.
    "dob-with-date": r"(?i)\bd\.?o\.?b\.?\b[^\n]{0,4}\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
    "mrn-with-digits": r"(?i)\bmrn\b[^\n]{0,6}\d",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b",
    # US short dates. ISO dates (2026-08-10) do not match: "2026" cannot be the
    # one-or-two-digit first field, and there is no word boundary mid-number.
    "us-short-date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
}

# Clinical phrases the name harvester mistakes for names. These are vocabulary,
# not identifiers, and they are already committed.
#
# The labeled forms are here because the bare token is not enough: the filter
# below tests the WHOLE harvested string, and the harvester really does index
# "allergy NKDA" and "allergies nkda" as two-word names, so "nkda" alone exempts
# neither. fixtures/day-b/shorthand/case-10.md writes it without a colon and was
# refused on exactly this. Only a form written without punctuation can be
# harvested at all -- "allergies: nkda" fails the fullmatch in _looks_like_a_name
# -- which is why day-a never tripped it.
#
# **Curate this by hand, one entry at a time.** #12 counted 26 harvested names
# carrying clinical vocabulary. That figure is not reproducible here and should
# not be quoted as if it were: it came from an unrecorded word list, and the
# count moves with whatever list you pick. What is reproducible is the shape of
# the problem -- each such name is a fixture refusal waiting to happen.
#
# The entries that hid a real patient name inside a longer phrase are gone;
# `prune_covered` drops those, and there were 3. What stops the class being
# exempted in bulk is the other direction: the harvest is lexical, so a
# surviving two-word phrase may simply *be* a patient name the index's own name
# field missed. Nothing in the set distinguishes that from vocabulary, which is
# the open question in #12.
NOT_NAMES = {
    "african american",
    "sore throat",
    "vaccs utd",
    "nkda",
    "allergy nkda",
    "allergies nkda",
}


_WORD_RUN = re.compile(r"\w+")


# A word character outside ASCII: word, and not one of the first 128.
_NON_ASCII_WORD = re.compile(r"[^\W\x00-\x7f]")


def _outside_ascii(text: str) -> bool:
    """True where comparing tokens cannot stand in for what ``re.I`` matches.

    Only **word** characters can break that correspondence, because only they
    take part in a word run or in a case substitution. Punctuation outside
    ASCII -- the em dashes and curly quotes this repo's Markdown is full of --
    separates runs on both sides and changes nothing. The distinction is worth
    making: treating any non-ASCII character as unindexable put most of the
    repo's own prose back on the slow path, and ``--all`` went from 0.2s to 2s.
    """
    return not text.isascii() and _NON_ASCII_WORD.search(text) is not None


class IndexedName(NamedTuple):
    name: str
    pattern: re.Pattern[str]


def _by_name(entry: IndexedName) -> str:
    """Sort on the name alone -- a compiled pattern has no ordering."""
    return entry.name


def _required_token(name: str) -> str | None:
    """A word every ASCII line containing ``name`` must also contain, or None.

    Any maximal run of word characters inside the name shows up in a matching
    line as a whole word: inside the name the run is bounded by non-word
    characters, and at the name's own edges the ``\\b`` anchors assert the same
    boundary. So a line whose word tokens exclude the run cannot contain the
    name, and the run is a sound thing to filter on. The longest run is chosen
    because it is the most selective.

    **Over ASCII only**, which is what ``build_index`` and ``CorpusIndex``
    between them guarantee. Case folding is where a token comparison and
    ``re.I`` part company, and the Latin i family is the specific hole:
    ``re.I`` matches ``i`` against U+0130 and U+0131, while
    ``'İ'.casefold()`` is ``i`` + a combining dot that is not a word character
    -- so ``İsmail`` tokenizes to ``i`` + ``smail`` and the bucket ``ismail``
    is never reached. Restricted to ASCII, folding and ``re.I`` agree exactly.

    Returns None for a name with no word run at all; the caller tests those
    against every line.
    """
    runs = _WORD_RUN.findall(name.casefold())
    return max(runs, key=len) if runs else None


@dataclass(frozen=True)
class CorpusIndex:
    """Corpus identifiers arranged for scanning many lines against many names.

    The scan is names x lines -- 1,031 names over 4,657 tracked lines when this
    was measured on 2026-08-11 -- and until #18 it built a fresh pattern inside
    that loop. ``re`` caches 512 compiled patterns, so 1,031 names thrashed the
    cache and recompiled nearly every name on nearly every line: ``--all`` took
    128s. It now takes under half a second.

    Those 1,031 are what the harvest produced *before* #12 added `prune_covered`;
    the same corpus now yields 563. Both figures are left standing because the
    cache argument is about the size that broke it, not today's size.

    Two changes, and only the second one matters. Compiling each name once is
    the obvious one and gets 128s to ~5s. The buckets are what make the layer
    effectively free: a line is only tested against the names filed under the
    words that line actually contains, which skips over 99% of the pairs.

    **The buckets are a filter, not a matcher.** Every candidate they let
    through is still tested with the same ``\\bname\\b`` pattern the naive scan
    used, so nested names are still reported separately and nothing about a
    finding changes. The only way this can be wrong is by skipping a pair that
    would have matched, which is what ``CorpusIndexing`` in the tests exists to
    rule out -- by generated input as well as by hand, because the hand-written
    cases missed one.
    """

    buckets: dict[str, tuple[IndexedName, ...]]
    # Names the buckets cannot speak for: no word run to file them under, or a
    # character outside ASCII. Tested against every line.
    unbucketed: tuple[IndexedName, ...]
    # Every name, for lines the buckets cannot speak for.
    everything: tuple[IndexedName, ...]
    dates: tuple[str, ...]

    def candidates(self, text: str) -> Sequence[IndexedName]:
        """The names that could appear in this line, in reporting order."""
        if _outside_ascii(text):
            return self.everything
        found = list(self.unbucketed)
        for token in set(_WORD_RUN.findall(text.casefold())) & self.buckets.keys():
            found.extend(self.buckets[token])
        return sorted(found, key=_by_name)


def build_index(names: set[str], dates: set[str]) -> CorpusIndex:
    buckets: dict[str, list[IndexedName]] = {}
    unbucketed: list[IndexedName] = []
    everything: list[IndexedName] = []

    for name in names:
        entry = IndexedName(name, re.compile(r"\b" + re.escape(name) + r"\b", re.I))
        everything.append(entry)
        token = None if _outside_ascii(name) else _required_token(name)
        if token is None:
            unbucketed.append(entry)
        else:
            buckets.setdefault(token, []).append(entry)

    # Sorted throughout: findings get printed, and set iteration order is not
    # stable across processes.
    return CorpusIndex(
        buckets={token: tuple(sorted(v, key=_by_name)) for token, v in buckets.items()},
        unbucketed=tuple(sorted(unbucketed, key=_by_name)),
        everything=tuple(sorted(everything, key=_by_name)),
        dates=tuple(sorted(dates)),
    )


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    match: str

    def render(self, show: bool) -> str:
        shown = self.match if show else _redact(self.match)
        return f"  {self.path}:{self.line}  [{self.rule}]  {shown}"


def _redact(text: str) -> str:
    return text[0] + "*" * (len(text) - 1) if text else ""


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=REPO_ROOT,
    ).stdout


def corpus_identifiers() -> tuple[set[str], set[str]]:
    """Patient names and date literals harvested from the gitignored corpus."""
    names: set[str] = set()
    dates: set[str] = set()

    index = REPO_ROOT / "scratch" / "name-index.json"
    if index.is_file():
        try:
            entries = json.loads(index.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            entries = []
        for entry in entries:
            if entry.get("name"):
                names.add(entry["name"].strip())
            for line in entry.get("win", []):
                candidate = line.strip()
                if _looks_like_a_name(candidate):
                    names.add(candidate)

    corpus = REPO_ROOT / "scratch" / "day-file-text"
    if corpus.is_dir():
        for path in corpus.glob("*.txt"):
            text = path.read_text(encoding="utf-8", errors="replace")
            dates.update(re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text))

    return kept_names(names), dates


def kept_names(harvested: set[str]) -> set[str]:
    """The harvested strings the corpus layer will actually scan for.

    One function rather than two calls at the call site, because the order is
    load-bearing and easy to get wrong: the length floor and the allowlist run
    **before** the pruning, so a string they remove is not available to cover
    anything. `prune_covered` says what that costs.
    """
    kept = {n for n in harvested if len(n) > 5 and n.lower() not in NOT_NAMES}
    return prune_covered(kept)


def prune_covered(names: set[str]) -> set[str]:
    """The harvested names, minus those that cannot refuse a line on their own.

    A name is dropped when a kept name matches inside it at word boundaries.
    That is sound in one step: a match of ``\\bouter\\b`` in a line carries the
    inner name at the same boundaries it has inside ``outer``, so the inner name
    matches that line too. Dropping ``outer`` changes which identifier a finding
    *names* -- to the shorter, more likely real one -- and cannot change whether
    the line is refused.

    **Measured 2026-08-11, because the reason is not the one it looks like.**
    Of 1031 harvested strings, 468 are dropped and **465 of those are case
    variants of a name that is kept** -- the harvest holds only 566 distinct
    names case-insensitively, and the corpus layer matches with ``re.I``, so
    every duplicate was always dead weight. Exactly **3** are the longer-phrase
    case above. So this is a deduplication that happens to subsume phrase
    nesting, not a filter aimed at note fragments, and it does **not**
    meaningfully shrink the surface #12 is about: the clinical-vocabulary false
    positives are two-word phrases with no name inside them, and every one of
    them survives.

    It goes some way toward #12's stated blocker without removing it. The
    objection to reasoning about the harvested class was that some entries hide
    a real patient name inside a longer phrase; those are exactly what gets
    dropped, and the issue counted two where this measures 3.

    **But the guarantee is narrower than "no survivor hides a name."** What
    holds is that no survivor contains another *surviving harvested* name, and
    `kept_names` applies the length floor and `NOT_NAMES` first -- so a phrase
    carrying a surname of five characters or fewer is covered by nothing and
    survives intact. No such survivor exists in the corpus today, which makes
    that a fact about this corpus and not a property of this code.

    **This prunes the harvest, not the matcher.** ``build_index`` is untouched
    and still reports nested names separately, because a nested name surviving
    here is one the corpus genuinely carries twice.

    Shortest first, so a name is only tested against names already kept. That
    terminates and cannot delete a whole coverage chain, because coverage
    composes: whatever a dropped name covered directly is still covered by the
    kept name that displaced it. Strictly shorter coverage bottoms out at a name
    nothing covers. Equal-length coverage means the two differ only in case --
    they cover each other -- and sorting on ``(len, name)`` breaks that tie so
    one survives rather than both being dropped.
    """
    survivors: list[IndexedName] = []
    for name in sorted(names, key=lambda n: (len(n), n)):
        if any(pattern.search(name) for _, pattern in survivors):
            continue
        survivors.append(
            IndexedName(name, re.compile(r"\b" + re.escape(name) + r"\b", re.I))
        )
    return {name for name, _ in survivors}


def _looks_like_a_name(text: str) -> bool:
    return bool(
        len(text) > 5
        and re.fullmatch(r"[A-Za-z][A-Za-z'\-]+(?: [A-Za-z][A-Za-z'\-.]+){1,2}", text)
    )


def declares_synthetic(text: str) -> bool:
    return SYNTHETIC_PRAGMA in text[:PRAGMA_SEARCH_CHARS]


def scan_text(text: str, path: str, index: CorpusIndex) -> list[Finding]:
    """Corpus layer always runs. Shape layer runs unless the file opts out."""
    findings: list[Finding] = []
    shapes_apply = not declares_synthetic(text)

    for number, line in enumerate(text.splitlines(), start=1):
        findings.extend(_scan_line(line, path, number, index, shapes_apply))
    return findings


def staged_paths() -> list[str]:
    out = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [p for p in out.splitlines() if p.strip()]


def staged_additions() -> dict[str, list[tuple[int, str]]]:
    """Added lines per file, with their line numbers in the new file."""
    return parse_diff(_git("diff", "--cached", "--unified=0", "--diff-filter=ACMR"))


def parse_diff(diff: str) -> dict[str, list[tuple[int, str]]]:
    """Added lines per file, keyed by path.

    A binary file contributes nothing: git prints ``Binary files ... differ``
    with no ``+++ b/`` header and no ``+`` lines, so the path never enters this
    map. That is what keeps ``scan_staged`` from pulling the 13 MB code set
    through ``git show`` on every commit, and ``test_phi_scan`` pins it down.
    """
    additions: dict[str, list[tuple[int, str]]] = {}
    path = ""
    number = 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            additions.setdefault(path, [])
        elif line.startswith("@@"):
            header = re.search(r"\+(\d+)", line)
            number = int(header.group(1)) if header else 0
        elif line.startswith("+") and not line.startswith("+++") and path:
            additions[path].append((number, line[1:]))
            number += 1
    return additions


def scan_staged(index: CorpusIndex) -> list[Finding]:
    findings: list[Finding] = []

    for path in staged_paths():
        if any(path.startswith(directory) for directory in PHI_DIRECTORIES):
            findings.append(Finding(path, 0, "phi-directory", path))

    for path, added in staged_additions().items():
        if any(path.startswith(directory) for directory in PHI_DIRECTORIES):
            continue  # already reported, and its contents must not be echoed
        whole = _git("show", f":{path}")
        shapes_apply = not declares_synthetic(whole)
        for number, text in added:
            findings.extend(_scan_line(text, path, number, index, shapes_apply))
    return findings


def _scan_line(
    text: str, path: str, number: int, index: CorpusIndex, shapes: bool
) -> list[Finding]:
    findings: list[Finding] = []
    for name, pattern in index.candidates(text):
        if pattern.search(text):
            findings.append(Finding(path, number, "corpus-name", name))
    for date in index.dates:
        if date in text:
            findings.append(Finding(path, number, "corpus-date", date))
    if shapes:
        for rule, pattern in SHAPE_RULES.items():
            for match in re.finditer(pattern, text):
                findings.append(Finding(path, number, rule, match.group(0)))
    return findings


def looks_binary(data: bytes) -> bool:
    """A NUL byte in the first block. The same test git itself uses.

    Deliberately not an extension list: this repo tracks a ``.sqlite`` today and
    an allowlist would need editing for whatever it tracks next, silently
    scanning the new thing as text until someone noticed.
    """
    return b"\x00" in data[:8192]


def read_text_if_text(path: Path) -> str | None:
    """The file's text, or None where it is binary and there is nothing to scan.

    Decoding a binary with ``errors="replace"`` and running the shape rules over
    it produces findings that are neither true nor false -- bytes that happened
    to match a phone number. Every finding this scanner prints has to be worth
    reading, or the hook becomes something people learn to skip.
    """
    data = path.read_bytes()
    if looks_binary(data):
        return None
    return data.decode("utf-8", errors="replace")


def scan_all(index: CorpusIndex) -> list[Finding]:
    findings: list[Finding] = []
    for path in _git("ls-files").splitlines():
        full = REPO_ROOT / path
        if not full.is_file():
            continue
        text = read_text_if_text(full)
        if text is None:
            continue
        findings.extend(scan_text(text, path, index))
    return findings


def main(argv: list[str]) -> int:
    show = "--show" in argv
    names, dates = corpus_identifiers()

    if not names and not dates:
        print(
            "phi-scan: no corpus under scratch/ -- the corpus layer is inactive, "
            "only PHI-shaped patterns will be caught.",
            file=sys.stderr,
        )

    index = build_index(names, dates)
    findings = scan_all(index) if "--all" in argv else scan_staged(index)
    if not findings:
        return 0

    print("\nphi-scan: refusing the commit. Standing rule 1: no PHI is ever committed.\n",
          file=sys.stderr)
    for finding in findings:
        print(finding.render(show), file=sys.stderr)
    print(
        "\nMatches are redacted. Re-run with --show to reveal them:\n"
        "    python tools/phi_scan.py --show\n"
        "\nIdentifiers become placeholders -- [PT], [DOB], [MRN]. If a value is\n"
        "genuinely synthetic and the file needs PHI-shaped literals, declare\n"
        f"'{SYNTHETIC_PRAGMA}' near the top of that file. That exempts the shape\n"
        "rules only; real corpus names and dates are still refused.\n",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
