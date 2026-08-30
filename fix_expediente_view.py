with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_sql = "SELECT d.*, t.nombre as tipo_nombre"
new_sql = "SELECT d.*, t.nombre_oficial as tipo_nombre"

content = content.replace(old_sql, new_sql)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
