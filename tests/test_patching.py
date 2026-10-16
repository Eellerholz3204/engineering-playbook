"""Maintained patch delivery contracts: preview, preservation, integrity and recovery."""

import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zipfile

from repository_builder import patching
from repository_builder.core import ROOT, CreationPlan, create_repository, load_catalog
from repository_builder.app import RepositoryBuilder
from scripts.build_windows_release import copy_playbook


def refresh_fixture(root):
    catalog = json.loads((root / "playbook.json").read_text())
    pins_path = root / "governance-context.json"
    pins = json.loads(pins_path.read_text())
    pins["sha256"] = {name: patching.digest((root / name).read_bytes().replace(b"\r\n", b"\n")) for name in pins["sha256"]}
    pins_path.write_bytes(patching.json_bytes(pins))
    (root / "SHA256SUMS.txt").write_text("".join(
        f"{patching.digest((root / name).read_bytes())}  {name}\n"
        for name in sorted(catalog["immutable_framework_files"]) if name != "SHA256SUMS.txt"), encoding="ascii")


def tree_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class PatchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="playbook-patch-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.base = self.root / "base"
        self.target = self.root / "target"
        self.repo = self.root / "existing project"
        self.scratch = self.root / "scratch-é"
        environment = patch.dict(os.environ, {"ENGINEERING_PLAYBOOK_SCRATCH_ROOT": str(self.scratch)})
        environment.start()
        self.addCleanup(environment.stop)
        copy_playbook(self.base)
        shutil.copytree(self.base, self.target)
        # A released framework change with a new file and changed instructions.
        (self.target / "GOVERNANCE_CONTEXT.md").write_text("Updated supported framework policy.\n")
        (self.target / "templates/agents.md").write_text("Updated governance startup block.\n")
        (self.target / "scripts/patch-feature.ps1").write_text("throw 'Bundle code must never be executed by the updater'\n")
        catalog = json.loads((self.target / "playbook.json").read_text())
        catalog["playbook_version"] = "3.3.1"
        catalog["immutable_framework_files"].append("scripts/patch-feature.ps1")
        (self.target / "playbook.json").write_bytes(patching.json_bytes(catalog))
        (self.target / "VERSION").write_text("3.3.1\n")
        refresh_fixture(self.target)
        shutil.copytree(self.base, self.repo / "engineering-playbook")
        (self.repo / "AGENTS.md").write_text("Existing organization and project instructions.\n")
        (self.repo / "docs").mkdir()
        (self.repo / "docs/product_vision.md").write_text("Our real product vision.\n")
        (self.repo / "source.py").write_text("project_code = True\n")
        (self.repo / ".engineering-playbook.json").write_bytes(patching.json_bytes({
            "schema_version": 1, "project_name": "existing-project", "project_type": "generic",
            "capabilities": [], "playbook_version": load_catalog()["playbook_version"], "local_setting": "preserve"}))
        self.bundle = self.root / "release.zip"
        self.release = patching.build_patch(self.base, self.target, self.bundle, "test-patch", "Test framework update")

    def test_preview_apply_reapply_preserve_project_and_backups(self):
        before = tree_bytes(self.repo)
        preview = patching.inspect_patch(self.bundle, self.repo, self.release["sha256"])
        self.assertTrue(preview["can_apply"])
        self.assertTrue(preview["review_required"])
        self.assertEqual(before, tree_bytes(self.repo))
        self.assertFalse(self.scratch.exists())
        applied = patching.apply_patch(self.bundle, self.repo, preview["sha256"])
        self.assertEqual("applied", applied["status"])
        backup = Path(applied["backup"])
        self.assertTrue(backup.is_relative_to(self.scratch))
        for name in ("AGENTS.md", "docs/product_vision.md", "source.py"):
            self.assertEqual(before[name], (self.repo / name).read_bytes())
        self.assertEqual(tree_bytes(self.target), tree_bytes(self.repo / "engineering-playbook"))
        self.assertEqual(before["engineering-playbook/GOVERNANCE_CONTEXT.md"],
                         (backup / "engineering-playbook/GOVERNANCE_CONTEXT.md").read_bytes())
        self.assertIn("Updated governance", (backup / "AGENTS.blocks.md").read_text())
        config = json.loads((self.repo / ".engineering-playbook.json").read_text())
        self.assertEqual("preserve", config["local_setting"])
        self.assertEqual("3.3.1", config["playbook_version"])
        self.assertEqual("test-patch", config["last_playbook_patch"]["patch_id"])
        after = tree_bytes(self.root)
        self.assertEqual("already_applied", patching.apply_patch(self.bundle, self.repo, preview["sha256"])["status"])
        self.assertEqual(after, tree_bytes(self.root))

    def test_conflicts_and_stale_release_checksum_make_no_changes(self):
        local = self.repo / "engineering-playbook/GOVERNANCE_CONTEXT.md"
        local.write_text("Local framework customization")
        before = tree_bytes(self.repo)
        report = patching.inspect_patch(self.bundle, self.repo)
        self.assertIn("GOVERNANCE_CONTEXT.md", report["conflicts"])
        with self.assertRaisesRegex(ValueError, "no files changed"):
            patching.apply_patch(self.bundle, self.repo, report["sha256"])
        self.assertEqual(before, tree_bytes(self.repo))
        self.assertFalse(self.scratch.exists())
        with self.bundle.open("ab") as stream:
            stream.write(b"changed after preview")
        with self.assertRaisesRegex(ValueError, "checksum"):
            patching.apply_patch(self.bundle, self.repo, report["sha256"])

    def test_payload_tampering_and_unsafe_zip_entries_are_rejected(self):
        with zipfile.ZipFile(self.bundle) as archive:
            entries = {n: archive.read(n) for n in archive.namelist()}
        for name in ("../outside", "payload/../../AGENTS.md", "payload/C:evil", "payload/templates/CON", "payload/playbook.json"):
            with self.subTest(name=name):
                malformed = self.root / ("bad-" + str(len(list(self.root.glob("bad-*")))) + ".zip")
                changed = {**entries, name: b"untrusted"}
                with zipfile.ZipFile(malformed, "w") as archive:
                    for entry, data in changed.items():
                        archive.writestr(entry, data)
                before = tree_bytes(self.repo)
                with self.assertRaises((ValueError, KeyError)):
                    patching.inspect_patch(malformed, self.repo)
                self.assertEqual(before, tree_bytes(self.repo))

    def test_write_failure_rolls_back_and_retains_external_backup(self):
        before = tree_bytes(self.repo)
        real_write = patching.atomic_write
        failed = False

        def fail_once(path, data):
            nonlocal failed
            if path == self.repo / "engineering-playbook/scripts/patch-feature.ps1" and not failed:
                failed = True
                raise OSError("Simulated disk write failure")
            return real_write(path, data)

        with patch.object(patching, "atomic_write", side_effect=fail_once):
            with self.assertRaisesRegex(RuntimeError, "rolled_back"):
                patching.apply_patch(self.bundle, self.repo, self.release["sha256"])
        self.assertTrue(failed)
        self.assertEqual(before, tree_bytes(self.repo))
        journals = list(self.scratch.rglob("transaction.json"))
        self.assertEqual(1, len(journals))
        self.assertEqual("rolled_back", json.loads(journals[0].read_text())["status"])

    def test_real_generator_output_can_be_patched_by_cli(self):
        repo = self.root / "generated"
        plan = CreationPlan("generated", str(repo), initialize_git=False, playbook_version=load_catalog()["playbook_version"])
        output = []
        self.assertEqual(0, create_repository(plan, output.append), "\n".join(output))
        for action in ("preview", "apply"):
            process = subprocess.run([sys.executable, str(ROOT / "scripts/playbook_patch.py"), action,
                "--bundle", str(self.bundle), "--repo", str(repo), "--sha256", self.release["sha256"]],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertEqual(tree_bytes(self.target), tree_bytes(repo / "engineering-playbook"))

    def test_builder_preview_then_apply_and_input_change_invalidate_review(self):
        async def scenario():
            page = MagicMock()
            page.services = []
            app = RepositoryBuilder(page)
            app.open_patch_view(None)
            view = app.patch_view
            view.repository.value = str(self.repo)
            view.bundle.value = str(self.bundle)
            await view.preview(None)
            self.assertTrue(view.report["can_apply"])
            self.assertEqual("Apply patch", app.next.content)
            self.assertFalse(self.scratch.exists())
            view.bundle.value = "a different ZIP"
            await view.apply(None)
            self.assertIsNone(view.report)
            self.assertFalse(self.scratch.exists())
            view.bundle.value = str(self.bundle)
            await view.preview(None)
            await view.apply(None)
            self.assertTrue(view.completed, app.error.value)
            self.assertEqual("applied", view.report["status"])
            view.close(None)
            self.assertEqual("Choose type", app.next.content)
        asyncio.run(scenario())

    def test_invalid_snapshot_and_duplicate_zip_names_are_rejected(self):
        (self.target / "VERSION").write_text("0.0.0\n")
        with self.assertRaises(ValueError):
            patching.build_patch(self.base, self.target, self.root / "invalid.zip", "invalid", "Invalid snapshot")
        self.assertFalse((self.root / "invalid.zip").exists())
        duplicate = self.root / "duplicate.zip"
        with zipfile.ZipFile(self.bundle) as original, zipfile.ZipFile(duplicate, "w") as archive:
            for name in original.namelist():
                archive.writestr(name, original.read(name))
            archive.writestr("PATCH.JSON", original.read("patch.json"))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            patching.inspect_patch(duplicate, self.repo)

    @unittest.skipUnless(os.name == "nt", "Windows directory junction")
    def test_framework_link_cannot_redirect_patch_writes(self):
        linked_repo = self.root / "linked-project"
        linked_repo.mkdir()
        result = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"New-Item -ItemType Junction -Path '{linked_repo / 'engineering-playbook'}' -Target '{self.repo / 'engineering-playbook'}'"],
            capture_output=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stderr)
        with self.assertRaisesRegex(ValueError, "Directory links"):
            patching.inspect_patch(self.bundle, linked_repo)
