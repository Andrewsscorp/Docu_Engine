with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific 'Crear' button for Fondo to open the new modal
old_fondo_label = '''<label class="block text-sm font-semibold text-gray-600">Fondo:</label>
                    <div class="flex items-center gap-1">
                        <button type="button" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>'''
new_fondo_label = '''<label class="block text-sm font-semibold text-gray-600">Fondo:</label>
                    <div class="flex items-center gap-1">
                        <button type="button" onclick="window.openCrearFondoModal()" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>'''
content = content.replace(old_fondo_label, new_fondo_label)

# Add the new endpoints at the end of the file
new_endpoints = '''

@router.get("/modal/fondo")
async def get_crear_fondo_modal(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
):
    html = f"""
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white">
        <h2 class="text-xl font-bold text-[#1e293b] font-sans">CREAR NUEVO FONDO DOCUMENTAL</h2>
        <button type="button" onclick="Swal.close()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    </div>
    <div class="p-6 bg-[#f8fafc]">
        <form id="crear-fondo-form" hx-post="/api/v1/agn/fondos" hx-encoding="multipart/form-data" hx-swap="none" @htmx:after-request="if(event.detail.successful) window.location.reload()">
            <div class="mb-4">
                <label class="block text-xs font-bold text-gray-600 mb-1">Código Oficial del Fondo</label>
                <input type="text" name="codigo" required placeholder="Ej. F-001" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
            </div>
            
            <div class="mb-4">
                <label class="block text-xs font-bold text-gray-600 mb-1">Nombre de la Entidad Productora</label>
                <input type="text" name="nombre" required placeholder="Ingrese el nombre completo de la entidad" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Acto Administrativo</label>
                    <div class="relative">
                        <input type="text" name="acto_administrativo" required placeholder="Resolución, Decreto, etc." class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                        <label class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-indigo-600 cursor-pointer">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                            <input type="file" name="archivo_acto" class="hidden" accept=".pdf">
                        </label>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Estado del Fondo</label>
                    <select name="estado" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors appearance-none">
                        <option value="ACTIVA">Fondo Abierto / Activo</option>
                        <option value="FUSIONADA">Fondo Fusionado</option>
                        <option value="SUPRIMIDA">Fondo Suprimido / Cerrado</option>
                    </select>
                </div>
            </div>
            
            <div class="flex justify-end gap-3 pt-2">
                <button type="button" onclick="Swal.close()" class="px-5 py-2.5 text-sm font-semibold text-gray-600 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" class="px-5 py-2.5 text-sm font-semibold text-white bg-[#4f46e5] hover:bg-[#4338ca] rounded-lg shadow-sm flex items-center gap-2 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                    Guardar Fondo
                </button>
            </div>
        </form>
    </div>
    <script>
        htmx.process(document.getElementById('crear-fondo-form'));
        
        document.body.addEventListener('htmx:responseError', function(evt) {
            if(evt.detail.elt.id === 'crear-fondo-form') {
                try {
                    const resp = JSON.parse(evt.detail.xhr.response);
                    Swal.fire('Error', resp.detail, 'error');
                } catch(e) {
                    Swal.fire('Error', 'Ocurrió un error en el servidor.', 'error');
                }
            }
        });
        document.body.addEventListener('htmx:afterRequest', function(evt) {
            if(evt.detail.elt.id === 'crear-fondo-form' && evt.detail.successful) {
                Swal.fire({
                    title: '¡Fondo Creado!',
                    text: 'El fondo documental ha sido registrado exitosamente.',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    // Reopen the main AGN modal
                    window.openAgnModal();
                });
            }
        });
    </script>
    """
    return HTMLResponse(html)

from fastapi import Form, UploadFile, File, HTTPException
import json

@router.post("/fondos")
async def create_agn_fondo(
    request: Request,
    codigo: str = Form(...),
    nombre: str = Form(...),
    acto_administrativo: str = Form(...),
    estado: str = Form(...),
    archivo_acto: UploadFile = File(None),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    ip_address = request.client.host if request.client else "unknown"
    
    # Check UNIQUE code
    check_q = text("SELECT id FROM agn_dependencias WHERE tenant_id = :t AND codigo = :c AND parent_id IS NULL")
    res = await db.execute(check_q, {"t": tenant_id, "c": codigo})
    if res.fetchone():
        raise HTTPException(status_code=400, detail=f"El código '{codigo}' ya existe como Fondo en este sistema.")
    
    # Save file logic would go here, for now we just keep the filename or None
    archivo_url = archivo_acto.filename if archivo_acto and archivo_acto.filename else None
    
    insert_q = text("""
        INSERT INTO agn_dependencias (tenant_id, codigo, nombre, tipo, parent_id, acto_administrativo, archivo_acto_url, estado)
        VALUES (:tenant, :codigo, :nombre, 'FONDO', NULL, :acto, :archivo, :estado)
        RETURNING id
    """)
    
    result = await db.execute(insert_q, {
        "tenant": tenant_id,
        "codigo": codigo,
        "nombre": nombre,
        "acto": acto_administrativo,
        "archivo": archivo_url,
        "estado": estado
    })
    
    new_id = str(result.scalar())
    
    # Audit Logging
    audit_q = text("""
        INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles)
        VALUES (:accion, :user_id, :ip, :detalles)
    """)
    await db.execute(audit_q, {
        "accion": "CREAR_FONDO_AGN",
        "user_id": user_id,
        "ip": ip_address,
        "detalles": json.dumps({"fondo_id": new_id, "codigo": codigo, "nombre": nombre, "estado": estado})
    })
    
    await db.commit()
    
    return JSONResponse({"status": "success", "id": new_id})
'''

# Use binary mode to avoid BOM and ensure clean UTF-8
with open('app/routers/agn.py', 'wb') as f:
    f.write((content + new_endpoints).encode('utf-8'))
