with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(":payload::jsonb", "CAST(:payload AS JSONB)")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
