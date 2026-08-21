"""Cover ``voice_corpus``'s reply walk, its partition and its exit statuses.

Every export here is built in this file and a temp directory, on
``test_name_index``'s arrangement and for its reason: **the real export is one
318 MB file on one machine, it is gitignored where it is mined to, and three
years of a working nurse's chat history carries patient material.** Nothing here
reads it, and no count taken against it is asserted anywhere -- those live in the
module's own docstring beside the command that reprints them.

phi-scan: synthetic

The prose in these fixtures is invented. It is shaped like the corpus's -- a
typed message, a pasted document, a smoothing pass's reply -- because the shape
is what the parser reads.

**The load-bearing class is ``TheReplyWalkDescendsPastInterleavedNodes``**, and
it is pointed at a recorded defect rather than a hypothetical one:
[#388](https://github.com/mshamblin5150-code/clinical-skills/issues/388)'s first
pass took a user node's immediate child and gave up unless it was an assistant
message with text, which reported 85 paired versions where the corpus holds 163.
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
        """A regenerated turn forks the tree; the shallowest reply is the answer."""
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

    def test_the_report_says_a_pair_is_not_a_rewrite(self):
        with TemporaryDirectory() as tmp:
            path = export_at(tmp, [linear(
                message("user", "improve this: raw"), message("assistant", "smoothed"),
            )])
            _, out, _ = run([str(path), "--pairs", "--match", "improve this"])
        self.assertIn("whether a reply is a rewrite of the same content is a reading", out)


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

    def test_a_finding_outranks_an_undated_conversation(self):
        """``differential_scan``'s ordering: 1 wins, and the banner rides along."""
        conv = linear(message("user", "a"), message("user", "x", content_type="future_shape"))
        del conv["create_time"]
        with TemporaryDirectory() as tmp:
            status, out, _ = run([str(export_at(tmp, [conv]))])
        self.assertEqual(status, FOUND)
        self.assertIn("undated", out)
        self.assertIn("unclassified", out)


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
