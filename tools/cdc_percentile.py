"""Compute pediatric BMI-for-age percentiles and ICD-10-CM bands.

    python tools/cdc_percentile.py male 198 21.6
    python tools/cdc_percentile.py female 16 21.6 --age-years

The committed table is CDC's 2022 Extended BMI-for-Age data file.  CDC uses
the 2000 LMS calculation through the 95th percentile and the extended
half-normal calculation above it.  The table's selected percentile columns are
an independent answer key for ``tools/test_cdc_percentile.py``.

Age is accepted as completed months.  CDC's half-month row represents that
whole month: row 198.5 covers 198.0 through just under 199.0 months.  When an
encounter gives only whole years, ``--age-years`` deliberately fills the
midpoint month.  The report names that fill; it does not turn a guessed month
into a documented date of birth.

Source: https://www.cdc.gov/growthcharts/extended-bmi-data-files.htm
Downloaded file: https://www.cdc.gov/growthcharts/data/extended-bmi/bmi-age-2022.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

from console_codec import use_utf8

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHART = REPO_ROOT / "reference" / "cdc-bmi-for-age-2022.csv"
MIN_MONTHS = 24
MAX_MONTHS = 239
MIDYEAR_MONTH = 6

SEX_CODES = {
    "1": 1,
    "m": 1,
    "male": 1,
    "boy": 1,
    "2": 2,
    "f": 2,
    "female": 2,
    "girl": 2,
}
SEX_NAMES = {1: "male", 2: "female"}

Z68_DESCRIPTORS = {
    "Z68.51": "Body mass index [BMI] pediatric, less than 5th percentile for age",
    "Z68.52": "Body mass index [BMI] pediatric, 5th percentile to less than 85th percentile for age",
    "Z68.53": "Body mass index [BMI] pediatric, 85th percentile to less than 95th percentile for age",
    "Z68.54": "Body mass index [BMI] pediatric, 95th percentile for age to less than 120% of the 95th percentile for age",
    "Z68.55": "Body mass index [BMI] pediatric, 120% of the 95th percentile for age to less than 140% of the 95th percentile for age",
    "Z68.56": "Body mass index [BMI] pediatric, greater than or equal to 140% of the 95th percentile for age",
}

E66_BY_Z68 = {
    "Z68.51": (None, "underweight"),
    "Z68.52": (None, "healthy weight"),
    "Z68.53": ("E66.3", "overweight"),
    "Z68.54": ("E66.811", "obesity, class 1"),
    "Z68.55": ("E66.812", "obesity, class 2"),
    "Z68.56": ("E66.813", "obesity, class 3"),
}


@dataclass(frozen=True)
class ChartRow:
    sex: int
    age_months: float
    l: float
    m: float
    s: float
    sigma: float
    p5: float
    p85: float
    p95: float
    p120_of_p95: float


@dataclass(frozen=True)
class Result:
    sex: str
    completed_months: int
    chart_age_months: float
    bmi: float
    percentile: float
    percent_of_p95: float
    z68_code: str
    z68_descriptor: str
    e66_code: str | None
    weight_status: str
    age_month_was_filled: bool = False


def _number(row: dict[str, str], name: str) -> float:
    try:
        return float(row[name])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"CDC chart row has no usable {name} value") from error


@lru_cache(maxsize=None)
def load_chart(path: Path = DEFAULT_CHART) -> dict[tuple[int, float], ChartRow]:
    """Read CDC rows by sex and their published half-month age."""
    try:
        source = Path(path).open(encoding="utf-8-sig", newline="")
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"no CDC chart at {path}. It is committed to this repo."
        ) from error
    with source:
        rows = {}
        for item in csv.DictReader(source):
            row = ChartRow(
                sex=int(item["sex"]),
                age_months=_number(item, "agemos"),
                l=_number(item, "L"),
                m=_number(item, "M"),
                s=_number(item, "S"),
                sigma=_number(item, "sigma"),
                p5=_number(item, "P5"),
                p85=_number(item, "P85"),
                p95=_number(item, "P95"),
                p120_of_p95=_number(item, "pct120ofP95"),
            )
            rows[(row.sex, row.age_months)] = row
    return rows


def normalize_sex(sex: str | int) -> int:
    code = SEX_CODES.get(str(sex).strip().lower())
    if code is None:
        raise ValueError("sex must be male or female")
    return code


def _row(sex: int, completed_months: int) -> ChartRow:
    if not MIN_MONTHS <= completed_months <= MAX_MONTHS:
        raise ValueError("age in completed months must be 24 through 239")
    chart_age = completed_months + 0.5
    try:
        return load_chart()[(sex, chart_age)]
    except KeyError as error:
        raise ValueError(
            f"CDC chart has no row for sex {sex}, age {chart_age:g} months"
        ) from error


def _normal_cdf(z_score: float) -> float:
    return 0.5 * (1.0 + math.erf(z_score / math.sqrt(2.0)))


def _percentile(row: ChartRow, bmi: float) -> float:
    if bmi <= row.p95:
        if row.l == 0:
            z_score = math.log(bmi / row.m) / row.s
        else:
            z_score = ((bmi / row.m) ** row.l - 1.0) / (row.l * row.s)
        return 100.0 * _normal_cdf(z_score)
    # CDC's extended half-normal method: 90 + ten times the normal CDF of
    # distance above P95 in units of the row's sigma parameter.
    return 90.0 + 10.0 * _normal_cdf((bmi - row.p95) / row.sigma)


def _band(row: ChartRow, bmi: float) -> str:
    if bmi < row.p5:
        return "Z68.51"
    if bmi < row.p85:
        return "Z68.52"
    if bmi < row.p95:
        return "Z68.53"
    if bmi < row.p120_of_p95:
        return "Z68.54"
    if bmi < 1.4 * row.p95:
        return "Z68.55"
    return "Z68.56"


def calculate(sex: str | int, completed_months: int, bmi: float) -> Result:
    """Calculate one pediatric percentile and its FY2026 coding bands."""
    sex_code = normalize_sex(sex)
    if isinstance(completed_months, bool) or not isinstance(completed_months, int):
        raise ValueError("age in completed months must be a whole number")
    if not math.isfinite(bmi) or bmi <= 0:
        raise ValueError("BMI must be finite and greater than zero")
    row = _row(sex_code, completed_months)
    z68_code = _band(row, bmi)
    e66_code, status = E66_BY_Z68[z68_code]
    return Result(
        sex=SEX_NAMES[sex_code],
        completed_months=completed_months,
        chart_age_months=row.age_months,
        bmi=bmi,
        percentile=_percentile(row, bmi),
        percent_of_p95=100.0 * bmi / row.p95,
        z68_code=z68_code,
        z68_descriptor=Z68_DESCRIPTORS[z68_code],
        e66_code=e66_code,
        weight_status=status,
    )


def calculate_for_years(sex: str | int, age_years: int, bmi: float) -> Result:
    """Fill the midpoint month when the encounter supplies whole years only."""
    if isinstance(age_years, bool) or not isinstance(age_years, int):
        raise ValueError("age in years must be a whole number")
    result = calculate(sex, age_years * 12 + MIDYEAR_MONTH, bmi)
    return replace(result, age_month_was_filled=True)


def format_report(result: Result) -> str:
    age = f"{result.completed_months} completed months"
    if result.age_month_was_filled:
        age += " (filled midpoint month from the stated whole-year age)"
    e66 = result.e66_code or "none"
    return "\n".join(
        (
            f"sex: {result.sex}",
            f"age: {age}",
            f"CDC chart row: {result.chart_age_months:g} months",
            f"BMI: {result.bmi:g}",
            f"extended BMI-for-age percentile: {result.percentile:.2f}",
            f"percent of the 95th percentile: {result.percent_of_p95:.2f}%",
            f"Z68: {result.z68_code}  {result.z68_descriptor}",
            f"E66: {e66}  {result.weight_status}",
        )
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sex", help="male/female, M/F, or CDC code 1/2")
    parser.add_argument("age", type=int, help="completed months, or whole years with --age-years")
    parser.add_argument("bmi", type=float)
    parser.add_argument(
        "--age-years",
        action="store_true",
        help="age is whole years; fill its midpoint month and disclose the fill",
    )
    args = parser.parse_args(argv)
    try:
        result = (
            calculate_for_years(args.sex, args.age, args.bmi)
            if args.age_years
            else calculate(args.sex, args.age, args.bmi)
        )
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))
    print(format_report(result))
    return 0


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
