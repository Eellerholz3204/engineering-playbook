[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$InstallerPath)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$qaRoot = [System.IO.Path]::GetFullPath((Join-Path $root '.builder-qa'))
$testRoot = [System.IO.Path]::GetFullPath((Join-Path $qaRoot ('installer-' + [guid]::NewGuid().ToString('N'))))
if (-not $testRoot.StartsWith($qaRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe installer test path.' }
$uninstallKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{388798AF-7865-4545-8A97-50E17BE5F0A0}_is1'
if (Test-Path $uninstallKey) { throw 'Repository Builder is already installed. Run this installer test in a disposable account.' }
$installer = (Resolve-Path -LiteralPath $InstallerPath).Path
$app = Join-Path $testRoot 'Installed app'
$group = 'Repository Builder QA ' + [guid]::NewGuid().ToString('N')
$report = Join-Path $testRoot 'self-test.json'
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
$savedConfig = Join-Path $testRoot 'saved-configuration.json'
Set-Content -LiteralPath $savedConfig -Value '{"preserve":true}' -Encoding ascii
$installed = $false
try {
    foreach ($pass in @(1, 2)) {
        $process = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/SP-','/NORESTART',('/DIR="' + $app + '"'),('/GROUP="' + $group + '"'),('/LOG="' + (Join-Path $testRoot "install-$pass.log") + '"')) -WindowStyle Hidden -Wait -PassThru
        if ($process.ExitCode -ne 0) { throw "Installer pass $pass failed: $($process.ExitCode)" }
        $installed = $true
        if (-not (Test-Path -LiteralPath (Join-Path $app 'Repository Builder.exe'))) { throw 'Installed launcher is missing.' }
        $process = Start-Process -FilePath (Join-Path $app 'Repository Builder.exe') -ArgumentList @('--self-test', ('"' + $report + '"')) -WindowStyle Hidden -Wait -PassThru
        if ($process.ExitCode -ne 0) { throw "Installed launcher self-test failed: $($process.ExitCode)" }
        $result = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
        if (-not $result.success -or -not $result.resource_root.StartsWith($app)) { throw 'Installed app used incorrect resources.' }
    }
    $shortcutPath = Join-Path ([Environment]::GetFolderPath('Programs')) ($group + '\Repository Builder.lnk')
    $wsh = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut($shortcutPath)
    if ($shortcut.TargetPath -ne (Join-Path $app 'Repository Builder.exe')) { throw 'Installed shortcut has an incorrect target.' }
    $playbook = Get-Content -LiteralPath (Join-Path $app 'playbook\playbook.json') -Raw | ConvertFrom-Json
    $config = @{
        schema_version = 1; project_name = 'preserved-project'; repository_path = (Join-Path $testRoot 'preserved-project')
        project_type = 'generic'; capabilities = @(); create_venv = $false; initialize_git = $false; playbook_version = $playbook.playbook_version
    }
    $configPath = Join-Path $testRoot 'creation.json'
    $config | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding utf8
    & powershell -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -File (Join-Path $app 'playbook\scripts\create_repository_from_config.ps1') -ConfigurationPath $configPath | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Installed playbook could not create a project.' }
} finally {
    if ($installed) {
        $uninstaller = [System.IO.Path]::GetFullPath((Join-Path $app 'unins000.exe'))
        if (-not $uninstaller.StartsWith($testRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe uninstaller path.' }
        $process = Start-Process -FilePath $uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/LOG="' + (Join-Path $testRoot 'uninstall.log') + '"')) -WindowStyle Hidden -Wait -PassThru
        if ($process.ExitCode -ne 0) { throw "Uninstall failed: $($process.ExitCode)" }
    }
}
if (Test-Path -LiteralPath (Join-Path $app 'Repository Builder.exe')) { throw 'Uninstall left the launcher installed.' }
if (-not (Test-Path -LiteralPath $savedConfig)) { throw 'Saved configuration was removed.' }
if (-not (Test-Path -LiteralPath (Join-Path $testRoot 'preserved-project\.engineering-playbook.json'))) { throw 'Generated project was removed.' }
Write-Output "PASS: install, reinstall, shortcut, packaged launch, uninstall, and project/configuration preservation. Evidence: $testRoot"
