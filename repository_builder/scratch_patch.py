"""Fixed, additive scratch-workspace migration; never replace existing instructions."""

from pathlib import Path
import re
import zipfile

from .patching import destination, digest, json_bytes, ordinary_path, read_json, snapshot

FEATURE = "agent-scratch-workspace"
SUPPORTED = {"3.0.1": 1, "3.2.0": 2, "3.2.1": 2, "3.3.0": 2, "3.3.1": 2}
HELPER = "engineering-playbook/scripts/initialize_agent_workspace.ps1"
POLICY = "engineering-playbook/features/agent-scratch-workspace/POLICY.md"
RECEIPT = "engineering-playbook/features/agent-scratch-workspace/feature.json"
BEGIN = "<!-- engineering-playbook:agent-scratch-workspace:v1:begin -->"
END = "<!-- engineering-playbook:agent-scratch-workspace:v1:end -->"
MARKER = "<!-- engineering-playbook:agent-scratch-workspace:"
BLOCK = f"""{BEGIN}
## Agent scratch workspace

Read `engineering-playbook/features/agent-scratch-workspace/POLICY.md` before
creating task diagnostics, experiments or temporary tooling. Resolve external
scratch with `engineering-playbook/scripts/initialize_agent_workspace.ps1`.
Keep temporary work out of project source, tests, commits and PRs. Promote only
artifacts that protect maintained project behavior; reusable tooling fixes belong
to the tooling owner. Do not remove existing tests merely because agents wrote them.

Existing project and organizational instructions remain in force. This section
does not grant new authority or supersede custom rules. If instructions conflict,
report the conflict and obtain explicit reconciliation before dependent work.
{END}
"""
PATHS = {HELPER, POLICY, "AGENTS.md", RECEIPT}


def normalized(data: bytes) -> str:
    """Only BOM and newline equivalence; never normalize whitespace or semantics."""
    return data.decode("utf-8-sig").replace("\r\n", "\n")


def receipt(payload: dict[str, bytes]) -> bytes:
    return json_bytes({"schema_version": 1, "feature": FEATURE, "feature_version": 1,
                      "hash_format": "utf8-no-bom-lf",
                      "components": {n: digest(normalized(payload[n]).encode("utf-8"))
                                     for n in sorted(PATHS - {RECEIPT})},
                      "agents_component": "managed block only, not the whole AGENTS.md"})


def validate(manifest: dict, payload: dict[str, bytes]) -> None:
    if (manifest.get("kind") != FEATURE or type(manifest.get("feature_version")) is not int
            or manifest["feature_version"] != 1 or manifest.get("supported_versions") != SUPPORTED
            or set(payload) != PATHS):
        raise ValueError("Unsupported scratch migration recipe or destinations.")
    if payload["AGENTS.md"] != BLOCK.encode("utf-8"):
        raise ValueError("Scratch migration must use the additive v1 instruction block.")
    if not normalized(payload[HELPER]).strip() or not normalized(payload[POLICY]).strip():
        raise ValueError("Scratch migration is missing its helper or policy.")
    if payload[RECEIPT] != receipt(payload):
        raise ValueError("Scratch feature receipt does not match its components.")


def build(target: Path, output: Path, patch_id: str, summary: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", patch_id) or not summary.strip():
        raise ValueError("Provide a valid patch ID and nonempty summary.")
    catalog, files = snapshot(target)
    governance = normalized(files["GOVERNANCE_CONTEXT.md"])
    start = governance.index("## Agent scratch space and project ownership\n")
    end = governance.find("\n## ", start + 1)
    policy = governance[start:end if end != -1 else None]
    # Ship only the existing canonical scratch policy, not unrelated framework rules.
    policy = ("# Agent scratch workspace feature v1\n\n"
              "This additive feature leaves the installed framework version and custom\n"
              "instructions unchanged. Existing project/organizational rules remain in force;\n"
              "stop for explicit reconciliation if they conflict with this policy.\n\n" + policy)
    payload = {HELPER: files["scripts/initialize_agent_workspace.ps1"],
               POLICY: policy.encode("utf-8"), "AGENTS.md": BLOCK.encode("utf-8")}
    payload[RECEIPT] = receipt(payload)
    manifest = {"schema_version": 2, "kind": FEATURE, "feature_version": 1,
                "patch_id": patch_id, "summary": summary,
                "source_version": catalog["playbook_version"], "supported_versions": SUPPORTED,
                "after": {n: digest(b) for n, b in payload.items()}}
    validate(manifest, payload)
    output = output.absolute()
    ordinary_path(output)
    if output.is_relative_to(target.resolve()):
        raise ValueError("Write patch artifacts outside the source snapshot.")
    sidecar = output.with_suffix(output.suffix + ".sha256")
    ordinary_path(sidecar)
    if output.exists() or sidecar.exists():
        raise ValueError("Patch ZIP or checksum sidecar already exists; choose a new output path.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("patch.json", json_bytes(manifest))
            for name, data in sorted(payload.items()):
                archive.writestr("payload/" + name, data)
    sha = digest(output.read_bytes())
    with sidecar.open("x", encoding="ascii") as stream:
        stream.write(f"{sha}  {output.name}\n")
    return {"bundle": str(output), "sha256": sha, "patch_id": patch_id,
            "kind": FEATURE, "supported_versions": list(SUPPORTED)}


def append_block(original: bytes) -> bytes:
    text = normalized(original)
    # Do not append inside unfinished Markdown or mistake a quoted example for
    # an adopted instruction section. This is structural, not semantic approval.
    fence = None
    comment = False
    for line in text.splitlines():
        if MARKER in line and (fence or comment):
            raise ValueError("Scratch instruction markers are inside a code fence or comment; reconcile them manually.")
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match and not comment:
            token, suffix = match.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip():
                fence = None
        elif fence is None:
            for token in re.findall(r"<!--|-->", line):
                comment = token == "<!--"
    if fence or comment:
        raise ValueError("AGENTS.md ends inside a code fence or comment; close it explicitly before appending instructions.")
    # A damaged/edited block is not an invitation to replace custom instructions.
    if MARKER in text:
        if (text.count(MARKER) != 2 or text.count(BLOCK.rstrip("\n")) != 1
                or not re.search(r"(?m)^" + re.escape(BEGIN) + r"$", text)
                or not re.search(r"(?m)^" + re.escape(END) + r"$", text)):
            raise ValueError("The existing scratch instruction block was modified or is incomplete; reconcile it manually.")
        return original
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    # Preserve every original byte, including BOM, mixed line endings and no final newline.
    return original + (newline * 2 if original else b"") + BLOCK.encode().replace(b"\n", newline)


def inspect(manifest: dict, payload: dict[str, bytes], sha: str, repo: Path) -> dict:
    observed, changes, conflicts, reasons, writes = {}, [], [], {}, {}

    def read(name):
        path = destination(repo, name)
        data = path.read_bytes() if path.exists() else None
        observed[name] = digest(data) if data is not None else None
        return data

    catalog_data = read("engineering-playbook/playbook.json")
    catalog = read_json(catalog_data) if catalog_data else {}
    version_data = read("engineering-playbook/VERSION")
    version = catalog.get("playbook_version")
    if (catalog.get("install_directory") != "engineering-playbook"
            or not isinstance(version, str) or version not in SUPPORTED
            or type(catalog.get("schema_version")) is not int
            or catalog["schema_version"] != SUPPORTED[version]
            or version_data is None or normalized(version_data).strip() != version):
        conflicts.append("engineering-playbook/playbook.json")
        reasons[conflicts[-1]] = "Unsupported catalog/version pair or VERSION disagreement; no full framework upgrade is attempted."
    for name in sorted(PATHS):
        try:
            current = read(name)
            if name == "AGENTS.md":
                desired = append_block(current or b"")
            elif current is None:
                desired = payload[name]
            elif normalized(current) == normalized(payload[name]):
                desired = current  # Reuse equivalent bytes; do not rewrite encoding.
            else:
                raise ValueError("Existing feature file differs; preserve it and reconcile explicitly.")
            if desired != current:
                writes[name] = desired
                changes.append({"path": name, "action": "append" if name == "AGENTS.md" and current is not None else "add"})
        except (ValueError, UnicodeError) as exc:
            conflicts.append(name)
            reasons[name] = str(exc)
    return {"kind": FEATURE, "patch_id": manifest["patch_id"], "summary": manifest["summary"],
            "sha256": sha, "base_version": version, "target_version": version,
            "feature_version": 1, "repository": str(repo), "changes": changes,
            "conflicts": conflicts, "conflict_reasons": reasons, "can_apply": not conflicts,
            "already_applied": not changes and not conflicts, "configuration_update": False,
            "observed": observed, "config_sha256": None, "updated_config": None,
            "agent_blocks": BLOCK, "_writes": writes,
            "review_required": [
                "Review the appended AGENTS.md section below against your custom rules. Existing text is retained byte-for-byte; conflicting instructions require explicit reconciliation.",
                "This installs scratch support only. VERSION, catalogs, checksums, project configuration, workflows, source, tests and project documents remain unchanged.",
                "Use the installed helper for each task. No tests or existing artifacts are removed and no consumer Git actions run."]}
