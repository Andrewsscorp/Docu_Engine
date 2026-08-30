with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_where = "WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid"
new_where = """WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid
          -- NUEVA REGLA NORMATIVA: El candado de evidencia real
          AND EXISTS (
              SELECT 1 
              FROM documents doc 
              WHERE doc.agn_expediente_id = exp.id 
                AND doc.status IN ('COMPLETED', 'ARCHIVED')
          )"""

content = content.replace(old_where, new_where)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
