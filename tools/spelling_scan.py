"""Standing rule 4, made runnable. American English, always.

The rule is in ``AGENTS.md`` and the table it points at is in
``skills/clinical-note/SKILL.md`` under *Conventions > Spelling*. This is that
table with a command in front of it, and ``test_spelling_scan`` parses the
skill's copy and asserts the two agree -- so the scanner cannot start holding a
different answer than the file a reader opens.

Usage:

    python tools/spelling_scan.py               # staged Markdown (what the hook runs)
    python tools/spelling_scan.py --all         # every tracked .md
    python tools/spelling_scan.py --record      # the run record, form by form
    python tools/spelling_scan.py <a run dir>   # grade a run's finished notes
    python tools/spelling_scan.py --quiet       # print nothing when clean

**A run directory is how the rule gets exercised.** Writing the rule down does
not demonstrate that `clinical-note` obeys it, and the only thing that does is a
run over the same encounters that emits none of the forms. Point this at the
run's output directory. It reads notes and prints no note text, so what it
reports is safe to paste even though what it read is a patient record.

**A mention is not a use, and the discriminator is the code span.** Naming a
wrong spelling in order to rule against it is how the rule gets written down at
all, and every such mention in this repo -- the table itself, ``AGENTS.md``,
``corpus_census``'s comment about ``apnoea`` -- is already written inside
backticks. So a form in a code span is being reported and a form in running
prose is being used, and no file needs a pragma.

**That is deliberately not ``phi_scan``'s shape.** Its ``phi-scan: synthetic``
exempts a whole file, and for a while two files earned the exemption merely by
explaining it. Nothing here can exempt itself: the unit is the span, not the
file, and a British spelling written into prose is a finding in the file that
documents the rule as readily as anywhere else.

**One exemption, and it is a directory rather than a declaration.**
``fixtures/filled-anchor/notes/case-*.md`` is day-b run 1 byte for byte apart
from two redacted site names, and the British spellings that run emitted are
the evidence for issue #73. **How many is ``--record``'s to say and is not
written here** -- adding a form to the table moves that count without moving
the record, which happened twice on 2026-08-18. Editing them would falsify the
record, so they are **counted and reported, never
refused** -- and the count is what ``test_spelling_scan`` pins, so a quiet tidy
fails a test instead of voiding an argument. The record's own ``README.md`` is
not in the exemption: it is prose about the record and takes the mention rule
like any other prose.

**Findings name the table's entry, never the bytes matched.** A note is a patient
record, so a scanner that echoed the line it matched would have output nobody
could paste into a ticket. What prints is a path, a line number and the entry
this module already contains -- the same discipline ``corpus_census.py`` keeps,
and the reason there is no ``--show``.

Known limits, stated so nobody reads this as the rule itself:

- **Markdown only.** Standing rule 4 reaches commit messages, filenames and
  ticket text, and this scans none of them. What it scans is every tracked
  ``.md``, which is the notes, the fixtures, the skills and the prose about them.
- **It holds the table, not the language.** The ``-ise`` family beyond
  ``catheterise``, and every British form nobody has written here yet, are out.
  A scan that comes back clean means no *listed* form was used. **Since #278
  that is on the page as well as here**, in ``vocabulary_covered`` and beside
  every clean line -- ``licence`` and ``manoeuvres`` were written into skill
  files in one commit minutes apart and only the listed one was reported.
- Advisory in the pre-commit hook, and deliberately: a spelling is not worth
  refusing a commit over. **It is not the only advisory check and standing rule
  1 is not the only refuser** -- ``threshold_sheet.py`` has refused a staged
  ``reference/thresholds/*.md`` since #83, and this docstring asserted
  otherwise for long enough to be the fourth surviving copy of a claim
  ``AGENTS.md`` and ``CLAUDE.md`` had already corrected. #278.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Iterable, NamedTuple

from console_codec import use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent

# The run record. Its README is not included -- see the module docstring.
EVIDENCE_PREFIXES = ("fixtures/filled-anchor/notes/case-",)

# *Conventions > Spelling* in skills/clinical-note/SKILL.md, transcribed. Parity
# is asserted rather than trusted; see `parse_skill_table`.
TABLE = {
    "dyspnoea": "dyspnea",
    "apnoea": "apnea",
    "anaemia": "anemia",
    "haemoglobin": "hemoglobin",
    "oedema": "edema",
    "diarrhoea": "diarrhea",
    "paediatric": "pediatric",
    "caesarean": "cesarean",
    "sulphate": "sulfate",
    "nebuliser": "nebulizer",
    "catheterise": "catheterize",
    "millilitre": "milliliter",
    "centimetre": "centimeter",
    "litre": "liter",
    "fibre": "fiber",
    "grey": "gray",
    "behaviour": "behavior",
    "favour": "favor",
    "colour": "color",
    "tumour": "tumor",
    "labelled": "labeled",
    "recognisable": "recognizable",
    "programme": "program",
    "licence": "license",
    "neighbour": "neighbor",
    "judgement": "judgment",
    "manoeuvre": "maneuver",
}

# Inflections whose stem changes, so the suffix rule below cannot reach them from
# the table's entry. Two, because two are what the corpus and the run record have
# produced -- this is not an attempt at English.
STEM_CHANGES = {
    "labelling": "labeling",
    "catheterisation": "catheterization",
}

FORMS = {**TABLE, **STEM_CHANGES}

# The same rule where it costs the most to get wrong: a clinician reading the
# other name has to translate it before they can check the dose. Named in the
# skill's prose rather than its table, so parity is asserted differently.
DRUGS = {
    "paracetamol": "acetaminophen",
    "adrenaline": "epinephrine",
    "salbutamol": "albuterol",
}

ALL_FORMS = {**FORMS, **DRUGS}

# Longest first so the alternation prefers `ally` over `al` and `es` over `s`.
# Only ever adds matches: every suffix here turns a listed form into another
# spelling of the same wrong word, and none of them turns it into a right one.
_SUFFIX = r"(?:ally|ing|es|ed|al|ly|s|d)?"

_PATTERNS = tuple(
    (form, american, re.compile(r"\b" + re.escape(form) + _SUFFIX + r"\b", re.I))
    for form, american in ALL_FORMS.items()
)

# The American form of each entry, for the run record's counterpart column only.
# Nothing scans for these: they are what a correct note says.
_COUNTERPARTS = tuple(
    (form, re.compile(r"\b" + re.escape(american) + _SUFFIX + r"\b", re.I))
    for form, american in ALL_FORMS.items()
)

# A run of backticks, its contents, and a run of backticks. Anything inside is
# being named. Kept to a single line: an inline span does not span lines, and a
# fence line reduces to nothing, which leaves the fenced block's own lines to be
# read as the prose they are.
_CODE_SPAN = re.compile(r"`+[^`\n]*`+")


class Finding(NamedTuple):
    path: str
    line: int
    form: str
    american: str

    def render(self) -> str:
        return f"  {self.path}:{self.line}  {self.form} -> {self.american}"


class Evidence(NamedTuple):
    """What the run record contains. Counted, never refused."""

    forms: dict[str, int]
    files: tuple[str, ...]

    @property
    def occurrences(self) -> int:
        return sum(self.forms.values())


class Report(NamedTuple):
    findings: list[Finding]
    evidence: Evidence


def strip_code_spans(line: str) -> str:
    """The line with every backticked span blanked out.

    Replaced with a space rather than removed, so two spans cannot be spliced
    into a word that was never written.
    """
    return _CODE_SPAN.sub(" ", line)


class _Tally:
    """Findings on one side, the run record's counts on the other.

    Both scan paths -- the working tree and the staged diff -- split their hits
    the same way, and the split is the whole of what this module decides. It
    lives here once so the two cannot start disagreeing about what the evidence
    directory is.
    """

    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.counts: dict[str, int] = {}
        self.record: list[str] = []

    def add(self, finding: Finding) -> None:
        if not is_evidence(finding.path):
            self.findings.append(finding)
            return
        self.counts[finding.form] = self.counts.get(finding.form, 0) + 1
        if finding.path not in self.record:
            self.record.append(finding.path)

    def report(self) -> Report:
        return Report(self.findings, Evidence(self.counts, tuple(self.record)))


def _matches(line: str) -> list[tuple[str, str]]:
    """``(form, american)`` for the line, in the order they are written.

    Overlapping matches keep the longer, which is what stops a form that
    contains another from being reported twice. Nothing in the table does today
    -- ``litre`` inside ``millilitre`` is excluded by the word boundary -- and
    the guard is here because the table grows.
    """
    found = []
    for form, american, pattern in _PATTERNS:
        for match in pattern.finditer(line):
            found.append((match.start(), match.end(), form, american))

    found.sort(key=lambda item: (item[0], -item[1]))
    kept: list[tuple[str, str]] = []
    reach = -1
    for start, end, form, american in found:
        if start < reach:
            continue
        kept.append((form, american))
        reach = end
    return kept


def scan_text(text: str, path: str) -> list[Finding]:
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        for form, american in _matches(strip_code_spans(line)):
            findings.append(Finding(path, number, form, american))
    return findings


def is_evidence(path: str) -> bool:
    return path.startswith(EVIDENCE_PREFIXES)


def is_markdown(path: str) -> bool:
    return path.lower().endswith(".md")


def scan(paths: Iterable[str], read: Callable[[str], str | None]) -> Report:
    tally = _Tally()
    for path in paths:
        if not is_markdown(path):
            continue
        text = read(path)
        if text is None:
            continue
        for finding in scan_text(text, path):
            tally.add(finding)
    return tally.report()


class RecordRow(NamedTuple):
    """One British form in the run record, against its American counterpart."""

    form: str
    american: str
    cases: tuple[tuple[str, int], ...]
    british: int
    american_count: int


def record_rows(paths: Iterable[str], read: Callable[[str], str | None]) -> list[RecordRow]:
    """The run record, form by form, with the American form's count beside it.

    The counterpart column is the point of this view rather than decoration.
    Eight British forms alone read as a run written in a British register; the
    same run writing ``cesarean`` eight times and ``caesarean`` once reads as
    drift, which is what issue #73 claims and what makes the record worth
    keeping.
    """
    british: dict[str, dict[str, int]] = {}
    counterpart: dict[str, int] = {}

    for path in paths:
        if not is_evidence(path):
            continue
        text = read(path)
        if text is None:
            continue
        case = Path(path).stem
        for finding in scan_text(text, path):
            british.setdefault(finding.form, {}).setdefault(case, 0)
            british[finding.form][case] += 1
        for form, pattern in _COUNTERPARTS:
            counterpart[form] = counterpart.get(form, 0) + len(pattern.findall(text))

    return [
        RecordRow(
            form,
            ALL_FORMS[form],
            tuple(sorted(cases.items())),
            sum(cases.values()),
            counterpart.get(form, 0),
        )
        for form, cases in sorted(british.items())
    ]


def render_record(rows: list[RecordRow]) -> list[str]:
    lines = [
        "spelling-scan: fixtures/filled-anchor/notes/ -- day-b run 1, byte for "
        "byte apart from two redacted site names. Issue #73.",
        "",
    ]
    for row in rows:
        where = ", ".join(f"{case} x{count}" for case, count in row.cases)
        lines.append(
            f"  {row.form:<13} {row.british:>2}   {where}"
            f"   ({row.american}: {row.american_count})"
        )
    lines.append("")
    lines.append(
        f"  {len(rows)} forms, {sum(r.british for r in rows)} occurrences, "
        f"{len({c for r in rows for c, _ in r.cases})} of the twelve notes."
    )
    lines.append("")
    lines.append(
        "These stay. Correcting them would falsify the record of what the run "
        "produced -- see the set's README."
    )
    lines.append(
        "This tally is bounded by that set: adding a form moves it without the "
        "record moving, which has happened. Issue #278; the instance is in "
        "skills/clinical-note/SKILL.md under Conventions."
    )
    lines.append(vocabulary_covered())
    return lines


def parse_skill_table(text: str) -> list[tuple[str, str]]:
    """The *Conventions > Spelling* table, as ``(british, american)`` pairs.

    The columns pair positionally within a row, which is how the table is
    written and read. A row whose two cells hold different numbers of entries is
    a table nobody could follow, so it raises rather than guessing.
    """
    section = re.search(r"(?ms)^### Spelling$(.*?)(?=^### |\Z)", text)
    if not section:
        raise ValueError("no '### Spelling' section in the skill file")

    pairs: list[tuple[str, str]] = []
    for line in section.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2:
            continue
        never = re.findall(r"`([^`]+)`", cells[0])
        always = re.findall(r"`([^`]+)`", cells[1])
        if not never and not always:
            continue
        if len(never) != len(always):
            raise ValueError(f"unpaired row in the Spelling table: {line.strip()}")
        pairs.extend(zip(never, always))
    return pairs


def _git(*args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(REPO_ROOT)) + args,
        check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    ).stdout


def tracked_markdown() -> list[str]:
    """Every **tracked** ``.md``, which is the whole of what a clean result covers.

    [#254](https://github.com/mshamblin5150-code/clinical-skills/issues/254).
    The name said *tracked* and nothing said what a pass means, which is the
    half of the statement that matters: ``git ls-files`` is the index, an
    untracked file is not in it, and the honest form of a clean ``--all`` is
    *no tracked file uses a listed form*.

    **This walk has the recorded instance rather than the hypothetical one.**
    ``CLAUDE.md`` carries it: ``licence`` landed in
    ``skills/practicum-case-study/SKILL.md`` with neither net catching it --
    the staged scan crashed inside ``staged_additions`` on a ``_git`` that had
    raised ``UnicodeDecodeError``, and this mode *"cannot see a file until the
    commit that makes it tracked"*. A commit is what turns this walk's blind
    spot into its coverage, which is one commit too late to refuse it.

    **Since [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)
    that statement is on the page as well as here**, in `scanned_population` and
    beside every clean line this scanner prints. A docstring is the page for a
    walk whose only reader opens the file; this one prints.
    """
    return [p for p in _git("ls-files", "*.md").splitlines() if p.strip()]


def read_tracked(path: str) -> str | None:
    full = REPO_ROOT / path
    if not full.is_file():
        return None
    return full.read_text(encoding="utf-8", errors="replace")


def markdown_under(targets: Iterable[Path]) -> list[str]:
    """Every ``.md`` under the given files and directories, as absolute strings.

    Absolute, so nothing here can collide with ``EVIDENCE_PREFIXES`` -- a run
    being graded is not the run record, whatever it is called or wherever it
    sits.
    """
    found: list[str] = []
    for target in targets:
        if target.is_dir():
            found.extend(str(p) for p in sorted(target.rglob("*.md")))
        elif target.is_file():
            found.append(str(target))
    return found


def read_file(path: str) -> str | None:
    full = Path(path)
    if not full.is_file():
        return None
    return full.read_text(encoding="utf-8", errors="replace")


def staged_additions() -> dict[str, list[tuple[int, str]]]:
    """Added lines per staged Markdown file, numbered in the new file.

    Added lines only, so a commit touching one paragraph is not answerable for
    every form already in the file.
    """
    diff = _git("diff", "--cached", "--unified=0", "--diff-filter=ACMR", "--", "*.md")
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


def scan_staged() -> Report:
    tally = _Tally()
    for path, added in staged_additions().items():
        if not is_markdown(path):
            continue
        for number, text in added:
            for form, american in _matches(strip_code_spans(text)):
                tally.add(Finding(path, number, form, american))
    return tally.report()


POPULATIONS = {
    "--all": ("every tracked .md -- an untracked file is not scanned until the "
              "commit that tracks it"),
    "staged": ("the added lines in staged .md -- an unstaged or untracked file "
               "is not scanned"),
    "paths": "the .md under the paths given -- nothing else in the tree is scanned",
}


def scanned_population(mode: str) -> str:
    """The set this run actually read, so a clean line cannot be read wider.

    [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258).
    ``spelling-scan: no listed British spelling found.`` was an unqualified
    clean result over ``git ls-files``, and #254 had already ruled that every
    such walk says what a clean result covers -- the statement went into
    `tracked_markdown`'s docstring, which is not the page a reader of this
    output is looking at.

    **This is the walk with the recorded instance rather than the hypothetical
    one.** ``CLAUDE.md`` carries it: ``licence`` landed in
    ``skills/practicum-case-study/SKILL.md`` because the staged scan had crashed
    and ``--all`` cannot see a file until the commit that makes it tracked. Both
    nets were down and both printed nothing that said so.

    **Advisory was argued in both directions and ruled toward saying so**
    (#258 open question 3). A line read past costs nothing; an unqualified clean
    line is what let the recorded instance through.

    **Every mode, including the paths one.** Naming only ``--all`` would teach a
    reader that the qualifier's absence elsewhere is a stronger claim, which is
    the defect one level down. And an unrecognized mode is a ``KeyError`` rather
    than a default, on `research_ledger.py`'s ruling for an unrecognized
    ``STATUS``: the value picks which claim is printed, so a third one would
    quietly print the exact unqualified line this ticket is about.

    Not shared with ``phi_scan``'s copy of this line, on `research_ledger.py`'s
    and `checks_ledger.py`'s terms: what transfers is the rule, and a shared
    helper would forbid the divergence two scanners with different populations
    are entitled to.

    **``--record`` needs none of this and got none**, which is a limit worth
    naming rather than an omission. Its first printed line already names the one
    directory it reports on, and it renders no clean verdict for a reader to
    read as a claim about the tree.
    """
    return f"spelling-scan: scanned {POPULATIONS[mode]}."


def vocabulary_covered() -> str:
    """The forms this run looked for, so a clean line cannot be read wider.

    [#278](https://github.com/mshamblin5150-code/clinical-skills/issues/278).
    #258 put the walked **population** on the page -- which files were read.
    That is one axis of what a clean result covers, and this scanner is weakest
    on the other: it holds a table rather than the language, so the honest form
    of a clean run is *no form on an N-entry table appears in the walked set*
    and it reads as *American English*.

    **The recorded instance is two forms in one commit, minutes apart.**
    ``licence`` was on the table and was reported; ``manoeuvres`` was not on it
    and was not, and was found only by going and looking by hand afterwards.
    Nothing the clean run printed said the second had never been looked for --
    which is the same silence #258 closed, one axis over.

    **Declared rather than widened**, which is the clinician's #254 ruling and
    the one he re-ruled here on 2026-08-19. ``manoeuvre`` is on the table now,
    because it was written in this repo and that is the table's growth rule --
    evidence, the way ``neighbour`` and ``judgement`` arrived. The productive
    families the ticket priced (``-ise``, ``-our``, ``-re``) were declined:
    every one of them fires on a correct word, and a scanner that refuses
    ``seizure`` and ``figure`` is worse than one that says what it holds.
    ``foetal`` and ``oesophag-`` stay off for the narrower reason that nobody
    has written them here, which is #104's open question and not this one's.

    **Derived from ``_PATTERNS`` rather than typed.** That tuple is what
    ``_matches`` iterates, so the printed number cannot disagree with what ran
    -- a hand-typed figure beside a table that grows is #143 with a schedule.

    **Its own row, on #258's terms.** Folding it into the population line would
    put two claims where a reader edits one, which is #220; and a reader who
    learns to read one qualifier reads the absence of the other as the stronger
    claim, which is the defect one level down.

    **The count names its own composition, and that is not decoration.** The
    table a reader opens in ``skills/clinical-note/SKILL.md`` holds fewer rows
    than this set has patterns -- the stem changes and the drug names are not
    rows of it -- so a bare total is a figure a reader counting the table gets a
    different answer to, which is the two-files-two-answers failure the parity
    test exists to close. The parts are read off the same dicts and reconcile to
    the total. **The figures are not restated in prose anywhere**, here or in
    ``CLAUDE.md``, on #143's terms.

    **``--record`` gets this same line, and calls it rather than holding a
    copy.** #258 ruled that view needs no *population* line, its first printed
    line naming the one directory it reports on. Its tally is still bounded by
    this set: adding a form has moved it while the twelve notes did not move at
    all. **The instance is stated once, in the skill's Conventions section**,
    which tells a reader to re-derive it with ``--record`` rather than quote it
    -- so printing it here would be the command quoting the sentence that says
    not to.
    """
    return (
        f"spelling-scan: checked {len(_PATTERNS)} listed forms and their "
        f"regular inflections -- {len(TABLE)} table rows, {len(STEM_CHANGES)} "
        f"stem changes, {len(DRUGS)} drug names. A form this set does not hold "
        "is not a finding."
    )


def render(report: Report, quiet: bool, mode: str) -> list[str]:
    lines: list[str] = []
    if report.findings:
        lines.append(
            "spelling-scan: British spelling in Markdown. Standing rule 4: "
            "American English, always."
        )
        lines.append("")
        lines.extend(finding.render() for finding in report.findings)
        lines.append("")
        lines.append(
            "A form named inside `backticks` is a mention and is not reported. "
            "The table is in skills/clinical-note/SKILL.md under Conventions."
        )
    elif not quiet:
        lines.append("spelling-scan: no listed British spelling found.")

    evidence = report.evidence
    if evidence.forms and not quiet:
        lines.append(
            f"spelling-scan: {len(evidence.forms)} forms, {evidence.occurrences} "
            f"occurrences across {len(evidence.files)} notes in "
            "fixtures/filled-anchor/notes/ -- a preserved run record, issue #73. "
            "Not findings."
        )

    # **Whether or not the run was clean, and last, so it qualifies everything
    # above it.** A finding is a floor rather than the whole -- so the walked
    # set is stated beside a report that found something exactly as it is beside
    # one that did not, which is `differential_scan.py`'s ordering one scanner
    # over. The one silence kept is `--quiet` **and** clean, and the reason is
    # narrower than the hook: what the ruling qualifies is a **printed clean
    # result**, and that pair prints none. There is nothing on the page for a
    # reader to read as a claim about the tree, which is not true of any other
    # combination here -- and it is the whole distinction, since `--quiet --all`
    # has no caller in this repo and the argument cannot rest on who runs it.
    # #258.
    if report.findings or not quiet:
        lines.append(scanned_population(mode))
        lines.append(vocabulary_covered())
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report British spelling in Markdown. Standing rule 4, "
                    "advisory -- this scanner refuses no commit.",
    )
    parser.add_argument(
        "paths", nargs="*", type=Path,
        help="files or directories to scan (default: the staged changes)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="scan every tracked .md rather than the staged changes",
    )
    parser.add_argument(
        "--record", action="store_true",
        help="report the preserved run record form by form, and exit",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="print nothing when clean; still exits non-zero when not",
    )
    args = parser.parse_args(argv)

    if args.record:
        for line in render_record(record_rows(tracked_markdown(), read_tracked)):
            print(line)
        return 0

    # The mode travels with the report because the report cannot say what it
    # walked -- `_Tally` sees findings and never the paths it was handed. Chosen
    # here, where the branch already is, rather than threaded through `scan`.
    if args.paths:
        mode, report = "paths", scan(markdown_under(args.paths), read_file)
    elif args.all:
        mode, report = "--all", scan(tracked_markdown(), read_tracked)
    else:
        mode, report = "staged", scan_staged()

    for line in render(report, args.quiet, mode):
        print(line)
    return 1 if report.findings else 0


if __name__ == "__main__":
    use_utf8()
    sys.exit(main())
