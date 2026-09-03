# A git path read is bytes through -z and the staged walk is the headline because a quoted path reaches no layer

Grilled [#860](https://github.com/mshamblin5150-code/clinical-skills/issues/860), 2026-09-03, at
`origin/main` `fb850699c789e54bb5126f29f36c6df824e7163e`, freshness gate `FRESH` before reading and
before publishing. **Ruled by the clinician on that date.** Nothing is built here; this is the record
the build reads.

**This record supersedes [ADR 0122](0122-the-tracked-path-set-is-the-bytes-git-stores-and-the-cited-path-is-the-bytes-the-author-wrote-so-the-citation-join-normalizes-both-sides.md)
ruling 2's decode-mode limb and nothing else in that record.** Its `-z` half stands; its text-mode
half is falsified below.

#860 was filed as a ticket about `phi_scan --all` silently skipping a tracked file git C-quotes. Its
subject is real, its headline is the wrong member of its own population, and the measurement that
shows why is worth more than the repair.

## Measured before ruling

Every figure below was taken by running git against throwaway repositories, never by reading git's
documentation or fabricating a stdout. Two beliefs this session started from turned out to be false,
and both were beliefs a fixture would have confirmed.

**The staged walk is the sharpest member, not `scan_all`.** A file staged from a PHI directory with a
non-ASCII name reaches no layer at all. Driving `phi_scan.PHI_DIRECTORIES` and the real
`phi_scan.parse_diff` over real `git diff --cached` output:

```
staged_paths()   '"scratch/caf\303\251.md"'  -> path layer: NOT REPORTED
                 'scratch/plain.md'          -> path layer: REPORTED

parse_diff keys: only 'scratch/plain.md'     -> the quoted file's added lines
                                                reach no corpus or shape rule
```

The path layer's `path.startswith("scratch/")` fails because the string opens with a quote, and
`parse_diff` drops the file outright, so its contents are never scanned either. **Standing rule 1 is
fully bypassed for that file, at the commit boundary, exit 0**, on the hook that runs on every
commit. **Both nets miss it permanently**: once committed the path is tracked, so `--all` lists it
quoted, `is_file()` is `False`, and it is skipped — and `--all`'s path layer is `NOT RUN` by design,
so CI misses it too.

`scan_all` drops **one file from one walk** in a mode that runs in CI and by hand. `scan_staged`
drops **one file from all three layers** in the mode that is the only net a new file passes through.

**The ticket's stated coverage mechanism does not exist.** Its body says the population row *"counts
it as read"*. `scanned_population` returns a **sentence**, not a count:

```
scanned   tracked files -- git ls-files; an untracked file is not scanned
          until the commit that tracks it
```

**`phi_scan._git` swallows a failed git, and that is larger than the defect the ticket was filed
over.** Real git, no mock:

```
git ls-files --bogus-flag  -> returncode 129, stdout ''
phi_scan._git(...)         -> ''
scan_all over that         -> [] -> main returns 0
```

`spelling_scan._git` sets `check=True`, `tracker_scan._run_git` raises `GitError`, and `adr_next`'s
callers read the returncode. `phi_scan` — the module that is standing rule 1 — is the only one of the
four that reports clean when the walk did not run.

**`rev-list --objects` is not the same defect as its six siblings.** It does not C-quote at all, and
`core.quotePath=false` changes nothing about it. It **truncates**:

```
tracked b'new\nline.md'   non-z -> b'... new'        the tail is absent from the stream
                          -z    -> b'path=new\nline.md'
tracked b'raw\xe9.md'     non-z -> 'raw?.md' under errors="replace"
                          -z    -> b'path=raw\xe9.md'
```

The `path=` prefix is not ambiguous: a file genuinely named `path=trap.md` emits
`b'path=path=trap.md'`, and an object id is 40 hex characters and can never open with `path=`. The
`-z` parse is therefore **smaller** than the one it replaces, not two-dimensional as #860's decision
3 supposed.

**ADR 0122 ruling 2's text-mode decode is not injective, and the case it was measured on is the case
where text mode happens to work.** Reading `ls-tree -r -z --name-only` two ways:

| tracked path | bytes | text, `encoding="utf-8", errors="surrogateescape"` |
| --- | --- | --- |
| `car\rriage.md` | round-trips | `'car\nriage.md'` — `\r` became `\n` |
| `crlf\r\nboth.md` | round-trips | `'crlf\nboth.md'` — two bytes collapsed to one |
| `raw\xe9.md` | round-trips | `'raw\udce9.md'` round-trips |

Universal-newline translation runs **before** the NUL split, so `-z` does not protect it. ADR 0122
ruling 2 calls surrogateescape *"lossless and injective for this comparison"* and cites a
byte-identical round trip — taken on `\xe9`. Two distinct tracked paths `a\rb.md` and `a\nb.md` both
arrive as `a\nb.md`: **two tracked files colliding onto one member**, which is exactly what that
record's own **ruling 5** refuses for the citation side. `aar_scan._tracked_files`, which 0122 names
as the committed answer, reads **bytes** and is correct.

**The walks quote uniformly and the diff walks need no separate ruling.** `ls-files`,
`diff --cached --name-only` and `diff --name-only` produce byte-identical quoting and accept `-z`
identically. #860's decision 2 is one repair, re-derived rather than assumed.

**`-z` does not exist for a patch, and a per-path patch does not escape quoting.**

```
diff --cached --unified=0            -> +++ "b/caf\303\251.md"
diff --cached --unified=0 -- <path>  -> +++ "b/caf\303\251.md"   even given the exact pathspec
diff --cached -z --numstat           -> b'1\t0\tcaf\xc3\xa9.md\x00...'
diff --cached -z --raw               -> NUL-separated, with modes
```

**The instrument that would hold this sheds it.** `TheOtherEndOfTheSameBoundary`'s `decodes`
predicate keys on `text=`, `universal_newlines=` and `check_output`, so a bytes-mode call is outside
it by construction. Nothing in `tools/` walks `.decode(`, and `surrogateescape` appears exactly once
in non-test code. With the widened predicate #832 item 3 briefs, the population is 62 calls and
**exactly one fails** — `tracker_branch_scope.py:150`, that item's own target.

**What `--all` skips today, on plain ASCII.** A submodule gitlink and a file deleted from the working
tree while still in the index. On this checkout: 624 tracked, 0 absent, 1 binary-skipped, 623
scanned.

## Ruled 2026-09-03

### 1. A skipped file is ruled per cause, and no cause takes an exit status

The `continue` has four causes and they are not one class. A quoted path is a real coverage hole and
**stops existing** once `-z` lands, so it needs no status. A submodule gitlink and an index-versus-
worktree deletion become a **counted row beside the population row** — `not on disk: N`. The binary
`continue` stays declared, unchanged; #860's decision 4 is answered — it is a different cause with the
same shape and it is already on the page.

**Exit 2 on any skip was refused** because it refuses an ordinary commit with an unstaged deletion or
a submodule, which is how a check gets learned around. **A bare counted line was refused as the whole
answer** because it files a real hole beside a non-event.

The deletion residue is declared in `scan_all`'s coverage rather than closed: *a tracked file absent
from the working tree is not scanned, and its committed content is not read.* **Reading index blobs
instead was priced and declined** — it costs a read per tracked file to close a hole that exists only
on a dirty local tree, where CI's clean checkout is already the second net.

### 2. The headline is `scan_staged`, and the severity changes with it

#860's body and ADR 0122 both call `scan_all` the sharpest. On the measurement above it is not. The
ticket is rewritten around the staged walk, with `scan_all` as its sibling.

**This is not a reordering.** As filed the ticket reads as a coverage gap with no members; measured,
it is a total bypass of this repository's one non-negotiable rule, reachable by `git add -f` on a
file with an accented name. *"The class has no member today"* reads very differently against *a file
is skipped* than against *the firewall is off for that file*.

Two defects sit on that one input and both are repaired. `parse_diff` is an **eighth read shape** the
ticket does not list. The path layer's `startswith` is independent of it: even given a correct path
set, that test does string-prefix work on a value the walk must first make canonical.

### 3. The canonical form is bytes through `-z`, decoded `surrogateescape` at the seam

ADR 0122 ruling 2's `-z` half stands. Its text-mode half is superseded: the read is **bytes**, and
`raw.decode("utf-8", errors="surrogateescape")` happens after the NUL split, never before it.

**Amending ADR 0122 in place was refused**, on that record's own reasoning for refusing to amend ADR
0121: the interesting fact is *why* a correct-looking ruling was wrong, and here it is the same
species one record later — a ruling made from a round trip that passed for a reason narrower than the
claim it was quoted for. That is the kind of finding this repository keeps and cites rather than
overwrites. This is the second time in two days that a ruling on this function has been made about a
mechanism nobody ran.

### 4. `phi_scan._git`'s swallowed failure is in scope and is the strongest member after the staged walk

It is the same sentence as the headline — *a search that could not have worked, answering like a
settled negative* — at the same boundary, in the same direction, and strictly larger: the quoting
defect drops one member of the population and this drops the whole population. Unlike ruling 1's
causes it has **no benign member**; a `git ls-files` that fails is never a clean tree.

The shared reader raises; `phi_scan` converts to `NOT_SCANNED` at its own boundary; the existing
*findings beat a dead corpus* ordering decides precedence unchanged.

**ADR 0122 ruling 4 drew this ticket's boundary at read *shape*; this widens it to read *outcome*.**
The alternative — a second ticket owning how a failed git is reported — was refused for ruling 4's
own reason: it reads as principled and is not.

### 5. `tracker_scan:548` takes the repair, and its defect is named correctly

Its failure is truncation and decode rather than quoting, and it is the same direction: a scan that
under-reads and reports clean, on standing rule 1's own tracker surface. Deferring it is ADR 0122
ruling 4's *sixteenth tool* again — it is the site most likely to be left out precisely because it
looks unlike its siblings.

### 6. The shared shape is `tools/git_paths.py`, and it is narrow enough to survive the postures

Two public readers — one for the path-listing subcommands, one for `rev-list --objects`' `path=`
shape — and one exception type. **Callers convert at their own boundary**, which is
[#303](https://github.com/mshamblin5150-code/clinical-skills/issues/303)'s ruling: the shared helper
owns whether the read failed, the command boundary owns what that means for its run. The sites
legitimately differ in posture, and the shared thing has to be narrow enough that those differences
survive it.

This passes [#253](https://github.com/mshamblin5150-code/clinical-skills/issues/253)'s test for when
a helper may be shared: the sites **must not** be allowed to diverge, which is `repo_root.py`'s
situation and not `keyword_of`'s. It is `console_codec`'s class — infrastructure, rather than a tool
another tool happens to need — so it carries no `DECLARED_LIMITS`, as `repo_root`, `console_codec`,
`grader_conformance` and `run_grader` carry none.

**The `path=` parse lives in the shared module** rather than staying local: a measured-once parse of
an output shape that looks undocumented is precisely what must not be re-derived by the next reader.

**Per-site repair bound by an AST test was refused.** It is the seven editable copies #860's own
*What must not come out of this* forbids, and such a test can assert only that the flag is present,
never that the decode is lossless.

### 7. `parse_diff` stops parsing paths out of the patch

The path set comes from `diff --cached -z --numstat`; the added lines come from a per-path
`diff --cached --unified=0 -- <path>` whose header is **ignored**, because the path is already known.

**The cost is named rather than discovered**: one git process per staged file instead of one for the
whole commit, bounded by what is being committed, on a hook that already runs several git commands.

**A C-unquoter was refused.** Git's quoting is reversible and it would keep one process, but it
answers the quoting question with new code where this approach removes it — which is ADR 0122 ruling
2's own stated reason for choosing `-z` over `core.quotePath=false`. **`core.quotePath=false` stays
refused** for that record's reason: it reopens the newline break.

### 8. The three tickets are one implementation unit, and the label is the insurance

[#832](https://github.com/mshamblin5150-code/clinical-skills/issues/832),
[#858](https://github.com/mshamblin5150-code/clinical-skills/issues/858) and #860 are built together,
so ADR 0122 ruling 9's annotation-against-ordering has nothing left to insure — there is no
independent order.

**`ready-for-agent` comes off #832 and #858 while the unit is open.** That label promises an
unattended agent can build the thing without guessing, and building either alone now produces exactly
the copy the unit exists to remove. #858's brief is corrected on its ticket the way #832's was, so the
correction is where an agent reads it rather than only where it is recorded.

**Blocking #858 on #860 was refused.** #858 is a live false refusal at a publication boundary,
refusing correct citations today; holding it behind an unbuilt refactor buys one rule at the price of
the working gate. **#858 dropping its `-z` limb was also refused**: its subject is the two-sided join,
and a join whose tree side is still C-quoted leaves the false refusal live until #860 ships.

### 9. #832 item 3's red observation is taken now, on the current tree

Inside the unit, `tracker_branch_scope.py:150` becomes a `git_paths` call and leaves the `decodes`
population, so its "green" would arrive by **deletion of the subject** — a check passing for the
wrong reason, which is this repository's signature failure.

The widened predicate is a one-line change and `:150` is red **today**, the only failing member of 62.
Recording that observation before anything lands makes the instrument's liveness a fact the unit's
later edits cannot invalidate, and removes a fragile three-step ordering dependency from the build.

### 10. Adoption is held by a walk whose ceiling is declared in the same breath

An AST walk asserts that no non-test module in `tools/` invokes git with a path-listing subcommand
except through `git_paths`. **It reads the argv list literally**, so a subcommand assembled at run
time or passed in as a variable is invisible to it — the honest claim is a floor on the shapes in the
tree, never *a ninth site cannot arrive quietly*. That is `test_ls_files_coverage.py`'s and
`test_write_guards.py`'s ceiling adopted rather than rediscovered.

`git_paths`' own tests take ADR 0122 ruling 7's arrangement whole — a mock for the argv and the parse,
a real throwaway repository for the class no fixture can falsify — **extended by a `git mktree` case
for `\r`**, which is the case that falsified ruling 2 and which Windows will not create through the
working tree.

### 11. A surrogate path may appear in a report, degraded, and that is declared

`phi_scan.Finding.render` prints the path, and `console_codec`'s `errors="replace"` renders a
surrogate as `?` — no crash, exit status preserved, which is that module's stated design: *the thing
being protected is the exit status and not the glyph*. `json.dumps` defaults to `ensure_ascii=True`
and escapes it safely, and none of the seven `ensure_ascii=False` sites in `tools/` sits on a
path-reading route.

The declared sentence says what a reader loses rather than that surrogates are possible: **the finding
is true, the line number is usable, and the path as printed may not be.**

**Escaping it in `render` was refused**: it rewrites a report format on behalf of zero members. ADR
0122's parked question — *whether a normalized path may appear in a report* — is answered here for the
routes #860 creates and for no others.

## What this record does not settle

**Whether the corpus will ever contain such a path.** It does not today: 0 of 624 tracked paths are
non-ASCII or contain `%`, `(`, `)`, `'` or a space. Every ruling above rests on the failure direction,
never on a predicted arrival.

**Whether `git_paths` should be reached by the modules that read git for something other than paths.**
Only path reads are ruled. `git show`, `rev-parse`, `merge-base` and the rest keep their modules' own
helpers and their own decode posture.

**Hook latency.** Ruling 7's per-file cost was reasoned from what a commit stages and was not timed. If
it proves to matter the C-unquoter is the option that was refused on shape rather than on speed.

**The `startswith` repair's own boundary.** Ruling 2 requires the path layer to test a canonical path;
it does not settle whether that test should become a path-relative comparison rather than a string
prefix, which is a question about `PHI_DIRECTORIES` rather than about how the path was read.
