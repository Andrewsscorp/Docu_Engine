from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
from app.database import get_db_session

router = APIRouter(prefix="/api/v1/etiquetas", tags=["Etiquetas"])

def get_row_html(et, uso_count):
    if uso_count > 0:
        enlace_uso = f'''
            <a href="/#explorador?filtro_etiqueta={et.id_etiqueta}" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium hover:underline">
                Aplicada en {uso_count} documentos
            </a>
        '''
    else:
        enlace_uso = f'''<span class="text-gray-400 text-sm">Aplicada en 0 documentos</span>'''
    
    kebab_menu = f'''
    <td class="py-3 px-4 text-right relative" x-data="{{ open: false }}" @click.outside="open = false">
        <button @click="open = !open" class="p-2 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 14a2 2 0 100-4 2 2 0 000 4zm0-6a2 2 0 100-4 2 2 0 000 4zm0 12a2 2 0 100-4 2 2 0 000 4z"></path></svg>
        </button>

        <div x-show="open" x-transition x-cloak class="absolute right-8 top-10 w-48 bg-white rounded-lg shadow-xl border border-slate-100 z-[100] text-left overflow-hidden">
            <ul class="text-sm text-slate-700">
                <li>
    '''
    
    if uso_count > 0:
        kebab_menu += f'''
                    <button @click.prevent="open=false; Swal.fire({{icon: 'warning', title: 'Etiqueta Bloqueada', text: 'Esta etiqueta ya ha sido aplicada a {uso_count} documentos. Para proteger la inmutabilidad de la auditoría, su nombre y color han sido sellados. Si necesita una nueva nomenclatura, por favor cree una etiqueta nueva y desactive esta.', confirmButtonText: 'Entendido'}})" class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center transition-colors">
                        <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg> Editar
                    </button>
        '''
    else:
        kebab_menu += f'''
                    <button @click.prevent="open=false; window.dispatchEvent(new CustomEvent('edit-tag', {{detail: {{id: '{et.id_etiqueta}', nombre: '{et.nombre}', bg: '{et.color_fondo}', text: '{et.color_texto}', cat: '{et.categoria}'}}}}))" class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center transition-colors">
                        <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg> Editar
                    </button>
        '''

    kebab_menu += f'''
                </li>
                <li>
                    <button hx-get="/api/v1/etiquetas/{et.id_etiqueta}/permisos" 
                            hx-target="#modal-permisos-content" 
                            @click="open = false; window.dispatchEvent(new Event('abrirmodalpermisos'))"
                            class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center transition-colors">
                        <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg> Permisos
                    </button>
                </li>
                <li>
                    <button x-data="{{ clicking: false }}" 
                        @click.prevent="
                            if(clicking) return; 
                            clicking = true; 
                            open = false; 
                            Swal.fire({{
                                title: 'Módulo de Automatización',
                                text: 'Las reglas de disparo hacia Novu estarán habilitadas en la v2.0.',
                                icon: 'info',
                                confirmButtonColor: '#4f46e5'
                            }}); 
                            setTimeout(() => clicking = false, 1000);
                        " class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center transition-colors">
                        <svg class="w-4 h-4 mr-3 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg> Automatización
                    </button>
                </li>
                <li class="border-t border-slate-100">
    '''
    
    if not et.es_sistema:
        kebab_menu += f'''
                    <button hx-delete="/api/v1/etiquetas/{et.id_etiqueta}" hx-confirm="¿Está completamente seguro de desactivar esta etiqueta del sistema?" hx-target="closest tr" hx-swap="delete" class="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 flex items-center font-medium transition-colors">
                        <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg> Desactivar
                    </button>
        '''
    else:
        kebab_menu += f'''
                    <button @click.prevent="Swal.fire('Restringido', 'No se puede desactivar una etiqueta del sistema', 'error')" class="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-400 flex items-center cursor-not-allowed">
                        <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg> Sistema
                    </button>
        '''
        
    kebab_menu += '''
                </li>
            </ul>
        </div>
    </td>
    '''
    
    return f'''
    <tr class="border-b border-gray-100 hover:bg-slate-50/50 transition-colors animate-fade-in-up" id="etiqueta-row-{et.id_etiqueta}">
        <td class="py-3 px-4">
            <span class="px-3 py-1 text-xs font-semibold rounded-full {et.color_fondo} {et.color_texto}">
                {et.nombre}
            </span>
        </td>
        <td class="py-3 px-4">
            <div class="font-medium text-slate-800">{et.nombre}</div>
            <div class="text-xs text-slate-400">Tipo: {et.categoria}</div>
        </td>
        <td class="py-3 px-4">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gray-50 text-xs font-medium text-gray-600 border border-gray-200">
                <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Pública
            </span>
        </td>
        <td class="py-3 px-4">
            {enlace_uso}
        </td>
        {kebab_menu}
    </tr>
    '''

@router.get("", response_class=HTMLResponse)
async def list_etiquetas(request: Request, categoria: str = Query("Todos"), q: str = Query(None), db: AsyncSession = Depends(get_db_session)):
    try:
        query_str = """
            SELECT e.id_etiqueta, e.nombre, e.color_fondo, e.color_texto, e.es_sistema, e.categoria,
                   COUNT(de.id_documento) as uso_count
            FROM etiquetas_maestras e
            LEFT JOIN documento_etiquetas de ON e.id_etiqueta = de.id_etiqueta
            WHERE e.estado_activa = TRUE
        """
        params = {}
        if categoria != "Todos":
            query_str += " AND e.categoria = :cat"
            params["cat"] = categoria
            
        if q and q.strip():
            query_str += " AND e.nombre ILIKE :q"
            params["q"] = f"%{q.strip()}%"
            
        query_str += " GROUP BY e.id_etiqueta ORDER BY e.fecha_creacion ASC"
        
        if q and q.strip():
            query_str += " LIMIT 50"
        
        result = await db.execute(text(query_str), params)
        etiquetas = result.all()
        
        html_out = ""
        for et in etiquetas:
            html_out += get_row_html(et, et.uso_count)
            
        if not html_out:
            return HTMLResponse(f"""
            <tr>
                <td colspan='5' class='py-12 text-center'>
                    <div class="flex flex-col items-center justify-center text-gray-500">
                        <svg class="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>
                        <p class="text-sm font-medium">No se encontraron etiquetas</p>
                        <p class="text-xs text-gray-400 mt-1">Prueba con otro término de búsqueda</p>
                    </div>
                </td>
            </tr>
            """)
            
        return HTMLResponse(content=html_out)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(f"<tr><td colspan='5' class='text-red-500'>Error: {str(e)}</td></tr>")

@router.post("", response_class=HTMLResponse)
async def create_etiqueta(
    request: Request, nombre: str = Form(...), color_fondo: str = Form(...), color_texto: str = Form(...), categoria: str = Form(...), db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    try:
        clean_name = nombre.strip()
        
        # Validación Preventiva (Case-Insensitive)
        check_query = text("SELECT id_etiqueta FROM etiquetas_maestras WHERE nombre ILIKE :nombre AND estado_activa = TRUE LIMIT 1")
        check_res = await db.execute(check_query, {"nombre": clean_name})
        if check_res.fetchone():
            response = HTMLResponse(content="")
            response.headers["HX-Trigger"] = json.dumps({
                "alertaError": {
                    "mensaje": "Ya existe una etiqueta activa con este nombre."
                }
            })
            return response
            
        result = await db.execute(
            text("""
                INSERT INTO etiquetas_maestras (nombre, color_fondo, color_texto, categoria, creado_por)
                VALUES (:nombre, :color_fondo, :color_texto, :categoria, :creado_por)
                RETURNING id_etiqueta, nombre, color_fondo, color_texto, es_sistema, categoria
            """),
            {"nombre": clean_name, "color_fondo": color_fondo, "color_texto": color_texto, "categoria": categoria, "creado_por": user_id}
        )
        await db.commit()
        et = result.fetchone()
        
        response = HTMLResponse(content=get_row_html(et, 0))
        # Trigger Toast Success & Close modal
        response.headers["HX-Trigger"] = json.dumps({
            "closeModal": "",
            "toastExito": {
                "mensaje": "Etiqueta creada exitosamente."
            }
        })
        return response
    except Exception as e:
        await db.rollback()
        return HTMLResponse(f"<tr><td colspan='5' class='text-red-500'>Error al crear etiqueta: {str(e)}</td></tr>", status_code=500)

@router.put("/{id}", response_class=HTMLResponse)
async def update_etiqueta(
    id: str, request: Request, nombre: str = Form(...), color_fondo: str = Form(...), color_texto: str = Form(...), categoria: str = Form(...), db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        clean_name = nombre.strip()
        async with db.begin():
            query_etiqueta = text("SELECT * FROM etiquetas_maestras WHERE id_etiqueta = :id FOR UPDATE")
            etiqueta_res = await db.execute(query_etiqueta, {"id": id})
            if not etiqueta_res.fetchone():
                raise HTTPException(status_code=404, detail="Etiqueta no encontrada")

            result_uso = await db.execute(text("SELECT COUNT(1) FROM documento_etiquetas WHERE id_etiqueta = :id"), {"id": id})
            uso_count = result_uso.scalar()
            
            if uso_count > 0:
                detalles = json.dumps({"etiqueta_id": id, "intento_cambio_nombre": clean_name, "razon_bloqueo": f"En uso por {uso_count} documentos"})
                await db.execute(text("""
                    INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles) 
                    VALUES ('INTENTO_EDICION_BLOQUEADO', :user, :ip, :detalles)
                """), {"user": user_id, "ip": client_ip, "detalles": detalles})
                
                response = HTMLResponse(content="") 
                response.headers["HX-Trigger"] = json.dumps({
                    "alertaForense": {
                        "mensaje": "Etiqueta sellada criptográficamente por uso en documentos."
                    }
                })
                return response
                
            # Verificar si existe otra con el mismo nombre y que no sea esta misma
            check_query = text("SELECT id_etiqueta FROM etiquetas_maestras WHERE nombre ILIKE :nombre AND id_etiqueta != :id AND estado_activa = TRUE LIMIT 1")
            check_res = await db.execute(check_query, {"nombre": clean_name, "id": id})
            if check_res.fetchone():
                response = HTMLResponse(content="")
                response.headers["HX-Trigger"] = json.dumps({
                    "alertaError": {
                        "mensaje": "Ya existe una etiqueta activa con este nombre."
                    }
                })
                return response
                
            result = await db.execute(text("""
                UPDATE etiquetas_maestras 
                SET nombre = :nombre, color_fondo = :color_fondo, color_texto = :color_texto, categoria = :categoria 
                WHERE id_etiqueta = :id 
                RETURNING id_etiqueta, nombre, color_fondo, color_texto, es_sistema, categoria
            """), {"id": id, "nombre": clean_name, "color_fondo": color_fondo, "color_texto": color_texto, "categoria": categoria})
            et = result.fetchone()
            
            response = HTMLResponse(content=get_row_html(et, 0))
            response.headers["HX-Trigger"] = json.dumps({
                "closeModal": "",
                "toastExito": {
                    "mensaje": "Etiqueta actualizada exitosamente."
                }
            })
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(f"Error: {str(e)}", status_code=500)

@router.delete("/{id}", response_class=HTMLResponse)
async def delete_etiqueta(id: str, request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        async with db.begin():
            result = await db.execute(text("SELECT es_sistema FROM etiquetas_maestras WHERE id_etiqueta = :id"), {"id": id})
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
                
            if row.es_sistema:
                return HTMLResponse("No puedes eliminar una etiqueta de sistema", status_code=403)
                
            query_tareas = text("""
                SELECT COUNT(1) FROM tareas_asignaciones ta
                JOIN documento_etiquetas de ON ta.id_documento = de.id_documento
                WHERE de.id_etiqueta = :id AND ta.estado IN ('PENDIENTE', 'EN_PROGRESO')
            """)
            tareas_vivas = await db.execute(query_tareas, {"id": id})
            
            if tareas_vivas.scalar() > 0:
                response = HTMLResponse(content="")
                response.headers["HX-Trigger"] = json.dumps({
                    "alertaBloqueo": {
                        "mensaje": "No se puede desactivar. Hay tareas en progreso que dependen de esta etiqueta."
                    }
                })
                return response
                
            await db.execute(text("UPDATE etiquetas_maestras SET estado_activa = FALSE WHERE id_etiqueta = :id"), {"id": id})
            
        response = HTMLResponse(content="")
        response.headers["HX-Trigger"] = json.dumps({
            "toastExito": {
                "mensaje": "Etiqueta desactivada."
            }
        })
        return response
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(f"Error: {str(e)}", status_code=500)

@router.get("/dropdown", response_class=HTMLResponse)
async def get_etiquetas_dropdown(request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        result = await db.execute(text("SELECT id_etiqueta, nombre, color_fondo, color_texto FROM etiquetas_maestras WHERE estado_activa = TRUE ORDER BY fecha_creacion ASC"))
        etiquetas = result.all()
        html_out = '<option value="">-- Selecciona una etiqueta --</option>'
        for et in etiquetas:
            html_out += f'<option value="{et.nombre}" data-bg="{et.color_fondo}" data-text="{et.color_texto}">{et.nombre}</option>'
        return HTMLResponse(content=html_out)
    except Exception as e:
        return HTMLResponse(f"<option value=''>Error: {str(e)}</option>")


@router.get("/{id}/permisos", response_class=HTMLResponse)
async def get_etiqueta_permisos(id: str, request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        # Check if etiqueta exists
        res = await db.execute(text("SELECT id_etiqueta, nombre, es_sistema FROM etiquetas_maestras WHERE id_etiqueta = :id"), {"id": id})
        et = res.fetchone()
        if not et:
            return HTMLResponse("<div class='text-red-500'>Etiqueta no encontrada</div>", status_code=404)
            
        # Get all roles
        roles_res = await db.execute(text("SELECT id, name as nombre, '' as descripcion FROM roles ORDER BY name"))
        roles = roles_res.all()
        
        # Get currently permitted roles
        perm_res = await db.execute(text("SELECT id_rol FROM etiqueta_roles_permitidos WHERE id_etiqueta = :id"), {"id": id})
        permitted = {r.id_rol for r in perm_res.all()}
        
        html_out = f"""
        <form hx-post="/api/v1/etiquetas/{id}/permisos" hx-target="#modal-permisos-content" hx-swap="innerHTML">
            <p class="text-sm text-gray-600 mb-4">
                Seleccione los roles que tendr&aacute;n permiso para asignar y remover la etiqueta <strong>{et.nombre}</strong>.
            </p>
            
            <div class="space-y-3 mb-6 bg-gray-50 p-4 rounded-lg border border-gray-100">
        """
        
        for r in roles:
            checked = "checked" if r.id in permitted else ""
            is_admin = r.nombre in ['Administrador', 'Revisor Fiscal']
            # If system tag, force admin checkbox checked and disabled visually, but we will enforce it in backend too.
            disabled_str = ""
            if et.es_sistema and is_admin:
                checked = "checked"
                disabled_str = 'onclick="return false;" readonly'
                
            html_out += f"""
                <label class="flex items-start gap-3 p-2 hover:bg-white rounded transition-colors cursor-pointer">
                    <div class="flex items-center h-5">
                        <input type="checkbox" name="roles_ids" value="{r.id}" {checked} {disabled_str} class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
                    </div>
                    <div class="flex flex-col">
                        <span class="text-sm font-medium text-gray-800">{r.nombre}</span>
                        <span class="text-xs text-gray-500">{r.descripcion or ''}</span>
                    </div>
                </label>
            """
            
        html_out += """
            </div>
            
            <div class="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700 flex gap-2 mb-6">
                <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                Si no selecciona ningún rol, esta etiqueta será Pública y cualquier usuario podrá utilizarla.
            </div>
            
            <div class="flex justify-end gap-3 mt-4">
                <button type="button" @click="showPermisosModal = false" class="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors">Cancelar</button>
                <button type="submit" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors">Guardar Permisos</button>
            </div>
        </form>
        """
        return HTMLResponse(content=html_out)
    except Exception as e:
        return HTMLResponse(f"<div class='text-red-500'>Error: {str(e)}</div>")

@router.post("/{id}/permisos", response_class=HTMLResponse)
async def update_etiqueta_permisos(id: str, request: Request, roles_ids: list[str] = Form(default=[]), db: AsyncSession = Depends(get_db_session)):
    user_id = getattr(request.state, "user_id", None)
    try:
        async with db.begin():
            # Obtener etiqueta
            res = await db.execute(text("SELECT id_etiqueta, es_sistema FROM etiquetas_maestras WHERE id_etiqueta = :id"), {"id": id})
            et = res.fetchone()
            if not et:
                raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
                
            # Si es etiqueta de sistema, forzar Administrador / Revisor Fiscal
            if et.es_sistema:
                admin_res = await db.execute(text("SELECT id_rol FROM roles WHERE nombre IN ('Administrador', 'Revisor Fiscal')"))
                admin_roles = [r.id_rol for r in admin_res.all()]
                for ar in admin_roles:
                    if str(ar) not in roles_ids:
                        roles_ids.append(str(ar))
            
            # Borrar permisos actuales
            await db.execute(text("DELETE FROM etiqueta_roles_permitidos WHERE id_etiqueta = :id"), {"id": id})
            
            # Bulk insert nuevos permisos si hay
            if roles_ids:
                insert_query = text("INSERT INTO etiqueta_roles_permitidos (id_etiqueta, id_rol) VALUES (:id_etiqueta, :id_rol)")
                valores = [{"id_etiqueta": id, "id_rol": rid} for rid in roles_ids]
                await db.execute(insert_query, valores)
                
            # Audit log
            detalles = json.dumps({"etiqueta_id": id, "nuevos_roles": roles_ids})
            await db.execute(text("""
                INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles) 
                VALUES ('PERMISOS_ETIQUETA_ACTUALIZADOS', :user, :ip, :detalles)
            """), {"user": user_id, "ip": request.client.host if request.client else 'unknown', "detalles": detalles})
            
        # Success response
        response = HTMLResponse(content="")
        response.headers["HX-Trigger"] = json.dumps({
            "cerrarModalPermisos": True,
            "toastexito": {
                "mensaje": "Permisos actualizados con rigor forense."
            }
        })
        return response
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(f"<div class='text-red-500'>Error al guardar permisos: {str(e)}</div>")

