"""Cover ``voice_corpus``'s reply walk, its partition and its exit statuses.

Every export here is built in this file and a temp directory, on
``test_name_index``'s arrangement and for its reason: **the real export is one
large file on one machine, it is gitignored where it is mined to, and three years
of a working nurse's chat history carries patient material.** Nothing here reads
it, and no count taken against it is asserted anywhere -- those live in the
module's own docstring beside the command that reprints them. *(Its size in
megabytes was stated here and in ``CLAUDE.md`` until the standards axis priced it:
that file's own byte count reads two ways depending on the convention, which
``CLAUDE.md`` records as the trap that has already produced two published figures
for one artifact.)*

phi-scan: synthetic

The prose in these fixtures is invented. It is shaped like the corpus's -- a
typed message, a pasted document, a smoothing pass's reply -- because the shape
is what the parser reads.

**The load-bearing class is ``TheReplyWalkDescendsPastInterleavedNodes``**, and
it is pointed at a recorded defect rather than a hypothetical one:
[#388](https://github.com/mshamblin5150-code/clinical-skills/issues/388)'s first
pass took a user node's immediate child and gave up unless it was an assistant
message with text, and undercounted the paired versions accordingly. **The figures
are ``voice_corpus``'s docstring's to state and are deliberately not repeated
here** -- an earlier draft of this docstring carried them three lines above the
sentence promising it did not, which is
[#143](https://github.com/mshamblin5150-code/clinical-skills/issues/143) at the
shortest range this file has recorded.

**A one-hop walk fails that class**, checked by mutation before it was believed.
The failure direction is the one worth naming: no error, no unparsed remainder,
and every record it did find was correct -- *partial coverage reading as
complete*, which ``CLAUDE.md``'s extractor-coverage rule exists for.

**And one class pins the partition.** Every user message lands in exactly one
class and the classes sum to the independently derived population; if it ever
fails, the fix is a new class and never the assertion, because a message the
matcher cannot recognize is the one it also cannot count as unread.
"""

from __future__ import annotations

import ast
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import voice_corpus
from voice_corpus import (
    CLEAN,
    FOUND,
    NOT_READ,
    Population,
    classify_user_message,
    load_export,
    main,
    partition,
    reply_to,
    user_messages,
)

MARKER = "Zzyzx-marker-9174"

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"


def normalized(text):
    """Collapse whitespace before comparing prose.

    ``test_run_record_claim``'s finding: a phrase hard-wrapped across two lines is
    invisible to a substring search, so a check that reads the raw file reports a
    clean absence about a file that names the thing.
    """
    return " ".join(text.split())


def node(node_id, parent, children, message=None):
    return {"id": node_id, "parent": parent, "children": list(children), "message": message}


def message(role, text, content_type="text", create_time=1.0):
    return {
        "id": f"m-{role}-{abs(hash(text)) % 100000}",
        "author": {"role": role, "name": None, "metadata": {}},
        "create_time": create_time,
        "content": {"content_type": content_type, "parts": [text]},
    }


def conversation(nodes, conversation_id="conv-1", create_time=1_700_000_000.0, title="A title"):
    """One conversation whose ``mapping`` is the nodes given, keyed by id."""
    return {
        "id": conversation_id,
        "conversation_id": conversation_id,
        "title": title,
        "create_time": create_time,
        "mapping": {n["id"]: n for n in nodes},
    }


def linear(*messages, conversation_id="conv-1", **kwargs):
    """A conversation whose nodes are a straight chain, root first."""
    nodes = [node("root", None, ["n0"])]
    for index, msg in enumerate(messages):
        children = [f"n{index + 1}"] if index + 1 < len(messages) else []
        nodes.append(node(f"n{index}", f"n{index - 1}" if index else "root", children, msg))
    return conversation(nodes, conversation_id=conversation_id, **kwargs)


def export_at(directory, conversations):
    path = Path(directory) / "conversations.json"
    path.write_text(json.dumps(conversations), encoding="utf-8")
    return path


def run(argv):
    """Drive ``main`` and return its status with both streams."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = main(argv)
    return status, out.getvalue(), err.getvalue()


class TheReplyWalkDescendsPastInterleavedNodes(unittest.TestCase):
    """#388's recorded defect: the reply is frequently not the immediate child.

    A ChatGPT export interleaves system, tool and reasoning nodes between a user
    message and the assistant's answer, so the reply is a grandchild or deeper.
    **A one-hop walk reports a complete-looking floor**, which is why every case
    here asserts the answer is found rather than that some answer exists.
    """

    def walk(self, *messages):
        conv = linear(*messages)
        user = next(
            n["id"] for n in conv["mapping"].values()
            if n["message"] and n["message"]["author"]["role"] == "user"
        )
        return reply_to(conv["mapping"], user)

    def test_the_immediate_child_is_the_reply(self):
        found = self.walk(message("user", "raw sentence"), message("assistant", "smoothed"))
        self.assertEqual(found.text, "smoothed")

    def test_a_reply_behind_a_tool_node_is_found(self):
        found = self.walk(
            message("user", "raw sentence"),
            message("tool", "search results", content_type="tether_quote"),
            message("assistant", "smoothed"),
        )
        self.assertEqual(found.text, "smoothed")

    def test_a_reply_behind_reasoning_and_system_nodes_is_found(self):
        found = self.walk(
            message("user", "raw sentence"),
            message("assistant", "thinking", content_type="thoughts"),
            message("system", ""),
            message("assistant", "recap", content_type="reasoning_recap"),
            message("assistant", "smoothed"),
        )
        self.assertEqual(found.text, "smoothed")

    def test_an_empty_assistant_message_is_not_the_reply(self):
        found = self.walk(
            message("user", "raw sentence"),
            message("assistant", "   "),
            message("assistant", "smoothed"),
        )
        self.assertEqual(found.text, "smoothed")

    def test_a_user_message_with_no_assistant_below_it_has_no_reply(self):
        self.assertIsNone(self.walk(message("user", "raw sentence")))

    def test_the_nearest_assistant_wins_across_branches(self):
        """Where the tree forks, the shallowest assistant text is the answer.

        **This is not a claim about regenerated turns**, which sit at *equal*
        depth and are settled by nothing here -- the module's docstring says so.
        What it pins is that a deeper branch does not beat a nearer reply.
        """
        conv = conversation([
            node("root", None, ["u"]),
            node("u", "root", ["deep", "shallow"], message("user", "raw sentence")),
            node("deep", "u", ["deeper"], message("tool", "x", content_type="tether_quote")),
            node("deeper", "deep", [], message("assistant", "second draft")),
            node("shallow", "u", [], message("assistant", "first draft")),
        ])
        self.assertEqual(reply_to(conv["mapping"], "u").text, "first draft")

    def test_a_cycle_does_not_hang(self):
        conv = conversation([
            node("root", None, ["u"]),
            node("u", "root", ["a"], message("user", "raw sentence")),
            node("a", "u", ["b"], None),
            node("b", "a", ["a"], None),
        ])
        self.assertIsNone(reply_to(conv["mapping"], "u"))

    def test_a_child_id_absent_from_the_mapping_is_survived(self):
        conv = conversation([
            node("root", None, ["u"]),
            node("u", "root", ["gone", "a"], message("user", "raw sentence")),
            node("a", "u", [], message("assistant", "smoothed")),
        ])
        self.assertEqual(reply_to(conv["mapping"], "u").text, "smoothed")


class EveryUserMessageLandsInExactlyOneClass(unittest.TestCase):
    """The partition is the coverage claim, and it sums to the population.

    ``CLAUDE.md``'s rule: the population is derived independently of the
    extraction, and the unread remainder prints on every run. A class that
    recognizes nothing cannot count it as unread, so an unrecognized shape is a
    named class of its own rather than a silent drop.
    """

    def classify(self, content_type, parts):
        return classify_user_message({"content_type": content_type, "parts": parts})

    def test_typed_prose(self):
        self.assertEqual(self.classify("text", ["a typed sentence"]).kind, "typed")

    def test_an_empty_text_message_is_its_own_class(self):
        self.assertEqual(self.classify("text", ["   "]).kind, "empty")

    def test_a_multimodal_message_carrying_a_string_is_typed_beside_an_image(self):
        found = self.classify("multimodal_text", [
            {"content_type": "image_asset_pointer"}, "a typed caption",
        ])
        self.assertEqual(found.kind, "multimodal-typed")
        self.assertEqual(found.text, "a typed caption")

    def test_a_dictated_message_is_not_typed_prose(self):
        """Spoken and machine-transcribed. His words, not his typing."""
        found = self.classify("multimodal_text", [
            {"content_type": "audio_transcription", "text": "spoken aloud"},
        ])
        self.assertEqual(found.kind, "audio-transcription")

    def test_the_custom_instructions_blob_is_its_own_class(self):
        self.assertEqual(
            classify_user_message({"content_type": "user_editable_context",
                                   "user_instructions": "be blunt"}).kind,
            "editable-context",
        )

    def test_an_unrecognized_content_type_is_named_rather_than_dropped(self):
        self.assertEqual(self.classify("some_future_shape", ["x"]).kind, "unclassified")

    def test_the_classes_sum_to_the_population(self):
        conv = linear(
            message("user", "typed"),
            message("assistant", "reply"),
            message("user", "", content_type="some_future_shape"),
            message("user", "   "),
        )
        found = partition([conv])
        self.assertEqual(
            sum(found.by_kind.values()), found.population.user_messages,
            "the partition must account for every user message in the mapping",
        )

    def test_a_class_this_module_does_not_know_is_a_finding(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(
                message("user", "typed"), message("assistant", "reply"),
                message("user", "x", content_type="some_future_shape"),
            )])
            status, out, _ = run([str(path)])
        self.assertEqual(status, FOUND)
        self.assertIn("unclassified", out)


class ThePopulationIsDerivedIndependently(unittest.TestCase):
    """It is counted off the mapping walk, never off what the matcher read."""

    def test_the_conversation_count_is_the_top_level_list(self):
        found = partition([linear(message("user", "a"), message("assistant", "b")),
                           linear(message("user", "c"), conversation_id="conv-2")])
        self.assertEqual(found.population.conversations, 2)

    def test_every_role_is_counted_even_where_nothing_is_extracted(self):
        found = partition([linear(
            message("user", "a"),
            message("tool", "results", content_type="tether_quote"),
            message("assistant", "b"),
        )])
        self.assertEqual(found.population.by_role["tool"], 1)

    def test_a_node_with_no_message_is_not_a_message(self):
        conv = conversation([
            node("root", None, ["u"]),
            node("u", "root", [], message("user", "a")),
        ])
        self.assertEqual(partition([conv]).population.messages, 1)


class TheDateComesFromCreateTime(unittest.TestCase):
    """#388 trap 5: a previous pass invented a dating method and it was wrong.

    Decoding the conversation UUID's leading hex as a Unix timestamp is right for
    about four in five and wild for the rest -- a 2024 conversation decoding to
    1979. The export carries ``create_time`` on every conversation, so a
    conversation without one is reported rather than dated another way.
    """

    def test_the_stamp_is_read_from_the_field(self):
        conv = linear(message("user", "a"), create_time=1_725_000_000.0)
        self.assertEqual(partition([conv]).dated[0].year, 2024)

    def test_a_conversation_with_no_create_time_is_a_finding(self):
        conv = linear(message("user", "a"))
        del conv["create_time"]
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [conv])
            status, out, _ = run([str(path)])
        self.assertEqual(status, FOUND)
        self.assertIn("undated", out)

    def test_the_hex_of_the_conversation_id_is_never_consulted(self):
        """The id here decodes to 1979; the stamp says 2024, and the stamp wins."""
        conv = linear(
            message("user", "a"),
            conversation_id="12345678-0000-0000-0000-000000000000",
            create_time=1_725_000_000.0,
        )
        self.assertEqual(partition([conv]).dated[0].year, 2024)

    def test_a_decodable_id_does_not_rescue_a_conversation_with_no_stamp(self):
        """**The discriminating case, and the one a first pass here did not write.**

        A conversation whose id is *not* hex fails a decode by accident, so a test
        using one passes whether the fallback exists or not. Reinstating the UUID
        decode survived the whole suite until this case was added -- the defect
        #388 trap 5 records, reintroducible with every light green. The id below
        decodes to 1979 and the conversation must still read as undated.
        """
        conv = linear(message("user", "a"), conversation_id="12345678-0000-0000-0000-000000000000")
        del conv["create_time"]
        found = partition([conv])
        self.assertEqual(found.undated, 1)
        self.assertEqual(found.dated, [])


class DistinctConversationsAreTheUnit(unittest.TestCase):
    """#388 trap 2: one memoir passage recurs about twenty times.

    Counting messages reads a paste as twenty attestations of one thing, which is
    the two-sample rule satisfied by a single document.
    """

    def test_a_paste_repeated_in_one_conversation_is_one_conversation(self):
        conv = linear(
            message("user", "the anvil passage"),
            message("assistant", "reply"),
            message("user", "the anvil passage"),
            message("assistant", "reply again"),
        )
        found = voice_corpus.select([conv], "anvil")
        self.assertEqual(found.messages, 2)
        self.assertEqual(found.conversations, 1)

    def test_the_same_phrase_in_two_conversations_is_two(self):
        found = voice_corpus.select([
            linear(message("user", "the anvil passage"), conversation_id="conv-1"),
            linear(message("user", "the anvil passage"), conversation_id="conv-2"),
        ], "anvil")
        self.assertEqual(found.conversations, 2)

    def test_the_report_states_both(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(
                message("user", "the anvil passage"), message("assistant", "r"),
                message("user", "the anvil passage again"),
            )])
            _, out, _ = run([str(path), "--match", "anvil"])
        self.assertIn("2 message(s)", out)
        self.assertIn("1 conversation(s)", out)

    def test_an_assistant_message_never_matches(self):
        """The corpus is mined for his writing; the machine's is not his."""
        found = voice_corpus.select(
            [linear(message("user", "nothing here"), message("assistant", "the anvil"))],
            "anvil",
        )
        self.assertEqual(found.messages, 0)


class ThePairFloorReportsWhatItCouldNotReach(unittest.TestCase):
    """A pair is a mechanical floor; whether the reply is a rewrite is a reading."""

    def test_a_matched_message_with_a_reply_is_a_pair(self):
        found = voice_corpus.pairs([linear(
            message("user", "improve this: raw"), message("assistant", "smoothed"),
        )], "improve this")
        self.assertEqual(len(found.records), 1)
        self.assertEqual(found.missing_reply, 0)

    def test_a_matched_message_with_no_reply_is_counted_and_named(self):
        found = voice_corpus.pairs(
            [linear(message("user", "improve this: raw"))], "improve this",
        )
        self.assertEqual(found.missing_reply, 1)

    def test_the_hop_distribution_makes_a_one_hop_regression_visible(self):
        found = voice_corpus.pairs([linear(
            message("user", "improve this: raw"),
            message("tool", "x", content_type="tether_quote"),
            message("assistant", "smoothed"),
        )], "improve this")
        self.assertEqual(found.hops[2], 1)
        self.assertEqual(found.hops.get(1, 0), 0)

    def test_a_paste_repeated_in_one_conversation_is_one_conversation(self):
        """Trap 2 reaches the pair report and not only ``select``."""
        found = voice_corpus.pairs([linear(
            message("user", "improve this: raw"), message("assistant", "smoothed"),
            message("user", "improve this: raw again"), message("assistant", "smoothed again"),
        )], "improve this")
        self.assertEqual(len(found.records), 2)
        self.assertEqual(found.conversations, 1)

    def test_the_pair_report_states_both_figures(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(
                message("user", "improve this: raw"), message("assistant", "smoothed"),
                message("user", "improve this: more"), message("assistant", "smoothed too"),
            )])
            _, out, _ = run([str(path), "--pairs", "--match", "improve this"])
        self.assertIn("2 pair(s) in 1 conversation(s)", out)

    def test_the_report_says_a_pair_is_not_a_rewrite(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(
                message("user", "improve this: raw"), message("assistant", "smoothed"),
            )])
            _, out, _ = run([str(path), "--pairs", "--match", "improve this"])
        self.assertIn("whether a reply is a rewrite of the same content is a reading", out)


class TheTextJoinIsOneHelper(unittest.TestCase):
    """Both sides of a pair have to agree about what counts as text.

    ``case_study_scan``'s precedent for holding no second parser: the classifier
    and the reply walk read a ``parts`` list the same way because they call the
    same function, not because two comprehensions were written alike.
    """

    def test_a_non_list_is_empty(self):
        self.assertEqual(voice_corpus.joined_text(None), "")

    def test_non_string_parts_are_skipped(self):
        self.assertEqual(
            voice_corpus.joined_text([{"content_type": "image_asset_pointer"}, " a "]), "a"
        )

    def test_both_sites_call_it(self):
        source = (REPO_ROOT / "tools" / "voice_corpus.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        callers = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and any(
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Name)
                and inner.func.id == "joined_text"
                for inner in ast.walk(node)
            )
        }
        self.assertEqual(callers, {"classify_user_message", "reply_to"})


class TheReplyWalkStopsAtTheNextQuestion(unittest.TestCase):
    """A later turn's reply is not this turn's reply.

    #388's defect was a one-hop walk reporting a floor that looked like a total.
    **This is the same defect with the sign flipped**: descending through a user
    node joins a request to the answer to a *different* message, which fails
    ``voice.md`` §5's *same author, same claim, same audience* while counting as a
    pair. Measured against the export before the rule changed: 162 of 17,438
    joined replies were the wrong turn's.

    The discriminating case needs an assistant node with **no text** between the
    two questions, because that is what makes the walk keep going. With a
    text-carrying reply in that slot the walk stops there anyway and the rule is
    never exercised -- a test that passes for a reason other than the one beside
    it is what a green run hides.
    """

    def interleaved(self):
        return {
            "u1": {"id": "u1", "children": ["a0"], "message": {
                "author": {"role": "user"},
                "content": {"content_type": "text", "parts": ["FIRST"]}}},
            "a0": {"id": "a0", "children": ["u2"], "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "text", "parts": [""]}}},
            "u2": {"id": "u2", "children": ["a2"], "message": {
                "author": {"role": "user"},
                "content": {"content_type": "text", "parts": ["SECOND"]}}},
            "a2": {"id": "a2", "children": [], "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "text", "parts": ["answer to SECOND"]}}},
        }

    def test_the_next_questions_answer_is_not_borrowed(self):
        self.assertIsNone(voice_corpus.reply_to(self.interleaved(), "u1"))

    def test_the_next_question_still_gets_its_own(self):
        """The rule narrows the first turn and must leave the second alone."""
        answer = voice_corpus.reply_to(self.interleaved(), "u2")
        self.assertEqual(answer.text, "answer to SECOND")
        self.assertEqual(answer.hops, 1)

    def test_a_tool_node_is_still_walked_through(self):
        """Only a *user* node stops the descent; interleaving is the whole reason
        the walk is breadth-first rather than one hop."""
        mapping = {
            "u1": {"id": "u1", "children": ["t"], "message": {
                "author": {"role": "user"},
                "content": {"content_type": "text", "parts": ["q"]}}},
            "t": {"id": "t", "children": ["a"], "message": {
                "author": {"role": "tool"},
                "content": {"content_type": "text", "parts": ["tool output"]}}},
            "a": {"id": "a", "children": [], "message": {
                "author": {"role": "assistant"},
                "content": {"content_type": "text", "parts": ["reply"]}}},
        }
        self.assertEqual(voice_corpus.reply_to(mapping, "u1").hops, 2)

    def test_the_pair_report_counts_it_as_missing_rather_than_joining_it(self):
        conv = {"conversation_id": "c1", "create_time": 1_700_000_000,
                "mapping": self.interleaved()}
        found = voice_corpus.pairs([conv], "FIRST")
        self.assertEqual(found.records, [])
        self.assertEqual(found.missing_reply, 1)


class AFailedWriteIsNotAFailedRead(unittest.TestCase):
    """``--out`` raising is not a finding about the corpus.

    The first version let ``OSError`` escape ``main``: an absent parent directory
    was a traceback and **exit 1**, which is this module's code for a finding --
    and the report never printed at all, contradicting the docstring's *a refused
    write is not a refused read*. ``docx_write`` carries the recorded precedent
    for an uncaught ``OSError`` at a write boundary. **Both axes of
    ``/code-review`` found this independently.**
    """

    def test_an_unwritable_target_leaves_the_report_standing(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(message("user", "a"), message("assistant", "b"))])
            target = Path(tmp) / "no-such-directory" / "mined.md"
            status, out, err = run([str(path), "--out", str(target)])
        self.assertEqual(status, CLEAN)
        self.assertIn("could not write", err)
        self.assertIn("user message(s)", out)
        self.assertIn("what a clean run does not establish", out)


class ThePairReportMeasuresTheDirection(unittest.TestCase):
    """#388 comment 1: *each record now carries `his chars` and `generic chars`,
    so the direction of the smoothing pass is measurable per pair rather than only
    readable.* A character count is a count, so it belongs in the default report;
    behind ``--show`` it would be readable only, which is what that sentence is
    against."""

    def scan(self):
        conv = linear(message("user", "improve this"), message("assistant", "a much longer reply"))
        return voice_corpus.partition([conv]), conv

    def test_the_counts_are_in_the_default_report(self):
        scan, conv = self.scan()
        joined = voice_corpus.pairs([conv], "improve")
        printed = chr(10).join(voice_corpus.format_report(scan, None, joined))
        self.assertIn("character(s) against the replies'", printed)
        self.assertIn("the reply is longer in 1 of 1 pair(s)", printed)

    def test_the_default_report_still_carries_no_corpus_text(self):
        scan, conv = self.scan()
        joined = voice_corpus.pairs([conv], "improve")
        printed = chr(10).join(voice_corpus.format_report(scan, None, joined))
        self.assertNotIn("a much longer reply", printed)


class EveryClassNamedIsAClassPrinted(unittest.TestCase):
    """A class the report cannot print is a silent subtraction from the denominator.

    ``format_report`` iterates ``KINDS``, and ``Scan.by_kind`` is a ``Counter``.
    So a branch of ``classify_user_message`` returning a name ``KINDS`` does not
    hold is **counted, never printed, and never reaches the exit status** -- while
    ``test_the_classes_sum_to_the_population`` stays green, because the sum is
    over the counter rather than over what was shown. That is *partial coverage
    reading as complete*, which is the defect this module exists against, and it
    would have arrived inside it.

    By AST rather than by substring, on ``test_console_codec.py``'s instrument and
    for its reason: this module's docstring names several of these strings in
    prose, so a text search is satisfied by the paragraph explaining a class
    rather than by the branch producing one.

    **The ceiling is declared and it is the reason the walk refuses rather than
    skips.** A first argument that is neither a literal nor a choice between two
    literals -- a local variable, a lookup, a name -- is opaque here, and
    ``tracker_bodies.grade`` carries the recorded instance of an assignment making
    a completeness walk pass over a set containing nothing at all. So an
    unreadable argument fails the test instead of being ignored.
    """

    def named_classes(self):
        source = (REPO_ROOT / "tools" / "voice_corpus.py").read_text(encoding="utf-8")
        found = set()
        for node in ast.walk(ast.parse(source)):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
                continue
            if node.func.id != "Classified" or not node.args:
                continue
            first = node.args[0]
            options = [first.body, first.orelse] if isinstance(first, ast.IfExp) else [first]
            for option in options:
                self.assertIsInstance(
                    option,
                    ast.Constant,
                    "a Classified(...) class name this walk cannot read is not a class "
                    "it can vouch for -- name the string at the call site",
                )
                found.add(option.value)
        return found

    def test_the_walk_is_live(self):
        """Asserting a clean tree proves only that the walk found nothing."""
        named = self.named_classes()
        self.assertGreaterEqual(len(named), 4)
        self.assertIn("typed", named)
        self.assertIn("unclassified", named)

    def test_every_class_the_code_names_is_one_the_report_prints(self):
        self.assertEqual(self.named_classes() - set(voice_corpus.KINDS), set())

    def test_every_class_the_report_prints_is_one_the_code_names(self):
        """The other direction, so a retired branch cannot leave a row that is
        always zero and reads as a measured absence."""
        self.assertEqual(set(voice_corpus.KINDS) - self.named_classes(), set())

    def test_the_prose_classes_are_classes(self):
        self.assertEqual(set(voice_corpus.PROSE_KINDS) - set(voice_corpus.KINDS), set())

    def test_a_class_outside_kinds_would_be_counted_and_never_shown(self):
        """The defect the walk exists for, driven rather than described."""
        scan = voice_corpus.Scan(
            population=voice_corpus.Population(1, 1, 1, {"user": 1}),
            by_kind={"typed": 0, "smoke-signal": 1},
            dated=[],
            undated=0,
            prose_chars=0,
        )
        printed = "\n".join(voice_corpus.format_report(scan))
        self.assertNotIn("smoke-signal", printed)


class CountsOnlyByDefault(unittest.TestCase):
    """``--show`` output is PHI; the default report is safe to paste.

    Driven by a marker rather than argued, on ``reference_scan``'s method.
    """

    def export(self, tmp):
        return export_at(tmp, [linear(
            message("user", f"improve this: {MARKER} and the rest"),
            message("assistant", f"smoothed {MARKER}"),
        )])

    def test_no_corpus_text_reaches_the_default_report(self):
        with TemporaryDirectory() as tmp:
            _, out, err = run([str(self.export(tmp)), "--match", MARKER])
        self.assertNotIn(MARKER, out + err)

    def test_no_corpus_text_reaches_the_default_pairs_report(self):
        with TemporaryDirectory() as tmp:
            _, out, err = run([str(self.export(tmp)), "--pairs", "--match", MARKER])
        self.assertNotIn(MARKER, out + err)

    def test_show_is_what_reveals_it(self):
        with TemporaryDirectory() as tmp:
            _, out, _ = run([str(self.export(tmp)), "--match", MARKER, "--show"])
        self.assertIn(MARKER, out)

    def test_the_default_coverage_report_carries_no_text(self):
        with TemporaryDirectory() as tmp:
            _, out, err = run([str(self.export(tmp))])
        self.assertNotIn(MARKER, out + err)


class TheCeilingIsDeclared(unittest.TestCase):
    """A floor is not proof the extractor recognizes every form."""

    def test_the_report_names_what_it_cannot_reach(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(message("user", "a"), message("assistant", "b"))])
            _, out, _ = run([str(path)])
        for limb in voice_corpus.NOT_REACHED:
            self.assertIn(limb, out)

    def test_the_module_docstring_points_at_the_object_and_copies_no_row(self):
        """[#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s
        repair: a prose copy of a limit fails nothing when it goes stale."""
        doc = voice_corpus.__doc__
        self.assertIn("NOT_REACHED", doc)
        for limb in voice_corpus.NOT_REACHED:
            self.assertNotIn(limb, doc)

    def test_claude_md_points_at_the_object_and_copies_no_row(self):
        """The second place a reader looks, held to the same rule.

        ``CLAUDE.md``'s own section claims a test asserts this; without one the
        claim is the [#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)
        shape it was written to avoid -- a prose edit that fails nothing.
        """
        prose = normalized(CLAUDE_MD.read_text(encoding="utf-8"))
        self.assertIn("voice_corpus.NOT_REACHED", prose)
        for limb in voice_corpus.NOT_REACHED:
            self.assertNotIn(normalized(limb), prose)

    def test_claude_md_names_the_command(self):
        prose = CLAUDE_MD.read_text(encoding="utf-8")
        self.assertIn("python tools/voice_corpus.py", prose)


class ExitStatusDistinguishesNotReading(unittest.TestCase):
    """0 clean, 1 for a finding, 2 for every way of not having read."""

    def test_no_argument(self):
        self.assertEqual(run([])[0], NOT_READ)

    def test_an_absent_file(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(run([str(Path(tmp) / "gone.json")])[0], NOT_READ)

    def test_a_file_that_is_not_json(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "conversations.json"
            path.write_text("not json", encoding="utf-8")
            self.assertEqual(run([str(path)])[0], NOT_READ)

    def test_a_payload_that_is_not_a_list(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "conversations.json"
            path.write_text(json.dumps({"conversations": 788}), encoding="utf-8")
            self.assertEqual(run([str(path)])[0], NOT_READ)

    def test_an_export_with_no_conversation(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(run([str(export_at(tmp, []))])[0], NOT_READ)

    def test_an_export_with_no_user_message(self):
        """Every conversation is the machine's. Nothing here is his writing."""
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(message("assistant", "hello"))])
            status, _, err = run([str(path)])
        self.assertEqual(status, NOT_READ)
        self.assertIn("no user message", err)

    def test_a_clean_export_is_zero(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(message("user", "a"), message("assistant", "b"))])
            self.assertEqual(run([str(path)])[0], CLEAN)

    def test_each_finding_limb_fires_on_its_own(self):
        """**Driven one limb at a time, because together they prove nothing.**

        The first version of this class asserted that a finding *outranks* an
        undated conversation, on ``differential_scan``'s 1-wins-over-2 ordering.
        That reading was vacuous -- undated is itself a finding here, so there was
        never a 2 for it to outrank -- and a single fixture carrying both passed
        whichever limb happened to be live. Both axes of ``/code-review`` found it.
        """
        with TemporaryDirectory() as tmp:
            undated = linear(message("user", "a"))
            del undated["create_time"]
            status, out, _ = run([str(export_at(tmp, [undated]))])
            self.assertEqual(status, FOUND)
            self.assertIn("undated", out)

        with TemporaryDirectory() as tmp:
            unknown = linear(
                message("user", "a"), message("user", "x", content_type="future_shape")
            )
            status, out, _ = run([str(export_at(tmp, [unknown]))])
            self.assertEqual(status, FOUND)
            self.assertIn("unclassified", out)

    def test_both_limbs_together_are_still_one_finding(self):
        conv = linear(message("user", "a"), message("user", "x", content_type="future_shape"))
        del conv["create_time"]
        with TemporaryDirectory() as tmp:
            status, out, _ = run([str(export_at(tmp, [conv]))])
        self.assertEqual(status, FOUND)
        self.assertIn("undated", out)
        self.assertIn("unclassified", out)

    def test_a_match_that_will_not_compile_is_not_a_finding(self):
        """``guidelines_search``'s contract: 1 means a genuine zero about the
        corpus, and a pattern that never compiled consulted no corpus at all."""
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(message("user", "a"), message("assistant", "b"))])
            status, _, err = run([str(path), "--match", "(("])
        self.assertEqual(status, NOT_READ)
        self.assertIn("not a regex", err)

    def test_pairs_with_no_match_is_not_a_silent_clean_run(self):
        """**This module's own subject, rebuilt inside it.** The first version
        printed the coverage report, no pair section, no warning and exit 0."""
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(message("user", "a"), message("assistant", "b"))])
            status, out, err = run([str(path), "--pairs"])
        self.assertEqual(status, NOT_READ)
        self.assertIn("--match", err)
        self.assertNotIn("pair(s)", out)

    def test_show_with_no_match_is_not_a_silent_clean_run(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(message("user", "a"), message("assistant", "b"))])
            status, _, err = run([str(path), "--show"])
        self.assertEqual(status, NOT_READ)
        self.assertIn("--match", err)


class TheLoaderRefusesRatherThanReadingEmpty(unittest.TestCase):
    def test_a_list_member_that_is_not_a_record_is_refused(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "conversations.json"
            path.write_text(json.dumps(["not a conversation"]), encoding="utf-8")
            loaded, why = load_export(path)
        self.assertIsNone(loaded)
        self.assertIsNotNone(why)

    def test_a_conversation_with_no_mapping_is_refused(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "conversations.json"
            path.write_text(json.dumps([{"id": "c"}]), encoding="utf-8")
            loaded, why = load_export(path)
        self.assertIsNone(loaded)
        self.assertIn("mapping", why)

class TheWriteTargetIsRefusedOutsideScratch(unittest.TestCase):
    """A mined record is his own writing and the corpus carries patient material.

    ``name_index.refuse_target``'s rule and its reason, at a second artifact.
    """

    def test_a_path_in_a_checkout_is_refused(self):
        with TemporaryDirectory() as tmp:
            checkout = Path(tmp) / "repo"
            (checkout / ".git").mkdir(parents=True)
            scratch = checkout / "scratch"
            scratch.mkdir()
            self.assertIsNotNone(
                voice_corpus.refuse_target(checkout / "mined.md", scratch=scratch)
            )

    def test_a_path_under_scratch_is_permitted(self):
        with TemporaryDirectory() as tmp:
            checkout = Path(tmp) / "repo"
            (checkout / ".git").mkdir(parents=True)
            scratch = checkout / "scratch"
            scratch.mkdir()
            self.assertIsNone(
                voice_corpus.refuse_target(scratch / "mined.md", scratch=scratch)
            )

    def test_the_written_file_is_the_report_the_console_got(self):
        """**Not an unconditional ``show=True``.** The first version wrote corpus
        text to disk on the strength of a flag nobody passed, which is a PHI
        posture taken by accident while #388's decision 2 is still open.
        """
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(
                message("user", f"improve this: {MARKER}"), message("assistant", "smoothed"),
            )])
            written = Path(tmp) / "mined.md"
            status, _, _ = run([str(path), "--match", MARKER, "--out", str(written)])
            self.assertEqual(status, CLEAN)
            self.assertNotIn(MARKER, written.read_text(encoding="utf-8"))

    def test_show_is_what_puts_text_in_the_written_file(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(
                message("user", f"improve this: {MARKER}"), message("assistant", "smoothed"),
            )])
            written = Path(tmp) / "mined.md"
            run([str(path), "--match", MARKER, "--show", "--out", str(written)])
            self.assertIn(MARKER, written.read_text(encoding="utf-8"))

    def test_a_refused_write_is_not_a_refused_read(self):
        """The run read the whole export and knows what it found."""
        with TemporaryDirectory() as tmp:
            checkout = Path(tmp) / "repo"
            (checkout / ".git").mkdir(parents=True)
            path = export_at(tmp, [linear(message("user", "a"), message("assistant", "b"))])
            status, out, err = run([str(path), "--out", str(checkout / "mined.md")])
        self.assertEqual(status, CLEAN)
        self.assertIn("refusing to write", err)
        self.assertIn("user message(s)", out)


class UserMessagesAreReadInOrder(unittest.TestCase):
    def test_the_conversation_id_travels_with_each_message(self):
        conv = linear(message("user", "a"), message("assistant", "b"), conversation_id="conv-9")
        self.assertEqual(user_messages(conv)[0].conversation_id, "conv-9")

    def test_only_user_messages_come_back(self):
        conv = linear(message("user", "a"), message("assistant", "b"), message("user", "c"))
        self.assertEqual([m.text for m in user_messages(conv)], ["a", "c"])


if __name__ == "__main__":
    unittest.main()
