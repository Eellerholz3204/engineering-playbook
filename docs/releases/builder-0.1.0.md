# Repository Builder 0.1.0 — preview

Windows x64 desktop app with Engineering Playbook 3.2.1 included.

- Browse repository types and capabilities with descriptions and document previews.
- Create local repositories, optionally initialize Git and create a Python virtual environment.
- Save and restore creation configurations or copy the equivalent PowerShell command.
- Launch from a custom-icon Start menu or taskbar shortcut without a terminal.
- Run from a portable ZIP or install for the current user with upgrade and uninstall support.
- Python, Flet, and the desktop client are bundled; no app runtime setup is required.

Choose the setup EXE for normal installation. Choose the ZIP for portable use and
extract the entire folder before opening `Repository Builder.exe`.

PowerShell is required. Git is needed only when Initialize Git is enabled. Creating
a project virtual environment requires an external Python installation.

This first preview is unsigned and uses manual updates. Windows x64 is the supported
target. Existing project repositories are not changed when the app is upgraded or
uninstalled. Verify downloads against the accompanying SHA256SUMS file.
