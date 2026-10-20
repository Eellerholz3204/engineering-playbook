"""Read-only GitHub release discovery and validated, external patch downloads."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .core import ROOT
from .patching import MAX_BUNDLE_BYTES, digest, load_patch, ordinary_path, valid_path

REPOSITORY = "Eellerholz3204/engineering-playbook"
RELEASES_URL = f"https://github.com/{REPOSITORY}/releases"
API_URL = f"https://api.github.com/repos/{REPOSITORY}/releases"
CHECKSUM_LIMIT = 4096


def check_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.username or parsed.password or
            parsed.port not in (None, 443) or parsed.hostname not in {
                "github.com", "api.github.com", "release-assets.githubusercontent.com",
                "objects.githubusercontent.com"}):
        raise ValueError("Patch downloads must stay on GitHub HTTPS hosts.")


class GitHubRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, limit):
    check_url(url)
    request = Request(url, headers={"User-Agent": "Engineering-Playbook-Repository-Builder",
        "Accept": "application/vnd.github+json" if url.startswith(API_URL) else "application/octet-stream"})
    try:
        with build_opener(GitHubRedirects()).open(request, timeout=30) as response:
            check_url(response.url)
            length = response.headers.get("Content-Length")
            if length and int(length) > limit:
                raise ValueError("GitHub response exceeds the patch download size limit.")
            data = response.read(limit + 1)
            if len(data) > limit:
                raise ValueError("GitHub response exceeds the patch download size limit.")
            return data
    except HTTPError as exc:
        exc.close()
        if exc.code in (403, 429):
            raise ValueError("GitHub denied or rate-limited the request. Try later or use Browse for a local ZIP.") from exc
        raise ValueError(f"GitHub returned HTTP {exc.code}. Try again or use Browse for a local ZIP.") from exc
    except (URLError, OSError) as exc:
        raise ValueError("Couldn't reach GitHub. Check your connection or use Browse for a local ZIP.") from exc


def safe_component(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}", value):
        raise ValueError("Invalid release tag or asset name.")
    valid_path(value)
    return value


@dataclass(frozen=True)
class PublishedPatch:
    tag: str
    name: str
    title: str
    asset_digest: str | None = None

    def __post_init__(self):
        safe_component(self.tag)
        safe_component(self.name)
        if not self.tag.startswith("playbook-patch-") or not self.name.endswith(".zip"):
            raise ValueError("Not a published playbook patch.")
        if self.asset_digest is not None and not re.fullmatch(r"[a-f0-9]{64}", self.asset_digest):
            raise ValueError("Invalid GitHub asset digest.")

    @property
    def key(self):
        return f"{self.tag}/{self.name}"

    @property
    def url(self):
        # Never follow arbitrary asset URLs supplied in release metadata.
        return f"https://github.com/{REPOSITORY}/releases/download/{quote(self.tag)}/{quote(self.name)}"


def available_patches():
    found = {}
    for page in range(1, 6):
        releases = json.loads(fetch(f"{API_URL}?per_page=100&page={page}", 4 * 1024 * 1024))
        if not isinstance(releases, list):
            raise ValueError("GitHub returned an invalid release list.")
        for release in releases:
            if not isinstance(release, dict) or release.get("draft") is not False or release.get("prerelease") is not False:
                continue
            tag = release.get("tag_name")
            if not isinstance(tag, str) or not tag.startswith("playbook-patch-"):
                continue
            assets = release.get("assets", [])
            if not isinstance(assets, list):
                continue
            names = {a.get("name"): a for a in assets if isinstance(a, dict) and
                     isinstance(a.get("name"), str) and a.get("state") == "uploaded"}
            for name, asset in names.items():
                sidecar = names.get(name + ".sha256")
                if not name.endswith(".zip") or sidecar is None:
                    continue
                try:
                    if not (0 < asset["size"] <= MAX_BUNDLE_BYTES and 0 < sidecar["size"] <= CHECKSUM_LIMIT):
                        continue
                    raw_digest = asset.get("digest")
                    if raw_digest is not None and (not isinstance(raw_digest, str) or
                            not re.fullmatch(r"sha256:[a-f0-9]{64}", raw_digest)):
                        continue
                    sha = None if raw_digest is None else raw_digest[7:]
                    title = release.get("name") or tag
                    item = PublishedPatch(tag, name, str(title)[:200], sha)
                except (ValueError, TypeError, KeyError, AttributeError):
                    continue
                found[item.key] = item
        if len(releases) < 100:
            return list(found.values())
    raise ValueError("Release list exceeded 500 entries. Use GitHub Releases and Browse for this update.")


def cache_directory():
    base = Path(os.environ["LOCALAPPDATA"]) if os.environ.get("LOCALAPPDATA") else Path.home() / ".cache"
    return base / "RepositoryBuilder" / "patches"


def checksum_value(data, name):
    match = re.fullmatch(r"([a-fA-F0-9]{64})[ \t]+\*?" + re.escape(name), data.decode("ascii").strip())
    if not match:
        raise ValueError("The release checksum file does not match the selected ZIP filename.")
    return match[1].lower()


def cached_patches():
    root = cache_directory()
    ordinary_path(root)
    if not root.exists():
        return []
    return [p for folder in root.iterdir() if re.fullmatch(r"[a-f0-9]{64}", folder.name) and folder.is_dir()
            for p in folder.glob("*.zip") if p.is_file()]


def cached_checksum(path):
    """The content-addressed cache pins offline preview to the downloaded digest."""
    if path.parent.parent != cache_directory() or not re.fullmatch(r"[a-f0-9]{64}", path.parent.name):
        return None
    ordinary_path(path)
    return path.parent.name


def download_patch(item, repository=None):
    root = cache_directory()
    if not root.is_absolute():
        raise ValueError("The patch cache must be an absolute external path.")
    ordinary_path(root)
    for project in (ROOT, repository):
        if project is not None:
            project = Path(project).resolve()
            if root.is_relative_to(project) or project.is_relative_to(root):
                raise ValueError("The patch cache must be outside the project. Check LOCALAPPDATA.")
    checksum_data = fetch(item.url + ".sha256", CHECKSUM_LIMIT)
    expected = checksum_value(checksum_data, item.name)
    if item.asset_digest and item.asset_digest != expected:
        raise ValueError("GitHub's asset digest and release checksum disagree.")
    folder = root / expected
    target = folder / item.name
    ordinary_path(target)

    def verify_cached():
        ordinary_path(target)
        load_patch(target, expected)
        sidecar = target.with_suffix(".zip.sha256")
        ordinary_path(sidecar)
        if sidecar.stat().st_size > CHECKSUM_LIMIT or checksum_value(sidecar.read_bytes(), item.name) != expected:
            raise ValueError("Cached checksum is invalid. Use Browse or review the cache folder.")
        return target, expected

    if folder.exists():
        return verify_cached()
    data = fetch(item.url, MAX_BUNDLE_BYTES)
    if digest(data) != expected:
        raise ValueError("Downloaded ZIP does not match the release checksum; nothing was cached.")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".download-", dir=root) as temporary:
        staging = Path(temporary)
        staged_zip = staging / item.name
        staged_zip.write_bytes(data)
        load_patch(staged_zip, expected)
        staged_zip.with_suffix(".zip.sha256").write_bytes(checksum_data)
        ordinary_path(folder)
        try:
            # A complete verified pair becomes discoverable in one directory rename.
            staging.rename(folder)
        except OSError:
            if not folder.exists():
                raise
            return verify_cached()
    return target, expected
