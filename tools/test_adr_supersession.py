"""Bind declared ADR supersessions in both directions; see DECLARED_LIMITS.

Grammar: an optional exact ``## Supersedes`` section contains hyphen bullets,
each beginning with a relative ``[ADR NNNN](NNNN-slug.md)`` link followed by
``ruling N,`` and explanatory prose. Indented continuation lines are joined.
A target outside numbered rulings instead uses ``the words "…",`` as its
coordinate. Whitespace is collapsed; the quote occurs exactly once outside
markers, and its marker sits directly beneath the quoted paragraph.
A marker is a paragraph beginning ``*Superseded YYYY-MM-DD.*`` beneath a
recognized ruling heading or numbered ruling item using ``adr_read``'s grammar.
It may be indented within a numbered ruling's list item.
It contains a quoted span, the same relative ADR link
followed by ``ruling N``, and an account of what survives. The account's truth
is read at review, not inferred from supersession verbs.
A bare overturning link is accepted only for a record with no numbered rulings.
No marker paragraph may contain a heading.

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
from typing import NamedTuple
from unittest import mock

from adr_read import ruling_attributions, ruling_ordinals
from adr_supersession_population import banner_disposition_findings, banner_population, classification_findings, derive_population, derive_records, legacy_marker_findings
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
    "Quotes in numbered-ruling and whole-record markers are required but are not compared with target words; exact-once quote binding applies to quote coordinates only.",
    f"The historical classification's unsure-pair unread remainder is {unsure_remainder()}; its source is supersession-classification-1518.json, not a completed supersession reading.",
    "Only the documented relative-link, bullet, paragraph, and adr_read ruling grammar is read; alternative Markdown forms are not certified.",
    f"The unattributed legacy-marker unread remainder is {unsure_remainder(legacy=True)}; exact retained source and the committed manifest bind these exceptions, and available Git history independently verifies them.",
)
LINK = r"\[ADR (\d{4})\]\((\d{4}-[^()\s]+\.md)\)"
DECLARATION = re.compile(r"^- " + LINK + r"\s+ruling (\d+),\s+(.+)$")
QUOTE_DECLARATION = re.compile(r'^- ' + LINK + r'\s+the words "([^"]+)",\s+(.+)$')
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
    if isinstance(ruling, str):
        return f'the words "{ruling}"'
    kept = sorted(ruling[1])
    return "every ruling" + (f" except ruling {', '.join(map(str, kept))}" if kept else "")
MARKER_LINK = re.compile(LINK + r"(?:\s+ruling (\d+)\b)?")
OPENING = re.compile(r"^\*Superseded (\d{4}-\d{2}-\d{2})\.\*\s+(.+)$")


def collapsed(text: str) -> str:
    return " ".join(text.split())


class QuoteLocation(NamedTuple):
    paragraph: int
    line: int
    end_line: int


def quote_locations(text: str, quote: str) -> list[QuoteLocation]:
    """Locate exact words outside markers, keeping paragraph and ruling context."""
    pattern = re.compile(r"\s+".join(re.escape(word) for word in quote.split()))
    return [
        QuoteLocation(line, line + paragraph[:match.start()].count("\n"),
                      line + paragraph[:match.end()].count("\n"))
        for line, paragraph in paragraphs(text)
        if not OPENING.match(collapsed(paragraph))
        for match in pattern.finditer(paragraph)
    ]


def supersession_findings(records: dict[str, str], report: dict | None = None, *, root: Path | None = None) -> tuple[str, ...]:
    """Grade an independently supplied complete ADR filename/text population.

    The cutoff belongs to the overturning record, so an old target can still
    owe a marker for a new declaration. This seam writes nothing.
    """
    findings, unresolved = legacy_marker_findings(report or {}, records, root=root)
    findings.extend(banner_disposition_findings(*banner_population(records), (report or {}).get('pairs', [])))
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
            quoted = None if parsed or whole else QUOTE_DECLARATION.fullmatch(joined)
            found = parsed or whole or quoted
            if found is None or found.group(1) != found.group(2)[:4]:
                findings.append(f"{name}: unread Supersedes declaration")
                continue
            if quoted:
                target = "\n".join(unfenced_lines(records.get(quoted.group(2), "")))
                quote = collapsed(quoted.group(3))
                locations = quote_locations(target, quote)
                target_contexts = {row.line: row.number for row in ruling_attributions(target)}
                if len(locations) != 1:
                    findings.append(f"{name}: target quote occurs {len(locations)} times outside markers")
                elif any(target_contexts.get(line) is not None for line in range(
                    locations[0].line, locations[0].end_line + 1
                )):
                    findings.append(f"{name}: quote coordinate targets a numbered ruling")
                declarations.add((name, quoted.group(2), quote))
            elif whole:
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
        blocks = list(paragraphs(text))
        for index, (line_number, paragraph) in enumerate(blocks):
            paragraph = re.sub(r"^ {1,3}(?=\*Superseded)", "", paragraph)
            ruling = contexts.get(line_number)
            if first_section is None or line_number < first_section:
                phrase = WHOLE_PHRASE.search(" ".join(paragraph.splitlines()))
                if phrase:
                    ruling = whole_record(phrase.group(1))
            if not paragraph.startswith("*Superseded") or paragraph.startswith("*Superseded grounding marked "):
                continue
            if (name, paragraph) in unresolved:
                continue
            links = list(MARKER_LINK.finditer(paragraph))
            # Authored notes also link background records (for example ADR 0016).
            # With a numbered overturning link present, bare links participate
            # only when the declaring record actually claims this target.
            if any(link.group(3) is not None for link in links):
                numbered = {link.group(2) for link in links if link.group(3) is not None}
                links = [link for link in links if link.group(3) is not None or any(
                    declaring == link.group(2) and target == name and isinstance(key, str)
                    and f'"{key}"' in collapsed(paragraph) and declaring not in numbered
                    for declaring, target, key in declarations
                )]
            # Old targets with only old links belong to the repair, not this rule.
            if int(name[:4]) < CUTOFF and links and all(
                int(link.group(1)) < CUTOFF for link in links
            ):
                continue
            opening = OPENING.match(" ".join(paragraph.splitlines()))
            if re.search(r"^##(?:\s|#)", paragraph, re.M):
                findings.append(f"{name}: heading inside supersession marker")
            valid_date = False
            if opening:
                try:
                    date.fromisoformat(opening.group(1))
                    valid_date = True
                except ValueError:
                    pass
            quotes = re.findall(r'"([^"\n]+)"', collapsed(paragraph))
            if not valid_date or not links or not quotes:
                findings.append(f"{name}: unread supersession marker")
                continue
            for link in links:
                if link.group(1) != link.group(2)[:4]:
                    findings.append(f"{name}: marker link number disagrees with path")
                    continue
                ordinals = ruling_ordinals(records.get(link.group(2), ""))
                if link.group(3) is None and ordinals:
                    findings.append(f"{name}: bare marker link names a record with rulings")
                elif link.group(3) is not None and int(link.group(3)) not in ordinals:
                    findings.append(f"{name}: marker links an absent overturning ruling")
                if ruling is None:
                    matched = [quote for quote in quotes if (link.group(2), name, quote) in declarations]
                    if not matched:
                        findings.append(f"{name}: unread supersession marker")
                    for quote in matched:
                        locations = quote_locations(text, quote)
                        if len(locations) != 1:
                            findings.append(f"{name}: marker quote occurs {len(locations)} times outside markers")
                        elif index == 0 or locations[0].paragraph != blocks[index - 1][0]:
                            findings.append(f"{name}: quote marker is not directly beneath its target paragraph")
                        markers.add((link.group(2), name, quote))
                else:
                    markers.add((link.group(2), name, ruling))

    for declaring, target, ruling in sorted(declarations - markers, key=str):
        findings.append(f"{declaring}: {target} {shown(ruling)} has no matching marker")
    for declaring, target, ruling in sorted(markers - declarations, key=str):
        findings.append(f"{target}: {declaring} does not declare {shown(ruling)}")
    return tuple(findings)


class SupersessionBindingTests(unittest.TestCase):
    def test_marker_inside_numbered_ruling_preserves_binding(self):
        records = {
            "0001-old.md": '1. Old choice.\n\n   *Superseded 2026-10-19.* The words "Old choice" fall to [ADR 0002](0002-new.md) ruling 1. Other choices stand.\n\n2. Other choice.\n',
            "0002-new.md": '1. New choice.\n\n## Supersedes\n\n- [ADR 0001](0001-old.md) ruling 1, the words "Old choice". Other choices stand.\n',
        }
        self.assertEqual(supersession_findings(records), ())
        records['0001-old.md'] = records['0001-old.md'].replace('ruling 1.', 'ruling 2.')
        self.assertTrue(supersession_findings(records))

    def quote_records(self):
        return {
            "0014-new.md": '## Decision\n\nNew practice.\n\n## Supersedes\n\n- [ADR 0005](0005-old.md) the words "Old words.", the date rule stands.\n',
            "0005-old.md": '## Decision\n\nOld\nwords.\n\n*Superseded 2026-10-17.* The words "Old words." fall to [ADR 0014](0014-new.md). The date rule stands.\n',
        }

    def test_quote_coordinate_accepts_wrapped_words_and_a_bare_unruled_record(self):
        self.assertEqual(supersession_findings(self.quote_records()), ())

    def test_quote_coordinate_requires_exactly_one_nonmarker_occurrence(self):
        for replacement in ('Absent words.', 'Old words. Old words.'):
            with self.subTest(replacement=replacement):
                records = self.quote_records()
                records['0005-old.md'] = records['0005-old.md'].replace('Old\nwords.', replacement)
                self.assertTrue(any('quote occurs' in row for row in supersession_findings(records)))

    def test_quote_coordinate_refuses_a_numbered_target(self):
        records = self.quote_records()
        records['0005-old.md'] = records['0005-old.md'].replace('## Decision', '## Ruling 1')
        self.assertTrue(any('numbered ruling' in row for row in supersession_findings(records)))

    def test_quote_context_is_read_at_the_words_not_the_paragraph_opening(self):
        records = self.quote_records()
        records['0005-old.md'] = records['0005-old.md'].replace(
            '## Decision\n\nOld\nwords.',
            'Introductory prose.\n## Ruling 1\nOld\nwords.\n## Commentary',
        )
        self.assertTrue(any('numbered ruling' in row for row in supersession_findings(records)))

    def test_quote_coordinate_cannot_cross_into_a_numbered_ruling(self):
        records = self.quote_records()
        quote = 'Introductory prose. ## Ruling 1 Old words.'
        records = {name: text.replace('"Old words."', f'"{quote}"') for name, text in records.items()}
        records['0005-old.md'] = records['0005-old.md'].replace(
            '## Decision\n\nOld\nwords.',
            'Introductory prose.\n## Ruling 1\nOld words.\n## Commentary',
        )
        self.assertTrue(any('numbered ruling' in row for row in supersession_findings(records)))

    def test_bare_marker_link_refuses_an_overturning_record_with_rulings(self):
        records = self.quote_records()
        records['0014-new.md'] = records['0014-new.md'].replace('## Decision', '## Ruling 1')
        self.assertTrue(any('bare marker link' in row for row in supersession_findings(records)))

    def test_quote_marker_must_be_directly_beneath_the_quoted_paragraph(self):
        records = self.quote_records()
        records['0005-old.md'] = records['0005-old.md'].replace('\n\n*Superseded', '\n\nIntervening paragraph.\n\n*Superseded')
        self.assertTrue(any('directly beneath' in row for row in supersession_findings(records)))

    def test_heading_inside_a_marker_is_a_finding(self):
        records = self.paired_records()
        records['0135-old.md'] = records['0135-old.md'].replace('The verdict stands.\n', 'The verdict stands.\n## Absorbed heading\n')
        self.assertTrue(any('heading inside' in row for row in supersession_findings(records)))

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

    def test_binding_requires_live_banner_proof_and_disposition_for_a_discharged_pair(self):
        records = self.whole_records()
        records['0107-middle.md'] = 'ADR 0106 is replaced.\n'
        report = {'pairs': [{
            'later': '0107', 'earlier': '0106', 'classification': 'overturned',
            'disposition': 'adr-0343-banner',
        }]}
        self.assertEqual(supersession_findings(records, report), ())
        del report['pairs'][0]['disposition']
        self.assertTrue(any('no declaration or banner disposition' in finding for finding in supersession_findings(records, report)))
        report['pairs'][0]['disposition'] = 'adr-0343-banner'
        records['0106-old.md'] = records['0106-old.md'].replace('*Superseded', '*Corrected')
        self.assertTrue(any('invalid banner disposition' in finding for finding in supersession_findings(records, report)))

    def test_an_unread_declaration_is_a_finding(self) -> None:
        records = self.paired_records()
        records["0280-new.md"] = records["0280-new.md"].replace("- [ADR", "* [ADR")
        self.assertTrue(any("unread Supersedes" in row for row in supersession_findings(records)))


if __name__ == "__main__":
    unittest.main()
