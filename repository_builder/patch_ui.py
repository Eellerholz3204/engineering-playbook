"""Preview/apply surface for an existing repository; patch policy lives in patching."""

import asyncio
import json
from pathlib import Path
import zipfile

import flet as ft

from .patching import apply_patch, inspect_patch
from .core import ROOT


def children(folder):
    """Bound discovery to immediate children; unavailable folders are optional."""
    try:
        return list(folder.iterdir())
    except OSError:
        return []


def patch_label(path):
    """Read only bounded display metadata. Preview remains the validation gate."""
    try:
        if path.suffix.lower() != ".zip" or path.stat().st_size > 32 * 1024 * 1024:
            return None
        with zipfile.ZipFile(path) as archive:
            entry = archive.getinfo("patch.json")
            if entry.file_size > 1024 * 1024:
                return None
            data = json.loads(archive.read(entry))
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            return None
        if not all(isinstance(data.get(k), str) and data[k] for k in
                   ("patch_id", "base_version", "target_version")):
            return None
        return f"{data['patch_id']} ({data['base_version']} → {data['target_version']}) · {path.name}"
    except (OSError, ValueError, KeyError, RuntimeError, zipfile.BadZipFile, NotImplementedError):
        return None


class PatchView:
    def __init__(self, builder):
        self.builder = builder
        self.report = None
        self.reviewed_inputs = None
        self.completed = False
        self.repository = ft.Dropdown(label="Existing repository", on_select=self.changed,
            expand=True, expanded_insets=0,
            editable=True, enable_filter=True, on_text_change=self.search_changed,
            enable_search=True, menu_height=300, hint_text="Select a repository or browse…",
            **builder.field_style())
        self.bundle = ft.Dropdown(label="Available patch", on_select=self.bundle_changed,
            expand=True, expanded_insets=0,
            editable=True, enable_filter=True, on_text_change=self.search_changed,
            enable_search=True, menu_height=300, hint_text="Select a patch or browse…",
            **builder.field_style())
        self.repository_path = ft.Text(size=12, selectable=True)
        self.bundle_path = ft.Text(size=12, selectable=True)
        self.checksum = ft.TextField(label="Release SHA-256 (optional for preview)", on_change=self.changed,
                                    **builder.field_style())
        self.pick_repository = ft.TextButton("Browse repositories…", on_click=self.choose_repository)
        self.pick_bundle = ft.TextButton("Browse patch ZIPs…", on_click=self.choose_bundle)
        self.refresh_button = ft.TextButton("Refresh lists", icon=ft.Icons.REFRESH, on_click=self.refresh)
        # Session-only choices: no project files or machine-specific paths are saved.
        if not hasattr(builder, "patch_choices"):
            builder.patch_choices = {"repositories": set(), "bundles": set()}
        self.choices = builder.patch_choices
        self.populate()
        # Keep the input subtree stable when filtering so typing retains focus.
        self.title = builder.heading("Update an existing repository.",
            "Preview a playbook patch before applying it to this project.")
        self.inputs = builder.card([
            ft.Row([self.repository, self.pick_repository]), self.repository_path,
            ft.Row([self.bundle, self.pick_bundle]), self.bundle_path, self.refresh_button,
            ft.Text("Lists include installed projects in your parent folder and ~/source/repos; patches in Downloads, Builder dist, and folders browsed this session.", size=12),
            self.checksum,
            ft.Text("Use a trusted release and compare its published checksum. Preview does not change files.", size=12),
            ft.Text("Project documents and AGENTS.md are preserved. Local framework edits block the patch; backups are stored outside the project.", size=12),
        ])

    def discovery_locations(self):
        parents = {Path.home() / "source" / "repos"}
        if self.builder.parent.value:
            parents.add(Path(self.builder.parent.value).expanduser().absolute())
        patches = {Path.home() / "Downloads", ROOT / "dist"}
        patches.update(Path(p).parent for p in self.choices["bundles"])
        return parents, patches

    def populate(self):
        parents, patches = self.discovery_locations()
        repositories = {p for folder in parents for p in children(folder)
                        if (p / "engineering-playbook" / "playbook.json").is_file()}
        repositories.update(Path(p) for p in self.choices["repositories"])
        bundles = {p for folder in patches for p in children(folder) if p.suffix.lower() == ".zip"}
        bundles.update(Path(p) for p in self.choices["bundles"])
        # Preserve explicit selections so refresh never silently switches targets.
        if self.repository.value:
            repositories.add(Path(self.repository.value))
        if self.bundle.value:
            bundles.add(Path(self.bundle.value))
        self.repository.options = [ft.DropdownOption(key=str(p), text=f"{p.name} · {p.parent}")
            for p in sorted(repositories, key=lambda p: str(p).casefold())]
        self.bundle.options = []
        for path in sorted(bundles, key=lambda p: str(p).casefold()):
            label = patch_label(path)
            if label or str(path) in self.choices["bundles"] or str(path) == self.bundle.value:
                self.bundle.options.append(ft.DropdownOption(key=str(path),
                    text=label or path.name, tooltip=str(path)))

    def refresh(self, _=None):
        if self.builder.busy:
            return
        self.populate()
        self.changed()

    def bundle_changed(self, _=None):
        self.checksum.value = ""
        self.changed()

    def search_changed(self, event):
        control = event.control
        selected = next((o for o in control.options if o.key == control.value), None)
        if selected is None or control.text != selected.text:
            control.value = None
            if control is self.bundle:
                self.checksum.value = ""
            self.changed()

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
                self.choices["repositories"].add(chosen)
                self.repository.value = chosen
                self.populate()
                self.changed()
        except Exception as exc:
            self.builder.show_error(str(exc))

    async def choose_bundle(self, _):
        try:
            files = await self.builder.picker.pick_files(dialog_title="Choose a released patch ZIP",
                file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["zip"])
            if files and files[0].path:
                self.choices["bundles"].add(files[0].path)
                self.bundle.value = files[0].path
                self.populate()
                self.bundle_changed()
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
        self.repository_path.value = self.repository.value or (
            "No installed repositories found. Browse to a repository containing engineering-playbook/."
            if not self.repository.options else "Choose the project you want to update.")
        self.bundle_path.value = self.bundle.value or (
            "No patches found. Download a released patch ZIP, then Refresh or Browse."
            if not self.bundle.options else "Choose a patch, then preview its compatibility with the selected repository.")
        app.body.controls = [self.title, self.inputs]
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
        for control in (self.repository, self.bundle, self.checksum, self.pick_repository,
                        self.pick_bundle, self.refresh_button):
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
