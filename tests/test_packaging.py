from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from repository_builder.runtime import resource_root
from repository_builder.core import ROOT
from repository_builder.core import CreationPlan, create_repository
from scripts.build_windows_release import copy_playbook


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

    def test_packaged_allowlist_can_generate_external_workspace(self):
        with tempfile.TemporaryDirectory(prefix="playbook-package-") as temporary:
            base = Path(temporary)
            bundle = base / "relocated playbook"
            catalog = copy_playbook(bundle)  # Also verifies every packaged checksum.
            scratch = base / "scratch"
            plan = CreationPlan("packaged-project", str(base / "project"), initialize_git=False,
                                playbook_version=catalog["playbook_version"])
            with patch.dict(os.environ, {"ENGINEERING_PLAYBOOK_SCRATCH_ROOT": str(scratch)}):
                output = []
                self.assertEqual(0, create_repository(plan, output.append, root=bundle), "\n".join(output))
            self.assertTrue(list(scratch.glob("*/default")))
            self.assertEqual(set(catalog["immutable_framework_files"]),
                             {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()})
            self.assertTrue((Path(plan.repository_path) / "engineering-playbook/scripts/initialize_agent_workspace.ps1").is_file())
