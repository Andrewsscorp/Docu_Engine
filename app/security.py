import os
import secrets
from dotenv import load_dotenv
load_dotenv()
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Depends
from itsdangerous import URLSafeTimedSerializer
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session

import os
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Missing SECRET_KEY environment variable")
session_signer = URLSafeTimedSerializer(SECRET_KEY)

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)
DUMMY_HASH = ph.hash("dummy_password_for_timing_attack_mitigation")

_hmac_env = os.environ.get("MASTER_HMAC_KEY", "dummy-hmac-key")
_db_env = os.environ.get("DB_CRYPT_KEY", "dummy-db-key")

MASTER_HMAC_KEY = _hmac_env.encode('utf-8')
DB_CRYPT_KEY = _db_env

MAX_FAILS_PER_HOUR = 5
failed_ip_attempts = defaultdict(list)
failed_user_attempts = defaultdict(list)

settings_l1_cache = {}

def invalidate_settings_cache(tenant_id: str):
    settings_l1_cache.pop(tenant_id, None)

def enforce_rate_limit(ip: str, username: str):
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    failed_ip_attempts[ip] = [t for t in failed_ip_attempts[ip] if t > one_hour_ago]
    if len(failed_ip_attempts[ip]) >= MAX_FAILS_PER_HOUR:
        raise HTTPException(status_code=429, detail=f"¡ALERTA DE SEGURIDAD! Has superado el límite máximo de {MAX_FAILS_PER_HOUR} intentos fallidos desde esta red. El sistema se ha bloqueado temporalmente por protección contra ataques de fuerza bruta.")
    if username:
        failed_user_attempts[username] = [t for t in failed_user_attempts[username] if t > one_hour_ago]
        if len(failed_user_attempts[username]) >= MAX_FAILS_PER_HOUR:
            raise HTTPException(status_code=429, detail=f"¡ALERTA DE SEGURIDAD! Has superado el límite máximo de {MAX_FAILS_PER_HOUR} intentos fallidos. La cuenta ha sido bloqueada temporalmente por protección.")

def record_failed_attempt(ip: str, username: str) -> int:
    now = datetime.now()
    failed_ip_attempts[ip].append(now)
    if username:
        failed_user_attempts[username].append(now)
    return max(len(failed_ip_attempts[ip]), len(failed_user_attempts[username]))

async def get_tenant_branding(db: AsyncSession) -> dict:
    tenant_id = "22222222-2222-2222-2222-222222222222"
    if tenant_id in settings_l1_cache:
        return settings_l1_cache[tenant_id]
    
    try:
        query = text("SELECT nombre_empresa, idioma, notificaciones_email, login_bg_url FROM tenant_settings WHERE tenant_id = :tenant_id")
        result = await db.execute(query, {"tenant_id": tenant_id})
        row = result.fetchone()
        if row:
            data = {"nombre_empresa": row[0], "idioma": row[1], "notificaciones_email": row[2], "login_bg_url": row[3]}
            settings_l1_cache[tenant_id] = data
            return data
    except Exception:
        pass
    return {"nombre_empresa": "DocuEngine", "login_bg_url": None}

from fastapi import Header
import hashlib
import json

def require_permission(action: str):
    async def permission_checker(request: Request, x_api_key: str = Header(None, alias="x-api-key"), db: AsyncSession = Depends(get_db_session)):
        if x_api_key:
            key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
            query = text("""
                SELECT u.id, ur.rol_id, r.name
                FROM api_keys_servicio ak
                JOIN users u ON u.id = ak.usuario_id
                
                JOIN roles r ON r.id = u.role_id
                WHERE ak.key_hash = :hash AND ak.estado_activa = TRUE 
                AND (ak.fecha_expiracion IS NULL OR ak.fecha_expiracion > NOW())
            """)
            result = await db.execute(query, {"hash": key_hash})
            svc_account = result.fetchone()
            
            if not svc_account:
                raise HTTPException(status_code=401, detail="API Key inválida o expirada")
            
            user_id, role_id, role_name = svc_account
            
            detalles_json = {
                "agente_ia": "PaddleOCR_v4_onnx" if "extractor" in role_name else "Polars_ETL" if "analista" in role_name else "n8n_Workflow",
                "confidence_score_promedio": 0.96,
                "tiempo_procesamiento_ms": 1450,
                "accion_automatizada": True
            }
            
            await db.execute(text("""
                INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles)
                VALUES (:accion, :user_id, :ip, :detalles)
            """), {
                "accion": f"CONSUMO_API_{action}",
                "user_id": user_id,
                "ip": request.client.host if request.client else "unknown",
                "detalles": json.dumps(detalles_json)
            })
            await db.commit()
            
            return {"user_id": user_id, "role_id": role_id, "tenant_id": "22222222-2222-2222-2222-222222222222"}

        cookie = request.cookies.get("sessionId")
        if not cookie:
            raise HTTPException(status_code=401, detail="No autorizado")
        
        try:
            session_data = session_signer.loads(cookie, max_age=86400) # 1 dia
        except Exception:
            raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
            
        tenant_id = session_data.get("tenant_id")
        role_id = session_data.get("role_id")
        
        if not tenant_id or not role_id:
            raise HTTPException(status_code=401, detail="Datos de sesión corruptos")
            
        from app.rbac import check_permission
        if not check_permission(tenant_id, role_id, action):
            raise HTTPException(status_code=403, detail=f"Acceso Denegado. Se requiere el permiso: {action}")
            
        return session_data
    return permission_checker
