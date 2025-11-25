# Optimización de Costos GCP - CMMS

## ✅ Optimizaciones Aplicadas

### 1. Cloud Run Backend
- **Antes**: Min instances: 1, Memory: 1GB
- **Ahora**: Min instances: 0, Memory: 512MB
- **Ahorro**: ~$15-20/mes
- **Impacto**: Cold start de 1-2 segundos en primera petición

### 2. Cloud SQL
- **Antes**: db-g1-small (1.7GB RAM)
- **Ahora**: db-f1-micro (0.6GB RAM)
- **Ahorro**: ~$15-20/mes
- **Impacto**: Menor rendimiento, adecuado para desarrollo/pruebas

### 3. Cloud Run Jobs
- **Eliminado**: load-templates job
- **Ahorro**: ~$2-5/mes
- **Nota**: Las plantillas ya están cargadas

## 💰 Estimación de Costos Mensuales

### Antes de Optimización
- Cloud Run: ~$20/mes
- Cloud SQL: ~$25/mes
- Cloud Storage: ~$2/mes
- Cloud Build: ~$5/mes
- **Total**: ~$52/mes

### Después de Optimización
- Cloud Run: ~$3-5/mes (solo cuando hay tráfico)
- Cloud SQL: ~$7-10/mes
- Cloud Storage: ~$2/mes
- Cloud Build: ~$2/mes (solo cuando despliegas)
- **Total**: ~$14-19/mes

## 📊 Créditos Actuales
- **Disponible**: $0.88
- **Duración estimada**: 1-2 días con uso normal
- **Recomendación**: Pausar servicios cuando no los uses

## 🛑 Cómo Pausar Servicios (Ahorro Máximo)

### Pausar Cloud SQL (cuando no lo uses)
```bash
gcloud sql instances patch cmms-db --activation-policy NEVER
```

### Reactivar Cloud SQL
```bash
gcloud sql instances patch cmms-db --activation-policy ALWAYS
```

### Eliminar Revisiones Antiguas de Cloud Run
```bash
# Ver revisiones
gcloud run revisions list --service cmms-backend --region us-central1

# Eliminar revisiones antiguas (mantén solo las últimas 2-3)
gcloud run revisions delete cmms-backend-00001-xxx --region us-central1 --quiet
```

## 💡 Recomendaciones Adicionales

### 1. Usar Firebase Hosting Free Tier
- ✅ Ya implementado
- Hosting del frontend: GRATIS
- 10GB almacenamiento, 360MB/día transferencia

### 2. Limitar Cloud Build
```bash
# Solo construir cuando sea necesario
# Evitar múltiples deploys seguidos
```

### 3. Monitorear Uso
```bash
# Ver uso actual
gcloud billing accounts list
gcloud billing projects describe argon-edge-478500-i8
```

### 4. Configurar Alertas de Presupuesto
- Ve a: https://console.cloud.google.com/billing/budgets
- Configura alerta cuando gastes $5, $10, $15

## 🚨 Plan de Emergencia (Si se acaban los créditos)

### Opción 1: Modo Desarrollo Local
```bash
# Backend local
cd backend
python manage.py runserver

# Frontend local
cd frontend
npm run dev
```

### Opción 2: Servicios Gratuitos Alternativos
- **Backend**: Railway.app (500 horas gratis/mes)
- **Base de Datos**: Supabase (500MB gratis)
- **Frontend**: Vercel/Netlify (gratis ilimitado)

## 📈 Optimizaciones Futuras

### Cuando tengas más créditos:
1. **Cloud CDN**: Cachear contenido estático
2. **Cloud Scheduler**: Pausar servicios automáticamente por la noche
3. **Committed Use Discounts**: 30-50% descuento con compromiso de 1-3 años

## 🔍 Monitoreo de Costos

### Ver costos en tiempo real:
```bash
# Costos del proyecto
gcloud billing projects describe argon-edge-478500-i8

# Costos por servicio
gcloud billing accounts list
```

### Dashboard de costos:
https://console.cloud.google.com/billing/

## ⚠️ Importante

Con las optimizaciones actuales:
- El sistema funcionará perfectamente para desarrollo y pruebas
- Puede haber latencia inicial (cold start) de 1-2 segundos
- La base de datos es adecuada para hasta 100 usuarios concurrentes
- **Costo estimado**: $14-19/mes (vs $52/mes anterior)

## 🎯 Próximos Pasos

1. **Monitorear uso diario** en el dashboard de GCP
2. **Pausar servicios** cuando no los uses activamente
3. **Considerar alternativas gratuitas** si los créditos se agotan
4. **Configurar alertas de presupuesto** para evitar sorpresas
