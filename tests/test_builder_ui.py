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
            self.assertIn("3.2.1 → 3.3.0", view.bundle.options[0].text)
            self.assertIsNone(view.repository.value)  # Never pick a target silently.
            view.repository.value = str(repo)
            view.bundle.value = str(bundle)
            view.report = {"reviewed": True}
            view.reviewed_inputs = view.values()
            view.refresh()
            self.assertIsNone(view.report)
            self.assertEqual(str(repo), view.repository.value)
            self.assertEqual(str(bundle), view.bundle.value)
            view.checksum.value = "old-patch-checksum"
            view.bundle_changed()
            self.assertEqual("", view.checksum.value)
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
            self.assertEqual((str(repo), str(bundle), ""), view.values())
            view.close(None)
            self.app.open_patch_view(None)
            self.assertEqual([str(bundle)], [o.key for o in self.app.patch_view.bundle.options])
        parents, patches = self.app.patch_view.discovery_locations()
        self.assertIn(root, parents)
        self.assertIn(root, patches)
        self.assertIn(Path.home() / "Downloads", patches)

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
