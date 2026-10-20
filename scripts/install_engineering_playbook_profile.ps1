[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [string]$PlaybookSourcePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$resolvedSource = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $PlaybookSourcePath).Path)
if (Test-Path -LiteralPath (Join-Path $resolvedSource 'playbook.json') -PathType Leaf) {
    $source = $resolvedSource
} elseif (Test-Path -LiteralPath (Join-Path $resolvedSource 'engineering-playbook\playbook.json') -PathType Leaf) {
    $source = Join-Path $resolvedSource 'engineering-playbook'
} else {
    throw "Playbook source does not contain playbook.json: $resolvedSource"
}
$installScript = Join-Path $source 'scripts\install_engineering_playbook.ps1'
$newScript = Join-Path $source 'scripts\new_engineering_repository.ps1'
if (-not (Test-Path -LiteralPath $installScript)) { throw "Missing installer: $installScript" }
if (-not (Test-Path -LiteralPath $newScript)) { throw "Missing repository creator: $newScript" }

$profileParent = Split-Path -Parent $PROFILE

$begin = '# BEGIN ENGINEERING PLAYBOOK V3'
$end = '# END ENGINEERING PLAYBOOK V3'
$existing = if (Test-Path -LiteralPath $PROFILE -PathType Leaf) {
    Get-Content -LiteralPath $PROFILE -Raw
} else {
    ''
}
if ($null -eq $existing) { $existing = '' }
$escapedSource = $source.Replace("'", "''")
$block = @"
$begin
`$script:EngineeringPlaybookSourcePath = '$escapedSource'
function Install-EngineeringPlaybook {
    [CmdletBinding(SupportsShouldProcess=`$true)]
    param(
        [Parameter(Mandatory=`$true)][string]`$RepositoryPath,
        [ValidateSet('generic','dbt','python','dbt-python','powershell','dotnet','node')][string]`$ProjectType,
        [ValidateSet('ai-governance','service-operations','operator-application','document-processing','metis-governance')][string[]]`$Capabilities,
        [switch]`$Reconcile
    )
    `$parameters = @{
        RepositoryPath = `$RepositoryPath
        PlaybookSourcePath = `$script:EngineeringPlaybookSourcePath
        Reconcile = `$Reconcile
        WhatIf = `$WhatIfPreference
    }
    if (`$PSBoundParameters.ContainsKey('ProjectType')) { `$parameters.ProjectType = `$ProjectType }
    if (`$PSBoundParameters.ContainsKey('Capabilities')) { `$parameters.Capabilities = `$Capabilities }
    & (Join-Path `$script:EngineeringPlaybookSourcePath 'scripts\install_engineering_playbook.ps1') @parameters
}
function New-EngineeringRepository {
    [CmdletBinding(SupportsShouldProcess=`$true)]
    param(
        [Parameter(Mandatory=`$true)][string]`$ProjectName,
        [Parameter(Mandatory=`$true)][string]`$RepositoryPath,
        [ValidateSet('generic','dbt','python','dbt-python','powershell','dotnet','node')][string]`$ProjectType = 'generic',
        [ValidateSet('ai-governance','service-operations','operator-application','document-processing','metis-governance')][string[]]`$Capabilities = @(),
        [switch]`$CreateVenv,
        [switch]`$NoGit
    )
    `$parameters = @{
        ProjectName = `$ProjectName
        RepositoryPath = `$RepositoryPath
        ProjectType = `$ProjectType
        Capabilities = `$Capabilities
        PlaybookSourcePath = `$script:EngineeringPlaybookSourcePath
        CreateVenv = `$CreateVenv
        NoGit = `$NoGit
        WhatIf = `$WhatIfPreference
    }
    & (Join-Path `$script:EngineeringPlaybookSourcePath 'scripts\new_engineering_repository.ps1') @parameters
}
$end
"@

$pattern = [regex]::Escape($begin) + '.*?' + [regex]::Escape($end)
if ($existing -match $pattern) {
    $updated = [regex]::Replace($existing, $pattern, $block, [System.Text.RegularExpressions.RegexOptions]::Singleline)
} else {
    $updated = $existing.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $block + [Environment]::NewLine
}
if ($PSCmdlet.ShouldProcess($PROFILE, 'Install Engineering Playbook commands')) {
    if (-not (Test-Path -LiteralPath $profileParent)) {
        New-Item -ItemType Directory -Path $profileParent -Force | Out-Null
    }
    Set-Content -LiteralPath $PROFILE -Value $updated -Encoding utf8
    Write-Host "Installed Engineering Playbook commands in $PROFILE" -ForegroundColor Green
    Write-Host 'Reload with: . $PROFILE' -ForegroundColor Cyan
}
