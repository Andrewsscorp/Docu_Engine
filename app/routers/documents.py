from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile, File
from fastapi import APIRouter, Request, Response, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.database import get_db_session

import os
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timezone, timedelta
from fastapi_csrf_protect import CsrfProtect
from fastapi.templating import Jinja2Templates

# Security dependencies (we must import the globals/functions from app.main or app.security)
# Since we didn't split security completely, we'll import them from app.main!
from app.security import session_signer, require_permission, get_tenant_branding, enforce_rate_limit, record_failed_attempt
from app.security import MAX_FAILS_PER_HOUR, DUMMY_HASH, ph, MASTER_HMAC_KEY, DB_CRYPT_KEY
from app import rbac
from app.rbac import check_permission, get_role_hierarchy, log_audit_action

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

async def generate_carousel_html(db, tenant_id, q=""):
    query_str = """
        SELECT id, file_name, thumbnail_path, created_at, mime_type, status, ocr_progress_percent, file_size_bytes 
        FROM documents 
        WHERE tenant_id = :t 
    """
    params = {"t": tenant_id}
    if q and len(q) >= 3:
        query_str += " AND (file_name ILIKE :q OR extracted_text ILIKE :q OR file_hash ILIKE :q) "
        params["q"] = f"%{q}%"
        
    query_str += " ORDER BY created_at DESC LIMIT 10"
    
    from sqlalchemy import text
    result = await db.execute(text(query_str), params)
    docs = result.fetchall()
    
    if not docs:
        return "<div class='text-gray-400 p-8 text-center font-medium bg-gray-50 border border-dashed border-gray-200 rounded-2xl w-full'>No hay documentos coincidentes.</div>"
        
    html_parts = []
    
    import math
    def format_size(size_bytes):
        if not size_bytes: return "0 KB"
        size_bytes = float(size_bytes)
        if size_bytes == 0: return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 1)
        if s.is_integer(): s = int(s)
        return f"{s} {size_name[i]}"
        
    for doc in docs:
        doc_id, fn, thumb, created_at, mime, status, progress, size_bytes = doc
        if progress is None: progress = 0
        
        # Determine visual style
        tag_bg = "bg-blue-500"
        tag_text = "DOC"
        if mime:
            if "pdf" in mime: tag_bg = "bg-red-500"; tag_text = "PDF"
            elif "word" in mime: tag_bg = "bg-blue-500"; tag_text = "DOCX"
            elif "excel" in mime or "spreadsheet" in mime: tag_bg = "bg-green-500"; tag_text = "XLSX"
            elif "image" in mime: tag_bg = "bg-orange-500"; tag_text = "PNG"
            
        date_str = created_at.strftime("%d %b, %H:%M") if created_at else "Reciente"
        size_str = format_size(size_bytes)
        
        thumb_url = thumb if thumb else "https://ui-avatars.com/api/?name=DOC&background=718096&color=fff&rounded=true&font-size=0.3"
        if not thumb:
            # Fallbacks if no thumbnail
            if "pdf" in (mime or ""): thumb_url = "https://ui-avatars.com/api/?name=PDF&background=E53E3E&color=fff&rounded=true&font-size=0.3"
            else: thumb_url = "https://ui-avatars.com/api/?name=DOC&background=3182CE&color=fff&rounded=true&font-size=0.3"
            
        status_badge = ""
        if status == "PENDING":
            status_badge = "<div class='absolute inset-0 bg-white/60 backdrop-blur-[2px] flex items-center justify-center'><span class='bg-yellow-100 text-yellow-800 text-xs font-bold px-3 py-1 rounded-full shadow-sm'>En Cola</span></div>"
        elif status == "EXTRACTING":
            status_badge = f"<div class='absolute inset-0 bg-white/60 backdrop-blur-[2px] flex items-center justify-center'><span class='bg-blue-100 text-blue-800 text-xs font-bold px-3 py-1 rounded-full shadow-sm animate-pulse'>OCR: {progress}%</span></div>"
        elif status == "ERROR":
            status_badge = "<div class='absolute inset-0 bg-white/60 backdrop-blur-[2px] flex items-center justify-center'><span class='bg-red-100 text-red-800 text-xs font-bold px-3 py-1 rounded-full shadow-sm'>Error</span></div>"
            
        card = f"""
        <div class="bg-white rounded-3xl w-64 shrink-0 shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300  cursor-pointer overflow-hidden group" hx-get="/api/v1/documents/{doc_id}/details" hx-trigger="click" hx-target="#modal-container" @click="if(dragged) {{ $event.preventDefault(); $event.stopPropagation(); }}">
            <div class="h-40 w-full bg-gray-50 relative overflow-hidden flex items-center justify-center p-4">
                <img src="{thumb_url}" class="max-h-full max-w-full object-contain drop-shadow-md group-hover:scale-110 transition-transform duration-500" alt="thumbnail" onerror="this.style.display='none'">
                {status_badge}
                <div class="absolute bottom-3 left-3 {tag_bg} text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm">
                    {tag_text}
                </div>
            </div>
            <div class="p-4 relative">
                <h3 class="font-bold text-textmain text-sm mb-2 truncate" title="{fn}">{fn}</h3>
                <div class="flex items-center justify-between mt-1">
                    <div class="flex items-center text-textmuted text-[11px] font-medium gap-1">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        {date_str}
                    </div>
                </div>
                <div class="mt-3 inline-block bg-gray-100 text-gray-500 text-[10px] font-bold px-2 py-1 rounded">
                    {size_str}
                </div>
                <button class="absolute bottom-4 right-4 text-gray-400 hover:text-primary transition-colors">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path></svg>
                </button>
            </div>
        </div>
        """
        html_parts.append(card)
        
    return "".join(html_parts)



















from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.responses import HTMLResponse


@router.post("/api/v1/documents/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    file_hash: str = Form(...),
    group_id: str = Form(None),
    session_data: dict = Depends(require_permission("documentos:subir")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    
    from app import rbac
    hierarchy = rbac.get_role_hierarchy(tenant_id, session_data["role_id"])
    
    # Valida pertenencia al grupo (Zero Trust)
    if hierarchy != 99:
        user_groups = rbac.get_user_groups(tenant_id, user_id)
        if group_id and group_id not in user_groups:
            raise HTTPException(status_code=403, detail="No perteneces al grupo destino.")
    
    if not group_id:
        # Fallback a General
        query_fallback = text("SELECT id FROM groups WHERE tenant_id = :t AND name = 'General' LIMIT 1")
        res = await db.execute(query_fallback, {"t": tenant_id})
        row = res.fetchone()
        group_id = str(row[0]) if row else None
    
    # Create upload directory securely
    upload_dir = os.path.join("uploads", str(tenant_id))
    thumb_dir = os.path.join(upload_dir, "thumbnails")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)
    try:
        os.chmod(upload_dir, 0o700) # Ensure restrictive permissions
    except:
        pass # Ignore on Windows if not supported
        
    file_path = os.path.join(upload_dir, f"{file_hash}_{file.filename}")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # 1. Smart Routing Classification & Thumbnail Generation
    mime = file.content_type
    fast_route_text = None
    final_status = "PENDING"
    thumbnail_path = None
    
    thumb_filename = f"thumb_{file_hash}.webp"
    thumb_full_path = os.path.join(thumb_dir, thumb_filename)
    thumb_rel_path = f"/api/v1/documents/thumbnail/{tenant_id}/{thumb_filename}"
    
    # Fast route for DOCX
    if mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            fast_route_text = "\n".join([para.text for para in doc.paragraphs])
            final_status = "COMPLETED"
            thumbnail_path = None # Usa el ícono genérico en frontend
        except Exception as e:
            print(f"Error fast-routing DOCX: {e}")
            final_status = "FAILED"
            
    # Fast route for Native PDF & Thumbnail
    elif mime == "application/pdf":
        try:
            import fitz # PyMuPDF
            pdf_doc = fitz.open(stream=content, filetype="pdf")
            
            # Generate thumbnail from page 0
            if len(pdf_doc) > 0:
                page = pdf_doc.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) # Scale down
                from PIL import Image
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                if mode == "RGBA":
                    # Convert to RGB by adding a white background
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                img.thumbnail((300, 400))
                img.save(thumb_full_path, "WEBP", quality=70)
                thumbnail_path = thumb_rel_path
                
            text_blocks = []
            for page in pdf_doc:
                text_blocks.append(page.get_text())
            pdf_text = "\n".join(text_blocks).strip()
            fast_route_text = pdf_text
            
            # Calcular caracteres promedio por pagina
            total_pages = len(pdf_doc)
            avg_chars_per_page = len(pdf_text) / total_pages if total_pages > 0 else 0
            
            # Si el documento tiene mas de 600 caracteres en promedio por pagina,
            # asumimos que es un PDF nativo. Si tiene menos, probablemente es
            # un documento escaneado que solo tiene sellos o marcas de agua nativas.
            if avg_chars_per_page > 600:
                final_status = "COMPLETED"
            else:
                final_status = "PENDING"
        except Exception as e:
            print(f"Error PDF routing/thumbnail: {e}")
            final_status = "PENDING"
            
    # Image Thumbnail
    elif mime in ["image/jpeg", "image/png", "image/webp"]:
        final_status = "PENDING"
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(content))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((300, 400))
            img.save(thumb_full_path, "WEBP", quality=70)
            thumbnail_path = thumb_rel_path
        except Exception as e:
            print(f"Error image thumbnail: {e}")
        
    # 2. Database Insertion (Checking Uniqueness via Constraint)
    try:
        query = text('''
            INSERT INTO documents (tenant_id, group_id, file_name, mime_type, file_size_bytes, file_hash, status, extracted_text, ocr_confidence_score, file_path, thumbnail_path, uploaded_by)
            VALUES (:t, :gid, :fn, :mime, :size, :hash, :status, :text, :score, :path, :thumb, :uid)
            RETURNING id
        ''')
        result = await db.execute(query, {
            "t": tenant_id,
            "gid": group_id,
            "fn": file.filename,
            "mime": mime,
            "size": file_size,
            "hash": file_hash,
            "status": final_status,
            "text": fast_route_text,
            "score": 1.0 if final_status == "COMPLETED" else None,
            "path": file_path,
            "thumb": thumbnail_path,
            "uid": user_id
        })
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return JSONResponse({"error": "Archivo ya procesado (Duplicate Hash)"}, status_code=409)
    except Exception as e:
        await db.rollback()
        import traceback
        tb = traceback.format_exc()
        with open("upload_crash.log", "w", encoding="utf-8") as lf:
            lf.write(tb)
        return JSONResponse({"error": str(e), "traceback": tb}, status_code=500)
        
    # Save the file physically only if DB insert succeeded
    with open(file_path, "wb") as out_file:
        out_file.write(content)
        
    return JSONResponse({"status": "success", "file_status": final_status})

@router.get("/api/v1/documents/thumbnail/{tenant_id}/{filename}")
async def get_thumbnail(
    request: Request,
    tenant_id: str,
    filename: str,
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie:
        return Response(status_code=401)
    try:
        session_data = session_signer.loads(cookie, max_age=86400)
    except Exception:
        return Response(status_code=401)
        
    if session_data.get("tenant_id") != tenant_id:
        return Response(status_code=403)
        
    file_path = os.path.join("uploads", tenant_id, "thumbnails", filename)
    if not os.path.exists(file_path):
        return Response(status_code=404)
        
    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type="image/webp")

@router.get("/api/v1/documents/recent", response_class=HTMLResponse)
async def get_recent_documents(
    request: Request,
    limit: int = 5,
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("No autorizado", status_code=401)
    try: session_data = session_signer.loads(cookie, max_age=86400)
    except: return HTMLResponse("Sesin invalida", status_code=401)
        
    tenant_id = session_data.get("tenant_id")
    html = await generate_carousel_html(db, tenant_id, "")
    return HTMLResponse(html)

@router.get("/api/v1/documents/search", response_class=HTMLResponse)
async def search_documents(
    request: Request,
    q: str = "",
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("")
    try: session_data = session_signer.loads(cookie, max_age=86400)
    except: return HTMLResponse("")
    tenant_id = session_data.get("tenant_id")
    
    if not q or len(q) < 3:
        carousel = await generate_carousel_html(db, tenant_id, "")
        return HTMLResponse(carousel)
        
    from sqlalchemy import text
    query = text('''
        SELECT id, file_name, status, created_at
        FROM documents 
        WHERE tenant_id = :t 
          AND (file_name ILIKE :q OR extracted_text ILIKE :q OR file_hash ILIKE :q)
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    result = await db.execute(query, {"t": tenant_id, "q": f"%{q}%"})
    docs = result.fetchall()
    
    dropdown_html = ""
    if not docs:
        dropdown_html = "<div class='p-4 text-center text-gray-500 font-medium'>No se encontraron documentos que coincidan con la búsqueda.</div>"
    else:
        html = "<ul class='divide-y divide-gray-100 max-h-96 overflow-y-auto custom-scrollbar'>"
        for doc in docs:
            doc_id, fn, status, created_at = doc
            html += f'''
            <li class="p-4 hover:bg-gray-50 cursor-pointer transition-colors flex items-center justify-between group" hx-get="/api/v1/documents/{doc_id}/details" hx-trigger="click" hx-target="#modal-container" @click="if(dragged) {{ $event.preventDefault(); $event.stopPropagation(); }}">
                <div class="flex items-center gap-3">
                    <span class="text-2xl opacity-80 group-hover:opacity-100 transition-opacity">📄</span>
                    <div>
                        <p class="font-bold text-sm text-textmain truncate max-w-md">{fn}</p>
                        <p class="text-xs text-textmuted">{created_at.strftime("%d %b, %H:%M")} &bull; <span class="uppercase tracking-wider">{status}</span></p>
                    </div>
                </div>
                <button class="px-4 py-2 bg-primary/10 text-primary rounded-lg text-sm font-semibold hover:bg-primary hover:text-white transition-colors shadow-sm">Ver Detalles</button>
            </li>
            '''
        html += "</ul>"
        dropdown_html = html

    carousel = await generate_carousel_html(db, tenant_id, q)
    return HTMLResponse(dropdown_html + carousel)

@router.get("/api/v1/documents/{doc_id}/details", response_class=HTMLResponse)
async def get_document_details(
    doc_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("No autorizado", status_code=401)
    
    from sqlalchemy import text
    query = text('''
        SELECT d.id, d.file_name, d.status, d.created_at, d.updated_at, d.file_size_bytes, d.extracted_text, d.ocr_confidence_score, d.mime_type, u.username as uploader_name
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        WHERE d.id = :id
    ''')
    result = await db.execute(query, {"id": doc_id})
    doc = result.fetchone()
    if not doc: return HTMLResponse("")
    
    exec_time = "N/A"
    if doc.status == "COMPLETED" and doc.updated_at and doc.created_at:
        diff = (doc.updated_at - doc.created_at).total_seconds()
        exec_time = f"{diff:.1f} seg"
        
    char_count = len(doc.extracted_text) if doc.extracted_text else 0
    confidence = f"{doc.ocr_confidence_score * 100:.1f}%" if doc.ocr_confidence_score else "N/A"
    
    preview_text = doc.extracted_text[:1500] + "..." if doc.extracted_text and len(doc.extracted_text) > 1500 else (doc.extracted_text or "Sin texto extraído aún.")
    
    html = f'''
    <div x-data="{{ show: true }}" x-show="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-gray-900/40 backdrop-blur-sm" x-transition.opacity>
        <div @click.away="show = false" class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col" x-transition>
            
            <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-white z-10 shrink-0">
                <div class="flex items-center gap-4">
                    <div class="p-3 bg-primary/10 rounded-xl text-primary">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    </div>
                    <div>
                        <h2 class="text-xl font-bold text-textmain truncate max-w-md">{doc.file_name}</h2>
                        <p class="text-sm text-textmuted">ID: {doc.id}</p>
                    </div>
                </div>
                <button @click="show = false" class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
            </div>
            
            <div class="p-6 overflow-y-auto flex-1 space-y-6">
                <!-- Info Cards -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div class="bg-blue-50/50 p-4 rounded-xl border border-blue-100">
                        <p class="text-[10px] text-blue-500 font-bold uppercase tracking-widest mb-1">Estado</p>
                        <p class="font-bold text-blue-900">{doc.status}</p>
                    </div>
                    <div class="bg-gray-50 p-4 rounded-xl border border-gray-200">
                        <p class="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1">Subido el</p>
                        <p class="font-bold text-gray-900">{doc.created_at.strftime("%d %b, %H:%M")}</p>
                    </div>
                    <div class="bg-green-50/50 p-4 rounded-xl border border-green-100">
                        <p class="text-[10px] text-green-600 font-bold uppercase tracking-widest mb-1">Tiempo OCR</p>
                        <p class="font-bold text-green-900">{exec_time}</p>
                    </div>
                    <div class="bg-purple-50/50 p-4 rounded-xl border border-purple-100">
                        <p class="text-[10px] text-purple-600 font-bold uppercase tracking-widest mb-1">Caracteres</p>
                        <p class="font-bold text-purple-900">{char_count:,}</p>
                    </div>
                </div>
                
                <div class="flex flex-col sm:flex-row gap-4">
                    <div class="flex items-center gap-3 text-sm text-gray-600 bg-gray-50 px-4 py-3 rounded-xl border border-gray-200 flex-1">
                        <div class="p-2 bg-white rounded-lg shadow-sm">
                            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                        <span>Subido por: <strong class="text-gray-900">{doc.uploader_name or 'Desconocido'}</strong></span>
                    </div>
                    
                    <div class="flex items-center gap-3 text-sm text-gray-600 bg-gray-50 px-4 py-3 rounded-xl border border-gray-200 flex-1">
                        <div class="p-2 bg-white rounded-lg shadow-sm">
                            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </div>
                        <span>Confianza OCR: <strong class="text-gray-900">{confidence}</strong></span>
                    </div>
                </div>
                
                <div>
                    <h3 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
                        <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"></path></svg>
                        Vista Previa de Texto Extraído
                    </h3>
                    <div class="bg-gray-50 p-5 rounded-xl border border-gray-200 max-h-72 overflow-y-auto text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed custom-scrollbar shadow-inner">
                        {preview_text}
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    return HTMLResponse(html)
@router.get("/api/v1/documents/{doc_id}/download")
async def download_document(
    doc_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("No autorizado", status_code=401)
    try: session_data = session_signer.loads(cookie, max_age=86400)
    except: return HTMLResponse("Sesión inválida", status_code=401)
    
    tenant_id = session_data.get("tenant_id")
    user_id = session_data.get("user_id")
    role_id = session_data.get("role_id")
    
    from app.rbac import get_role_hierarchy, get_user_groups
    hierarchy = get_role_hierarchy(tenant_id, role_id)
    
    query = text('''
        SELECT d.file_path, d.file_name, d.mime_type, d.group_id
        FROM documents d
        WHERE d.id = :id AND d.tenant_id = :t
    ''')
    result = await db.execute(query, {"id": doc_id, "t": tenant_id})
    doc = result.fetchone()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
        
    if hierarchy != 99:
        user_groups = get_user_groups(tenant_id, user_id)
        if doc.group_id not in user_groups:
            raise HTTPException(status_code=403, detail="Acceso denegado a este grupo de documentos")
            
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="El archivo físico ya no existe en el servidor")
        
    # Track download and log to audit
    try:
        from app.rbac import log_audit_action
        await log_audit_action(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            action="DOWNLOAD_DOCUMENT",
            target_id=doc_id,
            details={"file_name": doc.file_name, "client_ip": request.client.host if request.client else "unknown"}
        )
        update_query = text("UPDATE documents SET download_count = COALESCE(download_count, 0) + 1 WHERE id = :id")
        await db.execute(update_query, {"id": doc_id})
        await db.commit()
    except Exception as e:
        import traceback; traceback.print_exc()
        await db.rollback()
        
    from fastapi.responses import FileResponse
    import urllib.parse
    encoded_filename = urllib.parse.quote(doc.file_name)
    return FileResponse(
        path=doc.file_path,
        media_type=doc.mime_type,
        filename=doc.file_name,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )

@router.get("/api/v1/documents/explorer", response_class=HTMLResponse)
async def explorer_view(
    request: Request,
    q: str = "",
    sort: str = "desc",
    view: str = "grid",
    group_id: str = "",
    status: str = "",
    page: int = 1,
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("No autorizado", status_code=401)
    try: session_data = session_signer.loads(cookie, max_age=86400)
    except: return HTMLResponse("Sesi��n inv��lida", status_code=401)
    
    tenant_id = session_data.get("tenant_id")
    user_id = session_data.get("user_id")
    role_id = session_data.get("role_id")
    
    from app.rbac import get_role_hierarchy, get_user_groups, check_permission
    hierarchy = get_role_hierarchy(tenant_id, role_id)
    
    can_delete = hierarchy == 99 or check_permission(tenant_id, role_id, "documentos:eliminar")
    can_reassign = hierarchy == 99 or check_permission(tenant_id, role_id, "documentos:reasignar")
    
    # Base query for FTS
    base_query = """
        SELECT d.id, d.file_name, d.status, d.created_at, d.thumbnail_path, d.mime_type, d.file_size_bytes, g.name as group_name
        FROM documents d
        LEFT JOIN groups g ON d.group_id = g.id
        WHERE d.tenant_id = :t
    """
    params = {"t": tenant_id}
    
    # RLS logic
    if hierarchy != 99:
        user_groups = get_user_groups(tenant_id, user_id)
        if not user_groups:
            base_query += " AND 1=0" # Deny if no groups
        else:
            base_query += " AND d.group_id = ANY(:ugroups)"
            params["ugroups"] = list(user_groups)
            
    if group_id:
        if hierarchy != 99:
            if group_id not in user_groups:
                base_query += " AND 1=0" # Deny
            else:
                base_query += " AND d.group_id = :gid"
                params["gid"] = group_id
        else:
            base_query += " AND d.group_id = :gid"
            params["gid"] = group_id
            
    if status:
        base_query += " AND d.status = :status"
        params["status"] = status
        
    if q:
        base_query += " AND d.fts_vector @@ plainto_tsquery('spanish', :q)"
        params["q"] = q
        
    # Order by
    if sort == "asc":
        base_query += " ORDER BY d.created_at ASC"
    else:
        base_query += " ORDER BY d.created_at DESC"
        
    # Pagination
    limit = 20
    offset = (page - 1) * limit
    base_query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    result = await db.execute(text(base_query), params)
    docs = result.fetchall()
    
    return templates.TemplateResponse(request=request, name="components/explorer.html", context={
        "request": request,
        "docs": docs,
        "view": view,
        "page": page,
        "has_more": len(docs) == limit,
        "q": q,
        "sort": sort,
        "group_id": group_id,
        "status": status,
        "can_delete": can_delete,
        "can_reassign": can_reassign
    })


@router.get("/api/v1/documents/{doc_id}/drawer", response_class=HTMLResponse)
async def document_drawer(
    doc_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("No autorizado", status_code=401)
    try: session_data = session_signer.loads(cookie, max_age=86400)
    except: return HTMLResponse("Sesi��n inv��lida", status_code=401)
    
    tenant_id = session_data.get("tenant_id")
    user_id = session_data.get("user_id")
    role_id = session_data.get("role_id")
    
    # RLS checks
    from app.rbac import get_role_hierarchy, get_user_groups, check_permission
    hierarchy = get_role_hierarchy(tenant_id, role_id)
    
    query = text('''
        SELECT d.id, d.file_name, d.status, d.created_at, d.updated_at, 
               d.file_size_bytes, d.extracted_text, d.ocr_confidence_score, 
               d.mime_type, u.username as uploader_name, d.group_id, d.thumbnail_path, d.download_count
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        WHERE d.id = :id AND d.tenant_id = :t
    ''')
    result = await db.execute(query, {"id": doc_id, "t": tenant_id})
    doc = result.fetchone()
    if not doc: return HTMLResponse("Documento no encontrado o sin acceso", status_code=404)
    
    if hierarchy != 99:
        user_groups = get_user_groups(tenant_id, user_id)
        if doc.group_id not in user_groups:
             return HTMLResponse("Acceso denegado", status_code=403)
             
    can_edit = check_permission(tenant_id, role_id, "documentos:editar")
    
    return templates.TemplateResponse(request=request, name="components/drawer.html", context={
        "request": request,
        "doc": doc,
        "can_edit": can_edit
    })

@router.put("/api/v1/documents/{doc_id}/reassign")
async def reassign_document(
    doc_id: str,
    group_id: str = Form(...),
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    role_id = session_data["role_id"]
    
    from app.rbac import get_role_hierarchy, get_user_groups
    hierarchy = get_role_hierarchy(tenant_id, role_id)
    
    # Ensure they have access to the target group if not admin
    if hierarchy != 99:
        user_groups = get_user_groups(tenant_id, user_id)
        if group_id not in user_groups:
            raise HTTPException(status_code=403, detail="No tienes acceso al grupo destino")
            
    # Check if doc exists and they have access to current group
    query = text("SELECT group_id FROM documents WHERE id = :id AND tenant_id = :t")
    res = await db.execute(query, {"id": doc_id, "t": tenant_id})
    row = res.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
        
    if hierarchy != 99:
        user_groups = get_user_groups(tenant_id, user_id)
        if row.group_id not in user_groups:
             raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    update_q = text("UPDATE documents SET group_id = :gid WHERE id = :id AND tenant_id = :t")
    await db.execute(update_q, {"gid": group_id, "id": doc_id, "t": tenant_id})
    await db.commit()
    
    return {"status": "success"}


from sqlalchemy import text
from app.routers.documents import router
from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from app.database import get_db_session
from app.security import session_signer
import math

def format_size(size_bytes):
    if not size_bytes: return "0 B"
    size_bytes = float(size_bytes)
    if size_bytes == 0: return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)
    if s.is_integer(): s = int(s)
    return f"{s} {size_name[i]}"

@router.get('/api/v1/documents/kpis', response_class=HTMLResponse)
async def get_kpis(request: Request, db=Depends(get_db_session)):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("")
    try: session_data = session_signer.loads(cookie, max_age=86400)
    except: return HTMLResponse("")
    tenant_id = session_data.get("tenant_id")

    query = text('''
        SELECT 
            COUNT(id) as total_docs,
            SUM(CASE WHEN status = 'READY' THEN 1 ELSE 0 END) as ocr_docs,
            COALESCE(SUM(file_size_bytes), 0) as total_size
        FROM documents 
        WHERE tenant_id = :tenant_id
    ''')
    result = await db.execute(query, {"tenant_id": tenant_id})
    row = result.fetchone()
    
    total_docs = row[0] or 0
    ocr_docs = row[1] or 0
    total_size = format_size(row[2] or 0)
    
    html = f'''
        <!-- Stat 1 -->
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow">
            <div class="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-primary shrink-0">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            </div>
            <div>
                <p class="text-xs font-medium text-textmuted">Documentos</p>
                <div class="flex items-end gap-2">
                    <h4 class="text-xl font-bold text-textmain leading-none">{total_docs}</h4>
                    <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">+12%</span>
                </div>
            </div>
        </div>
        <!-- Stat 2 -->
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow">
            <div class="w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-500 shrink-0">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            </div>
            <div>
                <p class="text-xs font-medium text-textmuted">OCR Procesados</p>
                <div class="flex items-end gap-2">
                    <h4 class="text-xl font-bold text-textmain leading-none">{ocr_docs}</h4>
                    <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">+8%</span>
                </div>
            </div>
        </div>
        <!-- Stat 3 -->
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition-shadow">
            <div class="w-12 h-12 rounded-full bg-sky-50 flex items-center justify-center text-sky-500 shrink-0">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"></path></svg>
            </div>
            <div>
                <p class="text-xs font-medium text-textmuted">Almacenados</p>
                <div class="flex items-end gap-2">
                    <h4 class="text-xl font-bold text-textmain leading-none">{total_size}</h4>
                    <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-full">+5%</span>
                </div>
            </div>
        </div>
    '''
    return HTMLResponse(html)

@router.post("/{doc_id}/asignar")
async def asignar_documento(
    doc_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint de Transacción Dual:
    1. Inserta en la DB (tareas_asignaciones).
    2. Dispara evento a Novu.
    """
    # Este endpoint debería recibir un body (JSON o Form) con los detalles.
    # Como es un POST desde HTMX, probablemente sea un form.
    form_data = await request.form()
    asignado_a = form_data.get("asignado_a")
    etiqueta_accion = form_data.get("etiqueta_accion", "Revisión General")
    tiempo_respuesta = form_data.get("tiempo_respuesta_esperado")
    
    if not asignado_a or not tiempo_respuesta:
        return HTMLResponse("<div class='text-red-500'>Faltan datos requeridos</div>", status_code=400)
        
    asignado_por = getattr(request.state, "user_id", None)
    if not asignado_por:
        return HTMLResponse("No autenticado", status_code=401)
        
    # 1. DB Insert
    try:
        await db.execute(
            text("""
                INSERT INTO tareas_asignaciones 
                (id_documento, asignado_por, asignado_a, etiqueta_accion, tiempo_respuesta_esperado)
                VALUES 
                (:doc_id, :asignado_por, :asignado_a, :etiqueta_accion, :tiempo_respuesta)
            """),
            {
                "doc_id": doc_id,
                "asignado_por": asignado_por,
                "asignado_a": asignado_a,
                "etiqueta_accion": etiqueta_accion,
                "tiempo_respuesta": tiempo_respuesta
            }
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        return HTMLResponse(f"<div class='text-red-500'>Error en base de datos: {str(e)}</div>", status_code=500)
        
    # 2. Trigger Novu
    from app.services.novu_client import novu_client
    
    # Podríamos buscar el nombre del remitente y del doc, pero usaremos dummies para el MVP
    payload = {
        "remitente_nombre": "Auditor Asignador", 
        "documento_titulo": f"Documento {doc_id}",
        "etiqueta_color": "#EF4444" if "Urgente" in etiqueta_accion else "#3B82F6",
        "etiqueta_texto": etiqueta_accion,
        "fecha_limite": str(tiempo_respuesta),
        "url_accion": f"/api/v1/documentos/{doc_id}/drawer"
    }
    
    # Disparamos sin bloquear el response
    # En producción usaríamos un BackgroundTask
    import asyncio
    asyncio.create_task(
        novu_client.trigger_event("WORKFLOW_DOCUMENTO_ASIGNADO", asignado_a, payload)
    )
    
    return HTMLResponse("<div class='text-green-500 p-2 bg-green-50 rounded'>Documento asignado y notificación enviada correctamente.</div>")

import os
import uuid
import hashlib
import json
import asyncio
from werkzeug.utils import secure_filename
from fastapi import BackgroundTasks

# Mock OCR function as requested
async def iniciar_extraccion_ocr(document_id: str):
    # This simulates a background task taking time without blocking the main event loop
    await asyncio.sleep(2)
    # Here it would update the DB...
    print(f"OCR finished for {document_id}")

@router.post("/api/v1/documents/upload-initial", response_class=HTMLResponse)
async def upload_inicial_documento(
    request: Request,
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:subir"))
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    
    # 1. Sanitization: secure_filename
    safe_name = secure_filename(archivo.filename)
    # Ensure it's safe and give it a unique UUID on disk
    file_ext = os.path.splitext(safe_name)[1]
    disk_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    upload_dir = os.path.join("uploads", str(tenant_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, disk_filename)
    
    content = await archivo.read()
    file_size = len(content)
    with open(file_path, "wb") as f:
        f.write(content)
        
    # 2. Find fallback group_id since it is NOT NULL in DB
    group_id = None
    query_fallback = text("SELECT id FROM groups WHERE tenant_id = :t AND name = 'General' LIMIT 1")
    res_group = await db.execute(query_fallback, {"t": tenant_id})
    row = res_group.fetchone()
    if row:
        group_id = row.id
    else:
        # Just grab the first group available
        res_group = await db.execute(text("SELECT id FROM groups WHERE tenant_id = :t LIMIT 1"), {"t": tenant_id})
        row = res_group.fetchone()
        if row:
            group_id = row.id

    # 3. Insert into documents as DRAFT
    mime = archivo.content_type or "application/octet-stream"
    file_hash = hashlib.sha256(content).hexdigest()
    query = text("""
        INSERT INTO documents (id, tenant_id, group_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash)
        VALUES (:id, :t, :gid, :fn, :path, :uid, 'PENDING', FALSE, :mime, :size, :hash)
        RETURNING id
    """)
    doc_id = str(uuid.uuid4())
    await db.execute(query, {
        "id": doc_id,
        "t": tenant_id,
        "gid": group_id,
        "fn": safe_name,
        "path": disk_filename,
        "uid": user_id,
        "mime": mime,
        "size": file_size,
        "hash": file_hash
    })
    await db.commit()
    
    # 3. Fetch tags, users, groups for the modal
    tags_res = await db.execute(text("SELECT id_etiqueta, nombre FROM etiquetas_maestras WHERE estado_activa = TRUE ORDER BY nombre"))
    etiquetas = tags_res.all()
    
    users_res = await db.execute(text("SELECT u.id, u.username, r.name as role_name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.tenant_id = :t AND u.id != :uid"), {"t": tenant_id, "uid": user_id})
    usuarios = users_res.all()
    
    groups_res = await db.execute(text("SELECT id, name FROM groups WHERE tenant_id = :t ORDER BY name"), {"t": tenant_id})
    grupos = groups_res.all()
    
    from app.main import templates
    return templates.TemplateResponse("modals/routing_modal.html", {
        "request": request,
        "document_id": doc_id,
        "document_name": safe_name,
        "etiquetas": etiquetas,
        "usuarios": usuarios,
        "grupos": grupos
    })

@router.post("/api/v1/documents/{documento_id}/finalize-routing")
async def finalizar_enrutamiento(
    documento_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    es_privado: bool = Form(False),
    etiqueta_id: str = Form(None),
    asignado_usuario_id: str = Form(None),
    asignado_grupo_id: str = Form(None),
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:subir"))
):
    tenant_id = session_data["tenant_id"]
    current_user_id = session_data["user_id"]
    
    async with db.begin():
        # Validate rules
        if not es_privado:
            if asignado_usuario_id == current_user_id:
                raise HTTPException(status_code=400, detail="Fallo de Integridad: No puede auto-asignarse un documento de revisión.")
            if not asignado_usuario_id and not asignado_grupo_id:
                raise HTTPException(status_code=400, detail="Debe asignar el documento a un usuario o grupo.")
                
        # 2. Update Document
        estado_nuevo = "PRIVADO" if es_privado else "OCR_PENDING"
        # Since group_id exists in our schema, but we added assigned_user_id
        await db.execute(text("""
            UPDATE documents 
            SET is_private = :priv, assigned_user_id = :u_id, group_id = :g_id, status = :estado
            WHERE id = :id AND tenant_id = :t
        """), {
            "priv": es_privado, 
            "u_id": asignado_usuario_id if asignado_usuario_id else None, 
            "g_id": asignado_grupo_id if asignado_grupo_id else None, 
            "estado": estado_nuevo, 
            "id": documento_id,
            "t": tenant_id
        })
        
        # 3. Assign Tag
        if etiqueta_id:
            await db.execute(text("INSERT INTO documento_etiquetas (id_documento, id_etiqueta) VALUES (:d_id, :e_id)"), 
                            {"d_id": documento_id, "e_id": etiqueta_id})
                            
        # 4. Shadow Logging & SLA Assignment
        if not es_privado:
            await db.execute(text("""
                INSERT INTO tasks_assignments (document_id, assigned_by, assigned_to, status)
                VALUES (:d_id, :por, :para, 'PENDING')
            """), {"d_id": documento_id, "por": current_user_id, "para": asignado_usuario_id})
            
            # NOVU trigger mock...
            
        # Shadow Log
        await db.execute(text("""
            INSERT INTO audit_rbac_logs (tenant_id, user_id, action, target_resource, target_id, ip_address, user_agent, details)
            VALUES (:t, :uid, 'DOCUMENTO_INGRESADO_Y_ENRUTADO', 'documents', :d_id, '127.0.0.1', 'System', :det)
        """), {
            "t": tenant_id,
            "uid": current_user_id,
            "d_id": str(documento_id),
            "det": json.dumps({"is_private": es_privado, "assigned_to": asignado_usuario_id})
        })
        
        # 5. Background Task
        if not es_privado:
            background_tasks.add_task(iniciar_extraccion_ocr, documento_id)
            
    response = HTMLResponse(content="")
    response.headers["HX-Trigger"] = json.dumps({"toastExito": {"mensaje": "Documento cargado y enrutado exitosamente."}})
    return response

