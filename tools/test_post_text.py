"""Plain Canvas builds refuse unknown shapes and bind to the approved source."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
import post_text
import peer_critique_scan

class PlainTextTests(unittest.TestCase):
    def test_prescribed_headings_prose_references_and_lists(self):
        source = "**Clinical Assessment**\n\nText & *title* with `code` and \\*.\n\n# References\n\nA. (2026). *Title*. https://example.test/a?x=1&y=2\n\n- One\n2. Two\n"
        self.assertEqual("Clinical Assessment\n\nText & title with code and *.\n\nReferences\n\nA. (2026). Title. https://example.test/a?x=1&y=2\n\n- One\n2. Two\n", post_text.render(source))

    def test_literal_urls_and_list_numerals_keep_their_text(self):
        self.assertEqual('https://example.test/a*b_c_d?x=1&y=2\n01. First\n',
                         post_text.render('https://example.test/a\\*b_c_d?x=1&y=2\n01. First\n'))

    def test_each_unknown_shape_names_its_line_and_writes_nothing(self):
        shapes = ('[title](https://example.test)', '![image](url)', '[name][ref]', '[ref]: url',
                  '> Quote', '| A | B |\n| --- | --- |', '---', '```code', '~~~code',
                  '<em>HTML</em>', '~~strike~~', '_italic_', '__bold__', '+ list', '* list',
                  '  - nested', '    indented', '##### heading', '**unfinished', '`unfinished', 'back\\q')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for shape in shapes:
                with self.subTest(shape=shape):
                    source = root / 'source.md'; target = root / 'plain.txt'
                    source.write_text('First.\n\n' + shape, encoding='utf-8')
                    with contextlib.redirect_stderr(io.StringIO()) as error:
                        self.assertEqual(2, post_text.main([str(source), str(target)]))
                    self.assertIn('line 3:', error.getvalue())
                    self.assertFalse(target.exists())

    def test_nested_emphasis_escaped_characters_and_comments(self):
        self.assertEqual('A title\n\nBold italic code.\n', post_text.render('# A title\n\n<!-- working -->\n\n**Bold *italic* `code`.**\n'))
        self.assertEqual('a * b _ c ` d \\ e', post_text.render(r'a \* b \_ c \` d \\ e'))

    def test_grader_refuses_one_character_or_line_ending_difference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'critique.md').write_text('**Heading**\n\nProse & text.\n', encoding='utf-8')
            target = root / 'critique.txt'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, post_text.main([str(root / 'critique.md'), str(target)]))
            self.assertFalse(peer_critique_scan.plain_text_gate(root)[0])
            original = target.read_bytes()
            for changed in (original + b'x', original.replace(b'\n', b'\r\n')):
                target.write_bytes(changed)
                self.assertTrue(peer_critique_scan.plain_text_gate(root)[0])

if __name__ == '__main__':
    unittest.main()
