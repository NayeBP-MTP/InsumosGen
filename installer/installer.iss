; Instalador de InsumosGen (Inno Setup). Sin administrador: todo va a %LOCALAPPDATA%\Programs\InsumosGen.
;
; Lo que instala es el zip de código del release ya extraído (StageDir); Python, el entorno virtual y las
; librerías los prepara bootstrap.ps1 como último paso. Compilar:
;   ISCC.exe /DAppVersion=1.0.0 /DStageDir=<carpeta con el zip extraído> /DOutputDir=dist installer\installer.iss

#ifndef AppVersion
  #error Falta /DAppVersion=X.Y.Z
#endif
#ifndef StageDir
  #error Falta /DStageDir=<carpeta con el contenido del zip del release>
#endif
#ifndef OutputDir
  #define OutputDir "..\dist"
#endif

#define AppName "InsumosGen"

[Setup]
; GUID fijo: es lo que hace que una versión nueva se instale encima de la anterior. No cambiarlo nunca.
AppId={{6F2A9C1E-3B7D-4E58-9A41-5C0D8E7B2F13}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=InsumosGen
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=
OutputDir={#OutputDir}
OutputBaseFilename={#AppName}-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#AppName}
CloseApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[InstallDelete]
; Una instalación encima deja el código exactamente como el del zip (sin restos de versiones anteriores).
Type: filesandordirs; Name: "{app}\app"
Type: filesandordirs; Name: "{app}\app.old"
Type: filesandordirs; Name: "{app}\app.new"

[Files]
Source: "{#StageDir}\*"; DestDir: "{app}\app"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\runtime\venv\Scripts\pythonw.exe"; Parameters: """{app}\app\launch.pyw"""; WorkingDir: "{app}\app"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\runtime\venv\Scripts\pythonw.exe"; Parameters: """{app}\app\launch.pyw"""; WorkingDir: "{app}\app"

[Run]
Filename: "{app}\runtime\venv\Scripts\pythonw.exe"; Parameters: """{app}\app\launch.pyw"""; WorkingDir: "{app}\app"; Description: "Abrir {#AppName}"; Flags: nowait postinstall skipifsilent; Check: EntornoListo

[UninstallDelete]
; Solo lo que instaló el programa. Los datos del usuario (%LOCALAPPDATA%\InsumosGen) y las contraseñas del
; Administrador de credenciales de Windows no se tocan.
Type: filesandordirs; Name: "{app}\app"
Type: filesandordirs; Name: "{app}\app.old"
Type: filesandordirs; Name: "{app}\app.new"
Type: filesandordirs; Name: "{app}\runtime"

[Code]
var
  EntornoOk: Boolean;

function PrepararEntorno(): Boolean;
var
  Script, Parametros: String;
  Codigo: Integer;
begin
  Script := ExpandConstant('{app}\app\installer\bootstrap.ps1');
  Parametros := '-NoProfile -ExecutionPolicy Bypass -File "' + Script + '" -InstallDir "' +
    ExpandConstant('{app}') + '" -AppVersion "{#AppVersion}"';
  // Ventana visible: la primera vez puede descargar Python e instalar librerías (varios minutos).
  Result := Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), Parametros, '',
    SW_SHOWNORMAL, ewWaitUntilTerminated, Codigo) and (Codigo = 0);
end;

function EntornoListo(): Boolean;
begin
  Result := EntornoOk;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    WizardForm.StatusLabel.Caption := 'Preparando Python y las librerías (puede tardar unos minutos)...';
    EntornoOk := PrepararEntorno();
    if not EntornoOk then
      SuppressibleMsgBox(
        'InsumosGen se copió, pero no se pudo preparar el entorno (Python y librerías).' + #13#10 + #13#10 +
        'Revisa tu conexión a internet y vuelve a ejecutar este instalador: retoma desde donde quedó.',
        mbError, MB_OK, IDOK);
  end;
end;
