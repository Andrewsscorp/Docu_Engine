# postgres_user_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from backend.src.domain.entities.usuario import Usuario
from backend.src.domain.interfaces.i_user_repository import IUserRepository

class PostgresUserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Optional[Usuario]:
        query = text("""
            SELECT id, username, password_hash, estado, tenant_id, mfa_secret, es_cuenta_servicio 
            FROM usuarios WHERE username = :u
        """)
        res = await self.db.execute(query, {"u": username})
        row = res.fetchone()
        if not row:
            return None
        
        return Usuario(
            id=str(row.id),
            username=row.username,
            password_hash=row.password_hash,
            estado=row.estado,
            tenant_id=row.tenant_id,
            mfa_secret=row.mfa_secret,
            es_cuenta_servicio=row.es_cuenta_servicio
        )

    async def update_last_login(self, user_id: str) -> None:
        query = text("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = :id")
        await self.db.execute(query, {"id": user_id})
