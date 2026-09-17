#ifndef AppVersion
  #error AppVersion must be supplied by the release builder.
#endif
#ifndef SourceDirectory
  #error SourceDirectory must be supplied by the release builder.
#endif
#ifndef OutputDirectory
  #error OutputDirectory must be supplied by the release builder.
#endif

[Setup]
AppId={{388798AF-7865-4545-8A97-50E17BE5F0A0}
AppName=Repository Builder
AppVersion={#AppVersion}
AppPublisher=Engineering Playbook
DefaultDirName={localappdata}\Programs\Engineering Playbook\Repository Builder
DefaultGroupName=Engineering Playbook
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir={#OutputDirectory}
OutputBaseFilename=RepositoryBuilder-{#AppVersion}-windows-x64-setup
SetupIconFile={#SourceDirectory}\playbook\repository_builder\assets\repository-builder.ico
UninstallDisplayIcon={app}\Repository Builder.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=no
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes
VersionInfoVersion={#AppVersion}.0

[Files]
Source: "{#SourceDirectory}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Repository Builder"; Filename: "{app}\Repository Builder.exe"; WorkingDir: "{app}"; AppUserModelID: "EngineeringPlaybook.RepositoryBuilder"

[Run]
Filename: "{app}\Repository Builder.exe"; Description: "Open Repository Builder"; Flags: nowait postinstall skipifsilent unchecked

; Project repositories, saved configurations and per-user logs are outside {app}.
; No wildcard uninstall deletion is used: only installed files are removed.
