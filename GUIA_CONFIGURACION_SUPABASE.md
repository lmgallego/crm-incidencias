# 📋 Guía Paso a Paso: Configuración Final de Supabase

## 🎯 Objetivo
Completar la configuración de Supabase para que tu aplicación funcione correctamente en producción.

## ✅ Estado Actual
- ✅ Código migrado completamente
- ✅ Archivos de configuración creados
- ⏳ **PENDIENTE**: Crear tablas en Supabase (paso manual)

---

## 🚀 Paso 1: Acceder a Supabase Dashboard

1. **Abre tu navegador** y ve a: https://supabase.com/dashboard
2. **Inicia sesión** con tu cuenta de Supabase
3. **Selecciona tu proyecto** de la lista

---

## 🛠️ Paso 2: Crear las Tablas

### 2.1 Abrir el SQL Editor
1. En el menú lateral izquierdo, haz clic en **"SQL Editor"**
2. Haz clic en **"New Query"** (botón verde)

### 2.2 Ejecutar el Script SQL
1. **Copia TODO el contenido** del archivo `supabase_schema.sql`
2. **Pégalo** en el editor SQL de Supabase
3. Haz clic en **"Run"** (botón verde con ícono de play)
4. **Espera** a que aparezca el mensaje de confirmación

### 2.3 Verificar la Creación
1. Ve a **"Table Editor"** en el menú lateral
2. Deberías ver estas 6 tablas:
   - ✅ `coordinators`
   - ✅ `verifiers` 
   - ✅ `warehouses`
   - ✅ `incidents`
   - ✅ `incident_records`
   - ✅ `incident_actions`

---

## 🔧 Paso 3: Configurar Variables de Entorno

### 3.1 Obtener las Credenciales
1. En Supabase Dashboard, ve a **"Settings" → "API"**
2. Copia estos valores:
   - **Project URL** (ejemplo: `https://abc123.supabase.co`)
   - **anon public key** (clave larga que empieza con `eyJ...`)

### 3.2 Configurar para Desarrollo Local (Opcional)
Si quieres probar Supabase en local:

**Windows (PowerShell):**
```powershell
$env:SUPABASE_URL="tu_project_url_aqui"
$env:SUPABASE_ANON_KEY="tu_anon_key_aqui"
```

**Windows (CMD):**
```cmd
set SUPABASE_URL=tu_project_url_aqui
set SUPABASE_ANON_KEY=tu_anon_key_aqui
```

### 3.3 Configurar para Producción
En tu plataforma de despliegue (Streamlit Cloud, Heroku, etc.):
- `SUPABASE_URL` = tu Project URL
- `SUPABASE_ANON_KEY` = tu anon public key

---

## 🧪 Paso 4: Probar la Configuración

### 4.1 Probar Localmente con Supabase
```bash
# Configurar variables de entorno (ver paso 3.2)
# Luego ejecutar:
streamlit run app.py
```

### 4.2 Verificar la Conexión
1. **Abre la aplicación** en tu navegador
2. Ve a la sección **"Gestión de Datos"**
3. Intenta **crear un coordinador** de prueba
4. Si funciona, ¡la configuración es correcta! ✅

---

## 🔍 Solución de Problemas

### Error: "Table 'coordinators' not found"
- ❌ **Causa**: No ejecutaste el script SQL
- ✅ **Solución**: Repite el Paso 2

### Error: "Invalid API key"
- ❌ **Causa**: Variables de entorno incorrectas
- ✅ **Solución**: Verifica el Paso 3

### Error: "Connection failed"
- ❌ **Causa**: URL de Supabase incorrecta
- ✅ **Solución**: Verifica la URL en el Paso 3.1

---

## 📁 Archivos Importantes

- `supabase_schema.sql` - Script para crear tablas
- `supabase_config.py` - Configuración de Supabase
- `SUPABASE_SETUP.md` - Documentación técnica completa
- `DEPLOY_GUIDE.md` - Guía de despliegue actualizada

---

## 🎉 ¡Listo!

Una vez completados estos pasos:
- ✅ Tu aplicación usará Supabase en producción
- ✅ Los datos persistirán correctamente
- ✅ Podrás escalar sin problemas
- ✅ SQLite seguirá funcionando en desarrollo local

**¿Necesitas ayuda?** Revisa `SUPABASE_SETUP.md` para más detalles técnicos.