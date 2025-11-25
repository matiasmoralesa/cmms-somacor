# Script para probar los endpoints de Checklist API

$baseUrl = "https://cmms-backend-232652686658.us-central1.run.app/api/v1"

Write-Host "=== Probando API de Checklists ===" -ForegroundColor Green
Write-Host ""

# 1. Login (necesitas tener un usuario creado)
Write-Host "1. Intentando login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = "admin@cmms.com"
        password = "admin123"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/auth/login/" -Method POST -ContentType "application/json" -Body $loginBody
    $token = $loginResponse.access
    Write-Host "✓ Login exitoso" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Error en login: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Nota: Asegúrate de tener un usuario creado en la base de datos" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 2. Listar plantillas
Write-Host "2. Listando plantillas de checklist..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $templates = Invoke-RestMethod -Uri "$baseUrl/checklists/templates/" -Method GET -Headers $headers
    Write-Host "✓ Plantillas obtenidas: $($templates.count) plantillas" -ForegroundColor Green
    
    foreach ($template in $templates.results) {
        Write-Host "  - $($template.code): $($template.name) ($($template.item_count) items)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "✗ Error listando plantillas: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 3. Filtrar por tipo de vehículo
Write-Host "3. Filtrando plantillas por tipo de vehículo (CAMIONETA_MDO)..." -ForegroundColor Yellow
try {
    $filteredTemplates = Invoke-RestMethod -Uri "$baseUrl/checklists/templates/?vehicle_type=CAMIONETA_MDO" -Method GET -Headers $headers
    Write-Host "✓ Plantillas filtradas: $($filteredTemplates.count)" -ForegroundColor Green
    
    foreach ($template in $filteredTemplates.results) {
        Write-Host "  - $($template.code): $($template.name)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "✗ Error filtrando plantillas: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 4. Obtener detalles de una plantilla
if ($templates.results.Count -gt 0) {
    $firstTemplate = $templates.results[0]
    Write-Host "4. Obteniendo detalles de plantilla: $($firstTemplate.code)..." -ForegroundColor Yellow
    try {
        $templateDetail = Invoke-RestMethod -Uri "$baseUrl/checklists/templates/$($firstTemplate.id)/" -Method GET -Headers $headers
        Write-Host "✓ Detalles obtenidos" -ForegroundColor Green
        Write-Host "  Nombre: $($templateDetail.name)" -ForegroundColor Cyan
        Write-Host "  Tipo: $($templateDetail.vehicle_type_display)" -ForegroundColor Cyan
        Write-Host "  Items: $($templateDetail.item_count)" -ForegroundColor Cyan
        Write-Host "  Puntaje mínimo: $($templateDetail.passing_score)%" -ForegroundColor Cyan
    } catch {
        Write-Host "✗ Error obteniendo detalles: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# 5. Listar respuestas de checklist
Write-Host "5. Listando checklists completados..." -ForegroundColor Yellow
try {
    $responses = Invoke-RestMethod -Uri "$baseUrl/checklists/responses/" -Method GET -Headers $headers
    Write-Host "✓ Checklists completados: $($responses.count)" -ForegroundColor Green
    
    if ($responses.results.Count -gt 0) {
        foreach ($response in $responses.results) {
            Write-Host "  - $($response.template_code): $($response.asset_name) - Puntaje: $($response.score)% ($($response.passed ? 'Aprobado' : 'Reprobado'))" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  No hay checklists completados aún" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Error listando respuestas: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 6. Estadísticas
Write-Host "6. Obteniendo estadísticas..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/checklists/responses/statistics/" -Method GET -Headers $headers
    Write-Host "✓ Estadísticas obtenidas" -ForegroundColor Green
    Write-Host "  Total: $($stats.total)" -ForegroundColor Cyan
    Write-Host "  Aprobados: $($stats.passed)" -ForegroundColor Cyan
    Write-Host "  Reprobados: $($stats.failed)" -ForegroundColor Cyan
    Write-Host "  Promedio: $($stats.average_score)%" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Error obteniendo estadísticas: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Pruebas completadas ===" -ForegroundColor Green
