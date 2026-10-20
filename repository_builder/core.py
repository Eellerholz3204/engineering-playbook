"""Catalog, validated creation plans, and process execution without UI dependencies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Callable
from .runtime import resource_root

ROOT = resource_root()
PYTHON_PROFILES = {"python", "dbt-python"}


def load_catalog(root: Path = ROOT) -> dict:
    return json.loads((root / "playbook.json").read_text(encoding="utf-8-sig"))


@dataclass(frozen=True)
class CreationPlan:
    project_name: str
    repository_path: str
    project_type: str = "generic"
    capabilities: tuple[str, ...] = ()
    create_venv: bool = False
    initialize_git: bool = True
    playbook_version: str = ""
    schema_version: int = 1

    def validate(self, catalog: dict, *, check_destination: bool = True) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("This configuration version is not supported.")
        if not isinstance(self.project_name, str) or not re.fullmatch(
            r"[A-Za-z][A-Za-z0-9_-]{0,79}", self.project_name
        ):
            raise ValueError("Use a project name starting with a letter, followed by letters, numbers, hyphens or underscores (up to 80 characters).")
        if self.project_name.upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
            raise ValueError("Choose a project name that is not a reserved Windows filename.")
        if not isinstance(self.project_type, str) or self.project_type not in catalog["repository_profiles"]:
            raise ValueError("Select a repository type from the catalog.")
        if not isinstance(self.capabilities, (list, tuple)) or any(
            not isinstance(cap, str) or cap not in catalog["capability_packs"] for cap in self.capabilities
        ):
            raise ValueError("The configuration contains an unknown capability.")
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("Capabilities must not be repeated.")
        if type(self.create_venv) is not bool or type(self.initialize_git) is not bool:
            raise ValueError("Virtual environment and Git options must be true or false.")
        if self.create_venv and self.project_type not in PYTHON_PROFILES:
            raise ValueError("A virtual environment is available only for Python and dbt + Python.")
        if self.playbook_version != catalog["playbook_version"]:
            raise ValueError(f"This configuration requires playbook {self.playbook_version or '(unspecified)'}. This copy is {catalog['playbook_version']}.")
        if not isinstance(self.repository_path, str) or not self.repository_path.strip():
            raise ValueError("Choose a repository location.")
        path = Path(self.repository_path)
        if not path.is_absolute() or ".." in path.parts:
            raise ValueError("Use an absolute repository path without '..' segments.")
        if path == path.parent:
            raise ValueError("Choose a project folder, not a drive root.")
        if check_destination:
            if path.exists() and (not path.is_dir() or any(path.iterdir())):
                raise ValueError("The destination must be a new or empty folder. Existing files will not be replaced.")
            parent = path.parent
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            if not parent.is_dir():
                raise ValueError("The destination is inside a file. Choose another location.")

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2) + "\n"

    @classmethod
    def from_json(cls, content: str, catalog: dict) -> CreationPlan:
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError("The configuration must be a JSON object.")
            plan = cls(**data)
            plan.validate(catalog, check_destination=False)
            return cls(**{**data, "capabilities": tuple(plan.capabilities)})
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("The configuration is invalid or contains unsupported fields.") from exc


def document_paths(catalog: dict, profile: str, capabilities=()) -> list[str]:
    entries = list(catalog["common_project_templates"])
    entries += catalog["repository_profiles"][profile]["templates"]
    for capability in capabilities:
        entries += catalog["capability_packs"][capability]["templates"]
    return sorted({"AGENTS.md", *(entry["target"] for entry in entries)})


def scaffold_paths(plan: CreationPlan) -> list[str]:
    paths = [".engineering-playbook.json", ".gitignore", "engineering-playbook/"]
    if plan.project_type in {"dbt", "dbt-python"}:
        paths += ["dbt_project.yml", "models/", "tests/", "macros/", "seeds/", "snapshots/"]
    if plan.project_type in PYTHON_PROFILES:
        paths += ["pyproject.toml", f"src/{plan.project_name.replace('-', '_')}/__init__.py", "tests/"]
    if plan.create_venv:
        paths.append(".venv/")
    if plan.initialize_git:
        paths.append(".git/")
    return sorted(set(paths))


def powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable:
        raise ValueError("PowerShell was not found. Install PowerShell or add it to PATH.")
    return executable


def check_prerequisites(plan: CreationPlan) -> None:
    powershell_executable()
    if plan.initialize_git and not shutil.which("git"):
        raise ValueError("Git was not found. Install Git or turn off Initialize Git.")
    if plan.create_venv and not shutil.which("python"):
        raise ValueError("Python was not found on PATH. Turn off Create virtual environment or install Python.")


def powershell_command(plan: CreationPlan, root: Path = ROOT) -> str:
    def quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    parameters = {
        "ProjectName": quote(plan.project_name),
        "RepositoryPath": quote(plan.repository_path),
        "ProjectType": quote(plan.project_type),
        "Capabilities": "@(" + ", ".join(map(quote, plan.capabilities)) + ")",
        "PlaybookSourcePath": quote(str(root)),
        "CreateVenv": "$true" if plan.create_venv else "$false",
        "NoGit": "$false" if plan.initialize_git else "$true",
    }
    lines = ["$repositoryOptions = @{"]
    lines += [f"    {key} = {value}" for key, value in parameters.items()]
    lines += ["}", f"& {quote(str(root / 'scripts' / 'new_engineering_repository.ps1'))} @repositoryOptions"]
    return "\n".join(lines)


def create_repository(plan: CreationPlan, on_output: Callable[[str], None], root: Path = ROOT) -> int:
    """Pass data via JSON to a fixed script, never through an evaluated command string."""
    plan.validate(load_catalog(root))
    check_prerequisites(plan)
    with tempfile.TemporaryDirectory(prefix="engineering-playbook-") as temporary:
        config = Path(temporary) / "repository.json"
        config.write_text(plan.to_json(), encoding="utf-8")
        command = [powershell_executable(), "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "RemoteSigned", "-File",
                   str(root / "scripts" / "create_repository_from_config.ps1"), "-ConfigurationPath", str(config)]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding="utf-8", errors="replace", cwd=root,
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)) as process:
            assert process.stdout is not None
            for line in process.stdout:
                on_output(line.rstrip())
            return process.wait()
