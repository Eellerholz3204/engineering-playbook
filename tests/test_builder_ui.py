"""Check interface state and persistence without requiring a desktop client."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock

from repository_builder.app import RepositoryBuilder
from repository_builder.core import CreationPlan


class BuilderUITests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.page = MagicMock()
        self.page.services = []
        self.app = RepositoryBuilder(self.page)
        self.temporary = tempfile.TemporaryDirectory(prefix="playbook-ui-test-")
        self.addCleanup(self.temporary.cleanup)
        self.app.name.value = "example-project"
        self.app.parent.value = self.temporary.name

    async def test_save_and_import_configuration(self):
        self.app.choose_profile("dbt-python")
        self.app.toggle_capability("ai-governance", True)
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
        self.assertEqual({"ai-governance"}, self.app.selected_capabilities)

    async def test_invalid_name_stays_on_project_screen(self):
        self.app.name.value = "../outside"
        await self.app.advance(None)
        self.assertEqual(0, self.app.step)
        self.assertTrue(self.app.error.visible)

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
