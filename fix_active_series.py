with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "SELECT id, nombre, codigo FROM agn_series WHERE tenant_id = :t",
    "SELECT id, nombre, codigo FROM agn_series WHERE tenant_id = :t AND estado_activa = TRUE"
)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
