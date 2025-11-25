# Prompt Detallado para la Creación de un Sistema de Gestión de Mantenimiento (CMMS) Avanzado

## 🎯 Objetivo del Proyecto

Crear un **Sistema de Gestión de Mantenimiento Computarizado (CMMS)** moderno y distribuido, enfocado en la **predicción de fallas** y la **automatización de procesos**, optimizado para el despliegue y la operación en **Google Cloud Platform (GCP)**.

## 🚀 Arquitectura Optimizada para GCP

La arquitectura propuesta reemplaza los componentes auto-gestionados por servicios gestionados de GCP para maximizar la escalabilidad, reducir la sobrecarga operativa y aprovechar las capacidades nativas de la nube.

| Componente | Tecnología Original | Propuesta GCP | Razón de la Mejora |
| :--- | :--- | :--- | :--- |
| **Backend Deployment** | Servidor Python/Gunicorn | **Cloud Run** | Contenedores sin servidor, escalado a cero, y gestión simplificada. |
| **Frontend Deployment** | Servidor Node.js | **Firebase Hosting** | CDN global, despliegue rápido y seguro para contenido estático. |
| **Orquestación** | Apache Airflow | **Cloud Composer** (Managed Airflow) | Servicio gestionado de Airflow, elimina la gestión de infraestructura. |
| **Procesamiento Distribuido** | Dask Cluster | **Dataproc** (con Dask o Spark) | Plataforma de datos distribuida escalable y bajo demanda. |
| **Base de Datos** | SQLite/PostgreSQL (self-managed) | **Cloud SQL (PostgreSQL)** | Base de datos relacional gestionada, alta disponibilidad y copias de seguridad automáticas. |
| **Almacenamiento de Archivos** | Local/Servidor | **Cloud Storage** | Almacenamiento de objetos escalable para PDFs, imágenes y modelos ML. |
| **Machine Learning** | Scikit-learn local | **Vertex AI** (para despliegue) | Plataforma unificada para el ciclo de vida de ML, mejor para producción. |

## 🛠️ Stack Tecnológico Requerido (GCP-Optimizado)

### 1. Backend (Python)

*   **Framework:** Django (versión 4.x o superior).
*   **API:** Django REST Framework (DRF).
*   **Comunicación en Tiempo Real:** `channels` para **WebSockets**. El despliegue en Cloud Run requerirá un **servidor de canales separado** (ej. Redis en Memorystore) o el uso de un servicio como **Cloud Pub/Sub** para notificaciones asíncronas.
*   **Análisis de Datos:** `pandas`, `numpy`.
*   **Base de Datos:** Conexión a **Cloud SQL (PostgreSQL)**.
*   **Contenerización:** Archivo `Dockerfile` para empaquetar la aplicación para Cloud Run.

### 2. Frontend (Web)

*   **Framework:** React (versión 18+ o 19+).
*   **Lenguaje:** TypeScript.
*   **Build Tool:** Vite.
*   **Estilos:** Tailwind CSS.
*   **Gráficos:** `recharts` o `Nivo`.
*   **Despliegue:** Configuración para **Firebase Hosting**.

### 3. Infraestructura y Ciencia de Datos (GCP Services)

*   **Orquestación:** **Cloud Composer** (Managed Apache Airflow).
*   **Computación Distribuida:** **Dataproc** (para ejecutar cargas de trabajo de Dask o Spark bajo demanda).
*   **Base de Datos:** **Cloud SQL** (PostgreSQL).
*   **Almacenamiento:** **Cloud Storage** (para guardar modelos de ML, PDFs de checklists y archivos de usuario).
*   **Despliegue de ML:** **Vertex AI** (para servir el modelo de predicción de fallas como un endpoint).

## 🚀 Funcionalidades y Módulos Específicos

El sistema debe mantener las funcionalidades avanzadas, adaptando su implementación a los servicios de GCP:

### A. Módulos de Gestión (Backend & Frontend)

1.  **Gestión de Equipos y Activos:** CRUD completo, con almacenamiento de documentos y fotos en **Cloud Storage**.
2.  **Órdenes de Trabajo (OT):** Creación, asignación, seguimiento de estado.
3.  **Planes de Mantenimiento:** Programación de mantenimiento preventivo y predictivo.
4.  **Inventario de Repuestos:** Gestión de stock y alertas.
5.  **Checklists Dinámicos:** Generación de plantillas y almacenamiento de PDFs completados en **Cloud Storage**.

### B. Funcionalidades Avanzadas

*   **Inteligencia Artificial (Predicción de Fallas):**
    *   El modelo de ML debe ser entrenado en **Dataproc** (usando datos de Cloud SQL).
    *   El modelo final debe ser desplegado como un endpoint de **Vertex AI**.
    *   El Backend (Cloud Run) debe consumir este endpoint para generar alertas predictivas.
*   **Automatización con Cloud Composer (Airflow):**
    *   **DAG 1 (ETL/ML):** Extracción de datos de Cloud SQL, procesamiento en Dataproc, reentrenamiento del modelo y despliegue en Vertex AI.
    *   **DAG 2 (Preventivo):** Generación automática de Órdenes de Trabajo Preventivas.
    *   **DAG 3 (Reportes):** Generación de reportes diarios/semanales (usando datos de Cloud SQL) y envío por correo electrónico (vía SendGrid o similar).
*   **Tiempo Real y Notificaciones:** Uso de **Cloud Pub/Sub** para desacoplar el envío de notificaciones (ej. "OT asignada", "Alerta de falla") al Frontend y al Bot de Telegram.

### C. Bot de Telegram

*   Implementación de un bot con un **sistema de roles** (Administrador, Supervisor, Técnico, Operador, Invitado).
*   **Comandos Mínimos:** `/status`, `/equipos`, `/ordenes`, `/pendientes`, `/alertas`, `/kpis`.
*   El bot debe ser desplegado como un **Cloud Function** o un servicio ligero en **Cloud Run** para manejar los webhooks de Telegram.

## ⚙️ Requisitos de Despliegue en GCP

El proyecto debe incluir la configuración necesaria para un despliegue "Infrastructure as Code" (IaC) en GCP:

1.  **Contenerización:** Archivos `Dockerfile` y `docker-compose.yml` para desarrollo local.
2.  **Configuración de GCP:** Archivos de configuración para **Cloud Run**, **Cloud SQL**, y scripts de inicialización para **Cloud Composer** y **Dataproc**.
3.  **Scripts de Despliegue:** Scripts de `gcloud` para el despliegue de los servicios principales.

Este prompt mejorado proporciona una base sólida para construir un CMMS avanzado, aprovechando al máximo la infraestructura y los servicios gestionados de Google Cloud Platform.
