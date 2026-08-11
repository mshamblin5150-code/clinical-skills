"""Recompute the measured claims asserted in prose in skills/clinical-note/SKILL.md.

Four claims in that file are counts over the clinician's shorthand corpus. They are
load-bearing — rulings have turned on them — and until this script existed none of
them could be re-derived. Run it when a claim is about to be relied on again, or
when the corpus grows:

    python tools/corpus_census.py [path-to-day-files]

The corpus lives in ``scratch/``, which is gitignored PHI. **This script prints
counts only and never emits note text or a matched value**, so its output is safe
to paste into a ticket. ``format_report`` reads from a ``Census`` of integers and
never sees a note; the only non-numeric things it prints are its own fixed labels
and the corpus directory name. ``test_corpus_census.py`` guards it.

Extractor limits worth knowing before quoting a number:

- A note is a block introduced by a line starting ``Note <n>``. Text before the
  first such line is a day-file header and is dropped.
- Heights without the ``ht`` token are only caught in the ``5'10`` and ``36in``
  forms. A height written any other way reads as absent.
- A date of birth is the ``dob`` token or a bare date alone on its own line.
  A date embedded in prose is not counted, because visit dates and LMP dates
  outnumber birth dates in that position. Audited 2026-08-11 against every
  date literal in the 38 encounters the census reads as carrying neither an
  age nor a birth date: ten literals across nine of those encounters, every
  one of them a menstrual, follow-up, referral or administrative date, and
  none a birth date. Counting all nine encounters anyway is what lands at
  530 of 559 -- the reading the prose carried before 2026-08-11. Issue #9.
- ``dob`` welded straight to its date, with no space between token and value,
  is the shape that defeated ``\\bht\\b`` for ``ht5'7"`` and it would not match
  here either. There is no instance of it in the corpus as of 2026-08-11, so
  the alternative is not carried; this is the line to change if one appears.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# A note opens with "Note 1" at the start of a line. Case-insensitive: the corpus
# contains "NOte 3", and fixtures/day-a/shorthand/case-03.md preserves it.
NOTE_DELIMITER = re.compile(r"(?im)^\s*note\s*#?\s*\d+")

# Two to three digits either side, not touching another digit, slash, dot or dash.
# The negative look-around is what keeps a three-part date and "200/5ml" out; the
# plausibility range below is what keeps "10/10 pain" out.
BP_PAIR = re.compile(r"(?<![\d/.\-])(\d{2,3})\s*/\s*(\d{2,3})(?![\d/.\-])")
SYSTOLIC_RANGE = (70, 260)
DIASTOLIC_RANGE = (30, 160)

# Normal is below 130/80. The threshold is stated in SKILL.md next to the figure,
# because a different threshold gives a materially different percentage.
NORMAL_SYSTOLIC = 130
NORMAL_DIASTOLIC = 80

# The spelled-out "63 inches" form must be matched without relying on the "ht"
# token, because the token is sometimes mistyped: fixtures/day-a/shorthand/case-08
# preserves "hr 65 inches", and its README names that typo as a defect the set
# exists to find. A bare "165 in the office" is excluded by requiring either the
# full word or no space before "in".
#
# ``\bht\s*\d`` is the token run straight into its value -- he writes both
# "ht 62.5" and "ht5'7"". The trailing ``\b`` on the plain token cannot match the
# second, and neither can the feet-and-inches alternative, because there is no
# word boundary between the "t" and the "5". It is an extra alternative rather
# than a replacement, so nothing the plain token caught is lost; requiring the
# digit is what keeps "htn" out.
HEIGHT = re.compile(
    r"(?i)\b(?:ht|hgt|height)\b|\bht\s*\d"
    r"|\b\d\s*'\s*\d{1,2}|\b\d{2,3}\s*inch(?:es)?\b|\b\d{2,3}in\b"
)
WEIGHT = re.compile(r"(?i)\b(?:wt|weight)\b|\bwt\s*\d|\b\d{2,3}\s?lbs?\b")
OTHER_VITALS = re.compile(r"(?i)\b(?:hr|pulse|rr|spo2|sao2|temp)\b|\bt\s*\d{2,3}(?:\.\d)?\b")

# ``y\.?/?o\.?[mf]\b`` is the run-together form -- "45yof", "45y/om" -- where the
# sex letter is welded to the token and defeats the trailing ``\b`` after "o",
# the same shape that defeated ``\bht\b`` for "ht5'7"". It is an extra
# alternative, never a replacement. Requiring the sex letter is what keeps a
# stray "3 your" out; today the corpus's one instance is counted only because it
# sits alone on a line and AGE_AND_SEX_LINE catches it.
AGE_IN_YEARS = re.compile(
    r"(?i)\b\d{1,3}\s*(?:y\.?o\.?\b|y/o\b|y\.?/?o\.?[mf]\b"
    r"|years?\s*old\b|yrs?\s*old\b|years?\s*of\s*age\b)"
)
# Infants are written "8 months old" or "13 month male". A bare "[mf]" is not
# accepted here: it would read "x 3 days f/u" as a three-day-old.
AGE_UNDER_ONE = re.compile(
    r"(?i)\b\d{1,3}\s*(?:month|mo|week|wk|day)s?\s*(?:old\b|male\b|female\b)"
)
# "51 f" / "48f" / "61F" — always alone on its own line in this corpus. Anchoring
# to the line is what stops "t 98 F" reading as a 98-year-old and "toradol 10 m"
# as a ten-year-old. Audited 2026-08-11: exactly three digit+sex matches in the
# corpus sit anywhere other than alone on a line, and all three are decoys — two
# doses, and the "f/u" follow-up token taking the "f", which is the form the
# anchor most has to reject. No encounter loses an age to it.
AGE_AND_SEX_LINE = re.compile(r"(?im)^\s*\d{1,3}\s*(?:yo|y/o)?\s*[mf]\b\.?\s*$")

DOB_TOKEN = re.compile(r"(?i)\bd\.?o\.?b\.?\b")
DOB_BARE_LINE = re.compile(r"(?m)^\s*\d{1,2}[/-]\d{1,2}[/-](?:19|20)?\d{2}\s*$")

Reading = tuple[int, int]


def split_notes(text: str) -> list[str]:
    """Split a day file into encounters, dropping the day-file header."""
    return NOTE_DELIMITER.split(text)[1:]


def bp_readings(note: str) -> list[Reading]:
    """Every plausible blood pressure in a note, as (systolic, diastolic)."""
    readings: list[Reading] = []
    for match in BP_PAIR.finditer(note):
        systolic, diastolic = int(match.group(1)), int(match.group(2))
        if not SYSTOLIC_RANGE[0] <= systolic <= SYSTOLIC_RANGE[1]:
            continue
        if not DIASTOLIC_RANGE[0] <= diastolic <= DIASTOLIC_RANGE[1]:
            continue
        readings.append((systolic, diastolic))
    return readings


def is_normal_bp(reading: Reading) -> bool:
    systolic, diastolic = reading
    return systolic < NORMAL_SYSTOLIC and diastolic < NORMAL_DIASTOLIC


def has_bp(note: str) -> bool:
    return bool(bp_readings(note))


def has_height(note: str) -> bool:
    return bool(HEIGHT.search(note))


def has_weight(note: str) -> bool:
    return bool(WEIGHT.search(note))


def has_other_vitals(note: str) -> bool:
    """Pulse, temperature, respiratory rate or oxygen saturation."""
    return bool(OTHER_VITALS.search(note))


def has_any_vital(note: str) -> bool:
    return has_bp(note) or has_height(note) or has_weight(note) or has_other_vitals(note)


def has_stated_age(note: str) -> bool:
    return bool(
        AGE_IN_YEARS.search(note)
        or AGE_UNDER_ONE.search(note)
        or AGE_AND_SEX_LINE.search(note)
    )


def has_dob(note: str) -> bool:
    return bool(DOB_TOKEN.search(note) or DOB_BARE_LINE.search(note))


@dataclass(frozen=True)
class Census:
    """Counts only. Nothing here can carry note text."""

    notes: int = 0
    with_bp: int = 0
    with_height: int = 0
    with_weight: int = 0
    with_other_vitals: int = 0
    with_no_vital: int = 0
    bp_and_weight_no_height: int = 0
    readings: int = 0
    readings_normal: int = 0
    with_stated_age: int = 0
    with_dob: int = 0
    with_both_age_and_dob: int = 0
    with_neither: int = 0

    @property
    def without_bp(self) -> int:
        return self.notes - self.with_bp

    @property
    def with_either_age_or_dob(self) -> int:
        return self.notes - self.with_neither

    @property
    def with_dob_instead_of_age(self) -> int:
        """A date of birth where no age is stated -- the "instead" in the claim."""
        return self.with_dob - self.with_both_age_and_dob


def survey(notes: list[str]) -> Census:
    bp_n = height_n = weight_n = other_n = no_vital_n = 0
    bp_weight_no_height_n = readings_n = readings_normal_n = 0
    age_n = dob_n = both_n = neither_n = 0

    for note in notes:
        bp, height, weight = has_bp(note), has_height(note), has_weight(note)
        other, age, dob = has_other_vitals(note), has_stated_age(note), has_dob(note)

        bp_n += bp
        height_n += height
        weight_n += weight
        other_n += other
        no_vital_n += not has_any_vital(note)
        bp_weight_no_height_n += bp and weight and not height

        for reading in bp_readings(note):
            readings_n += 1
            readings_normal_n += is_normal_bp(reading)

        age_n += age
        dob_n += dob
        both_n += age and dob
        neither_n += not (age or dob)

    return Census(
        notes=len(notes),
        with_bp=bp_n,
        with_height=height_n,
        with_weight=weight_n,
        with_other_vitals=other_n,
        with_no_vital=no_vital_n,
        bp_and_weight_no_height=bp_weight_no_height_n,
        readings=readings_n,
        readings_normal=readings_normal_n,
        with_stated_age=age_n,
        with_dob=dob_n,
        with_both_age_and_dob=both_n,
        with_neither=neither_n,
    )


def _pct(part: int, whole: int) -> str:
    return f"{round(100 * part / whole)}%" if whole else "n/a"


def format_report(census: Census, source: str, date: str) -> str:
    c = census
    # ASCII only: this output is read in a Windows console and pasted into tickets.
    lines = [
        f"corpus census - {source} - {date}",
        f"encounters: {c.notes}",
        "",
        'claim: "about 93% carry an age or a date of birth"',
        'claim: "age stated in 42%, a date of birth appears instead in 47%"',
        "  (the second was measured over a 353-note catalog, not this corpus)",
        f"  stated age            {c.with_stated_age:>5}  {_pct(c.with_stated_age, c.notes)}",
        f"  date of birth         {c.with_dob:>5}  {_pct(c.with_dob, c.notes)}",
        f"  dob and no age        {c.with_dob_instead_of_age:>5}  "
        f"{_pct(c.with_dob_instead_of_age, c.notes)}",
        f"  both                  {c.with_both_age_and_dob:>5}  "
        f"{_pct(c.with_both_age_and_dob, c.notes)}",
        f"  either                {c.with_either_age_or_dob:>5}  "
        f"{_pct(c.with_either_age_or_dob, c.notes)}",
        f"  neither               {c.with_neither:>5}  {_pct(c.with_neither, c.notes)}",
        "",
        'claim: "transcription is all-or-nothing" (Filled vitals and body measurements)',
        f"  no vital at all       {c.with_no_vital:>5}  {_pct(c.with_no_vital, c.notes)}",
        f"  blood pressure        {c.with_bp:>5}  {_pct(c.with_bp, c.notes)}",
        f"  height                {c.with_height:>5}  {_pct(c.with_height, c.notes)}",
        f"  weight                {c.with_weight:>5}  {_pct(c.with_weight, c.notes)}",
        f"  pulse/temp/rr/spo2    {c.with_other_vitals:>5}  "
        f"{_pct(c.with_other_vitals, c.notes)}",
        f"  BP + weight, no ht    {c.bp_and_weight_no_height:>5}",
        "",
        f'claim: "half the blood pressures he transcribes are below '
        f'{NORMAL_SYSTOLIC}/{NORMAL_DIASTOLIC}"',
        f"  readings              {c.readings:>5}",
        f"  normal                {c.readings_normal:>5}  "
        f"{_pct(c.readings_normal, c.readings)}",
    ]
    return "\n".join(lines)


def read_corpus(directory: Path) -> list[str]:
    notes: list[str] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() in (".txt", ".md") and path.is_file():
            notes.extend(split_notes(path.read_text(encoding="utf-8", errors="replace")))
    return notes


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    directory = Path(argv[1]) if len(argv) > 1 else repo_root / "scratch" / "day-file-text"
    if not directory.is_dir():
        print(f"no corpus at {directory}", file=sys.stderr)
        return 1
    notes = read_corpus(directory)
    if not notes:
        print(f"no notes found in {directory}", file=sys.stderr)
        return 1
    today = __import__("datetime").date.today().isoformat()
    print(format_report(survey(notes), source=directory.name, date=today))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
