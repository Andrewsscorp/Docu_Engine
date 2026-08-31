import os
import subprocess
import shutil
import sys
import argparse

DB_URL = os.getenv("DATABASE_URL", "postgresql://docuengine_api:api_secure_password_123@localhost:5432/docuengine")
UPLOADS_DIR = "uploads"
BACKUP_DIR = "backups"

def run_restore(timestamp):
    db_backup_path = os.path.join(BACKUP_DIR, f"db_backup_{timestamp}.sql")
    uploads_backup_path = os.path.join(BACKUP_DIR, f"uploads_backup_{timestamp}.tar.gz")
    
    if not os.path.exists(db_backup_path):
        print(f"[-] ERROR: No se encuentra el backup de base de datos {db_backup_path}")
        return
    if not os.path.exists(uploads_backup_path):
        print(f"[-] ERROR: No se encuentra el backup de archivos {uploads_backup_path}")
        return
        
    # 1. Restore DB
    print(f"[*] Restaurando base de datos desde {db_backup_path}...")
    try:
        # Require pg_restore
        # Warning: This will overwrite or error out if tables exist depending on pg_restore flags (-c cleans)
        subprocess.run(["pg_restore", "-d", DB_URL, "-c", "-1", db_backup_path], check=True)
        print(f"[+] Base de datos restaurada con éxito.")
    except FileNotFoundError:
        print("[-] ERROR: 'pg_restore' no encontrado en el sistema.")
    except subprocess.CalledProcessError as e:
        print(f"[-] ERROR durante pg_restore: {e}")
        
    # 2. Restore Files
    print(f"[*] Restaurando archivos en /{UPLOADS_DIR}...")
    try:
        if os.path.exists(UPLOADS_DIR):
            print(f"[*] Limpiando directorio {UPLOADS_DIR} existente...")
            shutil.rmtree(UPLOADS_DIR)
        shutil.unpack_archive(uploads_backup_path, UPLOADS_DIR, 'gztar')
        print(f"[+] Archivos restaurados con éxito.")
    except Exception as e:
        print(f"[-] ERROR restaurando archivos: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restaurar backup del SGDEA")
    parser.add_argument("timestamp", help="El timestamp del backup (ej. 20260830_200000)")
    args = parser.parse_args()
    run_restore(args.timestamp)
