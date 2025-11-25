# Configuración Completa del Bot de Telegram - Paso a Paso

## 📋 Información del Bot

**Bot Token:** `8206203157:AAHx9v2uTonXA8T5Oa4vaF9MKwGD7qxJJ38`

## 🚀 Paso 1: Configurar Comandos del Bot

### Comandos Básicos

Ir a BotFather y configurar los siguientes comandos:

```
/start - Iniciar el bot y obtener tu Chat ID
/help - Mostrar ayuda y comandos disponibles
/link - Vincular tu cuenta CMMS
/unlink - Desvincular tu cuenta CMMS
/status - Ver estado de vinculación
/test - Enviar notificación de prueba
```

### Cómo configurar en BotFather:

1. Abrir chat con @BotFather
2. Enviar `/setcommands`
3. Seleccionar tu bot
4. Copiar y pegar:

```
start - Iniciar el bot y obtener tu Chat ID
help - Mostrar ayuda y comandos disponibles
link - Vincular tu cuenta CMMS
unlink - Desvincular tu cuenta CMMS
status - Ver estado de vinculación
test - Enviar notificación de prueba
```

## 🔧 Paso 2: Configurar Descripción del Bot

### Descripción Corta (About)

```
Bot oficial del Sistema CMMS para recibir notificaciones de órdenes de trabajo, mantenimiento y alertas en tiempo real.
```

### Descripción Larga (Description)

```
🔧 Bot Oficial del Sistema CMMS

Recibe notificaciones instantáneas sobre:
• 📋 Órdenes de trabajo asignadas
• ⚙️ Mantenimiento programado
• 📦 Alertas de inventario
• 🔮 Predicciones de fallas
• 🚨 Alertas críticas del sistema

Para vincular tu cuenta:
1. Obtén tu Chat ID con /start
2. Ingresa a la aplicación CMMS
3. Ve a Configuración > Notificaciones
4. Ingresa tu Chat ID y vincula

¿Necesitas ayuda? Usa /help
```

### Cómo configurar:

1. Abrir chat con @BotFather
2. Para descripción corta: `/setabouttext`
3. Para descripción larga: `/setdescription`
4. Seleccionar tu bot
5. Pegar el texto correspondiente

## 🖼️ Paso 3: Configurar Imagen del Bot

### Foto de Perfil

Crear o usar una imagen de 512x512 px con:
- Logo del sistema CMMS
- Colores corporativos
- Icono de notificación o campana

### Cómo configurar:

1. Abrir chat con @BotFather
2. Enviar `/setuserpic`
3. Seleccionar tu bot
4. Enviar la imagen

## 🌐 Paso 4: Crear Webhook Handler

Voy a crear un endpoint en Django para manejar los mensajes del bot:

