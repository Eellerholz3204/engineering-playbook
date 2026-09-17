"""Build a relocatable Windows ZIP and optional per-user installer from allowlisted files."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from repository_builder.version import __version__


def execute(command: list[str], **kwargs) -> None:
    print("Running:", subprocess.list2cmdline(command), flush=True)
    subprocess.run(command, check=True, cwd=ROOT, **kwargs)


def safe_source(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"Invalid manifest source: {relative}")
    return path


def copy_playbook(destination: Path) -> dict:
    manifest = json.loads((ROOT / "playbook.json").read_text(encoding="utf-8-sig"))
    if (ROOT / "VERSION").read_text().strip() != manifest["playbook_version"]:
        raise ValueError("VERSION and playbook.json do not agree.")
    for name in manifest["immutable_framework_files"]:
        source = safe_source(name)
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for line in (destination / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split("  ", 1)
        if hashlib.sha256((destination / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Refresh SHA256SUMS.txt before building: {name}")
    return manifest


def write_notices(destination: Path, client: Path) -> None:
    notices = ["Repository Builder — third-party runtime notices\n",
               "The following components retain their respective licenses.\n"]
    packages = ["flet", "flet-desktop", "httpx", "httpcore", "anyio", "certifi", "h11", "idna",
                "msgpack", "oauthlib", "repath", "six", "typing_extensions", "pyinstaller"]
    for name in packages:
        distribution = importlib.metadata.distribution(name)
        notices.append(f"\n{'=' * 72}\n{name} {distribution.version}\n")
        included = set()
        for entry in distribution.files or []:
            if any(part.lower().startswith(("license", "copying", "notice")) for part in entry.parts):
                path = Path(distribution.locate_file(entry))
                if path.is_file() and path.suffix not in {".py", ".pyc"}:
                    content = path.read_text(encoding="utf-8", errors="replace")
                    if content not in included:
                        notices.append(content + "\n")
                        included.add(content)
        if not included:
            notices.append(distribution.metadata.get("License", "License information is in the upstream project.") + "\n")
        for link in distribution.metadata.get_all("Project-URL", []):
            notices.append(link + "\n")
    # Flutter's generated notice archive includes its native plugin dependencies.
    notice_archive = client / "data" / "flutter_assets" / "NOTICES.Z"
    if notice_archive.exists():
        import gzip
        notices.append("\nFlutter desktop client and native plugins\n" + gzip.decompress(notice_archive.read_bytes()).decode("utf-8"))
    notices.append("\n" + (Path(sys.base_prefix) / "LICENSE.txt").read_text(encoding="utf-8"))
    (destination / "THIRD-PARTY-NOTICES.txt").write_text("\n".join(notices), encoding="utf-8")


def build(iscc: Path | None, output: Path) -> None:
    if sys.platform != "win32" or sys.maxsize <= 2**32:
        raise RuntimeError("Build this release with 64-bit Python on Windows.")
    import flet_desktop
    client = flet_desktop.ensure_client_cached() / "flet"
    if not (client / "flet.exe").exists():
        raise RuntimeError("The Flet desktop client was not found.")
    build_root = ROOT / ".build"
    build_root.mkdir(exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    name = f"RepositoryBuilder-{__version__}-windows-x64"
    # Every intermediate path is generated beneath this workspace's .build directory.
    with tempfile.TemporaryDirectory(prefix="release-", dir=build_root) as temporary:
        job = Path(temporary).resolve()
        if not job.is_relative_to(build_root.resolve()):
            raise RuntimeError("Build directory escaped the workspace.")
        bundle = job / name
        bundle.mkdir()
        manifest = copy_playbook(bundle / "playbook")
        execute([sys.executable, "-m", "PyInstaller", "--noconfirm", "--onedir", "--console",
            "--name", "RepositoryBuilder.Runtime", "--distpath", str(job / "frozen"),
            "--workpath", str(job / "work"), "--specpath", str(job), "--paths", str(ROOT),
            "--icon", str(ROOT / "repository_builder/assets/repository-builder.ico"),
            "--collect-all", "flet", "--collect-all", "flet_desktop",
            "--add-data", f"{client}:flet-client", str(ROOT / "packaging/entry.py")],
            env={**os.environ, "PYINSTALLER_CONFIG_DIR": str(job / "cache")})
        shutil.move(str(job / "frozen/RepositoryBuilder.Runtime"), str(bundle / "_runtime"))
        compiler = Path(os.environ["WINDIR"]) / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
        version_source = job / "Version.cs"
        version_source.write_text(f'using System.Reflection;\n[assembly: AssemblyFileVersion("{__version__}.0")]\n', encoding="utf-8")
        execute([str(compiler), "/nologo", "/target:winexe", "/platform:x64", "/codepage:65001",
            f"/win32icon:{ROOT / 'repository_builder/assets/repository-builder.ico'}",
            f"/out:{bundle / 'Repository Builder.exe'}", "/reference:System.Windows.Forms.dll",
            str(ROOT / "repository_builder/windows/Launcher.cs"), str(version_source)])
        write_notices(bundle, client)
        (bundle / "README.txt").write_text(
            f"Repository Builder {__version__}\nBundled playbook: {manifest['playbook_version']}\n\n"
            "Extract the ENTIRE ZIP to a folder, then open Repository Builder.exe.\n"
            "Python and Flet are included; do not run files inside _runtime directly.\n"
            "PowerShell is required. Git is optional when Initialize Git is turned off.\n"
            "Creating a project's Python virtual environment requires an external Python installation.\n\n"
            "Projects and saved configurations stay wherever you choose to save them.\n"
            "Logs: %LOCALAPPDATA%\\EngineeringPlaybook\\RepositoryBuilder\\Logs\n"
            "Use the setup EXE for Start menu integration and uninstall support.\n"
            "Updates are manual. Keep all extracted files together.\n\n"
            "This preview is unsigned. Follow your organization's software approval policy.\n",
            encoding="utf-8")
        (bundle / "release.json").write_text(json.dumps({"app_version": __version__,
            "playbook_version": manifest["playbook_version"], "platform": "windows-x64"}, indent=2), encoding="utf-8")
        # Catch resource and subprocess failures before distributing an archive.
        report = job / "self-test.json"
        execute([str(bundle / "_runtime/RepositoryBuilder.Runtime.exe"), "--self-test", str(report)], timeout=120)
        if not json.loads(report.read_text())["success"]:
            raise RuntimeError("Packaged self-test failed.")
        archive = output / (name + ".zip")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
            for path in sorted(bundle.rglob("*")):
                if path.is_file():
                    zip_file.write(path, Path(name) / path.relative_to(bundle))
        artifacts = [archive]
        if iscc:
            execute([str(iscc.resolve()), f"/DAppVersion={__version__}", f"/DSourceDirectory={bundle}",
                f"/DOutputDirectory={output.resolve()}", str(ROOT / "packaging/windows.iss")])
            artifacts.append(output / (name + "-setup.exe"))
        checksums = output / (name + "-SHA256SUMS.txt")
        lines = []
        for artifact in artifacts:
            with artifact.open("rb") as stream:
                lines.append(f"{hashlib.file_digest(stream, 'sha256').hexdigest()}  {artifact.name}\n")
        checksums.write_text("".join(lines), encoding="ascii")
        print("Release artifacts:", *(str(p) for p in artifacts + [checksums]), sep="\n", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iscc", type=Path, help="Inno Setup compiler; omit for a portable ZIP only")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    arguments = parser.parse_args()
    build(arguments.iscc, arguments.output.resolve())
