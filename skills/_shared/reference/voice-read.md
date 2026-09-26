# Coursework voice read

This is the one planted-read protocol used by `course-assignment`, `discussion-post`,
`practicum-case-study`, `discussion-reply`, and `peer-critique`. Run it after the draft is final and
before asking for the go-ahead. The completion grader later enforces the records through
`voice_read.apply_completion_gate`; `voice_read.DECLARED_LIMITS` is the complete ceiling and no
skill copies one of its rows.

For submission key `<key>`, make `scratch/runs/<run-key>/voice-reads/<key-stem>/`. All files
below belong there. The key stem is the terminal `--submission` value with its file extension
removed. Discussion replies keep one directory per reply, so the terminal comma-separated run
grades both earlier reads instead of replacing the first with the second.

## 1. Capture the clinician's supplied voice before drafting

Before the first prose, read only the run input the clinician authored. Do not capture faculty,
classmate, source, or model language. Quote every image and reasoning ground he supplied, without
paraphrasing it, in `supplied-voice.json`:

```json
{
  "status": "complete",
  "items": [
    {
      "id": "input-1",
      "kind": "image",
      "quote": "<his exact words>"
    }
  ]
}
```

`kind` is `image` or `reasoning-ground`. The latter records every principle supplied in the run
input, whether or not the draft ultimately argues from it; its run-local name distinguishes the
capture from the corpus-level **Stated principle** in `CONTEXT.md`, which it does not create or
revise. Each `id` is unique within this submission. When he supplied
neither, write exactly `{"status":"none"}`. An empty complete list is not the same record. The
capture belongs to the submission-key directory before its draft begins; a later reader does not
reconstruct it from the finished prose.

## 2. The planter

Send a fresh **Planter** context the final artifact and only the canonical model's discriminating
pairs. It must not be the artifact's author or the Voice reader. The brief says to rewrite exactly
one sentence toward one pair's generic half without copying that half verbatim. It writes:

- `voice-read-planted.txt`: the full grader-owned voice surface as UTF-8 with LF line endings and
  only that sentence changed.
  Markdown uses the complete file text. A Word assignment uses its nonempty document paragraphs in
  document order, joined by line feeds. A deck uses every slide's readable face text in slide order,
  followed by every speaker note in note order, joined by line feeds; the changed sentence must be
  in the notes.
- `voice-read-planter.json`, exactly:

```json
{
  "status": "complete",
  "draft_sha256": "<SHA-256 of the final Markdown, DOCX, or PPTX bytes>",
  "planted_sha256": "<SHA-256 of voice-read-planted.txt bytes>",
  "pair_id": "<the model's pair heading without its final period>",
  "original_sentence": "<the one exact sentence from the real voice surface>",
  "planted_sentence": "<its one-sentence replacement>"
}
```

Keep this record from the Voice reader. The grader reconstructs the planted copy from the real
surface and these two sentence strings; any other byte change fails.
The planter does not change a sentence quoted for a supplied item; the supplied-item verdict must
bind to the real draft as well as the planted copy.

## 3. The Voice reader

Send a separate fresh **Voice reader** only `voice-read-planted.txt`, `supplied-voice.json`, and the
canonical model. The brief explicitly includes both model sections headed `Seen in the samples, never reproduce` and
`Seen in the corpus, never reproduce`; it does not include the real draft or
`voice-read-planter.json`. The reader answers every discriminating pair derived from the model at
grading time. It also answers every captured item as `kept whole`, `shrunk`, or `dropped`. A
surviving item quotes the exact complete draft sentence; a dropped item uses `null`. Removing
profanity for graded copy is not shrinkage. It writes `voice-read.json`, exactly:

```json
{
  "status": "complete",
  "draft_sha256": "<the real artifact SHA-256 supplied in the brief>",
  "planted_sha256": "<SHA-256 of voice-read-planted.txt bytes>",
  "model_sha256": "<SHA-256 from voice-model-identity.json>",
  "supplied_voice_sha256": "<SHA-256 of supplied-voice.json bytes>",
  "suspected_plant_quote": "<the exact planted sentence the reader flags>",
  "answers": [
    {
      "pair_id": "<model pair heading without its final period>",
      "quote": "<closest verbatim sentence from the planted copy, or null>",
      "resemblance": "generic"
    }
  ],
  "supplied_voice_answers": [
    {
      "item_id": "input-1",
      "verdict": "kept whole",
      "quote": "<the exact complete sentence in the planted copy>"
    }
  ]
}
```

`resemblance` is `generic`, `his`, or `no counterpart`. `no counterpart` requires `quote: null`;
the other two require a verbatim quote from the planted copy. A missed plant voids the read. A real
sentence placed on `generic` returns the draft to its author. After either outcome, revise when
needed and repeat both contexts on a fresh plant because the draft digest has moved.

Every captured item is answered exactly once. `kept whole` is clean. `shrunk` and `dropped` are
findings and return the draft to its author. A missing capture is a finding; an unanswered captured
item is incomplete coverage, never clean. When a finding and an unanswered item coexist, the
finding still controls the result.

## 4. No subagent tool

Do not substitute a self-read. Write both JSON records as:

```json
{"status": "not run", "reason": "no subagent tool"}
```

No planted copy is owed. The completion grader reports incomplete coverage, never clean, and the
clinician's go-ahead is that run's only voice gate. `supplied-voice.json` is still owed because its
capture happens before drafting and does not require a subagent.

## 5. Separate deck ground

For a deck, this read covers voice in slide text and speaker notes. `intent.md` separately covers
the signed audience purpose and talk style. Neither record stands in for the other, and both must
be complete before the go-ahead.
