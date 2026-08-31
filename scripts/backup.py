import os
import datetime
import subprocess
import shutil
import sys
import argparse

DB_URL = os.getenv("DATABASE_URL", "postgresql://docuengine_api:api_secure_password_123@localhost:5432/docuengine")
UPLOADS_DIR = "uploads"
BACKUP_DIR = "backups"

def run_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Backup Base de Datos
    print(f"[*] Iniciando backup de la base de datos...")
    db_backup_path = os.path.join(BACKUP_DIR, f"db_backup_{timestamp}.sql")
    try:
        # Require pg_dump to be in PATH
        subprocess.run(["pg_dump", DB_URL, "-F", "c", "-f", db_backup_path], check=True)
        print(f"[+] Backup de DB completado: {db_backup_path}")
    except FileNotFoundError:
        print("[-] ERROR: 'pg_dump' no encontrado en el sistema. Asegúrate de tener PostgreSQL client instalado.")
    except subprocess.CalledProcessError as e:
        print(f"[-] ERROR durante pg_dump: {e}")
        
    # 2. Backup Archivos Físicos (Uploads)
    print(f"[*] Iniciando backup de archivos físicos (Tenant aisled)...")
    uploads_backup_path = os.path.join(BACKUP_DIR, f"uploads_backup_{timestamp}")
    try:
        # Shutil make_archive creates a zip or tar
        shutil.make_archive(uploads_backup_path, 'gztar', UPLOADS_DIR)
        print(f"[+] Backup de archivos completado: {uploads_backup_path}.tar.gz")
    except Exception as e:
        print(f"[-] ERROR archivando uploads: {e}")
        
    print(f"[*] Proceso de backup finalizado. Timestamp: {timestamp}")

if __name__ == "__main__":
    run_backup()
