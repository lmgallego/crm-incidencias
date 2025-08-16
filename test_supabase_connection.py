#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la conexión a Supabase
"""

import os
from supabase_config import get_supabase_client, test_connection

def main():
    print("🔍 Verificando configuración de Supabase...")
    print("="*50)
    
    # Verificar variables de entorno
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"📍 SUPABASE_URL: {'✅ Configurada' if supabase_url else '❌ No configurada'}")
    print(f"🔑 SUPABASE_ANON_KEY: {'✅ Configurada' if supabase_key else '❌ No configurada'}")
    print()
    
    if not supabase_url or not supabase_key:
        print("⚠️  Variables de entorno no configuradas.")
        print("📖 Consulta GUIA_CONFIGURACION_SUPABASE.md para configurarlas.")
        print()
        print("🔧 Ejemplo para Windows PowerShell:")
        print('$env:SUPABASE_URL="https://tu-proyecto.supabase.co"')
        print('$env:SUPABASE_ANON_KEY="eyJ...tu_clave_aqui"')
        return
    
    # Probar conexión
    print("🔌 Probando conexión a Supabase...")
    try:
        client = get_supabase_client()
        success = test_connection(client)
        
        if success:
            print("✅ ¡Conexión exitosa a Supabase!")
            print("🎉 Tu aplicación está lista para usar Supabase en producción.")
        else:
            print("❌ Error en la conexión a Supabase.")
            print("🔍 Verifica que las credenciales sean correctas.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("🔍 Verifica que las tablas estén creadas en Supabase.")
    
    print("\n" + "="*50)
    print("📚 Para más ayuda, consulta: GUIA_CONFIGURACION_SUPABASE.md")

if __name__ == "__main__":
    main()