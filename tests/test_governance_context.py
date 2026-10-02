from dataclasses import replace
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from tests import test_repository_builder as builder_tests
from repository_builder.core import ROOT, create_repository, powershell_executable
from scripts.verify_governance_context import check


class GovernanceTests(unittest.TestCase):
    setUp = builder_tests.BuilderTests.setUp
    def test_metis_creation_and_preservation(self):
        plan = replace(self.plan, capabilities=("metis-governance",))
        output = []
        self.assertEqual(0, create_repository(plan, output.append), "\n".join(output))
        repo = Path(plan.repository_path)
        agents = repo / "AGENTS.md"
        self.assertIn("METIS GOVERNANCE CONTEXT v1", agents.read_text())
        self.assertIn("## Model routing", agents.read_text())
        self.assertIn("governed-judgment/medium", agents.read_text())
        self.assertEqual([], check(repo, source=ROOT, local_only=True))
        central = self.base / "authority"
        (central / "docs").mkdir(parents=True)
        for doc in (repo / "docs").rglob("*.md"):
            target = central / "docs" / doc.relative_to(repo / "docs")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(doc, target)
        for name in ("contract_agent_workflow.md", "data_platform_architecture.md", "reference_data.md"):
            (central / "docs" / name).write_text("test authority")
        self.assertEqual([], check(repo, metis=True, metis_root=central, source=ROOT))
        (central / "docs/reference_data.md").unlink()
        self.assertTrue(any("Missing Metis authority" in e for e in check(repo, metis=True, metis_root=central)))
        before = agents.read_bytes() + b"\nLocal rules must survive.\n"
        agents.write_bytes(before)
        command = [powershell_executable(), "-NoProfile", "-File", str(ROOT / "scripts/install_engineering_playbook.ps1"),
                   "-RepositoryPath", str(repo), "-PlaybookSourcePath", str(ROOT), "-Reconcile"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, agents.read_bytes())
        self.assertIn("reconcile governance blocks", result.stdout)

    def test_missing_entrypoint_and_stale_asset_fail(self):
        self.assertEqual(0, create_repository(self.plan, lambda line: None))
        repo = Path(self.plan.repository_path)
        self.assertNotIn("METIS GOVERNANCE", (repo / "AGENTS.md").read_text())
        (repo / "engineering-playbook/GOVERNANCE_CONTEXT.md").write_text("stale")
        self.assertTrue(any("differs" in e for e in check(repo, source=ROOT, local_only=True)))
        (repo / "AGENTS.md").unlink()
        result = subprocess.run([sys.executable, str(ROOT / "scripts/verify_governance_context.py"), "--repo", str(repo)], capture_output=True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn(b"Missing required context: AGENTS.md", result.stdout)
