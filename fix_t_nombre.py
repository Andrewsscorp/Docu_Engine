with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("t.nombre ASC", "t.nombre_oficial ASC")
content = content.replace("SELECT t.id, t.nombre, st.obligatoria", "SELECT t.id, t.nombre_oficial, st.obligatoria")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
