[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [string]$RepositoryPath,

    [Parameter()]
    [string]$PlaybookSourcePath,

    [Parameter()]
    [ValidateSet('generic','dbt','python','dbt-python','powershell','dotnet','node')]
    [string]$ProjectType,

    [Parameter()]
    [string[]]$Capabilities,

    [Parameter()]
    [switch]$Reconcile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($PlaybookSourcePath)) { $PlaybookSourcePath = Split-Path -Parent $PSScriptRoot }

function Get-FullPath([string]$Path) {
    return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path).Path)
}

function Add-TemplateEntries([System.Collections.ArrayList]$Destination, $Entries) {
    foreach ($entry in @($Entries)) {
        $key = "$($entry.source)|$($entry.target)"
        if (-not ($Destination | Where-Object { $_.Key -eq $key })) {
            [void]$Destination.Add([pscustomobject]@{ Key = $key; Source = $entry.source; Target = $entry.target })
        }
    }
}

$sourceRoot = Get-FullPath $PlaybookSourcePath
if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot 'playbook.json') -PathType Leaf)) {
    $nestedSource = Join-Path $sourceRoot 'engineering-playbook'
    if (Test-Path -LiteralPath (Join-Path $nestedSource 'playbook.json') -PathType Leaf) {
        $sourceRoot = Get-FullPath $nestedSource
    }
}
$repositoryRoot = [System.IO.Path]::GetFullPath($RepositoryPath)
if (-not (Test-Path -LiteralPath $repositoryRoot)) {
    throw "Repository path does not exist: $repositoryRoot"
}

$manifestPath = Join-Path $sourceRoot 'playbook.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Playbook manifest not found: $manifestPath"
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$configPath = Join-Path $repositoryRoot '.engineering-playbook.json'
$projectConfig = $null
if (Test-Path -LiteralPath $configPath -PathType Leaf) {
    $projectConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
}
if (-not $PSBoundParameters.ContainsKey('ProjectType') -or [string]::IsNullOrWhiteSpace($ProjectType)) {
    $ProjectType = if ($null -ne $projectConfig -and $projectConfig.project_type) { $projectConfig.project_type } else { 'generic' }
}
if (-not $PSBoundParameters.ContainsKey('Capabilities') -or $null -eq $Capabilities) {
    $Capabilities = if ($null -ne $projectConfig -and $projectConfig.capabilities) { @($projectConfig.capabilities) } else { @() }
}

$profile = $manifest.repository_profiles.PSObject.Properties[$ProjectType]
if ($null -eq $profile) { throw "Unknown repository profile: $ProjectType" }
foreach ($capability in @($Capabilities)) {
    if ($null -eq $manifest.capability_packs.PSObject.Properties[$capability]) {
        $valid = ($manifest.capability_packs.PSObject.Properties.Name | Sort-Object) -join ', '
        throw "Unknown capability '$capability'. Valid capabilities: $valid"
    }
}

$targetPlaybook = Join-Path $repositoryRoot $manifest.install_directory
$timestamp = Get-Date -Format 'yyyyMMddTHHmmss'
$backupRoot = Join-Path $repositoryRoot ".engineering-playbook-backup\$timestamp"
$installed = @()
$refreshed = @()
$preserved = @()
$review = @()

foreach ($relative in $manifest.immutable_framework_files) {
    $source = Join-Path $sourceRoot $relative
    $target = Join-Path $targetPlaybook $relative
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Manifest source is missing: $source" }
    $targetParent = Split-Path -Parent $target
    if (-not (Test-Path -LiteralPath $targetParent) -and $PSCmdlet.ShouldProcess($targetParent, 'Create framework directory')) {
        New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
    }
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
        $targetHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
        if ($sourceHash -eq $targetHash) { $preserved += $target; continue }
        if (-not $Reconcile) { $review += "$target (framework version differs; rerun with -Reconcile)"; continue }
        $backup = Join-Path $backupRoot (Join-Path $manifest.install_directory $relative)
        $backupParent = Split-Path -Parent $backup
        if ($PSCmdlet.ShouldProcess($target, 'Back up and refresh immutable framework file')) {
            New-Item -ItemType Directory -Path $backupParent -Force | Out-Null
            Copy-Item -LiteralPath $target -Destination $backup -Force
            Copy-Item -LiteralPath $source -Destination $target -Force
            $refreshed += $target
        }
    } elseif ($PSCmdlet.ShouldProcess($target, 'Install missing immutable framework file')) {
        Copy-Item -LiteralPath $source -Destination $target -Force
        $installed += $target
    }
}

$selectedTemplates = [System.Collections.ArrayList]::new()
Add-TemplateEntries $selectedTemplates $manifest.common_project_templates
Add-TemplateEntries $selectedTemplates $profile.Value.templates
foreach ($capability in @($Capabilities)) {
    Add-TemplateEntries $selectedTemplates $manifest.capability_packs.PSObject.Properties[$capability].Value.templates
}
foreach ($entry in $selectedTemplates) {
    $source = Join-Path $sourceRoot $entry.Source
    $target = Join-Path $repositoryRoot $entry.Target
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Template source is missing: $source" }
    $parent = Split-Path -Parent $target
    if (-not (Test-Path -LiteralPath $parent) -and $PSCmdlet.ShouldProcess($parent, 'Create project documentation directory')) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        $preserved += $target
        $review += "$target (existing project-owned document preserved; reconcile content manually)"
    } elseif ($PSCmdlet.ShouldProcess($target, 'Install selected project-document template')) {
        Copy-Item -LiteralPath $source -Destination $target
        $installed += $target
    }
}

# AGENTS.md is project-owned: compose new entry points, preserve existing rules.
$agentTemplates = @($manifest.agent_instruction_templates)
foreach ($capability in @($Capabilities)) {
    $pack = $manifest.capability_packs.PSObject.Properties[$capability].Value
    if ($pack.PSObject.Properties['agent_instruction_templates']) {
        $agentTemplates += @($pack.agent_instruction_templates)
    }
}
$agentTarget = Join-Path $repositoryRoot 'AGENTS.md'
if (Test-Path -LiteralPath $agentTarget) {
    $preserved += $agentTarget
    $review += "$agentTarget (preserved; reconcile governance blocks from $($agentTemplates -join ', '))"
} elseif ($PSCmdlet.ShouldProcess($agentTarget, 'Install governance startup instructions')) {
    $agentContent = (@($agentTemplates | ForEach-Object {
        Get-Content -LiteralPath (Join-Path $sourceRoot $_) -Raw -Encoding UTF8
    }) -join "`n")
    [System.IO.File]::WriteAllText($agentTarget, $agentContent, [System.Text.UTF8Encoding]::new($false))
    $installed += $agentTarget
}

Write-Host ''
Write-Host "Engineering Playbook $($manifest.playbook_version) reconciliation summary" -ForegroundColor Cyan
Write-Host "Profile: $ProjectType; Capabilities: $(if (@($Capabilities).Length -gt 0) { @($Capabilities) -join ', ' } else { 'none' })" -ForegroundColor Cyan
Write-Host ('-' * 68)
$installed | ForEach-Object { Write-Host "INSTALLED  $_" -ForegroundColor Green }
$refreshed | ForEach-Object { Write-Host "REFRESHED  $_" -ForegroundColor Green }
$preserved | ForEach-Object { Write-Host "PRESERVED  $_" -ForegroundColor DarkGray }
$review | ForEach-Object { Write-Host "REVIEW     $_" -ForegroundColor Yellow }
if ($refreshed.Count -gt 0) { Write-Host "BACKUP     $backupRoot" -ForegroundColor Cyan }
Write-Host ''
Write-Host 'No project-owned file was overwritten.' -ForegroundColor Cyan
