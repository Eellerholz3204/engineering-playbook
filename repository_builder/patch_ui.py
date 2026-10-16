"""Preview/apply surface for an existing repository; patch policy lives in patching."""

import asyncio
from pathlib import Path

import flet as ft

from .patching import apply_patch, inspect_patch


class PatchView:
    def __init__(self, builder):
        self.builder = builder
        self.report = None
        self.reviewed_inputs = None
        self.completed = False
        self.repository = ft.TextField(label="Existing repository folder", on_change=self.changed,
                                       **builder.field_style())
        self.bundle = ft.TextField(label="Patch ZIP", on_change=self.changed, **builder.field_style())
        self.checksum = ft.TextField(label="Release SHA-256 (optional for preview)", on_change=self.changed,
                                    **builder.field_style())
        self.pick_repository = ft.TextButton("Choose repository", on_click=self.choose_repository)
        self.pick_bundle = ft.TextButton("Choose patch ZIP", on_click=self.choose_bundle)

    def values(self):
        return (self.repository.value or "", self.bundle.value or "", self.checksum.value or "")

    def changed(self, _=None):
        self.report = self.reviewed_inputs = None
        self.completed = False
        self.show()

    async def choose_repository(self, _):
        try:
            chosen = await self.builder.picker.get_directory_path(dialog_title="Choose an existing repository")
            if chosen:
                self.repository.value = chosen
                self.changed()
        except Exception as exc:
            self.builder.show_error(str(exc))

    async def choose_bundle(self, _):
        try:
            files = await self.builder.picker.pick_files(dialog_title="Choose a released patch ZIP",
                file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["zip"])
            if files:
                self.bundle.value = files[0].path
                self.changed()
        except Exception as exc:
            self.builder.show_error(str(exc))

    def close(self, _):
        if self.builder.busy:
            return
        self.builder.back.on_click = self.builder.previous
        self.builder.next.disabled = False
        self.builder.render()

    def show(self):
        app = self.builder
        app.back.visible = True
        app.back.on_click = self.close
        app.import_button.visible = False
        app.error.visible = False
        ready = self.report and self.report["can_apply"] and not self.report["already_applied"]
        app.next.content = "Patch applied" if self.completed else ("Apply patch" if ready else "Preview patch")
        app.next.on_click = self.apply if ready else self.preview
        app.next.disabled = self.completed or app.busy
        app.body.controls = [app.heading("Update an existing repository.",
            "Preview a playbook patch before applying it to this project."), app.card([
                self.repository, self.pick_repository, self.bundle, self.pick_bundle, self.checksum,
                ft.Text("Use a trusted release and compare its published checksum. Preview does not change files.", size=12),
                ft.Text("Project documents and AGENTS.md are preserved. Local framework edits block the patch; backups are stored outside the project.", size=12),
            ])]
        if self.report:
            report = self.report
            details = [ft.Text(report["patch_id"], size=18, weight=ft.FontWeight.W_600),
                       ft.Text(report["summary"]),
                       ft.Text(f"Playbook {report['base_version']} → {report['target_version']}", size=13),
                       ft.Text("ZIP SHA-256: " + report["sha256"], size=11, selectable=True)]
            if self.completed:
                details.append(ft.Text("Framework patch applied. Complete any instruction/document review listed below."))
            elif report["already_applied"]:
                details.append(ft.Text("The framework is already at this patch's target state."))
            details += [ft.Text(f"{item['action'].upper()}  {item['path']}", size=12) for item in report["changes"]]
            details += [ft.Text("CONFLICT  " + name, size=12, color="#B42318") for name in report["conflicts"]]
            if report["configuration_update"]:
                details.append(ft.Text("UPDATE  Installed version and last-patch receipt in .engineering-playbook.json", size=12))
            details += [ft.Text("REVIEW  " + item, size=12) for item in report["review_required"]]
            if report.get("backup"):
                details.append(ft.Text("Backups and suggested AGENTS.md blocks: " + report["backup"], size=12, selectable=True))
            app.body.controls.append(app.card(details))
        app.page.update()

    def busy(self, value):
        app = self.builder
        app.busy = value
        app.page.window.prevent_close = value
        app.back.disabled = app.next.disabled = value
        for control in (self.repository, self.bundle, self.checksum, self.pick_repository, self.pick_bundle):
            control.disabled = value
        app.page.update()

    async def preview(self, _):
        if self.builder.busy:
            return
        self.busy(True)
        try:
            values = self.values()
            repo, bundle, checksum = (v.strip() for v in values)
            if not repo or not bundle:
                raise ValueError("Choose the existing repository and patch ZIP.")
            self.report = await asyncio.to_thread(inspect_patch, Path(bundle), Path(repo), checksum or None)
            self.reviewed_inputs = values
            self.show()
        except Exception as exc:
            self.report = self.reviewed_inputs = None
            self.show()
            self.builder.show_error(str(exc))
        finally:
            self.busy(False)

    async def apply(self, _):
        if self.builder.busy:
            return
        if not self.report or not self.report["can_apply"] or self.reviewed_inputs != self.values():
            self.changed()
            self.builder.show_error("Preview the selected repository and patch before applying.")
            return
        self.busy(True)
        try:
            repo, bundle, _ = (v.strip() for v in self.reviewed_inputs)
            self.report = await asyncio.to_thread(apply_patch, Path(bundle), Path(repo), self.report["sha256"])
            self.completed = True
            self.show()
        except Exception as exc:
            self.report = self.reviewed_inputs = None
            self.show()
            self.builder.show_error(str(exc))
        finally:
            self.busy(False)
            self.builder.next.disabled = self.completed
            self.builder.page.update()
