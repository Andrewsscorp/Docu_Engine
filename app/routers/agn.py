from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi import Form, UploadFile, File, HTTPException, Query
import json
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db_session, AsyncSessionLocal
from app.security import require_permission
from datetime import datetime

router = APIRouter(prefix="/api/v1/agn", tags=["agn"])

@router.get("/modal")
async def get_agn_modal(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    
    # Fetch Fondos
    fondos_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_dependencias WHERE tipo = 'FONDO' AND estado = 'ABIERTO' AND tenant_id = :t"), {"t": tenant_id})
    fondos = fondos_res.fetchall()
    
    # Fetch Secciónes
    secciones_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_dependencias WHERE tipo = 'SECCION' AND tenant_id = :t"), {"t": tenant_id})
    secciones = secciones_res.fetchall()

    # Fetch Subsecciones
    subsecciones_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_dependencias WHERE tipo = 'SUBSECCION' AND tenant_id = :t"), {"t": tenant_id})
    subsecciones = subsecciones_res.fetchall()

    
    # Fetch Series
    series_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_series WHERE tenant_id = :t AND estado_activa = TRUE"), {"t": tenant_id})
    series = series_res.fetchall()
    
    # Fetch Subseries
    subseries_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_subseries WHERE tenant_id = :t AND estado_activa = TRUE"), {"t": tenant_id})
    subseries = subseries_res.fetchall()
    
    codigo_expediente = "ALC-SECED-CON-PS-2026-003"
    
    today = datetime.now().strftime('%Y-%m-%d')
    username = session_data.get("username", "Admin")

    html = f"""
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-blue-50/50">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center border border-gray-200">
                <span class="text-xs font-bold text-gray-700">AGN</span>
            </div>
            <div>
                <h2 class="text-xl font-bold text-gray-800 font-sans">CREAR NUEVO EXPEDIENTE ELECTRÓNICO</h2>
                <p class="text-sm font-semibold text-gray-600">(Acuerdo 001/2024 AGN)</p>
            </div>
        </div>
    </div>
    <div class="p-6">
        
    
    <form id="agn-expediente-form" x-data="{{
    previewCode: 'Seleccione la clasificación documental para generar el código...',
    updatePreview() {{
        const getCode = (selectId) => {{
            const select = document.getElementById(selectId);
            if (!select || !select.value) return '';
            const option = select.options[select.selectedIndex];
            return option.getAttribute('data-codigo') || '';
        }};
        const f = getCode('fondo_select');
        const sec = getCode('seccion_select');
        const subsec = getCode('subseccion_select');
        const ser = getCode('serie_select');
        const subser = getCode('subserie_select');
        const fecha = document.getElementById('fecha_apertura')?.value;
        const year = fecha ? fecha.split('-')[0] : new Date().getFullYear();
        
        let parts = [];
        if (f) parts.push(f);
        if (sec) parts.push(sec);
        if (subsec) parts.push(subsec);
        if (ser) parts.push(ser);
        if (subser) parts.push(subser);
        
        if (parts.length > 0) {{
            parts.push(year);
            parts.push('XXX');
            this.previewCode = parts.join('-');
        }} else {{
            this.previewCode = 'Seleccione la clasificación documental para generar el código...';
        }}
    }}
}}" x-init="updatePreview()" onsubmit="event.preventDefault(); window.submitAgnExpediente();">

            <h3 class="text-md font-bold text-gray-800 mb-3">1. Clasificación Documental (CCD/TRD)</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                    <div class="flex justify-between items-center mb-1">
                    <label class="block text-sm font-semibold text-gray-600">Fondo:</label>
                    <div class="flex items-center gap-1">
                        <button type="button" onclick="window.openCrearFondoModal()" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>
                        <div class="relative group flex items-center">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full right-0 mb-1 w-max px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100]">
                                Entidad productora u organismo que ha reunido o generado los documentos.
                                <div class="absolute top-full right-1 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div>
                    </div>
                </div>
                    <select id="fondo_select" name="fondo" @change="updatePreview()" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        {"".join([f'<option value="{f.id}" data-codigo="{f.codigo}">{f.nombre}</option>' for f in fondos])}
                    </select>
                </div>
                <div>
                    <div class="flex justify-between items-center mb-1">
                    <label class="block text-sm font-semibold text-gray-600">Sección:</label>
                    <div class="flex items-center gap-1">
                        <button type="button" onclick="window.openCrearSeccionModal()" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>
                        <div class="relative group flex items-center">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full right-0 mb-1 w-max px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100]">
                                Dependencia administrativa de alto nivel (ej. Dirección, Secretaría).
                                <div class="absolute top-full right-1 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div>
                    </div>
                </div>
                    <select id="seccion_select" name="seccion" @change="updatePreview()" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        {"".join([f'<option value="{s.id}" data-codigo="{s.codigo}">{s.nombre}</option>' for s in secciones])}
                    </select>
                </div>
                <div>
                    <div class="flex justify-between items-center mb-1">
                    <label class="block text-sm font-semibold text-gray-600">Subsección (Opcional):</label>
                    <div class="flex items-center gap-1">
                        <button type="button" onclick="window.openCrearSubseccionModal()" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>
                        <div class="relative group flex items-center">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full right-0 mb-1 w-max px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100]">
                                Unidad administrativa operativa o grupo de trabajo subordinado.
                                <div class="absolute top-full right-1 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div>
                    </div>
                </div>
                    <select id="subseccion_select" name="subseccion" @change="updatePreview()" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        <option value="">-- Seleccionar --</option>
                        {"".join([f'<option value="{s.id}" data-codigo="{s.codigo}">{s.nombre}</option>' for s in subsecciones])}
                    </select>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <div class="flex justify-between items-center mb-1">
                    <label class="block text-sm font-semibold text-gray-600">Serie:</label>
                    <div class="flex items-center gap-1">
                        <button type="button" onclick="window.openCrearSerieModal()" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>
                        <div class="relative group flex items-center">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full right-0 mb-1 w-max px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100]">
                                Conjunto de expedientes con estructura y contenido homogéneos.
                                <div class="absolute top-full right-1 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div>
                    </div>
                </div>
                    <select id="serie_select" name="serie" @change="updatePreview()" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        {"".join([f'<option value="{s.id}" data-codigo="{s.codigo}">{s.nombre}</option>' for s in series])}
                    </select>
                </div>
                <div>
                    <div class="flex justify-between items-center mb-1">
                    <label class="block text-sm font-semibold text-gray-600">Subserie (Opcional):</label>
                    <div class="flex items-center gap-1">
                        <button type="button" onclick="window.openCrearSubserieModal()" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>
                        <div class="relative group flex items-center">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full right-0 mb-1 w-max px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100]">
                                División de la serie documental según un trámite específico.
                                <div class="absolute top-full right-1 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div>
                    </div>
                </div>
                    <select id="subserie_select" name="subserie" @change="updatePreview()" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        <option value="">-- Seleccionar --</option>
                        {"".join([f'<option value="{s.id}" data-codigo="{s.codigo}">{s.nombre}</option>' for s in subseries])}
                    </select>
                </div>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-semibold text-gray-600 mb-1">Código de Expediente (Generado Automáticamente):</label>
                <input type="text" readonly :value="previewCode" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-100 font-mono text-gray-800 font-bold">
                <p class="text-xs text-gray-500 mt-1">Este código es único e inmutable.</p>
            </div>
            
            <h3 class="text-md font-bold text-gray-800 mb-3">2. Identificación del Expediente</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Nombre del Expediente:*</label>
                    <input type="text" name="nombre_expediente" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Asunto:*</label>
                    <textarea name="asunto" rows="2" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary"></textarea>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Fecha de Apertura:*</label>
                    <input type="date" id="fecha_apertura" name="fecha_apertura" max="{today}" @change="updatePreview()" required value="{today}" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Responsable:*</label>
                    <select name="responsable" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50">
                        <option value="{session_data['user_id']}">{username}</option>
                    </select>
                </div>
            </div>
            
            <h3 class="text-md font-bold text-gray-800 mb-3">3. Controles y Acciones</h3>
            <div class="space-y-2 mb-6">
                <label class="flex items-start gap-2 cursor-pointer">
                    <input type="checkbox" name="confirmTrd" x-model="confirmTrd" required class="mt-1 border-gray-300 rounded text-primary focus:ring-primary">
                    <span class="text-sm text-gray-700">Confirmo que la clasificación corresponde a la TRD vigente.</span>
                </label>
                <label class="flex items-start gap-2 cursor-pointer">
                    <input type="checkbox" name="confirmImmutable" x-model="confirmImmutable" required class="mt-1 border-gray-300 rounded text-primary focus:ring-primary">
                    <span class="text-sm text-gray-700">Entiendo que este expediente generará un índice electrónico inmutable.</span>
                </label>
            </div>
            
            <div class="flex justify-center gap-3">
                <button type="submit" :disabled="!canSubmit" :class="canSubmit ? \'bg-green-600 hover:bg-green-700\' : \'bg-gray-400 cursor-not-allowed\'" class="px-6 py-2.5 text-sm font-bold text-white bg-green-600 hover:bg-green-700 rounded-lg shadow-sm flex items-center gap-2 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    Crear Expediente
                </button>
                <button type="button" onclick="Swal.close()" class="px-5 py-2.5 text-sm font-medium text-white bg-gray-500 hover:bg-gray-600 rounded-lg transition-colors">Cancelar</button>
            </div>
        </form>
    </div>
    """
    
    return HTMLResponse(html)


@router.get("/consecutivo_preview")
async def get_consecutivo_preview(
    tenant_id: str = Query(...),
    seccion_id: str = Query(...),
    serie_id: str = Query(...),
    anio: int = Query(...),
    subseccion_id: str = Query(None),
    subserie_id: str = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    subsec = subseccion_id if subseccion_id and subseccion_id.strip() else None
    subser = subserie_id if subserie_id and subserie_id.strip() else None

    # Query WITHOUT locking just to get the current sequence
    q = text('''
        SELECT ultimo_consecutivo 
        FROM agn_consecutivos 
        WHERE tenant_id = :tenant 
          AND seccion_id = :sec 
          AND serie_id = :ser 
          AND (subseccion_id = :subsec OR (subseccion_id IS NULL AND :subsec IS NULL))
          AND (subserie_id = :subser OR (subserie_id IS NULL AND :subser IS NULL))
          AND anio = :anio 
    ''')
    
    res = await db.execute(q, {
        "tenant": tenant_id, "sec": seccion_id, "ser": serie_id, 
        "subsec": subsec, "subser": subser, "anio": anio
    })
    row = res.fetchone()
    
    if row:
        return {"next": str(row.ultimo_consecutivo + 1).zfill(3)}
    else:
        return {"next": "001"}


@router.post("/expedientes")
async def create_agn_expediente(
    request: Request,
    fondo: str = Form(...),
    seccion: str = Form(...),
    subseccion: str = Form(None),
    serie: str = Form(...),
    subserie: str = Form(None),
    nombre_expediente: str = Form(...),
    asunto: str = Form(None),
    fecha_apertura: str = Form(...),
    responsable: str = Form(...),
    confirmTrd: str = Form(None),
    confirmImmutable: str = Form(None),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import html
    from datetime import datetime
    tenant_id = session_data["tenant_id"]
    
    if not confirmTrd or not confirmImmutable:
        raise HTTPException(status_code=400, detail="Debe confirmar los términos legales (TRD e Índice) para crear el contenedor.")

    nombre_sanitizado = html.escape(nombre_expediente.strip())[:255]
    asunto_sanitizado = html.escape(asunto.strip())[:500] if asunto else ""
    
    try:
        dt = datetime.strptime(fecha_apertura, '%Y-%m-%d')
        year = dt.year
    except Exception:
        raise HTTPException(status_code=400, detail="Fecha de apertura inválida")
        
    # Validation
    q_fondo = text("SELECT estado FROM agn_dependencias WHERE id = :id AND tipo = 'FONDO'")
    res = await db.execute(q_fondo, {"id": fondo})
    estado_fondo = res.scalar()
    
    if estado_fondo == 'CERRADO':
        raise HTTPException(status_code=403, detail="Violación Normativa: El Fondo Documental se encuentra CERRADO (Acumulado). Está estrictamente prohibido por el AGN generar nuevos expedientes bajo esta raíz.")

    consecutivo = 1
    
    subsec_id = subseccion if subseccion and subseccion.strip() else None
    subser_id = subserie if subserie and subserie.strip() else None

    # Lógica Normativa: Bloqueo de Transacciones (Pessimistic Locking)
    lock_q = text('''
        SELECT id, ultimo_consecutivo 
        FROM agn_consecutivos 
        WHERE tenant_id = :tenant 
          AND seccion_id = :sec 
          AND serie_id = :ser 
          AND (subseccion_id = :subsec OR (subseccion_id IS NULL AND :subsec IS NULL))
          AND (subserie_id = :subser OR (subserie_id IS NULL AND :subser IS NULL))
          AND anio = :anio 
        FOR UPDATE
    ''')
    
    lock_res = await db.execute(lock_q, {
        "tenant": tenant_id, "sec": seccion, "ser": serie, 
        "subsec": subsec_id, "subser": subser_id, "anio": year
    })
    row = lock_res.fetchone()
    
    if row:
        consecutivo = row.ultimo_consecutivo + 1
        await db.execute(text("UPDATE agn_consecutivos SET ultimo_consecutivo = :c WHERE id = :id"), {"c": consecutivo, "id": row.id})
    else:
        # Prevent race condition inserting the sequence row by relying on the unique constraint if needed, 
        # but in most cases, this is safe enough in async if not intensely hammered.
        try:
            await db.execute(text('''
                INSERT INTO agn_consecutivos (tenant_id, seccion_id, serie_id, subseccion_id, subserie_id, anio, ultimo_consecutivo)
                VALUES (:tenant, :sec, :ser, :subsec, :subser, :anio, 1)
            '''), {
                "tenant": tenant_id, "sec": seccion, "ser": serie, 
                "subsec": subsec_id, "subser": subser_id, "anio": year
            })
        except Exception:
            # If it fails, another thread inserted it. Retry lock.
            lock_res = await db.execute(lock_q, {
                "tenant": tenant_id, "sec": seccion, "ser": serie, 
                "subsec": subsec_id, "subser": subser_id, "anio": year
            })
            row = lock_res.fetchone()
            consecutivo = row.ultimo_consecutivo + 1
            await db.execute(text("UPDATE agn_consecutivos SET ultimo_consecutivo = :c WHERE id = :id"), {"c": consecutivo, "id": row.id})

    # Construcción del Código Completo
    codigo_parts = []
    
    f_res = await db.execute(text("SELECT codigo FROM agn_dependencias WHERE id = :id"), {"id": fondo})
    fc = f_res.fetchone()
    if fc: codigo_parts.append(fc.codigo)
    
    s_res = await db.execute(text("SELECT codigo FROM agn_dependencias WHERE id = :id"), {"id": seccion})
    sc = s_res.fetchone()
    if sc: codigo_parts.append(sc.codigo)
    
    if subsec_id:
        ss_res = await db.execute(text("SELECT codigo FROM agn_dependencias WHERE id = :id"), {"id": subsec_id})
        ssc = ss_res.fetchone()
        if ssc: codigo_parts.append(ssc.codigo)
        
    se_res = await db.execute(text("SELECT codigo FROM agn_series WHERE id = :id"), {"id": serie})
    sec = se_res.fetchone()
    if sec: codigo_parts.append(sec.codigo)
    
    if subser_id:
        sse_res = await db.execute(text("SELECT codigo FROM agn_subseries WHERE id = :id"), {"id": subser_id})
        ssec = sse_res.fetchone()
        if ssec: codigo_parts.append(ssec.codigo)
        
    codigo_parts.append(str(year))
    codigo_parts.append(f"{consecutivo:03d}")
    
    codigo_final = "-".join(codigo_parts)
    
    # Insert Expediente
    ins_q = text('''
        INSERT INTO agn_expedientes 
        (tenant_id, fondo_id, seccion_id, subseccion_id, serie_id, subserie_id, anio, consecutivo, codigo_expediente, nombre_expediente, asunto, fecha_apertura, responsable_id)
        VALUES 
        (:t, :f, :sec, :subsec, :ser, :subser, :a, :c, :cod, :nom, :asunto, :fa, :r)
        RETURNING id
    ''')
    
    res_exp = await db.execute(ins_q, {
        "t": tenant_id, "f": fondo, "sec": seccion, "subsec": subsec_id, 
        "ser": serie, "subser": subser_id, "a": year, "c": consecutivo, 
        "cod": codigo_final, "nom": nombre_sanitizado, "asunto": asunto_sanitizado, 
        "fa": dt, "r": responsable
    })
    exp_id = res_exp.scalar()
    
    # Generate First Index (Apertura)
    import hashlib
    xml_seed = f"<IndiceElectronico><Expediente>{codigo_final}</Expediente><Apertura>{dt.isoformat()}</Apertura></IndiceElectronico>"
    xml_hash = hashlib.sha256(xml_seed.encode()).hexdigest()
    
    await db.execute(text('''
        INSERT INTO agn_indice_electronico (expediente_id, accion, usuario_id, firma_indice)
        VALUES (:exp, 'APERTURA_EXPEDIENTE', :uid, :hash)
    '''), {"exp": exp_id, "uid": session_data['user_id'], "hash": xml_hash})
    
    # Inserción en Log de Auditoría Legal (No Repudio)
    import json
    client_ip = request.client.host if request.client and request.client.host else "127.0.0.1"
    payload_legal = {
        "trd_confirmada": True if confirmTrd else False,
        "acepta_inmutabilidad": True if confirmImmutable else False,
        "user_agent": request.headers.get("user-agent", "Unknown")
    }
    
    await db.execute(text('''
        INSERT INTO log_auditoria_sgdea (id_expediente, id_usuario, tipo_evento, ip_origen, payload_legal)
        VALUES (:exp_id, :usr_id, 'CREACION_EXPEDIENTE', :ip, :payload)
    '''), {
        "exp_id": exp_id, 
        "usr_id": session_data['user_id'], 
        "ip": client_ip, 
        "payload": json.dumps(payload_legal)
    })
    
    await db.commit()
    
    return JSONResponse({"status": "success", "message": "Expediente electrónico creado.", "codigo_expediente": codigo_final})

@router.get("/modal/fondo")
async def get_crear_fondo_modal(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
):
    html = f"""
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white">
        <div class="flex items-center gap-3">
            <button type="button" onclick="window.openAgnModal()" class="text-[#4f46e5] hover:text-[#4338ca] hover:bg-indigo-50 p-1.5 rounded-md transition-colors" title="Volver al Expediente">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </button>
            <h2 class="text-xl font-bold text-[#1e293b] font-sans">CREAR NUEVO FONDO DOCUMENTAL</h2>
        </div>
        <button type="button" onclick="Swal.close()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    </div>
    <div class="p-6 bg-[#f8fafc]">
        <form id="crear-fondo-form" hx-post="/api/v1/agn/fondos" hx-encoding="multipart/form-data" hx-swap="none" @htmx:after-request.camel="if($event.detail.successful) {{ Swal.fire({{title: 'Fondo Creado!', text: 'Guardado exitosamente', icon: 'success', timer: 1500, showConfirmButton: false}}).then(() => {{ window.openAgnModal(); }}) }}" @htmx:response-error.camel="Swal.fire('Error', JSON.parse($event.detail.xhr.response).detail || 'Ocurrió un error al guardar', 'error')">
            <div class="mb-4">
                <div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Código Oficial del Fondo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Identificador alfanumérico único e irrepetible asignado a la entidad.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>
                <input type="text" name="codigo" required placeholder="Ej. F-001" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
            </div>
            
            <div class="mb-4">
                <div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Nombre de la Entidad Productora</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Razón social legal y completa de la institución productora.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>
                <input type="text" name="nombre" required placeholder="Ingrese el nombre completo de la entidad" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div x-data="{{ fileName: '' }}">
                    <div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Acto Administrativo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Ley, decreto o resolución que crea formalmente la entidad.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>
                    <div class="relative">
                        <input type="text" name="acto_administrativo" placeholder="Resolución, Decreto, etc." class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                        <label class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-indigo-600 cursor-pointer">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                            <input type="file" x-ref="fileInput" name="archivo_acto" class="hidden" accept=".pdf" @change="fileName = $refs.fileInput.files[0] ? $refs.fileInput.files[0].name : ''">
                        </label>
                    </div>
                    
                    <template x-if="fileName">
                        <div class="mt-2 flex items-center justify-between px-3 py-1.5 bg-indigo-50 border border-indigo-100 rounded text-xs text-indigo-700 shadow-sm animate-fade-in-down">
                            <div class="flex items-center gap-2 truncate">
                                <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                <span x-text="fileName" class="truncate font-medium"></span>
                            </div>
                            <button type="button" @click="$refs.fileInput.value = ''; fileName = ''" class="ml-2 text-indigo-400 hover:text-red-500 focus:outline-none transition-colors">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                            </button>
                        </div>
                    </template>
                </div>
                <div>
                    <div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Estado del Fondo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Condición activa o liquidada para habilitar o restringir expedientes.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>
                    <select name="estado" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors appearance-none">
                        <option value="ABIERTO">Fondo Abierto (Activo)</option>
                        <option value="CERRADO">Fondo Cerrado (Acumulado)</option>
                    </select>
                </div>
            </div>
            
            
            <div class="flex justify-end gap-3 pt-2">
                <button type="button" onclick="window.openAgnModal()" class="px-5 py-2.5 text-sm font-semibold text-gray-600 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" :disabled="!canSubmit" :class="canSubmit ? \'bg-green-600 hover:bg-green-700\' : \'bg-gray-400 cursor-not-allowed\'" class="px-5 py-2.5 text-sm font-semibold text-white bg-[#4f46e5] hover:bg-[#4338ca] rounded-lg shadow-sm flex items-center gap-2 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                    Guardar Fondo
                </button>
            </div>
        </form>
        

    </div>
    
    """
    return HTMLResponse(html)


@router.post("/fondos")
async def create_agn_fondo(
    request: Request,
    codigo: str = Form(...),
    nombre: str = Form(...),
    acto_administrativo: str = Form(None),
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
        INSERT INTO audit_rbac_logs (tenant_id, action, performed_by_user_id, details)
        VALUES (:tenant, :action, :user_id, :details)
    """)
    await db.execute(audit_q, {
        "tenant": tenant_id,
        "action": "CREAR_FONDO_AGN",
        "user_id": user_id,
        "details": json.dumps({"ip_origen": ip_address, "fondo_id": new_id, "codigo": codigo, "nombre": nombre, "estado": estado})
    })
    
    await db.commit()
    
    return JSONResponse({"status": "success", "id": new_id})


class CerrarFondoRequest(BaseModel):
    fecha_cierre: str
    soporte_cierre: str

@router.put("/fondos/{fondo_id}/cerrar")
async def cerrar_fondo(
    fondo_id: str,
    payload: CerrarFondoRequest,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    ip_address = request.client.host if request.client else "unknown"
    
    # Verify the fondo exists and is currently open
    q_check = text("SELECT id, estado FROM agn_dependencias WHERE id = :id AND tipo = 'FONDO' AND tenant_id = :t")
    res = await db.execute(q_check, {"id": fondo_id, "t": tenant_id})
    fondo = res.fetchone()
    
    if not fondo:
        raise HTTPException(status_code=404, detail="Fondo no encontrado.")
    if fondo[1] == 'CERRADO':
        raise HTTPException(status_code=400, detail="El fondo ya se encuentra cerrado.")
        
    # Perform the closure
    q_update = text('''
        UPDATE agn_dependencias 
        SET estado = 'CERRADO', fecha_cierre = :fecha::timestamp, soporte_cierre = :soporte 
        WHERE id = :id
    ''')
    await db.execute(q_update, {
        "fecha": payload.fecha_cierre,
        "soporte": payload.soporte_cierre,
        "id": fondo_id
    })
    
    # Audit Logging for this critical action
    audit_q = text('''
        INSERT INTO audit_rbac_logs (tenant_id, action, target_id, performed_by_user_id, details)
        VALUES (:tenant, :action, :target_id, :user_id, :details)
    ''')
    await db.execute(audit_q, {
        "tenant": tenant_id,
        "action": "CERRAR_FONDO_AGN",
        "target_id": fondo_id,
        "user_id": user_id,
        "details": json.dumps({"ip_origen": ip_address, "fecha_cierre": payload.fecha_cierre, "soporte": payload.soporte_cierre})
    })
    
    await db.commit()
    
    return JSONResponse({"status": "success", "message": "El Fondo Documental ha sido clausurado legalmente y preservado."})


@router.get("/modal/seccion")
async def get_crear_seccion_modal(
    request: Request,
    fondo_id: str,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    fondo_res = await db.execute(text("SELECT nombre, codigo FROM agn_dependencias WHERE id = :id AND tipo = 'FONDO'"), {"id": fondo_id})
    fondo = fondo_res.fetchone()
    fondo_text = f"{fondo.nombre} (Código: {fondo.codigo})" if fondo else "Fondo Desconocido"
    
    html = f'''
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white">
        <div class="flex items-center gap-3">
            <button type="button" onclick="window.openAgnModal()" class="text-[#4f46e5] hover:text-[#4338ca] hover:bg-indigo-50 p-1.5 rounded-md transition-colors" title="Volver al Expediente">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </button>
            <h2 class="text-xl font-bold text-[#1e293b] font-sans uppercase">Crear Nueva Sección (Dependencia)</h2>
        </div>
        <button type="button" onclick="Swal.close()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    </div>
    <div class="p-6 bg-[#f8fafc]">
        <form id="crear-seccion-form" hx-post="/api/v1/agn/secciones" hx-encoding="multipart/form-data" hx-swap="none" @htmx:after-request.camel="if($event.detail.successful) {{ Swal.fire({{title: '¡Sección Creada!', text: 'Guardado exitosamente', icon: 'success', timer: 1500, showConfirmButton: false}}).then(() => {{ window.openAgnModal(); }}) }}" @htmx:response-error.camel="Swal.fire('Error', JSON.parse($event.detail.xhr.response).detail || 'Ocurrió un error al guardar', 'error')">
            <input type="hidden" name="fondo_id" value="{fondo_id}">
            
            <div class="mb-4">
                <label class="block text-xs font-bold text-gray-600 mb-1">Fondo Documental Padre</label>
                <div class="relative">
                    <input type="text" readonly value="{fondo_text}" class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-100 text-gray-500 font-medium select-none outline-none">
                    <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                    </div>
                </div>
                <p class="text-[10px] text-gray-500 mt-1 font-semibold">Este campo es heredado y no puede ser modificado.</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Código de la Sección <div class="relative group inline-flex items-center ml-1">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 px-2 py-1.5 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] text-center leading-tight">
                                Segundo eslabón de clasificación. Debe ser único dentro de este Fondo (Ej. 110).
                                <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div></label>
                    <input type="text" name="codigo" required placeholder="Ej: 110" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Nombre de la Dependencia <div class="relative group inline-flex items-center ml-1">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 px-2 py-1.5 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] text-center leading-tight">
                                Nombre oficial de la oficina o grupo de trabajo que produce los documentos.
                                <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div></label>
                    <input type="text" name="nombre" required placeholder="Ej: Secretaría de Hacienda" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div x-data="{{ fileName: '' }}">
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Acto Administrativo y Funciones <div class="relative group inline-flex items-center ml-1">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 px-2 py-1.5 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] text-center leading-tight">
                                Ley, decreto o resolución que respalda la creación jurídica de esta oficina. ¡Debe adjuntar el PDF!
                                <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div></label>
                    <div class="relative">
                        <input type="text" name="acto_administrativo" placeholder="Resolución de creación..." class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                        <label class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-indigo-600 cursor-pointer" title="Adjuntar PDF">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                            <input type="file" x-ref="fileInput" name="archivo_acto" class="hidden" accept=".pdf" @change="fileName = $refs.fileInput.files[0] ? $refs.fileInput.files[0].name : ''">
                        </label>
                    </div>
                    <template x-if="fileName">
                        <div class="mt-2 flex items-center justify-between px-3 py-1.5 bg-indigo-50 border border-indigo-100 rounded text-xs text-indigo-700 shadow-sm">
                            <div class="flex items-center gap-2 truncate">
                                <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                <span x-text="fileName" class="truncate font-medium"></span>
                            </div>
                            <button type="button" @click="$refs.fileInput.value = ''; fileName = ''" class="ml-2 text-indigo-400 hover:text-red-500 focus:outline-none">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                            </button>
                        </div>
                    </template>
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Estado de la Sección <div class="relative group inline-flex items-center ml-1">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 px-2 py-1.5 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] text-center leading-tight">
                                Si la oficina fue liquidada, márquela como Inactiva para bloquear la creación de nuevos expedientes.
                                <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div></label>
                    <select name="estado" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors appearance-none">
                        <option value="ABIERTO">Activa</option>
                        <option value="CERRADO">Inactiva (Liquidada)</option>
                    </select>
                </div>
            </div>
            
            <div class="flex justify-end gap-3 pt-2">
                <button type="button" onclick="window.openAgnModal()" class="px-5 py-2.5 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" @click="if(!$el.form.checkValidity()) $el.form.reportValidity()" class="px-5 py-2.5 text-sm font-bold text-white bg-[#10b981] hover:bg-[#059669] rounded-lg shadow-sm transition-colors">
                    Guardar Sección
                </button>
            </div>
        </form>
    </div>
    '''
    return HTMLResponse(content=html)


@router.post("/secciones")
async def create_agn_seccion(
    request: Request,
    fondo_id: str = Form(...),
    codigo: str = Form(...),
    nombre: str = Form(...),
    acto_administrativo: str = Form(None),
    estado: str = Form(...),
    archivo_acto: UploadFile = File(None),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    ip_address = request.client.host

    codigo = codigo.strip().upper()
    nombre = nombre.strip().upper()

    check_q = text("SELECT id FROM agn_dependencias WHERE tenant_id = :t AND parent_id = :p AND codigo = :c")
    existing = await db.execute(check_q, {"t": tenant_id, "p": fondo_id, "c": codigo})
    if existing.fetchone():
        raise HTTPException(status_code=400, detail="El código de Sección ya existe para este Fondo.")

    archivo_url = None
    if archivo_acto and archivo_acto.filename:
        archivo_url = f"/uploads/{archivo_acto.filename}"

    insert_q = text("""
        INSERT INTO agn_dependencias (tenant_id, codigo, nombre, tipo, parent_id, acto_administrativo, archivo_acto_url, estado)
        VALUES (:tenant, :codigo, :nombre, 'SECCION', :fondo_id, :acto, :archivo, :estado)
        RETURNING id
    """)
    result = await db.execute(insert_q, {
        "tenant": tenant_id,
        "codigo": codigo,
        "nombre": nombre,
        "fondo_id": fondo_id,
        "acto": acto_administrativo,
        "archivo": archivo_url,
        "estado": estado
    })
    new_id = str(result.scalar())

    import json
    audit_q = text("""
        INSERT INTO audit_rbac_logs (tenant_id, action, target_id, performed_by_user_id, details)
        VALUES (:tenant, :action, :target_id, :user_id, :details)
    """)
    await db.execute(audit_q, {
        "tenant": tenant_id,
        "action": "CREAR_SECCION_AGN",
        "target_id": new_id,
        "user_id": user_id,
        "details": json.dumps({"ip_origen": ip_address, "fondo_id": fondo_id, "codigo": codigo, "nombre": nombre, "estado": estado})
    })

    await db.commit()
    warning = "No se anexó documento PDF de Acto Administrativo o Resolución." if not archivo_url else None
    return {"status": "success", "id": new_id, "warning": warning}



@router.get("/modal/subseccion")
async def get_crear_subseccion_modal(
    request: Request,
    fondo_id: str,
    seccion_id: str,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    fondo_res = await db.execute(text("SELECT nombre, codigo FROM agn_dependencias WHERE id = :id AND tipo = 'FONDO'"), {"id": fondo_id})
    fondo = fondo_res.fetchone()
    fondo_text = f"{fondo.nombre} (Código: {fondo.codigo})" if fondo else "Fondo Desconocido"
    
    seccion_res = await db.execute(text("SELECT nombre, codigo FROM agn_dependencias WHERE id = :id AND tipo = 'SECCION'"), {"id": seccion_id})
    seccion = seccion_res.fetchone()
    seccion_text = f"{seccion.nombre} (Código: {seccion.codigo})" if seccion else "Sección Desconocida"
    
    html = f'''
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white">
        <div class="flex items-center gap-3">
            <button type="button" onclick="window.openAgnModal()" class="text-[#4f46e5] hover:text-[#4338ca] hover:bg-indigo-50 p-1.5 rounded-md transition-colors" title="Volver al Expediente">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </button>
            <h2 class="text-xl font-bold text-[#1e293b] font-sans uppercase">Crear Nueva Subsección (Grupo de Trabajo)</h2>
        </div>
        <button type="button" onclick="Swal.close()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    </div>
    <div class="p-6 bg-[#f8fafc]">
        <form id="crear-subseccion-form" hx-post="/api/v1/agn/subsecciones" hx-encoding="multipart/form-data" hx-swap="none" @htmx:after-request.camel="let r=JSON.parse($event.detail.xhr.response); if($event.detail.successful) {{ if(r.warning){{Swal.fire({{title: 'Guardado con Advertencia', text: r.warning, icon: 'warning', confirmButtonText: 'Entendido'}}).then(()=>window.openAgnModal())}} else {{Swal.fire({{title: '¡Subsección Creada!', text: 'Guardado exitosamente', icon: 'success', timer: 1500, showConfirmButton: false}}).then(()=>window.openAgnModal())}} }}" @htmx:response-error.camel="Swal.fire('Error', JSON.parse($event.detail.xhr.response).detail || 'Ocurrió un error al guardar', 'error')">
            <input type="hidden" name="seccion_id" value="{seccion_id}">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1 uppercase">Fondo Padre</label>
                    <div class="relative">
                        <input type="text" readonly value="{fondo_text}" class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-100 text-gray-500 font-medium select-none outline-none">
                        <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1 uppercase">Sección Padre</label>
                    <div class="relative">
                        <input type="text" readonly value="{seccion_text}" class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-100 text-gray-500 font-medium select-none outline-none">
                        <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Código de la Subsección <span class="text-red-500 ml-1">*</span></label>
                    <input type="text" name="codigo" required placeholder="Ej: SUB-001" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Nombre del Grupo de Trabajo <span class="text-red-500 ml-1">*</span></label>
                    <input type="text" name="nombre" required placeholder="Ingrese el nombre descriptivo" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div x-data="{{ fileName: '' }}">
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Acto Administrativo o Resolución</label>
                    <div class="relative">
                        <input type="text" name="acto_administrativo" placeholder="Adjuntar documento (PDF)..." class="w-full px-3 py-2 pr-16 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                        <label class="absolute right-2 top-1/2 -translate-y-1/2 cursor-pointer flex items-center">
                            <span class="text-[10px] font-bold text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded mr-1">Max 10MB</span>
                            <svg class="w-4 h-4 text-gray-400 hover:text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                            <input type="file" x-ref="fileInput" name="archivo_acto" class="hidden" accept=".pdf" @change="fileName = $refs.fileInput.files[0] ? $refs.fileInput.files[0].name : ''">
                        </label>
                    </div>
                    <template x-if="fileName">
                        <div class="mt-2 flex items-center justify-between px-3 py-1.5 bg-indigo-50 border border-indigo-100 rounded text-xs text-indigo-700 shadow-sm">
                            <div class="flex items-center gap-2 truncate">
                                <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                <span x-text="fileName" class="truncate font-medium"></span>
                            </div>
                            <button type="button" @click="$refs.fileInput.value = ''; fileName = ''" class="ml-2 text-indigo-400 hover:text-red-500 focus:outline-none">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                            </button>
                        </div>
                    </template>
                </div>
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Estado de la Subsección</label>
                    <select name="estado" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors appearance-none">
                        <option value="ABIERTO">Activa</option>
                        <option value="CERRADO">Inactiva (Desintegrado)</option>
                    </select>
                </div>
            </div>
            
            <div class="flex justify-end gap-3 pt-2">
                <button type="button" onclick="window.openAgnModal()" class="px-5 py-2.5 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" @click="if(!$el.form.checkValidity()) $el.form.reportValidity()" class="px-5 py-2.5 text-sm font-bold text-white bg-[#10b981] hover:bg-[#059669] rounded-lg shadow-sm transition-colors">
                    Guardar Subsección
                </button>
            </div>
        </form>
    </div>
    '''
    return HTMLResponse(content=html)


@router.post("/subsecciones")
async def create_agn_subseccion(
    request: Request,
    seccion_id: str = Form(...),
    codigo: str = Form(...),
    nombre: str = Form(...),
    acto_administrativo: str = Form(None),
    estado: str = Form(...),
    archivo_acto: UploadFile = File(None),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    ip_address = request.client.host

    codigo = codigo.strip().upper()
    nombre = nombre.strip().upper()

    check_q = text("SELECT id FROM agn_dependencias WHERE tenant_id = :t AND parent_id = :p AND codigo = :c")
    existing = await db.execute(check_q, {"t": tenant_id, "p": seccion_id, "c": codigo})
    if existing.fetchone():
        raise HTTPException(status_code=400, detail="El código de Subsección ya existe para esta Sección.")

    archivo_url = None
    if archivo_acto and archivo_acto.filename:
        archivo_url = f"/uploads/{archivo_acto.filename}"

    insert_q = text("""
        INSERT INTO agn_dependencias (tenant_id, codigo, nombre, tipo, parent_id, acto_administrativo, archivo_acto_url, estado)
        VALUES (:tenant, :codigo, :nombre, 'SUBSECCION', :seccion_id, :acto, :archivo, :estado)
        RETURNING id
    """)
    result = await db.execute(insert_q, {
        "tenant": tenant_id,
        "codigo": codigo,
        "nombre": nombre,
        "seccion_id": seccion_id,
        "acto": acto_administrativo,
        "archivo": archivo_url,
        "estado": estado
    })
    new_id = str(result.scalar())

    import json
    audit_q = text("""
        INSERT INTO audit_rbac_logs (tenant_id, action, target_id, performed_by_user_id, details)
        VALUES (:tenant, :action, :target_id, :user_id, :details)
    """)
    await db.execute(audit_q, {
        "tenant": tenant_id,
        "action": "CREAR_SUBSECCION_AGN",
        "target_id": new_id,
        "user_id": user_id,
        "details": json.dumps({"ip_origen": ip_address, "seccion_id": seccion_id, "codigo": codigo, "nombre": nombre, "estado": estado})
    })

    await db.commit()
    warning = "No se anexó documento PDF de Acto Administrativo o Resolución." if not archivo_url else None
    return {"status": "success", "id": new_id, "warning": warning}



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
        
    insert_q = text("""
        INSERT INTO agn_series (tenant_id, fondo_id, seccion_id, subseccion_id, codigo, nombre, retencion_ag, retencion_ac, disposicion, estado_activa)
        VALUES (:tenant, :fondo_id, :seccion_id, :subseccion_id, :codigo, :nombre, :ag, :ac, :disp, :estado)
        RETURNING id
    """)
    
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



@router.get("/modal/subserie")
async def get_crear_subserie_modal(
    request: Request,
    fondo_id: str,
    seccion_id: str,
    serie_id: str,
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
        
    serie_res = await db.execute(text("SELECT nombre, codigo FROM agn_series WHERE id = :id"), {"id": serie_id})
    serie = serie_res.fetchone()
    serie_text = f"{serie.codigo} - {serie.nombre}" if serie else "Serie Desconocida"
            
    html = f'''
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white">
        <div class="flex items-center gap-3">
            <button type="button" onclick="window.openAgnModal()" class="text-[#4f46e5] hover:text-[#4338ca] hover:bg-indigo-50 p-1.5 rounded-md transition-colors" title="Volver al Expediente">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </button>
            <h2 class="text-xl font-bold text-[#1e293b] font-sans uppercase">Crear Nueva Subserie Documental</h2>
        </div>
        <button type="button" onclick="Swal.close()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    </div>
    <div class="p-6 bg-[#f8fafc]">
        <form id="crear-subserie-form" hx-post="/api/v1/agn/subseries" hx-swap="none" @htmx:after-request.camel="let r=JSON.parse($event.detail.xhr.response); if($event.detail.successful) {{ Swal.fire({{title: '¡Subserie Creada!', text: 'Guardado exitosamente', icon: 'success', timer: 1500, showConfirmButton: false}}).then(()=>window.openAgnModal()) }} else {{ Swal.fire('Error', r.detail || 'Ocurrió un error', 'error') }}" @htmx:response-error.camel="Swal.fire('Error', JSON.parse($event.detail.xhr.response).detail || 'Ocurrió un error al guardar', 'error')">
            
            <input type="hidden" name="serie_id" value="{serie_id}">
            
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
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Serie Padre</label>
                    <div class="relative">
                        <input type="text" readonly value="{serie_text}" class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-200 text-gray-600 font-bold select-none outline-none truncate" title="{serie_text}">
                        <div class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Código de la Subserie <span class="text-red-500 ml-1">*</span>
                        <div class="relative group inline-flex items-center ml-1">
                            <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600">?</span>
                            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 px-2 py-1.5 bg-gray-800 text-white text-[10px] rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible z-[100] text-center">
                                Identificador único (Ej. 100.01).
                            </div>
                        </div>
                    </label>
                    <input type="text" name="codigo" required placeholder="Ej: 100.01" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                </div>
                <div>
                    <label class="flex items-center text-xs font-bold text-gray-600 mb-1">Nombre de la Subserie <span class="text-red-500 ml-1">*</span></label>
                    <input type="text" name="nombre" required placeholder="Ingrese el nombre completo de la subserie documental" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
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
                        <option value="">Seleccione disposición...</option>
                        <option value="CT">Conservación Total (CT)</option>
                        <option value="E">Eliminación (E)</option>
                        <option value="M">Microfilmación (M)</option>
                        <option value="S">Selección (S)</option>
                    </select>
                </div>
            </div>
            
            <div class="grid grid-cols-1 gap-4 mb-6">
                <div>
                    <label class="block text-xs font-bold text-gray-600 mb-1">Estado de la Subserie</label>
                    <select name="estado_activa" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors appearance-none">
                        <option value="true">Activo</option>
                        <option value="false">Inactivo</option>
                    </select>
                </div>
            </div>
            
            <div class="flex justify-end gap-3 pt-2">
                <button type="button" onclick="window.openAgnModal()" class="px-5 py-2.5 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" @click="if(!$el.form.checkValidity()) $el.form.reportValidity()" class="px-5 py-2.5 text-sm font-bold text-white bg-[#10b981] hover:bg-[#059669] rounded-lg shadow-sm transition-colors flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path></svg>
                    Guardar Subserie
                </button>
            </div>
        </form>
    </div>
    '''
    return HTMLResponse(content=html)


@router.post("/subseries")
async def create_agn_subserie(
    request: Request,
    serie_id: str = Form(...),
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
    
    # 1. Herencia Estructural Estricta: Validar que la Serie esté Activa
    serie_q = text("SELECT estado_activa FROM agn_series WHERE id = :id AND tenant_id = :t")
    serie = await db.execute(serie_q, {"id": serie_id, "t": tenant_id})
    serie_row = serie.fetchone()
    
    if not serie_row:
        raise HTTPException(status_code=400, detail="La Serie matriz no existe o no pertenece a este tenant.")
        
    if not serie_row.estado_activa:
        raise HTTPException(status_code=400, detail="Cadena Rota: No puede crear una Subserie sobre una Serie matriz que se encuentra Inactiva.")
        
    # 2. Constraint de Código Único
    check_q = text("SELECT id FROM agn_subseries WHERE serie_id = :s AND codigo = :c")
    existing = await db.execute(check_q, {"s": serie_id, "c": codigo})
    if existing.fetchone():
        raise HTTPException(status_code=400, detail="El código de Subserie ya existe para esta Serie matriz.")
        
    insert_q = text("""
        INSERT INTO agn_subseries (tenant_id, serie_id, codigo, nombre, retencion_ag, retencion_ac, disposicion, estado_activa)
        VALUES (:tenant, :serie_id, :codigo, :nombre, :ag, :ac, :disp, :estado)
        RETURNING id
    """)
    
    result = await db.execute(insert_q, {
        "tenant": tenant_id,
        "serie_id": serie_id,
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



@router.post("/expedientes/{expediente_id}/vincular")
async def vincular_documento_expediente(
    expediente_id: str,
    documento_id: str = Form(...),
    tipologia_id: str = Form(...),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import fitz
    import hashlib
    import os
    
    # 1. Fetch document
    doc_res = await db.execute(text("SELECT id, file_path, file_name FROM documents WHERE id = :did AND tenant_id = :t"), 
                               {"did": documento_id, "t": session_data["tenant_id"]})
    doc_row = doc_res.fetchone()
    if not doc_row:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
        
    file_path = doc_row.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="El archivo físico no existe en disco")
        
    # 2. Extract pages using PyMuPDF
    pages = 1
    if file_path.lower().endswith('.pdf'):
        try:
            with fitz.open(file_path) as pdf_doc:
                pages = len(pdf_doc)
        except Exception:
            pages = 1
            
    # 3. Calculate Hash
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    doc_hash = sha256_hash.hexdigest()
    
    # 4. Foliation Logic & Update (Atomic)
    # Lock the expediente to prevent concurrent foliation issues
    await db.execute(text("SELECT id FROM agn_expedientes WHERE id = :eid FOR UPDATE"), {"eid": expediente_id})
    
    max_res = await db.execute(text("SELECT COALESCE(MAX(folio_fin), 0) FROM documents WHERE agn_expediente_id = :eid"), {"eid": expediente_id})
    max_folio = max_res.scalar()
    
    nuevo_folio_inicio = max_folio + 1
    nuevo_folio_fin = max_folio + pages
    
    await db.execute(text('''
        UPDATE documents 
        SET agn_expediente_id = :eid, 
            tipologia_id = :tid, 
            folio = :f_ini, 
            folio_fin = :f_fin,
            hash_documento = :dhash
        WHERE id = :did
    '''), {
        "eid": expediente_id,
        "tid": tipologia_id,
        "f_ini": nuevo_folio_inicio,
        "f_fin": nuevo_folio_fin,
        "dhash": doc_hash,
        "did": documento_id
    })
    
    # 5. Blockchain / Index Logic
    # Get previous hash
    prev_hash_res = await db.execute(text('''
        SELECT firma_indice FROM agn_indice_electronico 
        WHERE expediente_id = :eid 
        ORDER BY fecha_accion DESC LIMIT 1
    '''), {"eid": expediente_id})
    prev_hash_row = prev_hash_res.fetchone()
    prev_hash = prev_hash_row.firma_indice if prev_hash_row else "INITIAL"
    
    # New Index Node Hash = SHA256(prev_hash + doc_hash + action)
    index_seed = f"{prev_hash}{doc_hash}VINCULAR_DOCUMENTO"
    new_index_hash = hashlib.sha256(index_seed.encode()).hexdigest()
    
    await db.execute(text('''
        INSERT INTO agn_indice_electronico (expediente_id, documento_id, accion, usuario_id, firma_indice)
        VALUES (:eid, :did, 'VINCULAR_DOCUMENTO', :uid, :ihash)
    '''), {
        "eid": expediente_id,
        "did": documento_id,
        "uid": session_data["user_id"],
        "ihash": new_index_hash
    })
    
    await db.commit()
    
    return {"status": "success", "folio": f"{nuevo_folio_inicio:03d}-{nuevo_folio_fin:03d}", "hash": doc_hash}


@router.get("/expedientes/explorer")
async def get_expedientes_explorer(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # Carga la lista de expedientes del tenant
    tenant_id = session_data["tenant_id"]
    res = await db.execute(text('''
        SELECT e.id, e.codigo_expediente, e.nombre_expediente, e.fecha_apertura, (e.estado = 'ABIERTO') as estado_abierto,
               (SELECT COUNT(d.id) FROM documents d WHERE d.agn_expediente_id = e.id) as doc_count
        FROM agn_expedientes e
        WHERE e.tenant_id = :t
        ORDER BY e.created_at DESC
    '''), {"t": tenant_id})
    expedientes = [dict(row._mapping) for row in res.fetchall()]
    
    html = '''
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for exp in expedientes %}
        <div class="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col gap-3 group relative"
             @click="currentView = 'expediente'" hx-get="/api/v1/agn/expedientes/{{ exp.id }}/view" hx-target="#expediente-inner-container" >
            <div class="flex justify-between items-start">
                <div class="w-12 h-12 rounded-xl flex items-center justify-center bg-blue-50 text-blue-600 group-hover:scale-110 transition-transform">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
                </div>
                {% if exp.estado_abierto %}
                <span class="px-2.5 py-1 text-xs font-bold bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                    <div class="w-1.5 h-1.5 rounded-full bg-green-500"></div>Abierto
                </span>
                {% else %}
                <span class="px-2.5 py-1 text-xs font-bold bg-red-100 text-red-700 rounded-full flex items-center gap-1">
                    <div class="w-1.5 h-1.5 rounded-full bg-red-500"></div>Cerrado
                </span>
                {% endif %}
            </div>
            <div>
                <h4 class="font-bold text-gray-800 line-clamp-1" title="{{ exp.nombre_expediente }}">{{ exp.nombre_expediente }}</h4>
                <p class="text-xs text-gray-500 font-mono mt-1">{{ exp.codigo_expediente }}</p>
            </div>
            <div class="mt-2 pt-3 border-t border-gray-100 flex justify-between items-center text-xs text-gray-500">
                <span>{{ exp.fecha_apertura }}</span>
                <span class="font-bold text-gray-700">{{ exp.doc_count }} docs</span>
            </div>
        </div>
        {% endfor %}
        {% if not expedientes %}
        <div class="col-span-full py-12 text-center text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-2xl">
            Aún no tienes Expedientes AGN. Haz clic en "Entidades Públicas" > "Crear Expediente" para crear uno.
        </div>
        {% endif %}
    </div>
    '''
    
    from fastapi.templating import Jinja2Templates
    from jinja2 import Template
    return HTMLResponse(Template(html).render(expedientes=expedientes))


@router.get("/expedientes/{expediente_id}/view")
async def get_expediente_inner_view(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # 1. Expediente Data
    exp_res = await db.execute(text("SELECT * FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), 
                               {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_row = exp_res.fetchone()
    if not exp_row:
        return HTMLResponse("Expediente no encontrado o sin permisos", status_code=404)
        
    exp = dict(exp_row._mapping)
    exp['estado_abierto'] = exp.get('estado') == 'ABIERTO'
    
    # 2. Documentos del Expediente
    docs_res = await db.execute(text('''
        SELECT d.*, t.nombre_oficial as tipo_nombre 
        FROM documents d
        LEFT JOIN agn_tipologias t ON d.tipologia_id = t.id
        WHERE d.agn_expediente_id = :eid
        ORDER BY d.folio ASC
    '''), {"eid": expediente_id})
    docs = []
    for row in docs_res.fetchall():
        d = dict(row._mapping)
        d["fecha_str"] = d["created_at"].strftime("%Y-%m-%d") if d["created_at"] else ""
        docs.append(d)
        
    # 2.5 Completitud TRD
    matrix_res = await db.execute(text('''
        SELECT 
            st.obligatoria,
            doc.id as documento_id
        FROM agn_subserie_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        WHERE st.subserie_id = :sid
    '''), {"eid": expediente_id, "sid": exp.get("subserie_id")})
    
    requeridas = 0
    completadas = 0
    
    for row in matrix_res.fetchall():
        r = dict(row._mapping)
        if r["obligatoria"]:
            requeridas += 1
            if r["documento_id"]:
                completadas += 1
                
    completitud_pct = int((completadas / requeridas * 100)) if requeridas > 0 else 100
    
    # 3. Índice Electrónico
    idx_res = await db.execute(text('''
        SELECT accion, usuario_id, firma_indice, fecha_accion
        FROM agn_indice_electronico
        WHERE expediente_id = :eid
        ORDER BY fecha_accion DESC
    '''), {"eid": expediente_id})
    eventos = []
    for row in idx_res.fetchall():
        ev = dict(row._mapping)
        # Parse timestamp to nice string like "Hoy, 14:30" - simple fallback for now
        ev["fecha_str"] = ev["fecha_accion"].strftime("%d %b, %H:%M") if ev["fecha_accion"] else ""
        if ev["accion"] == 'APERTURA_EXPEDIENTE': ev["accion_str"] = "Apertura de Expediente"
        elif ev["accion"] == 'VINCULAR_DOCUMENTO': ev["accion_str"] = "Documento Vinculado"
        elif ev["accion"] == 'CERRAR_EXPEDIENTE': ev["accion_str"] = "Cierre de Expediente"
        else: ev["accion_str"] = ev["accion"]
        eventos.append(ev)
        
    # 4. Motor TRD (Completitud)
    subserie_id = exp["subserie_id"]
    requeridas_res = await db.execute(text('''
        SELECT t.id, t.nombre_oficial, st.obligatoria 
        FROM agn_tipologias t
        LEFT JOIN agn_subserie_tipologia st ON st.tipologia_id = t.id AND st.subserie_id = :sid
        WHERE st.obligatoria = TRUE OR t.tenant_id = :t
    '''), {"sid": subserie_id, "t": session_data["tenant_id"]})
    
    tipologias = []
    req_ids = []
    for row in requeridas_res.fetchall():
        t = dict(row._mapping)
        # If it's mandatory for this subserie
        if t["obligatoria"] is True:
            req_ids.append(str(t["id"]))
        tipologias.append(t)
        
    # Count how many of req_ids are in the docs
    doc_tipos = [str(d["tipologia_id"]) for d in docs if d["tipologia_id"]]
    completadas = 0
    for rid in req_ids:
        if rid in doc_tipos: completadas += 1
        
    requeridas = len(req_ids)
    if requeridas == 0: 
        completitud_pct = 100
        requeridas = 1
        completadas = 1
    else:
        completitud_pct = int((completadas / requeridas) * 100)
        
    # 5. User's loose documents (for the modal)
    user_docs_res = await db.execute(text('''
        SELECT id, file_name 
        FROM documents 
        WHERE tenant_id = :t 
        AND status = 'COMPLETED' 
        AND agn_expediente_id IS NULL
        ORDER BY created_at DESC LIMIT 50
    '''), {"t": session_data["tenant_id"]})
    user_docs = [dict(r._mapping) for r in user_docs_res.fetchall()]

    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request=request, name="pages/expediente_view.html", context={
        "request": request,
        "exp": exp,
        "docs": docs,
        "eventos": eventos,
        "tipologias": tipologias,
        "user_docs": user_docs,
        "completitud_pct": completitud_pct,
        "completadas": completadas,
        "requeridas": requeridas
    })


@router.post("/expedientes/{expediente_id}/cerrar")
async def cerrar_expediente(
    expediente_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    import hashlib
    import os
    import xml.etree.ElementTree as ET
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # 1. Lock Expediente and Fetch Metadata
    exp_res = await db.execute(text('''
        SELECT e.id, e.subserie_id, (e.estado = 'ABIERTO') as estado_abierto, e.codigo_expediente, e.nombre_expediente, 
               e.fondo_id, e.serie_id, e.fecha_apertura,
               s.retencion_ag
        FROM agn_expedientes e
        LEFT JOIN agn_subseries s ON e.subserie_id = s.id
        WHERE e.id = :eid FOR UPDATE
    '''), {"eid": expediente_id})
    exp = exp_res.fetchone()
    if not exp:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    if not exp.estado_abierto:
        raise HTTPException(status_code=403, detail="El expediente ya se encuentra cerrado")
        
    # 2. Check Completitud
    requeridas_res = await db.execute(text('''
        SELECT tipologia_id 
        FROM agn_subserie_tipologia 
        WHERE subserie_id = :sid AND obligatoria = TRUE
    '''), {"sid": exp.subserie_id})
    req_ids = [str(r[0]) for r in requeridas_res.fetchall()]
    
    docs_res = await db.execute(text('''
        SELECT d.id, d.tipologia_id, d.hash_documento, d.file_hash, d.folio, d.folio_fin, d.file_name, d.created_at,
               t.nombre_oficial 
        FROM documents d
        LEFT JOIN agn_tipologias t ON d.tipologia_id = t.id
        WHERE d.agn_expediente_id = :eid AND d.status IN ('COMPLETED', 'ARCHIVED')
        ORDER BY d.folio ASC
    '''), {"eid": expediente_id})
    docs = docs_res.fetchall()
    doc_tipos = [str(d.tipologia_id) for d in docs if d.tipologia_id]
    
    for rid in req_ids:
        if rid not in doc_tipos:
            raise HTTPException(status_code=403, detail="El expediente no cumple el 100% de la completitud documental. Faltan tipologías obligatorias.")
            
    # 3. Calcular Fecha Cierre y Retención
    fecha_cierre_dt = datetime.utcnow()
    fecha_cierre_iso = fecha_cierre_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    fecha_apertura_iso = exp.fecha_apertura.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Calcular fecha_transferencia_central = fecha_cierre + retencion_ag (años)
    retencion_ag_years = exp.retencion_ag or 0
    fecha_transferencia_dt = fecha_cierre_dt + relativedelta(years=retencion_ag_years)
    
    total_folios = 0
    if docs:
        last_doc = docs[-1]
        total_folios = last_doc.folio_fin if last_doc.folio_fin else last_doc.folio
        
    # 4. Generate XML Manifest (AGN XSD Standard)
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<IndiceElectronico xmlns="urn:co:gov:agn:sgdea:indice:v1">
  <MetadatosExpediente>
    <Identificador>{exp.codigo_expediente}</Identificador>
    <Nombre>{exp.nombre_expediente}</Nombre>
    <CodigoFondo>{exp.fondo_id}</CodigoFondo>
    <CodigoSerie>{exp.serie_id}</CodigoSerie>
    <CodigoSubserie>{exp.subserie_id}</CodigoSubserie>
    <FechaApertura>{fecha_apertura_iso}</FechaApertura>
    <FechaCierre>{fecha_cierre_iso}</FechaCierre>
    <TotalFolios>{total_folios}</TotalFolios>
  </MetadatosExpediente>
  <ListaDocumentos>
"""
    
    consecutivo = 1
    for d in docs:
        d_hash = d.file_hash or d.hash_documento or "HASH_ERROR"
        d_fecha = d.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        xml_content += f"""    <Documento id="{d.id}">
      <OrdenConsecutivo>{consecutivo}</OrdenConsecutivo>
      <TipologiaDocumental>{d.nombre_oficial}</TipologiaDocumental>
      <NombreArchivo>{d.file_name}</NombreArchivo>
      <FechaIncorporacion>{d_fecha}</FechaIncorporacion>
      <FolioInicio>{d.folio}</FolioInicio>
      <FolioFin>{d.folio_fin if d.folio_fin else d.folio}</FolioFin>
      <Soporte>Electronico</Soporte>
      <HuellaCriptografica algoritmo="SHA-256">{d_hash}</HuellaCriptografica>
    </Documento>
"""
        consecutivo += 1
        
    xml_content += "  </ListaDocumentos>
"
    
    # Generate PKI Signature Hash
    raw_hash = hashlib.sha256(xml_content.encode()).hexdigest()
    # Mocking W3C XMLDSig standard payload inside FirmaIndice
    xml_content += f"""  <FirmaIndice>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
      <SignedInfo>
         <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
         <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha256"/>
      </SignedInfo>
      <SignatureValue>{raw_hash}</SignatureValue>
    </Signature>
  </FirmaIndice>
</IndiceElectronico>"""
    
    # 5. Save XML to Blob Storage
    upload_dir = os.path.join("uploads", str(session_data["tenant_id"]))
    os.makedirs(upload_dir, exist_ok=True)
    xml_filename = f"{expediente_id}_indice.xml"
    xml_path = os.path.join(upload_dir, xml_filename)
    
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    # 6. Atomic DB Update
    await db.execute(text('''
        UPDATE agn_expedientes 
        SET estado = 'CERRADO', 
            fecha_cierre = :fc,
            fecha_transferencia_central = :ftc,
            indice_xml_path = :xml_path,
            indice_xml_hash = :xml_hash
        WHERE id = :eid
    '''), {
        "eid": expediente_id,
        "fc": fecha_cierre_dt,
        "ftc": fecha_transferencia_dt,
        "xml_path": xml_path,
        "xml_hash": raw_hash
    })
    
    # 7. Insert Indice Electronico log and Auditoria SGDEA
    await db.execute(text('''
        INSERT INTO agn_indice_electronico (expediente_id, accion, usuario_id, firma_indice)
        VALUES (:eid, 'CIERRE_EXPEDIENTE', :uid, :ihash)
    '''), {"eid": expediente_id, "uid": session_data["user_id"], "ihash": raw_hash})
    
    await db.commit()
    
    ip_origen = request.client.host if request.client else "unknown"
    background_tasks.add_task(log_audit_sgdea_async, expediente_id, session_data["user_id"], "CIERRE_EXPEDIENTE", ip_origen, {"hash_final_xml": raw_hash, "folios_cerrados": total_folios})
    
    return JSONResponse({"status": "success", "xml_hash": raw_hash})

import io
import zipfile
import tempfile
from fastapi.responses import StreamingResponse

# Tarea asíncrona para registrar la auditoría forense sin bloquear al usuario
async def log_audit_sgdea_async(expediente_id: str, usuario_id: str, tipo_evento: str, ip_origen: str, payload_legal: dict):
    import json
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text('''
                INSERT INTO log_auditoria_sgdea (id_expediente, id_usuario, tipo_evento, ip_origen, payload_legal)
                VALUES (:eid, :uid, :tev, :ip, CAST(:payload AS JSONB))
            '''), {
                "eid": expediente_id,
                "uid": usuario_id,
                "tev": tipo_evento,
                "ip": ip_origen,
                "payload": json.dumps(payload_legal)
            })
            await session.commit()
    except Exception as e:
        print(f"Error asíncrono en log_audit_sgdea_async: {e}")

@router.get("/expedientes/{expediente_id}/exportar")
async def get_exportar_expediente_dip(
    expediente_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("expedientes:exportar")),
    db: AsyncSession = Depends(get_db_session)
):
    import hashlib
    # Verificar existencia y permisos
    exp_res = await db.execute(text("SELECT codigo_expediente, nombre_expediente, estado FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), 
                               {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_row = exp_res.fetchone()
    if not exp_row:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
        
    exp_code = exp_row.codigo_expediente
    
    # Obtener documentos
    docs_res = await db.execute(text('''
        SELECT d.id, d.file_name, d.file_path, d.file_hash, d.status, t.nombre_oficial 
        FROM documents d
        LEFT JOIN agn_tipologias t ON d.tipologia_id = t.id
        WHERE d.agn_expediente_id = :eid AND d.status IN ('COMPLETED', 'ARCHIVED')
        ORDER BY d.folio ASC
    '''), {"eid": expediente_id})
    docs = docs_res.fetchall()
    
    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        metadata = []
        for d in docs:
            d_dict = dict(d._mapping)
            if os.path.exists(d_dict["file_path"]):
                # Write to zip
                zip_file.write(d_dict["file_path"], arcname=f"documentos/{d_dict['file_name']}")
                metadata.append(d_dict)
                
        # Escribir metadatos
        zip_file.writestr("metadata_control.json", json.dumps(metadata, default=str, indent=2))
        
        # Obtener ultimo XML
        idx_res = await db.execute(text("SELECT * FROM agn_indice_electronico WHERE expediente_id = :eid ORDER BY fecha_accion DESC LIMIT 1"), {"eid": expediente_id})
        idx = idx_res.fetchone()
        if idx:
            xml_content = f"<?xml version='1.0'?><indice><hash_estado>{idx.firma_indice}</hash_estado></indice>" # Mock simple
            zip_file.writestr("indice_electronico.xml", xml_content)
            
    # Registrar auditoria
    ip_origen = request.client.host if request.client else "unknown"
    background_tasks.add_task(log_audit_sgdea_async, expediente_id, session_data["user_id"], "EXPORTACION_EXPEDIENTE", ip_origen, {"total_docs": len(docs)})
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=DIP_{exp_code}.zip"}
    )

@router.get("/documentos/{doc_id}/descargar_forense")
async def get_descargar_documento_forense(
    doc_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    import os
    doc_res = await db.execute(text("SELECT agn_expediente_id, file_path, file_name, file_hash FROM documents WHERE id = :did AND tenant_id = :t"), 
                               {"did": doc_id, "t": session_data["tenant_id"]})
    doc_row = doc_res.fetchone()
    if not doc_row or not doc_row.file_path or not os.path.exists(doc_row.file_path):
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
        
    def iterfile():
        with open(doc_row.file_path, mode="rb") as file_like:
            yield from file_like

    if doc_row.agn_expediente_id:
        ip_origen = request.client.host if request.client else "unknown"
        background_tasks.add_task(log_audit_sgdea_async, str(doc_row.agn_expediente_id), session_data["user_id"], "DESCARGA_FISICA", ip_origen, {"hash_sha256": doc_row.file_hash, "file": doc_row.file_name})

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={doc_row.file_name}"}
    )

@router.get("/documentos/{doc_id}/ver_forense")
async def get_ver_documento_forense(
    doc_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    import os
    doc_res = await db.execute(text("SELECT agn_expediente_id, file_path, file_name, file_hash, folio FROM documents WHERE id = :did AND tenant_id = :t"), 
                               {"did": doc_id, "t": session_data["tenant_id"]})
    doc_row = doc_res.fetchone()
    if not doc_row or not doc_row.file_path or not os.path.exists(doc_row.file_path):
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
        
    def iterfile():
        with open(doc_row.file_path, mode="rb") as file_like:
            yield from file_like

    if doc_row.agn_expediente_id:
        ip_origen = request.client.host if request.client else "unknown"
        background_tasks.add_task(log_audit_sgdea_async, str(doc_row.agn_expediente_id), session_data["user_id"], "VISUALIZACION_DOC", ip_origen, {"folio_iniciado": doc_row.folio})

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={doc_row.file_name}"}
    )

