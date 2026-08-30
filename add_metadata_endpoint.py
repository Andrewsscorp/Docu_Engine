with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

endpoint_code = """
@router.get("/expedientes/{expediente_id}/metadata")
async def get_expediente_metadata(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    query = '''
        SELECT e.codigo_expediente, e.nombre_expediente, e.fecha_apertura, e.estado_abierto, e.fase_archivo, e.soporte,
               d.nombre as fondo_nombre,
               s.codigo as serie_codigo, s.nombre as serie_nombre, s.retencion_ag as s_ag, s.retencion_ac as s_ac, s.disposicion as s_disp,
               ss.codigo as subserie_codigo, ss.nombre as subserie_nombre, ss.retencion_ag as ss_ag, ss.retencion_ac as ss_ac, ss.disposicion as ss_disp,
               u.username as responsable
        FROM agn_expedientes e
        LEFT JOIN agn_dependencias d ON e.fondo_id = d.id
        LEFT JOIN agn_series s ON e.serie_id = s.id
        LEFT JOIN agn_subseries ss ON e.subserie_id = ss.id
        LEFT JOIN users u ON e.responsable_id = CAST(u.id AS VARCHAR)
        WHERE e.id = :eid AND e.tenant_id = :t
    '''
    res = await db.execute(text(query), {"eid": expediente_id, "t": session_data["tenant_id"]})
    row = res.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
        
    d = dict(row._mapping)
    ag = d.get('ss_ag') if d.get('subserie_codigo') else d.get('s_ag')
    ac = d.get('ss_ac') if d.get('subserie_codigo') else d.get('s_ac')
    disp = d.get('ss_disp') if d.get('subserie_codigo') else d.get('s_disp')
    
    html = f'''
    <div class="text-left space-y-4 text-sm text-gray-700">
        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
            <p class="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">Clasificación TRD</p>
            <p><b>Fondo:</b> {d.get("fondo_nombre", "N/A")}</p>
            <p><b>Serie:</b> {d.get("serie_codigo", "")} - {d.get("serie_nombre", "")}</p>
            <p><b>Subserie:</b> {d.get("subserie_codigo", "")} - {d.get("subserie_nombre", "N/A")}</p>
        </div>
        <div class="bg-amber-50 p-3 rounded-lg border border-amber-200">
            <p class="text-xs text-amber-600 uppercase font-bold tracking-wider mb-1">Reglas de Retención</p>
            <p><b>Archivo de Gestión:</b> {ag} Años</p>
            <p><b>Archivo Central:</b> {ac} Años</p>
            <p><b>Disposición Final:</b> {disp}</p>
        </div>
        <div class="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <p class="text-xs text-blue-600 uppercase font-bold tracking-wider mb-1">Detalles del Contenedor</p>
            <p><b>Responsable:</b> {d.get("responsable", "Sin Asignar")}</p>
            <p><b>Fase Actual:</b> {d.get("fase_archivo", "")}</p>
            <p><b>Estado:</b> {"Abierto" if d.get("estado_abierto") else "Cerrado"}</p>
        </div>
    </div>
    '''
    return HTMLResponse(html)
"""

if "@router.get(\"/expedientes/{expediente_id}/metadata\")" not in content:
    content = content.replace("async def get_expedientes_module(", endpoint_code + "\n\nasync def get_expedientes_module(")
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added get_expediente_metadata endpoint")
else:
    print("Endpoint already exists")
