"""Build, preview, or apply an offline Engineering Playbook patch ZIP."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from repository_builder.patching import apply_patch, build_patch, inspect_patch


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Create a ZIP and SHA-256 sidecar; does not publish")
    build.add_argument("--base", type=Path, required=True)
    build.add_argument("--target", type=Path, default=Path(__file__).resolve().parents[1])
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--patch-id", required=True)
    build.add_argument("--summary", required=True)
    for name in ("preview", "apply"):
        command = commands.add_parser(name)
        command.add_argument("--bundle", type=Path, required=True)
        command.add_argument("--repo", type=Path, required=True)
        command.add_argument("--sha256", required=name == "apply")
    args = parser.parse_args()
    try:
        if args.command == "build":
            report = build_patch(args.base, args.target, args.output, args.patch_id, args.summary)
        elif args.command == "preview":
            report = inspect_patch(args.bundle, args.repo, args.sha256)
        else:
            report = apply_patch(args.bundle, args.repo, args.sha256)
        public = {k: v for k, v in report.items() if k not in {"observed", "updated_config", "config_sha256", "agent_blocks"}}
        print(json.dumps(public, indent=2))
        return 2 if report.get("conflicts") else 0
    except Exception as exc:
        print(f"Patch error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
