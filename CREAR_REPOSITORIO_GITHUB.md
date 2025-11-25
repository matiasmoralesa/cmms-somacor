# Crear Repositorio en GitHub

## Opción 1: Desde la Web (Recomendado)

1. Ve a https://github.com/new
2. Configura el repositorio:
   - **Repository name**: `cmms-sistema-mantenimiento` (o el nombre que prefieras)
   - **Description**: `Sistema de Gestión de Mantenimiento Computarizado (CMMS) con Django REST Framework y GCP`
   - **Visibility**: Elige Private o Public según tus necesidades
   - **NO** marques "Initialize this repository with a README" (ya tenemos uno)
   - **NO** agregues .gitignore ni licencia (ya los tenemos)

3. Haz clic en "Create repository"

4. GitHub te mostrará comandos para subir tu código. Copia y ejecuta estos comandos en tu terminal:

```powershell
# Agregar el repositorio remoto (reemplaza TU_USUARIO con tu nombre de usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/cmms-sistema-mantenimiento.git

# Renombrar la rama principal a 'main' (opcional, si prefieres usar 'main' en lugar de 'master')
git branch -M main

# Subir el código
git push -u origin main
```

## Opción 2: Usando GitHub CLI

Si prefieres usar la línea de comandos, primero instala GitHub CLI:

### Instalar GitHub CLI en Windows

1. Descarga el instalador desde: https://cli.github.com/
2. O usa winget:
```powershell
winget install --id GitHub.cli
```

3. Reinicia tu terminal

4. Autentícate:
```powershell
gh auth login
```

5. Crea el repositorio:
```powershell
gh repo create cmms-sistema-mantenimiento --private --source=. --remote=origin --push
```

## Verificar que se subió correctamente

Después de hacer push, verifica en tu navegador:
```
https://github.com/TU_USUARIO/cmms-sistema-mantenimiento
```

## Comandos Git Útiles

### Ver el estado del repositorio
```powershell
git status
```

### Ver el historial de commits
```powershell
git log --oneline
```

### Ver los remotos configurados
```powershell
git remote -v
```

### Hacer cambios futuros
```powershell
# 1. Hacer cambios en tus archivos
# 2. Agregar los cambios
git add .

# 3. Hacer commit
git commit -m "Descripción de los cambios"

# 4. Subir a GitHub
git push
```

## Estructura del Repositorio

Tu repositorio incluye:

```
cmms-sistema-mantenimiento/
├── backend/              # API Django REST Framework
├── frontend/            # Aplicación React (pendiente)
├── deployment/          # Scripts de despliegue GCP
├── airflow/            # DAGs de Apache Airflow
├── docs/               # Documentación
├── .gitignore          # Archivos ignorados por Git
├── README.md           # Documentación principal
├── INICIO_RAPIDO_DESPLIEGUE.md
├── COMPLETAR_DESPLIEGUE.md
└── MODELO_IA_EXPLICACION.md
```

## Próximos Pasos

1. ✅ Crear repositorio en GitHub
2. ✅ Subir código inicial
3. 🔄 Configurar GitHub Actions para CI/CD (opcional)
4. 🔄 Agregar colaboradores (si es necesario)
5. 🔄 Configurar branch protection rules (recomendado para producción)

## Notas de Seguridad

⚠️ **IMPORTANTE**: El `.gitignore` está configurado para NO subir:
- Credenciales de GCP
- Variables de entorno (.env)
- Archivos de base de datos local
- Directorios de entornos virtuales
- Cloud SQL Proxy

Verifica que no se hayan subido archivos sensibles:
```powershell
git log --all --full-history -- "*credentials*"
git log --all --full-history -- "*.env"
```

Si accidentalmente subiste credenciales:
1. Revoca las credenciales inmediatamente en GCP Console
2. Usa `git filter-branch` o BFG Repo-Cleaner para eliminar el historial
3. Genera nuevas credenciales
