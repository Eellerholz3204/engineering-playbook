"""Render and exercise the desktop app in a temporary project.

Run from the playbook root: python -m tests.render_builder
Screenshots are written to .builder-qa; no user project is created.
"""

import asyncio
from pathlib import Path
import tempfile

import flet as ft
import flet_desktop

from repository_builder.app import RepositoryBuilder
from repository_builder.core import ROOT

desktop_processes = []
open_desktop = flet_desktop.open_flet_view_async


async def tracked_desktop(*args, **kwargs):
    process, pid_file = await open_desktop(*args, **kwargs)
    desktop_processes.append(process)
    return process, pid_file


async def main(page: ft.Page):
    destination = ROOT / ".builder-qa"
    destination.mkdir(exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="playbook-ui-") as temporary:
            app = RepositoryBuilder(page)
            page.controls.clear()
            screenshot = ft.Screenshot(content=app.content, expand=True)
            page.add(screenshot)
            await asyncio.sleep(1)
            (destination / "01-project.png").write_bytes(await screenshot.capture(pixel_ratio=1.0, delay=500))
            app.name.value = "example-data-product"
            app.parent.value = temporary
            app.git.value = False
            await app.advance(None)
            app.choose_profile("dbt-python")
            app.toggle_capability("service-operations", True)
            app.toggle_capability("ai-governance", True)
            (destination / "02-catalog.png").write_bytes(await screenshot.capture(pixel_ratio=1.0, delay=500))
            await app.body.scroll_to(offset=-1)
            (destination / "03-capabilities.png").write_bytes(await screenshot.capture(pixel_ratio=1.0, delay=500))
            await app.advance(None)
            await app.body.scroll_to(offset=0)
            (destination / "04-review.png").write_bytes(await screenshot.capture(pixel_ratio=1.0, delay=500))
            await app.advance(None)
            assert app.completed, app.error.value
            assert (Path(temporary) / "example-data-product" / "dbt_project.yml").exists()
            (destination / "05-complete.png").write_bytes(await screenshot.capture(pixel_ratio=1.0, delay=500))
            (destination / "result.txt").write_text("PASS: desktop screens rendered and app creation completed.", encoding="utf-8")
    except Exception:
        import traceback
        (destination / "result.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
    finally:
        try:
            await asyncio.wait_for(page.window.destroy(), timeout=2)
        except (TimeoutError, RuntimeError):
            pass
        finally:
            for process in desktop_processes:
                if process.returncode is None:
                    process.terminate()


if __name__ == "__main__":
    flet_desktop.open_flet_view_async = tracked_desktop
    ft.run(main, view=ft.AppView.FLET_APP_HIDDEN)
