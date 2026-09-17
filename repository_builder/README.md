# Repository Builder

A local Flet desktop app for creating repositories from the Engineering Playbook.
The app reads types, descriptions, capabilities, and document mappings from
`playbook.json`. It calls the existing PowerShell generator and never evaluates
user-entered command text.

## Run on Windows

Prerequisites: Python 3.11 or newer, PowerShell, and Git if you choose to initialize
a repository. The desktop dependency is pinned to Flet 0.83.1.

From the playbook root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-builder.txt
.\.venv\Scripts\python.exe -m repository_builder
```

Alternatively, `scripts/start_repository_builder.ps1` uses the local `.venv` when
present and otherwise uses `python` on PATH. Neither launch method needs the
playbook profile commands. If Flet is already installed, make sure its desktop
extra is installed too; the base Python package alone does not include the desktop
runtime.

## Windows shortcut and icon

After setting up `.venv`, install a shortcut for the current user:

```powershell
.\scripts\install_repository_builder_shortcut.ps1
```

Search Start for **Repository Builder**, right-click, and choose **Pin to Start** or
**Pin to taskbar** (sometimes under **More**). You can also pin the running app's
taskbar button. The installer does not change your existing pins.

The installer compiles a small Windows GUI launcher using the .NET Framework
compiler included with Windows. It embeds the app's icon, starts the local Python
environment without a console, and assigns a matching Windows application ID to
the shortcut and its own Flet window. Relaunch properties point pinned buttons back
to the launcher. This also supports older Flet desktop clients that do not yet read
the newer [Flet taskbar environment variables](https://flet.dev/docs/reference/environment-variables/).

The source launcher is generated under `.launcher/`. Startup logs are written to
`%LOCALAPPDATA%\EngineeringPlaybook\RepositoryBuilder\Logs`, with a separate log for
each launch. Close the app before rebuilding the launcher, or use
`-SkipBuild` to create another shortcut from the existing launcher. To put a shortcut
somewhere else, pass `-ShortcutDirectory 'C:\path\to\folder'`.

Keep this playbook folder and its `.venv` in place: the shortcut uses them. If you
move the playbook, run the installer again and refresh any old taskbar pins. This
is a local launcher, not a standalone distribution for computers without Python.

The editable icon is `assets/repository-builder.svg`. Its PNG and multi-resolution
Windows ICO are included; regenerate both with
`scripts/build_repository_builder_icon.ps1` after changing the vector artwork.

## Workflow

1. **Project:** enter a name and choose a parent folder. Git initialization is optional.
2. **Catalog:** choose one type and any capabilities. Cards explain the current
   scaffolding, and capabilities show when their documents are already included.
   Virtual environments are offered only for Python profiles.
3. **Review:** inspect the destination and file list. Save the configuration or copy
   the PowerShell command, then create the repository. The output panel displays
   progress and errors; the success screen can open the project folder.

Names begin with a letter and contain letters, digits, hyphens, or underscores,
up to 80 characters. The destination must be new or empty. The app creates local
files and optionally initializes Git; it does not create a GitHub remote or publish
anything. Closing the window is temporarily disabled during creation so the
generator can finish.

If creation fails after writing files, the app preserves those files and shows the
failure. Inspect the destination before retrying; it does not automatically erase
partial output.

## Reuse a configuration

**Save configuration** writes a JSON document containing the selections and exact
playbook version. **Open saved configuration** restores it. Review the destination
when sharing a configuration because local paths differ between computers.

You can also execute a saved configuration without the app:

```powershell
.\scripts\create_repository_from_config.ps1 -ConfigurationPath .\example.repository.json
```

The runner rejects unknown fields, unsupported types, and version mismatches.
The app requires the destination folder name to match the project name; the runner
supports custom destination names. Copied PowerShell commands use a parameter
hashtable, so line-continuation backticks are unnecessary.

The app starts a child PowerShell process with a process-only `RemoteSigned`
execution policy. It does not change machine or user policy, and organization
policies still apply. Downloaded scripts may need to be unblocked after review or
signed according to your organization's requirements.

## Design

The interface follows principles from Apple's
[Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/):
clear hierarchy, a restrained sidebar, grouped settings, a single primary action,
and a separate review step. Native file dialogs, labeled controls, keyboard-operable
radio buttons, and resizable, scrolling content support desktop use. Windows uses
Segoe UI; the app does not bundle Apple's fonts or claim to be a native macOS app.

Windows is the verified execution target. Flet is cross-platform, but macOS and
Linux packaging, platform fonts, and generator behavior still need validation
before those platforms are advertised as supported. This initial interface uses a
light theme.

## Verify changes

```powershell
python -m unittest discover -s tests -v
```

The tests create disposable repositories for every catalog type, exercise capability
combinations, Git and virtual environment creation, check literal path handling,
and verify the generated profile wrappers in an isolated profile file. Your real
PowerShell profile is not modified by the tests.

The UI lives in `app.py`; catalog, validation, preview, and execution logic live in
`core.py`. Add catalog descriptions in `playbook.json`, and implement any new
technical scaffolding in the PowerShell generator. The desktop interface and a
future public catalog can share that catalog without duplicating it.
