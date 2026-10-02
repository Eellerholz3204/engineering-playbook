"""Refresh checksums for the exact framework files listed in playbook.json."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "playbook.json").read_text(encoding="utf-8-sig"))
# A small separately versioned bundle supports additive adoption in older repos.
assets = ["GOVERNANCE_CONTEXT.md", "templates/agents.md", "templates/metis_agents.md",
          "scripts/verify_governance_context.py"]
pins = {name: hashlib.sha256((root / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for name in assets}
(root / "governance-context.json").write_text(json.dumps({"version": 1, "sha256": pins}, indent=2) + "\n", encoding="utf-8", newline="\n")
lines = []
for name in sorted(manifest["immutable_framework_files"], key=str.lower):
    path = (root / name).resolve()
    if name == "SHA256SUMS.txt":
        continue
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Invalid framework path: {name}")
    lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}\n")
(root / "SHA256SUMS.txt").write_text("".join(lines), encoding="ascii", newline="\n")
print(f"Updated {len(lines)} framework checksums.")
