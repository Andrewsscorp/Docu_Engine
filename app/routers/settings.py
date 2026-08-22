from fastapi import APIRouter, Request, Response, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
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


@router.get("/api/v1/license/ui", response_class=HTMLResponse)
async def get_license_ui(
    request: Request,
    session_data: dict = Depends(require_permission("ajustes:licencia")),
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    
    try:
        # Get License from DB
        query = text("""
            SELECT pgp_sym_decrypt(encrypted_license, :db_crypt_key)
            FROM users
            WHERE tenant_id = :tenant_id AND encrypted_license IS NOT NULL
            LIMIT 1
        """)
        result = await db.execute(query, {"tenant_id": tenant_id, "db_crypt_key": DB_CRYPT_KEY})
        row = result.fetchone()
        
        license_data = {}
        if row and row[0]:
            import json
            license_data = json.loads(row[0])
            
        exp_timestamp = license_data.get("exp_timestamp", 0)
        issued_at_str = license_data.get("issued_at", "")
        max_users = license_data.get("max_activations", 0)
        
        # Calculate Time Metrics
        from datetime import datetime
        exp_date = datetime.fromtimestamp(exp_timestamp)
        now = datetime.now()
        
        days_left = max((exp_date - now).days, 0)
        
        try:
            issued_date = datetime.fromisoformat(issued_at_str)
        except:
            issued_date = now
            
        total_days = max((exp_date - issued_date).days, 1)
        time_percentage = max(0, min(100, (days_left / total_days) * 100))
        time_color = "bg-green-500"
        if time_percentage < 20: time_color = "bg-red-500"
        elif time_percentage < 50: time_color = "bg-yellow-500"
        
        # Calculate User Metrics
        count_query = text("SELECT COUNT(*) FROM users WHERE tenant_id = :tenant_id AND is_active = true")
        count_res = await db.execute(count_query, {"tenant_id": tenant_id})
        current_users = count_res.fetchone()[0]
        
        user_percentage = max(0, min(100, (current_users / max_users) * 100)) if max_users > 0 else 100
        user_color = "bg-green-500"
        if user_percentage > 90: user_color = "bg-red-500"
        elif user_percentage > 70: user_color = "bg-yellow-500"
        
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
        
        html = f'''
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Columna Izquierda: Estado de la Licencia -->
            <div class="space-y-6">
                <div class="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                    <h4 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        Tiempo Restante
                    </h4>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="font-medium text-gray-600">{days_left} das disponibles</span>
                        <span class="text-gray-400">Total: {total_days} das</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3 mb-2">
                        <div class="{time_color} h-3 rounded-full transition-all duration-1000" style="width: {time_percentage}%"></div>
                    </div>
                    <p class="text-xs text-gray-500 text-right">Expira el {exp_date.strftime('%d/%m/%Y')}</p>
                </div>
                
                <div class="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                    <h4 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                        Usuarios de la Licencia
                    </h4>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="font-medium text-gray-600">{current_users} activos</span>
                        <span class="text-gray-400">Lmite: {max_users} usuarios</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-3 mb-2">
                        <div class="{user_color} h-3 rounded-full transition-all duration-1000" style="width: {user_percentage}%"></div>
                    </div>
                    <p class="text-xs text-gray-500 text-right">Lmite establecido por la licencia actual</p>
                </div>
            </div>
            
            <!-- Columna Derecha: Renovacin y HWID -->
            <div class="space-y-6">
                <!-- Tarjeta HWID -->
                <div class="bg-blue-50 rounded-2xl p-6 border border-blue-100">
                    <h4 class="text-lg font-bold text-blue-900 mb-2">ID de Hardware (HWID)</h4>
                    <p class="text-sm text-blue-700 mb-4">Enva este cdigo a tu proveedor para generar una nueva licencia. Este cdigo es único para esta Máquina.</p>
                    
                    <div class="flex gap-2">
                        <input type="text" id="hwidDisplay" readonly class="w-full px-4 py-2 bg-white border border-blue-200 rounded-lg text-sm text-gray-600 font-mono focus:outline-none focus:border-blue-400">
                        <button onclick="navigator.clipboard.writeText(document.getElementById('hwidDisplay').value); Swal.fire({{toast:true, position:'top-end', icon:'success', title:'HWID copiado!', showConfirmButton:false, timer:2000}})" class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm">
                            Copiar
                        </button>
                    </div>
                </div>
                
                <!-- Formulario Renovacin -->
                <form hx-post="/api/v1/license/renew" hx-swap="none" @htmx:after-request="if($event.detail.successful) {{ const res = JSON.parse($event.detail.xhr.response); if(res.status==='success') {{ Swal.fire({{icon:'success', title:'%xito!', text:res.message}}).then(()=>window.location.reload()); }} else {{ Swal.fire({{icon:'error', title:'Error', text:res.detail}}); }} }}" class="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm relative">
                    <input type="hidden" name="csrf_token" value="{signed_token}">
                    <input type="hidden" name="hwid_hash" id="hwidSubmit" value="">
                    
                    <h4 class="text-lg font-bold text-gray-800 mb-2">Aplicar Nueva Licencia</h4>
                    <p class="text-sm text-gray-500 mb-4">Pega el token JWT emitido por el sistema central de licencias.</p>
                    
                    <textarea name="license_token" rows="3" required placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 text-sm font-mono text-gray-600 mb-4 resize-none shadow-inner"></textarea>
                    
                    <button type="submit" class="w-full py-3 bg-primary text-white font-semibold rounded-xl hover:bg-blue-700 hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2 relative overflow-hidden group">
                        <span class="relative z-10 group-[.htmx-request]:opacity-0 transition-opacity">Renovar / Activar Licencia</span>
                        <div class="htmx-indicator absolute inset-0 flex items-center justify-center">
                            <div class="loader-spinner !w-6 !h-6 !border-2"></div>
                        </div>
                    </button>
                </form>
            </div>
        </div>
        <script>
            (async function() {{
                try {{
                    const rawHwid = navigator.userAgent + navigator.hardwareConcurrency + screen.colorDepth;
                    const msgBuffer = new TextEncoder().encode(rawHwid);
                    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
                    const hashArray = Array.from(new Uint8Array(hashBuffer));
                    const hwid = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                    
                    const disp = document.getElementById('hwidDisplay');
                    if (disp) disp.value = hwid;
                    const sub = document.getElementById('hwidSubmit');
                    if (sub) sub.value = hwid;
                }} catch (e) {{
                    console.error("No se pudo generar HWID:", e);
                }}
            }})();
        </script>
        '''
        return HTMLResponse(html)
    except Exception as e:
        import traceback; traceback.print_exc()
        return templates.TemplateResponse('component_12.html', {'request': request, 'str': str, 'e': e})

@router.post("/api/v1/license/renew")
async def renew_license(
    request: Request,
    hwid_hash: str = Form(...),
    license_token: str = Form(...),
    csrf_token: str = Form(...),
    session_data: dict = Depends(require_permission("ajustes:licencia")),
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    class PayloadDummy:
        def __init__(self, hw, lt, ct):
            self.hwid_hash = hw
            self.license_token = lt
            self.csrf_token = ct
    payload = PayloadDummy(hwid_hash, license_token, csrf_token)
    
    try:
        csrf_protect.validate_csrf(payload.csrf_token)
    except Exception:
        return JSONResponse({"status": "error", "detail": "Invalid CSRF token"}, status_code=403)
        
    client_ip = request.client.host if request.client else "unknown"
    tenant_id = session_data["tenant_id"]
    
    # Validation logic cloned from /api/register
    try:
        import hmac
        import hashlib
        import base64
        import json
        b64_license_payload, signature = payload.license_token.split('.')
        padding = '=' * (4 - len(b64_license_payload) % 4)
        payload_bytes = base64.urlsafe_b64decode(b64_license_payload + padding)
        
        expected_sig = hmac.new(MASTER_HMAC_KEY, payload_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return JSONResponse({"status": "error", "detail": "Firma de licencia inválida (Spoofing detectado)."})
            
        license_data = json.loads(payload_bytes.decode('utf-8'))
    except Exception as e:
        return JSONResponse({"status": "error", "detail": "Token de licencia malformado."})

    if license_data.get("hwid_hash") != payload.hwid_hash:
        return JSONResponse({"status": "error", "detail": "La licencia no pertenece a este hardware (HWID Mismatch)."})
        
    from datetime import datetime
    if license_data.get("exp_timestamp") < datetime.now().timestamp():
        return JSONResponse({"status": "error", "detail": "La licencia ha expirado."})
        
    # Validation passed. Update the encrypted_license in the database!
    # Update for the admin user (or we could just update the first user with an encrypted license)
    update_query = text("""
        UPDATE users 
        SET encrypted_license = pgp_sym_encrypt(:license_json, :db_crypt_key)
        WHERE tenant_id = :tenant_id AND encrypted_license IS NOT NULL
    """)
    try:
        await db.execute(update_query, {
            "tenant_id": tenant_id,
            "license_json": json.dumps(license_data),
            "db_crypt_key": DB_CRYPT_KEY
        })
        await db.commit()
    except Exception as e:
        await db.rollback()
        return JSONResponse({"status": "error", "detail": "Error en Base de Datos al guardar la licencia."})
        
    return JSONResponse({"status": "success", "message": "¡Licencia renovada exitosamente!"})

@router.get("/api/v1/ocr/settings/ui", response_class=HTMLResponse)
async def get_ocr_settings_ui(
    request: Request,
    session_data: dict = Depends(require_permission("ajustes:modificar")),
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    query = text("SELECT ocr_use_angle_cls, ocr_languages, ocr_confidence_threshold, ocr_pdf_resolution_dpi FROM tenant_ocr_settings WHERE tenant_id = :t")
    result = await db.execute(query, {"t": tenant_id})
    row = result.fetchone()
    if not row:
        return HTMLResponse("Error: Configuracion OCR no encontrada")
        
    angle = "checked" if row[0] else ""
    langs = row[1]
    conf = row[2]
    dpi = row[3]
    
    es_chk = "checked" if "es" in langs else ""
    en_chk = "checked" if "en" in langs else ""
    
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    
    html = f'''
    <form hx-post="/api/v1/ocr/settings/update" class="space-y-6">
        <input type="hidden" name="csrf_token" value="{signed_token}">
        
        <div>
            <label class="flex items-center gap-3 cursor-pointer">
                <div class="relative">
                    <input type="checkbox" name="ocr_use_angle_cls" class="sr-only" {angle}>
                    <div class="block bg-gray-200 w-14 h-8 rounded-full"></div>
                    <div class="dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition transform"></div>
                </div>
                <div>
                    <div class="font-bold text-gray-800">Detección de Ángulo (Angle Classification)</div>
                    <div class="text-xs text-gray-500">Corrige documentos escaneados al revés o torcidos. Consume +15% CPU.</div>
                </div>
            </label>
        </div>
        
        <div>
            <label class="block font-bold text-gray-800 mb-2">Idiomas Activos</label>
            <div class="flex gap-4">
                <label class="flex items-center gap-2">
                    <input type="checkbox" name="lang_es" value="1" {es_chk} class="w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"> Español
                </label>
                <label class="flex items-center gap-2">
                    <input type="checkbox" name="lang_en" value="1" {en_chk} class="w-5 h-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"> Inglés
                </label>
            </div>
            <p class="text-xs text-gray-500 mt-1">Limitar idiomas acelera el proceso y reduce falsos positivos.</p>
        </div>
        
        <div>
            <label class="block font-bold text-gray-800 mb-2">Umbral de Confianza: <span id="conf_val">{conf}</span></label>
            <input type="range" name="ocr_confidence_threshold" min="0.1" max="1.0" step="0.05" value="{conf}" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" oninput="document.getElementById('conf_val').innerText = this.value">
            <p class="text-xs text-gray-500 mt-1">Palabras con menor confianza serán marcadas para revisión humana.</p>
        </div>
        
        <div>
            <label class="block font-bold text-gray-800 mb-2">Resolución de Escaneo PDF (DPI)</label>
            <select name="ocr_pdf_resolution_dpi" class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 outline-none">
                <option value="150" {"selected" if dpi == 150 else ""}>150 DPI (Rápido, baja calidad)</option>
                <option value="200" {"selected" if dpi == 200 else ""}>200 DPI (Recomendado)</option>
                <option value="300" {"selected" if dpi == 300 else ""}>300 DPI (Lento, alta nitidez)</option>
            </select>
        </div>
        
        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-500/30">
            Guardar Configuración OCR
        </button>
        <style>
            input:checked ~ .dot {{ transform: translateX(100%); background-color: #2563eb; }}
        </style>
    </form>
    '''
    return HTMLResponse(content=html)

@router.post("/api/v1/ocr/settings/update", response_class=HTMLResponse)
async def update_ocr_settings(
    request: Request,
    csrf_token: str = Form(...),
    ocr_use_angle_cls: str = Form(None),
    lang_es: str = Form(None),
    lang_en: str = Form(None),
    ocr_confidence_threshold: float = Form(...),
    ocr_pdf_resolution_dpi: int = Form(...),
    session_data: dict = Depends(require_permission("ajustes:modificar")),
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        csrf_protect.validate_csrf(csrf_token)
    except Exception:
        return HTMLResponse("<div class='text-red-500'>Invalid CSRF</div>")
        
    tenant_id = session_data["tenant_id"]
    angle = True if ocr_use_angle_cls else False
    
    langs = []
    if lang_es: langs.append("es")
    if lang_en: langs.append("en")
    if not langs: langs.append("es") # fallback
    
    query = text('''
        UPDATE tenant_ocr_settings
        SET ocr_use_angle_cls = :angle,
            ocr_languages = :langs,
            ocr_confidence_threshold = :conf,
            ocr_pdf_resolution_dpi = :dpi
        WHERE tenant_id = :t
    ''')
    await db.execute(query, {
        "angle": angle,
        "langs": langs,
        "conf": ocr_confidence_threshold,
        "dpi": ocr_pdf_resolution_dpi,
        "t": tenant_id
    })
    await db.commit()
    
    return HTMLResponse("<div class='text-green-600 font-bold p-4 bg-green-50 rounded-xl'>Configuración guardada exitosamente.</div>")