with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_def = """async def get_fuid_subserie(
    subserie_id: str,
    request: Request,"""

new_def = """async def get_fuid_subserie(
    subserie_id: str,
    request: Request,
    expediente_id: Optional[str] = None,"""

content = content.replace(old_def, new_def)

old_context = """    return templates.TemplateResponse(request=request, name="pages/fuid_view.html", context={
        "request": request,
        "subserie": subserie_dict,
        "registros": registros
    })"""

new_context = """    return templates.TemplateResponse(request=request, name="pages/fuid_view.html", context={
        "request": request,
        "subserie": subserie_dict,
        "registros": registros,
        "expediente_id_origen": expediente_id
    })"""

content = content.replace(old_context, new_context)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
