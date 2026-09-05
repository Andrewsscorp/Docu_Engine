from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

class AGNRepository:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def check_codigo_fondo_exists(self, codigo: str) -> bool:
        check_q = text("SELECT id FROM agn_dependencias WHERE tenant_id = :t AND codigo = :c AND parent_id IS NULL")
        res = await self.db.execute(check_q, {"t": self.tenant_id, "c": codigo})
        return res.fetchone() is not None

    async def create_fondo(self, codigo: str, nombre: str, acto: str, archivo_url: Optional[str], estado: str) -> str:
        insert_q = text("""
            INSERT INTO agn_dependencias (tenant_id, codigo, nombre, tipo, acto_administrativo, archivo_acto_url, estado)
            VALUES (:t, :c, :n, 'FONDO', :a, :url, :e) RETURNING id
        """)
        res = await self.db.execute(insert_q, {
            "t": self.tenant_id, "c": codigo, "n": nombre, "a": acto, "url": archivo_url, "e": estado
        })
        return str(res.scalar())
        
    async def log_audit(self, action: str, user_id: str, ip_address: str, entity_id: str):
        query = text("""
            INSERT INTO log_auditoria_sgdea (tenant_id, user_id, accion, detalle, ip_address)
            VALUES (:t, :uid, :acc, :det, :ip)
        """)
        await self.db.execute(query, {
            "t": self.tenant_id,
            "uid": user_id,
            "acc": action,
            "det": f"Creación de Fondo AGN ID: {entity_id}",
            "ip": ip_address
        })
