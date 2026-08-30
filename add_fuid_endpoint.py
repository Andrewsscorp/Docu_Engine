with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
@router.get("/subseries/{subserie_id}/fuid")
async def get_fuid_subserie(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # 1. Fetch subserie details
    sub_res = await db.execute(text("SELECT s.codigo, s.nombre, se.nombre as serie_nombre FROM agn_subseries s LEFT JOIN agn_series se ON s.serie_id = se.id WHERE s.id = :sid"), {"sid": subserie_id})
    subserie = sub_res.fetchone()
    if not subserie:
        return HTMLResponse("Subserie no encontrada", status_code=404)
        
    # 2. Try to query the materialized view, fallback to raw SQL if it doesn't exist
    try:
        fuid_res = await db.execute(text("SELECT * FROM vista_fuid_detalle_subserie WHERE subserie_id = :sid ORDER BY no_orden ASC"), {"sid": subserie_id})
        filas = fuid_res.fetchall()
    except Exception as e:
        # Fallback raw query if the view hasn't been created yet by the admin
        fallback_sql = \"\"\"
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
        \"\"\"
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
    return templates.TemplateResponse("pages/fuid_view.html", {
        "request": request,
        "subserie": subserie,
        "registros": registros
    })
"""

content = content + new_endpoint

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
