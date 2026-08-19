"""Refuse to commit PHI. Standing rule 1, enforced instead of remembered.

Installed as a pre-commit hook (see CLAUDE.md), so it binds every commit in this
clone regardless of who or what makes it.

Two layers, and the difference between them is the whole design:

- **Corpus layer.** Every patient name and every date literal appearing in the
  gitignored corpus under ``scratch/``. This is the layer that catches real PHI,
  and **nothing can exempt a file from it.**
- **Shape layer.** Things that look like PHI whatever the corpus says: a ``dob``
  token followed by a date, an SSN, a phone number, an MRN followed by digits, a
  US-style ``M-D-YY`` short date. A file may exempt itself from this layer only,
  by declaring ``phi-scan: synthetic`` near the top and alone on its line --
  which ``test_corpus_census`` does, because testing a date extractor requires
  date-shaped literals. Naming the pragma in a sentence, as this docstring is
  doing, declares nothing.

  This prose names the date shape rather than writing one out, here and in
  README.md and CLAUDE.md. All three used to give an impossible February date as
  the example; ``--all`` flagged CLAUDE.md for it and stayed silent about the
  other two, which had accidentally exempted themselves -- see
  ``SYNTHETIC_PRAGMA_LINE``. A file explaining a rule should not have to opt out
  of that rule to say what it does.

The asymmetry is deliberate. A file can say "my dates are invented"; no file can
say "my patient names are fine".

Known limits, stated so nobody mistakes this for a guarantee:

- ``git commit --no-verify`` bypasses it, as it bypasses any hook.
- The corpus layer is only as good as ``scratch/``. Where there is no corpus that
  layer finds nothing and the shape layer is all that remains -- but since #93
  that is a **refusal** rather than a warning, so it can no longer happen
  quietly. See `NOT_SCANNED` and `allows_no_corpus`.
- A patient name that appears nowhere in the corpus and is not date-shaped is
  caught by neither layer. All PHI here originates in the corpus, so this is a
  narrow hole, but it is a real one.
- **It has no concept of the account profile**, and that hole is wider than the
  one above. A site name, a preceptor, a payer mapping -- none of them is a
  patient name, a corpus date or a PHI shape, so nothing here matches one.
  Committed fixture notes have carried the clinician's practicum site names
  straight through this scanner; a reviewer who thought to grep is what found
  them, on every commit they survived. #50 ruled that **acceptable rather than
  unnoticed** and built no fourth layer, so do not refile it. What the ruling
  kept instead is the reasoning rather than the string, and it lives in
  ``fixtures/README.md`` as prose -- a fixture built from another skill's
  *output* inherits that skill's whole context, which is wider than any site
  list and is why the list was not written. The counts and the ruling's grounds
  are stated once each over there, not here.

  #212 found the same hole a second time, in ``reference/medatrax-fields.md``
  rather than in a fixture, and ruled 2026-08-18 that **this stays true**: no
  site layer, and the history keeps its copies, because a placement and a
  preceptor are facts about the clinician rather than about a patient. What
  changed is only the tree -- that file no longer carries the values, on a
  ground that is not de-identification at all. ``skills/setup-clinical-skills``
  already says the reference holds universal Medatrax behavior and the profile
  holds everything about the clinician, and per-account picklists sitting in
  the reference simply broke that split. So do not read a clean tree here as
  this scanner having gained a layer; it has not.
- **Binary files are skipped entirely**, so nothing inside ``reference/
  icd10cm-2026.sqlite`` is scanned. Its contents are the public ICD-10-CM
  release and carry no patient data. If a binary that could carry PHI is ever
  tracked here, this scanner will not say so.

Usage:

    python tools/phi_scan.py              # scan staged changes (what the hook runs)
    python tools/phi_scan.py --all        # scan every tracked file
    python tools/phi_scan.py --show       # reveal matches instead of redacting
    python tools/phi_scan.py --layers     # report which layers would run; scan nothing

Exit status, and the three values mean three different things:

===  ==========================================================================
0    Scanned with the corpus layer live, and found nothing.
1    Found something. The commit is refused.
2    **Did not scan** -- there is no corpus to scan against. Also refuses, and
     `NOT_SCANNED` says why that is a status rather than a warning.
===  ==========================================================================

``--layers`` exists for #86: the CI job prints it beside its own checkmark,
because in CI the corpus layer is dead on every run that will ever happen and a
clean scan there would otherwise read as coverage. It composes with ``--all``,
which reports a different path layer -- see `layer_report`. It reports and never
scans, so it is the one mode that always exits 0.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Sequence

from console_codec import use_utf8
from repo_root import scratch_root

# The tree being committed from -- this worktree. `_git` runs here and `scan_all`
# walks from here, and both are right: the subject of a commit is the tree making
# it. Deliberately **not** the corpus root; see below.
REPO_ROOT = Path(__file__).resolve().parent.parent

# The tree that holds `scratch/`, which is the main clone and never a worktree --
# `scratch/` is gitignored, so `git worktree` does not bring it. Splitting these
# two apart is issue #93: they were one constant, so in a worktree the corpus
# layer looked for patient names in a directory that had never existed there,
# found none, and let the commit through on the shape layer alone. That was the
# steady state for most commits made to this repo, because agents work in
# worktrees.
SCRATCH = scratch_root()

# Directories the PHI firewall in .gitignore already covers -- scratch/ is working
# files, output/ is finished notes and case studies. Staging anything under them
# means someone reached for `git add -f`.
PHI_DIRECTORIES = ("scratch/", "output/", "cases/", "patients/")

# Harvested strings a human has ruled on and judged to be real names. Under
# scratch/ because that is what it holds -- see `reviewed_names`.
REVIEWED_LEDGER = SCRATCH / "harvest-reviewed.json"

# **Exit 2 is "did not scan", and it is this repo's own convention rather than a
# new one** -- `guidelines_search.py` reserves it for every way of not having
# searched, and `specificity_scan`, `differential_scan`, `anchor_scan` and
# `block_scan` all copy it. #93 names the defect it fixes in one line of its own
# comments: *those two exit-0s mean different things and nothing in the status
# distinguishes them*. Now the status does.
#
# The hook needs no edit to honor it. `tools/hooks/pre-commit` already runs
# `phi_scan.py || status=1`, so any non-zero refuses the commit.
NOT_SCANNED = 2

# The two doors out of NOT_SCANNED, for the two environments where an absent
# corpus is expected rather than a fault: a clone that holds no patient material,
# and CI, where `scratch/` is gitignored PHI that must never reach a runner. See
# `allows_no_corpus` for why one is a config and the other a flag.
ALLOW_NO_CORPUS_FLAG = "--allow-no-corpus"
ALLOW_NO_CORPUS_CONFIG = "clinical.phiAllowNoCorpus"

# A file declaring this near its top is exempt from the SHAPE layer only.
SYNTHETIC_PRAGMA = "phi-scan: synthetic"
PRAGMA_SEARCH_CHARS = 4000

# The declaration has to be the whole line -- comment or docstring punctuation
# around it is fine, prose is not. Until 2026-08-11 this was a substring test, so
# any file that merely *explained* the pragma near its top exempted itself, and
# three did: this module, whose ``SYNTHETIC_PRAGMA`` assignment sat at char 726;
# README.md, whose PHI section reached it at char 2760; and test_icd10.py, at char
# 531. CLAUDE.md explains the same pragma at char 5647, past the window, and so was
# never exempt -- that inconsistency, files saying one thing and being treated two
# ways, is what gave it away. What the exemptions hid was the scanner's own
# documentation, not any real PHI -- the module docstring says what that was and
# how it was resolved.
#
# test_icd10.py is the one that shows what was wrong with the old rule. Its
# docstring says it "needs no ``phi-scan: synthetic`` pragma and deliberately does
# not claim one" -- and saying so was what claimed one. A file could not describe
# its own relationship to this scanner without changing it.
#
# The offsets are one-based over the LF form, measured 2026-08-11 against the
# commit before this one; all three files have been edited since, so only
# CLAUDE.md's still stands. They are approximate on purpose about which form they
# count, because the two paths in here disagree and it changed nothing: LF is what
# ``scan_staged`` reads from the index blob, while ``scan_all`` decodes the working
# tree verbatim, CRLF and all, putting the same three at 739, 2811 and 5730.
# Neither figure crosses the 4000 boundary the other stays inside.
#
# That same disagreement is why ``\r`` is allowed before the line end: this has to
# accept both forms of one file. Trailing-whitespace classes are spelled out rather
# than using ``\s``, which would match a newline and let the "line" span two.
#
# README.md and CLAUDE.md write the pragma mid-sentence inside backticks, so
# anchoring to the line excludes them without either file being reworded.
SYNTHETIC_PRAGMA_LINE = re.compile(
    r"(?m)^[ \t]*(?:#|//|\*|--)?[ \t]*" + re.escape(SYNTHETIC_PRAGMA) + r"[ \t\r]*$"
)

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
# why `tools/harvest_review.py` prints them for a human and rules on nothing.
#
# The block below is the first such review, run 2026-08-11 against the 28 strings
# outstanding at the time. 27 were vocabulary. **One was a real patient name**,
# and it went to scratch/harvest-reviewed.json rather than here -- which is the
# entire reason this list is not generated. The misspellings are the clinician's
# own and are kept verbatim: the harvester indexes the literal line, so a
# corrected spelling would exempt nothing.
NOT_NAMES = {
    "african american",
    "sore throat",
    "vaccs utd",
    "nkda",
    # Reviewed 2026-08-11, issue #12.
    "allergies codeine",
    "allergies seasonal.",
    "allergies seroqeul",
    "allergy amoxicillin",
    "allergy asa",
    "allergy avelox",
    "allergy pcn",
    "allergy to biaxin",
    "annual exam",
    "awaiting ultrasound",
    "enometrial ablation",
    "family hx copd",
    "friday fever yesterday.",
    "hospital follow up",
    "hx anxiety",
    "hx fibroids",
    "hx gerd",
    "hx seasonal allergies",
    "hx uti",
    "known to me",
    "meds none",
    "no allergies",
    "no dating ultrasound",
    "no meds",
    "nonadherent with medication",
    "pmh strep",
    "started yesterday eveneing",
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


def _load_json(path: Path, fallback):
    if not path.is_file():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def harvest_entries() -> list[dict]:
    """The raw name-index records, or [] where there is no corpus.

    **The index does not cover the corpus, and this is where that starts.** It
    carries one entry per encounter and holds 548 of the 551 the census counts;
    the three with no entry each put something other than the patient's name on
    the line after ``Note N``, which is the shape ``batch-shift`` step 3 warns a
    one-line parser loses. So a patient named *only* in one of those three is in
    no entry, no name of theirs is harvested, and the corpus layer never scans
    for it. Measured 2026-08-15, issue #63.

    Narrower than the hole the README states -- there the name is nowhere in the
    corpus, here it is in the corpus and the harvest did not reach it -- and it
    closes the same way, by rebuilding the index with a window rather than a
    line. **No generator for it is committed**, only this consumer and
    ``harvest_review.py``, so nothing here can rebuild it.
    """
    return _load_json(SCRATCH / "name-index.json", [])


def reviewed_names() -> set[str]:
    """Strings already ruled on by a human and judged to be real names (#12).

    Lives under ``scratch/`` because it is a list of patient names, so the
    firewall that covers the corpus covers it too -- gitignored, and refused by
    the path layer if anybody force-adds it. Absent on a fresh clone, which
    costs a re-review and never costs a refusal.
    """
    return {str(n).strip() for n in _load_json(REVIEWED_LEDGER, [])}


def harvested_names(entries: Sequence[dict]) -> set[str]:
    names: set[str] = set()
    for entry in entries:
        if entry.get("name"):
            names.add(entry["name"].strip())
        for line in entry.get("win", []):
            candidate = line.strip()
            if _looks_like_a_name(candidate):
                names.add(candidate)
    return names


def name_position_names(entries: Sequence[dict]) -> set[str]:
    """Strings the index itself puts where a name goes.

    ``win[0]`` is the name's own line -- 491 of 548 entries on 2026-08-11 have
    the ``name`` field there verbatim, which is also why the harvest carried 465
    case-variant duplicates before #12 pruned them. Everything at ``win[1..3]``
    is the shorthand that follows, and a string appearing only there has no
    positional evidence that it is a name at all.

    **548 is a count of entries, not of encounters.** The corpus holds 551, and
    ``batch-shift`` step 3 carries the reconciliation and what the gap costs;
    ``harvest_entries`` above says what it costs *here*. Both are worth the
    reminder because the same 548 sat in two skill files as the catalog's size
    until 2026-08-15. Issue #63.
    """
    found: set[str] = set()
    for entry in entries:
        if entry.get("name"):
            found.add(entry["name"].strip())
        window = entry.get("win", [])
        if window and _looks_like_a_name(window[0].strip()):
            found.add(window[0].strip())
    return found


def unreviewed_names(entries: Sequence[dict], reviewed: set[str]) -> set[str]:
    """Scanned-for strings with no name-position evidence and no ruling yet.

    The residual #12 is about. Each is either clinical vocabulary -- in which
    case it will refuse an innocent fixture line sooner or later -- or a real
    name the index only ever caught in passing. **Nothing here can tell which**,
    which is why `tools/harvest_review.py` prints them for a human instead of
    deciding. 28 of them on 2026-08-11.
    """
    positions = {n.casefold() for n in name_position_names(entries)}
    ruled = {n.casefold() for n in reviewed}
    return {
        name for name in kept_names(harvested_names(entries))
        if name.casefold() not in positions and name.casefold() not in ruled
    }


def corpus_identifiers() -> tuple[set[str], set[str]]:
    """Patient names and date literals harvested from the gitignored corpus."""
    dates: set[str] = set()
    names = harvested_names(harvest_entries())

    corpus = SCRATCH / "day-file-text"
    if corpus.is_dir():
        for path in corpus.glob("*.txt"):
            text = path.read_text(encoding="utf-8", errors="replace")
            dates.update(re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text))

    return kept_names(names), dates


def missing_corpus_sources() -> list[str]:
    """The halves of the corpus that are not on disk, named.

    **Two sources, and they fail independently** -- ``name-index.json`` carries
    the patient names, ``day-file-text/`` carries the date literals. Asking
    whether *the corpus* is present is the wrong question, and the first version
    of #93's fix asked it: it inferred deadness from ``not names and not dates``,
    so a tree holding one source and not the other reported a live layer, printed
    nothing and exited 0.

    **The dangerous direction is the name half**, because it is the half the
    shape layer cannot stand in for -- #93's own sentence, *shape rules catch an
    SSN or a ``dob`` token; they do not catch a patient's name*. With
    ``day-file-text/`` present and ``name-index.json`` gone, the conjunction was
    false, the scan ran on dates alone, and no patient name was checked at all.
    That is this ticket's defect one artifact narrower, reintroduced by its own
    fix and caught in review.

    Tested on disk rather than on the yield, because the two are not the same
    claim. ``harvest_entries`` falls back to ``[]`` for a file that is absent
    *and* for one that is malformed, and a corpus directory that genuinely holds
    no date literal is present rather than missing.
    """
    absent = []
    if not (SCRATCH / "name-index.json").is_file():
        absent.append("name-index.json")
    if not (SCRATCH / "day-file-text").is_dir():
        absent.append("day-file-text")
    return absent


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


def _pragma_window(text: str) -> str:
    """The file's first lines -- whole ones only.

    Truncating at a character count can cut through the middle of a line, and
    ``$`` matches the end of the string as readily as a newline, so a *prose*
    line beginning with the pragma whose remainder fell past the cut would have
    read as a bare declaration and silenced the shape layer. Constructing it
    takes a line starting at exactly the right offset, which is why this is an
    accident rather than an attack -- but the whole point of the line rule is
    that documenting the pragma cannot exempt a file, and this was a way for it
    to do so anyway.

    A cut line is dropped rather than repaired. When the window contains no
    newline at all the result is empty, which is correct: there is no complete
    line to judge. Text shorter than the window is returned untouched, so a
    pragma on an unterminated final line still counts.
    """
    head = text[:PRAGMA_SEARCH_CHARS]
    if len(text) > PRAGMA_SEARCH_CHARS:
        head = head[: head.rfind("\n") + 1]
    return head


def declares_synthetic(text: str) -> bool:
    """True where the file's own first lines declare the pragma, alone on a line.

    Two conditions, and both are about accidents rather than adversaries: near
    the top, so the declaration is where a reader looks, and on its own line, so
    a file cannot exempt itself merely by documenting the rule.
    """
    return SYNTHETIC_PRAGMA_LINE.search(_pragma_window(text)) is not None


def scan_lines(
    text: str, path: str, index: CorpusIndex, shapes: bool
) -> list[Finding]:
    """Every line of ``text``, with the shape layer decided by the caller.

    Split out of `scan_text` for ``tracker_scan``, and the split is the whole
    point rather than tidiness: a **file** may declare ``phi-scan: synthetic``
    and switch the shape layer off, and an issue body or a commit message may
    not. Those are text nobody can be trusted to have written under this repo's
    rules -- a ticket about the ``dob`` shape quotes one, which is exactly how
    the pragma would arrive there -- so that caller passes ``shapes=True`` and
    the decision is never read out of the text being scanned.

    The corpus layer is not a parameter, here or anywhere. No caller may switch
    it off.
    """
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        findings.extend(_scan_line(line, path, number, index, shapes))
    return findings


def scan_text(text: str, path: str, index: CorpusIndex) -> list[Finding]:
    """Corpus layer always runs. Shape layer runs unless the file opts out."""
    return scan_lines(text, path, index, shapes=not declares_synthetic(text))


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
    """Every **tracked** file, which is the whole of what a clean result covers.

    [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254).
    ``git ls-files`` is the index, so an untracked file is not in it -- and the
    honest form of a clean ``--all`` is *no tracked file carries PHI*, never
    *this tree carries none*. A file is invisible to this mode until the commit
    that makes it tracked.

    **Tracked is the right set to audit and that is not the same as being the
    whole tree.** ``--all`` exists to check what is already committed, and the
    staged paths are the pre-commit mode's job -- so between them nothing
    reaches a commit unread. What has no second net is **CI**, which runs this
    mode with nothing staged and two of three layers already dark.

    Its own blind spot is recorded rather than only reasoned about:
    ``spelling_scan``'s ``--all`` is this walk's twin, and ``CLAUDE.md`` records
    ``licence`` landing in a skill file because the staged scan had crashed and
    this mode could not see the file until the commit that made it tracked.
    """
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


def layer_report(
    names: set[str], dates: set[str], all_mode: bool, missing: Sequence[str] = (),
) -> list[str]:
    """What ran and what did not, one line per layer. #86 decision 2.

    **A layer that did not run is named as not having run, never omitted.** The
    omission is the whole defect this answers: a scanner that prints only its
    live layers reports a clean tree in exactly the configuration where the
    layer that catches real patient names is dead, and a checkmark over that
    reads as coverage. CI is permanently in that configuration -- ``scratch/``
    is gitignored PHI and must never reach a runner -- so the report is not an
    edge case there, it is every run.

    **Counts only, never an identifier**, on ``corpus_census.py``'s terms and
    for its reason: this is written to a CI step summary, which is a place a
    person pastes from.

    Takes the harvested sets rather than reading the corpus itself, so the
    caller's single ``corpus_identifiers()`` call answers for both the scan and
    the report. A second read could disagree with the first.

    ``all_mode`` rather than ``scan_all``, which is the name of a function in
    this module -- a parameter shadowing it reads as a call at a glance.
    """
    dead: list[str] = []

    # `--all` walks `git ls-files`, and every guarded directory is gitignored,
    # so no tracked path can ever be under one. The layer is inapplicable there
    # rather than clean -- the distinction this whole report exists to draw.
    if all_mode:
        path = "NOT RUN  -- --all walks tracked files; nothing can be staged from a gitignored directory"
        dead.append("path")
    else:
        path = "ACTIVE   -- " + ", ".join(PHI_DIRECTORIES)

    # **A half-present corpus is named as half-present, never as ACTIVE.** The
    # two sources fail independently and only one of them is patient names, so a
    # single ACTIVE/NOT RUN verdict has to lie about one of the three states.
    # `missing_corpus_sources` says why that mattered.
    if missing:
        lost = ", ".join(missing)
        harm = (
            "PATIENT NAMES ARE NOT CHECKED" if "name-index.json" in missing
            else "date literals are not checked"
        )
        verdict = "NOT RUN " if len(missing) > 1 else "PARTIAL "
        corpus = f"{verdict} -- no {lost} under scratch/; {harm}"
        dead.append("corpus")
    elif names or dates:
        corpus = f"ACTIVE   -- {len(names)} name(s), {len(dates)} date literal(s) from scratch/"
    else:
        corpus = "NOT RUN  -- no corpus under scratch/; PATIENT NAMES ARE NOT CHECKED"
        dead.append("corpus")

    lines = [
        f"phi-scan layers ({'--all' if all_mode else 'staged'}):",
        f"  path layer     {path}",
        f"  corpus layer   {corpus}",
        "  shape layer    ACTIVE   -- dob, SSN, phone, MRN, US-style short date",
    ]
    if dead:
        lines.append(
            f"  ** A clean result here is NOT \"no PHI\": the {' and '.join(dead)} "
            f"layer{'s' if len(dead) > 1 else ''} did not run. **"
        )
    return lines


def allows_no_corpus(argv: Sequence[str]) -> bool:
    """Whether this environment has declared that it has no corpus and never will.

    **Two callers, one condition, and they need different doors.** The hook is
    what runs this scanner at commit time, so a person committing has nowhere to
    put a flag -- they get the git config. CI invokes the scanner directly, so it
    gets the flag, written into ``checks.yml`` where anyone opening the file can
    read that the job knowingly runs a layer short.

    The config is read with ``--bool`` and unset is false, so the default posture
    is to refuse. **Per clone rather than per worktree, which is the granularity
    the fact actually has**: worktrees share their clone's ``.git/config``, and
    whether a machine holds patient material is a property of the clone. That is
    also the mechanism ``CLAUDE.md`` already spends once per clone on
    ``core.hooksPath``, so this is the repo's existing shape rather than a new one.

    Deliberately not an environment variable. An exported variable is ambient --
    set in a shell profile and forgotten, inherited by every process, invisible
    to anyone reading the repo, and needing to be set again for every agent
    session. ``.git/config`` is a file somebody chose to write.
    """
    if ALLOW_NO_CORPUS_FLAG in argv:
        return True
    return _git("config", "--bool", "--get", ALLOW_NO_CORPUS_CONFIG).strip() == "true"


def no_corpus_hint(missing: Sequence[str] = ()) -> str:
    """What to do about a dead corpus layer, naming both doors and neither vaguely."""
    return (
        "\nphi-scan: DID NOT SCAN. The corpus layer did not run, so no patient\n"
        "name was checked -- standing rule 1 cannot be enforced from here.\n"
        f"\nLooked in: {SCRATCH}\n"
        f"Absent:    {', '.join(missing) if missing else '(nothing)'}\n"
        "\nThat is resolved through the checkout this tree belongs to, which in a\n"
        "worktree is not this tree. If the path above is wrong, the resolution is\n"
        "the bug and not the corpus -- see tools/repo_root.py.\n"
        "\nIf this clone genuinely has no corpus and never will -- a fresh clone,\n"
        "or a machine that holds no patient material -- say so once:\n"
        f"\n    git config {ALLOW_NO_CORPUS_CONFIG} true\n"
        f"\nFor a single invocation, pass {ALLOW_NO_CORPUS_FLAG}. Either way the\n"
        "layer report above still prints: the exemption is about the exit status,\n"
        "not about the silence.\n"
    )


def main(argv: list[str]) -> int:
    show = "--show" in argv
    all_mode = "--all" in argv
    names, dates = corpus_identifiers()
    missing = missing_corpus_sources()

    # Reports and does not scan, so a CI job can print the layers as their own
    # step -- a clean scan prints nothing, which is the moment the reader most
    # needs to be told what was not looked at.
    if "--layers" in argv:
        for line in layer_report(names, dates, all_mode, missing):
            print(line)
        return 0

    # **The full report, not the one-line notice it replaces.** #93's finding is
    # that `no corpus under scratch/ -- the corpus layer is inactive` reads as a
    # fact about the environment, in the same register as the mirror's advisory
    # line, and scrolls past in the same output. `layer_report` already names
    # what is not being checked in the words that say so -- PATIENT NAMES ARE NOT
    # CHECKED -- and #86's own comment drew the corollary that the local hook
    # deserves it too. It costs one call.
    #
    # Printed before the scan rather than after, so a refusal below reads with
    # its coverage already stated.
    # **Any missing source, not both.** `missing_corpus_sources` carries why: the
    # conjunction let a tree with `day-file-text/` and no `name-index.json` scan
    # on dates alone and exit 0 in silence, which is checking no patient name at
    # all -- #93's harm, reintroduced by #93's fix.
    dead_corpus = bool(missing)
    if dead_corpus:
        for line in layer_report(names, dates, all_mode, missing):
            print(line, file=sys.stderr)

    index = build_index(names, dates)
    findings = scan_all(index) if all_mode else scan_staged(index)

    if not findings:
        if not dead_corpus or allows_no_corpus(argv):
            return 0
        print(no_corpus_hint(missing), file=sys.stderr)
        return NOT_SCANNED

    # **Findings beat a dead corpus, and the order is deliberate.** Returning
    # NOT_SCANNED here would file the strongest thing known about this tree under
    # the weakest heading -- `differential_scan.py`'s ruling, for its reason. The
    # layer report is already above, so the refusal reads as a floor rather than
    # as the whole.
    print("\nphi-scan: refusing the commit. Standing rule 1: no PHI is ever committed.\n",
          file=sys.stderr)
    for finding in findings:
        print(finding.render(show), file=sys.stderr)
    print(
        "\nMatches are redacted. Re-run with --show to reveal them:\n"
        "    python tools/phi_scan.py --show\n"
        "\nIdentifiers become placeholders -- [PT], [DOB], [MRN]. If a value is\n"
        "genuinely synthetic and the file needs PHI-shaped literals, put this on\n"
        "a line of its own near the top of that file:\n"
        f"\n    {SYNTHETIC_PRAGMA}\n"
        "\nAlone on the line -- mentioning it in a sentence declares nothing. That\n"
        "exempts the shape rules only; real corpus names and dates are still\n"
        "refused.\n",
        file=sys.stderr,
    )

    hint = review_hint(findings, unreviewed_names(harvest_entries(), reviewed_names()))
    if hint:
        print(hint, file=sys.stderr)
    return 1


def review_hint(findings: Sequence[Finding], unreviewed: set[str]) -> str:
    """The line pointing at `harvest_review`, or "" where there is nothing to say.

    Printed only on a ``corpus-name`` refusal, because that is the one moment the
    number is worth reading: a name matched, and somebody is deciding whether it
    is really a name. On every commit it would be noise, and this scanner cannot
    afford noise -- see `read_text_if_text` for the same argument.

    Takes the set and reports only its size. The hook's output has to stay safe
    to paste into a ticket, so this line may say how many and never which. #12.
    """
    waiting = len(unreviewed)
    if not waiting or not any(f.rule == "corpus-name" for f in findings):
        return ""
    return (
        f"{waiting} harvested strings have never been ruled on, and any of them\n"
        "can refuse a line that is not PHI at all. If this refusal is spurious,\n"
        "that list is where to look:\n"
        "    python tools/harvest_review.py\n"
    )


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
