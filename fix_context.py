with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '"q": q, "status": status, "subserie_id": subserie_id,',
    '"q": q, "status": status, "serie_id": serie_id, "subserie_id": subserie_id,'
)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Added serie_id to context")
