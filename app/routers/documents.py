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
        SELECT d.id, d.file_name, d.thumbnail_path, d.created_at, d.mime_type, d.status, d.ocr_progress_percent, d.file_size_bytes,
        (SELECT json_agg(json_build_object('nombre', em.nombre, 'color_fondo', em.color_fondo, 'color_texto', em.color_texto))
         FROM documento_etiquetas de
         JOIN etiquetas_maestras em ON de.id_etiqueta = em.id_etiqueta
         WHERE de.id_documento = d.id) as tags
        FROM documents d
        WHERE d.tenant_id = :t 
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
        
    import json
    for row in docs:
        d = dict(row._mapping)
        doc_id = d['id']
        fn = d['file_name']
        thumb = d['thumbnail_path']
        created_at = d['created_at']
        mime = d['mime_type']
        status = d['status']
        progress = d['ocr_progress_percent'] or 0
        size_bytes = d['file_size_bytes']
        
        tags = d.get('tags')
        if tags and isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = []
        elif not tags:
            tags = []
        
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
            
        tag_html = ""
        if tags and len(tags) > 0:
            t = tags[0]
            tag_html = f"<div class='absolute top-2 right-2 px-2.5 py-1 rounded-md text-xs font-extrabold shadow-md backdrop-blur-md z-10 px-3 py-1.5 border border-white/20 uppercase tracking-wide {t['color_fondo']} {t['color_texto']}'>{t['nombre']}</div>"
        else:
            tag_html = status_badge
            
        card = f"""
        <div class="bg-white rounded-3xl w-64 shrink-0 shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300  cursor-pointer overflow-hidden group" hx-get="/api/v1/documents/{doc_id}/details" hx-trigger="click" hx-target="#modal-container" @click="if(dragged) {{ $event.preventDefault(); $event.stopPropagation(); }}">
            <div class="h-40 w-full bg-gray-50 relative overflow-hidden flex items-center justify-center p-4">
                <img src="{thumb_url}" class="max-h-full max-w-full object-contain drop-shadow-md group-hover:scale-110 transition-transform duration-500" alt="thumbnail" onerror="this.src='https://ui-avatars.com/api/?name=DOC&background=718096&color=fff&rounded=true&font-size=0.3'">
                {tag_html}
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
        
    file_path = os.path.join(upload_dir, f"{file_hash}_{file.filename}").replace("\\", "/")
    
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
            thumbnail_path = None # Usa el Ã­cono genÃ©rico en frontend
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
        dropdown_html = "<div class='p-4 text-center text-gray-500 font-medium'>No se encontraron documentos que coincidan con la bÃºsqueda.</div>"
    else:
        html = "<ul class='divide-y divide-gray-100 max-h-96 overflow-y-auto custom-scrollbar'>"
        for doc in docs:
            doc_id, fn, status, created_at = doc
            html += f'''
            <li class="p-4 hover:bg-gray-50 cursor-pointer transition-colors flex items-center justify-between group" hx-get="/api/v1/documents/{doc_id}/details" hx-trigger="click" hx-target="#modal-container" @click="if(dragged) {{ $event.preventDefault(); $event.stopPropagation(); }}">
                <div class="flex items-center gap-3">
                    <span class="text-2xl opacity-80 group-hover:opacity-100 transition-opacity">ðŸ“„</span>
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
    
    preview_text = doc.extracted_text[:1500] + "..." if doc.extracted_text and len(doc.extracted_text) > 1500 else (doc.extracted_text or "Sin texto extraÃ­do aÃºn.")
    
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
                        Vista Previa de Texto ExtraÃ­do
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
    except: return HTMLResponse("SesiÃ³n invÃ¡lida", status_code=401)
    
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
            # Check if user has an active/historical task for this document (assigned to them or by them)
            task_check_q = text("""
                SELECT 1 FROM tareas_asignaciones 
                WHERE id_documento = :did 
                AND (asignado_a = :uid OR asignado_por = :uid)
                LIMIT 1
            """)
            task_res = await db.execute(task_check_q, {"did": doc_id, "uid": user_id})
            if not task_res.fetchone():
                raise HTTPException(status_code=403, detail="Acceso denegado a este grupo de documentos")
            
    
        
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
    file_path = doc.file_path
    import os
    if "/" not in file_path and "\\" not in file_path:
        file_path = os.path.join("uploads", tenant_id, file_path)
        
    if not os.path.exists(file_path):
        return HTMLResponse("Archivo no encontrado en el servidor.", status_code=404)
        
    preview = request.query_params.get("preview")
    disp = "inline" if preview else "attachment"
    
    return FileResponse(
        path=file_path,
        media_type=doc.mime_type,
        filename=doc.file_name if not preview else None,
        content_disposition_type=disp
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
    folder_filter: str = "",
    type_filter: str = "",
    date_filter: str = "",
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("No autorizado", status_code=401)
    try: session_data = session_signer.loads(cookie, max_age=86400)
    except: return HTMLResponse("Sesiï¿½ï¿½n invï¿½ï¿½lida", status_code=401)
    
    tenant_id = session_data.get("tenant_id")
    user_id = session_data.get("user_id")
    role_id = session_data.get("role_id")
    
    from app.rbac import get_role_hierarchy, get_user_groups, check_permission
    hierarchy = get_role_hierarchy(tenant_id, role_id)
    
    can_delete = hierarchy == 99 or check_permission(tenant_id, role_id, "documentos:eliminar")
    can_reassign = hierarchy == 99 or check_permission(tenant_id, role_id, "documentos:reasignar")
    
    folders = []
    if request.headers.get("hx-target") != "explorer-results":
        f_res = await db.execute(
            text("SELECT f.id, f.name, f.color, (SELECT COUNT(id) FROM documents WHERE folder_id = f.id) as doc_count FROM folders f WHERE f.tenant_id = :t ORDER BY f.created_at DESC"),
            {"t": tenant_id}
        )
        for r in f_res.fetchall():
            folders.append(dict(r._mapping))

    # Base query for FTS
    base_query = """
        SELECT d.id, d.file_name, d.status, d.created_at, d.thumbnail_path, d.mime_type, d.file_size_bytes, g.name as group_name,
        (SELECT json_agg(json_build_object('nombre', em.nombre, 'color_fondo', em.color_fondo, 'color_texto', em.color_texto))
         FROM documento_etiquetas de
         JOIN etiquetas_maestras em ON de.id_etiqueta = em.id_etiqueta
         WHERE de.id_documento = d.id) as tags
        FROM documents d
        LEFT JOIN groups g ON d.group_id = g.id
        WHERE d.tenant_id = :t
    """
    params = {"t": tenant_id}
    

    if q:
        # Also match if q matches a folder name
        base_query += " AND (d.fts_vector @@ plainto_tsquery('spanish', :q) OR d.folder_id IN (SELECT id FROM folders WHERE name ILIKE :q_like AND tenant_id = :t))"
        params["q"] = q
        params["q_like"] = f"%{q}%"
        
    if folder_filter:
        base_query += " AND d.folder_id = :f"
        params["f"] = folder_filter
        
    if type_filter == "pdf":
        base_query += " AND d.mime_type ILIKE '%pdf%'"
    elif type_filter == "images":
        base_query += " AND d.mime_type ILIKE '%image%'"
        
    if date_filter == "week":
        base_query += " AND d.created_at >= NOW() - INTERVAL '7 days'"
    elif date_filter == "month":
        base_query += " AND d.created_at >= date_trunc('month', NOW())"
    elif date_filter == "year":
        base_query += " AND d.created_at >= date_trunc('year', NOW())"

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
        base_query += """ AND (
            d.fts_vector @@ websearch_to_tsquery('spanish', :q)
            OR d.file_name ILIKE :q_wild
            OR g.name ILIKE :q_wild
            OR d.mime_type ILIKE :q_wild
        )"""
        params["q"] = q
        params["q_wild"] = f"%{q}%"
        
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
    
    import json
    result = await db.execute(text(base_query), params)
    rows = result.fetchall()
    
    docs = []
    for row in rows:
        d = dict(row._mapping)
        if d.get("tags") and isinstance(d["tags"], str):
            try:
                d["tags"] = json.loads(d["tags"])
            except:
                d["tags"] = []
        elif not d.get("tags"):
            d["tags"] = []
        docs.append(d)
    
    template_name = "components/explorer_results.html" if request.headers.get("hx-target") == "explorer-results" else "components/explorer.html"
    return templates.TemplateResponse(request=request, name=template_name, context={
        "request": request,
        "docs": docs,
        "folders": folders,
        "type_filter": type_filter,
        "date_filter": date_filter,
        "folder_filter": folder_filter,
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
    except: return HTMLResponse("Sesiï¿½ï¿½n invï¿½ï¿½lida", status_code=401)
    
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
            task_check_q = text("""
                SELECT 1 FROM tareas_asignaciones 
                WHERE id_documento = :did 
                AND (asignado_a = :uid OR asignado_por = :uid)
                LIMIT 1
            """)
            task_res = await db.execute(task_check_q, {"did": doc_id, "uid": user_id})
            if not task_res.fetchone():
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
    Endpoint de TransacciÃ³n Dual:
    1. Inserta en la DB (tareas_asignaciones).
    2. Dispara evento a Novu.
    """
    # Este endpoint deberÃ­a recibir un body (JSON o Form) con los detalles.
    # Como es un POST desde HTMX, probablemente sea un form.
    form_data = await request.form()
    asignado_a = form_data.get("asignado_a")
    etiqueta_accion = form_data.get("etiqueta_accion", "RevisiÃ³n General")
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
        
        # Actualizar assigned_user_id para que el RLS le de permisos de lectura al asignado
        await db.execute(
            text("UPDATE documents SET assigned_user_id = :uid WHERE id = :did"),
            {"uid": asignado_a, "did": doc_id}
        )
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        return HTMLResponse(f"<div class='text-red-500'>Error en base de datos: {str(e)}</div>", status_code=500)
        
    # 2. Trigger Novu
    from app.services.novu_client import novu_client
    
    # PodrÃ­amos buscar el nombre del remitente y del doc, pero usaremos dummies para el MVP
    payload = {
        "remitente_nombre": "Auditor Asignador", 
        "documento_titulo": f"Documento {doc_id}",
        "etiqueta_color": "#EF4444" if "Urgente" in etiqueta_accion else "#3B82F6",
        "etiqueta_texto": etiqueta_accion,
        "fecha_limite": str(tiempo_respuesta),
        "url_accion": f"/api/v1/documentos/{doc_id}/drawer"
    }
    
    # Disparamos sin bloquear el response
    # En producciÃ³n usarÃ­amos un BackgroundTask
    import asyncio
    asyncio.create_task(
        novu_client.trigger_event("WORKFLOW_DOCUMENTO_ASIGNADO", asignado_a, payload)
    )
    
    return HTMLResponse("<div class='text-green-500 p-2 bg-green-50 rounded'>Documento asignado y notificaciÃ³n enviada correctamente.</div>")

import os
import uuid
import hashlib
import json
import asyncio
from werkzeug.utils import secure_filename
from fastapi import BackgroundTasks

# Mock OCR function as requested
async def iniciar_extraccion_ocr(document_id: str):
    import asyncio
    from app.database import AsyncSessionLocal
    from sqlalchemy import text
    import fitz
    
    await asyncio.sleep(2)
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(text("SELECT file_path, extracted_text FROM documents WHERE id = :id"), {"id": document_id})
            row = res.fetchone()
            if not row:
                return
            
            file_path = row[0]
            existing_text = row[1]
            
            if existing_text and len(existing_text) > 50:
                await session.execute(text("UPDATE documents SET status = 'COMPLETED', ocr_confidence_score = 1.0 WHERE id = :id"), {"id": document_id})
                await session.commit()
                return

            text_content = ""
            if file_path and file_path.lower().endswith(".pdf"):
                try:
                    pdf_doc = fitz.open(file_path)
                    for page in pdf_doc:
                        text_content += page.get_text() + "\n"
                except Exception as e:
                    pass
            
            if not text_content.strip():
                text_content = "Texto extraído por OCR simulado (Documento escaneado)"
                
            await session.execute(text("UPDATE documents SET status = 'COMPLETED', ocr_confidence_score = 0.95, extracted_text = :text WHERE id = :id"), {"id": document_id, "text": text_content.strip()})
            await session.commit()
    except Exception as e:
        print(f"Error in OCR: {e}")
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
        
    # 2. Find fallback group_id that the user ACTUALLY belongs to
    # because Row-Level Security (RLS) blocks inserting a document for a group you don't belong to!
    group_id = None
    query_fallback = text("SELECT group_id FROM user_groups WHERE user_id = :uid LIMIT 1")
    res_group = await db.execute(query_fallback, {"uid": user_id})
    row = res_group.fetchone()
    if row:
        group_id = row.group_id
    else:
        # Fallback to any group if superadmin
        res_group = await db.execute(text("SELECT id FROM groups WHERE tenant_id = :t LIMIT 1"), {"t": tenant_id})
        row = res_group.fetchone()
        if row:
            group_id = row.id

    # 3. Insert into documents as DRAFT
    mime = archivo.content_type or "application/octet-stream"
    file_hash = hashlib.sha256(content).hexdigest()

    # GENERATE THUMBNAIL & FAST ROUTE
    thumb_dir = os.path.join(upload_dir, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)
    thumbnail_path = None
    fast_route_text = None
    final_status = "PENDING"
    
    thumb_filename = f"thumb_{file_hash}.webp"
    thumb_full_path = os.path.join(thumb_dir, thumb_filename)
    thumb_rel_path = f"/api/v1/documents/thumbnail/{tenant_id}/{thumb_filename}"
    
    import io
    if mime == "application/pdf":
        try:
            import fitz # PyMuPDF
            pdf_doc = fitz.open(stream=content, filetype="pdf")
            if len(pdf_doc) > 0:
                page = pdf_doc.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                from PIL import Image
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                if mode == "RGBA":
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                img.thumbnail((300, 400))
                img.save(thumb_full_path, "WEBP", quality=70)
                thumbnail_path = thumb_rel_path
                
            text_blocks = []
            for page in pdf_doc:
                text_blocks.append(page.get_text())
            fast_route_text = "\n".join(text_blocks).strip()
            if fast_route_text:
                final_status = "PENDING" # modal still requires PENDING
        except Exception as e:
            print(f"Error PDF routing/thumbnail: {e}")
            
    elif mime in ["image/jpeg", "image/png", "image/webp"]:
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


    query = text("""
        INSERT INTO documents (id, tenant_id, group_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, thumbnail_path, extracted_text)
        VALUES (:id, :t, :gid, :fn, :path, :uid, 'PENDING', FALSE, :mime, :size, :hash, :thumb, :text)
        RETURNING id
    """)
    doc_id = str(uuid.uuid4())
    from sqlalchemy.exc import IntegrityError
    try:
        await db.execute(query, {
            "id": doc_id,
            "t": tenant_id,
            "gid": group_id,
            "fn": safe_name,
            "path": disk_filename,
            "uid": user_id,
            "mime": mime,
            "size": file_size,
            "hash": file_hash,
            "thumb": thumbnail_path,
            "text": fast_route_text
        })
    except IntegrityError as e:
        await db.rollback()
        if "uq_tenant_file_hash" in str(e.orig):
            # Fetch the existing document info
            dup_query = text("""
                SELECT d.id, d.file_name, d.created_at, u.username
                FROM documents d
                LEFT JOIN users u ON d.uploaded_by = u.id
                WHERE d.file_hash = :hash AND d.tenant_id = :t
                LIMIT 1
            """)
            dup_res = await db.execute(dup_query, {"hash": file_hash, "t": tenant_id})
            dup_doc = dup_res.fetchone()
            
            if dup_doc:
                return templates.TemplateResponse(request=request, name="modals/duplicate_modal.html", context={
                    "request": request,
                    "document_name": safe_name,
                    "existing_id": dup_doc.id,
                    "existing_name": dup_doc.file_name,
                    "existing_date": dup_doc.created_at.strftime("%d %b, %Y %H:%M") if dup_doc.created_at else "Desconocida",
                    "existing_uploader": dup_doc.username or "Sistema"
                })
            else:
                import json
                response = HTMLResponse(content="")
                response.headers["HX-Trigger"] = json.dumps({
                    "alertaError": {"mensaje": "Documento duplicado."}
                })
                return response
        raise e
    
    # 3. Fetch tags, users, groups for the modal
    tags_res = await db.execute(text("SELECT id_etiqueta, nombre FROM etiquetas_maestras WHERE estado_activa = TRUE ORDER BY nombre"))
    etiquetas = tags_res.all()
    
    users_res = await db.execute(text("SELECT u.id, u.username, r.name as role_name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.tenant_id = :t AND u.id != :uid"), {"t": tenant_id, "uid": user_id})
    usuarios = users_res.all()
    
    groups_res = await db.execute(text("SELECT id, name FROM groups WHERE tenant_id = :t ORDER BY name"), {"t": tenant_id})
    grupos = groups_res.all()
    
    await db.commit()
    
    return templates.TemplateResponse(request=request, name="modals/routing_modal.html", context={
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
    
    # SANITIZACION FORENSE (HTMX envia strings vacios para selects no seleccionados)
    etiqueta_id = None if not etiqueta_id or etiqueta_id.strip() == "" else etiqueta_id
    asignado_usuario_id = None if not asignado_usuario_id or asignado_usuario_id.strip() == "" else asignado_usuario_id
    asignado_grupo_id = None if not asignado_grupo_id or asignado_grupo_id.strip() == "" else asignado_grupo_id
    
    try:
        # Validate rules
        if not es_privado:
            if asignado_usuario_id == current_user_id:
                raise HTTPException(status_code=400, detail="Fallo de Integridad: No puede auto-asignarse un documento de revisiÃ³n.")
            if not asignado_usuario_id and not asignado_grupo_id:
                raise HTTPException(status_code=400, detail="Debe asignar el documento a un usuario o grupo.")
                
        # 2. Update Document
        # REMOVED status update because 'PRIVADO' and 'OCR_PENDING' violate the documents_status_check constraint
        # The document is already in 'PENDING' or 'COMPLETED' (from fast route) and is_private boolean handles privacy.
        await db.execute(text("""
            UPDATE documents 
            SET is_private = :priv, assigned_user_id = :u_id, group_id = :g_id
            WHERE id = :id AND tenant_id = :t
        """), {
            "priv": es_privado, 
            "u_id": asignado_usuario_id if asignado_usuario_id else None, 
            "g_id": asignado_grupo_id if asignado_grupo_id else None,
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
        from app.rbac import log_audit_action
        await log_audit_action(
            db=db,
            tenant_id=tenant_id,
            user_id=current_user_id,
            action='DOCUMENTO_INGRESADO_Y_ENRUTADO',
            target_id=str(documento_id),
            details={"is_private": es_privado, "assigned_to": asignado_usuario_id}
        )
        
        # 5. Background Task
        # REMOVED if not es_privado: ALL documents (private or not) must run through OCR
        # otherwise they stay in PENDING forever and user cannot search their contents.
        # background_tasks.add_task(iniciar_extraccion_ocr, documento_id) # DELEGATED TO REAL OCR WORKER
            
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
        
    response = HTMLResponse(content="")
    response.headers["HX-Trigger"] = json.dumps({
        "toastExito": {"mensaje": "Documento cargado y enrutado exitosamente."},
        "reloadRecent": "",
        "reloadExplorer": ""
    })
    return response






@router.get("/api/v1/documentos/{doc_id}/reasignar/ui", response_class=HTMLResponse)
async def get_reasignar_modal(doc_id: str, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id: return HTMLResponse("")
    
    # Obtener grupos
    res_grupos = await db.execute(text("SELECT id, name FROM roles WHERE name != 'Admin'"))
    grupos = [dict(r._mapping) for r in res_grupos.fetchall()]
    
    res_usuarios = await db.execute(text("SELECT id, username, role_id FROM users WHERE role_id IS NOT NULL"))
    all_users = res_usuarios.fetchall()
    
    for g in grupos:
        g['id'] = str(g['id'])
        g['usuarios'] = [{"id": str(u.id), "username": u.username} for u in all_users if str(u.role_id) == g['id']]
        
    # Obtener etiquetas maestras (RBAC simulado: todas activas)
    res_etiquetas = await db.execute(text("SELECT id_etiqueta, nombre, color_fondo, color_texto FROM etiquetas_maestras WHERE estado_activa = TRUE"))
    etiquetas = res_etiquetas.fetchall()
    
    from datetime import datetime
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    
    return templates.TemplateResponse(request=request, name="modals/reasignar_modal.html", context={
        "documento_id": doc_id,
        "grupos": grupos,
        "etiquetas": etiquetas,
        "fecha_hoy": fecha_hoy
    })

@router.post("/api/v1/documentos/{doc_id}/reasignar", response_class=HTMLResponse)
async def post_reasignar(
    doc_id: str, 
    request: Request,
    destinatario_id: str = Form(...),
    etiqueta_id: str = Form(...),
    fecha_limite: str = Form(...),
    mensaje: str = Form(""),
    db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    tenant_id = getattr(request.state, "tenant_id", None)
    if not user_id: return HTMLResponse("No autorizado", status_code=401)
    
    try:
        # Transaccion ACID - The user specified logic exactly:
        # PASO 1: Cerrar tareas previas
        await db.execute(text("""
            UPDATE tareas_asignaciones 
            SET estado_tarea = 'Reasignado', fecha_cierre = CURRENT_TIMESTAMP 
            WHERE id_documento = :did AND estado_tarea IN ('Pendiente', 'En Progreso', 'Vencido')
        """), {"did": doc_id})
        
        from datetime import datetime
        fecha_obj = datetime.strptime(fecha_limite, "%Y-%m-%d")
        
        # PASO 2: Crear nueva tarea
        res_tarea = await db.execute(text("""
            INSERT INTO tareas_asignaciones (id_documento, asignado_por, asignado_a, tiempo_respuesta_esperado, estado_tarea, etiqueta_accion)
            VALUES (:did, :uid, :dest_id, :fecha, 'Pendiente', :etiqueta_id)
            RETURNING id_asignacion
        """), {
            "did": doc_id, 
            "uid": user_id, 
            "dest_id": destinatario_id, 
            "fecha": fecha_obj,
            "etiqueta_id": etiqueta_id
        })
        id_nueva_tarea = res_tarea.scalar()
        
        # PASO X: Actualizar el propietario del documento para el RLS
        await db.execute(text("""
            UPDATE documents 
            SET assigned_user_id = :dest_id 
            WHERE id = :did
        """), {"dest_id": destinatario_id, "did": doc_id})
        
        # PASO 3: Guardar mensaje
        if mensaje:
            await db.execute(text("""
                INSERT INTO tarea_mensajes (id_tarea, remitente_id, cuerpo)
                VALUES (:id_tarea, :uid, :msg)
            """), {"id_tarea": id_nueva_tarea, "uid": user_id, "msg": mensaje})
            
        # PASO 4: Actualizar etiqueta del documento
        await db.execute(text("DELETE FROM documento_etiquetas WHERE id_documento = :did"), {"did": doc_id})
        await db.execute(text("INSERT INTO documento_etiquetas (id_documento, id_etiqueta) VALUES (:did, :eid)"), 
            {"did": doc_id, "eid": etiqueta_id})
            
        # PASO 5: Boveda de auditoria
        from app.rbac import log_audit_action
        await log_audit_action(
            db=db, tenant_id=tenant_id, user_id=user_id,
            action='DOCUMENTO_REASIGNADO', target_id=str(doc_id),
            details={
                "destinatario_id": destinatario_id,
                "etiqueta_aplicada": etiqueta_id,
                "fecha_limite_sla": fecha_limite,
                "mensaje_incluido": bool(mensaje)
            }
        )
        
        await db.commit()
        
        # Disparo Novu asincrono
        from app.services.novu_client import novu_client
        await novu_client.trigger_event(
            event_name="documento_reasignado",
            user_id=destinatario_id,
            payload={
                "mensaje": f"Se te ha reasignado un documento. SLA: {fecha_limite}"
            }
        )
        
        # Return HTTP 200 with HTMX headers
        import json
        headers = {
            "HX-Trigger": "cerrar-modal-reasignacion",
            "HX-Trigger-After-Swap": json.dumps({
                "toastExito": {
                    "mensaje": "Documento reasignado y asegurado en la bandeja del destinatario."
                }
            })
        }
        return HTMLResponse(content="", headers=headers)
        
    except Exception as e:
        await db.rollback()
        raise e

@router.post("/api/v1/folders")
async def create_folder(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:subir")),
    db: AsyncSession = Depends(get_db_session)
):
    uid = session_data["user_id"]
    
    tenant_id = session_data["tenant_id"]
    form_data = await request.form()
    name = form_data.get("name")
    color = form_data.get("color", "#4648d4")
    
    if not name:
        return JSONResponse({"status": "error", "message": "Nombre requerido"}, status_code=400)
        
    try:
        res = await db.execute(
            text("INSERT INTO folders (tenant_id, name, color, created_by) VALUES (:t, :n, :c, :u) RETURNING id"),
            {"t": tenant_id, "n": name, "c": color, "u": uid}
        )
        folder_id = res.scalar()
        
        await db.execute(
            text("INSERT INTO folder_audit_logs (folder_id, action, user_id, details) VALUES (:f, 'CREAR_CARPETA', :u, :d)"),
            {"f": folder_id, "u": uid, "d": '{"name": "' + name + '"}'}
        )
        await db.commit()
        return JSONResponse({"status": "success", "folder_id": str(folder_id)})
    except Exception as e:
        await db.rollback()
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.post("/api/v1/documentos/{doc_id}/mover")
async def move_document(
    doc_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    uid = session_data["user_id"]
        
    form_data = await request.form()
    folder_id = form_data.get("folder_id")
    
    try:
        # Verify document exists and belongs to tenant
        doc_res = await db.execute(text("SELECT id FROM documents WHERE id = :d AND tenant_id = :t"), {"d": doc_id, "t": session_data["tenant_id"]})
        if not doc_res.scalar():
            return JSONResponse({"status": "error", "message": "Documento no encontrado"}, status_code=404)
            
        await db.execute(text("UPDATE documents SET folder_id = :f WHERE id = :d"), {"f": folder_id if folder_id else None, "d": doc_id})
        
        if folder_id:
            await db.execute(
                text("INSERT INTO folder_audit_logs (folder_id, action, user_id, details) VALUES (:f, 'MOVER_DOCUMENTO', :u, :d)"),
                {"f": folder_id, "u": uid, "d": '{"doc_id": "' + doc_id + '"}'}
            )
            
        await db.commit()
        
        return HTMLResponse(content='<script>Swal.fire({toast: true, position: "top-end", icon: "success", title: "Documento movido", showConfirmButton: false, timer: 2000}); setTimeout(()=>htmx.trigger("body", "reloadExplorer"), 1000);</script>', headers={"HX-Trigger": "reloadExplorer"})
    except Exception as e:
        await db.rollback()
        return HTMLResponse(f"<script>Swal.fire('Error', 'No se pudo mover: {str(e)}', 'error');</script>")
