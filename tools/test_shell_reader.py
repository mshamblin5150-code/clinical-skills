"""Generic shell reading shared by tracker publication and AAR grading."""

import unittest

import shell_reader


class ExecutableCallsAreCommandPositionAndQuoteAware(unittest.TestCase):
    def test_environment_prefix_reaches_the_command(self):
        calls = list(shell_reader.executable_calls("env TOKEN=x gh issue comment 834", "gh"))
        self.assertEqual(calls[0][0][calls[0][1]:calls[0][1] + 3], ["gh", "issue", "comment"])

    def test_quoted_and_argument_mentions_are_not_commands(self):
        for command in ('echo "gh issue comment"', "printf x gh issue comment"):
            with self.subTest(command=command):
                self.assertFalse(shell_reader.has_executable(command, "gh"))

    def test_a_later_compound_command_is_found(self):
        self.assertTrue(shell_reader.has_executable("echo ready && gh issue view 834", "gh"))


if __name__ == "__main__":
    unittest.main()
