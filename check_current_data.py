#!/usr/bin/env python3
"""Script para verificar los datos actuales en Supabase"""

import logging
from supabase_config import get_supabase_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_supabase_data():
    """Verifica los datos actuales en Supabase"""
    try:
        client = get_supabase_client()
        
        print("\n" + "="*60)
        print("DATOS ACTUALES EN SUPABASE")
        print("="*60)
        
        # Verificar coordinadores
        coordinators = client.table('coordinators').select('*').execute()
        print(f"\n📋 COORDINADORES: {len(coordinators.data)} registros")
        if coordinators.data:
            for coord in coordinators.data[:3]:  # Mostrar solo los primeros 3
                print(f"  - ID: {coord['id']}, Nombre: {coord['name']}")
            if len(coordinators.data) > 3:
                print(f"  ... y {len(coordinators.data) - 3} más")
        
        # Verificar verificadores
        verifiers = client.table('verifiers').select('*').execute()
        print(f"\n🔍 VERIFICADORES: {len(verifiers.data)} registros")
        if verifiers.data:
            for ver in verifiers.data[:3]:  # Mostrar solo los primeros 3
                print(f"  - ID: {ver['id']}, Nombre: {ver['name']}, Zona: {ver['zone']}")
            if len(verifiers.data) > 3:
                print(f"  ... y {len(verifiers.data) - 3} más")
        
        # Verificar bodegas
        warehouses = client.table('warehouses').select('*').execute()
        print(f"\n🏪 BODEGAS: {len(warehouses.data)} registros")
        if warehouses.data:
            for wh in warehouses.data[:3]:  # Mostrar solo los primeros 3
                print(f"  - ID: {wh['id']}, Nombre: {wh['name']}")
            if len(warehouses.data) > 3:
                print(f"  ... y {len(warehouses.data) - 3} más")
        
        # Verificar incidencias
        incidents = client.table('incidents').select('*').execute()
        print(f"\n⚠️ INCIDENCIAS: {len(incidents.data)} registros")
        if incidents.data:
            for inc in incidents.data:
                print(f"  - ID: {inc['id']}, Código: {inc['code']}, Descripción: {inc['description']}")
        
        # Verificar registros de incidencias
        incident_records = client.table('incident_records').select('*').execute()
        print(f"\n📝 REGISTROS DE INCIDENCIAS: {len(incident_records.data)} registros")
        if incident_records.data:
            for rec in incident_records.data[:3]:  # Mostrar solo los primeros 3
                print(f"  - ID: {rec['id']}, Estado: {rec.get('status', 'N/A')}")
            if len(incident_records.data) > 3:
                print(f"  ... y {len(incident_records.data) - 3} más")
        
        print("\n" + "="*60)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando datos: {e}")
        return False

if __name__ == "__main__":
    check_supabase_data()