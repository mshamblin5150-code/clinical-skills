"""ADR 0398 through the public PowerPoint grader. All decks are synthetic.

phi-scan: synthetic
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import tempfile
import unittest
from xml.sax.saxutils import escape

import completion_checks
import deck_scan
import run_grader
from discussion_post_scan import traceable_numeric_values
from test_deck_scan import Run, BAR, A, P, slide_xml, notes_xml, trusted_claim


ENTRY = "Example Group. (2026). A work. https://example.org/work"


def entry_paragraph(text, *, indent=True, inherited=False):
    properties = (' marL="457200" indent="-228600"' if indent else '')
    default = '<a:defRPr i="1"/>' if inherited else ''
    parts = []
    for index, piece in enumerate(text.split('*')):
        for line_index, line in enumerate(piece.split('\v')):
            if line_index:
                parts.append('<a:br/>')
            italic = '' if inherited else f' i="{int(index % 2 == 1)}"'
            parts.append(f'<a:r><a:rPr sz="2800"{italic}/><a:t>{escape(line)}</a:t></a:r>')
    return f'<a:p><a:pPr{properties}>{default}</a:pPr>{"".join(parts)}</a:p>'


def box(text, y, x=0, **kwargs):
    paragraphs = text if isinstance(text, tuple) else (text,)
    return (f'<p:sp><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/></a:xfrm></p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/>{"".join(entry_paragraph(item, **kwargs) for item in paragraphs)}</p:txBody></p:sp>')


def reference_slide(*entries, heading='References | Sources', boxes=None, **kwargs):
    contents = boxes if boxes is not None else ''.join(box(entry, (i + 1) * 100, **kwargs) for i, entry in enumerate(entries))
    return (f'<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>'
            f'{box(heading, 0)}{contents}{box("2", 99999)}</p:spTree></p:cSld></p:sld>')


def prepare(root, entries=(ENTRY,), *, body='A finding (Example Group, 2026).', notes=(), references=None, **kwargs):
    run = Run(root)
    bar = BAR.replace('SLIDE-MAX: 2', 'SLIDE-MAX: 20').replace('BULLETS-PER-SLIDE: 2', 'BULLETS-PER-SLIDE: 100').replace('WORDS-PER-BULLET: 6', 'WORDS-PER-BULLET: 200')
    (root / 'bar.md').write_text(bar, encoding='utf-8')
    refs = references if references is not None else (reference_slide(*entries, **kwargs),)
    run.write_deck((slide_xml('Purpose', body), *refs), tuple(notes_xml(note) for note in notes))
    numbers = traceable_numeric_values(' '.join((*entries, body, *notes)))
    claims = trusted_claim('2', *numbers)
    for entry in entries:
        claims += f'\n## CLAIM: A source.\nREFERENCE: {entry.replace(chr(11), " ")}\n'
    (root / 'claims.md').write_text(claims, encoding='utf-8')
    run.retain(1, 1 + len(refs))
    run.write_rendered(slides=f'{1 + len(refs)} of {1 + len(refs)} read')
    run.write_intent(content_slides='1', reference_slides=', '.join(str(n) for n in range(2, 2 + len(refs))))
    run.write_adversarial()
    return run


class DeckReferenceCommand(unittest.TestCase):
    def command(self, entries=(ENTRY,), **kwargs):
        with tempfile.TemporaryDirectory() as temp:
            run = prepare(Path(temp), entries, **kwargs)
            status, report, errors = run.grade('--show')
            return status, report + errors

    def test_correct_reference_and_citations_on_either_surface(self):
        for body, notes in (('A finding (Example Group, 2026).', ()), ('A finding.', ('A finding (Example Group, 2026).',))):
            status, report = self.command(body=body, notes=notes)
            self.assertEqual(0, status, report)
            self.assertIn('references read   1', report)
            self.assertIn('citation candidates 1', report)
            self.assertIn('citation unread   0', report)
            self.assertNotIn('heading-not-apa:', report)
            self.assertNotIn('entry-not-a-paragraph:', report)

    def test_reference_list_does_not_cite_itself(self):
        status, report = self.command(body='A finding.')
        self.assertEqual(1, status, report)
        self.assertIn('uncited-entry: 1', report)

    def test_heading_and_numeric_page_boxes_match_visible_text_across_italic_runs(self):
        slide = reference_slide(ENTRY, heading='Ref*erences* | Sources').replace(box('2', 99999), box('1*2*', 99999))
        # A visually empty italic paragraph is not a heading or an entry.
        slide = slide.replace('<p:spTree>', '<p:spTree>' + box('* *', -100))
        with tempfile.TemporaryDirectory() as temp:
            run = prepare(Path(temp), references=(slide,))
            claims = run.root / 'claims.md'
            claims.write_text(claims.read_text(encoding='utf-8') + trusted_claim('12'), encoding='utf-8')
            run.write_adversarial()
            status, report, errors = run.grade('--show')
            self.assertEqual(0, status, report + errors)
            self.assertIn('references read   1', report)
            self.assertIn('reference slides unread 0', report)
            self.assertIn('entry-has-no-year: 0', report)

    def test_unlisted_and_wrong_year_citations_are_refused(self):
        for body, kind in (('A finding (Other Group, 2026).', 'unlisted-citation'), ('A finding (Example Group, 2025).', 'intext-year-mismatch')):
            status, report = self.command(body=body)
            self.assertEqual(1, status, report)
            self.assertIn(f'{kind}: 1', report)

    def test_missing_year_and_split_entries_stay_broken(self):
        status, report = self.command(('Example Group. A work. https://example.org/work',))
        self.assertEqual(1, status, report)
        self.assertIn('entry-has-no-year: 1', report)
        entries = ('Example Group. (2026).', 'A work. https://example.org/work')
        status, report = self.command(entries, references=tuple(reference_slide(entry) for entry in entries))
        self.assertEqual(1, status, report)
        self.assertIn('references read   2', report)
        self.assertIn('entry-has-no-year: 1', report)

    def test_slide_population_and_opening_heading_disagreement_is_unread(self):
        for listed, heading in (('none', 'References'), ('2', 'Sources')):
            with self.subTest(listed=listed, heading=heading), tempfile.TemporaryDirectory() as temp:
                run = prepare(Path(temp), heading=heading, body='A finding.')
                run.write_intent(content_slides='1, 2' if listed == 'none' else '1', reference_slides=listed)
                status, report, errors = run.grade('--show')
                self.assertEqual(2, status, report + errors)
                self.assertIn('reference slides unread 1', report)

    def test_boxes_follow_position_then_left_to_right_and_record_slide_order(self):
        alpha = 'Alpha. (2026). A work.'
        zulu = 'Zulu. (2026). A work.'
        body = '(Alpha, 2026; Zulu, 2026).'
        for boxes in (box(zulu, 200) + box(alpha, 100), box(zulu, 100, 200) + box(alpha, 100, 0)):
            status, report = self.command((alpha, zulu), body=body, boxes=boxes)
            self.assertEqual(0, status, report)
        with tempfile.TemporaryDirectory() as temp:
            run = prepare(Path(temp), (alpha, zulu), body=body, references=(reference_slide(zulu), reference_slide(alpha)))
            run.write_intent(content_slides='1', reference_slides='3, 2')
            status, report, errors = run.grade()
            self.assertEqual(0, status, report + errors)
            run.write_intent(content_slides='1', reference_slides='2, 3')
            status, report, errors = run.grade()
            self.assertEqual(1, status, report + errors)
            self.assertIn('list-not-sorted: 1', report)

    def test_forced_break_is_space_and_each_paragraph_is_an_entry(self):
        status, report = self.command((ENTRY.replace('Group.', 'Group.\v'),))
        self.assertEqual(0, status, report)
        status, report = self.command((ENTRY, ENTRY.replace('Example Group', 'Zulu')), body='(Example Group, 2026; Zulu, 2026).', boxes=box((ENTRY, ENTRY.replace('Example Group', 'Zulu')), 100))
        self.assertEqual(0, status, report)
        self.assertIn('references read   2', report)

    def test_each_paragraph_needs_its_own_indent(self):
        status, report = self.command(indent=False)
        self.assertEqual(1, status, report)
        self.assertIn('reference-hanging-indent: 1', report)
        for old, new in (('marL="457200"', 'marL="0"'), ('indent="-228600"', 'indent="228600"')):
            status, report = self.command(references=(reference_slide(ENTRY).replace(old, new),))
            self.assertEqual(1, status, report)
            self.assertIn('reference-hanging-indent: 1', report)
        slide = reference_slide(ENTRY, indent=False).replace('<a:lstStyle/>', '<a:lstStyle><a:lvl1pPr marL="457200" indent="-228600"/></a:lstStyle>')
        status, report = self.command(references=(slide,))
        self.assertEqual(1, status, report)
        self.assertIn('reference-hanging-indent: 1', report)

    def test_uptodate_requires_retrieval_date_and_explicit_italics(self):
        entry = 'Example, A. (2026). A topic. In B. Editor (Ed.), *UpToDate*. Retrieved September 2, 2026, from https://www.uptodate.com/contents/a-topic'
        for text, inherited, expected in ((entry, False, 0), (entry.replace('*', ''), True, 1)):
            status, report = self.command((text,), body='(Example, 2026).', inherited=inherited)
            self.assertEqual(expected, status, report)
            self.assertIn(f'uptodate-italics: {expected}', report)
        status, report = self.command((entry.replace('Retrieved September 2, 2026, from ', ''),), body='(Example, 2026).')
        self.assertEqual(1, status, report)
        self.assertIn('requires-retrieval-date: 1', report)
        status, report = self.command((entry.replace('*UpToDate*', '*Up**ToDate*'),), body='(Example, 2026).')
        self.assertEqual(0, status, report)

    def test_unpositioned_entry_is_unread_and_default_report_hides_text(self):
        slide = reference_slide(ENTRY).replace('<a:off x="0" y="100"/>', '')
        status, report = self.command(references=(slide,))
        self.assertEqual(2, status, report)
        self.assertIn('reference slides unread 1', report)
        with tempfile.TemporaryDirectory() as temp:
            marker = 'private-reference-marker'
            run = prepare(Path(temp), (ENTRY + marker,), body='A finding.')
            _, report, errors = run.grade()
            self.assertNotIn(marker, report + errors)
            _, report, errors = run.grade('--show')
            self.assertIn(marker, report + errors)

    def test_paper_language_flag_bar_then_profile_and_missing_answer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = prepare(root)
            profile = root / 'profile.md'
            profile.write_text('PAPER-LANGUAGE: Swedish\n', encoding='utf-8')
            for options, expected, status in ((('--profile', str(profile)), 'en', 0), (('--profile', str(profile), '--paper-language', 'Danish'), 'da', 0)):
                actual, report, errors = run.grade(*options)
                self.assertEqual(status, actual, report + errors)
                self.assertIn(f'reference order ({expected}): graded', report)
            bar = root / 'bar.md'
            bar.write_text(bar.read_text(encoding='utf-8').replace('PAPER-LANGUAGE: en\n', ''), encoding='utf-8')
            status, report, errors = run.grade('--profile', str(profile))
            self.assertEqual(0, status, report + errors)
            self.assertIn('reference order (sv): graded', report)
            profile.write_text('', encoding='utf-8')
            status, report, errors = run.grade('--profile', str(profile))
            self.assertEqual(2, status, report + errors)
            self.assertIn('reference order (unspecified): not graded', report)

    def test_citation_reader_unread_reaches_the_shared_remainder(self):
        status, report = self.command(body='A finding (Example Group, 2026). A malformed date (Example Group, 1899-2010).')
        self.assertEqual(2, status, report)
        self.assertIn('citation unread   1', report)
        self.assertIn('unread remainder 1', report)

    def test_legal_section_form_resolves_and_is_refused_for_form(self):
        entry = 'Patient rights, 42 C.F.R. § 482.13 (2024).'
        for body, expected in (('The rule (Patient rights, 2024).', 0), ('The rule (42 C.F.R. § 482.13, 2024).', 1), ('The rule 42 C.F.R. § 482.13.', 1)):
            status, report = self.command((entry,), body=body)
            self.assertEqual(expected, status, report)
            self.assertIn(f'legal-citation-section-form: {expected}', report)
            self.assertIn('unlisted-citation: 0', report)
            self.assertIn('uncited-entry: 0', report)

    def test_recent_reference_rows_and_correct_controls_reach_decks(self):
        dailymed = 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1234-5678-9012'
        cases = (
            ('retrieval-date-on-archived', f'Example Group. (2026). *Patient FAQ*. Retrieved October 19, 2026, from https://example.org/patients', 'Example Group. (2026). *Patient FAQ*. https://example.org/patients'),
            ('missing-drug-description', f'Example Group. (2026). *Amoxicillin tablet*. DailyMed. {dailymed}', f'Example Group. (2026). *Amoxicillin tablet* [Drug information]. DailyMed. {dailymed}'),
            ('parent-first-author', 'National Institutes of Health, Office of Dietary Supplements. (2026). *Fact sheet*. https://example.org/topic', 'Office of Dietary Supplements. (2026). *Fact sheet*. National Institutes of Health. https://example.org/topic'),
            ('bracketed-document-number', 'Example Group. (2026). *Report* [Report No. NASA/CR-2018-220043]. https://example.org/report', 'Example Group. (2026). *Report* (Report No. NASA/CR-2018-220043). https://example.org/report'),
            ('hyphenated-range', 'Example Group. (2026). Article. *Journal, 12*(3), e212-e316. https://example.org/topic', 'Example Group. (2026). Article. *Journal, 12*(3), e212–e316. https://example.org/topic'),
            ('missing-article', 'Example Group. (2026). Article. *Journal, 12*(3), e12345. https://doi.org/10.1000/e12345', 'Example Group. (2026). Article. *Journal, 12*(3), Article e12345. https://doi.org/10.1000/e12345'),
            ('format-bracket', 'Example Group. (2026). *Work* [PDF]. https://example.org/work', 'Example Group. (2026). *Work*. https://example.org/work'),
            ('italic-identifier', 'Example Group. (2026). *Work (Table AB-12)*. https://example.org/work', 'Example Group. (2026). *Work* (Table AB-12). https://example.org/work'),
            ('site-repeats-author', 'Example Group. (2026). *Work*. Example Group. https://example.org/work', 'Example Group. (2026). *Work*. https://example.org/work'),
        )
        for kind, defective, correct in cases:
            for entry, expected in ((defective, 1), (correct, 0)):
                author = entry.split('. (2026)', 1)[0]
                with self.subTest(kind=kind, expected=expected):
                    status, report = self.command((entry,), body=f'({author}, 2026).')
                    self.assertEqual(expected, status, report)
                    self.assertIn(f'{kind}: {expected}', report)
        for description in ('Drug label', 'Package insert', 'Prescribing information'):
            status, report = self.command((f'Example Group. (2026). *Amoxicillin tablet* [{description}]. DailyMed. {dailymed}',))
            self.assertEqual(0, status, report)
        for title in ('Work (COVID-19)', 'Work (HP2030)', 'Work (2000–2019)', 'Work (CMS-1807-F)', 'Children aged 5-12 and doses of 10-20 mg'):
            status, report = self.command((f'Example Group. (2026). *{title}*. https://example.org/work',))
            self.assertEqual(0, status, report)
        status, report = self.command(('Example Group. (2026). *Work* (NIH Publication No. 2025-2026). https://example.org/work',))
        self.assertEqual(0, status, report)

    def test_new_checks_are_exempt_before_approval_boundary_without_frozen_grade(self):
        with tempfile.TemporaryDirectory() as temp:
            run = prepare(Path(temp), indent=False, body='A finding.')
            source = deck_scan.load(run_grader.Parsed(source=str(run.root), values={'--pptx': str(run.deck)}))
            start, moment = completion_checks.registry()['deck_scan:reference-hanging-indent']
            self.assertEqual('approval', moment)
            for approval, expected in ((start - timedelta(seconds=1), set()), (start, {'reference-hanging-indent', 'uncited-entry'})):
                token = completion_checks.MOMENTS.set({'approval': approval})
                try:
                    found = {f.kind for f in deck_scan.survey(source).findings}
                finally:
                    completion_checks.MOMENTS.reset(token)
                self.assertEqual(expected, found)

    def test_empty_reference_population_still_requires_an_answered_supported_language(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = Run(root)
            run.write_deck((slide_xml('Purpose', 'A finding.'),))
            bar = root / 'bar.md'
            bar.write_text(bar.read_text(encoding='utf-8').replace('PAPER-LANGUAGE: en\n', ''), encoding='utf-8')
            profile = root / 'profile.md'
            profile.write_text('', encoding='utf-8')
            for options, language, status in (
                ((), 'unspecified', 2),
                (('--paper-language', 'unlisted'), 'unlisted', 2),
                (('--paper-language', 'English'), 'en', 0),
            ):
                with self.subTest(language=language):
                    actual, report, errors = run.grade('--profile', str(profile), *options)
                    self.assertEqual(status, actual, report + errors)
                    self.assertIn('references read   0', report)
                    expected = 'graded' if status == 0 else 'not graded'
                    self.assertIn(f'reference order ({language}): {expected}', report)


if __name__ == '__main__':
    unittest.main()
