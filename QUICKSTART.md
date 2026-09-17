# Engineering Playbook v3 Quick Start

## Install commands once

Open PowerShell in this directory and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

& ".\scripts\install_engineering_playbook_profile.ps1" `
  -PlaybookSourcePath (Get-Location).Path

. $PROFILE
```

## Reconcile an existing repository

```powershell
Install-EngineeringPlaybook `
  -RepositoryPath "C:\path\to\ExistingProject" `
  -Reconcile `
  -WhatIf
```

Review the preview, then remove `-WhatIf` to apply it.

## Create a typed repository

```powershell
New-EngineeringRepository `
  -ProjectName "my-data-product" `
  -RepositoryPath "C:\path\to\my-data-product" `
  -ProjectType dbt-python
```

Add optional architecture packs with `-Capabilities`, for example
`-Capabilities ai-governance,service-operations`.
