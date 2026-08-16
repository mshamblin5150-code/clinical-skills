"""Grade the ``SPECIFICITY`` flags on a run of ``icd10-cpt``.

    python tools/specificity_scan.py <a run directory> [--show]

``fixtures/filled-anchor`` **C5** is this, and [#56] is why it exists. The skill's
step-3 template used to read ``SPECIFICITY: <complete | needs: ...>``, so a bare
``complete`` was compliant output -- and a run that never opened a code produced
the identical line to one that opened every code and found no axis left. The two
are indistinguishable on the page, which is the same silent-failure shape the
whole ``filled-anchor`` set exists for.

**Two tests, and neither needs a reader.**

- **A flag carries substance beyond its keyword.** ``complete`` and ``needs:``
  both fail; ``complete -- I10 has no further axis`` and ``needs: site`` both
  pass. The reason is the evidence that the check happened. Nobody writes *"Z98.51
  has no further axis"* without having looked at ``Z98.51``'s axes; anybody can
  write ``complete``. **This reaches both branches deliberately** -- a ``needs:``
  naming no axis is the same defect wearing the other keyword.
- **A descriptor saying "unspecified" may not read ``complete``.** The descriptor
  is the code set stating that an axis exists and that this code declines to name
  it, so ``M19.90 Unspecified osteoarthritis, unspecified site`` flagged
  ``complete`` contradicts the line above it. This is only checkable because C2
  already requires the descriptor be the **verbatim official string**; against a
  paraphrase it would prove nothing, which is worth knowing before trusting a
  clean scan over a run that has not been through C2.

**What it does not test, and cannot.** Whether a reason is a real check or a stock
phrase. ``L85.3`` has five siblings and ``Z98.51`` has one, and ruling that those
are different conditions rather than axes of one thing takes a reader --
``complete -- L85.3 has no further axis`` is true and no string test confirms it.
That residue is ``filled-anchor``'s R2, counted rather than enforced.

**Counts only by default, and that is load-bearing rather than conventional.** A
run directory lives under ``scratch/`` or ``output/`` and is a patient record. A
code with its descriptor is a diagnosis attached to an encounter, so nothing but
integers is printed unless ``--show`` asks; **``--show`` output is PHI** on
``harvest_review.py``'s terms -- read it, do not paste it.

**Exit status distinguishes not having scanned from having found nothing**, which
``guidelines_search.py`` is the precedent for: 0 when every flag passes, 1 when C5
fails, and **2 for every way of not having scanned** -- no directory, no
worksheets in it, no argument at all. A run whose output landed somewhere else
would otherwise report a clean set of flags and look like a pass.

Extractor limits worth knowing before quoting a number:

- An entry opens on a line beginning ``ICD-10``, ``CPT`` or ``HCPCS`` followed by
  a code and a descriptor, and a ``SPECIFICITY`` line is paired with the most
  recent one above it. A run that writes its worksheet some other way reads here
  as having flagged nothing, which is a floor on every count and **not** on the
  exit status -- the bare-flag test still fires on an unpaired flag, because it
  needs no descriptor.
- A **differential** entry is graded on nothing, and that is enforced rather than
  assumed. It is *supposed* to carry three parts and no ``SPECIFICITY`` line --
  but a run that writes one anyway would be graded against a descriptor reading
  ``..., unspecified`` **by design**, because the skill codes a differential at
  the unspecified level on purpose. So a flag on a ``NOT FOR ENTRY`` line is
  parsed, counted, and exempt from both tests; writing one is a C4 failure, which
  counts parts, and C5 firing as well would name the wrong row. The count is
  printed rather than dropped, because a non-zero there is worth going to look at.
- ``Other ...`` is not ``unspecified``. ``R06.89 Other abnormalities of breathing``
  says the finding fits no named code, not that the documentation is thin, and it
  reads ``complete`` with a reason like anything else. ``Other specified ...`` is
  likewise not ``not specified``.
- A flag whose value starts with neither keyword is counted as unrecognized and
  **fails nothing**. The template names two branches; policing a third would be
  this script inventing a rule the skill does not state.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from console_codec import use_utf8

# ``ICD-10  M19.90  Unspecified osteoarthritis, unspecified site``. The trailing
# ``NOT FOR ENTRY`` mark belongs to the differential shape and is not descriptor.
ENTRY = re.compile(
    r"(?mi)^[ \t]*(?:ICD-?10(?:-CM)?|CPT|HCPCS)[ \t]+"
    r"([A-Z0-9][A-Z0-9.]*)[ \t]+(.+?)[ \t]*$"
)
SPECIFICITY = re.compile(r"(?mi)^[ \t]*SPECIFICITY[ \t]*:[ \t]*(.*?)[ \t]*$")

# A code's own parts. These close an entry's header, so ``NOT FOR ENTRY`` is
# looked for above the first of them and never in the prose below.
FIELD = re.compile(r"(?mi)^[ \t]*(?:ANCHOR|SOURCE|SPECIFICITY|CONFIDENCE|NOTE)[ \t]*:")

# ``NOT FOR ENTRY`` at the end of any line of the entry's header, not only the
# code's own. **An official descriptor can run past a line** -- ``K27.9 Peptic
# ulcer, site unspecified, unspecified as acute or chronic, without hemorrhage or
# perforation`` is 96 characters -- and the mark then lands on the continuation. A
# single-line reading calls such an entry for-entry and then grades it on the
# descriptor test, which fires on ``..., unspecified`` **by design** in a
# differential. So the wrap produced a false C5 finding on exactly the shape the
# exemption below exists to protect. Found by a reader, in the run [#124]
# committed; no flag in that run was affected, because none of its wrapped
# differential entries carries a ``SPECIFICITY`` line at all.
NOT_FOR_ENTRY = re.compile(r"(?mi)[ \t]NOT FOR ENTRY[ \t]*$")

# The code set's own words for *an axis exists and this code does not name it*.
# ``Other specified ...`` is deliberately outside it -- see the module docstring.
UNSPECIFIED = re.compile(r"(?i)\bunspecified\b|\bnot specified\b")

# Anything alphanumeric after the keyword is substance. Judging whether it is a
# real check is R2's, and is not available to a string test.
SUBSTANCE = re.compile(r"[0-9A-Za-z]")

BARE = "bare-flag"
UNSPECIFIED_COMPLETE = "unspecified-complete"


@dataclass(frozen=True)
class Flag:
    """One ``SPECIFICITY`` line and the entry it belongs to."""

    code: str
    descriptor: str
    keyword: str
    remainder: str
    value: str
    for_entry: bool = True

    @property
    def has_substance(self) -> bool:
        return bool(SUBSTANCE.search(self.remainder))


@dataclass(frozen=True)
class Finding:
    """One flag failing one of C5's two tests."""

    kind: str
    code: str
    descriptor: str
    value: str


@dataclass(frozen=True)
class Scan:
    """Counts over a set of worksheets, plus the findings ``--show`` prints."""

    worksheets: int
    flags: int
    complete_flags: int
    needs_flags: int
    unrecognized_flags: int
    # A flag on a ``NOT FOR ENTRY`` line. C5 grades none of these, and the count is
    # reported rather than dropped: a differential is not supposed to carry one at
    # all, so a non-zero here is a C4 matter the reader should go looking at.
    not_for_entry_flags: int
    bare_flags: int
    unspecified_complete: int
    # One flag can fail both tests, so the two counters above sum higher than the
    # number of flags at fault. ``failing_flags`` is what the exit message says,
    # because C5 fails a *flag* and a reader who saw ``2`` where one line is wrong
    # would go looking for a second one.
    failing_flags: int = 0
    findings: tuple[Finding, ...] = ()


def _keyword(value: str) -> tuple[str, str]:
    """Split a flag value into its branch keyword and everything after it."""
    stripped = value.lstrip()
    lowered = stripped.lower()
    for keyword in ("complete", "needs"):
        if lowered.startswith(keyword):
            return keyword, stripped[len(keyword) :]
    return "", stripped


def read_flags(text: str) -> list[Flag]:
    """Every ``SPECIFICITY`` line in one worksheet, paired with its entry.

    Pairing is positional -- the most recent entry line above the flag -- because
    the skill's template puts the two three lines apart and nothing else in the
    output carries a code and its official descriptor on one line.
    """
    found = list(ENTRY.finditer(text))

    def header(index: int) -> str:
        """One entry's lines up to its first field line or the next entry.

        The span rather than the line, because a descriptor that wraps puts
        ``NOT FOR ENTRY`` on the continuation. Bounded on both sides so the mark
        cannot be borrowed from the entry below or from prose beneath the code.
        """
        start = found[index].start()
        end = found[index + 1].start() if index + 1 < len(found) else len(text)
        field = FIELD.search(text, start, end)
        return text[start : field.start() if field else end]

    entries = [
        (m.start(), m.group(1), m.group(2), not NOT_FOR_ENTRY.search(header(i)))
        for i, m in enumerate(found)
    ]
    flags: list[Flag] = []
    for match in SPECIFICITY.finditer(text):
        code, descriptor, for_entry = "", "", True
        for start, found_code, found_descriptor, entry_is_for_entry in entries:
            if start < match.start():
                code = found_code
                for_entry = entry_is_for_entry
                descriptor = NOT_FOR_ENTRY.sub("", found_descriptor)
            else:
                break
        keyword, remainder = _keyword(match.group(1))
        flags.append(
            Flag(
                code=code,
                descriptor=descriptor,
                keyword=keyword,
                remainder=remainder,
                value=match.group(1),
                for_entry=for_entry,
            )
        )
    return flags


def flag_findings(flag: Flag) -> list[Finding]:
    """C5's two tests, applied to one flag. A flag can fail both.

    **A flag on a ``NOT FOR ENTRY`` line is graded on neither.** A differential is
    coded at the unspecified level *on purpose* -- ``icd10-cpt`` says so and drops
    the specificity part from that shape entirely -- so an entry whose descriptor
    reads ``..., unspecified`` by design is not evidence that anybody failed to
    look. A run that writes a ``SPECIFICITY`` line there has already broken C4,
    which counts parts; firing C5 as well would name the wrong row and point at a
    descriptor the skill asked for.
    """
    found: list[Finding] = []
    if not flag.for_entry:
        return found
    if flag.keyword and not flag.has_substance:
        found.append(Finding(BARE, flag.code, flag.descriptor, flag.value))
    if flag.keyword == "complete" and UNSPECIFIED.search(flag.descriptor):
        found.append(Finding(UNSPECIFIED_COMPLETE, flag.code, flag.descriptor, flag.value))
    return found


def findings(flags: list[Flag]) -> list[Finding]:
    """Every finding across a set of flags, in flag order."""
    return [finding for flag in flags for finding in flag_findings(flag)]


def survey(per_worksheet: list[list[Flag]]) -> Scan:
    """Count across a run. Takes parsed flags rather than paths, so a ``Scan``
    never learns a filename -- a run directory's paths name the shift."""
    flags = [flag for sheet in per_worksheet for flag in sheet]
    found = findings(flags)
    return Scan(
        worksheets=len(per_worksheet),
        flags=len(flags),
        complete_flags=sum(1 for f in flags if f.keyword == "complete"),
        needs_flags=sum(1 for f in flags if f.keyword == "needs"),
        unrecognized_flags=sum(1 for f in flags if not f.keyword),
        not_for_entry_flags=sum(1 for f in flags if not f.for_entry),
        bare_flags=sum(1 for f in found if f.kind == BARE),
        unspecified_complete=sum(1 for f in found if f.kind == UNSPECIFIED_COMPLETE),
        failing_flags=sum(1 for flag in flags if flag_findings(flag)),
        findings=tuple(found),
    )


def format_report(scan: Scan, source: str, show: bool = False) -> str:
    """The report, as one string. Carries no code and no descriptor unless ``show``."""
    # Plain ASCII throughout, on ``icd10_lookup.py``'s reasoning: this prints to a
    # Windows console, where a middle dot outside cp1252 comes back as a question
    # mark and reads like corruption in the one output meant to be pasted.
    lines = [
        f"specificity scan over {source}",
        "",
        f"  worksheets read                  {scan.worksheets}",
        f"  SPECIFICITY flags                {scan.flags}",
        f"    complete                       {scan.complete_flags}",
        f"    needs                          {scan.needs_flags}",
        f"    neither keyword                {scan.unrecognized_flags}",
        f"    on a NOT FOR ENTRY line        {scan.not_for_entry_flags}",
        "",
        f"  C5 - flag carries no reason      {scan.bare_flags}",
        f"  C5 - complete on unspecified     {scan.unspecified_complete}",
        f"  C5 - flags at fault              {scan.failing_flags}",
    ]
    if show:
        lines += ["", "  findings (PHI - read, do not paste):"]
        for finding in scan.findings:
            lines.append(
                f"    {finding.kind:<22} {finding.code:<9} "
                f"SPECIFICITY: {finding.value}  [{finding.descriptor}]"
            )
    return "\n".join(lines)


def read_worksheets(directory: Path) -> list[str]:
    """The text of every worksheet in ``directory``, README excluded.

    A run's README is prose about the run; counting it would put a wrong
    denominator beside every figure below it.
    """
    return [
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(directory.glob("*.md"))
        if path.is_file() and path.stem.lower() != "readme"
    ]


def main(argv: list[str]) -> int:
    """``argv`` is the argument list without the program name."""
    args = [a for a in argv if not a.startswith("--")]
    show = "--show" in argv
    if not args:
        print("usage: specificity_scan.py <a run directory> [--show]", file=sys.stderr)
        return 2
    directory = Path(args[0])
    # The directory name, never the path: a run directory sits under ``scratch/``
    # or ``output/``, and its path names the shift and often the site.
    if not directory.is_dir():
        print(f"no directory named {directory.name}", file=sys.stderr)
        return 2
    worksheets = read_worksheets(directory)
    if not worksheets:
        print(f"no worksheets found in {directory.name}", file=sys.stderr)
        return 2
    scan = survey([read_flags(text) for text in worksheets])
    print(format_report(scan, source=directory.name, show=show))
    if scan.failing_flags:
        findings_count = len(scan.findings)
        detail = "" if findings_count == scan.failing_flags else f" ({findings_count} findings)"
        print(
            f"\n{scan.failing_flags} flag(s) fail fixtures/filled-anchor C5{detail}."
            " Re-run with --show to see which, and do not paste that output.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
