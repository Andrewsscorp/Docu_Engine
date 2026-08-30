with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Update get_modal_trd to check permissions
old_endpoint = """@router.get("/subseries/{subserie_id}/modal_trd")
async def get_modal_trd(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    sub_res = await db.execute(text("SELECT * FROM agn_subseries WHERE id = :sid"), {"sid": subserie_id})
    sub = dict(sub_res.fetchone()._mapping)
    
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request=request, name="components/modal_vincular_trd.html", context={
        "request": request,
        "subserie": sub
    })"""

new_endpoint = """@router.get("/subseries/{subserie_id}/modal_trd")
async def get_modal_trd(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    sub_res = await db.execute(text("SELECT * FROM agn_subseries WHERE id = :sid"), {"sid": subserie_id})
    sub = dict(sub_res.fetchone()._mapping)
    
    # Check if user has tipologias:crear permission
    # In a real app we'd query the permissions, but since we rely on require_permission dependency, 
    # we can do a quick check:
    perm_res = await db.execute(text('''
        SELECT 1 FROM user_groups ug
        JOIN groups g ON ug.group_id = g.id
        JOIN role_permissions rp ON g.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE ug.user_id = :uid AND p.name = 'tipologias:crear'
    '''), {"uid": session_data["user_id"]})
    has_perm = perm_res.fetchone() is not None
    
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request=request, name="components/modal_vincular_trd.html", context={
        "request": request,
        "subserie": sub,
        "puede_crear_tipologias": has_perm
    })"""

content = content.replace(old_endpoint, new_endpoint)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)

with open("app/templates/components/modal_vincular_trd.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Wrap the button with {% if puede_crear_tipologias %}
old_btn = """<button @click="mostrarNuevaTipologia = !mostrarNuevaTipologia" type="button" class="text-xs font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-3 py-1 rounded-lg transition-colors flex items-center gap-1 border border-indigo-200">"""
new_btn = """{% if puede_crear_tipologias %}<button @click="mostrarNuevaTipologia = !mostrarNuevaTipologia" type="button" class="text-xs font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-3 py-1 rounded-lg transition-colors flex items-center gap-1 border border-indigo-200">{% else %}<button style="display:none">{% endif %}"""

html_content = html_content.replace(old_btn, new_btn)

with open("app/templates/components/modal_vincular_trd.html", "w", encoding="utf-8") as f:
    f.write(html_content)
