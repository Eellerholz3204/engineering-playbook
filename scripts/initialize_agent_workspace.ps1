[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [string]$RepositoryPath,

    [Parameter()]
    [string]$TaskId = 'default',

    [Parameter()]
    [switch]$ResolveOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$isWindowsPlatform = [System.IO.Path]::DirectorySeparatorChar -eq '\'
function Test-AbsolutePath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path) -or -not [System.IO.Path]::IsPathRooted($Path)) { return $false }
    # IsPathRooted alone also accepts drive-relative C:folder and \folder on Windows.
    if ($isWindowsPlatform) { return $Path -match '^(?:[A-Za-z]:[\\/]|\\\\[^\\/]+[\\/][^\\/]+(?:[\\/]|$))' }
    return $true
}
if (-not (Test-AbsolutePath $RepositoryPath)) {
    throw 'RepositoryPath must be an absolute path.'
}
if ($TaskId -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$' -or $TaskId -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$') {
    throw 'TaskId must contain only letters, numbers, hyphens or underscores (up to 80 characters; no reserved Windows names).'
}
$repositoryRoot = [System.IO.Path]::GetFullPath($RepositoryPath).TrimEnd([char[]]'\/')
if ([string]::IsNullOrEmpty($repositoryRoot) -or [System.IO.Path]::GetPathRoot($RepositoryPath).TrimEnd([char[]]'\/') -eq $repositoryRoot) {
    throw 'Choose a repository folder, not a filesystem root.'
}
$workspaceBase = $env:ENGINEERING_PLAYBOOK_SCRATCH_ROOT
if ([string]::IsNullOrWhiteSpace($workspaceBase)) {
    $localData = [Environment]::GetFolderPath('LocalApplicationData')
    if ([string]::IsNullOrWhiteSpace($localData)) { throw 'Set ENGINEERING_PLAYBOOK_SCRATCH_ROOT to an external absolute directory.' }
    $workspaceBase = Join-Path $localData 'AgentWorkspaces'
}
if (-not (Test-AbsolutePath $workspaceBase)) { throw 'ENGINEERING_PLAYBOOK_SCRATCH_ROOT must be an absolute path.' }
$workspaceBase = [System.IO.Path]::GetFullPath($workspaceBase)
$comparison = if ($isWindowsPlatform) { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
$identity = if ($isWindowsPlatform) { $repositoryRoot.ToLowerInvariant() } else { $repositoryRoot }
$hasher = [System.Security.Cryptography.SHA256]::Create()
try {
    $digest = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($identity))).Replace('-', '').ToLowerInvariant()
} finally { $hasher.Dispose() }
$label = ([System.IO.Path]::GetFileName($identity) -replace '[^A-Za-z0-9_-]', '_')
if ($label.Length -gt 40) { $label = $label.Substring(0, 40) }
$workspace = Join-Path (Join-Path $workspaceBase "$label-$($digest.Substring(0, 16))") $TaskId
$separator = [System.IO.Path]::DirectorySeparatorChar
if ($workspace.Equals($repositoryRoot, $comparison) -or
    $workspace.StartsWith($repositoryRoot + $separator, $comparison) -or
    $repositoryRoot.StartsWith($workspace + $separator, $comparison)) {
    throw 'Agent workspace must be outside the repository, without overlapping it.'
}
# A redirected workspace could silently put scratch files back inside a checkout.
$ancestor = $workspace
while (-not [string]::IsNullOrEmpty($ancestor)) {
    if (Test-Path -LiteralPath $ancestor) {
        $item = Get-Item -LiteralPath $ancestor -Force
        if (-not $item.PSIsContainer -or ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            throw "Agent workspace requires ordinary directories, not files or directory links: $ancestor"
        }
    }
    $ancestor = [System.IO.Path]::GetDirectoryName($ancestor)
}
if (-not $ResolveOnly -and $PSCmdlet.ShouldProcess($workspace, 'Create external agent task workspace')) {
    [void][System.IO.Directory]::CreateDirectory($workspace)
}
# Emit only the path on the success stream, so agents can capture it directly.
Write-Output $workspace
