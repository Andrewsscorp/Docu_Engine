from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json
from app.database import get_db_session

router = APIRouter(prefix="/api/v1/etiquetas", tags=["Etiquetas"])

def get_row_html(et, uso_count):
    enlace_uso = f'''
        <a href="#" @click.prevent="Swal.fire('Próximamente', 'Navegación al explorador con filtro: {et.id_etiqueta}', 'info')" 
           class="text-indigo-600 hover:text-indigo-800 text-sm font-medium hover:underline">
            Aplicada en {uso_count} documentos
        </a>
    '''
    
    kebab_menu = f'''
    <td class="py-3 px-4 text-right relative" x-data="{{ open: false }}">
        <button @click="open = !open" @click.away="open = false" class="p-2 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-indigo-50">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 14a2 2 0 100-4 2 2 0 000 4zm0-6a2 2 0 100-4 2 2 0 000 4zm0 12a2 2 0 100-4 2 2 0 000 4z"></path></svg>
        </button>

        <div x-show="open" x-transition x-cloak class="absolute right-8 top-10 w-48 bg-white rounded-lg shadow-xl border border-slate-100 z-[100] text-left overflow-hidden">
            <ul class="text-sm text-slate-700">
                <li>
    '''
    
    if uso_count > 0:
        kebab_menu += f'''
                    <button @click.prevent="open=false; Swal.fire({{icon: 'warning', title: 'Etiqueta Bloqueada', text: 'Esta etiqueta ya ha sido aplicada a {uso_count} documentos. Para proteger la inmutabilidad de la auditoría, su nombre y color han sido sellados. Si necesita una nueva nomenclatura, por favor cree una etiqueta nueva y desactive esta.', confirmButtonText: 'Entendido'}})" class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center">
                        <span class="mr-2">🔒</span> Editar
                    </button>
        '''
    else:
        kebab_menu += f'''
                    <button @click.prevent="open=false; document.body.dispatchEvent(new CustomEvent('edit-tag', {{detail: {{id: '{et.id_etiqueta}', nombre: '{et.nombre}', bg: '{et.color_fondo}', text: '{et.color_texto}', cat: '{et.categoria}'}}}}))" class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center">
                        <span class="mr-2">✏️</span> Editar
                    </button>
        '''

    kebab_menu += '''
                </li>
                <li>
                    <button @click.prevent="open=false; Swal.fire('Próximamente', 'El módulo de permisos RBAC estará disponible en la versión 2.0', 'info')" class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center">
                        <span class="mr-2">🛡️</span> Permisos
                    </button>
                </li>
                <li>
                    <button @click.prevent="open=false; Swal.fire('Próximamente', 'El módulo de automatizaciones estará disponible en la versión 2.0', 'info')" class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center">
                        <span class="mr-2">⚡</span> Automatización
                    </button>
                </li>
                <li class="border-t border-slate-100">
    '''
    
    if not et.es_sistema:
        kebab_menu += f'''
                    <button hx-delete="/api/v1/etiquetas/{et.id_etiqueta}" hx-confirm="¿Seguro que deseas desactivar esta etiqueta?" hx-target="closest tr" hx-swap="outerHTML" class="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 flex items-center">
                        <span class="mr-2">🗑️</span> Desactivar
                    </button>
        '''
    else:
        kebab_menu += f'''
                    <button @click.prevent="Swal.fire('Restringido', 'No se puede desactivar una etiqueta del sistema', 'error')" class="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-400 flex items-center cursor-not-allowed">
                        <span class="mr-2">🗑️</span> Sistema
                    </button>
        '''
        
    kebab_menu += '''
                </li>
            </ul>
        </div>
    </td>
    '''
    
    return f'''
    <tr class="border-b border-gray-100 hover:bg-slate-50/50 transition-colors" id="etiqueta-row-{et.id_etiqueta}">
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
async def list_etiquetas(request: Request, categoria: str = Query("Todos"), db: AsyncSession = Depends(get_db_session)):
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
            
        query_str += " GROUP BY e.id_etiqueta ORDER BY e.fecha_creacion ASC"
        
        result = await db.execute(text(query_str), params)
        etiquetas = result.all()
        
        html_out = ""
        for et in etiquetas:
            html_out += get_row_html(et, et.uso_count)
            
        if not html_out:
            return HTMLResponse("<tr><td colspan='5' class='py-8 text-center text-gray-500'>No hay etiquetas en esta categoría</td></tr>")
            
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
        result = await db.execute(
            text("""
                INSERT INTO etiquetas_maestras (nombre, color_fondo, color_texto, categoria, creado_por)
                VALUES (:nombre, :color_fondo, :color_texto, :categoria, :creado_por)
                RETURNING id_etiqueta, nombre, color_fondo, color_texto, es_sistema, categoria
            """),
            {"nombre": nombre, "color_fondo": color_fondo, "color_texto": color_texto, "categoria": categoria, "creado_por": user_id}
        )
        await db.commit()
        et = result.fetchone()
        return HTMLResponse(content=get_row_html(et, 0))
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
        result = await db.execute(text("SELECT COUNT(*) FROM documento_etiquetas WHERE id_etiqueta = :id"), {"id": id})
        uso_count = result.scalar()
        
        if uso_count > 0:
            detalles = json.dumps({"etiqueta_id": id, "intento_cambio_nombre": nombre, "razon_bloqueo": f"En uso por {uso_count} documentos"})
            await db.execute(text("""
                INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles) 
                VALUES ('INTENTO_ALTERACION_ETIQUETA_BLOQUEADO', :user, :ip, :detalles)
            """), {"user": user_id, "ip": client_ip, "detalles": detalles})
            await db.commit()
            
            response = HTMLResponse(content="") 
            response.headers["HX-Trigger"] = "mostrarAlertaInmutabilidad"
            return response
            
        result = await db.execute(text("""
            UPDATE etiquetas_maestras 
            SET nombre = :nombre, color_fondo = :color_fondo, color_texto = :color_texto, categoria = :categoria 
            WHERE id_etiqueta = :id 
            RETURNING id_etiqueta, nombre, color_fondo, color_texto, es_sistema, categoria
        """), {"id": id, "nombre": nombre, "color_fondo": color_fondo, "color_texto": color_texto, "categoria": categoria})
        et = result.fetchone()
        
        if not et:
            return HTMLResponse(status_code=404)
            
        await db.commit()
        response = HTMLResponse(content=get_row_html(et, 0))
        response.headers["HX-Trigger"] = "closeModal"
        return response
        
    except Exception as e:
        await db.rollback()
        return HTMLResponse(f"Error: {str(e)}", status_code=500)

@router.delete("/{id}", response_class=HTMLResponse)
async def delete_etiqueta(id: str, request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        result = await db.execute(text("SELECT es_sistema FROM etiquetas_maestras WHERE id_etiqueta = :id"), {"id": id})
        row = result.fetchone()
        if not row:
            return HTMLResponse(status_code=404)
        if row.es_sistema:
            return HTMLResponse("No puedes eliminar una etiqueta de sistema", status_code=403)
            
        await db.execute(text("UPDATE etiquetas_maestras SET estado_activa = FALSE WHERE id_etiqueta = :id"), {"id": id})
        await db.commit()
        return HTMLResponse(content="")
    except Exception as e:
        await db.rollback()
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
