"""ADR 0422 writer-shape floor across every top-level non-test tools module.

Recognizes direct write_text/write_bytes, literal writing open modes, os.replace,
and one-argument replace/rename calls. Aliases, indirect streams, ZipFile, copy
helpers, dynamic modes and nested packages are outside this floor. This is a
source route ratchet, not a claim that all filesystem writes are recognized.
"""
import ast
from pathlib import Path
import unittest


TOOLS = Path(__file__).resolve().parent

# Owning operation, not filename, decides whether a write is mutable run bookkeeping.
# New direct-write shapes fail until their ownership and transaction route are read.
EXCLUDED_MODULES = {
    'adr_next': 'Maintainer ADR number reservations, outside clinical runs.',
    'adr_supersession_population': 'Maintainer ADR audit reports.',
    'anchor_scan': 'Answer-free agreement brief is a reader input, not later tool-read bookkeeping.',
    'artifact_lock': 'Lock implementation and owner handoff, not a clinical record.',
    'assignment_docx': 'Outbound Word artifact producer.',
    'clinical_credentials': 'Account profile answers, outside run-directory records.',
    'coding_freshness': 'Producer receipt has no committed readback; old receipt is invalidated before a fresh run.',
    'cpt_descriptor_agreement': 'Maintainer licensed code-set import agreement, not a clinical run.',
    'cpt_mdm_sheet': 'Maintainer licensed reference-sheet comparison output.',
    'day_file_text': 'Source-text artifact for the clinical reader.',
    'discussion_post_render': 'New unpublished render-pass artifacts, not existing pass rewrites.',
    'docx_write': 'Outbound Word artifact producer.',
    'entry_copy': 'Outbound portal note copy.',
    'file_digest': 'Render fingerprints are written only into unpublished pass staging.',
    'guidelines_build': 'Maintainer guideline corpus and reference artifacts.',
    'guidelines_currency': 'Maintainer publisher observations and corpus records.',
    'guidelines_extract': 'Maintainer guideline text corpus.',
    'guidelines_index': 'Maintainer guideline corpus index.',
    'guidelines_manifest': 'Maintainer corpus producer provenance.',
    'guidelines_recs': 'Maintainer reference recommendation artifacts.',
    'install_compaction_reminder': 'User-level engineering configuration.',
    'install_grilling_guard': 'User-level guard configuration.',
    'install_run_status_guard': 'User-level guard configuration.',
    'memory_index': 'Account memory index, outside clinical run-directory records.',
    'name_index': 'Account name index, outside run-directory records.',
    'page_image': 'Rendered image artifact.',
    'post_html': 'Outbound submission artifact.',
    'post_text': 'Outbound submission artifact.',
    'render_pass': 'Immutable pass directory publication; no existing pass is rewritten.',
    'skills_mirror': 'Maintainer mirror audit report.',
    'suite': 'Engineering test scheduling weights.',
    'title_page_credentials': 'Account profile answer, outside run-directory records.',
    'tracker_event_checks': 'Engineering tracker audit summary.',
    'tracker_population': 'Engineering tracker harvest evidence.',
    'tracker_publish_marker': 'Engineering tracker publication marker.',
    'tracker_scan': 'Engineering tracker harvest and verdict evidence.',
    'uptodate_store': 'Account source corpus and its index, outside run-directory records.',
    'uspstf_table': 'Maintainer reference table producer.',
    'voice_corpus': 'Maintainer corpus report output.',
}

# These raw writes are siblings under an owning operation, or separately governed
# legacy transactions. Their actual mutable record writes use the shared seam.
GUARDED_SIBLINGS = {
    ('bar_signatures', '_replace'): 'Signed bar and rollback under canonical history transaction.',
    ('bar_signatures', '_sign'): 'Exclusive new retained copy under canonical history transaction.',
    ('case_video', 'transcribe'): 'Transcript artifact under parent-owned capture-directory lock.',
    ('case_video', 'main'): 'Private worker log under parent-owned capture-directory lock.',
    ('encounter_openers', 'atomic_write'): 'Encounter artifacts or account identity-map replacement under existing owner lock.',
    ('refutation_apply', '_snapshot_ledger'): 'Exclusive immutable prior ledger snapshot under ledger transaction.',
    ('refutation_apply', '_apply'): 'Exclusive immutable saved return under ledger transaction.',
    ('aar_scan', '_retire_orphan_pointers'): 'Immutable legacy evidence relocation under allocation/source locks.',
    ('aar_scan', '_rebuilt_update'): 'Exclusive immutable refused extract archive under allocation/extract transaction.',
    ('artifact_repairs', '_write_ledger'): 'Separately governed repair-ledger transaction, ADR 0405.',
    ('artifact_repairs', 'begin'): 'Immutable repair original artifact under ADR 0405.',
    ('artifact_repairs', 'record_repair'): 'Immutable repair comparison artifact under ADR 0405.',
    ('frozen_grade', '_write'): 'Existing locked freeze/adoption transaction, ADR 0422 ruling 5.',
    ('run_record_reader', 'update_tool_record'): 'Shared lock-owned read/change/atomic replace or append.',
}


def write_sites(source):
    found = set()
    def scan(node, owner='module'):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            owner = node.name
        if isinstance(node, ast.Call):
            function = node.func
            name = function.attr if isinstance(function, ast.Attribute) else function.id if isinstance(function, ast.Name) else ''
            values = [arg.value for arg in [*node.args, *[kw.value for kw in node.keywords if kw.arg == 'mode']]
                      if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
            writing_open = name == 'open' and any(value and value[0] in 'wax' and set(value) <= set('rwaxbt+') for value in values)
            os_replace = (name == 'replace' and isinstance(function, ast.Attribute)
                          and isinstance(function.value, ast.Name) and function.value.id == 'os')
            path_move = name in {'replace', 'rename'} and len(node.args) == 1 and not node.keywords
            if name in {'write_text', 'write_bytes'} or writing_open or os_replace or path_move:
                found.add(owner)
        for child in ast.iter_child_nodes(node):
            scan(child, owner)
    scan(ast.parse(source))
    return found


class WriterRouteFloor(unittest.TestCase):
    def test_every_recognized_direct_writer_has_an_owned_route(self):
        unclassified = []
        for path in TOOLS.glob('*.py'):
            if path.name.startswith('test') or path.name.endswith('_test_support.py') or path.stem == 'grader_conformance':
                continue
            for function in write_sites(path.read_text(encoding='utf-8-sig')):
                if path.stem not in EXCLUDED_MODULES and (path.stem, function) not in GUARDED_SIBLINGS:
                    unclassified.append((path.stem, function))
        self.assertEqual(unclassified, [], 'Read new writer ownership and route mutable records through update_tool_record.')

    def test_the_floor_discriminates_new_writers_from_ordinary_readers(self):
        self.assertEqual(write_sites("def bad(p):\n p.write_text('changed')\n"), {'bad'})
        self.assertEqual(write_sites("def append(p):\n p.open('ab').write(b'x')\n"), {'append'})
        self.assertEqual(write_sites("def read(p):\n return p.read_text().replace('a','b')\n"), set())
        self.assertNotIn(('new_record_writer', 'bad'), GUARDED_SIBLINGS)
        self.assertNotIn('new_record_writer', EXCLUDED_MODULES)
