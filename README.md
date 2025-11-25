# 🏭 Sistema CMMS Avanzado - Gestión de Mantenimiento Inteligente

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4.svg)](https://cloud.google.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema de Gestión de Mantenimiento Computarizado (CMMS) moderno y distribuido, optimizado para Google Cloud Platform. Incluye predicción de fallas mediante inteligencia artificial, automatización de procesos con Airflow, y gestión integral de activos industriales.

## 🚀 Características Principales

### 🔧 Gestión de Mantenimiento
- **Órdenes de Trabajo**: Creación, asignación y seguimiento completo
- **Mantenimiento Preventivo**: Planes programados con recurrencia configurable
- **Mantenimiento Predictivo**: Predicción de fallas con Machine Learning
- **Checklists Digitales**: 5 plantillas profesionales basadas en estándares industriales

### 📊 Gestión de Activos
- **Inventario Completo**: 5 tipos de vehículos (Camión Supersucker, Camionetas MDO, Retroexcavadora, Cargador Frontal, Minicargador)
- **Seguimiento en Tiempo Real**: Estado operativo, ubicación, y condición
- **Historial Completo**: Registro de mantenimientos, reparaciones y actualizaciones
- **Gestión de Documentos**: Almacenamiento en Cloud Storage

### 🤖 Inteligencia Artificial
- **Predicción de Fallas**: Modelo ML entrenado con datos históricos
- **Alertas Automáticas**: Notificaciones cuando la probabilidad de falla supera el 70%
- **Reentrenamiento Automático**: Pipeline ETL con Airflow y Dataproc
- **Dashboard Predictivo**: Visualización de salud de activos y tendencias

### 📱 Acceso Multi-Canal
- **Web App**: Interfaz React moderna y responsive
- **Bot de Telegram**: Comandos específicos por rol (ADMIN, SUPERVISOR, OPERADOR)
- **API REST**: Documentación completa con Swagger/OpenAPI
- **Notificaciones en Tiempo Real**: Cloud Pub/Sub + WebSockets

### 📈 Reportes y Analytics
- **KPIs Automáticos**: MTBF, MTTR, OEE, disponibilidad
- **Reportes Programados**: Generación automática semanal con Airflow
- **Exportación**: CSV, JSON, PDF
- **Dashboards Interactivos**: Gráficos con Recharts

## 🏗️ Arquitectura

### Stack Tecnológico

**Backend:**
- Django 4.2 + Django REST Framework
- PostgreSQL 14 (Cloud SQL)
- Celery para tareas asíncronas
- JWT para autenticación

**Frontend:**
- React 18 + TypeScript
- Vite para build
- Tailwind CSS para estilos
- Recharts para visualizaciones
- Zustand para state management

**Machine Learning:**
- Scikit-learn para modelos
- Vertex AI para deployment
- Apache Airflow (Cloud Composer) para orquestación
- Dataproc para procesamiento distribuido

**Infraestructura GCP:**
- Cloud Run (Backend)
- Cloud Storage (Frontend + Archivos)
- Cloud SQL (Base de datos)
- Cloud Pub/Sub (Notificaciones)
- Cloud Composer (Airflow)
- Vertex AI (ML)

### Arquitectura de 3 Capas

```
┌─────────────────────────────────────────────────────────┐
│  CAPA DE CLIENTE                                        │
│  • React Web App (Cloud Storage)                        │
│  • Telegram Bot (Cloud Run)                             │
│  • App Móvil (Futuro)                                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  CAPA DE LÓGICA (Backend Core)                          │
│  • Django REST API (Cloud Run)                          │
│  • Autenticación JWT                                    │
│  • Lógica de negocio                                    │
│  • Celery Workers                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  CAPA DE DATOS E INTELIGENCIA                           │
│  • PostgreSQL (Cloud SQL) - Datos transaccionales       │
│  • Cloud Storage - Archivos y documentos                │
│  • Vertex AI - Predicciones ML                          │
│  • Cloud Composer - Orquestación Airflow                │
└─────────────────────────────────────────────────────────┘
```

## 📦 Instalación

### Prerrequisitos

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- Google Cloud SDK
- Docker (opcional)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/cmms-somacor.git
cd cmms-somacor
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con la URL de tu backend

# Iniciar servidor de desarrollo
npm run dev
```

### 4. Configurar Base de Datos Local

```bash
# Usando Docker
docker-compose up -d

# O manualmente con PostgreSQL
createdb cmms_db
psql cmms_db < schema.sql
```

## 🚀 Despliegue en GCP

### Despliegue Rápido

```bash
# Configurar proyecto GCP
gcloud config set project TU_PROJECT_ID

# Desplegar backend
cd backend
gcloud run deploy cmms-backend-service \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# Desplegar frontend
cd frontend
npm run build
gcloud storage cp -r dist/* gs://cmms-frontend-bucket/
```

### Despliegue Completo

Ver [GUIA_DESPLIEGUE_PRODUCCION.md](GUIA_DESPLIEGUE_PRODUCCION.md) para instrucciones detalladas.

## 🔑 Credenciales de Acceso

**Usuario Administrador por Defecto:**
- Email: `admin@somacor.com`
- Password: `admin123`
- Rol: Administrador

**⚠️ IMPORTANTE:** Cambiar estas credenciales en producción.

## 📚 Documentación

- [Guía de Despliegue](GUIA_DESPLIEGUE_PRODUCCION.md)
- [Documentación de API](https://cmms-backend-service.run.app/api/docs/)
- [Guía de Usuario](USER_GUIDE.md)
- [Guía de Administrador](ADMIN_GUIDE.md)
- [Arquitectura del Sistema](ARQUITECTURA.md)

## 🧪 Testing

```bash
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm run test

# E2E
npm run test:e2e
```

## 📊 Módulos Implementados

- ✅ Autenticación y Autorización (3 roles)
- ✅ Gestión de Activos y Vehículos
- ✅ Órdenes de Trabajo
- ✅ Mantenimiento Preventivo
- ✅ Checklists Digitales (5 plantillas)
- ✅ Inventario de Repuestos
- ✅ Predicción de Fallas (ML)
- ✅ Reportes y Analytics
- ✅ Bot de Telegram
- ✅ Notificaciones en Tiempo Real
- ✅ Dashboard Interactivo
- ✅ Gestión de Usuarios
- ✅ Actualización de Estado de Máquinas

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **Equipo Somacor** - *Desarrollo inicial*

## 🙏 Agradecimientos

- Inspirado en estándares industriales de mantenimiento
- Basado en mejores prácticas de CMMS empresariales
- Optimizado para Google Cloud Platform

## 📞 Soporte

Para soporte y preguntas:
- 📧 Email: soporte@somacor.com
- 💬 Telegram: @SomacorBot
- 🐛 Issues: [GitHub Issues](https://github.com/TU_USUARIO/cmms-somacor/issues)

## 🗺️ Roadmap

- [ ] App móvil nativa (Flutter/React Native)
- [ ] Procesamiento de imágenes con ML
- [ ] Chat en tiempo real con Firebase
- [ ] Integración con sensores IoT
- [ ] Dashboard de BI avanzado
- [ ] Integración con ERP

---

**Desarrollado con ❤️ para la industria del mantenimiento**
