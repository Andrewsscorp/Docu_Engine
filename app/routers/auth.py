
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    licencia: str

class MFAVerifyRequest(BaseModel):
    username: str
    password: str
    code: str

from fastapi import APIRouter, Request, Response, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db_session
from argon2.exceptions import VerifyMismatchError
import argon2

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
from pydantic import BaseModel, Field
from enum import Enum

class IdiomaEnum(str, Enum):
    es = 'es'
    en = 'en'

class SettingsUpdate(BaseModel):
    nombre_empresa: str = Field(..., max_length=100)
    idioma: IdiomaEnum
    notificaciones_email: bool

router = APIRouter()

# Memory cache
from app.security import settings_l1_cache

def invalidate_settings_cache(tenant_id: str):
    if tenant_id in settings_l1_cache:
        del settings_l1_cache[tenant_id]


# Moved to main.py
# @app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return templates.TemplateResponse('component_1.html', {'request': request, 'exc': exc})


@router.get("/")
async def get_index(request: Request, db: AsyncSession = Depends(get_db_session)):
    # Si ya tiene cookie de sesiÃƒÂ³n vÃƒÂ¡lida, redirigir al dashboard
    if request.cookies.get("sessionId"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard")
        
    branding = await get_tenant_branding(db)
    bg_style = f"url('{branding['login_bg_url']}')" if branding.get('login_bg_url') else "url('/imgs_externas/FONDO%20LOGGGIN.jpg')"
    with open("app/templates/pages/index.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("DOCUENGINE_BRAND_NAME", branding['nombre_empresa'])
        html = html.replace("DOCUENGINE_LOGIN_BG", bg_style)
        return HTMLResponse(content=html, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})

@router.get("/style.css")
async def get_style():
    with open("style.css", "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="text/css")

@router.get("/api/v1/csrf-token")
def get_csrf(response: Response, csrf_protect: CsrfProtect = Depends()):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)
    return {"csrf_token": csrf_token}

def render_settings_form(csrf_token: str, data: dict, show_success: bool=False):
    button_html = f"""\n        <div class="flex justify-end mt-4">\n            <button type="submit" x-data="{{ show: true }}" x-init="setTimeout(() => show = false, 3000)" \n                    class="font-semibold py-3 px-8 rounded-lg transition-colors shadow-lg"\n                    :class="show ? 'bg-green-500 hover:bg-green-600 text-white shadow-green-500/30' : 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/30'"\n                    x-text="show ? 'Ã‚Â¡Ajustes Guardados exitosamente!' : 'Guardar Cambios'">\n            </button>\n        </div>\n    """ if show_success else '\n        <div class="flex justify-end mt-4">\n            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors shadow-lg shadow-blue-500/30">\n                Guardar Cambios\n            </button>\n        </div>\n    '
    oob_html = f'''\n    <div id="brandLogo" hx-swap-oob="true" class="text-xl md:text-2xl font-bold text-center mb-10 tracking-widest text-textmain break-words whitespace-normal leading-tight px-2" title="{data['nombre_empresa']}">\n        {data['nombre_empresa']}\n    </div>\n    ''' if show_success else ''
    return f'''\n    {oob_html}\n    <form hx-patch="/api/v1/settings" hx-headers='{{"X-CSRF-Token": "{csrf_token}"}}' hx-encoding="multipart/form-data" hx-swap="outerHTML" class="space-y-6">\n        <div class="settings-group">\n            <label class="block font-medium text-gray-700 mb-2">Nombre de la Empresa</label>\n            <input type="text" name="nombre_empresa" value="{data['nombre_empresa']}" required maxlength="100" class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none text-gray-800 transition-colors">\n        </div>\n        \n        <div class="settings-group">\n            <label class="block font-medium text-gray-700 mb-2">Idioma Preferido</label>\n            <select name="idioma" class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none text-gray-800 transition-colors">\n                <option value="es" {('selected' if data['idioma'] == 'es' else '')}>EspaÃƒÂ±ol</option>\n                <option value="en" {('selected' if data['idioma'] == 'en' else '')}>InglÃƒÂ©s</option>\n            </select>\n        </div>\n\n        \n        <div class="settings-group">\n            <label class="block font-medium text-gray-700 mb-2">Imagen de Fondo (Login)</label>\n            <input type="file" name="login_bg_image" accept="image/*" class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none text-gray-800 transition-colors">\n            <p class="text-sm text-gray-500 mt-1">Sube una nueva imagen para cambiar el fondo de la pantalla de inicio.</p>\n        </div>\n\n        <div class="settings-group">\n            <label class="block font-medium text-gray-700 mb-2">Notificaciones por Email</label>\n            <select name="notificaciones_email" class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none text-gray-800 transition-colors">\n                <option value="true" {('selected' if data['notificaciones_email'] else '')}>Activadas</option>\n                <option value="false" {('selected' if not data['notificaciones_email'] else '')}>Desactivadas</option>\n            </select>\n        </div>\n        \n        {button_html}\n    </form>\n    '''

@router.get("/api/v1/settings", response_class=HTMLResponse)
async def get_settings(
    request: Request, 
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    if not request.cookies.get("sessionId"):
        return HTMLResponse("No autorizado", status_code=401)

    tenant_id = "22222222-2222-2222-2222-222222222222"
    
    # Check L1 Cache
    if tenant_id in settings_l1_cache:
        data = settings_l1_cache[tenant_id]
    else:
        query = text("SELECT nombre_empresa, idioma, notificaciones_email, login_bg_url FROM tenant_settings WHERE tenant_id = :tenant_id")
        result = await db.execute(query, {"tenant_id": tenant_id})
        row = result.fetchone()
        
        if not row:
            return HTMLResponse("Tenant no encontrado", status_code=404)
            
        data = {
            "nombre_empresa": row[0],
            "idioma": row[1],
            "notificaciones_email": row[2],
            "login_bg_url": row[3]
        }
        settings_l1_cache[tenant_id] = data
        
    # Generar Token CSRF
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    
    response = HTMLResponse(content=render_settings_form(csrf_token, data))
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

@router.patch("/api/v1/settings", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    if not request.cookies.get("sessionId"):
        return HTMLResponse("No autorizado", status_code=401)
        
    await csrf_protect.validate_csrf(request)

    form_data = await request.form()
    
    try:
        update_data = SettingsUpdate(
            nombre_empresa=form_data.get("nombre_empresa"),
            idioma=form_data.get("idioma"),
            notificaciones_email=(form_data.get("notificaciones_email") == "true")
        )
    except Exception as e:
        return HTMLResponse(f"<div class='text-red-500 font-bold'>Datos invalidos. Intento de manipulacion bloqueado.</div>", status_code=200)

    tenant_id = "22222222-2222-2222-2222-222222222222"
    
    # Extraemos el archivo si existe
    bg_url = None
    import os
    import shutil
    import time
    bg_file = form_data.get("login_bg_image")
    with open("debug.txt", "w") as f:
        f.write("========== DEBUG UPLOAD ==========\n")
        f.write(f"form_data keys: {form_data.keys()}\n")
        f.write(f"bg_file: {bg_file}\n")
        if bg_file:
            f.write(f"filename: {getattr(bg_file, 'filename', 'NO FILENAME')}\n")
        f.write("==================================\n")
    if bg_file and hasattr(bg_file, "filename") and bg_file.filename:
        # Guardar en disk
        file_ext = os.path.splitext(bg_file.filename)[1]
        save_path = f"uploads/bg_{tenant_id}_{int(time.time())}{file_ext}"
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(bg_file.file, buffer)
        bg_url = f"/{save_path}"
        
    if bg_url:
        query = text("""
            UPDATE tenant_settings 
            SET nombre_empresa = :nombre, idioma = :idioma, notificaciones_email = :notif, login_bg_url = :bg_url, updated_at = CURRENT_TIMESTAMP
            WHERE tenant_id = :tenant_id
        """)
        await db.execute(query, {
            "nombre": update_data.nombre_empresa,
            "idioma": update_data.idioma.value,
            "notif": update_data.notificaciones_email,
            "bg_url": bg_url,
            "tenant_id": tenant_id
        })
    else:
        query = text("""
            UPDATE tenant_settings 
            SET nombre_empresa = :nombre, idioma = :idioma, notificaciones_email = :notif, updated_at = CURRENT_TIMESTAMP
            WHERE tenant_id = :tenant_id
        """)
        await db.execute(query, {
            "nombre": update_data.nombre_empresa,
            "idioma": update_data.idioma.value,
            "notif": update_data.notificaciones_email,
            "tenant_id": tenant_id
        })
    await db.commit()

    invalidate_settings_cache(tenant_id)

    # Generamos de nuevo la pÃƒÂ¡gina con un nuevo token CSRF por seguridad post-consumo
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    
    data = {
        "nombre_empresa": update_data.nombre_empresa,
        "idioma": update_data.idioma.value,
        "notificaciones_email": update_data.notificaciones_email
    }

    # 4. Respuesta Reactiva de HTMX
    response = HTMLResponse(content=render_settings_form(csrf_token, data, show_success=True))
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

@router.get("/api/logout")
async def logout(request: Request):
    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("sessionId")
    return response

@router.get("/dashboard")
async def get_dashboard(request: Request, db: AsyncSession = Depends(get_db_session)):
    cookie = request.cookies.get("sessionId")
    if not cookie:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/")
        
    try:
        session_data = session_signer.loads(cookie, max_age=86400)
    except Exception:
        from fastapi.responses import RedirectResponse
        response = RedirectResponse(url="/")
        response.delete_cookie("sessionId")
        return response
        
    tenant_id = session_data.get("tenant_id")
    role_id = session_data.get("role_id")
    must_change = session_data.get("must_change_password", False)
    
    if must_change:
        html = f'''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Cambio de ContraseÃ±a Requerido</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://unpkg.com/htmx.org@1.9.10"></script>
        </head>
        <body class="bg-gray-50 flex items-center justify-center min-h-screen">
            <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
                <div class="mb-6 text-center">
                    <div class="text-4xl mb-4">ðŸ”</div>
                    <h2 class="text-2xl font-bold text-gray-800">Actualiza tu Seguridad</h2>
                    <p class="text-sm text-gray-500 mt-2">Por polÃ­ticas de la empresa o porque es tu primer ingreso, debes cambiar tu contraseÃ±a ahora mismo.</p>
                </div>
                <form hx-post="/api/v1/force-password-change" class="space-y-4">
                    <div>
                        <label class="block text-sm font-bold text-gray-700 mb-1">Nueva ContraseÃ±a</label>
                        <input type="password" name="new_password" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 outline-none">
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-gray-700 mb-1">Confirmar ContraseÃ±a</label>
                        <input type="password" name="confirm_password" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 outline-none">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-all">Cambiar y Entrar</button>
                    <div id="password-error" class="text-red-500 text-sm mt-2 text-center font-bold"></div>
                </form>
            </div>
        </body>
        </html>
        '''
        return HTMLResponse(content=html, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})
    
    branding = await get_tenant_branding(db)
    with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
        import json
        from app import rbac
        html = f.read()
        html = html.replace("DOCUENGINE_BRAND_NAME", branding['nombre_empresa'])
        html = html.replace("DOCUENGINE_USERNAME", session_data.get("username", "Usuario"))
        
        # Inyectar usuarios para el filtro avanzado
        users_html = ""
        try:
            from sqlalchemy import text
            res = await db.execute(text("SELECT id, username FROM users WHERE is_active = true ORDER BY username ASC"))
            users = res.fetchall()
            for u in users:
                users_html += f'<option value="{u.id}">{u.username}</option>\n'
        except Exception:
            pass
        html = html.replace("<!-- USERS_OPTIONS_INJECTION -->", users_html)
        
        # Inject Groups logic
        user_id = session_data.get("user_id")
        hierarchy = rbac.get_role_hierarchy(tenant_id, role_id)
        is_sa = hierarchy == 99
        
        groups_list = []
        if is_sa:
            # Superadmin gets all groups
            if tenant_id in rbac.rbac_l1_cache:
                for g_id, g_data in rbac.rbac_l1_cache[tenant_id].get("groups", {}).items():
                    groups_list.append({"id": g_id, "name": g_data["name"]})
        else:
            # Regular user gets only their groups
            assigned_groups = rbac.get_user_groups(tenant_id, user_id)
            if tenant_id in rbac.rbac_l1_cache:
                for g_id in assigned_groups:
                    g_data = rbac.rbac_l1_cache[tenant_id].get("groups", {}).get(g_id)
                    if g_data:
                        groups_list.append({"id": g_id, "name": g_data["name"]})
        
        # Ensure at least General exists if empty (fallback)
        if not groups_list:
            groups_list.append({"id": "", "name": "General (Default)"})
            
        html = html.replace("DOCUENGINE_USER_GROUPS_JSON", json.dumps(groups_list))
        html = html.replace("DOCUENGINE_IS_SUPERADMIN", "true" if is_sa else "false")
        
        # Zero Trust Rendering
        
        
        from app.rbac import check_permission
        c1 = check_permission(tenant_id, role_id, "usuarios:leer")
        c2 = check_permission(tenant_id, role_id, "roles:leer")
        from app import rbac
        c_lic = check_permission(tenant_id, role_id, "ajustes:licencia")
        if c1 or c2:


            usuarios_btn = '''
                <div id="btn-users" @click="currentView = 'users'" class="bg-white p-6 rounded-2xl card-shadow cursor-pointer hover:-translate-y-1 transition-transform flex items-center gap-4 border border-transparent hover:border-blue-500">
                    <div class="text-4xl">&#128101;</div>
                    <div>
                        <h4 class="font-bold text-textmain">Usuarios y Roles</h4>
                        <p class="text-sm text-textmuted">Seguridad y Permisos</p>
                    </div>
                </div>'''
            usuarios_section = '''
            <section x-show="currentView === 'users'" x-transition.opacity.duration.300ms x-cloak>
                <button @click="currentView = 'settings'" class="mb-4 text-blue-600 font-bold hover:underline">â† Volver a Ajustes</button>
                <div hx-get="/api/v1/rbac/ui" hx-trigger="click from:#btn-users">Cargando mÃ³dulo de seguridad...</div>
            </section>'''
            
            html = html.replace("<!-- MENUS_DINAMICOS_AJUSTES -->", usuarios_btn)
            html = html.replace("<!-- MENUS_DINAMICOS_SECTION -->", usuarios_section)
        else:
            html = html.replace("<!-- MENUS_DINAMICOS_AJUSTES -->", "")
            html = html.replace("<!-- MENUS_DINAMICOS_SECTION -->", "")
            
        
        if c_lic:
            licencia_btn = '''
                <div id="btn-licencia" @click="licenseOpen = true" class="bg-white p-6 rounded-2xl card-shadow cursor-pointer hover:-translate-y-1 transition-transform flex items-center gap-4 border border-transparent hover:border-primary">
                    <div class="text-4xl">&#128273;</div>
                    <div>
                        <h4 class="font-bold text-textmain">Licencia del Sistema</h4>
                        <p class="text-sm text-textmuted">RenovaciÃ³n, LÃ­mites y HWID</p>
                    </div>
                </div>'''
            html = html.replace("<!-- MENUS_DINAMICOS_LICENCIA -->", licencia_btn)
        else:
            html = html.replace("<!-- MENUS_DINAMICOS_LICENCIA -->", "")
            

        html = html.replace("<!-- MENUS_DINAMICOS_LICENCIA -->", "")
        
        # Inyectar modulos laterales (Notificaciones y Etiquetas) segun permisos
        dinamicos_li = ""
        if rbac.check_permission(tenant_id, role_id, "notificaciones:ver") or is_sa:
            dinamicos_li += '''<li @click="currentView = 'notifications'" title="Notificaciones"
              class="px-5 py-3.5 rounded-2xl cursor-pointer font-medium transition-all flex items-center gap-4 whitespace-nowrap overflow-hidden relative"
              :class="currentView === 'notifications' ? 'bg-gradient-to-r from-primary to-[#868CFF] text-white shadow-lg shadow-primary/40' : 'text-gray-400 hover:text-white hover:bg-white/5'">
              <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
            <span x-show="sidebarOpen" x-transition.opacity>Notificaciones</span>
            <!-- AlpineJS Badge for Unread Notifications -->
              <div x-data="{ total: 0 }" 
                   @update-sidebar-counts.window="total = $event.detail" 
                   x-show="total > 0 && sidebarOpen" x-cloak 
                   class="ml-auto flex shrink-0 items-center justify-center bg-rose-500 text-white min-w-[20px] h-5 px-1.5 rounded-full text-[11px] font-bold shadow-sm ring-1 ring-white/20"
                   x-text="total">
              </div>
              <div x-data="{ total: 0 }" 
                   @update-sidebar-counts.window="total = $event.detail" 
                   x-show="total > 0 && !sidebarOpen" x-cloak 
                   class="absolute top-2 right-2 w-3 h-3 bg-rose-500 rounded-full border-2 border-[#1E1B4B] shadow-sm">
              </div>
          </li>'''
        if rbac.check_permission(tenant_id, role_id, "etiquetas:ver") or is_sa:
            dinamicos_li += '''<li @click="currentView = 'tags'" title="Etiquetas"
            class="px-5 py-3.5 rounded-2xl cursor-pointer font-medium transition-all flex items-center gap-4 whitespace-nowrap overflow-hidden"
            :class="currentView === 'tags' ? 'bg-gradient-to-r from-primary to-[#868CFF] text-white shadow-lg shadow-primary/40' : 'text-gray-400 hover:text-white hover:bg-white/5'">
            <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>
            <span x-show="sidebarOpen" x-transition.opacity>Etiquetas</span>
        </li>'''
        
        html = html.replace("<!-- MENUS_DINAMICOS_LI -->", dinamicos_li)


            
        return HTMLResponse(content=html, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"})

@router.get("/dashboard.css")
async def get_dashboard_style():
    with open("dashboard.css", "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="text/css")

@router.post("/api/register")
async def register(
    payload: RegisterRequest, 
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
):
    client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit(client_ip, payload.username)

    # 1. ValidaciÃƒÂ³n de la Licencia Off-Grid en Memoria (HMAC-SHA256)
    try:
        b64_license_payload, signature = payload.license_token.split('.')
        # Corregir padding base64 si es necesario
        padding = '=' * (4 - len(b64_license_payload) % 4)
        payload_bytes = base64.urlsafe_b64decode(b64_license_payload + padding)
        
        # Recalcular y comparar firma
        expected_sig = hmac.new(MASTER_HMAC_KEY, payload_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            attempts = record_failed_attempt(client_ip, payload.username)
            raise HTTPException(status_code=200, detail=f"Firma de licencia invÃƒÂ¡lida (Spoofing detectado). Intento fallido {attempts} de {MAX_FAILS_PER_HOUR}.")
            
        license_data = json.loads(payload_bytes.decode('utf-8'))
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        attempts = record_failed_attempt(client_ip, payload.username)
        raise HTTPException(status_code=200, detail=f"Token de licencia malformado. Intento fallido {attempts} de {MAX_FAILS_PER_HOUR}.")

    # 2. Verificar Hardware ID y ExpiraciÃƒÂ³n
    if license_data.get("hwid_hash") != payload.hwid_hash:
        attempts = record_failed_attempt(client_ip, payload.username)
        raise HTTPException(status_code=200, detail=f"La licencia no pertenece a este hardware (HWID Mismatch). Intento fallido {attempts} de {MAX_FAILS_PER_HOUR}.")
        
    if license_data.get("exp_timestamp") < datetime.now().timestamp():
        raise HTTPException(status_code=200, detail="La licencia ha expirado.")

    # 3. DerivaciÃƒÂ³n de Clave Argon2id
    hashed_password = ph.hash(payload.password)
    
    # 4. InserciÃƒÂ³n en PostgreSQL usando pgcrypto (Zero Trust)
    # RLS tenant_id ya fue inyectado por database.py
    insert_query = text("""
        INSERT INTO users (tenant_id, username, hash_password, encrypted_license)
        VALUES (
            :tenant_id, 
            :username, 
            :hash_password, 
            pgp_sym_encrypt(:license_json, :db_crypt_key)
        )
    """)
    try:
        await db.execute(insert_query, {
            "tenant_id": "22222222-2222-2222-2222-222222222222", # Hardcoded para demo
            "username": payload.username,
            "hash_password": hashed_password,
            "license_json": json.dumps(license_data),
            "db_crypt_key": DB_CRYPT_KEY
        })
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=200, detail="El usuario ya existe o error en DB.")

    return {"status": "success", "message": "Administrador registrado exitosamente bajo licencia encriptada."}

@router.post("/api/login")
async def login(
    credentials: LoginRequest, 
    request: Request, 
    response: Response,
    db: AsyncSession = Depends(get_db_session)
):
    client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit(client_ip, credentials.username)
    
    query = text("SELECT id, tenant_id, role_id, hash_password, require_password_change, password_expires_at, password_policy, is_active, access_time_start, access_time_end, mfa_enabled, mfa_secret, mfa_verified FROM users WHERE username = :username LIMIT 1")
    result = await db.execute(query, {"username": credentials.username})
    row = result.fetchone()
    
    user_hash = row[3] if row else None
    user_exists = user_hash is not None
    hash_to_verify = user_hash if user_exists else DUMMY_HASH
    
    is_valid = False
    try:
        is_valid = ph.verify(hash_to_verify, credentials.password)
    except (VerifyMismatchError, argon2.exceptions.InvalidHashError):
        is_valid = False

    if user_exists and is_valid:
        is_active = row[7]
        if not is_active:
            raise HTTPException(status_code=403, detail="Tu cuenta ha sido bloqueada. Contacta al administrador.")
            
        time_start = row[8]
        time_end = row[9]
        from datetime import datetime, timezone
        if time_start is not None and time_end is not None:
            current_time = datetime.now().time()
            if time_start <= time_end:
                if not (time_start <= current_time <= time_end):
                    raise HTTPException(status_code=403, detail=f"Acceso denegado. Tu horario permitido es de {time_start.strftime('%H:%M')} a {time_end.strftime('%H:%M')}.")
            else:
                if not (current_time >= time_start or current_time <= time_end):
                    raise HTTPException(status_code=403, detail=f"Acceso denegado. Tu horario permitido es de {time_start.strftime('%H:%M')} a {time_end.strftime('%H:%M')}.")
                    
        require_change = row[4]
        expires_at = row[5]
        
        from datetime import datetime, timezone
        
        must_change = require_change
        if expires_at and expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            must_change = True
            
        session_data = {
            "user_id": str(row[0]),
            "tenant_id": str(row[1]),
            "role_id": str(row[2]) if row[2] else "",
            "username": credentials.username,
            "must_change_password": must_change
        }
        mfa_enabled = len(row) > 10 and row[10]
        mfa_secret = row[11] if len(row) > 11 else None
        mfa_verified = row[12] if len(row) > 12 else False
        
        if mfa_enabled:
            # We issue a preauth token, NOT a session cookie
            preauth_data = {
                "user_id": str(row[0]),
                "tenant_id": str(row[1]),
                "role_id": str(row[2]) if row[2] else "",
                "username": credentials.username,
                "must_change_password": must_change
            }
            token = session_signer.dumps(preauth_data)
            
            setup_required = False
            qr_url = ""
            if not mfa_verified:
                setup_required = True
                if not mfa_secret:
                    mfa_secret = pyotp.random_base32()
                    # Save it immediately so it's ready for verification
                    await db.execute(text("UPDATE users SET mfa_secret = :secret WHERE id = :uid"), {"secret": mfa_secret, "uid": str(row[0])})
                    await db.commit()
                
                totp = pyotp.TOTP(mfa_secret)
                prov_uri = totp.provisioning_uri(name=credentials.username, issuer_name="DocuEngine")
                
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(prov_uri)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                qr_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
                
            return {"mfa_required": True, "setup": setup_required, "token": token, "qr_url": qr_url}
            
        # Actualizar last_login_at
        await db.execute(text("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = :uid"), {"uid": str(row[0])})
        from app.rbac import log_audit_action
        await log_audit_action(db, str(row[1]), str(row[0]), "USER_LOGIN", str(row[0]), {"ip_address": client_ip, "mfa_used": False})
        await db.commit()
        session_token = session_signer.dumps(session_data)
        response.set_cookie(
            key="sessionId",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=86400
        )
        return {"status": "success", "message": "Login exitoso. Autenticado contra PostgreSQL seguro."}
    else:
        attempts = record_failed_attempt(client_ip, credentials.username)
        raise HTTPException(status_code=401, detail=f"Credenciales invÃƒÂ¡lidas. Intento fallido {attempts} de {MAX_FAILS_PER_HOUR}.")

@router.post("/api/v1/auth/mfa/verify")
async def verify_mfa(req: MFAVerifyRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db_session)):
    try:
        session_data = session_signer.loads(req.token, max_age=300) # 5 minutes max to verify MFA
    except Exception:
        raise HTTPException(status_code=401, detail="Token expirado o invÃ¡lido. Inicia sesiÃ³n nuevamente.")
        
    user_id = session_data["user_id"]
    query = text("SELECT mfa_secret FROM users WHERE id = :uid LIMIT 1")
    res = await db.execute(query, {"uid": user_id})
    row = res.fetchone()
    
    if not row or not row[0]:
        raise HTTPException(status_code=400, detail="MFA no estÃ¡ configurado correctamente para este usuario.")
        
    totp = pyotp.TOTP(row[0])
    if not totp.verify(req.code):
        raise HTTPException(status_code=401, detail="CÃ³digo incorrecto.")
        
    # Mark as verified!
    await db.execute(text("UPDATE users SET mfa_verified = true, last_login_at = CURRENT_TIMESTAMP WHERE id = :uid"), {"uid": user_id})
    from app.rbac import log_audit_action
    client_ip = request.client.host if request.client else "unknown"
    await log_audit_action(db, session_data["tenant_id"], user_id, "USER_LOGIN", user_id, {"ip_address": client_ip, "mfa_used": True})
    await db.commit()
        
    # Validation successful. Issue real session.
    session_token = session_signer.dumps(session_data)
    response.set_cookie(
        key="sessionId",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=86400
    )
    return {"status": "success", "message": "MFA verificado correctamente."}

@router.get("/api/v1/auth/status")
async def check_auth_status(request: Request, response: Response, db: AsyncSession = Depends(get_db_session)):
    cookie = request.cookies.get("sessionId")
    if not cookie: return HTMLResponse("")
    try: 
        session_data = session_signer.loads(cookie, max_age=86400)
    except: 
        return HTMLResponse("<script>window.location.href='/login';</script>")
        
    user_id = session_data.get("user_id")
    query = text("SELECT expel_at FROM users WHERE id = :uid")
    res = await db.execute(query, {"uid": user_id})
    row = res.fetchone()
    
    if not row or not row[0]:
        return HTMLResponse("")
        
    expel_at = row[0]
    from datetime import datetime, timezone
    now_utc = datetime.now(timezone.utc)
    if expel_at.tzinfo is None:
        expel_at_utc = expel_at.replace(tzinfo=timezone.utc)
    else:
        expel_at_utc = expel_at
        
    # If expel_at is in the past, log them out
    if expel_at_utc <= now_utc:
        response = HTMLResponse("<script>window.location.href='/login';</script>")
        response.delete_cookie("sessionId")
        return response
        
    # If expel_at is in the future, show countdown popup
    seconds_left = int((expel_at_utc - now_utc).total_seconds())
    
    return templates.TemplateResponse('component_2.html', {'request': request, 'seconds_left': seconds_left})

@router.post("/api/v1/force-password-change", response_class=HTMLResponse)
async def force_password_change(
    request: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: AsyncSession = Depends(get_db_session)
):
    cookie = request.cookies.get("sessionId")
    if not cookie:
        return HTMLResponse("<div id='password-error' class='text-red-500 font-bold'>SesiÃ³n no vÃ¡lida.</div>")
        
    try:
        session_data = session_signer.loads(cookie, max_age=86400)
    except Exception:
        return HTMLResponse("<div id='password-error' class='text-red-500 font-bold'>SesiÃ³n expirada.</div>")
        
    user_id = session_data["user_id"]
    
    if new_password != confirm_password:
        return HTMLResponse("<div id='password-error' class='text-red-500 font-bold'>Las contraseÃ±as no coinciden.</div>")
        
    query = text("SELECT password_policy FROM users WHERE id = :user_id")
    res = await db.execute(query, {"user_id": user_id})
    row = res.fetchone()
    
    if not row:
        return HTMLResponse("<div id='password-error' class='text-red-500 font-bold'>Usuario no encontrado.</div>")
        
    import json
    policy = {}
    if row[0]:
        policy = row[0]
        if isinstance(policy, str):
            policy = json.loads(policy)
            
    min_len = int(policy.get("min_length", 8))
    req_alpha = policy.get("require_alphanumeric", False)
    rot_days = int(policy.get("rotation_days", 0))
    
    if len(new_password) < min_len:
        return templates.TemplateResponse('component_4.html', {'request': request, 'min_len': min_len})
        
    if req_alpha:
        import string
        has_letter = any(c in string.ascii_letters for c in new_password)
        has_digit = any(c in string.digits for c in new_password)
        has_special = any(c in "!@#$%^&*" for c in new_password)
        if not (has_letter and has_digit and has_special):
            return HTMLResponse("<div id='password-error' class='text-red-500 font-bold'>Debe contener letras, nÃºmeros y al menos un sÃ­mbolo (!@#$%^&*).</div>")
            
    # Success! Update DB
    hashed = ph.hash(new_password)
    from datetime import datetime, timedelta
    
    expires_at = None
    if rot_days > 0:
        expires_at = datetime.utcnow() + timedelta(days=rot_days)
        
    query_update = text("""
        UPDATE users 
        SET hash_password = :hash_password, require_password_change = FALSE, password_expires_at = :expires_at
        WHERE id = :user_id
    """)
    
    await db.execute(query_update, {"hash_password": hashed, "expires_at": expires_at, "user_id": user_id})
    await db.commit()
    
    # Generate new session WITHOUT must_change_password flag
    session_data["must_change_password"] = False
    session_token = session_signer.dumps(session_data)
    
    response = HTMLResponse("<script>window.location.href = '/dashboard';</script>")
    response.set_cookie(
        key="sessionId",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=86400
    )
    return response
@router.get("/login")
async def redirect_login():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")


