"""Preview/apply surface for an existing repository; patch policy lives in patching."""

import asyncio
import json
import re
from pathlib import Path
import zipfile

import flet as ft

from .patching import apply_patch, inspect_patch
from .core import ROOT
from .patch_downloads import available_patches, cached_checksum, cached_patches, download_patch, local_checksum


def children(folder):
    """Bound discovery to immediate children; unavailable folders are optional."""
    try:
        return list(folder.iterdir())
    except OSError:
        return []


def patch_metadata(path):
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
        return data
    except (OSError, ValueError, KeyError, RuntimeError, zipfile.BadZipFile, NotImplementedError):
        return None


def patch_label(path):
    data = patch_metadata(path)
    if data:
        return f"{data['patch_id'].replace('-', ' ')} ({data['base_version']} to {data['target_version']})"
    return None


def release_title(item):
    return re.sub(r"^Playbook patch:\s*", "", item.title, flags=re.IGNORECASE)


def release_summary(notes):
    """Show introductory prose, not download commands or release identity fields."""
    intro = re.split(r"(?m)^##\s", notes, maxsplit=1)[0]
    for paragraph in re.split(r"\n\s*\n", intro.strip()):
        text = " ".join(paragraph.split())
        if text and not text.startswith(("#", "-", "*", "```", "Patch ID:", "Framework version:", "Release tag:")):
            return text
    return "No overview was provided. Review the release notes and preview for details."


class PatchView:
    def __init__(self, builder):
        self.builder = builder
        self.report = None
        self.reviewed_inputs = None
        self.completed = False
        self.published = {}
        self.downloaded = {}
        self.reviewed_bundle = None
        self.check_button = ft.TextButton("Check for patches", icon=ft.Icons.CLOUD_DOWNLOAD_OUTLINED,
            on_click=self.check_online)
        self.online_status = ft.Text("Checks this project's public GitHub releases only when requested. No sign-in needed.", size=12)
        self.repository = ft.Dropdown(label="Existing repository", on_select=self.changed,
            expand=True, expanded_insets=0,
            editable=True, enable_filter=True, on_text_change=self.search_changed,
            enable_search=True, menu_height=300, hint_text="Select a repository or browse…",
            **builder.field_style())
        self.bundle = ft.Dropdown(label="Patch", on_select=self.changed,
            expand=True, expanded_insets=0,
            editable=True, enable_filter=True, on_text_change=self.search_changed,
            enable_search=True, menu_height=300, hint_text="Select a patch or browse…",
            **builder.field_style())
        self.repository_path = ft.Text(size=12, selectable=True)
        self.bundle_path = ft.Text(size=12, selectable=True)
        self.description = ft.Text()
        self.notes_text = ft.Text(selectable=True, size=12)
        self.notes = ft.ExpansionTile(title=ft.Text("Release notes"), visible=False,
            controls=[self.notes_text])
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
            ft.Row([self.check_button, self.pick_bundle, self.refresh_button]),
            self.bundle, self.bundle_path,
            ft.Text("What this patch does", size=16, weight=ft.FontWeight.W_600),
            self.description, self.notes,
            self.online_status,
            ft.Text("Preview downloads published patches and verifies their checksums automatically. It does not change project files.", size=12),
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
        try:
            bundles.update(cached_patches())
        except (OSError, ValueError) as exc:
            self.online_status.value = f"Patch cache unavailable: {exc}. Local Browse is still available."
        bundles.update(Path(p) for p in self.choices["bundles"])
        # Preserve explicit selections so refresh never silently switches targets.
        if self.repository.value:
            repositories.add(Path(self.repository.value))
        if self.bundle.value and self.bundle.value not in self.published:
            bundles.add(Path(self.bundle.value))
        self.repository.options = [ft.DropdownOption(key=str(p), text=f"{p.name} · {p.parent}")
            for p in sorted(repositories, key=lambda p: str(p).casefold())]
        # Match only pinned cache identities, never filenames alone. One choice per
        # published download; local selections are retained without silently switching.
        for path in bundles:
            try:
                sha = cached_checksum(path)
            except (OSError, ValueError):
                continue
            for key, item in self.published.items():
                if sha and sha == item.asset_digest and path.name == item.name:
                    self.downloaded[key] = (path, sha)
        self.bundle.options = [ft.DropdownOption(key=p.key, text=release_title(p))
            for p in self.published.values()]
        remote_paths = {str(path) for key, (path, _) in self.downloaded.items() if key in self.published}
        for path in sorted(bundles, key=lambda p: str(p).casefold()):
            if str(path) in remote_paths and str(path) != self.bundle.value:
                continue
            label = patch_label(path)
            if label or str(path) in self.choices["bundles"] or str(path) == self.bundle.value:
                self.bundle.options.append(ft.DropdownOption(key=str(path),
                    text=label or path.name, tooltip=str(path)))

    def refresh(self, _=None):
        if self.builder.busy:
            return
        self.populate()
        self.changed()

    async def check_online(self, _):
        if self.builder.busy:
            return
        self.online_status.value = "Checking published GitHub patches…"
        self.changed()
        self.busy(True)
        try:
            patches = await asyncio.to_thread(available_patches)
            # A disappeared release becomes an offline local choice only if downloaded.
            selected = self.bundle.value
            if selected in self.published and selected not in {p.key for p in patches}:
                cached = self.downloaded.get(selected)
                self.bundle.value = str(cached[0]) if cached else None
            self.published = {p.key: p for p in patches}
            self.downloaded = {key: cached for key, cached in self.downloaded.items()
                if key in self.published and self.published[key].asset_digest == cached[1]}
            self.populate()
            if not self.bundle.value and len(self.bundle.options) == 1:
                self.bundle.value = self.bundle.options[0].key
            self.online_status.value = (f"Found {len(patches)} published patch(es). Choose a patch, then Preview patch."
                if patches else "No published patch ZIP/checksum pairs found. Local patches remain available.")
            self.show()
        except Exception as exc:
            self.online_status.value = "Couldn't refresh published patches. Existing choices remain available; downloaded patches work offline."
            self.show()
            self.builder.show_error(str(exc))
        finally:
            self.busy(False)

    def search_changed(self, event):
        control = event.control
        selected = next((o for o in control.options if o.key == control.value), None)
        if selected is None or control.text != selected.text:
            control.value = None
            self.changed()

    def values(self):
        return (self.repository.value or "", self.bundle.value or "")

    def changed(self, _=None):
        self.report = self.reviewed_inputs = None
        self.reviewed_bundle = None
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
        self.repository_path.value = self.repository.value or (
            "No installed repositories found. Browse to a repository containing engineering-playbook/."
            if not self.repository.options else "Choose the project you want to update.")
        item = self.published.get(self.bundle.value)
        self.notes.visible = bool(item and item.notes)
        self.notes_text.value = item.notes if item else ""
        if item:
            self.bundle_path.value = ("Downloaded · Available offline" if item.key in self.downloaded else
                "Published on GitHub · Downloads automatically when you preview")
            self.description.value = release_summary(item.notes)
        elif self.bundle.value:
            self.bundle_path.value = self.bundle.value
            data = patch_metadata(Path(self.bundle.value)) or {}
            summary = data.get("summary")
            self.description.value = summary if isinstance(summary, str) and summary else "Preview this local patch to read its summary and check compatibility. Use only ZIPs from a trusted publisher."
        else:
            self.description.value = "Select a patch to see its purpose before making changes."
            self.bundle_path.value = (
                "No patches found. Check for patches above, or Browse to a local ZIP."
                if not self.bundle.options else "Choose a patch, then preview its compatibility with the selected repository.")
        app.body.controls = [self.title, self.inputs]
        if self.report:
            report = self.report
            details = [ft.Text(report["patch_id"], size=18, weight=ft.FontWeight.W_600),
                       ft.Text(report["summary"]),
                       ft.Text(f"Playbook {report['base_version']} → {report['target_version']}", size=13)]
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
        for control in (self.repository, self.bundle, self.pick_repository,
                        self.pick_bundle, self.refresh_button, self.check_button):
            control.disabled = value
        app.page.update()

    async def preview(self, _):
        if self.builder.busy:
            return
        self.changed()
        self.busy(True)
        try:
            values = self.values()
            repo, bundle = values
            if not repo or not bundle:
                raise ValueError("Choose the existing repository and patch.")
            item = self.published.get(bundle)
            if item:
                cached = self.downloaded.get(bundle)
                if cached:
                    path, checksum = cached
                else:
                    self.online_status.value = "Downloading and verifying the selected patch…"
                    self.show()
                    path, checksum = await asyncio.to_thread(download_patch, item, Path(repo))
                    self.downloaded[bundle] = (path, checksum)
                    self.choices["bundles"].add(str(path))
                    self.populate()
                self.online_status.value = "Download verified. Checking repository compatibility…"
            else:
                path = Path(bundle)
                checksum = local_checksum(path)
            self.report = await asyncio.to_thread(inspect_patch, path, Path(repo), checksum)
            self.reviewed_bundle = path
            self.reviewed_inputs = values
            self.online_status.value = "Preview complete. No project files changed. Review the results before applying."
            self.show()
        except Exception as exc:
            self.report = self.reviewed_inputs = None
            self.reviewed_bundle = None
            self.online_status.value = "Preview failed. No patch was applied. Review the error and retry or choose another patch."
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
            repo, _ = self.reviewed_inputs
            self.report = await asyncio.to_thread(apply_patch, self.reviewed_bundle, Path(repo), self.report["sha256"])
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
