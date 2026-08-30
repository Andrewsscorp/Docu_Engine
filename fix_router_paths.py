import re
with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('@router.post("/api/v1/agn/expedientes/{expediente_id}/vincular")', '@router.post("/expedientes/{expediente_id}/vincular")')
content = content.replace('@router.get("/api/v1/agn/expedientes/explorer")', '@router.get("/expedientes/explorer")')
content = content.replace('@router.get("/api/v1/agn/expedientes/{expediente_id}/view")', '@router.get("/expedientes/{expediente_id}/view")')
content = content.replace('@router.post("/api/v1/agn/expedientes/{expediente_id}/cerrar")', '@router.post("/expedientes/{expediente_id}/cerrar")')

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
