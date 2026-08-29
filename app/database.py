from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from typing import AsyncGenerator

# ==============================================================
# FASE 3: CONEXIÓN ASÍNCRONA SEGURA Y PREPARED STATEMENTS
# ==============================================================

# Usamos asyncpg (Asíncrono)
# IMPORTANTE: Nos conectamos usando el rol restringido (docuengine_api), NO como superusuario.
import os
DB_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_URL = f"postgresql+asyncpg://docuengine_api:api_secure_password_123@{DB_HOST}:5432/docuengine"

# create_async_engine previene automáticamente inyecciones SQL si se usa `text()` con :parametros
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

from fastapi import Request
async def get_db_session(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            tenant_id = "22222222-2222-2222-2222-222222222222"
            user_id = ""
            is_superadmin = False
            
            if request and hasattr(request.state, "tenant_id"):
                tenant_id = request.state.tenant_id
                user_id = getattr(request.state, "user_id", "")
                is_superadmin = getattr(request.state, "is_superadmin", False)

            if not tenant_id or str(tenant_id).strip() == "":
                tenant_id = "22222222-2222-2222-2222-222222222222"

            await session.execute(
                text("SELECT set_config('app.current_tenant', :tenant, false)"), 
                {"tenant": str(tenant_id)}
            )
            
            if user_id:
                await session.execute(
                    text("SELECT set_config('app.current_user_id', :uid, false)"), 
                    {"uid": str(user_id)}
                )
                
            await session.execute(
                text("SELECT set_config('app.is_superadmin', :is_sa, false)"), 
                {"is_sa": 'true' if is_superadmin else 'false'}
            )
            
            yield session
        finally:
            await session.close()


async def get_global_db_session():
    async with AsyncSessionLocal() as session:
        try:
            tenant_id = "22222222-2222-2222-2222-222222222222"
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tenant, false)"), 
                {"tenant": str(tenant_id)}
            )
            await session.execute(
                text("SELECT set_config('app.is_superadmin', 'true', false)")
            )
            yield session
        finally:
            await session.execute(text("SELECT set_config('app.is_superadmin', 'false', false)"))
            await session.close()
