"""The Canvas submission renderer consumes the shared Markdown seams."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

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
