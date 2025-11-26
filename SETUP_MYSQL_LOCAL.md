# Configuración MySQL Local para Railway (Temporal)

## ⚠️ ADVERTENCIA
Esta es una solución TEMPORAL. Para producción real, migra a PlanetScale o Railway MySQL.

---

## Paso 1: Instalar MySQL en Windows

### Opción A: MySQL Installer (Recomendado)
1. Descarga: https://dev.mysql.com/downloads/installer/
2. Ejecuta el instalador
3. Selecciona "Developer Default"
4. Configura password para root (guárdala bien)
5. Puerto por defecto: 3306

### Opción B: XAMPP (Más fácil)
1. Descarga: https://www.apachefriends.org/
2. Instala XAMPP
3. Inicia MySQL desde el panel de control
4. Puerto por defecto: 3306

---

## Paso 2: Crear Base de Datos

Abre MySQL Workbench o la consola MySQL:

```sql
CREATE DATABASE cmms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cmms_user'@'%' IDENTIFIED BY 'cmms_password_2024';
GRANT ALL PRIVILEGES ON cmms_db.* TO 'cmms_user'@'%';
FLUSH PRIVILEGES;
```

---

## Paso 3: Configurar Acceso Remoto

### 3.1 Editar my.ini (MySQL) o my.cnf (XAMPP)

**Ubicación:**
- MySQL: `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
- XAMPP: `C:\xampp\mysql\bin\my.ini`

**Cambiar:**
```ini
# Busca esta línea:
bind-address = 127.0.0.1

# Cámbiala a:
bind-address = 0.0.0.0
```

### 3.2 Reiniciar MySQL

**MySQL:**
```powershell
Restart-Service MySQL80
```

**XAMPP:**
- Para y reinicia MySQL desde el panel de control

---

## Paso 4: Configurar Firewall de Windows

```powershell
# Ejecuta como Administrador
New-NetFirewallRule -DisplayName "MySQL Server" -Direction Inbound -LocalPort 3306 -Protocol TCP -Action Allow
```

---

## Paso 5: Obtener tu IP Pública

### Opción A: Usar ngrok (RECOMENDADO para IP dinámica)

1. Descarga ngrok: https://ngrok.com/download
2. Crea cuenta gratis
3. Ejecuta:
```powershell
ngrok tcp 3306
```

4. Obtendrás algo como:
```
Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:3306
```

5. Usa esto en Railway:
   - Host: `0.tcp.ngrok.io`
   - Port: `12345`

### Opción B: IP Pública Directa (Solo si tienes IP estática)

```powershell
# Ver tu IP pública
Invoke-RestMethod -Uri "https://api.ipify.org?format=json"
```

**⚠️ Problema:** Tu IP cambiará y romperá la conexión.

---

## Paso 6: Configurar Variables en Railway

Ve a tu proyecto en Railway → Settings → Variables:

### Si usas ngrok:
```
MYSQLHOST=0.tcp.ngrok.io
MYSQLPORT=12345
MYSQLUSER=cmms_user
MYSQLPASSWORD=cmms_password_2024
MYSQLDATABASE=cmms_db
```

### Si usas IP directa:
```
MYSQLHOST=tu.ip.publica.aqui
MYSQLPORT=3306
MYSQLUSER=cmms_user
MYSQLPASSWORD=cmms_password_2024
MYSQLDATABASE=cmms_db
```

---

## Paso 7: Configurar Router (Si usas IP directa)

1. Accede a tu router (usualmente 192.168.1.1)
2. Busca "Port Forwarding" o "Reenvío de puertos"
3. Crea regla:
   - Puerto externo: 3306
   - Puerto interno: 3306
   - IP interna: Tu IP local (192.168.x.x)
   - Protocolo: TCP

---

## Paso 8: Probar Conexión Local

Antes de desplegar, prueba localmente:

```powershell
cd backend
python manage.py migrate
python manage.py create_admin
python manage.py runserver
```

---

## Paso 9: Desplegar a Railway

```powershell
git push origin main
```

Railway redesplega automáticamente.

---

## 🔍 Verificar Conexión desde Railway

Después del deployment, verifica los logs en Railway:
- ✅ "Running migrations..." = Conexión exitosa
- ❌ "Can't connect to MySQL server" = Problema de conexión

---

## ⚠️ PROBLEMAS COMUNES

### 1. "Can't connect to MySQL server"
- Verifica firewall de Windows
- Verifica que MySQL esté corriendo
- Verifica las variables de entorno en Railway

### 2. "Access denied for user"
- Verifica usuario y password
- Verifica que el usuario tenga permisos remotos (`'@'%'`)

### 3. "Connection timeout"
- Tu router está bloqueando el puerto
- Configura port forwarding
- Usa ngrok en su lugar

### 4. IP cambió
- Si usas IP dinámica, cambiará frecuentemente
- Usa ngrok o migra a base de datos en la nube

---

## 📝 Checklist de Configuración

- [ ] MySQL instalado y corriendo
- [ ] Base de datos `cmms_db` creada
- [ ] Usuario `cmms_user` creado con permisos
- [ ] `bind-address = 0.0.0.0` en my.ini
- [ ] MySQL reiniciado
- [ ] Firewall de Windows configurado
- [ ] ngrok corriendo (o port forwarding configurado)
- [ ] Variables de entorno en Railway configuradas
- [ ] Conexión probada localmente
- [ ] Código pusheado a GitHub
- [ ] Railway desplegado

---

## 🚀 Próximos Pasos

Una vez que el proyecto esté listo, migra a:
1. **PlanetScale** (gratis, profesional)
2. **Railway MySQL** ($10/mes, simple)

Para migrar los datos:
```bash
# Exportar
mysqldump -u cmms_user -p cmms_db > backup.sql

# Importar a nueva BD
mysql -h nuevo_host -u nuevo_user -p nueva_db < backup.sql
```

---

¿Necesitas ayuda con algún paso específico?
