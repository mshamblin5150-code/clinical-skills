"""Compute each note's BMI from its own height and weight and name the codes it owes.

``clinical-note`` rules that a measurement of the patient's own body takes its
code (#70) and that a BMI from the note's own values is *not withheld* (#46).
Issue #1461 is the run where a delegated answer removed those codes from six
posted notes and every gate still passed, because none of them computed a BMI.
ADR 0309 ruling 2 is this module: the arithmetic on two numbers already in the
note, joined to the code set the skill already names.

``filled_vitals_census`` consumes ``read_note`` and owns the report, the row and
the exit status. This module has no command line, so it carries no console-codec
call.

**What it grades.** An adult (20 or older) at a BMI of 25.0 or above owes the
exact ``Z68`` band and an ``E66`` code from the matching family: ``E66.3`` for
25.0-29.9, and any obesity code other than ``E66.3`` at 30.0 or above. A patient
aged 2 through 19 is read through ``cdc_percentile``; where its band pairs with an
``E66`` code the note owes that ``Z68.5-`` band and the same ``E66`` family. A
normal or low BMI, and any age under 2, is reported and never graded, because
whether a ``Z68`` belongs at a normal BMI with no condition under it is the
coding-guidelines question ``clinical-note`` deliberately leaves open.

**Where it reads.** Height and weight are the first labeled values in the note
outside its tier block; the codes are read from the same region with every welded
``NOT CODED:`` refusal removed first, so a refused code never counts as written.
A note carrying a BMI, height or weight candidate that the strict reader cannot
turn into both inputs, or a graded-range BMI whose age or sex cannot be read, is
unread rather than clean.

The complete boundary of a clean result is ``bmi_codes.DECLARED_LIMITS``.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

import cdc_percentile
import run_grader


DECLARED_LIMITS = (
    (
        "first labeled height and weight",
        "Only the first labeled height and weight outside the tier block are read; an unlabeled vitals row is outside the population unless a BMI value marks the note as a candidate.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "first age and sex mention",
        "Age and sex come from the first mention in the note, so a relative named before the patient can be read as the patient.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "obesity code family",
        "At 30.0 or above any E66 code other than E66.3 satisfies the row, so the class-specific E66.81- choice stays a reader's.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
    (
        "code mentioned in prose",
        "A code written anywhere outside the tier block and outside a welded refusal counts as present, including a sentence that only discusses it.",
        run_grader.EvidenceDisposition.BEHAVIOR,
    ),
    (
        "normal and low BMI",
        "A BMI under 25.0, a pediatric band with no paired E66 code, and any age under 2 are reported and never graded.",
        run_grader.EvidenceDisposition.DECLARED_READING,
    ),
)

# A tier key at column 0 opens a tier line; indented lines continue it.
TIER_LINE = re.compile(r"^(?:FILLED|DERIVED|FLAG|GAPS|UNKNOWN|PROPOSED)\b")

_LABEL_GAP = r"[\s.:*]*"
HEIGHT = re.compile(
    rf"(?i)\b(?:ht|height)\b{_LABEL_GAP}"
    r"(?:(\d)\s*'\s*(\d{1,2}(?:\.\d+)?)\s*(?:\"|in\b|inches\b)?"
    r"|(\d{2,3}(?:\.\d+)?)\s*(in\b|inches\b|cm\b|\"))"
)
WEIGHT = re.compile(
    rf"(?i)\b(?:wt|weight)\b{_LABEL_GAP}(\d{{1,3}}(?:\.\d+)?)\s*(lbs?\b|pounds\b|kg\b)"
)
HEIGHT_CANDIDATE = re.compile(rf"(?i)\b(?:ht|height)\b{_LABEL_GAP}\d")
WEIGHT_CANDIDATE = re.compile(rf"(?i)\b(?:wt|weight)\b{_LABEL_GAP}\d")
BMI_CANDIDATE = re.compile(r"\bBMI\b[^\n\d]{0,12}\d")

AGE = re.compile(
    # ``N-year-old`` and ``N-month-old``; ``N yo`` and ``N mo``; ``age N`` and the
    # Medatrax ``Age + unit:`` field. Days and weeks are deliberately absent:
    # ``1 to 2 days old`` is how a note dates an illness, and an age that young
    # owes no BMI code anyway. A range -- ``aged 2 to 19``, ``ages 15-65`` -- is
    # a population a recommendation names, not this patient.
    r"(?i)\b(\d{1,3})[\s\-‐‑]*(years?|yrs?|months?|mos?)[\s\-‐‑]*old\b"
    r"|\b(\d{1,3})\s*(y/?o|m/?o)\b"
    r"|\bage(?:\s*\+\s*unit)?[\s:]*(\d{1,3})(?:\s*(years?|months?))?\b"
    r"(?!\s*(?:to|through|-|–)\s*\d)"
)
SEX = re.compile(
    r"(?i)\b(male|female|man|woman|boy|girl|gentleman|lady|transgender|nonbinary)\b"
)
_SEX_CODE = {
    "male": "male", "man": "male", "boy": "male", "gentleman": "male",
    "female": "female", "woman": "female", "girl": "female", "lady": "female",
}

REFUSAL = re.compile(r"NOT CODED:\s*[A-Z]\d{2}(?:\.[0-9A-Z]{1,4})?")
CODE = re.compile(r"(?<![A-Za-z0-9.])([A-Z]\d{2}(?:\.[0-9A-Z]{1,4})?)(?![0-9A-Za-z])")

OVERWEIGHT = "E66.3"


@dataclass(frozen=True)
class Reading:
    """One note's BMI reading. Holds no note text."""

    bmi: float | None = None
    # The codes the note owes: the exact Z68 band, and the E66 family as either
    # ``E66.3`` or ``obesity`` (any E66 code other than E66.3). Empty where the
    # BMI is outside the graded range or the note was not read.
    z68: str | None = None
    e66: str | None = None
    missing: tuple[str, ...] = ()
    candidate: bool = False

    @property
    def read(self) -> bool:
        return self.bmi is not None

    @property
    def graded(self) -> bool:
        return self.z68 is not None

    @property
    def unread(self) -> bool:
        return self.candidate and not self.read


def body_region(text: str) -> str:
    """The note with every tier line and its indented continuations removed."""
    kept: list[str] = []
    in_tier = False
    for line in text.splitlines():
        if TIER_LINE.match(line):
            in_tier = True
            continue
        if in_tier and line[:1] in (" ", "\t"):
            continue
        in_tier = False
        kept.append(line)
    return "\n".join(kept)


def _height_inches(match: re.Match[str]) -> float:
    if match.group(1) is not None:
        return int(match.group(1)) * 12 + float(match.group(2))
    value = float(match.group(3))
    return value / 2.54 if match.group(4).lower() == "cm" else value


def _weight_pounds(match: re.Match[str]) -> float:
    value = float(match.group(1))
    return value * 2.2046226 if match.group(2).lower() == "kg" else value


def bmi_of(height_in: float, weight_lb: float) -> float:
    """BMI rounded to one decimal, the precision every note writes it at."""
    return round(703 * weight_lb / height_in**2, 1)


def _most_stated(matches: list[re.Match[str]], key) -> re.Match[str] | None:
    """The most often stated value, the earliest of a tie, or ``None``."""
    if not matches:
        return None
    counts = Counter(key(match) for match in matches)
    best = max(counts.values())
    return next(match for match in matches if counts[key(match)] == best)


def age_years(region: str) -> tuple[float, int | None] | None:
    """The most often stated age, in years, with completed months where stated in months.

    The patient's age is the one a note repeats; a relative's age stated once
    loses to it. A tie goes to the earliest mention.
    """
    match = _most_stated(list(AGE.finditer(region)), _age_of)
    return None if match is None else _age_of(match)


def _age_of(match: re.Match[str]) -> tuple[float, int | None]:
    value = int(match.group(1) or match.group(3) or match.group(5))
    unit = (match.group(2) or match.group(4) or match.group(6) or "y").lower()
    if unit.startswith("m"):
        return (value / 12, value)
    return (float(value), None)


def adult_band(bmi: float) -> str:
    """The adult ``Z68`` band for a BMI already rounded to one decimal."""
    if bmi < 20:
        return "Z68.1"
    if bmi < 40:
        return f"Z68.{int(bmi)}"
    for ceiling, code in ((45, "Z68.41"), (50, "Z68.42"), (60, "Z68.43"), (70, "Z68.44")):
        if bmi < ceiling:
            return code
    return "Z68.45"


def _family(e66: str) -> str:
    return OVERWEIGHT if e66 == OVERWEIGHT else "obesity"


def owed(
    bmi: float, age: float, sex: str | None, months: int | None = None
) -> tuple[str, str] | None:
    """The ``Z68`` band and ``E66`` family owed, ``None`` where nothing is graded.

    Raises ``LookupError`` where the age needs the CDC table and no sex is read.
    """
    if age >= 20:
        if bmi < 25:
            return None
        return (adult_band(bmi), OVERWEIGHT if bmi < 30 else "obesity")
    if age < 2:
        return None
    # A whole-year age fills the midpoint month, as ``clinical-note`` directs.
    # Where no sex is read, both charts are consulted and graded only where
    # they agree, since a band both sexes share needs no sex to settle.
    bands = {
        (result.z68_code, result.e66_code)
        for result in (
            cdc_percentile.calculate_for_years(each, int(age), bmi)
            if months is None
            else cdc_percentile.calculate(each, months, bmi)
            for each in ((sex,) if sex else ("male", "female"))
        )
    }
    if len(bands) != 1:
        raise LookupError("pediatric BMI needs a sex where the charts disagree")
    z68, e66 = bands.pop()
    return None if e66 is None else (z68, _family(e66))


def written_codes(region: str) -> set[str]:
    return {match.group(1) for match in CODE.finditer(REFUSAL.sub(" ", region))}


def read_note(text: str) -> Reading:
    """Compute one note's BMI and name any code it owes and lacks."""
    region = body_region(text)
    candidate = bool(BMI_CANDIDATE.search(region)) or bool(
        HEIGHT_CANDIDATE.search(region) and WEIGHT_CANDIDATE.search(region)
    )
    height = HEIGHT.search(region)
    weight = WEIGHT.search(region)
    if height is None or weight is None:
        return Reading(candidate=candidate)
    bmi = bmi_of(_height_inches(height), _weight_pounds(weight))
    stated = age_years(region)
    sex_match = _most_stated(
        list(SEX.finditer(region)), lambda m: _SEX_CODE.get(m.group(1).lower())
    )
    sex = _SEX_CODE.get(sex_match.group(1).lower()) if sex_match else None
    if stated is None:
        # Under 25 owes nothing at any age, so only a graded-range BMI is unread.
        return Reading(bmi=None if bmi >= 25 else bmi, candidate=True)
    try:
        due = owed(bmi, stated[0], sex, stated[1])
    except (LookupError, ValueError):
        return Reading(candidate=True)
    if due is None:
        return Reading(bmi=bmi, candidate=True)
    z68, e66 = due
    codes = written_codes(region)
    missing: list[str] = []
    if z68 not in codes:
        missing.append(z68)
    e66_written = {code for code in codes if code.startswith("E66")}
    if not any(_family(code) == e66 for code in e66_written):
        missing.append(OVERWEIGHT if e66 == OVERWEIGHT else "an obesity E66 code")
    return Reading(bmi=bmi, z68=z68, e66=e66, missing=tuple(missing), candidate=True)
