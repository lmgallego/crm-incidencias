"""Script para crear las tablas en Supabase"""

from supabase_config import get_supabase_client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL para crear las tablas en PostgreSQL (Supabase)
CREATE_TABLES_SQL = [
    # Tabla coordinators
    """
    CREATE TABLE IF NOT EXISTS coordinators (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        surnames TEXT NOT NULL
    );
    """,
    
    # Tabla verifiers
    """
    CREATE TABLE IF NOT EXISTS verifiers (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        surnames TEXT NOT NULL,
        phone TEXT,
        zone TEXT
    );
    """,
    
    # Tabla warehouses
    """
    CREATE TABLE IF NOT EXISTS warehouses (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        nif TEXT NOT NULL,
        zone TEXT
    );
    """,
    
    # Tabla incidents
    """
    CREATE TABLE IF NOT EXISTS incidents (
        id SERIAL PRIMARY KEY,
        code TEXT UNIQUE,
        description TEXT NOT NULL
    );
    """,
    
    # Tabla incident_records
    """
    CREATE TABLE IF NOT EXISTS incident_records (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        registering_coordinator_id INTEGER NOT NULL,
        warehouse_id INTEGER NOT NULL,
        causing_verifier_id INTEGER NOT NULL,
        incident_id INTEGER NOT NULL,
        assigned_coordinator_id INTEGER NOT NULL,
        explanation TEXT,
        status TEXT NOT NULL,
        responsible TEXT NOT NULL,
        FOREIGN KEY (registering_coordinator_id) REFERENCES coordinators(id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
        FOREIGN KEY (causing_verifier_id) REFERENCES verifiers(id),
        FOREIGN KEY (incident_id) REFERENCES incidents(id),
        FOREIGN KEY (assigned_coordinator_id) REFERENCES coordinators(id)
    );
    """,
    
    # Tabla incident_actions
    """
    CREATE TABLE IF NOT EXISTS incident_actions (
        id SERIAL PRIMARY KEY,
        incident_record_id INTEGER NOT NULL,
        action_date DATE NOT NULL,
        action_description TEXT NOT NULL,
        new_status TEXT,
        performed_by INTEGER NOT NULL,
        FOREIGN KEY (incident_record_id) REFERENCES incident_records(id),
        FOREIGN KEY (performed_by) REFERENCES coordinators(id)
    );
    """
]

# Índices para optimizar consultas
CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_warehouses_zone ON warehouses(zone);",
    "CREATE INDEX IF NOT EXISTS idx_verifiers_zone ON verifiers(zone);",
    "CREATE INDEX IF NOT EXISTS idx_incident_records_status ON incident_records(status);",
    "CREATE INDEX IF NOT EXISTS idx_incident_records_warehouse_id ON incident_records(warehouse_id);",
    "CREATE INDEX IF NOT EXISTS idx_incident_records_causing_verifier_id ON incident_records(causing_verifier_id);",
    "CREATE INDEX IF NOT EXISTS idx_incident_records_incident_id ON incident_records(incident_id);"
]

def create_tables():
    """Crea todas las tablas en Supabase usando RPC"""
    try:
        client = get_supabase_client()
        
        logger.info("Creando tablas en Supabase...")
        
        # Crear todas las tablas en una sola llamada RPC
        full_sql = "\n".join(CREATE_TABLES_SQL + CREATE_INDEXES_SQL)
        
        logger.info("Ejecutando SQL completo...")
        try:
            # Intentar usar la función RPC personalizada
            result = client.rpc('execute_sql', {'query': full_sql}).execute()
            logger.info("✅ Tablas creadas usando RPC personalizada")
        except Exception as rpc_error:
            logger.warning(f"RPC personalizada falló: {rpc_error}")
            logger.info("Intentando crear tablas individualmente...")
            
            # Si no hay RPC personalizada, intentar crear las tablas verificando si existen
            tables_info = [
                ('coordinators', ['id', 'name', 'surnames']),
                ('verifiers', ['id', 'name', 'surnames', 'phone', 'zone']),
                ('warehouses', ['id', 'name', 'nif', 'zone']),
                ('incidents', ['id', 'code', 'description']),
                ('incident_records', ['id', 'date', 'registering_coordinator_id', 'warehouse_id', 'causing_verifier_id', 'incident_id', 'assigned_coordinator_id', 'explanation', 'status', 'responsible']),
                ('incident_actions', ['id', 'incident_record_id', 'action_date', 'action_description', 'new_status', 'performed_by'])
            ]
            
            for table_name, columns in tables_info:
                try:
                    # Intentar hacer una consulta simple para ver si la tabla existe
                    result = client.table(table_name).select("count", count="exact").limit(1).execute()
                    logger.info(f"✅ Tabla '{table_name}' ya existe")
                except Exception:
                    logger.warning(f"⚠️ Tabla '{table_name}' no existe o no es accesible")
                    logger.info(f"Por favor, crea la tabla '{table_name}' manualmente en el dashboard de Supabase")
                    logger.info(f"Columnas necesarias: {', '.join(columns)}")
        
        logger.info("✅ Proceso de creación de tablas completado")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando tablas en Supabase: {e}")
        return False

def verify_tables():
    """Verifica que las tablas existan en Supabase"""
    try:
        client = get_supabase_client()
        
        tables = ['coordinators', 'verifiers', 'warehouses', 'incidents', 'incident_records', 'incident_actions']
        
        logger.info("Verificando tablas en Supabase...")
        
        for table in tables:
            try:
                result = client.table(table).select("count", count="exact").execute()
                logger.info(f"✅ Tabla '{table}' existe y es accesible")
            except Exception as e:
                logger.error(f"❌ Error accediendo a tabla '{table}': {e}")
                return False
        
        logger.info("✅ Todas las tablas están disponibles")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando tablas: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando creación de tablas en Supabase...")
    
    # Crear tablas
    if create_tables():
        print("\n🔍 Verificando tablas...")
        if verify_tables():
            print("\n🎉 ¡Migración completada exitosamente!")
        else:
            print("\n⚠️ Las tablas se crearon pero hay problemas de acceso")
    else:
        print("\n❌ Error en la migración")