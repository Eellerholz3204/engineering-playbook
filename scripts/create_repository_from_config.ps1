[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)][string]$ConfigurationPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$config = Get-Content -LiteralPath $ConfigurationPath -Raw -Encoding UTF8 | ConvertFrom-Json
$source = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $source 'playbook.json') -Raw | ConvertFrom-Json
$required = @('schema_version','project_name','repository_path','project_type','capabilities','create_venv','initialize_git','playbook_version')
if ($null -eq $config -or $config -isnot [pscustomobject]) { throw 'Configuration must be a JSON object.' }
$names = @($config.PSObject.Properties.Name)
foreach ($name in $required) { if ($name -notin $names) { throw "Missing configuration field: $name" } }
foreach ($name in $names) { if ($name -notin $required) { throw "Unknown configuration field: $name" } }
# Windows PowerShell parses JSON integers as Int32; PowerShell 7 uses Int64.
if (($config.schema_version -isnot [int] -and $config.schema_version -isnot [long]) -or $config.schema_version -ne 1) { throw 'Unsupported configuration version.' }
if ($config.playbook_version -ne $manifest.playbook_version) { throw "Configuration requires playbook $($config.playbook_version); this copy is $($manifest.playbook_version)." }
foreach ($name in @('project_name','repository_path','project_type','playbook_version')) {
    if ($config.$name -isnot [string] -or [string]::IsNullOrWhiteSpace($config.$name)) { throw "Invalid configuration field: $name" }
}
if ($config.create_venv -isnot [bool] -or $config.initialize_git -isnot [bool]) { throw 'Environment and Git options must be JSON booleans.' }
if ($config.capabilities -isnot [array]) { throw 'Capabilities must be a JSON array.' }
foreach ($capability in $config.capabilities) {
    if ($capability -isnot [string] -or $null -eq $manifest.capability_packs.PSObject.Properties[$capability]) { throw "Unknown capability: $capability" }
}
if (@($config.capabilities | Select-Object -Unique).Count -ne $config.capabilities.Count) { throw 'Capabilities must not be repeated.' }
if ($null -eq $manifest.repository_profiles.PSObject.Properties[$config.project_type]) { throw 'Unknown project type.' }
$parameters = @{
    ProjectName = $config.project_name
    RepositoryPath = $config.repository_path
    ProjectType = $config.project_type
    Capabilities = [string[]]$config.capabilities
    PlaybookSourcePath = $source
    CreateVenv = $config.create_venv
    NoGit = -not $config.initialize_git
    WhatIf = $WhatIfPreference
}
& (Join-Path $PSScriptRoot 'new_engineering_repository.ps1') @parameters
