from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db_session
from app.routers.auth import require_permission
from fastapi.templating import Jinja2Templates

tree_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@tree_router.get("/api/v1/agn/tree_html", response_class=HTMLResponse)
async def get_agn_tree_html(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:leer"))
):
    tenant_id = session_data["tenant_id"]
    
    # 1. Fetch all structural data for the tenant
    secciones = (await db.execute(text("SELECT id, codigo, nombre FROM agn_secciones WHERE tenant_id = :t ORDER BY codigo"), {"t": tenant_id})).fetchall()
    subsecciones = (await db.execute(text("SELECT id, seccion_id, codigo, nombre FROM agn_subsecciones WHERE tenant_id = :t ORDER BY codigo"), {"t": tenant_id})).fetchall()
    series = (await db.execute(text("SELECT id, seccion_id, subseccion_id, codigo, nombre FROM agn_series WHERE tenant_id = :t ORDER BY codigo"), {"t": tenant_id})).fetchall()
    subseries = (await db.execute(text("SELECT id, serie_id, codigo, nombre FROM agn_subseries WHERE tenant_id = :t ORDER BY codigo"), {"t": tenant_id})).fetchall()
    expedientes = (await db.execute(text("SELECT id, serie_id, subserie_id, codigo_expediente as codigo, nombre_expediente as nombre, estado FROM agn_expedientes WHERE tenant_id = :t ORDER BY codigo_expediente"), {"t": tenant_id})).fetchall()

    # 2. Build the nested tree
    # Helper index dictionaries
    sec_dict = { s.id: {"id": s.id, "type": "seccion", "codigo": s.codigo, "nombre": s.nombre, "children": []} for s in secciones }
    subsec_dict = { s.id: {"id": s.id, "type": "subseccion", "codigo": s.codigo, "nombre": s.nombre, "children": []} for s in subsecciones }
    ser_dict = { s.id: {"id": s.id, "type": "serie", "codigo": s.codigo, "nombre": s.nombre, "children": []} for s in series }
    subser_dict = { s.id: {"id": s.id, "type": "subserie", "codigo": s.codigo, "nombre": s.nombre, "children": []} for s in subseries }
    
    # Link Expedientes to Series/Subseries
    for e in expedientes:
        node = {"id": e.id, "type": "expediente", "codigo": e.codigo, "nombre": e.nombre, "estado": e.estado, "children": []}
        if e.subserie_id and e.subserie_id in subser_dict:
            subser_dict[e.subserie_id]["children"].append(node)
        elif e.serie_id and e.serie_id in ser_dict:
            ser_dict[e.serie_id]["children"].append(node)
            
    # Link Subseries to Series
    for s in subseries:
        if s.serie_id and s.serie_id in ser_dict:
            ser_dict[s.serie_id]["children"].append(subser_dict[s.id])
            
    # Link Series to Secciones/Subsecciones
    for s in series:
        if s.subseccion_id and s.subseccion_id in subsec_dict:
            subsec_dict[s.subseccion_id]["children"].append(ser_dict[s.id])
        elif s.seccion_id and s.seccion_id in sec_dict:
            sec_dict[s.seccion_id]["children"].append(ser_dict[s.id])
            
    # Link Subsecciones to Secciones
    for s in subsecciones:
        if s.seccion_id and s.seccion_id in sec_dict:
            sec_dict[s.seccion_id]["children"].append(subsec_dict[s.id])
            
    # The root elements are the Secciones
    tree_data = list(sec_dict.values())
    
    return templates.TemplateResponse("components/agn_tree.html", {"request": request, "tree": tree_data})

