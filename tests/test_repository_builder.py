"""Regression tests exercise actual PowerShell creation in disposable directories."""

from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from repository_builder.core import (
    ROOT, CreationPlan, create_repository, document_paths, load_catalog,
    powershell_command, powershell_executable,
)


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="playbook-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.scratch_root = self.base / "external scratch"
        environment = patch.dict(os.environ, {"ENGINEERING_PLAYBOOK_SCRATCH_ROOT": str(self.scratch_root)})
        environment.start()
        self.addCleanup(environment.stop)
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

    def test_json_schema_version_in_available_powershell_editions(self):
        config = self.base / "configuration.json"
        for shell in ("powershell", "pwsh"):
            executable = shutil.which(shell)
            if not executable:
                continue
            for version in (1, True, "1", 1.0, 2):
                with self.subTest(shell=shell, version=repr(version)):
                    config.write_text(json.dumps({**json.loads(self.plan.to_json()), "schema_version": version}), encoding="utf-8")
                    result = subprocess.run([executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "RemoteSigned",
                        "-File", str(ROOT / "scripts/create_repository_from_config.ps1"),
                        "-ConfigurationPath", str(config), "-WhatIf"], capture_output=True, text=True, timeout=30)
                    if type(version) is int and version == 1:
                        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    else:
                        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                        self.assertIn("Unsupported configuration version", result.stderr)
        self.assertFalse(Path(self.plan.repository_path).exists())
        self.assertFalse(self.scratch_root.exists())

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
                scratch_line = next(line for line in output if line.startswith("Agent scratch space (outside repository): "))
                workspace = Path(scratch_line.split(": ", 1)[1])
                self.assertTrue(workspace.is_dir())
                self.assertTrue(workspace.is_relative_to(self.scratch_root))
                self.assertFalse(workspace.is_relative_to(destination))
                self.assertNotIn(str(self.scratch_root), (destination / ".engineering-playbook.json").read_text())
                self.assertIn("## Agent scratch space", (destination / "AGENTS.md").read_text())
                self.assertTrue((destination / "engineering-playbook/scripts/initialize_agent_workspace.ps1").is_file())
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

    def test_workspace_lifecycle_in_available_powershell_editions(self):
        helper = ROOT / "scripts/initialize_agent_workspace.ps1"
        repo = self.base / "O'Brien $literal" / "same-name"
        repo.mkdir(parents=True)
        (repo / "project.txt").write_text("project content")
        for shell in ("powershell", "pwsh"):
            executable = shutil.which(shell)
            if not executable:
                continue
            with self.subTest(shell=shell):
                def invoke(path=repo, task=shell, *options):
                    result = subprocess.run([executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "RemoteSigned",
                        "-File", str(helper), "-RepositoryPath", str(path), "-TaskId", task, *options],
                        capture_output=True, text=True, timeout=30)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    return Path(result.stdout.strip().splitlines()[-1])

                workspace = invoke(repo, shell, "-ResolveOnly")
                self.assertFalse(workspace.exists())
                self.assertEqual(workspace, invoke(repo, shell, "-WhatIf"))
                self.assertFalse(workspace.exists())
                self.assertEqual(workspace, invoke())
                note = workspace / "notes.txt"
                note.write_text("resume this task")
                self.assertEqual(workspace, invoke())
                self.assertEqual("resume this task", note.read_text())
                self.assertNotEqual(workspace, invoke(repo, shell + "-another"))
                self.assertNotEqual(workspace.parent, invoke(self.base / "other" / "same-name").parent)
                self.assertEqual(["project.txt"], [p.name for p in repo.iterdir()])

    def test_workspace_invalid_locations_fail_before_generation(self):
        helper = ROOT / "scripts/initialize_agent_workspace.ps1"
        invalid_roots = [str(Path(self.plan.repository_path) / "scratch"), "relative-scratch"]
        if os.name == "nt":
            invalid_roots += ["C:relative-scratch", "\\relative-scratch"]
        for scratch in invalid_roots:
            with self.subTest(scratch=scratch), patch.dict(os.environ, {"ENGINEERING_PLAYBOOK_SCRATCH_ROOT": scratch}):
                result = self.run_ps(powershell_command(self.plan))
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(Path(self.plan.repository_path).exists())
        for task in ("../escape", "two words", "CON", ""):
            result = subprocess.run([powershell_executable(), "-NoProfile", "-File", str(helper),
                "-RepositoryPath", self.plan.repository_path, "-TaskId", task], capture_output=True, timeout=30)
            self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.scratch_root.exists())

    @unittest.skipUnless(os.name == "nt", "Windows directory junction")
    def test_workspace_rejects_directory_link_into_project(self):
        repo = Path(self.plan.repository_path)
        repo.mkdir()
        # All targets are disposable test directories; no existing links are modified.
        command = f"New-Item -ItemType Junction -Path '{self.scratch_root}' -Target '{repo}' | Out-Null"
        result = self.run_ps(command)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        result = subprocess.run([powershell_executable(), "-NoProfile", "-File",
            str(ROOT / "scripts/initialize_agent_workspace.ps1"), "-RepositoryPath", str(repo)],
            capture_output=True, text=True, timeout=30)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("directory links", result.stderr)
        self.assertEqual([], list(repo.iterdir()))


if __name__ == "__main__":
    unittest.main()
