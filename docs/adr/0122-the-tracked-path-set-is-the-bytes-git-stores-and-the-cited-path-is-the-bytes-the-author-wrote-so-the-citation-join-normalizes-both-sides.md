# The tracked path set is the bytes git stores and the cited path is the bytes the author wrote, so the citation join normalizes both sides

Found while grilling [#858](https://github.com/mshamblin5150-code/clinical-skills/issues/858),
2026-09-03, at `origin/main` `1206efc87be039c783a2374d381cc687cf47be9f`, freshness gate `FRESH`
before reading and before publishing. **Ruled by the clinician on that date.** Nothing is built
here; this is the record the build reads.

#858 was filed as a ticket about a tracked path whose bytes are not valid UTF-8 coming back with
`U+FFFD` substituted, so that a correct citation is reported unresolved and the publication is
refused. Its subject is real and its stated mechanism is not, and the measurement that shows why is
worth more than the repair.

**This record supersedes [ADR 0121](0121-the-module-root-literal-is-the-worktree-and-is-bound-by-a-property-rather-than-a-walk-and-a-failed-tree-read-is-a-coverage-gap-while-an-unvouched-publication-is-refused.md)
ruling 3's `errors="replace"` limb and nothing else in that record.**

## Measured before ruling

Every figure below was taken by running git, not by reading it. The one belief this session started
from that a fixture would have confirmed was the belief that turned out to be false.

**The ticket's mechanism does not fire.** `git ls-tree -r --name-only` C-quotes any path that is not
pure ASCII, so the byte never reaches Python's decoder. On a tree built with `git mktree` holding
`b'raw\xe9.md'`:

```
quoting on   strict          -> '"raw\351.md"'
quoting on   replace         -> '"raw\351.md"'
-z           strict          -> UnicodeDecodeError
-z           replace         -> 'raw�.md'
-z           surrogateescape -> 'raw\udce9.md'   round trip -> b'raw\xe9.md'   lossless: True
```

Strict and `replace` return the **identical** string. ADR 0121 ruling 3's `errors="replace"` on this
call is inert as the command is written, and the decode error it exists to survive is reachable only
after quoting is turned off.

**The false refusal is reachable today on valid UTF-8, with no decode involved.** `core.quotePath` is
unset in this checkout and defaults to `true`, so a tracked `docs/café.md` is returned as
`"docs/caf\303\251.md"` — with literal double quotes and backslash-octal escapes — and a correct
citation to it does not match. The undecodable byte is the rarest member of that class, not the
class.

**There is a second, independent corruption on the citation side, and the ticket does not name it.**
GitHub writes non-ASCII blob URLs percent-encoded and nothing here percent-decodes. Driving the real
functions over a body citing one path both ways:

```
cited paths     : ['docs/caf%C3%A9.md', 'docs/café.md']
quoted (today)  : tracked=['"docs/caf\303\251.md"']  unresolved = BOTH
raw (-z)        : tracked=['docs/café.md']           unresolved = the %-encoded one
```

So `-z` alone fixes the plain-URL citation and leaves the Markdown-link citation refused.

**No single normalization of the citation gets every correct citation.** Extracting from real bodies:

| tracked path | citation form | extracted | raw | unquoted |
| --- | --- | --- | --- | --- |
| `docs/a(b).md` | any | `docs/a(b` | MISS | MISS |
| `docs/it's.md` | any | `docs/it` | MISS | MISS |
| `docs/a b.md` | encoded | `docs/a%20b.md` | MISS | OK |
| `docs/a%20b.md` | literal | `docs/a%20b.md` | OK | MISS |
| `docs/a%20b.md` | encoded | `docs/a%2520b.md` | MISS | OK |
| `docs/café.md` | literal | `docs/café.md` | OK | OK |
| `docs/café.md` | encoded | `docs/caf%C3%A9.md` | MISS | OK |

Rows 4 and 5 are the collision: a literal `%` in a tracked path resolves on the raw citation and
misses on the unquoted one, and a space resolves the other way. **Unconditional `unquote` would
introduce a false refusal on a correct citation, which is the defect this record exists to remove.**

**The change is a no-op on the live tree**, which is the safest available shape and also means no
test pointed at the repository can prove it:

```
today (--name-only, strict)              : 623
proposed (-z, surrogateescape)           : 623      identical: True
tracked paths containing '%'             : 0
tracked paths with a non-ASCII character : 0
tracked paths containing ( ) ' or a space: 0
adr_next.slugify: re.sub(r"[^a-z0-9]+", "-", folded.casefold())
```

**The population of the same read shape is wider than the ticket's decision 4, and one member is
worse than the tracker gate.** #858 named `_main_ancestry`, which reads only a returncode, and the
`gh graphql` readback, which decodes JSON; both are correctly unaffected. It named none of the seven
git reads in `tools/` that split path output on newlines. `phi_scan.scan_all` is the sharpest:

```python
for path in _git("ls-files").splitlines():
    full = REPO_ROOT / path
    if not full.is_file():
        continue          # silent
```

A quoted path does not exist on disk, so the file is **skipped without a word** and standing rule 1's
`--all` walk reports clean over a file it never opened. `spelling_scan.tracked_files` carries the
identical line; `phi_scan`'s staged walk, `spelling_scan`'s staged walk, `aar_scan:588`,
`adr_next:158` and `tracker_scan:548` are the same read shape.

**`aar_scan._tracked_files` already ships the answer**, committed on #814's branch before either
ticket was filed:

```python
["git", "ls-files", "-z"], ...
root / raw.decode("utf-8", errors="surrogateescape") for raw in completed.stdout.split(b"\0")
```

## Ruled 2026-09-03

### 1. The subject is the citation join, not the undecodable byte

#858's scope widens. Its subject is that **the tracked path set is not the bytes git stores and the
cited path is not the bytes the author wrote**; the undecodable byte is its rarest member.

Every member fails one comparison — `citation.path not in tracked` — for one reason: neither side is
normalized. Splitting the members across tickets would put two rulings on one `in` test, which is
[#220](https://github.com/mshamblin5150-code/clinical-skills/issues/220)'s two copies of one rule
with the copies in the tracker instead of in prose.

**The ticket as filed was also unbuildable in its own terms.** Its *Done when* asks for a
measurement of what the corpus can contain; that measurement returns *nothing today, and the rare
thing you asked about is not the thing that will bite you*, which answers the wrong question.

### 2. The canonical form is `str` through `-z` and `surrogateescape`

`_default_branch_paths` reads `git ls-tree -r -z --name-only origin/main`, decodes with
`errors="surrogateescape"`, and splits on `\0`. The citation side decodes with
`unquote(path, encoding="utf-8", errors="surrogateescape")`.

**Bytes were refused because they buy no correctness.** Surrogateescape is lossless and injective for
this comparison — the round trip above is byte-identical — so the bytes option costs the rewrite
#858's decision 3 already concedes, on `PurePosixPath(entry).parents` in the directories set and
`Path(path).name.partition("-")` in `_has_near_miss`, for nothing. A second mechanism that cannot
fail is a line that costs a test, which is ADR 0121 ruling 5's own argument.

**`core.quotePath=false` was refused because a filename may contain a newline.** With quoting off and
`--name-only`, `splitlines()` silently splits one tracked path into two members — a fresh instance of
this defect, introduced by the fix for it. `-z` removes that question rather than reporting it.

### 3. ADR 0121 ruling 3's `errors=` limb is superseded; its `check=` limb stands

Ruling 3 has two limbs on one call and they part company here.

**`check=False` and returning `None` rather than a `frozenset` stands, unchanged and still needed.**
An unfetched `origin/main` is the reachable failure, the row reports *not graded*, and the
publication proceeds.

**`errors="replace"` is superseded.** It is inert today, and once `-z` lands it collapses every
undecodable byte to one `U+FFFD` — manufacturing exactly the state #858 was filed over, where a
corrupted member is indistinguishable from a genuinely absent path. Ruling 3 would install the defect
this record removes.

**The two changes are coupled in one direction and that is worth stating plainly: adopting `-z` is
what first makes ruling 3's decode failure reachable at all.**

**Amending ADR 0121 in place was refused.** The interesting fact is *why* a correct-looking ruling
was wrong — the ruling was made about a mechanism that does not fire, because git quoted the byte
before Python saw it — and that is the kind of finding this repository keeps and cites rather than
overwrites. **Blocking #858 on #832 was also refused**: it schedules writing a known-wrong line and
then removing it, leaving a window where `main` carries an `errors=` this repository has already
measured as wrong for its own call.

### 4. The repository-wide read is a separate ticket

The seven other git path reads are filed on their own ticket, headlined by `phi_scan.scan_all`'s
silent skip, citing this record's measurement and `aar_scan._tracked_files` as the worked fix.

**Ruling 1's argument for widening does not transfer, and the reason is the failure direction.** The
tracker gate refuses a correct citation, loudly, at a publication boundary. `phi_scan` passes an
unscanned file, silently, at the commit boundary. They want different rulings, different exit-status
treatment and different declared prose, and one of them is standing rule 1 and is prioritized as
standing rule 1 rather than inherited from a tracker-gate ticket's tail.

**Drawing the line at *walks that refuse* was refused.** It reads as principled and is not:
`aar_scan:588` and `tracker_scan:548` are the same one-line defect, and leaving them out of a ticket
that fixed two of their siblings is how the sixteenth tool arrived in `CLAUDE.md`'s console-codec
record.

### 5. The citation side is a set of accepted forms, and the tree side is not

A citation resolves when **either** its raw form **or** its `unquote`d form is in `tracked`. One
extra membership test.

**Only one side may be widened.** The tree has one true answer from git; the citation is genuinely
ambiguous, because a `%` in a URL means one thing when the tracked path contains a literal `%` and
another when it does not. **Normalizing `tracked` the same way was refused**: a file genuinely named
`a%20b.md` would be recorded as `a b.md`, so the set stops describing the repository, and two
distinct tracked files can collide onto one member, silently dropping a path from the denominator.
Symmetry is not the property wanted.

**The cost is named rather than discovered.** A citation whose raw form happens to match some
literal-`%` tracked path while the URL points elsewhere is a false **pass**. Zero tracked paths
contain `%` today, and a false pass at this gate is the cheap direction — this whole record rests on
false refusal being the expensive one.

### 6. The extractor's truncation is declared, not fixed

The citation extractor stops at `(`, `)`, `'`, `"` and backtick, so a tracked path containing one is
reported unresolved even when the citation is correct. **The regex is untouched** and
`NOT_REACHED` gains a row saying so.

Zero members, zero producers, and `adr_next.slugify` reduces every ADR title to `[a-z0-9-]`, so the
dominant citation traffic at this gate is structurally incapable of carrying one. Against that,
widening rewrites the one regex whose exclusions every ordinary citation depends on — the `)` that
terminates `[ADR 0121](https://…/0121-….md)` is the link's paren, not the path's. That is
`differential_scan`'s first positional rule, which failed in both directions at once.

**The declared row is worth having because it names a false refusal**, so the next reader who hits it
knows the gate is wrong rather than their citation.

### 7. It is held by a mock and by real git, and the seam is a defaulted parameter

`_default_branch_paths` takes a defaulted `repo` parameter. The literal stays the default, so ADR
0121 ruling 2's four declared `cwd` sites are unchanged, and the signature is being touched by ruling
3 regardless.

**Both tests are kept, and they catch different things.** The mock pins the argv and the parse: a
regression dropping `-z` while the parse still splits on `\0` leaves a real-git test **passing**,
because a quoted line contains no `\0`, so the split returns it whole and unmatched. The real
throwaway repo catches the class of error this entire session was made of — a belief about git that
no fixture can falsify. The existing tests fabricate `completed.stdout`, and a fabricated stdout
reproduces whatever its author believed; that is how #858 came to state a mechanism that does not
fire.

**The undecodable case must be built with `git mktree`.** The Windows filesystem coerced a raw
`\xe9` filename to UTF-8 on creation, so the one case #858 was filed about is unreachable through the
working tree on this host and reachable through `mktree` in three lines. Without it, that case is the
one case untested.

### 8. The accepted-forms rule lives in one function

`_citation_forms(path) -> tuple[str, ...]` returns the raw form and its `unquote`d form,
deduplicated. All three join sites consume it — membership in `tracked`, the `tree`-kind directories
set, and `_has_near_miss`'s prefix scan — and nothing else knows the rule.

**Three `or` clauses were refused.** They are three editable copies of one rule with nothing between
them, and this repository has the recorded instance one module away, in `reference_scan` holding its
own copy of the reference-heading rule while the renderer held the real one.

**Carrying both forms on `CitedPath` was also refused.** It moves a normalization decision into an
extractor whose one job is to say what strings the prose cites, and `CitedPath` is what the report
and the near-miss diagnostic read, so a tuple-valued `path` puts the rule back at three sites wearing
a different hat.

This passes [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s test for when
a helper may be shared: depending on it is the point. The three joins **must not** be allowed to
diverge, which is exactly what `module_root()` failed in ADR 0121 ruling 6.

For `_has_near_miss` the rule runs over the union of forms. It cannot change the exit status — both
branches are already 1 — so it decides only which remedy the author is told, and an inconsistent rule
there sends someone to fix a slug that is correct.

### 9. #832 is annotated before anything is built

A comment on [#832](https://github.com/mshamblin5150-code/clinical-skills/issues/832) records that
ruling 3's `errors=` limb is superseded, that the limb to build is `check=False` and `-> None` only,
and that a conflict on `_default_branch_paths` resolves toward `-z` and `surrogateescape`.

**Order is not something either branch controls** — #832 carries `ready-for-agent` and can be picked
up at any moment. If it lands first, #858 rewrites a line that was correct as briefed. **If #858
lands first, #832's agent holds a ratified brief saying `errors="replace"` and building it verbatim
reverts the fix.** Git conflicts rather than merging silently, which is the safe direction, and this
repository's record is that the resolver keeps their own side — the side with the brief in hand.

**Relying on the conflict was refused.** It loads the merge with noticing that a ratified ADR ruling
is wrong, against a brief that says otherwise, which is the load the merge is worst at carrying —
[#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s *the merge is the unguarded
moment*. The annotation is where ruling 3's supersession becomes operative rather than recorded: an
ADR states it, and a ticket comment is what an agent reads before editing the function.

## What this record does not settle

**Whether the corpus will ever contain such a path.** It does not today, on any of the three
measured shapes. The rulings above rest on the failure direction being a refusal of a correct
citation, not on a predicted arrival.

**The seven other git path reads.** Ruling 4 files them and rules nothing about them; their failure
direction is the opposite of this record's and their remedies are theirs to argue.

**Anything about `_main_ancestry` or the `gh graphql` readback.** Both were re-derived as unaffected
rather than taken from #858's body, and neither gains an obligation here.

**Whether a normalized path may appear in a report.** No `Result` in `tracker_branch_scope` names a
path today, so the question is not live; a future diagnostic that printed one would have to answer
for a surrogate reaching stdout or a JSON hook response.
