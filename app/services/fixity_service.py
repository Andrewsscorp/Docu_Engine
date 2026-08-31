import hashlib
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.notifications import log_audit_sgdea_async
from datetime import datetime

class FixityService:
    @staticmethod
    async def run_fixity_check(tenant_id: str, db: AsyncSession, admin_user_id: str = "system"):
        """
        Recorre todos los documentos del tenant, recalcula su SHA-256 leyendo el disco,
        y lo compara contra el `file_hash` almacenado en la BD para detectar corrupción.
        """
        # Fetch all documents that have a file_path and file_hash
        docs_res = await db.execute(text("""
            SELECT id, file_path, file_hash, file_name, agn_expediente_id 
            FROM documents 
            WHERE tenant_id = :t AND file_path IS NOT NULL AND status != 'DELETED'
        """), {"t": tenant_id})
        docs = docs_res.fetchall()
        
        corrupted = 0
        missing = 0
        verified = 0
        
        for doc in docs:
            full_path = os.path.join("uploads", str(tenant_id), doc.file_path).replace("\\", "/")
            if not os.path.exists(full_path):
                missing += 1
                # Log audit event for missing physical file (Silent data loss)
                await log_audit_sgdea_async(
                    expediente_id=str(doc.agn_expediente_id) if doc.agn_expediente_id else "00000000-0000-0000-0000-000000000000",
                    usuario_id=admin_user_id,
                    accion="FIXITY_ERROR_MISSING",
                    ip_origen="127.0.0.1",
                    detalles={"doc_id": str(doc.id), "file_name": doc.file_name, "expected_hash": doc.file_hash}
                )
                continue
            
            # Recalculate hash (streaming to avoid memory overload)
            sha256 = hashlib.sha256()
            try:
                with open(full_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                
                real_hash = sha256.hexdigest()
                
                if real_hash != doc.file_hash:
                    corrupted += 1
                    # Log audit event for corrupted file (bit rot or tampering)
                    await log_audit_sgdea_async(
                        expediente_id=str(doc.agn_expediente_id) if doc.agn_expediente_id else "00000000-0000-0000-0000-000000000000",
                        usuario_id=admin_user_id,
                        accion="FIXITY_ERROR_CORRUPTED",
                        ip_origen="127.0.0.1",
                        detalles={"doc_id": str(doc.id), "file_name": doc.file_name, "expected_hash": doc.file_hash, "actual_hash": real_hash}
                    )
                else:
                    verified += 1
            except Exception as e:
                missing += 1 # Read error treated as missing/corrupted
                
        # Register the fixity check run itself
        await log_audit_sgdea_async(
            expediente_id="00000000-0000-0000-0000-000000000000",
            usuario_id=admin_user_id,
            accion="FIXITY_CHECK_COMPLETED",
            ip_origen="127.0.0.1",
            detalles={"verified": verified, "corrupted": corrupted, "missing": missing, "total": len(docs)}
        )
        
        return {"verified": verified, "corrupted": corrupted, "missing": missing, "total": len(docs)}
