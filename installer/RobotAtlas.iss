; RobotAtlas — Inno Setup Script
; Packages the PyInstaller dist folder into a professional Windows installer.
;
; Prerequisites:
;   1. Build with PyInstaller first:  pyinstaller ../installer/robotatlas.spec
;   2. Then compile this script:      ISCC RobotAtlas.iss
;
; Output: installer/Output/RobotAtlasSetup.exe

#define MyAppName      "RobotAtlas"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "RobotAtlas"
#define MyAppExeName   "RobotAtlas.exe"
#define MyAppURL       "https://github.com/robotatlas"

; Path to the PyInstaller dist output (relative to this .iss file)
#define DistDir        "..\ia-clases\dist\RobotAtlas"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Output installer to installer/Output/
OutputDir=Output
OutputBaseFilename=RobotAtlasSetup
; Compression
Compression=lzma2/ultra
SolidCompression=yes
LZMAUseSeparateProcess=yes
; Require admin for Program Files install
PrivilegesRequired=admin
; Minimum Windows 10
MinVersion=10.0
; Uninstall
UninstallDisplayName={#MyAppName}
; Architecture (x64 only)
ArchitecturesAllowed=x64compatible
; Wizard
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable
Source: "{#DistDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; _internal folder (all Python runtime, libraries, bundled data)
Source: "{#DistDir}\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; Note: demos/ and sequences/ are bundled inside _internal/ by PyInstaller.
; If a future build places them at top-level, uncomment these lines:
; Source: "{#DistDir}\demos\*"; DestDir: "{app}\demos"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "{#DistDir}\sequences\*"; DestDir: "{app}\sequences"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Create the writable data directory at %LOCALAPPDATA%\RobotAtlas
// and seed it with default files from the install if they don't already exist.
procedure InitializeDataDir();
var
  DataDir: String;
  BundleDir: String;
begin
  DataDir := ExpandConstant('{localappdata}\RobotAtlas');
  BundleDir := ExpandConstant('{app}\_internal');

  // Create data directory
  if not DirExists(DataDir) then
    ForceDirectories(DataDir);

  // Seed env.example -> .env (only if .env doesn't exist yet)
  if not FileExists(DataDir + '\.env') then
  begin
    if FileExists(BundleDir + '\env.example') then
      CopyFile(BundleDir + '\env.example', DataDir + '\.env', False);
  end;

  // Seed esp32_config.json
  if not FileExists(DataDir + '\esp32_config.json') then
  begin
    if FileExists(BundleDir + '\esp32_config.json') then
      CopyFile(BundleDir + '\esp32_config.json', DataDir + '\esp32_config.json', False);
  end;

  // Seed students_data.json
  if not FileExists(DataDir + '\students_data.json') then
  begin
    if FileExists(BundleDir + '\students_data.json') then
      CopyFile(BundleDir + '\students_data.json', DataDir + '\students_data.json', False);
  end;

  // Seed clases directory
  if not DirExists(DataDir + '\clases') then
  begin
    if DirExists(BundleDir + '\clases') then
    begin
      ForceDirectories(DataDir + '\clases');
      // Note: Inno Setup Pascal Script doesn't have recursive dir copy.
      // The app's _bootstrap_frozen_data() handles full seeding at first run.
      // We just create the directory here so the app detects it.
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    InitializeDataDir();
end;

// Clean up data directory on uninstall (ask user first)
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\RobotAtlas');
    if DirExists(DataDir) then
    begin
      if MsgBox('Do you want to remove RobotAtlas user data?' + #13#10 +
                '(' + DataDir + ')' + #13#10#13#10 +
                'This includes your classes, configurations, and student data.',
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(DataDir, True, True, True);
      end;
    end;
  end;
end;
