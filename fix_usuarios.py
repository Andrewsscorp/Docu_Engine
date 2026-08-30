with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace LEFT JOIN usuarios u ON e.responsable_id = CAST(u.id AS VARCHAR)
# with LEFT JOIN users u ON e.responsable_id = CAST(u.id AS VARCHAR)
# And u.nombres || ' ' || u.apellidos as responsable_nombre
# with u.username as responsable_nombre

content = content.replace("u.nombres || ' ' || u.apellidos as responsable_nombre", "u.username as responsable_nombre")
content = content.replace("LEFT JOIN usuarios u", "LEFT JOIN users u")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed table name users in agn.py")
