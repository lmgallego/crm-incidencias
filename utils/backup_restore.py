import sqlite3
import shutil
import datetime
import os

DB_PATH = 'db/cavacrm.db'

def backup_db(backup_dir='backups'):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'cavacrm_backup_{timestamp}.db')
    shutil.copy(DB_PATH, backup_path)
    return backup_path

def restore_db(backup_path):
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    shutil.copy(backup_path, DB_PATH)
    return DB_PATH