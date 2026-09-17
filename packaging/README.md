# Windows distribution

Repository Builder's app version is defined in `repository_builder/version.py`.
The bundled playbook version comes from `playbook.json` and `VERSION`. App updates
do not automatically reconcile repositories previously created by the app.

## Build

Use 64-bit Python 3.11 on Windows and install Inno Setup 7.1.0 (or a compatible
compiler supporting `packaging/windows.iss`). From the source root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r packaging/requirements-windows.lock
.\.venv\Scripts\python.exe scripts/build_windows_release.py --iscc "C:\path\to\Inno Setup\ISCC.exe"
```

Omit `--iscc` for a portable ZIP only. Flet's pinned desktop runtime is fetched on
the build computer when not already cached. The resulting package includes the
runtime and works offline; end users do not download Flet on first launch.

The builder uses PyInstaller's one-folder format and the existing Windows launcher.
It copies only files declared by the playbook manifest, bundles the native Flet
client, retains third-party notices, and runs the packaged repository creator before
writing release artifacts. It rejects stale playbook checksums. After intentional
framework edits, refresh them with `python scripts/update_checksums.py`.

Outputs under `dist/`:

- `RepositoryBuilder-<version>-windows-x64.zip`: extract the entire folder and run
  `Repository Builder.exe`.
- `RepositoryBuilder-<version>-windows-x64-setup.exe`: per-user installation,
  Start menu shortcut, upgrade support, and uninstall entry. Administrator access
  is not requested by the installer.
- `RepositoryBuilder-<version>-windows-x64-SHA256SUMS.txt`: checksums for both downloads.

The installer keeps a stable application ID and installation directory across
versions. It replaces installed app files, preserves logs and saved configurations
outside the install directory, and never migrates or deletes generated project
repositories. Updates are manual. There is no automatic update service.

## Verify

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/verify_windows_release.py dist\RepositoryBuilder-0.1.0-windows-x64.zip --graphical
powershell -NoProfile -ExecutionPolicy RemoteSigned -File scripts/verify_windows_installer.ps1 -InstallerPath dist\RepositoryBuilder-0.1.0-windows-x64-setup.exe
```

The release verifier extracts the ZIP into a different temporary directory with
spaces in its name, removes Python and Git from the child PATH, checks bundled file
hashes, and creates a dbt + Python project with capabilities. `--graphical` also
renders the bundled desktop client and creates a repository through the UI. Its
screenshots are saved under `.builder-qa/release/`.

Before a release, install the setup EXE into a disposable location, test a second
installation as an upgrade, and uninstall it. Confirm generated projects and saved
configurations outside that directory are preserved. A clean Windows VM remains
the recommended additional validation for broader deployment; PATH isolation on a
developer workstation does not prove compatibility with every managed Windows image.

## GitHub releases

The **Build Windows release** workflow runs on demand and uploads the ZIP, setup
EXE, and checksums as an Actions artifact. It does not publish automatically.
Review the artifacts, attach them to a release for a `builder-v<version>` tag, and
include notes describing the bundled playbook version and supported platforms.

Preview packages are unsigned. Production code signing requires a certificate
or signing service supplied by the maintainer. Do not disable Windows or company
security controls to install an unapproved build.

Git and an external Python installation remain optional creation prerequisites:
Git is needed only for initialization, and external Python is needed only to create
a project's virtual environment. The app itself includes its own Python runtime.
