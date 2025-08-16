#!/usr/bin/env python3
"""Script para verificar la configuración actual de la base de datos"""

from config import DB_CONFIG, is_deployed_environment, is_supabase_configured, should_use_supabase
from utils.database_unified import get_database_type

print("=" * 60)
print("CONFIGURACIÓN ACTUAL DE BASE DE DATOS")
print("=" * 60)

print(f"Entorno de deploy detectado: {is_deployed_environment()}")
print(f"Supabase configurado: {is_supabase_configured()}")
print(f"Debería usar Supabase: {should_use_supabase()}")
print(f"Usando Supabase: {DB_CONFIG['use_supabase']}")
print(f"Tipo de base de datos activa: {get_database_type()}")

print("\nConfiguración completa:")
for key, value in DB_CONFIG.items():
    print(f"  {key}: {value}")

print("\n" + "=" * 60)
if DB_CONFIG['use_supabase']:
    print("✅ Los datos se están grabando en SUPABASE")
else:
    print("✅ Los datos se están grabando en SQLITE (db/cavacrm.db)")
print("=" * 60)