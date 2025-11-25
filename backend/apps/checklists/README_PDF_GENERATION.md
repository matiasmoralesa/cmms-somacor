# Generación de PDFs para Checklists

## Descripción

El sistema genera automáticamente PDFs de los checklists completados. Sin embargo, la generación de PDFs es **opcional y no bloqueante**, lo que significa que si falla, el checklist se guarda de todas formas.

## Comportamiento

### Generación Automática

Cuando se completa un checklist:
1. El sistema intenta generar un PDF automáticamente
2. Si tiene éxito, el PDF se sube a Cloud Storage y se guarda la URL en `pdf_url`
3. Si falla (por ejemplo, por falta de dependencias), el checklist se guarda sin PDF

### Mensajes de Log

El sistema registra diferentes mensajes según el resultado:

- **Éxito**: `"PDF generated and uploaded successfully for checklist {id}"`
- **Storage no configurado**: `"GCP Storage client not configured - PDF generation skipped"`
- **Dependencias faltantes**: `"PDF generation dependencies not available for checklist {id}"`
- **Error general**: `"Error generating PDF for checklist {id}: {error}"`

## Regeneración Manual de PDFs

Si un checklist se guardó sin PDF, puedes regenerarlo manualmente usando el endpoint:

```http
POST /api/v1/checklists/responses/{id}/regenerate_pdf/
```

**Respuesta exitosa:**
```json
{
  "message": "PDF generado exitosamente",
  "pdf_url": "https://storage.googleapis.com/..."
}
```

**Respuesta de error:**
```json
{
  "error": "No se pudo generar el PDF",
  "message": "Verifique que LibreOffice esté instalado y que el servicio de almacenamiento esté configurado"
}
```

## Requisitos para Generación de PDFs

### Dependencias Python

Las siguientes librerías están incluidas en `requirements.txt`:
- `reportlab==4.0.7` - Para generación de PDFs
- `Pillow==10.1.0` - Para manejo de imágenes

### LibreOffice (Opcional)

**Nota**: Actualmente el sistema usa solo ReportLab y NO requiere LibreOffice. Si en el futuro se necesita LibreOffice para conversiones de documentos:

#### Windows
1. Descargar de: https://www.libreoffice.org/download/download/
2. Instalar en la ruta por defecto
3. Agregar al PATH: `C:\Program Files\LibreOffice\program`

#### Linux
```bash
sudo apt-get install libreoffice
```

#### macOS
```bash
brew install libreoffice
```

## Verificar Estado de PDFs

### Obtener PDF de un Checklist

```http
GET /api/v1/checklists/responses/{id}/pdf/
```

**Si el PDF existe:**
```json
{
  "pdf_url": "https://storage.googleapis.com/..."
}
```

**Si no existe:**
```json
{
  "error": "PDF no disponible",
  "message": "El PDF no se generó automáticamente. Use el endpoint /regenerate_pdf/ para generarlo."
}
```

## Troubleshooting

### El PDF no se genera automáticamente

**Posibles causas:**
1. Cloud Storage no está configurado (modo desarrollo local)
2. Error en las dependencias de ReportLab
3. Datos del checklist incompletos o corruptos

**Solución:**
1. Verificar logs del servidor para ver el error específico
2. Intentar regenerar manualmente con el endpoint `/regenerate_pdf/`
3. Verificar que las variables de entorno de GCP estén configuradas

### Error "PDF generation dependencies not available"

**Causa:** Falta alguna dependencia de Python

**Solución:**
```bash
pip install -r requirements.txt
```

### Error al subir a Cloud Storage

**Causa:** Credenciales de GCP no configuradas o bucket no existe

**Solución:**
1. Verificar variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`
2. Verificar que el bucket existe en GCP
3. Verificar permisos de la cuenta de servicio

## Desarrollo Local sin GCP

Si estás desarrollando localmente sin acceso a GCP:

1. Los checklists se guardarán sin PDF (campo `pdf_url` será `null`)
2. No habrá errores ni bloqueos
3. Los logs mostrarán: `"GCP Storage client not configured - PDF generation skipped"`
4. Cuando configures GCP, podrás regenerar los PDFs manualmente

## Formato del PDF

El PDF generado incluye:

### Encabezado
- Nombre de la plantilla
- Código de la plantilla

### Información del Activo
- Nombre y código del activo
- Tipo de vehículo
- Patente
- Operador y turno
- Fecha de completado
- Horómetro/Kilometraje

### Items de Inspección
- Agrupados por sección
- Pregunta, respuesta y observaciones
- Formato visual con colores

### Pie de Página
- Puntaje obtenido vs mínimo
- Estado (APROBADO/NO APROBADO)
- Firma del operador
- Fecha de generación del documento

## API Endpoints Relacionados

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/checklists/responses/` | POST | Crear checklist (genera PDF automáticamente) |
| `/api/v1/checklists/responses/{id}/pdf/` | GET | Obtener URL del PDF |
| `/api/v1/checklists/responses/{id}/regenerate_pdf/` | POST | Regenerar PDF manualmente |

## Logs Importantes

Para debugging, busca estos mensajes en los logs:

```
INFO - Starting PDF generation for checklist {id}
INFO - PDF generated and uploaded successfully for checklist {id}
WARNING - GCP Storage client not configured - PDF generation skipped
WARNING - PDF generation dependencies not available for checklist {id}
ERROR - Error generating PDF for checklist {id}: {error}
```

## Mejoras Futuras

- [ ] Generación de PDFs en background con Celery
- [ ] Notificación al usuario cuando el PDF esté listo
- [ ] Plantillas de PDF personalizables por tipo de vehículo
- [ ] Inclusión de fotos en el PDF
- [ ] Firma digital en el PDF
