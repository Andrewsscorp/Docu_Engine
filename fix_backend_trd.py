with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# 1. Update GET /subseries/{subserie_id}/modal_trd -> GET /expedientes/{expediente_id}/modal_trd
old_modal_route = """@router.get("/subseries/{subserie_id}/modal_trd")
async def get_modal_trd(
    subserie_id: str,"""
new_modal_route = """@router.get("/expedientes/{expediente_id}/modal_trd")
async def get_modal_trd(
    expediente_id: str,"""
content = content.replace(old_modal_route, new_modal_route)

old_modal_logic = """    sub_res = await db.execute(text("SELECT * FROM agn_subseries WHERE id = :sid"), {"sid": subserie_id})
    sub = dict(sub_res.fetchone()._mapping)"""
new_modal_logic = """    exp_res = await db.execute(text("SELECT * FROM agn_expedientes WHERE id = :eid"), {"eid": expediente_id})
    exp = dict(exp_res.fetchone()._mapping)"""
content = content.replace(old_modal_logic, new_modal_logic)

old_modal_context = """    return templates.TemplateResponse(request=request, name="components/modal_vincular_trd.html", context={
        "request": request,
        "subserie": sub,
        "puede_crear_tipologias": has_perm
    })"""
new_modal_context = """    return templates.TemplateResponse(request=request, name="components/modal_vincular_trd.html", context={
        "request": request,
        "expediente": exp,
        "puede_crear_tipologias": has_perm
    })"""
content = content.replace(old_modal_context, new_modal_context)

# 2. Update GET /subseries/{subserie_id}/tipologias/disponibles -> /expedientes/{expediente_id}/...
old_disp_route = """@router.get("/subseries/{subserie_id}/tipologias/disponibles")
async def get_tipologias_disponibles(
    subserie_id: str,"""
new_disp_route = """@router.get("/expedientes/{expediente_id}/tipologias/disponibles")
async def get_tipologias_disponibles(
    expediente_id: str,"""
content = content.replace(old_disp_route, new_disp_route)

old_disp_sql = """SELECT t.id, t.nombre_oficial 
        FROM agn_tipologias t
        WHERE t.estado_activo = TRUE 
          AND t.tenant_id = :t
          AND t.id NOT IN (
              SELECT tipologia_id FROM agn_subserie_tipologia WHERE subserie_id = :sid AND estado_regla = TRUE
          )"""
new_disp_sql = """SELECT t.id, t.nombre_oficial 
        FROM agn_tipologias t
        WHERE t.estado_activo = TRUE 
          AND t.tenant_id = :t
          AND t.id NOT IN (
              SELECT tipologia_id FROM agn_expediente_tipologia WHERE expediente_id = :eid AND estado_regla = TRUE
          )"""
content = content.replace(old_disp_sql, new_disp_sql)
content = content.replace('{"t": session_data["tenant_id"], "sid": subserie_id}', '{"t": session_data["tenant_id"], "eid": expediente_id}')

# 3. Update POST /subseries/{subserie_id}/tipologias -> /expedientes/{expediente_id}/tipologias
old_post_route = """@router.post("/subseries/{subserie_id}/tipologias")
async def post_vincular_trd(
    subserie_id: str,"""
new_post_route = """@router.post("/expedientes/{expediente_id}/tipologias")
async def post_vincular_trd(
    expediente_id: str,"""
content = content.replace(old_post_route, new_post_route)

old_post_exist = """exist_res = await db.execute(text("SELECT id FROM agn_subserie_tipologia WHERE subserie_id = :sid AND tipologia_id = :tid"), {"sid": subserie_id, "tid": payload.id_tipologia})
    if exist_res.fetchone():
        return JSONResponse({"status": "error", "message": "Esta tipología ya pertenece a la Subserie."}, status_code=409)"""
new_post_exist = """exist_res = await db.execute(text("SELECT id FROM agn_expediente_tipologia WHERE expediente_id = :eid AND tipologia_id = :tid"), {"eid": expediente_id, "tid": payload.id_tipologia})
    if exist_res.fetchone():
        return JSONResponse({"status": "error", "message": "Esta tipología ya pertenece al Expediente."}, status_code=409)"""
content = content.replace(old_post_exist, new_post_exist)

old_post_insert = """INSERT INTO agn_subserie_tipologia (subserie_id, tipologia_id, obligatoria, orden_sugerido, usuario_creador)
        VALUES (:sid, :tid, :obl, :ord, :uid)"""
new_post_insert = """INSERT INTO agn_expediente_tipologia (expediente_id, tipologia_id, obligatoria, orden_sugerido, usuario_creador)
        VALUES (:eid, :tid, :obl, :ord, :uid)"""
content = content.replace(old_post_insert, new_post_insert)
content = content.replace('"sid": subserie_id,', '"eid": expediente_id,')


# 4. Update get_expediente_inner_view and get_control_tipologias_view to query agn_expediente_tipologia
old_inner_matrix = """FROM agn_subserie_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        WHERE st.subserie_id = :sid"""
new_inner_matrix = """FROM agn_expediente_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        WHERE st.expediente_id = :eid"""
content = content.replace(old_inner_matrix, new_inner_matrix)
content = content.replace('{"eid": expediente_id, "sid": exp.get("subserie_id")}', '{"eid": expediente_id}')

old_control_matrix = """FROM agn_subserie_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        LEFT JOIN users u ON doc.uploaded_by = u.id
        WHERE st.subserie_id = :sid"""
new_control_matrix = """FROM agn_expediente_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        LEFT JOIN users u ON doc.uploaded_by = u.id
        WHERE st.expediente_id = :eid"""
content = content.replace(old_control_matrix, new_control_matrix)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
