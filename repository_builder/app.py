"""Flet desktop interface; creation behavior lives in core and the existing scripts."""

from __future__ import annotations

import asyncio
from pathlib import Path
import queue

import flet as ft
from .version import __version__

from .core import (
    ROOT, PYTHON_PROFILES, CreationPlan, check_prerequisites, create_repository,
    document_paths, load_catalog, powershell_command, scaffold_paths,
)

BLUE = "#0067D9"
INK = "#1D1D1F"
MUTED = "#626269"
LINE = "#E1E2E6"
BACKGROUND = "#F5F5F7"


class RepositoryBuilder:
    def __init__(self, page: ft.Page):
        self.page = page
        self.catalog = load_catalog()
        self.step = 0
        self.busy = False
        self.completed = False
        self.reviewed_plan = None
        self.selected_profile = "generic"
        self.selected_capabilities: set[str] = set()
        self.picker = ft.FilePicker()
        self.clipboard = ft.Clipboard()
        page.services.extend([self.picker, self.clipboard])
        page.title = "Repository Builder · Engineering Playbook"
        page.window.icon = str(ROOT / "repository_builder" / "assets" / "repository-builder.ico")
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(color_scheme_seed=BLUE, font_family="Segoe UI", use_material3=True)
        page.bgcolor = BACKGROUND
        page.padding = 0
        page.window.width = 1160
        page.window.height = 860
        page.window.min_width = 860
        page.window.min_height = 680

        self.name = ft.TextField(label="Project name", hint_text="my-data-product", autofocus=True,
                                 on_change=self.project_changed, **self.field_style())
        self.parent = ft.TextField(label="Parent folder", value=str(Path.home() / "source" / "repos"),
                                   expand=True, on_change=self.project_changed, **self.field_style())
        self.location = ft.Text(size=12, color=MUTED, selectable=True)
        self.git = ft.Switch(label="Initialize Git", value=True)
        self.venv = ft.Switch(label="Create a Python virtual environment", value=False, disabled=True)
        self.error = ft.Text(color="#B42318", size=14, visible=False)
        self.status = ft.Text("Ready when you are.", color=MUTED, size=13)
        self.progress = ft.ProgressBar(color=BLUE, visible=False)
        self.output = ft.TextField(read_only=True, multiline=True, min_lines=5, max_lines=9,
                                   visible=False, **{**self.field_style(), "text_size": 12})
        self.sidebar = ft.Column(spacing=8, expand=True)
        self.body = ft.Column(spacing=22, scroll=ft.ScrollMode.AUTO, expand=True,
                              horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.back = ft.TextButton("Back", on_click=self.previous)
        self.import_button = ft.TextButton("Open configuration", icon=ft.Icons.UPLOAD_FILE_OUTLINED,
                                            on_click=self.import_configuration)
        self.next = ft.Button("Choose type", on_click=self.advance, bgcolor=BLUE, color="white",
                              height=42, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=9)))
        self.form = ft.Container(self.body, padding=ft.Padding.symmetric(horizontal=36, vertical=28),
                                 expand=True, bgcolor=BACKGROUND)
        self.footer = ft.Container(ft.Column([self.error, ft.Row([self.back, self.import_button, ft.Container(expand=True), self.next])]),
                                   padding=ft.Padding.symmetric(horizontal=36, vertical=18),
                                   bgcolor="white", border=ft.Border(top=ft.BorderSide(1, LINE)))
        self.content = ft.Row([
            ft.Container(self.sidebar, width=218, padding=24, bgcolor="#ECEEF2",
                         border=ft.Border(right=ft.BorderSide(1, LINE))),
            ft.Column([self.form, self.footer], spacing=0, expand=True),
        ], spacing=0, expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH)
        self.build_sidebar()
        page.add(self.content)
        self.render()

    @staticmethod
    def field_style() -> dict:
        return dict(border_radius=9, border_color="#C6C8CE", focused_border_color=BLUE,
                    filled=True, fill_color="white", text_size=14)

    @staticmethod
    def heading(title: str, subtitle: str) -> ft.Column:
        return ft.Column([ft.Text(title, size=29, weight=ft.FontWeight.W_600, color=INK),
                          ft.Text(subtitle, size=14, color=MUTED)], spacing=8)

    @staticmethod
    def card(controls: list, padding=20) -> ft.Container:
        return ft.Container(ft.Column(controls, spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH), bgcolor="white", padding=padding,
                            border_radius=13, border=ft.Border.all(1, LINE))

    def plan(self) -> CreationPlan:
        return CreationPlan(
            project_name=self.name.value.strip(),
            repository_path=str(Path(self.parent.value.strip()) / self.name.value.strip()),
            project_type=self.selected_profile,
            capabilities=tuple(key for key in self.catalog["capability_packs"] if key in self.selected_capabilities),
            create_venv=bool(self.venv.value), initialize_git=bool(self.git.value),
            playbook_version=self.catalog["playbook_version"],
        )

    def project_changed(self, _=None):
        self.location.value = f"Will create: {Path(self.parent.value or '.') / (self.name.value or 'project-name')}"
        self.page.update()

    def show_error(self, message: str):
        self.error.value = message
        self.error.visible = True
        self.page.update()

    async def choose_folder(self, _):
        try:
            chosen = await self.picker.get_directory_path(dialog_title="Choose the parent folder")
            if chosen:
                self.parent.value = chosen
                self.project_changed()
        except Exception as exc:
            self.show_error(f"Couldn't open the folder picker. You can enter the path directly. {exc}")

    async def import_configuration(self, _):
        try:
            files = await self.picker.pick_files(dialog_title="Open repository configuration",
                file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["json"])
            if not files:
                return
            plan = CreationPlan.from_json(Path(files[0].path).read_text(encoding="utf-8-sig"), self.catalog)
            if Path(plan.repository_path).name != plan.project_name:
                raise ValueError("For this interface, the destination folder name must match the project name. You can run custom paths using the configuration script.")
            self.name.value = plan.project_name
            self.parent.value = str(Path(plan.repository_path).parent)
            self.selected_profile = plan.project_type
            self.selected_capabilities = set(plan.capabilities)
            self.git.value = plan.initialize_git
            self.venv.value = plan.create_venv
            self.render()
        except Exception as exc:
            self.show_error(str(exc))

    def build_sidebar(self):
        self.nav_items = []
        self.sidebar.controls = [
            ft.Image(src=str(ROOT / "repository_builder" / "assets" / "repository-builder.png"),
                     width=42, height=42, semantics_label="Repository Builder"),
            ft.Text("Engineering\nPlaybook", size=20, weight=ft.FontWeight.W_600, color=INK),
            ft.Text("REPOSITORY BUILDER", size=10, weight=ft.FontWeight.W_600, color=MUTED),
            ft.Container(height=24),
        ]
        for index, (label, icon) in enumerate([
            ("Project", ft.Icons.FOLDER_OUTLINED),
            ("Catalog", ft.Icons.GRID_VIEW_ROUNDED),
            ("Review", ft.Icons.FACT_CHECK_OUTLINED),
        ]):
            selected = index == self.step
            item = ft.Container(
                ft.Row([ft.Icon(icon, size=19, color=BLUE if selected else MUTED),
                        ft.Text(label, size=14, color=BLUE if selected else MUTED,
                                weight=ft.FontWeight.W_600 if selected else ft.FontWeight.NORMAL)], spacing=12),
                bgcolor="#DDE8F8" if selected else None, border_radius=8, padding=12,
            )
            self.nav_items.append(item)
            self.sidebar.controls.append(item)
        self.sidebar.controls.extend([
            ft.Container(expand=True),
            ft.Text("A considered start\nfor your next project.", size=13, color=MUTED),
            ft.Text(f"Playbook {self.catalog['playbook_version']}", size=11, color=MUTED),
            ft.Text(f"Builder {__version__}", size=11, color=MUTED),
        ])

    def render(self):
        self.error.visible = False
        for index, item in enumerate(self.nav_items):
            selected = index == self.step
            item.bgcolor = "#DDE8F8" if selected else None
            icon, label = item.content.controls
            icon.color = label.color = BLUE if selected else MUTED
            label.weight = ft.FontWeight.W_600 if selected else ft.FontWeight.NORMAL
        self.back.visible = self.step > 0 and not self.completed
        self.import_button.visible = self.step == 0
        self.next.content = ["Choose type", "Review repository", "Create repository"][self.step]
        if self.completed:
            self.next.content = "Open repository folder"
        self.next.on_click = self.open_repository if self.completed else self.advance
        self.body.controls = [self.project_view, self.catalog_view, self.review_view][self.step]()
        self.project_changed()

    def project_view(self) -> list:
        return [self.heading("Start something well.", "Create a repository with the structure and guidance your project needs."),
            self.card([
                ft.Text("Project details", size=17, weight=ft.FontWeight.W_600),
                self.name,
                ft.Text("Use a short, descriptive name. Hyphens and underscores are welcome.", size=12, color=MUTED),
                ft.Row([self.parent, ft.IconButton(ft.Icons.FOLDER_OPEN_OUTLINED,
                    tooltip="Choose parent folder", on_click=self.choose_folder)]),
                self.location,
            ]),
            self.card([
                ft.Text("Version control", size=17, weight=ft.FontWeight.W_600), self.git,
                ft.Text("Creates a local Git repository. You can connect it to GitHub later.", size=13, color=MUTED),
            ]),
        ]

    def choose_profile(self, key: str):
        self.selected_profile = key
        if key not in PYTHON_PROFILES:
            self.venv.value = False
        self.render()

    def toggle_capability(self, key: str, selected: bool):
        if selected:
            self.selected_capabilities.add(key)
        else:
            self.selected_capabilities.discard(key)
        self.render()

    def catalog_view(self) -> list:
        profile_cards = []
        for key, profile in self.catalog["repository_profiles"].items():
            selected = key == self.selected_profile
            profile_cards.append(ft.Container(
                ft.Column([
                    ft.Radio(value=key, label=profile.get("label", key), fill_color=BLUE),
                    ft.Text(profile.get("description", key), size=12, color=MUTED),
                ], spacing=9),
                col={"xs": 12, "md": 6}, padding=16, border_radius=11,
                bgcolor="#EDF5FF" if selected else "white",
                border=ft.Border.all(2 if selected else 1, BLUE if selected else LINE),
                on_click=lambda _, k=key: self.choose_profile(k),
                tooltip=f"Select {profile.get('label', key)}",
            ))
        base = set(document_paths(self.catalog, self.selected_profile))
        capability_rows = []
        for key, capability in self.catalog["capability_packs"].items():
            extra = {entry["target"] for entry in capability["templates"]} - base
            note = f"Adds {len(extra)} document{'s' if len(extra) != 1 else ''}" if extra else "Documents already included by this type"
            capability_rows.append(ft.Column([
                ft.Checkbox(label=capability.get("label", key), value=key in self.selected_capabilities,
                            on_change=lambda e, k=key: self.toggle_capability(k, e.control.value)),
                ft.Text(capability.get("description", ""), size=12, color=MUTED),
                ft.Text(note, size=11, color=BLUE),
            ], spacing=3))
        self.venv.disabled = self.selected_profile not in PYTHON_PROFILES
        return [self.heading("Find the right foundation.", "Choose one repository type, then add the capabilities your project needs."),
            ft.Text("Repository type", size=17, weight=ft.FontWeight.W_600),
            ft.RadioGroup(value=self.selected_profile,
                          content=ft.ResponsiveRow(profile_cards, spacing=12, run_spacing=12),
                          on_change=lambda e: self.choose_profile(e.control.value)),
            self.card([ft.Text("Optional capabilities", size=17, weight=ft.FontWeight.W_600), *capability_rows]),
            self.card([self.venv, ft.Text("Available for Python and dbt + Python repositories.", size=12, color=MUTED)]),
        ]

    def review_view(self) -> list:
        plan = self.reviewed_plan or self.plan()
        documents = document_paths(self.catalog, plan.project_type, plan.capabilities)
        files = scaffold_paths(plan)
        title = "Your repository is ready." if self.completed else "A clear view before you create."
        capabilities = ", ".join(self.catalog["capability_packs"][key].get("label", key) for key in plan.capabilities) or "None"
        return [self.heading(title, "Review the location, included files, and setup options." if not self.completed else "Your project files are in place. Open the folder to begin."),
            self.card([
                ft.Text(plan.project_name, size=21, weight=ft.FontWeight.W_600),
                ft.Text(plan.repository_path, size=13, color=MUTED, selectable=True),
                ft.Divider(color=LINE),
                ft.Text(f"Type: {self.catalog['repository_profiles'][plan.project_type].get('label', plan.project_type)}", size=14),
                ft.Text(f"Capabilities: {capabilities}", size=14),
                ft.Text(f"Git: {'Yes' if plan.initialize_git else 'No'}    ·    Virtual environment: {'Yes' if plan.create_venv else 'No'}", size=13, color=MUTED),
            ]),
            self.card([
                ft.Text(f"{len(documents)} project documents", size=17, weight=ft.FontWeight.W_600),
                ft.Text("Shared documents appear once, even when multiple selections include them.", size=12, color=MUTED),
                ft.ExpansionTile(title=ft.Text("View included files", size=14), controls=[
                    ft.Container(ft.Column([ft.Text(path, size=12, selectable=True) for path in files + documents], spacing=7), padding=16)
                ]),
                ft.Text("The engineering-playbook folder contains the versioned framework. Project-owned documents live in docs/.", size=12, color=MUTED),
            ]),
            ft.Row([ft.TextButton("Save configuration", icon=ft.Icons.SAVE_OUTLINED, on_click=self.save_configuration),
                    ft.TextButton("Copy PowerShell", icon=ft.Icons.CONTENT_COPY, on_click=self.copy_command)], wrap=True),
            self.progress, self.status, self.output,
        ]

    def previous(self, _):
        if self.busy:
            return
        self.step = max(0, self.step - 1)
        self.reviewed_plan = None
        self.render()

    async def advance(self, _):
        if self.busy or self.completed:
            return
        try:
            plan = self.plan()
            plan.validate(self.catalog)
            if not self.parent.value.strip():
                raise ValueError("Choose a parent folder.")
            if self.step < 2:
                if self.step == 1:
                    check_prerequisites(plan)
                    self.reviewed_plan = plan
                self.step += 1
                self.render()
            else:
                await self.create()
        except Exception as exc:
            self.show_error(str(exc))

    async def save_configuration(self, _):
        try:
            plan = self.reviewed_plan or self.plan()
            destination = await self.picker.save_file(dialog_title="Save repository configuration",
                file_name=f"{plan.project_name}.repository.json",
                file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["json"],
                src_bytes=plan.to_json().encode("utf-8"))
            if destination:
                Path(destination).write_text(plan.to_json(), encoding="utf-8")
                self.status.value = "Configuration saved. Open it in the builder to reuse these selections."
                self.page.update()
        except Exception as exc:
            self.show_error(f"Couldn't save the configuration: {exc}")

    async def copy_command(self, _):
        try:
            await self.clipboard.set(powershell_command(self.reviewed_plan or self.plan()))
            self.status.value = "PowerShell command copied."
            self.page.update()
        except Exception as exc:
            self.show_error(f"Couldn't copy the command: {exc}")

    async def open_repository(self, _):
        import os
        import subprocess
        import sys

        path = self.reviewed_plan.repository_path
        try:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])
        except OSError as exc:
            self.show_error(f"Couldn't open the folder: {exc}")

    async def create(self):
        plan = self.reviewed_plan
        plan.validate(self.catalog)
        self.busy = True
        self.back.disabled = self.next.disabled = True
        self.progress.visible = True
        self.output.visible = True
        self.output.value = ""
        self.error.visible = False
        self.status.value = "Creating your repository… This may take a few minutes with a virtual environment."
        self.page.window.prevent_close = True
        self.page.update()
        await self.body.scroll_to(offset=-1)
        messages: queue.Queue[str] = queue.Queue()
        task = asyncio.create_task(asyncio.to_thread(create_repository, plan, messages.put))
        lines = []
        try:
            while not task.done() or not messages.empty():
                while not messages.empty():
                    lines.append(messages.get_nowait())
                self.output.value = "\n".join(lines[-250:])
                self.page.update()
                if not task.done():
                    await asyncio.sleep(0.15)
            code = await task
            if code:
                raise RuntimeError(f"Creation stopped (exit code {code}). Review the output below. Some files may have been created; inspect the destination before retrying.")
            self.completed = True
            self.status.value = "Created successfully. Review the document placeholders before implementation."
        except Exception as exc:
            self.status.value = "Repository creation did not finish."
            self.error.value = str(exc)
            self.error.visible = True
        finally:
            self.busy = False
            self.progress.visible = False
            self.back.disabled = self.next.disabled = False
            self.page.window.prevent_close = False
            if self.completed:
                self.render()
                await self.body.scroll_to(offset=0)
            self.page.update()


def main(page: ft.Page):
    RepositoryBuilder(page)
