; WF Label Printer Installer Script
; Inno Setup 6.0 or higher required

#define MyAppName "WF Label Printer"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "WF Corporation"
#define MyAppExeName "WF_Label_Printer.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{B5C7A8E2-3F4D-4A9B-8C1E-5D6F7A8B9C0D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
SourceDir=..\..
OutputDir=build\installer
OutputBaseFilename=WF_Label_Printer_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "build\application\WF_Label_Printer\WF_Label_Printer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\application\WF_Label_Printer\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "prn\*"; DestDir: "{app}\prn"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // DB는 AppData에 자동 생성되므로 여기서 data 폴더를 만들 필요 없음
  end;
end;
