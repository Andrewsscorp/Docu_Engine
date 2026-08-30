with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("WHERE e.id = :eid FOR UPDATE", "WHERE e.id = :eid FOR UPDATE OF e")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
