with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Fix dates
content = content.replace("e.fecha_apertura >= :fi::date", "e.fecha_apertura >= CAST(:fi AS date)")
content = content.replace("e.fecha_apertura <= :ff::date", "e.fecha_apertura <= CAST(:ff AS date)")

# Fix subserie
content = content.replace("e.subserie_id = :subid::uuid", "e.subserie_id = CAST(:subid AS uuid)")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
