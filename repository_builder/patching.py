"""Build and apply reviewed framework snapshots without executing bundle code."""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
import uuid
import zipfile

from .core import ROOT, powershell_executable

MAX_BUNDLE_BYTES = 32 * 1024 * 1024
REQUIRED = {"playbook.json", "VERSION", "SHA256SUMS.txt"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_json(data: bytes):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique)


def valid_path(name: str) -> str:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError(f"Invalid framework path: {name!r}")
    parts = name.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"{p}{n}" for p in ("COM", "LPT") for n in range(1, 10))}
    if any(not p or p in {".", ".."} or p.endswith((".", " ")) or
           p.split(".")[0].upper() in reserved or re.search(r'[<>"|?*\x00-\x1f]', p)
           for p in parts):
        raise ValueError(f"Invalid framework path: {name!r}")
    if parts[0].casefold() in {".git", ".svn", ".hg"}:
        raise ValueError(f"Version-control path is not a framework resource: {name}")
    return name


def ordinary_path(path: Path) -> None:
    # Reject links/junctions before resolving paths, including existing ancestors.
    for item in (path, *path.parents):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Directory links are not supported during patching: {item}")


def destination(root: Path, relative: str) -> Path:
    path = root.joinpath(*PurePosixPath(valid_path(relative)).parts)
    ordinary_path(path)
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a file: {path}")
    return path


def validate_snapshot(files: dict[str, bytes]) -> dict:
    if not REQUIRED <= files.keys():
        raise ValueError("Framework snapshot is missing its manifest, version or checksums.")
    catalog = read_json(files["playbook.json"])
    if catalog.get("install_directory") != "engineering-playbook":
        raise ValueError("Only engineering-playbook framework installations are supported.")
    names = catalog.get("immutable_framework_files")
    if not isinstance(names, list) or any(not isinstance(n, str) for n in names):
        raise ValueError("Invalid framework allowlist.")
    for name in names:
        valid_path(name)
    if len({n.casefold() for n in names}) != len(names) or set(names) != set(files):
        raise ValueError("Framework allowlist must match the snapshot exactly, without duplicate paths.")
    if files["VERSION"].decode("utf-8-sig").strip() != catalog.get("playbook_version"):
        raise ValueError("Framework VERSION and catalog disagree.")
    checksums = {}
    for line in files["SHA256SUMS.txt"].decode("ascii").splitlines():
        expected, name = line.split("  ", 1)
        if name in checksums or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("Invalid or duplicate framework checksum.")
        checksums[name] = expected
    if set(checksums) != set(files) - {"SHA256SUMS.txt"}:
        raise ValueError("Framework checksums do not cover the allowlist exactly.")
    for name, expected in checksums.items():
        if digest(files[name]) != expected:
            raise ValueError(f"Framework checksum mismatch: {name}; refresh checksums before packaging.")
    return catalog


def snapshot(root: Path) -> tuple[dict, dict[str, bytes]]:
    root = root.absolute()
    ordinary_path(root)
    catalog = read_json((root / "playbook.json").read_bytes())
    files = {name: destination(root, name).read_bytes() for name in catalog["immutable_framework_files"]}
    return validate_snapshot(files), files


def build_patch(base: Path, target: Path, output: Path, patch_id: str, summary: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", patch_id):
        raise ValueError("Use a patch ID of at most 80 letters, numbers, hyphens and underscores.")
    if not summary.strip():
        raise ValueError("Provide a release summary explaining the patch.")
    before_catalog, before = snapshot(base)
    after_catalog, after = snapshot(target)
    if before_catalog.get("schema_version") != after_catalog.get("schema_version"):
        raise ValueError("Catalog schema changes require a reviewed migration, not a patch.")
    for field in ("repository_profiles", "capability_packs"):
        if set(before_catalog.get(field, {})) - set(after_catalog.get(field, {})):
            raise ValueError(f"Patch releases cannot remove {field}; use a reviewed migration.")
    if set(before) - set(after):
        raise ValueError("Patch releases cannot remove framework files; use a reviewed migration.")
    if before == after:
        raise ValueError("There are no framework changes to package.")
    manifest = {"schema_version": 1, "patch_id": patch_id, "summary": summary,
                "base_version": before_catalog["playbook_version"],
                "target_version": after_catalog["playbook_version"],
                "before": {n: digest(b) for n, b in before.items()},
                "after": {n: digest(b) for n, b in after.items()}}
    output = output.absolute()
    ordinary_path(output)
    if output.exists() or output.with_suffix(output.suffix + ".sha256").exists():
        raise ValueError("Patch ZIP or checksum sidecar already exists; choose a new output path.")
    for source in (base.resolve(), target.resolve()):
        if output.is_relative_to(source):
            raise ValueError("Write patch artifacts outside the source snapshots.")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation avoids silently replacing a previously reviewed patch.
    with output.open("xb") as stream:
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr("patch.json", json_bytes(manifest))
            for name, data in sorted(after.items()):
                bundle.writestr("payload/" + name, data)
    sha256 = digest(output.read_bytes())
    with output.with_suffix(output.suffix + ".sha256").open("x", encoding="ascii") as stream:
        stream.write(f"{sha256}  {output.name}\n")
    return {"bundle": str(output), "sha256": sha256, "patch_id": patch_id,
            "base_version": manifest["base_version"], "target_version": manifest["target_version"]}


def load_patch(bundle: Path, expected_sha256: str | None = None) -> tuple[dict, dict[str, bytes], str]:
    if bundle.stat().st_size > MAX_BUNDLE_BYTES:
        raise ValueError("Patch ZIP exceeds the 32 MiB limit.")
    data = bundle.read_bytes()
    sha256 = digest(data)
    if expected_sha256 is not None and sha256 != expected_sha256.lower():
        raise ValueError("Patch ZIP checksum does not match the reviewed release.")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if len(entries) > 2000 or sum(e.file_size for e in entries) > MAX_BUNDLE_BYTES:
            raise ValueError("Expanded patch exceeds the resource limit.")
        names = [valid_path(e.filename) for e in entries]
        if len({n.casefold() for n in names}) != len(names):
            raise ValueError("Duplicate ZIP entries are not allowed.")
        if any(stat.S_ISLNK(e.external_attr >> 16) or e.is_dir() for e in entries):
            raise ValueError("ZIP links and directory entries are not allowed.")
        manifest = read_json(archive.read("patch.json"))
        if (type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1 or
            not isinstance(manifest.get("patch_id"), str) or
            not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", manifest["patch_id"]) or
            not isinstance(manifest.get("summary"), str)):
            raise ValueError("Invalid patch manifest.")
        for field in ("before", "after"):
            hashes = manifest.get(field)
            if not isinstance(hashes, dict) or not REQUIRED <= hashes.keys():
                raise ValueError("Patch manifest has an incomplete snapshot.")
            for name, value in hashes.items():
                valid_path(name)
                if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                    raise ValueError("Invalid patch file checksum.")
            if len({n.casefold() for n in hashes}) != len(hashes):
                raise ValueError("Duplicate framework paths in patch manifest.")
        if set(manifest["before"]) - set(manifest["after"]):
            raise ValueError("Patch file removals are not supported.")
        if set(names) != {"patch.json", *("payload/" + n for n in manifest["after"])}:
            raise ValueError("ZIP contents do not match the patch manifest.")
        payload = {n: archive.read("payload/" + n) for n in manifest["after"]}
    if any(digest(payload[n]) != h for n, h in manifest["after"].items()):
        raise ValueError("Patch payload checksum mismatch.")
    catalog = validate_snapshot(payload)
    if catalog["playbook_version"] != manifest.get("target_version"):
        raise ValueError("Patch target version disagrees with its payload.")
    return manifest, payload, sha256


def inspect_patch(bundle: Path, repository: Path, expected_sha256: str | None = None) -> dict:
    manifest, payload, sha256 = load_patch(bundle, expected_sha256)
    repo = repository.absolute()
    ordinary_path(repo)
    framework = repo / "engineering-playbook"
    ordinary_path(framework)
    if not framework.is_dir() or not (framework / "playbook.json").is_file():
        raise ValueError("Choose an existing repository with an installed engineering-playbook.")
    config_file = destination(repo, ".engineering-playbook.json")
    config = read_json(config_file.read_bytes()) if config_file.exists() else None
    if config is not None and not isinstance(config, dict):
        raise ValueError("Project configuration must be a JSON object.")
    changes, conflicts = [], []
    observed = {}
    for name, target_hash in manifest["after"].items():
        path = destination(framework, name)
        current = digest(path.read_bytes()) if path.exists() else None
        observed[name] = current
        if current == target_hash:
            continue
        if current != manifest["before"].get(name):
            conflicts.append(name)
        else:
            changes.append({"path": name, "action": "add" if current is None else "update"})
    catalog = read_json(payload["playbook.json"])
    if config and config.get("project_type", "generic") not in catalog["repository_profiles"]:
        raise ValueError("Patch does not support the repository's selected profile.")
    capabilities = (config or {}).get("capabilities", [])
    if not isinstance(capabilities, list) or any(not isinstance(c, str) for c in capabilities):
        raise ValueError("Project capabilities must be a list of names.")
    templates = list(catalog.get("agent_instruction_templates", []))
    for capability in capabilities:
        if capability not in catalog["capability_packs"]:
            raise ValueError(f"Patch does not support selected capability: {capability}")
        templates += catalog["capability_packs"][capability].get("agent_instruction_templates", [])
    blocks = "\n".join(payload[valid_path(name)].decode("utf-8-sig").strip() for name in templates)
    agents_path = destination(repo, "AGENTS.md")
    agents = agents_path.read_text(encoding="utf-8-sig") if agents_path.exists() else ""
    review = []
    if any(payload[name].decode("utf-8-sig").strip() not in agents for name in templates):
        review.append("AGENTS.md: preserve local rules and merge the supplied governance blocks manually.")
    changed_templates = [n for n, h in manifest["after"].items()
                         if n.startswith("templates/") and h != manifest["before"].get(n)]
    if changed_templates:
        review.append("Project documents are preserved. Review changed templates: " + ", ".join(changed_templates))
    if config is None:
        review.append("No .engineering-playbook.json exists; project configuration will not be created.")
    receipt = {"patch_id": manifest["patch_id"], "sha256": sha256}
    updated_config = None if config is None else {**config, "playbook_version": manifest["target_version"], "last_playbook_patch": receipt}
    config_change = config is not None and config != updated_config
    return {"patch_id": manifest["patch_id"], "summary": manifest["summary"], "sha256": sha256,
            "base_version": manifest.get("base_version"), "target_version": manifest["target_version"],
            "repository": str(repo), "changes": changes, "conflicts": conflicts,
            "review_required": review, "configuration_update": config_change,
            "can_apply": not conflicts, "already_applied": not changes and not conflicts and not config_change,
            "observed": observed, "agent_blocks": blocks, "updated_config": updated_config,
            "config_sha256": digest(config_file.read_bytes()) if config_file.exists() else None}


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".playbook-patch-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def apply_patch(bundle: Path, repository: Path, expected_sha256: str) -> dict:
    if not expected_sha256:
        raise ValueError("Apply requires the SHA-256 of the reviewed patch ZIP.")
    report = inspect_patch(bundle, repository, expected_sha256)
    if report["conflicts"]:
        raise ValueError("Local edits or incompatible baseline; no files changed: " + ", ".join(report["conflicts"]))
    if report["already_applied"]:
        return {**report, "status": "already_applied", "backup": None}
    _, payload, _ = load_patch(bundle, expected_sha256)
    repo = Path(report["repository"])
    writes = {"engineering-playbook/" + item["path"]: payload[item["path"]] for item in report["changes"]}
    if report["configuration_update"]:
        writes[".engineering-playbook.json"] = json_bytes(report["updated_config"])
    task = "patch-" + uuid.uuid4().hex
    result = subprocess.run([powershell_executable(), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "RemoteSigned",
                             "-File", str(ROOT / "scripts/initialize_agent_workspace.ps1"),
                             "-RepositoryPath", str(repo), "-TaskId", task],
                            capture_output=True, text=True, encoding="utf-8", check=True, timeout=30,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    backup = Path(result.stdout.strip()) / "backup"
    backup.mkdir()
    originals = {}
    for name in writes:
        path = destination(repo, name)
        originals[name] = path.read_bytes() if path.exists() else None
        if originals[name] is not None:
            atomic_write(destination(backup, name), originals[name])
    journal = {"repository": str(repo), "patch_id": report["patch_id"], "sha256": report["sha256"],
               "status": "prepared", "files": {n: {"before": digest(b) if b is not None else None,
               "after": digest(writes[n])} for n, b in originals.items()}}
    atomic_write(backup / "transaction.json", json_bytes(journal))
    atomic_write(backup / "AGENTS.blocks.md", report["agent_blocks"].encode("utf-8"))
    # Recheck every baseline file and configuration after taking backups, before any replacement.
    current = inspect_patch(bundle, repo, expected_sha256)
    if current["observed"] != report["observed"] or current["config_sha256"] != report["config_sha256"]:
        raise ValueError(f"Repository changed after preview; no files replaced. Backup: {backup}")
    completed = []
    try:
        for name, content in writes.items():
            path = destination(repo, name)
            now = path.read_bytes() if path.exists() else None
            if now != originals[name]:
                raise ValueError(f"File changed while applying patch: {name}")
            atomic_write(path, content)
            completed.append(name)
        verified = inspect_patch(bundle, repo, expected_sha256)
        if not verified["already_applied"]:
            raise ValueError("Post-apply framework verification failed.")
        journal["status"] = "applied"
        atomic_write(backup / "transaction.json", json_bytes(journal))
    except Exception as exc:
        failed = []
        for name in reversed(completed):
            try:
                path = destination(repo, name)
                if path.read_bytes() != writes[name]:
                    raise ValueError("Concurrent modification; retained for manual recovery")
                if originals[name] is None:
                    path.unlink()
                else:
                    atomic_write(path, originals[name])
            except Exception:
                failed.append(name)
        journal["status"] = "recovery_required" if failed else "rolled_back"
        journal["recovery_required"] = failed
        atomic_write(backup / "transaction.json", json_bytes(journal))
        raise RuntimeError(f"Patch failed ({journal['status']}); backups: {backup}. {exc}") from exc
    return {**verified, "status": "applied", "backup": str(backup)}
