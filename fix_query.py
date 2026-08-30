with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_query = """        SELECT t.id, t.nombre_oficial, st.obligatoria 
        FROM agn_tipologias t
        LEFT JOIN agn_subserie_tipologia st ON st.tipologia_id = t.id AND st.subserie_id = :sid
        WHERE st.obligatoria = TRUE OR t.tenant_id = :t"""

new_query = """        SELECT t.id, t.nombre_oficial, st.obligatoria 
        FROM agn_tipologias t
        LEFT JOIN agn_expediente_tipologia st ON st.tipologia_id = t.id AND st.expediente_id = :eid
        WHERE st.obligatoria = TRUE OR t.tenant_id = :t"""

if old_query in content:
    content = content.replace(old_query, new_query)
else:
    print("Old query not found! Please check exact string.")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
