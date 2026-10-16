# Engineering Playbook Scripts

These scripts are already in the Engineering Playbook directory. Do not copy them into this folder.

## One-time workstation setup

From the extracted Engineering Playbook root, run:

```powershell
& ".\scripts\install_engineering_playbook_profile.ps1" `
  -PlaybookSourcePath (Get-Location).Path

. $PROFILE
```

This installs two reusable PowerShell commands in your profile. It does not change a project.

## Existing repository

Preview:

```powershell
Install-EngineeringPlaybook `
  -RepositoryPath "C:\path\to\ExistingProject" `
  -Reconcile `
  -WhatIf
```

Apply:

```powershell
Install-EngineeringPlaybook `
  -RepositoryPath "C:\Users\me\source\repos\ExistingProject" `
  -Reconcile
```

Reconciliation refreshes framework-owned files under `engineering-playbook\`, creates backups before replacement, installs missing project-document templates, and preserves existing project-owned documents.

## New repository

To add the desktop app to your Start menu after setting up its `.venv`, run
`install_repository_builder_shortcut.ps1`. The resulting **Repository Builder**
shortcut can be pinned to Start or the taskbar and launches without a console.

For guided creation, run `start_repository_builder.ps1` after installing
`requirements-builder.txt` in a local `.venv`. See
[`repository_builder/README.md`](../repository_builder/README.md).

Saved app configurations can also run directly:

```powershell
.\scripts\create_repository_from_config.ps1 -ConfigurationPath .\example.repository.json
```

```powershell
New-EngineeringRepository `
  -ProjectName "MyProject" `
  -RepositoryPath "C:\Users\me\source\repos\MyProject" `
  -ProjectType python `
  -CreateVenv
```

There is no broad `-Force` mode for existing repositories.

## Agent scratch space

New repository creation initializes an external workspace and prints its path.
From a generated repository, create/resume a task folder with:

```powershell
$agentScratch = & ./engineering-playbook/scripts/initialize_agent_workspace.ps1 `
  -RepositoryPath (Get-Location).Path -TaskId 'task-123'
```

From this source repository, use `./scripts/initialize_agent_workspace.ps1`.
The helper outputs the path; `-ResolveOnly` resolves and validates without writing,
and `-WhatIf` previews creation. Repeated calls preserve existing contents. The
default TaskId is `default`; choose separate IDs for concurrent tasks. IDs accept
letters, numbers, hyphens and underscores, at most 80 characters, excluding Windows
reserved names.

Windows defaults to `%LOCALAPPDATA%\AgentWorkspaces\<checkout-name>-<path-hash>\<task-id>`.
`ENGINEERING_PLAYBOOK_SCRATCH_ROOT` may override the base with an external absolute
directory. Overlapping checkout locations and directory links in the scratch path
are rejected. No path is stored in the repository or saved Builder configuration.
Fresh clones can invoke the helper directly. Moving a checkout gives it a new
workspace; old scratch is preserved. There is no automatic deletion.

Existing-repository installation installs the helper but preserves AGENTS.md and
project documents. Reconcile the reported instruction block, then initialize scratch
when needed. Ownership, promotion and retention rules live in `GOVERNANCE_CONTEXT.md`.

## Additional creation examples

```powershell
New-EngineeringRepository `
  -ProjectName "my-data-product" `
  -RepositoryPath "C:\path\to\my-data-product" `
  -ProjectType dbt-python `
  -Capabilities service-operations `
  -CreateVenv
```

`ProjectType` selects technical scaffolding and profile documents. `Capabilities` adds
optional architecture documents. Git is initialized unless `-NoGit` is supplied; no
commit or remote is created.

The profile installer uses parameter hashtables to forward arguments. If a profile
installed by an earlier version prompts for parameters you already supplied, rerun
the workstation setup and reload the profile. You can also call
`new_engineering_repository.ps1` directly without installing the profile commands.
