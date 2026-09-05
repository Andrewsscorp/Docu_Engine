from fastapi import HTTPException
from app.repositories.agn_repository import AGNRepository
import os
import uuid

class AGNService:
    def __init__(self, repo: AGNRepository):
        self.repo = repo

    async def crear_fondo(self, codigo, nombre, acto_administrativo, archivo_acto, estado, user_id, ip_address):
        # 1. Validación de negocio
        if await self.repo.check_codigo_fondo_exists(codigo):
            raise HTTPException(status_code=400, detail=f"El código '{codigo}' ya existe.")
        
        # 2. Manejo de archivos (StorageService)
        archivo_url = None
        if archivo_acto and archivo_acto.filename:
            # We save it to a safe path in production, but here we just emulate the storage
            file_ext = os.path.splitext(archivo_acto.filename)[1]
            safe_name = f"{uuid.uuid4().hex}{file_ext}"
            archivo_url = f"/uploads/{safe_name}"
            # You would save the physical file here!
            # content = await archivo_acto.read()
            # with open(safe_name, "wb") as f: f.write(content)
        
        # 3. Persistencia
        new_id = await self.repo.create_fondo(codigo, nombre, acto_administrativo, archivo_url, estado)
        
        # 4. Auditoría
        await self.repo.log_audit("CREAR_FONDO_AGN", user_id, ip_address, new_id)
        
        return new_id
