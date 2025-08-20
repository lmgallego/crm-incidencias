import os
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Detectar si Supabase está configurado
def is_supabase_configured():
    """
    Detecta si Supabase está configurado mediante variables de entorno
    """
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    # También verificar si existe el archivo de configuración
    config_file_exists = os.path.exists('supabase_config.py')
    
    return bool(supabase_url and supabase_key) or config_file_exists

# Detectar si estamos en un entorno de deploy
def is_deployed_environment():
    """
    Detecta si la aplicación está ejecutándose en un entorno de deploy
    """
    # Detectar Streamlit Cloud
    if os.getenv('STREAMLIT_SHARING_MODE') or os.getenv('STREAMLIT_SERVER_PORT'):
        return True
    
    # Detectar Heroku
    if os.getenv('DYNO'):
        return True
    
    # Detectar Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        return True
    
    # Detectar otros servicios comunes
    if any([
        os.getenv('VERCEL'),
        os.getenv('NETLIFY'),
        os.getenv('AWS_LAMBDA_FUNCTION_NAME'),
        os.getenv('GOOGLE_CLOUD_PROJECT')
    ]):
        return True
    
    # Para testing: permitir forzar modo deploy
    if os.getenv('FORCE_DEPLOY_MODE') == 'true':
        return True
    
    return False

# Detectar qué base de datos usar
def should_use_supabase():
    """
    Determina si se debe usar Supabase en lugar de SQLite
    """
    # Usar Supabase si está configurado (sin importar el entorno)
    # O si se fuerza mediante variable de entorno
    if os.getenv('FORCE_SUPABASE') == 'true':
        return True
    
    # Cambio: usar Supabase siempre que esté configurado
    return is_supabase_configured()

# Configuración de la base de datos
DB_CONFIG = {
    'path': 'db/cavacrm.db',
    'backup_on_deploy': True,
    'preserve_data': True,
    'use_supabase': should_use_supabase()
}

# Logging de configuración
logger.info(f"Deployed environment detected: {is_deployed_environment()}")
logger.info(f"Supabase configured: {is_supabase_configured()}")
logger.info(f"Using Supabase: {should_use_supabase()}")
logger.info(f"Database config: {DB_CONFIG}")