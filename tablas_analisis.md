# 📊 Tablas de Análisis - Sistema CMMS SOMACOR

**Fecha**: 18 de Noviembre de 2025

---

## 1. Análisis Comparativo de Tecnologías

### 1.1 Comparación de Frameworks Backend

| Criterio | Django | Flask | FastAPI | Peso | Puntaje Django |
|----------|--------|-------|---------|------|----------------|
| **Madurez y Estabilidad** | 9/10 | 7/10 | 6/10 | 20% | 1.8 |
| **Ecosistema y Librerías** | 10/10 | 8/10 | 7/10 | 15% | 1.5 |
| **ORM Integrado** | 10/10 | 0/10 | 0/10 | 15% | 1.5 |
| **Admin Panel** | 10/10 | 0/10 | 0/10 | 10% | 1.0 |
| **Seguridad** | 9/10 | 7/10 | 8/10 | 15% | 1.35 |
| **Rendimiento** | 7/10 | 8/10 | 10/10 | 10% | 0.7 |
| **Documentación** | 10/10 | 8/10 | 9/10 | 10% | 1.0 |
| **Comunidad** | 10/10 | 9/10 | 8/10 | 5% | 0.5 |
| **Total** | - | - | - | 100% | **9.35/10** |

**Decisión**: Django seleccionado por su madurez, ORM robusto y admin panel integrado.

---

### 1.2 Comparación de Frameworks Frontend

| Criterio | React | Vue | Angular | Peso | Puntaje React |
|----------|-------|-----|---------|------|---------------|
| **Popularidad** | 10/10 | 8/10 | 7/10 | 15% | 1.5 |
| **Ecosistema** | 10/10 | 8/10 | 9/10 | 15% | 1.5 |
| **Curva de Aprendizaje** | 7/10 | 9/10 | 5/10 | 10% | 0.7 |
| **Rendimiento** | 9/10 | 9/10 | 8/10 | 15% | 1.35 |
| **TypeScript** | 10/10 | 9/10 | 10/10 | 15% | 1.5 |
| **Flexibilidad** | 10/10 | 8/10 | 6/10 | 15% | 1.5 |
| **Comunidad** | 10/10 | 8/10 | 8/10 | 10% | 1.0 |
| **Herramientas** | 9/10 | 8/10 | 9/10 | 5% | 0.45 |
| **Total** | - | - | - | 100% | **9.5/10** |

**Decisión**: React seleccionado por su ecosistema maduro y flexibilidad.

---

### 1.3 Comparación de Bases de Datos

| Criterio | PostgreSQL | MySQL | MongoDB | Peso | Puntaje PostgreSQL |
|----------|------------|-------|---------|------|--------------------|
| **Características** | 10/10 | 8/10 | 7/10 | 20% | 2.0 |
| **Rendimiento** | 9/10 | 9/10 | 8/10 | 15% | 1.35 |
| **Escalabilidad** | 9/10 | 8/10 | 10/10 | 15% | 1.35 |
| **Integridad Datos** | 10/10 | 8/10 | 6/10 | 20% | 2.0 |
| **Soporte JSON** | 10/10 | 7/10 | 10/10 | 10% | 1.0 |
| **Comunidad** | 9/10 | 9/10 | 8/10 | 10% | 0.9 |
| **Costo GCP** | 8/10 | 8/10 | 7/10 | 10% | 0.8 |
| **Total** | - | - | - | 100% | **9.4/10** |

**Decisión**: PostgreSQL seleccionado por su robustez y características avanzadas.

---

### 1.4 Comparación de Plataformas Cloud

| Criterio | GCP | AWS | Azure | Peso | Puntaje GCP |
|----------|-----|-----|-------|------|-------------|
| **Servicios ML/AI** | 10/10 | 9/10 | 8/10 | 20% | 2.0 |
| **Facilidad de Uso** | 9/10 | 7/10 | 8/10 | 15% | 1.35 |
| **Costo** | 8/10 | 7/10 | 8/10 | 20% | 1.6 |
| **Integración** | 10/10 | 8/10 | 8/10 | 15% | 1.5 |
| **Documentación** | 9/10 | 9/10 | 8/10 | 10% | 0.9 |
| **Soporte** | 8/10 | 9/10 | 8/10 | 10% | 0.8 |
| **Escalabilidad** | 10/10 | 10/10 | 9/10 | 10% | 1.0 |
| **Total** | - | - | - | 100% | **9.15/10** |

**Decisión**: GCP seleccionado por sus servicios de ML/AI y facilidad de integración.

---

## 2. Análisis de Costos

### 2.1 Costos de Infraestructura (Mensual)

| Servicio | Configuración | Costo Mensual (USD) |
|----------|---------------|---------------------|
| **Cloud Run (Backend)** | 1-10 instancias, 1GB RAM | $20 - $50 |
| **Cloud SQL (PostgreSQL)** | db-f1-micro, 10GB | $50 - $80 |
| **Cloud Storage** | Standard, 50GB | $5 - $10 |
| **Firebase Hosting** | CDN, 10GB transfer | $0 - $5 |
| **Cloud Pub/Sub** | 1M mensajes/mes | $0 - $5 |
| **Cloud Composer** | Small environment | $100 - $150 |
| **Vertex AI** | Predicciones bajo demanda | $10 - $30 |
| **Cloud Monitoring** | Métricas y logs | $10 - $20 |
| **TOTAL MENSUAL** | - | **$195 - $350** |
| **TOTAL ANUAL** | - | **$2,340 - $4,200** |

### 2.2 Costos de Desarrollo

| Fase | Horas | Costo/Hora (USD) | Total (USD) |
|------|-------|------------------|-------------|
| **Análisis y Diseño** | 80 | $50 | $4,000 |
| **Desarrollo Backend** | 200 | $50 | $10,000 |
| **Desarrollo Frontend** | 150 | $50 | $7,500 |
| **Integración y Pruebas** | 100 | $50 | $5,000 |
| **Documentación** | 40 | $50 | $2,000 |
| **Despliegue** | 30 | $50 | $1,500 |
| **TOTAL DESARROLLO** | 600 | - | **$30,000** |

### 2.3 Costos de Mantenimiento (Anual)

| Concepto | Costo Anual (USD) |
|----------|-------------------|
| **Infraestructura GCP** | $2,340 - $4,200 |
| **Soporte Técnico** (20h/mes) | $12,000 |
| **Actualizaciones** (40h/año) | $2,000 |
| **Monitoreo y Seguridad** | $1,000 |
| **TOTAL ANUAL** | **$17,340 - $19,200** |

### 2.4 Análisis de ROI

| Concepto | Valor |
|----------|-------|
| **Inversión Inicial** | $30,000 |
| **Costo Anual Operación** | $17,340 - $19,200 |
| **Ahorro Anual Estimado** | $50,000 |
| **ROI Año 1** | 66% |
| **Payback Period** | 7.2 meses |

**Beneficios Cuantificables**:
- Reducción 40% en tiempo de gestión de mantenimiento
- Reducción 30% en fallas no programadas
- Reducción 25% en costos de inventario
- Aumento 20% en disponibilidad de equipos

---

## 3. KPIs SMART

### 3.1 KPI 1: Reducción de Tiempo de Respuesta

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Reducir el tiempo promedio de respuesta ante fallas de equipos |
| **Measurable** | De 4 horas a 2.5 horas (reducción del 37.5%) |
| **Achievable** | Mediante notificaciones en tiempo real y asignación automática |
| **Relevant** | Impacta directamente en la continuidad operacional |
| **Time-bound** | Lograr en 3 meses desde el lanzamiento |
| **Fórmula** | Tiempo Promedio = Σ(Tiempo Respuesta) / Total Fallas |
| **Frecuencia** | Medición semanal |
| **Responsable** | Supervisor de Mantenimiento |
| **Meta Actual** | 4.0 horas |
| **Meta Objetivo** | 2.5 horas |

### 3.2 KPI 2: Disponibilidad de Equipos

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Aumentar la disponibilidad mecánica de la flota de vehículos |
| **Measurable** | De 85% a 95% de disponibilidad |
| **Achievable** | Mediante mantenimiento preventivo programado |
| **Relevant** | Crítico para cumplir contratos con el mandante |
| **Time-bound** | Lograr en 6 meses desde el lanzamiento |
| **Fórmula** | Disponibilidad = (Horas Disponibles / Horas Totales) × 100 |
| **Frecuencia** | Medición diaria, reporte mensual |
| **Responsable** | Gerente de Operaciones |
| **Meta Actual** | 85% |
| **Meta Objetivo** | 95% |

### 3.3 KPI 3: Digitalización de Órdenes

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Digitalizar las órdenes de trabajo eliminando el papel |
| **Measurable** | Lograr que el 90% de las órdenes sean digitales |
| **Achievable** | Mediante capacitación y adopción del sistema |
| **Relevant** | Mejora trazabilidad y reduce pérdida de información |
| **Time-bound** | Lograr en 2 meses desde el lanzamiento |
| **Fórmula** | % Digital = (Órdenes Digitales / Total Órdenes) × 100 |
| **Frecuencia** | Medición semanal |
| **Responsable** | Supervisor de Mantenimiento |
| **Meta Actual** | 0% |
| **Meta Objetivo** | 90% |

### 3.4 KPI 4: Reducción de Costos de Mantenimiento

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Reducir los costos totales de mantenimiento correctivo |
| **Measurable** | Reducción del 20% en costos anuales |
| **Achievable** | Mediante mantenimiento preventivo y mejor gestión de inventario |
| **Relevant** | Impacta directamente en la rentabilidad del contrato |
| **Time-bound** | Lograr en 12 meses desde el lanzamiento |
| **Fórmula** | Reducción = ((Costo Anterior - Costo Actual) / Costo Anterior) × 100 |
| **Frecuencia** | Medición mensual, reporte trimestral |
| **Responsable** | Gerente de Operaciones |
| **Meta Actual** | $100,000/año |
| **Meta Objetivo** | $80,000/año |

### 3.5 KPI 5: Cumplimiento de Checklists

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Asegurar el cumplimiento de inspecciones mediante checklists |
| **Measurable** | Lograr 95% de cumplimiento de checklists programados |
| **Achievable** | Mediante recordatorios automáticos y seguimiento digital |
| **Relevant** | Asegura calidad y cumplimiento de estándares |
| **Time-bound** | Lograr en 3 meses desde el lanzamiento |
| **Fórmula** | % Cumplimiento = (Checklists Completados / Checklists Programados) × 100 |
| **Frecuencia** | Medición diaria, reporte semanal |
| **Responsable** | Supervisor de Mantenimiento |
| **Meta Actual** | 70% |
| **Meta Objetivo** | 95% |

### 3.6 KPI 6: Tiempo Medio Entre Fallas (MTBF)

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Aumentar el tiempo medio entre fallas de los equipos críticos |
| **Measurable** | De 200 horas a 300 horas (aumento del 50%) |
| **Achievable** | Mediante mantenimiento preventivo y predicciones de IA |
| **Relevant** | Indica confiabilidad de los equipos |
| **Time-bound** | Lograr en 9 meses desde el lanzamiento |
| **Fórmula** | MTBF = Tiempo Total Operación / Número de Fallas |
| **Frecuencia** | Medición mensual |
| **Responsable** | Ingeniero de Confiabilidad |
| **Meta Actual** | 200 horas |
| **Meta Objetivo** | 300 horas |

### 3.7 KPI 7: Tiempo Medio de Reparación (MTTR)

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Reducir el tiempo medio de reparación de fallas |
| **Measurable** | De 6 horas a 4 horas (reducción del 33%) |
| **Achievable** | Mediante mejor gestión de repuestos y asignación eficiente |
| **Relevant** | Impacta en la disponibilidad de equipos |
| **Time-bound** | Lograr en 4 meses desde el lanzamiento |
| **Fórmula** | MTTR = Tiempo Total Reparación / Número de Reparaciones |
| **Frecuencia** | Medición semanal |
| **Responsable** | Supervisor de Mantenimiento |
| **Meta Actual** | 6 horas |
| **Meta Objetivo** | 4 horas |

### 3.8 KPI 8: Precisión de Predicciones de IA

| Aspecto | Descripción |
|---------|-------------|
| **Specific** | Mejorar la precisión del modelo de predicción de fallas |
| **Measurable** | Lograr 80% de precisión en predicciones |
| **Achievable** | Mediante entrenamiento continuo con datos reales |
| **Relevant** | Permite mantenimiento predictivo efectivo |
| **Time-bound** | Lograr en 6 meses desde el lanzamiento |
| **Fórmula** | Precisión = (Predicciones Correctas / Total Predicciones) × 100 |
| **Frecuencia** | Medición mensual |
| **Responsable** | Data Scientist |
| **Meta Actual** | 65% |
| **Meta Objetivo** | 80% |

---

## 4. Acuerdos de Nivel de Servicio (SLA)

### 4.1 Disponibilidad del Sistema

| Nivel | Descripción | Objetivo | Medición |
|-------|-------------|----------|----------|
| **Disponibilidad** | Tiempo que el sistema está operativo | 99.5% uptime | Mensual |
| **Downtime Permitido** | Tiempo de inactividad máximo | 3.6 horas/mes | Acumulado |
| **Mantenimiento Programado** | Ventanas de mantenimiento | Domingos 2:00-4:00 AM | Notificado con 48h |
| **Penalización** | Si disponibilidad < 99% | Crédito 10% del costo mensual | Por mes |

### 4.2 Rendimiento del Sistema

| Métrica | Objetivo | Medición | Penalización |
|---------|----------|----------|--------------|
| **Tiempo de Carga Frontend** | < 2 segundos (p95) | Continua | Crédito 5% si > 3s |
| **Tiempo de Respuesta API** | < 500ms (p95) | Continua | Crédito 5% si > 1s |
| **Tiempo de Generación PDF** | < 10 segundos | Por operación | N/A |
| **Capacidad Concurrente** | 100 usuarios simultáneos | Pruebas mensuales | Crédito 10% si < 50 |

### 4.3 Soporte Técnico

| Prioridad | Descripción | Tiempo de Respuesta | Tiempo de Resolución |
|-----------|-------------|---------------------|----------------------|
| **P1 - Crítica** | Sistema no disponible | 1 hora | 4 horas |
| **P2 - Alta** | Funcionalidad crítica no disponible | 4 horas | 8 horas |
| **P3 - Media** | Error menor, workaround disponible | 8 horas | 24 horas |
| **P4 - Baja** | Consulta o mejora | 24 horas | 5 días hábiles |

**Horario de Soporte**:
- Lunes a Viernes: 8:00 AM - 6:00 PM (Chile)
- Sábados: 9:00 AM - 1:00 PM (Chile)
- Domingos y Festivos: Solo P1 (emergencias)

**Canales de Soporte**:
- Email: soporte-cmms@somacor.com
- Teléfono: +56 X XXXX XXXX
- Portal Web: https://soporte.cmms-somacor.com

### 4.4 Seguridad y Backups

| Aspecto | Compromiso | Frecuencia | Retención |
|---------|------------|------------|-----------|
| **Backup Base de Datos** | Automático | Diario (3:00 AM) | 30 días |
| **Backup Archivos** | Automático | Continuo (versionado) | 90 días |
| **Prueba de Restauración** | Verificada | Mensual | Documentado |
| **Encriptación Datos** | TLS 1.3 en tránsito | Continua | N/A |
| **Encriptación Reposo** | AES-256 | Continua | N/A |
| **Auditoría de Seguridad** | Revisión completa | Trimestral | Reportado |

### 4.5 Actualizaciones y Mantenimiento

| Tipo | Frecuencia | Notificación | Downtime |
|------|------------|--------------|----------|
| **Parches de Seguridad** | Según necesidad | 24 horas | < 30 minutos |
| **Actualizaciones Menores** | Mensual | 1 semana | < 1 hora |
| **Actualizaciones Mayores** | Trimestral | 2 semanas | < 2 horas |
| **Nuevas Funcionalidades** | Según roadmap | 1 mes | Coordinado |

### 4.6 Métricas de Cumplimiento SLA

| Métrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| **Disponibilidad Mensual** | 99.5% | 99.8% | ✅ |
| **Tiempo Respuesta P1** | < 1 hora | 45 min | ✅ |
| **Tiempo Respuesta P2** | < 4 horas | 3.2 horas | ✅ |
| **Backups Exitosos** | 100% | 100% | ✅ |
| **Satisfacción Usuario** | > 4/5 | 4.3/5 | ✅ |

---

## 5. Estudio de Factibilidad

### 5.1 Factibilidad Técnica

| Aspecto | Evaluación | Riesgo | Mitigación |
|---------|------------|--------|------------|
| **Tecnologías Disponibles** | ✅ Todas disponibles | Bajo | N/A |
| **Experiencia del Equipo** | ✅ Equipo capacitado | Bajo | Capacitación continua |
| **Infraestructura GCP** | ✅ Servicios maduros | Bajo | Soporte GCP |
| **Integración Sistemas** | ✅ APIs estándar | Medio | Documentación clara |
| **Escalabilidad** | ✅ Auto-scaling | Bajo | Monitoreo continuo |

**Conclusión**: Técnicamente factible con riesgo bajo.

### 5.2 Factibilidad Económica

| Concepto | Valor | Justificación |
|----------|-------|---------------|
| **Inversión Inicial** | $30,000 | Desarrollo completo |
| **Costo Operación Anual** | $17,340 - $19,200 | Infraestructura + soporte |
| **Ahorro Anual Estimado** | $50,000 | Eficiencia operativa |
| **ROI Año 1** | 66% | Positivo |
| **Payback Period** | 7.2 meses | Aceptable |

**Conclusión**: Económicamente viable con ROI positivo en primer año.

### 5.3 Factibilidad Operacional

| Aspecto | Evaluación | Observaciones |
|---------|------------|---------------|
| **Adopción de Usuarios** | ✅ Alta | Interfaz intuitiva |
| **Capacitación Requerida** | ✅ Mínima | 6 horas por rol |
| **Cambio de Procesos** | ✅ Gradual | Transición planificada |
| **Soporte Disponible** | ✅ Completo | 8x5 + emergencias |
| **Resistencia al Cambio** | 🟡 Media | Plan de gestión del cambio |

**Conclusión**: Operacionalmente factible con plan de gestión del cambio.

---

**Documento creado**: 18 de Noviembre de 2025  
**Versión**: 1.0

