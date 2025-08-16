# Guía de Deploy - Gestión de Incidencias

## 🚀 Nueva Solución: Supabase (Recomendado)

**IMPORTANTE**: La aplicación ahora soporta Supabase como base de datos en producción, eliminando completamente los problemas de persistencia de datos.

### Ventajas de Supabase:
- ✅ **Persistencia garantizada**: Los datos nunca se pierden
- ✅ **Escalabilidad**: Base de datos PostgreSQL en la nube
- ✅ **Detección automática**: Se activa automáticamente en producción
- ✅ **Fallback a SQLite**: Funciona en desarrollo local
- ✅ **Cero configuración adicional**: Solo variables de entorno

### Configuración Rápida:
1. **Crea las tablas en Supabase**: Ejecuta `supabase_schema.sql` en el SQL Editor
2. **Configura variables de entorno**:
   ```bash
   SUPABASE_URL=tu_url_de_supabase
   SUPABASE_ANON_KEY=tu_clave_anonima
   ```
3. **¡Listo!** La aplicación detectará automáticamente Supabase en producción

📖 **Guía completa**: Ver `SUPABASE_SETUP.md`

---

## 📜 Problema Anterior (Solo SQLite)
La base de datos se borra al hacer logout y volver a hacer login en el entorno de deploy.

### Causa Principal en Streamlit Cloud
**IMPORTANTE**: En Streamlit Cloud, cada deploy toma los archivos directamente desde GitHub. Si el archivo `db/cavacrm.db` no está actualizado en el repositorio, se despliega con una base de datos vacía.

### ¿Por qué sucede esto?
1. Streamlit Cloud clona el repositorio de GitHub en cada deploy
2. Si `db/cavacrm.db` no está en GitHub o está desactualizado, se usa la versión vacía
3. Al hacer logout/login, la aplicación se reinicia y vuelve a usar la base vacía del repositorio

## Soluciones Implementadas

### 1. Botón de Logout Seguro
- Se añadió un botón "🚪 Cerrar Sesión" en la barra lateral
- Limpia solo las variables de sesión relacionadas con login
- No afecta los datos de la base de datos

### 2. Protección de Datos en Deploy
- Nuevo archivo `config.py` que detecta entornos de deploy
- Función `init_db()` mejorada que preserva datos existentes
- Backup automático antes de cualquier inicialización en deploy
- Logging detallado para monitorear el comportamiento

### 3. Configuración de Deploy

#### Para Streamlit Cloud (con Supabase):
```bash
# Variables de entorno obligatorias para Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_clave_anonima_aqui

# Variables de entorno opcionales
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SHARING_MODE=true
```

#### Para Heroku (con Supabase):
```bash
# Procfile
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

# Variables de entorno obligatorias
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_clave_anonima_aqui
PORT=8080
DYNO=web.1
```

#### Para Railway (con Supabase):
```bash
# Variables de entorno obligatorias
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_clave_anonima_aqui
RAILWAY_ENVIRONMENT=production
PORT=8080
```

#### Configuración Solo SQLite (No Recomendado):
```bash
# Para forzar SQLite en producción (no recomendado)
FORCE_SUPABASE=false
```

## Archivos Importantes para el Deploy

### 1. Estructura de Archivos (Actualizada)
```
├── app.py                    # Aplicación principal
├── config.py                # Configuración de entorno y detección automática
├── requirements.txt         # Dependencias (incluye supabase)
├── supabase_config.py       # Configuración de Supabase
├── supabase_schema.sql      # Script SQL para crear tablas en Supabase
├── SUPABASE_SETUP.md        # Guía de configuración de Supabase
├── migrate_to_supabase.py   # Script de migración de datos
├── db/
│   ├── cavacrm.db          # Base de datos SQLite (fallback)
│   └── schema.sql          # Esquema SQLite original
├── utils/
│   ├── database.py         # Funciones SQLite originales
│   ├── database_supabase.py # Funciones para Supabase
│   ├── database_unified.py  # Módulo unificado (selecciona BD automáticamente)
│   └── backup_restore.py   # Funciones de backup
└── components/             # Componentes de la UI
```

### 2. requirements.txt (Actualizado)
```
streamlit
streamlit-option-menu
pandas
supabase
openpyxl
```

**Nota**: `sqlite3` se removió porque viene incluido con Python por defecto.

## Recomendaciones para Deploy

### 1. Persistencia de Datos en Streamlit Cloud
- **CRÍTICO**: El archivo `db/cavacrm.db` debe estar actualizado en GitHub
- **PROBLEMA**: Streamlit Cloud NO mantiene archivos persistentes entre reinicios
- **SOLUCIÓN RECOMENDADA**: Usar base de datos externa (ver sección siguiente)

### 2. Soluciones para Streamlit Cloud

#### Opción A: Base de Datos Externa (RECOMENDADO)
```python
# Usar PostgreSQL, MySQL o SQLite en un servicio persistente
# Ejemplo con Supabase (PostgreSQL gratuito):
import psycopg2

# En utils/database.py, reemplazar:
# DB_PATH = 'db/cavacrm.db'
# conn = sqlite3.connect(DB_PATH)

# Por:
# DATABASE_URL = os.getenv('DATABASE_URL')  # Variable de entorno en Streamlit Cloud
# conn = psycopg2.connect(DATABASE_URL)
```

#### Opción B: Commit Manual de la Base de Datos
```bash
# Después de añadir datos importantes:
git add db/cavacrm.db
git commit -m "Update database with new data"
git push origin main
```
**ADVERTENCIA**: Esta opción no es recomendada para producción ya que la base de datos puede crecer mucho.

#### Opción C: Inicialización con Datos por Defecto (IMPLEMENTADO)
- **NUEVO**: Script `init_default_data.py` que añade datos iniciales automáticamente
- Se ejecuta automáticamente en entornos de deploy cuando no hay datos
- Incluye:
  - 3 coordinadores por defecto (Admin Sistema, Coordinador Principal, Supervisor General)
  - 8 tipos de incidencia comunes (INC001-INC008)
  - 1 verificador por zona (PENEDES, ALT CAMP, CONCA, ALMENDRALEJO, REQUENA, CARIÑENA)
  - 1 bodega por zona con NIF generado automáticamente
- **Ventaja**: Siempre tendrás datos básicos para empezar a trabajar
- **Limitación**: Los datos de producción (incidencias reales) se perderán en cada deploy

### 3. Instrucciones Específicas para Streamlit Cloud

#### Paso 1: Preparar el Repositorio
```bash
# 1. Asegurar que todos los archivos estén en GitHub
git add .
git commit -m "Add all application files"
git push origin main

# 2. Verificar que estos archivos estén incluidos:
# - app.py
# - config.py
# - init_default_data.py
# - requirements.txt
# - db/schema.sql
# - Todos los archivos en components/ y utils/
```

#### Paso 2: Configurar Streamlit Cloud
1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Conectar tu repositorio de GitHub
3. Configurar:
   - **Main file path**: `app.py`
   - **Python version**: 3.9+ (recomendado)

#### Paso 3: Variables de Entorno (Opcional)
```bash
# En Streamlit Cloud > Settings > Secrets
# Añadir si necesitas configuración específica:
LOG_LEVEL = "INFO"
ENVIRONMENT = "production"
```

#### Paso 4: Primer Deploy
- La aplicación se desplegará automáticamente
- Se crearán datos por defecto automáticamente
- Podrás empezar a usar la aplicación inmediatamente

#### Paso 5: Uso en Producción
- **Para datos temporales**: Usar la aplicación normalmente
- **Para datos importantes**: Considerar migrar a base de datos externa
- **Backup regular**: Usar "Administración > Copia de Seguridad" y descargar

### 4. Variables de Entorno
```bash
# Opcional: Configurar ruta de base de datos
DB_PATH=/app/db/cavacrm.db

# Para debugging
LOG_LEVEL=INFO
```

### 3. Monitoreo
- Los logs ahora muestran:
  - Si se detecta entorno de deploy
  - Cuántos registros existen antes y después de init
  - Si se crean backups automáticos
  - Estado de integridad de la base de datos

### 4. Backup Automático
- En entornos de deploy, se crea automáticamente un backup antes de cualquier inicialización
- Los backups se guardan con timestamp en el nombre
- Usa la función "Restaurar Copia" si necesitas recuperar datos

## Solución de Problemas

### Si los datos siguen desapareciendo:

1. **Verificar logs**:
   ```bash
   # Buscar en los logs del deploy:
   - "Environment - Deployed: True"
   - "Existing coordinators in database: X"
   - "Tables already exist, skipping schema execution"
   ```

2. **Verificar persistencia de archivos**:
   - Confirmar que `db/cavacrm.db` se mantiene entre reinicios
   - Verificar permisos de escritura en el directorio `db/`

3. **Usar base de datos externa**:
   - Para producción, considera PostgreSQL o MySQL
   - Modifica `utils/database.py` para usar la nueva conexión

### Comandos de Diagnóstico
```python
# En la consola de Python del deploy:
import os
from utils.database import get_db_connection

# Verificar si existe la base de datos
print(f"DB exists: {os.path.exists('db/cavacrm.db')}")

# Contar registros
conn = get_db_connection()
cursor = conn.cursor()
print(f"Coordinators: {cursor.execute('SELECT COUNT(*) FROM coordinators').fetchone()[0]}")
print(f"Incidents: {cursor.execute('SELECT COUNT(*) FROM incident_records').fetchone()[0]}")
conn.close()
```

## Contacto
Si el problema persiste, revisar los logs detallados que ahora se generan automáticamente.