"""Shared entry point for source and standalone builds."""

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import tempfile
import traceback

import flet as ft
import flet_desktop

from .app import RepositoryBuilder, main
from .core import ROOT, CreationPlan, create_repository, load_catalog
from .runtime import configure_desktop
from .version import __version__


def verify_resources() -> dict:
    catalog = load_catalog()
    for name in catalog["immutable_framework_files"]:
        if not (ROOT / name).is_file():
            raise RuntimeError(f"Missing bundled playbook file: {name}")
    for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Bundled playbook checksum failed: {name}")
    return catalog


def self_test(report: Path) -> None:
    catalog = verify_resources()
    with tempfile.TemporaryDirectory(prefix="repository-builder-check-") as temporary:
        plan = CreationPlan("portable-check", str(Path(temporary) / "portable-check"),
            project_type="dbt-python", capabilities=("ai-governance", "service-operations"),
            initialize_git=False, playbook_version=catalog["playbook_version"])
        output = []
        code = create_repository(plan, output.append)
        if code:
            raise RuntimeError("\n".join(output))
        target = Path(plan.repository_path)
        for relative in ("dbt_project.yml", "pyproject.toml", "docs/ai_governance.md", ".engineering-playbook.json"):
            if not (target / relative).is_file():
                raise RuntimeError(f"Creation did not produce {relative}")
    report.write_text(json.dumps({"success": True, "app_version": __version__,
        "playbook_version": catalog["playbook_version"], "resource_root": str(ROOT)}, indent=2), encoding="utf-8")


def run() -> None:
    parser = argparse.ArgumentParser(description="Engineering Playbook Repository Builder")
    parser.add_argument("--self-test", type=Path, metavar="REPORT_JSON")
    parser.add_argument("--smoke-test", type=Path, metavar="OUTPUT_DIRECTORY")
    args = parser.parse_args()
    configure_desktop()
    if args.self_test:
        self_test(args.self_test)
        return
    if not args.smoke_test:
        ft.run(main)
        return

    destination = args.smoke_test.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    clients = []
    original_open = flet_desktop.open_flet_view_async

    async def tracked_open(*args, **kwargs):
        process, pid_file = await original_open(*args, **kwargs)
        clients.append(process)
        return process, pid_file

    async def smoke(page):
        try:
            verify_resources()
            with tempfile.TemporaryDirectory(prefix="repository-builder-ui-") as temporary:
                app = RepositoryBuilder(page)
                page.controls.clear()
                capture = ft.Screenshot(content=app.content, expand=True)
                page.add(capture)
                await asyncio.sleep(1)
                (destination / "project.png").write_bytes(await capture.capture(pixel_ratio=1.0, delay=500))
                app.name.value = "packaged-project"
                app.parent.value = temporary
                app.git.value = False
                await app.advance(None)
                app.choose_profile("dbt-python")
                app.toggle_capability("ai-governance", True)
                await app.advance(None)
                await app.advance(None)
                if not app.completed:
                    raise RuntimeError(app.error.value)
                (destination / "complete.png").write_bytes(await capture.capture(pixel_ratio=1.0, delay=500))
            (destination / "result.json").write_text(json.dumps({"success": True, "app_version": __version__}), encoding="utf-8")
        except Exception:
            (destination / "result.json").write_text(json.dumps({"success": False, "error": traceback.format_exc()}), encoding="utf-8")
        finally:
            for client in clients:
                if client.returncode is None:
                    client.terminate()

    flet_desktop.open_flet_view_async = tracked_open
    ft.run(smoke, view=ft.AppView.FLET_APP_HIDDEN)
    result_path = destination / "result.json"
    if not result_path.exists() or not json.loads(result_path.read_text())["success"]:
        raise RuntimeError(f"Desktop verification failed; see {result_path}")
