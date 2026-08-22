from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db_session
from app.security import session_signer
import jwt
import os
import json
import hashlib
import uuid
import httpx
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from app.rbac import get_role_hierarchy, check_permission, log_audit_action
import urllib.parse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

COLLABORA_SECRET = "docuengine_super_secret_jwt_collabora_key"

@router.get("/api/v1/documentos/{doc_id}/interfaz-editor")
async def generar_vista_editor_htmx(doc_id: str, request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        cookie = request.cookies.get("sessionId")
        if not cookie: return HTMLResponse("No autorizado", status_code=401)
        try: session_data = session_signer.loads(cookie, max_age=86400)
        except: return HTMLResponse("Sesión inválida", status_code=401)
        
        tenant_id = session_data.get("tenant_id")
        user_id = session_data.get("user_id")
        role_id = session_data.get("role_id")
        username = session_data.get("username", "Auditor")
        
        if not check_permission(tenant_id, role_id, "documentos:editar"):
            return HTMLResponse("<div class='p-4 text-red-500'>No tienes permisos para editar documentos.</div>", status_code=403)
            
        query = text('''
            SELECT d.id, d.file_name, d.group_id, v.version_number
            FROM documents d
            LEFT JOIN document_versions v ON d.id = v.document_id
            WHERE d.id = :id AND d.tenant_id = :t
            ORDER BY v.version_number DESC LIMIT 1
        ''')
        res = await db.execute(query, {"id": doc_id, "t": tenant_id})
        doc = res.fetchone()
        if not doc:
            return HTMLResponse("Documento no encontrado", status_code=404)
        
        # Construimos el Access Token para el WOPI Host de Collabora
        payload = {
            "tenant_id": str(tenant_id),
            "user_id": str(user_id),
            "username": username,
            "version": doc.version_number or 1,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        token = jwt.encode(payload, COLLABORA_SECRET, algorithm="HS256")
        
        # El WOPISrc es la URL absoluta donde Collabora nos pedirá el archivo
        host_ip = "host.docker.internal:8555" 
        wopi_src = f"http://{host_ip}/wopi/files/{doc_id}"
        wopi_src_encoded = urllib.parse.quote(wopi_src)
        
        # En la Versión 24.04+ de Collabora (CODE), la ruta correcta es cool.html
        import time
        collabora_url = f"http://localhost:9980/browser/dist/cool.html?WOPISrc={wopi_src_encoded}&v={int(time.time())}"
        
        return templates.TemplateResponse(request=request, name="components/editor_modal.html", context={
            "request": request,
            "collabora_url": collabora_url,
            "access_token": token,
            "doc_id": doc_id,
            "file_name": doc.file_name
        })
    except Exception as e:
        import traceback
        return HTMLResponse(f"<div class='fixed inset-0 z-[150] flex items-center justify-center bg-black/50'><div class='bg-white p-6 rounded-xl max-w-2xl max-h-screen overflow-auto'><h3 class='text-red-600 font-bold mb-4'>Error Interno</h3><pre class='text-xs text-gray-800 whitespace-pre-wrap'>{traceback.format_exc()}</pre><button onclick='this.parentElement.parentElement.remove()' class='mt-4 px-4 py-2 bg-gray-200 rounded'>Cerrar</button></div></div>", status_code=200)

# =========================================================
# PROTOCOLO WOPI (Web Application Open Platform Interface)
# =========================================================

@router.get("/wopi/files/{doc_id}")
async def wopi_check_file_info(doc_id: str, access_token: str, db: AsyncSession = Depends(get_db_session)):
    """WOPI CheckFileInfo: Collabora pregunta sobre las capacidades y metadata del documento"""
    try:
        try:
            payload = jwt.decode(access_token, COLLABORA_SECRET, algorithms=["HS256"])
        except:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
            
        await db.execute(text("SELECT set_config('app.current_tenant', :t, false)"), {"t": payload["tenant_id"]})
        await db.execute(text("SELECT set_config('app.current_user_id', :u, false)"), {"u": payload["user_id"]})
        # Si es Admin, lo tratamos como superadmin temporal para la visualización del documento
        is_super = 'true' if payload.get("username") == "Admin" else 'false'
        await db.execute(text("SELECT set_config('app.is_superadmin', :s, false)"), {"s": is_super})
        
        query = text("SELECT file_name, file_size_bytes FROM documents WHERE id = :id")
        res = await db.execute(query, {"id": doc_id})
        doc = res.fetchone()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado o sin permisos")
            
        # Get latest version and size
        query_v = text("SELECT version_number, file_size_bytes FROM document_versions WHERE document_id = :id ORDER BY version_number DESC LIMIT 1")
        res_v = await db.execute(query_v, {"id": doc_id})
        latest_v = res_v.fetchone()
        
        current_version = str(latest_v[0]) if latest_v else "1"
        current_size = latest_v[1] if latest_v else doc.file_size_bytes
        
        return JSONResponse({
            "BaseFileName": doc.file_name,
            "OwnerId": payload["user_id"],
            "Size": current_size if current_size is not None else 1000,
            "UserId": payload["user_id"],
            "UserFriendlyName": payload.get("username", "Auditor"),
            "Version": current_version,
            "UserCanWrite": True,
            "DisablePrint": False,
            "DisableExport": False
        })
    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/wopi/files/{doc_id}/contents")
async def wopi_get_file_contents(doc_id: str, access_token: str, db: AsyncSession = Depends(get_db_session)):
    """WOPI GetFile: Collabora descarga los bytes reales del archivo para renderizarlos"""
    try:
        payload = jwt.decode(access_token, COLLABORA_SECRET, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401)
        
    await db.execute(text("SELECT set_config('app.current_tenant', :t, false)"), {"t": payload["tenant_id"]})
    await db.execute(text("SELECT set_config('app.current_user_id', :u, false)"), {"u": payload["user_id"]})
    is_super = 'true' if payload.get("username") == "Admin" else 'false'
    await db.execute(text("SELECT set_config('app.is_superadmin', :s, false)"), {"s": is_super})
    
    # Intenta obtener de document_versions
    query = text("SELECT file_path FROM document_versions WHERE document_id = :id ORDER BY version_number DESC LIMIT 1")
    res = await db.execute(query, {"id": doc_id})
    row = res.fetchone()
    
    file_path = None
    if row:
        file_path = row[0]
    else:
        # Fallback a documents.file_path si es la version inicial y no hay versiones
        query_fallback = text("SELECT file_path FROM documents WHERE id = :id")
        res_fallback = await db.execute(query_fallback, {"id": doc_id})
        row_fallback = res_fallback.fetchone()
        if row_fallback:
            file_path = row_fallback[0]
            
    print(f"WOPI GETFILE FALLBACK RESOLVED PATH: {file_path}")
            
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404)
        
    return FileResponse(file_path)

@router.post("/wopi/files/{doc_id}/contents")
async def wopi_put_file_contents(doc_id: str, request: Request, access_token: str, db: AsyncSession = Depends(get_db_session)):
    """WOPI PutFile: Guarda una nueva version en la base de datos sin alterar la original"""
    import jwt
    import hashlib
    import os
    
    print(f"================ WOPI PUTFILE HIT! doc_id={doc_id}")
    
    try:
        payload = jwt.decode(access_token, COLLABORA_SECRET, algorithms=["HS256"])
    except Exception as e:
        print(f"WOPI PUTFILE JWT ERROR: {e}")
        raise HTTPException(status_code=401)
        
    try:
        tenant_id = payload["tenant_id"]
        user_id = payload["user_id"]
        
        await db.execute(text("SELECT set_config('app.current_tenant', :t, false)"), {"t": payload["tenant_id"]})
        await db.execute(text("SELECT set_config('app.current_user_id', :u, false)"), {"u": payload["user_id"]})
        is_super = 'true' if payload.get("username") == "Admin" else 'false'
        await db.execute(text("SELECT set_config('app.is_superadmin', :s, false)"), {"s": is_super})
        
        # 1. Leer los bytes del nuevo archivo desde el Request
        content_bytes = await request.body()
        file_size = len(content_bytes)
        file_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # 2. Obtener la extension original y crear el path
        query_ext = text("SELECT file_name FROM documents WHERE id = :id AND tenant_id = :t")
        res_ext = await db.execute(query_ext, {"id": doc_id, "t": tenant_id})
        row_ext = res_ext.fetchone()
        if not row_ext:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
            
        original_name = row_ext[0]
        _, ext = os.path.splitext(original_name)
        
        # 3. Determinar el numero de version (max + 1)
        query_v = text("SELECT COALESCE(MAX(version_number), 1) FROM document_versions WHERE document_id = :id")
        res_v = await db.execute(query_v, {"id": doc_id})
        current_v = res_v.fetchone()[0]
        new_v = current_v + 1
        
        # 4. Guardar fisicamente el archivo
        upload_dir = os.path.join("uploads", tenant_id)
        os.makedirs(upload_dir, exist_ok=True)
        new_file_path = os.path.join(upload_dir, f"{doc_id}_v{new_v}{ext}")
        
        with open(new_file_path, "wb") as f:
            f.write(content_bytes)
            
        # 5. Insertar el registro de la version
        query_ins = text("""
            INSERT INTO document_versions (document_id, version_number, file_path, file_hash, file_size_bytes, edited_by)
            VALUES (:doc_id, :v, :path, :hash, :size, :uid)
        """)
        await db.execute(query_ins, {
            "doc_id": doc_id,
            "v": new_v,
            "path": new_file_path,
            "hash": file_hash,
            "size": file_size,
            "uid": user_id
        })
        await db.commit()
        
        print(f"WOPI PUTFILE SUCCESS! doc_id={doc_id} saved version {new_v}")
        return JSONResponse({"status": "success"})
        
    except Exception as e:
        await db.rollback()
        print(f"WOPI PUTFILE CRASHED: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
