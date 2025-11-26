# Resolver Problema de Facturación

## Problema Actual

La cuenta de facturación `01BB05-89A92F-50D74C` asociada a `matilqsabe@gmail.com` no está en buen estado ("not in good standing"), lo que impide crear nuevos recursos en GCP.

## Pasos para Resolver

### 1. Verificar Estado de Facturación
1. Ve a: https://console.cloud.google.com/billing
2. Inicia sesión con `matilqsabe@gmail.com`
3. Selecciona la cuenta "Mi cuenta de facturación"
4. Verifica si hay:
   - ⚠️ Alertas o notificaciones
   - 💳 Problemas con el método de pago
   - 💰 Saldo pendiente
   - 🚫 Límites de crédito alcanzados

### 2. Actualizar Método de Pago
Si el método de pago está vencido o rechazado:
1. Ve a "Métodos de pago"
2. Agrega o actualiza tu tarjeta de crédito/débito
3. Verifica que la tarjeta esté activa y tenga fondos

### 3. Resolver Saldo Pendiente
Si hay facturas pendientes:
1. Ve a "Transacciones"
2. Paga cualquier saldo pendiente
3. Espera 24-48 horas para que se actualice el estado

### 4. Verificar Límites
Si alcanzaste límites de crédito:
1. Ve a "Presupuestos y alertas"
2. Ajusta los límites según sea necesario
3. Contacta a soporte de GCP si necesitas aumentar límites

## Alternativa: Usar Proyecto Existente

Mientras resuelves la facturación, podemos usar el proyecto `cmms-somacorv2` que ya tiene facturación funcionando:

```bash
gcloud config set project cmms-somacorv2
```

Este proyecto ya tiene:
- ✅ Facturación activa
- ✅ Cloud SQL configurado
- ✅ Cloud Run desplegado
- ✅ APIs habilitadas

## Contacto con Soporte

Si el problema persiste:
1. Ve a: https://console.cloud.google.com/support
2. Crea un caso de soporte
3. Categoría: "Facturación"
4. Describe el problema: "Billing account not in good standing"

## Verificación Rápida

Ejecuta este comando para verificar el estado:
```bash
gcloud billing accounts describe 01BB05-89A92F-50D74C
```

Debería mostrar `open: true` sin errores.

---

**Nota**: Una vez resuelto el problema de facturación, podremos crear recursos en `cmms-somacor-v3` o `cmms-somacor-prod`.
