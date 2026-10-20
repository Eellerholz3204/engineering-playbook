"""Check interface state and persistence without requiring a desktop client."""

from pathlib import Path
import json
import os
import tempfile
import unittest
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

from repository_builder.app import RepositoryBuilder
from repository_builder.core import CreationPlan, create_repository
from repository_builder.patch_ui import PatchView
from repository_builder.patch_downloads import PublishedPatch


class BuilderUITests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.page = MagicMock()
        self.page.services = []
        self.app = RepositoryBuilder(self.page)
        self.temporary = tempfile.TemporaryDirectory(prefix="playbook-ui-test-")
        self.addCleanup(self.temporary.cleanup)
        environment = patch.dict(os.environ, {"ENGINEERING_PLAYBOOK_SCRATCH_ROOT": str(Path(self.temporary.name) / "scratch")})
        environment.start()
        self.addCleanup(environment.stop)
        cache = patch("repository_builder.patch_ui.cached_patches", return_value=[])
        cache.start()
        self.addCleanup(cache.stop)
        self.app.name.value = "example-project"
        self.app.parent.value = self.temporary.name

    async def test_save_and_import_configuration(self):
        self.app.choose_profile("dbt-python")
        self.app.toggle_capability("ai-governance", True)
        self.app.toggle_capability("metis-governance", True)
        self.app.git.value = False
        self.app.reviewed_plan = self.app.plan()
        config = Path(self.temporary.name) / "project.json"
        self.app.picker = MagicMock()
        self.app.picker.save_file = AsyncMock(return_value=str(config))
        await self.app.save_configuration(None)
        self.assertTrue(config.exists())
        plan = CreationPlan.from_json(config.read_text(encoding="utf-8"), self.app.catalog)
        self.assertEqual(self.app.reviewed_plan, plan)
        self.app.choose_profile("generic")
        self.app.picker.pick_files = AsyncMock(return_value=[MagicMock(path=str(config))])
        await self.app.import_configuration(None)
        self.assertEqual("dbt-python", self.app.selected_profile)
        self.assertEqual({"ai-governance", "metis-governance"}, self.app.selected_capabilities)
        self.assertEqual(plan, self.app.plan())
        cards = self.app.review_view()
        self.assertTrue(any(getattr(card, "content", None) and
            getattr(card.content, "controls", None) and
            getattr(card.content.controls[0], "value", None) == "Agent scratch space" for card in cards))
        output = []
        self.assertEqual(0, create_repository(self.app.plan(), output.append), "\n".join(output))
        self.assertTrue(any(line.startswith("Agent scratch space (outside repository): ") for line in output))

    async def test_invalid_name_stays_on_project_screen(self):
        self.app.name.value = "../outside"
        await self.app.advance(None)
        self.assertEqual(0, self.app.step)
        self.assertTrue(self.app.error.visible)

    async def test_patch_dropdown_discovery_refresh_and_search(self):
        root = Path(self.temporary.name)
        repo = root / "project-é"
        (repo / "engineering-playbook").mkdir(parents=True)
        (repo / "engineering-playbook/playbook.json").write_text("{}")
        (root / "not-installed").mkdir()
        downloads = root / "Downloads"
        downloads.mkdir()
        bundle = downloads / "release.zip"
        with zipfile.ZipFile(bundle, "w") as archive:
            archive.writestr("patch.json", json.dumps({"schema_version": 1,
                "patch_id": "scratch-rules", "base_version": "3.2.1", "target_version": "3.3.0"}))
        (downloads / "broken.zip").write_bytes(b"not a zip")
        with zipfile.ZipFile(downloads / "ordinary.zip", "w") as archive:
            archive.writestr("readme.txt", "not a patch")
        with patch.object(PatchView, "discovery_locations", return_value=({root}, {downloads, root / "missing"})):
            self.app.open_patch_view(None)
            view = self.app.patch_view
            self.assertEqual([str(repo)], [o.key for o in view.repository.options])
            self.assertEqual([str(bundle)], [o.key for o in view.bundle.options])
            self.assertIn("3.2.1 to 3.3.0", view.bundle.options[0].text)
            self.assertNotIn("release.zip", view.bundle.options[0].text)
            self.assertIsNone(view.repository.value)  # Never pick a target silently.
            view.repository.value = str(repo)
            view.bundle.value = str(bundle)
            view.report = {"reviewed": True}
            view.reviewed_inputs = view.values()
            view.refresh()
            self.assertIsNone(view.report)
            self.assertEqual(str(repo), view.repository.value)
            self.assertEqual(str(bundle), view.bundle.value)
            self.assertFalse(hasattr(view, "checksum"))
            self.assertFalse(hasattr(view, "remote"))
            view.repository.text = "typing another project"
            inputs = self.app.body.controls[1]
            view.search_changed(MagicMock(control=view.repository))
            self.assertIsNone(view.repository.value)
            self.assertIs(inputs, self.app.body.controls[1])
            view.busy(True)
            self.assertTrue(view.refresh_button.disabled)
            self.assertTrue(view.bundle.disabled)
            view.busy(False)

    async def test_patch_browse_adds_choices_and_cancel_preserves_them(self):
        root = Path(self.temporary.name)
        repo, bundle = root / "outside-project", root / "outside.zip"
        self.app.picker = MagicMock()
        self.app.picker.get_directory_path = AsyncMock(return_value=str(repo))
        self.app.picker.pick_files = AsyncMock(return_value=[MagicMock(path=str(bundle))])
        with patch.object(PatchView, "discovery_locations", return_value=(set(), set())):
            self.app.open_patch_view(None)
            view = self.app.patch_view
            self.assertIn("No installed repositories", view.repository_path.value)
            self.assertIn("No patches found", view.bundle_path.value)
            await view.choose_repository(None)
            await view.choose_bundle(None)
            self.assertEqual([str(repo)], [o.key for o in view.repository.options])
            self.assertEqual([str(bundle)], [o.key for o in view.bundle.options])
            self.assertEqual(str(bundle), view.bundle_path.value)
            self.app.picker.get_directory_path.return_value = None
            self.app.picker.pick_files.return_value = []
            await view.choose_repository(None)
            await view.choose_bundle(None)
            self.assertEqual((str(repo), str(bundle)), view.values())
            view.close(None)
            self.app.open_patch_view(None)
            self.assertEqual([str(bundle)], [o.key for o in self.app.patch_view.bundle.options])
        parents, patches = self.app.patch_view.discovery_locations()
        self.assertIn(root, parents)
        self.assertIn(root, patches)
        self.assertIn(Path.home() / "Downloads", patches)

    async def test_online_patch_preview_downloads_and_errors_preserve_apply_gate(self):
        item = PublishedPatch("playbook-patch-test", "test.zip", "Playbook patch: agent scratch workspaces (3.2.1 to 3.3.0)",
            notes="# Scratch workspaces\n\nPatch ID: `test`\n\nKeep temporary agent work outside projects.\n\n## Downloads\n\nRelease instructions.")
        with patch("repository_builder.patch_ui.available_patches", return_value=[item]) as check:
            self.app.open_patch_view(None)
            view = self.app.patch_view
            check.assert_not_called()  # Opening the screen is offline.
            await view.check_online(None)
        self.assertEqual([item.key], [o.key for o in view.bundle.options])
        self.assertEqual(item.key, view.bundle.value)
        self.assertEqual("agent scratch workspaces (3.2.1 to 3.3.0)", view.bundle.options[0].text)
        self.assertEqual("Keep temporary agent work outside projects.", view.description.value)
        self.assertTrue(view.notes.visible)
        self.assertEqual(item.notes, view.notes_text.value)
        repo = Path(self.temporary.name) / "consumer"
        view.repository.value = str(repo)
        view.report = {"previous": "review"}
        view.changed()
        self.assertIsNone(view.report)
        path = Path(self.temporary.name) / "downloaded.zip"
        report = dict(can_apply=True, already_applied=False, patch_id="test", summary="Verified summary",
            base_version="3.2.1", target_version="3.3.0", sha256="a" * 64,
            changes=[], conflicts=[], configuration_update=False, review_required=[])
        with patch("repository_builder.patch_ui.download_patch", return_value=(path, "a" * 64)) as download, \
             patch("repository_builder.patch_ui.inspect_patch", return_value=report) as inspect, \
             patch("repository_builder.patch_ui.apply_patch") as apply:
            await view.preview(None)
            download.assert_called_once_with(item, repo)
            inspect.assert_called_once_with(path, repo, "a" * 64)
            apply.assert_not_called()
            self.assertEqual(item.key, view.bundle.value)
            self.assertEqual([item.key], [o.key for o in view.bundle.options])
            self.assertEqual("Apply patch", self.app.next.content)
            self.assertFalse(view.completed)
            # Re-preview a verified download offline, still verifying its pinned hash.
            await view.preview(None)
            self.assertEqual(1, download.call_count)
            self.assertEqual(2, inspect.call_count)
            view.repository.value = str(repo / "different")
            await view.apply(None)
            apply.assert_not_called()
            self.assertIsNone(view.report)
        view.downloaded.clear()
        with patch("repository_builder.patch_ui.download_patch", side_effect=ValueError("checksum mismatch")):
            await view.preview(None)
        self.assertIn("checksum mismatch", self.app.error.value)
        self.assertFalse(self.app.busy)
        self.assertIsNone(view.report)
        self.assertFalse(view.completed)
        with patch("repository_builder.patch_ui.available_patches", side_effect=ValueError("offline")):
            await view.check_online(None)
        self.assertEqual(item.key, view.bundle.value)
        self.assertTrue(self.app.error.visible)
        self.assertFalse(self.app.busy)
        self.assertIn(item.key, [o.key for o in view.bundle.options])
        with patch("repository_builder.patch_ui.available_patches", return_value=[]):
            await view.check_online(None)
        self.assertIn("No published", view.online_status.value)
        self.assertNotIn(item.key, [o.key for o in view.bundle.options])

    async def test_cached_patch_merges_with_release_and_keeps_offline_summary(self):
        root = Path(self.temporary.name)
        bundle = root / "cached.zip"
        with zipfile.ZipFile(bundle, "w") as archive:
            archive.writestr("patch.json", json.dumps({"schema_version": 1, "patch_id": "scratch-rules",
                "summary": "Keep agent artifacts out of the project.", "base_version": "3.2.1", "target_version": "3.3.0"}))
        item = PublishedPatch("playbook-patch-test", bundle.name, "Scratch workspaces", "a" * 64)
        with patch("repository_builder.patch_ui.cached_patches", return_value=[bundle]), \
             patch("repository_builder.patch_ui.cached_checksum", return_value="a" * 64), \
             patch("repository_builder.patch_ui.available_patches", return_value=[item]):
            self.app.open_patch_view(None)
            view = self.app.patch_view
            view.bundle.value = str(bundle)
            view.changed()
            self.assertEqual("Keep agent artifacts out of the project.", view.description.value)
            self.assertFalse(view.notes.visible)
            await view.check_online(None)
            self.assertEqual(str(bundle), view.bundle.value)  # Never switch an explicit choice.
            view.bundle.value = item.key
            view.refresh()
            self.assertEqual([item.key], [o.key for o in view.bundle.options])
            self.assertIn("Available offline", view.bundle_path.value)
            replacement = PublishedPatch(item.tag, item.name, item.title, "b" * 64)
            with patch("repository_builder.patch_ui.available_patches", return_value=[replacement]):
                await view.check_online(None)
            self.assertNotIn(item.key, view.downloaded)  # A changed release cannot reuse old bytes.
            await view.check_online(None)
            with patch("repository_builder.patch_ui.available_patches", return_value=[]):
                await view.check_online(None)
            self.assertEqual(str(bundle), view.bundle.value)
            self.assertEqual("Keep agent artifacts out of the project.", view.description.value)

    async def test_conflicting_preview_is_explicitly_blocked_until_inputs_change(self):
        self.app.open_patch_view(None)
        view = self.app.patch_view
        view.repository.value = str(Path(self.temporary.name) / "consumer")
        view.bundle.value = str(Path(self.temporary.name) / "patch.zip")
        report = dict(can_apply=False, already_applied=False, patch_id="test", summary="Test update",
            base_version="3.3.0", target_version="3.3.0", sha256="a" * 64,
            changes=[], conflicts=["GOVERNANCE_CONTEXT.md"], configuration_update=False, review_required=[])
        with patch("repository_builder.patch_ui.local_checksum", return_value=None), \
             patch("repository_builder.patch_ui.inspect_patch", return_value=report), \
             patch("repository_builder.patch_ui.apply_patch") as apply:
            await view.preview(None)
            self.assertEqual("Patch blocked", self.app.next.content)
            self.assertTrue(self.app.next.disabled)
            self.assertFalse(view.bundle.disabled)
            self.assertIn(view.blocked_notice, self.app.body.controls)
            self.assertIn("1 framework file(s)", view.blocked_reason.value)
            self.assertIn("Patch blocked", view.online_status.value)
            view.busy(True)
            view.busy(False)
            self.assertTrue(self.app.next.disabled)
            apply.assert_not_called()
            view.refresh()
            self.assertEqual("Preview patch", self.app.next.content)
            self.assertFalse(self.app.next.disabled)
            self.assertNotIn(view.blocked_notice, self.app.body.controls)

    async def test_catalog_disables_unsupported_virtual_environment(self):
        await self.app.advance(None)
        self.assertEqual(1, self.app.step)
        self.app.choose_profile("python")
        self.app.venv.value = True
        self.app.choose_profile("node")
        self.assertFalse(self.app.venv.value)
        self.assertTrue(self.app.venv.disabled)
        await self.app.advance(None)
        self.assertEqual(2, self.app.step)
        self.assertEqual("node", self.app.reviewed_plan.project_type)

    async def test_copy_command_calls_clipboard_with_reviewed_values(self):
        self.app.reviewed_plan = self.app.plan()
        self.app.clipboard = MagicMock()
        self.app.clipboard.set = AsyncMock()
        await self.app.copy_command(None)
        command = self.app.clipboard.set.call_args.args[0]
        self.assertIn("ProjectName = 'example-project'", command)
        self.assertIn("@repositoryOptions", command)
