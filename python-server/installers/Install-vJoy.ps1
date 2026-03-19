# vJoy Installer PowerShell Script
# Uso: ./Install-vJoy.ps1

param(
    [switch]$Silent,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Colores
$colors = @{
    Success = 'Green'
    Error = 'Red'
    Warning = 'Yellow'
    Info = 'Cyan'
}

function Write-Color {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

# Verificar derechos de administrador
function Test-Administrator {
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      vJoy Automatic Installer - PowerShell Edition        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar derechos de administrador
if (-not (Test-Administrator)) {
    Write-Color "⚠️  Requiere derechos de administrador" $colors.Warning
    Write-Color "Reiniciando script con privilegios elevados..." $colors.Info
    Start-Process PowerShell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Silent" -Verb RunAs
    exit
}

Write-Color "✓ Derechos de administrador confirmados" $colors.Success

# Obtener ruta del script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Color "📁 Directorio: $scriptPath" $colors.Info

# Ejecutar el instalador de Python
Write-Color ""
Write-Color "Iniciando instalador de vJoy..." $colors.Info
Write-Color ""

try {
    $pythonScript = Join-Path $scriptPath "vjoy_installer.py"
    
    if (-not (Test-Path $pythonScript)) {
        throw "No se encontró vjoy_installer.py"
    }
    
    # Ejecutar el script de Python
    & python $pythonScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Color ""
        Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║          ✓ vJoy instalado correctamente                    ║" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Color ""
        
        if (-not $Silent) {
            Read-Host "Presione Enter para cerrar"
        }
        exit 0
    } else {
        throw "El instalador de vJoy falló con código: $LASTEXITCODE"
    }
}
catch {
    Write-Color "✗ Error: $_" $colors.Error
    Write-Color ""
    
    if (-not $Silent) {
        Read-Host "Presione Enter para cerrar"
    }
    exit 1
}
