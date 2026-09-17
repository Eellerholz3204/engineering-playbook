# Engineering Playbook v3.2.1

Engineering Playbook v3 is a reusable software architecture and repository-governance framework. It is installed into each governed repository as a dedicated root-level `engineering-playbook/` directory.

## Governing rule

> The Engineering Playbook governs the repository but does not describe the project.

Framework files live under `engineering-playbook/`. Project-specific architecture, status, milestones, and decisions live under `docs/`.

## Download Repository Builder for Windows

For normal use, download the installer or portable ZIP from
[GitHub Releases](https://github.com/Eellerholz3204/engineering-playbook/releases).
The desktop app includes Python, Flet, and a specific playbook version. Choose the
installer for a Start menu shortcut and uninstall support, or extract the entire
portable ZIP and open `Repository Builder.exe`.

PowerShell is required. Git and an external Python installation are needed only
for Git initialization and project virtual environments respectively. Initial
downloads are unsigned previews for Windows x64. See
[distribution details](packaging/README.md) and [contributor setup](CONTRIBUTING.md).

## Repository layout

```text
<ProjectRoot>/
  engineering-playbook/        # Playbook-managed framework
  docs/                        # Project-owned documentation
  scripts/                     # Project-owned scripts
  source code and configuration
```

## One-time workstation setup

Run this once to add the reusable commands to your PowerShell profile:

```powershell
& "C:\path\to\engineering-playbook-v3\scripts\install_engineering_playbook_profile.ps1" `
  -PlaybookSourcePath "C:\path\to\engineering-playbook-v3"
```

Restart PowerShell or reload the profile:

```powershell
. $PROFILE
```

This installs commands into your PowerShell profile. It does **not** modify a repository.

## Create a new repository

The desktop **Repository Builder** lets you browse repository types and optional
capabilities, preview the included files, and create a repository without assembling
a PowerShell command. It uses the catalog in `playbook.json` and the same creation
script shown below.

From this directory, install the desktop dependencies once:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-builder.txt
```

Launch the app:

```powershell
.\.venv\Scripts\python.exe -m repository_builder
```

For a Start menu shortcut with the app icon, run once:

```powershell
.\scripts\install_repository_builder_shortcut.ps1
```

Then search Start for **Repository Builder** and right-click it to pin it to Start
or the taskbar. The shortcut opens the app without a terminal window.

Choose **Project → Catalog → Review**, then **Create repository**. You can save a
JSON configuration for reuse or copy the equivalent PowerShell command. No profile
installation is required for the app. See [the builder guide](repository_builder/README.md)
for prerequisites, configuration automation, and design notes.

For command-line creation after the optional workstation setup above:

```powershell
New-EngineeringRepository `
  -ProjectName "MyProject" `
  -RepositoryPath "C:\Users\me\source\repos\MyProject" `
  -ProjectType dbt-python `
  -Capabilities service-operations `
  -CreateVenv
```

Repository types are `generic`, `dbt`, `python`, `dbt-python`, `powershell`,
`dotnet`, and `node`. Types select technical scaffolding and project documents.

Optional capabilities are `ai-governance`, `service-operations`,
`operator-application`, and `document-processing`. Architecture patterns remain a
catalog until a profile or capability selects the corresponding project documents.

Without installing the profile commands, call `scripts/new_engineering_repository.ps1`
directly with the same parameters. Python and dbt types add language-specific
scaffolding; the other types currently install the core framework and common project
documents only.

## Controlled milestone continuation

Agents close, verify, and document every milestone. They may continue into the next
documented milestone without ending the work session when it is unambiguous, remains
inside standing authorization, and does not require human review. Review and authorization
gates always stop continuation; a configured email channel may be used to request review.
When connected Gmail is selected, the agent sends the request to the authenticated account
and may resume only after an unambiguous reply in the same milestone-specific thread is
recorded as review evidence.

## Install or reconcile an existing repository

Preview first:

```powershell
Install-EngineeringPlaybook `
  -RepositoryPath "C:\Users\me\source\repos\ExistingProject" `
  -Reconcile `
  -WhatIf
```

Apply reconciliation:

```powershell
Install-EngineeringPlaybook `
  -RepositoryPath "C:\Users\me\source\repos\ExistingProject" `
  -Reconcile
```

Reconciliation:

- installs missing framework files;
- refreshes immutable playbook-managed files;
- installs missing project-document templates;
- preserves existing project documentation;
- reports files requiring human review;
- backs up replaced framework files;
- never rewrites project source code or project-owned scripts.

See `scripts/README.md` for command details.
