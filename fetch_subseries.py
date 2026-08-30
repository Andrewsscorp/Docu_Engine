with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_fetch = """    # Query with filters and pagination
    query_str = f'''"""

new_fetch = """    # Fetch subseries for the dropdown
    res_sub = await db.execute(text("SELECT id, codigo, nombre FROM agn_subseries WHERE tenant_id = :t ORDER BY codigo"), {"t": tenant_id})
    subseries = [dict(r._mapping) for r in res_sub.fetchall()]
    
    # Query with filters and pagination
    query_str = f'''"""

content = content.replace(old_fetch, new_fetch)

old_context2 = """        "page": page,
        "has_more": has_more,"""

new_context2 = """        "page": page,
        "subseries": subseries,
        "has_more": has_more,"""

content = content.replace(old_context2, new_context2)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
