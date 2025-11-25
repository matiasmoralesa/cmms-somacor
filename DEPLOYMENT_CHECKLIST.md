# ✅ Checklist de Despliegue CMMS en GCP

## 📋 Pre-Despliegue

### Requisitos de Cuenta
- [ ] Cuenta de Google Cloud Platform creada
- [ ] Método de pago configurado (tarjeta de crédito/débito)
- [ ] Créditos gratuitos de $300 activados (si aplica)
- [ ] Proyecto de GCP creado o nombre decidido

### Herramientas Instaladas
- [ ] Google Cloud SDK (`gcloud --version`)
- [ ] Firebase CLI (`firebase --version`)
- [ ] Docker (`docker --version`) - Opcional
- [ ] Python 3.11+ (`python --version`)
- [ ] Node.js 18+ (`node --version`)
- [ ] Git (`git --version`)

### Preparación del Código
- [ ] Repositorio clonado localmente
- [ ] Rama principal actualizada (`git pull`)
- [ ] Sin cambios pendientes (`git status`)
- [ ] Dependencias del backend instaladas
- [ ] Dependencias del frontend instaladas

---

## 🚀 Fase 1: Preparación (5-10 min)

### Autenticación
- [ ] Ejecutado `gcloud auth login`
- [ ] Cuenta correcta seleccionada
- [ ] Permisos de Owner o Editor verificados

### Configuración Inicial
- [ ] Navegado a `cd deployment/gcp`
- [ ] Permisos de ejecución dados (`chmod +x *.sh`)
- [ ] Ejecutado `./00-prepare-deployment.sh`
- [ ] ID del proyecto ingresado
- [ ] Región seleccionada (us-central1 recomendado)
- [ ] Archivo `.env.gcp` creado
- [ ] Archivo `DEPLOYMENT_SUMMARY.txt` guardado en lugar seguro

### Verificación de APIs
- [ ] Cloud Run API habilitada
- [ ] Cloud SQL Admin API habilitada
- [ ] Cloud Storage API habilitada
- [ ] Cloud Pub/Sub API habilitada
- [ ] Cloud Build API habilitada
- [ ] Secret Manager API habilitada
- [ ] Firebase API habilitada

---

## 🏗️ Fase 2: Infraestructura (15-20 min)

### Cloud SQL
- [ ] Ejecutado `./01-create-cloud-sql.sh`
- [ ] Instancia `cmms-db` creada
- [ ] Base de datos `cmms_prod` creada
- [ ] Usuario `cmms_user` creado
- [ ] Backups automáticos configurados
- [ ] Sin errores en logs

### Cloud Storage
- [ ] Ejecutado `./02-create-storage-buckets.sh`
- [ ] Bucket `{project}-cmms-documents` creado
- [ ] Bucket `{project}-cmms-ml-models` creado
- [ ] Bucket `{project}-cmms-reports` creado
- [ ] Bucket `{project}-cmms-backups` creado
- [ ] Permisos configurados correctamente

### Cloud Pub/Sub
- [ ] Ejecutado `./03-create-pubsub-topics.sh`
- [ ] Topic `notifications` creado
- [ ] Topic `events` creado
- [ ] Topic `alerts` creado
- [ ] Subscriptions creadas
- [ ] Dead letter queue configurada

---

## 🖥️ Fase 3: Aplicaciones (10-15 min)

### Backend (Cloud Run)
- [ ] Ejecutado `./04-deploy-backend-cloud-run.sh`
- [ ] Imagen Docker construida exitosamente
- [ ] Servicio `cmms-backend` desplegado
- [ ] Variables de entorno configuradas
- [ ] Conexión a Cloud SQL establecida
- [ ] Migraciones ejecutadas
- [ ] Health check respondiendo (200 OK)
- [ ] URL del servicio obtenida

### Frontend (Firebase Hosting)
- [ ] Ejecutado `./05-deploy-frontend-firebase.sh`
- [ ] Proyecto Firebase inicializado
- [ ] Build de producción completado
- [ ] Archivos desplegados a Firebase
- [ ] URL del frontend obtenida
- [ ] Página carga correctamente

---

## 🔧 Fase 4: Configuración Post-Despliegue (5-10 min)

### Superusuario
- [ ] Superusuario creado
- [ ] Email: `admin@cmms.com` (o personalizado)
- [ ] Password temporal configurado
- [ ] Login exitoso en el sistema
- [ ] Password cambiado a uno seguro

### Verificación de Funcionalidad
- [ ] Frontend carga sin errores
- [ ] Login funciona correctamente
- [ ] Dashboard se muestra
- [ ] API responde correctamente
- [ ] CORS configurado correctamente
- [ ] Assets estáticos cargan

### Datos Iniciales
- [ ] Roles creados (ADMIN, SUPERVISOR, OPERADOR)
- [ ] Categorías de equipos creadas
- [ ] Plantillas de checklist cargadas
- [ ] Datos de prueba cargados (opcional)

---

## 🔐 Fase 5: Seguridad (10-15 min)

### Contraseñas y Secretos
- [ ] Password de admin cambiado
- [ ] Password de base de datos seguro (generado automáticamente)
- [ ] SECRET_KEY de Django seguro (generado automáticamente)
- [ ] Archivo `DEPLOYMENT_SUMMARY.txt` guardado fuera del repo
- [ ] Archivos `.env*` en `.gitignore`

### Configuración de Seguridad
- [ ] HTTPS forzado (automático en Cloud Run)
- [ ] CORS restrictivo configurado
- [ ] DEBUG=False en producción
- [ ] ALLOWED_HOSTS configurado correctamente
- [ ] Secure cookies habilitadas

### Backups
- [ ] Backups automáticos de Cloud SQL verificados
- [ ] Política de retención configurada (7 días)
- [ ] Backup manual creado y probado
- [ ] Procedimiento de restauración documentado

---

## 📊 Fase 6: Monitoreo (10-15 min)

### Logs
- [ ] Cloud Logging configurado
- [ ] Logs del backend visibles
- [ ] Logs estructurados (JSON)
- [ ] Niveles de log apropiados
- [ ] Comando de logs guardado para referencia

### Métricas
- [ ] Cloud Monitoring habilitado
- [ ] Métricas de Cloud Run visibles
- [ ] Métricas de Cloud SQL visibles
- [ ] Dashboard básico creado

### Alertas
- [ ] Alerta de errores configurada
- [ ] Alerta de latencia configurada
- [ ] Alerta de costos configurada
- [ ] Notificaciones por email configuradas

---

## 🧪 Fase 7: Pruebas (15-20 min)

### Pruebas Funcionales
- [ ] Login/Logout funciona
- [ ] CRUD de Assets funciona
- [ ] CRUD de Work Orders funciona
- [ ] CRUD de Maintenance Plans funciona
- [ ] CRUD de Spare Parts funciona
- [ ] CRUD de Users funciona
- [ ] Checklists funcionan

### Pruebas de Integración
- [ ] Subida de archivos funciona
- [ ] Notificaciones se envían
- [ ] Filtros y búsquedas funcionan
- [ ] Paginación funciona
- [ ] Validaciones funcionan

### Pruebas de Rendimiento
- [ ] Tiempo de carga < 3 segundos
- [ ] API responde < 500ms
- [ ] Sin errores en consola del navegador
- [ ] Sin memory leaks evidentes

---

## 📱 Fase 8: Configuración Avanzada (Opcional)

### Dominio Personalizado
- [ ] Dominio comprado
- [ ] DNS configurado
- [ ] Dominio mapeado al backend
- [ ] Dominio mapeado al frontend
- [ ] Certificados SSL configurados
- [ ] Redirects configurados

### Telegram Bot
- [ ] Bot creado en BotFather
- [ ] Token obtenido
- [ ] Bot desplegado
- [ ] Comandos funcionando
- [ ] Notificaciones funcionando

### Cloud Composer (Airflow)
- [ ] Entorno creado
- [ ] DAGs desplegados
- [ ] Schedules configurados
- [ ] Workflows probados

### ML Service (Vertex AI)
- [ ] Datos de entrenamiento preparados
- [ ] Modelo entrenado
- [ ] Modelo desplegado
- [ ] Endpoint funcionando
- [ ] Predicciones funcionando

---

## 📝 Fase 9: Documentación (10-15 min)

### Documentación Técnica
- [ ] URLs de producción documentadas
- [ ] Credenciales guardadas en lugar seguro
- [ ] Procedimientos de despliegue documentados
- [ ] Procedimientos de rollback documentados
- [ ] Contactos de soporte documentados

### Documentación de Usuario
- [ ] Guía de usuario actualizada
- [ ] Videos de capacitación creados (opcional)
- [ ] FAQ actualizado
- [ ] Casos de uso documentados

### Runbooks
- [ ] Procedimiento de backup/restore
- [ ] Procedimiento de actualización
- [ ] Procedimiento de rollback
- [ ] Procedimiento de troubleshooting
- [ ] Contactos de emergencia

---

## 👥 Fase 10: Capacitación y Entrega (Variable)

### Capacitación del Equipo
- [ ] Administradores capacitados
- [ ] Supervisores capacitados
- [ ] Operadores capacitados
- [ ] Soporte técnico capacitado

### Entrega
- [ ] Demo del sistema realizada
- [ ] Documentación entregada
- [ ] Credenciales entregadas
- [ ] Soporte post-despliegue acordado
- [ ] Feedback inicial recopilado

---

## 🎯 Verificación Final

### Checklist de Producción
- [ ] Sistema accesible 24/7
- [ ] Backups funcionando
- [ ] Monitoreo activo
- [ ] Alertas configuradas
- [ ] Documentación completa
- [ ] Equipo capacitado
- [ ] Plan de soporte definido
- [ ] Plan de escalamiento definido

### Métricas de Éxito
- [ ] Uptime > 99%
- [ ] Tiempo de respuesta < 500ms
- [ ] 0 errores críticos
- [ ] Usuarios pueden trabajar sin problemas
- [ ] Feedback positivo del equipo

---

## 📊 Resumen de Tiempos

| Fase | Tiempo Estimado | Prioridad |
|------|----------------|-----------|
| Pre-Despliegue | 10-15 min | Alta |
| Preparación | 5-10 min | Alta |
| Infraestructura | 15-20 min | Alta |
| Aplicaciones | 10-15 min | Alta |
| Post-Despliegue | 5-10 min | Alta |
| Seguridad | 10-15 min | Alta |
| Monitoreo | 10-15 min | Media |
| Pruebas | 15-20 min | Alta |
| Avanzado | Variable | Baja |
| Documentación | 10-15 min | Media |
| Capacitación | Variable | Media |

**Tiempo Total Mínimo**: ~1.5-2 horas
**Tiempo Total Completo**: ~4-6 horas
**Tiempo con Opcionales**: ~1-2 semanas

---

## 🎉 Celebración

- [ ] Sistema en producción ✅
- [ ] Equipo notificado 📢
- [ ] Éxito celebrado 🎊
- [ ] Lecciones aprendidas documentadas 📝
- [ ] Mejoras futuras planificadas 🚀

---

## 📞 Contactos de Soporte

### Soporte Técnico
- Email: soporte@cmms.com
- Teléfono: +56 9 XXXX XXXX
- Horario: Lunes a Viernes 9:00-18:00

### Emergencias
- Email: emergencias@cmms.com
- Teléfono: +56 9 XXXX XXXX
- Disponibilidad: 24/7

### Documentación
- Guía de Usuario: `/USER_GUIDE.md`
- Guía de Admin: `/ADMIN_GUIDE.md`
- API Docs: `{SERVICE_URL}/api/docs/`

---

**Última Actualización**: $(date)
**Versión**: 1.0
**Estado**: ✅ Listo para Producción
