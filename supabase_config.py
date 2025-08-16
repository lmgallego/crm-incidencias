"""Configuración de Supabase para CavaCRM"""

import os
from supabase import create_client, Client
from typing import Optional

# Configuración de Supabase
SUPABASE_URL = "https://kwzjwphngmjzuabeyivk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3emp3cGhuZ21qenVhYmV5aXZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUzNDE4NTEsImV4cCI6MjA3MDkxNzg1MX0.xbAKxMSXuJ-4Yc97hanUjVU07R5ufAgfgKgQuAC-eNQ"

# Cliente global de Supabase
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Obtiene el cliente de Supabase (singleton)"""
    global _supabase_client
    
    if _supabase_client is None:
        # Permitir override desde variables de entorno para mayor seguridad
        url = os.environ.get("SUPABASE_URL", SUPABASE_URL)
        key = os.environ.get("SUPABASE_KEY", SUPABASE_KEY)
        
        _supabase_client = create_client(url, key)
    
    return _supabase_client

def test_connection() -> bool:
    """Prueba la conexión con Supabase"""
    try:
        client = get_supabase_client()
        # Intentar hacer una consulta simple para verificar la conexión
        result = client.table("coordinators").select("count", count="exact").execute()
        return True
    except Exception as e:
        print(f"Error conectando con Supabase: {e}")
        return False