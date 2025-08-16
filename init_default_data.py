#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialización con datos por defecto
Se ejecuta automáticamente en deploys para asegurar datos básicos
"""

import logging
from utils.database import (
    get_db_connection, insert_coordinator, insert_verifier, 
    insert_warehouse, insert_incident
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_default_coordinators():
    """Inicializa coordinadores por defecto"""
    try:
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) FROM coordinators').fetchone()[0]
        conn.close()
        
        if count == 0:
            logger.info("Añadiendo coordinadores por defecto...")
            coordinators = [
                ("Admin", "Sistema"),
                ("Coordinador", "Principal"),
                ("Supervisor", "General")
            ]
            
            for name, surnames in coordinators:
                insert_coordinator(name, surnames)
            
            logger.info(f"Añadidos {len(coordinators)} coordinadores por defecto")
        else:
            logger.info(f"Ya existen {count} coordinadores, omitiendo inicialización")
            
    except Exception as e:
        logger.error(f"Error inicializando coordinadores: {e}")

def init_default_incidents():
    """Inicializa tipos de incidencia por defecto"""
    try:
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) FROM incidents').fetchone()[0]
        conn.close()
        
        if count == 0:
            logger.info("Añadiendo tipos de incidencia por defecto...")
            incidents = [
                ("INC001", "Problema de calidad del producto"),
                ("INC002", "Retraso en la entrega"),
                ("INC003", "Documentación incorrecta"),
                ("INC004", "Problema de temperatura"),
                ("INC005", "Daño en el transporte"),
                ("INC006", "Cantidad incorrecta"),
                ("INC007", "Problema de etiquetado"),
                ("INC008", "Incumplimiento de especificaciones")
            ]
            
            for code, description in incidents:
                insert_incident(code, description)
            
            logger.info(f"Añadidos {len(incidents)} tipos de incidencia por defecto")
        else:
            logger.info(f"Ya existen {count} tipos de incidencia, omitiendo inicialización")
            
    except Exception as e:
        logger.error(f"Error inicializando incidencias: {e}")

def init_default_zones_data():
    """Inicializa verificadores y bodegas por defecto para cada zona"""
    zones = ["PENEDES", "ALT CAMP", "CONCA", "ALMENDRALEJO", "REQUENA", "CARIÑENA"]
    
    try:
        # Verificar si ya hay verificadores
        conn = get_db_connection()
        verifier_count = conn.execute('SELECT COUNT(*) FROM verifiers').fetchone()[0]
        warehouse_count = conn.execute('SELECT COUNT(*) FROM warehouses').fetchone()[0]
        conn.close()
        
        # Añadir verificadores por defecto
        if verifier_count == 0:
            logger.info("Añadiendo verificadores por defecto...")
            for i, zone in enumerate(zones, 1):
                insert_verifier(f"Verificador{i}", f"Zona{zone}", f"60000000{i}", zone)
            logger.info(f"Añadidos {len(zones)} verificadores por defecto")
        else:
            logger.info(f"Ya existen {verifier_count} verificadores, omitiendo inicialización")
        
        # Añadir bodegas por defecto
        if warehouse_count == 0:
            logger.info("Añadiendo bodegas por defecto...")
            for i, zone in enumerate(zones, 1):
                insert_warehouse(f"Bodega {zone}", f"B{12345678+i:08d}A", zone)
            logger.info(f"Añadidas {len(zones)} bodegas por defecto")
        else:
            logger.info(f"Ya existen {warehouse_count} bodegas, omitiendo inicialización")
            
    except Exception as e:
        logger.error(f"Error inicializando datos de zonas: {e}")

def insert_incident(code, description):
    """Inserta un tipo de incidencia"""
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO incidents (code, description) VALUES (?, ?)', (code, description))
        conn.commit()
        logger.info(f"Inserted incident: {code} - {description}")
    except Exception as e:
        logger.error(f"Error inserting incident: {e}")
    finally:
        conn.close()

def run_default_initialization():
    """Ejecuta toda la inicialización de datos por defecto"""
    logger.info("=== INICIANDO INICIALIZACIÓN DE DATOS POR DEFECTO ===")
    
    try:
        init_default_coordinators()
        init_default_incidents()
        init_default_zones_data()
        
        logger.info("=== INICIALIZACIÓN COMPLETADA EXITOSAMENTE ===")
        
        # Mostrar resumen
        conn = get_db_connection()
        coordinators = conn.execute('SELECT COUNT(*) FROM coordinators').fetchone()[0]
        incidents = conn.execute('SELECT COUNT(*) FROM incidents').fetchone()[0]
        verifiers = conn.execute('SELECT COUNT(*) FROM verifiers').fetchone()[0]
        warehouses = conn.execute('SELECT COUNT(*) FROM warehouses').fetchone()[0]
        conn.close()
        
        logger.info(f"RESUMEN: {coordinators} coordinadores, {incidents} tipos de incidencia, {verifiers} verificadores, {warehouses} bodegas")
        
    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        raise

if __name__ == "__main__":
    run_default_initialization()