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


@router.delete("/api/v1/rbac/users/{user_id}", response_class=HTMLResponse)
async def delete_user(
    user_id: str,
    session_data: dict = Depends(require_permission("usuarios:eliminar")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    actor_level = get_role_hierarchy(tenant_id, session_data["role_id"])
    
    # Check hierarchy
    query_target = text("SELECT r.hierarchy_level FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.id = :user_id AND u.tenant_id = :tenant_id")
    target_res = await db.execute(query_target, {"user_id": user_id, "tenant_id": tenant_id})
    target_row = target_res.fetchone()
    
    if not target_row or (target_row[0] and target_row[0] > actor_level):
        return HTMLResponse("<script>Swal.fire({icon: 'error', title: 'Acceso Denegado', text: 'No puedes eliminar a un usuario de nivel superior.'});</script>")
        
    try:
        await db.execute(text("DELETE FROM users WHERE id = :user_id AND tenant_id = :tenant_id"), {"user_id": user_id, "tenant_id": tenant_id})
        await db.commit()
        # Return empty so the user list reloads (or we can return a script to trigger reload-users)
        return HTMLResponse("<script>Swal.fire({icon: 'success', title: 'Eliminado', text: 'El usuario ha sido eliminado correctamente.'}); document.body.dispatchEvent(new Event('reload-users'));</script>")
    except Exception as e:
        await db.rollback()
        error_msg = str(e).lower()
        if 'foreign key constraint' in error_msg or 'violates foreign key' in error_msg:
            return HTMLResponse("<script>Swal.fire({icon: 'error', title: 'No se puede eliminar', text: 'Este usuario no se puede eliminar porque ya subió documentos o tiene movimientos registrados en las bases de datos. Por favor, desactiva la cuenta en su lugar.'});</script>")
        return HTMLResponse("<div class='p-4 text-red-500'>Ocurrió un error. Verifique los datos o permisos e intente nuevamente.</div>", status_code=400)

@router.post("/api/v1/rbac/users/{user_id}/expel")
async def expel_user(user_id: str, request: Request, session_data: dict = Depends(require_permission("usuarios:modificar")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    actor_level = get_role_hierarchy(tenant_id, session_data["role_id"])
    
    query = text("SELECT r.hierarchy_level FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.id = :uid AND u.tenant_id = :t")
    res = await db.execute(query, {"uid": user_id, "t": tenant_id})
    target_row = res.fetchone()
    if not target_row or (target_row[0] and target_row[0] > actor_level):
        return HTMLResponse("<script>alert('Operación denegada.')</script>")
        
    # Establecer expel_at a 30 segundos en el futuro
    await db.execute(text("UPDATE users SET expel_at = CURRENT_TIMESTAMP + INTERVAL '30 seconds' WHERE id = :uid"), {"uid": user_id})
    await db.commit()
    return HTMLResponse("<script>Swal.fire({toast:true, position:'top-end', icon:'success', title:'Usuario marcado para expulsión. Saldrá en 30s.', showConfirmButton:false, timer:3000}); htmx.trigger('body', 'reload-users');</script>")

@router.get("/api/v1/rbac/ui", response_class=HTMLResponse)
async def rbac_ui(request: Request, db: AsyncSession = Depends(get_db_session), csrf_protect: CsrfProtect = Depends()):
    cookie = request.cookies.get("sessionId")
    if not cookie:
        return HTMLResponse("No autorizado", status_code=401)
    
    try:
        session_data = session_signer.loads(cookie, max_age=86400)
    except Exception:
        return HTMLResponse("Sesión inválida", status_code=401)
        
    tenant_id = session_data.get("tenant_id")
    role_id = session_data.get("role_id")
    actor_level = get_role_hierarchy(tenant_id, role_id)
    
    if not check_permission(tenant_id, role_id, "usuarios:leer") and not check_permission(tenant_id, role_id, "roles:leer"):
        return HTMLResponse("<div class='text-red-500 font-bold'>Acceso Denegado. No tienes permisos para ver esta sección.</div>", status_code=200)

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    
    html = f'''
    <div x-data="{{ userModal: false, roleModal: false, groupModal: false }}" class="space-y-6">
        <h2 class="text-2xl font-bold text-gray-800">Administración de Accesos y Seguridad</h2>
        <p class="text-gray-500">Módulo central de auditoría y jerarquías (Topología de Bóveda de Datos).</p>
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-lg font-bold flex items-center gap-2"><span>👤</span> Usuarios</h3>
    '''
    
    if check_permission(tenant_id, role_id, "usuarios:crear"):
        html += '''<button @click="userModal = true" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">Nuevo Usuario</button>'''
        
    html += '''
                </div>
                <div id="users-list" hx-get="/api/v1/rbac/users/list" hx-trigger="load, reload-users from:body" class="min-h-[200px]">Cargando usuarios...</div>
            </div>
            
            <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-lg font-bold flex items-center gap-2"><span>🛡️</span> Roles de Seguridad</h3>
    '''
    
    if check_permission(tenant_id, role_id, "roles:crear"):
        html += '''<button @click="roleModal = true" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">Crear Rol</button>'''
        
    html += f'''
                </div>
                <div id="roles-list" hx-get="/api/v1/rbac/roles/list" hx-trigger="load, reload-roles from:body" class="min-h-[200px]">Cargando roles...</div>
            </div>
            
            <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-lg font-bold flex items-center gap-2"><span>🏢</span> Grupos de Trabajo</h3>
                    <button @click="groupModal = true; htmx.ajax('GET', '/api/v1/rbac/groups/new', {{target:'#group-edit-container'}})" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">Crear Grupo</button>
                </div>
                <div id="groups-list" hx-get="/api/v1/rbac/groups/list" hx-trigger="load, reload-groups from:body" class="min-h-[200px]">Cargando grupos...</div>
            </div>
        </div>
        
        <!-- MODAL EDITAR GRUPO -->
        <div x-show="groupModal" class="fixed inset-0 z-50 flex items-center justify-center" x-cloak>
            <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="groupModal = false" x-transition.opacity></div>
            <div class="bg-white p-8 rounded-3xl w-full max-w-4xl relative z-10 card-shadow"
                 x-transition:enter="transition ease-out duration-300"
                 x-transition:enter-start="opacity-0 scale-95"
                 x-transition:enter-end="opacity-100 scale-100">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="font-bold text-2xl text-textmain">Gestión de Grupo</h3>
                    <button @click="groupModal = false" class="text-gray-400 hover:text-red-500 transition-colors text-2xl font-bold">&times;</button>
                </div>
                <div id="group-edit-container" @edit-group.window="htmx.ajax('GET', '/api/v1/rbac/groups/' + $event.detail + '/edit', {{target:'#group-edit-container'}})">
                    <p class="text-gray-500 italic">Cargando...</p>
                </div>
            </div>
        </div>
        
        <!-- MODAL NUEVO USUARIO -->
        <div x-show="userModal" class="fixed inset-0 z-50 flex items-center justify-center" x-cloak>
            <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="userModal = false" x-transition.opacity></div>
            <div class="bg-white p-8 rounded-3xl w-full max-w-md relative z-10 card-shadow"
                 x-transition:enter="transition ease-out duration-300"
                 x-transition:enter-start="opacity-0 scale-95"
                 x-transition:enter-end="opacity-100 scale-100">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="font-bold text-2xl text-textmain">Crear Nuevo Usuario</h3>
                    <button @click="userModal = false" class="text-gray-400 hover:text-red-500 transition-colors text-2xl font-bold">&times;</button>
                </div>
                <form hx-post="/api/v1/rbac/users" hx-headers='{{"X-CSRF-Token": "{csrf_token}"}}' hx-target="#users-list" @htmx:after-request="if($event.detail.successful) userModal = false" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de Usuario / Correo</label>
                        <input type="text" name="username" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all" placeholder="ej. nombre@empresa.com">
                    </div>
                    
                    <div class="p-4 bg-blue-50 border border-blue-100 rounded-xl flex items-start gap-3">
                        <div class="text-blue-600 text-xl">🔒</div>
                        <div>
                            <h4 class="font-bold text-blue-900 text-sm">Generación Segura</h4>
                            <p class="text-xs text-blue-700">El sistema generará automáticamente una contraseña criptográficamente fuerte para este usuario y se mostrará al finalizar para que puedas copiarla y entregarla de forma segura.</p>
                        </div>
                    </div>
                    
                    <div x-data="{{ openPolicy: false }}" class="border border-gray-200 rounded-xl overflow-hidden mt-4">
                        <button type="button" @click="openPolicy = !openPolicy" class="w-full flex justify-between items-center bg-gray-50 p-4 font-bold text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                            <span>⚙️ Políticas Avanzadas de Identidad</span>
                            <span x-show="!openPolicy">+</span>
                            <span x-show="openPolicy">-</span>
                        </button>
                        <div x-show="openPolicy" class="p-4 space-y-4 bg-white" x-transition>
                            <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer border border-transparent hover:border-gray-200">
                                <input type="checkbox" name="require_password_change" value="true" class="mt-1 w-4 h-4 text-blue-600" checked>
                                <div>
                                    <div class="text-sm font-bold text-gray-800">Exigir Cambio al Primer Ingreso</div>
                                    <div class="text-xs text-gray-500">El usuario será forzado a establecer su propia contraseña la primera vez que inicie sesión.</div>
                                </div>
                            </label>
                            
                            <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer border border-transparent hover:border-gray-200">
                                <input type="checkbox" name="require_alphanumeric" value="true" class="mt-1 w-4 h-4 text-blue-600" checked>
                                <div>
                                    <div class="text-sm font-bold text-gray-800">Complejidad Alfanumérica Obligatoria</div>
                                    <div class="text-xs text-gray-500">La nueva contraseña deberá contener letras y números obligatoriamente.</div>
                                </div>
                            </label>

                            <div class="grid grid-cols-2 gap-4 mt-2">
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 mb-1">Longitud Mínima</label>
                                    <input type="number" name="min_length" value="8" min="4" max="32" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:border-blue-500 outline-none">
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 mb-1">Rotación (Días)</label>
                                    <input type="number" name="rotation_days" value="90" min="0" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:border-blue-500 outline-none">
                                    <div class="text-[10px] text-gray-400 mt-1">0 = Nunca expira</div>
                                </div>
                            </div>
                        </div>
                    </div>


                    <div class="bg-blue-50 p-4 rounded-xl border border-blue-100 mt-4">
                        <div class="font-bold text-blue-900 text-sm mb-2 flex items-center gap-2"><span>🕒</span> Ventana de Acceso Permitido</div>
                        <div class="grid grid-cols-2 gap-4" x-data="{{ start: '00:00', end: '23:59' }}">
                            <div>
                                <label class="block text-xs font-bold text-blue-800 mb-1">Hora Inicio</label>
                                <select name="access_time_start" x-model="start" class="w-full px-3 py-2 text-sm rounded-lg border border-blue-200 outline-none bg-white">
                                    <option value="00:00">00:00</option><option value="01:00">01:00</option><option value="02:00">02:00</option><option value="03:00">03:00</option><option value="04:00">04:00</option><option value="05:00">05:00</option><option value="06:00">06:00</option><option value="07:00">07:00</option><option value="08:00">08:00</option><option value="09:00">09:00</option><option value="10:00">10:00</option><option value="11:00">11:00</option><option value="12:00">12:00</option><option value="13:00">13:00</option><option value="14:00">14:00</option><option value="15:00">15:00</option><option value="16:00">16:00</option><option value="17:00">17:00</option><option value="18:00">18:00</option><option value="19:00">19:00</option><option value="20:00">20:00</option><option value="21:00">21:00</option><option value="22:00">22:00</option><option value="23:00">23:00</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-blue-800 mb-1">Hora Fin</label>
                                <select name="access_time_end" x-model="end" class="w-full px-3 py-2 text-sm rounded-lg border border-blue-200 outline-none bg-white">
                                    <option value="00:59">00:59</option><option value="01:59">01:59</option><option value="02:59">02:59</option><option value="03:59">03:59</option><option value="04:59">04:59</option><option value="05:59">05:59</option><option value="06:59">06:59</option><option value="07:59">07:59</option><option value="08:59">08:59</option><option value="09:59">09:59</option><option value="10:59">10:59</option><option value="11:59">11:59</option><option value="12:59">12:59</option><option value="13:59">13:59</option><option value="14:59">14:59</option><option value="15:59">15:59</option><option value="16:59">16:59</option><option value="17:59">17:59</option><option value="18:59">18:59</option><option value="19:59">19:59</option><option value="20:59">20:59</option><option value="21:59">21:59</option><option value="22:59">22:59</option><option value="23:59">23:59</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1 mt-4">Rol de Acceso</label>
                        <select name="role_id" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all">
                            <option value="" disabled selected>Seleccione un rol...</option>
    '''
    
    query_roles = text("SELECT id, name, hierarchy_level FROM roles WHERE tenant_id = :tenant_id AND hierarchy_level <= :actor_level ORDER BY hierarchy_level DESC")
    roles_result = await db.execute(query_roles, {"tenant_id": tenant_id, "actor_level": actor_level})
    for r in roles_result.fetchall():
        html += f'<option value="{r[0]}">{r[1]} (Lvl {r[2]})</option>'
        
    html += f'''
                        </select>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl transition-all shadow-lg shadow-blue-500/30">Guardar Usuario</button>
                </form>
            </div>
        </div>

        <!-- CONTENEDOR MODAL EDICIÓN -->
        <div id="edit-modal-container"></div>
        <!-- MODAL CREAR ROL -->
        <div x-show="roleModal" class="fixed inset-0 z-50 flex items-center justify-center" x-cloak>
            <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="roleModal = false" x-transition.opacity></div>
            <div class="bg-white p-8 rounded-3xl w-full max-w-2xl relative z-10 card-shadow max-h-[90vh] overflow-y-auto"
                 x-transition:enter="transition ease-out duration-300"
                 x-transition:enter-start="opacity-0 scale-95"
                 x-transition:enter-end="opacity-100 scale-100">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="font-bold text-2xl text-textmain">Crear Nuevo Rol</h3>
                    <button @click="roleModal = false" class="text-gray-400 hover:text-red-500 transition-colors text-2xl font-bold">&times;</button>
                </div>
                <form hx-post="/api/v1/rbac/roles" hx-headers='{{"X-CSRF-Token": "{csrf_token}"}}' hx-target="#roles-list" @htmx:after-request="if($event.detail.successful) roleModal = false" class="space-y-6">
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Perfil</label>
                            <input type="text" name="name" placeholder="Ej. Auditor Financiero" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Nivel de Jerarquía (1-{actor_level})</label>
                            <input type="number" name="hierarchy_level" min="1" max="{actor_level}" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all">
                        </div>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-3">Matriz de Permisos (Catálogo Global)</label>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 bg-gray-50 p-4 rounded-xl border border-gray-100">
    '''
    
    query_perms = text("SELECT id, name, description FROM permissions ORDER BY name ASC")
    perms_result = await db.execute(query_perms)
    for p in perms_result.fetchall():
        p_id = str(p[0])
        p_name = p[1]
        p_desc = p[2]
        
        has_perm = (actor_level == 99) or check_permission(tenant_id, role_id, p_name)
        disabled_attr = "" if has_perm else "disabled opacity-50 cursor-not-allowed"
        locked_icon = "" if has_perm else "🔒 "
        
        html += f'''
                            <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors {disabled_attr}">
                                <input type="checkbox" name="permissions" value="{p_id}" class="mt-1 w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" {disabled_attr}>
                                <div>
                                    <div class="text-sm font-bold text-gray-800">{locked_icon}{p_name}</div>
                                    <div class="text-xs text-gray-500">{p_desc}</div>
                                </div>
                            </label>
        '''
        
    html += '''
                        </div>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl transition-all shadow-lg shadow-blue-500/30">Guardar Rol y Compilar Matriz</button>
                </form>
            </div>
        </div>
    </div>
    '''
    response = HTMLResponse(content=html)
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response

@router.get("/api/v1/rbac/users/list", response_class=HTMLResponse)
async def rbac_users_list(request: Request, session_data: dict = Depends(require_permission("usuarios:leer")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    actor_role_id = session_data["role_id"]
    
    query = text("""
        SELECT u.id, u.username, u.is_active, r.name, r.hierarchy_level, r.id as target_role_id, u.last_login_at
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.tenant_id = :tenant_id
        ORDER BY r.hierarchy_level DESC, u.username ASC
    """)
    result = await db.execute(query, {"tenant_id": tenant_id})
    users = result.fetchall()
    
    can_modify = check_permission(tenant_id, actor_role_id, "usuarios:modificar")
    can_delete = check_permission(tenant_id, actor_role_id, "usuarios:eliminar")
    actor_level = get_role_hierarchy(tenant_id, actor_role_id)
    
    html = '<div class="space-y-3">'
    for u in users:
        target_level = u[4] if u[4] else 0
        is_modifiable = actor_level >= target_level # Regla relajada para SuperAdmins: Nivel mayor puede modificar a nivel menor.
        
        status_color = "bg-green-100 text-green-700" if u[2] else "bg-red-100 text-red-700"
        status_text = "Activo" if u[2] else "Inactivo"
        
        last_login_text = ""
        is_online = False
        if u[6]:
            last_login_text = f"<span class='text-xs text-gray-500'>Ingreso: {u[6].strftime('%H:%M')}</span>"
            from datetime import datetime, timezone
            
            now_utc = datetime.now(timezone.utc)
            if u[6].tzinfo is None:
                u6_utc = u[6].replace(tzinfo=timezone.utc)
            else:
                u6_utc = u[6]
                
            delta_seconds = (now_utc - u6_utc).total_seconds()
            
            # Si delta es negativo o menor a 12 horas (43200s), está online
            if -86400 < delta_seconds < 43200:
                is_online = True
                
        online_badge = "<span class='text-xs font-bold text-green-600 flex items-center gap-1'><span class='w-2 h-2 rounded-full bg-green-500 animate-pulse'></span>Online</span>" if is_online else ""
        
        html += f'''
        <div class="flex flex-col xl:flex-row items-start xl:items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100 gap-4">
            <div class="flex-1 w-full min-w-0">
                <div class="font-bold text-gray-800 flex items-center gap-2">{u[1]} {online_badge}</div>
                <div class="flex gap-2 items-center mt-1">
                    <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">{u[3] or 'Sin Rol'} (Lvl {target_level})</span>
                    <span class="text-xs font-semibold px-2 py-0.5 rounded-full {status_color}">{status_text}</span>
                    {last_login_text}
                </div>
            </div>
        '''
        
        # Zero Trust Actions
        actions_html = ""
        if can_modify and is_modifiable:
            actions_html += f'<button hx-get="/api/v1/rbac/users/{u[0]}/edit" hx-target="#edit-modal-container" class="text-blue-500 hover:text-blue-700 text-sm font-medium">Modificar</button>'
        if can_delete and is_modifiable:
            actions_html += f'<button onclick="alert(\'Módulo de eliminación en desarrollo (Fase 4)\')" class="text-red-500 hover:text-red-700 text-sm font-medium">Eliminar</button>'
        if is_modifiable and is_online and str(u[0]) != session_data.get("user_id"):
            actions_html += f'<button hx-post="/api/v1/rbac/users/{u[0]}/expel" hx-swap="beforeend" hx-target="body" hx-confirm="⚠️ ¿Estás seguro que deseas EXPULSAR a este usuario? Perderá todo su trabajo no guardado en 30 segundos." class="text-red-600 hover:text-red-800 text-sm font-bold flex items-center gap-1"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg> Expulsar</button>'
            
        if actions_html:
            html += f'<div class="flex flex-wrap gap-2 xl:gap-3 justify-end w-full xl:w-auto">{actions_html}</div>'
            
        html += '</div>'
        
    html += '</div>'
    return HTMLResponse(content=html)

@router.get("/api/v1/rbac/roles/list", response_class=HTMLResponse)
async def rbac_roles_list(request: Request, session_data: dict = Depends(require_permission("roles:leer")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    actor_role_id = session_data["role_id"]
    
    query = text("""
        SELECT r.id, r.name, r.hierarchy_level, COUNT(u.id) as user_count
        FROM roles r
        LEFT JOIN users u ON r.id = u.role_id
        WHERE r.tenant_id = :tenant_id
        GROUP BY r.id
        ORDER BY r.hierarchy_level DESC
    """)
    result = await db.execute(query, {"tenant_id": tenant_id})
    roles = result.fetchall()
    
    actor_level = get_role_hierarchy(tenant_id, actor_role_id)
    can_modify = check_permission(tenant_id, actor_role_id, "roles:modificar")
    
    html = '<div class="space-y-3">'
    for r in roles:
        target_level = r[2]
        is_modifiable = actor_level >= target_level
        
        html += f'''
        <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
            <div class="flex justify-between items-center mb-2">
                <div class="font-bold text-gray-800 flex items-center gap-2">
                    {r[1]} <span class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">Lvl {r[2]}</span>
                </div>
        '''
        
        if can_modify and is_modifiable:
            html += f'<button hx-get="/api/v1/rbac/roles/{r[0]}/edit" hx-target="#edit-modal-container" class="text-blue-500 hover:text-blue-700 text-sm font-medium">Editar Rol</button>'
            
        html += f'''
            </div>
            <div class="text-sm text-gray-500">{r[3]} usuarios asignados a este rol.</div>
        </div>
        '''
        
    html += '</div>'
    return HTMLResponse(content=html)

@router.post("/api/v1/rbac/users", response_class=HTMLResponse)
async def create_user(
    request: Request,
    username: str = Form(...),
    role_id: str = Form(...),
    require_password_change: bool = Form(False),
    min_length: int = Form(8),
    require_alphanumeric: bool = Form(False),
    rotation_days: int = Form(0),
    access_time_start: str = Form("00:00"),
    access_time_end: str = Form("23:59"),
    mfa_enabled: bool = Form(False),
    session_data: dict = Depends(require_permission("usuarios:crear")),
    db: AsyncSession = Depends(get_db_session),
    ):
    pass # CSRF ya está mitigado por samesite=strict en la cookie sessionId
    
    tenant_id = session_data["tenant_id"]
    actor_role_id = session_data["role_id"]
    actor_level = get_role_hierarchy(tenant_id, actor_role_id)
    
    # Validation: target role must exist and be <= actor_level
    query_role = text("SELECT hierarchy_level FROM roles WHERE id = :role_id AND tenant_id = :tenant_id")
    result = await db.execute(query_role, {"role_id": role_id, "tenant_id": tenant_id})
    row = result.fetchone()
    if not row:
        return HTMLResponse("<div class='text-red-500'>Rol inválido.</div>", status_code=200)
        
    target_level = row[0]
    if target_level > actor_level:
        return HTMLResponse("<div class='text-red-500'>No puedes asignar un rol superior al tuyo.</div>", status_code=200)
        
    # Unique constraint check
    query_check = text("SELECT id FROM users WHERE username = :username AND tenant_id = :tenant_id")
    if (await db.execute(query_check, {"username": username, "tenant_id": tenant_id})).fetchone():
        return HTMLResponse("<div class='text-red-500'>El nombre de usuario ya existe en este inquilino.</div>", status_code=200)
        
    # Generar contraseña automática fuerte
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
    hashed_password = ph.hash(generated_password)
    
    import json
    from datetime import datetime, timedelta
    
    policy = {
        "min_length": min_length,
        "require_alphanumeric": require_alphanumeric,
        "rotation_days": rotation_days
    }
    
    # Calcular fecha de expiración inicial si hay días de rotación
    expires_at = None
    if rotation_days > 0:
        expires_at = datetime.utcnow() + timedelta(days=rotation_days)
    
    query_insert = text("""
        INSERT INTO users (tenant_id, username, hash_password, role_id, require_password_change, password_policy, password_expires_at)
        VALUES (:tenant_id, :username, :hash_password, :role_id, :require_password_change, :password_policy, :password_expires_at)
        RETURNING id
    """)
    
    try:
        res = await db.execute(query_insert, {
            "tenant_id": tenant_id,
            "username": username,
            "hash_password": hashed_password,
            "role_id": role_id,
            "require_password_change": require_password_change,
            "password_policy": json.dumps(policy),
            "password_expires_at": expires_at
        })
        new_user_id = str(res.fetchone()[0])
        await log_audit_action(db, tenant_id, session_data["user_id"], "CREATE_USER", new_user_id, {"username": username, "role_id": role_id})
        await db.commit()
    except Exception as e:
        await db.rollback()
        return HTMLResponse("<div class='p-4 text-red-500'>Ocurrió un error. Verifique los datos o permisos e intente nuevamente.</div>", status_code=400)
        
    # Devolver una alerta visual con la contraseña copiable
    # Como el hx-target es #users-list, enviaremos la alerta por OOB a un div de notificaciones y recargaremos la tabla
    response_html = f'''
    <div id="password-alert-container" hx-swap-oob="beforeend">
        <div x-data="{{ show: true }}" x-show="show" class="fixed top-4 right-4 bg-green-50 border border-green-200 text-green-800 p-6 rounded-xl shadow-2xl z-[9999] max-w-md" x-transition>
            <div class="flex justify-between items-start mb-2">
                <h4 class="font-bold text-lg">✅ Usuario Creado Exitosamente</h4>
                <button @click="show = false" class="text-green-600 hover:text-green-800 font-bold">&times;</button>
            </div>
            <p class="mb-4 text-sm">El sistema ha generado una clave inicial de alta entropía. Cópiala y envíala de forma segura al empleado:</p>
            <div class="bg-white border border-green-200 p-3 rounded-lg flex items-center justify-between">
                <code class="font-mono text-lg font-bold select-all tracking-wider text-black">{generated_password}</code>
            </div>
            <p class="mt-4 text-xs text-green-600">⚠ Esta clave nunca más podrá ser vista. El usuario {"deberá" if require_password_change else "podrá"} cambiarla al ingresar.</p>
        </div>
    </div>
    '''
    response = HTMLResponse(content=response_html)
    response.headers["HX-Trigger"] = "reload-users"
    return response

@router.post("/api/v1/rbac/roles", response_class=HTMLResponse)
async def create_role(
    request: Request,
    name: str = Form(...),
    hierarchy_level: int = Form(...),
    permissions: list[str] = Form(default=[]),
    session_data: dict = Depends(require_permission("roles:crear")),
    db: AsyncSession = Depends(get_db_session),
    ):
    pass # CSRF ya está mitigado por samesite=strict en la cookie sessionId
    
    tenant_id = session_data["tenant_id"]
    actor_role_id = session_data["role_id"]
    actor_level = get_role_hierarchy(tenant_id, actor_role_id)
    
    # 1. Validation: Hierarchy block
    if hierarchy_level > actor_level:
        return HTMLResponse("<div class='p-4 text-red-500'>Ocurrió un error. Verifique los datos o permisos e intente nuevamente.</div>", status_code=400)
        
    # 2. Validation: Permissions Governance (Zero Trust)
    # Check if the actor actually has all the requested permissions
    if permissions:
        query_check_perms = text("SELECT id, name FROM permissions WHERE id = ANY(:perms)")
        res = await db.execute(query_check_perms, {"perms": permissions})
        for p_id, p_name in res.fetchall():
            if not ((actor_level == 99) or check_permission(tenant_id, actor_role_id, p_name)):
                return HTMLResponse(f"<div class='p-4 text-red-500'>Error de Seguridad: No posees el permiso {p_name}.</div>", status_code=403)
                
    try:
        # Atomic Transaction
        query_insert_role = text("""
            INSERT INTO roles (tenant_id, name, hierarchy_level)
            VALUES (:tenant_id, :name, :hierarchy_level)
            RETURNING id
        """)
        res = await db.execute(query_insert_role, {
            "tenant_id": tenant_id,
            "name": name,
            "hierarchy_level": hierarchy_level
        })
        new_role_id = str(res.fetchone()[0])
        
        if permissions:
            for p_id in permissions:
                query_insert_perm = text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)")
                await db.execute(query_insert_perm, {"role_id": new_role_id, "permission_id": p_id})
                
        await log_audit_action(db, tenant_id, session_data["user_id"], "CREATE_ROLE", new_role_id, {"name": name, "hierarchy_level": hierarchy_level, "permissions": permissions})
        await db.commit()
        
        # Purge L1 Cache (Reload)
        from app import rbac
        await rbac.load_rbac_cache(db)
        
    except Exception as e:
        await db.rollback()
        import traceback; traceback.print_exc(); return HTMLResponse("<div class='p-4 text-red-500'>Ocurrió un error. Verifique los datos o permisos e intente nuevamente.</div>", status_code=400)
        
    response = HTMLResponse("")
    response.headers["HX-Trigger"] = "reload-roles"
    return response

@router.get("/api/v1/rbac/users/{user_id}/edit", response_class=HTMLResponse)
async def get_edit_user(user_id: str, request: Request, session_data: dict = Depends(require_permission("usuarios:modificar")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    actor_level = get_role_hierarchy(tenant_id, session_data["role_id"])
    
    query = text("SELECT u.id, u.username, u.is_active, u.role_id, r.hierarchy_level, u.access_time_start, u.access_time_end, u.require_password_change, u.password_policy, u.mfa_enabled FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.id = :user_id AND u.tenant_id = :tenant_id")
    res = await db.execute(query, {"user_id": user_id, "tenant_id": tenant_id})
    user = res.fetchone()
    
    if not user:
        return HTMLResponse("<div class='text-red-500'>Usuario no encontrado.</div>")
        
    target_level = user[4] if user[4] else 0
    if target_level > actor_level:
        return HTMLResponse("<div class='text-red-500'>No puedes modificar a un usuario de nivel superior.</div>")
        
    query_roles = text("SELECT id, name, hierarchy_level FROM roles WHERE tenant_id = :tenant_id AND hierarchy_level <= :actor_level ORDER BY hierarchy_level DESC")
    roles_res = await db.execute(query_roles, {"tenant_id": tenant_id, "actor_level": actor_level})
    roles = roles_res.fetchall()
    
    options = ""
    for r in roles:
        selected = "selected" if str(r[0]) == str(user[3]) else ""
        options += f'<option value="{r[0]}" {selected}>{r[1]} (Lvl {r[2]})</option>'
        
    active_checked = "checked" if user[2] else ""
    t_start = user[5].strftime('%H:%M') if user[5] else ""
    t_end = user[6].strftime('%H:%M') if user[6] else ""
    
    req_change = "checked" if user[7] else ""
    policy = user[8] if user[8] else {}
    req_alpha = "checked" if policy.get("require_alphanumeric", False) else ""
    min_len = policy.get("min_length", 8)
    rot_days = policy.get("rotation_days", 90)
    mfa_checked = "checked" if len(user) > 9 and user[9] else ""
    
    html = f'''
    <div x-data="{{ editModal: true, openPolicy: false }}" x-show="editModal" class="fixed inset-0 z-50 flex items-center justify-center" x-cloak>
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="editModal = false" x-transition.opacity></div>
        <div class="bg-white p-8 rounded-3xl w-full max-w-md relative z-10 card-shadow max-h-[90vh] overflow-y-auto"
             x-transition:enter-start="opacity-0 scale-95"
             x-transition:enter-end="opacity-100 scale-100">
            <div class="flex justify-between items-center mb-6">
                <h3 class="font-bold text-2xl text-textmain">Editar Usuario</h3>
                <button type="button" @click="editModal = false" class="text-gray-400 hover:text-red-500 transition-colors text-2xl font-bold">&times;</button>
            </div>
            <form hx-post="/api/v1/rbac/users/{user[0]}/edit" hx-target="#users-list" @htmx:after-request="if($event.detail.successful) editModal = false" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de Usuario</label>
                    <input type="text" name="username" value="{user[1]}" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Rol de Acceso</label>
                    <select name="role_id" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 outline-none">
                        {options}
                    </select>
                </div>
                <div class="bg-gray-50 p-4 rounded-xl border border-gray-200">
                    <label class="flex items-center gap-3 cursor-pointer">
                        <input type="checkbox" name="is_active" value="true" class="w-5 h-5 text-blue-600 rounded border-gray-300" {active_checked}>
                        <div class="flex flex-col">
                            <span class="font-bold text-gray-800 text-sm">Usuario Activo</span>
                            <span class="text-xs text-gray-500">Si se desmarca, el usuario no podrá iniciar sesión.</span>
                        </div>
                    </label>
                </div>
                
                <div class="bg-blue-50 p-4 rounded-xl border border-blue-100">
                    <div class="font-bold text-blue-900 text-sm mb-2 flex items-center gap-2"><span>🕒</span> Ventana de Acceso Permitido</div>
                    <div class="text-xs text-blue-700 mb-3">Deja ambos en blanco para permitir acceso 24h.</div>
                    <div class="grid grid-cols-2 gap-4" x-data="{{ start: '{t_start}' || '00:00', end: '{t_end}' || '23:59' }}">
                        <div>
                            <label class="block text-xs font-bold text-blue-800 mb-1">Hora Inicio</label>
                            <select name="access_time_start" x-model="start" class="w-full px-3 py-2 text-sm rounded-lg border border-blue-200 outline-none bg-white">
                                <option value="00:00">00:00</option><option value="01:00">01:00</option><option value="02:00">02:00</option><option value="03:00">03:00</option><option value="04:00">04:00</option><option value="05:00">05:00</option><option value="06:00">06:00</option><option value="07:00">07:00</option><option value="08:00">08:00</option><option value="09:00">09:00</option><option value="10:00">10:00</option><option value="11:00">11:00</option><option value="12:00">12:00</option><option value="13:00">13:00</option><option value="14:00">14:00</option><option value="15:00">15:00</option><option value="16:00">16:00</option><option value="17:00">17:00</option><option value="18:00">18:00</option><option value="19:00">19:00</option><option value="20:00">20:00</option><option value="21:00">21:00</option><option value="22:00">22:00</option><option value="23:00">23:00</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-blue-800 mb-1">Hora Fin</label>
                            <select name="access_time_end" x-model="end" class="w-full px-3 py-2 text-sm rounded-lg border border-blue-200 outline-none bg-white">
                                <option value="00:59">00:59</option><option value="01:59">01:59</option><option value="02:59">02:59</option><option value="03:59">03:59</option><option value="04:59">04:59</option><option value="05:59">05:59</option><option value="06:59">06:59</option><option value="07:59">07:59</option><option value="08:59">08:59</option><option value="09:59">09:59</option><option value="10:59">10:59</option><option value="11:59">11:59</option><option value="12:59">12:59</option><option value="13:59">13:59</option><option value="14:59">14:59</option><option value="15:59">15:59</option><option value="16:59">16:59</option><option value="17:59">17:59</option><option value="18:59">18:59</option><option value="19:59">19:59</option><option value="20:59">20:59</option><option value="21:59">21:59</option><option value="22:59">22:59</option><option value="23:59">23:59</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="border border-gray-200 rounded-xl overflow-hidden mt-4">
                    <button type="button" @click="openPolicy = !openPolicy" class="w-full flex justify-between items-center bg-gray-50 p-4 font-bold text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                        <span>⚙️ Políticas de Identidad</span>
                        <span x-show="!openPolicy">+</span>
                        <span x-show="openPolicy">-</span>
                    </button>
                    <div x-show="openPolicy" class="p-4 space-y-4 bg-white">
                        
                        
                        
                        <label class="flex items-start gap-3 p-2 rounded-lg bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 transition-colors cursor-pointer">
                            <input type="checkbox" name="mfa_enabled" value="true" class="mt-1 w-4 h-4 text-indigo-600" {mfa_checked}>
                            <div>
                                <div class="text-sm font-bold text-indigo-800">Autenticación de Dos Factores (2FA)</div>
                                <div class="text-xs text-indigo-700">Obliga al usuario a usar Google Authenticator.</div>
                            </div>
                        </label>
                        
                        <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
                            <input type="checkbox" name="require_password_change" value="true" class="mt-1 w-4 h-4 text-blue-600" {req_change}>
                            <div>
                                <div class="text-sm font-bold text-gray-800">Exigir Cambio al Siguiente Ingreso</div>
                            </div>
                        </label>
                        
                        <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
                            <input type="checkbox" name="require_alphanumeric" value="true" class="mt-1 w-4 h-4 text-blue-600" {req_alpha}>
                            <div>
                                <div class="text-sm font-bold text-gray-800">Complejidad Alfanumérica Obligatoria</div>
                            </div>
                        </label>

                        <div class="grid grid-cols-2 gap-4 mt-2">
                            <div>
                                <label class="block text-xs font-bold text-gray-700 mb-1">Longitud Mínima</label>
                                <input type="number" name="min_length" value="{min_len}" min="4" max="32" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 outline-none">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-700 mb-1">Rotación (Días)</label>
                                <input type="number" name="rotation_days" value="{rot_days}" min="0" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 outline-none">
                            </div>
                        </div>
                    </div>
                </div>

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-500/30">Guardar Cambios</button>
            </form>
        </div>
    </div>
    '''
    return HTMLResponse(content=html)

@router.post("/api/v1/rbac/users/{user_id}/edit", response_class=HTMLResponse)
async def post_edit_user(
    user_id: str,
    request: Request,
    username: str = Form(...),
    role_id: str = Form(...),
    is_active: bool = Form(False),
    access_time_start: str = Form(""),
    access_time_end: str = Form(""),
    
    require_password_change: bool = Form(False),
    require_alphanumeric: bool = Form(False),
    min_length: int = Form(8),
    rotation_days: int = Form(0),
    mfa_enabled: bool = Form(False),
    session_data: dict = Depends(require_permission("usuarios:modificar")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    actor_role_id = session_data["role_id"]
    actor_level = get_role_hierarchy(tenant_id, actor_role_id)
    
    query_target = text("SELECT r.hierarchy_level FROM users u LEFT JOIN roles r ON u.role_id = r.id WHERE u.id = :user_id AND u.tenant_id = :tenant_id")
    target_res = await db.execute(query_target, {"user_id": user_id, "tenant_id": tenant_id})
    target_row = target_res.fetchone()
    
    if not target_row or (target_row[0] and target_row[0] > actor_level):
        return HTMLResponse("<div class='text-red-500'>Operación denegada.</div>")
        
    try:
        from datetime import datetime
        t_start = datetime.strptime(access_time_start, "%H:%M").time() if access_time_start else None
        t_end = datetime.strptime(access_time_end, "%H:%M").time() if access_time_end else None
    except Exception:
        t_start = None
        t_end = None
        
    import json
    policy = {
        "min_length": min_length,
        "require_alphanumeric": require_alphanumeric,
        "rotation_days": rotation_days
    }
    
    # Si se desactiva el MFA, limpiamos el mfa_secret para que deba configurarlo de nuevo al reactivarse.
    if not mfa_enabled:
        query_update = text("UPDATE users SET username = :username, role_id = :role_id, is_active = :is_active, access_time_start = :t_start, access_time_end = :t_end, require_password_change = :rpc, password_policy = :policy, mfa_enabled = false, mfa_secret = NULL, mfa_verified = false WHERE id = :user_id")
    else:
        query_update = text("UPDATE users SET username = :username, role_id = :role_id, is_active = :is_active, access_time_start = :t_start, access_time_end = :t_end, require_password_change = :rpc, password_policy = :policy, mfa_enabled = true WHERE id = :user_id")
        
    await db.execute(query_update, {"username": username, "role_id": role_id, "is_active": is_active, "t_start": t_start, "t_end": t_end, "rpc": require_password_change, "policy": json.dumps(policy), "user_id": user_id})
    await db.commit()
    from app import rbac
    await rbac.load_rbac_cache(db)
    return HTMLResponse("")

@router.get("/api/v1/rbac/roles/{role_id}/edit", response_class=HTMLResponse)
async def get_edit_role(role_id: str, request: Request, session_data: dict = Depends(require_permission("roles:modificar")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    actor_level = get_role_hierarchy(tenant_id, session_data["role_id"])
    
    query = text("SELECT id, name, hierarchy_level FROM roles WHERE id = :role_id AND tenant_id = :tenant_id")
    res = await db.execute(query, {"role_id": role_id, "tenant_id": tenant_id})
    role = res.fetchone()
    
    if not role:
        return HTMLResponse("<div class='text-red-500'>Rol no encontrado.</div>")
        
    target_level = role[2]
    if target_level > actor_level:
        return HTMLResponse("<div class='text-red-500'>No puedes modificar un rol de jerarquía superior.</div>")
        
    query_perms = text("SELECT p.id, p.name, p.description, rp.role_id FROM permissions p LEFT JOIN role_permissions rp ON p.id = rp.permission_id AND rp.role_id = :role_id ORDER BY p.name")
    perms_res = await db.execute(query_perms, {"role_id": role_id})
    permissions = perms_res.fetchall()
    
    perms_html = ""
    for p in permissions:
        p_id = str(p[0])
        p_name = p[1]
        p_desc = p[2]
        is_assigned = p[3] is not None
        
        has_perm = (actor_level == 99) or check_permission(tenant_id, session_data["role_id"], p_name)
        disabled_attr = "" if has_perm else "disabled opacity-50 cursor-not-allowed"
        locked_icon = "" if has_perm else "🔒 "
        checked_attr = "checked" if is_assigned else ""
        
        perms_html += f'''
        <label class="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors {disabled_attr}">
            <input type="checkbox" name="permissions" value="{p_id}" class="mt-1 w-4 h-4 text-blue-600" {checked_attr} {disabled_attr}>
            <div>
                <div class="text-sm font-bold text-gray-800">{locked_icon}{p_name}</div>
                <div class="text-xs text-gray-500">{p_desc}</div>
            </div>
        </label>
        '''
        
    html = f'''
    <div x-data="{{ editRoleModal: true }}" x-show="editRoleModal" class="fixed inset-0 z-50 flex items-center justify-center" x-cloak>
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="editRoleModal = false" x-transition.opacity></div>
        <div class="bg-white p-8 rounded-3xl w-full max-w-2xl relative z-10 card-shadow max-h-[90vh] overflow-y-auto"
             x-transition:enter-start="opacity-0 scale-95"
             x-transition:enter-end="opacity-100 scale-100">
            <div class="flex justify-between items-center mb-6">
                <h3 class="font-bold text-2xl text-textmain">Editar Rol</h3>
                <button @click="editRoleModal = false" class="text-gray-400 hover:text-red-500 transition-colors text-2xl font-bold">&times;</button>
            </div>
            <form hx-post="/api/v1/rbac/roles/{role_id}/edit" hx-target="#roles-list" @htmx:after-request="if($event.detail.successful) editRoleModal = false" class="space-y-6">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Perfil</label>
                        <input type="text" name="name" value="{role[1]}" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 outline-none">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nivel de Jerarquía (1-{actor_level-1})</label>
                        <input type="number" name="hierarchy_level" value="{role[2]}" min="1" max="{actor_level-1}" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 outline-none">
                    </div>
                </div>
                <div>
                    <h4 class="font-bold text-gray-800 mb-3 border-b pb-2">Matriz de Permisos</h4>
                    <div class="grid grid-cols-2 gap-2 max-h-[300px] overflow-y-auto bg-gray-50 p-4 rounded-xl border border-gray-200">
                        {perms_html}
                    </div>
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-500/30">Guardar Cambios del Rol</button>
            </form>
        </div>
    </div>
    '''
    return HTMLResponse(content=html)

@router.post("/api/v1/rbac/roles/{role_id}/edit", response_class=HTMLResponse)
async def post_edit_role(
    role_id: str,
    request: Request,
    name: str = Form(...),
    hierarchy_level: int = Form(...),
    permissions: list[str] = Form(default=[]),
    session_data: dict = Depends(require_permission("roles:modificar")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    actor_level = get_role_hierarchy(tenant_id, session_data["role_id"])
    
    # 1. Val target role < actor_level
    query_target = text("SELECT hierarchy_level FROM roles WHERE id = :role_id AND tenant_id = :tenant_id")
    target_res = await db.execute(query_target, {"role_id": role_id, "tenant_id": tenant_id})
    target_row = target_res.fetchone()
    
    if not target_row or target_row[0] > actor_level:
        return HTMLResponse("<div class='text-red-500'>Operación denegada.</div>")
        
    if hierarchy_level > actor_level:
        return HTMLResponse("<div class='text-red-500'>No puedes elevar la jerarquía por encima de tu propio rol.</div>")
        
    # Zero Trust: Check assigned permissions are held by actor
    query_all_perms = text("SELECT id, name FROM permissions")
    all_perms_res = await db.execute(query_all_perms)
    perm_map = {str(row[0]): row[1] for row in all_perms_res.fetchall()}
    
    for p_id in permissions:
        p_name = perm_map.get(p_id)
        if p_name and not ((actor_level == 99) or check_permission(tenant_id, session_data["role_id"], p_name)):
            return HTMLResponse(f"<div class='p-4 text-red-500'>Error de Seguridad: No posees el permiso {p_name}.</div>", status_code=403)

    try:
        query_update = text("UPDATE roles SET name = :name, hierarchy_level = :hierarchy_level WHERE id = :role_id AND tenant_id = :tenant_id")
        await db.execute(query_update, {"name": name, "hierarchy_level": hierarchy_level, "role_id": role_id, "tenant_id": tenant_id})
        
        # Clear old permissions and insert new
        await db.execute(text("DELETE FROM role_permissions WHERE role_id = :role_id"), {"role_id": role_id})
        for p_id in permissions:
            await db.execute(text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)"), {"role_id": role_id, "permission_id": p_id})
            
        await log_audit_action(db, tenant_id, session_data["user_id"], "UPDATE_ROLE", role_id, {"name": name, "hierarchy_level": hierarchy_level, "permissions": permissions})
        await db.commit()
        from app import rbac
        await rbac.load_rbac_cache(db)
    except Exception as e:
        await db.rollback()
        import traceback; traceback.print_exc()
        return HTMLResponse("<div class='p-4 text-red-500'>Ocurrió un error. Verifique los datos o permisos e intente nuevamente.</div>", status_code=400)
        
    response = HTMLResponse("")
    response.headers["HX-Trigger"] = "reload-roles"
    return response

@router.get("/api/v1/rbac/groups/list", response_class=HTMLResponse)
async def list_groups(request: Request, session_data: dict = Depends(require_permission("roles:leer")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    query = text("""
        SELECT g.id, g.name, r.name as role_name, COUNT(ug.user_id) as user_count 
        FROM groups g 
        LEFT JOIN roles r ON g.role_id = r.id 
        LEFT JOIN user_groups ug ON g.id = ug.group_id 
        WHERE g.tenant_id = :tenant_id
        GROUP BY g.id, g.name, r.name
        ORDER BY g.name ASC
    """)
    res = await db.execute(query, {"tenant_id": tenant_id})
    
    html = '<div class="space-y-4">'
    for row in res.fetchall():
        g_id, g_name, role_name, count = row
        role_badge = f'<span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded ml-2">{role_name}</span>' if role_name else ''
        html += f"""
        <div class="p-4 border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors flex flex-col gap-2">
            <div class="flex justify-between items-start">
                <div class="flex items-center">
                    <h4 class="font-bold text-gray-800">{g_name}</h4>
                    {role_badge}
                </div>
                <div class="flex items-center gap-3">
                    <button @click="groupModal = true; $dispatch('edit-group', '{g_id}')" class="text-sm font-medium text-blue-600 hover:text-blue-800">Editar Grupo</button>
                </div>
            </div>
            <p class="text-xs text-gray-500">{count} usuarios asignados a este grupo.</p>
        </div>
        """
    html += '</div>'
    return HTMLResponse(content=html)

@router.get("/api/v1/rbac/groups/{group_id}/edit", response_class=HTMLResponse)
async def get_edit_group(group_id: str, request: Request, session_data: dict = Depends(require_permission("roles:modificar")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    actor_level = get_role_hierarchy(tenant_id, session_data["role_id"])
    
    g_res = await db.execute(text("SELECT name, role_id FROM groups WHERE id = :id AND tenant_id = :t"), {"id": group_id, "t": tenant_id})
    g_row = g_res.fetchone()
    if not g_row: return HTMLResponse("Grupo no encontrado")
    g_name, g_role_id = g_row
    
    r_res = await db.execute(text("SELECT id, name FROM roles WHERE tenant_id = :t AND hierarchy_level <= :lvl"), {"t": tenant_id, "lvl": actor_level})
    roles = r_res.fetchall()
    role_opts = '<option value="">Sin Rol</option>'
    for r in roles:
        sel = "selected" if str(r[0]) == str(g_role_id) else ""
        role_opts += f'<option value="{r[0]}" {sel}>{r[1]}</option>'
        
    u_res = await db.execute(text("SELECT id, username FROM users WHERE tenant_id = :t"), {"t": tenant_id})
    all_users = {str(u[0]): u[1] for u in u_res.fetchall()}
    
    ug_res = await db.execute(text("SELECT user_id FROM user_groups WHERE group_id = :id"), {"id": group_id})
    in_group = {str(ug[0]) for ug in ug_res.fetchall()}
    
    avail_users = [u for uid, u in all_users.items() if uid not in in_group]
    curr_users = [u for uid, u in all_users.items() if uid in in_group]
    
    import json
    
    html = f"""
    <form hx-post="/api/v1/rbac/groups/{group_id}/edit" hx-target="#groups-list" hx-swap="innerHTML" @submit="groupModal = false" class="space-y-6">
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Nombre del Grupo</label>
            <input type="text" name="name" value="{g_name}" required class="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none">
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Rol Heredado</label>
            <select name="role_id" class="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none">
                {role_opts}
            </select>
        </div>
        
        <div x-data='{{ 
            avail: {json.dumps(avail_users)}, 
            curr: {json.dumps(curr_users)},
            moveToCurr(u) {{ this.avail = this.avail.filter(x => x !== u); this.curr.push(u); }},
            moveToAvail(u) {{ this.curr = this.curr.filter(x => x !== u); this.avail.push(u); }}
        }}' class="grid grid-cols-2 gap-4">
            <template x-for="u in curr">
                <input type="hidden" name="user_usernames" :value="u">
            </template>
            <div class="border rounded-lg p-4 bg-gray-50">
                <h4 class="text-sm font-bold mb-3">Usuarios Disponibles</h4>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                    <template x-for="u in avail">
                        <div class="flex justify-between items-center bg-white p-2 rounded shadow-sm text-sm border cursor-pointer hover:bg-blue-50" @click="moveToCurr(u)">
                            <span x-text="u"></span>
                            <span class="text-green-500 font-bold">&rarr;</span>
                        </div>
                    </template>
                </div>
            </div>
            <div class="border rounded-lg p-4 bg-gray-50">
                <h4 class="text-sm font-bold mb-3">En el Grupo</h4>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                    <template x-for="u in curr">
                        <div class="flex justify-between items-center bg-white p-2 rounded shadow-sm text-sm border cursor-pointer hover:bg-red-50" @click="moveToAvail(u)">
                            <span class="text-red-500 font-bold">&larr;</span>
                            <span x-text="u"></span>
                        </div>
                    </template>
                </div>
            </div>
        </div>
        
        <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 rounded-lg mt-6">Guardar Grupo</button>
    </form>
    """
    return HTMLResponse(content=html)

@router.post("/api/v1/rbac/groups/{group_id}/edit", response_class=HTMLResponse)
async def post_edit_group(
    group_id: str, 
    request: Request, 
    name: str = Form(...), 
    role_id: str = Form(None), 
    user_usernames: list[str] = Form(default=[]),
    session_data: dict = Depends(require_permission("roles:modificar")), 
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    try:
        if not role_id: role_id = None
        await db.execute(text("UPDATE groups SET name = :n, role_id = :r WHERE id = :id AND tenant_id = :t"), {"n": name, "r": role_id, "id": group_id, "t": tenant_id})
        
        u_ids = []
        if user_usernames:
            u_res = await db.execute(text("SELECT id FROM users WHERE username = ANY(:names) AND tenant_id = :t"), {"names": user_usernames, "t": tenant_id})
            u_ids = [str(row[0]) for row in u_res.fetchall()]
            
        await db.execute(text("DELETE FROM user_groups WHERE group_id = :id"), {"id": group_id})
        for uid in u_ids:
            await db.execute(text("INSERT INTO user_groups (user_id, group_id) VALUES (:u, :g)"), {"u": uid, "g": group_id})
            
        await db.commit()
        from app import rbac
        await rbac.load_rbac_cache(db)
        
        return await list_groups(request, session_data, db)
    except Exception as e:
        await db.rollback()
        return HTMLResponse("<div class='p-4 text-red-500'>Ocurrió un error. Verifique los datos o permisos e intente nuevamente.</div>", status_code=400)

@router.get("/api/v1/rbac/groups/new", response_class=HTMLResponse)
async def get_new_group(request: Request, session_data: dict = Depends(require_permission("roles:modificar")), db: AsyncSession = Depends(get_db_session)):
    tenant_id = session_data["tenant_id"]
    actor_level = get_role_hierarchy(tenant_id, session_data["role_id"])
    
    r_res = await db.execute(text("SELECT id, name FROM roles WHERE tenant_id = :t AND hierarchy_level <= :lvl"), {"t": tenant_id, "lvl": actor_level})
    roles = r_res.fetchall()
    role_opts = '<option value="">Sin Rol</option>'
    for r in roles:
        role_opts += f'<option value="{r[0]}">{r[1]}</option>'
        
    u_res = await db.execute(text("SELECT id, username FROM users WHERE tenant_id = :t"), {"t": tenant_id})
    all_users = [u[1] for u in u_res.fetchall()]
    
    import json
    
    html = f"""
    <form hx-post="/api/v1/rbac/groups" hx-target="#groups-list" hx-swap="innerHTML" @submit="groupModal = false" class="space-y-6">
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Nombre del Grupo</label>
            <input type="text" name="name" required class="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none">
        </div>
        <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Rol Heredado</label>
            <select name="role_id" class="w-full px-4 py-3 rounded-lg border border-gray-200 outline-none">
                {role_opts}
            </select>
        </div>
        
        <div x-data='{{ 
            avail: {json.dumps(all_users)}, 
            curr: [],
            moveToCurr(u) {{ this.avail = this.avail.filter(x => x !== u); this.curr.push(u); }},
            moveToAvail(u) {{ this.curr = this.curr.filter(x => x !== u); this.avail.push(u); }}
        }}' class="grid grid-cols-2 gap-4">
            <template x-for="u in curr">
                <input type="hidden" name="user_usernames" :value="u">
            </template>
            <div class="border rounded-lg p-4 bg-gray-50">
                <h4 class="text-sm font-bold mb-3">Usuarios Disponibles</h4>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                    <template x-for="u in avail">
                        <div class="flex justify-between items-center bg-white p-2 rounded shadow-sm text-sm border cursor-pointer hover:bg-blue-50" @click="moveToCurr(u)">
                            <span x-text="u"></span>
                            <span class="text-green-500 font-bold">&rarr;</span>
                        </div>
                    </template>
                </div>
            </div>
            <div class="border rounded-lg p-4 bg-gray-50">
                <h4 class="text-sm font-bold mb-3">En el Grupo</h4>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                    <template x-for="u in curr">
                        <div class="flex justify-between items-center bg-white p-2 rounded shadow-sm text-sm border cursor-pointer hover:bg-red-50" @click="moveToAvail(u)">
                            <span class="text-red-500 font-bold">&larr;</span>
                            <span x-text="u"></span>
                        </div>
                    </template>
                </div>
            </div>
        </div>
        
        <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 rounded-lg mt-6">Crear Grupo</button>
    </form>
    """
    return HTMLResponse(content=html)

@router.post("/api/v1/rbac/groups", response_class=HTMLResponse)
async def post_create_group(
    request: Request, 
    name: str = Form(...), 
    role_id: str = Form(None), 
    user_usernames: list[str] = Form(default=[]),
    session_data: dict = Depends(require_permission("roles:crear")), 
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    try:
        if not role_id: role_id = None
        
        ins_res = await db.execute(
            text("INSERT INTO groups (tenant_id, name, role_id) VALUES (:t, :n, :r) RETURNING id"), 
            {"t": tenant_id, "n": name, "r": role_id}
        )
        group_id = str(ins_res.fetchone()[0])
        
        u_ids = []
        if user_usernames:
            u_res = await db.execute(text("SELECT id FROM users WHERE username = ANY(:names) AND tenant_id = :t"), {"names": user_usernames, "t": tenant_id})
            u_ids = [str(row[0]) for row in u_res.fetchall()]
            
        for uid in u_ids:
            await db.execute(text("INSERT INTO user_groups (user_id, group_id) VALUES (:u, :g)"), {"u": uid, "g": group_id})
            
        await db.commit()
        from app import rbac
        await rbac.load_rbac_cache(db)
        
        return await list_groups(request, session_data, db)
    except Exception as e:
        await db.rollback()
        return HTMLResponse("<div class='p-4 text-red-500'>Ocurrió un error. Verifique los datos o permisos e intente nuevamente.</div>", status_code=400)
@router.get("/api/v1/grupos/{grupo_id}/usuarios", response_class=HTMLResponse)
async def get_grupo_usuarios(grupo_id: str, request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id: return HTMLResponse("")
    
    query = text("""
        SELECT id, username
        FROM users
        WHERE role_id = :gid
    """)
    res = await db.execute(query, {"gid": grupo_id})
    usuarios = res.fetchall()
    
    html = """
    <div x-data="{ qUser: '' }" class="p-2 bg-white flex flex-col gap-2">
        <input type="text" x-model="qUser" placeholder="Filtrar usuario en este grupo..." class="w-full px-3 py-1.5 border border-slate-200 rounded text-xs focus:ring-1 focus:ring-indigo-500 mb-2">
        <div class="max-h-40 overflow-y-auto">
    """
    for u in usuarios:
        html += f"""
            <label x-show="'{u.username.lower()}'.includes(qUser.toLowerCase())" class="flex items-center gap-3 p-2 hover:bg-slate-50 cursor-pointer rounded-lg border border-transparent transition-colors">
                <input type="radio" name="usuario_destino_dummy" class="text-indigo-600 focus:ring-indigo-500" @change="usuarioDestino = '{u.id}'">
                <div class="flex items-center gap-2">
                    <div class="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">
                        {u.username[:2].upper()}
                    </div>
                    <span class="text-sm font-medium text-slate-700">{u.username}</span>
                </div>
            </label>
        """
    if not usuarios:
        html += '<div class="text-sm text-slate-500 p-2">No hay miembros en este grupo.</div>'
        
    html += "</div></div>"
    return HTMLResponse(html)

@router.get("/api/v1/usuarios/buscar", response_class=HTMLResponse)
async def buscar_usuarios_global(request: Request, query: str = "", db: AsyncSession = Depends(get_db_session)):
    if len(query) < 2:
        return HTMLResponse("")
        
    sql = text("""
        SELECT id, username 
        FROM users 
        WHERE username ILIKE :q 
        LIMIT 10
    """)
    res = await db.execute(sql, {"q": f"%{query}%"})
    usuarios = res.fetchall()
    
    html = ""
    for u in usuarios:
        html += f"""
        <label class="flex items-center gap-3 p-2 hover:bg-slate-50 cursor-pointer rounded-lg border border-slate-100 mb-1 transition-colors">
            <input type="radio" name="usuario_destino_dummy" class="text-indigo-600 focus:ring-indigo-500" @change="usuarioDestino = '{u.id}'">
            <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">
                    {u.username[:2].upper()}
                </div>
                <span class="text-sm font-medium text-slate-700">{u.username}</span>
            </div>
        </label>
        """
    if not html:
        html = '<div class="text-sm text-slate-500">No se encontraron auditores.</div>'
    return HTMLResponse(html)
