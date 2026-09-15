# Descriptor-agreement negative control

This control pairs exact copies of
`fixtures/filled-anchor/notes/case-01.md` and
`fixtures/worksheet-grammar-positive-control/case-01.md` in isolated
stem-matched directories. A fresh reader received the blind agreement brief
without being told which rows were suspect and wrote `agreement-read.json`.

The read is expected to fail. It independently re-derived failures for
`M79.5` as both an entry and differential code and for `Z13.1`. It also catches
the historical differential row whose osteomyelitis discussion is paired with
`M79.675`; that descriptor cannot satisfy its own support. The procedure
descriptor the reader could not settle remains in the shared unread remainder,
and the later note/worksheet bind correctly exposes the legacy run's structural
differences.
