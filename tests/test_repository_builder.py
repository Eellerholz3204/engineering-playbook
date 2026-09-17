"""Regression tests exercise actual PowerShell creation in disposable directories."""

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from repository_builder.core import (
    ROOT, CreationPlan, create_repository, document_paths, load_catalog,
    powershell_command, powershell_executable,
)


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="playbook-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.catalog = load_catalog()
        self.plan = CreationPlan("example-project", str(self.base / "example-project"),
            initialize_git=False, playbook_version=self.catalog["playbook_version"])

    def run_ps(self, script):
        return subprocess.run([powershell_executable(), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "RemoteSigned", "-Command", script],
            capture_output=True, text=True, timeout=120)

    def test_configuration_round_trip_and_invalid_types(self):
        plan = replace(self.plan, project_type="dbt-python", capabilities=("service-operations", "ai-governance"))
        self.assertEqual(plan, CreationPlan.from_json(plan.to_json(), self.catalog))
        for changes in ({"create_venv": "false"}, {"capabilities": "ai-governance"},
                        {"project_type": "other"}, {"playbook_version": "0.0.0"},
                        {"extra": "unsupported"}, {"schema_version": True}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                CreationPlan.from_json(json.dumps({**json.loads(plan.to_json()), **changes}), self.catalog)

    def test_invalid_destinations_and_names_are_rejected(self):
        target = Path(self.plan.repository_path)
        target.mkdir()
        (target / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.plan.validate(self.catalog)
        for name in ("../escape", "bad\"name", "123name", "CON", "", "two words"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                replace(self.plan, project_name=name).validate(self.catalog, check_destination=False)
        self.assertEqual("keep", (target / "keep.txt").read_text())

    def test_capabilities_deduplicate_documents(self):
        baseline = document_paths(self.catalog, "dbt-python")
        self.assertEqual(baseline, document_paths(self.catalog, "dbt-python", ("service-operations",)))
        self.assertGreater(len(document_paths(self.catalog, "dbt-python", ("ai-governance",))), len(baseline))

    def test_every_profile_and_multiple_capabilities(self):
        for profile in self.catalog["repository_profiles"]:
            with self.subTest(profile=profile):
                plan = replace(self.plan, repository_path=str(self.base / profile), project_type=profile,
                               capabilities=("ai-governance", "document-processing"))
                output = []
                self.assertEqual(0, create_repository(plan, output.append), "\n".join(output))
                destination = Path(plan.repository_path)
                config = json.loads((destination / ".engineering-playbook.json").read_text(encoding="utf-8-sig"))
                self.assertEqual(profile, config["project_type"])
                self.assertEqual(list(plan.capabilities), config["capabilities"])
                for document in document_paths(self.catalog, profile, plan.capabilities):
                    self.assertTrue((destination / document).is_file(), document)
                self.assertEqual(profile in {"python", "dbt-python"}, (destination / "pyproject.toml").exists())
                self.assertEqual(profile in {"dbt", "dbt-python"}, (destination / "dbt_project.yml").exists())

    def test_copied_command_preserves_literal_paths(self):
        plan = replace(self.plan, repository_path=str(self.base / "O'Brien $literal" / "example-project"))
        result = self.run_ps(powershell_command(plan))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue((Path(plan.repository_path) / ".engineering-playbook.json").exists())

    def test_profile_wrapper_forwards_parameters_and_preserves_reconcile_defaults(self):
        profile = self.base / "profile.ps1"
        destination = self.base / "wrapped"
        quote = lambda value: "'" + str(value).replace("'", "''") + "'"
        script = f"""
$ErrorActionPreference = 'Stop'
$PROFILE = {quote(profile)}
& {quote(ROOT / 'scripts/install_engineering_playbook_profile.ps1')} -PlaybookSourcePath {quote(ROOT)}
. $PROFILE
New-EngineeringRepository -ProjectName 'wrapped-project' -RepositoryPath {quote(destination)} -ProjectType dbt-python -Capabilities ai-governance,document-processing -NoGit
Install-EngineeringPlaybook -RepositoryPath {quote(destination)} -Reconcile
"""
        result = self.run_ps(script)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        config = json.loads((destination / ".engineering-playbook.json").read_text(encoding="utf-8-sig"))
        self.assertEqual("wrapped-project", config["project_name"])
        self.assertEqual(["ai-governance", "document-processing"], config["capabilities"])
        self.assertIn("Profile: dbt-python; Capabilities: ai-governance, document-processing", result.stdout)

    def test_git_and_virtual_environment(self):
        plan = replace(self.plan, project_type="python", initialize_git=True, create_venv=True)
        output = []
        self.assertEqual(0, create_repository(plan, output.append), "\n".join(output))
        destination = Path(plan.repository_path)
        self.assertTrue((destination / ".git").is_dir())
        self.assertTrue((destination / ".venv/pyvenv.cfg").is_file())

    def test_invalid_venv_does_not_create_directory(self):
        command = powershell_command(replace(self.plan, create_venv=True))
        result = self.run_ps(command)
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(Path(self.plan.repository_path).exists())


if __name__ == "__main__":
    unittest.main()
