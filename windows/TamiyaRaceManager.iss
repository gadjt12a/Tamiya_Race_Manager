; Tamiya Race Manager - Inno Setup installer script
; Build with: BUILD INSTALLER (developer use only).bat
; Paths are relative to this file (windows\); version from app\VERSION.

#define VerFile FileOpen(SourcePath + "\..\app\VERSION")
#define AppVer Trim(FileRead(VerFile))
#expr FileClose(VerFile)

[Setup]
AppId={{8F2C4B7A-9D31-4E5A-A6C0-52B8A1F0D9E3}
AppName=Tamiya Race Manager
AppVersion={#AppVer}
AppPublisher=Tamiya Race Manager
DefaultDirName={localappdata}\Programs\TamiyaRaceManager
DisableProgramGroupPage=yes
DisableDirPage=yes
; Per-user install - no admin rights needed on club laptops
PrivilegesRequired=lowest
OutputDir=..\dist\installer
OutputBaseFilename=TamiyaRaceManager-Setup-{#AppVer}
SetupIconFile=..\app\icon.ico
UninstallDisplayIcon={app}\TamiyaRaceManager.exe
Compression=lzma2
SolidCompression=yes
InfoBeforeFile=installer-info.txt
CloseApplications=yes
WizardStyle=modern

[Files]
Source: "..\dist\TamiyaRaceManager.exe"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Icons]
Name: "{autodesktop}\Tamiya Race Manager"; Filename: "{app}\TamiyaRaceManager.exe"; Tasks: desktopicon
Name: "{autoprograms}\Tamiya Race Manager"; Filename: "{app}\TamiyaRaceManager.exe"

[Run]
Filename: "{app}\TamiyaRaceManager.exe"; Description: "Launch Tamiya Race Manager"; Flags: nowait postinstall skipifsilent

[Code]
// Politely ask a running Race Manager to shut down before installing,
// so the exe is never locked mid-update on race night.
function InitializeSetup(): Boolean;
var
  WinHttp: Variant;
begin
  Result := True;
  try
    WinHttp := CreateOleObject('WinHttp.WinHttpRequest.5.1');
    WinHttp.Open('POST', 'http://127.0.0.1:8765/shutdown', False);
    WinHttp.SetTimeouts(500, 500, 500, 500);
    WinHttp.Send('');
    Sleep(1500);
  except
    // Not running - nothing to do
  end;
end;

// On uninstall, remind the user their race data is untouched.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    if not UninstallSilent() then
      MsgBox('Your race data has NOT been deleted. It remains in:'#13#10#13#10 +
             ExpandConstant('{localappdata}\TamiyaRaceManager'), mbInformation, MB_OK);
end;
