"""The Canvas submission renderer consumes the shared Markdown seams."""

import contextlib
import io
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

import discussion_post_scan
import docx_write
import post_html


MARKDOWN = """# A title

## Why **shared** parsing matters

Plain & *careful* text with `code`.

- first
- second

| Field | Value |
| --- | --- |
| Route | HTML |

<!-- INVOKED: gravity | attracts mass -->

## References

Quill, R. (2024). *A useful source*.
"""


class SharedInlineTests(unittest.TestCase):
    def test_the_format_neutral_splitter_carries_nested_properties(self):
        spans = tuple(
            (span.text, span.bold, span.italic, span.monospace)
            for span in docx_write.inline_spans(
                "**Acute PID due to *Neisseria gonorrhoeae* and `code`.**"
            )
        )

        self.assertEqual(
            spans,
            (
                ("Acute PID due to ", True, False, False),
                ("Neisseria gonorrhoeae", True, True, False),
                (" and ", True, False, False),
                ("code", True, False, True),
                (".", True, False, False),
            ),
        )


class HtmlRendererTests(unittest.TestCase):
    def test_finished_markdown_becomes_canvas_html_without_own_line_comments(self):
        rendered = post_html.render(MARKDOWN)

        self.assertIn("<p><strong>A title</strong></p>", rendered)
        self.assertIn(
            "<p><strong>Why <strong>shared</strong> parsing matters</strong></p>",
            rendered,
        )
        self.assertIn("Plain &amp; <em>careful</em> text with <code>code</code>.", rendered)
        self.assertIn("<ul><li>first</li><li>second</li></ul>", rendered)
        self.assertIn("<table><thead><tr><th>Field</th><th>Value</th></tr></thead>", rendered)
        self.assertIn("<tbody><tr><td>Route</td><td>HTML</td></tr></tbody></table>", rendered)
        self.assertIn("<p><strong>References</strong></p>", rendered)
        self.assertNotIn("INVOKED", rendered)

    def test_mid_line_comment_delimiters_reach_the_submission_for_the_grader(self):
        rendered = post_html.render("Text <!-- INVOKED: x | does y --> tail.\n")

        self.assertIn("<!-- INVOKED: x | does y -->", rendered)

    def test_a_block_quotation_uses_the_semantic_html_element(self):
        rendered = post_html.render("> Exact words from the cited source.\n")

        self.assertEqual(rendered, "<blockquote>Exact words from the cited source.</blockquote>\n")

    def test_a_reference_url_becomes_an_anchor_whose_text_is_the_url(self):
        rendered = post_html.render(
            "Author, A. (2026). *A title*. https://www.example.gov/files/a-b.pdf\n"
        )

        self.assertEqual(
            rendered,
            "<p>Author, A. (2026). <em>A title</em>. "
            '<a href="https://www.example.gov/files/a-b.pdf">'
            "https://www.example.gov/files/a-b.pdf</a></p>\n",
        )

    def test_no_url_in_a_reference_list_is_left_outside_an_anchor(self):
        markdown = (
            "**References**\n\n"
            "Agency. (2026, March 10). *First page*. https://www.example.gov/first\n\n"
            "Social Security Act, 42 U.S.C. § 1396a(bb) (2024). "
            "https://www.example.gov/content/pkg/USCODE-2024-title42/html/sec1396a.htm\n\n"
            "Doe, J. (2025). Article. *Journal, 1*(2), 3-4. https://doi.org/10.1000/xyz123\n"
        )

        class Outside(HTMLParser):
            def __init__(self):
                super().__init__()
                self.depth = 0
                self.outside: list[str] = []
                self.anchors = 0

            def handle_starttag(self, tag, _attrs):
                if tag == "a":
                    self.depth += 1
                    self.anchors += 1

            def handle_endtag(self, tag):
                if tag == "a":
                    self.depth -= 1

            def handle_data(self, data):
                if self.depth == 0:
                    self.outside.append(data)

        reader = Outside()
        reader.feed(post_html.render(markdown))

        self.assertEqual(reader.anchors, 3)
        self.assertNotIn("http", "".join(reader.outside))

    def test_trailing_punctuation_and_an_unbalanced_parenthesis_stay_outside_the_link(self):
        rendered = post_html.render(
            "See https://example.org/page. Also (https://example.org/a_(b)).\n"
        )

        self.assertIn('<a href="https://example.org/page">https://example.org/page</a>. ', rendered)
        self.assertIn(
            '(<a href="https://example.org/a_(b)">https://example.org/a_(b)</a>).',
            rendered,
        )

    def test_an_unbalanced_bracket_and_a_trailing_quote_stay_outside_the_link(self):
        rendered = post_html.render("[See https://example.org/x] and 'https://example.org/y'\n")

        self.assertIn('[See <a href="https://example.org/x">https://example.org/x</a>]', rendered)
        self.assertIn(
            "'<a href=\"https://example.org/y\">https://example.org/y</a>'",
            rendered,
        )

    def test_a_url_inside_a_code_span_is_not_linked(self):
        rendered = post_html.render("Run `https://example.org/raw` exactly.\n")

        self.assertIn("<code>https://example.org/raw</code>", rendered)
        self.assertNotIn("<a ", rendered)

    def test_an_ampersand_in_a_url_is_escaped_in_the_href_and_the_text(self):
        rendered = post_html.render("Source https://example.org/view?id=1&page=2\n")

        self.assertIn(
            '<a href="https://example.org/view?id=1&amp;page=2">'
            "https://example.org/view?id=1&amp;page=2</a>",
            rendered,
        )

    def test_the_post_grader_reads_linked_urls_as_the_same_visible_text(self):
        markdown = (
            "Body text.\n\n"
            "**References**\n\n"
            "Agency. (2026). *Title*. https://www.example.gov/a-page\n"
        )
        parser = discussion_post_scan.SubmissionHtmlParser()
        parser.feed(post_html.render(markdown))
        parser.close()
        expected, block_count = discussion_post_scan._expected_html_units(markdown)

        self.assertEqual(
            tuple((unit.tag, unit.text) for unit in parser.units),
            tuple((unit.tag, unit.text) for unit in expected),
        )
        self.assertEqual(parser.block_count, block_count)

    def test_the_command_writes_the_exact_rendered_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "post.md"
            destination = Path(temp) / "post.html"
            source.write_text(MARKDOWN, encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = post_html.main([str(source), str(destination)])

            self.assertEqual(status, 0)
            self.assertEqual(destination.read_text(encoding="utf-8"), post_html.render(MARKDOWN))
            self.assertIn(str(destination), stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
