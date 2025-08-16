#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que las funciones de edición se pueden importar correctamente
"""

try:
    from components.forms import (
        edit_coordinator_form,
        edit_verifier_form, 
        edit_warehouse_form,
        edit_incident_form
    )
    print("✅ ÉXITO: Todas las funciones de edición se importaron correctamente")
    print(f"✅ edit_coordinator_form: {edit_coordinator_form}")
    print(f"✅ edit_verifier_form: {edit_verifier_form}")
    print(f"✅ edit_warehouse_form: {edit_warehouse_form}")
    print(f"✅ edit_incident_form: {edit_incident_form}")
except ImportError as e:
    print(f"❌ ERROR DE IMPORTACIÓN: {e}")
except Exception as e:
    print(f"❌ ERROR GENERAL: {e}")

print("\n📋 Verificando contenido del archivo forms.py...")
try:
    with open('components/forms.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    functions_to_check = [
        'def edit_coordinator_form(',
        'def edit_verifier_form(',
        'def edit_warehouse_form(',
        'def edit_incident_form('
    ]
    
    for func in functions_to_check:
        if func in content:
            print(f"✅ Encontrada: {func}")
        else:
            print(f"❌ NO encontrada: {func}")
            
except Exception as e:
    print(f"❌ Error leyendo forms.py: {e}")