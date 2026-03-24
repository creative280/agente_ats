param(
    [int]$Port = 8000,
    [switch]$Reload
)

$ErrorActionPreference = "Stop"

Write-Host "[START] Puerto objetivo: $Port"

try {
    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
} catch {
    $listeners = @()
}

$pids = @()
if ($listeners) {
    $pids += $listeners | Select-Object -ExpandProperty OwningProcess -Unique
}

# Respaldo por netstat por si Get-NetTCPConnection omite algún listener.
$netstatPids = netstat -ano |
    Select-String "LISTENING" |
    Select-String ":$Port\s" |
    ForEach-Object {
        $parts = ($_ -replace "\s+", " ").Trim().Split(" ")
        $parts[-1]
    } |
    Where-Object { $_ -match "^\d+$" } |
    Select-Object -Unique
$pids += $netstatPids
$pids = $pids | Where-Object { $_ -match "^\d+$" } | Select-Object -Unique

if ($pids.Count -eq 0) {
    Write-Host "[INFO] No hay procesos escuchando en el puerto $Port"
} else {
    foreach ($procId in $pids) {
        try {
            $proc = Get-Process -Id $procId -ErrorAction Stop
            Write-Host "[STOP] Cerrando PID $procId ($($proc.ProcessName)) en puerto $Port"
            Stop-Process -Id $procId -Force -ErrorAction Stop
        } catch {
            Write-Host "[WARN] No se pudo cerrar PID ${procId}: $($_.Exception.Message)"
        }
    }
    Start-Sleep -Milliseconds 700
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$venvPython = Join-Path $scriptDir "..\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "[RUN] Iniciando uvicorn con venv: $venvPython"
    if ($Reload) {
        & $venvPython -m uvicorn app:app --reload --port $Port
    } else {
        & $venvPython -m uvicorn app:app --port $Port
    }
} else {
    Write-Host "[RUN] venv no encontrado. Usando python del sistema."
    if ($Reload) {
        python -m uvicorn app:app --reload --port $Port
    } else {
        python -m uvicorn app:app --port $Port
    }
}
