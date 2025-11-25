#!/usr/bin/env pwsh
# Script para subir el proyecto a GitHub

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Subir Proyecto CMMS a GitHub" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que gh esté instalado
Write-Host "Verificando GitHub CLI..." -ForegroundColor Yellow
$ghPath = Get-Command gh -ErrorAction SilentlyContinue

if (-not $ghPath) {
    Write-Host "ERROR: GitHub CLI no está disponible en esta sesión." -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Cierra esta terminal" -ForegroundColor White
    Write-Host "2. Abre una nueva terminal PowerShell" -ForegroundColor White
    Write-Host "3. Ejecuta este script nuevamente: .\subir-a-github.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✓ GitHub CLI encontrado" -ForegroundColor Green
Write-Host ""

# Verificar autenticación
Write-Host "Verificando autenticación con GitHub..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "No estás autenticado en GitHub." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Iniciando proceso de autenticación..." -ForegroundColor Cyan
    Write-Host "Se abrirá tu navegador. Sigue las instrucciones." -ForegroundColor White
    Write-Host ""
    
    gh auth login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Falló la autenticación" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ Autenticado correctamente" -ForegroundColor Green
Write-Host ""

# Crear el repositorio
Write-Host "Creando repositorio en GitHub..." -ForegroundColor Yellow
Write-Host ""

$repoName = "cmms-sistema-mantenimiento"
$description = "Sistema de Gestión de Mantenimiento Computarizado (CMMS) con Django REST Framework y GCP"

Write-Host "Nombre del repositorio: $repoName" -ForegroundColor White
Write-Host "Descripción: $description" -ForegroundColor White
Write-Host ""

# Preguntar si quiere repositorio privado o público
$visibility = Read-Host "¿Repositorio privado o público? (private/public) [private]"
if ([string]::IsNullOrWhiteSpace($visibility)) {
    $visibility = "private"
}

Write-Host ""
Write-Host "Creando repositorio $visibility..." -ForegroundColor Cyan

if ($visibility -eq "private") {
    gh repo create $repoName --private --source=. --remote=origin --description="$description"
} else {
    gh repo create $repoName --public --source=. --remote=origin --description="$description"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo crear el repositorio" -ForegroundColor Red
    Write-Host ""
    Write-Host "Posibles causas:" -ForegroundColor Yellow
    Write-Host "- Ya existe un repositorio con ese nombre" -ForegroundColor White
    Write-Host "- No tienes permisos suficientes" -ForegroundColor White
    Write-Host ""
    Write-Host "Intenta crear el repositorio manualmente en:" -ForegroundColor White
    Write-Host "https://github.com/new" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "✓ Repositorio creado exitosamente" -ForegroundColor Green
Write-Host ""

# Subir el código
Write-Host "Subiendo código a GitHub..." -ForegroundColor Yellow

# Renombrar rama a main si es necesario
$currentBranch = git branch --show-current
if ($currentBranch -eq "master") {
    Write-Host "Renombrando rama master a main..." -ForegroundColor Cyan
    git branch -M main
}

# Push
git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo subir el código" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  ✓ PROYECTO SUBIDO EXITOSAMENTE" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""

# Obtener la URL del repositorio
$repoUrl = gh repo view --json url -q .url

Write-Host "Tu repositorio está disponible en:" -ForegroundColor Cyan
Write-Host $repoUrl -ForegroundColor White
Write-Host ""

# Abrir en el navegador
$openBrowser = Read-Host "¿Quieres abrir el repositorio en el navegador? (s/n) [s]"
if ([string]::IsNullOrWhiteSpace($openBrowser) -or $openBrowser -eq "s") {
    Start-Process $repoUrl
}

Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Revisa tu repositorio en GitHub" -ForegroundColor White
Write-Host "2. Completa el despliegue siguiendo COMPLETAR_DESPLIEGUE.md" -ForegroundColor White
Write-Host "3. Configura GitHub Actions para CI/CD (opcional)" -ForegroundColor White
Write-Host ""
