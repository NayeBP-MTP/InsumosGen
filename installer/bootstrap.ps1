<#
.SYNOPSIS
  Prepara (o repara) el entorno de InsumosGen en la máquina del usuario: Python 3.13, entorno virtual y librerías.

.DESCRIPTION
  Lo ejecuta el instalador como último paso y la app ("Reparar entorno"). Es idempotente: lo que ya está
  bien no se repite.
    1. Busca un Python 3.13 de 64 bits ya instalado (con tkinter, venv y ensurepip). Si no hay, descarga el
       instalador oficial de python.org (SHA-256 fijo) y lo instala solo para este usuario, sin admin.
    2. Crea (o reconstruye, si está roto) el entorno virtual en <InstallDir>\runtime\venv.
    3. Instala las librerías de requirements.txt (con reintentos), salvo que ya estén instaladas con ese mismo
       requirements.txt.
    4. Guarda <InstallDir>\runtime\state.json (lo lee el updater).

  Se ejecuta sin cambiar la política global:
    powershell -NoProfile -ExecutionPolicy Bypass -File bootstrap.ps1
  Códigos de salida: 0 = listo, 1 = falló (el mensaje dice qué hacer).
#>
[CmdletBinding()]
param(
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA 'Programs\InsumosGen'),
    [string]$Requirements,
    [string]$AppVersion = '',
    [switch]$DetectOnly
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # Invoke-WebRequest es mucho más rápido sin la barra
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# --- Python que se acepta / que se instala si no hay ninguno -------------------------------------------------
$PythonSerie   = @(3, 13)
$PythonVersion = '3.13.7'
$PythonUrl     = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
# Instalador firmado por la Python Software Foundation; el hash se calculó al fijar la versión.
$PythonSha256  = 'B12E2E82461AC8E51FC43289050BC8EB937A32D84CE4D242E2C88258C37CF2BB'
$BootstrapVersion = 1

$RuntimeDir = Join-Path $InstallDir 'runtime'
$VenvDir    = Join-Path $RuntimeDir 'venv'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
$OwnPython  = Join-Path $RuntimeDir 'python\python.exe'
$StatePath  = Join-Path $RuntimeDir 'state.json'
if (-not $Requirements) { $Requirements = Join-Path $InstallDir 'app\requirements.txt' }

# Sin comillas dentro: se pasa como un solo argumento a python.exe.
$ProbeCode = "import sys, tkinter, venv, ensurepip; sys.exit(0 if (sys.version_info[:2] == ($($PythonSerie[0]), $($PythonSerie[1])) and sys.maxsize > 2**32) else 1)"

function Write-Paso([int]$n, [int]$total, [string]$texto) {
    Write-Host ""
    Write-Host "[$n/$total] $texto"
}

function Test-Python([string]$exe) {
    if (-not $exe -or -not (Test-Path -LiteralPath $exe)) { return $false }
    try {
        & $exe -c $ProbeCode 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Get-CandidatosPython {
    $serie = "$($PythonSerie[0]).$($PythonSerie[1])"
    $candidatos = @($OwnPython)

    # Registro (PEP 514): instalaciones por usuario y por equipo.
    foreach ($raiz in @("HKCU:\SOFTWARE\Python\PythonCore\$serie\InstallPath",
                        "HKLM:\SOFTWARE\Python\PythonCore\$serie\InstallPath",
                        "HKLM:\SOFTWARE\WOW6432Node\Python\PythonCore\$serie\InstallPath")) {
        try {
            $clave = Get-ItemProperty -LiteralPath $raiz -ErrorAction Stop
            if ($clave.ExecutablePath) { $candidatos += $clave.ExecutablePath }
            elseif ($clave.'(default)') { $candidatos += (Join-Path $clave.'(default)' 'python.exe') }
        } catch { }
    }

    # Lanzador "py".
    try {
        $viaPy = & py "-$serie" -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $viaPy) { $candidatos += $viaPy.Trim() }
    } catch { }

    # PATH, sin el alias de la Microsoft Store (abre la tienda en vez de ejecutar Python).
    foreach ($comando in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)) {
        if ($comando.Source -and $comando.Source -notmatch '\\WindowsApps\\') { $candidatos += $comando.Source }
    }
    return $candidatos | Where-Object { $_ } | Select-Object -Unique
}

function Find-Python {
    foreach ($candidato in Get-CandidatosPython) {
        if (Test-Python $candidato) { return $candidato }
    }
    return $null
}

function Install-Python {
    $instalador = Join-Path ([IO.Path]::GetTempPath()) "python-$PythonVersion-amd64.exe"
    Write-Host "      No hay un Python $($PythonSerie[0]).$($PythonSerie[1]) válido; descargando Python $PythonVersion (~28 MB)..."
    try {
        Invoke-WebRequest -Uri $PythonUrl -OutFile $instalador -UseBasicParsing
    } catch {
        throw "No se pudo descargar Python desde python.org ($($_.Exception.Message)). Revisa tu conexión a internet y vuelve a intentarlo, o instala Python $PythonVersion manualmente desde https://www.python.org/downloads/ y ejecuta de nuevo."
    }
    $hash = (Get-FileHash -LiteralPath $instalador -Algorithm SHA256).Hash
    if ($hash -ne $PythonSha256) {
        Remove-Item -LiteralPath $instalador -Force -ErrorAction SilentlyContinue
        throw "El instalador de Python descargado no coincide con el hash esperado; no se instaló. Vuelve a intentarlo y, si se repite, avisa al equipo."
    }
    Write-Host "      Instalando Python solo para tu usuario (sin permisos de administrador)..."
    $destino = Join-Path $RuntimeDir 'python'
    $argumentos = @('/quiet', 'InstallAllUsers=0', 'PrependPath=0', 'Include_launcher=0', 'Include_test=0',
                    'Include_doc=0', 'Include_pip=1', 'Include_tcltk=1', "TargetDir=$destino")
    $proceso = Start-Process -FilePath $instalador -ArgumentList $argumentos -Wait -PassThru
    Remove-Item -LiteralPath $instalador -Force -ErrorAction SilentlyContinue
    if ($proceso.ExitCode -ne 0 -or -not (Test-Python $OwnPython)) {
        throw "La instalación de Python terminó con código $($proceso.ExitCode) y no quedó utilizable. Vuelve a intentarlo o instala Python $PythonVersion manualmente."
    }
    return $OwnPython
}

function Test-Venv {
    if (-not (Test-Path -LiteralPath $VenvPython)) { return $false }
    try {
        # Falla si el Python base en el que se creó el entorno ya no existe.
        & $VenvPython -c "import sys, tkinter" 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Get-RequirementsHash {
    return (Get-FileHash -LiteralPath $Requirements -Algorithm SHA256).Hash.ToLower()
}

function Read-State {
    if (Test-Path -LiteralPath $StatePath) {
        try { return Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json } catch { return $null }
    }
    return $null
}

function Write-State([string]$pythonVersion, [string]$hash) {
    $previo = Read-State
    $estado = [ordered]@{
        appVersion         = if ($AppVersion) { $AppVersion } elseif ($previo -and $previo.appVersion) { $previo.appVersion } else { '' }
        pythonVersion      = $pythonVersion
        requirementsSha256 = $hash
        bootstrapVersion   = $BootstrapVersion
        installedAt        = (Get-Date).ToString('s')
    }
    $json = $estado | ConvertTo-Json
    [IO.File]::WriteAllText($StatePath, $json, (New-Object Text.UTF8Encoding($false)))
}

function Install-Requirements {
    $maximo = 3
    for ($intento = 1; $intento -le $maximo; $intento++) {
        & $VenvPython -m pip install --disable-pip-version-check --no-input -r $Requirements
        if ($LASTEXITCODE -eq 0) { return }
        if ($intento -lt $maximo) {
            Write-Host "      pip falló (intento $intento de $maximo); reintentando en $(5 * $intento) s..."
            Start-Sleep -Seconds (5 * $intento)
        }
    }
    throw "No se pudieron instalar las librerías (pip falló $maximo veces). Revisa tu conexión a internet y que PyPI (pypi.org) sea accesible desde tu red, y vuelve a ejecutar; en la app usa 'Reparar entorno'."
}

# ===============================================================================================================
try {
    if ($DetectOnly) {
        $encontrado = Find-Python
        if ($encontrado) { Write-Output $encontrado } else { Write-Output 'NINGUNO' }
        exit 0
    }

    if (-not (Test-Path -LiteralPath $Requirements)) { throw "No se encontró requirements.txt en $Requirements." }
    New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

    Write-Paso 1 4 "Buscando Python $($PythonSerie[0]).$($PythonSerie[1])..."
    $python = Find-Python
    if ($python) { Write-Host "      Usando $python" } else { $python = Install-Python }

    Write-Paso 2 4 'Preparando el entorno virtual...'
    if (Test-Venv) {
        Write-Host '      El entorno virtual ya está listo.'
    } else {
        if (Test-Path -LiteralPath $VenvDir) {
            Write-Host '      El entorno virtual está dañado; se reconstruye.'
            Remove-Item -LiteralPath $VenvDir -Recurse -Force
        }
        & $python -m venv $VenvDir
        if ($LASTEXITCODE -ne 0 -or -not (Test-Venv)) { throw 'No se pudo crear el entorno virtual.' }
    }

    Write-Paso 3 4 'Instalando las librerías (la primera vez tarda unos minutos)...'
    $hash = Get-RequirementsHash
    $estado = Read-State
    if ($estado -and $estado.requirementsSha256 -eq $hash -and (Test-Venv)) {
        Write-Host '      Las librerías ya están instaladas con este requirements.txt.'
    } else {
        Install-Requirements
    }

    Write-Paso 4 4 'Guardando el estado...'
    $version = (& $VenvPython -c "import sys; print(sys.version.split()[0])").Trim()
    Write-State -pythonVersion $version -hash $hash

    Write-Host ''
    Write-Host 'Listo: el entorno de InsumosGen está preparado.'
    exit 0
} catch {
    Write-Host ''
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
