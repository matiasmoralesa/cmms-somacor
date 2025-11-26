# 🚀 Inicio Rápido - MySQL Local (Temporal)

## ⚡ Configuración en 5 Pasos

### 1️⃣ Instalar MySQL

**Opción más fácil - XAMPP:**
- Descarga: https://www.apachefriends.org/
- Instala y abre el panel de control
- Click en "Start" en MySQL

**O MySQL directo:**
- Descarga: https://dev.mysql.com/downloads/installer/
- Instala con configuración por defecto

---

### 2️⃣ Configurar Base de Datos

**Ejecuta como Administrador:**
```powershell
.\setup_mysql_local.ps1
```

Este script:
- ✅ Verifica MySQL
- ✅ Crea base de datos `cmms_db`
- ✅ Crea usuario `cmms_user`
- ✅ Configura firewall
- ✅ Te da las variables para Railway

---

### 3️⃣ Probar Localmente

```powershell
.\test_mysql_local.ps1
```

Esto verifica que todo funcione antes de desplegar.

---

### 4️⃣ Configurar ngrok (RECOMENDADO)

**¿Por qué ngrok?**
- Tu IP cambia constantemente
- ngrok te da una URL estable
- Gratis y fácil

**Pasos:**
1. Descarga: https://ngrok.com/download
2. Crea cuenta gratis
3. Ejecuta:
```powershell
ngrok tcp 3306
```

4. Verás algo como:
```
Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

5. Usa esos valores en Railway ⬇️

---

### 5️⃣ Configurar Railway

Ve a tu proyecto en Railway → Settings → Variables

**Agrega estas variables:**

```
MYSQLHOST=0.tcp.ngrok.io
MYSQLPORT=12345
MYSQLUSER=cmms_user
MYSQLPASSWORD=cmms_password_2024
MYSQLDATABASE=cmms_db
```

*(Usa los valores que ngrok te dio)*

---

### 6️⃣ Desplegar

```powershell
git push origin main
```

Railway redesplega automáticamente.

---

## ✅ Verificar que Funciona

1. Ve a los logs de Railway
2. Busca: `"Running migrations..."` ✅
3. Busca: `"Superusuario admin@somacor.cl creado"` ✅
4. Busca: `"Listening at: http://0.0.0.0:8080"` ✅

---

## ⚠️ IMPORTANTE

### Mantén Corriendo:
- ✅ MySQL (XAMPP o servicio MySQL)
- ✅ ngrok (si lo usas)
- ✅ Tu PC encendida

### Si algo falla:
```powershell
# Verificar MySQL
Get-Service MySQL*

# Verificar ngrok
# Debe estar corriendo en otra terminal

# Probar conexión local
.\test_mysql_local.ps1
```

---

## 🔄 Cuando Migres a Producción

**Exportar datos:**
```powershell
mysqldump -u cmms_user -pcmms_password_2024 cmms_db > backup.sql
```

**Importar a PlanetScale/Railway:**
```bash
mysql -h nuevo_host -u nuevo_user -p nueva_db < backup.sql
```

---

## 🆘 Problemas Comunes

### "Can't connect to MySQL server"
```powershell
# Verificar que MySQL esté corriendo
Get-Service MySQL*

# Si no está corriendo
Start-Service MySQL80  # o el nombre de tu servicio
```

### "Access denied"
```sql
-- Reconectar a MySQL como root y ejecutar:
GRANT ALL PRIVILEGES ON cmms_db.* TO 'cmms_user'@'%';
FLUSH PRIVILEGES;
```

### "Connection timeout" desde Railway
- Verifica que ngrok esté corriendo
- Verifica las variables en Railway
- Verifica el firewall de Windows

### ngrok se desconecta
- ngrok gratis se desconecta cada 8 horas
- Reinicia ngrok
- Actualiza el puerto en Railway si cambió

---

## 📊 Resumen

| Paso | Comando | Tiempo |
|------|---------|--------|
| Instalar MySQL | Manual | 10 min |
| Configurar | `.\setup_mysql_local.ps1` | 2 min |
| Probar | `.\test_mysql_local.ps1` | 1 min |
| ngrok | `ngrok tcp 3306` | 1 min |
| Railway | Agregar variables | 2 min |
| Desplegar | `git push origin main` | 3 min |

**Total: ~20 minutos**

---

¿Listo para empezar? Ejecuta:
```powershell
.\setup_mysql_local.ps1
```
