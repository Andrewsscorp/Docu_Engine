with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_join = "JOIN agn_dependencias d ON s.seccion_id = d.id OR s.subseccion_id = d.id"
good_join = "JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)"

if bad_join in content:
    content = content.replace(bad_join, good_join)
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed JOIN to COALESCE")
else:
    print("Join not found!")
