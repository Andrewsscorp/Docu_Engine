from app.services.encryption import encrypt_message, decrypt_message
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.novu_client import novu_client
from app.rbac import log_audit_action
import json

router = APIRouter(prefix="/api/v1", tags=["Tareas"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/buzon/conteo_sidebar", response_class=HTMLResponse)
async def obtener_conteo_sidebar(request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return HTMLResponse("")
    
    query = text("SELECT COUNT(*) FROM tareas_asignaciones WHERE asignado_a = :uid AND estado_tarea IN ('Pendiente', 'Vencido')")
    res = await db.execute(query, {"uid": user_id})
    count = res.scalar() or 0
    
    if count > 0:
        return HTMLResponse(f"""
        <span class="absolute top-1/2 -translate-y-1/2 right-4 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full min-w-[20px] text-center shadow-sm animate-pulse-once">{count}</span>
        """)
    return HTMLResponse("")

@router.get("/buzon/asignaciones", response_class=HTMLResponse)
async def obtener_bandeja_asignaciones(
    request: Request,
    estado: str = "todo",
    q: str = "",
    fecha_inicio: str = None,
    fecha_fin: str = None,
    pill_filter: str = None,
    user_filter: str = None,
    proximos_vencer: bool = False,
    page: int = 1,
    db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return HTMLResponse("No autorizado", status_code=401)
        
    query_str = '''
    SELECT 
        ta.id_asignacion,
        ta.fecha_asignacion,
        ta.tiempo_respuesta_esperado,
        ta.estado_tarea,
        d.file_name,
        d.id as doc_id,
        u_asignador.username as asignador_nombre,
        u_asignado.username as asignado_nombre,
        (
            SELECT json_agg(
                json_build_object(
                    'nombre', em.nombre,
                    'color_fondo', em.color_fondo,
                    'color_texto', em.color_texto
                )
            )
            FROM documento_etiquetas de
            JOIN etiquetas_maestras em ON de.id_etiqueta = em.id_etiqueta
            WHERE de.id_documento = d.id
        ) as etiquetas,
        (
            SELECT json_agg(
                json_build_object(
                    'cuerpo', tm.cuerpo, 
                    'codigo', tm.codigo_mensaje,
                    'fecha', tm.fecha_envio,
                    'asunto', tm.asunto,
                    'remitente_nombre', u_rem.username
                ) ORDER BY tm.fecha_envio DESC
            )
            FROM tarea_mensajes tm
            LEFT JOIN users u_rem ON tm.remitente_id = u_rem.id
            WHERE tm.id_tarea = ta.id_asignacion
        ) as timeline_mensajes,
        -- Check if it's expired
        ta.tiempo_respuesta_esperado < CURRENT_TIMESTAMP as vencido
    FROM tareas_asignaciones ta
    JOIN documents d ON ta.id_documento = d.id
    JOIN users u_asignador ON ta.asignado_por = u_asignador.id
    JOIN users u_asignado ON ta.asignado_a = u_asignado.id
    WHERE ta.asignado_a = :uid
    '''
    
    params = {"uid": user_id}
    
    if estado == 'enviadas':
        query_str = query_str.replace("WHERE ta.asignado_a = :uid", "WHERE ta.asignado_por = :uid")
    elif estado == 'pendientes':
        query_str += " AND ta.estado_tarea IN ('Pendiente') "
    elif estado == 'vencidas':
        query_str += " AND ta.estado_tarea IN ('Vencido', 'Pendiente') AND ta.tiempo_respuesta_esperado < CURRENT_TIMESTAMP "
    elif estado == 'aceptados':
        query_str += " AND ta.estado_tarea IN ('En Progreso', 'Completado') "
    elif estado == 'rechazados':
        query_str += " AND ta.estado_tarea = 'Rechazado' "
    else:
        query_str += " AND ta.estado_tarea IN ('Pendiente', 'Vencido') "
        
    if q:
        query_str += " AND d.file_name ILIKE :q "
        params["q"] = f"%{q}%"
        
    import datetime
    if fecha_inicio:
        try:
            params["fi"] = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
            query_str += " AND ta.fecha_asignacion >= :fi "
        except Exception:
            pass
            
    if fecha_fin:
        try:
            params["ff"] = datetime.datetime.strptime(fecha_fin + " 23:59:59", "%Y-%m-%d %H:%M:%S")
            query_str += " AND ta.fecha_asignacion <= :ff "
        except Exception:
            pass

    if estado == 'enviadas':
        query_str += " ORDER BY ta.fecha_asignacion DESC "
    else:
        query_str += '''
        ORDER BY 
            CASE WHEN ta.estado_tarea = 'Pendiente' THEN 1 WHEN ta.estado_tarea = 'Vencido' THEN 2 ELSE 3 END,
            ta.tiempo_respuesta_esperado ASC NULLS LAST
        '''
    
    result = await db.execute(text(query_str), params)
    rows = result.fetchall()
    
    tareas = []
    for row in rows:
        t_dict = dict(row._mapping)
        if t_dict.get('timeline_mensajes'):
            # Decrypt each message
            decrypted_timeline = []
            from datetime import datetime
            for msg in t_dict['timeline_mensajes']:
                if msg:
                    if msg.get('cuerpo'):
                        msg['cuerpo'] = decrypt_message(msg['cuerpo'])
                    if msg.get('fecha') and isinstance(msg['fecha'], str):
                        try:
                            # Parse ISO string from PostgreSQL JSON
                            msg['fecha'] = datetime.fromisoformat(msg['fecha'].replace('Z', '+00:00'))
                        except ValueError:
                            pass
                decrypted_timeline.append(msg)
            t_dict['timeline_mensajes'] = decrypted_timeline
        else:
            t_dict['timeline_mensajes'] = []
            
        t_dict['vista_enviadas'] = (estado == 'enviadas')
        tareas.append(t_dict)
    
    return templates.TemplateResponse(request=request, name="components/buzon_tarjetas.html", context={
        "request": request,
        "tareas": tareas,
        "page": page
    })

@router.put("/tareas/{tarea_id}/aceptar", response_class=HTMLResponse)
async def aceptar_tarea(
    tarea_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="No autorizado")
        
    try:
        check_q = text('''
            SELECT ta.estado_tarea, ta.asignado_por, d.file_name 
            FROM tareas_asignaciones ta
            JOIN documents d ON ta.id_documento = d.id
            WHERE ta.id_asignacion = :tid AND ta.asignado_a = :uid
        ''')
        res = await db.execute(check_q, {"tid": tarea_id, "uid": user_id})
        tarea = res.fetchone()
        
        if not tarea:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
            
        if tarea.estado_tarea != 'Pendiente':
            raise HTTPException(status_code=400, detail=f"La tarea ya esta en estado {tarea.estado_tarea}")
            
        update_q = text('''
            UPDATE tareas_asignaciones 
            SET estado_tarea = 'En Progreso', fecha_aceptacion = CURRENT_TIMESTAMP
            WHERE id_asignacion = :tid
        ''')
        await db.execute(update_q, {"tid": tarea_id})
        
        await log_audit_action(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            action="TAREA_ACEPTADA",
            target_id=str(tarea_id),
            details={"documento": tarea.file_name, "estado_anterior": "Pendiente", "estado_nuevo": "En Progreso"}
        )
        
        import asyncio
        asyncio.create_task(novu_client.trigger_event(event_name="tarea_aceptada", user_id=str(tarea.asignado_por), payload={
                "documento": tarea.file_name,
                "mensaje": f"El auditor ha comenzado a trabajar en {tarea.file_name}"
            }
        ))
        
        await db.commit()
        response = HTMLResponse(content="")
        import json
        response.headers["HX-Trigger"] = json.dumps({"update-sidebar-badge": {}, "reloadBuzon": {}, "toastExito": {"mensaje": "Tarea aceptada en proceso."}})
        return response
    except Exception as e:
        await db.rollback()
        raise e

@router.post("/tareas/{tarea_id}/responder", response_class=HTMLResponse)
async def responder_tarea(
    tarea_id: str,
    request: Request,
    asunto: str = Form(...),
    cuerpo: str = Form(...),
    sendEmail: bool = Form(False),
    db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="No autorizado")
        
    try:
        check_q = text('''
            SELECT ta.asignado_por, d.file_name, u.username as remitente_nombre
            FROM tareas_asignaciones ta
            JOIN documents d ON ta.id_documento = d.id
            JOIN users u ON u.id = :uid
            WHERE ta.id_asignacion = :tid
        ''')
        res = await db.execute(check_q, {"uid": user_id, "tid": tarea_id})
        tarea = res.fetchone()
        
        if not tarea:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
            
        insert_msg = text('''
            INSERT INTO tarea_mensajes (id_tarea, remitente_id, asunto, cuerpo, notificado_por_correo)
            VALUES (:tid, :uid, :asunto, :cuerpo, :notificado)
        ''')
        await db.execute(insert_msg, {
            "tid": tarea_id,
            "uid": user_id,
            "asunto": asunto,
            "cuerpo": encrypt_message(cuerpo),
            "notificado": sendEmail
        })
        
        # Re-asignar la tarea de vuelta al asignador original ("bounce back")
        swap_q = text("""
            UPDATE tareas_asignaciones
            SET asignado_a = asignado_por,
                asignado_por = asignado_a,
                estado_tarea = 'Pendiente',
                fecha_asignacion = CURRENT_TIMESTAMP
            WHERE id_asignacion = :tid
            RETURNING id_documento, asignado_a
        """)
        swap_res = await db.execute(swap_q, {"tid": tarea_id})
        updated_task = swap_res.fetchone()
        
        if updated_task:
            # Transferir el ownership del documento tambien. Bypass RLS temporalmente
            await db.execute(text("SELECT set_config('app.is_superadmin', 'true', true)"))
            update_doc = text("UPDATE documents SET assigned_user_id = :uid WHERE id = :did")
            await db.execute(update_doc, {"uid": updated_task.asignado_a, "did": updated_task.id_documento})
            # RLS volverá a su estado normal al hacer commit/rollback gracias al tercer parametro 'true' (is_local)

        
        overrides = {}
        if sendEmail:
            overrides = {"email": {"active": True}}
        else:
            overrides = {"email": {"active": False}}
            
        payload = {
            "asunto": asunto,
            "mensaje": cuerpo,
            "documento_nombre": tarea.file_name,
            "remitente": tarea.remitente_nombre
        }
        
        import asyncio
        asyncio.create_task(novu_client.trigger_event(event_name="nueva_respuesta_tarea", user_id=str(tarea.asignado_por), payload=payload,
            overrides=overrides
        ))
        
        await db.commit()
        
        response = HTMLResponse(content="")
        response.headers["HX-Trigger"] = json.dumps({
            "cerrarModalYNotificar": {},
            "toastExito": {"mensaje": "Respuesta enviada exitosamente."},
            "update-sidebar-badge": {}, "reloadBuzon": {}
        })
        return response
    except Exception as e:
        await db.rollback()
        raise e

@router.get("/buzon/conteos")
async def obtener_conteos_tabs(request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return {}
    
    # Obtenemos las tareas con su fecha de ultima actualizacion (ultimo mensaje o fecha de actualizacion)
    query = text("""
        SELECT 
            ta.id_asignacion,
            ta.estado_tarea,
            ta.asignado_a,
            ta.asignado_por,
            COALESCE(
                (SELECT MAX(fecha_envio) FROM tarea_mensajes WHERE id_tarea = ta.id_asignacion AND remitente_id != :uid),
                ta.fecha_asignacion
            ) as last_update
        FROM tareas_asignaciones ta
        WHERE ta.asignado_a = :uid OR ta.asignado_por = :uid
    """)
    res = await db.execute(query, {"uid": user_id})
    rows = res.fetchall()
    
    def get_list(category_condition):
        import datetime
        def to_ts(dt):
            if not dt: return 0
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return int(dt.timestamp() * 1000)
            
        return [
            {"id": str(r.id_asignacion), "ts": to_ts(r.last_update)} 
            for r in rows if category_condition(r)
        ]

    return {
        "nuevo": get_list(lambda r: str(r.asignado_a) == user_id and r.estado_tarea in ('Pendiente', 'Vencido')),
        "enviadas": get_list(lambda r: str(r.asignado_por) == user_id),
        "pendientes": get_list(lambda r: str(r.asignado_a) == user_id and r.estado_tarea == 'Pendiente'),
        "vencidas": get_list(lambda r: str(r.asignado_a) == user_id and r.estado_tarea == 'Vencido'),
        "aceptados": get_list(lambda r: str(r.asignado_a) == user_id and r.estado_tarea in ('En Progreso', 'Completado')),
        "rechazados": get_list(lambda r: str(r.asignado_a) == user_id and r.estado_tarea == 'Rechazado')
    }

@router.get("/buzon/estadisticas", response_class=HTMLResponse)
async def obtener_estadisticas_buzon(request: Request, db: AsyncSession = Depends(get_db_session)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id: return HTMLResponse("")
    
    q_urgentes = "SELECT COUNT(*) FROM tareas_asignaciones WHERE asignado_a = :uid AND estado_tarea IN ('Pendiente', 'Vencido') AND tiempo_respuesta_esperado < CURRENT_TIMESTAMP + INTERVAL '24 hours'"
    q_pendientes = "SELECT COUNT(*) FROM tareas_asignaciones WHERE asignado_a = :uid AND estado_tarea IN ('Pendiente')"
    q_completadas = "SELECT COUNT(*) FROM tareas_asignaciones WHERE asignado_a = :uid AND estado_tarea IN ('Completado', 'Rechazado', 'En Progreso')"
    
    urg = (await db.execute(text(q_urgentes), {"uid": user_id})).scalar() or 0
    pend = (await db.execute(text(q_pendientes), {"uid": user_id})).scalar() or 0
    comp = (await db.execute(text(q_completadas), {"uid": user_id})).scalar() or 0
    
    return HTMLResponse(f"""
        <div class="px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 shadow-sm border cursor-pointer hover:shadow-md transition-all hover:-translate-y-0.5"
             :class="pillFilter === 'urgentes' ? 'bg-red-600 text-white border-red-700 ring-2 ring-red-300 ring-offset-2' : 'bg-gradient-to-r from-red-50 to-red-100 text-red-700 border-red-200'"
             @click="pillFilter = (pillFilter === 'urgentes' ? '' : 'urgentes'); tabFiltro = 'todo'; setTimeout(() => htmx.trigger('#buzon-filters', 'submit'), 10);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span class="flex items-center gap-1">
                {f'<span class="relative flex h-2 w-2 mr-1"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span></span>' if urg > 0 else ''}
                {urg}
            </span> Urgentes
        </div>
        
        <div class="px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 shadow-sm border cursor-pointer hover:shadow-md transition-all hover:-translate-y-0.5"
             :class="pillFilter === 'pendientes' ? 'bg-amber-500 text-white border-amber-600 ring-2 ring-amber-300 ring-offset-2' : 'bg-gradient-to-r from-amber-50 to-amber-100 text-amber-700 border-amber-200'"
             @click="pillFilter = (pillFilter === 'pendientes' ? '' : 'pendientes'); tabFiltro = 'todo'; setTimeout(() => htmx.trigger('#buzon-filters', 'submit'), 10);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
            <span class="py-0.5 px-2 rounded-md" :class="pillFilter === 'pendientes' ? 'bg-amber-600 text-white' : 'bg-amber-200 text-amber-800'">{pend}</span> Pendientes
        </div>
        
        <div class="px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 shadow-sm border cursor-pointer hover:shadow-md transition-all hover:-translate-y-0.5"
             :class="pillFilter === 'procesadas' ? 'bg-emerald-600 text-white border-emerald-700 ring-2 ring-emerald-300 ring-offset-2' : 'bg-gradient-to-r from-emerald-50 to-emerald-100 text-emerald-700 border-emerald-200'"
             @click="pillFilter = (pillFilter === 'procesadas' ? '' : 'procesadas'); tabFiltro = 'todo'; setTimeout(() => htmx.trigger('#buzon-filters', 'submit'), 10);">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span class="py-0.5 px-2 rounded-md" :class="pillFilter === 'procesadas' ? 'bg-emerald-700 text-white' : 'bg-emerald-200 text-emerald-800'">{comp}</span> Procesadas
        </div>
    """)

@router.put("/tareas/{tarea_id}/rechazar", response_class=HTMLResponse)
async def rechazar_tarea(
    tarea_id: str,
    request: Request,
    motivo: str = Form(...),
    db: AsyncSession = Depends(get_db_session)
):
    user_id = getattr(request.state, "user_id", None)
    tenant_id = getattr(request.state, "tenant_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="No autorizado")
        
    try:
        check_q = text('''
            SELECT ta.estado_tarea, ta.asignado_por, d.file_name, u.username as remitente_nombre
            FROM tareas_asignaciones ta
            JOIN documents d ON ta.id_documento = d.id
            JOIN users u ON ta.asignado_por = u.id
            WHERE ta.id_asignacion = :tid AND ta.asignado_a = :uid
        ''')
        res = await db.execute(check_q, {"tid": tarea_id, "uid": user_id})
        tarea = res.fetchone()
        
        if not tarea:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
            
        if tarea.estado_tarea != 'Pendiente':
            raise HTTPException(status_code=400, detail=f"La tarea ya esta en estado {tarea.estado_tarea}")
            
        update_q = text('''
            UPDATE tareas_asignaciones 
            SET estado_tarea = 'Rechazado', fecha_cierre = CURRENT_TIMESTAMP
            WHERE id_asignacion = :tid
        ''')
        await db.execute(update_q, {"tid": tarea_id})
        
        insert_msg = text('''
            INSERT INTO tarea_mensajes (id_tarea, remitente_id, asunto, cuerpo)
            VALUES (:tid, :uid, 'Tarea Rechazada', :motivo)
        ''')
        await db.execute(insert_msg, {"tid": tarea_id, "uid": user_id, "motivo": encrypt_message(motivo)})
        
        from app.rbac import log_audit_action
        await log_audit_action(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            action="TAREA_RECHAZADA",
            target_id=str(tarea_id),
            details={"documento": tarea.file_name, "motivo": motivo}
        )
        
        from app.services.novu_client import novu_client
        import asyncio
        asyncio.create_task(novu_client.trigger_event(event_name="tarea_rechazada", user_id=str(tarea.asignado_por), payload={
                "documento": tarea.file_name,
                "mensaje": f"El auditor ha rechazado la tarea: {motivo}"
            }
        ))
        
        await db.commit()
        
        import json
        response = HTMLResponse(content="")
        response.headers["HX-Trigger"] = json.dumps({
            "cerrarModalYNotificar": {},
            "toastExito": {"mensaje": "Documento devuelto exitosamente."},
            "update-sidebar-badge": {}, "reloadBuzon": {}
        })
        return response
    except Exception as e:
        await db.rollback()
        raise e
