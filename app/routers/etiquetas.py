from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db_session

router = APIRouter(prefix="/api/v1/etiquetas", tags=["Etiquetas"])

@router.get("", response_class=HTMLResponse)
async def list_etiquetas(request: Request, db: AsyncSession = Depends(get_db_session)):
    try:
        result = await db.execute(text('''
            SELECT e.id_etiqueta, e.nombre, e.color_fondo, e.color_texto, e.es_sistema,
                   COUNT(de.id_documento) as uso_count
            FROM etiquetas_maestras e
            LEFT JOIN documento_etiquetas de ON e.id_etiqueta = de.id_etiqueta
            WHERE e.estado_activa = TRUE
            GROUP BY e.id_etiqueta
            ORDER BY e.fecha_creacion ASC
        '''))
        etiquetas = result.all()
        
        html_out = ""
        for et in etiquetas:
            delete_btn = f'''
                <button hx-delete="/api/v1/etiquetas/{et.id_etiqueta}" 
                        hx-confirm="¿Seguro que deseas eliminar esta etiqueta?" 
                        hx-target="closest tr" 
                        hx-swap="outerHTML"
                        class="text-slate-400 hover:text-red-600 transition-colors p-2 rounded hover:bg-slate-50"
                        title="Eliminar">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
            ''' if not et.es_sistema else '''
                <span class="text-xs text-slate-400 italic">Sistema</span>
            '''
            
            html_out += f'''
            <tr class="border-b border-gray-100 hover:bg-slate-50/50 transition-colors">
                <td class="py-3 px-4">
                    <span class="px-3 py-1 text-xs font-semibold rounded-full {et.color_fondo} {et.color_texto}">
                        {et.nombre}
                    </span>
                </td>
                <td class="py-3 px-4 text-slate-800 font-medium">
                    {et.nombre}
                </td>
                <td class="py-3 px-4 text-slate-500 text-sm">
                    Aplicada en {et.uso_count} documentos
                </td>
                <td class="py-3 px-4 text-right">
                    <div class="flex items-center justify-end gap-2">
                        {delete_btn}
                    </div>
                </td>
            </tr>
            '''
        return HTMLResponse(content=html_out)
    except Exception as e:
        return HTMLResponse(f"<tr><td colspan='4' class='text-red-500'>Error: {str(e)}</td></tr>")

@router.post("", response_class=HTMLResponse)
async def create_etiqueta(
    request: Request,
    nombre: str = Form(...),
    color_fondo: str = Form(...),
    color_texto: str = Form(...),
    db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    try:
        result = await db.execute(
            text('''
                INSERT INTO etiquetas_maestras (nombre, color_fondo, color_texto, creado_por)
                VALUES (:nombre, :color_fondo, :color_texto, :creado_por)
                RETURNING id_etiqueta
            '''),
            {"nombre": nombre, "color_fondo": color_fondo, "color_texto": color_texto, "creado_por": user_id}
        )
        await db.commit()
        id_etiqueta = result.scalar()
        
        html_row = f'''
        <tr class="border-b border-gray-100 hover:bg-slate-50/50 transition-colors animate-fade-in-up">
            <td class="py-3 px-4">
                <span class="px-3 py-1 text-xs font-semibold rounded-full {color_fondo} {color_texto}">
                    {nombre}
                </span>
            </td>
            <td class="py-3 px-4 text-slate-800 font-medium">
                {nombre}
            </td>
            <td class="py-3 px-4 text-slate-500 text-sm">
                Aplicada en 0 documentos
            </td>
            <td class="py-3 px-4 text-right">
                <div class="flex items-center justify-end gap-2">
                    <button hx-delete="/api/v1/etiquetas/{id_etiqueta}" 
                            hx-confirm="¿Seguro que deseas eliminar esta etiqueta?" 
                            hx-target="closest tr" 
                            hx-swap="outerHTML"
                            class="text-slate-400 hover:text-red-600 transition-colors p-2 rounded hover:bg-slate-50"
                            title="Eliminar">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </td>
        </tr>
        '''
        return HTMLResponse(content=html_row)
    except Exception as e:
        await db.rollback()
        return HTMLResponse(f"<tr><td colspan='4' class='text-red-500'>Error al crear etiqueta: {str(e)}</td></tr>", status_code=500)

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
        result = await db.execute(text('''
            SELECT id_etiqueta, nombre, color_fondo, color_texto 
            FROM etiquetas_maestras 
            WHERE estado_activa = TRUE
            ORDER BY fecha_creacion ASC
        '''))
        etiquetas = result.all()
        
        html_out = '<option value="">-- Selecciona una etiqueta --</option>'
        for et in etiquetas:
            html_out += f'<option value="{et.nombre}" data-bg="{et.color_fondo}" data-text="{et.color_texto}">{et.nombre}</option>'
        return HTMLResponse(content=html_out)
    except Exception as e:
        return HTMLResponse(f"<option value=''>Error: {str(e)}</option>")
