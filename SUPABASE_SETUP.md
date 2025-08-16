# 🚀 Configuración de Supabase para Gestión de Incidencias

## ✅ Estado Actual de la Migración

La migración a Supabase está **casi completada**. Solo falta un paso manual:

### 📋 Pasos Completados
- ✅ Instalación de dependencias (`supabase-py`)
- ✅ Configuración de credenciales de Supabase
- ✅ Creación del módulo de base de datos para Supabase
- ✅ Actualización del sistema de configuración automática
- ✅ Migración de datos existentes (no había datos para migrar)
- ✅ Actualización de todos los imports en la aplicación

### 🔧 Paso Pendiente: Crear Tablas en Supabase

**IMPORTANTE**: Debes ejecutar el script SQL manualmente en el dashboard de Supabase.

#### Instrucciones:

1. **Accede al Dashboard de Supabase**:
   - Ve a [https://supabase.com/dashboard](https://supabase.com/dashboard)
   - Inicia sesión en tu cuenta
   - Selecciona tu proyecto

2. **Abre el SQL Editor**:
   - En el menú lateral, haz clic en "SQL Editor"
   - Haz clic en "New Query"

3. **Ejecuta el Script SQL**:
   - Copia todo el contenido del archivo `supabase_schema.sql`
   - Pégalo en el editor SQL
   - Haz clic en "Run" para ejecutar el script

4. **Verifica la Creación**:
   - Ve a "Table Editor" en el menú lateral
   - Deberías ver las siguientes tablas:
     - `coordinators`
     - `verifiers`
     - `warehouses`
     - `incidents`
     - `incident_records`
     - `incident_actions`

## 🔄 Cómo Funciona la Migración

### Detección Automática
La aplicación detecta automáticamente qué base de datos usar:

- **En desarrollo local**: Usa SQLite por defecto
- **En producción**: Usa Supabase si está configurado
- **Forzar Supabase**: Establece `FORCE_SUPABASE=true` como variable de entorno

### Variables de Entorno para Producción

Para el despliegue en producción, configura estas variables de entorno:

```bash
SUPABASE_URL=https://kwzjwphngmjzuabeyivk.supabase.co
SUPABASE_ANON_KEY=tu_clave_anonima_aqui
```

## 🧪 Pruebas

### Probar Localmente con Supabase

```bash
# Forzar uso de Supabase en desarrollo
$env:FORCE_SUPABASE='true'
python -m streamlit run app.py
```

### Verificar Conexión

```bash
# Verificar configuración
$env:FORCE_SUPABASE='true'
python -c "from utils.database_unified import get_database_type, check_database_connection; print('BD:', get_database_type()); print('Conexión:', check_database_connection())"
```

## 📁 Archivos Creados/Modificados

### Nuevos Archivos
- `supabase_config.py` - Configuración de Supabase
- `database_supabase.py` - Funciones de BD para Supabase
- `database_unified.py` - Módulo unificado que selecciona la BD
- `supabase_schema.sql` - Script SQL para crear tablas
- `migrate_to_supabase.py` - Script de migración de datos
- `create_supabase_tables.py` - Verificador de tablas

### Archivos Modificados
- `config.py` - Detección automática de entorno
- `requirements.txt` - Dependencia de Supabase
- `app.py` - Import actualizado
- `components/*.py` - Imports actualizados
- `init_default_data.py` - Import actualizado

## 🚀 Despliegue

### Streamlit Cloud
1. Configura las variables de entorno en Streamlit Cloud:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

2. La aplicación detectará automáticamente el entorno de producción y usará Supabase

### Otros Servicios (Heroku, Railway, etc.)
1. Configura las mismas variables de entorno
2. La detección automática funcionará en cualquier plataforma

## 🔍 Solución de Problemas

### Error: "Could not find the table"
- **Causa**: Las tablas no existen en Supabase
- **Solución**: Ejecuta el script `supabase_schema.sql` en el dashboard

### Error de Conexión
- **Causa**: Credenciales incorrectas
- **Solución**: Verifica `SUPABASE_URL` y `SUPABASE_ANON_KEY`

### Aplicación Usa SQLite en Producción
- **Causa**: Variables de entorno no configuradas
- **Solución**: Configura las variables de entorno de Supabase

## 📞 Soporte

Si encuentras problemas:
1. Verifica que las tablas existan en Supabase
2. Confirma las variables de entorno
3. Revisa los logs de la aplicación
4. Usa `python create_supabase_tables.py` para diagnosticar

---

**¡La migración está lista! Solo ejecuta el script SQL en Supabase y estarás listo para producción! 🎉**