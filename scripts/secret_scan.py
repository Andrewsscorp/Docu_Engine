import os
import re
import sys

# Definimos los patrones de vulnerabilidad (Secretos quemados)
PATTERNS = {
    "AWS Key": r"AKIA[0-9A-Z]{16}",
    "Private Key": r"-----BEGIN PRIVATE KEY-----",
    "Generic Token": r"ghp_[a-zA-Z0-9]{36}|ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
    "Burned Password": r"(?i)password\s*=\s*['\"][^'\"]+['\"]"
}

def scan_directory(directory):
    found_secrets = False
    for root, dirs, files in os.walk(directory):
        # Ignorar directorios de desarrollo
        if ".venv" in root or ".git" in root or "__pycache__" in root:
            continue
            
        for file in files:
            # Solo escaneamos código fuente
            if file.endswith(('.py', '.yml', '.env', '.json', '.html')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.readlines()
                        
                    for line_num, line in enumerate(content, 1):
                        for label, pattern in PATTERNS.items():
                            if re.search(pattern, line):
                                print(f"[!] SECRET EXPUESTO: {label} en {filepath}:{line_num}")
                                found_secrets = True
                except Exception:
                    pass
    return found_secrets

if __name__ == "__main__":
    print("[*] Iniciando Escáner de Secretos Estático (SAST)...")
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    has_secrets = scan_directory(target)
    
    if has_secrets:
        print("[-] FALLO: Se encontraron secretos quemados en el código. ¡Bloqueando despliegue!")
        sys.exit(1)
    else:
        print("[+] ÉXITO: Código limpio. No se detectaron secretos quemados.")
        sys.exit(0)
