# 🛡️ Guía de Migración Segura SQLite → Supabase

## ⚠️ **IMPORTANTE: Prevención de Duplicados**

Este documento describe el flujo seguro para migrar datos de SQLite local a Supabase sin riesgo de duplicar o perder información.

---

## 🚨 Problema Identificado

El script actual `migrate_to_supabase.py` tiene una **limitación crítica**:

- ❌ **No verifica duplicados**: Cada ejecución añade todos los datos nuevamente
- ❌ **INSERT directo**: No usa UPSERT para evitar conflictos
- ⚠️ **Riesgo**: Múltiples ejecuciones = datos multiplicados

### Ejemplo del Problema
```
Primera migración:  6 coordinadores, 2 incidencias
Segunda migración: 12 coordinadores, 4 incidencias  
Tercera migración: 18 coordinadores, 6 incidencias
```

---

## ✅ Flujo Seguro de Migración

### Paso 1: Verificar Estado Actual

```bash
# Verificar qué base de datos está usando localmente
python check_db_config.py

# Verificar estado de Supabase (forzar conexión)
$env:FORCE_SUPABASE='true'
python check_db_config.py
```

**Resultado esperado**:
- Local: `Using Supabase: False` (SQLite activo)
- Supabase: `Using Supabase: True` + conteo de registros

### Paso 2: Preparar Supabase

#### 2.1 Crear Tablas (Si es primera vez)
```bash
# Verificar si las tablas existen
python create_supabase_tables.py
```

#### 2.2 Limpiar Datos Existentes (Si hay duplicados)
```bash
# CUIDADO: Esto borra TODOS los datos de Supabase
python -c "from utils.database_supabase import reset_database; reset_database()"
```

### Paso 3: Ejecutar Migración

```bash
# Migrar datos de SQLite a Supabase
python migrate_to_supabase.py
```

**El script automáticamente**:
- ✅ Crea backup de SQLite antes de migrar
- ✅ Verifica conexión a Supabase
- ✅ Migra en orden correcto (respeta claves foráneas)
- ✅ Procesa en lotes para eficiencia

### Paso 4: Verificar Resultado

```bash
# Confirmar que los datos se migraron correctamente
$env:FORCE_SUPABASE='true'
python check_db_config.py
```

**Verificar**:
- Conteo de registros coincide con SQLite original
- No hay duplicados
- Todas las tablas tienen datos

---

## 🔄 Comandos Completos (Copy-Paste)

### Migración Inicial (Primera vez)
```bash
# 1. Verificar estado local
python check_db_config.py

# 2. Crear tablas en Supabase
python create_supabase_tables.py

# 3. Migrar datos
python migrate_to_supabase.py

# 4. Verificar resultado
$env:FORCE_SUPABASE='true'
python check_db_config.py
```

### Migración con Datos Existentes (Limpieza previa)
```bash
# 1. Verificar estado actual
python check_db_config.py
$env:FORCE_SUPABASE='true'
python check_db_config.py

# 2. Limpiar Supabase (si hay datos duplicados)
python -c "from utils.database_supabase import reset_database; reset_database()"

# 3. Migrar datos limpios
python migrate_to_supabase.py

# 4. Verificar resultado final
$env:FORCE_SUPABASE='true'
python check_db_config.py
```

---

## 🛡️ Protecciones Incluidas

### Backups Automáticos
- **Ubicación**: `db/backups/backup_pre_supabase_YYYYMMDD_HHMMSS.db`
- **Cuándo**: Después de cada migración exitosa
- **Contenido**: Copia completa de SQLite antes de migrar

### Verificaciones de Seguridad
- ✅ Conexión a Supabase antes de iniciar
- ✅ Existencia de tablas en destino
- ✅ Conteo de registros origen vs destino
- ✅ Procesamiento por lotes con manejo de errores

---

## 🚀 Después de la Migración

### Cambiar a Supabase Permanentemente
```bash
# Forzar uso de Supabase en desarrollo local
$env:FORCE_SUPABASE='true'
python -m streamlit run app.py
```

### Despliegue en Producción
1. **Subir código a GitHub**
2. **Configurar variables en Streamlit Cloud**:
   - `SUPABASE_URL=https://tu-proyecto.supabase.co`
   - `SUPABASE_ANON_KEY=tu_clave_aqui`
3. **Desplegar**: La app detectará automáticamente Supabase

---

## 🔍 Solución de Problemas

### Error: "Could not find the table"
```bash
# Crear tablas manualmente
python create_supabase_tables.py
```

### Error: "Duplicate key value"
```bash
# Limpiar Supabase y volver a migrar
python -c "from utils.database_supabase import reset_database; reset_database()"
python migrate_to_supabase.py
```

### Verificar Conexión
```bash
# Test de conectividad
python test_supabase_connection.py
```

---

## 📞 Checklist de Migración

- [ ] ✅ Verificar datos en SQLite local
- [ ] ✅ Confirmar configuración de Supabase
- [ ] ✅ Crear/verificar tablas en Supabase
- [ ] ✅ Limpiar datos duplicados (si existen)
- [ ] ✅ Ejecutar migración
- [ ] ✅ Verificar conteo de registros
- [ ] ✅ Probar aplicación con Supabase
- [ ] ✅ Configurar variables para producción

---

## ⚡ Comandos Rápidos

```bash
# Estado actual
python check_db_config.py

# Migración completa (primera vez)
python create_supabase_tables.py && python migrate_to_supabase.py

# Migración con limpieza
python -c "from utils.database_supabase import reset_database; reset_database()" && python migrate_to_supabase.py

# Verificar resultado
$env:FORCE_SUPABASE='true' && python check_db_config.py

# Usar Supabase localmente
$env:FORCE_SUPABASE='true' && python -m streamlit run app.py
```

---

**🎯 Objetivo**: Migrar datos una sola vez, sin duplicados, con backups automáticos y verificación completa.

**⚠️ Recuerda**: Siempre verificar el estado antes y después de cada migración.