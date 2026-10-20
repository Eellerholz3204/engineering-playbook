"""Published patch discovery, network boundaries and validated cache contracts."""

import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError
from urllib.request import Request
import zipfile

from repository_builder import patch_downloads as downloads
from repository_builder.patching import digest, json_bytes


def bundle_bytes():
    files = {"VERSION": b"3.3.0\n", "playbook.json": json_bytes({
        "install_directory": "engineering-playbook", "playbook_version": "3.3.0",
        "immutable_framework_files": ["VERSION", "playbook.json", "SHA256SUMS.txt"]})}
    files["SHA256SUMS.txt"] = "".join(f"{digest(b)}  {n}\n" for n, b in files.items()).encode()
    hashes = {n: digest(b) for n, b in files.items()}
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("patch.json", json_bytes({"schema_version": 1, "patch_id": "test",
            "summary": "Test release", "base_version": "3.3.0", "target_version": "3.3.0",
            "before": hashes, "after": hashes}))
        for name, content in files.items():
            archive.writestr("payload/" + name, content)
    return stream.getvalue()


class PatchDownloadTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="patch-download-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        environment = patch.dict(os.environ, {"LOCALAPPDATA": str(self.root / "local-é")})
        environment.start()
        self.addCleanup(environment.stop)
        self.data = bundle_bytes()
        self.sha = digest(self.data)
        self.item = downloads.PublishedPatch("playbook-patch-test", "test.zip", "Test release", self.sha)
        self.sidecar = f"{self.sha}  test.zip\n".encode()

    def test_catalog_filters_pairs_and_paginates_without_trusting_urls(self):
        good = {"draft": False, "prerelease": False, "tag_name": self.item.tag, "name": "Test",
            "assets": [{"name": "test.zip", "size": len(self.data), "state": "uploaded",
                        "digest": "sha256:" + self.sha, "browser_download_url": "https://evil.invalid/file"},
                       {"name": "test.zip.sha256", "size": len(self.sidecar), "state": "uploaded"}]}
        invalid = [{**good, "draft": True}, {**good, "prerelease": True},
                   {**good, "tag_name": "builder-v1"}, {**good, "assets": good["assets"][:1]},
                   {**good, "tag_name": "playbook-patch-../../evil"}]
        first = [good, *invalid] + [{"draft": True}] * 94
        with patch.object(downloads, "fetch", side_effect=[json_bytes(first), b"[]"]) as fetch:
            found = downloads.available_patches()
        self.assertEqual(1, len(found))
        self.assertEqual(self.item.url, found[0].url)
        self.assertEqual(2, fetch.call_count)
        self.assertIn("page=2", fetch.call_args.args[0])
        with patch.object(downloads, "fetch", return_value=b"[]"):
            self.assertEqual([], downloads.available_patches())

    def test_network_limits_redirects_and_error_messages(self):
        for url in ("http://github.com/x", "https://evil.invalid/x", "https://github.com@evil.invalid/x",
                    "https://github.com:8443/x", "file:///tmp/x"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                downloads.check_url(url)
        with self.assertRaises(ValueError):
            downloads.GitHubRedirects().redirect_request(Request(self.item.url), None, 302, "", {}, "http://github.com/x")
        response = MagicMock()
        response.url = self.item.url
        response.headers = {}
        response.read.return_value = b"12345"
        response.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(downloads, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "size limit"):
                downloads.fetch(self.item.url, 4)
            self.assertEqual(30, opener.open.call_args.kwargs["timeout"])
            self.assertNotIn("Authorization", opener.open.call_args.args[0].headers)
            for error, message in ((HTTPError(self.item.url, 429, "", {}, None), "rate-limited"),
                                   (HTTPError(self.item.url, 404, "", {}, None), "HTTP 404"),
                                   (URLError("offline"), "connection")):
                opener.open.side_effect = error
                with self.assertRaisesRegex(ValueError, message):
                    downloads.fetch(self.item.url, 4)

    def test_download_cache_reuse_and_offline_pin(self):
        project = self.root / "consumer"
        project.mkdir()
        with patch.object(downloads, "fetch", side_effect=[self.sidecar, self.data]) as fetch:
            path, sha = downloads.download_patch(self.item, project)
        self.assertEqual(self.sha, sha)
        self.assertEqual(self.data, path.read_bytes())
        self.assertEqual(self.sidecar, path.with_suffix(".zip.sha256").read_bytes())
        self.assertEqual([path], downloads.cached_patches())
        self.assertEqual(sha, downloads.cached_checksum(path))
        self.assertEqual([], list(project.iterdir()))
        self.assertEqual(2, fetch.call_count)
        with patch.object(downloads, "fetch", return_value=self.sidecar) as fetch:
            self.assertEqual((path, sha), downloads.download_patch(self.item))
            self.assertEqual(1, fetch.call_count)  # Rechecks publisher checksum, reuses verified bytes.
        self.assertEqual([sha], [p.name for p in downloads.cache_directory().iterdir()])

    def test_failed_download_never_exposes_partial_or_unvalidated_zip(self):
        corrupt = b"not a patch zip"
        cases = [(self.sidecar, b"changed"), (f"{digest(corrupt)}  test.zip\n".encode(), corrupt),
                 (f"{self.sha}  wrong.zip\n".encode(), self.data)]
        item = downloads.PublishedPatch(self.item.tag, self.item.name, "Test")
        for sidecar, data in cases:
            with self.subTest(sidecar=sidecar), patch.object(downloads, "fetch", side_effect=[sidecar, data]):
                with self.assertRaises((ValueError, zipfile.BadZipFile)):
                    downloads.download_patch(item)
            self.assertEqual([], downloads.cached_patches())
            if downloads.cache_directory().exists():
                self.assertEqual([], list(downloads.cache_directory().iterdir()))
        with patch.object(downloads, "fetch", return_value=f"{'0' * 64}  test.zip\n".encode()):
            with self.assertRaisesRegex(ValueError, "disagree"):
                downloads.download_patch(self.item)
        with patch.object(downloads, "fetch", side_effect=[self.sidecar, ValueError("connection lost")]):
            with self.assertRaisesRegex(ValueError, "connection lost"):
                downloads.download_patch(self.item)
        self.assertEqual([], downloads.cached_patches())

    def test_cache_cannot_overlap_project_or_overwrite_corrupt_files(self):
        with self.assertRaisesRegex(ValueError, "outside the project"):
            downloads.download_patch(self.item, self.root)
        for name in ("../escape.zip", "CON.zip", "C:evil.zip"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                downloads.PublishedPatch(self.item.tag, name, "Test")
        with patch.object(downloads, "fetch", side_effect=[self.sidecar, self.data]):
            path, _ = downloads.download_patch(self.item)
        path.write_bytes(b"local change")
        with patch.object(downloads, "fetch", return_value=self.sidecar):
            with self.assertRaisesRegex(ValueError, "checksum"):
                downloads.download_patch(self.item)
        self.assertEqual(b"local change", path.read_bytes())
