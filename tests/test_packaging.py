from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from repository_builder.runtime import resource_root
from repository_builder.core import ROOT


class PackagingTests(unittest.TestCase):
    def test_source_resources_are_relative_to_package(self):
        self.assertEqual(ROOT, resource_root())

    def test_frozen_resources_are_relative_to_executable_not_checkout(self):
        fake = ROOT / "some relocated directory" / "_runtime" / "RepositoryBuilder.Runtime.exe"
        with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", str(fake)):
            self.assertEqual(fake.parent.parent / "playbook", resource_root())

    def test_manifest_excludes_local_settings_and_environments(self):
        import json
        manifest = json.loads((ROOT / "playbook.json").read_text())
        forbidden = {".venv", ".vscode", ".git", ".builder-qa", ".launcher", ".build", ".build-tools"}
        for name in manifest["immutable_framework_files"]:
            self.assertNotIn(Path(name).parts[0], forbidden)
            self.assertTrue((ROOT / name).is_file(), name)
