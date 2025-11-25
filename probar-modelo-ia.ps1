# Script para Probar el Modelo de IA
# Proyecto: argon-edge-478500-i8

$backendUrl = "https://cmms-backend-4qfhh2wkzq-uc.a.run.app"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Probando Modelo de IA - Predicción de Fallas" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Login
Write-Host "Paso 1: Iniciando sesión..." -ForegroundColor Yellow
Write-Host ""

$loginBody = @{
    email = "admin@cmms.com"
    password = "Admin123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access
    Write-Host "✓ Login exitoso" -ForegroundColor Green
    Write-Host "Usuario: $($loginResponse.user.email)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Error en login: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Asegúrate de haber creado el superusuario primero" -ForegroundColor Yellow
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host ""

# Paso 2: Verificar activos existentes
Write-Host "Paso 2: Verificando activos existentes..." -ForegroundColor Yellow
Write-Host ""

try {
    $assetsResponse = Invoke-RestMethod -Uri "$backendUrl/api/v1/assets/" -Headers $headers
    $totalAssets = $assetsResponse.count
    Write-Host "✓ Activos encontrados: $totalAssets" -ForegroundColor Green
    
    if ($totalAssets -eq 0) {
        Write-Host ""
        Write-Host "No hay activos. Creando activos de prueba..." -ForegroundColor Yellow
        
        # Crear activos de prueba
        $testAssets = @(
            @{
                name = "Camión Supersucker 01"
                asset_code = "CSS-001"
                vehicle_type = "CAMION_SUPERSUCKER"
                serial_number = "SN-CSS-001"
                status = "OPERATIONAL"
                installation_date = "2023-01-15"
            },
            @{
                name = "Camioneta MDO 01"
                asset_code = "CMD-001"
                vehicle_type = "CAMIONETA_MDO"
                serial_number = "SN-CMD-001"
                status = "OPERATIONAL"
                installation_date = "2022-06-20"
            },
            @{
                name = "Retroexcavadora 01"
                asset_code = "RET-001"
                vehicle_type = "RETROEXCAVADORA"
                serial_number = "SN-RET-001"
                status = "MAINTENANCE"
                installation_date = "2021-03-10"
            }
        )
        
        foreach ($asset in $testAssets) {
            $assetBody = $asset | ConvertTo-Json
            try {
                $newAsset = Invoke-RestMethod -Uri "$backendUrl/api/v1/assets/" -Method POST -Headers $headers -Body $assetBody
                Write-Host "  ✓ Creado: $($newAsset.name)" -ForegroundColor Green
            } catch {
                Write-Host "  ✗ Error creando activo: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        # Actualizar lista de activos
        $assetsResponse = Invoke-RestMethod -Uri "$backendUrl/api/v1/assets/" -Headers $headers
    }
    
    $assets = $assetsResponse.results
    
} catch {
    Write-Host "✗ Error obteniendo activos: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Paso 3: Generar predicciones
Write-Host "Paso 3: Generando predicciones de falla..." -ForegroundColor Yellow
Write-Host ""

if ($assets.Count -eq 0) {
    Write-Host "✗ No hay activos para predecir" -ForegroundColor Red
    exit 1
}

# Predecir para el primer activo
$firstAsset = $assets[0]
Write-Host "Prediciendo falla para: $($firstAsset.name)" -ForegroundColor White

$predictBody = @{
    asset_id = $firstAsset.id
    use_vertex_ai = $false
} | ConvertTo-Json

try {
    $prediction = Invoke-RestMethod -Uri "$backendUrl/api/v1/predictions/predict_asset/" -Method POST -Headers $headers -Body $predictBody
    
    Write-Host ""
    Write-Host "✓ Predicción generada:" -ForegroundColor Green
    Write-Host "  Activo: $($firstAsset.name)" -ForegroundColor White
    Write-Host "  Probabilidad de falla: $($prediction.failure_probability)%" -ForegroundColor $(if($prediction.failure_probability -gt 50){"Red"}else{"Green"})
    Write-Host "  Nivel de riesgo: $($prediction.risk_level)" -ForegroundColor $(
        switch($prediction.risk_level) {
            "CRITICAL" {"Red"}
            "HIGH" {"Yellow"}
            "MEDIUM" {"Cyan"}
            default {"Green"}
        }
    )
    Write-Host "  Confianza: $($prediction.confidence_score)%" -ForegroundColor Gray
    Write-Host "  Recomendaciones: $($prediction.recommendations)" -ForegroundColor Cyan
    
} catch {
    Write-Host "✗ Error generando predicción: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Paso 4: Predecir todos los activos
Write-Host "Paso 4: Generando predicciones para todos los activos..." -ForegroundColor Yellow
Write-Host ""

try {
    $allPredictions = Invoke-RestMethod -Uri "$backendUrl/api/v1/predictions/predict_all_assets/" -Method POST -Headers $headers
    
    Write-Host "✓ Predicciones generadas: $($allPredictions.count)" -ForegroundColor Green
    Write-Host ""
    
    foreach ($pred in $allPredictions.predictions) {
        $assetName = ($assets | Where-Object {$_.id -eq $pred.asset}).name
        Write-Host "  $assetName" -ForegroundColor White
        Write-Host "    Probabilidad: $($pred.failure_probability)% | Riesgo: $($pred.risk_level)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "✗ Error generando predicciones: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Paso 5: Dashboard de salud
Write-Host "Paso 5: Obteniendo dashboard de salud..." -ForegroundColor Yellow
Write-Host ""

try {
    $dashboard = Invoke-RestMethod -Uri "$backendUrl/api/v1/predictions/asset_health_dashboard/" -Headers $headers
    
    Write-Host "✓ Dashboard de Salud de Activos" -ForegroundColor Green
    Write-Host ""
    Write-Host "Resumen:" -ForegroundColor Cyan
    Write-Host "  Total de activos: $($dashboard.summary.total_assets)" -ForegroundColor White
    Write-Host "  Salud promedio: $($dashboard.summary.average_health_score)%" -ForegroundColor White
    Write-Host "  Riesgo crítico: $($dashboard.summary.critical_risk)" -ForegroundColor Red
    Write-Host "  Riesgo alto: $($dashboard.summary.high_risk)" -ForegroundColor Yellow
    Write-Host "  Riesgo medio: $($dashboard.summary.medium_risk)" -ForegroundColor Cyan
    Write-Host "  Riesgo bajo: $($dashboard.summary.low_risk)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Detalle por Activo:" -ForegroundColor Cyan
    foreach ($asset in $dashboard.assets) {
        Write-Host ""
        Write-Host "  $($asset.asset_name) ($($asset.asset_code))" -ForegroundColor White
        Write-Host "    Health Score: $($asset.health_score)%" -ForegroundColor $(if($asset.health_score -lt 50){"Red"}elseif($asset.health_score -lt 70){"Yellow"}else{"Green"})
        Write-Host "    Probabilidad de falla: $($asset.failure_probability)%" -ForegroundColor Gray
        Write-Host "    Nivel de riesgo: $($asset.risk_level_display)" -ForegroundColor Gray
        if ($asset.predicted_failure_date) {
            Write-Host "    Fecha estimada de falla: $($asset.predicted_failure_date)" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "✗ Error obteniendo dashboard: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Paso 6: Predicciones de alto riesgo
Write-Host "Paso 6: Obteniendo predicciones de alto riesgo..." -ForegroundColor Yellow
Write-Host ""

try {
    $highRisk = Invoke-RestMethod -Uri "$backendUrl/api/v1/predictions/high_risk/" -Headers $headers
    
    if ($highRisk.Count -gt 0) {
        Write-Host "✓ Activos de alto riesgo encontrados: $($highRisk.Count)" -ForegroundColor Yellow
        foreach ($pred in $highRisk) {
            $assetName = ($assets | Where-Object {$_.id -eq $pred.asset}).name
            Write-Host "  ⚠ $assetName - $($pred.failure_probability)%" -ForegroundColor Red
        }
    } else {
        Write-Host "✓ No hay activos de alto riesgo" -ForegroundColor Green
    }
    
} catch {
    Write-Host "✗ Error obteniendo alto riesgo: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Paso 7: Alertas generadas
Write-Host "Paso 7: Verificando alertas generadas..." -ForegroundColor Yellow
Write-Host ""

try {
    $alerts = Invoke-RestMethod -Uri "$backendUrl/api/v1/predictions/alerts/" -Headers $headers
    
    if ($alerts.count -gt 0) {
        Write-Host "✓ Alertas encontradas: $($alerts.count)" -ForegroundColor Yellow
        
        $unread = $alerts.results | Where-Object {-not $_.is_read}
        $critical = $alerts.results | Where-Object {$_.severity -eq "CRITICAL"}
        
        Write-Host "  No leídas: $($unread.Count)" -ForegroundColor White
        Write-Host "  Críticas: $($critical.Count)" -ForegroundColor Red
    } else {
        Write-Host "✓ No hay alertas" -ForegroundColor Green
    }
    
} catch {
    Write-Host "⚠ Endpoint de alertas no disponible" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "     Prueba del Modelo de IA Completada" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs útiles:" -ForegroundColor Cyan
Write-Host "  API Docs: $backendUrl/api/docs/" -ForegroundColor White
Write-Host "  Predictions: $backendUrl/api/v1/predictions/" -ForegroundColor White
Write-Host "  Dashboard: $backendUrl/api/v1/predictions/asset_health_dashboard/" -ForegroundColor White
Write-Host ""
Write-Host "Token de acceso guardado en `$token" -ForegroundColor Gray
Write-Host ""
