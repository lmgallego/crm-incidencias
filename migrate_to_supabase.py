#!/usr/bin/env python3
"""
Script para migrar datos de SQLite a Supabase
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_sqlite_db():
    """Verifica si existe la base de datos SQLite y tiene datos"""
    db_path = 'db/cavacrm.db'
    
    if not os.path.exists(db_path):
        logger.info("❌ No se encontró la base de datos SQLite")
        return False, None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si existen las tablas principales
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['coordinators', 'verifiers', 'warehouses', 'incidents', 'incident_records', 'incident_actions']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            logger.warning(f"⚠️ Faltan tablas en SQLite: {missing_tables}")
        
        # Contar registros en cada tabla
        table_counts = {}
        for table in expected_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts[table] = count
                logger.info(f"📊 {table}: {count} registros")
        
        conn.close()
        
        total_records = sum(table_counts.values())
        logger.info(f"📊 Total de registros: {total_records}")
        
        return total_records > 0, table_counts
        
    except Exception as e:
        logger.error(f"❌ Error verificando SQLite: {e}")
        return False, None

def migrate_table_data(sqlite_conn, supabase_client, table_name, batch_size=100):
    """Migra datos de una tabla específica de SQLite a Supabase"""
    try:
        cursor = sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        
        # Obtener nombres de columnas
        columns = [description[0] for description in cursor.description]
        
        # Obtener todos los datos
        rows = cursor.fetchall()
        
        if not rows:
            logger.info(f"📋 {table_name}: No hay datos para migrar")
            return True
        
        logger.info(f"🔄 Migrando {len(rows)} registros de {table_name}...")
        
        # Convertir a lista de diccionarios
        data_to_insert = []
        for row in rows:
            record = {}
            for i, value in enumerate(row):
                # Convertir None a null para Supabase
                record[columns[i]] = value
            data_to_insert.append(record)
        
        # Insertar en lotes
        for i in range(0, len(data_to_insert), batch_size):
            batch = data_to_insert[i:i + batch_size]
            
            try:
                result = supabase_client.table(table_name).insert(batch).execute()
                logger.info(f"✅ {table_name}: Lote {i//batch_size + 1} insertado ({len(batch)} registros)")
            except Exception as e:
                logger.error(f"❌ Error insertando lote en {table_name}: {e}")
                # Intentar insertar registro por registro en caso de error
                for record in batch:
                    try:
                        supabase_client.table(table_name).insert(record).execute()
                    except Exception as record_error:
                        logger.error(f"❌ Error insertando registro individual en {table_name}: {record_error}")
                        logger.error(f"Registro problemático: {record}")
        
        logger.info(f"✅ {table_name}: Migración completada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrando {table_name}: {e}")
        return False

def main():
    """Función principal de migración"""
    logger.info("🚀 Iniciando migración de SQLite a Supabase")
    
    # Verificar SQLite
    has_data, table_counts = check_sqlite_db()
    
    if not has_data:
        logger.info("✅ No hay datos en SQLite para migrar")
        return
    
    # Importar y configurar Supabase
    try:
        from supabase_config import get_supabase_client, test_connection
        
        if not test_connection():
            logger.error("❌ No se puede conectar a Supabase")
            return
        
        supabase = get_supabase_client()
        logger.info("✅ Conexión a Supabase establecida")
        
    except ImportError:
        logger.error("❌ No se puede importar la configuración de Supabase")
        return
    except Exception as e:
        logger.error(f"❌ Error configurando Supabase: {e}")
        return
    
    # Conectar a SQLite
    try:
        sqlite_conn = sqlite3.connect('db/cavacrm.db')
        logger.info("✅ Conexión a SQLite establecida")
    except Exception as e:
        logger.error(f"❌ Error conectando a SQLite: {e}")
        return
    
    # Orden de migración (respetando dependencias de claves foráneas)
    migration_order = [
        'coordinators',
        'verifiers', 
        'warehouses',
        'incidents',
        'incident_records',
        'incident_actions'
    ]
    
    # Migrar cada tabla
    successful_migrations = 0
    total_tables = len([table for table in migration_order if table in table_counts])
    
    for table_name in migration_order:
        if table_name in table_counts and table_counts[table_name] > 0:
            logger.info(f"\n📋 Migrando tabla: {table_name}")
            
            if migrate_table_data(sqlite_conn, supabase, table_name):
                successful_migrations += 1
            else:
                logger.error(f"❌ Falló la migración de {table_name}")
    
    # Cerrar conexión SQLite
    sqlite_conn.close()
    
    # Resumen final
    logger.info(f"\n📊 Resumen de migración:")
    logger.info(f"✅ Tablas migradas exitosamente: {successful_migrations}/{total_tables}")
    
    if successful_migrations == total_tables:
        logger.info("🎉 ¡Migración completada exitosamente!")
        
        # Crear backup de SQLite después de migración exitosa
        backup_name = f"backup_pre_supabase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = f"db/backups/{backup_name}"
        
        try:
            os.makedirs('db/backups', exist_ok=True)
            import shutil
            shutil.copy2('db/cavacrm.db', backup_path)
            logger.info(f"💾 Backup creado: {backup_path}")
        except Exception as e:
            logger.error(f"⚠️ Error creando backup: {e}")
    else:
        logger.error("❌ La migración no se completó correctamente")

if __name__ == "__main__":
    main()