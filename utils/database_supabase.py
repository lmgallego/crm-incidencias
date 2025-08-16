import pandas as pd
import os
import logging
import datetime
from supabase_config import get_supabase_client, test_connection
from .backup_restore import backup_db
try:
    from config import is_deployed_environment, DB_CONFIG
except ImportError:
    # Fallback si no existe config.py
    def is_deployed_environment():
        return False
    DB_CONFIG = {'path': 'db/cavacrm.db', 'preserve_data': True}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_supabase_connection():
    """Obtiene el cliente de Supabase"""
    return get_supabase_client()

def init_db():
    """Inicializa la base de datos Supabase"""
    # Verificar entorno y configuración
    deployed = is_deployed_environment()
    preserve_data = DB_CONFIG.get('preserve_data', True)
    
    logger.info(f"Environment - Deployed: {deployed}, Preserve data: {preserve_data}")
    
    try:
        # Verificar conexión con Supabase
        client = get_supabase_connection()
        
        # Verificar si las tablas existen y tienen datos
        existing_records = 0
        tables_exist = True
        
        try:
            # Verificar si las tablas existen consultando coordinators
            result = client.table('coordinators').select('count', count='exact').limit(1).execute()
            existing_records = result.count if result.count else 0
            logger.info(f"Existing coordinators in database: {existing_records}")
        except Exception as e:
            logger.info(f"Database tables don't exist yet or are not accessible: {e}")
            tables_exist = False
        
        if not tables_exist:
            logger.warning("⚠️ Las tablas no existen en Supabase.")
            logger.info("Por favor, ejecuta el script supabase_schema.sql en el SQL Editor de Supabase")
            return False
        
        # Verificar datos después de la inicialización
        try:
            coordinators_result = client.table('coordinators').select('count', count='exact').limit(1).execute()
            final_count = coordinators_result.count if coordinators_result.count else 0
            logger.info(f"Final coordinators count after init: {final_count}")
            
            # Verificar otras tablas importantes
            incidents_result = client.table('incident_records').select('count', count='exact').limit(1).execute()
            incident_count = incidents_result.count if incidents_result.count else 0
            logger.info(f"Total incident records: {incident_count}")
            
        except Exception as e:
            logger.warning(f"Could not count records after init: {e}")
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing Supabase database: {e}")
        return False

def insert_coordinator(name, surnames):
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').insert({
            'name': name,
            'surnames': surnames
        }).execute()
        logger.info(f"Inserted coordinator: {name} {surnames}")
        return True
    except Exception as e:
        logger.error(f"Error inserting coordinator: {e}")
        return False

def insert_verifier(name, surnames, phone, zone):
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').insert({
            'name': name,
            'surnames': surnames,
            'phone': phone,
            'zone': zone
        }).execute()
        logger.info(f"Inserted verifier: {name} {surnames}")
        return True
    except Exception as e:
        logger.error(f"Error inserting verifier: {e}")
        return False

def insert_warehouse(name, codigo_consejo, zone):
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').insert({
            'name': name,
            'codigo_consejo': codigo_consejo,
            'zone': zone
        }).execute()
        logger.info(f"Inserted warehouse: {name} with Código Consejo {codigo_consejo}")
        return True
    except Exception as e:
        logger.error(f"Error inserting warehouse: {e}")
        return False

def load_csv_to_verifiers(csv_file, sep=','):
    # Resetear el puntero del archivo al inicio
    csv_file.seek(0)
    df = pd.read_csv(csv_file, sep=sep, encoding='utf-8-sig')
    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
    client = get_supabase_connection()
    
    for _, row in df.iterrows():
        name = row['name']
        surnames = row['surnames']
        
        # Verificar si ya existe
        existing = client.table('verifiers').select('id').eq('name', name).eq('surnames', surnames).execute()
        
        if not existing.data:
            insert_verifier(name, surnames, row.get('phone', ''), row.get('zone', ''))
        else:
            print(f"Verifier {name} {surnames} already exists, skipping.")

def load_csv_to_warehouses(csv_file, sep=','):
    # Resetear el puntero del archivo al inicio
    csv_file.seek(0)
    df = pd.read_csv(csv_file, sep=sep, encoding='utf-8-sig')
    # Limpiar nombres de columnas (eliminar espacios, BOM y caracteres especiales)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ï»¿', '')
    client = get_supabase_connection()
    
    for _, row in df.iterrows():
        codigo_consejo = row['codigo_consejo']
        
        # Verificar si ya existe
        existing = client.table('warehouses').select('id').eq('codigo_consejo', codigo_consejo).execute()
        
        if not existing.data:
            insert_warehouse(row['name'], codigo_consejo, row.get('zone', ''))
        else:
            print(f"Warehouse with Código Consejo {codigo_consejo} already exists, skipping.")

def insert_incident(description, custom_code=None):
    """Inserta una nueva incidencia con código automático o personalizado"""
    try:
        client = get_supabase_connection()
        
        if custom_code:
            # Verificar si el código personalizado ya existe
            existing = client.table('incidents').select('id').eq('code', custom_code).execute()
            if existing.data:
                return {'success': False, 'error': f'El código "{custom_code}" ya existe. Por favor, use un código diferente.'}
            code = custom_code
        else:
            # Generar código automático
            count_result = client.table('incidents').select('count', count='exact').execute()
            count = count_result.count if count_result.count else 0
            code = f"{count + 1:03d}"
            
            # Verificar que el código automático no exista (por seguridad)
            while True:
                existing = client.table('incidents').select('id').eq('code', code).execute()
                if not existing.data:
                    break
                count += 1
                code = f"{count + 1:03d}"
        
        result = client.table('incidents').insert({
            'code': code,
            'description': description
        }).execute()
        
        logger.info(f"Inserted incident with code {code}")
        return {'success': True, 'code': code}
        
    except Exception as e:
        logger.error(f"Error inserting incident: {e}")
        return {'success': False, 'error': f'Error al guardar la incidencia: {str(e)}'}

def get_coordinators():
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').select('id, name, surnames').execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting coordinators: {e}")
        return []

def get_verifiers():
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').select('id, name, surnames, phone, zone').execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting verifiers: {e}")
        return []

def get_warehouses():
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').select('id, name, codigo_consejo, zone').execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting warehouses: {e}")
        return []

def get_incidents():
    try:
        client = get_supabase_connection()
        result = client.table('incidents').select('id, code, description').execute()
        return [(row['id'], f"{row['code']} - {row['description']}") for row in result.data]
    except Exception as e:
        logger.error(f"Error getting incidents: {e}")
        return []

def insert_incident_record(date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, status, responsible):
    try:
        client = get_supabase_connection()
        result = client.table('incident_records').insert({
            'date': date,
            'registering_coordinator_id': registering_coordinator_id,
            'warehouse_id': warehouse_id,
            'causing_verifier_id': causing_verifier_id,
            'incident_id': incident_id,
            'assigned_coordinator_id': assigned_coordinator_id,
            'explanation': explanation,
            'status': status,
            'responsible': responsible
        }).execute()
        logger.info(f"Inserted incident record on date {date}")
        return True
    except Exception as e:
        logger.error(f"Error inserting incident record: {e}")
        return False

def get_incident_records():
    try:
        client = get_supabase_connection()
        result = client.table('incident_records').select(
            'id, date, registering_coordinator_id, warehouse_id, causing_verifier_id, incident_id, assigned_coordinator_id, explanation, status, responsible, '
            'coordinators!registering_coordinator_id(name, surnames), '
            'warehouses(name), '
            'verifiers(name, surnames), '
            'incidents(code, description), '
            'coordinators!assigned_coordinator_id(name, surnames)'
        ).order('date', desc=True).execute()
        
        records = []
        for record in result.data:
            registering_coordinator = f"{record['coordinators']['name']} {record['coordinators']['surnames']}"
            warehouse = record['warehouses']['name']
            causing_verifier = f"{record['verifiers']['name']} {record['verifiers']['surnames']}"
            incident = f"{record['incidents']['code']} - {record['incidents']['description']}"
            assigned_coordinator = f"{record['coordinators']['name']} {record['coordinators']['surnames']}"
            
            display_text = f"ID: {record['id']} - Fecha: {record['date']} - Incidencia: {incident} - Bodega: {warehouse} - Verificador: {causing_verifier} - Coordinador: {assigned_coordinator}"
            records.append((record['id'], display_text))
        
        return records
    except Exception as e:
        logger.error(f"Error getting incident records: {e}")
        return []

def insert_incident_action(incident_record_id, action_date, action_description, new_status, performed_by):
    try:
        client = get_supabase_connection()
        
        # Insertar la acción
        result = client.table('incident_actions').insert({
            'incident_record_id': incident_record_id,
            'action_date': action_date,
            'action_description': action_description,
            'new_status': new_status,
            'performed_by': performed_by
        }).execute()
        
        # Actualizar el estado del registro si se proporciona un nuevo estado
        if new_status:
            client.table('incident_records').update({
                'status': new_status
            }).eq('id', incident_record_id).execute()
        
        logger.info(f"Inserted action for incident record {incident_record_id}")
        return True
    except Exception as e:
        logger.error(f"Error inserting incident action: {e}")
        return False

def get_incident_actions(incident_record_id):
    try:
        client = get_supabase_connection()
        result = client.table('incident_actions').select(
            'action_date, action_description, new_status, coordinators(name, surnames)'
        ).eq('incident_record_id', incident_record_id).order('action_date').execute()
        
        actions = []
        for row in result.data:
            coordinator = row['coordinators']
            performed_by = f"{coordinator['name']} {coordinator['surnames']}" if coordinator else "N/A"
            actions.append({
                'action_date': row['action_date'],
                'action_description': row['action_description'],
                'new_status': row['new_status'],
                'performed_by': performed_by
            })
        
        return actions
    except Exception as e:
        logger.error(f"Error getting incident actions: {e}")
        return []

def get_all_incident_records_df():
    try:
        client = get_supabase_connection()
        
        # Consulta compleja con joins usando RPC o múltiples consultas
        result = client.table('incident_records').select(
            '*, coordinators!registering_coordinator_id(name, surnames), '
            'warehouses(name, zone), verifiers(name, surnames, zone), '
            'incidents(description), coordinators!assigned_coordinator_id(name, surnames)'
        ).execute()
        
        # Procesar los datos para crear el DataFrame
        processed_data = []
        for row in result.data:
            reg_coord = row['coordinators']
            warehouse = row['warehouses']
            verifier = row['verifiers']
            incident = row['incidents']
            assigned_coord = row.get('coordinators', {})
            
            processed_row = {
                'id': row['id'],
                'date': row['date'],
                'registering_coordinator': f"{reg_coord['name']} {reg_coord['surnames']}" if reg_coord else "N/A",
                'warehouse': warehouse['name'] if warehouse else "N/A",
                'warehouse_zone': warehouse['zone'] if warehouse else "N/A",
                'causing_verifier': f"{verifier['name']} {verifier['surnames']}" if verifier else "N/A",
                'verifier_zone': verifier['zone'] if verifier else "N/A",
                'incident_type': incident['description'] if incident else "N/A",
                'assigned_coordinator': f"{assigned_coord['name']} {assigned_coord['surnames']}" if assigned_coord else "N/A",
                'explanation': row['explanation'],
                'status': row['status'],
                'responsible': row['responsible']
            }
            processed_data.append(processed_row)
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting incident records dataframe: {e}")
        return pd.DataFrame()

def get_all_verifiers_df():
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').select('*').execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        logger.error(f"Error getting verifiers dataframe: {e}")
        return pd.DataFrame()

def get_all_warehouses_df():
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').select('*').execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        logger.error(f"Error getting warehouses dataframe: {e}")
        return pd.DataFrame()

def get_incidents_by_zone():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('warehouse_zone').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_verifier():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('causing_verifier').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_warehouse():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('warehouse').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_type():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('incident_type').size().reset_index(name='count')
    return pd.DataFrame()

def get_incidents_by_status():
    df = get_all_incident_records_df()
    if not df.empty:
        return df.groupby('status').size().reset_index(name='count')
    return pd.DataFrame()

def get_assignments_by_verifier():
    df = get_all_incident_records_df()
    if not df.empty:
        return df[df['responsible'] == 'Verificador'].groupby('causing_verifier').size().reset_index(name='count')
    return pd.DataFrame()

def reset_database():
    try:
        client = get_supabase_connection()
        tables = ['incident_actions', 'incident_records', 'incidents', 'warehouses', 'verifiers', 'coordinators']
        
        for table in tables:
            try:
                # Eliminar todos los registros de cada tabla
                result = client.table(table).delete().neq('id', 0).execute()
                logger.info(f"Cleared table: {table}")
            except Exception as e:
                logger.warning(f"Could not clear table {table}: {e}")
        
        logger.info("Database reset completed")
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False

def get_incident_record_details(incident_record_id):
    try:
        client = get_supabase_connection()
        result = client.table('incident_records').select(
            '*, coordinators!registering_coordinator_id(name, surnames), '
            'warehouses(name, zone), verifiers(name, surnames, zone), '
            'incidents(description), coordinators!assigned_coordinator_id(name, surnames)'
        ).eq('id', incident_record_id).execute()
        
        if result.data:
            row = result.data[0]
            reg_coord = row['coordinators']
            warehouse = row['warehouses']
            verifier = row['verifiers']
            incident = row['incidents']
            assigned_coord = row.get('coordinators', {})
            
            return {
                'id': row['id'],
                'date': row['date'],
                'registering_coordinator': f"{reg_coord['name']} {reg_coord['surnames']}" if reg_coord else "N/A",
                'warehouse': warehouse['name'] if warehouse else "N/A",
                'warehouse_zone': warehouse['zone'] if warehouse else "N/A",
                'causing_verifier': f"{verifier['name']} {verifier['surnames']}" if verifier else "N/A",
                'verifier_zone': verifier['zone'] if verifier else "N/A",
                'incident_type': incident['description'] if incident else "N/A",
                'assigned_coordinator': f"{assigned_coord['name']} {assigned_coord['surnames']}" if assigned_coord else "N/A",
                'explanation': row['explanation'],
                'status': row['status'],
                'responsible': row['responsible']
            }
        return {}
    except Exception as e:
        logger.error(f"Error getting incident record details: {e}")
        return {}

def export_incidents_to_excel():
    """Exporta historial completo de incidencias con acciones a Excel"""
    try:
        # Obtener datos usando las funciones existentes
        df_incidents = get_all_incident_records_df()
        
        # Para las acciones, necesitamos una consulta separada
        client = get_supabase_connection()
        actions_result = client.table('incident_actions').select(
            'incident_record_id, action_date, action_description, new_status, '
            'coordinators(name, surnames)'
        ).execute()
        
        actions_data = []
        for row in actions_result.data:
            coordinator = row['coordinators']
            actions_data.append({
                'ID Registro': row['incident_record_id'],
                'Fecha Acción': row['action_date'],
                'Descripción Acción': row['action_description'],
                'Nuevo Estado': row['new_status'],
                'Realizado Por': f"{coordinator['name']} {coordinator['surnames']}" if coordinator else "N/A"
            })
        
        df_actions = pd.DataFrame(actions_data)
        
        # Crear archivo Excel
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'historial_incidencias_{timestamp}.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_incidents.to_excel(writer, sheet_name='Incidencias', index=False)
            df_actions.to_excel(writer, sheet_name='Acciones', index=False)
        
        return filename
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise e

def create_backup():
    """Crea una copia de seguridad de la base de datos"""
    try:
        # Para Supabase, podríamos exportar los datos a JSON o CSV
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'supabase_backup_{timestamp}.json'
        
        # Exportar todas las tablas
        client = get_supabase_connection()
        backup_data = {}
        
        tables = ['coordinators', 'verifiers', 'warehouses', 'incidents', 'incident_records', 'incident_actions']
        
        for table in tables:
            try:
                result = client.table(table).select('*').execute()
                backup_data[table] = result.data
            except Exception as e:
                logger.warning(f"Could not backup table {table}: {e}")
                backup_data[table] = []
        
        # Guardar en archivo JSON
        import json
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Backup created: {backup_filename}")
        return backup_filename
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise e

def get_dashboard_stats():
    """Obtiene estadísticas para el dashboard"""
    try:
        client = get_supabase_connection()
        
        # Estadísticas generales
        stats = {}
        
        # Total de incidencias
        total_result = client.table('incident_records').select('count', count='exact').execute()
        stats['total_incidents'] = total_result.count if total_result.count else 0
        
        # Incidencias no resueltas (pendientes)
        pending_result = client.table('incident_records').select('count', count='exact').neq('status', 'Solucionado').execute()
        stats['pending_incidents'] = pending_result.count if pending_result.count else 0
        
        # Incidencias resueltas
        resolved_result = client.table('incident_records').select('count', count='exact').eq('status', 'Solucionado').execute()
        stats['resolved_incidents'] = resolved_result.count if resolved_result.count else 0
        
        # Incidencias por estado
        df = get_all_incident_records_df()
        if not df.empty:
            stats['by_status'] = df.groupby('status').size().reset_index(name='count')
        else:
            stats['by_status'] = pd.DataFrame()
        
        # Incidencias recientes (últimos 7 días)
        from datetime import datetime, timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_result = client.table('incident_records').select('count', count='exact').gte('date', seven_days_ago).execute()
        stats['recent_incidents'] = recent_result.count if recent_result.count else 0
        
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {
            'total_incidents': 0,
            'pending_incidents': 0,
            'resolved_incidents': 0,
            'by_status': pd.DataFrame(),
            'recent_incidents': 0
        }

def get_pending_incidents_summary():
    """Obtiene resumen de incidencias pendientes para el dashboard"""
    try:
        client = get_supabase_connection()
        result = client.table('incident_records').select(
            'id, date, status, responsible, '
            'warehouses(name, zone), verifiers(name, surnames), '
            'incidents(description), coordinators(name, surnames)'
        ).neq('status', 'Solucionado').order('date', desc=True).limit(10).execute()
        
        processed_data = []
        for row in result.data:
            warehouse = row['warehouses']
            verifier = row['verifiers']
            incident = row['incidents']
            coordinator = row['coordinators']
            
            processed_data.append({
                'id': row['id'],
                'date': row['date'],
                'warehouse': warehouse['name'] if warehouse else "N/A",
                'warehouse_zone': warehouse['zone'] if warehouse else "N/A",
                'causing_verifier': f"{verifier['name']} {verifier['surnames']}" if verifier else "N/A",
                'incident_type': incident['description'] if incident else "N/A",
                'assigned_coordinator': f"{coordinator['name']} {coordinator['surnames']}" if coordinator else "N/A",
                'status': row['status'],
                'responsible': row['responsible']
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting pending incidents summary: {e}")
        return pd.DataFrame()

def get_recent_actions():
    """Obtiene las acciones más recientes para el dashboard"""
    try:
        client = get_supabase_connection()
        result = client.table('incident_actions').select(
            'action_date, action_description, new_status, '
            'coordinators(name, surnames), incident_records(id, warehouses(name))'
        ).order('action_date', desc=True).limit(5).execute()
        
        processed_data = []
        for row in result.data:
            coordinator = row['coordinators']
            incident_record = row['incident_records']
            warehouse = incident_record['warehouses'] if incident_record else None
            
            processed_data.append({
                'action_date': row['action_date'],
                'action_description': row['action_description'],
                'new_status': row['new_status'],
                'performed_by': f"{coordinator['name']} {coordinator['surnames']}" if coordinator else "N/A",
                'incident_id': incident_record['id'] if incident_record else "N/A",
                'warehouse': warehouse['name'] if warehouse else "N/A"
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting recent actions: {e}")
        return pd.DataFrame()

def search_incident_by_code(code):
    """Busca una incidencia por su código único"""
    try:
        client = get_supabase_connection()
        result = client.table('incidents').select('*').eq('code', code).execute()
        
        if result.data:
            return {'success': True, 'incident': result.data[0]}
        else:
            return {'success': False, 'error': f'No se encontró ninguna incidencia con el código "{code}"'}
    except Exception as e:
        logger.error(f"Error searching incident by code: {e}")
        return {'success': False, 'error': f'Error al buscar la incidencia: {str(e)}'}

def get_incident_records_by_incident_code(code):
    """Obtiene todos los registros de incidencia asociados a un código de incidencia"""
    try:
        client = get_supabase_connection()
        result = client.table('incident_records').select(
            '*, incidents!inner(code, description), '
            'coordinators!registering_coordinator_id(name, surnames), '
            'warehouses(name, zone), verifiers(name, surnames), '
            'coordinators!assigned_coordinator_id(name, surnames)'
        ).eq('incidents.code', code).order('date', desc=True).execute()
        
        if result.data:
            processed_records = []
            for row in result.data:
                incident = row['incidents']
                reg_coord = row['coordinators']
                warehouse = row['warehouses']
                verifier = row['verifiers']
                assigned_coord = row.get('coordinators', {})
                
                processed_records.append({
                    'id': row['id'],
                    'date': row['date'],
                    'incident_code': incident['code'] if incident else "N/A",
                    'incident_description': incident['description'] if incident else "N/A",
                    'registering_coordinator': f"{reg_coord['name']} {reg_coord['surnames']}" if reg_coord else "N/A",
                    'warehouse': warehouse['name'] if warehouse else "N/A",
                    'warehouse_zone': warehouse['zone'] if warehouse else "N/A",
                    'causing_verifier': f"{verifier['name']} {verifier['surnames']}" if verifier else "N/A",
                    'assigned_coordinator': f"{assigned_coord['name']} {assigned_coord['surnames']}" if assigned_coord else "N/A",
                    'explanation': row['explanation'],
                    'status': row['status'],
                    'responsible': row['responsible']
                })
            
            return {'success': True, 'records': processed_records}
        else:
            return {'success': False, 'error': f'No se encontraron registros para el código de incidencia "{code}"'}
    except Exception as e:
        logger.error(f"Error getting incident records by code: {e}")
        return {'success': False, 'error': f'Error al buscar registros: {str(e)}'}

# Funciones de actualización/edición
def update_coordinator(coordinator_id, name, surnames):
    """Actualizar un coordinador existente"""
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').update({
            'name': name,
            'surnames': surnames
        }).eq('id', coordinator_id).execute()
        
        if result.data:
            logger.info(f"Updated coordinator ID {coordinator_id}: {name} {surnames}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating coordinator: {e}")
        return False

def update_verifier(verifier_id, name, surnames, phone, zone):
    """Actualizar un verificador existente"""
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').update({
            'name': name,
            'surnames': surnames,
            'phone': phone,
            'zone': zone
        }).eq('id', verifier_id).execute()
        
        if result.data:
            logger.info(f"Updated verifier ID {verifier_id}: {name} {surnames}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating verifier: {e}")
        return False

def update_warehouse(warehouse_id, name, codigo_consejo, zone):
    """Actualizar una bodega existente"""
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').update({
            'name': name,
            'codigo_consejo': codigo_consejo,
            'zone': zone
        }).eq('id', warehouse_id).execute()
        
        if result.data:
            logger.info(f"Updated warehouse ID {warehouse_id}: {name}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating warehouse: {e}")
        return False

def update_incident(incident_id, code, description):
    """Actualizar un tipo de incidencia existente"""
    try:
        client = get_supabase_connection()
        result = client.table('incidents').update({
            'code': code,
            'description': description
        }).eq('id', incident_id).execute()
        
        if result.data:
            logger.info(f"Updated incident ID {incident_id}: {code}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating incident: {e}")
        return False

# Funciones para obtener registros individuales
def get_coordinator_by_id(coordinator_id):
    """Obtener un coordinador por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('coordinators').select('*').eq('id', coordinator_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting coordinator: {e}")
        return None

def get_verifier_by_id(verifier_id):
    """Obtener un verificador por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('verifiers').select('*').eq('id', verifier_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting verifier: {e}")
        return None

def get_warehouse_by_id(warehouse_id):
    """Obtener una bodega por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('warehouses').select('*').eq('id', warehouse_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting warehouse: {e}")
        return None

def get_incident_by_id(incident_id):
    """Obtener un tipo de incidencia por ID"""
    try:
        client = get_supabase_connection()
        result = client.table('incidents').select('*').eq('id', incident_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting incident: {e}")
        return None

def get_pending_incidents_by_coordinator(coordinator_id=None):
    """Obtiene incidencias pendientes filtradas por coordinador asignado"""
    try:
        client = get_supabase_connection()
        
        if coordinator_id:
            result = client.table('incident_records').select(
                'id, date, status, responsible, '
                'warehouses(name, zone), verifiers(name, surnames), '
                'incidents(description), coordinators(name, surnames)'
            ).neq('status', 'Solucionado').eq('assigned_coordinator_id', coordinator_id).order('date', desc=True).limit(10).execute()
        else:
            result = client.table('incident_records').select(
                'id, date, status, responsible, '
                'warehouses(name, zone), verifiers(name, surnames), '
                'incidents(description), coordinators(name, surnames)'
            ).neq('status', 'Solucionado').order('date', desc=True).limit(10).execute()
        
        processed_data = []
        for row in result.data:
            warehouse = row['warehouses']
            verifier = row['verifiers']
            incident = row['incidents']
            coordinator = row['coordinators']
            
            processed_data.append({
                'id': row['id'],
                'date': row['date'],
                'warehouse': warehouse['name'] if warehouse else "N/A",
                'warehouse_zone': warehouse['zone'] if warehouse else "N/A",
                'causing_verifier': f"{verifier['name']} {verifier['surnames']}" if verifier else "N/A",
                'incident_type': incident['description'] if incident else "N/A",
                'assigned_coordinator': f"{coordinator['name']} {coordinator['surnames']}" if coordinator else "N/A",
                'status': row['status'],
                'responsible': row['responsible']
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting pending incidents by coordinator: {e}")
        return pd.DataFrame()

def get_filtered_pending_incidents(coordinator_id=None, status=None, days=None):
    """Obtiene incidencias pendientes con filtros múltiples"""
    try:
        client = get_supabase_connection()
        
        # Construir la consulta base
        query = client.table('incident_records').select(
            'id, date, status, responsible, '
            'warehouses(name, zone), verifiers(name, surnames), '
            'incidents(description), coordinators(name, surnames)'
        ).neq('status', 'Solucionado')
        
        # Agregar filtros según los parámetros
        if coordinator_id:
            query = query.eq('assigned_coordinator_id', coordinator_id)
        
        if status:
            query = query.eq('status', status)
        
        if days:
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = query.gte('date', cutoff_date)
        
        result = query.order('date', desc=True).limit(20).execute()
        
        processed_data = []
        for row in result.data:
            warehouse = row['warehouses']
            verifier = row['verifiers']
            incident = row['incidents']
            coordinator = row['coordinators']
            
            processed_data.append({
                'id': row['id'],
                'date': row['date'],
                'warehouse': warehouse['name'] if warehouse else "N/A",
                'warehouse_zone': warehouse['zone'] if warehouse else "N/A",
                'causing_verifier': f"{verifier['name']} {verifier['surnames']}" if verifier else "N/A",
                'incident_type': incident['description'] if incident else "N/A",
                'assigned_coordinator': f"{coordinator['name']} {coordinator['surnames']}" if coordinator else "N/A",
                'status': row['status'],
                'responsible': row['responsible']
            })
        
        return pd.DataFrame(processed_data)
    except Exception as e:
        logger.error(f"Error getting filtered pending incidents: {e}")
        return pd.DataFrame()