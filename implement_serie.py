with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Add onclick to Serie
content = re.sub(
    r'(<label class="block text-sm font-semibold text-gray-600">Serie:</label>\s*<div class="flex items-center gap-1">\s*<button type="button" )class',
    r'\1onclick="window.openCrearSerieModal()" class',
    content
)

# Add id="serie_select" to Serie
content = re.sub(
    r'<select name="serie" class=',
    r'<select id="serie_select" name="serie" class=',
    content
)
# Ensure subseccion has id="subseccion_select"
content = re.sub(
    r'<select name="subseccion" class=',
    r'<select id="subseccion_select" name="subseccion" class=',
    content
)

new_routes = r"""

@router.get("/modal/serie")
async def get_crear_serie_modal(
    request: Request,
    fondo_id: str,
    seccion_id: str,
    subseccion_id: str = None,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    fondo_res = await db.execute(text("SELECT nombre, codigo FROM agn_dependencias WHERE id = :id AND tipo = 'FONDO'"), {"id": fondo_id})
    fondo = fondo_res.fetchone()
    fondo_text = f"{fondo.nombre} (Código: {fondo.codigo})" if fondo else "Fondo Desconocido"
    
    seccion_res = await db.execute(text("SELECT nombre, codigo FROM agn_dependencias WHERE id = :id AND tipo = 'SECCION'"), {"id": seccion_id})
    seccion = seccion_res.fetchone()
    seccion_text = f"{seccion.nombre} (Código: {seccion.codigo})" if seccion else "Sección Desconocida"
    
    subseccion_text = "N/A (Sin Subsección)"
    if subseccion_id and subseccion_id.strip() != "" and subseccion_id.strip() != "null":
        sub_res = await db.execute(text("SELECT nombre, codigo FROM agn_dependencias WHERE id = :id AND tipo = 'SUBSECCION'"), {"id": subseccion_id})
        sub = sub_res.fetchone()
        if sub:
            subseccion_text = f"{sub.nombre} (Código: {sub.codigo})"
    else:
        subseccion_id = ""
            
    html = f'''
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white">
        <div class="flex items-center gap-3">
            <button type="button" onclick="window.openAgnModal()" class="text-[#4f46e5] hover:text-[#4338ca] hover:bg-indigo-50 p-1.5 rounded-md transition-colors" title="Volver al Expediente">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </button>
            <h2 class="text-xl font-bold text-[#1e293b] font-sans uppercase">Crear Nueva Serie Documental</h2>
        </div>
        <button type="button" onclick="Swal.close()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    </div>
    <div class="p-6 bg-[#f8fafc]">
        <form id="crear-serie-form" hx-post="/api/v1/agn/series" hx-swap="none" @htmx:after-request.camel="let r=JSON.parse($event.detail.xhr.response); if($event.detail.successful) {{ Swal.fire({{title: '¡Serie Creada!', text: 'Guardado exitosamente', icon: 'success', timer: 1500, showConfirmButton: false}}).then(()=>window.openAgnModal()) }} else {{ Swal.fire('Error', r.detail || 'Ocurrió un error', 'error') }}" @htmx:response-error.camel="Swal.fire('Error', JSON.parse($event.detail.xhr.response).detail || 'Ocurrió un error al guardar', 'error')">
            
            <input type="hidden" name="fondo_id" value="{fondo_id}">
            <input type="hidden" name="seccion_id" value="{seccion_id}">
            <input type="hidden" name="subseccion_id" value="{subseccion_id}">
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Fondo</label>
                    <div class="relative">
                        <input type="text" readonly value="{fondo_text}" class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-xs bg-gray-100 text-gray-500 font-medium select-none outline-none truncate" title="{fondo_text}">
                        <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Sección</label>
                    <div class="relative">
                        <input type="text" readonly value="{seccion_text}" class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-xs bg-gray-100 text-gray-500 font-medium select-none outline-none truncate" title="{seccion_text}">
                        <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Subsección</label>
                    <div class="relative">
                        <input type="text" readonly value="{subseccion_text}" class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-xs bg-gray-100 text-gray-500 font-medium select-none outline-none truncate" title="{subseccion_text}">
                        <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Código de la Serie <span class="text-red-500 ml-1">*</span>
                        <div class="relative group inline-flex items-center ml-1">
                            <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600">?</span>
                            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 px-2 py-1.5 bg-gray-800 text-white text-[10px] rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible z-[100] text-center">
                                Identificador único (Ej. 15). Se concatena para formar el código final del expediente.
                            </div>
                        </div>
                    </label>
                    <input type="text" name="codigo" required placeholder="Ej. 110" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Nombre de la Serie <span class="text-red-500 ml-1">*</span></label>
                    <input type="text" name="nombre" required placeholder="Ingrese el nombre completo de la serie" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Retención Archivo Gestión (Años) <span class="text-red-500 ml-1">*</span></label>
                    <input type="number" min="0" name="retencion_ag" required value="0" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Retención Archivo Central (Años) <span class="text-red-500 ml-1">*</span></label>
                    <input type="number" min="0" name="retencion_ac" required value="0" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Disposición Final <span class="text-red-500 ml-1">*</span></label>
                    <select name="disposicion" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors appearance-none">
                        <option value="">Seleccione opción</option>
                        <option value="CT">Conservación Total (CT)</option>
                        <option value="E">Eliminación (E)</option>
                        <option value="M">Microfilmación (M)</option>
                        <option value="S">Selección (S)</option>
                    </select>
                </div>
            </div>
            
            <div class="grid grid-cols-1 gap-4 mb-6">
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Estado de la Serie</label>
                    <select name="estado_activa" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors appearance-none">
                        <option value="true">Activa</option>
                        <option value="false">Inactiva</option>
                    </select>
                </div>
            </div>
            
            <div class="flex justify-end gap-3 pt-2">
                <button type="button" onclick="window.openAgnModal()" class="px-5 py-2.5 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" @click="if(!$el.form.checkValidity()) $el.form.reportValidity()" class="px-5 py-2.5 text-sm font-bold text-white bg-[#0f172a] hover:bg-[#1e293b] rounded-lg shadow-sm transition-colors flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                    Guardar Serie
                </button>
            </div>
        </form>
    </div>
    '''
    return HTMLResponse(content=html)


@router.post("/series")
async def create_agn_serie(
    request: Request,
    fondo_id: str = Form(...),
    seccion_id: str = Form(...),
    subseccion_id: str = Form(None),
    codigo: str = Form(...),
    nombre: str = Form(...),
    retencion_ag: int = Form(...),
    retencion_ac: int = Form(...),
    disposicion: str = Form(...),
    estado_activa: bool = Form(True),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    
    codigo = codigo.strip().upper()
    nombre = nombre.strip().upper()
    
    if subseccion_id and subseccion_id.strip() == "":
        subseccion_id = None
        
    check_q = text("SELECT id FROM agn_series WHERE seccion_id = :s AND (subseccion_id = :sub OR (subseccion_id IS NULL AND :sub IS NULL)) AND codigo = :c")
    existing = await db.execute(check_q, {"s": seccion_id, "sub": subseccion_id, "c": codigo})
    if existing.fetchone():
        raise HTTPException(status_code=400, detail="El código de Serie ya existe para esta dependencia.")
        
    insert_q = text(\"""
        INSERT INTO agn_series (tenant_id, fondo_id, seccion_id, subseccion_id, codigo, nombre, retencion_ag, retencion_ac, disposicion, estado_activa)
        VALUES (:tenant, :fondo_id, :seccion_id, :subseccion_id, :codigo, :nombre, :ag, :ac, :disp, :estado)
        RETURNING id
    \""")
    
    result = await db.execute(insert_q, {
        "tenant": tenant_id,
        "fondo_id": fondo_id,
        "seccion_id": seccion_id,
        "subseccion_id": subseccion_id,
        "codigo": codigo,
        "nombre": nombre,
        "ag": retencion_ag,
        "ac": retencion_ac,
        "disp": disposicion,
        "estado": estado_activa
    })
    
    new_id = str(result.scalar())
    await db.commit()
    
    return {"status": "success", "id": new_id}

"""
content += new_routes.replace('\\"""', '"""')

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
