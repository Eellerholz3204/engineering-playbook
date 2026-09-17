[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$localPython = Join-Path $root '.venv\Scripts\python.exe'
$python = if (Test-Path -LiteralPath $localPython) { $localPython } else { 'python' }
Push-Location $root
try {
    & $python -m repository_builder
    if ($LASTEXITCODE -ne 0) { throw "Repository Builder exited with code $LASTEXITCODE. See the error above." }
} finally {
    Pop-Location
}
