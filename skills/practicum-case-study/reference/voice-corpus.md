# Voice corpus — the vendor-neutral export method

This sheet is the contract for turning an assistant export into the corpus a voice model reads.
It describes the method rather than one vendor's file layout.
[`tools/voice_corpus.py`](../../../tools/voice_corpus.py) is the ChatGPT reference implementation;
this repository ships no second reader. A Claude, Grok, Gemini, Copilot, or other export needs a
converter into the normalized shape below. That converter belongs to the clinician using that
vendor, because this repository has no real export of those shapes against which to verify one.

## The normalized shape

The handoff is a top-level JSON list of conversations. Each conversation carries:

- `conversation_id` or `id`, which identifies a distinct conversation;
- its own numeric `create_time` timestamp, or an explicitly missing timestamp that will be reported
  as undated; and
- a `mapping` object whose keys are node ids and whose values are nodes.

Each node carries a `children` list and either no message or one `message`. A message carries
`author.role` and a `content` object. The content carries a `content_type` and `parts`; text parts
remain strings, and non-text parts remain typed objects. Preserve every node and every message.
Do not flatten branches, discard system or tool nodes, silently turn an unknown source type into a
known one, derive a date from an id, or join a user's turn to a later question's answer.

That is the shape `voice_corpus.py` already accepts. It is an interface, not permission to claim a
converter is complete merely because its output parses.

## The reading method

The converter and the reader both follow these rules:

1. Count the population off the export's structure walk, independently of every content matcher.
2. File every user message into exactly one class. The classes sum to that population, and the
   unread remainder is printed on every run.
3. An unrecognized type is a named class and a finding, never a silent drop.
4. Date a conversation from the export's own timestamp. Never derive a date from an id.
5. The unit is a distinct conversation, not a message. Print conversation and message counts
   together; one document pasted repeatedly is still one conversation's evidence.
6. A request-and-reply pair is a mechanical floor: take the nearest reply below the request without
   crossing a later user turn, and print the hop distribution. Whether it is a rewrite of the same
   claim remains a reading.
7. Only typed text is the clinician's writing for this method. Dictation, attachments, custom
   instructions, and other standing context are separate classes.
8. Counts only by default. Any output carrying corpus text is PHI and stays under `scratch/`.
9. Refuse rather than degrade. The converter exits non-zero and says what was not read when its
   source is unrecognized or when the normalized output fails its declared-shape validation.

## The report is the verification surface

Nobody maintaining this repository will see another clinician's export. The **converter's own
counts-only report** is therefore the evidence that it walked what it claims. It prints:

- the population by role;
- every user-message class and the unread remainder, with the classes summing to the user total;
- conversation and message totals together;
- the dated span and the undated count;
- the selected-message and distinct-conversation totals when a matcher is used; and
- for paired records, the missing-reply count and hop distribution.

A report missing one of those rows is not sufficient evidence for a converter. A clean report
establishes only that the declared walk accounted for its input; it does not establish that pasted
prose is the clinician's unwatched writing, that a reply is a rewrite, or that the resulting
features identify the clinician. Those remain readings under [voice.md](voice.md).

**This ticket changes no runtime behavior in `voice_corpus.py`.** The module remains the ChatGPT
reference implementation for the normalized shape and calculations; the contract above tells a
new converter what it must validate and print from its own source walk. Do not read this sheet as a
claim that the existing CLI gained a deeper shape gate or a new console layout.
