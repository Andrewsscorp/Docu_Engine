from fastapi import APIRouter, Depends, Request, BackgroundTasks
from app.services.expediente_service import ExpedienteService
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
    if fc: codigo_parts.append(fc.codigo if hasattr(fc, 'codigo') else fc[0])
    
    s_res = await db.execute(text("SELECT codigo FROM agn_dependencias WHERE id = :id"), {"id": seccion})
    sc = s_res.fetchone()
    if sc: codigo_parts.append(sc.codigo if hasattr(sc, 'codigo') else sc[0])
    
    if subsec_id:
        ss_res = await db.execute(text("SELECT codigo FROM agn_dependencias WHERE id = :id"), {"id": subsec_id})
        ssc = ss_res.fetchone()
        if ssc: codigo_parts.append(ssc.codigo if hasattr(ssc, 'codigo') else ssc[0])
        
    se_res = await db.execute(text("SELECT codigo FROM agn_series WHERE id = :id"), {"id": serie})
    sec = se_res.fetchone()
    if sec: codigo_parts.append(sec.codigo if hasattr(sec, 'codigo') else sec[0])
    
    if subser_id:
        sse_res = await db.execute(text("SELECT codigo FROM agn_subseries WHERE id = :id"), {"id": subser_id})
        ssec = sse_res.fetchone()
        if ssec: codigo_parts.append(ssec.codigo if hasattr(ssec, 'codigo') else ssec[0])
        
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
    
    if tipologia_id == "ANEXO":
        tipologia_id = None
    import hashlib
    import os
    
    # 0. Check Expediente is not CERRADO
    exp_status_res = await db.execute(text("SELECT estado FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"),
                                      {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_status_row = exp_status_res.fetchone()
    if not exp_status_row:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    if exp_status_row[0] == 'CERRADO':
        raise HTTPException(status_code=403, detail="No se pueden vincular documentos a un expediente CERRADO")

    # 1. Fetch document
    doc_res = await db.execute(text("SELECT id, file_path, file_name FROM documents WHERE id = :did AND tenant_id = :t"), 
                               {"did": documento_id, "t": session_data["tenant_id"]})
    doc_row = doc_res.fetchone()
    if not doc_row:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
        
    file_path = os.path.join("uploads", str(session_data["tenant_id"]), doc_row.file_path).replace("\\", "/")
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
    await db.execute(text("SELECT id FROM agn_expedientes WHERE id = :eid FOR UPDATE"), {"eid": expediente_id, "t": session_data["tenant_id"]})
    
    max_res = await db.execute(text("SELECT COALESCE(MAX(folio_fin), 0) FROM documents WHERE agn_expediente_id = :eid"), {"eid": expediente_id, "t": session_data["tenant_id"]})
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
    '''), {"eid": expediente_id, "t": session_data["tenant_id"]})
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


@router.get("/expedientes/module", response_class=HTMLResponse)
async def get_expedientes_module(
    request: Request,
    q: str = "",
    status: str = "",
    serie_id: str = "",
    subserie_id: str = "",
    fecha_inicio: str = "",
    fecha_fin: str = "",
    soporte: str = "",
    ultimo_fecha: str = "",
    ultimo_id: str = "",
    db: AsyncSession = Depends(get_db_session)
):
    session_data = {"tenant_id": "22222222-2222-2222-2222-222222222222"}
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    tenant_id = session_data["tenant_id"]
    
    # ---------------------------------------------------------
    # NIVEL 1: CARPETAS MAESTRAS (Si no hay subserie seleccionada)
    # ---------------------------------------------------------
    if not subserie_id and not serie_id and request.headers.get("hx-target") != "expedientes-results-grid" and request.headers.get("hx-target") != "expedientes-append-target":
        # Render the master folders view
        query_sub = '''
            -- 1. Subseries
            SELECT ss.id as subserie_id, ss.codigo as subserie_codigo, ss.nombre as subserie_nombre,
                   s.id as serie_id, s.codigo as serie_codigo, s.nombre as serie_nombre,
                   d.codigo as dep_codigo, d.nombre as dep_nombre,
                   ss.retencion_ag, ss.retencion_ac, ss.disposicion, ss.total_expedientes,
                   'SUBSERIE' as tipo_carpeta
            FROM agn_subseries ss
            JOIN agn_series s ON ss.serie_id = s.id
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE ss.tenant_id = :t
            
            UNION ALL
            
            -- 2. Series (como carpetas maestras para expedientes sin subserie)
            SELECT NULL as subserie_id, '' as subserie_codigo, '' as subserie_nombre,
                   s.id as serie_id, s.codigo as serie_codigo, s.nombre as serie_nombre,
                   d.codigo as dep_codigo, d.nombre as dep_nombre,
                   s.retencion_ag, s.retencion_ac, s.disposicion, 
                   (SELECT COUNT(*) FROM agn_expedientes WHERE serie_id = s.id AND subserie_id IS NULL) as total_expedientes,
                   'SERIE' as tipo_carpeta
            FROM agn_series s
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE s.tenant_id = :t 
              AND (
                  -- Mostrar Serie si no tiene subseries, o si ya tiene expedientes directos
                  NOT EXISTS (SELECT 1 FROM agn_subseries WHERE serie_id = s.id)
                  OR 
                  (SELECT COUNT(*) FROM agn_expedientes WHERE serie_id = s.id AND subserie_id IS NULL) > 0
              )
        '''
        res_sub = await db.execute(text(query_sub), {"t": tenant_id})
        carpetas = []
        for row in res_sub.fetchall():
            d = dict(row._mapping)
            # Orden logico manual si es necesario, o lo hacemos aqui:
            if d['tipo_carpeta'] == 'SUBSERIE':
                d["codigo_jerarquico"] = f"{d['dep_codigo']}-{d['serie_codigo']}-{d['subserie_codigo']}"
                d["nombre_mostrar"] = d["subserie_nombre"]
                d["filtro_id"] = f"&subserie_id={d['subserie_id']}"
            else:
                d["codigo_jerarquico"] = f"{d['dep_codigo']}-{d['serie_codigo']}"
                d["nombre_mostrar"] = d["serie_nombre"]
                d["filtro_id"] = f"&serie_id={d['serie_id']}&subserie_id="
            carpetas.append(d)
            
        # Sort carpetas by codigo_jerarquico
        carpetas.sort(key=lambda x: x["codigo_jerarquico"])
            
        total_folders = len(carpetas)
        return templates.TemplateResponse(request=request, name="components/subseries_module.html", context={
            "request": request,
            "carpetas": carpetas,
            "total_folders": total_folders
        })

    # ---------------------------------------------------------
    # NIVEL 2: EXPEDIENTES (Interior de la Subserie)
    # ---------------------------------------------------------
    limit = 12
    params = {"t": tenant_id, "limit": limit}
    where_clauses = ["e.tenant_id = :t"]
    
    is_filtered = bool(q or status or subserie_id or fecha_inicio or fecha_fin or soporte)
    
    if q:
        where_clauses.append("(to_tsvector('spanish', coalesce(e.codigo_expediente, '') || ' ' || coalesce(e.nombre_expediente, '')) @@ plainto_tsquery('spanish', :q))")
        params["q"] = q
        
    if status:
        if status == 'abierto':
            where_clauses.append("e.estado_abierto = TRUE")
        elif status == 'cerrado':
            where_clauses.append("e.estado_abierto = FALSE AND e.fase_archivo = 'GESTION'")
        elif status == 'transferencia':
            where_clauses.append("e.fase_archivo = 'TRANSFERENCIA'")
            
    if fecha_inicio and fecha_fin:
        where_clauses.append("e.fecha_apertura BETWEEN CAST(:fi AS timestamp with time zone) AND CAST(:ff AS timestamp with time zone)")
        params["fi"] = fecha_inicio + " 00:00:00"
        params["ff"] = fecha_fin + " 23:59:59"
        
    if soporte:
        where_clauses.append("e.soporte = :soporte")
        params["soporte"] = soporte
        
    if subserie_id:
        where_clauses.append("e.subserie_id = CAST(:subid AS uuid)")
        params["subid"] = subserie_id
    elif serie_id:
        where_clauses.append("e.serie_id = CAST(:serid AS uuid) AND e.subserie_id IS NULL")
        params["serid"] = serie_id
        
    # Keyset Pagination
    if ultimo_fecha and ultimo_id:
        where_clauses.append("(e.created_at, e.id) < (CAST(:uf AS timestamp with time zone), CAST(:uid AS uuid))")
        params["uf"] = ultimo_fecha
        params["uid"] = ultimo_id
        
    where_sql = " AND ".join(where_clauses)
    
    total_count = 0
    if is_filtered:
        count_query = f"SELECT COUNT(*) FROM agn_expedientes e WHERE {where_sql.replace('AND (e.created_at, e.id) < (CAST(:uf AS timestamp with time zone), CAST(:uid AS uuid))', '')}"
        res_count = await db.execute(text(count_query), {k: v for k, v in params.items() if k not in ['uf', 'uid', 'limit']})
        total_count = res_count.scalar()
    else:
        res_count = await db.execute(text("SELECT reltuples::bigint FROM pg_class WHERE relname = 'agn_expedientes'"))
        total_count = res_count.scalar() or 0
        
    # Fetch breadcrumbs context if inside a subserie
    breadcrumb = None
    if subserie_id:
        bc_query = '''
            SELECT ss.nombre as subserie_nombre, s.nombre as serie_nombre, d.nombre as dep_nombre
            FROM agn_subseries ss
            JOIN agn_series s ON ss.serie_id = s.id
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE ss.id = CAST(:subid AS uuid)
        '''
        res_bc = await db.execute(text(bc_query), {"subid": subserie_id})
        bc_row = res_bc.fetchone()
        if bc_row:
            bc = dict(bc_row._mapping)
            breadcrumb = f"Fondo > {bc['dep_nombre']} > {bc['serie_nombre']} > {bc['subserie_nombre']}"
    elif serie_id:
        bc_query = '''
            SELECT s.nombre as serie_nombre, d.nombre as dep_nombre
            FROM agn_series s
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE s.id = CAST(:serid AS uuid)
        '''
        res_bc = await db.execute(text(bc_query), {"serid": serie_id})
        bc_row = res_bc.fetchone()
        if bc_row:
            bc = dict(bc_row._mapping)
            breadcrumb = f"Fondo > {bc['dep_nombre']} > {bc['serie_nombre']}"
    
    query_str = f'''
        SELECT e.id, e.codigo_expediente, e.nombre_expediente, e.fecha_apertura, e.estado_abierto, e.fase_archivo,
               e.cantidad_documentos as doc_count, e.soporte, e.created_at,
               u.username as responsable_nombre
        FROM agn_expedientes e
        LEFT JOIN users u ON e.responsable_id = CAST(u.id AS VARCHAR)
        WHERE {where_sql}
        ORDER BY e.created_at DESC, e.id DESC
        LIMIT :limit
    '''
    res = await db.execute(text(query_str), params)
    expedientes = [dict(r._mapping) for r in res.fetchall()]
    
    context = {
        "request": request, 
        "expedientes": expedientes,
        "total_count": total_count,
        "has_more": len(expedientes) == limit,
        "q": q, "status": status, "serie_id": serie_id, "subserie_id": subserie_id,
        "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "soporte": soporte,
        "is_append": bool(ultimo_id),
        "breadcrumb": breadcrumb
    }
    
    # HTMX Target Check
    if request.headers.get("hx-target") == "expedientes-results-grid" or request.headers.get("hx-target") == "expedientes-append-target":
        template_name = "components/expedientes_grid_items.html" if request.headers.get("hx-target") == "expedientes-append-target" else "components/expedientes_grid.html"
        return templates.TemplateResponse(request=request, name=template_name, context=context)
        
    return templates.TemplateResponse(request=request, name="components/expedientes_module.html", context=context)

    
@router.post("/expedientes/{id}/cierre")
async def post_cierre_expediente(
    id: str,
    session_data: dict = Depends(require_permission("expedientes:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    res = await db.execute(text("UPDATE agn_expedientes SET estado_abierto = FALSE, fecha_cierre = CURRENT_TIMESTAMP WHERE id = :id AND tenant_id = :t RETURNING id"), {"id": id, "t": tenant_id})
    if not res.scalar():
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    await db.commit()
    return {"status": "success", "detail": "Expediente sellado correctamente (Inmutabilidad Activada)"}

    
    # Full module response
    return templates.TemplateResponse(request=request, name="components/expedientes_module.html", context=context)


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
    
    # 2. Documentos del Expediente
    docs_res = await db.execute(text('''
        SELECT d.*, t.nombre_oficial as tipo_nombre 
        FROM documents d
        LEFT JOIN agn_tipologias t ON d.tipologia_id = t.id
        WHERE d.agn_expediente_id = :eid
        ORDER BY d.folio ASC
    '''), {"eid": expediente_id, "t": session_data["tenant_id"]})
    docs = []
    for row in docs_res.fetchall():
        d = dict(row._mapping)
        d["fecha_str"] = d["created_at"].strftime("%Y-%m-%d") if d["created_at"] else ""
        if not d.get("tipo_nombre"):
            d["tipo_nombre"] = "Archivo Adjunto / Anexo"
        docs.append(d)
        
    # 2.5 Completitud TRD
    matrix_res = await db.execute(text('''
        SELECT 
            st.obligatoria,
            doc.id as documento_id
        FROM agn_expediente_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        WHERE st.expediente_id = :eid
    '''), {"eid": expediente_id, "t": session_data["tenant_id"]})
    
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
    '''), {"eid": expediente_id, "t": session_data["tenant_id"]})
    eventos = []
    for row in idx_res.fetchall():
        ev = dict(row._mapping)
        # Parse timestamp to nice string like "Hoy, 14:30" - simple fallback for now
        ev["fecha_str"] = ev["fecha_accion"].strftime("%d %b, %H:%M") if ev["fecha_accion"] else ""
        if ev["accion"] == 'APERTURA_EXPEDIENTE': ev["accion_str"] = "Apertura de Expediente"
        elif ev["accion"] == 'VINCULAR_DOCUMENTO': ev["accion_str"] = "Documento Vinculado"
        elif ev["accion"] == 'CIERRE_EXPEDIENTE': ev["accion_str"] = "Cierre de Expediente"
        else: ev["accion_str"] = ev["accion"]
        eventos.append(ev)
        
    # 4. Motor TRD (Completitud)
    subserie_id = exp["subserie_id"]
    requeridas_res = await db.execute(text('''
        SELECT t.id, t.nombre_oficial, st.obligatoria 
        FROM agn_tipologias t
        LEFT JOIN agn_expediente_tipologia st ON st.tipologia_id = t.id AND st.expediente_id = :eid
        WHERE st.obligatoria = TRUE OR t.tenant_id = :t
    '''), {"eid": expediente_id, "t": session_data["tenant_id"]})
    
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
    dropdown_tipologias = [t for t in tipologias if t["obligatoria"] is False]
    return templates.TemplateResponse(request=request, name="pages/expediente_view.html", context={
        "request": request,
        "exp": exp,
        "docs": docs,
        "eventos": eventos,
        "tipologias": tipologias,
        "dropdown_tipologias": dropdown_tipologias,
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
    ip_origen = request.client.host if request.client else "unknown"
    result = await ExpedienteService.cerrar_expediente(
        expediente_id=expediente_id,
        tenant_id=session_data["tenant_id"],
        user_id=session_data["user_id"],
        ip_origen=ip_origen,
        db=db,
        background_tasks=background_tasks
    )
    return JSONResponse(result)

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


@router.get("/expedientes/{expediente_id}/indice_xml")
async def descargar_indice_xml(
    expediente_id: str,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    res = await db.execute(text("SELECT indice_xml_path FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), {"eid": expediente_id, "t": session_data["tenant_id"]})
    row = res.fetchone()
    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="XML no encontrado")
        
    xml_path = row[0]
    import os
    if not os.path.exists(xml_path):
        raise HTTPException(status_code=404, detail="Archivo XML fisico no encontrado")
        
    from fastapi.responses import FileResponse
    return FileResponse(xml_path, media_type="application/xml", filename=f"{expediente_id}_indice_electronico.xml")

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
    '''), {"eid": expediente_id, "t": session_data["tenant_id"]})
    docs = docs_res.fetchall()
    
    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        metadata = []
        for d in docs:
            d_dict = dict(d._mapping)
            full_path = os.path.join("uploads", str(session_data["tenant_id"]), d_dict["file_path"]).replace("\\", "/")
            if os.path.exists(full_path):
                # Write to zip
                zip_file.write(full_path, arcname=f"documentos/{d_dict['file_name']}")
                metadata.append(d_dict)
                
        # Escribir metadatos
        zip_file.writestr("metadata_control.json", json.dumps(metadata, default=str, indent=2))
        
        # Obtener XML real
        exp_res = await db.execute(text("SELECT indice_xml_path FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), {"eid": expediente_id, "t": session_data["tenant_id"]})
        exp_row = exp_res.fetchone()
        if exp_row and exp_row.indice_xml_path and os.path.exists(exp_row.indice_xml_path):
            with open(exp_row.indice_xml_path, "r", encoding="utf-8") as xmlf:
                xml_content = xmlf.read()
            zip_file.writestr("indice_electronico.xml", xml_content)
        else:
            # Fallback a registro de base de datos
            idx_res = await db.execute(text("SELECT * FROM agn_indice_electronico WHERE expediente_id = :eid ORDER BY fecha_accion DESC LIMIT 1"), {"eid": expediente_id, "t": session_data["tenant_id"]})
            idx = idx_res.fetchone()
            if idx:
                xml_content = f"<?xml version='1.0'?><indice><hash_estado>{idx.firma_indice}</hash_estado></indice>"
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
    if not doc_row or not doc_row.file_path:
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
    
    full_path = os.path.join("uploads", str(session_data["tenant_id"]), doc_row.file_path).replace("\\", "/")
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
        
    def iterfile():
        with open(full_path, mode="rb") as file_like:
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
    if not doc_row or not doc_row.file_path:
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
    
    full_path = os.path.join("uploads", str(session_data["tenant_id"]), doc_row.file_path).replace("\\", "/")
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
        
    def iterfile():
        with open(full_path, mode="rb") as file_like:
            yield from file_like

    if doc_row.agn_expediente_id:
        ip_origen = request.client.host if request.client else "unknown"
        background_tasks.add_task(log_audit_sgdea_async, str(doc_row.agn_expediente_id), session_data["user_id"], "VISUALIZACION_DOC", ip_origen, {"folio_iniciado": doc_row.folio})

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={doc_row.file_name}"}
    )


@router.get("/expedientes/{expediente_id}/control_tipologias")
async def get_control_tipologias_view(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    exp_res = await db.execute(text("SELECT id, codigo_expediente, nombre_expediente, subserie_id, (estado = 'ABIERTO') as estado_abierto FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_row = exp_res.fetchone()
    if not exp_row:
        return HTMLResponse("Expediente no encontrado", status_code=404)
    exp = dict(exp_row._mapping)
    
    matrix_res = await db.execute(text('''
        SELECT 
            t.id as tipologia_id, 
            t.nombre_oficial as oficial, 
            t.formatos_permitidos,
            st.obligatoria,
            st.orden_sugerido,
            doc.id as documento_id,
            doc.file_name,
            doc.created_at as fecha_carga,
            u.username as autor_carga,
            (CASE WHEN doc.id IS NOT NULL THEN 'CARGADO' ELSE 'FALTANTE' END) as estado_carga
        FROM agn_expediente_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        LEFT JOIN users u ON doc.uploaded_by = u.id
        WHERE st.expediente_id = :eid
        ORDER BY st.obligatoria DESC, st.orden_sugerido ASC NULLS LAST, t.nombre_oficial ASC
    '''), {"eid": expediente_id, "sid": exp["subserie_id"]})
    
    tipologias = []
    obligatorias = []
    opcionales = []
    completadas_req = 0
    total_req = 0
    
    for row in matrix_res.fetchall():
        t = dict(row._mapping)
        if t["fecha_carga"]:
            t["fecha_str"] = t["fecha_carga"].strftime("%d %b %Y, %H:%M")
        
        if t["obligatoria"]:
            total_req += 1
            if t["estado_carga"] == 'CARGADO':
                completadas_req += 1
            obligatorias.append(t)
        else:
            opcionales.append(t)
            
    completitud = int((completadas_req / total_req * 100)) if total_req > 0 else 100
    pendientes = total_req - completadas_req
    
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
    return templates.TemplateResponse(request=request, name="pages/control_tipologias.html", context={
        "request": request,
        "exp": exp,
        "obligatorias": obligatorias,
        "opcionales": opcionales,
        "completitud": completitud,
        "total_req": total_req,
        "completadas_req": completadas_req,
        "pendientes": pendientes,
        "user_docs": user_docs
    })

@router.get("/expedientes/{expediente_id}/modal_trd")
async def get_modal_trd(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    exp_res = await db.execute(text("SELECT * FROM agn_expedientes WHERE id = :eid"), {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp = dict(exp_res.fetchone()._mapping)
    
    # Check if user has tipologias:crear permission
    # In a real app we'd query the permissions, but since we rely on require_permission dependency, 
    # we can do a quick check:
    perm_res = await db.execute(text('''
        SELECT 1 FROM users u
        JOIN role_permissions rp ON u.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE u.id = :uid AND p.name = 'tipologias:crear'
    '''), {"uid": session_data["user_id"]})
    has_perm = perm_res.fetchone() is not None
    
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request=request, name="components/modal_vincular_trd.html", context={
        "request": request,
        "expediente": exp,
        "puede_crear_tipologias": has_perm
    })

@router.get("/expedientes/{expediente_id}/tipologias/disponibles")
async def get_tipologias_disponibles(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # Trae tipolog├¡as maestras que NO est├®n vinculadas a esta subserie
    res = await db.execute(text('''
        SELECT t.id, t.nombre_oficial 
        FROM agn_tipologias t
        WHERE t.estado_activo = TRUE 
          AND t.tenant_id = :t
          AND t.id NOT IN (
              SELECT tipologia_id FROM agn_expediente_tipologia WHERE expediente_id = :eid AND estado_regla = TRUE
          )
        ORDER BY t.nombre_oficial ASC
    '''), {"t": session_data["tenant_id"], "eid": expediente_id})
    
    tipologias = [dict(r._mapping) for r in res.fetchall()]
    # Formatear para Select2 o frontend JSON:
    return JSONResponse([{"id": str(t["id"]), "text": t["nombre_oficial"]} for t in tipologias])

class TRDLinkPayload(BaseModel):
    id_tipologia: str
    es_obligatorio: bool
    orden: Optional[int] = None

@router.post("/expedientes/{expediente_id}/tipologias")
async def post_vincular_trd(
    expediente_id: str,
    payload: TRDLinkPayload,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    # Check if expediente is closed
    exp_status_res = await db.execute(text("SELECT estado FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"),
                                      {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_status_row = exp_status_res.fetchone()
    if exp_status_row and exp_status_row[0] == 'CERRADO':
        return JSONResponse({"status": "error", "message": "No se puede vincular a un expediente CERRADO."}, status_code=403)

    # Validar si ya existe
    exist_res = await db.execute(text("SELECT id FROM agn_expediente_tipologia WHERE expediente_id = :eid AND tipologia_id = :tid"), {"eid": expediente_id, "tid": payload.id_tipologia})
    if exist_res.fetchone():
        return JSONResponse({"status": "error", "message": "Esta tipolog├¡a ya pertenece a la Subserie."}, status_code=409)
        
    await db.execute(text('''
        INSERT INTO agn_expediente_tipologia (expediente_id, tipologia_id, obligatoria, orden_sugerido, usuario_creador)
        VALUES (:eid, :tid, :obl, :ord, :uid)
    '''), {
        "eid": expediente_id,
        "tid": payload.id_tipologia,
        "obl": payload.es_obligatorio,
        "ord": payload.orden,
        "uid": session_data["user_id"]
    })
    
    # Log Auditoria (opcional aqu├¡ si lo centralizamos)
    await db.commit()
    return JSONResponse({"status": "success"}, status_code=201)

from typing import List

class NuevaTipologiaPayload(BaseModel):
    nombre_oficial: str
    soporte_origen: str
    formatos_permitidos: List[str]
    clasificacion: str
    exige_firma: bool

@router.post("/tipologias/diccionario")
async def post_crear_tipologia_diccionario(
    payload: NuevaTipologiaPayload,
    request: Request,
    session_data: dict = Depends(require_permission("tipologias:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import json
    # Normalizaci├│n estricta (Sanitizaci├│n Sem├íntica)
    nombre_limpio = payload.nombre_oficial.strip().upper()
    
    # Verificar si el nombre ya existe (Unicidad)
    exist_res = await db.execute(text("SELECT id FROM agn_tipologias WHERE nombre_oficial = :nom"), {"nom": nombre_limpio})
    if exist_res.fetchone():
        return JSONResponse({"status": "error", "message": "Ya existe una tipología con ese nombre oficial en el catálogo."}, status_code=409)
        
    res = await db.execute(text('''
        INSERT INTO agn_tipologias (
            nombre_oficial, soporte_origen, formatos_permitidos, 
            clasificacion, exige_firma, tenant_id, usuario_creador, estado_activo
        )
        VALUES (:nom, :sop, CAST(:form AS JSONB), :clas, :firma, :t, :uid, TRUE)
        RETURNING id
    '''), {
        "nom": nombre_limpio,
        "sop": payload.soporte_origen,
        "form": json.dumps(payload.formatos_permitidos),
        "clas": payload.clasificacion,
        "firma": payload.exige_firma,
        "t": session_data["tenant_id"],
        "uid": session_data["user_id"]
    })
    
    nuevo_id = str(res.scalar())
    await db.commit()
    
    return JSONResponse({
        "status": "success", 
        "data": {
            "id": nuevo_id,
            "text": f"{nombre_limpio}"
        }
    }, status_code=201)

@router.post("/expedientes/{expediente_id}/upload_direct")
async def post_upload_direct_expediente(
    expediente_id: str,
    background_tasks: BackgroundTasks,
    tipologia_id: str = Form(...),
    file: UploadFile = File(...),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import os
    import hashlib
    import fitz
    from app.routers.documents import iniciar_extraccion_ocr
    
    tenant_id = session_data["tenant_id"]
    upload_dir = os.path.join("uploads", str(tenant_id))
    thumb_dir = os.path.join(upload_dir, "thumbnails")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)
    
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    disk_filename = f"{file_hash}_{file.filename}"
    file_path = os.path.join(upload_dir, disk_filename).replace("\\", "/")
    
    if tipologia_id == "ANEXO":
        tipologia_id = None
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
        
    pages = 1
    thumbnail_path = None
    thumb_filename = f"thumb_{file_hash}.webp"
    thumb_full_path = os.path.join(thumb_dir, thumb_filename)
    thumb_rel_path = f"/api/v1/documents/thumbnail/{tenant_id}/{thumb_filename}"
    
    if file_path.lower().endswith('.pdf'):
        try:
            doc_pdf = fitz.open(file_path)
            pages = doc_pdf.page_count
            
            if pages > 0:
                page = doc_pdf.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                from PIL import Image
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                if mode == "RGBA":
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                img.thumbnail((300, 400))
                img.save(thumb_full_path, "WEBP", quality=70)
                thumbnail_path = thumb_rel_path
        except:
            pass
            
    from sqlalchemy.exc import IntegrityError
    try:
        res_doc = await db.execute(text('''
            INSERT INTO documents (tenant_id, file_name, file_path, uploaded_by, status, is_private, mime_type, file_size_bytes, file_hash, agn_expediente_id, tipologia_id, paginas_cantidad, thumbnail_path)
            VALUES (:t, :n, :p, :u, 'PENDING', FALSE, :m, :s, :h, :eid, :tid, :pages, :thumb)
            RETURNING id
        '''), {
            "t": tenant_id, "n": file.filename, "p": disk_filename, "u": session_data["user_id"],
            "m": file.content_type, "s": len(file_content), "h": file_hash, "eid": expediente_id, "tid": tipologia_id,
            "pages": pages, "thumb": thumbnail_path
        })
        new_doc_id = str(res_doc.scalar())
    except IntegrityError:
        await db.rollback()
        return JSONResponse({"detail": "El documento ya existe en el sistema (Hash duplicado)."}, status_code=409)
    
    # Índice Electrónico
    index_seed = f"{expediente_id}|{new_doc_id}|{session_data['user_id']}"
    new_index_hash = hashlib.sha256(index_seed.encode()).hexdigest()
    
    await db.execute(text('''
        INSERT INTO agn_indice_electronico (expediente_id, documento_id, accion, usuario_id, firma_indice)
        VALUES (:eid, :did, 'VINCULAR_DOCUMENTO', :uid, :ihash)
    '''), {
        "eid": expediente_id, "did": new_doc_id, "uid": session_data["user_id"], "ihash": new_index_hash
    })
    
    background_tasks.add_task(iniciar_extraccion_ocr, new_doc_id) # DELEGATED TO REAL OCR WORKER
    
    await db.commit()
    
    return JSONResponse({"status": "success"})

@router.get("/subseries/{subserie_id}/fuid")
async def get_fuid_subserie(
    subserie_id: str,
    request: Request,
    expediente_id: Optional[str] = None,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # 1. Fetch subserie details
    sub_res = await db.execute(text("SELECT s.id, s.codigo, s.nombre, se.nombre as serie_nombre FROM agn_subseries s LEFT JOIN agn_series se ON s.serie_id = se.id WHERE s.id = :sid"), {"sid": subserie_id})
    subserie = sub_res.fetchone()
    if not subserie:
        return HTMLResponse("Subserie no encontrada", status_code=404)
        
    # 2. Try to query the materialized view, fallback to raw SQL if it doesn't exist
    try:
        fuid_res = await db.execute(text("SELECT * FROM vista_fuid_detalle_subserie WHERE subserie_id = :sid ORDER BY no_orden ASC"), {"sid": subserie_id})
        filas = fuid_res.fetchall()
    except Exception as e:
        # Transaction is aborted due to missing view, so we must rollback before running fallback query
        await db.rollback()
        # Re-apply RLS config because rollback clears it!
        await db.execute(
            text("SELECT set_config('app.current_tenant', :tenant, false)"), 
            {"tenant": session_data["tenant_id"]}
        )
        if session_data.get("user_id"):
            await db.execute(
                text("SELECT set_config('app.current_user_id', :uid, false)"), 
                {"uid": session_data["user_id"]}
            )
        # Fallback raw query if the view hasn't been created yet by the admin
        fallback_sql = """
        SELECT 
            ROW_NUMBER() OVER (
                PARTITION BY exp.subserie_id 
                ORDER BY exp.codigo_expediente ASC
            ) AS no_orden,
            
            exp.codigo_expediente AS codigo,
            exp.nombre_expediente AS nombre_unidad_conservacion,
            
            (SELECT MIN(created_at) 
             FROM documents doc 
             WHERE doc.agn_expediente_id = exp.id 
               AND doc.status IN ('COMPLETED', 'ARCHIVED')) AS fecha_inicial,
               
            (SELECT MAX(created_at) 
             FROM documents doc 
             WHERE doc.agn_expediente_id = exp.id 
               AND doc.status IN ('COMPLETED', 'ARCHIVED')) AS fecha_final,
               
            'N/A' AS caja_carpeta,
            
            COALESCE((SELECT SUM(paginas_cantidad) 
                      FROM documents doc 
                      WHERE doc.agn_expediente_id = exp.id 
                        AND doc.status IN ('COMPLETED', 'ARCHIVED')), 0) AS folios,
                        
            'ELECTRÓNICO' AS soporte,
            exp.subserie_id,
            exp.tenant_id,
            exp.id as exp_id
            
        FROM agn_expedientes exp
        WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid
        -- NUEVA REGLA NORMATIVA: El candado de evidencia real
        AND EXISTS (
            SELECT 1 
            FROM documents doc 
            WHERE doc.agn_expediente_id = exp.id 
              AND doc.status IN ('COMPLETED', 'ARCHIVED')
        )
        """
        fuid_res = await db.execute(text(fallback_sql), {"sid": subserie_id})
        filas = fuid_res.fetchall()
        
    registros = []
    for r in filas:
        d = dict(r._mapping)
        # Format dates to YYYY-MM-DD
        d['fecha_inicial_str'] = d['fecha_inicial'].strftime('%Y-%m-%d') if d['fecha_inicial'] else ''
        d['fecha_final_str'] = d['fecha_final'].strftime('%Y-%m-%d') if d['fecha_final'] else ''
        registros.append(d)
        
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    subserie_dict = dict(subserie._mapping) if subserie else {}
    return templates.TemplateResponse(request=request, name="pages/fuid_view.html", context={
        "request": request,
        "subserie": subserie_dict,
        "registros": registros,
        "expediente_id_origen": expediente_id
    })

import hashlib
from datetime import datetime
from fastapi.responses import PlainTextResponse, FileResponse
import os
from app.utils.pdf_generator import generar_pdf_fuid
from fastapi.responses import FileResponse


@router.post("/subseries/{subserie_id}/fuid/firmar")
async def firmar_fuid(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # 1. Fetch data
        fallback_sql = '''
        SELECT exp.id as exp_id, exp.codigo_expediente, 
               COALESCE((SELECT SUM(paginas_cantidad) FROM documents doc WHERE doc.agn_expediente_id = exp.id AND doc.status IN ('COMPLETED', 'ARCHIVED')), 0) AS folios
        FROM agn_expedientes exp
        WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid
        '''
        res = await db.execute(text(fallback_sql), {"sid": subserie_id})
        filas = res.fetchall()
        
        # 2. Check empty constraint
        exp_validos = []
        for r in filas:
            if r.folios > 0:
                exp_validos.append(r)
                
        if not exp_validos:
            return JSONResponse({"status": "error", "detail": "No hay expedientes con documentos validos en esta subserie para firmar."}, status_code=400)
            
        # 3. REAL PDF Generation & Hash
        sub_res = await db.execute(text("SELECT nombre FROM agn_subseries WHERE id = :sid"), {"sid": subserie_id})
        sub_nombre = sub_res.scalar()
        
        # Convert filas into simple dicts for the PDF generator
        registros_pdf = []
        for r in exp_validos:
            d = dict(r._mapping)
            d["no_orden"] = len(registros_pdf) + 1
            d["nombre_unidad_conservacion"] = d.get("nombre_expediente", "Expediente")
            d["fecha_inicial_str"] = "N/A"
            d["fecha_final_str"] = "N/A"
            d["caja_carpeta"] = "N/A"
            d["soporte"] = "ELECTRÓNICO"
            registros_pdf.append(d)
            
        pdf_bytes = generar_pdf_fuid(sub_nombre, registros_pdf)
        fuid_hash = hashlib.sha256(pdf_bytes).hexdigest()
        
        # Save to disk
        os.makedirs("fuid_archives", exist_ok=True)
        pdf_path = os.path.join("fuid_archives", f"{fuid_hash}.pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)
        
        # 4. Insert Transferencia
        transf_res = await db.execute(text('''
            INSERT INTO fuid_transferencias (subserie_id, consecutivo_oficial, usuario_firmante, hash_sha256, ruta_almacenamiento_pdf, tenant_id)
            VALUES (:sid, :consecutivo, :user_id, :hash, :ruta, :t)
            RETURNING id
        '''), {
            "eid": expediente_id, 
            "consecutivo": f"FUID-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": session_data["user_id"],
            "hash": fuid_hash,
            "ruta": pdf_path,
            "t": session_data["tenant_id"]
        })
        fuid_id = transf_res.scalar()
        
        # 5. Insert Vinculos and Update expedientes
        for idx, exp in enumerate(exp_validos):
            await db.execute(text('''
                INSERT INTO fuid_expedientes_vinculados (fuid_id, expediente_id, orden_consecutivo)
                VALUES (:fid, :eid, :orden)
            '''), {"fid": fuid_id, "eid": exp.exp_id, "orden": idx + 1})
            
            await db.execute(text("UPDATE agn_expedientes SET estado = 'ARCHIVO_CENTRAL' WHERE id = :eid"), {"eid": exp.exp_id})
            
        # 6. Audit
        import json
        payload_legal = json.dumps({
            "subserie_id": subserie_id,
            "hash_sha256": fuid_hash,
            "expedientes_vinculados": len(exp_validos),
            "user_agent": request.headers.get("user-agent", "unknown")
        })
        for r in exp_validos:
            await db.execute(text('''
                INSERT INTO log_auditoria_sgdea (id_expediente, id_usuario, tipo_evento, ip_origen, payload_legal)
                VALUES (:eid, :u, 'FIRMA_FUID_TRANSFERENCIA', :ip, CAST(:det AS JSONB))
            '''), {
                "eid": r.exp_id,
                "u": session_data["user_id"],
                "ip": request.client.host if request.client else "unknown",
                "det": payload_legal
            })
        
        await db.commit()
        return JSONResponse({"status": "success", "hash": fuid_hash})
    except Exception as e:
        await db.rollback()
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

@router.get("/subseries/{subserie_id}/fuid/csv")
async def descargar_plana_fuid(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # 1. Query the expedientes (same logic as get_fuid_subserie)
    try:
        fuid_res = await db.execute(text("SELECT * FROM vista_fuid_detalle_subserie WHERE subserie_id = :sid ORDER BY no_orden ASC"), {"sid": subserie_id})
        filas = fuid_res.fetchall()
    except Exception as e:
        await db.rollback()
        await db.execute(text("SELECT set_config('app.current_tenant', :tenant, false)"), {"tenant": session_data["tenant_id"]})
        if session_data.get("user_id"):
            await db.execute(text("SELECT set_config('app.current_user_id', :uid, false)"), {"uid": session_data["user_id"]})
        
        fallback_sql = """
        SELECT 
            ROW_NUMBER() OVER (
                PARTITION BY exp.subserie_id 
                ORDER BY exp.codigo_expediente ASC
            ) AS no_orden,
            exp.codigo_expediente AS codigo,
            exp.nombre_expediente AS nombre_unidad_conservacion,
            (SELECT MIN(created_at) FROM documents doc WHERE doc.agn_expediente_id = exp.id AND doc.status IN ('COMPLETED', 'ARCHIVED')) AS fecha_inicial,
            (SELECT MAX(created_at) FROM documents doc WHERE doc.agn_expediente_id = exp.id AND doc.status IN ('COMPLETED', 'ARCHIVED')) AS fecha_final,
            'N/A' AS caja_carpeta,
            COALESCE((SELECT SUM(paginas_cantidad) FROM documents doc WHERE doc.agn_expediente_id = exp.id AND doc.status IN ('COMPLETED', 'ARCHIVED')), 0) AS folios,
            'ELECTRÓNICO' AS soporte,
            exp.subserie_id,
            exp.tenant_id,
            exp.id AS exp_id
        FROM agn_expedientes exp
        WHERE exp.subserie_id = :sid AND exp.estado = 'CERRADO'
        ORDER BY exp.codigo_expediente ASC
        """
        fuid_res = await db.execute(text(fallback_sql), {"sid": subserie_id})
        filas = fuid_res.fetchall()

    # 2. Audit log first
    import json
    payload_legal = json.dumps({
        "subserie_id": subserie_id,
        "user_agent": request.headers.get("user-agent", "unknown")
    })
    
    for r in filas:
        await db.execute(text('''
            INSERT INTO log_auditoria_sgdea (id_expediente, id_usuario, tipo_evento, ip_origen, payload_legal)
            VALUES (:eid, :u, 'DESCARGA_METADATOS_PLANA', :ip, CAST(:det AS JSONB))
        '''), {
            "eid": r.exp_id,
            "u": session_data["user_id"],
            "ip": request.client.host if request.client else "unknown",
            "det": payload_legal
        })
    await db.commit()
    
    # 3. Generate CSV
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["NO_ORDEN", "CODIGO", "NOMBRE_UNIDAD", "FECHA_INICIAL", "FECHA_FINAL", "CAJA_CARPETA", "FOLIOS", "SOPORTE"])
    
    for r in filas:
        # Format dates if present
        fi = r.fecha_inicial.strftime("%Y-%m-%d") if r.fecha_inicial else "N/A"
        ff = r.fecha_final.strftime("%Y-%m-%d") if r.fecha_final else "N/A"
        
        writer.writerow([
            r.no_orden,
            r.codigo,
            r.nombre_unidad_conservacion,
            fi,
            ff,
            r.caja_carpeta,
            r.folios,
            r.soporte
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue().encode('utf-8-sig')]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=FUID_{subserie_id}_Plano.csv"}
    )

@router.get("/fuid/descargar_pdf/{hash}")
async def descargar_pdf_fuid(
    hash: str,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    pdf_path = os.path.join("fuid_archives", f"{hash}.pdf")
    if not os.path.exists(pdf_path):
        return JSONResponse({"status": "error", "detail": "PDF no encontrado"}, status_code=404)
        
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"FUID_{hash[:8]}.pdf")

@router.post("/expedientes/{expediente_id}/importar_trd")
async def post_importar_trd_subserie(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    # 1. Obtener la subserie del expediente
    exp_res = await db.execute(text("SELECT subserie_id FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), 
                               {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_row = exp_res.fetchone()
    
    import json
    from fastapi import Response
    
    if not exp_row or not exp_row.subserie_id:
        res = Response(status_code=204)
        trigger_data = {"showSwal": {"title": "Sin Subserie", "text": "Este expediente está asignado directamente a una Serie. No hay tipologías maestras configuradas para heredar.", "icon": "warning"}}
        res.headers["HX-Trigger"] = json.dumps(trigger_data)
        return res
        
    # 2. Copiar tipologías de la subserie al expediente ignorando duplicados
    res_insert = await db.execute(text('''
        INSERT INTO agn_expediente_tipologia (expediente_id, tipologia_id, obligatoria, orden_sugerido, usuario_creador)
        SELECT 
            :eid, 
            tipologia_id, 
            obligatoria, 
            orden_sugerido, 
            :uid
        FROM agn_subserie_tipologia
        WHERE subserie_id = :sid AND estado_regla = TRUE
        ON CONFLICT (expediente_id, tipologia_id) DO NOTHING
    '''), {
        "eid": expediente_id, 
        "sid": exp_row.subserie_id,
        "uid": session_data["user_id"]
    })
    
    inserted_count = res_insert.rowcount
    await db.commit()
    
    # 3. Retornar la vista actualizada
    response = await get_control_tipologias_view(expediente_id, request, session_data, db)
    
    if inserted_count == 0:
        res_check = await db.execute(text("SELECT COUNT(*) FROM agn_subserie_tipologia WHERE subserie_id = :sid AND estado_regla = TRUE"), {"sid": exp_row.subserie_id})
        total_mapped = res_check.scalar()
        if total_mapped == 0:
            trigger_data = {"showSwal": {"title": "TRD Vacía", "text": "La subserie asignada a este expediente no tiene tipologías documentales configuradas en el módulo maestro.", "icon": "warning"}}
        else:
            trigger_data = {"showSwal": {"title": "TRD al día", "text": "El expediente ya heredó todas las tipologías maestras de su subserie.", "icon": "info"}}
        response.headers["HX-Trigger"] = json.dumps(trigger_data)
    else:
        trigger_data = {"showSwal": {"title": "TRD Heredada", "text": f"Se heredaron {inserted_count} tipologías maestras de la subserie correctamente.", "icon": "success"}}
        response.headers["HX-Trigger"] = json.dumps(trigger_data)
        
    return response

@router.delete("/expedientes/{expediente_id}/tipologias/{tipologia_id}")
async def delete_expediente_tipologia(
    expediente_id: str,
    tipologia_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text('''
        DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid AND tipologia_id = :tid 
        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)
    '''), {"eid": expediente_id, "tid": tipologia_id, "t": session_data["tenant_id"]})
    await db.commit()
    return await get_control_tipologias_view(expediente_id, request, session_data, db)

@router.delete("/expedientes/{expediente_id}/tipologias")
async def delete_all_expediente_tipologias(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text('''
        DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid 
        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)
    '''), {"eid": expediente_id, "t": session_data["tenant_id"]})
    await db.commit()
    return await get_control_tipologias_view(expediente_id, request, session_data, db)

@router.put("/expedientes/{id}")
async def update_expediente(
    id: str,
    request: Request,
    session_data: dict = Depends(require_permission("expedientes:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    form_data = await request.form()
    nombre = form_data.get("nombre_expediente")
    resp_id = form_data.get("responsable_id")
    soporte = form_data.get("soporte")
    
    tenant_id = session_data["tenant_id"]
    
    # Validation constraint
    res_check = await db.execute(text("SELECT estado_abierto, fase_archivo FROM agn_expedientes WHERE id = :id AND tenant_id = :t"), {"id": id, "t": tenant_id})
    row = res_check.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
        
    if not row.estado_abierto or row.fase_archivo == 'TRANSFERENCIA':
        return JSONResponse(status_code=403, content={"error": "Inmutabilidad Activa: No se puede modificar un expediente cerrado o en transferencia según Ley 527."})
        
    if soporte:
        await db.execute(text("UPDATE agn_expedientes SET nombre_expediente = :n, soporte = :s WHERE id = :id AND tenant_id = :t"), {"n": nombre, "s": soporte, "id": id, "t": session_data["tenant_id"]})
    else:
        await db.execute(text("UPDATE agn_expedientes SET nombre_expediente = :n WHERE id = :id AND tenant_id = :t"), {"n": nombre, "id": id, "t": session_data["tenant_id"]})
    await db.commit()
    
    return {"status": "success"}
