# One export reader ships, and the export shape is the interface
<!-- no-numbered-rulings -->

[#388](https://github.com/mshamblin5150-code/clinical-skills/issues/388) established that a chat export is a far better voice-model corpus than supplied writing samples, and built `tools/voice_corpus.py` to read one. Grilling [#400](https://github.com/mshamblin5150-code/clinical-skills/issues/400) on 2026-08-22 asked which vendors a second clinician may be offered, when the reader understands exactly one of them.

The clinician ruled on 2026-08-22: **this repo ships the ChatGPT reader and no other.** A clinician on another assistant writes a converter into the shape `voice_corpus.py` already takes, and the module grows no reader interface. The **method** that converter must follow is published vendor-neutrally in `skills/practicum-case-study/reference/voice-corpus.md`, with `voice_corpus.py` named as the reference implementation.

The assistants are still named in the ask — ChatGPT, Claude, Grok and the rest — because the list is about the **option**, and what each name buys is stated beside it.

## What was measured

`voice_corpus.py` is keyed to the ChatGPT export at several independent points: a conversation must carry a `mapping` dict, a message must carry `author.role`, content must carry a `content_type` of `text` or `multimodal_text`, and the date is `create_time`. A Claude export satisfies none of them.

**It does not read one badly, it refuses it** — `member 0 carries no mapping`, exit 2. That is the good failure direction, and it is also the whole problem: the tool a clinician is being pointed at is silent about the other assistants they might use.

**There is no second real export in this repo, and there was none when this was ruled.** That is the fact the decision turns on.

## Considered options

**Widen the tool to read the flat-transcript formats.** Rejected on evidence rather than cost. #388's first mining pass read roughly half the available paired versions — a walk with no error, no unparsed remainder, and every record it found correct, which is *partial coverage reading as complete* and was caught only by measuring against a real export. A Claude or Grok reader written here would be tested against hand-made examples alone, which `CLAUDE.md`'s extractor-coverage rule refuses as sole evidence. Reachable if a real export of that shape ever lands.

**Grow a reader seam and let a consumer drop a module in.** Rejected. It designs an interface against exactly one implementation, and — by the row above — an interface shaped by guesswork about formats nobody here has seen. It is also strictly more work than the adopted option for the same result.

**Name only ChatGPT.** Rejected by the clinician. A clinician on another assistant would never learn the option exists, and the option is the point.

**Refuse a non-ChatGPT export outright.** Rejected. It throws away real writing from most people, and there is a bounded fallback that does not: reading a stated number of named conversations as ordinary writing samples, under §3's existing rules. `CLAUDE.md` licenses exactly that — *a deliberately partial report may keep its ordinary status only when its contract names the bound beside the result.* Ten named conversations is a denominator; "I read the export" is not.

## The shape is a contract, and a shape alone is not enough

**A converter that produces the right shape by a sloppy walk reproduces #388's defect in a new vendor.** So the published method states the reading rules rather than only the field names — the population is counted off the structure walk and never off what the matcher recognized, the classes sum to that population with the remainder printed, an unrecognized type is a named class and a finding, the date comes from the export's own stamp and is never derived from an id, the unit is a distinct conversation and both figures print, a pair is a mechanical floor with its hop distance, only typed text counts as the author's, counts only by default, and a file of the wrong shape exits non-zero rather than degrading.

**The sheet also specifies the report a reader must print**, and that is the only verification available. Nobody here will ever see a second clinician's export — it is their own writing and their own patients — so the printed population, class partition, unread remainder, conversation-and-message pair, hop distribution and undated count are the sole evidence that their reader did what this one does. A reader that quietly read half prints a remainder it cannot hide.

**The sheet is Markdown on the consumer side, not a docstring.** `CLAUDE.md` states that maintainer tooling is deliberately not cited from `AGENTS.md` and that a consumer needs the Markdown and nothing else; sending a second clinician's agent into `tools/` to read a method would break that split. `voice_corpus.py`'s docstring gains the shape as a stated contract in one block — today it is described in passing, with the `mapping` gate in the not-reached list, `author.role` in the population paragraph, `create_time` in its own section and `content_type` in the classes paragraph, and nowhere does it say *here is what a converter must produce*. `guidelines_extract.py`'s *top-level `documents` must be the list of entries*, pinned from the producing side by `TheIndexerCanReadWhatThisWrites`, is the precedent for stating a handoff where it is owned.

## The cost this accepts

**A clinician on another assistant gets a writing-sample-grade model rather than a corpus-grade one until somebody writes a converter**, and that has to be said out loud in the ask rather than discovered. It is the honest price of shipping one reader.

**The export shape becomes an interface the moment a second clinician builds against it**, which is what makes this hard to reverse and is why it is recorded here. Changing what `voice_corpus.py` accepts stops being a private refactor at that point.

**And nothing here can check a converter.** The published report is read by eye, by the clinician who ran it, on the machine that holds the export. No test in this repo will ever see one.
