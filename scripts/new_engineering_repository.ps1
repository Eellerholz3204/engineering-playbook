[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,

    [Parameter(Mandatory=$true)]
    [string]$RepositoryPath,

    [Parameter()]
    [ValidateSet('generic','dbt','python','dbt-python','powershell','dotnet','node')]
    [string]$ProjectType = 'generic',

    [Parameter()]
    [ValidateSet('ai-governance','service-operations','operator-application','document-processing')]
    [string[]]$Capabilities = @(),

    [Parameter()]
    [string]$PlaybookSourcePath,

    [Parameter()]
    [switch]$CreateVenv,

    [Parameter()]
    [switch]$NoGit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($ProjectName -notmatch '^[A-Za-z][A-Za-z0-9_-]{0,79}$' -or $ProjectName -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$') {
    throw 'Use a project name starting with a letter, followed by letters, numbers, hyphens or underscores (up to 80 characters; no reserved Windows names).'
}
if ([string]::IsNullOrWhiteSpace($RepositoryPath)) { throw 'RepositoryPath must not be empty.' }
if ($CreateVenv) {
    if ($ProjectType -notin @('python','dbt-python')) { throw '-CreateVenv is only valid for python and dbt-python projects.' }
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python was not found on PATH.' }
}
if (-not $NoGit -and -not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git was not found on PATH. Install Git or use -NoGit.' }
if ([string]::IsNullOrWhiteSpace($PlaybookSourcePath)) { $PlaybookSourcePath = Split-Path -Parent $PSScriptRoot }
$root = [System.IO.Path]::GetFullPath($RepositoryPath)
if ([System.IO.Path]::GetPathRoot($root) -eq $root) { throw 'Choose a project folder, not a drive root.' }
if (-not (Test-Path -LiteralPath $root)) {
    if ($PSCmdlet.ShouldProcess($root, 'Create repository directory')) {
        New-Item -ItemType Directory -Path $root -Force | Out-Null
    }
}
if (-not (Test-Path -LiteralPath $root)) { return }
if ((Get-ChildItem -LiteralPath $root -Force | Measure-Object).Count -gt 0) {
    throw 'New-EngineeringRepository requires an empty target directory. Use Install-EngineeringPlaybook for an existing repository.'
}

& (Join-Path $PSScriptRoot 'install_engineering_playbook.ps1') `
    -RepositoryPath $root `
    -PlaybookSourcePath $PlaybookSourcePath `
    -ProjectType $ProjectType `
    -Capabilities $Capabilities `
    -WhatIf:$WhatIfPreference

if ($WhatIfPreference) { return }

$config = [ordered]@{
    schema_version = 1
    project_name = $ProjectName
    project_type = $ProjectType
    capabilities = @($Capabilities)
    playbook_version = (Get-Content -LiteralPath (Join-Path $PlaybookSourcePath 'VERSION') -Raw).Trim()
}
$config | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $root '.engineering-playbook.json') -Encoding utf8

$gitignore = @('.engineering-playbook-backup/', '.env', '*.log')
if ($ProjectType -in @('python','dbt-python')) { $gitignore += @('.venv/', '__pycache__/', '*.py[cod]', '.pytest_cache/', '.ruff_cache/') }
if ($ProjectType -in @('dbt','dbt-python')) { $gitignore += @('target/', 'dbt_packages/', 'logs/', '.user.yml') }
$gitignore | Set-Content -LiteralPath (Join-Path $root '.gitignore') -Encoding utf8

if ($ProjectType -in @('dbt','dbt-python')) {
    foreach ($directory in @('models','tests','macros','seeds','snapshots')) {
        $path = Join-Path $root $directory
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        New-Item -ItemType File -Path (Join-Path $path '.gitkeep') -Force | Out-Null
    }
    $dbtName = ($ProjectName -replace '[^A-Za-z0-9_]', '_')
    @"
name: '$dbtName'
version: '0.1.0'
config-version: 2
profile: '$dbtName'
model-paths: ['models']
test-paths: ['tests']
seed-paths: ['seeds']
macro-paths: ['macros']
snapshot-paths: ['snapshots']
clean-targets: ['target', 'dbt_packages']
"@ | Set-Content -LiteralPath (Join-Path $root 'dbt_project.yml') -Encoding utf8
}

if ($ProjectType -in @('python','dbt-python')) {
    $packageName = ($ProjectName -replace '-', '_') -replace '[^A-Za-z0-9_]', ''
    New-Item -ItemType Directory -Path (Join-Path $root "src\$packageName") -Force | Out-Null
    New-Item -ItemType File -Path (Join-Path $root "src\$packageName\__init__.py") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $root 'tests') -Force | Out-Null
    @"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "$ProjectName"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.pytest.ini_options]
testpaths = ["tests"]
"@ | Set-Content -LiteralPath (Join-Path $root 'pyproject.toml') -Encoding utf8
}

if (-not $NoGit) {
    if ($PSCmdlet.ShouldProcess($root, 'Initialize Git repository')) {
        git -C $root init | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Git initialization failed with exit code $LASTEXITCODE." }
    }
}
if ($CreateVenv) {
    if ($PSCmdlet.ShouldProcess((Join-Path $root '.venv'), 'Create Python virtual environment')) {
        python -m venv (Join-Path $root '.venv')
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed with exit code $LASTEXITCODE." }
    }
}
Write-Host "Created repository scaffold for $ProjectName at $root" -ForegroundColor Green
Write-Host "Profile: $ProjectType; Capabilities: $(if (@($Capabilities).Count) { $Capabilities -join ', ' } else { 'none' })" -ForegroundColor Cyan
Write-Host 'Review and replace project-document template placeholders before implementation.' -ForegroundColor Yellow
