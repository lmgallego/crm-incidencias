"""Módulo unificado de base de datos que usa SQLite o Supabase según la configuración"""

import logging
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar el módulo de base de datos apropiado
if DB_CONFIG.get('use_supabase', False):
    logger.info("🔄 Usando Supabase como base de datos")
    try:
        from .database_supabase import *
        DATABASE_TYPE = "supabase"
    except ImportError as e:
        logger.error(f"❌ Error importando Supabase: {e}")
        logger.info("🔄 Fallback a SQLite")
        from .database import *
        DATABASE_TYPE = "sqlite"
else:
    logger.info("🔄 Usando SQLite como base de datos")
    from .database import *
    DATABASE_TYPE = "sqlite"

logger.info(f"✅ Base de datos configurada: {DATABASE_TYPE}")

# Función para obtener el tipo de base de datos actual
def get_database_type():
    """Retorna el tipo de base de datos en uso"""
    return DATABASE_TYPE

# Función para verificar el estado de la conexión
def check_database_connection():
    """Verifica si la conexión a la base de datos está funcionando"""
    try:
        if DATABASE_TYPE == "supabase":
            from supabase_config import test_connection
            return test_connection()
        else:
            # Para SQLite, intentar una consulta simple
            from .database import get_db_connection
            conn = get_db_connection()
            conn.execute('SELECT 1')
            conn.close()
            return True
    except Exception as e:
        logger.error(f"❌ Error de conexión a la base de datos: {e}")
        return False

# Función adicional para filtros del dashboard
def get_pending_incidents_by_coordinator(coordinator_id=None):
    """Obtiene incidencias pendientes filtradas por coordinador asignado"""
    if DATABASE_TYPE == "supabase":
        from .database_supabase import get_pending_incidents_by_coordinator as get_pending_supabase
        return get_pending_supabase(coordinator_id)
    else:
        from .database import get_pending_incidents_by_coordinator as get_pending_sqlite
        return get_pending_sqlite(coordinator_id)

def get_filtered_pending_incidents(coordinator_id=None, status=None, days=None):
    """Obtiene incidencias pendientes con filtros múltiples"""
    if DATABASE_TYPE == "supabase":
        from .database_supabase import get_filtered_pending_incidents as get_filtered_supabase
        return get_filtered_supabase(coordinator_id, status, days)
    else:
        from .database import get_filtered_pending_incidents as get_filtered_sqlite
        return get_filtered_sqlite(coordinator_id, status, days)