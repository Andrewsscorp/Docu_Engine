with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Remove the EXISTS clause from the fallback_sql in agn.py
old_query = """WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid
          -- NUEVA REGLA NORMATIVA: El candado de evidencia real
          AND EXISTS (
              SELECT 1 
              FROM documents doc 
              WHERE doc.agn_expediente_id = exp.id 
                AND doc.status IN ('COMPLETED', 'ARCHIVED')
          )"""

new_query = """WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid"""

content = content.replace(old_query, new_query)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
