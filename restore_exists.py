with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_query = """WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid"""

new_query = """WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid
        -- NUEVA REGLA NORMATIVA: El candado de evidencia real
        AND EXISTS (
            SELECT 1 
            FROM documents doc 
            WHERE doc.agn_expediente_id = exp.id 
              AND doc.status IN ('COMPLETED', 'ARCHIVED')
        )"""

# Only replace the one inside the fallback_sql string (the second occurrence probably, let's just replace all since it's the same logic)
content = content.replace(old_query, new_query)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
