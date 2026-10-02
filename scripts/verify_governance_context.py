"""Read-only structural governance checks; no claim of semantic compliance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CORE_DOCS = (
    "product_vision.md",
    "domain_map.md",
    "architecture_decisions.md",
    "project_status.md",
    "roadmap.md",
    "milestone_details.md",
    "releases/unreleased.md",
)
ASSETS = (
    "GOVERNANCE_CONTEXT.md",
    "templates/agents.md",
    "templates/metis_agents.md",
    "scripts/verify_governance_context.py",
)


def check(
    repo: Path,
    *,
    metis: bool = False,
    metis_root: Path | None = None,
    source: Path | None = None,
    local_only: bool = False,
) -> list[str]:
    # Saved capability selection and the installed marker both retain Metis checks
    # in generic CI invocations. An explicit --metis supports older installations.
    config_path = repo / ".engineering-playbook.json"
    if config_path.is_file():
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        metis = metis or "metis-governance" in config.get("capabilities", [])
    if (repo / "AGENTS.md").is_file():
        metis = metis or "BEGIN METIS GOVERNANCE CONTEXT" in (repo / "AGENTS.md").read_text(
            encoding="utf-8-sig"
        )
    errors = []
    framework = repo / "engineering-playbook"
    required = [
        "AGENTS.md",
        "engineering-playbook/GOVERNANCE_CONTEXT.md",
        "engineering-playbook/DEVELOPMENT_WORKFLOW.md",
        "engineering-playbook/REPOSITORY_CONTRACT.md",
        "engineering-playbook/DOCUMENTATION_REQUIREMENTS.md",
    ]
    required += ["docs/" + name for name in CORE_DOCS]
    for name in required:
        if not (repo / name).is_file():
            errors.append("Missing required context: " + name)
    agents = (
        (repo / "AGENTS.md").read_text(encoding="utf-8-sig")
        if (repo / "AGENTS.md").is_file()
        else ""
    )
    templates = ["agents.md"] + (["metis_agents.md"] if metis else [])
    for name in templates:
        template = framework / "templates" / name
        if not template.is_file():
            errors.append("Missing instruction template: " + name)
        elif template.read_text(encoding="utf-8-sig").strip() not in agents:
            errors.append("Missing or modified governance block: " + name)
    pin_path = framework / "governance-context.json"
    if not pin_path.is_file():
        errors.append("Missing governance asset manifest")
    else:
        try:
            pins = json.loads(pin_path.read_text(encoding="utf-8-sig"))
            if pins["version"] != 1 or set(pins["sha256"]) != set(ASSETS):
                raise ValueError("invalid manifest")
            for name in ASSETS:
                path = framework / name
                if (
                    not path.is_file()
                    or hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
                    != pins["sha256"][name]
                ):
                    errors.append("Governance asset hash mismatch: " + name)
        except (ValueError, KeyError, TypeError):
            errors.append("Invalid governance asset manifest")
    if metis and not local_only:
        central = metis_root or repo.parent / "metis-engineering-playbook"
        for name in (
            *CORE_DOCS,
            "contract_agent_workflow.md",
            "data_platform_architecture.md",
            "reference_data.md",
        ):
            if not (central / "docs" / name).is_file():
                errors.append("Missing Metis authority: " + str(central / "docs" / name))
    if source:
        for name in ASSETS:
            installed, expected = framework / name, source / name
            if not installed.is_file() or not expected.is_file():
                errors.append("Missing governance asset for source comparison: " + name)
            elif installed.read_text(encoding="utf-8-sig") != expected.read_text(
                encoding="utf-8-sig"
            ):
                errors.append("Governance asset differs from selected source: " + name)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--metis", action="store_true")
    parser.add_argument("--metis-root", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Skip external checkout availability in isolated CI",
    )
    args = parser.parse_args()
    errors = check(
        args.repo.resolve(),
        metis=args.metis,
        metis_root=args.metis_root,
        source=args.source,
        local_only=args.local_only,
    )
    for error in errors:
        print(error)
    if not errors:
        print(
            "Governance structure verified; semantic review remains required."
        )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
