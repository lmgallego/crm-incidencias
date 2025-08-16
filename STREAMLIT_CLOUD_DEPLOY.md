# 🚀 Guía de Deploy en Streamlit Cloud

## ✅ Solución Implementada

Hemos solucionado el problema de la **base de datos vacía** en Streamlit Cloud implementando:

### 🔧 Funcionalidades Añadidas

1. **Inicialización Automática de Datos** (`init_default_data.py`)
   - Se ejecuta automáticamente en entornos de deploy
   - Crea datos básicos si la base de datos está vacía
   - Incluye coordinadores, verificadores, bodegas y tipos de incidencia

2. **Detección de Entorno de Deploy** (`config.py`)
   - Detecta automáticamente Streamlit Cloud
   - Configura comportamiento específico para deploy

3. **Botón de Logout Seguro**
   - No borra la base de datos al cerrar sesión
   - Solo limpia variables de sesión

## 📋 Pasos para Deploy

### Paso 1: Preparar Repositorio
```bash
# Asegurar que todos los archivos estén en GitHub
git add .
git commit -m "Ready for Streamlit Cloud deploy"
git push origin main
```

### Paso 2: Deploy en Streamlit Cloud
1. Ir a **[share.streamlit.io](https://share.streamlit.io)**
2. **Conectar GitHub** y seleccionar tu repositorio
3. **Configurar**:
   - Main file path: `app.py`
   - Python version: 3.9+
4. **Deploy** - ¡La aplicación se desplegará automáticamente!

### Paso 3: Primer Uso
1. **Acceder** a la URL proporcionada por Streamlit Cloud
2. **Login** con credenciales por defecto:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. **¡Listo!** - Los datos por defecto se habrán creado automáticamente

## 📊 Datos por Defecto Incluidos

### 👥 Coordinadores (3)
- Admin Sistema
- Coordinador Principal  
- Supervisor General

### 🔍 Verificadores (6)
- Uno por cada zona: PENEDES, ALT CAMP, CONCA, ALMENDRALEJO, REQUENA, CARIÑENA
- Teléfonos: 600000001-600000006

### 🏭 Bodegas (6)
- Una por cada zona con NIF generado automáticamente
- Nombres: "Bodega [ZONA]"

### 📋 Tipos de Incidencia (8)
- INC001: Problema de calidad del producto
- INC002: Retraso en la entrega
- INC003: Documentación incorrecta
- INC004: Problema de temperatura
- INC005: Daño en el transporte
- INC006: Cantidad incorrecta
- INC007: Problema de etiquetado
- INC008: Incumplimiento de especificaciones

## ⚠️ Limitaciones Importantes

### 🔄 Persistencia de Datos
- **Los datos se mantienen** durante la sesión de la aplicación
- **Los datos se pierden** cuando Streamlit Cloud reinicia la aplicación
- **Solución**: Los datos por defecto se recrean automáticamente

### 💾 Para Datos de Producción
Si necesitas **persistencia real** de datos:

1. **Opción A: Base de Datos Externa** (Recomendado)
   - PostgreSQL (Supabase, Railway, etc.)
   - MySQL (PlanetScale, etc.)
   - SQLite en volumen persistente

2. **Opción B: Backup Regular**
   - Usar "Administración > Copia de Seguridad"
   - Descargar y guardar regularmente
   - Restaurar cuando sea necesario

## 🛠️ Solución de Problemas

### ❌ La aplicación no inicia
```bash
# Verificar que requirements.txt esté actualizado
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### ❌ No aparecen datos por defecto
1. Verificar logs en Streamlit Cloud
2. Buscar mensajes de "Deploy environment detected"
3. Si no aparece, contactar soporte

### ❌ Error de permisos
- Verificar que el repositorio sea público o que Streamlit Cloud tenga acceso
- Revisar configuración de GitHub en Streamlit Cloud

## 📞 Soporte

Si encuentras problemas:
1. **Revisar logs** en Streamlit Cloud
2. **Verificar archivos** en el repositorio
3. **Probar localmente** primero

## 🎉 ¡Éxito!

Una vez desplegado, tendrás:
- ✅ Aplicación funcionando en Streamlit Cloud
- ✅ Datos por defecto cargados automáticamente
- ✅ Sistema de login/logout seguro
- ✅ Todas las funcionalidades operativas

**URL de ejemplo**: `https://tu-usuario-gestion-incidencias-app-xyz123.streamlit.app`