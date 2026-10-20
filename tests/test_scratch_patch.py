"""Portable scratch migration contracts, including preserved custom instructions."""

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zipfile

from repository_builder import patching, scratch_patch
from repository_builder import patch_downloads
from repository_builder.app import RepositoryBuilder
from repository_builder.core import ROOT, powershell_executable
from repository_builder.patch_ui import patch_label, patch_metadata


def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class ScratchPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts = tempfile.TemporaryDirectory(prefix="scratch-feature-bundle-")
        cls.bundle = Path(cls.artifacts.name) / "scratch.zip"
        cls.release = scratch_patch.build(ROOT, cls.bundle, "scratch-portable", "Add external scratch; preserve custom instructions.")

    @classmethod
    def tearDownClass(cls):
        cls.artifacts.cleanup()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="scratch-feature-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "repo"
        self.scratch = self.root / "external"
        environment = patch.dict(os.environ, {"ENGINEERING_PLAYBOOK_SCRATCH_ROOT": str(self.scratch)})
        environment.start()
        self.addCleanup(environment.stop)
        self.fixture("3.2.0")

    def fixture(self, version):
        framework = self.repo / "engineering-playbook"
        framework.mkdir(parents=True, exist_ok=True)
        (framework / "playbook.json").write_bytes(patching.json_bytes({
            "schema_version": scratch_patch.SUPPORTED[version], "playbook_version": version,
            "install_directory": "engineering-playbook", "local_customization": "retain"}))
        (framework / "VERSION").write_bytes(version.encode() + b"\r\n")
        (framework / "DEVELOPMENT_WORKFLOW.md").write_bytes(b"\xef\xbb\xbfCustom workflow; no automatic release.\r\n")
        (framework / "SHA256SUMS.txt").write_bytes(b"Historical checksum manifest, unchanged\n")
        (self.repo / "AGENTS.md").write_bytes(b"\xef\xbb\xbf# Our instructions\r\nCustom organizational rules.\nNo deployments without approval.")
        (self.repo / "product.py").write_bytes(b"print('product')\n")
        (self.repo / ".engineering-playbook.json").write_bytes(b'{"playbook_version":"custom","retain":true}')

    def test_one_artifact_applies_across_families_preserves_bytes_and_repeats(self):
        for version in scratch_patch.SUPPORTED:
            with self.subTest(version=version):
                self.repo = self.root / version
                self.fixture(version)
                before = tree(self.repo)
                preview = patching.inspect_patch(self.bundle, self.repo)
                self.assertTrue(preview["can_apply"], preview["conflicts"])
                self.assertEqual(4, len(preview["changes"]))
                self.assertEqual(before, tree(self.repo))
                self.assertEqual(version, preview["target_version"])
                self.assertFalse(preview["configuration_update"])
                result = patching.apply_patch(self.bundle, self.repo, preview["sha256"], preview["observed"])
                self.assertEqual("applied", result["status"])
                after = tree(self.repo)
                self.assertEqual(set(before) | scratch_patch.PATHS, set(after))
                for name, content in before.items():
                    if name == "AGENTS.md":
                        self.assertTrue(after[name].startswith(content))
                        self.assertEqual(1, after[name].count(scratch_patch.BEGIN.encode()))
                    else:
                        self.assertEqual(content, after[name], name)
                backup = Path(result["backup"])
                self.assertEqual(before["AGENTS.md"], (backup / "AGENTS.md").read_bytes())
                self.assertEqual("applied", patching.read_json((backup / "transaction.json").read_bytes())["status"])
                self.assertEqual("already_applied", patching.apply_patch(self.bundle, self.repo, preview["sha256"])["status"])
                self.assertEqual(after, tree(self.repo))
                # Exercise the installed helper, not code evaluation during apply.
                resolved = subprocess.run([powershell_executable(), "-NoProfile", "-NonInteractive",
                    "-File", str(self.repo / scratch_patch.HELPER), "-RepositoryPath", str(self.repo),
                    "-TaskId", "product-task"], capture_output=True, text=True, timeout=30)
                self.assertEqual(0, resolved.returncode, resolved.stderr)
                self.assertTrue(Path(resolved.stdout.strip()).is_relative_to(self.scratch))
                self.assertTrue(Path(resolved.stdout.strip()).is_dir())

    def test_equivalent_existing_feature_bytes_are_reused_not_rewritten(self):
        _, payload, sha = patching.load_patch(self.bundle)
        for name in scratch_patch.PATHS - {"AGENTS.md"}:
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"\xef\xbb\xbf" + payload[name].replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        agents = self.repo / "AGENTS.md"
        agents.write_bytes(agents.read_bytes() + b"\r\n\r\n" + scratch_patch.BLOCK.replace("\n", "\r\n").encode())
        before = tree(self.repo)
        self.assertTrue(patching.inspect_patch(self.bundle, self.repo)["already_applied"])
        self.assertEqual("already_applied", patching.apply_patch(self.bundle, self.repo, sha)["status"])
        self.assertEqual(before, tree(self.repo))
        self.assertFalse(self.scratch.exists())

    def test_custom_feature_files_and_edited_blocks_block_without_writes(self):
        _, payload, sha = patching.load_patch(self.bundle)
        for name in scratch_patch.PATHS:
            with self.subTest(path=name):
                path = self.repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                original = path.read_bytes() if path.exists() else None
                path.write_bytes(payload[name] + b"custom code\n" if name != "AGENTS.md"
                                 else scratch_patch.BLOCK.replace("Keep temporary", "Keep MY temporary").encode())
                before = tree(self.repo)
                report = patching.inspect_patch(self.bundle, self.repo)
                self.assertIn(name, report["conflicts"])
                self.assertTrue(report["conflict_reasons"][name])
                with self.assertRaisesRegex(ValueError, "no files changed"):
                    patching.apply_patch(self.bundle, self.repo, sha)
                self.assertEqual(before, tree(self.repo))
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)
        self.assertFalse(self.scratch.exists())

    def test_marker_encoding_and_fence_safety(self):
        bad = [(scratch_patch.BLOCK * 2).encode(), scratch_patch.BEGIN.encode(),
               b"# instructions\n```python\nnot_closed = True\n", b"\xff\xfeinvalid encoding",
               ("```\n" + scratch_patch.BLOCK + "```\n").encode(),
               b"<!-- unfinished comment", ("Prefix " + scratch_patch.BLOCK).encode()]
        for data in bad:
            with self.subTest(data=data[:30]):
                (self.repo / "AGENTS.md").write_bytes(data)
                self.assertIn("AGENTS.md", patching.inspect_patch(self.bundle, self.repo)["conflicts"])
        for original in (b"", b"# title\n", b"# title\r\n", b"# title", b"\xef\xbb\xbf# title\r\n",
                         b"```python\nprint('ok')\n```\n"):
            added = scratch_patch.append_block(original)
            self.assertTrue(added.startswith(original))
            self.assertEqual(added, scratch_patch.append_block(added))

    def test_missing_agents_and_no_config_are_supported_without_inventing_a_version(self):
        (self.repo / "AGENTS.md").unlink()
        (self.repo / ".engineering-playbook.json").unlink()
        preview = patching.inspect_patch(self.bundle, self.repo)
        patching.apply_patch(self.bundle, self.repo, preview["sha256"])
        self.assertEqual(scratch_patch.BLOCK, (self.repo / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertFalse((self.repo / ".engineering-playbook.json").exists())
        (self.repo / "engineering-playbook/VERSION").write_text("99.0")
        report = patching.inspect_patch(self.bundle, self.repo)
        self.assertFalse(report["can_apply"])
        self.assertIn("VERSION disagreement", report["conflict_reasons"]["engineering-playbook/playbook.json"])

    def test_rejects_unknown_version_schema_and_linked_destination(self):
        path = self.repo / "engineering-playbook/playbook.json"
        base = patching.read_json(path.read_bytes())
        for edits in ({"playbook_version": "99.0"}, {"schema_version": 1},
                      {"schema_version": True}, {"install_directory": "../elsewhere"}):
            path.write_bytes(patching.json_bytes({**base, **edits}))
            self.assertFalse(patching.inspect_patch(self.bundle, self.repo)["can_apply"])
        path.write_bytes(patching.json_bytes(base))
        helper = self.repo / scratch_patch.HELPER
        target = self.root / "outside"
        target.mkdir()
        (target / helper.name).write_text("Do not touch")
        if os.name == "nt":
            process = subprocess.run([powershell_executable(), "-NoProfile", "-NonInteractive", "-Command",
                f"New-Item -ItemType Junction -Path '{helper.parent}' -Target '{target}'"],
                capture_output=True, timeout=30)
            self.assertEqual(0, process.returncode, process.stderr)
        else:
            helper.parent.symlink_to(target, target_is_directory=True)
        before = tree(target)
        self.assertIn(scratch_patch.HELPER, patching.inspect_patch(self.bundle, self.repo)["conflicts"])
        self.assertEqual(before, tree(target))

    def test_changed_inputs_since_preview_require_new_review_and_failure_rolls_back(self):
        preview = patching.inspect_patch(self.bundle, self.repo)
        agents = self.repo / "AGENTS.md"
        agents.write_bytes(agents.read_bytes() + b"\nNew instructions during review.\n")
        before = tree(self.repo)
        with self.assertRaisesRegex(ValueError, "changed after preview"):
            patching.apply_patch(self.bundle, self.repo, preview["sha256"], preview["observed"])
        self.assertEqual(before, tree(self.repo))
        self.assertFalse(self.scratch.exists())
        real_write = patching.atomic_write

        def fail(path, data):
            if path == self.repo / scratch_patch.HELPER:
                raise OSError("injected write failure")
            return real_write(path, data)

        with patch.object(patching, "atomic_write", side_effect=fail):
            with self.assertRaisesRegex(RuntimeError, "rolled_back"):
                patching.apply_patch(self.bundle, self.repo, preview["sha256"])
        self.assertEqual(before, tree(self.repo))

    def test_archive_recipe_scope_integrity_and_exclusive_build(self):
        with zipfile.ZipFile(self.bundle) as archive:
            entries = {n: archive.read(n) for n in archive.namelist()}
        manifest = patching.read_json(entries["patch.json"])
        self.assertEqual(2, manifest["schema_version"])
        self.assertEqual(scratch_patch.PATHS, set(manifest["after"]))
        for edit in ("extra", "kind", "version", "payload", "block"):
            changed = dict(entries)
            data = {**manifest, "after": dict(manifest["after"])}
            if edit == "extra":
                data["after"]["product.py"] = patching.digest(b"bad")
                changed["payload/product.py"] = b"bad"
            elif edit == "kind":
                data["kind"] = "execute"
            elif edit == "version":
                data["feature_version"] = 2
            elif edit == "block":
                changed["payload/AGENTS.md"] = b"Overwrite all custom instructions."
                data["after"]["AGENTS.md"] = patching.digest(changed["payload/AGENTS.md"])
            else:
                changed["payload/" + scratch_patch.HELPER] = b"modified payload"
            changed["patch.json"] = patching.json_bytes(data)
            bad = self.root / f"{edit}.zip"
            with zipfile.ZipFile(bad, "w") as archive:
                for name, content in changed.items():
                    archive.writestr(name, content)
            with self.assertRaises(ValueError):
                patching.inspect_patch(bad, self.repo)
        with self.assertRaisesRegex(ValueError, "already exists"):
            scratch_patch.build(ROOT, self.bundle, "again", "Do not overwrite")
        with self.assertRaisesRegex(ValueError, "checksum"):
            patching.load_patch(self.bundle, "0" * 64)

    def test_cli_builder_and_local_discovery_use_the_same_feature_recipe(self):
        bundle = self.root / "cli.zip"
        build = subprocess.run([sys.executable, str(ROOT / "scripts/playbook_patch.py"), "build-scratch",
            "--output", str(bundle), "--patch-id", "cli-scratch", "--summary", "Portable scratch"],
            capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(0, build.returncode, build.stderr)
        self.assertEqual("agent-scratch-workspace", json.loads(build.stdout)["kind"])
        self.assertEqual(2, patch_metadata(bundle)["schema_version"])
        self.assertIn("preserves custom instructions", patch_label(bundle))
        cli = subprocess.run([sys.executable, str(ROOT / "scripts/playbook_patch.py"), "preview",
            "--bundle", str(bundle), "--repo", str(self.repo)], capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(0, cli.returncode, cli.stderr)
        self.assertIn(scratch_patch.BEGIN, json.loads(cli.stdout)["agent_blocks"])

        async def scenario():
            page = MagicMock()
            page.services = []
            app = RepositoryBuilder(page)
            app.open_patch_view(None)
            view = app.patch_view
            view.repository.value = str(self.repo)
            view.bundle.value = str(bundle)
            view.choices["bundles"].add(str(bundle))
            published = patch_downloads.PublishedPatch("playbook-patch-portable", "published.zip",
                "Playbook patch: Portable scratch", patching.digest(bundle.read_bytes()),
                "# Portable scratch\n\nPreserve custom instructions.")
            view.published = {published.key: published}
            before = tree(self.repo)
            await view.repository_selected()
            self.assertEqual("Compatible", view.compatibility[str(bundle)][0])
            self.assertEqual([str(bundle)], [o.key for o in view.bundle.options])
            self.assertEqual("Portable scratch · Compatible", view.bundle.options[0].text)
            self.assertEqual(published.notes, view.notes_text.value)
            self.assertIsNone(view.report)
            self.assertEqual(before, tree(self.repo))
            await view.preview(None)
            self.assertEqual("Apply patch", app.next.content)
            self.assertIn(scratch_patch.BEGIN, view.report["agent_blocks"])
            await view.apply(None)
            self.assertTrue(view.completed)
            self.assertEqual([str(bundle)], [o.key for o in view.bundle.options])
            self.assertEqual("Already applied", view.compatibility[str(bundle)][0])
            self.assertTrue((self.repo / "AGENTS.md").read_bytes().startswith(before["AGENTS.md"]))

        with patch("repository_builder.patch_ui.cached_patches", return_value=[]), \
             patch("repository_builder.patch_ui.PatchView.discovery_locations", return_value=(set(), set())):
            asyncio.run(scenario())

    def test_feature_download_validates_before_exposing_offline_choice(self):
        sha = self.release["sha256"]
        item = patch_downloads.PublishedPatch("playbook-patch-portable", self.bundle.name, "Agent scratch workspaces", sha)
        before = tree(self.repo)
        with patch.dict(os.environ, {"LOCALAPPDATA": str(self.root / "local")}), \
             patch.object(patch_downloads, "fetch", side_effect=[
                 f"{sha}  {item.name}\n".encode(), self.bundle.read_bytes()]):
            downloaded, actual = patch_downloads.download_patch(item, self.repo)
            self.assertEqual(sha, actual)
            self.assertEqual(sha, patch_downloads.cached_checksum(downloaded))
            self.assertTrue(patching.inspect_patch(downloaded, self.repo, actual)["can_apply"])
            self.assertIn("additive", patch_label(downloaded))
        self.assertEqual(before, tree(self.repo))
