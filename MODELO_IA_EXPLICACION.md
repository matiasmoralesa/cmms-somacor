# 🤖 Modelo de IA en el Proyecto CMMS

**Proyecto**: argon-edge-478500-i8  
**Fecha**: 16 de Noviembre, 2025

---

## 📊 Resumen Ejecutivo

Tu proyecto CMMS incluye un **sistema de predicción de fallas** basado en Machine Learning que puede funcionar de dos formas:

1. **Modelo Local** (scikit-learn) - Actualmente activo
2. **Google Vertex AI** (opcional) - Preparado pero no configurado

---

## 🧠 Modelo de IA Implementado

### Tipo de Modelo
**Random Forest Classifier** (scikit-learn)

### Propósito
Predecir la probabilidad de falla de activos (vehículos/equipos) basándose en:
- Historial de mantenimiento
- Órdenes de trabajo
- Resultados de checklists
- Edad del activo
- Patrones de uso

---

## 🔧 Cómo Funciona

### 1. Extracción de Características (Features)

El modelo analiza **9 características** de cada activo:

```python
features = {
    'asset_age_days': 730,                    # Edad del activo en días
    'total_work_orders': 15,                  # Total de órdenes de trabajo
    'corrective_work_orders': 5,              # Órdenes correctivas (reparaciones)
    'preventive_work_orders': 10,             # Órdenes preventivas
    'avg_checklist_score': 75.5,              # Promedio de scores de inspección
    'failed_checklists': 2,                   # Checklists fallidos
    'days_since_last_maintenance': 45,        # Días desde último mantenimiento
    'work_orders_last_30_days': 2,            # Órdenes recientes (30 días)
    'work_orders_last_90_days': 6,            # Órdenes recientes (90 días)
}
```

### 2. Predicción

El modelo genera:
- **Probabilidad de falla** (0-100%)
- **Nivel de riesgo** (Bajo, Medio, Alto, Crítico)
- **Fecha estimada de falla** (si probabilidad > 50%)
- **Recomendaciones** de mantenimiento
- **Score de confianza** (70-95%)

### 3. Alertas Automáticas

Si la probabilidad de falla es:
- **≥ 70%**: Alerta CRÍTICA
- **≥ 50%**: Alerta de ADVERTENCIA
- **< 50%**: Solo registro

---

## 🌐 Conexión con Google Cloud

### Servicios de Google Utilizados

#### 1. **Cloud Storage** (Activo)
```
Uso: Almacenar modelos entrenados
Bucket: argon-edge-478500-i8-cmms-ml-models
Estado: ✅ Creado y funcionando
```

#### 2. **Vertex AI** (Opcional - No configurado)
```
Uso: Desplegar modelos de ML en la nube
Estado: ⚠️ Preparado pero no habilitado
Requiere: Configuración adicional
```

#### 3. **Cloud Run** (Activo)
```
Uso: Ejecutar el backend con el modelo de ML
Estado: ✅ Desplegado y funcionando
URL: https://cmms-backend-4qfhh2wkzq-uc.a.run.app
```

---

## 🔄 Dos Modos de Operación

### Modo 1: Modelo Local (Actual) ✅

**Ubicación**: Dentro del contenedor de Cloud Run  
**Librería**: scikit-learn + joblib  
**Ventajas**:
- ✅ Sin costos adicionales
- ✅ Respuesta rápida
- ✅ No requiere configuración extra
- ✅ Funciona offline

**Desventajas**:
- ⚠️ Limitado por recursos del contenedor
- ⚠️ No escala automáticamente
- ⚠️ Modelo se entrena con datos locales

**Cómo funciona**:
```python
# El modelo se entrena automáticamente con tus datos
ml_service = MLPredictionService()
ml_service.train_model()  # Entrena con datos históricos

# Hace predicciones
prediction = ml_service.predict_failure(asset)
# Resultado: {'failure_probability': 65.5, 'confidence_score': 82.0, ...}
```

### Modo 2: Google Vertex AI (Opcional) ⚠️

**Ubicación**: Google Cloud Vertex AI  
**Ventajas**:
- ✅ Escalabilidad automática
- ✅ Modelos más complejos
- ✅ Batch predictions
- ✅ Monitoreo avanzado
- ✅ Versionado de modelos

**Desventajas**:
- ❌ Costo adicional (~$50-100/mes)
- ❌ Requiere configuración
- ❌ Necesita entrenar y desplegar modelo

**Cómo habilitarlo**:
```python
# En settings/production.py
USE_VERTEX_AI = True
GCP_PROJECT_ID = 'argon-edge-478500-i8'
VERTEX_AI_ENDPOINT_ID = 'tu-endpoint-id'

# Luego el sistema usa Vertex AI automáticamente
prediction = ml_service.predict_failure(asset, use_vertex_ai=True)
```

---

## 📈 Endpoints de la API

### 1. Predecir Falla de un Activo
```http
POST /api/v1/predictions/predict_asset/
Content-Type: application/json

{
  "asset_id": "uuid-del-activo",
  "use_vertex_ai": false
}
```

**Respuesta**:
```json
{
  "id": "uuid",
  "asset": "uuid-del-activo",
  "failure_probability": 65.50,
  "confidence_score": 82.00,
  "predicted_failure_date": "2025-02-15",
  "risk_level": "HIGH",
  "recommendations": "ALTO: Programar inspección detallada en los próximos 7 días",
  "model_version": "1.0.0"
}
```

### 2. Predecir Todos los Activos
```http
POST /api/v1/predictions/predict_all_assets/
```

### 3. Dashboard de Salud
```http
GET /api/v1/predictions/asset_health_dashboard/
```

**Respuesta**:
```json
{
  "summary": {
    "total_assets": 5,
    "average_health_score": 78.5,
    "critical_risk": 1,
    "high_risk": 2,
    "medium_risk": 1,
    "low_risk": 1
  },
  "assets": [
    {
      "asset_id": "uuid",
      "asset_name": "Camión Supersucker 01",
      "health_score": 65.5,
      "failure_probability": 34.5,
      "risk_level": "MEDIUM"
    }
  ]
}
```

### 4. Predicciones de Alto Riesgo
```http
GET /api/v1/predictions/high_risk/
```

### 5. Tendencias de Predicción
```http
GET /api/v1/predictions/prediction_trends/?days=30
```

---

## 🎯 Algoritmo de Predicción

### Entrenamiento del Modelo

```python
# 1. Recolectar datos históricos
assets = Asset.objects.all()

# 2. Extraer características
for asset in assets:
    features = extract_features(asset)
    X.append(features)
    
    # Etiqueta: 1 si tiene alta tasa de fallas, 0 si no
    label = 1 if asset.corrective_work_orders > 3 else 0
    y.append(label)

# 3. Entrenar Random Forest
model = RandomForestClassifier(n_estimators=100, max_depth=10)
model.fit(X, y)

# 4. Guardar modelo
joblib.dump(model, 'ml_models/failure_prediction_model.joblib')
```

### Predicción

```python
# 1. Extraer características del activo
features = extract_features(asset)

# 2. Hacer predicción
probability = model.predict_proba([features])[0][1] * 100

# 3. Calcular nivel de riesgo
if probability >= 70:
    risk_level = 'CRITICAL'
elif probability >= 50:
    risk_level = 'HIGH'
elif probability >= 30:
    risk_level = 'MEDIUM'
else:
    risk_level = 'LOW'

# 4. Generar recomendaciones
recommendations = generate_recommendations(features, probability)
```

### Fallback: Modelo Basado en Reglas

Si no hay suficientes datos para entrenar, usa reglas:

```python
score = 0

# Muchas reparaciones correctivas
if corrective_work_orders > 5:
    score += 30

# Scores bajos en checklists
if avg_checklist_score < 70:
    score += 25

# Mucho tiempo sin mantenimiento
if days_since_last_maintenance > 180:
    score += 20

# Muchas órdenes recientes
if work_orders_last_30_days > 3:
    score += 15

failure_probability = min(100, score)
```

---

## 💰 Costos

### Configuración Actual (Modelo Local)
```
Costo adicional por ML: $0/mes
Incluido en Cloud Run: $5/mes
Total: $5/mes
```

### Si Habilitas Vertex AI
```
Vertex AI Endpoint: $50-100/mes
Predicciones: $0.01 por 1000 predicciones
Almacenamiento de modelos: $0.10/GB/mes
Total adicional: ~$50-100/mes
```

---

## 🚀 Cómo Usar el Modelo

### 1. Desde la API

```bash
# Obtener token
curl -X POST https://cmms-backend-4qfhh2wkzq-uc.a.run.app/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cmms.com","password":"Admin123!"}'

# Predecir falla de un activo
curl -X POST https://cmms-backend-4qfhh2wkzq-uc.a.run.app/api/v1/predictions/predict_asset/ \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"asset_id":"uuid-del-activo"}'
```

### 2. Desde el Frontend

```javascript
// Obtener predicciones
const response = await fetch('/api/v1/predictions/asset_health_dashboard/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
console.log(data.summary); // Resumen de salud de todos los activos
```

### 3. Automático (Scheduled)

Puedes configurar Cloud Scheduler para ejecutar predicciones automáticamente:

```bash
# Crear job que ejecuta predicciones diarias
gcloud scheduler jobs create http predict-daily \
  --schedule="0 2 * * *" \
  --uri="https://cmms-backend-4qfhh2wkzq-uc.a.run.app/api/v1/predictions/predict_all_assets/" \
  --http-method=POST \
  --headers="Authorization=Bearer TOKEN"
```

---

## 🔧 Configuración de Vertex AI (Opcional)

Si quieres habilitar Vertex AI en el futuro:

### 1. Habilitar API
```bash
gcloud services enable aiplatform.googleapis.com --project=argon-edge-478500-i8
```

### 2. Entrenar y Desplegar Modelo
```python
from apps.predictions.ml_service import MLPredictionService
from apps.predictions.vertex_ai_client import get_vertex_ai_client

# Entrenar modelo local
ml_service = MLPredictionService()
ml_service.train_model()
ml_service.save_model('ml_models/model.joblib')

# Desplegar a Vertex AI
vertex_client = get_vertex_ai_client()
endpoint_id = vertex_client.deploy_model(
    model_path='gs://argon-edge-478500-i8-cmms-ml-models/model.joblib',
    model_display_name='cmms-failure-prediction'
)
```

### 3. Configurar en Settings
```python
# backend/config/settings/production.py
USE_VERTEX_AI = True
VERTEX_AI_ENDPOINT_ID = 'tu-endpoint-id'
```

---

## 📊 Métricas del Modelo

El modelo rastrea:
- **Accuracy**: Precisión general
- **Precision**: Predicciones positivas correctas
- **Recall**: Fallas detectadas correctamente
- **F1 Score**: Balance entre precision y recall

Puedes ver las métricas en los logs cuando entrenas el modelo.

---

## ✅ Resumen

### Estado Actual
- ✅ **Modelo Local**: Funcionando con Random Forest
- ✅ **Cloud Storage**: Configurado para guardar modelos
- ✅ **API Endpoints**: Disponibles y documentados
- ⚠️ **Vertex AI**: Preparado pero no habilitado

### Servicios de Google Conectados
1. **Cloud Run** - Ejecuta el modelo ✅
2. **Cloud Storage** - Almacena modelos ✅
3. **Cloud SQL** - Almacena predicciones ✅
4. **Vertex AI** - Opcional, no configurado ⚠️

### Recomendación
**Mantén el modelo local** por ahora. Es suficiente para empezar y no tiene costo adicional. Considera Vertex AI solo si:
- Necesitas procesar miles de predicciones por día
- Quieres modelos más complejos (deep learning)
- Necesitas batch predictions grandes

---

**¿Quieres que te ayude a probar el modelo de predicción o configurar Vertex AI?**
