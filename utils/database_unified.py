"""Módulo unificado de base de datos que usa SQLite o Supabase según la configuración"""

import logging
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar el módulo de base de datos apropiado
# CONFIGURADO PARA USAR ÚNICAMENTE SUPABASE
logger.info("🔄 Usando Supabase como base de datos (configuración forzada)")
try:
    from .database_supabase import *
    DATABASE_TYPE = "supabase"
except ImportError as e:
    logger.error(f"❌ Error crítico: No se puede importar Supabase: {e}")
    logger.error("❌ La aplicación está configurada para usar únicamente Supabase")
    logger.error("❌ Verifique la configuración de Supabase y las dependencias")
    raise ImportError("Supabase no está disponible y es requerido para esta configuración")

logger.info(f"✅ Base de datos configurada: {DATABASE_TYPE}")

# Función para obtener el tipo de base de datos actual
def get_database_type():
    """Retorna el tipo de base de datos en uso"""
    return DATABASE_TYPE

# Función para verificar el estado de la conexión
def check_database_connection():
    """Verifica si la conexión a la base de datos está funcionando"""
    try:
        from supabase_config import test_connection
        return test_connection()
    except Exception as e:
        logger.error(f"❌ Error de conexión a Supabase: {e}")
        return False

# Función adicional para filtros del dashboard
def get_pending_incidents_by_coordinator(coordinator_id=None):
    """Obtiene incidencias pendientes filtradas por coordinador asignado"""
    from .database_supabase import get_pending_incidents_by_coordinator as get_pending_supabase
    return get_pending_supabase(coordinator_id)

def get_filtered_pending_incidents(coordinator_id=None, status=None, days=None):
    """Obtiene incidencias pendientes con filtros múltiples"""
    from .database_supabase import get_filtered_pending_incidents as get_filtered_supabase
    return get_filtered_supabase(coordinator_id, status, days)