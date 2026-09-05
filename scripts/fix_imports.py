import os

files = ["app/services/expediente_service.py", "app/services/fixity_service.py"]
for p in files:
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace("from app.notifications import log_audit_sgdea_async", "from app.services.audit_service import log_audit_sgdea_async")
    with open(p, "w", encoding="utf-8") as f:
        f.write(c)

with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    c = f.read()
if "from app.services.audit_service import log_audit_sgdea_async" not in c:
    c = c.replace("from app.services.expediente_service import ExpedienteService", "from app.services.expediente_service import ExpedienteService\nfrom app.services.audit_service import log_audit_sgdea_async")
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(c)
