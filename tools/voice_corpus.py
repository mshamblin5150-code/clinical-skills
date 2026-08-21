"""Read a ChatGPT conversation export into the pieces a voice model is built from.

    python tools/voice_corpus.py <conversations.json>
    python tools/voice_corpus.py <export> --match "improve this"
    python tools/voice_corpus.py <export> --pairs --match "improve this"
    python tools/voice_corpus.py <export> --match "the abyss" --show   # PHI

[#213](https://github.com/mshamblin5150-code/clinical-skills/issues/213) built
``scratch/voice-model.md`` from 46 supplied documents.
[#388](https://github.com/mshamblin5150-code/clinical-skills/issues/388) located a
corpus roughly forty times that size -- the clinician's own chat export -- and
``skills/practicum-case-study/reference/voice.md`` §3 argues for it directly:
*a sample written in order to demonstrate a voice is a performance of one*, and
nobody proofreads a prompt.

**This is a `tools/` module rather than the throwaway script it started as, and
the argument is a recorded defect rather than tidiness.** #388's first mining pass
took a user node's **immediate child** and gave up unless it was an assistant
message with text. A ChatGPT export interleaves system, tool and reasoning nodes,
so the reply is frequently a grandchild or deeper: that walk reported **85**
paired versions where the corpus holds **163**. Corpus-wide the same walk reaches
**10,857 of 18,376** replies, measured 2026-08-20.

**The failure direction is what earns the test.** There was no error, no unparsed
remainder, and every record it did find was correct -- a complete-looking floor
with nothing announcing it as one. That is this repo's most repeated defect,
*partial coverage reading as complete*, which ``voice.md`` §7 names in as many
words and which ``CLAUDE.md``'s extractor-coverage rule exists for: **a matcher
never gets to turn a partial read into a clean whole.**

The population is independent of the extraction
-----------------------------------------------

``Population`` is counted off the **mapping walk** -- every node carrying a
message, by role -- and never off what the content-type matcher recognized. Then
``partition`` files every user message into exactly one class and the classes sum
to that denominator, so the unread remainder prints on every run. **An
unrecognized ``content_type`` is a named class rather than a silent drop**, and it
is a finding: a rule that cannot recognize a member cannot count it as unread, so
the only honest place for one is its own row.

The classes are not all prose, and that distinction is the point. A message may be
typed, typed beside an image, **dictated and machine-transcribed**, the custom
instructions blob, an attachment with no words, or empty. Only the first two are
unwatched typing. Folding a dictation into a rhythm measurement would put a
transcriber's sentence boundaries into a claim about how he writes.

Dating
------

**``create_time``, and nothing else.** #388 trap 5: a previous pass invented a
dating method by decoding the conversation UUID's leading hex as a Unix
timestamp. It is right for about four in five and wild for the rest -- a
2024-09-04 conversation decoding to 1979 -- and every drift claim rested on it.
The export carries the field on every conversation, so one that lacks it is
reported **undated** rather than dated another way.

The unit is a distinct conversation
-----------------------------------

#388 trap 2: one memoir passage recurs about twenty times, so a message count
reads a single paste as twenty attestations -- ``voice.md`` §4's two-sample rule
satisfied by one document. ``select`` reports both figures and neither alone.

What a pair is, and what it is not
----------------------------------

``pairs`` is a **mechanical floor**: a matched user message and the nearest
assistant message with text below it. Whether that reply is a *rewrite of the same
content* is a reading, and #388 measured the gap -- 163 records carry both halves
and **36** are genuine rewrites; the rest are the model answering a question,
ghost-writing, or imitating a voice it had been trained on. That last is
``voice.md`` §5's own warning: a pair whose generic half is the build's imitation
is the build grading itself. **So the command prints the qualification on every
run rather than only when it fires**, and the hop distribution prints beside it so
a one-hop regression is visible rather than silent.

Counts only, and ``--show`` is PHI
----------------------------------

The export is the clinician's own writing and three years of a working nurse's
chat history carries patient material. Nothing this prints by default is corpus
text. **``--show`` output is PHI: read it, do not paste it** -- deliberately not
``reference_scan``'s exception, whose output is bounded by what its code can draw
from, because this one's is bounded by nothing.

A ``--out`` target must be under ``scratch/`` or outside every checkout, on
``name_index.refuse_target``'s rule and for its reason. **A refused write is not a
refused read**: the run read the whole export and the report stands.

Exit status
-----------

0 clean, 1 for a finding, **2 for every way of not having read**: no argument, no
file, a payload that is not a JSON list of conversations, no conversation in it,
and no user message in any of them. **Where a finding and an undated conversation
both hold, 1 wins**, on ``differential_scan``'s ordering, and the banner prints
beside it so the finding reads as a floor.

What it cannot reach is ``NOT_REACHED``, and this docstring deliberately copies no
row of it -- [#241](https://github.com/mshamblin5150-code/clinical-skills/issues/241)'s
repair: a prose edit to a limit fails nothing, so a limit written twice goes stale
in whichever copy the reader is not holding.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from console_codec import use_utf8
from repo_root import enclosing_checkout, scratch_root

CLEAN = 0
FOUND = 1
NOT_READ = 2

#: Every message class this module recognizes. **The prose ones are the first
#: two**, and the split is load-bearing rather than descriptive: a dictation is
#: his words in a transcriber's sentences, and the instructions blob is a
#: standing directive rather than writing to a reader.
PROSE_KINDS = ("typed", "multimodal-typed")
KINDS = PROSE_KINDS + (
    "audio-transcription",
    "editable-context",
    "attachment-only",
    "empty",
    "unclassified",
)

#: What a clean run does **not** establish. Printed on every run, on
#: [#258](https://github.com/mshamblin5150-code/clinical-skills/issues/258)'s
#: ruling -- a reader who learns to read a qualifier reads its absence as the
#: stronger claim. One object rather than a second prose copy, on
#: ``reference_scan.NOT_REACHED``'s arrangement.
NOT_REACHED = (
    "a message stored anywhere but a conversation's mapping is invisible to the "
    "population and to the extraction alike, so the denominator is a floor",
    "whether a reply is a rewrite of the same content is a reading, not a match",
    "a reply may be the machine imitating him, which is the build grading its own "
    "imitation rather than a control group",
    "text present only in an assistant message has three explanations that "
    "counting cannot separate: the machine drafted it, an upload's body was not "
    "captured, or the machine transcribed his handwriting",
    "a pasted third-party document is matched exactly as his own typing is",
)


@dataclass(frozen=True)
class Classified:
    """One user message's class and whatever prose it carries."""

    kind: str
    text: str = ""


@dataclass(frozen=True)
class Message:
    conversation_id: str
    node_id: str
    kind: str
    text: str


@dataclass(frozen=True)
class Reply:
    """An assistant message with text, and how far below the user node it sat."""

    text: str
    hops: int


@dataclass(frozen=True)
class Population:
    """Derived from the mapping walk, never from what the matcher read."""

    conversations: int
    messages: int
    user_messages: int
    by_role: dict


@dataclass
class Scan:
    population: Population
    by_kind: dict
    dated: list
    undated: int
    prose_chars: int


@dataclass
class Selection:
    messages: int
    conversations: int
    records: list = field(default_factory=list)


@dataclass
class Pairs:
    records: list
    missing_reply: int
    hops: dict


def load_export(path: Path):
    """The conversations, or ``(None, why not)``.

    **A payload that is not a list of conversations is refused rather than read as
    empty**, which is ``guidelines_extract``'s manifest contract and its reason: a
    count where the list belongs would otherwise scan clean over nothing.
    """
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{path} does not exist"
    except (OSError, UnicodeDecodeError) as why:
        return None, f"{path} could not be read: {why}"
    except json.JSONDecodeError as why:
        return None, f"{path} is not JSON: {why}"
    if not isinstance(loaded, list):
        return None, f"{path} is not a JSON list of conversations"
    for index, record in enumerate(loaded):
        if not isinstance(record, dict):
            return None, f"{path} member {index} is not a conversation record"
        if not isinstance(record.get("mapping"), dict):
            return None, f"{path} member {index} carries no mapping"
    return loaded, None


def classify_user_message(content) -> Classified:
    """Which class one user message's ``content`` falls into.

    **Every branch names a class and nothing falls through**, because the fallthrough
    is what a silent drop looks like: ``unclassified`` is a finding, so a shape
    this has never seen costs a red run rather than a quiet subtraction from the
    denominator.
    """
    if not isinstance(content, dict):
        return Classified("unclassified")
    content_type = content.get("content_type")
    if content_type == "user_editable_context":
        return Classified("editable-context")
    parts = content.get("parts")
    if content_type in ("text", "multimodal_text") and isinstance(parts, list):
        typed = "".join(part for part in parts if isinstance(part, str)).strip()
        if typed:
            return Classified("typed" if content_type == "text" else "multimodal-typed", typed)
        if content_type == "text":
            return Classified("empty")
        # **A dictation is not typing**, and an attachment with no words is not
        # prose. Both are counted so the denominator holds, and neither reaches a
        # measurement of how he writes.
        for part in parts:
            if isinstance(part, dict) and part.get("content_type") == "audio_transcription":
                return Classified("audio-transcription", str(part.get("text") or ""))
        return Classified("attachment-only")
    return Classified("unclassified")


def user_messages(conversation) -> list:
    """Every user message in one conversation, each carrying its class."""
    conversation_id = conversation.get("conversation_id") or conversation.get("id") or ""
    found = []
    for node_id, node in conversation.get("mapping", {}).items():
        message = node.get("message") if isinstance(node, dict) else None
        if not isinstance(message, dict):
            continue
        author = message.get("author") or {}
        if author.get("role") != "user":
            continue
        classified = classify_user_message(message.get("content"))
        found.append(Message(conversation_id, node_id, classified.kind, classified.text))
    return found


def reply_to(mapping, node_id) -> Reply | None:
    """The nearest assistant message with text below ``node_id``, or ``None``.

    **Breadth first, and that is the whole of #388's defect.** A depth-first or
    one-hop walk answers with a floor that looks like a total; breadth first also
    settles a regenerated turn, where the tree forks and the shallowest reply is
    the one the conversation actually shows.

    ``seen`` is not a formality -- an export's ``children`` can point back up, and
    a walk with no visited set hangs rather than reporting anything.
    """
    start = mapping.get(node_id)
    if not isinstance(start, dict):
        return None
    seen = {node_id}
    frontier = list(start.get("children") or [])
    hops = 0
    while frontier:
        hops += 1
        following = []
        for child_id in frontier:
            if child_id in seen:
                continue
            seen.add(child_id)
            node = mapping.get(child_id)
            if not isinstance(node, dict):
                continue
            message = node.get("message")
            if isinstance(message, dict):
                author = message.get("author") or {}
                if author.get("role") == "assistant":
                    content = message.get("content") or {}
                    if content.get("content_type") in ("text", "multimodal_text"):
                        parts = content.get("parts")
                        if isinstance(parts, list):
                            text = "".join(p for p in parts if isinstance(p, str)).strip()
                            if text:
                                return Reply(text, hops)
            following.extend(node.get("children") or [])
        frontier = following
    return None


def population_of(conversations) -> Population:
    """Counted off the mapping walk, independent of every matcher below it."""
    by_role = Counter()
    messages = 0
    for conversation in conversations:
        for node in conversation.get("mapping", {}).values():
            message = node.get("message") if isinstance(node, dict) else None
            if not isinstance(message, dict):
                continue
            messages += 1
            by_role[(message.get("author") or {}).get("role") or "unknown"] += 1
    return Population(
        conversations=len(conversations),
        messages=messages,
        user_messages=by_role["user"],
        by_role=dict(by_role),
    )


def stamped(conversation):
    """The conversation's own ``create_time`` as a datetime, or ``None``.

    **There is deliberately no fallback.** #388 trap 5: the fallback a previous
    pass reached for was decoding the conversation UUID, which is wrong for about
    one in five and wildly so. An undated conversation is reported as undated.
    """
    stamp = conversation.get("create_time")
    if not isinstance(stamp, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(stamp, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def partition(conversations) -> Scan:
    """File every user message into exactly one class, against the population."""
    by_kind = Counter({kind: 0 for kind in KINDS})
    prose_chars = 0
    dated, undated = [], 0
    for conversation in conversations:
        when = stamped(conversation)
        if when is None:
            undated += 1
        else:
            dated.append(when)
        for message in user_messages(conversation):
            by_kind[message.kind] += 1
            if message.kind in PROSE_KINDS:
                prose_chars += len(message.text)
    return Scan(population_of(conversations), dict(by_kind), dated, undated, prose_chars)


def _matcher(pattern):
    return re.compile(pattern, re.IGNORECASE | re.DOTALL)


def select(conversations, pattern) -> Selection:
    """His prose messages matching ``pattern``, counted two ways.

    **Both figures or neither.** A message count reads one document pasted twenty
    times as twenty attestations; a conversation count is what ``voice.md`` §4's
    two-sample rule is about.
    """
    matches = _matcher(pattern)
    records, seen = [], set()
    for conversation in conversations:
        for message in user_messages(conversation):
            if message.kind in PROSE_KINDS and matches.search(message.text):
                records.append(message)
                seen.add(message.conversation_id)
    return Selection(len(records), len(seen), records)


def pairs(conversations, pattern) -> Pairs:
    """Matched messages joined to the nearest assistant text below them."""
    matches = _matcher(pattern)
    records, missing, hops = [], 0, Counter()
    for conversation in conversations:
        mapping = conversation.get("mapping", {})
        for message in user_messages(conversation):
            if message.kind not in PROSE_KINDS or not matches.search(message.text):
                continue
            answer = reply_to(mapping, message.node_id)
            if answer is None:
                missing += 1
                continue
            hops[answer.hops] += 1
            records.append((message, answer))
    return Pairs(records, missing, dict(hops))


def refuse_target(path: Path, scratch: Path | None = None):
    """Why this path may not be written, or ``None``.

    A mined record is the clinician's own writing and the export carries patient
    material. ``scratch/`` is gitignored and ``phi_scan``'s path layer refuses a
    commit from it even under ``git add -f``; anywhere else inside a checkout it
    is one ``git add -A`` from being tracked with no net under it.
    ``name_index.refuse_target``'s rule at a second artifact.
    """
    permitted = (scratch_root() if scratch is None else scratch).resolve()
    target = path.resolve()
    checkout = enclosing_checkout(target, permitted=[permitted])
    if checkout is None:
        return None
    return (
        f"refusing to write {target}: it is inside the checkout at {checkout} "
        "and not under scratch/. Mined records are the clinician's own writing."
    )


def _span(dated):
    if not dated:
        return "no dated conversation"
    return f"{min(dated).date()} -> {max(dated).date()}"


def format_report(scan: Scan, selection=None, joined=None, show=False) -> list:
    """Counts only. Corpus text appears under ``show`` and nowhere else."""
    population = scan.population
    lines = [
        "== voice-corpus coverage",
        f"  {population.conversations} conversation(s), {population.messages} message(s), "
        f"{_span(scan.dated)}",
        f"  {population.user_messages} user message(s), the denominator every row below divides by",
    ]
    for kind in KINDS:
        count = scan.by_kind.get(kind, 0)
        note = "  <- prose" if kind in PROSE_KINDS else ""
        if kind == "unclassified" and count:
            note = "  <- a shape this module does not recognize"
        lines.append(f"    {kind:<20} {count}{note}")
    lines.append(f"  {scan.prose_chars} character(s) of prose")
    if scan.undated:
        lines.append(
            f"  {scan.undated} undated conversation(s) -- no create_time, and there is no "
            "second way to date one"
        )
    if selection is not None:
        lines.append("")
        lines.append(
            f"== matched {selection.messages} message(s) in "
            f"{selection.conversations} conversation(s)"
        )
        lines.append(
            "  a conversation is the unit; a message count reads one pasted document "
            "as many attestations"
        )
        if show:
            for message in selection.records:
                lines.append(f"    [{message.conversation_id}] {message.text}")
    if joined is not None:
        lines.append("")
        lines.append(f"== {len(joined.records)} pair(s), {joined.missing_reply} still missing a reply")
        spread = ", ".join(f"{hop}:{n}" for hop, n in sorted(joined.hops.items()))
        lines.append(f"  hops from the user node to the reply -- {spread or 'none'}")
        lines.append(
            "  whether a reply is a rewrite of the same content is a reading, and the "
            "join is a floor"
        )
        if show:
            for message, answer in joined.records:
                lines.append(f"    [{message.conversation_id}] HIS: {message.text}")
                lines.append(f"    [{message.conversation_id}] REPLY: {answer.text}")
    lines.append("")
    lines.append("== what a clean run does not establish")
    lines.extend(f"  - {limb}" for limb in NOT_REACHED)
    return lines


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Read a ChatGPT conversation export into the pieces a voice model is "
            "built from. Counts only; --show output is PHI."
        )
    )
    parser.add_argument("export", nargs="?", help="the export's conversations.json")
    parser.add_argument("--match", help="a regex over his prose messages")
    parser.add_argument("--pairs", action="store_true", help="join matches to their reply")
    parser.add_argument("--show", action="store_true", help="print the text. This is PHI.")
    parser.add_argument("--out", help="write the selection under scratch/")
    parsed = parser.parse_args(argv)

    if not parsed.export:
        print("no export named", file=sys.stderr)
        return NOT_READ
    conversations, why = load_export(Path(parsed.export))
    if conversations is None:
        print(why, file=sys.stderr)
        return NOT_READ
    if not conversations:
        print("no conversation in the export", file=sys.stderr)
        return NOT_READ

    scan = partition(conversations)
    if not scan.population.user_messages:
        print("no user message in any conversation read", file=sys.stderr)
        return NOT_READ

    selection = select(conversations, parsed.match) if parsed.match else None
    joined = pairs(conversations, parsed.match) if parsed.pairs and parsed.match else None

    # **A refused write is not a refused read**, which is `name_index`'s ordering:
    # the run read the whole export and knows what it found, so the refusal is a
    # note on stderr beside the report rather than instead of it.
    refused = None
    if parsed.out:
        target = Path(parsed.out)
        refused = refuse_target(target)
        if refused is None:
            target.write_text(
                "\n".join(format_report(scan, selection, joined, show=True)), encoding="utf-8"
            )

    print("\n".join(format_report(scan, selection, joined, show=parsed.show)))
    sys.stdout.flush()
    if refused is not None:
        print(f"\n{refused}", file=sys.stderr)
    # 1 wins over the undated banner, which prints in the report above so the
    # finding reads as a floor rather than as the whole.
    return FOUND if scan.by_kind.get("unclassified") or scan.undated else CLEAN


if __name__ == "__main__":
    use_utf8()
    raise SystemExit(main(sys.argv[1:]))
