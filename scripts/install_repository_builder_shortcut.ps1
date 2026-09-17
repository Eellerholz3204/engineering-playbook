[CmdletBinding(SupportsShouldProcess=$true)]
param(
    # Defaults to the current user's Start menu. A custom directory is useful for portable shortcuts.
    [string]$ShortcutDirectory,
    # Use an already-built launcher, for example while the app is open.
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Create the local .venv and install requirements-builder.txt first. See README.md.' }
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $compiler)) { throw 'The Windows .NET Framework C# compiler was not found.' }
$launchDirectory = Join-Path $root '.launcher'
$launcher = Join-Path $launchDirectory 'Repository Builder.exe'
$source = Join-Path $root 'repository_builder\windows\Launcher.cs'
$icon = Join-Path $root 'repository_builder\assets\repository-builder.ico'
if (-not (Test-Path -LiteralPath $icon)) { & (Join-Path $PSScriptRoot 'build_repository_builder_icon.ps1') }
if ([string]::IsNullOrWhiteSpace($ShortcutDirectory)) {
    $ShortcutDirectory = Join-Path ([Environment]::GetFolderPath('Programs')) 'Engineering Playbook'
}
$ShortcutDirectory = [System.IO.Path]::GetFullPath($ShortcutDirectory)
$shortcut = Join-Path $ShortcutDirectory 'Repository Builder.lnk'
if ($SkipBuild -and -not (Test-Path -LiteralPath $launcher)) { throw 'No launcher exists yet. Run without -SkipBuild first.' }
if (-not $SkipBuild -and $PSCmdlet.ShouldProcess($launcher, 'Build the windowless Repository Builder launcher')) {
    New-Item -ItemType Directory -Path $launchDirectory -Force | Out-Null
    & $compiler /nologo /target:winexe /platform:x64 /codepage:65001 "/win32icon:$icon" "/out:$launcher" /reference:System.Windows.Forms.dll $source
    if ($LASTEXITCODE -ne 0) { throw 'Launcher compilation failed. Close Repository Builder before reinstalling the shortcut.' }
}
if ($PSCmdlet.ShouldProcess($shortcut, 'Install Repository Builder shortcut')) {
    New-Item -ItemType Directory -Path $ShortcutDirectory -Force | Out-Null
    $process = Start-Process -FilePath $launcher -ArgumentList @('--shortcut', ('"' + $shortcut + '"')) -Wait -PassThru -WindowStyle Hidden
    if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $shortcut)) { throw 'Shortcut installation failed.' }
    Write-Output "Installed: $shortcut"
    Write-Output 'Find Repository Builder in Start, then right-click to pin it to Start or the taskbar.'
}
