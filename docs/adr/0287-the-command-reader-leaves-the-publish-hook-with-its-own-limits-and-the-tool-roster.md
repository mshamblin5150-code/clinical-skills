# The command reader leaves the publish hook with its own limits and the tool roster

**Measured at:** 4cb3818a65326472252ef6084b91530a06fcc34a

[#1329](https://github.com/mshamblin5150-code/clinical-skills/issues/1329) was filed from an
architecture review on 2026-09-16. It found that `tools/tracker_publish_hook.py` holds two modules
with no seam between them: reading a command into what the shell will run, and deciding whether a
publication is allowed. It also found that `tools/implementation_map_post_hook.py`, which never
refuses anything, imports the publish hook only for the reading half.
[ADR 0188](0188-a-publication-in-an-unmodeled-shell-is-refused-and-the-tool-roster-is-keyed-by-shell.md)
ruling 5 recorded that import as why the two hooks shared one defect. Grilled 2026-10-03 against
`main`, where the freshness gate read `FRESH`; the clinician ruled every point below in that
session. **Nothing is built here; this is the record the build reads.**

## Measured before ruling

### The limits object

`tracker_publish_hook.NOT_REACHED` holds 27 rows. Read one at a time, 11 describe the reading half:

- a file rewritten after the scan is graded on its earlier text
- which file an author meant is not established
- assignment expansion is reconstructed and reaches only the same command
- the command-folder reader reaches literal absolute cd targets only
- a shell command assembled at run time is invisible
- a program-formatted command is invisible
- an argv list assembled in pieces is invisible
- an alias or function standing in for gh is invisible
- a newly added API endpoint is refused until classified
- a wrong non-publication entry silently passes
- a GraphQL document assembled at run time is unreadable

Two of them, the assignment-expansion row and the command-folder row, describe functions that
already live in `tools/shell_reader.py`. The hook holds them because the hook makes the coverage
claim.

`implementation_map_post_hook.DECLARED_LIMITS` restates four of those rows in its own words: run-time
assembly, a program-formatted command, an argv list assembled in pieces, and an alias or function
standing in for `gh`. They are two copies of one ceiling, held in two modules because both modules
call one classifier.

[ADR 0246](0246-the-publish-marker-records-a-hook-run-per-checkout.md) already put five marker rows
in this object while their code lives in `tools/tracker_publish_marker.py`, which
`tools/test_declared_limits.py` declares limitless because its limits "belong to
tracker_publish_hook". So this module already holds limits for code in another file.

### The precedent

[ADR 0159](0159-the-sheet-grammar-leaves-as-a-pure-module-and-gate-results-split-per-gate.md)
ruling 1 and
[ADR 0173](0173-gate-schema-stays-one-gate-because-both-of-its-halves-are-bounded-by-the-one-limits-object.md)
ruling 1 refused to move `gate_schema` out of `threshold_sheet` because limit rows would be left
describing code in another module. ADR 0173 closed the move because both ways out were already
ruled shut: splitting the object, and giving the destination `threshold_grammar` a limits object,
which ADR 0159 ruling 8 forbade.

### The callers

`implementation_map_post_hook` reads `gh_command_tokens`, `loose_command_calls`, `LooseCommand`,
`command_tokens(command, "git")`, `COMMAND_TOOLS` and `MODELED_SHELL`. It never calls `extract`, and
it watches `pr merge`, which publishes no tracker text and so is no publish route `extract` reports.
`command_tokens` is a one-line wrapper over `shell_reader.executable_calls`. `command_tool_roster`
reads `COMMAND_TOOLS`. `implementation_map` imports `authorize_issue_body`, which is policy.
`tracker_publication_correspondence` reads four rule tuples, all policy. `tracker_publish_stub`
runs the hook in a subprocess and imports neither half.

### The tables

Every line that reads `PUBLISH_ROUTES`, `API_ROUTE_PATTERNS`, `API_NON_PUBLICATION_ENDPOINTS` or
`API_NON_PUBLICATION_RECORD_ENDPOINTS` lies in the reading half, above `analyze`. The policy half
answers through `COMMENT_ROUTES` and the remedy tables.

### The tests

`tools/test_tracker_publish_hook.py` holds 286 test methods. An AST walk over each method's
`hook.<name>` attribute reads finds 121 that touch only reader names (`extract`,
`gh_command_tokens`, `loose_command_calls`, `command_tokens`, `loose_publish_calls`), 126 that
touch only policy entry points (`handle`, `main`, `analyze`, `grade_command`,
`authorize_issue_body`), none that touch both, and 39 that touch neither through those names. That
matcher misses a call made through a helper or a local alias, so the figures are a floor and not a
classification; ruling 5 owns the real split.

## Ruling 1. The reader carries its own limits object

The reading rows move from the hook's object to the reader's with their keys unchanged. A row
worded as the hook's response ("is refused rather than guessed at") is reworded as what the reader
reports it could not read, and the refusal half stays a row in the hook's object. The hook's object
keeps its policy, environment and marker rows and points at the reader's object for the rest.
`implementation_map_post_hook.DECLARED_LIMITS` drops its four restated rows and points there too.
The end-to-end read of the moved code owns the final row split, on ADR 0074 ruling 2's method; the
11 rows above are the measured starting point.

**ADR 0159 ruling 1 and ADR 0173 ruling 1 stand and do not reach this move.** Their ground was that
moving code would leave its limits behind, and that the destination was ruled to carry none. This
destination is new, nothing rules it limitless, and its limits move with it.

## Ruling 2. The reader is a new file above `shell_reader`

The `gh`-level reader goes into a new module that imports `shell_reader`. `shell_reader` is
unchanged and keeps its declared no-limits reason: a module with no completeness claim of its own,
whose callers state their own boundaries. The two rows describing `shell_reader` functions go to the
new module's object, because it is the layer that claims coverage.

## Ruling 3. The reader exposes `extract` and the post hook's token-level names

The public interface is `extract` and its `Extraction` result for the publish hook, plus
`gh_command_tokens`, `loose_command_calls` and `LooseCommand` for the post hook. `command_tokens`
retires; both callers use `shell_reader.executable_calls` directly for a program other than `gh`.
The post hook is not moved onto `extract`, because that would teach `extract` commands that publish
nothing and widen the publish hook's input.

## Ruling 4. The route tables and the tool roster belong to the reader

`PUBLISH_ROUTES`, `API_ROUTE_PATTERNS`, both non-publication endpoint lists, `COMMAND_TOOLS` and
`MODELED_SHELL` move to the reader. `COMMENT_ROUTES`, `UNREADABLE_REMEDIES`,
`UNCLASSIFIED_API_REMEDIES` and every other remedy table stay with the hook. The publish hook, the
post hook and `command_tool_roster` import the roster from the reader. The glossary already defines a
**modeled shell** through what a command reader can reproduce, and every roster value is either that
shell or unmodeled, so the roster is a statement about what the reader can read.

## Ruling 5. A test moves when it calls only the reader

After a per-test reading of all 286 methods, a test that calls only the reader's public names or its
limits object moves to the reader's own test module. A test that calls the hook's entry point or
analysis stays where it is unchanged, including one that also calls `extract`. The unmoved
entry-point tests already prove the hook consumes the reader, so no dedicated seam test is added.
Tests that check the hook's limits object for a moved row follow the row.

## Ruling 6. The layer is called the command reader

`CONTEXT.md` defines **Command reader**, a term three existing entries already used undefined. The
module is `tools/command_reader.py` and its tests are `tools/test_command_reader.py`. The
`CLAUDE.md` sentences that name `tracker_publish_hook.PUBLISH_ROUTES`, `.COMMAND_TOOLS` or the
reading rows of `.NOT_REACHED` repoint to the reader in the same build.

## Unchanged by this record

No refusal, advisory or `UNREADABLE_REMEDIES` text a publication receives changes. The Bash stub
keeps its cost guard and stays import-light, because it runs the hook as a subprocess. The new module
joins `tools/test_console_codec.py`'s population only if it gains a command line, which nothing here
asks for.

## Rejected options

**Declare the reader limitless and keep its rows in the hook, on the marker precedent.** It
contradicts ADR 0159 and ADR 0173's stated ground and would need a record overriding them, and the
post hook's four restated rows would stay restated because the post hook cannot honestly point at the
policy hook for its own limits.

**Do not split, as ADR 0173 concluded.** The never-refusing post hook would keep importing the module
that decides refusals, which is the dependency ADR 0188 ruling 5 named as how the hooks came to share
a defect.

**Fold the `gh` reader into `shell_reader`.** `shell_reader` would lose its declared no-limits
reason and take on a list about `gh` aliases, GitHub endpoints and GraphQL, and `aar_scan`, its other
caller, would import publication machinery it never uses.

**Expose `extract` alone.** It cannot serve the post hook without reporting `pr merge` and other
non-publications.

**Keep `command_tokens` public in the reader.** It adds nothing over `shell_reader.executable_calls`
and would make the post hook's `git` reading depend on the `gh` reader.

**Leave the roster in the hook, or give it its own module.** The first keeps the post hook importing
policy for two constants; the second adds a file and a no-limits declaration to separate two
constants from the code that gives them meaning.

**Leave the tests in place, or add a seam test.** The first leaves the reader's behavior and limits
checked from another module's test file. The second proves nothing the entry-point tests do not.

**Name it the gh reader.** The three glossary entries that already say command reader would have to
be reworded.

## What this does not reach

**Whether a moved row is still true.** The move carries rows; it does not re-derive them.

**A limit that describes both halves.** A row whose sentence states a reading ceiling and the hook's
response to it is split by the build's reading, and a reader of one object can still miss the other
half until both objects are read.

**The full boundary of one publication is now two objects.** That cost was accepted in ruling 1.
