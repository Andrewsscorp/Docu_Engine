with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_sig = """async def get_expedientes_module(
    request: Request,
    q: str = "",
    status: str = "",
    fecha_inicio: str = "",
    fecha_fin: str = "",
    soporte: str = "",
    page: int = 1,
    limit: int = 15,"""

new_sig = """async def get_expedientes_module(
    request: Request,
    q: str = "",
    status: str = "",
    subserie_id: str = "",
    fecha_inicio: str = "",
    fecha_fin: str = "",
    soporte: str = "",
    page: int = 1,
    limit: int = 20,"""

content = content.replace(old_sig, new_sig)

old_where = """    if soporte:
        where_clauses.append("e.soporte = :soporte")
        params["soporte"] = soporte"""

new_where = """    if soporte:
        where_clauses.append("e.soporte = :soporte")
        params["soporte"] = soporte
        
    if subserie_id:
        where_clauses.append("e.subserie_id = :subid::uuid")
        params["subid"] = subserie_id"""

content = content.replace(old_where, new_where)

# also add it to context
old_context = """        "status": status,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "soporte": soporte,
        "page": page,"""

new_context = """        "status": status,
        "subserie_id": subserie_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "soporte": soporte,
        "page": page,"""

content = content.replace(old_context, new_context)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
