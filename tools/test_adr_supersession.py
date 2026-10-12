"""Bind declared ADR supersessions in both directions; see DECLARED_LIMITS.

Grammar: an optional exact ``## Supersedes`` section contains hyphen bullets,
each beginning with a relative ``[ADR NNNN](NNNN-slug.md)`` link followed by
``ruling N,`` and explanatory prose. Indented continuation lines are joined.
A marker is a paragraph beginning ``*Superseded YYYY-MM-DD.*`` beneath a
recognized ruling heading or numbered ruling item using ``adr_read``'s grammar.
It contains a quoted span, the same relative ADR link
followed by ``ruling N``, and an account of what survives. The account's truth
is read at review, not inferred from supersession verbs.

A wholly withdrawn record takes ADR 0343's whole-record form instead: the
bullet reads ``every ruling,`` (optionally ``every ruling except ruling N,``)
in place of ``ruling N,``, and its one marker is a paragraph above the record's
first ``##`` heading that says the same ``every ruling`` phrase, including any
exception, with the same quoted span and link requirements.
"""

from __future__ import annotations

import json
import re
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from adr_read import ruling_attributions, ruling_ordinals
from adr_supersession_population import classification_findings, derive_population, derive_records, legacy_marker_findings
from markdown_read import paragraphs, unfenced_lines
from prose_bind import NAMING, bind


CUTOFF = 0
CLASSIFICATION_REPORT = Path(__file__).resolve().parent.parent / "docs" / "adr" / "supersession-classification-1518.json"


def unsure_remainder(path=CLASSIFICATION_REPORT, *, legacy=False) -> int | None:
    """Read the historical reader remainder instead of copying a prose count."""
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        if legacy:
            return len(report.get("unresolved_legacy_markers", []))
        return sum(pair["classification"] == "unsure" for pair in report["pairs"])
    except (OSError, ValueError, TypeError, KeyError):
        return None


DECLARED_LIMITS = (
    "An overturning the author never declared is outside this binding.",
    "Whether a marker's account of what survives is true is a review reading.",
    f"The historical classification's unsure-pair unread remainder is {unsure_remainder()}; its source is supersession-classification-1518.json, not a completed supersession reading.",
    "Only the documented relative-link, bullet, paragraph, and adr_read ruling grammar is read; alternative Markdown forms are not certified.",
    f"The unattributed legacy-marker unread remainder is {unsure_remainder(legacy=True)}; exact retained source and the committed manifest bind these exceptions, and available Git history independently verifies them.",
)
LINK = r"\[ADR (\d{4})\]\((\d{4}-[^()\s]+\.md)\)"
DECLARATION = re.compile(r"^- " + LINK + r"\s+ruling (\d+),\s+(.+)$")
EVERY = r"every ruling(?: except rulings? (\d+(?:(?:, | and |, and )\d+)*))?"
WHOLE_DECLARATION = re.compile(r"^- " + LINK + r"\s+" + EVERY + r",\s+(.+)$")
WHOLE_PHRASE = re.compile(r"\b" + EVERY + r"\b", re.IGNORECASE)


def whole_record(exceptions: str | None) -> tuple[str, frozenset[int]]:
    """The ruling key of ADR 0343's whole-record form, exceptions included."""
    return ("every", frozenset(int(n) for n in re.findall(r"\d+", exceptions or "")))


def shown(ruling) -> str:
    """Name a declaration key the way its finding should read."""
    if isinstance(ruling, int):
        return f"ruling {ruling}"
    kept = sorted(ruling[1])
    return "every ruling" + (f" except ruling {', '.join(map(str, kept))}" if kept else "")
MARKER_LINK = re.compile(LINK + r"\s+ruling (\d+)\b")
OPENING = re.compile(r"^\*Superseded (\d{4}-\d{2}-\d{2})\.\*\s+(.+)$")


def supersession_findings(records: dict[str, str], report: dict | None = None, *, root: Path | None = None) -> tuple[str, ...]:
    """Grade an independently supplied complete ADR filename/text population.

    The cutoff belongs to the overturning record, so an old target can still
    owe a marker for a new declaration. This seam writes nothing.
    """
    findings, unresolved = legacy_marker_findings(report or {}, records, root=root)
    declarations: set[tuple[str, str, object]] = set()
    markers: set[tuple[str, str, object]] = set()
    for name, text in sorted(records.items()):
        text = "\n".join(unfenced_lines(text))
        if int(name[:4]) < CUTOFF:
            continue
        section = re.search(r"^## Supersedes\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if section is None:
            continue
        bullets = re.split(r"\n(?=- )", section.group(1).strip())
        for bullet in bullets:
            joined = " ".join(line.strip() for line in bullet.splitlines())
            parsed = DECLARATION.fullmatch(joined)
            whole = None if parsed else WHOLE_DECLARATION.fullmatch(joined)
            found = parsed or whole
            if found is None or found.group(1) != found.group(2)[:4]:
                findings.append(f"{name}: unread Supersedes declaration")
                continue
            if whole:
                key = whole_record(whole.group(3))
                if key[1] - set(ruling_ordinals(records.get(whole.group(2), ""))):
                    findings.append(f"{name}: {whole.group(2)} excepts an absent ruling")
                declarations.add((name, whole.group(2), key))
            else:
                declarations.add((name, parsed.group(2), int(parsed.group(3))))

    for name, text in sorted(records.items()):
        text = "\n".join(unfenced_lines(text))
        contexts = {row.line: row.number for row in ruling_attributions(text)}
        first_section = next(
            (index for index, line in enumerate(text.splitlines(), 1) if line.startswith("## ")),
            None,
        )
        for line_number, paragraph in paragraphs(text):
            ruling = contexts.get(line_number)
            if first_section is None or line_number < first_section:
                phrase = WHOLE_PHRASE.search(" ".join(paragraph.splitlines()))
                if phrase:
                    ruling = whole_record(phrase.group(1))
            if not paragraph.startswith("*Superseded"):
                continue
            if (name, paragraph) in unresolved:
                continue
            links = list(MARKER_LINK.finditer(paragraph))
            # Old targets with only old links belong to the repair, not this rule.
            if int(name[:4]) < CUTOFF and links and all(
                int(link.group(1)) < CUTOFF for link in links
            ):
                continue
            opening = OPENING.match(" ".join(paragraph.splitlines()))
            valid_date = False
            if opening:
                try:
                    date.fromisoformat(opening.group(1))
                    valid_date = True
                except ValueError:
                    pass
            if not valid_date or ruling is None or not links or not re.search(r'"[^"\n]+"', " ".join(paragraph.splitlines())):
                findings.append(f"{name}: unread supersession marker")
                continue
            for link in links:
                if link.group(1) != link.group(2)[:4]:
                    findings.append(f"{name}: marker link number disagrees with path")
                    continue
                if int(link.group(3)) not in ruling_ordinals(records.get(link.group(2), "")):
                    findings.append(f"{name}: marker links an absent overturning ruling")
                markers.add((link.group(2), name, ruling))

    for declaring, target, ruling in sorted(declarations - markers, key=str):
        findings.append(f"{declaring}: {target} {shown(ruling)} has no matching marker")
    for declaring, target, ruling in sorted(markers - declarations, key=str):
        findings.append(f"{target}: {declaring} does not declare {shown(ruling)}")
    return tuple(findings)


class SupersessionBindingTests(unittest.TestCase):
    def legacy_fixture(self):
        original = '*Superseded grounding marked 2026-09-12.* The ground "Old words." was replaced by [ADR 0280](0280-new.md) ruling 1. The verdict stands.'
        normalized = original.replace('Superseded grounding marked', 'Superseded')
        source = '# Record\n\n## Ground\n\n' + original + '\n'
        report = derive_records([('0039-old.md', source.encode('utf-8'))])
        report['revision'] = 'a' * 40
        report['unresolved_legacy_markers'] = [{
            'record': '0039-old.md', 'original_marker': original,
            'normalized_marker': normalized, 'reason': 'No ratified ruling ordinal.',
            'follow_up': 12, 'source_text': source, 'source_sha256': report['records'][0]['sha256'],
        }]
        return {'0039-old.md': source.replace(original, normalized)}, report

    def test_exact_unattributed_legacy_marker_remains_unread_without_inventing_a_ruling(self):
        records, report = self.legacy_fixture()
        self.assertEqual(supersession_findings(records, report), ())
        self.assertTrue(supersession_findings(records))

    def test_unresolved_legacy_readback_refuses_forged_or_changed_evidence(self):
        import copy
        for mutation in ('forged_marker', 'source_hash', 'body_change', 'follow_up', 'missing_live', 'live_quote', 'extra_entry', 'numbered'):
            with self.subTest(mutation=mutation):
                records, report = self.legacy_fixture()
                row = report['unresolved_legacy_markers'][0]
                if mutation == 'forged_marker':
                    row['original_marker'] = row['original_marker'].replace('Old words.', 'Invented words.')
                    row['normalized_marker'] = row['normalized_marker'].replace('Old words.', 'Invented words.')
                    records['0039-old.md'] = records['0039-old.md'].replace('Old words.', 'Invented words.')
                elif mutation == 'source_hash':
                    row['source_text'] += 'New text.\n'
                elif mutation == 'body_change':
                    row['normalized_marker'] += ' Altered body.'
                    records['0039-old.md'] += ' Altered body.'
                elif mutation == 'follow_up':
                    del row['follow_up']
                elif mutation == 'missing_live':
                    records.clear()
                elif mutation == 'live_quote':
                    records['0039-old.md'] = records['0039-old.md'].replace('Old words.', 'Changed words.')
                elif mutation == 'extra_entry':
                    extra = copy.deepcopy(row)
                    extra['record'] = '0040-absent.md'
                    report['unresolved_legacy_markers'].append(extra)
                elif mutation == 'numbered':
                    records['0039-old.md'] = records['0039-old.md'].replace('## Ground', '## Ruling 1 — ground')
                self.assertTrue(legacy_marker_findings(report, records)[0])

    def test_declared_limits_are_named_without_copying_rows(self) -> None:
        self.assertEqual(bind(DECLARED_LIMITS, __doc__, mode=NAMING), ())

    def paired_records(self) -> dict[str, str]:
        return {
            "0280-new.md": '## Ruling 1 — new practice\n\nNew words.\n\n## Supersedes\n\n- [ADR 0135](0135-old.md)\n  ruling 8, its practice "Old words." The verdict stands.\n',
            "0135-old.md": '## Ruling 8 — practice\n\nOld words.\n\n*Superseded 2026-10-03.* The practice "Old words." is replaced by [ADR 0280](0280-new.md) ruling 1. The verdict stands.\n',
        }

    def test_declared_pair_is_green(self) -> None:
        self.assertEqual(supersession_findings(self.paired_records()), ())

    def test_committed_adr_population_is_bound(self) -> None:
        directory = Path(__file__).resolve().parent.parent / "docs" / "adr"
        records = {path.name: path.read_text(encoding="utf-8") for path in directory.glob("[0-9][0-9][0-9][0-9]-*.md")}
        self.assertTrue(any(int(name[:4]) >= CUTOFF for name in records))
        report = json.loads(CLASSIFICATION_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(supersession_findings(records, report, root=directory.parents[1]), ())

    def test_declaration_without_marker_is_red(self) -> None:
        records = {
            "0280-new.md": '## Supersedes\n\n- [ADR 0135](0135-old.md) ruling 8, its practice "Old words." The verdict stands.\n',
            "0135-old.md": '## Ruling 8 — practice\n\nOld words.\n',
        }
        self.assertTrue(any("no matching marker" in row for row in supersession_findings(records)))

    def test_marker_linking_a_record_declaring_nothing_is_red(self) -> None:
        records = self.paired_records()
        records["0280-new.md"] = '## Ruling 1 — new practice\n\nNew words.\n'
        self.assertTrue(any("does not declare ruling 8" in row for row in supersession_findings(records)))

    def test_old_corrected_opening_cannot_discharge_a_declaration(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace("*Superseded", "*Corrected")
        self.assertTrue(any("no matching marker" in row for row in supersession_findings(records)))

    def test_a_marker_under_the_wrong_target_ruling_is_red_in_both_directions(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace("## Ruling 8", "## Ruling 7")
        rows = supersession_findings(records)
        self.assertTrue(any("no matching marker" in row for row in rows))
        self.assertTrue(any("does not declare ruling 7" in row for row in rows))

    def test_a_missing_overturning_ruling_is_red(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace("ruling 1.", "ruling 9.")
        self.assertTrue(any("absent overturning ruling" in row for row in supersession_findings(records)))

    def test_the_cutoff_excludes_old_overturnings_but_not_old_targets(self) -> None:
        records = {name.replace("0280", "0279"): text.replace("0280", "0279") for name, text in self.paired_records().items()}
        with mock.patch(__name__ + ".CUTOFF", 280):
            self.assertEqual(supersession_findings(records), ())

    def test_old_records_are_bound_after_the_cutoff_is_lowered(self) -> None:
        records = {name.replace("0280", "0020"): text.replace("0280", "0020") for name, text in self.paired_records().items()}
        records["0135-old.md"] = records["0135-old.md"].replace("*Superseded", "*Corrected")
        self.assertTrue(any("no matching marker" in row for row in supersession_findings(records)))

    def test_historical_classification_covers_its_live_pair_population(self) -> None:
        report = json.loads(CLASSIFICATION_REPORT.read_text(encoding="utf-8"))
        live = derive_population(CLASSIFICATION_REPORT.parent)
        self.assertEqual(classification_findings(live, report, historical_coverage=True), [])

    def test_numbered_and_bold_ruling_items_carry_markers_in_declared_sections(self) -> None:
        for heading in ("## The decisions\n\n8. Practice", "## Ruled\n\n**8. Practice.**", "## Ruled\n\n**Ruling 8. Practice.**", "## Decision 8 — practice"):
            with self.subTest(heading=heading):
                records = self.paired_records()
                records["0135-old.md"] = records["0135-old.md"].replace("## Ruling 8 — practice", heading)
                self.assertEqual(supersession_findings(records), ())

    def test_numbered_items_in_a_measured_section_are_not_rulings(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace("## Ruling 8 — practice", "## Measured before ruling\n\n**8. Practice.**")
        self.assertTrue(any("unread supersession marker" in row for row in supersession_findings(records)))

    def test_each_shared_ruling_form_attributes_ruling_two_and_not_before_it(self) -> None:
        marker = '*Superseded 2026-10-03.* "Old words." is replaced by [ADR 0280](0280-new.md) ruling 1. The verdict stands.'
        for form in ("## Ruling 2 — practice", "## Decision 2 — practice", "## Ruled\n\n### 2. Practice", "## The decisions\n\n2. Practice", "## Ruled\n\n**2. Practice.**", "## Ruled\n\n**Ruling 2. Practice.**"):
            with self.subTest(form=form):
                records = self.paired_records()
                records["0280-new.md"] = records["0280-new.md"].replace("ruling 8,", "ruling 2,")
                first = form.replace("2", "1")
                second = form.split("\n\n", 1)[-1] if form.startswith(("## Ruled\n", "## The decisions\n")) else form
                records["0135-old.md"] = first + "\n\nUnrelated first ruling text.\n\n" + second + "\n\nOld words.\n\n" + marker + "\n"
                self.assertEqual(supersession_findings(records), ())
                records["0135-old.md"] = "## Ruled\n\n" + marker + "\n\n" + form + "\n\nOld words.\n"
                self.assertTrue(any("unread supersession marker" in row for row in supersession_findings(records)))

    def test_a_numbered_subheading_in_a_ruled_section_carries_a_marker(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace(
            "## Ruling 8 — practice", "## Ruled 2026-09-12\n\n### 8. Practice"
        )
        self.assertEqual(supersession_findings(records), ())

    def test_a_numbered_subheading_outside_a_ruled_section_carries_no_marker(self) -> None:
        records = self.paired_records()
        records["0135-old.md"] = records["0135-old.md"].replace(
            "## Ruling 8 — practice", "## Measured before ruling\n\n### 8. Practice"
        )
        self.assertTrue(
            any("unread supersession marker" in row for row in supersession_findings(records))
        )

    def whole_records(self) -> dict[str, str]:
        return {
            "0343-new.md": '## Ruling 1 \u2014 retired\n\nRetired.\n\n## Supersedes\n\n- [ADR 0106](0106-old.md)\n  every ruling except ruling 2, the record "Old title". Ruling 2 stands.\n',
            "0106-old.md": '# Old title\n\n*Superseded 2026-10-11.* Every ruling except ruling 2 in "Old title" is withdrawn by [ADR 0343](0343-new.md) ruling 1, so every ruling except ruling 2 is history. Ruling 2 stands.\n\n## Ruled\n\n### 1. First\n\nWords.\n\n### 2. Second\n\nMore words.\n',
        }

    def test_a_whole_record_banner_and_declaration_pair_is_green(self) -> None:
        self.assertEqual(supersession_findings(self.whole_records()), ())

    def test_a_whole_record_declaration_without_its_banner_is_red(self) -> None:
        records = self.whole_records()
        title, _banner, rest = records["0106-old.md"].split("\n\n", 2)
        records["0106-old.md"] = title + "\n\n" + rest
        self.assertTrue(any("every ruling except ruling 2 has no matching marker" in row for row in supersession_findings(records)))

    def test_a_banner_and_declaration_disagreeing_on_exceptions_is_red_both_ways(self) -> None:
        records = self.whole_records()
        records["0106-old.md"] = records["0106-old.md"].replace(
            "Every ruling except ruling 2 in \"Old title\" is withdrawn", "Every ruling in \"Old title\" is withdrawn"
        ).replace("so every ruling except ruling 2 is history", "so it is history")
        rows = supersession_findings(records)
        self.assertTrue(any("except ruling 2 has no matching marker" in row for row in rows))
        self.assertTrue(any(row.endswith("does not declare every ruling") for row in rows))

    def test_a_banner_below_the_first_section_is_not_whole_record(self) -> None:
        records = self.whole_records()
        title, banner, rest = records["0106-old.md"].split("\n\n", 2)
        records["0106-old.md"] = title + "\n\n## Context\n\n" + banner + "\n\n" + rest
        self.assertTrue(any("unread supersession marker" in row for row in supersession_findings(records)))

    def test_an_exception_naming_an_absent_ruling_is_red(self) -> None:
        records = self.whole_records()
        records["0343-new.md"] = records["0343-new.md"].replace("except ruling 2,", "except ruling 7,")
        self.assertTrue(any("excepts an absent ruling" in row for row in supersession_findings(records)))

    def test_an_unread_declaration_is_a_finding(self) -> None:
        records = self.paired_records()
        records["0280-new.md"] = records["0280-new.md"].replace("- [ADR", "* [ADR")
        self.assertTrue(any("unread Supersedes" in row for row in supersession_findings(records)))


if __name__ == "__main__":
    unittest.main()
