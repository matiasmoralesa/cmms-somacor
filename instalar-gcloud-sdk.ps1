# Script de Instalación de Google Cloud SDK
# Para el proyecto: argon-edge-478500-i8

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "║     Instalación de Google Cloud SDK para CMMS            ║" -ForegroundColor Cyan
Write-Host "║     Proyecto: argon-edge-478500-i8                        ║" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar si ya está instalado
Write-Host "Verificando si Google Cloud SDK ya está instalado..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "✓ Google Cloud SDK ya está instalado: $gcloudVersion" -ForegroundColor Green
    Write-Host ""
    Write-Host "¿Deseas continuar con la configuración? (y/n): " -ForegroundColor Yellow -NoNewline
    $continue = Read-Host
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Host "Instalación cancelada" -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "✗ Google Cloud SDK no está instalado" -ForegroundColor Red
    Write-Host ""
    
    # Descargar instalador
    $installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
    $installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"
    
    Write-Host "Descargando Google Cloud SDK..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "✓ Descarga completada" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error al descargar el instalador" -ForegroundColor Red
        Write-Host "Por favor descarga manualmente desde:" -ForegroundColor Yellow
        Write-Host "https://cloud.google.com/sdk/docs/install#windows" -ForegroundColor Cyan
        exit 1
    }
    
    Write-Host ""
    Write-Host "Ejecutando instalador..." -ForegroundColor Yellow
    Write-Host "⚠️  IMPORTANTE: Durante la instalación:" -ForegroundColor Yellow
    Write-Host "   1. Acepta la ubicación predeterminada" -ForegroundColor White
    Write-Host "   2. Marca 'Run gcloud init' al finalizar" -ForegroundColor White
    Write-Host "   3. Después de instalar, CIERRA esta terminal" -ForegroundColor White
    Write-Host "   4. Abre una NUEVA terminal PowerShell" -ForegroundColor White
    Write-Host ""
    
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                                                           ║" -ForegroundColor Green
    Write-Host "║     ✓ Instalación Completada                             ║" -ForegroundColor Green
    Write-Host "║                                                           ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  PRÓXIMOS PASOS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. CIERRA esta terminal PowerShell" -ForegroundColor White
    Write-Host "2. Abre una NUEVA terminal PowerShell" -ForegroundColor White
    Write-Host "3. Ejecuta: .\configurar-gcp.ps1" -ForegroundColor Cyan
    Write-Host ""
    
    # Crear script de configuración
    $configScript = @"
# Script de Configuración de GCP
# Proyecto: argon-edge-478500-i8

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "║     Configuración de Google Cloud Platform               ║" -ForegroundColor Cyan
Write-Host "║     Proyecto: argon-edge-478500-i8                        ║" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar instalación
Write-Host "Verificando instalación de Google Cloud SDK..." -ForegroundColor Yellow
try {
    `$version = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "✓ Google Cloud SDK instalado: `$version" -ForegroundColor Green
} catch {
    Write-Host "✗ Google Cloud SDK no encontrado" -ForegroundColor Red
    Write-Host "Por favor cierra esta terminal y abre una nueva" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Paso 1: Autenticación" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se abrirá tu navegador para autenticarte en Google Cloud" -ForegroundColor White
Write-Host "Presiona Enter para continuar..." -ForegroundColor Yellow
Read-Host

gcloud auth login

if (`$LASTEXITCODE -ne 0) {
    Write-Host "✗ Error en la autenticación" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Autenticación exitosa" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Paso 2: Configurar Proyecto" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

gcloud config set project argon-edge-478500-i8
Write-Host "✓ Proyecto configurado: argon-edge-478500-i8" -ForegroundColor Green

gcloud config set compute/region us-central1
Write-Host "✓ Región configurada: us-central1" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Paso 3: Habilitar APIs (esto tomará 3-5 minutos)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

`$apis = @(
    "sqladmin.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage-api.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudscheduler.googleapis.com"
)

foreach (`$api in `$apis) {
    Write-Host "Habilitando `$api..." -ForegroundColor White
    gcloud services enable `$api --project=argon-edge-478500-i8 --quiet
    if (`$LASTEXITCODE -eq 0) {
        Write-Host "✓ `$api habilitada" -ForegroundColor Green
    } else {
        Write-Host "⚠ Error al habilitar `$api (puede que ya esté habilitada)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "║     ✓ Configuración Completada                           ║" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Configuración actual:" -ForegroundColor Cyan
gcloud config list

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Próximos Pasos" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ejecutar despliegue:" -ForegroundColor White
Write-Host "   cd deployment\gcp" -ForegroundColor Cyan
Write-Host "   .\deploy-windows.ps1 -ProjectId 'argon-edge-478500-i8'" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. O seguir la guía completa:" -ForegroundColor White
Write-Host "   Ver archivo: DESPLIEGUE_PERSONALIZADO.md" -ForegroundColor Cyan
Write-Host ""
"@

    $configScript | Out-File -FilePath "configurar-gcp.ps1" -Encoding UTF8
    Write-Host "✓ Script de configuración creado: configurar-gcp.ps1" -ForegroundColor Green
    
    exit 0
}

# Si ya está instalado, configurar directamente
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Configurando Google Cloud Platform" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Autenticando..." -ForegroundColor Yellow
gcloud auth login

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Error en la autenticación" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Autenticación exitosa" -ForegroundColor Green

Write-Host ""
Write-Host "Configurando proyecto..." -ForegroundColor Yellow
gcloud config set project argon-edge-478500-i8
Write-Host "✓ Proyecto configurado: argon-edge-478500-i8" -ForegroundColor Green

gcloud config set compute/region us-central1
Write-Host "✓ Región configurada: us-central1" -ForegroundColor Green

Write-Host ""
Write-Host "Habilitando APIs (esto tomará 3-5 minutos)..." -ForegroundColor Yellow

$apis = @(
    "sqladmin.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage-api.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudscheduler.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "Habilitando $api..." -ForegroundColor White
    gcloud services enable $api --project=argon-edge-478500-i8 --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $api habilitada" -ForegroundColor Green
    } else {
        Write-Host "⚠ Error al habilitar $api" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "║     ✓ Todo Listo para Desplegar                          ║" -ForegroundColor Green
Write-Host "║                                                           ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "  cd deployment\gcp" -ForegroundColor White
Write-Host "  .\deploy-windows.ps1 -ProjectId 'argon-edge-478500-i8'" -ForegroundColor White
Write-Host ""
