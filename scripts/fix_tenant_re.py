with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn = f.read()

import re

agn = re.sub(
    r"DELETE FROM agn_expediente_tipologia\s+WHERE expediente_id = :eid AND tipologia_id = :tid",
    "DELETE FROM agn_expediente_tipologia \\n        WHERE expediente_id = :eid AND tipologia_id = :tid \\n        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)",
    agn
)

agn = re.sub(
    r"DELETE FROM agn_expediente_tipologia\s+WHERE expediente_id = :eid(?!\s+AND)",
    "DELETE FROM agn_expediente_tipologia \\n        WHERE expediente_id = :eid \\n        AND expediente_id IN (SELECT id FROM agn_expedientes WHERE tenant_id = :t)",
    agn
)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(agn)
