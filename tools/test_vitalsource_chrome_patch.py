import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "vitalsource-chrome" / "scripts"
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_SCRIPTS))

from patch_codex_chrome import (
    ALREADY_PATCHED,
    DISABLE_OOPIF_METHOD,
    LEGACY_BLANK_DEFER_ATTACH_HANDLER,
    LEGACY_PATCHED_PARAM_GATE,
    LEGACY_PATCHED_NAVIGATION_START,
    LEGACY_STABLE_ATTACH_HANDLER,
    LEGACY_VITALSOURCE_NAVIGATION_PREFLIGHT,
    ORIGINAL_ATTACH_HANDLER,
    ORIGINAL_COMMAND_DISPATCH,
    ORIGINAL_DOCUMENT_MIME_GATE,
    ORIGINAL_DOMAIN_GATE,
    ORIGINAL_ENABLE_OOPIF_START,
    ORIGINAL_NAVIGATION_START,
    ORIGINAL_PARAM_GATE,
    PATCHED_ATTACH_HANDLER,
    PATCHED_COMMAND_DISPATCH,
    PATCHED_DOCUMENT_MIME_GATE,
    PATCHED_DOMAIN_GATE,
    PATCHED_NAVIGATION_START,
    PATCHED_PARAM_GATE,
    PATCH_LIFECYCLE_SEAMS,
    VITALSOURCE_NAVIGATION_PREFLIGHT,
    PatchError,
    installed_bundles,
    unique_paths,
    patch_source,
)


class PatchSourceTests(unittest.TestCase):
    def test_reference_lifecycle_names_every_patcher_seam(self) -> None:
        record_path = (
            Path(__file__).resolve().parents[1]
            / "skills/vitalsource-chrome/reference/claude-in-chrome-lifecycle.json"
        )

        record = json.loads(record_path.read_text(encoding="utf-8"))

        self.assertEqual(
            set(PATCH_LIFECYCLE_SEAMS),
            {fact["seam"] for fact in record["facts"]},
        )

    def test_reference_lifecycle_records_the_completed_live_calibration(self) -> None:
        record_path = (
            Path(__file__).resolve().parents[1]
            / "skills/vitalsource-chrome/reference/claude-in-chrome-lifecycle.json"
        )

        record = json.loads(record_path.read_text(encoding="utf-8"))
        facts = {fact["seam"]: fact for fact in record["facts"]}
        calibration = record["live_calibration"]

        self.assertNotIn("declared_limit", record)
        self.assertEqual("2026-09-15", calibration["observed_on"])
        self.assertEqual("Chrome DevTools function monitors", calibration["instrument"])
        self.assertIn("reattached", calibration["attachment_observation"])
        self.assertIn("detached while idle", calibration["attachment_observation"])
        self.assertEqual(
            ["Target.setAutoAttach", "Fetch.enable", "Page.navigate"],
            calibration["commands_not_observed"],
        )
        self.assertEqual(
            "observed-live",
            facts["oopif-auto-attachment-disabled"]["status"],
        )
        self.assertEqual(
            "observed-live",
            facts["xhtml-document-response"]["status"],
        )

    def test_keeps_vitalsource_xhtml_as_a_document_response(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertIn('e==="application/xhtml+xml"', patched)

    def test_matches_claude_stable_top_level_attachment_lifecycle(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertNotIn("enableOopifAutoAttach", PATCHED_ATTACH_HANDLER)
        self.assertIn(ORIGINAL_NAVIGATION_START, patched)
        self.assertNotIn(PATCHED_NAVIGATION_START, patched)
        self.assertIn(ORIGINAL_COMMAND_DISPATCH, patched)
        self.assertNotIn(PATCHED_COMMAND_DISPATCH, patched)

    def test_migrates_current_raw_navigation_and_dispatch_variant(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{PATCHED_ATTACH_HANDLER}next{PATCHED_NAVIGATION_START}"
            f"dispatch{PATCHED_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{PATCHED_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_ATTACH_HANDLER, patched)
        self.assertIn(ORIGINAL_NAVIGATION_START, patched)
        self.assertIn(ORIGINAL_COMMAND_DISPATCH, patched)

    def test_removes_oopif_auto_attach_from_the_tab_attachment_boundary(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_ATTACH_HANDLER, patched)
        self.assertNotIn(ORIGINAL_ATTACH_HANDLER, patched)
        self.assertIn(ORIGINAL_DOMAIN_GATE, patched)
        self.assertIn(ORIGINAL_PARAM_GATE, patched)
        self.assertNotIn(PATCHED_DOMAIN_GATE, patched)
        self.assertNotIn(PATCHED_PARAM_GATE, patched)
        self.assertIn(ORIGINAL_NAVIGATION_START, patched)
        self.assertNotIn(PATCHED_NAVIGATION_START, patched)
        self.assertIn(ORIGINAL_COMMAND_DISPATCH, patched)
        self.assertNotIn(PATCHED_COMMAND_DISPATCH, patched)

    def test_is_idempotent(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{PATCHED_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{PATCHED_DOCUMENT_MIME_GATE}"
        )

        self.assertEqual(source, patch_source(source))

    def test_migrates_the_earlier_raw_cdp_patch(self) -> None:
        source = (
            f"before{PATCHED_DOMAIN_GATE}middle{LEGACY_PATCHED_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_ATTACH_HANDLER, patched)
        self.assertIn(ORIGINAL_DOMAIN_GATE, patched)
        self.assertIn(ORIGINAL_PARAM_GATE, patched)
        self.assertNotIn(PATCHED_DOMAIN_GATE, patched)
        self.assertNotIn(LEGACY_PATCHED_PARAM_GATE, patched)

    def test_migrates_the_rejected_browser_management_navigation(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{LEGACY_STABLE_ATTACH_HANDLER}next{LEGACY_PATCHED_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertIn(ORIGINAL_NAVIGATION_START, patched)
        self.assertNotIn(LEGACY_PATCHED_NAVIGATION_START, patched)

    def test_migrates_the_blank_tab_preflight_patch(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{LEGACY_BLANK_DEFER_ATTACH_HANDLER}next"
            f"{ORIGINAL_NAVIGATION_START}{VITALSOURCE_NAVIGATION_PREFLIGHT}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}method"
            f"{DISABLE_OOPIF_METHOD}{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_ATTACH_HANDLER, patched)
        self.assertIn(ORIGINAL_NAVIGATION_START, patched)
        self.assertNotIn(VITALSOURCE_NAVIGATION_PREFLIGHT, patched)
        self.assertNotIn(DISABLE_OOPIF_METHOD, patched)

    def test_migrates_the_legacy_stable_preflight_patch(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{LEGACY_STABLE_ATTACH_HANDLER}next"
            f"{ORIGINAL_NAVIGATION_START}{LEGACY_VITALSOURCE_NAVIGATION_PREFLIGHT}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}method"
            f"{DISABLE_OOPIF_METHOD}{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        patched = patch_source(source)

        self.assertIn(PATCHED_ATTACH_HANDLER, patched)
        self.assertNotIn(LEGACY_VITALSOURCE_NAVIGATION_PREFLIGHT, patched)
        self.assertNotIn(DISABLE_OOPIF_METHOD, patched)

    def test_rejects_unknown_bundles_instead_of_guessing(self) -> None:
        with self.assertRaises(PatchError):
            patch_source("a future bundle with a different security gate")

    def test_rejects_an_unknown_document_mime_classifier(self) -> None:
        source = (
            f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            'mimefunction RX(e){return e==="text/html"||e==="text/xml"||zw(e)}'
        )

        with self.assertRaises(PatchError):
            patch_source(source)

    def test_rejects_partial_patch(self) -> None:
        source = (
            f"before{PATCHED_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
            f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
            f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
            f"method{ORIGINAL_ENABLE_OOPIF_START}after"
            f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
        )

        with self.assertRaises(PatchError):
            patch_source(source)


class OnDiskPatchTests(unittest.TestCase):
    def test_installed_bundles_include_plugin_cache_and_active_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            codex_root = root / ".codex"
            local_app_data = root / "AppData" / "Local"
            cached = (
                codex_root
                / "plugins/cache/openai-bundled/chrome/1/scripts/browser-service.mjs"
            )
            runtime = (
                local_app_data
                / "OpenAI/Codex/runtimes/cua_node/hash/bin/node_modules"
                / "@oai/browser-desktop/scripts/browser-service.mjs"
            )
            cached.parent.mkdir(parents=True)
            runtime.parent.mkdir(parents=True)
            cached.touch()
            runtime.touch()

            self.assertEqual(
                sorted([cached.resolve(), runtime.resolve()]),
                installed_bundles(codex_root, local_app_data),
            )

    def test_duplicate_bundle_paths_are_collapsed(self) -> None:
        paths = [Path("bundle.mjs"), Path("bundle.mjs"), Path("other.mjs")]

        self.assertEqual(2, len(unique_paths(paths)))

    def test_backup_is_created_once_and_original_is_preserved(self) -> None:
        from patch_codex_chrome import patch_file

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir) / "browser-service.mjs"
            original = (
                f"before{ORIGINAL_DOMAIN_GATE}middle{ORIGINAL_PARAM_GATE}"
                f"then{ORIGINAL_ATTACH_HANDLER}next{ORIGINAL_NAVIGATION_START}"
                f"dispatch{ORIGINAL_COMMAND_DISPATCH}"
                f"method{ORIGINAL_ENABLE_OOPIF_START}after"
                f"mime{ORIGINAL_DOCUMENT_MIME_GATE}"
            )
            bundle.write_text(original, encoding="utf-8")

            result = patch_file(bundle)
            second = patch_file(bundle)

            self.assertEqual("patched", result.status)
            self.assertEqual(ALREADY_PATCHED, second.status)
            self.assertEqual(original, result.backup_path.read_text(encoding="utf-8"))
            self.assertIn(
                'e==="application/xhtml+xml"',
                bundle.read_text(encoding="utf-8"),
            )


class SkillContractTests(unittest.TestCase):
    def test_every_agent_reads_one_standard_and_codex_prepares_one_ordered_route(self) -> None:
        skill = (REPO_ROOT / "skills/vitalsource-chrome/SKILL.md").read_text(
            encoding="utf-8"
        )
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        lower_skill = skill.lower()
        flat_skill = " ".join(skill.split())

        self.assertIn("`vitalsource-chrome` steps 2 through 5 bind every browser agent", skill)
        self.assertIn("attempt the read under `vitalsource-chrome` step 2", lower_skill)
        self.assertIn("repair the patcher", lower_skill)
        self.assertIn("clinician's go-ahead", skill)
        self.assertIn("Claude session", skill)
        self.assertIn("unreadable source", skill)
        self.assertIn("personal plugin's patcher", skill)
        self.assertIn("already-patched", skill)
        self.assertIn("reports `patched` or `already-patched`", skill)
        self.assertIn("claude-in-chrome-lifecycle.json", skill)
        self.assertIn("installed Claude in Chrome extension version differs", flat_skill)
        self.assertNotIn("through Codex Chrome", skill.split("---", 2)[1])
        self.assertNotIn("through Codex Chrome", agents)


if __name__ == "__main__":
    unittest.main()
