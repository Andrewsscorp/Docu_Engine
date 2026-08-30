with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Fix 1: The 'exist_res' query in post_vincular_trd
old_exist = """exist_res = await db.execute(text("SELECT id FROM agn_subserie_tipologia WHERE subserie_id = :sid AND tipologia_id = :tid"), {"eid": expediente_id, "tid": payload.id_tipologia})"""
new_exist = """exist_res = await db.execute(text("SELECT id FROM agn_expediente_tipologia WHERE expediente_id = :eid AND tipologia_id = :tid"), {"eid": expediente_id, "tid": payload.id_tipologia})"""
if old_exist in content:
    content = content.replace(old_exist, new_exist)

# Fix 2: The requeridas_res query when closing an expediente
old_cierre = """        SELECT tipologia_id 
        FROM agn_subserie_tipologia 
        WHERE subserie_id = :sid AND obligatoria = TRUE"""
new_cierre = """        SELECT tipologia_id 
        FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid AND obligatoria = TRUE"""
if old_cierre in content:
    content = content.replace(old_cierre, new_cierre)
    content = content.replace('{"sid": exp.subserie_id}', '{"eid": exp.id}')

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
