# 🚀 Despliegue de Componentes Avanzados

## Componentes Pendientes

Tienes razón, faltan estos componentes importantes:

1. **Cloud Composer (Airflow)** - Para orquestación de tareas
2. **Vertex AI** - Para el modelo de ML de predicción de fallas
3. **Bot de Telegram** - Para notificaciones

---

## 📊 Estado Actual

### ✅ Ya Desplegado
- Backend (Cloud Run)
- Frontend (Firebase)
- Base de Datos (Cloud SQL)
- Storage (Cloud Storage)
- Backups configurados

### ⚠️ Pendiente de Desplegar
- Cloud Composer (Airflow)
- Vertex AI (Modelo ML)
- Bot de Telegram

---

## 1️⃣ Cloud Composer (Airflow)

### ¿Qué es?
Servicio administrado de Apache Airflow para orquestar flujos de trabajo.

### DAGs Disponibles
```
airflow/dags/
├── etl_ml_training_dag.py          # ETL y entrenamiento del modelo ML
├── preventive_maintenance_dag.py   # Programación de mantenimientos
└── report_generation_dag.py        # Generación de reportes
```

### Costos
- **Ambiente Small:** ~$300/mes
- **Ambiente Medium:** ~$500/mes
- **Recomendación:** Empezar con Small

### Comandos de Despliegue

```bash
# 1. Habilitar API
gcloud services enable composer.googleapis.com

# 2. Crear ambiente de Composer (toma ~20-30 minutos)
gcloud composer environments create cmms-composer \
  --location us-central1 \
  --python-version 3 \
  --machine-type n1-standard-1 \
  --disk-size 20 \
  --node-count 3

# 3. Subir DAGs
gcloud composer environments storage dags import \
  --environment cmms-composer \
  --location us-central1 \
  --source airflow/dags/

# 4. Configurar variables de entorno
gcloud composer environments update cmms-composer \
  --location us-central1 \
  --update-env-variables \
    DB_HOST=/cloudsql/cmms-somacorv2:us-central1:cmms-db,\
    DB_NAME=cmms_db,\
    DB_USER=cmms_user,\
    DB_PASSWORD=cmms2024secure
```

### ⚠️ Consideración Importante
Cloud Composer es **costoso** (~$300-500/mes). 

**Alternativas más económicas:**
- Usar Cloud Run Jobs con Cloud Scheduler (~$5/mes)
- Usar Cloud Functions con Cloud Scheduler (~$5/mes)
- Desplegar Airflow en Cloud Run (~$20/mes)

---

## 2️⃣ Vertex AI (Modelo ML)

### ¿Qué es?
Plataforma de ML para entrenar y desplegar modelos de predicción de fallas.

### Modelo Disponible
```
backend/ml_models/failure_prediction_model.joblib
```

### Funcionalidad
- Predice probabilidad de falla de activos
- Basado en historial de mantenimiento
- Usa scikit-learn

### Costos
- **Entrenamiento:** ~$1-5 por entrenamiento
- **Predicción:** ~$0.01 por 1000 predicciones
- **Endpoint:** ~$50/mes si está siempre activo

### Comandos de Despliegue

```bash
# 1. Habilitar API
gcloud services enable aiplatform.googleapis.com

# 2. Crear bucket para modelos
gcloud storage buckets create gs://cmms-somacorv2-ml-models \
  --location=us-central1

# 3. Subir modelo
gcloud storage cp backend/ml_models/failure_prediction_model.joblib \
  gs://cmms-somacorv2-ml-models/

# 4. Crear endpoint de predicción
gcloud ai endpoints create \
  --region=us-central1 \
  --display-name=cmms-failure-prediction

# 5. Desplegar modelo
gcloud ai models upload \
  --region=us-central1 \
  --display-name=failure-prediction-v1 \
  --container-image-uri=gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-0:latest \
  --artifact-uri=gs://cmms-somacorv2-ml-models/
```

### ⚠️ Consideración Importante
Vertex AI puede ser costoso si el endpoint está siempre activo.

**Alternativa más económica:**
- Cargar el modelo en el backend de Cloud Run
- Hacer predicciones directamente en el backend
- Solo usar Vertex AI para reentrenamiento periódico

---

## 3️⃣ Bot de Telegram

### ¿Qué es?
Bot para enviar notificaciones de órdenes de trabajo, alertas, etc.

### Código Disponible
```
backend/apps/notifications/telegram_service.py
```

### Costos
- **Gratis** (Telegram no cobra)

### Pasos de Configuración

#### 1. Crear Bot en Telegram

```bash
# 1. Habla con @BotFather en Telegram
# 2. Envía: /newbot
# 3. Sigue las instrucciones
# 4. Guarda el TOKEN que te da
```

#### 2. Configurar en el Backend

```bash
# Actualizar variables de entorno
gcloud run services update cmms-backend \
  --region us-central1 \
  --update-env-vars="TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI"
```

#### 3. Configurar Webhook (Opcional)

```bash
# Si quieres que el bot responda a comandos
curl -X POST "https://api.telegram.org/botTU_TOKEN/setWebhook" \
  -d "url=https://cmms-backend-888881509782.us-central1.run.app/api/v1/telegram/webhook"
```

#### 4. Probar el Bot

```python
# Desde Python
import requests

TOKEN = "TU_TOKEN"
CHAT_ID = "TU_CHAT_ID"

requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": "¡Hola desde CMMS!"
    }
)
```

---

## 🎯 Recomendaciones

### Para Empezar (Mínimo Viable)

**Desplegar SOLO:**
1. ✅ Bot de Telegram (Gratis, fácil, útil)

**NO desplegar aún:**
- ❌ Cloud Composer (~$300/mes) - Muy costoso para empezar
- ❌ Vertex AI Endpoint (~$50/mes) - Costoso si está siempre activo

### Alternativas Económicas

#### En lugar de Cloud Composer:
```bash
# Usar Cloud Scheduler + Cloud Run Jobs
# Costo: ~$5/mes

# Ejemplo: Ejecutar reporte diario
gcloud scheduler jobs create http daily-report \
  --location=us-central1 \
  --schedule="0 8 * * *" \
  --uri="https://cmms-backend-888881509782.us-central1.run.app/api/v1/reports/generate-daily" \
  --http-method=POST \
  --headers="Content-Type=application/json"
```

#### En lugar de Vertex AI Endpoint:
```python
# Cargar modelo en el backend
# El modelo ya está en backend/ml_models/
# Solo necesitas usarlo en las vistas de Django

from joblib import load
import os

model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'failure_prediction_model.joblib')
model = load(model_path)

# Hacer predicción
prediction = model.predict(features)
```

---

## 📋 Plan de Despliegue Recomendado

### Fase 1: Inmediato (Gratis)
1. ✅ Configurar Bot de Telegram
2. ✅ Integrar modelo ML en el backend (sin Vertex AI)
3. ✅ Usar Cloud Scheduler para tareas programadas

**Costo adicional:** $0-5/mes

### Fase 2: Cuando tengas más usuarios (1-3 meses)
1. Evaluar si necesitas Cloud Composer
2. Considerar Vertex AI si necesitas reentrenamiento frecuente
3. Optimizar según uso real

**Costo adicional:** $50-100/mes

### Fase 3: Producción a escala (3-6 meses)
1. Desplegar Cloud Composer si tienes muchos flujos complejos
2. Usar Vertex AI para ML avanzado
3. Configurar CI/CD completo

**Costo adicional:** $300-500/mes

---

## 🚀 ¿Qué Quieres Desplegar Ahora?

### Opción 1: Solo Telegram (Recomendado)
- ✅ Gratis
- ✅ Fácil (10 minutos)
- ✅ Útil inmediatamente

### Opción 2: Telegram + ML en Backend
- ✅ Gratis
- ✅ Moderado (30 minutos)
- ✅ Predicciones funcionando

### Opción 3: Todo (Cloud Composer + Vertex AI + Telegram)
- ❌ Costoso (~$350/mes adicional)
- ❌ Complejo (2-3 horas)
- ⚠️ Solo si realmente lo necesitas

---

## 💡 Mi Recomendación

**Empezar con Opción 1 o 2:**

1. **Configurar Bot de Telegram** (10 min, gratis)
2. **Integrar ML en el backend** (20 min, gratis)
3. **Usar Cloud Scheduler** para tareas programadas (10 min, ~$5/mes)

**Total:** 40 minutos, ~$5/mes adicional

Esto te da el 90% de la funcionalidad por el 2% del costo.

---

## ❓ ¿Qué Prefieres?

1. **Desplegar solo Telegram** (rápido y gratis)
2. **Desplegar Telegram + ML** (completo y económico)
3. **Desplegar todo** (costoso pero completo)
4. **Ver más detalles** antes de decidir

**¿Cuál opción prefieres?**
